"""
Simple test to count challenges in each category.
"""
import sys
from app import create_app
from app.models.challenge_model import (
    load_sql_challenges,
    get_xss_challenges,
    get_command_injection_challenges,
    get_authentication_challenges,
    get_csrf_challenges
)

app = create_app()

with app.app_context():
    print("\n" + "=" * 70)
    print("Challenge Count Verification")
    print("=" * 70 + "\n")
    
    sql_challenges = load_sql_challenges()
    print(f"\u2705 SQL Injection: {len(sql_challenges)} challenges")
    
    xss_challenges = get_xss_challenges()
    print(f"\u2705 XSS: {len(xss_challenges)} challenges")
    
    cmd_challenges = get_command_injection_challenges()
    print(f"\u2705 Command Injection: {len(cmd_challenges)} challenges")
    
    auth_challenges = get_authentication_challenges()
    print(f"\u2705 Authentication: {len(auth_challenges)} challenges")
    
    csrf_challenges = get_csrf_challenges()
    print(f"\u2705 CSRF: {len(csrf_challenges)} challenges")
    
    total = len(sql_challenges) + len(xss_challenges) + len(cmd_challenges) + len(auth_challenges) + len(csrf_challenges)
    
    print(f"\n{'=' * 70}")
    print(f"Total Challenges: {total}/50")
    print("=" * 70 + "\n")
    
    if total == 50:
        print("\u2705\u2705\u2705 SUCCESS! All 50 challenges are ready! \u2705\u2705\u2705\n")
    else:
        print(f"\u274c Expected 50 challenges, got {total}\n")
