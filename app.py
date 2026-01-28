from flask import Flask, jsonify, request, send_from_directory
import json

app = Flask(__name__)

# Simple in-memory simulation state
state = {
    "money": 1000,
    "population": 1,
    "happiness": 50,
    "location": "Home",
    "energy": 100,
    "security": 50
}

# Load or initialize saved state from file
SAVE_FILE = '/home/workspace/Projects/OpenWorldLifeSimulator/state.json'

def load_state():
    try:
        with open(SAVE_FILE, 'r') as f:
            return json.load(f)
    except:
        return state

def save_state(s):
    with open(SAVE_FILE, 'w') as f:
        json.dump(s, f)

state = load_state()

@app.route("/")
def index():
    # Serve HTML page
    return send_from_directory('.', 'simulation.html')

@app.route("/api/state")
def get_state():
    return jsonify(state)

@app.route("/api/update", methods=["POST"])
def update_state():
    global state
    data = request.get_json()
    if isinstance(data, dict):
        state.update(data)
        save_state(state)
    return jsonify({"status": "ok", "new_state": state}), 200

@app.route("/api/reset", methods=["POST"])
def reset_state():
    global state
    state = {"money": 1000, "population": 1, "happiness": 50, "location": "Home", "energy": 100, "security": 50}
    save_state(state)
    return jsonify({"status": "ok", "new_state": state}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)