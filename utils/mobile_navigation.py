# utils/mobile_navigation.py
"""
Конфигурации мобильной навигации для разных типов страниц
Система навигации для приложения Become a Tandarts
"""

from flask import url_for, request, g
from models import db, Subject, Module


class MobileNavigationConfig:
    """Конфигуратор мобильной навигации"""
    
    # Базовые конфигурации для разных типов страниц
    CONFIGS = {
        # Главные страницы
        'welcome': {
            'show_bottom_nav': True,
            'show_back_button': False,
            'show_profile_button': True,
            'show_settings_button': True,
            'show_language_selector': True,
            'show_progress': False,
            'page_title': None,  # Использует заголовок из шаблона
            'breadcrumbs': None,
            'show_logo': True,
            'logo_url': '/static/images/logo.png'
        },
        
        'learning_map': {
            'show_bottom_nav': True,
            'show_back_button': False,
            'show_profile_button': True,
            'show_settings_button': True,
            'show_language_selector': False,
            'show_progress': False,
            'page_title': 'learning_map',
            'breadcrumbs': None,
            'show_logo': False,
            'logo_url': None
        },
        
        # Страницы обучения
        'subject_view': {
            'show_bottom_nav': True,
            'show_back_button': True,
            'show_profile_button': False,
            'show_settings_button': False,
            'show_language_selector': False,
            'show_progress': False,
            'page_title': None,  # Динамический заголовок
            'breadcrumbs': True,  # Динамические breadcrumbs
            'show_logo': False,
            'logo_url': None
        },
        
        'module_view': {
            'show_bottom_nav': True,
            'show_back_button': True,
            'show_profile_button': False,
            'show_settings_button': False,
            'show_language_selector': False,
            'show_progress': True,  # Прогресс модуля
            'page_title': None,
            'breadcrumbs': True,
            'show_logo': False,
            'logo_url': None
        },
        
        'lesson': {
            'show_bottom_nav': True,
            'show_back_button': True,
            'show_profile_button': False,
            'show_settings_button': False,
            'show_language_selector': False,
            'show_progress': True,  # Прогресс урока
            'page_title': None,
            'breadcrumbs': True,
            'show_logo': False,
            'logo_url': None
        },
        
        # Страницы тестов
        'test_setup': {
            'show_bottom_nav': True,
            'show_back_button': True,
            'show_profile_button': False,
            'show_settings_button': False,
            'show_language_selector': False,
            'show_progress': False,
            'page_title': 'test_preparation',
            'breadcrumbs': True,
            'show_logo': False,
            'logo_url': None
        },
        
        'test_question': {
            'show_bottom_nav': False,  # Убираем во время теста для фокуса
            'show_back_button': False,  # Нельзя выйти из теста
            'show_profile_button': False,
            'show_settings_button': False,
            'show_language_selector': False,
            'show_progress': True,  # Прогресс теста
            'page_title': 'test_in_progress',
            'breadcrumbs': False,
            'show_logo': False,
            'logo_url': None
        },
        
        'test_result': {
            'show_bottom_nav': True,
            'show_back_button': False,  # Нельзя вернуться к тесту
            'show_profile_button': True,
            'show_settings_button': False,
            'show_language_selector': False,
            'show_progress': False,
            'page_title': 'test_results',
            'breadcrumbs': False,
            'show_logo': False,
            'logo_url': None
        },
        
        # Виртуальные пациенты
        'virtual_patient_list': {
            'show_bottom_nav': True,
            'show_back_button': False,
            'show_profile_button': True,
            'show_settings_button': False,
            'show_language_selector': False,
            'show_progress': False,
            'page_title': 'virtual_patients',
            'breadcrumbs': None,
            'show_logo': False,
            'logo_url': None
        },
        
        'virtual_patient_interact': {
            'show_bottom_nav': False,  # Полное погружение
            'show_back_button': True,
            'show_profile_button': False,
            'show_settings_button': False,
            'show_language_selector': False,
            'show_progress': True,  # Прогресс сценария
            'page_title': None,
            'breadcrumbs': False,
            'show_logo': False,
            'logo_url': None
        },
        
        # Страницы аутентификации
        'login': {
            'show_bottom_nav': False,
            'show_back_button': True,
            'show_profile_button': False,
            'show_settings_button': False,
            'show_language_selector': True,
            'show_progress': False,
            'page_title': 'sign_in',
            'breadcrumbs': False,
            'show_logo': False,
            'logo_url': None
        },
        
        'register': {
            'show_bottom_nav': False,
            'show_back_button': True,
            'show_profile_button': False,
            'show_settings_button': False,
            'show_language_selector': True,
            'show_progress': False,
            'page_title': 'sign_up',
            'breadcrumbs': False,
            'show_logo': False,
            'logo_url': None
        },
        
        # AI чат
        'ai_chat': {
            'show_bottom_nav': True,
            'show_back_button': False,
            'show_profile_button': False,
            'show_settings_button': True,
            'show_language_selector': False,
            'show_progress': False,
            'page_title': 'ai_assistant',
            'breadcrumbs': False,
            'show_logo': False,
            'logo_url': None
        },
        
        # Настройки и профиль
        'settings': {
            'show_bottom_nav': True,
            'show_back_button': True,
            'show_profile_button': False,
            'show_settings_button': False,
            'show_language_selector': True,
            'show_progress': False,
            'page_title': 'settings',
            'breadcrumbs': False,
            'show_logo': False,
            'logo_url': None
        },
        
        'profile': {
            'show_bottom_nav': True,
            'show_back_button': True,
            'show_profile_button': False,
            'show_settings_button': True,
            'show_language_selector': False,
            'show_progress': False,
            'page_title': 'profile',
            'breadcrumbs': False,
            'show_logo': False,
            'logo_url': None
        }
    }
    
    @classmethod
    def get_config(cls, page_type, **overrides):
        """
        Получает конфигурацию навигации для типа страницы
        
        Args:
            page_type (str): Тип страницы из CONFIGS
            **overrides: Переопределения конфигурации
            
        Returns:
            dict: Конфигурация навигации
        """
        config = cls.CONFIGS.get(page_type, cls.CONFIGS['welcome']).copy()
        config.update(overrides)
        return config
    
    @classmethod
    def generate_breadcrumbs(cls, request, lang, custom_items=None):
        """
        Генерирует breadcrumbs на основе текущего маршрута
        
        Args:
            request: Flask request объект
            lang (str): Текущий язык
            custom_items (list, optional): Кастомные элементы breadcrumbs
            
        Returns:
            list: Список breadcrumbs
        """
        if custom_items:
            return custom_items
            
        breadcrumbs = []
        
        # Определяем breadcrumbs на основе endpoint
        endpoint = request.endpoint
        view_args = request.view_args or {}
        
        # Всегда добавляем главную страницу
        breadcrumbs.append({
            'title': 'home',
            'url': url_for('mobile.welcome', lang=lang)
        })
        
        # Логика для разных разделов
        if 'learning' in endpoint or 'module' in endpoint or 'lesson' in endpoint or 'subject' in endpoint:
            breadcrumbs.append({
                'title': 'learning_map',
                'url': url_for('mobile.subjects_view', lang=lang)
            })
            
            if 'subject_id' in view_args:
                # Добавляем предмет
                subject_title = get_subject_title(view_args['subject_id'], lang)
                breadcrumbs.append({
                    'title': subject_title,
                    'url': url_for('subject_view_bp.view_subject', 
                                  subject_id=view_args['subject_id'], lang=lang)
                })
                
            if 'module_id' in view_args:
                # Добавляем модуль
                module_title = get_module_title(view_args['module_id'], lang)
                breadcrumbs.append({
                    'title': module_title,
                    'url': url_for('modules_bp.view_module', 
                                  module_id=view_args['module_id'], lang=lang)
                })
        
        elif 'test' in endpoint:
            breadcrumbs.append({
                'title': 'tests',
                'url': url_for('mobile.tests', lang=lang)
            })
            
        elif 'virtual_patient' in endpoint:
            breadcrumbs.append({
                'title': 'virtual_patients',
                'url': url_for('virtual_patient_bp.scenarios_list', lang=lang)
            })
        
        return breadcrumbs


