# LangGraph Implementation Guide

**Status:** ✅ Implemented  
**Date:** December 21, 2024

## Overview

Discovery Coach now uses **LangGraph** for stateful conversation workflows, replacing the previous linear chain approach. This provides:

- ✅ **Conditional routing** (draft mode vs question mode)
- ✅ **Self-correction loops** (automatic retry on quality issues)
- ✅ **Better error recovery** (graceful degradation)
- ✅ **Intent classification** (understand user goals)
- ✅ **Validation & quality checks** (ensure good outputs)

---

## Architecture

### Workflow Flow

```
User Message
    ↓
┌───────────────────┐
│ Classify Intent   │ → Determines: draft, question, evaluate, outline
└────────┬──────────┘
         ↓
┌───────────────────┐
│  Build Context    │ → Adds active Epic/Feature/Strategic Initiative
└────────┬──────────┘
         ↓
    [Conditional]
    /          \
Retrieve    Skip Retrieval
Context     (for summaries)
    \          /
         ↓
┌───────────────────┐
│ Generate Response │ → Uses LLM with context & history
└────────┬──────────┘
         ↓
┌───────────────────┐
│ Validate Response │ → Checks quality & completeness
└────────┬──────────┘
         ↓
    [Conditional]
    /    |    \
Retry  Clarify  Success
(2x max)  ↓      ↓
   ↓    User   Return
   └──→ Loop   Result
```

### Key Components

#### 1. **State Schema** (`DiscoveryState`)

Tracks all information throughout the workflow:

```python
class DiscoveryState(TypedDict):
    # Messages
    messages: Annotated[Sequence[BaseMessage], add_messages]
    
    # User context
    user_message: str
    context_type: str  # strategic-initiative, epic, feature, etc.
    active_epic: str | None
    active_feature: str | None
    active_strategic_initiative: str | None
    
    # Intent & routing
    intent: str  # draft, question, evaluate, outline, clarify
    confidence_score: float
    
    # Generation
    generated_response: str
    
    # Validation & retry
    needs_clarification: bool
    needs_retry: bool
    validation_issues: list[str]
    retry_count: int
```

#### 2. **Node Functions**

Each node is a discrete step:

| Node | Purpose | Output |
|------|---------|--------|
| `classify_intent` | Determine user goal | Intent + confidence |
| `build_context` | Add active Epic/Feature | Enhanced query |
| `retrieve_context` | Get relevant docs | Context text |
| `generate_response` | LLM generation | AI response |
| `validate_response` | Quality check | Issues list |
| `increment_retry` | Update counter | Retry count |

#### 3. **Conditional Routing**

**After Build Context:**
```python
def should_retrieve_context(state):
    if state.get("is_summary", False):
        return "generate"  # Skip retrieval
    return "retrieve"
```

**After Validation:**
```python
def should_continue_after_validation(state):
    if state.get("needs_retry") and retry_count < 2:
        return "retry"
    elif state.get("needs_clarification"):
        return "clarify"
    else:
        return "end"
```

---

## Features

### 1. Intent Classification

Automatically detects what the user wants to do:

- **Draft:** "Help me create an epic"
- **Question:** "What is a hypothesis statement?"
- **Evaluate:** "Can you review my epic?"
- **Outline:** "Show me the epic structure"

**Implementation:**
```python
# Quick heuristic for common cases
if "draft" in message or "create" in message:
    intent = "draft"
    confidence = 0.9

# LLM classification for complex cases
else:
    llm_result = classify_with_llm(message)
    intent = llm_result["intent"]
    confidence = llm_result["confidence"]
```

### 2. Context-Aware Retrieval

Retrieval is optimized based on context:

```python
# Add context-specific keywords
if context_type == "strategic-initiative":
    query = f"Strategic Initiative {user_message}"
elif context_type == "pi-objective":
    query = f"PI Objectives {user_message}"

# Skip retrieval for summaries
if is_summary:
    return "Skip retrieval - use active context only"
```

### 3. Self-Correction Loop

Automatically retries if quality issues detected:

```python
# Validation checks
issues = []

if len(response) < 50:
    issues.append("Response too short")

if intent == "draft" and "EPIC NAME" not in response:
    issues.append("Missing required section: EPIC NAME")

# Retry logic
if issues and retry_count < 2:
    retry_count += 1
    return to generate_response_node  # Try again!
```

**Validation Criteria:**
- ✅ Response length (50-5000 chars)
- ✅ Template compliance (for drafts)
- ✅ Completeness (no "..." or "[To be filled]")
- ✅ Required sections present

### 4. Error Recovery

Graceful handling of failures:

```python
try:
    docs = retriever.invoke(query)
except Exception as e:
    print(f"⚠️ Retrieval failed: {e}")
    # Continue with active context only
    docs = []
    context = "Using active context only"
```

