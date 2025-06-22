from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, session, g, current_app,
    jsonify
)
from flask_login import (
    login_user, logout_user, login_required, current_user
)
from extensions import db, bcrypt
from models import User
from forms import LoginForm, RegistrationForm, ChangePasswordForm # Предполагаем, что формы в корневом forms.py

# Исправление 1: **name** должно быть __name__ (двойное подчеркивание)
auth_bp = Blueprint("auth_bp", __name__, url_prefix='/<string:lang>')

# --- Context Processor ---
@auth_bp.context_processor
def inject_lang():
    """Добавляет lang (из g.lang) в контекст шаблонов."""
    lang = getattr(g, 'lang', current_app.config['DEFAULT_LANGUAGE'])
    return dict(lang=lang)

# --- Маршрут для входа пользователей ---
@auth_bp.route("/login", methods=["GET", "POST"])
def login(lang):
    g.lang = lang
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.profile', lang=lang))
    
    form = LoginForm()
    if form.validate_on_submit():
        current_app.logger.info(f"Login attempt for email: {form.email.data}")
        current_app.logger.info(f"Form data: {form.data}")
        
        # Проверяем длину пароля
        if len(form.password.data) < 6:
            current_app.logger.warning(f"Password too short for user {form.email.data}")
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html", form=form, title="Login")
        
        user = User.query.filter_by(email=form.email.data).first()
        
        if not user:
            current_app.logger.warning(f"User not found for email: {form.email.data}")
            flash("Invalid email or password.", "danger")
            return render_template("auth/login.html", form=form, title="Login")
        
        current_app.logger.info(f"Found user: {user.email}, role: {user.role}")
        current_app.logger.info(f"User password hash: {user.password_hash[:20]}...")
        
        # Проверка валидности хеша
        valid_hash = False
        try:
            if user.password_hash:
                current_app.logger.info(f"Password hash format: {user.password_hash[:10]}...")
                if user.password_hash.startswith('$2b$') or user.password_hash.startswith('$2a$'):
                    valid_hash = True
                    current_app.logger.info("Password hash format is valid")
                else:
                    current_app.logger.warning("Invalid password hash format")
        except Exception as e:
            current_app.logger.error(f"Error checking password hash: {e}")
        
        # Проверяем пароль
        try:
            password_correct = False
            if valid_hash:
                password_correct = bcrypt.check_password_hash(user.password_hash, form.password.data)
                current_app.logger.info(f"Password check result: {password_correct}")
            
            if password_correct:
                login_user(user, remember=form.remember_me.data if hasattr(form, 'remember_me') else False)
                current_app.logger.info(f"User {user.email} logged in successfully")
                flash("Successfully logged in!", "success")
                
                next_page = request.args.get('next')
                if next_page and not next_page.startswith('/'):
                    next_page = None
                
                profile_url_success = url_for("main_bp.profile", lang=lang)
                return redirect(next_page or profile_url_success)
            else:
                current_app.logger.warning(f"Invalid password for user {user.email}")
                flash("Invalid email or password.", "danger")
        except ValueError as e:
            current_app.logger.error(f"Password hash error for user {form.email.data}: {e}")
            flash("Authentication error. Please contact support.", "danger")
    
    return render_template("auth/login.html", form=form, title="Login")

# --- Тестовый маршрут для новой версии логина ---
@auth_bp.route("/login-new", methods=["GET", "POST"])
def login_new(lang):
    g.lang = lang
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.profile', lang=lang))
    
    form = LoginForm()
    if form.validate_on_submit():
        current_app.logger.info(f"Login attempt for email: {form.email.data}")
        current_app.logger.info(f"Form data: {form.data}")
        
        # Проверяем длину пароля
        if len(form.password.data) < 6:
            current_app.logger.warning(f"Password too short for user {form.email.data}")
            flash("Invalid email or password.", "danger")
            return render_template("auth/login_new.html", form=form, title="Login")
        
        user = User.query.filter_by(email=form.email.data).first()
        
        if not user:
            current_app.logger.warning(f"User not found for email: {form.email.data}")
            flash("Invalid email or password.", "danger")
            return render_template("auth/login_new.html", form=form, title="Login")
        
        current_app.logger.info(f"Found user: {user.email}, role: {user.role}")
        current_app.logger.info(f"User password hash: {user.password_hash[:20]}...")
        
        # Проверка валидности хеша
        valid_hash = False
        try:
            if user.password_hash:
                current_app.logger.info(f"Password hash format: {user.password_hash[:10]}...")
                if user.password_hash.startswith('$2b$') or user.password_hash.startswith('$2a$'):
                    valid_hash = True
                    current_app.logger.info("Password hash format is valid")
                else:
                    current_app.logger.warning("Invalid password hash format")
        except Exception as e:
            current_app.logger.error(f"Error checking password hash: {e}")
        
        # Проверяем пароль
        try:
            password_correct = False
            if valid_hash:
                password_correct = bcrypt.check_password_hash(user.password_hash, form.password.data)
                current_app.logger.info(f"Password check result: {password_correct}")
            
            if password_correct:
                login_user(user, remember=form.remember_me.data if hasattr(form, 'remember_me') else False)
                current_app.logger.info(f"User {user.email} logged in successfully")
                flash("Successfully logged in!", "success")
                
                next_page = request.args.get('next')
                if next_page and not next_page.startswith('/'):
                    next_page = None
                
                profile_url_success = url_for("main_bp.profile", lang=lang)
                return redirect(next_page or profile_url_success)
            else:
                current_app.logger.warning(f"Invalid password for user {user.email}")
                flash("Invalid email or password.", "danger")
        except ValueError as e:
            current_app.logger.error(f"Password hash error for user {form.email.data}: {e}")
            flash("Authentication error. Please contact support.", "danger")
    
    return render_template("auth/login_new.html", form=form, title="Login")

