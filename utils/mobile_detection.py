# utils/mobile_detection.py
"""
Mobile Device Detection Utilities for Dental Academy
Автоматическое определение мобильных устройств и переключение на мобильные шаблоны
"""

import re
from flask import request, g, session
from functools import wraps
from user_agents import parse


class MobileDetector:
    """Класс для определения мобильных устройств и их характеристик"""
    
    # Паттерны User-Agent для мобильных устройств
    MOBILE_PATTERNS = [
        r'Mobile', r'Android', r'iPhone', r'iPad', r'iPod',
        r'BlackBerry', r'IEMobile', r'Opera Mini', r'Opera Mobi',
        r'Windows Phone', r'Kindle', r'Silk', r'Mobile Safari'
    ]
    
    # Паттерны для планшетов
    TABLET_PATTERNS = [
        r'iPad', r'Android(?!.*Mobile)', r'Tablet', r'Kindle',
        r'Silk', r'PlayBook', r'Nexus 7', r'Nexus 10'
    ]
    
    # Известные мобильные браузеры
    MOBILE_BROWSERS = [
        'Chrome Mobile', 'Safari Mobile', 'Firefox Mobile',
        'Opera Mobile', 'UC Browser', 'Samsung Browser'
    ]
    
    # Размеры экранов для определения устройств
    MOBILE_SCREEN_WIDTHS = {
        'small': 480,   # Маленькие телефоны (iPhone SE, и т.д.)
        'medium': 768,  # Средние телефоны (iPhone, Samsung Galaxy)
        'large': 1024,  # Планшеты и большие телефоны
        'desktop': 1200 # Десктопы
    }
    
    def __init__(self, user_agent_string=None, request_headers=None):
        """
        Инициализация детектора
        
        Args:
            user_agent_string (str): Строка User-Agent
            request_headers (dict): Заголовки запроса
        """
        self.user_agent_string = user_agent_string or ''
        self.request_headers = request_headers or {}
        self.parsed_ua = parse(self.user_agent_string) if self.user_agent_string else None
        
        # Кэшируем результаты
        self._is_mobile = None
        self._is_tablet = None
        self._device_type = None
        self._screen_size = None
    
    @property
    def is_mobile(self):
        """Определяет, является ли устройство мобильным (телефон)"""
        if self._is_mobile is None:
            self._is_mobile = self._detect_mobile()
        return self._is_mobile
    
    @property
    def is_tablet(self):
        """Определяет, является ли устройство планшетом"""
        if self._is_tablet is None:
            self._is_tablet = self._detect_tablet()
        return self._is_tablet
    
    @property
    def is_mobile_device(self):
        """Определяет, является ли устройство мобильным (телефон или планшет)"""
        return self.is_mobile or self.is_tablet
    
    @property
    def device_type(self):
        """Возвращает тип устройства: 'mobile', 'tablet', 'desktop'"""
        if self._device_type is None:
            if self.is_mobile:
                self._device_type = 'mobile'
            elif self.is_tablet:
                self._device_type = 'tablet'
            else:
                self._device_type = 'desktop'
        return self._device_type
    
    @property
    def screen_size_category(self):
        """Определяет категорию размера экрана"""
        if self._screen_size is None:
            self._screen_size = self._detect_screen_size()
        return self._screen_size
    
    def _detect_mobile(self):
        """Внутренний метод для определения мобильного устройства"""
        if not self.user_agent_string:
            return False
        
        # Используем библиотеку user-agents
        if self.parsed_ua and self.parsed_ua.is_mobile:
            return True
        
        # Дополнительная проверка по паттернам
        mobile_pattern = '|'.join(self.MOBILE_PATTERNS)
        if re.search(mobile_pattern, self.user_agent_string, re.IGNORECASE):
            # Исключаем планшеты
            tablet_pattern = '|'.join(self.TABLET_PATTERNS)
            if not re.search(tablet_pattern, self.user_agent_string, re.IGNORECASE):
                return True
        
        # Проверка заголовков
        if self._check_mobile_headers():
            return True
        
        return False
    
    def _detect_tablet(self):
        """Внутренний метод для определения планшета"""
        if not self.user_agent_string:
            return False
        
        # Используем библиотеку user-agents
        if self.parsed_ua and self.parsed_ua.is_tablet:
            return True
        
        # Проверка по паттернам
        tablet_pattern = '|'.join(self.TABLET_PATTERNS)
        return bool(re.search(tablet_pattern, self.user_agent_string, re.IGNORECASE))
    
    def _detect_screen_size(self):
        """Определяет категорию размера экрана на основе различных факторов"""
        # Проверяем заголовки для ширины экрана
        viewport_width = self._get_viewport_width()
        
        if viewport_width:
            if viewport_width <= self.MOBILE_SCREEN_WIDTHS['small']:
                return 'small'
            elif viewport_width <= self.MOBILE_SCREEN_WIDTHS['medium']:
                return 'medium'
            elif viewport_width <= self.MOBILE_SCREEN_WIDTHS['large']:
                return 'large'
            else:
                return 'desktop'
        
        # Fallback на основе типа устройства
        if self.is_mobile:
            return 'medium'  # По умолчанию средний размер для телефонов
        elif self.is_tablet:
            return 'large'   # Планшеты обычно большие
        else:
            return 'desktop'
    
    def _check_mobile_headers(self):
        """Проверяет специальные заголовки для мобильных устройств"""
        mobile_headers = [
            'HTTP_X_WAP_PROFILE',
            'HTTP_X_WAP_CLIENTID',
            'HTTP_WAP_CONNECTION',
            'HTTP_PROFILE',
            'HTTP_X_OPERAMINI_PHONE_UA',
            'HTTP_X_NOKIA_GATEWAY_ID',
            'HTTP_X_ORANGE_ID',
            'HTTP_X_VODAFONE_3GPDPCONTEXT',
            'HTTP_X_HUAWEI_USERID'
        ]
        
        for header in mobile_headers:
            if self.request_headers.get(header):
                return True
        
        # Проверка заголовка Accept
        accept = self.request_headers.get('HTTP_ACCEPT', '')
        if 'wap' in accept.lower() or 'application/vnd.wap' in accept.lower():
            return True
        
        return False
    
    def _get_viewport_width(self):
        """Получает ширину viewport из заголовков (если доступно)"""
        # Некоторые прокси и CDN добавляют информацию о размере экрана
        viewport = self.request_headers.get('HTTP_VIEWPORT_WIDTH')
        if viewport:
            try:
                return int(viewport)
            except (ValueError, TypeError):
                pass
        
        # Cloudflare может предоставлять информацию об устройстве
        cf_device = self.request_headers.get('HTTP_CF_DEVICE_TYPE')
        if cf_device:
            device_widths = {
                'mobile': 375,
                'tablet': 768,
                'desktop': 1200
            }
            return device_widths.get(cf_device.lower())
        
        return None
    
    def get_device_info(self):
        """Возвращает полную информацию об устройстве"""
        device_info = {
            'is_mobile': self.is_mobile,
            'is_tablet': self.is_tablet,
            'is_mobile_device': self.is_mobile_device,
            'device_type': self.device_type,
            'screen_size_category': self.screen_size_category,
            'user_agent': self.user_agent_string
        }
        
        if self.parsed_ua:
            device_info.update({
                'browser_family': self.parsed_ua.browser.family,
                'browser_version': self.parsed_ua.browser.version_string,
                'os_family': self.parsed_ua.os.family,
                'os_version': self.parsed_ua.os.version_string,
                'device_family': self.parsed_ua.device.family,
                'device_brand': self.parsed_ua.device.brand,
                'device_model': self.parsed_ua.device.model
            })
        
        return device_info
    
    def should_use_mobile_template(self, force_mobile=None):
        """
        Определяет, следует ли использовать мобильный шаблон
        
        Args:
            force_mobile (bool): Принудительное включение/отключение мобильного режима
        
        Returns:
            bool: True если нужно использовать мобильный шаблон
        """
        if force_mobile is not None:
            return force_mobile
        
        # Проверяем настройки пользователя в сессии
        user_preference = session.get('mobile_mode')
        if user_preference == 'force_mobile':
            return True
        elif user_preference == 'force_desktop':
            return False
        
        # Автоматическое определение
        return self.is_mobile_device


