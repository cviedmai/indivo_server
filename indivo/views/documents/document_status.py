from indivo.views.base import *

@paramloader()
@transaction.commit_on_success
def document_set_status(request, record, document):
  status_str, reason_str = 'status', 'reason'
  if not (request.POST.has_key(status_str) and \
          request.POST.has_key(reason_str) and \
          document.set_status(request, 
                              request.POST[status_str], 
                              request.POST[reason_str])):
    return HttpResponseBadRequest()
  return DONE

@paramloader()
@marsloader
def document_status_history(request, record, document):
  return render_template('document_status_history', 
          { 'document_id'      : document.id,
            'document_history' : DocumentStatusHistory.objects.filter(
                                  record    = record.id, 
                                  document  = document.id)})
