from indivo import models



class MachineAppRuleset:
  """
  the grants for an admin app
  """

  def __init__(self, machine_app):
    self.machine_app = machine_app

  def principal_email_matches_principal(self, request, principal, view_args, view_kwargs):
    """
    If there is a principal email in the URL, it should match the current principal
    """
    PRINCIPAL_EMAIL = 'principal_email'

    # if no principal email, then this check is not necessary
    if not view_kwargs.has_key(PRINCIPAL_EMAIL):
      return True
    
    return view_kwargs[PRINCIPAL_EMAIL] == principal.email
    
  def machineapp_record_created_rule(self, request, principal, view_args, view_kwargs):
    try:
      RECORD_ID = 'record_id'
      if view_kwargs.has_key(RECORD_ID):
        return models.Record.objects.get(id = view_kwargs[RECORD_ID]).creator == self.machine_app.principal_ptr
    except:
      return False
    return False

  def machineapp_account_created_rule(self, request, principal, view_args, view_kwargs):
    account = models.Account.objects.get(email = view_kwargs['account_email'])
    return account.creator == self.machine_app

  def no_external_id(self, request, principal, view_args, view_kwargs):
    """
    mostly for document_create, to disallow creation with an external ID, since that makes no sense
    for an admin app to create a document with external ID where the app_id has to be a PHA, not an admin app.
    """
    if view_kwargs.has_key('external_id') and view_kwargs['external_id'] != None:
      return False
    
    return True

  def appspecific_rule(self, request, principal, view_args, view_kwargs):
    RECORD_ID = 'record_id'
    PHA_EMAIL = 'pha_email'

    if view_kwargs.has_key(RECORD_ID) or \
        not view_kwargs.has_key(PHA_EMAIL):
      return False
    return view_kwargs[PHA_EMAIL] == principal.email
