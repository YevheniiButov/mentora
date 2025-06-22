# routes/admin/analytics_admin.py
# Аналитика и отчеты

from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import current_user
from sqlalchemy import func, desc, extract
from datetime import datetime, timedelta
import json

from models import db, User, UserProgress, Lesson, Module, Subject, LearningPath, AIConversation, VirtualPatientAttempt
from . import admin_required

# Создаем blueprint для аналитики
analytics_admin_bp = Blueprint('analytics_admin', __name__, url_prefix='/analytics')

# ================== ANALYTICS DASHBOARD ==================

@analytics_admin_bp.route('/dashboard')
@admin_required(['analytics'])
def analytics_dashboard(lang):
    """Главный дашборд аналитики"""
    
    # Общая статистика системы
    overview_stats = {
        'total_users': User.query.count(),
        'active_users_week': User.query.filter(
            User.last_login >= datetime.now() - timedelta(days=7)
        ).count(),
        'total_lessons': Lesson.query.count(),
        'completed_lessons': UserProgress.query.filter_by(completed=True).count(),
        'total_study_time': db.session.query(func.sum(UserProgress.time_spent)).scalar() or 0,
        'ai_conversations_today': AIConversation.query.filter(
            func.date(AIConversation.created_at) == datetime.now().date()
        ).count()
    }
    
    # Статистика за последние 30 дней
    daily_activity = []
    for i in range(30):
        date = datetime.now().date() - timedelta(days=i)
        
        active_users = User.query.filter(func.date(User.last_login) == date).count()
        new_registrations = User.query.filter(func.date(User.created_at) == date).count()
        lessons_completed = UserProgress.query.filter(
            func.date(UserProgress.timestamp) == date,
            UserProgress.completed == True
        ).count()
        
        daily_activity.append({
            'date': date.strftime('%Y-%m-%d'),
            'active_users': active_users,
            'new_registrations': new_registrations,
            'lessons_completed': lessons_completed
        })
    
    daily_activity.reverse()  # Хронологический порядок
    
    return render_template('admin/unified/analytics/dashboard.html',
                         overview_stats=overview_stats,
                         daily_activity=daily_activity)

# ================== LEARNING ANALYTICS ==================

@analytics_admin_bp.route('/learning')
@admin_required(['analytics'])
def learning_analytics(lang):
    """Аналитика обучения"""
    
    # Популярные модули
    popular_modules = db.session.query(
        Module.title,
        Module.id,
        func.count(UserProgress.id).label('attempts'),
        func.avg(UserProgress.time_spent).label('avg_time')
    ).join(Lesson).join(UserProgress).group_by(Module.id, Module.title).order_by(
        desc('attempts')
    ).limit(20).all()
    
    # Статистика завершения по предметам
    subject_completion = db.session.query(
        Subject.name,
        func.count(UserProgress.id).label('total_attempts'),
        func.sum(func.case([(UserProgress.completed == True, 1)], else_=0)).label('completed'),
        func.avg(UserProgress.time_spent).label('avg_time')
    ).join(Module).join(Lesson).join(UserProgress).group_by(Subject.id, Subject.name).all()
    
    # Статистика по времени суток
    hourly_activity = db.session.query(
        extract('hour', UserProgress.timestamp).label('hour'),
        func.count(UserProgress.id).label('activity_count')
    ).filter(UserProgress.timestamp >= datetime.now() - timedelta(days=30)).group_by('hour').all()
    
    # Конверсия по этапам обучения
    learning_funnel = []
    for path in LearningPath.query.all():
        total_users = User.query.count()
        started_path = db.session.query(func.count(func.distinct(UserProgress.user_id))).join(
            Lesson
        ).join(Module).join(Subject).filter(Subject.learning_path_id == path.id).scalar()
        
        learning_funnel.append({
            'path_name': path.name,
            'total_users': total_users,
            'started': started_path or 0,
            'conversion_rate': round((started_path or 0) / total_users * 100, 2) if total_users > 0 else 0
        })
    
    return render_template('admin/unified/analytics/learning.html',
                         popular_modules=popular_modules,
                         subject_completion=subject_completion,
                         hourly_activity=hourly_activity,
                         learning_funnel=learning_funnel)

# ================== AI ANALYTICS ==================

