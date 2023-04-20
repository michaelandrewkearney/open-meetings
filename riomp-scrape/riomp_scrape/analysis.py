from io import TextIOWrapper
import sqlite3
import sys
from time import sleep
import traceback
from typing import Iterable, Iterator, Tuple
from riomp_scrape.objects import AnalysisMeeting
from riomp_scrape.utils import get_meeting_details_page
from riomp_scrape.meeting import parse_analysis_meeting
import datetime as dt
import threading
from concurrent.futures import ThreadPoolExecutor
from os.path import isfile

ANALYSIS_DB_PATH = 'data/analysis.db'
LOG: TextIOWrapper = open(f"data/log_{str(dt.datetime.utcnow()).replace(' ', '_')}.txt", 'x')

# LOWER_BOUND: int = 700000
# UPPER_BOUND: int = 1130000
RETRY_COUNT = 100
RETRY_PAUSE = 10
WORKERS = 1024

START_TEST_ID = 900000
TEST_COUNT = 1000
TEST_WORKERS = 1024

MTGS: dict[int, AnalysisMeeting] = dict()

log_lock = threading.Lock()

def clear():
    if not isfile(ANALYSIS_DB_PATH):
        open(ANALYSIS_DB_PATH, 'x').close()
    conn: sqlite3.Connection = sqlite3.connect(ANALYSIS_DB_PATH)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS "meetings";')
    c.execute('''
        CREATE TABLE meetings
        (id INT PRIMARY KEY NOT NULL,
        form_action TEXT,
        body TEXT,
        meeting_date TEXT,
        meeting_time TEXT,
        meeting_address TEXT,
        filing_dt TEXT,
        is_emergency TEXT,
        is_annual_calendar TEXT,
        is_public_notice TEXT,
        agendas TEXT,
        minutes TEXT,
        contact_person TEXT,
        phone TEXT,
        email TEXT,
        is_meeting_date_changed TEXT,
        is_meeting_time_changed TEXT,
        is_address_changed TEXT,
        is_annual_calendar_changed TEXT,
        is_emergency_changed TEXT,
        is_public_notice_changed TEXT,
        is_agenda_changed TEXT,
        is_emergency_flag TEXT,
        is_annual_flag TEXT,
        is_public_notice_flag TEXT,
        is_cancelled TEXT,
        cancelled_dt TEXT,
        cancelled_reason TEXT)
    ''')
    c.execute('DROP TABLE IF EXISTS "nonmeetings";')
    c.execute('''
        CREATE TABLE nonmeetings
        (id INT PRIMARY KEY NOT NULL)''')
    c.execute('DROP TABLE IF EXISTS "unknownmeetings";')
    c.execute('''
        CREATE TABLE unknownmeetings
        (id INT PRIMARY KEY NOT NULL)''')
    conn.commit()
    c.close()
    conn.close()

def resilient_get_meeting_details_page(id: int) -> str:
    count: int = 0
    while count < RETRY_COUNT:
        try:
            text: str = get_meeting_details_page(id)
            return text
        except:
            count += 1
            sleep(RETRY_PAUSE)
    raise Exception(f"Tried getting meeting {id} details 10 times and failed.")

# 0 = id has associated meeting
# 1 = id has no associated meeting
# 2 = id association is unknown
def append_meeting(id: int) -> Tuple[int, int]:
    try:
        text = resilient_get_meeting_details_page(id)
        mtg: AnalysisMeeting = parse_analysis_meeting(text)
        if mtg.is_real_meeting():
            MTGS[id] = mtg
            return (0, id)
        return (1, id)
    except Exception:
        with log_lock:
            LOG.write(f"{id}: Could not parse meeting {id}:\n")
            traceback.print_exc(file=LOG)
        return (2, id)

def scrape_mtgs_threaded(ids: Iterator[int], max_workers):
    print(f'Parsing meetings...')
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        try:
            results = executor.map(append_meeting,    
                        ids,
                        timeout = 60)
        except:
            with log_lock:
                LOG.write(f"Threading Error:\n")
                traceback.print_exc(file=LOG)
                LOG.close()
                exit(1)
    print('Meetings parsed.')
    return results

def write_results_to_database(ids: Iterator[Tuple[int, int]]) -> list[int]:
    print('Writing meetings...')
    conn: sqlite3.Connection = sqlite3.connect(ANALYSIS_DB_PATH)
    c = conn.cursor()
    meeting_count: int = 0
    nonmeeting_count: int = 0
    unknownmeeting_count: int = 0
    for outcome, id in ids:
        if outcome == 0:
            # add real meeting
            try:
                mtg = MTGS[id]
                c.execute('''INSERT INTO meetings VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''',(
                (id,
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
                mtg.cancelled_reason)
                ))
                meeting_count += 1
            except:
                with log_lock:
                    LOG.write(f"Error writing meeting {id} to database:")
                    traceback.print_exc(file=LOG)
        elif outcome == 1:
            # add non meeting
            try:
                c.execute(f'''INSERT INTO nonmeetings VALUES ({id});''')
                nonmeeting_count += 1
                print(nonmeeting_count)
            except:
                with log_lock:
                    LOG.write(f"Error writing nonmeeting {id} to database:")
                    traceback.print_exc(file=LOG)
        else:
            # add unknown meeting
            try:
                c.execute(f'''INSERT INTO unknownmeetings VALUES ({id});''')
                unknownmeeting_count += 1
            except:
                with log_lock:
                    LOG.write(f"Error writing unknown meeting {id} to database:")
                    traceback.print_exc(file=LOG)
    conn.commit()
    c.close()
    conn.close()
    print('Meetings written.')
    return [meeting_count, nonmeeting_count, unknownmeeting_count]

