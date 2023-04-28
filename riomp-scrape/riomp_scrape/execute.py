from io import TextIOWrapper
import sqlite3
import sys
from time import sleep
import traceback
from typing import Callable, Iterable, Iterator, Tuple, Any
from riomp_scrape.objects import AnalysisMeeting
from riomp_scrape.meeting import parse_analysis_meeting
import datetime as dt
from os.path import isfile, isdir, exists
from os import mkdir, listdir
import requests
from requests import Response
from requests_html import HTML
import pandas as pd
from progress.bar import Bar
import threading
from pprint import pprint
from sqlite3 import Connection
from threading import Lock
from thread.analysis import build_is_normal, id_matches_form_action, is_document_normal, DATE_PATTERN, TIME_PATTERN, DT_PATTERN, YES_NO_PATTERN, INT_FLAG_PATTERN, PHONE_PATTERN, EMAIL_PATTERN
from enum import StrEnum, Enum
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection
import re
from tika import parser


from riomp_scrape.io_utils import make_dir_if_not_exists_and_check_is_dir, make_log, make_log_and_lock, threadsafe_write_if_log
from thread.download import build_download_unique_resource, threaded_download_resource, build_write_to_file, mock_write_to_file
from thread.process import build_process_unique_resource, threaded_process_resource

# Retry default constants are tailored to maximize request efficiency to the RISOS API without overloading it
TRY_COUNT = 3
TRY_PAUSE: float = 10.0
WORKERS = 1024

MEETING_LOWER_BOUND: int = 700000
MEETING_UPPER_BOUND: int = 130000
BODY_LOWER_BOUND: int = 0
BODY_UPPER_BOUND: int = 10000
DOCUMENT_LOWER_BOUND: int = 0
DOCUMENT_UPPER_BOUND: int = 0

DATA_DIR = 'data'
LOGS_DIR = f'{DATA_DIR}/logs'
DOWNLOADS_DIR = f'{DATA_DIR}/downloads'
FEATHERS_DIR = f'{DATA_DIR}/feathers'
DATABASE_FILE = f'{DATA_DIR}/database.db'

def setup_dir():
    make_dir_if_not_exists_and_check_is_dir(DATA_DIR)
    make_dir_if_not_exists_and_check_is_dir(LOGS_DIR)
    make_dir_if_not_exists_and_check_is_dir(DOWNLOADS_DIR)

raw_meeting_attributes = ['form_action',
                        'body',
                        'meeting_date',
                        'meeting_time',
                        'meeting_address',
                        'filing_dt',
                        'is_emergency',
                        'is_annual_calendar',
                        'is_public_notice',
                        'agendas',
                        'minutes',
                        'contact_person',
                        'phone',
                        'email',
                        'is_meeting_date_changed',
                        'is_meeting_time_changed',
                        'is_address_changed',
                        'is_annual_calendar_changed',
                        'is_emergency_changed',
                        'is_public_notice_changed',
                        'is_agenda_changed',
                        'is_emergency_flag',
                        'is_annual_flag',
                        'is_public_notice_flag',
                        'is_cancelled',
                        'cancelled_dt',
                        'cancelled_reason']

def setup_database():
    if not isfile(DATABASE_FILE):
        open(DATABASE_FILE, 'x').close()
    generated_cols = ',\n'.join(list(map(lambda col : col + " TEXT", raw_meeting_attributes)))
    database_execute(f'''
        CREATE TABLE IF NOT EXISTS raw_meetings (
            id INTEGER PRIMARY KEY,
            {generated_cols})''')

def database_execute(commands: str | list[str]):
    with sqlite3.connect(DATABASE_FILE) as conn:
        cur = conn.cursor()
        if type(commands) is list[str]:
            for command in commands:
                cur.execute(command)
        elif type(commands) is str:
            cur.execute(commands)
        conn.commit()

def setup_before_each():
    setup_dir()
    setup_database()
    
def build_request_resource(generate_url: Callable[[int], str]) -> Callable[[int], Response]:
    def request_resource(id: int) -> Response:
        url = generate_url(id)
        return requests.get(url)
    return request_resource

# Meeting Functions


MEETING_DOWNLOADS_DIR: str = f'{DOWNLOADS_DIR}/meetings'
make_dir_if_not_exists_and_check_is_dir(MEETING_DOWNLOADS_DIR)

def meeting_process_is_duplicate(id: int, conn: Connection) -> bool:
    cur = conn.cursor()
    cur.execute('''SELECT id FROM raw_meetings WHERE id=?''', (str(id),))
    result = cur.fetchone()
    return bool(result)

