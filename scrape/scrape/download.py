from time import sleep
from typing import Callable
from requests import Response, get, post
from io_utils import is_http_success

MAX_TRIES: int = 3
TRY_WAIT: float = 10.0

def url_to_file(url: str, method: str = 'get', filename: str | None = None):
    if method == 'get':
        r = get(url)
    elif method == 'post':
        r = post(url)
    else:
        raise ValueError("Method must be 'get' or 'post'.")
    
    if filename is None:
        filename = url.replace('.', '%2E').replace('/', '%2F') + '.html'
    
    with open(f'{filename}', 'xb') as f:
        for chunk in r.iter_content(chunk_size=128):
            f.write(chunk)

# Generate URLs

generate_meeting_url: Callable[[int], str] = lambda id : f'https://opengov.sos.ri.gov/OpenMeetingsPublic/ViewMeetingDetailByID?MeetingID={id}'

def generate_body_om_url(id: int) -> str:
    return f'https://opengov.sos.ri.gov/OpenMeetingsPublic/OpenMeetingDashboard?subtopmenuId=201&EntityID={id}'

def generate_body_gd_url(id: int) -> str:
    return f"https://opengov.sos.ri.gov/OpenMeetingsPublic/GovDirectory?subtopmenuID=202&EntityID={id}"

def generate_body_bm_url(id: int) -> str:
    return f"https://opengov.sos.ri.gov/OpenMeetingsPublic/BoardMembers?subtopmenuID=203&EntityID={id}"

def generate_document_url(filename: str) -> str:
    url: str = f"https://opengov.sos.ri.gov/Common/DownloadMeetingFiles?FilePath={filename}"
    return url

def download_meeting(id: int, max_tries: int = MAX_TRIES, wait: float = TRY_WAIT) -> Response:
    url = generate_meeting_url(id)
    r: Response = multitry(max_tries, wait, get, is_http_success, url)
    return r

def download_body(id: int, max_tries: int = MAX_TRIES, wait: float = TRY_WAIT) -> dict[str, Response]:
    om_url = generate_body_om_url(id)
    gd_url = generate_body_gd_url(id)
    bm_url = generate_body_bm_url(id)
    om: Response = multitry(max_tries, wait, get, is_http_success, om_url)
    gd: Response = multitry(max_tries, wait, get, is_http_success, gd_url)
    bm: Response = multitry(max_tries, wait, get, is_http_success, bm_url)
    return {'om': om, 'gd': gd, 'bm': bm}

def download_document(filename: str, max_tries: int = MAX_TRIES, wait: float = TRY_WAIT) -> Response:
    url = generate_document_url(filename)
    r: Response = multitry(max_tries, wait, get, is_http_success, url)
    return r

def multitry(max_tries: int, wait: float, func: Callable, is_success: Callable, *args):
    try_count = 0
    while try_count < max_tries:
        try_count += 1
        try:
            result = func(*args)
            if is_success(result):
                return result
            sleep(wait)
        except Exception:
            sleep(wait)
    raise RuntimeError(f'{str(func)} with args {str(args)} failed after {try_count} tries with {wait} second wait.')