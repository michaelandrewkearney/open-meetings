import re
import pytz
from bs4 import BeautifulSoup as bs
from bs4 import Tag
from requests import Response, put
import datetime as dt
from constants import TIKA_ENDPOINT
from io_utils import is_tika_server_healthy

RI_TZ = pytz.timezone("US/Eastern")

def local_dt_to_posix(datetime: dt.datetime) -> float:
    return RI_TZ.localize(datetime).timestamp()

class RawMeeting:
    def __init__(self,
                 stamp: float,
                 body: str,
                 meeting_date: str,
                 meeting_time: str,
                 meeting_address: str,
                 filing_dt: str,
                 agendas: list[tuple[str, str]],
                 minutes: list[tuple[str, str]],
                 contact_name: str,
                 contact_phone: str,
                 contact_email: str,
                 is_meeting_date_changed: str,
                 is_meeting_time_changed: str,
                 is_address_changed: str,
                 is_annual_calendar_changed: str,
                 is_emergency_changed: str,
                 is_public_notice_changed: str,
                 is_agenda_changed: str,
                 is_emergency: str,
                 is_annual_calendar: str,
                 is_public_notice: str,
                 is_cancelled: str,
                 cancelled_dt: str,
                 cancelled_reason: str):
        self.stamp: float = stamp
        self.body: str = body
        self.meeting_date: str = meeting_date
        self.meeting_time: str = meeting_time
        self.meeting_address: str = meeting_address
        self.filing_dt: str = filing_dt
        self.agendas: list[tuple[str, str]] = agendas
        self.minutes: list[tuple[str, str]] = minutes
        self.contact_name: str = contact_name
        self.contact_phone: str = contact_phone
        self.contact_email: str = contact_email
        self.is_meeting_date_changed: str = is_meeting_date_changed
        self.is_meeting_time_changed: str = is_meeting_time_changed
        self.is_address_changed: str = is_address_changed
        self.is_annual_calendar_changed: str = is_annual_calendar_changed
        self.is_emergency_changed: str = is_emergency_changed
        self.is_public_notice_changed: str = is_public_notice_changed
        self.is_agenda_changed: str = is_agenda_changed
        self.is_emergency: str = is_emergency
        self.is_annual_calendar: str = is_annual_calendar
        self.is_public_notice: str = is_public_notice
        self.is_cancelled: str = is_cancelled
        self.cancelled_dt: str = cancelled_dt
        self.cancelled_reason: str = cancelled_reason

class RawOMBody:
    def __init__(self,
                 name: str,
                 contact_name: str,
                 contact_phone: str,
                 contact_email: str,
                 subcommittees: list[tuple[str, str]]):
        self.name: str = name
        self.contact_name: str = contact_name
        self.contact_phone: str = contact_phone
        self.contact_email: str = contact_email
        self.subcommittees: list[tuple[str, str]] = subcommittees

class RawGDBody:
    def __init__(self,
                 contact_information: dict[str, str],
                 facebook: str,
                 twitter: str,
                 instagram: str,
                 linkedin: str,
                 budget: str,
                 personnel: str,
                 description: str,
                 responsibilities: str,
                 people: dict[str, list[tuple[str, str, str, str]]]):
        self.contact_information: dict[str, str] = contact_information
        self.facebook: str = facebook
        self.twitter: str = twitter
        self.instagram: str = instagram
        self.linkedin: str = linkedin
        self.budget: str = budget
        self.personnel: str = personnel
        self.description: str = description
        self.responsibilities: str = responsibilities
        self.people: dict[str, list[tuple[str, str, str, str]]] = people

class RawBMBody:
    def __init__(self,
                 max_members: str | None,
                 authority: tuple[str, str],
                 board_members: list[tuple[str, str, str, str, str]]):
        self.max_members: str | None = max_members
        self.authority: tuple[str, str] = authority
        self.board_members: list[tuple[str, str, str, str, str]] = board_members

