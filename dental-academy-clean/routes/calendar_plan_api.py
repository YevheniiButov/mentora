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

@calendar_plan_bp.route('/upcoming-plans', methods=['GET'])
@login_required
def get_upcoming_plans():
    """
    Получить планы с ротацией задач на ближайшие 14 дней учебы.
    
    Query parameters:
    - days: Количество дней (по умолчанию 14)
    
    Returns:
    - JSON с планами по дням учебы (День 1, День 2, ... День 14)
    """
    try:
        from routes.learning import get_daily_tasks
        from utils.individual_plan_helpers import get_study_day, update_study_day_count
        
        days = request.args.get('days', 28, type=int)
        days = min(days, 28)  # Максимум 28 дней (2 недели)
        
        # Получаем текущий день учебы
        study_day_info = update_study_day_count(current_user)
        current_study_day = study_day_info['study_day']
        
        # Проверяем, прошел ли пользователь BIG test (14-й день)
        # Если study_day > 14, значит BIG test пройден
        big_test_completed = current_study_day > 14
        
        plans = {}
        
        # Генерируем планы для всех 28 дней
        for day_num in range(1, 29):  # Дни 1-28
            # Определяем, заблокирован ли день
            is_locked = day_num > 14 and not big_test_completed
            
            # Для заблокированных дней не генерируем задачи
            if is_locked:
                plans[f'day_{day_num}'] = {
                    'study_day': day_num,
                    'cycle_day': 0,
                    'is_big_test_day': day_num == 14 or day_num == 28,  # BIG test на 14 и 28 день
                    'tasks': [],
                    'total_tasks': 0,
                    'intensity': 'locked',
                    'is_today': day_num == current_study_day,
                    'is_past': False,
                    'is_locked': True
                }
            else:
                # Для активных дней генерируем задачи
                # Если день > 14, используем цикл (день 15 = день 1, день 16 = день 2, и т.д.)
                effective_day = day_num if day_num <= 14 else ((day_num - 15) % 14) + 1
                
                # Получаем задачи для этого дня учебы
                tasks_data = get_daily_tasks(current_user.id, study_day=effective_day)
                
                # Определяем интенсивность дня
                intensity = 'medium'
                if day_num == 14 or day_num == 28:
                    intensity = 'high'  # BIG test
                elif tasks_data.get('cycle_day') in [3, 6]:  # Интенсивные дни
                    intensity = 'high'
                elif len(tasks_data.get('tasks', [])) == 2:  # Меньше задач
                    intensity = 'light'
                
                plans[f'day_{day_num}'] = {
                    'study_day': day_num,
                    'cycle_day': tasks_data.get('cycle_day', 1),
                    'is_big_test_day': day_num == 14 or day_num == 28,  # BIG test на 14 и 28 день
                    'tasks': tasks_data.get('tasks', []),
                    'total_tasks': len(tasks_data.get('tasks', [])),
                    'intensity': intensity,
                    'is_today': day_num == current_study_day,
                    'is_past': False,
                    'is_locked': False
                }
        
        return jsonify({
            'success': True,
            'plans': plans,
            'current_study_day': current_study_day,
            'total_days': 28,
            'big_test_completed': big_test_completed,
            'first_successful_day': study_day_info.get('first_successful_day').isoformat() if study_day_info.get('first_successful_day') else None
        })
        
    except Exception as e:
        logger.error(f"Error getting upcoming plans for user {current_user.id}: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': 'Внутренняя ошибка сервера',
            'message': str(e)
        }), 500 