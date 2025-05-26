# utils/decorators.py
from functools import wraps
from flask import redirect, url_for, flash, g
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