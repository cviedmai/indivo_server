from indivo.views.base import *
from indivo.views.documents.document import _set_doc_latest, _get_doc_relations

@paramloader('docbox')
def update_document_meta(request, docbox, document):
  return DONE

@paramloader('docbox')
def document_meta(request, docbox, document=None, pha=None, external_id=None, app_specific = False):
  """
  The metadata for a single document
  
  The app-specific parameter needs to be specified in the URL route
  """

  if not document:
    try:
      if docbox and docbox.record:
        full_external_id = Document.prepare_external_id(external_id, pha = pha, pha_specific = app_specific)

        # clear the pha argument if it's not app specific
        if not app_specific:
          pha = None

        document = docbox.record.documents.get(record=docbox.record, pha=pha, external_id = full_external_id)
      else:
        full_external_id = Document.prepare_external_id(external_id, pha = pha,
                                                        pha_specific = app_specific, record_specific=False)
        document = Document.objects.get(record=None, pha=pha, external_id = full_external_id)
    except Document.DoesNotExist:
      raise Http404
    except MultipleObjectsReturned:
      return HttpResponseBadRequest("Multiple external_ids returned, db is in a corrupted state")
  _set_doc_latest(document)

  # related stuff
  document.relates_to, document.is_related_from = _get_doc_relations(document)

  return render_template('single_document', {'doc' : document, 'record': document.record})
