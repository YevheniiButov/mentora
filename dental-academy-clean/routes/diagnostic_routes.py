"""
Diagnostic Routes for BI-toets System
Flask Blueprint for diagnostic testing with IRT engine integration
"""

from flask import Blueprint, render_template, request, session, current_app, g, flash, redirect, url_for
from flask_login import current_user, login_required
from werkzeug.exceptions import BadRequest, Unauthorized, TooManyRequests
from functools import wraps
import time
import logging
import json
from datetime import datetime, timedelta, timezone

from models import db, DiagnosticSession, Question, IRTParameters, User, PersonalLearningPlan, StudySession, BIGDomain, DiagnosticResponse
from utils.serializers import safe_jsonify
from utils.irt_engine import IRTEngine
from utils.rate_limiter import RateLimiter
from utils.session_validator import SessionValidator
from utils.translations import t

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Blueprint
diagnostic_bp = Blueprint('diagnostic', __name__, url_prefix='/big-diagnostic')

# Rate limiter instance
rate_limiter = RateLimiter()

# Session validator instance
session_validator = SessionValidator()

def rate_limit(requests_per_minute=60):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = current_user.id if current_user.is_authenticated else request.remote_addr
            if not rate_limiter.check_rate_limit(user_id, requests_per_minute):
                raise TooManyRequests('Rate limit exceeded')
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_session(f):
    """Session validation decorator - temporarily simplified for testing"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_id = kwargs.get('session_id') or request.json.get('session_id')
        
        # Проверяем, что session_id не равен 0 или None
        if not session_id or session_id == 0:
            logger.warning(f"Invalid session_id: {session_id}")
            return safe_jsonify({
                'success': False,
                'error': 'Invalid session ID'
            }), 400
        
        diagnostic_session = DiagnosticSession.query.get(session_id)
        if not diagnostic_session:
            logger.warning(f"Session not found: {session_id}")
            return safe_jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        # Проверяем, что пользователь имеет доступ к этой сессии
        if diagnostic_session.user_id != current_user.id:
            logger.warning(f"User {current_user.id} tried to access session {session_id} owned by {diagnostic_session.user_id}")
            return safe_jsonify({
                'success': False,
                'error': 'Access denied'
            }), 403
        
        g.current_session = diagnostic_session
        return f(*args, **kwargs)
    return decorated_function

@diagnostic_bp.route('/start', methods=['GET', 'POST'])
@login_required
@rate_limit(requests_per_minute=10)
def start_diagnostic():
    """Start new diagnostic session"""
    try:
        if request.method == 'POST':
            # Поддержка как JSON, так и form data
            if request.is_json:
                data = request.get_json() or {}
                diagnostic_type = data.get('diagnostic_type', 'express')
            else:
                diagnostic_type = request.form.get('diagnostic_type', 'express')
            
            # Валидация типа диагностики
            if diagnostic_type not in ['express', 'preliminary', 'readiness']:
                diagnostic_type = 'express'
            
            # Check for existing active session
            active_session = DiagnosticSession.query.filter_by(
                user_id=current_user.id,
                status='active'
            ).first()
            
            if active_session:
                if request.is_json:
                    session_data = active_session.get_session_data()
                    return safe_jsonify({
                        'success': False,
                        'error': 'active_session',
                        'session_info': {
                            'id': active_session.id,
                            'diagnostic_type': session_data.get('diagnostic_type', 'express'),
                            'questions_answered': active_session.questions_answered,
                            'correct_answers': active_session.correct_answers,
                            'current_ability': active_session.current_ability,
                            'progress': round((active_session.questions_answered / session_data.get('estimated_total_questions', 25)) * 100) if active_session.questions_answered > 0 else 0,
                            'created_at': active_session.started_at.isoformat()
                        }
                    }), 200
                else:
                    flash('У вас уже есть активная диагностическая сессия', 'warning')
                    return redirect(url_for('diagnostic.show_question', session_id=active_session.id))

            # Initialize new diagnostic session
            diagnostic_session = DiagnosticSession.create_session(
                user_id=current_user.id,
                session_type='adaptive_diagnostic',
                ip_address=request.remote_addr
            )
            
            # Сохранить тип диагностики в сессии
            session_data = {
                'diagnostic_type': diagnostic_type,
                'questions_per_domain': 1 if diagnostic_type == 'express' else (3 if diagnostic_type == 'preliminary' else 5),
                'estimated_total_questions': 25 if diagnostic_type == 'express' else (75 if diagnostic_type == 'preliminary' else 130)
            }
            diagnostic_session.set_session_data(session_data)
            
            # Get first question using IRT with diagnostic type
            irt_engine = IRTEngine(diagnostic_type=diagnostic_type)
            first_question = irt_engine.select_initial_question()
            
            if not first_question:
                raise BadRequest('No questions available')
            
            # Update session with first question
            diagnostic_session.current_question_id = first_question.id
            diagnostic_session.started_at = datetime.now(timezone.utc)
            db.session.commit()
            
            logger.info(f"Started {diagnostic_type} diagnostic session {diagnostic_session.id} for user {current_user.id}")
            
            if request.is_json:
                return safe_jsonify({
                    'success': True,
                    'session_id': diagnostic_session.id,
                    'diagnostic_type': diagnostic_type,
                    'redirect_url': url_for('diagnostic.show_question', session_id=diagnostic_session.id)
                })
            else:
                # Redirect to diagnostic question page
                return redirect(url_for('diagnostic.show_question', session_id=diagnostic_session.id))
        
        # GET request - redirect to diagnostic type selector
        return redirect(url_for('diagnostic.choose_diagnostic_type'))
        
    except Exception as e:
        logger.error(f"Error starting diagnostic: {str(e)}")
        if request.is_json:
            return safe_jsonify({
                'success': False,
                'error': 'Failed to start diagnostic session'
            }), 500
        else:
            flash('Ошибка при запуске диагностики', 'error')
            return redirect(url_for('diagnostic.choose_diagnostic_type'))

@diagnostic_bp.route('/next-question', methods=['POST'])
@login_required
@rate_limit(requests_per_minute=30)
@validate_session
def get_next_question():
    """Get next question in diagnostic session"""
    try:
        data = request.get_json()
        if not data:
            raise BadRequest('Invalid request data')
        
        diagnostic_session = g.current_session
        previous_answer = data.get('previous_answer')
        response_time = data.get('response_time', 0)
        
        # Получить тип диагностики из сессии
        session_data = diagnostic_session.get_session_data()
        diagnostic_type = session_data.get('diagnostic_type', 'express')
        
        # Process previous answer if provided (for backward compatibility)
        # Note: In the new flow, answers are recorded in submit-answer endpoint
        if previous_answer is not None:
            # Check if this answer was already recorded
            existing_response = DiagnosticResponse.query.filter_by(
                session_id=diagnostic_session.id,
                question_id=diagnostic_session.current_question_id
            ).first()
            
            if not existing_response:
                diagnostic_session.record_response(
                    question_id=diagnostic_session.current_question_id,
                    selected_option=previous_answer,
                    response_time=response_time
                )
                logger.info(f"Recorded answer for session {diagnostic_session.id}: {previous_answer}")
            else:
                logger.info(f"Answer already recorded for session {diagnostic_session.id}, skipping duplicate")
        
        # Get next question using IRT with diagnostic type
        irt_engine = IRTEngine(diagnostic_session, diagnostic_type=diagnostic_type)
        
        # Check if session should terminate
        if irt_engine.should_terminate():
            diagnostic_session.status = 'completed'
            diagnostic_session.completed_at = datetime.now(timezone.utc)
            db.session.commit()
            
            logger.info(f"Diagnostic session {diagnostic_session.id} completed")
            
            return safe_jsonify({
                'success': True,
                'session_completed': True,
                'message': 'Diagnostic completed successfully',
                'redirect_url': f'/big-diagnostic/results/{diagnostic_session.id}'
            })
        
        next_question = irt_engine.select_next_question()
        if not next_question:
            # No more questions available - complete the session
            diagnostic_session.status = 'completed'
            diagnostic_session.completed_at = datetime.now(timezone.utc)
            db.session.commit()
            
            logger.info(f"Diagnostic session {diagnostic_session.id} completed - no more questions")
            
            return safe_jsonify({
                'success': True,
                'session_completed': True,
                'message': 'Diagnostic completed - no more questions available',
                'redirect_url': f'/big-diagnostic/results/{diagnostic_session.id}'
            })
        
        diagnostic_session.current_question_id = next_question.id
        db.session.commit()
        
        # Calculate session info
        session_info = {
            'questions_answered': diagnostic_session.questions_answered,
            'correct_answers': diagnostic_session.correct_answers,
            'current_ability': irt_engine.current_ability_estimate,
            'confidence_interval': irt_engine.get_confidence_interval(),
            'domain_abilities': irt_engine.get_domain_abilities(),
            'estimated_questions_remaining': irt_engine.estimate_questions_remaining()
        }
        
        return safe_jsonify({
            'success': True,
            'question': next_question.to_dict(),
            'session_info': session_info,
            'progress': irt_engine.get_progress_percentage()
        })
        
    except Exception as e:
        logger.error(f"Error getting next question: {str(e)}")
        return safe_jsonify({
            'success': False,
            'error': 'Failed to get next question'
        }), 500

@diagnostic_bp.route('/submit-answer/<int:session_id>', methods=['POST'])
@login_required
def submit_answer(session_id):
    print(f"🔍 ОТЛАДКА: submit_answer вызвана для session_id = {session_id}")
    
    session = DiagnosticSession.query.get_or_404(session_id)
    print(f"🔍 ОТЛАДКА: session.status = {session.status}")
    print(f"🔍 ОТЛАДКА: session.questions_answered = {session.questions_answered}")
    
    if session.status == 'completed':
        print(f"🔍 ОТЛАДКА: сессия уже завершена, редирект на результаты")
        return redirect(url_for('diagnostic.show_results', session_id=session_id))
    
    user_answer = request.form.get('answer')
    print(f"🔍 ОТЛАДКА: user_answer = {user_answer}")
    
    # Вычисляем правильность ответа
    from models import Question
    question = Question.query.get(session.current_question_id)
    print(f"🔍 ОТЛАДКА: question = {question}")
    print(f"🔍 ОТЛАДКА: question.correct_answer_index = {question.correct_answer_index if question else 'None'}")
    
    is_correct = (int(user_answer) == question.correct_answer_index) if question else False
    print(f"🔍 ОТЛАДКА: is_correct = {is_correct}")
    
    # Сохраняем ответ пользователя
    from models import DiagnosticResponse
    response = DiagnosticResponse(
        session_id=session.id,
        question_id=session.current_question_id,
        selected_answer=user_answer,
        is_correct=is_correct
    )
    db.session.add(response)
    session.questions_answered += 1
    
    print(f"🔍 ОТЛАДКА: ответ сохранен, questions_answered = {session.questions_answered}")
    
    # ===== УПРОЩЕННЫЙ IRT КОД - ОБНОВЛЕНИЕ ABILITY =====
    try:
        # Initialize IRT engine and update ability estimate
        from utils.irt_engine import IRTEngine
        irt = IRTEngine(session)
        irt_result = irt.update_ability_estimate(response)
        
        print(f"🎯 IRT Updated: ability={irt_result['ability']:.3f}, SE={irt_result['se']:.3f}")
        
    except Exception as e:
        print(f"❌ IRT Error: {e}")
        # Don't break the flow if IRT fails
        pass
    
    # Проверяем завершён ли тест
    # Получаем информацию о типе диагностики из session_data
    session_data = session.get_session_data()
    diagnostic_type = session_data.get('diagnostic_type', 'express')
    print(f"🔍 ОТЛАДКА: diagnostic_type = {diagnostic_type}")
    
    # Определяем максимальное количество вопросов для каждого типа
    max_questions = {
        'express': 25,
        'preliminary': 75, 
        'readiness': 130
    }.get(diagnostic_type, 25)
    
    print(f"🔍 ОТЛАДКА: max_questions = {max_questions}")
    print(f"🔍 ОТЛАДКА: questions_answered >= max_questions = {session.questions_answered >= max_questions}")
    
    if session.questions_answered >= max_questions:
        print(f"🔍 ОТЛАДКА: достигнут лимит вопросов, завершаем сессию")
        session.status = 'completed'
        session.completed_at = datetime.now(timezone.utc)
        db.session.commit()
        print(f"🔍 ОТЛАДКА: сессия помечена как completed")
        return redirect(url_for('diagnostic.show_results', session_id=session_id))
    else:
        print(f"🔍 ОТЛАДКА: продолжаем диагностику")
        # Выбираем следующий вопрос
        # IRTEngine уже импортирован выше в try блоке
        irt = IRTEngine(session)
        next_question = irt.select_next_question()
        print(f"🔍 ОТЛАДКА: next_question = {next_question}")
        
        if next_question:
            session.current_question_id = next_question.id
            db.session.commit()
            print(f"🔍 ОТЛАДКА: следующий вопрос установлен, редирект")
            return redirect(url_for('diagnostic.show_question', session_id=session_id))
        else:
            # Больше нет доступных вопросов - завершаем диагностику
            print(f"🔍 ОТЛАДКА: нет доступных вопросов, завершаем сессию")
            session.status = 'completed'
            session.completed_at = datetime.now(timezone.utc)
            db.session.commit()
            print(f"🔍 ОТЛАДКА: сессия помечена как completed")
            return redirect(url_for('diagnostic.show_results', session_id=session_id))


@diagnostic_bp.route('/results/<int:session_id>')
@login_required
@validate_session
def show_results(session_id):
    """Show diagnostic results with modern UI"""
    print(f"🔍 ОТЛАДКА: show_results вызвана для session_id = {session_id}")
    
    # Получаем язык из сессии или используем дефолтный
    lang = session.get('lang', 'nl')
    
    try:
        diagnostic_session = g.current_session
        print(f"🔍 ОТЛАДКА: diagnostic_session = {diagnostic_session}")
        print(f"🔍 ОТЛАДКА: diagnostic_session.status = {diagnostic_session.status}")
        print(f"🔍 ОТЛАДКА: diagnostic_session.questions_answered = {diagnostic_session.questions_answered}")
        
        if diagnostic_session.status != 'completed':
            print(f"🔍 ОТЛАДКА: сессия не завершена, возвращаем ошибку 400")
            return safe_jsonify({
                'success': False,
                'error': 'Session not completed'
            }), 400
        
        print(f"🔍 ОТЛАДКА: сессия завершена, генерируем результаты")
        
        # Generate comprehensive results
        results = diagnostic_session.generate_results()
        print(f"🔍 ОТЛАДКА: results = {results}")
        
        # Calculate overall score and readiness level
        overall_score = int(results.get('readiness_percentage', 0))
        readiness_level = 'ready' if overall_score >= 80 else 'almost_ready' if overall_score >= 60 else 'in_progress'
        
        # Prepare domain data for new interface
        domains = []
        domain_statistics = results.get('domain_statistics', {})
        
        for domain_code, domain_data in domain_statistics.items():
            if domain_data.get('has_data', False):
                # Get domain info
                domain_info = BIGDomain.query.filter_by(code=domain_code).first()
                domain_name = domain_info.name if domain_info else domain_code
                
                # Calculate domain score
                domain_score = int(domain_data.get('accuracy_percentage', 0))
                
                # Generate chart data (simulated progression)
                chart_data = []
                base_score = max(domain_score - 20, 0)
                for i in range(5):
                    if i == 0:
                        chart_data.append(base_score)
                    elif i == 4:
                        chart_data.append(domain_score)
                    else:
                        chart_data.append(base_score + (domain_score - base_score) * (i / 4))
                
                # Determine strengths and weaknesses
                strengths = []
                weaknesses = []
                
                if domain_score >= 80:
                    strengths.append(t('excellent_understanding_basics', lang))
                elif domain_score >= 60:
                    strengths.append(t('good_basic_understanding', lang))
                else:
                    weaknesses.append(t('need_study_basics', lang))
                
                if domain_score < 70:
                    weaknesses.append(t('need_additional_practice', lang))
                
                domains.append({
                    'name': domain_name,
                    'code': domain_code,
                    'score': domain_score,
                    'progress': domain_score,
                    'questionsAnswered': domain_data.get('questions_answered', 0),
                    'correctAnswers': domain_data.get('correct_answers', 0),
                    'strengths': strengths,
                    'weaknesses': weaknesses,
                    'chartData': chart_data
                })
        
        # Generate recommendations
        recommendations = []
        weak_domains = [d for d in domains if d['score'] < 70]
        strong_domains = [d for d in domains if d['score'] >= 80]
        
        # High priority recommendations for weak domains
        for domain in weak_domains[:2]:
            recommendations.append({
                'priority': 'high',
                'title': t('focus_on_domain', lang).format(domain_name=domain["name"]),
                'description': t('weak_domain_recommendation', lang).format(
                    domain_name=domain["name"], 
                    score=domain["score"]
                ),
                'timeEstimate': t('time_estimate_4_6_weeks', lang),
                'modules': [
                    t('basics_of_domain', lang).format(domain_name=domain["name"]), 
                    t('practice_of_domain', lang).format(domain_name=domain["name"])
                ]
            })
        
        # Medium priority for domains needing improvement
        medium_domains = [d for d in domains if 70 <= d['score'] < 80]
        for domain in medium_domains[:2]:
            recommendations.append({
                'priority': 'medium',
                'title': t('improve_domain', lang).format(domain_name=domain["name"]),
                'description': t('medium_domain_recommendation', lang).format(
                    domain_name=domain["name"], 
                    score=domain["score"]
                ),
                'timeEstimate': t('time_estimate_2_3_weeks', lang),
                'modules': [t('advanced_study_of_domain', lang).format(domain_name=domain["name"])]
            })
        
        # Positive feedback for strong domains
        for domain in strong_domains[:2]:
            recommendations.append({
                'priority': 'low',
                'title': t('maintain_domain', lang).format(domain_name=domain["name"]),
                'description': t('strong_domain_recommendation', lang).format(
                    domain_name=domain["name"], 
                    score=domain["score"]
                ),
                'timeEstimate': t('time_estimate_1_2_weeks', lang),
                'modules': [t('review_of_domain', lang).format(domain_name=domain["name"])]
            })
        
        # Prepare diagnostic data for template
        diagnostic_data = {
            'session_id': diagnostic_session.id,
            'overall_score': overall_score,
            'readiness_level': readiness_level,
            'total_questions': diagnostic_session.questions_answered,
            'correct_answers': diagnostic_session.correct_answers,
            'accuracy_percentage': round((diagnostic_session.correct_answers / diagnostic_session.questions_answered) * 100, 1) if diagnostic_session.questions_answered > 0 else 0.0,
            'domains': domains,
            'recommendations': recommendations,
            'results': results
        }
        
        print(f"🔍 ОТЛАДКА: diagnostic_data подготовлен, рендерим шаблон")
        
        return render_template('assessment/results.html', 
                             diagnostic_data=diagnostic_data,
                             session_id=session_id,
                             lang=lang)
                             
    except Exception as e:
        print(f"❌ Ошибка в show_results: {e}")
        import traceback
        traceback.print_exc()
        return safe_jsonify({
            'success': False,
            'error': f'Error generating results: {str(e)}'
        }), 500

@diagnostic_bp.route('/session/<int:session_id>/status')
@login_required
@validate_session
def get_session_status(session_id):
    """Get current session status"""
    try:
        diagnostic_session = g.current_session
        
        return safe_jsonify({
            'success': True,
            'session': {
                'id': diagnostic_session.id,
                'status': diagnostic_session.status,
                'questions_answered': diagnostic_session.questions_answered,
                'correct_answers': diagnostic_session.correct_answers,
                'current_ability': diagnostic_session.current_ability,
                'started_at': diagnostic_session.started_at.isoformat() if diagnostic_session.started_at else None,
                'completed_at': diagnostic_session.completed_at.isoformat() if diagnostic_session.completed_at else None
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting session status: {str(e)}")
        return safe_jsonify({
            'success': False,
            'error': 'Failed to get session status'
        }), 500

@diagnostic_bp.route('/session/<int:session_id>/end', methods=['POST'])
@login_required
@validate_session
def end_session(session_id):
    """End diagnostic session"""
    try:
        diagnostic_session = g.current_session
        
        # Проверяем статус сессии
        if diagnostic_session.status == 'completed':
            return safe_jsonify({
                'success': True,
                'message': 'Session already completed'
            })
        
        if diagnostic_session.status == 'abandoned':
            return safe_jsonify({
                'success': True,
                'message': 'Session already abandoned'
            })
        
        # Завершаем активную сессию
        if diagnostic_session.status == 'active':
            diagnostic_session.status = 'abandoned'
            diagnostic_session.completed_at = datetime.now(timezone.utc)
            db.session.commit()
            
            logger.info(f"Ended diagnostic session {session_id}")
        
        return safe_jsonify({
            'success': True,
            'message': 'Session ended successfully',
            'session_id': session_id,
            'status': diagnostic_session.status
        })
        
    except Exception as e:
        logger.error(f"Error ending session {session_id}: {str(e)}")
        db.session.rollback()
        return safe_jsonify({
            'success': False,
            'error': 'Failed to end session',
            'session_id': session_id
        }), 500

@diagnostic_bp.route('/restart', methods=['POST'])
@login_required
@rate_limit(requests_per_minute=10)
def restart_diagnostic():
    """Restart diagnostic session (general endpoint)"""
    try:
        # Find active session
        active_session = DiagnosticSession.query.filter_by(
            user_id=current_user.id,
            status='active'
        ).first()
        
        if not active_session:
            return safe_jsonify({
                'success': False,
                'error': 'No active session found'
            }), 404
        
        # End current session
        active_session.status = 'abandoned'
        active_session.completed_at = datetime.now(timezone.utc)
        db.session.commit()
        
        # Get diagnostic type from old session
        old_session_data = active_session.get_session_data()
        diagnostic_type = old_session_data.get('diagnostic_type', 'express')
        
        # Create new session
        new_session = DiagnosticSession.create_session(
            user_id=current_user.id,
            session_type='adaptive_diagnostic',
            ip_address=request.remote_addr
        )
        
        # Сохранить тип диагностики в новой сессии
        session_data = {
            'diagnostic_type': diagnostic_type,
            'questions_per_domain': 1 if diagnostic_type == 'express' else (3 if diagnostic_type == 'preliminary' else 5),
            'estimated_total_questions': 25 if diagnostic_type == 'express' else (75 if diagnostic_type == 'preliminary' else 130)
        }
        new_session.set_session_data(session_data)
        
        # Get first question using IRT with diagnostic type
        irt_engine = IRTEngine(diagnostic_type=diagnostic_type)
        first_question = irt_engine.select_initial_question()
        
        new_session.current_question_id = first_question.id
        new_session.started_at = datetime.now(timezone.utc)
        db.session.commit()
        
        logger.info(f"Restarted diagnostic session: {new_session.id}")
        
        return safe_jsonify({
            'success': True,
            'session_id': new_session.id,
            'redirect_url': url_for('diagnostic.show_question', session_id=new_session.id)
        })
        
    except Exception as e:
        logger.error(f"Error restarting session: {str(e)}")
        return safe_jsonify({
            'success': False,
            'error': 'Failed to restart session'
        }), 500

@diagnostic_bp.route('/session/<int:session_id>/restart', methods=['POST'])
@login_required
@validate_session
def restart_session(session_id):
    """Restart diagnostic session"""
    try:
        diagnostic_session = g.current_session
        
        # End current session
        diagnostic_session.status = 'abandoned'
        diagnostic_session.completed_at = datetime.now(timezone.utc)
        db.session.commit()
        
        # Get diagnostic type from old session
        old_session_data = diagnostic_session.get_session_data()
        diagnostic_type = old_session_data.get('diagnostic_type', 'express')
        
        # Create new session
        new_session = DiagnosticSession.create_session(
            user_id=current_user.id,
            session_type='adaptive_diagnostic',
            ip_address=request.remote_addr
        )
        
        # Сохранить тип диагностики в новой сессии
        session_data = {
            'diagnostic_type': diagnostic_type,
            'questions_per_domain': 1 if diagnostic_type == 'express' else (3 if diagnostic_type == 'preliminary' else 5),
            'estimated_total_questions': 25 if diagnostic_type == 'express' else (75 if diagnostic_type == 'preliminary' else 130)
        }
        new_session.set_session_data(session_data)
        
        # Get first question using IRT with diagnostic type
        irt_engine = IRTEngine(diagnostic_type=diagnostic_type)
        first_question = irt_engine.select_initial_question()
        
        new_session.current_question_id = first_question.id
        new_session.started_at = datetime.now(timezone.utc)
        db.session.commit()
        
        logger.info(f"Restarted diagnostic session: {new_session.id}")
        
        return safe_jsonify({
            'success': True,
            'session_id': new_session.id,
            'question': first_question.to_dict(),
            'session_info': {
                'questions_answered': 0,
                'correct_answers': 0,
                'current_ability': 0.0,
                'confidence_interval': [0.0, 1.0],
                'domain_abilities': {},
                'estimated_questions_remaining': 50
            },
            'progress': 0
        })
        
    except Exception as e:
        logger.error(f"Error restarting session: {str(e)}")
        return safe_jsonify({
            'success': False,
            'error': 'Failed to restart session'
        }), 500

@diagnostic_bp.route('/questions/<int:question_id>')
@login_required
@rate_limit(requests_per_minute=60)
def get_question_details(question_id):
    """Get detailed question information"""
    try:
        question = Question.query.get_or_404(question_id)
        
        return safe_jsonify({
            'success': True,
            'question': question.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error getting question details: {str(e)}")
        return safe_jsonify({
            'success': False,
            'error': 'Failed to get question details'
        }), 500

@diagnostic_bp.route('/generate-learning-plan', methods=['POST'])
@login_required
@rate_limit(requests_per_minute=10)
def generate_learning_plan():
    """Generate personalized learning plan based on diagnostic results"""
    try:
        data = request.get_json()
        if not data:
            raise BadRequest('Invalid request data')
        
        session_id = data.get('session_id')
        study_hours_per_week = data.get('study_hours_per_week', 20)
        exam_date = data.get('exam_date')
        
        if not session_id:
            raise BadRequest('Session ID required')
        
        # Get diagnostic session
        diagnostic_session = DiagnosticSession.query.get(session_id)
        if not diagnostic_session:
            raise BadRequest('Diagnostic session not found')
        
        if diagnostic_session.user_id != current_user.id:
            raise Unauthorized('Access denied')
        
        # Generate results if not already generated
        results = diagnostic_session.generate_results()
        
        # Create or update learning plan
        existing_plan = PersonalLearningPlan.query.filter_by(
            user_id=current_user.id,
            status='active'
        ).first()
        
        if existing_plan:
            plan = existing_plan
        else:
            plan = PersonalLearningPlan(user_id=current_user.id)
            db.session.add(plan)
        
        # Update plan with diagnostic results
        plan.current_ability = results['final_ability']
        plan.target_ability = 0.5  # Target for exam readiness
        plan.study_hours_per_week = study_hours_per_week
        
        if exam_date:
            plan.exam_date = datetime.strptime(exam_date, '%Y-%m-%d').date()
        
        # Set domain analysis
        plan.set_domain_analysis(results['domain_abilities'])
        plan.set_weak_domains(results['weak_domains'])
        plan.set_strong_domains(results['strong_domains'])
        
        # Generate study schedule
        schedule = generate_study_schedule(results, study_hours_per_week, exam_date)
        plan.set_study_schedule(schedule)
        
        # Generate milestones
        milestones = generate_milestones(results, study_hours_per_week, exam_date)
        plan.set_milestones(milestones)
        
        # Calculate estimated readiness
        plan.estimated_readiness = plan.calculate_readiness()
        
        db.session.commit()
        
        # Create study sessions
        create_study_sessions(plan, schedule)
        
        logger.info(f"Generated learning plan {plan.id} for user {current_user.id}")
        
        return safe_jsonify({
            'success': True,
            'plan_id': plan.id,
            'plan_summary': {
                'current_ability': plan.current_ability,
                'target_ability': plan.target_ability,
                'estimated_readiness': plan.estimated_readiness,
                'weak_domains': plan.get_weak_domains(),
                'strong_domains': plan.get_strong_domains(),
                'total_sessions': len(schedule.get('weekly_schedule', [])),
                'estimated_weeks': len(schedule.get('weekly_schedule', []))
            }
        })
        
    except Exception as e:
        logger.error(f"Error generating learning plan: {str(e)}")
        return safe_jsonify({
            'success': False,
            'error': 'Failed to generate learning plan'
        }), 500

def generate_study_schedule(results, study_hours_per_week, exam_date=None):
    """Generate personalized study schedule"""
    weak_domains = results.get('weak_domains', [])
    strong_domains = results.get('strong_domains', [])
    current_ability = results.get('final_ability', 0.0)
    
    # Calculate total weeks needed
    if exam_date:
        exam_date_obj = datetime.strptime(exam_date, '%Y-%m-%d').date()
        weeks_until_exam = max(1, (exam_date_obj - datetime.now().date()).days // 7)
    else:
        # Estimate based on current ability and weak domains
        weeks_until_exam = max(8, len(weak_domains) * 2 + int((0.5 - current_ability) * 10))
    
    # Generate weekly schedule
    weekly_schedule = []
    
    for week in range(weeks_until_exam):
        week_schedule = {
            'week_number': week + 1,
            'focus_domains': [],
            'daily_sessions': [],
            'milestone_test': week % 4 == 0,  # Test every 4 weeks
            'estimated_hours': study_hours_per_week
        }
        
        # Focus on weak domains first
        if week < len(weak_domains):
            week_schedule['focus_domains'] = [weak_domains[week]]
        elif weak_domains:
            # Rotate through weak domains
            week_schedule['focus_domains'] = [weak_domains[week % len(weak_domains)]]
        
        # Generate daily sessions
        daily_sessions = []
        for day in range(7):
            if day < 5:  # Weekdays
                session = {
                    'day': day + 1,
                    'type': 'theory' if day % 2 == 0 else 'practice',
                    'duration': study_hours_per_week / 5,  # Distribute hours across weekdays
                    'focus_domains': week_schedule['focus_domains']
                }
            else:  # Weekend
                session = {
                    'day': day + 1,
                    'type': 'review',
                    'duration': study_hours_per_week / 10,  # Less time on weekends
                    'focus_domains': week_schedule['focus_domains']
                }
            daily_sessions.append(session)
        
        week_schedule['daily_sessions'] = daily_sessions
        weekly_schedule.append(week_schedule)
    
    return {
        'total_weeks': weeks_until_exam,
        'weekly_schedule': weekly_schedule,
        'total_hours': weeks_until_exam * study_hours_per_week
    }

def generate_milestones(results, study_hours_per_week, exam_date=None):
    """Generate learning milestones"""
    weak_domains = results.get('weak_domains', [])
    current_ability = results.get('final_ability', 0.0)
    
    milestones = []
    
    # Calculate target ability improvements
    target_ability = 0.5
    ability_gap = target_ability - current_ability
    
    # Determine total weeks based on exam date or default
    if exam_date:
        exam_date_obj = datetime.strptime(exam_date, '%Y-%m-%d').date()
        total_weeks = max(1, (exam_date_obj - datetime.now().date()).days // 7)
    else:
        total_weeks = 8  # Default to 8 weeks to match schedule
    
    # Weekly milestones - only for the actual duration
    for week in range(1, total_weeks + 1):
        milestone = {
            'week': week,
            'type': 'progress_check',
            'description': f'Неделя {week}: Проверка прогресса',
            'target_ability': min(target_ability, current_ability + (ability_gap * week / total_weeks)),
            'focus_domains': weak_domains[week % len(weak_domains)] if weak_domains else []
        }
        milestones.append(milestone)
    
    # Domain-specific milestones - distribute across available weeks
    for i, domain in enumerate(weak_domains):
        week_number = min((i + 1) * 2, total_weeks)  # Don't exceed total weeks
        milestone = {
            'week': week_number,
            'type': 'domain_mastery',
            'description': f'Освоение домена: {domain}',
            'target_ability': current_ability + 0.2,
            'focus_domains': [domain]
        }
        milestones.append(milestone)
    
    # Final exam milestone
    if exam_date:
        milestones.append({
            'week': total_weeks,
            'type': 'final_exam',
            'description': 'Финальный экзамен BI-toets',
            'target_ability': target_ability,
            'focus_domains': weak_domains
        })
    
    return milestones

def create_study_sessions(plan, schedule):
    """Create individual study sessions for the plan"""
    # Clear existing sessions
    plan.study_sessions.delete()
    
    weekly_schedule = schedule.get('weekly_schedule', [])
    
    for week_idx, week in enumerate(weekly_schedule):
        for day_idx, day_session in enumerate(week['daily_sessions']):
            # Create study session
            study_session = StudySession(
                learning_plan_id=plan.id,
                session_type=day_session['type'],
                planned_duration=day_session['duration'] * 60,  # Convert to minutes
                status='planned'
            )
            
            # Set domain if specified
            if day_session['focus_domains']:
                domain = BIGDomain.query.filter_by(code=day_session['focus_domains'][0]).first()
                if domain:
                    study_session.domain_id = domain.id
            
            db.session.add(study_session)
    
    db.session.commit()

@diagnostic_bp.errorhandler(BadRequest)
def handle_bad_request(error):
    """Handle bad request errors"""
    return safe_jsonify({
        'success': False,
        'error': str(error.description)
    }), 400

@diagnostic_bp.errorhandler(Unauthorized)
def handle_unauthorized(error):
    """Handle unauthorized errors"""
    return safe_jsonify({
        'success': False,
        'error': 'Authentication required'
    }), 401

@diagnostic_bp.errorhandler(TooManyRequests)
def handle_rate_limit(error):
    """Handle rate limit errors"""
    return safe_jsonify({
        'success': False,
        'error': 'Rate limit exceeded. Please try again later.'
    }), 429

@diagnostic_bp.errorhandler(404)
def handle_not_found(error):
    """Handle not found errors"""
    return safe_jsonify({
        'success': False,
        'error': 'Resource not found'
    }), 404

@diagnostic_bp.errorhandler(500)
def handle_internal_error(error):
    """Handle internal server errors"""
    logger.error(f"Internal server error: {str(error)}")
    return safe_jsonify({
        'success': False,
        'error': 'Internal server error'
    }), 500 

# ========================================
# DOMAIN-SPECIFIC ENDPOINTS
# ========================================

@diagnostic_bp.route('/api/domains')
@login_required
@rate_limit(requests_per_minute=60)
def get_all_domains():
    """Получить список всех доменов"""
    try:
        domains = BIGDomain.query.filter_by(is_active=True).order_by(BIGDomain.weight_percentage.desc()).all()
        domain_data = []
        for domain in domains:
            question_count = Question.query.filter_by(domain=domain.code).count()
            user_stats = get_user_domain_statistics(current_user.id, domain.code)
            domain_data.append({
                'code': domain.code,
                'name': domain.name,
                'description': domain.description,
                'weight': domain.weight_percentage,
                'question_count': question_count,
                'user_stats': user_stats
            })
        return safe_jsonify({
            'success': True,
            'domains': domain_data
        })
    except Exception as e:
        logger.error(f"Error getting domains: {e}")
        return safe_jsonify({
            'success': False,
            'error': 'Failed to load domains'
        }), 500

@diagnostic_bp.route('/api/domains/<domain_code>')
@login_required
@rate_limit(requests_per_minute=60)
def get_domain_info(domain_code):
    """Получить информацию о конкретном домене"""
    try:
        domain = BIGDomain.query.filter_by(code=domain_code).first()
        if not domain:
            return safe_jsonify({'success': False, 'error': 'Domain not found'}), 404
        
        # Статистика пользователя по домену
        user_stats = get_user_domain_statistics(current_user.id, domain_code)
        
        # Статистика домена
        question_count = Question.query.filter_by(domain=domain_code).count()
        
        return safe_jsonify({
            'success': True,
            'domain': {
                'code': domain.code,
                'name': domain.name,
                'description': domain.description,
                'weight': domain.weight_percentage,
                'question_count': question_count,
                'user_stats': user_stats
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting domain info: {e}")
        return safe_jsonify({
            'success': False,
            'error': 'Failed to load domain information'
        }), 500

@diagnostic_bp.route('/api/domains/<domain_code>/start', methods=['POST'])
@login_required
@rate_limit(requests_per_minute=10)
def start_domain_diagnostic(domain_code):
    """Запустить диагностику для конкретного домена"""
    domain = BIGDomain.query.filter_by(code=domain_code).first()
    if not domain:
        return safe_jsonify({'success': False, 'error': 'Domain not found'}), 404
    
    # Создать сессию диагностики для домена
    session = DiagnosticSession(
        user_id=current_user.id,
        session_type='domain_diagnostic',
        target_questions=20  # Меньше вопросов для доменной диагностики
    )
    session.set_session_data({
        'domain_code': domain_code,
        'domain_name': domain.name
    })
    db.session.add(session)
    db.session.commit()
    
    # Инициализировать IRT движок
    irt_engine = IRTEngine(session)
    first_question = irt_engine.select_next_question_by_domain(domain_code)
    
    if not first_question:
        return safe_jsonify({'success': False, 'error': 'No questions available for this domain'}), 400
    
    # Обновить сессию с первым вопросом
    session_data = session.get_session_data()
    session_data['current_question_id'] = first_question.id
    session_data['questions_asked'] = 1
    session.set_session_data(session_data)
    db.session.commit()
    
    return safe_jsonify({
        'success': True,
        'session_id': session.id,
        'question': format_question_for_frontend(first_question),
        'progress': {
            'current': 1,
            'total': session.target_questions,
            'percentage': 5
        }
    })

@diagnostic_bp.route('/domain/<domain_code>')
@login_required
def domain_diagnostic_page(domain_code):
    """Страница доменной диагностики"""
    domain = BIGDomain.query.filter_by(code=domain_code).first()
    if not domain:
        flash('Domain not found', 'error')
        return redirect(url_for('diagnostic_bp.start_diagnostic'))
    
    return render_template('assessment/domain_diagnostic.html', domain=domain)
    """Запустить диагностику для конкретного домена"""
    try:
        domain = BIGDomain.query.filter_by(code=domain_code).first()
        if not domain:
            return safe_jsonify({'success': False, 'error': 'Domain not found'}), 404
        
        # Проверить, есть ли активная сессия
        active_session = DiagnosticSession.query.filter_by(
            user_id=current_user.id,
            status='active'
        ).first()
        
        if active_session:
            return safe_jsonify({
                'success': False,
                'has_active_session': True,
                'active_session': {
                    'id': active_session.id,
                    'questions_answered': active_session.questions_answered,
                    'correct_answers': active_session.correct_answers,
                    'current_ability': active_session.current_ability,
                    'started_at': active_session.started_at.isoformat()
                }
            }), 400
        
        # Создать сессию диагностики для домена
        session_data = {
            'domain_code': domain_code,
            'domain_name': domain.name,
            'session_type': 'domain_diagnostic',
            'target_questions': 20,  # Меньше вопросов для доменной диагностики
            'questions_asked': 0,
            'current_question_id': None
        }
        
        diagnostic_session = DiagnosticSession(
            user_id=current_user.id,
            session_type='domain_diagnostic',
            test_length=20,
            ip_address=request.remote_addr
        )
        diagnostic_session.set_session_data(session_data)
        
        db.session.add(diagnostic_session)
        db.session.commit()
        
        # Инициализировать IRT движок
        irt_engine = IRTEngine(diagnostic_session)
        first_question = irt_engine.select_next_question_by_domain(domain_code)
        
        if not first_question:
            return safe_jsonify({'success': False, 'error': 'No questions available for this domain'}), 400
        
        # Обновить сессию с первым вопросом
        session_data['current_question_id'] = first_question.id
        session_data['questions_asked'] = 1
        diagnostic_session.set_session_data(session_data)
        diagnostic_session.current_question_id = first_question.id
        db.session.commit()
        
        return safe_jsonify({
            'success': True,
            'session_id': diagnostic_session.id,
            'question': format_question_for_frontend(first_question),
            'progress': {
                'current': 1,
                'total': 20,
                'percentage': 5
            },
            'domain': {
                'code': domain_code,
                'name': domain.name
            }
        })
        
    except Exception as e:
        logger.error(f"Error starting domain diagnostic: {e}")
        return safe_jsonify({
            'success': False,
            'error': 'Failed to start domain diagnostic'
        }), 500

def get_user_domain_statistics(user_id: int, domain_code: str) -> dict:
    """Получить статистику пользователя по домену"""
    try:
        # Найти все диагностические сессии пользователя для этого домена
        sessions = DiagnosticSession.query.filter_by(
            user_id=user_id,
            session_type='domain_diagnostic'
        ).all()
        
        domain_sessions = []
        for session in sessions:
            try:
                session_data = session.get_session_data()
                if session_data.get('domain_code') == domain_code:
                    domain_sessions.append(session)
            except (json.JSONDecodeError, KeyError):
                continue
        
        if not domain_sessions:
            return {
                'sessions_completed': 0,
                'average_score': None,  # Нет данных вместо 0
                'current_ability': None,  # Нет данных вместо 0.0
                'questions_answered': 0,
                'last_session_date': None,
                'has_data': False  # Флаг отсутствия данных
            }
        
        # Рассчитать статистику
        total_score = 0
        total_questions = 0
        abilities = []
        completed_sessions = 0
        
        for session in domain_sessions:
            if session.status == 'completed':
                completed_sessions += 1
                total_questions += session.questions_answered
                if session.current_ability is not None:
                    abilities.append(session.current_ability)
                
                # Рассчитать процент правильных ответов
                if session.questions_answered > 0:
                    score_percentage = (session.correct_answers / session.questions_answered) * 100
                    total_score += score_percentage
        
        # Проверить, есть ли достаточно данных для статистики
        if completed_sessions == 0 or total_questions == 0:
            return {
                'sessions_completed': 0,
                'average_score': None,
                'current_ability': None,
                'questions_answered': 0,
                'last_session_date': None,
                'has_data': False
            }
        
        return {
            'sessions_completed': completed_sessions,
            'average_score': round(total_score / max(completed_sessions, 1), 1),
            'current_ability': round(sum(abilities) / max(len(abilities), 1), 2) if abilities else None,
            'questions_answered': total_questions,
            'last_session_date': max([s.started_at for s in domain_sessions]).isoformat() if domain_sessions else None,
            'has_data': True
        }
        
    except Exception as e:
        logger.error(f"Error getting user domain statistics: {e}")
        return {
            'sessions_completed': 0,
            'average_score': None,
            'current_ability': None,
            'questions_answered': 0,
            'last_session_date': None,
            'has_data': False
        }

def format_question_for_frontend(question: Question) -> dict:
    """Форматировать вопрос для фронтенда"""
    return {
        'id': question.id,
        'text': question.text,
        'options': question.options,
        'category': question.category,
        'domain': question.domain,
        'difficulty_level': question.difficulty_level,
        'image_url': question.image_url,
        'tags': question.tags or []
    } 

@diagnostic_bp.route('/diagnostic-types', methods=['GET'])
@login_required
@rate_limit(requests_per_minute=60)
def get_diagnostic_types():
    """Получить информацию о доступных типах диагностики"""
    try:
        # Получить количество доменов
        total_domains = BIGDomain.query.filter_by(is_active=True).count()
        
        diagnostic_types = {
            'express': {
                'name': 'Экспресс диагностика',
                'description': 'Быстрая оценка по всем доменам',
                'questions_per_domain': 1,
                'total_questions': total_domains,
                'estimated_time': '15-20 минут',
                'accuracy': 'Базовая',
                'suitable_for': 'Быстрая оценка, первое знакомство с системой'
            },
            'preliminary': {
                'name': 'Предварительная диагностика',
                'description': 'Детальная оценка с высокой точностью',
                'questions_per_domain': 3,
                'total_questions': total_domains * 3,
                'estimated_time': '45-60 минут',
                'accuracy': 'Высокая',
                'suitable_for': 'Подготовка к экзамену, детальный анализ'
            },
            'readiness': {
                'name': 'Диагностика готовности',
                'description': 'Полная диагностика для оценки готовности к экзамену',
                'questions_per_domain': 5,
                'total_questions': total_domains * 5,
                'estimated_time': '90-120 минут',
                'accuracy': 'Экзаменационная',
                'suitable_for': 'Финальная подготовка к экзамену, полная оценка'
            }
        }
        
        return safe_jsonify({
            'success': True,
            'diagnostic_types': diagnostic_types,
            'total_domains': total_domains
        })
        
    except Exception as e:
        logger.error(f"Error getting diagnostic types: {e}")
        return safe_jsonify({
            'success': False,
            'error': 'Failed to load diagnostic types'
        }), 500

@diagnostic_bp.route('/choose-type')
@login_required
def choose_diagnostic_type():
    """Страница выбора типа диагностики"""
    # Получаем язык из сессии или используем дефолтный
    lang = session.get('lang', 'nl')
    return render_template('assessment/diagnostic_type_selector.html', lang=lang)

@diagnostic_bp.route('/question/<int:session_id>', methods=['GET'])
@login_required
def show_question(session_id):
    try:
        diagnostic_session = DiagnosticSession.query.get_or_404(session_id)
        
        # Проверяем, что сессия активна
        if diagnostic_session.status != 'active':
            flash('Диагностическая сессия завершена', 'warning')
            return redirect(url_for('diagnostic.choose_diagnostic_type'))
        
        # Получить текущий вопрос для пользователя
        if not diagnostic_session.current_question_id:
            # Если нет текущего вопроса, выбираем первый
            from utils.irt_engine import IRTEngine
            irt = IRTEngine()
            first_question = irt.select_initial_question()
            if not first_question:
                flash('Нет доступных вопросов', 'error')
                return redirect(url_for('diagnostic.choose_diagnostic_type'))
            
            diagnostic_session.current_question_id = first_question.id
            db.session.commit()
        
        # Получаем вопрос
        question = Question.query.get(diagnostic_session.current_question_id)
        if not question:
            flash('Вопрос не найден', 'error')
            return redirect(url_for('diagnostic.choose_diagnostic_type'))
        
        # Для шаблона нужны номер вопроса, всего вопросов и т.д.
        question_num = diagnostic_session.questions_answered + 1
        
        # Получаем общее количество вопросов
        session_data = diagnostic_session.get_session_data()
        total_questions = session_data.get('estimated_total_questions', 25)
        
        # Добавляем атрибут question_text для совместимости с шаблоном
        question.question_text = question.text
        
        # Добавляем оставшееся время
        remaining_time = 3600  # 1 час по умолчанию
        if diagnostic_session.started_at:
            # Убеждаемся, что оба времени имеют часовой пояс
            current_time = datetime.now(timezone.utc)
            started_time = diagnostic_session.started_at
            if started_time.tzinfo is None:
                # Если started_at наивное время, добавляем UTC
                started_time = started_time.replace(tzinfo=timezone.utc)
            elapsed = (current_time - started_time).total_seconds()
            remaining_time = max(0, 3600 - int(elapsed))
        
        return render_template('assessment/question.html', 
                             diagnostic_session=diagnostic_session, 
                             question=question, 
                             question_num=question_num, 
                             total_questions=total_questions, 
                             session_id=session_id,
                             remaining_time=remaining_time)
                             
    except Exception as e:
        logger.error(f"Error showing question: {str(e)}")
        flash('Ошибка при загрузке вопроса', 'error')
        return redirect(url_for('diagnostic.choose_diagnostic_type')) 

@diagnostic_bp.route('/session/terminate', methods=['POST'])
@login_required
@rate_limit(requests_per_minute=10)
def terminate_active_session():
    """Terminate user's active diagnostic session"""
    try:
        # Находим активную сессию пользователя
        active_session = DiagnosticSession.query.filter_by(
            user_id=current_user.id,
            status='active'
        ).first()
        
        if active_session:
            # Завершаем сессию
            active_session.status = 'terminated'
            active_session.completed_at = datetime.now(timezone.utc)
            db.session.commit()
            
            logger.info(f"Terminated active session {active_session.id} for user {current_user.id}")
            
            return safe_jsonify({
                'success': True,
                'message': 'Active session terminated successfully'
            })
        else:
            # Нет активной сессии - это нормально
            return safe_jsonify({
                'success': True,
                'message': 'No active session found'
            })
            
    except Exception as e:
        logger.error(f"Error terminating session: {str(e)}")
        db.session.rollback()
        return safe_jsonify({
            'success': False,
            'error': 'Failed to terminate session'
        }), 500 

