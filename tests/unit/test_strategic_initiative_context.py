#!/usr/bin/env python3
"""Quick test for Strategic Initiative context routing"""

import json

import requests

BASE_URL = "http://localhost:8050"


def test_strategic_initiative():
    """Test that Strategic Initiative responses appear in correct context"""

    print("Testing Strategic Initiative context...")
    print("=" * 70)

    # Test 1: Draft Strategic Initiative
    payload = {
        "message": "Help me create a strategic initiative for digital transformation",
        "contextType": "strategic-initiative",
        "provider": "ollama",
        "model": "llama3.2",
    }

    print(f"\n📤 Sending: {payload['message']}")
    print(f"   Context Type: {payload['contextType']}")

    response = requests.post(f"{BASE_URL}/api/chat", json=payload, timeout=60)

    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            response_text = data.get("response", "")
            metadata = data.get("metadata", {})

            print(f"\n✅ Response received ({len(response_text)} chars)")
            print(f"   Intent: {metadata.get('intent')}")
            print(f"   Retry count: {metadata.get('retry_count')}")

            # Check if response contains Strategic Initiative markers
            has_initiative_name = "INITIATIVE NAME" in response_text
            has_strategic_context = "STRATEGIC CONTEXT" in response_text

            print(f"\n📋 Content Analysis:")
            print(f"   Contains 'INITIATIVE NAME': {has_initiative_name}")
            print(f"   Contains 'STRATEGIC CONTEXT': {has_strategic_context}")

            if has_initiative_name and has_strategic_context:
                print(f"\n✅ SUCCESS: Strategic Initiative content detected!")
                print(f"   This should appear in Strategic Initiative tab.")
            else:
                print(f"\n⚠️  WARNING: Expected Strategic Initiative format not found")
                print(f"   Response preview: {response_text[:200]}...")

            return True
        else:
            print(f"\n❌ API returned error: {data.get('error')}")
            return False
    else:
        print(f"\n❌ HTTP Error {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        return False


if __name__ == "__main__":
    try:
        test_strategic_initiative()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
