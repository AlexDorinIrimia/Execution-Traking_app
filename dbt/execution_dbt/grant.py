import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()  # loads your .env automatically

DB_HOST = "127.0.0.1"
DB_PORT =  "15432"
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")        # current dbt user = user_exec
DB_PASSWORD = os.getenv("DB_PASSWORD")

# IMPORTANT: run grants as the table owner
ADMIN_USER = DB_USER
ADMIN_PASSWORD = DB_PASSWORD

if not ADMIN_PASSWORD:
    raise Exception("Add ADMIN_DB_PASSWORD to .env (password for exec_user or RDS master user)")

conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=ADMIN_USER,
    password=ADMIN_PASSWORD,
)
conn.autocommit = True
cur = conn.cursor()

print("Connected. Applying grants...")

cur.execute("""
GRANT USAGE ON SCHEMA public TO user_exec;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO user_exec;

ALTER DEFAULT PRIVILEGES FOR USER user_exec IN SCHEMA public
GRANT SELECT ON TABLES TO user_exec;
""")

cur.execute("""
GRANT USAGE, CREATE ON SCHEMA analytics_staging TO user_exec;
GRANT USAGE, CREATE ON SCHEMA analytics_analytics TO user_exec;
""")

print("✅ Grants applied.")
cur.close()
conn.close()
