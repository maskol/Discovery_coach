"""
FastAPI Server for Discovery Coach GUI
Connects the HTML/JavaScript frontend to the discovery_coach.py backend
"""

import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Add backend directory to path to import discovery_coach
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

from discovery_coach import active_context, initialize_vector_store
from langchain_core.messages import AIMessage, HumanMessage
from template_db import TemplateDatabase

app = FastAPI(title="Discovery Coach API", version="1.0.0")

# Initialize template database
template_db = TemplateDatabase()

# Enable CORS for frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic models for request validation
class ChatRequest(BaseModel):
    message: str
    activeEpic: Optional[str] = None
    activeFeature: Optional[str] = None
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    provider: str = "openai"  # "openai" or "ollama"


class EvaluateRequest(BaseModel):
    type: str
    content: str


class OutlineRequest(BaseModel):
    type: str


class ClearRequest(BaseModel):
    type: str = "all"


class SessionSaveRequest(BaseModel):
    activeEpic: Optional[str] = None
    activeFeature: Optional[str] = None
    activeEpicId: Optional[int] = None
    activeFeatureId: Optional[int] = None
    conversationHistory: list = []
    messages: str = ""


class SessionLoadRequest(BaseModel):
    filename: str


class SessionDeleteRequest(BaseModel):
    filenames: List[str]


class FillTemplateRequest(BaseModel):
    template_type: str  # "epic", "feature", or "story"
    conversationHistory: list = []
    activeEpic: Optional[str] = None
    activeFeature: Optional[str] = None
    activeStory: Optional[str] = None
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    provider: str = "openai"


class SaveTemplateRequest(BaseModel):
    template_type: str  # "epic", "feature", or "story"
    name: str
    content: str
    epic_id: Optional[int] = None
    epic_hypothesis_statement: Optional[str] = None
    business_outcome: Optional[str] = None
    leading_indicators: Optional[str] = None
    benefit_hypothesis: Optional[str] = None
    acceptance_criteria: Optional[str] = None
    wsjf: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict] = None
    tags: Optional[List[str]] = None


class UpdateTemplateRequest(BaseModel):
    template_id: int
    template_type: str  # "epic" or "feature"
    name: Optional[str] = None
    content: Optional[str] = None
    epic_id: Optional[int] = None
    epic_hypothesis_statement: Optional[str] = None
    business_outcome: Optional[str] = None
    leading_indicators: Optional[str] = None
    metadata: Optional[Dict] = None
    tags: Optional[List[str]] = None


class DeleteTemplateRequest(BaseModel):
    template_id: int
    template_type: str  # "epic" or "feature"


class LoadTemplateRequest(BaseModel):
    template_id: int
    template_type: str  # "epic" or "feature"


class ExportTemplateRequest(BaseModel):
    template_id: Optional[int] = None
    template_type: str  # "epic" or "feature"
    export_all: bool = False


class ExtractFeaturesRequest(BaseModel):
    activeEpic: Optional[str] = None
    conversationHistory: list = []
    model: str = "gpt-4o-mini"
    temperature: float = 0.7
    provider: str = "openai"


# Initialize the Discovery Coach
print("Initializing Discovery Coach...")
# Use Ollama if available, otherwise fall back to OpenAI
use_ollama = os.getenv("OLLAMA_BASE_URL") and os.getenv("OLLAMA_CHAT_MODEL")
if use_ollama:
    print("Using Ollama for local LLM inference")
else:
    print("Using OpenAI for LLM inference")
