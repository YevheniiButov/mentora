# routes/admin/dashboard.py
# Главный дашборд единой админки

from flask import Blueprint, render_template, jsonify, current_app
from flask_login import current_user
from sqlalchemy import func
from datetime import datetime, timedelta

from models import db, User, LearningPath, Subject, Module, Lesson, UserProgress, AIConversation, VirtualPatientAttempt
from . import admin_required, admin_unified_bp

# Главный маршрут единой админки
@admin_unified_bp.route('/dashboard')
@admin_required()
def unified_dashboard(lang):
    """Главный дашборд единой админки"""
    
    # === ОБЩАЯ СТАТИСТИКА СИСТЕМЫ ===
    overview_stats = {
        # Контент
        'learning_paths': LearningPath.query.count(),
        'subjects': Subject.query.count(),
        'modules': Module.query.count(),
        'lessons': Lesson.query.count(),
        
        # Пользователи
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'premium_users': User.query.filter_by(has_subscription=True).count(),
        'admin_users': User.query.filter_by(role='admin').count(),
        
        # Активность
        'completed_lessons': UserProgress.query.filter_by(completed=True).count(),
        'total_study_time': db.session.query(func.sum(UserProgress.time_spent)).scalar() or 0,
        'ai_conversations': AIConversation.query.count(),
        'vp_attempts': VirtualPatientAttempt.query.count()
    }
    
    # === СТАТИСТИКА ЗА ПЕРИОД ===
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    period_stats = {
        'new_users_today': User.query.filter(func.date(User.created_at) == today).count(),
        'new_users_week': User.query.filter(User.created_at >= week_ago).count(),
        'new_users_month': User.query.filter(User.created_at >= month_ago).count(),
        
        'lessons_completed_today': UserProgress.query.filter(
            func.date(UserProgress.timestamp) == today,
            UserProgress.completed == True
        ).count(),
        'lessons_completed_week': UserProgress.query.filter(
            UserProgress.timestamp >= week_ago,
            UserProgress.completed == True
        ).count(),
        
        'ai_conversations_today': AIConversation.query.filter(
            func.date(AIConversation.created_at) == today
        ).count(),
        'ai_conversations_week': AIConversation.query.filter(
            AIConversation.created_at >= week_ago
        ).count()
    }
    
    # === ПОСЛЕДНЯЯ АКТИВНОСТЬ ===
    # Последние регистрации
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    # Последние завершенные уроки
    recent_completions = UserProgress.query.filter_by(completed=True).join(
        Lesson
    ).order_by(UserProgress.timestamp.desc()).limit(10).all()
    
    # Популярные модули за неделю
    popular_modules = db.session.query(
        Module.title,
        Module.id,
        func.count(UserProgress.id).label('activity_count')
    ).join(Lesson).join(UserProgress).filter(
        UserProgress.timestamp >= week_ago
    ).group_by(Module.id, Module.title).order_by(
        func.count(UserProgress.id).desc()
    ).limit(5).all()
    
    # === СОСТОЯНИЕ СИСТЕМЫ ===
    system_health = {
        'database_connected': True,  # Если мы здесь, то БД работает
        'upload_folder_accessible': check_upload_folder(),
        'recent_errors': get_recent_errors_count(),
        'memory_usage': get_memory_usage_info()
    }
    
    # === УВЕДОМЛЕНИЯ ДЛЯ АДМИНА ===
    admin_notifications = []
    
    # Проверяем модули без контента
    empty_modules = Module.query.outerjoin(Lesson).group_by(Module.id).having(
        func.count(Lesson.id) == 0
    ).count()
    if empty_modules > 0:
        admin_notifications.append({
            'type': 'warning',
            'title': 'Модули без контента',
            'message': f'{empty_modules} модулей не содержат уроков',
            'action_url': f'/{lang}/admin/content/modules',
            'action_text': 'Просмотреть'
        })
    
    # Проверяем неактивных пользователей
    inactive_users = User.query.filter(User.last_login == None).count()
    if inactive_users > 10:
        admin_notifications.append({
            'type': 'info',
            'title': 'Неактивные пользователи',
            'message': f'{inactive_users} пользователей никогда не входили в систему',
            'action_url': f'/{lang}/admin/users',
            'action_text': 'Просмотреть'
        })
    
    # Проверяем ошибки ИИ
    ai_errors_today = AIConversation.query.filter(
        func.date(AIConversation.created_at) == today,
        AIConversation.user_rating < 3
    ).count()
    if ai_errors_today > 5:
        admin_notifications.append({
            'type': 'danger',
            'title': 'Проблемы с ИИ',
            'message': f'{ai_errors_today} негативных оценок ИИ сегодня',
            'action_url': f'/{lang}/admin/analytics/ai',
            'action_text': 'Подробнее'
        })
    
    return render_template('admin/unified/dashboard.html',
                         overview_stats=overview_stats,
                         period_stats=period_stats,
                         recent_users=recent_users,
                         recent_completions=recent_completions,
                         popular_modules=popular_modules,
                         system_health=system_health,
                         admin_notifications=admin_notifications,
                         current_user_role=current_user.role)

def check_upload_folder():
    """Проверка доступности папки загрузок"""
    try:
        import os
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
        return os.path.exists(upload_folder) and os.access(upload_folder, os.W_OK)
    except:
        return False

def get_recent_errors_count():
    """Получение количества недавних ошибок из логов"""
    try:
        # Здесь можно реализовать парсинг логов или проверку таблицы ошибок
        return 0
    except:
        return 0

def get_memory_usage_info():
    """Получение информации об использовании памяти"""
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        return {
            'rss': memory_info.rss,
            'vms': memory_info.vms,
            'percent': process.memory_percent()
        }
    except:
        return {'rss': 0, 'vms': 0, 'percent': 0}

# === API ДЛЯ ДИНАМИЧЕСКИХ ДАННЫХ ДАШБОРДА ===

@admin_unified_bp.route('/api/dashboard/stats')
@admin_required()
def dashboard_stats_api(lang):
    """API для получения свежих статистик дашборда"""
    try:
        # Быстрые статистики для обновления через AJAX
        quick_stats = {
            'online_users': get_online_users_count(),
            'active_sessions': get_active_sessions_count(),
            'current_load': get_current_system_load(),
            'last_activity': get_last_activity_timestamp()
        }
        
        return jsonify({
            'success': True,
            'stats': quick_stats,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting dashboard stats: {e}")
        return jsonify({'success': False, 'message': str(e)})

def get_online_users_count():
    """Получение количества онлайн пользователей"""
    # Пользователи, которые были активны в последние 15 минут
    cutoff = datetime.now() - timedelta(minutes=15)
    return User.query.filter(User.last_login >= cutoff).count()

def get_active_sessions_count():
    """Получение количества активных сессий"""
    # Здесь можно подключиться к системе сессий Flask/Redis
    return 0

def get_current_system_load():
    """Получение текущей нагрузки системы"""
    try:
        import psutil
        return {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_percent': psutil.disk_usage('/').percent
        }
    except:
        return {'cpu_percent': 0, 'memory_percent': 0, 'disk_percent': 0}

def get_last_activity_timestamp():
    """Получение времени последней активности в системе"""
    last_progress = UserProgress.query.order_by(UserProgress.timestamp.desc()).first()
    last_ai_conversation = AIConversation.query.order_by(AIConversation.created_at.desc()).first()
    
    timestamps = []
    if last_progress:
        timestamps.append(last_progress.timestamp)
    if last_ai_conversation:
        timestamps.append(last_ai_conversation.created_at)
    
    if timestamps:
        return max(timestamps).isoformat()
    return None 