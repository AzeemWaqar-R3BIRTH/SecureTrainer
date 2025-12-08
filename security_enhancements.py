"""
Session Security and User Authentication Enhancements for SecureTrainer
"""
import os
import secrets
import hashlib
import hmac
import time
import jwt
from datetime import datetime, timedelta
from flask import session, request, g, current_app
from functools import wraps
import bcrypt
from typing import Optional, Dict, Any
import ipaddress
from collections import defaultdict, deque
from monitoring_system import securetrainer_logger, handle_security_breach, ErrorType


class SessionSecurityManager:
    \"\"\"Enhanced session security management for SecureTrainer.\"\"\"
    
    def __init__(self):
        self.session_store = {}  # In production, use Redis or database
        self.failed_attempts = defaultdict(lambda: {'count': 0, 'last_attempt': 0})
        self.suspicious_ips = deque(maxlen=1000)
        self.active_sessions = {}
        
        # Security settings
        self.max_failed_attempts = 5
        self.lockout_duration = 900  # 15 minutes
        self.session_timeout = 3600  # 1 hour
        self.max_sessions_per_user = 3
        self.csrf_token_lifetime = 1800  # 30 minutes
    
    def generate_secure_session_id(self) -> str:
        \"\"\"Generate cryptographically secure session ID.\"\"\"
        return secrets.token_urlsafe(32)
    
    def generate_csrf_token(self, user_id: str) -> str:
        \"\"\"Generate CSRF token for user session.\"\"\"
        timestamp = int(time.time())
        data = f\"{user_id}:{timestamp}:{secrets.token_urlsafe(16)}\"
        secret = current_app.secret_key.encode('utf-8')
        signature = hmac.new(secret, data.encode('utf-8'), hashlib.sha256).hexdigest()
        return f\"{data}:{signature}\"
    
    def validate_csrf_token(self, token: str, user_id: str) -> bool:
        \"\"\"Validate CSRF token.\"\"\"
        try:
            parts = token.split(':')
            if len(parts) != 4:
                return False
            
            token_user_id, timestamp, nonce, signature = parts
            
            # Check user ID match
            if token_user_id != user_id:
                return False
            
            # Check timestamp (token expiry)
            if int(time.time()) - int(timestamp) > self.csrf_token_lifetime:
                return False
            
            # Verify signature
            data = f\"{token_user_id}:{timestamp}:{nonce}\"
            secret = current_app.secret_key.encode('utf-8')
            expected_signature = hmac.new(secret, data.encode('utf-8'), hashlib.sha256).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
            
        except Exception as e:
            securetrainer_logger.log_error(
                'CSRF_VALIDATION',
                f\"CSRF token validation error: {str(e)}\",
                e,
                error_type=ErrorType.SECURITY_ERROR
            )
            return False
    
    def create_secure_session(self, user_id: str, user_data: Dict[str, Any]) -> str:
        \"\"\"Create secure session with comprehensive tracking.\"\"\"
        try:
            # Generate session ID
            session_id = self.generate_secure_session_id()
            
            # Check for maximum sessions per user
            user_sessions = [sid for sid, data in self.active_sessions.items() 
                           if data.get('user_id') == user_id]
            
            if len(user_sessions) >= self.max_sessions_per_user:
                # Remove oldest session
                oldest_session = min(user_sessions, 
                                    key=lambda sid: self.active_sessions[sid]['created_at'])
                self.destroy_session(oldest_session)
            
            # Create session data
            session_data = {
                'user_id': user_id,
                'user_data': user_data,
                'created_at': time.time(),
                'last_activity': time.time(),
                'ip_address': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', ''),
                'csrf_token': self.generate_csrf_token(user_id),
                'security_flags': {
                    'ip_verified': True,
                    'user_agent_verified': True,
                    'two_factor_enabled': False  # For future implementation
                }
            }
            
            # Store session
            self.active_sessions[session_id] = session_data
            
            # Set Flask session
            session.permanent = True
            session['session_id'] = session_id
            session['user_id'] = user_id
            session['csrf_token'] = session_data['csrf_token']
            session['created_at'] = session_data['created_at']
            
            # Log session creation
            securetrainer_logger.log_security_event(
                'SESSION_CREATED',
                f\"Secure session created for user {user_id}\",
                {
                    'session_id': session_id[:8] + '***',  # Partial session ID for logging
                    'user_id': user_id,
                    'ip_address': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent', '')
                },
                'INFO'
            )
            
            return session_id
            
        except Exception as e:
            securetrainer_logger.log_error(
                'SESSION_CREATION',
                f\"Error creating secure session: {str(e)}\",
                e,
                error_type=ErrorType.SECURITY_ERROR
            )
            raise
    
    def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        \"\"\"Validate and refresh session if valid.\"\"\"
        try:
            if session_id not in self.active_sessions:
                return None
            
            session_data = self.active_sessions[session_id]
            current_time = time.time()
            
            # Check session timeout
            if current_time - session_data['last_activity'] > self.session_timeout:
                self.destroy_session(session_id)
                securetrainer_logger.log_security_event(
                    'SESSION_TIMEOUT',
                    f\"Session expired for user {session_data['user_id']}\",
                    {'session_id': session_id[:8] + '***'},
                    'INFO'
                )
                return None
            
            # Validate IP address consistency
            if session_data['ip_address'] != request.remote_addr:
                self.destroy_session(session_id)
                handle_security_breach(
                    'IP_ADDRESS_MISMATCH',
                    f\"IP address changed during session: {session_data['ip_address']} -> {request.remote_addr}\",
                    {'session_id': session_id[:8] + '***', 'user_id': session_data['user_id']}
                )
                return None
            
            # Validate User-Agent consistency (basic check)
            current_user_agent = request.headers.get('User-Agent', '')
            if session_data['user_agent'] != current_user_agent:
                # Log suspicious activity but don't terminate session immediately
                securetrainer_logger.log_security_event(
                    'USER_AGENT_CHANGE',
                    f\"User-Agent changed during session\",
                    {
                        'session_id': session_id[:8] + '***',
                        'user_id': session_data['user_id'],
                        'original_ua': session_data['user_agent'][:50],
                        'current_ua': current_user_agent[:50]
                    },
                    'WARNING'
                )
            
            # Update last activity
            session_data['last_activity'] = current_time
            
            return session_data
            
        except Exception as e:
            securetrainer_logger.log_error(
                'SESSION_VALIDATION',
                f\"Error validating session: {str(e)}\",
                e,
                error_type=ErrorType.SECURITY_ERROR
            )
            return None
    
    def destroy_session(self, session_id: str) -> bool:
        \"\"\"Securely destroy session.\"\"\"
        try:
            if session_id in self.active_sessions:
                session_data = self.active_sessions[session_id]
                del self.active_sessions[session_id]
                
                # Clear Flask session
                session.clear()
                
                # Log session destruction
                securetrainer_logger.log_security_event(
                    'SESSION_DESTROYED',
                    f\"Session destroyed for user {session_data['user_id']}\",
                    {'session_id': session_id[:8] + '***'},
                    'INFO'
                )
                
                return True
            
            return False
            
        except Exception as e:
            securetrainer_logger.log_error(
                'SESSION_DESTRUCTION',
                f\"Error destroying session: {str(e)}\",
                e,
                error_type=ErrorType.SECURITY_ERROR
            )
            return False
    
    def check_failed_login_attempts(self, identifier: str) -> bool:
        \"\"\"Check if login attempts should be blocked.\"\"\"
        current_time = time.time()
        attempt_data = self.failed_attempts[identifier]
        
        # Reset counter if lockout period has passed
        if current_time - attempt_data['last_attempt'] > self.lockout_duration:
            attempt_data['count'] = 0
        
        return attempt_data['count'] >= self.max_failed_attempts
    
    def record_failed_login(self, identifier: str, context: Dict[str, Any] = None) -> None:
        \"\"\"Record failed login attempt.\"\"\"
        current_time = time.time()
        self.failed_attempts[identifier]['count'] += 1
        self.failed_attempts[identifier]['last_attempt'] = current_time
        
        # Log security event
        securetrainer_logger.log_security_event(
            'FAILED_LOGIN_ATTEMPT',
            f\"Failed login attempt for {identifier}\",
            {
                'identifier': identifier,
                'attempt_count': self.failed_attempts[identifier]['count'],
                'ip_address': request.remote_addr,
                **(context or {})
            },
            'WARNING'
        )
        
        # Check for brute force attack
        if self.failed_attempts[identifier]['count'] >= self.max_failed_attempts:
            handle_security_breach(
                'BRUTE_FORCE_ATTACK',
                f\"Multiple failed login attempts detected for {identifier}\",
                {
                    'identifier': identifier,
                    'attempt_count': self.failed_attempts[identifier]['count'],
                    'ip_address': request.remote_addr
                }
            )
    
    def reset_failed_attempts(self, identifier: str) -> None:
        \"\"\"Reset failed login attempts after successful login.\"\"\"
        if identifier in self.failed_attempts:
            del self.failed_attempts[identifier]
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        \"\"\"Get session information for monitoring.\"\"\"
        if session_id not in self.active_sessions:
            return None
        
        session_data = self.active_sessions[session_id].copy()
        # Remove sensitive data
        session_data.pop('csrf_token', None)
        session_data.pop('user_data', None)
        
        return session_data


