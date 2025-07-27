# utils/mobile_detection.py
"""
Система определения мобильных устройств для Mentora
Интеграция с существующей mobile_integration.py
"""

from flask import request, g, session, current_app
import re

class MobileDetector:
    """Улучшенный детектор мобильных устройств"""
    
    def __init__(self):
        self.user_agent = request.headers.get('User-Agent', '') if request else ''
        self._is_mobile = None
        self._is_tablet = None
        self._device_type = None
        self._screen_size_category = None
    
    @property
    def is_mobile(self):
        """Определяет, является ли устройство мобильным телефоном"""
        if self._is_mobile is None:
            mobile_patterns = [
                r'Mobile', r'Android.*Mobile', r'iPhone', r'iPod',
                r'BlackBerry', r'IEMobile', r'Opera Mini', r'Mobile Safari',
                r'Windows Phone', r'webOS'
            ]
            mobile_regex = re.compile('|'.join(mobile_patterns), re.IGNORECASE)
            self._is_mobile = bool(mobile_regex.search(self.user_agent))
        return self._is_mobile
    
    @property
    def is_tablet(self):
        """Определяет, является ли устройство планшетом"""
        if self._is_tablet is None:
            tablet_patterns = [
                r'iPad', r'Android(?!.*Mobile)', r'Kindle', r'Silk',
                r'PlayBook', r'Tablet'
            ]
            tablet_regex = re.compile('|'.join(tablet_patterns), re.IGNORECASE)
            self._is_tablet = bool(tablet_regex.search(self.user_agent))
        return self._is_tablet
    
    @property
    def is_mobile_device(self):
        """Определяет, является ли устройство мобильным (телефон или планшет)"""
        return self.is_mobile or self.is_tablet
    
    @property
    def device_type(self):
        """Возвращает тип устройства"""
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
        if self._screen_size_category is None:
            if self.is_mobile:
                self._screen_size_category = 'small'
            elif self.is_tablet:
                self._screen_size_category = 'medium'
            else:
                self._screen_size_category = 'large'
        return self._screen_size_category
    
    def should_use_mobile_template(self):
        """Определяет, следует ли использовать мобильный шаблон"""
        # Проверяем принудительный режим из сессии
        mobile_mode = session.get('mobile_mode', 'auto')
        
        if mobile_mode == 'force_mobile':
            return True
        elif mobile_mode == 'force_desktop':
            return False
        else:
            # Автоматическое определение
            return self.is_mobile_device
    
    def get_device_info(self):
        """Возвращает подробную информацию об устройстве"""
        return {
            'user_agent': self.user_agent,
            'is_mobile': self.is_mobile,
            'is_tablet': self.is_tablet,
            'is_mobile_device': self.is_mobile_device,
            'device_type': self.device_type,
            'screen_size_category': self.screen_size_category,
            'should_use_mobile_template': self.should_use_mobile_template(),
            'mobile_mode': session.get('mobile_mode', 'auto')
        }

# Глобальный экземпляр детектора
_mobile_detector = None

def get_mobile_detector():
    """Возвращает экземпляр MobileDetector для текущего запроса"""
    global _mobile_detector
    if _mobile_detector is None or (request and _mobile_detector.user_agent != request.headers.get('User-Agent', '')):
        _mobile_detector = MobileDetector()
    return _mobile_detector

def is_mobile_device(user_agent=None):
    """
    Простая функция для определения мобильного устройства
    (для обратной совместимости)
    """
    if user_agent:
        # Создаем временный детектор с переданным user-agent
        temp_detector = MobileDetector()
        temp_detector.user_agent = user_agent
        return temp_detector.is_mobile_device
    else:
        return get_mobile_detector().is_mobile_device

def mobile_optimized_render_template(template_name, **context):
    """
    Рендерит шаблон с мобильной оптимизацией
    (интеграция с MobileTemplateManager)
    """
    from flask import render_template
    
    # Добавляем мобильную информацию в контекст
    detector = get_mobile_detector()
    mobile_context = {
        'is_mobile': detector.is_mobile,
        'is_tablet': detector.is_tablet,
        'is_mobile_device': detector.is_mobile_device,
        'device_type': detector.device_type,
        'screen_size_category': detector.screen_size_category,
        'device_info': detector.get_device_info()
    }
    
    context.update(mobile_context)
    return render_template(template_name, **context)

