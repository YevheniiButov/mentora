"""
Profile Routes - Новый профессиональный личный кабинет
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, session, g
from flask_login import login_required, current_user
from models import User
from extensions import db
from datetime import datetime, timezone
import os
from werkzeug.utils import secure_filename
from utils.file_upload import allowed_file, validate_file_size
from translations import t

profile_bp = Blueprint('profile', __name__)

# Настройки загрузки файлов
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'gif', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

@profile_bp.route('/profile')
@login_required
def index():
    """Главная страница профиля"""
    # Получаем язык из URL параметра или сессии
    lang = request.args.get('lang') or session.get('lang', 'nl')
    # Обновляем язык в сессии
    session['lang'] = lang
    
    # Получаем статистику пользователя
    user_stats = {
        'registration_date': current_user.created_at.strftime('%d.%m.%Y') if current_user.created_at else 'Не указано',
        'last_login': current_user.last_login.strftime('%d.%m.%Y %H:%M') if current_user.last_login else 'Никогда',
        'email_confirmed': current_user.email_confirmed,
        'profile_completed': current_user.registration_completed,
        'documents_uploaded': bool(current_user.diploma_file or current_user.language_certificate),
        'profession': current_user.profession,
        'workplace': current_user.workplace,
        'bsn': current_user.bsn  # Используем BSN вместо big_number
    }
    
    return render_template('profile/index.html', 
                         user=current_user, 
                         stats=user_stats,
                         lang=lang)

@profile_bp.route('/profile/personal-info', methods=['GET', 'POST'])
@login_required
def personal_info():
    """Редактирование личной информации"""
    # Получаем язык из URL параметра или сессии
    lang = request.args.get('lang') or session.get('lang', 'nl')
    # Обновляем язык в сессии
    session['lang'] = lang
    
    if request.method == 'POST':
        try:
            # Получаем данные из формы
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            email = request.form.get('email', '').strip().lower()
            phone = request.form.get('phone', '').strip()
            birth_date = request.form.get('birth_date', '').strip()
            nationality = request.form.get('nationality', '').strip()
            
            # Валидация
            errors = []
            if not first_name:
                errors.append('Имя обязательно для заполнения')
            if not last_name:
                errors.append('Фамилия обязательна для заполнения')
            if not email:
                errors.append('Email обязателен для заполнения')
            
            # Проверяем уникальность email
            if email != current_user.email:
                existing_user = User.query.filter_by(email=email).first()
                if existing_user:
                    errors.append('Этот email уже используется другим пользователем')
            
            if errors:
                for error in errors:
                    flash(error, 'error')
                return render_template('profile/personal_info.html', user=current_user, lang=lang)
            
            # Обновляем данные пользователя
            current_user.first_name = first_name
            current_user.last_name = last_name
            current_user.email = email
            current_user.phone = phone if phone else None
            current_user.birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date() if birth_date else None
            current_user.nationality = nationality if nationality else None
            # current_user.updated_at = datetime.now(timezone.utc)  # Поле может отсутствовать
            
            db.session.commit()
            flash(t('personal_info_updated_successfully', lang), 'success')
            return redirect(url_for('profile.personal_info'))
            
        except Exception as e:
            db.session.rollback()
            flash(t('error_updating_info', lang).format(error=str(e)), 'error')
            return render_template('profile/personal_info.html', user=current_user, lang=lang)
    
    return render_template('profile/personal_info.html', user=current_user, lang=lang)

@profile_bp.route('/profile/update-personal-info', methods=['POST'])
@login_required
def update_personal_info():
    """Обновление личной информации"""
    # Получаем язык из URL параметра или сессии
    lang = request.args.get('lang') or session.get('lang', 'nl')
    # Обновляем язык в сессии
    session['lang'] = lang
    
    try:
        # Обновляем данные пользователя
        current_user.first_name = request.form.get('first_name', '').strip()
        current_user.last_name = request.form.get('last_name', '').strip()
        current_user.profession = request.form.get('profession', '').strip()
        current_user.big_number = request.form.get('big_number', '').strip()
        current_user.workplace = request.form.get('workplace', '').strip()
        current_user.language = request.form.get('language', 'nl')
        
        db.session.commit()
        flash(t('personal_info_updated_successfully', lang), 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(t('error_updating_info', lang).format(error=str(e)), 'error')
    
    return redirect(url_for('profile.personal_info', lang=lang))

@profile_bp.route('/profile/documents', methods=['GET', 'POST'])
@login_required
def documents():
    """Управление документами"""
    # Получаем язык из URL параметра или сессии
    lang = request.args.get('lang') or session.get('lang', 'nl')
    # Обновляем язык в сессии
    session['lang'] = lang
    
    if request.method == 'POST':
        try:
            # Обработка загрузки диплома
            if 'diploma' in request.files:
                diploma_file = request.files['diploma']
                if diploma_file and diploma_file.filename:
                    if allowed_file(diploma_file.filename):
                        if validate_file_size(diploma_file):
                            filename = secure_filename(f"diploma_{current_user.id}_{diploma_file.filename}")
                            filepath = os.path.join(UPLOAD_FOLDER, filename)
                            diploma_file.save(filepath)
                            current_user.diploma_file = filepath
                            flash(t('diploma_uploaded_successfully', lang), 'success')
                        else:
                            flash(t('file_too_large', lang), 'error')
                    else:
                        flash(t('invalid_file_type', lang), 'error')
            
            # Обработка загрузки языкового сертификата
            if 'language_certificate' in request.files:
                cert_file = request.files['language_certificate']
                if cert_file and cert_file.filename:
                    if allowed_file(cert_file.filename):
                        if validate_file_size(cert_file):
                            filename = secure_filename(f"language_cert_{current_user.id}_{cert_file.filename}")
                            filepath = os.path.join(UPLOAD_FOLDER, filename)
                            cert_file.save(filepath)
                            current_user.language_certificate = filepath
                            flash(t('language_certificate_uploaded_successfully', lang), 'success')
                        else:
                            flash(t('file_too_large', lang), 'error')
                    else:
                        flash(t('invalid_file_type', lang), 'error')
            
            db.session.commit()
            return redirect(url_for('profile.documents'))
            
        except Exception as e:
            db.session.rollback()
            flash(t('error_uploading_document', lang).format(error=str(e)), 'error')
    
    return render_template('profile/documents.html', user=current_user, lang=lang)

@profile_bp.route('/profile/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Настройки профиля"""
    # Получаем язык из URL параметра или сессии
    lang = request.args.get('lang') or session.get('lang', 'nl')
    # Обновляем язык в сессии
    session['lang'] = lang
    
    if request.method == 'POST':
        try:
            # Получаем данные из формы
            language = request.form.get('language', 'nl')
            theme = request.form.get('theme', 'light')
            
            # Обновляем настройки (только существующие поля)
            current_user.language = language
            current_user.theme = theme
            # current_user.updated_at = datetime.now(timezone.utc)  # Поле может отсутствовать
            
            # Обновляем язык в сессии
            session['lang'] = language
            
            db.session.commit()
            flash(t('settings_saved_successfully', lang), 'success')
            return redirect(url_for('profile.settings'))
            
        except Exception as e:
            db.session.rollback()
            flash(t('error_processing_request', lang).format(error=str(e)), 'error')
    
    return render_template('profile/settings.html', user=current_user, lang=lang)

