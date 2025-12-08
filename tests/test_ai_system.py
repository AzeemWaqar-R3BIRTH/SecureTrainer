"""
Comprehensive Test Suite for AI Challenge System
Production-ready testing for SecureTrainer AI components

Tests cover:
1. AI challenge engine functionality
2. Validation system accuracy
3. Adaptive scoring correctness
4. Hint generation quality
5. Integration layer performance
6. Real-time ML pipeline
"""

import unittest
import asyncio
import json
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import AI components
from app.ai.challenge_engine import AIChallengEngine, PerformanceMetrics, DifficultyLevel
from app.ai.validation_system import AdvancedChallengeValidator, ValidationResult, PatternMatch
from app.ai.adaptive_scoring import AdaptiveScoringEngine, ScoringFactors, PerformanceSnapshot
from app.ai.hint_generator import IntelligentHintGenerator, HintContext, LearningStyle, HintLevel
from app.ai.enhanced_challenges import EnhancedChallengeModel, ChallengeVariant
from app.ai.ai_integration import AIOrchestrator, AIResponse, UserSession

class TestAIChallengeEngine(unittest.TestCase):
    """Test suite for AI Challenge Engine."""
    
    def setUp(self):
        """Set up test environment."""
        self.engine = AIChallengEngine()
        self.test_user_id = "test_user_123"
        
    def test_analyze_real_time_performance(self):
        """Test real-time performance analysis."""
        # Mock challenge attempt data
        attempt_data = {
            'is_correct': True,
            'completion_time': 120,
            'hint_count': 1,
            'category': 'sql_injection'
        }
        
        # Test performance analysis
        metrics = self.engine.analyze_real_time_performance(self.test_user_id, attempt_data)
        
        # Assertions
        self.assertIsInstance(metrics, PerformanceMetrics)
        self.assertGreaterEqual(metrics.success_rate, 0.0)
        self.assertLessEqual(metrics.success_rate, 1.0)
        self.assertGreaterEqual(metrics.average_completion_time, 0.0)
        
    def test_predict_optimal_difficulty(self):
        """Test optimal difficulty prediction."""
        # Create test performance metrics
        metrics = PerformanceMetrics(
            success_rate=0.8,
            average_completion_time=90.0,
            hint_usage_rate=1.5,
            category_mastery={'sql_injection': 0.75},
            learning_velocity=2.0,
            consecutive_successes=3,
            consecutive_failures=0,
            skill_progression_rate=0.1
        )
        
        # Test difficulty prediction
        difficulty = self.engine.predict_optimal_difficulty(
            self.test_user_id, 'sql_injection', metrics
        )
        
        # Assertions
        self.assertIsInstance(difficulty, DifficultyLevel)
        self.assertIn(difficulty, [DifficultyLevel.BEGINNER, DifficultyLevel.INTERMEDIATE, 
                                  DifficultyLevel.ADVANCED, DifficultyLevel.EXPERT])
        
    def test_generate_adaptive_challenge_sequence(self):
        """Test adaptive challenge sequence generation."""
        # Test sequence generation
        sequence = self.engine.generate_adaptive_challenge_sequence(
            self.test_user_id, 'sql_injection', count=3
        )
        
        # Assertions
        self.assertIsInstance(sequence, list)
        self.assertLessEqual(len(sequence), 3)
        
        if sequence:
            # Check challenge structure
            challenge = sequence[0]
            self.assertIn('id', challenge)
            self.assertIn('ai_metadata', challenge)
            
    def test_calculate_dynamic_score(self):
        """Test dynamic score calculation."""
        # Mock challenge and performance data
        challenge = {
            'score_weight': 100,
            'difficulty': 'intermediate',
            'category': 'sql_injection'
        }
        
        performance_data = {
            'completion_time': 120,
            'hint_count': 1,
            'is_correct': True
        }
        
        # Test score calculation
        score = self.engine.calculate_dynamic_score(
            self.test_user_id, challenge, performance_data
        )
        
        # Assertions
        self.assertIsInstance(score, int)
        self.assertGreaterEqual(score, 10)  # Minimum score
        self.assertLessEqual(score, 5000)   # Maximum reasonable score

