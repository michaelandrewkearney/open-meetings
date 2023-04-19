from io import TextIOWrapper
import sqlite3
import sys
from time import sleep
import traceback
from riomp_scrape.objects import AnalysisMeeting
from riomp_scrape.utils import get_meeting_details_page
from riomp_scrape.meeting import parse_analysis_meeting
import datetime as dt
import threading
from concurrent.futures import ThreadPoolExecutor

ANALYSIS_DB_PATH = 'data/analysis.db'
LOG: TextIOWrapper = open(f"data/log_{str(dt.datetime.utcnow()).replace(' ', '_')}.txt", 'x')

LOWER_BOUND: int = 700000
UPPER_BOUND: int = 1130000

MTGS: list[AnalysisMeeting] = list()
NONMTGS: list[int] = list()
DUPLICATES: list[int] = list()

log_lock = threading.Lock()

def clear():
    conn: sqlite3.Connection = sqlite3.connect(ANALYSIS_DB_PATH)
    c = conn.cursor()
    c.execute('DROP TABLE IF EXISTS "meetings";')
    c.execute('''
        CREATE TABLE meetings
        (id INT PRIMARY KEY NOT NULL,
        is_meeting INT,
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
    conn.commit()
    c.close()
    conn.close()

def insert_mtgs_into_db():
    conn: sqlite3.Connection = sqlite3.connect(ANALYSIS_DB_PATH)
    c = conn.cursor()
    for mtg in MTGS:
        try:
            c.execute('''INSERT INTO meetings VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''',(
                    (mtg.id,
                    1,
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
        except sqlite3.IntegrityError:
            DUPLICATES.append(mtg.id)
        except:
            with log_lock:
                LOG.write(f"Error writing meeting {mtg.id} to database:")
                traceback.print_exc(file=LOG)
    for nonid in NONMTGS:
        try:
            c.execute(f'''INSERT INTO nonmeetings VALUES ({nonid});''')
        except sqlite3.IntegrityError:
            DUPLICATES.append(nonid)
        except:
            with log_lock:
                LOG.write(f"Error writing nonmeeting {nonid} to database:")
                traceback.print_exc(file=LOG)
    conn.commit()
    c.close()
    conn.close()
    MTGS.clear()
    NONMTGS.clear()

def tear_down():
    LOG.close()

def get_meeting_details(id: int) -> str:
    count: int = 0
    while count < 10:
        try:
            text: str = get_meeting_details_page(id)
            return text
        except:
            sleep(0.01)
    raise Exception(f"Tried getting meeting {id} details 10 times and failed.")

def append_analysis_meeting(id: int):
    try:
        text = get_meeting_details(id)
        mtg: AnalysisMeeting = parse_analysis_meeting(text)
        mtg.id = id
        if mtg.is_real_meeting():
            MTGS.append(mtg)
        else:
            NONMTGS.append(id)
    except Exception:
        with log_lock:
            LOG.write(f"{id}: Could not parse meeting {id}:\n")
            traceback.print_exc(file=LOG)

def run_threads(id_range: range, max_workers: int = 4096):
    print(f'Parsing {len(id_range)} meetings...')
    try:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            executor.map(append_analysis_meeting,    
                                id_range,
                                timeout = 60)
    except:
        with log_lock:
            LOG.write(f"Threading Error:\n")
            traceback.print_exc(file=LOG)
    print(f'Parsed {len(MTGS)} out of {len(MTGS)+len(NONMTGS)} meetings, of which {len(DUPLICATES)} were duplicates.')
    insert_mtgs_into_db()
    print(f'Meetings added to database.')

def get_ungotten_meetings(from_id: int, to_id: int):
    conn: sqlite3.Connection = sqlite3.connect(ANALYSIS_DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT id FROM meetings OUTERJOIN nonmeetings''')

def main(args):

    start_test_id = 1030000
    test_count = 5000
    from_id: int
    to_id: int
    if len(args) == 2:
        if args[1].lower() == 'help':
            print("Use this script to add an analysis meeting to the analysis database.\n\tMeeting range is inclusive.\n\tThis script takes one or two arguments as follows:\n\n\t\tanalysis.py < 'help' | mtg_id:int | (from_mtg_id:int to_mtg_id:int) >\n\n")
            return
        if args[1].lower() == 'test':
            print('Testing speed against number of worker threads...')
            for i in range(1, 10):
                before = dt.datetime.utcnow().timestamp()
                run_threads(range(start_test_id, start_test_id+test_count), max_workers=i)
                after = dt.datetime.utcnow().timestamp()
                print(f"{i} thread{'s' if i != 1 else ' '} took {after-before} seconds.\n")
            tear_down()
            return
        if args[1].lower() == 'clear':
            print('Clearing database...')
            clear()
            print('Database cleared.')
            return
        try:
            id: int = int(args[1])
        except ValueError:
            print("Error: argument must be parseable int.")
            return
        from_id = id
        to_id = id + 1
    elif len(args) == 3:
        if args[1].lower() == 'test':
            try:
                threads: int = int(args[2])
            except:
                print("Error: must pass int parseable argument with test.")
                return
            print(f'Testing speed for {threads} threads...')
            before = dt.datetime.utcnow().timestamp()
            run_threads(range(start_test_id, start_test_id+test_count), max_workers=threads)
            after = dt.datetime.utcnow().timestamp()
            print(f"{threads} thread{'s' if threads != 1 else ' '} took {after-before} seconds.\n")
            tear_down()
            return
        try:
            from_id: int = int(args[1])
            to_id: int = int(args[2])
        except ValueError:
            print("Error: arguments must be parseable ints.")
            return
        if from_id > to_id:
            print("Error: from_mtg_id cannot be greater than to_mtg_id.")
            return
    else:
        print("Error: wrong number of arguments. Try 'analysis.py help'.")
        return
    run_threads(range(from_id, to_id))
    tear_down()
    

if __name__ == '__main__':
    main(sys.argv)