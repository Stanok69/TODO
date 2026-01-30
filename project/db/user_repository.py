import bcrypt

class UserRepository:
    def __init__(self, connection):
        self._conn = connection
        self._ensure_table_exists()

    def _ensure_table_exists(self):
        with self._conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL
                )
            """)
            self._conn.commit()

    def create_user(self, username, password):
        password_hash = bcrypt.hashpw(
            password.encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')

        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id",
                    (username, password_hash)
                )
                user_id = cur.fetchone()[0]
                self._conn.commit()
                return user_id
        except Exception as e:
            self._conn.rollback()
            raise e

    def get_user_by_username(self, username):
        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT id, username, password_hash FROM users WHERE username = %s",
                (username,)
            )
            return cur.fetchone()

    def verify_password(self, stored_hash, password):
        return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))
