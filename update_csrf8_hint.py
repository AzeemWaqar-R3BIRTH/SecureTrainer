#!/usr/bin/env python3
"""
Update the hint for csrf_8 challenge in MongoDB
"""

from pymongo import MongoClient

def update_csrf8_hint():
    """Update the hint for csrf_8 challenge."""
    print("🔧 Updating csrf_8 hint in MongoDB...")
    
    try:
        # Connect to MongoDB
        client = MongoClient("mongodb://localhost:27017/")
        db = client.securetrainer
        
        # New hint with actionable guidance
        new_hint = 'Create an auto-submitting HTML form with enctype="multipart/form-data" and a file input that submits to the upload endpoint. Host it on your site to exploit authenticated users.'
        
        # Update the challenge
        result = db.challenges.update_one(
            {'id': 'csrf_8'},
            {'$set': {'hint': new_hint}}
        )
        
        if result.modified_count > 0:
            print("✅ Successfully updated csrf_8 hint!")
            
            # Verify the update
            challenge = db.challenges.find_one({'id': 'csrf_8'})
            if challenge:
                print(f"\n📝 New hint: {challenge['hint']}")
        else:
            print("⚠️  No changes made (hint may already be updated or challenge not found)")
            
            # Check if challenge exists
            challenge = db.challenges.find_one({'id': 'csrf_8'})
            if challenge:
                print(f"\n📝 Current hint: {challenge.get('hint', 'NO HINT FOUND')}")
            else:
                print("❌ Challenge csrf_8 not found in database!")
        
        client.close()
        print("\n✅ Update complete!")
        return True
        
    except Exception as e:
        print(f"❌ Update failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    update_csrf8_hint()
