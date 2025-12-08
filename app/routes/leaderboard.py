from flask import Blueprint, jsonify, request
from app.models.user_model import (
    get_top_users, get_user_rank, get_department_leaderboard,
    get_user_dashboard_data
)
from app.models.analytics_model import get_department_analytics, get_system_analytics
from app.routes.ai_model import get_achievement_recommendations, calculate_user_rank_score
from datetime import datetime, timedelta

leaderboard_bp = Blueprint('leaderboard', __name__)

@leaderboard_bp.route('/global', methods=['GET'])
def get_global_leaderboard():
    """Get global leaderboard with advanced ranking."""
    try:
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        
        # Get top users globally
        top_users = get_top_users(limit + offset)
        
        if not top_users:
            return jsonify({
                'success': True,
                'leaderboard': [],
                'total_users': 0
            }), 200
        
        # Apply pagination
        paginated_users = top_users[offset:offset + limit]
        
        # Add rank positions
        for i, user in enumerate(paginated_users):
            user['global_rank'] = offset + i + 1
            user['rank_change'] = 0  # TODO: Calculate rank change from previous period
        
        return jsonify({
            'success': True,
            'leaderboard': paginated_users,
            'total_users': len(top_users),
            'pagination': {
                'limit': limit,
                'offset': offset,
                'has_more': offset + limit < len(top_users)
            }
        }), 200
        
    except Exception as e:
        print(f"Error getting global leaderboard: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get leaderboard'
        }), 500

@leaderboard_bp.route('/department/<dept>', methods=['GET'])
def get_department_leaderboard_api(dept):
    """Get department-specific leaderboard."""
    try:
        limit = int(request.args.get('limit', 20))
        
        # Get department leaderboard
        try:
            leaderboard = get_department_leaderboard(dept, limit)
        except:
            leaderboard = get_top_users(limit, department=dept)
        
        if not leaderboard:
            return jsonify({
                'success': True,
                'department': dept,
                'leaderboard': [],
                'analytics': None
            }), 200
        
        # Get department analytics
        try:
            analytics = get_department_analytics(dept)
        except Exception as e:
            print(f"Error getting department analytics: {e}")
            analytics = None
        
        return jsonify({
            'success': True,
            'department': dept,
            'leaderboard': leaderboard,
            'analytics': analytics
        }), 200
        
    except Exception as e:
        print(f"Error getting department leaderboard for {dept}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get department leaderboard'
        }), 500


@leaderboard_bp.route('/rank/<user_id>', methods=['GET'])
def get_user_rank_api(user_id):
    """Get detailed rank information for a specific user."""
    try:
        rank_info = get_user_rank(user_id)
        
        if 'error' in rank_info:
            return jsonify({
                'success': False,
                'error': rank_info['error']
            }), 404
        
        # Get additional ranking context
        from app.models.user_model import get_user_by_id
        user = get_user_by_id(user_id)
        
        if user:
            # Get achievement recommendations
            try:
                achievements = get_achievement_recommendations(user)
                rank_info['recommended_achievements'] = achievements
            except Exception as e:
                print(f"Error getting achievement recommendations: {e}")
                rank_info['recommended_achievements'] = []
        
        return jsonify({
            'success': True,
            'rank_info': rank_info
        }), 200
        
    except Exception as e:
        print(f"Error getting user rank for {user_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get user rank'
        }), 500