class RawBody:
    def __init__(self,
                 stamp: float,
                 om: RawOMBody,
                 gd: RawGDBody,
                 bm: RawBMBody):
        self.stamp: float = stamp
        self.name: str = om.name
        self.contact_name: str = om.contact_name
        self.contact_phone: str = om.contact_phone
        self.contact_email: str = om.contact_email
        self.subcommittees: list[tuple[str, str]] = om.subcommittees
        self.contact_information: dict[str, str] = gd.contact_information
        self.facebook: str = gd.facebook
        self.twitter: str = gd.twitter
        self.instagram: str = gd.instagram
        self.linkedin: str = gd.linkedin
        self.budget: str = gd.budget
        self.personnel: str = gd.personnel
        self.description: str = gd.description
        self.responsibilities: str = gd.responsibilities
        self.people: dict[str, list[tuple[str, str, str, str]]] = gd.people
        self.max_members: str | None  = bm.max_members
        self.authority: tuple[str, str]  = bm.authority
        self.board_members: list[tuple[str, str, str, str, str]] = bm.board_members

class RawDocument:
    def __init__(self,
                 stamp: float,
                 snippets: list[str]):
        self.stamp: float = stamp
        self.snippets: list[str] = snippets

def check_meeting_table_title(table: Tag, expected_title: str):
    # raise AttributeError or TypeError if selector chain is not valid
    title: str = table.select('thead > tr label')[0].getText()
    if title is None:
        raise RuntimeError(f"Expected table title but was None.")
    if title != expected_title:
        raise RuntimeError(f"Expected table title '{expected_title}' but got '{title}'.")

def get_dict_from_meeting_table(table: Tag, num_rows: int = -1, num_cells: int = -1) -> dict:
    tabledict = dict()
    tablerows = table.select('tbody > tr')
    if tablerows is None:
        raise RuntimeError(f"Did not any find tbody rows in table {table}.")
    # infotable should have num_rows rows in tbody
    if num_rows != -1 and len(tablerows) != num_rows:
        raise RuntimeError(f"Expected {num_rows} rows in infotable.tbody but found {len(tablerows)}.")
    for tr in tablerows:
        cells = tr('td')
        # infotable tbody row should have num_cells cells
        if num_cells != -1 and len(cells) != num_cells:
            raise RuntimeError(f"Expected {num_cells} cells in row but got {len(cells)}.")
        tabledict[cells[0].text.strip()] = cells[1].text.strip()
    return tabledict

def get_list_from_meeting_table(table: Tag, num_rows: int = -1, num_cells: int = -1) -> list:
    tablelist = list()
    tablerows = table.select('tbody > tr')
    if tablerows is None:
        raise RuntimeError(f"Did not any find tbody rows in table {table}.")
    # infotable should have num_rows rows in tbody
    if num_rows != -1 and len(tablerows) != num_rows:
        raise RuntimeError(f"Expected {num_rows} rows in infotable.tbody but found {len(tablerows)}.")
    for tr in tablerows:
        cells = tr('td')
        # infotable tbody row should have num_cells cells
        if num_cells != -1 and len(cells) != num_cells:
            raise RuntimeError(f"Expected {num_cells} cells in row but got {len(cells)}.")
        tablelist.append(cells[1].text.strip())
    return tablelist

def get_dict_from_input_vals(inputs: list[Tag]) -> dict[str, str]:
    input_dict = dict()
    for input in inputs:
        values: str | list[str] = input['value']
        ids: str | list[str] = input['id']
        id: str = ids if type(ids) is str else ','.join(ids)
        if type(values) is list[str]:
            input_dict[id] = ','.join(values)
        else:
            input_dict[id] = values
    return input_dict

def onclicks_to_onclick(onclicks: str | list[str]) -> str:
    if type(onclicks) is list[str]:
        return ','.join(onclicks)
    return onclicks # type: ignore

def parse_doclist(links: list[Tag]) -> list[tuple[str, str]]:
    return [(link.get_text(), onclicks_to_onclick(link['onclick'])) for link in links]

DATE_PATTERN = "%a, %d %b %Y %H:%M:%S GMT"

# TODO: change to use local timezone for remote working
def get_stamp(response: Response) -> float:
    if 'Date' in response.headers:
        string: str = response.headers['Date']
        return local_dt_to_posix(dt.datetime.strptime(string, DATE_PATTERN))
    return 0.0

