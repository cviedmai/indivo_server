"""
IDP - Indivo Document Processing
"""

import os
import sys
import hashlib
#import libxml2
#import libxslt
from lxml import etree

#from xml.dom import minidom

from indivo.models import DocumentSchema
from django.conf import settings
from django.db import transaction

from idp_objs.allergy               import IDP_Allergy
from idp_objs.equipment             import IDP_Equipment
from idp_objs.measurement           import IDP_Measurement
from idp_objs.immunization          import IDP_Immunization
from idp_objs.lab                   import IDP_Lab
from idp_objs.medication            import IDP_Medication
from idp_objs.problem               import IDP_Problem
from idp_objs.procedure             import IDP_Procedure
from idp_objs.simple_clinical_note  import IDP_SimpleClinicalNote
from idp_objs.vitals                import IDP_Vitals

DOM = 'dom'
OCON = 'ocon'

DP_DOBJ_PROCESS   = 'process'
DP_DOBJ_POST_DATA = 'post_data'
DOC_CLASS_REL     = { 
                  'http://indivo.org/vocab/xml/documents#Allergy'       :   {'class' : 'IDP_Allergy',       'stylesheet' : 'allergy'},
                  'http://indivo.org/vocab/xml/documents#SimpleClinicalNote'  :   {'class' : 'IDP_SimpleClinicalNote',       'stylesheet' : 'simple_clinical_note'},
                  'http://indivo.org/vocab/xml/documents#Equipment'     :   {'class' : 'IDP_Equipment',     'stylesheet' : 'equipment'},
                  'http://indivo.org/vocab/xml/documents#HBA1C'         :   {'class' : 'IDP_Measurement'},
                  'http://indivo.org/vocab/xml/documents#Immunization'  :   {'class' : 'IDP_Immunization',  'stylesheet' : 'immunization'},
                  'http://indivo.org/vocab/xml/documents#Lab'           :   {'class' : 'IDP_Lab',           'stylesheet' : 'lab'},
                  'http://indivo.org/vocab/xml/documents#Medication'    :   {'class' : 'IDP_Medication',    'stylesheet' : 'medication'},
                  'http://indivo.org/vocab/xml/documents#Problem'       :   {'class' : 'IDP_Problem',       'stylesheet' : 'problem'},
                  'http://indivo.org/vocab/xml/documents#Procedure'     :   {'class' : 'IDP_Procedure',     'stylesheet' : 'procedure'},
                  'http://s1984.it.kth.se/indivo/vitals.xsd#VitalSign'     :   {'class' : 'IDP_Vitals',        'stylesheet' : 'vitalsign'}
                }

DEFAULT_PREFIX= "http://indivo.org/vocab/xml/documents#"

