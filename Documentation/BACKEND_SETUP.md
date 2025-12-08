# Discovery Coach - Backend API Setup

## Install Required Packages

```bash
pip install fastapi uvicorn
```

## Start the Backend Server

```bash
cd Discovery_coach
python app.py
```

You should see:
```
🎯 Discovery Coach FastAPI Server
==================================================
Server running on http://localhost:8050
Frontend should connect to http://localhost:8050/api/chat
API docs available at http://localhost:8050/docs
==================================================
```

## Open the GUI

Open `index.html` in your browser (or use a local server):

```bash
# Option 1: Python simple server
python -m http.server 8080

# Then open: http://localhost:8080

# Option 2: Just open the file
open index.html
```

## Architecture

**OLD (Hard-coded JavaScript):**
- ❌ JavaScript keyword matching
- ❌ No real AI
- ❌ Hard-coded responses
- ❌ No RAG knowledge base

**NEW (Real Backend):**
- ✅ Python Flask API server (`app.py`)
- ✅ Connects to `discovery_coach.py`
- ✅ Real GPT-4 with RAG
- ✅ System prompts and knowledge base
- ✅ Persistent context management

## API Endpoints

- `POST /api/chat` - Send message, get LLM response
- `POST /api/evaluate` - Evaluate Epic or Feature
- `POST /api/outline` - Get current Epic/Feature
- `POST /api/clear` - Clear context
- `GET /api/health` - Health check

## How It Works

1. User types message in GUI → JavaScript sends to `/api/chat`
2. Flask receives → passes to `discovery_coach.py`
3. LangChain retrieval chain invokes GPT-4 with RAG
4. Response sent back to GUI → displayed to user

The **actual coaching intelligence** comes from your Python backend with:
- System prompts
- RAG knowledge base (Epic/Feature templates)
- GPT-4o-mini
- Conversation history
