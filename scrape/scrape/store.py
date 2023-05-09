from threading import Lock
from pymongo.database import Database
from pymongo.collection import Collection
from resource_type import ResourceType
from validate import Meeting, Body, Document

def insert(db: Database, db_lock: Lock, collection: str, object: dict) -> int:
    with db_lock:
        return db[collection].insert_one(object).inserted_id

def delete(db: Database, db_lock: Lock, collection: str, id: int) -> int:
    with db_lock:
        return db[collection].delete_one({'_id':id}).deleted_count

meetings = ResourceType.MEETING.collection_name()
bodies = ResourceType.BODY.collection_name()
docs = ResourceType.DOCUMENT.collection_name()
snips = ResourceType.SNIPPET.collection_name()

def store_meeting(db: Database, db_lock: Lock, id: int, meeting: Meeting) -> int:
    d: dict = {}
    d['_id'] = id
    d['stamp'] = meeting.stamp
    d['body'] = meeting.body
    d['meeting_dt'] = meeting.meeting_dt
    d['meeting_address'] = meeting.meeting_address
    d['filing_dt'] = meeting.filing_dt
    agendas: list[int] = []
    for doc in meeting.agendas:
        agendas.append(store_document(db, db_lock, doc))
    d['agendas'] = agendas
    minutes: list[int] = []
    for doc in meeting.minutes:
        minutes.append(store_document(db, db_lock, doc))
    d['minutes'] = minutes

    if meeting.contact_name:
        d['contact_name'] = meeting.contact_name
    if meeting.contact_phone:
        d['contact_phone'] = meeting.contact_phone
    if meeting.contact_email:
        d['contact_email'] = meeting.contact_email
    if meeting.is_meeting_dt_changed:
        d['is_meeting_dt_changed'] = True
    if meeting.is_address_changed:
        d['is_address_changed'] = True
    if meeting.is_annual_calendar_changed:
        d['is_annual_calendar_changed'] = True
    if meeting.is_emergency_changed:
        d['is_emergency_changed'] = True
    if meeting.is_public_notice_changed:
        d['is_public_notice_changed'] = True
    if meeting.is_agenda_changed:
        d['is_agenda_changed'] = True
    if meeting.is_emergency:
        d['is_emergency'] = True
    if meeting.is_annual_calendar:
        d['is_annual_calendar'] = True
    if meeting.is_public_notice:
        d['is_public_notice'] = True
    if meeting.is_cancelled:
        d['is_cancelled'] = True
        d['cancelled_dt'] = meeting.cancelled_dt
        d['cancelled_reason'] = meeting.cancelled_reason
    return insert(db, db_lock, meetings, d)

def store_body(db: Database, db_lock: Lock, id: int, body: Body) -> int:
    d: dict = {}
    d['_id'] = id
    d['stamp'] = body.stamp
    d['name'] = body.name
    d['contact_name'] = body.contact_name
    d['contact_phone'] = body.contact_phone
    d['contact_email'] = body.contact_email
    d['subcommittees'] = body.subcommittees
    d['contact_information'] = body.contact_information
    if body.facebook:
        d['facebook'] = body.facebook
    if body.twitter:
        d['twitter'] = body.twitter
    if body.instagram:
        d['instagram'] = body.instagram
    if body.linkedin:
        d['linkedin'] = body.linkedin
    if body.budget:
        d['budget'] = body.budget
    if body.personnel:
        d['personnel'] = body.personnel
    if body.description:
        d['description'] = body.description
    if body.responsibilities:
        d['responsibilities'] = body.responsibilities
    d['people'] = body.people
    if body.max_members:
        d['max_members'] = body.max_members
    if body.authority:
        d['authority'] = body.authority
    d['board_members'] = body.board_members
    return insert(db, db_lock, bodies, d)

def store_document(db: Database, db_lock: Lock, doc: Document) -> int:
    d: dict = {}
    d['stamp'] = doc.stamp
    if doc.name:
        d['name'] = doc.name
    d['doctype'] = doc.doctype.value
    d['filing_dt'] = doc.dt
    if doc.filer:
        d['filer'] = doc.filer
    if doc.path:
        d['path'] = doc.path
    snippets: list[int] = []
    for snippet in doc.snippets:
        snippets.append(insert_snippet(db, db_lock, snippet))
    d['snippets'] = snippets
    return insert(db, db_lock, docs, d)

def insert_snippet(db: Database, db_lock: Lock, snippet: str) -> int:
    return insert(db, db_lock, snips, {'text': snippet})

def get_collection(self, db: Database) -> Collection:
    return db[self.collection_name()]

def get_changes_collection(self, db: Database) -> Collection:
    return db[self.changes_collection_name()]



# def build_insert_db(self, db: Database) -> Callable[[dict[str, Any]], int]:
#     field_types = self.get_db_fields()
#     collection = self.get_collection(db)
#     lock = self.get_lock()

#     def insert_db(to_insert: dict[str, Any]) -> int:
#         # Validate field types
#         for name, type in field_types.items():
#             assert(name in to_insert)
#             assert(isinstance(to_insert[name], type))
#         # Thread lock to prevent duplicate _id creation
#         with lock:
#             _id = collection.insert_one(to_insert).inserted_id
#         return _id
#     return insert_db

# def build_update_db(self, db: Database) -> Callable[[int], int]:
#     if not self.is_updateable():
#         raise RuntimeError(f'Error: cannot create update function for {str(self)}. Only updateable ResourceTypes can be updated.')
#     def update_db(id: int | str) -> int:
#         # scrape data
#         timestamp: float = dt.datetime.utcnow().timestamp()

#         scraped_data: dict[str, Any] = self.get_process()(self.get_scrape()(id)) # type: ignore
#         col: Collection = db[self.collection_name()]
#         id_query = {'_id': id}
#         results: list = list(col.find(id_query))
#         results_count: int = len(results)
#         if results_count > 1:
#             raise ValueError(f'Error: multiple entries for id {id} in {col}.')
#         if results_count == 1:
#             existing_data = results[0]
#             changes: dict[str, Any] = dict()
#             for key, val in existing_data.items():
#                 if scraped_data[key] != val:
#                     changes[key] = val
#             if len(changes) > 0:
#                 changes['id'] = existing_data['id']
#                 changes['timestamp'] = existing_data['timestamp']
#                 changes_col: Collection = db[self.changes_collection_name()]
#                 changes_col.insert_one(changes)
#                 col.update_one
#             scraped_data['timestamp'] = timestamp
#             for key in changes:
#                 pass
#         return 1
#     return update_db