"""
Indivo Views -- Measurements
"""

from django.http import HttpResponseBadRequest
from indivo.lib.view_decorators import paramloader, marsloader
from indivo.lib.utils import render_template, carenet_filter
from indivo.models import *
from reportutils import report_orderby_update

@paramloader()
@marsloader
def measurement_list(request, limit, offset, status, order_by, lab_code, record=None, carenet=None):
  """
  Func for listing measurements
  """

  if carenet:
    record = carenet.record
  if not record:
    return HttpResponseBadRequest()

  processed_order_by = report_orderby_update(order_by)

  measurements = carenet_filter(carenet,
                  Measurement.objects.select_related().filter(
                    record=record, 
                    document__status=status).order_by(processed_order_by))
  return render_template('reports/measurements', 
                          { 'measurements': measurements[offset:offset+limit],
                            'record': record,
                            'trc' : len(measurements),
                            'limit' : limit,
                            'offset' : offset,
                            'order_by' : order_by}, 
                          type="xml")
