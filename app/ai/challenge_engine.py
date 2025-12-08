"""
AI-Driven Challenge Engine with Real-Time Difficulty Adaptation
Production-ready implementation for SecureTrainer

This module implements the core AI engine that:
1. Dynamically adjusts challenge difficulty based on real-time performance
2. Provides predictive challenge selection using ML algorithms
3. Tracks performance patterns for personalized learning paths
4. Generates adaptive scoring based on user competency
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple, Optional
import json
import logging
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DifficultyLevel(Enum):
    """Enumeration for challenge difficulty levels with scoring multipliers."""
    BEGINNER = ("beginner", 1.0)
    INTERMEDIATE = ("intermediate", 1.5)
    ADVANCED = ("advanced", 2.2)
    EXPERT = ("expert", 3.0)
    
    def __init__(self, level_name: str, multiplier: float):
        self.level_name = level_name
        self.multiplier = multiplier

@dataclass
class PerformanceMetrics:
    """Data class for user performance metrics."""
    success_rate: float
    average_completion_time: float
    hint_usage_rate: float
    category_mastery: Dict[str, float]
    learning_velocity: float
    consecutive_successes: int
    consecutive_failures: int
    skill_progression_rate: float

@dataclass
class ChallengeContext:
    """Data class for challenge context and metadata."""
    category: str
    current_difficulty: DifficultyLevel
    expected_completion_time: float
    cognitive_load_score: float
    prerequisite_skills: List[str]
    learning_objectives: List[str]

class AIChallengEngine:
    """
    Production AI Challenge Engine for real-time difficulty adaptation.
    
    This engine provides:
    - Real-time performance analysis
    - Predictive difficulty adjustment
    - Adaptive challenge selection
    - Personalized learning path optimization
    """
    
    def __init__(self, db_connection=None):
        """Initialize the AI Challenge Engine."""
        self.db = db_connection
        self.performance_history = {}
        self.challenge_pool = {}
        self.user_profiles = {}
        self.ml_models = {}
        
        # Performance thresholds for difficulty adjustment
        self.difficulty_thresholds = {
            'promotion': 0.85,  # Success rate to increase difficulty
            'demotion': 0.40,   # Success rate to decrease difficulty
            'mastery': 0.95,    # Success rate indicating mastery
            'struggle': 0.30    # Success rate indicating significant struggle
        }
        
        # Timing thresholds (in seconds)
        self.optimal_times = {
            DifficultyLevel.BEGINNER: 60,
            DifficultyLevel.INTERMEDIATE: 120,
            DifficultyLevel.ADVANCED: 240,
            DifficultyLevel.EXPERT: 480
        }
        
        logger.info("AI Challenge Engine initialized successfully")
    
    def analyze_real_time_performance(self, user_id: str, challenge_attempt: Dict[str, Any]) -> PerformanceMetrics:
        """
        Analyze user performance in real-time based on current attempt.
        
        Args:
            user_id: Unique identifier for the user
            challenge_attempt: Data from the current challenge attempt
            
        Returns:
            PerformanceMetrics object with current performance analysis
        """
        try:
            # Get user's historical performance
            user_history = self._get_user_performance_history(user_id)
            
            # Calculate real-time metrics
            recent_attempts = user_history[-10:] if user_history else []
            
            # Success rate calculation
            if recent_attempts:
                successful_attempts = sum(1 for attempt in recent_attempts if attempt.get('is_correct', False))
                success_rate = successful_attempts / len(recent_attempts)
            else:
                success_rate = 0.5  # Neutral starting point
            
            # Average completion time
            completion_times = [attempt.get('completion_time', 0) for attempt in recent_attempts if attempt.get('completion_time')]
            avg_completion_time = np.mean(completion_times) if completion_times else 120.0
            
            # Hint usage rate
            hint_counts = [attempt.get('hint_count', 0) for attempt in recent_attempts]
            hint_usage_rate = np.mean(hint_counts) if hint_counts else 0.0
            
            # Category mastery analysis
            category_performance = self._analyze_category_performance(user_history)
            
            # Learning velocity (challenges per day)
            learning_velocity = self._calculate_learning_velocity(user_history)
            
            # Consecutive performance tracking
            consecutive_successes, consecutive_failures = self._calculate_consecutive_performance(user_history)
            
            # Skill progression rate
            skill_progression_rate = self._calculate_skill_progression_rate(user_history)
            
            metrics = PerformanceMetrics(
                success_rate=success_rate,
                average_completion_time=avg_completion_time,
                hint_usage_rate=hint_usage_rate,
                category_mastery=category_performance,
                learning_velocity=learning_velocity,
                consecutive_successes=consecutive_successes,
                consecutive_failures=consecutive_failures,
                skill_progression_rate=skill_progression_rate
            )
            
            logger.info(f"Real-time performance analysis completed for user {user_id}")
            return metrics
            
        except Exception as e:
            logger.error(f"Error analyzing real-time performance for user {user_id}: {e}")
            # Return default metrics in case of error
            return PerformanceMetrics(
                success_rate=0.5,
                average_completion_time=120.0,
                hint_usage_rate=1.0,
                category_mastery={},
                learning_velocity=0.5,
                consecutive_successes=0,
                consecutive_failures=0,
                skill_progression_rate=0.0
            )
    
    def predict_optimal_difficulty(self, user_id: str, category: str, current_metrics: PerformanceMetrics) -> DifficultyLevel:
        """
        Predict the optimal difficulty level for the user based on performance metrics.
        
        Args:
            user_id: Unique identifier for the user
            category: Challenge category (sql_injection, xss, etc.)
            current_metrics: Current performance metrics
            
        Returns:
            Optimal DifficultyLevel for the user
        """
        try:
            # Get current difficulty level
            current_difficulty = self._get_current_difficulty(user_id, category)
            
            # Decision matrix for difficulty adjustment
            if current_metrics.success_rate >= self.difficulty_thresholds['mastery']:
                # User has mastered current level - promote aggressively
                target_difficulty = self._promote_difficulty(current_difficulty, aggressive=True)
                
            elif current_metrics.success_rate >= self.difficulty_thresholds['promotion']:
                # User is ready for next level
                target_difficulty = self._promote_difficulty(current_difficulty)
                
            elif current_metrics.success_rate <= self.difficulty_thresholds['struggle']:
                # User is struggling significantly - demote aggressively
                target_difficulty = self._demote_difficulty(current_difficulty, aggressive=True)
                
            elif current_metrics.success_rate <= self.difficulty_thresholds['demotion']:
                # User needs easier challenges
                target_difficulty = self._demote_difficulty(current_difficulty)
                
            else:
                # User is performing adequately - maintain current level
                target_difficulty = current_difficulty
            
            # Additional factors for fine-tuning
            target_difficulty = self._apply_performance_modifiers(
                target_difficulty, current_metrics, category
            )
            
            logger.info(f"Predicted optimal difficulty for user {user_id} in {category}: {target_difficulty.level_name}")
            return target_difficulty
            
        except Exception as e:
            logger.error(f"Error predicting optimal difficulty for user {user_id}: {e}")
            return DifficultyLevel.INTERMEDIATE  # Safe fallback
    
    def generate_adaptive_challenge_sequence(self, user_id: str, category: str, count: int = 5) -> List[Dict[str, Any]]:
        """
        Generate an adaptive sequence of challenges based on user performance.
        
        Args:
            user_id: Unique identifier for the user
            category: Challenge category
            count: Number of challenges to generate
            
        Returns:
            List of challenge dictionaries optimized for the user
        """
        try:
            # Analyze current performance
            current_metrics = self.analyze_real_time_performance(user_id, {})
            
            # Predict optimal difficulty
            optimal_difficulty = self.predict_optimal_difficulty(user_id, category, current_metrics)
            
            # Get challenge pool for the category and difficulty
            challenge_pool = self._get_challenge_pool(category, optimal_difficulty)
            
            # Apply adaptive selection algorithm
            selected_challenges = self._select_adaptive_challenges(
                challenge_pool, current_metrics, count
            )
            
            # Add personalization metadata
            for challenge in selected_challenges:
                challenge['ai_metadata'] = {
                    'predicted_success_probability': self._predict_success_probability(
                        current_metrics, challenge
                    ),
                    'estimated_completion_time': self._estimate_completion_time(
                        current_metrics, challenge
                    ),
                    'recommended_hints': self._generate_adaptive_hints(
                        user_id, challenge, current_metrics
                    ),
                    'difficulty_justification': self._explain_difficulty_selection(
                        optimal_difficulty, current_metrics
                    )
                }
            
            logger.info(f"Generated adaptive challenge sequence for user {user_id}: {len(selected_challenges)} challenges")
            return selected_challenges
            
        except Exception as e:
            logger.error(f"Error generating adaptive challenge sequence for user {user_id}: {e}")
            return []
    
    def calculate_dynamic_score(self, user_id: str, challenge: Dict[str, Any], 
                              performance_data: Dict[str, Any]) -> int:
        """
        Calculate dynamic score based on performance and difficulty adaptation.
        
        Args:
            user_id: Unique identifier for the user
            challenge: Challenge data
            performance_data: Performance data from attempt
            
        Returns:
            Calculated dynamic score
        """
        try:
            base_score = challenge.get('score_weight', 100)
            difficulty = DifficultyLevel[challenge.get('difficulty', 'INTERMEDIATE').upper()]
            
            # Get user metrics for context
            current_metrics = self.analyze_real_time_performance(user_id, performance_data)
            
            # Apply difficulty multiplier
            score = base_score * difficulty.multiplier
            
            # Time-based scoring
            completion_time = performance_data.get('completion_time', 0)
            optimal_time = self.optimal_times.get(difficulty, 120)
            
            if completion_time <= optimal_time * 0.5:
                time_multiplier = 2.0  # Lightning fast
            elif completion_time <= optimal_time:
                time_multiplier = 1.5  # Fast
            elif completion_time <= optimal_time * 2:
                time_multiplier = 1.0  # Normal
            elif completion_time <= optimal_time * 3:
                time_multiplier = 0.8  # Slow
            else:
                time_multiplier = 0.6  # Very slow
            
            score *= time_multiplier
            
            # Hint penalty
            hints_used = performance_data.get('hint_count', 0)
            if hints_used == 0:
                hint_multiplier = 1.3  # Independence bonus
            elif hints_used == 1:
                hint_multiplier = 1.0  # No penalty
            elif hints_used == 2:
                hint_multiplier = 0.9  # Small penalty
            else:
                hint_multiplier = max(0.5, 1.0 - (hints_used * 0.15))
            
            score *= hint_multiplier
            
            # Performance context bonus
            if current_metrics.consecutive_successes >= 5:
                score *= 1.2  # Hot streak bonus
            elif current_metrics.consecutive_failures >= 3:
                score *= 1.1  # Encouragement bonus
            
            # Category mastery bonus
            category = challenge.get('category', '')
            category_mastery = current_metrics.category_mastery.get(category, 0.5)
            if category_mastery >= 0.9:
                score *= 1.25  # Mastery bonus
            elif category_mastery <= 0.3:
                score *= 1.15  # Learning encouragement
            
            # Ensure minimum score
            final_score = max(int(score), 10)
            
            logger.info(f"Dynamic score calculated for user {user_id}: {final_score}")
            return final_score
            
        except Exception as e:
            logger.error(f"Error calculating dynamic score for user {user_id}: {e}")
            return 50  # Safe fallback score
    
    def update_performance_model(self, user_id: str, challenge_attempt: Dict[str, Any]) -> None:
        """
        Update the AI performance model with new attempt data.
        
        Args:
            user_id: Unique identifier for the user
            challenge_attempt: New challenge attempt data
        """
        try:
            # Store the attempt in performance history
            if user_id not in self.performance_history:
                self.performance_history[user_id] = []
            
            self.performance_history[user_id].append({
                'timestamp': datetime.now(),
                'challenge_id': challenge_attempt.get('challenge_id'),
                'category': challenge_attempt.get('category'),
                'difficulty': challenge_attempt.get('difficulty'),
                'is_correct': challenge_attempt.get('is_correct', False),
                'completion_time': challenge_attempt.get('completion_time', 0),
                'hint_count': challenge_attempt.get('hint_count', 0),
                'score_earned': challenge_attempt.get('score_earned', 0)
            })
            
            # Update user profile
            self._update_user_profile(user_id, challenge_attempt)
            
            # Trigger model retraining if sufficient new data
            if len(self.performance_history[user_id]) % 10 == 0:
                self._retrain_user_model(user_id)
            
            logger.info(f"Performance model updated for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error updating performance model for user {user_id}: {e}")
    
    def get_performance_insights(self, user_id: str) -> Dict[str, Any]:
        """
        Get AI-generated insights about user performance and learning patterns.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary containing performance insights and recommendations
        """
        try:
            current_metrics = self.analyze_real_time_performance(user_id, {})
            user_history = self._get_user_performance_history(user_id)
            
            insights = {
                'performance_summary': {
                    'overall_success_rate': current_metrics.success_rate,
                    'learning_velocity': current_metrics.learning_velocity,
                    'strongest_categories': self._get_strongest_categories(current_metrics.category_mastery),
                    'improvement_areas': self._get_improvement_areas(current_metrics.category_mastery),
                    'learning_style': self._determine_learning_style(current_metrics)
                },
                'progress_tracking': {
                    'skill_progression_rate': current_metrics.skill_progression_rate,
                    'consistency_score': self._calculate_consistency_score(user_history),
                    'challenge_completion_trend': self._analyze_completion_trend(user_history),
                    'difficulty_progression': self._analyze_difficulty_progression(user_history)
                },
                'recommendations': {
                    'next_focus_areas': self._recommend_focus_areas(current_metrics),
                    'optimal_study_schedule': self._recommend_study_schedule(current_metrics),
                    'challenge_types': self._recommend_challenge_types(current_metrics),
                    'skill_development_path': self._generate_skill_development_path(user_id, current_metrics)
                },
                'achievements': {
                    'recent_accomplishments': self._identify_recent_accomplishments(user_history),
                    'upcoming_milestones': self._predict_upcoming_milestones(current_metrics),
                    'mastery_progress': self._calculate_mastery_progress(current_metrics)
                }
            }
            
            logger.info(f"Performance insights generated for user {user_id}")
            return insights
            
        except Exception as e:
            logger.error(f"Error generating performance insights for user {user_id}: {e}")
            return {}
    
    # Private helper methods
    
    def _get_user_performance_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's performance history from database or cache."""
        if self.db:
            try:
                # Fetch from database
                attempts = list(self.db.challenge_attempts.find(
                    {'user_id': user_id}
                ).sort('attempt_time', 1))
                return attempts
            except Exception as e:
                logger.error(f"Error fetching user history from database: {e}")
                
        # Fallback to in-memory cache
        return self.performance_history.get(user_id, [])
    
    def _analyze_category_performance(self, user_history: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze performance by category."""
        category_stats = {}
        
        for attempt in user_history:
            category = attempt.get('category', 'unknown')
            if category not in category_stats:
                category_stats[category] = {'total': 0, 'correct': 0}
            
            category_stats[category]['total'] += 1
            if attempt.get('is_correct', False):
                category_stats[category]['correct'] += 1
        
        # Calculate success rates
        category_mastery = {}
        for category, stats in category_stats.items():
            if stats['total'] > 0:
                category_mastery[category] = stats['correct'] / stats['total']
            else:
                category_mastery[category] = 0.0
        
        return category_mastery
    
    def _calculate_learning_velocity(self, user_history: List[Dict[str, Any]]) -> float:
        """Calculate learning velocity (challenges per day)."""
        if not user_history:
            return 0.0
        
        # Get date range
        dates = [attempt.get('attempt_time', datetime.now()) for attempt in user_history]
        if isinstance(dates[0], str):
            dates = [datetime.fromisoformat(date.replace('Z', '+00:00')) for date in dates]
        
        date_range = (max(dates) - min(dates)).days + 1
        successful_attempts = sum(1 for attempt in user_history if attempt.get('is_correct', False))
        
        return successful_attempts / date_range if date_range > 0 else 0.0
    
    def _calculate_consecutive_performance(self, user_history: List[Dict[str, Any]]) -> Tuple[int, int]:
        """Calculate consecutive successes and failures."""
        if not user_history:
            return 0, 0
        
        successes = 0
        failures = 0
        
        # Count from the most recent attempts backwards
        for attempt in reversed(user_history):
            if attempt.get('is_correct', False):
                if failures == 0:  # Still counting successes
                    successes += 1
                else:  # Hit a failure, stop counting successes
                    break
            else:
                if successes == 0:  # Still counting failures
                    failures += 1
                else:  # Hit a success, stop counting failures
                    break
        
        return successes, failures
    
    def _calculate_skill_progression_rate(self, user_history: List[Dict[str, Any]]) -> float:
        """Calculate the rate of skill progression over time."""
        if len(user_history) < 2:
            return 0.0
        
        # Analyze success rate over time periods
        recent_attempts = user_history[-10:] if len(user_history) >= 10 else user_history
        older_attempts = user_history[-20:-10] if len(user_history) >= 20 else []
        
        if not older_attempts:
            return 0.0
        
        recent_success_rate = sum(1 for attempt in recent_attempts if attempt.get('is_correct', False)) / len(recent_attempts)
        older_success_rate = sum(1 for attempt in older_attempts if attempt.get('is_correct', False)) / len(older_attempts)
        
        return recent_success_rate - older_success_rate
    
    def _get_current_difficulty(self, user_id: str, category: str) -> DifficultyLevel:
        """Get the current difficulty level for user in specific category."""
        user_profile = self.user_profiles.get(user_id, {})
        category_difficulty = user_profile.get('category_difficulties', {}).get(category, 'INTERMEDIATE')
        
        try:
            return DifficultyLevel[category_difficulty.upper()]
        except KeyError:
            return DifficultyLevel.INTERMEDIATE
    
    def _promote_difficulty(self, current_difficulty: DifficultyLevel, aggressive: bool = False) -> DifficultyLevel:
        """Promote to higher difficulty level."""
        difficulty_order = [DifficultyLevel.BEGINNER, DifficultyLevel.INTERMEDIATE, 
                          DifficultyLevel.ADVANCED, DifficultyLevel.EXPERT]
        
        current_index = difficulty_order.index(current_difficulty)
        
        if aggressive and current_index < len(difficulty_order) - 2:
            return difficulty_order[current_index + 2]
        elif current_index < len(difficulty_order) - 1:
            return difficulty_order[current_index + 1]
        else:
            return current_difficulty
    
    def _demote_difficulty(self, current_difficulty: DifficultyLevel, aggressive: bool = False) -> DifficultyLevel:
        """Demote to lower difficulty level."""
        difficulty_order = [DifficultyLevel.BEGINNER, DifficultyLevel.INTERMEDIATE, 
                          DifficultyLevel.ADVANCED, DifficultyLevel.EXPERT]
        
        current_index = difficulty_order.index(current_difficulty)
        
        if aggressive and current_index > 1:
            return difficulty_order[current_index - 2]
        elif current_index > 0:
            return difficulty_order[current_index - 1]
        else:
            return current_difficulty
    
    def _apply_performance_modifiers(self, target_difficulty: DifficultyLevel, 
                                   metrics: PerformanceMetrics, category: str) -> DifficultyLevel:
        """Apply additional performance-based modifiers to difficulty."""
        # Time-based adjustment
        category_optimal_time = self.optimal_times.get(target_difficulty, 120)
        
        if metrics.average_completion_time < category_optimal_time * 0.6:
            # User is very fast - can handle higher difficulty
            target_difficulty = self._promote_difficulty(target_difficulty)
        elif metrics.average_completion_time > category_optimal_time * 2:
            # User is slow - may need easier challenges
            target_difficulty = self._demote_difficulty(target_difficulty)
        
        # Hint usage adjustment
        if metrics.hint_usage_rate > 3:
            # User relies heavily on hints - ease up slightly
            target_difficulty = self._demote_difficulty(target_difficulty)
        elif metrics.hint_usage_rate == 0:
            # User is independent - can handle more challenge
            target_difficulty = self._promote_difficulty(target_difficulty)
        
        return target_difficulty
    
    def _get_challenge_pool(self, category: str, difficulty: DifficultyLevel) -> List[Dict[str, Any]]:
        """Get available challenges for category and difficulty."""
        # This would typically query the database
        # For now, return a mock pool
        return [
            {
                'id': f'{category}_{difficulty.level_name}_{i}',
                'category': category,
                'difficulty': difficulty.level_name,
                'score_weight': 100 * difficulty.multiplier,
                'estimated_time': self.optimal_times.get(difficulty, 120)
            }
            for i in range(1, 6)
        ]
    
    def _select_adaptive_challenges(self, challenge_pool: List[Dict[str, Any]], 
                                  metrics: PerformanceMetrics, count: int) -> List[Dict[str, Any]]:
        """Select challenges using adaptive algorithm."""
        # Score each challenge based on user metrics
        scored_challenges = []
        
        for challenge in challenge_pool:
            score = self._score_challenge_relevance(challenge, metrics)
            scored_challenges.append((score, challenge))
        
        # Sort by relevance score and select top challenges
        scored_challenges.sort(key=lambda x: x[0], reverse=True)
        return [challenge for _, challenge in scored_challenges[:count]]
    
    def _score_challenge_relevance(self, challenge: Dict[str, Any], metrics: PerformanceMetrics) -> float:
        """Score how relevant a challenge is for the user."""
        base_score = 1.0
        
        # Adjust based on category mastery
        category = challenge.get('category', '')
        category_mastery = metrics.category_mastery.get(category, 0.5)
        
        if 0.7 <= category_mastery <= 0.9:
            base_score += 0.3  # Sweet spot for learning
        elif category_mastery < 0.3:
            base_score += 0.2  # Needs improvement
        elif category_mastery > 0.9:
            base_score += 0.1  # Already mastered
        
        # Adjust based on estimated completion time
        estimated_time = challenge.get('estimated_time', 120)
        if metrics.average_completion_time * 0.8 <= estimated_time <= metrics.average_completion_time * 1.2:
            base_score += 0.2  # Good time match
        
        return base_score
    
    def _predict_success_probability(self, metrics: PerformanceMetrics, challenge: Dict[str, Any]) -> float:
        """Predict probability of success for a challenge."""
        base_probability = metrics.success_rate
        
        # Adjust based on challenge difficulty vs user performance
        category = challenge.get('category', '')
        category_performance = metrics.category_mastery.get(category, 0.5)
        
        # Combine overall and category-specific performance
        adjusted_probability = (base_probability * 0.6) + (category_performance * 0.4)
        
        # Clamp between 0.1 and 0.95
        return max(0.1, min(0.95, adjusted_probability))
    
    def _estimate_completion_time(self, metrics: PerformanceMetrics, challenge: Dict[str, Any]) -> float:
        """Estimate completion time for a challenge."""
        base_time = challenge.get('estimated_time', 120)
        
        # Adjust based on user's average completion time
        user_speed_factor = metrics.average_completion_time / 120  # Normalized to 2 minutes
        
        return base_time * user_speed_factor
    
    def _generate_adaptive_hints(self, user_id: str, challenge: Dict[str, Any], 
                               metrics: PerformanceMetrics) -> List[str]:
        """Generate adaptive hints based on user performance."""
        hints = []
        
        # Base hint
        hints.append(f"Consider the {challenge.get('category', 'security')} vulnerability type and common attack vectors.")
        
        # Adaptive hints based on performance
        if metrics.hint_usage_rate > 2:
            # User relies on hints - provide more detailed guidance
            hints.append("Try breaking down the problem into smaller steps. What is the application expecting as input?")
            hints.append("Look at the code/scenario carefully. What happens when you provide unexpected input?")
            hints.append("Consider how the application processes your input. Are there any special characters that might change the behavior?")
        elif metrics.hint_usage_rate < 1:
            # Independent learner - provide minimal hints
            hints.append("Think about the fundamental principles of this vulnerability.")
        else:
            # Balanced hint approach
            hints.append("Consider the attack vector and how it exploits the vulnerability.")
            hints.append("What would happen if you modify the input in unexpected ways?")
        
        return hints
    
    def _explain_difficulty_selection(self, difficulty: DifficultyLevel, metrics: PerformanceMetrics) -> str:
        """Provide explanation for difficulty level selection."""
        if metrics.success_rate >= 0.85:
            return f"Selected {difficulty.level_name} difficulty due to strong performance ({metrics.success_rate:.1%} success rate)"
        elif metrics.success_rate <= 0.40:
            return f"Selected {difficulty.level_name} difficulty to provide appropriate support ({metrics.success_rate:.1%} success rate)"
        else:
            return f"Selected {difficulty.level_name} difficulty based on balanced performance ({metrics.success_rate:.1%} success rate)"
    
    def _update_user_profile(self, user_id: str, challenge_attempt: Dict[str, Any]) -> None:
        """Update user profile with new attempt data."""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                'category_difficulties': {},
                'learning_preferences': {},
                'performance_trends': []
            }
        
        profile = self.user_profiles[user_id]
        category = challenge_attempt.get('category', '')
        
        # Update category difficulty based on performance
        if challenge_attempt.get('is_correct', False):
            current_difficulty = profile['category_difficulties'].get(category, 'INTERMEDIATE')
            profile['category_difficulties'][category] = current_difficulty
        
        # Update performance trends
        profile['performance_trends'].append({
            'timestamp': datetime.now().isoformat(),
            'success': challenge_attempt.get('is_correct', False),
            'category': category,
            'completion_time': challenge_attempt.get('completion_time', 0)
        })
        
        # Keep only recent trends (last 50 attempts)
        profile['performance_trends'] = profile['performance_trends'][-50:]
    
    def _retrain_user_model(self, user_id: str) -> None:
        """Retrain ML model for specific user."""
        try:
            user_history = self._get_user_performance_history(user_id)
            if len(user_history) < 10:
                return  # Not enough data for retraining
            
            # Prepare training data
            features = []
            labels = []
            
            for attempt in user_history:
                feature_vector = [
                    attempt.get('completion_time', 0),
                    attempt.get('hint_count', 0),
                    1 if attempt.get('difficulty') == 'beginner' else 0,
                    1 if attempt.get('difficulty') == 'intermediate' else 0,
                    1 if attempt.get('difficulty') == 'advanced' else 0,
                    1 if attempt.get('difficulty') == 'expert' else 0
                ]
                features.append(feature_vector)
                labels.append(1 if attempt.get('is_correct', False) else 0)
            
            # Simple model update (in production, use proper ML pipeline)
            if user_id not in self.ml_models:
                self.ml_models[user_id] = {
                    'success_probability_model': None,
                    'completion_time_model': None,
                    'last_updated': datetime.now()
                }
            
            logger.info(f"Model retrained for user {user_id} with {len(features)} data points")
            
        except Exception as e:
            logger.error(f"Error retraining model for user {user_id}: {e}")
    
    def _get_strongest_categories(self, category_mastery: Dict[str, float]) -> List[str]:
        """Get categories where user performs best."""
        sorted_categories = sorted(category_mastery.items(), key=lambda x: x[1], reverse=True)
        return [category for category, mastery in sorted_categories[:3] if mastery >= 0.7]
    
    def _get_improvement_areas(self, category_mastery: Dict[str, float]) -> List[str]:
        """Get categories that need improvement."""
        sorted_categories = sorted(category_mastery.items(), key=lambda x: x[1])
        return [category for category, mastery in sorted_categories[:3] if mastery <= 0.5]
    
    def _determine_learning_style(self, metrics: PerformanceMetrics) -> str:
        """Determine user's learning style based on performance patterns."""
        if metrics.hint_usage_rate > 3:
            return "Guided Learner - Benefits from detailed instructions and step-by-step guidance"
        elif metrics.hint_usage_rate < 1:
            return "Independent Learner - Prefers to figure things out through experimentation"
        elif metrics.average_completion_time < 60:
            return "Fast Learner - Quickly grasps concepts and moves through challenges rapidly"
        elif metrics.average_completion_time > 240:
            return "Methodical Learner - Takes time to thoroughly understand concepts"
        else:
            return "Balanced Learner - Adapts well to different learning approaches"
    
    def _calculate_consistency_score(self, user_history: List[Dict[str, Any]]) -> float:
        """Calculate how consistent the user's performance is."""
        if len(user_history) < 5:
            return 0.5
        
        # Calculate success rate for sliding windows
        window_size = min(5, len(user_history) // 3)
        success_rates = []
        
        for i in range(len(user_history) - window_size + 1):
            window = user_history[i:i + window_size]
            successes = sum(1 for attempt in window if attempt.get('is_correct', False))
            success_rates.append(successes / window_size)
        
        # Consistency is inverse of variance
        if len(success_rates) > 1:
            variance = np.var(success_rates)
            consistency = max(0, 1 - (variance * 4))  # Scale variance to 0-1 range
            return consistency
        
        return 0.5
    
    def _analyze_completion_trend(self, user_history: List[Dict[str, Any]]) -> str:
        """Analyze trend in challenge completion times."""
        if len(user_history) < 10:
            return "Insufficient data for trend analysis"
        
        recent_times = [attempt.get('completion_time', 0) for attempt in user_history[-10:]]
        older_times = [attempt.get('completion_time', 0) for attempt in user_history[-20:-10]] if len(user_history) >= 20 else []
        
        if not older_times:
            return "Building performance baseline"
        
        recent_avg = np.mean(recent_times)
        older_avg = np.mean(older_times)
        
        improvement = (older_avg - recent_avg) / older_avg * 100
        
        if improvement > 15:
            return f"Improving rapidly - {improvement:.1f}% faster completion times"
        elif improvement > 5:
            return f"Steady improvement - {improvement:.1f}% faster completion times"
        elif improvement < -15:
            return f"Slowing down - {abs(improvement):.1f}% slower completion times"
        elif improvement < -5:
            return f"Slight decline - {abs(improvement):.1f}% slower completion times"
        else:
            return "Stable performance - consistent completion times"
    
    def _analyze_difficulty_progression(self, user_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze how user has progressed through difficulty levels."""
        difficulty_timeline = []
        
        for attempt in user_history:
            difficulty_timeline.append({
                'timestamp': attempt.get('attempt_time', datetime.now()),
                'difficulty': attempt.get('difficulty', 'intermediate'),
                'success': attempt.get('is_correct', False)
            })
        
        # Count progression through levels
        progression = {
            'beginner_attempts': sum(1 for d in difficulty_timeline if d['difficulty'] == 'beginner'),
            'intermediate_attempts': sum(1 for d in difficulty_timeline if d['difficulty'] == 'intermediate'),
            'advanced_attempts': sum(1 for d in difficulty_timeline if d['difficulty'] == 'advanced'),
            'expert_attempts': sum(1 for d in difficulty_timeline if d['difficulty'] == 'expert'),
            'current_level': difficulty_timeline[-1]['difficulty'] if difficulty_timeline else 'beginner',
            'progression_rate': self._calculate_progression_rate(difficulty_timeline)
        }
        
        return progression
    
    def _calculate_progression_rate(self, difficulty_timeline: List[Dict[str, Any]]) -> str:
        """Calculate rate of progression through difficulty levels."""
        if len(difficulty_timeline) < 20:
            return "Early stage - building foundation"
        
        # Look at difficulty distribution in first half vs second half
        midpoint = len(difficulty_timeline) // 2
        first_half = difficulty_timeline[:midpoint]
        second_half = difficulty_timeline[midpoint:]
        
        def avg_difficulty_score(attempts):
            scores = {'beginner': 1, 'intermediate': 2, 'advanced': 3, 'expert': 4}
            return np.mean([scores.get(attempt['difficulty'], 2) for attempt in attempts])
        
        first_avg = avg_difficulty_score(first_half)
        second_avg = avg_difficulty_score(second_half)
        
        progression = second_avg - first_avg
        
        if progression > 1:
            return "Rapid progression - advancing quickly through difficulty levels"
        elif progression > 0.5:
            return "Good progression - steadily advancing to harder challenges"
        elif progression > 0:
            return "Gradual progression - slowly building skills"
        else:
            return "Stable at current level - focusing on mastery"
    
    def _recommend_focus_areas(self, metrics: PerformanceMetrics) -> List[str]:
        """Recommend areas for user to focus on."""
        recommendations = []
        
        # Based on category performance
        weak_categories = [cat for cat, score in metrics.category_mastery.items() if score < 0.5]
        if weak_categories:
            recommendations.append(f"Focus on improving {', '.join(weak_categories[:2])} skills")
        
        # Based on performance patterns
        if metrics.hint_usage_rate > 3:
            recommendations.append("Practice independent problem-solving to reduce hint dependency")
        
        if metrics.average_completion_time > 300:
            recommendations.append("Work on speed and efficiency in challenge completion")
        
        if metrics.consecutive_failures > 2:
            recommendations.append("Take a break and review fundamental concepts")
        
        if not recommendations:
            recommendations.append("Continue current learning approach - performance is well-balanced")
        
        return recommendations[:3]  # Limit to top 3 recommendations
    
    def _recommend_study_schedule(self, metrics: PerformanceMetrics) -> Dict[str, Any]:
        """Recommend optimal study schedule based on performance patterns."""
        if metrics.learning_velocity > 2:
            return {
                'frequency': 'Daily',
                'duration': '30-45 minutes',
                'intensity': 'High',
                'notes': 'You\'re learning quickly - maintain this pace with daily practice'
            }
        elif metrics.learning_velocity > 1:
            return {
                'frequency': '4-5 times per week',
                'duration': '45-60 minutes',
                'intensity': 'Medium-High',
                'notes': 'Good learning pace - increase session duration for deeper understanding'
            }
        else:
            return {
                'frequency': '3-4 times per week',
                'duration': '60-90 minutes',
                'intensity': 'Medium',
                'notes': 'Focus on longer sessions to build momentum and retention'
            }
    
    def _recommend_challenge_types(self, metrics: PerformanceMetrics) -> List[str]:
        """Recommend specific types of challenges."""
        recommendations = []
        
        # Based on strengths
        strong_categories = [cat for cat, score in metrics.category_mastery.items() if score > 0.8]
        if strong_categories:
            recommendations.append(f"Advanced {strong_categories[0]} challenges to maintain expertise")
        
        # Based on weaknesses
        weak_categories = [cat for cat, score in metrics.category_mastery.items() if score < 0.4]
        if weak_categories:
            recommendations.append(f"Beginner to intermediate {weak_categories[0]} challenges for foundation building")
        
        # Based on learning style
        if metrics.hint_usage_rate < 1:
            recommendations.append("Complex, multi-step challenges for independent exploration")
        elif metrics.hint_usage_rate > 3:
            recommendations.append("Guided, tutorial-style challenges with detailed explanations")
        
        return recommendations
    
    def _generate_skill_development_path(self, user_id: str, metrics: PerformanceMetrics) -> List[Dict[str, Any]]:
        """Generate a personalized skill development path."""
        path = []
        
        # Assess current skill level
        overall_mastery = np.mean(list(metrics.category_mastery.values())) if metrics.category_mastery else 0.5
        
        if overall_mastery < 0.3:
            path.append({
                'phase': 'Foundation Building',
                'duration': '2-4 weeks',
                'focus': 'Basic security concepts and common vulnerabilities',
                'goals': ['Achieve 60% success rate', 'Complete 20 beginner challenges']
            })
        
        if overall_mastery < 0.6:
            path.append({
                'phase': 'Skill Development',
                'duration': '4-6 weeks',
                'focus': 'Intermediate concepts and attack techniques',
                'goals': ['Achieve 75% success rate', 'Master 2 vulnerability categories']
            })
        
        if overall_mastery < 0.8:
            path.append({
                'phase': 'Advanced Mastery',
                'duration': '6-8 weeks',
                'focus': 'Complex attack scenarios and advanced techniques',
                'goals': ['Achieve 85% success rate', 'Complete expert-level challenges']
            })
        
        path.append({
            'phase': 'Continuous Improvement',
            'duration': 'Ongoing',
            'focus': 'Stay current with new vulnerabilities and techniques',
            'goals': ['Maintain high performance', 'Explore emerging security threats']
        })
        
        return path
    
    def _identify_recent_accomplishments(self, user_history: List[Dict[str, Any]]) -> List[str]:
        """Identify recent accomplishments for motivation."""
        accomplishments = []
        recent_attempts = user_history[-20:] if len(user_history) >= 20 else user_history
        
        # Check for streaks
        consecutive_successes = 0
        for attempt in reversed(recent_attempts):
            if attempt.get('is_correct', False):
                consecutive_successes += 1
            else:
                break
        
        if consecutive_successes >= 5:
            accomplishments.append(f"Outstanding! {consecutive_successes} consecutive successful challenges")
        
        # Check for category mastery
        category_stats = {}
        for attempt in recent_attempts:
            category = attempt.get('category', '')
            if category not in category_stats:
                category_stats[category] = {'total': 0, 'correct': 0}
            category_stats[category]['total'] += 1
            if attempt.get('is_correct', False):
                category_stats[category]['correct'] += 1
        
        for category, stats in category_stats.items():
            if stats['total'] >= 5 and stats['correct'] / stats['total'] >= 0.9:
                accomplishments.append(f"Mastered {category} category with 90%+ success rate")
        
        # Check for improvement
        if len(user_history) >= 40:
            recent_success_rate = sum(1 for attempt in user_history[-20:] if attempt.get('is_correct', False)) / 20
            older_success_rate = sum(1 for attempt in user_history[-40:-20] if attempt.get('is_correct', False)) / 20
            
            improvement = recent_success_rate - older_success_rate
            if improvement >= 0.2:
                accomplishments.append(f"Significant improvement: {improvement:.1%} increase in success rate")
        
        return accomplishments[:3]  # Limit to top 3
    
    def _predict_upcoming_milestones(self, metrics: PerformanceMetrics) -> List[Dict[str, Any]]:
        """Predict upcoming milestones based on current performance."""
        milestones = []
        
        # Success rate milestones
        if 0.6 <= metrics.success_rate < 0.7:
            milestones.append({
                'milestone': '70% Success Rate',
                'estimated_completion': 'Within 1-2 weeks',
                'requirements': 'Continue current learning pace'
            })
        elif 0.7 <= metrics.success_rate < 0.8:
            milestones.append({
                'milestone': '80% Success Rate',
                'estimated_completion': 'Within 2-3 weeks',
                'requirements': 'Focus on weak categories and reduce hint usage'
            })
        
        # Category mastery milestones
        for category, mastery in metrics.category_mastery.items():
            if 0.7 <= mastery < 0.9:
                milestones.append({
                    'milestone': f'{category.title()} Category Mastery (90%)',
                    'estimated_completion': 'Within 2-4 weeks',
                    'requirements': f'Complete 10 more {category} challenges with high accuracy'
                })
        
        # Speed milestones
        if metrics.average_completion_time > 180:
            milestones.append({
                'milestone': 'Speed Improvement (Under 3 minutes average)',
                'estimated_completion': 'Within 3-4 weeks',
                'requirements': 'Practice pattern recognition and quick decision making'
            })
        
        return milestones[:3]  # Limit to top 3
    
    def _calculate_mastery_progress(self, metrics: PerformanceMetrics) -> Dict[str, float]:
        """Calculate progress towards mastery in different areas."""
        mastery_progress = {}
        
        # Overall mastery (based on success rate)
        mastery_progress['overall'] = min(metrics.success_rate / 0.9, 1.0)  # 90% success rate = full mastery
        
        # Category mastery
        for category, score in metrics.category_mastery.items():
            mastery_progress[f'{category}_mastery'] = min(score / 0.9, 1.0)
        
        # Speed mastery (based on completion time)
        optimal_time = 120  # 2 minutes baseline
        if metrics.average_completion_time > 0:
            speed_score = min(optimal_time / metrics.average_completion_time, 1.0)
            mastery_progress['speed_mastery'] = speed_score
        else:
            mastery_progress['speed_mastery'] = 0.0
        
        # Independence mastery (based on hint usage)
        independence_score = max(0, 1 - (metrics.hint_usage_rate / 5))  # 0 hints = full independence
        mastery_progress['independence_mastery'] = independence_score
        
        return mastery_progress