class TestValidationSystem(unittest.TestCase):
    """Test suite for Advanced Validation System."""
    
    def setUp(self):
        """Set up test environment."""
        self.validator = AdvancedChallengeValidator()
        
    def test_sql_injection_validation(self):
        """Test SQL injection payload validation."""
        test_cases = [
            ("' OR '1'='1' --", ValidationResult.GOOD),
            ("admin'--", ValidationResult.ACCEPTABLE),
            ("' UNION SELECT username, password FROM users--", ValidationResult.GOOD),
            ("normal_input", ValidationResult.INCORRECT),
            ("'; DROP TABLE users; --", ValidationResult.GOOD)
        ]
        
        context = {'challenge_category': 'sql_injection'}
        
        for payload, expected_min_level in test_cases:
            with self.subTest(payload=payload):
                result, patterns = self.validator.validate_sql_injection(payload, context)
                
                # Check that result is appropriate
                self.assertIsInstance(result, ValidationResult)
                self.assertIsInstance(patterns, list)
                
                # For valid payloads, should not be incorrect
                if expected_min_level != ValidationResult.INCORRECT:
                    self.assertNotEqual(result, ValidationResult.INCORRECT)
                    
    def test_xss_validation(self):
        """Test XSS payload validation."""
        test_cases = [
            ("<script>alert('XSS')</script>", ValidationResult.ACCEPTABLE),
            ("<img src=x onerror=alert(1)>", ValidationResult.GOOD),
            ("<svg onload=alert(1)>", ValidationResult.GOOD),
            ("normal text", ValidationResult.INCORRECT),
            ("javascript:alert('XSS')", ValidationResult.ACCEPTABLE)
        ]
        
        context = {'challenge_category': 'xss'}
        
        for payload, expected_min_level in test_cases:
            with self.subTest(payload=payload):
                result, patterns = self.validator.validate_xss_payload(payload, context)
                
                self.assertIsInstance(result, ValidationResult)
                self.assertIsInstance(patterns, list)
                
    def test_command_injection_validation(self):
        """Test command injection payload validation."""
        test_cases = [
            ("127.0.0.1; ls", ValidationResult.ACCEPTABLE),
            ("test && whoami", ValidationResult.GOOD),
            ("$(whoami)", ValidationResult.GOOD),
            ("`id`", ValidationResult.GOOD),
            ("normal_input", ValidationResult.INCORRECT)
        ]
        
        context = {'challenge_category': 'command_injection'}
        
        for payload, expected_min_level in test_cases:
            with self.subTest(payload=payload):
                result, patterns = self.validator.validate_command_injection(payload, context)
                
                self.assertIsInstance(result, ValidationResult)
                self.assertIsInstance(patterns, list)
                
    def test_evasion_technique_detection(self):
        """Test evasion technique detection."""
        # Test URL encoding detection
        url_encoded = "admin%27%20OR%20%271%27%3D%271"
        evasions = self.validator._detect_evasion_techniques(url_encoded)
        self.assertIn('url_encoding', evasions)
        
        # Test HTML encoding detection
        html_encoded = "admin&#39; OR &#39;1&#39;=&#39;1"
        evasions = self.validator._detect_evasion_techniques(html_encoded)
        self.assertIn('html_encoding', evasions)
        
    def test_pattern_confidence_scoring(self):
        """Test pattern confidence scoring."""
        high_confidence_payload = "' OR '1'='1' --"
        low_confidence_payload = "maybe injection?"
        
        context = {'challenge_category': 'sql_injection'}
        
        # High confidence test
        result1, patterns1 = self.validator.validate_sql_injection(high_confidence_payload, context)
        if patterns1:
            self.assertGreater(patterns1[0].confidence, 0.7)
            
        # Low confidence test
        result2, patterns2 = self.validator.validate_sql_injection(low_confidence_payload, context)
        # Should have no patterns or low confidence
        if patterns2:
            self.assertLess(patterns2[0].confidence, 0.8)