chain, retriever = initialize_vector_store(use_ollama=bool(use_ollama))
retrieval_chain = chain
print(f"Discovery Coach ready! Retriever type: {type(retriever)}")
print(f"Chain type: {type(chain)}")


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Handle chat messages from the frontend"""
    try:
        if not request.message:
            raise HTTPException(status_code=400, detail="No message provided")

        # Update active context if provided
        if request.activeEpic:
            active_context["epic"] = request.activeEpic
        if request.activeFeature:
            active_context["feature"] = request.activeFeature

        # Check if this is a summary or draft request (needs special optimization)
        is_summary_request = (
            "summary" in request.message.lower()
            or "summarize" in request.message.lower()
        )
        is_draft_request = "draft" in request.message.lower() and (
            "epic" in request.message.lower() or "feature" in request.message.lower()
        )

        # Build the full query with context
        # For summaries, don't include the full Epic/Feature - they're too large
        context_parts = []
        if not is_summary_request:
            if active_context.get("epic"):
                context_parts.append(f"[ACTIVE EPIC]\n{active_context['epic']}\n")
            if active_context.get("feature"):
                context_parts.append(f"[ACTIVE FEATURE]\n{active_context['feature']}\n")

        full_query = request.message
        if context_parts:
            full_query = (
                "".join(context_parts) + f"\n[USER QUESTION]\n{request.message}"
            )

        # Get relevant context from retriever
        # For summaries, skip retrieval entirely - we don't need template docs
        if is_summary_request:
            print("Summary request - skipping retrieval")
            context_text = "Summary request - using active Epic/Feature context only."
        else:
            print(
                f"Regular request - invoking retriever with query length: {len(full_query)}"
            )
            try:
                docs = retriever.invoke(full_query)
                print(f"Retriever returned {len(docs)} documents")
                context_text = "\n\n".join([doc.page_content for doc in docs])
            except Exception as e:
                print(f"⚠️ Retriever error: {e} - proceeding without RAG context")
                context_text = "Retrieval failed - using only active context."

        # Initialize chat history if not exists
        if "chat_history" not in active_context:
            active_context["chat_history"] = []

        print(f"Creating LLM instance with provider: {request.provider}")
        # Create LLM with requested model, temperature, and provider
        # Use longer timeout for draft and summary requests (4 minutes)
        llm_timeout = 240 if (is_draft_request or is_summary_request) else 90

        if request.provider == "ollama":
            from ollama_config import create_ollama_llm

            llm = create_ollama_llm(
                model=request.model,
                temperature=request.temperature,
                timeout=llm_timeout,
            )
            print(
                f"Using Ollama LLM with model: {request.model}, timeout: {llm_timeout}s"
            )
        else:
            from langchain_openai import ChatOpenAI

            llm = ChatOpenAI(
                model=request.model,
                temperature=request.temperature,
                timeout=llm_timeout,  # Longer timeout for complex operations
                max_retries=1,  # Only retry once
            )
            print(
                f"Using OpenAI LLM with model: {request.model}, timeout: {llm_timeout}s"
            )

        print("Loading system prompt...")
        # Load system prompt
        from discovery_coach import load_prompt_file
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

        system_prompt = load_prompt_file("system_prompt.txt")
        print(f"System prompt loaded: {len(system_prompt)} chars")

        print("Creating prompt template...")
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("system", "Content from internal documents:\n{context}"),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{user_input}"),
            ]
        )
        print("Building chain...")
        chain = prompt | llm
        print("Chain built successfully")

        # Limit chat history to prevent context overflow
        # This keeps the conversation flowing while preventing excessive token usage
        # Different limits for different request types
        if is_summary_request:
            max_history_messages = (
                0  # No chat history for summaries - rely on Epic/Feature context only
            )
        elif is_draft_request:
            max_history_messages = (
                12  # Draft requests get 6 turns - enough context without overload
            )
        else:
            max_history_messages = 10  # Normal conversation gets 5 turns

        recent_history = (
            active_context["chat_history"][-max_history_messages:]
            if len(active_context["chat_history"]) > max_history_messages
            else active_context["chat_history"]
        )

        # Get response from the LLM chain with proper parameters
        print(f"Invoking LLM with model={request.model}, temp={request.temperature}")
        print(
            f"Context length: {len(context_text)}, History messages: {len(recent_history)}"
        )
        print(f"Full query length: {len(full_query)}")

        import time

        start_time = time.time()

        try:
            print("About to call chain.invoke()...")

            response = chain.invoke(
                {
                    "user_input": full_query,
                    "context": context_text,
                    "chat_history": recent_history,
                }
            )
            elapsed = time.time() - start_time
            print(
                f"✓ LLM response received in {elapsed:.2f}s: {len(response.content)} chars"
            )
        except Exception as e:
            elapsed = time.time() - start_time
            print(
                f"❌ LLM invocation error after {elapsed:.2f}s: {type(e).__name__}: {e}"
            )
            raise

        # Update chat history with this conversation turn
        from langchain_core.messages import AIMessage, HumanMessage

        active_context["chat_history"].append(HumanMessage(content=request.message))
        active_context["chat_history"].append(AIMessage(content=response.content))

        # Auto-detect and store Epic/Feature content
        response_text = response.content

        # Check for Epic content (look for EPIC NAME or Epic template structure)
        if ("EPIC NAME" in response_text or "1. EPIC NAME" in response_text) and (
            "EPIC HYPOTHESIS STATEMENT" in response_text
            or "BUSINESS CONTEXT" in response_text
        ):
            # Extract Epic content - store the entire response as it likely contains the full Epic
            active_context["epic"] = response_text
            print("✅ Epic automatically detected and stored in active_context")

        # Check for Feature content
        elif ("FEATURE NAME" in response_text or "Feature Name:" in response_text) and (
            "USER STORY" in response_text or "ACCEPTANCE CRITERIA" in response_text
        ):
            active_context["feature"] = response_text
            print("✅ Feature automatically detected and stored in active_context")

        # Check for PI Objectives
        elif (
            "PI OBJECTIVE" in response_text
            or "Program Increment Objective" in response_text
        ):
            active_context["pi_objectives"] = response_text
            print(
                "✅ PI Objectives automatically detected and stored in active_context"
            )

        return {"response": response.content, "success": True}

    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/evaluate")
async def evaluate(request: EvaluateRequest):
    """Evaluate an Epic or Feature"""
    try:
        if not request.content:
            raise HTTPException(status_code=400, detail="No content provided")

        # Update active context
        if request.type == "epic":
            active_context["epic"] = request.content
            prompt = f"Please evaluate the following Epic against SAFe best practices:\n\n{request.content}"
        elif request.type == "feature":
            active_context["feature"] = request.content
            prompt = f"Please evaluate the following Feature against SAFe best practices:\n\n{request.content}"
        else:
            raise HTTPException(
                status_code=400, detail='Invalid type. Must be "epic" or "feature"'
            )

        # Get relevant context from retriever
        docs = retriever.invoke(prompt)
        context_text = "\n\n".join([doc.page_content for doc in docs])

        # Get evaluation from LLM
        response = retrieval_chain.invoke(
            {"user_input": prompt, "context": context_text, "chat_history": []}
        )

        return {
            "response": response.content,
            "success": True,
            "activeContext": active_context,
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in evaluate endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/outline")
async def outline(request: OutlineRequest):
    """Get outline of current Epic or Feature"""
    try:
        if request.type == "epic":
            if active_context.get("epic"):
                return {"content": active_context["epic"], "success": True}
            else:
                return {
                    "message": 'No active Epic. Use "Evaluate Epic" to load one.',
                    "success": True,
                    "content": None,
                }
        elif request.type == "feature":
            if active_context.get("feature"):
                return {"content": active_context["feature"], "success": True}
            else:
                return {
                    "message": 'No active Feature. Use "Evaluate Feature" to load one.',
                    "success": True,
                    "content": None,
                }
        else:
            raise HTTPException(status_code=400, detail="Invalid type")

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in outline endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/clear")
async def clear(request: ClearRequest):
    """Clear active context"""
    try:
        if request.type == "epic" or request.type == "all":
            active_context["epic"] = None
        if request.type == "feature" or request.type == "all":
            active_context["feature"] = None
        if request.type == "all":
            active_context["chat_history"] = []

        return {
            "success": True,
            "message": f"{request.type.capitalize()} context cleared",
            "activeContext": active_context,
        }

    except Exception as e:
        print(f"Error in clear endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Discovery Coach API"}


@app.get("/api/ollama/status")
async def ollama_status():
    """Check Ollama connection status and available models"""
    try:
        from ollama_config import test_ollama_connection

        result = test_ollama_connection()
        return result
    except Exception as e:
        return {"success": False, "message": f"Error checking Ollama status: {str(e)}"}


@app.get("/api/ollama/models")
async def ollama_models():
    """List available Ollama models"""
    try:
        from ollama_config import list_ollama_models

        models = list_ollama_models()
        return {"success": True, "models": models}
    except Exception as e:
        return {
            "success": False,
            "message": f"Error listing Ollama models: {str(e)}",
            "models": [],
        }


@app.post("/api/session/save")
async def save_session(request: SessionSaveRequest):
    """Save session to Session_storage folder"""
    try:
        import json
        from datetime import datetime

        # Create Session_storage directory if it doesn't exist
        project_root = os.path.dirname(os.path.dirname(__file__))
        storage_dir = os.path.join(project_root, "data", "Session_storage")
        os.makedirs(storage_dir, exist_ok=True)

        # Create session data including current active_context
        session = {
            "activeEpic": active_context.get("epic") or request.activeEpic,
            "activeFeature": active_context.get("feature") or request.activeFeature,
            "activeEpicId": request.activeEpicId,
            "activeFeatureId": request.activeFeatureId,
            "piObjectives": active_context.get("pi_objectives"),
            "conversationHistory": request.conversationHistory,
            "messages": request.messages,
            "timestamp": datetime.now().isoformat(),
        }

        # Generate filename with timestamp
        filename = f"session-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.json"
        filepath = os.path.join(storage_dir, filename)

        # Save to file
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(session, f, indent=2, ensure_ascii=False)

        return {
            "success": True,
            "filename": filename,
            "message": f"Session saved to {filename}",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/session/list")
async def list_sessions():
    """List all saved sessions"""
    try:
        from datetime import datetime

        project_root = os.path.dirname(os.path.dirname(__file__))
        storage_dir = os.path.join(project_root, "data", "Session_storage")
        storage_dir = os.path.join(project_root, "data", "Session_storage")

        if not os.path.exists(storage_dir):
            return {"success": True, "sessions": []}

        # Get all JSON files
        files = [f for f in os.listdir(storage_dir) if f.endswith(".json")]

        # Get file info
        sessions = []
        for filename in sorted(files, reverse=True):
            filepath = os.path.join(storage_dir, filename)
            stat = os.stat(filepath)
            sessions.append(
                {
                    "filename": filename,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "size": stat.st_size,
                }
            )

        return {"success": True, "sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/session/load")
async def load_session(request: SessionLoadRequest):
    """Load session from Session_storage folder"""
    try:
        import os

        project_root = os.path.dirname(os.path.dirname(__file__))
        storage_dir = os.path.join(project_root, "data", "Session_storage")
        filepath = os.path.join(storage_dir, request.filename)

        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="Session file not found")

        # Load session data
        with open(filepath, "r", encoding="utf-8") as f:
            session = json.load(f)

        # Update backend context
        active_context["epic"] = session.get("activeEpic")
        active_context["feature"] = session.get("activeFeature")
        active_context["pi_objectives"] = session.get("piObjectives")

        # Restore chat history from conversationHistory
        chat_history = []
        conversation = session.get("conversationHistory", [])
        for msg in conversation:
            if msg.get("role") == "user":
                chat_history.append(HumanMessage(content=msg.get("content", "")))
            elif msg.get("role") == "agent":
                chat_history.append(AIMessage(content=msg.get("content", "")))

        active_context["chat_history"] = chat_history

        # Load associated templates if IDs are present
        epic_template = None
        feature_template = None

        if session.get("activeEpicId"):
            epic_template = template_db.get_epic_template(session["activeEpicId"])

        if session.get("activeFeatureId"):
            feature_template = template_db.get_feature_template(
                session["activeFeatureId"]
            )

        return {
            "success": True,
            "session": session,
            "epicTemplate": epic_template,
            "featureTemplate": feature_template,
            "message": f"Session loaded from {request.filename}",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/session/delete")
async def delete_session(request: SessionDeleteRequest):
    """Delete one or more session files from Session_storage folder"""
    try:
        import json

        storage_dir = os.path.join(os.path.dirname(__file__), "Session_storage")
        deleted = []
        errors = []

        for filename in request.filenames:
            filepath = os.path.join(storage_dir, filename)

            if not os.path.exists(filepath):
                errors.append(f"{filename}: File not found")
                continue

            try:
                os.remove(filepath)
                deleted.append(filename)
            except Exception as e:
                errors.append(f"{filename}: {str(e)}")

        if deleted and not errors:
            return {
                "success": True,
                "message": f"Successfully deleted {len(deleted)} session(s)",
                "deleted": deleted,
            }
        elif deleted and errors:
            return {
                "success": True,
                "message": f"Deleted {len(deleted)} session(s), {len(errors)} error(s)",
                "deleted": deleted,
                "errors": errors,
            }
        else:
            return {
                "success": False,
                "message": "No sessions were deleted",
                "errors": errors,
            }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/fill-template")
async def fill_template(request: FillTemplateRequest):
    """Fill Epic or Feature template with conversation output"""
    try:
        template_type = request.template_type.lower()
        if template_type not in ["epic", "feature", "story"]:
            raise HTTPException(
                status_code=400,
                detail="Template type must be 'epic', 'feature', or 'story'",
            )

        # Load the appropriate template
        template_file = (
            "epic_template.txt"
            if template_type == "epic"
            else (
                "feature_template.txt"
                if template_type == "feature"
                else "user_story_template.txt"
            )
        )
        template_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "data",
            "knowledge_base",
            template_file,
        )

        with open(template_path, "r") as f:
            template_content = f.read()

        # Create LLM based on provider
        llm_timeout = 240  # 4 minutes for template filling
        if request.provider == "ollama":
            from ollama_config import create_ollama_llm

            llm = create_ollama_llm(
                model=request.model,
                temperature=request.temperature,
                timeout=llm_timeout,
            )
        else:
            from langchain_openai import ChatOpenAI

            llm = ChatOpenAI(
                model=request.model,
                temperature=request.temperature,
                timeout=llm_timeout,
                max_retries=1,
            )

        # Create conversation summary from history
        conversation_text = "\n\n".join(
            [
                f"{msg['role'].upper()}: {msg['content']}"
                for msg in request.conversationHistory[-20:]  # Last 20 messages
            ]
        )

        # Create prompt to fill template
        field_count = (
            19 if template_type == "epic" else 10 if template_type == "feature" else 8
        )
        prompt_text = f"""Based on the following discovery conversation, please fill out the {template_type.upper()} template with all {field_count} sections.

