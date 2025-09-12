# routes/auth_routes.py - Authentication routes

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app, g
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
import requests
import re
from datetime import datetime, timezone

auth_bp = Blueprint('auth', __name__)

# reCAPTCHA validation
def verify_recaptcha(response_token):
    """Verify reCAPTCHA token with Google"""
    secret_key = current_app.config.get('RECAPTCHA_PRIVATE_KEY', '6LdnzsYrAAAAABe7nFDNs9L7PfSNujJZLQOywdKd')
    
    data = {
        'secret': secret_key,
        'response': response_token
    }
    
    try:
        response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data, timeout=10)
        result = response.json()
        return result.get('success', False)
    except Exception as e:
        print(f"reCAPTCHA verification error: {e}")
        return False

# Email validation
def validate_email_format(email):
    """Validate email format using regex"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_email_domain(email):
    """Check if email domain exists (basic validation)"""
    domain = email.split('@')[1] if '@' in email else ''
    
    # List of common disposable email domains
    disposable_domains = [
        '10minutemail.com', 'tempmail.org', 'guerrillamail.com',
        'mailinator.com', 'yopmail.com', 'temp-mail.org'
    ]
    
    if domain.lower() in disposable_domains:
        return False
    
    return True

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

# Активирую маршруты аутентификации:
@auth_bp.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    return redirect(url_for('main.index', lang=g.get('lang', 'en')))

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
    return redirect(url_for('main.index', lang=g.get('lang', 'en')))

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
    country_code = request.form.get('country_code', '').strip()
    
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
    if country_code != current_user.country_code:
        changes.append(('country_code', current_user.country_code, country_code))
    
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
    current_user.country_code = country_code or None
    current_user.profile_updated_at = datetime.now(timezone.utc)
    
    # Log changes
    for field, old_val, new_val in changes:
        current_user.log_profile_change(field, old_val, new_val)
    
    db.session.commit()
    flash('Personal information updated successfully!', 'success')
    return redirect(url_for('auth.profile'))

def handle_professional_data_update():
    """Handle professional data section updates"""
    workplace = request.form.get('workplace', '').strip()
    specialization = request.form.get('specialization', '').strip()
    profession = request.form.get('profession', '').strip()
    other_profession = request.form.get('other_profession', '').strip()
    
    # Track changes
    changes = []
    if workplace != current_user.workplace:
        changes.append(('workplace', current_user.workplace, workplace))
    if specialization != current_user.specialization:
        changes.append(('specialization', current_user.specialization, specialization))
    if profession != current_user.profession:
        changes.append(('profession', current_user.profession, profession))
    if other_profession != current_user.other_profession:
        changes.append(('other_profession', current_user.other_profession, other_profession))
    
    # Update data
    current_user.workplace = workplace or None
    current_user.specialization = specialization or None
    current_user.profession = profession or None
    current_user.other_profession = other_profession or None
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

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Extended registration form for new users"""
    print(f"=== REGISTER ROUTE CALLED - METHOD: {request.method} ===")
    print(f"=== REQUEST URL: {request.url} ===")
    
    if request.method == 'GET':
        print("=== HANDLING GET REQUEST ===")
        from flask import g
        lang = g.get('lang', 'nl')
        return render_template('auth/register.html', lang=lang)
    
    try:
        print("=== HANDLING POST REQUEST ===")
        print(f"=== FORM DATA KEYS: {list(request.form.keys())} ===")
        print(f"=== FILES: {list(request.files.keys())} ===")
        
        # Get form data
        data = request.form.to_dict()
        files = request.files
        
        # Validate reCAPTCHA (only if configured)
        recaptcha_secret = current_app.config.get('RECAPTCHA_PRIVATE_KEY')
        if recaptcha_secret:
            recaptcha_response = data.get('g-recaptcha-response')
            if not recaptcha_response or not verify_recaptcha(recaptcha_response):
                print("=== reCAPTCHA VALIDATION FAILED ===")
                return jsonify({'success': False, 'error': 'Please complete the reCAPTCHA verification'}), 400
        
        # Validate email format and domain
        email = data.get('email', '').strip().lower()
        if not validate_email_format(email):
            print("=== EMAIL FORMAT VALIDATION FAILED ===")
            return jsonify({'success': False, 'error': 'Invalid email format'}), 400
        
        if not validate_email_domain(email):
            print("=== EMAIL DOMAIN VALIDATION FAILED ===")
            return jsonify({'success': False, 'error': 'Disposable email addresses are not allowed'}), 400
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email', 'password', 'confirm_password', 'birth_date', 'nationality', 'profession', 'legal_status', 'dutch_level', 'university_name', 'degree_type', 'study_start_year', 'study_end_year', 'study_country', 'required_consents', 'digital_signature']
        errors = []
        
        print("=== VALIDATING REQUIRED FIELDS ===")
        for field in required_fields:
            value = data.get(field)
            print(f"=== {field}: '{value}' ===")
            if not value:
                errors.append(f'{field} is required')
        
        print(f"=== VALIDATION ERRORS: {errors} ===")
        
        # Validate password
        password = data.get('password', '')
        confirm_password = data.get('confirm_password', '')
        
        if password != confirm_password:
            errors.append('Passwords do not match')
        
        if len(password) < 8:
            errors.append('Password must be at least 8 characters long')
        
        if not any(c.isalpha() for c in password):
            errors.append('Password must contain at least one letter')
        
        if not any(c.isdigit() for c in password):
            errors.append('Password must contain at least one number')
        
        # Check if email already exists
        print(f"=== CHECKING EMAIL: {data['email']} ===")
        existing_user = User.query.filter_by(email=data['email']).first()
        print(f"=== EXISTING USER FOUND: {existing_user is not None} ===")
        if existing_user:
            print(f"=== EXISTING USER: {existing_user.email} ({existing_user.first_name} {existing_user.last_name}) ===")
            errors.append('Email already registered')
        
        # Validate "Other" fields
        if data.get('profession') == 'other' and not data.get('other_profession'):
            errors.append('Please specify your profession')
        
        if data.get('nationality') == 'OTHER' and not data.get('other_nationality'):
            errors.append('Please specify your nationality')
        
        if data.get('legal_status') == 'other' and not data.get('other_legal_status'):
            errors.append('Please specify your legal status')
        
        # Validate digital signature (more flexible)
        digital_signature = data.get('digital_signature', '').strip()
        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        
        if not digital_signature:
            errors.append('Digital signature is required')
        elif len(digital_signature) < 3:
            errors.append('Digital signature must be at least 3 characters long')
        elif first_name and last_name:
            # Check if signature contains both first and last name (flexible matching)
            first_name_lower = first_name.lower()
            last_name_lower = last_name.lower()
            signature_lower = digital_signature.lower()
            
            if not (first_name_lower in signature_lower and last_name_lower in signature_lower):
                errors.append('Digital signature should contain your first and last name')
        
        if errors:
            print(f"=== RETURNING ERRORS: {errors} ===")
            return jsonify({
                'success': False,
                'error': '; '.join(errors)
            }), 400
        
        # Create new user
        user = User(
            email=data['email'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            birth_date=datetime.strptime(data['birth_date'], '%Y-%m-%d').date() if data['birth_date'] else None,
            gender=data.get('gender'),
            phone=data.get('phone'),
            country_code=data.get('country_code'),
            nationality=data['nationality'],
            language=data.get('language', 'nl'),
            profession=data['profession'],
            workplace=data.get('workplace'),
            specialization=data.get('specialization'),
            legal_status=data.get('legal_status'),
            dutch_level=data.get('dutch_level'),
            english_level=data.get('english_level'),
            idw_assessment=data.get('idw_assessment'),
            big_exam_registered=data.get('big_exam_registered'),
            exam_date=datetime.strptime(data['exam_date'], '%Y-%m-%d').date() if data.get('exam_date') else None,
            preparation_time=data.get('preparation_time'),
            # New structured diploma fields
            university_name=data.get('university_name'),
            degree_type=data.get('degree_type'),
            study_start_year=int(data.get('study_start_year')) if data.get('study_start_year') else None,
            study_end_year=int(data.get('study_end_year')) if data.get('study_end_year') else None,
            study_country=data.get('study_country'),
            medical_specialization=data.get('medical_specialization'),
            additional_education_info=data.get('additional_education_info'),
            # Legacy field for backward compatibility
            diploma_info=f"{data.get('university_name', '')} - {data.get('degree_type', '')} ({data.get('study_start_year', '')}-{data.get('study_end_year', '')})",
            work_experience=data.get('work_experience'),
            additional_qualifications=data.get('additional_qualifications'),
            # New fields
            other_profession=data.get('other_profession'),
            other_nationality=data.get('other_nationality'),
            other_legal_status=data.get('other_legal_status'),
            required_consents=bool(data.get('required_consents')),
            optional_consents=bool(data.get('optional_consents')),
            digital_signature=data.get('digital_signature'),
            registration_completed=True,
            is_active=True
        )
        
        # Set password from form
        user.set_password(password)
        
        # Generate email confirmation token
        confirmation_token = user.generate_email_confirmation_token()
        
        db.session.add(user)
        db.session.flush()  # Get user ID
        
        # Handle file uploads
        uploaded_files = {}
        
        # Diploma file
        if 'diploma_file' in files and files['diploma_file'].filename:
            diploma_file = files['diploma_file']
            if allowed_file(diploma_file.filename, ALLOWED_DOCUMENT_EXTENSIONS):
                filename = secure_filename(f"diploma_{user.id}_{diploma_file.filename}")
                filepath = os.path.join(DOCUMENTS_FOLDER, filename)
                diploma_file.save(filepath)
                user.diploma_file = filepath
                uploaded_files['diploma'] = filepath
        
        # Language certificates
        language_certs = []
        if 'language_certificates' in files:
            for file in files.getlist('language_certificates'):
                if file.filename and allowed_file(file.filename, ALLOWED_DOCUMENT_EXTENSIONS):
                    filename = secure_filename(f"lang_cert_{user.id}_{file.filename}")
                    filepath = os.path.join(DOCUMENTS_FOLDER, filename)
                    file.save(filepath)
                    language_certs.append(filepath)
        
        if language_certs:
            user.language_certificates = json.dumps(language_certs)
        
        # Additional documents
        additional_docs = []
        if 'additional_documents' in files:
            for file in files.getlist('additional_documents'):
                if file.filename and allowed_file(file.filename, ALLOWED_DOCUMENT_EXTENSIONS):
                    filename = secure_filename(f"additional_{user.id}_{file.filename}")
                    filepath = os.path.join(DOCUMENTS_FOLDER, filename)
                    file.save(filepath)
                    additional_docs.append(filepath)
        
        if additional_docs:
            user.additional_documents = json.dumps(additional_docs)
        
        # Store additional registration data
        registration_data = {
            'legal_status': data.get('legal_status'),
            'dutch_level': data.get('dutch_level'),
            'english_level': data.get('english_level'),
            'idw_assessment': data.get('idw_assessment'),
            'big_exam_registered': data.get('big_exam_registered'),
            'exam_date': data.get('exam_date'),
            'preparation_time': data.get('preparation_time'),
            'registration_date': datetime.now(timezone.utc).isoformat()
        }
        
        # Store in user's additional data
        user.notification_settings = json.dumps(registration_data)
        
        db.session.commit()
        
        # Send email confirmation
        from utils.email_service import send_email_confirmation
        email_sent = send_email_confirmation(user, confirmation_token)
        
        # Log registration
        try:
            user.log_profile_change('registration', 'user_registered', 'User completed registration')
        except Exception as e:
            print(f"Warning: Could not log registration: {e}")
            # Continue without failing the registration
        
        return jsonify({
            'success': True,
            'message': 'Registration completed successfully. Please check your email to confirm your account.',
            'user_id': user.id,
            'email_sent': email_sent
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Registration error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Registration failed. Please try again.'
        }), 500

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login form for registered users"""
    if request.method == 'GET':
        from flask import g
        lang = g.get('lang', 'nl')
        return render_template('auth/login.html', lang=lang)
    
    try:
        data = request.get_json() if request.is_json else request.form.to_dict()
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({
                'success': False,
                'error': 'Email and password are required'
            }), 400
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                return jsonify({
                    'success': False,
                    'error': 'Account is deactivated'
                }), 400
            
            # Check if email is confirmed
            if not user.email_confirmed:
                return jsonify({
                    'success': False,
                    'error': 'Please confirm your email before logging in. Check your inbox for confirmation link.',
                    'email_not_confirmed': True
                }), 400
            
            login_user(user, remember=True)
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'redirect_url': url_for('profile.index')
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid email or password'
            }), 401
            
    except Exception as e:
        current_app.logger.error(f"Login error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Login failed. Please try again.'
        }), 500

@auth_bp.route('/confirm-email/<token>')
def confirm_email(token):
    """Confirm user's email with token"""
    try:
        # Find user by token
        user = User.query.filter_by(email_confirmation_token=token).first()
        
        if not user:
            # Try to find by hashed token
            import hashlib
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            user = User.query.filter_by(email_confirmation_token=token_hash).first()
        
        if not user:
            flash('Invalid or expired confirmation link', 'error')
            return redirect(url_for('auth.login'))
        
        # Verify token
        if not user.verify_email_confirmation_token(token):
            flash('Confirmation link has expired. Please request a new one.', 'error')
            return redirect(url_for('auth.login'))
        
        # Confirm email
        user.confirm_email()
        db.session.commit()
        
        # Send welcome email
        from utils.email_service import send_welcome_email
        send_welcome_email(user)
        
        flash('Email successfully confirmed! Welcome to Mentora!', 'success')
        return redirect(url_for('auth.login'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Email confirmation error: {str(e)}")
        flash('An error occurred while confirming email', 'error')
        return redirect(url_for('auth.login'))

@auth_bp.route('/resend-confirmation', methods=['POST'])
def resend_confirmation():
    """Resend email confirmation"""
    try:
        data = request.get_json()
        email = data.get('email')
        
        if not email:
            return jsonify({
                'success': False,
                'error': 'Email is required'
            }), 400
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        if user.email_confirmed:
            return jsonify({
                'success': False,
                'error': 'Email already confirmed'
            }), 400
        
        # Generate new token
        confirmation_token = user.generate_email_confirmation_token()
        db.session.commit()
        
        # Send email
        from utils.email_service import send_email_confirmation
        email_sent = send_email_confirmation(user, confirmation_token)
        
        return jsonify({
            'success': True,
            'message': 'Confirmation email sent successfully',
            'email_sent': email_sent
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Resend confirmation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to resend confirmation email'
        }), 500

@auth_bp.route('/auth/unsubscribe/<int:user_id>')
def unsubscribe(user_id):
    """Handle unsubscribe requests"""
    try:
        user = User.query.get(user_id)
        if user:
            # Update user's marketing consent
            user.marketing_consent = False
            db.session.commit()
            
            flash('You have been successfully unsubscribed from marketing communications.', 'success')
            current_app.logger.info(f"User {user.email} unsubscribed from marketing")
        else:
            flash('User not found.', 'error')
            
    except Exception as e:
        current_app.logger.error(f"Unsubscribe error: {e}")
        flash('An error occurred while processing your unsubscribe request.', 'error')
    
    return redirect(url_for('main.index', lang=g.get('lang', 'en')))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Forgot password form"""
    print(f"=== FORGOT PASSWORD ROUTE CALLED - METHOD: {request.method} ===")
    print(f"=== REQUEST URL: {request.url} ===")
    print(f"=== REQUEST HEADERS: {dict(request.headers)} ===")
    
    if request.method == 'GET':
        print("=== HANDLING GET REQUEST ===")
        from flask import g
        lang = g.get('lang', 'nl')
        return render_template('auth/forgot_password.html', lang=lang)
    
    try:
        print("=== FORGOT PASSWORD REQUEST START ===")
        
        data = request.get_json() if request.is_json else request.form.to_dict()
        email = data.get('email', '').strip()
        
        print(f"=== EMAIL RECEIVED: {email} ===")
        
        if not email:
            print("=== ERROR: No email provided ===")
            return jsonify({
                'success': False,
                'error': 'Email is required'
            }), 400
        
        # Find user by email
        print(f"=== SEARCHING FOR USER WITH EMAIL: '{email}' ===")
        print(f"=== EMAIL LENGTH: {len(email)} ===")
        print(f"=== EMAIL BYTES: {email.encode('utf-8')} ===")
        
        user = User.query.filter_by(email=email).first()
        print(f"=== USER FOUND: {user is not None} ===")
        
        if user:
            print(f"=== USER DETAILS: {user.email} ({user.first_name} {user.last_name}) ===")
        else:
            # Попробуем найти по части email для отладки
            similar_users = User.query.filter(User.email.like(f'%{email.split("@")[0]}%')).all()
            print(f"=== SIMILAR USERS FOUND: {len(similar_users)} ===")
            for u in similar_users:
                print(f"=== SIMILAR: '{u.email}' ===")
        
        if not user:
            print("=== USER NOT FOUND - returning generic message ===")
            # Don't reveal if email exists or not for security
            return jsonify({
                'success': True,
                'message': 'If the email exists, a password reset link has been sent.'
            })
        
        print(f"=== USER FOUND: {user.email} ===")
        
        # Generate password reset token
        print("=== GENERATING PASSWORD RESET TOKEN ===")
        reset_token = user.generate_password_reset_token()
        print(f"=== TOKEN GENERATED: {reset_token[:20]}... ===")
        
        db.session.commit()
        print("=== DATABASE COMMITTED ===")
        
        # Send password reset email
        print("=== STARTING EMAIL SENDING ===")
        from utils.email_service import send_password_reset_email
        
        # Check email configuration
        print(f"=== MAIL_SUPPRESS_SEND: {current_app.config.get('MAIL_SUPPRESS_SEND')} ===")
        print(f"=== MAIL_USERNAME: {current_app.config.get('MAIL_USERNAME')} ===")
        print(f"=== MAIL_PASSWORD: {'***' if current_app.config.get('MAIL_PASSWORD') else 'NOT SET'} ===")
        print(f"=== MAIL_SERVER: {current_app.config.get('MAIL_SERVER')} ===")
        
        email_sent = send_password_reset_email(user, reset_token)
        print(f"=== EMAIL SENDING RESULT: {email_sent} ===")
        
        return jsonify({
            'success': True,
            'message': 'If the email exists, a password reset link has been sent.',
            'email_sent': email_sent
        })
        
    except Exception as e:
        print(f"=== FORGOT PASSWORD ERROR: {str(e)} ===")
        import traceback
        print(f"=== TRACEBACK: {traceback.format_exc()} ===")
        
        db.session.rollback()
        current_app.logger.error(f"Forgot password error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to process password reset request'
        }), 500

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token"""
    try:
        # Find user by token
        user = User.query.filter_by(password_reset_token=token).first()
        
        if not user:
            # Try to find by hashed token
            import hashlib
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            user = User.query.filter_by(password_reset_token=token_hash).first()
        
        if not user:
            flash('Неверная или истекшая ссылка сброса пароля', 'error')
            return redirect(url_for('auth.forgot_password'))
        
        # Verify token
        if not user.verify_password_reset_token(token):
            flash('Ссылка сброса пароля истекла. Пожалуйста, запросите новую.', 'error')
            return redirect(url_for('auth.forgot_password'))
        
        if request.method == 'GET':
            from flask import g
            lang = g.get('lang', 'nl')
            return render_template('auth/reset_password.html', token=token, lang=lang)
        
        # Handle POST request
        data = request.get_json() if request.is_json else request.form.to_dict()
        password = data.get('password', '').strip()
        confirm_password = data.get('confirm_password', '').strip()
        
        # Validate password
        if not password or not confirm_password:
            return jsonify({
                'success': False,
                'error': 'Password and confirmation are required'
            }), 400
        
        if password != confirm_password:
            return jsonify({
                'success': False,
                'error': 'Passwords do not match'
            }), 400
        
        if len(password) < 8:
            return jsonify({
                'success': False,
                'error': 'Password must be at least 8 characters long'
            }), 400
        
        if not any(c.isalpha() for c in password):
            return jsonify({
                'success': False,
                'error': 'Password must contain at least one letter'
            }), 400
        
        if not any(c.isdigit() for c in password):
            return jsonify({
                'success': False,
                'error': 'Password must contain at least one number'
            }), 400
        
        # Update password
        user.set_password(password)
        user.clear_password_reset_token()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Password has been reset successfully. You can now log in with your new password.',
            'redirect_url': url_for('auth.login')
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Reset password error: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to reset password'
        }), 500 