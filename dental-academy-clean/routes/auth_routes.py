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

# Import registration logger
try:
    from utils.registration_logger import registration_logger
    from utils.visitor_tracker import VisitorTracker
except ImportError as e:
    print(f"Warning: Could not import registration_logger: {e}")
    registration_logger = None

def safe_log(log_method, *args, **kwargs):
    """Safely call registration logger methods"""
    if registration_logger and hasattr(registration_logger, log_method):
        try:
            getattr(registration_logger, log_method)(*args, **kwargs)
        except Exception as e:
            print(f"Failed to log {log_method}: {e}")
    else:
        print(f"Registration logger not available for {log_method}")

auth_bp = Blueprint('auth', __name__)

# reCAPTCHA validation
def verify_recaptcha(response_token):
    """Verify reCAPTCHA token with Google - with emergency bypass"""
    
    # === EMERGENCY FIX ===
    # Check if reCAPTCHA is enabled in production
    recaptcha_enabled = current_app.config.get('RECAPTCHA_ENABLED', True)
    if not recaptcha_enabled:
        print("=== reCAPTCHA DISABLED - BYPASSING ===")
        return True
    
    secret_key = current_app.config.get('RECAPTCHA_PRIVATE_KEY', '6LdnzsYrAAAAABe7nFDNs9L7PfSNujJZLQOywdKd')
    
    # If no key - skip
    if not secret_key or secret_key.strip() == '':
        print("=== NO RECAPTCHA KEY - BYPASSING ===")
        return True
    
    # If no token - skip only in development
    if not response_token:
        if current_app.config.get('FLASK_ENV') == 'development':
            print("=== DEVELOPMENT MODE - BYPASSING RECAPTCHA ===")
            return True
        return False
    
    data = {
        'secret': secret_key,
        'response': response_token
    }
    
    try:
        response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data, timeout=10)
        result = response.json()
        success = result.get('success', False)
        
        print(f"=== reCAPTCHA RESULT: {success} ===")
        if not success:
            print(f"=== reCAPTCHA ERRORS: {result.get('error-codes', [])} ===")
        
        return success
    except Exception as e:
        print(f"=== reCAPTCHA ERROR: {str(e)} ===")
        
        # In case of API error - skip in development
        if current_app.config.get('FLASK_ENV') == 'development':
            print("=== reCAPTCHA API ERROR - BYPASSING IN DEV ===")
            return True
        
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

# Activating authentication routes:
@auth_bp.route('/logout')
@auth_bp.route('/<lang>/logout')
@login_required
def logout(lang=None):
    """Logout user"""
    logout_user()
    if not lang:
        lang = g.get('lang', 'en')
    return redirect(f'/{lang}/')

# Keeping only DigiD:
@auth_bp.route('/digid/login')
def digid_login():
    from flask import render_template, request, g
    # Use g.lang, which is set in before_request
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
    # Can add session cleanup if needed: session.clear()
    lang = g.get('lang', 'en')
    return redirect(f'/{lang}/')


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
    return redirect(url_for('profile.index', lang=g.get('lang', 'en')))

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
    return redirect(url_for('profile.index', lang=g.get('lang', 'en')))

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
    return redirect(url_for('profile.index', lang=g.get('lang', 'en')))

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
            return redirect(url_for('profile.index', lang=g.get('lang', 'en')))
            
        except Exception as e:
            db.session.rollback()
            flash('Failed to change password. Please try again.', 'error')
    
    return render_template('auth/change_password.html')

# @auth_bp.route('/register', methods=['GET', 'POST'])
# def register():
#     """Extended registration form for new users - DISABLED"""
#     # Redirect to quick registration instead
#     from flask import redirect, url_for, g
#     lang = g.get('lang', 'nl')
#     return redirect(url_for('auth.quick_register', lang=lang))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Extended registration form for new users - REDIRECTED TO QUICK REGISTER"""
    from flask import redirect, url_for, g
    lang = g.get('lang', 'nl')
    return redirect(url_for('auth.quick_register', lang=lang))

