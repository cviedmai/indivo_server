from django.conf.urls.defaults import *

from indivo.views import *
from indivo.lib.utils import MethodDispatcher

urlpatterns = patterns('',

    # reset
    (r'^reset$', account_reset),

    # set state
    (r'^set-state$', MethodDispatcher({'POST' : account_set_state})),

    # update info
    (r'^info-set$', MethodDispatcher({'POST': account_info_set})),

    # auth systems
    (r'^authsystems/$', MethodDispatcher({ 'POST' : account_authsystem_add})),

    # change the password
    (r'^authsystems/password/change$', MethodDispatcher({
                'POST' : account_password_change})),

    # set the password
    (r'^authsystems/password/set$', MethodDispatcher({
                'POST' : account_password_set})),

    # set the username
    (r'^authsystems/password/set-username$', MethodDispatcher({
                'POST' : account_username_set})),

    # URL to initialize account
    (r'^initialize/(?P<primary_secret>[^/]+)$', MethodDispatcher({
                'POST' : account_initialize})),
    (r'^check-secrets/(?P<primary_secret>[^/]+)$', MethodDispatcher({
                'GET' : account_check_secrets})),

    # URL to resend the login URL
    (r'^secret-resend$', account_resend_secret),

    # secret
    (r'^secret$', account_secret),

    # primary secret (very limited call)
    (r'^primary-secret$', account_primary_secret),

    # record list 
    (r'^records/$', record_list),

    # send a message or read the inbox
    (r'^inbox/$', MethodDispatcher({
                'GET' : account_inbox,
                'POST': account_send_message})),

    # read a message
    (r'^inbox/(?P<message_id>[^/]+)$',
      MethodDispatcher({'GET' : account_inbox_message})),

    # archive a message
    (r'^inbox/(?P<message_id>[^/]+)/archive$',
      MethodDispatcher({'POST' : account_message_archive})),

    # accept an attachment
    (r'^inbox/(?P<message_id>[^/]+)/attachments/(?P<attachment_num>[^/]+)/accept$', MethodDispatcher({
                'POST': account_inbox_message_attachment_accept})),

    # healthfeed
    (r'^notifications/$', account_notifications),

    (r'^permissions/$', MethodDispatcher({
                'GET' : account_permissions
                })), 
)    