def int_pkey_to_set(keylist: list[Tuple[int, None]]) -> set[int]:
    keys: set[int] = set()
    for key in keylist:
        keys.add(key[0])
    return keys

# Generates a set of meeting_id ints in the given range that have not already been parsed into the database
def get_ungotten_meetings(from_id: int, parse_count: int):
    conn: sqlite3.Connection = sqlite3.connect(ANALYSIS_DB_PATH)
    c = conn.cursor()
    meetings = set()
    meetings = meetings.union(
        int_pkey_to_set(c.execute('''SELECT id FROM meetings''').fetchall()),
        int_pkey_to_set(c.execute('''SELECT id FROM nonmeetings''').fetchall()))
    c.close()
    conn.close()
    return set(range(from_id, from_id + parse_count)) - meetings

def main(args):
    arg_count = len(args)
    if arg_count >= 2:
        match(args[1]):
            case 'help':
                print("Use this script to scrape meetings into the analysis database.\nCommands:\n\tclear : Clears and resets the database\n\ttest (num_threads)? (num_tests)? (start_id)? : tests thread efficiency\n\t\tnum_threads: the numbers of threads to test\n\t\tnum_tests: the number of meetings to test\n\t\tstart_id: the id of the first meeting\n\t(start_id) (num_mtgs) : parses meetings into database\n\t\tstart_id: the id of the first meeting\n\t\tnum_mtgs: the number of meetings to parse")
                return
            case 'clear':
                clear()
                print("Database reinitialized.")
                return
            case 'test':
                workers: int = TEST_WORKERS
                start_id: int = START_TEST_ID
                test_count: int = TEST_COUNT
                try:
                    if arg_count == 3 or arg_count == 4 or arg_count == 5: 
                        workers = int(args[2])
                    if arg_count == 4 or arg_count == 5:
                        test_count = int(args[3])
                    if arg_count == 5:
                        start_id = int(args[4])
                except ValueError:
                        print("Arguments passed to 'test' command must be ints.")
                        return
                before = dt.datetime.utcnow().timestamp()
                results = scrape_mtgs_threaded(
                    range(start_id, start_id+test_count).__iter__(),
                    max_workers=workers)
                elapsed = dt.datetime.utcnow().timestamp() - before
                counts = [0, 0, 0]
                for outcome, id in results:
                    counts[outcome] += 1
                print(f'''Test Results:
                max_workers:        {workers}
                time elapsed:       {elapsed}
                avg time per parse: {elapsed/test_count}
                start_id:           {start_id}
                test_count:         {test_count}
                real mtgs parsed:   {counts[0]}
                non-mtgs parsed:    {counts[1]}
                total mtgs parsed:  {counts[0] + counts[1]}
                error count:        {counts[2]}''')
                return
        if arg_count == 3 or arg_count == 4:
            try:
                start_id: int = int(args[1])
                parse_count: int = int(args[2])
            except ValueError:
                print("Arguments passed to scraper must be ints.")
                return
            workers: int = WORKERS
            if arg_count == 4:
                try:
                    workers = int(args[3])
                except ValueError:
                    print("Arguments passed to scraper must be ints.")
                    return
            ids = get_ungotten_meetings(start_id, parse_count).__iter__()
            before: float = dt.datetime.utcnow().timestamp()
            results = scrape_mtgs_threaded(ids, workers)
            after_parse: float = dt.datetime.utcnow().timestamp()
            counts = write_results_to_database(results)
            after_write: float = dt.datetime.utcnow().timestamp()
            parse_elapsed: float = after_parse-before
            print(f'''Parse results:
                max_workers:        {workers}
                parse time elapsed: {parse_elapsed}
                avg time per parse: {parse_elapsed/parse_count}
                write time elapsed: {after_write-after_parse}
                start_id:           {start_id}
                parse_count:        {sum(1 for _ in ids)}
                real mtgs parsed:   {counts[0]}
                non-mtgs parsed:    {counts[1]}
                total mtgs parsed:  {counts[0] + counts[1]}
                error count:        {counts[2]}\n''')
            return
    print("Error: incorrect arguments. Try 'analysis.py help'.")
    return
    

if __name__ == '__main__':
    try:
        main(sys.argv)
    except:
        print("Something went wrong. Have you initialized the database by running 'analysis.py clear'?")
    LOG.close()