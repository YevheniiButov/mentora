# routes/virtual_patient_api.py
"""
API endpoints для расширенной функциональности виртуальных пациентов
"""

from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from models import db, VirtualPatientScenario, VirtualPatientAttempt, Achievement, UserStats
from utils.gamification_engine import GamificationEngine
from utils.adaptive_learning import AdaptiveLearningService
from utils.virtual_patient_analytics import register_analytics_filters
import json
from datetime import datetime, timedelta

virtual_patient_api_bp = Blueprint(
    "virtual_patient_api_bp",
    __name__,
    url_prefix='/<string:lang>/virtual-patient/api'
)

@virtual_patient_api_bp.context_processor
def inject_lang():
    return dict(lang=g.lang)

# ============ ГЕЙМИФИКАЦИЯ API ============

@virtual_patient_api_bp.route("/leaderboard/<category>")
@login_required
def get_leaderboard(lang, category):
    """Получает таблицу лидеров по категории"""
    try:
        gamification = GamificationEngine(db.session)
        
        # Определяем метрику на основе категории
        if category == 'weekly':
            metric_type = 'total_score'
        elif category == 'monthly':
            metric_type = 'scenarios_completed'
        else:  # all_time
            metric_type = 'total_experience'
        
        leaderboard = gamification.get_leaderboard(category, metric_type, limit=20)
        user_position = gamification.get_user_leaderboard_position(current_user.id, category, metric_type)
        
        return jsonify({
            'status': 'success',
            'leaderboard': leaderboard,
            'user_position': user_position
        })
    except Exception as e:
        current_app.logger.error(f"Error getting leaderboard: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@virtual_patient_api_bp.route("/achievement/<int:achievement_id>")
@login_required
def get_achievement_details(lang, achievement_id):
    """Получает детали достижения"""
    try:
        achievement = Achievement.query.get_or_404(achievement_id)
        
        return jsonify({
            'status': 'success',
            'achievement': {
                'id': achievement.id,
                'name': achievement.name,
                'description': achievement.description,
                'icon': achievement.icon,
                'type': achievement.type,
                'rarity': achievement.rarity,
                'points': achievement.points
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@virtual_patient_api_bp.route("/user-stats")
@login_required
def get_user_stats(lang):
    """Получает статистику пользователя"""
    try:
        gamification = GamificationEngine(db.session)
        stats = gamification.get_or_create_user_stats(current_user.id)
        achievements_summary = gamification.get_user_achievements_summary(current_user.id)
        
        return jsonify({
            'status': 'success',
            'stats': {
                'total_scenarios_completed': stats.total_scenarios_completed,
                'total_score_earned': stats.total_score_earned,
                'average_score_percentage': round(stats.average_score_percentage, 1),
                'current_streak_days': stats.current_streak_days,
                'longest_streak_days': stats.longest_streak_days,
                'total_experience_points': stats.total_experience_points,
                'current_level': stats.current_level,
                'points_to_next_level': stats.points_to_next_level
            },
            'achievements_summary': achievements_summary
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============ АДАПТИВНОЕ ОБУЧЕНИЕ API ============

@virtual_patient_api_bp.route("/recommendations")
@login_required
def get_scenario_recommendations(lang):
    """Получает рекомендации сценариев для пользователя"""
    try:
        adaptive_service = AdaptiveLearningService(db.session)
        
        # Получаем доступные сценарии
        available_scenarios = VirtualPatientScenario.query.filter_by(is_published=True).all()
        
        recommendations = adaptive_service.get_scenario_recommendations(
            current_user.id, 
            available_scenarios
        )
        
        # Преобразуем в JSON-совместимый формат
        formatted_recommendations = []
        for rec in recommendations:
            scenario = rec['scenario']
            formatted_recommendations.append({
                'scenario_id': scenario['id'],
                'title': scenario['title'],
                'relevance_score': rec['relevance_score'],
                'reason': rec['recommendation_reason'],
                'difficulty': scenario.get('difficulty', 'medium')
            })
        
        return jsonify({
            'status': 'success',
            'recommendations': formatted_recommendations
        })
    except Exception as e:
        current_app.logger.error(f"Error getting recommendations: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@virtual_patient_api_bp.route("/hints")
@login_required
def get_personalized_hints(lang):
    """Получает персонализированные подсказки"""
    try:
        current_node = request.json.get('current_node', {})
        scenario_context = request.json.get('scenario_context', {})
        
        adaptive_service = AdaptiveLearningService(db.session)
        hints = adaptive_service.get_personalized_hints(
            current_user.id, 
            current_node, 
            scenario_context
        )
        
        return jsonify({
            'status': 'success',
            'hints': hints
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============ АНАЛИТИКА API ============

@virtual_patient_api_bp.route("/analytics/performance")
@login_required
def get_performance_analytics(lang):
    """Получает аналитику производительности пользователя"""
    try:
        # Получаем последние попытки пользователя
        recent_attempts = VirtualPatientAttempt.query.filter_by(
            user_id=current_user.id,
            completed=True
        ).order_by(VirtualPatientAttempt.completed_at.desc()).limit(20).all()
        
        if not recent_attempts:
            return jsonify({
                'status': 'success',
                'analytics': {
                    'performance_trend': [],
                    'skill_breakdown': {},
                    'improvement_areas': [],
                    'strengths': []
                }
            })
        
        # Подготавливаем данные для анализа
        attempts_data = []
        for attempt in recent_attempts:
            attempts_data.append({
                'score': attempt.score,
                'max_score': attempt.scenario.max_score,
                'dialogue_history': attempt.dialogue_history,
                'completed_at': attempt.completed_at.isoformat(),
                'time_spent': attempt.time_spent
            })
        
        # Импортируем функции аналитики
        from utils.virtual_patient_analytics import (
            calculate_empathy_score, calculate_clinical_score, 
            calculate_communication_score, generate_recommendations
        )
        
        # Рассчитываем метрики
        analytics = {
            'performance_trend': [
                {
                    'date': attempt['completed_at'],
                    'score_percentage': (attempt['score'] / attempt['max_score']) * 100
                }
                for attempt in attempts_data
            ],
            'skill_breakdown': {
                'empathy': calculate_empathy_score({'decisions': []}),  # Упрощено для примера
                'clinical': calculate_clinical_score({'decisions': []}),
                'communication': calculate_communication_score({'decisions': []})
            },
            'total_scenarios': len(attempts_data),
            'average_score': sum(a['score'] for a in attempts_data) / len(attempts_data),
            'average_time': sum(a.get('time_spent', 0) for a in attempts_data) / len(attempts_data)
        }
        
        return jsonify({
            'status': 'success',
            'analytics': analytics
        })
    except Exception as e:
        current_app.logger.error(f"Error getting analytics: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============ СЦЕНАРИИ API ============

@virtual_patient_api_bp.route("/scenario/<int:scenario_id>/analytics")
@login_required
def get_scenario_analytics(lang, scenario_id):
    """Получает аналитику по конкретному сценарию"""
    try:
        scenario = VirtualPatientScenario.query.get_or_404(scenario_id)
        
        # Получаем все попытки пользователя для этого сценария
        user_attempts = VirtualPatientAttempt.query.filter_by(
            user_id=current_user.id,
            scenario_id=scenario_id,
            completed=True
        ).order_by(VirtualPatientAttempt.completed_at.desc()).all()
        
        # Получаем общую статистику по сценарию
        all_attempts = VirtualPatientAttempt.query.filter_by(
            scenario_id=scenario_id,
            completed=True
        ).all()
        
        analytics = {
            'user_attempts': len(user_attempts),
            'best_score': max((a.score for a in user_attempts), default=0),
            'average_score': sum(a.score for a in user_attempts) / len(user_attempts) if user_attempts else 0,
            'completion_rate': len([a for a in user_attempts if a.score > 0]) / len(user_attempts) if user_attempts else 0,
            'global_stats': {
                'total_attempts': len(all_attempts),
                'average_global_score': sum(a.score for a in all_attempts) / len(all_attempts) if all_attempts else 0,
                'completion_rate': len([a for a in all_attempts if a.score > 0]) / len(all_attempts) if all_attempts else 0
            }
        }
        
        return jsonify({
            'status': 'success',
            'analytics': analytics
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============ ПРОГРЕСС API ============

@virtual_patient_api_bp.route("/progress/sync", methods=['POST'])
@login_required
def sync_progress(lang):
    """Синхронизирует прогресс пользователя"""
    try:
        data = request.json
        attempt_id = data.get('attempt_id')
        progress_data = data.get('progress_data', {})
        
        attempt = VirtualPatientAttempt.query.get_or_404(attempt_id)
        if attempt.user_id != current_user.id:
            return jsonify({'status': 'error', 'message': 'Access denied'}), 403
        
        # Обновляем прогресс
        if 'decision_times' in progress_data:
            history = json.loads(attempt.dialogue_history) if attempt.dialogue_history else {}
            history['decision_times'] = progress_data['decision_times']
            attempt.dialogue_history = json.dumps(history)
        
        if 'interaction_data' in progress_data:
            # Сохраняем дополнительные данные взаимодействия
            history = json.loads(attempt.dialogue_history) if attempt.dialogue_history else {}
            history['interaction_data'] = progress_data['interaction_data']
            attempt.dialogue_history = json.dumps(history)
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Progress synced successfully'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============ ОБРАТНАЯ СВЯЗЬ API ============

@virtual_patient_api_bp.route("/feedback", methods=['POST'])
@login_required
def submit_feedback(lang):
    """Принимает обратную связь по сценарию"""
    try:
        data = request.json
        scenario_id = data.get('scenario_id')
        rating = data.get('rating')  # 1-5
        feedback_text = data.get('feedback_text', '')
        feedback_type = data.get('type', 'general')  # general, bug, suggestion
        
        # Здесь можно сохранить обратную связь в отдельную таблицу
        # или отправить на email администраторов
        
        current_app.logger.info(f"Feedback received from user {current_user.id} for scenario {scenario_id}: {rating}/5 - {feedback_text}")
        
        return jsonify({
            'status': 'success',
            'message': 'Feedback submitted successfully'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============ ЭКСПОРТ DATA API ============

@virtual_patient_api_bp.route("/export/progress")
@login_required
def export_user_progress(lang):
    """Экспортирует прогресс пользователя в JSON"""
    try:
        # Получаем все попытки пользователя
        attempts = VirtualPatientAttempt.query.filter_by(
            user_id=current_user.id,
            completed=True
        ).all()
        
        # Получаем статистику
        gamification = GamificationEngine(db.session)
        stats = gamification.get_or_create_user_stats(current_user.id)
        achievements_summary = gamification.get_user_achievements_summary(current_user.id)
        
        export_data = {
            'user_id': current_user.id,
            'export_date': datetime.utcnow().isoformat(),
            'statistics': {
                'total_scenarios_completed': stats.total_scenarios_completed,
                'total_score_earned': stats.total_score_earned,
                'average_score_percentage': stats.average_score_percentage,
                'current_streak_days': stats.current_streak_days,
                'longest_streak_days': stats.longest_streak_days,
                'total_experience_points': stats.total_experience_points,
                'current_level': stats.current_level
            },
            'achievements': achievements_summary,
            'scenario_attempts': [
                {
                    'scenario_id': attempt.scenario_id,
                    'scenario_title': attempt.scenario.title,
                    'score': attempt.score,
                    'max_score': attempt.scenario.max_score,
                    'completion_date': attempt.completed_at.isoformat(),
                    'time_spent': attempt.time_spent
                }
                for attempt in attempts
            ]
        }
        
        return jsonify({
            'status': 'success',
            'data': export_data
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============ СИСТЕМА УВЕДОМЛЕНИЙ API ============

@virtual_patient_api_bp.route("/notifications")
@login_required
def get_notifications(lang):
    """Получает уведомления для пользователя"""
    try:
        notifications = []
        
        # Проверяем достижения
        gamification = GamificationEngine(db.session)
        stats = gamification.get_or_create_user_stats(current_user.id)
        
        # Уведомление о прерванной серии
        if stats.last_activity_date:
            days_since_activity = (datetime.utcnow() - stats.last_activity_date).days
            if days_since_activity > 1:
                notifications.append({
                    'type': 'streak_broken',
                    'title': 'Серия прервана',
                    'message': f'Ваша серия была прервана {days_since_activity} дней назад. Начните новую!',
                    'priority': 'medium',
                    'action_url': url_for('virtual_patient_bp.scenarios_list', lang=lang)
                })
        
        # Уведомление о рекомендуемых сценариях
        adaptive_service = AdaptiveLearningService(db.session)
        available_scenarios = VirtualPatientScenario.query.filter_by(is_published=True).limit(5).all()
        recommendations = adaptive_service.get_scenario_recommendations(current_user.id, available_scenarios)
        
        if recommendations:
            top_recommendation = recommendations[0]
            notifications.append({
                'type': 'recommendation',
                'title': 'Рекомендуемый сценарий',
                'message': f'Попробуйте сценарий "{top_recommendation["scenario"]["title"]}" - {top_recommendation["recommendation_reason"]}',
                'priority': 'low',
                'action_url': url_for('virtual_patient_bp.start_scenario', lang=lang, scenario_id=top_recommendation["scenario"]["id"])
            })
        
        return jsonify({
            'status': 'success',
            'notifications': notifications
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============ МОБИЛЬНЫЕ API ============

@virtual_patient_api_bp.route("/mobile/sync", methods=['POST'])
@login_required
def mobile_sync(lang):
    """Синхронизация данных для мобильного приложения"""
    try:
        data = request.json
        device_info = data.get('device_info', {})
        
        # Получаем основные данные пользователя
        gamification = GamificationEngine(db.session)
        stats = gamification.get_or_create_user_stats(current_user.id)
        
        # Получаем последние сценарии
        recent_scenarios = VirtualPatientScenario.query.filter_by(
            is_published=True
        ).order_by(VirtualPatientScenario.id.desc()).limit(10).all()
        
        sync_data = {
            'user_stats': {
                'level': stats.current_level,
                'experience': stats.total_experience_points,
                'scenarios_completed': stats.total_scenarios_completed
            },
            'available_scenarios': [
                {
                    'id': s.id,
                    'title': s.title,
                    'difficulty': s.difficulty,
                    'is_premium': s.is_premium
                }
                for s in recent_scenarios
            ],
            'sync_timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'status': 'success',
            'data': sync_data
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ============ ОБРАБОТКА ОШИБОК ============

@virtual_patient_api_bp.errorhandler(404)
def api_not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'API endpoint not found'
    }), 404

@virtual_patient_api_bp.errorhandler(500)
def api_internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error'
    }), 500