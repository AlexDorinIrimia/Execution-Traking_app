import os
import time as time_module
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

def get_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        sslmode='require',
        cursor_factory=RealDictCursor
    )
    return conn

#def init_db():
#    conn = get_connection()
#    cursor = conn.cursor()
#    cursor.execute("""
#        CREATE TABLE IF NOT EXISTS executions (
#            id SERIAL PRIMARY KEY,
#            job_name TEXT NOT NULL,
#            run_id TEXT NOT NULL,
#            status TEXT NOT NULL,
#            start_time TIMESTAMP NOT NULL,
#            end_time TIMESTAMP NOT NULL,
#            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
#        );
#    """)
#    conn.commit()
#    cursor.close()
#    conn.close()
def init_db(retries=5, delay=3):
    for attempt in range(retries):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS executions (
                    id SERIAL PRIMARY KEY,
                    job_name TEXT NOT NULL,
                    run_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            cursor.close()
            conn.close()
            print("✅ Database initialized")
            return
        except Exception as e:
            print(f"⏳ DB not ready ({attempt+1}/{retries}): {e}")
            time_module.sleep(delay)

    raise RuntimeError("❌ Could not connect to DB")