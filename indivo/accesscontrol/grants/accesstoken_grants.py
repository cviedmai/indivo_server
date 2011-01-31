from indivo.views import *
from indivo.accesscontrol import And, Or
from indivo.accesscontrol.rulesets.accesstoken_ruleset import AccessTokenRuleset
  
def get_grants(access_token):

  accesstoken_ruleset = AccessTokenRuleset(access_token)
  
  # Access rules
  ar_share_record_or_pha  = Or(
    # user behind token has proper record-or-carenet access, and share's carenet restrictions are respected
    And(
      # record-level or carenet-level access
      Or(
        accesstoken_ruleset.share_record_rule, 
        accesstoken_ruleset.token_carenet_rule),
      # either no carenet in the share, or carenet_id must match the share's constraint
      Or(accesstoken_ruleset.share_carenet_rule, 
         accesstoken_ruleset.share_no_carenet_rule)), 
    # this activates only if pha_email is in the kwargs
    accesstoken_ruleset.share_pha_rule)

  ar_carenet_document = And( 
                          Or( accesstoken_ruleset.token_record_rule, 
                              accesstoken_ruleset.carenet_account_rule), 
                          accesstoken_ruleset.carenet_document_rule) 
  ar_carenet_account  = Or(accesstoken_ruleset.token_record_rule, accesstoken_ruleset.carenet_account_rule)
  
  
  grants = {
    allergy_list                  : ar_share_record_or_pha,
    account_forgot_password       : ar_share_record_or_pha,
    audit_document_view           : ar_share_record_or_pha,
    audit_function_view           : ar_share_record_or_pha,
    audit_record_view             : ar_share_record_or_pha,
  
    carenet_account_permissions   : ar_share_record_or_pha,
    carenet_document_list         : ar_share_record_or_pha,
    carenet_document              : ar_share_record_or_pha,
    carenet_record                : ar_share_record_or_pha,

    # this is allowed for all tokens, but it may fail later
    get_long_lived_token          : None,
  
    document                      : ar_share_record_or_pha,
    document_create               : ar_share_record_or_pha,
    document_create_by_rel        : ar_share_record_or_pha,
    document_create_or_update     : ar_share_record_or_pha,
    document_delete               : ar_share_record_or_pha,
    document_label                : ar_share_record_or_pha,
    document_meta                 : ar_share_record_or_pha,
    document_rels                 : ar_share_record_or_pha,
    document_set_status           : ar_share_record_or_pha,
    document_status_history       : ar_share_record_or_pha,
    document_version              : ar_share_record_or_pha,
    document_versions             : ar_share_record_or_pha,
    document_list                 : ar_share_record_or_pha,
    equipment_list                : ar_share_record_or_pha,
    get_documents_by_rel          : ar_share_record_or_pha,
    immunization_list             : ar_share_record_or_pha,
    lab_list                      : ar_share_record_or_pha,
    measurement_list              : ar_share_record_or_pha,
    medication_list               : ar_share_record_or_pha,
    problem_list                  : ar_share_record_or_pha,
    procedure_list                : ar_share_record_or_pha,
    read_special_document         : ar_share_record_or_pha,
    record                        : ar_share_record_or_pha,
    record_shares                 : ar_share_record_or_pha,
    record_share_add              : ar_share_record_or_pha,
    record_share_delete           : ar_share_record_or_pha,
    record_inbox                  : ar_carenet_account,
    record_notify                 : ar_share_record_or_pha,
    simple_clinical_notes_list    : ar_share_record_or_pha,
    vitals_list                   : ar_share_record_or_pha,

    # messaging
    record_send_message           : ar_share_record_or_pha,
    record_message_attach         : ar_share_record_or_pha,
  }

  return grants
