"""
Middleware (filters) for Indivo

inspired by django.contrib.auth middleware, but doing it differently
for tighter integration into email-centric users in Indivo.
"""

import re
import indivo

from time import strftime
from django.http import *
from django.core.exceptions import PermissionDenied
from django.conf import settings

class Authorization(object):

  def process_view(self, request, view_func, view_args, view_kwargs):
    """ The process_view() hook allows us to examine the request before view_func is called"""

    # Url exception(s)
    exc_pattern= settings.INDIVO_ACCESS_CONTROL_EXCEPTION
    if exc_pattern and re.match(exc_pattern, request.path):
      return None
 
    if hasattr(view_func, 'resolve'):
      view_func = view_func.resolve(request)

    try:
      if view_func:
        access_rule = self.get_permset(request, view_args, view_kwargs).evaluate(view_func)
        if access_rule and access_rule(request, request.principal, view_args, view_kwargs):
          return None
    except:
      raise PermissionDenied
    raise PermissionDenied

  def get_permset(self, request, view_args, view_kwargs):
    if hasattr(request, 'principal'):
      if request.principal:
        permset         = request.principal.permset
        permset.request = request
        permset.view_args, permset.view_kwargs = view_args, view_kwargs
      else:
        if request.META.has_key('HTTP_AUTHORIZATION'):
          return False
        else:
          permset = indivo.accesscontrol.PermissionSetType().nouser()
      return permset
    else:
      return False

# Mark that the authorization module has been loaded
# nothing gets served otherwise
indivo.AUTHORIZATION_MODULE_LOADED = True
