import sys
import psycopg
from config import DB_CONFIG
import bcrypt

print("--- DIAGNOSTIC START ---")

# 1. Check imports
print("[OK] Imports successful")

# 2. Check DB Connection
try:
    conn = psycopg.connect(**DB_CONFIG)
    print("[OK] DB Connection successful")
except Exception as e:
    print(f"[FAIL] DB Connection failed: {e}")
    sys.exit(1)

# 3. Check Users Table
try:
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM information_schema.tables WHERE table_name = 'users'")
        if cur.fetchone():
            print("[OK] Table 'users' exists")
            
            cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'users'")
            columns = [row[0] for row in cur.fetchall()]
            print(f"[INFO] Columns in 'users': {columns}")
            
            required = ['id', 'username', 'password_hash']
            if all(col in columns for col in required):
                print("[OK] All required columns present")
            else:
                print(f"[FAIL] Missing columns. Found: {columns}")
        else:
            print("[FAIL] Table 'users' does NOT exist")
except Exception as e:
    print(f"[FAIL] Error checking table: {e}")

# 4. Test User Creation and Verification
test_user = "test_diagnostic_user"
test_pass = "test_pass"

try:
    # Clean up if exists
    with conn.cursor() as cur:
        cur.execute("DELETE FROM users WHERE username = %s", (test_user,))
    conn.commit()
    
    # Create
    hashed = bcrypt.hashpw(test_pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    with conn.cursor() as cur:
        cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s) RETURNING id", (test_user, hashed))
        uid = cur.fetchone()[0]
        conn.commit()
        print(f"[OK] Created test user with ID: {uid}")
        
    # Verify
    with conn.cursor() as cur:
        cur.execute("SELECT password_hash FROM users WHERE id = %s", (uid,))
        stored_hash = cur.fetchone()[0]
        
    if bcrypt.checkpw(test_pass.encode('utf-8'), stored_hash.encode('utf-8')):
        print("[OK] Password verification successful")
    else:
        print("[FAIL] Password verification failed")
        
except Exception as e:
    print(f"[FAIL] User creation/verification failed: {e}")

conn.close()
print("--- DIAGNOSTIC END ---")
