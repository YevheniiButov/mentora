import logging
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app, g, session
from flask_login import login_required, current_user
from utils.daily_learning_algorithm import DailyLearningAlgorithm, generate_from_personal_plan, create_emergency_plan
from utils.domain_mapping import get_domain_name
from extensions import db
from models import UserProgress, Lesson, PersonalLearningPlan
import random
import json
import os
from datetime import datetime, timezone

logger = logging.getLogger(__name__)
daily_learning_bp = Blueprint('daily_learning', __name__, url_prefix='/<string:lang>')

# Поддерживаемые языки
SUPPORTED_LANGUAGES = ['en', 'ru', 'nl', 'uk', 'es', 'pt', 'tr', 'fa', 'ar']
DEFAULT_LANGUAGE = 'en'

@daily_learning_bp.before_request
def before_request_daily_learning():
    """Обработка языка для всех маршрутов daily_learning"""
    # Просто обрабатываем язык, без проверок - Flask сам определит правильный blueprint
    lang_from_url = request.view_args.get('lang') if request.view_args else None
    
    if lang_from_url and lang_from_url in SUPPORTED_LANGUAGES:
        g.lang = lang_from_url
    else:
        g.lang = session.get('lang') or DEFAULT_LANGUAGE
    
    # Обновляем сессию
    if session.get('lang') != g.lang:
        session['lang'] = g.lang

@daily_learning_bp.context_processor
def inject_lang_daily_learning():
    """Добавляет lang в контекст шаблонов этого блюпринта."""
    lang = getattr(g, 'lang', session.get('lang', DEFAULT_LANGUAGE))
    return dict(lang=lang)



def _adapt_daily_plan_for_template(daily_plan_result):
    """
    Адаптирует результат generate_from_personal_plan для шаблона learning_map.html
    """
    if not daily_plan_result.get('success'):
        return daily_plan_result
    
    # Получаем данные из результата
    domains_data = daily_plan_result.get('daily_plan', {}).get('domains', {})
    
    # Создаем структуру для шаблона
    adapted_plan = {
        'sections': {
            'theory': {
                'title': 'Теория',
                'content_items': [],
                'total_time': 0,
                'estimated_time': 0
            },
            'practice': {
                'title': 'Практика',
                'content_items': [],
                'total_time': 0,
                'estimated_time': 0
            },
            'review': {
                'title': 'Повторение',
                'content_items': [],
                'total_time': 0,
                'estimated_time': 0
            }
        },
        'target_minutes': daily_plan_result.get('daily_plan', {}).get('total_time', 30),
        'total_time': daily_plan_result.get('daily_plan', {}).get('total_time', 30)
    }
    
    # Преобразуем данные доменов в секции
    for domain_code, domain_data in domains_data.items():
        domain_name = get_domain_name(domain_code) or domain_code
        
        # Теория
        for theory_item in domain_data.get('theory', []):
            adapted_item = {
                'id': f"theory_{theory_item.get('id', domain_code)}",
                'title': theory_item.get('title', f'Изучение {domain_name}'),
                'type': 'theory',
                'domain': domain_code,
                'difficulty': theory_item.get('difficulty', 'medium'),
                'estimated_time': theory_item.get('time_minutes', 10),
                'description': theory_item.get('description', f'Теоретический материал по теме {domain_name}')
            }
            adapted_plan['sections']['theory']['content_items'].append(adapted_item)
            adapted_plan['sections']['theory']['total_time'] += adapted_item['estimated_time']
            adapted_plan['sections']['theory']['estimated_time'] += adapted_item['estimated_time']
        
        # Практика
        for practice_item in domain_data.get('practice', []):
            adapted_item = {
                'id': f"practice_{practice_item.get('id', domain_code)}",
                'title': practice_item.get('title', f'Практика {domain_name}'),
                'type': 'practice',
                'domain': domain_code,
                'difficulty': practice_item.get('difficulty', 'medium'),
                'estimated_time': practice_item.get('time_minutes', 15),
                'description': practice_item.get('description', f'Практические задания по теме {domain_name}'),
                'questions_count': practice_item.get('questions_count', 5)
            }
            adapted_plan['sections']['practice']['content_items'].append(adapted_item)
            adapted_plan['sections']['practice']['total_time'] += adapted_item['estimated_time']
            adapted_plan['sections']['practice']['estimated_time'] += adapted_item['estimated_time']
    
    # Обновляем результат
    daily_plan_result['daily_plan'] = adapted_plan
    return daily_plan_result

