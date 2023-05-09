import re
import ast
from typing import Callable
import pytz
import datetime as dt
from pymongo.database import Database
from resource_type import DocType
from download import download_document
from parse import RawMeeting, RawBody, parse_document
from io_utils import get_body_id_from_name
from threading import Lock

class Document:
    def __init__(self,
                 stamp: float,
                 name: str | None,
                 doctype: DocType,
                 dt: float,
                 filer: str | None,
                 path: str | None,
                 snippets: list[str]):
        self.stamp: float = stamp
        self.name: str | None = name
        self.doctype: DocType = doctype
        self.dt: float = dt
        self.filer: str | None = filer
        self.path: str | None = path
        self.snippets: list[str] = snippets

class Meeting:
    def __init__(self,
                 stamp: float,
                 body: int,
                 meeting_dt: float,
                 meeting_address: str,
                 filing_dt: float,
                 agendas: list[Document],
                 minutes: list[Document],
                 contact_name: str,
                 contact_phone: str,
                 contact_email: str,
                 is_meeting_dt_changed: bool,
                 is_address_changed: bool,
                 is_annual_calendar_changed: bool,
                 is_emergency_changed: bool,
                 is_public_notice_changed: bool,
                 is_agenda_changed: bool,
                 is_emergency: bool,
                 is_annual_calendar: bool,
                 is_public_notice: bool,
                 is_cancelled: bool,
                 cancelled_dt: float | None,
                 cancelled_reason: str | None):
        self.stamp: float = stamp
        self.body: int = body
        self.meeting_dt: float = meeting_dt
        self.meeting_address: str = meeting_address
        self.filing_dt: float = filing_dt
        self.agendas: list[Document] = agendas
        self.minutes: list[Document] = minutes
        self.contact_name: str = contact_name
        self.contact_phone: str = contact_phone
        self.contact_email: str = contact_email
        self.is_meeting_dt_changed: bool = is_meeting_dt_changed
        self.is_address_changed: bool = is_address_changed
        self.is_annual_calendar_changed: bool = is_annual_calendar_changed
        self.is_emergency_changed: bool = is_emergency_changed
        self.is_public_notice_changed: bool = is_public_notice_changed
        self.is_agenda_changed: bool = is_agenda_changed
        self.is_emergency: bool = is_emergency
        self.is_annual_calendar: bool = is_annual_calendar
        self.is_public_notice: bool = is_public_notice
        self.is_cancelled: bool = is_cancelled
        self.cancelled_dt: float | None = cancelled_dt
        self.cancelled_reason: str | None = cancelled_reason

class Body:
    def __init__(self,
                 stamp: float,
                 name: str,
                contact_name: str,
                contact_phone: str,
                contact_email: str,
                subcommittees: list[int],
                contact_information: dict[str, str],
                facebook: str | None,
                twitter: str | None,
                instagram: str | None,
                linkedin: str | None,
                budget: str | None,
                personnel: str | None,
                description: str | None,
                responsibilities: str | None,
                people: dict[str, list[tuple[str, str, str, str]]],
                max_members: str | None,
                authority: tuple[str, str] | None,
                board_members: list[tuple[str, str, str, str, str]]):
        self.stamp: float = stamp
        self.name: str = name
        self.contact_name: str = contact_name
        self.contact_phone: str = contact_phone
        self.contact_email: str = contact_email
        self.subcommittees: list[int] = subcommittees
        self.contact_information: dict[str, str] = contact_information
        self.facebook: str | None = facebook
        self.twitter: str | None = twitter
        self.instagram: str | None = instagram
        self.linkedin: str | None = linkedin
        self.budget: str | None = budget
        self.personnel: str | None = personnel
        self.description: str | None = description
        self.responsibilities: str | None = responsibilities
        self.people: dict[str, list[tuple[str, str, str, str]]] = people
        self.max_members: str | None = max_members
        self.authority: tuple[str, str] | None = authority
        self.board_members: list[tuple[str, str, str, str, str]] = board_members

# analysis.py contains regex patterns that match fields to be scraped from meeting and body pages. These patterns were developed from analysis of all data on the SOS OMP up to May 1, 2023. These patterns can be used to validate new data scraped from the SOS OMP and to detect changes in the format of data presented on the OMP.

#TODO test groups for cancelled datetimes

# groups: meeting_id
FORM_ACTION_PATTERN = '/OpenMeetingsPublic/ViewMeetingDetailByID\?MeetingID=(\d{6,7})'

# groups: mon, day, year
SIMPLE_DATE_PATTERN = '(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (?: ?(\d\d?)) (\d{4})'

# groups: mon, day, year, cancelled_mon, cancelled_day, cancelled_year
DATE_PATTERN = f'{SIMPLE_DATE_PATTERN}(?:\s*\({SIMPLE_DATE_PATTERN}\))?'

