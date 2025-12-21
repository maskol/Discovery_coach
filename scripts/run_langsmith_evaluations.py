#!/usr/bin/env python3
"""
LangSmith Evaluation Runner
Runs evaluations on test datasets to measure Discovery Coach quality

Usage:
    python scripts/run_langsmith_evaluations.py [--dataset DATASET_NAME]

Examples:
    # Run all evaluations
    python scripts/run_langsmith_evaluations.py

    # Run specific dataset
    python scripts/run_langsmith_evaluations.py --dataset discovery-coach-epic-questions
"""

import argparse
import asyncio
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

# Add backend to path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))

# Load environment
load_dotenv()

try:
    from langchain.smith import RunEvalConfig, run_on_dataset
    from langsmith import Client
except ImportError:
    print("❌ Error: langsmith or langchain packages not found")
    print("Install with: pip install langsmith langchain")
    sys.exit(1)


def create_evaluators():
    """Create custom evaluators for Discovery Coach"""

    def check_epic_template_compliance(run, example):
        """Check if epic response follows template structure"""
        output = run.outputs.get("response", "")

        required_sections = [
            "EPIC NAME",
            "EPIC HYPOTHESIS STATEMENT",
            "BUSINESS CONTEXT",
            "LEADING INDICATORS",
        ]

        score = sum(1 for section in required_sections if section in output) / len(
            required_sections
        )

        return {
            "key": "epic_template_compliance",
            "score": score,
            "comment": f"Found {int(score * len(required_sections))}/{len(required_sections)} required sections",
        }

    def check_response_length(run, example):
        """Check if response is appropriate length (not too short or long)"""
        output = run.outputs.get("response", "")
        length = len(output)

        # Ideal range: 200-2000 characters for most responses
        if length < 100:
            score = 0.0
            comment = "Too short"
        elif length > 3000:
            score = 0.7
            comment = "Very long - might be too detailed"
        elif 200 <= length <= 2000:
            score = 1.0
            comment = "Good length"
        else:
            score = 0.9
            comment = "Acceptable length"

        return {
            "key": "response_length",
            "score": score,
            "comment": f"{length} chars - {comment}",
        }

    def check_actionable(run, example):
        """Check if response provides actionable guidance"""
        output = run.outputs.get("response", "").lower()

        actionable_keywords = [
            "should",
            "must",
            "can",
            "need to",
            "start by",
            "first",
            "then",
            "next",
            "example",
            "template",
            "consider",
            "ensure",
            "include",
        ]

        count = sum(1 for keyword in actionable_keywords if keyword in output)
        score = min(count / 3, 1.0)  # 3+ keywords = full score

        return {
            "key": "actionability",
            "score": score,
            "comment": f"Found {count} actionable terms",
        }

    return [
        check_epic_template_compliance,
        check_response_length,
        check_actionable,
    ]


async def run_evaluation(dataset_name: str):
    """Run evaluation on a specific dataset"""

    client = Client()

    # Check if dataset exists
    try:
        dataset = client.read_dataset(dataset_name=dataset_name)
        print(f"📊 Running evaluation on: {dataset_name}")
        print(f"   Examples: {len(list(client.list_examples(dataset_id=dataset.id)))}")
    except Exception as e:
        print(f"❌ Dataset not found: {dataset_name}")
        print(f"   Error: {e}")
        return

    # Import the chain/function to evaluate
    # This would be your actual Discovery Coach chat function
    async def discovery_coach_wrapper(inputs: dict) -> dict:
        """Wrapper to call Discovery Coach with test inputs"""
        # This is a placeholder - replace with actual API call
        message = inputs.get("message", "")

        # For now, return mock response
        # In production, this would call your actual backend
        return {"response": f"Mock response for: {message}", "success": True}

    # Configure evaluation
    eval_config = RunEvalConfig(
        evaluators=[
            "qa",  # Question answering accuracy
            "criteria:helpfulness",
            "criteria:conciseness",
            "criteria:relevance",
        ],
        custom_evaluators=create_evaluators(),
    )

    # Run evaluation
    experiment_name = f"eval-{dataset_name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    print(f"🚀 Starting evaluation: {experiment_name}")
    print("   This may take a few minutes...\n")

    try:
        results = run_on_dataset(
            client=client,
            dataset_name=dataset_name,
            llm_or_chain_factory=discovery_coach_wrapper,
            evaluation=eval_config,
            project_name=experiment_name,
        )

        print(f"✅ Evaluation complete!")
        print(f"   View results: https://smith.langchain.com/")
        print(f"   Experiment: {experiment_name}\n")

        return results
    except Exception as e:
        print(f"❌ Evaluation failed: {e}")
        return None


def main():
    """Main execution"""

    parser = argparse.ArgumentParser(description="Run LangSmith evaluations")
    parser.add_argument(
        "--dataset",
        type=str,
        help="Specific dataset to evaluate (default: all)",
        default=None,
    )
    args = parser.parse_args()

    print("\n" + "=" * 70)
    print("🧪 LangSmith Evaluation Runner")
    print("=" * 70 + "\n")

    # Verify API key
    api_key = os.getenv("LANGCHAIN_API_KEY")
    if not api_key or api_key == "your-langsmith-api-key-here":
        print("❌ Error: LANGCHAIN_API_KEY not set")
        print("Add it to your .env file and try again")
        sys.exit(1)

    # Get available datasets
    datasets = [
        "discovery-coach-epic-questions",
        "discovery-coach-strategic-initiatives",
        "discovery-coach-feature-questions",
        "discovery-coach-pi-objectives",
        "discovery-coach-quality-checks",
    ]

    if args.dataset:
        if args.dataset not in datasets:
            print(f"❌ Unknown dataset: {args.dataset}")
            print(f"Available datasets: {', '.join(datasets)}")
            sys.exit(1)
        datasets = [args.dataset]

    # Run evaluations
    print(f"📋 Will evaluate {len(datasets)} dataset(s)\n")

    for dataset_name in datasets:
        asyncio.run(run_evaluation(dataset_name))
        print()

    print("=" * 70)
    print("✅ All evaluations complete!")
    print("=" * 70)
    print("\nView detailed results at: https://smith.langchain.com/")
    print()


if __name__ == "__main__":
    main()
