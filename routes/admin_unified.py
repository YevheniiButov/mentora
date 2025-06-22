# routes/admin_unified.py

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from models import *
from extensions import db
import os
from werkzeug.utils import secure_filename

admin_unified_bp = Blueprint('admin_simple', __name__, url_prefix='/admin')

@admin_unified_bp.before_request
@login_required
def require_admin():
    if not current_user.is_admin:
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('main_bp.index'))

@admin_unified_bp.route('/')
@admin_unified_bp.route('/dashboard')
def dashboard():
    stats = {
        'total_users': User.query.count(),
        'total_modules': Module.query.count(),
        'total_lessons': Lesson.query.count(),
        'total_questions': Question.query.count() if hasattr(globals(), 'Question') else 0
    }
    return render_template('admin/dashboard_unified.html', stats=stats)

@admin_unified_bp.route('/content-manager')
def content_manager():
    learning_paths = LearningPath.query.all()
    return render_template('admin/content_manager.html', learning_paths=learning_paths)

@admin_unified_bp.route('/api/learning-paths')
def api_learning_paths():
    paths = LearningPath.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'subjects': [{
            'id': s.id,
            'name': s.name,
            'modules_count': len(s.modules) if hasattr(s, 'modules') else 0
        } for s in p.subjects] if hasattr(p, 'subjects') else []
    } for p in paths])

@admin_unified_bp.route('/users')
def users_manager():
    users = User.query.all()
    return render_template('admin/users_manager.html', users=users)

@admin_unified_bp.route('/modules')
def modules_manager():
    modules = Module.query.all()
    return render_template('admin/modules_manager.html', modules=modules)

@admin_unified_bp.route('/analytics')
def analytics():
    return render_template('admin/analytics.html')

@admin_unified_bp.route('/settings')
def settings():
    return render_template('admin/settings.html') 