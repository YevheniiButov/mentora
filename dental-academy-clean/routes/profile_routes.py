# profile_routes.py - Profile management routes
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app, g, session
from flask_login import login_required, current_user
from models import User
from extensions import db

# Create blueprint
profile_bp = Blueprint('profile', __name__)

@profile_bp.before_request
def before_request():
    """Set language from URL parameter or session"""
    try:
        lang = request.args.get('lang', 'en')
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
def profile():
    """Profile page"""
    try:
        current_app.logger.info(f"Profile page accessed by user: {current_user.id}")
        return render_template('profile/index.html', user=current_user)
    except Exception as e:
        current_app.logger.error(f"Error in profile route: {e}", exc_info=True)
        flash('Произошла ошибка при загрузке профиля', 'error')
        return redirect(url_for('index'))

@profile_bp.route('/personal_info')
@login_required
def personal_info():
    """Personal information page"""
    lang = g.get('lang', 'en')
    return render_template('profile/personal_info.html', user=current_user, lang=lang)

@profile_bp.route('/personal_info', methods=['POST'])
@login_required
def update_personal_info():
    """Update personal information"""
    try:
        lang = g.get('lang', 'en')
        
        # Get form data
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        
        # Update user data
        if first_name:
            current_user.first_name = first_name
        if last_name:
            current_user.last_name = last_name
        if email and email != current_user.email:
            current_user.email = email
        if phone:
            current_user.phone = phone
            
        db.session.commit()
        flash('Personal information updated successfully!', 'success')
        
    except Exception as e:
        current_app.logger.error(f"Error updating personal info: {e}", exc_info=True)
        db.session.rollback()
        flash('Error updating personal information', 'error')
    
    return redirect(url_for('profile.personal_info', lang=lang))

@profile_bp.route('/settings')
@login_required
def settings():
    """Profile settings page"""
    return render_template('profile/settings.html', user=current_user)

@profile_bp.route('/security')
@login_required
def security():
    """Profile security page"""
    return render_template('profile/security.html', user=current_user)

@profile_bp.route('/statistics')
@login_required
def statistics():
    """Profile statistics page"""
    return render_template('profile/statistics.html', user=current_user)