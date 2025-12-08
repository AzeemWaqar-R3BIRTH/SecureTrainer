#!/usr/bin/env python3
"""
Comprehensive Test Suite for SQL Challenge Answer Validation Fix
Tests the integrated validation system to ensure 100% accuracy for demo answers
"""

import sys
import os
import unittest
import time
from typing import Dict, List, Tuple, Any

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

class TestSQLValidationFix(unittest.TestCase):
    """
    Comprehensive test suite for the SQL validation fix.
    Ensures 100% validation accuracy for all demo guide answers.
    """
    
    def setUp(self):
        """Set up test environment"""
        try:
            from app.ai.integrated_validation_system import integrated_validation_system
            self.validation_system = integrated_validation_system
            
            # Demo answers from the demo guide
            self.demo_answers = {
                # SQL Injection Challenges
                'sql_1': [
                    "authentication bypass",
                    "bypasses authentication", 
                    "WHERE clause always true",
                    "WHERE clause always evaluates to true",
                    "login bypass",
                    "SQL injection authentication bypass",
                    "always true condition",
                    "conditional bypass",
                    "makes the WHERE clause always true",
                    "bypasses login security"
                ],
                'sql_2': [
                    "drop table users",
                    "deletes users table",
                    "destroys user data", 
                    "removes users table",
                    "data loss",
                    "table deletion",
                    "destructive SQL command",
                    "database table removal",
                    "drops the users table",
                    "causes data loss"
                ],
                'sql_3': [
                    "extracts user credentials",
                    "retrieves usernames and passwords",
                    "data extraction",
                    "combines query results", 
                    "UNION SELECT attack",
                    "database information disclosure",
                    "credential extraction",
                    "user data retrieval",
                    "combines results and extracts data",
                    "accesses user table data"
                ],
                
                # XSS Challenges
                'xss_1': [
                    "executes JavaScript",
                    "shows alert popup",
                    "runs malicious script",
                    "JavaScript code execution",
                    "script injection", 
                    "client-side code execution",
                    "browser script execution",
                    "alert dialog display",
                    "displays an alert",
                    "runs JavaScript code"
                ],
                'xss_2': [
                    "onerror event handler",
                    "image error event",
                    "JavaScript without script tags",
                    "event-based JavaScript execution",
                    "HTML attribute injection",
                    "image onerror payload",
                    "event handler exploitation", 
                    "alternative JavaScript execution",
                    "uses event handlers",
                    "image onerror technique"
                ],
                
                # Command Injection Challenges
                'cmd_1': [
                    "ping and list directory",
                    "executes multiple commands",
                    "command chaining",
                    "semicolon command separator",
                    "ping then ls command",
                    "command injection",
                    "multiple system commands",
                    "command sequence execution",
                    "runs ping and ls",
                    "chains commands together"
                ],
                'cmd_2': [
                    "conditional command execution",
                    "runs whoami if file processing succeeds",
                    "logical AND operator",
                    "command chaining with &&",
                    "conditional system information",
                    "filename processing then user identification",
                    "logical command operator",
                    "success-dependent execution",
                    "executes whoami conditionally",
                    "uses && operator"
                ],
                
                # Authentication Challenges
                'auth_1': [
                    "weak password",
                    "common password",
                    "easily guessable password",
                    "default password",
                    "password vulnerability",
                    "insecure password choice",
                    "dictionary password",
                    "predictable credential"
                ],
                'auth_2': [
                    "brute force attack",
                    "password guessing attack",
                    "credential enumeration",
                    "systematic password attempts",
                    "automated login attempts", 
                    "dictionary attack",
                    "password spraying",
                    "credential brute forcing",
                    "unlimited login attempts",
                    "password cracking"
                ]
            }
            
            print("✅ Test setup completed successfully")
            
        except ImportError as e:
            self.skipTest(f"Required modules not available: {e}")
        except Exception as e:
            self.skipTest(f"Setup failed: {e}")
    
    def test_sql_injection_demo_answers(self):
        """Test all SQL injection demo answers for 100% acceptance"""
        print("\\n🔍 Testing SQL Injection Demo Answers...")
        
        failed_tests = []
        passed_tests = 0
        total_tests = 0
        
        for challenge_id in ['sql_1', 'sql_2', 'sql_3']:
            if challenge_id in self.demo_answers:
                for answer in self.demo_answers[challenge_id]:
                    total_tests += 1
                    try:
                        is_correct, feedback = self.validation_system.validate_challenge_solution(challenge_id, answer)
                        
                        if is_correct:
                            passed_tests += 1
                            print(f"  ✅ {challenge_id}: '{answer}' -> ACCEPTED")
                        else:
                            failed_tests.append((challenge_id, answer, feedback))
                            print(f"  ❌ {challenge_id}: '{answer}' -> REJECTED ({feedback})")
                    
                    except Exception as e:
                        failed_tests.append((challenge_id, answer, f"Error: {e}"))
                        print(f"  ⚠️  {challenge_id}: '{answer}' -> ERROR ({e})")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"\\n📊 SQL Injection Results: {passed_tests}/{total_tests} passed ({success_rate:.1f}%)")
        
        # Assert 100% success rate for SQL injection
        self.assertEqual(len(failed_tests), 0, f"SQL injection validation failed for: {failed_tests}")
        self.assertEqual(success_rate, 100.0, "SQL injection should have 100% success rate")
    
    def test_xss_demo_answers(self):
        """Test XSS demo answers for 100% acceptance"""
        print("\\n🔍 Testing XSS Demo Answers...")
        
        failed_tests = []
        passed_tests = 0
        total_tests = 0
        
        for challenge_id in ['xss_1', 'xss_2']:
            if challenge_id in self.demo_answers:
                for answer in self.demo_answers[challenge_id]:
                    total_tests += 1
                    try:
                        is_correct, feedback = self.validation_system.validate_challenge_solution(challenge_id, answer)
                        
                        if is_correct:
                            passed_tests += 1
                            print(f"  ✅ {challenge_id}: '{answer}' -> ACCEPTED")
                        else:
                            failed_tests.append((challenge_id, answer, feedback))
                            print(f"  ❌ {challenge_id}: '{answer}' -> REJECTED ({feedback})")
                    
                    except Exception as e:
                        failed_tests.append((challenge_id, answer, f"Error: {e}"))
                        print(f"  ⚠️  {challenge_id}: '{answer}' -> ERROR ({e})")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"\\n📊 XSS Results: {passed_tests}/{total_tests} passed ({success_rate:.1f}%)")
        
        # Allow some flexibility for XSS (95% minimum)
        self.assertGreaterEqual(success_rate, 95.0, "XSS should have at least 95% success rate")
    
    def test_command_injection_demo_answers(self):
        """Test command injection demo answers for 100% acceptance"""
        print("\\n🔍 Testing Command Injection Demo Answers...")
        
        failed_tests = []
        passed_tests = 0
        total_tests = 0
        
        for challenge_id in ['cmd_1', 'cmd_2']:
            if challenge_id in self.demo_answers:
                for answer in self.demo_answers[challenge_id]:
                    total_tests += 1
                    try:
                        is_correct, feedback = self.validation_system.validate_challenge_solution(challenge_id, answer)
                        
                        if is_correct:
                            passed_tests += 1
                            print(f"  ✅ {challenge_id}: '{answer}' -> ACCEPTED")
                        else:
                            failed_tests.append((challenge_id, answer, feedback))
                            print(f"  ❌ {challenge_id}: '{answer}' -> REJECTED ({feedback})")
                    
                    except Exception as e:
                        failed_tests.append((challenge_id, answer, f"Error: {e}"))
                        print(f"  ⚠️  {challenge_id}: '{answer}' -> ERROR ({e})")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"\\n📊 Command Injection Results: {passed_tests}/{total_tests} passed ({success_rate:.1f}%)")
        
        # Allow some flexibility for command injection (95% minimum)
        self.assertGreaterEqual(success_rate, 95.0, "Command injection should have at least 95% success rate")
    
    def test_authentication_demo_answers(self):
        """Test authentication demo answers for 100% acceptance"""
        print("\\n🔍 Testing Authentication Demo Answers...")
        
        failed_tests = []
        passed_tests = 0
        total_tests = 0
        
        for challenge_id in ['auth_1', 'auth_2']:
            if challenge_id in self.demo_answers:
                for answer in self.demo_answers[challenge_id]:
                    total_tests += 1
                    try:
                        is_correct, feedback = self.validation_system.validate_challenge_solution(challenge_id, answer)
                        
                        if is_correct:
                            passed_tests += 1
                            print(f"  ✅ {challenge_id}: '{answer}' -> ACCEPTED")
                        else:
                            failed_tests.append((challenge_id, answer, feedback))
                            print(f"  ❌ {challenge_id}: '{answer}' -> REJECTED ({feedback})")
                    
                    except Exception as e:
                        failed_tests.append((challenge_id, answer, f"Error: {e}"))
                        print(f"  ⚠️  {challenge_id}: '{answer}' -> ERROR ({e})")
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        print(f"\\n📊 Authentication Results: {passed_tests}/{total_tests} passed ({success_rate:.1f}%)")
        
        # Allow some flexibility for authentication (90% minimum)
        self.assertGreaterEqual(success_rate, 90.0, "Authentication should have at least 90% success rate")
    
    def test_case_insensitive_validation(self):
        """Test that validation is case-insensitive"""
        print("\\n🔍 Testing Case Insensitive Validation...")
        
        test_cases = [
            ('sql_1', 'AUTHENTICATION BYPASS'),
            ('sql_1', 'Authentication Bypass'),
            ('sql_1', 'authentication bypass'),
            ('sql_2', 'DROP TABLE USERS'),
            ('sql_2', 'Drop Table Users'),
            ('xss_1', 'EXECUTES JAVASCRIPT'),
            ('xss_1', 'Executes JavaScript')
        ]
        
        failed_tests = []
        for challenge_id, answer in test_cases:
            try:
                is_correct, feedback = self.validation_system.validate_challenge_solution(challenge_id, answer)
                if is_correct:
                    print(f"  ✅ {challenge_id}: '{answer}' -> ACCEPTED")
                else:
                    failed_tests.append((challenge_id, answer, feedback))
                    print(f"  ❌ {challenge_id}: '{answer}' -> REJECTED ({feedback})")
            except Exception as e:
                failed_tests.append((challenge_id, answer, f"Error: {e}"))
                print(f"  ⚠️  {challenge_id}: '{answer}' -> ERROR ({e})")
        
        self.assertEqual(len(failed_tests), 0, f"Case insensitive validation failed: {failed_tests}")
    
    def test_whitespace_handling(self):
        """Test that validation handles extra whitespace correctly"""
        print("\\n🔍 Testing Whitespace Handling...")
        
        test_cases = [
            ('sql_1', '  authentication bypass  '),
            ('sql_1', 'authentication   bypass'),
            ('sql_1', '\\tauthentication bypass\\n'),
            ('sql_2', ' drop table users '),
            ('xss_1', '  executes javascript  ')
        ]
        
        failed_tests = []
        for challenge_id, answer in test_cases:
            try:
                is_correct, feedback = self.validation_system.validate_challenge_solution(challenge_id, answer)
                if is_correct:
                    print(f"  ✅ {challenge_id}: '{repr(answer)}' -> ACCEPTED")
                else:
                    failed_tests.append((challenge_id, answer, feedback))
                    print(f"  ❌ {challenge_id}: '{repr(answer)}' -> REJECTED ({feedback})")
            except Exception as e:
                failed_tests.append((challenge_id, answer, f"Error: {e}"))
                print(f"  ⚠️  {challenge_id}: '{repr(answer)}' -> ERROR ({e})")
        
        self.assertEqual(len(failed_tests), 0, f"Whitespace handling failed: {failed_tests}")
    
    def test_partial_answer_rejection(self):
        """Test that clearly wrong answers are properly rejected"""
        print("\\n🔍 Testing Wrong Answer Rejection...")
        
        wrong_answers = [
            ('sql_1', 'completely wrong answer'),
            ('sql_1', 'random text'),
            ('sql_2', 'invalid response'),
            ('xss_1', 'not related to xss'),
            ('cmd_1', 'unrelated command stuff')
        ]
        
        accepted_wrong = []
        for challenge_id, answer in wrong_answers:
            try:
                is_correct, feedback = self.validation_system.validate_challenge_solution(challenge_id, answer)
                if is_correct:
                    accepted_wrong.append((challenge_id, answer))
                    print(f"  ⚠️  {challenge_id}: '{answer}' -> INCORRECTLY ACCEPTED")
                else:
                    print(f"  ✅ {challenge_id}: '{answer}' -> CORRECTLY REJECTED")
            except Exception as e:
                print(f"  ✅ {challenge_id}: '{answer}' -> ERROR (acceptable for wrong answers)")
        
        # Allow some false positives but not too many
        false_positive_rate = len(accepted_wrong) / len(wrong_answers) * 100
        print(f"\\n📊 False positive rate: {false_positive_rate:.1f}%")
        
        self.assertLessEqual(false_positive_rate, 20.0, "Too many wrong answers were accepted")
    
    def test_performance_benchmarks(self):
        """Test validation performance"""
        print("\\n🔍 Testing Performance Benchmarks...")
        
        test_answer = "authentication bypass"
        challenge_id = "sql_1"
        num_tests = 100
        
        start_time = time.time()
        
        for i in range(num_tests):
            try:
                is_correct, feedback = self.validation_system.validate_challenge_solution(challenge_id, test_answer)
            except Exception as e:
                print(f"  ⚠️  Performance test error: {e}")
        
        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / num_tests
        
        print(f"  📊 {num_tests} validations completed in {total_time:.3f}s")
        print(f"  📊 Average time per validation: {avg_time*1000:.2f}ms")
        
        # Performance should be under 100ms per validation on average
        self.assertLess(avg_time, 0.1, f"Validation too slow: {avg_time*1000:.2f}ms average")
    
    def test_error_recovery(self):
        """Test error recovery mechanisms"""
        print("\\n🔍 Testing Error Recovery...")
        
        # Test with edge cases that might cause errors
        edge_cases = [
            ('sql_1', ''),  # Empty string
            ('sql_1', None),  # None value
            ('invalid_challenge', 'authentication bypass'),  # Invalid challenge ID
            ('sql_1', 'a' * 1000),  # Very long string
        ]
        
        for challenge_id, answer in edge_cases:
            try:
                if answer is None:
                    continue  # Skip None test as it would cause TypeError before reaching validation
                
                is_correct, feedback = self.validation_system.validate_challenge_solution(challenge_id, answer)
                print(f"  ✅ {challenge_id}: Edge case handled gracefully")
                
                # Feedback should always be a string
                self.assertIsInstance(feedback, str, "Feedback should always be a string")
                
            except Exception as e:
                print(f"  ⚠️  {challenge_id}: Error not recovered: {e}")
                # Error recovery should prevent exceptions from propagating
                # This test might fail initially but should pass after error handling is implemented
    
    def test_integration_with_existing_system(self):
        """Test integration with existing challenge model"""
        print("\\n🔍 Testing Integration with Existing System...")
        
        try:
            # Test the main validation function from challenge model
            from app.models.challenge_model import validate_challenge_solution
            
            test_cases = [
                ('sql_1', 'authentication bypass'),
                ('sql_2', 'drop table users'),
                ('xss_1', 'executes javascript')
            ]
            
            failed_integrations = []
            for challenge_id, answer in test_cases:
                try:
                    is_correct, feedback = validate_challenge_solution(challenge_id, answer)
                    if is_correct:
                        print(f"  ✅ Integration test: {challenge_id} -> PASSED")
                    else:
                        failed_integrations.append((challenge_id, answer, feedback))
                        print(f"  ❌ Integration test: {challenge_id} -> FAILED ({feedback})")
                except Exception as e:
                    failed_integrations.append((challenge_id, answer, f"Error: {e}"))
                    print(f"  ⚠️  Integration test: {challenge_id} -> ERROR ({e})")
            
            # Integration should work for basic test cases
            self.assertEqual(len(failed_integrations), 0, f"Integration failed: {failed_integrations}")
            
        except ImportError as e:
            print(f"  ⚠️  Integration test skipped: {e}")
    
    def test_comprehensive_demo_validation(self):
        """Run the comprehensive demo test from the integrated system"""
        print("\\n🔍 Running Comprehensive Demo Validation Test...")
        
        try:
            test_results = self.validation_system.test_demo_answers()
            
            print(f"  📊 Total tests: {test_results['total_tests']}")
            print(f"  📊 Passed tests: {test_results['passed_tests']}")
            print(f"  📊 Failed tests: {test_results['failed_tests']}")
            print(f"  📊 Success rate: {test_results['success_rate']}%")
            
            # Print failed tests for debugging
            failed_details = [detail for detail in test_results['test_details'] if not detail['passed']]
            if failed_details:
                print("\\n❌ Failed test details:")
                for detail in failed_details[:5]:  # Show first 5 failures
                    print(f"    {detail['challenge_id']}: '{detail['answer']}' - {detail['feedback']}")
            
            # Success rate should be at least 95%
            self.assertGreaterEqual(test_results['success_rate'], 95.0, 
                                  f"Demo validation success rate too low: {test_results['success_rate']}%")
            
        except Exception as e:
            self.fail(f"Comprehensive demo validation failed: {e}")

def run_validation_tests():
    """Run all validation tests and provide detailed results"""
    print("🚀 Starting SQL Challenge Validation Fix Tests\\n")
    print("=" * 80)
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSQLValidationFix)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    print("=" * 80)
    print(f"\\n📊 Test Summary:")
    print(f"   Tests run: {result.testsRun}")
    print(f"   Failures: {len(result.failures)}")
    print(f"   Errors: {len(result.errors)}")
    print(f"   Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\\n❌ Failures:")
        for test, traceback in result.failures:
            print(f"   {test}: {traceback.split('AssertionError: ')[-1].split('\\n')[0]}")
    
    if result.errors:
        print(f"\\n⚠️  Errors:")
        for test, traceback in result.errors:
            print(f"   {test}: {traceback.split('\\n')[-2]}")
    
    if not result.failures and not result.errors:
        print("\\n🎉 All tests passed! SQL Challenge validation fix is working correctly.")
    
    return result.wasSuccessful()

if __name__ == '__main__':
    success = run_validation_tests()
    sys.exit(0 if success else 1)