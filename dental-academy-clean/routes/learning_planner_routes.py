from flask import Blueprint, render_template, request, jsonify, make_response
from flask_login import login_required, current_user
from models import DiagnosticSession, PersonalLearningPlan
from utils.serializers import clean_for_template
from translations import get_translation
from utils.domain_mapping import ALL_BIG_DOMAINS, OLD_TO_NEW_DOMAIN_MAPPING, get_domain_name
from utils.diagnostic_data_manager import DiagnosticDataManager
import json

learning_planner_bp = Blueprint('learning_planner', __name__)

@learning_planner_bp.route('/learning-planner/<int:plan_id>')
@login_required
def learning_planner(plan_id):
    """Enhanced learning planner with calendar and charts"""
    
    print(f"🔍 ОТЛАДКА: learning_planner вызван")
    print(f"🔍 ОТЛАДКА: current_user.id = {current_user.id}")
    
    # Get current language
    lang = request.args.get('lang', 'en')
    
    # Используем общий менеджер данных для получения унифицированной информации
    diagnostic_results = DiagnosticDataManager.get_user_diagnostic_data(current_user.id)
    learning_plan_data = DiagnosticDataManager.get_learning_plan_data(current_user.id)
    
    print(f"🔍 ОТЛАДКА: diagnostic_results = {diagnostic_results}")
    print(f"🔍 ОТЛАДКА: learning_plan_data = {learning_plan_data}")
    
    # Переводим названия доменов
    for domain in diagnostic_results.get('domains', []):
        translated_name = get_translation(domain['code'], lang)
        if translated_name == domain['code']:
            translated_name = domain['name']
        domain['name'] = translated_name
    
    response = make_response(render_template('dashboard/learning_planner_translated.html',
                         diagnostic_results=clean_for_template(diagnostic_results),
                         learning_plan_data=clean_for_template(learning_plan_data)))
    
    # Add headers to prevent caching
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    
    return response 