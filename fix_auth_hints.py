#!/usr/bin/env python3
"""
Fix auth_3 and auth_7 hints to be more actionable
"""

from pymongo import MongoClient

def update_authentication_hints():
    """Update hints for auth_3 and auth_7 challenges."""
    print("🔧 Updating authentication challenge hints...")
    
    try:
        # Connect to MongoDB
        client = MongoClient("mongodb://localhost:27017/")
        db = client.securetrainer
        
        # Update auth_3 - Brute Force Attack hint
        new_hint_auth3 = "Without rate limiting, attackers can automate thousands of login attempts per minute using tools like Hydra or Burp Suite Intruder to guess passwords systematically."
        
        result3 = db.challenges.update_one(
            {'id': 'auth_3'},
            {'$set': {'hint': new_hint_auth3}}
        )
        
        if result3.modified_count > 0:
            print("✅ Successfully updated auth_3 hint!")
            challenge = db.challenges.find_one({'id': 'auth_3'})
            if challenge:
                print(f"   New hint: {challenge['hint'][:80]}...")
        else:
            print("⚠️  auth_3 not updated (may already be correct or not found)")
        
        # Update auth_7 - Security Questions Bypass hint
        new_hint_auth7 = "Search social media profiles, public records, or use OSINT tools to find answers to common security questions like 'mother's maiden name' or 'first pet'. Many answers are publicly available on Facebook, LinkedIn, or data breach databases."
        
        result7 = db.challenges.update_one(
            {'id': 'auth_7'},
            {'$set': {'hint': new_hint_auth7}}
        )
        
        if result7.modified_count > 0:
            print("✅ Successfully updated auth_7 hint!")
            challenge = db.challenges.find_one({'id': 'auth_7'})
            if challenge:
                print(f"   New hint: {challenge['hint'][:80]}...")
        else:
            print("⚠️  auth_7 not updated (may already be correct or not found)")
        
        client.close()
        print("\n✅ Hint updates complete!")
        print(f"\nTotal challenges updated: {result3.modified_count + result7.modified_count}")
        return True
        
    except Exception as e:
        print(f"❌ Update failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    update_authentication_hints()
