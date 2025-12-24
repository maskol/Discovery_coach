# Discovery Coach - Testing Guide

## 📋 Overview

This document describes the comprehensive testing framework for the Discovery Coach application.

## 🧪 Test Suite Structure

```
tests/
├── e2e/
│   ├── test_complete_suite.py    # Comprehensive E2E tests (17 tests)
│   └── test_e2e.py               # Original E2E tests
├── unit/
│   └── (unit tests for individual modules)
├── results/
│   └── test_results_*.json       # Test execution results
└── README_TESTING.md             # This file
```

## 🚀 Quick Start

### Prerequisites

1. **Start the backend server:**
   ```bash
   ./start.sh
   ```

2. **Verify server is running:**
   ```bash
   curl http://localhost:8050/api/health
   ```

### Running Tests

**Option 1: Use the test runner script (recommended)**
```bash
./run_tests.sh              # Run complete test suite
./run_tests.sh e2e          # Run E2E tests only
./run_tests.sh unit         # Run unit tests only
./run_tests.sh quick        # Run quick smoke tests
```

**Option 2: Run directly**
```bash
python3 tests/e2e/test_complete_suite.py
```

## 📊 Complete Test Suite (test_complete_suite.py)

### Test Categories

#### 1. Infrastructure Tests (3 tests)
- ✅ **Server Health Check** - Verifies API is accessible
- ✅ **Ollama Connection** - Confirms LLM backend is available
- ✅ **Ollama Models** - Lists available models

#### 2. Template Database Tests (5 tests)
- ✅ **Strategic Initiative Templates** - Lists all strategic initiatives
- ✅ **PI Objectives Templates** - Lists all PI objectives
- ✅ **Epic Templates** - Lists all epics
- ✅ **Feature Templates** - Lists all features
- ✅ **Story Templates** - Lists all user stories

#### 3. Monitoring & Metrics Tests (4 tests)
- ✅ **Metrics Statistics** - Validates conversation stats endpoint
- ✅ **Recent Conversations** - Retrieves recent conversation history
- ✅ **Recent Errors** - Fetches error logs
- ✅ **Daily Metrics Report** - Generates metrics report

#### 4. Chat & Conversation Tests (2 tests)
- ✅ **Simple Chat Message** - Tests basic chat interaction
- ✅ **Strategic Initiative Chat** - Tests context-aware chat

#### 5. Session Management Tests (1 test)
- ✅ **List Sessions** - Validates session persistence

#### 6. Help Documentation Tests (1 test)
- ✅ **Get Help Content** - Verifies help system

### Total: **17 Tests**

## 📈 Test Results

### Success Criteria
- All tests must pass (100% success rate)
- No warnings or errors
- Response times < 30s total

### Result Format
```json
{
  "test_name": "Server Health Check",
  "status": "passed",
  "duration": 0.234,
  "timestamp": "2025-12-24T10:06:14",
  "details": {
    "response": {...}
  }
}
```

Results are automatically saved to:
```
tests/results/test_results_YYYYMMDD_HHMMSS.json
```

## 🔧 Test Execution Details

### Expected Output Example
```
╔════════════════════════════════════════════════════════════════╗
║            Discovery Coach - Complete Test Suite              ║
╚════════════════════════════════════════════════════════════════╝

Testing against: http://localhost:8050

═══════════════════════════════════════════════════════════════════════════
Infrastructure Tests
═══════════════════════════════════════════════════════════════════════════

1. Server Health Check
   Status: UP ✓
   ✅ PASSED (0.05s)

...

================================================================================
TEST SUMMARY
================================================================================
Total Tests: 17
✅ Passed: 17 (100%)
❌ Failed: 0
⚠️  Warnings: 0
⏭️  Skipped: 0
⏱️  Duration: 19.23s
```

## 🐛 Troubleshooting

### Common Issues

**1. Server not running**
```
❌ Error: Failed to connect to http://localhost:8050
Solution: Run ./start.sh to start the backend server
```

**2. Ollama not available**
```
⚠️  WARNING: Ollama connection failed
Solution: Ensure Ollama is installed and running
```

**3. No templates found**
```
✅ PASSED - Found 0 templates (empty is valid)
Note: This is normal for fresh installations
```

## 📝 Adding New Tests

### Template for New Test Function

```python
def test_my_new_feature():
    """Test description"""
    runner.test_start("My New Feature Test")
    
    try:
        response = requests.get(f"{BASE_URL}/api/my-endpoint")
        
        if response.status_code == 200:
            data = response.json()
            runner.pass_test("My New Feature Test", 
                           response_time=response.elapsed.total_seconds(),
                           details={"response": data})
        else:
            runner.fail_test("My New Feature Test", 
                           f"Status: {response.status_code}")
    except Exception as e:
        runner.fail_test("My New Feature Test", str(e))
```

### Integration Steps
1. Add test function to appropriate section
2. Call from `main()`: `test_my_new_feature()`
3. Run test suite to validate
4. Commit changes with test results

## 🎯 CI/CD Integration

### GitHub Actions Example
```yaml
name: Run Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Start Server
        run: ./start.sh &
      - name: Wait for Server
        run: sleep 10
      - name: Run Tests
        run: ./run_tests.sh complete
```

## 📚 Related Documentation

- [API Reference](../docs/04-API-REFERENCE.md)
- [Backend Setup](../docs/BACKEND_SETUP.md)
- [E2E Test Report](../docs/E2E_TEST_REPORT.md)
- [Local Monitoring](../docs/LOCAL_MONITORING_GUIDE.md)

## ✅ Best Practices

1. **Always test before committing** - Run complete suite
2. **Test after adding features** - Validate new functionality
3. **Check test results** - Review JSON outputs for patterns
4. **Keep tests fast** - Target < 30s for full suite
5. **Document new tests** - Update this README with new test categories

## 🔄 Regression Testing

The test suite is designed for regression testing:
- Run before major changes to establish baseline
- Run after changes to detect regressions
- Compare JSON results to track trends
- Use for release validation

---

**Last Updated:** 2025-12-24  
**Test Suite Version:** 1.0  
**Total Tests:** 17  
**Coverage:** Infrastructure, Templates, Monitoring, Chat, Sessions, Help
