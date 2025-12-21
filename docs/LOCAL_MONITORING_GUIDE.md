# Local Monitoring Guide

Since external monitoring services (LangSmith) cannot be used, Discovery Coach now implements comprehensive **local monitoring** with structured logging, metrics collection, and visualization tools.

## 📁 Architecture

### Components

1. **Local Monitoring Module** ([backend/local_monitoring.py](../backend/local_monitoring.py))
   - Logger configuration (console, file, JSON)
   - Metrics collector (conversations, errors, performance)
   - Decorators for automatic instrumentation
   - Utility functions for reporting

2. **LangGraph Workflow Integration** ([backend/discovery_workflow.py](../backend/discovery_workflow.py))
   - All nodes decorated with `@log_node_execution`
   - Automatic node-level timing and error tracking
   - State transitions logged

3. **FastAPI Integration** ([backend/app.py](../backend/app.py))
   - Conversation-level metrics collection
   - Error tracking with context
   - Request/response logging

4. **CLI Tool** ([scripts/view_metrics.py](../scripts/view_metrics.py))
   - View statistics
   - Export metrics
   - Analyze performance trends

## 🚀 Quick Start

### 1. Enable Local Monitoring

Already configured in `.env`:
```bash
# Disable external monitoring
LANGCHAIN_TRACING_V2=false
LANGCHAIN_CALLBACKS_BACKGROUND=false

# Enable local logging
LOG_LEVEL=INFO
LOG_TO_FILE=true
```

### 2. View Real-Time Logs

**Terminal 1 - Console Logs:**
```bash
cd /Users/mats/Egna-Dokument/Utveckling/Jobb/Discovery_coach
source venv/bin/activate
python backend/app.py
```

You'll see detailed logs:
```
2025-01-15 14:30:00 - discovery_coach - INFO - Starting workflow: classify_intent for epic
2025-01-15 14:30:01 - discovery_coach - DEBUG - Node [classify_intent] starting - epic/draft
2025-01-15 14:30:02 - discovery_coach - DEBUG - Node [classify_intent] completed in 0.85s
2025-01-15 14:30:02 - discovery_coach - INFO - Conversation logged: epic/draft - 3.42s - ✓ - retries: 0
```

**Terminal 2 - Follow JSON Logs:**
```bash
tail -f logs/discovery_coach_$(date +%Y-%m-%d).json | jq
```

Beautiful structured output:
```json
{
  "timestamp": "2025-01-15 14:30:00",
  "level": "INFO",
  "module": "discovery_coach",
  "function": "classify_intent_node",
  "line": 75,
  "message": "Node [classify_intent] starting - epic/draft"
}
```

### 3. View Metrics Dashboard

```bash
# Daily summary
python scripts/view_metrics.py report

# Last 7 days stats
python scripts/view_metrics.py stats 7

# Last 20 conversations
python scripts/view_metrics.py conversations 20

# Last 10 errors
python scripts/view_metrics.py errors 10

# Export to JSON
python scripts/view_metrics.py export metrics_export.json
```

## 📊 Metrics Collected

### Conversation Metrics
- **Context type**: epic, feature, strategic-initiative, etc.
- **Intent**: draft, question, evaluate, outline
- **Model & Provider**: Which LLM was used
- **Latency**: Total response time
- **Success**: Whether workflow completed successfully
- **Retry count**: How many self-correction loops
- **Validation issues**: What quality checks failed

### Error Metrics
- **Error type**: Exception class name
- **Error message**: Detailed error description
- **Context**: What was happening when error occurred
- **Timestamp**: When it happened

### Performance Metrics
- **Average latency**: By context type, by intent, overall
- **Min/Max latency**: Performance bounds
- **Daily breakdown**: Trends over time
- **Success rate**: Percentage of successful conversations

## 📈 Example Metrics Output

```
======================================================================
📊 Discovery Coach Statistics - Last 7 Days
======================================================================

Total Conversations: 45
  ✅ Successful: 42
  ❌ Errors: 3
  🔄 Total Retries: 8
  ⏱️  Average Latency: 3.24s

📁 By Context Type:
  epic                |  20 convos | 3.45s avg | 1.20-5.80s
  feature             |  15 convos | 2.98s avg | 1.50-4.20s
  strategic-initiative|  10 convos | 3.12s avg | 1.80-4.50s

🎯 By Intent:
  draft               |  25 convos | 3.80s avg | 2.10-5.80s
  question            |  15 convos | 2.50s avg | 1.20-3.90s
  evaluate            |   5 convos | 3.10s avg | 2.30-4.20s

📅 Daily Breakdown:
  2025-01-15 |  12 total |  91.7% success | 3.12s avg
  2025-01-14 |  18 total |  94.4% success | 3.28s avg
  2025-01-13 |  15 total |  93.3% success | 3.35s avg
```

## 🔍 Log Files

All logs are stored in the `logs/` directory:

### File Structure
```
logs/
├── discovery_coach_2025-01-15.log      # Human-readable logs
├── discovery_coach_2025-01-15.json     # Structured JSON logs
└── metrics.json                         # Aggregated metrics
```

### Log Levels
- **DEBUG**: Node executions, state transitions
- **INFO**: Workflow starts/completions, API requests
- **WARNING**: Validation failures, retry attempts
- **ERROR**: Exceptions, failures

### Changing Log Level
Edit `.env`:
```bash
LOG_LEVEL=DEBUG  # More verbose
LOG_LEVEL=INFO   # Balanced (default)
LOG_LEVEL=WARNING # Only warnings and errors
```

## 🛠️ Advanced Usage

### 1. Programmatic Access

