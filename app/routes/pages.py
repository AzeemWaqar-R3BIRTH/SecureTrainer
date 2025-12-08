"""
Main Page Routes for SecureTrainer
Serves HTML templates for the application pages
"""

from flask import Blueprint, render_template, session, redirect, url_for
from app.models.user_model import get_user_by_id
from app.models.analytics_model import get_dashboard_analytics
from app.routes.learning import get_user_learning_progress
from app.models.challenge_model import (
    load_sql_challenges,
    get_xss_challenges,
    get_command_injection_challenges,
    get_authentication_challenges,
    get_csrf_challenges
)
import logging

logger = logging.getLogger(__name__)

pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/')
def index():
    """Home/landing page."""
    return render_template('index.html')


@pages_bp.route('/login')
def login_page():
    """Login page."""
    return render_template('login.html')


@pages_bp.route('/register')
def register_page():
    """Registration page."""
    return render_template('register.html')


@pages_bp.route('/dashboard')
def dashboard_page():
    """Dashboard page - requires authentication."""
    try:
        if 'user_id' not in session:
            return redirect(url_for('pages.login_page'))
        
        user_id = session['user_id']
        user = get_user_by_id(user_id)
        
        if not user:
            return redirect(url_for('pages.login_page'))
        
        # Get dashboard analytics
        analytics = get_dashboard_analytics(user_id)
        
        return render_template('dashboard.html', user=user, analytics=analytics)
        
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        return redirect(url_for('pages.login_page'))


