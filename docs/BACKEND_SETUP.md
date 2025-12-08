# Discovery Coach - Backend API Setup

## Prerequisites

- Python 3.13+ (required for chromadb compatibility)
- Virtual environment: `venv/` in project root
- OpenAI API key in `.env` file
- ⚠️ **VPN must be disabled** for OpenAI API connectivity

## Install Required Packages

```bash
# Activate virtual environment first
source venv/bin/activate

# Install all dependencies
pip install -r requirements.txt
```

Key dependencies:
- `fastapi>=0.115.0` - Modern async web framework
- `uvicorn==0.38.0` - ASGI server with auto-reload
- `langchain==1.1.2` - LLM framework core
- `langchain-openai==1.1.0` - OpenAI integration
- `langchain-community` - Community integrations (Chroma)
- `chromadb>=1.0.0` - Vector database for RAG
- `openai>=1.109.1` - OpenAI API client
- `python-dotenv` - Environment variable management

## Start the Backend Server

### Using start script (recommended):
```bash
cd Discovery_coach
./start.sh
```

The script will:
1. Activate virtual environment
2. Check port 8050 availability
3. Start uvicorn server
4. Open default browser automatically

### Manual start:
```bash
source venv/bin/activate
uvicorn app:app --host 0.0.0.0 --port 8050
```

You should see:
```
🎯 Discovery Coach Starting...
==================================================
Server: http://localhost:8050
API Docs: http://localhost:8050/docs
Knowledge Base: ./knowledge_base
Vector DB: ./rag_db
==================================================
```

## Architecture

### Current Architecture (FastAPI + LangChain RAG)

```
┌─────────────────────────────────────────────┐
│  Frontend (index.html + script.js)          │
│  - User interface                           │
│  - Session management UI                    │
│  - Model/temperature controls               │
└──────────────────┬──────────────────────────┘
                   │ HTTP/JSON :8050
                   ▼
┌─────────────────────────────────────────────┐
│  app.py (FastAPI Server)                    │
│  - REST API endpoints                       │
│  - Request validation (Pydantic)            │
│  - Session save/load/delete                 │
│  - Auto-detection of Epics/Features         │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│  discovery_coach.py (Core Module)           │
│  - initialize_vector_store()                │
│  - load_prompt_file()                       │
│  - build_or_load_vectorstore()              │
│  - active_context (global state)            │
└──────────┬──────────────────┬───────────────┘
           │                  │
           ▼                  ▼
┌──────────────────┐  ┌──────────────────┐
│  LangChain RAG   │  │  Chroma Vector   │
│  - OpenAI GPT    │  │  Database        │
│  - System prompt │  │  - Embeddings    │
│  - Chat history  │  │  - Documents     │
└──────────────────┘  └──────────────────┘
```

### Module Responsibilities

**app.py (460 lines):**
- FastAPI application and CORS setup
- API endpoints: `/api/chat`, `/api/evaluate`, `/api/session/*`
- Request/response models (Pydantic)
- Session file management (JSON)
- Auto-detection of Epic/Feature content in responses
- Active context management

**discovery_coach.py (140 lines):**
- Vector store initialization and loading
- Prompt file loading from `prompt_help/`
- LangChain chain building (system prompt + RAG)
- Global state for API: `active_context`, `_chain`, `_retriever`
- Clean API module (no CLI code)

**Knowledge Base:**
- `knowledge_base/*.txt` - Templates and guidelines
- `prompt_help/system_prompt.txt` - Main coaching instructions
- `rag_db/` - Chroma vector database (auto-generated)

## API Endpoints

### Chat Endpoint
```http
POST /api/chat
Content-Type: application/json

{
  "message": "string",
  "activeEpic": "string (optional)",
  "activeFeature": "string (optional)",
  "model": "gpt-4o-mini (default)",
  "temperature": 0.7
}
```

### Session Management
```http
POST /api/session/save  - Save current session
POST /api/session/load  - Load existing session
GET  /api/sessions      - List all sessions
DELETE /api/session/delete - Delete session(s)
```

### Evaluation
```http
POST /api/evaluate
{
  "type": "epic" | "feature",
  "content": "string"
}
```

### Utility
```http
GET  /api/health - Health check
POST /api/clear  - Clear active context
```

View interactive API docs at: `http://localhost:8050/docs`

## How It Works

1. **User sends message** → Frontend POSTs to `/api/chat`
2. **FastAPI receives** → Validates request with Pydantic model
3. **Context building** → Combines active Epic/Feature with user message
4. **RAG retrieval** → Queries Chroma for relevant knowledge base content
5. **LLM invocation** → LangChain chain runs with:
   - System prompt (Socratic coaching instructions)
   - Retrieved context (templates, guidelines)
   - Chat history (conversation continuity)
   - User input
