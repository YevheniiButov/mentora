# routes/auth_routes.py - Authentication routes

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
try:
    from werkzeug.urls import url_parse
except ImportError:
    from urllib.parse import urlparse as url_parse
from werkzeug.utils import secure_filename
from models import User, ProfileAuditLog
from extensions import db
import os
import json
from datetime import datetime, timezone

auth_bp = Blueprint('auth', __name__)

# Constants for file uploads
UPLOAD_FOLDER = 'static/uploads'
PROFILE_PHOTO_FOLDER = 'static/uploads/profile_photos'
DOCUMENTS_FOLDER = 'static/uploads/documents'
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png'}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_DOCUMENT_SIZE = 10 * 1024 * 1024  # 10MB

# Create upload directories
for folder in [UPLOAD_FOLDER, PROFILE_PHOTO_FOLDER, DOCUMENTS_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

def allowed_file(filename, allowed_extensions):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_file_size(file):
    """Get file size"""
    file.seek(0, 2)  # Seek to end
    size = file.tell()
    file.seek(0)  # Reset to beginning
    return size

# Удаляю старые маршруты:
# @auth_bp.route('/login', methods=['GET', 'POST'])
# @auth_bp.route('/register', methods=['GET', 'POST'])
# @auth_bp.route('/logout')
# @auth_bp.route('/forgot-password')
# @auth_bp.route('/reset-password')

# Оставляю только DigiD:
@auth_bp.route('/digid/login')
def digid_login():
    from flask import render_template, request, g
    # Используем g.lang, который устанавливается в before_request
    lang = g.get('lang', 'nl')
    return render_template('digid/login.html', lang=lang)

@auth_bp.route('/digid/callback')
def digid_callback():
    # DigiD callback logic
    pass

@auth_bp.route('/digid/logout')
def digid_logout():
    from flask_login import logout_user
    logout_user()
    # Можно добавить очистку сессии, если нужно: session.clear()
    return redirect(url_for('main.index'))

@auth_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    user_stats = current_user.get_progress_stats()
    return render_template('auth/profile.html', user_stats=user_stats)

@auth_bp.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    """Enhanced edit user profile with multiple sections"""
    if request.method == 'POST':
        try:
            section = request.form.get('section', 'personal')
            
            if section == 'personal':
                return handle_personal_data_update()
            elif section == 'professional':
                return handle_professional_data_update()
            elif section == 'documents':
                return handle_documents_update()
            elif section == 'settings':
                return handle_settings_update()
            else:
                flash('Invalid section specified.', 'error')
                
        except Exception as e:
            db.session.rollback()
            flash(f'Failed to update profile: {str(e)}', 'error')
    
    # Get current user data for form
    user_data = {
        'notification_settings': current_user.get_notification_settings(),
        'privacy_settings': current_user.get_privacy_settings(),
        'additional_documents': current_user.get_additional_documents(),
        'language_certificates': current_user.get_language_certificates()
    }
    
    return render_template('auth/edit_profile.html', user_data=user_data)

def handle_personal_data_update():
    """Handle personal data section updates"""
    # Extract form data
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()
    email = request.form.get('email', '').strip()
    phone = request.form.get('phone', '').strip()
    
    # Validation
    errors = []
    
    if email and email != current_user.email:
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            errors.append('Email already in use by another account.')
    
    if errors:
        for error in errors:
            flash(error, 'error')
        return redirect(url_for('auth.edit_profile'))
    
    # Track changes for audit log
    changes = []
    if first_name != current_user.first_name:
        changes.append(('first_name', current_user.first_name, first_name))
    if last_name != current_user.last_name:
        changes.append(('last_name', current_user.last_name, last_name))
    if email != current_user.email:
        changes.append(('email', current_user.email, email))
    if phone != current_user.phone:
        changes.append(('phone', current_user.phone, phone))
    
    # Handle profile photo upload
    if 'profile_photo' in request.files:
        file = request.files['profile_photo']
        if file and file.filename and allowed_file(file.filename, ALLOWED_IMAGE_EXTENSIONS):
            if get_file_size(file) <= MAX_IMAGE_SIZE:
                filename = secure_filename(f"user_{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
                file_path = os.path.join(PROFILE_PHOTO_FOLDER, filename)
                file.save(file_path)
                
                # Remove old photo
                if current_user.profile_photo and os.path.exists(current_user.profile_photo):
                    try:
                        os.remove(current_user.profile_photo)
                    except:
                        pass
                
                changes.append(('profile_photo', current_user.profile_photo, file_path))
                current_user.profile_photo = file_path
            else:
                flash('Profile photo is too large. Maximum size is 5MB.', 'error')
                return redirect(url_for('auth.edit_profile'))
        elif file and file.filename:
            flash('Invalid file type for profile photo. Allowed: PNG, JPG, JPEG, GIF, WEBP.', 'error')
            return redirect(url_for('auth.edit_profile'))
    
    # Update user data
    current_user.first_name = first_name or None
    current_user.last_name = last_name or None
    current_user.email = email
    current_user.phone = phone or None
    current_user.profile_updated_at = datetime.now(timezone.utc)
    
    # Log changes
    for field, old_val, new_val in changes:
        current_user.log_profile_change(field, old_val, new_val)
    
    db.session.commit()
    flash('Personal information updated successfully!', 'success')
    return redirect(url_for('auth.profile'))

def handle_professional_data_update():
    """Handle professional data section updates"""
    big_number = request.form.get('big_number', '').strip()
    workplace = request.form.get('workplace', '').strip()
    specialization = request.form.get('specialization', '').strip()
    
    # Track changes
    changes = []
    if big_number != current_user.big_number:
        changes.append(('big_number', current_user.big_number, big_number))
    if workplace != current_user.workplace:
        changes.append(('workplace', current_user.workplace, workplace))
    if specialization != current_user.specialization:
        changes.append(('specialization', current_user.specialization, specialization))
    
    # Update data
    current_user.big_number = big_number or None
    current_user.workplace = workplace or None
    current_user.specialization = specialization or None
    current_user.profile_updated_at = datetime.now(timezone.utc)
    
    # Log changes
    for field, old_val, new_val in changes:
        current_user.log_profile_change(field, old_val, new_val)
    
    db.session.commit()
    flash('Professional information updated successfully!', 'success')
    return redirect(url_for('auth.profile'))

def handle_documents_update():
    """Handle documents section updates"""
    # Handle diploma re-upload
    if 'diploma_file' in request.files:
        file = request.files['diploma_file']
        if file and file.filename and allowed_file(file.filename, ALLOWED_DOCUMENT_EXTENSIONS):
            if get_file_size(file) <= MAX_DOCUMENT_SIZE:
                filename = secure_filename(f"diploma_{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
                file_path = os.path.join(DOCUMENTS_FOLDER, filename)
                file.save(file_path)
                
                # Remove old diploma
                if current_user.diploma_file and os.path.exists(current_user.diploma_file):
                    try:
                        os.remove(current_user.diploma_file)
                    except:
                        pass
                
                current_user.log_profile_change('diploma_file', current_user.diploma_file, file_path)
                current_user.diploma_file = file_path
                flash('Diploma uploaded successfully!', 'success')
            else:
                flash('Diploma file is too large. Maximum size is 10MB.', 'error')
                return redirect(url_for('auth.edit_profile'))
        elif file and file.filename:
            flash('Invalid file type for diploma. Allowed: PDF, DOC, DOCX, JPG, PNG.', 'error')
            return redirect(url_for('auth.edit_profile'))
    
    # Handle additional document upload
    if 'additional_document' in request.files:
        file = request.files['additional_document']
        doc_type = request.form.get('document_type', '').strip()
        doc_name = request.form.get('document_name', '').strip()
        
        if file and file.filename and doc_type and doc_name:
            if allowed_file(file.filename, ALLOWED_DOCUMENT_EXTENSIONS):
                if get_file_size(file) <= MAX_DOCUMENT_SIZE:
                    filename = secure_filename(f"doc_{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
                    file_path = os.path.join(DOCUMENTS_FOLDER, filename)
                    file.save(file_path)
                    
                    current_user.add_additional_document(file_path, doc_type, doc_name)
                    current_user.log_profile_change('additional_documents', 'document_added', f"{doc_type}: {doc_name}")
                    flash(f'Document "{doc_name}" uploaded successfully!', 'success')
                else:
                    flash('Document is too large. Maximum size is 10MB.', 'error')
                    return redirect(url_for('auth.edit_profile'))
            else:
                flash('Invalid file type. Allowed: PDF, DOC, DOCX, JPG, PNG.', 'error')
                return redirect(url_for('auth.edit_profile'))
    
    # Handle language certificate upload
    if 'language_certificate' in request.files:
        file = request.files['language_certificate']
        cert_type = request.form.get('certificate_type', '').strip()
        cert_level = request.form.get('certificate_level', '').strip()
        
        if file and file.filename and cert_type and cert_level:
            if allowed_file(file.filename, ALLOWED_DOCUMENT_EXTENSIONS):
                if get_file_size(file) <= MAX_DOCUMENT_SIZE:
                    filename = secure_filename(f"lang_{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
                    file_path = os.path.join(DOCUMENTS_FOLDER, filename)
                    file.save(file_path)
                    
                    current_user.add_language_certificate(file_path, cert_type, cert_level)
                    current_user.log_profile_change('language_certificates', 'certificate_added', f"{cert_type}: {cert_level}")
                    flash(f'Language certificate "{cert_type} - {cert_level}" uploaded successfully!', 'success')
                else:
                    flash('Certificate is too large. Maximum size is 10MB.', 'error')
                    return redirect(url_for('auth.edit_profile'))
            else:
                flash('Invalid file type. Allowed: PDF, DOC, DOCX, JPG, PNG.', 'error')
                return redirect(url_for('auth.edit_profile'))
    
    current_user.profile_updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return redirect(url_for('auth.edit_profile'))

def handle_settings_update():
    """Handle settings section updates"""
    language = request.form.get('language', 'en')
    theme = request.form.get('theme', 'light')
    
    # Notification settings
    notification_settings = {
        'email_notifications': bool(request.form.get('email_notifications')),
        'sms_notifications': bool(request.form.get('sms_notifications')),
        'push_notifications': bool(request.form.get('push_notifications')),
        'learning_reminders': bool(request.form.get('learning_reminders')),
        'exam_notifications': bool(request.form.get('exam_notifications')),
        'community_updates': bool(request.form.get('community_updates')),
        'marketing_emails': bool(request.form.get('marketing_emails'))
    }
    
    # Privacy settings
    privacy_settings = {
        'profile_visibility': request.form.get('profile_visibility', 'registered_users'),
        'show_progress': bool(request.form.get('show_progress')),
        'show_achievements': bool(request.form.get('show_achievements')),
        'allow_messages': bool(request.form.get('allow_messages')),
        'show_last_seen': bool(request.form.get('show_last_seen')),
        'data_sharing': bool(request.form.get('data_sharing')),
        'analytics_tracking': bool(request.form.get('analytics_tracking'))
    }
    
    # Validation
    if language not in ['en', 'ru', 'nl', 'uk', 'es', 'pt', 'tr', 'fa', 'ar']:
        language = 'en'
    
    if theme not in ['light', 'dark']:
        theme = 'light'
    
    # Track changes
    changes = []
    if language != current_user.language:
        changes.append(('language', current_user.language, language))
    if theme != current_user.theme:
        changes.append(('theme', current_user.theme, theme))
    
    # Update settings
    current_user.language = language
    current_user.theme = theme
    current_user.set_notification_settings(notification_settings)
    current_user.set_privacy_settings(privacy_settings)
    current_user.profile_updated_at = datetime.now(timezone.utc)
    
    # Log changes
    for field, old_val, new_val in changes:
        current_user.log_profile_change(field, old_val, new_val)
    
    current_user.log_profile_change('notification_settings', 'settings_updated', json.dumps(notification_settings))
    current_user.log_profile_change('privacy_settings', 'settings_updated', json.dumps(privacy_settings))
    
    # Update session language
    session['language'] = language
    
    db.session.commit()
    flash('Settings updated successfully!', 'success')
    return redirect(url_for('auth.profile'))

@auth_bp.route('/profile/delete-document', methods=['POST'])
@login_required
def delete_document():
    """Delete a document from user profile"""
    try:
        document_type = request.json.get('type')
        document_path = request.json.get('path')
        
        if document_type == 'additional':
            docs = current_user.get_additional_documents()
            docs = [doc for doc in docs if doc['path'] != document_path]
            current_user.additional_documents = json.dumps(docs)
        elif document_type == 'language':
            certs = current_user.get_language_certificates()
            certs = [cert for cert in certs if cert['path'] != document_path]
            current_user.language_certificates = json.dumps(certs)
        else:
            return jsonify({'success': False, 'message': 'Invalid document type'})
        
        # Remove file from filesystem
        if os.path.exists(document_path):
            try:
                os.remove(document_path)
            except:
                pass
        
        current_user.log_profile_change(f'{document_type}_documents', 'document_deleted', document_path)
        current_user.profile_updated_at = datetime.now(timezone.utc)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Document deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)})

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Change user password"""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        errors = []
        
        if not current_user.check_password(current_password):
            errors.append('Current password is incorrect.')
        
        if len(new_password) < 6:
            errors.append('New password must be at least 6 characters long.')
        
        if new_password != confirm_password:
            errors.append('New passwords do not match.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/change_password.html')
        
        # Update password
        try:
            current_user.set_password(new_password)
            current_user.log_profile_change('password', 'password_changed', 'password_changed')
            db.session.commit()
            
            flash('Password changed successfully!', 'success')
            return redirect(url_for('auth.profile'))
            
        except Exception as e:
            db.session.rollback()
            flash('Failed to change password. Please try again.', 'error')
    
    return render_template('auth/change_password.html') 