def meeting_request_resource(id: int) -> Response:
    url: str = f"https://opengov.sos.ri.gov/OpenMeetingsPublic/ViewMeetingDetailByID?MeetingID={id}"
    r = requests.get(url)
    r.iter_content()
    return requests.get(url)

def meeting_generate_filename(id: int) -> str:
    return f'{MEETING_DOWNLOADS_DIR}/{id}.html'

def meeting_process_resource(id: int, conn: Connection) -> None:
    with open(meeting_generate_filename(id)) as f:
        mtg: AnalysisMeeting = parse_analysis_meeting(f.read())
    if not mtg.is_real_meeting():
        return
    conn.cursor().execute('''INSERT INTO raw_meetings VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''', (
        id,
        mtg.form_action,
        mtg.body,
        mtg.meeting_date,
        mtg.meeting_time,
        mtg.meeting_address,
        mtg.filing_dt,
        mtg.is_emergency,
        mtg.is_annual_calendar,
        mtg.is_public_notice,
        str(mtg.agendas),
        str(mtg.minutes),
        mtg.contact_person,
        mtg.phone,
        mtg.email,
        mtg.is_meeting_date_changed,
        mtg.is_meeting_time_changed,
        mtg.is_address_changed,
        mtg.is_annual_calendar_changed,
        mtg.is_emergency_changed,
        mtg.is_public_notice_changed,
        mtg.is_agenda_changed,
        mtg.is_emergency_flag,
        mtg.is_annual_flag,
        mtg.is_public_notice_flag,
        mtg.is_cancelled,
        mtg.cancelled_dt,
        mtg.cancelled_reason
    ))
    conn.commit()

def meeting_download_is_duplicate(id: int) -> bool:
    is_in_dir = isfile(meeting_generate_filename(id))
    with Connection(DATABASE_FILE) as conn:
        is_processed = meeting_process_is_duplicate(id, conn)
    return is_in_dir or is_processed

def meeting_is_response_success(response: Response) -> bool:
    code: int = response.status_code
    return 200 <= code and code < 300


# Body Download Function
BODY_OM_DOWNLOADS_DIR: str = f'{DOWNLOADS_DIR}/bodies_om'
make_dir_if_not_exists_and_check_is_dir(BODY_OM_DOWNLOADS_DIR)

def body_process_is_duplicate(id: int) -> bool:
    return False

def body_om_get_url(id: int) -> str:
    return f'https://opengov.sos.ri.gov/OpenMeetingsPublic/OpenMeetingDashboard?subtopmenuId=201&EntityID={id}'

def body_gd_get_url(id: int) -> str:
    return f"https://opengov.sos.ri.gov/OpenMeetingsPublic/GovDirectory?subtopmenuID=202&EntityID={id}"

def body_bm_get_url(id: int) -> str:
    return f"https://opengov.sos.ri.gov/OpenMeetingsPublic/BoardMembers?subtopmenuID=203&EntityID={id}"



# Body GovDirectory Download Functions

BODY_GD_DOWNLOADS_DIR: str = f'{DOWNLOADS_DIR}/bodies_gd'
make_dir_if_not_exists_and_check_is_dir(BODY_GD_DOWNLOADS_DIR)

def body_gd_process_is_duplicate(id: int) -> bool:
    return False



def body_gd_request_resource(id: int) -> Response:
    url: str = body_gd_get_url(id)
    return requests.get(url)

def body_gd_generate_filename(id: int) -> str:
    return f'{BODY_GD_DOWNLOADS_DIR}/{id}.html'

def body_gd_download_is_duplicate(id: int) -> bool:
    is_in_dir = isfile(body_gd_generate_filename(id))
    is_processed = body_gd_process_is_duplicate(id)
    return is_in_dir or is_processed

def body_gd_is_response_success(response: Response) -> bool:
    code: int = response.status_code
    return 200 <= code and code < 300

# Body Board Members Download Functions

BODY_BM_DOWNLOADS_DIR: str = f'{DOWNLOADS_DIR}/bodies_bm'
make_dir_if_not_exists_and_check_is_dir(BODY_BM_DOWNLOADS_DIR)

def body_bm_process_is_duplicate(id: int) -> bool:
    return False



def body_bm_request_resource(id: int) -> Response:
    return requests.get(body_bm_get_url(id))

def body_bm_generate_filename(id: int) -> str:
    return f'{BODY_BM_DOWNLOADS_DIR}/{id}.html'

