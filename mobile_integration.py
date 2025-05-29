# mobile_integration.py
"""
Интеграция мобильных шаблонов с Flask роутами
Автоматическое переключение между десктопными и мобильными версиями
"""

from flask import Blueprint, request, render_template, g, session, jsonify, redirect, url_for
from functools import wraps
import os
from utils.mobile_detection import (
    get_mobile_detector, 
    mobile_optimized_render_template,
    setup_mobile_detection
)


class MobileTemplateManager:
    """Менеджер мобильных шаблонов"""
    
    def __init__(self, app=None):
        self.app = app
        self.mobile_templates = {}
        self.template_mappings = {}
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Инициализация для Flask приложения"""
        self.app = app
        
        # Настраиваем определение мобильных устройств
        setup_mobile_detection(app)
        
        # Регистрируем функции в Jinja2
        app.jinja_env.globals['render_mobile_template'] = self.render_mobile_template
        app.jinja_env.globals['is_mobile_device'] = lambda: get_mobile_detector().is_mobile_device
        app.jinja_env.globals['get_device_type'] = lambda: get_mobile_detector().device_type
        
        # Добавляем кастомные фильтры
        app.jinja_env.filters['mobile_image'] = self.mobile_image_filter
        app.jinja_env.filters['mobile_truncate'] = self.mobile_truncate_filter
        
        # Регистрируем Blueprint для мобильных API
        mobile_bp = self.create_mobile_blueprint()
        app.register_blueprint(mobile_bp, url_prefix='/mobile-api')
        
        # Переопределяем render_template
        self.override_render_template(app)
        
        # Регистрируем новый шаблон
        self.register_mobile_template('auth/change_password.html', 'auth/change_password_mobile.html')
    
    def register_mobile_template(self, desktop_template, mobile_template):
        """
        Регистрирует соответствие между десктопным и мобильным шаблоном
        
        Args:
            desktop_template (str): Путь к десктопному шаблону
            mobile_template (str): Путь к мобильному шаблону
        """
        self.template_mappings[desktop_template] = mobile_template
    
    def get_appropriate_template(self, template_name):
        """
        Возвращает подходящий шаблон в зависимости от устройства
        
        Args:
            template_name (str): Имя исходного шаблона
            
        Returns:
            str: Имя шаблона для использования
        """
        detector = get_mobile_detector()
        
        # Проверяем принудительное переопределение
        if hasattr(g, 'force_desktop_template'):
            return template_name
        
        if hasattr(g, 'force_mobile_template'):
            return self.template_mappings.get(template_name, template_name.replace('.html', '_mobile.html'))
        
        # Автоматическое определение
        if detector.should_use_mobile_template():
            # Сначала проверяем зарегистрированные соответствия
            if template_name in self.template_mappings:
                return self.template_mappings[template_name]
            
            # Затем пробуем автоматическое именование
            mobile_template = template_name.replace('.html', '_mobile.html')
            
            # Проверяем, существует ли мобильный шаблон
            if self.template_exists(mobile_template):
                return mobile_template
        
        return template_name
    
    def template_exists(self, template_name):
        """Проверяет, существует ли шаблон"""
        try:
            self.app.jinja_env.get_template(template_name)
            return True
        except:
            return False
    
    def render_mobile_template(self, template_name, **context):
        """
        Рендерит шаблон с автоматическим выбором мобильной версии
        
        Args:
            template_name (str): Имя шаблона
            **context: Контекст шаблона
            
        Returns:
            str: Отрендеренный HTML
        """
        appropriate_template = self.get_appropriate_template(template_name)
        
        # Добавляем мобильную информацию в контекст
        detector = get_mobile_detector()
        mobile_context = {
            'is_mobile': detector.is_mobile,
            'is_tablet': detector.is_tablet,
            'is_mobile_device': detector.is_mobile_device,
            'device_type': detector.device_type,
            'screen_size': detector.screen_size_category,
            'device_info': detector.get_device_info(),
            'current_template': appropriate_template,
            'original_template': template_name
        }
        
        context.update(mobile_context)
        
        return render_template(appropriate_template, **context)
    
    def override_render_template(self, app):
        """Переопределяет стандартную функцию render_template"""
        original_render_template = app.jinja_env.globals.get('render_template')
        
        def mobile_aware_render_template(template_name_or_list, **context):
            if isinstance(template_name_or_list, str):
                return self.render_mobile_template(template_name_or_list, **context)
            else:
                # Если передан список шаблонов, обрабатываем каждый
                appropriate_templates = []
                for template in template_name_or_list:
                    appropriate_templates.append(self.get_appropriate_template(template))
                
                detector = get_mobile_detector()
                mobile_context = {
                    'is_mobile': detector.is_mobile,
                    'is_tablet': detector.is_tablet,
                    'is_mobile_device': detector.is_mobile_device,
                    'device_type': detector.device_type,
                    'screen_size': detector.screen_size_category,
                    'device_info': detector.get_device_info()
                }
                
                context.update(mobile_context)
                
                return render_template(appropriate_templates, **context)
        
        # Сохраняем в globals для доступа из шаблонов
        app.jinja_env.globals['render_template'] = mobile_aware_render_template
    
    def mobile_image_filter(self, image_path, size='auto'):
        """
        Фильтр для автоматического выбора размера изображения
        
        Args:
            image_path (str): Путь к изображению
            size (str): Размер ('auto', 'small', 'medium', 'large')
            
        Returns:
            str: Путь к оптимизированному изображению
        """
        if size == 'auto':
            detector = get_mobile_detector()
            size = detector.screen_size_category
        
        # Mapping размеров
        size_suffixes = {
            'small': '_small',
            'medium': '_medium', 
            'large': '_large',
            'desktop': ''
        }
        
        suffix = size_suffixes.get(size, '')
        
        if suffix and '.' in image_path:
            name, ext = image_path.rsplit('.', 1)
            optimized_path = f"{name}{suffix}.{ext}"
            
            # Проверяем, существует ли оптимизированная версия
            # В реальном приложении здесь была бы проверка файловой системы
            return optimized_path
        
        return image_path
    
    def mobile_truncate_filter(self, text, length=None):
        """
        Фильтр для обрезки текста в зависимости от устройства
        
        Args:
            text (str): Исходный текст
            length (int): Длина (если None, определяется автоматически)
            
        Returns:
            str: Обрезанный текст
        """
        if not text:
            return text
        
        if length is None:
            detector = get_mobile_detector()
            # Разные длины для разных устройств
            length_map = {
                'small': 50,
                'medium': 80,
                'large': 120,
                'desktop': 200
            }
            length = length_map.get(detector.screen_size_category, 80)
        
        if len(text) <= length:
            return text
        
        return text[:length-3] + '...'
    
    def create_mobile_blueprint(self):
        """Создает Blueprint для мобильных API"""
        mobile_bp = Blueprint('mobile_api', __name__)
        
        @mobile_bp.route('/device-info')
        def device_info():
            """API для получения информации об устройстве"""
            detector = get_mobile_detector()
            return jsonify(detector.get_device_info())
        
        @mobile_bp.route('/toggle-mode', methods=['POST'])
        def toggle_mode():
            """API для переключения мобильного режима"""
            data = request.get_json()
            mode = data.get('mode', 'auto')
            
            valid_modes = ['auto', 'force_mobile', 'force_desktop']
            if mode not in valid_modes:
                return jsonify({'error': 'Invalid mode'}), 400
            
            session['mobile_mode'] = mode
            
            return jsonify({
                'success': True,
                'mode': mode,
                'message': f'Режим изменен на {mode}'
            })
        
        @mobile_bp.route('/template-info')
        def template_info():
            """API для получения информации о текущем шаблоне"""
            template_name = request.args.get('template')
            if not template_name:
                return jsonify({'error': 'Template name required'}), 400
            
            detector = get_mobile_detector()
            appropriate_template = self.get_appropriate_template(template_name)
            
            return jsonify({
                'original_template': template_name,
                'used_template': appropriate_template,
                'is_mobile_version': appropriate_template != template_name,
                'device_info': detector.get_device_info()
            })
        
        @mobile_bp.route('/performance-metrics', methods=['POST'])
        def performance_metrics():
            """API для отправки метрик производительности"""
            data = request.get_json()
            
            # Здесь можно логировать метрики производительности
            # для анализа работы мобильной версии
            metrics = {
                'load_time': data.get('load_time'),
                'first_paint': data.get('first_paint'),
                'largest_contentful_paint': data.get('largest_contentful_paint'),
                'cumulative_layout_shift': data.get('cumulative_layout_shift'),
                'device_type': get_mobile_detector().device_type,
                'user_agent': request.headers.get('User-Agent'),
                'timestamp': data.get('timestamp')
            }
            
            # Логируем метрики (в реальном приложении сохранить в БД)
            self.app.logger.info(f"Mobile performance metrics: {metrics}")
            
            return jsonify({'success': True})
        
        return mobile_bp


# Декораторы для удобного использования

def mobile_route(rule, **options):
    """
    Декоратор для создания роутов с автоматической поддержкой мобильных шаблонов
    
    Usage:
        @mobile_route('/learning-map')
        def learning_map():
            return mobile_template_manager.render_mobile_template('learning/subject_view.html')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Добавляем информацию о мобильном устройстве в g
            detector = get_mobile_detector()
            g.is_mobile_request = detector.is_mobile_device
            g.device_type = detector.device_type
            
            return f(*args, **kwargs)
        
        # Регистрируем роут
        from flask import current_app
        current_app.add_url_rule(rule, f.__name__, decorated_function, **options)
        
        return decorated_function
    return decorator


