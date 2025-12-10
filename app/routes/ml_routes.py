"""
ML Training API Routes
Provides endpoints for triggering training and viewing model status
"""

from flask import Blueprint, jsonify, request, session
from functools import wraps
import os
import json
import subprocess
from datetime import datetime

ml_bp = Blueprint('ml', __name__, url_prefix='/api/ml')


def require_admin(f):
    """Decorator to require admin authentication (shared with admin panel)."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # 1) Must have user_id in session
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({
                    'success': False,
                    'error': 'Authentication required. Please log in as admin.'
                }), 401

            # 2) Use same user lookup as admin.py
            from app.models.user_model import get_user_by_id
            user = get_user_by_id(user_id)
            if not user:
                return jsonify({
                    'success': False,
                    'error': 'User not found. Please log in again.'
                }), 401

            # 3) Use same admin rules as admin.is_admin
            role = (user.get('role') or '').strip()
            is_admin_flag = user.get('is_admin', False)
            allowed_roles = ['admin', 'Department Head', 'Security Architect', 'Chief Security Officer']

            if not (is_admin_flag or role in allowed_roles):
                return jsonify({
                    'success': False,
                    'error': 'Admin access required.'
                }), 403

            return f(*args, **kwargs)

        except Exception as e:
            # Fail closed but with clear JSON error
            return jsonify({
                'success': False,
                'error': f'Authentication error: {str(e)}'
            }), 500

    return decorated_function

@ml_bp.route('/status', methods=['GET'])
def get_ml_status():
    """Get current ML model status."""
    try:
        # Check if model exists
        model_path = 'model/challenge_difficulty_model.pkl'
        metrics_path = 'model/metrics.json'
        
        if not os.path.exists(model_path):
            return jsonify({
                'success': True,
                'model_exists': False,
                'message': 'No trained model found'
            }), 200
        
        # Load metrics
        metrics = {}
        if os.path.exists(metrics_path):
            with open(metrics_path, 'r') as f:
                metrics = json.load(f)
        
        # Get model file info
        model_size = os.path.getsize(model_path)
        model_modified = datetime.fromtimestamp(os.path.getmtime(model_path))
        
        return jsonify({
            'success': True,
            'model_exists': True,
            'model_info': {
                'size_bytes': model_size,
                'last_modified': model_modified.isoformat(),
                'accuracy': metrics.get('accuracy', 0),
                'training_date': metrics.get('training_date'),
                'training_samples': metrics.get('training_samples', 0)
            },
            'metrics': metrics
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ml_bp.route('/export-data', methods=['POST'])
@require_admin
def export_training_data():
    """Trigger data export from MongoDB."""
    try:
        # Get the root directory of the project
        root_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        script_path = os.path.join(root_dir, 'scripts', 'export_training_data.py')
        
        # Run from root directory to ensure correct paths
        result = subprocess.run(
            ['python', script_path],
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            cwd=root_dir  # Set working directory to project root
        )
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': 'Data exported successfully',
                'output': result.stdout
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Export failed',
                'output': result.stderr
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Export timed out'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ml_bp.route('/train', methods=['POST'])
@require_admin
def train_model():
    """Trigger model training."""
    try:
        # Get the root directory of the project
        root_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        script_path = os.path.join(root_dir, 'scripts', 'train_difficulty_model.py')
        
        # Run from root directory to ensure correct paths
        result = subprocess.run(
            ['python', script_path],
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout
            cwd=root_dir  # Set working directory to project root
        )
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': 'Model trained successfully',
                'output': result.stdout
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Training failed',
                'output': result.stderr
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Training timed out'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ml_bp.route('/retrain', methods=['POST'])
@require_admin
def retrain_model():
    """Trigger automated retraining pipeline."""
    try:
        force = request.json.get('force', False) if request.is_json else False
        
        # Get the root directory of the project
        root_dir = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        script_path = os.path.join(root_dir, 'scripts', 'retrain_model.py')
        
        cmd = ['python', script_path]
        if force:
            cmd.append('--force')
        
        # Run from root directory to ensure correct paths
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=900,  # 15 minute timeout
            cwd=root_dir  # Set working directory to project root
        )
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': 'Retraining completed successfully',
                'output': result.stdout
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Retraining failed',
                'output': result.stderr
            }), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Retraining timed out'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@ml_bp.route('/metrics', methods=['GET'])
def get_model_metrics():
    """Get detailed model metrics."""
    try:
        metrics_path = 'model/metrics.json'
        
        if not os.path.exists(metrics_path):
            return jsonify({
                'success': False,
                'error': 'No metrics file found'
            }), 404
        
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
        
        return jsonify({
            'success': True,
            'metrics': metrics
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
