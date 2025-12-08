#!/bin/bash

# Discovery Coach - Check Server Status Script
# Shows information about running server instances

echo "🔍 Discovery Coach Server Status"
echo "================================="
echo ""

# Check port 8050
if lsof -Pi :8050 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✅ Server is RUNNING on port 8050"
    echo ""
    echo "Process details:"
    lsof -Pi :8050 -sTCP:LISTEN
    echo ""
    echo "To stop the server, run: ./stop.sh"
else
    echo "❌ No server running on port 8050"
    echo ""
    echo "To start the server, run: ./start.sh"
fi

echo ""
echo "================================="

# Check if rag_db exists
if [ -d "rag_db" ]; then
    RAG_SIZE=$(du -sh rag_db 2>/dev/null | cut -f1)
    echo "📚 Knowledge base: $RAG_SIZE (rag_db)"
else
    echo "📚 Knowledge base: Not initialized"
fi

# Check if Session_storage exists and count files
if [ -d "Session_storage" ]; then
    SESSION_COUNT=$(find Session_storage -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
    echo "💾 Saved sessions: $SESSION_COUNT"
else
    echo "💾 Saved sessions: 0 (folder not created)"
fi

echo "================================="
