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
    lang = request.args.get('lang', 'en')
    if lang in ['en', 'ru', 'nl', 'es', 'pt', 'tr', 'uk', 'fa']:
        g.lang = lang
        session['lang'] = lang
    else:
        g.lang = session.get('lang', 'en')

@profile_bp.route('/')
@login_required
def profile():
    """Profile page"""
    return render_template('profile/index.html', user=current_user)

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