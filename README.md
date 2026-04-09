# DailyFlow AI — Backend API

FastAPI backend powering the DailyFlow AI workflow assistant.
Deployed on Railway, connects to Claude AI via the Anthropic API.

---

## 🚀 Quick Start (Local)

### 1. Clone and enter the project
```bash
git clone https://github.com/yourusername/dailyflow-backend
cd dailyflow-backend
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate       # Mac/Linux
venv\Scripts\activate          # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
# Open .env and add your ANTHROPIC_API_KEY
```

### 5. Run the server
```bash
uvicorn app.main:app --reload
```

The API will be running at: **http://localhost:8000**
Interactive docs at: **http://localhost:8000/docs**

---

## 📡 API Endpoints

### Tasks
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/tasks/prioritize` | AI prioritizes a list of tasks |
| POST | `/api/tasks/breakdown` | AI breaks a task into steps |

### Messages
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/messages/improve` | Rewrites a message with a given tone |
| POST | `/api/messages/subject` | Generates an email subject line |

### Explain
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/explain/refine` | Refines an explanation for interviews/pitches |
| POST | `/api/explain/questions` | Generates follow-up interview questions |

### Summary
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/summary/generate` | Generates a structured daily summary |

### Voice
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/voice/process` | Converts a transcript into structured tasks |

---

## 📦 Example API Calls

### Prioritize Tasks
```bash
curl -X POST http://localhost:8000/api/tasks/prioritize \
  -H "Content-Type: application/json" \
  -d '{"tasks": "Study networking, fix bug, prepare for Cisco interview"}'
```

### Improve a Message
```bash
curl -X POST http://localhost:8000/api/messages/improve \
  -H "Content-Type: application/json" \
  -d '{
    "message": "hey can u send me the report asap its kinda urgent",
    "tone": "professional",
    "message_type": "email"
  }'
```

### Refine an Explanation
```bash
curl -X POST http://localhost:8000/api/explain/refine \
  -H "Content-Type: application/json" \
  -d '{
    "explanation": "My project detects network attacks using machine learning",
    "mode": "interview"
  }'
```

### Generate Daily Summary
```bash
curl -X POST http://localhost:8000/api/summary/generate \
  -H "Content-Type: application/json" \
  -d '{
    "description": "I studied Python for 2 hours, fixed a bug, but didnt finish networking assignment",
    "tasks": [
      {"text": "Study Python", "done": true, "priority": "high"},
      {"text": "Networking assignment", "done": false, "priority": "med"}
    ]
  }'
```

---

## 🚂 Deploy to Railway

### Option 1 — Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Initialize and deploy
railway init
railway up
```

### Option 2 — GitHub Integration (Recommended)
1. Push this repo to GitHub
2. Go to [railway.app](https://railway.app)
3. Click **New Project** → **Deploy from GitHub repo**
4. Select your repo
5. Add environment variable: `ANTHROPIC_API_KEY=your_key`
6. Railway auto-detects the Procfile and deploys ✓

Your API will be live at: `https://your-app.railway.app`

---

## 🔧 Project Structure

```
dailyflow-backend/
├── app/
│   ├── main.py          # FastAPI app, CORS, router registration
│   ├── claude.py        # Anthropic API client wrapper
│   └── routers/
│       ├── tasks.py     # Task prioritization & breakdown
│       ├── messages.py  # Message & email improvement
│       ├── explain.py   # Explanation refinement & interview prep
│       ├── summary.py   # Daily summary generation
│       └── voice.py     # Voice transcript → action plan
├── requirements.txt
├── Procfile             # Railway deployment config
├── .env.example         # Environment variable template
└── README.md
```

---

## 🔗 Connect to Frontend

In your DailyFlow frontend, replace the direct Claude API calls with:

```javascript
const API_URL = "https://your-app.railway.app"  // your Railway URL

// Example: prioritize tasks
const response = await fetch(`${API_URL}/api/tasks/prioritize`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ tasks: "Study networking, fix bug" })
})
const data = await response.json()
console.log(data.result)
```

---

## 🛠 Tech Stack

- **FastAPI** — fast, modern Python web framework
- **Anthropic SDK** — Claude AI integration
- **Pydantic** — request/response validation
- **Uvicorn** — ASGI server
- **Railway** — deployment platform

---

## 📄 License
MIT — built by Daniel Nkemdirim
