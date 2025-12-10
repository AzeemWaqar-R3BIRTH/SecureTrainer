# Challenge logic with advanced scoring and validation
from flask import Blueprint, request, jsonify, session
from app.models.user_model import get_user_by_id, update_user_comprehensive
from app.models.challenge_model import (
    get_random_challenge, get_challenge_by_id,
    validate_challenge_solution, record_challenge_attempt,
    calculate_challenge_score, get_all_challenges
)
from app.models.analytics_model import record_user_activity
from app.routes.ai_model import (
    ai_recommendation_ml, calculate_dynamic_score, 
    generate_adaptive_hint, get_adaptive_challenge_sequence
)
import os
import time
from datetime import datetime

challenge_bp = Blueprint('challenge', __name__)


@challenge_bp.route('/start/<user_id>', methods=['GET'])
def start_challenge(user_id):
    """Start a new challenge with AI-powered difficulty selection."""
    try:
        user = get_user_by_id(user_id)
        if not user:
            print(f"User not found: {user_id}")
            return jsonify({'error': 'User not found'}), 404

        # Record activity
        record_user_activity(user_id, 'challenge_request')

        # Get category preference from request
        category = request.args.get('category')
        
        # Handle random category specially
        if category == 'random':
            category = None  # Set to None to get challenges from all categories
        
        # Get adaptive challenge sequence
        try:
            challenges = get_adaptive_challenge_sequence(user, category, count=1)
            if challenges:
                challenge = challenges[0]
            else:
                # Fallback to AI recommendation
                difficulty = ai_recommendation_ml(user)
                challenge = get_random_challenge(difficulty, category)
        except Exception as e:
            print(f"Error getting adaptive challenge: {e}")
            # Ultimate fallback
            challenge = get_fallback_challenge('beginner')

        if not challenge:
            # Try to get a challenge without difficulty filter
            challenge = get_random_challenge(None, category)
            
        if not challenge:
            # Final fallback
            challenge = get_fallback_challenge('beginner')

        # Store challenge start time in session for timing
        session[f'challenge_{challenge["id"]}_start_time'] = time.time()
        session[f'challenge_{challenge["id"]}_attempts'] = 0
        session[f'challenge_{challenge["id"]}_hints_used'] = 0

        # Log the challenge start
        print(f"User {user_id} starting challenge {challenge['id']} ({challenge.get('difficulty', 'unknown')})")

        # Calculate AI insights
        from app.routes.ai_model import predict_user_success_probability
        
        success_prob = predict_user_success_probability(user, challenge)
        confidence_score = int(success_prob * 100)
        
        # Generate reason based on user state
        reason = "Recommended based on your skill level."
        if category:
            reason = f"Selected from {category} to improve your mastery."
        elif user.get('success_rate', 0) < 0.4:
            reason = "Selected to help build your confidence with foundational concepts."
        elif user.get('success_rate', 0) > 0.8:
            reason = "Selected to challenge your high proficiency."
            
        # Return enhanced challenge details with AI insights
        return jsonify({
            'success': True,
            'challenge': {
                'id': challenge['id'],
                'category': challenge['category'],
                'difficulty': challenge.get('difficulty', 'beginner'),
                'scenario': challenge['scenario'],
                'question': challenge['question'],
                'payload': challenge.get('payload', ''),
                'type': challenge.get('type', 'unknown'),
                'score_weight': challenge.get('score_weight', 100),
                'interactive_demo': challenge.get('interactive_demo', False),
                'demo_html': challenge.get('demo_html', ''),
                'hide_payload': challenge.get('hide_payload', False),
                'ai_insights': {
                    'confidence_score': confidence_score,
                    'reason': reason,
                    'difficulty_rating': challenge.get('difficulty', 'beginner').title()
                }
            }
        }), 200
        
    except Exception as e:
        print(f"Error in start_challenge: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return a fallback challenge for presentation
        fallback = get_fallback_challenge("beginner")
        return jsonify({
            'success': True,
            'challenge': {
                'id': fallback['id'],
                'category': fallback['category'],
                'difficulty': fallback['difficulty'],
                'scenario': fallback['scenario'],
                'question': fallback['question'],
                'payload': fallback['payload']
            }
        }), 200


@challenge_bp.route('/submit/<user_id>', methods=['POST'])
def submit_challenge_solution(user_id):
    """Submit and validate challenge solution with comprehensive scoring."""
    try:
        user = get_user_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        data = request.json
        challenge_id = data.get('challenge_id')
        submitted_answer = data.get('answer', '')
        
        if not challenge_id or not submitted_answer:
            return jsonify({'error': 'Missing challenge_id or answer'}), 400

        # CRITICAL: Check if challenge already completed - prevent duplicate submissions
        completed_challenges = user.get('challenges_completed', [])
        if challenge_id in completed_challenges:
            return jsonify({
                'success': False,
                'error': 'Challenge already completed',
                'feedback': 'You have already completed this challenge. Please try a different one.',
                'already_completed': True
            }), 400

        # Get challenge details
        challenge = get_challenge_by_id(challenge_id)
        if not challenge:
            challenge = get_fallback_challenge('beginner')
            if challenge['id'] != challenge_id:
                return jsonify({'error': 'Challenge not found'}), 404

        # Calculate completion time
        start_time_key = f'challenge_{challenge_id}_start_time'
        completion_time = 0
        if start_time_key in session:
            completion_time = time.time() - session[start_time_key]
        
        # Get attempt count and hints used
        attempts_key = f'challenge_{challenge_id}_attempts'
        hints_key = f'challenge_{challenge_id}_hints_used'
        
        attempts_count = session.get(attempts_key, 0) + 1
        hints_used = session.get(hints_key, 0)
        
        # Update session
        session[attempts_key] = attempts_count

        # Validate solution
        is_correct, feedback = validate_challenge_solution(challenge_id, submitted_answer)
        
        # Calculate score
        score_earned = 0
        if is_correct:
            try:
                score_earned = calculate_dynamic_score(
                    user, challenge, completion_time, hints_used, attempts_count
                )
            except Exception as e:
                print(f"Error calculating dynamic score: {e}")
                # Fallback scoring
                base_score = challenge.get('score_weight', 100)
                score_earned = max(base_score // attempts_count, 10)

        # Record the attempt
        try:
            record_challenge_attempt(
                user_id, challenge_id, submitted_answer, 
                is_correct, completion_time, hints_used
            )
        except Exception as e:
            print(f"Error recording challenge attempt: {e}")

        # Update user progress if correct
        if is_correct and score_earned > 0:
            challenge_data = {
                'category': challenge.get('category', ''),
                'difficulty': challenge.get('difficulty', 'beginner'),
                'hints_used': hints_used
            }
            
            try:
                update_user_comprehensive(user_id, score_earned, challenge_data)
            except Exception as e:
                print(f"Error updating user comprehensively: {e}")
                # Fallback to simple update
                from app.models.user_model import update_user_score_level
                update_user_score_level(user_id, score_earned)

        # Record activity
        record_user_activity(user_id, 'challenge_submission', {
            'challenge_id': challenge_id,
            'is_correct': is_correct,
            'score_earned': score_earned,
            'completion_time': completion_time,
            'attempts': attempts_count
        })

        # Get updated user data
        updated_user = get_user_by_id(user_id)
        
        # Clear session data if challenge completed successfully
        if is_correct:
            session.pop(start_time_key, None)
            session.pop(attempts_key, None)
            session.pop(hints_key, None)

        # Prepare response
        response_data = {
            'success': True,
            'correct': is_correct,
            'feedback': feedback,
            'score_earned': score_earned,
            'completion_time': round(completion_time, 2),
            'attempts_count': attempts_count,
            'hints_used': hints_used
        }
        
        if updated_user:
            response_data.update({
                'new_score': updated_user.get('score', 0),
                'new_level': updated_user.get('level', 1),
                'new_role': updated_user.get('role', 'Trainee')
            })

        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"Error in submit_challenge_solution: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'feedback': 'Something went wrong. Please try again.'
        }), 500


