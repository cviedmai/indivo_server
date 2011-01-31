
class UserAppRuleset:

  def __init__(self, userapp):
    self.userapp = userapp

  def userapp_documents(self, request, principal, view_args, view_kwargs):
    """ 
    allow only if all the following are fulfilled:
    - there is NO record specified, 
    - there IS a PHA specified, and
    - the pha specified matches this userapp
    """

    PHA_EMAIL = 'pha_email'
    RECORD_ID = 'record_id'

    # record ID specified? Then it's not okay for a non-token-authorized app
    if view_kwargs.has_key(RECORD_ID) and view_kwargs[RECORD_ID] != None:
      return False
    if view_kwargs.has_key(PHA_EMAIL):
      return view_kwargs[PHA_EMAIL] == principal.email
    else:
      return False
