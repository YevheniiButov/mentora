# app.py

import os
import time
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, flash, render_template, redirect, url_for, g, request, session, jsonify, current_app
from flask_login import current_user
from flask_migrate import Migrate
from werkzeug.middleware.proxy_fix import ProxyFix
import sys
import os

# Условный импорт termios только для Unix-систем
try:
    import termios
except ImportError:
    termios = None

# Добавляем текущую директорию в PYTHONPATH
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from translations_new import setup_translations
from utils.subtopics import create_slug, update_lesson_subtopics, reorder_subtopic_lessons
from utils.mobile_navigation import MobileNavigationConfig, get_active_nav_item
from mobile_integration import init_mobile_integration
from utils.mobile_helpers import init_mobile_helpers
from flask import send_from_directory, Response

# Import extensions
from extensions import db, login_manager, bcrypt, babel, cache, csrf

# Import models
from models import (
    User, Module, Lesson, UserProgress, Subject, LearningPath, VirtualPatientScenario,
    AssessmentCategory, AssessmentQuestion, PreAssessmentAttempt, PreAssessmentAnswer, LearningPlan
)

# Import routes
from routes.main_routes import main_bp
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.admin import admin_unified_bp  # Новая единая админка
from routes.forum_routes import forum_bp
from routes.virtual_patient_routes import virtual_patient_bp
from routes.api_routes import api_bp
from routes.tests_routes import tests_bp
from routes.learning_map_routes import learning_map_bp
from routes.dashboard_routes import dashboard_bp
from routes.modules_routes import modules_bp
from routes.subject_view_routes import subject_view_bp
from routes.mobile_routes import mobile_bp
from routes.ai_routes import ai_bp
from routes.assessment_routes import assessment_bp

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Языковые настройки
SUPPORTED_LANGUAGES = ['en', 'ru', 'nl', 'uk', 'es', 'pt', 'tr', 'fa', 'ar']
DEFAULT_LANGUAGE = 'en'

def fromjson_filter(json_string):
    """Преобразует строку JSON в объект Python."""
    if isinstance(json_string, str):
        try:
            return json.loads(json_string)
        except json.JSONDecodeError:
            return None
    return json_string

def register_template_filters(app):
    """Регистрирует пользовательские фильтры шаблонов Jinja2."""
    app.jinja_env.filters['fromjson'] = fromjson_filter

# CLI команды для импорта контента
def import_cards_from_folder():
    """Импортирует карточки и тесты из папки cards/ в базу данных"""
    from pathlib import Path
    
    cards_path = Path('cards')
    if not cards_path.exists():
        print(f"❌ Directory 'cards' not found at {cards_path.absolute()}")
        return
    
    print(f"📂 Importing from: {cards_path.absolute()}")
    
    # Статистика импорта
    stats = {
        'modules_created': 0,
        'lessons_created': 0,
        'cards_imported': 0,
        'tests_imported': 0,
        'errors': 0
    }
    
    try:
        # Проходим по всем папкам в cards/
        for topic_folder in cards_path.iterdir():
            if not topic_folder.is_dir():
                continue
                
            topic_name = topic_folder.name
            print(f"\n📁 Processing folder: {topic_name}")
            
            # Импортируем learning_cards.json
            cards_file = topic_folder / 'learning_cards.json'
            if cards_file.exists():
                print(f"  📚 Found learning_cards.json")
                try:
                    with open(cards_file, 'r', encoding='utf-8') as f:
                        cards_data = json.load(f)
                    
                    # Группируем карточки по module_title
                    modules_cards = {}
                    for card in cards_data:
                        module_title = card.get('module_title', topic_name.title())
                        if module_title not in modules_cards:
                            modules_cards[module_title] = []
                        modules_cards[module_title].append(card)
                    
                    # Создаем модули и уроки для карточек
                    for module_title, cards in modules_cards.items():
                        module = create_or_get_module(module_title, f"Module imported from {topic_name}")
                        stats['modules_created'] += 1
                        
                        for card in cards:
                            lesson = create_lesson_from_card(module, card)
                            stats['lessons_created'] += 1
                            stats['cards_imported'] += 1
                    
                    print(f"    ✅ Imported {len(cards_data)} learning cards")
                    
                except json.JSONDecodeError as e:
                    print(f"    ❌ JSON Error in {cards_file}: {e}")
                    print(f"    ⚠️  Skipping this file and continuing...")
                    stats['errors'] += 1
                    continue
                except Exception as e:
                    print(f"    ❌ Error processing {cards_file}: {e}")
                    stats['errors'] += 1
                    continue
            
            # Импортируем tests.json
            tests_file = topic_folder / 'tests.json'
            if tests_file.exists():
                print(f"  🧪 Found tests.json")
                try:
                    with open(tests_file, 'r', encoding='utf-8') as f:
                        tests_data = json.load(f)
                    
                    # Группируем тесты по module_title
                    modules_tests = {}
                    for test in tests_data:
                        module_title = test.get('module_title', topic_name.title())
                        if module_title not in modules_tests:
                            modules_tests[module_title] = []
                        modules_tests[module_title].append(test)
                    
                    # Создаем модули и уроки для тестов
                    for module_title, tests in modules_tests.items():
                        module = create_or_get_module(module_title, f"Module imported from {topic_name}")
                        
                        for test in tests:
                            lesson = create_lesson_from_test(module, test)
                            stats['lessons_created'] += 1
                            stats['tests_imported'] += 1
                    
                    print(f"    ✅ Imported {len(tests_data)} tests")
                    
                except json.JSONDecodeError as e:
                    print(f"    ❌ JSON Error in {tests_file}: {e}")
                    print(f"    ⚠️  Skipping this file and continuing...")
                    stats['errors'] += 1
                    continue
                except Exception as e:
                    print(f"    ❌ Error processing {tests_file}: {e}")
                    stats['errors'] += 1
                    continue
        
        # Сохраняем изменения
        db.session.commit()
        
        print(f"\n🎉 Import completed!")
        print(f"📊 Statistics:")
        print(f"   - Modules created: {stats['modules_created']}")
        print(f"   - Lessons created: {stats['lessons_created']}")
        print(f"   - Learning cards imported: {stats['cards_imported']}")
        print(f"   - Tests imported: {stats['tests_imported']}")
        if stats['errors'] > 0:
            print(f"   - ⚠️  Files with errors (skipped): {stats['errors']}")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Critical error during import: {e}")
        raise

