# app.py - Mentora Application

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
from extensions import init_extensions, db, login_manager, babel, csrf
from flask_wtf.csrf import CSRFProtect
from utils.analytics_middleware import init_analytics_middleware
from models import User, LearningPath, Subject, Module, Lesson, create_sample_data, DigiDSession, UserProgress, Test, Question, QuestionCategory, WebsiteVisit, PageView, UserSession
from translations import get_translation, get_available_languages, DEFAULT_LANGUAGE, LANGUAGE_NAMES, RTL_LANGUAGES, COUNTRY_CODES
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
            try:
                return url_for(request.endpoint, lang=lang_code, **request.view_args)
            except:
                # Fallback если роут не поддерживает lang
                return f'/{lang_code}/'
        return f'/{lang_code}/'
    
    def main_index_url(lang_code='en'):
        """Generate URL for main index page with language"""
        return f'/{lang_code}/'
    
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
        'main_index_url': main_index_url,  # Добавляем функцию генерации URL главной страницы
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
    
    # Для mentora.com.in - разрешаем главную страницу и языковые роуты
    if 'mentora.com.in' in host:
        # Разрешенные пути
        allowed_paths = ['/', '/nl', '/en', '/ru', '/uk', '/es', '/pt', '/tr', '/fa', '/mentora-login']
        allowed_prefixes = ['/admin', '/api', '/analytics', '/static']
        
        # Проверяем, разрешен ли текущий путь
        path_allowed = (
            request.path in allowed_paths or 
            any(request.path.startswith(prefix) for prefix in allowed_prefixes)
        )
        
        # Если путь не разрешен - редирект на главную
        if not path_allowed:
            return redirect('/')

# ========================================
# MAIN ROUTES (always available)
# ========================================

@app.route('/')
def root_redirect():
    """Redirect root to default language"""
    return redirect('/nl')

@app.route('/debug-mentora-login', methods=['GET', 'POST'])
def debug_mentora_login():
    """Debug endpoint to test mentora-login routing"""
    return jsonify({
        'success': True,
        'message': 'Debug endpoint reached',
        'host': request.host,
        'method': request.method,
        'url': request.url,
        'path': request.path
    })

