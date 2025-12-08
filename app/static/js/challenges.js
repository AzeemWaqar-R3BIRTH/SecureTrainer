/**
 * Challenge Interface Module
 * Handles interactive cybersecurity challenge components
 * Supports SQL injection, XSS, command injection, and authentication challenges
 */

// Challenge system core
SecureTrainer.Challenges = {
    // Current challenge state
    currentChallenge: null,
    startTime: null,
    hintsUsed: 0,
    attempts: 0,
    
    // Initialize challenge system
    init() {
        console.log('🎯 Initializing challenge system...');
        this.setupEventHandlers();
        this.loadChallengeInterface();
        this.initializeChallengeTypes();
    },
    
    // Setup event handlers
    setupEventHandlers() {
        // Challenge category selection
        document.addEventListener('click', (event) => {
            if (event.target.matches('[data-challenge-category]')) {
                const category = event.target.dataset.challengeCategory;
                this.startChallengeCategory(category);
            }
        });
        
        // Challenge submission
        document.addEventListener('submit', (event) => {
            if (event.target.matches('.challenge-form')) {
                event.preventDefault();
                this.submitChallenge(event.target);
            }
        });
        
        // Hint requests
        document.addEventListener('click', (event) => {
            if (event.target.matches('[data-action="request-hint"]')) {
                this.requestHint();
            }
        });
        
        // Challenge reset
        document.addEventListener('click', (event) => {
            if (event.target.matches('[data-action="reset-challenge"]')) {
                this.resetChallenge();
            }
        });
    },
    
    // Load challenge interface
    async loadChallengeInterface() {
        const container = document.getElementById('challenge-container');
        if (!container) return;
        
        try {
            const challengeData = await SecureTrainer.API.get('/challenges/list');
            this.renderChallengeCategories(challengeData);
        } catch (error) {
            console.error('Failed to load challenges:', error);
            this.showError('Failed to load challenges. Please refresh the page.');
        }
    },
    
    // Render challenge categories
    renderChallengeCategories(challengeData) {
        const container = document.getElementById('challenge-container');
        
        const categories = [
            {
                id: 'sql_injection',
                name: 'SQL Injection',
                description: 'Learn to identify and prevent SQL injection vulnerabilities',
                icon: 'fas fa-database',
                color: 'red',
                challenges: challengeData.filter(c => c.category === 'sql_injection')
            },
            {
                id: 'xss',
                name: 'Cross-Site Scripting',
                description: 'Master XSS detection and prevention techniques',
                icon: 'fas fa-code',
                color: 'yellow',
                challenges: challengeData.filter(c => c.category === 'xss')
            },
            {
                id: 'command_injection',
                name: 'Command Injection',
                description: 'Understand command injection vulnerabilities',
                icon: 'fas fa-terminal',
                color: 'purple',
                challenges: challengeData.filter(c => c.category === 'command_injection')
            },
            {
                id: 'authentication',
                name: 'Authentication Bypass',
                description: 'Learn about authentication vulnerabilities',
                icon: 'fas fa-key',
                color: 'green',
                challenges: challengeData.filter(c => c.category === 'authentication')
            }
        ];
        
        const categoriesHTML = categories.map(category => `
            <div class="challenge-card challenge-type-${category.id.replace('_', '-')} card">
                <div class="card-header">
                    <div class="flex items-center">
                        <i class="${category.icon} text-2xl text-${category.color}-600 mr-3"></i>
                        <h3 class="text-lg font-semibold">${category.name}</h3>
                    </div>
                </div>
                <div class="card-body">
                    <p class="text-gray-600 mb-4">${category.description}</p>
                    <div class="mb-4">
                        <div class="flex justify-between mb-1">
                            <span class="text-sm font-medium text-gray-700">Progress</span>
                            <span class="text-sm font-medium text-gray-700" id="${category.id}-progress">
                                0/${category.challenges.length} completed
                            </span>
                        </div>
                        <div class="progress-bar">
                            <div class="progress-fill bg-${category.color}-600" id="${category.id}-progress-bar" style="width: 0%"></div>
                        </div>
                    </div>
                    <button 
                        data-challenge-category="${category.id}"
                        class="btn btn-block bg-${category.color}-600 hover:bg-${category.color}-700">
                        Start ${category.name} Challenges
                    </button>
                </div>
            </div>
        `).join('');
        
        container.innerHTML = `
            <div class="challenge-grid">
                ${categoriesHTML}
            </div>
        `;
    },
    
    // Start challenge category
    async startChallengeCategory(category) {
        try {
            SecureTrainer.Performance.startTiming('challenge-load');
            
            const response = await SecureTrainer.API.post('/challenges/start', {
                category: category,
                user_id: SecureTrainer.state.currentUser?.id
            });
            
            if (response.success) {
                this.currentChallenge = response.challenge;
                this.startTime = Date.now();
                this.hintsUsed = 0;
                this.attempts = 0;
                
                this.renderChallengeInterface(response.challenge);
                
                SecureTrainer.events.dispatchEvent(new CustomEvent('challenge:start', {
                    detail: response.challenge
                }));
                
                SecureTrainer.Analytics.trackEvent('challenge_started', {
                    challengeId: response.challenge.id,
                    category: category
                });
            } else {
                this.showError(response.message || 'Failed to start challenge');
            }
            
            SecureTrainer.Performance.endTiming('challenge-load');
            
        } catch (error) {
            console.error('Failed to start challenge:', error);
            this.showError('Failed to start challenge. Please try again.');
        }
    },
    
    // Render challenge interface
    renderChallengeInterface(challenge) {
        const container = document.getElementById('challenge-container');
        
        const interfaceHTML = `
            <div class="challenge-active">
                <div class="challenge-header mb-6">
                    <div class="flex justify-between items-start">
                        <div>
                            <h2 class="text-2xl font-bold mb-2">${challenge.title}</h2>
                            <div class="flex items-center space-x-4 text-sm text-gray-600">
                                <span class="flex items-center">
                                    <i class="fas fa-signal mr-1"></i>
                                    Difficulty: ${challenge.difficulty}
                                </span>
                                <span class="flex items-center">
                                    <i class="fas fa-clock mr-1"></i>
                                    <span id="challenge-timer">00:00</span>
                                </span>
                                <span class="flex items-center">
                                    <i class="fas fa-lightbulb mr-1"></i>
                                    Hints: <span id="hints-used">0</span>
                                </span>
                            </div>
                        </div>
                        <button data-action="reset-challenge" class="btn btn-secondary">
                            <i class="fas fa-redo mr-2"></i>New Challenge
                        </button>
                    </div>
                </div>
                
                <div class="challenge-content">
                    <div class="challenge-description mb-6">
                        <div class="card">
                            <div class="card-header">
                                <h3 class="font-semibold">Challenge Description</h3>
                            </div>
                            <div class="card-body">
                                <p>${challenge.question}</p>
                                ${challenge.scenario ? `<div class="mt-4 p-4 bg-blue-50 rounded-lg">
                                    <h4 class="font-semibold text-blue-800 mb-2">Scenario:</h4>
                                    <p class="text-blue-700">${challenge.scenario}</p>
                                </div>` : ''}
                            </div>
                        </div>
                    </div>
                    
                    <div class="challenge-interface grid grid-cols-1 lg:grid-cols-2 gap-6">
                        <div class="challenge-workspace">
                            ${this.getChallengeWorkspace(challenge)}
                        </div>
                        
                        <div class="challenge-feedback">
                            <div class="card">
                                <div class="card-header">
                                    <h3 class="font-semibold">Results & Feedback</h3>
                                </div>
                                <div class="card-body">
                                    <div id="challenge-output" class="terminal min-h-32">
                                        <div class="terminal-content">
                                            <div class="text-green-400">Ready to execute your payload...</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            
                            <div class="mt-4">
                                <button data-action="request-hint" class="btn btn-secondary mr-2">
                                    <i class="fas fa-lightbulb mr-2"></i>Get Hint
                                </button>
                                <button data-action="submit-challenge" class="btn btn-primary">
                                    <i class="fas fa-check mr-2"></i>Submit Solution
                                </button>
                            </div>
                            
                            <div id="hint-container" class="mt-4" style="display: none;">
                                <!-- Hints will be displayed here -->
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        container.innerHTML = interfaceHTML;
        
        // Start challenge timer
        this.startChallengeTimer();
        
        // Initialize challenge-specific components
        this.initializeChallengeWorkspace(challenge);
    },
    
    // Get challenge workspace based on type
    getChallengeWorkspace(challenge) {
        switch (challenge.category) {
            case 'sql_injection':
                return this.getSQLInjectionWorkspace(challenge);
            case 'xss':
                return this.getXSSWorkspace(challenge);
            case 'command_injection':
                return this.getCommandInjectionWorkspace(challenge);
            case 'authentication':
                return this.getAuthenticationWorkspace(challenge);
            default:
                return this.getGenericWorkspace(challenge);
        }
    },
    
    // SQL Injection workspace
    getSQLInjectionWorkspace(challenge) {
        return `
            <div class="card">
                <div class="card-header">
                    <h3 class="font-semibold">SQL Injection Interface</h3>
                </div>
                <div class="card-body">
                    <div class="vulnerable-form">
                        <label class="block text-sm font-medium mb-2">Enter your SQL payload:</label>
                        <input 
                            type="text" 
                            id="sql-payload" 
                            class="payload-input"
                            placeholder="e.g., ' OR '1'='1' --"
                            autocomplete="off">
                        <button onclick="SecureTrainer.Challenges.executeSQLPayload()" class="btn btn-primary mt-2">
                            Execute Query
                        </button>
                    </div>
                    
                    <div class="mt-4">
                        <h4 class="font-semibold mb-2">Executed Query:</h4>
                        <div class="code-box" data-language="sql">
                            <code id="query-preview">SELECT * FROM users WHERE username = '[payload]' AND password = 'password'</code>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },
    
    // XSS workspace
    getXSSWorkspace(challenge) {
        return `
            <div class="card">
                <div class="card-header">
                    <h3 class="font-semibold">XSS Testing Interface</h3>
                </div>
                <div class="card-body">
                    <div class="vulnerable-form">
                        <label class="block text-sm font-medium mb-2">Enter your XSS payload:</label>
                        <textarea 
                            id="xss-payload" 
                            class="payload-input"
                            rows="3"
                            placeholder="e.g., <script>alert('XSS')</script>"></textarea>
                        <button onclick="SecureTrainer.Challenges.executeXSSPayload()" class="btn btn-primary mt-2">
                            Test Payload
                        </button>
                    </div>
                    
                    <div class="mt-4">
                        <h4 class="font-semibold mb-2">Vulnerable Page Preview:</h4>
                        <div class="border rounded p-4 bg-white min-h-32" id="xss-preview">
                            <div class="text-gray-500">Enter a payload above to see the result...</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },
    
    // Command Injection workspace
    getCommandInjectionWorkspace(challenge) {
        return `
            <div class="card">
                <div class="card-header">
                    <h3 class="font-semibold">Network Utility Interface</h3>
                </div>
                <div class="card-body">
                    <div class="vulnerable-form">
                        <label class="block text-sm font-medium mb-2">Enter IP address to ping:</label>
                        <input 
                            type="text" 
                            id="cmd-input" 
                            class="payload-input"
                            placeholder="127.0.0.1">
                        <button onclick="SecureTrainer.Challenges.executeCommand()" class="btn btn-primary mt-2">
                            Execute Ping
                        </button>
                    </div>
                    
                    <div class="mt-4">
                        <h4 class="font-semibold mb-2">Command to Execute:</h4>
                        <div class="code-box" data-language="bash">
                            <code id="cmd-preview">ping -c 4 [input]</code>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },
    
    // Authentication workspace
    getAuthenticationWorkspace(challenge) {
        return `
            <div class="card">
                <div class="card-header">
                    <h3 class="font-semibold">Login Interface</h3>
                </div>
                <div class="card-body">
                    <div class="vulnerable-form">
                        <div class="mb-4">
                            <label class="block text-sm font-medium mb-2">Username:</label>
                            <input 
                                type="text" 
                                id="auth-username" 
                                class="payload-input"
                                placeholder="Enter username">
                        </div>
                        <div class="mb-4">
                            <label class="block text-sm font-medium mb-2">Password:</label>
                            <input 
                                type="password" 
                                id="auth-password" 
                                class="payload-input"
                                placeholder="Enter password">
                        </div>
                        <button onclick="SecureTrainer.Challenges.attemptLogin()" class="btn btn-primary">
                            Login
                        </button>
                    </div>
                </div>
            </div>
        `;
    },
    
    // Generic workspace
    getGenericWorkspace(challenge) {
        return `
            <div class="card">
                <div class="card-header">
                    <h3 class="font-semibold">Challenge Workspace</h3>
                </div>
                <div class="card-body">
                    <div class="vulnerable-form">
                        <label class="block text-sm font-medium mb-2">Enter your solution:</label>
                        <textarea 
                            id="generic-payload" 
                            class="payload-input"
                            rows="4"
                            placeholder="Enter your solution here..."></textarea>
                        <button onclick="SecureTrainer.Challenges.executeGenericPayload()" class="btn btn-primary mt-2">
                            Submit Answer
                        </button>
                    </div>
                </div>
            </div>
        `;
    },
    
    // Initialize challenge-specific components
    initializeChallengeWorkspace(challenge) {
        // Add real-time input preview
        this.setupInputPreview(challenge);
        
        // Setup keyboard shortcuts
        this.setupKeyboardShortcuts();
        
        // Initialize challenge-specific functionality
        switch (challenge.category) {
            case 'sql_injection':
                this.initializeSQLInterface();
                break;
            case 'xss':
                this.initializeXSSInterface();
                break;
            case 'command_injection':
                this.initializeCommandInterface();
                break;
            case 'authentication':
                this.initializeAuthInterface();
                break;
        }
    },
    
    // Setup input preview
    setupInputPreview(challenge) {
        const payloadInput = document.getElementById('sql-payload') || 
                           document.getElementById('xss-payload') || 
                           document.getElementById('cmd-input');
        
        if (payloadInput) {
            payloadInput.addEventListener('input', SecureTrainer.Utils.debounce((event) => {
                this.updatePreview(challenge.category, event.target.value);
            }, 300));
        }
    },
    
    // Update preview based on input
    updatePreview(category, payload) {
        switch (category) {
            case 'sql_injection':
                this.updateSQLPreview(payload);
                break;
            case 'command_injection':
                this.updateCommandPreview(payload);
                break;
        }
    },
    
    // Update SQL preview
    updateSQLPreview(payload) {
        const preview = document.getElementById('query-preview');
        if (preview) {
            const query = `SELECT * FROM users WHERE username = '${payload}' AND password = 'password'`;
            preview.textContent = query;
        }
    },
    
    // Update command preview
    updateCommandPreview(input) {
        const preview = document.getElementById('cmd-preview');
        if (preview) {
            preview.textContent = `ping -c 4 ${input}`;
        }
    },
    
    // Setup keyboard shortcuts
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (event) => {
            if (event.ctrlKey || event.metaKey) {
                switch (event.key) {
                    case 'Enter':
                        event.preventDefault();
                        this.submitCurrentChallenge();
                        break;
                    case 'h':
                        event.preventDefault();
                        this.requestHint();
                        break;
                    case 'r':
                        event.preventDefault();
                        this.resetChallenge();
                        break;
                }
            }
        });
    },
    
    // Challenge timer
    startChallengeTimer() {
        const timerElement = document.getElementById('challenge-timer');
        if (!timerElement) return;
        
        this.timerInterval = setInterval(() => {
            const elapsed = Date.now() - this.startTime;
            const minutes = Math.floor(elapsed / 60000);
            const seconds = Math.floor((elapsed % 60000) / 1000);
            
            timerElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
        }, 1000);
    },
    
    // Show error message
    showError(message) {
        SecureTrainer.showNotification(message, 'error');
    },
    
    // Show success message
    showSuccess(message) {
        SecureTrainer.showNotification(message, 'success');
    }
};

// Challenge execution methods will be added in the next part
// Due to length constraints, continuing in separate files for each challenge type