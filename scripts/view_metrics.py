#!/usr/bin/env python3
"""
View Discovery Coach metrics from local monitoring
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from local_monitoring import export_metrics, get_daily_report, metrics_collector


def print_stats(days=7):
    """Print statistics for last N days"""
    stats = metrics_collector.get_stats(days=days)

    print(f"\n{'='*70}")
    print(f"📊 Discovery Coach Statistics - Last {days} Days")
    print(f"{'='*70}\n")

    print(f"Total Conversations: {stats['total_conversations']}")
    print(f"  ✅ Successful: {stats['successful']}")
    print(f"  ❌ Errors: {stats['errors']}")
    print(f"  🔄 Total Retries: {stats['total_retries']}")
    print(f"  ⏱️  Average Latency: {stats['avg_latency']:.2f}s")

    if stats["by_context_type"]:
        print(f"\n📁 By Context Type:")
        for context, perf in sorted(stats["by_context_type"].items()):
            print(
                f"  {context:20} | {perf['count']:3} convos | {perf['avg']:.2f}s avg | {perf['min']:.2f}-{perf['max']:.2f}s"
            )

    if stats["by_intent"]:
        print(f"\n🎯 By Intent:")
        for intent, perf in sorted(stats["by_intent"].items()):
            print(
                f"  {intent:20} | {perf['count']:3} convos | {perf['avg']:.2f}s avg | {perf['min']:.2f}-{perf['max']:.2f}s"
            )

    if stats["daily_breakdown"]:
        print(f"\n📅 Daily Breakdown:")
        for date_str, day_stats in sorted(stats["daily_breakdown"].items()):
            success_rate = (
                (day_stats["success"] / day_stats["total"] * 100)
                if day_stats["total"] > 0
                else 0
            )
            print(
                f"  {date_str} | {day_stats['total']:3} total | {success_rate:5.1f}% success | {day_stats['avg_latency']:.2f}s avg"
            )

    print(f"\n{'='*70}\n")


def print_recent_errors(n=10):
    """Print last N errors"""
    errors = metrics_collector.metrics.get("errors", [])

    if not errors:
        print("\n✅ No errors recorded!")
        return

    print(f"\n{'='*70}")
    print(f"❌ Last {min(n, len(errors))} Errors")
    print(f"{'='*70}\n")

    for error in errors[-n:]:
        timestamp = datetime.fromisoformat(error["timestamp"]).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        print(f"[{timestamp}] {error['type']}")
        print(f"  Message: {error['message']}")
        if error.get("context"):
            print(f"  Context: {error['context']}")
        print()


def print_recent_conversations(n=10):
    """Print last N conversations"""
    conversations = metrics_collector.metrics.get("conversations", [])

    if not conversations:
        print("\n🔇 No conversations recorded yet!")
        return

    print(f"\n{'='*70}")
    print(f"💬 Last {min(n, len(conversations))} Conversations")
    print(f"{'='*70}\n")

    for conv in conversations[-n:]:
        timestamp = datetime.fromisoformat(conv["timestamp"]).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        status = "✅" if conv["success"] else "❌"
        retry_str = (
            f" (retries: {conv['retry_count']})" if conv["retry_count"] > 0 else ""
        )

        print(
            f"[{timestamp}] {status} {conv['context_type']:15} | {conv['intent']:10} | {conv['latency']:.2f}s{retry_str}"
        )

        if conv.get("validation_issues"):
            print(f"  ⚠️  Issues: {', '.join(conv['validation_issues'])}")


def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        print("Usage:")
        print(
            "  python view_metrics.py stats [N]       - Show stats for last N days (default: 7)"
        )
        print("  python view_metrics.py report          - Show daily report")
        print(
            "  python view_metrics.py errors [N]      - Show last N errors (default: 10)"
        )
        print(
            "  python view_metrics.py conversations [N] - Show last N conversations (default: 10)"
        )
        print("  python view_metrics.py export [FILE]   - Export metrics to JSON file")
        sys.exit(1)

    command = sys.argv[1]

    if command == "stats":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        print_stats(days)

    elif command == "report":
        print(get_daily_report())

    elif command == "errors":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        print_recent_errors(n)

    elif command == "conversations":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        print_recent_conversations(n)

    elif command == "export":
        output_file = sys.argv[2] if len(sys.argv) > 2 else None
        exported = export_metrics(output_file)
        print(f"✅ Metrics exported to: {exported}")

    else:
        print(f"❌ Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