def force_mobile_template(template_name):
    """
    Декоратор для принудительного использования мобильного шаблона
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            g.force_mobile_template = True
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def force_desktop_template(template_name):
    """
    Декоратор для принудительного использования десктопного шаблона
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            g.force_desktop_template = True
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# Глобальный экземпляр менеджера
mobile_template_manager = MobileTemplateManager()


def init_mobile_integration(app):
    """
    Инициализирует мобильную интеграцию для Flask приложения
    
    Args:
        app: Flask приложение
    """
    mobile_template_manager.init_app(app)
    
    # Регистрируем основные соответствия шаблонов
    template_mappings = {
        # Основные страницы
        'index.html': 'index_mobile.html',
        'learning/subject_view.html': 'learning/subject_view_mobile.html',
        'learning/lesson.html': 'learning/lesson_mobile.html',
        'learning/module.html': 'learning/module_mobile.html',
        'profile.html': 'profile_mobile.html',
        'dashboard.html': 'dashboard_mobile.html',
        
        # Тесты и экзамены
        'tests/test_setup.html': 'tests/test_setup_mobile.html',
        'tests/test_question.html': 'tests/test_question_mobile.html',
        'tests/test_result.html': 'tests/test_result_mobile.html',
        
        # Виртуальные пациенты
        'virtual_patient/scenarios_list.html': 'virtual_patient/scenarios_list_mobile.html',
        'virtual_patient/interact.html': 'virtual_patient/interact_mobile.html',
        'virtual_patient/results.html': 'virtual_patient/results_mobile.html',
        
        # Аутентификация
        'auth/login.html': 'auth/login_mobile.html',
        'auth/register.html': 'auth/register_mobile.html',
        'auth/reset_password.html': 'auth/reset_password_mobile.html',
    }
    
    for desktop, mobile in template_mappings.items():
        mobile_template_manager.register_mobile_template(desktop, mobile)
    
    app.logger.info(f"Mobile integration initialized with {len(template_mappings)} template mappings")


