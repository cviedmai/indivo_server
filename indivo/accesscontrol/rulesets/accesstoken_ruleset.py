from indivo import models

class AccessTokenRuleset:

  def __init__(self, access_token):
    self.access_token = access_token

  def _get(self, obj_model, view_kwargs):
    try:
      ID = str(obj_model()).lower().strip() + '_id'
      if view_kwargs.has_key(ID):
        return obj_model.objects.get(id = view_kwargs[ID])
      return False
    except obj_model.DoesNotExist:
      return False

  def share_record_rule(self, request, principal, view_args, view_kwargs):
    """check proper record for the share that a token corresponds to,
    and ensure the token isn't carenet restricted"""
    RECORD_ID   = 'record_id'
    if view_kwargs.has_key(RECORD_ID):
      return (view_kwargs[RECORD_ID] == self.access_token.share.record.id
              and
              self.access_token.carenet == None)

  def token_carenet_rule(self, request, principal, view_args, view_kwargs):
    """
    assuming this is a carenet related call, ensure the carenet constraint
    on the token itself is appropriate: null or matching.
    """
    CARENET_ID = 'carenet_id'
    if view_kwargs.has_key(CARENET_ID):
      return (self.access_token.carenet == None
              or
              view_kwargs[CARENET_ID] == self.access_token.carenet.id)

  def share_no_carenet_rule(self, request, principal, view_args, view_kwargs):
    """Returns True if there is no carenet associated with the share"""
    return self.access_token.share.carenet == None

  def share_carenet_rule(self, request, principal, view_args, view_kwargs):
    """Returns True if there is a carenet associated with the share"""
    CARENET_ID  = 'carenet_id'
    if view_kwargs.has_key(CARENET_ID):
      return (self.access_token.share.carenet == None or
              view_kwargs[CARENET_ID] == self.access_token.share.carenet.id)

  def share_pha_rule(self, request, principal, view_args, view_kwargs):
    """
    identifies app-specific calls, which do NOT have a record or a document specified.
    the view has to be tagged as __app_specific for this to fire
    """

    PHA_EMAIL   = 'pha_email'
    APP_SPECIFIC = "__app_specific"
    if view_kwargs.has_key(PHA_EMAIL) and view_kwargs.has_key(APP_SPECIFIC) and view_kwargs[APP_SPECIFIC]:
      return view_kwargs[PHA_EMAIL] == self.access_token.share.with_pha.email

  def carenet_account_rule(self, request, principal, view_args, view_kwargs):
    record = self._get(models.Record, view_kwargs)
    if record and models.CarenetAccount.objects.select_related().filter(
                                                    account = principal, 
                                                    carenet__record = record):
      return True
    return False

  def carenet_document_rule(self, request, principal, view_args, view_kwargs):
    record    = self._get(models.Record, view_kwargs)
    document  = self._get(models.Document, view_kwargs)
    if record and document and models.CarenetDocument.objects.select_related().filter(
                                                                      document = document, 
                                                                      carenet__record = record):
      return True
    return False
  
  def token_record_rule(self, request, principal, view_args, view_kwargs):
    "FIXME: should this be comparing owners, or the records themselves??"
    record = self._get(models.Record, view_kwargs)
    if record and record == self.access_token.share.record:
      return True
    return False
