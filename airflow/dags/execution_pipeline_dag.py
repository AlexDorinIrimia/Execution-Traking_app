"""
execution_pipeline_dag.py
─────────────────────────
Phase 5 – Workflow Orchestration

DAG: execution_pipeline
Schedule: every hour

Tasks:
  1. check_api_health    - HTTP GET /health on the ingestion API
  2. run_dbt_staging     - dbt run --select staging
  3. run_dbt_analytics   - dbt run --select analytics
  4. run_dbt_tests       - dbt test
  5. check_recent_data   - assert rows landed in the last 2h
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

DEFAULT_ARGS = {
    "owner":            "data-engineering",
    "retries":          1,
    "retry_delay":      timedelta(minutes=2),
    "email_on_failure": False,
}

INGESTION_API_URL = os.getenv("INGESTION_API_URL", "http://host.docker.internal:8000")
DBT_PROJECT_DIR   = os.getenv("DBT_PROJECT_DIR",  "/opt/airflow/dbt/execution_dbt")
DBT_PROFILES_DIR  = os.getenv("DBT_PROFILES_DIR", DBT_PROJECT_DIR)


# ── Task callables ────────────────────────────────────────────────────────────

def check_api_health():
    import requests
    url = f"{INGESTION_API_URL.rstrip('/')}/health"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
    except Exception as exc:
        raise RuntimeError(f"API health check failed [{url}]: {exc}")

    body = resp.json()
    if body.get("status") != "healthy":
        raise ValueError(f"API unhealthy: {body}")
    print(f"API healthy — {body}")


def _run_dbt_python(*args):
    """Call dbt via its Python API instead of subprocess.
    This avoids PATH and permission issues inside the Airflow container.
    """
    from dbt.cli.main import dbtRunner, dbtRunnerResult

    runner = dbtRunner()
    cli_args = list(args) + ["--project-dir", DBT_PROJECT_DIR, "--profiles-dir", DBT_PROFILES_DIR]
    print(f"Running: dbt {' '.join(cli_args)}")
    result: dbtRunnerResult = runner.invoke(cli_args)

    if not result.success:
        raise RuntimeError(f"dbt failed: {result.exception}")


def run_dbt_staging():
    _run_dbt_python("run", "--select", "staging")


def run_dbt_analytics():
    _run_dbt_python("run", "--select", "analytics")


def run_dbt_tests():
    _run_dbt_python("test")


def check_recent_data(**context):
    import psycopg2

    window_hours = int(os.getenv("DATA_FRESHNESS_HOURS", "2"))
    conn = psycopg2.connect(
        host=os.environ["DB_HOST"],
        port=int(os.getenv("DB_PORT", 5432)),
        dbname=os.environ["DB_NAME"],
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        sslmode=os.getenv("DB_SSLMODE", "disable"),
    )
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT COUNT(*) FROM executions WHERE created_at >= NOW() - INTERVAL '%s hours';",
            (window_hours,),
        )
        count = cur.fetchone()[0]
        cur.close()
    finally:
        conn.close()

    print(f"Rows in last {window_hours}h: {count}")
    if count == 0:
        raise ValueError(f"No executions in the last {window_hours} hours.")
    print(f"Data freshness OK — {count} rows.")


# ── DAG ───────────────────────────────────────────────────────────────────────

with DAG(
    dag_id="execution_pipeline",
    description="API health → dbt staging → dbt analytics → dbt tests → freshness check",
    start_date=datetime(2025, 1, 1),
    schedule_interval="@hourly",
    catchup=False,
    default_args=DEFAULT_ARGS,
    tags=["execution-tracking", "dbt"],
) as dag:

    t_health = PythonOperator(
        task_id="check_api_health",
        python_callable=check_api_health,
    )

    t_staging = PythonOperator(
        task_id="run_dbt_staging",
        python_callable=run_dbt_staging,
    )

    t_analytics = PythonOperator(
        task_id="run_dbt_analytics",
        python_callable=run_dbt_analytics,
    )

    t_tests = PythonOperator(
        task_id="run_dbt_tests",
        python_callable=run_dbt_tests,
    )

    t_freshness = PythonOperator(
        task_id="check_recent_data",
        python_callable=check_recent_data,
    )

    t_health >> t_staging >> t_analytics >> t_tests >> t_freshness
