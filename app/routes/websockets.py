"""
WebSocket routes for real-time progress tracking
"""

from flask import request, session
from flask_socketio import emit, join_room, leave_room, rooms
from datetime import datetime
import json
from app import socketio
from app.models.progress import UserProgress
from app.models.analytics import Analytics

# Active users tracking
active_users = {}
live_stats = {
    'active_users': 0,
    'total_completions': 0,
    'recent_activities': []
}

@socketio.on('connect', namespace='/progress')
def handle_connect():
    """Handle WebSocket connection for progress tracking"""
    user_id = request.args.get('user_id', 'anonymous')
    session_id = request.sid
    
    # Track active user
    active_users[session_id] = {
        'user_id': user_id,
        'connected_at': datetime.utcnow(),
        'last_activity': datetime.utcnow()
    }
    
    # Join user-specific room
    join_room(f'user_{user_id}')
    
    # Update live stats
    live_stats['active_users'] = len(active_users)
    
    # Send initial data to connected user
    emit('progress_update', {
        'type': 'connection_established',
        'user_id': user_id,
        'timestamp': datetime.utcnow().isoformat()
    })
    
    # Broadcast updated stats to all users
    emit('live_stats', {
        'type': 'live_stats',
        'stats': live_stats
    }, broadcast=True)
    
    print(f"User {user_id} connected to progress tracking")

@socketio.on('disconnect', namespace='/progress')
def handle_disconnect():
    """Handle WebSocket disconnection"""
    session_id = request.sid
    
    if session_id in active_users:
        user_id = active_users[session_id]['user_id']
        del active_users[session_id]
        
        # Leave user room
        leave_room(f'user_{user_id}')
        
        # Update live stats
        live_stats['active_users'] = len(active_users)
        
        # Broadcast updated stats
        emit('live_stats', {
            'type': 'live_stats',
            'stats': live_stats
        }, broadcast=True)
        
        print(f"User {user_id} disconnected from progress tracking")

@socketio.on('challenge_progress', namespace='/progress')
def handle_challenge_progress(data):
    """Handle challenge progress updates"""
    try:
        user_id = data.get('userId', 'anonymous')
        challenge_type = data.get('challengeType')
        progress = data.get('progress', 0)
        score = data.get('score', 0)
        timestamp = datetime.utcnow()
        
        # Update user's last activity
        session_id = request.sid
        if session_id in active_users:
            active_users[session_id]['last_activity'] = timestamp
        
        # Store progress in database (if models exist)
        try:
            user_progress = UserProgress.query.filter_by(
                user_id=user_id, 
                challenge_type=challenge_type
            ).first()
            
            if user_progress:
                user_progress.progress = progress
                user_progress.score = score
                user_progress.last_updated = timestamp
            else:
                user_progress = UserProgress(
                    user_id=user_id,
                    challenge_type=challenge_type,
                    progress=progress,
                    score=score,
                    last_updated=timestamp
                )
                db.session.add(user_progress)
            
            db.session.commit()
        except Exception as e:
            print(f"Database error: {e}")
        
        # Add to recent activities
        activity = {
            'user_id': user_id,
            'type': 'progress_update',
            'challenge_type': challenge_type,
            'progress': progress,
            'score': score,
            'timestamp': timestamp.isoformat()
        }
        
        live_stats['recent_activities'].insert(0, activity)
        # Keep only last 10 activities
        live_stats['recent_activities'] = live_stats['recent_activities'][:10]
        
        # Emit progress update to user's room
        emit('progress_update', {
            'type': 'progress_update',
            'challengeType': challenge_type,
            'progress': progress,
            'score': score,
            'timestamp': timestamp.isoformat()
        }, room=f'user_{user_id}')
        
        # Check for achievements
        achievements = check_achievements(user_id, challenge_type, score)
        for achievement in achievements:
            emit('achievement_unlocked', {
                'type': 'achievement_unlocked',
                'achievement': achievement
            }, room=f'user_{user_id}')
        
        print(f"Progress update: {user_id} - {challenge_type}: {progress}% ({score} points)")
        
    except Exception as e:
        print(f"Error handling challenge progress: {e}")
        emit('error', {'message': 'Failed to process progress update'})

@socketio.on('challenge_completion', namespace='/progress')
def handle_challenge_completion(data):
    """Handle challenge completion"""
    try:
        user_id = data.get('userId', 'anonymous')
        challenge_type = data.get('challengeType')
        final_score = data.get('finalScore', 0)
        timestamp = datetime.utcnow()
        
        # Update completion stats
        live_stats['total_completions'] += 1
        
        # Store completion in database
        try:
            analytics = Analytics(
                user_id=user_id,
                event_type='challenge_completion',
                challenge_type=challenge_type,
                score=final_score,
                timestamp=timestamp
            )
            db.session.add(analytics)
            db.session.commit()
        except Exception as e:
            print(f"Database error: {e}")
        
        # Add to recent activities
        activity = {
            'user_id': user_id,
            'type': 'challenge_completion',
            'challenge_type': challenge_type,
            'final_score': final_score,
            'timestamp': timestamp.isoformat()
        }
        
        live_stats['recent_activities'].insert(0, activity)
        live_stats['recent_activities'] = live_stats['recent_activities'][:10]
        
        # Emit completion notification
        emit('challenge_completion', {
            'type': 'challenge_completion',
            'challengeType': challenge_type,
            'finalScore': final_score,
            'timestamp': timestamp.isoformat()
        }, room=f'user_{user_id}')
        
        # Broadcast updated stats
        emit('live_stats', {
            'type': 'live_stats',
            'stats': live_stats
        }, broadcast=True)
        
        # Check for completion achievements
        achievements = check_completion_achievements(user_id, challenge_type, final_score)
        for achievement in achievements:
            emit('achievement_unlocked', {
                'type': 'achievement_unlocked',
                'achievement': achievement
            }, room=f'user_{user_id}')
        
        print(f"Challenge completed: {user_id} - {challenge_type} - {final_score} points")
        
    except Exception as e:
        print(f"Error handling challenge completion: {e}")
        emit('error', {'message': 'Failed to process completion'})

