import psycopg
from config import DB_CONFIG

try:
    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT username FROM users WHERE username='admin'")
            result = cur.fetchone()
            if result:
                print(f"SUCCESS: Found user '{result[0]}'")
            else:
                print("FAILURE: User 'admin' NOT found")
except Exception as e:
    print(f"ERROR: {e}")
