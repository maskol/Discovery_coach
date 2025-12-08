// State management
const state = {
    activeEpic: null,
    activeFeature: null,
    conversationHistory: [],
    isLoading: false,
    inputHistory: [],
    historyIndex: -1,
    model: 'gpt-4o-mini',
    temperature: 0.7
};

// Timeout wrapper for fetch with configurable timeout
async function fetchWithTimeout(url, options = {}, timeout = 120000) { // 2 minute default timeout
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);

    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal
        });
        clearTimeout(id);
        return response;
    } catch (error) {
        clearTimeout(id);
        if (error.name === 'AbortError') {
            throw new Error('Request timeout - the server took too long to respond. Try with a shorter conversation or simpler request.');
        }
        throw error;
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    addSystemMessage('Welcome to Discovery Coach! I am your CDM coaching assistant. Load an Epic or Feature to get started, or ask me any Epic or Feature related questions.');
    document.getElementById('messageInput').focus();

    // Add arrow key navigation for input history
    document.getElementById('messageInput').addEventListener('keydown', (e) => {
        if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (state.inputHistory.length > 0) {
                if (state.historyIndex === -1) {
                    state.historyIndex = state.inputHistory.length - 1;
                } else if (state.historyIndex > 0) {
                    state.historyIndex--;
                }
                document.getElementById('messageInput').value = state.inputHistory[state.historyIndex];
            }
        } else if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (state.historyIndex !== -1) {
                state.historyIndex++;
                if (state.historyIndex >= state.inputHistory.length) {
                    state.historyIndex = -1;
                    document.getElementById('messageInput').value = '';
                } else {
                    document.getElementById('messageInput').value = state.inputHistory[state.historyIndex];
                }
            }
        }
    });
});

// Message handling
function sendMessage(event) {
    event.preventDefault();
    const input = document.getElementById('messageInput');
    const message = input.value.trim();

    if (!message || state.isLoading) return;

    // Add to input history
    if (message !== state.inputHistory[state.inputHistory.length - 1]) {
        state.inputHistory.push(message);
    }
    state.historyIndex = -1;

    // Add user message
    addUserMessage(message);
    state.conversationHistory.push({ role: 'user', content: message });
    input.value = '';

    // Process command or send to coach
    if (message.toLowerCase() === 'outline epic') {
        outlineEpic();
    } else if (message.toLowerCase() === 'outline feature') {
        outlineFeature();
    } else if (message.toLowerCase() === 'new epic') {
        newEpic();
    } else if (message.toLowerCase() === 'new feature') {
        newFeature();
    } else if (message.toLowerCase() === 'help') {
        showHelp();
    } else {
        // Simulate coaching response (in production, this would call your backend)
        simulateCoachResponse(message);
    }
}

async function simulateCoachResponse(userMessage) {
    state.isLoading = true;
    updateStatus('Coach is thinking...');
    document.getElementById('sendBtn').disabled = true;

    try {
        // Call the actual backend API
        const response = await fetchWithTimeout('http://localhost:8050/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: userMessage,
                activeEpic: state.activeEpic,
                activeFeature: state.activeFeature,
                model: state.model,
                temperature: state.temperature
            })
        }, 120000); // 2 minute timeout

        const data = await response.json();

        if (data.success) {
            // Add agent message
            addAgentMessage(data.response);
            state.conversationHistory.push({ role: 'agent', content: data.response });
        } else {
            addAgentMessage(`❌ Error: ${data.error}\n\nMake sure the Discovery Coach backend server is running:\n\`python app.py\``);
        }

    } catch (error) {
        console.error('API Error:', error);
        addAgentMessage(`⚠️ Cannot connect to Discovery Coach backend.\n\nPlease start the server:\n1. Open terminal in Discovery_coach folder\n2. Run: \`python app.py\`\n3. Server should start on http://localhost:8050`);
    } finally {
        state.isLoading = false;
        updateStatus('Ready');
        document.getElementById('sendBtn').disabled = false;
        document.getElementById('messageInput').focus();
        scrollToBottom();
    }
}

// generateCoachResponse function removed - now using real backend API
// The Python discovery_coach.py with GPT-4 and RAG handles all responses

