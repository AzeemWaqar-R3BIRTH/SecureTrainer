"""
AI Integration Layer for SecureTrainer
Production-ready ML pipeline integration

This module provides:
1. Unified interface for all AI components
2. Real-time ML pipeline orchestration
3. Performance prediction and analytics
4. Continuous learning and model updates
5. Production-ready error handling and fallbacks
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from dataclasses import dataclass
import json

# Import AI components
from .challenge_engine import AIChallengEngine, PerformanceMetrics, DifficultyLevel
from .validation_system import AdvancedChallengeValidator, ValidationResult
from .adaptive_scoring import AdaptiveScoringEngine, ScoreBreakdown
from .hint_generator import IntelligentHintGenerator, HintContext, LearningStyle
from .enhanced_challenges import EnhancedChallengeModel, ChallengeVariant

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AIResponse:
    """Unified AI response structure."""
    success: bool
    data: Any
    confidence: float
    processing_time: float
    model_version: str
    explanation: str
    fallback_used: bool = False

@dataclass
class UserSession:
    """User session context for AI processing."""
    user_id: str
    session_id: str
    current_challenge: Optional[str]
    performance_history: List[Dict[str, Any]]
    learning_style: LearningStyle
    skill_profile: Dict[str, float]
    session_start: datetime
    interactions: List[Dict[str, Any]]

class AIOrchestrator:
    """
    Main orchestrator for AI-driven challenge system.
    
    Coordinates all AI components and provides unified interface
    for the application layer.
    """
    
    def __init__(self, db_connection=None):
        """Initialize AI orchestrator."""
        self.db = db_connection
        
        # Initialize AI components
        self.challenge_engine = AIChallengEngine(db_connection)
        self.validator = AdvancedChallengeValidator()
        self.scoring_engine = AdaptiveScoringEngine(db_connection)
        self.hint_generator = IntelligentHintGenerator(db_connection)
        self.challenge_model = EnhancedChallengeModel()
        
        # Session management
        self.active_sessions = {}
        
        # Performance tracking
        self.performance_metrics = {
            'total_requests': 0,
            'successful_predictions': 0,
            'average_response_time': 0.0,
            'model_accuracy': 0.0
        }
        
        logger.info("AI Orchestrator initialized successfully")
    
    async def start_user_session(self, user_id: str, user_data: Dict[str, Any]) -> UserSession:
        """Start AI-powered user session."""
        try:
            session_id = f"{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Analyze user performance for session initialization
            performance_metrics = self.challenge_engine.analyze_real_time_performance(user_id, {})
            
            # Determine learning style
            learning_style = self._determine_learning_style(user_data, performance_metrics)
            
            # Build skill profile
            skill_profile = self._build_skill_profile(user_data, performance_metrics)
            
            # Get performance history
            performance_history = self._get_user_performance_history(user_id)
            
            session = UserSession(
                user_id=user_id,
                session_id=session_id,
                current_challenge=None,
                performance_history=performance_history,
                learning_style=learning_style,
                skill_profile=skill_profile,
                session_start=datetime.now(),
                interactions=[]
            )
            
            self.active_sessions[session_id] = session
            
            logger.info(f"AI session started for user {user_id}: {session_id}")
            return session
            
        except Exception as e:
            logger.error(f"Error starting AI session for user {user_id}: {e}")
            raise
    
    async def get_adaptive_challenge(self, session_id: str, category: Optional[str] = None) -> AIResponse:
        """Get AI-recommended challenge for user."""
        start_time = datetime.now()
        
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return AIResponse(
                    success=False,
                    data=None,
                    confidence=0.0,
                    processing_time=0.0,
                    model_version="1.0",
                    explanation="Session not found",
                    fallback_used=True
                )
            
            # Get adaptive challenge sequence
            challenges = self.challenge_engine.generate_adaptive_challenge_sequence(
                session.user_id, category or 'sql_injection', count=1
            )
            
            if challenges:
                challenge = challenges[0]
                session.current_challenge = challenge['id']
                
                # Get AI insights for the challenge
                insights = self.challenge_engine.get_performance_insights(session.user_id)
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                return AIResponse(
                    success=True,
                    data=challenge,
                    confidence=0.85,
                    processing_time=processing_time,
                    model_version="1.0",
                    explanation="AI-selected challenge based on performance analysis",
                    fallback_used=False
                )
            else:
                # Fallback to enhanced challenge model
                fallback_challenges = self.challenge_model.get_adaptive_sequence(
                    session.skill_profile.get('overall', 0.5), category, 1
                )
                
                processing_time = (datetime.now() - start_time).total_seconds()
                
                return AIResponse(
                    success=True,
                    data=fallback_challenges[0].__dict__ if fallback_challenges else None,
                    confidence=0.6,
                    processing_time=processing_time,
                    model_version="1.0",
                    explanation="Fallback challenge selection used",
                    fallback_used=True
                )
                
        except Exception as e:
            logger.error(f"Error getting adaptive challenge: {e}")
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AIResponse(
                success=False,
                data=None,
                confidence=0.0,
                processing_time=processing_time,
                model_version="1.0",
                explanation=f"Error: {str(e)}",
                fallback_used=True
            )
    
    async def validate_solution(self, session_id: str, challenge_id: str, 
                              user_solution: str) -> AIResponse:
        """Validate user solution using AI."""
        start_time = datetime.now()
        
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return self._create_error_response("Session not found", start_time)
            
            # Get challenge data
            challenge = self.challenge_model.get_challenge_by_id(challenge_id)
            if not challenge:
                return self._create_error_response("Challenge not found", start_time)
            
            # Prepare validation context
            context = {
                'challenge_category': challenge.category,
                'difficulty_level': challenge.difficulty.level_name,
                'user_skill_level': session.skill_profile.get(challenge.category, 0.5)
            }
            
            # Validate solution
            validation_result, analysis = self.validator.validate_solution(
                user_solution, challenge.__dict__, context
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AIResponse(
                success=True,
                data={
                    'is_correct': validation_result != ValidationResult.INCORRECT,
                    'result_level': validation_result.level,
                    'score_multiplier': validation_result.score_multiplier,
                    'analysis': analysis
                },
                confidence=analysis.get('confidence_score', 0.8),
                processing_time=processing_time,
                model_version="1.0",
                explanation=validation_result.description
            )
            
        except Exception as e:
            logger.error(f"Error validating solution: {e}")
            return self._create_error_response(f"Validation error: {str(e)}", start_time)
    
    async def calculate_adaptive_score(self, session_id: str, challenge_id: str,
                                     attempt_data: Dict[str, Any]) -> AIResponse:
        """Calculate adaptive score using AI."""
        start_time = datetime.now()
        
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return self._create_error_response("Session not found", start_time)
            
            challenge = self.challenge_model.get_challenge_by_id(challenge_id)
            if not challenge:
                return self._create_error_response("Challenge not found", start_time)
            
            # Calculate adaptive score
            final_score, breakdown = self.scoring_engine.calculate_adaptive_score(
                session.user_id, challenge.__dict__, attempt_data
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AIResponse(
                success=True,
                data={
                    'final_score': final_score,
                    'breakdown': breakdown.__dict__,
                    'performance_insights': self.scoring_engine.get_user_scoring_insights(session.user_id)
                },
                confidence=0.9,
                processing_time=processing_time,
                model_version="1.0",
                explanation="Adaptive scoring based on user performance profile"
            )
            
        except Exception as e:
            logger.error(f"Error calculating adaptive score: {e}")
            return self._create_error_response(f"Scoring error: {str(e)}", start_time)
    
    async def generate_intelligent_hint(self, session_id: str, challenge_id: str,
                                      attempt_count: int, time_spent: float) -> AIResponse:
        """Generate intelligent hint using AI."""
        start_time = datetime.now()
        
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return self._create_error_response("Session not found", start_time)
            
            challenge = self.challenge_model.get_challenge_by_id(challenge_id)
            if not challenge:
                return self._create_error_response("Challenge not found", start_time)
            
            # Create hint context
            hint_context = HintContext(
                user_id=session.user_id,
                challenge_category=challenge.category,
                difficulty_level=challenge.difficulty.level_name,
                attempt_count=attempt_count,
                time_spent=time_spent,
                previous_hints=self._get_previous_hints(session, challenge_id),
                user_learning_style=session.learning_style,
                struggle_indicators=[],
                skill_level=session.skill_profile.get(challenge.category, 0.5)
            )
            
            # Generate hint
            generated_hint = self.hint_generator.generate_adaptive_hint(
                hint_context, challenge.__dict__
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AIResponse(
                success=True,
                data=generated_hint.__dict__,
                confidence=generated_hint.effectiveness_prediction,
                processing_time=processing_time,
                model_version="1.0",
                explanation=generated_hint.reasoning
            )
            
        except Exception as e:
            logger.error(f"Error generating hint: {e}")
            return self._create_error_response(f"Hint generation error: {str(e)}", start_time)
    
    async def get_performance_analytics(self, session_id: str) -> AIResponse:
        """Get comprehensive performance analytics."""
        start_time = datetime.now()
        
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                return self._create_error_response("Session not found", start_time)
            
            # Get insights from challenge engine
            insights = self.challenge_engine.get_performance_insights(session.user_id)
            
            # Get scoring insights
            scoring_insights = self.scoring_engine.get_user_scoring_insights(session.user_id)
            
            # Get hint analytics
            hint_analytics = self.hint_generator.get_hint_analytics(session.user_id)
            
            # Combine all analytics
            combined_analytics = {
                'performance_insights': insights,
                'scoring_insights': scoring_insights,
                'hint_analytics': hint_analytics,
                'session_summary': self._generate_session_summary(session),
                'recommendations': self._generate_recommendations(session, insights)
            }
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return AIResponse(
                success=True,
                data=combined_analytics,
                confidence=0.85,
                processing_time=processing_time,
                model_version="1.0",
                explanation="Comprehensive performance analytics generated"
            )
            
        except Exception as e:
            logger.error(f"Error generating analytics: {e}")
            return self._create_error_response(f"Analytics error: {str(e)}", start_time)
    
    async def update_user_model(self, session_id: str, challenge_result: Dict[str, Any]) -> None:
        """Update user model with new performance data."""
        try:
            session = self.active_sessions.get(session_id)
            if not session:
                logger.warning(f"Cannot update model: session {session_id} not found")
                return
            
            # Update challenge engine model
            self.challenge_engine.update_performance_model(session.user_id, challenge_result)
            
            # Record interaction
            session.interactions.append({
                'timestamp': datetime.now(),
                'challenge_id': challenge_result.get('challenge_id'),
                'result': challenge_result,
                'type': 'challenge_completion'
            })
            
            logger.info(f"User model updated for session {session_id}")
            
        except Exception as e:
            logger.error(f"Error updating user model: {e}")
    
    def get_system_performance_metrics(self) -> Dict[str, Any]:
        """Get AI system performance metrics."""
        return {
            'orchestrator_metrics': self.performance_metrics,
            'active_sessions': len(self.active_sessions),
            'component_status': {
                'challenge_engine': 'active',
                'validator': 'active',
                'scoring_engine': 'active',
                'hint_generator': 'active',
                'challenge_model': 'active'
            },
            'last_updated': datetime.now().isoformat()
        }
    
    # Private helper methods
    
    def _determine_learning_style(self, user_data: Dict[str, Any], 
                                 performance_metrics: PerformanceMetrics) -> LearningStyle:
        """Determine user's learning style from data."""
        # Simple heuristic - in production, use ML model
        if performance_metrics.hint_usage_rate > 3:
            return LearningStyle.GUIDED
        elif performance_metrics.hint_usage_rate < 1:
            return LearningStyle.INDEPENDENT
        elif performance_metrics.average_completion_time < 60:
            return LearningStyle.PRACTICAL
        else:
            return LearningStyle.ANALYTICAL
    
    def _build_skill_profile(self, user_data: Dict[str, Any], 
                           performance_metrics: PerformanceMetrics) -> Dict[str, float]:
        """Build user skill profile."""
        skill_profile = {
            'overall': performance_metrics.success_rate,
            'sql_injection': performance_metrics.category_mastery.get('sql_injection', 0.5),
            'xss': performance_metrics.category_mastery.get('xss', 0.5),
            'command_injection': performance_metrics.category_mastery.get('command_injection', 0.5),
            'authentication': performance_metrics.category_mastery.get('authentication', 0.5)
        }
        
        return skill_profile
    
    def _get_user_performance_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user performance history."""
        if self.db:
            try:
                return list(self.db.challenge_attempts.find(
                    {'user_id': user_id}
                ).sort('attempt_time', -1).limit(50))
            except Exception as e:
                logger.error(f"Error fetching performance history: {e}")
        
        return []
    
    def _get_previous_hints(self, session: UserSession, challenge_id: str) -> List[str]:
        """Get previous hints for the challenge."""
        hints = []
        for interaction in session.interactions:
            if (interaction.get('type') == 'hint_request' and 
                interaction.get('challenge_id') == challenge_id):
                hints.append(interaction.get('hint_content', ''))
        
        return hints
    
    def _generate_session_summary(self, session: UserSession) -> Dict[str, Any]:
        """Generate session summary."""
        return {
            'session_duration': (datetime.now() - session.session_start).total_seconds(),
            'interactions_count': len(session.interactions),
            'challenges_attempted': len(set(i.get('challenge_id') for i in session.interactions)),
            'learning_style': session.learning_style.value,
            'skill_profile': session.skill_profile
        }
    
    def _generate_recommendations(self, session: UserSession, insights: Dict[str, Any]) -> List[str]:
        """Generate personalized recommendations."""
        recommendations = []
        
        # Based on skill profile
        weak_areas = [cat for cat, score in session.skill_profile.items() if score < 0.5]
        if weak_areas:
            recommendations.append(f"Focus on improving {', '.join(weak_areas[:2])} skills")
        
        # Based on learning style
        if session.learning_style == LearningStyle.GUIDED:
            recommendations.append("Continue using hints and guided learning")
        elif session.learning_style == LearningStyle.INDEPENDENT:
            recommendations.append("Try more advanced challenges with minimal hints")
        
        return recommendations
    
    def _create_error_response(self, error_message: str, start_time: datetime) -> AIResponse:
        """Create standardized error response."""
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return AIResponse(
            success=False,
            data=None,
            confidence=0.0,
            processing_time=processing_time,
            model_version="1.0",
            explanation=error_message,
            fallback_used=True
        )