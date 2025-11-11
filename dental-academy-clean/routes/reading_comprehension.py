# routes/reading_comprehension.py
# Reading Comprehension Lessons Routes

from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from extensions import db
from models import User
from datetime import datetime, timezone
import json
import os
import re

reading_comprehension_bp = Blueprint('reading_comprehension', __name__, url_prefix='/api/reading-comprehension')


@reading_comprehension_bp.route('/lessons', methods=['GET'])
@login_required
def get_all_lessons():
    """Get list of all available lessons"""
    try:
        lessons_list = []
        
        # Read all lesson files from static/js/lessons/
        lessons_dir = os.path.join(current_app.root_path, '..', 'static', 'js', 'lessons')
        lessons_dir = os.path.abspath(lessons_dir)
        
        for i in range(1, 11):
            lesson_file = os.path.join(lessons_dir, f'lesson_{i:03d}.js')
            if os.path.exists(lesson_file):
                try:
                    # Read and parse lesson file
                    with open(lesson_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract basic info using regex (simple approach)
                    title_match = re.search(r"title:\s*['\"]([^'\"]+)['\"]", content)
                    id_match = re.search(r"id:\s*['\"]([^'\"]+)['\"]", content)
                    image_match = re.search(r"imageUrl:\s*['\"]([^'\"]+)['\"]", content)
                    
                    lesson_info = {
                        'id': id_match.group(1) if id_match else f'lesson_{i:03d}',
                        'title': title_match.group(1) if title_match else f'Lesson {i}',
                        'index': i,
                        'imageUrl': image_match.group(1) if image_match else None
                    }
                    lessons_list.append(lesson_info)
                except Exception as e:
                    current_app.logger.error(f"Error reading lesson {i}: {str(e)}")
                    continue
        
        return jsonify({
            'success': True,
            'lessons': lessons_list,
            'total': len(lessons_list)
        })
    except Exception as e:
        current_app.logger.error(f"Error getting lessons list: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@reading_comprehension_bp.route('/lesson/<lesson_id>', methods=['GET'])
@login_required
def get_lesson(lesson_id):
    """Get a specific lesson by ID"""
    try:
        # Extract lesson number from ID (e.g., 'lesson_001' -> 1)
        lesson_num_match = re.search(r'lesson_(\d+)', lesson_id)
        if not lesson_num_match:
            return jsonify({'error': 'Invalid lesson ID'}), 400
        
        lesson_num = int(lesson_num_match.group(1))
        if lesson_num < 1 or lesson_num > 10:
            return jsonify({'error': 'Lesson number out of range'}), 400
        
        # Read lesson file
        lessons_dir = os.path.join(current_app.root_path, '..', 'static', 'js', 'lessons')
        lessons_dir = os.path.abspath(lessons_dir)
        lesson_file = os.path.join(lessons_dir, f'lesson_{lesson_num:03d}.js')
        
        if not os.path.exists(lesson_file):
            return jsonify({'error': 'Lesson not found'}), 404
        
        # Read and parse lesson
        with open(lesson_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse JavaScript object to JSON (simplified approach)
        # For production, consider using a proper JS parser
        # This is a basic regex-based parser
        lesson_data = parse_lesson_js(content)
        
        if not lesson_data:
            return jsonify({'error': 'Failed to parse lesson'}), 500
        
        return jsonify({
            'success': True,
            'lesson': lesson_data
        })
    except Exception as e:
        current_app.logger.error(f"Error getting lesson {lesson_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def parse_lesson_js(js_content):
    """Parse JavaScript lesson object to Python dict"""
    try:
        # Remove export statement
        js_content = re.sub(r'export\s+const\s+\w+\s*=\s*', '', js_content)
        
        # Remove comments
        js_content = re.sub(r'//.*?$', '', js_content, flags=re.MULTILINE)
        js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)
        
        # Convert JavaScript object to JSON-like string
        # Replace single quotes with double quotes (simple approach)
        js_content = re.sub(r"'([^']*)'", r'"\1"', js_content)
        
        # Handle template literals in text fields
        # Replace backticks with double quotes
        js_content = re.sub(r'`([^`]*)`', r'"\1"', js_content)
        
        # Remove trailing semicolon
        js_content = js_content.rstrip().rstrip(';')
        
        # Try to parse as JSON
        lesson_data = json.loads(js_content)
        return lesson_data
    except Exception as e:
        current_app.logger.error(f"Error parsing lesson JS: {str(e)}")
        # Fallback: return basic structure
        return None


@reading_comprehension_bp.route('/lesson/<lesson_id>/progress', methods=['GET', 'POST'])
@login_required
def lesson_progress(lesson_id):
    """Get or update progress for a lesson"""
    try:
        if request.method == 'GET':
            # Get progress
            # TODO: Implement progress tracking in database
            # For now, return empty progress
            return jsonify({
                'success': True,
                'progress': {
                    'lessonId': lesson_id,
                    'vocabularyMastery': {},
                    'questionAttempts': {},
                    'comprehensionLevel': 'determining',
                    'timeSpent': 0,
                    'strengths': [],
                    'weaknesses': []
                }
            })
        else:
            # Update progress
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # TODO: Save progress to database
            # For now, just acknowledge
            return jsonify({
                'success': True,
                'message': 'Progress updated'
            })
    except Exception as e:
        current_app.logger.error(f"Error handling progress for {lesson_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@reading_comprehension_bp.route('/lesson/<lesson_id>/submit', methods=['POST'])
@login_required
def submit_lesson_answers(lesson_id):
    """Submit answers for a lesson and get results"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        answers = data.get('answers', {})  # {questionId: answerId}
        time_spent = data.get('timeSpent', 0)
        
        # Get lesson to check answers
        lesson_num_match = re.search(r'lesson_(\d+)', lesson_id)
        if not lesson_num_match:
            return jsonify({'error': 'Invalid lesson ID'}), 400
        
        lesson_num = int(lesson_num_match.group(1))
        lessons_dir = os.path.join(current_app.root_path, '..', 'static', 'js', 'lessons')
        lessons_dir = os.path.abspath(lessons_dir)
        lesson_file = os.path.join(lessons_dir, f'lesson_{lesson_num:03d}.js')
        
        if not os.path.exists(lesson_file):
            return jsonify({'error': 'Lesson not found'}), 404
        
        with open(lesson_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lesson_data = parse_lesson_js(content)
        if not lesson_data:
            return jsonify({'error': 'Failed to parse lesson'}), 500
        
        # Check answers
        results = []
        correct_count = 0
        total_questions = len(lesson_data.get('questions', []))
        
        for question in lesson_data.get('questions', []):
            question_id = question.get('id')
            user_answer = answers.get(question_id)
            
            # Find correct answer
            correct_answer = None
            for option in question.get('options', []):
                if option.get('correct'):
                    correct_answer = option.get('id')
                    break
            
            is_correct = user_answer == correct_answer
            if is_correct:
                correct_count += 1
            
            results.append({
                'questionId': question_id,
                'userAnswer': user_answer,
                'correctAnswer': correct_answer,
                'isCorrect': is_correct,
                'explanation': next(
                    (opt.get('explanation') for opt in question.get('options', []) 
                     if opt.get('id') == user_answer),
                    None
                )
            })
        
        score = (correct_count / total_questions * 100) if total_questions > 0 else 0
        
        # TODO: Save results to database
        
        return jsonify({
            'success': True,
            'results': results,
            'score': round(score, 1),
            'correctCount': correct_count,
            'totalQuestions': total_questions,
            'timeSpent': time_spent
        })
    except Exception as e:
        current_app.logger.error(f"Error submitting answers for {lesson_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

