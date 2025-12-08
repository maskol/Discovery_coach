#!/bin/bash

# Discovery Coach - Stop Server Script
# Checks for and stops any running instances on port 8050

echo "🔍 Checking for Discovery Coach server on port 8050..."

# Check if any process is using port 8050
if lsof -Pi :8050 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Found active server process(es):"
    echo ""
    lsof -Pi :8050 -sTCP:LISTEN
    echo ""
    echo "🛑 Stopping server..."
    
    # Kill all processes using port 8050
    lsof -ti:8050 | xargs kill -9 2>/dev/null
    
    # Wait a moment for processes to terminate
    sleep 1
    
    # Verify they're stopped
    if lsof -Pi :8050 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "❌ Failed to stop some processes. Try manually with:"
        echo "   lsof -ti:8050 | xargs kill -9"
        exit 1
    else
        echo "✅ All server processes stopped successfully"
        exit 0
    fi
else
    echo "✅ No active server found on port 8050"
    exit 0
fi