@app.route('/mentora-login', methods=['GET', 'POST'])
def mentora_login():
    """Обработка входа с лендинговой страницы mentora.com.in"""
    from flask_login import login_user
    from werkzeug.security import check_password_hash
    from models import User
    
    host = request.host.lower()
    
    # Отладочная информация
    current_app.logger.info(f"Mentora login attempt from host: {host}, method: {request.method}")
    current_app.logger.info(f"Request URL: {request.url}")
    current_app.logger.info(f"Request path: {request.path}")
    
    # Обработка GET запросов - перенаправляем на главную страницу
    if request.method == 'GET':
        current_app.logger.info("GET request to mentora-login, redirecting to index")
        return redirect(url_for('index'))
    
    # Проверяем, что запрос пришел с mentora.com.in
    if 'mentora.com.in' not in host:
        current_app.logger.warning(f"Unauthorized domain attempt: {host}")
        return jsonify({'success': False, 'message': 'Unauthorized domain'}), 403
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        username_or_email = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username_or_email or not password:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400
        
        # Поиск пользователя по email или username
        user = User.query.filter(
            (User.email == username_or_email) | (User.username == username_or_email)
        ).first()
        
        if not user:
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
        
        # Проверка пароля
        if not user.check_password(password):
            return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
        
        # Проверка активности аккаунта
        if not user.is_active:
            return jsonify({'success': False, 'message': 'Account is disabled'}), 401
        
        # Вход пользователя
        login_user(user, remember=True)
        
        # Обновить время последнего входа
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Login successful',
            'redirect_url': url_for('dashboard')
        })
        
    except Exception as e:
        current_app.logger.error(f"Mentora login error: {str(e)}")
        return jsonify({'success': False, 'message': 'Login failed'}), 500

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
    from routes.learning_map_routes import learning_map_bp
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
    
    # User statistics API
    from routes.user_statistics_api import statistics_bp
    
    # Импорт Learning Planner роутов
    from routes.learning_planner_routes import learning_planner_bp
    
    # Импорт Simple Learning роутов
    from routes.simple_learning_routes import simple_learning_bp
    
    # Импорт SEO роутов
    from routes.seo_routes import seo_bp
    
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
    
    # Импорт Games роутов
    from routes.games_routes import games_bp

    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(learning_bp, url_prefix='/learning')  # ВКЛЮЧЕНО с декораторами блокировки
    # app.register_blueprint(test_bp, url_prefix='/tests')  # ОТКЛЮЧЕНО для предварительного запуска
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(virtual_patient_bp)  # ВКЛЮЧЕНО с декораторами блокировки
    
    # Регистрация новых blueprint-ов системы обучения
    app.register_blueprint(subject_view_bp)
    app.register_blueprint(learning_map_bp)  # Профессиональные карты обучения
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
    
    # Регистрация Statistics API blueprint
    app.register_blueprint(statistics_bp)
    logger.info("✅ Statistics API blueprint registered successfully")
    
    # Регистрация Learning Planner blueprint
    app.register_blueprint(learning_planner_bp, url_prefix='/dashboard')
    
    # Регистрация Simple Learning blueprint
    app.register_blueprint(simple_learning_bp)
    
    # Регистрация SEO blueprint
    app.register_blueprint(seo_bp)
    
    # Регистрация API blueprint
    app.register_blueprint(api_bp)
    
    # Регистрация новых Learning blueprint
    app.register_blueprint(daily_learning_bp)
    
    # Регистрация Calendar Plan API blueprint
    app.register_blueprint(calendar_plan_bp)
    
    # Регистрация Email Test blueprint
    app.register_blueprint(email_test_bp)
    
    # Регистрация IRT + Spaced Repetition Integration blueprint
    app.register_blueprint(irt_spaced_bp)
    
    # Регистрация Games blueprint
    app.register_blueprint(games_bp)
    logger.info("✅ Games blueprint registered successfully")
    
    # Регистрация Analytics blueprint
    try:
        from routes.analytics_routes import analytics_bp
        app.register_blueprint(analytics_bp)
        logger.info("✅ Analytics blueprint registered successfully")
    except Exception as analytics_error:
        logger.error(f"❌ ERROR importing Analytics routes: {analytics_error}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
    
    # Tracking routes
    from routes.tracking_routes import tracking_bp
    app.register_blueprint(tracking_bp)
    
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
    
    # Membership System
    try:
        from routes.membership_routes import membership_bp
        app.register_blueprint(membership_bp)
        logger.info("✅ Membership blueprint registered successfully")
    except Exception as membership_error:
        logger.error(f"❌ ERROR importing Membership routes: {membership_error}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
    
    # Individual Plan API System
    try:
        from routes.individual_plan_api import individual_plan_api_bp
        app.register_blueprint(individual_plan_api_bp)
        logger.info("✅ Individual Plan API blueprint registered successfully")
    except Exception as individual_plan_error:
        logger.error(f"❌ ERROR importing Individual Plan API routes: {individual_plan_error}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
    
    # CSRF exemptions for API endpoints (only in development)
    if app.config.get('FLASK_ENV') != 'production':
        # csrf.exempt(digid_bp)  # ОТКЛЮЧЕНО - не используется
        csrf.exempt(diagnostic_bp)
    
    logger.info("✅ All route blueprints registered successfully")
    
    # Система контроля доступа отключена (модуль не существует)
    # logger.info("ℹ️ Access control system not implemented")
    
    # Membership card route
    @app.route('/membership/card')
    @login_required
    def membership_card():
        """Display digital membership card for authenticated users"""
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        
        # Generate member ID if not exists
        if not hasattr(current_user, 'member_id') or not current_user.member_id:
            # Generate a simple member ID based on user ID
            import hashlib
            user_hash = hashlib.md5(str(current_user.id).encode()).hexdigest()[:5].upper()
            current_user.member_id = f"MNT-{user_hash}"
            db.session.commit()
        
        # Set membership expiry date if not exists (1 year from now)
        if not hasattr(current_user, 'membership_expires') or not current_user.membership_expires:
            from datetime import datetime, timedelta
            current_user.membership_expires = datetime.now() + timedelta(days=365)
            db.session.commit()
        
        # Generate QR code if user is premium and doesn't have one
        if (current_user.membership_type == 'premium' and 
            (not hasattr(current_user, 'qr_code_path') or not current_user.qr_code_path)):
            try:
                from routes.membership_routes import generate_member_qr
                generate_member_qr(current_user)
            except Exception as e:
                logger.warning(f"Could not generate QR code: {e}")
        
        return render_template('membership/card.html')
    
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
    

    # Legacy routes removed - handled by blueprints
    
    
    # Legacy auth routes removed - handled by auth_bp
    
    # Profile and community routes removed - handled by blueprints
    
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

@app.route('/demo/learning-map-light')
def demo_learning_map_light():
    """Demo страница - Alpine.js версия карты обучения (светлая с шапкой)"""
    return render_template('learning/learning_map_light_with_header.html')

@app.route('/demo/learning-map-modern')
def demo_learning_map_modern():
    """Demo страница - Alpine.js версия карты обучения (стиль как главная страница)"""
    return render_template('learning/learning_map_modern_style.html')

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

# Create BIG domains command
@app.cli.command('create-domains')
def create_domains_command():
    """Create BIG domains in database"""
    from scripts.create_big_domains import create_big_domains
    create_big_domains()

# Update questions domains command
@app.cli.command('update-domains')
def update_domains_command():
    """Update existing questions to link them with BIG domains"""
    from scripts.update_questions_domains import update_questions_domains
    update_questions_domains()

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

# CLI Commands (only load in development mode)
if os.getenv('FLASK_ENV') == 'development' or os.getenv('LOAD_ADMIN_ENDPOINTS') == 'true':
    # Import questions command
    try:
        from commands.import_questions import import_questions
        app.cli.add_command(import_questions)
        logger.info("✅ Import questions command registered")
    except ImportError as e:
        logger.warning(f"⚠️ Import questions command not available: {e}")
else:
    logger.info("🚀 CLI commands skipped (production mode)")

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

# DISABLED: Create production topics command (not needed anymore)
# @app.cli.command()
# def create_topics():
#     """Создать темы для сообщества в продакшене"""
#     import subprocess
#     import sys
#     from pathlib import Path
#
#     script_path = Path(__file__).parent / 'scripts' / 'create_production_topics.py'
#
#     if not script_path.exists():
#         print(f"❌ Script not found: {script_path}")
#         return
#
#     try:
#         result = subprocess.run([sys.executable, str(script_path)], 
#                               capture_output=True, text=True, check=True)
#         print(result.stdout)
#         print("✅ Создание тем завершено успешно!")
#     except subprocess.CalledProcessError as e:
#         print(f"❌ Ошибка при создании тем: {e}")
#         print(f"STDOUT: {e.stdout}")
#         print(f"STDERR: {e.stderr}")
#
# logger.info("✅ Create topics command registered")

# DISABLED: Force recreate topics command (not needed anymore)
# @app.cli.command()
# def recreate_topics():
#     """Принудительно пересоздать темы сообщества"""
#     import subprocess
#     import sys
#     from pathlib import Path
#
#     script_path = Path(__file__).parent / 'scripts' / 'recreate_production_topics.py'
#
#     if not script_path.exists():
#         print(f"❌ Script not found: {script_path}")
#         return
#
#     try:
#         result = subprocess.run([sys.executable, str(script_path)], 
#                               capture_output=True, text=True, check=True)
#         print(result.stdout)
#         print("✅ Пересоздание тем завершено успешно!")
#     except subprocess.CalledProcessError as e:
#         print(f"❌ Ошибка при пересоздании тем: {e}")
#         print(f"STDOUT: {e.stdout}")
#         print(f"STDERR: {e.stderr}")
#
# logger.info("✅ Recreate topics command registered")

# Web endpoints for development/admin tasks (DISABLED - not needed anymore)
if False:  # os.getenv('FLASK_ENV') == 'development' or os.getenv('LOAD_ADMIN_ENDPOINTS') == 'true':
    
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

    # Email client fix endpoint
    @app.route('/admin/fix-email-client', methods=['GET', 'POST'])
    def web_fix_email_client():
        """Веб-эндпоинт для исправления email client"""
        if request.method == 'GET':
            return """
            <html>
            <head><title>Fix Email Client</title></head>
            <body>
                <h1>Fix Email Client Database Schema</h1>
                <form method="POST">
                    <button type="submit">Fix Email Client</button>
                </form>
            </body>
            </html>
            """
        
        try:
            from scripts.fix_email_client import fix_email_client
            
            print("🔧 Starting email client fix...")
            success = fix_email_client()
            
            if success:
                return safe_jsonify({
                    'success': True,
                    'message': 'Email client database schema fixed successfully!'
                })
            else:
                return safe_jsonify({
                    'success': False,
                    'error': 'Failed to fix email client database schema'
                }), 500
                
        except Exception as e:
            error_details = str(e)
            print(f"Error in web_fix_email_client: {error_details}")
            
            return safe_jsonify({
                'success': False,
                'error': str(e),
                'details': error_details
            }), 500

    logger.info("✅ Web fix email client endpoint registered")

    # Add messages to topics endpoint
    @app.route('/admin/add-messages-to-topics', methods=['GET', 'POST'])
    def web_add_messages_to_topics():
        """Веб-эндпоинт для добавления сообщений в темы"""
        if request.method == 'GET':
            return """
            <html>
            <head><title>Add Messages to Topics</title></head>
            <body>
                <h1>Add Messages to Community Topics</h1>
                <p>This will add realistic conversation messages to existing topics.</p>
                <form method="POST">
                    <button type="submit">Add Messages to Topics</button>
                </form>
            </body>
            </html>
            """
        
        try:
            from scripts.add_messages_to_topics import add_messages_to_topics
            
            print("🔧 Starting add messages to topics...")
            success = add_messages_to_topics()
            
            if success:
                return safe_jsonify({
                    'success': True,
                    'message': 'Messages added to topics successfully!'
                })
            else:
                return safe_jsonify({
                    'success': False,
                    'error': 'Failed to add messages to topics'
                }), 500
                
        except Exception as e:
            error_details = str(e)
            print(f"Error in web_add_messages_to_topics: {error_details}")
            
            return safe_jsonify({
                'success': False,
                'error': str(e),
                'details': error_details
            }), 500
    
    logger.info("✅ Web add messages to topics endpoint registered")
    
    # Create production topics endpoint
    @app.route('/admin/create-production-topics', methods=['GET', 'POST'])
    def web_create_production_topics():
        """Веб-эндпоинт для создания тем с вашими переписками"""
        if request.method == 'GET':
            return """
            <html>
            <head><title>Create Production Topics</title></head>
            <body>
                <h1>Create Production Topics with Your Conversations</h1>
                <p>This will create topics with your original conversations from the script.</p>
                <ul>
                    <li>AKV tandartsen - BIG Registration Discussion 🦷</li>
                    <li>General Chat - Let's talk about everything! 💬</li>
                    <li>Welcome to Mentora Community! 👋</li>
                    <li>And 10 more topics...</li>
                </ul>
                <form method="POST">
                    <button type="submit">Create Topics with Your Conversations</button>
                </form>
            </body>
            </html>
            """
        
        try:
            from scripts.create_production_topics_fixed import create_production_topics
            
            print("🔧 Starting create production topics...")
            success = create_production_topics()
            
            if success:
                return safe_jsonify({
                    'success': True,
                    'message': 'Production topics with your conversations created successfully!'
                })
            else:
                return safe_jsonify({
                    'success': False,
                    'error': 'Failed to create production topics'
                }), 500
                
        except Exception as e:
            error_details = str(e)
            print(f"Error in web_create_production_topics: {error_details}")
            
            return safe_jsonify({
                'success': False,
                'error': str(e),
                'details': error_details
            }), 500
    
    logger.info("✅ Web create production topics endpoint registered")
    
    # Delete all topics endpoint
    @app.route('/admin/delete-all-topics', methods=['GET', 'POST'])
    def web_delete_all_topics():
        """Веб-эндпоинт для удаления всех тем"""
        if request.method == 'GET':
            return """
            <html>
            <head><title>Delete All Topics</title></head>
            <body>
                <h1>⚠️ Delete All Community Topics</h1>
                <p><strong>WARNING:</strong> This will permanently delete ALL topics and messages in the community!</p>
                <p>This action cannot be undone.</p>
                <form method="POST">
                    <button type="submit" style="background-color: red; color: white; padding: 10px 20px; border: none; border-radius: 5px;">DELETE ALL TOPICS</button>
                </form>
            </body>
            </html>
            """
        
        try:
            from scripts.delete_all_topics import delete_all_topics
            
            print("🗑️ Starting delete all topics...")
            success = delete_all_topics()
            
            if success:
                return safe_jsonify({
                    'success': True,
                    'message': 'All topics and messages deleted successfully!'
                })
            else:
                return safe_jsonify({
                    'success': False,
                    'error': 'Failed to delete topics'
                }), 500
                
        except Exception as e:
            error_details = str(e)
            print(f"Error in web_delete_all_topics: {error_details}")
            
            return safe_jsonify({
                'success': False,
                'error': str(e),
                'details': error_details
            }), 500
    
    logger.info("✅ Web delete all topics endpoint registered")
    
    # Add messages only endpoint
    @app.route('/admin/add-messages-only', methods=['GET', 'POST'])
    def web_add_messages_only():
        """Веб-эндпоинт для добавления только сообщений"""
        if request.method == 'GET':
            return """
            <html>
            <head><title>Add Messages Only</title></head>
            <body>
                <h1>Add Messages to Existing Topics</h1>
                <p>This will add your original conversations to existing topics.</p>
                <ul>
                    <li>AKV tandartsen - BIG Registration Discussion 🦷 (9 messages)</li>
                    <li>General Chat - Let's talk about everything! 💬 (4 messages)</li>
                </ul>
                <form method="POST">
                    <button type="submit">Add Messages to Topics</button>
                </form>
            </body>
            </html>
            """
        
        try:
            from scripts.add_messages_only import add_messages_only
            
            print("🔧 Starting add messages only...")
            success = add_messages_only()
            
            if success:
                return safe_jsonify({
                    'success': True,
                    'message': 'Messages added to topics successfully!'
                })
            else:
                return safe_jsonify({
                    'success': False,
                    'error': 'Failed to add messages'
                }), 500
                
        except Exception as e:
            error_details = str(e)
            print(f"Error in web_add_messages_only: {error_details}")
            
            return safe_jsonify({
                'success': False,
                'error': str(e),
                'details': error_details
            }), 500
    
    logger.info("✅ Web add messages only endpoint registered")
    
    # Force add messages endpoint
    @app.route('/admin/force-add-messages', methods=['GET', 'POST'])
    def web_force_add_messages():
        """Веб-эндпоинт для принудительного добавления сообщений"""
        if request.method == 'GET':
            return """
            <html>
            <head><title>Force Add Messages</title></head>
            <body>
                <h1>⚠️ Force Add Messages to Topics</h1>
                <p><strong>WARNING:</strong> This will DELETE existing messages and add your original conversations!</p>
                <ul>
                    <li>AKV tandartsen - BIG Registration Discussion 🦷 (9 messages)</li>
                    <li>General Chat - Let's talk about everything! 💬 (4 messages)</li>
                </ul>
                <form method="POST">
                    <button type="submit" style="background-color: orange; color: white; padding: 10px 20px; border: none; border-radius: 5px;">FORCE ADD MESSAGES</button>
                </form>
            </body>
            </html>
            """
        
        try:
            from scripts.force_add_messages import force_add_messages
            
            print("🔧 Starting force add messages...")
            success = force_add_messages()
            
            if success:
                return safe_jsonify({
                    'success': True,
                    'message': 'Messages force added to topics successfully!'
                })
            else:
                return safe_jsonify({
                    'success': False,
                    'error': 'Failed to force add messages'
                }), 500
                
        except Exception as e:
            error_details = str(e)
            print(f"Error in web_force_add_messages: {error_details}")
            
            return safe_jsonify({
                'success': False,
                'error': str(e),
                'details': error_details
            }), 500
    
    logger.info("✅ Web force add messages endpoint registered")
    
    # Debug messages endpoint
    @app.route('/admin/debug-messages', methods=['GET', 'POST'])
    def web_debug_messages():
        """Веб-эндпоинт для отладки сообщений"""
        if request.method == 'GET':
            return """
            <html>
            <head><title>Debug Messages</title></head>
            <body>
                <h1>🔍 Debug Messages in Topics</h1>
                <p>This will check and fix message counts in topics.</p>
                <form method="POST">
                    <button type="submit">Debug Messages</button>
                </form>
            </body>
            </html>
            """
        
        try:
            from scripts.check_messages_debug import check_messages_debug
            
            print("🔧 Starting debug messages...")
            success = check_messages_debug()
            
            if success:
                return safe_jsonify({
                    'success': True,
                    'message': 'Messages debug completed successfully!'
                })
            else:
                return safe_jsonify({
                    'success': False,
                    'error': 'Failed to debug messages'
                }), 500
                
        except Exception as e:
            error_details = str(e)
            print(f"Error in web_debug_messages: {error_details}")
            
            return safe_jsonify({
                'success': False,
                'error': str(e),
                'details': error_details
            }), 500
    
    logger.info("✅ Web debug messages endpoint registered")
    
    # Fix message authors endpoint
    @app.route('/admin/fix-message-authors', methods=['GET', 'POST'])
    def web_fix_message_authors():
        """Веб-эндпоинт для исправления авторов сообщений"""
        if request.method == 'GET':
            return """
            <html>
            <head><title>Fix Message Authors</title></head>
            <body>
                <h1>🔧 Fix Message Authors</h1>
                <p>This will fix invalid message authors and update message counts.</p>
                <form method="POST">
                    <button type="submit">Fix Message Authors</button>
                </form>
            </body>
            </html>
            """
        
        try:
            from scripts.fix_message_authors import fix_message_authors
            
            print("🔧 Starting fix message authors...")
            success = fix_message_authors()
            
            if success:
                return safe_jsonify({
                    'success': True,
                    'message': 'Message authors fixed successfully!'
                })
            else:
                return safe_jsonify({
                    'success': False,
                    'error': 'Failed to fix message authors'
                }), 500
                
        except Exception as e:
            error_details = str(e)
            print(f"Error in web_fix_message_authors: {error_details}")
            
            return safe_jsonify({
                'success': False,
                'error': str(e),
                'details': error_details
            }), 500
    
    logger.info("✅ Web fix message authors endpoint registered")
    
    # Add your conversations endpoint
    @app.route('/admin/add-your-conversations', methods=['GET', 'POST'])
    def web_add_your_conversations():
        """Веб-эндпоинт для добавления ваших оригинальных переписок"""
        if request.method == 'GET':
            return """
            <html>
            <head><title>Add Your Conversations</title></head>
            <body>
                <h1>💬 Add Your Original Conversations</h1>
                <p>This will add your original conversations using the working method from the old script.</p>
                <ul>
                    <li>AKV tandartsen - BIG Registration Discussion 🦷 (9 messages)</li>
                    <li>General Chat - Let's talk about everything! 💬 (4 messages)</li>
                </ul>
                <form method="POST">
                    <button type="submit">Add Your Conversations</button>
                </form>
            </body>
            </html>
            """
        
        try:
            from scripts.add_your_conversations import add_your_conversations
            
            print("🔧 Starting add your conversations...")
            success = add_your_conversations()
            
            if success:
                return safe_jsonify({
                    'success': True,
                    'message': 'Your original conversations added successfully!'
                })
            else:
                return safe_jsonify({
                    'success': False,
                    'error': 'Failed to add your conversations'
                }), 500
                
        except Exception as e:
            error_details = str(e)
            print(f"Error in web_add_your_conversations: {error_details}")
            
            return safe_jsonify({
                'success': False,
                'error': str(e),
                'details': error_details
            }), 500
    
    logger.info("✅ Web add your conversations endpoint registered")
    
    # Diagnose conversations endpoint
    @app.route('/admin/diagnose-conversations', methods=['GET', 'POST'])
    def web_diagnose_conversations():
        """Веб-эндпоинт для диагностики проблем с переписками"""
        if request.method == 'GET':
            return """
            <html>
            <head><title>Diagnose Conversations</title></head>
            <body>
                <h1>🔍 Diagnose Conversations</h1>
                <p>This will check users, topics, and messages to find the issue.</p>
                <form method="POST">
                    <button type="submit">Run Diagnosis</button>
                </form>
            </body>
            </html>
            """
        
        try:
            from scripts.diagnose_conversations import diagnose_conversations
            
            print("🔧 Starting diagnose conversations...")
            success = diagnose_conversations()
            
            if success:
                return safe_jsonify({
                    'success': True,
                    'message': 'Diagnosis completed successfully! Check logs for details.'
                })
            else:
                return safe_jsonify({
                    'success': False,
                    'error': 'Diagnosis failed'
                }), 500
                
        except Exception as e:
            error_details = str(e)
            print(f"Error in web_diagnose_conversations: {error_details}")
            
            return safe_jsonify({
                'success': False,
                'error': str(e),
                'details': error_details
            }), 500
    
    logger.info("✅ Web diagnose conversations endpoint registered")
    
    # Simple add conversations endpoint
    @app.route('/admin/simple-add-conversations', methods=['GET', 'POST'])
    def web_simple_add_conversations():
        """Веб-эндпоинт для простого добавления переписок"""
        if request.method == 'GET':
            return """
            <html>
            <head><title>Simple Add Conversations</title></head>
            <body>
                <h1>💬 Simple Add Conversations</h1>
                <p>This will add your conversations to topics WITHOUT messages (exactly like the old working script).</p>
                <form method="POST">
                    <button type="submit">Add Conversations to Empty Topics</button>
                </form>
            </body>
            </html>
            """
        
        try:
            from scripts.simple_add_conversations import simple_add_conversations
            
            print("🔧 Starting simple add conversations...")
            success = simple_add_conversations()
            
            if success:
                return safe_jsonify({
                    'success': True,
                    'message': 'Conversations added to empty topics successfully!'
                })
            else:
                return safe_jsonify({
                    'success': False,
                    'error': 'Failed to add conversations'
                }), 500
                
        except Exception as e:
            error_details = str(e)
            print(f"Error in web_simple_add_conversations: {error_details}")
            
            return safe_jsonify({
                'success': False,
                'error': str(e),
                'details': error_details
            }), 500
    
    logger.info("✅ Web simple add conversations endpoint registered")
    
    # Fix conversations precise endpoint
    @app.route('/admin/fix-conversations-precise', methods=['GET', 'POST'])
    def web_fix_conversations_precise():
        """Веб-эндпоинт для точного исправления переписок"""
        if request.method == 'GET':
            return """
            <html>
            <head><title>Fix Conversations Precise</title></head>
            <body>
                <h1>🎯 Fix Conversations Precise</h1>
                <p>This will:</p>
                <ul>
                    <li>Delete ALL existing messages</li>
                    <li>Add your conversations to the CORRECT topics</li>
                    <li>Fix the display issue</li>
                </ul>
                <form method="POST">
                    <button type="submit">Fix Conversations Precisely</button>
                </form>
            </body>
            </html>
            """
        
        try:
            from scripts.fix_conversations_precise import fix_conversations_precise
            
            print("🔧 Starting fix conversations precise...")
            success = fix_conversations_precise()
            
            if success:
                return safe_jsonify({
                    'success': True,
                    'message': 'Conversations fixed precisely! Messages added to correct topics.'
                })
            else:
                return safe_jsonify({
                    'success': False,
                    'error': 'Failed to fix conversations'
                }), 500
                
        except Exception as e:
            error_details = str(e)
            print(f"Error in web_fix_conversations_precise: {error_details}")
            
            return safe_jsonify({
                'success': False,
                'error': str(e),
                'details': error_details
            }), 500
    
    # Add real conversations endpoint
    @app.route('/admin/add-real-conversations', methods=['GET', 'POST'])
    def web_add_real_conversations():
        """Веб-эндпоинт для добавления реальных переписок пользователя"""
        if request.method == 'GET':
            return """
            <html>
            <head><title>Add Real Conversations</title></head>
            <body>
                <h1>🎯 Add Your Real Conversations</h1>
                <p>This will:</p>
                <ul>
                    <li>Add your conversations from create_production_topics.py</li>
                    <li>Replace existing messages in topics</li>
                    <li>Use correct authors and timing</li>
                </ul>
                <form method="POST">
                    <button type="submit">Add Real Conversations</button>
                </form>
            </body>
            </html>
            """
        
        try:
            from scripts.add_your_real_conversations import add_real_conversations
            
            print("🔧 Starting add real conversations...")
            add_real_conversations()
            
            return safe_jsonify({
                'success': True,
                'message': 'Real conversations added successfully!'
            })
                
        except Exception as e:
            error_details = str(e)
            print(f"Error in web_add_real_conversations: {error_details}")
            
            return safe_jsonify({
                'success': False,
                'error': f'Error: {error_details}'
            }), 500
    
    # Add fake conversations endpoint
    @app.route('/admin/add-fake-conversations', methods=['GET', 'POST'])
    def web_add_fake_conversations():
        """Веб-эндпоинт для добавления фейковых переписок"""
        if request.method == 'GET':
            return """
            <html>
            <head><title>Add Fake Conversations</title></head>
            <body>
                <h1>💬 Add Fake Conversations</h1>
                <p>This will:</p>
                <ul>
                    <li>Add realistic conversations to existing topics</li>
                    <li>Create fake users if needed</li>
                    <li>Replace existing messages with new ones</li>
                </ul>
                <form method="POST">
                    <button type="submit">Add Fake Conversations</button>
                </form>
            </body>
            </html>
            """
        
        try:
            from scripts.add_fake_conversations_simple import add_fake_conversations
            
            print("🔧 Starting add fake conversations...")
            add_fake_conversations()
            
            return safe_jsonify({
                'success': True,
                'message': 'Fake conversations added successfully!'
            })
                
        except Exception as e:
            error_details = str(e)
            print(f"Error in web_add_fake_conversations: {error_details}")
            
            return safe_jsonify({
                'success': False,
                'error': f'Error: {error_details}'
            }), 500
    
    # Add smart fake conversations endpoint
    @app.route('/admin/add-smart-fake-conversations', methods=['GET', 'POST'])
    def web_add_smart_fake_conversations():
        """Веб-эндпоинт для добавления умных фейковых переписок"""
        if request.method == 'GET':
            return """
            <html>
            <head><title>Add Smart Fake Conversations</title></head>
            <body>
                <h1>🧠 Add Smart Fake Conversations</h1>
                <p>This will:</p>
                <ul>
                    <li>Add topic-specific conversations to each forum topic</li>
                    <li>Match conversations to topic content (BIG registration, study materials, etc.)</li>
                    <li>Create realistic discussions with proper context</li>
                    <li>Replace existing messages with relevant ones</li>
                </ul>
                <form method="POST">
                    <button type="submit">Add Smart Fake Conversations</button>
                </form>
            </body>
            </html>
            """
        
        try:
            from scripts.add_smart_fake_conversations import add_smart_fake_conversations
            
            print("🔧 Starting add smart fake conversations...")
            add_smart_fake_conversations()
            
            return safe_jsonify({
                'success': True,
                'message': 'Smart fake conversations added successfully!'
            })
                
        except Exception as e:
            error_details = str(e)
            print(f"Error in web_add_smart_fake_conversations: {error_details}")
            
            return safe_jsonify({
                'success': False,
                'error': f'Error: {error_details}'
            }), 500
    
    # Debug conversations endpoint
    @app.route('/admin/debug-conversations', methods=['GET', 'POST'])
    def web_debug_conversations():
        """Веб-эндпоинт для диагностики переписок"""
        if request.method == 'GET':
            return """
            <html>
            <head><title>Debug Conversations</title></head>
            <body>
                <h1>🔍 Debug Conversations</h1>
                <p>This will check:</p>
                <ul>
                    <li>Number of users, topics, and posts</li>
                    <li>Posts per topic</li>
                    <li>Recent messages</li>
                    <li>User details</li>
                </ul>
                <form method="POST">
                    <button type="submit">Run Diagnostics</button>
                </form>
            </body>
            </html>
            """
        
        try:
            from scripts.debug_conversations import debug_conversations
            
            print("🔧 Starting conversation diagnostics...")
            debug_conversations()
            
            return safe_jsonify({
                'success': True,
                'message': 'Diagnostics completed! Check server logs for details.'
            })
                
        except Exception as e:
            error_details = str(e)
            print(f"Error in web_debug_conversations: {error_details}")
            
            return safe_jsonify({
                'success': False,
                'error': f'Error: {error_details}'
            }), 500
    
    # Add simple conversations endpoint
    @app.route('/admin/add-simple-conversations', methods=['GET', 'POST'])
    def web_add_simple_conversations():
        """Веб-эндпоинт для добавления простых переписок"""
        if request.method == 'GET':
            return """
            <html>
            <head><title>Add Simple Conversations</title></head>
            <body>
                <h1>💬 Add Simple Conversations</h1>
                <p>This will:</p>
                <ul>
                    <li>Add 3-5 simple messages to each topic</li>
                    <li>Use basic messages like "Hello everyone!", "Great topic!"</li>
                    <li>Use the first available user as author</li>
                    <li>Replace existing messages</li>
                </ul>
                <form method="POST">
                    <button type="submit">Add Simple Conversations</button>
                </form>
            </body>
            </html>
            """
        
        try:
            from scripts.add_simple_conversations import add_simple_conversations
            
            print("🔧 Starting simple conversations...")
            add_simple_conversations()
            
            return safe_jsonify({
                'success': True,
                'message': 'Simple conversations added successfully!'
            })
                
        except Exception as e:
            error_details = str(e)
            print(f"Error in web_add_simple_conversations: {error_details}")
            
            return safe_jsonify({
                'success': False,
                'error': f'Error: {error_details}'
            }), 500
    
    logger.info("✅ Web fix conversations precise endpoint registered")
    logger.info("✅ Web add fake conversations endpoint registered")
    logger.info("✅ Web add smart fake conversations endpoint registered")
    logger.info("✅ Web debug conversations endpoint registered")
    logger.info("✅ Web add simple conversations endpoint registered")
    
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
    # DISABLED: Force load data command (not needed anymore)
    # @app.cli.command()
    # def force_load_data():
    #     """Принудительно загрузить данные на production"""
    #     import subprocess
    #     import sys
    #     from pathlib import Path
    #
    #     script_path = Path(__file__).parent / 'scripts' / 'force_load_production_data.py'
    #
    #     if not script_path.exists():
    #         print(f"❌ Script not found: {script_path}")
    #         sys.exit(1)
    #
    #     try:
    #         result = subprocess.run([sys.executable, str(script_path)],
    #                               capture_output=True, text=True, check=True)
    #         print(result.stdout)
    #         print("✅ Принудительная загрузка данных завершена успешно!")
    #     except subprocess.CalledProcessError as e:
    #         print(f"❌ Ошибка при принудительной загрузке данных: {e}")
    #         print(f"STDOUT: {e.stdout}")
    #         print(f"STDERR: {e.stderr}")
    #         sys.exit(1)
    #
    # logger.info("✅ Force load data command registered")

else:
    logger.info("🚀 Admin endpoints skipped (production mode)")

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
# REGISTRATION TRACKING ENDPOINTS (NO LANGUAGE PREFIX)
# ========================================

@app.route('/track-registration-visit', methods=['POST'])
@csrf.exempt
def track_registration_visit():
    """Track registration page visits"""
    try:
        data = request.get_json()
        logger.info(f"Registration visit tracked: {data}")
        return safe_jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error tracking registration visit: {str(e)}")
        return safe_jsonify({'success': False, 'error': str(e)}), 500

@app.route('/track-form-start', methods=['POST'])
@csrf.exempt
def track_form_start():
    """Track form start events"""
    try:
        data = request.get_json()
        logger.info(f"Form start tracked: {data}")
        return safe_jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error tracking form start: {str(e)}")
        return safe_jsonify({'success': False, 'error': str(e)}), 500

@app.route('/track-form-submit', methods=['POST'])
@csrf.exempt
def track_form_submit():
    """Track form submission events"""
    try:
        data = request.get_json()
        logger.info(f"Form submit tracked: {data}")
        return safe_jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error tracking form submit: {str(e)}")
        return safe_jsonify({'success': False, 'error': str(e)}), 500

@app.route('/track-page-exit', methods=['POST'])
@csrf.exempt
def track_page_exit():
    """Track page exit events"""
    try:
        data = request.get_json()
        logger.info(f"Page exit tracked: {data}")
        return safe_jsonify({'success': True})
    except Exception as e:
        logger.error(f"Error tracking page exit: {str(e)}")
        return safe_jsonify({'success': False, 'error': str(e)}), 500

@app.route("/track-email-entry", methods=["POST"])
@csrf.exempt
def track_email_entry():
    """Track email entry events"""
    try:
        data = request.get_json()
        email = data.get("email")
        page_type = data.get("page_type")
        
        if not email or not page_type:
            return safe_jsonify({"success": False, "error": "Missing email or page_type"}), 400
        
        # Use VisitorTracker to actually track the email entry
        from utils.visitor_tracker import VisitorTracker
        success = VisitorTracker.track_email_entry(email, page_type)
        
        if success:
            logger.info(f"✅ Email entry tracked successfully: {email} on {page_type}")
            return safe_jsonify({"success": True})
        else:
            logger.warning(f"⚠️ Failed to track email entry: {email} on {page_type}")
            # Не возвращаем ошибку 500, так как это может быть нормально (нет активной сессии)
            return safe_jsonify({"success": False, "message": "No active visitor session"})
            
    except Exception as e:
        logger.error(f"❌ Error tracking email entry: {str(e)}")
        return safe_jsonify({"success": False, "error": str(e)}), 500
# ========================================

@app.route("/track-name-entry", methods=["POST"])
@csrf.exempt
def track_name_entry():
    """Track name entry events"""
    try:
        data = request.get_json()
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        page_type = data.get("page_type")
        
        if not first_name or not last_name or not page_type:
            return safe_jsonify({"success": False, "error": "Missing first_name, last_name or page_type"}), 400
        
        # Use VisitorTracker to actually track the name entry
        from utils.visitor_tracker import VisitorTracker
        success = VisitorTracker.track_name_entry(first_name, last_name, page_type)
        
        if success:
            logger.info(f"✅ Name entry tracked successfully: {first_name} {last_name} on {page_type}")
            return safe_jsonify({"success": True})
        else:
            logger.warning(f"⚠️ Failed to track name entry: {first_name} {last_name} on {page_type}")
            return safe_jsonify({"success": False, "error": "Failed to track name entry"}), 500
            
    except Exception as e:
        logger.error(f"❌ Error tracking name entry: {str(e)}")
        return safe_jsonify({"success": False, "error": str(e)}), 500# APPLICATION ENTRY POINT
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
    
    # Admin user deletion routes (bypass CSRF issues)
    @app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
    @login_required
    @csrf.exempt
    def admin_delete_user(user_id):
        """Delete user (admin only) - bypass CSRF"""
        from utils.decorators import admin_required
        from models import User
        
        if not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        user = User.query.get_or_404(user_id)
        
        # Prevent deleting yourself
        if user.id == current_user.id:
            return jsonify({'error': 'Cannot delete own account'}), 400
        
        try:
            user_email = user.email
            db.session.delete(user)
            db.session.commit()
            
            return jsonify({'success': True, 'message': f'User {user_email} deleted'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Error deleting user: {str(e)}'}), 500

    @app.route('/admin/users/bulk-actions', methods=['POST'])
    @login_required
    @csrf.exempt
    def admin_bulk_user_actions():
        """Bulk actions on users - bypass CSRF"""
        from models import User
        
        if not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        action = request.form.get('action')
        selected_items = request.form.getlist('selected_items')
        
        if not selected_items:
            return jsonify({'error': 'No items selected'}), 400
        
        try:
            if action == 'delete':
                # Get user emails for logging before deletion
                users_to_delete = User.query.filter(User.id.in_(selected_items)).all()
                user_emails = [user.email for user in users_to_delete]
                
                # Prevent deleting admins
                admin_users = [user for user in users_to_delete if user.is_admin]
                if admin_users:
                    return jsonify({'error': 'Cannot delete admin users'}), 400
                
                # Delete users
                User.query.filter(User.id.in_(selected_items)).delete()
                db.session.commit()
                
                return jsonify({'success': True, 'message': f'Deleted {len(selected_items)} users'})
            else:
                return jsonify({'error': f'Unknown action: {action}'}), 400
                
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': f'Error: {str(e)}'}), 500

    # Create admin user if it doesn't exist (production only)
    with app.app_context():
        create_admin_if_not_exists()
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    ) 
