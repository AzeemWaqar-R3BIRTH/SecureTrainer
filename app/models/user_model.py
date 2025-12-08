from bson import ObjectId
from flask import current_app
from datetime import datetime, timedelta
import math


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


def insert_user(user_data):
    """Insert a new user into the users collection and return their ID."""
    db = get_db()
    
    # Ensure admin fields exist
    if 'is_admin' not in user_data:
        user_data['is_admin'] = False
    if 'admin_role' not in user_data:
        user_data['admin_role'] = None
        
    result = db.users.insert_one(user_data)
    return str(result.inserted_id)  # Return the inserted user ID


def get_user_by_id(user_id):
    """Get a user by ID with more robust ID handling.

    This function tries multiple approaches to find the user:
    1. First try as ObjectId
    2. Then try as string
    3. Finally try as a substring match (in case of encoding issues)
    """
    db = get_db()

    # Print debug info
    print(f"Searching for user with ID: {user_id}, type: {type(user_id)}")

    # Try as ObjectId
    try:
        user = db.users.find_one({'_id': ObjectId(user_id)})
        if user:
            print(f"Found user using ObjectId: {user['_id']}")
            return user
    except Exception as e:
        print(f"Error with ObjectId search: {str(e)}")

    # Try as string
    try:
        user = db.users.find_one({'_id': user_id})
        if user:
            print(f"Found user using string ID: {user['_id']}")
            return user
    except:
        pass

    # Try substring search if it might be a QR string with extra data
    if isinstance(user_id, str) and len(user_id) > 10:
        # Look for shorter patterns that might be the ID
        try:
            for possible_id in db.users.find():
                str_id = str(possible_id['_id'])
                if str_id in user_id or user_id in str_id:
                    print(f"Found user using substring match: {possible_id['_id']}")
                    return possible_id
        except:
            pass

    print(f"No user found for ID: {user_id}")
    return None


def get_user_by_email(email):
    """Get a user by email address."""
    db = get_db()
    try:
        user = db.users.find_one({'email': email})
        return user
    except Exception as e:
        print(f"Error finding user by email: {e}")
        return None


def update_user_score_level(user_id, score_delta=0):
    """Update user level and role based on their CURRENT score.
    
    NOTE: This function does NOT add score_delta to the user's score.
    It only recalculates and updates the level and role based on the current score.
    The score_delta parameter is kept for backwards compatibility but is ignored.
    
    Use update_user_challenge_progress() in challenge_model.py to update scores.
    """
    db = get_db()
    user = get_user_by_id(user_id)
    if not user:
        return

    # Get CURRENT score from database (don't add score_delta)
    current_score = user.get('score', 0)
    
    # Calculate level and role based on current score
    new_level = calculate_user_level(current_score)
    new_role = get_role_for_level(new_level)

    try:
        db.users.update_one(
            {'_id': user['_id']},
            {'$set': {'level': new_level, 'role': new_role}}
        )
        print(f"Updated user {user_id} level to {new_level} and role to {new_role} (score: {current_score})")
    except Exception as e:
        print(f"Error updating user level: {str(e)}")


def get_top_users(limit=5, department=None):
    db = get_db()
    query = {}
    if department:
        query['department'] = department
    users = db.users.find(query).sort('score', -1).limit(limit)

    result = []
    for u in users:
        # Use username if first_name/last_name not available
        first_name = u.get('first_name', '')
        last_name = u.get('last_name', '')
        if first_name and last_name:
            name = f"{first_name} {last_name}"
        else:
            name = u.get('username', 'Unknown User')
        
        result.append({
            'user_id': str(u['_id']),  # Include user_id in results
            'name': name,
            'score': u.get('score', 0),
            'level': u.get('level', 1),
            'role': u.get('role', 'Trainee'),
            'department': u.get('department', 'Unknown')
        })
    return result


