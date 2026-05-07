import json
import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
import os

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("APP_VERSION", "0.0.0-test")
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_NAME", "execution_db")
os.environ.setdefault("DB_USER", "user_exec")
os.environ.setdefault("DB_PASSWORD", "password")
os.environ.setdefault("DB_SSLMODE", "disable")

# Patch get_connection before app is imported so init_db() doesn't
# try to reach a real database during test collection.
with patch("app.db.get_connection", MagicMock()):
    from app.app import app


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_cursor(rows=None):
    rows = rows or []
    cur = MagicMock()
    cur.fetchall.return_value = rows
    cur.fetchone.return_value = rows[0] if rows else {"id": 1}
    return cur

def _make_conn(cursor=None):
    conn = MagicMock()
    conn.cursor.return_value = cursor or _make_cursor()
    return conn


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def client():
    app.config["TESTING"] = True
    return app.test_client()


# ── /health ───────────────────────────────────────────────────────────────────

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'


# ── POST /executions ──────────────────────────────────────────────────────────

VALID_PAYLOAD = {
    "job_name":   "data_ingestion",
    "run_id":     "12345",
    "status":     "completed",
    "start_time": "2024-01-01T10:00:00",
    "end_time":   "2024-01-01T10:30:00",
}

def test_execute_success(client):
    with patch("app.app.get_connection", return_value=_make_conn()):
        response = client.post('/executions', json=VALID_PAYLOAD)
    assert response.status_code == 201
    assert response.json['message'] == 'Execution recorded successfully'

def test_execute_missing_fields(client):
    payload = {"job_name": "data_ingestion", "run_id": "12345", "status": "completed"}
    response = client.post('/executions', json=payload)
    assert response.status_code == 400
    assert 'Missing fields' in response.json['error']

def test_execute_no_body(client):
    response = client.post('/executions', content_type='application/json')
    assert response.status_code == 400


# ── GET /executions ───────────────────────────────────────────────────────────

def test_list_executions_empty(client):
    with patch("app.app.get_connection", return_value=_make_conn(_make_cursor([]))):
        response = client.get('/executions')
    assert response.status_code == 200
    assert response.json['executions'] == []

def test_list_executions_returns_data(client):
    now = datetime.utcnow()
    rows = [{"id": 1, "job_name": "etl", "run_id": "abc", "status": "success",
             "start_time": now, "end_time": now, "created_at": now}]
    with patch("app.app.get_connection", return_value=_make_conn(_make_cursor(rows))):
        response = client.get('/executions')
    assert response.status_code == 200
    assert len(response.json['executions']) == 1


# ── /metrics ──────────────────────────────────────────────────────────────────

def test_metrics_endpoint(client):
    row = {"total": 10, "success": 8, "failed": 1, "running": 1, "avg_duration_seconds": 45.5}
    with patch("app.app.get_connection", return_value=_make_conn(_make_cursor([row]))):
        response = client.get('/metrics')
    assert response.status_code == 200
    assert b'execution_total' in response.data
