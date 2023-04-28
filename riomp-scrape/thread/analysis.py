import re
import ast
from typing import Callable

# groups: meeting_id
FORM_ACTION_PATTERN = '/OpenMeetingsPublic/ViewMeetingDetailByID\?MeetingID=(\d{6,7})'

# groups: mon, day, year
SIMPLE_DATE_PATTERN = '(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) (?: (\d)|(\d{2})) (\d{4})'

# groups: mon, day, year, cancelled_mon, cancelled_day, cancelled_year
DATE_PATTERN = f'{SIMPLE_DATE_PATTERN}(?:\s*\({SIMPLE_DATE_PATTERN}\))?'

# groups: hours, minutes, meridiem
SIMPLE_TIME_PATTERN = '(\d{1,2})\:(\d{2}) ?((?:A|P)M)'
# groups: hours, minutes, meridiem, cancelled_hours, cancelled_minutes, cancelled_meridiem
TIME_PATTERN = f'{SIMPLE_TIME_PATTERN}(?:\s*\({SIMPLE_TIME_PATTERN}\))?'

# groups: mon, day, year, hours, minutes, meridiem
DT_PATTERN = f'{SIMPLE_DATE_PATTERN}, {SIMPLE_TIME_PATTERN}'

# groups: value
YES_NO_PATTERN = '(Yes|No)'

# groups: value
INT_FLAG_PATTERN = '(0|1)'

# groups: extension
EXTENSION_PATTERN = ',?\s?(?:(?:\(x?(\d)+\))|(?:VP)|(?:(?:ext|EXT|Ext|X|x| )[\,\.]?\s?(\d*)))'

# groups: area_code, prefix, line_number, extension
PHONE_PATTERN = '(?:(?:\d[-\.]?\s?)?\(?(\d{3})\)?[-\.]?\s?)?(\d{3})[-\.]?\s?(\d{4})' + f'(?:{EXTENSION_PATTERN})?'
# groups: email
EMAIL_PATTERN = '(\S*@\S*)'

# groups: docname, doctype, filing_dt, poster
DOC_TEXT_PATTERN = f'(?:(.*), )?(Agenda|Minutes) filed on {DT_PATTERN}(?: by (.+))?'

# groups: filepath
DOC_ONCLICK_PATTERN = "DownloadMeetingFiles\('(.*)'\)"

def add_line_markers_to_pattern(pattern: str) -> str:
    return f'^{pattern}$'

def build_is_normal(pattern: str) -> Callable[[str], bool]:
    def is_normal(string: str) -> bool:
        return re.fullmatch(pattern, string) is not None
    return is_normal

def id_matches_form_action(id: int, form_action:str) -> bool:
    match = re.fullmatch(FORM_ACTION_PATTERN, form_action)
    if match is None:
        return False
    return id == int(match.group(1))

def is_document_normal(string: str) -> bool:
    docs: dict[str, str]= ast.literal_eval(string)
    for text, onclick in docs.items():
        onclick_match = re.fullmatch(DOC_ONCLICK_PATTERN, onclick)
        if onclick_match is None:
            return False
        if text == '' and onclick_match.group(1) == '':
            continue
        if re.fullmatch(DOC_TEXT_PATTERN, text) is None:
            return False
    return True