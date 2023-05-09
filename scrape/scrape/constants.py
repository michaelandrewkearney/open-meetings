TIKA_PORT: int = 9998
MONGODB_PORT: int = 27017
TYPESENSE_PORT: int = 8108

def localhost_with_port(port: int) -> str:
    return f"http://127.0.0.1:{port}"

TIKA_SERVER: str = localhost_with_port(TIKA_PORT)
TIKA_ENDPOINT: str = TIKA_SERVER + '/tika'
MONGODB_SERVER: str = localhost_with_port(MONGODB_PORT)
TYPESENSE_SERVER: str = localhost_with_port(TYPESENSE_PORT)