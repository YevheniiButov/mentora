# routes/learning.py
# Daily tasks rotation logic for learning activities

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user
from datetime import datetime, timedelta, timezone
from extensions import db
from models import (
    User, DiagnosticSession, VirtualPatientAttempt, 
    DailyFlashcardProgress, UserEnglishProgress
)

daily_tasks_bp = Blueprint('daily_tasks', __name__, url_prefix='/api')


def get_daily_tasks(user_id, study_day=None):
    """
    Generate daily tasks based on rotation schedule.
    
    Args:
        user_id: ID пользователя
        study_day: День учебы (1-14). Если None, вычисляется автоматически.
    
    Returns:
        dict: Задачи на день с учетом ротации
    """
    user = User.query.get(user_id)
    if not user:
        return {'error': 'User not found'}
    
    today = datetime.now(timezone.utc).date()
    
    # Получаем день учебы (1-14) вместо календарных дней
    if study_day is None:
        from utils.individual_plan_helpers import get_study_day
        study_day = get_study_day(user)
    
    # Используем день учебы для расчета cycle_day (ротация на 6 дней)
    cycle_day = ((study_day - 1) % 6) + 1  # 1, 2, 3, 4, 5, or 6
    
    # Get today's start and end timestamps
    today_start = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
    today_end = today_start + timedelta(days=1)
    
    # Check what user completed today
    # Diagnostic tests
    tests_today = DiagnosticSession.query.filter(
        DiagnosticSession.user_id == user_id,
        DiagnosticSession.started_at >= today_start,
        DiagnosticSession.started_at < today_end
    ).all()
    # Check if session is completed (either by status='completed' or completed_at is set)
    tests_completed = len([t for t in tests_today if (
        getattr(t, 'status', None) == 'completed' or 
        getattr(t, 'completed_at', None) is not None
    )])
    
    # Flashcards (terms)
    flashcard_today = DailyFlashcardProgress.query.filter_by(
        user_id=user_id,
        date=today
    ).first()
    flashcards_completed = flashcard_today is not None and flashcard_today.terms_studied and flashcard_today.terms_studied > 0
    
    # Virtual patients
    vp_today = VirtualPatientAttempt.query.filter(
        VirtualPatientAttempt.user_id == user_id,
        VirtualPatientAttempt.started_at >= today_start,
        VirtualPatientAttempt.started_at < today_end
    ).all()
    vp_completed = len([v for v in vp_today if getattr(v, 'completed', False)]) > 0
    
    # English reading
    english_today = UserEnglishProgress.query.filter(
        UserEnglishProgress.user_id == user_id,
        UserEnglishProgress.completed_at >= today_start,
        UserEnglishProgress.completed_at < today_end
    ).all()
    english_completed = len(english_today) > 0
    
    # Memory game (check if user played today - using localStorage on client side)
    # For now, we'll assume it's not completed (client will track this)
    memory_completed = False
    
    # Проверяем, является ли это 14-м или 28-м днем (BIG test)
    is_big_test_day = study_day == 14 or study_day == 28
    
    tasks = {
        'cycle_day': cycle_day,
        'study_day': study_day,
        'is_big_test_day': is_big_test_day,
        'tasks': []
    }
    
    # Если это 14-й день - показываем только BIG test
    if is_big_test_day:
        tasks['tasks'] = [
            {
                'type': 'big_test',
                'title': 'BIG Test',
                'target': 60,
                'icon': 'clipboard-check',
                'completed': False,  # Будет обновляться при прохождении
                'progress': 0,
                'description': 'Comprehensive test with 60 questions from your last 2 weeks of study'
            }
        ]
        return tasks
    
    if cycle_day == 1:
        # Day 1: Tests + Flashcards + English Reading
        tasks['tasks'] = [
            {
                'type': 'diagnostic_test',
                'title': 'Medische Testen',
                'target': 10,
                'icon': 'clipboard-check',
                'completed': tests_completed > 0,
                'progress': min(tests_completed, 10)
            },
            {
                'type': 'flashcards',
                'title': 'Nederlandse Termen',
                'target': 10,
                'icon': 'card-text',
                'completed': flashcards_completed,
                'progress': flashcard_today.terms_studied if flashcard_today and flashcard_today.terms_studied else 0
            },
            {
                'type': 'english_reading',
                'title': 'English Reading',
                'target': 1,
                'icon': 'book',
                'completed': english_completed,
                'progress': 1 if english_completed else 0
            }
        ]
    elif cycle_day == 2:
        # Day 2: Tests + Flashcards + VP
        tasks['tasks'] = [
            {
                'type': 'diagnostic_test',
                'title': 'Medische Testen',
                'target': 10,
                'icon': 'clipboard-check',
                'completed': tests_completed > 0,
                'progress': min(tests_completed, 10)
            },
            {
                'type': 'flashcards',
                'title': 'Nederlandse Termen',
                'target': 10,
                'icon': 'card-text',
                'completed': flashcards_completed,
                'progress': flashcard_today.terms_studied if flashcard_today and flashcard_today.terms_studied else 0
            },
            {
                'type': 'virtual_patient',
                'title': 'Virtual Patient',
                'target': 1,
                'icon': 'person-badge',
                'completed': vp_completed,
                'progress': 1 if vp_completed else 0
            }
        ]
    elif cycle_day == 3:
        # Day 3: Intensive Tests + English Reading
        tasks['tasks'] = [
            {
                'type': 'diagnostic_test',
                'title': 'Medische Testen (Intensief)',
                'target': 20,
                'icon': 'clipboard-check',
                'completed': tests_completed >= 20,
                'progress': min(tests_completed, 20)
            },
            {
                'type': 'english_reading',
                'title': 'English Reading',
                'target': 1,
                'icon': 'book',
                'completed': english_completed,
                'progress': 1 if english_completed else 0
            }
        ]
    elif cycle_day == 4:
        # Day 4: Tests + Flashcards + VP
        tasks['tasks'] = [
            {
                'type': 'diagnostic_test',
                'title': 'Medische Testen',
                'target': 10,
                'icon': 'clipboard-check',
                'completed': tests_completed > 0,
                'progress': min(tests_completed, 10)
            },
            {
                'type': 'flashcards',
                'title': 'Nederlandse Termen',
                'target': 10,
                'icon': 'card-text',
                'completed': flashcards_completed,
                'progress': flashcard_today.terms_studied if flashcard_today and flashcard_today.terms_studied else 0
            },
            {
                'type': 'virtual_patient',
                'title': 'Virtual Patient',
                'target': 1,
                'icon': 'person-badge',
                'completed': vp_completed,
                'progress': 1 if vp_completed else 0
            }
        ]
    elif cycle_day == 5:
        # Day 5: Tests + Memory Game + English Reading
        tasks['tasks'] = [
            {
                'type': 'diagnostic_test',
                'title': 'Medische Testen',
                'target': 10,
                'icon': 'clipboard-check',
                'completed': tests_completed > 0,
                'progress': min(tests_completed, 10)
            },
            {
                'type': 'memory',
                'title': 'Memory Game',
                'target': 1,
                'icon': 'bullseye',
                'completed': memory_completed,
                'progress': 1 if memory_completed else 0
            },
            {
                'type': 'english_reading',
                'title': 'English Reading',
                'target': 1,
                'icon': 'book',
                'completed': english_completed,
                'progress': 1 if english_completed else 0
            }
        ]
    else:  # cycle_day == 6
        # Day 6: Intensive Tests + Flashcards
        tasks['tasks'] = [
            {
                'type': 'diagnostic_test',
                'title': 'Medische Testen (Intensief)',
                'target': 20,
                'icon': 'clipboard-check',
                'completed': tests_completed >= 20,
                'progress': min(tests_completed, 20)
            },
            {
                'type': 'flashcards',
                'title': 'Nederlandse Termen',
                'target': 10,
                'icon': 'card-text',
                'completed': flashcards_completed,
                'progress': flashcard_today.terms_studied if flashcard_today and flashcard_today.terms_studied else 0
            }
        ]
    
    # Calculate daily progress
    completed_count = sum(1 for task in tasks['tasks'] if task['completed'])
    total_count = len(tasks['tasks'])
    tasks['progress'] = int((completed_count / total_count) * 100) if total_count > 0 else 0
    
    return tasks


@daily_tasks_bp.route('/daily-tasks', methods=['GET'])
@login_required
def api_daily_tasks():
    """
    API endpoint for daily tasks with rotation.
    Returns tasks for current study day, synchronized with planner.
    """
    try:
        # Получаем текущий день учебы
        from utils.individual_plan_helpers import get_study_day
        study_day = get_study_day(current_user)
        
        # Получаем задачи для текущего дня учебы
        tasks = get_daily_tasks(current_user.id, study_day=study_day)
        
        return jsonify({
            'success': True,
            'tasks': tasks,
            'study_day': study_day
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

