import re

file_path = r"c:\Users\Azeem's ASUS\Desktop\Antigravity Test 2\Google Antigravity Test\Google Antigravity Test\Secure trainer backup after mid evaluation\qoder Secure Trainer FYP\Secure Trainer FYP\securetrainer\app\utils\qr.py"

# Read with utf-8
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Function to remove non-ascii characters from a match
def remove_non_ascii(match):
    text = match.group(0)
    return re.sub(r'[^\x00-\x7F]+', '', text)

# Replace emojis
emojis = ['✅', '⚠️', '❌', '🔧', '🔐', '🔍', '📧', '📁', '📱']

for emoji in emojis:
    content = content.replace(emoji, '')

# Write back with utf-8
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Removed emojis from app/utils/qr.py")
