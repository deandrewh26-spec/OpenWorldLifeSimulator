from flask import Flask, jsonify, request, send_from_directory
import json
import random
import re

app = Flask(__name__)

# Real-world locations
LOCATIONS = {
    "San Francisco Bay Area": {
        "type": "Tech Hub",
        "defensibility": 80,
        "description": "Global technology center: home to Silicon Valley giants and startups",
        "specialization": ["Technology", "Innovation", "Venture Capital"],
        "population": 5000000,
        "weather": "Mild, foggy winters"
    },
    "New York City": {
        "type": "Financial Center",
        "defensibility": 85,
        "description": "World’s primary financial hub: Wall Street, headquarters of major corporations",
        "specialization": ["Finance", "Media", "Law", "Fashion"],
        "population": 8400000,
        "weather": "Humid summers, cold winters"
    },
    "London": {
        "type": "Financial Center",
        "defensibility": 75,
        "description": "Global financial capital: City of London, multinational banks",
        "specialization": ["Finance", "Law", "Insurance", "Culture"],
        "population": 8900000,
        "weather": "Rainy, temperate"
    },
    "Shanghai": {
        "type": "Industrial Hub",
        "defensibility": 60,
        "description": "Manufacturing powerhouse: global supply chain hub",
        "specialization": ["Manufacturing", "Trade", "Technology"],
        "population": 26000000,
        "weather": "Humid, hot summers"
    },
    "Texas Hill Country": {
        "type": "Energy Hub",
        "defensibility": 65,
        "description": "Energy frontier: oil, gas, and emerging renewable energy production",
        "specialization": ["Energy", "Manufacturing", "Technology"],
        "population": 2700000,
        "weather": "Hot summers, mild winters"
    }
}

# Real-world economic indicators
MARKETS = {
    "NASDAQ": {"index": 15000, "volatility": 1.2, "sector": "Technology"},
    "S&P 500": {"index": 4700, "volatility": 0.8, "sector": "Large Cap"},
    "DOW JONES": {"index": 38000, "volatility": 0.7, "sector": "Blue Chip"},
    "BTC-USD": {"index": 45000, "volatility": 2.5, "sector": "Crypto"}
}

# Real-world AI prompts for game control
AI_PROMPTS = [
    "Send a team to expand into the San Francisco Bay Area",
    "Invest in green technology sectors in Texas",
    "Launch a cryptocurrency exchange in London",
    "Build renewable energy infrastructure in Shanghai",
    "Establish a AI lab in San Francisco",
    "Offer stock market services in New York",
    "Create a fintech startup in London",
    "Develop healthcare technologies in New York",
    "Enter the EV market in Shanghai",
    "Invest in chip manufacturing in Taiwan"
]

# Real-world event scenarios
EVENTS = {
    "Tech Boom": {
        "name": "Technology Boom",
        "location": "San Francisco Bay Area",
        "effect": {"money": 5000, "happiness": 15},
        "chance": 0.3,
        "description": "New startup finds breakthrough AI algorithm. Valuation skyrockets."
    },
    "Market Crash": {
        "name": "Market Crash",
        "location": "New York City",
        "effect": {"money": -2000, "happiness": -10, "security": -5},
        "chance": 0.2,
        "description": "Sudden stock market collapse due to geopolitical tensions."
    },
    "Tech Breakthrough": {
        "name": "Tech Breakthrough",
        "location": "Texas Hill Country",
        "effect": {"energy": 20, "money": 1000},
        "chance": 0.25,
        "description": "Renewable energy efficiency improves by 40% in region."
    },
    "Fintech Expansion": {
        "name": "Fintech Expansion",
        "location": "London",
        "effect": {"money": 1500, "happiness": 10},
        "chance": 0.35,
        "description": "Digital banking adoption reaches new highs across markets."
    },
    "Supply Chain Disruption": {
        "name": "Supply Chain Disruption",
        "location": "Shanghai",
        "effect": {"money": -3000, "population": -5},
        "chance": 0.15,
        "description": "Port congestion and manufacturing delays impact global supply."
    },
    "Crypto Surge": {
        "name": "Crypto Surge",
        "location": "London",
        "effect": {"money": 3000, "happiness": 12},
        "chance": 0.2,
        "description": "Major institutional adoption drives cryptocurrency prices higher."
    },
    "Climate Event": {
        "name": "Climate Event",
        "location": "Texas Hill Country",
        "effect": {"happiness": -15, "energy": -10, "money": -1000},
        "chance": 0.1,
        "description": "Severe weather events disrupt energy production."
    },
    "Venture Capital Influx": {
        "name": "Venture Capital Influx",
        "location": "San Francisco Bay Area",
        "effect": {"money": 4000, "happiness": 8, "population": 5},
        "chance": 0.3,
        "description": "Silicon Valley sees record venture capital investments."
    }
}

