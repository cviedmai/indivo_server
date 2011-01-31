from django.conf.urls.defaults import *

from indivo.views import *
from indivo.lib.utils import MethodDispatcher

urlpatterns = patterns('',
    ##
    ## Application-Specific Data Storage
    ##

    # List of app-specific documents / create a doc
    (r'^/documents/$', 
      MethodDispatcher({ 'GET': document_list, 'POST': document_create_or_update})),

    # create app-specific doc by document external ID
    (r'^/documents/external/(?P<external_id>[^/]+)$', 
      MethodDispatcher({'PUT': document_create_or_update})),

    # One app-specific document
    # app-specific document replace
    (r'^/documents/(?P<document_id>[^/]+)$', 
      MethodDispatcher({'GET': document, 'PUT': document_create_or_update})),

    # update
    (r'^/documents/(?P<document_id>[^/]+)/update$', pha_document_update),

    # One app-specific document's metadata
    # and app-specific document metadata by external ID
    (r'^/documents/(?P<document_id>[^/]+)/meta$', 
      MethodDispatcher({'GET': document_meta}), {'app_specific': True}),
    (r'^/documents/external/(?P<external_id>[^/]+)/meta$', 
      MethodDispatcher({'GET': document_meta}), {'app_specific': True}),

    # app-specific document label
    # FIXME: not sure this view works
    (r'^/documents/(?P<document_id>[^/]+)/label$', document_label, {'app_specific': True}),

    # app-specific document types
    (r'^/documents/types/(?P<type>[A-Za-z0-9._%-:#]+)/$', document_list)
)
