# app.py - Clean Mentora Application
# Minimal Flask app with core functionality only

import os
import logging
import json
from datetime import datetime, timezone
from flask import Flask, render_template, request, session, g, redirect, url_for, flash, send_from_directory, abort
from utils.serializers import safe_jsonify
from flask_login import current_user, login_user, logout_user, login_required
# Заменяем импорт на более конкретный
try:
    from flask_babel import get_locale
except ImportError:
    # Fallback функция, если flask_babel не установлен
    def get_locale():
        return 'en'

# Import extensions and models
from extensions import init_extensions, db, login_manager, babel
from models import User, LearningPath, Subject, Module, Lesson, create_sample_data, DigiDSession, UserProgress, Test, Question, QuestionCategory
from translations import get_translation, get_available_languages, DEFAULT_LANGUAGE, LANGUAGE_NAMES, RTL_LANGUAGES, COUNTRY_CODES
from flask_wtf.csrf import CSRFProtect
from utils.serializers import setup_json_serialization

app = Flask(__name__)
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

# Initialize CSRF protection
csrf = CSRFProtect(app)
# Temporarily disable CSRF for testing
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
                flash('Ваша DigiD сессия истекла. Пожалуйста, войдите снова.', 'warning')
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

# ========================================
# MAIN ROUTES (always available)
# ========================================

@app.route('/')
@app.route('/<string:lang>/')
def index(lang='nl'):
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
    from routes.learning_map_routes import learning_map_bp, profession_map_bp
    from routes.lesson_routes import lesson_bp
    from routes.modules_routes import modules_bp
    from routes.content_navigation import content_nav_bp
    from routes.content_routes import content_bp
    
    # Импорт DigiD роутов
    from routes.digid_routes import digid_bp
    
    # Импорт AI Assistant роутов
    from routes.ai_assistant_routes import ai_assistant_bp
    
    # Импорт Diagnostic роутов
    from routes.diagnostic_routes import diagnostic_bp
    
    # Импорт Testing роутов
    from routes.testing_routes import testing_bp
    
    # Импорт Learning Planner роутов
    from routes.learning_planner_routes import learning_planner_bp
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(learning_bp, url_prefix='/learning')
    app.register_blueprint(test_bp, url_prefix='/tests')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(virtual_patient_bp)
    
    # Регистрация новых blueprint-ов системы обучения
    app.register_blueprint(subject_view_bp)
    app.register_blueprint(learning_map_bp)
    app.register_blueprint(profession_map_bp)  # Профессиональные карты обучения
    app.register_blueprint(lesson_bp, url_prefix='/lesson')
    app.register_blueprint(modules_bp)
    app.register_blueprint(content_nav_bp, url_prefix='/content')
    app.register_blueprint(content_bp, url_prefix='/content')
    
    # Регистрация DigiD blueprint
    app.register_blueprint(digid_bp)
    
    # Регистрация AI Assistant blueprint
    app.register_blueprint(ai_assistant_bp)
    
    # Регистрация Diagnostic blueprint
    app.register_blueprint(diagnostic_bp, url_prefix='/big-diagnostic')
    
    # Регистрация Testing blueprint
    app.register_blueprint(testing_bp, url_prefix='/testing')
    
    # Регистрация Learning Planner blueprint
    app.register_blueprint(learning_planner_bp, url_prefix='/dashboard')
    
    # Отключить CSRF для DigiD API роутов
    csrf.exempt(digid_bp)
    
    # Отключить CSRF для Diagnostic API роутов (временно для тестирования)
    csrf.exempt(diagnostic_bp)
    
    logger.info("✅ All route blueprints registered successfully")
    
except ImportError as e:
    logger.warning(f"Could not import routes: {e}")
    logger.info("Creating minimal routes...")
    
    # Все равно пытаемся зарегистрировать DigiD blueprint
    try:
        from routes.digid_routes import digid_bp
        app.register_blueprint(digid_bp)
        csrf.exempt(digid_bp)
        logger.info("✅ DigiD blueprint registered successfully")
    except ImportError as digid_error:
        logger.warning(f"Could not import DigiD routes: {digid_error}")
    
    # Пытаемся зарегистрировать Diagnostic blueprint
    try:
        from routes.diagnostic_routes import diagnostic_bp
        app.register_blueprint(diagnostic_bp)
        logger.info("✅ Diagnostic blueprint registered successfully")
    except ImportError as diagnostic_error:
        logger.warning(f"Could not import Diagnostic routes: {diagnostic_error}")
    
    @app.route('/big_info')
    def big_info():
        return render_template('big_info.html')
    
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
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                return redirect(url_for('index'))
            else:
                from flask import flash
                flash('Неверное имя пользователя или пароль', 'error')
        
        return redirect(url_for('auth.digid_login'))
    
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
                db.session.add(user)
                db.session.commit()
                
                login_user(user)
                return redirect(url_for('index'))
        
        return render_template('auth/register.html')
    
    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('index'))
    
    @app.route('/profile')
    def profile():
        return render_template('auth/profile.html')
    
    @app.route('/edit_profile')
    def edit_profile():
        return render_template('auth/edit_profile.html')
    
    # Removed conflicting route - using blueprint instead

# ========================================
# SIMPLE TEST ROUTES
# ========================================

@app.route('/ai-test')
def ai_test():
    """Simple AI test route"""
    return safe_jsonify({
        'message': 'AI test successful',
        'status': 'ok'
    })

@app.route('/learning-map/')
def learning_map_redirect():
    """Redirect old learning-map URLs to new format"""
    lang = request.args.get('lang', 'ru')
    return redirect(url_for('learning_map_bp.learning_map', lang=lang))

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

logger.info("🦷 Mentora Clean application created successfully!")

# Import questions command
try:
    from commands.import_questions import import_questions
    app.cli.add_command(import_questions)
    logger.info("✅ Import questions command registered")
except ImportError as e:
    logger.warning(f"⚠️ Import questions command not available: {e}")

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
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    ) 
