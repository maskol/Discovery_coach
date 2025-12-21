# LangSmith Monitoring Dashboard Setup Guide

**Quick Setup:** 15 minutes to full observability

## 📋 Prerequisites

- [ ] LangSmith account created at https://smith.langchain.com/
- [ ] API key obtained from Settings > API Keys
- [ ] `.env` file updated with `LANGCHAIN_API_KEY`

## ⚡ Quick Start (5 minutes)

### Step 1: Get Your API Key

1. Go to https://smith.langchain.com/
2. Sign up or log in
3. Navigate to **Settings** → **API Keys**
4. Click **Create API Key**
5. Copy the key (starts with `lsv2_pt_...`)

### Step 2: Update Configuration

Open your `.env` file and set:

```bash
LANGCHAIN_TRACING_V2=true
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=lsv2_pt_your_actual_key_here
LANGCHAIN_PROJECT=discovery-coach
```

### Step 3: Restart Backend

```bash
cd /Users/mats/Egna-Dokument/Utveckling/Jobb/Discovery_coach
./stop.sh
./start.sh
```

### Step 4: Verify Tracing

1. Have a conversation in the Discovery Coach GUI
2. Go to https://smith.langchain.com/
3. Click on **Projects** → **discovery-coach**
4. You should see your trace appear within seconds! 🎉

---

## 🎯 Understanding the Dashboard

### Main Views

#### 1. **Traces View** (Most Important)
- **What:** Every LLM call is logged as a "trace"
- **Location:** Projects → discovery-coach → Traces tab
- **What You'll See:**
  - Each conversation appears as a trace
  - Click any trace to see full details:
    - Input message
    - Retrieved context
    - LLM prompt
    - Response
    - Latency
    - Token usage
    - Cost estimate

#### 2. **Runs View**
- **What:** Historical view of all executions
- **Filters Available:**
  - By tag (epic, feature, strategic-initiative)
  - By metadata (model, provider, context_type)
  - By date range
  - By status (success/error)

#### 3. **Datasets View**
- **What:** Test datasets for evaluation
- **Created By:** `scripts/setup_langsmith_datasets.py`
- **Use For:** Regression testing, prompt comparison

#### 4. **Monitoring View**
- **What:** Aggregate metrics and charts
- **Metrics:**
  - Request volume over time
  - Latency percentiles (p50, p95, p99)
  - Error rates
  - Cost per day

---

## 📊 Setting Up Custom Dashboards

### Dashboard 1: Performance Monitoring

Create a custom dashboard to track:

**Charts to Add:**

1. **Response Time by Context Type**
   - Metric: Latency
   - Group by: `metadata.context_type`
   - Chart: Line graph
   - Period: Last 7 days

2. **Success Rate**
   - Metric: Count
   - Filter: Status = error vs success
   - Chart: Pie chart
   - Period: Last 24 hours

3. **Token Usage by Model**
   - Metric: Total tokens
   - Group by: `metadata.model`
   - Chart: Bar chart
   - Period: Last 30 days

4. **Cost Per Conversation**
   - Metric: Estimated cost
   - Average by: trace_id
   - Chart: Line graph
   - Period: Last 30 days

**How to Create:**
1. Go to **Monitoring** tab
2. Click **New Dashboard**
3. Add widgets using the "+ Add Chart" button
4. Configure each chart with above settings
5. Save as "Discovery Coach Performance"

### Dashboard 2: Quality Monitoring

**Charts to Add:**

1. **Feedback Scores**
   - Metric: User feedback score
   - Average per day
   - Chart: Line graph

2. **Error Rate by Endpoint**
   - Metric: Error count
   - Group by: `metadata.endpoint`
   - Chart: Bar chart

3. **Common Error Types**
   - Metric: Error messages
   - Top 10
   - Chart: Table

4. **Response Length Distribution**
   - Metric: Output length (chars)
   - Distribution
   - Chart: Histogram

---

## 🏷️ Understanding Metadata Tags

Your traces now include these tags (configured in code):

### Tags (for filtering)
- `strategic-initiative`, `epic`, `feature`, `story`, `pi-objective`
- `openai`, `ollama`
- `model:gpt-4o-mini`, `model:llama3.2:latest`
- `draft`, `chat`, `evaluate`, `fill-template`, etc.

### Metadata (for detailed analysis)
- `context_type`: Strategic initiative, epic, feature, etc.
- `model`: Which LLM was used
- `provider`: openai or ollama
- `temperature`: Model temperature setting
- `is_summary`: Was this a summary request?
- `is_draft`: Was this a draft request?
- `endpoint`: Which API endpoint was called
- `has_epic`, `has_feature`, etc.: Active context presence

### Example Queries

**Find all strategic initiative conversations:**
```
tags: strategic-initiative
```

**Find slow requests (>5 seconds):**
```
latency: >5s
```

**Find all draft requests using GPT-4:**
```
tags: draft AND model:gpt-4o-mini
```

**Find errors in the past hour:**
```
status: error AND time: last_1h
```

---

## 🔔 Setting Up Alerts

Configure alerts to notify you of issues:

### Alert 1: High Error Rate
1. Go to **Monitoring** → **Alerts**
2. Click **Create Alert**
3. Configure:
   - Name: "High Error Rate"
   - Condition: Error rate > 10% over 15 minutes
   - Notification: Email or Slack
   - Channels: Your email