def setup_mobile_detection(app):
    """
    Настраивает систему определения мобильных устройств
    (интеграция с Flask приложением)
    """
    
    @app.before_request
    def detect_device():
        """Middleware для определения устройства"""
        detector = get_mobile_detector()
        g.is_mobile = detector.is_mobile
        g.is_tablet = detector.is_tablet
        g.is_mobile_device = detector.is_mobile_device
        g.device_type = detector.device_type
        g.screen_size_category = detector.screen_size_category
    
    @app.context_processor
    def inject_mobile_context():
        """Добавляет мобильный контекст в все шаблоны"""
        detector = get_mobile_detector()
        return {
            'is_mobile': detector.is_mobile,
            'is_tablet': detector.is_tablet,
            'is_mobile_device': detector.is_mobile_device,
            'device_type': detector.device_type,
            'screen_size_category': detector.screen_size_category
        }
    
    # Добавляем функции в Jinja2 (БЕЗ создания роутов - они уже есть в mobile_integration.py)
    app.jinja_env.globals.update(
        is_mobile_device=lambda: get_mobile_detector().is_mobile_device,
        get_device_type=lambda: get_mobile_detector().device_type,
        get_country_code=get_country_code,
        is_rtl_language=is_rtl_language
    )
    
    app.logger.info("✅ Mobile detection system initialized")

def get_country_code(lang_code):
    """Возвращает код страны для флага"""
    lang_to_country = {
        'en': 'gb', 'nl': 'nl', 'ru': 'ru', 'uk': 'ua',
        'es': 'es', 'pt': 'pt', 'tr': 'tr', 'fa': 'ir'
    }
    return lang_to_country.get(lang_code, lang_code)

def is_rtl_language(lang_code):
    """Определяет RTL языки"""
    rtl_languages = ['fa', 'ar', 'he', 'ur']
    return lang_code in rtl_languages

# Функции для статистики (используются в welcome экране)
def get_user_stats():
    """Получает статистику пользователя"""
    from flask_login import current_user
    
    user_data = {}
    if current_user.is_authenticated:
        try:
            from models import UserProgress
            user_progress = UserProgress.query.filter_by(user_id=current_user.id).all()
            completed_lessons = len([p for p in user_progress if p.completed])
            
            user_data = {
                'name': current_user.username or current_user.email.split('@')[0],
                'email': current_user.email,
                'completed_lessons': completed_lessons,
                'total_progress': len(user_progress),
                'level': min(completed_lessons // 10 + 1, 10),
                'experience_points': completed_lessons * 10,
                'next_level_progress': (completed_lessons % 10) * 10,
                'streak_days': getattr(current_user, 'streak_days', 0),
                'total_study_time': getattr(current_user, 'total_study_time', 0)
            }
        except Exception as e:
            current_app.logger.warning(f"Error getting user stats: {e}")
            user_data = {
                'name': current_user.email.split('@')[0] if current_user.email else 'Student',
                'email': current_user.email,
                'completed_lessons': 0,
                'level': 1,
                'experience_points': 0,
                'next_level_progress': 0,
                'streak_days': 0,
                'total_study_time': 0
            }
    
    return user_data

def get_app_stats():
    """Получает общую статистику приложения"""
    try:
        from models import Module, Lesson, User
        
        stats = {
            'total_modules': Module.query.count(),
            'total_lessons': Lesson.query.count(),
            'total_users': User.query.count(),
            'supported_languages': len(current_app.config.get('SUPPORTED_LANGUAGES', []))
        }
    except Exception as e:
        current_app.logger.warning(f"Error getting app stats: {e}")
        stats = {
            'total_modules': 50,
            'total_lessons': 500,
            'total_users': 1200,
            'supported_languages': 8
        }
    
    return stats