"""
Decorators for views
"""

from django.http import HttpResponse, HttpResponseRedirect, Http404
from indivo import models
from indivo import check_safety
from indivo.document_processing.docbox import Docbox

from django.db.transaction import commit_on_success, rollback
from functools import wraps

import inspect
import functools, copy, logging

# This should be abstracted
ID    = 'id'
EMAIL = 'email'
QPARAM_RELS = { 
  'account_email'   : ( 'account',  models.Account,  EMAIL ),
  'account_id'      : ( 'account',  models.Account,  EMAIL ),
  'carenet_id'      : ( 'carenet',  models.Carenet,  ID    ),
  'document_id'     : ( 'document', models.Document, ID    ), 
  'pha_email'       : ( 'pha',      models.PHA,      EMAIL ),
  'record_id'       : ( 'record',   models.Record,   ID    )
}


def paramloader(*params):
  """
  paramloader pre-processes parameters that are passed to Indivo views,
  so that the views don't have to do repetitive things like loading records,
  loading documents, etc...

  IMPORTANT paramloader removes any arguments with double-underscore prefixes as names,
  since these are used for access control.
  """
  def paramloader_decorator(func):
    def _get_params_intersection(new_args):
      qparam_list = {}
      for tmp_qparam, tmp_qparam_rel in QPARAM_RELS.items():
        if new_args.has_key(tmp_qparam):
          qparam_list[tmp_qparam] = tmp_qparam_rel
      return qparam_list

    def _remove_non_appspecific_pha(request, req_path, new_args):
      """ Remove non-app-specific pha from arg list"""

      # SZ: Hack, re-organize
      PHA = 'pha'
      if PHA in new_args and 'apps' not in req_path:
        del new_args[PHA]
      return new_args

    def _init_docbox(params):
      docbox_obj = None
      insert_docbox = 'docbox' in params
      if insert_docbox:
        docbox_obj = Docbox()
      return docbox_obj, insert_docbox

    def paramloaded_func(request, **kwargs):
      """ A decorator for automatically loading URL-based parameters 
          that are in standard form.
      """
      
      DOCBOX      = 'docbox'
      # SZ: Add pha
      docbox_list = ('carenet', 'record')

      # Init
      check_safety()
      new_args                  = copy.copy(kwargs)

      # immediately remove the double-underscore parameters
      for arg_name in new_args.keys():
        if arg_name[:2] == "__":
          del new_args[arg_name]

      req_path                  = request.path_info.split('/')
      params_intersect          = _get_params_intersection(new_args)
      docbox_obj, insert_docbox = _init_docbox(params)

      for qparam, qparam_rel in params_intersect.items():
        # If the argument given is None then keep it as None
        if new_args[qparam] is None:
          new_args[qparam_rel[0]] = None
          del new_args[qparam]
        else:
          try:
            query_kwargs = {qparam_rel[2] : new_args[qparam]}
            res_obj = qparam_rel[1].objects.get(**query_kwargs)
            if qparam_rel[0] in docbox_list and insert_docbox:
              new_args[DOCBOX] = docbox_obj.set(res_obj)
            else:
              new_args[qparam_rel[0]] = res_obj
            del new_args[qparam]
          except Exception, e:
            raise Http404

      # removed by Ben, this can lead to some serious problems down the road
      # as it changes the developer's expectation and magically removes
      # a parameter. I'd rather have a bit more code where each view is much
      # more explicit.
      #
      # new_args = _remove_non_appspecific_pha(request, req_path, new_args)

      # Hack, remove
      if insert_docbox and not DOCBOX in new_args:
        new_args[DOCBOX] = Docbox()
      return func(request, **new_args)
    return functools.update_wrapper(paramloaded_func, func)
  return paramloader_decorator

def marsloader(func):
  def marsloader_func(request, *args, **kwargs):
    """MARS_loader (Modifying Arguments for the Result Set) 
      
      adds arguments specifically meant to modify the result set 
      (eg. limit, offset and order_by)
    """

    check_safety()

    STATUS = 'status'

    # This should be abstracted
    # StatusName 'active' should always be available
    arg_list = [  ('limit', 100), 
                  ('offset', 0),
                  ('order_by', '-created_at'),
                  (STATUS, models.StatusName.objects.get(name='active'))]

    new_args = copy.copy(kwargs)
    rsm_arg_list = {}
    for arg in arg_list:
      rsm_arg_list[arg[0]] = arg[1]

    # All paths that end in a slash and have an HTTP method of GET will return a result set
    rsm_cand = request.method == 'GET' and request.META['PATH_INFO'][-1] == '/'
    if rsm_cand:
      for rsm_arg, qdefault in rsm_arg_list.items():
        if request.GET.has_key(rsm_arg):
          if rsm_arg == STATUS:
            try:
              new_args[rsm_arg] = models.StatusName.objects.get(name=request.GET[rsm_arg])
            except models.StatusName.DoesNotExist:
              raise Http404
              new_args[rsm_arg] = qdefault
          else:
            try:
              new_args[rsm_arg] = int(request.GET[rsm_arg])
            except:
              new_args[rsm_arg] = request.GET[rsm_arg]
        else:
          new_args[rsm_arg] = qdefault

    # Check that the new arguments are all in func()
    if len(inspect.getargspec(func)) > 0:
      for new_arg in new_args.keys():
        if new_arg not in inspect.getargspec(func)[0]:
          raise Exception("Missing arg " + new_arg + " in " + func.func_name)
    return func(request, **new_args)
  return functools.update_wrapper(marsloader_func, func)


##
## transaction management
##

def commit_on_200(func):
  """
  Commit changes to the database only if the response is a 200.
  Anything else causes a rollback.
  This is a more stringent version of commit_on_success, which
  only rolls back in the case of an exception.

  The idea here is that first we call the func, and if it returns a bad result
  we do a rollback. The exception catching, we leave to the commit_on_success wrapper,
  which we wrap around ourselves
  """

  @wraps(func)
  def _inner_commit(*args, **kwargs):
    result = func(*args, **kwargs)
    if not hasattr(result, 'status_code') or result.status_code != 200:
      rollback()

    return result

  # layer the commit_on_successoutside of our first check for 200
  # note that, if the wrapped func raises an exception, it goes 
  # right through our decorator here (like butter), and hits the commit_on_success
  # handler which will roll back the transaction then. We keep it simple.
  return commit_on_success(_inner_commit)
      
      
