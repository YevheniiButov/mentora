# app.py

import os
import json
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, g, request, session, jsonify
from flask_login import current_user
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix
from translations import get_translation
from utils.subtopics import create_slug, update_lesson_subtopics, reorder_subtopic_lessons
from mobile_integration import init_mobile_integration
from utils.mobile_helpers import init_mobile_helpers

# Import extensions
from extensions import db, login_manager, bcrypt, babel, cache

# Import models
from models import User, Module, Lesson, UserProgress, Subject, LearningPath, VirtualPatientScenario

# Import routes
from routes.main_routes import main_bp
from routes.auth_routes import auth_bp
from routes.admin_routes import admin_bp
from routes.forum_routes import forum_bp
from routes.virtual_patient_routes import virtual_patient_bp
from routes.api_routes import api_bp
from routes.lesson_routes import lesson_bp
from routes.tests_routes import tests_bp
from routes.learning_map_routes import learning_map_bp
from routes.dashboard_routes import dashboard_bp
from routes.modules_routes import modules_bp 
from routes.subject_view_routes import subject_view_bp

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Языковые настройки
SUPPORTED_LANGUAGES = ['en', 'ru', 'nl', 'uk', 'es', 'pt', 'tr', 'fa']
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
    

    # Настройка поддержки прокси для правильных URL
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)
    
    # Инициализация расширений
    db.init_app(app)
    migrate = Migrate(app, db)
    bcrypt.init_app(app)
    csrf = CSRFProtect(app)
    cache.init_app(app)
    
    # Настройка логина с измененными параметрами
    login_manager.init_app(app)
    login_manager.login_view = 'auth_bp.login'
    login_manager.session_protection = 'basic'  # Изменено с 'strong' на 'basic' для отладки
    login_manager.login_message = "Please log in to access this page."
    login_manager.refresh_view = 'auth_bp.login'
    login_manager.needs_refresh_message = "Please log in again to confirm your identity"
    
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))    
    
    # Добавляем функцию перевода в глобальное пространство имен Jinja2
    app.jinja_env.globals.update(t=get_translation)
    
    # ОБЪЕДИНЕННЫЙ обработчик для языка и безопасности сессии
    @app.before_request
    def handle_language_and_redirect():
        """Комбинированный обработчик запросов: установка языка, проверка сессии и перенаправление."""
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
    def update_subtopics():
        """Обновляет поля subtopic и subtopic_slug у всех уроков"""
        print("🔄 Updating subtopics in all lessons...")
        
        # Импортируем необходимые функции
        import re
        import json
        
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
                    for card in content_data['cards']:
                        if 'module_title' in card:
                            module_title = card.get('module_title')
                            break
                elif 'questions' in content_data and content_data['questions']:
                    for question in content_data['questions']:
                        if 'module_title' in question:
                            module_title = question.get('module_title')
                            break
                
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
    def reorder_subtopics():
        """Переупорядочивает уроки в подтемах, чередуя карточки и тесты"""
        print("🔄 Reordering lessons in all subtopics...")
        
        # Получаем все уникальные подтемы с уроками
        subtopics = db.session.query(
            Lesson.subtopic,
            Lesson.subtopic_slug
        ).filter(
            Lesson.subtopic.isnot(None),
            Lesson.subtopic_slug.isnot(None)
        ).distinct().all()
        
        total_updated = 0
        
        for subtopic_name, subtopic_slug in subtopics:
            print(f"   - Reordering subtopic: '{subtopic_name}'")
            
            # Получаем все уроки подтемы
            lessons = Lesson.query.filter_by(
                subtopic_slug=subtopic_slug
            ).all()
            
            # Разделяем на карточки и тесты
            learning_cards = [l for l in lessons if l.content_type == 'learning_card']
            tests = [l for l in lessons if l.content_type in ['quiz', 'test_question']]
            
            # Сортируем по имеющемуся порядку
            learning_cards.sort(key=lambda x: x.order or 0)
            tests.sort(key=lambda x: x.order or 0)
            
            # Чередуем карточки и тесты (2 карточки, 1 тест)
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
                total_updated += 1
            
            print(f"     ✅ Updated {len(new_order)} lessons")
        
        # Сохраняем изменения
        db.session.commit()
        
        print(f"\n🎉 Total updated lessons: {total_updated}")

    # Регистрация Blueprint'ов
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(virtual_patient_bp)
    app.register_blueprint(lesson_bp)
    app.register_blueprint(forum_bp)  
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(tests_bp, url_prefix='/<string:lang>/tests')
    app.register_blueprint(learning_map_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(modules_bp)  
    app.register_blueprint(subject_view_bp)

    # Установка глобальных контекстных переменных для шаблонов
    @app.context_processor
    def inject_global_vars():
        return dict(
            current_year=datetime.now().year,
            app_name="Become a Tandarts",
            supported_languages=SUPPORTED_LANGUAGES,
            config=app.config
        )
    
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
        return render_template('404.html'), 404
    
    # Страница 500
    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        return render_template('500.html'), 500
    
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

    init_mobile_integration(app)
    init_mobile_helpers(app)

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
if __name__ == '__main__':
    # Дополнительная отладочная информация при запуске
    print("\n" + "="*50)
    print("🚀 STARTING BECOME A TANDARTS APPLICATION")
    print("="*50)
    
    # Проверяем структуру каталогов
    cards_dir = os.path.join(os.getcwd(), 'cards')
    print(f"📂 Cards directory: {cards_dir}")
    print(f"📂 Directory exists: {os.path.exists(cards_dir)}")
    
    if os.path.exists(cards_dir):
        subdirs = [d for d in os.listdir(cards_dir) if os.path.isdir(os.path.join(cards_dir, d))]
        print(f"📁 Available topic folders: {subdirs}")
        
        for subdir in subdirs:
            subdir_path = os.path.join(cards_dir, subdir)
            files = os.listdir(subdir_path)
            json_files = [f for f in files if f.endswith('.json')]
            print(f"   📁 {subdir}/: {json_files}")
    else:
        print("⚠️  WARNING: Cards directory not found!")
        print(f"   Current working directory: {os.getcwd()}")
        print(f"   Expected directory: {cards_dir}")
        print("   💡 To import content, create the cards/ directory with JSON files")
        print("      Then run: flask import-content")
    
    # Показываем информацию о модулях в БД
    with app.app_context():
        try:
            modules = Module.query.all()
            print(f"\n📚 Database modules ({len(modules)} total):")
            for module in modules:
                lessons_count = Lesson.query.filter_by(module_id=module.id).count()
                print(f"   - ID {module.id}: {module.title} ({lessons_count} lessons)")
            
            if len(modules) == 0:
                print("   ℹ️  No modules found in database.")
                print("      To import content from JSON files, run: flask import-content")
        except Exception as e:
            print(f"❌ Error querying database: {e}")
    
    print("="*50)
    print("🌐 Starting Flask development server...")
    print("💡 Available CLI commands:")
    print("   - flask import-content  : Import JSON files to database")
    print("   - flask clear-content   : Clear all imported content")
    print("   - flask show-modules    : Show all modules in database")
    print("="*50 + "\n")
    
    app.run(debug=True)