"""
Enhanced Error Handling Framework for SecureTrainer
Provides comprehensive error handling, graceful degradation, and user-friendly error communication.
"""

import os
import sys
import logging
import traceback
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from functools import wraps
from flask import Flask, request, jsonify, render_template, redirect, url_for, flash, session, g
from werkzeug.exceptions import HTTPException
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorCategory:
    """Error categories for classification."""
    DATABASE = "database"
    AUTHENTICATION = "authentication"
    VALIDATION = "validation"
    SYSTEM = "system"
    AI_SERVICE = "ai_service"
    NETWORK = "network"
    PERMISSION = "permission"

class ErrorSeverity:
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SystemError:
    """Structured error representation."""
    
    def __init__(self, 
                 error_code: str, 
                 message: str, 
                 category: str = ErrorCategory.SYSTEM,
                 severity: str = ErrorSeverity.MEDIUM,
                 details: Optional[Dict[str, Any]] = None,
                 user_message: Optional[str] = None,
                 recovery_suggestions: Optional[list] = None):
        
        self.error_code = error_code
        self.message = message
        self.category = category
        self.severity = severity
        self.details = details or {}
        self.user_message = user_message or self._generate_user_message()
        self.recovery_suggestions = recovery_suggestions or []
        self.timestamp = datetime.now()
        self.request_id = getattr(g, 'request_id', None)
    
    def _generate_user_message(self) -> str:
        """Generate user-friendly message based on error category."""
        user_messages = {
            ErrorCategory.DATABASE: "We're experiencing database connectivity issues. Please try again in a moment.",
            ErrorCategory.AUTHENTICATION: "There was an issue with authentication. Please log in again.",
            ErrorCategory.VALIDATION: "The information provided doesn't meet our requirements. Please check and try again.",
            ErrorCategory.SYSTEM: "We're experiencing technical difficulties. Our team has been notified.",
            ErrorCategory.AI_SERVICE: "Our AI services are temporarily unavailable. You can continue with basic features.",
            ErrorCategory.NETWORK: "Network connectivity issues detected. Please check your connection.",
            ErrorCategory.PERMISSION: "You don't have permission to access this resource."
        }
        
        return user_messages.get(self.category, "An unexpected error occurred. Please try again.")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary representation."""
        return {
            'error_code': self.error_code,
            'message': self.message,
            'category': self.category,
            'severity': self.severity,
            'user_message': self.user_message,
            'details': self.details,
            'recovery_suggestions': self.recovery_suggestions,
            'timestamp': self.timestamp.isoformat(),
            'request_id': self.request_id
        }

class ErrorHandler:
    """Central error handling manager."""
    
    def __init__(self, app: Flask = None):
        self.app = app
        self.error_log = []
        self.error_stats = {
            'total_errors': 0,
            'by_category': {},
            'by_severity': {},
            'recent_errors': []
        }
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize error handling for Flask app."""
        self.app = app
        
        # Register error handlers
        app.errorhandler(400)(self.handle_bad_request)
        app.errorhandler(401)(self.handle_unauthorized)
        app.errorhandler(403)(self.handle_forbidden)
        app.errorhandler(404)(self.handle_not_found)
        app.errorhandler(405)(self.handle_method_not_allowed)
        app.errorhandler(500)(self.handle_internal_error)
        app.errorhandler(503)(self.handle_service_unavailable)
        app.errorhandler(Exception)(self.handle_generic_exception)
        
        # Add request ID middleware
        app.before_request(self.generate_request_id)
        
        # Add error logging
        app.after_request(self.log_response_errors)
    
    def generate_request_id(self):
        """Generate unique request ID for tracking."""
        import uuid
        g.request_id = str(uuid.uuid4())[:8]
    
    def log_response_errors(self, response):
        """Log response errors for monitoring."""
        if response.status_code >= 400:
            self.log_error(
                f"HTTP {response.status_code}",
                f"Request failed: {request.url}",
                ErrorCategory.SYSTEM,
                ErrorSeverity.LOW if response.status_code < 500 else ErrorSeverity.HIGH,
                {
                    'url': request.url,
                    'method': request.method,
                    'status_code': response.status_code,
                    'user_agent': request.headers.get('User-Agent', ''),
                    'ip_address': request.remote_addr
                }
            )
        
        return response
    
    def log_error(self, error_code: str, message: str, category: str, severity: str, details: Dict[str, Any] = None):
        """Log error with structured information."""
        error = SystemError(error_code, message, category, severity, details)
        
        # Add to error log
        self.error_log.append(error)
        
        # Update statistics
        self.error_stats['total_errors'] += 1
        self.error_stats['by_category'][category] = self.error_stats['by_category'].get(category, 0) + 1
        self.error_stats['by_severity'][severity] = self.error_stats['by_severity'].get(severity, 0) + 1
        self.error_stats['recent_errors'].append(error.to_dict())
        
        # Keep only recent errors (last 100)
        if len(self.error_stats['recent_errors']) > 100:
            self.error_stats['recent_errors'] = self.error_stats['recent_errors'][-100:]
        
        # Log to application logger
        log_level = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }.get(severity, logging.ERROR)
        
        logger.log(log_level, f"[{error.request_id}] {error_code}: {message} | Details: {details}")
        
        return error
    
    def handle_bad_request(self, error):
        """Handle 400 Bad Request errors."""
        system_error = self.log_error(
            "BAD_REQUEST",
            "Invalid request format or parameters",
            ErrorCategory.VALIDATION,
            ErrorSeverity.LOW,
            {'original_error': str(error)}
        )
        
        if request.is_json:
            return jsonify({
                'success': False,
                'error': system_error.to_dict()
            }), 400
        
        flash(system_error.user_message, 'error')
        return render_template('400.html', error=system_error), 400
    
    def handle_unauthorized(self, error):
        """Handle 401 Unauthorized errors."""
        system_error = self.log_error(
            "UNAUTHORIZED",
            "Authentication required",
            ErrorCategory.AUTHENTICATION,
            ErrorSeverity.MEDIUM,
            {'original_error': str(error)}
        )
        
        if request.is_json:
            return jsonify({
                'success': False,
                'error': system_error.to_dict(),
                'redirect_url': '/login'
            }), 401
        
        flash("Please log in to access this page.", 'error')
        return redirect(url_for('login'))
    
    def handle_forbidden(self, error):
        """Handle 403 Forbidden errors."""
        system_error = self.log_error(
            "FORBIDDEN",
            "Access denied",
            ErrorCategory.PERMISSION,
            ErrorSeverity.MEDIUM,
            {'original_error': str(error)}
        )
        
        if request.is_json:
            return jsonify({
                'success': False,
                'error': system_error.to_dict()
            }), 403
        
        flash(system_error.user_message, 'error')
        return render_template('403.html', error=system_error), 403
    
    def handle_not_found(self, error):
        """Handle 404 Not Found errors."""
        system_error = self.log_error(
            "NOT_FOUND",
            f"Resource not found: {request.url}",
            ErrorCategory.SYSTEM,
            ErrorSeverity.LOW,
            {'url': request.url, 'method': request.method}
        )
        
        if request.is_json:
            return jsonify({
                'success': False,
                'error': system_error.to_dict()
            }), 404
        
        return render_template('404.html', error=system_error), 404
    
    def handle_method_not_allowed(self, error):
        """Handle 405 Method Not Allowed errors."""
        system_error = self.log_error(
            "METHOD_NOT_ALLOWED",
            f"Method {request.method} not allowed for {request.url}",
            ErrorCategory.VALIDATION,
            ErrorSeverity.LOW,
            {'method': request.method, 'url': request.url}
        )
        
        if request.is_json:
            return jsonify({
                'success': False,
                'error': system_error.to_dict()
            }), 405
        
        flash("Invalid request method for this page.", 'error')
        return redirect(url_for('index'))
    
    def handle_internal_error(self, error):
        """Handle 500 Internal Server errors."""
        error_details = {
            'traceback': traceback.format_exc(),
            'url': request.url,
            'method': request.method,
            'original_error': str(error)
        }
        
        system_error = self.log_error(
            "INTERNAL_ERROR",
            "Internal server error occurred",
            ErrorCategory.SYSTEM,
            ErrorSeverity.HIGH,
            error_details
        )
        
        if request.is_json:
            return jsonify({
                'success': False,
                'error': {
                    'error_code': system_error.error_code,
                    'user_message': system_error.user_message,
                    'request_id': system_error.request_id
                }
            }), 500
        
        return render_template('500.html', error=system_error), 500
    
    def handle_service_unavailable(self, error):
        """Handle 503 Service Unavailable errors."""
        system_error = self.log_error(
            "SERVICE_UNAVAILABLE",
            "Service temporarily unavailable",
            ErrorCategory.SYSTEM,
            ErrorSeverity.HIGH,
            {'original_error': str(error)}
        )
        
        if request.is_json:
            return jsonify({
                'success': False,
                'error': system_error.to_dict()
            }), 503
        
        return render_template('503.html', error=system_error), 503
    
    def handle_generic_exception(self, error):
        """Handle any unhandled exception."""
        if isinstance(error, HTTPException):
            # Let HTTP exceptions be handled by their specific handlers
            raise error
        
        error_details = {
            'error_type': type(error).__name__,
            'traceback': traceback.format_exc(),
            'url': request.url,
            'method': request.method
        }
        
        system_error = self.log_error(
            "UNHANDLED_EXCEPTION",
            f"Unhandled exception: {str(error)}",
            ErrorCategory.SYSTEM,
            ErrorSeverity.CRITICAL,
            error_details
        )
        
        if request.is_json:
            return jsonify({
                'success': False,
                'error': {
                    'error_code': system_error.error_code,
                    'user_message': system_error.user_message,
                    'request_id': system_error.request_id
                }
            }), 500
        
        return render_template('500.html', error=system_error), 500
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for monitoring."""
        return {
            'total_errors': self.error_stats['total_errors'],
            'by_category': self.error_stats['by_category'],
            'by_severity': self.error_stats['by_severity'],
            'recent_errors_count': len(self.error_stats['recent_errors']),
            'last_updated': datetime.now().isoformat()
        }

class GracefulDegradation:
    """Handles graceful service degradation."""
    
    def __init__(self):
        self.service_status = {
            'database': True,
            'ai_system': True,
            'email_service': True,
            'qr_service': True
        }
        self.degraded_features = set()
    
    def mark_service_down(self, service_name: str, reason: str = ""):
        """Mark a service as unavailable."""
        self.service_status[service_name] = False
        logger.warning(f"Service {service_name} marked as down: {reason}")
        
        # Add degraded features based on service
        if service_name == 'database':
            self.degraded_features.update(['user_progress', 'leaderboard', 'analytics'])
        elif service_name == 'ai_system':
            self.degraded_features.update(['adaptive_challenges', 'smart_hints', 'personalization'])
        elif service_name == 'email_service':
            self.degraded_features.update(['registration_email', 'notifications'])
        elif service_name == 'qr_service':
            self.degraded_features.update(['qr_login', 'qr_generation'])
    
    def mark_service_up(self, service_name: str):
        """Mark a service as available."""
        self.service_status[service_name] = True
        logger.info(f"Service {service_name} restored")
        
        # Remove degraded features if service is restored
        if service_name == 'database':
            self.degraded_features.discard('user_progress')
            self.degraded_features.discard('leaderboard')
            self.degraded_features.discard('analytics')
        elif service_name == 'ai_system':
            self.degraded_features.discard('adaptive_challenges')
            self.degraded_features.discard('smart_hints')
            self.degraded_features.discard('personalization')
        elif service_name == 'email_service':
            self.degraded_features.discard('registration_email')
            self.degraded_features.discard('notifications')
        elif service_name == 'qr_service':
            self.degraded_features.discard('qr_login')
            self.degraded_features.discard('qr_generation')
    
    def is_feature_available(self, feature_name: str) -> bool:
        """Check if a feature is available."""
        return feature_name not in self.degraded_features
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status."""
        return {
            'services': self.service_status,
            'degraded_features': list(self.degraded_features),
            'overall_health': 'healthy' if not self.degraded_features else 'degraded'
        }

