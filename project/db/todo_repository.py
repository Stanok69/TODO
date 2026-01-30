class TodoRepository:
    def __init__(self, connection):
        self._conn = connection
        self._ensure_table_exists()

    def _ensure_table_exists(self):
        with self._conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS todos (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    task TEXT NOT NULL,
                    is_completed BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self._conn.commit()

    def add_task(self, user_id, task_text):
        with self._conn.cursor() as cur:
            cur.execute(
                "INSERT INTO todos (user_id, task) VALUES (%s, %s)",
                (user_id, task_text)
            )
            self._conn.commit()

    def get_all_by_user(self, user_id):
        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT id, task, is_completed FROM todos WHERE user_id = %s ORDER BY id",
                (user_id,)
            )
            return cur.fetchall()

    def get_completed_by_user(self, user_id):
        with self._conn.cursor() as cur:
            cur.execute(
                "SELECT id, task, is_completed FROM todos WHERE user_id = %s AND is_completed = TRUE ORDER BY id",
                (user_id,)
            )
            return cur.fetchall()

    def toggle_status(self, task_id, user_id):
        with self._conn.cursor() as cur:
            cur.execute(
                """
                UPDATE todos
                SET is_completed = NOT is_completed
                WHERE id = %s AND user_id = %s
                """,
                (task_id, user_id)
            )
            self._conn.commit()
            return cur.rowcount > 0

    def delete_task(self, task_id, user_id):
        with self._conn.cursor() as cur:
            cur.execute(
                "DELETE FROM todos WHERE id = %s AND user_id = %s",
                (task_id, user_id)
            )
            self._conn.commit()
            return cur.rowcount > 0
