from io import TextIOWrapper
import sqlite3
import sys
from time import sleep
import traceback
from typing import Callable, Iterable, Iterator, Tuple, Any
from riomp_scrape.objects import AnalysisMeeting
import datetime as dt
from os.path import isfile, isdir, exists
from os import mkdir, listdir
import requests
from requests import Response
import pandas as pd

from riomp_scrape.io_utils import make_dir_if_not_exists_and_check_is_dir, make_log_and_lock
from thread.download import build_download_unique_resource, threaded_download_resource
from thread.process import build_process_unique_resource, threaded_process_resource


# Retry default constants are tailored to maximize request efficiency to the RISOS API without overloading it
TRY_COUNT = 3
TRY_PAUSE: float = 10.0
WORKERS = 1024

DATA_DIR = 'data'
LOGS_DIR = f'{DATA_DIR}/logs'
DOWNLOADS_DIR = f'{DATA_DIR}/downloads'
FEATHERS_DIR = f'{DATA_DIR}/feathers'

def dir_setup():
    make_dir_if_not_exists_and_check_is_dir(DATA_DIR)
    print(DATA_DIR)
    make_dir_if_not_exists_and_check_is_dir(LOGS_DIR)
    print(LOGS_DIR)
    make_dir_if_not_exists_and_check_is_dir(DOWNLOADS_DIR)
    print(DOWNLOADS_DIR)
    make_dir_if_not_exists_and_check_is_dir(FEATHERS_DIR)
    print(FEATHERS_DIR)

def setup_before_each():
    dir_setup()

# Meeting Download Functions

MEETING_DOWNLOADS_DIR: str = f'{DOWNLOADS_DIR}/meetings'
make_dir_if_not_exists_and_check_is_dir(MEETING_DOWNLOADS_DIR)

def meeting_process_is_duplicate(id: int) -> bool:
    return False

def meeting_request_resource(id: int) -> Response:
    url: str = f"https://opengov.sos.ri.gov/OpenMeetingsPublic/ViewMeetingDetailByID?MeetingID={id}"
    return requests.get(url)

def meeting_generate_filename(id: int) -> str:
    return f'{MEETING_DOWNLOADS_DIR}/{id}.html'

def meeting_download_is_duplicate(id: int) -> bool:
    is_in_dir = isfile(meeting_generate_filename(id))
    is_processed = meeting_process_is_duplicate(id)
    return is_in_dir or is_processed

def meeting_is_response_success(response: Response) -> bool:
    code: int = response.status_code
    return 200 <= code and code < 300

# Body GovDirectory Download Functions

BODY_GD_DOWNLOADS_DIR: str = f'{DOWNLOADS_DIR}/bodies_gd'
make_dir_if_not_exists_and_check_is_dir(BODY_GD_DOWNLOADS_DIR)

def body_gd_process_is_duplicate(id: int) -> bool:
    return False

def body_gd_request_resource(id: int) -> Response:
    url: str = f"https://opengov.sos.ri.gov/OpenMeetingsPublic/GovDirectory?subtopmenuID=202&EntityID={id}"
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
    url: str = f"https://opengov.sos.ri.gov/OpenMeetingsPublic/BoardMembers?subtopmenuID=203&EntityID={id}"
    return requests.get(url)

def body_bm_generate_filename(id: int) -> str:
    return f'{BODY_BM_DOWNLOADS_DIR}/{id}.html'

def body_bm_download_is_duplicate(id: int) -> bool:
    is_in_dir = isfile(body_bm_generate_filename(id))
    is_processed = body_bm_process_is_duplicate(id)
    return is_in_dir or is_processed

def body_bm_is_response_success(response: Response) -> bool:
    code: int = response.status_code
    return 200 <= code and code < 300

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