@diagnostic_bp.route('/quick-test', methods=['POST'])
@login_required
@rate_limit(requests_per_minute=10)
def quick_test():
    """Quick test endpoint for testing learning planning system"""
    try:
        if not request.is_json:
            return safe_jsonify({'success': False, 'error': 'JSON required'}), 400
        
        data = request.get_json()
        result_type = data.get('result_type', 'random')
        diagnostic_type = data.get('diagnostic_type', 'express')
        
        # Валидация типа результата
        if result_type not in ['high', 'medium', 'low', 'random']:
            result_type = 'random'
        
        # Создаем тестовую сессию
        diagnostic_session = DiagnosticSession.create_session(
            user_id=current_user.id,
            session_type='adaptive_diagnostic',
            ip_address=request.remote_addr
        )
        
        # Сохраняем тип диагностики
        session_data = {
            'diagnostic_type': diagnostic_type,
            'questions_per_domain': 1 if diagnostic_type == 'express' else (3 if diagnostic_type == 'preliminary' else 5),
            'estimated_total_questions': 25 if diagnostic_type == 'express' else (75 if diagnostic_type == 'preliminary' else 130),
            'is_test_session': True,
            'test_result_type': result_type
        }
        diagnostic_session.set_session_data(session_data)
        
        # Генерируем тестовые результаты
        test_results = generate_test_results(result_type, diagnostic_type)
        
        # Сохраняем тестовые ответы
        save_test_responses(diagnostic_session, test_results)
        
        # Завершаем сессию
        diagnostic_session.status = 'completed'
        diagnostic_session.completed_at = datetime.now(timezone.utc)
        diagnostic_session.questions_answered = test_results['total_questions']
        diagnostic_session.correct_answers = test_results['correct_answers']
        diagnostic_session.current_ability = test_results['final_ability']
        
        db.session.commit()
        
        logger.info(f"Quick test session {diagnostic_session.id} created for user {current_user.id} with result type: {result_type}")
        
        return safe_jsonify({
            'success': True,
            'session_id': diagnostic_session.id,
            'redirect_url': url_for('diagnostic.show_results', session_id=diagnostic_session.id)
        })
        
    except Exception as e:
        logger.error(f"Error in quick test: {str(e)}")
        db.session.rollback()
        return safe_jsonify({
            'success': False,
            'error': 'Failed to create test session'
        }), 500

