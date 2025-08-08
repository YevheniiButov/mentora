"""
API роуты для интеграции планов обучения с календарем
Безопасная интеграция без изменения существующих роутов
"""

from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from utils.calendar_plan_integration import CalendarPlanIntegration
import logging

logger = logging.getLogger(__name__)

# Создаем новый blueprint для API планов
calendar_plan_bp = Blueprint('calendar_plan_api', __name__, url_prefix='/api/calendar-plan')

@calendar_plan_bp.route('/detailed-plan', methods=['GET'])
@login_required
def get_detailed_plan():
    """
    Получить детальный план обучения для календаря
    
    Query parameters:
    - target_minutes: Целевое время в минутах (по умолчанию 30)
    
    Returns:
    - JSON с детальным планом
    """
    try:
        target_minutes = request.args.get('target_minutes', 30, type=int)
        
        integration = CalendarPlanIntegration()
        plan_result = integration.get_detailed_plan_for_calendar(
            current_user.id, 
            target_minutes
        )
        
        if not plan_result.get('success'):
            return jsonify({
                'success': False,
                'error': plan_result.get('error'),
                'requires_diagnostic': plan_result.get('requires_diagnostic', False)
            }), 400
        
        return jsonify({
            'success': True,
            'plan': plan_result.get('plan'),
            'generated_at': plan_result.get('generated_at'),
            'total_time': plan_result.get('total_time')
        })
        
    except Exception as e:
        logger.error(f"Error getting detailed plan for user {current_user.id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Внутренняя ошибка сервера',
            'requires_diagnostic': True
        }), 500

@calendar_plan_bp.route('/study-sessions', methods=['GET'])
@login_required
def get_study_sessions():
    """
    Получить сессии обучения для календаря
    
    Query parameters:
    - days: Количество дней назад (по умолчанию 7)
    
    Returns:
    - JSON со списком сессий
    """
    try:
        days = request.args.get('days', 7, type=int)
        
        integration = CalendarPlanIntegration()
        sessions = integration.get_user_study_sessions(current_user.id, days)
        
        return jsonify({
            'success': True,
            'sessions': sessions,
            'total_sessions': len(sessions)
        })
        
    except Exception as e:
        logger.error(f"Error getting study sessions for user {current_user.id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Внутренняя ошибка сервера'
        }), 500

@calendar_plan_bp.route('/statistics', methods=['GET'])
@login_required
def get_plan_statistics():
    """
    Получить статистику плана обучения
    
    Returns:
    - JSON со статистикой
    """
    try:
        integration = CalendarPlanIntegration()
        stats = integration.get_plan_statistics(current_user.id)
        
        if not stats.get('success'):
            return jsonify({
                'success': False,
                'error': stats.get('error')
            }), 400
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting plan statistics for user {current_user.id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Внутренняя ошибка сервера'
        }), 500

@calendar_plan_bp.route('/generate-plan', methods=['POST'])
@login_required
def generate_new_plan():
    """
    Сгенерировать новый план обучения
    
    JSON body:
    - target_minutes: Целевое время в минутах
    
    Returns:
    - JSON с новым планом
    """
    try:
        data = request.get_json() or {}
        target_minutes = data.get('target_minutes', 30)
        
        integration = CalendarPlanIntegration()
        plan_result = integration.get_detailed_plan_for_calendar(
            current_user.id, 
            target_minutes
        )
        
        if not plan_result.get('success'):
            return jsonify({
                'success': False,
                'error': plan_result.get('error'),
                'requires_diagnostic': plan_result.get('requires_diagnostic', False)
            }), 400
        
        return jsonify({
            'success': True,
            'plan': plan_result.get('plan'),
            'generated_at': plan_result.get('generated_at'),
            'total_time': plan_result.get('total_time'),
            'message': 'Новый план успешно сгенерирован'
        })
        
    except Exception as e:
        logger.error(f"Error generating new plan for user {current_user.id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Внутренняя ошибка сервера'
        }), 500

@calendar_plan_bp.route('/health', methods=['GET'])
@login_required
def health_check():
    """
    Проверка работоспособности API планов
    
    Returns:
    - JSON с статусом
    """
    try:
        integration = CalendarPlanIntegration()
        
        # Проверяем базовую функциональность
        stats = integration.get_plan_statistics(current_user.id)
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'user_id': current_user.id,
            'has_plan': stats.get('success', False),
            'message': 'API планов работает корректно'
        })
        
    except Exception as e:
        logger.error(f"Health check failed for user {current_user.id}: {str(e)}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e)
        }), 500 