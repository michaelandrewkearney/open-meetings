import typesense

# client = typesense.Client({
#   'nodes': [{ 'host': 'localhost', 'port': '8108', 'protocol': 'http' }],
#   'api_key': 'xyz'
# })

# bodies_schema = {
#   "name": "bodies",
#   "fields": [
#     {"name": "id", "type": "int32"},
#     {"name": "name", "type": "string"},
#     {"name": "contact_person", "type": "int32"}
#   ],
#   "default_sorting_field": "ratings"
# }
# #client.collections.create(schema)

# documents = [
#   {"title":"Book 1","author":"Author1","ratings":24},
#   {"title":"Book 2","author":"Author2","ratings":31},
#   {"title":"Book 3","author":"Author3","ratings":30}
# ]

# books = client.collections['books']
# if books is not None:
#     books.documents.import_(documents)
#     print(books.documents.search({
#     'query_by': 'title,author',
#     'q': 'boo'
#     }))