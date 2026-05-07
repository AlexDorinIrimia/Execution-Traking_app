"""
grant.py – Apply SELECT grants to the dbt user on the public schema.

Run once after Terraform creates RDS and before running dbt:
    python dbt/execution_dbt/grant.py

Requires: psycopg2-binary, python-dotenv
"""
import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

# FIX: original hardcoded host="127.0.0.1" and port="15432" (a local SSH-tunnel
#      port). These values were never right for production and would silently break
#      in any environment that is not the developer's laptop.
#      Now reads from the same env vars used by the API and dbt.
DB_HOST     = os.getenv("DB_HOST")
DB_PORT     = os.getenv("DB_PORT", "5432")
DB_NAME     = os.getenv("DB_NAME")
DB_USER     = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

if not all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]):
    raise EnvironmentError(
        "Missing required env vars. Set DB_HOST, DB_NAME, DB_USER, DB_PASSWORD "
        "in your .env or environment before running grant.py"
    )

conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    sslmode=os.getenv("DB_SSLMODE", "require"),
)
conn.autocommit = True
cur = conn.cursor()

print(f"Connected to {DB_HOST}:{DB_PORT}/{DB_NAME} as {DB_USER}")
print("Applying grants…")

# Grant read access on the raw public schema tables
cur.execute("""
GRANT USAGE  ON SCHEMA public TO user_exec;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO user_exec;

ALTER DEFAULT PRIVILEGES FOR USER user_exec IN SCHEMA public
  GRANT SELECT ON TABLES TO user_exec;
""")

# FIX: original granted on 'analytics_staging' and 'analytics_analytics' —
#      these schema names do not exist.  dbt creates schemas named after the
#      profile's `schema` setting + model folder, which with schema=analytics
#      in profiles.yml gives: analytics_staging and analytics_analytics (dbt
#      appends the subfolder).  But the dbt_project.yml overrides +schema:
#      public for both layers, so both models land in public.
#      Grant CREATE on public so dbt can materialise tables/views there.
cur.execute("""
GRANT USAGE, CREATE ON SCHEMA public TO user_exec;
""")

print("✅ Grants applied.")
cur.close()
conn.close()