For each section in the template, replace the [Fill in here] placeholders with specific, detailed information based on the conversation.

If information is not available in the conversation for a particular field, provide a reasonable inference or note what additional information would be needed.

DISCOVERY CONVERSATION:
{conversation_text}

{template_type.upper()} CONTEXT:
Active Epic: {request.activeEpic or 'None'}
Active Feature: {request.activeFeature or 'None'}

TEMPLATE TO FILL:
{template_content}

Please provide the completed template with all sections filled in. Maintain the template structure and section headers."""

        # Get completion from LLM
        from langchain_core.messages import HumanMessage

        response = llm.invoke([HumanMessage(content=prompt_text)])
        filled_template = response.content

        return {
            "success": True,
            "template_type": template_type,
            "content": filled_template,
            "message": f"{template_type.capitalize()} template filled successfully",
        }

    except Exception as e:
        print(f"Error filling template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/template/save")
async def save_template(request: SaveTemplateRequest):
    """Save a filled template to the database"""
    try:
        template_type = request.template_type.lower()
        if template_type not in ["epic", "feature", "story"]:
            raise HTTPException(
                status_code=400,
                detail="Template type must be 'epic', 'feature', or 'story'",
            )

        if template_type == "epic":
            template_id = template_db.save_epic_template(
                name=request.name,
                content=request.content,
                epic_hypothesis_statement=request.epic_hypothesis_statement,
                business_outcome=request.business_outcome,
                leading_indicators=request.leading_indicators,
                metadata=request.metadata,
                tags=request.tags,
            )
        elif template_type == "feature":
            template_id = template_db.save_feature_template(
                name=request.name,
                content=request.content,
                epic_id=request.epic_id,
                benefit_hypothesis=request.benefit_hypothesis,
                acceptance_criteria=request.acceptance_criteria,
                wsjf=request.wsjf,
                metadata=request.metadata,
                tags=request.tags,
            )
        else:  # story
            template_id = template_db.save_story_template(
                name=request.name,
                content=request.content,
                feature_id=request.epic_id,  # Using epic_id field to pass feature_id
                description=request.description,
                acceptance_criteria=request.acceptance_criteria,
                metadata=request.metadata,
                tags=request.tags,
            )

        return {
            "success": True,
            "template_id": template_id,
            "message": f"{template_type.capitalize()} template saved successfully",
        }

    except Exception as e:
        print(f"Error saving template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/template/update")
async def update_template(request: UpdateTemplateRequest):
    """Update an existing template in the database"""
    try:
        template_type = request.template_type.lower()
        if template_type not in ["epic", "feature"]:
            raise HTTPException(
                status_code=400, detail="Template type must be 'epic' or 'feature'"
            )

        if template_type == "epic":
            success = template_db.update_epic_template(
                template_id=request.template_id,
                name=request.name,
                content=request.content,
                epic_hypothesis_statement=request.epic_hypothesis_statement,
                business_outcome=request.business_outcome,
                leading_indicators=request.leading_indicators,
                metadata=request.metadata,
                tags=request.tags,
            )
        else:
            success = template_db.update_feature_template(
                template_id=request.template_id,
                name=request.name,
                content=request.content,
                epic_id=request.epic_id,
                metadata=request.metadata,
                tags=request.tags,
            )

        if success:
            return {
                "success": True,
                "message": f"{template_type.capitalize()} template updated successfully",
            }
        else:
            raise HTTPException(status_code=404, detail="Template not found")

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/template/load")
async def load_template(request: LoadTemplateRequest):
    """Load a template from the database"""
    try:
        template_type = request.template_type.lower()
        if template_type not in ["epic", "feature", "story"]:
            raise HTTPException(
                status_code=400,
                detail="Template type must be 'epic', 'feature', or 'story'",
            )

        if template_type == "epic":
            template = template_db.get_epic_template(request.template_id)
        elif template_type == "feature":
            template = template_db.get_feature_template(request.template_id)
        else:  # story
            template = template_db.get_story_template(request.template_id)

        if template:
            return {"success": True, "template": template}
        else:
            raise HTTPException(status_code=404, detail="Template not found")

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error loading template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/template/list/{template_type}")
async def list_templates(
    template_type: str,
    limit: int = 100,
    offset: int = 0,
    epic_id: Optional[int] = None,
    search: Optional[str] = None,
):
    """List all templates of a given type"""
    try:
        template_type = template_type.lower()
        if template_type not in ["epic", "feature", "story"]:
            raise HTTPException(
                status_code=400,
                detail="Template type must be 'epic', 'feature', or 'story'",
            )

        if template_type == "epic":
            templates = template_db.list_epic_templates(
                limit=limit, offset=offset, search=search
            )
        elif template_type == "feature":
            templates = template_db.list_feature_templates(
                limit=limit, offset=offset, epic_id=epic_id, search=search
            )
            # Filter to exclude stories (only show actual features)
            templates = [
                t
                for t in templates
                if t.get("metadata", {}).get("parent_type") != "feature"
            ]
        else:  # story
            templates = template_db.list_story_templates(
                limit=limit, offset=offset, feature_id=epic_id, search=search
            )

        return {"success": True, "templates": templates, "count": len(templates)}

    except Exception as e:
        print(f"Error listing templates: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/template/delete")
async def delete_template(request: DeleteTemplateRequest):
    """Delete a template from the database"""
    try:
        template_type = request.template_type.lower()
        if template_type not in ["epic", "feature", "story"]:
            raise HTTPException(
                status_code=400,
                detail="Template type must be 'epic', 'feature', or 'story'",
            )

        if template_type == "epic":
            success = template_db.delete_epic_template(request.template_id)
        elif template_type == "feature":
            success = template_db.delete_feature_template(request.template_id)
        else:  # story
            success = template_db.delete_story_template(request.template_id)

        if success:
            return {
                "success": True,
                "message": f"{template_type.capitalize()} template deleted successfully",
            }
        else:
            raise HTTPException(status_code=404, detail="Template not found")

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error deleting template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/template/export")
async def export_template(request: ExportTemplateRequest):
    """Export template(s) as JSON"""
    try:
        template_type = request.template_type.lower()
        if template_type not in ["epic", "feature"]:
            raise HTTPException(
                status_code=400, detail="Template type must be 'epic' or 'feature'"
            )

        if request.export_all:
            # Export all templates
            if template_type == "epic":
                data = template_db.export_all_epics_as_json()
            else:
                data = template_db.export_all_features_as_json()

            return {
                "success": True,
                "export_type": "all",
                "template_type": template_type,
                "data": data,
                "count": len(data),
            }
        else:
            # Export single template
            if not request.template_id:
                raise HTTPException(
                    status_code=400,
                    detail="template_id required when export_all is false",
                )

            if template_type == "epic":
                data = template_db.export_epic_as_json(request.template_id)
            else:
                data = template_db.export_feature_as_json(request.template_id)

            if data:
                return {
                    "success": True,
                    "export_type": "single",
                    "template_type": template_type,
                    "data": data,
                }
            else:
                raise HTTPException(status_code=404, detail="Template not found")

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error exporting template: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/extract-features")
async def extract_features(request: ExtractFeaturesRequest):
    """Extract all feature proposals from conversation and fill templates for each"""
    try:
        # Build the conversation context
        conversation_text = "\n\n".join(
            [
                f"{'User' if msg.get('role') == 'user' else 'Coach'}: {msg.get('content', '')}"
                for msg in request.conversationHistory
            ]
        )

        # Load the feature template
        template_path = os.path.join(
            backend_dir, "../data/knowledge_base/feature_template.txt"
        )
        with open(template_path, "r", encoding="utf-8") as f:
            feature_template = f.read()

        # Ask LLM to extract all feature proposals and fill a template for each
        extraction_prompt = f"""You are extracting feature proposals from a conversation. Below is the conversation where multiple features were proposed for an Epic.

