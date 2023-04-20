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
import requests

LOG: TextIOWrapper = open(f"data/log_{str(dt.datetime.utcnow()).replace(' ', '_')}.txt", 'x')

# LOWER_BOUND: int = 700000
# UPPER_BOUND: int = 1130000

# Retry constants are tailored to maximize request efficiency to the RISOS API without overloading it
RETRY_COUNT = 10
RETRY_PAUSE = 10
WORKERS = 1024

START_TEST_ID = 900000
TEST_COUNT = 1000
TEST_WORKERS = 1024

log_lock = threading.Lock()

# 0 success
# 1 duplicate
# 2 error
def download_meeting_details(id: int) -> Tuple[int, int, int]:
    count: int = 0
    r = None
    log = ''
    filename: str = f'pages/{id}.html'
    if isfile(filename):
        log += f'\t{dt.datetime.utcnow()}: Meeting {id} is already downloaded.\n'
        with log_lock:
            LOG.write(f'\nReport for Meeting ID {id}:\n' + log)
        return (id, 1, count)
    url: str = 'https://opengov.sos.ri.gov/OpenMeetingsPublic/ViewMeetingDetailByID?MeetingID='+ str(id)
    while count < RETRY_COUNT:
        count += 1
        try:
            before = dt.datetime.utcnow().timestamp()
            r = requests.get(url)
            elapsed = dt.datetime.utcnow().timestamp() - before
            if r.status_code != 200:
                log += f'\t{dt.datetime.utcnow()}: Request #{count} returned with status code {r.status_code} in {elapsed} seconds. Retrying...\n'
                continue
            log += f'\t{dt.datetime.utcnow()}: Request successful in {elapsed} seconds.\n'
            break
        except Exception as e:
            log += f'\t{dt.datetime.utcnow()}: Request #{count} raised {str(type(e))}. Retrying...\n'
            sleep(RETRY_PAUSE)
    if r is None or r.status_code != 200:
        log += f'\t{dt.datetime.utcnow()}: Could not complete request after {count} retries.\n'
        with log_lock:
            LOG.write(f'\nReport for Meeting ID {id}:\n' + log)
        return (id, 2, count)
    try:
        with open(filename, 'xb') as f:
            for chunk in r.iter_content(chunk_size=128):
                f.write(chunk)
        log += f'\t{dt.datetime.utcnow()}: Meeting successfully written.\n'
        with log_lock:
            LOG.write(f'\nReport for Meeting {id}:\n' + log)
        return (id, 0, count)
    except FileExistsError:
        log += f'\t{dt.datetime.utcnow()}: Meeting is already downloaded.\n'
        with log_lock:
            LOG.write(f'\nReport for Meeting {id}:\n' + log)
        return (id, 1, count)
    except Exception as e:
        log += f"\t{dt.datetime.utcnow()}: Could not create file '{filename}' due to {str(type(e))}.\n"
        with log_lock:
            LOG.write(f'\nReport for Meeting {id}:\n' + log)
        return (id, 2, count)
    

def scrape_mtgs_threaded(ids: Iterator[int], max_workers):
    print(f'Downloading meetings...')
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        try:
            return executor.map(download_meeting_details,    
                        ids,
                        timeout = 60)
        except Exception as e:
            with log_lock:
                LOG.write(f"Exception {str(type(e))}:\n")
                traceback.print_exc(file=LOG)

def main(args):
    arg_count = len(args)
    if arg_count >= 2:
        match(args[1]):
            case 'help':
                print("Use this script to scrape meetings into the analysis database.\nCommands:\n\tclear : Clears and resets the database\n\ttest (num_threads)? (num_tests)? (start_id)? : tests thread efficiency\n\t\tnum_threads: the numbers of threads to test\n\t\tnum_tests: the number of meetings to test\n\t\tstart_id: the id of the first meeting\n\t(start_id) (num_mtgs) : parses meetings into database\n\t\tstart_id: the id of the first meeting\n\t\tnum_mtgs: the number of meetings to parse")
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
                if results is None:
                    print('Test failed. Check log for details.')
                    return
                counts = [0, 0, 0]
                for _, outcome, count in results:
                    counts[outcome] += 1
                print(f'Test Results:\n'+
                f'\tmax_workers:    {workers}\n'+
                f'\ttime elapsed:   {elapsed}\n'+
                f'\tavg time:       {elapsed/test_count}\n'+
                f'\tstart_id:       {start_id}\n'+
                f'\ttest_count:     {test_count}\n'+
                f'\tdownloaded:     {counts[0]}\n'+
                f'\tduplicates:     {counts[1]}\n'+
                f'\terrors:         {counts[2]}\n'+
                f'\ttotal tried:    {counts[0] + counts[1]}\n'+
                f'\terror rate:     {counts[1]/(counts[0]+counts[1])}')
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
            before = dt.datetime.utcnow().timestamp()
            results = scrape_mtgs_threaded(
                range(start_id, start_id+parse_count).__iter__(),
                max_workers=workers)
            elapsed = dt.datetime.utcnow().timestamp() - before
            if results is None:
                print('Download failed. Check log for details.')
                return
            counts = [0, 0, 0]
            tries: dict[int, int] = dict((i, 0) for i in range (0, RETRY_COUNT+1))
            for _, outcome, count in results:
                counts[outcome] += 1
                tries[count] += 1
            print(f'Download Results:\n'+
            f'\tmax_workers:    {workers}\n'+
            f'\ttime elapsed:   {elapsed}\n'+
            f'\tavg time:       {elapsed/(counts[0]+counts[1])}\n'+
            f'\tstart_id:       {start_id}\n'+
            f'\tcount:          {parse_count}\n'+
            f'\tdownloaded:     {counts[0]}\n'+
            f'\tduplicates:     {counts[1]}\n'+
            f'\tnonerrors:      {counts[0]+counts[1]}\n'+
            f'\terrors:         {counts[2]}\n'+
            f'\terror rate:     {counts[2]/(counts[0]+counts[1]+counts[2])}\n'+
            f'\ttry distribution:\n'+
            ''.join(list((f'\t\t{k}:\t{tries[k]}\n' if tries[k] else '' for k in tries.keys()))))
            return
    print("Error: incorrect arguments. Try 'analysis.py help'.")
    return
    

if __name__ == '__main__':
    try:
        main(sys.argv)
    except Exception as e:
        print(f"Exception {str(type(e))} while running main.")
        with log_lock:
            LOG.write(f"Exception {str(type(e))}:\n")
            traceback.print_exc(file=LOG)
    LOG.close()