function generateCoachResponse_DEPRECATED(userMessage) {
    // This function is deprecated - kept for reference only
    // All responses now come from the Python backend
    const lowerMessage = userMessage.toLowerCase();

    if (/\b(hello|hi|hey)\b/.test(lowerMessage) && lowerMessage.length < 20) {
        return `👋 Hello! I'm your Discovery Coach, here to help you create well-defined Epics and Features aligned with CDM principles.\n\nI can help you with:\n• **Epic Hypothesis Statements** - structured problem/solution format\n• **Business Outcomes** - measurable results\n• **Leading Indicators** - early success signals\n• **Features** - acceptance criteria, benefits, user value\n• **Evaluation** - feedback on your current content\n\n### Next Steps:\n1. Tell me what you're working on (Epic or Feature)\n2. Share the challenge you're facing\n3. I'll provide targeted coaching`;
    }

    // Check conversation history to detect if user is providing follow-up details
    const userMessages = state.conversationHistory
        .filter(msg => msg.role === 'user')
        .map(msg => msg.content.toLowerCase());

    const agentMessages = state.conversationHistory
        .filter(msg => msg.role === 'agent')
        .map(msg => msg.content.toLowerCase());

    const isFollowUpMessage = userMessages.length > 1; // More than one user message in history
    const currentMessageHasDetails = lowerMessage.length > 10; // Substantive message

    // Check if previous agent message was asking questions (contains "Next Steps:" or question marks)
    const previousAgentAskedQuestions = agentMessages.length > 0 &&
        (agentMessages[agentMessages.length - 1].includes('next steps:') ||
            agentMessages[agentMessages.length - 1].includes('?'));

    // Detect if this appears to be additional context/refinement
    const isProblemDescription = (lowerMessage.includes('customer') || lowerMessage.includes('user')) &&
        (lowerMessage.includes('problem') || lowerMessage.includes('connectivity') ||
            lowerMessage.includes('remote') || lowerMessage.includes('video') ||
            lowerMessage.includes('meeting') || lowerMessage.includes('document'));

    // Check if user is providing specific details in response to our questions
    const hasLocationDetails = /\b(sweden|northern|southern|region|area|location|country|city|town|rural|urban)\b/.test(lowerMessage);
    const hasDepartmentDetails = /\b(department|team|group|division|unit|sales|engineering|marketing)\b/.test(lowerMessage);
    const hasQuantification = /\b(\d+|many|several|some|few|most|all|half|percent)\b/.test(lowerMessage);
    const hasTimeframeDetails = /\b(daily|weekly|monthly|often|always|sometimes|rarely|hour|day|week|month)\b/.test(lowerMessage);

    // If user is answering our questions with specifics, continue the dialogue
    if (isFollowUpMessage && previousAgentAskedQuestions && currentMessageHasDetails) {
        let acknowledgedDetails = [];

        if (hasLocationDetails) {
            acknowledgedDetails.push('✓ Customer location: ' + (lowerMessage.match(/\b(sweden|northern|southern|rural|urban)\b/)?.[0] || 'specified'));
        }
        if (hasDepartmentDetails) {
            acknowledgedDetails.push('✓ Department/group identified');
        }
        if (hasQuantification) {
            acknowledgedDetails.push('✓ Scope/quantity noted');
        }
        if (hasTimeframeDetails) {
            acknowledgedDetails.push('✓ Timeframe/frequency mentioned');
        }

        // Determine what else we still need
        const needsImpactQuantification = !hasQuantification && !hasTimeframeDetails;
        const needsSolutionApproach = !lowerMessage.includes('solution') && !lowerMessage.includes('implement') && !lowerMessage.includes('build');
        const needsBusinessOutcome = !lowerMessage.includes('reduce') && !lowerMessage.includes('increase') && !lowerMessage.includes('improve');

        return `Great! You're building up the Epic details. ${acknowledgedDetails.length > 0 ? '\n\n' + acknowledgedDetails.join('\n') : ''}\n\nLet's continue refining. I still need:\n\n${needsImpactQuantification ? '1. **Impact Quantification:** How often/how many?\n   - How frequently do connectivity problems occur?\n   - How many customers are affected?\n   - What\'s the productivity impact? (Hours lost per week?)\n\n' : ''}2. **Business Outcome:** What measurable result do you want?\n   - Example: "Reduce video call failures by 80%"\n   - Example: "Increase remote work satisfaction from 6 to 8.5"\n   - Example: "Reduce support tickets by 50%"\n\n3. **Proposed Solution:** What will you implement?\n   - Network infrastructure upgrades?\n   - Local edge servers in northern Sweden?\n   - Improved VPN/bandwidth?\n   - Alternative collaboration tools?\n\n### Next Steps:\n1. ${needsImpactQuantification ? 'Share the frequency/impact of the problem' : 'Define your measurable business outcome'}\n2. Describe what solution you're considering\n3. I'll help you structure the complete Epic Hypothesis Statement`;
    }

    // If user is providing follow-up details to refine the problem, ask for business outcome/solution
    if (isFollowUpMessage && currentMessageHasDetails && isProblemDescription) {
        // Extract any specific details they mentioned to acknowledge them
        let acknowledgedDetails = [];
        if (/\b(sweden|northern|southern|region|area|location|country|city|town)\b/.test(lowerMessage)) {
            acknowledgedDetails.push('Geographic location specified');
        }
        if (lowerMessage.includes('complain') || lowerMessage.includes('concern') || lowerMessage.includes('feedback')) {
            acknowledgedDetails.push('Customer feedback captured');
        }
        if (/\b(\d+|many|several|some|few|most)\b/.test(lowerMessage)) {
            acknowledgedDetails.push('Scope/quantity indicated');
        }

        return `Excellent! You're adding important details. ${acknowledgedDetails.length > 0 ? 'I noticed: ' + acknowledgedDetails.join(', ') + '.' : ''}\n\nNow let's define the **Business Outcome** and **Solution**. I need:\n\n1. **Measurable Business Outcome:** What specific metric will improve?\n   - Example: "Reduce video call dropouts by 80%"\n   - Example: "Increase remote work productivity by 25%"\n   - Example: "Improve customer satisfaction score from 6.5 to 8.5"\n\n2. **Proposed Solution:** What will you build/implement?\n   - Network infrastructure upgrade?\n   - New VPN solution?\n   - Edge servers or CDN?\n   - Bandwidth optimization tools?\n\n3. **Success Timeline:** When should results be visible?\n   - Q1 2026? Within 6 months? 12 months?\n\n### Next Steps:\n1. Define ONE specific, measurable business outcome with a target\n2. Describe your proposed solution approach\n3. I'll help you structure the complete Epic Hypothesis Statement`;
    }

    // Epic-related questions
    if (lowerMessage.includes('epic') || lowerMessage.includes('business outcome') || lowerMessage.includes('hypothesis')) {
        if (lowerMessage.includes('business outcome')) {
            return `Great question about Business Outcome! This is critical for your Epic. The Business Outcome must be:\n\n• Measurable (specific metrics, %s, timeframes)\n• Business-focused (not technical)\n• Achievable within your planning horizon\n\n### Next Steps:\n1. What is the specific metric you want to improve?\n2. What's your target value and timeline?\n3. How will you measure this in production?`;
        } else if (lowerMessage.includes('hypothesis') && (lowerMessage.includes('customer') || lowerMessage.includes('user') || lowerMessage.includes('problem') || lowerMessage.length > 30)) {
            // User is describing their hypothesis - provide structured guidance
            return `Excellent! I can see you're describing the problem space. Let me help you structure this into a proper Epic Hypothesis Statement.\n\nBased on what you shared, let's build it using the CDM format:\n\n**For** <customers>\n**who** <do something>\n**the** <solution>\n**is a** <something – the 'how'>\n**that** <provides this value>\n**unlike** <competitor, current solution or non-existing solution>\n**our solution** <does something better — the 'why'>\n\nHere's a draft based on your input:\n\nFor [remote workers]\nwho [have connectivity problems affecting video meetings and document sharing]\nthe [your solution name]\nis a [describe the solution approach]\nthat [provides reliable connectivity and collaboration]\nunlike [current unreliable remote access solutions]\nour solution [ensures seamless remote work with improved performance and reliability]\n\n### Next Steps:\n1. What specific solution are you proposing?\n2. What makes your solution better than current alternatives?\n3. What measurable improvement will users see?`;
        } else if (lowerMessage.includes('hypothesis') && lowerMessage.length < 30) {
            return `Excellent! The Hypothesis Statement is the foundation of your Epic. Remember the format:\n\nFor <customers>\nwho <do something>\nthe <solution>\nis a <something – the 'how'>\nthat <provides this value>\nunlike <competitor, current solution or non-existing solution>\nour solution <does something better — the 'why'>\n\n### Next Steps:\n1. Have you clearly identified your target customers?\n2. Is the problem statement specific and measurable?\n3. Does your solution clearly differentiate from alternatives?`;
        } else if (lowerMessage.includes('leading indicator')) {
            return `Leading Indicators are early signals that predict your Business Outcome. They should:\n\n• Lead the outcome by weeks or months\n• Be measurable and observable\n• Be within your control\n• Include specific targets\n\nExamples: user adoption rate, feature usage, support tickets reduction, performance metrics\n\n### Next Steps:\n1. What early signals would indicate you're on track?\n2. How will you measure these signals?\n3. What targets make sense for your initiative?`;
        } else if (lowerMessage.includes('epic name') || (lowerMessage.includes('name') && lowerMessage.includes('epic'))) {
            return `The Epic Name should be clear and descriptive, capturing the essence of what you're trying to achieve.\n\n• Keep it concise (3-5 words)\n• Focus on the outcome or value, not the solution\n• Make it memorable and business-focused\n\nExamples:\n- Reduce Time-to-Market for B2B Services\n- Improve Customer Onboarding Experience\n- Enable Real-Time Payment Processing\n- Enhance Remote Work Connectivity\n\n### Next Steps:\n1. What's the primary business value you're delivering?\n2. Who are the main beneficiaries?\n3. What outcome should the name emphasize?`;
        } else if (lowerMessage.includes('scope')) {
            return `Defining Scope is crucial to keep your Epic manageable. Clearly state:\n\n**In Scope:**\n- What systems/processes are included\n- Which customer segments are affected\n- What capabilities will be delivered\n\n**Out of Scope:**\n- What you explicitly won't do (even if related)\n- Why certain items are excluded\n\n### Next Steps:\n1. What are the core capabilities you must include?\n2. What related work should be excluded to keep scope manageable?\n3. Are there dependencies on other epics?`;
        } else if (lowerMessage.includes('risk') || lowerMessage.includes('assumption') || lowerMessage.includes('constraint')) {
            return `Identifying Risks, Assumptions, and Constraints is essential for realistic planning.\n\n**Assumptions:** What are we taking as true?\n- Stakeholder adoption\n- Technology availability\n- Market conditions\n\n**Constraints:** What limits us?\n- Budget\n- Timeline\n- Resource availability\n\n**Risks:** What could go wrong?\n- Technical complexity\n- Change resistance\n- External dependencies\n\n### Next Steps:\n1. What's your biggest assumption that could fail?\n2. What constraints are non-negotiable?\n3. What's the top risk to success?`;
        } else if (lowerMessage.includes('epic') && lowerMessage.length < 20) {
            return `I see you're working on an Epic! To give you the best coaching, which aspect would you like to focus on?\n\n• **Business Outcome** - measurable results you want to achieve\n• **Hypothesis Statement** - structured problem/solution format\n• **Leading Indicators** - early signals of success\n• **Scope** - what's in/out of the epic\n• **Risks & Assumptions** - what could go wrong\n• **WSJF** - prioritization scoring\n\n### Next Steps:\n1. Pick one aspect to work on\n2. Share your current thinking\n3. I'll provide targeted feedback`;
        }
    }
    // Feature-related questions
    else if (lowerMessage.includes('feature')) {
        if (lowerMessage.includes('acceptance criteria') || lowerMessage.includes('acceptance')) {
            return `Excellent focus on Acceptance Criteria! These define how we know the Feature is complete. Use Gherkin format:\n\nGiven [context]\nWhen [user action]\nThen [expected result]\n\nMake each criterion testable and observable.\n\nExamples:\n- Given a user has saved payment methods\n  When they start checkout\n  Then they see saved methods in a dropdown\n\n### Next Steps:\n1. What are the main user scenarios?\n2. What are the success conditions for each?\n3. Are all criteria testable by QA?`;
        } else if (lowerMessage.includes('benefit') || lowerMessage.includes('value')) {
            return `The Benefit Hypothesis connects your Feature to business value. It should clearly state:\n\n• What customer problem it solves\n• Who benefits\n• How it delivers measurable value\n\nGood example: "Reduces checkout time by 40%, increasing conversion rate by 15%"\nPoor example: "Improves user experience"\n\n### Next Steps:\n1. What customer pain does this solve?\n2. How will you measure adoption?\n3. What's the success metric?`;
        } else if (lowerMessage.includes('feature name') || (lowerMessage.includes('name') && lowerMessage.includes('feature'))) {
            return `Feature Names should be clear and user-centric:\n\n• User-facing language (not technical)\n• Action-oriented or outcome-focused\n• Specific about what user can do\n\nGood: "One-Click Payment Save"\nPoor: "Payment Persistence Enhancement"\n\n### Next Steps:\n1. What does the user actually do?\n2. What's the primary benefit?\n3. Can a non-technical person understand it?`;
        } else if (lowerMessage.includes('description')) {
            return `A good Feature Description explains:\n\n• What capability is being delivered\n• How users interact with it\n• Why it matters\n\nKeep it to 2-3 sentences, focus on user value, not implementation.\n\n### Next Steps:\n1. What is the core capability?\n2. How will users interact with it?\n3. What problem does it solve?`;
        } else {
            return `I see you're working on a Feature! Let me help with the key areas:\n\n• **Acceptance Criteria** - testable requirements (Gherkin format)\n• **Benefit Hypothesis** - value delivered to users\n• **Name** - clear, user-focused naming\n• **Description** - what the feature does\n• **Stories** - detailed user stories\n\n### Next Steps:\n1. Which aspect do you need help with?\n2. Share what you have so far\n3. I'll provide targeted feedback`;
        }
    }
    // Help questions
    else if (lowerMessage.includes('help') || lowerMessage.includes('how do i')) {
        return `I can help you with:\n\n📋 **Templates & Formats:**\n- Epic Hypothesis Statement structure\n- Feature acceptance criteria (Gherkin format)\n- Business outcome definitions\n\n💡 **Coaching Topics:**\n- Defining measurable business outcomes\n- Identifying leading indicators\n- Creating testable acceptance criteria\n- Writing hypothesis statements\n- Scope management\n\n🔧 **Actions:**\n- Load and evaluate existing content\n- View active Epic/Feature\n- Clear context and start fresh\n\n### Next Steps:\n1. Click the Help button for detailed guidance\n2. Ask about a specific topic (epic, feature, outcome, etc.)\n3. Share your content for evaluation`;
    }
    // Empty or very unclear input
    else if (lowerMessage.length < 5) {
        return `I'm ready to help! Could you tell me more about what you're working on?\n\nFor example:\n- "I'm creating an epic for mobile payments"\n- "Help me define success metrics"\n- "How do I write acceptance criteria?"\n- "What's a leading indicator?"\n\n### Next Steps:\n1. Describe your challenge or question\n2. Share the topic (Epic, Feature, Business Outcome, etc.)\n3. I'll provide targeted coaching`;
    }
    // Check if this is an initial problem description about connectivity/remote work
    else if (isProblemDescription && !isFollowUpMessage) {
        // First mention of the problem - acknowledge and ask for more details
        return `Great! You've identified a real customer problem. Let me help you refine this into an Epic.\n\n**What I heard:**\n- Customers have connectivity issues when working remotely\n- Problems with video meetings and document sharing\n\n**To create a strong Epic, I need more specifics:**\n\n1. **Who specifically?**\n   - Which customer segment? (Geographic location? Department? Role?)\n   - How many customers are affected?\n   - Is this all remote workers or specific groups?\n\n2. **How big is the impact?**\n   - How often do these problems occur?\n   - What's the business impact? (Lost productivity? Revenue? Satisfaction?)\n   - Can you quantify the pain? (Hours lost? Meetings failed?)\n\n3. **Current situation:**\n   - What do they use today?\n   - Why isn't it working?\n   - What have they tried?\n\n### Next Steps:\n1. Identify the specific customer segment (location, role, size)\n2. Quantify the business impact\n3. Share more details so I can help structure your Epic`;
    }
    // Default: provide helpful generic coaching
    else {
        return `I understand you're sharing context about your Epic. To avoid repeating questions, let me provide a different approach.\n\n**Based on our conversation, you might be ready to:**\n\n1. **Create the Epic Hypothesis Statement** - Use the format:\n   - For [customers in northern Sweden]\n   - who [work remotely and face connectivity issues]\n   - the [solution name]\n   - is a [type of solution]\n   - that [benefit]\n   - unlike [current approach]\n   - our solution [differentiation]\n\n2. **Define Business Outcome** - What measurable result do you want?\n   - "Reduce [metric] by X%"\n   - "Increase [metric] from X to Y"\n   - "Achieve [target] by [date]"\n\n3. **Ask a Specific Question** - What aspect do you need help with?\n   - Business outcome?\n   - Solution approach?\n   - Leading indicators?\n   - Scope definition?\n\n### Next Steps:\n1. Type "business outcome" to define measurable results\n2. Type "hypothesis" to structure your Epic statement\n3. Ask a specific question about your Epic\n4. Share your proposed solution approach`;
    }
}

