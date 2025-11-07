from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta, timezone
from flask import current_app
from models import (
    StudySession, TestAttempt, VirtualPatientAttempt, DailyFlashcardProgress
)
from extensions import db

daily_progress_bp = Blueprint('daily_progress', __name__, url_prefix='/api')

@daily_progress_bp.route('/daily-progress', methods=['GET'])
@login_required
def get_daily_progress():
    """
    Получить прогресс пользователя на сегодня (календарный день)
    Все компоненты используют календарный день, сбрасываются в полночь
    """
    try:
        # Используем календарный день (сброс в полночь)
        try:
            now = datetime.now(timezone.utc)
        except Exception:
            now = datetime.now()
        
        # Получаем начало и конец сегодняшнего дня в UTC
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        current_app.logger.info(f"Daily progress check: user={current_user.id}, today_start={today_start}, today_end={today_end}")
        
        # Tests progress - используем DiagnosticSession с календарным днем
        from models import DiagnosticSession
        tests_today = DiagnosticSession.query.filter(
            DiagnosticSession.user_id == current_user.id,
            DiagnosticSession.started_at >= today_start,
            DiagnosticSession.started_at < today_end  # До начала следующего дня
        ).all()
        
        tests_completed = len([t for t in tests_today if getattr(t, 'completed_at', None) is not None])
        tests_in_progress = len([t for t in tests_today if getattr(t, 'completed_at', None) is None])
        
        # Terms progress - get from daily flashcard progress (уже использует календарный день)
        daily_flashcard = DailyFlashcardProgress.query.filter_by(
            user_id=current_user.id,
            date=now.date()  # Календарный день
        ).first()
        
        terms_completed = daily_flashcard.terms_studied if daily_flashcard and daily_flashcard.terms_studied is not None else 0
        terms_in_progress = 1 if terms_completed == 0 else 0  # Show as in progress if not completed
        
        # Log the progress
        current_app.logger.info(f"Daily progress check: user={current_user.id}, terms_studied={terms_completed}, daily_flashcard={daily_flashcard}")
        
        # VP progress - используем календарный день
        vp_today = VirtualPatientAttempt.query.filter(
            VirtualPatientAttempt.user_id == current_user.id,
            VirtualPatientAttempt.started_at >= today_start,
            VirtualPatientAttempt.started_at < today_end  # До начала следующего дня
        ).all()
        
        vp_completed = len([v for v in vp_today if getattr(v, 'completed', False)])
        vp_in_progress = len([v for v in vp_today if not getattr(v, 'completed', False)])
        
        # Calculate scores
        today_score = sum([getattr(t, 'correct_answers', 0) for t in tests_today if getattr(t, 'completed_at', None) is not None]) + \
                     sum([getattr(v, 'score', 0) for v in vp_today if getattr(v, 'completed', False)])
        
        # Calculate study time (in minutes)
        study_time = 0
        
        # Time from tests (DiagnosticSession)
        tests_time = 0
        for t in tests_today:
            duration = getattr(t, 'time_spent', None)
            if duration is None or duration == 0:
                duration = getattr(t, 'actual_duration', 0) or 0
            tests_time += duration
        study_time += tests_time
        
        # Time from virtual patients
        vp_time = 0
        for v in vp_today:
            # VirtualPatientAttempt использует time_spent (в минутах)
            duration = getattr(v, 'time_spent', 0) or 0
            if duration > 0:
                vp_time += duration
                current_app.logger.info(f"VP time added: attempt_id={v.id}, time_spent={duration}, completed={v.completed}")
        study_time += vp_time
        
        # Time from terms (DailyFlashcardProgress)
        terms_time = 0
        if daily_flashcard:
            # Используем реальное время, если оно сохранено
            # Проверяем, есть ли поле time_spent в DailyFlashcardProgress
            if hasattr(daily_flashcard, 'time_spent'):
                terms_duration = daily_flashcard.time_spent
                # Используем реальное время только если оно больше 0
                # Если 0, значит время еще не было сохранено (старые записи)
                if terms_duration and terms_duration > 0:
                    terms_time = terms_duration
                # Если time_spent = 0 или None, не используем fallback - просто 0
                # (fallback был неточным и давал неправильные значения)
            # Если поля нет (старая версия БД), используем 0
        study_time += terms_time
        
        # Логирование для диагностики
        current_app.logger.info(f"Daily study time calculation: user={current_user.id}, tests={tests_time}min, vp={vp_time}min, terms={terms_time}min, total={study_time}min")
        
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
        # Логируем, но возвращаем «мягкий» нулевой прогресс, чтобы не ломать страницу
        try:
            current_app.logger.exception(f"/api/daily-progress failed: {e}")
        except Exception:
            pass
        return jsonify({
            'success': True,
            'progress': {
                'tests': {
                    'completed': False,
                    'in_progress': False,
                    'progress': 0,
                    'total': 1
                },
                'terms': {
                    'completed': False,
                    'in_progress': False,
                    'progress': 0,
                    'total': 10
                },
                'virtual_patient': {
                    'completed': False,
                    'in_progress': False,
                    'total': 1
                },
                'today_score': 0,
                'study_time': '0 min'
            }
        }), 200

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
            time_spent = data.get('time_spent', 0)  # Время в минутах
            
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
            current_time_spent = getattr(daily_progress, 'time_spent', 0) or 0
            
            daily_progress.terms_studied = min(current_terms_studied + terms_studied, 10)  # Cap at 10 terms per day
            daily_progress.terms_completed = current_terms_completed + 1  # One session completed
            daily_progress.xp_earned = current_xp_earned + score
            daily_progress.session_count = current_session_count + 1
            daily_progress.last_session = datetime.now()
            
            # Сохраняем время, если поле существует
            if hasattr(daily_progress, 'time_spent'):
                daily_progress.time_spent = current_time_spent + time_spent
                current_app.logger.info(f"Updated time_spent: user={current_user.id}, current={current_time_spent}, added={time_spent}, total={daily_progress.time_spent}")
            else:
                # Если поля нет, используем fallback вычисление позже
                current_app.logger.warning(f"time_spent field not found in DailyFlashcardProgress for user={current_user.id}")
            
            # Log the update
            current_app.logger.info(f"Updated daily progress: user={current_user.id}, terms_studied={daily_progress.terms_studied}, terms_completed={daily_progress.terms_completed}, time_spent={getattr(daily_progress, 'time_spent', 'N/A')}")
        
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
