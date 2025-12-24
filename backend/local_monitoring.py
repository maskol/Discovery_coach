"""
Local Logging and Monitoring for Discovery Coach
Provides observability without external services
"""

import json
import logging
import os
import time
from datetime import datetime
from functools import wraps
from pathlib import Path
from typing import Any, Dict, Optional

# ============================================================================
# Logger Configuration
# ============================================================================

# Create logs directory
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_TO_FILE = os.getenv("LOG_TO_FILE", "true").lower() == "true"

# Create formatters
detailed_formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

json_formatter = logging.Formatter(
    '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(name)s", '
    '"function": "%(funcName)s", "line": %(lineno)d, "message": "%(message)s"}',
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Create logger
logger = logging.getLogger("discovery_coach")
logger.setLevel(getattr(logging, LOG_LEVEL))

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(detailed_formatter)
logger.addHandler(console_handler)

# File handler (daily rotation)
if LOG_TO_FILE:
    today = datetime.now().strftime("%Y-%m-%d")
    log_file = LOGS_DIR / f"discovery_coach_{today}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)

# JSON log file for structured analysis
if LOG_TO_FILE:
    json_log_file = LOGS_DIR / f"discovery_coach_{today}.json"
    json_handler = logging.FileHandler(json_log_file)
    json_handler.setFormatter(json_formatter)
    logger.addHandler(json_handler)


# ============================================================================
# Metrics Collection
# ============================================================================


class MetricsCollector:
    """Collects and stores metrics locally"""

    def __init__(self):
        self.metrics_file = LOGS_DIR / "metrics.json"
        self.metrics = self._load_metrics()

    def _load_metrics(self) -> Dict:
        """Load existing metrics or create new structure"""
        if self.metrics_file.exists():
            try:
                with open(self.metrics_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass

        return {
            "conversations": [],
            "daily_stats": {},
            "errors": [],
            "performance": {
                "avg_latency": [],
                "by_context_type": {},
                "by_intent": {},
            },
        }

    def _save_metrics(self):
        """Save metrics to file"""
        with open(self.metrics_file, "w", encoding="utf-8") as f:
            json.dump(self.metrics, f, indent=2)

    def log_conversation(
        self,
        context_type: str,
        intent: str,
        model: str,
        provider: str,
        latency: float,
        success: bool,
        retry_count: int = 0,
        validation_issues: Optional[list] = None,
    ):
        """Log a conversation"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "context_type": context_type,
            "intent": intent,
            "model": model,
            "provider": provider,
            "latency": latency,
            "success": success,
            "retry_count": retry_count,
            "validation_issues": validation_issues or [],
        }

        self.metrics["conversations"].append(entry)

        # Update daily stats
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.metrics["daily_stats"]:
            self.metrics["daily_stats"][today] = {
                "total": 0,
                "success": 0,
                "errors": 0,
                "avg_latency": 0,
                "retries": 0,
            }

        stats = self.metrics["daily_stats"][today]
        stats["total"] += 1
        if success:
            stats["success"] += 1
        else:
            stats["errors"] += 1
        stats["retries"] += retry_count

        # Update average latency
        old_avg = stats["avg_latency"]
        stats["avg_latency"] = (old_avg * (stats["total"] - 1) + latency) / stats[
            "total"
        ]

        # Update performance by context type
        if context_type not in self.metrics["performance"]["by_context_type"]:
            self.metrics["performance"]["by_context_type"][context_type] = []
        self.metrics["performance"]["by_context_type"][context_type].append(latency)

        # Update performance by intent
        if intent not in self.metrics["performance"]["by_intent"]:
            self.metrics["performance"]["by_intent"][intent] = []
        self.metrics["performance"]["by_intent"][intent].append(latency)

        # Keep only last 1000 conversations in memory
        if len(self.metrics["conversations"]) > 1000:
            self.metrics["conversations"] = self.metrics["conversations"][-1000:]

        self._save_metrics()

        logger.info(
            f"Conversation logged: {context_type}/{intent} - "
            f"{latency:.2f}s - {'✓' if success else '✗'} - "
            f"retries: {retry_count}"
        )

    def log_error(
        self,
        error_type: str,
        error_message: str,
        context: Optional[Dict] = None,
    ):
        """Log an error"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "message": error_message,
            "context": context or {},
        }

        self.metrics["errors"].append(entry)

        # Keep only last 100 errors
        if len(self.metrics["errors"]) > 100:
            self.metrics["errors"] = self.metrics["errors"][-100:]

        self._save_metrics()

        logger.error(f"Error logged: {error_type} - {error_message}")

    def get_stats(self, days: int = 7) -> Dict:
        """Get statistics for last N days"""
        from datetime import timedelta

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        stats = {
            "period": f"Last {days} days",
            "total_conversations": 0,
            "successful": 0,
            "errors": 0,
            "avg_latency": 0,
            "total_retries": 0,
            "by_context_type": {},
            "by_intent": {},
            "daily_breakdown": {},
        }

        for date_str, day_stats in self.metrics["daily_stats"].items():
            date = datetime.fromisoformat(date_str)
            if start_date.date() <= date.date() <= end_date.date():
                stats["total_conversations"] += day_stats["total"]
                stats["successful"] += day_stats["success"]
                stats["errors"] += day_stats["errors"]
                stats["total_retries"] += day_stats["retries"]
                stats["daily_breakdown"][date_str] = day_stats

        # Calculate average latency
        if stats["total_conversations"] > 0:
            total_latency = sum(
                day["avg_latency"] * day["total"]
                for day in stats["daily_breakdown"].values()
            )
            stats["avg_latency"] = total_latency / stats["total_conversations"]

        # Performance by context type
        for context, latencies in self.metrics["performance"][
            "by_context_type"
        ].items():
            if latencies:
                stats["by_context_type"][context] = {
                    "count": len(latencies),
                    "avg": sum(latencies) / len(latencies),
                    "min": min(latencies),
                    "max": max(latencies),
                }

        # Performance by intent
        for intent, latencies in self.metrics["performance"]["by_intent"].items():
            if latencies:
                stats["by_intent"][intent] = {
                    "count": len(latencies),
                    "avg": sum(latencies) / len(latencies),
                    "min": min(latencies),
                    "max": max(latencies),
                }

        return stats


# Global metrics collector
metrics_collector = MetricsCollector()


# ============================================================================
# Decorators
# ============================================================================


def log_workflow_execution(func):
    """Decorator to log workflow execution"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()

        # Extract state from args if available
        state = args[0] if args else kwargs.get("state", {})
        context_type = (
            state.get("context_type", "unknown")
            if isinstance(state, dict)
            else "unknown"
        )

        logger.info(f"Starting workflow: {func.__name__} for {context_type}")

        try:
            result = await func(*args, **kwargs)
            elapsed = time.time() - start_time
            logger.info(f"Completed workflow: {func.__name__} in {elapsed:.2f}s")
            return result
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                f"Workflow failed: {func.__name__} after {elapsed:.2f}s - {str(e)}"
            )
            raise

    return wrapper


def log_node_execution(node_name: str):
    """Decorator to log node execution in LangGraph"""

    def decorator(func):
        @wraps(func)
        async def wrapper(state, *args, **kwargs):
            start_time = time.time()

            context_type = state.get("context_type", "unknown")
            intent = state.get("intent", "unknown")

            logger.debug(f"Node [{node_name}] starting - {context_type}/{intent}")

            try:
                result = await func(state, *args, **kwargs)
                elapsed = time.time() - start_time
                logger.debug(f"Node [{node_name}] completed in {elapsed:.2f}s")
                return result
            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(
                    f"Node [{node_name}] failed after {elapsed:.2f}s - {str(e)}"
                )

                metrics_collector.log_error(
                    error_type=f"node_error_{node_name}",
                    error_message=str(e),
                    context={
                        "node": node_name,
                        "context_type": context_type,
                        "intent": intent,
                    },
                )
                raise

        return wrapper

    return decorator


# ============================================================================
# Utility Functions
# ============================================================================


def log_api_request(
    endpoint: str,
    method: str = "POST",
    status_code: int = 200,
    latency: float = 0.0,
):
    """Log API request"""
    logger.info(f"API {method} {endpoint} - {status_code} - {latency:.2f}s")


def log_llm_call(
    model: str,
    provider: str,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    latency: float = 0.0,
):
    """Log LLM API call"""
    logger.info(
        f"LLM call: {provider}/{model} - "
        f"{prompt_tokens}→{completion_tokens} tokens - {latency:.2f}s"
    )


def get_daily_report() -> str:
    """Generate daily report"""
    stats = metrics_collector.get_stats(days=1)

    report = f"""
📊 Discovery Coach Daily Report
{'='*50}
Date: {datetime.now().strftime('%Y-%m-%d')}

Conversations: {stats['total_conversations']}
  ✓ Successful: {stats['successful']}
  ✗ Errors: {stats['errors']}
  🔄 Retries: {stats['total_retries']}

Performance:
  Avg Latency: {stats['avg_latency']:.2f}s

By Context Type:
"""

    for context, perf in stats["by_context_type"].items():
        report += (
            f"  {context}: {perf['count']} conversations, {perf['avg']:.2f}s avg\n"
        )

    report += "\nBy Intent:\n"
    for intent, perf in stats["by_intent"].items():
        report += f"  {intent}: {perf['count']} conversations, {perf['avg']:.2f}s avg\n"

    return report


def export_metrics(output_file: Optional[str] = None) -> str:
    """Export metrics to JSON file"""
    if output_file is None:
        output_file = (
            LOGS_DIR / f"metrics_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

    stats = metrics_collector.get_stats(days=30)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)

    logger.info(f"Metrics exported to {output_file}")
    return str(output_file)


# ============================================================================
# CLI for viewing logs
# ============================================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "report":
        print(get_daily_report())
    elif len(sys.argv) > 1 and sys.argv[1] == "stats":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        stats = metrics_collector.get_stats(days=days)
        print(json.dumps(stats, indent=2))
    elif len(sys.argv) > 1 and sys.argv[1] == "export":
        output = sys.argv[2] if len(sys.argv) > 2 else None
        export_metrics(output)
    else:
        print("Usage:")
        print("  python local_monitoring.py report      - Show daily report")
        print("  python local_monitoring.py stats [N]   - Show stats for last N days")
        print("  python local_monitoring.py export [F]  - Export metrics to file")
