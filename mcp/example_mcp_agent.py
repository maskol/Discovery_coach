"""
Example: Using Local MCP Server with Discovery Coach Agent
"""

import asyncio
import os
from dotenv import load_dotenv
from mcp.client.session import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client
from langchain_openai import ChatOpenAI
from langchain_core.tools import Tool
from langgraph.prebuilt import create_react_agent

# Load environment variables
load_dotenv()


def mcp_tool_to_langchain(mcp_tool, session):
    """Convert an MCP tool to a LangChain tool."""
    
    async def tool_func(**kwargs):
        """Execute the MCP tool."""
        result = await session.call_tool(mcp_tool.name, arguments=kwargs)
        # Extract text from result
        text_parts = []
        for content in result.content:
            if hasattr(content, 'text'):
                text_parts.append(content.text)
        return '\n'.join(text_parts)
    
    return Tool(
        name=mcp_tool.name,
        description=mcp_tool.description,
        func=lambda **kwargs: asyncio.run(tool_func(**kwargs)),
        coroutine=tool_func,
    )


async def main():
    """Run Discovery Coach with local MCP tools."""
    
    print("🚀 Starting Discovery Coach with Local MCP Server\n")
    
    # Start the local MCP server
    server_params = StdioServerParameters(
        command="node",
        args=["local_mcp_server.js"],
        env=None
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()
            
            # Get tools from MCP server
            tools_result = await session.list_tools()
            mcp_tools = tools_result.tools
            
            print(f"✅ Loaded {len(mcp_tools)} tools from MCP server\n")
            
            # Convert MCP tools to LangChain tools
            langchain_tools = [
                mcp_tool_to_langchain(tool, session) 
                for tool in mcp_tools
            ]
            
            # Create LLM
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
            
            # Create agent with MCP tools
            agent = create_react_agent(llm, langchain_tools)
            
            print("🤖 Discovery Coach Agent ready with MCP tools!\n")
            print("=" * 60)
            
            # Example 1: Create a Jira Epic
            print("\n📝 Example 1: Creating a Jira Epic\n")
            
            result1 = await agent.ainvoke({
                "messages": [{
                    "role": "user",
                    "content": "Create a Jira epic in project DISCO for implementing SSO authentication with OAuth 2.0"
                }]
            })
            
            print("Agent Response:")
            print(result1["messages"][-1].content)
            
            # Example 2: Search Jira
            print("\n" + "=" * 60)
            print("\n🔍 Example 2: Searching Jira\n")
            
            result2 = await agent.ainvoke({
                "messages": [{
                    "role": "user",
                    "content": "Search Jira for issues related to authentication"
                }]
            })
            
            print("Agent Response:")
            print(result2["messages"][-1].content)
            
            # Example 3: Create Confluence page
            print("\n" + "=" * 60)
            print("\n📄 Example 3: Creating Confluence Documentation\n")
            
            result3 = await agent.ainvoke({
                "messages": [{
                    "role": "user",
                    "content": "Create a Confluence page in the DISCO space documenting the SSO authentication epic"
                }]
            })
            
            print("Agent Response:")
            print(result3["messages"][-1].content)
            
            print("\n" + "=" * 60)
            print("\n✅ All examples completed!")
            print("\n💡 Next steps:")
            print("   1. Integrate this into app.py")
            print("   2. Replace mock tools with real Jira/Confluence APIs")
            print("   3. Add more tools as needed")


if __name__ == "__main__":
    asyncio.run(main())