**Error Strategies:**
- Retrieval fails → Use active context
- LLM timeout → Retry with shorter context
- Max retries → Return best attempt with note
- Validation fails → Ask for clarification

### 5. Metadata & Tracing

Every node execution is tracked:

```python
config={
    "metadata": {
        "context_type": state["context_type"],
        "intent": state["intent"],
        "retry_count": state.get("retry_count", 0),
    },
    "tags": [
        context_type,
        provider,
        f"model:{model}",
        intent,
    ],
}
```

View in LangSmith:
- See each node execution
- Track decision points
- Debug routing logic
- Measure performance per node

---

## Usage

### From Chat Endpoint

The `/api/chat` endpoint now uses LangGraph automatically:

```python
from discovery_workflow import create_discovery_workflow, prepare_initial_state

# Create workflow
workflow = create_discovery_workflow()

# Prepare state
initial_state = prepare_initial_state(
    message=request.message,
    context_type=request.contextType,
    model=request.model,
    provider=request.provider,
    temperature=request.temperature,
    active_epic=request.activeEpic,
    active_feature=request.activeFeature,
    active_strategic_initiative=request.activeStrategicInitiative,
    chat_history=active_context["chat_history"],
)

# Execute workflow
final_state = await workflow.ainvoke(initial_state)

# Get result
response = final_state["generated_response"]
```

### Response Metadata

The endpoint now returns additional metadata:

```json
{
  "response": "...",
  "success": true,
  "metadata": {
    "intent": "draft",
    "confidence": 0.9,
    "retry_count": 0,
    "validation_issues": [],
    "needs_clarification": false
  }
}
```

### Legacy Endpoint

The original linear chain is available at `/api/chat/legacy` for comparison.

---

## Examples

### Example 1: Draft Request with Retry

**User:** "Help me create an epic"

**Workflow:**
1. ✅ Classify Intent → "draft" (confidence: 0.9)
2. ✅ Build Context → Add active Strategic Initiative
3. ✅ Retrieve Context → Get epic template & examples
4. ✅ Generate Response → Create draft
5. ⚠️ Validate → Missing "LEADING INDICATORS" section
6. 🔄 Increment Retry → retry_count = 1
7. ✅ Generate Response → Create improved draft
8. ✅ Validate → All sections present
9. ✅ Return Result

**Result:** High-quality epic with all required sections

### Example 2: Question with Context

**User:** "What's a good hypothesis statement?"

**Workflow:**
1. ✅ Classify Intent → "question" (confidence: 0.85)
2. ✅ Build Context → Include active epic for context
3. ✅ Retrieve Context → Get hypothesis examples
4. ✅ Generate Response → Explain with examples
5. ✅ Validate → Good length, actionable
6. ✅ Return Result

**Result:** Clear explanation with relevant examples

### Example 3: Summary Request (Skip Retrieval)

**User:** "Summarize the epic"

**Workflow:**
1. ✅ Classify Intent → "question" (is_summary: true)
2. ✅ Build Context → Include full epic text
3. ⏭️ Skip Retrieval → Not needed for summary
4. ✅ Generate Response → Create summary
5. ✅ Validate → Appropriate length
6. ✅ Return Result

**Result:** Concise summary, faster response

### Example 4: Low Confidence → Clarification

**User:** "Can you help with the thing?"

**Workflow:**
1. ⚠️ Classify Intent → "question" (confidence: 0.4)
2. ✅ Build Context → Limited context
3. ✅ Retrieve Context → Generic results
4. ✅ Generate Response → Vague answer
5. ⚠️ Validate → Low confidence detected
6. 💡 Request Clarification

**Result:** "I need more information. Are you asking about an Epic, Feature, or Strategic Initiative?"

---

## Benefits Over Linear Chain

| Aspect | Linear Chain (Old) | LangGraph (New) |
|--------|-------------------|-----------------|
| **Flow Control** | Hardcoded sequential | Dynamic conditional routing |
| **Error Handling** | Single try-catch | Multi-level recovery strategies |
| **Quality Control** | None | Automatic validation & retry |
| **Intent Detection** | Manual if/else | Intelligent classification |
| **Observability** | Single trace | Per-node tracing |
| **Adaptability** | Fixed path | Context-aware decisions |
| **Self-Correction** | None | Up to 2 automatic retries |
| **Clarification** | Not supported | Asks user when unsure |

---

## Performance

### Typical Latencies

| Scenario | Nodes Executed | Time |
|----------|---------------|------|
| Simple question | 5 nodes | 2-4s |
| Draft (first try) | 5 nodes | 5-8s |
| Draft with retry | 7 nodes | 10-15s |
| Summary (skip retrieval) | 4 nodes | 1-3s |

### Node Timings

