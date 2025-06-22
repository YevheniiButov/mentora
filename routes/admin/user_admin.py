# routes/admin/user_admin.py
# Управление пользователями

from flask import Blueprint, render_template, request, jsonify, flash, current_app
from flask_login import current_user
from sqlalchemy import func, desc, or_
from datetime import datetime, timedelta
import bcrypt

from models import db, User, UserProgress, UserStats, UserAchievement
from . import admin_required

# Создаем blueprint для пользователей
user_admin_bp = Blueprint('user_admin', __name__, url_prefix='/users')

# ================== USERS DASHBOARD ==================

@user_admin_bp.route('/dashboard')
@admin_required(['users'])
def user_dashboard(lang):
    """Дашборд управления пользователями"""
    
    # Статистика пользователей
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    stats = {
        'total_users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'premium_users': User.query.filter_by(has_subscription=True).count(),
        'admin_users': User.query.filter_by(role='admin').count(),
        'new_users_today': User.query.filter(func.date(User.created_at) == today).count(),
        'new_users_week': User.query.filter(User.created_at >= week_ago).count(),
        'new_users_month': User.query.filter(User.created_at >= month_ago).count()
    }
    
    # Последние регистрации
    recent_users = User.query.order_by(desc(User.created_at)).limit(10).all()
    
    # Топ активных пользователей
    active_users = User.query.join(UserProgress).group_by(User.id).order_by(
        desc(func.count(UserProgress.id))
    ).limit(10).all()
    
    return render_template('admin/unified/users/dashboard.html',
                         stats=stats,
                         recent_users=recent_users,
                         active_users=active_users)

# ================== USERS LIST ==================

@user_admin_bp.route('/')
@admin_required(['users'])
def users_list(lang):
    """Список пользователей с фильтрацией"""
    
    # Параметры фильтрации
    search = request.args.get('search', '')
    role = request.args.get('role', '')
    status = request.args.get('status', '')
    subscription = request.args.get('subscription', '')
    
    # Базовый запрос
    query = User.query
    
    # Применяем фильтры
    if search:
        query = query.filter(or_(
            User.name.ilike(f'%{search}%'),
            User.email.ilike(f'%{search}%'),
            User.username.ilike(f'%{search}%')
        ))
    
    if role:
        query = query.filter(User.role == role)
    
    if status == 'active':
        query = query.filter(User.is_active == True)
    elif status == 'inactive':
        query = query.filter(User.is_active == False)
    
    if subscription == 'premium':
        query = query.filter(User.has_subscription == True)
    elif subscription == 'free':
        query = query.filter(User.has_subscription == False)
    
    # Сортировка и пагинация
    sort_by = request.args.get('sort', 'created_at')
    sort_order = request.args.get('order', 'desc')
    
    if sort_by == 'name':
        order_field = User.name
    elif sort_by == 'email':
        order_field = User.email
    elif sort_by == 'last_login':
        order_field = User.last_login
    else:
        order_field = User.created_at
    
    if sort_order == 'desc':
        order_field = desc(order_field)
    
    page = request.args.get('page', 1, type=int)
    per_page = 25
    
    users = query.order_by(order_field).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/unified/users/list.html',
                         users=users,
                         current_filters={
                             'search': search,
                             'role': role,
                             'status': status,
                             'subscription': subscription,
                             'sort': sort_by,
                             'order': sort_order
                         })

# ================== USER DETAILS ==================

@user_admin_bp.route('/<int:user_id>')
@admin_required(['users'])
def user_details(lang, user_id):
    """Детальная информация о пользователе"""
    user = User.query.get_or_404(user_id)
    
    # Статистика прогресса
    progress_stats = {
        'total_lessons': user.progress.count(),
        'completed_lessons': user.progress.filter_by(completed=True).count(),
        'total_time': user.progress.with_entities(func.sum(UserProgress.time_spent)).scalar() or 0
    }
    
    # Последняя активность
    recent_progress = user.progress.order_by(desc(UserProgress.last_accessed)).limit(10).all()
    
    # Достижения
    achievements = UserAchievement.query.filter_by(user_id=user_id).join(
        UserAchievement.achievement
    ).all()
    
    return render_template('admin/unified/users/details.html',
                         user=user,
                         progress_stats=progress_stats,
                         recent_progress=recent_progress,
                         achievements=achievements)

# ================== USER CRUD ==================

