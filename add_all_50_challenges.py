"""
Add all 50 challenges to database (10 per category).
"""

from pymongo import MongoClient
from datetime import datetime

# Connect to database
client = MongoClient("mongodb://localhost:27017/")
db = client.securetrainer

# Delete all existing challenges first
print(f"Deleting existing challenges...")
result = db.challenges.delete_many({})
print(f"Deleted {result.deleted_count} challenges")

# Import the challenge functions
import sys
sys.path.append('.')
from expand_challenges_to_10 import (
    get_new_sql_challenges,
    get_new_xss_challenges,
    get_new_command_injection_challenges,
    get_new_authentication_challenges,
    get_new_csrf_challenges
)

# Also need to add challenges 1-5 for each category
from app.models.challenge_model import (
    get_fallback_sql_challenges,
    get_xss_challenges as get_xss_1_6,
    get_command_injection_challenges as get_cmd_1_5,
    get_authentication_challenges as get_auth_1_6,
    get_csrf_challenges as get_csrf_1_3
)

print("\nGathering all challenges...")

# Get challenges 6-10 from expand script
sql_6_10 = get_new_sql_challenges()
xss_7_10 = get_new_xss_challenges()
cmd_6_10 = get_new_command_injection_challenges()
auth_7_10 = get_new_authentication_challenges()
csrf_4_10 = get_new_csrf_challenges()

# Get challenges 1-5 from hardcoded functions
sql_1_5 = get_fallback_sql_challenges()
xss_1_6 = get_xss_1_6()
cmd_1_5 = get_cmd_1_5()
auth_1_6 = get_auth_1_6()
csrf_1_3 = get_csrf_1_3()

# Combine all challenges
all_challenges = (
    sql_1_5 + sql_6_10 +
    xss_1_6 + xss_7_10 +
    cmd_1_5 + cmd_6_10 +
    auth_1_6 + auth_7_10 +
    csrf_1_3 + csrf_4_10
)

# Add metadata
for challenge in all_challenges:
    challenge['created_at'] = datetime.now()
    challenge['active'] = True
    challenge['_id'] = challenge.get('id', challenge.get('_id'))
    if 'expected_solutions' not in challenge:
        challenge['expected_solutions'] = []

print(f"Adding {len(all_challenges)} challenges to database...")

# Insert all challenges
try:
    result = db.challenges.insert_many(all_challenges, ordered=False)
    print(f"✅ Successfully added {len(result.inserted_ids)} challenges!")
except Exception as e:
    print(f"Error: {e}")

# Verify count by category
print("\n" + "=" * 60)
print("Challenge Count by Category:")
print("=" * 60)

categories = {
    'SQL Injection': 10,
    'Cross-Site Scripting (XSS)': 10,
    'Command Injection': 10,
    'Authentication Attacks': 10,
    'CSRF Vulnerabilities': 10
}

for category, expected in categories.items():
    count = db.challenges.count_documents({'category': category, 'active': True})
    status = "✅" if count == expected else f"⚠️"
    print(f"{status} {category}: {count}/{expected} challenges")

total = db.challenges.count_documents({'active': True})
print(f"\n📊 Total Active Challenges: {total}/50")
print("=" * 60)

if total == 50:
    print("\n🎉 SUCCESS! All 50 challenges added!")
else:
    print(f"\n⚠️ WARNING: Expected 50 challenges but got {total}")
