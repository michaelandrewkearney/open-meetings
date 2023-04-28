from concurrent.futures import ThreadPoolExecutor
import traceback
from typing import Callable, Tuple, Iterator
import threading
from io import TextIOWrapper
from riomp_scrape.io_utils import threadsafe_write_if_log, add_event
import pandas as pd
from progress.bar import Bar
from sqlite3 import Connection

def build_process_unique_resource(
    is_duplicate: Callable[[int, Connection], bool],
    process_resource: Callable[[int, Connection], None],
    db_connection: Connection,
    bar: Bar | None,
    log: TextIOWrapper | None,
    verbose: bool = False,
    resource_name:str = 'resource'
    ) -> Callable[[int], Tuple[int, int]]:
    """
    Construct a function to download a resource
    
    :param get_local_resource: gets local resource with unique identifier
    :param is_duplicate: if resource was already processed
    :param process_resource: processes the resource
    :param log_and_lock: the file and thread lock on it to write the log to
    :param verbose: if true, also writes non-error downloads to log.
    :param resource_name: short name of the resource type, e.g. 'meeting'
    """
    def process_unique_resource(id: int) -> Tuple[int, int]:
        """
        Downloads a a unique resource.

        :param id: a unique identifier for the resource
        :return: (id, outcome) where
                    id: id of resource
                    outcome: 0=success, 1=duplicate, 2=error
        """
        log_header = f'\nDownload report for {resource_name} {id}:\n'
        running_log: str = ''

        def before_return(is_error: bool):
            if log and (verbose or is_error):
                log.write(log_header + running_log)
            if bar:
                bar.next()

        # Check if resource was already processed
        if is_duplicate(id, db_connection):
            running_log = add_event(f"{resource_name} {id} is duplicate.", running_log)
            before_return(True)
            return (id, 1)
        try:
            process_resource(id, db_connection)
        except Exception as e:
            running_log = add_event(f"Error processing {resource_name} {id}: exception {str(type(e))} occurred:", running_log)
            before_return(True)
            return(id, 2)
        running_log = add_event(f"{resource_name} {id} processed.", running_log)
        before_return(True)
        return (id, 0)
    return process_unique_resource

def build_file_to_dataframe(
        id_to_filename: Callable[[int], str],
        file_to_row: Callable[[str], pd.Series],
        df: pd.DataFrame,
        ) -> Callable[[int], int]:
    
    def file_to_dataframe(id: int) -> int:
        if id in df.index:
            raise IndexError(f"Index {id} already in dataframe.")
        try:
            filename = id_to_filename(id)
            row: pd.Series = file_to_row(filename)
            df.loc[id] = row # type: ignore
            return 0
        except Exception as e:
            return 2
    return file_to_dataframe

def threaded_process_resource(
    ids: Iterator[int],
    process_resource: Callable[[int], Tuple[int, int]],
    max_workers: int,
    log_and_lock: Tuple[TextIOWrapper, threading.Lock] | None = None
    ) -> Iterator[Tuple[int, int]]:
    """
    Processes resources in a multi-threaded way

    :param ids: unique ids to process
    :param process_resource: processes a unique resource
    :param max_workers: maximum number of threads to use
    :param log_and_lock: the file and thread lock on it to write the log to
    :return: 
    """
    print(f'Processing...')
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        try:
            return executor.map(process_resource, ids)
        except Exception as e:
            traceback.print_exc()
            if log_and_lock is not None:
                with log_and_lock[1]:
                    log_and_lock[0].write(f"Exception {str(type(e))}:\n")
                    traceback.print_exc(file=log_and_lock[0])
        return list().__iter__()