def body_bm_download_is_duplicate(id: int) -> bool:
    is_in_dir = isfile(body_bm_generate_filename(id))
    is_processed = body_bm_process_is_duplicate(id)
    return is_in_dir or is_processed

def body_bm_is_response_success(response: Response) -> bool:
    code: int = response.status_code
    return 200 <= code and code < 300

def body_process(id: int) -> Tuple[int, int]:

    return (id,3)


# Document Download Functions

DOCUMENT_DOWNLOADS_DIR: str = f'{DOWNLOADS_DIR}/documents'
make_dir_if_not_exists_and_check_is_dir(DOCUMENT_DOWNLOADS_DIR)

def document_process_is_duplicate(id: int) -> bool:
    return False

def get_document_filename_from_id(id: int) -> str:
    return '' # TODO

def document_request_resource(id: int) -> Response:
    url: str = f"https://opengov.sos.ri.gov/Common/DownloadMeetingFiles?FilePath={get_document_filename_from_id(id)}"
    return requests.get(url) # TODO: How to get PDF file from requests

def document_generate_filename(id: int) -> str:
    return f'{DOCUMENT_DOWNLOADS_DIR}/{id}.pdf'

def document_download_is_duplicate(id: int) -> bool:
    is_in_dir = isfile(document_generate_filename(id))
    is_processed = document_process_is_duplicate(id)
    return is_in_dir or is_processed

def document_is_response_success(response: Response) -> bool:
    code: int = response.status_code
    return 200 <= code and code < 300

def scrape_meeting(id: int) -> dict[str, str]:
    return {}

def scrape_body(id: int) -> dict[str, str]:
    return {}

def scrape_document(filename: str) -> dict[str, str]:
    return {}

def process_meeting(values: dict[str, str]) -> dict[str, Any]:
    return {}

def process_body(values: dict[str, str]) -> dict[str, Any]:
    return {}

def process_document(values: dict[str, str]) -> dict[str, Any]:
    return {}

def parse_sos_dt(dt: str) -> float:
    return 0.0

def multitry(max_tries: int, wait: float, func: Callable, *args):
    try_count = 0
    while try_count < max_tries:
        try_count += 1
        try:
            return func(*args)
        except Exception:
            sleep(wait)
    raise RuntimeError(f'{str(func)} with args {str(args)} failed after {try_count} tries with {wait} second wait.')

class DocType(Enum):
    AGENDA = 1
    MINUTES = 2

class RawDocument:
    def __init__(self,
                 name: str,
                 doctype: str,
                 dt: str,
                 filer: str,
                 path: str):
        self.name: str | None = name if name else None
        match(doctype.lower()):
            case 'agenda':
                self.doctype: DocType = DocType.AGENDA
            case 'minutes':
                self.doctype: DocType = DocType.MINUTES
            case _:
                raise ValueError(f'Unrecognized document type {doctype}')
        self.dt: float = parse_sos_dt(dt)
        self.filer: str | None = filer if filer else None
        self.path: str | None = re.sub('\\+', '/', path) if path else None
    
    def get_url(self) -> str:
        return f'https://opengov.sos.ri.gov/Common/DownloadMeetingFiles?FilePath={self.path}'
    
    def get_snippets(self):
        if self.path is None:
            return []
        response: Response = multitry(10, 3.0, requests.get, self.get_url())
        response.raw

        self.snippets: list[str] = []

class RawMeeting:
    def __init__(self,
                 scrape_ts: float,
                 id: int,
                 body: str,
                 meeting_date: str,
                 meeting_time: str,
                 meeting_address: str,
                 filing_dt: str,
                 agendas: list[Tuple[str, str]],
                 minutes: list[Tuple[str, str]],
                 contact_name: str,
                 contact_phone: str,
                 contact_email: str,
                 is_meeting_date_changed: int,
                 is_meeting_time_changed: int,
                 is_address_changed: int,
                 is_annual_calendar_changed: int,
                 is_emergency_changed: int,
                 is_public_notice_changed: int,
                 is_agenda_changed: int,
                 is_emergency: int,
                 is_annual_calendar: int,
                 is_public_notice: int,
                 cancelled: bool,
                 cancelled_dt: str,
                 cancelled_reason: str):
        self.scrape_ts: float = scrape_ts
        self.id: int = id
        self.body: str = body
        self.meeting_date: str = meeting_date
        self.meeting_time: str = meeting_time
        self.meeting_address: str = meeting_address
        self.filing_dt: str = filing_dt
        self.agendas: list[RawDocument] = agendas
        self.minutes: list[RawDocument] = minutes
        self.contact_name: str = contact_name
        self.contact_phone: str = contact_phone
        self.contact_email: str = contact_email
        self.is_meeting_date_changed: int = is_meeting_date_changed
        self.is_meeting_time_changed: int = is_meeting_time_changed
        self.is_address_changed: int = is_address_changed
        self.is_annual_calendar_changed: int = is_annual_calendar_changed
        self.is_emergency_changed: int = is_emergency_changed
        self.is_public_notice_changed: int = is_public_notice_changed
        self.is_agenda_changed: int = is_agenda_changed
        self.is_emergency: int = is_emergency
        self.is_annual_calendar: int = is_annual_calendar
        self.is_public_notice: int = is_public_notice
        self.cancelled: int = cancelled
        self.cancelled_dt: str = cancelled_dt
        self.cancelled_reason: str = cancelled_reason
      
    def to_dict(self) -> dict[str, Any]:
        return {}

