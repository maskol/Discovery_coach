#!/usr/bin/env python3
"""
Test the local MCP server with Discovery Coach
"""

import asyncio
import os
import subprocess
from mcp_integration import create_mcp_coach


async def test_local_mcp_server():
    """Test the local MCP server."""
    print("🧪 Testing Local MCP Server\n")
    
    # Import the MCP client for stdio
    try:
        from mcp.client.session import ClientSession
        from mcp.client.stdio import StdioServerParameters, stdio_client
    except ImportError as e:
        print(f"❌ Error importing mcp: {e}")
        print("\nTrying alternative import...")
        try:
            # Alternative import path
            import mcp
            print(f"mcp package found at: {mcp.__file__}")
            print(f"Available modules: {dir(mcp)}")
        except Exception as e2:
            print(f"❌ mcp package not installed or incompatible: {e2}")
            print("\nInstall with:")
            print("  pip install mcp")
        return
    
    # Start the local MCP server as a subprocess
    server_params = StdioServerParameters(
        command="node",
        args=["local_mcp_server.js"],
        env=None
    )
    
    print("🔌 Connecting to local MCP server...\n")
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            # List available tools
            tools_result = await session.list_tools()
            tools = tools_result.tools
            
            print(f"✅ Connected! Found {len(tools)} tools:\n")
            for tool in tools:
                print(f"  • {tool.name}")
                print(f"    {tool.description}")
                print()
            
            # Test a tool - create mock Jira epic
            print("\n📝 Testing create_jira_epic tool...\n")
            
            result = await session.call_tool(
                "create_jira_epic",
                arguments={
                    "summary": "Implement SSO Authentication",
                    "description": "Add single sign-on authentication support for enterprise users",
                    "project": "DISCO"
                }
            )
            
            print("Result:")
            for content in result.content:
                if hasattr(content, 'text'):
                    print(content.text)
            
            # Test search
            print("\n🔍 Testing search_jira tool...\n")
            
            search_result = await session.call_tool(
                "search_jira",
                arguments={
                    "query": "authentication"
                }
            )
            
            print("Search Results:")
            for content in search_result.content:
                if hasattr(content, 'text'):
                    print(content.text)
            
            print("\n✅ Local MCP server is working!")
            print("\nNow you can use these tools in your Discovery Coach agent.")


if __name__ == "__main__":
    asyncio.run(test_local_mcp_server())