// UI Functions
function addUserMessage(text) {
    const messagesDiv = document.getElementById('messages');
    const msgEl = document.createElement('div');
    msgEl.className = 'message user';
    msgEl.innerHTML = `
        <div>
            <div class="message-content">${escapeHtml(text)}</div>
            <div class="message-time">${new Date().toLocaleTimeString()}</div>
        </div>
    `;
    messagesDiv.appendChild(msgEl);
    scrollToBottom();
}

function addAgentMessage(text) {
    const messagesDiv = document.getElementById('messages');
    const msgEl = document.createElement('div');
    msgEl.className = 'message agent';
    msgEl.innerHTML = `
        <div>
            <div class="message-content">${formatMessage(text)}</div>
            <div class="message-time">${new Date().toLocaleTimeString()}</div>
        </div>
    `;
    messagesDiv.appendChild(msgEl);
    scrollToBottom();
}

function addSystemMessage(text) {
    const messagesDiv = document.getElementById('messages');
    const msgEl = document.createElement('div');
    msgEl.className = 'message agent';
    msgEl.innerHTML = `
        <div>
            <div class="message-content" style="font-style: italic; color: #666;">${formatMessage(text)}</div>
        </div>
    `;
    messagesDiv.appendChild(msgEl);
}

function scrollToBottom() {
    const messagesDiv = document.getElementById('messages');
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function updateStatus(text) {
    document.getElementById('status').textContent = text;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatMessage(text) {
    return text
        .replace(/\n/g, '<br>')
        .replace(/###\s+Next Steps:/g, '<strong style="color: #667eea;">### Next Steps:</strong>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>');
}

// Action Functions
// Show summary of collected information
async function showSummary() {
    state.isLoading = true;
    updateStatus('Generating discovery summary...');
    document.getElementById('sendBtn').disabled = true;

    try {
        const response = await fetchWithTimeout('http://localhost:8050/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: 'Provide a brief summary of the key discovery information collected. Focus on: 1) Customer/User details, 2) Core problems identified, 3) Business impact, 4) What we still need. Keep it concise.',
                activeEpic: state.activeEpic,
                activeFeature: state.activeFeature,
                model: state.model,
                temperature: state.temperature
            })
        }, 180000); // 3 minute timeout for summary generation

        const data = await response.json();

        if (data.success) {
            addAgentMessage('📊 **Discovery Summary:**\n\n' + data.response);
            state.conversationHistory.push({ role: 'agent', content: data.response });
        }
    } catch (error) {
        addSystemMessage(`❌ Error getting summary: ${error.message}`);
        console.error('Summary error:', error);
    } finally {
        state.isLoading = false;
        updateStatus('Ready');
        document.getElementById('sendBtn').disabled = false;
    }
}