Active Epic:
{request.activeEpic or 'Not specified'}

Conversation:
{conversation_text}

I can see these feature proposals in the conversation. For EACH feature listed, you must create a SEPARATE filled template.

Feature Template Structure:
{feature_template}

CRITICAL INSTRUCTIONS - READ CAREFULLY:
1. Count the features: How many distinct features were proposed? (e.g., Feature 1, Feature 2, Feature 3, etc.)
2. Create ONE filled template for EACH feature - if there are 5 features, you MUST create 5 separate templates
3. Use the EXACT feature name/heading from the proposal (e.g., "Basic 5G Connectivity Service", "Free Antenna Installation")
4. After EACH completed template, add this exact line on its own: ---FEATURE_SEPARATOR---
5. Fill all fields based on the conversation - use "Not specified in conversation" for missing information
6. Do NOT combine multiple features into one template
7. Do NOT add any explanations - ONLY the filled templates separated by ---FEATURE_SEPARATOR---

Example format if there are 3 features:
[FILLED TEMPLATE FOR FEATURE 1]
---FEATURE_SEPARATOR---
[FILLED TEMPLATE FOR FEATURE 2]
---FEATURE_SEPARATOR---
[FILLED TEMPLATE FOR FEATURE 3]

NOW: Create a separate filled template for EVERY feature proposal. Begin now:"""

        # Create LLM instance
        if request.provider == "ollama":
            from ollama_config import create_ollama_llm

            llm = create_ollama_llm(
                model=request.model,
                temperature=request.temperature,
                timeout=180,
            )
        else:
            from langchain_openai import ChatOpenAI

            llm = ChatOpenAI(
                model=request.model,
                temperature=request.temperature,
                timeout=180,
                max_retries=1,
            )

        # Get response from LLM
        from langchain_core.messages import HumanMessage

        response = llm.invoke([HumanMessage(content=extraction_prompt)])

        # Parse response to extract individual features
        response_text = (
            response.content if hasattr(response, "content") else str(response)
        )

        # Debug: Print response for troubleshooting
        print(f"\n=== LLM Response for Feature Extraction ===")
        print(f"Response length: {len(response_text)} chars")
        print(f"First 500 chars: {response_text[:500]}")
        print(f"Contains separator: {'---FEATURE_SEPARATOR---' in response_text}")
        print(f"Number of separators: {response_text.count('---FEATURE_SEPARATOR---')}")
        print(f"===========================================\n")

        # Split by separator
        features = [
            f.strip()
            for f in response_text.split("---FEATURE_SEPARATOR---")
            if f.strip()
            and len(f.strip()) > 100  # Filter out very short/empty responses
        ]

        print(f"Extracted {len(features)} feature(s)")

        return {"success": True, "features": features, "count": len(features)}

    except Exception as e:
        print(f"Error extracting features: {str(e)}")
        import traceback

        traceback.print_exc()
        return {"success": False, "message": str(e), "features": []}


@app.post("/api/extract-stories")
async def extract_stories(request: ExtractFeaturesRequest):
    """Extract all user story proposals from conversation and fill templates for each"""
    try:
        # Build the conversation context
        conversation_text = "\n\n".join(
            [
                f"{'User' if msg.get('role') == 'user' else 'Coach'}: {msg.get('content', '')}"
                for msg in request.conversationHistory
            ]
        )

        # Load the user story template
        template_path = os.path.join(
            backend_dir, "../data/knowledge_base/user_story_template.txt"
        )
        with open(template_path, "r", encoding="utf-8") as f:
            story_template = f.read()

        # Ask LLM to extract all story proposals and fill a template for each
        extraction_prompt = f"""You are extracting user story proposals from a conversation. Below is the conversation where multiple user stories were proposed for a Feature.

