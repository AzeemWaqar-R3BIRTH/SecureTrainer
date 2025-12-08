"""
Generate synthetic training data for AI model demonstration
This creates realistic user performance data for model training
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_synthetic_users(num_users=50):
    """Generate synthetic user training data."""
    
    training_data = []
    
    # Define realistic ranges for each difficulty level
    difficulty_profiles = {
        'beginner': {
            'level': (1, 3),
            'score': (0, 500),
            'hint_count': (5, 15),
            'challenges_completed': (0, 10),
            'success_rate': (0.3, 0.6),
            'avg_completion_time': (180, 420),
            'consecutive_successes': (0, 2),
            'consecutive_failures': (0, 3)
        },
        'intermediate': {
            'level': (4, 6),
            'score': (500, 2000),
            'hint_count': (2, 8),
            'challenges_completed': (10, 30),
            'success_rate': (0.6, 0.8),
            'avg_completion_time': (120, 240),
            'consecutive_successes': (2, 5),
            'consecutive_failures': (0, 2)
        },
        'advanced': {
            'level': (7, 9),
            'score': (2000, 4500),
            'hint_count': (0, 4),
            'challenges_completed': (30, 60),
            'success_rate': (0.75, 0.9),
            'avg_completion_time': (60, 150),
            'consecutive_successes': (3, 8),
            'consecutive_failures': (0, 1)
        },
        'expert': {
            'level': (10, 15),
            'score': (4500, 10000),
            'hint_count': (0, 2),
            'challenges_completed': (60, 150),
            'success_rate': (0.85, 0.98),
            'avg_completion_time': (30, 90),
            'consecutive_successes': (5, 15),
            'consecutive_failures': (0, 1)
        }
    }
    
    # Generate balanced dataset
    users_per_difficulty = num_users // 4
    
    for difficulty, profile in difficulty_profiles.items():
        for i in range(users_per_difficulty):
            user_data = {
                'user_id': f'synthetic_user_{difficulty}_{i}',
                'level': np.random.randint(profile['level'][0], profile['level'][1] + 1),
                'score': np.random.randint(profile['score'][0], profile['score'][1]),
                'hint_count': np.random.randint(profile['hint_count'][0], profile['hint_count'][1]),
                'challenges_completed': np.random.randint(profile['challenges_completed'][0], profile['challenges_completed'][1] + 1),
                'success_rate': np.random.uniform(profile['success_rate'][0], profile['success_rate'][1]),
                'avg_completion_time': np.random.uniform(profile['avg_completion_time'][0], profile['avg_completion_time'][1]),
                'consecutive_successes': np.random.randint(profile['consecutive_successes'][0], profile['consecutive_successes'][1] + 1),
                'consecutive_failures': np.random.randint(profile['consecutive_failures'][0], profile['consecutive_failures'][1] + 1),
                'days_since_registration': np.random.randint(1, 180),
                
                # Category-specific scores (proportional to overall score)
                'sql_injection_score': int(np.random.uniform(0.2, 0.35) * user_data['score'] if 'score' in locals() else 0),
                'xss_score': int(np.random.uniform(0.15, 0.3) * user_data['score'] if 'score' in locals() else 0),
                'command_injection_score': int(np.random.uniform(0.15, 0.25) * user_data['score'] if 'score' in locals() else 0),
                'authentication_score': int(np.random.uniform(0.15, 0.25) * user_data['score'] if 'score' in locals() else 0),
                'csrf_score': int(np.random.uniform(0.1, 0.2) * user_data['score'] if 'score' in locals() else 0),
                
                'difficulty_label': difficulty
            }
            
            # Adjust category scores based on overall score
            base_score = user_data['score']
            user_data['sql_injection_score'] = int(np.random.uniform(0.2, 0.35) * base_score)
            user_data['xss_score'] = int(np.random.uniform(0.15, 0.3) * base_score)
            user_data['command_injection_score'] = int(np.random.uniform(0.15, 0.25) * base_score)
            user_data['authentication_score'] = int(np.random.uniform(0.15, 0.25) * base_score)
            user_data['csrf_score'] = int(np.random.uniform(0.1, 0.2) * base_score)
            
            training_data.append(user_data)
    
    # Add some noise/variance to make data more realistic
    for user in training_data:
        # Add 10% random noise to numeric features
        for key in ['success_rate', 'avg_completion_time']:
            if key in user:
                noise = np.random.normal(0, 0.1)
                user[key] = max(0, user[key] + (user[key] * noise))
        
        # Clamp success_rate between 0 and 1
        if 'success_rate' in user:
            user['success_rate'] = max(0.0, min(1.0, user['success_rate']))
    
    return pd.DataFrame(training_data)


if __name__ == "__main__":
    print("=" * 60)
    print("Generating Synthetic Training Data for Demo")
    print("=" * 60)
    
    # Generate 60 synthetic users (15 per difficulty level)
    print("\nGenerating 60 synthetic users...")
    df = generate_synthetic_users(60)
    
    # Save to CSV
    output_file = 'data/training_data.csv'
    df.to_csv(output_file, index=False)
    
    print(f"✓ Generated {len(df)} synthetic users")
    print(f"✓ Saved to {output_file}")
    
    # Print statistics
    print("\n" + "=" * 60)
    print("Dataset Statistics")
    print("=" * 60)
    print(f"Total samples: {len(df)}")
    print(f"\nDifficulty distribution:")
    print(df['difficulty_label'].value_counts())
    
    print(f"\nFeature summary:")
    feature_cols = ['level', 'score', 'hint_count', 'challenges_completed', 
                   'success_rate', 'avg_completion_time']
    print(df[feature_cols].describe())
    
    print("\n" + "=" * 60)
    print("✅ Synthetic training data generated successfully!")
    print("Next step: Run 'python scripts\\train_difficulty_model.py'")
    print("=" * 60)
