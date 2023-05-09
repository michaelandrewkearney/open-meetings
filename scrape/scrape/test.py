from typing import Callable
import sqlite3
from sqlite3 import Connection
from validate import build_is_normal, FORM_ACTION_PATTERN, DATE_PATTERN, TIME_PATTERN, DT_PATTERN, YES_NO_PATTERN, INT_FLAG_PATTERN, is_document_normal

DATABASE_FILE = 'data/database.db'

raw_meeting_validators: list[tuple[str, Callable[[str], bool]]] = [
    ('form_action', build_is_normal(FORM_ACTION_PATTERN)),
    ('meeting_date', build_is_normal(DATE_PATTERN)),
    ('meeting_time', build_is_normal(TIME_PATTERN)),
    ('filing_dt', build_is_normal(DT_PATTERN)),
    ('is_emergency', build_is_normal(YES_NO_PATTERN)),
    ('is_annual_calendar', build_is_normal(YES_NO_PATTERN)),
    ('is_public_notice', build_is_normal(YES_NO_PATTERN)),
    ('agendas', is_document_normal),
    ('minutes', is_document_normal),
    ('is_cancelled', build_is_normal(INT_FLAG_PATTERN)),
    ('cancelled_dt', build_is_normal(DT_PATTERN))
]

def validate_raw_meeting_data():
    conn: Connection = Connection(DATABASE_FILE)
    c = conn.cursor()
    for column, is_normal in raw_meeting_validators:
        success = 0
        count = 0
        c.execute(f'''SELECT {column} FROM raw_meetings''')
        items = c.fetchall()
        for item, in items:
            if item:
                count += 1
                try:
                    assert(is_normal(item))
                    success += 1
                except Exception as e:
                    print(column + ": '" + item + "' of length " + str(len(item)))
                    raise e
        print(f'{success} of {count} ({success/count*100}%) of entries in column {column} are normal.')

validate_raw_meeting_data()