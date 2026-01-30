from app.app import app
import pytest

@pytest.fixture
def client():
    return app.test_client()

def test_health_check(client):
    response = client.get('/health')

    assert response.status_code == 200
    assert response.json['status'] == 'healthy'

def test_execute_success(client):
    payload = {
        "job_name": "data_ingestion",
        "run_id": "12345",
        "status": "completed",
        "start_time": "2024-01-01T10:00:00Z",
        "end_time": "2024-01-01T10:30:00Z"
    }
    response = client.post('/execution', json=payload)

    assert response.status_code == 202
    assert response.json['message'] == 'Execution recorded successfully'

def test_execute_missing_fields(client):
    payload = {
        "job_name": "data_ingestion",
        "run_id": "12345",
        "status": "completed"
    }
    response = client.post('/execution', json=payload)

    assert response.status_code == 400
    assert 'Missing fields' in response.json['error']