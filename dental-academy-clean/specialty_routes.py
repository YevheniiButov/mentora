#!/usr/bin/env python3
"""
API маршруты для системы специальностей
Диагностические и обучающие режимы
"""

import logging
from flask import Blueprint, request, jsonify, render_template, current_app
from flask_login import login_required, current_user
from sqlalchemy import and_, or_

from extensions import db
from models import User, Question, DiagnosticSession, DiagnosticResponse
from models_specialty import Specialty, SpecialtyDomain, DiagnosticResult, PilotResponse
from assessment_modes import AssessmentMode, LearningMode, PilotMode
from diagnostic_results import DiagnosticResults, ResultsComparison
from utils.decorators import admin_required

logger = logging.getLogger(__name__)

# Создаем Blueprint для специальностей
specialty_bp = Blueprint('specialty', __name__, url_prefix='/specialty')

# =============================================================================
# СПЕЦИАЛЬНОСТИ
# =============================================================================

@specialty_bp.route('/specialties')
def get_specialties():
    """Получить список доступных специальностей"""
    try:
        specialties = Specialty.query.filter_by(is_active=True).all()
        
        return jsonify({
            'success': True,
            'specialties': [s.to_dict() for s in specialties]
        })
        
    except Exception as e:
        logger.error(f"Error getting specialties: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve specialties'
        }), 500

@specialty_bp.route('/specialties/<int:specialty_id>')
def get_specialty(specialty_id):
    """Получить информацию о специальности"""
    try:
        specialty = Specialty.query.get_or_404(specialty_id)
        
        # Получаем домены специальности
        domains = specialty.domains.all()
        
        return jsonify({
            'success': True,
            'specialty': specialty.to_dict(),
            'domains': [d.to_dict() for d in domains],
            'calibration_progress': specialty.get_calibration_progress(),
            'ready_for_adaptive': specialty.is_ready_for_adaptive_testing()
        })
        
    except Exception as e:
        logger.error(f"Error getting specialty {specialty_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve specialty information'
        }), 500

# =============================================================================
# ДИАГНОСТИЧЕСКИЕ СЕССИИ
# =============================================================================

@specialty_bp.route('/specialties/<int:specialty_id>/start-assessment', methods=['POST'])
@login_required
def start_assessment(specialty_id):
    """Начать диагностическую сессию для специальности"""
    try:
        specialty = Specialty.query.get_or_404(specialty_id)
        
        if not specialty.is_calibrated:
            return jsonify({
                'success': False,
                'error': 'Specialty is not yet calibrated for assessment'
            }), 400
        
        # Создаем диагностическую сессию
        assessment_mode = AssessmentMode(specialty_id)
        session = assessment_mode.start_diagnostic_session(current_user.id)
        
        # Получаем первый вопрос
        first_question = assessment_mode.select_next_question(session)
        
        if not first_question:
            return jsonify({
                'success': False,
                'error': 'No questions available for assessment'
            }), 400
        
        return jsonify({
            'success': True,
            'session': {
                'id': session.id,
                'specialty': specialty.to_dict(),
                'mode': 'assessment',
                'current_ability': session.current_ability,
                'ability_se': session.ability_se
            },
            'question': {
                'id': first_question.id,
                'text': first_question.text,
                'options': first_question.options,
                'domain': first_question.domain,
                'difficulty_level': first_question.difficulty_level
            }
        })
        
    except Exception as e:
        logger.error(f"Error starting assessment: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to start assessment'
        }), 500

