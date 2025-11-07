# routes/english_routes.py
# English Reading (IELTS) Routes

from flask import Blueprint, jsonify, request, render_template, current_app
from flask_login import login_required, current_user
from extensions import db
from models import EnglishPassage, EnglishQuestion, UserEnglishProgress
from datetime import datetime, timezone
import json
from utils.ielts_generator import parse_generated_passage, generate_passage_title_from_topic
from utils.mastery_helpers import update_item_mastery

english_bp = Blueprint('english', __name__, url_prefix='/api/english')


@english_bp.route('/passage/<int:passage_id>', methods=['GET'])
@login_required
def get_passage(passage_id):
    """Get passage with questions"""
    try:
        passage = EnglishPassage.query.get_or_404(passage_id)
        
        # Get questions ordered by question_number
        questions = EnglishQuestion.query.filter_by(
            passage_id=passage_id
        ).order_by(EnglishQuestion.question_number).all()
        
        # Format questions for frontend
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
            
            # Add options if available
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
        current_app.logger.error(f"Error getting passage: {str(e)}")
        return jsonify({'error': str(e)}), 500


@english_bp.route('/submit', methods=['POST'])
@login_required
def submit_answers():
    """Submit answers and calculate score"""
    try:
        data = request.get_json()
        passage_id = data.get('passage_id')
        answers = data.get('answers', {})  # {question_id: answer}
        time_spent = data.get('time_spent', 0)  # seconds
        
        if not passage_id:
            return jsonify({'error': 'Passage ID required'}), 400
        
        # Get passage and questions
        passage = EnglishPassage.query.get_or_404(passage_id)
        questions = EnglishQuestion.query.filter_by(passage_id=passage_id).all()
        
        # Calculate score
        correct_count = 0
        total_questions = len(questions)
        results = []
        
        for q in questions:
            user_answer = answers.get(str(q.id), '').strip()
            correct_answer = q.correct_answer.strip() if q.correct_answer else ''
            
            # Case-insensitive comparison
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