def generate_test_results(result_type, diagnostic_type):
    """Generate test results based on result type"""
    import random
    
    # Определяем количество вопросов
    total_questions = 25 if diagnostic_type == 'express' else (75 if diagnostic_type == 'preliminary' else 130)
    
    # Генерируем результаты в зависимости от типа
    if result_type == 'high':
        correct_answers = int(total_questions * random.uniform(0.8, 0.95))  # 80-95%
        final_ability = random.uniform(1.5, 2.5)  # Высокий уровень
    elif result_type == 'medium':
        correct_answers = int(total_questions * random.uniform(0.5, 0.75))  # 50-75%
        final_ability = random.uniform(0.0, 1.0)  # Средний уровень
    elif result_type == 'low':
        correct_answers = int(total_questions * random.uniform(0.2, 0.45))  # 20-45%
        final_ability = random.uniform(-1.5, 0.0)  # Низкий уровень
    else:  # random
        correct_answers = random.randint(5, total_questions - 5)
        final_ability = random.uniform(-2.0, 2.5)
    
    return {
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'final_ability': final_ability,
        'result_type': result_type
    }

def save_test_responses(diagnostic_session, test_results):
    """Save test responses to database"""
    import random
    
    # Получаем случайные вопросы
    questions = Question.query.limit(test_results['total_questions']).all()
    
    for i, question in enumerate(questions):
        # Определяем правильность ответа на основе желаемого результата
        if test_results['result_type'] == 'high':
            is_correct = random.choices([True, False], weights=[0.85, 0.15])[0]
        elif test_results['result_type'] == 'medium':
            is_correct = random.choices([True, False], weights=[0.6, 0.4])[0]
        elif test_results['result_type'] == 'low':
            is_correct = random.choices([True, False], weights=[0.3, 0.7])[0]
        else:  # random
            is_correct = random.choice([True, False])
        
        # Выбираем ответ
        if is_correct:
            selected_answer = question.correct_answer_index
        else:
            # Выбираем неправильный ответ
            wrong_answers = [j for j in range(4) if j != question.correct_answer_index]
            selected_answer = random.choice(wrong_answers)
        
        # Создаем ответ
        response = DiagnosticResponse(
            session_id=diagnostic_session.id,
            question_id=question.id,
            selected_answer=selected_answer,
            is_correct=is_correct,
            responded_at=datetime.now(timezone.utc)
        )
        db.session.add(response)
    
    db.session.commit() 

