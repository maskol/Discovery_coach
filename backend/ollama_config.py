"""
Ollama Configuration and Helper Functions
Provides utilities for connecting to local Ollama LLMs
"""

import os
from typing import Dict, List, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

# Default Ollama endpoint (can be overridden in .env)
DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", DEFAULT_OLLAMA_BASE_URL)

# Default models for different use cases
DEFAULT_OLLAMA_CHAT_MODEL = "llama3.2:latest"  # or llama2, mistral, etc.
DEFAULT_OLLAMA_EMBEDDING_MODEL = "nomic-embed-text:latest"


def get_ollama_base_url() -> str:
    """Get the Ollama base URL from environment or default"""
    return OLLAMA_BASE_URL


def test_ollama_connection() -> Dict[str, any]:
    """
    Test connection to Ollama server

    Returns:
        Dict with 'success' (bool) and 'message' (str) keys
    """
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return {
                "success": True,
                "message": f"Connected to Ollama. Found {len(models)} model(s)",
                "models": [m.get("name") for m in models],
            }
        else:
            return {
                "success": False,
                "message": f"Ollama responded with status {response.status_code}",
            }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "message": "Cannot connect to Ollama. Make sure it's running on "
            + OLLAMA_BASE_URL,
        }
    except Exception as e:
        return {"success": False, "message": f"Error connecting to Ollama: {str(e)}"}


def list_ollama_models() -> List[str]:
    """
    List available Ollama models (excluding embedding models)

    Returns:
        List of chat-capable model names
    """
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            # Filter out embedding models (they can't be used for chat)
            chat_models = []
            for m in models:
                model_name = m.get("name", "")
                # Exclude common embedding model patterns
                if not any(x in model_name.lower() for x in ["embed", "embedding"]):
                    chat_models.append(model_name)
            return chat_models
        return []
    except Exception as e:
        print(f"Error listing Ollama models: {e}")
        return []


def get_default_chat_model() -> str:
    """Get the default Ollama chat model from environment or use default"""
    return os.getenv("OLLAMA_CHAT_MODEL", DEFAULT_OLLAMA_CHAT_MODEL)


def get_default_embedding_model() -> str:
    """Get the default Ollama embedding model from environment or use default"""
    return os.getenv("OLLAMA_EMBEDDING_MODEL", DEFAULT_OLLAMA_EMBEDDING_MODEL)


def is_model_available(model_name: str) -> bool:
    """
    Check if a specific model is available in Ollama

    Args:
        model_name: Name of the model to check

    Returns:
        True if model is available, False otherwise
    """
    available_models = list_ollama_models()
    return model_name in available_models


def create_ollama_llm(model: str, temperature: float = 0.7, timeout: int = 180):
    """
    Create an Ollama LLM instance

    Args:
        model: Model name (e.g., "llama3.2:latest")
        temperature: Temperature setting for generation
        timeout: Request timeout in seconds (default: 180)

    Returns:
        ChatOllama instance
    """
    from langchain_ollama import ChatOllama

    return ChatOllama(
        model=model,
        temperature=temperature,
        base_url=OLLAMA_BASE_URL,
        timeout=timeout,
    )


def create_ollama_embeddings(model: Optional[str] = None):
    """
    Create an Ollama embeddings instance

    Args:
        model: Model name (defaults to DEFAULT_OLLAMA_EMBEDDING_MODEL)

    Returns:
        OllamaEmbeddings instance
    """
    from langchain_ollama import OllamaEmbeddings

    if model is None:
        model = get_default_embedding_model()

    return OllamaEmbeddings(
        model=model,
        base_url=OLLAMA_BASE_URL,
    )


if __name__ == "__main__":
    # Test connection when run directly
    print("Testing Ollama connection...")
    result = test_ollama_connection()
    print(f"Result: {result['message']}")
    if result["success"]:
        print(f"Available models: {', '.join(result.get('models', []))}")
