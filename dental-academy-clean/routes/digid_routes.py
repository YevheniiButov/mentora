from flask import Blueprint, request, session, redirect, url_for, render_template, flash, jsonify, g
from flask_login import login_user, logout_user, current_user, login_required
from functools import wraps
from datetime import datetime, timezone, timedelta
import uuid
import logging
import os
from werkzeug.utils import secure_filename

from extensions import db
from models import User, DigiDSession, create_digid_user
from translations import get_translation as t

# Импорт для отключения CSRF
from flask_wtf import CSRFProtect

# Логгер
logger = logging.getLogger(__name__)

# Blueprint

digid_bp = Blueprint('digid', __name__, url_prefix='/digid')

# Константы для загрузки файлов
UPLOAD_FOLDER = 'static/uploads/documents'
ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# Создаём папку для загрузок если её нет
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_size(file_stream):
    """Проверяем размер файла"""
    file_stream.seek(0, os.SEEK_END)
    file_size = file_stream.tell()
    file_stream.seek(0)
    return file_size <= MAX_FILE_SIZE

# Мок-данные пользователей DigiD (только для теста)
MOCK_DIGID_USERS = {
    'demo.tandarts': {
        'digid_username': 'demo.tandarts',
        'bsn': '123456789',
        'email': 'jan.vandenberg@mentora.nl',
        'first_name': 'Jan',
        'last_name': 'van der Berg',
        'role': 'user',
        'profession': 'tandarts'
    },
    'demo.apotheker': {
        'digid_username': 'demo.apotheker',
        'bsn': '234567890',
        'email': 'maria.jansen@mentora.nl',
        'first_name': 'Maria',
        'last_name': 'Jansen',
        'role': 'user',
        'profession': 'apotheker'
    },
    'demo.arts': {
        'digid_username': 'demo.arts',
        'bsn': '456789012',
        'email': 'peter.smits@mentora.nl',
        'first_name': 'Peter',
        'last_name': 'Smits',
        'role': 'user',
        'profession': 'huisarts'
    },
    'demo.verpleegkundige': {
        'digid_username': 'demo.verpleegkundige',
        'bsn': '345678901',
        'email': 'anneke.devries@mentora.nl',
        'first_name': 'Anneke',
        'last_name': 'de Vries',
        'role': 'user',
        'profession': 'verpleegkundige'
    },
    'demo.admin': {
        'digid_username': 'demo.admin',
        'bsn': '999999999',
        'email': 'admin@mentora.nl',
        'first_name': 'Admin',
        'last_name': 'Beheerder',
        'role': 'admin',
        'profession': 'admin'
    }
}

# Декоратор для защищённых DigiD-страниц

def digid_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_digid_user():
            lang = session.get('lang', 'nl')
            flash(t('digid_auth_required', lang), 'warning')
            return redirect('/digid/login')
        return f(*args, **kwargs)
    return decorated_function

# Вспомогательная функция: создать/обновить пользователя из DigiD-данных

def get_or_create_digid_user(digid_data):
    user = User.query.filter_by(digid_username=digid_data['digid_username']).first()
    if user:
        # Обновить данные
        user.bsn = digid_data['bsn']
        user.email = digid_data['email']
        user.first_name = digid_data.get('first_name')
        user.last_name = digid_data.get('last_name')
        user.digid_verified = True
        user.created_via_digid = True
        user.role = digid_data.get('role', 'user')
        db.session.commit()
    else:
        user = create_digid_user(
            digid_username=digid_data['digid_username'],
            bsn=digid_data['bsn'],
            email=digid_data['email'],
            first_name=digid_data.get('first_name'),
            last_name=digid_data.get('last_name')
        )
        if user:
            user.role = digid_data.get('role', 'user')
            db.session.commit()
    return user

# DigiD: страница входа (выбор тестового пользователя)
@digid_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        digid_username = request.form.get('digid_username')
        if digid_username not in MOCK_DIGID_USERS:
            flash('Пользователь не найден (мок DigiD)', 'danger')
            return render_template('digid/mock_login.html', users=MOCK_DIGID_USERS)
        # Сохраняем выбранного пользователя в сессии
        session['digid_username'] = digid_username
        return redirect('/digid/authenticate')
    return render_template('digid/mock_login.html', users=MOCK_DIGID_USERS)