def create_or_get_module(title, description=""):
    """Создает новый модуль или возвращает существующий"""
    module = Module.query.filter_by(title=title).first()
    
    if not module:
        # Получаем порядковый номер для нового модуля
        max_order = db.session.query(db.func.max(Module.order)).scalar() or 0
        
        # Создаем новый модуль
        module = Module(
            title=title,
            description=description,
            order=max_order + 1,
            module_type='education',
            is_premium=False
        )
        db.session.add(module)
        db.session.flush()  # Получаем ID модуля
        print(f"    ✨ Created new module: {title} (ID: {module.id})")
    else:
        print(f"    ✨ Using existing module: {title} (ID: {module.id})")
    
    return module

def create_lesson_from_card(module, card_data):
    """Создает урок из данных карточки с сохранением всех полей"""
    lesson_count = Lesson.query.filter_by(module_id=module.id).count()
    
    # Извлекаем module_title из карточки
    module_title = card_data.get('module_title', module.title)
    
    # Сохраняем ВСЮ карточку как JSON + дополнительные поля
    lesson = Lesson(
        title=card_data.get('question', f"Learning Card {lesson_count + 1}"),
        content=json.dumps(card_data, ensure_ascii=False),  # Полная карточка!
        content_type='learning_card',
        module_id=module.id,
        order=lesson_count + 1,
        subtopic=module_title,
        subtopic_slug=create_slug(module_title)
    )
    
    db.session.add(lesson)
    print(f"    📚 Created lesson: {lesson.title[:50]}... | Module Title: {module_title}")
    return lesson

def create_lesson_from_test(module, test_data):
    """Создает урок из данных теста с сохранением всех полей"""
    lesson_count = Lesson.query.filter_by(module_id=module.id).count()
    
    # Извлекаем module_title из теста
    module_title = test_data.get('module_title', module.title)
    
    # Сохраняем ВЕСЬ тест как JSON
    lesson = Lesson(
        title=test_data.get('question', f"Test Question {lesson_count + 1}"),
        content=json.dumps(test_data, ensure_ascii=False),  # Полный тест!
        content_type='test_question',
        module_id=module.id,
        order=lesson_count + 1,
        subtopic=module_title,
        subtopic_slug=create_slug(module_title)
    )
    
    db.session.add(lesson)
    print(f"    🧪 Created lesson: {lesson.title[:50]}... | Module Title: {module_title}")
    return lesson

def clear_imported_content():
    """Удаляет все импортированные данные"""
    print("⚠️  Clearing all imported content...")
    
    # Удаляем все уроки
    lessons_count = Lesson.query.count()
    Lesson.query.delete()
    print(f"   🗑️  Deleted {lessons_count} lessons")
    
    # Удаляем все модули
    modules_count = Module.query.count()
    Module.query.delete()
    print(f"   🗑️  Deleted {modules_count} modules")
    
    db.session.commit()
    print("✅ Content cleared successfully!")

