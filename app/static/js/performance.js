/**
 * Performance Optimization Module
 * Implements caching, lazy loading, asset optimization, and performance monitoring
 */

if (!window.SecureTrainer) {
    window.SecureTrainer = {};
}

SecureTrainer.Performance = {
    // Configuration
    config: {
        enableCaching: true,
        enableLazyLoading: true,
        enablePreloading: true,
        enableServiceWorker: false, // Disabled by default for security
        cacheExpiryMinutes: 30,
        lazyLoadOffset: 100,
        performanceThreshold: 1000, // milliseconds
        batchSize: 10
    },

    // Cache management
    cache: new Map(),
    performanceMetrics: new Map(),
    loadedResources: new Set(),
    
    init() {
        this.setupLazyLoading();
        this.setupImageOptimization();
        this.setupResourcePreloading();
        this.setupPerformanceMonitoring();
        this.optimizeScriptLoading();
        this.setupMemoryManagement();
        console.log('⚡ Performance optimization module initialized');
    },

    // Caching System
    setCache(key, data, expiryMinutes = null) {
        if (!this.config.enableCaching) return;

        const expiry = expiryMinutes || this.config.cacheExpiryMinutes;
        const cacheEntry = {
            data: data,
            timestamp: Date.now(),
            expiry: Date.now() + (expiry * 60 * 1000)
        };

        this.cache.set(key, cacheEntry);
        
        // Store in localStorage for persistence
        try {
            const cacheData = {
                [key]: cacheEntry
            };
            localStorage.setItem('securetrainer_cache', JSON.stringify({
                ...JSON.parse(localStorage.getItem('securetrainer_cache') || '{}'),
                ...cacheData
            }));
        } catch (e) {
            console.warn('Failed to persist cache to localStorage:', e);
        }
    },

    getCache(key) {
        if (!this.config.enableCaching) return null;

        let cacheEntry = this.cache.get(key);
        
        // Try localStorage if not in memory
        if (!cacheEntry) {
            try {
                const storedCache = JSON.parse(localStorage.getItem('securetrainer_cache') || '{}');
                cacheEntry = storedCache[key];
                if (cacheEntry) {
                    this.cache.set(key, cacheEntry);
                }
            } catch (e) {
                console.warn('Failed to read cache from localStorage:', e);
            }
        }

        if (!cacheEntry) return null;

        // Check if expired
        if (Date.now() > cacheEntry.expiry) {
            this.cache.delete(key);
            this.clearExpiredCache();
            return null;
        }

        return cacheEntry.data;
    },

    clearCache(key = null) {
        if (key) {
            this.cache.delete(key);
        } else {
            this.cache.clear();
            localStorage.removeItem('securetrainer_cache');
        }
    },

    clearExpiredCache() {
        const now = Date.now();
        const expiredKeys = [];

        this.cache.forEach((entry, key) => {
            if (now > entry.expiry) {
                expiredKeys.push(key);
            }
        });

        expiredKeys.forEach(key => this.cache.delete(key));
    },

    // Lazy Loading Implementation
    setupLazyLoading() {
        if (!this.config.enableLazyLoading) return;

        // Create intersection observer for lazy loading
        this.lazyObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.loadResource(entry.target);
                    this.lazyObserver.unobserve(entry.target);
                }
            });
        }, {
            rootMargin: `${this.config.lazyLoadOffset}px`
        });

        // Observe existing lazy elements
        this.observeLazyElements();

        // Watch for new lazy elements
        this.setupLazyMutationObserver();
    },

    observeLazyElements() {
        const lazyElements = document.querySelectorAll('[data-lazy]');
        lazyElements.forEach(element => {
            this.lazyObserver.observe(element);
        });
    },

    setupLazyMutationObserver() {
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        const lazyElements = node.querySelectorAll ? 
                            node.querySelectorAll('[data-lazy]') : [];
                        lazyElements.forEach(element => {
                            this.lazyObserver.observe(element);
                        });
                        
                        if (node.hasAttribute && node.hasAttribute('data-lazy')) {
                            this.lazyObserver.observe(node);
                        }
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    },

    loadResource(element) {
        const src = element.dataset.lazy;
        const type = element.dataset.type || 'image';

        switch (type) {
            case 'image':
                this.loadImage(element, src);
                break;
            case 'script':
                this.loadScript(element, src);
                break;
            case 'style':
                this.loadStylesheet(element, src);
                break;
            case 'content':
                this.loadContent(element, src);
                break;
        }
    },

    loadImage(img, src) {
        const startTime = performance.now();
        
        img.onload = () => {
            const loadTime = performance.now() - startTime;
            this.recordMetric('image_load', loadTime);
            img.classList.add('loaded');
        };

        img.onerror = () => {
            console.warn('Failed to load image:', src);
            img.classList.add('error');
        };

        img.src = src;
        img.removeAttribute('data-lazy');
    },

    loadScript(container, src) {
        if (this.loadedResources.has(src)) return;

        const script = document.createElement('script');
        const startTime = performance.now();

        script.onload = () => {
            const loadTime = performance.now() - startTime;
            this.recordMetric('script_load', loadTime);
            this.loadedResources.add(src);
            container.classList.add('loaded');
        };

        script.onerror = () => {
            console.warn('Failed to load script:', src);
            container.classList.add('error');
        };

        script.src = src;
        script.async = true;
        document.head.appendChild(script);
    },

    loadStylesheet(container, href) {
        if (this.loadedResources.has(href)) return;

        const link = document.createElement('link');
        const startTime = performance.now();

        link.onload = () => {
            const loadTime = performance.now() - startTime;
            this.recordMetric('style_load', loadTime);
            this.loadedResources.add(href);
            container.classList.add('loaded');
        };

        link.onerror = () => {
            console.warn('Failed to load stylesheet:', href);
            container.classList.add('error');
        };

        link.rel = 'stylesheet';
        link.href = href;
        document.head.appendChild(link);
    },

    async loadContent(container, url) {
        const startTime = performance.now();
        
        try {
            // Check cache first
            const cached = this.getCache(`content_${url}`);
            if (cached) {
                container.innerHTML = cached;
                container.classList.add('loaded');
                return;
            }

            const response = await fetch(url);
            const content = await response.text();
            
            const loadTime = performance.now() - startTime;
            this.recordMetric('content_load', loadTime);

            // Cache the content
            this.setCache(`content_${url}`, content);

            container.innerHTML = content;
            container.classList.add('loaded');
            container.removeAttribute('data-lazy');

        } catch (error) {
            console.warn('Failed to load content:', url, error);
            container.classList.add('error');
        }
    },

    // Image Optimization
    setupImageOptimization() {
        // Add loading="lazy" to images without it
        const images = document.querySelectorAll('img:not([loading])');
        images.forEach(img => {
            if (!img.hasAttribute('data-lazy')) {
                img.setAttribute('loading', 'lazy');
            }
        });

        // Optimize image formats
        this.optimizeImageFormats();
    },

    optimizeImageFormats() {
        // Check for WebP support and replace image sources if available
        const supportsWebP = this.checkWebPSupport();
        
        if (supportsWebP) {
            const images = document.querySelectorAll('img[data-webp]');
            images.forEach(img => {
                img.src = img.dataset.webp;
                img.removeAttribute('data-webp');
            });
        }
    },

    checkWebPSupport() {
        try {
            return document.createElement('canvas')
                .toDataURL('image/webp')
                .indexOf('data:image/webp') === 0;
        } catch (e) {
            return false;
        }
    },

    // Resource Preloading
    setupResourcePreloading() {
        if (!this.config.enablePreloading) return;

        // Preload critical resources
        this.preloadCriticalResources();

        // Setup intelligent preloading based on user behavior
        this.setupIntelligentPreloading();
    },

    preloadCriticalResources() {
        const criticalResources = [
            '/static/css/main.css',
            '/static/js/main.js',
            '/static/js/challenges.js'
        ];

        criticalResources.forEach(resource => {
            this.preloadResource(resource);
        });
    },

    preloadResource(href, as = 'script') {
        if (this.loadedResources.has(href)) return;

        const link = document.createElement('link');
        link.rel = 'preload';
        link.href = href;
        link.as = as;
        
        if (as === 'script') {
            link.crossOrigin = 'anonymous';
        }

        document.head.appendChild(link);
        this.loadedResources.add(href);
    },

    setupIntelligentPreloading() {
        // Preload resources when user hovers over links
        document.addEventListener('mouseover', (event) => {
            if (event.target.tagName === 'A') {
                const href = event.target.getAttribute('href');
                if (href && href.startsWith('/')) {
                    this.preloadPage(href);
                }
            }
        });
    },

    preloadPage(url) {
        // Intelligent page preloading
        const cacheKey = `preload_${url}`;
        if (this.getCache(cacheKey)) return;

        fetch(url, { method: 'GET' })
            .then(response => response.text())
            .then(html => {
                this.setCache(cacheKey, html, 5); // Cache for 5 minutes
            })
            .catch(error => {
                console.warn('Failed to preload page:', url, error);
            });
    },

    // Performance Monitoring
    setupPerformanceMonitoring() {
        this.startPerformanceObserver();
        this.monitorCoreWebVitals();
        this.setupPerformanceReporting();
    },

    startPerformanceObserver() {
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                list.getEntries().forEach(entry => {
                    this.processPerformanceEntry(entry);
                });
            });

            try {
                observer.observe({ entryTypes: ['measure', 'navigation', 'resource', 'paint'] });
            } catch (e) {
                console.warn('Performance Observer not fully supported:', e);
            }
        }
    },

    processPerformanceEntry(entry) {
        switch (entry.entryType) {
            case 'navigation':
                this.recordNavigationMetrics(entry);
                break;
            case 'resource':
                this.recordResourceMetrics(entry);
                break;
            case 'paint':
                this.recordPaintMetrics(entry);
                break;
            case 'measure':
                this.recordCustomMetrics(entry);
                break;
        }
    },

    recordNavigationMetrics(entry) {
        const metrics = {
            dns_lookup: entry.domainLookupEnd - entry.domainLookupStart,
            tcp_connect: entry.connectEnd - entry.connectStart,
            ssl_negotiation: entry.connectEnd - entry.secureConnectionStart,
            ttfb: entry.responseStart - entry.requestStart,
            download: entry.responseEnd - entry.responseStart,
            dom_processing: entry.domComplete - entry.responseEnd,
            total_load_time: entry.loadEventEnd - entry.navigationStart
        };

        Object.entries(metrics).forEach(([name, value]) => {
            if (value > 0) {
                this.recordMetric(`navigation_${name}`, value);
            }
        });
    },

    recordResourceMetrics(entry) {
        if (entry.duration > this.config.performanceThreshold) {
            console.warn(`Slow resource loading detected: ${entry.name} took ${entry.duration}ms`);
        }

        this.recordMetric('resource_load', entry.duration);
    },

    recordPaintMetrics(entry) {
        this.recordMetric(entry.name.replace('-', '_'), entry.startTime);
    },

    recordCustomMetrics(entry) {
        this.recordMetric(entry.name, entry.duration);
    },

    monitorCoreWebVitals() {
        // Monitor Largest Contentful Paint (LCP)
        this.observeLCP();
        
        // Monitor First Input Delay (FID)
        this.observeFID();
        
        // Monitor Cumulative Layout Shift (CLS)
        this.observeCLS();
    },

    observeLCP() {
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                const entries = list.getEntries();
                const lastEntry = entries[entries.length - 1];
                this.recordMetric('lcp', lastEntry.startTime);
            });

            try {
                observer.observe({ entryTypes: ['largest-contentful-paint'] });
            } catch (e) {
                console.warn('LCP observation not supported:', e);
            }
        }
    },

    observeFID() {
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                list.getEntries().forEach(entry => {
                    this.recordMetric('fid', entry.processingStart - entry.startTime);
                });
            });

            try {
                observer.observe({ entryTypes: ['first-input'] });
            } catch (e) {
                console.warn('FID observation not supported:', e);
            }
        }
    },

    observeCLS() {
        let clsValue = 0;
        
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                list.getEntries().forEach(entry => {
                    if (!entry.hadRecentInput) {
                        clsValue += entry.value;
                        this.recordMetric('cls', clsValue);
                    }
                });
            });

            try {
                observer.observe({ entryTypes: ['layout-shift'] });
            } catch (e) {
                console.warn('CLS observation not supported:', e);
            }
        }
    },

    setupPerformanceReporting() {
        // Report performance metrics periodically
        setInterval(() => {
            this.reportPerformanceMetrics();
        }, 30000); // Every 30 seconds

        // Report on page unload
        window.addEventListener('beforeunload', () => {
            this.reportPerformanceMetrics();
        });
    },

    reportPerformanceMetrics() {
        const metrics = {};
        this.performanceMetrics.forEach((values, key) => {
            metrics[key] = {
                avg: values.reduce((a, b) => a + b, 0) / values.length,
                min: Math.min(...values),
                max: Math.max(...values),
                count: values.length
            };
        });

        // Send to analytics if available
        if (SecureTrainer.API) {
            SecureTrainer.API.post('/analytics/performance', {
                metrics: metrics,
                timestamp: Date.now(),
                url: window.location.href
            }).catch(error => {
                console.warn('Failed to report performance metrics:', error);
            });
        }
    },

    // Script Loading Optimization
    optimizeScriptLoading() {
        // Defer non-critical scripts
        this.deferNonCriticalScripts();
        
        // Bundle related scripts
        this.optimizeScriptBundles();
    },

    deferNonCriticalScripts() {
        const nonCriticalScripts = document.querySelectorAll('script[data-defer]');
        nonCriticalScripts.forEach(script => {
            script.defer = true;
            script.removeAttribute('data-defer');
        });
    },

    optimizeScriptBundles() {
        // Group related functionality and load as needed
        const challengeScripts = [
            '/static/js/sql-challenges.js',
            '/static/js/xss-challenges.js',
            '/static/js/command-injection.js',
            '/static/js/auth-challenges.js'
        ];

        // Only load challenge scripts when needed
        document.addEventListener('click', (event) => {
            if (event.target.matches('[data-challenge-type]')) {
                const challengeType = event.target.dataset.challengeType;
                this.loadChallengeScript(challengeType);
            }
        });
    },

    loadChallengeScript(challengeType) {
        const scriptMap = {
            'sql': '/static/js/sql-challenges.js',
            'xss': '/static/js/xss-challenges.js',
            'command': '/static/js/command-injection.js',
            'auth': '/static/js/auth-challenges.js'
        };

        const scriptUrl = scriptMap[challengeType];
        if (scriptUrl && !this.loadedResources.has(scriptUrl)) {
            this.loadScript(document.body, scriptUrl);
        }
    },

    // Memory Management
    setupMemoryManagement() {
        // Monitor memory usage
        this.monitorMemoryUsage();
        
        // Cleanup unused resources
        this.setupResourceCleanup();
    },

    monitorMemoryUsage() {
        if ('memory' in performance) {
            setInterval(() => {
                const memory = performance.memory;
                const usage = {
                    used: memory.usedJSHeapSize,
                    total: memory.totalJSHeapSize,
                    limit: memory.jsHeapSizeLimit
                };

                // Warn if memory usage is high
                const usagePercent = (usage.used / usage.limit) * 100;
                if (usagePercent > 80) {
                    console.warn(`High memory usage detected: ${usagePercent.toFixed(1)}%`);
                    this.performMemoryCleanup();
                }

                this.recordMetric('memory_usage', usagePercent);
            }, 10000); // Every 10 seconds
        }
    },

    setupResourceCleanup() {
        // Clean up expired cache entries
        setInterval(() => {
            this.clearExpiredCache();
        }, 300000); // Every 5 minutes

        // Remove unused event listeners
        this.cleanupEventListeners();
    },

    performMemoryCleanup() {
        // Clear old cache entries
        this.clearExpiredCache();
        
        // Remove unused DOM elements
        this.cleanupUnusedElements();
        
        // Trigger garbage collection if available
        if (window.gc) {
            window.gc();
        }
    },

    cleanupUnusedElements() {
        // Remove hidden or inactive elements that are no longer needed
        const hiddenElements = document.querySelectorAll('[style*="display: none"], .hidden');
        hiddenElements.forEach(element => {
            if (element.dataset.keepHidden !== 'true') {
                element.remove();
            }
        });
    },

    cleanupEventListeners() {
        // This would be implemented based on specific event tracking needs
        console.log('Cleaning up unused event listeners...');
    },

    // Utility Methods
    recordMetric(name, value) {
        if (!this.performanceMetrics.has(name)) {
            this.performanceMetrics.set(name, []);
        }
        
        const values = this.performanceMetrics.get(name);
        values.push(value);
        
        // Keep only last 100 values to prevent memory leaks
        if (values.length > 100) {
            values.shift();
        }
    },

    getAverageMetric(name) {
        const values = this.performanceMetrics.get(name);
        if (!values || values.length === 0) return 0;
        
        return values.reduce((a, b) => a + b, 0) / values.length;
    },

    // Public API
    measure(name, fn) {
        const startTime = performance.now();
        const result = fn();
        const endTime = performance.now();
        
        this.recordMetric(name, endTime - startTime);
        
        if (result instanceof Promise) {
            return result.finally(() => {
                const finalTime = performance.now();
                this.recordMetric(`${name}_async`, finalTime - startTime);
            });
        }
        
        return result;
    },

    preload(url, type = 'script') {
        this.preloadResource(url, type);
    },

    cache(key, data, expiry) {
        this.setCache(key, data, expiry);
    },

    getCached(key) {
        return this.getCache(key);
    }
};

// Initialize performance optimization when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    SecureTrainer.Performance.init();
});

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SecureTrainer.Performance;
}