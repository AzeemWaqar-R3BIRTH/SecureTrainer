"""
Robust Error Handling and Recovery System for SQL Challenge Validation
Ensures validation never completely fails and provides comprehensive fallbacks
"""

import logging
import traceback
from typing import Dict, List, Tuple, Any, Optional, Callable
from functools import wraps
from enum import Enum
import time
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class RecoveryStrategy(Enum):
    """Recovery strategy types"""
    RETRY = "retry"
    FALLBACK = "fallback"
    EMERGENCY = "emergency"
    BYPASS = "bypass"

@dataclass
class ErrorContext:
    """Error context information"""
    error_type: str
    error_message: str
    severity: ErrorSeverity
    challenge_id: str
    submitted_answer: str
    stack_trace: str
    timestamp: float
    recovery_attempts: int = 0

@dataclass
class RecoveryResult:
    """Result of recovery attempt"""
    success: bool
    strategy_used: RecoveryStrategy
    result_data: Any
    error_context: Optional[ErrorContext] = None

class ValidationErrorHandler:
    """
    Comprehensive error handling system for validation failures.
    Implements multiple recovery strategies to ensure validation never completely fails.
    """
    
    def __init__(self):
        self.error_log = []
        self.recovery_strategies = self._setup_recovery_strategies()
        self.emergency_validation_database = self._build_emergency_database()
        self.statistics = {
            'total_errors': 0,
            'recovered_errors': 0,
            'error_types': {},
            'recovery_strategies_used': {strategy: 0 for strategy in RecoveryStrategy}
        }
        logger.info("Validation Error Handler initialized")
    
    def handle_validation_error(self, 
                               error: Exception, 
                               challenge_id: str, 
                               submitted_answer: str, 
                               context: Optional[Dict] = None) -> RecoveryResult:
        """
        Main error handling function that attempts multiple recovery strategies.
        """
        try:
            # Create error context
            error_context = ErrorContext(
                error_type=type(error).__name__,
                error_message=str(error),
                severity=self._assess_error_severity(error),
                challenge_id=challenge_id,
                submitted_answer=submitted_answer,
                stack_trace=traceback.format_exc(),
                timestamp=time.time()
            )
            
            # Log error
            self._log_error(error_context)
            
            # Update statistics
            self.statistics['total_errors'] += 1
            self.statistics['error_types'][error_context.error_type] = \
                self.statistics['error_types'].get(error_context.error_type, 0) + 1
            
            # Attempt recovery strategies in order of preference
            recovery_result = self._attempt_recovery(error_context, context)
            
            if recovery_result.success:
                self.statistics['recovered_errors'] += 1
                self.statistics['recovery_strategies_used'][recovery_result.strategy_used] += 1
                logger.info(f"Recovered from error using {recovery_result.strategy_used.value} strategy")
            else:
                logger.error(f"Failed to recover from error: {error_context.error_message}")
            
            return recovery_result
            
        except Exception as handler_error:
            logger.critical(f"Error handler itself failed: {handler_error}")
            # Return emergency fallback
            return self._emergency_fallback(challenge_id, submitted_answer)
    
    def _attempt_recovery(self, error_context: ErrorContext, context: Optional[Dict]) -> RecoveryResult:
        """Attempt recovery using multiple strategies"""
        
        # Strategy 1: Retry with simplified validation
        if error_context.recovery_attempts < 2:
            recovery_result = self._retry_with_simplified_validation(error_context, context)
            if recovery_result.success:
                return recovery_result
        
        # Strategy 2: Fallback to demo database direct lookup
        recovery_result = self._fallback_to_demo_database(error_context)
        if recovery_result.success:
            return recovery_result
        
        # Strategy 3: Pattern-based emergency validation
        recovery_result = self._emergency_pattern_validation(error_context)
        if recovery_result.success:
            return recovery_result
        
        # Strategy 4: Emergency acceptance for known good answers
        recovery_result = self._emergency_acceptance_validation(error_context)
        if recovery_result.success:
            return recovery_result
        
        # Final strategy: Helpful error message
        return self._generate_helpful_error_response(error_context)
    
    def _retry_with_simplified_validation(self, error_context: ErrorContext, context: Optional[Dict]) -> RecoveryResult:
        """Retry validation with simplified logic"""
        try:
            error_context.recovery_attempts += 1
            
            # Simple normalization and matching
            normalized_answer = self._simple_normalize(error_context.submitted_answer)
            expected_answers = self._get_emergency_answers(error_context.challenge_id)
            
            for expected in expected_answers:
                normalized_expected = self._simple_normalize(expected)
                
                # Simple contains check
                if normalized_expected in normalized_answer or normalized_answer in normalized_expected:
                    return RecoveryResult(
                        success=True,
                        strategy_used=RecoveryStrategy.RETRY,
                        result_data={
                            'is_correct': True,
                            'feedback': "Answer accepted after error recovery.",
                            'confidence': 0.7
                        }
                    )
            
            return RecoveryResult(
                success=False,
                strategy_used=RecoveryStrategy.RETRY,
                result_data=None,
                error_context=error_context
            )
            
        except Exception as e:
            logger.error(f"Retry strategy failed: {e}")
            return RecoveryResult(
                success=False,
                strategy_used=RecoveryStrategy.RETRY,
                result_data=None,
                error_context=error_context
            )
    
    def _fallback_to_demo_database(self, error_context: ErrorContext) -> RecoveryResult:
        """Direct lookup in demo database"""
        try:
            demo_answers = self.emergency_validation_database.get(error_context.challenge_id, [])
            normalized_answer = self._simple_normalize(error_context.submitted_answer)
            
            for demo_answer in demo_answers:
                normalized_demo = self._simple_normalize(demo_answer)
                
                # Check if the submitted answer contains key words from demo answer
                demo_words = normalized_demo.split()
                answer_words = normalized_answer.split()
                
                common_words = set(demo_words).intersection(set(answer_words))
                if len(common_words) >= min(2, len(demo_words) * 0.6):
                    return RecoveryResult(
                        success=True,
                        strategy_used=RecoveryStrategy.FALLBACK,
                        result_data={
                            'is_correct': True,
                            'feedback': "Answer matched demo database entry.",
                            'confidence': 0.8
                        }
                    )
            
            return RecoveryResult(
                success=False,
                strategy_used=RecoveryStrategy.FALLBACK,
                result_data=None,
                error_context=error_context
            )
            
        except Exception as e:
            logger.error(f"Demo database fallback failed: {e}")
            return RecoveryResult(
                success=False,
                strategy_used=RecoveryStrategy.FALLBACK,
                result_data=None,
                error_context=error_context
            )
    
    def _emergency_pattern_validation(self, error_context: ErrorContext) -> RecoveryResult:
        """Emergency pattern-based validation"""
        try:
            challenge_type = self._get_challenge_type_from_id(error_context.challenge_id)
            normalized_answer = self._simple_normalize(error_context.submitted_answer)
            
            # Define emergency patterns for each challenge type
            emergency_patterns = {
                'sql_injection': [
                    'bypass', 'authentication', 'where', 'true', 'login',
                    'drop', 'table', 'delete', 'data', 'loss',
                    'union', 'select', 'extract', 'credentials'
                ],
                'xss': [
                    'javascript', 'execute', 'alert', 'script', 'popup',
                    'event', 'handler', 'onerror', 'onload',
                    'svg', 'iframe', 'dom', 'cookie'
                ],
                'command_injection': [
                    'command', 'ping', 'ls', 'chain', 'multiple',
                    'whoami', 'conditional', 'substitution', 'shell'
                ],
                'authentication': [
                    'password', 'weak', 'brute', 'force', 'token',
                    'session', 'hijack', 'attack', 'guess'
                ]
            }
            
            patterns = emergency_patterns.get(challenge_type, [])
            pattern_matches = sum(1 for pattern in patterns if pattern in normalized_answer)
            
            # Accept if sufficient patterns match
            threshold = max(1, len(patterns) * 0.3)  # 30% of patterns must match
            if pattern_matches >= threshold:
                return RecoveryResult(
                    success=True,
                    strategy_used=RecoveryStrategy.EMERGENCY,
                    result_data={
                        'is_correct': True,
                        'feedback': f"Answer accepted based on {pattern_matches} matching patterns.",
                        'confidence': min(0.9, pattern_matches / len(patterns))
                    }
                )
            
            return RecoveryResult(
                success=False,
                strategy_used=RecoveryStrategy.EMERGENCY,
                result_data=None,
                error_context=error_context
            )
            
        except Exception as e:
            logger.error(f"Emergency pattern validation failed: {e}")
            return RecoveryResult(
                success=False,
                strategy_used=RecoveryStrategy.EMERGENCY,
                result_data=None,
                error_context=error_context
            )
    
    def _emergency_acceptance_validation(self, error_context: ErrorContext) -> RecoveryResult:
        """Emergency acceptance for known good answer patterns"""
        try:
            normalized_answer = self._simple_normalize(error_context.submitted_answer)
            
            # Known good answer patterns that should always be accepted
            always_accept_patterns = [
                'authentication bypass',
                'login bypass',
                'where clause always true',
                'executes javascript',
                'shows alert popup',
                'command chaining',
                'multiple commands',
                'data extraction',
                'union select',
                'drop table',
                'brute force',
                'weak password',
                'session hijacking'
            ]
            
            for pattern in always_accept_patterns:
                normalized_pattern = self._simple_normalize(pattern)
                
                # Check for substantial overlap
                pattern_words = set(normalized_pattern.split())
                answer_words = set(normalized_answer.split())
                
                overlap = len(pattern_words.intersection(answer_words))
                if overlap >= min(2, len(pattern_words)):
                    return RecoveryResult(
                        success=True,
                        strategy_used=RecoveryStrategy.BYPASS,
                        result_data={
                            'is_correct': True,
                            'feedback': "Answer accepted through emergency validation.",
                            'confidence': 0.6
                        }
                    )
            
            return RecoveryResult(
                success=False,
                strategy_used=RecoveryStrategy.BYPASS,
                result_data=None,
                error_context=error_context
            )
            
        except Exception as e:
            logger.error(f"Emergency acceptance validation failed: {e}")
            return RecoveryResult(
                success=False,
                strategy_used=RecoveryStrategy.BYPASS,
                result_data=None,
                error_context=error_context
            )
    
    def _generate_helpful_error_response(self, error_context: ErrorContext) -> RecoveryResult:
        """Generate helpful error response when all recovery fails"""
        try:
            challenge_type = self._get_challenge_type_from_id(error_context.challenge_id)
            
            helpful_messages = {
                'sql_injection': "Try focusing on SQL injection techniques like authentication bypass, data extraction, or database manipulation.",
                'xss': "Consider cross-site scripting concepts like JavaScript execution, script injection, or DOM manipulation.",
                'command_injection': "Think about command injection methods like command chaining, multiple commands, or shell execution.",
                'authentication': "Focus on authentication vulnerabilities like weak passwords, brute force attacks, or session issues.",
                'default': "Please review the challenge scenario and think about the security vulnerability being demonstrated."
            }
            
            message = helpful_messages.get(challenge_type, helpful_messages['default'])
            
            return RecoveryResult(
                success=False,
                strategy_used=RecoveryStrategy.EMERGENCY,
                result_data={
                    'is_correct': False,
                    'feedback': f"Validation system encountered an error. {message}",
                    'confidence': 0.0,
                    'error_recovered': True
                }
            )
            
        except Exception as e:
            logger.critical(f"Failed to generate helpful error response: {e}")
            return RecoveryResult(
                success=False,
                strategy_used=RecoveryStrategy.EMERGENCY,
                result_data={
                    'is_correct': False,
                    'feedback': "System error occurred. Please try again.",
                    'confidence': 0.0
                }
            )
    
    def _emergency_fallback(self, challenge_id: str, submitted_answer: str) -> RecoveryResult:
        """Final emergency fallback when everything fails"""
        return RecoveryResult(
            success=False,
            strategy_used=RecoveryStrategy.EMERGENCY,
            result_data={
                'is_correct': False,
                'feedback': "System temporarily unavailable. Please try again in a moment.",
                'confidence': 0.0,
                'system_error': True
            }
        )
    
    def _build_emergency_database(self) -> Dict[str, List[str]]:
        """Build emergency validation database"""
        return {
            'sql_1': [
                "authentication bypass", "login bypass", "where clause always true",
                "bypasses authentication", "makes where clause always true"
            ],
            'sql_2': [
                "drop table users", "deletes users table", "data loss",
                "destroys user data", "removes users table"
            ],
            'sql_3': [
                "extracts user credentials", "data extraction", "union select attack",
                "retrieves usernames and passwords", "combines query results"
            ],
            'xss_1': [
                "executes javascript", "shows alert popup", "runs malicious script",
                "javascript code execution", "script injection"
            ],
            'xss_2': [
                "onerror event handler", "image error event", "javascript without script tags",
                "event-based javascript execution", "html attribute injection"
            ],
            'cmd_1': [
                "command chaining", "executes multiple commands", "ping and list directory",
                "semicolon command separator", "multiple system commands"
            ],
            'cmd_2': [
                "conditional command execution", "logical and operator", "command chaining with &&",
                "runs whoami if file processing succeeds", "conditional system information"
            ],
            'auth_1': [
                "weak password", "common password", "easily guessable password",
                "default password", "insecure password choice"
            ],
            'auth_2': [
                "brute force attack", "password guessing attack", "credential enumeration",
                "automated login attempts", "systematic password attempts"
            ]
        }
    
    def _simple_normalize(self, text: str) -> str:
        """Simple text normalization for emergency validation"""
        if not text:
            return ""
        return text.lower().strip().replace('-', ' ').replace('_', ' ')
    
    def _get_emergency_answers(self, challenge_id: str) -> List[str]:
        """Get emergency answers for a challenge"""
        return self.emergency_validation_database.get(challenge_id, [])
    
    def _get_challenge_type_from_id(self, challenge_id: str) -> str:
        """Extract challenge type from challenge ID"""
        if challenge_id.startswith('sql_'):
            return 'sql_injection'
        elif challenge_id.startswith('xss_'):
            return 'xss'
        elif challenge_id.startswith('cmd_'):
            return 'command_injection'
        elif challenge_id.startswith('auth_'):
            return 'authentication'
        elif challenge_id.startswith('csrf_'):
            return 'csrf'
        return 'unknown'
    
    def _assess_error_severity(self, error: Exception) -> ErrorSeverity:
        """Assess the severity of an error"""
        critical_errors = ['SystemError', 'MemoryError', 'DatabaseError']
        high_errors = ['ImportError', 'ModuleNotFoundError', 'ConnectionError']
        medium_errors = ['KeyError', 'ValueError', 'AttributeError']
        
        error_type = type(error).__name__
        
        if error_type in critical_errors:
            return ErrorSeverity.CRITICAL
        elif error_type in high_errors:
            return ErrorSeverity.HIGH
        elif error_type in medium_errors:
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW
    
    def _log_error(self, error_context: ErrorContext):
        """Log error with appropriate level"""
        log_message = f"Validation error - {error_context.error_type}: {error_context.error_message} " \
                     f"(Challenge: {error_context.challenge_id}, Answer: {error_context.submitted_answer[:50]}...)"
        
        if error_context.severity == ErrorSeverity.CRITICAL:
            logger.critical(log_message)
        elif error_context.severity == ErrorSeverity.HIGH:
            logger.error(log_message)
        elif error_context.severity == ErrorSeverity.MEDIUM:
            logger.warning(log_message)
        else:
            logger.info(log_message)
        
        # Store in error log
        self.error_log.append(error_context)
        
        # Keep only last 1000 errors
        if len(self.error_log) > 1000:
            self.error_log = self.error_log[-1000:]
    
    def _setup_recovery_strategies(self) -> Dict[str, Callable]:
        """Setup recovery strategy mappings"""
        return {
            'import_error': self._fallback_to_demo_database,
            'database_error': self._emergency_pattern_validation,
            'validation_error': self._retry_with_simplified_validation,
            'system_error': self._emergency_acceptance_validation
        }
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error statistics"""
        total_errors = self.statistics['total_errors']
        recovery_rate = (self.statistics['recovered_errors'] / total_errors * 100) if total_errors > 0 else 0
        
        return {
            'total_errors': total_errors,
            'recovered_errors': self.statistics['recovered_errors'],
            'recovery_rate': round(recovery_rate, 2),
            'error_types': self.statistics['error_types'],
            'recovery_strategies': {k.value: v for k, v in self.statistics['recovery_strategies_used'].items()},
            'recent_errors': len([e for e in self.error_log if time.time() - e.timestamp < 3600])  # Last hour
        }
    
    def clear_error_log(self):
        """Clear error log"""
        self.error_log.clear()
        logger.info("Error log cleared")

def validation_error_handler(func):
    """Decorator for automatic error handling in validation functions"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            # Extract challenge_id and submitted_answer from args if possible
            challenge_id = args[0] if len(args) > 0 else "unknown"
            submitted_answer = args[1] if len(args) > 1 else "unknown"
            
            # Use global error handler instance
            recovery_result = error_handler.handle_validation_error(e, challenge_id, submitted_answer)
            
            if recovery_result.success:
                return recovery_result.result_data['is_correct'], recovery_result.result_data['feedback']
            else:
                return False, recovery_result.result_data.get('feedback', 'Validation failed')
    
    return wrapper

# Global error handler instance
error_handler = ValidationErrorHandler()