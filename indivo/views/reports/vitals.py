"""
Indivo Views -- Vitals
"""
import datetime
from django.http import HttpResponseBadRequest
from indivo.lib.view_decorators import paramloader, marsloader
from indivo.lib.utils import render_template, carenet_filter
from indivo.models import *
from reportutils import report_orderby_update
from itertools import groupby

@paramloader()
@marsloader
def vitals_list(request, limit, offset, status, category=None, order_by='-created_at', record=None, carenet=None):
  if carenet:
    record = carenet.record
  if not record:
    return HttpResponseBadRequest()

  occurred_min = request.GET.get('occurred-min', None)
  occurred_max = request.GET.get('occurred-max', None)
  aggregation  = request.GET.get('aggregation', None)
  segmentation = request.GET.get('segmentation', None)

  processed_order_by = report_orderby_update(order_by)

  vitals = Vitals.objects.select_related().filter(record=record, document__status=status)
  
  #Apply all the different filters
  if category:
    # change underscores to spaces in the category, to make it easier without URL encoding
    category = category.replace("_"," ")
    vitals = vitals.filter(name=category)
  
  if occurred_min:
    occurred_min = datetime.datetime.strptime(occurred_min, "%Y-%m-%dT%H:%M:%SZ")
    vitals = vitals.filter(date_measured__gte = occurred_min)
  
  if occurred_max:
    occurred_max = datetime.datetime.strptime(occurred_max, "%Y-%m-%dT%H:%M:%SZ")
    #If there is no date_measured_end then it should be date_measured (start)
    vitals = vitals.filter(date_measured_end__lte = occurred_max)

  #Create the segments
  
  #These functions are methods in the class of vitals
  segmentation_functions = {
    "weekday"    : lambda v: v.weekday(),
    "hourofday"  : lambda v: v.hour_of_day(),
    "hour"       : lambda v: v.hour(),
    "day"        : lambda v: v.day(),
    "week"       : lambda v: v.week(),
    "weekofyear" : lambda v: v.week_of_year(),
    "month"      : lambda v: v.month(),
    "year"       : lambda v: v.year()
  }

  if segmentation:
    if segmentation in segmentation_functions.keys():
      temp = {}
      for key, group in groupby(vitals, segmentation_functions[segmentation]):
        temp[key] = [vital for vital in group]
    vitals = temp 
    # at this point we have a dictionary where Keys are the 
    #segment identifiers and the values are lists of vitals

  #Aggregation functions
 
  sum_vitals = lambda l: reduce(lambda x,y: x + y.value, l, 0)
    
  aggregation_functions = {
    "sum" : lambda l: sum_vitals(l),
    "avg" : lambda l: sum_vitals(l) / float(len(l)),
    "min" : lambda l: min(l, key=lambda x: x.value).value,
    "max" : lambda l: max(l, key=lambda x: x.value).value
  }
  
  #Apply the aggregation functions
  if aggregation:
    #Apply the aggregation if we know how to do
    if aggregation in aggregation_functions.keys():
      temp = []
      for key in vitals.keys():
        #res.append(vitals[k].aggregate(functions[aggregation]('value')))
        #value = reduce(lambda x,y: x + y.value, vitals[k], 0)
        value = aggregation_functions[aggregation](vitals[key])
        vital = Vitals(value = value, 
                       name = "Step Count", 
                       unit = "steps")
        vital.index = key
        temp.append(vital)
    vitals = temp
 
  #Apply carenet_filter and order the results
  #vitals = carenet_filter(carenet, vitals.order_by(processed_order_by))
  vitals = carenet_filter(carenet, vitals)
  #FIX: The ordering data does not work on a normal list. Only in querysets
 
  #Select the template depending if is aggregated vitals or not
  if aggregation:
    template = "reports/vitals_aggregation"
  else:
    template = "reports/vitals" 

  return render_template(template, 
                          { 'vitals' : vitals[offset:offset+limit],
                            'trc' : len(vitals),
                            'limit' : limit,
                            'offset' : offset,
                            'order_by' : order_by
                          }, type='xml')