# groups: hours, minutes, meridiem
SIMPLE_TIME_PATTERN = '(\d{1,2})\:(\d{2}) ?((?:A|P)M)'

# groups: hours, minutes, meridiem, cancelled_hours, cancelled_minutes, cancelled_meridiem
TIME_PATTERN = f'{SIMPLE_TIME_PATTERN}(?:\s*\({SIMPLE_TIME_PATTERN}\))?'

# groups: mon, day, year, hours, minutes, meridiem
DT_PATTERN = f'{SIMPLE_DATE_PATTERN}, {SIMPLE_TIME_PATTERN}'

# groups: value
YES_NO_PATTERN = '(Yes|No)'

# groups: value
INT_FLAG_PATTERN = '(0|1)'

# groups: extension
EXTENSION_PATTERN = ',?\s?(?:(?:\(x?(\d)+\))|(?:VP)|(?:(?:ext|EXT|Ext|X|x| )[\,\.]?\s?(\d*)))'

# groups: area_code, prefix, line_number, extension
PHONE_PATTERN = '(?:(?:\d[-\.]?\s?)?\(?(\d{3})\)?[-\.]?\s?)?(\d{3})[-\.]?\s?(\d{4})' + f'(?:{EXTENSION_PATTERN})?'
# groups: email
EMAIL_PATTERN = '(\S*@\S*)'

# groups: docname, doctype, filing_dt, poster
DOC_TEXT_PATTERN = f'(?:(.*), )?(Agenda|Minutes) filed on ({DT_PATTERN})(?: by (.+))?'

# groups: filepath
DOC_ONCLICK_PATTERN = "DownloadMeetingFiles\('(.*)'\)"

# groups: entity
BODY_URL_PATTERN = '^.+EntityID=(\d+)(\D+.*)?$'

# datetimes are converted from local format to posix epoch time for storage.
# Note the space-padding in single-digit days
# SOS datetime format: "Jun  2 2021, 01:02PM", "May 28 2004, 11:59AM"
SOS_DT_FORMAT: str = '%b %d %Y, %I:%M%p'
# Days in SOS datetimes are unpadded. This formatting string accepts padded and unpadded values, but using it to generate str will pad values. Use this pattern matching to unpad the day field after str conversion:
# re.sub("^(\\S{3}\\s)(0?)", "\\1", str_dt)
RI_TZ = pytz.timezone("US/Eastern")

def local_dt_to_posix(datetime: dt.datetime) -> float:
    return RI_TZ.localize(datetime).timestamp()

# parses SOS datetime to posix time
# param: str_datetime in the form "Jun 2 2021, 01:02PM"
def parse_sos_dt_to_timestamp(str_datetime: str) -> float:
    return local_dt_to_posix(dt.datetime.strptime(str_datetime, SOS_DT_FORMAT))

# creates SOS datetime-formatted string from posix time
# param: ts the posix time to convert
def timestamp_to_sos_dt(ts: float) -> str:
    str_dt: str = dt.datetime.fromtimestamp(ts, RI_TZ).strftime(SOS_DT_FORMAT)
    # strftime pads day, but SOS DT format includes unpadded day
    return re.sub("^(\\S{3}\\s)(0?)", "\\1", str_dt)

def add_line_markers_to_pattern(pattern: str) -> str:
    return f'^{pattern}$'

def build_is_normal(pattern: str) -> Callable[[str], bool]:
    def is_normal(string: str) -> bool:
        return re.fullmatch(pattern, string) is not None
    return is_normal

def id_matches_form_action(id: int, form_action:str) -> bool:
    match = re.fullmatch(FORM_ACTION_PATTERN, form_action)
    if match is None:
        return False
    return id == int(match.group(1))

def is_document_normal(string: str) -> bool:
    docs: dict[str, str]= ast.literal_eval(string)
    for text, onclick in docs.items():
        onclick_match = re.fullmatch(DOC_ONCLICK_PATTERN, onclick)
        if onclick_match is None:
            return False
        if text == '' and onclick_match.group(1) == '':
            continue
        if re.fullmatch(DOC_TEXT_PATTERN, text) is None:
            return False
    return True

# groups: mon, day, year, cancelled_mon, cancelled_day, cancelled_year
# groups: hours, minutes, meridiem, cancelled_hours, cancelled_minutes, cancelled_meridiem
def validate_meeting_datetime(date: str, time: str) -> float:
    match = re.fullmatch(DATE_PATTERN, date)
    if match is None:
        return 0.0
    dates = match.groups()[0:3]
    match = re.fullmatch(TIME_PATTERN, time)
    if match is None:
        return 0.0
    times = match.groups()[0:3]
    dtstr = " ".join(dates + times)
    return local_dt_to_posix(dt.datetime.strptime(dtstr, '%b %d %Y %I %M %p'))

