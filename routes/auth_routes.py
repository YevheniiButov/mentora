from flask import (
    Blueprint, render_template, request, redirect, url_for, flash, session, g, current_app,
    jsonify
)
from flask_login import (
    login_user, logout_user, login_required, current_user
)
from extensions import db, bcrypt
from models import User
from forms import LoginForm, RegistrationForm # Предполагаем, что формы в корневом forms.py

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
    g.lang = lang # Устанавливаем g.lang
    if current_user.is_authenticated:
        # Используем main_bp.profile, предполагая его существование
        return redirect(url_for('main_bp.profile', lang=lang))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        # Исправление 2: Добавляем проверку валидности хеша
        valid_hash = False
        if user:
            try:
                # Проверяем формат хеша (должен начинаться с $2b$ или $2a$)
                if user.password_hash and (user.password_hash.startswith('$2b$') or 
                                         user.password_hash.startswith('$2a$')):
                    valid_hash = True
            except Exception as e:
                current_app.logger.error(f"Error checking password hash: {e}")
        
        # Проверяем пароль только если хеш имеет правильный формат
        try:
            password_correct = False
            if user and valid_hash:
                password_correct = bcrypt.check_password_hash(user.password_hash, form.password.data)
            
            if user and password_correct:
                login_user(user, remember=form.remember_me.data if hasattr(form, 'remember_me') else False)
                flash("Successfully logged in!", "success") # TODO: Локализация
                current_app.logger.info(f"User {user.email} logged in successfully.")
                
                # Пытаемся редиректнуть на 'next' или на профиль
                next_page = request.args.get('next')
                # Проверка безопасности редиректа (базовая)
                if next_page and not next_page.startswith('/'):
                    next_page = None # Сброс, если URL внешний или подозрительный
                
                profile_url_success = url_for("main_bp.profile", lang=lang)
                return redirect(next_page or profile_url_success)
            else:
                flash("Invalid email or password.", "danger") # TODO: Локализация
                current_app.logger.warning(f"Failed login attempt for email {form.email.data}")
        except ValueError as e:
            # Добавляем обработку ошибки хеша
            current_app.logger.error(f"Password hash error for user {form.email.data}: {e}")
            flash("Authentication error. Please contact support.", "danger")
    
    # Обновлен путь к шаблону
    return render_template("auth/login.html", form=form, title="Login")

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
            flash('An account with this email already exists.', 'warning') # TODO: Локализация
            return render_template("auth/register.html", form=form, title="Register")
        
        # Исправление 3: Убедимся, что хеш правильно создается
        try:
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            
            new_user = User(
                email=form.email.data,
                username=form.email.data, 
                password_hash=hashed_password,
                name=form.name.data
                # Остальные поля User (avatar, role и т.д.) получат значения по умолчанию
            )
            
            db.session.add(new_user)
            db.session.commit()
            current_app.logger.info(f"New user registered: {new_user.email}")
            flash('Registration successful! Please log in.', 'success') # TODO: Локализация
            
            # Используем абсолютный путь вместо относительного для согласованности
            return redirect(url_for('auth_bp.login', lang=lang))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error during registration for {form.email.data}: {e}", exc_info=True)
            flash(f'An error occurred during registration. Please try again.', 'danger') # TODO: Локализация
    
    # Обновлен путь к шаблону
    return render_template("auth/register.html", form=form, title="Register")

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