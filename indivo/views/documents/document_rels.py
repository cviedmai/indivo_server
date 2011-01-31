from indivo.views.base import *
from indivo.views.documents.document import _document_create, _render_documents

@paramloader()
@marsloader
def get_documents_by_rel(request, record, document, rel, limit, offset, status, order_by='id', pha=None):
  tdc = 0 
  try:
    # SZ: Make more readable!
    # SZ: add limit, offset, order_by support
    relationship = DocumentSchema.objects.get(type=DocumentSchema.expand_rel(rel))
    docs = [x for x in [[relation.document_1 \
                for relation in doc.rels_as_doc_0.filter(relationship=relationship).select_related()] \
                  for doc in [document \
                    for document in Document.objects.filter(status=status, 
                      original=document.original_id)]] \
                        if len(x) > 0][0]
    tdc = len(docs)
  except:
    docs = []
  return _render_documents(request, docs, record, pha, tdc)

@paramloader()
def document_rels(request, record, document_id_0, rel, document_id_1=None):
  """
  create a new document relationship, either with paylod of a new document, or between existing docs.
  2010-08-15: removed external_id and pha parameters as they are never set.
  That's for create_by_rel
  """
  try:
    document_0    = Document.objects.get(id = document_id_0)
    relationship  = DocumentSchema.objects.get(type= DocumentSchema.expand_rel(rel))
    if document_id_1:
      document_1 = Document.objects.get(id = document_id_1)
    else:
      try:
        document_1 = _document_create(record=record, 
                                      creator=request.principal,
                                      content=request.raw_post_data,
                                      mime_type=utils.get_content_type(request))
      except:
        raise Http404
    DocumentRels.objects.create(document_0=document_0, document_1=document_1, relationship=relationship)
  except:
    raise Http404
  return DONE

@paramloader()
@transaction.commit_on_success
def document_create_by_rel(request, record, document, rel, pha=None, external_id=None):
  """Create a document and relate it to an existing document, all in one call.
  
  FIXME: currently ignoring app_email
  """

  # no rels in app-specific docs
  full_external_id = Document.prepare_external_id(external_id, pha=pha, pha_specific = False)

  try:
    # create the doc
    new_doc = _document_create( record = record, 
                                creator = request.principal,
                                pha = None,
                                content = request.raw_post_data,
                                external_id = full_external_id)
    # create the rel
    DocumentRels.objects.create(document_0 = document, 
                                document_1 = new_doc, 
                                relationship = DocumentSchema.objects.get(type=DocumentSchema.expand_rel(rel)))
  except:
    raise Http404
  return DONE
