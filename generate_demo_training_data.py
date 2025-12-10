"""
Generate synthetic training data for AI model demonstration.
This creates realistic user performance data with outliers for robust model training.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Windows console encoding fix
import builtins
original_print = builtins.print

def safe_print(*args, **kwargs):
    """Print with fallback for Windows console encoding."""
    try:
        original_print(*args, **kwargs)
    except UnicodeEncodeError:
        message = ' '.join(str(arg) for arg in args)
        message = message.replace('\u2713', '[OK]').replace('\u2705', '[SUCCESS]')
        message = message.replace('\u26a0\ufe0f', '[WARNING]').replace('\u274c', '[ERROR]')
        message = message.replace('\u2717', '[X]')
        original_print(message, **kwargs)

builtins.print = safe_print

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)


def generate_normal_user(difficulty, profile, index):
    """Generate a normal user with realistic stats."""
    base_score = np.random.randint(profile['score'][0], profile['score'][1])
    
    user_data = {
        'user_id': f'synthetic_{difficulty}_{index}',
        'level': np.random.randint(profile['level'][0], profile['level'][1] + 1),
        'score': base_score,
        'hint_count': np.random.randint(profile['hint_count'][0], profile['hint_count'][1] + 1),
        'challenges_completed': np.random.randint(
            profile['challenges_completed'][0], 
            profile['challenges_completed'][1] + 1
        ),
        'success_rate': np.random.uniform(profile['success_rate'][0], profile['success_rate'][1]),
        'avg_completion_time': np.random.uniform(
            profile['avg_completion_time'][0], 
            profile['avg_completion_time'][1]
        ),
        'consecutive_successes': np.random.randint(
            profile['consecutive_successes'][0], 
            profile['consecutive_successes'][1] + 1
        ),
        'consecutive_failures': np.random.randint(
            profile['consecutive_failures'][0], 
            profile['consecutive_failures'][1] + 1
        ),
        'days_since_registration': np.random.randint(1, 365),
        'difficulty_label': difficulty
    }
    
    # Category-specific scores (proportional to overall score)
    user_data['sql_injection_score'] = int(np.random.uniform(0.2, 0.35) * base_score)
    user_data['xss_score'] = int(np.random.uniform(0.15, 0.3) * base_score)
    user_data['command_injection_score'] = int(np.random.uniform(0.15, 0.25) * base_score)
    user_data['authentication_score'] = int(np.random.uniform(0.15, 0.25) * base_score)
    user_data['csrf_score'] = int(np.random.uniform(0.1, 0.2) * base_score)
    
    return user_data


def generate_outlier_user(outlier_type, index):
    """Generate outlier users with extreme characteristics."""
    
    if outlier_type == 'prodigy':
        # Extremely high performance, low experience
        return {
            'user_id': f'outlier_prodigy_{index}',
            'level': np.random.randint(15, 25),
            'score': np.random.randint(10000, 20000),
            'hint_count': np.random.randint(0, 2),
            'challenges_completed': np.random.randint(100, 250),
            'success_rate': np.random.uniform(0.95, 0.99),
            'avg_completion_time': np.random.uniform(10, 40),
            'consecutive_successes': np.random.randint(15, 30),
            'consecutive_failures': 0,
            'days_since_registration': np.random.randint(30, 180),
            'sql_injection_score': np.random.randint(3000, 6000),
            'xss_score': np.random.randint(2000, 4000),
            'command_injection_score': np.random.randint(2000, 4000),
            'authentication_score': np.random.randint(2000, 4000),
            'csrf_score': np.random.randint(1000, 2000),
            'difficulty_label': 'expert'
        }
    
    elif outlier_type == 'struggling':
        # Very low performance despite high activity
        return {
            'user_id': f'outlier_struggling_{index}',
            'level': np.random.randint(1, 3),
            'score': np.random.randint(0, 100),
            'hint_count': np.random.randint(30, 50),
            'challenges_completed': np.random.randint(50, 100),
            'success_rate': np.random.uniform(0.05, 0.2),
            'avg_completion_time': np.random.uniform(400, 600),
            'consecutive_successes': 0,
            'consecutive_failures': np.random.randint(10, 20),
            'days_since_registration': np.random.randint(100, 365),
            'sql_injection_score': np.random.randint(0, 30),
            'xss_score': np.random.randint(0, 20),
            'command_injection_score': np.random.randint(0, 20),
            'authentication_score': np.random.randint(0, 20),
            'csrf_score': np.random.randint(0, 10),
            'difficulty_label': 'beginner'
        }
    
    elif outlier_type == 'inconsistent':
        # Wildly varying performance
        base_level = np.random.randint(4, 8)
        return {
            'user_id': f'outlier_inconsistent_{index}',
            'level': base_level,
            'score': np.random.randint(1000, 3000),
            'hint_count': np.random.randint(0, 25),
            'challenges_completed': np.random.randint(20, 60),
            'success_rate': np.random.uniform(0.3, 0.9),  # Highly variable
            'avg_completion_time': np.random.uniform(50, 400),  # Highly variable
            'consecutive_successes': np.random.randint(0, 10),
            'consecutive_failures': np.random.randint(0, 8),
            'days_since_registration': np.random.randint(30, 200),
            'sql_injection_score': np.random.randint(100, 1000),
            'xss_score': np.random.randint(50, 800),
            'command_injection_score': np.random.randint(50, 700),
            'authentication_score': np.random.randint(100, 600),
            'csrf_score': np.random.randint(50, 400),
            'difficulty_label': np.random.choice(['intermediate', 'advanced'])
        }
    
    elif outlier_type == 'speedster':
        # Extremely fast completion times
        return {
            'user_id': f'outlier_speedster_{index}',
            'level': np.random.randint(8, 14),
            'score': np.random.randint(3000, 7000),
            'hint_count': np.random.randint(0, 3),
            'challenges_completed': np.random.randint(40, 100),
            'success_rate': np.random.uniform(0.8, 0.95),
            'avg_completion_time': np.random.uniform(5, 25),  # Extremely fast
            'consecutive_successes': np.random.randint(5, 12),
            'consecutive_failures': np.random.randint(0, 2),
            'days_since_registration': np.random.randint(20, 150),
            'sql_injection_score': np.random.randint(800, 2000),
            'xss_score': np.random.randint(600, 1500),
            'command_injection_score': np.random.randint(500, 1500),
            'authentication_score': np.random.randint(600, 1500),
            'csrf_score': np.random.randint(400, 1000),
            'difficulty_label': 'advanced'
        }
    
    elif outlier_type == 'slow_learner':
        # Very slow but eventually successful
        return {
            'user_id': f'outlier_slow_{index}',
            'level': np.random.randint(5, 9),
            'score': np.random.randint(1500, 3500),
            'hint_count': np.random.randint(8, 20),
            'challenges_completed': np.random.randint(25, 50),
            'success_rate': np.random.uniform(0.7, 0.85),
            'avg_completion_time': np.random.uniform(300, 600),  # Very slow
            'consecutive_successes': np.random.randint(3, 7),
            'consecutive_failures': np.random.randint(1, 4),
            'days_since_registration': np.random.randint(150, 400),
            'sql_injection_score': np.random.randint(400, 1000),
            'xss_score': np.random.randint(300, 800),
            'command_injection_score': np.random.randint(300, 700),
            'authentication_score': np.random.randint(300, 700),
            'csrf_score': np.random.randint(200, 500),
            'difficulty_label': 'intermediate'
        }
    
    elif outlier_type == 'hint_dependent':
        # High hints but good success rate
        return {
            'user_id': f'outlier_hints_{index}',
            'level': np.random.randint(6, 10),
            'score': np.random.randint(2000, 4500),
            'hint_count': np.random.randint(20, 40),  # Very high
            'challenges_completed': np.random.randint(30, 70),
            'success_rate': np.random.uniform(0.75, 0.9),
            'avg_completion_time': np.random.uniform(150, 300),
            'consecutive_successes': np.random.randint(4, 9),
            'consecutive_failures': np.random.randint(0, 2),
            'days_since_registration': np.random.randint(60, 220),
            'sql_injection_score': np.random.randint(500, 1300),
            'xss_score': np.random.randint(400, 1000),
            'command_injection_score': np.random.randint(400, 1000),
            'authentication_score': np.random.randint(400, 1000),
            'csrf_score': np.random.randint(300, 700),
            'difficulty_label': 'advanced'
        }
    
    else:  # natural_talent
        # Low experience but high performance
        return {
            'user_id': f'outlier_talent_{index}',
            'level': np.random.randint(8, 15),
            'score': np.random.randint(4000, 9000),
            'hint_count': np.random.randint(0, 3),
            'challenges_completed': np.random.randint(15, 40),  # Low experience
            'success_rate': np.random.uniform(0.88, 0.97),
            'avg_completion_time': np.random.uniform(40, 100),
            'consecutive_successes': np.random.randint(8, 15),
            'consecutive_failures': 0,
            'days_since_registration': np.random.randint(7, 60),  # Short time
            'sql_injection_score': np.random.randint(1000, 2500),
            'xss_score': np.random.randint(800, 2000),
            'command_injection_score': np.random.randint(700, 1800),
            'authentication_score': np.random.randint(800, 1900),
            'csrf_score': np.random.randint(500, 1200),
            'difficulty_label': 'expert'
        }


def add_realistic_noise(user_data):
    """Add realistic noise/variance to user data."""
    # Add 5-15% noise to numeric features
    noise_features = ['success_rate', 'avg_completion_time', 'score']
    
    for key in noise_features:
        if key in user_data and user_data[key] > 0:
            noise_factor = np.random.uniform(0.05, 0.15)
            noise = np.random.normal(0, noise_factor)
            user_data[key] = max(0, user_data[key] + (user_data[key] * noise))
    
    # Clamp success_rate between 0 and 1
    if 'success_rate' in user_data:
        user_data['success_rate'] = max(0.0, min(1.0, user_data['success_rate']))
    
    # Ensure integer fields remain integers
    int_fields = ['level', 'score', 'hint_count', 'challenges_completed',
                  'consecutive_successes', 'consecutive_failures', 'days_since_registration',
                  'sql_injection_score', 'xss_score', 'command_injection_score',
                  'authentication_score', 'csrf_score']
    
    for field in int_fields:
        if field in user_data:
            user_data[field] = int(user_data[field])


def generate_synthetic_users(num_users=20000, outlier_percentage=0.15):
    """
    Generate synthetic user training data with realistic outliers.
    
    Args:
        num_users: Total number of synthetic users to generate
        outlier_percentage: Percentage of users to be outliers (default 15%)
    """
    
    training_data = []
    num_outliers = int(num_users * outlier_percentage)
    num_normal = num_users - num_outliers
    
    print(f"Generating {num_users:,} synthetic users:")
    print(f"  - Normal users: {num_normal:,}")
    print(f"  - Outlier users: {num_outliers:,}")
    
    # Define realistic ranges for each difficulty level
    difficulty_profiles = {
        'beginner': {
            'level': (1, 3),
            'score': (0, 500),
            'hint_count': (5, 20),
            'challenges_completed': (0, 10),
            'success_rate': (0.2, 0.6),
            'avg_completion_time': (180, 480),
            'consecutive_successes': (0, 2),
            'consecutive_failures': (0, 5)
        },
        'intermediate': {
            'level': (4, 6),
            'score': (500, 2000),
            'hint_count': (2, 10),
            'challenges_completed': (10, 35),
            'success_rate': (0.55, 0.8),
            'avg_completion_time': (90, 240),
            'consecutive_successes': (2, 6),
            'consecutive_failures': (0, 3)
        },
        'advanced': {
            'level': (7, 10),
            'score': (2000, 5000),
            'hint_count': (0, 5),
            'challenges_completed': (30, 70),
            'success_rate': (0.7, 0.92),
            'avg_completion_time': (45, 150),
            'consecutive_successes': (3, 10),
            'consecutive_failures': (0, 2)
        },
        'expert': {
            'level': (10, 20),
            'score': (4500, 12000),
            'hint_count': (0, 3),
            'challenges_completed': (60, 200),
            'success_rate': (0.85, 0.99),
            'avg_completion_time': (20, 90),
            'consecutive_successes': (5, 20),
            'consecutive_failures': (0, 1)
        }
    }
    
    # Generate balanced normal dataset
    users_per_difficulty = num_normal // 4
    
    print("\nGenerating normal users...")
    for difficulty, profile in difficulty_profiles.items():
        for i in range(users_per_difficulty):
            user_data = generate_normal_user(difficulty, profile, i)
            training_data.append(user_data)
        
        if (i + 1) % 1000 == 0:
            print(f"  Generated {len(training_data):,} users...")
    
    print(f"[OK] Generated {len(training_data):,} normal users")
    
    # Generate outliers
    print("\nGenerating outlier users...")
    outlier_types = [
        'prodigy',           # Extremely high performance
        'struggling',        # Very low performance despite high activity
        'inconsistent',      # Wildly varying performance
        'speedster',         # Extremely fast completion times
        'slow_learner',      # Very slow but eventually successful
        'hint_dependent',    # High hints but good success
        'natural_talent'     # Low experience but high performance
    ]
    
    outliers_per_type = num_outliers // len(outlier_types)
    
    for outlier_type in outlier_types:
        for i in range(outliers_per_type):
            user_data = generate_outlier_user(outlier_type, i)
            training_data.append(user_data)
    
    print(f"[OK] Generated {num_outliers:,} outlier users")
    
    # Add realistic noise to all users
    print("\nAdding realistic variance...")
    for i, user in enumerate(training_data):
        add_realistic_noise(user)
        if (i + 1) % 5000 == 0:
            print(f"  Processed {i + 1:,}/{len(training_data):,} users...")
    
    print("[OK] Added variance to data")
    
    # Shuffle the data
    random.shuffle(training_data)
    
    return pd.DataFrame(training_data)


if __name__ == "__main__":
    print("=" * 60)
    print("Generating Synthetic Training Data")
    print("=" * 60)
    
    # Generate 20,000 synthetic users with 15% outliers
    df = generate_synthetic_users(num_users=20000, outlier_percentage=0.15)
    
    # Save to CSV
    os.makedirs('data', exist_ok=True)
    output_file = 'data/training_data.csv'
    df.to_csv(output_file, index=False)
    
    print(f"\n[SUCCESS] Generated {len(df):,} synthetic users")
    print(f"[SUCCESS] Saved to {output_file}")
    
    # Print statistics
    print("\n" + "=" * 60)
    print("Dataset Statistics")
    print("=" * 60)
    print(f"Total samples: {len(df):,}")
    print(f"\nDifficulty distribution:")
    print(df['difficulty_label'].value_counts().sort_index())
    
    print(f"\nFeature summary:")
    feature_cols = ['level', 'score', 'hint_count', 'challenges_completed', 
                   'success_rate', 'avg_completion_time']
    print(df[feature_cols].describe())
    
    print("\n" + "=" * 60)
    print("[SUCCESS] Synthetic training data generated successfully!")
    print("Next step: Run 'python scripts\\train_difficulty_model.py'")
    print("=" * 60)