class PasswordSecurityManager:
    \"\"\"Enhanced password security management.\"\"\"
    
    def __init__(self):
        self.min_length = 8
        self.require_uppercase = True
        self.require_lowercase = True
        self.require_numbers = True
        self.require_special = True
        self.max_length = 128
        self.common_passwords = self._load_common_passwords()
    
    def _load_common_passwords(self) -> set:
        \"\"\"Load common passwords list (in production, load from file).\"\"\"
        return {
            'password', '123456', 'password123', 'admin', 'qwerty',
            'letmein', 'welcome', 'monkey', '1234567890', 'abc123'
        }
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        \"\"\"Validate password strength and return detailed feedback.\"\"\"
        validation_result = {
            'is_valid': True,
            'score': 0,
            'feedback': [],
            'strength': 'weak'
        }
        
        # Length check
        if len(password) < self.min_length:
            validation_result['is_valid'] = False
            validation_result['feedback'].append(f'Password must be at least {self.min_length} characters long')
        elif len(password) >= 12:
            validation_result['score'] += 2
        else:
            validation_result['score'] += 1
        
        if len(password) > self.max_length:
            validation_result['is_valid'] = False
            validation_result['feedback'].append(f'Password must not exceed {self.max_length} characters')
        
        # Character requirements
        if self.require_uppercase and not any(c.isupper() for c in password):
            validation_result['is_valid'] = False
            validation_result['feedback'].append('Password must contain at least one uppercase letter')
        elif any(c.isupper() for c in password):
            validation_result['score'] += 1
        
        if self.require_lowercase and not any(c.islower() for c in password):
            validation_result['is_valid'] = False
            validation_result['feedback'].append('Password must contain at least one lowercase letter')
        elif any(c.islower() for c in password):
            validation_result['score'] += 1
        
        if self.require_numbers and not any(c.isdigit() for c in password):
            validation_result['is_valid'] = False
            validation_result['feedback'].append('Password must contain at least one number')
        elif any(c.isdigit() for c in password):
            validation_result['score'] += 1
        
        if self.require_special and not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            validation_result['is_valid'] = False
            validation_result['feedback'].append('Password must contain at least one special character')
        elif any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            validation_result['score'] += 1
        
        # Common password check
        if password.lower() in self.common_passwords:
            validation_result['is_valid'] = False
            validation_result['feedback'].append('Password is too common, please choose a more unique password')
        
        # Calculate strength
        if validation_result['score'] >= 6:
            validation_result['strength'] = 'very_strong'
        elif validation_result['score'] >= 4:
            validation_result['strength'] = 'strong'
        elif validation_result['score'] >= 2:
            validation_result['strength'] = 'medium'
        else:
            validation_result['strength'] = 'weak'
        
        return validation_result
    
    def hash_password(self, password: str) -> str:
        \"\"\"Hash password using bcrypt with strong parameters.\"\"\"
        # Use cost factor of 12 for strong security
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        \"\"\"Verify password against hash.\"\"\"
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            securetrainer_logger.log_error(
                'PASSWORD_VERIFICATION',
                f\"Error verifying password: {str(e)}\",
                e,
                error_type=ErrorType.SECURITY_ERROR
            )
            return False