def create_app(test_config=None):
    """Создает и настраивает приложение Flask."""
    app = Flask(
        __name__,
        static_folder="static",
        static_url_path="/static",
        instance_relative_config=True
    )
    
    # Импорт blueprints в начале функции
    from routes import (
        auth_bp, main_bp, learning_map_bp, lesson_bp, modules_bp, 
        tests_bp, content_bp, forum_bp, virtual_patient_bp, subject_view_bp,
        api_bp, admin_bp, admin_unified_bp, ai_bp, mobile_bp,
        virtual_patient_api_bp, content_nav_bp, dashboard_bp, assessment_bp
    )
    
    # Загрузка конфигурации
    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)
    
    # Настройка конфигурации приложения
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key_replace_in_production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SUPPORTED_LANGUAGES'] = SUPPORTED_LANGUAGES
    app.config['DEFAULT_LANGUAGE'] = DEFAULT_LANGUAGE
    app.config['CACHE_TYPE'] = 'SimpleCache'
    app.config['SESSION_COOKIE_NAME'] = 'tandarts_session'  # Добавлено: уникальное имя для cookie сессии
    app.config['SESSION_COOKIE_SECURE'] = False  # Установите True в production с HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)  # Увеличено время жизни сессии
    
    # Настройки CSRF для предотвращения истечения токенов
    app.config['WTF_CSRF_TIME_LIMIT'] = 7200  # 2 часа вместо стандартного 1 часа
    app.config['WTF_CSRF_CHECK_DEFAULT'] = True
    app.config['WTF_CSRF_METHODS'] = ['POST', 'PUT', 'PATCH', 'DELETE']
    
    # Настройка поддержки прокси для правильных URL
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    
    # Инициализация расширений
    db.init_app(app)
    migrate = Migrate(app, db)
    bcrypt.init_app(app)
    csrf.init_app(app)
    cache.init_app(app)
    
    # Настройка логина с измененными параметрами
    login_manager.init_app(app)
    login_manager.login_view = 'auth_bp.login'
    login_manager.session_protection = 'basic'  # Изменено с 'strong' на 'basic' для отладки
    login_manager.login_message = "Please log in to access this page."
    login_manager.refresh_view = 'auth_bp.login'
    login_manager.needs_refresh_message = "Please log in again to confirm your identity"
    
    # Регистрация blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(learning_map_bp)
    app.register_blueprint(lesson_bp)
    app.register_blueprint(modules_bp)
    app.register_blueprint(tests_bp)
    app.register_blueprint(content_bp)
    app.register_blueprint(forum_bp)
    app.register_blueprint(virtual_patient_bp)
    app.register_blueprint(subject_view_bp)
    app.register_blueprint(assessment_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(admin_unified_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(mobile_bp)
    app.register_blueprint(virtual_patient_api_bp)
    app.register_blueprint(content_nav_bp)
    app.register_blueprint(dashboard_bp)
    
    @login_manager.user_loader
    def load_user(user_id):
        try:
            return db.session.get(User, int(user_id))
        except Exception as e:
            app.logger.warning(f"Error loading user {user_id}: {e}")
            return None
    
    # Добавляем функции перевода в глобальное пространство имен Jinja2
    setup_translations(app)
    # ОБЪЕДИНЕННЫЙ обработчик для языка и безопасности сессии
    @app.before_request
    def handle_language_and_redirect():
        if getattr(g, 'force_desktop', False):
            return None  # Не делаем редирект, не меняем язык, не трогаем сессию
        # Игнорируем статические файлы, API запросы и т.д.
        if request.path.startswith('/static/') or request.path == '/routes' or request.path == '/':
            return None
        
        # Получение языка из URL-параметра
        lang_from_url = request.view_args.get('lang') if request.view_args else None
        
        # Валидация и установка языка в g
        if lang_from_url and lang_from_url in SUPPORTED_LANGUAGES:
            g.lang = lang_from_url
        else:
            # Если в URL нет валидного языка, берем из сессии или accept_languages
            g.lang = session.get('lang') \
                    or request.accept_languages.best_match(SUPPORTED_LANGUAGES) \
                    or DEFAULT_LANGUAGE
        
        # Обновляем сессию, только если язык отличается
        if session.get('lang') != g.lang:
            session['lang'] = g.lang
            
        # Проверяем наличие языкового префикса в URL и делаем перенаправление если нужно
        path_parts = request.path.lstrip('/').split('/')
        if not path_parts or path_parts[0] not in SUPPORTED_LANGUAGES:
            # Создаем новый URL с языковым префиксом
            new_url = f"/{g.lang}{request.path}"
            
            # Сохраняем параметры запроса
            if request.query_string:
                new_url = f"{new_url}?{request.query_string.decode('utf-8')}"
            
            # Перенаправляем на URL с языком
            return redirect(new_url)
        
        # Безопасность сессии - упрощенный вариант без перезаписи _creation_time при каждом запросе
        if '_creation_time' not in session:
            session['_creation_time'] = datetime.now().isoformat()
            
        # Отладочная информация для сессии
        if 'user_id' in session:
            app.logger.debug(f"Session active for user_id: {session['user_id']}")
    
    # Обработчик для выбора языка в babel
    def get_locale():
        return g.get('lang', DEFAULT_LANGUAGE)

    babel.init_app(app, locale_selector=get_locale)
    
    # Улучшенный обработчик для неавторизованных запросов
    @login_manager.unauthorized_handler
    def unauthorized():
        # Использование языка из g для сохранения контекста, иначе из сессии
        lang = g.get('lang', session.get('lang', DEFAULT_LANGUAGE))
        app.logger.warning(f"Unauthorized access attempt to: {request.path}, redirecting to login")
        # Сохраняем URL в параметре next для возврата после авторизации
        return redirect(url_for('auth_bp.login', lang=lang, next=request.path))
    
    # Добавление маршрута для отладки сессии
    @app.route('/debug-session')
    def debug_session():
        from flask_login import current_user
        debug_info = {
            'session_data': {k: v for k, v in session.items() if k != '_csrf_token'},
            'is_authenticated': hasattr(current_user, 'is_authenticated') and current_user.is_authenticated,
            'user_id': getattr(current_user, 'id', None) if hasattr(current_user, 'id') else None,
            'request_path': request.path,
            'g_data': {'lang': g.get('lang', 'not set')}
        }
        
        return jsonify(debug_info)
    
    # Регистрация CLI команд
    @app.cli.command()
    def import_content():
        """Импортирует контент из JSON файлов в БД"""
        print("🚀 Starting content import...")
        import_cards_from_folder()
        print("✅ Content import completed!")
    
    @app.cli.command()
    def clear_content():
        """Очищает весь импортированный контент"""
        print("🗑️  Starting content cleanup...")
        clear_imported_content()
        print("✅ Content cleanup completed!")
    
    @app.cli.command()
    def show_modules():
        """Показывает все модули в БД"""
        modules = Module.query.all()
        print(f"\n📚 Found {len(modules)} modules in database:")
        for module in modules:
            lessons_count = Lesson.query.filter_by(module_id=module.id).count()
            print(f"   - {module.id}: {module.title} ({lessons_count} lessons)")

    @app.cli.command()
    def debug_lessons():
        """Показывает структуру уроков в БД для отладки"""
        lessons = Lesson.query.limit(10).all()
        print(f"\n📚 Checking {len(lessons)} lessons structure:")
        
        for lesson in lessons:
            print(f"\n{'='*50}")
            print(f"Lesson ID: {lesson.id}")
            print(f"Title: {lesson.title}")
            print(f"Content Type: {lesson.content_type}")
            print(f"Module ID: {lesson.module_id}")
            
            if lesson.content:
                try:
                    content_data = json.loads(lesson.content)
                    print(f"Content keys: {list(content_data.keys())}")
                    
                    # Проверяем разные структуры
                    if 'cards' in content_data and content_data['cards']:
                        print(f"Cards count: {len(content_data['cards'])}")
                        first_card = content_data['cards'][0]
                        print(f"First card module_title: {first_card.get('module_title', 'NOT FOUND')}")
                        print(f"First card question: {first_card.get('question', 'NO QUESTION')[:50]}...")
                    
                    elif 'questions' in content_data and content_data['questions']:
                        print(f"Questions count: {len(content_data['questions'])}")
                        first_question = content_data['questions'][0]
                        print(f"First question module_title: {first_question.get('module_title', 'NOT FOUND')}")
                        print(f"First question text: {first_question.get('question', 'NO QUESTION')[:50]}...")
                    
                    else:
                        print(f"Unknown content structure")
                        
                except json.JSONDecodeError as e:
                    print(f"JSON Error: {e}")
                    print(f"Raw content preview: {lesson.content[:100]}...")
            else:
                print("No content")      
    @app.cli.command()
    def update_subtopics():
        """Обновляет поля subtopic и subtopic_slug у всех уроков"""
        print("🔄 Updating subtopics in all lessons...")
        
        # Импортируем необходимые функции
        import re
        
        def create_slug(text):
            """Создаёт унифицированный слаг из текста"""
            if not text:
                return ""
            return re.sub(r'[^a-z0-9]+', '_', text.lower()).strip('_')
        
        # Получаем все уроки
        lessons = Lesson.query.all()
        stats = {
            'total': len(lessons),
            'updated': 0,
            'skipped': 0,
            'errors': 0,
            'subtopics': {}
        }
        
        # Словарь для определения порядка внутри подтем
        subtopic_counters = {}
        
        for lesson in lessons:
            try:
                # Извлекаем module_title из контента
                if not lesson.content:
                    print(f"⚠️ Lesson {lesson.id} has no content")
                    stats['skipped'] += 1
                    continue
                    
                content_data = json.loads(lesson.content)
                module_title = None
                
                # Проверяем различные структуры данных
                if 'module_title' in content_data:
                    module_title = content_data.get('module_title')
                elif 'type' in content_data and content_data.get('type') in ['learning', 'test']:
                    module_title = content_data.get('module_title')
                elif 'cards' in content_data and content_data['cards']:
                    module_title = content_data['cards'][0].get('module_title')
                elif 'questions' in content_data and content_data['questions']:
                    module_title = content_data['questions'][0].get('module_title')
                
                if not module_title:
                    print(f"⚠️ Lesson {lesson.id} has no module_title")
                    stats['skipped'] += 1
                    continue
                    
                # Формируем слаг
                slug = create_slug(module_title)
                
                # Определяем порядок внутри подтемы
                if slug not in subtopic_counters:
                    subtopic_counters[slug] = 0
                subtopic_counters[slug] += 1
                
                # Обновляем поля
                lesson.subtopic = module_title
                lesson.subtopic_slug = slug
                lesson.subtopic_order = subtopic_counters[slug]
                
                # Обновляем статистику
                stats['updated'] += 1
                if slug not in stats['subtopics']:
                    stats['subtopics'][slug] = {
                        'name': module_title,
                        'count': 0
                    }
                stats['subtopics'][slug]['count'] += 1
                    
            except Exception as e:
                print(f"❌ Error updating lesson {lesson.id}: {e}")
                stats['errors'] += 1
        
        # Сохраняем изменения
        db.session.commit()
        
        print(f"✅ Updated {stats['updated']} of {stats['total']} lessons with subtopic information")
        print(f"⚠️ Skipped: {stats['skipped']} | ❌ Errors: {stats['errors']}")
        
        print("\n📊 Found subtopics:")
        for slug, data in stats['subtopics'].items():
            print(f"   - '{data['name']}' ({slug}): {data['count']} lessons")
    
    @app.cli.command()
    def debug_subtopics():
        """Показывает структуру подтем и их слагов"""
        modules = Module.query.all()
        print(f"\n📚 Analyzing subtopics in {len(modules)} modules:")
        
        for module in modules:
            print(f"\n📂 MODULE: {module.id} - {module.title}")
            
            # Получаем уникальные подтемы из БД
            subtopics_data = db.session.query(
                Lesson.subtopic,
                Lesson.subtopic_slug,
                db.func.count(Lesson.id).label('total_lessons')
            ).filter(
                Lesson.module_id == module.id,
                Lesson.subtopic.isnot(None)
            ).group_by(
                Lesson.subtopic,
                Lesson.subtopic_slug
            ).all()
            
            if subtopics_data:
                print(f"   Found {len(subtopics_data)} subtopics:")
                for subtopic_name, subtopic_slug, total_lessons in subtopics_data:
                    print(f"   - Subtopic: '{subtopic_name}' (slug: '{subtopic_slug}')")
                    print(f"     Lessons: {total_lessons}")
                    
                    # Показываем типы контента в подтеме
                    lesson_types = db.session.query(
                        Lesson.content_type, 
                        db.func.count(Lesson.id)
                    ).filter(
                        Lesson.module_id == module.id,
                        Lesson.subtopic_slug == subtopic_slug
                    ).group_by(Lesson.content_type).all()
                    
                    for content_type, count in lesson_types:
                        print(f"       {content_type}: {count}")
            else:
                print("   ⚠️ No subtopics found")
    
    @app.cli.command()
    def reorder_all_subtopics():
        """Переупорядочивает уроки во всех подтемах, чередуя карточки и тесты"""
        print("🔄 Reordering lessons in all subtopics...")
        
        # Получаем все модули
        modules = Module.query.all()
        total_updated = 0
        
        for module in modules:
            print(f"\n📂 MODULE: {module.id} - {module.title}")
            
            # Получаем все подтемы модуля
            subtopics_data = db.session.query(
                Lesson.subtopic,
                Lesson.subtopic_slug,
                db.func.count(Lesson.id).label('total_lessons')
            ).filter(
                Lesson.module_id == module.id,
                Lesson.subtopic.isnot(None)
            ).group_by(
                Lesson.subtopic,
                Lesson.subtopic_slug
            ).all()
            
            for subtopic_name, subtopic_slug, total_lessons in subtopics_data:
                print(f"   - Reordering subtopic: '{subtopic_name}'")
                
                # Получаем все уроки подтемы
                lessons = Lesson.query.filter_by(
                    module_id=module.id,
                    subtopic_slug=subtopic_slug
                ).all()
                
                # Разделяем на карточки и тесты
                learning_cards = [l for l in lessons if l.content_type == 'learning_card']
                tests = [l for l in lessons if l.content_type == 'test_question']
                
                # Сортируем по имеющемуся порядку
                learning_cards.sort(key=lambda x: x.order)
                tests.sort(key=lambda x: x.order)
                
                # Чередуем карточки и тесты
                new_order = []
                cards_index = 0
                tests_index = 0
                
                # Берем по 2 карточки, затем 1 тест
                while cards_index < len(learning_cards) or tests_index < len(tests):
                    # Добавляем до 2 карточек
                    for _ in range(2):
                        if cards_index < len(learning_cards):
                            new_order.append(learning_cards[cards_index])
                            cards_index += 1
                    
                    # Добавляем 1 тест
                    if tests_index < len(tests):
                        new_order.append(tests[tests_index])
                        tests_index += 1
                
                # Обновляем порядок
                for i, lesson in enumerate(new_order):
                    lesson.subtopic_order = i + 1
                
                # Обновляем счетчик
                total_updated += len(new_order)
                print(f"     ✅ Updated {len(new_order)} lessons")
                
            # Сохраняем изменения после каждого модуля
            db.session.commit()
            
        print(f"\n🎉 Total updated lessons: {total_updated}")
    
    @app.cli.command()
    def reorder_subtopics():
        """Переупорядочивает уроки в определенной подтеме"""
        from utils.subtopics import reorder_subtopic_lessons
        
        print("📋 Available subtopics:")
        subtopics = db.session.query(
            Lesson.subtopic,
            Lesson.subtopic_slug,
            db.func.count(Lesson.id).label('total_lessons')
        ).filter(
            Lesson.subtopic.isnot(None)
        ).group_by(
            Lesson.subtopic,
            Lesson.subtopic_slug
        ).all()
        
        for i, (name, slug, count) in enumerate(subtopics, 1):
            print(f"{i:2}. {name} ({slug}) - {count} lessons")
        
        choice = input("\nChoose subtopic number (or 'q' to quit): ").strip()
        
        if choice.lower() == 'q':
            print("❌ Operation cancelled")
            return
            
        try:
            index = int(choice) - 1
            if 0 <= index < len(subtopics):
                selected_name, selected_slug, _ = subtopics[index]
                print(f"\n🔄 Reordering subtopic: {selected_name}")
                
                result = reorder_subtopic_lessons(selected_slug)
                
                if result['success']:
                    print(f"✅ Successfully reordered {result['reordered_count']} lessons")
                    if result['warnings']:
                        print("\n⚠️ Warnings:")
                        for warning in result['warnings']:
                            print(f"   - {warning}")
                else:
                    print(f"❌ Error: {result['error']}")
            else:
                print("❌ Invalid choice")
        except ValueError:
            print("❌ Please enter a valid number")

    # Инициализация мобильной интеграции
    init_mobile_integration(app)
    
    # Регистрация дополнительных соответствий шаблонов
    from mobile_integration import mobile_template_manager
    
    # Добавляем новые соответствия шаблонов
    mobile_template_manager.register_mobile_template('index.html', 'mobile/learning/welcome_mobile.html')
    mobile_template_manager.register_mobile_template('big-info.html', 'big-info_mobile.html')
    mobile_template_manager.register_mobile_template('demo.html', 'demo_mobile.html')
    
    print("✅ Mobile integration initialized with welcome screen")
    
    # Установка глобальных контекстных переменных для шаблонов
    @app.context_processor
    def inject_global_vars():
        def is_rtl_language(lang):
            """Проверяет, является ли язык языком с письмом справа налево"""
            rtl_languages = ['fa', 'ar', 'he']
            return lang in rtl_languages
        
        def get_country_code(lang_code):
            """Возвращает код страны для флага"""
            lang_to_country = {
                'en': 'gb', 'nl': 'nl', 'ru': 'ru', 'uk': 'ua',
                'es': 'es', 'pt': 'pt', 'tr': 'tr', 'fa': 'ir'
            }
            return lang_to_country.get(lang_code, lang_code)
        
        return dict(
            current_year=datetime.now().year,
            app_name="Become a Tandarts",
            supported_languages=SUPPORTED_LANGUAGES,
            config=app.config,
            is_rtl_language=is_rtl_language,
            get_country_code=get_country_code,
            current_app=current_app
        )
    
    # Функции для отображения геймификации в шаблонах
    @app.context_processor
    def inject_gamification_data():
        """Добавляет данные геймификации в контекст всех шаблонов"""
        
        def get_user_level():
            if current_user.is_authenticated:
                try:
                    from utils.gamification_engine import GamificationEngine
                    from extensions import db
                    gamification = GamificationEngine(db.session)
                    stats = gamification.get_or_create_user_stats(current_user.id)
                    return stats.current_level
                except:
                    return 1
            return 1
        
        def get_user_xp():
            if current_user.is_authenticated:
                try:
                    from utils.gamification_engine import GamificationEngine
                    from extensions import db
                    gamification = GamificationEngine(db.session)
                    stats = gamification.get_or_create_user_stats(current_user.id)
                    return stats.total_experience_points
                except:
                    return 0
            return 0
        
        def get_user_progress_to_next_level():
            if current_user.is_authenticated:
                try:
                    from utils.gamification_engine import GamificationEngine
                    from extensions import db
                    gamification = GamificationEngine(db.session)
                    stats = gamification.get_or_create_user_stats(current_user.id)
                    return stats.points_to_next_level
                except:
                    return 100
            return 100
        
        return dict(
            get_user_level=get_user_level,
            get_user_xp=get_user_xp,
            get_user_progress_to_next_level=get_user_progress_to_next_level
        )

    # Функции для мобильной навигации
    @app.context_processor
    def inject_navigation_helpers():
        """Добавляет помощники мобильной навигации в контекст всех шаблонов"""
        return {
            'get_navigation_config': MobileNavigationConfig.get_config,
            'generate_breadcrumbs': MobileNavigationConfig.generate_breadcrumbs,
            'get_active_nav_item': get_active_nav_item
        }

    print(f"Registered blueprint: {subject_view_bp.name} with url_prefix: {subject_view_bp.url_prefix}")

    @app.route('/routes')
    def list_routes():
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append({
                "endpoint": rule.endpoint,
                "methods": list(rule.methods),
                "route": str(rule)
            })
        return jsonify(routes)
    
    # Страница 404
    @app.errorhandler(404)
    def page_not_found(e):
        from utils.mobile_detection import get_mobile_detector
        detector = get_mobile_detector()
        
        # Получаем язык из g или сессии
        lang = getattr(g, 'lang', session.get('lang', app.config.get('DEFAULT_LANGUAGE', 'en')))
        g.current_language = lang  # Для совместимости с шаблонами
        
        if detector.is_mobile_device:
            return render_template('mobile/404.html', current_language=lang), 404
        else:
            return render_template('404.html', current_language=lang), 404
    
    # Страница 500
    @app.errorhandler(500)
    def internal_error(e):
        """Обработчик внутренних ошибок сервера."""
        lang = g.get('lang', session.get('lang', DEFAULT_LANGUAGE))
        
        # Логируем ошибку
        app.logger.error(f"Internal server error: {e}", exc_info=True)
        
        # Проверяем, является ли это AJAX-запросом
        if request.headers.get('Content-Type') == 'application/json' or \
           request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'error': 'Внутренняя ошибка сервера',
                'code': 500
            }), 500
        
        return render_template(
            'errors/500.html',
            lang=lang,
            t=lambda key, default=None: translations.get(lang, {}).get(key, default or key)
        ), 500

    @app.errorhandler(400)
    def bad_request(e):
        """Обработчик ошибок CSRF и других неправильных запросов."""
        lang = g.get('lang', session.get('lang', DEFAULT_LANGUAGE))
        
        # Проверяем, является ли это ошибкой CSRF
        error_description = str(e.description) if hasattr(e, 'description') else str(e)
        is_csrf_error = 'CSRF' in error_description or 'csrf' in error_description.lower()
        
        app.logger.warning(f"Bad request (400): {error_description}")
        
        # Если это AJAX-запрос
        if request.headers.get('Content-Type') == 'application/json' or \
           request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            if is_csrf_error:
                return jsonify({
                    'error': 'CSRF токен истек. Пожалуйста, обновите страницу.',
                    'code': 400,
                    'csrf_error': True,
                    'reload_required': True
                }), 400
            else:
                return jsonify({
                    'error': 'Неправильный запрос',
                    'code': 400
                }), 400
        
        # Для обычных запросов
        if is_csrf_error:
            flash('Время сессии истекло. Пожалуйста, повторите действие.', 'warning')
            return redirect(request.referrer or url_for('main_bp.index', lang=lang))
        
        return render_template(
            'errors/400.html',
            lang=lang,
            t=lambda key, default=None: translations.get(lang, {}).get(key, default or key)
        ), 400
    
    # Редирект на страницу с языком по умолчанию из корня
    @app.route('/')
    def index():
        return redirect(url_for('main_bp.home', lang=DEFAULT_LANGUAGE))
    
    # Регистрация пользовательских фильтров
    register_template_filters(app)
    
    # Инициализация БД (но НЕ загружаем JSON - это делается через CLI команды)
    with app.app_context():
        try:
            db.create_all()
            logger.info("✅ Database tables created successfully")
        except Exception as e:
            logger.error(f"❌ Error creating database tables: {e}")

    print("="*50)
    print("🌐 Flask application configured successfully!")
    print("💡 Available CLI commands:")
    print("   - flask import-content  : Import JSON files to database")
    print("   - flask clear-content   : Clear all imported content")
    print("   - flask show-modules    : Show all modules in database")
    print("="*50)

    return app