async function draftEpic() {
    state.isLoading = true;
    updateStatus('Drafting Epic based on discovery conversation...');
    document.getElementById('sendBtn').disabled = true;

    try {
        const response = await fetchWithTimeout('http://localhost:8050/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: 'Based on our discovery conversation, please draft a complete Epic using the Epic template format. Include all sections: Epic Name, Epic Owner, Business Context, Problem/Opportunity, Target Customers, Epic Hypothesis Statement, Desired Business Outcomes, Leading Indicators, MVP, Forecasted Full Scope, Scope/Out of Scope, Business Impact, Risks/Assumptions/Constraints, WSJF, and Metrics. Use the information we have discussed to fill in each section.',
                activeEpic: state.activeEpic,
                activeFeature: state.activeFeature,
                model: state.model,
                temperature: state.temperature
            })
        }, 180000); // 3 minute timeout for epic drafting

        const data = await response.json();

        if (data.success) {
            addSystemMessage('✍️ **Epic Draft:**\n\n' + data.response);
            // The Epic will be auto-detected and stored by the backend
        }
    } catch (error) {
        addSystemMessage(`❌ Error drafting Epic: ${error.message}`);
    } finally {
        state.isLoading = false;
        updateStatus('Ready');
        document.getElementById('sendBtn').disabled = false;
    }
}