class TestAdaptiveScoringEngine(unittest.TestCase):
    """Test suite for Adaptive Scoring Engine."""
    
    def setUp(self):
        """Set up test environment."""
        self.scoring_engine = AdaptiveScoringEngine()
        self.test_user_id = "test_user_scoring"
        
    def test_scoring_factors_calculation(self):
        """Test scoring factors calculation."""
        # Mock user performance
        user_performance = PerformanceSnapshot(
            user_id=self.test_user_id,
            timestamp=datetime.now(),
            overall_success_rate=0.7,
            category_success_rates={'sql_injection': 0.8},
            average_completion_time=120.0,
            hint_usage_average=1.5,
            current_streak=3,
            level=5,
            total_score=2500,
            learning_velocity=1.8,
            recent_improvement=0.1
        )
        
        challenge = {
            'score_weight': 100,
            'difficulty': 'intermediate',
            'category': 'sql_injection'
        }
        
        attempt_data = {
            'completion_time': 90,
            'hint_count': 1,
            'attempt_number': 1
        }
        
        # Calculate scoring factors
        factors = self.scoring_engine._calculate_scoring_factors(
            user_performance, challenge, attempt_data
        )
        
        # Assertions
        self.assertIsInstance(factors, ScoringFactors)
        self.assertEqual(factors.base_score, 100)
        self.assertGreater(factors.difficulty_multiplier, 1.0)  # Intermediate difficulty
        self.assertGreater(factors.time_multiplier, 1.0)       # Fast completion
        self.assertGreaterEqual(factors.hint_multiplier, 0.5)  # Reasonable hint usage
        
    def test_adaptive_score_calculation(self):
        """Test complete adaptive score calculation."""
        challenge = {
            'id': 'test_challenge',
            'score_weight': 100,
            'difficulty': 'intermediate',
            'category': 'sql_injection'
        }
        
        attempt_data = {
            'completion_time': 120,
            'hint_count': 1,
            'attempt_number': 1,
            'is_correct': True
        }
        
        # Calculate score
        final_score, breakdown = self.scoring_engine.calculate_adaptive_score(
            self.test_user_id, challenge, attempt_data
        )
        
        # Assertions
        self.assertIsInstance(final_score, int)
        self.assertGreater(final_score, 0)
        self.assertIsNotNone(breakdown)
        self.assertIsInstance(breakdown.explanation, list)
        self.assertTrue(len(breakdown.explanation) > 0)
        
    def test_scoring_consistency(self):
        """Test scoring consistency across multiple attempts."""
        challenge = {
            'id': 'consistency_test',
            'score_weight': 100,
            'difficulty': 'beginner',
            'category': 'sql_injection'
        }
        
        attempt_data = {
            'completion_time': 60,
            'hint_count': 0,
            'attempt_number': 1,
            'is_correct': True
        }
        
        # Calculate same scenario multiple times
        scores = []
        for _ in range(5):
            score, _ = self.scoring_engine.calculate_adaptive_score(
                self.test_user_id, challenge, attempt_data
            )
            scores.append(score)
            
        # Scores should be identical for same input
        self.assertEqual(len(set(scores)), 1, "Scoring should be consistent")
        
    def test_leaderboard_calculation(self):
        """Test leaderboard score calculation."""
        # Test leaderboard generation
        leaderboard = self.scoring_engine.calculate_leaderboard_scores('all_time')
        
        # Should return a list (may be empty in test environment)
        self.assertIsInstance(leaderboard, list)

class TestHintGenerator(unittest.TestCase):
    """Test suite for Intelligent Hint Generator."""
    
    def setUp(self):
        """Set up test environment."""
        self.hint_generator = IntelligentHintGenerator()
        
    def test_hint_level_determination(self):
        """Test hint level determination logic."""
        # Test with independent learner
        context_independent = HintContext(
            user_id="test_user",
            challenge_category="sql_injection",
            difficulty_level="intermediate",
            attempt_count=1,
            time_spent=60.0,
            previous_hints=[],
            user_learning_style=LearningStyle.INDEPENDENT,
            struggle_indicators=[],
            skill_level=0.7
        )
        
        struggle_analysis = {'severity': 0.2, 'indicators': {}, 'primary_struggle': None, 'recommended_approach': 'minimal'}
        
        level = self.hint_generator._determine_hint_level(context_independent, struggle_analysis)
        self.assertEqual(level, HintLevel.SUBTLE)
        
        # Test with guided learner
        context_guided = HintContext(
            user_id="test_user",
            challenge_category="sql_injection",
            difficulty_level="intermediate",
            attempt_count=1,
            time_spent=60.0,
            previous_hints=[],
            user_learning_style=LearningStyle.GUIDED,
            struggle_indicators=[],
            skill_level=0.7
        )
        
        level = self.hint_generator._determine_hint_level(context_guided, struggle_analysis)
        self.assertEqual(level, HintLevel.DETAILED)
        
    def test_category_hint_generation(self):
        """Test category-specific hint generation."""
        challenge = {
            'id': 'sql_test',
            'category': 'sql_injection',
            'difficulty': 'beginner'
        }
        
        context = HintContext(
            user_id="test_user",
            challenge_category="sql_injection",
            difficulty_level="beginner",
            attempt_count=1,
            time_spent=60.0,
            previous_hints=[],
            user_learning_style=LearningStyle.ANALYTICAL,
            struggle_indicators=[],
            skill_level=0.5
        )
        
        # Generate hint
        hint = self.hint_generator.generate_adaptive_hint(context, challenge)
        
        # Assertions
        self.assertIsNotNone(hint.content)
        self.assertIsInstance(hint.content, str)
        self.assertGreater(len(hint.content), 10)  # Should be substantial
        self.assertIsInstance(hint.level, HintLevel)
        self.assertGreater(hint.effectiveness_prediction, 0.0)
        self.assertLess(hint.effectiveness_prediction, 1.0)
        
    def test_hint_personalization(self):
        """Test hint personalization for different learning styles."""
        base_hint = "Consider SQL injection techniques"
        
        context = HintContext(
            user_id="test_user",
            challenge_category="sql_injection",
            difficulty_level="beginner",
            attempt_count=1,
            time_spent=60.0,
            previous_hints=[],
            user_learning_style=LearningStyle.VISUAL,
            struggle_indicators=[],
            skill_level=0.5
        )
        
        # Test different learning styles
        for style in LearningStyle:
            personalized = self.hint_generator._personalize_hint(base_hint, style, context)
            self.assertIsInstance(personalized, str)
            self.assertGreaterEqual(len(personalized), len(base_hint))

