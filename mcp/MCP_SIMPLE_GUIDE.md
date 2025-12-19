# Simple MCP Integration Guide

Based on the guidance you received: **Just pass MCP tools directly to your agent.**

## Quick Overview

1. Use [MCP Inspector](https://modelcontextprotocol.io/docs/tools/inspector) to connect to any MCP server and check auth
2. Grab the auth token
3. Get the tools from the MCP server
4. Pass tools directly to your agent

No complex server management needed!

## Step 1: Use MCP Inspector

Visit: https://modelcontextprotocol.io/docs/tools/inspector

The Inspector helps you:
- Connect to any MCP server
- See what authentication it needs
- Browse available tools
- Test tools interactively
- Get the auth token you need

## Step 2: Get Your MCP Tools

Once you have the auth token from the Inspector, connect to your MCP server and get the tools:

```python
from langchain_mcp_adapters.client import MCPClient

# Connect to your MCP server with the auth token from Inspector
mcp_client = MCPClient({
    "url": "https://your-mcp-server-url/sse",
    "headers": {"Authorization": f"Bearer {your_token_from_inspector}"},
    "transport": "sse"
})

# Get the tools
tools = mcp_client.get_tools()
print(f"Got {len(tools)} tools:", [t.name for t in tools])
```

## Step 3: Pass Tools to Your Agent

Now just pass those tools directly to your Discovery Coach agent:

```python
from mcp_integration import create_mcp_coach

# Create agent with the MCP tools
mcp_coach = await create_mcp_coach(tools=tools)

# Use it in your /api/chat endpoint
result = await mcp_coach.chat(
    message="Create a Jira epic for user authentication",
    rag_context=context_text,  # From your existing RAG
    chat_history=active_context["chat_history"]
)
```

## Complete Integration Example for app.py

Here's how to integrate into your existing Discovery Coach:

```python
# At the top of app.py
from mcp_integration import create_mcp_coach
from langchain_mcp_adapters.client import MCPClient
import os

# Global variables
mcp_coach = None
mcp_tools = []

@app.on_event("startup")
async def startup_event():
    """Initialize MCP tools on startup."""
    global mcp_coach, mcp_tools
    
    # Get auth token from environment (use Inspector to find it first)
    mcp_token = os.getenv("MCP_AUTH_TOKEN")
    mcp_url = os.getenv("MCP_SERVER_URL")
    
    if mcp_token and mcp_url:
        try:
            # Connect to MCP server
            mcp_client = MCPClient({
                "url": mcp_url,
                "headers": {"Authorization": f"Bearer {mcp_token}"},
                "transport": "sse"
            })
            
            # Get tools
            mcp_tools = mcp_client.get_tools()
            print(f"✓ Loaded {len(mcp_tools)} MCP tools")
            
            # Create agent with tools
            mcp_coach = await create_mcp_coach(tools=mcp_tools)
            
        except Exception as e:
            print(f"⚠️  MCP tools not available: {e}")
            print("   Continuing without MCP integration")
    else:
        print("ℹ️  No MCP configuration found (set MCP_AUTH_TOKEN and MCP_SERVER_URL)")

@app.post("/api/chat")
async def chat(request: ChatRequest):
    # ... your existing RAG retrieval code ...
    
    # Check if user wants tool actions
    needs_tools = any(keyword in request.message.lower() 
                      for keyword in ["create", "update", "jira", "confluence", "ticket"])
    
    if needs_tools and mcp_coach:
        # Use MCP agent with tools
        result = await mcp_coach.chat(
            message=request.message,
            rag_context=context_text,
            chat_history=recent_history
        )
        return {
            "response": result["response"],
            "success": result["success"],
            "tools_used": [tc["tool"] for tc in result["tool_calls"]]
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

## Environment Configuration

Add to your `.env` file (after using MCP Inspector):

```bash
# OpenAI (already set)
OPENAI_API_KEY='sk-proj-...'

# MCP Configuration (get these from MCP Inspector)
MCP_SERVER_URL=https://your-mcp-server.com/sse
MCP_AUTH_TOKEN=your_bearer_token_from_inspector
```

## Using the MCP Inspector

### Step-by-Step:

1. **Open the Inspector**: https://modelcontextprotocol.io/docs/tools/inspector

2. **Connect to Your MCP Server**:
   - Enter server URL (e.g., `https://mcp.company.com/jira/sse`)
   - Select authentication type (usually Bearer token)
   - Enter credentials

3. **Browse Available Tools**:
   - See all tools the server provides
   - Read tool descriptions
   - Check required parameters

4. **Test Tools**:
   - Try calling tools with sample parameters
   - See actual responses
   - Verify authentication works

5. **Copy Auth Token**:
   - Inspector shows you the exact auth token/header
   - Copy it to your `.env` file as `MCP_AUTH_TOKEN`

## Example Usage Scenarios

### Scenario 1: Create Jira Epic from Chat

**User in Discovery Coach GUI**: "Create a Jira epic for implementing SSO authentication"

**What happens**:
1. RAG retrieves Epic template from knowledge base
2. Agent uses template to structure the Epic
3. Agent calls MCP tool `create_jira_epic` with structured data
4. Returns: "Created Epic PROJ-123: Implement SSO Authentication"

### Scenario 2: Document in Confluence

**User**: "Document this feature in Confluence"

**What happens**:
1. Agent reads active Feature context
2. Formats for Confluence
3. Calls MCP tool `create_confluence_page`
4. Returns: "Page created: https://confluence.company.com/display/PROJ/Feature-Name"

### Scenario 3: Search Existing Work

**User**: "Are there any existing Jira epics about authentication?"

**What happens**:
1. Agent calls MCP tool `search_jira` with query
2. Returns list of matching epics
3. User can reference existing work

## Installation

```bash
source venv/bin/activate
pip install langchain-mcp-adapters langgraph langchain-community
```

## Testing

Test your MCP integration:

```bash
python mcp_integration.py
```

This will create a mock tool and verify the agent can use it.

## Troubleshooting

### "Can't connect to MCP server"
- Use MCP Inspector first to verify connectivity
- Check auth token is correct
- Verify network/VPN access

### "No tools available"
- Check MCP server URL is correct
- Verify authentication worked
- Use Inspector to see if tools are actually available

### "Tools not being called"
- Make your request more explicit (e.g., "Use Jira to create...")
- Check tool descriptions match your request
- Verify agent has the tools (check startup logs)

## Key Differences from Complex Approach

**Old approach** (what I initially showed):
- Manage MCP server connections
- Handle SSE transport
- Deal with server lifecycle

**New approach** (what you should use):
- Use MCP Inspector to get auth
- Get tools from server
- Pass tools directly to agent
- Simple and clean!

## Next Steps

1. ✅ Visit MCP Inspector: https://modelcontextprotocol.io/docs/tools/inspector
2. ✅ Connect to your MCP server and get auth token
3. ✅ Add `MCP_SERVER_URL` and `MCP_AUTH_TOKEN` to `.env`
4. ✅ Install dependencies: `pip install langchain-mcp-adapters langgraph`
5. ✅ Test: `python mcp_integration.py`
6. ✅ Integrate into `app.py` using example above

---

**This is much simpler!** You don't need to manage MCP servers yourself - just use the Inspector to connect, get the tools, and pass them to your agent.