state = {
    "money": 1000000,
    "population": 5000,
    "happiness": 60,
    "location": "New York City",
    "day": 1,
    "energy": 100,
    "security": 70,
    "recent_events": ["Simulation started"],
    "cash_invested": 0,
    "dividends_received": 0
}

def load_state():
    global state
    try:
        with open('state.json', 'r') as f:
            state = json.load(f)
    except FileNotFoundError:
        pass

def save_state():
    global state
    with open('state.json', 'w') as f:
        json.dump(state, f, indent=2)

def add_event(description):
    state["recent_events"].append(f"Day {state['day']}: {description}")
    if len(state["recent_events"]) > 20:
        state["recent_events"].pop(0)
    save_state()

def ai_chat(prompt):
    prompt = prompt.lower()
    
    # Location commands
    if "go to" in prompt or "visit" in prompt:
        location_name = prompt.split("go to")[-1].strip().split()[0].strip()
        for loc in LOCATIONS:
            if loc.lower() in location_name:
                state["location"] = loc
                add_event(f"Travelled to {loc}")
                return {"response": f"You've moved to {loc}. {LOCATIONS[loc]['description']}", "state": state}
        return {"response": f"Location '{location_name}' not found. Available: {list(LOCATIONS.keys())}", "state": state}
    
    # AI prompt-style actions
    if any(action in prompt for action in AI_PROMPTS):
        action = random.choice(AI_PROMPTS)
        state["money"] += random.randint(2000, 8000)
        state["happiness"] += random.randint(5, 15)
        state["population"] += random.randint(10, 100)
        state["cash_invested"] += random.randint(50000, 200000)
        add_event(f"Executed: {action}")
        return {"response": f"Action completed successfully: {action} ✅\nWe've allocated funds and expanded operations. +${random.randint(2000, 8000)} capital, {random.randint(5, 15)} happiness gain, {random.randint(10, 100)} new personnel.", "state": state}
    
    # Command prompts
    elif "help" in prompt:
        help_text = """
AVAILABLE COMMANDS:
• "go to [location]" - Travel to a location (San Francisco Bay Area, New York City, London, Shanghai, Texas Hill Country)
• "do something" - Execute a random business venture or investment
• "check state" - View current simulation status
• "advance day" - Fast-forward time (gain income, face events)
• "invest [amount]" - Invest money in a venture (e.g., "invest 50000")
• "research [topic]" - Perform research in technology or finance
• "reset" - Start a new simulation
• "ai prompt" - Get a real AI-style business prompt to execute
• "market report" - View current market indices

EXAMPLES:
"I want to go to San Francisco"
"Invest 100000 in green technology"
"Execute this AI prompt: Launch a cryptocurrency exchange"
"""
        return {"response": help_text, "state": state}
    
    elif "check state" in prompt or "status" in prompt:
        market_index = MARKETS["S&P 500"]["index"] + random.randint(-200, 200)
        return {
            "response": f"📊 CURRENT STATUS: Day {state['day']}, Wealth: ${state['money']:,.0f}, Happiness: {state['happiness']}%, Population: {state['population']:,.0f}",
            "state": state
        }
    
    elif "advance day" in prompt:
        state["day"] += 1
        income = state["population"] * 10 + state["cash_invested"] * 0.05
        state["money"] += int(income)
        state["energy"] -= random.randint(5, 15)
        add_event(f"Day advanced. Gained ${int(income):,} income.")
        return {"response": f"⏱️ Day {state['day']} advanced. You've earned ${int(income):,} income.", "new_day": state["day"], "state": state}
    
    elif "reset" in prompt or "new game" in prompt:
        initial_state = {
            "money": 1000000,
            "population": 5000,
            "happiness": 60,
            "location": "New York City",
            "day": 1,
            "energy": 100,
            "security": 70,
            "recent_events": ["New game started"],
            "cash_invested": 0,
            "dividends_received": 0
        }
        state.update(initial_state)
        add_event("Simulation reset. New game started.")
        return {"response": "🔄 Game reset. Starting fresh with $1,000,000 and your choice of headquarters in New York City.", "state": state}
    
    elif "invest" in prompt:
        import re
        match = re.search(r'invest\s+(\d+)', prompt)
        if match:
            amount = int(match.group(1))
            if amount <= state["money"]:
                state["money"] -= amount
                state["cash_invested"] += amount
                add_event(f"Invested ${amount:,} in a venture")
                return {"response": f"💰 Invested ${amount:,} in a business venture. Funds deployed to multiple markets.", "state": state}
            else:
                return {"response": f"Insufficient funds. You have ${state['money']:,.0f}, but need ${amount:,}.", "state": state}
        else:
            return {"response": "Please specify an amount: invest [amount] (e.g., invest 50000)", "state": state}
    
    elif "research" in prompt:
        state["happiness"] += 5
        state["energy"] -= 10
        add_event(f"Research completed in technology sector")
        topics = ["AI Models", "Clean Energy", "Quantum Computing", "FinTech", "Biotech", "Space Technology"]
        topic = random.choice(topics)
        return {"response": f"🔬 Research completed: {topic} breakthrough discovered! +5 happiness, technology sector enhanced.", "state": state}
    
    elif "market report" in prompt:
        report = "\n".join([f"{k}: {v['index']:,} (Volatility: {v['volatility']})" for k, v in MARKETS.items()])
        return {"response": f"📈 MARKET REPORT:\n{report}", "state": state}
    
    elif "ai prompt" in prompt:
        return {"response": f"Here's a real AI-style business prompt for you:\n\n{random.choice(AI_PROMPTS)}\n\nType it as a command to execute it!", "state": state}
    
    else:
        return {"response": f"Command not recognized. Type 'help' for available commands.", "state": state}

@app.route("/")
def index():
    return send_from_directory('.', 'simulation.html')

@app.route("/api/state")
def get_state():
    return jsonify(state)

@app.route("/api/locations")
def get_locations():
    return jsonify(LOCATIONS)

@app.route("/api/market-report")
def get_market_report():
    report = "\n".join([f"{k}: {v['index']:,} (Volatility: {v['volatility']}) - {v['sector']}" for k, v in MARKETS.items()])
    return {"report": report, "markets": MARKETS}

@app.route("/api/ai-chat", methods=["POST"])
def ai_chat_endpoint():
    data = request.get_json()
    prompt = data.get("prompt", "")
    result = ai_chat(prompt)
    return jsonify(result)

@app.route("/api/advance-day", methods=["POST"])
def advance_day():
    income = state["population"] * 10 + state["cash_invested"] * 0.05
    state["day"] += 1
    state["money"] += int(income)
    state["energy"] -= random.randint(5, 15)
    add_event(f"Day advanced. Gained ${int(income):,} income.")
    return jsonify({"new_day": state["day"], "state": state})

if __name__ == "__main__":
    load_state()
    add_event("Simulation started")
    app.run(host="0.0.0.0", port=8080)