@user_admin_bp.route('/api/<int:user_id>', methods=['PUT'])
@admin_required(['users'])
def update_user(lang, user_id):
    """Обновление пользователя"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        # Проверяем права на изменение роли
        if 'role' in data and data['role'] == 'admin':
            if current_user.role != 'super_admin' and current_user.role != 'admin':
                return jsonify({'success': False, 'message': 'Недостаточно прав для назначения админа'})
        
        # Нельзя лишить себя админских прав
        if user.id == current_user.id and 'role' in data and data['role'] != 'admin':
            return jsonify({'success': False, 'message': 'Нельзя лишить себя админских прав'})
        
        # Обновляем поля
        if 'name' in data:
            user.name = data['name']
        if 'email' in data:
            # Проверяем уникальность email
            existing = User.query.filter(User.email == data['email'], User.id != user_id).first()
            if existing:
                return jsonify({'success': False, 'message': 'Email уже используется'})
            user.email = data['email']
        if 'role' in data:
            user.role = data['role']
        if 'is_active' in data:
            user.is_active = data['is_active']
        if 'has_subscription' in data:
            user.has_subscription = data['has_subscription']
        if 'language' in data:
            user.language = data['language']
        
        # Обновление пароля
        if 'password' in data and data['password']:
            user.password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        
        db.session.commit()
        
        current_app.logger.info(f"Admin {current_user.email} updated user: {user.email}")
        
        return jsonify({
            'success': True,
            'message': 'Пользователь обновлен'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating user {user_id}: {e}")
        return jsonify({'success': False, 'message': str(e)})

@user_admin_bp.route('/api/<int:user_id>', methods=['DELETE'])
@admin_required(['users'])
def delete_user(lang, user_id):
    """Удаление пользователя"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Нельзя удалить себя
        if user.id == current_user.id:
            return jsonify({'success': False, 'message': 'Нельзя удалить свой аккаунт'})
        
        # Нельзя удалить другого админа (только супер-админ может)
        if user.role == 'admin' and current_user.role != 'super_admin':
            return jsonify({'success': False, 'message': 'Недостаточно прав для удаления администратора'})
        
        user_email = user.email
        db.session.delete(user)
        db.session.commit()
        
        current_app.logger.info(f"Admin {current_user.email} deleted user: {user_email}")
        
        return jsonify({
            'success': True,
            'message': 'Пользователь удален'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting user {user_id}: {e}")
        return jsonify({'success': False, 'message': str(e)})

# ================== BULK OPERATIONS ==================

@user_admin_bp.route('/api/bulk', methods=['POST'])
@admin_required(['users'])
def bulk_user_operations(lang):
    """Массовые операции с пользователями"""
    try:
        data = request.get_json()
        user_ids = data.get('user_ids', [])
        operation = data.get('operation')
        
        if not user_ids or not operation:
            return jsonify({'success': False, 'message': 'Параметры не указаны'})
        
        users = User.query.filter(User.id.in_(user_ids)).all()
        affected_count = 0
        
        for user in users:
            # Защита от изменения своего аккаунта
            if user.id == current_user.id:
                continue
                
            if operation == 'activate':
                user.is_active = True
                affected_count += 1
            elif operation == 'deactivate':
                user.is_active = False
                affected_count += 1
            elif operation == 'grant_subscription':
                user.has_subscription = True
                affected_count += 1
            elif operation == 'revoke_subscription':
                user.has_subscription = False
                affected_count += 1
        
        db.session.commit()
        
        current_app.logger.info(f"Admin {current_user.email} performed bulk operation '{operation}' on {affected_count} users")
        
        return jsonify({
            'success': True,
            'message': f'Операция выполнена для {affected_count} пользователей'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in bulk user operation: {e}")
        return jsonify({'success': False, 'message': str(e)})

# ================== USER ANALYTICS ==================

@user_admin_bp.route('/analytics')
@admin_required(['users', 'analytics'])
def user_analytics(lang):
    """Аналитика пользователей"""
    
    # Статистика по дням за последний месяц
    daily_stats = []
    for i in range(30):
        date = datetime.now().date() - timedelta(days=i)
        registrations = User.query.filter(func.date(User.created_at) == date).count()
        daily_stats.append({
            'date': date.strftime('%Y-%m-%d'),
            'registrations': registrations
        })
    
    # Распределение по ролям
    role_stats = db.session.query(User.role, func.count(User.id)).group_by(User.role).all()
    
    # Активность пользователей
    activity_stats = {
        'never_logged_in': User.query.filter(User.last_login == None).count(),
        'logged_today': User.query.filter(func.date(User.last_login) == datetime.now().date()).count(),
        'logged_week': User.query.filter(User.last_login >= datetime.now() - timedelta(days=7)).count(),
        'logged_month': User.query.filter(User.last_login >= datetime.now() - timedelta(days=30)).count()
    }
    
    return render_template('admin/unified/users/analytics.html',
                         daily_stats=daily_stats,
                         role_stats=role_stats,
                         activity_stats=activity_stats) 