# Создание экземпляра приложения
app = create_app()

# Регистрируем фильтр после создания приложения
@app.template_filter('fromjson')
def fromjson_filter_global(value):
    """Jinja2 фильтр для преобразования JSON-строки в объект Python."""
    if value is None or value == '':
        return {}
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return {}

# ===== SERVICE WORKER =====
@app.route('/sw.js')
def service_worker():
    """Serve the Service Worker with proper headers"""
    try:
        # Try to serve the actual file
        response = app.send_static_file('sw.js')
        
        # Set proper headers for Service Worker
        response.headers['Content-Type'] = 'application/javascript'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['Service-Worker-Allowed'] = '/'
        
        return response
    except Exception as e:
        # Log error but still serve
        app.logger.warning(f"Service Worker file not found: {e}")
        
        # Return a minimal working Service Worker
        sw_content = '''
// Minimal Service Worker for Dental Academy
console.log('Service Worker: Loaded');

self.addEventListener('install', function(event) {
    console.log('Service Worker: Installing...');
    self.skipWaiting();
});

self.addEventListener('activate', function(event) {
    console.log('Service Worker: Activating...');
    event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', function(event) {
    // Let the browser handle all fetch requests
    return;
});
        '''
        
        response = Response(sw_content, mimetype='application/javascript')
        response.headers['Cache-Control'] = 'no-cache'
        response.headers['Service-Worker-Allowed'] = '/'
        
        return response

