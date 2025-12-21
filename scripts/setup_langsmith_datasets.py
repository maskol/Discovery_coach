#!/usr/bin/env python3
"""
LangSmith Dataset Setup Script
Creates test datasets for monitoring and evaluation of Discovery Coach

Usage:
    python scripts/setup_langsmith_datasets.py

Prerequisites:
    - LANGCHAIN_API_KEY set in environment or .env
    - langsmith package installed (pip install langsmith)
"""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv

# Add backend to path for imports
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Load environment variables
load_dotenv()

try:
    from langsmith import Client
except ImportError:
    print("❌ Error: langsmith package not found")
    print("Install with: pip install langsmith")
    sys.exit(1)

# Initialize LangSmith client
try:
    client = Client()
    print("✅ Connected to LangSmith API")
except Exception as e:
    print(f"❌ Error connecting to LangSmith: {e}")
    print("Make sure LANGCHAIN_API_KEY is set in your .env file")
    sys.exit(1)


def create_epic_questions_dataset():
    """Create dataset for Epic-related questions"""

    dataset_name = "discovery-coach-epic-questions"
    description = "Common questions about Epic creation and management in SAFe"

    # Check if dataset already exists
    try:
        existing = client.read_dataset(dataset_name=dataset_name)
        print(f"📦 Dataset '{dataset_name}' already exists (ID: {existing.id})")
        return existing
    except:
        pass

    # Create new dataset
    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description=description,
    )
    print(f"✨ Created dataset: {dataset_name}")

    # Define test examples
    examples = [
        {
            "inputs": {"message": "How do I write a good epic hypothesis statement?"},
            "outputs": {
                "expected_topics": ["hypothesis", "template", "format", "measurable"],
                "should_mention": ["business outcome", "leading indicators"],
            },
        },
        {
            "inputs": {
                "message": "What's the difference between an epic and a feature?"
            },
            "outputs": {
                "expected_topics": ["definition", "scope", "hierarchy", "size"],
                "should_mention": ["epic", "feature", "scope"],
            },
        },
        {
            "inputs": {"message": "Can you help me draft an epic?"},
            "outputs": {
                "expected_behavior": "should offer to use template",
                "should_ask_for": ["business context", "hypothesis", "outcomes"],
            },
        },
        {
            "inputs": {"message": "How do I calculate WSJF for my epic?"},
            "outputs": {
                "expected_topics": ["WSJF", "prioritization", "business value"],
                "should_mention": ["cost of delay", "job size"],
            },
        },
        {
            "inputs": {"message": "What should be in the MVP for an epic?"},
            "outputs": {
                "expected_topics": ["MVP", "minimum viable", "scope"],
                "should_mention": ["features", "outcomes", "hypothesis"],
            },
        },
        {
            "inputs": {"message": "How many features should an epic have?"},
            "outputs": {
                "expected_topics": ["features", "epic size", "scope"],
                "should_mention": ["depends", "outcomes", "complexity"],
            },
        },
        {
            "inputs": {"message": "What are leading indicators in an epic?"},
            "outputs": {
                "expected_topics": ["leading indicators", "metrics", "hypothesis"],
                "should_mention": ["measurable", "early signals", "validation"],
            },
        },
        {
            "inputs": {"message": "Can you evaluate my epic?"},
            "outputs": {
                "expected_behavior": "should ask for epic content",
                "action": "evaluate",
            },
        },
    ]

    # Add examples to dataset
    client.create_examples(
        dataset_id=dataset.id,
        inputs=[ex["inputs"] for ex in examples],
        outputs=[ex["outputs"] for ex in examples],
    )

    print(f"  ➕ Added {len(examples)} examples")
    return dataset


