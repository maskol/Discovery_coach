"""
LangGraph Workflow for Discovery Coach
Implements stateful conversation flows with conditional routing and self-correction
"""

import operator
import time
from typing import Annotated, Literal, Sequence, TypedDict

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages

# Import local monitoring
from local_monitoring import log_node_execution, logger, metrics_collector

# ============================================================================
# State Schema
# ============================================================================


class DiscoveryState(TypedDict):
    """
    State passed between nodes in the workflow.

    This captures all information needed throughout the conversation flow.
    """

    # Messages
    messages: Annotated[Sequence[BaseMessage], add_messages]

    # User input and context
    user_message: str
    context_type: (
        str  # "strategic-initiative", "epic", "feature", "story", "pi-objective"
    )

    # Active context from previous work
    active_epic: str | None
    active_feature: str | None
    active_strategic_initiative: str | None

    # Intent classification
    intent: str  # "draft", "question", "evaluate", "outline", "clarify"
    confidence_score: float

    # Retrieval
    retrieval_query: str
    retrieved_docs: list
    context_text: str

    # Generation
    generated_response: str

    # Validation and quality
    needs_clarification: bool
    needs_retry: bool
    validation_issues: list[str]
    retry_count: int

    # Model configuration
    model: str
    provider: str
    temperature: float

    # Metadata
    is_summary: bool
    is_draft: bool
    error_message: str | None


# ============================================================================
# Node Functions
# ============================================================================


@log_node_execution("classify_intent")
async def classify_intent_node(state: DiscoveryState) -> DiscoveryState:
    """
    Classify user intent to determine workflow path.

    Routes to:
    - draft: User wants to create Epic/Feature/Strategic Initiative
    - question: User has a question about existing content
    - evaluate: User wants feedback
    - outline: User wants to outline structure
    """
    import json

    from langchain_core.prompts import ChatPromptTemplate
    from langchain_openai import ChatOpenAI
    from ollama_config import create_ollama_llm

    user_message = state["user_message"].lower()

    # Quick heuristic classification
    if (
        "draft" in user_message
        or "create" in user_message
        or "help me write" in user_message
    ):
        intent = "draft"
        confidence = 0.9
    elif (
        "evaluate" in user_message
        or "review" in user_message
        or "feedback" in user_message
    ):
        intent = "evaluate"
        confidence = 0.9
    elif "outline" in user_message or "structure" in user_message:
        intent = "outline"
        confidence = 0.9
    elif "summary" in user_message or "summarize" in user_message:
        intent = "question"  # Treat as question but flag as summary
        confidence = 0.9
    else:
        # Use LLM for complex cases
        try:
            if state["provider"] == "ollama":
                llm = create_ollama_llm(model=state["model"], temperature=0.1)
            else:
                llm = ChatOpenAI(model=state["model"], temperature=0.1)

            classification_prompt = ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        """Analyze the user's message and classify their intent.
                
Intents:
- draft: User wants to create/draft an Epic, Feature, Story, or Strategic Initiative
- question: User has a question or needs information
- evaluate: User wants feedback on existing work
- outline: User wants to see structure/outline before creating

Return ONLY a JSON object: {{"intent": "...", "confidence": 0.0-1.0}}""",
                    ),
                    ("human", "Message: {message}\nContext Type: {context_type}"),
                ]
            )

            chain = classification_prompt | llm
            response = chain.invoke(
                {
                    "message": state["user_message"],
                    "context_type": state["context_type"],
                }
            )

            # Parse JSON response
            result = json.loads(response.content)
            intent = result.get("intent", "question")
            confidence = result.get("confidence", 0.7)
        except Exception as e:
            print(f"Intent classification error: {e}, defaulting to 'question'")
            intent = "question"
            confidence = 0.5

    print(f"🎯 Intent classified: {intent} (confidence: {confidence:.2f})")

    return {
        **state,
        "intent": intent,
        "confidence_score": confidence,
    }