class DocumentProcessing:

  @classmethod
  def expand_schema(cls, schema):
    """
    go from Allergy to http://indivo.org/vocab/xml/documents#Allergy
    """
    if schema is None:
      return None

    if schema.find(':') > -1 or schema.find('/') > -1:
      return schema
    else:
      return "%s%s" % (DEFAULT_PREFIX, schema)

  def __init__(self, doc):

    # FIXME: we should move away from checking types explicitly.
    # maybe what we're checking for here is the presence of a __string__ method
    # or a __len__ method, or...?
    if not (isinstance(doc, str) or \
            isinstance(doc, unicode)) or \
            len(doc) == 0:
      raise ValueError
    # SZ: Assigned twice so that it is initially set
    self.doc            = self.set_doc(doc)
    self.is_binary      = False
    self.content        = self.doc[OCON]

    # SZ: This should be abstracted out
    self.doctype        = None
    self.doc_schema     = None
    self.doc_class_rel  = DOC_CLASS_REL
    self.root_node_name = self.get_root_node_name()

  def process(self):
    self.f_objs_str = 'f_objs'
    p = self._process()
    if p and p.has_key(self.f_objs_str):
      self.f_objs = p[self.f_objs_str]

  def set_doc(self, doc):
    ret = {}
    ret[OCON] = doc
    ret[DOM]  = self.get_dom(self.get_clean_xml(doc))
    self.doc  = ret
    return ret

  def get_document_digest(self):
    md = hashlib.sha256()
    md.update(self.doc[OCON])
    return md.hexdigest()

  def get_document_size(self):
    return len(self.doc[OCON])

  def get_stylesheet(self):
    ext = '.xsl'
    if settings.XSLT_STYLESHEET_LOC:
      # get the path to the stylesheet from DOC_CLASS_REL mapping above
      doc_type_info = self.doc_class_rel[self.get_type()]
      if doc_type_info.has_key('stylesheet'):
        stylesheet_path = "%s%s%s" % (settings.XSLT_STYLESHEET_LOC, doc_type_info['stylesheet'], ext)
        if os.path.exists(stylesheet_path):
          return open(stylesheet_path).read()

    return None

  def apply_stylesheet(self, xml_doc, xsl_doc):
    try:
      #style = libxslt.parseStylesheetDoc(libxml2.parseDoc(xsl_doc))
      #doc = libxml2.parseDoc(xml_doc)
      #result = style.applyStylesheet(doc, None)
      #result_str = result.serialize()

      # Clean up
      #style.freeStylesheet()
      #doc.freeDoc()
      #result.freeDoc()
  
      style = etree.XSLT(etree.XML(xsl_doc))
      doc = etree.XML(xml_doc)
      result = style(doc)
      result_str = str(result)

      # Return result
      return result_str
    except:
      return False

  def _process(self):
    """ Process the incoming doc """

    # Is this document registered in document schema?
    # Is this document registered in doc_class_rel?
    # Does doc_class_rel contain 'class'?
    # FIXME: we should stop using this globals() approach. Not good. (Ben)
    doc_schema = self.get_document_schema()
    if  doc_schema and \
        self.doc_class_rel.has_key(doc_schema.type) and \
        globals().has_key(self.doc_class_rel[doc_schema.type]['class']):
      # Get the object that corresponds to the incoming xml node name
      dp_data_obj = globals()[self.doc_class_rel[doc_schema.type]['class']]()
      # Retrieve a stylesheet, if there is one
      stylesheet = self.get_stylesheet()
      if stylesheet:
        self.set_doc(self.apply_stylesheet(self.doc[OCON], stylesheet))

      # Test for a process method
      # If dp_data_obj has a process method then use it
      # else use document_processing standard
      if hasattr(dp_data_obj, DP_DOBJ_PROCESS):
        doc_data = dp_data_obj.process(self.root_node_name, self.doc)
      else:
        doc_data = self.parse_standard_facts_doc(self.doc)
      
      # If dp_data_obj has the post_data method
      # then post it and set and return the fact obj
      if hasattr(dp_data_obj, DP_DOBJ_POST_DATA) and doc_data:
        try:
          f_objs = []
          for data in doc_data:
            f_objs.append(dp_data_obj.post_data(**data))
          if f_objs:
            return {self.f_objs_str : f_objs}
        except ValueError, e:
          # FIXME: this rollback here doesn't seem to do the right thing
          # because we're not in a transaction. If we're going to roll
          # back a transaction, it should probably happen at a higher level,
          # probably in the view.
          try:
            transaction.rollback()
          except:
            # no transaction management is fine
            pass

          
          # we raise the exception, if processing fails we need to stop 
          raise e
    return False

  def parse_standard_facts_doc(self, doc):
    retval_facts = []
    xmldom = doc[DOM]

    # if there is a DOM, use etree find
    if xmldom is not None:
      for fact in xmldom.findall('fact'):
        # make a dictionary of the immediate children tags of the fact
        new_fact = dict([(e.tag, e.text) for e in fact.getchildren()])
        retval_facts.append(new_fact)

    if retval_facts:
      return retval_facts
    return False

  def unicode_to_string(self, s):
    retval = s
    if isinstance(s, unicode):
      retval = str(s)
    return retval

  def get_root_node_name(self):
    """
    get the namespace and remove it from the full tag,
    which is formatted as {ns}tag
    """
    if self.doc[DOM] is not None:
      ns = self.get_root_node_ns()
      return self.doc[DOM].tag.replace("{%s}" % ns, "")

  def get_root_node_ns(self):
    """
    get the URI of the namespace, by mapping the prefix
    with the NS map.
    """
    if self.doc[DOM] is not None:
      nsmap = self.doc[DOM].nsmap
      if nsmap.has_key(self.doc[DOM].prefix):
        return nsmap[self.doc[DOM].prefix]
      else:
        return ""

  def get_type(self):
    if not self.doctype:
      if self.doc[DOM] is not None:
        self.doctype = "%s%s" % (self.get_root_node_ns(), self.get_root_node_name())
    return self.doctype

  def get_document_schema(self):
    if not self.doc_schema:
      try:
        if self.get_type():
          self.doc_schema = DocumentSchema.objects.get(type=self.doctype)
      except DocumentSchema.DoesNotExist:
        pass
    return self.doc_schema

  def get_dom(self, doc):
    try:
      return etree.fromstring(doc)
    except:
      return None

  def get_clean_xml(self, doc):
    # SZ: Do more cleaning!
    return doc.strip()
