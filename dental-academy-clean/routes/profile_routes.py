# profile_routes.py - Profile management routes
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app, g, session
from flask_login import login_required, current_user
from models import User
from extensions import db

# Create blueprint with language support
profile_bp = Blueprint('profile', __name__, url_prefix='/<string:lang>/profile')

@profile_bp.before_request
def before_request():
    """Set language from URL parameter or session"""
    try:
        # Get language from URL parameter (from url_prefix)
        lang_from_url = request.view_args.get('lang') if request.view_args else None
        lang = lang_from_url or request.args.get('lang', 'en')
        
        current_app.logger.info(f"Profile route language request: {lang}")
        
        if lang in ['en', 'ru', 'nl', 'es', 'pt', 'tr', 'uk', 'fa', 'ar']:
            g.lang = lang
            session['lang'] = lang
            current_app.logger.info(f"Language set to: {lang}")
        else:
            g.lang = session.get('lang', 'en')
            current_app.logger.info(f"Language fallback to: {g.lang}")
            
    except Exception as e:
        current_app.logger.error(f"Error in profile before_request: {e}", exc_info=True)
        g.lang = 'en'  # Fallback to English

@profile_bp.route('/')
@login_required
def profile(lang):
    """Profile page"""
    try:
        current_app.logger.info(f"Profile page accessed by user: {current_user.id}")
        
        # Check if user needs to complete profile
        force_completion = request.args.get('complete') == 'true'
        profile_incomplete = not current_user.registration_completed
        
        return render_template('profile/index.html', 
                             user=current_user, 
                             force_completion=force_completion,
                             profile_incomplete=profile_incomplete)
    except Exception as e:
        current_app.logger.error(f"Error in profile route: {e}", exc_info=True)
        flash('Произошла ошибка при загрузке профиля', 'error')
        return redirect(url_for('main.index', lang=lang))

@profile_bp.route('/personal_info')
@login_required
def personal_info(lang):
    """Personal information page"""
    return render_template('profile/personal_info.html', user=current_user, lang=lang)

@profile_bp.route('/membership-card')
@login_required
def membership_card(lang):
    """Display membership card in profile"""
    # Generate member ID if not exists
    if not hasattr(current_user, 'member_id') or not current_user.member_id:
        import hashlib
        user_hash = hashlib.md5(str(current_user.id).encode()).hexdigest()[:5].upper()
        current_user.member_id = f"MNT-{user_hash}"
        db.session.commit()
    
    # Set membership expiry date if not exists (1 year from now)
    if not hasattr(current_user, 'membership_expires') or not current_user.membership_expires:
        from datetime import datetime, timedelta
        current_user.membership_expires = datetime.now() + timedelta(days=365)
        db.session.commit()
    
    # Generate QR code if user is premium and doesn't have one
    if (hasattr(current_user, 'membership_type') and current_user.membership_type == 'premium' and 
        (not hasattr(current_user, 'qr_code_path') or not current_user.qr_code_path)):
        try:
            from routes.membership_routes import generate_member_qr
            generate_member_qr(current_user)
        except Exception as e:
            current_app.logger.warning(f"Could not generate QR code: {e}")
    
    return render_template('membership/card.html')

