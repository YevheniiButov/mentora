# routes/test_routes.py - Test system routes

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import User, Question, QuestionCategory, BIGDomain, IRTParameters, DiagnosticSession, DiagnosticResponse, PersonalLearningPlan
from extensions import db
from utils.irt_engine import IRTEngine
from utils.helpers import get_user_profession_code
import logging
import json
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

test_bp = Blueprint('tests', __name__)

@test_bp.route('/')
@login_required
def index():
    """Main tests page"""
    return render_template('tests/index.html')

# @test_bp.route('/big-diagnostic')
# @login_required
# def big_diagnostic():
#     """BI-toets diagnostic testing page - MOVED TO diagnostic_bp"""
#     # Check if user has active diagnostic session
#     active_session = DiagnosticSession.query.filter_by(
#         user_id=current_user.id,
#         status='active'
#     ).first()
#     
#     # Get user's recent diagnostic sessions
#     recent_sessions = DiagnosticSession.query.filter_by(
#         user_id=current_user.id
#     ).order_by(DiagnosticSession.started_at.desc()).limit(5).all()
#     
#     # Get user's learning plans
#     learning_plans = PersonalLearningPlan.query.filter_by(
#         user_id=current_user.id
#     ).order_by(PersonalLearningPlan.last_updated.desc()).limit(3).all()
#     
#     return render_template('assessment/big_diagnostic.html',
#                          active_session=active_session,
#                          recent_sessions=recent_sessions,
#                          learning_plans=learning_plans)

@test_bp.route('/available')
@login_required
def available():
    """List of available tests"""
    categories = QuestionCategory.query.all()
    return render_template('tests/available.html', categories=categories)

@test_bp.route('/take/<int:category_id>')
@login_required
def take_test(category_id):
    """Take a specific test"""
    category = QuestionCategory.query.get_or_404(category_id)
    questions = category.questions.limit(10).all()
    
    if not questions:
        flash('В этой категории нет вопросов', 'warning')
        return redirect(url_for('tests.index'))
    
    return render_template('tests/take_test.html', category=category, questions=questions)

