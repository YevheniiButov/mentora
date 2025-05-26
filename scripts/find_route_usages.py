#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to find all occurrences of the missing route 'tests_bp.start_module_test' 
in HTML templates and other Python files.

Usage:
    $ python -m scripts.find_route_usages
"""

import os
import re
import sys

# Add the parent directory to the path so we can import the application
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

def search_files(directory, pattern, extensions=None):
    """
    Search for a pattern in all files in a directory with given extensions.
    
    Args:
        directory (str): Directory to search in
        pattern (str): Regular expression pattern to search for
        extensions (list): List of file extensions to search in (e.g. ['.html', '.py'])
        
    Returns:
        dict: Dictionary with file paths as keys and lists of matching lines as values
    """
    results = {}
    
    for root, _, files in os.walk(directory):
        for file in files:
            if extensions and not any(file.endswith(ext) for ext in extensions):
                continue
                
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                matches = re.finditer(pattern, content)
                lines = []
                
                for match in matches:
                    # Get the line number of the match
                    line_num = content[:match.start()].count('\n') + 1
                    
                    # Get the entire line containing the match
                    line_start = content.rfind('\n', 0, match.start())
                    if line_start == -1:
                        line_start = 0
                    else:
                        line_start += 1
                    
                    line_end = content.find('\n', match.end())
                    if line_end == -1:
                        line_end = len(content)
                    
                    line = content[line_start:line_end].strip()
                    lines.append((line_num, line, match.group(0)))
                
                if lines:
                    results[file_path] = lines
            except (UnicodeDecodeError, IOError) as e:
                print(f"Error reading {file_path}: {e}")
    
    return results

def suggest_fix(match, available_routes):
    """
    Suggest a fix for the missing route.
    
    Args:
        match (str): The matching line with the missing route
        available_routes (list): List of available routes in the application
        
    Returns:
        str: Suggested fix
    """
    # Check if the match is a url_for call
    if "url_for" in match:
        # Extract arguments to url_for
        args_match = re.search(r'url_for\([^)]*\)', match)
        if args_match:
            args_str = args_match.group(0)
            
            # Check if this is a module test
            # Typical format: url_for('tests_bp.start_module_test', lang=lang, module_id=module.id)
            if 'module_id' in args_str:
                # Replace with the closest alternative (final test)
                replacement = args_str.replace('start_module_test', 'start_final_test')
                replacement = replacement.replace('module_id=', 'subject_id=')
                
                # Generate the suggested fix
                return match.replace(args_str, replacement)
    
    # Default case: no specific suggestion
    return f"No specific suggestion. Consider replacing with one of the available routes: {', '.join(available_routes)}"

def main():
    """Main function to find usages of the missing route."""
    # Pattern to search for the missing route
    pattern = r'tests_bp\.start_module_test'
    
    # File extensions to search in
    extensions = ['.html', '.py']
    
    # Available routes that could be used as alternatives
    available_routes = [
        'tests_bp.start_final_test',
        'tests_bp.test_result',
        'tests_bp.list_tests',
        # Add other available routes here
    ]
    
    print(f"Searching for usages of '{pattern}' in {', '.join(extensions)} files...")
    
    # Search for the pattern in the application directory
    results = search_files(parent_dir, pattern, extensions)
    
    if not results:
        print("No usages found.")
        return
    
    print(f"\nFound {sum(len(lines) for lines in results.values())} usages in {len(results)} files:")
    print("=" * 80)
    
    for file_path, lines in results.items():
        rel_path = os.path.relpath(file_path, parent_dir)
        print(f"\nFile: {rel_path}")
        print("-" * 80)
        
        for line_num, line, match in lines:
            print(f"Line {line_num}: {line}")
            print(f"Suggested fix: {suggest_fix(line, available_routes)}")
            print()
    
    print("=" * 80)
    print("\nTo fix the issue, you have two options:")
    print("1. Implement the missing route 'tests_bp.start_module_test' in your Flask application")
    print("2. Update your templates to use an existing route, such as 'tests_bp.start_final_test'")
    print("\nExample implementation of the missing route:")
    print("""
@tests_bp.route('/<lang>/module_test/<int:module_id>', methods=['GET', 'POST'])
def start_module_test(lang, module_id):
    # Get the module
    module = Module.query.get_or_404(module_id)
    
    # Fetch all module test questions
    lessons = Lesson.query.filter_by(
        module_id=module_id, 
        content_type='module_test_question'
    ).all()
    
    # ... rest of the implementation
    
    return render_template('test.html', module=module, questions=questions)
""")

if __name__ == "__main__":
    main()