### Alert 2: Slow Response Times
- Condition: p95 latency > 8 seconds over 30 minutes
- Alert when sustained slow performance

### Alert 3: Daily Cost Threshold
- Condition: Daily cost > $5.00
- Alert when spending is high

### Alert 4: Evaluation Failure
- Condition: Evaluation score < 0.7
- Alert when quality degrades

---

## 📈 Useful Filters and Views

### Pre-configured Views to Create

#### View 1: "Strategic Initiatives Today"
```
Filter:
- tags: strategic-initiative
- time: today
Sort by: Latest first
```

#### View 2: "Failed Requests"
```
Filter:
- status: error
- time: last_7d
Group by: metadata.endpoint
```

#### View 3: "Expensive Requests"
```
Filter:
- cost: >$0.10
- time: last_30d
Sort by: Cost descending
```

#### View 4: "Draft Generation Performance"
```
Filter:
- tags: draft
- metadata.is_draft: true
Metrics:
- Average latency
- Success rate
- Token usage
```

---

## 🧪 Running Your First Evaluation

After setting up datasets:

```bash
# Install langsmith if not already installed
pip install langsmith

# Create test datasets
python scripts/setup_langsmith_datasets.py

# Run evaluation
python scripts/run_langsmith_evaluations.py

# View results in dashboard
open https://smith.langchain.com/
```

---

## 🔍 Debugging with LangSmith

### When You See an Error:

1. **Find the Trace:**
   - Go to Traces view
   - Filter by status: error
   - Click the failed trace

2. **Analyze the Trace:**
   - Check **Input**: Was the user message problematic?
   - Check **Context**: Did retrieval find relevant docs?
   - Check **Prompt**: Was the prompt well-formed?
   - Check **Error**: What was the exact error message?

3. **Root Cause Analysis:**
   - Timeout? → Check latency, may need longer timeout
   - Invalid format? → Check prompt template
   - No results? → Check vector store or retrieval query
   - LLM error? → Check API key, rate limits, model availability

4. **Fix and Verify:**
   - Make code changes
   - Re-run the same input
   - Compare traces side-by-side
   - Verify fix worked

---

## 📊 Key Metrics to Track

### Daily Checklist

Check these metrics each morning:

- [ ] **Error Rate:** Should be <5%
- [ ] **p95 Latency:** Should be <5 seconds for chat, <15 seconds for drafts
- [ ] **Daily Cost:** Track spend, set budget alerts
- [ ] **User Feedback:** Review any low-scored interactions
- [ ] **Success Rate:** Should be >95%

### Weekly Review

- [ ] **Trend Analysis:** Is performance improving or degrading?
- [ ] **Cost Efficiency:** Compare cost per successful interaction
- [ ] **Popular Features:** Which context types are used most?
- [ ] **Error Patterns:** Any recurring issues?
- [ ] **Evaluation Scores:** Run weekly regression tests

---

## 🎓 Best Practices

### DO:
✅ Tag all traces with relevant metadata  
✅ Set up alerts for critical issues  
✅ Review traces weekly  
✅ Create custom dashboards for your team  
✅ Use datasets for regression testing  
✅ Add user feedback to important traces  
✅ Compare prompt versions using experiments  

### DON'T:
❌ Ignore high-latency traces  
❌ Let errors accumulate without investigation  
❌ Deploy without testing on datasets first  
❌ Forget to set budget alerts  
❌ Skip tagging - it makes debugging harder  

---

## 🚀 Next Steps

### Week 1: Basic Monitoring
- ✅ Enable tracing (done)
- ✅ Add metadata tags (done)
- ✅ Create datasets (done)
- [ ] Set up 2-3 key dashboards
- [ ] Configure error rate alert
- [ ] Run first evaluation

### Week 2: Quality Improvement
- [ ] Analyze top 10 slowest traces
- [ ] Identify and fix common errors
- [ ] Compare prompts (v1 vs v2)
- [ ] Add user feedback collection
- [ ] Create quality dashboard

### Week 3: Optimization
- [ ] Optimize slow retrievals
- [ ] Reduce token usage where possible
- [ ] Improve prompt templates based on data
- [ ] Set up A/B testing framework
- [ ] Create cost optimization dashboard

### Week 4: Advanced Features
- [ ] Build custom evaluators
- [ ] Create experiments for new features
- [ ] Set up regression test suite
- [ ] Create team dashboards
- [ ] Document best practices

---

## 🔗 Useful Links

- **LangSmith Dashboard:** https://smith.langchain.com/
- **Documentation:** https://docs.smith.langchain.com/
- **API Reference:** https://docs.smith.langchain.com/api/
- **Examples:** https://github.com/langchain-ai/langsmith-cookbook
- **Community:** https://discord.com/invite/langchain

---

## 💡 Tips & Tricks

### Trace Comparison
- Select 2-3 traces
- Click "Compare"
- See side-by-side: inputs, outputs, latency, costs

### Bulk Tagging
- Filter traces
- Select multiple
- Add tags in bulk
- Great for categorizing old traces

### Export Data
- Any view can be exported to CSV
- Great for custom analysis in Excel/Python
- Export button in top right of views

### Sharing
- Share individual traces with team
- Share dashboards publicly or privately
- Embed charts in docs

---

**✅ Setup Complete!** You now have full observability into Discovery Coach operations.

**Questions?** Check the LangSmith docs or Discord community.
