"""
Diagnostic Routes for BI-toets System
Flask Blueprint for diagnostic testing with IRT engine integration
"""

from flask import Blueprint, render_template, request, session, current_app, g, flash, redirect, url_for, jsonify
from flask_login import current_user, login_required
from werkzeug.exceptions import BadRequest, Unauthorized, TooManyRequests
from functools import wraps
import time
import logging
import json
from datetime import datetime, timedelta, timezone, date

from models import db, DiagnosticSession, Question, IRTParameters, User, PersonalLearningPlan, StudySession, BIGDomain, DiagnosticResponse
from utils.serializers import safe_jsonify
from utils.irt_engine import IRTEngine
from utils.rate_limiter import RateLimiter
from utils.session_validator import SessionValidator
from utils.translations import t
from utils.irt_calibration import calibration_service
from utils.data_validator import DataValidator, ValidationLevel
from utils.irt_engine import validate_irt_parameters_for_calculation

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

            # Get first question using IRT with diagnostic type BEFORE creating session
            irt_engine = IRTEngine(diagnostic_type=diagnostic_type)
            first_question = irt_engine.select_initial_question()
            
            if not first_question:
                logger.error(f"No questions available for diagnostic type: {diagnostic_type}")
                # Try to get any question as emergency fallback
                emergency_question = Question.query.first()
                if not emergency_question:
                    logger.error("No questions found in database at all")
                    
                    # Try to load data automatically
                    logger.info("Attempting to load data automatically...")
                    try:
                        from scripts.seed_production_data_runner import main as load_data
                        load_data()
                        logger.info("Data loaded successfully, trying again...")
                        
                        # Try again after loading
                        irt_engine = IRTEngine(diagnostic_type=diagnostic_type)
                        first_question = irt_engine.select_initial_question()
                        
                        if not first_question:
                            emergency_question = Question.query.first()
                            if not emergency_question:
                                raise BadRequest('No questions available in database after loading')
                            else:
                                logger.warning(f"Using emergency fallback question after loading: {emergency_question.id}")
                                first_question = emergency_question
                        else:
                            logger.info(f"Successfully selected question after loading: {first_question.id}")
                    except Exception as load_error:
                        logger.error(f"Failed to load data automatically: {load_error}")
                        raise BadRequest('No questions available in database')
                else:
                    logger.warning(f"Using emergency fallback question: {emergency_question.id}")
                    first_question = emergency_question
            
            # Initialize new diagnostic session ONLY after we have a question
            diagnostic_session = DiagnosticSession.create_session(
                user_id=current_user.id,
                session_type='adaptive_diagnostic',
                ip_address=request.remote_addr
            )
            
            # Определяем правильный session_type и diagnostic_type на основе выбора пользователя
            if diagnostic_type == 'express':
                session_type = 'preliminary'
                diagnostic_type = 'preliminary'  # Оставляем как есть
                estimated_questions = 25
                questions_per_domain = 1
            elif diagnostic_type == 'preliminary':
                session_type = 'full'
                diagnostic_type = 'full'  # ИСПРАВЛЕНИЕ: меняем на 'full' для 75 вопросов
                estimated_questions = 75
                questions_per_domain = 3
            elif diagnostic_type == 'readiness':
                session_type = 'comprehensive'
                diagnostic_type = 'comprehensive'  # ИСПРАВЛЕНИЕ: меняем на 'comprehensive' для 130 вопросов
                estimated_questions = 130
                questions_per_domain = 6
            else:
                session_type = 'preliminary'
                diagnostic_type = 'preliminary'
                estimated_questions = 25
                questions_per_domain = 1
            
            logger.info(f"Creating session: type={session_type}, diagnostic_type={diagnostic_type}, questions={estimated_questions}")
            
            # Сохранить тип диагностики в сессии
            session_data = {
                'diagnostic_type': diagnostic_type,  # Теперь правильный тип
                'session_type': session_type,
                'questions_per_domain': questions_per_domain,
                'estimated_total_questions': estimated_questions
            }
            diagnostic_session.set_session_data(session_data)
            
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
@rate_limit(requests_per_minute=100)  # Увеличено для диагностических тестов (может потребоваться 40+ вопросов)
@validate_session
def get_next_question():
    """Get next question in diagnostic session"""
    try:
        import traceback
        logger.info("=== DEBUGGING NEXT QUESTION START ===")
        logger.info(f"DB session active: {db.session.is_active}")
        logger.info(f"Session info: {db.session.info}")
        
        data = request.get_json()
        if not data:
            raise BadRequest('Invalid request data')
        
        diagnostic_session = g.current_session
        previous_answer = data.get('previous_answer')
        response_time = data.get('response_time', 0)
        
        # Получить тип диагностики из сессии
        session_data = diagnostic_session.get_session_data()
        diagnostic_type = session_data.get('diagnostic_type', 'express')
        logger.info(f"Session data: {session_data}")
        logger.info(f"Diagnostic type from session: {diagnostic_type}")
        
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
        logger.info("About to create IRT Engine...")
        # ИСПРАВЛЕНИЕ: используем правильный diagnostic_type из session_data
        correct_diagnostic_type = session_data.get('diagnostic_type', 'express')
        logger.info(f"Using correct diagnostic_type: {correct_diagnostic_type}")
        irt_engine = IRTEngine(diagnostic_session, diagnostic_type=correct_diagnostic_type)
        logger.info("IRT Engine created successfully")
        
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
        
        logger.info("About to call irt_engine.select_next_question()...")
        next_question = irt_engine.select_next_question()
        logger.info(f"select_next_question() returned: {next_question}")
        if next_question:
            logger.info(f"Question ID: {next_question.id}")
            logger.info(f"Question object session: {db.session.object_session(next_question)}")
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
        
        # ИСПРАВЛЕНИЕ: Принудительно перезагружаем объект Question
        logger.info("About to reload question object from database...")
        try:
            # Принудительно перезагружаем объект из базы данных
            question_id = next_question.id
            logger.info(f"Reloading question {question_id} from database...")
            next_question = Question.query.options(
                db.joinedload(Question.irt_parameters),
                db.joinedload(Question.big_domain)
            ).get(question_id)
            
            if next_question:
                logger.info("Question reloaded successfully")
                # Force load attributes while session is active
                _ = next_question.id
                _ = next_question.text
                _ = next_question.options
                logger.info("Question attributes loaded successfully")
            else:
                logger.error(f"Failed to reload question {question_id}")
                return safe_jsonify({
                    'success': False,
                    'error': 'Question not found'
                }), 404
        except Exception as e:
            logger.error(f"Error reloading question: {e}")
            logger.error(f"FULL TRACEBACK: {traceback.format_exc()}")
            return safe_jsonify({
                'success': False,
                'error': 'Failed to load question'
            }), 500
        
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
        
        # ИСПРАВЛЕНИЕ: Безопасное преобразование в dict
        logger.info("About to convert question to dict...")
        try:
            logger.info("About to call next_question.to_dict()...")
            question_dict = next_question.to_dict()
            logger.info("to_dict() completed successfully")
        except Exception as e:
            logger.error(f"Error converting question to dict: {e}")
            logger.error(f"FULL TRACEBACK: {traceback.format_exc()}")
            logger.info("Using fallback dict creation...")
            # Fallback: создаем dict вручную
            try:
                question_dict = {
                    'id': next_question.id,
                    'text': next_question.text,
                    'options': next_question.options,
                    'correct_answer_index': next_question.correct_answer_index,
                    'correct_answer_text': next_question.correct_answer_text,
                    'explanation': next_question.explanation,
                    'category': next_question.category,
                    'domain': next_question.domain,
                    'difficulty_level': next_question.difficulty_level,
                    'image_url': next_question.image_url,
                    'tags': next_question.tags or [],
                    'irt_params': next_question.get_irt_parameters() if next_question.irt_parameters else None
                }
                logger.info("Fallback dict creation completed successfully")
            except Exception as fallback_error:
                logger.error(f"Fallback dict creation also failed: {fallback_error}")
                logger.error(f"FALLBACK TRACEBACK: {traceback.format_exc()}")
                # Final fallback - return minimal data
                question_dict = {
                    'id': getattr(next_question, 'id', 'unknown'),
                    'text': getattr(next_question, 'text', 'Question text unavailable'),
                    'options': getattr(next_question, 'options', []),
                    'error': 'Question data partially unavailable'
                }
        
        return safe_jsonify({
            'success': True,
            'question': question_dict,
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
    """Submit answer for diagnostic session with enhanced validation"""
    try:
        logger.info(f"Submit answer called for session {session_id}")
        logger.info(f"Request content type: {request.content_type}")
        logger.info(f"Request is_json: {request.is_json}")
        logger.info(f"Form data: {dict(request.form)}")
        logger.info(f"Request headers: {dict(request.headers)}")
        logger.info(f"Current user: {current_user.id if current_user else 'None'}")
        logger.info(f"Session user_id: {request.session.get('user_id') if hasattr(request, 'session') else 'No session'}")
        logger.info(f"Request method: {request.method}")
        logger.info(f"Request URL: {request.url}")
        logger.info(f"Request remote addr: {request.remote_addr}")
        
        # Get session with validation
        session = DiagnosticSession.query.get_or_404(session_id)
        
        # Validate session ownership
        if session.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Validate session status
        if session.status != 'active':
            return jsonify({'success': False, 'error': 'Session is not active'}), 400
        
        # Get request data - support both JSON and FormData
        data = None
        
        # Try to get JSON data first
        if request.is_json:
            data = request.get_json()
        
        # If no JSON data, try to get form data
        if not data:
            data = request.form.to_dict()
            
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        logger.info(f"Extracted data: {data}")
        logger.info(f"Data types: question_id={type(data.get('question_id'))}, selected_option={type(data.get('selected_option'))}, answer={type(data.get('answer'))}")
        
        # Extract data from either JSON or form
        question_id = data.get('question_id')
        # Fix: Handle both field names, but don't use 'or' since 0 is falsy
        selected_option = data.get('selected_option')
        if selected_option is None:
            selected_option = data.get('answer')
        response_time = data.get('response_time')
        
        # If question_id is not provided, get it from the current session
        if not question_id:
            question_id = session.current_question_id
        
        logger.info(f"Processed data: question_id={question_id}, selected_option={selected_option}, response_time={response_time}")
        
        # Validate required fields
        if not question_id:
            return jsonify({'success': False, 'error': 'question_id is required'}), 400
        
        if selected_option is None:
            return jsonify({'success': False, 'error': 'selected_option or answer is required'}), 400
        
        # Convert selected_option to int if it's a string
        try:
            # Handle both string and numeric inputs
            if isinstance(selected_option, str):
                # Handle empty string case
                if not selected_option.strip():
                    return jsonify({'success': False, 'error': 'selected_option cannot be empty'}), 400
                selected_option = int(selected_option.strip())
            else:
                selected_option = int(selected_option)
        except (ValueError, TypeError):
            logger.error(f"Invalid selected_option format: {selected_option} (type: {type(selected_option)})")
            return jsonify({'success': False, 'error': f'Invalid selected_option format: {selected_option}'}), 400
        
        # Validate question exists and belongs to session
        question = Question.query.get_or_404(question_id)
        
        # Validate response time
        if response_time is not None:
            try:
                response_time = float(response_time)
                if response_time < 0:
                    return jsonify({'success': False, 'error': 'Invalid response time'}), 400
                if response_time > 300000:  # 5 minutes
                    logger.warning(f"Very long response time: {response_time}ms for user {current_user.id}")
            except (ValueError, TypeError):
                logger.warning(f"Invalid response time format: {response_time}")
                response_time = None
        
        # Validate selected option
        if not isinstance(selected_option, int) or selected_option < 0 or selected_option >= len(question.options):
            return jsonify({'success': False, 'error': 'Invalid selected option'}), 400
        
        # Create response with validation
        response = session.record_response(
            question_id=question_id,
            selected_option=selected_option,
            response_time=response_time
        )
        
        # Validate response creation
        if not response:
            return jsonify({'success': False, 'error': 'Failed to create response'}), 500
        
        # Validate IRT parameters before calculation
        irt_params = None
        if hasattr(question, 'irt_parameters') and question.irt_parameters:
            irt_params = question.irt_parameters
            is_valid, error_msg = validate_irt_parameters_for_calculation(
                irt_params.difficulty,
                irt_params.discrimination,
                irt_params.guessing
            )
            
            if not is_valid:
                logger.warning(f"Invalid IRT parameters for question {question_id}: {error_msg}")
                irt_params = None  # Use fallback calculation
        else:
            logger.info(f"Question {question_id} has no IRT parameters, using fallback calculation")
        
        # Update IRT ability estimate with validation
        try:
            irt = IRTEngine(session)
            irt_result = irt.update_ability_estimate(response)
            
            # Validate IRT result
            if not isinstance(irt_result, dict):
                logger.error(f"Invalid IRT result format: {irt_result}")
                irt_result = {'ability': 0.0, 'se': 1.0}
            
            ability = irt_result.get('ability', 0.0)
            se = irt_result.get('se', 1.0)
            
            # Validate ability range
            if not (-4.0 <= ability <= 4.0):
                logger.warning(f"Ability out of valid range: {ability}")
                ability = max(-4.0, min(4.0, ability))
            
            # Validate standard error
            if se <= 0 or se > 2.0:
                logger.warning(f"Invalid standard error: {se}")
                se = 1.0
            
            # Update session with validated values
            session.current_ability = ability
            session.ability_se = se
            
            # Save ability history
            session.add_ability_estimate(ability, se, session.current_question_id)
            
            logger.info(f"IRT Updated: ability={ability:.3f}, SE={se:.3f}")
            
        except Exception as e:
            logger.error(f"IRT update failed: {e}")
            import traceback
            logger.error(f"IRT error traceback: {traceback.format_exc()}")
            # Fallback calculation
            if session.questions_answered > 0:
                accuracy = session.correct_answers / session.questions_answered
                session.current_ability = 2 * (accuracy - 0.5)
                session.ability_se = 1.0 / (session.questions_answered ** 0.5)
                logger.info(f"Fallback calculation: ability={session.current_ability:.3f}, SE={session.ability_se:.3f}")
            else:
                session.current_ability = 0.0
                session.ability_se = 1.0
                logger.info("No questions answered, using default values")
        
        # Validate session data before proceeding
        session_data = session.get_session_data()
        if not session_data:
            logger.error("Failed to get session data")
            return jsonify({'success': False, 'error': 'Session data error'}), 500
        
        diagnostic_type = session_data.get('diagnostic_type', 'express')
        
        # Validate diagnostic type
        if diagnostic_type not in ['express', 'preliminary', 'readiness', 'full', 'comprehensive']:
            logger.warning(f"Invalid diagnostic type: {diagnostic_type}")
            diagnostic_type = 'express'
        
        # Determine max questions with validation
        max_questions = {
            'express': 25,
            'preliminary': 75, 
            'readiness': 130,
            'full': 75,
            'comprehensive': 130
        }.get(diagnostic_type, 25)
        
        # Validate question count
        if session.questions_answered > max_questions:
            logger.warning(f"Session exceeded max questions: {session.questions_answered} > {max_questions}")
            session.questions_answered = max_questions
        
        # Check completion conditions
        should_complete = False
        completion_reason = None
        
        # Check max questions
        if session.questions_answered >= max_questions:
            should_complete = True
            completion_reason = 'max_questions'
        
        # Check precision (only if enough questions answered)
        elif session.questions_answered >= 5:
            if session.ability_se <= 0.3:  # Sufficient precision
                should_complete = True
                completion_reason = 'precision_reached'
        
        # Complete session if needed
        if should_complete:
            session.status = 'completed'
            session.completed_at = datetime.now(timezone.utc)
            session.termination_reason = completion_reason
            
            # Generate results
            try:
                results = session.generate_results()
                if not results:
                    logger.error("Failed to generate session results")
                    return jsonify({'success': False, 'error': 'Failed to generate results'}), 500
            except Exception as e:
                logger.error(f"Error generating results: {e}")
                return jsonify({'success': False, 'error': 'Failed to generate results'}), 500
        
        # Save all changes
        db.session.commit()
        
        # Prepare response
        response_data = {
            'success': True,  # Добавляем поле success
            'is_correct': response.is_correct,
            'correct_answer': question.correct_answer_text,
            'explanation': question.explanation,
            'current_ability': session.current_ability,
            'ability_se': session.ability_se,
            'questions_answered': session.questions_answered,
            'session_completed': should_complete
        }
        
        if should_complete:
            response_data['results'] = results
        
        # Добавляем логирование для отладки
        logger.info(f"Sending response: {response_data}")
        
        return jsonify(response_data)
        
    except Exception as e:
        logger.error(f"Error in submit_answer: {e}")
        import traceback
        logger.error(f"Submit answer error traceback: {traceback.format_exc()}")
        logger.error(f"Session ID: {session_id}")
        logger.error(f"Current user: {current_user.id if current_user else 'None'}")
        logger.error(f"Request data: {request.get_data()}")
        logger.error(f"Request method: {request.method}")
        logger.error(f"Request URL: {request.url}")
        logger.error(f"Request remote addr: {request.remote_addr}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Internal server error', 'details': str(e)}), 500

@diagnostic_bp.route('/results/<int:session_id>')
@login_required
@validate_session
def show_results(session_id):
    """Show diagnostic results with modern UI"""
    print(f"🔍 ОТЛАДКА: show_results вызвана для session_id = {session_id}")
    current_app.logger.info(f"Showing results for session {session_id}")
    
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
                
                # Translate domain name based on language
                domain_name_translation_key = f'domain_{domain_code.lower()}'
                translated_domain_name = t(domain_name_translation_key, lang) if t(domain_name_translation_key, lang) != domain_name_translation_key else domain_name
                
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
                    'name': translated_domain_name,
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
        
        # Calculate confidence statistics
        confidence_stats = {}
        responses = diagnostic_session.responses.all()
        if responses:
            confidence_levels = [r.confidence_level for r in responses if r.confidence_level is not None]
            if confidence_levels:
                confidence_stats = {
                    'average_confidence': round(sum(confidence_levels) / len(confidence_levels), 1),
                    'high_confidence_answers': len([c for c in confidence_levels if c >= 4]),
                    'low_confidence_answers': len([c for c in confidence_levels if c <= 2]),
                    'total_with_confidence': len(confidence_levels)
                }
        
        # Prepare diagnostic data for template
        diagnostic_data = {
            'session_id': diagnostic_session.id,
            'overall_score': overall_score,
            'readiness_level': readiness_level,
            'total_questions': diagnostic_session.questions_answered,
            'correct_answers': diagnostic_session.correct_answers,
            'accuracy_percentage': round((diagnostic_session.correct_answers / diagnostic_session.questions_answered) * 100, 1) if diagnostic_session.questions_answered > 0 else 0.0,
            'confidence_stats': confidence_stats,
            'domains': domains,
            'recommendations': recommendations,
            'results': results
        }
        
        print(f"🔍 ОТЛАДКА: diagnostic_data подготовлен, рендерим шаблон")
        
        # Сбрасываем флаг диагностики после успешного завершения
        current_user.requires_diagnostic = False
        db.session.commit()
        
        # Создание или обновление плана обучения на основе результатов диагностики
        if diagnostic_session.session_type in ['diagnostic', 'express', 'preliminary', 'readiness']:
            # Проверяем, есть ли активный план
            existing_plan = PersonalLearningPlan.query.filter_by(
                user_id=current_user.id,
                status='active'
            ).first()
            
            if existing_plan:
                # Обновляем существующий план
                existing_plan.diagnostic_session_id = diagnostic_session.id  # ВАЖНО!
                existing_plan.current_ability = results['final_ability']
                
                # Convert domain_abilities to proper format
                domain_analysis = {}
                for domain_code, ability_value in results['domain_abilities'].items():
                    domain_analysis[domain_code] = {
                        'ability_estimate': ability_value,
                        'accuracy': ability_value,  # For backward compatibility
                        'questions_answered': 0,
                        'correct_answers': 0
                    }
                existing_plan.set_domain_analysis(domain_analysis)
                existing_plan.set_weak_domains(results['weak_domains'])
                existing_plan.set_strong_domains(results['strong_domains'])
                existing_plan.next_diagnostic_date = date.today() + timedelta(days=14)
                existing_plan.last_updated = datetime.now(timezone.utc)
                db.session.commit()
                print(f"🔍 ОТЛАДКА: Существующий план обновлен: {existing_plan.id} с {len(domain_analysis)} доменами")
            else:
                # Создаем новый план
                new_plan = PersonalLearningPlan(
                    user_id=current_user.id,
                    diagnostic_session_id=diagnostic_session.id,  # ОБЯЗАТЕЛЬНО!
                    current_ability=results['final_ability'],
                    target_ability=0.7,
                    study_hours_per_week=20.0,
                    intensity='moderate',
                    status='active'
                )
                
                # Convert domain_abilities to proper format
                domain_analysis = {}
                for domain_code, ability_value in results['domain_abilities'].items():
                    domain_analysis[domain_code] = {
                        'ability_estimate': ability_value,
                        'accuracy': ability_value,  # For backward compatibility
                        'questions_answered': 0,
                        'correct_answers': 0
                    }
                new_plan.set_domain_analysis(domain_analysis)
                new_plan.set_weak_domains(results['weak_domains'])
                new_plan.set_strong_domains(results['strong_domains'])
                new_plan.next_diagnostic_date = date.today() + timedelta(days=14)
                new_plan.diagnostic_reminder_sent = False
                
                db.session.add(new_plan)
                db.session.commit()
                print(f"🔍 ОТЛАДКА: Новый план создан: {new_plan.id} с {len(domain_analysis)} доменами")
                
            flash('План обучения создан на основе результатов диагностики!', 'success')
        elif diagnostic_session.session_type == 'reassessment':
            active_plan = PersonalLearningPlan.query.filter_by(
                user_id=current_user.id,
                status='active'
            ).first()
            
            if active_plan:
                # Get old abilities for comparison
                old_abilities = active_plan.get_domain_analysis()
                new_abilities = results['domain_abilities']
                
                # Analyze improvements
                improvements = {}
                still_weak = []
                
                for domain_code, new_data in new_abilities.items():
                    old_ability = old_abilities.get(domain_code, {}).get('ability_estimate', 0.0)
                    new_ability = new_data.get('ability_estimate', 0.0)
                    improvement = new_ability - old_ability
                    
                    improvements[domain_code] = {
                        'old': old_ability,
                        'new': new_ability,
                        'improvement': improvement,
                        'improved': improvement > 0.1
                    }
                    
                                        # Use statistically justified threshold: weak if ability < -0.5 (1 SD below mean)
                    # This corresponds to approximately 30% accuracy in 3PL model
                    if new_ability < -0.5:
                        still_weak.append(domain_code)
                
                # Update plan with new data
                active_plan.current_ability = results['final_ability']
                active_plan.set_domain_analysis(new_abilities)
                active_plan.set_weak_domains(still_weak)
                
                # Log progress
                try:
                    from app import app
                    app.logger.info(f"Reassessment for user {current_user.id}: "
                                   f"Overall ability {active_plan.current_ability:.2f}, "
                                   f"Weak domains: {still_weak}")
                except ImportError:
                    # If app is not available, just continue
                    pass
                
                # Reset next diagnostic date
                from datetime import date, timedelta
                active_plan.next_diagnostic_date = date.today() + timedelta(days=14)
                active_plan.diagnostic_reminder_sent = False
                
                # Add improvement data to results for display
                results['improvements'] = improvements
                results['domains_still_weak'] = still_weak
                
                db.session.commit()
                
                flash(f'План обучения обновлен! Улучшение в {sum(1 for d in improvements.values() if d["improved"])} доменах.', 'success')
        
        # Рендерим шаблон результатов вместо редиректа на dashboard
        return render_template('assessment/results.html', 
                             diagnostic_data=diagnostic_data,
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
            'status': diagnostic_session.status,
            'redirect_url': url_for('diagnostic.show_results', session_id=session_id)
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
        # Получение ID сессии из запроса
        session_id = request.json.get('session_id')
        if not session_id:
            return safe_jsonify({'success': False, 'error': 'Diagnostic session ID is required.'}), 400
        
        # Проверяем наличие завершенной диагностики
        latest_diagnostic = DiagnosticSession.query.filter_by(
            user_id=current_user.id,
            status='completed'
        ).order_by(DiagnosticSession.completed_at.desc()).first()

        if not latest_diagnostic:
            flash('Необходимо пройти диагностику перед созданием плана', 'warning')
            return redirect(url_for('diagnostic.choose_diagnostic_type'))
        
        data = request.get_json()
        if not data:
            raise BadRequest('Invalid request data')
        
        study_hours_per_week = data.get('study_hours_per_week', 20)
        exam_date = data.get('exam_date')
        
        # Get diagnostic session
        diagnostic_session = DiagnosticSession.query.get(session_id)
        if not diagnostic_session:
            raise BadRequest('Diagnostic session not found')
        
        if diagnostic_session.user_id != current_user.id:
            raise Unauthorized('Access denied')
        
        # Generate results if not already generated
        try:
            results = diagnostic_session.generate_results()
        except Exception as e:
            logger.error(f"Error generating results for session {session_id}: {e}")
            return safe_jsonify({'success': False, 'error': f'Failed to generate results: {str(e)}'}), 500
        
        # Проверяем, есть ли уже активный план у пользователя
        existing_plan = PersonalLearningPlan.query.filter_by(
            user_id=current_user.id,
            status='active'
        ).first()

        if existing_plan:
            # Если план уже есть, обновляем его
            plan = existing_plan
            plan.diagnostic_session_id = diagnostic_session.id
            plan.last_updated = datetime.now(timezone.utc)
            plan.status = 'active'  # Убедимся, что план активен
            logger.info(f"Updating existing plan {plan.id} for user {current_user.id}")
        else:
            # Если плана нет, создаем новый
            plan = PersonalLearningPlan(
                user_id=current_user.id,
                diagnostic_session_id=diagnostic_session.id,
                status='active'  # Явно устанавливаем статус активным
            )
            db.session.add(plan)
            logger.info(f"Creating new plan for user {current_user.id}")

        # Обновляем данные плана
        plan.current_ability = results.get('final_ability', 0.0)
        # Target ability for BI-toets: 0.5 corresponds to ~70% accuracy in 3PL model
        # This is the minimum passing threshold for professional certification
        plan.target_ability = 0.5  # Target for exam readiness
        plan.study_hours_per_week = study_hours_per_week
        plan.diagnostic_session_id = diagnostic_session.id
        
        # Set next diagnostic date (14 days from today)
        from datetime import date
        plan.next_diagnostic_date = date.today() + timedelta(days=14)
        plan.diagnostic_reminder_sent = False
        
        if exam_date:
            try:
                plan.exam_date = datetime.strptime(exam_date, '%Y-%m-%d').date()
            except ValueError:
                logger.warning(f"Invalid exam date format: {exam_date}")
        
        # Set domain analysis from real IRT results with proper format
        if 'domain_abilities' in results:
            # Convert simple domain_abilities to proper format expected by DailyLearningAlgorithm
            domain_analysis = {}
            for domain_code, ability_value in results['domain_abilities'].items():
                domain_analysis[domain_code] = {
                    'ability_estimate': ability_value,
                    'accuracy': ability_value,  # For backward compatibility
                    'questions_answered': 0,  # Will be updated from actual responses
                    'correct_answers': 0
                }
            plan.set_domain_analysis(domain_analysis)
            logger.info(f"Saved domain analysis with {len(domain_analysis)} domains for user {current_user.id}")
        
        if 'weak_domains' in results:
            plan.set_weak_domains(results['weak_domains'])
            logger.info(f"Saved {len(results['weak_domains'])} weak domains for user {current_user.id}")
        
        if 'strong_domains' in results:
            plan.set_strong_domains(results['strong_domains'])
            logger.info(f"Saved {len(results['strong_domains'])} strong domains for user {current_user.id}")
        
        # Generate study schedule
        try:
            schedule = generate_study_schedule(results, study_hours_per_week, exam_date)
            plan.set_study_schedule(schedule)
        except Exception as e:
            logger.error(f"Error generating study schedule: {e}")
            # Создаем базовый расписание
            plan.set_study_schedule({'weekly_schedule': []})
        
        # Generate milestones
        try:
            milestones = generate_milestones(results, study_hours_per_week, exam_date)
            plan.set_milestones(milestones)
        except Exception as e:
            logger.error(f"Error generating milestones: {e}")
            # Создаем базовые вехи
            plan.set_milestones([])
        
        # Calculate estimated readiness
        try:
            plan.estimated_readiness = plan.calculate_readiness()
        except Exception as e:
            logger.error(f"Error calculating readiness: {e}")
            plan.estimated_readiness = 0.0

        # Явно сохраняем план в базе данных
        try:
            db.session.commit()
            logger.info(f"Successfully saved plan {plan.id} to database")
        except Exception as e:
            logger.error(f"Error saving plan to database: {e}")
            db.session.rollback()
            return safe_jsonify({'success': False, 'error': f'Failed to save plan: {str(e)}'}), 500
        
        # Create study sessions
        try:
            create_study_sessions(plan, schedule)
        except Exception as e:
            logger.error(f"Error creating study sessions: {e}")
            # Не прерываем выполнение, если не удалось создать сессии
        
        logger.info(f"Generated learning plan {plan.id} for user {current_user.id}")
        
        # Успешное завершение. Перенаправляем пользователя на карту обучения.
        return safe_jsonify({
            'success': True,
            'message': 'Learning plan successfully created!',
            'plan_id': plan.id,
                            'redirect_url': url_for('daily_learning.learning_map', lang='en'),
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
        logger.error(f"Error in generate_learning_plan: {e}")
        db.session.rollback()
        return safe_jsonify({'success': False, 'error': f'Internal server error: {str(e)}'}), 500

def generate_study_schedule(results, study_hours_per_week, exam_date=None):
    """Generate personalized study schedule"""
    weak_domains = results.get('weak_domains', [])
    strong_domains = results.get('strong_domains', [])
    current_ability = results.get('final_ability', 0.0)
    
    # Calculate total weeks needed
    if exam_date:
        exam_date_obj = datetime.strptime(exam_date, '%Y-%m-%d').date()
        weeks_until_exam = max(1, (exam_date_obj - datetime.now(timezone.utc).date()).days // 7)
    else:
        # Estimate based on current ability and weak domains
        # Calculate weeks needed based on ability gap and domain weights
        # Use adaptive calculation: more time for larger ability gaps and critical domains
        ability_gap = max(0, 0.5 - current_ability)
        critical_domains = [d for d in weak_domains if d in ['THER', 'SURG', 'EMERGENCY']]  # Critical domains
        weeks_until_exam = max(8, len(weak_domains) * 2 + len(critical_domains) * 3 + int(ability_gap * 15))
    
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
        # Target ability for BI-toets: 0.5 corresponds to ~70% accuracy in 3PL model
    # This represents the minimum passing threshold for professional certification
    target_ability = 0.5
    ability_gap = target_ability - current_ability
    
    # Determine total weeks based on exam date or default
    if exam_date:
        exam_date_obj = datetime.strptime(exam_date, '%Y-%m-%d').date()
        total_weeks = max(1, (exam_date_obj - datetime.now(timezone.utc).date()).days // 7)
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
    """Страница выбора типа диагностики - временно закрыта"""
    # Получаем язык из сессии или используем дефолтный
    lang = session.get('lang', 'nl')
    return render_template('coming_soon.html', lang=lang)

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
        # Generate realistic performance based on IRT model
        # 0.5-0.75 range corresponds to theta values of approximately -0.5 to +0.5
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

@diagnostic_bp.route('/reassessment/<int:plan_id>')
@login_required
def start_reassessment(plan_id):
    """Start a new diagnostic session for reassessment"""
    try:
        # Get the learning plan
        plan = PersonalLearningPlan.query.get_or_404(plan_id)
        
        # Check if plan belongs to current user
        if plan.user_id != current_user.id:
            flash('Access denied.', 'error')
            return redirect('/dashboard')
        
        # Create new diagnostic session for reassessment
        diagnostic_session = DiagnosticSession.create_session(
            user_id=current_user.id,
            session_type='reassessment',
            ip_address=request.remote_addr
        )
        
        # Update plan with new session
        plan.diagnostic_session_id = diagnostic_session.id
        plan.diagnostic_reminder_sent = False
        db.session.commit()
        
        flash('Начинаем переоценку вашего прогресса обучения.', 'info')
        return redirect(f'/big-diagnostic/question/{diagnostic_session.id}')
        
    except Exception as e:
        logger.error(f"Error starting reassessment: {e}")
        flash('Ошибка при запуске переоценки.', 'error')
        return redirect('/dashboard')

@diagnostic_bp.route('/session/<int:session_id>/complete', methods=['POST'])
@login_required
@validate_session
def complete_session(session_id):
    """Force complete diagnostic session and create learning plan"""
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
        
        # Автоматически создаем план обучения
        try:
            # Проверяем, есть ли уже активный план
            existing_plan = PersonalLearningPlan.query.filter_by(
                user_id=current_user.id,
                status='active'
            ).first()
            
            if not existing_plan:
                # Генерируем результаты диагностики
                results = session.generate_results()
                
                # Создаем новый план
                plan = PersonalLearningPlan(
                    user_id=current_user.id,
                    diagnostic_session_id=session.id,
                    status='active',
                    current_ability=results.get('final_ability', 0.0),
                    # Target ability for BI-toets: 0.5 corresponds to ~70% accuracy in 3PL model
        target_ability=0.5,
                    study_hours_per_week=20,  # Дефолтные значения
                    next_diagnostic_date=date.today() + timedelta(days=14)
                )
                
                # Устанавливаем анализ доменов
                if 'domain_abilities' in results:
                    plan.set_domain_analysis(results['domain_abilities'])
                
                if 'weak_domains' in results:
                    plan.set_weak_domains(results['weak_domains'])
                
                if 'strong_domains' in results:
                    plan.set_strong_domains(results['strong_domains'])
                
                # Генерируем расписание и вехи
                try:
                    schedule = generate_study_schedule(results, 20, None)
                    plan.set_study_schedule(schedule)
                    
                    milestones = generate_milestones(results, 20, None)
                    plan.set_milestones(milestones)
                    
                    plan.estimated_readiness = plan.calculate_readiness()
                except Exception as e:
                    logger.error(f"Error generating schedule/milestones: {e}")
                    # Устанавливаем базовые значения
                    plan.set_study_schedule({'weekly_schedule': []})
                    plan.set_milestones([])
                    plan.estimated_readiness = 0.0
                
                db.session.add(plan)
                db.session.commit()
                
                print(f"🔍 ОТЛАДКА: создан новый план обучения {plan.id}")
                
                return safe_jsonify({
                    'success': True,
                    'message': 'Session completed and learning plan created',
                    'plan_id': plan.id,
                    'redirect_url': url_for('daily_learning.learning_map', lang='en')
                })
            else:
                print(f"🔍 ОТЛАДКА: активный план уже существует {existing_plan.id}")
                return safe_jsonify({
                    'success': True,
                    'message': 'Session completed successfully',
                    'plan_id': existing_plan.id,
                    'redirect_url': url_for('daily_learning.learning_map', lang='en')
                })
                
        except Exception as e:
            logger.error(f"Error creating learning plan: {e}")
            # Возвращаем успех даже если не удалось создать план
            return safe_jsonify({
                'success': True,
                'message': 'Session completed successfully',
                'warning': 'Could not create learning plan automatically'
            })
        
    except Exception as e:
        print(f"❌ Ошибка в complete_session: {e}")
        import traceback
        traceback.print_exc()
        return safe_jsonify({
            'success': False,
            'error': f'Error completing session: {str(e)}'
        }), 500

@diagnostic_bp.route('/update-plan-after-reassessment', methods=['POST'])
@login_required
@rate_limit(requests_per_minute=10)
def update_plan_after_reassessment():
    """
    Update learning plan after reassessment with new ability estimates
    """
    try:
        data = request.get_json()
        if not data:
            raise BadRequest('Invalid request data')
        
        plan_id = data.get('plan_id')
        session_id = data.get('session_id')
        
        if not plan_id or not session_id:
            return safe_jsonify({'success': False, 'error': 'Plan ID and session ID are required'}), 400
        
        # Get the learning plan
        plan = PersonalLearningPlan.query.get(plan_id)
        if not plan or plan.user_id != current_user.id:
            return safe_jsonify({'success': False, 'error': 'Plan not found or access denied'}), 404
        
        # Get the diagnostic session
        diagnostic_session = DiagnosticSession.query.get(session_id)
        if not diagnostic_session or diagnostic_session.user_id != current_user.id:
            return safe_jsonify({'success': False, 'error': 'Session not found or access denied'}), 404
        
        # Generate results from reassessment
        try:
            results = diagnostic_session.generate_results()
        except Exception as e:
            logger.error(f"Error generating results for reassessment session {session_id}: {e}")
            return safe_jsonify({'success': False, 'error': f'Failed to generate results: {str(e)}'}), 500
        
        # Extract new abilities from results
        new_abilities = {}
        if 'domain_abilities' in results:
            for domain, data in results['domain_abilities'].items():
                if isinstance(data, dict) and 'accuracy' in data:
                    new_abilities[domain] = float(data['accuracy'])
        
        # Update plan with new abilities
        reassessment_date = date.today()
        success = plan.update_after_reassessment(new_abilities, reassessment_date)
        
        if not success:
            return safe_jsonify({'success': False, 'error': 'Failed to update plan'}), 500
        
        # Update current ability
        plan.current_ability = results.get('final_ability', plan.current_ability)
        plan.estimated_readiness = plan.calculate_readiness()
        
        # Update diagnostic session reference
        plan.diagnostic_session_id = session_id
        
        # Commit changes
        db.session.commit()
        
        logger.info(f"Updated plan {plan_id} after reassessment for user {current_user.id}")
        
        return safe_jsonify({
            'success': True,
            'message': 'Learning plan updated successfully after reassessment',
            'plan_id': plan.id,
            'new_abilities': new_abilities,
            'current_ability': plan.current_ability,
            'estimated_readiness': plan.estimated_readiness,
            'next_diagnostic_date': plan.next_diagnostic_date.isoformat() if plan.next_diagnostic_date else None,
            'redirect_url': url_for('daily_learning.learning_map', lang='en')
        })
        
    except Exception as e:
        logger.error(f"Error updating plan after reassessment: {e}")
        return safe_jsonify({
            'success': False,
            'error': f'Error updating plan: {str(e)}'
        }), 500 

@diagnostic_bp.route('/calibrate-irt', methods=['POST'])
@login_required
@rate_limit(requests_per_minute=5)
def calibrate_irt_parameters():
    """Пакетная калибровка IRT параметров для вопросов"""
    try:
        data = request.get_json() or {}
        domain_code = data.get('domain_code')
        
        if domain_code:
            # Калибровка конкретного домена
            result = calibration_service.batch_calibrate_domain(domain_code)
            if result.get('success'):
                return safe_jsonify({
                    'success': True,
                    'message': f'Калибровка домена {domain_code} завершена',
                    'statistics': result
                })
            else:
                return safe_jsonify({
                    'success': False,
                    'error': result.get('error', 'Ошибка калибровки')
                }), 400
        else:
            # Калибровка всех доменов
            from models import BIGDomain
            domains = BIGDomain.query.filter_by(is_active=True).all()
            
            total_results = {}
            for domain in domains:
                result = calibration_service.batch_calibrate_domain(domain.code)
                total_results[domain.code] = result
            
            return safe_jsonify({
                'success': True,
                'message': 'Калибровка всех доменов завершена',
                'results': total_results
            })
            
    except Exception as e:
        logger.error(f"Error calibrating IRT parameters: {str(e)}")
        return safe_jsonify({
            'success': False,
            'error': f'Ошибка калибровки: {str(e)}'
        }), 500

@diagnostic_bp.route('/irt-statistics', methods=['GET'])
@login_required
@rate_limit(requests_per_minute=10)
def get_irt_statistics():
    """Получить статистику IRT калибровки"""
    try:
        stats = calibration_service.get_calibration_statistics()
        
        if 'error' in stats:
            return safe_jsonify({
                'success': False,
                'error': stats['error']
            }), 500
        
        return safe_jsonify({
            'success': True,
            'statistics': stats
        })
        
    except Exception as e:
        logger.error(f"Error getting IRT statistics: {str(e)}")
        return safe_jsonify({
            'success': False,
            'error': f'Ошибка получения статистики: {str(e)}'
        }), 500

# Блокировка через CSS overlay - убрано для использования JavaScript overlay

 