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
        if medical_specialization:
            current_user.medical_specialization = medical_specialization
        if additional_education_info:
            current_user.additional_education_info = additional_education_info
        if work_experience:
            current_user.work_experience = work_experience
        if additional_qualifications:
            current_user.additional_qualifications = additional_qualifications
            
        # Check if profile is complete and mark registration as completed
        if not current_user.registration_completed:
            # Check if essential fields are filled
            essential_fields = [
                current_user.first_name,
                current_user.last_name,
                current_user.profession,
                current_user.legal_status
            ]
            
            if all(essential_fields):
                current_user.registration_completed = True
                current_app.logger.info(f"Registration completed for user: {current_user.email}")
            
        db.session.commit()
        
        # Check if this was a forced completion
        if request.form.get('force_completion') == 'true':
            flash('Profile completed successfully! Welcome to Mentora!', 'success')
            return redirect(url_for('main.index', lang=lang))
        else:
            flash('Personal information updated successfully!', 'success')
        
    except Exception as e:
        current_app.logger.error(f"Error updating personal info: {e}", exc_info=True)
        db.session.rollback()
        flash('Error updating personal information', 'error')
    
    return redirect(url_for('profile.personal_info', lang=lang))

@profile_bp.route('/settings')
@login_required
def settings(lang):
    """Profile settings page"""
    return render_template('profile/settings.html', user=current_user)

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