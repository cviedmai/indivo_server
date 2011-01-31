from django.conf.urls.defaults import *

from indivo.views import *
from indivo.lib.utils import MethodDispatcher

urlpatterns = patterns('',
  (r'^$', record_phas),
  (r'^(?P<pha_email>[^/]+)$', 
      MethodDispatcher({'GET' : record_pha, 'DELETE': pha_record_delete})),
  
  # List of app-specific documents / create a doc
  (r'^(?P<pha_email>[^/]+)/documents/$', 
      MethodDispatcher({
              'GET'  : document_list,
              'POST' : document_create_or_update})),
  
  # create app-specific doc by document external ID
  (r'^(?P<pha_email>[^/]+)/documents/external/(?P<external_id>[^/]+)$', 
      MethodDispatcher({
              'POST' : document_create_or_update, 
              'PUT'  : document_create_or_update})),

  # One app-specific document
  (r'^(?P<pha_email>[^/]+)/documents/(?P<document_id>[^/]+)$', MethodDispatcher({
                'GET': document})),

  # update
  (r'^(?P<pha_email>[^/]+)/documents/(?P<document_id>[^/]+)/update$', pha_document_update),
  
  # One app-specific document's metadata
  (r'^(?P<pha_email>[^/]+)/documents/(?P<document_id>[^/]+)/meta$', 
      MethodDispatcher({'GET': document_meta}), {'app_specific' : True}),

  # app-specific document metadata by external ID 
  (r'^(?P<pha_email>[^/]+)/documents/external/(?P<external_id>[^/]+)/meta$', 
      MethodDispatcher({'GET': document_meta}), {'app_specific' : True}),

  # app-specific set document label
  (r'^(?P<pha_email>[^/]+)/documents/(?P<document_id>[^/]+)/label$', document_label, {'app_specific': True}),

  # app-specific document types
  (r'^(?P<pha_email>[^/]+)/documents/types/(?P<type>[A-Za-z0-9._%-:#]+)/$', document_list),

  # setup a PHA completely (pre-auth'ed)
  (r'^(?P<pha_email>[^/]+)/setup$', record_pha_setup)
)