Active Feature:
{request.activeEpic or 'Not specified'}

Conversation:
{conversation_text}

I can see these user story proposals in the conversation. For EACH story listed, you must create a SEPARATE filled template.

User Story Template Structure:
{story_template}

CRITICAL INSTRUCTIONS - READ CAREFULLY:
1. Count the stories: How many distinct user stories were proposed? (e.g., Story 1, Story 2, Story 3, etc.)
2. Create ONE filled template for EACH story - if there are 5 stories, you MUST create 5 separate templates
3. Use the EXACT story title from the proposal
4. After EACH completed template, add this exact line on its own: ---STORY_SEPARATOR---
5. Fill all fields based on the conversation - use "Not specified in conversation" for missing information
6. Do NOT combine multiple stories into one template
7. Do NOT add any explanations - ONLY the filled templates separated by ---STORY_SEPARATOR---

Example format if there are 3 stories:
[FILLED TEMPLATE FOR STORY 1]
---STORY_SEPARATOR---
[FILLED TEMPLATE FOR STORY 2]
---STORY_SEPARATOR---
[FILLED TEMPLATE FOR STORY 3]

NOW: Create a separate filled template for EVERY user story proposal. Begin now:"""

        # Create LLM instance
        if request.provider == "ollama":
            from ollama_config import create_ollama_llm

            llm = create_ollama_llm(
                model=request.model,
                temperature=request.temperature,
                timeout=180,
            )
        else:
            from langchain_openai import ChatOpenAI

            llm = ChatOpenAI(
                model=request.model,
                temperature=request.temperature,
                timeout=180,
                max_retries=1,
            )

        # Get response from LLM
        from langchain_core.messages import HumanMessage

        response = llm.invoke([HumanMessage(content=extraction_prompt)])

        # Parse response to extract individual stories
        response_text = (
            response.content if hasattr(response, "content") else str(response)
        )

        # Debug: Print response for troubleshooting
        print(f"\n=== LLM Response for Story Extraction ===")
        print(f"Response length: {len(response_text)} chars")
        print(f"First 500 chars: {response_text[:500]}")
        print(f"Contains separator: {'---STORY_SEPARATOR---' in response_text}")
        print(f"Number of separators: {response_text.count('---STORY_SEPARATOR---')}")
        print(f"===========================================\n")

        # Split by separator
        stories = [
            s.strip()
            for s in response_text.split("---STORY_SEPARATOR---")
            if s.strip()
            and len(s.strip()) > 100  # Filter out very short/empty responses
        ]

        print(f"Extracted {len(stories)} story/stories")

        return {"success": True, "stories": stories, "count": len(stories)}

    except Exception as e:
        print(f"Error extracting stories: {str(e)}")
        import traceback

        traceback.print_exc()
        return {"success": False, "message": str(e), "stories": []}


if __name__ == "__main__":
    import uvicorn

    print("\n🎯 Discovery Coach FastAPI Server")
    print("=" * 50)
    print("Server running on http://localhost:8050")
    print("Frontend should connect to http://localhost:8050/api/chat")
    print("API docs available at http://localhost:8050/docs")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8050, log_level="info")
    uvicorn.run(app, host="0.0.0.0", port=8050, log_level="info")
    uvicorn.run(app, host="0.0.0.0", port=8050, log_level="info")
    uvicorn.run(app, host="0.0.0.0", port=8050, log_level="info")
    uvicorn.run(app, host="0.0.0.0", port=8050, log_level="info")
