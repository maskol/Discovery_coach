# Discovery Coach - API Reference

## Base URL
```
http://localhost:8050
```

## Authentication
Currently no authentication required (local development).

---

## Endpoints

### Health Check

**GET** `/api/health`

**Description:** Check if the server is running and responsive.

**Response:**
```json
{
  "status": "healthy"
}
```

**Example:**
```bash
curl http://localhost:8050/api/health
```

---

### Chat

**POST** `/api/chat`

**Description:** Send a message and get AI coach response with RAG context.

**Timeout:** 120 seconds (frontend), 60 seconds (LLM API call)

**Request Body:**
```json
{
  "message": "string (required)",
  "activeEpic": "string | null (optional)",
  "activeFeature": "string | null (optional)",
  "model": "string (optional, default: gpt-4o-mini)",
  "temperature": "number (optional, default: 0.7, range: 0.0-2.0)"
}
```

**Behavior:**
- Regular messages: Uses RAG retrieval (6 docs, ~5KB context)
- Summary requests: Skips RAG for performance
- Chat history: Limited to last 10 messages (0 for summaries)
- Auto-detects and stores Epic/Feature content

**Model Options:**
- `gpt-4o-mini` (default)
- `gpt-4o`
- `gpt-4-turbo`
- `gpt-3.5-turbo`
- `o1`

**Temperature Range:** 0.0 - 2.0

**Response:**
```json
{
  "response": "string",
  "success": true
}
```

**Auto-Detection Side Effects:**
- If response contains Epic structure → stores in `active_context["epic"]`
- If response contains Feature structure → stores in `active_context["feature"]`
- If response contains PI Objectives → stores in `active_context["pi_objectives"]`

**Example:**
```bash
curl -X POST http://localhost:8050/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I have B2C customers in remote areas with connectivity problems",
    "model": "gpt-4o-mini",
    "temperature": 0.7
  }'
```

**Detection Patterns:**

Epic Detection:
```
("EPIC NAME" OR "1. EPIC NAME") 
AND 
("EPIC HYPOTHESIS STATEMENT" OR "BUSINESS CONTEXT")
```

Feature Detection:
```
("FEATURE NAME" OR "Feature Name:") 
AND 
("USER STORY" OR "ACCEPTANCE CRITERIA")
```

PI Objectives Detection:
```
"PI OBJECTIVE" OR "Program Increment Objective"
```

---

### Evaluate Epic/Feature

**POST** `/api/evaluate`

**Description:** Evaluate Epic or Feature content against SAFe best practices.

**Request Body:**
```json
{
  "type": "epic | feature (required)",
  "content": "string (required)"
}
```

**Response:**
```json
{
  "response": "string (evaluation feedback)",
  "success": true,
  "activeContext": {
    "epic": "string | null",
    "feature": "string | null",
    "pi_objectives": "string | null"
  }
}
```

**Side Effects:**
- Stores content in `active_context["epic"]` or `active_context["feature"]`
- Content becomes active for subsequent chat messages

**Example:**
```bash
curl -X POST http://localhost:8050/api/evaluate \
  -H "Content-Type: application/json" \
  -d '{
    "type": "epic",
    "content": "For B2C customers who experience connectivity issues..."
  }'
```

---

### Outline Epic/Feature

**POST** `/api/outline`

**Description:** Retrieve currently active Epic or Feature content.

**Request Body:**
```json
{
  "type": "epic | feature (required)"
}
```

**Response (Content Available):**
```json
{
  "content": "string",
  "success": true
}
```

**Response (No Content):**
```json
{
  "message": "No active Epic/Feature. Use \"Evaluate\" to load one.",
  "success": true,
  "content": null
}
```

**Example:**
```bash
curl -X POST http://localhost:8050/api/outline \
  -H "Content-Type: application/json" \
  -d '{"type": "epic"}'
```

---

### Clear Context

**POST** `/api/clear`

**Description:** Clear active Epic, Feature, or all context.

**Request Body:**
```json
{
  "type": "epic | feature | all (required)"
}
```

**Response:**
```json
{
  "message": "Epic/Feature/All context cleared",
  "success": true
}
```

**Side Effects:**
- `epic`: Sets `active_context["epic"] = None`
- `feature`: Sets `active_context["feature"] = None`
- `all`: Clears epic, feature, and chat_history

**Example:**
```bash
curl -X POST http://localhost:8050/api/clear \
  -H "Content-Type: application/json" \
  -d '{"type": "all"}'
```

---

### Session Management

#### List Sessions