@specialty_bp.route('/sessions/<int:session_id>/answer', methods=['POST'])
@login_required
def submit_answer(session_id):
    """Отправить ответ на вопрос"""
    try:
        data = request.get_json()
        selected_answer = data.get('selected_answer')
        response_time = data.get('response_time', 0)
        
        if not selected_answer:
            return jsonify({
                'success': False,
                'error': 'Selected answer is required'
            }), 400
        
        # Получаем сессию
        session = DiagnosticSession.query.get_or_404(session_id)
        
        if session.user_id != current_user.id:
            return jsonify({
                'success': False,
                'error': 'Unauthorized access to session'
            }), 403
        
        if session.status != 'active':
            return jsonify({
                'success': False,
                'error': 'Session is not active'
            }), 400
        
        # Обрабатываем ответ
        assessment_mode = AssessmentMode(session.specialty_id)
        response = assessment_mode.process_response(
            session, session.current_question_id, selected_answer, response_time
        )
        
        # Проверяем критерии завершения
        should_terminate, reason = assessment_mode.check_termination_criteria(session)
        
        if should_terminate:
            # Завершаем сессию
            results = assessment_mode.complete_session(session)
            
            return jsonify({
                'success': True,
                'response': {
                    'is_correct': response.is_correct,
                    'correct_answer': response.question.correct_answer_text,
                    'explanation': response.question.explanation,
                    'ability_after': response.ability_after,
                    'se_after': response.se_after
                },
                'session_completed': True,
                'termination_reason': reason,
                'results': results
            })
        else:
            # Получаем следующий вопрос
            next_question = assessment_mode.select_next_question(session)
            
            if not next_question:
                # Нет больше вопросов, завершаем сессию
                results = assessment_mode.complete_session(session)
                
                return jsonify({
                    'success': True,
                    'response': {
                        'is_correct': response.is_correct,
                        'correct_answer': response.question.correct_answer_text,
                        'explanation': response.question.explanation,
                        'ability_after': response.ability_after,
                        'se_after': response.se_after
                    },
                    'session_completed': True,
                    'termination_reason': 'no_more_questions',
                    'results': results
                })
            
            return jsonify({
                'success': True,
                'response': {
                    'is_correct': response.is_correct,
                    'correct_answer': response.question.correct_answer_text,
                    'explanation': response.question.explanation,
                    'ability_after': response.ability_after,
                    'se_after': response.se_after
                },
                'next_question': {
                    'id': next_question.id,
                    'text': next_question.text,
                    'options': next_question.options,
                    'domain': next_question.domain,
                    'difficulty_level': next_question.difficulty_level
                },
                'session_completed': False
            })
        
    except Exception as e:
        logger.error(f"Error submitting answer: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to submit answer'
        }), 500

@specialty_bp.route('/sessions/<int:session_id>/status')
@login_required
def get_session_status(session_id):
    """Получить статус сессии"""
    try:
        session = DiagnosticSession.query.get_or_404(session_id)
        
        if session.user_id != current_user.id:
            return jsonify({
                'success': False,
                'error': 'Unauthorized access to session'
            }), 403
        
        return jsonify({
            'success': True,
            'session': {
                'id': session.id,
                'status': session.status,
                'specialty': session.specialty.to_dict(),
                'questions_answered': session.questions_answered,
                'correct_answers': session.correct_answers,
                'current_ability': session.current_ability,
                'ability_se': session.ability_se,
                'started_at': session.started_at.isoformat() if session.started_at else None,
                'completed_at': session.completed_at.isoformat() if session.completed_at else None
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting session status: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get session status'
        }), 500

# =============================================================================
# РЕЖИМ ОБУЧЕНИЯ
# =============================================================================

@specialty_bp.route('/specialties/<int:specialty_id>/learning/questions')
@login_required
def get_learning_questions(specialty_id):
    """Получить вопросы для обучения"""
    try:
        domain_code = request.args.get('domain')
        limit = int(request.args.get('limit', 10))
        
        learning_mode = LearningMode(specialty_id)
        
        if domain_code:
            questions = learning_mode.get_domain_questions(domain_code, limit)
        else:
            questions = learning_mode.get_learning_questions(limit=limit)
        
        return jsonify({
            'success': True,
            'questions': [{
                'id': q.id,
                'text': q.text,
                'options': q.options,
                'correct_answer_text': q.correct_answer_text,
                'explanation': q.explanation,
                'domain': q.domain,
                'difficulty_level': q.difficulty_level,
                'learning_mode': True
            } for q in questions]
        })
        
    except Exception as e:
        logger.error(f"Error getting learning questions: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get learning questions'
        }), 500

