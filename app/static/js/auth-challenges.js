/**
 * Authentication Challenge Interface
 * Interactive authentication security demonstration and testing environment
 */

if (!window.SecureTrainer) {
    window.SecureTrainer = {};
}

SecureTrainer.AuthChallenges = {
    // Authentication attack techniques
    attacks: {
        bruteforce: {
            name: "Brute Force Attack",
            description: "Systematic password guessing",
            payloads: ['123456', 'password', 'admin', 'qwerty', 'letmein']
        },
        dictionary: {
            name: "Dictionary Attack", 
            description: "Common password list attack",
            payloads: ['password123', 'welcome', 'changeme', 'secret', 'admin123']
        },
        credential_stuffing: {
            name: "Credential Stuffing",
            description: "Using leaked credential pairs",
            payloads: [
                'admin:admin',
                'user:password',
                'test@example.com:123456',
                'administrator:password123'
            ]
        }
    },

    // Vulnerable authentication scenarios
    vulnerableApps: {
        basicLogin: {
            name: "Basic Login Form",
            description: "Simple login without rate limiting",
            protection: "none",
            users: {
                'admin': 'password123',
                'user': 'qwerty',
                'test': '123456'
            }
        },
        rateLimited: {
            name: "Rate Limited Login",
            description: "Login with basic rate limiting",
            protection: "rate_limit",
            users: {
                'admin': 'SecurePass2023!',
                'manager': 'MyStr0ngP@ss',
                'employee': 'Work123!'
            }
        },
        mfaEnabled: {
            name: "MFA Protected Login",
            description: "Multi-factor authentication system",
            protection: "mfa",
            users: {
                'admin': 'UltraSecure2023!',
                'securityteam': 'DefenseDeep456!',
                'ciso': 'SecurityFirst789!'
            }
        }
    },

    currentChallenge: null,
    attemptHistory: [],
    rateLimitCount: 0,
    isLocked: false,

    init() {
        this.createAuthInterface();
        this.loadVulnerableApp('basicLogin');
        this.setupEventListeners();
    },

    createAuthInterface() {
        const container = document.getElementById('challenge-workspace');
        if (!container) return;

        container.innerHTML = `
            <div class="auth-challenge-container">
                <!-- Attack Configuration Panel -->
                <div class="auth-panel">
                    <h3 class="text-lg font-semibold mb-4">Authentication Attack Configuration</h3>
                    <div class="mb-4">
                        <label class="block text-sm font-medium mb-2">Target Application:</label>
                        <select id="auth-app-select" class="w-full px-3 py-2 border rounded-lg">
                            <option value="basicLogin">Basic Login Form</option>
                            <option value="rateLimited">Rate Limited Login</option>
                            <option value="mfaEnabled">MFA Protected Login</option>
                        </select>
                    </div>
                    <div class="mb-4">
                        <label class="block text-sm font-medium mb-2">Attack Type:</label>
                        <select id="attack-type-select" class="w-full px-3 py-2 border rounded-lg">
                            <option value="bruteforce">Brute Force Attack</option>
                            <option value="dictionary">Dictionary Attack</option>
                            <option value="credential_stuffing">Credential Stuffing</option>
                        </select>
                    </div>
                    <div class="mb-4">
                        <label class="block text-sm font-medium mb-2">Target Username:</label>
                        <input type="text" id="target-username" placeholder="admin" 
                               class="w-full px-3 py-2 border rounded-lg">
                    </div>
                    <div class="mb-4">
                        <label class="block text-sm font-medium mb-2">Custom Password List:</label>
                        <textarea id="password-list" 
                                placeholder="Enter passwords, one per line..."
                                class="w-full h-24 px-3 py-2 border rounded-lg font-mono text-sm"></textarea>
                    </div>
                    <div class="flex gap-2 mb-4">
                        <button id="start-attack-btn" class="btn-primary">Start Attack</button>
                        <button id="stop-attack-btn" class="btn-secondary" disabled>Stop Attack</button>
                        <button id="reset-attack-btn" class="btn-secondary">Reset</button>
                    </div>
                    
                    <!-- Attack Progress -->
                    <div class="attack-progress">
                        <h4 class="font-medium mb-2">Attack Progress:</h4>
                        <div class="progress-bar mb-2">
                            <div id="attack-progress" class="progress-fill" style="width: 0%"></div>
                        </div>
                        <div class="text-sm text-gray-600">
                            <span id="attempts-count">0</span> attempts | 
                            <span id="success-count">0</span> successful logins
                        </div>
                    </div>
                </div>

                <!-- Target Application Interface -->
                <div class="auth-panel">
                    <h3 class="text-lg font-semibold mb-4">Target Login System</h3>
                    <div id="auth-app-container" class="border rounded-lg p-4 bg-gray-50">
                        <!-- Dynamic authentication app content -->
                    </div>
                </div>

                <!-- Attack Results Panel -->
                <div class="auth-panel">
                    <h3 class="text-lg font-semibold mb-4">Attack Results & Analysis</h3>
                    <div class="results-tabs mb-4">
                        <button class="tab-btn active" data-tab="live">Live Feed</button>
                        <button class="tab-btn" data-tab="successful">Successful</button>
                        <button class="tab-btn" data-tab="analysis">Analysis</button>
                    </div>
                    
                    <div id="live-results" class="results-content">
                        <div class="terminal-container">
                            <div class="terminal-header">
                                <span class="terminal-title">Attack Monitor</span>
                            </div>
                            <div class="terminal-body">
                                <div id="attack-feed" class="terminal-text max-h-48 overflow-y-auto">
                                    <div class="terminal-line text-gray-400">Attack monitor ready...</div>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <div id="successful-results" class="results-content hidden">
                        <div id="success-list" class="space-y-2">
                            <p class="text-gray-500">No successful authentications yet.</p>
                        </div>
                    </div>
                    
                    <div id="analysis-results" class="results-content hidden">
                        <div id="security-analysis" class="space-y-3">
                            <p class="text-gray-500">Start an attack to see security analysis.</p>
                        </div>
                    </div>

                    <div class="mt-4">
                        <h4 class="font-medium mb-2">Challenge Score:</h4>
                        <div class="progress-bar">
                            <div id="auth-progress" class="progress-fill" style="width: 0%"></div>
                        </div>
                        <div class="text-sm text-gray-600 mt-1">
                            <span id="auth-score">0</span> / 100 points
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    loadVulnerableApp(appType) {
        const container = document.getElementById('auth-app-container');
        const app = this.vulnerableApps[appType];
        
        if (!container || !app) return;

        let protectionHTML = '';
        switch(app.protection) {
            case 'rate_limit':
                protectionHTML = '<div class="text-orange-600 text-sm mb-2">⚠️ Rate limiting enabled (5 attempts per minute)</div>';
                break;
            case 'mfa':
                protectionHTML = '<div class="text-blue-600 text-sm mb-2">🔒 Multi-factor authentication required</div>';
                break;
            default:
                protectionHTML = '<div class="text-red-600 text-sm mb-2">⚠️ No security protections</div>';
        }

        container.innerHTML = `
            <div class="vulnerable-auth-app">
                <h4 class="font-medium mb-2">${app.name}</h4>
                <p class="text-sm text-gray-600 mb-3">${app.description}</p>
                ${protectionHTML}
                
                <div class="login-form">
                    <div class="mb-3">
                        <label class="block text-sm mb-1">Username:</label>
                        <input type="text" id="login-username" placeholder="Enter username" 
                               class="w-full p-2 border rounded" ${this.isLocked ? 'disabled' : ''}>
                    </div>
                    <div class="mb-3">
                        <label class="block text-sm mb-1">Password:</label>
                        <input type="password" id="login-password" placeholder="Enter password" 
                               class="w-full p-2 border rounded" ${this.isLocked ? 'disabled' : ''}>
                    </div>
                    ${app.protection === 'mfa' ? `
                    <div class="mb-3">
                        <label class="block text-sm mb-1">MFA Code:</label>
                        <input type="text" id="mfa-code" placeholder="6-digit code" 
                               class="w-full p-2 border rounded" maxlength="6" ${this.isLocked ? 'disabled' : ''}>
                    </div>
                    ` : ''}
                    <button id="manual-login-btn" class="btn-primary text-sm w-full" ${this.isLocked ? 'disabled' : ''}>
                        ${this.isLocked ? 'Account Locked' : 'Login'}
                    </button>
                    ${this.isLocked ? `
                    <div class="text-red-600 text-sm mt-2 text-center">
                        Account locked due to too many failed attempts
                    </div>
                    ` : ''}
                </div>
                
                <div class="mt-4 p-3 bg-blue-50 rounded">
                    <h5 class="text-sm font-medium mb-2">Hint - Valid Users:</h5>
                    <div class="text-xs text-gray-600">
                        ${Object.keys(app.users).join(', ')}
                    </div>
                </div>
            </div>
        `;
        
        this.setupLoginForm();
    },

    setupEventListeners() {
        // App selector
        const appSelect = document.getElementById('auth-app-select');
        if (appSelect) {
            appSelect.addEventListener('change', (e) => {
                this.loadVulnerableApp(e.target.value);
                this.resetAttack();
            });
        }

        // Attack controls
        const startBtn = document.getElementById('start-attack-btn');
        const stopBtn = document.getElementById('stop-attack-btn');
        const resetBtn = document.getElementById('reset-attack-btn');

        if (startBtn) {
            startBtn.addEventListener('click', () => this.startAttack());
        }
        if (stopBtn) {
            stopBtn.addEventListener('click', () => this.stopAttack());
        }
        if (resetBtn) {
            resetBtn.addEventListener('click', () => this.resetAttack());
        }

        // Tab switching
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.switchTab(e.target.dataset.tab);
            });
        });

        this.setupLoginForm();
    },

    setupLoginForm() {
        const loginBtn = document.getElementById('manual-login-btn');
        if (loginBtn && !this.isLocked) {
            loginBtn.addEventListener('click', () => {
                const username = document.getElementById('login-username').value;
                const password = document.getElementById('login-password').value;
                const mfaCode = document.getElementById('mfa-code')?.value;
                
                this.attemptLogin(username, password, mfaCode, true);
            });
        }
    },

    startAttack() {
        const appType = document.getElementById('auth-app-select').value;
        const attackType = document.getElementById('attack-type-select').value;
        const username = document.getElementById('target-username').value;
        const customPasswords = document.getElementById('password-list').value;

        if (!username.trim()) {
            this.addToFeed('Error: Please specify a target username', 'error');
            return;
        }

        // Get password list
        let passwordList = [];
        if (customPasswords.trim()) {
            passwordList = customPasswords.split('\n').filter(p => p.trim());
        } else {
            passwordList = this.attacks[attackType].payloads;
        }

        this.currentAttack = {
            appType,
            attackType,
            username,
            passwordList,
            currentIndex: 0,
            isRunning: true,
            startTime: Date.now()
        };

        // Update UI
        document.getElementById('start-attack-btn').disabled = true;
        document.getElementById('stop-attack-btn').disabled = false;
        
        this.addToFeed(`Starting ${this.attacks[attackType].name} against ${username}`, 'info');
        this.addToFeed(`Password list: ${passwordList.length} entries`, 'info');
        
        this.runAttack();
    },

    async runAttack() {
        if (!this.currentAttack || !this.currentAttack.isRunning) return;

        const { username, passwordList, currentIndex, appType } = this.currentAttack;
        
        if (currentIndex >= passwordList.length) {
            this.stopAttack();
            this.addToFeed('Attack completed - all passwords tested', 'info');
            return;
        }

        const password = passwordList[currentIndex];
        const result = await this.attemptLogin(username, password, null, false);
        
        this.currentAttack.currentIndex++;
        
        // Update progress
        const progress = (currentIndex / passwordList.length) * 100;
        document.getElementById('attack-progress').style.width = progress + '%';
        document.getElementById('attempts-count').textContent = currentIndex + 1;

        // Continue attack with delay based on protection level
        if (this.currentAttack.isRunning) {
            const app = this.vulnerableApps[appType];
            let delay = 100; // Default fast attack
            
            if (app.protection === 'rate_limit') {
                delay = 12000; // Slow down for rate limiting
            } else if (app.protection === 'mfa') {
                delay = 2000; // Moderate delay for MFA
            }
            
            setTimeout(() => this.runAttack(), delay);
        }
    },

    async attemptLogin(username, password, mfaCode, isManual) {
        const appType = document.getElementById('auth-app-select').value;
        const app = this.vulnerableApps[appType];
        
        // Check rate limiting
        if (app.protection === 'rate_limit') {
            this.rateLimitCount++;
            if (this.rateLimitCount > 5) {
                this.isLocked = true;
                this.loadVulnerableApp(appType);
                this.addToFeed(`Rate limit exceeded - account locked`, 'error');
                return { success: false, reason: 'rate_limited' };
            }
        }

        // Check credentials
        const validPassword = app.users[username];
        const credentialsValid = validPassword && validPassword === password;
        
        let success = false;
        let reason = '';

        if (!credentialsValid) {
            reason = 'invalid_credentials';
            this.addToFeed(`Failed: ${username}:${password}`, 'error');
        } else {
            // Check MFA if required
            if (app.protection === 'mfa') {
                const validMfaCode = '123456'; // Simulated MFA code
                if (!mfaCode || mfaCode !== validMfaCode) {
                    reason = 'invalid_mfa';
                    this.addToFeed(`MFA failed: ${username}:${password} (MFA: ${mfaCode || 'none'})`, 'error');
                } else {
                    success = true;
                    reason = 'success';
                }
            } else {
                success = true;
                reason = 'success';
            }
        }

        if (success) {
            this.addToFeed(`SUCCESS: ${username}:${password}`, 'success');
            this.addSuccessfulLogin(username, password, mfaCode);
            this.updateScore(20);
            
            const currentSuccess = parseInt(document.getElementById('success-count').textContent);
            document.getElementById('success-count').textContent = currentSuccess + 1;
        }

        this.attemptHistory.push({
            username,
            password,
            mfaCode,
            success,
            reason,
            timestamp: new Date(),
            isManual
        });

        return { success, reason };
    },

    stopAttack() {
        if (this.currentAttack) {
            this.currentAttack.isRunning = false;
        }
        
        document.getElementById('start-attack-btn').disabled = false;
        document.getElementById('stop-attack-btn').disabled = true;
        
        this.addToFeed('Attack stopped by user', 'info');
        this.generateAnalysis();
    },

    resetAttack() {
        this.stopAttack();
        this.attemptHistory = [];
        this.rateLimitCount = 0;
        this.isLocked = false;
        this.currentAttack = null;
        
        // Reset UI
        document.getElementById('attack-progress').style.width = '0%';
        document.getElementById('attempts-count').textContent = '0';
        document.getElementById('success-count').textContent = '0';
        document.getElementById('attack-feed').innerHTML = '<div class="terminal-line text-gray-400">Attack monitor ready...</div>';
        document.getElementById('success-list').innerHTML = '<p class="text-gray-500">No successful authentications yet.</p>';
        document.getElementById('security-analysis').innerHTML = '<p class="text-gray-500">Start an attack to see security analysis.</p>';
        
        // Reload current app
        const appType = document.getElementById('auth-app-select').value;
        this.loadVulnerableApp(appType);
    },

    addToFeed(message, type) {
        const feed = document.getElementById('attack-feed');
        if (!feed) return;

        const timestamp = new Date().toLocaleTimeString();
        const typeClasses = {
            success: 'text-green-400',
            error: 'text-red-400',
            info: 'text-blue-400'
        };

        const logEntry = document.createElement('div');
        logEntry.className = `terminal-line ${typeClasses[type] || 'text-white'}`;
        logEntry.textContent = `[${timestamp}] ${message}`;
        
        feed.appendChild(logEntry);
        feed.scrollTop = feed.scrollHeight;
    },

    addSuccessfulLogin(username, password, mfaCode) {
        const successList = document.getElementById('success-list');
        if (!successList) return;

        if (successList.querySelector('.text-gray-500')) {
            successList.innerHTML = '';
        }

        const successItem = document.createElement('div');
        successItem.className = 'p-3 bg-green-50 border border-green-200 rounded';
        successItem.innerHTML = `
            <div class="font-medium text-green-800">Successful Login</div>
            <div class="text-sm text-green-600">
                Username: <code>${username}</code><br>
                Password: <code>${password}</code>
                ${mfaCode ? `<br>MFA Code: <code>${mfaCode}</code>` : ''}
            </div>
            <div class="text-xs text-gray-500 mt-1">
                ${new Date().toLocaleString()}
            </div>
        `;
        
        successList.appendChild(successItem);
    },

    generateAnalysis() {
        const analysisContainer = document.getElementById('security-analysis');
        if (!analysisContainer || this.attemptHistory.length === 0) return;

        const totalAttempts = this.attemptHistory.length;
        const successfulAttempts = this.attemptHistory.filter(a => a.success).length;
        const uniquePasswords = new Set(this.attemptHistory.map(a => a.password)).size;
        const appType = document.getElementById('auth-app-select').value;
        const app = this.vulnerableApps[appType];

        let securityRating = 'High Risk';
        let recommendations = [];

        if (app.protection === 'none') {
            securityRating = 'Critical Risk';
            recommendations = [
                'Implement account lockout after failed attempts',
                'Add rate limiting to prevent brute force attacks',
                'Require strong password policies',
                'Consider implementing multi-factor authentication'
            ];
        } else if (app.protection === 'rate_limit') {
            securityRating = 'Medium Risk';
            recommendations = [
                'Implement multi-factor authentication',
                'Use CAPTCHA after failed attempts',
                'Monitor and alert on suspicious login patterns',
                'Implement progressive delays for failed attempts'
            ];
        } else {
            securityRating = 'Low Risk';
            recommendations = [
                'Monitor MFA bypass attempts',
                'Implement behavioral analysis',
                'Regular security awareness training',
                'Consider hardware security keys'
            ];
        }

        analysisContainer.innerHTML = `
            <div class="space-y-4">
                <div class="grid grid-cols-2 gap-4">
                    <div class="stat-card">
                        <div class="text-2xl font-bold text-blue-600">${totalAttempts}</div>
                        <div class="text-sm text-gray-600">Total Attempts</div>
                    </div>
                    <div class="stat-card">
                        <div class="text-2xl font-bold ${successfulAttempts > 0 ? 'text-red-600' : 'text-green-600'}">${successfulAttempts}</div>
                        <div class="text-sm text-gray-600">Successful Logins</div>
                    </div>
                </div>
                
                <div class="security-rating">
                    <h5 class="font-medium mb-2">Security Assessment:</h5>
                    <div class="p-3 rounded ${securityRating === 'Critical Risk' ? 'bg-red-50 text-red-800' : 
                                              securityRating === 'High Risk' ? 'bg-orange-50 text-orange-800' :
                                              securityRating === 'Medium Risk' ? 'bg-yellow-50 text-yellow-800' :
                                              'bg-green-50 text-green-800'}">
                        ${securityRating}
                    </div>
                </div>
                
                <div class="recommendations">
                    <h5 class="font-medium mb-2">Security Recommendations:</h5>
                    <ul class="text-sm space-y-1">
                        ${recommendations.map(rec => `<li class="flex items-start"><span class="text-blue-500 mr-2">•</span>${rec}</li>`).join('')}
                    </ul>
                </div>
            </div>
        `;
    },

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

        // Show/hide content
        document.querySelectorAll('.results-content').forEach(content => {
            content.classList.add('hidden');
        });
        document.getElementById(`${tabName}-results`).classList.remove('hidden');
    },

    updateScore(points) {
        const currentScore = parseInt(document.getElementById('auth-score').textContent) || 0;
        const newScore = Math.min(currentScore + points, 100);
        
        document.getElementById('auth-score').textContent = newScore;
        document.getElementById('auth-progress').style.width = newScore + '%';
        
        if (newScore >= 100) {
            SecureTrainer.Analytics.trackChallengeCompletion('authentication', newScore);
        }
    }
};

// Auto-initialize when challenge is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('challenge-workspace')) {
        SecureTrainer.AuthChallenges.init();
    }
});