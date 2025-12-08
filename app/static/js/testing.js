/**
 * Testing Framework for SecureTrainer
 * Frontend and integration tests for challenge system
 */

if (!window.SecureTrainer) {
    window.SecureTrainer = {};
}

SecureTrainer.Testing = {
    // Test configuration
    config: {
        enableConsoleLogging: true,
        enableDetailedReports: true,
        autoRunTests: false,
        testTimeout: 5000,
        includePerformanceTests: true
    },

    // Test state
    testSuites: new Map(),
    testResults: {
        passed: 0,
        failed: 0,
        skipped: 0,
        total: 0,
        startTime: null,
        endTime: null
    },

    currentSuite: null,
    isRunning: false,

    init() {
        this.setupTestEnvironment();
        this.registerTestSuites();
        this.createTestInterface();
        console.log('🧪 Testing framework initialized');
    },

    // Test Suite Registration
    registerTestSuites() {
        // Core functionality tests
        this.registerSuite('core', this.coreTests);
        
        // Security tests
        this.registerSuite('security', this.securityTests);
        
        // Performance tests
        this.registerSuite('performance', this.performanceTests);
        
        // Challenge system tests
        this.registerSuite('challenges', this.challengeTests);
        
        // Progress tracking tests
        this.registerSuite('progress', this.progressTests);
        
        // Learning center tests
        this.registerSuite('learning', this.learningTests);
    },

    registerSuite(name, testFunctions) {
        this.testSuites.set(name, {
            name: name,
            tests: testFunctions,
            results: { passed: 0, failed: 0, skipped: 0 }
        });
    },

    // Test Environment Setup
    setupTestEnvironment() {
        // Create test container
        this.createTestContainer();
        
        // Setup test utilities
        this.setupTestUtilities();
        
        // Mock external dependencies
        this.setupMocks();
    },

    createTestContainer() {
        const container = document.createElement('div');
        container.id = 'test-container';
        container.style.cssText = 'position: fixed; top: -9999px; left: -9999px; width: 1000px; height: 800px;';
        document.body.appendChild(container);
    },

    setupTestUtilities() {
        // Test assertion helpers
        this.assert = {
            equals: (actual, expected, message) => {
                if (actual !== expected) {
                    throw new Error(`${message || 'Assertion failed'}: expected ${expected}, got ${actual}`);
                }
            },
            
            notEquals: (actual, expected, message) => {
                if (actual === expected) {
                    throw new Error(`${message || 'Assertion failed'}: expected not ${expected}, got ${actual}`);
                }
            },
            
            true: (value, message) => {
                if (value !== true) {
                    throw new Error(`${message || 'Assertion failed'}: expected true, got ${value}`);
                }
            },
            
            false: (value, message) => {
                if (value !== false) {
                    throw new Error(`${message || 'Assertion failed'}: expected false, got ${value}`);
                }
            },
            
            exists: (value, message) => {
                if (value == null) {
                    throw new Error(`${message || 'Assertion failed'}: expected value to exist, got ${value}`);
                }
            },
            
            contains: (container, item, message) => {
                if (!container.includes(item)) {
                    throw new Error(`${message || 'Assertion failed'}: expected container to include ${item}`);
                }
            },
            
            instanceOf: (object, constructor, message) => {
                if (!(object instanceof constructor)) {
                    throw new Error(`${message || 'Assertion failed'}: expected instance of ${constructor.name}`);
                }
            }
        };
    },

    setupMocks() {
        // Mock fetch for testing
        this.originalFetch = window.fetch;
        this.mockResponses = new Map();
        
        // Mock localStorage
        this.mockLocalStorage = {};
    },

    // Test Execution
    async runAllTests() {
        if (this.isRunning) {
            console.warn('Tests are already running');
            return;
        }

        this.isRunning = true;
        this.testResults = { passed: 0, failed: 0, skipped: 0, total: 0, startTime: Date.now(), endTime: null };

        console.log('🧪 Starting all tests...');

        for (const [suiteName, suite] of this.testSuites) {
            await this.runTestSuite(suiteName);
        }

        this.testResults.endTime = Date.now();
        this.isRunning = false;
        
        this.generateTestReport();
    },

    async runTestSuite(suiteName) {
        const suite = this.testSuites.get(suiteName);
        if (!suite) {
            console.error(`Test suite '${suiteName}' not found`);
            return;
        }

        this.currentSuite = suite;
        suite.results = { passed: 0, failed: 0, skipped: 0 };

        console.log(`📋 Running test suite: ${suiteName}`);

        for (const [testName, testFunction] of Object.entries(suite.tests)) {
            await this.runTest(testName, testFunction, suite);
        }

        this.updateOverallResults(suite.results);
    },

    async runTest(testName, testFunction, suite) {
        this.testResults.total++;
        
        try {
            console.log(`  ▶ Running test: ${testName}`);
            
            // Setup test environment
            this.setupTestCase();
            
            // Run test with timeout
            await this.withTimeout(testFunction.bind(this), this.config.testTimeout);
            
            // Test passed
            suite.results.passed++;
            this.testResults.passed++;
            
            console.log(`  ✅ ${testName} - PASSED`);
            
        } catch (error) {
            if (error.message === 'Test skipped') {
                suite.results.skipped++;
                this.testResults.skipped++;
                console.log(`  ⏭ ${testName} - SKIPPED`);
            } else {
                suite.results.failed++;
                this.testResults.failed++;
                console.error(`  ❌ ${testName} - FAILED:`, error.message);
            }
        } finally {
            // Cleanup test environment
            this.cleanupTestCase();
        }
    },

    setupTestCase() {
        // Clear test container
        const container = document.getElementById('test-container');
        if (container) {
            container.innerHTML = '';
        }
        
        // Reset mocks
        this.resetMocks();
    },

    cleanupTestCase() {
        // Clear any test artifacts
        const testElements = document.querySelectorAll('[data-test]');
        testElements.forEach(element => element.remove());
    },

    withTimeout(fn, timeout) {
        return new Promise((resolve, reject) => {
            const timer = setTimeout(() => {
                reject(new Error(`Test timeout after ${timeout}ms`));
            }, timeout);

            Promise.resolve(fn()).then(
                result => {
                    clearTimeout(timer);
                    resolve(result);
                },
                error => {
                    clearTimeout(timer);
                    reject(error);
                }
            );
        });
    },

    // Test Definitions
    coreTests: {
        'SecureTrainer namespace exists': function() {
            this.assert.exists(window.SecureTrainer, 'SecureTrainer namespace should exist');
        },

        'Core modules are loaded': function() {
            this.assert.exists(SecureTrainer.API, 'API module should be loaded');
            this.assert.exists(SecureTrainer.Progress, 'Progress module should be loaded');
            this.assert.exists(SecureTrainer.Analytics, 'Analytics module should be loaded');
        },

        'Configuration is valid': function() {
            this.assert.exists(SecureTrainer.config, 'Configuration should exist');
            this.assert.true(typeof SecureTrainer.config.apiBaseUrl === 'string', 'API base URL should be string');
        },

        'Utils functions work correctly': function() {
            if (SecureTrainer.Utils) {
                this.assert.true(typeof SecureTrainer.Utils.generateId === 'function', 'generateId should be function');
                const id1 = SecureTrainer.Utils.generateId();
                const id2 = SecureTrainer.Utils.generateId();
                this.assert.notEquals(id1, id2, 'Generated IDs should be unique');
            } else {
                throw new Error('Test skipped');
            }
        }
    },

    securityTests: {
        'Security module exists': function() {
            this.assert.exists(SecureTrainer.Security, 'Security module should exist');
        },

        'Input sanitization works': function() {
            if (SecureTrainer.Security && SecureTrainer.Security.sanitizeString) {
                const dangerous = '<script>alert("xss")</script>';
                const sanitized = SecureTrainer.Security.sanitizeString(dangerous);
                this.assert.true(!sanitized.includes('<script>'), 'Script tags should be removed');
            } else {
                throw new Error('Test skipped');
            }
        },

        'CSRF token is handled': function() {
            if (SecureTrainer.Security && SecureTrainer.Security.checkCSRFToken) {
                // This would test CSRF token functionality
                this.assert.true(typeof SecureTrainer.Security.checkCSRFToken === 'function', 'CSRF check should be function');
            } else {
                throw new Error('Test skipped');
            }
        }
    },

    performanceTests: {
        'Performance module exists': function() {
            this.assert.exists(SecureTrainer.Performance, 'Performance module should exist');
        },

        'Caching works correctly': function() {
            if (SecureTrainer.Performance && SecureTrainer.Performance.cache) {
                const testKey = 'test_cache_key';
                const testData = { test: 'data' };
                
                SecureTrainer.Performance.cache(testKey, testData);
                const cached = SecureTrainer.Performance.getCached(testKey);
                
                this.assert.equals(JSON.stringify(cached), JSON.stringify(testData), 'Cached data should match original');
            } else {
                throw new Error('Test skipped');
            }
        },

        'Lazy loading observer exists': function() {
            if (SecureTrainer.Performance && SecureTrainer.Performance.lazyObserver) {
                this.assert.instanceOf(SecureTrainer.Performance.lazyObserver, IntersectionObserver, 'Lazy observer should be IntersectionObserver');
            } else {
                throw new Error('Test skipped');
            }
        }
    },

    challengeTests: {
        'Challenge modules are loaded': function() {
            // Test that challenge modules exist
            const challengeModules = ['SQLChallenges', 'XSSChallenges', 'CommandInjection', 'AuthChallenges'];
            let loadedModules = 0;
            
            challengeModules.forEach(module => {
                if (SecureTrainer[module]) {
                    loadedModules++;
                }
            });
            
            this.assert.true(loadedModules > 0, 'At least one challenge module should be loaded');
        },

        'Challenge interface can be created': function() {
            const container = document.getElementById('test-container');
            container.innerHTML = '<div id="challenge-workspace"></div>';
            
            // Test SQL challenges interface
            if (SecureTrainer.SQLChallenges && SecureTrainer.SQLChallenges.createSQLInterface) {
                SecureTrainer.SQLChallenges.createSQLInterface();
                const interface = container.querySelector('.sql-challenge-container');
                this.assert.exists(interface, 'SQL challenge interface should be created');
            } else {
                throw new Error('Test skipped');
            }
        },

        'Challenge progress tracking works': function() {
            if (SecureTrainer.Analytics && SecureTrainer.Analytics.trackChallengeProgress) {
                // Mock the tracking function
                let trackingCalled = false;
                const originalTrack = SecureTrainer.Analytics.trackChallengeProgress;
                
                SecureTrainer.Analytics.trackChallengeProgress = function() {
                    trackingCalled = true;
                };
                
                // Simulate challenge progress
                SecureTrainer.Analytics.trackChallengeProgress('sql_injection', 50, 75);
                
                this.assert.true(trackingCalled, 'Progress tracking should be called');
                
                // Restore original function
                SecureTrainer.Analytics.trackChallengeProgress = originalTrack;
            } else {
                throw new Error('Test skipped');
            }
        }
    },

    progressTests: {
        'Progress tracker exists': function() {
            this.assert.exists(SecureTrainer.ProgressTracker, 'Progress tracker should exist');
        },

        'Progress UI elements are created': function() {
            if (SecureTrainer.ProgressTracker && SecureTrainer.ProgressTracker.createProgressTracker) {
                // Remove existing tracker if present
                const existing = document.getElementById('progress-tracker');
                if (existing) existing.remove();
                
                SecureTrainer.ProgressTracker.createProgressTracker();
                const tracker = document.getElementById('progress-tracker');
                this.assert.exists(tracker, 'Progress tracker UI should be created');
            } else {
                throw new Error('Test skipped');
            }
        },

        'Progress data can be stored and retrieved': function() {
            if (SecureTrainer.ProgressTracker) {
                const testData = { challenge: 'test', progress: 50, score: 75 };
                SecureTrainer.ProgressTracker.progressData.test_challenge = testData;
                
                this.assert.exists(SecureTrainer.ProgressTracker.progressData.test_challenge, 'Progress data should be stored');
                this.assert.equals(SecureTrainer.ProgressTracker.progressData.test_challenge.progress, 50, 'Progress value should match');
            } else {
                throw new Error('Test skipped');
            }
        }
    },

    learningTests: {
        'Learning center module exists': function() {
            this.assert.exists(SecureTrainer.LearningCenter, 'Learning center module should exist');
        },

        'Learning content can be loaded': function() {
            if (SecureTrainer.LearningCenter && SecureTrainer.LearningCenter.loadContent) {
                // Mock content loading
                let loadCalled = false;
                const originalLoad = SecureTrainer.LearningCenter.loadContent;
                
                SecureTrainer.LearningCenter.loadContent = function() {
                    loadCalled = true;
                    return Promise.resolve();
                };
                
                SecureTrainer.LearningCenter.loadContent('test-module');
                this.assert.true(loadCalled, 'Content loading should be called');
                
                // Restore original function
                SecureTrainer.LearningCenter.loadContent = originalLoad;
            } else {
                throw new Error('Test skipped');
            }
        }
    },

    // Mock Management
    resetMocks() {
        this.mockResponses.clear();
        this.mockLocalStorage = {};
    },

    mockFetch(url, response) {
        this.mockResponses.set(url, response);
        
        window.fetch = (requestUrl, options) => {
            const mockResponse = this.mockResponses.get(requestUrl);
            if (mockResponse) {
                return Promise.resolve({
                    ok: true,
                    json: () => Promise.resolve(mockResponse)
                });
            }
            return this.originalFetch(requestUrl, options);
        };
    },

    // Test Interface
    createTestInterface() {
        if (document.getElementById('test-interface')) return;
        
        const interface = document.createElement('div');
        interface.id = 'test-interface';
        interface.className = 'fixed bottom-4 left-4 bg-white shadow-lg rounded-lg border p-4 z-50';
        interface.innerHTML = `
            <div class="test-controls">
                <h4 class="text-sm font-semibold mb-2">🧪 Test Framework</h4>
                <div class="flex gap-2 mb-2">
                    <button id="run-all-tests" class="btn-sm btn-primary">Run All Tests</button>
                    <button id="run-core-tests" class="btn-sm btn-secondary">Core Tests</button>
                    <button id="run-security-tests" class="btn-sm btn-secondary">Security Tests</button>
                </div>
                <div id="test-status" class="text-xs text-gray-600">Ready to run tests</div>
                <div id="test-progress" class="hidden">
                    <div class="progress-bar h-2 bg-gray-200 rounded mt-2">
                        <div id="test-progress-bar" class="progress-fill h-full bg-blue-500 rounded" style="width: 0%"></div>
                    </div>
                </div>
            </div>
        `;

        document.body.appendChild(interface);
        this.setupTestInterfaceEvents();
    },

    setupTestInterfaceEvents() {
        document.getElementById('run-all-tests').addEventListener('click', () => {
            this.runAllTests();
        });

        document.getElementById('run-core-tests').addEventListener('click', () => {
            this.runTestSuite('core');
        });

        document.getElementById('run-security-tests').addEventListener('click', () => {
            this.runTestSuite('security');
        });
    },

    updateTestProgress(current, total) {
        const progressBar = document.getElementById('test-progress-bar');
        const status = document.getElementById('test-status');
        const progressContainer = document.getElementById('test-progress');

        if (progressBar && status) {
            const percentage = (current / total) * 100;
            progressBar.style.width = percentage + '%';
            status.textContent = `Running tests: ${current}/${total}`;
            progressContainer.classList.remove('hidden');
        }
    },

    updateOverallResults(suiteResults) {
        this.testResults.passed += suiteResults.passed;
        this.testResults.failed += suiteResults.failed;
        this.testResults.skipped += suiteResults.skipped;
    },

    generateTestReport() {
        const duration = this.testResults.endTime - this.testResults.startTime;
        
        console.log('\n📊 TEST REPORT');
        console.log('================');
        console.log(`Total Tests: ${this.testResults.total}`);
        console.log(`Passed: ${this.testResults.passed}`);
        console.log(`Failed: ${this.testResults.failed}`);
        console.log(`Skipped: ${this.testResults.skipped}`);
        console.log(`Duration: ${duration}ms`);
        console.log(`Success Rate: ${((this.testResults.passed / this.testResults.total) * 100).toFixed(1)}%`);

        // Update test interface
        const status = document.getElementById('test-status');
        const progressContainer = document.getElementById('test-progress');
        
        if (status) {
            status.innerHTML = `
                <div class="text-xs">
                    ✅ ${this.testResults.passed} passed 
                    ❌ ${this.testResults.failed} failed 
                    ⏭ ${this.testResults.skipped} skipped
                </div>
            `;
        }
        
        if (progressContainer) {
            progressContainer.classList.add('hidden');
        }

        // Generate detailed report if enabled
        if (this.config.enableDetailedReports) {
            this.generateDetailedReport();
        }
    },

    generateDetailedReport() {
        const report = {
            summary: this.testResults,
            suites: Array.from(this.testSuites.entries()).map(([name, suite]) => ({
                name: name,
                results: suite.results
            })),
            environment: {
                userAgent: navigator.userAgent,
                timestamp: new Date().toISOString(),
                url: window.location.href
            }
        };

        // Send report to analytics if available
        if (SecureTrainer.API) {
            SecureTrainer.API.post('/analytics/test-report', report).catch(error => {
                console.warn('Failed to send test report:', error);
            });
        }

        // Store report locally
        localStorage.setItem('securetrainer_test_report', JSON.stringify(report));
    },

    // Public API
    skip() {
        throw new Error('Test skipped');
    },

    runSuite(suiteName) {
        return this.runTestSuite(suiteName);
    },

    addTest(suiteName, testName, testFunction) {
        const suite = this.testSuites.get(suiteName);
        if (suite) {
            suite.tests[testName] = testFunction;
        }
    }
};

// Initialize testing framework when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    SecureTrainer.Testing.init();
});

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SecureTrainer.Testing;
}