@analytics_admin_bp.route('/ai')
@admin_required(['analytics'])
def ai_analytics(lang):
    """Аналитика ИИ системы"""
    
    # Общая статистика ИИ
    ai_stats = {
        'total_conversations': AIConversation.query.count(),
        'conversations_today': AIConversation.query.filter(
            func.date(AIConversation.created_at) == datetime.now().date()
        ).count(),
        'total_tokens_used': db.session.query(func.sum(AIConversation.tokens_used)).scalar() or 0,
        'avg_response_time': db.session.query(func.avg(AIConversation.response_time_ms)).scalar() or 0,
        'user_satisfaction': db.session.query(func.avg(AIConversation.user_rating)).filter(
            AIConversation.user_rating.isnot(None)
        ).scalar() or 0
    }
    
    # Использование по провайдерам
    provider_stats = db.session.query(
        AIConversation.provider,
        func.count(AIConversation.id).label('usage_count'),
        func.sum(AIConversation.tokens_used).label('total_tokens'),
        func.avg(AIConversation.response_time_ms).label('avg_response_time')
    ).group_by(AIConversation.provider).all()
    
    # Активность ИИ по дням
    ai_daily_activity = []
    for i in range(14):  # Последние 2 недели
        date = datetime.now().date() - timedelta(days=i)
        conversations = AIConversation.query.filter(func.date(AIConversation.created_at) == date).count()
        tokens = db.session.query(func.sum(AIConversation.tokens_used)).filter(
            func.date(AIConversation.created_at) == date
        ).scalar() or 0
        
        ai_daily_activity.append({
            'date': date.strftime('%Y-%m-%d'),
            'conversations': conversations,
            'tokens': tokens
        })
    
    ai_daily_activity.reverse()
    
    # Топ пользователей ИИ
    top_ai_users = db.session.query(
        User.name,
        User.email,
        func.count(AIConversation.id).label('conversation_count'),
        func.sum(AIConversation.tokens_used).label('tokens_used')
    ).join(AIConversation).group_by(User.id, User.name, User.email).order_by(
        desc('conversation_count')
    ).limit(10).all()
    
    return render_template('admin/unified/analytics/ai.html',
                         ai_stats=ai_stats,
                         provider_stats=provider_stats,
                         ai_daily_activity=ai_daily_activity,
                         top_ai_users=top_ai_users)

# ================== VIRTUAL PATIENTS ANALYTICS ==================

@analytics_admin_bp.route('/virtual-patients')
@admin_required(['analytics'])
def virtual_patients_analytics(lang):
    """Аналитика виртуальных пациентов"""
    
    # Общая статистика VP
    vp_stats = {
        'total_attempts': VirtualPatientAttempt.query.count(),
        'completed_attempts': VirtualPatientAttempt.query.filter_by(completed=True).count(),
        'avg_score': db.session.query(func.avg(VirtualPatientAttempt.score)).scalar() or 0,
        'avg_completion_time': db.session.query(func.avg(VirtualPatientAttempt.time_spent)).filter(
            VirtualPatientAttempt.completed == True
        ).scalar() or 0
    }
    
    # Популярные сценарии
    popular_scenarios = db.session.query(
        VirtualPatientAttempt.scenario_id,
        func.count(VirtualPatientAttempt.id).label('attempt_count'),
        func.avg(VirtualPatientAttempt.score).label('avg_score'),
        func.avg(VirtualPatientAttempt.time_spent).label('avg_time')
    ).group_by(VirtualPatientAttempt.scenario_id).order_by(desc('attempt_count')).limit(10).all()
    
    # Распределение оценок
    score_distribution = db.session.query(
        func.floor(VirtualPatientAttempt.score / 10) * 10,
        func.count(VirtualPatientAttempt.id)
    ).group_by(func.floor(VirtualPatientAttempt.score / 10)).all()
    
    return render_template('admin/unified/analytics/virtual_patients.html',
                         vp_stats=vp_stats,
                         popular_scenarios=popular_scenarios,
                         score_distribution=score_distribution)

# ================== REPORTS ==================

