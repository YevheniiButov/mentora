#!/usr/bin/env python3
"""
Маршруты для виртуальных пациентов в ежедневных сессиях
"""

from flask import Blueprint, request, jsonify, render_template, session
from flask_login import login_required, current_user
from utils.virtual_patient_utils import (
    VirtualPatientSelector, 
    VirtualPatientSessionManager,
    VirtualPatientDailyIntegration
)
from extensions import db, csrf
from models import VirtualPatientScenario, VirtualPatientAttempt
from datetime import datetime
import json

vp_daily_bp = Blueprint('vp_daily', __name__, url_prefix='/api/vp')


@vp_daily_bp.route('/daily-scenario', methods=['GET'])
@login_required
def get_daily_scenario():
    """
    Получить сценарий виртуального пациента для ежедневной сессии
    """
    try:
        scenario = VirtualPatientSelector.get_daily_scenario(current_user)
        
        if not scenario:
            return jsonify({
                'success': False,
                'message': 'No virtual patient scenarios available for your specialty'
            }), 200  # Возвращаем 200, а не 404 - роут найден, просто данных нет
        
        return jsonify({
            'success': True,
            'scenario': {
                'id': scenario.id,
                'title': scenario.title,
                'description': scenario.description,
                'difficulty': scenario.difficulty,
                'max_score': scenario.max_score,
                'keywords': scenario.keywords_list,
                'scenario_data': scenario.localized_data
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@vp_daily_bp.route('/start-attempt', methods=['POST'])
@csrf.exempt
@login_required
def start_attempt():
    """
    Начать попытку прохождения сценария
    """
    try:
        data = request.get_json()
        scenario_id = data.get('scenario_id')
        
        print(f"Start attempt request: scenario_id={scenario_id}, user_id={current_user.id}")
        
        if not scenario_id:
            print("No scenario ID provided")
            return jsonify({
                'success': False,
                'message': 'Scenario ID is required'
            }), 400
        
        attempt = VirtualPatientSessionManager.start_attempt(current_user, scenario_id)
        
        print(f"Start attempt result: attempt={attempt}")
        
        if not attempt:
            return jsonify({
                'success': False,
                'message': 'Failed to start attempt or scenario not available'
            }), 400
        
        return jsonify({
            'success': True,
            'attempt_id': attempt.id,
            'scenario_id': attempt.scenario_id,
            'max_score': attempt.max_score
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@vp_daily_bp.route('/save-choice', methods=['POST'])
@csrf.exempt
@login_required
def save_choice():
    """
    Сохранить выбор пользователя в диалоге
    """
    try:
        data = request.get_json()
        print(f"Received save-choice data: {data}")
        
        attempt_id = data.get('attempt_id')
        option_id = data.get('option_id')
        score = data.get('score', 0)
        next_node = data.get('next_node')
        dialogue_history = data.get('dialogue_history', [])
        
        print(f"Parsed data: attempt_id={attempt_id}, option_id={option_id}, score={score}")
        
        if not attempt_id or not option_id:
            print(f"Missing parameters: attempt_id={attempt_id}, option_id={option_id}")
            return jsonify({
                'success': False,
                'message': 'Missing required parameters'
            }), 400
        
        # Получить попытку
        attempt = VirtualPatientAttempt.query.get(attempt_id)
        if not attempt:
            return jsonify({
                'success': False,
                'message': 'Attempt not found'
            }), 404
        
        # Проверить доступ
        if attempt.user_id != current_user.id:
            return jsonify({
                'success': False,
                'message': 'Access denied'
            }), 403
        
        # Обновить счет
        attempt.score += score
        
        # Обновить историю диалога
        if dialogue_history:
            attempt.dialogue_history = json.dumps(dialogue_history)
        
        # Сохранить изменения
        db.session.commit()
        
        return jsonify({
            'success': True,
            'current_score': attempt.score,
            'fill_in_score': 0,  # Пока не используется
            'next_node': next_node
        })
        
    except Exception as e:
        print(f"Error in save_choice: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500


@vp_daily_bp.route('/validate-fill-in', methods=['POST'])
@csrf.exempt
@login_required
def validate_fill_in():
    """
    Валидировать ответ на вопрос с заполнением пропусков
    """
    try:
        data = request.get_json()
        attempt_id = data.get('attempt_id')
        node_id = data.get('node_id')
        user_answer = data.get('user_answer', '').strip()
        
        if not attempt_id or not node_id or not user_answer:
            return jsonify({
                'success': False,
                'valid': False,
                'message': 'Missing required fields'
            }), 400
        
        # Получить попытку
        attempt = VirtualPatientAttempt.query.get(attempt_id)
        if not attempt:
            return jsonify({
                'success': False,
                'valid': False,
                'message': 'Attempt not found'
            }), 404
        
        # Проверить доступ
        if attempt.user_id != current_user.id:
            return jsonify({
                'success': False,
                'valid': False,
                'message': 'Access denied'
            }), 403
        
        # Получить сценарий
        scenario = VirtualPatientScenario.query.get(attempt.scenario_id)
        if not scenario:
            return jsonify({
                'success': False,
                'valid': False,
                'message': 'Scenario not found'
            }), 404
        
        # Получить данные сценария
        scenario_data = scenario.localized_data
        dialogue_nodes = scenario_data.get('dialogue_nodes', [])
        
        # Найти узел
        node = next((n for n in dialogue_nodes if n.get('id') == node_id), None)
        if not node or not node.get('fill_in'):
            return jsonify({
                'success': False,
                'valid': False,
                'message': 'Node or fill-in config not found'
            }), 404
        
        fill_in_config = node['fill_in']
        correct_word = fill_in_config.get('word', '').strip().lower()
        user_answer_lower = user_answer.lower()
        
        # Проверяем совпадение (case-insensitive, допускаем частичное совпадение)
        is_correct = False
        score = 0
        
        if correct_word:
            # Точное совпадение
            if user_answer_lower == correct_word:
                is_correct = True
                score = 10  # Базовый балл за правильный ответ
            # Частичное совпадение (если пользователь ввел часть слова)
            elif correct_word in user_answer_lower or user_answer_lower in correct_word:
                is_correct = True
                score = 5  # Меньший балл за частичное совпадение
        
        # Обновить счет попытки
        if is_correct:
            attempt.score += score
            db.session.commit()
        
        # Сообщение для пользователя
        if is_correct:
            message = 'Correct! Goed gedaan!' if score == 10 else f'Bijna correct! Het juiste antwoord is: {correct_word}'
        else:
            hint = fill_in_config.get('hint', '')
            if hint:
                message = f'Niet helemaal correct. Hint: {hint}'
            else:
                message = f'Niet correct. Probeer het opnieuw. Het juiste antwoord is: {correct_word}'
        
        return jsonify({
            'success': True,
            'valid': is_correct,
            'score': score,
            'message': message,
            'correct_answer': correct_word if not is_correct else None
        })
        
    except Exception as e:
        print(f"Error in validate_fill_in: {e}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({
            'success': False,
            'valid': False,
            'message': str(e)
        }), 500


@vp_daily_bp.route('/complete-attempt', methods=['POST'])
@csrf.exempt
@login_required
def complete_attempt():
    """
    Завершить попытку прохождения
    """
    try:
        data = request.get_json()
        attempt_id = data.get('attempt_id')
        score = data.get('score', 0)
        time_spent = data.get('time_spent', 0)
        dialogue_history = data.get('dialogue_history', [])
        
        if not attempt_id:
            return jsonify({
                'success': False,
                'message': 'Attempt ID is required'
            }), 400
        
        success = VirtualPatientSessionManager.complete_attempt(
            attempt_id, score, time_spent, dialogue_history
        )
        
        if not success:
            return jsonify({
                'success': False,
                'message': 'Failed to complete attempt'
            }), 400
        
        # Получить обновленную попытку
        attempt = VirtualPatientAttempt.query.get(attempt_id)
        
        # Вычисляем процент
        percentage_score = 0
        if attempt.max_score and attempt.max_score > 0:
            percentage_score = round((attempt.score / attempt.max_score) * 100)
        elif attempt.max_score == 0:
            # Если max_score не установлен, используем 100 как базовый
            percentage_score = min(100, attempt.score)
        
        # Определяем уровень
        if percentage_score >= 85:
            level = 'excellent'
        elif percentage_score >= 70:
            level = 'good'
        elif percentage_score >= 50:
            level = 'needs_improvement'
        else:
            level = 'poor'
        
        return jsonify({
            'success': True,
            'message': 'Attempt completed successfully',
            'attempt': {
                'id': attempt.id,
                'score': attempt.score,
                'max_score': attempt.max_score,
                'percentage': percentage_score,
                'percentage_score': percentage_score,  # Добавляем для совместимости
                'level': level,
                'total_score': attempt.score,
                'fill_in_score': 0,
                'feedback': 'Uitstekend!' if percentage_score >= 85 else ('Goed gedaan!' if percentage_score >= 70 else 'Meer oefening nodig')
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@vp_daily_bp.route('/add-fill-in-answer', methods=['POST'])
@csrf.exempt
@login_required
def add_fill_in_answer():
    """
    Добавить ответ на вопрос с заполнением пропусков
    """
    try:
        data = request.get_json()
        attempt_id = data.get('attempt_id')
        node_id = data.get('node_id')
        answer = data.get('answer')
        
        if not all([attempt_id, node_id, answer]):
            return jsonify({
                'success': False,
                'message': 'Attempt ID, node ID, and answer are required'
            }), 400
        
        success = VirtualPatientSessionManager.add_fill_in_answer(
            attempt_id, node_id, answer
        )
        
        if not success:
            return jsonify({
                'success': False,
                'message': 'Failed to add fill-in answer'
            }), 400
        
        return jsonify({
            'success': True,
            'message': 'Answer added successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@vp_daily_bp.route('/my-statistics', methods=['GET'])
@login_required
def get_my_statistics():
    """
    Получить статистику пользователя по виртуальным пациентам
    """
    try:
        stats = VirtualPatientSelector.get_user_statistics(current_user)
        
        return jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@vp_daily_bp.route('/daily-session', methods=['GET'])
@login_required
def get_daily_session():
    """
    Получить полные данные для ежедневной сессии с виртуальным пациентом
    """
    try:
        session_data = VirtualPatientDailyIntegration.get_daily_vp_session(current_user)
        
        return jsonify(session_data)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@vp_daily_bp.route('/integrate-daily-learning', methods=['POST'])
@csrf.exempt
@login_required
def integrate_daily_learning():
    """
    Интегрировать виртуальных пациентов в ежедневные сессии
    """
    try:
        data = request.get_json()
        existing_sessions = data.get('sessions', [])
        
        updated_sessions = VirtualPatientDailyIntegration.integrate_with_daily_learning(
            current_user, existing_sessions
        )
        
        return jsonify({
            'success': True,
            'sessions': updated_sessions
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@vp_daily_bp.route('/scenario/<int:scenario_id>', methods=['GET'])
@login_required
def get_scenario_details(scenario_id):
    """
    Получить детали сценария
    """
    try:
        scenario = VirtualPatientScenario.query.get(scenario_id)
        
        if not scenario:
            return jsonify({
                'success': False,
                'message': 'Scenario not found'
            }), 404
        
        # Проверяем доступность для пользователя
        if not scenario.is_available_for_user(current_user):
            return jsonify({
                'success': False,
                'message': 'Scenario not available for your specialty or recently played'
            }), 403
        
        return jsonify({
            'success': True,
            'scenario': {
                'id': scenario.id,
                'title': scenario.title,
                'description': scenario.description,
                'difficulty': scenario.difficulty,
                'max_score': scenario.max_score,
                'keywords': scenario.keywords_list,
                'scenario_data': scenario.localized_data
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@vp_daily_bp.route('/attempt/<int:attempt_id>', methods=['GET'])
@login_required
def get_attempt_details(attempt_id):
    """
    Получить детали попытки
    """
    try:
        attempt = VirtualPatientAttempt.query.get(attempt_id)
        
        if not attempt or attempt.user_id != current_user.id:
            return jsonify({
                'success': False,
                'message': 'Attempt not found or access denied'
            }), 404
        
        return jsonify({
            'success': True,
            'attempt': {
                'id': attempt.id,
                'scenario_id': attempt.scenario_id,
                'score': attempt.score,
                'max_score': attempt.max_score,
                'completed': attempt.completed,
                'time_spent': attempt.time_spent,
                'started_at': attempt.started_at.isoformat() if attempt.started_at else None,
                'completed_at': attempt.completed_at.isoformat() if attempt.completed_at else None,
                'percentage_score': attempt.percentage_score,
                'fill_in_answers': attempt.fill_in_answers_dict,
                'fill_in_score': attempt.fill_in_score
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
