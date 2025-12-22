// State management
const state = {
    activeStrategicInitiative: null,
    activeStrategicInitiativeId: null, // Database ID of loaded Strategic Initiative template
    activeEpic: null,
    activeEpicId: null, // Database ID of loaded Epic template
    activeFeature: null,
    activeFeatureId: null, // Database ID of loaded Feature template
    activeStory: null,
    activeStoryId: null, // Database ID of loaded Story template
    conversationHistory: [],
    isLoading: false,
    inputHistory: [],
    historyIndex: -1,
    model: 'llama3.2',
    temperature: 0.7,
    provider: 'ollama',
    ollamaModels: []
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
    // Add welcome message to all tab message containers
    const welcomeMessage = 'Welcome to Discovery Coach! I am your CDM coaching assistant. Load a Strategic Initiative, Epic, Feature, or Story to get started, or ask me any coaching questions.';

    // Add to each message container
    const messageContainers = ['messages', 'messagesStrategicInitiatives', 'messagesPIObjectives', 'messagesFeatures', 'messagesStories'];
    messageContainers.forEach(containerId => {
        const container = document.getElementById(containerId);
        if (container) {
            const msgEl = document.createElement('div');
            msgEl.className = 'message agent';
            msgEl.innerHTML = `
                <div>
                    <div class="message-content" style="font-style: italic; color: #666;">${welcomeMessage}</div>
                </div>
            `;
            container.appendChild(msgEl);
        }
    });

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

    // Initialize Ollama as default provider
    updateProviderSettings();
});

// Message handling
function sendMessage(event) {
    event.preventDefault();

    // Get the active input field based on which tab is active
    const activeTab = document.querySelector('.main-tab.active');
    let inputId = 'messageInput'; // default

    if (activeTab) {
        const tabId = activeTab.id;
        const inputMap = {
            'strategicInitiativesTab': 'messageInputStrategicInitiatives',
            'piObjectivesTab': 'messageInputPIObjectives',
            'epicsTab': 'messageInput',
            'featuresTab': 'messageInputFeatures',
            'storiesTab': 'messageInputStories'
        };
        inputId = inputMap[tabId] || 'messageInput';
    }

    const input = document.getElementById(inputId);
    if (!input) return;

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

    // Get active tab and button/input IDs once
    const activeTab = document.querySelector('.main-tab.active');
    const sendBtnMap = {
        'strategicInitiativesTab': 'sendBtnStrategicInitiatives',
        'piObjectivesTab': 'sendBtnPIObjectives',
        'epicsTab': 'sendBtn',
        'featuresTab': 'sendBtnFeatures',
        'storiesTab': 'sendBtnStories'
    };
    const inputMap = {
        'strategicInitiativesTab': 'messageInputStrategicInitiatives',
        'piObjectivesTab': 'messageInputPIObjectives',
        'epicsTab': 'messageInput',
        'featuresTab': 'messageInputFeatures',
        'storiesTab': 'messageInputStories'
    };

    // Disable the active tab's send button
    const sendBtnId = activeTab ? (sendBtnMap[activeTab.id] || 'sendBtn') : 'sendBtn';
    const sendButton = document.getElementById(sendBtnId);
    if (sendButton) sendButton.disabled = true;

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
                activeStrategicInitiative: state.activeStrategicInitiative,
                contextType: getCurrentContextType(),
                model: state.model,
                temperature: state.temperature,
                provider: state.provider
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

        // Re-enable the active tab's send button
        if (sendButton) sendButton.disabled = false;

        // Focus the active tab's input field
        if (activeTab) {
            const inputId = inputMap[activeTab.id] || 'messageInput';
            const inputElement = document.getElementById(inputId);
            if (inputElement) {
                inputElement.focus();
            }
        }

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
// Helper function to get the active messages container
function getActiveMessagesDiv() {
    // Check which main tab is active
    const activeTab = document.querySelector('.main-tab.active');
    if (!activeTab) return document.getElementById('messages');

    const tabId = activeTab.id;
    const messagesDivMap = {
        'strategicInitiativesTab': 'messagesStrategicInitiatives',
        'piObjectivesTab': 'messagesPIObjectives',
        'epicsTab': 'messages',
        'featuresTab': 'messagesFeatures',
        'storiesTab': 'messagesStories',
        'adminTab': 'messages'
    };

    const divId = messagesDivMap[tabId] || 'messages';
    return document.getElementById(divId) || document.getElementById('messages');
}

// Helper function to get the current context type based on active tab
function getCurrentContextType() {
    const activeTab = document.querySelector('.main-tab.active');
    if (!activeTab) return 'epic';

    const tabId = activeTab.id;
    const contextMap = {
        'strategicInitiativesTab': 'strategic-initiative',
        'piObjectivesTab': 'pi-objective',
        'epicsTab': 'epic',
        'featuresTab': 'feature',
        'storiesTab': 'story',
        'adminTab': 'epic'
    };

    return contextMap[tabId] || 'epic';
}

function addUserMessage(text) {
    const messagesDiv = getActiveMessagesDiv();
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
    const messagesDiv = getActiveMessagesDiv();
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
    const messagesDiv = getActiveMessagesDiv();
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
    const messagesDiv = getActiveMessagesDiv();
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

function updateStatus(text) {
    // Update status bar for the active tab
    const activeTab = document.querySelector('.main-tab.active');
    if (!activeTab) {
        document.getElementById('status').textContent = text;
        return;
    }

    const tabId = activeTab.id;
    const statusMap = {
        'strategicInitiativesTab': 'statusStrategicInitiatives',
        'piObjectivesTab': 'statusPIObjectives',
        'epicsTab': 'status',
        'featuresTab': 'statusFeatures',
        'storiesTab': 'statusStories',
        'adminTab': 'status'
    };

    const statusId = statusMap[tabId] || 'status';
    const statusElement = document.getElementById(statusId);
    if (statusElement) {
        statusElement.textContent = text;
    }
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
                temperature: state.temperature,
                provider: state.provider
            })
        }, 360000); // 6 minute timeout for summary generation

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
                temperature: state.temperature,
                provider: state.provider
            })
        }, 360000); // 6 minute timeout for epic drafting

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
                temperature: state.temperature,
                provider: state.provider
            })
        }, 360000); // 6 minute timeout for feature drafting

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
    // If we have an active Epic in state, show it directly without calling the backend
    if (state.activeEpic) {
        addAgentMessage(`📋 **Current Epic:**\n\n${state.activeEpic}`);
        state.conversationHistory.push({ role: 'agent', content: `📋 **Current Epic:**\n\n${state.activeEpic}` });
        return;
    }

    // Otherwise, fetch from backend
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
    // If we have an active Feature in state, show it directly without calling the backend
    if (state.activeFeature) {
        addAgentMessage(`📋 **Current Feature:**\n\n${state.activeFeature}`);
        state.conversationHistory.push({ role: 'agent', content: `📋 **Current Feature:**\n\n${state.activeFeature}` });
        return;
    }

    // Otherwise, fetch from backend
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
    // Clear all message containers
    const containers = ['messages', 'messagesStrategicInitiatives', 'messagesPIObjectives', 'messagesFeatures', 'messagesStories'];
    containers.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.innerHTML = '';
    });

    try {
        await fetchWithTimeout('http://localhost:8050/api/clear', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: 'all' })
        }, 30000); // 30 second timeout
    } catch (error) {
        console.log('Backend clear failed (OK if server not running)');
    }

    // Add welcome message to all tabs to initiate fresh dialogue
    const welcomeMessage = 'Welcome to Discovery Coach! I am your CDM coaching assistant. Load a Strategic Initiative, Epic, Feature, or Story to get started, or ask me any coaching questions.';
    containers.forEach(id => {
        const container = document.getElementById(id);
        if (container) {
            const msgEl = document.createElement('div');
            msgEl.className = 'message agent';
            msgEl.innerHTML = `
                <div>
                    <div class="message-content" style="font-style: italic; color: #666;">${welcomeMessage}</div>
                </div>
            `;
            container.appendChild(msgEl);
        }
    });
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

// Provider settings functions
async function updateProviderSettings() {
    const provider = document.querySelector('input[name="provider"]:checked').value;
    state.provider = provider;

    const modelSelect = document.getElementById('modelSelect');
    const statusDiv = document.getElementById('ollamaStatus');

    if (provider === 'ollama') {
        // Check Ollama status and load models
        await checkOllamaStatus();
        await loadOllamaModels();
    } else {
        // Reset to OpenAI models
        modelSelect.innerHTML = `
            <option value="gpt-4o-mini">GPT-4o Mini</option>
            <option value="gpt-4o">GPT-4o</option>
            <option value="gpt-4-turbo">GPT-4 Turbo</option>
            <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
            <option value="o1">GPT-o1</option>
        `;
        state.model = 'gpt-4o-mini';
        statusDiv.style.display = 'none';
        addSystemMessage('☁️ Switched to External (OpenAI) LLMs');
    }
}

async function checkOllamaStatus() {
    const statusDiv = document.getElementById('ollamaStatus');
    statusDiv.style.display = 'block';
    statusDiv.textContent = 'Checking Ollama connection...';
    statusDiv.style.backgroundColor = '#f0f0f0';
    statusDiv.style.color = '#666';

    try {
        const response = await fetch('http://localhost:8050/api/ollama/status');
        const data = await response.json();

        if (data.success) {
            statusDiv.textContent = `✅ ${data.message}`;
            statusDiv.style.backgroundColor = '#d4edda';
            statusDiv.style.color = '#155724';
            addSystemMessage('🏠 Switched to Local (Ollama) LLMs');
        } else {
            statusDiv.textContent = `⚠️ ${data.message}`;
            statusDiv.style.backgroundColor = '#fff3cd';
            statusDiv.style.color = '#856404';
            addSystemMessage(`⚠️ Ollama connection issue: ${data.message}`);
        }
    } catch (error) {
        statusDiv.textContent = '❌ Cannot connect to backend';
        statusDiv.style.backgroundColor = '#f8d7da';
        statusDiv.style.color = '#721c24';
        addSystemMessage('❌ Cannot check Ollama status - is the backend running?');
    }
}