class RawBody:
    def __init__(self,
                id: int,
                name: str,
                contact_name: str,
                contact_phone: str,
                contact_email: str,
                subcommittees: list[str],
                contact_information: dict[str, str],
                facebook: str,
                twitter: str,
                instagram: str,
                linkedin: str,
                budget: str,
                personnel: str,
                description: str,
                responsibilities: str,
                people: dict[str, list[Tuple[str, str, str, str]]],
                max_members: str,
                authority: Tuple[str, str]):
        self.id: int = id
        self.name: str = name
        self.contact_name: str = contact_name
        self.contact_phone: str = contact_phone
        self.contact_email: str = contact_email
        self.subcommittees: list[str] = subcommittees
        self.contact_information: dict[str, str] = contact_information
        self.facebook: str = facebook
        self.twitter: str = twitter
        self.instagram: str = instagram
        self.linkedin: str = linkedin
        self.budget: str = budget
        self.personnel: str = personnel
        self.description: str = description
        self.responsibilities: str = responsibilities
        self.people: dict[str, list[Tuple[str, str, str, str]]] = people
        self.max_members: str = max_members
        self.authority: Tuple[str, str] = authority
    
    def to_dict(self) -> dict[str, Any]:
        return {}

def scrape_meeting(id: int) -> RawMeeting:
    pass

def scrape_body(id: int) -> RawBody:
    pass



