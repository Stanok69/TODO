import psycopg
from config import DB_CONFIG

try:
    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            # Get admin user id
            cur.execute("SELECT id FROM users WHERE username='admin'")
            user_id = cur.fetchone()[0]
            
            # Get tasks
            cur.execute("SELECT task, is_completed FROM todos WHERE user_id=%s", (user_id,))
            tasks = cur.fetchall()
            
            print(f"Found {len(tasks)} tasks for user 'admin':")
            for task, status in tasks:
                print(f"- {task} [{'x' if status else ' '}]")
                
except Exception as e:
    print(f"ERROR: {e}")