# Removed - conflicts with learning_map_bp
# @daily_learning_bp.route('/learning-map')
# @login_required
# def learning_map(lang):
#     """Redirect to real learning map"""
#     from flask import redirect, url_for, g
#     return redirect(url_for('learning_map_bp.learning_map', lang=lang, path_id='irt'))

@daily_learning_bp.route('/knowledge-base', strict_slashes=False)
@login_required  
def knowledge_base(lang):
    """Knowledge Base coming soon page - скрыта от пользователей"""
    from flask import abort
    # Скрываем страницу от всех пользователей
    abort(404)

# API Endpoints for Knowledge Base
@daily_learning_bp.route('/api/subject/<int:subject_id>/stats')
@login_required
def get_subject_stats(subject_id):
    """Получает статистику предмета"""
    from models import Subject, Module, Lesson
    from utils.unified_stats import get_module_stats_unified
    
    try:
        subject = Subject.query.get_or_404(subject_id)
        
        # Получаем все модули предмета
        modules = Module.query.filter_by(subject_id=subject_id).all()
        
        total_lessons = 0
        completed_lessons = 0
        
        for module in modules:
            module_stats = get_module_stats_unified(module.id, current_user.id)
            total_lessons += module_stats.get("total_lessons", 0)
            completed_lessons += module_stats.get("completed_lessons", 0)
        
        # Вычисляем прогресс
        progress_percentage = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
        
        return {
            'subject_id': subject_id,
            'subject_name': subject.name,
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'progress_percentage': progress_percentage,
            'estimated_time': f"{max(1, total_lessons // 10)}h"
        }
        
    except Exception as e:
        current_app.logger.error(f"Ошибка при получении статистики предмета {subject_id}: {e}", exc_info=True)
        return {'error': 'Ошибка загрузки данных'}, 500

@daily_learning_bp.route('/api/subject/<int:subject_id>/modules')
@login_required
def get_subject_modules(subject_id):
    """Получает модули предмета"""
    from models import Subject, Module, Lesson
    from utils.unified_stats import get_module_stats_unified
    
    try:
        subject = Subject.query.get_or_404(subject_id)
        modules = Module.query.filter_by(subject_id=subject_id).order_by(Module.order).all()
        
        modules_data = []
        for module in modules:
            module_stats = get_module_stats_unified(module.id, current_user.id)
            
            modules_data.append({
                'id': module.id,
                'title': module.title,
                'description': getattr(module, 'description', ''),
                'lessons_count': module_stats.get("total_lessons", 0),
                'completed_lessons': module_stats.get("completed_lessons", 0),
                'progress': module_stats.get("progress_percentage", 0),
                'estimated_time': f"{max(1, module_stats.get('total_lessons', 0) // 5)}h"
            })
        
        return {
            'subject_id': subject_id,
            'modules': modules_data
        }
        
    except Exception as e:
        current_app.logger.error(f"Ошибка при получении модулей предмета {subject_id}: {e}", exc_info=True)
        return {'error': 'Ошибка загрузки модулей'}, 500