@challenge_bp.route('/hint/<challenge_id>', methods=['POST'])
def get_adaptive_challenge_hint(challenge_id):
    """Get an adaptive hint for a specific challenge."""
    try:
        data = request.json or {}
        user_id = data.get('user_id')
        
        if not user_id:
            # Try to get from URL params as fallback
            user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'User ID required'}), 400

        user = get_user_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Get challenge details
        challenge = get_challenge_by_id(challenge_id)
        if not challenge:
            challenge = get_fallback_challenge('beginner')
            if challenge['id'] != challenge_id:
                return jsonify({'error': 'Challenge not found'}), 404

        # Get current attempt count
        attempts_key = f'challenge_{challenge_id}_attempts'
        hints_key = f'challenge_{challenge_id}_hints_used'
        
        attempt_count = session.get(attempts_key, 0)
        hints_used = session.get(hints_key, 0) + 1
        
        # Update hints used in session
        session[hints_key] = hints_used

        # Generate adaptive hint
        try:
            hint = generate_adaptive_hint(user, challenge, attempt_count)
        except Exception as e:
            print(f"Error generating adaptive hint: {e}")
            hint = challenge.get('hint', 'Think about the vulnerability type and how it can be exploited.')

        # Record hint request activity
        record_user_activity(user_id, 'hint_request', {
            'challenge_id': challenge_id,
            'hint_number': hints_used,
            'attempt_count': attempt_count
        })

        # Log hint request
        print(f"User {user_id} requested hint #{hints_used} for challenge {challenge_id}")

        return jsonify({
            'success': True,
            'hint': hint,
            'hint_number': hints_used,
            'hint_penalty': hints_used * 10  # 10% penalty per hint
        }), 200
        
    except Exception as e:
        print(f"Error in get_adaptive_challenge_hint: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            'success': True,
            'hint': 'Analyze the challenge carefully. Think about how the payload interacts with the system.',
            'hint_number': 1,
            'hint_penalty': 10
        }), 200


