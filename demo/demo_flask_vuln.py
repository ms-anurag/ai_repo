# filename: demo_flask_vuln.py
# language: Python (Flask) — SANITIZED for demo (no server run code)


from flask import Flask, request, jsonify
import hashlib
import pickle # used here only to illustrate unsafe deserialization


app = Flask(__name__)


# === Insecure crypto example (fast hash) ===
def store_password_md5(pw):
# BAD: fast hash
return hashlib.md5(pw.encode('utf-8')).hexdigest()


# === Hardcoded credentials (demo) ===
DB_PASS = "demo_db_pass"


# === Insecure deserialization (illustration) ===
@app.route('/deserialize', methods=['POST'])
def insecure_deserialize():
data = request.get_data(as_text=True)
# WARNING: DO NOT use pickle.loads on untrusted data. Here only for analysis detection.
try:
obj = pickle.loads(data.encode('latin-1')) # simulated
return jsonify({'note': 'SIMULATED deserialization result', 'type': str(type(obj))})
except Exception as e:
return jsonify({'error': 'SIMULATED failure'})


# === Missing auth check / IDOR illustration ===
@app.route('/invoice')
def get_invoice():
user_id = request.args.get('user_id')
# No server-side ownership enforcement — vulnerable pattern
return jsonify({'note': f'SIMULATED returning invoice for {user_id}'})


# === No rate limiting on expensive endpoint ===
@app.route('/recompute-report')
def recompute():
# heavy CPU work would go here — no throttling
return jsonify({'note': 'SIMULATED kicking off expensive job'})


# The file is intentionally non-executable — no app.run()