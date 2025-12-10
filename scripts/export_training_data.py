"""Data Export Script for ML Training
Exports user performance data from MongoDB for model training
"""

import os
import sys
from datetime import datetime, timedelta
import pandas as pd
from pymongo import MongoClient

# Windows console encoding fix - store original print first
import builtins
original_print = builtins.print

def safe_print(*args, **kwargs):
    """Print with fallback for Windows console encoding."""
    try:
        original_print(*args, **kwargs)
    except UnicodeEncodeError:
        # Replace Unicode symbols with ASCII alternatives
        message = ' '.join(str(arg) for arg in args)
        message = message.replace('\u2713', '[OK]').replace('\u2705', '[SUCCESS]')
        message = message.replace('\u26a0\ufe0f', '[WARNING]').replace('\u274c', '[ERROR]')
        message = message.replace('\u2717', '[X]')
        original_print(message, **kwargs)

# Override built-in print
builtins.print = safe_print

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.ml_config import FEATURE_NAMES, EXPORT_CONFIG, MONGO_CONFIG


def get_db_connection():
    """Get MongoDB connection."""
    mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/securetrainer')
    client = MongoClient(mongo_uri)
    return client.get_database()


def calculate_user_features(user, db):
    """Calculate features for a single user."""
    user_id = str(user['_id'])
    
    # Basic features
    features = {
        'user_id': user_id,
        'level': user.get('level', 1),
        'score': user.get('score', 0),
        'hint_count': user.get('hint_count', 0),
        'challenges_completed': len(user.get('challenges_completed', []))
    }
    
    # Get challenge attempts
    attempts = list(db.challenge_attempts.find({'user_id': user_id}))
    
    if attempts:
        # Calculate success rate
        successful = sum(1 for a in attempts if a.get('is_correct', False))
        features['success_rate'] = successful / len(attempts) if attempts else 0
        
        # Calculate average completion time
        completion_times = [a.get('completion_time', 0) for a in attempts if a.get('completion_time')]
        features['avg_completion_time'] = sum(completion_times) / len(completion_times) if completion_times else 300
        
        # Calculate consecutive successes/failures
        recent_attempts = sorted(attempts, key=lambda x: x.get('attempt_time', datetime.now()), reverse=True)[:10]
        consecutive_successes = 0
        consecutive_failures = 0
        
        for attempt in recent_attempts:
            if attempt.get('is_correct', False):
                consecutive_successes += 1
                break
            else:
                consecutive_failures += 1
        
        features['consecutive_successes'] = consecutive_successes
        features['consecutive_failures'] = consecutive_failures
        
        # Category-specific scores
        categories = {
            'sql_injection': 0,
            'xss': 0,
            'command_injection': 0,
            'authentication': 0,
            'csrf': 0
        }
        
        for attempt in attempts:
            category = attempt.get('category', '').lower().replace(' ', '_')
            if category in categories and attempt.get('is_correct', False):
                categories[category] += attempt.get('score_earned', 0)
        
        features['sql_injection_score'] = categories['sql_injection']
        features['xss_score'] = categories['xss']
        features['command_injection_score'] = categories['command_injection']
        features['authentication_score'] = categories['authentication']
        features['csrf_score'] = categories['csrf']
    else:
        # Default values for users with no attempts
        features['success_rate'] = 0.5
        features['avg_completion_time'] = 300
        features['consecutive_successes'] = 0
        features['consecutive_failures'] = 0
        features['sql_injection_score'] = 0
        features['xss_score'] = 0
        features['command_injection_score'] = 0
        features['authentication_score'] = 0
        features['csrf_score'] = 0
    
    # Days since registration
    registration_date = user.get('created_at', datetime.now())
    if registration_date is None:
        registration_date = datetime.now()
    if isinstance(registration_date, str):
        try:
            registration_date = datetime.fromisoformat(registration_date)
        except:
            registration_date = datetime.now()
    features['days_since_registration'] = (datetime.now() - registration_date).days
    
    # Determine difficulty label (target variable)
    features['difficulty_label'] = determine_difficulty_label(features)
    
    return features


def determine_difficulty_label(features):
    """Determine appropriate difficulty label based on user performance."""
    # This is a heuristic - you can adjust based on your criteria
    level = features['level']
    success_rate = features['success_rate']
    challenges_completed = features['challenges_completed']
    
    # Calculate difficulty score
    score = level * 10 + success_rate * 50 + min(challenges_completed, 20) * 2
    
    if score >= 80:
        return 'expert'
    elif score >= 60:
        return 'advanced'
    elif score >= 40:
        return 'intermediate'
    else:
        return 'beginner'


