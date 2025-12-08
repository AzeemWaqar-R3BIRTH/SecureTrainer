"""
Comprehensive Error Handling and Monitoring System for SecureTrainer
"""
import logging
import traceback
import functools
import time
import os
from datetime import datetime
from flask import request, session, jsonify, g
from pymongo import MongoClient
from enum import Enum
import psutil
import threading
from collections import defaultdict, deque


class LogLevel(Enum):
    DEBUG = \"DEBUG\"
    INFO = \"INFO\"
    WARNING = \"WARNING\"
    ERROR = \"ERROR\"
    CRITICAL = \"CRITICAL\"


class ErrorType(Enum):
    DATABASE_ERROR = \"DATABASE_ERROR\"
    VALIDATION_ERROR = \"VALIDATION_ERROR\"
    AUTHENTICATION_ERROR = \"AUTHENTICATION_ERROR\"
    AUTHORIZATION_ERROR = \"AUTHORIZATION_ERROR\"
    CHALLENGE_ERROR = \"CHALLENGE_ERROR\"
    AI_MODEL_ERROR = \"AI_MODEL_ERROR\"
    EMAIL_ERROR = \"EMAIL_ERROR\"
    QR_CODE_ERROR = \"QR_CODE_ERROR\"
    PERFORMANCE_ERROR = \"PERFORMANCE_ERROR\"
    SECURITY_ERROR = \"SECURITY_ERROR\"
    SYSTEM_ERROR = \"SYSTEM_ERROR\"


