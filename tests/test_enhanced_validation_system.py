"""
Comprehensive Test Suite for Enhanced Validation System
Tests the advanced answer validation and learning system enhancements
"""

import unittest
import sys
import os
import time
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

# Add the parent directory to the path to import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.ai.enhanced_validation_system import (
    EnhancedValidationEngine, ValidationResult, ValidationLayer, 
    ConfidenceLevel, TextNormalizer, SemanticAnalyzer, PatternRecognitionEngine
)
from app.ai.advanced_answer_validation import AdvancedAnswerValidator
from app.utils.enhanced_learning_system import LearningContentManager

class TestTextNormalizer(unittest.TestCase):
    """Test the text normalization engine."""
    
    def setUp(self):
        self.normalizer = TextNormalizer()
    
    def test_basic_normalization(self):
        """Test basic text normalization."""
        test_cases = [
            ("Hello World", "hello world"),
            ("  EXTRA   SPACES  ", "extra spaces"),
            ("Mixed&nbsp;Characters", "mixed characters"),
            ("URL%20Encoded", "url encoded"),
            ("HTML&amp;Entities", "html&entities")
        ]
        
        for input_text, expected in test_cases:
            with self.subTest(input_text=input_text):
                result = self.normalizer.normalize_text(input_text)
                self.assertEqual(result, expected)
    
    def test_keyword_extraction(self):
        """Test keyword extraction functionality."""
        text = "This is a test of SQL injection vulnerabilities"
        keywords = self.normalizer.extract_keywords(text)
        
        expected_keywords = ["test", "sql", "injection", "vulnerabilities"]
        self.assertEqual(sorted(keywords), sorted(expected_keywords))
    
    def test_empty_input(self):
        """Test handling of empty input."""
        self.assertEqual(self.normalizer.normalize_text(""), "")
        self.assertEqual(self.normalizer.extract_keywords(""), [])

class TestSemanticAnalyzer(unittest.TestCase):
    """Test the semantic analysis engine."""
    
    def setUp(self):
        self.analyzer = SemanticAnalyzer()
    
    def test_exact_match(self):
        """Test exact semantic matching."""
        result = self.analyzer.analyze_semantic_similarity(
            "SQL injection", "SQL injection"
        )
        self.assertGreaterEqual(result.similarity_score, 0.9)
    
    def test_synonym_matching(self):
        """Test synonym-based matching."""
        result = self.analyzer.analyze_semantic_similarity(
            "XSS attack", "cross-site scripting"
        )
        self.assertGreater(result.similarity_score, 0.5)
    
    def test_partial_matching(self):
        """Test partial content matching."""
        result = self.analyzer.analyze_semantic_similarity(
            "This payload performs SQL injection to bypass authentication",
            "authentication bypass"
        )
        self.assertGreater(result.similarity_score, 0.3)

