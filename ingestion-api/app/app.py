from flask import Flask, jsonify, request
from app.db import get_connection, init_db
import os

app = Flask(__name__)


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify(
        status='healthy',
        environment=os.getenv('APP_ENV'),
        version=os.getenv('APP_VERSION'),
    ), 200


@app.route('/metrics', methods=['GET'])
def metrics():
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                COUNT(*)                                          AS total,
                COUNT(*) FILTER (WHERE status = 'success')       AS success,
                COUNT(*) FILTER (WHERE status = 'failed')        AS failed,
                COUNT(*) FILTER (WHERE status = 'running')       AS running,
                ROUND(AVG(
                    EXTRACT(EPOCH FROM (end_time - start_time))
                )::numeric, 2)                                    AS avg_duration_seconds
            FROM executions;
        """)
        row = dict(cursor.fetchone())
        cursor.close()
        conn.close()
    except Exception as e:
        return jsonify(error=str(e)), 500

    lines = [
        "# HELP execution_total Total executions ingested",
        "# TYPE execution_total counter",
        f"execution_total {row['total']}",
        "# HELP execution_success_total Executions with status=success",
        "# TYPE execution_success_total counter",
        f"execution_success_total {row['success']}",
        "# HELP execution_failed_total Executions with status=failed",
        "# TYPE execution_failed_total counter",
        f"execution_failed_total {row['failed']}",
        "# HELP execution_running_total Executions currently running",
        "# TYPE execution_running_total gauge",
        f"execution_running_total {row['running']}",
        "# HELP execution_avg_duration_seconds Average execution duration",
        "# TYPE execution_avg_duration_seconds gauge",
        f"execution_avg_duration_seconds {row['avg_duration_seconds'] or 0}",
    ]
    return "\n".join(lines) + "\n", 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.route('/executions', methods=['POST'])
def execute():
    payload = request.get_json(silent=True)

    if not payload:
        return jsonify(error='Request body must be valid JSON'), 400

    required_fields = ["job_name", "run_id", "status", "start_time", "end_time"]
    missing = [f for f in required_fields if f not in payload]
    if missing:
        return jsonify(error=f"Missing fields: {', '.join(missing)}"), 400

    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO executions (job_name, run_id, status, start_time, end_time)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id;
        """, (
            payload["job_name"],
            payload["run_id"],
            payload["status"],
            payload["start_time"],
            payload["end_time"],
        ))
        # FIX: RealDictRow is not JSON-serialisable — wrap in dict()
        execution = dict(cursor.fetchone())
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        return jsonify(error=str(e)), 500

    return jsonify(message='Execution recorded successfully', id=execution['id']), 201


@app.route('/executions', methods=['GET'])
def list_executions():
    try:
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM executions ORDER BY created_at DESC;")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
    except Exception as e:
        return jsonify(error=str(e)), 500

    result = []
    for row in rows:
        r = dict(row)
        # FIX: datetime objects are not JSON-serialisable
        for key in ('start_time', 'end_time', 'created_at'):
            if r.get(key) is not None:
                r[key] = r[key].isoformat()
        result.append(r)

    return jsonify(executions=result), 200


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=8000)
