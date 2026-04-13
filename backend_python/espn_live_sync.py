from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os

app = Flask(__name__)
CORS(app)

DB_FILE = 'mystics_db.json'

def init_db():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, 'w') as f:
            json.dump({"masterDB": {}, "boards": {}}, f)

@app.route('/api/database', methods=['GET'])
def get_database():
    init_db()
    with open(DB_FILE, 'r') as f:
        return jsonify(json.load(f))

@app.route('/api/database', methods=['POST'])
def save_database():
    data = request.get_json()
    with open(DB_FILE, 'w') as f:
        json.dump(data, f)
    return jsonify({"status": "success", "message": "Database saved."}), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
