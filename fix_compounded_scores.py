"""
Database Migration Script: Fix Compounded Scores

This script recalculates user scores based on their challenge attempt history.
It fixes the issue where scores were being added 3x for each challenge completion.

Usage:
    python fix_compounded_scores.py [--dry-run]

Options:
    --dry-run: Show what would be changed without actually updating the database
"""

from pymongo import MongoClient
import os
import sys
from datetime import datetime

# Database connection
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/securetrainer')
client = MongoClient(MONGO_URI)
db = client.securetrainer


def calculate_user_level(score):
    """Calculate user level based on score with exponential progression."""
    import math
    if score < 100:
        return 1
    
    # Exponential level calculation for more balanced progression
    level = int(math.log(score / 100) / math.log(1.5)) + 2
    return min(level, 50)  # Cap at level 50


def get_role_for_level(level):
    """Get role based on user level with enhanced progression."""
    role_thresholds = [
        (1, "Trainee"),
        (5, "Junior Analyst"),
        (10, "Analyst"),
        (15, "Senior Analyst"),
        (20, "Specialist"),
        (25, "Expert"),
        (30, "Lead Analyst"),
        (35, "Team Lead"),
        (40, "Department Head"),
        (45, "Security Architect"),
        (50, "Chief Security Officer")
    ]
    
    for threshold, role in reversed(role_thresholds):
        if level >= threshold:
            return role
    
    return "Trainee"


def recalculate_user_scores(dry_run=False):
    """Recalculate all user scores based on challenge attempt history."""
    
    print("=" * 80)
    print("SCORE RECALCULATION SCRIPT")
    print("=" * 80)
    
    if dry_run:
        print("\n[DRY RUN] MODE - No changes will be made to the database\n")
    else:
        print("\n[LIVE] MODE - Database will be updated!\n")
        response = input("Are you sure you want to proceed? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            return
    
    print("\nFetching all users...")
    users = list(db.users.find({}))
    print(f"Found {len(users)} users\n")
    
    updates_made = 0
    total_score_difference = 0
    
    for user in users:
        user_id = str(user['_id'])
        current_score = user.get('score', 0)
        
        # Get all successful challenge attempts for this user
        attempts = list(db.challenge_attempts.find({
            'user_id': user_id,
            'is_correct': True
        }))
        
        # Get unique challenges completed
        completed_challenges = user.get('challenges_completed', [])
        
        # Calculate correct score by summing scores from unique challenges
        correct_score = 0
        challenge_scores = {}
        
        for attempt in attempts:
            challenge_id = attempt.get('challenge_id')
            score_earned = attempt.get('score_earned', 0)
            
            # Only count each challenge once (take the first successful attempt)
            if challenge_id not in challenge_scores:
                challenge_scores[challenge_id] = score_earned
                correct_score += score_earned
        
        # Calculate new level and role
        new_level = calculate_user_level(correct_score)
        new_role = get_role_for_level(new_level)
        
        # Check if update is needed
        score_difference = current_score - correct_score
        
        if score_difference != 0 or user.get('level') != new_level:
            updates_made += 1
            total_score_difference += score_difference
            
            print(f"User: {user.get('first_name', '')} {user.get('last_name', '')} ({user_id})")
            print(f"  Current Score: {current_score:,}")
            print(f"  Correct Score: {correct_score:,}")
            print(f"  Difference: {score_difference:,} ({(score_difference/current_score*100) if current_score > 0 else 0:.1f}%)")
            print(f"  Challenges Completed: {len(completed_challenges)}")
            print(f"  Level: {user.get('level', 1)} -> {new_level}")
            print(f"  Role: {user.get('role', 'Trainee')} -> {new_role}")
            
            if not dry_run:
                # Update the database
                db.users.update_one(
                    {'_id': user['_id']},
                    {
                        '$set': {
                            'score': correct_score,
                            'level': new_level,
                            'role': new_role,
                            'score_fixed_at': datetime.now()
                        }
                    }
                )
                print("  [OK] Updated")
            else:
                print("  [CHECK] Would update (dry run)")
            
            print()
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total users processed: {len(users)}")
    print(f"Users needing updates: {updates_made}")
    print(f"Total score difference: {total_score_difference:,}")
    
    if dry_run:
        print("\n[INFO] This was a dry run. No changes were made.")
        print("Run without --dry-run to apply changes.")
    else:
        print("\n[SUCCESS] Database updated successfully!")
    
    print()


def backup_database():
    """Create a backup of user scores before migration."""
    print("Creating backup of user scores...")
    
    users = list(db.users.find({}, {'_id': 1, 'score': 1, 'level': 1, 'role': 1}))
    
    backup_data = {
        'timestamp': datetime.now(),
        'users': users
    }
    
    db.score_backups.insert_one(backup_data)
    print(f"[OK] Backup created with {len(users)} user records\n")


if __name__ == '__main__':
    dry_run = '--dry-run' in sys.argv
    
    if not dry_run:
        # Create backup before making changes
        backup_database()
    
    recalculate_user_scores(dry_run=dry_run)
    
    client.close()
