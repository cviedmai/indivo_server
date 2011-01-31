from indivo.views.base import *

@paramloader()
def document_delete(request, document, record):
  """Delete a recently added document, only if it was recently added by the same person"""

  # FIXME: modularize timedelta(hours=1)
  # For now, 1 hour
  if document.creator == request.principal.effective_principal and \
      datetime.datetime.now() - document.created_at < datetime.timedelta(hours=1):

    # we mean explicitly for this to fail 
    # if the document is referenced by anything in the DB

    document.delete()
    return DONE
  else:
    raise Exception("document was inserted too long ago to allow this, or was not created by you")

@paramloader()
def documents_delete(request, record):
  Document.objects.filter(record=record).delete()
  return DONE