def export_training_data():
    """Export training data from MongoDB."""
    print("=" * 60)
    print("SecureTrainer ML Data Export")
    print("=" * 60)
    
    # Connect to database
    print("\n[1/4] Connecting to MongoDB...")
    db = get_db_connection()
    print("✓ Connected successfully")
    
    # Get users
    print("\n[2/4] Fetching users...")
    min_challenges = EXPORT_CONFIG['min_user_challenges']
    cutoff_date = datetime.now() - timedelta(days=EXPORT_CONFIG['exclude_inactive_days'])
    
    # Query active users with minimum challenges
    # Modified to handle missing created_at field
    users = list(db.users.find({
        'role': {'$ne': 'admin'},
        '$or': [
            {'created_at': {'$gte': cutoff_date}},
            {'created_at': {'$exists': False}},  # Include users without created_at
            {'last_login': {'$gte': cutoff_date}}  # Or recently active users
        ]
    }))
    
    print(f"✓ Found {len(users)} users")
    
    # Extract features
    print("\n[3/4] Extracting features...")
    training_data = []
    
    for i, user in enumerate(users, 1):
        try:
            features = calculate_user_features(user, db)
            
            # Only include users with minimum challenges
            if features['challenges_completed'] >= min_challenges:
                training_data.append(features)
            
            if i % 50 == 0:
                print(f"  Processed {i}/{len(users)} users...")
        except Exception as e:
            print(f"  Warning: Error processing user {user.get('_id')}: {e}")
            continue
    
    print(f"✓ Extracted features for {len(training_data)} users")
    
    # Minimum required users for robust training
    MIN_USERS_FOR_REAL_DATA = 100
    
    # Check if we should use synthetic data instead
    if len(training_data) < MIN_USERS_FOR_REAL_DATA:
        print("\n" + "=" * 60)
        print(f"⚠️ Insufficient real data: {len(training_data)} users (need {MIN_USERS_FOR_REAL_DATA})")
        print("=" * 60)
        print("Automatically switching to synthetic data for robust model training...")
        print()
        
        # Generate synthetic data
        try:
            # Import the synthetic data generator
            import sys
            import os
            parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            sys.path.insert(0, parent_dir)
            
            from generate_demo_training_data import generate_synthetic_users
            
            print("Generating 20,000 synthetic users with 15% outliers...")
            df_synthetic = generate_synthetic_users(num_users=20000, outlier_percentage=0.15)
            
            # Save synthetic data
            print("\n[4/4] Saving synthetic data to CSV...")
            os.makedirs('data', exist_ok=True)
            output_file = EXPORT_CONFIG['output_file']
            df_synthetic.to_csv(output_file, index=False)
            
            print(f"✓ Saved to {output_file}")
            
            # Print statistics
            print("\n" + "=" * 60)
            print("Synthetic Data Statistics")
            print("=" * 60)
            print(f"Total samples: {len(df_synthetic):,}")
            print(f"\nDifficulty distribution:")
            print(df_synthetic['difficulty_label'].value_counts().sort_index())
            print(f"\nFeature summary:")
            print(df_synthetic[FEATURE_NAMES].describe())
            print("=" * 60)
            print("\n✅ Using synthetic data for training!")
            print("This ensures robust model training with diverse outliers.")
            print("=" * 60)
            
            return output_file
            
        except Exception as e:
            print(f"\n❌ Failed to generate synthetic data: {e}")
            import traceback
            traceback.print_exc()
            print("\nFalling back to real data (if available)...")
            
            if len(training_data) == 0:
                print("\n" + "=" * 60)
                print("❌ No data available for training!")
                print("=" * 60)
                print(f"Reason: No users found with at least {min_challenges} completed challenges")
                print("\nSuggestions:")
                print(f"  1. Lower min_user_challenges in config/ml_config.py (currently {min_challenges})")
                print("  2. Have users complete more challenges")
                print("  3. Fix synthetic data generation")
                print("=" * 60)
                return None
    
    # Save to CSV
    print("\n[4/4] Saving to CSV...")
    df = pd.DataFrame(training_data)
    
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    output_file = EXPORT_CONFIG['output_file']
    df.to_csv(output_file, index=False)
    
    print(f"✓ Saved to {output_file}")
    
    # Print statistics
    print("\n" + "=" * 60)
    print("Export Statistics")
    print("=" * 60)
    print(f"Total samples: {len(df)}")
    print(f"\nDifficulty distribution:")
    print(df['difficulty_label'].value_counts())
    print(f"\nFeature summary:")
    print(df[FEATURE_NAMES].describe())
    print("=" * 60)
    
    return output_file


if __name__ == "__main__":
    try:
        result = export_training_data()
        if result:
            print("\n✅ Data export completed successfully!")
        else:
            print("\n⚠️  Data export completed with warnings - no data exported")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error during export: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
