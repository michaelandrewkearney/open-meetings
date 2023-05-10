import datetime as dt
import json
import sys
import traceback
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
from typing import Callable, Iterator
from progress.bar import Bar
from pymongo import MongoClient
from pymongo.database import Database
from io_utils import make_dir_if_not_exists_and_check_is_dir, make_log_and_lock, threadsafe_write_if_log, get_database, is_in_db, is_tika_server_healthy, is_mongodb_server_healthy
from download import download_meeting, download_body
from parse import parse_meeting, parse_body
from validate import validate_meeting, validate_body, Meeting, Body
from store import store_meeting, store_body, delete
from index import get_meeting_as_indexable, get_body_as_indexable
from resource_type import ResourceType

# Retry default constants are tailored to maximize request efficiency to the RISOS API without overloading it

WORKERS = 1024

MEETING_LOWER_BOUND: int = 724715
MEETING_UPPER_BOUND: int = 1042372
BODY_LOWER_BOUND: int = 1
BODY_UPPER_BOUND: int = 8534

DATA_DIR = 'data'
LOGS_DIR = f'{DATA_DIR}/logs'
OUTPUTS_DIR = f'{DATA_DIR}/outputs'

def setup_dir():
    make_dir_if_not_exists_and_check_is_dir(DATA_DIR)
    make_dir_if_not_exists_and_check_is_dir(LOGS_DIR)
    make_dir_if_not_exists_and_check_is_dir(OUTPUTS_DIR)

def setup_before_each():
    setup_dir()
    assert(is_tika_server_healthy())
    assert(is_mongodb_server_healthy())