class SecurityMiddleware:
    \"\"\"Security middleware for request processing.\"\"\"
    
    def __init__(self, app=None):
        self.app = app
        self.session_manager = SessionSecurityManager()
        self.password_manager = PasswordSecurityManager()
        self.rate_limits = defaultdict(lambda: {'count': 0, 'window_start': 0})
        
        # Rate limiting settings
        self.rate_limit_requests = 100  # requests per window
        self.rate_limit_window = 3600   # 1 hour window
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        \"\"\"Initialize security middleware with Flask app.\"\"\"
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        
        # Configure secure session settings
        app.config.update({
            'SESSION_COOKIE_SECURE': True,
            'SESSION_COOKIE_HTTPONLY': True,
            'SESSION_COOKIE_SAMESITE': 'Lax',
            'PERMANENT_SESSION_LIFETIME': timedelta(hours=1)
        })
    
    def before_request(self):
        \"\"\"Process request before handling.\"\"\"
        try:
            # Rate limiting
            if not self.check_rate_limit():
                handle_security_breach(
                    'RATE_LIMIT_EXCEEDED',
                    f\"Rate limit exceeded for IP {request.remote_addr}\",
                    {'ip_address': request.remote_addr, 'endpoint': request.endpoint}
                )
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            # Validate session if present
            session_id = session.get('session_id')
            if session_id:
                session_data = self.session_manager.validate_session(session_id)
                if not session_data:
                    session.clear()
                    return jsonify({'error': 'Invalid session'}), 401
                
                # Store session data in g for use in routes
                g.session_data = session_data
                g.user_id = session_data['user_id']
            
            # CSRF protection for state-changing requests
            if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                if not self.validate_csrf():
                    handle_security_breach(
                        'CSRF_ATTACK',
                        f\"CSRF validation failed for {request.endpoint}\",
                        {'endpoint': request.endpoint, 'method': request.method}
                    )
                    return jsonify({'error': 'CSRF validation failed'}), 403
            
        except Exception as e:
            securetrainer_logger.log_error(
                'SECURITY_MIDDLEWARE',
                f\"Error in before_request: {str(e)}\",
                e,
                error_type=ErrorType.SECURITY_ERROR
            )
    
    def after_request(self, response):
        \"\"\"Process response after handling.\"\"\"
        try:
            # Add security headers
            response.headers.update({
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': 'DENY',
                'X-XSS-Protection': '1; mode=block',
                'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
                'Referrer-Policy': 'strict-origin-when-cross-origin',
                'Content-Security-Policy': \"default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'\"
            })
            
            return response
            
        except Exception as e:
            securetrainer_logger.log_error(
                'SECURITY_MIDDLEWARE',
                f\"Error in after_request: {str(e)}\",
                e,
                error_type=ErrorType.SECURITY_ERROR
            )
            return response
    
    def check_rate_limit(self) -> bool:
        \"\"\"Check if request is within rate limits.\"\"\"
        ip_address = request.remote_addr
        current_time = time.time()
        
        rate_data = self.rate_limits[ip_address]
        
        # Reset window if needed
        if current_time - rate_data['window_start'] > self.rate_limit_window:
            rate_data['count'] = 0
            rate_data['window_start'] = current_time
        
        rate_data['count'] += 1
        
        return rate_data['count'] <= self.rate_limit_requests
    
    def validate_csrf(self) -> bool:
        \"\"\"Validate CSRF token for state-changing requests.\"\"\"
        # Skip CSRF for API endpoints with proper authentication
        if request.endpoint and request.endpoint.startswith('api.'):
            # Check for API key or JWT token
            auth_header = request.headers.get('Authorization')
            if auth_header and (auth_header.startswith('Bearer ') or auth_header.startswith('API-Key ')):
                return True
        
        # Get CSRF token from header or form
        csrf_token = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token')
        
        if not csrf_token:
            return False
        
        # Get user ID from session
        user_id = session.get('user_id')
        if not user_id:
            return False
        
        return self.session_manager.validate_csrf_token(csrf_token, user_id)