# ===== PWA MANIFEST =====
@app.route('/manifest.json')
def pwa_manifest():
    """Serve the PWA manifest with proper headers"""
    try:
        # Try to serve the actual file
        response = app.send_static_file('manifest.json')
        
        # Set proper headers for manifest
        response.headers['Content-Type'] = 'application/manifest+json'
        response.headers['Cache-Control'] = 'public, max-age=86400'  # Cache for 1 day
        
        return response
    except Exception as e:
        app.logger.warning(f"Manifest file not found: {e}")
        
        # Return a minimal working manifest
        manifest_data = {
            "name": "Dental Academy - Professional Training Platform",
            "short_name": "Dental Academy",
            "description": "Complete preparation for BIG dental examination in Netherlands",
            "start_url": "/",
            "scope": "/",
            "display": "standalone",
            "orientation": "portrait-primary",
            "theme_color": "#3ECDC1",
            "background_color": "#ffffff",
            "lang": "en",
            "icons": [
                {
                    "src": "/static/images/icon-192.png",
                    "sizes": "192x192",
                    "type": "image/png",
                    "purpose": "any"
                },
                {
                    "src": "/static/images/icon-512.png", 
                    "sizes": "512x512",
                    "type": "image/png",
                    "purpose": "any maskable"
                }
            ],
            "categories": ["education", "medical", "training"],
            "shortcuts": [
                {
                    "name": "Learning Map",
                    "url": "/learning-map",
                    "icons": [{"src": "/static/images/icon-192.png", "sizes": "192x192"}]
                },
                {
                    "name": "Practice Tests", 
                    "url": "/tests",
                    "icons": [{"src": "/static/images/icon-192.png", "sizes": "192x192"}]
                }
            ]
        }
        
        response = jsonify(manifest_data)
        response.headers['Content-Type'] = 'application/manifest+json'
        response.headers['Cache-Control'] = 'public, max-age=86400'
        
        return response

