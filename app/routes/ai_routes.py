"""
AI-Enhanced Routes for SecureTrainer
Production-ready AI integration with Flask

This module provides AI-enhanced endpoints that:
1. Integrate AI orchestrator with web application
2. Provide adaptive challenge selection and validation
3. Support real-time performance analytics
4. Enable intelligent hint generation
5. Offer comprehensive user insights
"""

import asyncio
import logging
from datetime import datetime
from flask import Blueprint, request, jsonify, session, current_app
from functools import wraps
import json

# Import AI components
from app.ai.ai_integration import AIOrchestrator, UserSession
from app.ai.hint_generator import LearningStyle

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

# Initialize AI Orchestrator
ai_orchestrator = None

def init_ai_orchestrator(db_connection=None):
    """Initialize AI orchestrator with database connection."""
    global ai_orchestrator
    if ai_orchestrator is None:
        ai_orchestrator = AIOrchestrator(db_connection)
        logger.info("AI Orchestrator initialized for routes")

def require_ai_session(f):
    """Decorator to ensure AI session exists."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'ai_session_id' not in session:
            return jsonify({
                'success': False,
                'error': 'AI session not found. Please start a session first.',
                'error_code': 'NO_AI_SESSION'
            }), 400
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

def async_route(f):
    """Decorator to handle async routes in Flask."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(f(*args, **kwargs))
            return result
        finally:
            loop.close()
    decorated_function.__name__ = f.__name__
    return decorated_function

@ai_bp.route('/session/start', methods=['POST'])
@async_route
async def start_ai_session():
    """Start AI-powered user session."""
    try:
        if not ai_orchestrator:
            return jsonify({
                'success': False,
                'error': 'AI system not available',
                'error_code': 'AI_UNAVAILABLE'
            }), 503
        
        # Get user data from session
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'User not authenticated',
                'error_code': 'NOT_AUTHENTICATED'
            }), 401
        
        user_id = session['user_id']
        
        # Get user data from database
        from app.models.user_model import get_user_by_id
        user_data = get_user_by_id(user_id)
        
        if not user_data:
            return jsonify({
                'success': False,
                'error': 'User not found',
                'error_code': 'USER_NOT_FOUND'
            }), 404
        
        # Start AI session
        ai_session = await ai_orchestrator.start_user_session(user_id, user_data)
        
        # Store session ID in Flask session
        session['ai_session_id'] = ai_session.session_id
        session.permanent = True
        
        return jsonify({
            'success': True,
            'data': {
                'session_id': ai_session.session_id,
                'learning_style': ai_session.learning_style.value,
                'skill_profile': ai_session.skill_profile,
                'session_start': ai_session.session_start.isoformat()
            },
            'message': 'AI session started successfully'
        })
        
    except Exception as e:
        logger.error(f"Error starting AI session: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to start AI session',
            'error_code': 'SESSION_START_FAILED',
            'details': str(e)
        }), 500

@ai_bp.route('/challenge/adaptive', methods=['GET'])
@require_ai_session
@async_route
async def get_adaptive_challenge():
    """Get AI-recommended challenge."""
    try:
        ai_session_id = session['ai_session_id']
        category = request.args.get('category')  # Optional category filter
        
        # Get adaptive challenge
        ai_response = await ai_orchestrator.get_adaptive_challenge(ai_session_id, category)
        
        if ai_response.success:
            return jsonify({
                'success': True,
                'data': {
                    'challenge': ai_response.data,
                    'ai_metadata': {
                        'confidence': ai_response.confidence,
                        'processing_time': ai_response.processing_time,
                        'explanation': ai_response.explanation,
                        'fallback_used': ai_response.fallback_used
                    }
                },
                'message': 'Adaptive challenge selected'
            })
        else:
            return jsonify({
                'success': False,
                'error': ai_response.explanation,
                'error_code': 'CHALLENGE_SELECTION_FAILED'
            }), 400
            
    except Exception as e:
        logger.error(f"Error getting adaptive challenge: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get adaptive challenge',
            'error_code': 'ADAPTIVE_CHALLENGE_FAILED',
            'details': str(e)
        }), 500

