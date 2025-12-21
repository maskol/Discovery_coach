# Strategic Initiative Tab Display Fix

**Issue:** When working with Strategic Initiative, the response was appearing in the Epic tab instead of the Strategic Initiative tab.

**Root Cause:** 
The `simulateCoachResponse` function in `script.js` was hard-coding focus to `messageInput` (Epic tab's input field) after receiving a response, regardless of which tab was active.

```javascript
// Before (line 193)
document.getElementById('messageInput').focus();  // Always Epic tab
```

**Fix:**
Modified the focus logic to detect the currently active tab and focus that tab's input field:

```javascript
// After
const activeTab = document.querySelector('.main-tab.active');
if (activeTab) {
    const tabId = activeTab.id;
    const inputMap = {
        'strategicInitiativesTab': 'messageInputStrategicInitiatives',
        'piObjectivesTab': 'messageInputPIObjectives',
        'epicsTab': 'messageInput',
        'featuresTab': 'messageInputFeatures',
        'storiesTab': 'messageInputStories'
    };
    const inputId = inputMap[tabId] || 'messageInput';
    const inputElement = document.getElementById(inputId);
    if (inputElement) {
        inputElement.focus();
    }
}
```

**Additional Enhancement:**
Added Strategic Initiative auto-detection in backend (`app.py` line 257):

```python
elif (
    "INITIATIVE NAME" in response_text or "1. INITIATIVE NAME" in response_text
) and (
    "STRATEGIC CONTEXT" in response_text
    or "CUSTOMER / USER SEGMENT" in response_text
):
    active_context["strategic_initiative"] = response_text
    print("✅ Strategic Initiative automatically detected and stored in active_context")
```

**Files Modified:**
- `frontend/script.js` - Lines 189-208 (focus logic)
- `backend/app.py` - Lines 257-263 (Strategic Initiative detection)

**Testing:**
1. Open Discovery Coach GUI
2. Navigate to Strategic Initiatives tab
3. Send message: "Help me create a strategic initiative for digital transformation"
4. Verify response appears in Strategic Initiatives tab (not Epic tab)
5. Verify input focus remains on Strategic Initiatives tab

**Impact:** 
- All context types (Strategic Initiative, PI Objectives, Features, Stories, Epics) now correctly maintain focus on their respective tabs
- Strategic Initiative content is now auto-detected and stored
- Consistent user experience across all tabs