@auth_bp.route('/login', methods=['GET', 'POST'])
@auth_bp.route('/<string:lang>/login', methods=['GET', 'POST'])
def login(lang=None):
    """Login form for registered users"""
    if request.method == 'GET':
        from flask import g, session
        
        # Get language from URL parameter, session, or default
        if lang and lang in ['nl', 'en', 'ru', 'uk', 'es', 'pt', 'tr', 'fa', 'ar']:
            g.lang = lang
            session['lang'] = lang
        else:
            lang = g.get('lang', session.get('lang', 'nl'))
        
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
            if user.is_deleted:
                return jsonify({
                    'success': False,
                    'error': 'Account has been deleted. Please register again to restore your account.'
                }), 400
            
            if not user.is_active:
                return jsonify({
                    'success': False,
                    'error': 'Account is deactivated'
                }), 400
            
            # ✅ Убрали проверку подтверждения email - пользователи активны сразу!
            
            login_user(user, remember=True)
            user.last_login = datetime.now(timezone.utc)
            db.session.commit()
            
            # Логируем успешный вход
            try:
                from utils.system_monitor import log_user_login
                log_user_login(user.id, user.email, success=True)
            except Exception as e:
                current_app.logger.error(f"Failed to log user login: {e}")
            
            # Check if profile is complete
            if not user.registration_completed:
                # Force profile completion for new users
                user_lang = user.language or session.get('lang', 'nl')
                redirect_url = f'/{user_lang}/profile?complete=true'
                return jsonify({
                    'success': True,
                    'message': 'Please complete your profile',
                    'redirect_url': redirect_url,
                    'profile_incomplete': True
                })
            
            # Determine redirect URL
            from flask import session
            next_url = session.pop('next', None)
            
            if next_url:
                # If there's a stored URL, redirect there
                redirect_url = next_url
            else:
                # Default redirect based on user role and language
                user_lang = user.language or session.get('lang', 'nl')
                if user.is_admin:
                    redirect_url = '/admin'
                else:
                    redirect_url = f'/{user_lang}/'
            
            return jsonify({
                'success': True,
                'message': 'Login successful',
                'redirect_url': redirect_url
            })
        else:
            # Логируем неудачную попытку входа
            try:
                from utils.system_monitor import log_user_login
                log_user_login(None, email, success=False, error_message='Invalid email or password')
            except Exception as e:
                current_app.logger.error(f"Failed to log failed login: {e}")
            
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
        current_app.logger.info(f"=== EMAIL CONFIRMATION ATTEMPT ===")
        current_app.logger.info(f"Token received: {token[:10]}...")
        
        # Find user by token - try both hashed and plain token for backward compatibility
        import hashlib
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # First try to find by hashed token (new format)
        user = User.query.filter_by(email_confirmation_token=token_hash).first()
        
        # If not found, try to find by plain token (old format for backward compatibility)
        if not user:
            current_app.logger.info("Token not found as hash, trying plain token...")
            user = User.query.filter_by(email_confirmation_token=token).first()
        
        if not user:
            current_app.logger.warning(f"User not found for token: {token[:10]}...")
            flash('Invalid or expired confirmation link', 'error')
            return redirect(url_for('auth.login'))
        
        current_app.logger.info(f"User found: {user.email}")
        current_app.logger.info(f"User current status - is_active: {user.is_active}, email_confirmed: {user.email_confirmed}")
        
        # Verify token
        if not user.verify_email_confirmation_token(token):
            current_app.logger.warning(f"Token verification failed for user: {user.email}")
            flash('Confirmation link has expired. Please request a new one.', 'error')
            return redirect(url_for('auth.login'))
        
        current_app.logger.info(f"Token verified successfully for user: {user.email}")
        
        # Confirm email and activate user
        user.confirm_email()
        user.email_confirmed = True
        user.email_confirmation_token = None
        user.is_active = True  # Activate user after email confirmation
        db.session.commit()
        
        current_app.logger.info(f"User activated successfully: {user.email} - is_active: {user.is_active}, email_confirmed: {user.email_confirmed}")
        
        # Send welcome email (with error handling)
        try:
            from utils.email_service import send_welcome_email
            send_welcome_email(user)
            current_app.logger.info(f"Welcome email sent to: {user.email}")
        except Exception as welcome_error:
            current_app.logger.warning(f"Failed to send welcome email to {user.email}: {str(welcome_error)}")
        
        flash('Email successfully confirmed! Welcome to Mentora!', 'success')
        current_app.logger.info(f"=== EMAIL CONFIRMATION SUCCESS ===")
        return redirect(url_for('auth.login'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Email confirmation error: {str(e)}", exc_info=True)
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
            user.optional_consents = False
            db.session.commit()
            
            flash('You have been successfully unsubscribed from marketing communications.', 'success')
            current_app.logger.info(f"User {user.email} unsubscribed from marketing")
        else:
            flash('User not found.', 'error')
            
    except Exception as e:
        current_app.logger.error(f"Unsubscribe error: {e}")
        flash('An error occurred while processing your unsubscribe request.', 'error')
    
    lang = g.get('lang', 'en')
    return redirect(f'/{lang}/')

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
            # Try to find by partial email for debugging
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
        
        # Clear any existing reset token first
        if user.password_reset_token:
            print("=== CLEARING EXISTING RESET TOKEN ===")
            user.clear_password_reset_token()
            db.session.commit()
        
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
        print(f"=== RESET PASSWORD ROUTE CALLED ===")
        print(f"=== TOKEN RECEIVED: {token[:20]}... ===")
        
        # Find user by hashed token (since we store hashed tokens in database)
        import hashlib
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        print(f"=== TOKEN HASH: {token_hash[:20]}... ===")
        
        user = User.query.filter_by(password_reset_token=token_hash).first()
        
        if not user:
            print(f"=== NO USER FOUND FOR TOKEN ===")
            flash('Invalid or expired password reset link. Please request a new password reset.', 'error')
            return redirect(url_for('auth.forgot_password'))
        
        print(f"=== USER FOUND: {user.email} ===")
        
        # Verify token
        if not user.verify_password_reset_token(token):
            flash('Password reset link has expired. Please request a new password reset.', 'error')
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

@auth_bp.route('/quick-register', methods=['GET', 'POST'])
@auth_bp.route('/<string:lang>/quick-register', methods=['GET', 'POST'])
def quick_register(lang=None):
    """Quick registration form for new users"""
    
    if request.method == 'GET':
        # Отслеживаем посещение страницы быстрой регистрации
        VisitorTracker.track_page_visit('quick_register', lang)
        from flask import g, session
        
        # Get language from URL parameter, session, or default
        if lang and lang in ['nl', 'en', 'ru', 'uk', 'es', 'pt', 'tr', 'fa', 'ar']:
            g.lang = lang
            session['lang'] = lang
        else:
            lang = g.get('lang', session.get('lang', 'nl'))
        
        return render_template('auth/quick_register.html', lang=lang)
    
    # Log the attempt immediately, even if it fails
    print(f"Quick registration POST request received")
    
    # Check if we have access to Flask context
    try:
        from flask import current_app
        print(f"Flask context available: {current_app is not None}")
    except Exception as e:
        print(f"Flask context error: {e}")
    
    safe_log('log_registration_start', 'quick_registration', {'method': 'POST', 'url': request.url})
    
    try:
        print(f"Attempting to get JSON data from request")
        data = request.get_json()
        print(f"Quick registration attempt - Data received: {data}")
        
        if not data:
            print("No data received in request")
            return jsonify({
                'success': False,
                'error': 'No data received'
            }), 400
        
        # Log registration start
        safe_log('log_registration_start', 'quick_registration', data)
        
        # Валидация данных
        required_fields = ['firstName', 'lastName', 'birthDate', 'email', 'password', 'profession']
        for field in required_fields:
            if not data.get(field):
                safe_log('log_validation_error', 'quick_registration', field, 'Required field is missing', data)
                return jsonify({
                    'success': False,
                    'error': f'Field {field} is required'
                }), 400
        
        # Валидация пароля
        password = data.get('password', '').strip()
        confirm_password = data.get('confirmPassword', '').strip()
        
        if len(password) < 8:
            safe_log('log_validation_error', 'quick_registration', 'password', 'Password too short', data)
            return jsonify({
                'success': False,
                'error': 'Password must be at least 8 characters long'
            }), 400
        
        if password != confirm_password:
            safe_log('log_validation_error', 'quick_registration', 'password', 'Passwords do not match', data)
            return jsonify({
                'success': False,
                'error': 'Passwords do not match'
            }), 400
        
        # Валидация профессии
        profession = data.get('profession')
        valid_professions = ['dentist', 'pharmacist', 'family_doctor', 'nurse', 'other']
        if profession not in valid_professions:
            safe_log('log_validation_error', 'quick_registration', 'profession', 'Invalid profession selected', data)
            return jsonify({
                'success': False,
                'error': 'Invalid profession selected'
            }), 400
        
        # Если выбрано "другое", проверяем поле otherProfession
        if profession == 'other':
            other_profession = data.get('otherProfession', '').strip()
            if not other_profession:
                safe_log('log_validation_error', 'quick_registration', 'otherProfession', 'Other profession not specified', data)
                return jsonify({
                    'success': False,
                    'error': 'Please specify your profession'
                }), 400
            # Используем указанную профессию вместо "other"
            profession = other_profession
        
        # Проверка reCAPTCHA
        try:
            recaptcha_enabled = current_app.config.get('RECAPTCHA_ENABLED', True)
        except Exception as e:
            print(f"Error getting RECAPTCHA config: {e}")
            recaptcha_enabled = True
        
        if recaptcha_enabled:
            recaptcha_response = data.get('g-recaptcha-response')
            if not recaptcha_response:
                safe_log('log_validation_error', 'quick_registration', 'g-recaptcha-response', 'No reCAPTCHA response provided', data)
                return jsonify({
                    'success': False,
                    'error': 'Please complete the reCAPTCHA verification'
                }), 400
            
            if not verify_recaptcha(recaptcha_response):
                safe_log('log_validation_error', 'quick_registration', 'g-recaptcha-response', 'Invalid reCAPTCHA response', data)
                return jsonify({
                    'success': False,
                    'error': 'reCAPTCHA verification failed. Please try again.'
                }), 400
        
        # Проверка согласий
        privacy_consent = data.get('privacyConsent', False)
        terms_consent = data.get('termsConsent', False)
        
        if not privacy_consent or not terms_consent:
            safe_log('log_validation_error', 'quick_registration', 'consent', 'Privacy or terms consent not provided', data)
            return jsonify({
                'success': False,
                'error': 'You must agree to the privacy policy and terms of service'
            }), 400
        
        # Проверка существования пользователя
        existing_user = User.query.filter_by(email=data['email']).first()
        if existing_user:
            # Если пользователь удален мягко, восстанавливаем его
            if existing_user.is_deleted:
                print(f"🔄 RESTORING SOFT DELETED USER: {existing_user.email}")
                existing_user.restore()
                
                # Обновляем данные пользователя
                existing_user.first_name = data['firstName']
                existing_user.last_name = data['lastName']
                existing_user.birth_date = datetime.strptime(data['birthDate'], '%Y-%m-%d').date()
                existing_user.profession = data['profession']
                existing_user.required_consents = True
                existing_user.optional_consents = data.get('marketingConsent', False)
                
                # Устанавливаем новый пароль
                existing_user.set_password(password)
                
                # Сохраняем изменения
                db.session.commit()
                
                # Отправляем welcome email
                try:
                    from utils.email_service import send_welcome_email
                    send_welcome_email(existing_user)
                    safe_log('log_registration_success', 'quick_registration', existing_user.id, existing_user.email, data)
                except Exception as e:
                    safe_log('log_unexpected_error', 'quick_registration', f'Email service error: {str(e)}', data)
                
                return jsonify({
                    'success': True,
                    'message': 'Account restored successfully! Welcome back! Check your email for login details.',
                    'redirect_url': url_for('auth.login')
                })
            else:
                # Пользователь активен, нельзя регистрироваться
                safe_log('log_business_logic_error', 'quick_registration', 'email_exists', f'Email already registered: {existing_user.email}', data)
                return jsonify({
                    'success': False,
                    'error': 'User with this email already exists'
                }), 400
        
        # Создание нового пользователя
        try:
            birth_date = datetime.strptime(data['birthDate'], '%Y-%m-%d').date()
        except Exception as e:
            print(f"Error parsing birth date: {e}")
            safe_log('log_validation_error', 'quick_registration', 'birthDate', f'Invalid birth date format: {e}', data)
            return jsonify({
                'success': False,
                'error': 'Invalid birth date format'
            }), 400
        
        user = User(
            first_name=data['firstName'],
            last_name=data['lastName'],
            email=data['email'],
            birth_date=birth_date,
            profession=data['profession'],
            required_consents=True,  # Terms and privacy consent
            optional_consents=data.get('marketingConsent', False),  # Marketing consent
            is_active=True,  # ✅ Активируем сразу после регистрации!
            email_confirmed=True  # ✅ Не требуем подтверждение email
        )
        
        # Установка пароля пользователя
        try:
            user.set_password(password)
        except Exception as e:
            print(f"Error setting password: {e}")
            safe_log('log_unexpected_error', 'quick_registration', e, data)
            return jsonify({
                'success': False,
                'error': 'Failed to create user account'
            }), 500
        
        try:
            db.session.add(user)
            db.session.commit()
        except Exception as e:
            safe_log('log_database_error', 'quick_registration', 'create_user', str(e), data)
            raise
        
        # Логируем регистрацию нового пользователя
        try:
            from utils.system_monitor import log_user_registration
            log_user_registration(user.id, user.email, registration_method='email')
        except Exception as e:
            current_app.logger.error(f"Failed to log user registration: {e}")
        
        # ✅ Отправляем welcome email с данными для входа
        try:
            from utils.email_service import send_welcome_email
            email_sent = send_welcome_email(user)
            if email_sent:
                safe_log('log_registration_success', 'quick_registration', user.id, user.email, data)
            else:
                safe_log('log_unexpected_error', 'quick_registration', 'Failed to send welcome email', data)
        except Exception as e:
            safe_log('log_unexpected_error', 'quick_registration', f'Email service error: {str(e)}', data)
        
        # Отслеживаем завершение регистрации
        VisitorTracker.track_registration_completion('quick_register', user.id)
        
        return jsonify({
            'success': True,
            'message': 'Registration successful! Welcome to Mentora! Check your email for login details.',
            'redirect_url': url_for('auth.login')
        })
        
    except Exception as e:
        db.session.rollback()
        
        # Enhanced error logging
        safe_log('log_unexpected_error', 'quick_registration', e, data if 'data' in locals() else None)
        
        # Fallback logging
        import traceback
        print(f"Quick registration error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        
        return jsonify({
            'success': False,
            'error': 'Registration failed. Please try again.'
        }), 500




# ========================================
# INVITATION-BASED REGISTRATION
# ========================================

@auth_bp.route('/invite/<token>')
def invite_register(token):
    """Страница регистрации по приглашению"""
    from utils.registration_logger import registration_logger
    from utils.visitor_tracker import VisitorTracker
    
    try:
        from models import Invitation
        
        # Находим приглашение по токену
        invitation = Invitation.query.filter_by(token=token).first()
        
        if not invitation:
            registration_logger.log_business_logic_error('invite_registration', 'invalid_token', f'Invalid invitation token: {token}', {'token': token})
            flash('Недействительная ссылка приглашения', 'error')
            return redirect(url_for('auth.login'))
        
        if not invitation.is_valid():
            if invitation.is_expired():
                registration_logger.log_business_logic_error('invite_registration', 'expired_token', f'Expired invitation token: {token}', {'token': token, 'email': invitation.email})
                flash('Срок действия приглашения истек', 'error')
            else:
                registration_logger.log_business_logic_error('invite_registration', 'used_token', f'Used invitation token: {token}', {'token': token, 'email': invitation.email})
                flash('Приглашение уже использовано или отменено', 'error')
            return redirect(url_for('auth.login'))
        
        # Проверяем, не зарегистрирован ли уже пользователь с этим email
        existing_user = User.query.filter_by(email=invitation.email).first()
        if existing_user:
            if existing_user.is_deleted:
                # Пользователь удален мягко, разрешаем восстановление
                flash('Ваш аккаунт был удален. Вы можете восстановить его, заполнив форму ниже.', 'info')
            else:
                # Пользователь активен
                registration_logger.log_business_logic_error('invite_registration', 'email_exists', f'Email already registered: {invitation.email}', {'token': token, 'email': invitation.email})
                flash('Пользователь с этим email уже зарегистрирован', 'error')
                return redirect(url_for('auth.login'))
        
        # Получаем язык из параметров или используем английский по умолчанию
        lang = request.args.get('lang', 'en')
        
        return render_template('auth/invite_register.html',
                             invitation=invitation,
                             lang=lang)
    
    except Exception as e:
        registration_logger.log_unexpected_error('invite_registration', e, {'token': token})
        flash('Ошибка загрузки страницы приглашения', 'error')
        return redirect(url_for('auth.login'))


@auth_bp.route('/invite/<token>/register', methods=['POST'])
def invite_register_submit(token):
    """Обработка регистрации по приглашению"""
    from utils.registration_logger import registration_logger
    from utils.visitor_tracker import VisitorTracker
    
    try:
        from models import Invitation
        
        # Получаем данные формы
        data = request.get_json()
        
        # Log registration start
        registration_logger.log_registration_start('invite_registration', data)
        
        # Находим приглашение
        invitation = Invitation.query.filter_by(token=token).first()
        
        if not invitation or not invitation.is_valid():
            registration_logger.log_business_logic_error('invite_registration', 'invalid_token', f'Invalid or expired invitation token: {token}', data)
            return jsonify({
                'success': False,
                'error': 'Недействительное или истекшее приглашение'
            }), 400
        
        if not data:
            registration_logger.log_validation_error('invite_registration', 'form_data', 'No form data received', data)
            return jsonify({
                'success': False,
                'error': 'Данные формы не получены'
            }), 400
        
        # Валидация пароля
        password = data.get('password', '').strip()
        confirm_password = data.get('confirmPassword', '').strip()
        
        if not password or len(password) < 6:
            registration_logger.log_validation_error('invite_registration', 'password', 'Password too short', data)
            return jsonify({
                'success': False,
                'error': 'Пароль должен содержать минимум 6 символов'
            }), 400
        
        if password != confirm_password:
            registration_logger.log_validation_error('invite_registration', 'password', 'Passwords do not match', data)
            return jsonify({
                'success': False,
                'error': 'Пароли не совпадают'
            }), 400
        
        # Проверяем, не зарегистрирован ли уже пользователь
        existing_user = User.query.filter_by(email=invitation.email).first()
        if existing_user:
            # Если пользователь удален мягко, восстанавливаем его
            if existing_user.is_deleted:
                print(f"🔄 RESTORING SOFT DELETED USER VIA INVITATION: {existing_user.email}")
                existing_user.restore()
                
                # Обновляем данные пользователя
                existing_user.first_name = data['firstName']
                existing_user.last_name = data['lastName']
                existing_user.birth_date = datetime.strptime(data['birthDate'], '%Y-%m-%d').date()
                existing_user.profession = data['profession']
                existing_user.required_consents = True
                existing_user.optional_consents = data.get('marketingConsent', False)
                
                # Устанавливаем новый пароль
                existing_user.set_password(data['password'])
                
                # Сохраняем изменения
                db.session.commit()
                
                # Отправляем welcome email
                try:
                    from utils.email_service import send_welcome_email
                    send_welcome_email(existing_user)
                    registration_logger.log_registration_success('invite_registration', existing_user.id, existing_user.email, data)
                except Exception as e:
                    registration_logger.log_unexpected_error('invite_registration', f'Email service error: {str(e)}', data)
                
                return jsonify({
                    'success': True,
                    'message': 'Account restored successfully! Welcome back! Check your email for login details.',
                    'redirect_url': url_for('auth.login')
                })
            else:
                # Пользователь активен, нельзя регистрироваться
                registration_logger.log_business_logic_error('invite_registration', 'email_exists', f'Email already registered: {invitation.email}', data)
                return jsonify({
                    'success': False,
                    'error': 'Пользователь с этим email уже зарегистрирован'
                }), 400
        
        # Создаем нового пользователя
        user = User(
            first_name=invitation.contact.full_name.split()[0] if invitation.contact.full_name else '',
            last_name=' '.join(invitation.contact.full_name.split()[1:]) if invitation.contact.full_name and len(invitation.contact.full_name.split()) > 1 else '',
            email=invitation.email,
            phone=invitation.contact.phone,
            profession=invitation.contact.profession.name if invitation.contact.profession else None,
            workplace=invitation.contact.workplace,
            is_active=True,  # Активируем сразу, так как приглашение от админа
            email_confirmed=True,  # Подтверждаем email сразу
            registration_completed=True
        )
        
        # Устанавливаем пароль
        user.set_password(password)
        
        try:
            db.session.add(user)
            
            # Обновляем приглашение
            invitation.status = 'accepted'
            invitation.accepted_at = datetime.utcnow()
            invitation.user_id = user.id
            
            # Связываем контакт с пользователем
            invitation.contact.user_id = user.id
            
            db.session.commit()
        except Exception as e:
            registration_logger.log_database_error('invite_registration', 'create_user_and_update_invitation', str(e), data)
            raise
        
        # Автоматически логиним пользователя
        login_user(user, remember=True)
        
        # Log successful registration
        registration_logger.log_registration_success('invite_registration', user.id, user.email, data)
        
        lang = session.get('lang') or 'nl'
        return jsonify({
            'success': True,
            'message': 'Регистрация успешно завершена!',
            'redirect_url': url_for('learning_map_bp.learning_map', lang=lang)
        })
        
    except Exception as e:
        db.session.rollback()
        registration_logger.log_unexpected_error('invite_registration', e, data)
        return jsonify({
            'success': False,
            'error': 'Ошибка регистрации. Попробуйте еще раз.'
        }), 500 