@diagnostic_bp.route('/session/<int:session_id>/complete', methods=['POST'])
@login_required
@validate_session
def complete_session(session_id):
    """Force complete diagnostic session"""
    print(f"🔍 ОТЛАДКА: complete_session вызвана для session_id = {session_id}")
    
    try:
        session = g.current_session
        print(f"🔍 ОТЛАДКА: session.status = {session.status}")
        print(f"🔍 ОТЛАДКА: session.questions_answered = {session.questions_answered}")
        
        if session.status == 'completed':
            print(f"🔍 ОТЛАДКА: сессия уже завершена")
            return safe_jsonify({
                'success': True,
                'message': 'Session already completed'
            })
        
        # Принудительно завершаем сессию
        session.status = 'completed'
        session.completed_at = datetime.now(timezone.utc)
        session.termination_reason = 'user_requested'
        
        db.session.commit()
        
        print(f"🔍 ОТЛАДКА: сессия принудительно завершена")
        
        return safe_jsonify({
            'success': True,
            'message': 'Session completed successfully'
        })
        
    except Exception as e:
        print(f"❌ Ошибка в complete_session: {e}")
        import traceback
        traceback.print_exc()
        return safe_jsonify({
            'success': False,
            'error': f'Error completing session: {str(e)}'
        }), 500 

 