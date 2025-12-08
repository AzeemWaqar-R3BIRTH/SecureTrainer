# Registration & QR login
from flask import Blueprint, request, jsonify, current_app
from app.utils.qr import QRCodeManager
from app.utils.email import EmailManager
from app.utils.security import hash_password
from app.models.user_model import insert_user, get_user_by_email

# Initialize managers
qr_manager = QRCodeManager()

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    required = ['first_name', 'last_name', 'username', 'email', 'password', 'company', 'department']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400

    # Hash password
    hashed_pw = hash_password(data['password'])

    # Create user object
    user = {
        "first_name": data['first_name'],
        "last_name": data['last_name'],
        "username": data['username'],
        "email": data['email'],
        "password": hashed_pw,
        "company": data['company'],
        "department": data['department'],
        "score": 0,
        "level": 1,
        "role": "Trainee"
    }

    try:
        # Insert to DB
        uid = insert_user(user)

        # Generate login QR
        qr_data = qr_manager.generate_qr_code(uid, user['email'])

        # Email QR code
        try:
            from securetrainer import email_manager
            print(f"📧 Attempting to send email to {user['email']}")
            result = email_manager.send_welcome_email(user['email'], f"{user['first_name']} {user['last_name']}", qr_data)
            print(f"📧 Email send result: {result}")
        except Exception as e:
            print(f"❌ Email sending failed: {e}")
            import traceback
            traceback.print_exc()

        return jsonify({'message': 'Registration successful. Check email for QR login.'}), 200
    
    except Exception as e:
        # Check if it's a duplicate key error
        if 'duplicate key error' in str(e).lower() or 'E11000' in str(e):
            if 'email' in str(e):
                return jsonify({'error': 'This email address is already registered. Please use a different email or sign in.'}), 400
            elif 'username' in str(e):
                return jsonify({'error': 'This username is already taken. Please choose a different username.'}), 400
            else:
                return jsonify({'error': 'This account already exists. Please use different credentials.'}), 400
        else:
            # Other errors
            print(f"❌ Registration error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': 'Registration failed. Please try again later.'}), 500


@auth_bp.route('/renew-qr', methods=['POST'])
def renew_qr():
    """Request a new QR code via email"""
    data = request.json
    email = data.get('email')
    
    if not email:
        return jsonify({'error': 'Email address is required'}), 400
    
    # Find user by email
    user = get_user_by_email(email)
    
    if not user:
        # Don't reveal if email exists or not (security)
        return jsonify({'message': 'If this email is registered, a new QR code has been sent to your inbox.'}), 200
    
    try:
        # Generate new QR code
        qr_data = qr_manager.generate_qr_code(str(user['_id']), user['email'])
        
        # Send email with new QR code
        from securetrainer import email_manager
        print(f"📧 Sending QR renewal email to {user['email']}")
        result = email_manager.send_qr_renewal_email(
            user['email'], 
            f"{user.get('first_name', '')} {user.get('last_name', '')}".strip() or user.get('username', 'User'), 
            qr_data
        )
        print(f"📧 QR renewal email result: {result}")
        
        return jsonify({'message': 'If this email is registered, a new QR code has been sent to your inbox.'}), 200
    
    except Exception as e:
        print(f"❌ QR renewal error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to send QR code. Please try again later.'}), 500