@profile_bp.route('/profile/security', methods=['GET', 'POST'])
@login_required
def security():
    """Настройки безопасности"""
    # Получаем язык из URL параметра или сессии
    lang = request.args.get('lang') or session.get('lang', 'nl')
    # Обновляем язык в сессии
    session['lang'] = lang
    
    if request.method == 'POST':
        try:
            current_password = request.form.get('current_password', '').strip()
            new_password = request.form.get('new_password', '').strip()
            confirm_password = request.form.get('confirm_password', '').strip()
            
            # Валидация
            errors = []
            if not current_password:
                errors.append('Текущий пароль обязателен')
            if not new_password:
                errors.append('Новый пароль обязателен')
            if len(new_password) < 8:
                errors.append('Новый пароль должен содержать минимум 8 символов')
            if new_password != confirm_password:
                errors.append('Пароли не совпадают')
            
            # Проверяем текущий пароль
            if not current_user.check_password(current_password):
                errors.append('Неверный текущий пароль')
            
            if errors:
                for error in errors:
                    flash(error, 'error')
                return render_template('profile/security.html', user=current_user, lang=lang)
            
            # Обновляем пароль
            current_user.set_password(new_password)
            # current_user.updated_at = datetime.now(timezone.utc)  # Поле может отсутствовать
            
            db.session.commit()
            flash(t('password_changed_successfully', lang), 'success')
            return redirect(url_for('profile.security'))
            
        except Exception as e:
            db.session.rollback()
            flash(t('error_processing_request', lang).format(error=str(e)), 'error')
    
    return render_template('profile/security.html', user=current_user, lang=lang)

@profile_bp.route('/profile/statistics')
@login_required
def statistics():
    """Статистика пользователя (заглушка)"""
    # Получаем язык из URL параметра или сессии
    lang = request.args.get('lang') or session.get('lang', 'nl')
    # Обновляем язык в сессии
    session['lang'] = lang
    
    # Заглушка для статистики
    stats = {
        'total_study_time': '0 часов',
        'completed_modules': 0,
        'average_score': 0,
        'current_streak': 0,
        'total_achievements': 0
    }
    
    return render_template('profile/statistics.html', 
                         user=current_user, 
                         stats=stats,
                         lang=lang)

@profile_bp.route('/profile/delete-document', methods=['POST'])
@login_required
def delete_document():
    """Удаление документа"""
    try:
        document_type = request.form.get('document_type')
        
        if document_type == 'diploma' and current_user.diploma_file:
            # Удаляем файл с диска
            if os.path.exists(current_user.diploma_file):
                os.remove(current_user.diploma_file)
            current_user.diploma_file = None
            flash(t('diploma_deleted', lang), 'success')
        elif document_type == 'language_certificate' and current_user.language_certificate:
            # Удаляем файл с диска
            if os.path.exists(current_user.language_certificate):
                os.remove(current_user.language_certificate)
            current_user.language_certificate = None
            flash(t('language_certificate_deleted', lang), 'success')
        else:
            flash(t('document_not_found', lang), 'error')
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        flash(t('error_deleting_document', lang).format(error=str(e)), 'error')
    
    return redirect(url_for('profile.documents'))
