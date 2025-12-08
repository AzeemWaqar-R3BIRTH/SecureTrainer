from flask import current_app
from bson import ObjectId
from datetime import datetime, timedelta
import json


def get_db():
    """Get database connection from Flask app context."""
    try:
        return current_app.config['MONGO_CLIENT'].get_database()
    except Exception as e:
        # Fallback for direct access scenarios
        from pymongo import MongoClient
        import os
        mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/securetrainer')
        client = MongoClient(mongo_uri)
        return client.securetrainer

def log_event(user_id, challenge_id, event_type, metadata=None):
    """Legacy function for backwards compatibility."""
    db = get_db()
    log = {
        'user_id': user_id,
        'challenge_id': challenge_id,
        'event_type': event_type,
        'metadata': metadata or {},
        'timestamp': datetime.utcnow()
    }
    db.analytics.insert_one(log)


def record_user_activity(user_id, activity_type, details=None):
    """Record user activity for analytics."""
    db = get_db()
    
    activity_data = {
        'user_id': user_id,
        'activity_type': activity_type,
        'details': details or {},
        'timestamp': datetime.now(),
        'session_id': None  # Can be populated from Flask session
    }
    
    result = db.user_activities.insert_one(activity_data)
    return str(result.inserted_id)

def get_challenge_logs(challenge_id):
    """Legacy function for backwards compatibility."""
    db = get_db()
    logs = db.analytics.find({'challenge_id': challenge_id})
    return [{
        'user_id': log['user_id'],
        'event': log['event_type'],
        'meta': log['metadata'],
        'time': log['timestamp']
    } for log in logs]


def export_analytics_for_csv():
    """Legacy function for backwards compatibility."""
    db = get_db()
    logs = db.analytics.find()

    processed = []
    for log in logs:
        processed.append({
            'user_id': log['user_id'],
            'challenge_id': log['challenge_id'],
            'event_type': log['event_type'],
            'timestamp': log['timestamp'].isoformat(),
            'hint_level': log.get('metadata', {}).get('level', ''),
            'meta_info': str(log.get('metadata', {}))
        })
    return processed


# New Comprehensive Analytics Functions

