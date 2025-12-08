file_path = r"c:\Users\Azeem's ASUS\Desktop\Antigravity Test 2\Google Antigravity Test\Google Antigravity Test\Secure trainer backup after mid evaluation\qoder Secure Trainer FYP\Secure Trainer FYP\securetrainer\app\routes\learning.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove lines 977 to 1091 (1-based index)
# In 0-based index: 976 to 1091 (exclusive of 1091)
# Wait, python slice [start:end] excludes end.
# So if I want to remove 977 (index 976) to 1091 (index 1090),
# I should keep lines[:976] and lines[1091:]

start_index = 976
end_index = 1091

new_lines = lines[:start_index] + lines[end_index:]

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"Removed lines {start_index+1} to {end_index}")
