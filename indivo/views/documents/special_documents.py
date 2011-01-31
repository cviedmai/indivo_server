from indivo.views.base import *
from indivo.views.documents.document import _document_create, _set_doc_latest

def special_document(request, record, document_alias):
  if document_alias == 'demographics':
    pass
  if document_alias == 'contact':
    pass

  # no such thing
  raise Http404
  
def special_document_update(request, record, document_alias):
  if document_alias == 'demographics':
    pass
  if document_alias == 'contact':
    pass

  # no such thing
  raise Http404

def get_special_doc(record, carenet, special_document):
  """
  Get a special doc
  either carenet or record must be non-null"""

  if record is None and carenet is None:
    raise ValueError("carenet or record must be non-null")

  the_doc = None

  docbox = record or carenet
    
  if special_document == 'demographics':
    the_doc = docbox.demographics
  if special_document == 'contact' :
    the_doc = docbox.contact

  return the_doc

def set_special_doc(record, special_document, new_doc):
  """Update the pointer to a new special doc"""

  if special_document == 'demographics':
    record.demographics = new_doc
  if special_document == 'contact' :
    record.contact = new_doc

    # update the label
    record.label = Contacts.from_xml(new_doc.content).full_name
  record.save()

@paramloader()
def read_special_document(request, special_document, record=None, carenet=None):
  """Read a special document"""
  doc = get_special_doc(record, carenet, special_document)
  if not doc:
    raise Http404
  return HttpResponse(doc.content, mimetype="application/xml")

@paramloader()
@transaction.commit_on_success
def save_special_document(request, record, special_document):
  """Save a new special document """
  
  doc = get_special_doc(record, carenet=None, special_document=special_document)

  # this will do the right thing in terms of replacement
  new_doc = _document_create(record=record, 
                             creator=request.principal, 
                             content=request.raw_post_data,
                             pha=None,
                             replaces_document=doc)

  # update the record pointer
  set_special_doc(record, special_document, new_doc)

  _set_doc_latest(new_doc)
  return render_template('document', { 'record'  : record, 
                                              'doc'     : new_doc, 
                                              'pha'     : None})