class ResourceType(StrEnum):
    __ignore__ = ['locks']
    MEETING = 'meeting'
    BODY = 'body'
    PERSON = 'person'
    DOCUMENT = 'document'
    SNIPPET = 'snippet'

    def get_db_fields(self) -> dict[str, type]:
        match(self):
            case ResourceType.MEETING:
                return {'_id': int,
                        'body': int,
                        'meeting_dt': float,
                        'meeting_address': str,
                        'virtual_link': str | None,
                        'filing_dt': float,
                        'emergency': bool,
                        'annual_calendar': bool,
                        'public_notice': bool,
                        'agendas': list[int],
                        'minutes': list[int],
                        'contact': int,
                        'cancelled': bool,
                        'cancelled_dt': float | None,
                        'cancelled_reason': str | None}
            case ResourceType.BODY:
                return {'_id': int,
                        'name': str,
                        'contact': int,
                        'address': str,
                        'phone': int,
                        'tty': str,
                        'fax': int,
                        'website': str,
                        'email': str,
                        'facebook': str,
                        'twitter': str,
                        'instagram': str,
                        'linkedin': str,
                        'attributes': dict[str, str|int],
                        'people': dict[str, list[int]],
                        'supercommittee': int | None,
                        'subcommittees': list[int] | None}
            case ResourceType.PERSON:
                return {'name': str,
                        'title': str | None,
                        'phone': int | None,
                        'email': str | None}
            case ResourceType.DOCUMENT:
                return {'meeting': int,
                        'most_recent': bool,
                        'filepath': str,
                        'name': str | None,
                        'doctype': DocType,
                        'dt': float,
                        'filer': int,
                        'snippets': list[int]}
            case ResourceType.SNIPPET:
                return {'content': str}

    def plural(self) -> str:
        match(self):
            case ResourceType.MEETING: return 'meetings'
            case ResourceType.BODY: return 'bodies'
            case ResourceType.PERSON: return 'persons'
            case ResourceType.DOCUMENT: return 'documents'
            case ResourceType.SNIPPET: return 'snippets'
    
    def is_updateable(self) -> bool:
        match(self):
            case (ResourceType.MEETING
                  | ResourceType.BODY):
                return True
            case (ResourceType.DOCUMENT
                  | ResourceType.PERSON
                  | ResourceType.SNIPPET):
                return False
    
    def collection_name(self) -> str:
        return self.plural()
    
    def changes_collection_name(self) -> str:
        return self.collection_name() + '_changes'
    
    def get_scrape(self) -> Callable[[int], dict[str, str]] | Callable[[str], dict[str, str]]:
        match (self):
            case ResourceType.MEETING:
                return scrape_meeting
            case ResourceType.BODY:
                return scrape_body
            case ResourceType.DOCUMENT:
                return scrape_document
            case _:
                raise RuntimeError(f'ResourceType {str(self)} is not updatable.')

    def get_process(self) -> Callable[[dict[str, str]], dict[str, Any]]:
        match (self):
            case ResourceType.MEETING:
                return process_meeting
            case ResourceType.BODY:
                return process_body
            case ResourceType.DOCUMENT:
                return process_document
            case _:
                raise RuntimeError(f'ResourceType {str(self)} is not updatable.')
    
    # TODO
    def get_lock(self) -> Lock:
        pass

    def get_collection(self, db: Database) -> Collection:
        return db[self.collection_name()]
    
    def get_changes_collection(self, db: Database) -> Collection:
        return db[self.changes_collection_name()]

    def build_in_db(self, db: Database) -> Callable[[int], bool]:
        def in_db(id: int) -> bool:
            collection = self.get_collection(db)
            return collection.find_one({'_id': id}) is not None
        return in_db

    def build_insert_db(self, db: Database) -> Callable[[dict[str, Any]], int]:
        field_types = self.get_db_fields()
        collection = self.get_collection(db)
        lock = self.get_lock()

        def insert_db(to_insert: dict[str, Any]) -> int:
            # Validate field types
            for name, type in field_types.items():
                assert(name in to_insert)
                assert(isinstance(to_insert[name], type))
            # Thread lock to prevent duplicate _id creation
            with lock:
                _id = collection.insert_one(to_insert).inserted_id
            return _id
        return insert_db
    
    def build_update_db(self, db: Database) -> Callable[[int], int]:
        if not self.is_updateable():
            raise RuntimeError(f'Error: cannot create update function for {str(self)}. Only updateable ResourceTypes can be updated.')
        def update_db(id: int | str) -> int:
            # scrape data
            timestamp: float = dt.datetime.utcnow().timestamp()

            scraped_data: dict[str, Any] = self.get_process()(self.get_scrape()(id)) # type: ignore
            col: Collection = db[self.collection_name()]
            id_query = {'_id': id}
            results: list = list(col.find(id_query))
            results_count: int = len(results)
            if results_count > 1:
                raise ValueError(f'Error: multiple entries for id {id} in {col}.')
            if results_count == 1:
                existing_data = results[0]
                changes: dict[str, Any] = dict()
                for key, val in existing_data.items():
                    if scraped_data[key] != val:
                        changes[key] = val
                if len(changes) > 0:
                    changes['id'] = existing_data['id']
                    changes['timestamp'] = existing_data['timestamp']
                    changes_col: Collection = db[self.changes_collection_name()]
                    changes_col.insert_one(changes)
                    col.update_one
                scraped_data['timestamp'] = timestamp
                for key in changes:
                    pass
            return 1
        return update_db

            
            

            # if item is in database
                # if any fields are different:
                    # log changed fields in changes database
                # else
                    # return
            # update fields in main database

# setup databases
    

# BUILD FUNCTIONS

def build_update_database(
        resource: ResourceType,
        get_resource: Callable[[int], Iterator[Any]],
        process_resource: Callable[[Iterator[Any]], dict[str, Any]],
        write_to_mongo: Callable[[str, int, float, dict[str, Any]], int],
        bar_and_lock: Tuple[Bar, Lock],
        log_and_lock: Tuple[TextIOWrapper, Lock],
) -> Callable[[int], int]:
    def update_database(id: int) -> int:

        # get resource

        # if item is in database
            # if any fields are different:
                # log changed fields in changes database
            # else
                # return
        # update fields in main database
        return 1
    return update_database

