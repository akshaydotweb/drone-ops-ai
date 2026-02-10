# 🚁 Drone Operations Coordinator AI

A conversational AI agent for intelligent drone fleet management, pilot assignment, and mission coordination with real-time conflict detection.

**[🔗 Live Demo](https://drone-ops-ai.replit.dev)** | **[📊 Architecture](#architecture)** | **[💡 Decision Log](./DECISION_LOG.md)**

---

## 📋 Overview

The Drone Operations Coordinator is an AI-powered conversational agent designed to streamline drone fleet management. It helps operators:

- **Find & assign available pilots** to missions based on skills, certifications, and location
- **Allocate drones** with matching capabilities for complex operations
- **Detect scheduling conflicts** (double-booking, skill mismatches, equipment gaps)
- **Manage urgent missions** with priority-based reassignment
- **Track mission status** and resource availability in real-time

### Key Features

✅ **Conversational Interface** - Natural language queries with intelligent fallback mode
✅ **Dual-Mode Processing** - AI-powered (ChatGPT) with rule-based fallback
✅ **Conflict Detection** - Identifies double-allocations, skill gaps, and maintenance issues
✅ **Rule-Based Intelligence** - Works without API keys (graceful degradation)
✅ **Real-time Data** - CSV-based fleet data with immediate updates

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   Web Interface (Flask)                  │
│              templates/index.html (Chat UI)              │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│                    app.py (API Layer)                    │
│        /api/chat  │  /api/status  │  /api/history       │
└──────────────────────┬──────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────┐
│              DroneOperationsAgent (Orchestrator)         │
│  - Conversation Management                              │
│  - Query Routing (_process_with_llm / _process_rule)    │
│  - LLM Integration (ChatOpenAI w/ graceful fallback)    │
└─────┬──────────────────────┬─────────────────┬──────────┘
      │                      │                 │
┌─────▼────────┐  ┌─────────▼──────┐  ┌──────▼─────────┐
│ Tools Layer  │  │ ConflictDetector│  │ DroneDatabase   │
│ (12 tools)   │  │ (5 checks)      │  │ (In-memory DB)  │
└─────────────►┘  └────────────────┘  └─────────────────┘
      │
┌─────┴───────────────────────────────────────────────────┐
│              CSV Data Sources (sample-data/)             │
│  pilots.csv  │  drones.csv  │  missions.csv             │
└───────────────────────────────────────────────────────────┘
```

### Components

| Component | Purpose | Technology |
|-----------|---------|-----------|
| **Agent** | Main orchestrator, query processing | Python + LangChain |
| **Tools** | Reusable drone operations functions | Custom Python classes |
| **Database** | Fleet data storage & querying | In-memory (CSV-backed) |
| **Conflict Detector** | Validates assignments, detects issues | Python logic |
| **Web Interface** | User interaction layer | Flask + HTML/CSS/JS |

---

## 🚀 Quick Start

### Local Development

```bash
# 1. Clone & setup
git clone <repo-url>
cd drone-ops-ai
bash setup.sh

# 2. Configure (optional - for ChatGPT integration)
echo "OPENAI_API_KEY=sk-..." >> .env

# 3. Run
python app.py
# Visit http://localhost:5000
```

### Environment Variables

```bash
OPENAI_API_KEY    # Optional: ChatOpenAI API key
PORT              # Default: 5000
DEBUG             # Default: False
```

---

## 💬 Usage Examples

### Query Examples

```
👤 User: "Show available pilots"
🤖 Agent: Lists all pilots with status "Available"

👤 User: "Find pilots in Bangalore with Mapping skills"
🤖 Agent: Filters by location and skill set

👤 User: "Assign Arjun to mission PRJ001"
🤖 Agent: Validates assignment, checks conflicts, confirms

👤 User: "What conflicts exist in current assignments?"
🤖 Agent: Detects double-bookings, skill gaps, location mismatches
```

### Query Categories

- **Availability Queries**: "Show available pilots/drones"
- **Mission Queries**: "Get details for PRJ001", "List all missions"
- **Assignment Queries**: "Best pilot for PRJ001", "Assign P001 to PRJ001"
- **Conflict Queries**: "Detect conflicts", "Check mission conflicts"

---

## 📊 Data Models

### Pilot
```python
- pilot_id: str
- name: str
- location: str
- skills: List[str]
- certifications: List[str]
- status: str (Available | On Leave | Assigned | Unavailable)
```

### Drone
```python
- drone_id: str
- model: str
- location: str
- capabilities: List[str]
- status: str (Available | Maintenance | Deployed)
```

### Mission
```python
- project_id: str
- client: str
- location: str
- required_skills: List[str]
- required_certs: List[str]
- priority: str (Standard | High | Urgent)
- start_date, end_date: datetime
```

---

## 🔍 Conflict Detection

The system detects 5 types of conflicts:

1. **Double-Booking** - Pilot/drone assigned to overlapping missions
2. **Skill Mismatch** - Pilot lacks required skills for mission
3. **Certification Mismatch** - Pilot missing required certifications
4. **Equipment Mismatch** - Drone lacks required capabilities
5. **Location Mismatch** - Resources unavailable at mission location

Example:
```
Conflict: CRITICAL - Double-booking
Pilot P001 (Arjun) assigned to:
  - PRJ001 (Jan 15-20) AND
  - PRJ002 (Jan 18-25)
```

---

## 🔄 Processing Modes

### Mode 1: ChatGPT + Tools (Premium)
```
User Query → LLM with Tool Descriptions → Tool Selection → Function Execution → Response
```
✅ Natural language understanding
✅ Contextual reasoning
❌ Requires API key & quota
❌ Slower & cost-incurring

### Mode 2: Rule-Based (Free Fallback)
```
User Query → Regex Pattern Matching → Direct Tool Call → Response
```
✅ Always works
✅ Fast & free
❌ Limited context awareness
✅ Sufficient for operational queries

---

## 🛠️ Technology Decisions

See [DECISION_LOG.md](./DECISION_LOG.md) for detailed reasoning on:
- Flask vs FastAPI vs Django
- OpenAI ChatGPT vs Claude vs Local LLM
- CSV vs SQL vs NoSQL
- Rule-based fallback architecture design
- Scalability trade-offs

---

## 📁 Project Structure

```
drone-ops-ai/
├── app.py                    # Flask web server
├── requirements.txt          # Python dependencies
├── setup.sh                  # Setup script
├── README.md                 # This file
├── DECISION_LOG.md          # Architecture decisions
│
├── src/
│   ├── agent.py             # Main orchestrator (conversational interface)
│   ├── tools.py             # 12 operational tools
│   ├── database.py          # Data management layer
│   ├── models.py            # Dataclasses (Pilot, Drone, Mission, Conflict)
│   └── conflict_detector.py # Conflict validation logic
│
├── templates/
│   └── index.html           # Chat UI
│
├── sample-data/
│   ├── pilot_roster.csv     # 5 sample pilots
│   ├── drone_fleet.csv      # 4 sample drones
│   └── missions.csv         # 3 sample missions
│
└── .github/workflows/
    └── deploy.yml           # CI/CD pipeline
```

---

## 🧪 Testing

```bash
# Test agent processing
python src/agent.py

# List available pilots
curl http://localhost:5000/api/chat -X POST \
  -H "Content-Type: application/json" \
  -d '{"message": "Show available pilots"}'

# Check status
curl http://localhost:5000/api/status
```

---

## 📦 Deployment

### Option 1: Railway (Recommended)
```bash
# Install Railway CLI
npm install -g @railway/cli

# Connect to Railway
railway login

# Deploy
railway up
```

### Option 2: Heroku
```bash
heroku create drone-ops-ai
git push heroku main
```

### Option 3: Local Docker
```bash
docker build -t drone-ops-ai .
docker run -p 5000:5000 drone-ops-ai
```

---

## 📈 Performance & Scalability

| Metric | Current | Bottleneck |
|--------|---------|-----------|
| Pilots | 5 | In-memory storage |
| Drones | 4 | CSV file I/O |
| Missions | 3 | Linear search |
| Response Time | <100ms (rule-based) | LLM API latency |
| Concurrent Users | 1 (dev) | Single thread |

**Production Recommendations:**
- Replace CSV with PostgreSQL for 1000+ records
- Implement caching for frequent queries
- Add async job queue for LLM calls
- Implement authentication & audit logging

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

---

## 📝 License

MIT License - See LICENSE file

---

## 👨‍💻 Author

**Developed for**: Drone Operations Management Challenge

**Stack**: Python 3.8+ | Flask | LangChain | ChatGPT API

---

## 🆘 Troubleshooting

### "Agent not initialized"
```bash
# Check CSV files exist
ls -la sample-data/

# Verify paths in app.py match your setup
```

### "Cannot import 'Tool' from 'langchain.tools'"
```bash
# Update dependencies
source .venv/bin/activate
pip install langchain-core --upgrade
```

### "OPENAI_API_KEY not set"
```bash
# Agent will use rule-based mode automatically
# Add key to .env for ChatGPT mode
echo "OPENAI_API_KEY=sk-..." >> .env
```

---

## 📞 Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check README.md FAQ section
- Review DECISION_LOG.md for architectural context

---

**Built with ❤️ for intelligent drone operations management**