def create_strategic_initiative_dataset():
    """Create dataset for Strategic Initiative questions"""

    dataset_name = "discovery-coach-strategic-initiatives"
    description = "Questions about Strategic Initiatives and business outcomes"

    # Check if dataset already exists
    try:
        existing = client.read_dataset(dataset_name=dataset_name)
        print(f"📦 Dataset '{dataset_name}' already exists (ID: {existing.id})")
        return existing
    except:
        pass

    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description=description,
    )
    print(f"✨ Created dataset: {dataset_name}")

    examples = [
        {
            "inputs": {"message": "How do I define a strategic initiative?"},
            "outputs": {
                "expected_topics": [
                    "strategic",
                    "business outcome",
                    "customer segment",
                ],
                "should_mention": ["OKR", "outcomes", "strategy"],
            },
        },
        {
            "inputs": {
                "message": "What's the difference between a strategic initiative and an epic?"
            },
            "outputs": {
                "expected_topics": ["hierarchy", "strategic", "epic", "scope"],
                "should_mention": ["higher level", "business strategy"],
            },
        },
        {
            "inputs": {"message": "Help me create OKRs for my initiative"},
            "outputs": {
                "expected_topics": ["OKR", "objectives", "key results"],
                "should_mention": ["measurable", "time-bound", "outcomes"],
            },
        },
        {
            "inputs": {"message": "How do I identify customer segments?"},
            "outputs": {
                "expected_topics": ["customer", "segment", "persona"],
                "should_mention": ["needs", "characteristics", "value"],
            },
        },
        {
            "inputs": {
                "message": "What milestones should a strategic initiative have?"
            },
            "outputs": {
                "expected_topics": ["milestones", "timeline", "deliverables"],
                "should_mention": ["target dates", "success criteria"],
            },
        },
    ]

    client.create_examples(
        dataset_id=dataset.id,
        inputs=[ex["inputs"] for ex in examples],
        outputs=[ex["outputs"] for ex in examples],
    )

    print(f"  ➕ Added {len(examples)} examples")
    return dataset


def create_feature_questions_dataset():
    """Create dataset for Feature-related questions"""

    dataset_name = "discovery-coach-feature-questions"
    description = "Common questions about Feature creation in SAFe"

    # Check if dataset already exists
    try:
        existing = client.read_dataset(dataset_name=dataset_name)
        print(f"📦 Dataset '{dataset_name}' already exists (ID: {existing.id})")
        return existing
    except:
        pass

    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description=description,
    )
    print(f"✨ Created dataset: {dataset_name}")

    examples = [
        {
            "inputs": {"message": "How do I write good acceptance criteria?"},
            "outputs": {
                "expected_topics": ["acceptance criteria", "testing", "done"],
                "should_mention": ["testable", "specific", "measurable"],
            },
        },
        {
            "inputs": {"message": "What's the benefit hypothesis for a feature?"},
            "outputs": {
                "expected_topics": ["benefit hypothesis", "value", "outcomes"],
                "should_mention": ["measurable", "user", "business value"],
            },
        },
        {
            "inputs": {"message": "Help me break down a feature into user stories"},
            "outputs": {
                "expected_behavior": "should guide story splitting",
                "should_mention": ["user", "story", "independent"],
            },
        },
        {
            "inputs": {"message": "How do I estimate a feature?"},
            "outputs": {
                "expected_topics": ["estimation", "sizing", "effort"],
                "should_mention": ["story points", "complexity", "team"],
            },
        },
    ]

    client.create_examples(
        dataset_id=dataset.id,
        inputs=[ex["inputs"] for ex in examples],
        outputs=[ex["outputs"] for ex in examples],
    )

    print(f"  ➕ Added {len(examples)} examples")
    return dataset


def create_pi_objectives_dataset():
    """Create dataset for PI Objectives questions"""

    dataset_name = "discovery-coach-pi-objectives"
    description = "Questions about PI Planning and Objectives"

    # Check if dataset already exists
    try:
        existing = client.read_dataset(dataset_name=dataset_name)
        print(f"📦 Dataset '{dataset_name}' already exists (ID: {existing.id})")
        return existing
    except:
        pass

    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description=description,
    )
    print(f"✨ Created dataset: {dataset_name}")

    examples = [
        {
            "inputs": {"message": "How do I write a PI Objective?"},
            "outputs": {
                "expected_topics": ["PI Objective", "outcomes", "committed"],
                "should_mention": ["SMART", "business value", "team"],
            },
        },
        {
            "inputs": {
                "message": "What's the difference between committed and uncommitted objectives?"
            },
            "outputs": {
                "expected_topics": ["committed", "uncommitted", "stretch goals"],
                "should_mention": ["capacity", "confidence", "risk"],
            },
        },
        {
            "inputs": {"message": "How many PI Objectives should we have?"},
            "outputs": {
                "expected_topics": ["planning", "capacity", "focus"],
                "should_mention": ["3-5", "realistic", "team capacity"],
            },
        },
    ]

    client.create_examples(
        dataset_id=dataset.id,
        inputs=[ex["inputs"] for ex in examples],
        outputs=[ex["outputs"] for ex in examples],
    )

    print(f"  ➕ Added {len(examples)} examples")
    return dataset