# DigiD: имитация редиректа на DigiD и возврат (мок)
@digid_bp.route('/authenticate', methods=['GET', 'POST'])
def authenticate():
    if request.method == 'POST':
        # Обработка данных с пин-кодом
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Geen data ontvangen'}), 400
            
        digid_username = data.get('digid_username')
        pincode = data.get('pincode') or data.get('koppelcode')  # Поддерживаем оба варианта
        
        if not digid_username or not pincode:
            return jsonify({'success': False, 'message': 'Gebruikersnaam en pincode zijn verplicht'}), 400
            
        if digid_username not in MOCK_DIGID_USERS:
            return jsonify({'success': False, 'message': 'Gebruiker niet gevonden'}), 404
            
        # Сохраняем выбранного пользователя в сессии
        session['digid_username'] = digid_username
        
        # Имитация успешной аутентификации
        digid_data = MOCK_DIGID_USERS[digid_username]
        
        try:
            user = get_or_create_digid_user(digid_data)
            if not user:
                logger.error(f"Failed to create DigiD user for {digid_username}")
                return jsonify({'success': False, 'message': 'Fout bij het aanmaken van gebruiker'}), 500
        except Exception as e:
            logger.error(f"Error creating DigiD user: {e}")
            return jsonify({'success': False, 'message': 'Database fout bij gebruiker aanmaken'}), 500
            
        try:
            # Создаём DigiD-сессию
            session_id = str(uuid.uuid4())
            expires_at = datetime.now(timezone.utc) + timedelta(hours=8)
            digid_session = DigiDSession(
                user_id=user.id,
                session_id=session_id,
                bsn=user.bsn,
                digid_username=user.digid_username,
                expires_at=expires_at
            )
            db.session.add(digid_session)
            db.session.commit()
            
            # Сохраняем токен и id сессии в session
            session['digid_session_id'] = digid_session.session_id
            session['digid_user_id'] = user.id
            login_user(user, remember=True)
            
            # Определяем куда перенаправить пользователя
            if user.is_admin:
                redirect_url = '/admin'
            else:
                # Проверяем, завершена ли регистрация
                if not user.registration_completed:
                    redirect_url = '/digid/complete-registration'
                else:
                    # Уже зарегистрирован → профессиональная карта обучения
                    redirect_url = get_learning_map_url_by_profession(user.profession)
            
            return jsonify({
                'success': True, 
                'message': f'Welkom, {user.get_display_name()}!',
                'redirect_url': redirect_url,
                'user_info': {
                    'id': user.id,
                    'name': user.get_display_name(),
                    'role': user.role,
                    'registration_completed': user.registration_completed
                }
            })
        
        except Exception as e:
            logger.error(f"Error creating DigiD session: {e}")
            db.session.rollback()
            return jsonify({'success': False, 'message': 'Fout bij sessie aanmaken'}), 500
    
    # GET запрос - перенаправляем на новый способ аутентификации
    return redirect('/digid/login')

# DigiD: callback после успешной аутентификации (мок)
@digid_bp.route('/callback')
def callback():
    digid_username = session.get('digid_username')
    if not digid_username:
        logger.error("DigiD callback: no digid_username in session")
        flash('Ошибка DigiD: пользователь не выбран', 'danger')
        return redirect('/digid/login')
        
    if digid_username not in MOCK_DIGID_USERS:
        logger.error(f"DigiD callback: invalid digid_username {digid_username}")
        flash('Ошибка DigiD: пользователь не найден', 'danger')
        return redirect('/digid/login')
        
    digid_data = MOCK_DIGID_USERS[digid_username]
    
    try:
        user = get_or_create_digid_user(digid_data)
        if not user:
            logger.error(f"DigiD callback: failed to create/get user for {digid_username}")
            flash('Ошибка создания пользователя DigiD', 'danger')
            return redirect('/digid/login')
            
        # Проверяем существующую сессию
        existing_session = DigiDSession.query.filter_by(
            user_id=user.id,
            is_active=True
        ).first()
        
        if existing_session and not existing_session.is_expired():
            # Используем существующую сессию
            session['digid_session_id'] = existing_session.session_id
            session['digid_user_id'] = user.id
            existing_session.refresh()
            db.session.commit()
        else:
            # Создаём новую DigiD-сессию
            session_id = str(uuid.uuid4())
            expires_at = datetime.now(timezone.utc) + timedelta(hours=8)
            digid_session = DigiDSession(
                user_id=user.id,
                session_id=session_id,
                bsn=user.bsn,
                digid_username=user.digid_username,
                expires_at=expires_at
            )
            db.session.add(digid_session)
            
            # Деактивируем старую сессию если есть
            if existing_session:
                existing_session.deactivate()
                
            db.session.commit()
            
            # Сохраняем токен и id сессии в session
            session['digid_session_id'] = digid_session.session_id
            session['digid_user_id'] = user.id
            
        login_user(user, remember=True)
        flash(f'Добро пожаловать, {user.get_display_name()}! (DigiD)', 'success')
        
        # Определяем куда перенаправить пользователя
        if user.is_admin:
            return redirect('/admin')
        else:
            # Проверяем, завершена ли регистрация
            if not user.registration_completed:
                return redirect('/digid/complete-registration')
            else:
                # Уже зарегистрирован → профессиональная карта обучения
                return redirect(get_learning_map_url_by_profession(user.profession))
                
    except Exception as e:
        logger.error(f"Error in DigiD callback: {e}")
        db.session.rollback()
        flash('Произошла ошибка при обработке DigiD аутентификации', 'danger')
        return redirect('/digid/login')

