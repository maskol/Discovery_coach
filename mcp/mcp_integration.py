"""
MCP Integration Module for Discovery Coach
Adds tool-calling capabilities by directly passing MCP tools to the agent.

Usage:
1. Use MCP Inspector (https://modelcontextprotocol.io/docs/tools/inspector) to find auth
2. Get the MCP tools from any server
3. Pass tools directly to the agent

This is simpler than managing separate MCP server connections.
"""

import asyncio
import os
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

load_dotenv()


class MCPDiscoveryCoach:
    """
    Enhanced Discovery Coach with MCP tool integration.

    Simple approach: Just pass MCP tools directly to the agent.
    No need for complex server management.
    """

    def __init__(
        self,
        tools: Optional[List] = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
    ):
        """
        Initialize MCP-enhanced Discovery Coach.

        Args:
            tools: List of MCP tools to give the agent (from any MCP server)
            model: OpenAI model name
            temperature: LLM temperature
        """
        self.tools = tools or []
        self.model = model
        self.temperature = temperature
        self.agent = None

    async def initialize(self):
        """Initialize agent with the provided MCP tools."""
        if not self.tools:
            print("⚠️  No tools provided. Agent will run without MCP capabilities.")

        # Create LLM
        llm = ChatOpenAI(
            model=self.model,
            temperature=self.temperature,
            timeout=60,
            max_retries=1,
        )

        # Create ReAct agent with MCP tools
        self.agent = create_react_agent(llm, self.tools)
        print(f"✓ Agent initialized with {len(self.tools)} tools")

        if self.tools:
            print(
                "  Available tools:",
                [t.name if hasattr(t, "name") else str(t) for t in self.tools[:5]],
            )
            if len(self.tools) > 5:
                print(f"  ... and {len(self.tools) - 5} more")

    async def close(self):
        """Clean up resources (no-op for direct tool approach)."""
        print("✓ Agent cleanup complete")

    async def chat(
        self,
        message: str,
        rag_context: Optional[str] = None,
        chat_history: Optional[List] = None,
    ) -> Dict[str, Any]:
        """
        Process a chat message with MCP tool support.

        Args:
            message: User's message
            rag_context: Optional RAG-retrieved context to inject
            chat_history: Optional conversation history

        Returns:
            {
                "response": str,
                "tool_calls": List[dict],  # Tools that were invoked
                "success": bool
            }
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized. Call initialize() first.")

        # Build messages list
        messages = []

        # Add RAG context if provided
        if rag_context:
            messages.append(
                (
                    "system",
                    f"Content from internal knowledge base:\n{rag_context}",
                )
            )

        # Add chat history
        if chat_history:
            messages.extend(chat_history)

        # Add user message
        messages.append(("user", message))

        # Invoke agent
        try:
            result = await self.agent.ainvoke({"messages": messages})

            # Extract response and tool calls
            final_message = result["messages"][-1]
            response_text = (
                final_message.content
                if hasattr(final_message, "content")
                else str(final_message)
            )

            # Track which tools were called
            tool_calls = []
            for msg in result["messages"]:
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    for tc in msg.tool_calls:
                        tool_calls.append(
                            {
                                "tool": tc.get("name", "unknown"),
                                "args": tc.get("args", {}),
                            }
                        )

            return {
                "response": response_text,
                "tool_calls": tool_calls,
                "success": True,
            }

        except Exception as e:
            print(f"❌ MCP agent error: {e}")
            return {
                "response": f"Error: {str(e)}",
                "tool_calls": [],
                "success": False,
            }

    def has_tools(self) -> bool:
        """Check if MCP tools are available."""
        return len(self.tools) > 0

    def list_tools(self) -> List[str]:
        """Get list of available tool names."""
        return [t.name for t in self.tools]


# ============================================================================
# Helper function for easy integration into existing app.py
# ============================================================================


async def create_mcp_coach(
    tools: Optional[List] = None,
    model: str = "gpt-4o-mini",
    temperature: float = 0.7,
) -> MCPDiscoveryCoach:
    """
    Convenience function to create and initialize MCP Discovery Coach.

    Args:
        tools: List of MCP tools from any MCP server
        model: OpenAI model to use
        temperature: LLM temperature

    Usage in app.py:
        from mcp_integration import create_mcp_coach

        # Get your MCP tools from wherever they come from
        # (use MCP Inspector to figure out auth and get tools)
        mcp_tools = [...]  # Your MCP tools here

        mcp_coach = await create_mcp_coach(tools=mcp_tools)

        # In your /api/chat endpoint:
        result = await mcp_coach.chat(
            message=request.message,
            rag_context=context_text,  # from your existing retriever
            chat_history=active_context["chat_history"]
        )
    """
    coach = MCPDiscoveryCoach(tools=tools, model=model, temperature=temperature)
    await coach.initialize()
    return coach


# ============================================================================
# Standalone test
# ============================================================================


async def test_mcp_integration():
    """Test MCP integration with sample tools."""
    print("\n🧪 Testing MCP Discovery Coach Integration\n")

    # Example: Create a mock tool for testing
    # In real usage, you'd get these from your MCP server using the Inspector
    from langchain.tools import Tool

    def mock_jira_tool(query: str) -> str:
        """Mock Jira search tool for testing."""
        return f"Found 3 Jira issues matching '{query}'"

    sample_tools = [
        Tool(
            name="search_jira",
            func=mock_jira_tool,
            description="Search for Jira issues",
        )
    ]

    # Create coach with sample tools
    coach = MCPDiscoveryCoach(tools=sample_tools)

    try:
        # Initialize
        await coach.initialize()

        # Test query
        result = await coach.chat(
            message="Search Jira for login bug issues",
            rag_context="User is working on SAFe Epic definition.",
        )

        print(f"\n✓ Response: {result['response']}")
        print(f"\n✓ Tools called: {result['tool_calls']}")

    finally:
        await coach.close()


if __name__ == "__main__":
    asyncio.run(test_mcp_integration())
