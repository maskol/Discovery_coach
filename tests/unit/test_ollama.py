#!/usr/bin/env python3
"""
Test script for Ollama integration
Run this to verify Ollama is properly configured and accessible
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))

from ollama_config import (
    test_ollama_connection,
    list_ollama_models,
    get_ollama_base_url,
    get_default_chat_model,
    get_default_embedding_model,
)


def main():
    print("=" * 60)
    print("Ollama Integration Test")
    print("=" * 60)
    print()

    # Test 1: Configuration
    print("📋 Configuration:")
    print(f"   Base URL: {get_ollama_base_url()}")
    print(f"   Default Chat Model: {get_default_chat_model()}")
    print(f"   Default Embedding Model: {get_default_embedding_model()}")
    print()

    # Test 2: Connection
    print("🔌 Testing Connection...")
    result = test_ollama_connection()
    if result["success"]:
        print(f"   ✅ {result['message']}")
        print()

        # Test 3: List Models
        print("📦 Available Models:")
        models = list_ollama_models()
        if models:
            for model in models:
                print(f"   - {model}")
            print()

            # Test 4: Check Required Models
            print("🔍 Required Models Check:")
            chat_model = get_default_chat_model()
            embed_model = get_default_embedding_model()

            if chat_model in models:
                print(f"   ✅ Chat model found: {chat_model}")
            else:
                print(f"   ⚠️  Chat model not found: {chat_model}")
                print(f"      Run: ollama pull {chat_model}")

            if embed_model in models:
                print(f"   ✅ Embedding model found: {embed_model}")
            else:
                print(f"   ⚠️  Embedding model not found: {embed_model}")
                print(f"      Run: ollama pull {embed_model}")
        else:
            print("   ⚠️  No models found")
            print("   Run: ollama pull llama3.2:latest")
            print("   Run: ollama pull nomic-embed-text:latest")
    else:
        print(f"   ❌ {result['message']}")
        print()
        print("💡 Troubleshooting:")
        print("   1. Install Ollama: https://ollama.ai")
        print("   2. Start Ollama: ollama serve")
        print("   3. Pull models: ollama pull llama3.2:latest")

    print()
    print("=" * 60)
    print("Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