class TestEnhancedChallengeModel(unittest.TestCase):
    """Test suite for Enhanced Challenge Model."""
    
    def setUp(self):
        """Set up test environment."""
        self.challenge_model = EnhancedChallengeModel()
        
    def test_challenge_database_loading(self):
        """Test challenge database initialization."""
        # Check that challenges are loaded
        self.assertIsInstance(self.challenge_model.challenge_variants, dict)
        self.assertGreater(len(self.challenge_model.challenge_variants), 0)
        
        # Check specific categories
        self.assertIn('sql_injection', self.challenge_model.challenge_variants)
        self.assertIn('xss', self.challenge_model.challenge_variants)
        
    def test_difficulty_filtering(self):
        """Test challenge filtering by difficulty."""
        from app.ai.enhanced_challenges import DifficultyLevel
        
        # Test beginner challenges
        beginner_challenges = self.challenge_model.get_challenges_by_difficulty(
            DifficultyLevel.BEGINNER
        )
        
        self.assertIsInstance(beginner_challenges, list)
        
        if beginner_challenges:
            for challenge in beginner_challenges:
                self.assertEqual(challenge.difficulty, DifficultyLevel.BEGINNER)
                
    def test_adaptive_sequence_generation(self):
        """Test adaptive challenge sequence generation."""
        # Test for different skill levels
        skill_levels = [0.2, 0.5, 0.8]
        
        for skill in skill_levels:
            with self.subTest(skill_level=skill):
                sequence = self.challenge_model.get_adaptive_sequence(
                    skill, category='sql_injection', count=3
                )
                
                self.assertIsInstance(sequence, list)
                self.assertLessEqual(len(sequence), 3)
                
                if sequence:
                    # Check challenge structure
                    challenge = sequence[0]
                    self.assertIsInstance(challenge, ChallengeVariant)
                    self.assertIsNotNone(challenge.id)
                    self.assertIsNotNone(challenge.title)
                    
    def test_challenge_by_id_retrieval(self):
        """Test challenge retrieval by ID."""
        # First get a challenge to test with
        all_challenges = []
        for challenges in self.challenge_model.challenge_variants.values():
            all_challenges.extend(challenges)
            
        if all_challenges:
            test_challenge = all_challenges[0]
            retrieved = self.challenge_model.get_challenge_by_id(test_challenge.id)
            
            self.assertIsNotNone(retrieved)
            self.assertEqual(retrieved.id, test_challenge.id)
            
        # Test with non-existent ID
        non_existent = self.challenge_model.get_challenge_by_id("non_existent_id")
        self.assertIsNone(non_existent)

