# extensions.py - Flask Extensions (Clean Version)
# Only essential extensions for core functionality

from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_babel import Babel
from flask_caching import Cache
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_mail import Mail

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
babel = Babel()
cache = Cache()
csrf = CSRFProtect()
migrate = Migrate()
mail = Mail()

def init_extensions(app):
    """Initialize all Flask extensions with the app"""
    
    # Database
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Authentication
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    # Custom login redirect handler to preserve language
    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import request, redirect, url_for, session
        # Get current language from URL or session
        lang = None
        if request.view_args and 'lang' in request.view_args:
            lang = request.view_args['lang']
        elif session.get('lang'):
            lang = session['lang']
        else:
            # Try to extract from referrer URL
            if request.referrer:
                import re
                match = re.search(r'/([a-z]{2})/', request.referrer)
                if match:
                    lang = match.group(1)
        
        # Default to Dutch if no language found
        if not lang or lang not in ['nl', 'en', 'ru', 'uk', 'es', 'pt', 'tr', 'fa', 'ar']:
            lang = 'nl'
        
        # Store the original URL for redirect after login
        session['next'] = request.url
        
        # Redirect to login with language preserved
        return redirect(url_for('auth.login', lang=lang))
    
    # Password hashing
    bcrypt.init_app(app)
    
    # Internationalization
    babel.init_app(app)
    
    # Caching
    cache.init_app(app)
    
    # CSRF Protection
    csrf.init_app(app)
    
    # Email
    mail.init_app(app)
    
    print("✅ All Flask extensions initialized successfully")
    
    return db, login_manager, bcrypt, babel, cache, csrf, mail 