# ===== OFFLINE PAGE =====
@app.route('/offline')
def offline_page():
    """Serve offline fallback page"""
    try:
        # Try to serve offline.html if it exists
        return render_template('offline.html')
    except:
        # Return a simple offline page
        offline_html = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dental Academy - Offline</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            display: flex; 
            align-items: center; 
            justify-content: center; 
            min-height: 100vh; 
            margin: 0; 
            background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
            color: #374151;
            padding: 1rem;
        }
        .offline-container {
            text-align: center;
            padding: 3rem 2rem;
            background: white;
            border-radius: 16px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.1);
            max-width: 480px;
            width: 100%;
        }
        .offline-icon {
            font-size: 5rem;
            margin-bottom: 1.5rem;
            opacity: 0.8;
        }
        .offline-title {
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 1rem;
            color: #111827;
        }
        .offline-message {
            margin-bottom: 2rem;
            line-height: 1.6;
            color: #6b7280;
            font-size: 1.1rem;
        }
        .retry-btn {
            background: linear-gradient(135deg, #3ECDC1, #2BB6AC);
            color: white;
            border: none;
            padding: 1rem 2rem;
            border-radius: 12px;
            font-weight: 600;
            font-size: 1rem;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }
        .retry-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(62, 205, 193, 0.3);
        }
        .connection-status {
            margin-top: 1.5rem;
            padding: 1rem;
            background: #f9fafb;
            border-radius: 8px;
            font-size: 0.9rem;
            color: #6b7280;
        }
        .status-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            margin-right: 8px;
            background: #ef4444;
        }
        .status-indicator.online {
            background: #10b981;
        }
        @media (max-width: 480px) {
            .offline-container {
                padding: 2rem 1.5rem;
            }
            .offline-title {
                font-size: 1.5rem;
            }
            .offline-icon {
                font-size: 4rem;
            }
        }
    </style>
