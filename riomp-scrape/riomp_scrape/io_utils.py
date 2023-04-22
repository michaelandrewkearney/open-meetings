from  os import mkdir
from os.path import exists, isdir, isfile
from io import TextIOWrapper
import threading
from typing import Tuple, Callable
import datetime as dt
import traceback

add_event: Callable[[str, str], str] = lambda event, log : log + f'\t{dt.datetime.utcnow()}: {event}\n'

def make_dir_if_not_exists_and_check_is_dir(dir: str) -> None:
    if not exists(dir):
        mkdir(dir)
    elif not isdir(dir):
        raise IOError(f'Cannot create dir {dir} in package: {dir} exists but is not a directory.')

def make_file_if_not_exists_and_check_is_file(file: str) -> None:
    if not exists(file):
        open(file, 'x').close()
    elif not isfile(file):
        raise IOError(f'Cannot create file {file}: {file} exists but is not a file.')

def make_log(dir: str, name:str = '') -> TextIOWrapper:
    """
    Safely makes a timestamped log file without overwriting
    
    :param dir: the directory in which to create the log
    :param name: optional descriptor to add the the log filename
    """
    if not isdir(dir):
        raise IOError(f"'{dir}' is not a directory.")
    log_base_name = f"{dir}/log_{name+'_' if name else name}{str(dt.datetime.utcnow()).replace(' ', '_')}"
    count: int = 0
    log_name = f'{log_base_name}.txt'
    while exists(log_name):
        count += 1
        log_name = f'{log_base_name}_{count}.txt'
    return open(log_name, 'x')

def make_log_and_lock(dir: str, name:str='') -> Tuple[TextIOWrapper, threading.Lock]:
    """
    Safely makes and packages a log file and thread lock on it
    
    :param dir: the directory in which to create the log
    :param name: optional descriptor to add the the log filename
    """
    return (make_log(dir, name), threading.Lock())

def threadsafe_write_if_log(to_write: str, log_and_lock: Tuple[TextIOWrapper, threading.Lock] | None, write_traceback: bool = False):
    if log_and_lock is not None:
        with log_and_lock[1]:
            log_and_lock[0].write(to_write)
            if write_traceback:
                traceback.print_exc(file=log_and_lock[0])