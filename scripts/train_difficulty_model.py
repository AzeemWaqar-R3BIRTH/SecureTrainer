"""Model Training Script for SecureTrainer
Trains RandomForest classifier for difficulty prediction
"""

import os
import sys
import json
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import joblib

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

from config.ml_config import (
    MODEL_CONFIG, FEATURE_NAMES, DIFFICULTY_LABELS,
    TRAINING_CONFIG, MODEL_PATHS
)


def load_training_data(data_file='data/training_data.csv'):
    """Load training data from CSV."""
    print(f"Loading data from {data_file}...")
    df = pd.DataFrame(pd.read_csv(data_file))
    print(f"✓ Loaded {len(df)} samples")
    return df


def preprocess_data(df):
    """Preprocess and split data."""
    print("\nPreprocessing data...")
    
    # Separate features and labels
    X = df[FEATURE_NAMES].values
    y = df['difficulty_label'].values
    
    # Check class distribution
    unique, counts = np.unique(y, return_counts=True)
    print(f"\nClass distribution:")
    for label, count in zip(unique, counts):
        print(f"  {label}: {count}")
    
    # Check minimum samples per class
    min_samples = TRAINING_CONFIG['min_samples_per_class']
    if any(counts < min_samples):
        print(f"\n⚠️  Warning: Some classes have fewer than {min_samples} samples")
        print("  This is okay for development - proceeding with available data")
    
    # Encode labels
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # Split data - adjust for small datasets
    test_size = min(TRAINING_CONFIG['test_size'], 0.1) if len(X) < 10 else TRAINING_CONFIG['test_size']
    random_state = TRAINING_CONFIG['random_state']
    
    # For very small datasets, don't stratify
    if len(X) < 10 or any(counts < 2):
        print("\n⚠️  Small dataset detected - using simple train/test split without stratification")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=test_size, random_state=random_state
        )
    else:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_encoded, test_size=test_size, random_state=random_state, stratify=y_encoded
        )
    
    print(f"\n✓ Train set: {len(X_train)} samples")
    print(f"✓ Test set: {len(X_test)} samples")
    
    # Feature scaling
    scaler = None
    if TRAINING_CONFIG['feature_scaling']:
        print("\nApplying feature scaling...")
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)
        print("✓ Features scaled")
    
    return X_train, X_test, y_train, y_test, label_encoder, scaler


def train_model(X_train, y_train):
    """Train RandomForest model."""
    print("\nTraining RandomForest model...")
    print(f"Hyperparameters: {MODEL_CONFIG}")
    
    model = RandomForestClassifier(**MODEL_CONFIG)
    model.fit(X_train, y_train)
    
    print("✓ Model trained successfully")
    return model


def evaluate_model(model, X_test, y_test, label_encoder):
    """Evaluate model performance."""
    print("\nEvaluating model...")
    
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n{'='*60}")
    print("Model Performance")
    print(f"{'='*60}")
    print(f"Accuracy: {accuracy:.4f}")
    
    # Get unique labels in test set
    unique_test_labels = np.unique(np.concatenate([y_test, y_pred]))
    test_label_names = label_encoder.inverse_transform(unique_test_labels)
    
    print(f"\nClassification Report:")
    try:
        print(classification_report(
            y_test, y_pred,
            labels=unique_test_labels,
            target_names=test_label_names,
            zero_division=0
        ))
    except Exception as e:
        print(f"Unable to generate full classification report: {e}")
        print(f"Test accuracy: {accuracy:.4f}")
    
    print(f"\nConfusion Matrix:")
    cm = confusion_matrix(y_test, y_pred, labels=unique_test_labels)
    print(cm)
    
    # Feature importance
    print(f"\nTop 10 Feature Importances:")
    feature_importance = sorted(
        zip(FEATURE_NAMES, model.feature_importances_),
        key=lambda x: x[1],
        reverse=True
    )
    for i, (feature, importance) in enumerate(feature_importance[:10], 1):
        print(f"  {i}. {feature}: {importance:.4f}")
    
    print(f"{'='*60}")
    
    # Return metrics
    metrics = {
        'accuracy': float(accuracy),
        'training_date': datetime.now().isoformat(),
        'model_config': MODEL_CONFIG,
        'training_samples': len(X_test) + len(y_test),
        'classes': label_encoder.classes_.tolist()
    }
    
    # Try to add classification report if possible
    try:
        metrics['classification_report'] = classification_report(
            y_test, y_pred,
            labels=unique_test_labels,
            target_names=test_label_names,
            output_dict=True,
            zero_division=0
        )
        metrics['confusion_matrix'] = cm.tolist()
        metrics['feature_importance'] = {
            name: float(imp) for name, imp in feature_importance
        }
    except Exception as e:
        print(f"Note: Some metrics could not be saved: {e}")
    
    return metrics


def save_model(model, label_encoder, scaler, metrics):
    """Save trained model and artifacts."""
    print("\nSaving model...")
    
    # Create model directory
    os.makedirs('model', exist_ok=True)
    os.makedirs(MODEL_PATHS['backup_dir'], exist_ok=True)
    
    # Backup existing model if it exists
    if MODEL_PATHS.get('backup_old_model', True):
        if os.path.exists(MODEL_PATHS['model']):
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(
                MODEL_PATHS['backup_dir'],
                f'model_backup_{timestamp}.pkl'
            )
            os.rename(MODEL_PATHS['model'], backup_path)
            print(f"  Backed up old model to {backup_path}")
    
    # Save new model
    joblib.dump(model, MODEL_PATHS['model'])
    print(f"✓ Model saved to {MODEL_PATHS['model']}")
    
    # Save label encoder
    joblib.dump(label_encoder, MODEL_PATHS['encoder'])
    print(f"✓ Label encoder saved to {MODEL_PATHS['encoder']}")
    
    # Save scaler if used
    if scaler is not None:
        joblib.dump(scaler, MODEL_PATHS['scaler'])
        print(f"✓ Scaler saved to {MODEL_PATHS['scaler']}")
    
    # Save metrics
    with open(MODEL_PATHS['metrics'], 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"✓ Metrics saved to {MODEL_PATHS['metrics']}")


def train_difficulty_model():
    """Main training pipeline."""
    print("=" * 60)
    print("SecureTrainer ML Model Training")
    print("=" * 60)
    
    # Load data
    df = load_training_data()
    
    # Preprocess
    X_train, X_test, y_train, y_test, label_encoder, scaler = preprocess_data(df)
    
    # Train
    model = train_model(X_train, y_train)
    
    # Evaluate
    metrics = evaluate_model(model, X_test, y_test, label_encoder)
    
    # Save
    save_model(model, label_encoder, scaler, metrics)
    
    print("\n" + "=" * 60)
    print("✅ Training completed successfully!")
    print("=" * 60)
    print(f"\nModel accuracy: {metrics['accuracy']:.2%}")
    print(f"Model saved to: {MODEL_PATHS['model']}")
    print("\nYou can now use this model in your application.")
    print("=" * 60)


if __name__ == "__main__":
    try:
        train_difficulty_model()
    except Exception as e:
        print(f"\n❌ Error during training: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