async function loadOllamaModels() {
    const modelSelect = document.getElementById('modelSelect');

    try {
        const response = await fetch('http://localhost:8050/api/ollama/models');
        const data = await response.json();

        if (data.success && data.models.length > 0) {
            state.ollamaModels = data.models;

            // Populate dropdown with Ollama models
            modelSelect.innerHTML = data.models.map(model =>
                `<option value="${model}">${model}</option>`
            ).join('');

            // Set default model
            state.model = data.models[0];
            addSystemMessage(`📋 Loaded ${data.models.length} Ollama model(s)`);
        } else {
            // No models available, show placeholder
            modelSelect.innerHTML = '<option value="">No models available</option>';
            addSystemMessage('⚠️ No Ollama models found. Please pull a model first (e.g., "ollama pull llama3.2")');
        }
    } catch (error) {
        modelSelect.innerHTML = '<option value="">Error loading models</option>';
        console.error('Error loading Ollama models:', error);
    }
}

// Session management functions
async function saveSession() {
    try {
        // Get the active tab name
        const activeTab = document.querySelector('.main-tab.active');
        const activeTabName = activeTab ? activeTab.id.replace('Tab', '').replace(/([A-Z])/g, '-$1').toLowerCase() : 'epics';

        // Ask user for an optional session name
        let sessionName = window.prompt('Enter a name for this session (optional):');
        if (sessionName) {
            sessionName = sessionName.trim();
            if (sessionName.length === 0) sessionName = null;
        }

        const response = await fetchWithTimeout('http://localhost:8050/api/session/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                activeEpic: state.activeEpic,
                activeFeature: state.activeFeature,
                activeEpicId: state.activeEpicId,
                activeFeatureId: state.activeFeatureId,
                conversationHistory: state.conversationHistory,
                messages: getActiveMessagesDiv().innerHTML,
                activeTab: activeTabName,
                sessionName: sessionName || null
            })
        }, 30000); // 30 second timeout

        const data = await response.json();

        if (data.success) {
            const nameInfo = (sessionName && sessionName.length > 0) ? ` as "${sessionName}"` : '';
            addSystemMessage(`💾 ${data.message}${nameInfo}`);
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

            // Switch to the saved tab first
            if (session.activeTab) {
                // Convert the saved tab name to the proper format
                const tabMap = {
                    'strategic-initiatives': 'strategic-initiatives',
                    'strategicinitiatives': 'strategic-initiatives',
                    'pi-objectives': 'pi-objectives',
                    'piobjectives': 'pi-objectives',
                    'epics': 'epics',
                    'features': 'features',
                    'stories': 'stories',
                    'admin': 'admin'
                };
                const tabName = tabMap[session.activeTab] || 'epics';
                switchMainTab(tabName);
            }

            // Restore state
            state.activeEpic = session.activeEpic || null;
            state.activeFeature = session.activeFeature || null;
            state.activeEpicId = session.activeEpicId || null;
            state.activeFeatureId = session.activeFeatureId || null;
            state.conversationHistory = session.conversationHistory || [];

            // Restore messages
            getActiveMessagesDiv().innerHTML = session.messages || '';

            // Load templates if they exist
            if (data.epicTemplate) {
                // Display the epic template content
                const epicContent = data.epicTemplate.content;
                addSystemMessage(`📄 Loaded Epic Template: "${data.epicTemplate.name}" (ID: ${data.epicTemplate.id})`);

                // Optionally display template in a collapsible section
                const epicSection = `
                    <details style="margin: 10px 0; padding: 10px; background: #e3f2fd; border-radius: 5px;">
                        <summary style="cursor: pointer; font-weight: bold; color: #1976d2;">
                            📋 Epic Template: ${data.epicTemplate.name}
                        </summary>
                        <pre style="white-space: pre-wrap; margin-top: 10px; font-size: 0.9em;">${epicContent}</pre>
                    </details>
                `;
                getActiveMessagesDiv().innerHTML += epicSection;
            }

            if (data.featureTemplate) {
                // Display the feature template content
                const featureContent = data.featureTemplate.content;
                addSystemMessage(`📄 Loaded Feature Template: "${data.featureTemplate.name}" (ID: ${data.featureTemplate.id})`);

                // Optionally display template in a collapsible section
                const featureSection = `
                    <details style="margin: 10px 0; padding: 10px; background: #e8f5e9; border-radius: 5px;">
                        <summary style="cursor: pointer; font-weight: bold; color: #388e3c;">
                            📋 Feature Template: ${data.featureTemplate.name}
                        </summary>
                        <pre style="white-space: pre-wrap; margin-top: 10px; font-size: 0.9em;">${featureContent}</pre>
                    </details>
                `;
                getActiveMessagesDiv().innerHTML += featureSection;
            }

            // Update display
            updateActiveContextDisplay();

            // Scroll to bottom
            const messagesDiv = getActiveMessagesDiv();
            messagesDiv.scrollTop = messagesDiv.scrollHeight;

            addSystemMessage(`📂 ${data.message}`);

            // Don't auto-fill templates - let user choose which template to fill
            if (state.conversationHistory.length > 0) {
                addSystemMessage('💡 Conversation loaded. Use "Fill Epic Template" or "Fill Feature Template" buttons when ready.');
            }
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

// ============================================
// Template Storage Management
// ============================================

// Store the last filled template for saving
let lastFilledTemplate = null;
let lastFilledTemplateType = null;

// Updated fill template functions to store the result
async function fillEpicTemplate() {
    if (state.conversationHistory.length === 0) {
        addSystemMessage('⚠️ No conversation history available. Please have a discovery conversation first before filling the template.');
        return;
    }

    // Prevent multiple simultaneous calls
    if (state.isLoading) {
        addSystemMessage('⚠️ Please wait, a template is already being filled...');
        return;
    }

    state.isLoading = true;
    updateStatus('Filling Epic Template with conversation output...');
    document.getElementById('sendBtn').disabled = true;

    try {
        const response = await fetchWithTimeout('http://localhost:8050/api/fill-template', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                template_type: 'epic',
                conversationHistory: state.conversationHistory,
                activeEpic: state.activeEpic,
                activeFeature: state.activeFeature,
                model: state.model,
                temperature: state.temperature,
                provider: state.provider
            })
        }, 360000);

        const data = await response.json();

        if (data.success) {
            lastFilledTemplate = data.content;
            lastFilledTemplateType = 'epic';
            // Update state so name extraction works when saving
            state.activeEpic = data.content;
            updateActiveContextDisplay();
            addSystemMessage('📝 **Epic Template (Filled):**\n\n' + data.content);
            addSystemMessage('\n💡 *Tip: Click "💾 Save Template to DB" to store this template in the database for later use.*');
        } else {
            addSystemMessage(`❌ Error: ${data.message || 'Failed to fill template'}`);
        }
    } catch (error) {
        addSystemMessage(`❌ Error filling Epic template: ${error.message}`);
    } finally {
        state.isLoading = false;
        updateStatus('Ready');
        document.getElementById('sendBtn').disabled = false;
    }
}

async function fillFeatureTemplate() {
    if (state.conversationHistory.length === 0) {
        addSystemMessage('⚠️ No conversation history available. Please have a discovery conversation first before filling the template.');
        return;
    }

    // Prevent multiple simultaneous calls
    if (state.isLoading) {
        addSystemMessage('⚠️ Please wait, a template is already being filled...');
        return;
    }

    state.isLoading = true;
    updateStatus('Filling Feature Template with conversation output...');
    document.getElementById('sendBtn').disabled = true;

    try {
        const response = await fetchWithTimeout('http://localhost:8050/api/fill-template', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                template_type: 'feature',
                conversationHistory: state.conversationHistory,
                activeEpic: state.activeEpic,
                activeFeature: state.activeFeature,
                model: state.model,
                temperature: state.temperature,
                provider: state.provider
            })
        }, 360000);

        const data = await response.json();

        if (data.success) {
            lastFilledTemplate = data.content;
            lastFilledTemplateType = 'feature';
            // Update state so name extraction works when saving
            state.activeFeature = data.content;
            updateActiveContextDisplay();
            addSystemMessage('📝 **Feature Template (Filled):**\n\n' + data.content);
            addSystemMessage('\n💡 *Tip: Click "💾 Save Template to DB" to store this template in the database for later use.*');
        } else {
            addSystemMessage(`❌ Error: ${data.message || 'Failed to fill template'}`);
        }
    } catch (error) {
        addSystemMessage(`❌ Error filling Feature template: ${error.message}`);
    } finally {
        state.isLoading = false;
        updateStatus('Ready');
        document.getElementById('sendBtn').disabled = false;
    }
}