@ai_bp.route('/challenge/validate', methods=['POST'])
@require_ai_session
@async_route
async def validate_solution():
    """Validate challenge solution using AI."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Invalid request data',
                'error_code': 'INVALID_REQUEST'
            }), 400
        
        challenge_id = data.get('challenge_id')
        user_solution = data.get('solution')
        
        if not challenge_id or not user_solution:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: challenge_id, solution',
                'error_code': 'MISSING_FIELDS'
            }), 400
        
        ai_session_id = session['ai_session_id']
        
        # Validate solution
        ai_response = await ai_orchestrator.validate_solution(
            ai_session_id, challenge_id, user_solution
        )
        
        if ai_response.success:
            return jsonify({
                'success': True,
                'data': {
                    'validation_result': ai_response.data,
                    'ai_metadata': {
                        'confidence': ai_response.confidence,
                        'processing_time': ai_response.processing_time,
                        'explanation': ai_response.explanation
                    }
                },
                'message': 'Solution validated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': ai_response.explanation,
                'error_code': 'VALIDATION_FAILED'
            }), 400
            
    except Exception as e:
        logger.error(f"Error validating solution: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to validate solution',
            'error_code': 'SOLUTION_VALIDATION_FAILED',
            'details': str(e)
        }), 500

@ai_bp.route('/challenge/score', methods=['POST'])
@require_ai_session
@async_route
async def calculate_adaptive_score():
    """Calculate adaptive score for challenge attempt."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Invalid request data',
                'error_code': 'INVALID_REQUEST'
            }), 400
        
        challenge_id = data.get('challenge_id')
        attempt_data = data.get('attempt_data', {})
        
        if not challenge_id:
            return jsonify({
                'success': False,
                'error': 'Missing required field: challenge_id',
                'error_code': 'MISSING_CHALLENGE_ID'
            }), 400
        
        ai_session_id = session['ai_session_id']
        
        # Calculate adaptive score
        ai_response = await ai_orchestrator.calculate_adaptive_score(
            ai_session_id, challenge_id, attempt_data
        )
        
        if ai_response.success:
            # Update user model with the result
            challenge_result = {
                'challenge_id': challenge_id,
                'is_correct': attempt_data.get('is_correct', False),
                'completion_time': attempt_data.get('completion_time', 0),
                'hint_count': attempt_data.get('hint_count', 0),
                'score_earned': ai_response.data['final_score']
            }
            
            await ai_orchestrator.update_user_model(ai_session_id, challenge_result)
            
            return jsonify({
                'success': True,
                'data': {
                    'scoring_result': ai_response.data,
                    'ai_metadata': {
                        'confidence': ai_response.confidence,
                        'processing_time': ai_response.processing_time,
                        'explanation': ai_response.explanation
                    }
                },
                'message': 'Adaptive score calculated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': ai_response.explanation,
                'error_code': 'SCORING_FAILED'
            }), 400
            
    except Exception as e:
        logger.error(f"Error calculating adaptive score: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to calculate adaptive score',
            'error_code': 'ADAPTIVE_SCORING_FAILED',
            'details': str(e)
        }), 500

