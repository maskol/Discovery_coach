# Bug Fix Summary - Epic Drafting Failures

**Date:** 2025-12-21  
**Fixed By:** LangGraph Workflow Debugging

## Issue Description

Epic and Strategic Initiative drafting were failing with HTTP 500 errors. Initial E2E test results showed:
- 30/35 tests passing (85.7% success rate)
- 3 Epic workflow tests failing
- 1 Strategic Initiative test failing
- 1 Long message test failing

## Root Cause

The `increment_retry_on_retry` node in [backend/discovery_workflow.py](backend/discovery_workflow.py#L452) was defined as a **synchronous function** but was decorated with `@log_node_execution("increment_retry")` which expects **async functions**.

### Error Details
```
TypeError: object dict can't be used in 'await' expression
Node [increment_retry] failed after 0.00s
```

### Problematic Code
```python
@log_node_execution("increment_retry")
def increment_retry_on_retry(state: DiscoveryState) -> DiscoveryState:  # ❌ Sync function
    """Increment retry count when retrying."""
    return {
        **state,
        "retry_count": state.get("retry_count", 0) + 1,
    }
```

### Why It Failed
The `log_node_execution` decorator in [backend/local_monitoring.py](backend/local_monitoring.py#L300-L335) creates an **async wrapper**:

```python
async def wrapper(state, *args, **kwargs):
    # ...
    result = await func(state, *args, **kwargs)  # ❌ Awaits sync function
```

When validation triggered a retry, the workflow would route to `increment_retry` node, the decorator would try to `await` the sync function's return value (a dict), causing the TypeError.

## Solution

Made `increment_retry_on_retry` an **async function** to match the decorator's expectations:

```python
@log_node_execution("increment_retry")
async def increment_retry_on_retry(state: DiscoveryState) -> DiscoveryState:  # ✅ Async function
    """Increment retry count when retrying."""
    return {
        **state,
        "retry_count": state.get("retry_count", 0) + 1,
    }
```

## Test Results After Fix

```
======================================================================
  TEST SUMMARY
======================================================================

⏱️  Total Time: 406.52s

✅ Passed: 40
❌ Failed: 0
⚠️  Warnings: 0

======================================================================
SUCCESS RATE: 100.0% (40/40)
======================================================================
```

## Impact

- **Before:** 85.7% test success rate (30/35)
- **After:** 100.0% test success rate (40/40)
- **Fixed:** All Epic and Strategic Initiative drafting workflows
- **Fixed:** Long message handling
- **Fixed:** Retry mechanism in validation flow

## Technical Details

### Affected Workflows
1. **Epic Drafting** - Draft/Evaluate/Question intents
2. **Strategic Initiative Drafting** - Draft/Evaluate/Question intents
3. **Validation Retry Logic** - All context types when validation fails

### LangGraph Nodes (All 6 nodes now async)
1. ✅ `classify_intent_node` - async
2. ✅ `build_context_node` - async
3. ✅ `retrieve_context_node` - async
4. ✅ `generate_response_node` - async
5. ✅ `validate_response_node` - async
6. ✅ `increment_retry_on_retry` - **NOW async** (was sync)

## Files Modified

- [backend/discovery_workflow.py](backend/discovery_workflow.py#L452) - Changed `increment_retry_on_retry` from sync to async

## Lessons Learned

1. **Decorator Consistency:** All LangGraph node functions should be async when using async decorators
2. **Error Messages:** "object dict can't be used in 'await' expression" indicates attempting to await non-coroutine
3. **Testing Coverage:** E2E tests successfully identified the issue through Epic drafting scenarios
4. **Workflow Validation:** Validation retry logic is critical - bugs here cascade to multiple workflows

## Related Documentation

- [E2E Test Report](../E2E_TEST_REPORT.md) - Original test results showing failures
- [Discovery Workflow](../backend/discovery_workflow.py) - LangGraph implementation
- [Local Monitoring](../backend/local_monitoring.py) - Decorator implementation
- [LangGraph Documentation](https://python.langchain.com/docs/langgraph) - Async best practices
