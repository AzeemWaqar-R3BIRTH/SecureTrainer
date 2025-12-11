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


def update_user_score_level(user_id, score_delta):
    db = get_db()
    user = get_user_by_id(user_id)
    if not user:
        return

    new_score = user.get('score', 0) + score_delta
    new_level = 1 + new_score // 1000

    role_map = {
        1: "Trainee",
        2: "Junior Analyst",
        4: "Analyst",
        6: "Senior Analyst",
        8: "Lead",
        10: "Department Head"
    }

    new_role = "Trainee"
    for level, role in sorted(role_map.items()):
        if new_level >= level:
            new_role = role

    try:
        db.users.update_one(
            {'_id': user['_id']},  # Use the _id from the found user
            {'$set': {'score': new_score, 'level': new_level, 'role': new_role}}
        )
    except Exception as e:
        print(f"Error updating user score: {str(e)}")


def get_top_users(limit=5, department=None):
    db = get_db()
    query = {}
    if department:
        query['department'] = department
    users = db.users.find(query).sort('score', -1).limit(limit)

    result = []
    for u in users:
        result.append({
            'user_id': str(u['_id']),  # Include user_id in results
            'name': f"{u['first_name']} {u['last_name']}",
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


def update_user_comprehensive(user_id, score_delta, challenge_data=None):
    """Comprehensive user update with advanced metrics."""
    db = get_db()
    user = get_user_by_id(user_id)
    
    if not user:
        return False
    
    # Calculate new scores and levels
    new_score = user.get('score', 0) + score_delta
    new_level = calculate_user_level(new_score)
    new_role = get_role_for_level(new_level)
    
    # Update basic fields
    update_data = {
        'score': new_score,
        'level': new_level,
        'role': new_role,
        'last_activity': datetime.now()
    }
    
    # Update category-specific scores if challenge data provided
    if challenge_data and score_delta > 0:
        category = challenge_data.get('category', '').lower().replace(' ', '_')
        if category:
            category_score_field = f"{category}_score"
            current_category_score = user.get(category_score_field, 0)
            update_data[category_score_field] = current_category_score + score_delta
    
    # Apply updates
    try:
        db.users.update_one(
            {'_id': user['_id']},
            {'$set': update_data}
        )
        
        # Check for achievements
        check_and_award_achievements(user_id, new_score, new_level)
        
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