class TestAIIntegration(unittest.TestCase):
    """Test suite for AI Integration Layer."""
    
    def setUp(self):
        """Set up test environment."""
        self.orchestrator = AIOrchestrator()
        self.test_user_id = "integration_test_user"
        
    async def async_test_session_management(self):
        """Test AI session management."""
        user_data = {
            'username': 'test_user',
            'level': 3,
            'score': 1500,
            'challenges_completed': ['sql_beginner_001']
        }
        
        # Start session
        session = await self.orchestrator.start_user_session(self.test_user_id, user_data)
        
        # Assertions
        self.assertIsInstance(session, UserSession)
        self.assertEqual(session.user_id, self.test_user_id)
        self.assertIsInstance(session.learning_style, LearningStyle)
        self.assertIsInstance(session.skill_profile, dict)
        
        # Check session is tracked
        self.assertIn(session.session_id, self.orchestrator.active_sessions)
        
        return session.session_id
        
    def test_session_management(self):
        """Test session management with async wrapper."""
        async def run_test():
            return await self.async_test_session_management()
            
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            session_id = loop.run_until_complete(run_test())
            self.assertIsNotNone(session_id)
        finally:
            loop.close()
            
    def test_system_performance_metrics(self):
        """Test system performance metrics."""
        metrics = self.orchestrator.get_system_performance_metrics()
        
        # Check required fields
        self.assertIn('orchestrator_metrics', metrics)
        self.assertIn('active_sessions', metrics)
        self.assertIn('component_status', metrics)
        
        # Check component status
        components = metrics['component_status']
        expected_components = ['challenge_engine', 'validator', 'scoring_engine', 
                             'hint_generator', 'challenge_model']
        
        for component in expected_components:
            self.assertIn(component, components)
            self.assertEqual(components[component], 'active')

class TestPerformanceAndSecurity(unittest.TestCase):
    """Test suite for performance and security validation."""
    
    def setUp(self):
        """Set up performance testing environment."""
        self.validator = AdvancedChallengeValidator()
        self.scoring_engine = AdaptiveScoringEngine()
        
    def test_validation_performance(self):
        """Test validation system performance."""
        test_payload = "' OR '1'='1' --"
        context = {'challenge_category': 'sql_injection'}
        
        # Measure performance
        start_time = time.time()
        iterations = 100
        
        for _ in range(iterations):
            result, patterns = self.validator.validate_sql_injection(test_payload, context)
            
        end_time = time.time()
        avg_time = (end_time - start_time) / iterations
        
        # Should be fast (under 10ms per validation)
        self.assertLess(avg_time, 0.01, f"Validation too slow: {avg_time:.4f}s per validation")
        
    def test_scoring_performance(self):
        """Test scoring system performance."""
        challenge = {
            'score_weight': 100,
            'difficulty': 'intermediate',
            'category': 'sql_injection'
        }
        
        attempt_data = {
            'completion_time': 120,
            'hint_count': 1,
            'attempt_number': 1,
            'is_correct': True
        }
        
        # Measure performance
        start_time = time.time()
        iterations = 50
        
        for _ in range(iterations):
            score, breakdown = self.scoring_engine.calculate_adaptive_score(
                "perf_test_user", challenge, attempt_data
            )
            
        end_time = time.time()
        avg_time = (end_time - start_time) / iterations
        
        # Should be fast (under 50ms per calculation)
        self.assertLess(avg_time, 0.05, f"Scoring too slow: {avg_time:.4f}s per calculation")
        
    def test_input_sanitization(self):
        """Test input sanitization and security."""
        # Test malicious inputs
        malicious_inputs = [
            "<script>alert('xss')</script>",
            "'; DROP TABLE users; --",
            "../../../etc/passwd",
            "eval(malicious_code)",
            "' UNION SELECT * FROM sensitive_data --"
        ]
        
        context = {'challenge_category': 'sql_injection'}
        
        for malicious_input in malicious_inputs:
            with self.subTest(input=malicious_input):
                # Should not crash or cause errors
                try:
                    result, patterns = self.validator.validate_sql_injection(malicious_input, context)
                    # Should return a valid result
                    self.assertIsInstance(result, ValidationResult)
                except Exception as e:
                    self.fail(f"Validation crashed on input '{malicious_input}': {e}")
                    
    def test_memory_usage(self):
        """Test memory usage under load."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform many operations
        validator = AdvancedChallengeValidator()
        test_payloads = ["' OR '1'='1' --"] * 1000
        context = {'challenge_category': 'sql_injection'}
        
        for payload in test_payloads:
            validator.validate_sql_injection(payload, context)
            
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Should not leak significant memory (under 50MB increase)
        self.assertLess(memory_increase, 50, f"Memory leak detected: {memory_increase:.2f}MB increase")

def run_test_suite():
    """Run the complete test suite."""
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestAIChallengeEngine,
        TestValidationSystem,
        TestAdaptiveScoringEngine,
        TestHintGenerator,
        TestEnhancedChallengeModel,
        TestAIIntegration,
        TestPerformanceAndSecurity
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Return success status
    return result.wasSuccessful()

if __name__ == '__main__':
    print("=" * 60)
    print("SecureTrainer AI System Test Suite")
    print("=" * 60)
    
    success = run_test_suite()
    
    if success:
        print("\n✅ All tests passed successfully!")
        exit(0)
    else:
        print("\n❌ Some tests failed!")
        exit(1)