@specialty_bp.route('/specialties/<int:specialty_id>/learning/domains')
@login_required
def get_learning_domains(specialty_id):
    """Получить доступные домены для обучения"""
    try:
        learning_mode = LearningMode(specialty_id)
        domains = learning_mode.get_available_domains()
        
        return jsonify({
            'success': True,
            'domains': domains
        })
        
    except Exception as e:
        logger.error(f"Error getting learning domains: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get learning domains'
        }), 500

# =============================================================================
# ПИЛОТИРОВАНИЕ
# =============================================================================

@specialty_bp.route('/specialties/<int:specialty_id>/start-pilot', methods=['POST'])
@login_required
def start_pilot(specialty_id):
    """Начать пилотную сессию для калибровки"""
    try:
        specialty = Specialty.query.get_or_404(specialty_id)
        
        if specialty.is_calibrated:
            return jsonify({
                'success': False,
                'error': 'Specialty is already calibrated'
            }), 400
        
        # Создаем пилотную сессию
        pilot_mode = PilotMode(specialty_id)
        session = pilot_mode.start_pilot_session(current_user.id)
        
        # Получаем вопросы для пилотирования
        pilot_questions = pilot_mode.select_pilot_questions(session)
        
        if not pilot_questions:
            return jsonify({
                'success': False,
                'error': 'No questions available for piloting'
            }), 400
        
        return jsonify({
            'success': True,
            'session': {
                'id': session.id,
                'specialty': specialty.to_dict(),
                'mode': 'pilot'
            },
            'questions': [{
                'id': q.id,
                'text': q.text,
                'options': q.options,
                'domain': q.domain,
                'difficulty_level': q.difficulty_level,
                'response_count': q.response_count
            } for q in pilot_questions]
        })
        
    except Exception as e:
        logger.error(f"Error starting pilot: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to start pilot session'
        }), 500

@specialty_bp.route('/sessions/<int:session_id>/pilot-answer', methods=['POST'])
@login_required
def submit_pilot_answer(session_id):
    """Отправить ответ в пилотной сессии"""
    try:
        data = request.get_json()
        question_id = data.get('question_id')
        selected_answer = data.get('selected_answer')
        response_time = data.get('response_time', 0)
        
        if not all([question_id, selected_answer]):
            return jsonify({
                'success': False,
                'error': 'Question ID and selected answer are required'
            }), 400
        
        # Получаем сессию
        session = DiagnosticSession.query.get_or_404(session_id)
        
        if session.user_id != current_user.id:
            return jsonify({
                'success': False,
                'error': 'Unauthorized access to session'
            }), 403
        
        if session.session_type != 'pilot':
            return jsonify({
                'success': False,
                'error': 'Session is not a pilot session'
            }), 400
        
        # Получаем вопрос
        question = Question.query.get(question_id)
        if not question:
            return jsonify({
                'success': False,
                'error': 'Question not found'
            }), 404
        
        # Проверяем правильность ответа
        is_correct = selected_answer == question.correct_answer_text
        
        # Собираем данные для калибровки
        pilot_mode = PilotMode(session.specialty_id)
        pilot_mode.collect_pilot_data(session, question_id, is_correct, response_time)
        
        return jsonify({
            'success': True,
            'response': {
                'is_correct': is_correct,
                'correct_answer': question.correct_answer_text,
                'explanation': question.explanation
            },
            'question_stats': {
                'response_count': question.response_count,
                'correct_count': question.correct_count,
                'accuracy': question.get_accuracy(),
                'ready_for_calibration': question.response_count >= session.specialty.calibration_threshold
            }
        })
        
    except Exception as e:
        logger.error(f"Error submitting pilot answer: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to submit pilot answer'
        }), 500

# =============================================================================
# РЕЗУЛЬТАТЫ ДИАГНОСТИКИ
# =============================================================================

@specialty_bp.route('/sessions/<int:session_id>/results')
@login_required
def get_session_results(session_id):
    """Получить результаты диагностической сессии"""
    try:
        session = DiagnosticSession.query.get_or_404(session_id)
        
        if session.user_id != current_user.id:
            return jsonify({
                'success': False,
                'error': 'Unauthorized access to session'
            }), 403
        
        if session.status != 'completed':
            return jsonify({
                'success': False,
                'error': 'Session is not completed'
            }), 400
        
        # Генерируем результаты
        results_generator = DiagnosticResults(session)
        results = results_generator.generate_comprehensive_report()
        
        # Сохраняем результаты в базе данных
        saved_result = results_generator.save_results()
        
        return jsonify({
            'success': True,
            'results': results,
            'saved_result_id': saved_result.id if saved_result else None
        })
        
    except Exception as e:
        logger.error(f"Error getting session results: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get session results'
        }), 500

