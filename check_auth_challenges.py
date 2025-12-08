#!/usr/bin/env python3
"""
Check what authentication challenges exist in the database
"""

from pymongo import MongoClient

def check_auth_challenges():
    """List all authentication challenges."""
    print("🔍 Checking authentication challenges in MongoDB...")
    
    try:
        client = MongoClient("mongodb://localhost:27017/")
        db = client.securetrainer
        
        # Find all authentication challenges
        auth_challenges = list(db.challenges.find({'type': 'authentication'}))
        
        print(f"\nFound {len(auth_challenges)} authentication challenges:")
        print("=" * 80)
        
        for challenge in auth_challenges:
            print(f"\nID: {challenge.get('id', 'NO ID')}")
            print(f"Difficulty: {challenge.get('difficulty', 'NO DIFFICULTY')}")
            print(f"Question: {challenge.get('question', 'NO QUESTION')[:60]}...")
            print(f"Hint: {challenge.get('hint', 'NO HINT')[:80]}...")
        
        print("\n" + "=" * 80)
        
        # Check specifically for auth_3
        auth_3 = db.challenges.find_one({'id': 'auth_3'})
        if auth_3:
            print("\n✅ auth_3 EXISTS:")
            print(f"   Question: {auth_3['question']}")
            print(f"   Current hint: {auth_3.get('hint', 'NO HINT')}")
        else:
            print("\n❌ auth_3 NOT FOUND in database!")
        
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_auth_challenges()
