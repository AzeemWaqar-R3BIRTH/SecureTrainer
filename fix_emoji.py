import os

file_path = r"c:\Users\Azeem's ASUS\Desktop\Antigravity Test 2\Google Antigravity Test\Google Antigravity Test\Secure trainer backup after mid evaluation\qoder Secure Trainer FYP\Secure Trainer FYP\securetrainer\securetrainer.py"

# Read with utf-8
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the problematic line
# We match the line with the emoji
content = content.replace('print("🔧 Initializing SecureTrainer components...")', 'print("Initializing SecureTrainer components...")')

# Write back with utf-8
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed emoji in securetrainer.py")
