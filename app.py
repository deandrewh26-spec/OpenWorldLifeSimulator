from flask import Flask, jsonify, request, send_from_directory
import json
import random
import re
import os

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

def generate_business_advice(user_prompt, current_state):
    """Generate realistic, data-driven business advice."""
    location = current_state.get("location", "New York City")
    money = current_state.get("money", 1000000)
    population = current_state.get("population", 5000)
    
    # Location-specific market insights
    market_insights = {
        "San Francisco Bay Area": """
🏢 San Francisco Bay Area Strategy:
• Tech Sector Dominance: With 50,000,000 people, focus on AI, cloud computing, and biotech
• Venture Capital Availability: Access to $50B+ in VC funding annually
• Talent Density: Silicon Valley hosts 500,000+ tech workers
• Action Plan: Consider establishing a $500,000 seed fund for AI startups. Project: 12-month ROI at 45% with exits at $2.5M-$5M per company.
        """.strip(),
        "New York City": """
🏙️ New York City Strategy:
• Financial Center Advantage: Wall Street's global dominance ($60T AUM)
• Media & Advertising: Top market for marketing spend ($100B+ annually)
• Law & Corporate HQs: Fortune 500 headquarters concentration
• Action Plan: Launch a $250,000 fintech accelerator. Project: 18-month timeline with $8M-$15M valuation upon Series A.
        """.strip(),
        "London": """
🇬🇧 London Strategy:
• Global Financial Hub: Time zone advantage for Asia-Pacific markets
• Fintech Innovation: $4B+ annual investment in UK fintech sector
• Legal Infrastructure: World-class corporate law and IP protection
• Action Plan: Develop a cryptocurrency compliance platform ($500,000 setup). Project: 24-month compliance-first approach, 22% YOY revenue growth targeting $2.8M ARR.
        """.strip(),
        "Shanghai": """
🏭 Shanghai Strategy:
• Manufacturing Powerhouse: 26,000,000 population, global supply chain hub
• Industrial Base: 90,000+ industrial enterprises
• Cost Efficiency: 40-60% lower operational costs than US
• Action Plan: Scale manufacturing operations. Budget: $800,000 for automated assembly line. Project: 36% cost reduction, 2.5x production capacity, 2-year ROI.
        """.strip(),
        "Texas Hill Country": """
⚡ Texas Hill Country Strategy:
• Energy Frontier: Oil & gas production, emerging renewable energy
• Regulatory Environment: 0% corporate income tax, 0% franchise tax
• Infrastructure: Gigawatt-scale renewable energy capacity
• Action Plan: Invest $1,000,000 in solar farm development. Project: 7-year ROI with 15% annual returns, 15MW operational by Year 3.
        """.strip()
    }
    
    prompt_lower = user_prompt.lower()
    
    # Location-specific advice
    if location in market_insights:
        return f"""
📍 LOCATION INSIGHTS: {location}
{market_insights[location]}

📊 CURRENT STATE:
• Capital: ${money:,.0f}
• Personnel: {population:,.0f} employees
• Operations: Expanding into {location}

💡 RECOMMENDATION:
Focus on sector specialization aligned with {location}'s competitive advantages. Consider increasing capital allocation by 30% for higher ROI in current location.
        """.strip()
    
    # Investment advice
    if "invest" in prompt_lower:
        allocation_options = {
            "low risk": ("Tech Equity Fund", 0.05, 0.08, "$500,000 minimum"),
            "medium risk": ("Clean Energy Fund", 0.10, 0.18, "$250,000 minimum"),
            "high risk": ("Crypto Venture Fund", 0.15, 0.35, "$100,000 minimum"),
            "real estate": ("Commercial REIT", 0.12, 0.22, "$750,000 minimum")
        }
        return f"""
💰 INVESTMENT ADVISORY
Based on your portfolio size (${money:,.0f}), consider the following allocations:

Option 1: {allocation_options['low risk'][0]}
• Yield: {allocation_options['low risk'][1]*100:.1f}-{allocation_options['low risk'][2]*100:.1f}% annually
• Minimum: {allocation_options['low risk'][3]}
• Risk Profile: Low

Option 2: {allocation_options['medium risk'][0]}
• Yield: {allocation_options['medium risk'][1]*100:.1f}-{allocation_options['medium risk'][2]*100:.1f}% annually
• Minimum: {allocation_options['medium risk'][3]}
• Risk Profile: Medium

Option 3: {allocation_options['high risk'][0]}
• Yield: {allocation_options['high risk'][1]*100:.1f}-{allocation_options['high risk'][2]*100:.1f}% annually
• Minimum: {allocation_options['high risk'][3]}
• Risk Profile: High

🎯 RECOMMENDATION: Diversify across 3-4 options to balance risk and return.
        """.strip()
    
    # Growth strategy
    if "expand" in prompt_lower or "growth" in prompt_lower:
        return f"""
📈 GROWTH STRATEGY ANALYSIS
Current Metrics:
• Employee Count: {population:,.0f}
• Capital Allocation: ${money:,.0f}
• Location: {location}

Strategic Recommendations:

1. Local Expansion (High Confidence)
• Action: Increase operations by 25% in {location}
• Investment Required: ${money * 0.25:,.0f}
• Expected Revenue: +${money * 0.35:,.0f} annually
• Timeline: 6-12 months

2. Market Diversification (Medium Confidence)
• Action: Enter adjacent market in another major hub
• Target: Competing location with specialization overlap
• Investment Required: ${money * 0.40:,.0f}
• Expected Revenue: +${money * 0.50:,.0f} annually
• Timeline: 12-18 months

3. Strategic Partnership (Low-Medium Risk)
• Action: Joint venture with local market leader
• Investment Required: ${money * 0.15:,.0f}
• Expected ROI: 22-35% over 2-3 years

💡 Suggested Path: Local expansion first (40% of capital), then market diversification.
        """.strip()
    
    # Market timing
    if "market" in prompt_lower or "timing" in prompt_lower:
        return f"""
📊 MARKET TIMING ANALYSIS
Current Markets:
• NASDAQ: 15,000 (Volatility: 1.2) - Tech sector recovering
• S&P 500: 4,700 (Volatility: 0.8) - Stable large-cap
• DOW JONES: 38,000 (Volatility: 0.7) - Blue-chip strength
• BTC-USD: 45,000 (Volatility: 2.5) - High-risk crypto

Timing Assessment:
• Bull Markets: S&P 500 + DOW JONES showing strength
• Risk Appetite: Varies by sector (Crypto: High, Tech: Medium)
• Diversification: Critical given volatility spread

Strategic Positioning:
• Allocate 60% to index funds (S&P 500, DOW JONES)
• Allocate 25% to tech exposure (NASDAQ)
• Allocate 15% to opportunistic (Crypto/Real Estate)

Expected Annual Return: 12-18% with 20% max drawdown
        """.strip()
    
    # General business advice
    return f"""
📋 STRATEGIC BUSINESS ADVISOR
Current Context:
• Location: {location}
• Capital: ${money:,.0f}
• Personnel: {population:,.0f} employees

Key Insights:
1. Location Advantage: {location} offers unique sector specialization
2. Market Position: Strong foundation with ${money:,.0f} in liquidity
3. Growth Potential: 25-40% annual expansion feasible

Recommended Actions:
• Increase local market share by 20% (6-12 month timeline)
• Allocate $750,000 for strategic expansion initiatives
• Diversify portfolio across 3-4 markets to reduce risk
• Plan for Series A funding at $5M-$8M valuation (18-month horizon)

Expected Outcomes:
• Revenue: +${money * 0.35:,.0f} annually
• Profit Margin: 18-24% after expansion costs
• Valuation Growth: 30-45% over 24 months

Do you want me to elaborate on any specific recommendation?
        """.strip()

def run_ai_api_call(user_prompt, state):
    """Run actual AI API call (OpenAI-style)."""
    messages = [
        {"role": "system", "content": "You are an expert business advisor providing realistic strategic guidance."},
        {"role": "user", "content": f"{user_prompt}. Context: {json.dumps(state, indent=2)}. Provide actionable business advice with specific numbers and timeline."}
    ]
    return messages

@app.route("/api/ai-chat", methods=["POST"])
def ai_chat():
    data = request.get_json()
    user_prompt = data.get("prompt", "").strip() if data else ""
    
    # Real-world business advisor logic
    response = generate_business_advice(user_prompt, state)
    
    return jsonify({"response": response, "state": state})

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