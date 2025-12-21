# Local Monitoring - Quick Reference

## 🚀 Quick Commands

### View Metrics
```bash
# Daily summary
.venv/bin/python scripts/view_metrics.py report

# Last 7 days
.venv/bin/python scripts/view_metrics.py stats 7

# Last 30 days
.venv/bin/python scripts/view_metrics.py stats 30
```

### View Recent Activity
```bash
# Last 10 conversations
.venv/bin/python scripts/view_metrics.py conversations 10

# Last 10 errors
.venv/bin/python scripts/view_metrics.py errors 10
```

### Export Data
```bash
# Export to timestamped file
.venv/bin/python scripts/view_metrics.py export

# Export to specific file
.venv/bin/python scripts/view_metrics.py export analysis/metrics.json
```

### View Logs
```bash
# Follow current day logs
tail -f logs/discovery_coach_$(date +%Y-%m-%d).log

# View JSON logs (pretty)
tail -f logs/discovery_coach_$(date +%Y-%m-%d).json | jq

# Search for errors
grep ERROR logs/discovery_coach_$(date +%Y-%m-%d).log

# Find slow operations (>5s)
grep "completed in [5-9]" logs/discovery_coach_$(date +%Y-%m-%d).log
```

## 📁 File Locations

```
logs/
├── discovery_coach_YYYY-MM-DD.log    # Human-readable daily logs
├── discovery_coach_YYYY-MM-DD.json   # Machine-readable JSON logs  
└── metrics.json                       # Aggregated metrics database
```

## 🔍 What Gets Logged

### Node Execution (DEBUG level)
```
Node [classify_intent] starting - epic/draft
Node [classify_intent] completed in 0.85s
```

### Workflow Completion (INFO level)
```
✅ Workflow completed in 3.42s
Intent: draft
Validation issues: 0
Retry count: 0
```

### Conversation Metrics (INFO level)
```
Conversation logged: epic/draft - 3.42s - ✓ - retries: 0
```

### Errors (ERROR level)
```
Error logged: ValueError - Invalid context type
Node [generate_response] failed after 2.10s - Connection timeout
```

## 📊 Metrics Collected

### Per Conversation
- **Context Type**: epic, feature, strategic-initiative, etc.
- **Intent**: draft, question, evaluate, outline
- **Model**: llama2, mistral, codellama, etc.
- **Provider**: ollama, openai
- **Latency**: Total response time in seconds
- **Success**: True/False
- **Retry Count**: Number of self-correction loops (0-2)
- **Validation Issues**: List of quality check failures

### Aggregated
- **Daily stats**: Total, success count, error count, avg latency, retry count
- **By context type**: Count, avg/min/max latency
- **By intent**: Count, avg/min/max latency

## 🎯 Common Tasks

### Check System Health
```bash
# View today's performance
.venv/bin/python scripts/view_metrics.py report

# Check for errors
.venv/bin/python scripts/view_metrics.py errors 5
```

### Identify Bottlenecks
```bash
# View stats by context type
.venv/bin/python scripts/view_metrics.py stats 7 | grep -A 10 "By Context Type"

# Find slowest operations
grep "completed in" logs/discovery_coach_*.log | sort -t' ' -k8 -rn | head -10
```

### Debug Issues
```bash
# Follow live logs
tail -f logs/discovery_coach_$(date +%Y-%m-%d).log

# Search for specific error
grep -B 5 -A 5 "ValueError" logs/discovery_coach_*.log

# Check validation failures
grep "validation_issues" logs/discovery_coach_*.json | jq
```

### Export for Analysis
```bash
# Export all metrics
.venv/bin/python scripts/view_metrics.py export monthly_metrics.json

# Analyze in Python
python << EOF
import json
with open('logs/metrics.json') as f:
    data = json.load(f)
print(f"Total conversations: {len(data['conversations'])}")
EOF
```

## ⚙️ Configuration

Edit `.env` to change settings:

```bash
# Log level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Enable/disable file logging
LOG_TO_FILE=true

# Disable external monitoring (already disabled)
LANGCHAIN_TRACING_V2=false
LANGCHAIN_CALLBACKS_BACKGROUND=false
```

## 🔧 Troubleshooting

### No logs appearing
```bash
# Check if logging is enabled
grep LOG_TO_FILE .env

# Check logs directory exists
ls -la logs/

# Check file permissions
chmod 755 logs/
```

### Metrics not updating
```bash
# Check metrics file
cat logs/metrics.json | jq

# If corrupted, reinitialize
echo '{"conversations": [], "daily_stats": {}, "errors": [], "performance": {"avg_latency": [], "by_context_type": {}, "by_intent": {}}}' > logs/metrics.json
```

### Server not logging
```bash
# Restart server
bash stop.sh
bash start.sh

# Check imports
grep "local_monitoring" backend/app.py backend/discovery_workflow.py
```

## 📈 Example Output

### Daily Report
```
📊 Discovery Coach Daily Report
==================================================
Date: 2025-01-15

Conversations: 12
  ✓ Successful: 11
  ✗ Errors: 1
  🔄 Retries: 2

Performance:
  Avg Latency: 3.24s

By Context Type:
  epic: 5 conversations, 3.45s avg
  feature: 4 conversations, 2.98s avg
  strategic-initiative: 3 conversations, 3.12s avg

By Intent:
  draft: 6 conversations, 3.80s avg
  question: 5 conversations, 2.50s avg
  evaluate: 1 conversations, 3.10s avg
```

### Recent Conversations
```
💬 Last 10 Conversations
==================================================
[2025-01-15 14:30:00] ✅ epic           | draft      | 3.42s
[2025-01-15 14:28:15] ✅ feature        | question   | 2.15s
[2025-01-15 14:25:30] ✅ epic           | evaluate   | 3.78s (retries: 1)
[2025-01-15 14:23:00] ❌ feature        | draft      | 1.20s
[2025-01-15 14:20:45] ✅ strategic-initiative | question | 2.89s
```

### Recent Errors
```
❌ Last 5 Errors
==================================================
[2025-01-15 14:23:00] ValueError
  Message: Invalid context type: unknown
  Context: {'context_type': 'unknown', 'model': 'llama2', 'provider': 'ollama'}

[2025-01-15 12:10:30] TimeoutError
  Message: LLM request timed out after 30s
  Context: {'context_type': 'epic', 'model': 'llama2', 'provider': 'ollama'}
```

## 🔗 Related Documentation

- [LOCAL_MONITORING_GUIDE.md](./LOCAL_MONITORING_GUIDE.md) - Complete guide
- [LOCAL_MONITORING_IMPLEMENTATION.md](./LOCAL_MONITORING_IMPLEMENTATION.md) - Implementation details
- [LANGGRAPH_IMPLEMENTATION.md](./LANGGRAPH_IMPLEMENTATION.md) - Workflow architecture

## 💡 Pro Tips

1. **Set up daily checks**: Add to cron for daily reports
2. **Monitor latency**: Alert on avg >5s
3. **Track error rate**: Alert on >10% errors
4. **Export monthly**: Keep historical data
5. **Use DEBUG for dev**: More detailed logs during development
6. **Archive old logs**: Compress logs older than 30 days

---

**Status**: ✅ Operational  
**Dependencies**: None (fully local)  
**Cost**: Free
