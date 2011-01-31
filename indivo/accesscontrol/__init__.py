import sys

try:
  from indivo import views
except:
  # TEMPORARY HACK
  pass

ACCESSCONTROL_MODULE = 'indivo.accesscontrol'

def _resolve_name(name, package, level):
  if not hasattr(package, 'rindex'):
    raise ValueError("'package' not set to a string")
  dot = len(package)
  for x in xrange(level, 1, -1):
    try:
      dot = package.rindex('.', 0, dot)
    except ValueError:
      raise ValueError("attempted relative import beyond top-level")
  return "%s.%s" % (package[:dot], name)

def import_module(name, package=None):
  level = 0 
  for character in name:
    if character != '.':
      break
    level += 1
  name = _resolve_name(name[level:], package, level)
  __import__(name)
  return sys.modules[name]

def get_permset(name, object=None):
  try:
    # Look for a module named 'name'
    module = import_module(name, ACCESSCONTROL_MODULE)
    if hasattr(module, name):
      return getattr(module, name)(object)
  except ImportError:
    # Otherwise look in the PermissionSetType class
    if hasattr(PermissionSetType, name):
      return getattr(PermissionSetType(), name)(object)
    return False
  return False

class PermissionSet(object):

  def __init__(self, principal):
    self.grants   = {}
    self.checkers = {}
    self.request  = {}
    self.principal    = principal
    self.view_args    = ()
    self.view_kwargs  = {}

  def grant(self, view_func, parameter_callbacks):
    self.grants[view_func] = parameter_callbacks

  def evaluate_expr(self, expr):
    """Recursively evaluate the callback expression """

    if isinstance(expr, list):
      if isinstance(expr, Operator):
        return expr.op(self.evaluate_expr(expr[0]), self.evaluate_expr(expr[1]))
      expr = expr[0]
    if expr is None:
      return True
    return expr(self.request, self.principal, self.view_args, self.view_kwargs)

  def evaluate(self, view_func):
    """Given a view_func this method returns 
          the value of the callbacks in self.grants

    """

    def access_rule(request, principal, view_args, view_kwargs):
      """Tranform and evaluate the access rule"""

      return self.evaluate_expr(PermissionSetAux().transform_expr(self.grants[view_func]))

    if not self.grants.has_key(view_func):
      return None
    return access_rule


class PermissionSetType:
  """Permission Sets Type

  """

  def account(self, account):
    from grants import account_grants
    return PermissionSetAux().get_permset(account, account_grants.get_grants(account))

  def accesstoken(self, access_token):
    from grants import accesstoken_grants
    return PermissionSetAux().get_permset(access_token, accesstoken_grants.get_grants(access_token))

  def machineapp(self, machine_app):
    from grants import machineapp_grants
    permset = PermissionSetAux().get_permset(machine_app, machineapp_grants.get_grants(machine_app))

    # FIXME: this should be reorganized rather than special-cased here
    if machine_app.app_type == 'chrome':
      permset = PermissionSetAux().add_grants(permset, 
                  { views.session_create : None, views.account_initialize : None })
    return permset

  def userapp(self, user_app):
    from grants import userapp_grants
    return PermissionSetAux().get_permset(user_app, userapp_grants.get_grants(user_app))

  def nouser(self):
    return PermissionSetAux().get_permset(None, {views.get_version : None})

  def principal(self, principal):
    return PermissionSetAux().get_permset(principal)

  def requesttoken(self, request_token):
    return PermissionSetAux().get_permset(request_token, {views.exchange_token : None}, False)


class PermissionSetAux:

  def _grant_baseline(self, permset):
    """Grant a common set of base grants"""

    # list the phas
    permset.grant(views.all_phas, None)

    # static files
    # for development purposes
    import django.views.static
    permset.grant(django.views.static.serve, None)
    return permset

  def get_permset(self, type_obj, grants=None, grant_baseline=True):
    """Get grants for a paricular principle"""

    permset = PermissionSet(type_obj)
    if grant_baseline:
      permset = self._grant_baseline(permset)
    return self.add_grants(permset, grants)

  def add_grants(self, permset, grants):
    """Add specific grants to the permset"""

    isiterable = lambda obj: isinstance(obj, basestring) or \
                              getattr(obj, '__iter__', False)

    if grants:
      for view, access_rule in grants.items():

        # access rules should always be of type list
        if not isinstance(access_rule, list):
          access_rule = [access_rule]

        if isiterable(access_rule):
          permset.grant(view, access_rule)
        else:
          return False
    return permset

  def transform_expr(self, expr):
    if not isinstance(expr, Operator):
      return expr
    expr[:] = map(self.transform_expr, expr)
    return expr


class Operator(list):
  """Generic Operator class"""

  def __init__(self, *args):
    super(Operator, self).__init__(args)

class Not(Operator):
  """Prop Cal Not"""

  def op(self, arg1):
    return not arg1

  def __str__(self):
    return '!(%s)' % tuple(self)

class And(Operator):
  """Prop Cal And"""

  def op(self, arg1, arg2):
    return arg1 and arg2

  def __str__(self):
    return '(%s & %s)' % tuple(self)

class Or(Operator):
  """Prop Cal Or"""

  def op(self, arg1, arg2):
    return arg1 or arg2

  def __str__(self):
    return '(%s | %s)' % tuple(self)
