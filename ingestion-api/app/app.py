from flask import Flask, jsonify, request
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

@app.route('/health')
def health_check():
    return jsonify(
        status='healthy',
        environment=app.config['APP_ENV'],
        version=app.config['APP_VERSION']
    ), 200

@app.route('/execution', methods=['POST'])
def execute():
    payload = request.json

    if not payload:
        return jsonify(error='Invalid payload'), 400
    
    required_fields = [
        "job_name",
        "run_id",
        "status",
        "start_time",
        "end_time"
    ]

    missing = [f for f in required_fields if f not in payload]
    if missing:
        return jsonify(error=f'Missing fields: {", ".join(missing)}'), 400
    
    return jsonify(message='Execution recorded successfully'), 202

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)