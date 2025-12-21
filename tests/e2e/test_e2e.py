#!/usr/bin/env python3
"""
End-to-End Test Suite for Discovery Coach
Tests all tabs, buttons, database operations, and use cases
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import requests

# Configuration
BASE_URL = "http://localhost:8050"
TIMEOUT = 120  # 2 minutes for LLM responses

# Test results tracking
test_results = {
    "passed": [],
    "failed": [],
    "warnings": [],
    "start_time": datetime.now(),
}


def print_header(text: str):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}")


def print_test(test_name: str):
    """Print test name"""
    print(f"\n🧪 Testing: {test_name}")


def pass_test(test_name: str, message: str = ""):
    """Mark test as passed"""
    test_results["passed"].append(test_name)
    msg = f"✅ PASS: {test_name}"
    if message:
        msg += f" - {message}"
    print(msg)


def fail_test(test_name: str, error: str):
    """Mark test as failed"""
    test_results["failed"].append((test_name, error))
    print(f"❌ FAIL: {test_name}")
    print(f"   Error: {error}")


def warn_test(test_name: str, warning: str):
    """Add warning"""
    test_results["warnings"].append((test_name, warning))
    print(f"⚠️  WARN: {test_name} - {warning}")


def test_health_check():
    """Test 1: Health check endpoint"""
    print_test("Health Check")
    try:
        response = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                pass_test("Health Check", f"Service: {data.get('service')}")
                return True
        fail_test("Health Check", f"Status: {response.status_code}")
        return False
    except Exception as e:
        fail_test("Health Check", str(e))
        return False


def test_ollama_status():
    """Test 2: Ollama connection status"""
    print_test("Ollama Status")
    try:
        response = requests.get(f"{BASE_URL}/api/ollama/status", timeout=10)
        data = response.json()

        if data.get("success"):
            pass_test("Ollama Status", data.get("message"))
            return True
        else:
            warn_test("Ollama Status", data.get("message", "Connection issue"))
            return False
    except Exception as e:
        warn_test("Ollama Status", f"Cannot connect: {str(e)}")
        return False


def test_ollama_models():
    """Test 3: Load Ollama models"""
    print_test("Ollama Models")
    try:
        response = requests.get(f"{BASE_URL}/api/ollama/models", timeout=10)
        data = response.json()

        if data.get("success") and data.get("models"):
            models = data["models"]
            pass_test(
                "Ollama Models", f"Found {len(models)} models: {', '.join(models[:3])}"
            )
            return models
        else:
            warn_test("Ollama Models", "No models found")
            return []
    except Exception as e:
        fail_test("Ollama Models", str(e))
        return []


def test_chat_endpoint(
    context_type: str, message: str, model: str = "llama3.2", provider: str = "ollama"
) -> Tuple[bool, str]:
    """Test chat endpoint with various contexts"""
    print_test(f"Chat - {context_type}")
    try:
        payload = {
            "message": message,
            "contextType": context_type,
            "model": model,
            "provider": provider,
            "temperature": 0.7,
        }

        print(f"   Sending: {message[:50]}...")
        start_time = time.time()

        response = requests.post(f"{BASE_URL}/api/chat", json=payload, timeout=TIMEOUT)

        elapsed = time.time() - start_time

        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                response_text = data.get("response", "")
                metadata = data.get("metadata", {})

                pass_test(
                    f"Chat - {context_type}",
                    f"Response length: {len(response_text)} chars, "
                    f"Intent: {metadata.get('intent', 'unknown')}, "
                    f"Time: {elapsed:.2f}s",
                )
                return True, response_text
            else:
                fail_test(f"Chat - {context_type}", "Success=False in response")
                return False, ""
        else:
            fail_test(f"Chat - {context_type}", f"Status: {response.status_code}")
            return False, ""

    except requests.Timeout:
        fail_test(f"Chat - {context_type}", f"Timeout after {TIMEOUT}s")
        return False, ""
    except Exception as e:
        fail_test(f"Chat - {context_type}", str(e))
        return False, ""


def test_epic_workflow():
    """Test 4-7: Epic tab workflow"""
    print_header("EPIC WORKFLOW TESTS")

    # Test 4: Draft an Epic
    success, epic_content = test_chat_endpoint(
        "epic",
        "Help me draft an Epic for a customer portal that allows users to manage their accounts online.",
        "llama3.2",
        "ollama",
    )

    if not success:
        warn_test("Epic Workflow", "Could not draft epic, skipping evaluation")
        return None

    # Test 5: Evaluate the Epic
    success, evaluation = test_chat_endpoint(
        "epic",
        "Evaluate this epic and provide feedback on its hypothesis statement.",
        "llama3.2",
        "ollama",
    )

    # Test 6: Ask question about Epic
    success, answer = test_chat_endpoint(
        "epic", "What are the key success metrics for this epic?", "llama3.2", "ollama"
    )

    return epic_content


def test_strategic_initiative_workflow():
    """Test 8-10: Strategic Initiative workflow"""
    print_header("STRATEGIC INITIATIVE WORKFLOW TESTS")

    # Test 8: Draft Strategic Initiative
    success, si_content = test_chat_endpoint(
        "strategic-initiative",
        "Help me create a strategic initiative for digital transformation in our telecom company.",
        "llama3.2",
        "ollama",
    )

    if not success:
        return None

    # Test 9: Evaluate Strategic Initiative
    success, evaluation = test_chat_endpoint(
        "strategic-initiative",
        "Review this strategic initiative for alignment with business goals.",
        "llama3.2",
        "ollama",
    )

    # Test 10: Ask about Strategic Initiative
    success, answer = test_chat_endpoint(
        "strategic-initiative",
        "What risks should we consider for this initiative?",
        "llama3.2",
        "ollama",
    )

    return si_content


def test_feature_workflow():
    """Test 11-13: Feature workflow"""
    print_header("FEATURE WORKFLOW TESTS")

    # Test 11: Draft Feature
    success, feature_content = test_chat_endpoint(
        "feature",
        "Help me draft a Feature for user authentication with multi-factor authentication support.",
        "llama3.2",
        "ollama",
    )

    if not success:
        return None

    # Test 12: Evaluate Feature
    success, evaluation = test_chat_endpoint(
        "feature",
        "Evaluate this feature for completeness and clarity.",
        "llama3.2",
        "ollama",
    )

    # Test 13: Ask about Feature
    success, answer = test_chat_endpoint(
        "feature", "What acceptance criteria should we add?", "llama3.2", "ollama"
    )

    return feature_content


def test_story_workflow():
    """Test 14-16: User Story workflow"""
    print_header("USER STORY WORKFLOW TESTS")

    # Test 14: Draft User Story
    success, story_content = test_chat_endpoint(
        "story",
        "Help me write a user story for password reset functionality.",
        "llama3.2",
        "ollama",
    )

    if not success:
        return None

    # Test 15: Evaluate Story
    success, evaluation = test_chat_endpoint(
        "story", "Review this user story for INVEST criteria.", "llama3.2", "ollama"
    )

    # Test 16: Ask about Story
    success, answer = test_chat_endpoint(
        "story", "What edge cases should we consider?", "llama3.2", "ollama"
    )

    return story_content


def test_pi_objectives_workflow():
    """Test 17-18: PI Objectives workflow"""
    print_header("PI OBJECTIVES WORKFLOW TESTS")

    # Test 17: Draft PI Objectives
    success, pi_content = test_chat_endpoint(
        "pi-objective",
        "Help me create PI objectives for Q1 2026 focused on customer experience improvements.",
        "llama3.2",
        "ollama",
    )

    if not success:
        return None

    # Test 18: Evaluate PI Objectives
    success, evaluation = test_chat_endpoint(
        "pi-objective", "Are these PI objectives SMART?", "llama3.2", "ollama"
    )

    return pi_content


def test_template_database():
    """Test 19-24: Template database operations"""
    print_header("TEMPLATE DATABASE TESTS")

    # Test 19: List Epic templates
    print_test("List Epic Templates")
    try:
        response = requests.get(f"{BASE_URL}/api/template/list/epic", timeout=10)
        if response.status_code == 200:
            data = response.json()
            templates = data.get("templates", [])
            pass_test("List Epic Templates", f"Found {len(templates)} templates")
        else:
            fail_test("List Epic Templates", f"Status: {response.status_code}")
    except Exception as e:
        fail_test("List Epic Templates", str(e))

    # Test 20: Save Epic template
    print_test("Save Epic Template")
    try:
        payload = {
            "content": "Test Epic\n\nEPIC NAME: Customer Portal\nBUSINESS CONTEXT: Test context",
            "name": "Test Epic - E2E",
            "description": "End-to-end test epic",
            "template_type": "epic",
        }
        response = requests.post(
            f"{BASE_URL}/api/template/save", json=payload, timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                template_id = data.get("template_id")
                pass_test("Save Epic Template", f"Saved with ID: {template_id}")

                # Test 21: Load Epic template
                print_test("Load Epic Template")
                load_payload = {"template_id": template_id, "template_type": "epic"}
                response = requests.post(
                    f"{BASE_URL}/api/template/load", json=load_payload, timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        pass_test(
                            "Load Epic Template", f"Loaded template {template_id}"
                        )
                    else:
                        fail_test("Load Epic Template", "Success=False")
                else:
                    fail_test("Load Epic Template", f"Status: {response.status_code}")

                # Test 22: Delete Epic template
                print_test("Delete Epic Template")
                delete_payload = {"template_id": template_id, "template_type": "epic"}
                response = requests.post(
                    f"{BASE_URL}/api/template/delete", json=delete_payload, timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("success"):
                        pass_test(
                            "Delete Epic Template", f"Deleted template {template_id}"
                        )
                    else:
                        fail_test("Delete Epic Template", "Success=False")
                else:
                    fail_test("Delete Epic Template", f"Status: {response.status_code}")
            else:
                fail_test("Save Epic Template", "Success=False")
        else:
            fail_test("Save Epic Template", f"Status: {response.status_code}")
    except Exception as e:
        fail_test("Save Epic Template", str(e))

    # Test 23: List Feature templates
    print_test("List Feature Templates")
    try:
        response = requests.get(f"{BASE_URL}/api/template/list/feature", timeout=10)
        if response.status_code == 200:
            data = response.json()
            templates = data.get("templates", [])
            pass_test("List Feature Templates", f"Found {len(templates)} templates")
        else:
            fail_test("List Feature Templates", f"Status: {response.status_code}")
    except Exception as e:
        fail_test("List Feature Templates", str(e))

    # Test 24: Save Feature template
    print_test("Save Feature Template")
    try:
        payload = {
            "content": "Test Feature\n\nFEATURE NAME: Multi-factor Authentication",
            "name": "Test Feature - E2E",
            "description": "End-to-end test feature",
            "template_type": "feature",
        }
        response = requests.post(
            f"{BASE_URL}/api/template/save", json=payload, timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                template_id = data.get("template_id")
                pass_test("Save Feature Template", f"Saved with ID: {template_id}")

                # Clean up
                delete_payload = {
                    "template_id": template_id,
                    "template_type": "feature",
                }
                requests.post(
                    f"{BASE_URL}/api/template/delete", json=delete_payload, timeout=10
                )
            else:
                fail_test("Save Feature Template", "Success=False")
        else:
            fail_test("Save Feature Template", f"Status: {response.status_code}")
    except Exception as e:
        fail_test("Save Feature Template", str(e))


def test_monitoring_endpoints():
    """Test 25-28: Monitoring metrics endpoints"""
    print_header("MONITORING METRICS TESTS")

    # Test 25: Metrics report
    print_test("Metrics Report")
    try:
        response = requests.get(f"{BASE_URL}/api/metrics/report", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                report = data.get("report", "")
                pass_test("Metrics Report", f"Report length: {len(report)} chars")
            else:
                fail_test("Metrics Report", "Success=False")
        else:
            fail_test("Metrics Report", f"Status: {response.status_code}")
    except Exception as e:
        fail_test("Metrics Report", str(e))

    # Test 26: Metrics stats
    print_test("Metrics Stats")
    try:
        response = requests.get(f"{BASE_URL}/api/metrics/stats?days=7", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                stats = data.get("stats", {})
                pass_test(
                    "Metrics Stats",
                    f"Total conversations: {stats.get('total_conversations', 0)}, "
                    f"Successful: {stats.get('successful', 0)}",
                )
            else:
                fail_test("Metrics Stats", "Success=False")
        else:
            fail_test("Metrics Stats", f"Status: {response.status_code}")
    except Exception as e:
        fail_test("Metrics Stats", str(e))

    # Test 27: Recent conversations
    print_test("Recent Conversations")
    try:
        response = requests.get(
            f"{BASE_URL}/api/metrics/conversations?limit=10", timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                conversations = data.get("conversations", [])
                pass_test(
                    "Recent Conversations", f"Found {len(conversations)} conversations"
                )
            else:
                fail_test("Recent Conversations", "Success=False")
        else:
            fail_test("Recent Conversations", f"Status: {response.status_code}")
    except Exception as e:
        fail_test("Recent Conversations", str(e))

    # Test 28: Recent errors
    print_test("Recent Errors")
    try:
        response = requests.get(f"{BASE_URL}/api/metrics/errors?limit=10", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                errors = data.get("errors", [])
                pass_test("Recent Errors", f"Found {len(errors)} errors")
            else:
                fail_test("Recent Errors", "Success=False")
        else:
            fail_test("Recent Errors", f"Status: {response.status_code}")
    except Exception as e:
        fail_test("Recent Errors", str(e))


def test_context_switching():
    """Test 29-30: Context switching between different content types"""
    print_header("CONTEXT SWITCHING TESTS")

    # Test 29: Switch from Epic to Feature context
    print_test("Epic to Feature Context Switch")
    try:
        # Create Epic context
        success1, epic = test_chat_endpoint(
            "epic", "Create an Epic for mobile app development", "llama3.2", "ollama"
        )

        # Switch to Feature context (simulating active Epic)
        success2, feature = test_chat_endpoint(
            "feature", "Create a feature for push notifications", "llama3.2", "ollama"
        )

        if success1 and success2:
            pass_test(
                "Epic to Feature Context Switch", "Successfully switched contexts"
            )
        else:
            fail_test("Epic to Feature Context Switch", "One or both contexts failed")
    except Exception as e:
        fail_test("Epic to Feature Context Switch", str(e))

    # Test 30: Multiple context types in sequence
    print_test("Multiple Context Sequence")
    try:
        contexts = [
            ("strategic-initiative", "What is a good strategic initiative?"),
            ("epic", "What makes a good epic?"),
            ("feature", "What are feature best practices?"),
            ("story", "How to write good user stories?"),
        ]

        all_success = True
        for context_type, message in contexts:
            success, _ = test_chat_endpoint(context_type, message, "llama3.2", "ollama")
            if not success:
                all_success = False

        if all_success:
            pass_test("Multiple Context Sequence", "All contexts handled correctly")
        else:
            fail_test("Multiple Context Sequence", "Some contexts failed")
    except Exception as e:
        fail_test("Multiple Context Sequence", str(e))


def test_edge_cases():
    """Test 31-34: Edge cases and error handling"""
    print_header("EDGE CASE TESTS")

    # Test 31: Empty message
    print_test("Empty Message Handling")
    try:
        payload = {
            "message": "",
            "contextType": "epic",
            "model": "llama3.2",
            "provider": "ollama",
        }
        response = requests.post(f"{BASE_URL}/api/chat", json=payload, timeout=10)
        if response.status_code == 400:
            pass_test("Empty Message Handling", "Correctly rejected empty message")
        else:
            warn_test("Empty Message Handling", f"Status: {response.status_code}")
    except Exception as e:
        fail_test("Empty Message Handling", str(e))

    # Test 32: Very long message
    print_test("Long Message Handling")
    try:
        long_message = "Help me create an Epic. " * 200  # ~5000 chars
        success, _ = test_chat_endpoint("epic", long_message, "llama3.2", "ollama")
        if success:
            pass_test("Long Message Handling", "Handled long message successfully")
        else:
            warn_test("Long Message Handling", "Failed to handle long message")
    except Exception as e:
        fail_test("Long Message Handling", str(e))

    # Test 33: Invalid context type
    print_test("Invalid Context Type")
    try:
        payload = {
            "message": "Test message",
            "contextType": "invalid_context",
            "model": "llama3.2",
            "provider": "ollama",
        }
        response = requests.post(f"{BASE_URL}/api/chat", json=payload, timeout=10)
        # Should either reject or handle gracefully
        if response.status_code in [200, 400]:
            pass_test(
                "Invalid Context Type",
                f"Handled gracefully (Status: {response.status_code})",
            )
        else:
            fail_test(
                "Invalid Context Type", f"Unexpected status: {response.status_code}"
            )
    except Exception as e:
        fail_test("Invalid Context Type", str(e))

    # Test 34: Invalid template ID
    print_test("Invalid Template ID")
    try:
        payload = {"template_id": 99999, "template_type": "epic"}
        response = requests.post(
            f"{BASE_URL}/api/template/load", json=payload, timeout=10
        )
        if response.status_code in [404, 200]:
            data = response.json()
            if not data.get("success"):
                pass_test("Invalid Template ID", "Correctly handled invalid ID")
            else:
                warn_test("Invalid Template ID", "Returned success for invalid ID")
        else:
            warn_test(
                "Invalid Template ID", f"Unexpected status: {response.status_code}"
            )
    except Exception as e:
        fail_test("Invalid Template ID", str(e))


def print_summary():
    """Print test summary"""
    elapsed = datetime.now() - test_results["start_time"]

    print_header("TEST SUMMARY")
    print(f"\n⏱️  Total Time: {elapsed.total_seconds():.2f}s")
    print(f"\n✅ Passed: {len(test_results['passed'])}")
    print(f"❌ Failed: {len(test_results['failed'])}")
    print(f"⚠️  Warnings: {len(test_results['warnings'])}")

    if test_results["failed"]:
        print(f"\n{'='*70}")
        print("FAILED TESTS:")
        print(f"{'='*70}")
        for test_name, error in test_results["failed"]:
            print(f"\n❌ {test_name}")
            print(f"   {error}")

    if test_results["warnings"]:
        print(f"\n{'='*70}")
        print("WARNINGS:")
        print(f"{'='*70}")
        for test_name, warning in test_results["warnings"]:
            print(f"\n⚠️  {test_name}")
            print(f"   {warning}")

    # Calculate success rate
    total_tests = len(test_results["passed"]) + len(test_results["failed"])
    success_rate = (
        (len(test_results["passed"]) / total_tests * 100) if total_tests > 0 else 0
    )

    print(f"\n{'='*70}")
    print(
        f"SUCCESS RATE: {success_rate:.1f}% ({len(test_results['passed'])}/{total_tests})"
    )
    print(f"{'='*70}\n")

    return len(test_results["failed"]) == 0


def main():
    """Run all tests"""
    print_header("DISCOVERY COACH - END-TO-END TEST SUITE")
    print(f"Start Time: {test_results['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")

    # Basic connectivity tests
    print_header("CONNECTIVITY TESTS")
    if not test_health_check():
        print("\n❌ Server is not running! Please start the server first.")
        print("   Run: bash start.sh")
        return False

    ollama_available = test_ollama_status()
    models = test_ollama_models()

    if not ollama_available or not models:
        print("\n⚠️  Ollama is not available. Tests will be limited.")
        print("   To enable full testing:")
        print("   1. Install Ollama: https://ollama.ai")
        print("   2. Pull a model: ollama pull llama3.2")
        print("   3. Ensure Ollama is running")
        return False

    # Workflow tests
    test_epic_workflow()
    test_strategic_initiative_workflow()
    test_feature_workflow()
    test_story_workflow()
    test_pi_objectives_workflow()

    # Database tests
    test_template_database()

    # Monitoring tests
    test_monitoring_endpoints()

    # Context switching tests
    test_context_switching()

    # Edge cases
    test_edge_cases()

    # Print summary
    success = print_summary()

    return success


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Fatal error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
