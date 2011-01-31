from indivo import models

class AccountRuleset:
  """
  the grants for a given account
  """

  def __init__(self, account):
    self.account = account

  #########################
  # Accounts              #
  #########################

  def _get(self, obj_model, view_kwargs):
    try:
      ID = str(obj_model()).lower().strip() + '_id'
      if view_kwargs.has_key(ID):
        return obj_model.objects.get(id = view_kwargs[ID])
      return False
    except obj_model.DoesNotExist:
      return False

  def account_rule(self, request, principal, view_args, view_kwargs):
    """The given account is equivalent to the stated account id"""
    return view_kwargs['account_email'] == self.account.email

  def is_completely_shared(self, request, principal, view_args, view_kwargs):
    record  = self._get(models.Record, view_kwargs)
    if record and models.Share.objects.filter(record = record, with_account = self.account):
      return True

    # if we're only looking at the carenet, we need this query instead
    carenet = self._get(models.Carenet, view_kwargs)
    if carenet and models.Share.objects.filter(record = carenet.record, with_account = self.account):
      return True

    return False

  def is_owner(self, request, principal, view_args, view_kwargs):
    """The given account owns the record"""

    # Given a record, is the owner of that record
    record  = self._get(models.Record, view_kwargs)
    if record and record.owner == self.account:
      return True

    # Given a carenet, is the owner of the record in the carenet
    carenet = self._get(models.Carenet, view_kwargs)
    if carenet and carenet.record.owner == self.account:
      return True

    # Otherwise, return False
    return False

  def account_in_carenet(self, request, principal, view_args, view_kwargs):
    """The account is in the carenet being requested"""

    carenet = self._get(models.Carenet, view_kwargs)
    if carenet and models.CarenetAccount.objects.filter(
                    carenet = carenet, account = principal):
      return True
    return False

  def document_in_carenet(self, request, principal, view_args, view_kwargs):
    """The given document and record are in the same carenet"""

    carenet   = self._get(models.Carenet,  view_kwargs)
    document  = self._get(models.Document, view_kwargs)
    if carenet and document and models.CarenetDocument.objects.filter(
                                  carenet__record = carenet.record, document = document):
      return True
    return False

  def doctype_in_autoshare(self, request, principal, view_args, view_kwargs):
    """The given document type is within an autoshare"""

    carenet   = self._get(models.Carenet, view_kwargs)
    document  = self._get(models.Document, view_kwargs)
    if document.type and \
      models.CarenetAutoshare.objects.select_related().filter(
        type            = document.type,
        carenet__record = carenet.record):
      return True
    return False


  #########################
  # Request Tokens        #
  #########################

  def _get_reqtoken(self, view_kwargs):
    try:
      rt = models.ReqToken.objects.get( token = view_kwargs['request_token'], authorized_by = self.account)
    except models.ReqToken.DoesNotExist:
      return False
    return rt

  def reqtoken_exists(self, request, principal, view_args, view_kwargs):
    """The request token exists"""
    return self._get_reqtoken(view_kwargs)

  def reqtoken_record(self, request, principal, view_args, view_kwargs):
    """The given account can administer the requested record"""
    record_id = request.POST.get('record_id', None)
    if self._get_reqtoken(view_kwargs) and record_id:
      return models.Record.objects.get(id = record_id).can_admin(self.account)
    return False

  def reqtoken_carenet(self, request, principal, view_args, view_kwargs):
    """the given account is in the given carenet, and the PHA is in the carenet, too"""
    carenet_id = request.POST.get('carenet_id', None)
    rt = self._get_reqtoken(view_kwargs)
    if rt and carenet_id:
      return models.CarenetAccount.objects.filter(carenet__id = carenet_id, account = principal) and \
          models.CarenetPHA.objects.filter(carenet__id = carenet_id, pha = rt.pha)
    return False
