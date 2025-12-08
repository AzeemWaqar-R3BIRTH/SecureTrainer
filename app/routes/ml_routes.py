"""
ML Training API Routes
Provides endpoints for triggering training and viewing model status
"""

from flask import Blueprint, jsonify, request
from functools import wraps
import os
import json
import subprocess
from datetime import datetime

ml_bp = Blueprint('ml', __name__, url_prefix='/api/ml')


def require_admin(f):
    """Decorator to require admin authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Import here to avoid circular imports
        from app.models.user_model import get_current_user
        
        user = get_current_user()
        if not user or user.get('role') != 'admin':
            return jsonify({
                'success': False,
                'error': 'Admin access required'
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function


@ml_bp.route('/status', methods=['GET'])
@require_admin
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
        # Run export script
        script_path = os.path.join('scripts', 'export_training_data.py')
        
        result = subprocess.run(
            ['python', script_path],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
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
        # Run training script
        script_path = os.path.join('scripts', 'train_difficulty_model.py')
        
        result = subprocess.run(
            ['python', script_path],
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout
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
        
        # Run retraining script
        script_path = os.path.join('scripts', 'retrain_model.py')
        cmd = ['python', script_path]
        
        if force:
            cmd.append('--force')
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=900  # 15 minute timeout
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
@require_admin
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