async function draftFeature() {
    state.isLoading = true;
    updateStatus('Drafting Feature based on discovery conversation...');
    document.getElementById('sendBtn').disabled = true;

    try {
        const response = await fetchWithTimeout('http://localhost:8050/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: 'Based on our discovery conversation, please draft a complete Feature using the Feature template format. Include: Feature Name, Feature Owner, Business Context, User Story (As a... I want... So that...), Acceptance Criteria (in Given-When-Then format), Dependencies, Risks, and Success Metrics. Use the information we have discussed to fill in each section.',
                activeEpic: state.activeEpic,
                activeFeature: state.activeFeature,
                model: state.model,
                temperature: state.temperature
            })
        }, 120000); // 2 minute timeout

        const data = await response.json();

        if (data.success) {
            addSystemMessage('✍️ **Feature Draft:**\n\n' + data.response);
            // The Feature will be auto-detected and stored by the backend
        }
    } catch (error) {
        addSystemMessage(`❌ Error drafting Feature: ${error.message}`);
    } finally {
        state.isLoading = false;
        updateStatus('Ready');
        document.getElementById('sendBtn').disabled = false;
    }
}

async function evaluateEpic() {
    const content = prompt('Paste your Epic content here (or paste a file path):');
    if (content) {
        state.activeEpic = content;
        updateActiveContextDisplay();
        addSystemMessage(`📋 Epic loaded. ${content.length} characters. Evaluating against CDM best practices...`);

        try {
            const response = await fetchWithTimeout('http://localhost:8050/api/evaluate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type: 'epic', content: content })
            }, 120000); // 2 minute timeout
            const data = await response.json();
            if (data.success) {
                addAgentMessage(data.response);
                state.conversationHistory.push({ role: 'agent', content: data.response });
            }
        } catch (error) {
            addAgentMessage('⚠️ Backend connection error. Start server with: python app.py');
        }
    }
}

