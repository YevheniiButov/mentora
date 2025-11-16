# routes/dutch_routes.py
# Dutch Reading (API) Routes

from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from extensions import db, csrf
from models import DutchPassage, DutchQuestion, UserDutchProgress
from datetime import datetime, timezone
import json
import os
import re
from utils.mastery_helpers import update_item_mastery

dutch_bp = Blueprint('dutch', __name__, url_prefix='/api/dutch')

# Mapping passage IDs to lesson numbers (for JS file-based lessons)
# For now, if we use DB, this is not needed
# But keep structure for future expansion
PASSAGE_ID_TO_LESSON_MAP = {}

def parse_lesson_js(js_content):
    """Parse JavaScript lesson object to Python dict - uses Node.js if available"""
    import subprocess
    import tempfile
    
    # First, try using Node.js to parse (most reliable)
    try:
        # Extract the variable name from export statement
        export_match = re.search(r'export\s+const\s+(\w+)\s*=', js_content)
        var_name = export_match.group(1) if export_match else 'lesson'
        
        # Create a temporary JS file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False, encoding='utf-8') as f:
            f.write(js_content)
            temp_file = f.name
        
        try:
            # Use node to evaluate and convert to JSON
            wrapper_script = f'''
const fs = require('fs');
const content = fs.readFileSync('{temp_file}', 'utf8');
const modifiedContent = content.replace(/export\\s+const\\s+(\\w+)\\s*=\\s*/, 'const $1 = ');
const finalContent = modifiedContent + '\\nmodule.exports = {var_name};';
const tempModule = require('path').join(require('path').dirname('{temp_file}'), 'temp_module.js');
fs.writeFileSync(tempModule, finalContent);
const data = require(tempModule);
fs.unlinkSync(tempModule);
console.log(JSON.stringify(data, null, 2));
'''
            result = subprocess.run(
                ['node', '-e', wrapper_script],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and result.stdout.strip():
                lesson_data = json.loads(result.stdout)
                os.unlink(temp_file)
                current_app.logger.info("Successfully parsed Dutch lesson using Node.js")
                return lesson_data
            else:
                current_app.logger.warning(f"Node.js parsing failed: {result.stderr}")
        except Exception as e:
            current_app.logger.warning(f"Node.js parsing error: {str(e)}")
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    except Exception as e:
        current_app.logger.warning(f"Node.js not available or failed: {str(e)}")
    
    # Fallback: try improved regex parser
    try:
        original_content = js_content
        js_content = re.sub(r'export\s+const\s+\w+\s*=\s*', '', js_content)
        js_content = re.sub(r'//.*?$', '', js_content, flags=re.MULTILINE)
        js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)
        
        def replace_backticks(match):
            content = match.group(1)
            content = json.dumps(content)[1:-1]
            return f'"{content}"'
        
        js_content = re.sub(r'`([^`]*)`', replace_backticks, js_content)
        
        def replace_single_quotes(match):
            content = match.group(1)
            return json.dumps(content)
        
        js_content = re.sub(r"'([^']*)'", replace_single_quotes, js_content)
        js_content = js_content.rstrip().rstrip(';').strip()
        
        lesson_data = json.loads(js_content)
        current_app.logger.info("Successfully parsed Dutch lesson using regex parser")
        return lesson_data
        
    except json.JSONDecodeError as e:
        current_app.logger.error(f"JSON decode error: {str(e)}")
        return None
    except Exception as e:
        current_app.logger.error(f"Error parsing Dutch lesson JS: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return None

def get_lesson_from_file(lesson_num):
    """Load Dutch lesson from JS file"""
    try:
        lessons_dir = None
        lesson_file = None
        
        # Strategy 1: Use static_folder if available
        if hasattr(current_app, 'static_folder') and current_app.static_folder:
            lessons_dir = os.path.join(current_app.static_folder, 'js', 'lessons_dutch')
            lesson_file = os.path.join(lessons_dir, f'lesson_{lesson_num:03d}.js')
            if os.path.exists(lesson_file):
                current_app.logger.info(f"Found Dutch lesson file via static_folder: {lesson_file}")
            else:
                lesson_file = None
        
        # Strategy 2: Use root_path with relative path
        if not lesson_file or not os.path.exists(lesson_file):
            lessons_dir = os.path.join(current_app.root_path, '..', 'static', 'js', 'lessons_dutch')
            lessons_dir = os.path.abspath(lessons_dir)
            lesson_file = os.path.join(lessons_dir, f'lesson_{lesson_num:03d}.js')
            if os.path.exists(lesson_file):
                current_app.logger.info(f"Found Dutch lesson file via root_path: {lesson_file}")
            else:
                lesson_file = None
        
        # Strategy 3: Use absolute path from project root
        if not lesson_file or not os.path.exists(lesson_file):
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            lessons_dir = os.path.join(project_root, 'static', 'js', 'lessons_dutch')
            lesson_file = os.path.join(lessons_dir, f'lesson_{lesson_num:03d}.js')
            if os.path.exists(lesson_file):
                current_app.logger.info(f"Found Dutch lesson file via project root: {lesson_file}")
            else:
                current_app.logger.error(f"Dutch lesson file not found: lesson_{lesson_num:03d}.js")
                return None
        
        # Read and parse file
        with open(lesson_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        current_app.logger.info(f"Successfully loaded Dutch lesson {lesson_num}, content length: {len(content)}")
        
        parsed_data = parse_lesson_js(content)
        if not parsed_data:
            current_app.logger.error(f"Failed to parse Dutch lesson {lesson_num}")
            return None
        
        current_app.logger.info(f"Successfully parsed Dutch lesson {lesson_num}")
        return parsed_data
        
    except Exception as e:
        current_app.logger.error(f"Error loading Dutch lesson {lesson_num}: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return None

def convert_lesson_to_passage_format(lesson_data, passage_id):
    """Convert lesson format to passage format for compatibility"""
    if not lesson_data:
        return None, []
    
    # Convert passage info
    passage_info = {
        'id': passage_id,
        'title': lesson_data.get('title', ''),
        'text': lesson_data.get('text', ''),
        'category': lesson_data.get('category', 'algemeen'),
        'difficulty': lesson_data.get('difficulty', 3),
        'word_count': len(lesson_data.get('text', '').split()),
        'image_url': lesson_data.get('imageUrl', '')
    }
    
    # Convert questions
    questions_data = []
    for idx, q in enumerate(lesson_data.get('questions', []), 1):
        correct_answer = None
        options_dict = {}
        
        for opt in q.get('options', []):
            opt_id = opt.get('id', '')
            opt_text = opt.get('text', '')
            options_dict[opt_id] = opt_text
            if opt.get('correct'):
                correct_answer = opt_id
        
        question_data = {
            'id': idx,
            'question_number': idx,
            'question_type': q.get('type', 'multiple_choice'),
            'question_text': q.get('question', ''),
            'correct_answer': correct_answer or '',
            'explanation': next((opt.get('explanation', '') for opt in q.get('options', []) if opt.get('correct')), ''),
            'options': options_dict
        }
        questions_data.append(question_data)
    
    return passage_info, questions_data


@dutch_bp.route('/passage/<int:passage_id>', methods=['GET'])
@login_required
def get_passage(passage_id):
    """Get Dutch passage with questions"""
    try:
        current_app.logger.info(f"Getting Dutch passage {passage_id}")
        
        # Try to load from JS file first
        lesson_num = PASSAGE_ID_TO_LESSON_MAP.get(passage_id, passage_id)
        lesson_data = get_lesson_from_file(lesson_num)
        
        if lesson_data:
            # Return full lesson data
            use_full_format = request.args.get('format') == 'full' or request.headers.get('X-Use-Full-Format') == 'true'
            
            if use_full_format:
                return jsonify({
                    'success': True,
                    'lesson': {
                        'id': lesson_data.get('id', f'lesson_{lesson_num:03d}'),
                        'title': lesson_data.get('title', ''),
                        'text': lesson_data.get('text', ''),
                        'paragraphs': lesson_data.get('paragraphs', []),
                        'vocabulary': lesson_data.get('vocabulary', []),
                        'questions': lesson_data.get('questions', []),
                        'imageUrl': lesson_data.get('imageUrl', ''),
                        'category': lesson_data.get('category', 'algemeen'),
                        'difficulty': lesson_data.get('difficulty', 3)
                    },
                    'passage_id': passage_id
                })
            else:
                passage_info, questions_data = convert_lesson_to_passage_format(lesson_data, passage_id)
                if not passage_info:
                    return jsonify({'error': 'Failed to convert lesson'}), 500
                
                return jsonify({
                    'passage': passage_info,
                    'questions': questions_data
                })
        
        # Fallback to database
        passage = DutchPassage.query.get_or_404(passage_id)
        questions = DutchQuestion.query.filter_by(
            passage_id=passage_id
        ).order_by(DutchQuestion.question_number).all()
        
        questions_data = []
        for q in questions:
            question_data = {
                'id': q.id,
                'question_number': q.question_number,
                'question_type': q.question_type,
                'question_text': q.question_text,
                'correct_answer': q.correct_answer,
                'explanation': q.explanation
            }
            if q.options:
                try:
                    options = json.loads(q.options) if isinstance(q.options, str) else q.options
                    question_data['options'] = options
                except:
                    question_data['options'] = {}
            questions_data.append(question_data)
        
        return jsonify({
            'passage': {
                'id': passage.id,
                'title': passage.title,
                'text': passage.text,
                'category': passage.category,
                'difficulty': passage.difficulty,
                'word_count': passage.word_count,
                'image_url': passage.image_url
            },
            'questions': questions_data
        })
    except Exception as e:
        current_app.logger.error(f"Error getting Dutch passage: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@dutch_bp.route('/submit', methods=['POST'])
@login_required
@csrf.exempt
def submit_answers():
    """Submit answers and calculate score"""
    try:
        current_app.logger.info(f"Dutch submit request - Content-Type: {request.content_type}")
        
        data = None
        if request.is_json:
            data = request.get_json()
        else:
            try:
                if request.data:
                    data = json.loads(request.data.decode('utf-8'))
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                current_app.logger.error(f"Dutch submit: Failed to parse JSON: {str(e)}")
                return jsonify({'error': 'Invalid JSON format'}), 400
        
        if not data:
            current_app.logger.error("Dutch submit: No data received")
            return jsonify({'error': 'No data received'}), 400
        
        current_app.logger.info(f"Dutch submit data: {data}")
        
        passage_id = data.get('passage_id')
        answers = data.get('answers', {})
        time_spent = data.get('time_spent', 0)
        
        if passage_id is None:
            return jsonify({'error': 'Passage ID required'}), 400
        
        try:
            passage_id = int(passage_id)
        except (ValueError, TypeError):
            return jsonify({'error': f'Invalid passage ID format: {passage_id}'}), 400
        
        if answers is None:
            answers = {}
        
        if not isinstance(answers, dict):
            if isinstance(answers, list):
                answers = {str(i+1): str(ans) for i, ans in enumerate(answers)}
            else:
                return jsonify({'error': f'Answers must be an object'}), 400
        
        # Try to load from JS file
        lesson_num = PASSAGE_ID_TO_LESSON_MAP.get(passage_id, passage_id)
        lesson_data = get_lesson_from_file(lesson_num)
        
        if lesson_data:
            # Check answers against lesson
            correct_count = 0
            questions_list = lesson_data.get('questions', [])
            total_questions = len(questions_list)
            results = []
            
            for idx, q in enumerate(questions_list, 1):
                question_id = q.get('id', str(idx))
                user_answer = answers.get(str(idx), '') or answers.get(str(question_id), '') or answers.get(question_id, '')
                
                if user_answer:
                    user_answer = str(user_answer).strip()
                else:
                    user_answer = ''
                
                correct_answer = None
                for opt in q.get('options', []):
                    if opt.get('correct'):
                        correct_answer = str(opt.get('id', ''))
                        break
                
                is_correct = user_answer == correct_answer
                
                if is_correct:
                    correct_count += 1
                
                explanation = None
                if not is_correct:
                    for opt in q.get('options', []):
                        if opt.get('id') == user_answer:
                            explanation = opt.get('explanation', '')
                            break
                
                results.append({
                    'question_id': idx,
                    'question_number': idx,
                    'correct': is_correct,
                    'user_answer': user_answer,
                    'correct_answer': correct_answer or '',
                    'explanation': explanation
                })
        else:
            # Fallback to database
            passage = DutchPassage.query.get_or_404(passage_id)
            questions = DutchQuestion.query.filter_by(passage_id=passage_id).all()
            
            correct_count = 0
            total_questions = len(questions)
            results = []
            
            for q in questions:
                user_answer = answers.get(str(q.id), '').strip()
                correct_answer = q.correct_answer.strip() if q.correct_answer else ''
                is_correct = user_answer.lower() == correct_answer.lower()
                
                if is_correct:
                    correct_count += 1
                
                results.append({
                    'question_id': q.id,
                    'question_number': q.question_number,
                    'correct': is_correct,
                    'user_answer': user_answer,
                    'correct_answer': correct_answer,
                    'explanation': q.explanation if not is_correct else None
                })
        
        # Calculate percentage
        percentage = int((correct_count / total_questions * 100)) if total_questions > 0 else 0
        
        # Calculate XP (10 XP per correct answer)
        xp_earned = correct_count * 10
        
        # Save progress
        completion_time = datetime.now(timezone.utc)
        progress = UserDutchProgress(
            user_id=current_user.id,
            passage_id=passage_id,
            completed_at=completion_time,
            score=correct_count,
            total_questions=total_questions,
            time_spent=time_spent
        )
        db.session.add(progress)

        is_session_mastered = total_questions > 0 and correct_count == total_questions
        session_date = completion_time.date()
        update_item_mastery(
            user_id=current_user.id,
            item_type='dutch',
            item_id=passage_id,
            is_correct=is_session_mastered,
            session_reference=f'dutch-{session_date.isoformat()}',
            session_date=session_date
        )
        
        # Update user XP
        current_user.xp = (current_user.xp or 0) + xp_earned
        db.session.commit()
        
        return jsonify({
            'success': True,
            'score': correct_count,
            'total': total_questions,
            'percentage': percentage,
            'xp_earned': xp_earned,
            'results': results
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error submitting Dutch answers: {str(e)}")
        return jsonify({'error': str(e)}), 500


# Admin routes for managing Dutch passages
@dutch_bp.route('/admin/passages', methods=['GET'])
@login_required
def list_passages():
    """List all Dutch passages (admin only)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        passages = DutchPassage.query.order_by(DutchPassage.created_at.desc()).all()
        
        return jsonify({
            'passages': [{
                'id': p.id,
                'title': p.title,
                'category': p.category,
                'difficulty': p.difficulty,
                'word_count': p.word_count,
                'question_count': p.questions.count(),
                'created_at': p.created_at.isoformat() if p.created_at else None
            } for p in passages]
        })
    except Exception as e:
        current_app.logger.error(f"Error listing Dutch passages: {str(e)}")
        return jsonify({'error': str(e)}), 500


@dutch_bp.route('/admin/passage', methods=['POST'])
@login_required
def create_passage():
    """Create new Dutch passage (admin only)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        
        passage = DutchPassage(
            title=data.get('title'),
            text=data.get('text'),
            category=data.get('category', 'algemeen'),
            difficulty=data.get('difficulty', 3),
            word_count=data.get('word_count'),
            image_url=data.get('image_url')
        )
        
        db.session.add(passage)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'passage': {
                'id': passage.id,
                'title': passage.title
            }
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating Dutch passage: {str(e)}")
        return jsonify({'error': str(e)}), 500

