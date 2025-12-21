#!/bin/bash

# Discovery Coach Startup Script
# Starts the FastAPI backend server and opens the GUI in default browser

echo "🚀 Starting Discovery Coach..."
echo ""

# Get the directory where this script is located and go to project root
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

# Activate virtual environment (check for both .venv and venv)
echo "📦 Activating virtual environment..."
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Error: No virtual environment found (.venv or venv)"
    echo "Please create one with: python -m venv .venv"
    exit 1
fi

# Verify venv is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "❌ Error: Failed to activate virtual environment"
    exit 1
fi
echo "✅ Using virtual environment: $VIRTUAL_ENV"

# Use the venv's Python explicitly
VENV_PYTHON="$VIRTUAL_ENV/bin/python"

# Check if fastapi is installed, if not install requirements
echo "🔍 Checking dependencies..."
if ! "$VENV_PYTHON" -c "import fastapi" 2>/dev/null; then
    echo "⚠️  FastAPI not found. Installing dependencies from requirements.txt..."
    "$VENV_PYTHON" -m pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to install dependencies"
        exit 1
    fi
    echo "✅ Dependencies installed successfully"
else
    echo "✅ Dependencies are installed"
fi

# Check if port 8050 is already in use
if lsof -Pi :8050 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8050 is already in use. Stopping existing server..."
    lsof -ti:8050 | xargs kill -9
    sleep 2
fi

# Start the backend server in background
echo "🎯 Starting FastAPI backend server..."
"$VENV_PYTHON" backend/app.py &
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

# Open the GUI in default browser
echo "🌐 Opening Discovery Coach GUI in default browser..."
sleep 1

# Use system default browser
open "$PROJECT_ROOT/frontend/index.html"

echo ""
echo "=================================="
echo "✨ Discovery Coach is running!"
echo "=================================="
echo "Backend:  http://localhost:8050"
echo "API Docs: http://localhost:8050/docs"
echo "GUI:      file://$PROJECT_ROOT/frontend/index.html"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================="
echo ""

# Keep script running and handle Ctrl+C
trap "echo ''; echo '🛑 Stopping server...'; kill $SERVER_PID; exit 0" INT

# Wait for the server process
wait $SERVER_PID