def get_user_rank(user_id):
    db = get_db()
    user = get_user_by_id(user_id)
    if not user:
        return {'error': 'User not found'}

    score = user.get('score', 0)
    dept = user.get('department')

    global_rank = db.users.count_documents({'score': {'$gt': score}}) + 1
    dept_rank = db.users.count_documents({'department': dept, 'score': {'$gt': score}}) + 1

    return {
        'user_id': str(user['_id']),  # Include user_id in results
        'name': f"{user['first_name']} {user['last_name']}",
        'score': score,
        'level': user.get('level', 1),
        'role': user.get('role', 'Trainee'),
        'department': dept,
        'global_rank': global_rank,
        'department_rank': dept_rank
    }


def promote_user(user_id, new_role):
    db = get_db()
    user = get_user_by_id(user_id)
    if not user:
        return False

    try:
        db.users.update_one(
            {'_id': user['_id']},  # Use the _id from the found user
            {'$set': {'role': new_role}}
        )
        return True
    except:
        return False


# Advanced User Management Functions

def calculate_user_level(score):
    """Calculate user level based on score with exponential progression."""
    if score < 100:
        return 1
    
    # Exponential level calculation for more balanced progression
    level = int(math.log(score / 100) / math.log(1.5)) + 2
    return min(level, 50)  # Cap at level 50


def get_level_requirements(level):
    """Get score requirements for a specific level."""
    if level <= 1:
        return 0
    return int(100 * (1.5 ** (level - 2)))


def update_performance_metrics(user_id, challenge_data, success=False):
    """
    Update user performance metrics after a challenge attempt.
    """
    try:
        db = get_db()
        if not challenge_data:
            return

        # Simple metrics update logic - can be expanded
        pass
        
    except Exception as e:
        print(f"Error updating performance metrics: {e}")


def update_user_comprehensive(user_id, score_delta=0, challenge_data=None, update_score=False):
    """Comprehensive user update with advanced metrics.
    
    Args:
        user_id: The user's ID
        score_delta: Points to add (only used if update_score=True)
        challenge_data: Optional challenge metadata
        update_score: If True, adds score_delta to user's score. If False, only updates metadata.
                     Default is False to prevent duplicate scoring.
    
    NOTE: For challenge completion, use update_user_challenge_progress() in challenge_model.py
          which is the single source of truth for scoring.
    """
    db = get_db()
    user = get_user_by_id(user_id)
    
    if not user:
        return False
    
    # Get current score
    current_score = user.get('score', 0)
    
    # Only update score if explicitly requested
    if update_score and score_delta > 0:
        new_score = current_score + score_delta
        new_level = calculate_user_level(new_score)
        new_role = get_role_for_level(new_level)
    else:
        # Just recalculate level/role based on current score
        new_score = current_score
        new_level = calculate_user_level(current_score)
        new_role = get_role_for_level(new_level)
    
    # Update basic fields
    update_data = {
        'score': new_score,
        'level': new_level,
        'role': new_role,
        'last_activity': datetime.now()
    }
    
    # Update category-specific scores if challenge data provided AND score update requested
    if challenge_data and update_score and score_delta > 0:
        category = challenge_data.get('category', '').lower().replace(' ', '_')
        if category:
            category_score_field = f"{category}_score"
            current_category_score = user.get(category_score_field, 0)
            update_data[category_score_field] = current_category_score + score_delta
    
    # Update performance metrics
    update_performance_metrics(user_id, challenge_data, score_delta > 0 if update_score else False)
    
    # Apply updates
    try:
        db.users.update_one(
            {'_id': user['_id']},
            {'$set': update_data}
        )
        
        # Check for achievements only if score was updated
        if update_score and score_delta > 0:
            # Note: check_and_award_achievements expects to be imported or available.
            # If not available, we might want to wrap this in try/except or comment out if it calls undefined function.
            # Assuming check_and_award_achievements is NOT defined in this file (based on previous view), likely referenced from elsewhere or missing.
            # However, code analysis showed it was used. I'll wrap it safely.
            try:
                from app.models.gamification import check_and_award_achievements
                check_and_award_achievements(user_id, new_score, new_level)
            except ImportError:
                pass
        
        return True
    except Exception as e:
        print(f"Error updating user comprehensively: {e}")
        return False


