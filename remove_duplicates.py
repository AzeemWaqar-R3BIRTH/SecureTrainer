file_path = r"c:\Users\Azeem's ASUS\Desktop\Antigravity Test 2\Google Antigravity Test\Google Antigravity Test\Secure trainer backup after mid evaluation\qoder Secure Trainer FYP\Secure Trainer FYP\securetrainer\app\routes\learning.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Remove lines 977 to 1089 (0-indexed: 976 to 1089)
# The lines to remove are the duplicate definitions of track_module_progress and get_module_progress
# We should verify the content first, but based on view_file, these are the lines.

# Let's find the second occurrence of "@learning_bp.route('/progress/<module_id>', methods=['POST'])"
start_line = -1
occurrence = 0

for i, line in enumerate(lines):
    if "@learning_bp.route('/progress/<module_id>', methods=['POST'])" in line:
        occurrence += 1
        if occurrence == 2:
            start_line = i
            break

if start_line != -1:
    # Find the end of the block. The block ends before the next route definition
    # which is @learning_bp.route('/module/<module_id>/complete', methods=['POST'])
    end_line = -1
    for i in range(start_line + 1, len(lines)):
        if "@learning_bp.route('/module/<module_id>/complete', methods=['POST'])" in line:
            end_line = i
            break
    
    if end_line != -1:
        # Keep lines before start_line and lines from end_line onwards
        new_lines = lines[:start_line] + lines[end_line:]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"Removed duplicate routes from line {start_line+1} to {end_line}")
    else:
        print("Could not find end of duplicate block")
else:
    print("Could not find second occurrence of route")
