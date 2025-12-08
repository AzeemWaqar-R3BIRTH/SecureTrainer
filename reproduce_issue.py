
from app import create_app
from app.models.user_model import insert_user, get_user_by_id
from app.models.challenge_model import update_user_challenge_progress
from flask import session
import time

app = create_app()

def test_cmd_injection_progress():
    with app.app_context():
        # 1. Create a dummy user
        user_data = {
            "username": "progress_test_user",
            "email": "progress_test@example.com",
            "password": "hashed_password_placeholder",
            "role": "Trainee",
            "level": 1,
            "score": 0,
            "challenges_completed": []
        }
        
        # Clean up previous runs
        db = app.config['MONGO_CLIENT'].get_database()
        db.users.delete_many({"username": "progress_test_user"})
        
        user_id = insert_user(user_data)
        print(f"Created test user: {user_id}")
        
        # 2. Simulate Command Injection Submission via Route Handler logic
        # We can't easily import the route handler function and mock request/session without more work.
        # But we can emulate what the route DOES.
        # Actually, since I'm modifying the route code, I want to verify the ROUTE code.
        # So I should use the test client.
        
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user_id'] = user_id
                sess['challenge_cmd_1_start_time'] = time.time()
                
            # Payload for Generic Challenge Submission (as used by frontend)
            # The validator expects descriptive text, not code!
            payload = {
                "answer": "ping and list directory",
                "challenge_id": "cmd_1"
            }
            
            print("\n--- Attempt 1: Valid Submission ---")
            # Using the now-registered challenge_bp endpoint
            resp = client.post(f'/api/challenges/submit/{user_id}', json=payload)
            print(f"Response Status: {resp.status_code}")
            print(f"Response Data: {resp.json}")
            
            # Check DB state
            user = get_user_by_id(user_id)
            print(f"User Score: {user.get('score')}")
            print(f"Completed Challenges: {user.get('challenges_completed')}")
            
            if 'cmd_1' not in user.get('challenges_completed', []):
                print("FAILURE: 'cmd_1' not found in challenges_completed!")
                initial_success = False
            else:
                print("SUCCESS: 'cmd_1' recorded in challenges_completed.")
                initial_success = True
                
            initial_score = user.get('score', 0)
            
            # 3. Double Submission Test
            print("\n--- Attempt 2: Duplicate Submission ---")
            resp = client.post(f'/api/challenges/submit/{user_id}', json=payload)
            print(f"Response Status: {resp.status_code}")
            print(f"Response Data: {resp.json}")
            
            user = get_user_by_id(user_id)
            new_score = user.get('score', 0)
            print(f"User Score after 2nd attempt: {new_score}")
            
            if new_score > initial_score:
                print("FAILURE: Score increased on duplicate submission!")
            elif new_score == initial_score and initial_success: # Only count as pass if initial worked
                print("SUCCESS: Score did not increase on duplicate submission.")
            else:
                print("Double submission check inclusive due to initial failure.")

if __name__ == "__main__":
    test_cmd_injection_progress()