def parse_meeting(response: Response) -> RawMeeting:
    soup = bs(response.text, "html.parser")

    # get meeting tables
    tables = soup.find_all(name="table", class_="table meeting")

    if len(tables) != 4:
        raise RuntimeError(f"Expected 4 tables of class 'table meeting' in html, but found {len(tables)}.")

    # parse infotable
    infotable = tables[0]
    inputs: list[Tag] = infotable.select('thead > tr > input')
    if len(inputs) != 13:
        raise RuntimeError(f"Expected 13 input tags but only got {len(inputs)}.")
    flag_dict: dict[str, str] = get_dict_from_input_vals(inputs)

    # parse infotable hidden input values
    is_meeting_date_changed: str = flag_dict['HdnMeetingDateChange']
    is_meeting_time_changed: str = flag_dict['HdnMeetingTimeChange']
    is_address_changed: str = flag_dict['HdnAddressChange']
    is_annual_calendar_changed: str = flag_dict['HdnIsAnnualCalendarChange']
    is_emergency_changed: str = flag_dict['HdnIsEmergencyChange']
    is_public_notice_changed: str = flag_dict['HdnIsPublicNoticeChange']
    is_agenda_changed: str = flag_dict['HdnIsAgendaChange']
    is_emergency_flag: str = flag_dict['HdnEmergencyStr']
    is_annual_calendar_flag: str = flag_dict['HdnAnualStr']
    is_public_notice_flag: str = flag_dict['HdnIspublicAnnouncementnotice']
    is_cancelled: str = flag_dict['HdnCancelMeetingFlag']
    cancelled_dt: str = flag_dict['HdnCancelMeetingDateTime']
    cancelled_reason: str = flag_dict['HdnCancelledComments']
    
    # parse infotable tbody rows
    # use dict so KeyError is raised if key is not in table
    infodict = get_dict_from_meeting_table(infotable)
    body: str = infodict['Public Body Name:']
    meeting_date: str = infodict['Date:']
    meeting_time: str = infodict['Time:']
    meeting_address: str = infodict['Address:']
    filing_dt: str = infodict['Filed on:']

    # parse agendas
    agenda_table = tables[1]
    agendas: list[tuple[str, str]] = parse_doclist(agenda_table.select('tbody > tr > td > a'))

    # parse minutes
    minutes_table = tables[2]
    minutes: list[tuple[str, str]] = parse_doclist(minutes_table.select('tbody > tr > td > a'))

    # parse point of contact
    contact_table = tables[3]
    check_meeting_table_title(contact_table, 'Contact Information')
    contact_dict = get_dict_from_meeting_table(contact_table)
    contact_name: str = contact_dict['Contact Person:']
    contact_phone: str = contact_dict['Phone:']
    contact_email: str = contact_dict['Email:']

    return RawMeeting(stamp=get_stamp(response),
                        body=body,
                        meeting_date=meeting_date,
                        meeting_time=meeting_time,
                        meeting_address=meeting_address,
                        filing_dt=filing_dt,
                        agendas=agendas,
                        minutes=minutes,
                        contact_name=contact_name,
                        contact_phone=contact_phone,
                        contact_email=contact_email,
                        is_meeting_date_changed=is_meeting_date_changed,
                        is_meeting_time_changed=is_meeting_time_changed,
                        is_address_changed=is_address_changed,
                        is_annual_calendar_changed=is_annual_calendar_changed,
                        is_emergency_changed=is_emergency_changed,
                        is_public_notice_changed=is_public_notice_changed,
                        is_agenda_changed=is_agenda_changed,
                        is_emergency=is_emergency_flag,
                        is_annual_calendar=is_annual_calendar_flag,
                        is_public_notice=is_public_notice_flag,
                        is_cancelled=is_cancelled,
                        cancelled_dt=cancelled_dt,
                        cancelled_reason=cancelled_reason)

def parse_body(om_response: Response, gd_response: Response, bm_response: Response) -> RawBody:
    om = parse_body_om_page(om_response.text)
    gd = parse_body_gd_page(gd_response.text)
    bm = parse_body_bm_page(bm_response.text)
    return RawBody(stamp=get_stamp(om_response), om=om, gd=gd, bm=bm)

