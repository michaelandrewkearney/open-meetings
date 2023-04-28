import requests
from bs4 import BeautifulSoup as bs, Tag
from riomp_scrape.objects import AnalysisMeeting, Meeting, Document, DocumentType, Person, URL
from riomp_scrape.omp_utils import parse_sos_dt_to_timestamp, strip_ri_phone
import re
import datetime as dt

# parses a Document object from a link as presented on ViewMeetingDetails page
def parse_document_from_link(link: Tag) -> Document:
    # match optional name, document type, posted datetime, and poster from link text
    # text has convention "{name}, {doctype} filed on {datetime} by {poster}" or "{doctype} filed on {datetime} by {poster}"
    pattern: str = "(?:(.*), )?(Agenda|Minutes) filed on (.*) by (.*)"
    matches = re.search(pattern, link.get_text())
    # check for exactly four regex matches
    if matches is None:
        raise TypeError("Error parsing Document from string '{}'. No matches found.".format(link.get_text()))
    if len(matches.groups()) != 4:
        raise TypeError("Error parsing Document from string '{}'. Number of matches is not 4.".format(link.get_text()))
    # name will be None if not supplied, preserving index of other groups
    name: str | None = matches.group(1)
    doctype: DocumentType = DocumentType(matches.group(2))
    post_dt: float = parse_sos_dt_to_timestamp(matches.group(3))
    poster: Person = Person(name=matches.group(4))

    # parse filepath from js function argument in link's onlick attribute
    # Tags can have multi-valued attrs, but we expect a single value. 
    onclick: list[str] | str = link['onclick']
    if type(onclick) is str:
        str_onclick: str = onclick
    else :
        raise TypeError(f"Expect single str for Document link 'onclick' attribute but got list of str:\n{onclick}")
    
    # onclick attr has convention "DownloadMeetingFiles('{filepath}')"
    path_match = re.search("\\'(.*)\\'", str_onclick)
    # check for single regex match
    if path_match is None:
        raise TypeError("Could not parse Document filepath from '{}'. No matches found.".format(str_onclick))
    if len(path_match.groups()) != 1:
        raise TypeError("Could not parse Document filepath from '{}. Number of matches is not 1.'".format(str_onclick))
    
    filepath: str = str(path_match.group(1))
    # reduce double backslash to single backslash
    while "\\\\" in filepath:
        filepath = filepath.replace('\\\\', '\\')

    return Document(doctype, name, filepath, post_dt, poster)

# TODO: ensure compatability with all formats
def join_meeting_date_and_time(date: str, time: str) -> str:
    if re.match('\\D{3} \\d?\\d \\d{4}', date) is None:
        raise ValueError("Cannot join meeting date and time: date '{date}' is not of format 'Jan 1 1970'.")
    if re.match('\\d?\\d:\\d\\d (?:A|P)M', time) is None:
        raise ValueError("Cannot join meeting date and time: date '{time}' is not of format '1:00 PM'.")
    new_time: str = re.sub(' ', '', time)
    return f"{date}, {new_time}"

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

def get_dict_from_docs(links: list[Tag]) -> dict[str, str]:
    doc_dict = dict()
    for link in links:
        onclicks: str | list[str] = link['onclick']
        if type(onclicks) is list[str]:
            doc_dict[link.get_text()] = ','.join(onclicks)
        else:
            doc_dict[link.get_text()] = onclicks
    return doc_dict

def parse_analysis_meeting(text: str):
    soup = bs(text, "html.parser")

    form_action: str | list[str] = soup.select('form')[0]['action']

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
    is_annual_flag: str = flag_dict['HdnAnualStr']
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
    is_emergency: str = infodict['Emergency Meeting:']
    is_annual_calendar: str = infodict['Annual Calendar:']
    is_public_notice: str = infodict['Public Announcement:']
    

    # parse agendas
    agenda_table = tables[1]
    check_meeting_table_title(agenda_table, 'Agenda')
    agendas: dict[str, str] = get_dict_from_docs(agenda_table.select('tbody > tr > td > a'))

    # parse minutes
    minutes_table = tables[2]
    check_meeting_table_title(minutes_table, 'Meeting Minutes')
    minutes: dict[str, str] = get_dict_from_docs(minutes_table.select('tbody > tr > td > a'))

    # parse point of contact
    contact_table = tables[3]
    check_meeting_table_title(contact_table, 'Contact Information')
    contact_dict = get_dict_from_meeting_table(contact_table)
    contact_person: str = contact_dict['Contact Person:']
    phone: str = contact_dict['Phone:']
    email: str = contact_dict['Email:']

    return AnalysisMeeting(form_action, body, meeting_date, meeting_time, meeting_address, filing_dt, is_emergency, is_annual_calendar, is_public_notice, agendas, minutes, contact_person, phone, email, is_meeting_date_changed, is_meeting_time_changed, is_address_changed, is_annual_calendar_changed, is_emergency_changed, is_public_notice_changed, is_agenda_changed, is_emergency_flag, is_annual_flag, is_public_notice_flag, is_cancelled, cancelled_dt, cancelled_reason)

