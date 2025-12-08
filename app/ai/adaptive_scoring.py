"""
Adaptive Scoring Algorithm with User Performance Tracking
Production-ready implementation for SecureTrainer

This module implements dynamic scoring that:
1. Adapts to user skill level and performance history
2. Provides real-time score calculations based on multiple factors
3. Tracks performance trends for AI-driven insights
4. Implements fair scoring across different difficulty levels
5. Supports comparative analytics and leaderboards
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import logging
import json
from collections import defaultdict
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class ScoringFactors:
    """Data class for scoring factors."""
    base_score: int
    difficulty_multiplier: float
    time_multiplier: float
    hint_multiplier: float
    attempt_multiplier: float
    streak_multiplier: float
    category_mastery_multiplier: float
    learning_velocity_multiplier: float
    user_level_multiplier: float

@dataclass
class PerformanceSnapshot:
    """Snapshot of user performance at a point in time."""
    user_id: str
    timestamp: datetime
    overall_success_rate: float
    category_success_rates: Dict[str, float]
    average_completion_time: float
    hint_usage_average: float
    current_streak: int
    level: int
    total_score: int
    learning_velocity: float
    recent_improvement: float

@dataclass
class ScoreBreakdown:
    """Detailed breakdown of score calculation."""
    base_score: int
    factors: ScoringFactors
    final_score: int
    explanation: List[str]
    performance_impact: Dict[str, float]

class AdaptiveScoringEngine:
    """
    Production adaptive scoring engine for SecureTrainer.
    
    Provides sophisticated scoring that adapts to user performance:
    - Dynamic difficulty-based multipliers
    - Performance-aware bonus/penalty system
    - Real-time trend analysis
    - Fair scoring across skill levels
    """
    
    def __init__(self, db_connection=None):
        """Initialize the adaptive scoring engine."""
        self.db = db_connection
        self.user_performance_cache = {}
        self.scoring_config = self._load_scoring_config()
        self.performance_tracker = PerformanceTracker(db_connection)
        
        logger.info("Adaptive Scoring Engine initialized successfully")
    
    def calculate_adaptive_score(self, user_id: str, challenge: Dict[str, Any], 
                               attempt_data: Dict[str, Any]) -> Tuple[int, ScoreBreakdown]:
        """
        Calculate adaptive score based on user performance and challenge data.
        
        Args:
            user_id: Unique identifier for the user
            challenge: Challenge data including difficulty and category
            attempt_data: Data from the challenge attempt
            
        Returns:
            Tuple of (final_score, detailed_breakdown)
        """
        try:
            # Get user performance context
            user_performance = self.performance_tracker.get_current_performance(user_id)
            
            # Calculate base scoring factors
            factors = self._calculate_scoring_factors(
                user_performance, challenge, attempt_data
            )
            
            # Apply scoring formula
            final_score = self._apply_scoring_formula(factors)
            
            # Create detailed breakdown
            breakdown = self._create_score_breakdown(factors, final_score, user_performance)
            
            # Update performance tracking
            self.performance_tracker.record_attempt(user_id, challenge, attempt_data, final_score)
            
            logger.info(f"Adaptive score calculated for user {user_id}: {final_score}")
            return final_score, breakdown
            
        except Exception as e:
            logger.error(f"Error calculating adaptive score for user {user_id}: {e}")
            # Return basic score as fallback
            base_score = challenge.get('score_weight', 100)
            return base_score, self._create_fallback_breakdown(base_score)
    
    def get_user_scoring_insights(self, user_id: str) -> Dict[str, Any]:
        """
        Get detailed insights about user's scoring patterns and potential.
        
        Args:
            user_id: Unique identifier for the user
            
        Returns:
            Dictionary containing scoring insights and recommendations
        """
        try:
            performance = self.performance_tracker.get_current_performance(user_id)
            history = self.performance_tracker.get_performance_history(user_id)
            
            insights = {
                'current_performance': {
                    'success_rate': performance.overall_success_rate,
                    'average_score_per_challenge': self._calculate_average_score(history),
                    'scoring_efficiency': self._calculate_scoring_efficiency(history),
                    'performance_trend': self._analyze_performance_trend(history)
                },
                'scoring_potential': {
                    'maximum_possible_score': self._calculate_max_potential_score(performance),
                    'improvement_opportunities': self._identify_improvement_areas(performance),
                    'optimal_challenge_types': self._recommend_optimal_challenges(performance),
                    'projected_score_increase': self._project_score_increase(performance, history)
                },
                'comparative_analysis': {
                    'percentile_ranking': self._calculate_percentile_ranking(user_id),
                    'category_rankings': self._calculate_category_rankings(user_id),
                    'peer_comparison': self._compare_with_peers(user_id)
                },
                'recommendations': {
                    'focus_areas': self._recommend_focus_areas(performance),
                    'optimal_session_length': self._recommend_session_length(performance),
                    'difficulty_progression': self._recommend_difficulty_progression(performance)
                }
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating scoring insights for user {user_id}: {e}")
            return {}
    
    def calculate_leaderboard_scores(self, time_period: str = 'all_time') -> List[Dict[str, Any]]:
        """
        Calculate leaderboard scores with fair ranking across different skill levels.
        
        Args:
            time_period: Time period for leaderboard ('all_time', 'monthly', 'weekly')
            
        Returns:
            List of user rankings with normalized scores
        """
        try:
            # Get all user performances
            all_performances = self.performance_tracker.get_all_user_performances(time_period)
            
            leaderboard = []
            for user_id, performance in all_performances.items():
                # Calculate normalized score for fair comparison
                normalized_score = self._calculate_normalized_score(performance)
                
                # Calculate ranking factors
                ranking_data = {
                    'user_id': user_id,
                    'username': performance.get('username', f'User_{user_id[:8]}'),
                    'total_score': performance.get('total_score', 0),
                    'normalized_score': normalized_score,
                    'success_rate': performance.get('overall_success_rate', 0),
                    'challenges_completed': performance.get('challenges_completed', 0),
                    'average_completion_time': performance.get('average_completion_time', 0),
                    'learning_velocity': performance.get('learning_velocity', 0),
                    'current_streak': performance.get('current_streak', 0),
                    'level': performance.get('level', 1),
                    'category_mastery': performance.get('category_success_rates', {}),
                    'recent_activity': performance.get('last_activity', None)
                }
                
                leaderboard.append(ranking_data)
            
            # Sort by normalized score (fair ranking)
            leaderboard.sort(key=lambda x: x['normalized_score'], reverse=True)
            
            # Add ranking positions
            for i, user_data in enumerate(leaderboard):
                user_data['rank'] = i + 1
                user_data['rank_change'] = self._calculate_rank_change(user_data['user_id'])
            
            logger.info(f"Leaderboard calculated for {len(leaderboard)} users")
            return leaderboard
            
        except Exception as e:
            logger.error(f"Error calculating leaderboard scores: {e}")
            return []
    
    def _calculate_scoring_factors(self, user_performance: PerformanceSnapshot, 
                                 challenge: Dict[str, Any], 
                                 attempt_data: Dict[str, Any]) -> ScoringFactors:
        """Calculate all scoring factors for the attempt."""
        
        # Base score from challenge
        base_score = challenge.get('score_weight', 100)
        
        # Difficulty multiplier
        difficulty_multipliers = {
            'beginner': 1.0,
            'intermediate': 1.5,
            'advanced': 2.2,
            'expert': 3.0
        }
        difficulty = challenge.get('difficulty', 'intermediate').lower()
        difficulty_multiplier = difficulty_multipliers.get(difficulty, 1.5)
        
        # Time-based multiplier
        completion_time = attempt_data.get('completion_time', 0)
        time_multiplier = self._calculate_time_multiplier(completion_time, difficulty)
        
        # Hint usage multiplier
        hints_used = attempt_data.get('hint_count', 0)
        hint_multiplier = self._calculate_hint_multiplier(hints_used)
        
        # Attempt count multiplier
        attempt_count = attempt_data.get('attempt_number', 1)
        attempt_multiplier = self._calculate_attempt_multiplier(attempt_count)
        
        # Streak multiplier
        streak_multiplier = self._calculate_streak_multiplier(user_performance.current_streak)
        
        # Category mastery multiplier
        category = challenge.get('category', '').lower()
        category_mastery = user_performance.category_success_rates.get(category, 0.5)
        category_mastery_multiplier = self._calculate_mastery_multiplier(category_mastery)
        
        # Learning velocity multiplier
        learning_velocity_multiplier = self._calculate_velocity_multiplier(user_performance.learning_velocity)
        
        # User level multiplier
        user_level_multiplier = self._calculate_level_multiplier(user_performance.level)
        
        return ScoringFactors(
            base_score=base_score,
            difficulty_multiplier=difficulty_multiplier,
            time_multiplier=time_multiplier,
            hint_multiplier=hint_multiplier,
            attempt_multiplier=attempt_multiplier,
            streak_multiplier=streak_multiplier,
            category_mastery_multiplier=category_mastery_multiplier,
            learning_velocity_multiplier=learning_velocity_multiplier,
            user_level_multiplier=user_level_multiplier
        )
    
    def _apply_scoring_formula(self, factors: ScoringFactors) -> int:
        """Apply the comprehensive scoring formula."""
        
        # Core score calculation
        core_score = factors.base_score * factors.difficulty_multiplier
        
        # Apply performance multipliers
        performance_score = core_score * (
            factors.time_multiplier *
            factors.hint_multiplier *
            factors.attempt_multiplier
        )
        
        # Apply context multipliers
        context_score = performance_score * (
            factors.streak_multiplier *
            factors.category_mastery_multiplier *
            factors.learning_velocity_multiplier *
            factors.user_level_multiplier
        )
        
        # Ensure minimum score
        final_score = max(int(context_score), 10)
        
        # Apply score ceiling based on challenge difficulty
        max_scores = {
            1.0: 500,    # beginner
            1.5: 1000,   # intermediate
            2.2: 2000,   # advanced
            3.0: 5000    # expert
        }
        score_ceiling = max_scores.get(factors.difficulty_multiplier, 1000)
        final_score = min(final_score, score_ceiling)
        
        return final_score
    
    def _calculate_time_multiplier(self, completion_time: float, difficulty: str) -> float:
        """Calculate time-based score multiplier."""
        optimal_times = {
            'beginner': 60,      # 1 minute
            'intermediate': 120,  # 2 minutes
            'advanced': 240,     # 4 minutes
            'expert': 480        # 8 minutes
        }
        
        optimal_time = optimal_times.get(difficulty, 120)
        
        if completion_time <= 0:
            return 1.0
        elif completion_time <= optimal_time * 0.5:
            return 2.0  # Lightning fast bonus
        elif completion_time <= optimal_time:
            return 1.5  # Fast completion bonus
        elif completion_time <= optimal_time * 2:
            return 1.0  # Normal completion
        elif completion_time <= optimal_time * 3:
            return 0.8  # Slow penalty
        else:
            return 0.6  # Very slow penalty
    
    def _calculate_hint_multiplier(self, hints_used: int) -> float:
        """Calculate hint usage penalty/bonus multiplier."""
        if hints_used == 0:
            return 1.3  # Independence bonus
        elif hints_used == 1:
            return 1.0  # No penalty
        elif hints_used == 2:
            return 0.9  # Small penalty
        else:
            return max(0.5, 1.0 - (hints_used * 0.15))  # Progressive penalty
    
    def _calculate_attempt_multiplier(self, attempt_count: int) -> float:
        """Calculate attempt count multiplier."""
        if attempt_count == 1:
            return 1.3  # First try bonus
        elif attempt_count == 2:
            return 1.0  # No penalty
        else:
            return max(0.3, 1.0 - (attempt_count - 2) * 0.2)  # Progressive penalty
    
    def _calculate_streak_multiplier(self, current_streak: int) -> float:
        """Calculate streak bonus multiplier."""
        if current_streak >= 10:
            return 1.5  # Hot streak bonus
        elif current_streak >= 5:
            return 1.3  # Good streak bonus
        elif current_streak >= 3:
            return 1.1  # Small streak bonus
        else:
            return 1.0  # No bonus
    
    def _calculate_mastery_multiplier(self, category_mastery: float) -> float:
        """Calculate category mastery multiplier."""
        if category_mastery >= 0.9:
            return 1.2  # Mastery bonus
        elif category_mastery >= 0.7:
            return 1.1  # Proficiency bonus
        elif category_mastery <= 0.3:
            return 1.15  # Learning encouragement bonus
        else:
            return 1.0  # Standard multiplier
    
    def _calculate_velocity_multiplier(self, learning_velocity: float) -> float:
        """Calculate learning velocity multiplier."""
        if learning_velocity >= 3.0:
            return 1.2  # High velocity bonus
        elif learning_velocity >= 1.5:
            return 1.1  # Good velocity bonus
        elif learning_velocity <= 0.5:
            return 1.05  # Encouragement for slow learners
        else:
            return 1.0  # Standard multiplier
    
    def _calculate_level_multiplier(self, user_level: int) -> float:
        """Calculate user level progression multiplier."""
        # Slight bonus for higher levels to encourage progression
        return 1.0 + (user_level * 0.02)  # 2% per level, max 20% at level 10
    
    def _create_score_breakdown(self, factors: ScoringFactors, final_score: int, 
                              performance: PerformanceSnapshot) -> ScoreBreakdown:
        """Create detailed score breakdown with explanations."""
        
        explanations = []
        performance_impact = {}
        
        # Base score explanation
        explanations.append(f"Base score: {factors.base_score}")
        
        # Difficulty impact
        if factors.difficulty_multiplier > 1.0:
            explanations.append(f"Difficulty bonus: +{(factors.difficulty_multiplier - 1.0) * 100:.0f}%")
            performance_impact['difficulty'] = factors.difficulty_multiplier - 1.0
        
        # Time impact
        if factors.time_multiplier > 1.0:
            explanations.append(f"Speed bonus: +{(factors.time_multiplier - 1.0) * 100:.0f}%")
            performance_impact['speed'] = factors.time_multiplier - 1.0
        elif factors.time_multiplier < 1.0:
            explanations.append(f"Time penalty: -{(1.0 - factors.time_multiplier) * 100:.0f}%")
            performance_impact['speed'] = factors.time_multiplier - 1.0
        
        # Hint impact
        if factors.hint_multiplier > 1.0:
            explanations.append(f"Independence bonus: +{(factors.hint_multiplier - 1.0) * 100:.0f}%")
            performance_impact['independence'] = factors.hint_multiplier - 1.0
        elif factors.hint_multiplier < 1.0:
            explanations.append(f"Hint penalty: -{(1.0 - factors.hint_multiplier) * 100:.0f}%")
            performance_impact['independence'] = factors.hint_multiplier - 1.0
        
        # Streak impact
        if factors.streak_multiplier > 1.0:
            explanations.append(f"Streak bonus: +{(factors.streak_multiplier - 1.0) * 100:.0f}%")
            performance_impact['streak'] = factors.streak_multiplier - 1.0
        
        # Category mastery impact
        if factors.category_mastery_multiplier > 1.0:
            explanations.append(f"Category mastery bonus: +{(factors.category_mastery_multiplier - 1.0) * 100:.0f}%")
            performance_impact['mastery'] = factors.category_mastery_multiplier - 1.0
        
        # Learning velocity impact
        if factors.learning_velocity_multiplier > 1.0:
            explanations.append(f"Learning velocity bonus: +{(factors.learning_velocity_multiplier - 1.0) * 100:.0f}%")
            performance_impact['velocity'] = factors.learning_velocity_multiplier - 1.0
        
        return ScoreBreakdown(
            base_score=factors.base_score,
            factors=factors,
            final_score=final_score,
            explanation=explanations,
            performance_impact=performance_impact
        )
    
    def _create_fallback_breakdown(self, base_score: int) -> ScoreBreakdown:
        """Create fallback breakdown for error cases."""
        return ScoreBreakdown(
            base_score=base_score,
            factors=ScoringFactors(
                base_score=base_score,
                difficulty_multiplier=1.0,
                time_multiplier=1.0,
                hint_multiplier=1.0,
                attempt_multiplier=1.0,
                streak_multiplier=1.0,
                category_mastery_multiplier=1.0,
                learning_velocity_multiplier=1.0,
                user_level_multiplier=1.0
            ),
            final_score=base_score,
            explanation=[f"Basic score: {base_score} (fallback calculation)"],
            performance_impact={}
        )
    
    def _load_scoring_config(self) -> Dict[str, Any]:
        """Load scoring configuration."""
        return {
            'difficulty_multipliers': {
                'beginner': 1.0,
                'intermediate': 1.5,
                'advanced': 2.2,
                'expert': 3.0
            },
            'time_thresholds': {
                'beginner': 60,
                'intermediate': 120,
                'advanced': 240,
                'expert': 480
            },
            'bonus_caps': {
                'streak_max': 1.5,
                'speed_max': 2.0,
                'independence_max': 1.3
            },
            'penalty_floors': {
                'hint_min': 0.5,
                'time_min': 0.6,
                'attempt_min': 0.3
            }
        }
    
    # Additional helper methods for insights and analytics
    def _calculate_average_score(self, history: List[Dict[str, Any]]) -> float:
        """Calculate average score per challenge."""
        if not history:
            return 0.0
        
        scores = [attempt.get('score_earned', 0) for attempt in history]
        return sum(scores) / len(scores)
    
    def _calculate_scoring_efficiency(self, history: List[Dict[str, Any]]) -> float:
        """Calculate scoring efficiency (actual vs potential scores)."""
        if not history:
            return 0.0
        
        total_actual = sum(attempt.get('score_earned', 0) for attempt in history)
        total_potential = sum(attempt.get('max_possible_score', 100) for attempt in history)
        
        return (total_actual / total_potential) if total_potential > 0 else 0.0
    
    def _analyze_performance_trend(self, history: List[Dict[str, Any]]) -> str:
        """Analyze performance trend over time."""
        if len(history) < 10:
            return "Insufficient data for trend analysis"
        
        recent_scores = [attempt.get('score_earned', 0) for attempt in history[-10:]]
        older_scores = [attempt.get('score_earned', 0) for attempt in history[-20:-10]] if len(history) >= 20 else []
        
        if not older_scores:
            return "Building performance baseline"
        
        recent_avg = np.mean(recent_scores)
        older_avg = np.mean(older_scores)
        
        improvement = (recent_avg - older_avg) / older_avg * 100
        
        if improvement > 20:
            return f"Rapidly improving (+{improvement:.1f}%)"
        elif improvement > 10:
            return f"Improving steadily (+{improvement:.1f}%)"
        elif improvement > 0:
            return f"Slight improvement (+{improvement:.1f}%)"
        elif improvement > -10:
            return f"Stable performance ({improvement:.1f}%)"
        else:
            return f"Declining performance ({improvement:.1f}%)"

class PerformanceTracker:
    """Tracks and analyzes user performance for adaptive scoring."""
    
    def __init__(self, db_connection=None):
        """Initialize performance tracker."""
        self.db = db_connection
        self.performance_cache = {}
        
    def get_current_performance(self, user_id: str) -> PerformanceSnapshot:
        """Get current performance snapshot for user."""
        try:
            # Try cache first
            if user_id in self.performance_cache:
                cached_performance = self.performance_cache[user_id]
                # Check if cache is recent (within 5 minutes)
                if (datetime.now() - cached_performance.timestamp).seconds < 300:
                    return cached_performance
            
            # Fetch from database
            performance = self._fetch_performance_from_db(user_id)
            
            # Cache the result
            self.performance_cache[user_id] = performance
            
            return performance
            
        except Exception as e:
            logger.error(f"Error getting performance for user {user_id}: {e}")
            return self._create_default_performance(user_id)
    
    def record_attempt(self, user_id: str, challenge: Dict[str, Any], 
                      attempt_data: Dict[str, Any], score_earned: int) -> None:
        """Record a challenge attempt for performance tracking."""
        try:
            if self.db:
                attempt_record = {
                    'user_id': user_id,
                    'challenge_id': challenge.get('id'),
                    'category': challenge.get('category'),
                    'difficulty': challenge.get('difficulty'),
                    'is_correct': attempt_data.get('is_correct', False),
                    'completion_time': attempt_data.get('completion_time', 0),
                    'hint_count': attempt_data.get('hint_count', 0),
                    'attempt_number': attempt_data.get('attempt_number', 1),
                    'score_earned': score_earned,
                    'timestamp': datetime.now()
                }
                
                self.db.challenge_attempts.insert_one(attempt_record)
                
                # Invalidate cache for this user
                if user_id in self.performance_cache:
                    del self.performance_cache[user_id]
                
        except Exception as e:
            logger.error(f"Error recording attempt for user {user_id}: {e}")
    
    def _fetch_performance_from_db(self, user_id: str) -> PerformanceSnapshot:
        """Fetch performance data from database."""
        if not self.db:
            return self._create_default_performance(user_id)
        
        # Get user basic info
        user = self.db.users.find_one({'_id': user_id}) or {}
        
        # Get recent attempts (last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        attempts = list(self.db.challenge_attempts.find({
            'user_id': user_id,
            'timestamp': {'$gte': thirty_days_ago}
        }).sort('timestamp', 1))
        
        # Calculate performance metrics
        total_attempts = len(attempts)
        successful_attempts = sum(1 for attempt in attempts if attempt.get('is_correct', False))
        overall_success_rate = (successful_attempts / total_attempts) if total_attempts > 0 else 0.0
        
        # Category success rates
        category_stats = defaultdict(lambda: {'total': 0, 'correct': 0})
        for attempt in attempts:
            category = attempt.get('category', 'unknown')
            category_stats[category]['total'] += 1
            if attempt.get('is_correct', False):
                category_stats[category]['correct'] += 1
        
        category_success_rates = {}
        for category, stats in category_stats.items():
            category_success_rates[category] = stats['correct'] / stats['total'] if stats['total'] > 0 else 0.0
        
        # Average completion time
        completion_times = [attempt.get('completion_time', 0) for attempt in attempts if attempt.get('completion_time')]
        average_completion_time = np.mean(completion_times) if completion_times else 0.0
        
        # Hint usage average
        hint_counts = [attempt.get('hint_count', 0) for attempt in attempts]
        hint_usage_average = np.mean(hint_counts) if hint_counts else 0.0
        
        # Current streak
        current_streak = self._calculate_current_streak(attempts)
        
        # Learning velocity
        learning_velocity = self._calculate_learning_velocity(attempts)
        
        # Recent improvement
        recent_improvement = self._calculate_recent_improvement(attempts)
        
        return PerformanceSnapshot(
            user_id=user_id,
            timestamp=datetime.now(),
            overall_success_rate=overall_success_rate,
            category_success_rates=category_success_rates,
            average_completion_time=average_completion_time,
            hint_usage_average=hint_usage_average,
            current_streak=current_streak,
            level=user.get('level', 1),
            total_score=user.get('score', 0),
            learning_velocity=learning_velocity,
            recent_improvement=recent_improvement
        )
    
    def _create_default_performance(self, user_id: str) -> PerformanceSnapshot:
        """Create default performance snapshot for new users."""
        return PerformanceSnapshot(
            user_id=user_id,
            timestamp=datetime.now(),
            overall_success_rate=0.5,
            category_success_rates={},
            average_completion_time=120.0,
            hint_usage_average=1.0,
            current_streak=0,
            level=1,
            total_score=0,
            learning_velocity=0.0,
            recent_improvement=0.0
        )