@daily_learning_bp.route('/api/daily-plan/mark-completed', methods=['POST'])
@login_required
def mark_daily_plan_item_completed():
    """Отмечает элемент ежедневного плана как выполненный"""
    from models import UserProgress, StudySession
    from models import PersonalLearningPlan
    import json
    
    try:
        data = request.get_json()
        content_id = data.get('content_id')
        content_type = data.get('content_type')
        
        if not content_id or not content_type:
            return {'error': 'Missing content_id or content_type'}, 400
        
        # Создаем запись о выполнении
        if content_type == 'lesson':
            # Отмечаем урок как завершенный
            progress = UserProgress.query.filter_by(
                user_id=current_user.id,
                lesson_id=content_id
            ).first()
            
            # Check if this is a new completion
            was_completed_before = progress.completed if progress else False
            
            if not progress:
                progress = UserProgress(
                    user_id=current_user.id,
                    lesson_id=content_id,
                    completed=True,
                    completed_at=datetime.now(timezone.utc)
                )
                db.session.add(progress)
            else:
                progress.completed = True
                progress.completed_at = datetime.now(timezone.utc)
            
            # ✅ FIX: Update daily activity when lesson is newly completed
            if not was_completed_before:
                xp_earned = 10
                current_user.update_daily_activity(
                    lessons_completed=1,
                    time_spent=0,
                    xp_earned=xp_earned
                )
        
        elif content_type == 'question':
            # Отмечаем вопрос как изученный
            # Здесь можно добавить логику для вопросов
            pass
        
        elif content_type == 'spaced_repetition':
            # Обновляем spaced repetition элемент
            # Здесь можно добавить логику для повторений
            pass
        
        # Создаем сессию изучения
        # Получаем активный план обучения пользователя
        active_plan = PersonalLearningPlan.query.filter_by(
            user_id=current_user.id,
            status='active'
        ).first()
        
        if active_plan:
            study_session = StudySession(
                learning_plan_id=active_plan.id,
                session_type=content_type,
                domain_id=None,  # Можно добавить логику определения домена
                content_ids=json.dumps([content_id]),
                actual_duration=5,  # Примерная длительность в минутах
                completed_at=datetime.now(timezone.utc),
                status='completed'
            )
            db.session.add(study_session)
        
        db.session.commit()
        
        # ✅ Clear cache after progress update
        from utils.diagnostic_data_manager import clear_cache
        clear_cache(current_user.id)
        
        return {'success': True, 'message': 'Item marked as completed'}
        
    except Exception as e:
        current_app.logger.error(f"Ошибка при отметке выполнения: {e}", exc_info=True)
        db.session.rollback()
        return {'error': 'Ошибка при отметке выполнения'}, 500

