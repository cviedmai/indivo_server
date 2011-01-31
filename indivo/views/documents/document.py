"""
Indivo Views -- Documents
"""

import urllib2
import hashlib

from indivo.lib import utils

from indivo.views.base import *
from indivo.document_processing.docbox import Docbox
from indivo.document_processing.document_utils import DocumentUtils
from indivo.document_processing.document_processing import DocumentProcessing
from django.core.files.base import ContentFile


from django.db.models import Count


PHA, RECORD, CREATOR, MIME_TYPE, EXTERNAL_ID, ORIGINAL_ID, CONTENT, DIGEST, SIZE, TYPE  = (
  'pha', 'record', 'creator', 'mime_type', 'external_id', 'original_id', 'content', 'digest', 'size', 'type')

##
## The following calls need to be optimized and not done at load time
##
def _set_doc_latest(doc):
  docutils_obj = DocumentUtils()
  latest = docutils_obj.get_latest_doc(doc.id)
  doc.latest(latest.id, latest.created_at, latest.creator.email)

def _get_doc_relations(doc):
  relates_to = doc.rels_as_doc_0.values('relationship__type').annotate(count=Count('relationship'))
  is_related_from = doc.rels_as_doc_1.values('relationship__type').annotate(count=Count('relationship'))
  return relates_to, is_related_from
  

def _render_documents(request, docs, record, pha, tdc, format_type='xml'):
  # tdc: Total Document Count
  if docs:
    for doc in docs:
      if doc.id:
        _set_doc_latest(doc)
        doc.relates_to, doc.is_related_from = _get_doc_relations(doc)

  return utils.render_template('documents', {  'docs'    : docs, 
                                               'record'  : record, 
                                               'pha'     : pha, 
                                               'tdc'     : tdc}, 
                                                type=format_type)

def _get_document(docbox, document_id=None, pha=None, external_id=None):
  """Get a document with the given doc id/(external id and pha) and record"""
  doc = None
  try:
    if document_id:
      doc = Document.objects.get(record=docbox.record, pha=pha, id=document_id)
    elif external_id:
      if docbox.record:
        doc = docbox.record.documents.get(record=docbox.record, pha=pha, external_id=external_id)
      else:
        doc = Document.objects.get(record=None, pha=pha, external_id=external_id)
  except Document.DoesNotExist:
    return None
  return doc

def __document_create(doc, content, doc_args):
    # determine if this is text content or binary content
    if doc.is_binary:
      file = ContentFile(content)
      doc_args[CONTENT] = None
      doc_args[SIZE]    = file.size
      doc_args[DIGEST]  = hashlib.sha1(content).hexdigest()
    else:
      doc_args[CONTENT] = content
      doc_args[SIZE]    = doc.get_document_size()
      doc_args[DIGEST]  = doc.get_document_digest()
      doc_args[TYPE]    = doc.get_document_schema()
      
    # create the document
    new_doc = Document.objects.create(**doc_args)
    # binary
    if doc.is_binary:
      file = ContentFile(content)
      new_doc.content_file.save(new_doc.id, file)

    return new_doc

def _process_doc(content, pha):
  """process the document into medical facts. exceptions are passed up without processing."""
  if content:
    doc           = DocumentProcessing(content)
    doc.is_binary = DocumentUtils().is_binary(content)
    if not pha:
      doc.process()
    doc.get_document_schema()
    return doc
  
  return False

def _replace_document(doc, replaces_document, pha):
  is_existing_pha_doc = False
  # are we replacing a document?
  if replaces_document:
    original_id = replaces_document.original_id
    if replaces_document.replaced_by:
      raise Exception("cannot replace a document that is already replaced")
    is_existing_pha_doc = original_id and pha
    # a PHA document that already exists? replace its content
    if is_existing_pha_doc:
      if not doc.is_binary:
        replaces_document.type    = doc.get_document_schema()
        replaces_document.digest  = doc.get_document_digest()
        replaces_document.size    = doc.get_document_size()
        replaces_document.content = doc.content
      replaces_document.save()
      return True
  return False

def _update_fact_doc(doc, docbox, replaces_document, new_doc):
  # SZ: if document_processing returns a fact object
  if not doc.is_binary and hasattr(doc, 'f_objs'):
    for fobj in doc.f_objs:
      if replaces_document:
        fobj.__class__.objects.filter(
          document = replaces_document).delete()
      if fobj:
        # Update the fact with the source doc and record
        fobj.document = new_doc
        fobj.record   = docbox.record
        fobj.save()
  return True
  
