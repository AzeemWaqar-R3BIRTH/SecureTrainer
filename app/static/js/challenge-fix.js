/**
 * Simple Challenge Fix - Frontend functionality for SecureTrainer challenges
 * This file provides a clean, working implementation of challenge functionality
 */

// Global variables
let currentChallenge = null;
let currentUser = null;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎯 Challenge Fix loaded');
    initializeChallenges();
});

function initializeChallenges() {
    // Load user data
    loadUserData();
    
    // Set up challenge category buttons
    setupChallengeButtons();
    
    // Set up other UI elements
    setupUI();
}

function loadUserData() {
    // Try multiple sources for user data
    const userData = localStorage.getItem('userData') || 
                    sessionStorage.getItem('user') || 
                    sessionStorage.getItem('userData');
    
    if (userData) {
        try {
            currentUser = JSON.parse(userData);
            console.log('User loaded:', currentUser.username || currentUser.email);
        } catch (e) {
            console.warn('Could not parse user data:', e);
        }
    }
    
    // Also try to get from server-rendered data
    const userDataScript = document.getElementById('user-data');
    if (userDataScript && userDataScript.textContent) {
        try {
            const serverUser = JSON.parse(userDataScript.textContent);
            if (serverUser) {
                currentUser = serverUser;
                console.log('User loaded from server:', currentUser.username);
            }
        } catch (e) {
            console.warn('Could not parse server user data:', e);
        }
    }
}

function setupChallengeButtons() {
    // Find all challenge category buttons and add click handlers
    const buttons = document.querySelectorAll('button[onclick*="startChallengeCategory"]');
    
    buttons.forEach(button => {
        // Remove existing onclick
        button.removeAttribute('onclick');
        
        // Add new event listener
        button.addEventListener('click', function() {
            const category = extractCategoryFromButton(button);
            if (category) {
                startChallengeCategory(category);
            }
        });
    });
}

function extractCategoryFromButton(button) {
    // Extract category from button text or other attributes
    const buttonText = button.textContent.toLowerCase();
    
    if (buttonText.includes('sql')) return 'sql_injection';
    if (buttonText.includes('xss') || buttonText.includes('scripting')) return 'xss';
    if (buttonText.includes('command') || buttonText.includes('injection')) return 'command_injection';
    if (buttonText.includes('auth')) return 'authentication';
    if (buttonText.includes('csrf')) return 'csrf';
    
    return null;
}

function setupUI() {
    // Add message container if it doesn't exist
    if (!document.getElementById('message-container')) {
        const container = document.createElement('div');
        container.id = 'message-container';
        container.className = 'fixed top-4 right-4 z-50';
        document.body.appendChild(container);
    }
}

function startChallengeCategory(category) {
    console.log(`🎯 Starting ${category} challenges`);
    
    // Show loading message
    showMessage(`Loading ${category.replace('_', ' ')} challenge...`, 'info');
    
    // Check if user is logged in
    if (!currentUser || !currentUser.id) {
        showMessage('Please log in to start challenges.', 'error');
        setTimeout(() => {
            window.location.href = '/login';
        }, 2000);
        return;
    }
    
    // Make API call to start challenge
    const userId = currentUser.id || currentUser.user_id || currentUser._id;
    
    fetch(`/api/challenges/start/${userId}?category=${category}`, {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin'
    })
    .then(response => {
        console.log('API Response status:', response.status);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        console.log('Challenge data received:', data);
        
        if (data.success && data.challenge) {
            showMessage('Challenge loaded successfully!', 'success');
            loadChallenge(data.challenge);
        } else if (data.all_completed) {
            // User has completed all challenges in this category
            showMessage(data.message || '🎉 All challenges completed!', 'success');
            
            // Show completion message in the challenge area
            const challengeArea = document.getElementById('challenge-area');
            if (challengeArea) {
                challengeArea.innerHTML = `
                    <div class="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg shadow-lg p-8 text-center">
                        <div class="text-6xl mb-4">🎉</div>
                        <h2 class="text-3xl font-bold text-gray-800 mb-4">Congratulations!</h2>
                        <p class="text-xl text-gray-700 mb-6">${data.message}</p>
                        <div class="bg-white rounded-lg p-6 mb-6 inline-block">
                            <p class="text-lg text-gray-600 mb-2">Challenges Completed</p>
                            <p class="text-5xl font-bold text-green-600">${data.completed_count || 0}</p>
                        </div>
                        <div class="flex gap-4 justify-center">
                            <a href="/challenges" class="bg-blue-600 hover:bg-blue-700 text-white font-semibold px-6 py-3 rounded-lg transition duration-200">
                                Try Another Category
                            </a>
                            <a href="/dashboard" class="bg-gray-600 hover:bg-gray-700 text-white font-semibold px-6 py-3 rounded-lg transition duration-200">
                                View Dashboard
                            </a>
                        </div>
                    </div>
                `;
            }
            return; // Stop execution here
        } else {
            throw new Error(data.error || 'Failed to load challenge');
        }
    })
    .catch(error => {
        console.error('Error starting challenge:', error);
        showMessage(`Error: ${error.message}`, 'error');
        
        // Fallback to demo challenge
        console.log('Loading demo challenge as fallback...');
        loadDemoChallenge(category);
    });
}