class SecurityTrainerLogger:
    \"\"\"Centralized logging system for SecureTrainer.\"\"\"
    
    def __init__(self):
        self.mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/securetrainer')
        self.client = None
        self.db = None
        self.setup_logging()
        self.connect_db()
        
        # Performance monitoring
        self.request_times = deque(maxlen=1000)
        self.error_counts = defaultdict(int)
        self.performance_alerts = deque(maxlen=100)
    
    def setup_logging(self):
        \"\"\"Setup file-based logging.\"\"\"
        # Create logs directory if it doesn't exist
        logs_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(logs_dir, exist_ok=True)
        
        # Configure logging
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        
        # Main application log
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(os.path.join(logs_dir, 'securetrainer.log')),
                logging.StreamHandler()
            ]
        )
        
        # Error log
        error_handler = logging.FileHandler(os.path.join(logs_dir, 'errors.log'))
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(logging.Formatter(log_format))
        
        # Security log
        security_handler = logging.FileHandler(os.path.join(logs_dir, 'security.log'))
        security_handler.setLevel(logging.WARNING)
        security_handler.setFormatter(logging.Formatter(log_format))
        
        # Performance log
        perf_handler = logging.FileHandler(os.path.join(logs_dir, 'performance.log'))
        perf_handler.setLevel(logging.INFO)
        perf_handler.setFormatter(logging.Formatter(log_format))
        
        # Create specialized loggers
        self.logger = logging.getLogger('securetrainer')
        self.error_logger = logging.getLogger('securetrainer.errors')
        self.error_logger.addHandler(error_handler)
        self.security_logger = logging.getLogger('securetrainer.security')
        self.security_logger.addHandler(security_handler)
        self.perf_logger = logging.getLogger('securetrainer.performance')
        self.perf_logger.addHandler(perf_handler)
    
    def connect_db(self):
        \"\"\"Connect to MongoDB for log storage.\"\"\"
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client.securetrainer
        except Exception as e:
            self.logger.error(f\"Failed to connect to MongoDB for logging: {e}\")
    
    def log_to_database(self, level, component, message, context=None, error_type=None):
        \"\"\"Log message to database.\"\"\"
        if not self.db:
            return
        
        try:
            log_entry = {
                'timestamp': datetime.now(),
                'level': level.value if isinstance(level, LogLevel) else level,
                'component': component,
                'message': message,
                'context': context or {},
                'error_type': error_type.value if isinstance(error_type, ErrorType) else error_type,
                'request_id': getattr(g, 'request_id', None),
                'user_id': session.get('user_id'),
                'ip_address': request.remote_addr if request else None,
                'user_agent': request.headers.get('User-Agent') if request else None
            }
            
            self.db.system_logs.insert_one(log_entry)
            
        except Exception as e:
            self.logger.error(f\"Failed to log to database: {e}\")
    
    def log_error(self, component, message, exception=None, context=None, error_type=ErrorType.SYSTEM_ERROR):
        \"\"\"Log error with full context.\"\"\"
        error_context = context or {}
        
        if exception:
            error_context.update({
                'exception_type': type(exception).__name__,
                'exception_message': str(exception),
                'traceback': traceback.format_exc()
            })
        
        # Log to file
        self.error_logger.error(f\"{component}: {message}\", extra=error_context)
        
        # Log to database
        self.log_to_database(LogLevel.ERROR, component, message, error_context, error_type)
        
        # Update error counts
        self.error_counts[error_type] += 1
        
        # Check for error rate alerts
        self.check_error_rate_alerts(error_type)
    
    def log_security_event(self, event_type, message, context=None, severity=\"WARNING\"):
        \"\"\"Log security-related events.\"\"\"
        security_context = context or {}
        security_context.update({
            'event_type': event_type,
            'severity': severity,
            'timestamp': datetime.now().isoformat()
        })
        
        # Log to security file
        self.security_logger.warning(f\"SECURITY: {event_type} - {message}\", extra=security_context)
        
        # Log to database
        self.log_to_database(LogLevel.WARNING, 'SECURITY', message, security_context, ErrorType.SECURITY_ERROR)
    
    def log_performance(self, component, message, metrics=None):
        \"\"\"Log performance metrics.\"\"\"
        perf_context = metrics or {}
        perf_context['component'] = component
        
        # Log to performance file
        self.perf_logger.info(f\"PERF: {component} - {message}\", extra=perf_context)
        
        # Log to database
        self.log_to_database(LogLevel.INFO, 'PERFORMANCE', message, perf_context)
    
    def check_error_rate_alerts(self, error_type):
        \"\"\"Check if error rate exceeds thresholds.\"\"\"
        error_threshold = 10  # 10 errors of same type in 5 minutes
        time_window = 300  # 5 minutes
        
        current_time = time.time()
        
        # Clean old error counts (simplified implementation)
        if self.error_counts[error_type] > error_threshold:
            alert_message = f\"High error rate detected: {error_type.value} - {self.error_counts[error_type]} errors\"
            self.performance_alerts.append({
                'timestamp': current_time,
                'type': 'ERROR_RATE_HIGH',
                'message': alert_message,
                'error_type': error_type.value,
                'count': self.error_counts[error_type]
            })
            
            # Reset counter after alert
            self.error_counts[error_type] = 0


# Global logger instance
securetrainer_logger = SecurityTrainerLogger()


def error_handler(error_type=ErrorType.SYSTEM_ERROR, log_args=True):
    \"\"\"Decorator for comprehensive error handling.\"\"\"
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                # Log function call if requested
                if log_args:
                    securetrainer_logger.logger.debug(
                        f\"Calling {func.__name__} with args: {args[:2]}..., kwargs: {list(kwargs.keys())}\"
                    )
                
                result = func(*args, **kwargs)
                
                # Log performance
                execution_time = time.time() - start_time
                if execution_time > 1.0:  # Log slow operations
                    securetrainer_logger.log_performance(
                        func.__name__,
                        f\"Slow execution detected\",
                        {'execution_time': execution_time}
                    )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                # Prepare error context
                error_context = {
                    'function': func.__name__,
                    'execution_time': execution_time,
                    'args_count': len(args),
                    'kwargs_keys': list(kwargs.keys())
                }
                
                # Add request context if available
                if request:
                    error_context.update({
                        'endpoint': request.endpoint,
                        'method': request.method,
                        'url': request.url
                    })
                
                # Log the error
                securetrainer_logger.log_error(
                    func.__name__,
                    f\"Error in {func.__name__}: {str(e)}\",
                    e,
                    error_context,
                    error_type
                )
                
                # Re-raise the exception
                raise
                
        return wrapper
    return decorator


def monitor_request_performance():
    \"\"\"Decorator to monitor request performance.\"\"\"
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                # Generate request ID
                g.request_id = f\"req_{int(time.time())}_{id(request)}\"
                
                result = func(*args, **kwargs)
                
                # Log successful request
                execution_time = time.time() - start_time
                securetrainer_logger.request_times.append(execution_time)
                
                # Log performance metrics
                if execution_time > 2.0:  # Log slow requests
                    securetrainer_logger.log_performance(
                        'REQUEST',
                        f\"Slow request: {request.endpoint}\",
                        {
                            'execution_time': execution_time,
                            'endpoint': request.endpoint,
                            'method': request.method,
                            'status': 'SUCCESS'
                        }
                    )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                
                # Log failed request
                securetrainer_logger.log_error(
                    'REQUEST',
                    f\"Request failed: {request.endpoint}\",
                    e,
                    {
                        'execution_time': execution_time,
                        'endpoint': request.endpoint,
                        'method': request.method,
                        'status': 'FAILED'
                    },
                    ErrorType.SYSTEM_ERROR
                )
                
                raise
                
        return wrapper
    return decorator


def security_monitor(event_type):
    \"\"\"Decorator to monitor security events.\"\"\"
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                
                # Log successful security operation
                securetrainer_logger.log_security_event(
                    event_type,
                    f\"Security operation successful: {func.__name__}\",
                    {
                        'function': func.__name__,
                        'user_id': session.get('user_id'),
                        'status': 'SUCCESS'
                    },
                    'INFO'
                )
                
                return result
                
            except Exception as e:
                # Log security failure
                securetrainer_logger.log_security_event(
                    event_type,
                    f\"Security operation failed: {func.__name__} - {str(e)}\",
                    {
                        'function': func.__name__,
                        'user_id': session.get('user_id'),
                        'status': 'FAILED',
                        'error': str(e)
                    },
                    'ERROR'
                )
                
                raise
                
        return wrapper
    return decorator


class SystemMonitor:
    \"\"\"Real-time system monitoring and alerting.\"\"\"
    
    def __init__(self):
        self.monitoring_active = False
        self.monitor_thread = None
        self.alerts = deque(maxlen=100)
        
        # Thresholds
        self.cpu_threshold = 80.0  # 80%
        self.memory_threshold = 85.0  # 85%
        self.disk_threshold = 90.0  # 90%
        self.response_time_threshold = 2.0  # 2 seconds
    
    def start_monitoring(self):
        \"\"\"Start system monitoring in background thread.\"\"\"
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            securetrainer_logger.logger.info(\"System monitoring started\")
    
    def stop_monitoring(self):
        \"\"\"Stop system monitoring.\"\"\"
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        securetrainer_logger.logger.info(\"System monitoring stopped\")
    
    def _monitor_loop(self):
        \"\"\"Main monitoring loop.\"\"\"
        while self.monitoring_active:
            try:
                self._check_system_resources()
                self._check_response_times()
                self._check_error_rates()
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                securetrainer_logger.log_error(
                    'SYSTEM_MONITOR',
                    f\"Error in monitoring loop: {str(e)}\",
                    e,
                    error_type=ErrorType.SYSTEM_ERROR
                )
                time.sleep(60)  # Wait longer if there's an error
    
    def _check_system_resources(self):
        \"\"\"Check system resource usage.\"\"\"
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > self.cpu_threshold:
                self._create_alert('HIGH_CPU', f\"CPU usage: {cpu_percent:.1f}%\", 'WARNING')
            
            # Memory usage
            memory = psutil.virtual_memory()
            if memory.percent > self.memory_threshold:
                self._create_alert('HIGH_MEMORY', f\"Memory usage: {memory.percent:.1f}%\", 'WARNING')
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            if disk_percent > self.disk_threshold:
                self._create_alert('HIGH_DISK', f\"Disk usage: {disk_percent:.1f}%\", 'CRITICAL')
            
            # Log metrics
            securetrainer_logger.log_performance(
                'SYSTEM_RESOURCES',
                'Resource usage check',
                {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'disk_percent': disk_percent,
                    'memory_available_gb': memory.available / (1024**3)
                }
            )
            
        except Exception as e:
            securetrainer_logger.log_error(
                'SYSTEM_MONITOR',
                f\"Error checking system resources: {str(e)}\",
                e,
                error_type=ErrorType.PERFORMANCE_ERROR
            )
    
    def _check_response_times(self):
        \"\"\"Check application response times.\"\"\"
        if securetrainer_logger.request_times:
            recent_times = list(securetrainer_logger.request_times)[-100:]  # Last 100 requests
            avg_response_time = sum(recent_times) / len(recent_times)
            max_response_time = max(recent_times)
            
            if avg_response_time > self.response_time_threshold:
                self._create_alert(
                    'SLOW_RESPONSE',
                    f\"Average response time: {avg_response_time:.2f}s\",
                    'WARNING'
                )
            
            if max_response_time > self.response_time_threshold * 2:
                self._create_alert(
                    'VERY_SLOW_RESPONSE',
                    f\"Maximum response time: {max_response_time:.2f}s\",
                    'CRITICAL'
                )
    
    def _check_error_rates(self):
        \"\"\"Check application error rates.\"\"\"
        total_errors = sum(securetrainer_logger.error_counts.values())
        if total_errors > 20:  # More than 20 errors in monitoring period
            self._create_alert(
                'HIGH_ERROR_RATE',
                f\"Total errors: {total_errors}\",
                'CRITICAL'
            )
    
    def _create_alert(self, alert_type, message, severity):
        \"\"\"Create and log an alert.\"\"\"
        alert = {
            'timestamp': datetime.now(),
            'type': alert_type,
            'message': message,
            'severity': severity
        }
        
        self.alerts.append(alert)
        
        # Log alert
        securetrainer_logger.log_error(
            'SYSTEM_MONITOR',
            f\"ALERT: {alert_type} - {message}\",
            context=alert,
            error_type=ErrorType.SYSTEM_ERROR
        )
    
    def get_current_status(self):
        \"\"\"Get current system status.\"\"\"
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            status = {
                'monitoring_active': self.monitoring_active,
                'system_resources': {
                    'cpu_percent': cpu_percent,
                    'memory_percent': memory.percent,
                    'memory_available_gb': memory.available / (1024**3),
                    'disk_percent': (disk.used / disk.total) * 100,
                    'disk_free_gb': disk.free / (1024**3)
                },
                'application_metrics': {
                    'recent_requests': len(securetrainer_logger.request_times),
                    'avg_response_time': sum(securetrainer_logger.request_times) / len(securetrainer_logger.request_times) if securetrainer_logger.request_times else 0,
                    'total_errors': sum(securetrainer_logger.error_counts.values()),
                    'error_breakdown': dict(securetrainer_logger.error_counts)
                },
                'recent_alerts': list(self.alerts)[-10:],  # Last 10 alerts
                'generated_at': datetime.now().isoformat()
            }
            
            return status
            
        except Exception as e:
            securetrainer_logger.log_error(
                'SYSTEM_MONITOR',
                f\"Error getting system status: {str(e)}\",
                e,
                error_type=ErrorType.SYSTEM_ERROR
            )
            return None


# Global system monitor instance
system_monitor = SystemMonitor()


def handle_database_error(operation, exception, context=None):
    \"\"\"Handle database-specific errors.\"\"\"
    error_context = context or {}
    error_context.update({
        'operation': operation,
        'database': 'MongoDB'
    })
    
    securetrainer_logger.log_error(
        'DATABASE',
        f\"Database operation failed: {operation}\",
        exception,
        error_context,
        ErrorType.DATABASE_ERROR
    )


def handle_validation_error(field, value, rule, context=None):
    \"\"\"Handle validation errors.\"\"\"
    error_context = context or {}
    error_context.update({
        'field': field,
        'value': str(value)[:100],  # Limit value length
        'validation_rule': rule
    })
    
    securetrainer_logger.log_error(
        'VALIDATION',
        f\"Validation failed for field '{field}': {rule}\",
        context=error_context,
        error_type=ErrorType.VALIDATION_ERROR
    )


def handle_security_breach(breach_type, details, context=None):
    \"\"\"Handle security breach attempts.\"\"\"
    security_context = context or {}
    security_context.update({
        'breach_type': breach_type,
        'details': details,
        'user_id': session.get('user_id'),
        'ip_address': request.remote_addr if request else None,
        'user_agent': request.headers.get('User-Agent') if request else None
    })
    
    securetrainer_logger.log_security_event(
        breach_type,
        f\"Security breach attempt: {details}\",
        security_context,
        'CRITICAL'
    )


def get_monitoring_dashboard():
    \"\"\"Get comprehensive monitoring dashboard data.\"\"\"
    try:
        dashboard_data = {
            'system_status': system_monitor.get_current_status(),
            'recent_errors': list(securetrainer_logger.error_counts.items()),
            'performance_alerts': list(securetrainer_logger.performance_alerts),
            'log_summary': {
                'total_logs_today': 0,  # Would query database for actual count
                'error_logs_today': 0,
                'security_events_today': 0
            },
            'generated_at': datetime.now().isoformat()
        }
        
        return dashboard_data
        
    except Exception as e:
        securetrainer_logger.log_error(
            'MONITORING_DASHBOARD',
            f\"Error generating monitoring dashboard: {str(e)}\",
            e,
            error_type=ErrorType.SYSTEM_ERROR
        )
        return None


# Initialize monitoring on import
if __name__ != \"__main__\":
    system_monitor.start_monitoring()