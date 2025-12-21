# LangSmith Quick Start Guide

**⏱️ Total Time: ~20 minutes**

This guide walks you through enabling LangSmith monitoring for Discovery Coach in 4 simple steps.

---

## Step 1: Get Your LangSmith API Key (5 min)

1. Go to **https://smith.langchain.com/**
2. Sign up or log in with your account
3. Click on your profile → **Settings** → **API Keys**
4. Click **"Create API Key"**
5. Copy the key (it starts with `lsv2_pt_...`)

💾 **Save this key** - you'll need it in the next step!

---

## Step 2: Update Your Configuration (2 min)

1. Open your `.env` file in the Discovery Coach directory
2. Find these lines:
   ```bash
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
   LANGCHAIN_API_KEY=your-langsmith-api-key-here
   LANGCHAIN_PROJECT=discovery-coach
   ```
3. Replace `your-langsmith-api-key-here` with your actual API key
4. Save the file

Example:
```bash
LANGCHAIN_API_KEY=lsv2_pt_abc123def456...
```

---

## Step 3: Install LangSmith Package (2 min)

```bash
# Activate your virtual environment
source .venv/bin/activate

# Install langsmith
pip install langsmith

# Or update all dependencies
pip install -r requirements.txt
```

---

## Step 4: Restart the Backend (1 min)

```bash
# Stop the current server
./stop.sh

# Start it again
./start.sh
```

---

## ✅ Verify It's Working (5 min)

### Test 1: Send a Message

1. Open the Discovery Coach GUI
2. Send a test message: "What is an epic?"
3. Wait for the response

### Test 2: Check LangSmith

1. Go to **https://smith.langchain.com/**
2. Click **Projects** in the left sidebar
3. Click **discovery-coach** project
4. You should see your trace! 🎉

**What You'll See:**
- A new trace with your question
- Timestamp
- Latency (response time)
- Token usage
- Cost estimate
- Full conversation details

### Test 3: Explore the Trace

Click on your trace to see:
- ✅ **Input:** Your question
- ✅ **Retrieved Context:** Documents from knowledge base
- ✅ **Prompt:** Full prompt sent to LLM
- ✅ **Output:** AI response
- ✅ **Metadata:** Context type, model, provider
- ✅ **Tags:** epic/feature/strategic-initiative

---

## 🎯 Next Steps (Optional - 10 min)

### Create Test Datasets

```bash
# Run the dataset setup script
python scripts/setup_langsmith_datasets.py
```

This creates 5 test datasets:
- Epic questions
- Strategic Initiative questions
- Feature questions
- PI Objectives questions
- Quality checks

### Set Up Your First Dashboard

1. Go to LangSmith → **Monitoring**
2. Click **Create Dashboard**
3. Name it "Discovery Coach Performance"
4. Add charts:
   - Response time (last 24h)
   - Success rate
   - Token usage
5. Save!

### Configure an Alert

1. Go to **Monitoring** → **Alerts**
2. Click **Create Alert**
3. Set condition: "Error rate > 10% for 15 minutes"
4. Add your email
5. Save

---

## 🐛 Troubleshooting

### "API key not found" error
- ✅ Check `.env` file has the correct key
- ✅ Restart the backend after updating `.env`
- ✅ Make sure no spaces around the `=` in `.env`

### No traces appearing
- ✅ Verify `LANGCHAIN_TRACING_V2=true` in `.env`
- ✅ Check you're looking at the right project (discovery-coach)
- ✅ Wait 10-30 seconds for traces to appear
- ✅ Try refreshing the LangSmith page

### "Invalid API key" error
- ✅ Regenerate the key in LangSmith settings
- ✅ Make sure you copied the entire key
- ✅ Check for any extra characters or spaces

---

## 📊 What Metrics to Watch

### Daily Check (1 minute)
- Error rate: Should be < 5%
- Average latency: Should be < 5 seconds
- Success rate: Should be > 95%

### Weekly Review (10 minutes)
- Total conversations
- Most common context types
- Slowest operations
- Cost per conversation

---

## 💡 Pro Tips

### Tip 1: Use Filters
Filter traces by:
- Tags: `strategic-initiative`, `epic`, `feature`
- Time: `today`, `last_7d`, `last_30d`
- Status: `success`, `error`

### Tip 2: Compare Traces
- Select 2+ traces
- Click "Compare"
- See side-by-side differences
- Great for debugging!

### Tip 3: Add Comments
- Click any trace
- Add notes about issues
- Tag team members
- Build institutional knowledge

### Tip 4: Export Data
- Export any view to CSV
- Analyze in Excel or Python
- Create custom reports

---

## 📚 Resources

- **Full Monitoring Guide:** [docs/LANGSMITH_MONITORING_GUIDE.md](./LANGSMITH_MONITORING_GUIDE.md)
- **Architecture Review:** [docs/AI_ARCHITECTURE_REVIEW.md](./AI_ARCHITECTURE_REVIEW.md)
- **LangSmith Docs:** https://docs.smith.langchain.com/
- **LangSmith API:** https://docs.smith.langchain.com/api/

---

## ✅ Checklist

Setup Complete:
- [ ] LangSmith account created
- [ ] API key obtained
- [ ] `.env` file updated
- [ ] Backend restarted
- [ ] First trace visible in dashboard
- [ ] Test datasets created (optional)
- [ ] First dashboard created (optional)
- [ ] Error alert configured (optional)

**🎉 Congratulations!** You now have full observability into your Discovery Coach!

---

**Questions?** Check the [full monitoring guide](./LANGSMITH_MONITORING_GUIDE.md) or LangSmith docs.
