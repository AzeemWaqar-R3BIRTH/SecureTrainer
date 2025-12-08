/**
 * SecureTrainer JavaScript Core Module
 * Comprehensive frontend functionality for cybersecurity training platform
 * Implements challenge interface, API integration, and user experience features
 */

// Global application state
const SecureTrainer = {
    // Configuration
    config: {
        apiBaseUrl: '/api',
        debug: false,
        enableAnalytics: true,
        challengeTimeout: 1800000, // 30 minutes
        autoSaveInterval: 30000 // 30 seconds
    },
    
    // Application state
    state: {
        currentUser: null,
        activeChallenge: null,
        challengeStartTime: null,
        hintsUsed: 0,
        sessionActive: false
    },
    
    // Event handlers
    events: new EventTarget(),
    
    // Initialize application
    init() {
        console.log('🚀 SecureTrainer initializing...');
        this.setupEventListeners();
        this.loadUserSession();
        this.initializeCSRF();
        this.setupPerformanceMonitoring();
        console.log('✅ SecureTrainer initialized');
    },
    
    // Setup global event listeners
    setupEventListeners() {
        // DOM content loaded
        document.addEventListener('DOMContentLoaded', () => {
            this.initializeComponents();
        });
        
        // Handle authentication state changes
        this.events.addEventListener('auth:login', (event) => {
            this.handleLogin(event.detail);
        });
        
        this.events.addEventListener('auth:logout', () => {
            this.handleLogout();
        });
        
        // Handle challenge events
        this.events.addEventListener('challenge:start', (event) => {
            this.handleChallengeStart(event.detail);
        });
        
        this.events.addEventListener('challenge:complete', (event) => {
            this.handleChallengeComplete(event.detail);
        });
        
        // Handle errors
        window.addEventListener('error', (event) => {
            this.handleError(event.error);
        });
        
        window.addEventListener('unhandledrejection', (event) => {
            this.handleError(event.reason);
        });
    },
    
    // Initialize components after DOM is ready
    initializeComponents() {
        // Initialize progress tracking
        this.Progress.init();
        
        // Initialize challenge interface if on challenges page
        if (document.getElementById('challenge-container')) {
            this.Challenges.init();
        }
        
        // Initialize learning center if on learning page
        if (document.getElementById('learning-center')) {
            this.LearningCenter.init();
        }
        
        // Initialize QR scanner if on login page
        if (document.getElementById('qr-scanner')) {
            this.QRScanner.init();
        }
    },
    
    // Load user session from storage
    loadUserSession() {
        const userData = localStorage.getItem('user_data');
        const lastSync = localStorage.getItem('last_sync');
        
        if (userData && lastSync) {
            const syncTime = parseInt(lastSync);
            const hoursSinceSync = (Date.now() - syncTime) / (1000 * 60 * 60);
            
            if (hoursSinceSync < 24) {
                this.state.currentUser = JSON.parse(userData);
                this.state.sessionActive = true;
                this.events.dispatchEvent(new CustomEvent('auth:restored', {
                    detail: this.state.currentUser
                }));
            }
        }
    },
    
    // Initialize CSRF protection
    initializeCSRF() {
        const token = document.querySelector('meta[name="csrf-token"]');
        if (token) {
            this.config.csrfToken = token.getAttribute('content');
        }
    },
    
    // Setup performance monitoring
    setupPerformanceMonitoring() {
        this.Performance.init();
    },
    
    // Handle user login
    handleLogin(userData) {
        this.state.currentUser = userData;
        this.state.sessionActive = true;
        
        // Cache user data
        localStorage.setItem('user_data', JSON.stringify(userData));
        localStorage.setItem('last_sync', Date.now().toString());
        
        // Update UI
        this.updateUserInterface();
        
        console.log('👤 User logged in:', userData.username);
    },
    
    // Handle user logout
    handleLogout() {
        this.state.currentUser = null;
        this.state.sessionActive = false;
        this.state.activeChallenge = null;
        
        // Clear cached data
        localStorage.removeItem('user_data');
        localStorage.removeItem('last_sync');
        localStorage.removeItem('challenge_progress');
        
        // Redirect to login
        window.location.href = '/login';
        
        console.log('👋 User logged out');
    },
    
    // Handle challenge start
    handleChallengeStart(challengeData) {
        this.state.activeChallenge = challengeData;
        this.state.challengeStartTime = Date.now();
        this.state.hintsUsed = 0;
        
        // Start auto-save
        this.startAutoSave();
        
        console.log('🎯 Challenge started:', challengeData.title);
    },
    
    // Handle challenge completion
    handleChallengeComplete(resultData) {
        if (this.state.activeChallenge) {
            const completionTime = Date.now() - this.state.challengeStartTime;
            
            // Stop auto-save
            this.stopAutoSave();
            
            // Update progress
            this.Progress.updateChallengeProgress(resultData);
            
            // Show celebration if successful
            if (resultData.success) {
                this.Progress.celebrateSuccess();
            }
            
            console.log('🏆 Challenge completed:', resultData);
        }
    },
    
    // Handle application errors
    handleError(error) {
        console.error('❌ Application error:', error);
        
        if (this.config.enableAnalytics) {
            this.Analytics.reportError(error);
        }
        
        // Show user-friendly error message
        this.showNotification('An error occurred. Please try again.', 'error');
    },
    
    // Update user interface based on current state
    updateUserInterface() {
        const userElements = document.querySelectorAll('[data-user-content]');
        userElements.forEach(element => {
            if (this.state.sessionActive) {
                element.style.display = 'block';
            } else {
                element.style.display = 'none';
            }
        });
    },
    
    // Auto-save functionality
    autoSaveInterval: null,
    
    startAutoSave() {
        this.autoSaveInterval = setInterval(() => {
            this.saveProgressLocally();
        }, this.config.autoSaveInterval);
    },
    
    stopAutoSave() {
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
            this.autoSaveInterval = null;
        }
    },
    
    saveProgressLocally() {
        if (this.state.activeChallenge) {
            const progressData = {
                challengeId: this.state.activeChallenge.id,
                startTime: this.state.challengeStartTime,
                hintsUsed: this.state.hintsUsed,
                timestamp: Date.now()
            };
            
            localStorage.setItem('challenge_progress', JSON.stringify(progressData));
        }
    },
    
    // Show notification to user
    showNotification(message, type = 'info', duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.textContent = message;
        
        // Add to DOM
        const container = document.getElementById('notification-container') || document.body;
        container.appendChild(notification);
        
        // Remove after duration
        setTimeout(() => {
            notification.remove();
        }, duration);
    }
};

