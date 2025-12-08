# Discovery Coach - Features Documentation

## Table of Contents
1. [Core Features](#core-features)
2. [Discovery Workflow](#discovery-workflow)
3. [Session Management](#session-management)
4. [Epic & Feature Management](#epic--feature-management)
5. [Model Configuration](#model-configuration)
6. [User Interface Features](#user-interface-features)

---

## Core Features

### 1. Socratic Discovery Coaching

The Discovery Coach uses a Socratic questioning approach to guide users through strategic thinking:

**Discovery Framework (WHO/WHAT/WHY/IMPACT):**
- **WHO**: Customer segments, personas, user groups
- **WHAT**: Problems, opportunities, solutions
- **WHY**: Business value, strategic importance
- **IMPACT**: Measurable outcomes, success metrics

**Conversation Flow:**
1. Ask open-ended questions to understand context
2. Probe deeper with follow-up questions
3. Challenge assumptions constructively
4. Guide toward SMART objectives
5. Help articulate hypothesis statements

### 2. RAG-Enhanced Responses

**Knowledge Base Integration:**
- Vector database (Chroma) with 7 organizational documents
- Retrieves relevant context for each question (~5KB)
- Grounds responses in documented best practices
- k=6 similarity search for comprehensive context
- <1 second retrieval time

**Knowledge Base Contents:**
- `epic_template.txt` - SAFe Epic template structure
- `feature_template.txt` - Feature hypothesis format
- `guidelines_epic_vs_feature.txt` - When to use Epic vs Feature
- `product_operating_model.txt` - Organizational methodology
- `telecom_examples_epics_and_features.txt` - Industry examples
- System prompts and questionnaires

**RAG Process:**
1. User message received
2. Query enhanced with active Epic/Feature context
3. Vector search retrieves top 6 relevant documents
4. **Optimization**: Summary requests skip RAG for speed
5. Regular queries use full RAG context
4. LLM generates response grounded in knowledge base
5. Response includes specific guidance from documents

### 3. Automatic Content Detection

**Epic Detection:**
- Detects when Epic is created in conversation
- Looks for: "EPIC NAME" AND ("EPIC HYPOTHESIS STATEMENT" OR "BUSINESS CONTEXT")
- Automatically stores in `active_context["epic"]`
- Enables immediate Outline Epic functionality

**Feature Detection:**
- Detects when Feature is created
- Looks for: "FEATURE NAME" AND ("USER STORY" OR "ACCEPTANCE CRITERIA")
- Automatically stores in `active_context["feature"]`
- Ready for evaluation and refinement

**PI Objectives Detection:**
- Detects PI Objective content
- Looks for: "PI OBJECTIVE" OR "Program Increment Objective"
- Stores in `active_context["pi_objectives"]`

---

## Discovery Workflow

### Standard Discovery Flow

```
1. Start Conversation
   ↓
2. Discovery Questions (WHO/WHAT/WHY/IMPACT)
   ↓
3. Show Summary (check progress)
   ↓
4. Continue Discovery OR Draft Epic
   ↓
5. Draft Epic (auto-generates from conversation)
   ↓
6. Review Epic (Outline Epic button)
   ↓
7. Refine Sections (conversational edits)
   ↓
8. Evaluate Epic (SAFe best practices check)
   ↓
9. Save Session (preserve all work)
```

### Discovery Summary Feature

**Purpose:** Track discovery progress without creating full Epic

**When to Use:**
- Check what information has been collected
- Identify missing information
- Decide next steps (continue discovery vs draft Epic)

**What It Shows:**
1. Customer/User details (who, where, how many)
2. Problems identified (what, frequency, severity)
3. Business impact (metrics, NPS, churn, etc.)
4. What information is still needed for Epic

**Follow-Up:**
Agent asks: "What would you like to do next - continue discovery on missing areas, draft the Epic, or explore a specific aspect in more detail?"

### Draft Epic Feature

**One-Click Epic Generation:**
- Button: "✍️ Draft Epic"
- Generates complete Epic from discovery conversation
- Uses Epic template with all sections
- Includes MVP and Forecasted Full Scope
- Automatically detected and stored for Outline

**Epic Sections Generated:**
1. Epic Name
2. Epic Owner
3. Business Context/Background
4. Problem/Opportunity
5. Target Customers/Users
6. Epic Hypothesis Statement
7. Desired Business Outcomes
8. Leading Indicators
9. **MVP** (scope, success criteria, timeline, users)
10. **Forecasted Full Scope** (capabilities, rollout, benefits)
11. Scope / Out of Scope
12. Business Impact & Value Assumptions
13. Risks, Assumptions & Constraints
14. WSJF (optional)
15. Metrics & Measurement Plan

### Draft Feature Feature

**One-Click Feature Generation:**
- Button: "✍️ Draft Feature"
- Creates Feature from conversation
- Uses Feature template format
- Auto-detected and stored

**Feature Sections Generated:**
1. Feature Name
2. Feature Owner
3. Business Context
4. User Story (As a... I want... So that...)
5. Acceptance Criteria (Given-When-Then)
6. Dependencies
7. Risks
8. Success Metrics

---

## Session Management

### Save Session

**What Gets Saved:**
- Active Epic content
- Active Feature content
- PI Objectives
- Full conversation history (user + agent messages)
- HTML message display
- Timestamp

**File Format:**
```json
{
  "activeEpic": "...",
  "activeFeature": "...",
  "piObjectives": "...",
  "conversationHistory": [
    {"role": "user", "content": "..."},
    {"role": "agent", "content": "..."}
  ],
  "messages": "<div>...</div>",
  "timestamp": "2025-12-07T19:44:19.425514"
}
```

**Storage Location:** `Session_storage/session-YYYY-MM-DD-HH-MM-SS.json`

### Load Session

**Restores:**
- Active context (Epic, Feature, PI Objectives)
- Full chat history (backend LangChain messages)
- Visual message display
- Conversation continuity

**Process:**
1. Shows modal with all available sessions
2. Displays session metadata (filename, date, size)
3. Click session to load
4. Backend restores `active_context["chat_history"]` from conversationHistory
5. Frontend restores visual display
6. Continue conversation where you left off

### Delete Sessions

**Multi-Select Deletion:**
- Shows all sessions with checkboxes
- Select one or multiple sessions
- Visual feedback (selected items turn red)
- Confirmation dialog before deletion
- Detailed feedback on success/errors

**Process:**
1. Click "🗑️ Delete Session(s)"
2. Modal shows all sessions with checkboxes
3. Select sessions to delete
4. Click "🗑️ Delete Selected"
5. Confirm deletion
6. Sessions permanently removed from `Session_storage/`

---

## Epic & Feature Management

### Outline Epic

**Displays Current Epic:**
- Shows stored Epic content from `active_context["epic"]`
- Displays as agent message (white background)
- Adds Epic to conversation history

**Follow-Up Question:**
"What would you like to do next? Would you like to: 1) Evaluate this Epic against SAFe best practices, 2) Refine specific sections, 3) Break it down into Features, or 4) Continue with something else?"

**When Available:**
- After Draft Epic
- After Evaluate Epic (paste Epic content)
- After Epic auto-detection from conversation

### Outline Feature

**Displays Current Feature:**
- Shows stored Feature from `active_context["feature"]`
- Displays as agent message
- Adds to conversation history

**Follow-Up Question:**
"What would you like to do next? Would you like to: 1) Evaluate this Feature against SAFe best practices, 2) Refine the acceptance criteria, 3) Identify dependencies, or 4) Continue with something else?"

### Evaluate Epic/Feature

**Manual Content Loading:**
- Paste Epic or Feature content
- Stores in active context
- Evaluates against SAFe best practices
- Provides detailed feedback

**Evaluation Criteria:**
- Hypothesis format correctness
- SMART objectives compliance
- Customer segment clarity
- Business value articulation
- Measurable outcomes defined
- Risk identification completeness

### New Epic / New Feature

**Clear Active Context:**
- Removes current Epic or Feature
- Chat history preserved
- Start fresh Epic/Feature discovery
- Previous content can be reloaded from session

---

## Model Configuration

### Model Selection

**Available Models:**
1. **GPT-4o Mini** (default) - Fast, cost-effective
2. **GPT-4o** - Most capable, balanced
3. **GPT-4 Turbo** - High performance
4. **GPT-3.5 Turbo** - Legacy, fast
5. **GPT-o1** - Latest reasoning model

**Dynamic LLM Creation:**
- Backend creates LLM instance per request
- Uses model and temperature from frontend
- No server restart needed
- Instant model switching

### Temperature Control

**Range:** 0.0 - 2.0 (step 0.1)  
**Default:** 0.7

**Temperature Effects:**
- **0.0-0.3**: Deterministic, focused, consistent
- **0.4-0.7**: Balanced creativity and consistency
- **0.8-1.2**: More creative, varied responses
- **1.3-2.0**: Highly creative, experimental

**Slider Display:**
- Visual slider in Model Settings
- Live value display
- Updates sent with each message

---

## User Interface Features

### Chat Interface

**Message Types:**
1. **User Messages** - Left-aligned, purple gradient background
2. **Agent Messages** - White background, black text
3. **System Messages** - Gray italic (status updates)

**Features:**
- Auto-scroll to latest message
- Timestamp on user messages
- Markdown rendering (bold, italic, headers)
- Code block formatting
- Link preservation

### Input History

**Terminal-Like Navigation:**
- **↑ Arrow**: Previous message
- **↓ Arrow**: Next message (or clear if at end)
- Preserves input being typed
- Cycles through conversation history

### Loading States

**Visual Feedback:**
- Status bar shows current operation
- Send button disabled during processing
- Clear status messages:
  - "Coach is thinking..."
  - "Generating discovery summary..."
  - "Drafting Epic based on discovery conversation..."
  - "Retrieving Epic..."

### Action Buttons

**Organized by Function:**

**Actions Section:**
- 📊 Show Discovery Summary
- **Epic:** ✍️ Draft Epic, 📂 Evaluate Epic, 📋 Outline Epic
- **Feature:** ✍️ Draft Feature, 📂 Evaluate Feature, 📋 Outline Feature

**Context Management:**
- 🔄 New Epic
- 🔄 New Feature
- 🗑️ Clear All

**Session Management:**
- 💾 Save Session
- 📂 Load Session
- 🗑️ Delete Session(s)

**Model Settings:**
- Model dropdown
- Temperature slider

### Active Context Display

**Sidebar Shows:**
- Current Epic (if loaded)
- Current Feature (if loaded)
- Expandable/collapsible
- Click to view details

**Updates Automatically:**
- When Epic drafted or loaded
- When Feature drafted or loaded
- When context cleared
- When session loaded

### Help Modal

**Accessible via:** ❓ Help button

**Contains:**
- Command reference
- Workflow guide
- Active context explanation
- Key features overview
- Epic hypothesis format
- Acceptance criteria format (Gherkin)

---

## Advanced Features

### Conversation Continuity

**After Summary:**
- Agent asks follow-up questions
- Conversation flows naturally
- Summary added to history
- Can continue discovery or draft Epic

**After Outline:**
- Agent suggests next steps
- Epic/Feature content in conversation
- Can refine, evaluate, or break down
- Full context maintained

### Context Awareness

**Active Context Injection:**
- Every message includes active Epic/Feature
- Backend sees full context
- Responses reference current work
- Progressive refinement supported

**Chat History:**
- Full conversation retained in backend
- HumanMessage/AIMessage objects
- Enables follow-up questions
- Maintains discovery thread

### Knowledge Base Management

**Reset Knowledge Base:**
```bash
./reset_knowledge.sh
```

**When to Reset:**
- After adding new knowledge files
- After updating existing files
- After changing embeddings model
- Database corruption

**What Happens:**
- Removes `rag_db/` folder
- Next server start rebuilds vector DB
- Re-indexes all knowledge_base/*.txt files
- Fresh embeddings generated

### Server Management Scripts

**start.sh:**
- Activates venv
- Kills existing server on port 8050
- Starts FastAPI server in background
- Waits for health check
- Opens Chrome to GUI
- Handles Ctrl+C gracefully

**stop.sh:**
- Checks for processes on port 8050
- Shows process details
- Prompts for confirmation
- Kills processes
- Verifies termination

**status.sh:**
- Shows server running status
- Displays process information
- Shows RAG DB size
- Shows session count
- Network port status

**reset_knowledge.sh:**
- Confirms action (destructive)
- Removes rag_db folder
- Instructions for rebuild

---

## Workflow Examples

### Example 1: Create Epic from Scratch

1. Start conversation: "I have customers with connectivity problems..."
2. Agent asks WHO/WHAT/WHY questions
3. Periodically click "📊 Show Summary" to check progress
4. When ready: Click "✍️ Draft Epic"
5. Agent generates complete Epic with MVP and Full Scope
6. Epic auto-detected and stored
7. Click "📋 Outline Epic" to review
8. Refine: "Can you improve the MVP section?"
9. Click "💾 Save Session"

### Example 2: Evaluate Existing Epic

1. Click "📂 Evaluate Epic"
2. Paste Epic content
3. Agent evaluates against SAFe best practices
4. Provides detailed feedback
5. Ask: "How can I improve the hypothesis statement?"
6. Iterative refinement conversation
7. Click "📋 Outline Epic" to see updated version

### Example 3: Session Management

1. Work on Epic discovery
2. Click "💾 Save Session" before leaving
3. Later: Click "📂 Load Session"
4. Select session from list
5. Full conversation restored
6. Continue where you left off
7. Periodically delete old sessions with "🗑️ Delete Session(s)"

### Example 4: Multi-Model Experimentation

1. Start with GPT-4o Mini (fast, cheap)
2. Get initial Epic draft
3. Switch to GPT-4o for refinement
4. Adjust temperature to 0.3 for consistency
5. Get detailed evaluation
6. Switch to GPT-o1 for creative alternatives
7. Compare responses

---

## Best Practices

### Discovery Conversations

✅ **Do:**
- Start broad, then narrow focus
- Provide specific examples
- Share actual metrics and data
- Use "Show Summary" to track progress
- Draft Epic when discovery feels complete

❌ **Don't:**
- Rush to draft Epic too early
- Skip customer segment details
- Ignore business impact questions
- Forget to save sessions

### Epic Refinement

✅ **Do:**
- Iterate on specific sections
- Ask for examples and alternatives
- Reference SAFe best practices
- Define clear MVP and full scope
- Include measurable outcomes

❌ **Don't:**
- Try to perfect in one iteration
- Skip hypothesis statement format
- Ignore feasibility constraints
- Overlook risks and assumptions

### Session Management

✅ **Do:**
- Save after major milestones
- Use descriptive timestamps
- Delete obsolete sessions regularly
- Load previous sessions for reference
- Export important Epics to separate files

❌ **Don't:**
- Rely only on browser memory
- Accumulate hundreds of sessions
- Lose work by forgetting to save

### Model Selection

✅ **Do:**
- Use GPT-4o Mini for most work (cost-effective)
- Switch to GPT-4o for complex refinement
- Lower temperature for consistency
- Raise temperature for creative ideation
- Test different models for comparison

❌ **Don't:**
- Use GPT-o1 for simple questions (expensive)
- Keep temperature too high (inconsistent)
- Change models mid-refinement (style shifts)

---

## Troubleshooting

### Epic Not Detected

**Symptom:** Draft Epic, but Outline Epic shows "No Epic content available"

**Solutions:**
1. Check server logs for "✅ Epic automatically detected"
2. Verify Epic contains "EPIC NAME" and "EPIC HYPOTHESIS STATEMENT"
3. Manually load with "📂 Evaluate Epic"
4. Restart server (detection may have failed)

### Session Load Incomplete

**Symptom:** Session loads but conversation history missing

**Solutions:**
1. Check session JSON file has conversationHistory array
2. Verify backend converts messages to HumanMessage/AIMessage
3. Look for errors in server logs
4. Try reloading session

### Follow-Up Questions Not Appearing

**Symptom:** Outline shows content but no follow-up from agent

**Solutions:**
1. Check browser console for JavaScript errors
2. Verify `addAgentMessage()` called correctly
3. Check network tab for failed API calls
4. Restart server and try again

### Temperature/Model Changes Ignored

**Symptom:** Responses don't reflect new settings

**Solutions:**
1. Check browser console that settings update
2. Verify network request includes model and temperature
3. Backend should log LLM creation
4. Try hard refresh (Cmd+Shift+R)
