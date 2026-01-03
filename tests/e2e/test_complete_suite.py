#!/usr/bin/env python3
"""
Complete End-to-End Test Suite for Discovery Coach
Tests all features including new monitoring, metrics, and template browser functionality
Run this when adding new features to ensure nothing breaks
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import requests

# Configuration
BASE_URL = "http://localhost:8050"
TIMEOUT = 120
TEST_RESULTS_DIR = Path("tests/results")
TEST_RESULTS_DIR.mkdir(exist_ok=True)


class TestRunner:
    """Test runner with comprehensive tracking"""

    def __init__(self):
        self.results = {
            "passed": [],
            "failed": [],
            "warnings": [],
            "skipped": [],
            "start_time": datetime.now(),
            "test_count": 0,
        }

    def header(self, text: str):
        """Print formatted header"""
        print(f"\n{'='*80}")
        print(f"  {text}")
        print(f"{'='*80}")

    def test_start(self, test_name: str):
        """Start a test"""
        self.results["test_count"] += 1
        print(f"\n[{self.results['test_count']}] 🧪 {test_name}")

    def pass_test(self, test_name: str, message: str = ""):
        """Mark test as passed"""
        self.results["passed"].append(test_name)
        msg = f"   ✅ PASS"
        if message:
            msg += f": {message}"
        print(msg)

    def fail_test(self, test_name: str, error: str):
        """Mark test as failed"""
        self.results["failed"].append((test_name, error))
        print(f"   ❌ FAIL: {error}")

    def warn_test(self, test_name: str, warning: str):
        """Add warning"""
        self.results["warnings"].append((test_name, warning))
        print(f"   ⚠️  WARN: {warning}")

    def skip_test(self, test_name: str, reason: str):
        """Skip test"""
        self.results["skipped"].append((test_name, reason))
        print(f"   ⏭️  SKIP: {reason}")

    def summary(self):
        """Print test summary"""
        elapsed = (datetime.now() - self.results["start_time"]).total_seconds()

        self.header("TEST SUMMARY")
        print(f"Total Tests: {self.results['test_count']}")
        print(f"✅ Passed: {len(self.results['passed'])}")
        print(f"❌ Failed: {len(self.results['failed'])}")
        print(f"⚠️  Warnings: {len(self.results['warnings'])}")
        print(f"⏭️  Skipped: {len(self.results['skipped'])}")
        print(f"⏱️  Duration: {elapsed:.2f}s")

        if self.results["failed"]:
            print("\n❌ Failed Tests:")
            for name, error in self.results["failed"]:
                print(f"  - {name}: {error}")

        if self.results["warnings"]:
            print("\n⚠️  Warnings:")
            for name, warning in self.results["warnings"]:
                print(f"  - {name}: {warning}")

        # Save results
        result_file = (
            TEST_RESULTS_DIR
            / f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    **self.results,
                    "start_time": self.results["start_time"].isoformat(),
                    "duration_seconds": elapsed,
                },
                f,
                indent=2,
                default=str,
            )

        print(f"\n📄 Results saved to: {result_file}")

        # Return exit code
        return 0 if not self.results["failed"] else 1


# Initialize test runner
runner = TestRunner()


# =============================================================================
# INFRASTRUCTURE TESTS
# =============================================================================


def test_server_health():
    """Test server is running and healthy"""
    test_name = "Server Health Check"
    runner.test_start(test_name)
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                runner.pass_test(
                    test_name, f"Service: {data.get('service', 'Discovery Coach')}"
                )
                return True
        runner.fail_test(test_name, f"Status code: {response.status_code}")
        return False
    except Exception as e:
        runner.fail_test(test_name, str(e))
        return False


def test_ollama_connection():
    """Test Ollama is connected"""
    test_name = "Ollama Connection"
    runner.test_start(test_name)
    try:
        response = requests.get(f"{BASE_URL}/api/ollama/status", timeout=10)
        data = response.json()
        if data.get("success"):
            runner.pass_test(test_name, data.get("message", "Connected"))
            return True
        runner.warn_test(test_name, data.get("message", "Not connected"))
        return False
    except Exception as e:
        runner.warn_test(test_name, str(e))
        return False


def test_ollama_models():
    """Test Ollama models are available"""
    test_name = "Ollama Models Available"
    runner.test_start(test_name)
    try:
        response = requests.get(f"{BASE_URL}/api/ollama/models", timeout=10)
        data = response.json()
        if data.get("success") and data.get("models"):
            models = data["models"]
            runner.pass_test(
                test_name, f"{len(models)} models: {', '.join(models[:3])}"
            )
            return True
        runner.warn_test(test_name, "No models available")
        return False
    except Exception as e:
        runner.warn_test(test_name, str(e))
        return False


# =============================================================================
# TEMPLATE DATABASE TESTS
# =============================================================================


def test_list_strategic_initiatives():
    """Test listing strategic initiative templates"""
    test_name = "List Strategic Initiative Templates"
    runner.test_start(test_name)
    try:
        response = requests.get(
            f"{BASE_URL}/api/template/list/strategic-initiative", timeout=10
        )
        data = response.json()
        if data.get("success"):
            count = data.get("count", 0)
            runner.pass_test(test_name, f"Found {count} templates")
            return True
        runner.fail_test(test_name, data.get("message", "Unknown error"))
        return False
    except Exception as e:
        runner.fail_test(test_name, str(e))
        return False


def test_list_pi_objectives():
    """Test listing PI objectives templates"""
    test_name = "List PI Objectives Templates"
    runner.test_start(test_name)
    try:
        response = requests.get(
            f"{BASE_URL}/api/template/list/pi-objective", timeout=10
        )
        data = response.json()
        if data.get("success"):
            count = data.get("count", 0)
            runner.pass_test(test_name, f"Found {count} templates")
            return True
        runner.fail_test(test_name, data.get("message", "Unknown error"))
        return False
    except Exception as e:
        runner.fail_test(test_name, str(e))
        return False


def test_list_epics():
    """Test listing epic templates"""
    test_name = "List Epic Templates"
    runner.test_start(test_name)
    try:
        response = requests.get(f"{BASE_URL}/api/template/list/epic", timeout=10)
        data = response.json()
        if data.get("success"):
            count = data.get("count", 0)
            runner.pass_test(test_name, f"Found {count} templates")
            return True
        runner.fail_test(test_name, data.get("message", "Unknown error"))
        return False
    except Exception as e:
        runner.fail_test(test_name, str(e))
        return False


def test_list_features():
    """Test listing feature templates"""
    test_name = "List Feature Templates"
    runner.test_start(test_name)
    try:
        response = requests.get(f"{BASE_URL}/api/template/list/feature", timeout=10)
        data = response.json()
        if data.get("success"):
            count = data.get("count", 0)
            runner.pass_test(test_name, f"Found {count} templates")
            return True
        runner.fail_test(test_name, data.get("message", "Unknown error"))
        return False
    except Exception as e:
        runner.fail_test(test_name, str(e))
        return False


def test_list_stories():
    """Test listing story templates"""
    test_name = "List Story Templates"
    runner.test_start(test_name)
    try:
        response = requests.get(f"{BASE_URL}/api/template/list/story", timeout=10)
        data = response.json()
        if data.get("success"):
            count = data.get("count", 0)
            runner.pass_test(test_name, f"Found {count} templates")
            return True
        runner.fail_test(test_name, data.get("message", "Unknown error"))
        return False
    except Exception as e:
        runner.fail_test(test_name, str(e))
        return False


# =============================================================================
# MONITORING & METRICS TESTS
# =============================================================================


def test_metrics_stats():
    """Test metrics statistics endpoint"""
    test_name = "Metrics Statistics"
    runner.test_start(test_name)
    try:
        response = requests.get(f"{BASE_URL}/api/metrics/stats?days=7", timeout=10)
        data = response.json()
        if data.get("success") and data.get("stats"):
            stats = data["stats"]
            convs = stats.get("total_conversations", 0)
            runner.pass_test(test_name, f"{convs} conversations in last 7 days")
            return True
        runner.fail_test(test_name, "No stats returned")
        return False
    except Exception as e:
        runner.fail_test(test_name, str(e))
        return False


def test_metrics_conversations():
    """Test recent conversations endpoint"""
    test_name = "Recent Conversations"
    runner.test_start(test_name)
    try:
        response = requests.get(
            f"{BASE_URL}/api/metrics/conversations?limit=10", timeout=10
        )
        data = response.json()
        if data.get("success"):
            convs = data.get("conversations", [])
            runner.pass_test(test_name, f"{len(convs)} recent conversations")
            return True
        runner.fail_test(test_name, "Failed to fetch conversations")
        return False
    except Exception as e:
        runner.fail_test(test_name, str(e))
        return False


def test_metrics_errors():
    """Test recent errors endpoint"""
    test_name = "Recent Errors"
    runner.test_start(test_name)
    try:
        response = requests.get(f"{BASE_URL}/api/metrics/errors?limit=10", timeout=10)
        data = response.json()
        if data.get("success"):
            errors = data.get("errors", [])
            runner.pass_test(test_name, f"{len(errors)} recent errors")
            return True
        runner.fail_test(test_name, "Failed to fetch errors")
        return False
    except Exception as e:
        runner.fail_test(test_name, str(e))
        return False


def test_metrics_report():
    """Test daily metrics report"""
    test_name = "Daily Metrics Report"
    runner.test_start(test_name)
    try:
        response = requests.get(f"{BASE_URL}/api/metrics/report", timeout=10)
        data = response.json()
        if data.get("success") and data.get("report"):
            report = data["report"]
            runner.pass_test(test_name, f"Report length: {len(report)} chars")
            return True
        runner.fail_test(test_name, "No report generated")
        return False
    except Exception as e:
        runner.fail_test(test_name, str(e))
        return False


# =============================================================================
# CHAT/CONVERSATION TESTS
# =============================================================================


def test_simple_chat():
    """Test basic chat functionality"""
    test_name = "Simple Chat Message"
    runner.test_start(test_name)
    try:
        payload = {
            "message": "What is an Epic in SAFe?",
            "model": "llama3.2",
            "temperature": 0.7,
            "provider": "ollama",
            "contextType": "epic",
        }
        response = requests.post(f"{BASE_URL}/api/chat", json=payload, timeout=TIMEOUT)
        data = response.json()
        if data.get("success") and data.get("response"):
            response_text = data["response"]
            runner.pass_test(test_name, f"Response: {len(response_text)} chars")
            return True
        runner.fail_test(test_name, data.get("message", "No response"))
        return False
    except Exception as e:
        runner.fail_test(test_name, str(e))
        return False


def test_strategic_initiative_chat():
    """Test strategic initiative context chat"""
    test_name = "Strategic Initiative Chat"
    runner.test_start(test_name)
    try:
        payload = {
            "message": "Help me define a strategic initiative",
            "model": "llama3.2",
            "temperature": 0.7,
            "provider": "ollama",
            "contextType": "strategic-initiative",
        }
        response = requests.post(f"{BASE_URL}/api/chat", json=payload, timeout=TIMEOUT)
        data = response.json()
        if data.get("success") and data.get("response"):
            runner.pass_test(test_name, "Context working")
            return True
        runner.fail_test(test_name, data.get("message", "Failed"))
        return False
    except Exception as e:
        runner.fail_test(test_name, str(e))
        return False


# =============================================================================
# SESSION MANAGEMENT TESTS
# =============================================================================


def test_list_sessions():
    """Test listing saved sessions"""
    test_name = "List Sessions"
    runner.test_start(test_name)
    try:
        response = requests.get(f"{BASE_URL}/api/session/list", timeout=10)
        data = response.json()
        if data.get("success"):
            sessions = data.get("sessions", [])
            runner.pass_test(test_name, f"{len(sessions)} sessions found")
            return True
        runner.fail_test(test_name, "Failed to list sessions")
        return False
    except Exception as e:
        runner.fail_test(test_name, str(e))
        return False


# =============================================================================
# HELP DOCUMENTATION TESTS
# =============================================================================


def test_get_help_content():
    """Test getting help documentation"""
    test_name = "Get Help Content"
    runner.test_start(test_name)
    try:
        response = requests.get(f"{BASE_URL}/api/help/content", timeout=10)
        data = response.json()
        if data.get("success") and data.get("content"):
            content = data["content"]
            runner.pass_test(test_name, f"{len(content)} chars")
            return True
        runner.fail_test(test_name, "No content returned")
        return False
    except Exception as e:
        runner.fail_test(test_name, str(e))
        return False


# =============================================================================
# MAIN TEST EXECUTION
# =============================================================================


def main():
    """Run all tests"""
    runner.header("DISCOVERY COACH - COMPLETE TEST SUITE")
    print(f"Target: {BASE_URL}")
    print(f"Started: {runner.results['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")

    # Infrastructure Tests
    runner.header("INFRASTRUCTURE TESTS")
    server_ok = test_server_health()
    if not server_ok:
        print("\n❌ Server not available. Aborting tests.")
        return 1

    test_ollama_connection()
    test_ollama_models()

    # Template Database Tests
    runner.header("TEMPLATE DATABASE TESTS")
    test_list_strategic_initiatives()
    test_list_pi_objectives()
    test_list_epics()
    test_list_features()
    test_list_stories()

    # Monitoring & Metrics Tests
    runner.header("MONITORING & METRICS TESTS")
    test_metrics_stats()
    test_metrics_conversations()
    test_metrics_errors()
    test_metrics_report()

    # Chat/Conversation Tests
    runner.header("CHAT & CONVERSATION TESTS")
    if test_ollama_connection():
        test_simple_chat()
        test_strategic_initiative_chat()
    else:
        runner.skip_test("Chat Tests", "Ollama not available")

    # Session Management Tests
    runner.header("SESSION MANAGEMENT TESTS")
    test_list_sessions()

    # Help Documentation Tests
    runner.header("HELP DOCUMENTATION TESTS")
    test_get_help_content()

    # Print summary and exit
    exit_code = runner.summary()

    if exit_code == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {len(runner.results['failed'])} test(s) failed")

    return exit_code


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        sys.exit(1)