# DigiD: статус текущей DigiD-сессии
@digid_bp.route('/status')
@login_required
def status():
    digid_session_id = session.get('digid_session_id')
    digid_user_id = session.get('digid_user_id')
    digid_session = None
    if digid_session_id and digid_user_id:
        digid_session = DigiDSession.query.filter_by(session_id=digid_session_id, user_id=digid_user_id).first()
    return render_template('digid/status.html', digid_session=digid_session, user=current_user)

# DigiD: выход
@digid_bp.route('/logout')
@login_required
def logout():
    digid_session_id = session.pop('digid_session_id', None)
    digid_user_id = session.pop('digid_user_id', None)
    if digid_session_id and digid_user_id:
        digid_session = DigiDSession.query.filter_by(session_id=digid_session_id, user_id=digid_user_id).first()
        if digid_session:
            digid_session.deactivate()
            db.session.commit()
    logout_user()
    session.pop('digid_username', None)
    
    # Получаем язык из сессии или используем дефолтный
    lang = session.get('lang', 'nl')
    flash(t('logged_out_digid', lang), 'info')
    return redirect('/digid/login')

# Пример защищённого роутера
@digid_bp.route('/protected')
@digid_required
def protected():
    return f'Это защищённая страница DigiD. Пользователь: {current_user.get_display_name()}'

# API: получить статус сессии (JSON)
@digid_bp.route('/api/session_status')
@login_required
def api_session_status():
    digid_session_id = session.get('digid_session_id')
    digid_user_id = session.get('digid_user_id')
    digid_session = None
    if digid_session_id and digid_user_id:
        digid_session = DigiDSession.query.filter_by(session_id=digid_session_id, user_id=digid_user_id).first()
    if not digid_session:
        return jsonify({'active': False, 'error': 'No active DigiD session'}), 401
    return jsonify({
        'active': digid_session.is_active and not digid_session.is_expired(),
        'expires_at': digid_session.expires_at.isoformat(),
        'user': {
            'id': current_user.id,
            'name': current_user.get_display_name(),
            'role': current_user.role,
            'digid_username': current_user.digid_username,
            'bsn': current_user.bsn,
        }
    })

# Тестовый роут для быстрой аутентификации (только для development)
@digid_bp.route('/test-auth/<username>')
def test_auth(username):
    """Быстрая аутентификация для тестирования (только в dev режиме)"""
    from flask import current_app
    
    if not current_app.config.get('DIGID_MOCK_MODE', False):
        return jsonify({'error': 'Test auth only available in mock mode'}), 403
    
    if username not in MOCK_DIGID_USERS:
        return jsonify({'error': f'User {username} not found'}), 404
    
    try:
        digid_data = MOCK_DIGID_USERS[username]
        user = get_or_create_digid_user(digid_data)
        
        if not user:
            return jsonify({'error': 'Failed to create user'}), 500
        
        # Создаём DigiD-сессию
        session_id = str(uuid.uuid4())
        expires_at = datetime.now(timezone.utc) + timedelta(hours=8)
        digid_session = DigiDSession(
            user_id=user.id,
            session_id=session_id,
            bsn=user.bsn,
            digid_username=user.digid_username,
            expires_at=expires_at
        )
        db.session.add(digid_session)
        db.session.commit()
        
        # Сохраняем токен и id сессии в session
        session['digid_session_id'] = digid_session.session_id
        session['digid_user_id'] = user.id
        session['digid_username'] = username
        login_user(user, remember=True)
        
        # Получаем язык из сессии или используем дефолтный
        lang = session.get('lang', 'nl')
        flash(f'{t("test_login_successful", lang)}: {user.get_display_name()}', 'success')
        
        # Определяем куда перенаправить пользователя
        if user.is_admin:
            return redirect('/admin')
        else:
            # Проверяем, завершена ли регистрация
            if not user.registration_completed:
                return redirect('/digid/complete-registration')
            else:
                # Уже зарегистрирован → dashboard (карта обучения)
                return redirect('/ru/learning-map/')
        
    except Exception as e:
        logger.error(f"Error in test auth: {e}")
        return jsonify({'error': str(e)}), 500

