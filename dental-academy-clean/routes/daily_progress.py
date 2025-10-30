from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from models import (
    StudySession, TestAttempt, VirtualPatientAttempt, DailyFlashcardProgress
)
from extensions import db

daily_progress_bp = Blueprint('daily_progress', __name__, url_prefix='/api')

@daily_progress_bp.route('/daily-progress', methods=['GET'])
@login_required
def get_daily_progress():
    """
    Получить прогресс пользователя на сегодня
    """
    try:
        # Используем последние 24 часа вместо календарного дня
        now = datetime.now()
        yesterday = now - timedelta(hours=24)
        
        # Tests progress - используем DiagnosticSession вместо TestAttempt
        from models import DiagnosticSession
        tests_today = DiagnosticSession.query.filter(
            DiagnosticSession.user_id == current_user.id,
            DiagnosticSession.started_at >= yesterday,
            DiagnosticSession.started_at <= now
        ).all()
        
        tests_completed = len([t for t in tests_today if t.completed_at is not None])
        tests_in_progress = len([t for t in tests_today if t.completed_at is None])
        
        # Terms progress - get from daily flashcard progress
        daily_flashcard = DailyFlashcardProgress.query.filter_by(
            user_id=current_user.id,
            date=now.date()
        ).first()
        
        terms_completed = daily_flashcard.terms_studied if daily_flashcard and daily_flashcard.terms_studied is not None else 0
        terms_in_progress = 1 if terms_completed == 0 else 0  # Show as in progress if not completed
        
        # Log the progress
        print(f"Daily progress check: user={current_user.id}, terms_studied={terms_completed}, daily_flashcard={daily_flashcard}")
        
        # VP progress
        vp_today = VirtualPatientAttempt.query.filter(
            VirtualPatientAttempt.user_id == current_user.id,
            VirtualPatientAttempt.started_at >= yesterday,
            VirtualPatientAttempt.started_at <= now
        ).all()
        
        vp_completed = len([v for v in vp_today if v.completed])
        vp_in_progress = len([v for v in vp_today if not v.completed])
        
        # Calculate scores
        today_score = sum([t.correct_answers for t in tests_today if t.completed_at is not None]) + \
                     sum([v.score for v in vp_today if v.completed])
        
        # Calculate study time (in minutes)
        study_time = 0
        for t in tests_today:
            if hasattr(t, 'actual_duration') and t.actual_duration:
                study_time += t.actual_duration
        for v in vp_today:
            if hasattr(v, 'duration'):
                study_time += v.duration
        
        return jsonify({
            'success': True,
            'progress': {
                'tests': {
                    'completed': tests_completed >= 1,  # true if at least 1 session completed
                    'in_progress': tests_in_progress > 0,
                    'progress': min(tests_completed * 100, 100),  # 100% if completed
                    'total': 1
                },
                'terms': {
                    'completed': terms_completed >= 1,  # true if at least 10 done
                    'in_progress': terms_in_progress > 0,
                    'progress': min(terms_completed * 10, 100),  # Assuming 10 terms
                    'total': 10
                },
                'virtual_patient': {
                    'completed': vp_completed > 0,
                    'in_progress': vp_in_progress > 0,
                    'total': 1
                },
                'today_score': today_score,
                'study_time': f'{int(study_time)} min'
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@daily_progress_bp.route('/daily-progress/update', methods=['POST'])
@login_required
def update_daily_progress():
    """
    Обновить прогресс после завершения компонента
    """
    try:
        data = request.get_json()
        print(f"Received data: {data}")
        
        component_type = data.get('type')  # 'tests', 'terms', 'vp'
        status = data.get('status')  # 'completed', 'in_progress'
        score = data.get('score', 0)
        terms_studied = data.get('terms_studied', 0)
        
        print(f"Processing: type={component_type}, status={status}, score={score}, terms_studied={terms_studied}")
        
        # Update daily flashcard progress if it's a terms session
        if component_type == 'terms' and status == 'completed':
            today = datetime.now().date()
            
            # Get or create daily progress record
            daily_progress = DailyFlashcardProgress.query.filter_by(
                user_id=current_user.id,
                date=today
            ).first()
            
            if not daily_progress:
                daily_progress = DailyFlashcardProgress(
                    user_id=current_user.id,
                    date=today
                )
                db.session.add(daily_progress)
            
            # Update progress
            # Handle None values by defaulting to 0
            current_terms_studied = daily_progress.terms_studied or 0
            current_terms_completed = daily_progress.terms_completed or 0
            current_xp_earned = daily_progress.xp_earned or 0
            current_session_count = daily_progress.session_count or 0
            
            daily_progress.terms_studied = min(current_terms_studied + terms_studied, 10)  # Cap at 10 terms per day
            daily_progress.terms_completed = current_terms_completed + 1  # One session completed
            daily_progress.xp_earned = current_xp_earned + score
            daily_progress.session_count = current_session_count + 1
            daily_progress.last_session = datetime.now()
            
            # Log the update
            print(f"Updated daily progress: user={current_user.id}, terms_studied={daily_progress.terms_studied}, terms_completed={daily_progress.terms_completed}")
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Progress updated'
        }), 200
        
    except Exception as e:
        print(f"Error in update_daily_progress: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500
