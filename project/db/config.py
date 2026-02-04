DB_CONFIG = {
    "dbname": "postgres",
    "user": "postgres",
    "host": "localhost",
    "password": "****"
}

SQLALCHEMY_DATABASE_URL = (
    f"postgresql+psycopg://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
    f"@{DB_CONFIG['host']}/{DB_CONFIG['dbname']}"
)
