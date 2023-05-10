from  os import mkdir
from os.path import exists, isdir, isfile
from io import TextIOWrapper
import threading
from typing import Tuple, Callable
import datetime as dt
import traceback
from requests import Response, get
from pymongo import MongoClient
from pymongo.database import Database
from constants import TIKA_SERVER, MONGODB_SERVER
from resource_type import ResourceType
from threading import Lock

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

def is_http_success(response: Response) -> bool:
    code = response.status_code
    if code > 299:
        return False
    if code < 200:
        return False
    return True

def is_tika_server_healthy() -> bool:
    r: Response = get(TIKA_SERVER)
    return is_http_success(r)

def is_mongodb_server_healthy() -> bool:
    r: Response = get(MONGODB_SERVER)
    return is_http_success(r)

def build_in_db(rtype: ResourceType, db: Database, db_lock: Lock) -> Callable[[int], bool]:
    def in_db(id: int) -> bool:
        with db_lock:
            collection = db[rtype.collection_name()]
            return collection.find_one({'_id': id}) is not None
    return in_db

bodies = ResourceType.BODY.collection_name()

def get_body_id_from_name(db: Database, db_lock: Lock, name: str) -> int:
    collection = db[bodies]
    with db_lock:
        found = collection.find_one({'name': name})
    if found:
        return found['_id']
    raise RuntimeError(f"No body with name '{name}' was found.")

def get_database() -> Database:
    assert(is_mongodb_server_healthy())
    client = MongoClient()
    return client.scrape

def clear(db: Database):
    for rtype in ResourceType:
        db[rtype.collection_name()].delete_many({})

def is_in_db(db: Database, db_lock: Lock, collection: str, id: int) -> bool:
    return db[collection].find_one({'_id': id}) is not None