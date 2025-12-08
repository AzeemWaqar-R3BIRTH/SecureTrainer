import re

file_path = r"c:\Users\Azeem's ASUS\Desktop\Antigravity Test 2\Google Antigravity Test\Google Antigravity Test\Secure trainer backup after mid evaluation\qoder Secure Trainer FYP\Secure Trainer FYP\securetrainer\securetrainer.py"

# Read with utf-8
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Function to remove non-ascii characters from a match
def remove_non_ascii(match):
    text = match.group(0)
    # Keep only ascii characters
    return re.sub(r'[^\x00-\x7F]+', '', text)

# Replace print statements containing non-ascii characters
# This regex matches print("...") or print(f"...") where the string contains non-ascii
# It's a bit complex to match perfectly, so let's just replace specific known emojis for now
# to avoid breaking code
emojis = ['✅', '⚠️', '❌', '🔧', '🔐', '🔍', '📧', '📁', '📱']

for emoji in emojis:
    content = content.replace(emoji, '')

# Write back with utf-8
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Removed emojis from securetrainer.py")
