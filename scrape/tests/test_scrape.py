# import pytest
# from bs4 import BeautifulSoup as bs, Tag, NavigableString
# from scrape.scrape.objects import AnalysisMeeting, Document, DocumentType
# from riomp_scrape.meeting import parse_analysis_meeting, parse_document_from_link
# from riomp_scrape.omp_utils import timestamp_to_sos_dt, get_meeting_details_page
# import datetime as dt

# def load_mock_meeting(url: str) -> str:
#     f = open(url)
#     return f.read()

# def get_soup_from_file(url: str) -> bs:
#     return bs(load_mock_meeting(url))


# def test_lbl_meeting_change():
#     #soup = get_soup_from_file('data/mock_cancelled_meeting.html')
#     pass

# def test_parse_document_from_link():
#     f = open("tests/data/mock_document_links.html")
#     links = bs(f.read(), "html.parser")("a")
#     d1: Document = parse_document_from_link(links[0])
#     assert d1.doctype == DocumentType.AGENDA
#     assert d1.name == None
#     assert timestamp_to_sos_dt(d1.post_dt) == "May 28 2021, 03:01PM"
#     assert d1.filepath == '\\Notices\\4749\\2021\\397008.pdf'
#     assert d1.poster.name == "Stephany Lopes"

#     d2: Document = parse_document_from_link(links[1])
#     assert d2.doctype == DocumentType.AGENDA
#     assert d2.name == ''
#     assert timestamp_to_sos_dt(d2.post_dt) == "May 2 2021, 02:58PM"
#     assert d2.filepath == "\\Notices\\4749\\2021\\397007.pdf"
#     assert d2.poster.name == "Stephany Lopes"

#     d3: Document = parse_document_from_link(links[2])
#     assert d3.doctype == DocumentType.MINUTES
#     assert d3.name == 'approved'
#     assert timestamp_to_sos_dt(d3.post_dt) == "Mar 29 2023, 05:17PM"
#     assert d3.filepath == "\\Minutes\\4832\\2023\\456234.pdf"
#     assert d3.poster.name == "Dianna Liss"

# def test_parse_meeting_view_to_analysis_meeting():
#     f = open('tests/data/1009540.html')
#     mtg: AnalysisMeeting = parse_analysis_meeting(f.read())
#     assert mtg.form_action == "/OpenMeetingsPublic/ViewMeetingDetailByID?id=0.8631531299131113&MeetingID=1009540"
#     assert mtg.body == "Providence Board of Licenses"
#     assert mtg.meeting_date == "Jun  2 2021"
#     assert mtg.meeting_time == "3:00 PM"
#     assert mtg.meeting_address == "Virtual, Providence, RI, 02903"
#     assert mtg.filing_dt == "May 28 2021, 02:58PM"
#     assert mtg.is_emergency == 'No'
#     assert mtg.is_annual_calendar == 'No'
#     assert mtg.is_public_notice == 'No'
#     assert len(mtg.agendas) == 2
#     assert mtg.agendas['Agenda filed on May 28 2021, 03:01PM by Stephany Lopes'] == "DownloadMeetingFiles('\\\\Notices\\\\4749\\\\2021\\\\397008.pdf')"
#     assert mtg.agendas['Agenda filed on May 28 2021, 02:58PM by Stephany Lopes'] == "DownloadMeetingFiles('\\\\Notices\\\\4749\\\\2021\\\\397007.pdf')"
#     assert len(mtg.minutes) == 0
#     assert mtg.contact_person == "Stephany Lopes"
#     assert mtg.phone == "(401) 680-5207"
#     assert mtg.email == "slopes@providenceri.gov"
#     assert mtg.is_meeting_date_changed == '0'
#     assert mtg.is_meeting_time_changed == '0'
#     assert mtg.is_address_changed == '0'
#     assert mtg.is_annual_calendar_changed == '0'
#     assert mtg.is_emergency_changed == '0'
#     assert mtg.is_public_notice_changed == '0'
#     assert mtg.is_agenda_changed == '1'
#     assert mtg.is_cancelled == '1'
#     assert mtg.cancelled_dt == 'Jun  2 2021, 01:02PM'
#     assert mtg.cancelled_reason == "6/2/2021 Meeting has been cancelled. All items will be heard on 6/9/2021"

# def test_parse_empty_meeting_to_analysis_meeting():
#     mtg: AnalysisMeeting = parse_analysis_meeting(get_meeting_details_page(0))
#     print(mtg.__dict__)
