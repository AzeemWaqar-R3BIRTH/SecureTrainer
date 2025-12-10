#!/usr/bin/env python3
"""
SecureTrainer - Cybersecurity Awareness Training Platform
Final Year Project for Bachelor's in Cyber Security

A comprehensive web application that provides interactive cybersecurity training
through gamified challenges including SQL injection, XSS, command injection,
and more. Features AI-driven difficulty adjustment and QR code authentication.
"""

import os
import sys
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session, make_response
from flask_mail import Mail, Message
from flask_cors import CORS
import bcrypt
import qrcode
from PIL import Image
import io
import base64
import uuid
import json
from dotenv import load_dotenv

# Load environment variables
try:
    load_dotenv()
except Exception as e:
    print(f"Warning: Could not load .env file: {e}")
    print("Using default environment variables...")

# Import our modules
from app.models.user_model import (
    get_db, insert_user, get_user_by_id, update_user_score_level, 
    get_top_users, get_user_rank, promote_user
)
from app.models.challenge_model import (
    add_challenge, delete_challenge, list_challenges, load_sql_challenges,
    get_fallback_sql_challenges, get_xss_challenges, get_command_injection_challenges,
    get_authentication_challenges, get_csrf_challenges, get_all_challenges,
    get_challenges_by_category, get_random_challenge, get_challenge_by_id,
    get_challenges_by_difficulty, get_user_appropriate_challenges, get_challenge_statistics
)
from app.utils.qr import QRCodeManager
from app.utils.email import EmailManager
from robust_email_manager import RobustEmailManager

# Import AI routes
from app.routes.ai_routes import ai_bp, init_ai_orchestrator
from app.routes.learning import learning_bp

# Set default environment variables if .env fails to load
if not os.getenv('SECRET_KEY'):
    os.environ['SECRET_KEY'] = 'Azeem and Saffan Developed this AI Driven Cyber Security Training Application in Supervision of Dr Shahbaz Siddiqui and Dr Fahad Samad'
if not os.getenv('MONGO_URI'):
    os.environ['MONGO_URI'] = 'mongodb://localhost:27017/securetrainer'
if not os.getenv('MAIL_SERVER'):
    os.environ['MAIL_SERVER'] = 'smtp.gmail.com'
if not os.getenv('MAIL_PORT'):
    os.environ['MAIL_PORT'] = '587'
if not os.getenv('MAIL_USERNAME'):
    os.environ['MAIL_USERNAME'] = 'azeemwaqar.work@gmail.com'
if not os.getenv('MAIL_PASSWORD'):
    os.environ['MAIL_PASSWORD'] = 'wmwb ejkp sevx ipap'
if not os.getenv('MAIL_USE_TLS'):
    os.environ['MAIL_USE_TLS'] = 'True'
if not os.getenv('ADMIN_TOKEN'):
    os.environ['ADMIN_TOKEN'] = 'supersecretadmintoken123'

