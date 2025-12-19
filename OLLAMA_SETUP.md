# Ollama Setup Guide for Discovery Coach

This guide will help you set up Ollama to use local LLMs with Discovery Coach, ensuring your sensitive data never leaves your machine.

## What is Ollama?

Ollama is an open-source tool that allows you to run Large Language Models (LLMs) locally on your machine. This means:
- **Data Privacy**: Your questions and data never leave your computer
- **No Internet Required**: Works completely offline once models are downloaded
- **Cost Effective**: No API costs - completely free to use
- **Full Control**: Choose which models to use and when to use them

## Prerequisites

- macOS (for this guide; Ollama also supports Linux and Windows)
- At least 8GB RAM (16GB+ recommended for larger models)
- Sufficient disk space (models range from 1GB to 40GB+)

## Installation

### Step 1: Install Ollama

Visit [ollama.ai](https://ollama.ai) or install via Homebrew:

```bash
# Option 1: Download from website
# Visit https://ollama.ai/download and download the macOS installer

# Option 2: Install via Homebrew
brew install ollama
```

### Step 2: Start Ollama Service

Ollama runs as a service in the background:

```bash
# Start Ollama (it will run on http://localhost:11434)
ollama serve
```

**Note**: On macOS, Ollama usually starts automatically after installation. You can verify it's running by checking:

```bash
curl http://localhost:11434/api/tags
```

### Step 3: Pull Models

Download the models you want to use. Here are recommended models for Discovery Coach:

#### Recommended Chat Models

```bash
# Small, fast model (good for testing) - ~2GB
ollama pull llama3.2:latest

# Balanced model (recommended) - ~4.7GB  
ollama pull llama3.2:3b

# Larger, more capable model - ~7.4GB
ollama pull mistral:latest

# High quality model - ~26GB (requires more RAM)
ollama pull llama3.1:70b
```

#### Required Embedding Model

For the RAG (Retrieval Augmented Generation) knowledge base, you need an embedding model:

```bash
# Essential for vector embeddings - ~275MB
ollama pull nomic-embed-text:latest
```

### Step 4: Verify Installation

Check which models you have installed:

```bash
ollama list
```

Test a model:

```bash
ollama run llama3.2:latest "Hello, how are you?"
```

## Configuration

### Default Settings

Discovery Coach uses these defaults (configurable in `.env`):

```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=llama3.2:latest
OLLAMA_EMBEDDING_MODEL=nomic-embed-text:latest
```

### Custom Configuration

Create or update your `.env` file in the Discovery Coach root directory:

```bash
# Ollama Settings (optional - defaults shown)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=llama3.2:latest
OLLAMA_EMBEDDING_MODEL=nomic-embed-text:latest
```

### For Remote Ollama Server

If running Ollama on a different machine:

```bash
# In .env file
OLLAMA_BASE_URL=http://192.168.1.100:11434
```

## Using Ollama with Discovery Coach

### Step 1: Install Python Dependencies

Make sure you have the updated dependencies:

```bash
cd /Users/maskol/Local-Development/Discovery_coach
source venv/bin/activate
pip install -r requirements.txt
```

### Step 2: Start Discovery Coach

```bash
# Start the backend
python backend/app.py

# Or use the start script
./start.sh
```

### Step 3: Select Ollama in UI

1. Open the Discovery Coach UI in your browser: http://localhost:8050
2. Look at the sidebar under "Model Settings"
3. Select **🏠 Local (Ollama)** radio button
4. The UI will:
   - Check Ollama connection status
   - Load available models
   - Display connection status

### Step 4: Choose Your Model

Once Ollama is selected, the Model dropdown will show your installed Ollama models. Select the one you want to use.

## Model Recommendations

### For Discovery Coach Use Cases

| Model | Size | Speed | Quality | RAM Required | Best For |
|-------|------|-------|---------|--------------|----------|
| `llama3.2:1b` | ~1GB | ⚡⚡⚡ | ⭐⭐ | 4GB+ | Quick testing |
| `llama3.2:3b` | ~2GB | ⚡⚡⚡ | ⭐⭐⭐ | 8GB+ | **Recommended** - Good balance |
| `llama3.2:latest` (8b) | ~4.7GB | ⚡⚡ | ⭐⭐⭐⭐ | 8GB+ | **Best choice** for most use cases |
| `mistral:latest` | ~7.4GB | ⚡⚡ | ⭐⭐⭐⭐ | 16GB+ | High quality responses |
| `llama3.1:70b` | ~40GB | ⚡ | ⭐⭐⭐⭐⭐ | 64GB+ | Enterprise/production |

### For Embeddings (Required for RAG)

- `nomic-embed-text:latest` - **Essential** for knowledge base search (275MB)

## Troubleshooting

### Ollama Not Connecting

**Status Message**: "Cannot connect to Ollama"

**Solutions**:
1. Check if Ollama is running:
   ```bash
   curl http://localhost:11434/api/tags
   ```

2. Start Ollama service:
   ```bash
   ollama serve
   ```

3. Check firewall settings (Ollama needs port 11434)

### No Models Available

**Status Message**: "No Ollama models found"

**Solution**: Pull at least one model:
```bash
ollama pull llama3.2:latest
ollama pull nomic-embed-text:latest
```

### Slow Responses

**Possible Causes**:
1. Model too large for your RAM
2. CPU is being used instead of GPU
3. Other applications using system resources

**Solutions**:
1. Use a smaller model (e.g., `llama3.2:3b`)
2. Close other applications
3. Check Activity Monitor for CPU/RAM usage

### Out of Memory Errors

**Solution**: Use a smaller model:
```bash
# Instead of llama3.2:latest (8B parameters)
ollama pull llama3.2:3b  # 3B parameters - uses less RAM
```

## Performance Optimization

### Speed Tips

1. **Keep Ollama Running**: Don't stop/start repeatedly - it stays in memory
2. **Model Size**: Smaller models = faster responses
3. **RAM**: More RAM allows larger context windows
4. **First Request**: First request after starting is slower (model loads)

### Quality vs Speed Trade-offs

```bash
# Fast but less capable
ollama pull llama3.2:1b

# Balanced (recommended)
ollama pull llama3.2:3b

# Slower but higher quality
ollama pull llama3.2:latest
```

## Advanced Usage

### Viewing Ollama Logs

```bash
# Check Ollama status
ollama ps

# View running models
ollama list
```

### Removing Models

To free up disk space:

```bash
# Remove a model
ollama rm llama3.2:1b

# List to see current models
ollama list
```

### Customizing Model Parameters

In Discovery Coach, you can adjust:
- **Temperature** (0.0 - 2.0): Lower = more focused, Higher = more creative
- **Model Selection**: Choose different models for different use cases

## When to Use Ollama vs OpenAI

### Use Ollama (Local) When:
- ✅ Working with sensitive/confidential information
- ✅ No internet connection available
- ✅ Want to avoid API costs
- ✅ Need full data privacy
- ✅ Prefer offline-first workflows

### Use OpenAI (External) When:
- ✅ Need highest quality responses
- ✅ Working with very complex tasks
- ✅ Don't have powerful local hardware
- ✅ Speed is critical (OpenAI is usually faster)
- ✅ Data sensitivity is not a concern

## Security & Privacy

### Data Privacy with Ollama

When using Ollama:
- ✅ All data stays on your machine
- ✅ No data sent to external servers
- ✅ No API keys required
- ✅ Complete offline capability
- ✅ No telemetry or tracking

### Best Practices

1. **Sensitive Projects**: Always use Ollama for confidential work
2. **Hybrid Approach**: Use Ollama for sensitive queries, OpenAI for general questions
3. **Model Updates**: Regularly check for model updates (`ollama pull <model>`)

## Additional Resources

- **Ollama Documentation**: https://github.com/ollama/ollama
- **Model Library**: https://ollama.ai/library
- **Discord Community**: https://discord.gg/ollama

## Quick Reference

```bash
# Essential Commands
ollama serve              # Start Ollama service
ollama pull <model>       # Download a model
ollama list               # List installed models
ollama run <model>        # Test a model
ollama rm <model>         # Remove a model
ollama ps                 # Show running models

# Recommended Setup
ollama pull llama3.2:latest
ollama pull nomic-embed-text:latest

# Test Installation
curl http://localhost:11434/api/tags
```

## Support

If you encounter issues:

1. Check this documentation first
2. Verify Ollama is running: `curl http://localhost:11434/api/tags`
3. Check Discovery Coach backend logs
4. Test Ollama directly: `ollama run llama3.2:latest "test"`
5. Consult Ollama documentation: https://github.com/ollama/ollama

---

**Ready to use local LLMs?** Select "🏠 Local (Ollama)" in the Discovery Coach UI and start coaching with complete privacy!
