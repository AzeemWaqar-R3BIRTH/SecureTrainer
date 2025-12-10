import re

with open('app/ai/comprehensive_validation_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

matches = set(re.findall(r"'(sql|xss|cmd|auth|csrf)_(\d+)':", content))

categories = {}
for cat, num in matches:
    if cat not in categories:
        categories[cat] = []
    categories[cat].append(int(num))

for cat in sorted(categories.keys()):
    nums = sorted(categories[cat])
    print(f"{cat.upper()}: {nums}")
    print(f"  Count: {len(nums)}, Range: {min(nums)}-{max(nums)}")

print(f"\nTOTAL CHALLENGES: {len(matches)}")
print(f"Expected: 50 (10 per category)")
print(f"Status: {'✓ COMPLETE' if len(matches) == 50 else '✗ INCOMPLETE'}")