**GET** `/api/session/list`

**Description:** Get list of all saved sessions with metadata.

**Response:**
```json
{
  "success": true,
  "sessions": [
    {
      "filename": "session-2025-12-07-19-44-19.json",
      "modified": "2025-12-07T19:44:19.425514",
      "size": 45678
    }
  ]
}
```

**Example:**
```bash
curl http://localhost:8050/api/session/list
```

---

#### Save Session

**POST** `/api/session/save`

**Description:** Save current session to server-side JSON file.

**Request Body:**
```json
{
  "activeEpic": "string | null",
  "activeFeature": "string | null",
  "conversationHistory": [
    {"role": "user", "content": "..."},
    {"role": "agent", "content": "..."}
  ],
  "messages": "string (HTML)"
}
```

**Response:**
```json
{
  "success": true,
  "filename": "session-2025-12-07-19-44-19.json",
  "message": "Session saved successfully"
}
```

**File Location:** `Session_storage/session-YYYY-MM-DD-HH-MM-SS.json`

**File Contents:**
```json
{
  "activeEpic": "...",
  "activeFeature": "...",
  "piObjectives": null,
  "conversationHistory": [...],
  "messages": "<div>...</div>",
  "timestamp": "2025-12-07T19:44:19.425514"
}
```

**Example:**
```bash
curl -X POST http://localhost:8050/api/session/save \
  -H "Content-Type: application/json" \
  -d '{
    "activeEpic": null,
    "activeFeature": null,
    "conversationHistory": [],
    "messages": ""
  }'
```

---

#### Load Session

**POST** `/api/session/load`

**Description:** Load previously saved session and restore full context.

**Request Body:**
```json
{
  "filename": "session-2025-12-07-19-44-19.json"
}
```

**Response:**
```json
{
  "success": true,
  "session": {
    "activeEpic": "...",
    "activeFeature": "...",
    "piObjectives": null,
    "conversationHistory": [...],
    "messages": "...",
    "timestamp": "..."
  },
  "message": "Session loaded from session-2025-12-07-19-44-19.json"
}
```

**Side Effects:**
- Restores `active_context["epic"]`
- Restores `active_context["feature"]`
- Restores `active_context["pi_objectives"]`
- Converts conversationHistory to LangChain messages (HumanMessage/AIMessage)
- Restores `active_context["chat_history"]`

**Example:**
```bash
curl -X POST http://localhost:8050/api/session/load \
  -H "Content-Type: application/json" \
  -d '{"filename": "session-2025-12-07-19-44-19.json"}'
```

---

#### Delete Sessions

**POST** `/api/session/delete`

**Description:** Delete one or more session files.

**Request Body:**
```json
{
  "filenames": ["session-2025-12-07-19-44-19.json", "session-2025-12-06-10-30-00.json"]
}
```

**Response (All Deleted):**
```json
{
  "success": true,
  "message": "Successfully deleted 2 session(s)",
  "deleted": ["session-2025-12-07-19-44-19.json", "session-2025-12-06-10-30-00.json"]
}
```

**Response (Partial Success):**
```json
{
  "success": true,
  "message": "Deleted 1 session(s), 1 error(s)",
  "deleted": ["session-2025-12-07-19-44-19.json"],
  "errors": ["session-2025-12-06-10-30-00.json: File not found"]
}
```

**Response (All Failed):**
```json
{
  "success": false,
  "message": "No sessions were deleted",
  "errors": ["session-2025-12-07-19-44-19.json: File not found"]
}
```

**Example:**
```bash
curl -X POST http://localhost:8050/api/session/delete \
  -H "Content-Type: application/json" \
  -d '{"filenames": ["session-2025-12-07-19-44-19.json"]}'
```

---

## Request Models (Pydantic)

### ChatRequest
```python
class ChatRequest(BaseModel):
    message: str
    activeEpic: Optional[str] = None
    activeFeature: Optional[str] = None
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
```

### EvaluateRequest
```python
class EvaluateRequest(BaseModel):
    type: str  # "epic" or "feature"
    content: str
```

### OutlineRequest
```python
class OutlineRequest(BaseModel):
    type: str  # "epic" or "feature"
```

### ClearRequest
```python
class ClearRequest(BaseModel):
    type: str  # "epic", "feature", or "all"
```

### SessionSaveRequest
```python
class SessionSaveRequest(BaseModel):
    activeEpic: Optional[str] = None
    activeFeature: Optional[str] = None
    conversationHistory: list = []
    messages: str = ""
```

