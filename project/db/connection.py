import psycopg
from config import DB_CONFIG

class DatabaseConnection:
    def __init__(self):
        self._connection = None

    def __enter__(self):
        self._connection = psycopg.connect(**DB_CONFIG)
        return self._connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._connection:
            self._connection.close()

def get_db_connection():
    return psycopg.connect(**DB_CONFIG)