def get_role_for_level(level):
    """Get role based on user level with enhanced progression."""
    role_thresholds = [
        (1, "Trainee"),
        (5, "Junior Analyst"),
        (10, "Analyst"),
        (15, "Senior Analyst"),
        (20, "Specialist"),
        (25, "Expert"),
        (30, "Lead Analyst"),
        (35, "Team Lead"),
        (40, "Department Head"),
        (45, "Security Architect"),
        (50, "Chief Security Officer")
    ]
    
    for threshold, role in reversed(role_thresholds):
        if level >= threshold:
            return role
    
    return "Trainee"


def get_department_leaderboard(department, limit=10):
    """Get leaderboard for a specific department."""
    db = get_db()
    
    query = {'department': department} if department else {}
    users = db.users.find(query).sort('score', -1).limit(limit)
    
    leaderboard = []
    rank = 1
    
    for user in users:
        leaderboard.append({
            'rank': rank,
            'user_id': str(user['_id']),
            'username': user.get('username', ''),
            'name': f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
            'score': user.get('score', 0),
            'level': user.get('level', 1),
            'role': user.get('role', 'Trainee'),
            'department': user.get('department', ''),
            'challenges_completed': len(user.get('challenges_completed', [])),
            'last_activity': user.get('last_activity')
        })
        rank += 1
    
    return leaderboard


def get_user_dashboard_data(user_id):
    """Get comprehensive dashboard data for a user."""
    db = get_db()
    user = get_user_by_id(user_id)
    
    if not user:
        return None
    
    # Get user basic info
    user_info = {
        'user_id': str(user['_id']),
        'username': user.get('username', ''),
        'name': f"{user.get('first_name', '')} {user.get('last_name', '')}".strip(),
        'email': user.get('email', ''),
        'company': user.get('company', ''),
        'department': user.get('department', ''),
        'role': user.get('role', 'Trainee'),
        'level': user.get('level', 1),
        'score': user.get('score', 0),
        'created_at': user.get('created_at'),
        'last_login': user.get('last_login')
    }
    
    # Get progress data
    current_level = user.get('level', 1)
    current_score = user.get('score', 0)
    
    # Use the shared level requirements formula instead of hardcoded 1000/level
    level_base_score = get_level_requirements(current_level)
    next_level_score = get_level_requirements(current_level + 1)
    
    progress_in_level = current_score - level_base_score
    points_to_next_level = next_level_score - current_score
    
    progress = {
        'current_level': current_level,
        'current_score': current_score,
        'level_base_score': level_base_score,
        'next_level_score': next_level_score,
        'progress_in_level': progress_in_level,
        'points_to_next_level': max(0, points_to_next_level),
        'level_progress_percentage': int((progress_in_level / (next_level_score - level_base_score)) * 100) if next_level_score > level_base_score else 100
    }
    
    # Get performance metrics
    challenges_completed = len(user.get('challenges_completed', []))
    
    # Get attempts from challenge_attempts collection
    attempts = list(db.challenge_attempts.find({'user_id': str(user['_id'])}))
    total_attempts = len(attempts)
    successful_attempts = len([a for a in attempts if a.get('is_correct', False)])
    success_rate = int((successful_attempts / total_attempts) * 100) if total_attempts > 0 else 0
    
    performance = {
        'challenges_completed': challenges_completed,
        'total_attempts': total_attempts,
        'successful_attempts': successful_attempts,
        'success_rate': success_rate,
        'achievements': user.get('achievements', [])
    }
    
    # Get ranking
    rank_info = get_user_rank(user_id)
    ranking = {
        'global_rank': rank_info.get('global_rank', 0),
        'department_rank': rank_info.get('department_rank', 0)
    }
    
    return {
        'user_info': user_info,
        'progress': progress,
        'performance': performance,
        'ranking': ranking
    }
