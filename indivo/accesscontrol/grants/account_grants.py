from indivo.views import *
from indivo.accesscontrol import And, Or
from indivo.accesscontrol.rulesets.account_ruleset import AccountRuleset
  
  
def get_grants(account):
  
  account_ruleset = AccountRuleset(account)
 
  full_control = Or(account_ruleset.is_owner, account_ruleset.is_completely_shared)
 
  # Access rules
  accessrule_carenet_document = Or( full_control, 
                                    account_ruleset.account_in_carenet)
  # I don't think we need to check the document permissions here, we just
  # let the filter in the carenet view return a 404. We don't actually want
  # to inform the user that they found a legit document_id (Ben)
  # FIXED accordingly 2010-10-13

  accessrule_carenet_account  = Or( full_control, account_ruleset.account_in_carenet)

  
  grants = {
    all_phas                    : None,

    account_permissions         : account_ruleset.account_rule,
    account_password_change     : account_ruleset.account_rule,
    account_forgot_password     : account_ruleset.account_rule,

    account_notifications       : account_ruleset.account_rule,
    account_inbox               : account_ruleset.account_rule,
    account_inbox_message       : account_ruleset.account_rule,
    account_message_archive     : account_ruleset.account_rule,
    account_inbox_message_attachment_accept : account_ruleset.account_rule,
    account_info                : account_ruleset.account_rule,
    account_info_set            : account_ruleset.account_rule,
    account_username_set        : account_ruleset.account_rule,
    record_list                 : account_ruleset.account_rule,
  
    audit_document_view         : full_control,
    audit_function_view         : full_control,
    audit_record_view           : full_control,
  
    autoshare_list              : full_control,
    autoshare_list_bytype_all   : full_control,
    autoshare_create            : full_control,
    autoshare_delete            : full_control,
  
    carenet_account_list        : accessrule_carenet_account,
    carenet_account_create      : full_control,
    carenet_account_delete      : full_control,
    carenet_account_permissions : accessrule_carenet_account,
    carenet_app_permissions     : full_control,
    carenet_apps_create         : full_control,
    carenet_apps_delete         : full_control,
    carenet_apps_list           : accessrule_carenet_account,
    carenet_document            : accessrule_carenet_document,
    carenet_document_delete     : full_control,
    carenet_document_list       : accessrule_carenet_account,
    carenet_document_placement  : full_control,
    carenet_list                : full_control,
    document_set_nevershare     : full_control,
    document_remove_nevershare  : full_control,

    carenet_record              : accessrule_carenet_account,
  
    document                    : full_control,
    document_carenets           : full_control,
    document_create             : full_control,
    document_create_or_update   : full_control,
    document_create_by_rel      : full_control,
    document_delete             : full_control,
    document_label              : full_control,
    document_meta               : full_control,
    document_rels               : full_control,
    document_set_status         : full_control,
    document_status_history     : full_control,
    document_version            : full_control,
    document_versions           : full_control,
    document_list               : full_control,
  
    allergy_list                : accessrule_carenet_account,
    lab_list                    : accessrule_carenet_account,
    equipment_list              : accessrule_carenet_account,
    get_documents_by_rel        : full_control,
    immunization_list           : accessrule_carenet_account,
    measurement_list            : accessrule_carenet_account,
    medication_list             : accessrule_carenet_account,
    pha_record_delete           : full_control,
    problem_list                : accessrule_carenet_account,
    procedure_list              : accessrule_carenet_account,
    simple_clinical_notes_list  : accessrule_carenet_account,
    report_ccr                  : accessrule_carenet_account,

    read_special_document       : accessrule_carenet_account,
    save_special_document       : full_control,

    record                      : full_control,
    record_get_owner            : full_control,
    record_inbox                : full_control,
    record_pha                  : full_control,
    record_phas                 : full_control,

    # full shares are managed only by the owner for now
    record_shares               : account_ruleset.is_owner,
    record_share_add            : account_ruleset.is_owner,
    record_share_delete         : account_ruleset.is_owner,
    vitals_list                 : accessrule_carenet_account,
  
    request_token_approve       : Or(account_ruleset.reqtoken_record, account_ruleset.reqtoken_carenet),
    request_token_claim         : None,
    request_token_info          : account_ruleset.reqtoken_exists,

    surl_verify                 : None,
  }

  return grants