# Хелперы для использования в роутах

def render_adaptive_template(template_name, **context):
    """
    Удобная функция для рендеринга адаптивных шаблонов
    
    Args:
        template_name (str): Имя шаблона
        **context: Контекст для шаблона
        
    Returns:
        str: Отрендеренный HTML
    """
    return mobile_template_manager.render_mobile_template(template_name, **context)


def is_mobile_session():
    """Проверяет, является ли текущая сессия мобильной"""
    detector = get_mobile_detector()
    return detector.is_mobile_device


def get_optimal_content_length(content_type='text'):
    """
    Возвращает оптимальную длину контента для текущего устройства
    
    Args:
        content_type (str): Тип контента ('text', 'title', 'description')
        
    Returns:
        int: Рекомендуемая длина
    """
    detector = get_mobile_detector()
    device_type = detector.device_type
    
    length_map = {
        'text': {
            'mobile': 150,
            'tablet': 250,
            'desktop': 400
        },
        'title': {
            'mobile': 30,
            'tablet': 50,
            'desktop': 80
        },
        'description': {
            'mobile': 80,
            'tablet': 120,
            'desktop': 200
        }
    }
    
    return length_map.get(content_type, {}).get(device_type, 200)


def should_lazy_load(device_type=None):
    """
    Определяет, следует ли использовать ленивую загрузку
    
    Args:
        device_type (str): Тип устройства (опционально)
        
    Returns:
        bool: True если следует использовать lazy loading
    """
    if device_type is None:
        device_type = get_mobile_detector().device_type
    
    # На мобильных устройствах всегда используем lazy loading
    return device_type in ['mobile', 'tablet']


def get_touch_friendly_spacing():
    """Возвращает рекомендуемые отступы для touch-friendly интерфейса"""
    detector = get_mobile_detector()
    
    if detector.is_mobile:
        return {
            'button_height': '44px',
            'touch_target': '44px',
            'padding': '16px',
            'margin': '12px'
        }
    elif detector.is_tablet:
        return {
            'button_height': '48px',
            'touch_target': '48px', 
            'padding': '20px',
            'margin': '16px'
        }
    else:
        return {
            'button_height': '40px',
            'touch_target': '40px',
            'padding': '24px',
            'margin': '20px'
        }