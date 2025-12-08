"""
Enhanced Validation API Endpoints
Provides advanced validation capabilities and analytics
"""

from flask import Blueprint, request, jsonify, session
from app.ai.advanced_answer_validation import advanced_validator
from app.utils.enhanced_learning_system import (
    get_learning_performance_metrics, 
    clear_learning_cache,
    get_learning_error_summary
)
from app.models.user_model import get_user_by_id
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

enhanced_validation_bp = Blueprint('enhanced_validation', __name__, url_prefix='/api/validation')

@enhanced_validation_bp.route('/challenge/<challenge_id>', methods=['POST'])
def validate_challenge_enhanced(challenge_id):
    """Enhanced challenge validation with detailed analysis."""
    try:
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        data = request.get_json()
        if not data or 'answer' not in data:
            return jsonify({
                'success': False,
                'error': 'Answer is required'
            }), 400
        
        submitted_answer = data['answer']
        user_id = session['user_id']
        
        # Get user context
        user = get_user_by_id(user_id)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        # Prepare challenge context
        challenge_context = {
            'user_level': user.get('level', 1),
            'user_score': user.get('score', 0),
            'timestamp': datetime.now().isoformat()
        }
        
        # Add any additional context from request
        if 'context' in data:
            challenge_context.update(data['context'])
        
        # Validate using advanced system
        is_correct, feedback, analysis = advanced_validator.validate_challenge_answer(
            challenge_id, submitted_answer, challenge_context
        )
        
        # Return comprehensive response
        return jsonify({
            'success': True,
            'is_correct': is_correct,
            'feedback': feedback,
            'confidence': analysis.get('confidence_score', 0),
            'validation_layer': analysis.get('validation_layer', 'unknown'),
            'semantic_score': analysis.get('semantic_score', 0),
            'pattern_matches': analysis.get('pattern_matches', []),
            'evasion_techniques': analysis.get('evasion_techniques', []),
            'processing_time': analysis.get('processing_time', 0),
            'validation_path': analysis.get('validation_path', []),
            'detailed_analysis': analysis.get('detailed_analysis', {}),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error in enhanced validation: {e}")
        return jsonify({
            'success': False,
            'error': 'Validation system error',
            'message': str(e)
        }), 500

@enhanced_validation_bp.route('/feedback/<challenge_id>', methods=['POST'])
def get_validation_feedback(challenge_id):
    """Get detailed validation feedback without scoring."""
    try:
        data = request.get_json()
        if not data or 'answer' not in data:
            return jsonify({
                'success': False,
                'error': 'Answer is required'
            }), 400
        
        submitted_answer = data['answer']
        
        # Get context if provided
        context = data.get('context', {})
        
        # Validate using advanced system
        is_correct, feedback, analysis = advanced_validator.validate_challenge_answer(
            challenge_id, submitted_answer, context
        )
        
        # Return feedback-focused response
        return jsonify({
            'success': True,
            'feedback': feedback,
            'is_correct': is_correct,
            'confidence': analysis.get('confidence_score', 0),
            'hints': analysis.get('detailed_analysis', {}).get('hints', []),
            'suggestions': analysis.get('detailed_analysis', {}).get('suggestions', []),
            'validation_summary': {
                'layer': analysis.get('validation_layer', 'unknown'),
                'processing_time': analysis.get('processing_time', 0),
                'patterns_found': len(analysis.get('pattern_matches', []))
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting validation feedback: {e}")
        return jsonify({
            'success': False,
            'error': 'Feedback system error'
        }), 500

@enhanced_validation_bp.route('/statistics', methods=['GET'])
def get_validation_statistics():
    """Get validation system statistics."""
    try:
        # Check if user is authenticated and has appropriate permissions
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        user_id = session['user_id']
        user = get_user_by_id(user_id)
        
        # Only allow admin or high-level users to see statistics
        if not user or user.get('role', '').lower() not in ['admin', 'instructor']:
            return jsonify({
                'success': False,
                'error': 'Insufficient permissions'
            }), 403
        
        # Get validation statistics
        validation_stats = advanced_validator.get_validation_statistics()
        
        # Get learning system performance metrics
        learning_stats = get_learning_performance_metrics()
        
        # Get error summary
        error_summary = get_learning_error_summary()
        
        return jsonify({
            'success': True,
            'validation_statistics': validation_stats,
            'learning_performance': learning_stats,
            'error_summary': error_summary,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting validation statistics: {e}")
        return jsonify({
            'success': False,
            'error': 'Statistics retrieval error'
        }), 500

@enhanced_validation_bp.route('/cache/clear', methods=['POST'])
def clear_validation_cache():
    """Clear validation system cache."""
    try:
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        user_id = session['user_id']
        user = get_user_by_id(user_id)
        
        # Only allow admin users to clear cache
        if not user or user.get('role', '').lower() != 'admin':
            return jsonify({
                'success': False,
                'error': 'Admin privileges required'
            }), 403
        
        # Clear validation cache
        advanced_validator.clear_validation_cache()
        
        # Clear learning cache
        clear_learning_cache()
        
        return jsonify({
            'success': True,
            'message': 'Validation and learning caches cleared',
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return jsonify({
            'success': False,
            'error': 'Cache clear error'
        }), 500

@enhanced_validation_bp.route('/health', methods=['GET'])
def validation_system_health():
    """Get validation system health status."""
    try:
        health_status = {
            'validation_system': 'operational',
            'learning_system': 'operational',
            'cache_system': 'operational',
            'database_connection': 'unknown',
            'timestamp': datetime.now().isoformat()
        }
        
        # Test validation system
        try:
            test_result = advanced_validator.validate_challenge_answer(
                'test_challenge', 'test_answer', {'test': True}
            )
            health_status['validation_system'] = 'operational'
        except Exception as e:
            health_status['validation_system'] = 'error'
            health_status['validation_error'] = str(e)
        
        # Test database connection
        try:
            from app.models.user_model import get_db
            db = get_db()
            if db:
                # Try a simple query
                db.list_collection_names()
                health_status['database_connection'] = 'operational'
            else:
                health_status['database_connection'] = 'unavailable'
        except Exception as e:
            health_status['database_connection'] = 'error'
            health_status['database_error'] = str(e)
        
        # Get performance metrics
        try:
            validation_stats = advanced_validator.get_validation_statistics()
            learning_stats = get_learning_performance_metrics()
            
            health_status['performance'] = {
                'validation_success_rate': validation_stats.get('success_rate', 0),
                'learning_cache_hit_rate': learning_stats.get('cache_hit_rate', 0),
                'average_response_time': learning_stats.get('average_response_time', 0)
            }
        except Exception as e:
            health_status['performance_error'] = str(e)
        
        # Determine overall health
        critical_systems = ['validation_system', 'database_connection']
        overall_health = 'healthy'
        
        for system in critical_systems:
            if health_status.get(system) == 'error':
                overall_health = 'unhealthy'
                break
            elif health_status.get(system) == 'unavailable':
                overall_health = 'degraded'
        
        health_status['overall_status'] = overall_health
        
        # Return appropriate HTTP status based on health
        if overall_health == 'healthy':
            return jsonify({
                'success': True,
                'health': health_status
            }), 200
        elif overall_health == 'degraded':
            return jsonify({
                'success': True,
                'health': health_status,
                'warning': 'Some systems are degraded'
            }), 200
        else:
            return jsonify({
                'success': False,
                'health': health_status,
                'error': 'Critical systems are unhealthy'
            }), 503
        
    except Exception as e:
        logger.error(f"Error checking system health: {e}")
        return jsonify({
            'success': False,
            'error': 'Health check failed',
            'timestamp': datetime.now().isoformat()
        }), 500

@enhanced_validation_bp.route('/answer-database/add', methods=['POST'])
def add_expected_answers():
    """Add expected answers to the validation database."""
    try:
        if 'user_id' not in session:
            return jsonify({
                'success': False,
                'error': 'Authentication required'
            }), 401
        
        user_id = session['user_id']
        user = get_user_by_id(user_id)
        
        # Only allow admin or instructor users to add answers
        if not user or user.get('role', '').lower() not in ['admin', 'instructor']:
            return jsonify({
                'success': False,
                'error': 'Insufficient permissions'
            }), 403
        
        data = request.get_json()
        if not data or 'challenge_id' not in data or 'answers' not in data:
            return jsonify({
                'success': False,
                'error': 'challenge_id and answers are required'
            }), 400
        
        challenge_id = data['challenge_id']
        answers = data['answers']
        
        if not isinstance(answers, list):
            return jsonify({
                'success': False,
                'error': 'answers must be a list'
            }), 400
        
        # Add answers to validation database
        advanced_validator.add_expected_answers(challenge_id, answers)
        
        return jsonify({
            'success': True,
            'message': f'Added {len(answers)} expected answers for challenge {challenge_id}',
            'challenge_id': challenge_id,
            'answers_added': len(answers),
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error adding expected answers: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to add answers'
        }), 500

# Error handlers for the enhanced validation blueprint
@enhanced_validation_bp.errorhandler(404)
def validation_not_found(error):
    return jsonify({
        'success': False,
        'error': 'Validation endpoint not found'
    }), 404

@enhanced_validation_bp.errorhandler(500)
def validation_internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Validation system internal error'
    }), 500