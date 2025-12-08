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

# Add current directory to path to import discovery_coach
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from discovery_coach import active_context, initialize_vector_store
from langchain_core.messages import AIMessage, HumanMessage

app = FastAPI(title="Discovery Coach API", version="1.0.0")

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
    conversationHistory: list = []
    messages: str = ""


class SessionLoadRequest(BaseModel):
    filename: str


class SessionDeleteRequest(BaseModel):
    filenames: List[str]


# Initialize the Discovery Coach
print("Initializing Discovery Coach...")
chain, retriever = initialize_vector_store()
retrieval_chain = chain
print("Discovery Coach ready!")


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

        # Build the full query with context
        context_parts = []
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
        docs = retriever.invoke(full_query)
        context_text = "\n\n".join([doc.page_content for doc in docs])

        # Initialize chat history if not exists
        if "chat_history" not in active_context:
            active_context["chat_history"] = []

        # Create LLM with requested model and temperature
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(
            model=request.model,
            temperature=request.temperature,
        )

        # Load system prompt
        from discovery_coach import load_prompt_file
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

        system_prompt = load_prompt_file("system_prompt.txt")
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("system", "Content from internal documents:\n{context}"),
                MessagesPlaceholder(variable_name="chat_history"),
                ("human", "{user_input}"),
            ]
        )
        chain = prompt | llm

        # Get response from the LLM chain with proper parameters
        response = chain.invoke(
            {
                "user_input": full_query,
                "context": context_text,
                "chat_history": active_context["chat_history"],
            }
        )

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


@app.post("/api/session/save")
async def save_session(request: SessionSaveRequest):
    """Save session to Session_storage folder"""
    try:
        import json
        from datetime import datetime

        # Create Session_storage directory if it doesn't exist
        storage_dir = os.path.join(os.path.dirname(__file__), "Session_storage")
        os.makedirs(storage_dir, exist_ok=True)

        # Create session data including current active_context
        session = {
            "activeEpic": active_context.get("epic") or request.activeEpic,
            "activeFeature": active_context.get("feature") or request.activeFeature,
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

        storage_dir = os.path.join(os.path.dirname(__file__), "Session_storage")

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
        import json

        storage_dir = os.path.join(os.path.dirname(__file__), "Session_storage")
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

        return {
            "success": True,
            "session": session,
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
