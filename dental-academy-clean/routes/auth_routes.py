from flask import Blueprint, render_template, request, redirect, url_for, flash, session, g, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from models import User
from extensions import db
from utils.email_service import send_password_reset_email, send_email_confirmation
import os
from datetime import datetime, timezone

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    lang = g.get('lang', 'en')
    if current_user.is_authenticated:
        return redirect(url_for('main.index', lang=lang))
        
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            remember = data.get('remember', False)
        else:
            email = request.form.get('email')
            password = request.form.get('password')
            remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            error_msg = 'Please check your login details and try again.'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg}), 401
            flash(error_msg, 'error')
            return redirect(url_for('auth.login', lang=lang))
            
        if not user.email_confirmed:
            error_msg = 'Please confirm your email address before logging in.'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg, 'unconfirmed': True}), 403
            flash(error_msg, 'warning')
            return redirect(url_for('auth.login', lang=lang))
            
        login_user(user, remember=remember)
        user.last_login = datetime.now(timezone.utc)
        db.session.commit()
        
        if request.is_json:
            next_page = request.args.get('next') or url_for('main.index', lang=lang)
            return jsonify({'success': True, 'redirect_url': next_page})
            
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('main.index', lang=lang))
        
    return render_template('auth/login.html', lang=lang)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    lang = g.get('lang', 'en')
    if current_user.is_authenticated:
        return redirect(url_for('main.index', lang=lang))
    return render_template('auth/register.html', lang=lang)

@auth_bp.route('/quick-register')
def quick_register():
    return render_template('auth/quick_register.html', lang=g.get('lang', 'en'))

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index', lang=g.get('lang', 'en')))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    lang = g.get('lang', 'en')
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            email = data.get('email')
        else:
            email = request.form.get('email')
            
        user = User.query.filter_by(email=email).first()
        
        if user:
            token = user.generate_password_reset_token()
            db.session.commit()
            send_password_reset_email(user, token)
            
        message = 'If an account exists with that email, we have sent password reset instructions.'
        if request.is_json:
            return jsonify({'success': True, 'message': message})
            
        flash(message, 'info')
        return redirect(url_for('auth.login', lang=lang))
        
    return render_template('auth/forgot_password.html', lang=lang)

@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    lang = g.get('lang', 'en')
    # Using list comprehension or filter to find user with matching token
    all_users = User.query.filter(User.password_reset_token.isnot(None)).all()
    target_user = None
    for u in all_users:
        if u.verify_password_reset_token(token):
            target_user = u
            break
            
    if not target_user:
        flash('The reset link is invalid or has expired.', 'error')
        return redirect(url_for('auth.forgot_password', lang=lang))
        
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            password = data.get('password')
        else:
            password = request.form.get('password')
            
        target_user.set_password(password)
        target_user.clear_password_reset_token()
        db.session.commit()
        
        message = 'Your password has been reset.'
        if request.is_json:
            return jsonify({
                'success': True, 
                'message': message,
                'redirect_url': url_for('auth.login', lang=lang)
            })
            
        flash(message, 'success')
        return redirect(url_for('auth.login', lang=lang))
        
    return render_template('auth/reset_password.html', lang=lang, token=token)

@auth_bp.route('/confirm-email/<token>')
def confirm_email(token):
    lang = g.get('lang', 'en')
    all_users = User.query.filter(User.email_confirmation_token.isnot(None)).all()
    target_user = None
    for u in all_users:
        if u.verify_email_confirmation_token(token):
            target_user = u
            break
            
    if not target_user:
        flash('The confirmation link is invalid or has expired.', 'error')
        return redirect(url_for('auth.login', lang=lang))
        
    target_user.confirm_email()
    db.session.commit()
    flash('Your email has been confirmed!', 'success')
    return redirect(url_for('auth.login', lang=lang))

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    lang = g.get('lang', 'en')
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            current_password = data.get('current_password')
            new_password = data.get('new_password')
        else:
            current_password = request.form.get('current_password')
            new_password = request.form.get('new_password')
            
        if not current_user.check_password(current_password):
            error_msg = 'Current password is incorrect.'
            if request.is_json:
                return jsonify({'success': False, 'error': error_msg}), 401
            flash(error_msg, 'error')
            return redirect(url_for('auth.change_password', lang=lang))
            
        current_user.set_password(new_password)
        db.session.commit()
        
        message = 'Your password has been changed successfully!'
        if request.is_json:
            return jsonify({'success': True, 'message': message})
            
        flash(message, 'success')
        return redirect(url_for('auth.profile', lang=lang))
        
    return render_template('auth/change_password.html', lang=lang)

@auth_bp.route('/resend-confirmation', methods=['GET', 'POST'])
def resend_confirmation():
    lang = g.get('lang', 'en')
    if request.method == 'POST':
        if request.is_json:
            data = request.get_json()
            email = data.get('email')
        else:
            email = request.form.get('email')
            
        user = User.query.filter_by(email=email).first()
        
        if user and not user.email_confirmed:
            token = user.generate_email_confirmation_token()
            db.session.commit()
            send_email_confirmation(user, token)
            
        message = 'If the account is not yet confirmed, a new confirmation email has been sent.'
        if request.is_json:
            return jsonify({'success': True, 'message': message})
            
        flash(message, 'info')
        return redirect(url_for('auth.login', lang=lang))
        
    return render_template('auth/resend_confirmation.html', lang=lang)

# DigiD Routes
@auth_bp.route('/digid/login')
def digid_login():
    lang = g.get('lang', 'en')
    return render_template('digid/login.html', lang=lang)

@auth_bp.route('/digid/callback')
def digid_callback():
    # DigiD callback logic stub
    pass

@auth_bp.route('/digid/logout')
def digid_logout():
    logout_user()
    return redirect(url_for('main.index', lang=g.get('lang', 'en')))
