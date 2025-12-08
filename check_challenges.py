
from app import create_app
from app.models.challenge_model import get_all_challenges, get_db
from app.models.user_model import get_user_by_id

app = create_app()

with app.app_context():
    db = get_db()
    
    # Get all defined challenges
    all_challenges = get_all_challenges()
    print(f"Total defined challenges: {len(all_challenges)}")
    
    challenges_by_id = {c['id']: c for c in all_challenges}
    
    # Get a user (I'll pick one, or list all)
    users = list(db.users.find())
    for user in users:
        print(f"\nUser: {user.get('username')} ({user.get('_id')})")
        completed = user.get('challenges_completed', [])
        print(f"Completed IDs: {completed}")
        
        for cid in completed:
            if cid not in challenges_by_id:
                print(f"  WARNING: Completed challenge {cid} NOT found in defined challenges!")
            else:
                c = challenges_by_id[cid]
                print(f"  - {cid}: {c['category']}")
