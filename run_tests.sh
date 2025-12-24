#!/bin/bash
# Quick Test Runner for Discovery Coach
# Usage: ./run_tests.sh [options]

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║        Discovery Coach - Test Suite Runner                    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if server is running
echo -e "${YELLOW}📡 Checking server status...${NC}"
if ! curl -s http://localhost:8050/api/health > /dev/null 2>&1; then
    echo -e "${RED}❌ Server not running on http://localhost:8050${NC}"
    echo -e "${YELLOW}💡 Start the server first: ./start.sh${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Server is running${NC}"
echo ""

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    echo -e "${YELLOW}🔧 Activating virtual environment...${NC}"
    source .venv/bin/activate
fi

# Parse arguments
TEST_TYPE="${1:-complete}"

case "$TEST_TYPE" in
    complete|full)
        echo -e "${YELLOW}🧪 Running complete test suite...${NC}"
        python3 tests/e2e/test_complete_suite.py
        ;;
    e2e)
        echo -e "${YELLOW}🧪 Running original E2E tests...${NC}"
        python3 tests/e2e/test_e2e.py
        ;;
    unit)
        echo -e "${YELLOW}🧪 Running unit tests...${NC}"
        python3 -m pytest tests/unit/ -v
        ;;
    quick)
        echo -e "${YELLOW}🧪 Running quick smoke tests...${NC}"
        python3 tests/e2e/test_complete_suite.py --quick
        ;;
    *)
        echo -e "${RED}Unknown test type: $TEST_TYPE${NC}"
        echo ""
        echo "Usage: ./run_tests.sh [complete|e2e|unit|quick]"
        echo ""
        echo "  complete  - Run the complete test suite (default)"
        echo "  e2e       - Run original E2E tests"
        echo "  unit      - Run unit tests"
        echo "  quick     - Run quick smoke tests"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✨ Testing complete!${NC}"
