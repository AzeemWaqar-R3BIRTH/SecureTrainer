/**
 * SecureTrainer Challenge Handler - Clean Production Version
 * Handles challenge loading, submission, and user interaction
 * Version: 2.1
 */

// Global challenge state
window.SecureTrainerChallenges = {
    currentChallenge: null,
    currentUser: null,
    hintCount: 0,
    isLoading: false,
    challengeCompleted: false,

    // Add CSS classes for better visual feedback
    addVisualStyles() {
        if (document.getElementById('challenge-styles')) return; // Avoid duplicates

        const styles = document.createElement('style');
        styles.id = 'challenge-styles';
        styles.textContent = `
            .difficulty-beginner { background-color: #dcfce7 !important; color: #166534 !important; }
            .difficulty-intermediate { background-color: #fef3c7 !important; color: #92400e !important; }
            .difficulty-advanced { background-color: #fecaca !important; color: #991b1b !important; }
            .difficulty-demo { background-color: #e0e7ff !important; color: #3730a3 !important; }
            
            .challenge-message {
                animation: slideInFromRight 0.3s ease-out;
                z-index: 9999;
            }
            
            @keyframes slideInFromRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            
            .loading-spinner {
                animation: spin 1s linear infinite;
            }
            
            @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
        `;
        document.head.appendChild(styles);
    },

    // Initialize the challenge system
    init() {
        this.loadUserData();
        this.setupChallengeButtons();
        this.setupEventHandlers();
        this.addVisualStyles();
        this.setupNetworkErrorHandling();
    },

    // Setup network error handling
    setupNetworkErrorHandling() {
        // Listen for network connectivity changes
        window.addEventListener('online', () => {
            this.showMessage('Connection restored!', 'success');
        });

        window.addEventListener('offline', () => {
            this.showMessage('Connection lost. Challenges will use demo mode.', 'warning');
        });

        // Global error handler for unhandled promise rejections
        window.addEventListener('unhandledrejection', (event) => {
            this.showMessage('An unexpected error occurred. Please try again.', 'error');
        });
    },

    // Load user data from multiple sources
    loadUserData() {
        // Try embedded user data first
        const userDataScript = document.getElementById('user-data');
        if (userDataScript && userDataScript.textContent && userDataScript.textContent.trim() !== 'null') {
            try {
                this.currentUser = JSON.parse(userDataScript.textContent);
                return;
            } catch (e) {
                // Fallback to storage data
            }
        }

        // Fallback to localStorage/sessionStorage
        const storedData = localStorage.getItem('userData') ||
            sessionStorage.getItem('userData') ||
            sessionStorage.getItem('user');

        if (storedData) {
            try {
                this.currentUser = JSON.parse(storedData);
            } catch (e) {
                // Silent fallback - user may need to log in
            }
        }
    },

    // Setup challenge category buttons with proper event handlers
    setupChallengeButtons() {
        // Find all challenge buttons with onclick attributes
        const buttons = document.querySelectorAll('button[onclick*="startChallengeCategory"]');

        buttons.forEach(button => {
            // Extract category from onclick attribute
            const onclickAttr = button.getAttribute('onclick');
            const categoryMatch = onclickAttr?.match(/startChallengeCategory\(['"]([^'"]+)['"]\)/);

            if (categoryMatch) {
                const category = categoryMatch[1];

                // Remove original onclick to prevent conflicts
                button.removeAttribute('onclick');

                // Add new event listener with proper error handling
                button.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    this.startChallengeCategory(category, button);
                });
            }
        });
    },

    // Setup global event handlers
    setupEventHandlers() {
        // Handle browser back button
        window.addEventListener('popstate', () => {
            this.backToChallenges();
        });

        // Handle escape key to go back
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.currentChallenge) {
                this.backToChallenges();
            }
        });
    },

    // Main function to start a challenge category
    async startChallengeCategory(category, buttonElement = null) {
        // Prevent multiple simultaneous requests
        if (this.isLoading) {
            return;
        }

        // Check user authentication
        if (!this.currentUser) {
            this.showMessage('Please log in to start challenges.', 'error');
            setTimeout(() => {
                window.location.href = '/login';
            }, 2000);
            return;
        }

        const userId = this.currentUser.user_id || this.currentUser.id || this.currentUser._id;
        if (!userId) {
            this.showMessage('User ID not found. Please log in again.', 'error');
            return;
        }

        // Set loading state
        this.isLoading = true;
        this.setButtonLoadingState(buttonElement, true);
        this.showMessage(`Loading ${category.replace('_', ' ')} challenge...`, 'info');

        try {
            // Make API call to start challenge
            const response = await fetch(`/api/challenges/start/${userId}?category=${category}`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.success && data.challenge) {
                this.loadChallenge(data.challenge);
                this.showMessage('Challenge loaded successfully!', 'success');
            } else {
                throw new Error(data.error || 'Failed to load challenge data');
            }

        } catch (error) {
            this.showMessage(`Error: ${error.message}`, 'error');

            // Fallback to demo challenge
            setTimeout(() => {
                this.loadDemoChallenge(category);
            }, 1000);

        } finally {
            // Reset loading state
            this.isLoading = false;
            this.setButtonLoadingState(buttonElement, false);
        }
    },

    // Load challenge data and display interface
    loadChallenge(challengeData) {
        console.log('Challenge Data Loaded:', challengeData);
        console.log('Hide Payload Flag:', challengeData.hide_payload);
        this.currentChallenge = challengeData;
        this.hintCount = 0;

        // Hide challenge categories grid
        this.hideChallengeGrid();

        // Show challenge interface
        this.showChallengeInterface();

        // Update challenge display
        this.updateChallengeDisplay(challengeData);

        // Create challenge interface
        this.createChallengeInterface(challengeData);
    },

    // Hide the challenge categories grid
    hideChallengeGrid() {
        const categoryGrid = document.querySelector('main .grid');
        if (categoryGrid) {
            categoryGrid.style.display = 'none';
        }

        // Also hide the header if it exists
        const header = document.querySelector('.bg-gradient-to-r.from-blue-600');
        if (header) {
            header.style.display = 'none';
        }
    },

    // Show the challenge interface
    showChallengeInterface() {
        const challengeSection = document.getElementById('current-challenge-section');
        if (challengeSection) {
            challengeSection.classList.remove('hidden');
            challengeSection.style.display = 'block';

            // Scroll to top to ensure challenge is visible
            challengeSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    },

    // Update challenge display elements safely
    updateChallengeDisplay(challengeData) {
        const elements = {
            'challenge-title': (challengeData.category || 'Unknown') + ' Challenge',
            'challenge-difficulty': challengeData.difficulty || 'Intermediate',
            'challenge-points': (challengeData.score_weight || 10) * 10,
            'challenge-scenario': challengeData.scenario || 'Challenge scenario',
            'challenge-question': challengeData.question || 'Challenge question'
        };

        Object.entries(elements).forEach(([id, content]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = content;
            }
        });

        // Update difficulty badge styling
        const difficultyEl = document.getElementById('challenge-difficulty');
        if (difficultyEl) {
            const difficulty = (challengeData.difficulty || 'intermediate').toLowerCase();
            difficultyEl.className = `ml-1 px-2 py-1 rounded bg-blue-100 text-blue-800 difficulty-${difficulty}`;
        }
    },

    // Create the challenge interface
    createChallengeInterface(challengeData) {
        const interfaceEl = document.getElementById('challenge-interface');
        if (!interfaceEl) return;

        const safePayload = this.escapeHtml(challengeData.payload || 'No payload provided');

        interfaceEl.innerHTML = `
            <div class="bg-white rounded-lg border border-gray-200 p-6">
                <!-- AI Insight Card -->
                <div class="mb-6 bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-100 rounded-lg p-4">
                    <div class="flex items-start">
                        <div class="flex-shrink-0">
                            <div class="bg-indigo-100 rounded-full p-2">
                                <i class="fas fa-robot text-indigo-600 text-xl"></i>
                            </div>
                        </div>
                        <div class="ml-4 flex-1">
                            <h4 class="text-sm font-bold text-indigo-900 uppercase tracking-wide mb-1">AI Insight</h4>
                            <p class="text-sm text-indigo-800 mb-2">${challengeData.ai_insights ? challengeData.ai_insights.reason : 'Recommended for your skill level.'}</p>
                            
                            <div class="flex items-center mt-2">
                                <div class="flex items-center mr-4">
                                    <span class="text-xs font-medium text-gray-500 mr-2">Success Probability:</span>
                                    <div class="w-24 bg-gray-200 rounded-full h-2.5">
                                        <div class="bg-indigo-600 h-2.5 rounded-full" style="width: ${challengeData.ai_insights ? challengeData.ai_insights.confidence_score : 50}%"></div>
                                    </div>
                                    <span class="ml-2 text-xs font-bold text-indigo-700">${challengeData.ai_insights ? challengeData.ai_insights.confidence_score : 50}%</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                <h3 class="text-lg font-semibold mb-4">Challenge Workspace</h3>
                
                ${!challengeData.hide_payload && !challengeData.id.startsWith('auth_') && !challengeData.id.startsWith('csrf_') ? `
                <div class="mb-4">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Payload to Analyze:</label>
                    <div class="bg-gray-100 p-3 rounded border font-mono text-sm break-all">
                        ${safePayload}
                    </div>
                </div>
                ` : ''}
                
                <div class="mb-6">
                    <label class="block text-sm font-medium text-gray-700 mb-2">Your Analysis:</label>
                    <textarea 
                        id="user-answer" 
                        class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500" 
                        rows="4" 
                        placeholder="Explain what this payload does and how the attack works..."
                    ></textarea>
                </div>
                
                <div class="flex space-x-4 mb-4">
                    <button id="hint-button" class="bg-yellow-500 hover:bg-yellow-600 text-white py-2 px-4 rounded-md transition-colors">
                        <i class="fas fa-lightbulb mr-2"></i>Get Hint
                    </button>
                    <button id="submit-button" class="bg-green-600 hover:bg-green-700 text-white py-2 px-6 rounded-md transition-colors">
                        <i class="fas fa-check mr-2"></i>Submit Answer
                    </button>
                </div>
                
                <div id="hint-display" class="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-md" style="display: none;">
                    <h4 class="font-medium text-yellow-800 mb-2">💡 Hint:</h4>
                    <p class="text-yellow-700" id="hint-text"></p>
                </div>
            </div>
        `;

        // Setup button event listeners
        this.setupChallengeButtons();
    },

    // Setup challenge interface buttons
    setupChallengeButtons() {
        const submitBtn = document.getElementById('submit-button');
        const hintBtn = document.getElementById('hint-button');

        if (submitBtn) {
            submitBtn.addEventListener('click', () => this.submitAnswer());
        }

        if (hintBtn) {
            hintBtn.addEventListener('click', () => this.showHint());
        }
    },

    // Submit challenge answer
    async submitAnswer() {
        if (!this.currentChallenge || !this.currentUser) {
            this.showMessage('Challenge or user data missing', 'error');
            return;
        }

        const answerEl = document.getElementById('user-answer');
        if (!answerEl) {
            this.showMessage('Answer field not found', 'error');
            return;
        }

        const answer = answerEl.value.trim();
        if (!answer) {
            this.showMessage('Please provide an answer before submitting.', 'warning');
            answerEl.focus();
            return;
        }

        const submitBtn = document.getElementById('submit-button');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Submitting...';
        }

        try {
            const userId = this.currentUser.id || this.currentUser.user_id || this.currentUser._id;

            const response = await fetch(`/api/challenges/submit/${userId}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin',
                body: JSON.stringify({
                    challenge_id: this.currentChallenge.id,
                    answer: answer
                })
            });

            const data = await response.json();

            if (data.success) {
                if (data.correct) {
                    this.showMessage(`🎉 Correct! You earned ${data.score_earned || 0} points!`, 'success');
                    this.challengeCompleted = true;
                    
                    // KEEP BUTTON DISABLED - challenge completed
                    if (submitBtn) {
                        submitBtn.disabled = true;
                        submitBtn.innerHTML = '<i class="fas fa-check mr-2"></i>Challenge Completed!';
                        submitBtn.classList.add('opacity-50', 'cursor-not-allowed');
                    }
                    
                    // Disable answer input
                    if (answerEl) {
                        answerEl.disabled = true;
                    }
                    
                    return; // Don't re-enable button
                } else {
                    this.showMessage(data.feedback || '❌ Incorrect answer. Try again!', 'warning');
                }
            } else {
                // Check if already completed
                if (data.already_completed) {
                    this.showMessage(data.feedback || 'Challenge already completed!', 'info');
                    this.challengeCompleted = true;
                    
                    // Keep button disabled
                    if (submitBtn) {
                        submitBtn.disabled = true;
                        submitBtn.innerHTML = '<i class="fas fa-check mr-2"></i>Already Completed';
                        submitBtn.classList.add('opacity-50', 'cursor-not-allowed');
                    }
                    
                    if (answerEl) {
                        answerEl.disabled = true;
                    }
                    
                    return; // Don't re-enable button
                }
                
                this.showMessage(data.error || 'Failed to submit answer', 'error');
            }

        } catch (error) {
            this.showMessage('Error submitting answer. Please try again.', 'error');

        } finally {
            // Only re-enable if challenge NOT completed
            if (submitBtn && !this.challengeCompleted) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-check mr-2"></i>Submit Answer';
            }
        }
    },

    // Show hint for current challenge with AI adaptation
    async showHint() {
        if (!this.currentChallenge) return;

        const hintDisplay = document.getElementById('hint-display');
        const hintText = document.getElementById('hint-text');
        const hintBtn = document.getElementById('hint-button');

        if (!hintDisplay || !hintText) return;

        // Toggle off if already visible
        if (hintDisplay.style.display !== 'none') {
            hintDisplay.style.display = 'none';
            return;
        }

        // Set loading state
        if (hintBtn) {
            const originalText = hintBtn.innerHTML;
            hintBtn.disabled = true;
            hintBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Thinking...';

            try {
                const userId = this.currentUser.id || this.currentUser.user_id || this.currentUser._id;

                // Call AI Hint API
                const response = await fetch(`/api/challenges/hint/${this.currentChallenge.id}`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ user_id: userId })
                });

                if (!response.ok) throw new Error('Failed to generate hint');

                const data = await response.json();

                if (data.success) {
                    hintText.textContent = data.hint;
                    this.hintCount = data.hint_number;
                    hintDisplay.style.display = 'block';

                    // Show penalty warning if applicable
                    if (data.hint_penalty > 0) {
                        this.showMessage(`Hint used! Score penalty: -${data.hint_penalty} points`, 'info');
                    }
                } else {
                    throw new Error(data.error || 'Unknown error');
                }

            } catch (error) {
                console.error('Hint generation error:', error);
                // Fallback to static hint
                hintText.textContent = this.currentChallenge.hint || 'Think about the vulnerability type and how it can be exploited.';
                hintDisplay.style.display = 'block';
                this.showMessage('Using offline hint (AI unavailable)', 'warning');
            } finally {
                // Reset button
                if (hintBtn) {
                    hintBtn.disabled = false;
                    hintBtn.innerHTML = originalText;
                }
            }
        }
    },

    // Load demo challenge as fallback with enhanced error handling
    loadDemoChallenge(category) {
        const demoChallenge = window.DEMO_CONFIG ?
            window.DEMO_CONFIG.getDemoChallenge(category) :
            this.createBasicDemo(category);

        this.loadChallenge(demoChallenge);
        this.showMessage('Demo challenge loaded! This is a simulated environment for learning.', 'info');
    },

    // Fallback demo creation if config not loaded
    createBasicDemo(category) {
        return {
            id: category + '_demo_' + Date.now(),
            category: category.replace('_', ' ').toUpperCase(),
            difficulty: 'Demo',
            scenario: `This is a demo ${category.replace('_', ' ')} challenge.`,
            question: `Analyze this ${category.replace('_', ' ')} vulnerability.`,
            payload: 'demo payload',
            hint: 'Consider the attack vector and potential defenses.',
            score_weight: 10,
            type: category
        };
    },

    // Go back to challenge selection
    backToChallenges() {
        // Check if we need to reload to update progress
        if (this.challengeCompleted) {
            window.location.reload();
            return;
        }

        // Hide challenge interface
        const challengeSection = document.getElementById('current-challenge-section');
        if (challengeSection) {
            challengeSection.classList.add('hidden');
            challengeSection.style.display = 'none';
        }

        // Show category grid
        const categoryGrid = document.querySelector('main .grid');
        if (categoryGrid) {
            categoryGrid.style.display = 'grid';
        }

        // Show header
        const header = document.querySelector('.bg-gradient-to-r.from-blue-600');
        if (header) {
            header.style.display = 'block';
        }

        // Reset state
        this.currentChallenge = null;
        this.hintCount = 0;
        this.challengeCompleted = false;

        this.showMessage('Returned to challenge selection', 'info');
    },

    // Set button loading state
    setButtonLoadingState(button, loading) {
        if (!button) return;

        if (loading) {
            button.disabled = true;
            button.dataset.originalText = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Loading...';
        } else {
            button.disabled = false;
            if (button.dataset.originalText) {
                button.innerHTML = button.dataset.originalText;
                delete button.dataset.originalText;
            }
        }
    },

    // Show message to user
    showMessage(message, type = 'info') {
        // Remove existing messages
        const existingMessage = document.querySelector('.challenge-message');
        if (existingMessage) {
            existingMessage.remove();
        }

        // Create message
        const messageEl = document.createElement('div');
        messageEl.className = 'challenge-message fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50';

        const colors = {
            'info': 'bg-blue-500 text-white',
            'success': 'bg-green-500 text-white',
            'error': 'bg-red-500 text-white',
            'warning': 'bg-yellow-500 text-black'
        };

        messageEl.className += ` ${colors[type] || colors.info}`;
        messageEl.textContent = message;

        document.body.appendChild(messageEl);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (messageEl.parentNode) {
                messageEl.remove();
            }
        }, 5000);

        console.log(`${type.toUpperCase()}: ${message}`);
    },

    // Escape HTML to prevent XSS
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
};

// Global function for backward compatibility
window.startChallengeCategory = function (category) {
    window.SecureTrainerChallenges.startChallengeCategory(category);
};

window.backToChallenges = function () {
    window.SecureTrainerChallenges.backToChallenges();
};

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.SecureTrainerChallenges.init();
    });
} else {
    window.SecureTrainerChallenges.init();
}