function loadChallenge(challengeData) {
    currentChallenge = challengeData;
    
    // Debug: Log the challenge data to see what's included
    console.log('📝 Challenge loaded:', {
        id: challengeData.id,
        category: challengeData.category,
        difficulty: challengeData.difficulty,
        hasHint: !!challengeData.hint,
        hint: challengeData.hint,
        hintLength: challengeData.hint ? challengeData.hint.length : 0
    });
    
    // Hide challenge categories
    const categoriesSection = document.querySelector('main .grid') || 
                             document.querySelector('.challenge-grid');
    if (categoriesSection) {
        categoriesSection.style.display = 'none';
    }
    
    // Show challenge section
    const challengeSection = document.getElementById('current-challenge-section');
    if (challengeSection) {
        challengeSection.classList.remove('hidden');
        challengeSection.style.display = 'block';
        
        // Update challenge details
        updateChallengeDisplay(challengeData);
    } else {
        // Create challenge section if it doesn't exist
        createChallengeSection(challengeData);
    }
}

function updateChallengeDisplay(challengeData) {
    // Update challenge title - safely
    const titleEl = document.getElementById('challenge-title');
    if (titleEl) {
        titleEl.textContent = (challengeData.category || 'Unknown') + ' Challenge';
    }
    
    // Update difficulty - safely
    const difficultyEl = document.getElementById('challenge-difficulty');
    if (difficultyEl) {
        difficultyEl.textContent = challengeData.difficulty || 'Intermediate';
    }
    
    // Update scenario - safely (prevent HTML injection)
    const scenarioEl = document.getElementById('challenge-scenario');
    if (scenarioEl) {
        scenarioEl.textContent = challengeData.scenario || 'Challenge scenario';
    }
    
    // Update question - safely (prevent HTML injection)
    const questionEl = document.getElementById('challenge-question');
    if (questionEl) {
        questionEl.textContent = challengeData.question || 'Challenge question';
    }
    
    // Update points with range
    const pointsEl = document.getElementById('challenge-points');
    if (pointsEl) {
        const baseScore = (challengeData.score_weight || 10);
        const difficultyMultipliers = {
            'beginner': 1.0,
            'intermediate': 1.5,
            'advanced': 2.2,
            'expert': 3.0
        };
        const difficulty = (challengeData.difficulty || 'intermediate').toLowerCase();
        const diffMultiplier = difficultyMultipliers[difficulty] || 1.5;
        const minScore = Math.round(baseScore * diffMultiplier * 0.3);
        const maxScore = Math.round(baseScore * diffMultiplier * 3.5);
        pointsEl.textContent = `${minScore}-${maxScore}`;
    }
    
    // Create challenge interface
    createChallengeInterface(challengeData);
}

function createChallengeInterface(challengeData) {
    const interfaceEl = document.getElementById('challenge-interface');
    if (!interfaceEl) return;
    
    const category = challengeData.type || challengeData.category;
    
    // Always use basic interface to prevent XSS from demo HTML
    interfaceEl.innerHTML = createBasicInterface(challengeData);
    
    // Add submit button functionality
    setupSubmitButton();
}

function createBasicInterface(challengeData) {
    // Safely escape any HTML/JS content to prevent XSS
    const safePayload = escapeHtml(challengeData.payload || 'No payload provided');
    
    return `
        <div class="bg-white rounded-lg shadow-md p-6">
            <h3 class="text-lg font-semibold mb-4">Challenge Workspace</h3>
            
            <div class="mb-4">
                <label class="block text-sm font-medium mb-2">Payload:</label>
                <div class="bg-gray-100 p-3 rounded border font-mono text-sm">
                    ${safePayload}
                </div>
            </div>
            
            <div class="mb-4">
                <label class="block text-sm font-medium mb-2">Your Analysis:</label>
                <textarea 
                    id="user-answer" 
                    class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" 
                    rows="4" 
                    placeholder="Explain what this payload does and how it works..."></textarea>
            </div>
            
            <div class="flex space-x-4">
                <button id="hint-button" class="bg-yellow-500 hover:bg-yellow-600 text-white py-2 px-4 rounded-md">
                    Get Hint
                </button>
                <button id="submit-button" class="bg-green-600 hover:bg-green-700 text-white py-2 px-6 rounded-md">
                    Submit Answer
                </button>
            </div>
            
            <div id="hint-display" class="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-md" style="display: none; max-width: 100%; width: 100%;">
                <h4 class="font-medium text-yellow-800 mb-2">
                    <i class="fas fa-lightbulb mr-2"></i>💡 Hint:
                </h4>
                <p class="text-yellow-700 whitespace-pre-wrap break-words overflow-wrap-anywhere" id="hint-text" style="word-wrap: break-word; overflow-wrap: break-word; white-space: pre-wrap; max-width: 100%; text-overflow: clip; overflow: visible;"></p>
            </div>
        </div>
    `;
}

