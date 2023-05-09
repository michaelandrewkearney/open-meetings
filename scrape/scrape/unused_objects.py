import pytz
from enum import StrEnum
import re
import datetime as dt

# Analysis Classes parse data as strings from the OMP. This data is then manually examined for cleanliness to ensure that all information is captured and processed appropriate in non-Analysis Classes.

class URL:
    def __init__(self,
                 protocol: str | None = None,
                 domain: list[str] = list(),
                 port: int | None = None,
                 endpoint_path: list[str] = list(),
                 queries: dict[str, str] = dict(),
                 parse: str | None = None):
        if parse:
            assert not protocol
            assert not domain
            assert not port
            assert not endpoint_path
            assert not queries
            # TODO test regex
            matches = re.search(
                "([^/:]*)"+ # protocol
                "://"+ # separator
                "([^/:]*)"+ # domain
                "(:\\d{4})?"+ # optional port
                "(?:"+ # start optional path
                "((?:/[^/]+)+)"+ # endpoint(s)
                "(?:\\?"+ # start optional params
                "((?:[^=&]+=[^=&]+&?)*)"+ # params
                ")?"+ # end optional params
                ")?" # end optional path
                , parse)
            if matches:
                self.protocol: str | None = matches.group(1)
                self.domain: list[str] = matches.group(2).split('.') if matches.group(2) else list()
                self.port: int | None = int(matches.group(3)) if matches.group(3) else None
                self.endpoint_path: list[str] = matches.group(4).split('/') if matches.group(4) else list()
                self.queries: dict[str, str] = dict()
                if matches.group(5):
                    for pair in matches.group(5).split('&'):
                        kv: list[str] = pair.split('=')
                        assert len(kv) == 2
                        self.queries[kv[0]] = kv[1]
            else:
                raise RuntimeError(f"Could not match url '{parse}'.")
        else:
            self.protocol: str | None = protocol
            self.domain: list[str] = domain
            self.port: int | None = port
            self.endpoint_path: list[str] = endpoint_path
            self.queries: dict[str, str] = queries

    def get_query_arg(self, param: str) -> str | None:
        return self.queries.get(param)

# DocumentType represents the type of a document
# add document types as needed, with the string value with the same casing as presented on the SOS Open Meetings Portal
class DocumentType(StrEnum):
    AGENDA = 'Agenda',
    AGENDA_PACKET = 'Agenda Packet'
    MINUTES = 'Minutes'

# Person represents a person associated with a public body of meeting
class Person:
    def __init__(self,
                 title: str | None = None,
                 name: str | None = None,
                 phone: int | None = None,
                 email: str | None = None):
        self.title: str | None = title
        self.name: str | None = name
        self.phone: int| None = phone
        self.email: str | None = email

# Document is a document available from the SOS
class Document:
    def __init__(self,
                 doctype: DocumentType,
                 name: str | None,
                 filepath: str,
                 post_dt: float,
                 poster: Person):
        self.doctype: DocumentType = doctype
        self.name: str | None = name
        self.filepath: str = filepath
        self.post_dt: float = post_dt
        self.poster: Person = poster

