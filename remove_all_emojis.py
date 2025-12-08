import re

file_path = r"c:\Users\Azeem's ASUS\Desktop\Antigravity Test 2\Google Antigravity Test\Google Antigravity Test\Secure trainer backup after mid evaluation\qoder Secure Trainer FYP\Secure Trainer FYP\securetrainer\securetrainer.py"

# Read with utf-8
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the rocket emoji
content = content.replace('🚀', '')

# Also replace any other potential emojis I missed
# This regex matches any character outside the basic multilingual plane (emojis are usually here)
# and other non-ascii symbols
content = re.sub(r'[^\x00-\x7F]+', '', content)

# Write back with utf-8
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Removed all remaining non-ascii characters from securetrainer.py")
