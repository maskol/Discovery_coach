#!/bin/bash
# Test script for Prompt Management API

echo "🧪 Testing Prompt Management API"
echo "=================================="
echo ""

# Check if server is running
if ! curl -s http://localhost:8050/api/health > /dev/null 2>&1; then
    echo "❌ Server is not running!"
    echo "Please start the server with: ./start.sh"
    exit 1
fi

echo "✅ Server is running"
echo ""

# Test 1: List prompt files
echo "📝 Test 1: Listing prompt files..."
response=$(curl -s http://localhost:8050/api/prompts/list)
echo "$response" | python3 -m json.tool
echo ""

# Test 2: Get content of a prompt file
echo "📄 Test 2: Getting content of system_prompt.txt..."
curl -s http://localhost:8050/api/prompts/content/system_prompt.txt | python3 -c "import sys, json; data = json.load(sys.stdin); print(f\"Success: {data['success']}\"); print(f\"Content length: {len(data.get('content', ''))} chars\"); print(f\"First 100 chars: {data.get('content', '')[:100]}...\")"
echo ""

# Test 3: List versions (should be empty initially)
echo "🗂️  Test 3: Listing versions for system_prompt.txt..."
curl -s http://localhost:8050/api/prompts/versions/list/system_prompt.txt | python3 -m json.tool
echo ""

echo "✅ All basic tests completed!"
echo ""
echo "To test the full functionality:"
echo "1. Open the GUI: http://localhost:8050 (or use the file:// URL shown when starting)"
echo "2. Click on the '⚙️ Admin' tab"
echo "3. Scroll to '📝 Prompt Management'"
echo "4. Select a prompt file and try editing, creating versions, etc."
