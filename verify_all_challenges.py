"""
Verify that all challenge categories now have exactly 10 challenges each.
"""

from app.models.challenge_model import (
    load_sql_challenges,
    get_xss_challenges,
    get_command_injection_challenges,
    get_authentication_challenges,
    get_csrf_challenges,
    get_all_challenges
)

def verify_challenges():
    """Verify challenge counts."""
    print("=" * 70)
    print("SecureTrainer Challenge Verification")
    print("=" * 70)
    print()
    
    categories = {
        'SQL Injection': load_sql_challenges(),
        'Cross-Site Scripting (XSS)': get_xss_challenges(),
        'Command Injection': get_command_injection_challenges(),
        'Authentication Attacks': get_authentication_challenges(),
        'CSRF Vulnerabilities': get_csrf_challenges()
    }
    
    all_pass = True
    total_challenges = 0
    
    for category_name, challenges in categories.items():
        count = len(challenges)
        total_challenges += count
        status = "\u2705" if count == 10 else "\u274c"
        
        print(f"{status} {category_name}: {count} challenges")
        
        if count != 10:
            all_pass = False
            print(f"   \u26a0\ufe0f Expected 10, got {count}")
        else:
            # Show difficulty distribution
            difficulties = {}
            for challenge in challenges:
                diff = challenge.get('difficulty', 'Unknown')
                difficulties[diff] = difficulties.get(diff, 0) + 1
            
            print(f"   Difficulty distribution: {difficulties}")
    
    print()
    print("=" * 70)
    print(f"Total Challenges: {total_challenges}")
    print(f"Expected Total: 50")
    print(f"Status: {'\u2705 PASS' if all_pass and total_challenges == 50 else '\u274c FAIL'}")
    print("=" * 70)
    print()
    
    # Test get_all_challenges()
    all_challenges = get_all_challenges()
    print(f"\u2139\ufe0f get_all_challenges() returns: {len(all_challenges)} challenges")
    
    # Show unique challenge IDs
    unique_ids = set()
    duplicates = []
    
    for challenge in all_challenges:
        challenge_id = challenge.get('id')
        if challenge_id in unique_ids:
            duplicates.append(challenge_id)
        unique_ids.add(challenge_id)
    
    if duplicates:
        print(f"\u26a0\ufe0f Duplicate challenge IDs found: {duplicates}")
    else:
        print(f"\u2705 All challenge IDs are unique")
    
    print()
    return all_pass and total_challenges == 50

if __name__ == "__main__":
    try:
        success = verify_challenges()
        
        if success:
            print("\n\u2705 All verification checks passed!")
            print("\ud83c\udf89 You now have 50 challenges (10 per category)")
            print("\n\ud83d\ude80 Next Steps:")
            print("   1. Start your Flask application: python start.py")
            print("   2. Visit http://localhost:5000")
            print("   3. Check the Challenges page to see all 50 challenges")
            print("   4. Test challenge submission and validation")
        else:
            print("\n\u274c Verification failed. Please check the errors above.")
            
    except Exception as e:
        print(f"\n\u274c Error during verification: {e}")
        import traceback
        traceback.print_exc()
