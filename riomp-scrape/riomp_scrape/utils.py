import pytz
import datetime as dt
import re
import requests

def get_meeting_details_page(id: int) -> str:
    url: str = 'https://opengov.sos.ri.gov/OpenMeetingsPublic/ViewMeetingDetailByID?MeetingID='+ str(id)
    r = requests.get(url)
    if r.status_code != 200:
        print(f'Request for meeting {id} details returned with status code {r.status_code}.')
    return r.text


# datetimes are converted from local format to posix epoch time for storage.
# Note the space-padding in single-digit days
# SOS datetime format: Jun  2 2021, 01:02PM, May 28 2004, 11:59AM
SOS_DT_FORMAT: str = '%b %d %Y, %I:%M%p'
# Days in SOS datetimes are unpadded. This formatting string accepts padded and unpadded values, but using it to generate str will pad values. Use this pattern matching to unpad the day field after str conversion:
# re.sub("^(\\S{3}\\s)(0?)", "\\1", str_dt)
RI_TZ = pytz.timezone("US/Eastern")

# parses SOS datetime to posix time
# param: str_datetime in the form "Jun 2 2021, 01:02PM"
def parse_sos_dt_to_timestamp(str_datetime: str) -> float:
    return RI_TZ.localize(dt.datetime.strptime(str_datetime, SOS_DT_FORMAT)).timestamp()

# creates SOS datetime-formatted string from posix time
# param: ts the posix time to convert
def timestamp_to_sos_dt(ts: float) -> str:
    str_dt: str = dt.datetime.fromtimestamp(ts, RI_TZ).strftime(SOS_DT_FORMAT)
    # strftime pads day, but SOS DT format includes unpadded day
    return re.sub("^(\\S{3}\\s)(0?)", "\\1", str_dt)

# formats phone number into int for database storage. adds 401 area code if none is present.
def strip_ri_phone(str_phone: str) -> int:
    strip_phone = re.sub("[^\\d]", "", str_phone)
    if len(strip_phone) == 7:
        strip_phone = '401' + strip_phone
    if len(strip_phone) == 0:
        return 0
    return int(strip_phone)