@daily_learning_bp.route('/api/study-session/<int:session_id>/complete', methods=['POST'])
@login_required
def complete_study_session(session_id):
    """Complete a study session and update progress"""
    from models import StudySession, PersonalLearningPlan, BIGDomain
    from utils.daily_learning_algorithm import DailyLearningAlgorithm
    
    try:
        session = StudySession.query.get_or_404(session_id)
        
        # Verify ownership
        if session.learning_plan.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        data = request.get_json()
        
        # Update session with results
        session.complete_session(
            actual_duration=data.get('duration_minutes'),
            accuracy=data.get('accuracy')
        )
        
        # Update questions answered and correct
        if 'questions_answered' in data:
            session.questions_answered = data['questions_answered']
        if 'correct_answers' in data:
            session.correct_answers = data['correct_answers']
        
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Обновляем план обучения
        learning_plan = session.learning_plan
        plan_updated = learning_plan.update_progress_from_session(session)
        
        if not plan_updated:
            current_app.logger.warning(f"Failed to update learning plan {learning_plan.id} from session {session.id}")
        
        db.session.commit()
        
        # Trigger ability recalculation for additional updates
        algorithm = DailyLearningAlgorithm()
        try:
            algorithm._analyze_current_abilities(current_user.id)
        except Exception as e:
            current_app.logger.error(f"Failed to update abilities: {e}")
        
        return jsonify({
            'success': True,
            'session_id': session.id,
            'status': session.status,
            'plan_updated': plan_updated,
            'new_progress': learning_plan.overall_progress,
            'new_ability': learning_plan.current_ability
        })
        
    except Exception as e:
        current_app.logger.error(f"Error completing study session: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to complete session'}), 500


@daily_learning_bp.route('/api/session/answer', methods=['POST'])
@login_required
def submit_session_answer():
    """Submit answer during study session for IRT feedback"""
    from models import StudySessionResponse, StudySession
    
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        question_id = data.get('question_id')
        is_correct = data.get('is_correct')
        response_time = data.get('response_time')  # milliseconds
        
        # Validate session ownership
        session = StudySession.query.get_or_404(session_id)
        if session.learning_plan.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Create response record
        response = StudySessionResponse(
            session_id=session_id,
            question_id=question_id,
            is_correct=is_correct,
            response_time=response_time
        )
        
        db.session.add(response)
        
        # Update session statistics
        session.questions_answered = (session.questions_answered or 0) + 1
        if is_correct:
            session.correct_answers = (session.correct_answers or 0) + 1
        
        db.session.commit()
        
        return jsonify({'status': 'success'})
        
    except Exception as e:
        current_app.logger.error(f"Error submitting session answer: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to submit answer'}), 500


@daily_learning_bp.route('/api/session/complete', methods=['POST'])
@login_required
def complete_study_session_with_irt():
    """Complete study session and update ability using IRT with conflict protection"""
    from models import StudySession
    from utils.irt_engine import update_ability_from_session_responses
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'error': 'session_id is required'}), 400
        
        session = StudySession.query.get_or_404(session_id)
        
        # Verify ownership
        if session.learning_plan.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Check if session is already completed
        if session.status == 'completed':
            return jsonify({
                'status': 'already_completed',
                'session_id': session_id,
                'ability_updated': session.ability_updated,
                'feedback_processed': session.feedback_processed
            })
        
        # Mark session as completed
        session.status = 'completed'
        session.completed_at = datetime.now(timezone.utc)
        
        # КРИТИЧЕСКОЕ ИСПРАВЛЕНИЕ: Обновляем план обучения
        learning_plan = session.learning_plan
        plan_updated = learning_plan.update_progress_from_session(session)
        
        if not plan_updated:
            logger.warning(f"Failed to update learning plan {learning_plan.id} from session {session_id}")
        
        db.session.commit()
        
        # Update user ability based on responses (with conflict protection)
        try:
            new_ability = update_ability_from_session_responses(
                user_id=current_user.id,
                session_id=session_id
            )
            
            if new_ability is not None:
                return jsonify({
                    'status': 'success',
                    'session_id': session_id,
                    'updated_ability': new_ability,
                    'ability_updated': session.ability_updated,
                    'feedback_processed': session.feedback_processed,
                    'plan_updated': plan_updated,
                    'new_progress': learning_plan.overall_progress,
                    'new_ability': learning_plan.current_ability,
                    'message': 'Session completed and ability updated successfully'
                })
            else:
                return jsonify({
                    'status': 'success',
                    'session_id': session_id,
                    'ability_updated': session.ability_updated,
                    'feedback_processed': session.feedback_processed,
                    'plan_updated': plan_updated,
                    'new_progress': learning_plan.overall_progress,
                    'new_ability': learning_plan.current_ability,
                    'message': 'Session completed but ability update failed',
                    'warning': 'No valid responses found or IRT parameters missing'
                })
            
        except Exception as e:
            logger.error(f"Error updating ability: {str(e)}")
            return jsonify({
                'status': 'success',
                'session_id': session_id,
                'message': 'Session completed but ability update failed',
                'error': str(e)
            })
        
    except Exception as e:
        logger.error(f"Error completing study session: {e}")
        db.session.rollback()
        return jsonify({'error': 'Failed to complete session'}), 500


@daily_learning_bp.route('/api/session/<int:session_id>/feedback', methods=['POST'])
@login_required
def process_session_feedback(session_id):
    """Process feedback for a completed study session"""
    from models import StudySession
    from utils.irt_engine import update_ability_from_session_responses
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        session = StudySession.query.get_or_404(session_id)
        
        # Verify ownership
        if session.learning_plan.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Check if session is completed
        if session.status != 'completed':
            return jsonify({'error': 'Session is not completed'}), 400
        
        # Check if feedback already processed
        if session.feedback_processed:
            return jsonify({
                'status': 'already_processed',
                'session_id': session_id,
                'ability_after': session.session_ability_after,
                'ability_change': session.ability_change
            })
        
        # Process feedback
        new_ability = update_ability_from_session_responses(
            user_id=current_user.id,
            session_id=session_id
        )
        
        if new_ability is not None:
            return jsonify({
                'status': 'success',
                'session_id': session_id,
                'ability_before': session.session_ability_before,
                'ability_after': new_ability,
                'ability_change': session.ability_change,
                'confidence': session.ability_confidence,
                'message': 'Feedback processed successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'session_id': session_id,
                'message': 'Failed to process feedback',
                'error': 'No valid responses or IRT parameters'
            }), 400
        
    except Exception as e:
        logger.error(f"Error processing session feedback: {e}")
        return jsonify({'error': 'Failed to process feedback'}), 500


