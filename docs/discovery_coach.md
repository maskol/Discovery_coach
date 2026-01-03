# Discovery Coach - Complete Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture & Design](#architecture--design)
3. [Technology Stack](#technology-stack)
4. [Code Structure](#code-structure)
5. [Frontend GUI](#frontend-gui)
6. [Backend API](#backend-api)
7. [Discovery Coach Engine](#discovery-coach-engine)
8. [Prompt Files & Questionnaires](#prompt-files--questionnaires)
9. [System Design Flow](#system-design-flow)
10. [User Guide](#user-guide)
11. [Configuration & Setup](#configuration--setup)
12. [API Reference](#api-reference)

---

## Overview

**Discovery Coach** is an intelligent SAFe (Scaled Agile Framework) coaching application that helps Product Managers, Epic Owners, and Product Leaders create well-defined Epic Hypothesis Statements, Features, and PI Objectives through Socratic discovery coaching.

### Key Capabilities
- **Web-Based GUI**: Modern HTML/CSS/JavaScript interface with real-time chat
- **Socratic Discovery Coaching**: Guides users through strategic questioning (WHO/WHAT/WHY/IMPACT)
- **RAG-Enhanced Coaching**: Uses Retrieval-Augmented Generation to ground advice in organizational knowledge
- **Conversation Memory**: Maintains chat history to build understanding progressively
- **Persistent Active Context**: Epic/Feature/PI Objectives remain active across conversation
- **Session Management**: Save and load conversation sessions with full context
- **Input History**: Arrow key navigation through previous inputs (terminal-like UX)
- **SMART Objectives**: Enforces Specific, Measurable, Achievable, Relevant, Time-bound criteria
- **Customer Segmentation**: Detailed customer segment definition (B2B/B2C, demographics, geography, psychographics)
- **External Prompt Management**: All system instructions and help content in editable .txt files

### Technology Stack
- **Frontend**: HTML5, CSS3, JavaScript (vanilla, no frameworks)
- **Backend**: FastAPI with Pydantic validation
- **LLM Framework**: LangChain 1.1.2
- **Language Model**: OpenAI GPT-4o-mini (temperature 0.7)
- **Vector Database**: Chroma with text-embedding-3-small
- **Python**: 3.13
- **Server**: Uvicorn (ASGI server)
- **Port**: 8050 (configurable)

---

## Architecture & Design

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    WEB BROWSER (USER)                           │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │  index.html (GUI Structure)                              │ │
│  │  - Chat interface, sidebar, modals                        │ │
│  │  - Active context display                                 │ │
│  │  - Action buttons (Evaluate, Outline, Save/Load)         │ │
│  └────────────────────────┬──────────────────────────────────┘ │
│  ┌────────────────────────▼──────────────────────────────────┐ │
│  │  styles.css (Styling)                                     │ │
│  │  - Gradient backgrounds, animations                        │ │
│  │  - Responsive layout                                       │ │
│  └───────────────────────────────────────────────────────────┘ │
│  ┌────────────────────────┬──────────────────────────────────┐ │
│  │  script.js (Frontend Logic)                              │ │
│  │  - State management (Epic, Feature, history)              │ │
│  │  - API communication (fetch to FastAPI)                   │ │
│  │  - Input history (arrow keys)                             │ │
│  │  - Session save/load (JSON export/import)                 │ │
│  └────────────────────────┬──────────────────────────────────┘ │
└─────────────────────────┬─│─────────────────────────────────────┘
                          │ │
                    HTTP  │ │  POST/GET
                    8050  │ │
                          ▼ ▼
┌─────────────────────────────────────────────────────────────────┐
│            FASTAPI SERVER (app.py) - Port 8050                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  API Endpoints                                           │  │
│  │  - POST /api/chat         → Send message, get response   │  │
│  │  - POST /api/evaluate     → Evaluate Epic/Feature        │  │
│  │  - POST /api/outline      → Get current content          │  │
│  │  - POST /api/clear        → Clear context                │  │
│  │  - GET  /api/health       → Health check                 │  │
│  │  - GET  /docs             → Auto-generated API docs      │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Pydantic Models (Request Validation)                    │  │
│  │  - ChatRequest, EvaluateRequest, OutlineRequest          │  │
│  │  - ClearRequest                                           │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Active Context (Global State)                           │  │
│  │  {                                                        │  │
│  │    "epic": "<content>",                                   │  │
│  │    "feature": "<content>",                                │  │
│  │    "chat_history": [HumanMessage, AIMessage, ...]        │  │
│  │  }                                                        │  │
│  └────────────────────┬─────────────────────────────────────┘  │
└───────────────────────┼─────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│        DISCOVERY COACH ENGINE (discovery_coach.py)              │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  RAG Chain Components                                    │  │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────────┐  │  │
│  │  │ ChatOpenAI   │  │ Embeddings   │  │  Retriever    │  │  │
│  │  │ gpt-4o-mini  │  │ text-embed-  │  │  (k=6 docs)   │  │  │
│  │  │ temp=0.7     │  │ 3-small      │  │               │  │  │
│  │  └──────────────┘  └──────────────┘  └───────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Chroma Vector Store                                     │  │
│  │  - Directory: ./rag_db (persisted)                       │  │
│  │  - Knowledge Base: ./knowledge_base/*.txt                │  │
│  │  - Chunks: 1000 chars, 200 overlap                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Prompt Management                                       │  │
│  │  - Load from ./prompt_help/*.txt files                   │  │
│  │  - ChatPromptTemplate with MessagesPlaceholder           │  │
│  │  - System + Context + History + User input              │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────────┐
│              PROMPT FILES (./prompt_help/)                      │
│  - system_prompt.txt           → Core coaching philosophy       │
│  - epic_questionnaire.txt      → Epic structure guide          │
│  - feature_questionnaire.txt   → Feature structure guide       │
│  - pi_objectives_questionnaire.txt → PI Objectives (SMART)     │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
1. User types message in browser
   ↓
2. script.js captures input, adds to history (arrow key support)
   ↓
3. POST /api/chat → FastAPI endpoint
   {
     "message": "user question",
     "activeEpic": "...",
     "activeFeature": "..."
   }
   ↓
4. app.py updates active_context, builds context prefix
   ↓
5. Retriever queries Chroma for relevant docs (k=6)
   ↓
6. Chain invokes LLM with:
   - user_input: full query with context prefix
   - context: retrieved documents
   - chat_history: previous messages (HumanMessage, AIMessage pairs)
   ↓
7. GPT-4o-mini generates response using:
   - system_prompt.txt (Socratic discovery coaching rules)
   - Retrieved knowledge base context
   - Full conversation history
   ↓
8. Response returned to frontend
   ↓
9. Chat history updated (both frontend and backend)
   ↓
10. Display in chat UI, scroll to bottom
```

---

## Technology Stack

### Frontend
- **HTML5**: Semantic structure, accessibility
- **CSS3**: Gradients, animations, flexbox layout
- **JavaScript (ES6+)**: 
  - Async/await for API calls
  - State management
  - Event handling
  - Session storage (JSON export/import)
  - Input history navigation

### Backend
- **FastAPI**: Modern Python web framework
  - Automatic API documentation (`/docs`)
  - Pydantic data validation
  - Type hints throughout
  - Async endpoint support
- **Uvicorn**: ASGI server for FastAPI
- **CORS Middleware**: Cross-origin request support

### AI/ML
- **LangChain 1.1.2**: 
  - Modern pipe syntax (`prompt | llm`)
  - ChatPromptTemplate with MessagesPlaceholder
  - Document loaders and text splitters
- **OpenAI GPT-4o-mini**: Cost-effective, fast
- **Chroma**: Open-source vector database
- **OpenAI Embeddings**: text-embedding-3-small

---

## Code Structure

```
Discovery_coach/
├── index.html                    # Main GUI structure
├── styles.css                    # All styling and animations
├── script.js                     # Frontend logic and API calls
├── app.py                        # FastAPI server
├── discovery_coach.py            # Core RAG engine
├── BACKEND_SETUP.md              # Installation instructions
├── FASTAPI_MIGRATION.md          # Migration notes
├── prompt_help/                  # External prompt files
│   ├── system_prompt.txt         # Core coaching rules
│   ├── epic_questionnaire.txt    # Epic structure
│   ├── feature_questionnaire.txt # Feature structure
│   └── pi_objectives_questionnaire.txt  # PI Objectives
├── knowledge_base/               # Organization knowledge (.txt files)
│   └── *.txt                     # SAFe guidelines, templates
├── rag_db/                       # Chroma vector database (auto-created)
└── Documentation/
    └── discovery_coach.md        # This file
```

---

## Frontend GUI

### Components

**index.html** - Main structure with:
- Header with title and description
- Sidebar:
  - Active Context display (Epic, Feature)
  - Action buttons (Evaluate, Outline)
  - Context Management (New, Clear)
  - Session Management (Save, Load)
  - Help button
- Chat area:
  - Messages container
  - Status bar
  - Input form with text field and send button
- Help modal

**styles.css** - Styling includes:
- Gradient background animations
- Message bubbles (user, agent, system)
- Sidebar sections with hover effects
- Modal overlays
- Responsive layout
- Smooth transitions

**script.js** - Frontend logic:

```javascript
// State Management
const state = {
    activeEpic: null,
    activeFeature: null,
    conversationHistory: [],
    isLoading: false,
    inputHistory: [],      // For arrow key navigation
    historyIndex: -1
};

// Key Functions:
- sendMessage(event)           // Handle form submission
- simulateCoachResponse(msg)   // API call to /api/chat
- evaluateEpic/Feature()       // Load content for evaluation
- outlineEpic/Feature()        // Display current content
- newEpic/Feature()            // Clear specific context
- clearAll()                   // Reset everything
- saveSession()                // Export to JSON file
- loadSession()                // Import from JSON file
- Arrow key handler           // Navigate input history
```

### Features

1. **Input History Navigation**:
   - Arrow Up: Previous input
   - Arrow Down: Next input or clear
   - Prevents duplicate consecutive entries

2. **Session Management**:
   - Save: Downloads JSON with full state
   - Load: Restores conversation and context
   - Includes timestamp for tracking

3. **Real-time Feedback**:
   - Status updates ("Coach is thinking...")
   - Button disable during processing
   - Auto-scroll to latest message

---

## Backend API

### app.py - FastAPI Server

**Port**: 8050 (configurable)

**Endpoints**:

```python
POST /api/chat
  Request: { message, activeEpic?, activeFeature? }
  Response: { response, success }
  
POST /api/evaluate
  Request: { type: "epic"|"feature", content }
  Response: { response, success, activeContext }
  
POST /api/outline
  Request: { type: "epic"|"feature" }
  Response: { content, success } or { message, success }
  
POST /api/clear
  Request: { type: "epic"|"feature"|"all" }
  Response: { success, message, activeContext }
  
GET /api/health
  Response: { status, service }
  
GET /docs
  Auto-generated interactive API documentation
```

**Key Features**:
- Pydantic models for request validation
- Global active_context state
- Chat history persistence
- HTTPException for error handling
- CORS middleware for frontend access

---

## Discovery Coach Engine

### discovery_coach.py

**Core Functions**:

```python
def build_or_load_vectorstore(knowledge_dir, persist_dir)
    # Creates or loads Chroma vector database
    # Chunks documents (1000 chars, 200 overlap)
    # Persists to disk for fast subsequent loads
    
def build_epic_pm_coach_with_rag(knowledge_dir, persist_dir)
    # Creates the RAG chain
    # Returns (chain, retriever)
    # Loads system_prompt.txt
    # Creates ChatPromptTemplate with history support
    
def initialize_vector_store()
    # Module-level initialization for API use
    # Lazy loading pattern
    
def get_retrieval_chain()
    # Returns initialized chain
```

**Active Context Structure**:
```python
active_context = {
    "epic": None,           # Epic content string
    "feature": None,        # Feature content string
    "chat_history": []      # List of HumanMessage/AIMessage
}
```

**RAG Chain**:
```python
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("system", "Content from internal documents:\n{context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{user_input}")
])

chain = prompt | llm
retriever = vectorstore.as_retriever(search_kwargs={"k": 6})
```

---

## Prompt Files & Questionnaires

### system_prompt.txt

**Philosophy**: Socratic Discovery Coach

**Key Sections**:
1. **Coaching Philosophy**:
   - Discovery coach, not solution provider
   - Guide through questions, not answers
   - Build understanding progressively
   - Train in strategic/creative thinking

2. **Important Rules**:
   - Review conversation history first
   - Never re-ask answered questions
   - Synthesize all previous answers
   - Challenge vague statements

3. **Conversation Style**:
   - NEVER jump to solutions in first 4-6 exchanges
   - Primary mode: ASKING QUESTIONS
   - Use Socratic method
   - 5-phase discovery: WHO → WHAT → WHY → IMPACT → CREATIVE EXPLORATION

4. **WHO (Customer Segment Discovery)**:
   - B2B or B2C?
   - Industry, role, context?
   - Geographic location?
   - How many affected?
   - What do they value/frustrates them?

5. **WHAT (Problem Discovery)**:
   - Specific problems occurring?
   - Evidence of the problem?
   - Frequency and severity?
   - Symptoms vs root causes?

6. **WHY (Root Cause Discovery)**:
   - Underlying causes?
   - Technical/process/organizational factors?
   - Assumptions to test?

7. **IMPACT (Business Impact Discovery)**:
   - Business metrics?
   - Current baseline vs target?
   - Risks if not solved?

8. **CREATIVE EXPLORATION**:
   - Alternative solutions considered?
   - What if budget unlimited?
   - What would competitor do?

### epic_questionnaire.txt

**Sections**:
1. Epic Name
2. Problem/Opportunity
3. **Target Customers/Users** (Enhanced):
   - Customer Type (B2B/B2C/Internal/Partners)
   - Demographics (age, industry, company size, role)
   - Geographic Location (country, region, urban/rural)
   - Behavioral Characteristics (usage patterns, tech-savviness)
   - Psychographics (pain points, motivations, goals)
   - Quantitative Details (user count, market size, growth)
   - Current Context (workflow, tools used)
4. Business Outcome (MUST BE MEASURABLE)
5. Leading Indicators
6. Non-Functional Requirements
7. Epic Hypothesis Statement (structured format)
8. Constraints/Risks

### feature_questionnaire.txt

Standard Feature structure with benefit hypothesis and acceptance criteria.

### pi_objectives_questionnaire.txt

**Key Updates**:
- **PI Context**: 10 weeks dev + 3 weeks planning/innovation
- **Feature Timing**: Average 3-5 weeks per feature
- **SMART Criteria**: Explicit definition
  - Specific, Measurable, Achievable, Relevant, Time-bound
- **Parent Epic & Features**: Traceability
- **Key Results**: Tied to specific Features with timing

**Structure**:
1. Objective Name (reflects Features from Epic)
2. Parent Epic(s) & Features (traceability)
3. Business Value/Strategic Theme
4. Measurable Success Criteria (SMART, 10-week timeframe)
5. Key Results (3-5 items, linked to Features)
6. Dependencies & Constraints
7. Leading Indicators

---

## System Design Flow

### Conversation Flow with Discovery Coaching

```
1. User: "I have customers with bad connectivity"
   ↓
2. Agent: WHO questions
   - "Who specifically are these customers? B2B or B2C?"
   - "What's their geographic location?"
   - "How many customers affected?"
   ↓
3. User answers: "B2C in northern Sweden, 15,000 users"
   ↓
4. Agent: WHAT questions
   - "What specific problems are occurring?"
   - "What evidence do you have?"
   - "How frequently does this happen?"
   ↓
5. User answers: "Video freezes, dropped calls, 300 complaints/week"
   ↓
6. Agent: WHY questions
   - "Why do you think this is happening?"
   - "Have you investigated technical factors?"
   ↓
7. User answers: "Weak 3G coverage, no fiber"
   ↓
8. Agent: IMPACT questions
   - "How does this affect business metrics?"
   - "What's current NPS? Target?"
   ↓
9. User answers: "NPS -10, want +30. Churn 30%, want 5%"
   ↓
10. Agent: CREATIVE EXPLORATION
    - "What solutions have you considered?"
    - "If budget unlimited, what would you do?"
    ↓
11. User answers: "5G SA deployment with specific hardware"
    ↓
12. Agent: Sufficient discovery completed
    - "We now have strong understanding. Would you like me to draft an Epic?"
    ↓
13. User: "Yes, outline epic"
    ↓
14. Agent: Creates Epic with all gathered details
    - Epic Name: "Rural Connectivity Enhancement..."
    - Target Customers: "B2C in Norrbotten, Västerbotten, 15,000 users..."
    - Business Outcomes: "NPS from -10 to +30, churn from 30% to 5%..."
    - etc.
```

### Session Save/Load Flow

```
Save:
1. User clicks "💾 Save Session"
2. JavaScript collects:
   - state.activeEpic
   - state.activeFeature
   - state.conversationHistory
   - messages HTML
   - timestamp
3. Creates JSON blob
4. Downloads as discovery-coach-session-YYYY-MM-DD.json

Load:
1. User clicks "📂 Load Session"
2. File picker opens
3. User selects .json file
4. JavaScript parses JSON
5. Restores:
   - state variables
   - messages HTML
   - active context display
6. Clears backend state
7. Shows confirmation with original timestamp
```

---

## User Guide

### Getting Started

1. **Install Dependencies**:
   ```bash
   pip install fastapi uvicorn
   ```

2. **Configure Python Environment**:
   ```bash
   source /path/to/.venv/bin/activate
   ```

3. **Start Server**:
   ```bash
   cd Discovery_coach
   python app.py
   ```
   Server starts on http://localhost:8050

4. **Open GUI**:
   - Open `index.html` in browser
   - Or visit http://localhost:8050/docs for API docs

### Workflow

1. **Discovery Phase**:
   - Start conversation: "I have customers with..."
   - Answer agent's WHO/WHAT/WHY/IMPACT questions
   - Build understanding through 5-8 exchanges

2. **Content Creation**:
   - Request outline: "outline epic"
   - Agent synthesizes all discovery into structured Epic
   - Review and refine through conversation

3. **Evaluation**:
   - Click "Evaluate Epic" to load existing content
   - Agent evaluates against SAFe best practices
   - Provides structured feedback

4. **Session Management**:
   - Save work: Click "💾 Save Session"
   - Resume later: Click "📂 Load Session"
   - Share: Send .json file to colleagues

### Commands

- **outline epic** - Display current Epic
- **outline feature** - Display current Feature
- **outline pi objectives** - Display PI Objectives template
- **new epic** - Clear Epic context
- **new feature** - Clear Feature context
- **help** - Show help modal

### Tips

- Use ↑/↓ arrows to navigate input history
- Agent won't jump to solutions—answer discovery questions first
- Be specific with numbers, segments, metrics
- Save sessions frequently during long discovery
- Backend maintains full conversation history

---

## Configuration & Setup

### Environment Variables

Create `.env` file:
```
OPENAI_API_KEY=sk-...
```

### Port Configuration

Change port in `app.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8050, log_level="info")
```

And in `script.js`:
```javascript
const response = await fetch('http://localhost:8050/api/chat', {
```

### Knowledge Base

Add organization-specific files to `knowledge_base/`:
- SAFe guidelines
- Epic templates
- Feature examples
- PI planning documentation

Files are auto-indexed on first run.

### Prompt Customization

Edit files in `prompt_help/`:
- `system_prompt.txt` - Core coaching behavior
- `epic_questionnaire.txt` - Epic structure
- `feature_questionnaire.txt` - Feature structure
- `pi_objectives_questionnaire.txt` - PI Objectives

Changes take effect on server restart.

---

## API Reference

### POST /api/chat

**Request**:
```json
{
  "message": "What should I focus on for the Epic?",
  "activeEpic": "Epic content...",
  "activeFeature": "Feature content..."
}
```

**Response**:
```json
{
  "response": "Let's explore the customer segment first...",
  "success": true
}
```

### POST /api/evaluate

**Request**:
```json
{
  "type": "epic",
  "content": "Epic: Improve Connectivity\nFor customers in rural areas..."
}
```

**Response**:
```json
{
  "response": "Evaluation against SAFe practices:\n...",
  "success": true,
  "activeContext": { "epic": "...", "feature": null }
}
```

### POST /api/outline

**Request**:
```json
{
  "type": "epic"
}
```

**Response**:
```json
{
  "content": "Epic content...",
  "success": true
}
```

Or if no content:
```json
{
  "message": "No active Epic. Use 'Evaluate Epic' to load one.",
  "success": true,
  "content": null
}
```

### POST /api/clear

**Request**:
```json
{
  "type": "all"
}
```

**Response**:
```json
{
  "success": true,
  "message": "All context cleared",
  "activeContext": { "epic": null, "feature": null, "chat_history": [] }
}
```

### GET /api/health

**Response**:
```json
{
  "status": "healthy",
  "service": "Discovery Coach API"
}
```

---

## Troubleshooting

**Issue**: "Cannot connect to Discovery Coach backend"
- **Fix**: Start server with `python app.py`
- **Check**: http://localhost:8050/api/health

**Issue**: Import errors
- **Fix**: `pip install fastapi uvicorn langchain langchain-openai langchain-community chromadb`

**Issue**: OpenAI API errors
- **Fix**: Check `.env` file has valid `OPENAI_API_KEY`

**Issue**: Chat history not maintained
- **Fix**: Restart server to clear corrupted state
- **Check**: Backend logs for exceptions

**Issue**: Session load fails
- **Fix**: Ensure JSON file matches expected format
- **Check**: Browser console for parsing errors

---

## Summary

**Discovery Coach** is a comprehensive SAFe coaching system combining:

1. **Modern Web Architecture**: FastAPI + HTML/CSS/JS
2. **Socratic Discovery**: WHO/WHAT/WHY/IMPACT/CREATIVE questioning
3. **RAG-Enhanced**: Grounded in organizational knowledge
4. **Conversation Memory**: Progressive understanding building
5. **SMART Objectives**: Enforced measurability and time-bounds
6. **Detailed Segmentation**: Customer demographics, geography, psychographics
7. **Session Persistence**: Save/load full conversation state
8. **Epic-Feature-PI Traceability**: Clear hierarchy and relationships

### Key Differentiators

- **No premature solutions**: 4-6 exchanges of discovery before offering Epics
- **Question-first coaching**: Builds user's strategic thinking skills
- **Progressive discovery**: Each phase builds on previous (WHO → WHAT → WHY → IMPACT)
- **External prompts**: Non-programmers can update coaching behavior
- **Session management**: Resume work across days/weeks
- **Input history**: Terminal-like UX for productivity
- **Automatic API docs**: FastAPI generates interactive docs at `/docs`

### Architecture Highlights

```
Browser (GUI) 
    ↓ HTTP/JSON
FastAPI (Validation, State Management)
    ↓
Discovery Coach (RAG Chain)
    ↓
GPT-4o-mini + Chroma (AI + Knowledge Base)
    ↓
System Prompt (Socratic Coaching Rules)
    ↓
Strategic Questions → Discovery → Synthesis → Epic/Feature
```

The system elegantly separates concerns:
- **Frontend**: User interaction, state, session management
- **Backend API**: Request validation, context management
- **Engine**: RAG, LLM, conversation memory
- **Prompts**: Coaching philosophy, questionnaires

Result: A maintainable, flexible coaching application that guides users to create rigorous, measurable SAFe artifacts through thoughtful discovery.