# Meeting represents a public meeting
class Meeting:
    def __init__(self,
                 body: int,
                 meeting_dt: float,
                 meeting_address: str,
                 filing_dt: float,
                 is_emergency: bool,
                 is_annual_calendar: bool,
                 is_public_notice: bool,
                 agendas: list[Document],
                 minutes: list[Document],
                 contact: Person,
                 is_meeting_dt_changed: bool,
                 is_address_changed: bool,
                 is_annual_calendar_changed: bool,
                 is_emergency_changed: bool,
                 is_public_notice_changed: bool,
                 is_agenda_changed: bool,
                 is_cancelled: bool,
                 cancelled_dt: float | None,
                 cancelled_reason: str | None):
        self.body: int = body
        self.meeting_dt: float = meeting_dt
        self.meeting_address: str = meeting_address
        self.filing_dt: float = filing_dt
        self.is_emergency: bool = is_emergency
        self.is_annual_calendar: bool = is_annual_calendar
        self.is_public_notice: bool = is_public_notice
        self.agendas: list[Document] = agendas
        self.minutes: list[Document] = minutes
        self.contact: Person = contact
        self.is_meeting_dt_changed: bool = is_meeting_dt_changed
        self.is_address_changed: bool = is_address_changed
        self.is_annual_calendar_changed: bool = is_annual_calendar_changed
        self.is_emergency_changed: bool = is_emergency_changed
        self.is_public_notice_changed: bool = is_public_notice_changed
        self.is_agenda_changed: bool = is_agenda_changed
        self.is_cancelled: bool = is_cancelled
        if self.is_cancelled:
            if cancelled_dt is None:
                raise TypeError("Meeting was cancelled but cancellation datetime is None.")
            if cancelled_reason is None:
                raise TypeError("Meeting was cancelled but cancellation reason is None.")
        else:
            if cancelled_dt is not None:
                raise TypeError(f"Meeting was not cancelled but cancellation datetime '{cancelled_dt}' was provided.")
            if cancelled_reason is not None:
                raise TypeError(f"Meeting was not cancelled but cancellation reason '{cancelled_reason}' was provided.")
        self.cancelled_dt: float | None = cancelled_dt
        self.cancelled_reason: str | None = cancelled_reason

class AnalysisMeeting:
    def __init__(self,
                 form_action: str | list[str],
                 body: str,
                 meeting_date: str,
                 meeting_time: str,
                 meeting_address: str,
                 filing_dt: str,
                 is_emergency: str,
                 is_annual_calendar: str,
                 is_public_notice: str,
                 agendas: dict[str, str],
                 minutes: dict[str, str],
                 contact_person: str,
                 phone: str,
                 email: str,
                 is_meeting_date_changed: str,
                 is_meeting_time_changed: str,
                 is_address_changed: str,
                 is_annual_calendar_changed: str,
                 is_emergency_changed: str,
                 is_public_notice_changed: str,
                 is_agenda_changed: str,
                 is_emergency_flag: str,
                 is_annual_flag: str,
                 is_public_notice_flag: str,
                 is_cancelled: str,
                 cancelled_dt: str,
                 cancelled_reason: str,
                 id: int = -1):
        self.form_action: str | list[str] = form_action
        self.body: str = body
        self.meeting_date: str = meeting_date
        self.meeting_time: str = meeting_time
        self.meeting_address: str = meeting_address
        self.filing_dt: str = filing_dt
        self.is_emergency: str = is_emergency
        self.is_annual_calendar: str = is_annual_calendar
        self.is_public_notice: str = is_public_notice
        self.agendas: dict[str, str] = agendas
        self.minutes: dict[str, str] = minutes
        self.contact_person: str = contact_person
        self.phone: str = phone
        self.email: str = email
        self.is_meeting_date_changed: str = is_meeting_date_changed
        self.is_meeting_time_changed: str = is_meeting_time_changed
        self.is_address_changed: str = is_address_changed
        self.is_annual_calendar_changed: str = is_annual_calendar_changed
        self.is_emergency_changed: str = is_emergency_changed
        self.is_public_notice_changed: str = is_public_notice_changed
        self.is_agenda_changed: str = is_agenda_changed
        self.is_emergency_flag: str = is_emergency_flag
        self.is_annual_flag: str = is_annual_flag
        self.is_public_notice_flag: str = is_public_notice_flag
        self.is_cancelled: str = is_cancelled
        self.cancelled_dt: str = cancelled_dt
        self.cancelled_reason: str = cancelled_reason
        self.id = id
    
    # TODO
    def to_meeting(self):
        pass

    def is_real_meeting(self) -> bool:
        if (self.is_emergency_flag == '' and
            self.is_annual_flag == '' and
            self.is_public_notice_flag == '' and
            self.body == '' and
            self.meeting_date == '' and
            self.meeting_time == '' and
            self.meeting_address == '' and
            self.filing_dt == '' and
            self.is_emergency == '' and
            self.is_annual_calendar == '' and
            self.is_public_notice == '' and
            len(self.agendas) == 0 and
            len(self.minutes) == 0 and
            self.contact_person == '' and
            self.phone == '' and
            self.email == ''):
            return False
        return True