# Discovery Coach - Changelog

## December 7, 2025

### Session Management Enhancements

#### Server-Side Session Storage
- ✅ Sessions now saved to `Session_storage/` folder on server
- ✅ Session files named with timestamp: `session-YYYY-MM-DD-HH-MM-SS.json`
- ✅ Includes: activeEpic, activeFeature, piObjectives, conversationHistory, messages, timestamp
- ✅ List sessions with metadata (filename, modified date, size)
- ✅ Load sessions with full context restoration

#### Multi-Select Session Deletion
- ✅ New "🗑️ Delete Session(s)" button
- ✅ Modal with checkboxes for selecting multiple sessions
- ✅ Visual feedback (selected items highlighted in red)
- ✅ Confirmation dialog before deletion
- ✅ Detailed success/error reporting
- ✅ Backend endpoint: `POST /api/session/delete`

#### Session Load Fix
- ✅ **CRITICAL FIX**: Chat history now properly restored from sessions
- ✅ `conversationHistory` converted to LangChain `HumanMessage`/`AIMessage` objects
- ✅ Backend `active_context["chat_history"]` populated correctly
- ✅ Show Summary now works correctly after session load
- ✅ Full conversation context maintained across sessions

### Automatic Content Detection

#### Epic Auto-Detection
- ✅ Automatically detects Epic creation in conversation
- ✅ Detection pattern: "EPIC NAME" AND ("EPIC HYPOTHESIS STATEMENT" OR "BUSINESS CONTEXT")
- ✅ Stores in `active_context["epic"]` without manual intervention
- ✅ Server logs: "✅ Epic automatically detected and stored"
- ✅ Enables immediate "Outline Epic" functionality

#### Feature Auto-Detection
- ✅ Automatically detects Feature creation
- ✅ Detection pattern: "FEATURE NAME" AND ("USER STORY" OR "ACCEPTANCE CRITERIA")
- ✅ Stores in `active_context["feature"]`
- ✅ Ready for evaluation and refinement

#### PI Objectives Auto-Detection
- ✅ Detects PI Objective content
- ✅ Detection pattern: "PI OBJECTIVE" OR "Program Increment Objective"
- ✅ Stores in `active_context["pi_objectives"]`

### Draft Buttons

#### Draft Epic Button
- ✅ New "✍️ Draft Epic" button in Actions section
- ✅ One-click Epic generation from discovery conversation
- ✅ Generates complete Epic with all sections:
  - Epic Name, Owner, Business Context
  - Problem/Opportunity, Target Customers
  - Epic Hypothesis Statement
  - Business Outcomes, Leading Indicators
  - **MVP** (scope, criteria, timeline, users)
  - **Forecasted Full Scope** (capabilities, rollout, benefits)
  - Scope, Business Impact, Risks, WSJF, Metrics
- ✅ Auto-detected and stored for immediate Outline
- ✅ Loading indicator: "Drafting Epic based on discovery conversation..."

#### Draft Feature Button
- ✅ New "✍️ Draft Feature" button
- ✅ Generates complete Feature from conversation
- ✅ Includes: Name, Owner, User Story, Acceptance Criteria, Dependencies, Risks, Metrics
- ✅ Auto-detected and stored
- ✅ Loading indicator: "Drafting Feature based on discovery conversation..."

### Conversation Continuity

#### Follow-Up Questions After Summary
- ✅ Show Summary now ends with agent follow-up question
- ✅ Prompt includes: "After the summary, ask me what I would like to do next"
- ✅ Suggestions: continue discovery, draft Epic, or explore specific aspects
- ✅ Summary displayed as agent message (not system message)
- ✅ Added to conversation history for context

#### Follow-Up Questions After Outline
- ✅ Outline Epic now includes follow-up question
- ✅ Agent asks: "What would you like to do next? 1) Evaluate, 2) Refine sections, 3) Break down into Features, 4) Continue with something else?"
- ✅ Epic content shown as agent message (white background)
- ✅ Epic added to conversation history
- ✅ Continuous conversation flow

- ✅ Outline Feature includes similar follow-up
- ✅ Agent asks: "What would you like to do next? 1) Evaluate, 2) Refine acceptance criteria, 3) Identify dependencies, 4) Continue with something else?"
- ✅ Feature shown as agent message
- ✅ Natural conversation continuation

### UI/UX Improvements

#### Model Selection
- ✅ Model dropdown in "Model Settings" section
- ✅ 5 models available:
  - GPT-4o Mini (default)
  - GPT-4o
  - GPT-4 Turbo
  - GPT-3.5 Turbo
  - GPT-o1
- ✅ Dynamic LLM creation per request (no server restart needed)
- ✅ Model selection sent with each chat message
- ✅ Instant model switching

