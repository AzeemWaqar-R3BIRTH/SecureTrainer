/**
 * Frontend Security Module
 * Implements CSP, input sanitization, CSRF protection and other security measures
 */

if (!window.SecureTrainer) {
    window.SecureTrainer = {};
}

SecureTrainer.Security = {
    // Configuration
    config: {
        enableCSP: true,
        enableInputSanitization: true,
        enableCSRFProtection: true,
        enableXSSProtection: true,
        maxInputLength: 10000,
        allowedDomains: ['localhost', '127.0.0.1'],
        trustedScriptSources: [
            "'self'",
            "https://cdn.jsdelivr.net",
            "https://unpkg.com"
        ]
    },

    // CSRF token management
    csrfToken: null,

    init() {
        this.setupCSRFProtection();
        this.setupInputSanitization();
        this.setupContentSecurityPolicy();
        this.setupXSSProtection();
        this.setupFormValidation();
        this.monitorSecurityEvents();
        console.log('🔒 Security module initialized');
    },

    // CSRF Protection
    setupCSRFProtection() {
        // Get CSRF token from meta tag or API
        const metaToken = document.querySelector('meta[name="csrf-token"]');
        if (metaToken) {
            this.csrfToken = metaToken.getAttribute('content');
        }

        // Add CSRF token to all forms
        this.addCSRFToForms();

        // Add CSRF token to AJAX requests
        this.addCSRFToAjax();
    },

    addCSRFToForms() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            if (!form.querySelector('input[name="csrf_token"]') && this.csrfToken) {
                const csrfInput = document.createElement('input');
                csrfInput.type = 'hidden';
                csrfInput.name = 'csrf_token';
                csrfInput.value = this.csrfToken;
                form.appendChild(csrfInput);
            }
        });
    },

    addCSRFToAjax() {
        // Override fetch to include CSRF token
        const originalFetch = window.fetch;
        window.fetch = async (url, options = {}) => {
            if (this.csrfToken && options.method && options.method !== 'GET') {
                options.headers = {
                    ...options.headers,
                    'X-CSRF-Token': this.csrfToken
                };
            }
            return originalFetch(url, options);
        };

        // Override XMLHttpRequest for older code
        const originalOpen = XMLHttpRequest.prototype.open;
        XMLHttpRequest.prototype.open = function(method, url, async, user, password) {
            this._method = method;
            return originalOpen.call(this, method, url, async, user, password);
        };

        const originalSend = XMLHttpRequest.prototype.send;
        XMLHttpRequest.prototype.send = function(data) {
            if (SecureTrainer.Security.csrfToken && this._method && this._method !== 'GET') {
                this.setRequestHeader('X-CSRF-Token', SecureTrainer.Security.csrfToken);
            }
            return originalSend.call(this, data);
        };
    },

    // Input Sanitization
    setupInputSanitization() {
        // Monitor all input fields
        document.addEventListener('input', (event) => {
            if (event.target.matches('input, textarea')) {
                this.sanitizeInput(event.target);
            }
        });

        // Monitor paste events
        document.addEventListener('paste', (event) => {
            if (event.target.matches('input, textarea')) {
                setTimeout(() => this.sanitizeInput(event.target), 0);
            }
        });
    },

    sanitizeInput(element) {
        if (!this.config.enableInputSanitization) return;

        const value = element.value;
        const sanitized = this.sanitizeString(value);
        
        if (value !== sanitized) {
            element.value = sanitized;
            this.showSecurityWarning('Input has been sanitized for security');
        }

        // Check input length
        if (value.length > this.config.maxInputLength) {
            element.value = value.substring(0, this.config.maxInputLength);
            this.showSecurityWarning(`Input truncated to ${this.config.maxInputLength} characters`);
        }
    },

    sanitizeString(str) {
        if (typeof str !== 'string') return str;

        // Remove potentially dangerous characters and patterns
        return str
            .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '') // Remove script tags
            .replace(/javascript:/gi, '') // Remove javascript: URLs
            .replace(/on\w+\s*=/gi, '') // Remove event handlers
            .replace(/expression\s*\(/gi, '') // Remove CSS expressions
            .replace(/<iframe\b[^>]*>/gi, '') // Remove iframe tags
            .replace(/<object\b[^>]*>/gi, '') // Remove object tags
            .replace(/<embed\b[^>]*>/gi, '') // Remove embed tags
            .replace(/data:(?!image\/[a-z]+;base64,)[^;]*;/gi, ''); // Remove non-image data URLs
    },

    sanitizeHTML(html) {
        // Create a temporary div to parse HTML
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;

        // Remove dangerous elements
        const dangerousElements = tempDiv.querySelectorAll('script, iframe, object, embed, form, input, button');
        dangerousElements.forEach(element => element.remove());

        // Remove dangerous attributes
        const allElements = tempDiv.querySelectorAll('*');
        allElements.forEach(element => {
            const attributes = [...element.attributes];
            attributes.forEach(attr => {
                if (attr.name.startsWith('on') || attr.name === 'src' && attr.value.startsWith('javascript:')) {
                    element.removeAttribute(attr.name);
                }
            });
        });

        return tempDiv.innerHTML;
    },

    // Content Security Policy
    setupContentSecurityPolicy() {
        if (!this.config.enableCSP) return;

        // Check if CSP is already set via headers
        const existingCSP = document.querySelector('meta[http-equiv="Content-Security-Policy"]');
        
        if (!existingCSP) {
            // Create CSP meta tag as fallback
            const cspMeta = document.createElement('meta');
            cspMeta.setAttribute('http-equiv', 'Content-Security-Policy');
            cspMeta.setAttribute('content', this.generateCSPPolicy());
            document.head.appendChild(cspMeta);
        }

        // Monitor CSP violations
        document.addEventListener('securitypolicyviolation', (event) => {
            this.handleCSPViolation(event);
        });
    },

    generateCSPPolicy() {
        const scriptSrc = this.config.trustedScriptSources.join(' ');
        return [
            `default-src 'self'`,
            `script-src ${scriptSrc} 'unsafe-inline'`, // unsafe-inline needed for some dynamic content
            `style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net`,
            `img-src 'self' data: https:`,
            `font-src 'self' https://cdn.jsdelivr.net`,
            `connect-src 'self' ws: wss:`,
            `frame-ancestors 'none'`,
            `base-uri 'self'`,
            `object-src 'none'`
        ].join('; ');
    },

    handleCSPViolation(event) {
        console.warn('CSP Violation:', {
            directive: event.violatedDirective,
            blockedURI: event.blockedURI,
            documentURI: event.documentURI,
            originalPolicy: event.originalPolicy
        });

        // Report violation to security endpoint
        if (SecureTrainer.API) {
            SecureTrainer.API.post('/security/csp-violation', {
                directive: event.violatedDirective,
                blockedURI: event.blockedURI,
                documentURI: event.documentURI,
                timestamp: Date.now(),
                userAgent: navigator.userAgent
            }).catch(error => {
                console.warn('Failed to report CSP violation:', error);
            });
        }
    },

    // XSS Protection
    setupXSSProtection() {
        if (!this.config.enableXSSProtection) return;

        // Monitor dynamic content insertion
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        this.scanForXSS(node);
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    },

    scanForXSS(element) {
        // Check for dangerous script content
        const scripts = element.querySelectorAll('script');
        scripts.forEach(script => {
            if (!this.isScriptTrusted(script)) {
                console.warn('Potentially malicious script detected and removed:', script);
                script.remove();
                this.showSecurityWarning('Potentially malicious script blocked');
            }
        });

        // Check for dangerous event handlers
        const elementsWithEvents = element.querySelectorAll('*[onclick], *[onload], *[onerror]');
        elementsWithEvents.forEach(el => {
            console.warn('Element with inline event handler detected:', el);
            this.showSecurityWarning('Inline event handlers detected');
        });
    },

    isScriptTrusted(script) {
        // Check if script source is trusted
        if (script.src) {
            try {
                const url = new URL(script.src);
                return this.config.allowedDomains.includes(url.hostname) ||
                       this.config.trustedScriptSources.some(source => 
                           source !== "'self'" && source !== "'unsafe-inline'" && script.src.startsWith(source));
            } catch (e) {
                return false;
            }
        }

        // For inline scripts, check content
        const content = script.textContent || script.innerHTML;
        const dangerousPatterns = [
            /eval\s*\(/,
            /Function\s*\(/,
            /setTimeout\s*\(\s*["']/,
            /setInterval\s*\(\s*["']/,
            /document\.write/,
            /innerHTML\s*=/,
            /location\s*=/
        ];

        return !dangerousPatterns.some(pattern => pattern.test(content));
    },

    // Form Validation
    setupFormValidation() {
        document.addEventListener('submit', (event) => {
            if (event.target.tagName === 'FORM') {
                this.validateForm(event.target, event);
            }
        });
    },

    validateForm(form, event) {
        const errors = [];

        // Validate CSRF token
        if (this.config.enableCSRFProtection && this.csrfToken) {
            const csrfInput = form.querySelector('input[name="csrf_token"]');
            if (!csrfInput || csrfInput.value !== this.csrfToken) {
                errors.push('CSRF token missing or invalid');
            }
        }

        // Validate input fields
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            if (input.hasAttribute('required') && !input.value.trim()) {
                errors.push(`${input.name || 'Field'} is required`);
            }

            if (input.type === 'email' && input.value && !this.isValidEmail(input.value)) {
                errors.push('Invalid email format');
            }

            if (input.maxLength && input.value.length > input.maxLength) {
                errors.push(`${input.name || 'Field'} exceeds maximum length`);
            }
        });

        if (errors.length > 0) {
            event.preventDefault();
            this.showValidationErrors(errors);
            return false;
        }

        return true;
    },

    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    },

    showValidationErrors(errors) {
        const errorList = errors.map(error => `• ${error}`).join('\n');
        this.showSecurityWarning(`Form validation failed:\n${errorList}`);
    },

    // Security Event Monitoring
    monitorSecurityEvents() {
        // Monitor for suspicious activities
        let suspiciousActivityCount = 0;
        const suspiciousActivityThreshold = 10;

        // Monitor rapid form submissions
        let lastSubmitTime = 0;
        document.addEventListener('submit', () => {
            const now = Date.now();
            if (now - lastSubmitTime < 1000) { // Less than 1 second
                suspiciousActivityCount++;
                this.reportSuspiciousActivity('rapid_form_submission');
            }
            lastSubmitTime = now;
        });

        // Monitor excessive input attempts
        let inputAttempts = 0;
        document.addEventListener('input', () => {
            inputAttempts++;
            if (inputAttempts > 100) { // More than 100 inputs per minute
                this.reportSuspiciousActivity('excessive_input');
                inputAttempts = 0;
            }
        });

        // Reset input counter every minute
        setInterval(() => {
            inputAttempts = 0;
        }, 60000);

        // Monitor for suspicious network requests
        this.monitorNetworkRequests();
    },

    monitorNetworkRequests() {
        // Override fetch to monitor requests
        const originalFetch = window.fetch;
        window.fetch = async (url, options = {}) => {
            try {
                // Check for suspicious URLs
                if (typeof url === 'string' && this.isSuspiciousURL(url)) {
                    this.reportSuspiciousActivity('suspicious_url_request', { url });
                }

                return await originalFetch(url, options);
            } catch (error) {
                // Log failed requests for security analysis
                this.reportSuspiciousActivity('failed_request', { url, error: error.message });
                throw error;
            }
        };
    },

    isSuspiciousURL(url) {
        const suspiciousPatterns = [
            /\b(?:eval|script|javascript|vbscript)\b/i,
            /\b(?:alert|confirm|prompt)\b/i,
            /[<>\"']/,
            /\.\.\/|\.\.\\/, // Path traversal
            /\b(?:admin|root|test|debug)\b/i
        ];

        return suspiciousPatterns.some(pattern => pattern.test(url));
    },

    reportSuspiciousActivity(type, details = {}) {
        console.warn(`Suspicious activity detected: ${type}`, details);

        // Report to security endpoint
        if (SecureTrainer.API) {
            SecureTrainer.API.post('/security/suspicious-activity', {
                type: type,
                details: details,
                timestamp: Date.now(),
                userAgent: navigator.userAgent,
                url: window.location.href
            }).catch(error => {
                console.warn('Failed to report suspicious activity:', error);
            });
        }
    },

    // User Notifications
    showSecurityWarning(message) {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = 'security-warning fixed top-4 right-4 bg-yellow-100 border border-yellow-400 text-yellow-800 px-4 py-3 rounded shadow-lg z-50';
        notification.innerHTML = `
            <div class="flex items-center">
                <i class="fas fa-exclamation-triangle mr-2"></i>
                <span class="text-sm">${this.sanitizeString(message)}</span>
                <button class="ml-4 text-yellow-600 hover:text-yellow-800" onclick="this.parentElement.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;

        document.body.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, 5000);
    },

    // Utility Methods
    generateNonce() {
        const array = new Uint8Array(16);
        crypto.getRandomValues(array);
        return Array.from(array, byte => byte.toString(16).padStart(2, '0')).join('');
    },

    hashString(str) {
        return crypto.subtle.digest('SHA-256', new TextEncoder().encode(str))
            .then(hash => Array.from(new Uint8Array(hash))
                .map(byte => byte.toString(16).padStart(2, '0'))
                .join(''));
    },

    // Public API for manual security checks
    validateUserInput(input) {
        return this.sanitizeString(input);
    },

    isContentSafe(content) {
        const sanitized = this.sanitizeHTML(content);
        return content === sanitized;
    },

    checkCSRFToken() {
        return this.csrfToken !== null;
    }
};

// Initialize security module when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    SecureTrainer.Security.init();
});

// Export for module use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SecureTrainer.Security;
}