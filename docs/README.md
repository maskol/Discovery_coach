# Discovery Coach Documentation

**Discovery Coach** is an intelligent SAFe (Scaled Agile Framework) coaching application that helps Product Managers, Epic Owners, and Product Leaders create well-defined Epic Hypothesis Statements, Features, and PI Objectives through Socratic discovery coaching.

## Documentation Structure

This documentation is split into focused modules for easier navigation and maintenance:

### Core Documentation
- **[01-OVERVIEW.md](01-OVERVIEW.md)** - System overview, capabilities, and use cases
- **[02-ARCHITECTURE.md](02-ARCHITECTURE.md)** - System architecture and design patterns
- **[03-FEATURES.md](03-FEATURES.md)** - Detailed feature descriptions and workflows
- **[04-API-REFERENCE.md](04-API-REFERENCE.md)** - Complete API endpoint documentation
- **[05-USER-GUIDE.md](05-USER-GUIDE.md)** - How to use Discovery Coach effectively

### Technical Documentation
- **[BACKEND_SETUP.md](BACKEND_SETUP.md)** - Backend configuration and setup
- **[FRONTEND.md](FRONTEND.md)** - Frontend implementation details
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deployment and operations guide
- **[CHANGELOG.md](CHANGELOG.md)** - Recent updates and version history

## Quick Start

### Prerequisites
- Python 3.13+
- OpenAI API key in `.env` file
- Virtual environment: `venv/`
- ⚠️ **IMPORTANT**: Disable VPN for optimal OpenAI API connectivity

### Launch Discovery Coach
```bash
cd Discovery_coach
./start.sh
```

The server will:
1. Activate virtual environment
2. Initialize RAG vector database (7 knowledge base documents)
3. Start FastAPI server on `http://localhost:8050`
4. Automatically open GUI in Chrome

### Alternative Manual Start
```bash
# Activate virtual environment
source venv/bin/activate

# Start backend server
python backend/app.py

# Access GUI at: frontend/index.html
```

### Performance Expectations
- Summary generation: 4-6 seconds
- Regular chat with RAG: 2-4 seconds
- RAG retrieval: <1 second (6 documents, ~5KB context)
- No hanging or timeouts

## Key Features at a Glance

✅ **Web-Based GUI** - Modern chat interface with real-time responses  
✅ **Socratic Discovery** - Guided questioning (WHO/WHAT/WHY/IMPACT)  
✅ **RAG-Enhanced** - Knowledge base integration via Chroma vector DB  
✅ **Session Management** - Save/load/delete conversation sessions  
✅ **Auto-Detection** - Automatically extracts and stores Epics/Features  
✅ **Draft Buttons** - One-click Epic and Feature generation  
✅ **Summary View** - Show discovery progress at any time  
✅ **Model Selection** - Choose between GPT-4o, GPT-4o-mini, GPT-o1, etc.  
✅ **Temperature Control** - Adjust response creativity (0-2)  
✅ **Conversation Continuity** - Follow-up questions after summaries/outlines  
✅ **MVP & Full Scope** - Epic template includes MVP and forecasted rollout  

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Frontend | HTML5, CSS3, Vanilla JavaScript |
| Backend | FastAPI + Uvicorn (Python 3.13) |
| LLM Framework | LangChain 1.1.2 |
| Language Model | OpenAI GPT-4o-mini (configurable) |
| Vector Database | Chroma with text-embedding-3-small |
| Session Storage | Server-side JSON files |
| Port | 8050 (configurable) |

## Architecture Overview

```
┌─────────────────┐
│   Web Browser   │  index.html + script.js + styles.css
│   (Frontend)    │
└────────┬────────┘
         │ HTTP/JSON (Port 8050)
         ▼
┌─────────────────┐
│  FastAPI Server │  app.py (REST API)
│   (Backend)     │
└────────┬────────┘
         │
         ├──────────────┐
         ▼              ▼
┌─────────────────┐  ┌──────────────────┐
│  LangChain RAG  │  │ Session Storage  │
│  discovery_coach│  │ (JSON files)     │
│  .py            │  │                  │
└────────┬────────┘  └──────────────────┘
         │
         ├──────────────┬──────────────┐
         ▼              ▼              ▼
┌──────────────┐  ┌──────────┐  ┌──────────────┐
│ OpenAI GPT   │  │ Chroma   │  │ Knowledge    │
│ (LLM)        │  │ Vector DB│  │ Base (.txt)  │
└──────────────┘  └──────────┘  └──────────────┘
```

## Recent Updates (December 2025)

### Architecture Improvements (Dec 8)
- ✅ Refactored `discovery_coach.py` - removed ~450 lines of unused CLI code (76% reduction)
- ✅ Clean separation: API module functions only, no CLI interface
- ✅ Improved maintainability with focused, single-purpose module
- ✅ Updated virtual environment path from `../.venv` to `venv/`

### Knowledge Base Enhancements (Dec 8)
- ✅ Epic template now includes 19 sections (was 15)
- ✅ Added Section 11: FORECASTED COSTS (MVP + Full Implementation)
- ✅ Added Section 14: SOLUTION ANALYSIS (customer, program, sales impact)
- ✅ Added Section 15: DEVELOPMENT STRATEGY (sourcing, phasing, dependencies)
- ✅ Comprehensive validation checklist in template usage notes
- ✅ Enhanced example with complete cost, solution, and strategy sections
- ✅ Feature selection workflow - system now asks which feature to draft
- ✅ Updated .gitignore to exclude *.sqlite3, *.bin, chroma.sqlite3

### Session Management Enhancements
- ✅ Server-side session storage in `Session_storage/` folder
- ✅ Session list view with metadata (date, size)
- ✅ Multi-select session deletion with confirmation
- ✅ Session load restores full chat history

### Conversation Flow Improvements
- ✅ Automatic Epic/Feature detection and storage
- ✅ Draft Epic and Draft Feature buttons
- ✅ Follow-up questions after Summary/Outline
- ✅ Continuous conversation context
- ✅ Feature selection prompt when multiple features proposed

### UI/UX Enhancements
- ✅ Model selection dropdown (5 models)
- ✅ Temperature slider (0-2 range)
- ✅ Loading indicators for all async operations
- ✅ Grouped action buttons (Epic/Feature)
- ✅ Left-aligned user messages for better readability

## Support & Troubleshooting

### Common Issues

**Server won't start (port in use):**
```bash
./stop.sh  # Kills processes on port 8050
./start.sh # Restarts server
```

**Knowledge base not updating:**
```bash
./reset_knowledge.sh  # Removes rag_db folder
# Restart server to rebuild
```

**Check server status:**
```bash
./status.sh  # Shows server, DB, and session info
```

### Getting Help

1. Check the detailed documentation in this folder
2. Review API docs at `http://localhost:8050/docs` (when server running)
3. Examine server logs for error messages
4. Verify `.env` file contains valid `OPENAI_API_KEY`

## Contributing

When adding features or fixing bugs:

1. Update relevant documentation files
2. Test with `./start.sh` and `./stop.sh` scripts
3. Verify session save/load functionality
4. Check Epic/Feature auto-detection works
5. Update CHANGELOG.md with changes

## License

[Include license information here]