def format_test_results(
        results: Iterator[tuple[int, int, int]],
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

def build_process_meeting(db: Database) -> Callable[[int], int]:
    db_lock = Lock()
    def process_meeting(id: int, overwrite: bool = False) -> int:
        collection: str = ResourceType.MEETING.collection_name()
        if is_in_db(db, db_lock, collection, id):
            if overwrite:
                db[collection].delete_one({'_id': id})
            else:
                return -1
        download = download_meeting(id)
        parse = parse_meeting(download)
        validate: Meeting | None = validate_meeting(db, db_lock, parse)
        if validate:
            store_meeting(db, db_lock, id, validate)
            return 0
        return -1
    return process_meeting

def build_process_body(db: Database) -> Callable[[int], int]:
    db_lock = Lock()
    def process_body(id: int, overwrite: bool = False) -> int:
        collection: str = ResourceType.BODY.collection_name()
        if is_in_db(db, db_lock, collection, id):
            if overwrite:
                db[collection].delete_one({'_id': id})
            else:
                return -1
        download = download_body(id)
        parse = parse_body(download['om'], download['gd'], download['bm'])
        validate: Body | None = validate_body(parse)
        if validate:
            store_body(db, db_lock, id, validate)
            return 0
        return 1
    return process_body

def build_export_meeting(db: Database) -> Callable[[int], dict]:
    db_lock = Lock()
    def export_meeting(id: int) -> dict:
        return get_meeting_as_indexable(db, db_lock, id)
    return export_meeting

def build_export_body(db: Database) -> Callable[[int], dict]:
    db_lock = Lock()
    def export_body(id: int) -> dict:
        return get_body_as_indexable(db, db_lock, id)
    return export_body
    
def build_clean(db: Database, db_lock: Lock, rtype: ResourceType, bar: Bar) -> Callable:
    assert(rtype == ResourceType.BODY)
    collection: str = rtype.collection_name()
    def clean(id: int) -> int:
        bar.next()
        if is_in_db(db, db_lock, collection, id):
            if db[collection].find_one({'_id':id})['name'] == '': #type: ignore
                return delete(db, db_lock, collection, id)      
        return 0
    return clean

def print_help():
    print('\nUsage:\n\tpython3 run.py [download|export] [meeting|body] [start_id: int] [count: int]\n')

def main(args):
    setup_before_each()
    arg_count = len(args)
    if arg_count != 5:
        print("Error: incorrect number of arguments.")
        print_help()
        exit(1)
    command: str
    match (args[1]):
        case 'download':
            match (args[2]):
                case 'body':
                    func_builder: Callable[[Database], Callable] = build_process_body
                case 'meeting':
                    func_builder = build_process_meeting
                case default:
                    print(f'Error: resource \'{default}\' not recognized.')
                    print_help()
                    exit(1)
        case 'export':
            match (args[2]):
                case 'body':
                    func_builder = build_export_body
                case 'meeting':
                    func_builder = build_export_meeting
                case default:
                    print(f'Error: resource \'{default}\' not recognized.')
                    print_help()
                    exit(1)
        case default:
            print(f'Error: command \'{default}\' not recognized.')
            print_help()
            exit(1)
    
    try:
        start = int(args[3])
        count = int(args[4])
    except ValueError:
        print("Error: arguments must be parseable integers.")
        print_help()
        exit(1)
    db = get_database()
    func = func_builder(db)
    bar_lock = Lock()
    log_and_lock = make_log_and_lock(LOGS_DIR, f'{args[1]}_{args[2]}')
    with Bar(args[1], max=count) as bar:
        def try_process(i: int) -> int | dict | None:
            result = None
            try:
                result = func(i)
            except Exception as e:
                threadsafe_write_if_log(f'{i}: Exception {e}', log_and_lock, True)
            with bar_lock:
                bar.next()
            return result
        with ThreadPoolExecutor(max_workers=64) as executor:
            results = list(executor.map(try_process, range(start, start+count).__iter__()))
        with open(f'{OUTPUTS_DIR}/output_{dt.datetime.utcnow()}.json', 'w') as output:
            output.write(json.dumps(results))


# def main(args):
#     setup_before_each()
#     arg_count = len(args)
#     if arg_count >= 2:
#         command: str = args[1]
#         match(command):
#             case 'help':
#                 print("Use this script to scrape meetings into the analysis database.\nCommands:\n\tclear : Clears and resets the database\n\ttest (num_threads)? (num_tests)? (start_id)? : tests thread efficiency\n\t\tnum_threads: the numbers of threads to test\n\t\tnum_tests: the number of meetings to test\n\t\tstart_id: the id of the first meeting\n\t(start_id) (num_mtgs) : parses meetings into database\n\t\tstart_id: the id of the first meeting\n\t\tnum_mtgs: the number of meetings to parse")
#                 return
#             case 'test':
#                 min_arg_count:int = 3
#                 max_arg_count:int = 3
#                 if arg_count < min_arg_count or arg_count > max_arg_count:
#                     print(f"Error: invalid number of arguments.")
#                     return
#                 command_to_test: str = args[2]
#                 match(command_to_test):
#                     case 'download':
#                         start_id:int = 1000000
#                         try_count: int = 10
#                         request_resource = meeting_request_resource
#                         download_is_duplicate = lambda id : False
#                         is_response_success = meeting_is_response_success
#                         write_to_file = mock_write_to_file
#                         workers_list = [64, 128, 256, 512, 1024]
#                         try_pause_list = [0.1, 1.0, 5.0, 10.0]
#                         download_count = 1024
#                         outcomes: dict[int, dict[float, str]] = {}
#                         log_and_lock = make_log_and_lock(LOGS_DIR, name=command)
#                         for workers in workers_list:
#                             outcomes[workers] = dict()
#                             for try_pause in try_pause_list:
#                                 print(f'{workers} workers with {try_pause} try_pause')
                                
#                                 bar_and_lock: Tuple[Bar, threading.Lock] = (Bar('Testing', max=download_count), threading.Lock())
                                    
#                                 download_resource = build_download_unique_resource(
#                                     request_resource=request_resource,
#                                     is_duplicate=download_is_duplicate,
#                                     is_response_success=is_response_success,
#                                     write_to_file=write_to_file,
#                                     try_count=try_count,
#                                     try_pause=try_pause,
#                                     resource_name='test',
#                                     bar_and_lock=bar_and_lock,
#                                     log_and_lock=log_and_lock)
#                                 before = dt.datetime.utcnow().timestamp()
#                                 try:
#                                     with bar_and_lock[0]:
#                                         results = threaded_download_resource(
#                                             range(start_id,
#                                                 start_id+download_count).__iter__(),
#                                             download_resource,
#                                             max_workers=workers)
#                                 except Exception as e:
#                                     threadsafe_write_if_log(f'Error: {type(e)}', log_and_lock)
#                                     traceback.print_exc()
#                                     continue
#                                 elapsed = dt.datetime.utcnow().timestamp() - before
#                                 outcomes[workers][try_pause] = format_test_results(results, elapsed)
#                         for workers in workers_list:
#                             for try_pause in try_pause_list:
#                                 print(f'Results for {workers} workers with pause of {try_pause}:')
#                                 print(outcomes[workers][try_pause])
#                         log_and_lock[0].close()
#                         return
#                     case default:
#                         print(f"Unrecognized argument '{command_to_test}'.")
#                         return
#             case 'download':
#                 # execute.py download type start count threads tries pause
#                 min_arg_count:int = 5
#                 max_arg_count:int = 8
#                 if arg_count < min_arg_count or arg_count > max_arg_count:
#                     print(f"Error: invalid number of arguments.")
#                     return
#                 name = args[2]
#                 workers: int = WORKERS
#                 try_count = TRY_COUNT
#                 try_pause = TRY_PAUSE
#                 try:
#                     start_id: int = int(args[3])
#                     download_count: int = int(args[4])
#                     if arg_count >= 6:
#                         workers = int(args[5])
#                     if arg_count >= 7:
#                         try_count = int(args[6])
#                     if arg_count >= 8:
#                         try_pause = float(args[7])
#                 except ValueError:
#                     print("Error: could not parse arguments as numbers.")
#                     return
#                 min_id: int
#                 max_id: int
#                 match(name):
#                     case 'meeting':
#                         min_id = MEETING_LOWER_BOUND
#                         max_id = MEETING_UPPER_BOUND
#                         request_resource = meeting_request_resource
#                         download_is_duplicate = meeting_download_is_duplicate
#                         is_response_success = meeting_is_response_success
#                         generate_filename = meeting_generate_filename
#                     case 'body_gd':
#                         min_id = BODY_LOWER_BOUND
#                         max_id = BODY_UPPER_BOUND
#                         request_resource = body_gd_request_resource
#                         download_is_duplicate = body_gd_download_is_duplicate
#                         is_response_success = body_gd_is_response_success
#                         generate_filename = body_gd_generate_filename
#                     case 'body_bm':
#                         min_id = BODY_LOWER_BOUND
#                         max_id = BODY_UPPER_BOUND
#                         request_resource = body_bm_request_resource
#                         download_is_duplicate = body_bm_download_is_duplicate
#                         is_response_success = body_bm_is_response_success
#                         generate_filename = body_bm_generate_filename
#                     case 'document':
#                         print("No support yet for downloading documents.")
#                         return
#                         min_id = DOCUMENT_LOWER_BOUND
#                         max_id = DOCUMENT_UPPER_BOUND
#                         request_resource = document_request_resource
#                         download_is_duplicate = document_download_is_duplicate
#                         is_response_success = document_is_response_success
#                         generate_filename = document_generate_filename
#                     case default:
#                         print(f"Unrecognized argument '{name}'.")
#                         return
#                 log_and_lock=make_log_and_lock(dir=LOGS_DIR, name=f'{command}_{name}')
#                 write_to_file = build_write_to_file(generate_filename)
#                 bar: Bar = Bar('Downloads', max=download_count)
#                 bar_and_lock = (bar, threading.Lock())
#                 download_resource = build_download_unique_resource(
#                     request_resource=request_resource,
#                     is_duplicate=download_is_duplicate,
#                     is_response_success=is_response_success,
#                     write_to_file=write_to_file,
#                     try_count=try_count,
#                     try_pause=try_pause,
#                     bar_and_lock=bar_and_lock,
#                     log_and_lock=log_and_lock,
#                     resource_name=name,
#                     verbose=False)
#                 try:
#                     with bar:
#                         before = dt.datetime.utcnow().timestamp()
#                         results = threaded_download_resource(
#                             range(start_id,
#                                 start_id+download_count).__iter__(),
#                             download_resource,
#                             max_workers=workers,)
#                         elapsed = dt.datetime.utcnow().timestamp() - before
#                 except Exception as e:
#                     threadsafe_write_if_log(f'Error: {type(e)}', log_and_lock)
#                     return

#                 print(format_results(
#                     results = results,
#                     start_id = start_id,
#                     parse_count = download_count,
#                     workers = workers,
#                     try_count = try_count,
#                     elapsed = elapsed))
#                 log_and_lock[0].close()
#                 return
#             case 'process':
#                 # execute.py process type start count
#                 min_arg_count:int = 5
#                 max_arg_count:int = 5
#                 if arg_count < min_arg_count or arg_count > max_arg_count:
#                     print(f"Error: invalid number of arguments.")
#                     return
#                 name = args[2]
#                 try:
#                     start_id = int(args[3])
#                     process_count = int(args[4])
#                 except ValueError:
#                     print("Error: could not parse arguments as numbers.")
#                     return
#                 match(name):
#                     case 'meeting':
#                         min_id = MEETING_LOWER_BOUND
#                         max_id = MEETING_UPPER_BOUND
#                         process_is_duplicate = meeting_process_is_duplicate
#                         process_resource = meeting_process_resource
#                     case 'body_gd':
#                         min_id = BODY_LOWER_BOUND
#                         max_id = BODY_UPPER_BOUND
#                         print("not yet supported.")
#                         return
#                     case 'body_bm':
#                         min_id = BODY_LOWER_BOUND
#                         max_id = BODY_UPPER_BOUND
#                         print("Not yet supported.")
#                         return
#                     case 'document':
#                         print("No support yet for downloading documents.")
#                         return
#                         min_id = DOCUMENT_LOWER_BOUND
#                         max_id = DOCUMENT_UPPER_BOUND
#                         request_resource = document_request_resource
#                         download_is_duplicate = document_download_is_duplicate
#                         is_response_success = document_is_response_success
#                         generate_filename = document_generate_filename
#                     case default:
#                         print(f"Unrecognized argument '{name}'.")
#                         return
#                 log=make_log(dir=LOGS_DIR, name=f'{command}_{name}')
#                 bar: Bar = Bar('Processing', max=process_count)
#                 conn: Connection = Connection(DATABASE_FILE)
#                 process_resource = build_process_unique_resource(
#                     is_duplicate=process_is_duplicate,
#                     process_resource=process_resource,
#                     db_connection=conn,
#                     bar=bar,
#                     log=log,
#                     resource_name=name,
#                     verbose=False)
#                 with bar, conn:
#                     before = dt.datetime.utcnow().timestamp()
#                     results = list(map(process_resource,
#                                   range(start_id, start_id+process_count)))
#                     elapsed = dt.datetime.utcnow().timestamp() - before
#                 return
#             case('analyze'):
#                 # execute.py process type start count
#                 min_arg_count:int = 3
#                 max_arg_count:int = 3
#                 if arg_count < min_arg_count or arg_count > max_arg_count:
#                     print(f"Error: invalid number of arguments.")
#                     return
#                 name = args[2]
#                 match(name):
#                     case 'meeting':
#                         min_id = MEETING_LOWER_BOUND
#                         max_id = MEETING_UPPER_BOUND
#                     case 'body_gd':
#                         min_id = BODY_LOWER_BOUND
#                         max_id = BODY_UPPER_BOUND
#                         print("not yet supported.")
#                         return
#                     case 'body_bm':
#                         min_id = BODY_LOWER_BOUND
#                         max_id = BODY_UPPER_BOUND
#                         print("Not yet supported.")
#                         return
#                     case 'document':
#                         print("No support yet for downloading documents.")
#                         return
#                         min_id = DOCUMENT_LOWER_BOUND
#                         max_id = DOCUMENT_UPPER_BOUND
#                         request_resource = document_request_resource
#                         download_is_duplicate = document_download_is_duplicate
#                         is_response_success = document_is_response_success
#                         generate_filename = document_generate_filename
#                     case default:
#                         print(f"Unrecognized argument '{name}'.")
#                         return
#                 counts: list[Tuple[str, int]] = []
#                 with make_log(LOGS_DIR, 'meeting_analysis') as log, Connection(DATABASE_FILE) as conn:
#                     cur = conn.cursor()
#                     cur.execute('''SELECT id, form_action FROM raw_meetings''')
#                     form_action_count = 0
#                     for id, form_action in cur.fetchall():
#                         if not id_matches_form_action(id, form_action):
#                             message = f'{id} has abnormal form_action: {form_action}'
#                             log.write(message+'\n')
#                             form_action_count += 1
#                     counts.append(('form_action', form_action_count))
#                     to_check: list[Tuple[str, Callable[[str], bool]]] = [
#                         ('meeting_date', build_is_normal(DATE_PATTERN)),
#                         ('meeting_time', build_is_normal(TIME_PATTERN)),
#                         ('filing_dt', build_is_normal(DT_PATTERN)),
#                         ('agendas', is_document_normal),
#                         ('minutes', is_document_normal),
#                         ('phone', build_is_normal(PHONE_PATTERN)),
#                         ('email', build_is_normal(EMAIL_PATTERN)),
#                         ('cancelled_dt', build_is_normal(DT_PATTERN))]
#                     for col_name, is_normal in to_check:
#                         cur.execute(f'''SELECT id, {col_name} FROM raw_meetings''')
#                         count = 0
#                         for id, entry in cur.fetchall():
#                             if entry and not is_normal(entry):
#                                 message = f"{id} has abnormal {col_name}: '{entry}'"
#                                 log.write(message+'\n')
#                                 count += 1
#                         counts.append((col_name, count))
#                     for col_name, count in counts:
#                         message = f'{col_name}:\t\t{count} abnormal entries'
#                         log.write(message+'\n')
#                         print(message)
#                 return
#     print("Error: incorrect usage. Try 'analysis.py help'.")
#     return


if __name__ == '__main__':
    try:
        main(sys.argv)
    except Exception as e:
        print(f"Exception {str(type(e))} while running main:")
        traceback.print_exc()