from flask import Blueprint, jsonify, make_response, current_app
from flask_login import current_user, login_required
from models import PersonalLearningPlan

export_bp = Blueprint('export', __name__)

@export_bp.route('/export-plan/<int:plan_id>/ical')
# @login_required  # Временно отключено для тестирования
def export_plan_ical(plan_id):
    """Экспорт плана обучения в формате iCal"""
    
    # Проверяем, авторизован ли пользователь
    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from utils.export_system import exporter
        
        # Экспортируем в iCal
        ical_content = exporter.export_to_ical(plan_id, current_user.id)
        
        if not ical_content:
            return jsonify({'error': 'Plan not found or export failed'}), 404
        
        # Создаем ответ с iCal файлом
        response = make_response(ical_content)
        response.headers['Content-Type'] = 'text/calendar; charset=utf-8'
        response.headers['Content-Disposition'] = f'attachment; filename=learning_plan_{plan_id}.ics'
        
        return response
        
    except Exception as e:
        current_app.logger.error(f"Error exporting plan to iCal: {e}")
        return jsonify({'error': 'Export failed'}), 500

@export_bp.route('/export-plan/<int:plan_id>/pdf')
# @login_required  # Временно отключено для тестирования
def export_plan_pdf(plan_id):
    """Экспорт плана обучения в формате PDF"""
    
    # Проверяем, авторизован ли пользователь
    if not current_user.is_authenticated:
        return jsonify({'error': 'Unauthorized'}), 401
    
    try:
        from utils.export_system import exporter
        
        # Экспортируем в PDF
        pdf_content = exporter.export_to_pdf(plan_id, current_user.id)
        
        if not pdf_content:
            return jsonify({'error': 'Plan not found or export failed'}), 404
        
        # Создаем ответ с PDF файлом
        response = make_response(pdf_content)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=learning_plan_{plan_id}.pdf'
        
        return response
        
    except Exception as e:
        current_app.logger.error(f"Error exporting plan to PDF: {e}")
        return jsonify({'error': 'Export failed'}), 500 