def format_results(
        results: Iterator[Tuple[int, int, int]],
        start_id:int,
        parse_count: int,
        workers: int,
        try_count: int,
        elapsed: float) -> str:
    counts = [0, 0, 0]
    tries: dict[int, int] = dict((i, 0) for i in range (0, try_count+1))
    for _, outcome, count in results:
        counts[outcome] += 1
        tries[count] += 1
    download_count = (counts[0]+counts[2])
    return ('\n'.join([
    f'\tmax_workers:    {workers}',
    f'\ttime elapsed:   {elapsed}',
    f'\tavg time:       {0 if download_count == 0 else elapsed/download_count}',
    f'\tstart_id:       {start_id}',
    f'\ttotal count:    {parse_count}',
    f'\tdownloaded:     {counts[0]}',
    f'\tduplicates:     {counts[1]}',
    f'\terrors:         {counts[2]}',
    f'\tnonerrors:      {counts[0]+counts[1]}',
    f'\terror rate:     {0 if download_count == 0 else counts[2]/download_count}',
    f'\ttry distribution:',
    str(''.join(list((f'\t\t{k}:\t{tries[k]}\n' if tries[k] else '' for k in tries.keys()))))]))

def format_test_results(
        results: Iterator[Tuple[int, int, int]],
        elapsed: float) -> str:
    counts = [0, 0, 0]
    tries: dict[int, int] = {}
    for _, outcome, count in results:
        counts[outcome] += 1
        if count not in tries:
            tries[count] = 0
        tries[count] += 1
    count = (counts[0]+counts[1]+counts[2])
    return ('\n'.join([
    f'\tsuccesses:      {counts[0]}/{counts[0]+counts[1]+counts[2]}',
    f'\tavg time:       {0 if count == 0 else elapsed/counts[0]}',
    f'\terror rate:     {0 if count == 0 else counts[2]/count}',
    f'\ttry distribution:',
    str(''.join(list((f'\t\t{k}:\t{tries[k]}\n' if tries[k] else '' for k in tries.keys()))))]))

