"""
Enhanced SecureTrainer Application with Advanced Validation System
Integrates the new enhanced validation and learning systems
"""

from flask import Flask
from flask_cors import CORS
import os
import logging

def create_app():
    """Create and configure the Flask application with enhanced features."""
    app = Flask(__name__)
    
    # Configure CORS
    CORS(app)
    
    # Configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    app.config['MONGO_URI'] = os.environ.get('MONGO_URI', 'mongodb://localhost:27017/securetrainer')
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Initialize database connection
    try:
        from pymongo import MongoClient
        client = MongoClient(app.config['MONGO_URI'])
        app.config['MONGO_CLIENT'] = client
        logging.info("MongoDB connection established")
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}")
    
    # Register blueprints
    try:
        # Page routes (non-API)
        from app.routes.pages import pages_bp
        
        # Core routes
        from app.routes.auth import auth_bp
        from app.routes.dashboard import dashboard_bp
        from app.routes.challenge import challenge_bp
        from app.routes.learning import learning_bp
        from app.routes.leaderboard import leaderboard_bp
        
        # Admin routes
        from app.routes.admin import admin_bp
        
        # Enhanced validation system
        from app.routes.enhanced_validation_api import enhanced_validation_bp
        
        # ML Training routes
        from app.routes.ml_routes import ml_bp
        
        # Register all blueprints
        app.register_blueprint(pages_bp)  # Register pages first (handles root routes)
        app.register_blueprint(auth_bp)
        app.register_blueprint(dashboard_bp)
        app.register_blueprint(challenge_bp, url_prefix='/api/challenges')
        app.register_blueprint(learning_bp)
        app.register_blueprint(leaderboard_bp, url_prefix='/api/leaderboard')
        app.register_blueprint(admin_bp)  # Admin routes with /admin prefix
        app.register_blueprint(enhanced_validation_bp)
        app.register_blueprint(ml_bp)  # ML training routes
        
        logging.info("All blueprints registered successfully")
        
    except Exception as e:
        logging.error(f"Error registering blueprints: {e}")
    
    # Initialize enhanced validation system
    try:
        from app.ai.advanced_answer_validation import advanced_validator
        from app.utils.enhanced_learning_system import learning_content_manager
        
        # Warm up the validation system
        advanced_validator.validate_challenge_answer("warmup", "test", {"warmup": True})
        
        # Test learning content manager
        learning_content_manager.get_content_with_fallback("warmup")
        
        logging.info("Enhanced validation and learning systems initialized")
        
    except Exception as e:
        logging.warning(f"Enhanced systems initialization warning: {e}")
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """System health check endpoint."""
        try:
            from app.ai.advanced_answer_validation import advanced_validator
            from app.utils.enhanced_learning_system import get_learning_performance_metrics
            
            # Basic health checks
            validation_stats = advanced_validator.get_validation_statistics()
            learning_metrics = get_learning_performance_metrics()
            
            health_status = {
                'status': 'healthy',
                'validation_system': 'operational',
                'learning_system': 'operational',
                'database': 'connected' if app.config.get('MONGO_CLIENT') else 'disconnected',
                'validation_accuracy': validation_stats.get('success_rate', 0),
                'cache_hit_rate': learning_metrics.get('cache_hit_rate', 0),
                'total_validations': validation_stats.get('total_validations', 0)
            }
            
            return health_status, 200
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }, 500
    
    # Root endpoint
    @app.route('/')
    def index():
        """Root endpoint with system information."""
        return {
            'message': 'SecureTrainer Enhanced Validation System',
            'version': '2.0.0',
            'features': [
                'Multi-layer answer validation',
                'Advanced semantic analysis', 
                'Pattern recognition',
                'Enhanced learning system',
                'Performance optimization',
                'Comprehensive error handling'
            ],
            'status': 'operational',
            'health_check': '/health'
        }
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {
            'error': 'Endpoint not found',
            'message': 'The requested resource was not found',
            'available_endpoints': [
                '/health - System health check',
                '/api/validation/ - Enhanced validation endpoints',
                '/api/learning/ - Enhanced learning endpoints'
            ]
        }, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {
            'error': 'Internal server error',
            'message': 'An internal error occurred. Please check the logs.'
        }, 500
    
    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    # Development server
    app.run(
        debug=os.environ.get('FLASK_ENV') == 'development',
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000))
    )