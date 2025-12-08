#!/bin/bash

# Discovery Coach Startup Script
# Starts the FastAPI backend server and opens the GUI in Chrome

echo "🚀 Starting Discovery Coach..."
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
echo "📦 Activating virtual environment..."
source ../../../.venv/bin/activate || source ../.venv/bin/activate

# Check if port 8050 is already in use
if lsof -Pi :8050 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8050 is already in use. Stopping existing server..."
    lsof -ti:8050 | xargs kill -9
    sleep 2
fi

# Start the backend server in background
echo "🎯 Starting FastAPI backend server..."
python app.py &
SERVER_PID=$!

# Wait for server to be ready
echo "⏳ Waiting for server to start..."
for i in {1..10}; do
    if curl -s http://localhost:8050/api/health > /dev/null 2>&1; then
        echo "✅ Server is ready!"
        break
    fi
    sleep 1
done

# Open Chrome browser with the GUI
echo "🌐 Opening Discovery Coach GUI in Chrome..."
sleep 1

# Try different Chrome paths (macOS)
if [ -d "/Applications/Google Chrome.app" ]; then
    open -a "Google Chrome" "$SCRIPT_DIR/index.html"
elif [ -d "/Applications/Brave Browser.app" ]; then
    open -a "Brave Browser" "$SCRIPT_DIR/index.html"
else
    # Fallback to default browser
    open "$SCRIPT_DIR/index.html"
fi

echo ""
echo "=================================="
echo "✨ Discovery Coach is running!"
echo "=================================="
echo "Backend:  http://localhost:8050"
echo "API Docs: http://localhost:8050/docs"
echo "GUI:      file://$SCRIPT_DIR/index.html"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================="
echo ""

# Keep script running and handle Ctrl+C
trap "echo ''; echo '🛑 Stopping server...'; kill $SERVER_PID; exit 0" INT

# Wait for the server process
wait $SERVER_PID