@log_node_execution("build_context")
async def build_context_node(state: DiscoveryState) -> DiscoveryState:
    """
    Build contextual query with active Epic/Feature/Strategic Initiative.
    """
    context_parts = []

    # Don't include full context for summaries (too large)
    if not state.get("is_summary", False):
        if state.get("active_strategic_initiative"):
            context_parts.append(
                f"[ACTIVE STRATEGIC INITIATIVE]\n{state['active_strategic_initiative']}\n"
            )
        if state.get("active_epic"):
            context_parts.append(f"[ACTIVE EPIC]\n{state['active_epic']}\n")
        if state.get("active_feature"):
            context_parts.append(f"[ACTIVE FEATURE]\n{state['active_feature']}\n")

    # Build full query
    if context_parts:
        full_query = (
            "".join(context_parts) + f"\n[USER QUESTION]\n{state['user_message']}"
        )
    else:
        full_query = state["user_message"]

    # Add context-specific keywords for better retrieval
    retrieval_query = full_query
    if state["context_type"] == "strategic-initiative":
        retrieval_query = f"Strategic Initiative {full_query}"
    elif state["context_type"] == "pi-objective":
        retrieval_query = f"PI Objectives {full_query}"

    print(f"📝 Built context query (length: {len(full_query)})")

    return {
        **state,
        "retrieval_query": retrieval_query,
    }


@log_node_execution("retrieve_context")
async def retrieve_context_node(state: DiscoveryState) -> DiscoveryState:
    """
    Retrieve relevant documents from vector store.
    """
    # Skip retrieval for summaries
    if state.get("is_summary", False):
        print("⏭️  Skipping retrieval for summary request")
        return {
            **state,
            "context_text": "Summary request - using active context only.",
            "retrieved_docs": [],
        }

    try:
        # Import retriever from app module
        import os
        import sys

        sys.path.insert(0, os.path.dirname(__file__))

        # Dynamically import to avoid circular dependency
        from app import retriever as app_retriever

        docs = app_retriever.invoke(state["retrieval_query"])
        context_text = "\n\n".join([doc.page_content for doc in docs])

        print(f"📚 Retrieved {len(docs)} documents for {state['context_type']}")

        return {
            **state,
            "retrieved_docs": [
                {"content": doc.page_content, "metadata": doc.metadata} for doc in docs
            ],
            "context_text": context_text,
        }
    except Exception as e:
        print(f"⚠️  Retrieval error: {e}")
        return {
            **state,
            "context_text": "Retrieval failed - proceeding with active context only.",
            "retrieved_docs": [],
        }


@log_node_execution("generate_response")
async def generate_response_node(state: DiscoveryState) -> DiscoveryState:
    """
    Generate AI response using LLM.
    """
    from discovery_coach import load_prompt_file
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain_openai import ChatOpenAI
    from ollama_config import create_ollama_llm

    # Determine timeout based on request type
    is_draft = state.get("is_draft", False)
    is_summary = state.get("is_summary", False)
    llm_timeout = 240 if (is_draft or is_summary) else 90

    # Create LLM
    if state["provider"] == "ollama":
        llm = create_ollama_llm(
            model=state["model"],
            temperature=state["temperature"],
            timeout=llm_timeout,
        )
    else:
        llm = ChatOpenAI(
            model=state["model"],
            temperature=state["temperature"],
            timeout=llm_timeout,
            max_retries=1,
        )

    # Load context-aware system prompt
    system_prompt = load_prompt_file("system_prompt.txt")

    if state["context_type"] == "strategic-initiative":
        system_prompt += "\n\nYou are currently helping with a Strategic Initiative. Focus on business outcomes, strategic alignment, customer segments, and high-level planning. Use the Strategic Initiative template from the knowledge base."
    elif state["context_type"] == "pi-objective":
        system_prompt += "\n\nYou are currently helping with PI Objectives. Focus on objectives, key results, and committed/uncommitted items for the Program Increment."

    # Build prompt
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("system", "Content from internal documents:\n{context}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{user_input}"),
        ]
    )

    # Create chain
    chain = prompt | llm

    # Get chat history (limited to prevent context overflow)
    max_history = 0 if is_summary else (12 if is_draft else 10)
    chat_history = list(state["messages"][-max_history:]) if max_history > 0 else []

    try:
        print(f"🤖 Generating response with {state['model']} (timeout: {llm_timeout}s)")

        # Use invoke instead of ainvoke for simplicity (LangChain handles sync/async)
        response = chain.invoke(
            {
                "user_input": state["retrieval_query"],
                "context": state["context_text"],
                "chat_history": chat_history,
            },
            config={
                "metadata": {
                    "context_type": state["context_type"],
                    "model": state["model"],
                    "provider": state["provider"],
                    "intent": state["intent"],
                    "retry_count": state.get("retry_count", 0),
                },
                "tags": [
                    state["context_type"],
                    state["provider"],
                    f"model:{state['model']}",
                    state["intent"],
                ],
            },
        )

        print(f"✅ Generated response ({len(response.content)} chars)")

        return {
            **state,
            "generated_response": response.content,
            "error_message": None,
        }
    except Exception as e:
        print(f"❌ Generation error: {e}")
        return {
            **state,
            "error_message": str(e),
            "needs_retry": True,
        }