6. **Auto-detection** → Checks response for Epic/Feature patterns, stores if found
7. **Response** → JSON with LLM response text sent to frontend
8. **History update** → Conversation added to `active_context['chat_history']`

## Configuration

### Environment Variables (.env)
```bash
OPENAI_API_KEY=sk-...
```

### Server Configuration (app.py)
```python
HOST = "0.0.0.0"
PORT = 8050
KNOWLEDGE_DIR = "./knowledge_base"
PERSIST_DIR = "./rag_db"
SESSION_DIR = "./Session_storage"
```

### RAG Configuration (discovery_coach.py)
```python
EMBEDDING_MODEL = "text-embedding-3-small"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
RETRIEVER_K = 6  # Number of docs to retrieve
```

## Troubleshooting

### Issue: System Hangs / Infinite "Thinking..."

**Symptoms:**
- Frontend shows "Coach is thinking..." indefinitely
- No response after 60+ seconds
- Server logs show "About to call chain.invoke()..." but no completion

**Root Cause:** VPN interfering with OpenAI API connectivity

**Solution:**
```bash
# 1. Disable VPN
# 2. Restart server
./stop.sh && ./start.sh
# 3. Try request again
```

**Expected Behavior:**
- Regular queries: 2-4 seconds
- Summaries: 4-6 seconds
- RAG retrieval: <1 second

### Issue: Retriever Returns 0 Documents

**Symptoms:**
- Server logs show "Retriever returned 0 documents"
- Responses lack knowledge base context
- Context length: 0

**Root Cause:** Empty or corrupted vector database

**Solution:**
```bash
# Delete and rebuild RAG database
rm -rf rag_db/
./start.sh

# Should see during startup:
# "Building new vector store from knowledge base documents..."
# "100% |████████| 7/7 [00:00<00:00, 2833.99it/s]"
```

**Verification:**
```bash
# Check database was created
ls -lh rag_db/
# Should show: chroma.sqlite3 (~164KB)
```

### Issue: "Cannot connect to Discovery Coach backend"

**Symptoms:**
- Frontend shows connection error banner
- Cannot send messages
- Server not responding on port 8050

**Solution:**
```bash
# Check if server is running
lsof -i :8050 | grep LISTEN

# If no output, start server
./start.sh

# If port occupied by old process
./stop.sh && sleep 2 && ./start.sh
```

### Issue: OpenAI API Key Error

**Symptoms:**
- Error: "The api_key client option must be set"
- No API key found in logs

**Solution:**
```bash
# 1. Check .env file exists and has key
cat .env
# Should show: OPENAI_API_KEY='sk-proj-...'

# 2. Verify key loads correctly
source venv/bin/activate
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(f'Key: {bool(os.getenv(\"OPENAI_API_KEY\"))}')"
# Should print: Key: True

# 3. Restart server
./stop.sh && ./start.sh
```

### Issue: ChromaDB Deprecation Warning

**Symptoms:**
```
LangChainDeprecationWarning: The class `Chroma` was deprecated in LangChain 0.2.9
```

**Status:** Known issue, does not affect functionality

**Future Fix:**
```bash
pip install -U langchain-chroma
# Update imports in discovery_coach.py:
# from langchain_chroma import Chroma
```

### Performance Monitoring

**Check Server Logs:**
```bash
# Look for these metrics in terminal output:
Regular request - invoking retriever with query length: 187
Retriever returned 6 documents
Creating LLM instance...
System prompt loaded: 9412 chars
Invoking LLM with model=gpt-4o-mini, temp=0.7
Context length: 5291, History messages: 0
✓ LLM response received in 2.08s: 562 chars
```

**Expected Performance:**
- RAG retrieval: <1 second, 6 documents, ~5KB context
- LLM response: 2-6 seconds
- Total request time: 3-8 seconds

**Warning Signs:**
- Retriever timeout (>10 seconds)
- 0 documents retrieved
- Response time >60 seconds
- VPN enabled

## Troubleshooting

### Server won't start
```bash
# Check if port is in use
./status.sh

# Kill existing server
./stop.sh

# Restart
./start.sh
```

### Knowledge base not updating
```bash
# Reset vector database
./reset_knowledge.sh

# Restart server (will rebuild)
./start.sh
```

### Module import errors
```bash
# Verify virtual environment
source venv/bin/activate
which python  # Should show venv/bin/python

# Reinstall dependencies
pip install -r requirements.txt
```

### Session issues
```bash
# Check session directory exists
ls -la Session_storage/

# Validate JSON format
cat Session_storage/session-*.json | jq .
```
