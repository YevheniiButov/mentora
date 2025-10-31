from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from models import (
    UserLearningProgress, VirtualPatientScenario, VirtualPatientAttempt
)
from utils.virtual_patient_utils import VirtualPatientSelector

daily_flow_bp = Blueprint('daily_flow', __name__, url_prefix='/learning-map')

@daily_flow_bp.route('/daily-session-flow')
@login_required
def daily_session_flow():
    """
    Главная страница для Daily Learning Flow:
    1. 20 Medical Tests
    2. 10 Dutch Terms
    3. 1 Virtual Patient
    """
    # Check if profile is complete
    from utils.profile_check import check_profile_complete
    from flask import redirect, url_for, session
    
    profile_check = check_profile_complete(current_user)
    if not profile_check['is_complete']:
        lang = session.get('lang', 'nl')
        return redirect(url_for('learning_map_bp.complete_profile', lang=lang))
    
    try:
        # Загрузить today's VP
        vp_result = VirtualPatientSelector.get_daily_scenario(current_user)
        
        return render_template(
            'learning/daily_session_flow.html',
            vp_available=vp_result['available'],
            vp_scenario=vp_result['scenario'],
            vp_message=vp_result['message']
        )
    except Exception as e:
        return render_template(
            'learning/daily_session_flow.html',
            vp_available=False,
            vp_message=f'Error: {str(e)}'
        ), 500

@daily_flow_bp.route('/daily-session-flow/status')
@login_required
def daily_session_flow_status():
    """
    Получить статус текущей daily session:
    - сколько тестов пройдено
    - сколько слов выучено
    - доступен ли VP
    """
    try:
        # TODO: Implement logic to check today's progress
        # For now, return basic structure
        
        return jsonify({
            'success': True,
            'tests': {
                'completed': 0,
                'total': 20,
                'status': 'pending'  # pending, in_progress, completed
            },
            'terms': {
                'completed': 0,
                'total': 10,
                'status': 'pending'
            },
            'virtual_patient': {
                'completed': 0,
                'available': True,
                'status': 'pending'
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@daily_flow_bp.route('/daily-session/dialogue/<int:attempt_id>')
@login_required
def virtual_patient_dialogue(attempt_id):
    """
    Загрузить страницу диалога с виртуальным пациентом
    """
    try:
        attempt = VirtualPatientAttempt.query.get(attempt_id)
        
        if not attempt or attempt.user_id != current_user.id:
            return 'Not found', 404
        
        if attempt.completed:
            return 'This attempt is already completed', 400
        
        return render_template(
            'virtual_patient_dialogue.html',
            scenario_id=attempt.scenario_id,
            attempt_id=attempt_id
        )
    except Exception as e:
        return f'Error: {str(e)}', 500

@daily_flow_bp.route('/daily-session/complete')
@login_required
def daily_session_complete():
    """
    Страница завершения daily session с результатами
    """
    try:
        # TODO: Get today's session results
        return render_template('learning/daily_session_complete.html')
    except Exception as e:
        return f'Error: {str(e)}', 500
