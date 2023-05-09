from enum import StrEnum, Enum

class DocType(Enum):
    UNKNOWN = 0
    AGENDA = 1
    MINUTES = 2

class ResourceType(StrEnum):
    __ignore__ = ['locks']
    MEETING = 'meeting'
    BODY = 'body'
    PERSON = 'person'
    DOCUMENT = 'document'
    SNIPPET = 'snippet'

    def get_db_fields(self) -> dict[str, type]:
        match(self):
            case ResourceType.MEETING:
                return {'_id': int,
                        'body': int,
                        'meeting_dt': float,
                        'meeting_address': str,
                        'virtual_link': str | None,
                        'filing_dt': float,
                        'emergency': bool,
                        'annual_calendar': bool,
                        'public_notice': bool,
                        'agendas': list[int],
                        'minutes': list[int],
                        'contact': int,
                        'cancelled': bool,
                        'cancelled_dt': float | None,
                        'cancelled_reason': str | None}
            case ResourceType.BODY:
                return {'_id': int,
                        'name': str,
                        'contact': int,
                        'address': str,
                        'phone': int,
                        'tty': str | None,
                        'fax': int | None,
                        'website': str,
                        'email': str,
                        'facebook': str,
                        'twitter': str,
                        'instagram': str,
                        'linkedin': str,
                        'attributes': dict[str, str|int],
                        'people': dict[str, list[int]],
                        'supercommittee': int | None,
                        'subcommittees': list[int] | None}
            case ResourceType.PERSON:
                return {'name': str,
                        'title': str | None,
                        'phone': int | None,
                        'email': str | None}
            case ResourceType.DOCUMENT:
                return {'meeting': int,
                        'most_recent': bool,
                        'filepath': str,
                        'name': str | None,
                        'doctype': DocType,
                        'dt': float,
                        'filer': int,
                        'snippets': list[int]}
            case ResourceType.SNIPPET:
                return {'content': str}

    def plural(self) -> str:
        match(self):
            case ResourceType.MEETING: return 'meetings'
            case ResourceType.BODY: return 'bodies'
            case ResourceType.PERSON: return 'persons'
            case ResourceType.DOCUMENT: return 'documents'
            case ResourceType.SNIPPET: return 'snippets'
    
    def is_updateable(self) -> bool:
        match(self):
            case (ResourceType.MEETING
                  | ResourceType.BODY):
                return True
            case (ResourceType.DOCUMENT
                  | ResourceType.PERSON
                  | ResourceType.SNIPPET):
                return False
    
    def collection_name(self) -> str:
        return self.plural()
    
    def changes_collection_name(self) -> str:
        return self.collection_name() + '_changes'