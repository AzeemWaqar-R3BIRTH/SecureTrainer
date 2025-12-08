file_path = r"c:\Users\Azeem's ASUS\Desktop\Antigravity Test 2\Google Antigravity Test\Google Antigravity Test\Secure trainer backup after mid evaluation\qoder Secure Trainer FYP\Secure Trainer FYP\securetrainer\app\routes\learning.py"

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the second occurrence of the route decorator
start_line = -1
occurrence = 0
target_string = "@learning_bp.route('/progress/<module_id>', methods=['POST'])"

for i, line in enumerate(lines):
    if target_string in line:
        occurrence += 1
        if occurrence == 2:
            start_line = i
            break

if start_line != -1:
    # Find the start of the mark_module_complete function
    end_line = -1
    next_func_string = "@learning_bp.route('/module/<module_id>/complete', methods=['POST'])"
    
    for i in range(start_line + 1, len(lines)):
        if next_func_string in line:
            end_line = i
            break
    
    if end_line != -1:
        # Keep lines before start_line and lines from end_line onwards
        # We want to keep the blank lines before the next function if possible, but it's fine
        new_lines = lines[:start_line] + lines[end_line:]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"Removed duplicate routes from line {start_line+1} to {end_line}")
    else:
        print("Could not find start of mark_module_complete function")
else:
    print("Could not find second occurrence of route")
