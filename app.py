from flask import Flask, jsonify, request, send_from_directory
import json
import random

app = Flask(__name__)

# Simple in-memory simulation state
state = {
    "money": 1000,
    "population": 1,
    "happiness": 50,
    "location": "Home",
    "energy": 100,
    "security": 50,
    "day": 1,
    "inventory": {"coins": 10, "items": []},
    "recent_events": []
}

# Locations
LOCATIONS = {
    "Home": {
        "resources": {"money": 0, "population": 0},
        "defensibility": 50,
        "description": "Your safe haven."
    },
    "City": {
        "resources": {"money": 10, "population": 0},
        "defensibility": 30,
        "description": "The bustling city center."
    },
    "Corporate": {
        "resources": {"money": 50, "population": 0},
        "defensibility": 10,
        "description": "High-stakes business district."
    },
    "Adventure": {
        "resources": {"money": 0, "population": 0},
        "defensibility": 100,
        "description": "Dangerous wilderness."
    }
}

SAVE_FILE = '/home/workspace/Projects/OpenWorldLifeSimulator/save.json'

def load_state():
    try:
        with open(SAVE_FILE, 'r') as f:
            data = json.load(f)
            state.update(data)
    except (FileNotFoundError, json.JSONDecodeError):
        pass
    return state

def save_state(s):
    with open(SAVE_FILE, 'w') as f:
        json.dump(s, f)

def add_event(message):
    state["recent_events"].append(message)
    if len(state["recent_events"]) > 10:
        state["recent_events"].pop(0)

@app.route("/")
def index():
    return send_from_directory('.', 'simulation.html')

@app.route("/api/state")
def get_state():
    return jsonify(state)

@app.route("/api/locations")
def get_locations():
    return jsonify(LOCATIONS)

@app.route("/api/events", methods=["POST"])
def trigger_event():
    data = request.get_json()
    location = data.get("location")
    event_type = data.get("type", "random")
    
    events = {
        "random": [
            {"text": f"You found {random.randint(10, 100)} coins in {location}", "money": random.randint(10, 100)},
            {"text": f"{location} is bustling today!", "happiness": random.randint(5, 15)},
            {"text": f"A stranger approaches you in {location}", "security": random.randint(-10, 10)},
        ],
        "business": [
            {"text": "Business deal goes well!", "money": random.randint(100, 500)},
            {"text": "Market downturn reduces profits", "money": random.randint(-200, -50)},
            {"text": "Investment opportunity appears", "money": random.randint(500, 2000)},
        ],
        "danger": [
            {"text": "Attack in the streets!", "security": random.randint(-30, -10), "happiness": random.randint(-20, -5)},
            {"text": "Safe route discovered", "security": random.randint(10, 30)},
            {"text": "Resource theft reported", "money": random.randint(-100, -50)},
        ]
    }
    
    options = events[event_type] if event_type in events else events["random"]
    result = random.choice(options)
    
    if "text" in result:
        add_event(result["text"])
    if "money" in result:
        state["money"] += result["money"]
    if "happiness" in result:
        state["happiness"] = max(0, min(100, state["happiness"] + result["happiness"]))
    if "security" in result:
        state["security"] = max(0, min(100, state["security"] + result["security"]))
    
    save_state(state)
    return jsonify({"event": result, "new_state": state})

@app.route("/api/update", methods=["POST"])
def update_state():
    data = request.get_json()
    if isinstance(data, dict):
        state.update(data)
    save_state(state)
    return jsonify({"status": "ok", "new_state": state}), 200

@app.route("/api/reset", methods=["POST"])
def reset_state():
    template = {
        "money": 1000, "population": 1, "happiness": 50, "location": "Home",
        "energy": 100, "security": 50, "day": 1, "inventory": {"coins": 10, "items": []},
        "recent_events": []
    }
    state.update(template)
    add_event("Simulation reset")
    save_state(state)
    return jsonify({"status": "ok", "new_state": state}), 200

@app.route("/api/ai-chat", methods=["POST"])
def ai_chat():
    data = request.get_json()
    prompt = data.get("prompt", "").lower()
    response = ""
    
    if "go to" in prompt or "visit" in prompt or "travel" in prompt:
        locations = list(LOCATIONS.keys())
        target = prompt.split(" ")[-1] if len(prompt.split(" ")) > 0 else random.choice(locations)
        if target in LOCATIONS:
            state["location"] = target
            response = f"Moving to {target}."
        else:
            response = f"{target} is not a valid location. Available: {', '.join(LOCATIONS.keys())}"
    elif "event" in prompt or "something" in prompt or "happen" in prompt:
        result = request.json or {}
        event_response = request.method == "POST"
        if event_response:
            return trigger_event()
        else:
            return jsonify({"locations": LOCATIONS})
    elif "help" in prompt or "what" in prompt or "command" in prompt:
        response = f"Available commands: 'go to [location]', 'do something', 'help', 'reset', 'check state', 'update [field] [value]'."
    elif "reset" in prompt:
        template = {
            "money": 1000, "population": 1, "happiness": 50, "location": "Home",
            "energy": 100, "security": 50, "day": 1, "inventory": {"coins": 10, "items": []},
            "recent_events": []
        }
        state.update(template)
        add_event("Simulation reset")
        save_state(state)
        response = "Simulation reset. New game started."
    elif "check" in prompt and "state" in prompt:
        response = f"Current state: {state}"
    elif "update" in prompt:
        parts = prompt.split()
        if len(parts) >= 4:
            field = parts[1]
            value_str = parts[3]
            try:
                value = int(value_str) if value_str.isdigit() else value_str
                if field in state:
                    state[field] = value
                    save_state(state)
                    response = f"Updated {field} to {value}."
                else:
                    response = f"Field '{field}' not found."
            except:
                response = "Invalid value. Use numbers for stats."
        else:
            response = "Usage: update [field] [value]"
    else:
        response = "I didn't understand. Try: 'go to City', 'do something', 'help', 'reset', or 'check state'."
    
    add_event(f"AI Chat: {prompt}")
    save_state(state)
    return jsonify({"response": response, "state": state})

@app.route("/api/day", methods=["POST"])
def advance_day():
    state["day"] += 1
    daily_losses = random.randint(-50, 50)
    if daily_losses > 0:
        state["money"] -= daily_losses
        add_event(f"Daily expenses: {daily_losses} money")
    else:
        income = random.randint(20, 100)
        state["money"] += income
        add_event(f"Daily income: {income} money")
    state["happiness"] = max(0, min(100, state["happiness"] + random.randint(-5, 5)))
    save_state(state)
    return jsonify({"new_day": state["day"], "state": state})

if __name__ == "__main__":
    load_state()
    add_event("Simulation started")
    app.run(host="0.0.0.0", port=8080)