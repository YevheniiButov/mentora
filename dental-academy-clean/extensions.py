# extensions.py - Flask Extensions (Clean Version)
# Only essential extensions for core functionality

import os
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_babel import Babel
from flask_caching import Cache
from flask_wtf.csrf import CSRFProtect
from flask_migrate import Migrate
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
bcrypt = Bcrypt()
babel = Babel()
cache = Cache()
csrf = CSRFProtect()
migrate = Migrate()
mail = Mail()
# Limiter will be initialized in init_extensions with proper storage backend
limiter = None

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
        # BUT: Don't store API endpoints (they should return JSON, not HTML)
        if not request.url.startswith('/api/'):
            session['next'] = request.url
        
        # Redirect to login with language preserved
        # Use direct URL instead of url_for to avoid BuildError
        return redirect(f'/auth/{lang}/login' if lang else '/auth/login')
    
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
    
    # Rate Limiting
    # Configure storage backend for production (Redis) or use memory for development
    global limiter
    redis_url = app.config.get('REDIS_URL') or os.environ.get('REDIS_URL')
    if redis_url:
        # Use Redis storage backend for production (works with multiple workers)
        # storage_uri must be passed when creating Limiter, not in init_app()
        limiter = Limiter(
            key_func=get_remote_address,
            storage_uri=redis_url,
            app=app
        )
        print(f"✅ Flask-Limiter configured with Redis storage: {redis_url.split('@')[-1] if '@' in redis_url else 'redis'}")
    else:
        # Use memory storage for development (not recommended for production)
        limiter = Limiter(key_func=get_remote_address, app=app)
        if app.config.get('FLASK_ENV') == 'production':
            print("⚠️  WARNING: Flask-Limiter using in-memory storage in production. Set REDIS_URL for proper rate limiting.")
        else:
            print("ℹ️  Flask-Limiter using in-memory storage (development mode)")
    
    # Set default rate limits
    limiter.enabled = True
    
    print("✅ All Flask extensions initialized successfully")
    
    return db, login_manager, bcrypt, babel, cache, csrf, mail, limiter 