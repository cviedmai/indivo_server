"""
Indivo Views -- Auditing
"""

import logging
from base import *

# SZ: Ignore order_by, use req_datetime

@paramloader()
@marsloader
def audit_function_view(request, record, document, function_name, limit, offset, order_by, status=None):
  try:
    audits = Audit.objects.filter(  record=record.id,
                                    document=document.id, 
      req_view_func=function_name).order_by('req_datetime').reverse()[offset:offset+limit]
    return render_template('audit', {'audits' : audits}, type='xml')
  except:
    raise Http404

@paramloader()
@marsloader
def audit_record_view(request, record, limit, offset, order_by, status = None):
  try:
    audits = Audit.objects.filter(record=record.id).order_by('req_datetime').reverse()[offset:offset+limit]
    return render_template('audit', {'audits' : audits}, type='xml')
  except:
    raise Http404

@paramloader()
@marsloader
def audit_document_view(request, record, document, limit, offset, order_by, status=None):
  try:
    audits = Audit.objects.filter(  record=record.id,
                                    document=document.id).order_by('req_datetime').reverse()[offset:offset+limit]
    return render_template('audit', {'audits' : audits}, type='xml')
  except:
    raise Http404
