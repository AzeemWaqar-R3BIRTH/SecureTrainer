# Enhanced User dashboard & statistics with server-side rendering support
from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from app.models.user_model import get_user_by_id, update_user_score_level
from app.models.analytics_model import get_dashboard_analytics
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

def get_user_from_session():
    """Get user data from session - consistent with main app."""
    if 'user_id' in session:
        from bson import ObjectId
        from app.models.user_model import get_db
        db = get_db()
        if db is not None:
            try:
                # Try ObjectId conversion first
                user_id = ObjectId(session['user_id'])
                user = db.users.find_one({'_id': user_id})
                return user
            except Exception:
                # Fallback to string
                user = db.users.find_one({'_id': session['user_id']})
                return user
    return None

@dashboard_bp.route('/', methods=['GET'])
def enhanced_dashboard():
    """Enhanced dashboard with server-side rendering and analytics."""
    user = get_user_from_session()
    if not user:
        return redirect('/login')
    
    # Get comprehensive analytics
    analytics = get_dashboard_analytics(str(user['_id']))
    
    if not analytics:
        # Fallback analytics if function fails
        analytics = {
            'level_name': 'Security Trainee',
            'progress_to_next_level': 0,
            'current_level_score': 0,
            'next_level_score': 1000,
            'challenges_completed': 0,
            'category_performance': {},
            'chart_labels': [],
            'chart_scores': [],
            'recent_scores': [],
            'recommended_topics': [],
            'daily_tip': 'Welcome to SecureTrainer! Start with our beginner challenges.',
            'improvement_percentage': 0
        }
    
    return render_template('dashboard.html', user=user, analytics=analytics)

@dashboard_bp.route('/api/<user_id>', methods=['GET'])
def get_dashboard_api(user_id):
    """API endpoint for dashboard data (legacy support)."""
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    data = {
        'username': user['username'],
        'full_name': f"{user['first_name']} {user['last_name']}",
        'department': user['department'],
        'score': user.get('score', 0),
        'level': user.get('level', 1),
        'role': user.get('role', 'Trainee'),
        'last_updated': datetime.now().isoformat()
    }
    return jsonify({'dashboard': data}), 200

@dashboard_bp.route('/refresh', methods=['GET'])
def dashboard_refresh():
    """AJAX endpoint for dashboard data refresh."""
    user = get_user_from_session()
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Get updated user data
    from app.models.user_model import get_db
    from bson import ObjectId
    db = get_db()
    updated_user = None
    
    if db is not None:
        try:
            user_id = ObjectId(str(user['_id']))
            updated_user = db.users.find_one({'_id': user_id})
        except:
            updated_user = db.users.find_one({'_id': str(user['_id'])})
    
    if updated_user:
        return jsonify({
            'success': True,
            'score': updated_user.get('score', 0),
            'level': updated_user.get('level', 1),
            'role': updated_user.get('role', 'Trainee'),
            'challenges_completed': len(updated_user.get('challenges_completed', [])),
            'last_updated': datetime.now().isoformat()
        })
    
    return jsonify({'success': False}), 500

@dashboard_bp.route('/stats/<user_id>', methods=['GET'])
def get_user_stats(user_id):
    """Get detailed user statistics for API consumption."""
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    # Get analytics data
    analytics = get_dashboard_analytics(user_id)
    
    stats = {
        'user_info': {
            'username': user['username'],
            'full_name': f"{user['first_name']} {user['last_name']}",
            'email': user['email'],
            'department': user['department'],
            'company': user['company'],
            'role': user.get('role', 'Trainee')
        },
        'performance': {
            'score': user.get('score', 0),
            'level': user.get('level', 1),
            'level_name': analytics.get('level_name', 'Security Trainee') if analytics else 'Security Trainee',
            'challenges_completed': len(user.get('challenges_completed', [])),
            'achievements': user.get('achievements', [])
        },
        'analytics': analytics or {},
        'last_updated': datetime.now().isoformat()
    }
    
    return jsonify(stats), 200