def create_quality_evaluation_dataset():
    """Create dataset for testing quality of generated content"""

    dataset_name = "discovery-coach-quality-checks"
    description = "Test cases for validating quality of AI responses"

    # Check if dataset already exists
    try:
        existing = client.read_dataset(dataset_name=dataset_name)
        print(f"📦 Dataset '{dataset_name}' already exists (ID: {existing.id})")
        return existing
    except:
        pass

    dataset = client.create_dataset(
        dataset_name=dataset_name,
        description=description,
    )
    print(f"✨ Created dataset: {dataset_name}")

    examples = [
        {
            "inputs": {
                "message": "Draft an epic for improving customer onboarding",
                "context_type": "epic",
            },
            "outputs": {
                "must_have_sections": [
                    "EPIC NAME",
                    "EPIC HYPOTHESIS STATEMENT",
                    "BUSINESS CONTEXT",
                    "LEADING INDICATORS",
                ],
                "quality_criteria": {
                    "has_measurable_outcomes": True,
                    "has_clear_hypothesis": True,
                    "follows_template": True,
                },
            },
        },
        {
            "inputs": {
                "message": "What are the key components of an epic?",
                "context_type": "epic",
            },
            "outputs": {
                "should_explain": [
                    "hypothesis",
                    "business context",
                    "outcomes",
                    "leading indicators",
                ],
                "should_be_concise": True,
                "should_reference_safe": True,
            },
        },
    ]

    client.create_examples(
        dataset_id=dataset.id,
        inputs=[ex["inputs"] for ex in examples],
        outputs=[ex["outputs"] for ex in examples],
    )

    print(f"  ➕ Added {len(examples)} examples")
    return dataset


def main():
    """Main execution function"""

    print("\n" + "=" * 70)
    print("🚀 LangSmith Dataset Setup for Discovery Coach")
    print("=" * 70 + "\n")

    # Verify API key
    api_key = os.getenv("LANGCHAIN_API_KEY")
    if not api_key or api_key == "your-langsmith-api-key-here":
        print("❌ Error: LANGCHAIN_API_KEY not set properly")
        print("\nSteps to fix:")
        print("1. Sign up at https://smith.langchain.com/")
        print("2. Get your API key from Settings > API Keys")
        print("3. Add to .env file: LANGCHAIN_API_KEY=your-actual-key")
        print("4. Run this script again")
        sys.exit(1)

    print(f"🔑 API Key: {api_key[:10]}...{api_key[-4:]}\n")

    # Create datasets
    datasets_created = []

    try:
        datasets_created.append(create_epic_questions_dataset())
        datasets_created.append(create_strategic_initiative_dataset())
        datasets_created.append(create_feature_questions_dataset())
        datasets_created.append(create_pi_objectives_dataset())
        datasets_created.append(create_quality_evaluation_dataset())

        print("\n" + "=" * 70)
        print("✅ Dataset Setup Complete!")
        print("=" * 70)
        print(f"\n📊 Created/Updated {len(datasets_created)} datasets\n")

        print("Next Steps:")
        print("1. View datasets at: https://smith.langchain.com/")
        print("2. Run evaluations with: python scripts/run_langsmith_evaluations.py")
        print("3. Monitor traces in LangSmith dashboard")
        print("\n")

    except Exception as e:
        print(f"\n❌ Error creating datasets: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
