# Template Filling Feature

## Overview
The Discovery Coach now includes functionality to automatically fill Epic and Feature templates with conversation output.

## How It Works

### Fill Epic Template
1. **Have a Discovery Conversation**: Engage in a detailed discovery conversation with the coach about your initiative
2. **Click "📝 Fill Epic Template"**: Located in the Actions sidebar
3. **Review the Filled Template**: The system analyzes your conversation history and populates all 19 Epic template sections:
   - Epic Name
   - Epic Owner
   - Key Stakeholders
   - Business Context / Background
   - Problem / Opportunity
   - Target Customers / Users
   - Epic Hypothesis Statement
   - Desired Business Outcomes (Measurable)
   - Leading Indicators
   - MVP (Minimum Viable Product)
   - Forecasted Full Scope
   - Forecasted Costs
   - Scope / Out of Scope
   - Business Impact & Value Assumptions
   - Solution Analysis
   - Development Strategy
   - Risks, Assumptions & Constraints
   - WSJF (Optional)
   - Metrics & Measurement Plan
   - Go / No-Go Recommendation

### Fill Feature Template
1. **Have a Discovery Conversation**: Discuss feature requirements with the coach
2. **Click "📝 Fill Feature Template"**: Located in the Actions sidebar
3. **Review the Filled Template**: The system populates all 10 Feature template sections:
   - Feature Name
   - Feature Type (Optional)
   - Description
   - Benefit Hypothesis
   - Acceptance Criteria (AC)
   - Non-Functional Requirements (NFR)
   - Dependencies
   - Assumptions & Constraints
   - WSJF – High Level (Optional)
   - Implementation Notes (Optional)

## Key Features

### Intelligent Template Population
- **Context-Aware**: Uses your entire conversation history to fill template fields
- **Epic/Feature Context**: Considers active Epic and Feature names
- **Smart Inference**: When information isn't explicitly discussed, provides reasonable inferences or notes what's needed

### Flexible LLM Support
- Works with both **OpenAI** (external) and **Ollama** (local) models
- Uses your current model and temperature settings
- 6-minute timeout for complex template filling

### User-Friendly Output
- Maintains template structure and formatting
- Ready to copy and paste into your documentation system
- Includes helpful tips after generation

## Usage Tips

1. **Comprehensive Conversations**: The more detailed your discovery conversation, the better the template will be filled
2. **Review and Refine**: Always review the filled template and adjust as needed - it's a starting point
3. **Save Your Work**: Use the session save feature to preserve conversations for later template generation
4. **Iterate**: You can fill templates multiple times as your conversation evolves

## Technical Details

### Backend Endpoint
- **URL**: `POST /api/fill-template`
- **Request Body**:
  ```json
  {
    "template_type": "epic" | "feature",
    "conversationHistory": [...],
    "activeEpic": "optional epic name",
    "activeFeature": "optional feature name",
    "model": "gpt-4o-mini",
    "temperature": 0.7,
    "provider": "openai" | "ollama"
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "template_type": "epic",
    "content": "filled template text...",
    "message": "Epic template filled successfully"
  }
  ```

### Frontend Functions
- `fillEpicTemplate()`: Fills Epic template with conversation output
- `fillFeatureTemplate()`: Fills Feature template with conversation output

Both functions:
- Check for conversation history before proceeding
- Show loading status during processing
- Display filled template in chat interface
- Include helpful tips for next steps

## Difference from Draft Epic/Feature

| Feature | Draft Epic/Feature | Fill Template |
|---------|-------------------|---------------|
| **Purpose** | Generate a narrative draft | Fill structured template fields |
| **Format** | Conversational/prose | Structured sections with headers |
| **Sections** | May summarize or omit sections | All sections explicitly filled |
| **Use Case** | Quick overview for review | Complete documentation ready for systems |
| **Output Style** | Flowing text | Template with placeholders replaced |

Both features are valuable and can be used together - draft first for review, then fill template for formal documentation.