// API utilities
SecureTrainer.API = {
    // Make authenticated API request
    async request(endpoint, options = {}) {
        const url = `${SecureTrainer.config.apiBaseUrl}${endpoint}`;
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...(SecureTrainer.config.csrfToken && {
                    'X-CSRF-Token': SecureTrainer.config.csrfToken
                })
            },
            credentials: 'same-origin'
        };
        
        const mergedOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };
        
        try {
            const response = await fetch(url, mergedOptions);
            
            if (!response.ok) {
                throw new Error(`API request failed: ${response.status} ${response.statusText}`);
            }
            
            const data = await response.json();
            return data;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    },
    
    // Convenience methods
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    },
    
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }
};

// Progress tracking module
SecureTrainer.Progress = {
    init() {
        this.setupProgressBars();
        this.loadProgressData();
    },
    
    setupProgressBars() {
        const progressBars = document.querySelectorAll('.progress-bar');
        progressBars.forEach(bar => {
            bar.setAttribute('role', 'progressbar');
            bar.setAttribute('aria-valuemin', '0');
            bar.setAttribute('aria-valuemax', '100');
        });
    },
    
    async loadProgressData() {
        if (!SecureTrainer.state.sessionActive) return;
        
        try {
            const progressData = await SecureTrainer.API.get('/user/progress');
            this.updateProgressDisplay(progressData);
        } catch (error) {
            console.error('Failed to load progress data:', error);
        }
    },
    
    updateProgressDisplay(progressData) {
        // Update category progress bars
        Object.entries(progressData.categories || {}).forEach(([category, progress]) => {
            const progressBar = document.getElementById(`${category}-progress-bar`);
            const progressText = document.getElementById(`${category}-progress`);
            
            if (progressBar) {
                this.animateProgress(progressBar, 0, progress.percentage);
            }
            
            if (progressText) {
                progressText.textContent = `${progress.completed}/${progress.total} completed`;
            }
        });
        
        // Update overall progress
        const overallProgress = document.getElementById('overall-progress');
        if (overallProgress && progressData.overall) {
            this.animateProgress(overallProgress, 0, progressData.overall.percentage);
        }
    },
    
    animateProgress(element, from, to, duration = 1000) {
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const easeOutCubic = 1 - Math.pow(1 - progress, 3);
            const current = from + (to - from) * easeOutCubic;
            
            element.style.width = `${current}%`;
            element.setAttribute('aria-valuenow', current);
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    },
    
    updateChallengeProgress(resultData) {
        // Update local progress tracking
        const category = resultData.category;
        const progressBar = document.getElementById(`${category}-progress-bar`);
        
        if (progressBar) {
            const currentProgress = parseFloat(progressBar.style.width) || 0;
            const newProgress = Math.min(currentProgress + 10, 100); // Increment by 10%
            this.animateProgress(progressBar, currentProgress, newProgress);
        }
    },
    
    celebrateSuccess() {
        const container = document.getElementById('challenge-container') || document.body;
        container.classList.add('success-animation');
        
        // Create confetti effect
        for (let i = 0; i < 50; i++) {
            const confetti = document.createElement('div');
            confetti.className = 'confetti';
            confetti.style.left = Math.random() * 100 + '%';
            confetti.style.animationDelay = Math.random() * 3 + 's';
            confetti.style.backgroundColor = this.getRandomColor();
            container.appendChild(confetti);
            
            setTimeout(() => {
                confetti.remove();
            }, 3000);
        }
        
        setTimeout(() => {
            container.classList.remove('success-animation');
        }, 3000);
    },
    
    getRandomColor() {
        const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57', '#ff9ff3'];
        return colors[Math.floor(Math.random() * colors.length)];
    }
};

