/**
 * Real-time Progress Tracking System
 * WebSocket-based live progress updates and analytics
 */

if (!window.SecureTrainer) {
    window.SecureTrainer = {};
}

SecureTrainer.ProgressTracker = {
    websocket: null,
    isConnected: false,
    reconnectAttempts: 0,
    maxReconnectAttempts: 5,
    reconnectDelay: 1000,
    progressData: {},
    listeners: {},

    init() {
        this.connectWebSocket();
        this.setupProgressInterface();
        this.initializeLocalStorage();
    },

    connectWebSocket() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}/ws/progress`;
            
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                console.log('WebSocket connected for progress tracking');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.onConnectionStatusChange(true);
                
                // Send initial progress data
                this.sendProgressUpdate('connection', {
                    type: 'connect',
                    userId: this.getUserId(),
                    timestamp: Date.now()
                });
            };

            this.websocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleProgressMessage(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };

            this.websocket.onclose = () => {
                console.log('WebSocket connection closed');
                this.isConnected = false;
                this.onConnectionStatusChange(false);
                this.scheduleReconnect();
            };

            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.isConnected = false;
                this.onConnectionStatusChange(false);
            };

        } catch (error) {
            console.error('Failed to connect WebSocket:', error);
            this.scheduleReconnect();
        }
    },

    scheduleReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
            
            console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);
            
            setTimeout(() => {
                this.connectWebSocket();
            }, delay);
        } else {
            console.error('Max reconnection attempts reached. Falling back to local storage.');
            this.enableOfflineMode();
        }
    },

    handleProgressMessage(data) {
        switch (data.type) {
            case 'progress_update':
                this.updateProgress(data.challengeType, data.progress);
                break;
            case 'leaderboard_update':
                this.updateLeaderboard(data.leaderboard);
                break;
            case 'achievement_unlocked':
                this.showAchievement(data.achievement);
                break;
            case 'live_stats':
                this.updateLiveStats(data.stats);
                break;
            case 'challenge_completion':
                this.handleChallengeCompletion(data);
                break;
            default:
                console.log('Unknown progress message type:', data.type);
        }
    },

    sendProgressUpdate(type, data) {
        const message = {
            type: type,
            userId: this.getUserId(),
            timestamp: Date.now(),
            ...data
        };

        if (this.isConnected && this.websocket.readyState === WebSocket.OPEN) {
            this.websocket.send(JSON.stringify(message));
        } else {
            // Store in local storage for offline sync
            this.storeOfflineProgress(message);
        }
    },

    setupProgressInterface() {
        // Add progress tracking UI to the page if not exists
        if (!document.getElementById('progress-tracker')) {
            this.createProgressTracker();
        }
        this.updateConnectionStatus();
    },

    createProgressTracker() {
        const tracker = document.createElement('div');
        tracker.id = 'progress-tracker';
        tracker.className = 'fixed bottom-4 right-4 z-50';
        tracker.innerHTML = `
            <div class="progress-tracker-container bg-white shadow-lg rounded-lg border p-4 max-w-sm">
                <div class="flex items-center justify-between mb-3">
                    <h4 class="text-sm font-semibold">Live Progress</h4>
                    <div class="flex items-center">
                        <div id="connection-status" class="w-2 h-2 rounded-full bg-gray-400 mr-2"></div>
                        <button id="toggle-tracker" class="text-gray-500 hover:text-gray-700">
                            <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"></path>
                            </svg>
                        </button>
                    </div>
                </div>
                
                <div id="tracker-content" class="space-y-3">
                    <!-- Overall Progress -->
                    <div class="progress-section">
                        <div class="flex justify-between text-xs mb-1">
                            <span>Overall Progress</span>
                            <span id="overall-percentage">0%</span>
                        </div>
                        <div class="progress-bar h-2">
                            <div id="overall-progress" class="progress-fill h-full" style="width: 0%"></div>
                        </div>
                    </div>

                    <!-- Challenge Progress -->
                    <div class="challenge-progress">
                        <div class="text-xs font-medium mb-2">Challenge Progress:</div>
                        <div id="challenge-list" class="space-y-1">
                            <!-- Dynamic challenge progress items -->
                        </div>
                    </div>

                    <!-- Live Stats -->
                    <div class="live-stats">
                        <div class="text-xs font-medium mb-2">Live Stats:</div>
                        <div class="grid grid-cols-2 gap-2 text-xs">
                            <div class="stat-item">
                                <div class="text-gray-500">Active Users</div>
                                <div id="active-users" class="font-semibold">--</div>
                            </div>
                            <div class="stat-item">
                                <div class="text-gray-500">Completions</div>
                                <div id="total-completions" class="font-semibold">--</div>
                            </div>
                        </div>
                    </div>

                    <!-- Recent Achievements -->
                    <div id="recent-achievements" class="achievements hidden">
                        <!-- Achievement notifications -->
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(tracker);
        this.setupTrackerEvents();
    },

    setupTrackerEvents() {
        const toggleBtn = document.getElementById('toggle-tracker');
        const content = document.getElementById('tracker-content');
        
        if (toggleBtn && content) {
            toggleBtn.addEventListener('click', () => {
                content.classList.toggle('hidden');
            });
        }
    },

    updateConnectionStatus() {
        const statusIndicator = document.getElementById('connection-status');
        if (statusIndicator) {
            statusIndicator.className = `w-2 h-2 rounded-full ${
                this.isConnected ? 'bg-green-400' : 'bg-red-400'
            }`;
            statusIndicator.title = this.isConnected ? 'Connected' : 'Disconnected';
        }
    },

    onConnectionStatusChange(isConnected) {
        this.updateConnectionStatus();
        
        if (isConnected) {
            // Sync any offline progress data
            this.syncOfflineProgress();
        }
    },

    // Challenge Progress Tracking
    trackChallengeProgress(challengeType, progress, score) {
        const progressData = {
            challengeType: challengeType,
            progress: progress,
            score: score,
            timestamp: Date.now()
        };

        // Update local progress
        this.progressData[challengeType] = progressData;
        
        // Send to server
        this.sendProgressUpdate('challenge_progress', progressData);
        
        // Update UI
        this.updateChallengeProgressUI(challengeType, progress, score);
        this.updateOverallProgress();
        
        // Store in localStorage
        this.saveProgressToStorage();
    },

    trackChallengeCompletion(challengeType, finalScore) {
        const completionData = {
            challengeType: challengeType,
            finalScore: finalScore,
            completedAt: Date.now()
        };

        this.sendProgressUpdate('challenge_completion', completionData);
        
        // Check for achievements
        this.checkAchievements(challengeType, finalScore);
    },

    trackLearningProgress(moduleId, progress, timeSpent) {
        const learningData = {
            moduleId: moduleId,
            progress: progress,
            timeSpent: timeSpent,
            timestamp: Date.now()
        };

        this.sendProgressUpdate('learning_progress', learningData);
    },

    updateChallengeProgressUI(challengeType, progress, score) {
        const challengeList = document.getElementById('challenge-list');
        if (!challengeList) return;

        const challengeNames = {
            'sql_injection': 'SQL Injection',
            'xss': 'Cross-Site Scripting',
            'command_injection': 'Command Injection',
            'authentication': 'Authentication'
        };

        let challengeItem = document.getElementById(`challenge-${challengeType}`);
        
        if (!challengeItem) {
            challengeItem = document.createElement('div');
            challengeItem.id = `challenge-${challengeType}`;
            challengeItem.className = 'challenge-progress-item';
            challengeList.appendChild(challengeItem);
        }

        challengeItem.innerHTML = `
            <div class="flex justify-between text-xs mb-1">
                <span>${challengeNames[challengeType] || challengeType}</span>
                <span>${score}/100</span>
            </div>
            <div class="progress-bar h-1">
                <div class="progress-fill h-full bg-blue-500" style="width: ${progress}%"></div>
            </div>
        `;
    },

    updateOverallProgress() {
        const challenges = Object.keys(this.progressData);
        if (challenges.length === 0) return;

        const totalProgress = challenges.reduce((sum, challenge) => {
            return sum + (this.progressData[challenge].progress || 0);
        }, 0);

        const averageProgress = totalProgress / challenges.length;
        
        const overallProgress = document.getElementById('overall-progress');
        const overallPercentage = document.getElementById('overall-percentage');
        
        if (overallProgress && overallPercentage) {
            overallProgress.style.width = averageProgress + '%';
            overallPercentage.textContent = Math.round(averageProgress) + '%';
        }
    },

    updateLiveStats(stats) {
        const activeUsers = document.getElementById('active-users');
        const totalCompletions = document.getElementById('total-completions');

        if (activeUsers) {
            activeUsers.textContent = stats.activeUsers || '--';
        }
        if (totalCompletions) {
            totalCompletions.textContent = stats.totalCompletions || '--';
        }
    },

    // Achievement System
    checkAchievements(challengeType, score) {
        const achievements = [
            {
                id: 'first_completion',
                name: 'First Steps',
                description: 'Complete your first challenge',
                condition: () => true
            },
            {
                id: 'perfect_score',
                name: 'Perfect Score',
                description: 'Score 100 points in a challenge',
                condition: () => score >= 100
            },
            {
                id: 'security_expert',
                name: 'Security Expert',
                description: 'Complete all challenge types',
                condition: () => Object.keys(this.progressData).length >= 4
            }
        ];

        achievements.forEach(achievement => {
            if (achievement.condition() && !this.hasAchievement(achievement.id)) {
                this.unlockAchievement(achievement);
            }
        });
    },

    hasAchievement(achievementId) {
        const achievements = JSON.parse(localStorage.getItem('securetrainer_achievements') || '[]');
        return achievements.includes(achievementId);
    },

    unlockAchievement(achievement) {
        // Store achievement
        const achievements = JSON.parse(localStorage.getItem('securetrainer_achievements') || '[]');
        achievements.push(achievement.id);
        localStorage.setItem('securetrainer_achievements', JSON.stringify(achievements));

        // Show achievement notification
        this.showAchievement(achievement);

        // Send to server
        this.sendProgressUpdate('achievement_unlocked', achievement);
    },

    showAchievement(achievement) {
        const achievementsContainer = document.getElementById('recent-achievements');
        if (!achievementsContainer) return;

        achievementsContainer.classList.remove('hidden');
        
        const achievementElement = document.createElement('div');
        achievementElement.className = 'achievement-notification bg-yellow-50 border border-yellow-200 rounded p-2 mb-2';
        achievementElement.innerHTML = `
            <div class="flex items-center">
                <div class="text-yellow-600 mr-2">🏆</div>
                <div>
                    <div class="text-xs font-semibold text-yellow-800">${achievement.name}</div>
                    <div class="text-xs text-yellow-600">${achievement.description}</div>
                </div>
            </div>
        `;

        achievementsContainer.appendChild(achievementElement);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            achievementElement.remove();
            if (achievementsContainer.children.length === 0) {
                achievementsContainer.classList.add('hidden');
            }
        }, 5000);
    },

    // Offline Support
    enableOfflineMode() {
        console.log('Operating in offline mode - progress will be synced when connection is restored');
        // Could show a notification to user about offline mode
    },

    storeOfflineProgress(data) {
        const offlineData = JSON.parse(localStorage.getItem('securetrainer_offline_progress') || '[]');
        offlineData.push(data);
        localStorage.setItem('securetrainer_offline_progress', JSON.stringify(offlineData));
    },

    syncOfflineProgress() {
        const offlineData = JSON.parse(localStorage.getItem('securetrainer_offline_progress') || '[]');
        
        if (offlineData.length > 0) {
            console.log(`Syncing ${offlineData.length} offline progress updates`);
            
            offlineData.forEach(data => {
                if (this.isConnected && this.websocket.readyState === WebSocket.OPEN) {
                    this.websocket.send(JSON.stringify(data));
                }
            });

            // Clear offline data after sync
            localStorage.removeItem('securetrainer_offline_progress');
        }
    },

    // Local Storage Management
    initializeLocalStorage() {
        const storedProgress = localStorage.getItem('securetrainer_progress');
        if (storedProgress) {
            try {
                this.progressData = JSON.parse(storedProgress);
                this.restoreProgressUI();
            } catch (error) {
                console.error('Error loading stored progress:', error);
            }
        }
    },

    saveProgressToStorage() {
        localStorage.setItem('securetrainer_progress', JSON.stringify(this.progressData));
    },

    restoreProgressUI() {
        Object.keys(this.progressData).forEach(challengeType => {
            const data = this.progressData[challengeType];
            this.updateChallengeProgressUI(challengeType, data.progress, data.score);
        });
        this.updateOverallProgress();
    },

    // Utility Functions
    getUserId() {
        let userId = localStorage.getItem('securetrainer_user_id');
        if (!userId) {
            userId = 'user_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('securetrainer_user_id', userId);
        }
        return userId;
    },

    // Public API for other modules
    addEventListener(event, callback) {
        if (!this.listeners[event]) {
            this.listeners[event] = [];
        }
        this.listeners[event].push(callback);
    },

    removeEventListener(event, callback) {
        if (this.listeners[event]) {
            this.listeners[event] = this.listeners[event].filter(cb => cb !== callback);
        }
    },

    emit(event, data) {
        if (this.listeners[event]) {
            this.listeners[event].forEach(callback => callback(data));
        }
    }
};

// Initialize progress tracking when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    SecureTrainer.ProgressTracker.init();
});

// Clean up WebSocket on page unload
window.addEventListener('beforeunload', () => {
    if (SecureTrainer.ProgressTracker.websocket) {
        SecureTrainer.ProgressTracker.websocket.close();
    }
});