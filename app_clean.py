# app.py - Clean Dental Academy Application
# Minimal Flask app with core functionality only

import os
import logging
from datetime import datetime, timezone
from flask import Flask, render_template, request, session, g, redirect, url_for
from flask_login import current_user
from flask_babel import get_locale

# Import extensions and models
from extensions import init_extensions, db, login_manager, babel
from models import User, LearningPath, Subject, Module, Lesson, create_sample_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Supported languages
SUPPORTED_LANGUAGES = ['en', 'ru', 'nl', 'uk', 'es', 'pt', 'tr', 'fa', 'ar']
DEFAULT_LANGUAGE = 'en'

def create_app(config_name='development'):
    """Application factory"""
    app = Flask(__name__)
    
    # ========================================
    # CONFIGURATION
    # ========================================
    
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database configuration
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Production database (PostgreSQL)
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        # Development database (SQLite)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dental_academy_clean.db'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    
    # Security
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_TIME_LIMIT'] = 3600
    
    # Internationalization
    app.config['LANGUAGES'] = {
        'en': 'English',
        'ru': 'Русский',
        'nl': 'Nederlands',
        'uk': 'Українська',
        'es': 'Español',
        'pt': 'Português',
        'tr': 'Türkçe',
        'fa': 'فارسی',
        'ar': 'العربية'
    }
    app.config['BABEL_DEFAULT_LOCALE'] = DEFAULT_LANGUAGE
    app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'
    
    # Cache
    app.config['CACHE_TYPE'] = 'simple'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 300
    
    # ========================================
    # INITIALIZE EXTENSIONS
    # ========================================
    
    init_extensions(app)
    
    # ========================================
    # USER LOADER
    # ========================================
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user for Flask-Login"""
        return User.query.get(int(user_id))
    
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
    
    # ========================================
    # TEMPLATE HELPERS
    # ========================================
    
    @app.context_processor
    def inject_template_vars():
        """Inject variables into all templates"""
        
        # Простая функция перевода для начала
        def simple_translate(key, lang=None):
            """Simple translation function"""
            if lang is None:
                lang = g.get('locale', DEFAULT_LANGUAGE)
            
            # Базовые переводы для старта
            translations = {
                'en': {
                    'home': 'Home',
                    'dashboard': 'Dashboard',
                    'learning_map': 'Learning Map',
                    'seo_title': 'Dental Academy - Professional Education',
                    'app_title': 'Dental Academy',
                    'learning': 'Learning',
                    'tests': 'Tests',
                    'profile': 'Profile',
                    'login': 'Login',
                    'register': 'Register',
                    'logout': 'Logout',
                    'welcome': 'Welcome',
                    'get_started': 'Get Started'
                },
                'ru': {
                    'home': 'Главная',
                    'dashboard': 'Панель',
                    'learning_map': 'Карта обучения',
                    'seo_title': 'Dental Academy - Профессиональное образование',
                    'app_title': 'Dental Academy',
                    'learning': 'Обучение',
                    'tests': 'Тесты',
                    'profile': 'Профиль',
                    'login': 'Вход',
                    'register': 'Регистрация',
                    'logout': 'Выход',
                    'welcome': 'Добро пожаловать',
                    'get_started': 'Начать'
                },
                'nl': {
                    'home': 'Home',
                    'dashboard': 'Dashboard',
                    'learning_map': 'Leerkaart',
                    'seo_title': 'Dental Academy - Professioneel onderwijs',
                    'app_title': 'Dental Academy',
                    'learning': 'Leren',
                    'tests': 'Tests',
                    'profile': 'Profiel',
                    'login': 'Inloggen',
                    'register': 'Registreren',
                    'logout': 'Uitloggen',
                    'welcome': 'Welkom',
                    'get_started': 'Beginnen'
                }
            }
            
            return translations.get(lang, translations['en']).get(key, key)
        
        def get_country_code(lang_code):
            """Возвращает код страны для флага"""
            lang_to_country = {
                'en': 'gb', 'nl': 'nl', 'ru': 'ru', 'uk': 'ua',
                'es': 'es', 'pt': 'pt', 'tr': 'tr', 'fa': 'ir'
            }
            return lang_to_country.get(lang_code, lang_code)
        
        return {
            'current_year': datetime.now().year,
            'app_name': 'Dental Academy',
            'supported_languages': app.config['LANGUAGES'],
            'current_language': g.get('locale', DEFAULT_LANGUAGE),
            'user': current_user if current_user.is_authenticated else None,
            't': simple_translate,
            'lang': g.get('locale', DEFAULT_LANGUAGE),
            'get_country_code': get_country_code
        }
    
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
        
        # Register blueprints
        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp, url_prefix='/auth')
        app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
        app.register_blueprint(learning_bp, url_prefix='/learning')
        app.register_blueprint(test_bp, url_prefix='/tests')
        app.register_blueprint(admin_bp, url_prefix='/admin')
        app.register_blueprint(virtual_patient_bp)
        
        logger.info("✅ All route blueprints registered successfully")
        
    except ImportError as e:
        logger.warning(f"Could not import routes: {e}")
        logger.info("Creating minimal routes...")
        
        # Create minimal routes if blueprints don't exist
        @app.route('/')
        def index():
            return render_template('index.html')
        
        @app.route('/dashboard')
        def dashboard():
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            return render_template('dashboard.html')
        
        @app.route('/login')
        def login():
            return render_template('auth/login.html')
    
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
    
    @app.cli.command('init-db')
    def init_db():
        """Initialize the database"""
        try:
            db.create_all()
            logger.info("✅ Database tables created successfully")
        except Exception as e:
            logger.error(f"❌ Error creating database tables: {e}")
    
    @app.cli.command('create-admin')
    def create_admin():
        """Create an admin user"""
        try:
            # Check if admin already exists
            admin = User.query.filter_by(role='admin').first()
            if admin:
                logger.info(f"Admin user already exists: {admin.username}")
                return
            
            # Create admin user
            admin = User(
                username='admin',
                email='admin@dentalacademy.com',
                first_name='Admin',
                last_name='User',
                role='admin',
                is_active=True
            )
            admin.set_password('admin123')  # Change this in production!
            
            db.session.add(admin)
            db.session.commit()
            
            logger.info("✅ Admin user created successfully")
            logger.info("Username: admin")
            logger.info("Password: admin123")
            logger.warning("⚠️ Please change the admin password in production!")
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"❌ Error creating admin user: {e}")
    
    @app.cli.command('create-sample-data')
    def create_sample_data_cli():
        """Create sample learning content"""
        try:
            stats = create_sample_data()
            logger.info("✅ Sample data created successfully!")
            logger.info(f"Created: {stats}")
        except Exception as e:
            logger.error(f"❌ Error creating sample data: {e}")
    
    @app.cli.command('reset-db')
    def reset_db():
        """Reset the database (WARNING: Deletes all data!)"""
        try:
            db.drop_all()
            db.create_all()
            logger.info("✅ Database reset successfully")
            logger.warning("⚠️ All data has been deleted!")
        except Exception as e:
            logger.error(f"❌ Error resetting database: {e}")
    
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
    
    logger.info("🦷 Dental Academy Clean application created successfully!")
    return app

# ========================================
# APPLICATION ENTRY POINT
# ========================================

if __name__ == '__main__':
    # Create the application
    app = create_app()
    
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
    
    logger.info(f"🚀 Starting Dental Academy Clean on port {port}")
    logger.info(f"🔧 Debug mode: {debug}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    ) 