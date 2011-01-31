from indivo.views.base import *
from indivo.views.documents.document import _document_create, _render_documents, _set_doc_latest

@transaction.commit_on_success
@paramloader()
def document_version(request, record, document, pha=None, external_id=None):
  """Version a document, *cannot* be a non-record document"""

  full_external_id = Document.prepare_external_id(external_id, pha)

  try:
    new_doc = _document_create(record=record, 
                               creator=request.principal, 
                               content=request.raw_post_data,
                               replaces_document = document, 
                               pha=None,
                               external_id = full_external_id,
                               mime_type=utils.get_content_type(request))
  except:
    raise Http404

  _set_doc_latest(new_doc)
  return render_template('document', {'record'  : record, 
                                      'doc'     : new_doc, 
                                      'pha'     : None })

@paramloader()
@marsloader
def document_versions(request, record, document, limit, offset, status, order_by='created_at', pha=None):
  """Retrieve the versions of a document"""
  try:
    docs = Document.objects.filter( original  = document.original_id, 
                                    status    = status).order_by(order_by)
  except:
    raise Http404
  return _render_documents(request, docs[offset:offset+limit], record, pha, len(docs))
