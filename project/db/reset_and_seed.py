import psycopg
from config import DB_CONFIG
import bcrypt

def reset_db():
    print("Resetting database...")
    try:
        with psycopg.connect(**DB_CONFIG) as conn:
            with conn.cursor() as cur:
                # Drop existing tables to ensure clean slate
                cur.execute("DROP TABLE IF EXISTS todos CASCADE")
                cur.execute("DROP TABLE IF EXISTS users CASCADE")
                
                # Recreate Users table
                cur.execute("""
                    CREATE TABLE users (
                        id SERIAL PRIMARY KEY,
                        username VARCHAR(50) UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL
                    )
                """)
                
                # Recreate Todos table
                cur.execute("""
                    CREATE TABLE todos (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        task TEXT NOT NULL,
                        is_completed BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create default admin user
                username = "admin"
                password = "123"
                password_hash = bcrypt.hashpw(
                    password.encode('utf-8'), 
                    bcrypt.gensalt()
                ).decode('utf-8')
                
                cur.execute(
                    "INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id",
                    (username, password_hash)
                )
                user_id = cur.fetchone()[0]
                
                # Add sample todos
                sample_todos = [
                    ("Buy groceries", False),
                    ("Finish Python project", True),
                    ("Call mom", False)
                ]
                
                for task, status in sample_todos:
                    cur.execute(
                        "INSERT INTO todos (user_id, task, is_completed) VALUES (%s, %s, %s)",
                        (user_id, task, status)
                    )
                
            conn.commit()
            print("Database reset successfully.")
            print(f"Created default user -> Username: '{username}', Password: '{password}'")
            print(f"Added {len(sample_todos)} sample tasks.")
            
    except Exception as e:
        print(f"Error resetting database: {e}")

if __name__ == "__main__":
    reset_db()