### SessionLoadRequest
```python
class SessionLoadRequest(BaseModel):
    filename: str
```

### SessionDeleteRequest
```python
class SessionDeleteRequest(BaseModel):
    filenames: List[str]
```

---

## Active Context Structure

The backend maintains a global `active_context` dictionary:

```python
active_context = {
    "epic": None | str,
    "feature": None | str,
    "pi_objectives": None | str,
    "chat_history": [HumanMessage(...), AIMessage(...), ...]
}
```

**Epic Example:**
```python
active_context["epic"] = """
EPIC NAME
Enhanced Connectivity Solutions for Remote B2C Customers

EPIC HYPOTHESIS STATEMENT
For B2C customers in remote areas
who experience connectivity issues during video meetings and document sharing
the Enhanced Connectivity Solutions Epic
is a 5G SA connectivity package with external antennas
that provides guaranteed uptime and bandwidth for work-from-home
unlike current ad-hoc connectivity support
our solution ensures reliable service with premium support and hardware installation
"""
```

**Chat History Example:**
```python
from langchain_core.messages import HumanMessage, AIMessage

active_context["chat_history"] = [
    HumanMessage(content="I have customers with connectivity problems"),
    AIMessage(content="Thank you for sharing. Can you tell me more about..."),
    HumanMessage(content="They are B2C customers in northern Sweden"),
    AIMessage(content="That's helpful context. What specific connectivity...")
]
```

---

## Error Responses

### 400 Bad Request
```json
{
  "detail": "No message provided"
}
```

### 404 Not Found
```json
{
  "detail": "Session file not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Auto-Generated API Documentation

FastAPI provides interactive API documentation at:

**Swagger UI:** http://localhost:8050/docs  
**ReDoc:** http://localhost:8050/redoc

These interfaces allow you to:
- Explore all endpoints
- View request/response schemas
- Test API calls directly from browser
- See example values
- Download OpenAPI spec

---

## CORS Configuration

The server allows all origins for development:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

For production, restrict to specific origins:

```python
allow_origins=["https://yourdomain.com"]
```

---

## Rate Limiting

Currently no rate limiting implemented. Consider adding for production:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/chat")
@limiter.limit("10/minute")
async def chat(request: ChatRequest):
    ...
```

---

## Logging

Server logs include:

**Startup:**
```
Initializing Discovery Coach...
Discovery Coach ready!

🎯 Discovery Coach FastAPI Server
==================================================
Server running on http://localhost:8050
Frontend should connect to http://localhost:8050/api/chat
API docs available at http://localhost:8050/docs
==================================================
```

**Auto-Detection:**
```
✅ Epic automatically detected and stored in active_context
✅ Feature automatically detected and stored in active_context
✅ PI Objectives automatically detected and stored in active_context
```

**Requests:**
```
INFO:     127.0.0.1:54595 - "POST /api/chat HTTP/1.1" 200 OK
INFO:     127.0.0.1:54601 - "POST /api/session/save HTTP/1.1" 200 OK
INFO:     127.0.0.1:55033 - "GET /api/session/list HTTP/1.1" 200 OK
```

**Errors:**
```
Error in chat endpoint: <error message>
Error in outline endpoint: <error message>
```

---

## Testing Examples

### Complete Discovery Flow via API

```bash
# 1. Start conversation
curl -X POST http://localhost:8050/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I have customers with connectivity problems in remote areas"}'

# 2. Continue discovery
curl -X POST http://localhost:8050/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "They are B2C customers, around 300 complaints per week"}'

# 3. Draft Epic
curl -X POST http://localhost:8050/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Please draft the epic based on our discussion"}'

# 4. Retrieve Epic
curl -X POST http://localhost:8050/api/outline \
  -H "Content-Type: application/json" \
  -d '{"type": "epic"}'

# 5. Save session
curl -X POST http://localhost:8050/api/session/save \
  -H "Content-Type: application/json" \
  -d '{
    "activeEpic": "<epic content>",
    "conversationHistory": [...]
  }'

# 6. List sessions
curl http://localhost:8050/api/session/list

# 7. Load session
curl -X POST http://localhost:8050/api/session/load \
  -H "Content-Type: application/json" \
  -d '{"filename": "session-2025-12-07-19-44-19.json"}'
```

---

## WebSocket Support

Currently not implemented. All communication is via HTTP REST.

For real-time streaming responses, consider adding WebSocket endpoint:

```python
from fastapi import WebSocket

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        # Stream response chunks
        await websocket.send_text(chunk)
```