# Decorators for error handling

def handle_database_errors(fallback_value=None):
    """Decorator to handle database operation errors."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Database error in {func.__name__}: {e}")
                if 'error_handler' in globals():
                    error_handler.log_error(
                        "DATABASE_ERROR",
                        f"Database operation failed in {func.__name__}",
                        ErrorCategory.DATABASE,
                        ErrorSeverity.HIGH,
                        {'function': func.__name__, 'error': str(e)}
                    )
                return fallback_value
        return wrapper
    return decorator

def handle_ai_errors(fallback_value=None):
    """Decorator to handle AI service errors."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"AI service error in {func.__name__}: {e}")
                if 'error_handler' in globals():
                    error_handler.log_error(
                        "AI_SERVICE_ERROR",
                        f"AI operation failed in {func.__name__}",
                        ErrorCategory.AI_SERVICE,
                        ErrorSeverity.MEDIUM,
                        {'function': func.__name__, 'error': str(e)}
                    )
                return fallback_value
        return wrapper
    return decorator

def require_service(service_name: str, fallback_response=None):
    """Decorator to require a service to be available."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'degradation_manager' in globals():
                if not degradation_manager.service_status.get(service_name, False):
                    if request.is_json:
                        return jsonify({
                            'success': False,
                            'error': f'Service {service_name} is currently unavailable',
                            'service_status': degradation_manager.get_status()
                        }), 503
                    
                    flash(f'This feature is temporarily unavailable due to {service_name} issues.', 'warning')
                    return fallback_response or redirect(url_for('index'))
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Global instances
error_handler = None
degradation_manager = None

def initialize_error_handling(app: Flask):
    """Initialize error handling for the application."""
    global error_handler, degradation_manager
    
    error_handler = ErrorHandler(app)
    degradation_manager = GracefulDegradation()
    
    # Add context processors for templates
    @app.context_processor
    def inject_system_status():
        from flask import session
        from app.models.user_model import get_user_by_id
        
        # Get current user from session
        user = None
        user_id = session.get('user_id')
        if user_id:
            try:
                user = get_user_by_id(user_id)
            except:
                pass
        
        return {
            'system_status': degradation_manager.get_status() if degradation_manager else {'overall_health': 'unknown'},
            'degraded_features': degradation_manager.degraded_features if degradation_manager else set(),
            'user': user  # Make user available in all templates
        }
    
    logger.info("✅ Error handling framework initialized")
    return error_handler, degradation_manager