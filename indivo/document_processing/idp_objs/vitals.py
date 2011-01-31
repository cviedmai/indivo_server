from indivo.lib import iso8601
from indivo.models import Vitals

XML = 'xml'
DOM = 'dom'

class IDP_Vitals:

  def post_data(self, date_measured=None,
                      name=None,
		      date_measured_end=None,
                      name_type=None,
                      name_value=None,
                      name_abbrev=None,
                      value=None,
                      unit=None,
                      unit_type=None,
                      unit_value=None,
                      unit_abbrev=None,
                      site=None,
                      position=None,
                      comments=None):

    """
    SZ: More error checking needs to be performed in this method
    """
    if date_measured: date_measured = iso8601.parse_utc_date(date_measured)
    if date_measured_end: date_measured_end = iso8601.parse_utc_date(date_measured_end)

    try:
      vitals_obj = Vitals.objects.create( date_measured=date_measured,
                                          name=name,
                                          date_measured_end=date_measured_end,
                                          name_type=name_type,
                                          name_value=name_value,
                                          name_abbrev=name_abbrev,
                                          value=value,
                                          unit=unit,
                                          unit_type=unit_type,
                                          unit_value=unit_value,
                                          unit_abbrev=unit_abbrev,
                                          site=site,
                                          position=position,
                                          comments=comments)

      return vitals_obj
    except Exception, e:
      raise ValueError("problem processing vitals report " + str(e))