# Initialize Flask app
app = Flask(__name__, 
           template_folder='app/templates',
           static_folder='app/static')
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Configuration
app.config.update(
    MAIL_SERVER=os.getenv('MAIL_SERVER', 'smtp.gmail.com'),
    MAIL_PORT=int(os.getenv('MAIL_PORT', 587)),
    MAIL_USE_TLS=os.getenv('MAIL_USE_TLS', 'True') == 'True',
    MAIL_USERNAME=os.getenv('MAIL_USERNAME'),
    MAIL_PASSWORD=os.getenv('MAIL_PASSWORD'),
    MONGO_URI=os.getenv('MONGO_URI', 'mongodb://localhost:27017/securetrainer'),
    PERMANENT_SESSION_LIFETIME=timedelta(hours=24),
    SESSION_COOKIE_SECURE=False,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

# Initialize Flask-Mail
mail = Mail(app)

# Initialize CORS
CORS(app)

# Initialize enhanced database manager
from app.database.db_manager import initialize_database_manager, get_database, get_database_status
from app.utils.error_handler import initialize_error_handling, error_handler, degradation_manager
from app.utils.session_manager import initialize_session_manager

print("🔧 Initializing SecureTrainer components...")

# Initialize database with robust connection handling
try:
    db_manager = initialize_database_manager(app.config['MONGO_URI'])
    db = get_database()
    
    if db is not None:
        print("✅ Database connection established")
        # Update Flask config with database client
        app.config['MONGO_CLIENT'] = db_manager.client
    else:
        print("⚠️ Database connection failed - enabling degraded mode")
        if 'degradation_manager' in globals():
            degradation_manager.mark_service_down('database', 'Connection failed during startup')
except Exception as e:
    print(f"❌ Database initialization error: {e}")
    db = None

# Initialize error handling framework
try:
    error_handler, degradation_manager = initialize_error_handling(app)
    print("✅ Error handling framework initialized")
except Exception as e:
    print(f"⚠️ Error handling initialization failed: {e}")

# Initialize session management
try:
    session_manager = initialize_session_manager(app)
    print("✅ Session management initialized")
except Exception as e:
    print(f"⚠️ Session management initialization failed: {e}")

# Initialize AI system with fallback handling
try:
    if db is not None:
        init_ai_orchestrator(db)
        print("✅ AI system initialized")
    else:
        print("⚠️ AI system initialization skipped - database unavailable")
        if degradation_manager:
            degradation_manager.mark_service_down('ai_system', 'Database dependency unavailable')
except ImportError as e:
    print(f"⚠️ AI modules not available: {e}")
    if degradation_manager:
        degradation_manager.mark_service_down('ai_system', 'AI modules import failed')
except Exception as e:
    print(f"⚠️ AI system initialization failed: {e}")
    if degradation_manager:
        degradation_manager.mark_service_down('ai_system', str(e))

# Register AI routes with error handling
try:
    app.register_blueprint(ai_bp)
    print("✅ AI routes registered")
except Exception as e:
    print(f"⚠️ AI routes registration failed: {e}")

# Register Page routes (must be before other routes)
try:
    from app.routes.pages import pages_bp
    app.register_blueprint(pages_bp)
    print("✅ Page routes registered")
except Exception as e:
    print(f"⚠️ Page routes registration failed: {e}")

# Register Learning Center routes
try:
    app.register_blueprint(learning_bp)
    print("✅ Learning routes registered")
except Exception as e:
    print(f"⚠️ Learning routes registration failed: {e}")

# Register Challenge routes with error handling
try:
    from app.routes.challenge import challenge_bp
    app.register_blueprint(challenge_bp, url_prefix='/api/challenges')
    print("✅ Challenge routes registered")
except Exception as e:
    print(f"⚠️ Challenge routes registration failed: {e}")

# Register other challenge-specific routes with error handling
try:
    from app.routes.hints import hints_bp
    from app.routes.auth_challenges import auth_challenges_bp
    from app.routes.xss_challenges import xss_bp
    from app.routes.cmd_injection import cmd_injection_bp
    from app.routes.admin import admin_bp, admin_api_bp
    from app.routes.auth import auth_bp
    from app.routes.login import login_bp
    from app.routes.ml_routes import ml_bp

    app.register_blueprint(hints_bp, url_prefix='/api/hints')
    app.register_blueprint(auth_challenges_bp, url_prefix='/api/auth-challenges')
    app.register_blueprint(xss_bp, url_prefix='/api/xss')
    app.register_blueprint(cmd_injection_bp, url_prefix='/api/cmd-injection')
    app.register_blueprint(admin_bp)  # admin_bp already has /admin prefix defined in routes/admin.py
    app.register_blueprint(admin_api_bp)  # API routes at /api/admin
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(login_bp, url_prefix='/api/login')
    app.register_blueprint(ml_bp)  # ML routes already have /api/ml prefix
    print("✅ Additional routes registered")
except Exception as e:
    print(f"⚠️ Some route registrations failed: {e}")

# Initialize managers with error handling
try:
    qr_manager = QRCodeManager()
    print("✅ QR manager initialized")
except Exception as e:
    print(f"⚠️ QR manager initialization failed: {e}")
    qr_manager = None
    if degradation_manager:
        degradation_manager.mark_service_down('qr_service', str(e))

try:
    email_manager = EmailManager(mail)
    print("✅ Email manager initialized")
except Exception as e:
    print(f"⚠️ Email manager initialization failed: {e}")
    email_manager = None
    if degradation_manager:
        degradation_manager.mark_service_down('email_service', str(e))

try:
    robust_email_manager = RobustEmailManager()
    print("✅ Robust email manager initialized")
except Exception as e:
    print(f"⚠️ Robust email manager initialization failed: {e}")
    robust_email_manager = None

# AI Model fallbacks (simplified versions for demo)
def analyze_user_learning_patterns(user): 
    return {
        'preferred_challenge_types': ['sql_injection', 'xss'],
        'learning_style': 'visual',
        'difficulty_preference': 'intermediate'
    }

def generate_adaptive_hint(user, challenge, attempt_count): 
    hints = [
        "Try thinking about how the application processes your input.",
        "Consider what happens when special characters are used.",
        "Look for ways to break out of the expected input format.",
        "Think about database query construction.",
        "Consider how the application handles different data types."
    ]
    return hints[min(attempt_count, len(hints) - 1)]

def predict_user_success_probability(user, challenge): 
    # Simple probability based on user level and challenge difficulty
    user_level = user.get('level', 1)
    challenge_difficulty = challenge.get('difficulty', 1)
    return max(0.1, min(0.9, 0.5 + (user_level - challenge_difficulty) * 0.1))

# Helper functions using enhanced session management
def set_user_session(user):
    """Set user session data consistently using session manager."""
    from app.utils.session_manager import session_manager
    
    if session_manager:
        success = session_manager.create_user_session(user)
        if success:
            print(f"🔐 Session created: user_id={user.get('_id')}, username={user.get('username')}")
            return True
        else:
            print(f"❌ Failed to create session for user: {user.get('username')}")
            return False
    else:
        # Fallback to original method if session manager not available
        try:
            session['user_id'] = str(user['_id'])
            session['username'] = user['username']
            session.permanent = True
            session.modified = True
            print(f"🔐 Fallback session set: user_id={session['user_id']}, username={session['username']}")
            return True
        except Exception as e:
            print(f"❌ Fallback session creation failed: {e}")
            return False

def get_user_from_session():
    """Get user data from session using session manager."""
    from app.utils.session_manager import session_manager
    
    if session_manager:
        user = session_manager.get_current_user()
        if user:
            print(f"🔍 User found via session manager: {user.get('username')}")
        else:
            print(f"🔍 No user found via session manager")
        return user
    else:
        # Fallback to original method
        print(f"🔍 Getting user from session (fallback): {dict(session)}")
        if 'user_id' in session:
            try:
                from app.database.db_manager import find_user_by_id
                user = find_user_by_id(session['user_id'])
                print(f"🔍 Fallback user lookup: {user.get('username') if user else 'Not found'}")
                return user
            except Exception as e:
                print(f"🔍 Fallback user lookup failed: {e}")
                return None
        print(f"🔍 No user_id in session")
        return None

def require_auth(f):
    """Decorator to require authentication using session manager."""
    from app.utils.session_manager import require_auth as sm_require_auth
    
    # Use session manager's require_auth if available, otherwise fallback
    try:
        return sm_require_auth(f)
    except:
        # Fallback decorator
        def decorated_function(*args, **kwargs):
            print(f"🔍 require_auth checking session: {dict(session)}")
            user = get_user_from_session()
            if not user:
                print("❌ require_auth: No user found, redirecting to login")
                return redirect('/login')
            print(f"✅ require_auth: User found: {user.get('username', 'Unknown')}")
            return f(*args, **kwargs)
        
        decorated_function.__name__ = f.__name__
        return decorated_function

@app.route('/api/system/status')
def system_status():
    """Get comprehensive system status."""
    try:
        # Database status
        db_status = get_database_status()
        
        # Session manager status
        session_stats = None
        try:
            from app.utils.session_manager import session_manager
            if session_manager:
                session_stats = session_manager.get_session_statistics()
        except Exception as e:
            print(f"Session stats error: {e}")
        
        # Error handler statistics
        error_stats = None
        if error_handler:
            error_stats = error_handler.get_error_statistics()
        
        # Degradation manager status
        system_health = None
        if degradation_manager:
            system_health = degradation_manager.get_status()
        
        status = {
            'timestamp': datetime.now().isoformat(),
            'overall_status': 'healthy' if db_status.get('status') == 'connected' else 'degraded',
            'database': db_status,
            'sessions': session_stats,
            'errors': error_stats,
            'system_health': system_health,
            'version': '1.0.0'
        }
        
        return jsonify({
            'success': True,
            'data': status
        }), 200
        
    except Exception as e:
        print(f"System status error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Failed to get system status: {str(e)}'
        }), 500