async function evaluateFeature() {
    const content = prompt('Paste your Feature content here:');
    if (content) {
        state.activeFeature = content;
        updateActiveContextDisplay();
        addSystemMessage(`📋 Feature loaded. ${content.length} characters. Evaluating against CDM best practices...`);

        try {
            const response = await fetchWithTimeout('http://localhost:8050/api/evaluate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ type: 'feature', content: content })
            }, 120000); // 2 minute timeout
            const data = await response.json();
            if (data.success) {
                addAgentMessage(data.response);
                state.conversationHistory.push({ role: 'agent', content: data.response });
            }
        } catch (error) {
            addAgentMessage('⚠️ Backend connection error. Start server with: python app.py');
        }
    }
}

async function outlineEpic() {
    state.isLoading = true;
    updateStatus('Retrieving Epic...');
    document.getElementById('sendBtn').disabled = true;

    try {
        const response = await fetchWithTimeout('http://localhost:8050/api/outline', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: 'epic' })
        }, 30000); // 30 second timeout

        const data = await response.json();

        if (data.success && data.content) {
            state.activeEpic = data.content;
            addAgentMessage(`📋 **Current Epic:**\n\n${data.content}`);
            state.conversationHistory.push({ role: 'agent', content: `📋 **Current Epic:**\n\n${data.content}` });

            // Ask follow-up question
            const followUpResponse = await fetchWithTimeout('http://localhost:8050/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: 'I have shown the current Epic. What would you like to do next? Would you like to: 1) Evaluate this Epic against CDM best practices, 2) Refine specific sections, 3) Break it down into Features, or 4) Continue with something else?',
                    activeEpic: state.activeEpic,
                    activeFeature: state.activeFeature,
                    model: state.model,
                    temperature: state.temperature
                })
            }, 60000); // 1 minute timeout

            const followUpData = await followUpResponse.json();
            if (followUpData.success) {
                addAgentMessage(followUpData.response);
                state.conversationHistory.push({ role: 'agent', content: followUpData.response });
            }
        } else {
            addSystemMessage(data.message || 'No Epic content available yet. Continue the discovery conversation, and when ready, ask the coach to "draft the epic" or "create epic outline".');
        }
    } catch (error) {
        addSystemMessage(`❌ Error retrieving Epic: ${error.message}`);
    } finally {
        state.isLoading = false;
        updateStatus('Ready');
        document.getElementById('sendBtn').disabled = false;
    }
}

async function outlineFeature() {
    state.isLoading = true;
    updateStatus('Retrieving Feature...');
    document.getElementById('sendBtn').disabled = true;

    try {
        const response = await fetchWithTimeout('http://localhost:8050/api/outline', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: 'feature' })
        }, 30000); // 30 second timeout

        const data = await response.json();

        if (data.success && data.content) {
            state.activeFeature = data.content;
            addAgentMessage(`📋 **Current Feature:**\n\n${data.content}`);
            state.conversationHistory.push({ role: 'agent', content: `📋 **Current Feature:**\n\n${data.content}` });

            // Ask follow-up question
            const followUpResponse = await fetchWithTimeout('http://localhost:8050/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: 'I have shown the current Feature. What would you like to do next? Would you like to: 1) Evaluate this Feature against CDM best practices, 2) Refine the acceptance criteria, 3) Identify dependencies, or 4) Continue with something else?',
                    activeEpic: state.activeEpic,
                    activeFeature: state.activeFeature,
                    model: state.model,
                    temperature: state.temperature
                })
            }, 60000); // 1 minute timeout

            const followUpData = await followUpResponse.json();
            if (followUpData.success) {
                addAgentMessage(followUpData.response);
                state.conversationHistory.push({ role: 'agent', content: followUpData.response });
            }
        } else {
            addSystemMessage(data.message || 'No Feature content available yet. Continue the discovery conversation, and when ready, ask the coach to "draft the feature".');
        }
    } catch (error) {
        addSystemMessage(`❌ Error retrieving Feature: ${error.message}`);
    } finally {
        state.isLoading = false;
        updateStatus('Ready');
        document.getElementById('sendBtn').disabled = false;
    }
}

async function newEpic() {
    state.activeEpic = null;
    updateActiveContextDisplay();

    try {
        await fetchWithTimeout('http://localhost:8050/api/clear', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: 'epic' })
        }, 30000); // 30 second timeout
    } catch (error) {
        console.log('Backend clear failed (OK if server not running)');
    }

    addSystemMessage('🔄 [NEW EPIC SESSION] Previous epic cleared. Ready for a new epic session.');
}