async function saveTemplateToDb() {
    if (!lastFilledTemplate || !lastFilledTemplateType) {
        addSystemMessage('⚠️ No filled template available. Please fill an Epic or Feature template first using the "📝 Fill Template" buttons.');
        return;
    }

    // Determine the suggested name with priority order:
    // Extract from template content directly
    let suggestedName = '';

    // Debug logging
    console.log('Template type:', lastFilledTemplateType);
    console.log('Template length:', lastFilledTemplate.length);

    // Try multiple patterns to find the name
    let nameMatch = null;

    // Pattern 1: Markdown format "1. **EPIC NAME**\nActual Name" 
    nameMatch = lastFilledTemplate.match(/1\.\s*\*\*(?:EPIC|FEATURE) NAME\*\*\s*\n([^\n]+?)(?:\n\n|\n2\.)/i);

    // Pattern 2: Plain format "1. EPIC NAME\nActual Name"
    if (!nameMatch) {
        nameMatch = lastFilledTemplate.match(/(?:^|\n)1\.\s*(?:EPIC|FEATURE) NAME\s*\n([A-Z][^\n]+?)(?:\n\n|\n2\.)/i);
    }

    // Pattern 3: After section header, skip any description, get the content line
    if (!nameMatch) {
        nameMatch = lastFilledTemplate.match(/(?:EPIC|FEATURE) NAME[^\n]*\n(?:[^\n]*\n)*?([A-Z][A-Za-z0-9\s&-]{5,100})(?:\n\n|\n2\.)/i);
    }

    // Pattern 4: Simple "EPIC NAME:" or "FEATURE NAME:" followed by name on same or next line
    if (!nameMatch) {
        nameMatch = lastFilledTemplate.match(/(?:EPIC|FEATURE) NAME:?\s*([A-Z][^\n]{5,100})(?:\n|$)/i);
    }

    // Extract and clean the name
    if (nameMatch && nameMatch[1]) {
        let extractedName = nameMatch[1].trim();
        console.log('Raw extracted name:', extractedName);

        // Clean up common markdown/formatting artifacts
        extractedName = extractedName.replace(/^\*+|\*+$/g, ''); // Remove asterisks
        extractedName = extractedName.replace(/^#+|#+$/g, ''); // Remove hashes
        extractedName = extractedName.replace(/^["']|["']$/g, ''); // Remove quotes
        extractedName = extractedName.trim();

        // Only use if it's not a placeholder and looks like a real name
        if (extractedName &&
            extractedName !== '[Fill in here]' &&
            !extractedName.startsWith('[') &&
            !extractedName.toLowerCase().includes('short, clear') &&
            !extractedName.toLowerCase().includes('describing') &&
            !extractedName.toLowerCase().includes('fill in') &&
            extractedName.length > 3 &&
            extractedName.length < 150) {
            suggestedName = extractedName;
        }
    }

    console.log('Final suggested name:', suggestedName);

    const templateName = prompt(`Enter a name for this ${lastFilledTemplateType} template:`, suggestedName);
    if (!templateName) {
        return;
    }

    const tags = prompt('Enter tags (comma-separated, optional):');
    const tagsList = tags ? tags.split(',').map(t => t.trim()).filter(t => t) : [];

    // If saving a feature and there's an active Epic, link them
    let epicId = null;
    if (lastFilledTemplateType === 'feature' && state.activeEpicId) {
        const linkToEpic = confirm(`Link this feature to the active Epic (ID: ${state.activeEpicId})?`);
        if (linkToEpic) {
            epicId = state.activeEpicId;
        }
    }

    state.isLoading = true;
    updateStatus(`Saving ${lastFilledTemplateType} template to database...`);

    try {
        const response = await fetch('http://localhost:8050/api/template/save', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                template_type: lastFilledTemplateType,
                name: templateName,
                content: lastFilledTemplate,
                epic_id: epicId,
                tags: tagsList,
                metadata: {
                    model: state.model,
                    provider: state.provider,
                    created_from: 'discovery_conversation'
                }
            })
        });

        const data = await response.json();

        if (data.success) {
            // Store the template ID in state for linking
            if (lastFilledTemplateType === 'epic') {
                state.activeEpicId = data.template_id;
                state.activeEpic = lastFilledTemplate; // Keep the epic content active
            } else if (lastFilledTemplateType === 'feature') {
                state.activeFeatureId = data.template_id;
                state.activeFeature = lastFilledTemplate;
            } else if (lastFilledTemplateType === 'story') {
                state.activeStoryId = data.template_id;
                state.activeStory = lastFilledTemplate;
            }

            // Update the sidebar to show the active template
            updateActiveContextDisplay();

            const epicLinkMsg = epicId ? `\n🔗 Linked to Epic ID: ${epicId}` : '';
            addSystemMessage(`✅ ${lastFilledTemplateType.charAt(0).toUpperCase() + lastFilledTemplateType.slice(1)} template saved successfully!\n\nTemplate ID: ${data.template_id}\nName: ${templateName}${epicLinkMsg}\n\n💡 *This ${lastFilledTemplateType} is now active and can be used for linking related templates.*`);
        } else {
            addSystemMessage(`❌ Error: ${data.message || 'Failed to save template'}`);
        }
    } catch (error) {
        addSystemMessage(`❌ Error saving template: ${error.message}`);
    } finally {
        state.isLoading = false;
        updateStatus('Ready');
    }
}

async function updateActiveTemplate(templateType) {
    const templateId = templateType === 'epic' ? state.activeEpicId : state.activeFeatureId;
    const templateContent = templateType === 'epic' ? state.activeEpic : state.activeFeature;

    if (!templateId || !templateContent) {
        addSystemMessage(`⚠️ No active ${templateType} template to update.`);
        return;
    }

    const confirmUpdate = confirm(`This will update the ${templateType} template incorporating refinements from the recent conversation. Continue?`);
    if (!confirmUpdate) {
        return;
    }

    state.isLoading = true;
    updateStatus(`Updating ${templateType} template with conversation refinements...`);

    try {
        // Create a targeted prompt to update the template preserving existing information
        const recentMessages = state.conversationHistory.slice(-10); // Last 10 messages for context
        const conversationText = recentMessages.map(msg =>
            `${msg.role.toUpperCase()}: ${msg.content}`
        ).join('\n\n');

        const updatePrompt = `You are updating an existing ${templateType.toUpperCase()} template based on recent conversation refinements.

IMPORTANT INSTRUCTIONS:
1. Keep the existing template structure and ALL field headers exactly as they are
2. PRESERVE the ${templateType} name - do NOT change it
3. Update ONLY the sections that were discussed in the recent conversation
4. Keep all other sections unchanged from the original template
5. If adding Gherkin scenarios, integrate them INTO the existing ACCEPTANCE CRITERIA section
6. Maintain all formatting and section numbers

ORIGINAL TEMPLATE:
${templateContent}

RECENT CONVERSATION (refinement discussion):
${conversationText}

Please provide the COMPLETE updated template with refinements integrated while preserving all unchanged sections.`;

        // Call LLM directly through chat endpoint
        const response = await fetchWithTimeout('http://localhost:8050/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: updatePrompt,
                activeEpic: state.activeEpic,
                activeFeature: state.activeFeature,
                model: state.model,
                temperature: 0.3, // Lower temperature for more consistent updates
                provider: state.provider
            })
        }, 180000);

        const chatData = await response.json();

        if (!chatData.response) {
            addSystemMessage('❌ Error: No response from AI');
            return;
        }

        const updatedContent = chatData.response;

        // Extract name from updated content
        let nameMatch = updatedContent.match(/(?:EPIC|FEATURE) NAME:\s*\n\s*(.+?)(?:\n|$)/i);
        if (!nameMatch) {
            nameMatch = updatedContent.match(/(?:\d+\.\s*)?(?:EPIC NAME|FEATURE NAME)\s*\n.*?\n\s*(.+?)(?:\n|$)/i);
        }
        const templateName = nameMatch && nameMatch[1] && nameMatch[1].trim() !== '[Fill in here]'
            ? nameMatch[1].trim()
            : null;

        if (!templateName) {
            addSystemMessage('⚠️ Could not extract template name from updated content.');
            return;
        }

        // Update in database
        const updateData = {
            template_id: templateId,
            template_type: templateType,
            name: templateName,
            content: updatedContent,
            metadata: {
                model: state.model,
                provider: state.provider,
                updated_from: 'conversation_refinement'
            }
        };

        if (templateType === 'feature' && state.activeEpicId) {
            updateData.epic_id = state.activeEpicId;
        }

        const updateResponse = await fetch('http://localhost:8050/api/template/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(updateData)
        });

        const data = await updateResponse.json();

        if (data.success) {
            // Update local state
            if (templateType === 'epic') {
                state.activeEpic = updatedContent;
            } else {
                state.activeFeature = updatedContent;
            }
            lastFilledTemplate = updatedContent;
            lastFilledTemplateType = templateType;

            addSystemMessage(`✅ ${templateType.charAt(0).toUpperCase() + templateType.slice(1)} template updated successfully!\n\nTemplate ID: ${templateId}\nName: ${templateName}`);

            // Reload to show updated content
            await loadTemplateById(templateId, templateType);
        } else {
            addSystemMessage(`❌ Error: ${data.message || 'Failed to update template'}`);
        }
    } catch (error) {
        addSystemMessage(`❌ Error updating template: ${error.message}`);
    } finally {
        state.isLoading = false;
        updateStatus('Ready');
    }
}

async function saveAllProposedFeatures() {
    // Check if there's an active Epic
    if (!state.activeEpicId) {
        addSystemMessage('⚠️ No active Epic loaded. Please load an Epic template first before saving features.');
        return;
    }

    const userConfirm = confirm('This will extract all feature proposals from the conversation and save them as templates linked to the active Epic. Continue?');
    if (!userConfirm) {
        return;
    }

    state.isLoading = true;
    updateStatus('Extracting and saving feature proposals...');

    try {
        // Ask the backend to extract all feature proposals and fill templates for each
        const response = await fetchWithTimeout('http://localhost:8050/api/extract-features', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                activeEpic: state.activeEpic,
                conversationHistory: state.conversationHistory,
                model: state.model,
                temperature: state.temperature,
                provider: state.provider
            })
        }, 180000); // 3 minute timeout

        const data = await response.json();

        if (data.success && data.features && data.features.length > 0) {
            addSystemMessage(`✅ Found ${data.features.length} feature proposal(s). Saving to database...`);

            // Save each feature to the database
            let savedCount = 0;
            const tags = prompt('Enter tags for these features (comma-separated, optional):');
            const tagsList = tags ? tags.split(',').map(t => t.trim()).filter(t => t) : [];

            for (const featureContent of data.features) {
                // Extract feature name - handle multiple formats
                console.log('=== Feature Content Preview ===');
                console.log(featureContent.substring(0, 300));
                console.log('==============================');

                // Try format 1: "1. FEATURE NAME" section specifically
                let nameMatch = featureContent.match(/1\.\s*FEATURE NAME\s*\n[^\n]*\n\s*(.+?)(?:\n|$)/i);

                // Try format 2: "FEATURE NAME:" followed by the name on next line
                if (!nameMatch) {
                    nameMatch = featureContent.match(/^FEATURE NAME:\s*\n\s*(.+?)(?:\n|$)/im);
                }

                console.log('Name match result:', nameMatch);

                const featureName = nameMatch && nameMatch[1] && nameMatch[1].trim() !== '[Fill in here]'
                    ? nameMatch[1].trim()
                    : `Feature ${savedCount + 1}`;

                console.log('Extracted feature name:', featureName);

                // Save feature
                const saveResponse = await fetch('http://localhost:8050/api/template/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        template_type: 'feature',
                        name: featureName,
                        content: featureContent,
                        epic_id: state.activeEpicId,
                        tags: tagsList,
                        metadata: {
                            model: state.model,
                            provider: state.provider,
                            created_from: 'bulk_feature_save'
                        }
                    })
                });

                const saveData = await saveResponse.json();
                if (saveData.success) {
                    savedCount++;
                }
            }

            addSystemMessage(`✅ Successfully saved ${savedCount} feature(s) linked to Epic ID: ${state.activeEpicId}\n\n💡 *Tip: View them in "📋 Browse Templates" under Features tab.*`);
        } else if (data.features && data.features.length === 0) {
            addSystemMessage('⚠️ No feature proposals found in the conversation. Try asking the coach to propose features first.');
        } else {
            addSystemMessage(`❌ Error: ${data.message || 'Failed to extract features'}`);
        }
    } catch (error) {
        addSystemMessage(`❌ Error: ${error.message}`);
    } finally {
        state.isLoading = false;
        updateStatus('Ready');
    }
}

