import asyncio
import os
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent


async def main():
    # Initialize the MCP client with Jira and Confluence SSE servers
    async with MultiServerMCPClient(
        {
            "jira": {
                "url": "https://your-mcp-server.com/jira/sse",
                "headers": {"Authorization": f"Bearer {os.environ['JIRA_TOKEN']}"},
                "transport": "sse",
            },
            "confluence": {
                "url": "https://your-mcp-server.com/confluence/sse",
                "headers": {
                    "Authorization": f"Bearer {os.environ['CONFLUENCE_TOKEN']}"
                },
                "transport": "sse",
            },
        }
    ) as client:
        # Get tools from MCP servers
        tools = client.get_tools()
        print(f"Loaded {len(tools)} tools:", [t.name for t in tools])

        # Create an LLM
        llm = ChatOpenAI(model="gpt-4o", temperature=0)

        # Create a ReAct agent with the MCP tools
        agent = create_react_agent(llm, tools)

        # Use the agent
        result = await agent.ainvoke(
            {
                "messages": [
                    (
                        "user",
                        "Create a Jira ticket for the login bug and document it in Confluence",
                    )
                ]
            }
        )

        print(result)


if __name__ == "__main__":
    asyncio.run(main())
