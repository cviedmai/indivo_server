from indivo.views.base import *
from indivo.views.documents.document import _render_documents, _get_document

@paramloader()
def document_label(request, record, document=None, external_id=None, pha=None, app_specific=False):
  """
  set the document label
  """
  label = request.raw_post_data

  # set up the full external id and potentially clear the PHA variable
  # if it was just meant for selecting the external ID
  full_external_id = Document.prepare_external_id(external_id, pha, pha_specific = app_specific)
  if not app_specific:
    pha = None

  if document:
    if pha and document.pha != pha:
      raise Http404

    if record and document.record != record:
      raise Http404
  else:
    document = record.documents.get(external_id=full_external_id, pha=pha)
  document.label = label
  document.save()

  return _render_documents(request, [document], record, pha, 1)
