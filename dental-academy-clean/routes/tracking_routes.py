#!/usr/bin/env python3
"""
Роуты для отслеживания посетителей регистрации
"""

from flask import Blueprint, request, jsonify, current_app
from extensions import db
from models import RegistrationVisitor
from utils.visitor_tracker import VisitorTracker
from functools import wraps

# Создаем Blueprint для отслеживания
tracking_bp = Blueprint('tracking', __name__, url_prefix='/track')

def require_csrf_token(f):
    """Декоратор для проверки CSRF токена"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            token = request.headers.get('X-CSRFToken') or request.form.get('csrf_token')
            if not token:
                return jsonify({'error': 'CSRF token required'}), 400
        return f(*args, **kwargs)
    return decorated_function

@tracking_bp.route('/registration-visit', methods=['POST'])
@require_csrf_token
def track_registration_visit():
    """Отслеживает посещение страницы регистрации"""
    try:
        data = request.get_json()
        page_type = data.get('page_type', 'unknown')
        language = data.get('language', 'en')
        
        success = VisitorTracker.track_page_visit(page_type, language)
        
        if success:
            return jsonify({'success': True, 'message': 'Visit tracked'})
        else:
            return jsonify({'success': False, 'error': 'Failed to track visit'}), 500
            
    except Exception as e:
        current_app.logger.error(f"Error in track_registration_visit: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@tracking_bp.route('/email-entry', methods=['POST'])
@require_csrf_token
def track_email_entry():
    """Отслеживает ввод email адреса"""
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        page_type = data.get('page_type', 'unknown')
        
        if not email or '@' not in email:
            return jsonify({'success': False, 'error': 'Invalid email'}), 400
        
        success = VisitorTracker.track_email_entry(email, page_type)
        
        if success:
            return jsonify({'success': True, 'message': 'Email entry tracked'})
        else:
            return jsonify({'success': False, 'error': 'Failed to track email entry'}), 500
            
    except Exception as e:
        current_app.logger.error(f"Error in track_email_entry: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@tracking_bp.route('/form-start', methods=['POST'])
@require_csrf_token
def track_form_start():
    """Отслеживает начало заполнения формы"""
    try:
        data = request.get_json()
        page_type = data.get('page_type', 'unknown')
        
        success = VisitorTracker.track_form_start(page_type)
        
        if success:
            return jsonify({'success': True, 'message': 'Form start tracked'})
        else:
            return jsonify({'success': False, 'error': 'Failed to track form start'}), 500
            
    except Exception as e:
        current_app.logger.error(f"Error in track_form_start: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@tracking_bp.route('/form-submit', methods=['POST'])
@require_csrf_token
def track_form_submit():
    """Отслеживает отправку формы"""
    try:
        data = request.get_json()
        page_type = data.get('page_type', 'unknown')
        
        # Предполагаем, что форма будет успешно отправлена
        # Если регистрация не удастся, это будет обработано отдельно
        success = VisitorTracker.track_form_start(page_type)  # Отмечаем как начало формы
        
        if success:
            return jsonify({'success': True, 'message': 'Form submit tracked'})
        else:
            return jsonify({'success': False, 'error': 'Failed to track form submit'}), 500
            
    except Exception as e:
        current_app.logger.error(f"Error in track_form_submit: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@tracking_bp.route('/form-abandonment', methods=['POST'])
@require_csrf_token
def track_form_abandonment():
    """Отслеживает отказ от заполнения формы"""
    try:
        data = request.get_json()
        page_type = data.get('page_type', 'unknown')
        
        success = VisitorTracker.track_form_abandonment(page_type)
        
        if success:
            return jsonify({'success': True, 'message': 'Form abandonment tracked'})
        else:
            return jsonify({'success': False, 'error': 'Failed to track form abandonment'}), 500
            
    except Exception as e:
        current_app.logger.error(f"Error in track_form_abandonment: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@tracking_bp.route('/page-exit', methods=['POST'])
@require_csrf_token
def track_page_exit():
    """Отслеживает выход со страницы"""
    try:
        data = request.get_json()
        page_type = data.get('page_type', 'unknown')
        time_on_page = data.get('time_on_page', 0)
        
        success = VisitorTracker.track_page_exit(page_type)
        
        if success:
            return jsonify({'success': True, 'message': 'Page exit tracked'})
        else:
            return jsonify({'success': False, 'error': 'Failed to track page exit'}), 500
            
    except Exception as e:
        current_app.logger.error(f"Error in track_page_exit: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@tracking_bp.route('/registration-completion', methods=['POST'])
@require_csrf_token
def track_registration_completion():
    """Отслеживает успешную регистрацию"""
    try:
        data = request.get_json()
        page_type = data.get('page_type', 'unknown')
        user_id = data.get('user_id', None)
        
        success = VisitorTracker.track_registration_completion(page_type, user_id)
        
        if success:
            return jsonify({'success': True, 'message': 'Registration completion tracked'})
        else:
            return jsonify({'success': False, 'error': 'Failed to track registration completion'}), 500
            
    except Exception as e:
        current_app.logger.error(f"Error in track_registration_completion: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
