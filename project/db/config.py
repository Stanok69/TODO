import os

DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "postgres"),
    "user": os.getenv("DB_USER", "postgres"),
    "host": os.getenv("DB_HOST", "localhost"),
    "password": os.getenv("DB_PASSWORD", "123"),
}

SQLALCHEMY_DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
)

TOKEN_EXPIRE_MINUTES = 60