@specialty_bp.route('/users/<int:user_id>/progress/<int:specialty_id>')
@login_required
def get_user_progress(user_id, specialty_id):
    """Получить прогресс пользователя по специальности"""
    try:
        # Проверяем права доступа
        if current_user.id != user_id and not current_user.is_admin:
            return jsonify({
                'success': False,
                'error': 'Unauthorized access to user progress'
            }), 403
        
        # Получаем прогресс
        progress_comparison = ResultsComparison(user_id, specialty_id)
        progress = progress_comparison.get_user_progress()
        specialty_stats = progress_comparison.get_specialty_statistics()
        
        return jsonify({
            'success': True,
            'progress': progress,
            'specialty_statistics': specialty_stats
        })
        
    except Exception as e:
        logger.error(f"Error getting user progress: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get user progress'
        }), 500

# =============================================================================
# АДМИНИСТРАТИВНЫЕ ФУНКЦИИ
# =============================================================================

@specialty_bp.route('/admin/specialties')
@login_required
@admin_required
def admin_specialties():
    """Административная панель специальностей"""
    try:
        specialties = Specialty.query.all()
        
        return render_template('admin/specialties.html', specialties=specialties)
        
    except Exception as e:
        logger.error(f"Error in admin specialties: {str(e)}")
        return render_template('admin/specialties.html', specialties=[], error=str(e))

@specialty_bp.route('/admin/specialties/<int:specialty_id>/calibration-status')
@login_required
@admin_required
def get_calibration_status(specialty_id):
    """Получить статус калибровки специальности"""
    try:
        specialty = Specialty.query.get_or_404(specialty_id)
        
        # Статистика по доменам
        domains_stats = []
        for domain in specialty.domains:
            domains_stats.append({
                'domain_code': domain.domain_code,
                'domain_name': domain.domain_name,
                'question_count': domain.question_count,
                'calibrated_count': domain.calibrated_count,
                'calibration_progress': domain.get_calibration_progress()
            })
        
        # Общая статистика
        total_questions = Question.query.filter_by(specialty_id=specialty_id).count()
        calibrated_questions = Question.query.filter(
            Question.specialty_id == specialty_id,
            Question.is_calibrated == True
        ).count()
        
        return jsonify({
            'success': True,
            'specialty': specialty.to_dict(),
            'overall_stats': {
                'total_questions': total_questions,
                'calibrated_questions': calibrated_questions,
                'calibration_progress': (calibrated_questions / total_questions) * 100 if total_questions > 0 else 0
            },
            'domains_stats': domains_stats
        })
        
    except Exception as e:
        logger.error(f"Error getting calibration status: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get calibration status'
        }), 500

@specialty_bp.route('/admin/specialties/<int:specialty_id>/pilot-progress')
@login_required
@admin_required
def get_pilot_progress(specialty_id):
    """Получить прогресс пилотирования"""
    try:
        specialty = Specialty.query.get_or_404(specialty_id)
        
        # Статистика пилотных ответов
        pilot_responses = PilotResponse.query.filter_by(specialty_id=specialty_id).count()
        unique_users = db.session.query(PilotResponse.user_id).filter_by(
            specialty_id=specialty_id
        ).distinct().count()
        
        # Вопросы, готовые к калибровке
        ready_for_calibration = Question.query.filter(
            Question.specialty_id == specialty_id,
            Question.is_calibrated == False,
            Question.response_count >= specialty.calibration_threshold
        ).count()
        
        return jsonify({
            'success': True,
            'pilot_stats': {
                'total_responses': pilot_responses,
                'unique_users': unique_users,
                'ready_for_calibration': ready_for_calibration,
                'calibration_threshold': specialty.calibration_threshold
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting pilot progress: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get pilot progress'
        }), 500