@challenge_bp.route('/list', methods=['GET'])
def list_available_challenges():
    """List available challenges with filtering and pagination."""
    try:
        # Get query parameters
        category = request.args.get('category')
        difficulty = request.args.get('difficulty')
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        user_id = request.args.get('user_id')
        
        # Get all challenges
        try:
            all_challenges = get_all_challenges()
        except Exception as e:
            print(f"Error getting all challenges: {e}")
            # Fallback to predefined challenges
            all_challenges = [
                get_fallback_challenge('beginner'),
                get_fallback_challenge('intermediate'),
                get_fallback_challenge('advanced')
            ]
        
        # Apply filters
        filtered_challenges = all_challenges
        
        if category:
            filtered_challenges = [
                c for c in filtered_challenges 
                if c.get('category', '').lower() == category.lower()
            ]
        
        if difficulty:
            filtered_challenges = [
                c for c in filtered_challenges 
                if c.get('difficulty', '').lower() == difficulty.lower()
            ]
        
        # Get user-specific recommendations if user_id provided
        if user_id:
            user = get_user_by_id(user_id)
            if user:
                try:
                    # Get adaptive sequence based on user
                    recommended_challenges = get_adaptive_challenge_sequence(
                        user, category, count=limit
                    )
                    if recommended_challenges:
                        filtered_challenges = recommended_challenges
                except Exception as e:
                    print(f"Error getting adaptive challenges: {e}")
        
        # Apply pagination
        total_count = len(filtered_challenges)
        paginated_challenges = filtered_challenges[offset:offset + limit]
        
        # Format challenges for response
        formatted_challenges = []
        for challenge in paginated_challenges:
            formatted_challenge = {
                'id': challenge['id'],
                'category': challenge['category'],
                'difficulty': challenge.get('difficulty', 'beginner'),
                'scenario': challenge['scenario'],
                'question': challenge['question'],
                'score_weight': challenge.get('score_weight', 100),
                'type': challenge.get('type', 'unknown'),
                'interactive_demo': challenge.get('interactive_demo', False)
            }
            
            # Add payload for non-sensitive challenges or if explicitly requested
            show_payload = request.args.get('show_payload', 'false').lower() == 'true'
            if show_payload:
                formatted_challenge['payload'] = challenge.get('payload', '')
            
            formatted_challenges.append(formatted_challenge)
        
        return jsonify({
            'success': True,
            'total_count': total_count,
            'challenges': formatted_challenges,
            'pagination': {
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < total_count
            }
        }), 200
        
    except Exception as e:
        print(f"Error in list_available_challenges: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return fallback challenges
        fallbacks = [
            get_fallback_challenge('beginner'),
            get_fallback_challenge('intermediate'),
            get_fallback_challenge('advanced')
        ]
        
        return jsonify({
            'success': True,
            'total_count': len(fallbacks),
            'challenges': fallbacks,
            'pagination': {
                'limit': 20,
                'offset': 0,
                'has_more': False
            }
        }), 200


@challenge_bp.route('/categories', methods=['GET'])
def get_challenge_categories():
    """Get available challenge categories with statistics."""
    try:
        from app.models.challenge_model import get_challenge_statistics
        
        stats = get_challenge_statistics()
        
        categories = []
        for category, count in stats.get('by_category', {}).items():
            categories.append({
                'name': category,
                'display_name': category.replace('_', ' ').title(),
                'count': count,
                'description': get_category_description(category)
            })
        
        return jsonify({
            'success': True,
            'categories': categories,
            'total_challenges': stats.get('total', 0)
        }), 200
        
    except Exception as e:
        print(f"Error getting challenge categories: {e}")
        # Fallback categories
        categories = [
            {
                'name': 'SQL Injection',
                'display_name': 'SQL Injection',
                'count': 10,
                'description': 'Learn to identify and exploit SQL injection vulnerabilities'
            },
            {
                'name': 'Cross-Site Scripting (XSS)',
                'display_name': 'Cross-Site Scripting',
                'count': 8,
                'description': 'Master XSS attack vectors and prevention techniques'
            }
        ]
        
        return jsonify({
            'success': True,
            'categories': categories,
            'total_challenges': 18
        }), 200


@challenge_bp.route('/progress/<user_id>', methods=['GET'])
def get_user_challenge_progress(user_id):
    """Get detailed challenge progress for a user."""
    try:
        user = get_user_by_id(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user analytics
        from app.models.analytics_model import get_user_learning_analytics
        analytics = get_user_learning_analytics(user_id)
        
        if not analytics:
            return jsonify({
                'success': True,
                'user_id': user_id,
                'progress': {
                    'completed_challenges': 0,
                    'total_attempts': 0,
                    'success_rate': 0,
                    'category_progress': {}
                }
            }), 200
        
        # Get challenge attempts
        from app.models.challenge_model import get_user_challenge_attempts
        recent_attempts = get_user_challenge_attempts(user_id, limit=20)
        
        progress_data = {
            'user_id': user_id,
            'progress': {
                'completed_challenges': analytics.get('challenges_completed', 0),
                'total_attempts': analytics.get('total_attempts', 0),
                'successful_attempts': analytics.get('successful_attempts', 0),
                'success_rate': analytics.get('success_rate', 0),
                'current_level': analytics.get('level', 1),
                'current_score': analytics.get('score', 0),
                'category_progress': analytics.get('category_performance', {}),
                'learning_velocity': analytics.get('learning_velocity', 0),
                'recent_performance': analytics.get('recent_performance', 0)
            },
            'recent_attempts': recent_attempts,
            'achievements': analytics.get('achievements', []),
            'last_activity': analytics.get('last_activity')
        }
        
        return jsonify({
            'success': True,
            **progress_data
        }), 200
        
    except Exception as e:
        print(f"Error getting user challenge progress: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get progress data'
        }), 500


def get_category_description(category):
    """Get description for challenge category."""
    descriptions = {
        'sql_injection': 'Learn to identify and exploit SQL injection vulnerabilities in web applications',
        'xss': 'Master Cross-Site Scripting (XSS) attack vectors and prevention techniques',
        'command_injection': 'Understand command injection attacks and secure coding practices',
        'authentication': 'Explore authentication bypass techniques and security measures',
        'csrf': 'Learn about Cross-Site Request Forgery attacks and countermeasures'
    }
    
    return descriptions.get(category.lower(), 'Security challenge category')


def get_fallback_challenge(difficulty="beginner"):
    """Return a hardcoded challenge for presentation purposes."""
    fallback_challenges = {
        "beginner": {
            'id': 'fallback1',
            'category': 'SQL Injection',
            'difficulty': 'Beginner',
            'scenario': 'Login form that checks username and password without proper input validation.',
            'question': 'What would this payload do in a vulnerable system?',
            'payload': "' OR '1'='1' --",
            'hint': 'This makes the WHERE clause always true, bypassing authentication.',
            'score_weight': 10
        },
        "intermediate": {
            'id': 'fallback2',
            'category': 'SQL Injection',
            'difficulty': 'Intermediate',
            'scenario': 'A search field where input is directly concatenated into SQL queries.',
            'question': 'What would this payload attempt to do if successful?',
            'payload': "; DROP TABLE users; --",
            'hint': 'The semicolon separates multiple SQL statements, allowing dangerous operations.',
            'score_weight': 20
        },
        "advanced": {
            'id': 'fallback3',
            'category': 'SQL Injection',
            'difficulty': 'Advanced',
            'scenario': 'Product search function that displays results from a database query.',
            'question': 'How does this attack attempt to extract sensitive information?',
            'payload': "' UNION SELECT username, password FROM users --",
            'hint': 'UNION combines the results of two queries, allowing access to other tables.',
            'score_weight': 30
        }
    }

    difficulty = difficulty.lower()
    if difficulty not in fallback_challenges:
        difficulty = "beginner"

    return fallback_challenges[difficulty]
