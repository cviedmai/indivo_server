from django.conf.urls.defaults import *

from indivo.views import *
from indivo.lib.utils import MethodDispatcher

urlpatterns = patterns('',
    (r'^/record$', carenet_record),
    (r'^/accounts/$',
                MethodDispatcher({
                  'GET'  : carenet_account_list, 
                  'POST' : carenet_account_create
                })), 
    (r'^/documents/', include('indivo.urls.carenet_documents')),
    (r'^/accounts/(?P<account_id>[^/]+)$', 
      MethodDispatcher({ 'DELETE' : carenet_account_delete })), 
    (r'^/apps/$', 
      MethodDispatcher({ 'GET' : carenet_apps_list})),
    (r'^/apps/(?P<pha_email>[^/]+)$', 
      MethodDispatcher({  'PUT' : carenet_apps_create,
                          'DELETE': carenet_apps_delete})),
    (r'^/accounts/(?P<account_id>[^/]+)/permissions$', 
      MethodDispatcher({ 'GET' : carenet_account_permissions })),
    (r'^/apps/(?P<app_id>[^/]+)/permissions$', 
      MethodDispatcher({ 'GET' : carenet_app_permissions })),
    (r'^/reports/minimal/immunizations/$',               immunization_list), 
    (r'^/reports/minimal/allergies/$',                   allergy_list), 
    (r'^/reports/minimal/procedures/$',                  procedure_list), 
    (r'^/reports/minimal/problems/$',                    problem_list), 
    (r'^/reports/minimal/medications/$',                 medication_list), 
    (r'^/reports/minimal/equipment/$',                   equipment_list), 
    (r'^/reports/minimal/vitals/$',                      vitals_list), 
    (r'^/reports/minimal/vitals/(?P<category>[^/]+)$',   vitals_list), 
    (r'^/reports/minimal/measurements/(?P<lab>[^/]+)/$', measurement_list)
)