async function newFeature() {
    state.activeFeature = null;
    updateActiveContextDisplay();

    try {
        await fetchWithTimeout('http://localhost:8050/api/clear', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: 'feature' })
        }, 30000); // 30 second timeout
    } catch (error) {
        console.log('Backend clear failed (OK if server not running)');
    }

    addSystemMessage('🔄 [NEW FEATURE SESSION] Previous feature cleared. Ready for a new feature session.');
}

async function clearAll() {
    state.activeEpic = null;
    state.activeFeature = null;
    state.conversationHistory = [];
    updateActiveContextDisplay();
    document.getElementById('messages').innerHTML = '';

    try {
        await fetchWithTimeout('http://localhost:8050/api/clear', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: 'all' })
        }, 30000); // 30 second timeout
    } catch (error) {
        console.log('Backend clear failed (OK if server not running)');
    }

    addSystemMessage('🗑️ All context and history cleared. Starting fresh!');
}

// Model settings functions
function updateModelSettings() {
    const modelSelect = document.getElementById('modelSelect');
    state.model = modelSelect.value;
    addSystemMessage(`🔧 Model changed to: ${state.model}`);
}

function updateTemperature() {
    const slider = document.getElementById('temperatureSlider');
    state.temperature = parseFloat(slider.value);
    document.getElementById('tempValue').textContent = state.temperature;
}

// Session management functions
async function saveSession() {
    try {
        const response = await fetchWithTimeout('http://localhost:8050/api/session/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                activeEpic: state.activeEpic,
                activeFeature: state.activeFeature,
                conversationHistory: state.conversationHistory,
                messages: document.getElementById('messages').innerHTML
            })
        }, 30000); // 30 second timeout

        const data = await response.json();

        if (data.success) {
            addSystemMessage(`💾 ${data.message}`);
        } else {
            addSystemMessage('❌ Failed to save session');
        }
    } catch (error) {
        addSystemMessage(`❌ Error saving session: ${error.message}`);
    }
}

async function loadSession() {
    try {
        // Get list of available sessions
        const listResponse = await fetchWithTimeout('http://localhost:8050/api/session/list', {}, 30000); // 30 second timeout
        const listData = await listResponse.json();

        if (!listData.success || listData.sessions.length === 0) {
            addSystemMessage('📂 No saved sessions found');
            return;
        }

        // Create modal to select session
        const modal = document.createElement('div');
        modal.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); display: flex; align-items: center; justify-content: center; z-index: 1000;';

        const content = document.createElement('div');
        content.style.cssText = 'background: white; padding: 2rem; border-radius: 10px; max-width: 600px; max-height: 80vh; overflow-y: auto;';

        const title = document.createElement('h2');
        title.textContent = 'Load Session';
        title.style.marginTop = '0';
        content.appendChild(title);

        const list = document.createElement('div');
        listData.sessions.forEach(session => {
            const item = document.createElement('div');
            item.style.cssText = 'padding: 1rem; margin: 0.5rem 0; border: 1px solid #ddd; border-radius: 5px; cursor: pointer; transition: background 0.2s;';
            item.innerHTML = `
                <div style="font-weight: bold;">${session.filename}</div>
                <div style="font-size: 0.9em; color: #666;">
                    Modified: ${new Date(session.modified).toLocaleString()}<br>
                    Size: ${(session.size / 1024).toFixed(2)} KB
                </div>
            `;
            item.onmouseover = () => item.style.background = '#f0f0f0';
            item.onmouseout = () => item.style.background = 'white';
            item.onclick = async () => {
                document.body.removeChild(modal);
                await loadSessionFile(session.filename);
            };
            list.appendChild(item);
        });
        content.appendChild(list);

        const closeBtn = document.createElement('button');
        closeBtn.textContent = 'Cancel';
        closeBtn.style.cssText = 'margin-top: 1rem; padding: 0.5rem 1rem; cursor: pointer;';
        closeBtn.onclick = () => document.body.removeChild(modal);
        content.appendChild(closeBtn);

        modal.appendChild(content);
        document.body.appendChild(modal);

    } catch (error) {
        addSystemMessage(`❌ Error loading sessions: ${error.message}`);
    }
}

async function loadSessionFile(filename) {
    try {
        const response = await fetchWithTimeout('http://localhost:8050/api/session/load', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ filename })
        }, 30000); // 30 second timeout

        const data = await response.json();

        if (data.success) {
            const session = data.session;

            // Restore state
            state.activeEpic = session.activeEpic || null;
            state.activeFeature = session.activeFeature || null;
            state.conversationHistory = session.conversationHistory || [];

            // Restore messages
            document.getElementById('messages').innerHTML = session.messages || '';

            // Update display
            updateActiveContextDisplay();

            // Scroll to bottom
            const messagesDiv = document.getElementById('messages');
            messagesDiv.scrollTop = messagesDiv.scrollHeight;

            addSystemMessage(`📂 ${data.message}`);
        } else {
            addSystemMessage('❌ Failed to load session');
        }
    } catch (error) {
        addSystemMessage(`❌ Error loading session: ${error.message}`);
    }
}