#### Temperature Control
- ✅ Temperature slider (0.0 - 2.0, step 0.1)
- ✅ Default: 0.7
- ✅ Live value display
- ✅ Custom webkit/moz slider styling
- ✅ Temperature included in all chat requests
- ✅ Affects response creativity dynamically

#### Loading Indicators
- ✅ Show Summary: "Generating discovery summary..."
- ✅ Draft Epic: "Drafting Epic based on discovery conversation..."
- ✅ Draft Feature: "Drafting Feature based on discovery conversation..."
- ✅ Outline Epic: "Retrieving Epic..."
- ✅ Outline Feature: "Retrieving Feature..."
- ✅ All async operations disable send button during processing
- ✅ Status updates visible in status bar

#### Button Organization
- ✅ Action buttons now grouped logically:
  - Show Discovery Summary (top)
  - Epic buttons: Draft, Evaluate, Outline (grouped together)
  - Feature buttons: Draft, Evaluate, Outline (grouped together)
- ✅ Clear visual hierarchy
- ✅ Easier to find related actions

#### Message Alignment
- ✅ User messages changed from right-aligned to left-aligned
- ✅ Improved readability and consistency
- ✅ CSS: `justify-content: flex-start` instead of `flex-end`

### Template Updates

#### Epic Template Enhancements
- ✅ Added **Section 9: MVP (Minimum Viable Product)**
  - MVP Scope (minimum features to test hypothesis)
  - MVP Success Criteria (validation outcomes)
  - MVP Timeline (expected delivery)
  - MVP Target Users (who will test/use it)

- ✅ Added **Section 10: Forecasted Full Scope**
  - Full Capabilities (complete feature set beyond MVP)
  - Full Rollout Plan (scaling strategy)
  - Estimated Timeline (MVP to full implementation)
  - Expected Benefits at Full Scale (business outcomes)

- ✅ Renumbered subsequent sections (11-15)
- ✅ Updated example with MVP and phased rollout

#### Knowledge Base
- ✅ `epic_template.txt` updated with MVP and Full Scope sections
- ✅ Example shows 3-phase rollout approach
- ✅ Clear guidance on MVP vs full implementation

### Backend Improvements

#### Dynamic Model Configuration
- ✅ `ChatRequest` now includes `model` and `temperature` fields
- ✅ Backend creates LLM instance per request with user-selected settings
- ✅ No longer uses single global LLM
- ✅ Supports experimentation with different models

#### Session Load Context Restoration
- ✅ **CRITICAL FIX**: `conversationHistory` from JSON converted to LangChain messages
- ✅ Loop through messages, create `HumanMessage` for user role
- ✅ Create `AIMessage` for agent role
- ✅ Populate `active_context["chat_history"]` with message objects
- ✅ Full conversation memory restored

#### Content Detection Logic
- ✅ After each chat response, check for Epic/Feature/PI content
- ✅ Pattern matching on response text
- ✅ Automatic storage in active_context
- ✅ Console logging for debugging

### Bug Fixes

#### Session Load Chat History Bug
- ❌ **Issue**: Loading session cleared chat_history to empty array
- ✅ **Fix**: Convert conversationHistory JSON to HumanMessage/AIMessage objects
- ✅ **Impact**: Show Summary now works after session load
- ✅ **Impact**: Full conversation context maintained

#### Outline Display as System Message
- ❌ **Issue**: Epic/Feature outline shown in gray italic (system message)
- ✅ **Fix**: Changed to `addAgentMessage()` (white background, normal text)
- ✅ **Fix**: Added to conversation history
- ✅ **Impact**: Outline feels like part of conversation, not disconnected status

#### Missing Loading States
- ❌ **Issue**: Show Summary had no loading indicator
- ✅ **Fix**: Added `state.isLoading`, status update, button disable
- ✅ **Fix**: Added `finally` block to restore state
- ✅ **Impact**: Clear feedback during async operations

### File Structure Changes

#### Documentation Split
- ✅ Created `Documentation/README.md` (overview and navigation)
- ✅ Created `Documentation/03-FEATURES.md` (comprehensive feature guide)
- ✅ Created `Documentation/04-API-REFERENCE.md` (complete API documentation)
- ✅ Created `Documentation/CHANGELOG.md` (this file)
- ✅ Modular structure for easier maintenance
- ✅ Each file focuses on specific aspect

### Server Management

#### No Changes
- Existing shell scripts continue to work:
  - `start.sh` - Start server and open GUI
  - `stop.sh` - Stop server on port 8050
  - `status.sh` - Check server status
  - `reset_knowledge.sh` - Reset vector DB

---

## Previous Updates (Summary)

### October-November 2025

#### Migration to FastAPI
- Migrated from Flask to FastAPI
- Added Pydantic request validation
- Uvicorn ASGI server
- Auto-generated API docs at /docs

