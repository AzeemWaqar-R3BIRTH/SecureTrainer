from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for, flash
from app.models.challenge_model import (
    add_challenge, delete_challenge, list_challenges,
    get_challenge_statistics, get_challenge_statistics_detailed
)
from app.models.analytics_model import (
    get_challenge_logs, get_system_analytics, get_department_analytics,
    get_user_learning_analytics
)
from app.models.user_model import (
    promote_user, get_top_users, get_department_leaderboard,
    get_user_dashboard_data, get_user_by_id, insert_user, update_user_score_level
)
from app.routes.ai_model import get_achievement_recommendations
import os
from datetime import datetime, timedelta
from bson import ObjectId
from app.utils.security import hash_password

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Enhanced admin authentication with role checking
def is_admin(token=None, user_id=None):
    """Check if user has admin privileges."""
    # Check token-based auth
    if token and token == os.getenv("ADMIN_TOKEN"):
        return True
    
    # Check session-based auth
    if user_id:
        user = get_user_by_id(user_id)
        if user and (user.get('is_admin', False) or user.get('role') in ['admin', 'Department Head', 'Security Architect', 'Chief Security Officer']):
            return True
    
    # Check current session
    if 'user_id' in session:
        user = get_user_by_id(session['user_id'])
        if user and (user.get('is_admin', False) or user.get('role') in ['admin', 'Department Head', 'Security Architect', 'Chief Security Officer']):
            return True
    
    return False


