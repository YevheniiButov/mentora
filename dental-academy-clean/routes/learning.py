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


def get_daily_tasks(user_id):
    """Generate daily tasks based on rotation schedule"""
    user = User.query.get(user_id)
    if not user:
        return {'error': 'User not found'}
    
    today = datetime.now(timezone.utc).date()
    
    # Calculate day number since user registration
    if user.created_at:
        user_created_date = user.created_at.date() if isinstance(user.created_at, datetime) else user.created_at
        days_since_start = (today - user_created_date).days
    else:
        days_since_start = 0
    
    cycle_day = (days_since_start % 3) + 1  # 1, 2, or 3
    
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
    
    tasks = {
        'cycle_day': cycle_day,
        'tasks': []
    }
    
    if cycle_day in [1, 2]:
        # Regular day: Tests + Flashcards + VP
        tasks['tasks'] = [
            {
                'type': 'diagnostic_test',
                'title': 'Diagnostische Test',
                'target': 10,
                'icon': 'clipboard-check',
                'completed': tests_completed > 0,
                'progress': min(tests_completed, 10)
            },
            {
                'type': 'flashcards',
                'title': 'Medische Termen',
                'target': 20,
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
    else:  # cycle_day == 3
        # Intensive day: More tests + English
        tasks['tasks'] = [
            {
                'type': 'diagnostic_test',
                'title': 'Diagnostische Test (Intensief)',
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
    
    # Calculate daily progress
    completed_count = sum(1 for task in tasks['tasks'] if task['completed'])
    total_count = len(tasks['tasks'])
    tasks['progress'] = int((completed_count / total_count) * 100) if total_count > 0 else 0
    
    return tasks


@daily_tasks_bp.route('/daily-tasks', methods=['GET'])
@login_required
def api_daily_tasks():
    """API endpoint for daily tasks"""
    try:
        tasks = get_daily_tasks(current_user.id)
        return jsonify(tasks)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

