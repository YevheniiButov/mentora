# utils/decorators.py
from functools import wraps
from flask import redirect, url_for, flash, g, jsonify
from flask_login import current_user

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Проверка, что пользователь аутентифицирован и является администратором
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('У вас нет доступа к этой странице', 'danger')
            return redirect(url_for('main_bp.home', lang=g.lang))
        return f(*args, **kwargs)
    return decorated_function

def api_login_required(f):
    """Декоратор для API эндпоинтов - возвращает JSON ошибку вместо редиректа"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({
                'success': False,
                'error': 'Authentication required',
                'code': 401,
                'message': 'Please log in to access this resource'
            }), 401
        return f(*args, **kwargs)
    return decorated_function

def api_admin_required(f):
    """Декоратор для API эндпоинтов - проверяет права администратора"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return jsonify({
                'success': False,
                'error': 'Authentication required',
                'code': 401,
                'message': 'Please log in to access this resource'
            }), 401
        
        # Проверяем права администратора
        if not getattr(current_user, 'is_admin', False) and getattr(current_user, 'role', '') != 'admin':
            return jsonify({
                'success': False,
                'error': 'Admin privileges required',
                'code': 403,
                'message': 'You need administrator privileges to access this resource'
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function