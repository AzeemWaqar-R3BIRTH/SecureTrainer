"""
Authentication Vulnerability Challenges with QR Code Integration
"""
from flask import Blueprint, request, jsonify, session
from app.models.challenge_model import get_challenge_by_id, record_challenge_attempt
from app.models.user_model import get_user_by_id
from app.routes.ai_model import calculate_dynamic_score
from app.utils.qr import QRCodeManager
import re
import time
import hashlib
import secrets
import base64
from datetime import datetime, timedelta

auth_challenges_bp = Blueprint('auth_challenges', __name__)
qr_manager = QRCodeManager()

# Simulate user database for authentication challenges
SIMULATED_USERS = {
    'admin': {'password': 'admin123', 'role': 'admin', 'id': 1},
    'user': {'password': 'password', 'role': 'user', 'id': 2},
    'guest': {'password': 'guest', 'role': 'guest', 'id': 3},
    'john_doe': {'password': 'john123', 'role': 'user', 'id': 4},
    'jane_admin': {'password': 'jane456', 'role': 'admin', 'id': 5}
}


@auth_challenges_bp.route('/demo/<demo_type>', methods=['GET'])
def get_auth_demo(demo_type):
    """Get interactive authentication vulnerability demonstration."""
    demo_types = ['sql_injection_login', 'weak_session', 'qr_authentication']
    
    if demo_type not in demo_types:
        return jsonify({
            'success': False,
            'error': 'Demo type not found'
        }), 404
    
    return jsonify({
        'success': True,
        'demo_type': demo_type,
        'description': f'Authentication vulnerability demo: {demo_type}'
    }), 200


@auth_challenges_bp.route('/simulate-login', methods=['POST'])
def simulate_vulnerable_login():
    """Simulate vulnerable login for authentication challenges."""
    try:
        data = request.json
        username = data.get('username', '')
        password = data.get('password', '')
        challenge_id = data.get('challenge_id')
        user_id = data.get('user_id')
        
        if not challenge_id or not user_id:
            return jsonify({
                'success': False,
                'error': 'Missing challenge_id or user_id'
            }), 400
        
        # Check for SQL injection patterns
        is_injection = check_sql_injection_bypass(username, password)
        
        auth_result = {
            'authenticated': is_injection or (username in SIMULATED_USERS and SIMULATED_USERS[username]['password'] == password),
            'vulnerability_detected': is_injection,
            'bypass_method': 'SQL Injection' if is_injection else 'Valid Credentials'
        }
        
        # Calculate score if successful
        score_earned = 0
        if is_injection:
            challenge = get_challenge_by_id(challenge_id)
            user = get_user_by_id(user_id)
            
            if challenge and user:
                completion_time = time.time() - session.get(f'challenge_{challenge_id}_start_time', time.time())
                hints_used = session.get(f'challenge_{challenge_id}_hints_used', 0)
                
                score_earned = calculate_dynamic_score(
                    user, challenge, completion_time, hints_used, 1
                )
                
                # Record the attempt
                record_challenge_attempt(
                    user_id, challenge_id, f"username: {username}, password: {password}",
                    True, completion_time, hints_used
                )
        
        return jsonify({
            'success': True,
            'auth_result': auth_result,
            'score_earned': score_earned
        }), 200
        
    except Exception as e:
        print(f"Error simulating login: {e}")
        return jsonify({
            'success': False,
            'error': 'Login simulation failed'
        }), 500


def check_sql_injection_bypass(username, password):
    """Check if the login attempt uses SQL injection."""
    injection_patterns = [
        "' OR '1'='1",
        "' OR 1=1",
        "admin' --",
        "' OR 'a'='a",
        "' UNION SELECT"
    ]
    
    for pattern in injection_patterns:
        if pattern.lower() in username.lower() or pattern.lower() in password.lower():
            return True
    
    return False