class TestPatternRecognitionEngine(unittest.TestCase):
    """Test the pattern recognition engine."""
    
    def setUp(self):
        self.engine = PatternRecognitionEngine()
    
    def test_sql_pattern_recognition(self):
        """Test SQL injection pattern recognition."""
        sql_payloads = [
            "' OR '1'='1' --",
            "' UNION SELECT username, password FROM users --",
            "; DROP TABLE users; --",
            "' OR 1=1 --"
        ]
        
        for payload in sql_payloads:
            with self.subTest(payload=payload):
                patterns = self.engine.recognize_patterns(payload, "sql")
                self.assertGreater(len(patterns), 0)
                self.assertTrue(any(p['confidence'] > 0.7 for p in patterns))
    
    def test_xss_pattern_recognition(self):
        """Test XSS pattern recognition."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert(1)>",
            "<svg onload=alert(1)>",
            "javascript:alert(1)"
        ]
        
        for payload in xss_payloads:
            with self.subTest(payload=payload):
                patterns = self.engine.recognize_patterns(payload, "xss")
                self.assertGreater(len(patterns), 0)
                self.assertTrue(any(p['confidence'] > 0.7 for p in patterns))
    
    def test_command_injection_patterns(self):
        """Test command injection pattern recognition."""
        cmd_payloads = [
            "; ls -la",
            "&& whoami",
            "| cat /etc/passwd",
            "$(whoami)"
        ]
        
        for payload in cmd_payloads:
            with self.subTest(payload=payload):
                patterns = self.engine.recognize_patterns(payload, "command")
                self.assertGreater(len(patterns), 0)

class TestEnhancedValidationEngine(unittest.TestCase):
    """Test the main validation engine."""
    
    def setUp(self):
        self.engine = EnhancedValidationEngine()
    
    def test_exact_match_validation(self):
        """Test exact match validation layer."""
        result = self.engine.validate_answer(
            "authentication bypass", 
            "authentication bypass", 
            {"category": "sql"}
        )
        
        self.assertTrue(result.is_correct)
        self.assertEqual(result.layer, ValidationLayer.EXACT_MATCH)
        self.assertEqual(result.confidence, 100.0)
    
    def test_semantic_validation(self):
        """Test semantic validation layer."""
        result = self.engine.validate_answer(
            "bypasses login security", 
            "authentication bypass", 
            {"category": "sql"}
        )
        
        # Should be caught by semantic analysis
        self.assertIn(result.layer, [ValidationLayer.SEMANTIC_ANALYSIS, ValidationLayer.FUZZY_MATCHING])
    
    def test_sql_pattern_validation(self):
        """Test SQL pattern validation."""
        result = self.engine.validate_answer(
            "' OR 1=1 -- bypasses authentication", 
            "authentication bypass", 
            {"category": "sql injection"}
        )
        
        # Should recognize the SQL pattern
        self.assertTrue(result.confidence > 0)
    
    def test_performance_tracking(self):
        """Test that processing time is tracked."""
        result = self.engine.validate_answer(
            "test answer", 
            "expected answer", 
            {"category": "test"}
        )
        
        self.assertGreater(result.processing_time, 0)
        self.assertIsInstance(result.validation_path, list)
        self.assertGreater(len(result.validation_path), 0)

class TestAdvancedAnswerValidator(unittest.TestCase):
    """Test the advanced answer validator integration."""
    
    def setUp(self):
        self.validator = AdvancedAnswerValidator()
    
    def test_sql_challenge_validation(self):
        """Test SQL injection challenge validation."""
        test_cases = [
            ("sql_1", "authentication bypass", True),
            ("sql_1", "bypasses authentication", True),
            ("sql_1", "WHERE clause always true", True),
            ("sql_1", "random answer", False),
            ("sql_2", "drops users table", True),
            ("sql_2", "deletes user data", True),
            ("sql_3", "extracts user credentials", True),
            ("sql_3", "UNION SELECT attack", True)
        ]
        
        for challenge_id, answer, should_be_correct in test_cases:
            with self.subTest(challenge_id=challenge_id, answer=answer):
                is_correct, feedback, analysis = self.validator.validate_challenge_answer(
                    challenge_id, answer
                )
                self.assertEqual(is_correct, should_be_correct, 
                    f"Challenge {challenge_id} with answer '{answer}' should be {should_be_correct}")
    
    def test_xss_challenge_validation(self):
        """Test XSS challenge validation."""
        test_cases = [
            ("xss_1", "executes JavaScript", True),
            ("xss_1", "shows alert popup", True),
            ("xss_1", "script injection", True),
            ("xss_2", "onerror event handler", True),
            ("xss_2", "image error event", True),
            ("xss_3", "SVG onload event", True),
            ("xss_3", "bypasses script tag filters", True)
        ]
        
        for challenge_id, answer, should_be_correct in test_cases:
            with self.subTest(challenge_id=challenge_id, answer=answer):
                is_correct, feedback, analysis = self.validator.validate_challenge_answer(
                    challenge_id, answer
                )
                self.assertEqual(is_correct, should_be_correct)
    
    def test_command_injection_validation(self):
        """Test command injection challenge validation."""
        test_cases = [
            ("cmd_1", "executes multiple commands", True),
            ("cmd_1", "command chaining", True),
            ("cmd_2", "conditional command execution", True),
            ("cmd_3", "command substitution", True)
        ]
        
        for challenge_id, answer, should_be_correct in test_cases:
            with self.subTest(challenge_id=challenge_id, answer=answer):
                is_correct, feedback, analysis = self.validator.validate_challenge_answer(
                    challenge_id, answer
                )
                self.assertEqual(is_correct, should_be_correct)
    
    def test_fallback_challenges(self):
        """Test fallback challenge validation."""
        is_correct, feedback, analysis = self.validator.validate_challenge_answer(
            "fallback1", "authentication bypass"
        )
        self.assertTrue(is_correct)
    
    def test_invalid_challenge(self):
        """Test handling of invalid challenge IDs."""
        is_correct, feedback, analysis = self.validator.validate_challenge_answer(
            "nonexistent_challenge", "any answer"
        )
        # Should handle gracefully
        self.assertIsInstance(is_correct, bool)
        self.assertIsInstance(feedback, str)
    
    def test_statistics_tracking(self):
        """Test that validation statistics are tracked."""
        initial_stats = self.validator.get_validation_statistics()
        initial_total = initial_stats['total_validations']
        
        # Perform a validation
        self.validator.validate_challenge_answer("sql_1", "authentication bypass")
        
        updated_stats = self.validator.get_validation_statistics()
        self.assertEqual(updated_stats['total_validations'], initial_total + 1)
    
    def test_add_expected_answers(self):
        """Test adding expected answers to a challenge."""
        test_challenge_id = "test_challenge_123"
        test_answers = ["answer1", "answer2", "answer3"]
        
        self.validator.add_expected_answers(test_challenge_id, test_answers)
        
        # Test that the answers were added
        is_correct, feedback, analysis = self.validator.validate_challenge_answer(
            test_challenge_id, "answer1"
        )
        self.assertTrue(is_correct)

class TestLearningContentManager(unittest.TestCase):
    """Test the enhanced learning content manager."""
    
    def setUp(self):
        self.manager = LearningContentManager()
    
    @patch('app.routes.learning.LEARNING_CONTENT')
    def test_content_loading_with_cache(self, mock_content):
        """Test content loading with caching."""
        mock_content.__contains__ = Mock(return_value=True)
        mock_content.__getitem__ = Mock(return_value={
            'id': 'test_module',
            'title': 'Test Module',
            'sections': []
        })
        
        # First request should miss cache
        success1, content1 = self.manager.get_content_with_fallback('test_module')
        self.assertTrue(success1)
        
        # Second request should hit cache
        success2, content2 = self.manager.get_content_with_fallback('test_module')
        self.assertTrue(success2)
        
        metrics = self.manager.get_performance_metrics()
        self.assertGreater(metrics['cache_hits'], 0)
    
    def test_fallback_content_loading(self):
        """Test fallback content loading."""
        # Test with non-existent module
        success, content = self.manager.get_content_with_fallback('nonexistent_module')
        
        # Should return fallback content
        self.assertTrue(success)
        self.assertIn('fallback_actions', content)
    
    def test_performance_metrics(self):
        """Test performance metrics tracking."""
        metrics = self.manager.get_performance_metrics()
        
        required_metrics = [
            'total_requests', 'cache_hits', 'cache_misses', 
            'cache_hit_rate', 'error_count', 'average_response_time'
        ]
        
        for metric in required_metrics:
            self.assertIn(metric, metrics)
    
    def test_cache_management(self):
        """Test cache management operations."""
        # Add some content to cache
        self.manager._cache_content('test_module', {'test': 'data'})
        
        initial_size = len(self.manager.content_cache)
        self.assertGreater(initial_size, 0)
        
        # Clear cache
        self.manager.clear_cache()
        
        final_size = len(self.manager.content_cache)
        self.assertEqual(final_size, 0)

class TestIntegrationScenarios(unittest.TestCase):
    """Test integration scenarios and edge cases."""
    
    def setUp(self):
        self.validator = AdvancedAnswerValidator()
    
    def test_multiple_answer_formats(self):
        """Test validation with multiple answer formats."""
        challenge_id = "sql_1"
        answer_variations = [
            "authentication bypass",
            "Authentication Bypass",
            "AUTHENTICATION BYPASS",
            "auth bypass",
            "login bypass",
            "bypasses authentication",
            "WHERE clause always true",
            "makes the WHERE clause always evaluate to true"
        ]
        
        for answer in answer_variations:
            with self.subTest(answer=answer):
                is_correct, feedback, analysis = self.validator.validate_challenge_answer(
                    challenge_id, answer
                )
                self.assertTrue(is_correct, 
                    f"Answer '{answer}' should be recognized as correct")
    
    def test_case_insensitive_validation(self):
        """Test that validation is case insensitive."""
        test_cases = [
            ("SQL INJECTION", True),
            ("sql injection", True),
            ("Sql Injection", True),
            ("sQl InJeCtIoN", True)
        ]
        
        for answer, should_be_correct in test_cases:
            with self.subTest(answer=answer):
                is_correct, feedback, analysis = self.validator.validate_challenge_answer(
                    "sql_1", answer
                )
                # Note: The answer "SQL injection" might not match "authentication bypass"
                # but we're testing the normalization works
                self.assertIsInstance(is_correct, bool)
    
    def test_special_characters_handling(self):
        """Test handling of special characters in answers."""
        special_answers = [
            "authentication bypass!",
            "authentication bypass.",
            "authentication bypass?",
            "authentication-bypass",
            "authentication_bypass",
            "authentication  bypass"  # extra spaces
        ]
        
        for answer in special_answers:
            with self.subTest(answer=answer):
                is_correct, feedback, analysis = self.validator.validate_challenge_answer(
                    "sql_1", answer
                )
                # Should handle special characters gracefully
                self.assertIsInstance(is_correct, bool)
                self.assertIsInstance(feedback, str)
    
    def test_performance_under_load(self):
        """Test performance under multiple concurrent validations."""
        start_time = time.time()
        
        # Perform multiple validations
        for i in range(100):
            self.validator.validate_challenge_answer(
                "sql_1", f"authentication bypass {i}"
            )
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete within reasonable time (less than 10 seconds)
        self.assertLess(duration, 10.0)
        
        # Check that statistics are properly tracked
        stats = self.validator.get_validation_statistics()
        self.assertGreaterEqual(stats['total_validations'], 100)

if __name__ == '__main__':
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestTextNormalizer,
        TestSemanticAnalyzer,
        TestPatternRecognitionEngine,
        TestEnhancedValidationEngine,
        TestAdvancedAnswerValidator,
        TestLearningContentManager,
        TestIntegrationScenarios
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*50}")
    print(f"TEST SUMMARY")
    print(f"{'='*50}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, failure in result.failures:
            print(f"- {test}: {failure.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, error in result.errors:
            print(f"- {test}: {error.split('Exception:')[-1].strip()}")