@pages_bp.route('/learning-center')
def learning_center():
    """Learning center page - requires authentication with comprehensive error handling."""
    # Initialize fallback data structure
    fallback_user = {
        'username': 'User',
        'email': '',
        'level': 1,
        'id': None
    }
    
    fallback_progress = {
        'modules': {},
        'overall_progress': 0,
        'last_accessed': None,
        'total_study_time': 0
    }
    
    try:
        # Check authentication
        if 'user_id' not in session:
            logger.info("Unauthenticated access attempt to learning center")
            return redirect(url_for('pages.login_page'))
        
        user_id = session['user_id']
        logger.info(f"Learning center accessed by user: {user_id}")
        
        # Get user data with error handling
        user = None
        try:
            user = get_user_by_id(user_id)
            if not user:
                logger.warning(f"User {user_id} not found in database")
                return redirect(url_for('pages.login_page'))
        except Exception as user_error:
            logger.error(f"Error fetching user {user_id}: {user_error}")
            # Use fallback user but keep session
            user = fallback_user.copy()
            user['id'] = user_id
        
        # Get learning progress with comprehensive error handling
        progress = None
        try:
            progress = get_user_learning_progress(user_id)
            if progress:
                logger.info(f"Progress loaded for user {user_id}: {progress.get('overall_progress', 0)}% complete")
            else:
                logger.info(f"No progress data found for user {user_id}, using defaults")
                progress = fallback_progress.copy()
        except ImportError as import_error:
            logger.warning(f"Learning progress module import failed: {import_error}")
            progress = fallback_progress.copy()
        except Exception as progress_error:
            logger.warning(f"Could not load progress for user {user_id}: {progress_error}")
            progress = fallback_progress.copy()
        
        # Ensure progress has expected structure
        if progress and not isinstance(progress, dict):
            logger.warning(f"Invalid progress data type: {type(progress)}")
            progress = fallback_progress.copy()
        
        # Render template with validated data
        return render_template('learning-center.html', 
                             user=user, 
                             progress=progress,
                             error_mode=False)
        
    except Exception as e:
        logger.error(f"Critical error loading learning center: {e}", exc_info=True)
        
        # Last resort fallback - render with minimal data
        try:
            return render_template('learning-center.html', 
                                 user=fallback_user, 
                                 progress=fallback_progress,
                                 error_mode=True)
        except Exception as template_error:
            logger.critical(f"Template rendering failed: {template_error}", exc_info=True)
            # Return emergency static HTML
            return f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Learning Center - Error</title>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 40px; text-align: center; }}
                    .error-container {{ max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e53e3e; border-radius: 8px; background: #fff5f5; }}
                    h1 {{ color: #e53e3e; }}
                    .actions {{ margin-top: 20px; }}
                    .btn {{ display: inline-block; padding: 10px 20px; margin: 5px; background: #3182ce; color: white; text-decoration: none; border-radius: 4px; }}
                </style>
            </head>
            <body>
                <div class="error-container">
                    <h1>⚠️ Service Temporarily Unavailable</h1>
                    <p>We're experiencing technical difficulties loading the Learning Center.</p>
                    <p>Our team has been notified and is working to resolve this issue.</p>
                    <div class="actions">
                        <a href="/dashboard" class="btn">Return to Dashboard</a>
                        <a href="javascript:location.reload()" class="btn">Retry</a>
                    </div>
                </div>
            </body>
            </html>
            """, 500


@pages_bp.route('/challenges')
def challenges_page():
    """Challenges page - requires authentication."""
    try:
        if 'user_id' not in session:
            return redirect(url_for('pages.login_page'))
        
        user_id = session['user_id']
        user = get_user_by_id(user_id)
        
        if not user:
            return redirect(url_for('pages.login_page'))
        
        # Get challenges by category
        challenges_by_category = {
            'sql_injection': load_sql_challenges(),
            'xss': get_xss_challenges(),
            'command_injection': get_command_injection_challenges(),
            'authentication': get_authentication_challenges(),
            'csrf': get_csrf_challenges()
        }

        # Get completed challenges
        completed_challenges = user.get('challenges_completed', [])
        
        # Calculate progress stats for each category
        category_stats = {}
        
        # Log user's completed challenges for debugging
        logger.info(f"========== PROGRESS BAR CALCULATION ==========")
        logger.info(f"User ID: {user_id}")
        logger.info(f"User has {len(completed_challenges)} completed challenges")
        logger.info(f"Completed IDs: {completed_challenges}")
        
        for category, challenges in challenges_by_category.items():
            total = len(challenges)
            # Count how many challenges in this category are completed
            completed_count = 0
            challenge_ids = [c['id'] for c in challenges]
            
            logger.info(f"\n--- Category: {category.upper()} ---")
            logger.info(f"Total challenges: {total}")
            logger.info(f"Challenge IDs: {challenge_ids}")
            
            # Match completed challenges with this category's challenges
            matched_ids = []
            for completed_id in completed_challenges:
                if completed_id in challenge_ids:
                    completed_count += 1
                    matched_ids.append(completed_id)
            
            percent = int((completed_count / total * 100)) if total > 0 else 0
            
            category_stats[category] = {
                'total': total,
                'completed': completed_count,
                'percent': percent
            }
            
            logger.info(f"Matched {completed_count}/{total} challenges")
            logger.info(f"Matched IDs: {matched_ids}")
            logger.info(f"Progress: {percent}%")
        
        logger.info(f"\n========== END CALCULATION ==========")

        return render_template('challenges.html', 
                             user=user,
                             challenges_by_category=challenges_by_category,
                             completed_challenges=completed_challenges,
                             category_stats=category_stats)
        
    except Exception as e:
        logger.error(f"Error loading challenges page: {e}")
        return redirect(url_for('pages.login_page'))


@pages_bp.route('/challenge/<challenge_id>')
def challenge_interface(challenge_id):
    """Challenge interface page - requires authentication."""
    try:
        if 'user_id' not in session:
            return redirect(url_for('pages.login_page'))
        
        user_id = session['user_id']
        user = get_user_by_id(user_id)
        
        if not user:
            return redirect(url_for('pages.login_page'))
        
        return render_template('challenge_interface.html', user=user, challenge_id=challenge_id)
        
    except Exception as e:
        logger.error(f"Error loading challenge interface: {e}")
        return redirect(url_for('pages.challenges_page'))


@pages_bp.route('/leaderboard')
def leaderboard_page():
    """Leaderboard page."""
    try:
        if 'user_id' not in session:
            return redirect(url_for('pages.login_page'))
        
        user_id = session['user_id']
        user = get_user_by_id(user_id)
        
        if not user:
            return redirect(url_for('pages.login_page'))
        
        return render_template('leaderboard.html', user=user)
        
    except Exception as e:
        logger.error(f"Error loading leaderboard: {e}")
        return redirect(url_for('pages.login_page'))