</head>
<body>
    <div class="offline-container">
        <div class="offline-icon">📱</div>
        <h1 class="offline-title">You're Offline</h1>
        <p class="offline-message">
            No internet connection detected. Some features may not be available, 
            but you can still access cached content.
        </p>
        <a href="/" class="retry-btn" onclick="window.location.reload(); return false;">
            🔄 Try Again
        </a>
        
        <div class="connection-status">
            <span class="status-indicator" id="connection-indicator"></span>
            <span id="connection-text">Checking connection...</span>
        </div>
    </div>
    
    <script>
        // Check online status
        function updateConnectionStatus() {
            const indicator = document.getElementById('connection-indicator');
            const text = document.getElementById('connection-text');
            
            if (navigator.onLine) {
                indicator.classList.add('online');
                text.textContent = 'Connection restored! Click "Try Again" to reload.';
            } else {
                indicator.classList.remove('online');
                text.textContent = 'Still offline. Please check your internet connection.';
            }
        }
        
        // Listen for connection changes
        window.addEventListener('online', updateConnectionStatus);
        window.addEventListener('offline', updateConnectionStatus);
        
        // Initial check
        updateConnectionStatus();
        
        // Auto-reload when back online
        window.addEventListener('online', () => {
            setTimeout(() => {
                window.location.reload();
            }, 1000);
        });
    </script>