async function loadTemplateFromDb() {
    const templateType = prompt('Enter template type (epic or feature):');
    if (!templateType || !['epic', 'feature'].includes(templateType.toLowerCase())) {
        addSystemMessage('⚠️ Invalid template type. Please enter "epic" or "feature".');
        return;
    }

    const templateId = prompt('Enter template ID to load:');
    if (!templateId) {
        return;
    }

    state.isLoading = true;
    updateStatus('Loading template from database...');

    try {
        const response = await fetch('http://localhost:8050/api/template/load', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                template_id: parseInt(templateId),
                template_type: templateType.toLowerCase()
            })
        });

        const data = await response.json();

        if (data.success) {
            const template = data.template;
            lastFilledTemplate = template.content;
            lastFilledTemplateType = templateType.toLowerCase();

            addSystemMessage(`📂 **Loaded ${templateType.charAt(0).toUpperCase() + templateType.slice(1)} Template**\n\n**Name:** ${template.name}\n**Created:** ${new Date(template.created_at).toLocaleString()}\n**Updated:** ${new Date(template.updated_at).toLocaleString()}\n**Tags:** ${template.tags.join(', ') || 'None'}\n\n**Content:**\n${template.content}`);
            addSystemMessage('\n💡 *Tip: You can now continue editing this template in the conversation or export it as JSON.*');
        } else {
            addSystemMessage(`❌ Error: ${data.message || 'Failed to load template'}`);
        }
    } catch (error) {
        addSystemMessage(`❌ Error loading template: ${error.message}`);
    } finally {
        state.isLoading = false;
        updateStatus('Ready');
    }
}

async function listTemplates() {
    openTemplateBrowser();
}

let currentBrowserType = 'epic';
let selectedTemplates = new Set();

async function openTemplateBrowser() {
    const modal = document.getElementById('templateBrowserModal');
    modal.style.display = 'block';
    currentBrowserType = 'epic';
    await loadTemplateBrowserContent('epic');
}

function closeTemplateBrowser() {
    const modal = document.getElementById('templateBrowserModal');
    modal.style.display = 'none';
}

async function loadTemplateBrowserContent(templateType) {
    currentBrowserType = templateType;
    const content = document.getElementById('templateBrowserContent');

    selectedTemplates.clear();

    content.innerHTML = `
        <div class="template-browser-tabs">
            <button class="template-browser-tab ${templateType === 'epic' ? 'active' : ''}" onclick="loadTemplateBrowserContent('epic')">📝 Epics</button>
            <button class="template-browser-tab ${templateType === 'feature' ? 'active' : ''}" onclick="loadTemplateBrowserContent('feature')">✨ Features</button>
            <button class="template-browser-tab ${templateType === 'story' ? 'active' : ''}" onclick="loadTemplateBrowserContent('story')">📖 Stories</button>
        </div>
        <div style="display: flex; gap: 10px; margin-bottom: 15px; padding: 10px; background: #f9f9f9; border-radius: 6px; align-items: center;">
            <input type="checkbox" id="selectAllTemplates" onchange="toggleSelectAll()" style="cursor: pointer;">
            <label for="selectAllTemplates" style="cursor: pointer; font-size: 13px; user-select: none;">Select All</label>
            <button class="template-action-btn" onclick="exportSelectedTemplates()" style="margin-left: auto; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white;" id="bulkExportBtn" disabled>
                📥 Export Selected (<span id="selectedExportCount">0</span>)
            </button>
            <button class="template-action-btn delete" onclick="deleteSelectedTemplates()" id="bulkDeleteBtn" disabled>
                🗑️ Delete Selected (<span id="selectedCount">0</span>)
            </button>
        </div>
        <div id="templateList">Loading...</div>
    `;

    try {
        const response = await fetch(`http://localhost:8050/api/template/list/${templateType}`);
        const data = await response.json();

        const listEl = document.getElementById('templateList');

        if (data.success) {
            if (data.templates.length === 0) {
                listEl.innerHTML = `<p style="text-align: center; color: #999; padding: 40px;">No ${templateType} templates found.<br><small>Fill and save a template to see it here.</small></p>`;
            } else {
                listEl.innerHTML = data.templates.map(t => {
                    const created = new Date(t.created_at).toLocaleString();
                    const updated = new Date(t.updated_at).toLocaleString();
                    const tags = t.tags && t.tags.length > 0
                        ? t.tags.map(tag => `<span class="template-tag">${tag}</span>`).join('')
                        : '<span style="color: #999; font-size: 11px;">No tags</span>';

                    // Show epic linkage for features, or feature linkage for stories
                    const epicLink = templateType === 'feature' && t.epic_id
                        ? `<div style="margin-top: 5px; font-size: 11px; color: #667eea;">🔗 Linked to Epic ID: ${t.epic_id}</div>`
                        : templateType === 'story' && t.feature_id
                            ? `<div style="margin-top: 5px; font-size: 11px; color: #667eea;">🔗 Linked to Feature ID: ${t.feature_id}</div>`
                            : '';

                    return `
                        <div class="template-card" onclick="event.stopPropagation()">
                            <div class="template-card-header">
                                <input type="checkbox" class="template-checkbox" data-id="${t.id}" onchange="toggleTemplateSelection(${t.id})" style="margin-right: 10px; cursor: pointer;">
                                <div class="template-card-title">${t.name}</div>
                                <div class="template-card-id">ID: ${t.id}</div>
                            </div>
                            <div class="template-card-meta">
                                📅 Created: ${created}<br>
                                🔄 Updated: ${updated}
                                ${epicLink}
                            </div>
                            <div class="template-card-tags">
                                ${tags}
                            </div>
                            <div class="template-actions">
                                <button class="template-action-btn" onclick="loadTemplateById(${t.id}, '${templateType}')">
                                    📂 Load
                                </button>
                                <button class="template-action-btn" onclick="exportTemplateById(${t.id}, '${templateType}')">
                                    📤 Export
                                </button>
                                <button class="template-action-btn delete" onclick="deleteTemplateById(${t.id}, '${templateType}')">
                                    🗑️ Delete
                                </button>
                            </div>
                        </div>
                    `;
                }).join('');
            }
        } else {
            listEl.innerHTML = `<p style="text-align: center; color: #e74c3c; padding: 20px;">Error loading templates: ${data.message}</p>`;
        }
    } catch (error) {
        document.getElementById('templateList').innerHTML = `<p style="text-align: center; color: #e74c3c; padding: 20px;">Error: ${error.message}</p>`;
    }
}

async function loadTemplateById(id, type) {
    closeTemplateBrowser();

    state.isLoading = true;
    updateStatus('Loading template...');

    try {
        const response = await fetch('http://localhost:8050/api/template/load', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                template_id: id,
                template_type: type
            })
        });

        const data = await response.json();

        if (data.success) {
            const template = data.template;
            lastFilledTemplate = template.content;
            lastFilledTemplateType = type;

            // Set as active Epic, Feature, or Story in state
            if (type === 'epic') {
                state.activeEpic = template.content;
                state.activeEpicId = id; // Store Epic ID for linking features
            } else if (type === 'feature') {
                state.activeFeature = template.content;
                state.activeFeatureId = id; // Store Feature ID for updates/linking stories
            } else if (type === 'story') {
                state.activeStory = template.content;
                state.activeStoryId = id; // Store Story ID for updates
            }

            // Update the sidebar display
            updateActiveContextDisplay();

            // Display the loaded template
            addSystemMessage(`📂 **Loaded ${type.charAt(0).toUpperCase() + type.slice(1)} Template: ${template.name}**\n\n**Created:** ${new Date(template.created_at).toLocaleString()}\n**Updated:** ${new Date(template.updated_at).toLocaleString()}\n**Tags:** ${template.tags.join(', ') || 'None'}\n\n**Content:**\n${template.content}`);

            // Notify the backend and get contextual response
            updateStatus('Activating template context...');
            const contextResponse = await fetchWithTimeout('http://localhost:8050/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: `I have loaded a ${type} template named "${template.name}". This is now my active ${type}. Please acknowledge this and ask me what I'd like to work on next.`,
                    activeEpic: state.activeEpic,
                    activeFeature: state.activeFeature,
                    model: state.model,
                    temperature: state.temperature,
                    provider: state.provider
                })
            }, 60000);

            const contextData = await contextResponse.json();
            if (contextData.success) {
                addAgentMessage(contextData.response);
                state.conversationHistory.push({ role: 'agent', content: contextData.response });
            }
        } else {
            addSystemMessage(`❌ Error: ${data.message || 'Failed to load template'}`);
        }
    } catch (error) {
        addSystemMessage(`❌ Error loading template: ${error.message}`);
    } finally {
        state.isLoading = false;
        updateStatus('Ready');
    }
}

async function exportTemplateById(id, type) {
    try {
        const response = await fetch('http://localhost:8050/api/template/export', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                template_type: type,
                template_id: id,
                export_all: false
            })
        });

        const data = await response.json();

        if (data.success) {
            const jsonStr = JSON.stringify(data.data, null, 2);
            const blob = new Blob([jsonStr], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${type}_template_${id}_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            addSystemMessage(`✅ Exported ${type} template (ID: ${id}) as JSON file.`);
        } else {
            addSystemMessage(`❌ Error exporting template: ${data.message}`);
        }
    } catch (error) {
        addSystemMessage(`❌ Error: ${error.message}`);
    }
}

function toggleTemplateSelection(id) {
    if (selectedTemplates.has(id)) {
        selectedTemplates.delete(id);
    } else {
        selectedTemplates.add(id);
    }
    updateBulkDeleteButton();
}

function toggleSelectAll() {
    const selectAllCheckbox = document.getElementById('selectAllTemplates');
    const checkboxes = document.querySelectorAll('.template-checkbox');

    if (selectAllCheckbox.checked) {
        checkboxes.forEach(cb => {
            const id = parseInt(cb.dataset.id);
            selectedTemplates.add(id);
            cb.checked = true;
        });
    } else {
        selectedTemplates.clear();
        checkboxes.forEach(cb => cb.checked = false);
    }
    updateBulkDeleteButton();
}

function updateBulkDeleteButton() {
    const bulkDeleteBtn = document.getElementById('bulkDeleteBtn');
    const bulkExportBtn = document.getElementById('bulkExportBtn');
    const selectedCountSpan = document.getElementById('selectedCount');
    const selectedExportCountSpan = document.getElementById('selectedExportCount');

    if (bulkDeleteBtn && selectedCountSpan) {
        selectedCountSpan.textContent = selectedTemplates.size;
        bulkDeleteBtn.disabled = selectedTemplates.size === 0;
    }

    if (bulkExportBtn && selectedExportCountSpan) {
        selectedExportCountSpan.textContent = selectedTemplates.size;
        bulkExportBtn.disabled = selectedTemplates.size === 0;
    }
}

async function deleteSelectedTemplates() {
    if (selectedTemplates.size === 0) {
        return;
    }

    const confirmMsg = `Are you sure you want to delete ${selectedTemplates.size} ${currentBrowserType} template(s)?`;
    if (!confirm(confirmMsg)) {
        return;
    }

    state.isLoading = true;
    updateStatus(`Deleting ${selectedTemplates.size} template(s)...`);

    let successCount = 0;
    let failCount = 0;

    for (const id of selectedTemplates) {
        try {
            const response = await fetch('http://localhost:8050/api/template/delete', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    template_id: id,
                    template_type: currentBrowserType
                })
            });

            const data = await response.json();
            if (data.success) {
                successCount++;
            } else {
                failCount++;
            }
        } catch (error) {
            failCount++;
        }
    }

    selectedTemplates.clear();

    if (successCount > 0) {
        addSystemMessage(`✅ Successfully deleted ${successCount} template(s).${failCount > 0 ? ` Failed: ${failCount}` : ''}`);
    } else {
        addSystemMessage(`❌ Failed to delete templates.`);
    }

    state.isLoading = false;
    updateStatus('Ready');

    await loadTemplateBrowserContent(currentBrowserType);
}

async function exportSelectedTemplates() {
    if (selectedTemplates.size === 0) {
        return;
    }

    state.isLoading = true;
    updateStatus(`Exporting ${selectedTemplates.size} template(s)...`);

    try {
        const exportData = [];

        for (const id of selectedTemplates) {
            const response = await fetch('http://localhost:8050/api/template/export', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    template_id: id,
                    template_type: currentBrowserType,
                    export_all: false
                })
            });

            const data = await response.json();
            if (data.success) {
                exportData.push(data.data);
            }
        }

        if (exportData.length > 0) {
            // Create JSON blob and download
            const jsonStr = JSON.stringify(exportData, null, 2);
            const blob = new Blob([jsonStr], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${currentBrowserType}_templates_${new Date().toISOString().split('T')[0]}.json`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            addSystemMessage(`✅ Successfully exported ${exportData.length} ${currentBrowserType} template(s) as JSON.`);
        } else {
            addSystemMessage('❌ No templates were exported.');
        }
    } catch (error) {
        addSystemMessage(`❌ Error exporting templates: ${error.message}`);
    } finally {
        state.isLoading = false;
        updateStatus('Ready');
    }
}