@app.route('/api/health')
def api_health_check():
    """Simple health check endpoint."""
    try:
        # Basic health indicators
        db_available = get_database() is not None
        
        health_status = {
            'status': 'healthy' if db_available else 'degraded',
            'database': 'connected' if db_available else 'disconnected',
            'timestamp': datetime.now().isoformat()
        }
        
        status_code = 200 if db_available else 503
        
        return jsonify(health_status), status_code
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Routes
@app.route('/')
def index():
    """Redirect root to login to ensure the correct template is served."""
    return redirect('/login')

@app.route('/login.html')
def login_html_alias():
    """Handle accidental visits to /login.html by redirecting to /login."""
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration page with enhanced error handling."""
    if request.method == 'POST':
        try:
            # Get form data
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            company = request.form.get('company')
            department = request.form.get('department')
            
            # Validate required fields
            if not all([first_name, last_name, username, email, password, company, department]):
                flash('All fields are required.', 'error')
                return render_template('register.html')
            
            # Check database availability
            db = get_database()
            if db is None:
                flash('Registration is temporarily unavailable. Please try again later.', 'error')
                return render_template('register.html')
            
            # Check if user already exists
            if db.users.find_one({'$or': [{'username': username}, {'email': email}]}):
                flash('Username or email already exists.', 'error')
                return render_template('register.html')
            
            # Hash password
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            # Create user
            user_data = {
                'first_name': first_name,
                'last_name': last_name,
                'username': username,
                'email': email,
                'password': hashed_password,
                'company': company,
                'department': department,
                'level': 1,
                'score': 0,
                'role': 'Trainee',
                'created_at': datetime.now(),
                'last_login': None,
                'challenges_completed': [],
                'achievements': []
            }
            
            result = db.users.insert_one(user_data)
            user_id = result.inserted_id
            
            # Generate QR code if service available
            qr_data = None
            if qr_manager and degradation_manager and degradation_manager.is_feature_available('qr_generation'):
                try:
                    qr_data = qr_manager.generate_qr_code(str(user_id), email)
                except Exception as e:
                    print(f"⚠️ QR generation failed: {e}")
                    if degradation_manager:
                        degradation_manager.mark_service_down('qr_service', str(e))
            
            # Send welcome email if service available
            if qr_data and robust_email_manager and degradation_manager and degradation_manager.is_feature_available('registration_email'):
                try:
                    # Send email in background to avoid blocking registration
                    import threading
                    def send_email_async():
                        try:
                            robust_email_manager.send_welcome_email(email, f"{first_name} {last_name}", qr_data)
                            print(f"✅ Welcome email sent to {email}")
                        except Exception as e:
                            print(f"⚠️ Failed to send email: {e}")
                            if degradation_manager:
                                degradation_manager.mark_service_down('email_service', str(e))
                    
                    # Start email sending in background thread
                    email_thread = threading.Thread(target=send_email_async)
                    email_thread.daemon = True
                    email_thread.start()
                    print(f"📧 Email sending started in background for {email}")
                except Exception as e:
                    print(f"⚠️ Failed to start email sending: {e}")
            
            success_message = 'Registration successful!'
            if qr_data:
                success_message += ' Check your email for your QR code.'
            else:
                success_message += ' QR code will be sent via email shortly.'
            
            flash(success_message, 'success')
            return redirect('/login')
            
        except Exception as e:
            print(f"Registration error: {e}")
            if error_handler:
                error_handler.log_error(
                    "REGISTRATION_FAILED",
                    f"User registration failed: {str(e)}",
                    "validation",
                    "medium",
                    {'username': request.form.get('username', 'unknown')}
                )
            flash('Registration failed. Please try again.', 'error')
    
    return render_template('register.html')

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    """API endpoint for user registration."""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'username', 'email', 'password', 'company', 'department']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'All fields are required'}), 400
        
        # Check if user already exists
        if db is not None and db.users.find_one({'$or': [{'username': data['username']}, {'email': data['email']}]}):
            return jsonify({'error': 'Username or email already exists'}), 400
        
        # Hash password
        hashed_password = bcrypt.hashpw(data['password'].encode('utf-8'), bcrypt.gensalt())
        
        # Create user
        user_data = {
            'first_name': data['first_name'],
            'last_name': data['last_name'],
            'username': data['username'],
            'email': data['email'],
            'password': hashed_password,
            'company': data['company'],
            'department': data['department'],
            'level': 1,
            'score': 0,
            'role': 'Trainee',
            'created_at': datetime.now(),
            'last_login': None,
            'challenges_completed': [],
            'achievements': []
        }
        
        if db is not None:
            result = db.users.insert_one(user_data)
            user_id = result.inserted_id
            
            # Generate QR code
            qr_data = qr_manager.generate_qr_code(str(user_id), data['email'])
            
            # Send welcome email with QR code (non-blocking)
            try:
                # Send email in background to avoid blocking registration
                import threading
                def send_email_async():
                    try:
                        robust_email_manager.send_welcome_email(data['email'], f"{data['first_name']} {data['last_name']}", qr_data)
                        print(f"✅ Welcome email sent to {data['email']}")
                    except Exception as e:
                        print(f"⚠️ Failed to send email: {e}")
                
                # Start email sending in background thread
                email_thread = threading.Thread(target=send_email_async)
                email_thread.daemon = True
                email_thread.start()
                print(f"📧 Email sending started in background for {data['email']}")
            except Exception as e:
                print(f"⚠️ Failed to start email sending: {e}")
            
            return jsonify({
                'success': True,
                'message': 'Registration successful! Check your email for your QR code.',
                'user_id': str(user_id),
                'redirect_url': '/login'
            }), 200
        else:
            return jsonify({'error': 'Database connection failed'}), 500
        
    except Exception as e:
        print(f"API registration error: {e}")
        return jsonify({'error': 'Registration failed. Please try again.'}), 500

@app.route('/login', methods=['GET', 'POST'])
def login():
    """QR code login page."""
    if request.method == 'POST':
        try:
            # Handle QR code upload
            if 'qr_image' in request.files:
                file = request.files['qr_image']
                if file.filename:
                    # Process uploaded QR code
                    is_valid, user_data = qr_manager.validate_qr_code_from_image(file)
                    if is_valid and db is not None:
                        from bson import ObjectId
                        try:
                            user_id = ObjectId(user_data['user_id'])
                            user = db.users.find_one({'_id': user_id})
                        except:
                            user = db.users.find_one({'_id': user_data['user_id']})
                        
                        if user:
                            set_user_session(user)
                            flash('Login successful!', 'success')
                            return redirect('/dashboard')
                    flash('Invalid QR code. Please try again.', 'error')
            
            # Handle manual QR code input
            qr_data = request.form.get('qr_data')
            if qr_data:
                # Validate QR code data
                is_valid, user_data = qr_manager.validate_qr_code(qr_data)
                if is_valid and db is not None:
                        from bson import ObjectId
                        try:
                            user_id = ObjectId(user_data['user_id'])
                            user = db.users.find_one({'_id': user_id})
                        except:
                            user = db.users.find_one({'_id': user_data['user_id']})
                        
                        if user:
                            set_user_session(user)
                            flash('Login successful!', 'success')
                            return redirect(url_for('dashboard'))
                
                flash('Invalid QR code. Please try again.', 'error')
        
        except Exception as e:
            print(f"Login error: {e}")
            flash('Login failed. Please try again.', 'error')
    
    response = make_response(render_template('login.html'))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    """API endpoint for user login."""
    print(f"🔍 API login called - Method: {request.method}")
    print(f"🔍 Content-Type: {request.content_type}")
    print(f"🔍 Request files: {list(request.files.keys())}")
    print(f"🔍 Request form: {dict(request.form)}")
    
    try:
        # Handle QR code image upload
        if 'qr_image' in request.files:
            file = request.files['qr_image']
            if file.filename:
                print(f"📁 Processing QR image: {file.filename}")
                # Reset file pointer to beginning
                file.seek(0)
                
                is_valid, result = qr_manager.validate_qr_code_from_image(file)
                print(f"🔍 QR validation result: valid={is_valid}, result={result}")
                
                if is_valid and db is not None:
                    user_data = result  # result contains user_data when valid
                    print(f"🔍 User data from QR: {user_data}")
                    
                    # Try to find user by ID
                    user = None
                    user_id_str = str(user_data['user_id'])
                    
                    # Try ObjectId first
                    try:
                        from bson import ObjectId
                        if ObjectId.is_valid(user_id_str):
                            user_id = ObjectId(user_id_str)
                            user = db.users.find_one({'_id': user_id})
                            print(f"🔍 User found with ObjectId: {user is not None}")
                    except Exception as e:
                        print(f"🔍 ObjectId lookup failed: {e}")
                    
                    # If not found, try as string
                    if not user:
                        user = db.users.find_one({'_id': user_id_str})
                        print(f"🔍 User found with string ID: {user is not None}")
                    
                    if user:
                        print(f"🔍 Found user: {user['username']}")
                        set_user_session(user)
                        
                        # Update last login
                        db.users.update_one(
                            {'_id': user['_id']},
                            {'$set': {'last_login': datetime.now()}}
                        )
                        
                        return jsonify({
                            'success': True,
                            'message': 'Login successful!',
                            'redirect_url': '/dashboard',
                            'user': {
                                'id': str(user['_id']),
                                'username': user['username'],
                                'email': user['email'],
                                'level': user.get('level', 1),
                                'role': user.get('role', 'Trainee')
                            }
                        }), 200
                    else:
                        print(f"❌ User not found for ID: {user_id_str}")
                        return jsonify({'success': False, 'message': 'User not found'}), 404
                else:
                    error_msg = result if isinstance(result, str) else 'Invalid QR code'
                    print(f"❌ QR validation failed: {error_msg}")
                    return jsonify({'success': False, 'message': error_msg}), 400
            else:
                return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        # Handle QR code data from camera
        elif request.is_json:
            data = request.get_json()
            if data and 'qr_data' in data:
                qr_data = data['qr_data']
                print(f"📱 Processing camera QR data: {qr_data[:100]}...")
                
                is_valid, result = qr_manager.validate_qr_code(qr_data)
                print(f"🔍 Camera QR validation result: valid={is_valid}, result={result}")
                
                if is_valid and db is not None:
                    user_data = result  # result contains user_data when valid
                    print(f"🔍 User data from camera QR: {user_data}")
                    
                    # Try to find user by ID
                    user = None
                    user_id_str = str(user_data['user_id'])
                    
                    # Try ObjectId first
                    try:
                        from bson import ObjectId
                        if ObjectId.is_valid(user_id_str):
                            user_id = ObjectId(user_id_str)
                            user = db.users.find_one({'_id': user_id})
                    except Exception as e:
                        print(f"🔍 ObjectId lookup failed: {e}")
                    
                    # If not found, try as string
                    if not user:
                        user = db.users.find_one({'_id': user_id_str})
                    
                    if user:
                        print(f"🔍 Found user: {user['username']}")
                        set_user_session(user)
                        
                        # Update last login
                        db.users.update_one(
                            {'_id': user['_id']},
                            {'$set': {'last_login': datetime.now()}}
                        )
                        
                        return jsonify({
                            'success': True,
                            'message': 'Login successful!',
                            'redirect_url': '/dashboard',
                            'user': {
                                'id': str(user['_id']),
                                'username': user['username'],
                                'email': user['email'],
                                'level': user.get('level', 1),
                                'role': user.get('role', 'Trainee')
                            }
                        }), 200
                    else:
                        print(f"❌ User not found for ID: {user_id_str}")
                        return jsonify({'success': False, 'message': 'User not found'}), 404
                else:
                    error_msg = result if isinstance(result, str) else 'Invalid QR code'
                    print(f"❌ Camera QR validation failed: {error_msg}")
                    return jsonify({'success': False, 'message': error_msg}), 400
            else:
                return jsonify({'success': False, 'message': 'No QR data provided in JSON request'}), 400
        else:
            return jsonify({'success': False, 'message': 'Invalid request format. Expected file upload or JSON data.'}), 400
        
    except Exception as e:
        print(f"❌ API login error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': 'Login failed. Please try again.'}), 500

@app.route('/demo-login')
def demo_login():
    """Demo login for testing purposes."""
    try:
        if db is not None:
            # Find or create a demo user
            demo_user = db.users.find_one({'username': 'demo_user'})
            if not demo_user:
                # Create demo user
                demo_user_data = {
                    'first_name': 'Demo',
                    'last_name': 'User',
                    'username': 'demo_user',
                    'email': 'demo@securetrainer.com',
                    'password': bcrypt.hashpw('demo123'.encode('utf-8'), bcrypt.gensalt()),
                    'company': 'SecureTrainer',
                    'department': 'IT',
                    'level': 5,
                    'score': 2500,
                    'role': 'Senior Analyst',
                    'created_at': datetime.now(),
                    'last_login': datetime.now(),
                    'challenges_completed': [],
                    'achievements': ['Fast Learner', 'SQL Master', 'XSS Defender']
                }
                result = db.users.insert_one(demo_user_data)
                demo_user = demo_user_data
                demo_user['_id'] = result.inserted_id
            
            set_user_session(demo_user)
            flash('Demo login successful!', 'success')
            return redirect('/dashboard')
        else:
            flash('Database not available for demo login.', 'error')
            return redirect('/login')
    except Exception as e:
        print(f"Demo login error: {e}")
        flash('Demo login failed.', 'error')
        return redirect('/login')

@app.route('/api/auth/renew-qr', methods=['POST'])
def renew_qr_code():
    """Renew QR code for a user by email."""
    try:
        data = request.get_json()
        if not data or 'email' not in data:
            return jsonify({
                'success': False,
                'message': 'Email address is required'
            }), 400
        
        email = data['email'].strip().lower()
        print(f"🔄 Renewing QR code for email: {email}")
        
        if db is None:
            return jsonify({
                'success': False,
                'message': 'Database not available'
            }), 500
        
        # Find user by email
        user = db.users.find_one({'email': email})
        if not user:
            print(f"❌ User not found for email: {email}")
            return jsonify({
                'success': False,
                'message': 'No account found with this email address'
            }), 404
        
        print(f"✅ User found: {user['username']}")
        
        # Generate new QR code
        user_id = str(user['_id'])
        qr_data = qr_manager.generate_qr_code(user_id, email, expires_in_hours=24)
        
        if not qr_data:
            print("❌ QR code generation failed")
            return jsonify({
                'success': False,
                'message': 'Failed to generate QR code'
            }), 500
        
        print(f"✅ QR code generated: {qr_data['token']}")
        
        # Send email with new QR code
        try:
            user_full_name = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or user.get('username', 'User')
            
            # Check if user is admin
            is_admin = user.get('is_admin', False) or user.get('role') in ['admin', 'Department Head', 'Security Architect', 'Chief Security Officer']
            
            if is_admin:
                # Send admin-specific email
                email_sent = email_manager.send_admin_welcome_email(
                    email,
                    user_full_name,
                    qr_data
                )
            else:
                # Send regular user email
                email_sent = email_manager.send_welcome_email(
                    email,
                    user_full_name,
                    qr_data
                )
            
            if email_sent:
                print(f"✅ QR renewal email sent to {email}")
                return jsonify({
                    'success': True,
                    'message': 'New QR code has been sent to your email'
                }), 200
            else:
                print("❌ Email sending failed")
                return jsonify({
                    'success': False,
                    'message': 'Failed to send email. Please contact support.'
                }), 500
                
        except Exception as email_error:
            print(f"❌ Email error: {email_error}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'message': 'Failed to send email. Please contact support.'
            }), 500
    
    except Exception as e:
        print(f"❌ Renew QR error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': 'An error occurred. Please try again later.'
        }), 500

@app.route('/dashboard')
@require_auth
def dashboard():
    """Enhanced user dashboard with server-side analytics."""
    print(f"🏠 Dashboard accessed - session: {dict(session)}")
    user = get_user_from_session()
    print(f"👤 User from session: {user}")
    if not user:
        print("❌ No user found, redirecting to login")
        return redirect('/login')
    
    # Ensure user has all required fields for template
    if 'achievements' not in user:
        user['achievements'] = []
    if 'challenges_completed' not in user:
        user['challenges_completed'] = []
    
    # Get comprehensive analytics
    from app.models.analytics_model import get_dashboard_analytics
    analytics = get_dashboard_analytics(str(user['_id']))
    
    if not analytics:
        # Fallback analytics
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
    
    print(f"📊 Dashboard analytics: {analytics}")
    return render_template('dashboard.html', user=user, analytics=analytics)


@app.route('/dashboard/refresh')
@require_auth  
def dashboard_refresh():
    """AJAX endpoint for dashboard data refresh."""
    user = get_user_from_session()
    if not user:
        return jsonify({'error': 'Not authenticated'}), 401
    
    # Get updated user data
    from bson import ObjectId
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
            'role': updated_user.get('role', 'Trainee')
        })
    
    return jsonify({'success': False}), 500

@app.route('/challenges')
@require_auth
def challenges():
    """Enhanced challenges page with server-side rendering."""
    user = get_user_from_session()
    if not user:
        return redirect('/login')
    
    # Get available challenges organized by category
    from app.models.challenge_model import get_all_challenges
    all_challenges = get_all_challenges()
    
    # Organize challenges by category
    challenges_by_category = {
        'sql_injection': [],
        'xss': [],
        'command_injection': [],
        'authentication': [],
        'csrf': []
    }
    
    for challenge in all_challenges:
        category = challenge.get('category', 'sql_injection')
        if category in challenges_by_category:
            challenges_by_category[category].append(challenge)
    
    # Get user progress
    completed_challenges = user.get('challenges_completed', [])
    
    return render_template('challenges.html', 
                         user=user, 
                         challenges_by_category=challenges_by_category,
                         completed_challenges=completed_challenges)


@app.route('/challenges/start', methods=['GET', 'POST'])
@require_auth
def start_challenge():
    """Start a challenge with server-side form handling."""
    user = get_user_from_session()
    if not user:
        return redirect('/login')
    
    if request.method == 'GET':
        # Handle category selection
        category = request.args.get('category', 'sql_injection')
        
        # Get appropriate challenge
        from app.models.challenge_model import get_user_appropriate_challenges
        challenges = get_user_appropriate_challenges(user, category)
        
        if challenges:
            challenge = challenges[0]  # Get first appropriate challenge
        else:
            # Fallback to a basic challenge
            challenge = {
                'id': 'basic_sql_1',
                'title': 'Basic SQL Injection',
                'category': 'sql_injection',
                'difficulty': 'beginner',
                'scenario': 'You found a login form that might be vulnerable to SQL injection.',
                'question': 'Try to bypass the authentication using SQL injection techniques.',
                'expected_solutions': ["' OR '1'='1", "admin' --", "' OR 1=1 --"],
                'hints': [
                    "Think about how SQL queries work with user input",
                    "Try using OR statements to make conditions always true",
                    "Consider using comment operators to ignore parts of the query"
                ]
            }
        
        # Store challenge in session
        session['current_challenge'] = challenge
        session['challenge_start_time'] = datetime.now().isoformat()
        session['attempts_count'] = 0
        session['hints_used'] = 0
        
        return render_template('challenge_interface.html', user=user, challenge=challenge)
    
    # Handle POST (challenge submission)
    challenge = session.get('current_challenge')
    if not challenge:
        flash('No active challenge found. Please start a new challenge.', 'error')
        return redirect('/challenges')
    
    submitted_answer = request.form.get('answer', '').strip()
    action = request.form.get('action', 'submit')
    
    if action == 'hint':
        # Handle hint request
        hints_used = session.get('hints_used', 0)
        hints = challenge.get('hints', [])
        
        if hints_used < len(hints):
            hint = hints[hints_used]
            session['hints_used'] = hints_used + 1
            flash(f'Hint: {hint}', 'info')
        else:
            flash('No more hints available for this challenge.', 'warning')
        
        return render_template('challenge_interface.html', user=user, challenge=challenge)
    
    # Handle solution submission
    if not submitted_answer:
        flash('Please provide an answer before submitting.', 'error')
        return render_template('challenge_interface.html', user=user, challenge=challenge)
    
    # Update attempts count
    attempts_count = session.get('attempts_count', 0) + 1
    session['attempts_count'] = attempts_count
    
    # Validate solution
    expected_solutions = challenge.get('expected_solutions', [])
    is_correct = any(sol.lower() in submitted_answer.lower() for sol in expected_solutions)
    
    if is_correct:
        # Calculate score
        base_score = challenge.get('points', 100)
        hints_penalty = session.get('hints_used', 0) * 10
        attempts_penalty = (attempts_count - 1) * 5
        score_earned = max(base_score - hints_penalty - attempts_penalty, 10)
        
        # Update user score and level
        if db is not None:
            new_score = user.get('score', 0) + score_earned
            new_level = (new_score // 1000) + 1
            
            db.users.update_one(
                {'_id': user['_id']},
                {
                    '$inc': {'score': score_earned},
                    '$set': {'level': new_level},
                    '$addToSet': {'challenges_completed': challenge['id']}
                }
            )
            
            # Record challenge attempt
            from app.models.analytics_model import record_user_activity
            start_time = datetime.fromisoformat(session.get('challenge_start_time'))
            completion_time = (datetime.now() - start_time).total_seconds()
            
            record_user_activity(str(user['_id']), 'challenge_completion', {
                'challenge_id': challenge['id'],
                'category': challenge['category'],
                'score_earned': score_earned,
                'completion_time': completion_time,
                'attempts': attempts_count,
                'hints_used': session.get('hints_used', 0)
            })
        
        # Clear session challenge data
        session.pop('current_challenge', None)
        session.pop('challenge_start_time', None)
        session.pop('attempts_count', None)
        session.pop('hints_used', None)
        
        flash(f'Congratulations! Challenge completed successfully. You earned {score_earned} points!', 'success')
        return redirect('/dashboard')
    else:
        # Incorrect answer
        flash(f'Incorrect answer. Try again! (Attempt {attempts_count})', 'error')
        return render_template('challenge_interface.html', user=user, challenge=challenge)

@app.route('/learning-center')
@require_auth
def learning_center():
    """Learning Center page."""
    user = get_user_from_session()
    if not user:
        return redirect('/login')
    
    return render_template('learning-center.html', user=user)

@app.route('/api/challenges/start/<user_id>', methods=['GET'])
@require_auth
def api_start_challenge(user_id):
    """Enhanced API endpoint for starting challenges with server-side validation."""
    try:
        category = request.args.get('category', 'sql_injection')
        user = get_user_from_session()
        if not user:
            return jsonify({'error': 'Not authenticated'}), 401
            
        # Get appropriate challenge
        from app.models.challenge_model import get_user_appropriate_challenges
        challenges = get_user_appropriate_challenges(user, category)
        
        if challenges:
            challenge = challenges[0]
        else:
            # Fallback challenge
            challenge = {
                'id': f'basic_{category}_1',
                'title': f'Basic {category.replace("_", " ").title()}',
                'category': category,
                'difficulty': 'beginner',
                'scenario': f'Practice {category.replace("_", " ")} vulnerability detection and exploitation.',
                'question': f'Identify and exploit the {category.replace("_", " ")} vulnerability.',
                'expected_solutions': ["' OR '1'='1", "admin' --", "' OR 1=1 --"],
                'hints': [
                    f"Think about how {category.replace('_', ' ')} attacks work",
                    "Consider the input validation mechanisms",
                    "Try different payload variations"
                ],
                'points': 100
            }
        
        return jsonify({
            'success': True,
            'challenge': challenge
        }), 200
        
    except Exception as e:
        print(f"Error in API start challenge: {e}")
        return jsonify({'error': 'Failed to start challenge'}), 500

@app.route('/api/challenges/submit', methods=['POST'])
@require_auth
def submit_challenge():
    """Submit challenge solution."""
    try:
        data = request.get_json()
        challenge_id = data.get('challenge_id')
        solution = data.get('solution')
        
        if not challenge_id or not solution or db is None:
            return jsonify({'error': 'Invalid submission'}), 400
        
        challenge = db.challenges.find_one({'_id': challenge_id})
        if not challenge:
            return jsonify({'error': 'Challenge not found'}), 404
        
        user = get_user_from_session()
        
        # Simple solution validation (in production, this would be more sophisticated)
        is_correct = solution.lower() in challenge.get('expected_solutions', [])
        
        if is_correct:
            # Award points
            points_earned = challenge.get('points', 10)
            new_score = user.get('score', 0) + points_earned
            new_level = (new_score // 1000) + 1
            
            # Update user
            db.users.update_one(
                {'_id': user['_id']},
                {
                    '$inc': {'score': points_earned},
                    '$set': {'level': new_level},
                    '$addToSet': {'challenges_completed': challenge_id}
                }
            )
            
            return jsonify({
                'success': True,
                'correct': True,
                'points_earned': points_earned,
                'new_score': new_score,
                'new_level': new_level
            }), 200
        else:
            return jsonify({
                'success': True,
                'correct': False,
                'message': 'Incorrect solution. Try again!'
            }), 200
        
    except Exception as e:
        print(f"Submit challenge error: {e}")
        return jsonify({'error': 'Failed to submit solution'}), 500

@app.route('/api/challenges/hint', methods=['POST'])
@require_auth
def get_hint():
    """Get hint for a challenge."""
    try:
        data = request.get_json()
        challenge_id = data.get('challenge_id')
        
        if not challenge_id or db is None:
            return jsonify({'error': 'Invalid challenge ID'}), 400
        
        challenge = db.challenges.find_one({'_id': challenge_id})
        if not challenge:
            return jsonify({'error': 'Challenge not found'}), 404
        
        user = get_user_from_session()
        attempt_count = data.get('attempt_count', 0)
        
        # Generate adaptive hint
        hint = generate_adaptive_hint(user, challenge, attempt_count)
        
        return jsonify({
            'success': True,
            'hint': hint
        }), 200
        
    except Exception as e:
        print(f"Get hint error: {e}")
        return jsonify({'error': 'Failed to get hint'}), 500

@app.route('/api/ai/recommendations', methods=['GET'])
@require_auth
def get_ai_recommendations():
    """Get AI-powered challenge recommendations."""
    try:
        user = get_user_from_session()
        if not user or db is None:
            return jsonify({'error': 'User not found'}), 404
        
        # Analyze user learning patterns
        patterns = analyze_user_learning_patterns(user)
        
        # Get recommended challenges
        recommended_challenges = []
        if db is not None:
            challenges_cursor = db.challenges.find({
                'level': {'$lte': user.get('level', 1) + 1},
                'category': {'$in': patterns.get('preferred_challenge_types', [])}
            }).limit(5)
            recommended_challenges = list(challenges_cursor)
        
        return jsonify({
            'success': True,
            'recommendations': recommended_challenges,
            'patterns': patterns
        }), 200
        
    except Exception as e:
        print(f"AI recommendations error: {e}")
        return jsonify({'error': 'Failed to get recommendations'}), 500

@app.route('/api/challenges/list', methods=['GET'])
@require_auth
def list_challenges_api():
    """List all available challenges."""
    try:
        challenges = get_all_challenges()
        return jsonify({
            'success': True,
            'challenges': challenges
        }), 200
    except Exception as e:
        print(f"Error listing challenges: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to load challenges'
        }), 500

@app.route('/api/challenges/<challenge_id>', methods=['GET'])
@require_auth
def get_challenge_api(challenge_id):
    """Get a specific challenge by ID."""
    try:
        challenge = get_challenge_by_id(challenge_id)
        if challenge:
            return jsonify({
                'success': True,
                'challenge': challenge
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Challenge not found'
            }), 404
    except Exception as e:
        print(f"Error getting challenge: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to load challenge'
        }), 500

@app.route('/api/challenges/category/<category>', methods=['GET'])
@require_auth
def get_challenges_by_category_api(category):
    """Get challenges by category."""
    try:
        challenges = get_challenges_by_category(category)
        return jsonify({
            'success': True,
            'challenges': challenges
        }), 200
    except Exception as e:
        print(f"Error getting challenges by category: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to load challenges'
        }), 500

@app.route('/api/challenges/difficulty/<difficulty>', methods=['GET'])
@require_auth
def get_challenges_by_difficulty_api(difficulty):
    """Get challenges by difficulty level."""
    try:
        challenges = get_challenges_by_difficulty(difficulty)
        return jsonify({
            'success': True,
            'challenges': challenges
        }), 200
    except Exception as e:
        print(f"Error getting challenges by difficulty: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to load challenges'
        }), 500

@app.route('/api/user/stats', methods=['GET'])
@require_auth
def get_user_stats():
    """Get user statistics."""
    try:
        user = get_user_from_session()
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        stats = {
            'username': user['username'],
            'level': user.get('level', 1),
            'score': user.get('score', 0),
            'role': user.get('role', 'Trainee'),
            'challenges_completed': len(user.get('challenges_completed', [])),
            'achievements': user.get('achievements', []),
            'department': user.get('department', 'Unknown'),
            'company': user.get('company', 'Unknown')
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        }), 200
        
    except Exception as e:
        print(f"Get user stats error: {e}")
        return jsonify({'error': 'Failed to get user stats'}), 500

@app.route('/logout')
def logout():
    """Logout user."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect('/login')

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

# Health check endpoint
@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0',
        'database': 'connected' if db is not None else 'disconnected'
    })

# Analytics performance endpoint (stub to prevent 404)
@app.route('/api/analytics/performance', methods=['POST', 'GET'])
def analytics_performance():
    """Performance analytics endpoint stub."""
    return jsonify({
        'success': True,
        'message': 'Performance data recorded',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Clean up expired QR codes
    qr_manager.cleanup_expired_codes()
    
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print("🚀 Starting SecureTrainer...")
    print(f"📍 Port: {port}")
    print(f"🔧 Debug: {debug}")
    print(f"📧 Mail: {app.config['MAIL_USERNAME']}")
    print(f"🗄️ Database: {'Connected' if db is not None else 'Disconnected'}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)