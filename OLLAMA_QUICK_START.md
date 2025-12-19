# Quick Start Guide - Ollama Integration

## Installation Steps

### 1. Update Python Dependencies

```bash
cd /Users/maskol/Local-Development/Discovery_coach
source venv/bin/activate
pip install -r requirements.txt
```

This will install the new `langchain-ollama` package.

### 2. Install Ollama (if not already installed)

#### Option A: Download from Website
Visit https://ollama.ai/download

#### Option B: Install via Homebrew
```bash
brew install ollama
```

### 3. Start Ollama Service

```bash
ollama serve
```

**Note**: On macOS, Ollama usually auto-starts after installation.

### 4. Pull Required Models

```bash
# Essential chat model (recommended - 4.7GB)
ollama pull llama3.2:latest

# Required for RAG embeddings (275MB)
ollama pull nomic-embed-text:latest
```

### 5. Test Ollama Integration

```bash
python test_ollama.py
```

Expected output:
```
============================================================
Ollama Integration Test
============================================================

📋 Configuration:
   Base URL: http://localhost:11434
   Default Chat Model: llama3.2:latest
   Default Embedding Model: nomic-embed-text:latest

🔌 Testing Connection...
   ✅ Connected to Ollama. Found 2 model(s)

📦 Available Models:
   - llama3.2:latest
   - nomic-embed-text:latest

🔍 Required Models Check:
   ✅ Chat model found: llama3.2:latest
   ✅ Embedding model found: nomic-embed-text:latest

============================================================
Test Complete
============================================================
```

### 6. Start Discovery Coach

```bash
./start.sh
```

Or manually:
```bash
python backend/app.py
```

### 7. Use Ollama in the UI

1. Open http://localhost:8050 in your browser
2. Look at the sidebar under "Model Settings"
3. Select the **🏠 Local (Ollama)** radio button
4. Wait for status check and model list to populate
5. Choose your model from the dropdown
6. Start chatting!

## Quick Test

Once everything is running:

1. In Discovery Coach UI, select "Local (Ollama)"
2. Send a test message: "Hello, can you help me with an Epic?"
3. You should get a response from your local Ollama model

## Troubleshooting

### "Cannot connect to Ollama"

**Check if Ollama is running:**
```bash
curl http://localhost:11434/api/tags
```

If you get "Connection refused":
```bash
ollama serve
```

### "No models available"

**Pull the required models:**
```bash
ollama pull llama3.2:latest
ollama pull nomic-embed-text:latest
```

### Slow responses

**Try a smaller model:**
```bash
ollama pull llama3.2:3b
```

Then select it in the UI dropdown.

## Switching Between OpenAI and Ollama

You can switch at any time:
- **For general questions**: Use OpenAI (faster, higher quality)
- **For sensitive data**: Use Ollama (private, offline)

Just toggle the radio button in Model Settings - no restart needed!

## Additional Models (Optional)

```bash
# Smaller, faster model (2GB)
ollama pull llama3.2:3b

# High quality model (7.4GB)
ollama pull mistral:latest

# Larger model for complex tasks (26GB, requires 16GB+ RAM)
ollama pull llama3.1:70b
```

## Environment Configuration (Optional)

Create or edit `.env` file:

```bash
# Ollama Configuration (optional - defaults work fine)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=llama3.2:latest
OLLAMA_EMBEDDING_MODEL=nomic-embed-text:latest
```

## Next Steps

- Read [OLLAMA_SETUP.md](OLLAMA_SETUP.md) for detailed information
- Read [OLLAMA_INTEGRATION_SUMMARY.md](OLLAMA_INTEGRATION_SUMMARY.md) for technical details
- Check [README.md](README.md) for general Discovery Coach documentation

## Need Help?

Run the test script to diagnose issues:
```bash
python test_ollama.py
```

This will show you exactly what's working and what needs attention.
