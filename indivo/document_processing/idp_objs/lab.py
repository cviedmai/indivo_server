from indivo.lib import iso8601
from indivo.models import Lab

XML = 'xml'
DOM = 'dom'

class IDP_Lab:

  def post_data(self,  date_measured,
                lab_type=None, 
                lab_name=None, 
                lab_address=None, 
                lab_comments=None,
                first_panel_name=None,
                first_lab_test_name=None,
                first_lab_test_value=None):
    """
    SZ: More error checking needs to be performed in this method
    """

    if date_measured:
      date_measured = iso8601.parse_utc_date(date_measured)

    try:
      lab_obj = Lab.objects.create( date_measured=date_measured, 
                                    lab_type=lab_type, 
                                    lab_name=lab_name, 
                                    lab_address=lab_address, 
                                    lab_comments=lab_comments,
                                    first_panel_name = first_panel_name,
                                    first_lab_test_name = first_lab_test_name,
                                    first_lab_test_value = first_lab_test_value)

      return lab_obj
    except Exception, e:
      raise ValueError("problem processing lab report " + str(e))