async function deleteTemplateById(id, type) {
    if (!confirm(`Are you sure you want to delete this ${type} template (ID: ${id})?`)) {
        return;
    }

    try {
        const response = await fetch('http://localhost:8050/api/template/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                template_id: id,
                template_type: type
            })
        });

        const data = await response.json();

        if (data.success) {
            addSystemMessage(`✅ Template deleted successfully.`);
            await loadTemplateBrowserContent(currentBrowserType);
        } else {
            addSystemMessage(`❌ Error: ${data.message}`);
        }
    } catch (error) {
        addSystemMessage(`❌ Error: ${error.message}`);
    }
}

async function exportTemplateAsJson() {
    const exportAll = confirm('Export all templates? (OK = All, Cancel = Single template)');

    let templateType, templateId;

    if (exportAll) {
        templateType = prompt('Export all templates of type (epic or feature):');
        if (!templateType || !['epic', 'feature'].includes(templateType.toLowerCase())) {
            addSystemMessage('⚠️ Invalid template type. Please enter "epic" or "feature".');
            return;
        }
    } else {
        templateType = prompt('Template type to export (epic or feature):');
        if (!templateType || !['epic', 'feature'].includes(templateType.toLowerCase())) {
            addSystemMessage('⚠️ Invalid template type. Please enter "epic" or "feature".');
            return;
        }

        templateId = prompt('Enter template ID to export:');
        if (!templateId) {
            return;
        }
    }

    state.isLoading = true;
    updateStatus('Exporting template(s) as JSON...');

    try {
        const response = await fetch('http://localhost:8050/api/template/export', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                template_type: templateType.toLowerCase(),
                template_id: templateId ? parseInt(templateId) : null,
                export_all: exportAll
            })
        });

        const data = await response.json();

        if (data.success) {
            // Create downloadable JSON file
            const jsonStr = JSON.stringify(data.data, null, 2);
            const blob = new Blob([jsonStr], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;

            if (exportAll) {
                a.download = `${templateType}_templates_export_${new Date().toISOString().split('T')[0]}.json`;
            } else {
                a.download = `${templateType}_template_${templateId}_${new Date().toISOString().split('T')[0]}.json`;
            }

            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);

            if (exportAll) {
                addSystemMessage(`✅ Exported ${data.count} ${templateType} template(s) as JSON file.`);
            } else {
                addSystemMessage(`✅ Exported ${templateType} template (ID: ${templateId}) as JSON file.`);
            }
        } else {
            addSystemMessage(`❌ Error: ${data.message || 'Failed to export template'}`);
        }
    } catch (error) {
        addSystemMessage(`❌ Error exporting template: ${error.message}`);
    } finally {
        state.isLoading = false;
        updateStatus('Ready');
    }
}

// Switch between Epic and Feature action tabs
function switchActionTab(type) {
    // Update tab styling
    document.getElementById('epicTab').classList.remove('active');
    document.getElementById('featureTab').classList.remove('active');
    document.getElementById('storyTab').classList.remove('active');

    if (type === 'epic') {
        document.getElementById('epicTab').classList.add('active');
        document.getElementById('epicActions').style.display = 'flex';
        document.getElementById('featureActions').style.display = 'none';
        document.getElementById('storyActions').style.display = 'none';
    } else if (type === 'feature') {
        document.getElementById('featureTab').classList.add('active');
        document.getElementById('featureActions').style.display = 'flex';
        document.getElementById('epicActions').style.display = 'none';
        document.getElementById('storyActions').style.display = 'none';
    } else if (type === 'story') {
        document.getElementById('storyTab').classList.add('active');
        document.getElementById('storyActions').style.display = 'flex';
        document.getElementById('epicActions').style.display = 'none';
        document.getElementById('featureActions').style.display = 'none';
    }
}

// Main tab switching function
function switchMainTab(tabName) {
    // Hide all tab contents
    const tabContents = ['strategicInitiativesContent', 'piObjectivesContent', 'epicsContent', 'featuresContent', 'storiesContent', 'adminContent'];
    tabContents.forEach(id => {
        const element = document.getElementById(id);
        if (element) element.style.display = 'none';
    });

    // Remove active class from all tabs
    const tabs = ['strategicInitiativesTab', 'piObjectivesTab', 'epicsTab', 'featuresTab', 'storiesTab', 'adminTab'];
    tabs.forEach(id => {
        const element = document.getElementById(id);
        if (element) element.classList.remove('active');
    });

    // Hide all action sections in sidebar
    const actionSections = ['strategicInitiativeActions', 'epicActions', 'featureActions', 'storyActions'];
    actionSections.forEach(id => {
        const element = document.getElementById(id);
        if (element) element.style.display = 'none';
    });

    // Show selected tab and activate it
    const contentMap = {
        'strategic-initiatives': 'strategicInitiativesContent',
        'pi-objectives': 'piObjectivesContent',
        'epics': 'epicsContent',
        'features': 'featuresContent',
        'stories': 'storiesContent',
        'admin': 'adminContent'
    };

    const tabMap = {
        'strategic-initiatives': 'strategicInitiativesTab',
        'pi-objectives': 'piObjectivesTab',
        'epics': 'epicsTab',
        'features': 'featuresTab',
        'stories': 'storiesTab',
        'admin': 'adminTab'
    };

    // Map tabs to their corresponding action sections
    const actionMap = {
        'strategic-initiatives': 'strategicInitiativeActions',
        'epics': 'epicActions',
        'features': 'featureActions',
        'stories': 'storyActions'
    };

    const contentId = contentMap[tabName];
    const tabId = tabMap[tabName];
    const actionId = actionMap[tabName];

    if (contentId) {
        const content = document.getElementById(contentId);
        if (content) content.style.display = 'flex';
    }

    if (tabId) {
        const tab = document.getElementById(tabId);
        if (tab) tab.classList.add('active');
    }

    // Show corresponding action section in sidebar
    if (actionId) {
        const action = document.getElementById(actionId);
        if (action) action.style.display = 'flex';
    }
}

// ============================================
// Template Editor Functions
// ============================================

