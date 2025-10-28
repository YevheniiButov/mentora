"""
Virtual Patient Daily Learning Routes
Маршруты для системы ежедневного обучения с виртуальными пациентами
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import json
import logging

from app.utils.virtual_patient_utils import (
    VirtualPatientSelector, 
    VirtualPatientSessionManager,
    calculate_fill_in_score,
    get_daily_learning_summary
)
from models import VirtualPatientScenario, VirtualPatientAttempt, db

# Создаем Blueprint
vp_daily_bp = Blueprint('vp_daily', __name__, url_prefix='/virtual-patient-daily')

logger = logging.getLogger(__name__)


@vp_daily_bp.route('/')
@login_required
def daily_learning():
    """Главная страница ежедневного обучения с виртуальными пациентами"""
    try:
        summary = get_daily_learning_summary(current_user)
        return render_template('virtual_patient/daily_learning.html', summary=summary)
    except Exception as e:
        logger.error(f"Error loading daily learning page: {e}")
        flash('Ошибка загрузки страницы ежедневного обучения', 'error')
        return redirect(url_for('dashboard'))


@vp_daily_bp.route('/scenarios')
@login_required
def get_scenarios():
    """API: Получить доступные сценарии для ежедневного обучения"""
    try:
        selector = VirtualPatientSelector(current_user)
        
        # Получаем параметры
        limit = request.args.get('limit', 5, type=int)
        difficulty = request.args.get('difficulty')
        category = request.args.get('category')
        keywords = request.args.get('keywords', '').split(',') if request.args.get('keywords') else []
        
        # Фильтруем ключевые слова
        keywords = [kw.strip() for kw in keywords if kw.strip()]
        
        # Получаем сценарии
        if keywords:
            scenarios = selector.get_scenario_by_keywords(keywords, limit)
        else:
            scenarios = selector.get_daily_scenarios(limit)
        
        # Дополнительная фильтрация
        if difficulty:
            scenarios = [s for s in scenarios if s.difficulty == difficulty]
        
        if category:
            scenarios = [s for s in scenarios if s.category == category]
        
        # Формируем ответ
        scenarios_data = []
        for scenario in scenarios:
            # Проверяем, играл ли пользователь этот сценарий
            last_attempt = VirtualPatientAttempt.query.filter(
                VirtualPatientAttempt.user_id == current_user.id,
                VirtualPatientAttempt.scenario_id == scenario.id
            ).order_by(VirtualPatientAttempt.completed_at.desc()).first()
            
            scenarios_data.append({
                'id': scenario.id,
                'title': scenario.title,
                'description': scenario.description,
                'difficulty': scenario.difficulty,
                'category': scenario.category,
                'max_score': scenario.max_score,
                'specialty': scenario.specialty,
                'is_premium': scenario.is_premium,
                'last_played': last_attempt.completed_at.isoformat() if last_attempt and last_attempt.completed_at else None,
                'best_score': last_attempt.score if last_attempt else 0,
                'is_available': scenario.is_available_for_user(current_user)
            })
        
        return jsonify({
            'success': True,
            'scenarios': scenarios_data,
            'total': len(scenarios_data)
        })
        
    except Exception as e:
        logger.error(f"Error getting scenarios: {e}")
        return jsonify({
            'success': False,
            'error': 'Ошибка получения сценариев'
        }), 500


@vp_daily_bp.route('/start/<int:scenario_id>')
@login_required
def start_scenario(scenario_id):
    """Начать сценарий виртуального пациента"""
    try:
        scenario = VirtualPatientScenario.query.get_or_404(scenario_id)
        
        # Проверяем доступность
        if not scenario.is_published:
            flash('Сценарий недоступен', 'error')
            return redirect(url_for('vp_daily.daily_learning'))
        
        if not scenario.is_available_for_user(current_user):
            flash('Сценарий недоступен для повторного прохождения', 'error')
            return redirect(url_for('vp_daily.daily_learning'))
        
        # Создаем менеджер сессии
        session_manager = VirtualPatientSessionManager(current_user, scenario)
        attempt = session_manager.start_session()
        
        # Сохраняем ID попытки в сессии
        session['current_vp_attempt_id'] = attempt.id
        
        # Получаем данные сценария
        scenario_data = scenario.localized_data
        
        return render_template('virtual_patient/play_scenario.html', 
                             scenario=scenario, 
                             scenario_data=scenario_data,
                             attempt_id=attempt.id)
        
    except Exception as e:
        logger.error(f"Error starting scenario {scenario_id}: {e}")
        flash('Ошибка запуска сценария', 'error')
        return redirect(url_for('vp_daily.daily_learning'))


@vp_daily_bp.route('/save-answer', methods=['POST'])
@login_required
def save_answer():
    """Сохранить ответ на fill-in вопрос"""
    try:
        data = request.get_json()
        node_id = data.get('node_id')
        answer = data.get('answer')
        
        if not node_id or not answer:
            return jsonify({
                'success': False,
                'error': 'Неверные данные'
            }), 400
        
        # Получаем текущую попытку
        attempt_id = session.get('current_vp_attempt_id')
        if not attempt_id:
            return jsonify({
                'success': False,
                'error': 'Сессия не найдена'
            }), 400
        
        attempt = VirtualPatientAttempt.query.get(attempt_id)
        if not attempt or attempt.user_id != current_user.id:
            return jsonify({
                'success': False,
                'error': 'Попытка не найдена'
            }), 400
        
        # Создаем менеджер сессии
        session_manager = VirtualPatientSessionManager(current_user, attempt.scenario)
        session_manager.attempt = attempt
        
        # Сохраняем ответ
        success = session_manager.save_fill_in_answer(node_id, answer)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Ответ сохранен'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Ошибка сохранения ответа'
            }), 500
            
    except Exception as e:
        logger.error(f"Error saving answer: {e}")
        return jsonify({
            'success': False,
            'error': 'Ошибка сохранения ответа'
        }), 500


@vp_daily_bp.route('/complete', methods=['POST'])
@login_required
def complete_scenario():
    """Завершить сценарий"""
    try:
        data = request.get_json()
        score = data.get('score', 0)
        dialogue_history = data.get('dialogue_history', [])
        fill_in_answers = data.get('fill_in_answers', {})
        
        # Получаем текущую попытку
        attempt_id = session.get('current_vp_attempt_id')
        if not attempt_id:
            return jsonify({
                'success': False,
                'error': 'Сессия не найдена'
            }), 400
        
        attempt = VirtualPatientAttempt.query.get(attempt_id)
        if not attempt or attempt.user_id != current_user.id:
            return jsonify({
                'success': False,
                'error': 'Попытка не найдена'
            }), 400
        
        # Создаем менеджер сессии
        session_manager = VirtualPatientSessionManager(current_user, attempt.scenario)
        session_manager.attempt = attempt
        
        # Сохраняем fill-in ответы
        for node_id, answer in fill_in_answers.items():
            session_manager.save_fill_in_answer(node_id, answer)
        
        # Вычисляем балл за fill-in вопросы (если есть правильные ответы)
        fill_in_score = 0
        if fill_in_answers:
            # Здесь должна быть логика получения правильных ответов из сценария
            # Пока просто считаем количество ответов
            fill_in_score = len(fill_in_answers)
        
        # Обновляем fill_in_score
        attempt.fill_in_score = fill_in_score
        
        # Завершаем сессию
        success = session_manager.complete_session(score, dialogue_history)
        
        if success:
            # Очищаем сессию
            session.pop('current_vp_attempt_id', None)
            
            return jsonify({
                'success': True,
                'message': 'Сценарий завершен',
                'score': score,
                'max_score': attempt.max_score,
                'percentage': attempt.percentage_score,
                'fill_in_score': fill_in_score
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Ошибка завершения сценария'
            }), 500
            
    except Exception as e:
        logger.error(f"Error completing scenario: {e}")
        return jsonify({
            'success': False,
            'error': 'Ошибка завершения сценария'
        }), 500


@vp_daily_bp.route('/stats')
@login_required
def get_stats():
    """Получить статистику пользователя"""
    try:
        selector = VirtualPatientSelector(current_user)
        stats = selector.get_user_progress_stats()
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({
            'success': False,
            'error': 'Ошибка получения статистики'
        }), 500


@vp_daily_bp.route('/history')
@login_required
def get_history():
    """Получить историю прохождения сценариев"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Получаем попытки пользователя
        attempts = VirtualPatientAttempt.query.filter(
            VirtualPatientAttempt.user_id == current_user.id
        ).join(VirtualPatientScenario).order_by(
            VirtualPatientAttempt.completed_at.desc()
        ).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        history_data = []
        for attempt in attempts.items:
            history_data.append({
                'id': attempt.id,
                'scenario_title': attempt.scenario.title,
                'scenario_difficulty': attempt.scenario.difficulty,
                'scenario_category': attempt.scenario.category,
                'score': attempt.score,
                'max_score': attempt.max_score,
                'percentage': attempt.percentage_score,
                'completed': attempt.completed,
                'time_spent': attempt.time_spent,
                'started_at': attempt.started_at.isoformat() if attempt.started_at else None,
                'completed_at': attempt.completed_at.isoformat() if attempt.completed_at else None,
                'fill_in_score': attempt.fill_in_score
            })
        
        return jsonify({
            'success': True,
            'history': history_data,
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': attempts.total,
                'pages': attempts.pages,
                'has_next': attempts.has_next,
                'has_prev': attempts.has_prev
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        return jsonify({
            'success': False,
            'error': 'Ошибка получения истории'
        }), 500


@vp_daily_bp.route('/recommendations')
@login_required
def get_recommendations():
    """Получить рекомендации сценариев"""
    try:
        selector = VirtualPatientSelector(current_user)
        limit = request.args.get('limit', 3, type=int)
        
        recommendations = selector.get_recommended_scenarios(limit)
        
        recommendations_data = []
        for scenario in recommendations:
            recommendations_data.append({
                'id': scenario.id,
                'title': scenario.title,
                'description': scenario.description,
                'difficulty': scenario.difficulty,
                'category': scenario.category,
                'max_score': scenario.max_score,
                'specialty': scenario.specialty,
                'is_premium': scenario.is_premium
            })
        
        return jsonify({
            'success': True,
            'recommendations': recommendations_data
        })
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        return jsonify({
            'success': False,
            'error': 'Ошибка получения рекомендаций'
        }), 500


@vp_daily_bp.route('/search')
@login_required
def search_scenarios():
    """Поиск сценариев по ключевым словам"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({
                'success': True,
                'scenarios': []
            })
        
        keywords = [kw.strip() for kw in query.split() if kw.strip()]
        selector = VirtualPatientSelector(current_user)
        limit = request.args.get('limit', 10, type=int)
        
        scenarios = selector.get_scenario_by_keywords(keywords, limit)
        
        search_results = []
        for scenario in scenarios:
            search_results.append({
                'id': scenario.id,
                'title': scenario.title,
                'description': scenario.description,
                'difficulty': scenario.difficulty,
                'category': scenario.category,
                'max_score': scenario.max_score,
                'specialty': scenario.specialty,
                'is_premium': scenario.is_premium,
                'keywords': scenario.keywords_list
            })
        
        return jsonify({
            'success': True,
            'scenarios': search_results,
            'query': query
        })
        
    except Exception as e:
        logger.error(f"Error searching scenarios: {e}")
        return jsonify({
            'success': False,
            'error': 'Ошибка поиска сценариев'
        }), 500