#### RAG Implementation
- Chroma vector database
- text-embedding-3-small embeddings
- k=6 retrieval
- Knowledge base in knowledge_base/ folder

#### GUI Development
- Full HTML/CSS/JavaScript interface
- Real-time chat with LangChain backend
- Active context display in sidebar
- Input history with arrow keys
- Session save/load (originally browser downloads)

#### Core Features
- Socratic discovery coaching
- Epic hypothesis statement validation
- Feature acceptance criteria formatting
- SMART objectives enforcement
- Customer segmentation guidance

---

## Upcoming Features (Planned)

### High Priority
- [ ] Export Epic/Feature to Markdown/PDF
- [ ] Copy Epic/Feature to clipboard
- [ ] Search within conversation history
- [ ] Conversation replay/summary view

### Medium Priority
- [ ] Multi-language support
- [ ] Custom knowledge base uploads via GUI
- [ ] Collaborative sessions (multi-user)
- [ ] Template customization interface

### Low Priority
- [ ] Dark mode theme
- [ ] Keyboard shortcuts
- [ ] Voice input support
- [ ] Integration with Jira/Azure DevOps

---

## Known Issues

### None Currently

All major issues resolved as of December 7, 2025.

### Previously Resolved
- ✅ Session load not restoring chat history (FIXED)
- ✅ Epic outline appearing as system message (FIXED)
- ✅ No loading indicator on Show Summary (FIXED)
- ✅ Epic not auto-detected from conversation (FIXED)

---

## Version History

### v2.0 - December 7, 2025
- Major release with session management, auto-detection, draft buttons
- Conversation continuity improvements
- Model/temperature configuration
- Epic template with MVP and Full Scope

### v1.5 - November 2025
- FastAPI migration
- RAG implementation
- GUI development

### v1.0 - October 2025
- Initial Flask-based CLI version
- Basic Epic coaching
- Manual prompt management

---

## Migration Notes

### From v1.5 to v2.0

**Breaking Changes:**
- Session files now server-side (not browser downloads)
- Session JSON structure includes piObjectives field
- Epic/Feature auto-detection changes behavior

**Migration Steps:**
1. Old browser-downloaded sessions can be manually uploaded to `Session_storage/` folder
2. Rename to format: `session-YYYY-MM-DD-HH-MM-SS.json`
3. Ensure JSON includes all required fields
4. Load via "📂 Load Session" button

**New Required Fields in Session JSON:**
```json
{
  "piObjectives": null,  // New field
  "conversationHistory": [...],  // Now required for chat history restoration
  "timestamp": "..."  // ISO format timestamp
}
```

---

## Performance Improvements

### December 7, 2025
- ✅ Reduced API calls for Outline operations (single fetch vs multiple)
- ✅ Parallel tool execution not yet implemented (sequential for safety)
- ✅ Session files compressed format (no change, already efficient)

### Areas for Future Optimization
- [ ] Implement response streaming for long Epic/Feature drafts
- [ ] Cache vector DB queries for repeated searches
- [ ] Lazy load chat history UI (virtual scrolling for long conversations)
- [ ] Debounce temperature slider updates

---

## Security Updates

### December 7, 2025
- ⚠️ CORS still allows all origins (development only)
- ⚠️ No authentication implemented (local use only)
- ⚠️ Session files readable by all with server access

### Production Recommendations
- [ ] Implement user authentication
- [ ] Restrict CORS to specific domains
- [ ] Encrypt session files
- [ ] Add rate limiting
- [ ] Input sanitization for file operations
- [ ] HTTPS/TLS for production deployment

---

## Testing Updates

### Manual Testing Completed
- ✅ Session save/load/delete workflow
- ✅ Epic auto-detection from conversation
- ✅ Draft Epic button functionality
- ✅ Model switching (GPT-4o-mini to GPT-4o)
- ✅ Temperature adjustment effects
- ✅ Follow-up questions after Summary/Outline
- ✅ Multi-select session deletion
- ✅ Chat history restoration after load

### Automated Testing
- [ ] Not yet implemented
- [ ] Future: pytest for backend endpoints
- [ ] Future: Jest for frontend JavaScript
- [ ] Future: E2E tests with Playwright

---

## Documentation Updates

### New Documentation Files
- `README.md` - Overview and navigation
- `03-FEATURES.md` - Complete feature guide (this file was created today)
- `04-API-REFERENCE.md` - API documentation (created today)
- `CHANGELOG.md` - Version history (this file)

### Updated Files
- `discovery_coach.md` - Now deprecated, use README.md instead
- `BACKEND_SETUP.md` - Still valid, no changes

### Documentation Standards
- Use Markdown for all documentation
- Include code examples for API endpoints
- Provide step-by-step workflows
- Keep changelog updated with each release
