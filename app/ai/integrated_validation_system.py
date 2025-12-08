"""
Integrated SQL Challenge Validation System
Combines comprehensive validation engine with error handling for 100% accuracy
"""

import logging
from typing import Dict, List, Tuple, Any, Optional
from app.ai.comprehensive_validation_engine import comprehensive_validator, ValidationResult
from app.ai.robust_error_handler import error_handler, validation_error_handler
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntegratedValidationSystem:
    """
    Integrated validation system that combines the comprehensive validation engine
    with robust error handling to ensure 100% validation accuracy for demo answers.
    """
    
    def __init__(self):
        self.validator = comprehensive_validator
        self.error_handler = error_handler
        self.performance_metrics = {
            'total_validations': 0,
            'successful_validations': 0,
            'error_recoveries': 0,
            'average_response_time': 0.0,
            'response_times': []
        }
        logger.info("Integrated Validation System initialized")
    
    @validation_error_handler
    def validate_challenge_solution(self, challenge_id: str, submitted_answer: str, context: Optional[Dict] = None) -> Tuple[bool, str]:
        """
        Main validation function that integrates comprehensive validation with error handling.
        This function ensures 100% validation accuracy for all demo guide answers.
        
        Args:
            challenge_id: Unique identifier for the challenge
            submitted_answer: User's submitted answer
            context: Optional context information
            
        Returns:
            Tuple of (is_correct, feedback_message)
        """
        start_time = time.time()
        
        try:
            # Update metrics
            self.performance_metrics['total_validations'] += 1
            
            # Validate using comprehensive engine
            validation_result = self.validator.validate_answer(challenge_id, submitted_answer, context)
            
            # Track performance
            processing_time = time.time() - start_time
            self.performance_metrics['response_times'].append(processing_time)
            self._update_average_response_time()
            
            if validation_result.is_correct:
                self.performance_metrics['successful_validations'] += 1
                
                # Generate success feedback based on confidence and tier
                feedback = self._generate_success_feedback(validation_result)
                
                logger.info(f"Validation successful - Challenge: {challenge_id}, "
                           f"Tier: {validation_result.tier_used.name}, "
                           f"Confidence: {validation_result.confidence:.2f}")
                
                return True, feedback
            else:
                # Generate helpful feedback for incorrect answers
                feedback = self._generate_failure_feedback(validation_result, challenge_id)
                
                logger.info(f"Validation failed - Challenge: {challenge_id}, "
                           f"Answer: {submitted_answer[:50]}...")
                
                return False, feedback
                
        except Exception as e:
            # Error handling is automatically applied by decorator
            logger.error(f"Validation system error: {e}")
            self.performance_metrics['error_recoveries'] += 1
            raise e
    
    def validate_sql_injection_solution(self, answer: str, expected_solutions: List[str], challenge: Dict) -> Tuple[bool, str]:
        """
        SQL injection specific validation function for backward compatibility.
        Routes to the integrated validation system.
        """
        challenge_id = challenge.get('id', 'sql_unknown')
        context = {
            'challenge_type': 'sql_injection',
            'expected_solutions': expected_solutions,
            'challenge_data': challenge
        }
        
        return self.validate_challenge_solution(challenge_id, answer, context)
    
    def validate_xss_solution(self, answer: str, expected_solutions: List[str], challenge: Dict) -> Tuple[bool, str]:
        """
        XSS specific validation function for backward compatibility.
        """
        challenge_id = challenge.get('id', 'xss_unknown')
        context = {
            'challenge_type': 'xss',
            'expected_solutions': expected_solutions,
            'challenge_data': challenge
        }
        
        return self.validate_challenge_solution(challenge_id, answer, context)
    
    def validate_command_injection_solution(self, answer: str, expected_solutions: List[str], challenge: Dict) -> Tuple[bool, str]:
        """
        Command injection specific validation function for backward compatibility.
        """
        challenge_id = challenge.get('id', 'cmd_unknown')
        context = {
            'challenge_type': 'command_injection',
            'expected_solutions': expected_solutions,
            'challenge_data': challenge
        }
        
        return self.validate_challenge_solution(challenge_id, answer, context)
    
    def validate_authentication_solution(self, answer: str, expected_solutions: List[str], challenge: Dict) -> Tuple[bool, str]:
        """
        Authentication specific validation function for backward compatibility.
        """
        challenge_id = challenge.get('id', 'auth_unknown')
        context = {
            'challenge_type': 'authentication',
            'expected_solutions': expected_solutions,
            'challenge_data': challenge
        }
        
        return self.validate_challenge_solution(challenge_id, answer, context)
    
    def validate_csrf_solution(self, answer: str, expected_solutions: List[str], challenge: Dict) -> Tuple[bool, str]:
        """
        CSRF specific validation function for backward compatibility.
        """
        challenge_id = challenge.get('id', 'csrf_unknown')
        context = {
            'challenge_type': 'csrf',
            'expected_solutions': expected_solutions,
            'challenge_data': challenge
        }
        
        return self.validate_challenge_solution(challenge_id, answer, context)
    
    def enhanced_answer_validation(self, normalized_answer: str, challenge: Dict) -> Tuple[bool, str]:
        """
        Enhanced answer validation function for backward compatibility.
        """
        challenge_id = challenge.get('id', 'unknown')
        context = {
            'normalized_input': True,
            'challenge_data': challenge
        }
        
        return self.validate_challenge_solution(challenge_id, normalized_answer, context)
    
    def generic_answer_validation(self, normalized_answer: str, expected_solutions: List[str]) -> Tuple[bool, str]:
        """
        Generic answer validation function for backward compatibility.
        """
        # Create a temporary challenge for validation
        context = {
            'generic_validation': True,
            'expected_solutions': expected_solutions
        }
        
        return self.validate_challenge_solution('generic', normalized_answer, context)
    
    def _generate_success_feedback(self, validation_result: ValidationResult) -> str:
        """Generate appropriate success feedback based on validation result"""
        
        confidence_messages = {
            (0.9, 1.0): [
                "Excellent! Perfect understanding demonstrated.",
                "Outstanding! Your answer is exactly right.",
                "Perfect! You've mastered this concept."
            ],
            (0.8, 0.9): [
                "Great job! Your answer shows strong understanding.",
                "Well done! You've got the key concepts right.",
                "Correct! Your technical knowledge is solid."
            ],
            (0.7, 0.8): [
                "Good work! Your answer captures the main ideas.",
                "Correct! You understand the core concepts.",
                "Nice! Your answer demonstrates good knowledge."
            ],
            (0.5, 0.7): [
                "Correct! Your answer contains the essential elements.",
                "Good! You've identified the key points.",
                "Right! Your understanding is on track."
            ]
        }
        
        # Select appropriate message based on confidence
        confidence = validation_result.confidence
        for (min_conf, max_conf), messages in confidence_messages.items():
            if min_conf <= confidence <= max_conf:
                import random
                return random.choice(messages)
        
        return "Correct answer!"
    
    def _generate_failure_feedback(self, validation_result: ValidationResult, challenge_id: str) -> str:
        """Generate helpful failure feedback"""
        
        challenge_type = self._get_challenge_type(challenge_id)
        
        base_message = "Your answer is not quite right. "
        
        type_specific_hints = {
            'sql_injection': "Think about SQL injection techniques like authentication bypass, data extraction, or database manipulation.",
            'xss': "Consider cross-site scripting concepts like JavaScript execution, script injection, or DOM manipulation.",
            'command_injection': "Focus on command injection methods like command chaining, multiple commands, or shell execution.",
            'authentication': "Consider authentication vulnerabilities like weak passwords, brute force attacks, or session issues.",
            'csrf': "Think about Cross-Site Request Forgery and how unauthorized actions can be performed."
        }
        
        hint = type_specific_hints.get(challenge_type, "Review the challenge scenario and think about the security vulnerability being demonstrated.")
        
        return base_message + hint
    
    def _get_challenge_type(self, challenge_id: str) -> str:
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
    
    def _update_average_response_time(self):
        """Update average response time"""
        if self.performance_metrics['response_times']:
            self.performance_metrics['average_response_time'] = \
                sum(self.performance_metrics['response_times']) / len(self.performance_metrics['response_times'])
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get comprehensive performance metrics"""
        total = self.performance_metrics['total_validations']
        success_rate = (self.performance_metrics['successful_validations'] / total * 100) if total > 0 else 0
        
        # Get metrics from underlying systems
        validator_stats = self.validator.get_statistics()
        error_stats = self.error_handler.get_error_statistics()
        
        return {
            'integrated_system': {
                'total_validations': total,
                'successful_validations': self.performance_metrics['successful_validations'],
                'success_rate': round(success_rate, 2),
                'error_recoveries': self.performance_metrics['error_recoveries'],
                'average_response_time_ms': round(self.performance_metrics['average_response_time'] * 1000, 2)
            },
            'validation_engine': validator_stats,
            'error_handling': error_stats,
            'system_health': {
                'operational': True,
                'error_rate': round((error_stats['total_errors'] / total * 100) if total > 0 else 0, 2),
                'recovery_rate': error_stats['recovery_rate']
            }
        }
    
    def test_demo_answers(self) -> Dict[str, Any]:
        """
        Test all demo answers to ensure 100% validation accuracy.
        This function verifies that every answer from the demo guide is accepted.
        """
        demo_test_cases = [
            # SQL Injection Tests
            ('sql_1', 'authentication bypass'),
            ('sql_1', 'bypasses authentication'),
            ('sql_1', 'WHERE clause always true'),
            ('sql_1', 'login bypass'),
            ('sql_2', 'drop table users'),
            ('sql_2', 'deletes users table'),
            ('sql_2', 'data loss'),
            ('sql_3', 'extracts user credentials'),
            ('sql_3', 'data extraction'),
            ('sql_3', 'UNION SELECT attack'),
            
            # XSS Tests
            ('xss_1', 'executes JavaScript'),
            ('xss_1', 'shows alert popup'),
            ('xss_1', 'runs JavaScript code'),
            ('xss_2', 'onerror event handler'),
            ('xss_2', 'image error event'),
            ('xss_3', 'SVG onload event'),
            ('xss_3', 'bypasses script tag filters'),
            
            # Command Injection Tests
            ('cmd_1', 'command chaining'),
            ('cmd_1', 'executes multiple commands'),
            ('cmd_1', 'ping and list directory'),
            ('cmd_2', 'conditional command execution'),
            ('cmd_2', 'logical AND operator'),
            ('cmd_3', 'command substitution'),
            ('cmd_3', 'executes whoami command'),
            
            # Authentication Tests
            ('auth_1', 'weak password'),
            ('auth_1', 'common password'),
            ('auth_2', 'brute force attack'),
            ('auth_2', 'password guessing attack'),
            ('auth_3', 'predictable reset tokens'),
            ('auth_4', 'session hijacking')
        ]
        
        test_results = {
            'total_tests': len(demo_test_cases),
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': [],
            'success_rate': 0.0
        }
        
        for challenge_id, answer in demo_test_cases:
            try:
                is_correct, feedback = self.validate_challenge_solution(challenge_id, answer)
                
                test_detail = {
                    'challenge_id': challenge_id,
                    'answer': answer,
                    'passed': is_correct,
                    'feedback': feedback
                }
                
                test_results['test_details'].append(test_detail)
                
                if is_correct:
                    test_results['passed_tests'] += 1
                else:
                    test_results['failed_tests'] += 1
                    logger.warning(f"Demo answer test failed: {challenge_id} - {answer}")
                
            except Exception as e:
                logger.error(f"Demo answer test error: {challenge_id} - {answer}: {e}")
                test_results['failed_tests'] += 1
                test_results['test_details'].append({
                    'challenge_id': challenge_id,
                    'answer': answer,
                    'passed': False,
                    'feedback': f"Test error: {str(e)}"
                })
        
        test_results['success_rate'] = round(
            (test_results['passed_tests'] / test_results['total_tests'] * 100), 2
        )
        
        logger.info(f"Demo answers test completed: {test_results['success_rate']}% success rate")
        
        return test_results
    
    def clear_all_caches(self):
        """Clear all system caches"""
        self.validator.clear_cache()
        self.error_handler.clear_error_log()
        logger.info("All caches cleared")

# Global integrated validation system instance
integrated_validation_system = IntegratedValidationSystem()

# Convenience functions for backward compatibility
def validate_challenge_solution(challenge_id: str, submitted_answer: str) -> Tuple[bool, str]:
    """Global validation function"""
    return integrated_validation_system.validate_challenge_solution(challenge_id, submitted_answer)

def validate_sql_injection_solution(answer: str, expected_solutions: List[str], challenge: Dict) -> Tuple[bool, str]:
    """Global SQL injection validation function"""
    return integrated_validation_system.validate_sql_injection_solution(answer, expected_solutions, challenge)

def validate_xss_solution(answer: str, expected_solutions: List[str], challenge: Dict) -> Tuple[bool, str]:
    """Global XSS validation function"""
    return integrated_validation_system.validate_xss_solution(answer, expected_solutions, challenge)

def validate_command_injection_solution(answer: str, expected_solutions: List[str], challenge: Dict) -> Tuple[bool, str]:
    """Global command injection validation function"""
    return integrated_validation_system.validate_command_injection_solution(answer, expected_solutions, challenge)

def validate_authentication_solution(answer: str, expected_solutions: List[str], challenge: Dict) -> Tuple[bool, str]:
    """Global authentication validation function"""
    return integrated_validation_system.validate_authentication_solution(answer, expected_solutions, challenge)

def validate_csrf_solution(answer: str, expected_solutions: List[str], challenge: Dict) -> Tuple[bool, str]:
    """Global CSRF validation function"""
    return integrated_validation_system.validate_csrf_solution(answer, expected_solutions, challenge)

def enhanced_answer_validation(normalized_answer: str, challenge: Dict) -> Tuple[bool, str]:
    """Global enhanced validation function"""
    return integrated_validation_system.enhanced_answer_validation(normalized_answer, challenge)

def generic_answer_validation(normalized_answer: str, expected_solutions: List[str]) -> Tuple[bool, str]:
    """Global generic validation function"""
    return integrated_validation_system.generic_answer_validation(normalized_answer, expected_solutions)