- **Classify Intent:** 0.5-1s (LLM call)
- **Build Context:** <0.1s (string manipulation)
- **Retrieve Context:** 0.5-1s (vector search)
- **Generate Response:** 2-5s (LLM generation)
- **Validate Response:** <0.1s (rule-based)

---

## Monitoring

### LangSmith Integration

Every workflow execution creates a detailed trace:

```
Trace: "Discovery Workflow"
├── classify_intent (0.8s)
│   └── LLM call: intent classification
├── build_context (0.05s)
│   └── String concatenation
├── retrieve_context (0.7s)
│   └── Vector store query
├── generate_response (4.2s)
│   └── LLM call: response generation
└── validate_response (0.03s)
    └── Quality checks
```

**Useful Filters:**
- `tags: draft AND retry` - See all retried drafts
- `metadata.intent: question` - Filter by intent
- `metadata.retry_count: >0` - Find retried requests

---

## Configuration

### Timeout Settings

```python
# Longer timeout for drafts and summaries
timeout = 240 if (is_draft or is_summary) else 90
```

### Retry Limits

```python
# Max 2 retries to prevent infinite loops
max_retries = 2
```

### History Limits

```python
# Vary by request type
if is_summary:
    max_history = 0  # No history for summaries
elif is_draft:
    max_history = 12  # 6 conversation turns
else:
    max_history = 10  # 5 conversation turns
```

---

## Future Enhancements

### Planned Improvements

1. **Human-in-the-Loop**
   - Explicit approval gates for drafts
   - Interactive refinement
   - Save/resume workflows

2. **Advanced Validation**
   - LLM-based quality scoring
   - Compliance checking against SAFe standards
   - Automatic improvements

3. **Multi-Agent Collaboration**
   - Specialist agents for Epic/Feature/Strategic Initiative
   - Peer review between agents
   - Consensus building

4. **Persistent State**
   - Save workflow checkpoints to PostgreSQL
   - Resume interrupted workflows
   - Undo/redo support

5. **A/B Testing**
   - Run multiple workflows in parallel
   - Compare outputs
   - Learn best strategies

---

## Troubleshooting

### Issue: Workflow hangs

**Symptoms:** Request times out or takes very long

**Solutions:**
- Check LLM timeouts are appropriate
- Verify retriever is working
- Look for infinite retry loops (should be impossible with max_retries)

### Issue: Low quality responses

**Symptoms:** Validation keeps failing, max retries reached

**Solutions:**
- Check retrieval is finding relevant docs
- Verify system prompts are appropriate
- Adjust validation criteria
- Increase max_retries if needed

### Issue: Too many retries

**Symptoms:** Most requests retry 1-2 times

**Solutions:**
- Review validation criteria (too strict?)
- Check if LLM is following templates
- Improve prompts for first-try success

---

## Testing

### Manual Testing

1. **Simple Question:**
   ```
   "What is an epic hypothesis statement?"
   → Should route to "question" intent
   → Should retrieve relevant docs
   → Should answer without retry
   ```

2. **Draft Request:**
   ```
   "Help me create an epic for customer onboarding"
   → Should route to "draft" intent
   → Should include all required sections
   → May retry if sections missing
   ```

3. **Summary:**
   ```
   "Summarize the active epic"
   → Should skip retrieval
   → Should use active epic content
   → Should be fast (<3s)
   ```

### Automated Testing

Create test datasets (see `scripts/setup_langsmith_datasets.py`):
```bash
python scripts/setup_langsmith_datasets.py
python scripts/run_langsmith_evaluations.py
```

---

## API Reference

### `create_discovery_workflow()`

Creates and compiles the LangGraph workflow.

**Returns:** Compiled StateGraph

**Example:**
```python
workflow = create_discovery_workflow()
result = await workflow.ainvoke(initial_state)
```

### `prepare_initial_state(...)`

Prepares state for workflow execution.

**Parameters:**
- `message` (str): User message
- `context_type` (str): "strategic-initiative" | "epic" | "feature" | "story" | "pi-objective"
- `model` (str): LLM model name
- `provider` (str): "openai" | "ollama"
- `temperature` (float): 0.0-1.0
- `active_epic` (str | None): Active epic content
- `active_feature` (str | None): Active feature content
- `active_strategic_initiative` (str | None): Active initiative content
- `chat_history` (list | None): Previous messages

**Returns:** DiscoveryState

---

## Summary

✅ **Implemented:** LangGraph workflow with conditional routing, self-correction, and validation  
✅ **Benefits:** Better quality, error recovery, and observability  
✅ **Status:** Live in production at `/api/chat`  
✅ **Legacy:** Old linear chain available at `/api/chat/legacy`  

**Next Steps:** Monitor LangSmith traces, adjust validation criteria, and iterate based on real usage.
