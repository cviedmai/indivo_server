from indivo.views import *
from indivo.accesscontrol.rulesets.machineapp_ruleset import MachineAppRuleset
  
def get_grants(machineapp):
  machapp_ruleset = MachineAppRuleset(machineapp)
  grants = {
    get_version             : None,
    account_authsystem_add  : None,
    account_create          : None,
    account_info            : None,
    account_info_set        : None,
    account_username_set    : None,
    account_forgot_password : None,
    account_check_secrets   : None,
    account_password_set    : None,
    account_primary_secret  : None,
    account_resend_secret   : None,
    account_reset           : None,
    account_set_state       : None,
    account_search          : None,
    account_send_message    : None,
    account_secret          : None,
    autoshare_create        : None,
    carenet_create          : None,
    carenet_list            : None,
    document_create         : machapp_ruleset.no_external_id,
    document_version        : None,
    document_list           : machapp_ruleset.appspecific_rule,
    pha_delete              : machapp_ruleset.appspecific_rule,
    pha_record_delete       : None,

    read_special_document   : machapp_ruleset.machineapp_record_created_rule,
    save_special_document   : machapp_ruleset.machineapp_record_created_rule,

    record_shares           : None,
    record_share_add        : None,
    record_share_delete     : None,
    record_create           : machapp_ruleset.principal_email_matches_principal,
    record_get_owner        : None,  
    record_notify           : None,
    record_pha_setup        : None,
    # FIXME: are we sure that all of these are None?
    record_send_message     : None,
    record_message_attach   : None,
    record_set_owner        : None,
    update_document_meta    : None
  }
  return grants