@analytics_admin_bp.route('/reports')
@admin_required(['analytics'])
def reports_list(lang):
    """Список доступных отчетов"""
    
    available_reports = [
        {
            'id': 'user_activity',
            'name': 'Активность пользователей',
            'description': 'Детальный отчет по активности пользователей',
            'format': ['csv', 'json']
        },
        {
            'id': 'learning_progress',
            'name': 'Прогресс обучения',
            'description': 'Статистика завершения уроков и модулей',
            'format': ['csv', 'json']
        },
        {
            'id': 'ai_usage',
            'name': 'Использование ИИ',
            'description': 'Статистика использования ИИ ассистента',
            'format': ['csv', 'json']
        },
        {
            'id': 'system_health',
            'name': 'Состояние системы',
            'description': 'Мониторинг производительности системы',
            'format': ['json']
        }
    ]
    
    return render_template('admin/unified/analytics/reports.html',
                         available_reports=available_reports)

@analytics_admin_bp.route('/api/reports/<report_id>')
@admin_required(['analytics'])
def generate_report(lang, report_id):
    """Генерация отчета"""
    try:
        format_type = request.args.get('format', 'json')
        date_from = request.args.get('from')
        date_to = request.args.get('to')
        
        # Базовая фильтрация по датам
        if date_from:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
        else:
            date_from = datetime.now() - timedelta(days=30)
            
        if date_to:
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
        else:
            date_to = datetime.now()
        
        if report_id == 'user_activity':
            # Отчет по активности пользователей
            users_data = db.session.query(
                User.id,
                User.name,
                User.email,
                User.created_at,
                User.last_login,
                func.count(UserProgress.id).label('lessons_completed'),
                func.sum(UserProgress.time_spent).label('total_time')
            ).outerjoin(UserProgress).filter(
                User.created_at.between(date_from, date_to)
            ).group_by(User.id).all()
            
            report_data = []
            for user in users_data:
                report_data.append({
                    'user_id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'registered': user.created_at.isoformat() if user.created_at else None,
                    'last_login': user.last_login.isoformat() if user.last_login else None,
                    'lessons_completed': user.lessons_completed or 0,
                    'total_study_time': float(user.total_time or 0)
                })
        
        elif report_id == 'learning_progress':
            # Отчет по прогрессу обучения
            progress_data = db.session.query(
                Module.title.label('module_name'),
                Subject.name.label('subject_name'),
                func.count(UserProgress.id).label('total_attempts'),
                func.sum(func.case([(UserProgress.completed == True, 1)], else_=0)).label('completed'),
                func.avg(UserProgress.time_spent).label('avg_time')
            ).join(Lesson).join(Module).join(Subject).filter(
                UserProgress.timestamp.between(date_from, date_to)
            ).group_by(Module.id, Subject.id).all()
            
            report_data = []
            for item in progress_data:
                completion_rate = (item.completed / item.total_attempts * 100) if item.total_attempts > 0 else 0
                report_data.append({
                    'module_name': item.module_name,
                    'subject_name': item.subject_name,
                    'total_attempts': item.total_attempts,
                    'completed': item.completed,
                    'completion_rate': round(completion_rate, 2),
                    'avg_study_time': round(float(item.avg_time or 0), 2)
                })
        
        elif report_id == 'ai_usage':
            # Отчет по использованию ИИ
            ai_data = db.session.query(
                AIConversation.provider,
                AIConversation.model_used,
                func.count(AIConversation.id).label('conversation_count'),
                func.sum(AIConversation.tokens_used).label('total_tokens'),
                func.avg(AIConversation.response_time_ms).label('avg_response_time'),
                func.avg(AIConversation.user_rating).label('avg_rating')
            ).filter(
                AIConversation.created_at.between(date_from, date_to)
            ).group_by(AIConversation.provider, AIConversation.model_used).all()
            
            report_data = []
            for item in ai_data:
                report_data.append({
                    'provider': item.provider,
                    'model': item.model_used,
                    'conversations': item.conversation_count,
                    'total_tokens': item.total_tokens or 0,
                    'avg_response_time_ms': round(float(item.avg_response_time or 0), 2),
                    'avg_user_rating': round(float(item.avg_rating or 0), 2)
                })
        
        else:
            return jsonify({'success': False, 'message': 'Неизвестный тип отчета'})
        
        # Логируем генерацию отчета
        current_app.logger.info(f"Admin {current_user.email} generated report: {report_id}")
        
        return jsonify({
            'success': True,
            'report_id': report_id,
            'generated_at': datetime.now().isoformat(),
            'date_range': {
                'from': date_from.isoformat(),
                'to': date_to.isoformat()
            },
            'data': report_data,
            'total_records': len(report_data)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error generating report {report_id}: {e}")
        return jsonify({'success': False, 'message': str(e)}) 