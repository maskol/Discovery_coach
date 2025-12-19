# MCP Integration Guide for Discovery Coach

## Overview

This guide shows how to add **Model Context Protocol (MCP)** tool-calling capabilities to your Discovery Coach, enabling integration with Jira, Confluence, and other external systems.

## Architecture

### Current Setup (RAG-only)
```
User Query → RAG Retriever → System Prompt + Context → LLM → Response
```

### With MCP Integration (Hybrid Mode)
```
User Query → RAG Retriever → System Prompt + Context + MCP Tools → ReAct Agent → Response
                                                                      ↓
                                                              [Can invoke Jira/Confluence]
```

## Installation

### 1. Install Required Packages

Add MCP dependencies to your virtual environment:

```bash
source venv/bin/activate
pip install langchain-mcp-adapters langgraph
```

Update `requirements.txt`:

```bash
pip freeze | grep -E "(langchain-mcp-adapters|langgraph)" >> requirements.txt
```

### 2. Configure MCP Servers

Add to your `.env` file:

```bash
# MCP Server Configuration
MCP_JIRA_URL=https://your-mcp-server.com/jira/sse
JIRA_TOKEN=your-jira-bearer-token

MCP_CONFLUENCE_URL=https://your-mcp-server.com/confluence/sse
CONFLUENCE_TOKEN=your-confluence-bearer-token
```

## Integration Methods

### Method 1: Selective MCP Mode (Recommended)

Use MCP **only when user explicitly requests tool actions** (e.g., "create a Jira ticket").

**Modify `app.py`:**

```python
from mcp_integration import create_mcp_coach

# Global MCP coach (initialized on startup if configured)
mcp_coach = None

@app.on_event("startup")
async def startup_event():
    global mcp_coach
    try:
        mcp_coach = await create_mcp_coach()
        print(f"✓ MCP enabled with tools: {mcp_coach.list_tools()}")
    except Exception as e:
        print(f"⚠️ MCP not available: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    if mcp_coach:
        await mcp_coach.close()

@app.post("/api/chat")
async def chat(request: ChatRequest):
    # ... existing RAG retrieval code ...
    
    # Check if user wants tool actions
    needs_tools = any(keyword in request.message.lower() 
                      for keyword in ["create", "update", "jira", "confluence", "ticket"])
    
    if needs_tools and mcp_coach and mcp_coach.has_tools():
        # Use MCP agent with tools
        result = await mcp_coach.chat(
            message=request.message,
            rag_context=context_text,
            chat_history=recent_history
        )
        return {
            "response": result["response"],
            "success": result["success"],
            "tools_used": result["tool_calls"]
        }
    else:
        # Use existing RAG-only chain
        response = chain.invoke({
            "user_input": full_query,
            "context": context_text,
            "chat_history": recent_history,
        })
        return {"response": response.content, "success": True}
```

### Method 2: Always-On Agent Mode

Replace the simple chain with a ReAct agent that **always has tools available**.

**Benefits:**
- Agent autonomously decides when to use tools
- Can chain operations (e.g., retrieve template → create Jira ticket)

**Trade-offs:**
- Slightly slower (agent reasoning overhead)
- May invoke tools unnecessarily

**Implementation:**

```python
# In app.py startup
mcp_coach = await create_mcp_coach()

# In /api/chat endpoint - replace chain.invoke with:
result = await mcp_coach.chat(
    message=request.message,
    rag_context=context_text,
    chat_history=recent_history
)
```

## Usage Examples

### Example 1: Create Jira Epic

**User:** "Create a Jira epic for improving user authentication with SSO"

**What happens:**
1. RAG retrieves Epic template from knowledge base
2. Agent uses template to structure the Epic
3. Agent invokes MCP Jira tool to create the Epic
4. Returns confirmation with Epic ID

### Example 2: Document Feature in Confluence

**User:** "Document this feature in Confluence"

**What happens:**
1. Agent reads active Feature context
2. Formats content for Confluence
3. Invokes MCP Confluence tool to create/update page
4. Returns page URL

### Example 3: Mixed Query

**User:** "What's the difference between an Epic and a Feature?"

**What happens:**
1. RAG retrieves SAFe documentation
2. Agent answers from knowledge base
3. **No tools invoked** (not needed)

## Testing MCP Integration

### Test 1: Verify MCP Setup

```bash
source venv/bin/activate
python mcp_integration.py
```

Expected output:
```
✓ Loaded 8 MCP tools: ['jira_create_issue', 'jira_search', ...]
✓ Agent initialized with 8 tools
```

### Test 2: Test with Discovery Coach

Start the server:
```bash
./start.sh
```

In the GUI, try:
- "List available Jira projects"
- "Create a test Epic in Jira"
- "Search Confluence for SAFe documentation"

## Configuration Options

### Custom MCP Servers

To add additional MCP servers (GitHub, Linear, etc.):

```python
# In mcp_integration.py or pass to MCPDiscoveryCoach:
mcp_config = {
    "jira": {...},
    "confluence": {...},
    "github": {
        "url": "https://your-mcp-server.com/github/sse",
        "headers": {"Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}"},
        "transport": "sse"
    }
}

coach = MCPDiscoveryCoach(mcp_config=mcp_config)
```

### Adjust Tool Behavior

Control which tools are available:

```python
# In mcp_integration.py, after getting tools:
self.tools = self.mcp_client.get_tools()

# Filter to only specific tools
self.tools = [t for t in self.tools if t.name.startswith("jira_")]
```

## Troubleshooting

### MCP Connection Issues

**Symptom:** `MCP client initialization failed`

**Solutions:**
1. Verify MCP server URLs are correct and reachable
2. Check authentication tokens are valid
3. Ensure VPN/firewall allows SSE connections
4. Test connectivity: `curl -H "Authorization: Bearer TOKEN" MCP_URL`

### Tools Not Being Invoked

**Symptom:** Agent responds but never uses tools

**Solutions:**
1. Make query more explicit: "Use Jira to create..." instead of "create..."
2. Check agent logs for reasoning traces
3. Verify tool names match expected patterns

### OpenAI Timeout

**Symptom:** `Timeout waiting for response`

**Solutions:**
1. Increase timeout in `mcp_integration.py`: `timeout=120`
2. Reduce RAG context size for tool-heavy queries
3. Use faster model (gpt-4o-mini instead of gpt-4o)

## Performance Considerations

- **Latency:** MCP tool calls add ~1-3s per tool invocation
- **Cost:** Agent reasoning uses more tokens than simple chain
- **Caching:** Consider caching tool results (e.g., project lists)

## Next Steps

1. **Install dependencies:** `pip install langchain-mcp-adapters langgraph`
2. **Configure MCP servers:** Add URLs/tokens to `.env`
3. **Choose integration method:** Selective (recommended) or Always-On
4. **Test:** Run `python mcp_integration.py`
5. **Deploy:** Integrate into `app.py` using examples above

## Additional Resources

- [MCP Documentation](https://modelcontextprotocol.io)
- [LangChain MCP Adapters](https://python.langchain.com/docs/integrations/tools/mcp)
- [LangGraph ReAct Agent](https://langchain-ai.github.io/langgraph/reference/prebuilt/#langgraph.prebuilt.chat_agent_executor.create_react_agent)
