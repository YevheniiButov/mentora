# routes/virtual_patient_routes.py
"""
Роуты для системы виртуальных пациентов
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import login_required, current_user
from models import db, VirtualPatientScenario, VirtualPatientAttempt, User
from datetime import datetime
import json

virtual_patient_bp = Blueprint('virtual_patient', __name__)

@virtual_patient_bp.route('/virtual-patients')
@login_required
def list_scenarios():
    """Список всех доступных виртуальных пациентов"""
    scenarios = VirtualPatientScenario.query.filter_by(is_published=True).order_by(VirtualPatientScenario.title).all()
    
    # Получаем прогресс пользователя для каждого сценария
    scenarios_with_progress = []
    for scenario in scenarios:
        # Найдем лучшую попытку пользователя
        best_attempt = VirtualPatientAttempt.query.filter_by(
            user_id=current_user.id,
            scenario_id=scenario.id,
            completed=True
        ).order_by(VirtualPatientAttempt.score.desc()).first()
        
        # Подсчитаем количество попыток
        attempts_count = VirtualPatientAttempt.query.filter_by(
            user_id=current_user.id,
            scenario_id=scenario.id
        ).count()
        
        scenarios_with_progress.append({
            'scenario': scenario,
            'best_score': best_attempt.score if best_attempt else 0,
            'best_percentage': best_attempt.percentage_score if best_attempt else 0,
            'attempts_count': attempts_count,
            'completed': best_attempt is not None
        })
    
    return render_template('virtual_patient/scenarios_list.html', scenarios=scenarios_with_progress)

@virtual_patient_bp.route('/virtual-patients/<int:scenario_id>')
@login_required
def scenario_detail(scenario_id):
    """Детальная информация о сценарии"""
    scenario = VirtualPatientScenario.query.get_or_404(scenario_id)
    
    # Получаем попытки пользователя для этого сценария
    attempts = VirtualPatientAttempt.query.filter_by(
        user_id=current_user.id,
        scenario_id=scenario_id
    ).order_by(VirtualPatientAttempt.started_at.desc()).all()
    
    return render_template('virtual_patient/scenario_detail.html', scenario=scenario, attempts=attempts)

@virtual_patient_bp.route('/virtual-patients/<int:scenario_id>/start', methods=['POST'])
@login_required
def start_scenario(scenario_id):
    """Начать новый сценарий"""
    scenario = VirtualPatientScenario.query.get_or_404(scenario_id)
    
    # Создаем новую попытку
    attempt = VirtualPatientAttempt(
        user_id=current_user.id,
        scenario_id=scenario_id,
        max_score=scenario.max_score,
        started_at=datetime.now(timezone.utc)
    )
    
    db.session.add(attempt)
    db.session.commit()
    
    return redirect(url_for('virtual_patient.play_scenario', attempt_id=attempt.id))

@virtual_patient_bp.route('/virtual-patients/play/<int:attempt_id>')
@login_required
def play_scenario(attempt_id):
    """Интерфейс для прохождения сценария"""
    attempt = VirtualPatientAttempt.query.get_or_404(attempt_id)
    
    # Проверяем, что попытка принадлежит текущему пользователю
    if attempt.user_id != current_user.id:
        flash('У вас нет доступа к этому сценарию', 'error')
        return redirect(url_for('virtual_patient.list_scenarios'))
    
    # Проверяем, не завершен ли сценарий
    if attempt.completed:
        return redirect(url_for('virtual_patient.scenario_results', attempt_id=attempt_id))
    
    scenario = attempt.scenario
    scenario_data = scenario.localized_data
    
    return render_template('virtual_patient/play_scenario.html', 
                         attempt=attempt, 
                         scenario=scenario, 
                         scenario_data=scenario_data)

@virtual_patient_bp.route('/virtual-patients/api/make-choice', methods=['POST'])
@login_required
def make_choice():
    """API для выбора варианта действий в сценарии"""
    data = request.json
    attempt_id = data.get('attempt_id')
    choice_id = data.get('choice_id')
    node_id = data.get('node_id')
    
    attempt = VirtualPatientAttempt.query.get_or_404(attempt_id)
    
    # Проверяем доступ
    if attempt.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    # Получаем данные сценария
    scenario_data = attempt.scenario.localized_data
    
    # Находим текущий узел
    current_node = None
    for node in scenario_data.get('dialogue_nodes', []):
        if node.get('id') == node_id:
            current_node = node
            break
    
    if not current_node:
        return jsonify({'error': 'Node not found'}), 404
    
    # Находим выбранный вариант
    selected_option = None
    for option in current_node.get('options', []):
        if option.get('id') == choice_id:
            selected_option = option
            break
    
    if not selected_option:
        return jsonify({'error': 'Option not found'}), 404
    
    # Добавляем баллы
    score_change = selected_option.get('score', 0)
    attempt.score += score_change
    
    # Обновляем историю диалога
    dialogue_history = json.loads(attempt.dialogue_history) if attempt.dialogue_history else []
    dialogue_history.append({
        'node_id': node_id,
        'choice_id': choice_id,
        'score_change': score_change,
        'timestamp': datetime.now(timezone.utc).isoformat()
    })
    attempt.dialogue_history = json.dumps(dialogue_history)
    
    # Переходим к следующему узлу
    next_node_id = selected_option.get('next_node')
    next_node = None
    is_final = False
    
    if next_node_id:
        for node in scenario_data.get('dialogue_nodes', []):
            if node.get('id') == next_node_id:
                next_node = node
                break
        
        if next_node and next_node.get('is_final', False):
            is_final = True
    
    # Если сценарий завершен
    if is_final or not next_node:
        attempt.completed = True
        attempt.completed_at = datetime.now(timezone.utc)
        
        # Рассчитываем время прохождения
        if attempt.started_at:
            time_diff = attempt.completed_at - attempt.started_at
            attempt.time_spent = time_diff.total_seconds() / 60.0  # в минутах
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'score_change': score_change,
        'total_score': attempt.score,
        'next_node': next_node,
        'is_final': is_final,
        'completed': attempt.completed
    })

@virtual_patient_bp.route('/virtual-patients/results/<int:attempt_id>')
@login_required
def scenario_results(attempt_id):
    """Результаты прохождения сценария"""
    attempt = VirtualPatientAttempt.query.get_or_404(attempt_id)
    
    # Проверяем доступ
    if attempt.user_id != current_user.id:
        flash('У вас нет доступа к этим результатам', 'error')
        return redirect(url_for('virtual_patient.list_scenarios'))
    
    # Определяем результат
    percentage = attempt.percentage_score
    scenario_data = attempt.scenario.localized_data
    outcomes = scenario_data.get('outcomes', {})
    
    if percentage >= 80:
        result_type = 'good'
    elif percentage >= 60:
        result_type = 'average'
    else:
        result_type = 'poor'
    
    outcome = outcomes.get(result_type, {
        'title': 'Сценарий завершен',
        'text': f'Вы набрали {attempt.score} из {attempt.max_score} баллов'
    })
    
    return render_template('virtual_patient/results.html', 
                         attempt=attempt, 
                         outcome=outcome, 
                         result_type=result_type)

@virtual_patient_bp.route('/virtual-patients/api/scenarios', methods=['GET'])
@login_required
def api_scenarios():
    """API для получения списка сценариев"""
    scenarios = VirtualPatientScenario.query.filter_by(is_published=True).all()
    
    scenarios_data = []
    for scenario in scenarios:
        scenario_info = {
            'id': scenario.id,
            'title': scenario.title,
            'description': scenario.description,
            'difficulty': scenario.difficulty,
            'category': scenario.category,
            'max_score': scenario.max_score,
            'is_premium': scenario.is_premium
        }
        scenarios_data.append(scenario_info)
    
    return jsonify(scenarios_data)

@virtual_patient_bp.route('/virtual-patients/check', methods=['GET'])
@login_required
def check_vp_count():
    """Публичный эндпоинт для проверки количества виртуальных пациентов (без админ прав)"""
    try:
        from sqlalchemy import func
        
        total_count = VirtualPatientScenario.query.count()
        published_count = VirtualPatientScenario.query.filter_by(is_published=True).count()
        
        # Группировка по специальности
        specialty_counts = db.session.query(
            VirtualPatientScenario.specialty,
            func.count(VirtualPatientScenario.id).label('count')
        ).group_by(VirtualPatientScenario.specialty).all()
        
        scenarios_list = VirtualPatientScenario.query.order_by(VirtualPatientScenario.id).all()
        
        scenarios_data = []
        for scenario in scenarios_list:
            scenarios_data.append({
                'id': scenario.id,
                'title': scenario.title,
                'specialty': scenario.specialty,
                'difficulty': scenario.difficulty,
                'is_published': scenario.is_published
            })
        
        return jsonify({
            'success': True,
            'total_count': total_count,
            'published_count': published_count,
            'unpublished_count': total_count - published_count,
            'by_specialty': {specialty: count for specialty, count in specialty_counts},
            'scenarios': scenarios_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Блокировка через CSS overlay - убрано для использования JavaScript overlay 