def main(args):
    setup_before_each()
    arg_count = len(args)
    if arg_count >= 2:
        command: str = args[1]
        match(command):
            case 'help':
                print("Use this script to scrape meetings into the analysis database.\nCommands:\n\tclear : Clears and resets the database\n\ttest (num_threads)? (num_tests)? (start_id)? : tests thread efficiency\n\t\tnum_threads: the numbers of threads to test\n\t\tnum_tests: the number of meetings to test\n\t\tstart_id: the id of the first meeting\n\t(start_id) (num_mtgs) : parses meetings into database\n\t\tstart_id: the id of the first meeting\n\t\tnum_mtgs: the number of meetings to parse")
                return
            case 'test':
                min_arg_count:int = 3
                max_arg_count:int = 3
                if arg_count < min_arg_count or arg_count > max_arg_count:
                    print(f"Error: invalid number of arguments.")
                    return
                command_to_test: str = args[2]
                match(command_to_test):
                    case 'download':
                        start_id:int = 1000000
                        try_count: int = 10
                        request_resource = meeting_request_resource
                        download_is_duplicate = lambda id : False
                        is_response_success = meeting_is_response_success
                        write_to_file = mock_write_to_file
                        workers_list = [64, 128, 256, 512, 1024]
                        try_pause_list = [0.1, 1.0, 5.0, 10.0]
                        download_count = 1024
                        outcomes: dict[int, dict[float, str]] = {}
                        log_and_lock = make_log_and_lock(LOGS_DIR, name=command)
                        for workers in workers_list:
                            outcomes[workers] = dict()
                            for try_pause in try_pause_list:
                                print(f'{workers} workers with {try_pause} try_pause')
                                
                                bar_and_lock: Tuple[Bar, threading.Lock] = (Bar('Testing', max=download_count), threading.Lock())
                                    
                                download_resource = build_download_unique_resource(
                                    request_resource=request_resource,
                                    is_duplicate=download_is_duplicate,
                                    is_response_success=is_response_success,
                                    write_to_file=write_to_file,
                                    try_count=try_count,
                                    try_pause=try_pause,
                                    resource_name='test',
                                    bar_and_lock=bar_and_lock,
                                    log_and_lock=log_and_lock)
                                before = dt.datetime.utcnow().timestamp()
                                try:
                                    with bar_and_lock[0]:
                                        results = threaded_download_resource(
                                            range(start_id,
                                                start_id+download_count).__iter__(),
                                            download_resource,
                                            max_workers=workers)
                                except Exception as e:
                                    threadsafe_write_if_log(f'Error: {type(e)}', log_and_lock)
                                    traceback.print_exc()
                                    continue
                                elapsed = dt.datetime.utcnow().timestamp() - before
                                outcomes[workers][try_pause] = format_test_results(results, elapsed)
                        for workers in workers_list:
                            for try_pause in try_pause_list:
                                print(f'Results for {workers} workers with pause of {try_pause}:')
                                print(outcomes[workers][try_pause])
                        log_and_lock[0].close()
                        return
                    case default:
                        print(f"Unrecognized argument '{command_to_test}'.")
                        return
            case 'download':
                # execute.py download type start count threads tries pause
                min_arg_count:int = 5
                max_arg_count:int = 8
                if arg_count < min_arg_count or arg_count > max_arg_count:
                    print(f"Error: invalid number of arguments.")
                    return
                name = args[2]
                workers: int = WORKERS
                try_count = TRY_COUNT
                try_pause = TRY_PAUSE
                try:
                    start_id: int = int(args[3])
                    download_count: int = int(args[4])
                    if arg_count >= 6:
                        workers = int(args[5])
                    if arg_count >= 7:
                        try_count = int(args[6])
                    if arg_count >= 8:
                        try_pause = float(args[7])
                except ValueError:
                    print("Error: could not parse arguments as numbers.")
                    return
                min_id: int
                max_id: int
                match(name):
                    case 'meeting':
                        min_id = MEETING_LOWER_BOUND
                        max_id = MEETING_UPPER_BOUND
                        request_resource = meeting_request_resource
                        download_is_duplicate = meeting_download_is_duplicate
                        is_response_success = meeting_is_response_success
                        generate_filename = meeting_generate_filename
                    case 'body_gd':
                        min_id = BODY_LOWER_BOUND
                        max_id = BODY_UPPER_BOUND
                        request_resource = body_gd_request_resource
                        download_is_duplicate = body_gd_download_is_duplicate
                        is_response_success = body_gd_is_response_success
                        generate_filename = body_gd_generate_filename
                    case 'body_bm':
                        min_id = BODY_LOWER_BOUND
                        max_id = BODY_UPPER_BOUND
                        request_resource = body_bm_request_resource
                        download_is_duplicate = body_bm_download_is_duplicate
                        is_response_success = body_bm_is_response_success
                        generate_filename = body_bm_generate_filename
                    case 'document':
                        print("No support yet for downloading documents.")
                        return
                        min_id = DOCUMENT_LOWER_BOUND
                        max_id = DOCUMENT_UPPER_BOUND
                        request_resource = document_request_resource
                        download_is_duplicate = document_download_is_duplicate
                        is_response_success = document_is_response_success
                        generate_filename = document_generate_filename
                    case default:
                        print(f"Unrecognized argument '{name}'.")
                        return
                log_and_lock=make_log_and_lock(dir=LOGS_DIR, name=f'{command}_{name}')
                write_to_file = build_write_to_file(generate_filename)
                bar: Bar = Bar('Downloads', max=download_count)
                bar_and_lock = (bar, threading.Lock())
                download_resource = build_download_unique_resource(
                    request_resource=request_resource,
                    is_duplicate=download_is_duplicate,
                    is_response_success=is_response_success,
                    write_to_file=write_to_file,
                    try_count=try_count,
                    try_pause=try_pause,
                    bar_and_lock=bar_and_lock,
                    log_and_lock=log_and_lock,
                    resource_name=name,
                    verbose=False)
                try:
                    with bar:
                        before = dt.datetime.utcnow().timestamp()
                        results = threaded_download_resource(
                            range(start_id,
                                start_id+download_count).__iter__(),
                            download_resource,
                            max_workers=workers,)
                        elapsed = dt.datetime.utcnow().timestamp() - before
                except Exception as e:
                    threadsafe_write_if_log(f'Error: {type(e)}', log_and_lock)
                    return

                print(format_results(
                    results = results,
                    start_id = start_id,
                    parse_count = download_count,
                    workers = workers,
                    try_count = try_count,
                    elapsed = elapsed))
                log_and_lock[0].close()
                return
            case 'process':
                # execute.py process type start count
                min_arg_count:int = 5
                max_arg_count:int = 5
                if arg_count < min_arg_count or arg_count > max_arg_count:
                    print(f"Error: invalid number of arguments.")
                    return
                name = args[2]
                try:
                    start_id = int(args[3])
                    process_count = int(args[4])
                except ValueError:
                    print("Error: could not parse arguments as numbers.")
                    return
                match(name):
                    case 'meeting':
                        min_id = MEETING_LOWER_BOUND
                        max_id = MEETING_UPPER_BOUND
                        process_is_duplicate = meeting_process_is_duplicate
                        process_resource = meeting_process_resource
                    case 'body_gd':
                        min_id = BODY_LOWER_BOUND
                        max_id = BODY_UPPER_BOUND
                        print("not yet supported.")
                        return
                    case 'body_bm':
                        min_id = BODY_LOWER_BOUND
                        max_id = BODY_UPPER_BOUND
                        print("Not yet supported.")
                        return
                    case 'document':
                        print("No support yet for downloading documents.")
                        return
                        min_id = DOCUMENT_LOWER_BOUND
                        max_id = DOCUMENT_UPPER_BOUND
                        request_resource = document_request_resource
                        download_is_duplicate = document_download_is_duplicate
                        is_response_success = document_is_response_success
                        generate_filename = document_generate_filename
                    case default:
                        print(f"Unrecognized argument '{name}'.")
                        return
                log=make_log(dir=LOGS_DIR, name=f'{command}_{name}')
                bar: Bar = Bar('Processing', max=process_count)
                conn: Connection = Connection(DATABASE_FILE)
                process_resource = build_process_unique_resource(
                    is_duplicate=process_is_duplicate,
                    process_resource=process_resource,
                    db_connection=conn,
                    bar=bar,
                    log=log,
                    resource_name=name,
                    verbose=False)
                with bar, conn:
                    before = dt.datetime.utcnow().timestamp()
                    results = list(map(process_resource,
                                  range(start_id, start_id+process_count)))
                    elapsed = dt.datetime.utcnow().timestamp() - before
                return
            case('analyze'):
                # execute.py process type start count
                min_arg_count:int = 3
                max_arg_count:int = 3
                if arg_count < min_arg_count or arg_count > max_arg_count:
                    print(f"Error: invalid number of arguments.")
                    return
                name = args[2]
                match(name):
                    case 'meeting':
                        min_id = MEETING_LOWER_BOUND
                        max_id = MEETING_UPPER_BOUND
                    case 'body_gd':
                        min_id = BODY_LOWER_BOUND
                        max_id = BODY_UPPER_BOUND
                        print("not yet supported.")
                        return
                    case 'body_bm':
                        min_id = BODY_LOWER_BOUND
                        max_id = BODY_UPPER_BOUND
                        print("Not yet supported.")
                        return
                    case 'document':
                        print("No support yet for downloading documents.")
                        return
                        min_id = DOCUMENT_LOWER_BOUND
                        max_id = DOCUMENT_UPPER_BOUND
                        request_resource = document_request_resource
                        download_is_duplicate = document_download_is_duplicate
                        is_response_success = document_is_response_success
                        generate_filename = document_generate_filename
                    case default:
                        print(f"Unrecognized argument '{name}'.")
                        return
                counts: list[Tuple[str, int]] = []
                with make_log(LOGS_DIR, 'meeting_analysis') as log, Connection(DATABASE_FILE) as conn:
                    cur = conn.cursor()
                    cur.execute('''SELECT id, form_action FROM raw_meetings''')
                    form_action_count = 0
                    for id, form_action in cur.fetchall():
                        if not id_matches_form_action(id, form_action):
                            message = f'{id} has abnormal form_action: {form_action}'
                            log.write(message+'\n')
                            form_action_count += 1
                    counts.append(('form_action', form_action_count))
                    to_check: list[Tuple[str, Callable[[str], bool]]] = [
                        ('meeting_date', build_is_normal(DATE_PATTERN)),
                        ('meeting_time', build_is_normal(TIME_PATTERN)),
                        ('filing_dt', build_is_normal(DT_PATTERN)),
                        ('agendas', is_document_normal),
                        ('minutes', is_document_normal),
                        ('phone', build_is_normal(PHONE_PATTERN)),
                        ('email', build_is_normal(EMAIL_PATTERN)),
                        ('cancelled_dt', build_is_normal(DT_PATTERN))]
                    for col_name, is_normal in to_check:
                        cur.execute(f'''SELECT id, {col_name} FROM raw_meetings''')
                        count = 0
                        for id, entry in cur.fetchall():
                            if entry and not is_normal(entry):
                                message = f"{id} has abnormal {col_name}: '{entry}'"
                                log.write(message+'\n')
                                count += 1
                        counts.append((col_name, count))
                    for col_name, count in counts:
                        message = f'{col_name}:\t\t{count} abnormal entries'
                        log.write(message+'\n')
                        print(message)
                return
    print("Error: incorrect usage. Try 'analysis.py help'.")
    return
    

if __name__ == '__main__':
    try:
        main(sys.argv)
    except Exception as e:
        print(f"Exception {str(type(e))} while running main:")
        traceback.print_exc()