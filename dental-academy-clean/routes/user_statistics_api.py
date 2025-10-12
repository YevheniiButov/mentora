# routes/user_statistics_api.py

from flask import Blueprint, jsonify, current_app
from flask_login import login_required, current_user
from extensions import db
from models import (
    UserProgress, DiagnosticSession, UserActivity, TestAttempt, 
    Module, Lesson
)
from datetime import datetime, timedelta

# Создаем Blueprint для статистики
statistics_bp = Blueprint(
    "statistics",
    __name__,
    url_prefix='/<string:lang>/api'
)


@statistics_bp.route('/user-statistics')
@login_required
def get_user_statistics():
    """
    API endpoint для получения реальной статистики пользователя
    """
    try:
        user_id = current_user.id
        
        # Получаем статистику по модулям и урокам
        total_lessons_completed = UserProgress.query.filter_by(
            user_id=user_id,
            is_completed=True
        ).count()
        
        # Получаем статистику по IRT тестированию
        irt_tests_completed = DiagnosticSession.query.filter_by(
            user_id=user_id,
            is_completed=True
        ).count()
        
        # Получаем средний балл по IRT тестам
        irt_sessions = DiagnosticSession.query.filter_by(
            user_id=user_id,
            is_completed=True
        ).all()
        
        avg_irt_score = 0
        if irt_sessions:
            scores = [session.estimated_ability for session in irt_sessions if session.estimated_ability is not None]
            if scores:
                # Конвертируем ability в проценты (примерно от -3 до +3 -> 0% до 100%)
                avg_irt_score = int(((sum(scores) / len(scores)) + 3) / 6 * 100)
        
        # Получаем статистику по времени обучения
        # Считаем общее время за последние 30 дней
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_activities = UserActivity.query.filter(
            UserActivity.user_id == user_id,
            UserActivity.date >= thirty_days_ago
        ).all()
        
        total_learning_time = 0
        for activity in recent_activities:
            if hasattr(activity, 'minutes_spent'):
                total_learning_time += activity.minutes_spent or 0
        
        # Конвертируем в часы
        total_hours = round(total_learning_time / 60, 1)
        
        # Получаем статистику по тестам (для среднего балла)
        test_attempts = TestAttempt.query.filter_by(user_id=user_id).all()
        avg_test_score = 0
        if test_attempts:
            scores = [attempt.score for attempt in test_attempts if attempt.score is not None]
            if scores:
                avg_test_score = int(sum(scores) / len(scores))
        
        # Комбинированный средний балл (IRT + обычные тесты)
        if avg_irt_score and avg_test_score:
            combined_avg_score = int((avg_irt_score + avg_test_score) / 2)
        elif avg_irt_score:
            combined_avg_score = avg_irt_score
        elif avg_test_score:
            combined_avg_score = avg_test_score
        else:
            combined_avg_score = 0
        
        # Считаем активные модули (начатые, но не завершенные)
        active_modules_count = db.session.query(Module.id).join(
            Lesson, Module.id == Lesson.module_id
        ).join(
            UserProgress, Lesson.id == UserProgress.lesson_id
        ).filter(
            UserProgress.user_id == user_id,
            UserProgress.is_started == True,
            UserProgress.is_completed == False
        ).distinct().count()
        
        # Считаем общее количество начатых уроков
        total_lessons_started = UserProgress.query.filter_by(
            user_id=user_id,
            is_started=True
        ).count()
        
        statistics = {
            'active_modules': active_modules_count,
            'total_lessons_completed': total_lessons_completed,
            'total_lessons_started': total_lessons_started,
            'total_learning_time': f'{total_hours}h' if total_hours > 0 else '0h',
            'total_learning_minutes': total_learning_time,
            'avg_score': combined_avg_score,
            'irt_tests_completed': irt_tests_completed,
            'avg_irt_score': avg_irt_score,
            'test_attempts': len(test_attempts),
            'avg_test_score': avg_test_score,
            'last_activity': datetime.utcnow().strftime('%Y-%m-%d') if recent_activities else None
        }
        
        return jsonify({
            'success': True,
            'statistics': statistics
        })
        
    except Exception as e:
        current_app.logger.error(f"Ошибка при получении статистики пользователя: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

