# Connecting to Existing MCP Servers - Setup Guide

## Step 1: Gather Required Information

Contact your **DevOps/Platform team** or **MCP Administrator** and request:

### For Each MCP Server (Jira, Confluence, etc.):

1. **MCP Server URL**
   - Example: `https://mcp.yourcompany.com/jira/sse`
   - Ask: "What is the SSE endpoint URL for the [Jira/Confluence] MCP server?"

2. **Authentication Token**
   - Example: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - Ask: "How do I authenticate with the MCP server? Do I need a Bearer token or API key?"

3. **Transport Protocol** (usually SSE)
   - Ask: "Does the MCP server use SSE (Server-Sent Events) or stdio?"

4. **Available Tools** (optional but helpful)
   - Ask: "What tools/operations are available on the MCP server?"
   - Examples: create_issue, search_issues, update_issue, etc.

## Step 2: Update Your .env File

Once you have the information, update `/Users/maskol/Local-Development/Discovery_coach/.env`:

```bash
# OpenAI Configuration (already set)
OPENAI_API_KEY='sk-proj-...'

# Jira MCP Server
MCP_JIRA_URL=https://your-actual-mcp-server.com/jira/sse
JIRA_TOKEN=your_actual_bearer_token_from_admin

# Confluence MCP Server
MCP_CONFLUENCE_URL=https://your-actual-mcp-server.com/confluence/sse
CONFLUENCE_TOKEN=your_actual_bearer_token_from_admin
```

**Security Note:** Never commit your `.env` file to git. It should already be in `.gitignore`.

## Step 3: Install Required Dependencies

```bash
cd /Users/maskol/Local-Development/Discovery_coach
source venv/bin/activate
pip install langchain-mcp-adapters langgraph
```

## Step 4: Test the Connection

Run the test script to verify everything is configured correctly:

```bash
python test_mcp_connection.py
```

**Expected Output (Success):**
```
🔍 Checking MCP Configuration...

📋 Configuration Status:
  Jira URL: ✓ Set - https://mcp.yourcompany.com/jira/sse
  Jira Token: ✓ Set - [HIDDEN]
  Confluence URL: ✓ Set - https://mcp.yourcompany.com/confluence/sse
  Confluence Token: ✓ Set - [HIDDEN]

🔌 Attempting to connect to MCP servers...

✓ MCP client initialized

✅ SUCCESS! Connected to MCP servers
📦 Loaded 12 tools:

  • jira_create_issue
    Create a new issue in Jira...

  • jira_search_issues
    Search for issues using JQL...

  • confluence_create_page
    Create a new Confluence page...

🎉 MCP integration is ready to use!
```

## Step 5: Questions to Ask Your MCP Administrator

### Basic Questions:
1. "Do we have MCP servers running for Jira and/or Confluence?"
2. "What are the MCP server endpoint URLs?"
3. "How do I get authentication credentials?"

### Technical Questions:
4. "What transport protocol should I use (SSE, stdio, or HTTP)?"
5. "Are there any network/firewall restrictions I should know about?"
6. "Is there documentation for the available MCP tools?"
7. "Are there rate limits or usage quotas?"

### Operational Questions:
8. "Who should I contact if I have connection issues?"
9. "Are there separate development and production MCP servers?"
10. "Is there a test/sandbox environment I can use first?"

## Step 6: Common Issues & Solutions

### Issue: "I don't know if we have MCP servers"

**Solution:** Ask your team if they use:
- Model Context Protocol infrastructure
- LangChain tool servers
- Agent-friendly API gateways for Jira/Confluence

If not, you may need to either:
- Request MCP server setup (show them https://modelcontextprotocol.io)
- Use direct API integration instead (simpler alternative)

### Issue: "Connection refused" or timeout errors

**Solutions:**
1. Check VPN/network access to MCP server
2. Verify URL is correct (try curl test)
3. Check firewall allows SSE connections
4. Confirm you're on the right network

```bash
# Test connectivity
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://your-mcp-server.com/jira/sse
```

### Issue: "Authentication failed" or 401/403 errors

**Solutions:**
1. Verify token is correct and not expired
2. Check token has proper permissions
3. Confirm Bearer format: `Bearer YOUR_TOKEN`
4. Request new token from administrator

### Issue: "No tools available" or empty tool list

**Solutions:**
1. Verify MCP server is properly configured
2. Check server logs (ask administrator)
3. Confirm your account has permissions
4. Try different endpoint (some servers have /api/sse vs /sse)

## Alternative: Direct API Integration (No MCP Needed)

If your organization doesn't have MCP servers or they're too complex to set up, you can use direct Jira/Confluence APIs instead. This is simpler but less standardized.

Let me know if you want me to create a direct API integration instead!

## Next Steps

1. ✅ Contact your team to gather MCP server information
2. ✅ Update `.env` with actual URLs and tokens
3. ✅ Install dependencies: `pip install langchain-mcp-adapters langgraph`
4. ✅ Run `python test_mcp_connection.py` to verify
5. ✅ Once connected, test with Discovery Coach

---

**Need Help?** Let me know what information you've gathered and I can help troubleshoot or create a direct API integration instead.