def require_secure_auth(require_admin=False):
    \"\"\"Decorator for secure authentication requirement.\"\"\"
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is authenticated
            if 'user_id' not in session:
                securetrainer_logger.log_security_event(
                    'UNAUTHORIZED_ACCESS',
                    f\"Unauthorized access attempt to {request.endpoint}\",
                    {'endpoint': request.endpoint, 'ip_address': request.remote_addr},
                    'WARNING'
                )
                return jsonify({'error': 'Authentication required'}), 401
            
            # Check admin requirement
            if require_admin:
                session_data = getattr(g, 'session_data', {})
                user_data = session_data.get('user_data', {})
                user_role = user_data.get('role', '')
                
                admin_roles = ['admin', 'Department Head', 'Security Architect', 'Chief Security Officer']
                if user_role not in admin_roles:
                    securetrainer_logger.log_security_event(
                        'INSUFFICIENT_PRIVILEGES',
                        f\"Insufficient privileges for {request.endpoint}\",
                        {
                            'endpoint': request.endpoint,
                            'user_id': session.get('user_id'),
                            'user_role': user_role
                        },
                        'WARNING'
                    )
                    return jsonify({'error': 'Insufficient privileges'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Global instances
session_security_manager = SessionSecurityManager()
password_security_manager = PasswordSecurityManager()
security_middleware = SecurityMiddleware()


def initialize_security_system(app):
    \"\"\"Initialize comprehensive security system.\"\"\"
    try:
        # Initialize security middleware
        security_middleware.init_app(app)
        
        # Set up secure session configuration
        app.config.update({
            'SECRET_KEY': os.getenv('SECRET_KEY') or secrets.token_hex(32),
            'SECURITY_PASSWORD_SALT': os.getenv('SECURITY_PASSWORD_SALT') or secrets.token_hex(16),
            'WTF_CSRF_ENABLED': True,
            'WTF_CSRF_TIME_LIMIT': 1800,  # 30 minutes
        })
        
        securetrainer_logger.logger.info(\"Security system initialized successfully\")
        return True
        
    except Exception as e:
        securetrainer_logger.log_error(
            'SECURITY_INITIALIZATION',
            f\"Failed to initialize security system: {str(e)}\",
            e,
            error_type=ErrorType.SECURITY_ERROR
        )
        return False