@test_bp.route('/submit/<int:category_id>', methods=['POST'])
@login_required
def submit_test(category_id):
    """Submit test answers"""
    category = QuestionCategory.query.get_or_404(category_id)
    
    # Process answers
    answers = request.form.to_dict()
    
    # Get questions for this category
    questions = category.questions.limit(10).all()
    total_questions = len(questions)
    correct_answers = 0
    
    # Calculate score and save attempts
    for question in questions:
        user_answer = answers.get(f'question_{question.id}')
        is_correct = question.check_answer(user_answer)
        
        if is_correct:
            correct_answers += 1
        
        # Save test attempt
        test_attempt = TestAttempt(
            user_id=current_user.id,
            test_id=category.id,  # Using category as test
            question_id=question.id,
            selected_option=user_answer,
            is_correct=is_correct
        )
        db.session.add(test_attempt)
    
    # Calculate final score
    score = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0
    
    # Save test session
    test_session = TestSession(
        user_id=current_user.id,
        module_id=category.id,  # Using category as module
        test_type='standard',
        difficulty='medium',
        total_questions=total_questions,
        correct_answers=correct_answers,
        score=score,
        status='completed',
        completed_at=datetime.now()
    )
    db.session.add(test_session)
    
    # Save test result
    test_result = TestResult(
        user_id=current_user.id,
        test_session_id=test_session.id,
        module_id=category.id,
        score=score,
        correct_answers=correct_answers,
        total_questions=total_questions,
        test_type='standard',
        difficulty='medium'
    )
    db.session.add(test_result)
    
    try:
        db.session.commit()
        flash(f'Тест завершен! Ваш результат: {score}% ({correct_answers}/{total_questions})', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error saving test results: {e}")
        flash('Ошибка при сохранении результатов теста', 'error')
    
    return redirect(url_for('tests.index'))

@test_bp.route('/categories')
@login_required
def categories():
    """View test categories"""
    categories = QuestionCategory.query.all()
    
    # Add question count for each category
    categories_data = []
    for category in categories:
        question_count = category.questions.count()
        categories_data.append({
            'category': category,
            'question_count': question_count
        })
    
    return render_template('tests/categories.html', categories=categories_data)

@test_bp.route('/api/stats')
@login_required
def api_stats():
    """API endpoint for test statistics"""
    
    # Get available categories
    categories = QuestionCategory.query.all()
    total_categories = len(categories)
    total_questions = sum(category.questions.count() for category in categories)
    
    return jsonify({
        'total_categories': total_categories,
        'total_questions': total_questions,
        'categories': [
            {
                'name': category.name,
                'questions_count': category.questions.count()
            } for category in categories
        ]
    })

# ========================================
# BI-TOETS DIAGNOSTIC TESTING ENDPOINTS
# ========================================

# @test_bp.route('/big-diagnostic/start', methods=['POST'])
# @login_required
# def start_big_diagnostic():
#     """Start a new BI-toets diagnostic session - MOVED TO diagnostic_bp"""
#     try:
#         data = request.get_json()
#         session_type = data.get('session_type', 'diagnostic')
#         test_length = data.get('test_length', None)  # None for adaptive
#         time_limit = data.get('time_limit', None)  # Minutes
#         
#         # Check if user has active session
#         active_session = DiagnosticSession.query.filter_by(
#             user_id=current_user.id,
#             status='active'
#         ).first()
#         
#         if active_session:
#             return jsonify({
#                 'success': False,
#                 'error': 'У вас уже есть активная сессия диагностики',
#                 'has_active_session': True,
#                 'active_session': {
#                     'id': active_session.id,
#                     'questions_answered': active_session.questions_answered,
#                     'correct_answers': active_session.correct_answers,
#                     'current_ability': float(active_session.current_ability) if active_session.current_ability is not None else 0.0,
#                     'started_at': active_session.started_at.isoformat() if active_session.started_at else None
#                 }
#             }), 400
#         
#         # Create new diagnostic session
#         session = DiagnosticSession(
#             user_id=current_user.id,
#             session_type=session_type,
#             test_length=test_length,
#             time_limit=time_limit
#         )
#         
#         db.session.add(session)
#         db.session.commit()
#         
#         # Get available questions with IRT parameters
#         available_questions = Question.query.join(IRTParameters).filter(
#             Question.big_domain_id.isnot(None)
#         ).all()
#         
#         if not available_questions:
#             return jsonify({
#                 'success': False,
#                 'error': 'Нет доступных вопросов для диагностики'
#             }), 400
#         
#         # Select first question
#         first_question = irt_engine.select_next_question(session, available_questions)
#         
#         if not first_question:
#             return jsonify({
#                 'success': False,
#                 'error': 'Не удалось выбрать первый вопрос'
#             }), 400
#         
#         return jsonify({
#             'success': True,
#             'session_id': session.id,
#             'question': {
#                 'id': first_question.id,
#                 'text': first_question.text,
#                 'options': first_question.get_options_list(),
#                 'image_filename': first_question.image_filename,
#                 'domain': first_question.big_domain.name if first_question.big_domain else None,
#                 'difficulty_level': first_question.difficulty_level
#             },
#             'session_info': {
#                 'current_ability': float(session.current_ability) if session.current_ability is not None else 0.0,
#                 'ability_se': float(session.ability_se) if session.ability_se is not None else 1.0,
#                 'questions_answered': int(session.questions_answered) if session.questions_answered is not None else 0
#             }
#         })
#         
#     except Exception as e:
#         logger.error(f"Error starting diagnostic session: {e}")
#         db.session.rollback()
#         return jsonify({
#             'success': False,
#             'error': 'Ошибка при запуске диагностики'
#         }), 500

# @test_bp.route('/big-diagnostic/next-question', methods=['POST'])
# @login_required
# def get_next_question():
#     """Get next question for diagnostic session - MOVED TO diagnostic_bp"""
#     try:
#         data = request.get_json()
#         session_id = data.get('session_id')
#         
#         session = DiagnosticSession.query.filter_by(
#             id=session_id,
#             user_id=current_user.id,
#             status='active'
#         ).first()
#         
#         if not session:
#             return jsonify({
#                 'success': False,
#                 'error': 'Сессия не найдена или завершена'
#             }), 404
#         
#         # Check termination conditions
#         termination_info = irt_engine._check_termination_conditions(session)
#         if termination_info['should_terminate']:
#             session.status = 'completed'
#             session.completed_at = datetime.now(timezone.utc)
#             session.termination_reason = termination_info['reasons'][0]
#             db.session.commit()
#             
#             return jsonify({
#                 'success': True,
#                 'session_completed': True,
#                 'termination_reasons': termination_info['reasons']
#             })
#         
#         # Get available questions (exclude already answered)
#         answered_question_ids = [r.question_id for r in session.responses.all()]
#         available_questions = Question.query.join(IRTParameters).filter(
#             Question.big_domain_id.isnot(None),
#             ~Question.id.in_(answered_question_ids)
#         ).all()
#         
#         if not available_questions:
#             # No more questions available
#             session.status = 'completed'
#             session.completed_at = datetime.now(timezone.utc)
#             session.termination_reason = 'no_more_questions'
#             db.session.commit()
#             
#             return jsonify({
#                 'success': True,
#                 'session_completed': True,
#                 'termination_reasons': ['no_more_questions']
#             })
#         
#         # Select next question
#         next_question = irt_engine.select_next_question(session, available_questions)
#         
#         if not next_question:
#             return jsonify({
#                 'success': False,
#                 'error': 'Не удалось выбрать следующий вопрос'
#             }), 400
#         
#         return jsonify({
#             'success': True,
#             'question': {
#                 'id': next_question.id,
#                 'text': next_question.text,
#                 'options': next_question.get_options_list(),
#                 'image_filename': next_question.image_filename,
#                 'domain': next_question.big_domain.name if next_question.big_domain else None,
#                 'difficulty_level': next_question.difficulty_level
#             },
#             'session_info': {
#                 'current_ability': float(session.current_ability) if session.current_ability is not None else 0.0,
#                 'ability_se': float(session.ability_se) if session.ability_se is not None else 1.0,
#                 'questions_answered': int(session.questions_answered) if session.questions_answered is not None else 0
#             }
#         })
#         
#     except Exception as e:
#         logger.error(f"Error getting next question: {e}")
#         return jsonify({
#             'success': False,
#             'error': 'Ошибка при получении вопроса'
#         }), 500

# @test_bp.route('/big-diagnostic/submit-answer', methods=['POST'])
# @login_required
# def submit_diagnostic_answer():
#     """Submit answer for diagnostic question - MOVED TO diagnostic_bp"""
#     try:
#         data = request.get_json()
#         session_id = data.get('session_id')
#         question_id = data.get('question_id')
#         selected_answer = data.get('selected_answer')
#         response_time = data.get('response_time')  # Seconds
#         
#         # Validate session
#         session = DiagnosticSession.query.filter_by(
#             id=session_id,
#             user_id=current_user.id,
#             status='active'
#         ).first()
#         
#         if not session:
#             return jsonify({
#                 'success': False,
#                 'error': 'Сессия не найдена или завершена'
#             }), 404
#         
#         # Get question
#         question = Question.query.get(question_id)
#         if not question:
#             return jsonify({
#                 'success': False,
#                 'error': 'Вопрос не найден'
#             }), 404
#         
#         # Check if already answered
#         existing_response = DiagnosticResponse.query.filter_by(
#             session_id=session_id,
#             question_id=question_id
#         ).first()
#         
#         if existing_response:
#             return jsonify({
#                 'success': False,
#                 'error': 'Вопрос уже отвечен'
#             }), 400
#         
#         # Check answer
#         is_correct = question.check_answer(selected_answer)
#         
#         # Create response record
#         response = DiagnosticResponse(
#             session_id=session_id,
#             question_id=question_id,
#             selected_answer=selected_answer,
#             is_correct=is_correct,
#             response_time=response_time
#         )
#         
#         db.session.add(response)
#         
#         # Update session ability
#         update_result = irt_engine.update_session_ability(
#             session, question, is_correct, response_time
#         )
#         
#         if 'error' in update_result:
#             return jsonify({
#                 'success': False,
#                 'error': update_result['error']
#             }), 400
#         
#         # Check if session should terminate
#         if update_result['termination_info']['should_terminate']:
#             session.status = 'completed'
#             session.completed_at = datetime.now(timezone.utc)
#             session.termination_reason = update_result['termination_info']['reasons'][0]
#         
#         db.session.commit()
#         
#         return jsonify({
#             'success': True,
#             'is_correct': is_correct,
#             'correct_answer': question.correct_answer,
#             'explanation': question.explanation,
#             'session_updated': {
#                 'ability': update_result['ability'],
#                 'standard_error': update_result['standard_error'],
#                 'accuracy': update_result['accuracy'],
#                 'questions_answered': update_result['questions_answered']
#             },
#             'session_completed': session.status == 'completed'
#         })
#         
#     except Exception as e:
#         logger.error(f"Error submitting answer: {e}")
#         db.session.rollback()
#         return jsonify({
#             'success': False,
#             'error': 'Ошибка при отправке ответа'
#         }), 500

# @test_bp.route('/big-diagnostic/end-session', methods=['POST'])
# @login_required
# def end_diagnostic_session():
#     """End active diagnostic session - MOVED TO diagnostic_bp"""
#     try:
#         # Find active session for current user
#         active_session = DiagnosticSession.query.filter_by(
#             user_id=current_user.id,
#             status='active'
#         ).first()
#         
#         if not active_session:
#             return jsonify({
#                 'success': False,
#                 'error': 'Активная сессия не найдена'
#             }), 404
#         
#         # End the session
#         active_session.status = 'cancelled'
#         active_session.completed_at = datetime.now(timezone.utc)
#         active_session.termination_reason = 'user_cancelled'
#         
#         db.session.commit()
#         
#         return jsonify({
#             'success': True,
#             'message': 'Сессия успешно завершена'
#         })
#         
#     except Exception as e:
#         logger.error(f"Error ending session: {e}")
#         db.session.rollback()
#         return jsonify({
#             'success': False,
#             'error': 'Ошибка при завершении сессии'
#         }), 500

# @test_bp.route('/big-diagnostic/results/<int:session_id>')
# @login_required
# def get_diagnostic_results(session_id):
#     """Get detailed results for completed diagnostic session - MOVED TO diagnostic_bp"""
#     try:
#         session = DiagnosticSession.query.filter_by(
#             id=session_id,
#             user_id=current_user.id,
#             status='completed'
#         ).first()
#         
#         if not session:
#             return jsonify({
#                 'success': False,
#                 'error': 'Сессия не найдена или не завершена'
#             }), 404
#         
#         # Generate domain analysis
#         domain_analysis = irt_engine.generate_domain_analysis(session)
#         
#         # Calculate exam readiness
#         readiness_analysis = irt_engine.calculate_exam_readiness(domain_analysis)
#         
#         # Get ability progression
#         ability_history = session.get_ability_history()
#         
#         return jsonify({
#             'success': True,
#             'session_info': {
#                 'id': session.id,
#                 'session_type': session.session_type,
#                 'started_at': session.started_at.isoformat(),
#                 'completed_at': session.completed_at.isoformat(),
#                 'questions_answered': session.questions_answered,
#                 'correct_answers': session.correct_answers,
#                 'accuracy': session.get_accuracy(),
#                 'termination_reason': session.termination_reason
#             },
#             'final_results': {
#                 'ability': session.current_ability,
#                 'standard_error': session.ability_se,
#                 'readiness': readiness_analysis['readiness'],
#                 'confidence': readiness_analysis['confidence']
#             },
#             'domain_analysis': domain_analysis,
#             'readiness_analysis': readiness_analysis,
#             'ability_history': ability_history
#         })
#         
#     except Exception as e:
#         logger.error(f"Error getting results: {e}")
#         return jsonify({
#             'success': False,
#             'error': 'Ошибка при получении результатов'
#         }), 500

@test_bp.route('/learning-plan/generate', methods=['POST'])
@login_required
def generate_learning_plan():
    """Generate personalized learning plan based on diagnostic results"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        exam_date = data.get('exam_date')  # Optional
        study_hours_per_week = data.get('study_hours_per_week', 20.0)
        
        # Get diagnostic session
        session = DiagnosticSession.query.filter_by(
            id=session_id,
            user_id=current_user.id,
            status='completed'
        ).first()
        
        if not session:
            return jsonify({
                'success': False,
                'error': 'Диагностическая сессия не найдена'
            }), 404
        
        # Generate domain analysis
        domain_analysis = irt_engine.generate_domain_analysis(session)
        readiness_analysis = irt_engine.calculate_exam_readiness(domain_analysis)
        
        # Check if plan already exists
        existing_plan = PersonalLearningPlan.query.filter_by(
            user_id=current_user.id,
            status='active'
        ).first()
        
        if existing_plan:
            existing_plan.status = 'paused'
        
        # Create new learning plan
        plan = PersonalLearningPlan(
            user_id=current_user.id,
            exam_date=exam_date,
            study_hours_per_week=study_hours_per_week,
            current_ability=session.current_ability,
            target_ability=0.5,  # Target for BI-toets
            overall_progress=0.0
        )
        
        # Set domain analysis
        plan.set_domain_analysis(domain_analysis)
        plan.set_weak_domains(readiness_analysis['weak_domains'])
        plan.set_strong_domains(readiness_analysis['strong_domains'])
        
        # Calculate estimated readiness
        plan.estimated_readiness = readiness_analysis['readiness']
        
        # Generate study schedule (simplified)
        study_schedule = _generate_study_schedule(
            readiness_analysis['weak_domains'],
            study_hours_per_week,
            exam_date
        )
        plan.set_study_schedule(study_schedule)
        
        # Generate milestones
        milestones = _generate_milestones(exam_date, study_hours_per_week)
        plan.set_milestones(milestones)
        
        db.session.add(plan)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'plan_id': plan.id,
            'plan_summary': {
                'current_ability': plan.current_ability,
                'target_ability': plan.target_ability,
                'estimated_readiness': plan.estimated_readiness,
                'weak_domains_count': len(readiness_analysis['weak_domains']),
                'strong_domains_count': len(readiness_analysis['strong_domains'])
            },
            'study_schedule': study_schedule,
            'milestones': milestones
        })
        
    except Exception as e:
        logger.error(f"Error generating learning plan: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Ошибка при создании плана обучения'
        }), 500

@test_bp.route('/learning-plan/<int:plan_id>')
@login_required
def get_learning_plan(plan_id):
    """Get detailed learning plan"""
    try:
        plan = PersonalLearningPlan.query.filter_by(
            id=plan_id,
            user_id=current_user.id
        ).first()
        
        if not plan:
            return jsonify({
                'success': False,
                'error': 'План обучения не найден'
            }), 404
        
        return jsonify({
            'success': True,
            'plan': {
                'id': plan.id,
                'exam_date': plan.exam_date.isoformat() if plan.exam_date else None,
                'current_ability': plan.current_ability,
                'target_ability': plan.target_ability,
                'overall_progress': plan.overall_progress,
                'estimated_readiness': plan.estimated_readiness,
                'study_hours_per_week': plan.study_hours_per_week,
                'status': plan.status,
                'last_updated': plan.last_updated.isoformat()
            },
            'domain_analysis': plan.get_domain_analysis(),
            'weak_domains': plan.get_weak_domains(),
            'strong_domains': plan.get_strong_domains(),
            'study_schedule': plan.get_study_schedule(),
            'milestones': plan.get_milestones()
        })
        
    except Exception as e:
        logger.error(f"Error getting learning plan: {e}")
        return jsonify({
            'success': False,
            'error': 'Ошибка при получении плана обучения'
        }), 500

# ========================================
# HELPER FUNCTIONS
# ========================================

def _generate_study_schedule(weak_domains, study_hours_per_week, exam_date):
    """Generate weekly study schedule based on weak domains"""
    schedule = {
        'weekly_hours': study_hours_per_week,
        'weeks': []
    }
    
    # Simple schedule generation
    for i, domain in enumerate(weak_domains[:8]):  # Focus on top 8 weak domains
        week = {
            'week_number': i + 1,
            'focus_domain': domain['code'],
            'domain_name': domain['name'],
            'hours': min(study_hours_per_week, 25),  # Cap at 25 hours
            'topics': [
                f"Основы {domain['name']}",
                f"Клинические случаи {domain['name']}",
                f"Практические навыки {domain['name']}"
            ]
        }
        schedule['weeks'].append(week)
    
    return schedule

def _generate_milestones(exam_date, study_hours_per_week):
    """Generate milestone dates for learning plan"""
    milestones = []
    
    if exam_date:
        from datetime import timedelta
        
        # Calculate weeks until exam
        weeks_until_exam = (exam_date - datetime.now().date()).days // 7
        
        # Generate milestones
        milestone_percentages = [25, 50, 75, 90]
        for percentage in milestone_percentages:
            weeks_offset = int(weeks_until_exam * (1 - percentage / 100))
            milestone_date = exam_date - timedelta(weeks=weeks_offset)
            
            milestones.append({
                'percentage': percentage,
                'date': milestone_date.isoformat(),
                'description': f"Достигнуть {percentage}% готовности к экзамену"
            })
    
    return milestones 