# app.py - Clean Mentora Application
# Minimal Flask app with core functionality only

import os
import logging
import json
from datetime import datetime, timezone

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # If python-dotenv is not installed, try to load .env manually
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
from flask import Flask, render_template, request, session, g, redirect, url_for, flash, send_from_directory, abort
from utils.serializers import safe_jsonify
from flask_login import current_user, login_user, logout_user, login_required
# Replace import with more specific one
try:
    from flask_babel import get_locale
except ImportError:
    # Fallback function if flask_babel is not installed
    def get_locale():
        return 'en'

# Import extensions and models
from extensions import init_extensions, db, login_manager, babel
from utils.analytics_middleware import init_analytics_middleware
from models import User, LearningPath, Subject, Module, Lesson, create_sample_data, DigiDSession, UserProgress, Test, Question, QuestionCategory, WebsiteVisit, PageView, UserSession
from translations import get_translation, get_available_languages, DEFAULT_LANGUAGE, LANGUAGE_NAMES, RTL_LANGUAGES, COUNTRY_CODES
from flask_wtf.csrf import CSRFProtect
from utils.serializers import setup_json_serialization

import os
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
setup_json_serialization(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supported languages
SUPPORTED_LANGUAGES = ['nl', 'en', 'es', 'pt', 'uk', 'fa', 'tr', 'ru']
DEFAULT_LANGUAGE = 'nl'

# Load configuration
if os.environ.get('FLASK_ENV') == 'production':
    app.config.from_object('config.ProductionConfig')
else:
    app.config.from_object('config.DevelopmentConfig')

# Initialize extensions
init_extensions(app)

# Initialize analytics middleware
init_analytics_middleware(app)

# ========================================
# STATIC FILE VERSIONING
# ========================================

@app.template_global()
def static_versioned(filename):
    """Generate versioned static file URLs to prevent caching issues"""
    import time
    # Use timestamp for development, or version for production
    if app.config.get('FLASK_ENV') == 'production':
        version = '1.0.0'  # Change this when you want to force cache refresh
    else:
        version = str(int(time.time()))  # Use timestamp in development
    
    return url_for('static', filename=filename, v=version)

# Create all database tables
with app.app_context():
    db.create_all()  # Создаст все таблицы

# Initialize CSRF protection
csrf = CSRFProtect(app)

# CSRF configuration based on environment
if app.config.get('FLASK_ENV') == 'production':
    # Enable CSRF protection in production
    csrf.exempt(lambda: False)
else:
    # Disable CSRF for development/testing only
    csrf.exempt(lambda: True)

# ========================================
# USER LOADER
# ========================================

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return db.session.get(User, int(user_id))

# ========================================
# LANGUAGE DETECTION
# ========================================

def get_locale():
    """Determine the best language to use"""
    # 1. Check URL parameter
    if 'lang' in request.args:
        lang = request.args['lang']
        if lang in SUPPORTED_LANGUAGES:
            session['language'] = lang
            return lang
    
    # 2. Check session
    if 'language' in session:
        lang = session['language']
        if lang in SUPPORTED_LANGUAGES:
            return lang
    
    # 3. Check user preference
    if current_user.is_authenticated and current_user.language:
        if current_user.language in SUPPORTED_LANGUAGES:
            session['language'] = current_user.language
            return current_user.language
    
    # 4. Check browser preference
    return request.accept_languages.best_match(SUPPORTED_LANGUAGES) or DEFAULT_LANGUAGE

# Set locale selector for different Babel versions
try:
    babel.localeselector(get_locale)
except AttributeError:
    # For newer versions of Flask-Babel
    babel.locale_selector_func = get_locale

# ========================================
# BEFORE REQUEST HANDLERS
# ========================================

@app.before_request
def before_request():
    """Set up global variables before each request"""
    g.locale = str(get_locale())
    g.lang = g.locale  # Добавляем g.lang для совместимости с шаблонами
    g.supported_languages = SUPPORTED_LANGUAGES
    g.current_language = g.locale
    
    # Update user's last activity
    if current_user.is_authenticated:
        current_user.last_login = datetime.now(timezone.utc)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating user activity: {e}")
    
    # DigiD Session Management
    if current_user.is_authenticated and current_user.is_digid_user():
        digid_session_id = session.get('digid_session_id')
        if digid_session_id:
            digid_session = DigiDSession.query.filter_by(
                session_id=digid_session_id, 
                user_id=current_user.id
            ).first()
            
            if digid_session and digid_session.is_expired():
                # Session expired, logout user
                logout_user()
                session.pop('digid_session_id', None)
                session.pop('digid_user_id', None)
                
                # Get current language for flash message
                current_lang = g.get('lang', 'nl')
                if current_lang == 'en':
                    flash('Your DigiD session has expired. Please log in again.', 'warning')
                elif current_lang == 'ru':
                    flash('Your DigiD session has expired. Please log in again.', 'warning')
                else:
                    flash('Uw DigiD sessie is verlopen. Log opnieuw in.', 'warning')
                
                return redirect(url_for('digid.login'))

# ========================================
# AFTER REQUEST HANDLERS
# ========================================

@app.after_request
def after_request(response):
    """Handle post-request processing"""
    # Update DigiD session if user is authenticated and has active DigiD session
    if current_user.is_authenticated and current_user.is_digid_user():
        digid_session_id = session.get('digid_session_id')
        if digid_session_id:
            digid_session = DigiDSession.query.filter_by(
                session_id=digid_session_id, 
                user_id=current_user.id
            ).first()
            
            if digid_session and not digid_session.is_expired():
                # Extend session if it's close to expiring (within 1 hour)
                from datetime import timedelta
                # Ensure both datetime objects have timezone info
                now_utc = datetime.now(timezone.utc)
                expires_at = digid_session.expires_at
                if expires_at.tzinfo is None:
                    expires_at = expires_at.replace(tzinfo=timezone.utc)
                
                if expires_at - now_utc < timedelta(hours=1):
                    digid_session.expires_at = datetime.now(timezone.utc) + timedelta(
                        seconds=app.config.get('DIGID_SESSION_TIMEOUT', 28800)
                    )
                    try:
                        db.session.commit()
                    except Exception as e:
                        db.session.rollback()
                        logger.error(f"Error extending DigiD session: {e}")
    
    return response

# ========================================
# TEMPLATE HELPERS
# ========================================

@app.context_processor
def inject_template_vars():
    """Inject variables into all templates"""
    def t(key, lang=None, **kwargs):
        """Translation function for templates"""
        if lang is None:
            lang = g.get('lang', DEFAULT_LANGUAGE)
        return get_translation(key, lang, **kwargs)
    
    def csrf_token():
        """Generate CSRF token for forms"""
        from flask_wtf.csrf import generate_csrf
        return generate_csrf()
    
    def language_url(lang_code):
        """Generate URL with language parameter"""
        # Исключаем админку из языковой локализации
        if request.endpoint and request.endpoint.startswith('admin'):
            return url_for(request.endpoint, **request.view_args)
        
        if request.endpoint:
            return url_for(request.endpoint, lang=lang_code, **request.view_args)
        return url_for('index', lang=lang_code)
    
    return {
        'current_year': datetime.now().year,
        'app_name': 'Mentora',
        'supported_languages': app.config['LANGUAGES'],
        'current_language': g.get('locale', DEFAULT_LANGUAGE),
        'lang': g.get('lang', DEFAULT_LANGUAGE),  # Добавляем переменную lang
        'user': current_user if current_user and current_user.is_authenticated else None,
        't': t,  # Добавляем функцию переводов
        'csrf_token': csrf_token,  # Добавляем функцию CSRF token
        'language_url': language_url,  # Добавляем функцию генерации URL с языком
        # DigiD variables
        'digid_enabled': app.config.get('DIGID_ENABLED', False),
        'digid_mock_mode': app.config.get('DIGID_MOCK_MODE', False),
        'is_digid_user': current_user.is_digid_user() if current_user and current_user.is_authenticated else False,
        'digid_session_active': session.get('digid_session_id') is not None if current_user and current_user.is_authenticated else False
    }

# Template filters
@app.template_filter('from_json')
def from_json_filter(value):
    """Convert JSON string to Python object"""
    if not value:
        return None
    try:
        import json
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return None

# ========================================
# DOMAIN ROUTING
# ========================================

@app.before_request
def route_by_domain():
    host = request.host.lower()
    
    # Для mentora.com.in - показываем только главную страницу
    if 'mentora.com.in' in host:
        # Исключаем админ панель, API и analytics из редиректа
        if request.path != '/' and not request.path.startswith('/admin') and not request.path.startswith('/api') and not request.path.startswith('/analytics'):
            # Все остальные пути редиректим на главную
            return redirect('/')

# ========================================
# MAIN ROUTES (always available)
# ========================================

@app.route('/')
@app.route('/<string:lang>/')
def index(lang='nl'):
    host = request.host.lower()
    
    # Для mentora.com.in показываем космический дизайн
    if 'mentora.com.in' in host:
        return render_template('mentora_landing.html')
    
    # Для bigmentor.nl показываем обычную главную
    # Validate language
    if lang not in SUPPORTED_LANGUAGES:
        lang = DEFAULT_LANGUAGE
    
    # Set language in session and g
    session['lang'] = lang
    g.lang = lang
    
    stats = {
        "overall_progress": 75,
        "completed_lessons": 24,
        "total_lessons": 156,
        "average_score": 89,
        "anatomy_progress": 92,
        "physiology_progress": 78,
        "radiology_progress": 65,
    }
    return render_template('index.html', stats=stats, lang=lang)

# ========================================
# IMPORT ROUTES
# ========================================

# Try to import routes, create minimal ones if not found
try:
    from routes.main_routes import main_bp
    from routes.auth_routes import auth_bp
    from routes.dashboard_routes import dashboard_bp
    from routes.learning_routes import learning_bp
    from routes.test_routes import test_bp
    from routes.admin_routes import admin_bp
    from routes.virtual_patient_routes import virtual_patient_bp
    
    # Импорт новых роутов системы обучения
    from routes.subject_view_routes import subject_view_bp
    from routes.learning_map_routes import profession_map_bp
    from routes.lesson_routes import lesson_bp
    from routes.modules_routes import modules_bp
    from routes.content_navigation import content_nav_bp
    from routes.content_routes import content_bp
    
    # Импорт DigiD роутов (ОТКЛЮЧЕНО - не используется)
    # from routes.digid_routes import digid_bp
    
    # Импорт AI Assistant роутов
    from routes.ai_assistant_routes import ai_assistant_bp
    
    # Импорт Diagnostic роутов
    from routes.diagnostic_routes import diagnostic_bp
    
    # Импорт Testing роутов
    from routes.testing_routes import testing_bp
    
    # Импорт Learning Planner роутов
    from routes.learning_planner_routes import learning_planner_bp
    
    # Импорт Simple Learning роутов
    from routes.simple_learning_routes import simple_learning_bp
    
    # Импорт API роутов
    from routes.api_routes import api_bp
    
    # Импорт новых Learning роутов
    from routes.learning_routes_new import daily_learning_bp
    
    # Импорт Calendar Plan API роутов
    from routes.calendar_plan_api import calendar_plan_bp
    
    # Импорт Email Test роутов
    from routes.email_test_routes import email_test_bp
    
    # Импорт IRT + Spaced Repetition Integration роутов
    from routes.irt_spaced_routes import irt_spaced_bp
    

    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(learning_bp, url_prefix='/learning')  # ВКЛЮЧЕНО с декораторами блокировки
    # app.register_blueprint(test_bp, url_prefix='/tests')  # ОТКЛЮЧЕНО для предварительного запуска
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(virtual_patient_bp)  # ВКЛЮЧЕНО с декораторами блокировки
    
    # Регистрация новых blueprint-ов системы обучения
    app.register_blueprint(subject_view_bp)
    app.register_blueprint(profession_map_bp)  # Профессиональные карты обучения
    # app.register_blueprint(lesson_bp, url_prefix='/lesson')  # ОТКЛЮЧЕНО для предварительного запуска
    # app.register_blueprint(modules_bp)  # ОТКЛЮЧЕНО для предварительного запуска
    # app.register_blueprint(content_nav_bp, url_prefix='/content')  # ОТКЛЮЧЕНО для предварительного запуска
    # app.register_blueprint(content_bp, url_prefix='/content')  # ОТКЛЮЧЕНО для предварительного запуска
    
    # Регистрация DigiD blueprint (ОТКЛЮЧЕНО - не используется)
    # app.register_blueprint(digid_bp)
    
    # Регистрация AI Assistant blueprint (ВКЛЮЧЕНО с декораторами блокировки)
    app.register_blueprint(ai_assistant_bp)
    
    # Регистрация Diagnostic blueprint (ВКЛЮЧЕНО с декораторами блокировки)
    app.register_blueprint(diagnostic_bp, url_prefix='/big-diagnostic')
    
    # Регистрация Testing blueprint (ВКЛЮЧЕНО с декораторами блокировки)
    app.register_blueprint(testing_bp, url_prefix='/testing')
    
    # Регистрация Learning Planner blueprint
    app.register_blueprint(learning_planner_bp, url_prefix='/dashboard')
    
    # Регистрация Simple Learning blueprint
    app.register_blueprint(simple_learning_bp)
    
    # Регистрация API blueprint
    app.register_blueprint(api_bp)
    
    # Регистрация новых Learning blueprint
    app.register_blueprint(daily_learning_bp, url_prefix='/daily-learning')
    
    # Регистрация Calendar Plan API blueprint
    app.register_blueprint(calendar_plan_bp)
    
    # Регистрация Email Test blueprint
    app.register_blueprint(email_test_bp)
    
    # Регистрация IRT + Spaced Repetition Integration blueprint
    app.register_blueprint(irt_spaced_bp)
    
    # Регистрация Analytics blueprint
    from routes.analytics_routes import analytics_bp
    app.register_blueprint(analytics_bp)
    
    # Регистрация Profile blueprint
    from routes.profile_routes import profile_bp
    app.register_blueprint(profile_bp)
    
    # Регистрация Migration blueprint
    from routes.migration_routes import migration_bp
    app.register_blueprint(migration_bp)
    
    # Communication Hub
    try:
        from routes.communication_routes import communication_bp
        app.register_blueprint(communication_bp)
        logger.info("✅ Communication Hub blueprint registered successfully")
    except ImportError as communication_error:
        logger.warning(f"Could not import Communication Hub routes: {communication_error}")
    
    # CRM System
    try:
        from routes.admin_crm_routes import crm_bp
        app.register_blueprint(crm_bp)
        logger.info("✅ CRM blueprint registered successfully")
    except ImportError as crm_error:
        logger.warning(f"Could not import CRM routes: {crm_error}")
    
    # Monitoring System
    try:
        from routes.admin_monitoring_routes import monitoring_bp
        app.register_blueprint(monitoring_bp)
        logger.info("✅ Monitoring blueprint registered successfully")
    except ImportError as monitoring_error:
        logger.warning(f"Could not import Monitoring routes: {monitoring_error}")
    
    # CSRF exemptions for API endpoints (only in development)
    if app.config.get('FLASK_ENV') != 'production':
        # csrf.exempt(digid_bp)  # ОТКЛЮЧЕНО - не используется
        csrf.exempt(diagnostic_bp)
    
    logger.info("✅ All route blueprints registered successfully")
    
    # Система контроля доступа отключена (модуль не существует)
    # logger.info("ℹ️ Access control system not implemented")
    
except ImportError as e:
    logger.warning(f"Could not import routes: {e}")
    logger.info("Creating minimal routes...")
    
    # Все равно пытаемся зарегистрировать DigiD blueprint (ОТКЛЮЧЕНО - не используется)
    # try:
    #     from routes.digid_routes import digid_bp
    #     app.register_blueprint(digid_bp)
    #     if app.config.get('FLASK_ENV') != 'production':
    #         csrf.exempt(digid_bp)
    #     logger.info("✅ DigiD blueprint registered successfully")
    # except ImportError as digid_error:
    #     logger.warning(f"Could not import DigiD routes: {digid_error}")
    
    # Пытаемся зарегистрировать Diagnostic blueprint
    # Diagnostic blueprint already registered above
    

    
    @app.route('/contact')
    def contact():
        return render_template('contact.html')
    
    @app.route('/privacy')
    def privacy():
        return render_template('privacy.html')
    
    @app.route('/terms')
    def terms():
        return render_template('terms.html')
    
    @app.route('/dashboard')
    def dashboard():
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        return render_template('dashboard.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        return redirect(url_for('auth.login'))
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            
            if User.query.filter_by(username=username).first():
                from flask import flash
                flash('Пользователь с таким именем уже существует', 'error')
            elif User.query.filter_by(email=email).first():
                from flask import flash
                flash('Пользователь с таким email уже существует', 'error')
            else:
                user = User(username=username, email=email)
                user.set_password(password)
                user.requires_diagnostic = True  # Устанавливаем флаг диагностики для новых пользователей
                db.session.add(user)
                db.session.commit()
                
                login_user(user)
                
                # Проверяем необходимость диагностики после входа
                if user.requires_diagnostic:
                    return redirect(url_for('diagnostic.choose_diagnostic_type'))
                
                return redirect(url_for('index'))
        
        return render_template('auth/register.html')
    
    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('index'))
    
    @app.route('/profile')
    def profile():
        return render_template('profile/index.html', user=current_user)
    
    @app.route('/edit_profile')
    def edit_profile():
        return render_template('auth/edit_profile.html')
    
    # Removed conflicting route - using blueprint instead

# ========================================
# SIMPLE TEST ROUTES
# ========================================

@app.route('/health')
def health_check():
    """Health check для Render"""
    try:
        # Проверяем подключение к БД
        db.session.execute('SELECT 1')
        
        # Проверяем основные модели
        user_count = User.query.count()
        question_count = Question.query.count()
        path_count = LearningPath.query.count()
        
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'environment': app.config.get('FLASK_ENV', 'unknown'),
            'database': 'connected',
            'stats': {
                'users': user_count,
                'questions': question_count,
                'learning_paths': path_count
            }
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, 500

@app.route('/ai-test')
def ai_test():
    """Simple AI test route"""
    return safe_jsonify({
        'message': 'AI test successful',
        'status': 'ok'
    })

# Удаляем дублирующий роут learning-map
# @app.route('/learning-map/')
# @app.route('/<string:lang>/learning-map/')
# def learning_map_redirect(lang='ru'):
#     """Redirect to new learning map"""
#     return redirect(url_for('daily_learning.learning_map', lang=lang))

@app.route('/test-diagnostic')
def test_diagnostic():
    """Тестовая страница для отладки диагностики"""
    return render_template('test_diagnostic.html')

# ========================================
# ERROR HANDLERS
# ========================================

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    return render_template('errors/500.html'), 500

# ========================================
# CLI COMMANDS
# ========================================

from commands.import_questions import import_questions
app.cli.add_command(import_questions)

# ========================================
# DEVELOPMENT ROUTES
# ========================================

if app.config.get('ENV') == 'development':
    @app.route('/debug/info')
    def debug_info():
        """Debug information (development only)"""
        info = {
            'app_name': app.name,
            'config': dict(app.config),
            'routes': [str(rule) for rule in app.url_map.iter_rules()],
            'current_user': current_user.username if current_user.is_authenticated else 'Anonymous',
            'language': g.get('locale', 'Unknown'),
            'database_uri': app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set'),
        }
        return f"<pre>{str(info)}</pre>"

logger.info("Mentora Clean application created successfully!")

# Import questions command
try:
    from commands.import_questions import import_questions
    app.cli.add_command(import_questions)
    logger.info("✅ Import questions command registered")
except ImportError as e:
    logger.warning(f"⚠️ Import questions command not available: {e}")

# IRT calibration command
@app.cli.command()
def calibrate_irt():
    """Калибровать IRT параметры для всех вопросов"""
    try:
        from scripts.calibrate_irt_parameters import calibrate_all_questions
        calibrate_all_questions()
        logger.info("✅ IRT calibration completed")
    except ImportError:
        logger.warning("⚠️ IRT calibration script not found, skipping...")

logger.info("✅ IRT calibration command registered")

# Seed database command
@app.cli.command()
def seed_database():
    """Загрузить все данные для production"""
    import subprocess
    import sys
    from pathlib import Path
    
    script_path = Path(__file__).parent / 'scripts' / 'seed_production_data_runner.py'
    
    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        sys.exit(1)
    
    try:
        result = subprocess.run([sys.executable, str(script_path)], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        print("✅ Загрузка данных завершена успешно!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при загрузке данных: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        sys.exit(1)

        logger.info("✅ Seed database command registered")
        
    except Exception as e:
        logger.error(f"Error registering seed database command: {e}")

# Production data check command
@app.cli.command()
def check_production_data():
    """Проверить и загрузить данные на production"""
    import subprocess
    import sys
    from pathlib import Path

    script_path = Path(__file__).parent / 'scripts' / 'check_production_data.py'

    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        sys.exit(1)

    try:
        result = subprocess.run([sys.executable, str(script_path)],
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        print("✅ Проверка production данных завершена успешно!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при проверке данных: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        sys.exit(1)

logger.info("✅ Check production data command registered")

# Create production topics command
@app.cli.command()
def create_topics():
    """Создать темы для сообщества в продакшене"""
    import subprocess
    import sys
    from pathlib import Path

    script_path = Path(__file__).parent / 'scripts' / 'create_production_topics.py'

    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        return

    try:
        result = subprocess.run([sys.executable, str(script_path)], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        print("✅ Создание тем завершено успешно!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при создании тем: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")

logger.info("✅ Create topics command registered")

# Force recreate topics command
@app.cli.command()
def recreate_topics():
    """Принудительно пересоздать темы сообщества"""
    import subprocess
    import sys
    from pathlib import Path

    script_path = Path(__file__).parent / 'scripts' / 'recreate_production_topics.py'

    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        return

    try:
        result = subprocess.run([sys.executable, str(script_path)], 
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        print("✅ Пересоздание тем завершено успешно!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при пересоздании тем: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")

logger.info("✅ Recreate topics command registered")

# Web endpoint for recreating topics (for production use)
@app.route('/admin/recreate-topics', methods=['GET', 'POST'])
def web_recreate_topics():
    """Веб-эндпоинт для пересоздания тем (для продакшена)"""
    if request.method == 'GET':
        return render_template('admin/recreate_topics.html')
    
    try:
        # Проверяем, что пользователь админ (если нужно)
        # if not current_user.is_authenticated or not current_user.is_admin:
        #     return jsonify({'error': 'Unauthorized'}), 403
        
        from scripts.recreate_production_topics import recreate_production_topics
        recreate_production_topics()
        
        return safe_jsonify({
            'success': True,
            'message': 'Topics recreated successfully!'
        }), 200
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error in web_recreate_topics: {error_details}")
        
        return safe_jsonify({
            'success': False,
            'error': str(e),
            'details': error_details
        }), 500

logger.info("✅ Web recreate topics endpoint registered")

# Simple direct script execution endpoint
@app.route('/admin/recreate-topics-direct')
def direct_recreate_topics():
    """Прямое выполнение скрипта пересоздания тем"""
    try:
        # Встроенная функция вместо импорта
        from models import db, ForumCategory, ForumTopic, ForumPost, User
        from datetime import datetime, timedelta
        import random
        
        with app.app_context():
            print("🔍 Starting topic recreation...")
            
            # Удаляем существующие темы
            topics_to_delete = ForumTopic.query.filter(
                ForumTopic.title.in_([
                    'AKV tandartsen - BIG Registration Discussion 🦷',
                    'General Chat - Let\'s talk about everything! 💬'
                ])
            ).all()
            
            deleted_count = 0
            for topic in topics_to_delete:
                print(f"🗑️ Deleting topic: {topic.title}")
                ForumPost.query.filter_by(topic_id=topic.id).delete()
                db.session.delete(topic)
                deleted_count += 1
            
            db.session.commit()
            print(f"✅ Deleted {deleted_count} topics")
            
            # Создаем фейковых пользователей
            fake_users_data = [
                {'name': 'Maria', 'email': 'maria@example.com'},
                {'name': 'Ahmed', 'email': 'ahmed@example.com'},
                {'name': 'Priya', 'email': 'priya@example.com'},
                {'name': 'Carlos', 'email': 'carlos@example.com'},
                {'name': 'Anna', 'email': 'anna@example.com'},
                {'name': 'Lucas', 'email': 'lucas@example.com'},
                {'name': 'Emma', 'email': 'emma@example.com'},
                {'name': 'Dr. Sarah', 'email': 'drsarah@example.com'},
                {'name': 'Alex', 'email': 'alex@example.com'},
                {'name': 'David', 'email': 'david@example.com'}
            ]
            
            fake_users = []
            for user_data in fake_users_data:
                existing_user = User.query.filter_by(email=user_data['email']).first()
                if not existing_user:
                    user = User(
                        email=user_data['email'],
                        first_name=user_data['name'],
                        last_name='',
                        role='user',
                        is_active=True,
                        created_at=datetime.now() - timedelta(days=random.randint(30, 90))
                    )
                    db.session.add(user)
                    fake_users.append(user)
                    print(f"✅ Created user: {user_data['name']}")
                else:
                    fake_users.append(existing_user)
                    print(f"⏭️ User exists: {user_data['name']}")
            
            db.session.commit()
            
            # Находим категорию
            general_category = ForumCategory.query.filter_by(slug='general').first()
            if not general_category:
                general_category = ForumCategory(
                    name='General Discussion',
                    slug='general',
                    description='General discussions about BIG registration and healthcare in the Netherlands',
                    is_active=True,
                    order=1
                )
                db.session.add(general_category)
                db.session.commit()
            
            # Находим админа
            admin_user = User.query.filter_by(role='admin').first()
            if not admin_user:
                admin_user = User.query.first()
            
            # Создаем темы
            base_date = datetime(2025, 9, 1)
            
            # Тема 1: AKV Discussion
            topic1 = ForumTopic(
                title='AKV tandartsen - BIG Registration Discussion 🦷',
                content='Discussion about AKV tests and BIG registration process for dentists.',
                category_id=general_category.id,
                author_id=admin_user.id,
                status='active',
                views_count=150,
                replies_count=10,
                likes_count=15,
                created_at=base_date,
                updated_at=base_date + timedelta(days=2)
            )
            db.session.add(topic1)
            db.session.flush()
            
            # Сообщения для темы 1
            messages1 = [
                {'author': 'Maria', 'content': 'Goedemorgen collega\'s, Ik heb een vraag, moeten we alle documenten bij BiG inleveren voordat we de AKV-toetsen afleggen, of moeten we eerst de tests afleggen?', 'hour': 9, 'minute': 23},
                {'author': 'Priya', 'content': 'Volgens mij kun je het beste eerst de taaltoets doen en daarna de documenten samen met het taalcertificaat opsturen.', 'hour': 9, 'minute': 45},
                {'author': 'Maria', 'content': 'Bedankt!', 'hour': 14, 'minute': 12},
                {'author': 'Ahmed', 'content': 'Hallo er bestaat geen akv test meer 👍', 'hour': 14, 'minute': 28},
                {'author': 'Maria', 'content': 'Hoe bedoel je?', 'hour': 14, 'minute': 31},
                {'author': 'Carlos', 'content': 'In plaats van AKV toets, moeten we nu B2+ taal certificaat halen en alle documenten naar CIBG sturen. Daarna krijgen we een datum voor BI-toets', 'hour': 14, 'minute': 47},
                {'author': 'Maria', 'content': 'Maar als we slagen voor de BGB en of Babel examens, dan wordt dat beschouwd als een B2+ certificaat? Krijgen we een certificaat van hun?', 'hour': 16, 'minute': 19},
                {'author': 'Anna', 'content': 'Maar als we slagen voor de BGB en of Babel examens, dan wordt dat beschouwd als een B2+ certificaat? Krijgen we een certificaat van hun?', 'hour': 16, 'minute': 30},
                {'author': 'Anna', 'content': 'Inderdaad', 'hour': 16, 'minute': 32},
                {'author': 'Maria', 'content': 'Bedankt!', 'hour': 18, 'minute': 15}
            ]
            
            for msg in messages1:
                author = next((u for u in fake_users if u.first_name == msg['author']), fake_users[0])
                post = ForumPost(
                    topic_id=topic1.id,
                    author_id=author.id,
                    content=msg['content'],
                    created_at=base_date + timedelta(hours=msg['hour'], minutes=msg['minute']),
                    updated_at=base_date + timedelta(hours=msg['hour'], minutes=msg['minute'])
                )
                db.session.add(post)
            
            # Тема 2: General Chat
            topic2 = ForumTopic(
                title='General Chat - Let\'s talk about everything! 💬',
                content='This is a general discussion thread where you can talk about anything.',
                category_id=general_category.id,
                author_id=admin_user.id,
                status='active',
                views_count=80,
                replies_count=4,
                likes_count=8,
                created_at=base_date + timedelta(days=2),
                updated_at=base_date + timedelta(days=4)
            )
            db.session.add(topic2)
            db.session.flush()
            
            # Сообщения для темы 2
            messages2 = [
                {'author': 'Emma', 'content': 'Dankjewel!', 'hour': 9, 'minute': 17},
                {'author': 'Lucas', 'content': 'Deze krijg ik net binnen...', 'hour': 9, 'minute': 34},
                {'author': 'Alex', 'content': 'не за что', 'hour': 15, 'minute': 22},
                {'author': 'David', 'content': 'Missed voice call', 'hour': 11, 'minute': 8}
            ]
            
            for msg in messages2:
                author = next((u for u in fake_users if u.first_name == msg['author']), fake_users[0])
                post = ForumPost(
                    topic_id=topic2.id,
                    author_id=author.id,
                    content=msg['content'],
                    created_at=base_date + timedelta(days=1, hours=msg['hour'], minutes=msg['minute']),
                    updated_at=base_date + timedelta(days=1, hours=msg['hour'], minutes=msg['minute'])
                )
                db.session.add(post)
            
            db.session.commit()
            print("✅ Topics created successfully!")
        
        return """
        <html>
        <head><title>Topics Recreated</title></head>
        <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px;">
            <h1 style="color: green;">✅ Topics Recreated Successfully!</h1>
            <p>Community topics have been recreated with new names and realistic timestamps.</p>
            <p><strong>Created:</strong></p>
            <ul>
                <li>AKV tandartsen - BIG Registration Discussion 🦷 (10 messages)</li>
                <li>General Chat - Let's talk about everything! 💬 (4 messages)</li>
            </ul>
            <p><a href="/community">Go to Community</a></p>
        </body>
        </html>
        """, 200
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        
        return f"""
        <html>
        <head><title>Error</title></head>
        <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px;">
            <h1 style="color: red;">❌ Error Recreating Topics</h1>
            <p><strong>Error:</strong> {str(e)}</p>
            <details>
                <summary>Technical Details</summary>
                <pre style="background: #f5f5f5; padding: 10px; overflow: auto;">{error_details}</pre>
            </details>
        </body>
        </html>
        """, 500

logger.info("✅ Direct recreate topics endpoint registered")

# Force load production data command
@app.cli.command()
def force_load_data():
    """Принудительно загрузить данные на production"""
    import subprocess
    import sys
    from pathlib import Path

    script_path = Path(__file__).parent / 'scripts' / 'force_load_production_data.py'

    if not script_path.exists():
        print(f"❌ Script not found: {script_path}")
        sys.exit(1)

    try:
        result = subprocess.run([sys.executable, str(script_path)],
                              capture_output=True, text=True, check=True)
        print(result.stdout)
        print("✅ Принудительная загрузка данных завершена успешно!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при принудительной загрузке данных: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        sys.exit(1)

logger.info("✅ Force load data command registered")

def create_admin_if_not_exists():
    """Create admin user if it doesn't exist (for production)"""
    try:
        from models import User, db
        
        admin_email = "admin@mentora.com.in"
        admin_password = "MentoraAdmin2025!"
        
        # Check if admin already exists
        existing_admin = User.query.filter_by(email=admin_email).first()
        
        if existing_admin:
            # Make sure existing user is admin
            if existing_admin.role != 'admin':
                existing_admin.role = 'admin'
                existing_admin.is_active = True
                existing_admin.email_confirmed = True
                existing_admin.set_password(admin_password)
                db.session.commit()
                logger.info(f"✅ User {admin_email} is now admin!")
        else:
            # Create new admin user
            admin_user = User(
                email=admin_email,
                first_name='Admin',
                last_name='User',
                role='admin',
                is_active=True,
                email_confirmed=True,
                registration_completed=True
            )
            admin_user.set_password(admin_password)
            
            db.session.add(admin_user)
            db.session.commit()
            logger.info(f"✅ Production admin {admin_email} created!")
        
        logger.info(f"🌐 Admin access: https://www.mentora.com.in/admin/")
        logger.info(f"📧 Email: {admin_email}")
        logger.info(f"🔑 Password: {admin_password}")
        logger.info("⚠️  IMPORTANT: Change password after first login!")
        
    except Exception as e:
        logger.error(f"❌ Error creating admin: {str(e)}")

# ========================================
# APPLICATION ENTRY POINT
# ========================================

if __name__ == '__main__':
    # Create database tables if they don't exist
    with app.app_context():
        try:
            db.create_all()
            logger.info("✅ Database initialized")
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
    
    # Run the application
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    
    logger.info(f"🚀 Starting Mentora on port {port}")
    logger.info(f"🔧 Debug mode: {debug}")
    
    # Create admin user if it doesn't exist (production only)
    with app.app_context():
        create_admin_if_not_exists()
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    ) 
