/**
 * Demo Challenge Configuration
 * Contains clean, educational payloads for demonstration purposes
 */

window.DEMO_CONFIG = {
    payloads: {
        'sql_injection': "' OR '1'='1' --",
        'xss': '<script>alert("XSS Demo")</script>',
        'command_injection': '; ls -la',
        'authentication': 'admin\' --',
        'csrf': '<form action="/transfer" method="POST"><input name="amount" value="10000"></form>'
    },
    
    hints: {
        'sql_injection': 'This SQL injection payload bypasses authentication by making the WHERE clause always true. The comment (--) ignores any remaining SQL code.',
        'xss': 'This Cross-Site Scripting payload executes JavaScript code when rendered in a web page, potentially stealing cookies or performing unauthorized actions.',
        'command_injection': 'This command injection payload uses a semicolon to chain commands, allowing execution of additional system commands beyond the intended one.',
        'authentication': 'This authentication bypass payload uses SQL injection to comment out the password check, allowing login with just a username.',
        'csrf': 'This Cross-Site Request Forgery payload creates a hidden form that automatically submits a money transfer request when loaded.'
    },
    
    getDemoChallenge(category) {
        return {
            id: category + '_demo_' + Date.now(),
            category: category.replace('_', ' ').toUpperCase(),
            difficulty: 'Demo',
            scenario: `This is a demo ${category.replace('_', ' ')} challenge to help you practice cybersecurity concepts. In a real scenario, this vulnerability could be exploited to compromise system security.`,
            question: `Analyze the payload below and explain how this ${category.replace('_', ' ')} attack works. What are the potential impacts and how could it be prevented?`,
            payload: this.payloads[category] || 'demo payload',
            hint: this.hints[category] || `Think about how ${category.replace('_', ' ')} attacks work and what the payload accomplishes.`,
            score_weight: 10,
            type: category
        };
    }
};