def get_subject_title(subject_id, lang):
    """
    Получает заголовок предмета по ID из базы данных
    
    Args:
        subject_id (int): ID предмета
        lang (str): Язык для локализации
        
    Returns:
        str: Заголовок предмета или заглушка
    """
    try:
        subject = Subject.query.get(subject_id)
        if subject:
            # Возвращаем локализованное название если есть
            return getattr(subject, f'name_{lang}', subject.name or f'Subject {subject_id}')
        return f'Subject {subject_id}'
    except Exception:
        return f'Subject {subject_id}'


def get_module_title(module_id, lang):
    """
    Получает заголовок модуля по ID из базы данных
    
    Args:
        module_id (int): ID модуля
        lang (str): Язык для локализации
        
    Returns:
        str: Заголовок модуля или заглушка
    """
    try:
        module = Module.query.get(module_id)
        if module:
            # Возвращаем локализованное название если есть
            return getattr(module, f'title_{lang}', module.title or f'Module {module_id}')
        return f'Module {module_id}'
    except Exception:
        return f'Module {module_id}'


def get_active_nav_item(endpoint):
    """
    Определяет активный элемент навигации на основе endpoint
    
    Args:
        endpoint (str): Flask endpoint
        
    Returns:
        str: Ключ активного элемента навигации
    """
    # Маппинг endpoint'ов на навигационные элементы
    endpoint_mapping = {
        # Home
        'mobile.welcome': 'home',
        'main.index': 'home',
        
        # Learning
        'mobile.learning_map': 'learning',
        'mobile.subjects_view': 'learning', 
        'mobile.subject_view': 'learning',
        'mobile.lesson_view': 'learning',
        'mobile.module_view': 'learning',
        'learning_map.learning_map_view': 'learning',
        'subjects.subject_detail': 'learning',
        'lessons.lesson_detail': 'learning',
        'modules_bp.module_view': 'learning',
        
        # Tests
        'mobile.tests': 'tests',
        'tests.test_list': 'tests',
        'tests.test_detail': 'tests',
        
        # Virtual Patients
        'virtual_patient_bp.scenarios_list': 'patients',
        'virtual_patient_bp.interact': 'patients',
        'virtual_patient_bp.scenario_detail': 'patients',
        
        # AI
        'ai.ai_chat': 'ai',
        'ai.mobile_chat': 'ai',
        'mobile.ai_chat': 'ai'
    }
    
    # Проверяем точное совпадение
    if endpoint in endpoint_mapping:
        return endpoint_mapping[endpoint]
    
    # Проверяем частичные совпадения
    for pattern, nav_item in endpoint_mapping.items():
        if pattern in endpoint:
            return nav_item
    
    return 'home'  # По умолчанию 