@log_node_execution("validate_response")
async def validate_response_node(state: DiscoveryState) -> DiscoveryState:
    """
    Validate response quality and completeness.

    Checks:
    - Response length is reasonable
    - For drafts: Contains required template sections
    - No obvious errors or incomplete sections
    """
    response = state["generated_response"]
    issues = []

    # Check length
    if len(response) < 50:
        issues.append("Response too short")
    elif len(response) > 5000 and not state.get("is_draft", False):
        issues.append("Response very long - might be overly detailed")

    # For draft requests, check template compliance
    if state["intent"] == "draft":
        if state["context_type"] == "epic":
            required = ["EPIC NAME", "EPIC HYPOTHESIS STATEMENT", "BUSINESS CONTEXT"]
            missing = [section for section in required if section not in response]
            if missing:
                issues.append(f"Missing sections: {', '.join(missing)}")
        elif state["context_type"] == "strategic-initiative":
            required = [
                "INITIATIVE NAME",
                "STRATEGIC CONTEXT",
                "CUSTOMER / USER SEGMENT",
            ]
            missing = [section for section in required if section not in response]
            if missing:
                issues.append(f"Missing sections: {', '.join(missing)}")
        elif state["context_type"] == "feature":
            required = ["FEATURE NAME", "USER STORY", "ACCEPTANCE CRITERIA"]
            missing = [section for section in required if section not in response]
            if missing:
                issues.append(f"Missing sections: {', '.join(missing)}")
        elif state["context_type"] == "story":
            required = ["USER STORY", "ACCEPTANCE CRITERIA"]
            missing = [section for section in required if section not in response]
            if missing:
                issues.append(f"Missing sections: {', '.join(missing)}")
        elif state["context_type"] == "pi-objective":
            required = ["OBJECTIVE", "KEY RESULTS"]
            missing = [section for section in required if section not in response]
            if missing:
                issues.append(f"Missing sections: {', '.join(missing)}")

    # Check for incomplete sections (ends with "..." or "[To be filled]")
    if "..." in response[-100:] or "[To be filled]" in response:
        issues.append("Response appears incomplete")

    # Determine if retry is needed
    needs_retry = len(issues) > 0 and state.get("retry_count", 0) < 2
    needs_clarification = len(issues) > 0 and state.get("confidence_score", 1.0) < 0.7

    if issues:
        print(f"⚠️  Validation issues: {', '.join(issues)}")
        if needs_retry:
            print(f"🔄 Will retry (attempt {state.get('retry_count', 0) + 1}/2)")
    else:
        print("✅ Response validated successfully")

    return {
        **state,
        "validation_issues": issues,
        "needs_retry": needs_retry and len(issues) > 0,
        "needs_clarification": needs_clarification,
    }


# ============================================================================
# Routing Functions
# ============================================================================


def should_retrieve_context(state: DiscoveryState) -> Literal["retrieve", "generate"]:
    """Decide if we need to retrieve context or can skip to generation."""
    # Skip retrieval for summaries
    if state.get("is_summary", False):
        return "generate"
    # Skip retrieval if we have error and retrying
    if state.get("error_message"):
        return "generate"
    return "retrieve"


