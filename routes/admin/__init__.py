# routes/admin/__init__.py
# Единая админ панель - центральный модуль

from flask import Blueprint, g, request, redirect, url_for, flash, current_app, session
from flask_login import current_user
from functools import wraps

# Создаем главный админ blueprint
admin_unified_bp = Blueprint(
    'admin_unified',
    __name__,
    url_prefix='/<string:lang>/admin',
    template_folder='../../templates/admin',
    static_folder='../../static'
)

# Поддерживаемые языки
SUPPORTED_LANGUAGES = ['en', 'ru', 'nl', 'uk', 'es', 'pt', 'tr', 'fa', 'ar']
DEFAULT_LANGUAGE = 'en'

# Роли доступа к админке
ADMIN_ROLES = {
    'super_admin': ['all'],  # Полный доступ
    'content_admin': ['content', 'lessons', 'modules', 'virtual_patients'],  # Только контент
    'user_admin': ['users', 'analytics'],  # Только пользователи
    'admin': ['all']  # Обратная совместимость
}

def admin_required(required_permissions=None):
    """
    Декоратор для проверки прав доступа к админке
    
    Args:
        required_permissions: список разрешений или строка с одним разрешением
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Проверка авторизации
            if not current_user.is_authenticated:
                flash("Для доступа к админ панели необходимо войти в систему", "warning")
                return redirect(url_for('auth_bp.login', lang=g.lang, next=request.url))
            
            # Проверка роли админа
            if not current_user.is_admin:
                flash("У вас нет прав для доступа к админ панели", "danger")
                return redirect(url_for('main_bp.home', lang=g.lang))
            
            # Проверка конкретных разрешений
            if required_permissions:
                user_role = current_user.role
                user_permissions = ADMIN_ROLES.get(user_role, [])
                
                # Если у пользователя есть 'all' - полный доступ
                if 'all' not in user_permissions:
                    # Проверяем конкретные разрешения
                    if isinstance(required_permissions, str):
                        required_permissions = [required_permissions]
                    
                    if not any(perm in user_permissions for perm in required_permissions):
                        flash("У вас недостаточно прав для выполнения этого действия", "warning")
                        return redirect(url_for('admin_unified.dashboard', lang=g.lang))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@admin_unified_bp.before_request
def before_admin_request():
    """Предварительная обработка всех запросов к админке"""
    # Установка языка
    lang_from_url = request.view_args.get('lang') if request.view_args else None
    
    if lang_from_url and lang_from_url in SUPPORTED_LANGUAGES:
        g.lang = lang_from_url
    else:
        g.lang = session.get('lang') or request.accept_languages.best_match(SUPPORTED_LANGUAGES) or DEFAULT_LANGUAGE
    
    # Обновляем сессию
    if session.get('lang') != g.lang:
        session['lang'] = g.lang
    
    # Логирование действий администратора
    if current_user.is_authenticated and current_user.is_admin:
        current_app.logger.info(f"Admin action: {current_user.email} accessed {request.endpoint}")

@admin_unified_bp.context_processor
def inject_admin_context():
    """Добавляет общие переменные в контекст всех админ шаблонов"""
    return {
        'lang': g.lang,
        'current_user': current_user,
        'admin_roles': ADMIN_ROLES,
        'user_role': current_user.role if current_user.is_authenticated else None
    }

# Импортируем дашборд
from .dashboard import *

# Импортируем модули админки
from .content_admin import content_admin_bp
from .user_admin import user_admin_bp  
from .analytics_admin import analytics_admin_bp
from .system_admin import system_admin_bp

# Регистрируем субблюпринты
admin_unified_bp.register_blueprint(content_admin_bp)
admin_unified_bp.register_blueprint(user_admin_bp)
admin_unified_bp.register_blueprint(analytics_admin_bp)
admin_unified_bp.register_blueprint(system_admin_bp) 