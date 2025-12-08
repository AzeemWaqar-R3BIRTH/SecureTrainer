import re

# Read the file
file_path = r"c:\Users\Azeem's ASUS\Desktop\Antigravity Test 2\Google Antigravity Test\Google Antigravity Test\Secure trainer backup after mid evaluation\qoder Secure Trainer FYP\Secure Trainer FYP\securetrainer\app\templates\challenges.html"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Define the categories and their colors
categories = [
    ('sql_injection', 'red'),
    ('xss', 'yellow'),
    ('command_injection', 'purple'),
    ('authentication', 'blue'),
    ('csrf', 'green')
]

# For each category, update the progress bar section
for category, color in categories:
    # Pattern to match the old progress section
    old_pattern = rf'''(<div class="mb-4">
                    <div class="flex justify-between text-xs text-gray-600 mb-1">
                        <span>Progress</span>
                        <span(?:[^>]*)>)\{{\{{ category_stats\.{category}\.(?:total|percent) \}}\}}([^<]*)</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                        <div class="bg-{color}-600 h-2 rounded-full(?:[^"]*)"
                            style="width: \{{\{{ category_stats\.{category}\.percent \}}\}}%"></div>
                    </div>
                    <p class="text-xs text-gray-500 mt-1">\{{\{{ category_stats\.{category}\.completed \}}\}}/\{{\{{
                        category_stats\.{category}\.total \}}\}} completed</p>
                </div>)'''
    
    # New progress section with percentage and completion badge
    new_section = f'''<div class="mb-4">
                    <div class="flex justify-between text-xs text-gray-600 mb-1">
                        <span>Progress</span>
                        <span class="font-bold">{{{{ category_stats.{category}.percent }}}}%</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                        <div class="bg-{color}-600 h-2 rounded-full transition-all duration-500"
                            style="width: {{{{ category_stats.{category}.percent }}}}%"></div>
                    </div>
                    <div class="flex justify-between items-center mt-1">
                        <p class="text-xs text-gray-500">{{{{ category_stats.{category}.completed }}}}/{{{{ category_stats.{category}.total }}}} completed</p>
                        {{% if category_stats.{category}.percent == 100 %}}
                        <span class="bg-green-100 text-green-800 text-xs font-semibold px-2 py-0.5 rounded">✓ Completed</span>
                        {{% endif %}}
                    </div>
                </div>'''
    
    # Simple string replacement approach
    # Find and replace the specific pattern for each category
    if category == 'sql_injection':
        content = content.replace(
            '''                <div class="mb-4">
                    <div class="flex justify-between text-xs text-gray-600 mb-1">
                        <span>Progress</span>
                        <span class="font-bold">{{ category_stats.sql_injection.percent }}%</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                        <div class="bg-red-600 h-2 rounded-full transition-all duration-500"
                            style="width: {{ category_stats.sql_injection.percent }}%"></div>
                    </div>
                    <p class="text-xs text-gray-500 mt-1">{{ category_stats.sql_injection.completed }}/{{
                        category_stats.sql_injection.total }} completed</p>
                </div>''',
            new_section
        )
    elif category == 'xss':
        content = content.replace(
            '''                <div class="mb-4">
                    <div class="flex justify-between text-xs text-gray-600 mb-1">
                        <span>Progress</span>
                        <span>{{ category_stats.xss.total }} challenges</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                        <div class="bg-yellow-600 h-2 rounded-full" style="width: {{ category_stats.xss.percent }}%">
                        </div>
                    </div>
                    <p class="text-xs text-gray-500 mt-1">{{ category_stats.xss.completed }}/{{ category_stats.xss.total
                        }} completed</p>
                </div>''',
            new_section
        )
    elif category == 'command_injection':
        content = content.replace(
            '''                <div class="mb-4">
                    <div class="flex justify-between text-xs text-gray-600 mb-1">
                        <span>Progress</span>
                        <span>{{ category_stats.command_injection.total }} challenges</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                        <div class="bg-purple-600 h-2 rounded-full"
                            style="width: {{ category_stats.command_injection.percent }}%"></div>
                    </div>
                    <p class="text-xs text-gray-500 mt-1">{{ category_stats.command_injection.completed }}/{{
                        category_stats.command_injection.total }} completed</p>
                </div>''',
            new_section
        )
    elif category == 'authentication':
        content = content.replace(
            '''                <div class="mb-4">
                    <div class="flex justify-between text-xs text-gray-600 mb-1">
                        <span>Progress</span>
                        <span>{{ category_stats.authentication.total }} challenges</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                        <div class="bg-blue-600 h-2 rounded-full"
                            style="width: {{ category_stats.authentication.percent }}%"></div>
                    </div>
                    <p class="text-xs text-gray-500 mt-1">{{ category_stats.authentication.completed }}/{{
                        category_stats.authentication.total }} completed</p>
                </div>''',
            new_section
        )
    elif category == 'csrf':
        content = content.replace(
            '''                <div class="mb-4">
                    <div class="flex justify-between text-xs text-gray-600 mb-1">
                        <span>Progress</span>
                        <span>{{ category_stats.csrf.total }} challenges</span>
                    </div>
                    <div class="w-full bg-gray-200 rounded-full h-2">
                        <div class="bg-green-600 h-2 rounded-full" style="width: {{ category_stats.csrf.percent }}%">
                        </div>
                    </div>
                    <p class="text-xs text-gray-500 mt-1">{{ category_stats.csrf.completed }}/{{
                        category_stats.csrf.total }} completed</p>
                </div>''',
            new_section
        )

# Write the updated content
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Progress bars updated successfully!")
