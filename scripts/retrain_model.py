"""
Automated Model Retraining Script
Handles periodic retraining and model updates
"""

import os
import sys
from datetime import datetime, timedelta
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from export_training_data import export_training_data
from train_difficulty_model import train_difficulty_model
from config.ml_config import RETRAIN_CONFIG, MODEL_PATHS


def check_if_retraining_needed():
    """Check if model retraining is needed."""
    print("Checking if retraining is needed...")
    
    # Check if metrics file exists
    if not os.path.exists(MODEL_PATHS['metrics']):
        print("✓ No existing model found - retraining needed")
        return True
    
    # Load existing metrics
    with open(MODEL_PATHS['metrics'], 'r') as f:
        metrics = json.load(f)
    
    # Check last training date
    last_training = datetime.fromisoformat(metrics.get('training_date', '2000-01-01'))
    days_since_training = (datetime.now() - last_training).days
    
    schedule = RETRAIN_CONFIG['schedule']
    retrain_intervals = {
        'daily': 1,
        'weekly': 7,
        'monthly': 30
    }
    
    interval = retrain_intervals.get(schedule, 7)
    
    if days_since_training >= interval:
        print(f"✓ Last training was {days_since_training} days ago - retraining needed")
        return True
    
    print(f"✗ Last training was {days_since_training} days ago - retraining not needed yet")
    return False


def retrain_model(force=False):
    """Execute model retraining pipeline."""
    print("=" * 60)
    print("SecureTrainer Automated Model Retraining")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Check if retraining is needed
    if not force and not check_if_retraining_needed():
        print("\n✓ Retraining not needed at this time")
        return False
    
    try:
        # Step 1: Export fresh data
        print("\n[Step 1/2] Exporting training data...")
        export_training_data()
        
        # Step 2: Train new model
        print("\n[Step 2/2] Training new model...")
        train_difficulty_model()
        
        print("\n" + "=" * 60)
        print("✅ Automated retraining completed successfully!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during retraining: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Retrain ML model')
    parser.add_argument('--force', action='store_true', help='Force retraining regardless of schedule')
    args = parser.parse_args()
    
    success = retrain_model(force=args.force)
    sys.exit(0 if success else 1)