def require_admin(f):
    """Decorator to require admin authentication."""
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        user_id = request.args.get('user_id') or session.get('user_id')
        
        if not is_admin(token, user_id):
            if request.is_json:
                return jsonify({'error': 'Unauthorized - Admin access required'}), 403
            return redirect(url_for('admin.admin_login'))
        
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page."""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Basic auth check (should be enhanced)
        from app.models.analytics_model import get_db
        db = get_db()
        user = db.users.find_one({'username': username})
        
        if user and user.get('password') == hash_password(password):
            if user.get('is_admin', False) or user.get('role') in ['admin', 'Department Head']:
                session['user_id'] = str(user['_id'])
                session['is_admin'] = True
                return redirect(url_for('admin.admin_dashboard'))
            else:
                flash('Access denied: Not an admin', 'error')
        else:
            flash('Invalid credentials', 'error')
            
    return render_template('admin/login.html')

@admin_bp.route('/register', methods=['GET', 'POST'])
def admin_register():
    """Secure admin registration page requiring environment token."""
    if request.method == 'POST':
        try:
            # Get form data
            registration_token = request.form.get('registration_token')
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            company = request.form.get('company', 'SecureTrainer')
            department = request.form.get('department', 'Administration')
            
            # Validate registration token
            admin_reg_token = os.getenv('ADMIN_REGISTRATION_TOKEN')
            if not admin_reg_token:
                flash('Admin registration is not configured. Contact system administrator.', 'error')
                return render_template('admin/register.html')
            
            if registration_token != admin_reg_token:
                flash('Invalid registration token. Admin registration denied.', 'error')
                return render_template('admin/register.html')
            
            # Validate required fields
            if not all([first_name, last_name, username, email, password, confirm_password]):
                flash('All fields are required.', 'error')
                return render_template('admin/register.html')
            
            # Validate password match
            if password != confirm_password:
                flash('Passwords do not match.', 'error')
                return render_template('admin/register.html')
            
            # Validate password strength
            if len(password) < 8:
                flash('Password must be at least 8 characters long.', 'error')
                return render_template('admin/register.html')
            
            # Check if username or email already exists
            from app.models.analytics_model import get_db
            db = get_db()
            
            if db.users.find_one({'username': username}):
                flash('Username already exists.', 'error')
                return render_template('admin/register.html')
            
            if db.users.find_one({'email': email}):
                flash('Email already exists.', 'error')
                return render_template('admin/register.html')
            
            # Create admin user
            admin_user = {
                "first_name": first_name,
                "last_name": last_name,
                "username": username,
                "email": email,
                "password": hash_password(password),
                "company": company,
                "department": department,
                "score": 0,
                "level": 1,
                "role": "Chief Security Officer",
                "is_admin": True,
                "admin_role": "admin",
                "created_at": datetime.now(),
                "challenges_completed": [],
                "achievements": []
            }
            
            # Insert user into database
            user_id = insert_user(admin_user)
            
            # Generate QR code with error handling
            qr_data = None
            try:
                from app.utils.qr import QRCodeManager
                qr_manager = QRCodeManager()
                qr_data = qr_manager.generate_qr_code(user_id, email)
                print(f"✅ QR code generated successfully for admin: {username}")
            except Exception as e:
                print(f"❌ QR code generation failed: {e}")
                import traceback
                traceback.print_exc()
                flash('Admin account created but QR code generation failed. Please contact support.', 'warning')
            
            # Send welcome email with QR code
            if qr_data:
                try:
                    from app.utils.email import EmailManager
                    from flask_mail import Mail
                    from flask import current_app
                    
                    # Get mail instance from current app
                    mail = Mail()
                    mail.init_app(current_app)
                    
                    email_manager = EmailManager(mail)
                    email_sent = email_manager.send_admin_welcome_email(email, f"{first_name} {last_name}", qr_data)
                    
                    if email_sent:
                        print(f"✅ Admin welcome email sent to {email}")
                        flash('Admin account created successfully! Check your email for the QR code.', 'success')
                    else:
                        print(f"⚠️ Failed to send admin welcome email to {email}")
                        flash('Admin account created but email sending failed. Please contact support for your QR code.', 'warning')
                        
                except Exception as e:
                    print(f"❌ Email sending error: {e}")
                    import traceback
                    traceback.print_exc()
                    flash('Admin account created but email sending failed. Please contact support for your QR code.', 'warning')
            else:
                flash('Admin account created but QR code generation failed. Please contact support.', 'warning')
            
            # Redirect to login page
            return redirect(url_for('admin.admin_login'))
            
        except Exception as e:
            print(f"Error during admin registration: {e}")
            import traceback
            traceback.print_exc()
            flash('An error occurred during registration. Please try again.', 'error')
            return render_template('admin/register.html')
    
    # GET request - show registration form
    return render_template('admin/register.html')

@admin_bp.route('/dashboard', methods=['GET'])
@require_admin
def admin_dashboard():
    """Get comprehensive admin dashboard data."""
    try:
        # Get system analytics
        system_analytics = get_system_analytics()
        
        # Get challenge statistics
        challenge_stats_raw = get_challenge_statistics()
        
        # Get top performing users
        top_users = get_top_users(limit=10)
        
        # Get recent activity (last 7 days)
        from app.models.analytics_model import get_db
        db = get_db()
        week_ago = datetime.now() - timedelta(days=7)
        day_ago = datetime.now() - timedelta(hours=24)
        
        recent_activity = {
            'new_users': db.users.count_documents({'created_at': {'$gte': week_ago}}),
            'challenges_attempted': db.challenge_attempts.count_documents({'attempt_time': {'$gte': week_ago}}),
            'successful_attempts': db.challenge_attempts.count_documents({
                'attempt_time': {'$gte': week_ago},
                'is_correct': True
            })
        }
        
        # Get department performance overview
        departments = db.users.distinct('department')
        department_overview = []
        
        for dept in departments[:10]:  # Limit to top 10 departments
            dept_analytics = get_department_analytics(dept)
            if dept_analytics:
                department_overview.append({
                    'department': dept,
                    'total_users': dept_analytics.get('total_users', 0),
                    'average_score': dept_analytics.get('average_score', 0),
                    'success_rate': dept_analytics.get('success_rate', 0)
                })
        
        # Extract overview data from system_analytics
        overview = system_analytics.get('overview', {})
        
        # Active users in last 24 hours
        active_users_24h = len(db.challenge_attempts.distinct('user_id', {
            'attempt_time': {'$gte': day_ago}
        }))
        
        # Calculate total challenge completions from challenge_attempts
        total_completions = db.challenge_attempts.count_documents({'is_correct': True})
        
        # Flatten the data structure for template
        dashboard_data = {
            'system_statistics': {
                'total_users': overview.get('total_users', 0),
                'active_users_24h': active_users_24h,
                'total_challenges': overview.get('total_challenges', 0),
                'total_attempts': overview.get('total_attempts', 0)
            },
            'challenge_statistics': {
                'total': challenge_stats_raw.get('total', 0),
                'total_completions': total_completions,
                'avg_success_rate': round(overview.get('overall_success_rate', 0), 1),
                'by_category': challenge_stats_raw.get('by_category', {}),
                'by_difficulty': challenge_stats_raw.get('by_difficulty', {})
            },
            'top_users': top_users,
            'recent_activity': recent_activity,
            'department_overview': department_overview,
            'generated_at': datetime.now().isoformat()
        }
        
        if request.is_json:
            return jsonify({
                'success': True,
                'dashboard': dashboard_data
            }), 200
            
        return render_template('admin/dashboard.html', data=dashboard_data)
        
    except Exception as e:
        print(f"Error getting admin dashboard: {e}")
        import traceback
        traceback.print_exc()
        if request.is_json:
            return jsonify({
                'success': False,
                'error': 'Failed to load dashboard'
            }), 500
        return render_template('500.html'), 500


@admin_bp.route('/users', methods=['GET'])
@require_admin
def manage_users():
    """List and manage users."""
    try:
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        department = request.args.get('department')
        search = request.args.get('search')
        
        from app.models.analytics_model import get_db
        db = get_db()
        
        # Build query
        query = {}
        if department:
            query['department'] = department
        if search:
            query['$or'] = [
                {'username': {'$regex': search, '$options': 'i'}},
                {'email': {'$regex': search, '$options': 'i'}},
                {'first_name': {'$regex': search, '$options': 'i'}},
                {'last_name': {'$regex': search, '$options': 'i'}}
            ]
        
        # Get users with pagination
        users_cursor = db.users.find(query).sort('created_at', -1).skip(offset).limit(limit)
        users = list(users_cursor)
        total_count = db.users.count_documents(query)
        
        if request.is_json:
            # Convert ObjectIds to strings for JSON response
            for user in users:
                user['_id'] = str(user['_id'])
            return jsonify({
                'success': True,
                'users': users,
                'total_count': total_count
            })
            
        return render_template('admin/users_list.html', users=users, total=total_count, page=offset//limit + 1)
        
    except Exception as e:
        print(f"Error managing users: {e}")
        return render_template('500.html'), 500

@admin_bp.route('/users/add', methods=['GET', 'POST'])
@require_admin
def add_user():
    """Add a new user manually."""
    if request.method == 'POST':
        try:
            data = request.form
            
            user = {
                "first_name": data.get('first_name'),
                "last_name": data.get('last_name'),
                "username": data.get('username'),
                "email": data.get('email'),
                "password": hash_password(data.get('password')),
                "company": data.get('company'),
                "department": data.get('department'),
                "score": int(data.get('score', 0)),
                "level": int(data.get('level', 1)),
                "role": data.get('role', 'Trainee'),
                "is_admin": data.get('is_admin') == 'on',
                "created_at": datetime.now()
            }
            
            insert_user(user)
            flash('User added successfully', 'success')
            return redirect(url_for('admin.manage_users'))
            
        except Exception as e:
            flash(f'Error adding user: {str(e)}', 'error')
            
    return render_template('admin/add_user.html')

@admin_bp.route('/users/<user_id>/edit', methods=['GET', 'POST'])
@require_admin
def edit_user(user_id):
    """Edit user details."""
    try:
        from app.models.analytics_model import get_db
        db = get_db()
        
        if request.method == 'POST':
            data = request.form
            update_data = {
                "first_name": data.get('first_name'),
                "last_name": data.get('last_name'),
                "email": data.get('email'),
                "company": data.get('company'),
                "department": data.get('department'),
                "score": int(data.get('score', 0)),
                "level": int(data.get('level', 1)),
                "role": data.get('role'),
                "is_admin": data.get('is_admin') == 'on'
            }
            
            if data.get('password'):
                update_data['password'] = hash_password(data.get('password'))
                
            db.users.update_one({'_id': ObjectId(user_id)}, {'$set': update_data})
            flash('User updated successfully', 'success')
            return redirect(url_for('admin.manage_users'))
            
        user = db.users.find_one({'_id': ObjectId(user_id)})
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('admin.manage_users'))
            
        return render_template('admin/edit_user.html', user=user)
        
    except Exception as e:
        print(f"Error editing user: {e}")
        return render_template('500.html'), 500

@admin_bp.route('/users/<user_id>/delete', methods=['POST'])
@require_admin
def delete_user(user_id):
    """Delete a user."""
    try:
        from app.models.analytics_model import get_db
        db = get_db()
        
        db.users.delete_one({'_id': ObjectId(user_id)})
        flash('User deleted successfully', 'success')
        
        if request.is_json:
            return jsonify({'success': True})
            
        return redirect(url_for('admin.manage_users'))
        
    except Exception as e:
        print(f"Error deleting user: {e}")
        if request.is_json:
            return jsonify({'success': False, 'error': str(e)}), 500
        return redirect(url_for('admin.manage_users'))


@admin_bp.route('/challenge', methods=['POST'])
@require_admin
def create_challenge():
    """Create a new challenge."""
    try:
        data = request.json
        
        # Validate required fields
        required_fields = ['challenge_id', 'category', 'difficulty', 'scenario', 'question', 'score_weight', 'type']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Missing required field: {field}'
                }), 400
        
        challenge_id = add_challenge(data)
        
        return jsonify({
            'success': True,
            'message': 'Challenge created successfully',
            'challenge_id': challenge_id
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400
    except Exception as e:
        print(f"Error creating challenge: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to create challenge'
        }), 500

@admin_bp.route('/challenge/<challenge_id>', methods=['DELETE'])
@require_admin
def remove_challenge(challenge_id):
    """Delete a challenge."""
    try:
        success = delete_challenge(challenge_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Challenge deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Challenge not found'
            }), 404
            
    except Exception as e:
        print(f"Error deleting challenge: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete challenge'
        }), 500


@admin_bp.route('/challenges', methods=['GET'])
@require_admin
def all_challenges():
    """Get all challenges with detailed statistics."""
    try:
        from app.models.challenge_model import get_all_challenges
        
        print("🔍 Fetching all challenges...")
        
        # Get all in-memory challenges
        try:
            challenges = get_all_challenges()
            print(f"✅ Retrieved {len(challenges)} challenges")
        except Exception as e:
            print(f"❌ Error in get_all_challenges: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': f'Failed to load challenges: {str(e)}'
            }), 500
        
        # Add detailed statistics for each challenge
        for i, challenge in enumerate(challenges):
            try:
                challenge_id = challenge.get('id')
                print(f"🔍 Processing challenge {i+1}/{len(challenges)}: {challenge_id}")
                detailed_stats = get_challenge_statistics_detailed(challenge_id)
                challenge['statistics'] = detailed_stats
            except Exception as e:
                print(f"⚠️ Error getting stats for challenge {challenge.get('id')}: {e}")
                # Provide default statistics
                challenge['statistics'] = {
                    'total_attempts': 0,
                    'successful_attempts': 0,
                    'success_rate': 0
                }
        
        print(f"✅ Successfully processed all challenges")
        
        if request.is_json or request.args.get('format') == 'json':
            return jsonify({
                'success': True,
                'challenges': challenges,
                'total_count': len(challenges)
            }), 200
            
        return render_template('admin/challenges.html', challenges=challenges)
        
    except Exception as e:
        print(f"❌ Error in all_challenges route: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Failed to get challenges: {str(e)}'
        }), 500

@admin_bp.route('/user/<user_id>/analytics', methods=['GET'])
@require_admin
def get_user_detailed_analytics(user_id):
    """Get detailed analytics for a specific user."""
    try:
        # Get comprehensive user data
        dashboard_data = get_user_dashboard_data(user_id)
        
        if not dashboard_data:
            flash('User not found', 'error')
            return redirect(url_for('admin.manage_users'))
        
        # Get learning analytics
        analytics = get_user_learning_analytics(user_id)
        
        # Get achievement recommendations
        from app.models.user_model import get_user_by_id
        user = get_user_by_id(user_id)
        achievement_recommendations = []
        
        if user:
            try:
                achievement_recommendations = get_achievement_recommendations(user)
            except Exception as e:
                print(f"Error getting achievement recommendations: {e}")
        
        # Get challenge attempts history
        from app.models.challenge_model import get_user_challenge_attempts
        from app.models.user_model import get_db
        db = get_db()
        
        challenge_attempts_raw = get_user_challenge_attempts(user_id, limit=50)
        
        # Enrich attempts with challenge names and format data
        challenge_attempts = []
        for attempt in challenge_attempts_raw:
            challenge_id = attempt.get('challenge_id')
            challenge_name = 'Unknown Challenge'
            
            # Try to get challenge name from database
            try:
                # First try to find in challenges collection
                challenge = db.challenges.find_one({'id': challenge_id})
                if not challenge:
                    # Try with _id if it's an ObjectId
                    from bson import ObjectId
                    if ObjectId.is_valid(challenge_id):
                        challenge = db.challenges.find_one({'_id': ObjectId(challenge_id)})
                
                if challenge:
                    challenge_name = challenge.get('title') or challenge.get('name') or f"Challenge {challenge_id[:8]}"
                else:
                    # If not found, use the category and ID
                    category = attempt.get('category', 'General')
                    challenge_name = f"{category} Challenge"
            except Exception as e:
                print(f"Error getting challenge name for {challenge_id}: {e}")
                challenge_name = f"Challenge {str(challenge_id)[:8]}"
            
            challenge_attempts.append({
                'challenge_name': challenge_name,
                'status': 'completed' if attempt.get('is_correct') else 'failed',
                'timestamp': attempt.get('attempt_time').strftime('%Y-%m-%d %H:%M') if attempt.get('attempt_time') else 'N/A',
                'is_correct': attempt.get('is_correct', False),
                'time_taken': attempt.get('time_taken', 0)
            })
        
        detailed_analytics = {
            'user_info': dashboard_data['user_info'],
            'progress': dashboard_data['progress'],
            'performance': dashboard_data['performance'],
            'ranking': dashboard_data['ranking'],
            'detailed_analytics': analytics,
            'achievement_recommendations': achievement_recommendations,
            'recent_attempts': challenge_attempts
        }
        
        # Render the analytics template with show_charts flag for Chart.js
        return render_template('admin/user_analytics.html', 
                             user_analytics=detailed_analytics,
                             show_charts=True)
        
    except Exception as e:
        print(f"Error getting user analytics: {e}")
        import traceback
        traceback.print_exc()
        flash('Failed to load user analytics', 'error')
        return redirect(url_for('admin.manage_users'))


@admin_bp.route('/logs/<challenge_id>', methods=['GET'])
@require_admin
def view_logs(challenge_id):
    """Get detailed logs for a specific challenge."""
    try:
        logs = get_challenge_logs(challenge_id)
        
        # Get detailed statistics
        detailed_stats = get_challenge_statistics_detailed(challenge_id)
        
        return jsonify({
            'success': True,
            'challenge_id': challenge_id,
            'logs': logs,
            'statistics': detailed_stats
        }), 200
        
    except Exception as e:
        print(f"Error getting challenge logs: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get logs'
        }), 500


@admin_bp.route('/promote/<user_id>', methods=['POST'])
@require_admin
def promote(user_id):
    """Promote a user to a new role."""
    try:
        data = request.json
        new_role = data.get('role')
        
        if not new_role:
            return jsonify({
                'success': False,
                'error': 'Role is required'
            }), 400
        
        # Valid roles
        valid_roles = [
            'Trainee', 'Junior Analyst', 'Analyst', 'Senior Analyst',
            'Specialist', 'Expert', 'Lead Analyst', 'Team Lead',
            'Department Head', 'Security Architect', 'Chief Security Officer'
        ]
        
        if new_role not in valid_roles:
            return jsonify({
                'success': False,
                'error': f'Invalid role. Valid roles: {valid_roles}'
            }), 400
        
        success = promote_user(user_id, new_role)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'User promoted to {new_role}'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to promote user'
            }), 404
            
    except Exception as e:
        print(f"Error promoting user: {e}")
        return jsonify({
            'success': False,
            'error': 'Promotion failed'
        }), 500


@admin_bp.route('/departments', methods=['GET'])
@require_admin
def get_departments_overview():
    """Get overview of all departments."""
    try:
        from app.models.analytics_model import get_db
        db = get_db()
        
        # Get all departments
        departments = db.users.distinct('department')
        
        departments_data = []
        for dept in departments:
            if dept:  # Skip empty departments
                analytics = get_department_analytics(dept)
                if analytics:
                    departments_data.append(analytics)
        
        # Sort by total users
        departments_data.sort(key=lambda x: x.get('total_users', 0), reverse=True)
        
        if request.is_json:
            return jsonify({
                'success': True,
                'departments': departments_data,
                'total_departments': len(departments_data)
            }), 200
            
        return render_template('admin/departments.html', departments=departments_data)
        
    except Exception as e:
        print(f"Error getting departments overview: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get departments overview'
        }), 500


@admin_bp.route('/export/users', methods=['GET'])
@require_admin
def export_users_data():
    """Export users data for analysis."""
    try:
        department = request.args.get('department')
        format_type = request.args.get('format', 'json')  # json or csv
        
        from app.models.analytics_model import get_db
        db = get_db()
        
        # Build query
        query = {}
        if department:
            query['department'] = department
        
        # Get all users
        users = list(db.users.find(query))
        
        export_data = []
        for user in users:
            user_export = {
                'user_id': str(user['_id']),
                'username': user['username'],
                'email': user['email'],
                'first_name': user.get('first_name', ''),
                'last_name': user.get('last_name', ''),
                'company': user.get('company', ''),
                'department': user.get('department', ''),
                'level': user.get('level', 1),
                'score': user.get('score', 0),
                'role': user.get('role', 'Trainee'),
                'created_at': user.get('created_at', '').isoformat() if user.get('created_at') else '',
                'last_login': user.get('last_login', '').isoformat() if user.get('last_login') else '',
                'challenges_completed': len(user.get('challenges_completed', [])),
                'achievements_count': len(user.get('achievements', []))
            }
            
            # Add analytics if available
            try:
                analytics = get_user_learning_analytics(str(user['_id']))
                if analytics:
                    user_export.update({
                        'success_rate': analytics.get('success_rate', 0),
                        'total_attempts': analytics.get('total_attempts', 0),
                        'learning_velocity': analytics.get('learning_velocity', 0)
                    })
            except:
                pass
            
            export_data.append(user_export)
        
        return jsonify({
            'success': True,
            'export_data': export_data,
            'total_records': len(export_data),
            'generated_at': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"Error exporting users data: {e}")
        return jsonify({
            'success': False,
            'error': 'Export failed'
        }), 500


@admin_bp.route('/ml-management', methods=['GET'])
@require_admin
def ml_management():
    """Render ML model management page."""
    return render_template('admin/ml_management.html')