// Performance monitoring
SecureTrainer.Performance = {
    metrics: new Map(),
    
    init() {
        this.setupPerformanceObserver();
    },
    
    setupPerformanceObserver() {
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    this.recordMetric(entry.name, entry.duration);
                }
            });
            
            observer.observe({ entryTypes: ['measure', 'navigation'] });
        }
    },
    
    startTiming(label) {
        this.metrics.set(label, performance.now());
    },
    
    endTiming(label) {
        const startTime = this.metrics.get(label);
        if (startTime) {
            const duration = performance.now() - startTime;
            console.log(`${label}: ${duration.toFixed(2)}ms`);
            
            // Report slow performance
            if (duration > 1000) {
                this.reportSlowPerformance(label, duration);
            }
            
            this.metrics.delete(label);
            return duration;
        }
    },
    
    recordMetric(name, value) {
        if (SecureTrainer.config.enableAnalytics) {
            // Send to analytics endpoint
            SecureTrainer.API.post('/analytics/performance', {
                metric: name,
                value: value,
                userAgent: navigator.userAgent,
                timestamp: Date.now()
            }).catch(error => {
                console.warn('Failed to record performance metric:', error);
            });
        }
    },
    
    reportSlowPerformance(operation, duration) {
        console.warn(`Slow performance detected: ${operation} took ${duration.toFixed(2)}ms`);
        
        if (SecureTrainer.config.enableAnalytics) {
            SecureTrainer.API.post('/analytics/performance', {
                operation,
                duration,
                userAgent: navigator.userAgent,
                timestamp: Date.now(),
                type: 'slow_performance'
            }).catch(error => {
                console.warn('Failed to report slow performance:', error);
            });
        }
    }
};

// Analytics module
SecureTrainer.Analytics = {
    trackChallengeCompletion(challengeType, score) {
        console.log(`Challenge completed: ${challengeType} - Score: ${score}`);
        
        // Track in localStorage for persistence
        const completions = JSON.parse(localStorage.getItem('challenge_completions') || '[]');
        completions.push({
            challenge: challengeType,
            score: score,
            completedAt: new Date().toISOString()
        });
        localStorage.setItem('challenge_completions', JSON.stringify(completions));
        
        // Send to progress tracker for real-time updates
        if (window.SecureTrainer.ProgressTracker) {
            window.SecureTrainer.ProgressTracker.trackChallengeCompletion(challengeType, score);
        }
        
        // Send to analytics endpoint if available
        this.trackEvent('challenge_completion', {
            challenge_type: challengeType,
            score: score,
            timestamp: new Date().toISOString()
        });
    },

    trackChallengeProgress(challengeType, progress, score) {
        // Track progress in real-time
        if (window.SecureTrainer.ProgressTracker) {
            window.SecureTrainer.ProgressTracker.trackChallengeProgress(challengeType, progress, score);
        }
    },

    reportError(error) {
        const errorData = {
            message: error.message,
            stack: error.stack,
            timestamp: Date.now(),
            url: window.location.href,
            userAgent: navigator.userAgent,
            userId: SecureTrainer.state.currentUser?.id
        };
        
        SecureTrainer.API.post('/analytics/error', errorData).catch(err => {
            console.warn('Failed to report error:', err);
        });
    },
    
    trackEvent(eventName, eventData = {}) {
        const eventPayload = {
            event: eventName,
            data: eventData,
            timestamp: Date.now(),
            userId: SecureTrainer.state.currentUser?.id,
            sessionId: SecureTrainer.state.sessionId
        };
        
        SecureTrainer.API.post('/analytics/event', eventPayload).catch(error => {
            console.warn('Failed to track event:', error);
        });
    }
};

// Utility functions
SecureTrainer.Utils = {
    // Debounce function calls
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },
    
    // Throttle function calls
    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    },
    
    // Format time duration
    formatDuration(milliseconds) {
        const seconds = Math.floor(milliseconds / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        
        if (hours > 0) {
            return `${hours}h ${minutes % 60}m ${seconds % 60}s`;
        } else if (minutes > 0) {
            return `${minutes}m ${seconds % 60}s`;
        } else {
            return `${seconds}s`;
        }
    },
    
    // Sanitize HTML input
    sanitizeHTML(html) {
        const div = document.createElement('div');
        div.textContent = html;
        return div.innerHTML;
    },
    
    // Generate unique ID
    generateId() {
        return Math.random().toString(36).substr(2, 9);
    }
};

// Initialize SecureTrainer when script loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => SecureTrainer.init());
} else {
    SecureTrainer.init();
}

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SecureTrainer;
}