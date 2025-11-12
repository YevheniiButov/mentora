# routes/archive_api.py
# Archive API - Get completed learning items

from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from datetime import datetime, timedelta, timezone
from extensions import db
from models import (
    UserEnglishProgress, UserTermProgress, DiagnosticSession,
    VirtualPatientAttempt, EnglishPassage, MedicalTerm, VirtualPatientScenario
)
from sqlalchemy import func, desc, asc

archive_api_bp = Blueprint('archive_api', __name__, url_prefix='/api/archive')


@archive_api_bp.route('/english', methods=['GET'])
@login_required
def get_english_archive():
    """Get completed English reading passages"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        sort_by = request.args.get('sort_by', 'date')  # date, score, time
        sort_order = request.args.get('sort_order', 'desc')  # asc, desc
        
        query = UserEnglishProgress.query.filter_by(user_id=current_user.id)
        
        # Search filter
        if search:
            # Search in passage titles (need to join with EnglishPassage or use lesson mapping)
            query = query.join(EnglishPassage, UserEnglishProgress.passage_id == EnglishPassage.id)
            query = query.filter(EnglishPassage.title.ilike(f'%{search}%'))
        
        # Sorting
        if sort_by == 'date':
            order_col = UserEnglishProgress.completed_at.desc() if sort_order == 'desc' else UserEnglishProgress.completed_at.asc()
        elif sort_by == 'score':
            # Calculate score percentage
            order_col = func.cast(UserEnglishProgress.score, db.Float) / func.cast(UserEnglishProgress.total_questions, db.Float)
            order_col = desc(order_col) if sort_order == 'desc' else asc(order_col)
        elif sort_by == 'time':
            order_col = UserEnglishProgress.time_spent.desc() if sort_order == 'desc' else UserEnglishProgress.time_spent.asc()
        else:
            order_col = UserEnglishProgress.completed_at.desc()
        
        query = query.order_by(order_col)
        
        # Pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        items = []
        for progress in pagination.items:
            # Map passage_id to lesson number
            from routes.english_routes import PASSAGE_ID_TO_LESSON_MAP
            lesson_num = PASSAGE_ID_TO_LESSON_MAP.get(progress.passage_id)
            if not lesson_num and 1 <= progress.passage_id <= 10:
                lesson_num = progress.passage_id
            
            # Try to get passage title
            passage = EnglishPassage.query.get(progress.passage_id)
            title = passage.title if passage else f'Lesson {lesson_num or progress.passage_id}'
            
            score_percentage = (progress.score / progress.total_questions * 100) if progress.total_questions > 0 else 0
            
            items.append({
                'id': progress.id,
                'passage_id': progress.passage_id,
                'lesson_num': lesson_num,
                'title': title,
                'score': progress.score,
                'total_questions': progress.total_questions,
                'score_percentage': round(score_percentage, 1),
                'time_spent': progress.time_spent or 0,
                'completed_at': progress.completed_at.isoformat() if progress.completed_at else None,
                'type': 'english'
            })
        
        return jsonify({
            'success': True,
            'items': items,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })
    except Exception as e:
        import traceback
        current_app.logger.error(f"Error getting English archive: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


@archive_api_bp.route('/terms', methods=['GET'])
@login_required
def get_terms_archive():
    """Get studied Dutch terms"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        category = request.args.get('category', '').strip()
        sort_by = request.args.get('sort_by', 'date')  # date, mastery, accuracy
        sort_order = request.args.get('sort_order', 'desc')
        
        query = UserTermProgress.query.filter_by(user_id=current_user.id)
        
        # Join with MedicalTerm for filtering
        query = query.join(MedicalTerm, UserTermProgress.term_id == MedicalTerm.id)
        
        # Search filter
        if search:
            query = query.filter(
                (MedicalTerm.term_nl.ilike(f'%{search}%')) |
                (MedicalTerm.term_en.ilike(f'%{search}%'))
            )
        
        # Category filter
        if category:
            query = query.filter(MedicalTerm.category == category)
        
        # Sorting
        if sort_by == 'date':
            order_col = UserTermProgress.last_reviewed.desc() if sort_order == 'desc' else UserTermProgress.last_reviewed.asc()
        elif sort_by == 'mastery':
            order_col = UserTermProgress.mastery_level.desc() if sort_order == 'desc' else UserTermProgress.mastery_level.asc()
        elif sort_by == 'accuracy':
            # Calculate accuracy
            order_col = func.cast(UserTermProgress.times_correct, db.Float) / func.cast(UserTermProgress.times_reviewed, db.Float)
            order_col = desc(order_col) if sort_order == 'desc' else asc(order_col)
        else:
            order_col = UserTermProgress.last_reviewed.desc()
        
        query = query.order_by(order_col)
        
        # Pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        items = []
        for progress in pagination.items:
            term = progress.term
            accuracy = progress.accuracy_rate if progress.times_reviewed > 0 else 0
            
            items.append({
                'id': progress.id,
                'term_id': progress.term_id,
                'term_nl': term.term_nl,
                'term_en': term.term_en or term.term_nl,
                'category': term.category,
                'mastery_level': progress.mastery_level,
                'accuracy': round(accuracy, 1),
                'times_reviewed': progress.times_reviewed,
                'last_reviewed': progress.last_reviewed.isoformat() if progress.last_reviewed else None,
                'next_review': progress.next_review.isoformat() if progress.next_review else None,
                'type': 'terms'
            })
        
        return jsonify({
            'success': True,
            'items': items,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })
    except Exception as e:
        from flask import current_app
        import traceback
        current_app.logger.error(f"Error getting terms archive: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


@archive_api_bp.route('/tests', methods=['GET'])
@login_required
def get_tests_archive():
    """Get completed medical tests"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        session_type = request.args.get('session_type', '').strip()
        sort_by = request.args.get('sort_by', 'date')  # date, score, questions
        sort_order = request.args.get('sort_order', 'desc')
        
        query = DiagnosticSession.query.filter_by(user_id=current_user.id, status='completed')
        
        # Session type filter
        if session_type:
            query = query.filter(DiagnosticSession.session_type == session_type)
        
        # Sorting
        if sort_by == 'date':
            order_col = DiagnosticSession.completed_at.desc() if sort_order == 'desc' else DiagnosticSession.completed_at.asc()
        elif sort_by == 'score':
            # Calculate score percentage
            order_col = func.cast(DiagnosticSession.correct_answers, db.Float) / func.cast(DiagnosticSession.questions_answered, db.Float)
            order_col = desc(order_col) if sort_order == 'desc' else asc(order_col)
        elif sort_by == 'questions':
            order_col = DiagnosticSession.questions_answered.desc() if sort_order == 'desc' else DiagnosticSession.questions_answered.asc()
        else:
            order_col = DiagnosticSession.completed_at.desc()
        
        query = query.order_by(order_col)
        
        # Pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        items = []
        for session in pagination.items:
            score_percentage = (session.correct_answers / session.questions_answered * 100) if session.questions_answered > 0 else 0
            
            items.append({
                'id': session.id,
                'session_type': session.session_type,
                'session_type_label': session.session_type.replace('_', ' ').title(),
                'questions_answered': session.questions_answered,
                'correct_answers': session.correct_answers,
                'score_percentage': round(score_percentage, 1),
                'current_ability': round(session.current_ability, 3) if session.current_ability else None,
                'time_spent': session.time_spent or 0,
                'started_at': session.started_at.isoformat() if session.started_at else None,
                'completed_at': session.completed_at.isoformat() if session.completed_at else None,
                'type': 'tests'
            })
        
        return jsonify({
            'success': True,
            'items': items,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })
    except Exception as e:
        from flask import current_app
        import traceback
        current_app.logger.error(f"Error getting tests archive: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


@archive_api_bp.route('/virtual-patients', methods=['GET'])
@login_required
def get_vp_archive():
    """Get completed virtual patients"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '').strip()
        sort_by = request.args.get('sort_by', 'date')  # date, score
        sort_order = request.args.get('sort_order', 'desc')
        
        query = VirtualPatientAttempt.query.filter_by(user_id=current_user.id, completed=True)
        
        # Join with VirtualPatientScenario for search
        query = query.join(VirtualPatientScenario, VirtualPatientAttempt.scenario_id == VirtualPatientScenario.id)
        
        # Search filter
        if search:
            query = query.filter(VirtualPatientScenario.title.ilike(f'%{search}%'))
        
        # Sorting
        if sort_by == 'date':
            order_col = VirtualPatientAttempt.completed_at.desc() if sort_order == 'desc' else VirtualPatientAttempt.completed_at.asc()
        elif sort_by == 'score':
            # Use percentage_score property
            order_col = VirtualPatientAttempt.percentage_score.desc() if sort_order == 'desc' else VirtualPatientAttempt.percentage_score.asc()
        else:
            order_col = VirtualPatientAttempt.completed_at.desc()
        
        query = query.order_by(order_col)
        
        # Pagination
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        items = []
        for attempt in pagination.items:
            scenario = attempt.scenario
            score = attempt.percentage_score if hasattr(attempt, 'percentage_score') else 0
            
            items.append({
                'id': attempt.id,
                'scenario_id': attempt.scenario_id,
                'title': scenario.title if scenario else 'Unknown Scenario',
                'score': round(score, 1),
                'time_spent': attempt.time_spent or 0,
                'started_at': attempt.started_at.isoformat() if attempt.started_at else None,
                'completed_at': attempt.completed_at.isoformat() if attempt.completed_at else None,
                'type': 'virtual_patients'
            })
        
        return jsonify({
            'success': True,
            'items': items,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': pagination.total,
                'pages': pagination.pages
            }
        })
    except Exception as e:
        from flask import current_app
        import traceback
        current_app.logger.error(f"Error getting VP archive: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500


@archive_api_bp.route('/stats', methods=['GET'])
@login_required
def get_archive_stats():
    """Get archive statistics"""
    try:
        # English passages
        english_progresses = UserEnglishProgress.query.filter_by(user_id=current_user.id).all()
        english_count = len(english_progresses)
        if english_count > 0:
            english_scores = [
                (p.score / p.total_questions * 100) 
                for p in english_progresses 
                if p.total_questions and p.total_questions > 0
            ]
            english_avg_score = sum(english_scores) / len(english_scores) if english_scores else 0
        else:
            english_avg_score = 0
        
        # Terms
        terms_count = UserTermProgress.query.filter_by(user_id=current_user.id).count()
        terms_avg_mastery = db.session.query(func.avg(UserTermProgress.mastery_level)).filter_by(user_id=current_user.id).scalar() or 0
        
        # Tests
        test_sessions = DiagnosticSession.query.filter_by(user_id=current_user.id, status='completed').all()
        tests_count = len(test_sessions)
        if tests_count > 0:
            test_scores = [
                (s.correct_answers / s.questions_answered * 100)
                for s in test_sessions
                if s.questions_answered and s.questions_answered > 0
            ]
            tests_avg_score = sum(test_scores) / len(test_scores) if test_scores else 0
        else:
            tests_avg_score = 0
        
        # Virtual Patients
        vp_attempts = VirtualPatientAttempt.query.filter_by(user_id=current_user.id, completed=True).all()
        vp_count = len(vp_attempts)
        if vp_count > 0:
            vp_scores = [attempt.percentage_score for attempt in vp_attempts if attempt.max_score > 0]
            vp_avg_score = sum(vp_scores) / len(vp_scores) if vp_scores else 0
        else:
            vp_avg_score = 0
        
        return jsonify({
            'success': True,
            'stats': {
                'english': {
                    'total': english_count,
                    'avg_score': round(english_avg_score, 1)
                },
                'terms': {
                    'total': terms_count,
                    'avg_mastery': round(terms_avg_mastery, 1)
                },
                'tests': {
                    'total': tests_count,
                    'avg_score': round(tests_avg_score, 1)
                },
                'virtual_patients': {
                    'total': vp_count,
                    'avg_score': round(vp_avg_score, 1)
                }
            }
        })
    except Exception as e:
        from flask import current_app
        import traceback
        current_app.logger.error(f"Error getting archive stats: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

