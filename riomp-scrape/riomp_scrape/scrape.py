import requests
import sys

def get_page_contents(url: str) -> str:
    # Connect to URL and return contents
    return requests.post(url).text

def get_meeting_page_contents(id: int) -> str:
    return get_page_contents('https://opengov.sos.ri.gov/OpenMeetingsPublic/ViewMeetingDetailByID?MeetingID='+ id.__str__())

def url_to_file(url: str, method: str = 'get', filename: str | None = None):
    if method == 'get':
        r = requests.get(url)
    elif method == 'post':
        r = requests.post(url)
    else:
        raise ValueError("Method must be 'get' or 'post'.")
    
    if filename is None:
        filename = url.replace('.', '%2E').replace('/', '%2F') + '.html'
    
    with open(f'data/{filename}', 'xb') as f:
        for chunk in r.iter_content(chunk_size=128):
            f.write(chunk)