def get_mobile_detector():
    """Получает экземпляр MobileDetector для текущего запроса"""
    if not hasattr(g, 'mobile_detector'):
        user_agent = request.headers.get('User-Agent', '')
        headers = dict(request.headers)
        g.mobile_detector = MobileDetector(user_agent, headers)
    
    return g.mobile_detector


def is_mobile_request():
    """Быстрая проверка, является ли текущий запрос мобильным"""
    detector = get_mobile_detector()
    return detector.is_mobile_device


def mobile_template(template_name):
    """
    Декоратор для автоматического выбора мобильного шаблона
    
    Usage:
        @mobile_template('learning/subject_view.html')
        def view_function():
            return render_template(...)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            detector = get_mobile_detector()
            
            if detector.should_use_mobile_template():
                # Заменяем расширение на _mobile
                mobile_template_name = template_name.replace('.html', '_mobile.html')
                g.mobile_template_override = mobile_template_name
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def setup_mobile_detection(app):
    """
    Настраивает обнаружение мобильных устройств для Flask приложения
    
    Args:
        app: Flask приложение
    """
    
    @app.before_request
    def detect_mobile_device():
        """Определяет тип устройства перед каждым запросом"""
        detector = get_mobile_detector()
        
        # Добавляем информацию об устройстве в g для использования в шаблонах
        g.is_mobile = detector.is_mobile
        g.is_tablet = detector.is_tablet
        g.is_mobile_device = detector.is_mobile_device
        g.device_type = detector.device_type
        g.screen_size = detector.screen_size_category
        g.device_info = detector.get_device_info()
    
    @app.context_processor
    def inject_mobile_context():
        """Добавляет мобильные переменные в контекст всех шаблонов"""
        detector = get_mobile_detector()
        return {
            'is_mobile': detector.is_mobile,
            'is_tablet': detector.is_tablet,
            'is_mobile_device': detector.is_mobile_device,
            'device_type': detector.device_type,
            'screen_size': detector.screen_size_category
        }
    
    @app.route('/api/device-info')
    def device_info_api():
        """API эндпоинт для получения информации об устройстве"""
        detector = get_mobile_detector()
        return detector.get_device_info()
    
    @app.route('/api/toggle-mobile-mode')
    def toggle_mobile_mode():
        """API для переключения мобильного режима"""
        mode = request.args.get('mode', 'auto')
        
        if mode in ['auto', 'force_mobile', 'force_desktop']:
            session['mobile_mode'] = mode
            return {'success': True, 'mode': mode}
        
        return {'success': False, 'error': 'Invalid mode'}, 400


def mobile_optimized_render_template(template_name_or_list, **context):
    """
    Функция рендеринга шаблонов с автоматическим выбором мобильной версии
    
    Args:
        template_name_or_list: Имя шаблона или список шаблонов
        **context: Контекст для шаблона
    
    Returns:
        Отрендеренный шаблон
    """
    from flask import render_template
    
    detector = get_mobile_detector()
    
    # Проверяем, есть ли принудительное переопределение шаблона
    if hasattr(g, 'mobile_template_override'):
        template_name_or_list = g.mobile_template_override
    elif detector.should_use_mobile_template():
        # Автоматически выбираем мобильную версию
        if isinstance(template_name_or_list, str):
            mobile_template = template_name_or_list.replace('.html', '_mobile.html')
            
            # Проверяем, существует ли мобильный шаблон
            try:
                from flask import current_app
                current_app.jinja_env.get_template(mobile_template)
                template_name_or_list = mobile_template
            except:
                # Если мобильный шаблон не найден, используем оригинальный
                pass
    
    # Добавляем мобильную информацию в контекст
    context.update({
        'is_mobile': detector.is_mobile,
        'is_tablet': detector.is_tablet,
        'is_mobile_device': detector.is_mobile_device,
        'device_type': detector.device_type,
        'screen_size': detector.screen_size_category,
        'device_info': detector.get_device_info()
    })
    
    return render_template(template_name_or_list, **context)


# Алиас для удобства
render_template_mobile = mobile_optimized_render_template


def create_responsive_image_url(image_path, size_category=None):
    """
    Создает URL для адаптивного изображения на основе размера экрана
    
    Args:
        image_path (str): Путь к оригинальному изображению
        size_category (str): Категория размера ('small', 'medium', 'large', 'desktop')
    
    Returns:
        str: URL адаптивного изображения
    """
    if not size_category:
        detector = get_mobile_detector()
        size_category = detector.screen_size_category
    
    # Определяем размеры для разных категорий
    size_mappings = {
        'small': '_small',    # Для маленьких экранов
        'medium': '_medium',  # Для средних экранов
        'large': '_large',    # Для больших экранов/планшетов
        'desktop': ''         # Для десктопов используем оригинал
    }
    
    suffix = size_mappings.get(size_category, '')
    
    if suffix:
        # Вставляем суффикс перед расширением файла
        name, ext = image_path.rsplit('.', 1)
        return f"{name}{suffix}.{ext}"
    
    return image_path


# Дополнительные утилитные функции

def get_optimal_image_quality(device_type):
    """Возвращает оптимальное качество изображения для типа устройства"""
    quality_map = {
        'mobile': 75,    # Более сжатые изображения для мобильных
        'tablet': 85,    # Средние качество для планшетов
        'desktop': 95    # Высокое качество для десктопов
    }
    return quality_map.get(device_type, 85)


def should_preload_images(device_type):
    """Определяет, следует ли предзагружать изображения"""
    # На мобильных устройствах лучше не предзагружать из-за трафика
    return device_type == 'desktop'


def get_optimal_video_quality(device_type, connection_type='unknown'):
    """Возвращает оптимальное качество видео"""
    if device_type == 'mobile':
        return '480p'
    elif device_type == 'tablet':
        return '720p'
    else:
        return '1080p'