def get_user_learning_analytics(user_id):
    """Get comprehensive learning analytics for a user."""
    db = get_db()
    
    # Get user basic info
    user = db.users.find_one({'_id': ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id})
    if not user:
        return None
    
    # Get challenge attempts
    attempts = list(db.challenge_attempts.find({'user_id': user_id}).sort('attempt_time', 1))
    
    # Calculate metrics
    total_attempts = len(attempts)
    successful_attempts = len([a for a in attempts if a['is_correct']])
    success_rate = (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0
    
    # Category performance
    category_stats = {}
    for attempt in attempts:
        category = attempt.get('category', 'unknown')
        if category not in category_stats:
            category_stats[category] = {'total': 0, 'correct': 0}
        category_stats[category]['total'] += 1
        if attempt['is_correct']:
            category_stats[category]['correct'] += 1
    
    # Calculate category success rates
    for category in category_stats:
        stats = category_stats[category]
        stats['success_rate'] = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
    
    # Learning velocity (challenges completed per day)
    if attempts:
        first_attempt = attempts[0]['attempt_time']
        days_active = (datetime.now() - first_attempt).days + 1
        challenges_per_day = successful_attempts / days_active
    else:
        challenges_per_day = 0
    
    # Recent performance (last 7 days)
    week_ago = datetime.now() - timedelta(days=7)
    recent_attempts = [a for a in attempts if a['attempt_time'] >= week_ago]
    recent_success_rate = (len([a for a in recent_attempts if a['is_correct']]) / len(recent_attempts) * 100) if recent_attempts else 0
    
    analytics = {
        'user_id': str(user['_id']),
        'username': user['username'],
        'level': user.get('level', 1),
        'score': user.get('score', 0),
        'role': user.get('role', 'Trainee'),
        'total_attempts': total_attempts,
        'successful_attempts': successful_attempts,
        'success_rate': success_rate,
        'category_performance': category_stats,
        'learning_velocity': challenges_per_day,
        'recent_performance': recent_success_rate,
        'challenges_completed': len(user.get('challenges_completed', [])),
        'achievements': user.get('achievements', []),
        'last_activity': attempts[-1]['attempt_time'] if attempts else None
    }
    
    return analytics


def get_department_analytics(department):
    """Get analytics for a specific department."""
    db = get_db()
    
    # Get all users in department
    users = list(db.users.find({'department': department}))
    user_ids = [str(user['_id']) for user in users]
    
    if not users:
        return None
    
    # Get all attempts for department users
    attempts = list(db.challenge_attempts.find({'user_id': {'$in': user_ids}}))
    
    # Calculate department metrics
    total_users = len(users)
    active_users = len(set(attempt['user_id'] for attempt in attempts))
    total_score = sum(user.get('score', 0) for user in users)
    avg_score = total_score / total_users if total_users > 0 else 0
    
    total_attempts = len(attempts)
    successful_attempts = len([a for a in attempts if a['is_correct']])
    department_success_rate = (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0
    
    # Level distribution
    level_distribution = {}
    for user in users:
        level = user.get('level', 1)
        level_distribution[level] = level_distribution.get(level, 0) + 1
    
    # Category performance
    category_stats = {}
    for attempt in attempts:
        category = attempt.get('category', 'unknown')
        if category not in category_stats:
            category_stats[category] = {'total': 0, 'correct': 0}
        category_stats[category]['total'] += 1
        if attempt['is_correct']:
            category_stats[category]['correct'] += 1
    
    # Calculate category success rates
    for category in category_stats:
        stats = category_stats[category]
        stats['success_rate'] = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
    
    analytics = {
        'department': department,
        'total_users': total_users,
        'active_users': active_users,
        'total_score': total_score,
        'average_score': avg_score,
        'total_attempts': total_attempts,
        'successful_attempts': successful_attempts,
        'success_rate': department_success_rate,
        'level_distribution': level_distribution,
        'category_performance': category_stats,
        'top_performers': get_top_department_users(department, limit=5),
        'last_updated': datetime.now()
    }
    
    return analytics


def get_learning_patterns(user_id):
    """Analyze user learning patterns for AI recommendations."""
    db = get_db()
    
    attempts = list(db.challenge_attempts.find({'user_id': user_id}).sort('attempt_time', 1))
    
    if not attempts:
        return {
            'preferred_categories': [],
            'optimal_difficulty': 'beginner',
            'learning_style': 'unknown',
            'peak_performance_time': None,
            'hint_dependency': 'low'
        }
    
    # Analyze preferred categories (highest success rate)
    category_performance = {}
    for attempt in attempts:
        category = attempt.get('category', 'unknown')
        if category not in category_performance:
            category_performance[category] = {'total': 0, 'correct': 0}
        category_performance[category]['total'] += 1
        if attempt['is_correct']:
            category_performance[category]['correct'] += 1
    
    # Calculate success rates and find preferred categories
    preferred_categories = []
    for category, stats in category_performance.items():
        success_rate = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
        if success_rate >= 0.7:  # 70% success rate threshold
            preferred_categories.append(category)
    
    # Determine optimal difficulty
    difficulty_performance = {}
    for attempt in attempts:
        difficulty = attempt.get('difficulty_level', 'beginner')
        if difficulty not in difficulty_performance:
            difficulty_performance[difficulty] = {'total': 0, 'correct': 0}
        difficulty_performance[difficulty]['total'] += 1
        if attempt['is_correct']:
            difficulty_performance[difficulty]['correct'] += 1
    
    optimal_difficulty = 'beginner'
    best_rate = 0
    for difficulty, stats in difficulty_performance.items():
        success_rate = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
        if success_rate > best_rate and stats['total'] >= 3:  # Minimum 3 attempts
            best_rate = success_rate
            optimal_difficulty = difficulty
    
    # Analyze learning style based on completion times
    completion_times = [a['completion_time'] for a in attempts if a['is_correct']]
    avg_completion_time = sum(completion_times) / len(completion_times) if completion_times else 0
    
    if avg_completion_time < 30:
        learning_style = 'fast_learner'
    elif avg_completion_time < 120:
        learning_style = 'methodical'
    else:
        learning_style = 'thorough'
    
    # Analyze hint dependency
    hint_counts = [a.get('hint_count', 0) for a in attempts]
    avg_hints = sum(hint_counts) / len(hint_counts) if hint_counts else 0
    
    if avg_hints < 1:
        hint_dependency = 'low'
    elif avg_hints < 2:
        hint_dependency = 'medium'
    else:
        hint_dependency = 'high'
    
    # Analyze peak performance time (hour of day)
    successful_attempts = [a for a in attempts if a['is_correct']]
    hour_performance = {}
    for attempt in successful_attempts:
        hour = attempt['attempt_time'].hour
        hour_performance[hour] = hour_performance.get(hour, 0) + 1
    
    peak_hour = max(hour_performance, key=hour_performance.get) if hour_performance else None
    
    patterns = {
        'preferred_categories': preferred_categories,
        'optimal_difficulty': optimal_difficulty,
        'learning_style': learning_style,
        'peak_performance_time': peak_hour,
        'hint_dependency': hint_dependency,
        'average_completion_time': avg_completion_time,
        'total_attempts': len(attempts),
        'success_rate': len(successful_attempts) / len(attempts) * 100 if attempts else 0
    }
    
    return patterns


def get_top_department_users(department, limit=5):
    """Get top performing users in a department."""
    db = get_db()
    
    users = list(db.users.find({'department': department}).sort('score', -1).limit(limit))
    
    top_users = []
    for user in users:
        top_users.append({
            'user_id': str(user['_id']),
            'username': user['username'],
            'name': f"{user.get('first_name', '')} {user.get('last_name', '')}",
            'score': user.get('score', 0),
            'level': user.get('level', 1),
            'role': user.get('role', 'Trainee'),
            'challenges_completed': len(user.get('challenges_completed', []))
        })
    
def get_dashboard_analytics(user_id):
    """Get comprehensive analytics data for dashboard display."""
    db = get_db()
    
    # Get user
    try:
        user_obj_id = ObjectId(user_id) if ObjectId.is_valid(user_id) else user_id
    except:
        user_obj_id = user_id
        
    user = db.users.find_one({'_id': user_obj_id})
    if not user:
        return None
    
    # Calculate level name and progress
    level = user.get('level', 1)
    score = user.get('score', 0)
    
    level_names = {
        1: 'Security Trainee',
        2: 'Junior Analyst', 
        3: 'Security Analyst',
        4: 'Senior Analyst',
        5: 'Security Expert',
        6: 'Security Specialist',
        7: 'Security Architect',
        8: 'Security Master',
        9: 'Elite Defender',
        10: 'Cybersecurity Guru'
    }
    
    level_name = level_names.get(level, f'Level {level}')
    
    # Calculate progress to next level using exponential formula (same as calculate_user_level)
    from app.models.user_model import get_level_requirements
    current_level_score = get_level_requirements(level)
    next_level_score = get_level_requirements(level + 1)
    points_in_current_level = score - current_level_score
    points_needed_for_next = next_level_score - current_level_score
    progress_to_next_level = min(100, int((points_in_current_level / points_needed_for_next) * 100)) if points_needed_for_next > 0 else 100
    
    # Get challenge attempts
    attempts = list(db.challenge_attempts.find({'user_id': str(user['_id'])}).sort('attempt_time', -1))
    
    # Calculate category performance
    category_performance = {}
    for attempt in attempts:
        category = attempt.get('category', 'unknown')
        if category not in category_performance:
            category_performance[category] = {'total': 0, 'correct': 0, 'completed': 0}
        category_performance[category]['total'] += 1
        if attempt['is_correct']:
            category_performance[category]['correct'] += 1
            category_performance[category]['completed'] += 1
    
    # Calculate success rates
    for category in category_performance:
        stats = category_performance[category]
        stats['success_rate'] = int((stats['correct'] / stats['total']) * 100) if stats['total'] > 0 else 0
    
    # Get recent scores for chart (last 30 days)
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_attempts = [a for a in attempts if a['attempt_time'] >= thirty_days_ago and a['is_correct']]
    
    # Group by day for chart
    daily_scores = {}
    for attempt in recent_attempts:
        date_key = attempt['attempt_time'].strftime('%Y-%m-%d')
        if date_key not in daily_scores:
            daily_scores[date_key] = 0
        daily_scores[date_key] += attempt.get('score_earned', 10)
    
    # Fill missing days with 0 and prepare chart data
    chart_labels = []
    chart_scores = []
    cumulative_score = score - sum(daily_scores.values())  # Starting score
    
    for i in range(30):
        date = thirty_days_ago + timedelta(days=i)
        date_key = date.strftime('%Y-%m-%d')
        chart_labels.append(date.strftime('%m/%d'))
        cumulative_score += daily_scores.get(date_key, 0)
        chart_scores.append(cumulative_score)
    
    # Get achievements
    achievements = user.get('achievements', [])
    
    # Get recommended topics based on performance
    recommended_topics = [
        {
            'title': 'Advanced SQL Injection',
            'description': 'Learn complex SQL injection techniques and prevention methods.',
            'slug': 'advanced-sql-injection'
        },
        {
            'title': 'Cross-Site Scripting (XSS)',
            'description': 'Understand XSS vulnerabilities and how to prevent them.',
            'slug': 'xss-prevention'
        },
        {
            'title': 'Command Injection',
            'description': 'Explore OS command injection attacks and mitigation strategies.',
            'slug': 'command-injection'
        }
    ]
    
    # Daily security tip
    tips = [
        "Always validate and sanitize user input to prevent injection attacks.",
        "Use parameterized queries to protect against SQL injection.",
        "Implement proper session management to prevent session hijacking.",
        "Keep your software and systems regularly updated with security patches.",
        "Use strong authentication mechanisms including multi-factor authentication.",
        "Regular security audits help identify vulnerabilities before attackers do.",
        "Principle of least privilege: Give users only the access they need."
    ]
    
    import random
    daily_tip = random.choice(tips)
    
    # Calculate improvement percentage (mock for now)
    improvement_percentage = min(95, max(5, len(attempts) * 2))
    
    analytics = {
        'level_name': level_name,
        'progress_to_next_level': int(progress_to_next_level),
        'current_level_score': current_level_score,
        'next_level_score': next_level_score,
        'challenges_completed': len([a for a in attempts if a['is_correct']]),
        'category_performance': category_performance,
        'chart_labels': chart_labels,
        'chart_scores': chart_scores,
        'recent_scores': [{'date': thirty_days_ago + timedelta(days=i), 'score': chart_scores[i]} for i in range(0, 30, 7)],
        'recommended_topics': recommended_topics,
        'daily_tip': daily_tip,
        'improvement_percentage': improvement_percentage
    }
    
    return analytics


def get_challenge_attempt_analytics(user_id, challenge_id):
    """Get analytics for a specific challenge attempt."""
    db = get_db()
    
    attempts = list(db.challenge_attempts.find({
        'user_id': str(user_id),
        'challenge_id': challenge_id
    }).sort('attempt_time', 1))
    
    if not attempts:
        return None
    
    analytics = {
        'total_attempts': len(attempts),
        'successful_attempts': len([a for a in attempts if a['is_correct']]),
        'average_completion_time': sum(a['completion_time'] for a in attempts if a['is_correct']) / len([a for a in attempts if a['is_correct']]) if any(a['is_correct'] for a in attempts) else 0,
        'hints_used_total': sum(a.get('hint_count', 0) for a in attempts),
        'first_attempt_time': attempts[0]['attempt_time'],
        'last_attempt_time': attempts[-1]['attempt_time'],
        'best_score': max(a.get('score_earned', 0) for a in attempts if a['is_correct']) if any(a['is_correct'] for a in attempts) else 0
    }
    
    return analytics


def get_system_analytics():
    """Get comprehensive system analytics."""
    db = get_db()
    
    try:
        # Get basic counts
        total_users = db.users.count_documents({})
        total_challenges = db.challenges.count_documents({})
        total_attempts = db.challenge_attempts.count_documents({})
        successful_attempts = db.challenge_attempts.count_documents({'is_correct': True})
        
        # Calculate overall success rate
        overall_success_rate = (successful_attempts / total_attempts * 100) if total_attempts > 0 else 0
        
        # Get active users (users who attempted challenges in last 30 days)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        active_users = len(db.challenge_attempts.distinct('user_id', {
            'attempt_time': {'$gte': thirty_days_ago}
        }))
        
        # Get category distribution
        category_pipeline = [
            {'$group': {
                '_id': '$category',
                'total_attempts': {'$sum': 1},
                'successful_attempts': {
                    '$sum': {'$cond': [{'$eq': ['$is_correct', True]}, 1, 0]}
                }
            }},
            {'$project': {
                'category': '$_id',
                'total_attempts': 1,
                'successful_attempts': 1,
                'success_rate': {
                    '$multiply': [
                        {'$divide': ['$successful_attempts', '$total_attempts']},
                        100
                    ]
                }
            }}
        ]
        
        category_stats = list(db.challenge_attempts.aggregate(category_pipeline))
        
        # Get department stats
        departments = db.users.distinct('department')
        department_count = len([d for d in departments if d])
        
        # Get difficulty distribution
        difficulty_pipeline = [
            {'$group': {
                '_id': '$difficulty_level',
                'total_attempts': {'$sum': 1},
                'successful_attempts': {
                    '$sum': {'$cond': [{'$eq': ['$is_correct', True]}, 1, 0]}
                }
            }}
        ]
        
        difficulty_stats = list(db.challenge_attempts.aggregate(difficulty_pipeline))
        
        # Get recent growth (last 7 days vs previous 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        two_weeks_ago = datetime.now() - timedelta(days=14)
        
        recent_users = db.users.count_documents({'created_at': {'$gte': week_ago}})
        previous_users = db.users.count_documents({
            'created_at': {'$gte': two_weeks_ago, '$lt': week_ago}
        })
        
        user_growth = ((recent_users - previous_users) / previous_users * 100) if previous_users > 0 else 0
        
        recent_attempts = db.challenge_attempts.count_documents({'attempt_time': {'$gte': week_ago}})
        previous_attempts = db.challenge_attempts.count_documents({
            'attempt_time': {'$gte': two_weeks_ago, '$lt': week_ago}
        })
        
        attempts_growth = ((recent_attempts - previous_attempts) / previous_attempts * 100) if previous_attempts > 0 else 0
        
        system_analytics = {
            'overview': {
                'total_users': total_users,
                'active_users': active_users,
                'total_challenges': total_challenges,
                'total_attempts': total_attempts,
                'successful_attempts': successful_attempts,
                'overall_success_rate': round(overall_success_rate, 2),
                'total_departments': department_count
            },
            'growth_metrics': {
                'user_growth_7d': round(user_growth, 2),
                'attempts_growth_7d': round(attempts_growth, 2),
                'new_users_7d': recent_users,
                'new_attempts_7d': recent_attempts
            },
            'category_performance': category_stats,
            'difficulty_distribution': difficulty_stats,
            'last_updated': datetime.now()
        }
        
        return system_analytics
        
    except Exception as e:
        print(f"Error getting system analytics: {e}")
        # Return minimal analytics on error
        return {
            'overview': {
                'total_users': 0,
                'active_users': 0,
                'total_challenges': 0,
                'total_attempts': 0,
                'successful_attempts': 0,
                'overall_success_rate': 0,
                'total_departments': 0
            },
            'growth_metrics': {
                'user_growth_7d': 0,
                'attempts_growth_7d': 0,
                'new_users_7d': 0,
                'new_attempts_7d': 0
            },
            'category_performance': [],
            'difficulty_distribution': [],
            'last_updated': datetime.now(),
            'error': str(e)
        }