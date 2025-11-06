#!/usr/bin/env python3
"""
Маршруты для системы промежуточного тестирования
"""

from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, g
from flask_login import login_required, current_user
from models import Module, TestSession, TestResult
from extensions import db
from utils.intermediate_testing import (
    create_module_test, get_next_question, submit_test_answer,
    get_test_history, get_performance_stats
)
from datetime import datetime, timezone

testing_bp = Blueprint('testing', __name__)

@testing_bp.route('/intermediate')
@login_required
def intermediate_tests():
    """Страница промежуточного тестирования"""
    
    # Получаем модули с прогрессом
    modules = Module.query.filter_by(is_active=True).all()
    
    modules_with_progress = []
    for module in modules:
        # Получаем статистику тестов для модуля
        stats = get_performance_stats(current_user.id, module.id)
        
        # Получаем последний тест
        history = get_test_history(current_user.id, module.id)
        last_test = history[0] if history else None
        
        modules_with_progress.append({
            'module': module,
            'stats': stats,
            'last_test': last_test,
            'can_take_test': True  # Можно ли пройти тест
        })
    
    return render_template('testing/intermediate_tests.html',
                         modules=modules_with_progress)

@testing_bp.route('/intermediate/module/<int:module_id>')
@login_required
def module_test_page(module_id):
    """Страница теста для конкретного модуля"""
    
    module = Module.query.get_or_404(module_id)
    
    # Получаем историю тестов для модуля
    test_history = get_test_history(current_user.id, module_id)
    
    # Получаем статистику производительности
    performance_stats = get_performance_stats(current_user.id, module_id)
    
    return render_template('testing/module_test.html',
                         module=module,
                         test_history=test_history,
                         performance_stats=performance_stats)

@testing_bp.route('/intermediate/module/<int:module_id>/start', methods=['POST'])
@login_required
def start_module_test(module_id):
    """Начинает тест для модуля"""
    
    try:
        test_type = request.form.get('test_type', 'adaptive')
        
        # Создаем тест
        test_data = create_module_test(current_user.id, module_id, test_type)
        
        return jsonify({
            'success': True,
            'session_id': test_data['session_id'],
            'total_questions': test_data['total_questions'],
            'estimated_time': test_data['estimated_time'],
            'difficulty': test_data['difficulty']
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Ошибка при создании теста: {str(e)}'
        }), 500

@testing_bp.route('/intermediate/test/<int:session_id>')
@login_required
def take_test(session_id):
    """Страница прохождения теста"""
    
    session = TestSession.query.get_or_404(session_id)
    
    # Проверяем, что тест принадлежит пользователю
    if session.user_id != current_user.id:
        flash('Доступ запрещен', 'error')
        return redirect(url_for('testing.intermediate_tests'))
    
    # Проверяем статус теста
    if session.status == 'completed':
        flash('Тест уже завершен', 'info')
        return redirect(url_for('testing.test_results', session_id=session_id))
    
    # Получаем первый вопрос
    first_question = get_next_question(current_user.id, session_id)
    
    return render_template('testing/take_test.html',
                         session=session,
                         first_question=first_question)

@testing_bp.route('/intermediate/test/<int:session_id>/question')
@login_required
def get_question(session_id):
    """Получает следующий вопрос теста"""
    
    session = TestSession.query.get_or_404(session_id)
    
    if session.user_id != current_user.id:
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    if session.status != 'in_progress':
        return jsonify({'error': 'Тест уже завершен'}), 400
    
    question = get_next_question(current_user.id, session_id)
    
    if not question:
        return jsonify({'error': 'Вопросы закончились'}), 404
    
    return jsonify(question)

@testing_bp.route('/intermediate/test/<int:session_id>/answer', methods=['POST'])
@login_required
def submit_answer(session_id):
    """Отправляет ответ на вопрос"""
    
    session = TestSession.query.get_or_404(session_id)
    
    if session.user_id != current_user.id:
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    if session.status != 'in_progress':
        return jsonify({'error': 'Тест уже завершен'}), 400
    
    try:
        data = request.get_json()
        question_id = data.get('question_id')
        answer = data.get('answer')
        
        if not question_id or answer is None:
            return jsonify({'error': 'Неверные данные'}), 400
        
        result = submit_test_answer(current_user.id, session_id, question_id, answer)
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({
            'error': f'Ошибка при отправке ответа: {str(e)}'
        }), 500

@testing_bp.route('/intermediate/test/<int:session_id>/results')
@login_required
def test_results(session_id):
    """Страница результатов теста"""
    
    session = TestSession.query.get_or_404(session_id)
    
    if session.user_id != current_user.id:
        flash('Доступ запрещен', 'error')
        return redirect(url_for('testing.intermediate_tests'))
    
    if session.status != 'completed':
        flash('Тест еще не завершен', 'warning')
        return redirect(url_for('testing.take_test', session_id=session_id))
    
    # Получаем детальную информацию о результатах
    session_data = session.get_session_data()
    
    return render_template('testing/test_results.html',
                         session=session,
                         session_data=session_data)

@testing_bp.route('/intermediate/history')
@login_required
def test_history():
    """Страница истории тестов"""
    
    # Получаем историю всех тестов
    all_history = get_test_history(current_user.id)
    
    # Получаем общую статистику
    overall_stats = get_performance_stats(current_user.id)
    
    # Группируем по модулям
    modules = Module.query.filter_by(is_active=True).all()
    module_stats = {}
    
    for module in modules:
        module_stats[module.id] = get_performance_stats(current_user.id, module.id)
    
    return render_template('testing/test_history.html',
                         test_history=all_history,
                         overall_stats=overall_stats,
                         module_stats=module_stats,
                         modules=modules)

@testing_bp.route('/intermediate/api/stats')
@login_required
def api_test_stats():
    """API для получения статистики тестов"""
    
    try:
        module_id = request.args.get('module_id', type=int)
        stats = get_performance_stats(current_user.id, module_id)
        
        return jsonify({
            'success': True,
            'stats': stats
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Ошибка при получении статистики: {str(e)}'
        }), 500

@testing_bp.route('/intermediate/api/history')
@login_required
def api_test_history():
    """API для получения истории тестов"""
    
    try:
        module_id = request.args.get('module_id', type=int)
        history = get_test_history(current_user.id, module_id)
        
        return jsonify({
            'success': True,
            'history': history
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Ошибка при получении истории: {str(e)}'
        }), 500

# Блокировка через CSS overlay - убрано для использования JavaScript overlay