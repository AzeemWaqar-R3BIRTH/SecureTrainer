"""
XSS Challenge Implementation with Sandbox Environment and Live Demonstrations
"""
from flask import Blueprint, request, jsonify, render_template_string, session
from app.models.challenge_model import get_challenge_by_id, record_challenge_attempt
from app.models.user_model import get_user_by_id
from app.routes.ai_model import calculate_dynamic_score
import html
import re
import time
import hashlib

xss_bp = Blueprint('xss_challenges', __name__)

# XSS Challenge Templates for Interactive Demos
XSS_DEMO_TEMPLATES = {
    'basic_xss': '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vulnerable Comment System</title>
        <style>
            .demo-container { max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; }
            .comment-box { background: #f9f9f9; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .input-section { margin: 15px 0; }
            .input-section input { width: 70%; padding: 8px; margin-right: 10px; }
            .input-section button { padding: 8px 15px; background: #007bff; color: white; border: none; border-radius: 3px; cursor: pointer; }
            .warning { background: #fff3cd; padding: 10px; border-radius: 5px; margin: 10px 0; color: #856404; }
        </style>
    </head>
    <body>
        <div class="demo-container">
            <h3>Vulnerable Comment System Demo</h3>
            <div class="warning">
                ⚠️ This is a demonstration of XSS vulnerability. In a real application, this would be dangerous!
            </div>
            <div class="comment-box">
                <strong>Previous Comments:</strong>
                <div id="comments">
                    <p>User1: Great article!</p>
                    <p>User2: Very informative, thanks for sharing.</p>
                </div>
            </div>
            <div class="input-section">
                <input type="text" id="comment-input" placeholder="Enter your comment..." />
                <button onclick="addComment()">Post Comment</button>
                <button onclick="clearComments()">Clear Comments</button>
            </div>
            <div class="warning">
                Try entering: &lt;script&gt;alert('XSS')&lt;/script&gt;
            </div>
        </div>
        <script>
            function addComment() {
                const input = document.getElementById('comment-input');
                const comments = document.getElementById('comments');
                const newComment = document.createElement('p');
                // Vulnerable: Direct innerHTML assignment without sanitization
                newComment.innerHTML = 'Guest: ' + input.value;
                comments.appendChild(newComment);
                input.value = '';
            }
            
            function clearComments() {
                const comments = document.getElementById('comments');
                comments.innerHTML = '<p>User1: Great article!</p><p>User2: Very informative, thanks for sharing.</p>';
            }
        </script>
    </body>
    </html>
    ''',
    
    'reflected_xss': '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Vulnerable Search Page</title>
        <style>
            .demo-container { max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; }
            .search-box { margin: 15px 0; }
            .search-box input { width: 70%; padding: 8px; margin-right: 10px; }
            .search-box button { padding: 8px 15px; background: #28a745; color: white; border: none; border-radius: 3px; cursor: pointer; }
            .results { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .warning { background: #fff3cd; padding: 10px; border-radius: 5px; margin: 10px 0; color: #856404; }
        </style>
    </head>
    <body>
        <div class="demo-container">
            <h3>Vulnerable Search Demo</h3>
            <div class="warning">
                ⚠️ This demonstrates reflected XSS. The search term is reflected without proper encoding.
            </div>
            <div class="search-box">
                <input type="text" id="search-input" placeholder="Enter search term..." />
                <button onclick="performSearch()">Search</button>
            </div>
            <div class="results" id="search-results">
                <p>Enter a search term above to see results.</p>
            </div>
            <div class="warning">
                Try searching for: &lt;img src=x onerror=alert('Reflected XSS')&gt;
            </div>
        </div>
        <script>
            function performSearch() {
                const input = document.getElementById('search-input');
                const results = document.getElementById('search-results');
                const searchTerm = input.value;
                
                if (searchTerm.trim() === '') {
                    results.innerHTML = '<p>Please enter a search term.</p>';
                    return;
                }
                
                // Vulnerable: Direct reflection without encoding
                results.innerHTML = '<h4>Search Results for: ' + searchTerm + '</h4>' +
                                  '<p>No results found for "' + searchTerm + '"</p>' +
                                  '<p>Try refining your search or check the spelling.</p>';
            }
        </script>
    </body>
    </html>
    ''',
    
    'dom_xss': '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>DOM-based XSS Demo</title>
        <style>
            .demo-container { max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; }
            .profile-section { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; }
            .input-section { margin: 15px 0; }
            .input-section input { width: 70%; padding: 8px; margin-right: 10px; }
            .input-section button { padding: 8px 15px; background: #dc3545; color: white; border: none; border-radius: 3px; cursor: pointer; }
            .warning { background: #fff3cd; padding: 10px; border-radius: 5px; margin: 10px 0; color: #856404; }
            .url-info { background: #e9ecef; padding: 10px; border-radius: 5px; font-family: monospace; }
        </style>
    </head>
    <body>
        <div class="demo-container">
            <h3>DOM-based XSS Demo</h3>
            <div class="warning">
                ⚠️ This demonstrates DOM-based XSS where JavaScript processes URL fragments.
            </div>
            <div class="profile-section">
                <h4>User Profile</h4>
                <p>Name: <span id="user-name">Guest User</span></p>
                <p>Bio: <span id="user-bio">Loading...</span></p>
            </div>
            <div class="input-section">
                <input type="text" id="bio-input" placeholder="Enter your bio..." />
                <button onclick="updateBio()">Update Bio</button>
            </div>
            <div class="url-info">
                <strong>URL Fragment:</strong> <span id="current-fragment">#</span>
            </div>
            <div class="warning">
                Try adding to URL: #&lt;img src=x onerror=alert('DOM XSS')&gt;
            </div>
        </div>
        <script>
            function updateBio() {
                const input = document.getElementById('bio-input');
                const bioSpan = document.getElementById('user-bio');
                // Vulnerable: Direct innerHTML assignment
                bioSpan.innerHTML = input.value;
                input.value = '';
            }
            
            function processUrlFragment() {
                const fragment = window.location.hash.substring(1);
                document.getElementById('current-fragment').textContent = '#' + fragment;
                
                if (fragment) {
                    // Vulnerable: Processing URL fragment without sanitization
                    const bioSpan = document.getElementById('user-bio');
                    bioSpan.innerHTML = decodeURIComponent(fragment);
                }
            }
            
            // Process URL fragment on load and hash change
            window.onload = processUrlFragment;
            window.onhashchange = processUrlFragment;
        </script>
    </body>
    </html>
    ''',
    
    'filter_bypass': '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>XSS Filter Bypass Demo</title>
        <style>
            .demo-container { max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #ddd; }
            .filter-info { background: #d1ecf1; padding: 15px; margin: 10px 0; border-radius: 5px; color: #0c5460; }
            .input-section { margin: 15px 0; }
            .input-section input { width: 70%; padding: 8px; margin-right: 10px; }
            .input-section button { padding: 8px 15px; background: #ffc107; color: #212529; border: none; border-radius: 3px; cursor: pointer; }
            .output { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; min-height: 50px; }
            .warning { background: #f8d7da; padding: 10px; border-radius: 5px; margin: 10px 0; color: #721c24; }
        </style>
    </head>
    <body>
        <div class="demo-container">
            <h3>XSS Filter Bypass Demo</h3>
            <div class="filter-info">
                🔒 Basic XSS Filter Active: Removes &lt;script&gt; tags and "javascript:" protocol
            </div>
            <div class="input-section">
                <input type="text" id="payload-input" placeholder="Enter your payload..." />
                <button onclick="testPayload()">Test Payload</button>
            </div>
            <div class="output" id="output">
                <em>Enter a payload above to test against the filter</em>
            </div>
            <div class="warning">
                Try bypassing with: &lt;svg onload=alert('Bypassed!')&gt; or &lt;img src=x onerror=alert(1)&gt;
            </div>
        </div>
        <script>
            function basicXSSFilter(input) {
                // Simple filter that removes script tags and javascript: protocol
                let filtered = input.replace(/<script[^>]*>.*?<\\/script>/gi, '[BLOCKED]');
                filtered = filtered.replace(/javascript:/gi, '[BLOCKED]');
                filtered = filtered.replace(/on\\w+\\s*=/gi, function(match) {
                    // Allow some but not all event handlers (simulating weak filter)
                    if (match.toLowerCase().includes('onload') || 
                        match.toLowerCase().includes('onerror')) {
                        return match; // Bypass: filter misses these
                    }
                    return '[BLOCKED]';
                });
                return filtered;
            }
            
            function testPayload() {
                const input = document.getElementById('payload-input');
                const output = document.getElementById('output');
                const originalPayload = input.value;
                
                if (!originalPayload.trim()) {
                    output.innerHTML = '<em>Please enter a payload</em>';
                    return;
                }
                
                // Apply basic filter
                const filteredPayload = basicXSSFilter(originalPayload);
                
                // Show filtering result
                output.innerHTML = '<strong>Original:</strong> ' + 
                                 '<code>' + originalPayload.replace(/</g, '&lt;').replace(/>/g, '&gt;') + '</code><br>' +
                                 '<strong>After Filter:</strong> ' + 
                                 '<code>' + filteredPayload.replace(/</g, '&lt;').replace(/>/g, '&gt;') + '</code><br>' +
                                 '<strong>Rendered Output:</strong><br>' +
                                 '<div style="border: 1px solid #ccc; padding: 10px; margin: 5px 0;">' + 
                                 filteredPayload + '</div>';
            }
        </script>
    </body>
    </html>
    '''
}


@xss_bp.route('/demo/<demo_type>', methods=['GET'])
def get_xss_demo(demo_type):
    """Get interactive XSS demonstration."""
    try:
        if demo_type not in XSS_DEMO_TEMPLATES:
            return jsonify({
                'success': False,
                'error': 'Demo type not found'
            }), 404
        
        demo_html = XSS_DEMO_TEMPLATES[demo_type]
        
        return jsonify({
            'success': True,
            'demo_type': demo_type,
            'demo_html': demo_html,
            'description': get_demo_description(demo_type)
        }), 200
        
    except Exception as e:
        print(f"Error getting XSS demo: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to load demo'
        }), 500


@xss_bp.route('/sandbox/validate', methods=['POST'])
def validate_xss_payload():
    """Validate XSS payload in a safe sandbox environment."""
    try:
        data = request.json
        payload = data.get('payload', '')
        challenge_id = data.get('challenge_id')
        user_id = data.get('user_id')
        
        if not payload or not challenge_id or not user_id:
            return jsonify({
                'success': False,
                'error': 'Missing required parameters'
            }), 400
        
        # Get challenge and user
        challenge = get_challenge_by_id(challenge_id)
        user = get_user_by_id(user_id)
        
        if not challenge or not user:
            return jsonify({
                'success': False,
                'error': 'Challenge or user not found'
            }), 404
        
        # Validate XSS payload
        validation_result = validate_xss_payload_safely(payload, challenge)
        
        # Record attempt
        completion_time = time.time() - session.get(f'challenge_{challenge_id}_start_time', time.time())
        hints_used = session.get(f'challenge_{challenge_id}_hints_used', 0)
        
        score_earned = 0
        if validation_result['is_valid']:
            score_earned = calculate_dynamic_score(
                user, challenge, completion_time, hints_used, 1
            )
        
        # Record the attempt
        record_challenge_attempt(
            user_id, challenge_id, payload,
            validation_result['is_valid'], completion_time, hints_used
        )
        
        return jsonify({
            'success': True,
            'validation_result': validation_result,
            'score_earned': score_earned
        }), 200
        
    except Exception as e:
        print(f"Error validating XSS payload: {e}")
        return jsonify({
            'success': False,
            'error': 'Validation failed'
        }), 500


@xss_bp.route('/challenges', methods=['GET'])
def get_xss_challenges():
    """Get available XSS challenges."""
    try:
        from app.models.challenge_model import get_xss_challenges as get_challenges
        
        challenges = get_challenges()
        
        # Add demo links to challenges
        for challenge in challenges:
            challenge['demo_available'] = challenge.get('interactive_demo', False)
            if challenge['demo_available']:
                demo_type = get_demo_type_for_challenge(challenge)
                challenge['demo_url'] = f"/api/xss/demo/{demo_type}"
        
        return jsonify({
            'success': True,
            'challenges': challenges
        }), 200
        
    except Exception as e:
        print(f"Error getting XSS challenges: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get challenges'
        }), 500


def validate_xss_payload_safely(payload, challenge):
    """Safely validate XSS payload without executing it."""
    validation_result = {
        'is_valid': False,
        'feedback': '',
        'detected_techniques': [],
        'risk_level': 'low'
    }
    
    # XSS pattern detection
    xss_patterns = [
        (r'<script[^>]*>.*?</script>', 'Script tag injection', 'high'),
        (r'<.*?on\w+\s*=.*?>', 'Event handler injection', 'high'),
        (r'javascript:', 'JavaScript protocol', 'medium'),
        (r'<iframe[^>]*>', 'Iframe injection', 'high'),
        (r'<object[^>]*>', 'Object tag injection', 'medium'),
        (r'<embed[^>]*>', 'Embed tag injection', 'medium'),
        (r'<svg[^>]*onload.*?>', 'SVG with onload', 'high'),
        (r'<img[^>]*onerror.*?>', 'Image with onerror', 'high'),
        (r'<.*?href\s*=\s*["\']?javascript:', 'JavaScript href', 'medium'),
        (r'<.*?src\s*=\s*["\']?javascript:', 'JavaScript src', 'medium'),
        (r'vbscript:', 'VBScript protocol', 'medium'),
        (r'data:.*?base64', 'Data URI with base64', 'medium')
    ]
    
    detected_techniques = []
    max_risk = 'low'
    
    for pattern, technique, risk in xss_patterns:
        if re.search(pattern, payload, re.IGNORECASE):
            detected_techniques.append({
                'technique': technique,
                'risk_level': risk
            })
            if risk == 'high':
                max_risk = 'high'
            elif risk == 'medium' and max_risk != 'high':
                max_risk = 'medium'
    
    validation_result['detected_techniques'] = detected_techniques
    validation_result['risk_level'] = max_risk
    
    # Check against expected solutions
    expected_solutions = challenge.get('expected_solutions', [])
    challenge_type = challenge.get('type', '')
    
    if challenge_type == 'xss' and detected_techniques:
        # Check if detected techniques match expected solutions
        for expected in expected_solutions:
            if expected.lower() in payload.lower():
                validation_result['is_valid'] = True
                validation_result['feedback'] = f"Correct! Detected {technique} technique."
                break
        
        if not validation_result['is_valid'] and detected_techniques:
            validation_result['is_valid'] = True
            validation_result['feedback'] = f"Good! Detected XSS techniques: {', '.join([t['technique'] for t in detected_techniques])}"
    
    if not validation_result['is_valid']:
        validation_result['feedback'] = "No XSS techniques detected. Try using HTML tags with JavaScript event handlers."
    
    return validation_result


def get_demo_description(demo_type):
    """Get description for demo type."""
    descriptions = {
        'basic_xss': 'Demonstrates basic stored XSS in a comment system with no input validation.',
        'reflected_xss': 'Shows reflected XSS where user input is immediately displayed on the page.',
        'dom_xss': 'Illustrates DOM-based XSS using URL fragments and client-side JavaScript.',
        'filter_bypass': 'Tests ability to bypass basic XSS filters using alternative injection methods.'
    }
    return descriptions.get(demo_type, 'XSS demonstration')


def get_demo_type_for_challenge(challenge):
    """Map challenge to appropriate demo type."""
    challenge_id = challenge.get('id', '')
    
    if 'dom' in challenge_id.lower():
        return 'dom_xss'
    elif 'filter' in challenge_id.lower() or 'bypass' in challenge_id.lower():
        return 'filter_bypass'
    elif 'reflected' in challenge_id.lower():
        return 'reflected_xss'
    else:
        return 'basic_xss'