@profile_bp.route('/personal_info', methods=['POST'])
@login_required
def update_personal_info(lang):
    """Update personal information"""
    try:
        # Get form data
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        country_code = request.form.get('country_code', '').strip()
        birth_date = request.form.get('birth_date', '').strip()
        nationality = request.form.get('nationality', '').strip()
        other_nationality = request.form.get('other_nationality', '').strip()
        gender = request.form.get('gender', '').strip()
        dutch_level = request.form.get('dutch_level', '').strip()
        english_level = request.form.get('english_level', '').strip()
        profession = request.form.get('profession', '').strip()
        other_profession = request.form.get('other_profession', '').strip()
        workplace = request.form.get('workplace', '').strip()
        workplace_specialization = request.form.get('workplace_specialization', '').strip()
        legal_status = request.form.get('legal_status', '').strip()
        other_legal_status = request.form.get('other_legal_status', '').strip()
        university_name = request.form.get('university_name', '').strip()
        degree_type = request.form.get('degree_type', '').strip()
        study_start_year = request.form.get('study_start_year', '').strip()
        study_end_year = request.form.get('study_end_year', '').strip()
        study_country = request.form.get('study_country', '').strip()
        other_study_country = request.form.get('other_study_country', '').strip()
        medical_specialization = request.form.get('medical_specialization', '').strip()
        additional_education_info = request.form.get('additional_education_info', '').strip()
        work_experience = request.form.get('work_experience', '').strip()
        additional_qualifications = request.form.get('additional_qualifications', '').strip()
        
        # Update user data
        if first_name:
            current_user.first_name = first_name
        if last_name:
            current_user.last_name = last_name
        if email and email != current_user.email:
            current_user.email = email
        if phone:
            current_user.phone = phone
        if country_code:
            current_user.country_code = country_code
        if birth_date:
            from datetime import datetime
            try:
                current_user.birth_date = datetime.strptime(birth_date, '%Y-%m-%d').date()
            except ValueError:
                pass
        if nationality:
            current_user.nationality = nationality
        if other_nationality:
            current_user.other_nationality = other_nationality
        if gender:
            current_user.gender = gender
        if dutch_level:
            current_user.dutch_level = dutch_level
        if english_level:
            current_user.english_level = english_level
        if profession:
            current_user.profession = profession
        if other_profession:
            current_user.other_profession = other_profession
        if workplace:
            current_user.workplace = workplace
        if workplace_specialization:
            current_user.specialization = workplace_specialization
        if legal_status:
            current_user.legal_status = legal_status
        if other_legal_status:
            current_user.other_legal_status = other_legal_status
        if university_name:
            current_user.university_name = university_name
        if degree_type:
            current_user.degree_type = degree_type
        if study_start_year:
            try:
                current_user.study_start_year = int(study_start_year)
            except ValueError:
                pass
        if study_end_year:
            try:
                current_user.study_end_year = int(study_end_year)
            except ValueError:
                pass
        if study_country:
            current_user.study_country = study_country
            # Clear other_study_country if a standard country is selected
            if study_country != 'OTHER':
                current_user.other_study_country = None
        if other_study_country:
            current_user.other_study_country = other_study_country
        if medical_specialization:
            current_user.medical_specialization = medical_specialization
        if additional_education_info:
            current_user.additional_education_info = additional_education_info
        if work_experience:
            current_user.work_experience = work_experience
        if additional_qualifications:
            current_user.additional_qualifications = additional_qualifications
            
        # Check if profile is complete using the same logic as learning map
        from utils.profile_check import check_profile_complete
        profile_check = check_profile_complete(current_user)
        
        # Mark registration as completed if profile is complete
        profile_was_complete = current_user.registration_completed
        if profile_check['is_complete']:
            current_user.registration_completed = True
            current_app.logger.info(f"Profile completed for user: {current_user.email}")
            
        db.session.commit()
        
        # Show success message
        if profile_check['is_complete'] and not profile_was_complete:
            flash('Great! Your profile is now complete. You can now access the learning map!', 'success')
        else:
            flash('Personal information updated successfully!', 'success')
        
        # Determine redirect target
        redirect_target = url_for('profile.personal_info', lang=lang)
        if profile_check['is_complete'] and not profile_was_complete:
            redirect_target = url_for('learning_map_bp.learning_map', lang=lang, path_id='irt', tour='1')
        elif request.form.get('force_completion') == 'true':
            redirect_target = url_for('main.index', lang=lang)
        
        return redirect(redirect_target)
        
    except Exception as e:
        current_app.logger.error(f"Error updating personal info: {e}", exc_info=True)
        db.session.rollback()
        flash('Error updating personal information', 'error')
    
    return redirect(url_for('profile.personal_info', lang=lang))

@profile_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings(lang):
    """Profile settings page"""
    if request.method == 'POST':
        return update_settings(lang)
    return render_template('profile/settings.html', user=current_user)


def update_settings(lang):
    """Handle settings form submission"""
    supported_languages = {'nl', 'en', 'ru', 'es', 'pt', 'uk', 'fa', 'tr'}
    updated_lang = lang
    try:
        # Interface language
        new_language = request.form.get('language', '').strip()
        if new_language in supported_languages:
            current_user.language = new_language
            session['lang'] = new_language
            g.lang = new_language
            updated_lang = new_language
        
        # Theme preference
        new_theme = request.form.get('theme', '').strip()
        if new_theme in {'light', 'dark', 'auto'}:
            current_user.theme = new_theme
            session['theme'] = new_theme
        
        db.session.commit()
        flash('Settings saved successfully!', 'success')
    except Exception as exc:
        current_app.logger.error(f"Failed to update settings for user {current_user.id}: {exc}", exc_info=True)
        db.session.rollback()
        flash('Failed to save settings. Please try again.', 'error')
    
    return redirect(url_for('profile.settings', lang=updated_lang))

@profile_bp.route('/security')
@login_required
def security(lang):
    """Profile security page"""
    return render_template('profile/security.html', user=current_user)

@profile_bp.route('/statistics')
@login_required
def statistics(lang):
    """Profile statistics page"""
    return render_template('profile/statistics.html', user=current_user)