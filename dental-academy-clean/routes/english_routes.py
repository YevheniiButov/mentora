# routes/english_routes.py
# English Reading (IELTS) Routes
# UPDATED: Now uses new reading comprehension lessons from JS files

from flask import Blueprint, jsonify, request, render_template, current_app
from flask_login import login_required, current_user
from extensions import db
from models import EnglishPassage, EnglishQuestion, UserEnglishProgress
from datetime import datetime, timezone
import json
import os
import re
from utils.ielts_generator import parse_generated_passage, generate_passage_title_from_topic
from utils.mastery_helpers import update_item_mastery

english_bp = Blueprint('english', __name__, url_prefix='/api/english')

# Mapping old passage IDs to new lesson numbers
# Old IDs from DB (5-14) -> New lesson numbers (1-10)
PASSAGE_ID_TO_LESSON_MAP = {
    5: 1,   # Artificial Intelligence in Healthcare
    6: 2,   # The Coffee Trade Through History
    7: 3,   # Urban Green Spaces and Mental Health
    8: 4,   # The Architecture of Ancient Rome
    9: 5,   # Climate Change and Ocean Currents
    10: 6,  # The Psychology of Color
    11: 7,  # The Evolution of Human Language
    12: 8,  # Renewable Energy Technologies
    13: 9,  # The Science of Sleep
    14: 10  # Space Exploration Milestones
}

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
            # Write the JS content
            f.write(js_content)
            temp_file = f.name
        
        try:
            # Use node to evaluate and convert to JSON
            # Create a wrapper script that properly handles ES6 export
            wrapper_script = f'''
const fs = require('fs');
const content = fs.readFileSync('{temp_file}', 'utf8');
// Replace export with module.exports
const modifiedContent = content.replace(/export\\s+const\\s+(\\w+)\\s*=\\s*/, 'const $1 = ');
// Add module.exports at the end
const finalContent = modifiedContent + '\\nmodule.exports = {var_name};';
// Write to a new temp file and require it
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
                current_app.logger.info("Successfully parsed lesson using Node.js")
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
        # Remove export statement
        original_content = js_content
        js_content = re.sub(r'export\s+const\s+\w+\s*=\s*', '', js_content)
        
        # Remove comments (simple approach)
        js_content = re.sub(r'//.*?$', '', js_content, flags=re.MULTILINE)
        js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)
        
        # Handle template literals (backticks) - convert to double quotes
        def replace_backticks(match):
            content = match.group(1)
            # Escape special characters for JSON
            content = json.dumps(content)[1:-1]  # Use json.dumps to properly escape
            return f'"{content}"'
        
        js_content = re.sub(r'`([^`]*)`', replace_backticks, js_content)
        
        # For single quotes, we need to be very careful
        # Only replace if it's clearly a string delimiter (not an apostrophe)
        # This is a simplified approach - may not work for all cases
        def replace_single_quotes(match):
            content = match.group(1)
            # Use json.dumps to properly escape
            return json.dumps(content)
        
        js_content = re.sub(r"'([^']*)'", replace_single_quotes, js_content)
        
        # Remove trailing semicolon
        js_content = js_content.rstrip().rstrip(';').strip()
        
        # Try to parse as JSON
        lesson_data = json.loads(js_content)
        current_app.logger.info("Successfully parsed lesson using regex parser")
        return lesson_data
        
    except json.JSONDecodeError as e:
        current_app.logger.error(f"JSON decode error: {str(e)}")
        # Last resort: try the reading_comprehension parser
        try:
            from routes.reading_comprehension import parse_lesson_js as parse_rc
            return parse_rc(original_content)
        except:
            pass
        
        current_app.logger.error(f"All parsing methods failed for lesson JS")
        return None
    except Exception as e:
        current_app.logger.error(f"Error parsing lesson JS: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return None

def get_lesson_from_file(lesson_num):
    """Load lesson from JS file"""
    try:
        # Try multiple path strategies
        lessons_dir = None
        lesson_file = None
        
        # Strategy 1: Use static_folder if available
        if hasattr(current_app, 'static_folder') and current_app.static_folder:
            lessons_dir = os.path.join(current_app.static_folder, 'js', 'lessons')
            lesson_file = os.path.join(lessons_dir, f'lesson_{lesson_num:03d}.js')
            if os.path.exists(lesson_file):
                current_app.logger.info(f"Found lesson file via static_folder: {lesson_file}")
            else:
                lesson_file = None
        
        # Strategy 2: Use root_path with relative path
        if not lesson_file or not os.path.exists(lesson_file):
            lessons_dir = os.path.join(current_app.root_path, '..', 'static', 'js', 'lessons')
            lessons_dir = os.path.abspath(lessons_dir)
            lesson_file = os.path.join(lessons_dir, f'lesson_{lesson_num:03d}.js')
            if os.path.exists(lesson_file):
                current_app.logger.info(f"Found lesson file via root_path: {lesson_file}")
            else:
                lesson_file = None
        
        # Strategy 3: Use absolute path from project root
        if not lesson_file or not os.path.exists(lesson_file):
            # Get project root (parent of routes directory)
            project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            lessons_dir = os.path.join(project_root, 'static', 'js', 'lessons')
            lesson_file = os.path.join(lessons_dir, f'lesson_{lesson_num:03d}.js')
            if os.path.exists(lesson_file):
                current_app.logger.info(f"Found lesson file via project root: {lesson_file}")
            else:
                current_app.logger.error(f"Lesson file not found: lesson_{lesson_num:03d}.js")
                current_app.logger.error(f"Tried paths: static_folder={getattr(current_app, 'static_folder', None)}, root_path={current_app.root_path}")
                return None
        
        # Read and parse file
        with open(lesson_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        current_app.logger.info(f"Successfully loaded lesson {lesson_num}, content length: {len(content)}")
        
        parsed_data = parse_lesson_js(content)
        if not parsed_data:
            current_app.logger.error(f"Failed to parse lesson {lesson_num}")
            return None
        
        current_app.logger.info(f"Successfully parsed lesson {lesson_num}")
        return parsed_data
        
    except Exception as e:
        current_app.logger.error(f"Error loading lesson {lesson_num}: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return None

def convert_lesson_to_passage_format(lesson_data, passage_id):
    """Convert new lesson format to old passage format for compatibility"""
    if not lesson_data:
        return None, []
    
    # Convert passage info
    passage_info = {
        'id': passage_id,
        'title': lesson_data.get('title', ''),
        'text': lesson_data.get('text', ''),
        'category': 'general',
        'difficulty': 7.0,
        'word_count': len(lesson_data.get('text', '').split()),
        'image_url': lesson_data.get('imageUrl', '')
    }
    
    # Convert questions
    questions_data = []
    for idx, q in enumerate(lesson_data.get('questions', []), 1):
        # Find correct answer option ID
        correct_answer = None
        options_dict = {}
        
        for opt in q.get('options', []):
            opt_id = opt.get('id', '')
            opt_text = opt.get('text', '')
            options_dict[opt_id] = opt_text
            if opt.get('correct'):
                correct_answer = opt_id
        
        question_data = {
            'id': idx,  # Use index as ID for compatibility
            'question_number': idx,
            'question_type': 'multiple_choice',  # All new questions are multiple choice
            'question_text': q.get('question', ''),
            'correct_answer': correct_answer or '',
            'explanation': next((opt.get('explanation', '') for opt in q.get('options', []) if opt.get('correct')), ''),
            'options': options_dict
        }
        questions_data.append(question_data)
    
    return passage_info, questions_data


@english_bp.route('/passage/<int:passage_id>', methods=['GET'])
@login_required
def get_passage(passage_id):
    """Get passage with questions - NOW USES NEW LESSONS FROM JS FILES"""
    try:
        current_app.logger.info(f"Getting passage {passage_id}")
        
        # Map old passage ID to new lesson number
        lesson_num = PASSAGE_ID_TO_LESSON_MAP.get(passage_id)
        current_app.logger.info(f"Passage ID {passage_id} mapped to lesson {lesson_num}")
        
        if not lesson_num:
            # If passage ID not in map, try to use it directly (for new IDs 1-10)
            if 1 <= passage_id <= 10:
                lesson_num = passage_id
                current_app.logger.info(f"Using passage ID directly as lesson number: {lesson_num}")
            else:
                # Fallback to old DB system for unknown IDs
                current_app.logger.warning(f"Passage ID {passage_id} not in map, falling back to DB")
                passage = EnglishPassage.query.get_or_404(passage_id)
                questions = EnglishQuestion.query.filter_by(
                    passage_id=passage_id
                ).order_by(EnglishQuestion.question_number).all()
                
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
        
        # Load new lesson from JS file
        current_app.logger.info(f"Loading lesson {lesson_num} from file")
        lesson_data = get_lesson_from_file(lesson_num)
        
        if not lesson_data:
            current_app.logger.error(f"Failed to load lesson {lesson_num} for passage {passage_id}")
            return jsonify({'error': f'Lesson {lesson_num} not found or failed to parse'}), 404
        
        current_app.logger.info(f"Successfully loaded lesson {lesson_num}")
        
        # Check if client wants full format (new frontend)
        use_full_format = request.args.get('format') == 'full' or request.headers.get('X-Use-Full-Format') == 'true'
        
        if use_full_format:
            # Return full lesson data for new frontend
            return jsonify({
                'success': True,
                'lesson': {
                    'id': lesson_data.get('id', f'lesson_{lesson_num:03d}'),
                    'title': lesson_data.get('title', ''),
                    'text': lesson_data.get('text', ''),
                    'paragraphs': lesson_data.get('paragraphs', []),
                    'vocabulary': lesson_data.get('vocabulary', []),
                    'questions': lesson_data.get('questions', []),
                    'recommendedSequence': lesson_data.get('recommendedSequence', []),
                    'spacedRepetition': lesson_data.get('spacedRepetition', {}),
                    'imageUrl': lesson_data.get('imageUrl', ''),
                    'estimatedTime': lesson_data.get('estimatedTime', 15),
                    'language': lesson_data.get('language', 'English'),
                    'professionContext': lesson_data.get('professionContext', '')
                },
                'passage_id': passage_id  # Keep for compatibility
            })
        else:
            # Convert to old format for backward compatibility
            current_app.logger.info(f"Converting lesson {lesson_num} to old passage format")
            passage_info, questions_data = convert_lesson_to_passage_format(lesson_data, passage_id)
            
            if not passage_info:
                current_app.logger.error(f"Failed to convert lesson {lesson_num} to passage format")
                return jsonify({'error': 'Failed to convert lesson'}), 500
            
            current_app.logger.info(f"Successfully converted lesson {lesson_num}, returning {len(questions_data)} questions")
            
            return jsonify({
                'passage': passage_info,
                'questions': questions_data
            })
    except Exception as e:
        current_app.logger.error(f"Error getting passage: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return jsonify({'error': str(e)}), 500


@english_bp.route('/submit', methods=['POST'])
@login_required
def submit_answers():
    """Submit answers and calculate score"""
    try:
        # Log request data for debugging
        current_app.logger.info(f"English submit request - Content-Type: {request.content_type}")
        current_app.logger.info(f"English submit request - Is JSON: {request.is_json}")
        
        if not request.is_json:
            current_app.logger.error("English submit: Request is not JSON")
            return jsonify({'error': 'Request must be JSON'}), 400
        
        data = request.get_json()
        if not data:
            current_app.logger.error("English submit: No data received")
            return jsonify({'error': 'No data received'}), 400
        
        current_app.logger.info(f"English submit data: {data}")
        
        passage_id = data.get('passage_id')
        answers = data.get('answers', {})  # {question_id: answer}
        time_spent = data.get('time_spent', 0)  # seconds
        
        # Convert passage_id to int if it's a string
        if passage_id:
            try:
                passage_id = int(passage_id)
            except (ValueError, TypeError):
                current_app.logger.error(f"English submit: Invalid passage_id type: {type(passage_id)}, value: {passage_id}")
                return jsonify({'error': 'Invalid passage ID format'}), 400
        
        if not passage_id:
            current_app.logger.error(f"English submit: Missing passage_id. Data: {data}")
            return jsonify({'error': 'Passage ID required'}), 400
        
        # Validate answers is a dict
        if not isinstance(answers, dict):
            current_app.logger.error(f"English submit: Invalid answers type: {type(answers)}, value: {answers}")
            return jsonify({'error': 'Answers must be an object'}), 400
        
        # Map old passage ID to new lesson number
        lesson_num = PASSAGE_ID_TO_LESSON_MAP.get(passage_id)
        if not lesson_num:
            if 1 <= passage_id <= 10:
                lesson_num = passage_id
            else:
                # Fallback to old DB system
                passage = EnglishPassage.query.get_or_404(passage_id)
                questions = EnglishQuestion.query.filter_by(passage_id=passage_id).all()
                
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
                
                # Continue with old system (rest of function)
                percentage = int((correct_count / total_questions * 100)) if total_questions > 0 else 0
                estimated_band = estimate_ielts_band(percentage)
                xp_earned = correct_count * 10
                completion_time = datetime.now(timezone.utc)
                progress = UserEnglishProgress(
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
                    item_type='english',
                    item_id=passage_id,
                    is_correct=is_session_mastered,
                    session_reference=f'english-{session_date.isoformat()}',
                    session_date=session_date
                )
                db.session.commit()
                
                return jsonify({
                    'success': True,
                    'score': correct_count,
                    'total': total_questions,
                    'percentage': percentage,
                    'estimated_band': estimated_band,
                    'xp_earned': xp_earned,
                    'results': results
                })
        
        # Load new lesson from JS file
        lesson_data = get_lesson_from_file(lesson_num)
        if not lesson_data:
            return jsonify({'error': 'Lesson not found'}), 404
        
        # Check answers against new lesson
        correct_count = 0
        total_questions = len(lesson_data.get('questions', []))
        results = []
        
        for idx, q in enumerate(lesson_data.get('questions', []), 1):
            # Get user answer (can be question ID or question number)
            user_answer = answers.get(str(idx), '').strip() or answers.get(q.get('id', ''), '').strip()
            
            # Find correct answer option ID
            correct_answer = None
            for opt in q.get('options', []):
                if opt.get('correct'):
                    correct_answer = opt.get('id', '')
                    break
            
            is_correct = user_answer == correct_answer
            
            if is_correct:
                correct_count += 1
            
            # Get explanation from selected option
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
        
        # Calculate percentage
        percentage = int((correct_count / total_questions * 100)) if total_questions > 0 else 0
        
        # Estimate IELTS band (simplified)
        estimated_band = estimate_ielts_band(percentage)
        
        # Calculate XP (10 XP per correct answer)
        xp_earned = correct_count * 10
        
        # Save progress
        completion_time = datetime.now(timezone.utc)
        progress = UserEnglishProgress(
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
            item_type='english',
            item_id=passage_id,
            is_correct=is_session_mastered,
            session_reference=f'english-{session_date.isoformat()}',
            session_date=session_date
        )
        
        # Update user XP
        current_user.xp = (current_user.xp or 0) + xp_earned
        db.session.commit()
        
        return jsonify({
            'score': correct_count,
            'total': total_questions,
            'percentage': percentage,
            'estimated_band': estimated_band,
            'xp_earned': xp_earned,
            'results': results
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error submitting answers: {str(e)}")
        return jsonify({'error': str(e)}), 500


def estimate_ielts_band(percentage: int) -> float:
    """Estimate IELTS band from percentage score"""
    if percentage >= 90:
        return 8.5
    elif percentage >= 80:
        return 7.5
    elif percentage >= 70:
        return 6.5
    elif percentage >= 60:
        return 5.5
    elif percentage >= 50:
        return 5.0
    else:
        return 4.5


# Admin routes for managing passages
@english_bp.route('/admin/passages', methods=['GET'])
@login_required
def list_passages():
    """List all passages (admin only)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        passages = EnglishPassage.query.order_by(EnglishPassage.created_at.desc()).all()
        
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
        current_app.logger.error(f"Error listing passages: {str(e)}")
        return jsonify({'error': str(e)}), 500


@english_bp.route('/admin/passage', methods=['POST'])
@login_required
def create_passage():
    """Create new passage (admin only)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        
        passage = EnglishPassage(
            title=data.get('title'),
            text=data.get('text'),
            category=data.get('category'),
            difficulty=data.get('difficulty', 7),
            word_count=data.get('word_count')
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
        current_app.logger.error(f"Error creating passage: {str(e)}")
        return jsonify({'error': str(e)}), 500


@english_bp.route('/admin/question', methods=['POST'])
@login_required
def create_question():
    """Create new question for passage (admin only)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        
        # Prepare options JSON
        options = data.get('options', {})
        if isinstance(options, dict):
            options = json.dumps(options)
        
        question = EnglishQuestion(
            passage_id=data.get('passage_id'),
            question_number=data.get('question_number'),
            question_type=data.get('question_type'),
            question_text=data.get('question_text'),
            correct_answer=data.get('correct_answer'),
            options=options,
            explanation=data.get('explanation')
        )
        
        db.session.add(question)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'question': {
                'id': question.id,
                'question_number': question.question_number
            }
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error creating question: {str(e)}")
        return jsonify({'error': str(e)}), 500


@english_bp.route('/admin/question/<int:question_id>', methods=['PUT', 'PATCH'])
@login_required
def update_question(question_id):
    """Update existing question (admin only)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        question = EnglishQuestion.query.get_or_404(question_id)
        data = request.get_json()
        
        # Update fields if provided
        if 'question_number' in data:
            question.question_number = data.get('question_number')
        if 'question_type' in data:
            question.question_type = data.get('question_type')
        if 'question_text' in data:
            question.question_text = data.get('question_text')
        if 'correct_answer' in data:
            question.correct_answer = data.get('correct_answer')
        if 'options' in data:
            options = data.get('options', {})
            if isinstance(options, dict):
                question.options = json.dumps(options)
            else:
                question.options = options
        if 'explanation' in data:
            question.explanation = data.get('explanation')
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'question': {
                'id': question.id,
                'question_number': question.question_number,
                'question_type': question.question_type
            }
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating question: {str(e)}")
        return jsonify({'error': str(e)}), 500


@english_bp.route('/admin/question/<int:question_id>', methods=['DELETE'])
@login_required
def delete_question(question_id):
    """Delete question (admin only)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        question = EnglishQuestion.query.get_or_404(question_id)
        passage_id = question.passage_id
        
        db.session.delete(question)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Question deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting question: {str(e)}")
        return jsonify({'error': str(e)}), 500


@english_bp.route('/admin/passage/<int:passage_id>', methods=['PUT', 'PATCH'])
@login_required
def update_passage(passage_id):
    """Update existing passage (admin only)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        passage = EnglishPassage.query.get_or_404(passage_id)
        data = request.get_json()
        
        # Update fields if provided
        if 'title' in data:
            passage.title = data.get('title')
        if 'text' in data:
            passage.text = data.get('text')
        if 'category' in data:
            passage.category = data.get('category')
        if 'difficulty' in data:
            passage.difficulty = data.get('difficulty')
        if 'word_count' in data:
            passage.word_count = data.get('word_count')
        if 'image_url' in data:
            passage.image_url = data.get('image_url')
        
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
        current_app.logger.error(f"Error updating passage: {str(e)}")
        return jsonify({'error': str(e)}), 500


@english_bp.route('/admin/passage/<int:passage_id>/questions', methods=['GET'])
@login_required
def get_passage_questions(passage_id):
    """Get all questions for a passage (admin only)"""
    if not current_user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        passage = EnglishPassage.query.get_or_404(passage_id)
        questions = EnglishQuestion.query.filter_by(passage_id=passage_id).order_by(EnglishQuestion.question_number).all()
        
        questions_data = []
        for q in questions:
            question_data = {
                'id': q.id,
                'passage_id': q.passage_id,
                'question_number': q.question_number,
                'question_type': q.question_type,
                'question_text': q.question_text,
                'correct_answer': q.correct_answer,
                'explanation': q.explanation
            }
            
            # Parse options
            if q.options:
                try:
                    question_data['options'] = json.loads(q.options) if isinstance(q.options, str) else q.options
                except:
                    question_data['options'] = {}
            else:
                question_data['options'] = {}
            
            questions_data.append(question_data)
        
        return jsonify({
            'passage': {
                'id': passage.id,
                'title': passage.title
            },
            'questions': questions_data
        })
    except Exception as e:
        current_app.logger.error(f"Error getting passage questions: {str(e)}")
        return jsonify({'error': str(e)}), 500


