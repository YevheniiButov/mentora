#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to add the missing 'start_module_test' route to your Flask application.
This will create or update the routes/tests_routes.py file with the missing endpoint.

Usage:
    $ python -m scripts.add_module_test_route_fixed
"""

import os
import re
import sys
import shutil

# Add the parent directory to the path so we can import the application
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
sys.path.insert(0, parent_dir)

# Path to the tests routes file (assuming common Flask project structure)
TESTS_ROUTES_FILE = os.path.join(parent_dir, 'routes', 'tests_routes.py')

# The code for the new route to be added
NEW_ROUTE_CODE = '''
@tests_bp.route('/<lang>/module_test/<int:module_id>', methods=['GET', 'POST'])
def start_module_test(lang, module_id):
    """Route to handle module-level tests.
    
    Args:
        lang (str): Language code
        module_id (int): ID of the module to test
        
    Returns:
        Rendered template or redirect
    """
    # Check if user is logged in
    if not current_user.is_authenticated:
        return redirect(url_for('auth_bp.login', lang=lang))
    
    # Get the module
    module = Module.query.get_or_404(module_id)
    
    # Check if module is premium and user has subscription
    if module.is_premium and not current_user.has_subscription:
        flash(_('This module requires a subscription'), 'warning')
        return redirect(url_for('learning_bp.learning_map', lang=lang))
    
    # Get all module test questions
    lessons = Lesson.query.filter_by(
        module_id=module_id, 
        content_type='module_test_question'
    ).order_by(Lesson.order).all()
    
    # Extract question IDs from lesson content
    question_ids = []
    for lesson in lessons:
        try:
            content_data = json.loads(lesson.content)
            if 'question_id' in content_data:
                question_ids.append(content_data['question_id'])
        except (json.JSONDecodeError, TypeError):
            continue
    
    # Get the actual questions
    questions = Question.query.filter(Question.id.in_(question_ids)).all() if question_ids else []
    
    # If we don't have questions, redirect to module view
    if not questions:
        flash(_('No test questions available for this module'), 'info')
        return redirect(url_for('learning_bp.module_view', lang=lang, module_id=module_id))
    
    # Handle form submission
    if request.method == 'POST':
        # Process test submission
        score = 0
        total = len(questions)
        
        for question in questions:
            answer = request.form.get(f'question_{question.id}')
            if answer and question.check_answer(answer):
                score += 1
            
            # Record the attempt
            attempt = TestAttempt(
                user_id=current_user.id,
                test_id=0,  # 0 for module tests
                question_id=question.id,
                selected_option=answer,
                is_correct=question.check_answer(answer) if answer else False
            )
            db.session.add(attempt)
        
        try:
            db.session.commit()
            flash(_('Test completed! Your score: %(score)s/%(total)s', score=score, total=total), 'success')
            return redirect(url_for('learning_bp.module_view', lang=lang, module_id=module_id))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f'Error saving test attempts: {e}')
            flash(_('Error saving your results'), 'danger')
    
    # Render the test template
    return render_template(
        'test.html',
        module=module,
        questions=questions,
        lang=lang,
        title=_('Module Test: %(title)s', title=module.title)
    )
'''

def check_imports(content):
    """
    Check if all necessary imports are present in the file.
    
    Args:
        content (str): The file content
        
    Returns:
        str: Updated content with any missing imports added
    """
    required_imports = [
        'from flask import Blueprint, render_template, request, redirect, url_for, flash',
        'from flask_login import current_user, login_required',
        'from flask_babel import _',
        'import json',
        'from app import app, db',
        'from models import Module, Lesson, Question, TestAttempt'
    ]
    
    # Remove comments and empty lines for better import checking
    cleaned_content = re.sub(r'#.*$', '', content, flags=re.MULTILINE)
    cleaned_content = re.sub(r'\n\s*\n', '\n', cleaned_content)
    
    # Check if each required import is present
    for imp in required_imports:
        # Create a pattern that matches the import regardless of exact syntax
        # For example, 'from flask import X' should match even if the file has 'from flask import X, Y, Z'
        if imp.startswith('from '):
            module, imports = imp.split(' import ')
            pattern = re.escape(module) + r'\s+import\s+' + '.*' + re.escape(imports)
            if not re.search(pattern, cleaned_content):
                # Add the import to the top of the file
                content = imp + '\n' + content
        elif imp.startswith('import '):
            pattern = r'import\s+' + re.escape(imp.split(' ')[1])
            if not re.search(pattern, cleaned_content):
                # Add the import to the top of the file
                content = imp + '\n' + content
    
    return content

def format_new_route(content):
    """Format the new route code to match the indentation style of the file."""
    # Determine the indentation style (spaces or tabs)
    if '\t' in content:
        # File uses tabs
        indent = '\t'
    else:
        # File uses spaces, determine how many
        spaces_match = re.search(r'^( +)\S', content, re.MULTILINE)
        if spaces_match:
            indent = spaces_match.group(1)
        else:
            # Default to 4 spaces
            indent = '    '
    
    # Format the new route code with the proper indentation
    formatted_code = NEW_ROUTE_CODE
    # Adjust indentation level for multiline string
    formatted_code = formatted_code.replace('\n', '\n' + indent)
    return formatted_code

def add_route():
    """Add the missing route to the tests routes file."""
    if not os.path.exists(TESTS_ROUTES_FILE):
        print(f"Error: Tests routes file not found at {TESTS_ROUTES_FILE}")
        return False
    
    # Create a backup of the original file
    backup_file = TESTS_ROUTES_FILE + '.bak'
    shutil.copy2(TESTS_ROUTES_FILE, backup_file)
    print(f"Created backup at {backup_file}")
    
    # Read the current file content
    with open(TESTS_ROUTES_FILE, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if the route already exists
    if 'def start_module_test' in content:
        print("The 'start_module_test' route already exists. No changes made.")
        return False
    
    # Check for required imports and add any missing ones
    content = check_imports(content)
    
    # Format the new route code
    formatted_code = format_new_route(content)
    
    # Find a good place to insert the new route
    # Ideally after an existing route function
    match = re.search(r'def [^:]+:[^\n]*\n\s*$', content)
    if match:
        # Insert after the last route function
        insert_position = match.end()
        new_content = content[:insert_position] + formatted_code + content[insert_position:]
    else:
        # Add to the end of the file
        new_content = content + '\n' + formatted_code
    
    # Write the updated content back to the file
    with open(TESTS_ROUTES_FILE, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"Successfully added 'start_module_test' route to {TESTS_ROUTES_FILE}")
    return True

def main():
    """Main function to add the missing route."""
    print("Adding missing 'start_module_test' route to your Flask application...")
    
    if add_route():
        print("\nThe route has been added successfully!")
        print(f"Please check {TESTS_ROUTES_FILE} to verify the changes.")
        print("\nNext steps:")
        print("1. Review the added route to make sure it matches your application's logic")
        print("2. Adjust test template ('test.html') if needed")
        print("3. Restart your Flask application to apply the changes")
    else:
        print("\nNo changes were made. Please check the error message above.")

if __name__ == "__main__":
    main()