# routes/user_statistics_api.py

from flask import Blueprint, jsonify, current_app
from flask_login import login_required, current_user
from extensions import db
from models import UserProgress, DiagnosticSession, UserActivity, TestAttempt
from datetime import datetime, timedelta, timezone

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
        current_app.logger.info(f"Fetching statistics for user {user_id}")
        
        # 1. Получаем статистику по урокам
        total_lessons_completed = UserProgress.query.filter_by(
            user_id=user_id,
            completed=True
        ).count()
        
        total_lessons_started = UserProgress.query.filter_by(
            user_id=user_id
        ).count()
        
        # 2. Получаем статистику по IRT тестированию
        irt_tests_completed = DiagnosticSession.query.filter_by(
            user_id=user_id,
            status='completed'
        ).count()
        
        # Получаем средний балл по IRT тестам
        irt_sessions = DiagnosticSession.query.filter_by(
            user_id=user_id,
            status='completed'
        ).all()
        
        avg_irt_score = 0
        if irt_sessions:
            scores = [session.user_ability for session in irt_sessions if session.user_ability is not None]
            if scores:
                # Конвертируем ability в проценты (примерно от -3 до +3 -> 0% до 100%)
                avg_irt_score = int(((sum(scores) / len(scores)) + 3) / 6 * 100)
        
        # 3. Получаем статистику по времени обучения (последние 30 дней)
        thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
        
        # Суммируем время из UserActivity
        total_learning_seconds = db.session.query(
            db.func.sum(UserActivity.time_spent_seconds)
        ).filter(
            UserActivity.user_id == user_id,
            UserActivity.activity_date >= thirty_days_ago.date()
        ).scalar() or 0
        
        # Конвертируем в часы
        total_hours = round(total_learning_seconds / 3600, 1)
        
        # 4. Получаем статистику по тестам (для среднего балла)
        test_attempts = TestAttempt.query.filter_by(
            user_id=user_id,
            status='completed'
        ).all()
        
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
        
        # 5. Считаем активные модули (начатые уроки)
        active_modules_count = total_lessons_started
        
        # 6. Получаем последнюю активность
        last_activity = UserActivity.query.filter_by(
            user_id=user_id
        ).order_by(UserActivity.activity_date.desc()).first()
        
        statistics = {
            'active_modules': active_modules_count,
            'total_lessons_completed': total_lessons_completed,
            'total_lessons_started': total_lessons_started,
            'total_learning_time': f'{total_hours}h' if total_hours > 0 else '0h',
            'total_learning_seconds': total_learning_seconds,
            'avg_score': combined_avg_score,
            'irt_tests_completed': irt_tests_completed,
            'avg_irt_score': avg_irt_score,
            'test_attempts': len(test_attempts),
            'avg_test_score': avg_test_score,
            'last_activity': last_activity.activity_date.strftime('%Y-%m-%d') if last_activity else None
        }
        
        current_app.logger.info(f"Statistics for user {user_id}: {statistics}")
        
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