@socketio.on('learning_progress', namespace='/progress')
def handle_learning_progress(data):
    """Handle learning module progress updates"""
    try:
        user_id = data.get('userId', 'anonymous')
        module_id = data.get('moduleId')
        progress = data.get('progress', 0)
        time_spent = data.get('timeSpent', 0)
        timestamp = datetime.utcnow()
        
        # Update user's last activity
        session_id = request.sid
        if session_id in active_users:
            active_users[session_id]['last_activity'] = timestamp
        
        # Store learning progress (if models exist)
        try:
            # This would be implemented with proper learning progress models
            pass
        except Exception as e:
            print(f"Database error: {e}")
        
        # Emit progress update
        emit('learning_progress_update', {
            'type': 'learning_progress_update',
            'moduleId': module_id,
            'progress': progress,
            'timeSpent': time_spent,
            'timestamp': timestamp.isoformat()
        }, room=f'user_{user_id}')
        
        print(f"Learning progress: {user_id} - {module_id}: {progress}%")
        
    except Exception as e:
        print(f"Error handling learning progress: {e}")
        emit('error', {'message': 'Failed to process learning progress'})

@socketio.on('get_leaderboard', namespace='/progress')
def handle_leaderboard_request():
    """Handle leaderboard data request"""
    try:
        # Generate mock leaderboard data
        leaderboard = generate_leaderboard()
        
        emit('leaderboard_update', {
            'type': 'leaderboard_update',
            'leaderboard': leaderboard
        })
        
    except Exception as e:
        print(f"Error generating leaderboard: {e}")
        emit('error', {'message': 'Failed to get leaderboard'})

def check_achievements(user_id, challenge_type, score):
    """Check for new achievements based on progress"""
    achievements = []
    
    # Achievement definitions
    achievement_definitions = {
        'first_challenge': {
            'name': 'First Steps',
            'description': 'Complete your first challenge',
            'condition': lambda: True  # Always trigger on first completion
        },
        'perfect_score': {
            'name': 'Perfect Score',
            'description': 'Score 100 points in any challenge',
            'condition': lambda: score >= 100
        },
        'sql_master': {
            'name': 'SQL Injection Master',
            'description': 'Complete SQL injection challenge with high score',
            'condition': lambda: challenge_type == 'sql_injection' and score >= 80
        },
        'xss_expert': {
            'name': 'XSS Expert',
            'description': 'Complete XSS challenge with high score',
            'condition': lambda: challenge_type == 'xss' and score >= 80
        }
    }
    
    # Check each achievement
    for achievement_id, achievement in achievement_definitions.items():
        if achievement['condition']() and not user_has_achievement(user_id, achievement_id):
            achievements.append({
                'id': achievement_id,
                'name': achievement['name'],
                'description': achievement['description'],
                'unlocked_at': datetime.utcnow().isoformat()
            })
            
            # Store achievement (if models exist)
            try:
                # This would store in database
                pass
            except Exception as e:
                print(f"Error storing achievement: {e}")
    
    return achievements

def check_completion_achievements(user_id, challenge_type, final_score):
    """Check for achievements triggered by challenge completion"""
    achievements = []
    
    # Get user's completed challenges count
    completed_challenges = get_user_completed_challenges(user_id)
    
    if len(completed_challenges) == 1:
        achievements.append({
            'id': 'first_completion',
            'name': 'Getting Started',
            'description': 'Complete your first challenge',
            'unlocked_at': datetime.utcnow().isoformat()
        })
    
    if len(completed_challenges) >= 4:
        achievements.append({
            'id': 'security_expert',
            'name': 'Security Expert',
            'description': 'Complete all challenge types',
            'unlocked_at': datetime.utcnow().isoformat()
        })
    
    return achievements

def user_has_achievement(user_id, achievement_id):
    """Check if user already has this achievement"""
    # This would check database for existing achievements
    # For now, return False to allow achievements
    return False

def get_user_completed_challenges(user_id):
    """Get list of challenges completed by user"""
    # This would query database for completed challenges
    # For now, return mock data
    return ['sql_injection', 'xss']

def generate_leaderboard():
    """Generate leaderboard data"""
    # This would query database for top users
    # For now, return mock data
    return [
        {'user_id': 'user_123', 'username': 'SecurityPro', 'total_score': 850, 'challenges_completed': 4},
        {'user_id': 'user_456', 'username': 'HackerX', 'total_score': 720, 'challenges_completed': 3},
        {'user_id': 'user_789', 'username': 'CyberNinja', 'total_score': 680, 'challenges_completed': 3},
        {'user_id': 'user_101', 'username': 'SecureCodex', 'total_score': 550, 'challenges_completed': 2},
        {'user_id': 'user_202', 'username': 'VulnHunter', 'total_score': 420, 'challenges_completed': 2}
    ]

# Periodic task to broadcast live stats (would be implemented with background task)
def broadcast_live_stats():
    """Broadcast current live statistics to all connected users"""
    socketio.emit('live_stats', {
        'type': 'live_stats',
        'stats': live_stats
    }, namespace='/progress')