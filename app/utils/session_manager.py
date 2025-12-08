"""
Unified Session Management for SecureTrainer
Provides consistent and secure session handling across all authentication pathways.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union
from functools import wraps
from flask import session, request, jsonify, redirect, url_for, flash, g
from bson import ObjectId
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SessionManager:
    """
    Unified session management with consistent user handling,
    security features, and automatic cleanup.
    """
    
    def __init__(self, app=None):
        self.app = app
        self.session_timeout = timedelta(hours=24)  # Default session timeout
        self.active_sessions = {}  # In-memory session tracking
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize session management for Flask app."""
        self.app = app
        
        # Configure session settings
        app.config.update(
            SESSION_COOKIE_SECURE=False,  # Set to True in production with HTTPS
            SESSION_COOKIE_HTTPONLY=True,
            SESSION_COOKIE_SAMESITE='Lax',
            PERMANENT_SESSION_LIFETIME=self.session_timeout
        )
        
        # Add session validation middleware
        app.before_request(self.validate_session)
        app.after_request(self.update_session_activity)
        
        logger.info("✅ Session management initialized")
    
    def validate_session(self):
        """Validate current session before each request."""
        if 'user_id' in session:
            # Check session timeout
            last_activity = session.get('last_activity')
            if last_activity:
                try:
                    last_activity_dt = datetime.fromisoformat(last_activity)
                    if datetime.now() - last_activity_dt > self.session_timeout:
                        self.clear_session()
                        logger.info(f"Session expired for user: {session.get('username', 'unknown')}")
                        return
                except (ValueError, TypeError):
                    # Invalid timestamp, clear session
                    self.clear_session()
                    return
            
            # Validate session integrity
            if not self._validate_session_integrity():
                self.clear_session()
                logger.warning("Session integrity check failed")
                return
    
    def update_session_activity(self, response):
        """Update session activity timestamp."""
        if 'user_id' in session:
            session['last_activity'] = datetime.now().isoformat()
            session.permanent = True
        
        return response
    
    def _validate_session_integrity(self) -> bool:
        """Validate session data integrity."""
        required_fields = ['user_id', 'username']
        
        for field in required_fields:
            if field not in session:
                return False
        
        # Additional validation can be added here
        return True
    
    def create_user_session(self, user: Dict[str, Any]) -> bool:
        """
        Create a new user session with standardized data.
        
        Args:
            user: User data from database
            
        Returns:
            True if session created successfully, False otherwise
        """
        try:
            if not user or '_id' not in user:
                logger.error("Cannot create session: Invalid user data")
                return False
            
            # Clear any existing session first
            self.clear_session()
            
            # Create session data
            session_data = {
                'user_id': str(user['_id']),  # Always store as string
                'username': user.get('username', ''),
                'email': user.get('email', ''),
                'level': user.get('level', 1),
                'role': user.get('role', 'Trainee'),
                'score': user.get('score', 0),
                'department': user.get('department', ''),
                'company': user.get('company', ''),
                'session_start': datetime.now().isoformat(),
                'last_activity': datetime.now().isoformat(),
                'login_method': 'qr_code',  # Default, can be overridden
                'session_id': self._generate_session_id()
            }
            
            # Set session data
            for key, value in session_data.items():
                session[key] = value
            
            session.permanent = True
            session.modified = True
            
            # Track active session
            self.active_sessions[session_data['session_id']] = {
                'user_id': session_data['user_id'],
                'username': session_data['username'],
                'start_time': datetime.now(),
                'last_activity': datetime.now()
            }
            
            logger.info(f"✅ Session created for user: {user.get('username', 'unknown')} (ID: {session_data['user_id']})")
            
            # Update user's last login in database
            self._update_user_last_login(user['_id'])
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating user session: {e}")
            return False
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Get current user data from session.
        
        Returns:
            User data dictionary or None if not authenticated
        """
        if 'user_id' not in session:
            return None
        
        try:
            # Get user from database to ensure fresh data
            from app.database.db_manager import find_user_by_id
            user = find_user_by_id(session['user_id'])
            
            if user:
                # Update session with fresh data (except sensitive fields)
                session['level'] = user.get('level', session.get('level', 1))
                session['role'] = user.get('role', session.get('role', 'Trainee'))
                session['score'] = user.get('score', session.get('score', 0))
                session.modified = True
                
                return user
            else:
                # User not found in database, clear session
                logger.warning(f"User {session['user_id']} not found in database, clearing session")
                self.clear_session()
                return None
                
        except Exception as e:
            logger.error(f"Error getting current user: {e}")
            return None
    
    def get_session_info(self) -> Dict[str, Any]:
        """
        Get current session information.
        
        Returns:
            Session information dictionary
        """
        if 'user_id' not in session:
            return {'authenticated': False}
        
        return {
            'authenticated': True,
            'user_id': session.get('user_id'),
            'username': session.get('username'),
            'email': session.get('email'),
            'level': session.get('level'),
            'role': session.get('role'),
            'score': session.get('score'),
            'session_start': session.get('session_start'),
            'last_activity': session.get('last_activity'),
            'login_method': session.get('login_method'),
            'session_id': session.get('session_id')
        }
    
    def update_session_data(self, updates: Dict[str, Any]) -> bool:
        """
        Update session data.
        
        Args:
            updates: Dictionary of updates to apply
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            for key, value in updates.items():
                if key not in ['user_id', 'session_id', 'session_start']:  # Protect critical fields
                    session[key] = value
            
            session['last_activity'] = datetime.now().isoformat()
            session.modified = True
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating session data: {e}")
            return False
    
    def clear_session(self):
        """Clear current user session."""
        session_id = session.get('session_id')
        username = session.get('username', 'unknown')
        
        # Remove from active sessions tracking
        if session_id and session_id in self.active_sessions:
            del self.active_sessions[session_id]
        
        # Clear Flask session
        session.clear()
        
        logger.info(f"🔓 Session cleared for user: {username}")
    
    def is_authenticated(self) -> bool:
        """
        Check if current session is authenticated.
        
        Returns:
            True if authenticated, False otherwise
        """
        return 'user_id' in session and self.get_current_user() is not None
    
    def has_permission(self, required_role: str = None, required_level: int = None) -> bool:
        """
        Check if current user has required permissions.
        
        Args:
            required_role: Required user role
            required_level: Required user level
            
        Returns:
            True if user has required permissions, False otherwise
        """
        if not self.is_authenticated():
            return False
        
        user_role = session.get('role', 'Trainee')
        user_level = session.get('level', 1)
        
        # Role hierarchy
        role_hierarchy = {
            'Trainee': 1,
            'Junior Analyst': 2,
            'Analyst': 3,
            'Senior Analyst': 4,
            'Lead': 5,
            'Department Head': 6,
            'Admin': 10
        }
        
        if required_role:
            user_role_level = role_hierarchy.get(user_role, 1)
            required_role_level = role_hierarchy.get(required_role, 1)
            
            if user_role_level < required_role_level:
                return False
        
        if required_level and user_level < required_level:
            return False
        
        return True
    
    def get_active_sessions_count(self) -> int:
        """Get count of active sessions."""
        # Clean up expired sessions
        self._cleanup_expired_sessions()
        return len(self.active_sessions)
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """Get session statistics."""
        self._cleanup_expired_sessions()
        
        return {
            'active_sessions': len(self.active_sessions),
            'session_timeout_hours': self.session_timeout.total_seconds() / 3600,
            'sessions_by_user': {
                session_data['username']: session_data['user_id'] 
                for session_data in self.active_sessions.values()
            }
        }
    
    def _generate_session_id(self) -> str:
        """Generate unique session ID."""
        import uuid
        return str(uuid.uuid4())
    
    def _update_user_last_login(self, user_id):
        """Update user's last login timestamp in database."""
        try:
            from app.database.db_manager import execute_db_operation
            
            def update_operation(db, uid):
                from bson import ObjectId
                
                # Handle both ObjectId and string formats
                try:
                    if isinstance(uid, str) and ObjectId.is_valid(uid):
                        uid = ObjectId(uid)
                except:
                    pass
                
                return db.users.update_one(
                    {'_id': uid},
                    {'$set': {'last_login': datetime.now()}}
                )
            
            execute_db_operation(update_operation, user_id)
            
        except Exception as e:
            logger.error(f"Error updating user last login: {e}")
    
    def _cleanup_expired_sessions(self):
        """Clean up expired session tracking."""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session_data in self.active_sessions.items():
            if current_time - session_data['last_activity'] > self.session_timeout:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.active_sessions[session_id]
        
        if expired_sessions:
            logger.info(f"Cleaned up {len(expired_sessions)} expired session(s)")

