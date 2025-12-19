import { MultiServerMCPClient } from '@langchain/mcp-adapters';
import { ChatOpenAI } from '@langchain/openai';
import { createReactAgent } from '@langchain/langgraph/prebuilt';

// Initialize the MCP client with Jira and Confluence SSE servers
const mcpClient = new MultiServerMCPClient({
  mcpServers: {
    jira: {
      url: 'https://your-mcp-server.com/jira/sse',
      headers: {
        Authorization: `Bearer ${process.env.JIRA_TOKEN}`,
      },
      automaticSSEFallback: true,
      reconnect: {
        enabled: true,
        maxAttempts: 3,
        delayMs: 1000,
      },
    },
    confluence: {
      url: 'https://your-mcp-server.com/confluence/sse',
      headers: {
        Authorization: `Bearer ${process.env.CONFLUENCE_TOKEN}`,
      },
      automaticSSEFallback: true,
      reconnect: {
        enabled: true,
        maxAttempts: 3,
        delayMs: 1000,
      },
    },
  },
  throwOnLoadError: false,
  prefixToolNameWithServerName: true,
});

// Get tools from MCP servers
const tools = await mcpClient.getTools();
console.log(`Loaded ${tools.length} tools:`, tools.map(t => t.name));

// Create an LLM
const llm = new ChatOpenAI({
  model: 'gpt-4o',
  temperature: 0,
});

// Create a ReAct agent with the MCP tools
const agent = createReactAgent({
  llm,
  tools,
});

// Use the agent
const result = await agent.invoke({
  messages: [{ role: 'user', content: 'Create a Jira ticket for the login bug and document it in Confluence' }],
});

console.log(result);

// Clean up when done
await mcpClient.close();