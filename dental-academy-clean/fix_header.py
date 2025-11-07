#!/usr/bin/env python3
"""
Quick script to fix all url_for in _header.html
"""

import re

# Read the file
with open('templates/includes/_header.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Define replacements
replacements = {
    r'{{ url_for\(\'main\.index\', lang=lang\) }}': '/{{ lang }}/',
    r'{{ url_for\(\'daily_learning\.learning_map\', lang=lang\|default\(\'en\'\)\) }}': '/{{ lang|default(\'en\') }}/learning-map',
    r'{{ url_for\(\'daily_learning\.knowledge_base\', lang=lang\|default\(\'en\'\)\) }}': '/{{ lang|default(\'en\') }}/knowledge-base',
    r'{{ url_for\(\'main\.big_info\', lang=lang\|default\(\'en\'\)\) }}': '/{{ lang|default(\'en\') }}/big-info',
    r'{{ url_for\(\'dashboard\.achievements\'\) }}': '/{{ lang }}/dashboard/achievements',
    r'{{ url_for\(\'dashboard\.activity\'\) }}': '/{{ lang }}/dashboard/activity',
    r'{{ url_for\(\'dashboard\.learning_planner_redirect\'\) }}': '/{{ lang }}/dashboard/learning-planner',
    r'{{ url_for\(\'profile\.profile\', lang=lang\) if lang != \'en\' else url_for\(\'profile\.profile\'\) }}': '/{{ lang }}/profile',
    r'{{ url_for\(\'digid\.logout\'\) }}': '/digid/logout',
    r'{{ url_for\(\'auth\.digid_logout\'\) }}': '/{{ lang }}/auth/logout',
    r'{{ url_for\(\'auth\.login\', lang=lang\) }}': '/{{ lang }}/auth/login',
    r'{{ url_for\(\'auth\.register\', lang=lang\) }}': '/{{ lang }}/auth/register',
}

# Apply replacements
for pattern, replacement in replacements.items():
    content = re.sub(pattern, replacement, content)

# Write back
with open('templates/includes/_header.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed all url_for in _header.html!")
print("🔄 Restart Flask and try again")