# Global session manager instance
session_manager = None

def initialize_session_manager(app) -> SessionManager:
    """
    Initialize global session manager.
    
    Args:
        app: Flask application instance
        
    Returns:
        SessionManager instance
    """
    global session_manager
    session_manager = SessionManager(app)
    return session_manager

def get_session_manager() -> Optional[SessionManager]:
    """Get global session manager instance."""
    return session_manager

# Authentication decorators

def require_auth(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session_manager or not session_manager.is_authenticated():
            logger.info(f"Unauthenticated access attempt to {request.endpoint}")
            
            if request.is_json:
                return jsonify({
                    'success': False,
                    'error': 'Authentication required',
                    'redirect_url': '/login'
                }), 401
            
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    
    decorated_function.__name__ = f.__name__
    return decorated_function

def require_role(required_role: str):
    """Decorator to require specific user role."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session_manager or not session_manager.has_permission(required_role=required_role):
                logger.warning(f"Insufficient permissions for {request.endpoint}: required role {required_role}")
                
                if request.is_json:
                    return jsonify({
                        'success': False,
                        'error': f'Role {required_role} required',
                        'current_role': session.get('role', 'None')
                    }), 403
                
                flash(f'Access denied. Role {required_role} required.', 'error')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        
        decorated_function.__name__ = f.__name__
        return decorated_function
    
    return decorator

def require_level(required_level: int):
    """Decorator to require minimum user level."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session_manager or not session_manager.has_permission(required_level=required_level):
                logger.warning(f"Insufficient level for {request.endpoint}: required level {required_level}")
                
                if request.is_json:
                    return jsonify({
                        'success': False,
                        'error': f'Level {required_level} required',
                        'current_level': session.get('level', 0)
                    }), 403
                
                flash(f'Access denied. Level {required_level} required.', 'error')
                return redirect(url_for('dashboard'))
            
            return f(*args, **kwargs)
        
        decorated_function.__name__ = f.__name__
        return decorated_function
    
    return decorator

# Helper functions for templates and views

def get_current_user():
    """Get current authenticated user."""
    if session_manager:
        return session_manager.get_current_user()
    return None

def get_current_session():
    """Get current session information."""
    if session_manager:
        return session_manager.get_session_info()
    return {'authenticated': False}

def login_user(user: Dict[str, Any], login_method: str = 'qr_code') -> bool:
    """
    Log in a user and create session.
    
    Args:
        user: User data from database
        login_method: Method used for login
        
    Returns:
        True if login successful, False otherwise
    """
    if session_manager:
        success = session_manager.create_user_session(user)
        if success:
            session_manager.update_session_data({'login_method': login_method})
        return success
    return False

def logout_user():
    """Log out current user and clear session."""
    if session_manager:
        session_manager.clear_session()

def update_user_session(updates: Dict[str, Any]) -> bool:
    """
    Update current user session.
    
    Args:
        updates: Dictionary of updates to apply
        
    Returns:
        True if update successful, False otherwise
    """
    if session_manager:
        return session_manager.update_session_data(updates)
    return False