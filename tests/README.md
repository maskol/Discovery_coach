# Tests and Utilities

This folder contains all test files, fix scripts, and test-related utilities for Discovery Coach.

## Folder Structure

### `/e2e/` - End-to-End Tests
- `test_e2e.py` - Comprehensive E2E test suite covering all workflows, tabs, and features
  - Run: `python tests/e2e/test_e2e.py`
  - Tests: Epic, Strategic Initiative, Feature, Story, PI Objectives workflows
  - Coverage: API endpoints, template database, monitoring metrics, edge cases

### `/unit/` - Unit Tests
- `test_ollama.py` - Ollama integration tests
  - Tests LLM connectivity and model availability

### `/mcp/` - MCP (Model Context Protocol) Tests
- `test_local_mcp.py` - Local MCP server tests
- `test_mcp_connection.py` - MCP connection validation tests

### `/fixes/` - Fix Scripts
- `fix_feature_names.py` - Script to fix feature naming issues in database

### `/results/` - Test Results
- `test_results_fixed.txt` - Latest E2E test results (100% pass rate)
- Historical test outputs and reports

## Running Tests

### E2E Test Suite (Recommended)
```bash
# Make sure server is running
./start.sh

# In another terminal
python tests/e2e/test_e2e.py
```

### Unit Tests
```bash
python tests/unit/test_ollama.py
```

### MCP Tests
```bash
python tests/mcp/test_local_mcp.py
python tests/mcp/test_mcp_connection.py
```

## Test Coverage

Current E2E test coverage:
- ✅ Health checks and connectivity (3 tests)
- ✅ Epic workflows - draft/evaluate/question (3 tests)
- ✅ Strategic Initiative workflows (3 tests)
- ✅ Feature workflows (3 tests)
- ✅ User Story workflows (3 tests)
- ✅ PI Objectives workflows (2 tests)
- ✅ Template database CRUD operations (6 tests)
- ✅ Monitoring metrics endpoints (4 tests)
- ✅ Context switching (2 tests)
- ✅ Edge cases and error handling (4 tests)

**Total:** 40 tests, 100% pass rate

## Notes

- E2E tests require the server to be running on port 8050
- Tests use the configured LLM provider (default: Ollama with llama3.2)
- Test results are automatically saved to `/results/` folder
- Fix scripts should be run with caution - always backup data first
