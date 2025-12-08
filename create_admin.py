from app.models.user_model import insert_user
from app.utils.security import hash_password
from app.utils.qr import QRCodeManager
from datetime import datetime
from flask import Flask
from app.database.db_manager import initialize_database_manager
import os

# Initialize Flask app context
app = Flask(__name__)
app.config['MONGO_URI'] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/securetrainer')

# Initialize DB
initialize_database_manager(app.config['MONGO_URI'])

def create_admin_user():
    print("Creating admin user...")
    
    admin_user = {
        "first_name": "System",
        "last_name": "Admin",
        "username": "admin",
        "email": "azeemwaqar.work@gmail.com",
        "password": hash_password("admin123"),
        "company": "SecureTrainer",
        "department": "Administration",
        "score": 99999,
        "level": 50,
        "role": "Chief Security Officer",
        "is_admin": True,
        "admin_role": "super_admin",
        "created_at": datetime.now()
    }
    
    with app.app_context():
        try:
            user_id = insert_user(admin_user)
            print(f"Admin user created successfully with ID: {user_id}")
            
            # Generate QR code
            qr_manager = QRCodeManager()
            qr_data = qr_manager.generate_qr_code(user_id, admin_user['email'])
            print(f"QR Code generated. You can find it in the qr_codes directory.")
            
        except Exception as e:
            print(f"Error creating admin user: {e}")

if __name__ == "__main__":
    create_admin_user()
