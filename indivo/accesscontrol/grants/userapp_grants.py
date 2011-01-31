from indivo.views import *
from indivo.accesscontrol import And, Or
from indivo.accesscontrol.rulesets.userapp_ruleset import UserAppRuleset

def get_grants(userapp):

  userapp_ruleset = UserAppRuleset(userapp)

  grants = {
    document                      : userapp_ruleset.userapp_documents,
    document_create               : userapp_ruleset.userapp_documents,
    document_create_or_update     : userapp_ruleset.userapp_documents,
    document_delete               : userapp_ruleset.userapp_documents,
    document_meta                 : userapp_ruleset.userapp_documents,
    document_list                 : userapp_ruleset.userapp_documents,
    request_token                 : None
  }

  return grants
