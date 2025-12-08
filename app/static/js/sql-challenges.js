/**
 * SQL Injection Challenge Interface
 * Interactive components for SQL injection training and practice
 */

// Extend SecureTrainer.Challenges with SQL injection functionality
SecureTrainer.Challenges.SQL = {
    currentChallenge: null,
    vulnerableDatabase: null,
    
    // Initialize SQL injection interface
    init() {
        console.log('🗃️ SQL Injection interface initialized');
        this.setupVulnerableDatabase();
    },
    
    // Setup simulated vulnerable database
    setupVulnerableDatabase() {
        this.vulnerableDatabase = {
            users: [
                { id: 1, username: 'admin', password: 'admin123', role: 'administrator', email: 'admin@company.com' },
                { id: 2, username: 'user1', password: 'password123', role: 'user', email: 'user1@company.com' },
                { id: 3, username: 'guest', password: 'guest', role: 'guest', email: 'guest@company.com' },
                { id: 4, username: 'manager', password: 'manager456', role: 'manager', email: 'manager@company.com' },
                { id: 5, username: 'test', password: 'test123', role: 'user', email: 'test@company.com' }
            ],
            products: [
                { id: 1, name: 'Laptop', price: 999.99, category: 'Electronics' },
                { id: 2, name: 'Mouse', price: 29.99, category: 'Electronics' },
                { id: 3, name: 'Keyboard', price: 79.99, category: 'Electronics' }
            ],
            orders: [
                { id: 1, user_id: 1, product_id: 1, quantity: 1, total: 999.99 },
                { id: 2, user_id: 2, product_id: 2, quantity: 2, total: 59.98 }
            ]
        };
    },
    
    // Initialize SQL injection challenge workspace
    initializeSQLInterface() {
        const workspace = document.querySelector('.challenge-workspace');
        if (!workspace) return;
        
        // Add SQL injection specific components
        this.addSQLEditor(workspace);
        this.addDatabaseViewer(workspace);
        this.addQueryResults(workspace);
        this.setupSQLEvents();
    },
    
    // Add SQL editor component
    addSQLEditor(container) {
        const editorHTML = `
            <div class="sql-editor-container mb-6">
                <div class="card">
                    <div class="card-header">
                        <h3 class="font-semibold flex items-center">
                            <i class="fas fa-database mr-2"></i>
                            SQL Injection Interface
                        </h3>
                    </div>
                    <div class="card-body">
                        <div class="mb-4">
                            <label class="block text-sm font-medium mb-2">Login Form (Vulnerable)</label>
                            <div class="vulnerable-form bg-gray-50 p-4 rounded border">
                                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                                    <div>
                                        <label class="block text-sm font-medium mb-1">Username:</label>
                                        <input type="text" id="sql-username" class="payload-input" placeholder="Enter username">
                                    </div>
                                    <div>
                                        <label class="block text-sm font-medium mb-1">Password:</label>
                                        <input type="password" id="sql-password" class="payload-input" placeholder="Enter password">
                                    </div>
                                </div>
                                <button onclick="SecureTrainer.Challenges.SQL.attemptLogin()" class="btn btn-primary">
                                    <i class="fas fa-sign-in-alt mr-2"></i>Login
                                </button>
                            </div>
                        </div>
                        
                        <div class="mb-4">
                            <label class="block text-sm font-medium mb-2">Direct SQL Query Interface</label>
                            <div class="flex gap-2">
                                <input type="text" id="sql-payload" class="payload-input flex-1" 
                                       placeholder="e.g., ' OR '1'='1' --">
                                <button onclick="SecureTrainer.Challenges.SQL.executePayload()" class="btn btn-primary">
                                    Execute
                                </button>
                            </div>
                        </div>
                        
                        <div class="mb-4">
                            <h4 class="font-semibold mb-2">Constructed Query:</h4>
                            <div class="code-box p-3" data-language="sql">
                                <code id="sql-query-preview">SELECT * FROM users WHERE username = '[username]' AND password = '[password]'</code>
                            </div>
                        </div>
                        
                        <div class="mb-4">
                            <h4 class="font-semibold mb-2">Quick Payloads:</h4>
                            <div class="flex flex-wrap gap-2">
                                <button onclick="SecureTrainer.Challenges.SQL.usePayload(\\'' OR \\'1\\'=\\'1\\' --\\')" class="btn btn-secondary btn-sm">
                                    ' OR '1'='1' --
                                </button>
                                <button onclick="SecureTrainer.Challenges.SQL.usePayload(\\'admin\\' --\\')" class="btn btn-secondary btn-sm">
                                    admin' --
                                </button>
                                <button onclick="SecureTrainer.Challenges.SQL.usePayload(\\'' UNION SELECT 1,2,3,4,5 --\\')" class="btn btn-secondary btn-sm">
                                    ' UNION SELECT 1,2,3,4,5 --
                                </button>
                                <button onclick="SecureTrainer.Challenges.SQL.usePayload(\\'' AND 1=2 UNION SELECT username,password,email,role,id FROM users --\\')" class="btn btn-secondary btn-sm">
                                    UNION Extract
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        container.insertAdjacentHTML('beforeend', editorHTML);
    },
    
    // Add database viewer
    addDatabaseViewer(container) {
        const viewerHTML = `
            <div class="database-viewer mb-6">
                <div class="card">
                    <div class="card-header">
                        <h3 class="font-semibold">Database Structure (Hidden from attacker)</h3>
                    </div>
                    <div class="card-body">
                        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
                            <div>
                                <h4 class="font-medium mb-2">Users Table</h4>
                                <div class="text-xs bg-gray-100 p-2 rounded">
                                    <div class="font-mono">
                                        id (INT)<br>
                                        username (VARCHAR)<br>
                                        password (VARCHAR)<br>
                                        role (VARCHAR)<br>
                                        email (VARCHAR)
                                    </div>
                                </div>
                            </div>
                            <div>
                                <h4 class="font-medium mb-2">Products Table</h4>
                                <div class="text-xs bg-gray-100 p-2 rounded">
                                    <div class="font-mono">
                                        id (INT)<br>
                                        name (VARCHAR)<br>
                                        price (DECIMAL)<br>
                                        category (VARCHAR)
                                    </div>
                                </div>
                            </div>
                            <div>
                                <h4 class="font-medium mb-2">Orders Table</h4>
                                <div class="text-xs bg-gray-100 p-2 rounded">
                                    <div class="font-mono">
                                        id (INT)<br>
                                        user_id (INT)<br>
                                        product_id (INT)<br>
                                        quantity (INT)<br>
                                        total (DECIMAL)
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        container.insertAdjacentHTML('beforeend', viewerHTML);
    },
    
    // Add query results display
    addQueryResults(container) {
        const resultsHTML = `
            <div class="query-results">
                <div class="card">
                    <div class="card-header">
                        <h3 class="font-semibold">Query Results</h3>
                    </div>
                    <div class="card-body">
                        <div id="sql-results" class="terminal min-h-32">
                            <div class="terminal-content">
                                <div class="text-green-400">Ready to execute SQL queries...</div>
                                <div class="text-yellow-400">Try different injection techniques to bypass authentication or extract data.</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        container.insertAdjacentHTML('beforeend', resultsHTML);
    },
    
    // Setup SQL specific event handlers
    setupSQLEvents() {
        // Real-time query preview
        const usernameInput = document.getElementById('sql-username');
        const passwordInput = document.getElementById('sql-password');
        const payloadInput = document.getElementById('sql-payload');
        
        if (usernameInput && passwordInput) {
            [usernameInput, passwordInput].forEach(input => {
                input.addEventListener('input', () => this.updateQueryPreview());
            });
        }
        
        if (payloadInput) {
            payloadInput.addEventListener('input', () => this.updateDirectQueryPreview());
        }
        
        // Enter key submission
        [usernameInput, passwordInput, payloadInput].forEach(input => {
            if (input) {
                input.addEventListener('keypress', (e) => {
                    if (e.key === 'Enter') {
                        if (input === payloadInput) {
                            this.executePayload();
                        } else {
                            this.attemptLogin();
                        }
                    }
                });
            }
        });
    },
    
    // Update query preview for login form
    updateQueryPreview() {
        const username = document.getElementById('sql-username')?.value || '[username]';
        const password = document.getElementById('sql-password')?.value || '[password]';
        const preview = document.getElementById('sql-query-preview');
        
        if (preview) {
            const query = `SELECT * FROM users WHERE username = '${username}' AND password = '${password}'`;
            preview.textContent = query;
            
            // Highlight potential injection
            if (username.includes("'") || password.includes("'") || 
                username.toLowerCase().includes('or') || password.toLowerCase().includes('or')) {
                preview.parentElement.classList.add('border-red-400', 'bg-red-50');
            } else {
                preview.parentElement.classList.remove('border-red-400', 'bg-red-50');
            }
        }
    },
    
    // Update query preview for direct input
    updateDirectQueryPreview() {
        const payload = document.getElementById('sql-payload')?.value || '[payload]';
        const preview = document.getElementById('sql-query-preview');
        
        if (preview) {
            const query = `SELECT * FROM users WHERE username = '${payload}' AND password = 'password'`;
            preview.textContent = query;
        }
    },
    
    // Use predefined payload
    usePayload(payload) {
        const usernameInput = document.getElementById('sql-username');
        const payloadInput = document.getElementById('sql-payload');
        
        if (usernameInput) {
            usernameInput.value = payload;
            this.updateQueryPreview();
        }
        
        if (payloadInput) {
            payloadInput.value = payload;
            this.updateDirectQueryPreview();
        }
    },
    
    // Attempt login with form inputs
    attemptLogin() {
        const username = document.getElementById('sql-username')?.value || '';
        const password = document.getElementById('sql-password')?.value || '';
        
        if (!username && !password) {
            this.displayResults('Error: Please enter username and password', 'error');
            return;
        }
        
        const query = `SELECT * FROM users WHERE username = '${username}' AND password = '${password}'`;
        this.executeSQLQuery(query, username, password);
    },
    
    // Execute payload directly
    executePayload() {
        const payload = document.getElementById('sql-payload')?.value || '';
        
        if (!payload) {
            this.displayResults('Error: Please enter a SQL payload', 'error');
            return;
        }
        
        const query = `SELECT * FROM users WHERE username = '${payload}' AND password = 'password'`;
        this.executeSQLQuery(query, payload, 'password');
    },
    
    // Execute SQL query against simulated database
    executeSQLQuery(query, username, password) {
        SecureTrainer.Performance.startTiming('sql-query');
        
        try {
            this.displayResults('Executing query...', 'info');
            
            // Simulate query execution delay
            setTimeout(() => {
                const result = this.simulateSQLExecution(query, username, password);
                this.displayResults(result.output, result.type);
                
                // Track analytics
                SecureTrainer.Analytics.trackEvent('sql_injection_attempt', {
                    query: query,
                    success: result.success,
                    technique: this.detectInjectionTechnique(username, password)
                });
                
                SecureTrainer.Performance.endTiming('sql-query');
            }, 500);
            
        } catch (error) {
            this.displayResults(`Database Error: ${error.message}`, 'error');
        }
    },
    
    // Simulate SQL execution
    simulateSQLExecution(query, username, password) {
        // Check for basic SQL injection patterns
        const isInjection = this.detectSQLInjection(username, password);
        
        if (isInjection.detected) {
            return this.handleSQLInjection(query, isInjection);
        } else {
            return this.handleNormalQuery(username, password);
        }
    },
    
    // Detect SQL injection attempts
    detectSQLInjection(username, password) {
        const input = (username + ' ' + password).toLowerCase();
        
        // Check for common injection patterns
        const patterns = {
            authentication_bypass: /('\\s*or\\s*'1'\\s*=\\s*'1'|'\\s*or\\s*1\\s*=\\s*1|'\\s*or\\s*true)/,
            comment_injection: /(--|#|\/\\*)/,
            union_attack: /union\\s+select/,
            boolean_blind: /('\\s*and\\s*1\\s*=\\s*1|'\\s*and\\s*1\\s*=\\s*2)/,
            time_based: /(sleep\\(|waitfor\\s+delay|benchmark\\()/,
            error_based: /(extractvalue\\(|updatexml\\(|exp\\()/
        };
        
        for (const [technique, pattern] of Object.entries(patterns)) {
            if (pattern.test(input)) {
                return {
                    detected: true,
                    technique: technique,
                    pattern: pattern
                };
            }
        }
        
        // Check for quote-based injection
        if (input.includes("'") && !input.match(/^[a-zA-Z0-9\\s]*$/)) {
            return {
                detected: true,
                technique: 'quote_injection',
                pattern: /'/
            };
        }
        
        return { detected: false };
    },
    
    // Handle SQL injection attempts
    handleSQLInjection(query, injection) {
        const technique = injection.technique;
        
        switch (technique) {
            case 'authentication_bypass':
                return {
                    success: true,
                    type: 'success',
                    output: this.formatSuccessfulBypass()
                };
                
            case 'union_attack':
                return {
                    success: true,
                    type: 'success',
                    output: this.formatUnionAttackResult()
                };
                
            case 'comment_injection':
                return {
                    success: true,
                    type: 'success',
                    output: this.formatCommentInjectionResult()
                };
                
            case 'quote_injection':
                return {
                    success: false,
                    type: 'error',
                    output: this.formatSQLError()
                };
                
            default:
                return {
                    success: true,
                    type: 'warning',
                    output: `SQL injection detected (${technique}) but query execution blocked by security measures.`
                };
        }
    },
    
    // Handle normal queries
    handleNormalQuery(username, password) {
        // Look for exact matches
        const user = this.vulnerableDatabase.users.find(u => 
            u.username === username && u.password === password
        );
        
        if (user) {
            return {
                success: true,
                type: 'info',
                output: `Login successful! Welcome ${user.username} (${user.role})`
            };
        } else {
            return {
                success: false,
                type: 'error',
                output: 'Invalid username or password'
            };
        }
    },
    
    // Format successful bypass result
    formatSuccessfulBypass() {
        const users = this.vulnerableDatabase.users;
        let output = '🎯 SQL Injection Successful! Authentication bypassed.\\n\\n';
        output += 'Retrieved user data:\\n';
        output += '| ID | Username | Role | Email |\\n';
        output += '|----|----------|------|-------|\\n';
        
        users.forEach(user => {
            output += `| ${user.id} | ${user.username} | ${user.role} | ${user.email} |\\n`;
        });
        
        output += '\\n✅ Challenge completed! You successfully bypassed authentication.';
        output += '\\n💡 In real applications, this would grant unauthorized access.';
        
        return output;
    },
    
    // Format UNION attack result
    formatUnionAttackResult() {
        let output = '🎯 UNION SQL Injection Successful!\\n\\n';
        output += 'Database schema information extracted:\\n';
        output += 'Tables: users, products, orders\\n';
        output += 'Columns in users: id, username, password, role, email\\n\\n';
        
        output += 'Sample extracted data:\\n';
        this.vulnerableDatabase.users.slice(0, 3).forEach(user => {
            output += `${user.id} | ${user.username} | ${user.password} | ${user.role}\\n`;
        });
        
        output += '\\n✅ Challenge completed! You successfully extracted data using UNION.';
        
        return output;
    },
    
    // Format comment injection result
    formatCommentInjectionResult() {
        let output = '🎯 Comment-based SQL Injection Successful!\\n\\n';
        output += 'Query execution modified using comment syntax.\\n';
        output += 'Password check bypassed using -- comment.\\n\\n';
        
        output += 'Logged in as: admin (administrator)\\n';
        output += '\\n✅ Challenge completed! You used SQL comments to bypass authentication.';
        
        return output;
    },
    
    // Format SQL error
    formatSQLError() {
        const errors = [
            "You have an error in your SQL syntax; check the manual that corresponds to your MySQL server version for the right syntax to use near ''1'='1' at line 1",
            "Unclosed quotation mark after the character string '.",
            "Invalid column name '1'.",
            "Syntax error in SQL statement."
        ];
        
        const randomError = errors[Math.floor(Math.random() * errors.length)];
        
        return `❌ Database Error: ${randomError}\\n\\n💡 This error reveals information about the database structure. Try refining your payload.`;
    },
    
    // Detect injection technique
    detectInjectionTechnique(username, password) {
        const input = (username + ' ' + password).toLowerCase();
        
        if (input.includes("or '1'='1'") || input.includes("or 1=1")) {
            return 'authentication_bypass';
        } else if (input.includes('union select')) {
            return 'union_attack';
        } else if (input.includes('--') || input.includes('#')) {
            return 'comment_injection';
        } else if (input.includes("'")) {
            return 'quote_injection';
        } else {
            return 'normal_query';
        }
    },
    
    // Display results in terminal
    displayResults(output, type) {
        const resultsContainer = document.getElementById('sql-results');
        if (!resultsContainer) return;
        
        const timestamp = new Date().toLocaleTimeString();
        const typeColors = {
            success: 'text-green-400',
            error: 'text-red-400',
            warning: 'text-yellow-400',
            info: 'text-blue-400'
        };
        
        const colorClass = typeColors[type] || 'text-gray-300';
        
        resultsContainer.innerHTML = `
            <div class="terminal-content">
                <div class="text-gray-400">[${timestamp}] Query executed</div>
                <div class="${colorClass} mt-2 whitespace-pre-line">${output}</div>
            </div>
        `;
        
        // Auto-scroll to bottom
        resultsContainer.scrollTop = resultsContainer.scrollHeight;
        
        // Show success celebration if injection was successful
        if (type === 'success' && output.includes('successful')) {
            setTimeout(() => {
                SecureTrainer.Progress.celebrateSuccess();
            }, 500);
        }
    }
};

// Auto-initialize when SecureTrainer is available
if (typeof SecureTrainer !== 'undefined') {
    SecureTrainer.Challenges.SQL.init();
    console.log('🗃️ SQL Injection challenge interface loaded');
} else {
    console.warn('SecureTrainer not available, SQL interface will be initialized when challenges load');
}