async function deleteSession() {
    try {
        // Get list of available sessions
        const listResponse = await fetchWithTimeout('http://localhost:8050/api/session/list', {}, 30000); // 30 second timeout
        const listData = await listResponse.json();

        if (!listData.success || listData.sessions.length === 0) {
            addSystemMessage('📂 No saved sessions found');
            return;
        }

        // Create modal to select sessions to delete
        const modal = document.createElement('div');
        modal.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); display: flex; align-items: center; justify-content: center; z-index: 1000;';

        const content = document.createElement('div');
        content.style.cssText = 'background: white; padding: 2rem; border-radius: 10px; max-width: 600px; max-height: 80vh; overflow-y: auto;';

        const title = document.createElement('h2');
        title.textContent = 'Delete Session(s)';
        title.style.marginTop = '0';
        title.style.color = '#d32f2f';
        content.appendChild(title);

        const instruction = document.createElement('p');
        instruction.textContent = 'Select sessions to delete (check the boxes):';
        instruction.style.cssText = 'color: #666; margin-bottom: 1rem;';
        content.appendChild(instruction);

        const selectedFiles = [];
        const list = document.createElement('div');

        listData.sessions.forEach(session => {
            const item = document.createElement('div');
            item.style.cssText = 'padding: 1rem; margin: 0.5rem 0; border: 1px solid #ddd; border-radius: 5px; display: flex; align-items: center; gap: 1rem;';

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            checkbox.style.cssText = 'width: 20px; height: 20px; cursor: pointer;';
            checkbox.onchange = (e) => {
                if (e.target.checked) {
                    selectedFiles.push(session.filename);
                    item.style.background = '#ffebee';
                } else {
                    const index = selectedFiles.indexOf(session.filename);
                    if (index > -1) selectedFiles.splice(index, 1);
                    item.style.background = 'white';
                }
            };

            const info = document.createElement('div');
            info.style.flex = '1';
            info.innerHTML = `
                <div style="font-weight: bold;">${session.filename}</div>
                <div style="font-size: 0.9em; color: #666;">
                    Modified: ${new Date(session.modified).toLocaleString()}<br>
                    Size: ${(session.size / 1024).toFixed(2)} KB
                </div>
            `;

            item.appendChild(checkbox);
            item.appendChild(info);
            list.appendChild(item);
        });
        content.appendChild(list);

        const buttonContainer = document.createElement('div');
        buttonContainer.style.cssText = 'margin-top: 1rem; display: flex; gap: 1rem;';

        const deleteBtn = document.createElement('button');
        deleteBtn.textContent = '🗑️ Delete Selected';
        deleteBtn.style.cssText = 'padding: 0.5rem 1rem; cursor: pointer; background: #d32f2f; color: white; border: none; border-radius: 5px; font-weight: bold;';
        deleteBtn.onclick = async () => {
            if (selectedFiles.length === 0) {
                alert('Please select at least one session to delete');
                return;
            }

            const confirmMsg = `Are you sure you want to delete ${selectedFiles.length} session(s)? This cannot be undone.`;
            if (!confirm(confirmMsg)) return;

            try {
                const response = await fetchWithTimeout('http://localhost:8050/api/session/delete', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ filenames: selectedFiles })
                }, 30000); // 30 second timeout

                const data = await response.json();

                document.body.removeChild(modal);

                if (data.success) {
                    addSystemMessage(`✅ ${data.message}`);
                    if (data.errors && data.errors.length > 0) {
                        addSystemMessage(`⚠️ Errors: ${data.errors.join(', ')}`);
                    }
                } else {
                    addSystemMessage(`❌ ${data.message}`);
                    if (data.errors) {
                        addSystemMessage(`Errors: ${data.errors.join(', ')}`);
                    }
                }
            } catch (error) {
                document.body.removeChild(modal);
                addSystemMessage(`❌ Error deleting sessions: ${error.message}`);
            }
        };

        const cancelBtn = document.createElement('button');
        cancelBtn.textContent = 'Cancel';
        cancelBtn.style.cssText = 'padding: 0.5rem 1rem; cursor: pointer; background: #666; color: white; border: none; border-radius: 5px;';
        cancelBtn.onclick = () => document.body.removeChild(modal);

        buttonContainer.appendChild(deleteBtn);
        buttonContainer.appendChild(cancelBtn);
        content.appendChild(buttonContainer);

        modal.appendChild(content);
        document.body.appendChild(modal);

    } catch (error) {
        addSystemMessage(`❌ Error loading sessions: ${error.message}`);
    }
}

function updateActiveContextDisplay() {
    const epicDiv = document.getElementById('activeEpic');
    const featureDiv = document.getElementById('activeFeature');
    const epicContent = document.getElementById('epicContent');
    const featureContent = document.getElementById('featureContent');

    if (state.activeEpic) {
        epicContent.textContent = state.activeEpic.substring(0, 200) + (state.activeEpic.length > 200 ? '...' : '');
        epicDiv.style.display = 'block';
    } else {
        epicDiv.style.display = 'none';
    }

    if (state.activeFeature) {
        featureContent.textContent = state.activeFeature.substring(0, 200) + (state.activeFeature.length > 200 ? '...' : '');
        featureDiv.style.display = 'block';
    } else {
        featureDiv.style.display = 'none';
    }
}

function showHelp() {
    document.getElementById('helpModal').classList.add('active');
}

function closeHelp() {
    document.getElementById('helpModal').classList.remove('active');
}

// Close modal when clicking outside
document.getElementById('helpModal').addEventListener('click', (e) => {
    if (e.target.id === 'helpModal') {
        closeHelp();
    }
});
