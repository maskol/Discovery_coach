#!/usr/bin/env python3
"""
Test MCP Server Connection
Run this script to verify your MCP servers are reachable and configured correctly.
"""

import os
import asyncio
from dotenv import load_dotenv

load_dotenv()


async def test_mcp_connection():
    """Test connection to configured MCP servers."""

    print("🔍 Checking MCP Configuration...\n")

    # Check environment variables
    jira_url = os.getenv("MCP_JIRA_URL")
    jira_token = os.getenv("JIRA_TOKEN")
    confluence_url = os.getenv("MCP_CONFLUENCE_URL")
    confluence_token = os.getenv("CONFLUENCE_TOKEN")

    print("📋 Configuration Status:")
    print(
        f"  Jira URL: {'✓ Set' if jira_url else '✗ Missing'} - {jira_url if jira_url else 'Not configured'}"
    )
    print(
        f"  Jira Token: {'✓ Set' if jira_token else '✗ Missing'} - {'[HIDDEN]' if jira_token else 'Not configured'}"
    )
    print(
        f"  Confluence URL: {'✓ Set' if confluence_url else '✗ Missing'} - {confluence_url if confluence_url else 'Not configured'}"
    )
    print(
        f"  Confluence Token: {'✓ Set' if confluence_token else '✗ Missing'} - {'[HIDDEN]' if confluence_token else 'Not configured'}"
    )
    print()

    # Check if using placeholder values
    if jira_url and "your-mcp-server.com" in jira_url:
        print(
            "⚠️  WARNING: Using placeholder Jira URL. Please update .env with actual MCP server URL."
        )
        return

    if confluence_url and "your-mcp-server.com" in confluence_url:
        print(
            "⚠️  WARNING: Using placeholder Confluence URL. Please update .env with actual MCP server URL."
        )
        return

    if not jira_url and not confluence_url:
        print(
            "❌ No MCP servers configured. Please add MCP_JIRA_URL or MCP_CONFLUENCE_URL to .env"
        )
        return

    # Try to connect to MCP servers
    print("🔌 Attempting to connect to MCP servers...\n")

    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient

        # Build config for available servers
        mcp_config = {}

        if jira_url and jira_token and "your-mcp-server.com" not in jira_url:
            mcp_config["jira"] = {
                "url": jira_url,
                "headers": {"Authorization": f"Bearer {jira_token}"},
                "transport": "sse",
            }

        if (
            confluence_url
            and confluence_token
            and "your-mcp-server.com" not in confluence_url
        ):
            mcp_config["confluence"] = {
                "url": confluence_url,
                "headers": {"Authorization": f"Bearer {confluence_token}"},
                "transport": "sse",
            }

        if not mcp_config:
            print("❌ No valid MCP servers configured")
            return

        # Connect to MCP servers
        async with MultiServerMCPClient(mcp_config) as client:
            print("✓ MCP client initialized\n")

            # Get available tools
            tools = client.get_tools()

            print(f"✅ SUCCESS! Connected to MCP servers")
            print(f"📦 Loaded {len(tools)} tools:\n")

            for tool in tools:
                print(f"  • {tool.name}")
                if hasattr(tool, "description") and tool.description:
                    print(f"    {tool.description[:80]}...")
                print()

            print(f"\n🎉 MCP integration is ready to use!")

    except ImportError:
        print("❌ langchain-mcp-adapters not installed")
        print("\nInstall with:")
        print("  source venv/bin/activate")
        print("  pip install langchain-mcp-adapters langgraph")

    except Exception as e:
        print(f"❌ Connection failed: {type(e).__name__}")
        print(f"   Error: {str(e)}\n")
        print("Troubleshooting steps:")
        print("  1. Verify MCP server URLs are correct and reachable")
        print("  2. Check that authentication tokens are valid")
        print("  3. Ensure your network/VPN allows SSE connections")
        print("  4. Test URL manually: curl -H 'Authorization: Bearer TOKEN' MCP_URL")


if __name__ == "__main__":
    asyncio.run(test_mcp_connection())