@ai_bp.route('/hint/generate', methods=['POST'])
@require_ai_session
@async_route
async def generate_intelligent_hint():
    """Generate intelligent hint for current challenge."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'error': 'Invalid request data',
                'error_code': 'INVALID_REQUEST'
            }), 400
        
        challenge_id = data.get('challenge_id')
        attempt_count = data.get('attempt_count', 1)
        time_spent = data.get('time_spent', 0)
        
        if not challenge_id:
            return jsonify({
                'success': False,
                'error': 'Missing required field: challenge_id',
                'error_code': 'MISSING_CHALLENGE_ID'
            }), 400
        
        ai_session_id = session['ai_session_id']
        
        # Generate intelligent hint
        ai_response = await ai_orchestrator.generate_intelligent_hint(
            ai_session_id, challenge_id, attempt_count, time_spent
        )
        
        if ai_response.success:
            return jsonify({
                'success': True,
                'data': {
                    'hint': ai_response.data,
                    'ai_metadata': {
                        'confidence': ai_response.confidence,
                        'processing_time': ai_response.processing_time,
                        'explanation': ai_response.explanation
                    }
                },
                'message': 'Intelligent hint generated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': ai_response.explanation,
                'error_code': 'HINT_GENERATION_FAILED'
            }), 400
            
    except Exception as e:
        logger.error(f"Error generating hint: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate hint',
            'error_code': 'HINT_GENERATION_FAILED',
            'details': str(e)
        }), 500

@ai_bp.route('/analytics/performance', methods=['GET'])
@require_ai_session
@async_route
async def get_performance_analytics():
    """Get comprehensive performance analytics."""
    try:
        ai_session_id = session['ai_session_id']
        
        # Get performance analytics
        ai_response = await ai_orchestrator.get_performance_analytics(ai_session_id)
        
        if ai_response.success:
            return jsonify({
                'success': True,
                'data': {
                    'analytics': ai_response.data,
                    'ai_metadata': {
                        'confidence': ai_response.confidence,
                        'processing_time': ai_response.processing_time,
                        'explanation': ai_response.explanation
                    }
                },
                'message': 'Performance analytics generated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': ai_response.explanation,
                'error_code': 'ANALYTICS_FAILED'
            }), 400
            
    except Exception as e:
        logger.error(f"Error getting performance analytics: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get performance analytics',
            'error_code': 'ANALYTICS_FAILED',
            'details': str(e)
        }), 500

@ai_bp.route('/system/metrics', methods=['GET'])
def get_system_metrics():
    """Get AI system performance metrics."""
    try:
        if not ai_orchestrator:
            return jsonify({
                'success': False,
                'error': 'AI system not available',
                'error_code': 'AI_UNAVAILABLE'
            }), 503
        
        metrics = ai_orchestrator.get_system_performance_metrics()
        
        return jsonify({
            'success': True,
            'data': metrics,
            'message': 'System metrics retrieved successfully'
        })
        
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get system metrics',
            'error_code': 'METRICS_FAILED',
            'details': str(e)
        }), 500

@ai_bp.route('/session/info', methods=['GET'])
@require_ai_session
def get_session_info():
    """Get current AI session information."""
    try:
        ai_session_id = session.get('ai_session_id')
        ai_session = ai_orchestrator.active_sessions.get(ai_session_id)
        
        if not ai_session:
            return jsonify({
                'success': False,
                'error': 'AI session not found',
                'error_code': 'SESSION_NOT_FOUND'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'session_id': ai_session.session_id,
                'user_id': ai_session.user_id,
                'learning_style': ai_session.learning_style.value,
                'skill_profile': ai_session.skill_profile,
                'session_start': ai_session.session_start.isoformat(),
                'current_challenge': ai_session.current_challenge,
                'interactions_count': len(ai_session.interactions)
            },
            'message': 'Session information retrieved successfully'
        })
        
    except Exception as e:
        logger.error(f"Error getting session info: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get session information',
            'error_code': 'SESSION_INFO_FAILED',
            'details': str(e)
        }), 500

@ai_bp.route('/session/end', methods=['POST'])
@require_ai_session
def end_ai_session():
    """End current AI session."""
    try:
        ai_session_id = session.get('ai_session_id')
        
        # Remove session from orchestrator
        if ai_session_id in ai_orchestrator.active_sessions:
            del ai_orchestrator.active_sessions[ai_session_id]
        
        # Remove from Flask session
        session.pop('ai_session_id', None)
        
        return jsonify({
            'success': True,
            'message': 'AI session ended successfully'
        })
        
    except Exception as e:
        logger.error(f"Error ending AI session: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to end AI session',
            'error_code': 'SESSION_END_FAILED',
            'details': str(e)
        }), 500

# Error handlers for the AI blueprint
@ai_bp.errorhandler(404)
def ai_not_found(error):
    """Handle 404 errors for AI routes."""
    return jsonify({
        'success': False,
        'error': 'AI endpoint not found',
        'error_code': 'AI_ENDPOINT_NOT_FOUND'
    }), 404

@ai_bp.errorhandler(500)
def ai_internal_error(error):
    """Handle 500 errors for AI routes."""
    logger.error(f"AI internal error: {error}")
    return jsonify({
        'success': False,
        'error': 'AI system internal error',
        'error_code': 'AI_INTERNAL_ERROR'
    }), 500