function openTemplateEditor(templateType) {
    const content = templateType === 'epic' ? state.activeEpic :
        templateType === 'feature' ? state.activeFeature :
            templateType === 'story' ? state.activeStory : null;

    if (!content) {
        addSystemMessage(`⚠️ No active ${templateType} to edit. Please load or create a ${templateType} first.`);
        return;
    }

    const modal = document.getElementById('templateEditorModal');
    const title = document.getElementById('editorModalTitle');
    const editorContent = document.getElementById('templateEditorContent');

    title.textContent = `✏️ Edit ${templateType.charAt(0).toUpperCase() + templateType.slice(1)} Template`;

    // Parse the template content into fields
    const fields = parseTemplateContent(content, templateType);

    console.log(`Parsed ${fields.length} fields from ${templateType} template`);

    if (fields.length === 0) {
        editorContent.innerHTML = `<p style="color: #d32f2f;">⚠️ Unable to parse template fields. The template format may be invalid.</p>
        <p style="font-size: 12px; color: #666;">Template length: ${content.length} characters</p>`;
        modal.style.display = 'flex';
        return;
    }

    // Build the form
    let formHtml = `<form id="templateEditForm" style="display: flex; flex-direction: column; gap: 20px;">`;

    fields.forEach((field, index) => {
        const isLargeField = field.value.length > 100 || field.value.includes('\n');
        formHtml += `
            <div style="display: flex; flex-direction: column; gap: 5px;">
                <label style="font-weight: bold; color: #333; font-size: 14px;">
                    ${field.number ? field.number + '. ' : ''}${field.label}
                </label>
                ${isLargeField ?
                `<textarea id="field_${index}" rows="6" style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-family: inherit; font-size: 13px; resize: vertical;">${escapeHtml(field.value)}</textarea>` :
                `<input type="text" id="field_${index}" value="${escapeHtml(field.value)}" style="width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-size: 13px;">`
            }
            </div>
        `;
    });

    formHtml += `</form>`;
    formHtml += `<input type="hidden" id="editingTemplateType" value="${templateType}">`;
    formHtml += `<input type="hidden" id="originalFieldsCount" value="${fields.length}">`;

    editorContent.innerHTML = formHtml;
    modal.style.display = 'flex';
}

function closeTemplateEditor() {
    document.getElementById('templateEditorModal').style.display = 'none';
}

function parseTemplateContent(content, templateType) {
    const fields = [];

    // Strip LLM preamble (text before actual template)
    // Look for common separators or the first numbered field
    let cleanContent = content;
    const separatorMatch = content.match(/\n-{3,}\n/); // Find --- separator
    if (separatorMatch) {
        cleanContent = content.substring(separatorMatch.index + separatorMatch[0].length);
        console.log('Stripped preamble at separator, remaining length:', cleanContent.length);
    } else {
        // Try to find first numbered field and start from there
        const firstFieldMatch = content.match(/\n\s*1\.\s+[A-Z]/);
        if (firstFieldMatch) {
            cleanContent = content.substring(firstFieldMatch.index + 1);
            console.log('Stripped preamble at first field, remaining length:', cleanContent.length);
        }
    }

    const lines = cleanContent.split('\n');

    // Define field patterns for Epic and Feature (handle both plain and markdown formats)
    const epicFields = [
        { number: '1', label: 'EPIC NAME', pattern: /^1\.\s*\*{0,2}EPIC NAME\*{0,2}/i },
        { number: '2', label: 'EPIC OWNER', pattern: /^2\.\s*\*{0,2}EPIC OWNER\*{0,2}/i },
        { number: '3', label: 'KEY STAKEHOLDERS', pattern: /^3\.\s*\*{0,2}KEY STAKEHOLDERS\*{0,2}/i },
        { number: '4', label: 'BUSINESS CONTEXT / BACKGROUND', pattern: /^4\.\s*\*{0,2}BUSINESS CONTEXT/i },
        { number: '5', label: 'PROBLEM / OPPORTUNITY', pattern: /^(?:4|5)\.\s*\*{0,2}PROBLEM/i },
        { number: '6', label: 'TARGET CUSTOMERS / USERS', pattern: /^(?:5|6)\.\s*\*{0,2}TARGET CUSTOMERS/i },
        { number: '7', label: 'EPIC HYPOTHESIS STATEMENT', pattern: /^(?:6|7)\.\s*\*{0,2}EPIC HYPOTHESIS/i },
        { number: '8', label: 'DESIRED BUSINESS OUTCOMES', pattern: /^(?:7|8)\.\s*\*{0,2}DESIRED BUSINESS/i },
        { number: '9', label: 'LEADING INDICATORS', pattern: /^(?:8|9)\.\s*\*{0,2}LEADING INDICATORS/i },
        { number: '10', label: 'MVP', pattern: /^(?:9|10)\.\s*\*{0,2}MVP/i },
        { number: '11', label: 'FORECASTED FULL SCOPE', pattern: /^(?:10|11)\.\s*\*{0,2}FORECASTED FULL SCOPE/i },
        { number: '12', label: 'FORECASTED COSTS', pattern: /^(?:11|12)\.\s*\*{0,2}FORECASTED COSTS/i },
        { number: '13', label: 'SCOPE / OUT OF SCOPE', pattern: /^(?:12|13)\.\s*\*{0,2}SCOPE/i },
        { number: '14', label: 'BUSINESS IMPACT & VALUE', pattern: /^(?:13|14)\.\s*\*{0,2}BUSINESS IMPACT/i },
        { number: '15', label: 'SOLUTION ANALYSIS', pattern: /^(?:14|15)\.\s*\*{0,2}SOLUTION ANALYSIS/i },
        { number: '16', label: 'DEVELOPMENT STRATEGY', pattern: /^(?:15|16)\.\s*\*{0,2}DEVELOPMENT STRATEGY/i },
        { number: '17', label: 'RISKS, ASSUMPTIONS & CONSTRAINTS', pattern: /^(?:16|17)\.\s*\*{0,2}RISKS/i },
        { number: '18', label: 'WSJF', pattern: /^(?:17|18)\.\s*\*{0,2}WSJF/i },
        { number: '19', label: 'METRICS & MEASUREMENT PLAN', pattern: /^(?:18|19)\.\s*\*{0,2}METRICS/i },
        { number: '20', label: 'GO / NO-GO RECOMMENDATION', pattern: /^(?:19|20)\.\s*\*{0,2}GO.*NO-GO/i }
    ];

    const featureFields = [
        { number: '1', label: 'FEATURE NAME', pattern: /^1\.\s*\*{0,2}FEATURE NAME\*{0,2}/i },
        { number: '2', label: 'FEATURE TYPE', pattern: /^2\.\s*\*{0,2}FEATURE TYPE\*{0,2}/i },
        { number: '3', label: 'DESCRIPTION', pattern: /^3\.\s*\*{0,2}DESCRIPTION\*{0,2}/i },
        { number: '4', label: 'BENEFIT HYPOTHESIS', pattern: /^4\.\s*\*{0,2}BENEFIT HYPOTHESIS\*{0,2}/i },
        { number: '5', label: 'ACCEPTANCE CRITERIA', pattern: /^5\.\s*\*{0,2}ACCEPTANCE CRITERIA\*{0,2}/i },
        { number: '6', label: 'NON-FUNCTIONAL REQUIREMENTS', pattern: /^6\.\s*\*{0,2}NON-FUNCTIONAL/i },
        { number: '7', label: 'DEPENDENCIES', pattern: /^7\.\s*\*{0,2}DEPENDENCIES\*{0,2}/i },
        { number: '8', label: 'ASSUMPTIONS & CONSTRAINTS', pattern: /^8\.\s*\*{0,2}ASSUMPTIONS/i },
        { number: '9', label: 'WSJF', pattern: /^9\.\s*\*{0,2}WSJF\*{0,2}/i },
        { number: '10', label: 'IMPLEMENTATION NOTES', pattern: /^10\.\s*\*{0,2}IMPLEMENTATION/i }
    ];

    const fieldDefinitions = templateType === 'epic' ? epicFields : featureFields;

    console.log(`Parsing ${templateType} template with ${fieldDefinitions.length} expected fields`);
    console.log('Template preview:', cleanContent.substring(0, 300));
    console.log('First 10 lines after cleaning:');
    for (let i = 0; i < Math.min(10, lines.length); i++) {
        console.log(`  Line ${i}: "${lines[i].substring(0, 60)}"`);
    }

    // Try smart extraction - look for numbered sections
    const numberedSections = [];
    for (let i = 0; i < lines.length; i++) {
        const match = lines[i].match(/^(\d+)\.\s*\*{0,2}(.+?)\*{0,2}\s*$/);
        if (match) {
            numberedSections.push({ line: i, number: match[1], label: match[2].trim() });
        }
    }

    console.log(`Found ${numberedSections.length} numbered sections`);

    // If no numbered sections, try label-only format (e.g., "FEATURE NAME:")
    if (numberedSections.length === 0) {
        console.log('Trying label-only format (e.g., "FEATURE NAME:")');

        // Sub-labels to ignore (common headings within sections)
        const subLabels = ['ASSUMPTIONS', 'CONSTRAINTS', 'BUSINESS / USER VALUE', 'TIME CRITICALITY',
            'RISK REDUCTION / OPPORTUNITY ENABLEMENT', 'JOB SIZE', 'CALCULATED WSJF'];

        // Find all lines that look like labels (ALL CAPS followed by :)
        const labelSections = [];
        for (let i = 0; i < lines.length; i++) {
            const labelMatch = lines[i].match(/^([A-Z][A-Z\s\/&-]+):\s*$/);
            if (labelMatch) {
                const label = labelMatch[1].trim();

                // Skip if it's a known sub-label
                if (subLabels.includes(label)) {
                    console.log(`Skipping sub-label at line ${i}: "${label}"`);
                    continue;
                }

                labelSections.push({ line: i, label: label });
                console.log(`Found label at line ${i}: "${label}"`);
            }
        }

        if (labelSections.length > 0) {
            // Extract content for each label
            for (let i = 0; i < labelSections.length; i++) {
                const section = labelSections[i];
                const nextSection = labelSections[i + 1];

                const startIdx = section.line;
                const endIdx = nextSection ? nextSection.line : lines.length;

                // Extract content between this label and the next
                let valueLines = [];
                for (let j = startIdx + 1; j < endIdx; j++) {
                    const line = lines[j];
                    // Skip empty lines at the start
                    if (line.trim() === '' && valueLines.length === 0) continue;
                    valueLines.push(line);
                }

                // Remove trailing empty lines
                while (valueLines.length > 0 && valueLines[valueLines.length - 1].trim() === '') {
                    valueLines.pop();
                }

                const value = valueLines.join('\n').trim();
                fields.push({
                    number: String(i + 1),
                    label: section.label,
                    value: value || '[Not filled]'
                });
            }

            console.log(`Extracted ${fields.length} fields using label-only format`);
            return fields;
        }
    }

    // If we found numbered sections, use them
    if (numberedSections.length > 0) {
        for (let i = 0; i < numberedSections.length; i++) {
            const section = numberedSections[i];
            const nextSection = numberedSections[i + 1];

            const startIdx = section.line;
            const endIdx = nextSection ? nextSection.line : lines.length;

            // Extract content between this section and the next
            let valueLines = [];
            for (let j = startIdx + 1; j < endIdx; j++) {
                const line = lines[j].trim();
                if (line && !line.startsWith('[') && !line.toLowerCase().includes('fill in here')) {
                    valueLines.push(lines[j]);
                } else if (valueLines.length > 0) {
                    // Keep collecting after we've found content
                    valueLines.push(lines[j]);
                }
            }

            const value = valueLines.join('\n').trim();
            fields.push({
                number: section.number,
                label: section.label,
                value: value || '[Not filled]'
            });
        }

        console.log(`Extracted ${fields.length} fields using smart extraction`);
        return fields;
    }

    // Fallback to pattern matching
    // Extract fields
    for (let i = 0; i < fieldDefinitions.length; i++) {
        const fieldDef = fieldDefinitions[i];
        const nextFieldDef = fieldDefinitions[i + 1];

        // Find start of this field
        let startIdx = -1;
        for (let j = 0; j < lines.length; j++) {
            if (fieldDef.pattern.test(lines[j])) {
                startIdx = j;
                console.log(`Found field ${fieldDef.number} at line ${j}: ${lines[j].substring(0, 50)}`);
                break;
            }
        }

        if (startIdx === -1) {
            console.log(`Field ${fieldDef.number} (${fieldDef.label}) not found`);
            continue;
        }

        // Find end of this field (start of next field or end of document)
        let endIdx = lines.length;
        if (nextFieldDef) {
            for (let j = startIdx + 1; j < lines.length; j++) {
                if (nextFieldDef.pattern.test(lines[j])) {
                    endIdx = j;
                    break;
                }
            }
        }

        // Extract field value (skip the header line and any description lines)
        let valueLines = [];
        let foundContent = false;
        for (let j = startIdx + 1; j < endIdx; j++) {
            const line = lines[j].trim();
            // Skip empty lines at the beginning and description lines
            if (!foundContent && (line === '' || line.startsWith('[') || line.toLowerCase().includes('fill in'))) {
                continue;
            }
            if (line !== '') {
                foundContent = true;
            }
            if (foundContent) {
                valueLines.push(lines[j]);
            }
        }

        const value = valueLines.join('\n').trim();
        fields.push({
            number: fieldDef.number,
            label: fieldDef.label,
            value: value || '[Not filled]'
        });
    }

    return fields;
}

function saveEditedTemplate() {
    const templateType = document.getElementById('editingTemplateType').value;
    const fieldsCount = parseInt(document.getElementById('originalFieldsCount').value);

    // Collect all field values
    const updatedFields = [];
    for (let i = 0; i < fieldsCount; i++) {
        const fieldElement = document.getElementById(`field_${i}`);
        if (fieldElement) {
            updatedFields.push(fieldElement.value);
        }
    }

    // Parse original template to get field definitions
    const content = templateType === 'epic' ? state.activeEpic : state.activeFeature;
    const fields = parseTemplateContent(content, templateType);

    // Rebuild template content
    let newContent = templateType === 'epic' ?
        'EPIC TEMPLATE – SAFe EPIC HYPOTHESIS STATEMENT\n' +
        '------------------------------------------------\n\n' :
        templateType === 'feature' ?
            'FEATURE TEMPLATE – SAFe FEATURE DESCRIPTION\n' +
            '--------------------------------------------\n\n' :
            'USER STORY TEMPLATE – Agile User Story\n' +
            '---------------------------------------\n\n';

    fields.forEach((field, index) => {
        newContent += `${field.number}. ${field.label}\n`;
        newContent += `${updatedFields[index]}\n\n`;
    });

    // Update state
    if (templateType === 'epic') {
        state.activeEpic = newContent;
    } else if (templateType === 'feature') {
        state.activeFeature = newContent;
    } else if (templateType === 'story') {
        state.activeStory = newContent;
    }

    // Update display
    updateActiveContextDisplay();

    // Close modal
    closeTemplateEditor();

    addSystemMessage(`✅ ${templateType.charAt(0).toUpperCase() + templateType.slice(1)} template updated. Click "Save Epic/Feature" to persist to database.`);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Close modal when clicking outside - DISABLED to prevent accidental data loss
// Users must click Cancel or Save Changes to close the modal
// document.getElementById('templateEditorModal').addEventListener('click', (e) => {
//     if (e.target.id === 'templateEditorModal') {
//         closeTemplateEditor();
//     }
// });

// ============================================
// User Story Functions
// ============================================

async function decomposeEpicToFeatures() {
    if (!state.activeEpic) {
        addSystemMessage('⚠️ No active Epic. Please load or create an Epic first.');
        return;
    }

    // Extract epic name for context
    const epicNameMatch = state.activeEpic.match(/EPIC NAME[:\s]*\n([^\n]+)/i);
    const epicName = epicNameMatch ? epicNameMatch[1].trim() : 'the active Epic';

    const userMessage = `Please decompose "${epicName}" into 3-7 Features that together implement the Epic. For each Feature, provide a brief name and benefit hypothesis following the format: "Increase/improve [benefit] by [action/capability] resulting in [measurable outcome]".`;

    // Add user message to conversation
    addUserMessage(userMessage);
    state.conversationHistory.push({ role: 'user', content: userMessage });

    // Send to backend
    await simulateCoachResponse(userMessage);
}

async function decomposeFeatureToStories() {
    if (!state.activeFeature) {
        addSystemMessage('⚠️ No active Feature. Please load or create a Feature first.');
        return;
    }

    // Extract feature name for context
    const featureNameMatch = state.activeFeature.match(/FEATURE NAME[:\s]*\n([^\n]+)/i);
    const featureName = featureNameMatch ? featureNameMatch[1].trim() : 'the active Feature';

    const userMessage = `Please decompose "${featureName}" into 3-5 user stories that together implement the Feature. For each story, provide a brief title and user story statement following the "As a... I want... So that..." format.`;

    // Add user message to conversation
    addUserMessage(userMessage);
    state.conversationHistory.push({ role: 'user', content: userMessage });

    // Send to backend
    await simulateCoachResponse(userMessage);
}

async function draftStory() {
    const userMessage = 'Please draft a complete user story based on our conversation. Use the user story template format with all sections filled in.';

    addUserMessage(userMessage);
    state.conversationHistory.push({ role: 'user', content: userMessage });

    await simulateCoachResponse(userMessage);
}

async function fillStoryTemplate() {
    if (state.isLoading) {
        console.log('Request in progress, ignoring duplicate fill request');
        return;
    }

    state.isLoading = true;
    updateStatus('Filling user story template...');

    try {
        const response = await fetchWithTimeout('/api/fill-template', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                conversation_history: state.conversationHistory,
                template_type: 'story',
                model: state.model,
                temperature: state.temperature,
                provider: state.provider
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to fill template');
        }

        const data = await response.json();
        state.activeStory = data.filled_template;

        addAssistantMessage(data.filled_template);
        addSystemMessage('✅ User Story template filled! You can now edit fields, save, or continue refining.');

        updateActiveContextDisplay();
    } catch (error) {
        console.error('Fill template error:', error);
        addSystemMessage(`❌ Error filling template: ${error.message}`);
    } finally {
        state.isLoading = false;
        updateStatus('Ready to coach');
    }
}

async function evaluateStory() {
    if (!state.activeStory) {
        addSystemMessage('⚠️ No active user story to evaluate. Please load or create a story first.');
        return;
    }

    const userMessage = 'Please evaluate the active user story against Agile best practices. Check if it follows INVEST criteria (Independent, Negotiable, Valuable, Estimable, Small, Testable). Provide specific feedback and suggestions for improvement.';

    addUserMessage(userMessage);
    state.conversationHistory.push({ role: 'user', content: userMessage });

    await simulateCoachResponse(userMessage);
}

function outlineStory() {
    if (!state.activeStory) {
        addSystemMessage('⚠️ No active user story to outline. Please load or create a story first.');
        return;
    }

    // Create formatted outline
    const outline = `
📖 **Active User Story Outline**
${'='.repeat(50)}

${state.activeStory}

${'='.repeat(50)}
    `.trim();

    addAssistantMessage(outline);
    addSystemMessage('✅ User Story outlined!');
}

function newStory() {
    if (confirm('Clear current user story and start fresh? (Conversation history will be preserved)')) {
        state.activeStory = null;
        state.activeStoryId = null;
        updateActiveContextDisplay();
        addSystemMessage('🔄 Ready for a new user story!');
    }
}

async function saveAllProposedStories() {
    // Check if there's an active Feature
    if (!state.activeFeatureId) {
        addSystemMessage('⚠️ No active Feature loaded. Please load a Feature template first before saving stories.');
        return;
    }

    const userConfirm = confirm('This will extract all user story proposals from the conversation and save them as templates linked to the active Feature. Continue?');
    if (!userConfirm) {
        return;
    }

    state.isLoading = true;
    updateStatus('Extracting and saving user story proposals...');

    try {
        // Ask the backend to extract all story proposals and fill templates for each
        const response = await fetchWithTimeout('http://localhost:8050/api/extract-stories', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                activeFeature: state.activeFeature,
                conversationHistory: state.conversationHistory,
                model: state.model,
                temperature: state.temperature,
                provider: state.provider
            })
        }, 180000); // 3 minute timeout

        const data = await response.json();

        if (data.success && data.stories && data.stories.length > 0) {
            addSystemMessage(`✅ Found ${data.stories.length} user story proposal(s). Saving to database...`);

            // Save each story to the database
            let savedCount = 0;
            const tags = prompt('Enter tags for these stories (comma-separated, optional):');
            const tagsList = tags ? tags.split(',').map(t => t.trim()).filter(t => t) : [];

            for (const storyContent of data.stories) {
                console.log('=== Story Content Preview ===');
                console.log(storyContent.substring(0, 300));
                console.log('==============================');

                // Extract story title - try multiple formats
                // Format 1: "USER STORY NAME" section (with or without number)
                let nameMatch = storyContent.match(/^\s*(?:\d+\.\s*)?USER STORY NAME\s*\n\s*(.+?)(?:\n|$)/im);

                // Format 2: "USER STORY NAME:" followed by name on next line
                if (!nameMatch) {
                    nameMatch = storyContent.match(/^USER STORY NAME:\s*\n\s*(.+?)(?:\n|$)/im);
                }

                // Format 3: "USER STORY TITLE:" (old format) for backwards compatibility
                if (!nameMatch) {
                    nameMatch = storyContent.match(/USER STORY TITLE:\s*\n\s*(.+?)(?:\n|$)/i);
                }

                console.log('Name match result:', nameMatch);

                const storyName = nameMatch && nameMatch[1] && nameMatch[1].trim() !== '[Fill in here]'
                    ? nameMatch[1].trim()
                    : `Story ${savedCount + 1}`;

                console.log('Extracted story name:', storyName);

                // Extract description (2. USER STORY STATEMENT section)
                let descriptionMatch = storyContent.match(/(?:\d+\.\s*)?USER STORY STATEMENT\s*\n([\s\S]+?)(?:\n\s*(?:\d+\.\s*)?STORY DESCRIPTION|\n\s*(?:\d+\.\s*)?ACCEPTANCE CRITERIA|$)/i);
                const description = descriptionMatch && descriptionMatch[1] ? descriptionMatch[1].trim() : null;

                // Extract acceptance criteria (4. ACCEPTANCE CRITERIA section)
                let acMatch = storyContent.match(/(?:\d+\.\s*)?ACCEPTANCE CRITERIA\s*\n([\s\S]+?)(?:\n\s*(?:\d+\.\s*)?TECHNICAL NOTES|\n\s*(?:\d+\.\s*)?DEPENDENCIES|\n\s*(?:\d+\.\s*)?STORY POINTS|$)/i);
                const acceptanceCriteria = acMatch && acMatch[1] ? acMatch[1].trim() : null;

                console.log('Extracted description:', description ? description.substring(0, 100) : 'none');
                console.log('Extracted acceptance criteria:', acceptanceCriteria ? acceptanceCriteria.substring(0, 100) : 'none');

                // Save story
                const saveResponse = await fetch('http://localhost:8050/api/template/save', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        template_type: 'story',
                        name: storyName,
                        content: storyContent,
                        description: description,
                        acceptance_criteria: acceptanceCriteria,
                        epic_id: state.activeFeatureId, // Using epic_id field to store feature_id
                        tags: tagsList,
                        metadata: {
                            model: state.model,
                            provider: state.provider,
                            created_from: 'bulk_story_save',
                            parent_type: 'feature'
                        }
                    })
                });

                const saveData = await saveResponse.json();
                if (saveData.success) {
                    savedCount++;
                }
            }

            addSystemMessage(`✅ Successfully saved ${savedCount} user story/stories linked to Feature ID: ${state.activeFeatureId}\n\n💡 *Tip: View them in "📋 Browse Templates" under Stories.*`);
        } else if (data.stories && data.stories.length === 0) {
            addSystemMessage('ℹ️ No user story proposals found in the conversation. Try asking the coach to create user stories first.');
        } else {
            addSystemMessage('⚠️ Unable to extract user stories. Please try again or check the conversation.');
        }

    } catch (error) {
        console.error('Extract stories error:', error);
        addSystemMessage(`❌ Error extracting stories: ${error.message}`);
    } finally {
        state.isLoading = false;
        updateStatus('Ready to coach');
    }
}

async function updateActiveTemplate(templateType) {
    const activeContent = templateType === 'epic' ? state.activeEpic :
        templateType === 'feature' ? state.activeFeature :
            templateType === 'story' ? state.activeStory : null;

    if (!activeContent) {
        addSystemMessage(`⚠️ No active ${templateType} to update.`);
        return;
    }

    const userMessage = `Please update the active ${templateType} template based on our recent conversation. Incorporate any new information, refinements, or changes we've discussed while keeping the existing content intact.`;

    addUserMessage(userMessage);
    state.conversationHistory.push({ role: 'user', content: userMessage });

    await simulateCoachResponse(userMessage);
}

// Update the updateActiveContextDisplay function to include story
function updateActiveContextDisplay() {
    // Epic display
    const epicContainer = document.getElementById('activeEpic');
    const epicContent = document.getElementById('epicContent');

    if (state.activeEpic) {
        const lines = state.activeEpic.split('\n');
        const preview = lines.slice(0, 5).join('\n');
        epicContent.textContent = preview + (lines.length > 5 ? '\n...' : '');
        epicContainer.style.display = 'block';
    } else {
        epicContainer.style.display = 'none';
    }

    // Feature display
    const featureContainer = document.getElementById('activeFeature');
    const featureContent = document.getElementById('featureContent');

    if (state.activeFeature) {
        const lines = state.activeFeature.split('\n');
        const preview = lines.slice(0, 5).join('\n');
        featureContent.textContent = preview + (lines.length > 5 ? '\n...' : '');
        featureContainer.style.display = 'block';
    } else {
        featureContainer.style.display = 'none';
    }

    // Story display
    const storyContainer = document.getElementById('activeStory');
    const storyContent = document.getElementById('storyContent');

    if (state.activeStory) {
        const lines = state.activeStory.split('\n');
        const preview = lines.slice(0, 5).join('\n');
        storyContent.textContent = preview + (lines.length > 5 ? '\n...' : '');
        storyContainer.style.display = 'block';
    } else {
        storyContainer.style.display = 'none';
    }
}
// ============================================================================
// Monitoring & Metrics Functions
// ============================================================================

async function loadMetricsReport() {
    const display = document.getElementById('metricsDisplay');
    display.style.display = 'block';
    display.textContent = 'Loading daily report...';

    try {
        const response = await fetchWithTimeout('http://localhost:8050/api/metrics/report');
        const data = await response.json();

        if (data.success) {
            display.textContent = data.report;
        } else {
            display.textContent = 'Error loading report';
        }
    } catch (error) {
        console.error('Error loading metrics report:', error);
        display.textContent = 'Error: ' + error.message;
    }
}

async function loadMetricsStats() {
    const display = document.getElementById('metricsDisplay');
    const days = document.getElementById('metricsDays').value;
    display.style.display = 'block';
    display.textContent = `Loading statistics for last ${days} days...`;

    try {
        const response = await fetchWithTimeout(`http://localhost:8050/api/metrics/stats?days=${days}`);
        const data = await response.json();

        if (data.success) {
            const stats = data.stats;
            let output = `📊 Discovery Coach Statistics - Last ${days} Days\n`;
            output += '='.repeat(70) + '\n\n';

            output += `Total Conversations: ${stats.total_conversations}\n`;
            output += `  ✅ Successful: ${stats.successful}\n`;
            output += `  ❌ Errors: ${stats.errors}\n`;
            output += `  🔄 Total Retries: ${stats.total_retries}\n`;
            output += `  ⏱️  Average Latency: ${stats.avg_latency.toFixed(2)}s\n\n`;

            if (Object.keys(stats.by_context_type).length > 0) {
                output += '📁 By Context Type:\n';
                for (const [context, perf] of Object.entries(stats.by_context_type)) {
                    output += `  ${context.padEnd(25)} | ${perf.count.toString().padStart(3)} convos | ${perf.avg.toFixed(2)}s avg | ${perf.min.toFixed(2)}-${perf.max.toFixed(2)}s\n`;
                }
                output += '\n';
            }

            if (Object.keys(stats.by_intent).length > 0) {
                output += '🎯 By Intent:\n';
                for (const [intent, perf] of Object.entries(stats.by_intent)) {
                    output += `  ${intent.padEnd(25)} | ${perf.count.toString().padStart(3)} convos | ${perf.avg.toFixed(2)}s avg | ${perf.min.toFixed(2)}-${perf.max.toFixed(2)}s\n`;
                }
                output += '\n';
            }

            if (Object.keys(stats.daily_breakdown).length > 0) {
                output += '📅 Daily Breakdown:\n';
                for (const [date, dayStats] of Object.entries(stats.daily_breakdown).sort()) {
                    const successRate = dayStats.total > 0 ? (dayStats.success / dayStats.total * 100) : 0;
                    output += `  ${date} | ${dayStats.total.toString().padStart(3)} total | ${successRate.toFixed(1).padStart(5)}% success | ${dayStats.avg_latency.toFixed(2)}s avg\n`;
                }
            }

            display.textContent = output;
        } else {
            display.textContent = 'Error loading statistics';
        }
    } catch (error) {
        console.error('Error loading metrics stats:', error);
        display.textContent = 'Error: ' + error.message;
    }
}

async function loadRecentConversations() {
    const display = document.getElementById('metricsDisplay');
    display.style.display = 'block';
    display.textContent = 'Loading recent conversations...';

    try {
        const response = await fetchWithTimeout('http://localhost:8050/api/metrics/conversations?limit=20');
        const data = await response.json();

        if (data.success) {
            const conversations = data.conversations;

            if (conversations.length === 0) {
                display.textContent = '🔇 No conversations recorded yet!\n\nStart using Discovery Coach to see metrics here.';
                return;
            }

            let output = `💬 Last ${conversations.length} Conversations\n`;
            output += '='.repeat(70) + '\n\n';

            conversations.forEach(conv => {
                const timestamp = new Date(conv.timestamp).toLocaleString();
                const status = conv.success ? '✅' : '❌';
                const retryStr = conv.retry_count > 0 ? ` (retries: ${conv.retry_count})` : '';

                output += `[${timestamp}] ${status} ${conv.context_type.padEnd(20)} | ${conv.intent.padEnd(12)} | ${conv.latency.toFixed(2)}s${retryStr}\n`;

                if (conv.validation_issues && conv.validation_issues.length > 0) {
                    output += `  ⚠️  Issues: ${conv.validation_issues.join(', ')}\n`;
                }
            });

            display.textContent = output;
        } else {
            display.textContent = 'Error loading conversations';
        }
    } catch (error) {
        console.error('Error loading conversations:', error);
        display.textContent = 'Error: ' + error.message;
    }
}

async function loadRecentErrors() {
    const display = document.getElementById('metricsDisplay');
    display.style.display = 'block';
    display.textContent = 'Loading recent errors...';

    try {
        const response = await fetchWithTimeout('http://localhost:8050/api/metrics/errors?limit=10');
        const data = await response.json();

        if (data.success) {
            const errors = data.errors;

            if (errors.length === 0) {
                display.textContent = '✅ No errors recorded!\n\nYour Discovery Coach is running smoothly.';
                return;
            }

            let output = `❌ Last ${errors.length} Errors\n`;
            output += '='.repeat(70) + '\n\n';

            errors.forEach(error => {
                const timestamp = new Date(error.timestamp).toLocaleString();
                output += `[${timestamp}] ${error.type}\n`;
                output += `  Message: ${error.message}\n`;
                if (error.context && Object.keys(error.context).length > 0) {
                    output += `  Context: ${JSON.stringify(error.context)}\n`;
                }
                output += '\n';
            });

            display.textContent = output;
        } else {
            display.textContent = 'Error loading errors';
        }
    } catch (error) {
        console.error('Error loading errors:', error);
        display.textContent = 'Error: ' + error.message;
    }
}