@daily_learning_bp.route('/api/session/<int:session_id>/retry-feedback', methods=['POST'])
@login_required
def retry_session_feedback(session_id):
    """Retry processing feedback for a study session (force reprocess)"""
    from models import StudySession
    from utils.irt_engine import update_ability_from_session_responses
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        session = StudySession.query.get_or_404(session_id)
        
        # Verify ownership
        if session.learning_plan.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Reset feedback processing flags
        session.feedback_processed = False
        session.ability_updated = False
        db.session.commit()
        
        # Process feedback
        new_ability = update_ability_from_session_responses(
            user_id=current_user.id,
            session_id=session_id
        )
        
        if new_ability is not None:
            return jsonify({
                'status': 'success',
                'session_id': session_id,
                'ability_before': session.session_ability_before,
                'ability_after': new_ability,
                'ability_change': session.ability_change,
                'confidence': session.ability_confidence,
                'message': 'Feedback reprocessed successfully'
            })
        else:
            return jsonify({
                'status': 'error',
                'session_id': session_id,
                'message': 'Failed to reprocess feedback'
            }), 400
        
    except Exception as e:
        logger.error(f"Error retrying session feedback: {e}")
        return jsonify({'error': 'Failed to retry feedback'}), 500


@daily_learning_bp.route('/api/session/<int:session_id>/feedback-status', methods=['GET'])
@login_required
def get_session_feedback_status(session_id):
    """Get feedback processing status for a study session"""
    from models import StudySession
    
    try:
        session = StudySession.query.get_or_404(session_id)
        
        # Verify ownership
        if session.learning_plan.user_id != current_user.id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify({
            'session_id': session_id,
            'status': session.status,
            'ability_updated': session.ability_updated,
            'feedback_processed': session.feedback_processed,
            'ability_before': session.session_ability_before,
            'ability_after': session.session_ability_after,
            'ability_change': session.ability_change,
            'confidence': session.ability_confidence,
            'last_ability_update': session.last_ability_update.isoformat() if session.last_ability_update else None
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to get feedback status'}), 500


@daily_learning_bp.route('/reassessment-required')
@login_required
def reassessment_required(lang):
    """Показывает страницу с требованием переоценки и прямой ссылкой на диагностику"""
    from datetime import date
    from models import PersonalLearningPlan
    
    try:
        # Получаем активный план пользователя
        active_plan = PersonalLearningPlan.query.filter_by(
            user_id=current_user.id,
            status='active'
        ).first()
        
        days_overdue = 0
        next_diagnostic_date = None
        
        if active_plan and active_plan.next_diagnostic_date:
            today = date.today()
            if active_plan.next_diagnostic_date < today:
                days_overdue = (today - active_plan.next_diagnostic_date).days
            next_diagnostic_date = active_plan.next_diagnostic_date
        
        # Определяем сообщение в зависимости от количества дней просрочки
        if days_overdue > 7:
            urgency_level = 'critical'
            message = f'Переоценка просрочена на {days_overdue} дней. Ваши данные устарели и требуют обновления.'
        elif days_overdue > 3:
            urgency_level = 'warning'
            message = f'Переоценка просрочена на {days_overdue} дней. Рекомендуется пройти переоценку для точного планирования обучения.'
        else:
            urgency_level = 'info'
            message = f'Переоценка просрочена на {days_overdue} дней. Пройдите переоценку для продолжения обучения.'
        
        return render_template('daily_learning/reassessment_required.html',
                             days_overdue=days_overdue,
                             plan=active_plan,
                             next_diagnostic_date=next_diagnostic_date,
                             urgency_level=urgency_level,
                             message=message,
                             lang=lang)
        
    except Exception as e:
        logger.error(f"Error in reassessment_required: {e}")
        flash('Произошла ошибка при загрузке страницы переоценки', 'error')
        lang = session.get('lang', 'nl')
        return redirect(url_for('learning_map_bp.learning_map', lang=lang)) 