def should_continue_after_validation(
    state: DiscoveryState,
) -> Literal["retry", "clarify", "end"]:
    """
    Routing logic after validation.

    - retry: Quality issues and can retry (retry_count < 2)
    - clarify: Low confidence and needs more info from user
    - end: Success or max retries reached
    """
    # Check for errors
    if state.get("error_message"):
        if state.get("retry_count", 0) < 2:
            return "retry"
        else:
            return "end"  # Max retries reached, return error

    # Check validation
    if state.get("needs_retry", False):
        return "retry"

    if state.get("needs_clarification", False):
        return "clarify"

    return "end"


@log_node_execution("increment_retry")
async def increment_retry_on_retry(state: DiscoveryState) -> DiscoveryState:
    """Increment retry count when retrying."""
    return {
        **state,
        "retry_count": state.get("retry_count", 0) + 1,
    }


# ============================================================================
# Graph Builder
# ============================================================================


def create_discovery_workflow() -> StateGraph:
    """
    Create the LangGraph workflow for Discovery Coach conversations.

    Flow:
    1. Classify intent (draft vs question vs evaluate)
    2. Build context with active Epic/Feature
    3. Retrieve relevant documents (conditional)
    4. Generate response
    5. Validate response
    6. Retry if needed (max 2 times) or ask for clarification
    """
    workflow = StateGraph(DiscoveryState)

    # Add nodes
    workflow.add_node("classify_intent", classify_intent_node)
    workflow.add_node("build_context", build_context_node)
    workflow.add_node("retrieve_context", retrieve_context_node)
    workflow.add_node("generate_response", generate_response_node)
    workflow.add_node("validate_response", validate_response_node)
    workflow.add_node("increment_retry", increment_retry_on_retry)

    # Define edges
    workflow.set_entry_point("classify_intent")
    workflow.add_edge("classify_intent", "build_context")

    # Conditional: skip retrieval for summaries
    workflow.add_conditional_edges(
        "build_context",
        should_retrieve_context,
        {
            "retrieve": "retrieve_context",
            "generate": "generate_response",
        },
    )

    workflow.add_edge("retrieve_context", "generate_response")
    workflow.add_edge("generate_response", "validate_response")

    # Conditional: retry, clarify, or end
    workflow.add_conditional_edges(
        "validate_response",
        should_continue_after_validation,
        {
            "retry": "increment_retry",  # Increment counter first
            "clarify": END,  # Return to user for clarification
            "end": END,  # Success!
        },
    )

    # After incrementing retry, go back to generate
    workflow.add_edge("increment_retry", "generate_response")

    return workflow.compile()


# ============================================================================
# Helper Functions
# ============================================================================


def prepare_initial_state(
    message: str,
    context_type: str,
    model: str,
    provider: str,
    temperature: float,
    active_epic: str | None = None,
    active_feature: str | None = None,
    active_strategic_initiative: str | None = None,
    chat_history: list | None = None,
) -> DiscoveryState:
    """
    Prepare initial state for workflow execution.
    """
    # Convert chat history to messages
    messages = []
    if chat_history:
        for msg in chat_history:
            if isinstance(msg, dict):
                if msg.get("type") == "human":
                    messages.append(HumanMessage(content=msg.get("content", "")))
                elif msg.get("type") == "ai":
                    messages.append(AIMessage(content=msg.get("content", "")))
            else:
                messages.append(msg)

    # Detect summary and draft requests
    is_summary = "summary" in message.lower() or "summarize" in message.lower()
    is_draft = "draft" in message.lower()

    return DiscoveryState(
        messages=messages,
        user_message=message,
        context_type=context_type,
        active_epic=active_epic,
        active_feature=active_feature,
        active_strategic_initiative=active_strategic_initiative,
        intent="",  # Will be set by classify_intent
        confidence_score=0.0,
        retrieval_query="",
        retrieved_docs=[],
        context_text="",
        generated_response="",
        needs_clarification=False,
        needs_retry=False,
        validation_issues=[],
        retry_count=0,
        model=model,
        provider=provider,
        temperature=temperature,
        is_summary=is_summary,
        is_draft=is_draft,
        error_message=None,
    )