def print_results(
        results: Iterator[Tuple[int, int, int]],
        start_id:int,
        parse_count: int,
        workers: int,
        try_count: int,
        elapsed: float) -> None:
    counts = [0, 0, 0]
    tries: dict[int, int] = dict((i, 0) for i in range (0, try_count+1))
    for _, outcome, count in results:
        counts[outcome] += 1
        tries[count] += 1
    download_count = (counts[0]+counts[2])
    print(f'Download Results:\n'+
    f'\tmax_workers:    {workers}\n'+
    f'\ttime elapsed:   {elapsed}\n'+
    f'\tavg time:       {0 if download_count == 0 else elapsed/download_count}\n'+
    f'\tstart_id:       {start_id}\n'+
    f'\ttotal count:    {parse_count}\n'+
    f'\tdownloaded:     {counts[0]}\n'+
    f'\tduplicates:     {counts[1]}\n'+
    f'\terrors:         {counts[2]}\n'+
    f'\tnonerrors:      {counts[0]+counts[1]}\n'+
    f'\terror rate:     {0 if download_count == 0 else counts[2]/download_count}\n'+
    f'\ttry distribution:\n'+
    ''.join(list((f'\t\t{k}:\t{tries[k]}\n' if tries[k] else '' for k in tries.keys()))))

def main(args):
    setup_before_each()
    arg_count = len(args)
    if arg_count >= 2:
        command: str = args[1]
        match(command):
            case 'help':
                print("Use this script to scrape meetings into the analysis database.\nCommands:\n\tclear : Clears and resets the database\n\ttest (num_threads)? (num_tests)? (start_id)? : tests thread efficiency\n\t\tnum_threads: the numbers of threads to test\n\t\tnum_tests: the number of meetings to test\n\t\tstart_id: the id of the first meeting\n\t(start_id) (num_mtgs) : parses meetings into database\n\t\tstart_id: the id of the first meeting\n\t\tnum_mtgs: the number of meetings to parse")
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
                    parse_count: int = int(args[4])
                    if arg_count >= 6:
                        workers = int(args[5])
                    if arg_count >= 7:
                        try_count = int(args[6])
                    if arg_count >= 8:
                        try_pause = float(args[7])
                except ValueError:
                    print("Error: could not parse arguments as numbers.")
                    return
                match(name):
                    case 'meeting':
                        request_resource = meeting_request_resource
                        download_is_duplicate = meeting_download_is_duplicate
                        is_response_success = meeting_is_response_success
                        generate_filename = meeting_generate_filename
                    case 'body_gd':
                        request_resource = body_gd_request_resource
                        download_is_duplicate = body_gd_download_is_duplicate
                        is_response_success = body_gd_is_response_success
                        generate_filename = body_gd_generate_filename
                    case 'body_bm':
                        request_resource = body_bm_request_resource
                        download_is_duplicate = body_bm_download_is_duplicate
                        is_response_success = body_bm_is_response_success
                        generate_filename = body_bm_generate_filename
                    case 'document':
                        print("No support yet for downloading documents.")
                        return
                        request_resource = document_request_resource
                        download_is_duplicate = document_download_is_duplicate
                        is_response_success = document_is_response_success
                        generate_filename = document_generate_filename
                    case default:
                        print(f"Unrecognized argument '{name}'.")
                        return
                log_and_lock=make_log_and_lock(dir=LOGS_DIR, name=name)
                download_resource = build_download_unique_resource(
                    request_resource,
                    download_is_duplicate,
                    is_response_success,
                    generate_filename,
                    try_count=try_count,
                    try_pause=try_pause,
                    log_and_lock=log_and_lock,
                    resource_name=name,
                    verbose=True)

                before = dt.datetime.utcnow().timestamp()
                results = threaded_download_resource(
                    range(start_id,
                          start_id+parse_count).__iter__(),
                    download_resource,
                    max_workers=workers,
                    log_and_lock=log_and_lock)
                elapsed = dt.datetime.utcnow().timestamp() - before

                if results is None:
                    print('Download failed. Check log for details.')
                else:
                    print_results(
                        results = results,
                        start_id = start_id,
                        parse_count = parse_count,
                        workers = workers,
                        try_count = try_count,
                        elapsed = elapsed)
                log_and_lock[0].close()
                return
            case 'process':
                print('No support yet for processing documents.')
                return
    print("Error: incorrect usage. Try 'analysis.py help'.")
    return
    

if __name__ == '__main__':
    try:
        main(sys.argv)
    except Exception as e:
        print(f"Exception {str(type(e))} while running main:")
        traceback.print_exc()