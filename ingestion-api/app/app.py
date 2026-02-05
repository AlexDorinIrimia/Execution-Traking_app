from flask import Flask, jsonify, request
from db import get_connection, init_db
import os

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify(
        status='healthy',
        environment=os.getenv('APP_ENV'),
        version=os.getenv('APP_VERSION')
    ), 200

@app.route('/executions', methods=['POST'])
def execute():
    payload = request.get_json()

    name = payload.get('job_name')
    status = payload.get('status', 'pending')

    if not name:
        return jsonify(error='Job name is required'), 400
    
    required_fields = ["job_name", "run_id", "status", "start_time", "end_time"]
    missing = [f for f in required_fields if f not in payload]

    if missing:
        return jsonify(error=f"Missing fields: {', '.join(missing)}"), 400
    
    job_name = payload["job_name"]
    run_id = payload["run_id"]
    status = payload["status"]
    start_time = payload["start_time"]
    end_time = payload["end_time"]

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO executions (job_name, run_id, status, start_time, end_time)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
    """, (job_name, run_id, status, start_time, end_time))
    execution= cursor.fetchone()
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify(message='Execution recorded successfully', execution=execution), 201

@app.route('/executions', methods=['GET'])
def list_executions():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM executions ORDER BY created_at DESC;")
    executions = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify(executions=executions), 200

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8000)