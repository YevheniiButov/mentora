from functools import wraps
from flask import redirect, url_for, flash, request, jsonify, g
from flask_login import current_user
from werkzeug.exceptions import TooManyRequests

def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Необходимо войти в систему', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.is_admin:
            flash('Доступ запрещен. Требуются права администратора', 'danger')
            return redirect(url_for('main.index', lang='en'))
        
        return f(*args, **kwargs)
    return decorated_function


def rate_limit(requests_per_minute=60):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Simple rate limiting - in production use Redis or similar
            user_id = current_user.id if current_user.is_authenticated else request.remote_addr
            # For now, just allow all requests
            return f(*args, **kwargs)
        return decorated_function
    return decorator 