</body>
</html>
        '''
        
        return Response(offline_html, mimetype='text/html')

# ===== PWA INSTALL BANNER API =====
@app.route('/api/pwa/install-status')
def pwa_install_status():
    """Check if PWA is installed (for analytics)"""
    user_agent = request.headers.get('User-Agent', '')
    
    return jsonify({
        'pwa_capable': True,
        'installation_prompt_shown': False,  # Track this in session/db
        'user_agent': user_agent,
        'timestamp': int(time.time())
    })

# ===== ICON FALLBACKS =====
@app.route('/static/images/icon-<int:size>.png')
def serve_icon_fallback(size):
    """Serve icon fallbacks if specific sizes don't exist"""
    try:
        # Try to serve the actual file
        return send_from_directory('static/images', f'icon-{size}.png')
    except:
        # Return a simple SVG icon as fallback
        svg_icon = f'''
<svg width="{size}" height="{size}" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <rect width="100" height="100" rx="20" fill="#3ECDC1"/>
    <text x="50" y="55" text-anchor="middle" fill="white" font-family="sans-serif" font-size="24" font-weight="bold">DA</text>
    <circle cx="30" cy="75" r="3" fill="white" opacity="0.8"/>
    <circle cx="50" cy="75" r="3" fill="white" opacity="0.8"/>
    <circle cx="70" cy="75" r="3" fill="white" opacity="0.8"/>
</svg>
        '''
        
        response = Response(svg_icon, mimetype='image/svg+xml')
        response.headers['Cache-Control'] = 'public, max-age=86400'
        
        return response

# ===== PWA SHARE TARGET (если нужно) =====
@app.route('/share-target', methods=['POST'])
def pwa_share_target():
    """Handle shared content from other apps"""
    try:
        title = request.form.get('title', '')
        text = request.form.get('text', '')
        url = request.form.get('url', '')
        
        # Handle shared files
        files = request.files.getlist('files')
        
        # Process shared content
        # You can save to database, redirect to appropriate page, etc.
        
        flash(f'Shared content received: {title}', 'success')
        return redirect(url_for('main_bp.index'))
        
    except Exception as e:
        app.logger.error(f"Share target error: {e}")
        flash('Error processing shared content', 'error')
        return redirect(url_for('main_bp.index'))

@app.route('/test-themes')
@app.route('/<lang>/test-themes')
def test_themes(lang=None):
    g.force_desktop = True
    return render_template('test_themes.html')

@app.route('/test-interactive')
@app.route('/<lang>/test-interactive')
def test_interactive(lang=None):
    g.force_desktop = True
    return render_template('theme_test_interactive.html')

@app.route('/index-new')
def index_new():
    """Новая версия главной страницы с системой тем"""
    lang = getattr(g, 'lang', session.get('lang', DEFAULT_LANGUAGE))
    translations = setup_translations(app)
    return render_template('index_new.html', 
                         lang=lang, 
                         translations=translations,
                         user=current_user)

if __name__ == '__main__':
    print("🌐 Starting Flask development server...")
    # Запуск с защитой от проблем с терминалом
    try:
        app.run(debug=True, port=8082, use_reloader=True)
    except (OSError, termios.error if termios else OSError) as e:
        print(f"⚠️  Debug mode error: {e}")
        print("🔄 Trying without reloader...")
        try:
            app.run(debug=False, port=8082, use_reloader=False)
        except Exception as e2:
            print(f"❌ Fatal error: {e2}")
            print("💡 Try running with: python app.py --no-debug")
            sys.exit(1)