# --- Маршрут для выхода пользователей ---
@auth_bp.route("/logout")
@login_required
def logout(lang):
    g.lang = lang
    logout_user()
    flash("Logged out successfully.", "info") # TODO: Локализация
    return redirect(url_for("main_bp.home", lang=lang))

# --- Маршрут для регистрации пользователей ---
@auth_bp.route("/register", methods=["GET", "POST"])
def register(lang):
    g.lang = lang
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.home', lang=lang))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('An account with this email already exists.', 'warning')
            return render_template("auth/register.html", form=form, title="Register")
        
        try:
            # Логируем процесс создания хеша
            current_app.logger.info(f"Creating password hash for user {form.email.data}")
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            current_app.logger.info(f"Generated hash: {hashed_password[:20]}...")
            
            new_user = User(
                email=form.email.data,
                username=form.email.data, 
                password_hash=hashed_password,
                name=form.name.data,
                role='user'  # Явно указываем роль
            )
            
            db.session.add(new_user)
            db.session.commit()
            current_app.logger.info(f"New user registered: {new_user.email} with role {new_user.role}")
            flash('Registration successful! Please log in.', 'success')
            
            return redirect(url_for('auth_bp.login', lang=lang))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error during registration for {form.email.data}: {e}", exc_info=True)
            flash(f'An error occurred during registration. Please try again.', 'danger')
    
    return render_template("auth/register.html", form=form, title="Register")

# --- Тестовый маршрут для новой версии регистрации ---
@auth_bp.route("/register-new", methods=["GET", "POST"])
def register_new(lang):
    g.lang = lang
    if current_user.is_authenticated:
        return redirect(url_for('main_bp.home', lang=lang))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('An account with this email already exists.', 'warning')
            return render_template("auth/register_new.html", form=form, title="Register")
        
        try:
            # Логируем процесс создания хеша
            current_app.logger.info(f"Creating password hash for user {form.email.data}")
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            current_app.logger.info(f"Generated hash: {hashed_password[:20]}...")
            
            new_user = User(
                email=form.email.data,
                username=form.email.data, 
                password_hash=hashed_password,
                name=form.name.data,
                role='user'  # Явно указываем роль
            )
            
            db.session.add(new_user)
            db.session.commit()
            current_app.logger.info(f"New user registered: {new_user.email} with role {new_user.role}")
            flash('Registration successful! Please log in.', 'success')
            
            return redirect(url_for('auth_bp.login_new', lang=lang))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error during registration for {form.email.data}: {e}", exc_info=True)
            flash(f'An error occurred during registration. Please try again.', 'danger')
    
    return render_template("auth/register_new.html", form=form, title="Register")

@auth_bp.route('/debug')
def debug_auth(lang):
    from flask_login import current_user
    debug_info = {
        'session_data': {k: v for k, v in session.items() if k != '_csrf_token'},
        'is_authenticated': current_user.is_authenticated if hasattr(current_user, 'is_authenticated') else False,
        'user_id': current_user.id if hasattr(current_user, 'id') else None,
        'user_email': current_user.email if hasattr(current_user, 'email') else None
    }
    return jsonify(debug_info)

@auth_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password(lang):
    g.lang = lang
    from forms import ChangePasswordForm
    
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        # Проверяем текущий пароль
        if bcrypt.check_password_hash(current_user.password_hash, form.current_password.data):
            # Генерируем новый хеш пароля
            hashed_password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            
            # Обновляем пароль пользователя
            current_user.password_hash = hashed_password
            db.session.commit()
            
            # Отправляем сообщение о успешной смене пароля
            flash('Your password has been updated successfully!', 'success')
            current_app.logger.info(f"Password changed for user {current_user.email}")
            
            # Повторная авторизация с новым паролем
            logout_user()
            flash('Please log in with your new password.', 'info')
            return redirect(url_for('auth_bp.login', lang=lang))
        else:
            flash('Current password is incorrect.', 'danger')
            current_app.logger.warning(f"Failed password change attempt for user {current_user.email}")
    
    return render_template("auth/change_password.html", form=form, title="Change Password")