def clean_filepath(path: str) -> str:
    return re.sub('\\\\+', '/', path)

def parse_doctype(doctype: str) -> DocType:
    match (doctype.lower()):
        case 'agenda':
            return DocType.AGENDA
        case 'minutes':
            return DocType.MINUTES
    return DocType.UNKNOWN

def validate_meeting(db: Database, db_lock: Lock, raw: RawMeeting) -> Meeting | None:
    if raw.body == '':
        return None
    body: int = get_body_id_from_name(db, db_lock, raw.body)
    meeting_dt: float = validate_meeting_datetime(raw.meeting_date, raw.meeting_time)
    filing_dt: float = parse_sos_dt_to_timestamp(raw.filing_dt)
    agendas: list[Document] = list()
    minutes: list[Document] = list()
    for begin, end in [(raw.agendas, agendas), (raw.minutes, minutes)]:
        for text, onclick in begin:
            text_match = re.fullmatch(DOC_TEXT_PATTERN, text)
            onclick_match = re.fullmatch(DOC_ONCLICK_PATTERN, onclick)
            name: str | None = text_match.group(1) if text_match else None
            doctype: DocType = parse_doctype(text_match.group(2)) if text_match else DocType.UNKNOWN
            filing_dt: float = parse_sos_dt_to_timestamp(text_match.group(3)) if text_match else 0.0
            filer: str | None = text_match.group(10) if text_match else None
            if onclick_match and onclick_match.group(1):
                path: str = clean_filepath(onclick_match.group(1))
                rawdoc = parse_document(download_document(path))
                end.append(Document(rawdoc.stamp, name, doctype, filing_dt, filer, path, rawdoc.snippets))
    is_meeting_dt_changed: bool = raw.is_meeting_date_changed != '0' or raw.is_meeting_time_changed != '0'
    is_address_changed: bool = raw.is_address_changed != '0'
    is_annual_calendar_changed: bool = raw.is_annual_calendar_changed != '0'
    is_emergency_changed: bool = raw.is_emergency_changed != '0'
    is_public_notice_changed: bool = raw.is_public_notice_changed != '0'
    is_agenda_changed: bool = raw.is_agenda_changed != '0'
    is_emergency: bool = raw.is_emergency != '0'
    is_annual_calendar: bool = raw.is_annual_calendar != '0'
    is_public_notice: bool = raw.is_public_notice != '0'
    is_cancelled: bool = raw.is_cancelled != '0'
    cancelled_dt: float | None = parse_sos_dt_to_timestamp(raw.cancelled_dt) if raw.cancelled_dt else None
 
    return Meeting(stamp=raw.stamp,
                   body=body,
                   meeting_dt=meeting_dt,
                   meeting_address=raw.meeting_address,
                   filing_dt=filing_dt,
                   agendas=agendas,
                   minutes=minutes,
                   contact_name=raw.contact_name,
                   contact_phone=raw.contact_phone,
                   contact_email=raw.contact_email,
                   is_meeting_dt_changed=is_meeting_dt_changed,
                   is_address_changed=is_address_changed,
                   is_annual_calendar_changed=is_annual_calendar_changed,
                   is_emergency_changed=is_emergency_changed,
                   is_public_notice_changed=is_public_notice_changed,
                   is_agenda_changed=is_agenda_changed,
                   is_emergency=is_emergency,
                   is_annual_calendar=is_annual_calendar,
                   is_public_notice=is_public_notice,
                   is_cancelled=is_cancelled,
                   cancelled_dt=cancelled_dt,
                   cancelled_reason=raw.cancelled_reason)

def validate_body(raw: RawBody) -> Body | None:
    if raw.name == '':
        return None
    subcommittees: list[int] = []
    for name, link in raw.subcommittees:
        m = re.match(BODY_URL_PATTERN, link)
        if m and m.group(0):
            subcommittees.append(int(m.group(0)))
    contact_information: dict[str, str] = dict()
    for field, value in raw.contact_information.items():
        contact_information[field.replace(':', '').strip()] = value
    return Body(stamp = raw.stamp,
                name = raw.name,
                contact_name = raw.contact_name,
                contact_phone = raw.contact_phone,
                contact_email = raw.contact_email,
                subcommittees = subcommittees,
                contact_information = contact_information,
                facebook = raw.facebook if raw.facebook else None,
                twitter = raw.twitter if raw.twitter else None,
                instagram = raw.instagram if raw.instagram else None,
                linkedin = raw.linkedin if raw.linkedin else None,
                budget = raw.budget if raw.budget else None,
                personnel = raw.personnel if raw.personnel else None,
                description = raw.description if raw.description else None,
                responsibilities = raw.responsibilities if raw.responsibilities else None,
                people = raw.people,
                max_members = raw.max_members if raw.max_members else None,
                authority = raw.authority if raw.authority else None,
                board_members = raw.board_members)