# TODO
def get_body_id_from_name(body_name: str) -> int:
    return -1

def get_docs_from_doc_table(table: Tag) -> list[Document]:
    doclist: list[Document] = list()
    links: list[Tag] = table.select('tbody.tr.td.a')
    # TODO: check for tag selection validity
    for tag in links:
        doclist.append(parse_document_from_link(tag))
    return doclist

def scrape_meeting_details(text: str):
    soup = bs(text, "html.parser")

    # parse meeting id
    form_action: str | list[str] = soup.select('form')[0]['action']
    if type(form_action) is str:
        url: URL = URL(parse=form_action)
    else:
        raise TypeError("Expect single str for form 'action' attribute but got list of str:\n{}")
    str_id: str | None = url.get_query_arg('MeetingID')
    if str_id:
        # will throw ValueError if MeetingID is not parseable to int
        id: int = int(str_id)
    else:
        raise RuntimeError(f"Could not parse MeetingID from URL '{url}'.")

    # get meeting tables
    tables = soup.find_all(name="table", class_="table meeting")

    if len(tables) != 4:
        raise RuntimeError(f"Expected 4 tables of class 'table meeting' in html, but found {len(tables)}.")

    # parse infotable
    infotable = tables[0]
    inputs: list[Tag] = infotable.select('thead.tr.input')
    if len(inputs) != 13:
        raise RuntimeError(f"Expected 13 input tags but only got {len(inputs)}.")
    flag_dict: dict[str, str] = get_dict_from_input_vals(inputs)


    # parse infotable hidden input values
    is_meeting_dt_changed: bool = (flag_dict['HdnMeetingDateChange'] == '1' or
                                   flag_dict['HdnMeetingTimeChange'] == '1')
    is_address_changed: bool = flag_dict['HdnAddressChange'] == '1'
    is_annual_calendar_changed: bool = flag_dict['HdnIsAnnualCalendarChange'] == '1'
    is_emergency_changed: bool = flag_dict['HdnIsEmergencyChange'] == '1'
    is_public_notice_changed: bool = flag_dict['HdnIsPublicNoticeChange'] == '1'
    is_agenda_changed: bool = flag_dict['HdnIsAgendaChange'] == '1'
    is_cancelled: bool = flag_dict['HdnCancelMeetingFlag'] == '1'
    
    if is_cancelled:
        str_cancel_dt: str = flag_dict['HdnCancelMeetingDateTime']
        cancelled_dt: float | None = parse_sos_dt_to_timestamp(str_cancel_dt)
        cancelled_reason = flag_dict['HdnCancelledComments']
    else:
        # TODO: see if val is stored in dict when meeting is not cancelled
        cancelled_dt = None
        cancelled_reason = None
    
    # parse infotable tbody rows
    # use dict so KeyError is raised if key is not in table
    infodict = get_dict_from_meeting_table(infotable)
    body: int = get_body_id_from_name(infodict['Public Body Name:'])
    if len(infodict['Date:']) > 0 and len(infodict['Time:']) > 0:
        meeting_dt: float = parse_sos_dt_to_timestamp(
            join_meeting_date_and_time(infodict['Date:'],
                                       infodict['Time:']))
    else:
        meeting_dt = 0
    meeting_address: str = infodict['Address:']
    if len(infodict['Filed on:']) > 0:
        filing_dt: float = parse_sos_dt_to_timestamp(infodict['Filed on:'])
    else: filing_dt = 0
    is_emergency_meeting: bool = 'Yes' in infodict['Emergency Meeting:']
    is_annual_calendar: bool = 'Yes' in infodict['Annual Calendar:']
    is_public_notice: bool = 'Yes' in infodict['Public Announcement:']

    # parse agendas
    agenda_table = tables[1]
    check_meeting_table_title(agenda_table, 'Agenda')
    agendas: list[Document] = get_docs_from_doc_table(agenda_table)

    # parse minutes
    minutes_table = tables[2]
    check_meeting_table_title(minutes_table, 'Minutes')
    minutes: list[Document] = get_docs_from_doc_table(minutes_table)

    # parse point of contact
    contact_table = tables[3]
    check_meeting_table_title(contact_table, 'Contact Information')
    contact_dict = get_dict_from_meeting_table(contact_table)
    point_of_contact: Person = Person(title=None,
                                      name=contact_dict['Contact Person:'],
                                      phone=strip_ri_phone(contact_dict['Phone:']),
                                      email=contact_dict['Email:'])

    return Meeting(body, meeting_dt, meeting_address, filing_dt, is_emergency_meeting, is_annual_calendar, is_public_notice, agendas, minutes, point_of_contact, is_meeting_dt_changed, is_address_changed, is_annual_calendar_changed, is_emergency_changed, is_public_notice_changed, is_agenda_changed, is_cancelled, cancelled_dt, cancelled_reason)