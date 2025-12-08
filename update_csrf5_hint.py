#!/usr/bin/env python3
"""
Update the hint for csrf_5 challenge in MongoDB
"""

from pymongo import MongoClient

def update_csrf5_hint():
    """Update the hint for csrf_5 challenge."""
    print("🔧 Updating csrf_5 hint in MongoDB...")
    
    try:
        # Connect to MongoDB
        client = MongoClient("mongodb://localhost:27017/")
        db = client.securetrainer
        
        # New hint with actionable guidance
        new_hint = 'Send a form with Content-Type: application/x-www-form-urlencoded, but structure the data like JSON. Many frameworks (Express.js, Flask) will parse both formats, letting you bypass the Content-Type check while still submitting valid JSON data.'
        
        # Update the challenge
        result = db.challenges.update_one(
            {'id': 'csrf_5'},
            {'$set': {'hint': new_hint}}
        )
        
        if result.modified_count > 0:
            print("✅ Successfully updated csrf_5 hint!")
            
            # Verify the update
            challenge = db.challenges.find_one({'id': 'csrf_5'})
            if challenge:
                print(f"\n📝 New hint: {challenge['hint']}")
        else:
            print("⚠️  No changes made (hint may already be updated or challenge not found)")
            
            # Check if challenge exists
            challenge = db.challenges.find_one({'id': 'csrf_5'})
            if challenge:
                print(f"\n📝 Current hint: {challenge.get('hint', 'NO HINT FOUND')}")
            else:
                print("❌ Challenge csrf_5 not found in database!")
        
        client.close()
        print("\n✅ Update complete!")
        return True
        
    except Exception as e:
        print(f"❌ Update failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    update_csrf5_hint()