```python
from backend.local_monitoring import metrics_collector, logger

# Get stats
stats = metrics_collector.get_stats(days=7)
print(f"Success rate: {stats['successful'] / stats['total_conversations'] * 100}%")

# Log custom metrics
metrics_collector.log_conversation(
    context_type="custom",
    intent="custom_intent",
    model="llama2",
    provider="ollama",
    latency=2.5,
    success=True,
    retry_count=0,
)

# Log errors
metrics_collector.log_error(
    error_type="CustomError",
    error_message="Something went wrong",
    context={"user": "test", "action": "custom"},
)
```

### 2. Custom Decorators

Add monitoring to your own functions:

```python
from backend.local_monitoring import log_node_execution

@log_node_execution("my_custom_node")
async def my_custom_node(state):
    # Your logic here
    return state
```

### 3. Export & Analyze

```python
from backend.local_monitoring import export_metrics
import json

# Export metrics
export_file = export_metrics("analysis/metrics_20250115.json")

# Load and analyze
with open(export_file) as f:
    data = json.load(f)

# Find slowest context type
slowest = max(data['by_context_type'].items(), key=lambda x: x[1]['avg'])
print(f"Slowest context: {slowest[0]} at {slowest[1]['avg']:.2f}s")
```

## 📉 Performance Optimization

Use metrics to identify bottlenecks:

### 1. Find Slow Nodes
```bash
# Enable DEBUG logging
echo "LOG_LEVEL=DEBUG" >> .env

# Restart server and run test
# Check logs for node timing:
grep "completed in" logs/discovery_coach_*.log | sort -t' ' -k8 -rn | head
```

### 2. Identify High-Retry Intents
```bash
python scripts/view_metrics.py stats 30 | grep -A 20 "By Intent"
```

### 3. Analyze Error Patterns
```bash
python scripts/view_metrics.py errors 50 | grep "Message:" | sort | uniq -c | sort -rn
```

## 🎯 Monitoring Best Practices

### 1. Regular Review
```bash
# Daily
python scripts/view_metrics.py report

# Weekly
python scripts/view_metrics.py stats 7

# Monthly export
python scripts/view_metrics.py export monthly_$(date +%Y%m).json
```

### 2. Set Up Alerts

Create a simple alert script (`scripts/alert_check.py`):
```python
from backend.local_monitoring import metrics_collector

stats = metrics_collector.get_stats(days=1)

# Alert on high error rate
if stats['total_conversations'] > 0:
    error_rate = stats['errors'] / stats['total_conversations']
    if error_rate > 0.1:  # > 10% errors
        print(f"🚨 HIGH ERROR RATE: {error_rate*100:.1f}%")

# Alert on slow performance
if stats['avg_latency'] > 5.0:  # > 5 seconds
    print(f"🐌 SLOW PERFORMANCE: {stats['avg_latency']:.2f}s avg")
```

Run daily via cron:
```bash
0 9 * * * cd /Users/mats/Egna-Dokument/Utveckling/Jobb/Discovery_coach && python scripts/alert_check.py
```

### 3. Log Rotation

Automatically handled by date-based file naming. Old logs can be archived:

```bash
# Archive logs older than 30 days
find logs/ -name "*.log" -mtime +30 -exec gzip {} \;
find logs/ -name "*.json" -mtime +30 -exec gzip {} \;
```

## 🔄 Comparison: External vs Local

| Feature | LangSmith (External) | Local Monitoring |
|---------|---------------------|------------------|
| **Setup** | API key required | ✅ Built-in |
| **Cost** | Paid service | ✅ Free |
| **Privacy** | Data sent externally | ✅ Stays local |
| **Real-time** | Web dashboard | ✅ Logs + CLI |
| **Metrics** | Comprehensive | ✅ Comprehensive |
| **Traces** | Visual flow | Structured logs |
| **Datasets** | Built-in | Export JSON |
| **Alerts** | Email/Slack | Custom scripts |
| **Retention** | Limited by plan | ✅ Unlimited |
| **Speed** | Network latency | ✅ Local I/O |

## 🎨 Future Enhancements

Possible additions:

1. **Simple Web Dashboard**
   - Local Flask app to visualize metrics
   - Real-time charts with Chart.js
   - No external dependencies

2. **SQLite Storage**
   - Store metrics in database instead of JSON
   - Better query performance
   - More structured analysis

3. **Grafana Integration**
   - Export metrics to Prometheus format
   - Use Grafana for visualization
   - Enterprise-grade dashboards

4. **Automated Testing**
   - Use metrics to track regression
   - Alert on performance degradation
   - Compare before/after changes

## 📝 Summary

Local monitoring provides:

✅ **Complete visibility** into workflow execution  
✅ **Performance metrics** for optimization  
✅ **Error tracking** for debugging  
✅ **No external dependencies** or costs  
✅ **Privacy-first** - all data stays local  
✅ **Easy to use** - CLI tools provided  
✅ **Extensible** - add custom metrics easily  

All without requiring external services like LangSmith!

## 🆘 Troubleshooting

### Logs not appearing
```bash
# Check LOG_TO_FILE setting
grep LOG_TO_FILE .env

# Check logs directory
ls -la logs/

# Check file permissions
chmod 755 logs/
```

### Metrics file corrupted
```bash
# Backup and reset
cp logs/metrics.json logs/metrics_backup.json
echo '{"conversations": [], "daily_stats": {}, "errors": [], "performance": {"avg_latency": [], "by_context_type": {}, "by_intent": {}}}' > logs/metrics.json
```

### No metrics showing
```bash
# Verify imports in app.py
grep "local_monitoring" backend/app.py

# Check if metrics_collector is being called
grep "metrics_collector.log" backend/app.py
```

---

**Need help?** Check the [implementation guide](./LANGGRAPH_IMPLEMENTATION.md) for the full workflow architecture.