# Демонстрационная страница DigiD интеграции
@digid_bp.route('/demo')
def demo():
    """Демонстрационная страница для показа DigiD функциональности"""
    from flask import current_app
    
    # Статистика DigiD
    total_users = User.query.filter_by(created_via_digid=True).count()
    active_sessions = DigiDSession.query.filter_by(is_active=True).count()
    
    demo_stats = {
        'digid_enabled': current_app.config.get('DIGID_ENABLED', False),
        'mock_mode': current_app.config.get('DIGID_MOCK_MODE', False),
        'session_timeout': current_app.config.get('DIGID_SESSION_TIMEOUT', 28800),
        'total_digid_users': total_users,
        'active_sessions': active_sessions,
        'mock_users': MOCK_DIGID_USERS
    }
    
    return render_template('digid/demo.html', 
                         stats=demo_stats, 
                         current_user=current_user,
                         is_authenticated=current_user.is_authenticated)

# DigiD: Обязательная форма регистрации
@digid_bp.route('/complete-registration', methods=['GET', 'POST'])
@login_required
def complete_registration():
    # Проверяем, что пользователь авторизован через DigiD
    if not current_user.is_digid_user():
        flash('Доступ только для DigiD пользователей', 'danger')
        return redirect('/digid/login')
    
    # Если регистрация уже завершена, перенаправляем на карту обучения
    if current_user.registration_completed:
        return redirect('/ru/learning-map/')
    
    if request.method == 'POST':
        # Получаем данные из формы
        profession = request.form.get('profession')
        
        # Валидация профессии
        valid_professions = ['tandarts', 'apotheker', 'huisarts', 'verpleegkundige']
        if not profession or profession not in valid_professions:
            flash('Выберите профессию', 'danger')
            return render_template('digid/registration_form.html', user=current_user)
        
        # Обработка файла диплома (обязательный)
        diploma_file = request.files.get('diploma_file')
        if not diploma_file or diploma_file.filename == '':
            flash('Загрузите диплом', 'danger')
            return render_template('digid/registration_form.html', user=current_user)
        
        if not allowed_file(diploma_file.filename):
            flash('Диплом должен быть в формате PDF', 'danger')
            return render_template('digid/registration_form.html', user=current_user)
        
        if not validate_file_size(diploma_file):
            flash('Размер файла диплома не должен превышать 5MB', 'danger')
            return render_template('digid/registration_form.html', user=current_user)
        
        # Сохраняем диплом
        diploma_filename = secure_filename(f"diploma_{current_user.bsn}_{diploma_file.filename}")
        diploma_path = os.path.join(UPLOAD_FOLDER, diploma_filename)
        diploma_file.save(diploma_path)
        
        # Обработка сертификата языка (необязательный)
        language_cert_path = None
        language_cert_file = request.files.get('language_certificate')
        if language_cert_file and language_cert_file.filename != '':
            if not allowed_file(language_cert_file.filename):
                flash('Сертификат языка должен быть в формате PDF', 'danger')
                return render_template('digid/registration_form.html', user=current_user)
            
            if not validate_file_size(language_cert_file):
                flash('Размер файла сертификата не должен превышать 5MB', 'danger')
                return render_template('digid/registration_form.html', user=current_user)
            
            language_cert_filename = secure_filename(f"language_cert_{current_user.bsn}_{language_cert_file.filename}")
            language_cert_path = os.path.join(UPLOAD_FOLDER, language_cert_filename)
            language_cert_file.save(language_cert_path)
        
        # Обновляем данные пользователя
        try:
            current_user.profession = profession
            current_user.diploma_file = diploma_path
            current_user.language_certificate = language_cert_path
            current_user.registration_completed = True
            db.session.commit()
            
            flash('Регистрация завершена успешно!', 'success')
            
            # Перенаправляем на карту обучения соответствующей профессии
            return redirect(get_learning_map_url_by_profession(profession))
            
        except Exception as e:
            logger.error(f"Error completing registration: {e}")
            db.session.rollback()
            flash('Ошибка при завершении регистрации', 'danger')
            return render_template('digid/registration_form.html', user=current_user)
    
    # GET запрос - показываем форму
    return render_template('digid/registration_form.html', user=current_user)

def get_learning_map_url_by_profession(profession):
    """Возвращает URL карты обучения в зависимости от профессии"""
    from flask import g
    
    # Получаем текущий язык из g или сессии, или используем дефолтный
    current_lang = getattr(g, 'lang', session.get('lang', 'ru'))
    
    profession_routes = {
        'tandarts': f'/{current_lang}/leerkaart/tandheelkunde',
        'apotheker': f'/{current_lang}/leerkaart/farmacie',
        'huisarts': f'/{current_lang}/leerkaart/huisartsgeneeskunde',
        'verpleegkundige': f'/{current_lang}/leerkaart/verpleegkunde'
    }
    return profession_routes.get(profession, f'/{current_lang}/leerkaart/')

@digid_bp.route('/test-users')
def test_users():
    """Тестовая страница для просмотра пользователей и их статуса регистрации"""
    digid_users = User.query.filter_by(created_via_digid=True).all()
    return render_template('digid/test_users.html', users=digid_users) 