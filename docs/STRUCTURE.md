# Discovery Coach - Project Structure

## Overview

The Discovery Coach project follows a clean, modular structure that separates concerns and makes the codebase easy to navigate and maintain.

## Directory Layout

```
Discovery_coach/
├── backend/                     # Python backend code
│   ├── app.py                  # FastAPI server (530+ lines)
│   ├── discovery_coach.py      # RAG core logic (136 lines)
│   └── __init__.py             # Python package marker
│
├── frontend/                    # Web user interface
│   ├── index.html              # Main GUI structure
│   ├── script.js               # Frontend logic (~943 lines)
│   └── styles.css              # Styling and layout
│
├── scripts/                     # Utility shell scripts
│   ├── start.sh                # Start server (main script)
│   ├── stop.sh                 # Stop server
│   ├── status.sh               # Check server status
│   └── reset_knowledge.sh      # Rebuild RAG database
│
├── data/                        # Application data
│   ├── knowledge_base/         # RAG source documents
│   │   ├── epic_template.txt
│   │   ├── feature_template.txt
│   │   ├── guidelines_epic_vs_feature.txt
│   │   ├── product_operating_model.txt
│   │   ├── telecom_examples_epics_and_features.txt
│   │   └── lean_business_case.txt
│   │
│   ├── prompt_help/            # System prompts
│   │   ├── system_prompt.txt
│   │   ├── epic_questionnaire.txt
│   │   ├── feature_questionnaire.txt
│   │   └── pi_objectives_questionnaire.txt
│   │
│   └── Session_storage/        # Saved sessions
│       └── session-*.json
│
├── docs/                        # Documentation
│   ├── README.md               # Documentation index
│   ├── STRUCTURE.md            # This file
│   ├── BACKEND_SETUP.md        # Backend configuration
│   ├── 03-FEATURES.md          # Features documentation
│   ├── 04-API-REFERENCE.md     # API endpoints
│   ├── CHANGELOG.md            # Version history
│   └── discovery_coach.md      # Original design docs
│
├── rag_db/                      # Vector database (auto-generated)
│   └── chroma.sqlite3          # ChromaDB storage (~164KB)
│
├── venv/                        # Python virtual environment
│   └── (Python 3.13 packages)
│
├── README.md                    # Project overview
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables (not in git)
├── .gitignore                   # Git ignore rules
│
└── start.sh, stop.sh, status.sh # Root convenience scripts
```

## Module Responsibilities

### Backend (`backend/`)

#### `app.py` - FastAPI Server
- **Lines**: ~530
- **Purpose**: REST API server and request handling
- **Key Functions**:
  - `POST /api/chat` - Main chat endpoint with RAG
  - `POST /api/evaluate` - Epic/Feature evaluation
  - `POST /api/session/save` - Save conversation sessions
  - `POST /api/session/load` - Load saved sessions
  - `GET /api/session/list` - List all sessions
  - `DELETE /api/session/delete` - Delete sessions
  - Auto-detection of Epic/Feature content
  - Chat history management (limited to 10 messages)
  - Summary optimization (skips RAG retrieval)

#### `discovery_coach.py` - RAG Core
- **Lines**: ~136
- **Purpose**: Vector store initialization and RAG logic
- **Key Functions**:
  - `load_prompt_file()` - Load prompts from data/prompt_help
  - `build_or_load_vectorstore()` - Create/load ChromaDB
  - `initialize_vector_store()` - Setup LLM chain with RAG
  - Global `active_context` dictionary
- **Configuration**:
  - Embedding model: text-embedding-3-small
  - Chunk size: 1000 chars
  - Chunk overlap: 200 chars
  - Retriever k: 6 documents

### Frontend (`frontend/`)

#### `index.html`
- Main GUI structure
- Chat interface
- Session management UI
- Model/temperature controls
- Draft/outline/evaluate buttons

#### `script.js`
- **Lines**: ~943
- **Key Features**:
  - `fetchWithTimeout()` wrapper (30-180s timeouts)
  - Message sending and display
  - Session save/load/delete operations
  - Epic/Feature drafting and evaluation
  - Summary generation (optimized)
  - Markdown rendering

#### `styles.css`
- Modern, clean styling
- Responsive layout
- Button states and animations
- Chat message formatting

### Scripts (`scripts/`)

#### `start.sh`
- Comprehensive startup script
- Activates virtual environment
- Checks port availability
- Starts FastAPI server (backend/app.py)
- Opens GUI in default browser
- Handles graceful shutdown

#### `stop.sh`
- Stops server on port 8050
- Force kills if necessary
- Verification of shutdown

#### `status.sh`
- Shows server status
- Displays RAG database size
- Counts saved sessions

#### `reset_knowledge.sh`
- Deletes and rebuilds RAG database
- Reloads knowledge_base documents

### Data (`data/`)

#### `knowledge_base/`
- **7 source documents** for RAG
- Epic and Feature templates
- Guidelines and examples
- Organizational methodology
- **Total size**: ~30KB text

#### `prompt_help/`
- System prompt for coaching behavior
- Questionnaires for different workflows
- Help text and instructions

#### `Session_storage/`
- JSON files with conversation history
- Includes Epic/Feature/PI Objectives
- Timestamp-based filenames
- Format: `session-YYYY-MM-DD-HH-MM-SS.json`

## Key Design Decisions

### 1. Backend/Frontend Separation
- Clean API boundary via REST endpoints
- Frontend can be deployed separately
- Easy to test backend independently

### 2. Data Isolation
- All data in `data/` directory
- Easy backup: just copy data/
- Knowledge base separate from code

### 3. Scripts Organization
- All utilities in `scripts/`
- Root-level convenience wrappers
- Makes automation easier

### 4. Path Resolution
All backend code uses project-relative paths:
```python
project_root = os.path.dirname(os.path.dirname(__file__))
data_path = os.path.join(project_root, "data", "knowledge_base")
```

### 5. Documentation
- Separate `docs/` directory
- Focused, modular documentation
- Easy to find specific topics

## File Paths in Code

### Backend References
```python
# discovery_coach.py
project_root = os.path.dirname(os.path.dirname(__file__))
prompt_path = os.path.join(project_root, "data", "prompt_help", filename)

# app.py
project_root = os.path.dirname(os.path.dirname(__file__))
session_dir = os.path.join(project_root, "data", "Session_storage")
```

### Script References
```bash
# start.sh
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"
python backend/app.py
```

## Benefits of This Structure

1. **Clear Organization**: Each directory has a single responsibility
2. **Easy Navigation**: Find files quickly by category
3. **Scalability**: Easy to add new features or modules
4. **Maintainability**: Related code is grouped together
5. **Documentation**: Dedicated docs/ directory
6. **Deployment**: Backend/frontend can be deployed separately
7. **Data Management**: All data in one place (data/)
8. **Version Control**: Easy to see what changed in git

## Migration from Old Structure

The project was reorganized on December 8, 2025:

**Old Structure** (flat):
```
app.py, discovery_coach.py (root)
index.html, script.js, styles.css (root)
start.sh, stop.sh, status.sh (root)
knowledge_base/, prompt_help/, Session_storage/ (root)
Documentation/ (root)
```

**New Structure** (organized):
```
backend/ - Python code
frontend/ - Web UI
scripts/ - Shell scripts
data/ - All data files
docs/ - Documentation
```

All path references were updated to maintain functionality.