def parse_body_om_page(text: str) -> RawOMBody:
    soup = bs(text, "html.parser")

    forms = soup.find_all('form')
    
    header_form = forms[0]

    name: str = header_form.find('h1').get_text()
    rows = header_form.find_all('div', class_='row')
    vals = [row.find_all('div', recursive=False)[1].text.strip() for row in rows]
    contact_name: str = vals[0]
    contact_phone: str = vals[1]
    contact_email: str = vals[2]

    form = forms[1]
    subcommittee_table: Tag = form.find('h2', class_='subTitle').next_sibling.next_sibling
    if subcommittee_table and subcommittee_table.name == 'div':
        subcommittees: list[tuple[str, str]] = [(link['href'], link.text) for link in subcommittee_table.find_all('a')]
    else:
        subcommittees = []
    
    return RawOMBody(name, contact_name, contact_phone, contact_email, subcommittees)

def parse_body_gd_page(text: str) -> RawGDBody:
    soup = bs(text, "html.parser")
    forms = soup.find_all('form')
    form = forms[1]
    if form.find('input', id='IsGovDataFlag')['value'] == '0':
        return RawGDBody(dict(), '', '', '', '', '', '', '', '', dict())
    standard_tables = form.find_all('table', class_='table meeting')
    has_contact_table = len(standard_tables) == 3
    if has_contact_table:
        contact_information = get_dict_from_meeting_table(standard_tables[0])
        social_table = standard_tables[1]
        attributes_table = standard_tables[2]
    else:
        contact_information = dict()
        social_table = standard_tables[0]
        attributes_table = standard_tables[1]
    social_list = get_list_from_meeting_table(social_table)
    facebook: str = social_list[0]
    twitter: str = social_list[1]
    instagram: str = social_list[2]
    linkedin: str = social_list[3]
    attribute_rows = attributes_table.tbody.find_all('tr', recursive=False)
    if len(attribute_rows) == 5:
        budget: str = attribute_rows[0].find_all('td')[1].text
        personnel: str = attribute_rows[1].find_all('td')[1].text
        description: str = attribute_rows[2].find_all('td')[0].text
        responsibilities: str = attribute_rows[4].find_all('td')[0].text
    else:
        budget = ''
        personnel = ''
        description = ''
        responsibilities = ''

    return RawGDBody(
        contact_information=contact_information,
        facebook=facebook,
        twitter=twitter,
        instagram=instagram,
        linkedin=linkedin,
        budget=budget,
        personnel=personnel,
        description=description,
        responsibilities=responsibilities,
        people=dict())

def parse_body_bm_page(text: str) -> RawBMBody:
    soup = bs(text, "html.parser")
    forms = soup.find_all('form')
    form = forms[1]
    if form.find('input', id='IsBoardsFlag')['value'] == '0':
        return RawBMBody(None, ('', ''), list())
    max_members: str = form.find('label').next_sibling.strip()
    authority_link = form.find('a', recursive=False)
    if False and authority_link is not None:
        authority = (authority_link.text, authority_link['href'])
    else:
        authority = ('', '')
    board_table = form.find(id='BoardMemberDetail')
    board_members = []
    for tr in board_table.tbody.find_all('tr'):
        member = tuple(td.text for td in tr.find_all('td'))
        board_members.append(member)
    return RawBMBody(
        max_members=max_members,
        authority=authority,
        board_members=board_members)

def extract_text(bytes: bytes, content_type: str = 'application/pdf', output_format: str = 'text/html') -> Response:
    files = {"files": bytes}
    headers = {'Content-type': content_type, 'Accept': output_format}
    tika_response: Response = put(TIKA_ENDPOINT, files=files, headers=headers)
    return tika_response

def parse_document(sos_response: Response) -> RawDocument:
    assert(is_tika_server_healthy())
    text = re.sub('\n+', '', extract_text(sos_response.content).text)
    ps = (p.text.strip() for p in bs(text, "html.parser").find_all('p'))
    snippets = [re.sub('\s+', ' ', p) for p in ps if p]
    return RawDocument(stamp=get_stamp(sos_response),
                       snippets=snippets)