def _document_create(creator, content, pha, record=None,
                     docbox=None, replaces_document=None, external_id=None, mime_type=None,
                     status = None):
  """ Create an Indivo Document

  This is called for both document creation within a record
    and document creation within a record for a specific application.

  The PHA argument, if non-null, indicates app-specificity only.
  By this point, the external_id should be fully formed.

  FIXME: figure out the transactional aspect here

  If status is specified, then it is used, otherwise it is not specified and the DB does its default thing.
  """
  doc, new_doc, original_id   = _process_doc(content, pha), None, None
  docbox                      = docbox if not record and docbox else Docbox(record)
  creator                     = creator.effective_principal

  if not _replace_document(doc, replaces_document, pha):
    # this condition needs to be copied here so we
    # don't forget to set the original_id
    if replaces_document:
      original_id = replaces_document.original_id
    
    doc_args = {  PHA         : pha,
                  RECORD      : docbox.record,
                  CREATOR     : creator,
                  MIME_TYPE   : mime_type,
                  EXTERNAL_ID : external_id,
                  ORIGINAL_ID : original_id
                }

    if status:
      doc_args['status'] = status

    # SZ: Find new name for __document_create
    new_doc = __document_create(doc, content, doc_args)
    if replaces_document and new_doc:
      replaces_document.replaced_by = new_doc
      replaces_document.save()

  _update_fact_doc(doc, docbox, replaces_document, new_doc)
    
  # return new doc if we have it, otherwise updated old doc
  return new_doc or replaces_document

def __local_document_create(request, docbox, pha, external_id, existing_doc):
  """
  This function only serves document_create and document_create_or_update
  The pha argument is null for medical data, non-null for app-specific
  The external_id is expected to be already adjusted
  """
  try:
    doc = _document_create( docbox              = docbox, 
                          creator             = request.principal,
                          pha                 = pha, 
                          content             = request.raw_post_data, 
                          external_id         = external_id,
                          replaces_document   = existing_doc,
                          mime_type           = utils.get_content_type(request))
  except ValueError, e:
    return HttpResponseBadRequest("the document submitted is malformed:" + str(e))

  _set_doc_latest(doc)
  return utils.render_template('document', {'record'  : doc.record, 
                                            'doc'     : doc, 
                                            'pha'     : pha }) 


@commit_on_200
@paramloader('docbox')
def document_create(request, docbox, pha=None, document_id=None, external_id=None):
  """
  Create a document, possibly with the given external_id
  This call is ONLY made on NON-app-specific data,
  so the PHA argument is non-null only for specifying an external_id
  """
  return __local_document_create(request, docbox, pha=None,
                                 external_id = Document.prepare_external_id(external_id, pha),
                                 existing_doc=None)

@commit_on_200
@paramloader('docbox')
def document_create_or_update(request, docbox, pha, document_id=None, external_id=None):
  """
  Create a document, possibly with the given external_id
  This call is ONLY made on app-specific data,
  and the pha argument indicates the app-specificity
  """
  existing_doc = None

  # set the external ID up properly
  full_external_id = Document.prepare_external_id(external_id, pha,
                                                  pha_specific=True, record_specific= (docbox.record != None))

  if document_id or external_id:
    existing_doc = _get_document(docbox, document_id, pha, full_external_id)

  return __local_document_create(request, docbox, pha, full_external_id, existing_doc)

@paramloader('docbox')
def document(request, document, docbox=None, pha=None):
  """Retrieve a document | Retrieval with external_id is not permitted"""

  if pha and document.pha != pha:
    raise Http404

  # no content, must be a file
  if not document.content:
    return HttpResponse(document.content_file, mimetype=document.mime_type)

  return HttpResponse(document.content, mimetype="application/xml")

@paramloader()
@marsloader
def document_list(request, limit, offset, status, order_by='created_at', 
                    record=None, pha=None, docbox=None):
  """
  As of 2010-08-16, type is no longer part of the URL, it's only in the GET
  query parameters
  """
  # SZ: CLEAN CODE!
  # SZ: CLEAN CODE!
  # SZ: CLEAN CODE!
  type = request.GET.get('type', None)
  type = DocumentProcessing.expand_schema(type)

  try:
    if type:
      try:
        type_obj = DocumentSchema.objects.get(type=type)
        if record:
          docs = record.documents.filter(type=type_obj, 
                                         replaced_by=None, 
                                         status=status, 
                                         pha=pha).order_by(order_by)
        else:
          docs = Document.objects.filter(type=type_obj, 
                                         pha=pha, 
                                         replaced_by=None, 
                                         status=status).order_by(order_by)
        return _render_documents(request, docs, record, pha, docs.count())
      except DocumentSchema.DoesNotExist:
        raise Http404
    docs = Document.objects.filter(record=record, 
            replaced_by=None, pha=pha, status=status).order_by(order_by)
  except:
    docs = []
  return _render_documents(request, docs[offset:offset+limit], record, pha, len(docs))
