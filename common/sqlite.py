import sqlite3
import time

def safe_execute(conn, query, params=(), retries=60):
    for i in range(retries):
        try:
            conn.execute(query, params)
            conn.commit()
            return
        except sqlite3.OperationalError as e:
            if "locked" in str(e):
                print(f"DB is locked, retrying in 0.5s... ({i+1}/{retries})")
                time.sleep(0.5)
            else:
                raise
    raise RuntimeError("Failed to execute after several retries")