function setupSubmitButton() {
    const submitBtn = document.getElementById('submit-button');
    const hintBtn = document.getElementById('hint-button');
    
    if (submitBtn) {
        submitBtn.addEventListener('click', submitAnswer);
    }
    
    if (hintBtn) {
        hintBtn.addEventListener('click', showHint);
    }
}

function submitAnswer() {
    if (!currentChallenge) {
        showMessage('No active challenge', 'error');
        return;
    }
    
    const answerEl = document.getElementById('user-answer');
    if (!answerEl) {
        showMessage('Answer field not found', 'error');
        return;
    }
    
    const answer = answerEl.value.trim();
    if (!answer) {
        showMessage('Please provide an answer before submitting.', 'warning');
        return;
    }
    
    // Make API call to submit answer
    const userId = currentUser.id || currentUser.user_id || currentUser._id;
    
    fetch(`/api/challenges/submit/${userId}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin',
        body: JSON.stringify({
            challenge_id: currentChallenge.id,
            answer: answer
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            if (data.correct) {
                showMessage(`Correct! You earned ${data.score_earned || 0} points!`, 'success');
            } else {
                showMessage(data.feedback || 'Incorrect answer. Try again!', 'warning');
            }
        } else {
            showMessage(data.error || 'Failed to submit answer', 'error');
        }
    })
    .catch(error => {
        console.error('Error submitting answer:', error);
        showMessage('Error submitting answer. Please try again.', 'error');
    });
}

function showHint() {
    if (!currentChallenge) {
        console.error('No challenge loaded');
        return;
    }
    
    const hintDisplay = document.getElementById('hint-display');
    const hintText = document.getElementById('hint-text');
    
    if (!hintDisplay || !hintText) {
        console.error('Hint elements not found');
        return;
    }
    
    if (hintDisplay.style.display === 'none') {
        // Get the hint directly from the challenge (already safe from backend)
        const hint = currentChallenge.hint || 'Think about the vulnerability type and how it can be exploited.';
        console.log('Displaying hint:', hint);
        
        // Set hint text directly (no need for escapeHtml since backend already sanitizes)
        hintText.textContent = hint;
        
        // Force full display with cssText override (equivalent to !important)
        hintText.style.cssText = `
            color: rgb(161, 98, 7);
            overflow: visible !important;
            text-overflow: clip !important;
            white-space: pre-wrap !important;
            word-wrap: break-word !important;
            word-break: break-word !important;
            overflow-wrap: break-word !important;
            display: block !important;
            max-height: none !important;
            height: auto !important;
            max-width: 100% !important;
            -webkit-line-clamp: unset !important;
            line-clamp: unset !important;
        `;
        // Also ensure parent container doesn't constrain
        const hintDisplayClasses = hintDisplay.className;
        hintDisplay.style.cssText = `
            display: block !important;
            max-width: 100% !important;
            width: 100% !important;
            overflow: visible !important;
        `;
        hintDisplay.className = hintDisplayClasses; // Preserve classes
    } else {
        hintDisplay.style.display = 'none';
    }
}

// Utility function to escape HTML and prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function loadDemoChallenge(category) {
    const demoChallenge = {
        id: category + '_demo',
        category: category.replace('_', ' ').toUpperCase(),
        difficulty: 'Demo',
        scenario: `This is a demo ${category.replace('_', ' ')} challenge to help you practice.`,
        question: `What techniques would you use to exploit this ${category.replace('_', ' ')} vulnerability?`,
        payload: getDemoPayload(category),
        hint: `Think about how ${category.replace('_', ' ')} attacks work and what the payload does.`,
        score_weight: 10,
        type: category
    };
    
    showMessage('Demo challenge loaded!', 'info');
    loadChallenge(demoChallenge);
}

function getDemoPayload(category) {
    const payloads = {
        'sql_injection': "' OR '1'='1' --",
        'xss': '<script>alert("XSS")</script>',
        'command_injection': '; ls -la',
        'authentication': 'admin\' --',
        'csrf': 'CSRF demo payload'
    };
    return payloads[category] || 'demo payload';
}

function showMessage(message, type = 'info') {
    const container = document.getElementById('message-container');
    if (!container) return;
    
    // Remove existing messages
    container.innerHTML = '';
    
    const messageEl = document.createElement('div');
    const colors = {
        'info': 'bg-blue-500 text-white',
        'success': 'bg-green-500 text-white',
        'error': 'bg-red-500 text-white',
        'warning': 'bg-yellow-500 text-black'
    };
    
    messageEl.className = `p-4 rounded-lg shadow-lg mb-2 ${colors[type] || colors.info}`;
    messageEl.textContent = message;
    
    container.appendChild(messageEl);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (messageEl.parentNode) {
            messageEl.remove();
        }
    }, 5000);
    
    console.log(`${type.toUpperCase()}: ${message}`);
}

// Export for global access
window.startChallengeCategory = startChallengeCategory;
window.showMessage = showMessage;

console.log('🎯 Challenge Fix script loaded successfully');