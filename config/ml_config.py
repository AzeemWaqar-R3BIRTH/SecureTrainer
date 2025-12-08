"""
ML Configuration for SecureTrainer
Defines hyperparameters, features, and training settings
"""

# Model Hyperparameters
MODEL_CONFIG = {
    'n_estimators': 100,
    'max_depth': 10,
    'min_samples_split': 5,
    'min_samples_leaf': 2,
    'random_state': 42,
    'n_jobs': -1
}

# Feature Definitions
FEATURE_NAMES = [
    'level',
    'score',
    'hint_count',
    'challenges_completed',
    'success_rate',
    'avg_completion_time',
    'consecutive_successes',
    'consecutive_failures',
    'days_since_registration',
    'sql_injection_score',
    'xss_score',
    'command_injection_score',
    'authentication_score',
    'csrf_score'
]

# Difficulty Labels
DIFFICULTY_LABELS = ['beginner', 'intermediate', 'advanced', 'expert']

# Training Configuration
TRAINING_CONFIG = {
    'test_size': 0.2,
    'validation_size': 0.1,
    'random_state': 42,
    'min_samples_per_class': 10,
    'feature_scaling': True
}

# Data Export Configuration
EXPORT_CONFIG = {
    'min_user_challenges': 0,  # Lowered to 0 to include all users with any activity
    'exclude_inactive_days': 365,  # Increased to 1 year to include more users
    'output_file': 'data/training_data.csv'
}

# Retraining Configuration
RETRAIN_CONFIG = {
    'min_new_samples': 100,  # Minimum new samples to trigger retraining
    'schedule': 'weekly',  # Options: 'daily', 'weekly', 'monthly'
    'backup_old_model': True,
    'model_version_format': 'v{version}_{timestamp}'
}

# Model Paths
MODEL_PATHS = {
    'model': 'model/challenge_difficulty_model.pkl',
    'encoder': 'model/label_encoder.pkl',
    'scaler': 'model/feature_scaler.pkl',
    'backup_dir': 'model/backups/',
    'metrics': 'model/metrics.json'
}

# MongoDB Configuration
MONGO_CONFIG = {
    'collections': {
        'users': 'users',
        'challenge_attempts': 'challenge_attempts',
        'analytics': 'user_analytics'
    }
}
