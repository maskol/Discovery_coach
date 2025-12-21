# Viewing Metrics in the Admin Tab

## Overview

You can now view monitoring metrics directly in the Discovery Coach GUI's Admin tab, without needing to use terminal commands.

## How to Access

1. **Open Discovery Coach** in your browser
2. **Click the "⚙️ Admin" tab** at the top
3. **Scroll down** to the "📊 Monitoring & Metrics" section

## Available Reports

### 1. 📈 View Daily Report
Shows a summary of today's activity:
- Total conversations
- Success/error counts
- Retry statistics
- Average latency
- Breakdown by context type and intent

**Click**: "📈 View Daily Report" button

### 2. 📊 View Statistics
Shows aggregated statistics for a selected time period:
- Select timeframe from dropdown (Today, Last 7 Days, Last 30 Days)
- Detailed performance metrics
- Daily breakdown
- Trends over time

**Click**: "📊 View Statistics" button

### 3. 💬 Recent Conversations
Shows the last 20 conversations with:
- Timestamp
- Success/failure status
- Context type and intent
- Latency
- Retry count
- Validation issues (if any)

**Click**: "💬 Recent Conversations" button

### 4. ⚠️ Recent Errors
Shows the last 10 errors with:
- Timestamp
- Error type
- Error message
- Context information

**Click**: "⚠️ Recent Errors" button

## Example Output

### Statistics View
```
📊 Discovery Coach Statistics - Last 7 Days
======================================================================

Total Conversations: 12
  ✅ Successful: 11
  ❌ Errors: 1
  🔄 Total Retries: 2
  ⏱️  Average Latency: 3.24s

📁 By Context Type:
  epic                      |   5 convos | 3.45s avg | 1.20-5.80s
  feature                   |   4 convos | 2.98s avg | 1.50-4.20s
  strategic-initiative      |   3 convos | 3.12s avg | 1.80-4.50s

🎯 By Intent:
  draft                     |   6 convos | 3.80s avg | 2.10-5.80s
  question                  |   5 convos | 2.50s avg | 1.20-3.90s
  evaluate                  |   1 convos | 3.10s avg | 2.30-4.20s

📅 Daily Breakdown:
  2025-12-21 |  12 total |  91.7% success | 3.24s avg
```

### Recent Conversations View
```
💬 Last 20 Conversations
======================================================================

[12/21/2025, 2:30:00 PM] ✅ epic                 | draft        | 3.42s
[12/21/2025, 2:28:15 PM] ✅ feature              | question     | 2.15s
[12/21/2025, 2:25:30 PM] ✅ epic                 | evaluate     | 3.78s (retries: 1)
[12/21/2025, 2:23:00 PM] ❌ feature              | draft        | 1.20s
  ⚠️  Issues: too_short, missing_acceptance_criteria
```

### Recent Errors View
```
❌ Last 10 Errors
======================================================================

[12/21/2025, 2:23:00 PM] ValueError
  Message: Invalid context type: unknown
  Context: {"context_type":"unknown","model":"llama2","provider":"ollama"}

[12/21/2025, 12:10:30 PM] TimeoutError
  Message: LLM request timed out after 30s
  Context: {"context_type":"epic","model":"llama2","provider":"ollama"}
```

## Tips

1. **Select Time Period**: Use the dropdown to change between Today, Last 7 Days, or Last 30 Days before clicking "View Statistics"

2. **Refresh Data**: Click the button again to refresh the metrics with the latest data

3. **Scroll in Display**: The metrics display area is scrollable if content is long

4. **No Data Yet**: If you see "No conversations recorded yet", start using Discovery Coach to generate metrics

5. **Performance Tracking**: Use metrics to:
   - Identify slow operations
   - Track error patterns
   - Monitor success rates
   - Optimize workflow performance

## Technical Details

### API Endpoints Used
- `/api/metrics/report` - Daily report
- `/api/metrics/stats?days=N` - Statistics for N days
- `/api/metrics/conversations?limit=N` - Last N conversations
- `/api/metrics/errors?limit=N` - Last N errors

### Data Storage
All metrics are stored locally in `logs/metrics.json` on your machine. No data is sent externally.

### Privacy
All monitoring data stays on your local machine. Nothing is transmitted to external services.

## Troubleshooting

### "Error loading..." message
1. Check that the backend server is running
2. Verify server is on http://localhost:8050
3. Check browser console for errors (F12)

### No data showing
1. Use Discovery Coach to generate some conversations first
2. Metrics are only collected after conversations complete
3. Check `logs/metrics.json` exists

### Server errors
1. Check backend logs: `tail -f logs/discovery_coach_$(date +%Y-%m-%d).log`
2. Verify imports in backend/app.py
3. Restart server: `bash stop.sh && bash start.sh`

## Command Line Alternative

You can still use command line tools if preferred:

```bash
# Daily report
.venv/bin/python scripts/view_metrics.py report

# Statistics
.venv/bin/python scripts/view_metrics.py stats 7

# Recent conversations
.venv/bin/python scripts/view_metrics.py conversations 20

# Recent errors
.venv/bin/python scripts/view_metrics.py errors 10
```

See [LOCAL_MONITORING_QUICKREF.md](./LOCAL_MONITORING_QUICKREF.md) for more command line options.

---

**Status**: ✅ Operational  
**Location**: Admin Tab → Monitoring & Metrics section  
**Data Storage**: Local (`logs/metrics.json`)
