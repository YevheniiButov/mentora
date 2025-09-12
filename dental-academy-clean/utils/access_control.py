"""
Система контроля доступа для предварительного запуска Mentora
Блокирует определенные функции с красивыми "coming soon" экранами
"""

from functools import wraps
from flask import render_template, request, g, current_app
from flask_login import current_user
import logging

logger = logging.getLogger(__name__)

def coming_soon_required(feature_name, feature_description=None):
    """
    Декоратор для блокировки функций с красивой страницей coming soon
    
    Args:
        feature_name (str): Название функции (например, "Диагностическое тестирование")
        feature_description (str): Описание функции (опционально)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Проверяем, если это админ - пропускаем
            if current_user.is_authenticated and getattr(current_user, 'is_admin', False):
                logger.info(f"🔓 Admin access granted to {feature_name}")
                return f(*args, **kwargs)
            
            # Для всех остальных показываем coming soon
            logger.info(f"🔒 Blocking access to {feature_name} for user: {current_user.username if current_user.is_authenticated else 'anonymous'}")
            
            return render_template('coming_soon.html', 
                                 feature_name=feature_name,
                                 feature_description=feature_description,
                                 current_path=request.path,
                                 lang=g.get('lang', 'en'))
        return decorated_function
    return decorator

def block_blueprint_access(blueprint_name, feature_name, feature_description=None):
    """
    Блокирует весь blueprint целиком с помощью before_request
    
    Args:
        blueprint_name: Имя blueprint для блокировки
        feature_name: Название функции
        feature_description: Описание функции
    """
    def block_access():
        # Проверяем, если это админ - пропускаем
        if current_user.is_authenticated and getattr(current_user, 'is_admin', False):
            return None  # Пропускаем запрос
        
        # Для всех остальных показываем coming soon
        logger.info(f"🔒 Blocking blueprint {blueprint_name} - {feature_name}")
        
        return render_template('coming_soon.html', 
                             feature_name=feature_name,
                             feature_description=feature_description,
                             current_path=request.path,
                             lang=g.get('lang', 'en'))
    
    return block_access

def is_route_allowed(path):
    """
    Проверяет, разрешен ли доступ к маршруту
    
    Args:
        path (str): Путь для проверки
        
    Returns:
        bool: True если доступ разрешен, False если заблокирован
    """
    # Список разрешенных маршрутов
    ALLOWED_ROUTES = [
        '/',
        '/auth/login',
        '/auth/register', 
        '/auth/logout',
        '/profile',
        '/community',
        '/forum',
        '/about',
        '/contact',
        '/privacy',
        '/terms',
        '/faq',
        '/big-info',
        '/daily-learning/knowledge-base',  # Разрешаем базу знаний
    ]
    
    # Список заблокированных префиксов
    BLOCKED_PREFIXES = [
        '/big-diagnostic',
        '/learning',
        '/lesson', 
        '/content',
        '/tests',
        '/testing',
        '/ai-assistant',
        '/virtual-patient',
        '/admin',  # Админка только для админов
    ]
    
    # Проверяем точные совпадения
    if path in ALLOWED_ROUTES:
        return True
    
    # Проверяем префиксы
    for prefix in BLOCKED_PREFIXES:
        if path.startswith(prefix):
            return False
    
    # Проверяем разрешенные префиксы
    for allowed_prefix in ALLOWED_ROUTES:
        if path.startswith(allowed_prefix):
            return True
    
    # По умолчанию разрешаем (для статических файлов и т.д.)
    return True

def register_access_control(app):
    """
    Регистрирует систему контроля доступа в приложении
    
    Args:
        app: Flask приложение
    """
    logger.info("🔒 Registering access control system...")
    
    # Добавляем функции в контекст шаблонов
    @app.context_processor
    def inject_access_control():
        return {
            'is_route_allowed': is_route_allowed,
            'BLOCKED_FEATURES': [
                {
                    'name': 'Диагностическое тестирование', 
                    'description': 'Персонализированная оценка знаний',
                    'icon': 'fas fa-brain',
                    'category': 'diagnostic_testing'
                },
                {
                    'name': 'Интерактивное обучение', 
                    'description': 'Модули, уроки и контент',
                    'icon': 'fas fa-book-open', 
                    'category': 'learning'
                },
                {
                    'name': 'Тесты и экзамены', 
                    'description': 'Проверка знаний и подготовка к экзаменам',
                    'icon': 'fas fa-clipboard-list',
                    'category': 'tests_exams'
                },
                {
                    'name': 'AI-помощник', 
                    'description': 'Искусственный интеллект для помощи в обучении',
                    'icon': 'fas fa-robot',
                    'category': 'ai_assistant'
                },
                {
                    'name': 'Виртуальные пациенты', 
                    'description': 'Практика с виртуальными клиническими случаями',
                    'icon': 'fas fa-user-md',
                    'category': 'virtual_patients'
                }
            ]
        }
    
    logger.info("✅ Access control system registered successfully")