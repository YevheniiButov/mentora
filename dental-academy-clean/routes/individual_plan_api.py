"""
API endpoints for Individual Plan functionality.

This module provides REST API endpoints for:
- Daily tasks management
- Progress tracking
- Daily session handling
- Progress updates
"""

from flask import Blueprint, jsonify, redirect, url_for, request, session, current_app, flash
from flask_login import login_required, current_user
from utils.individual_plan_helpers import (
    get_daily_tasks,
    get_progress_summary,
    update_daily_progress,
    select_questions_for_today
)
from utils.rate_limiter import rate_limiter

individual_plan_api_bp = Blueprint('individual_plan_api', __name__)

def rate_limit(requests_per_minute=120):
    """Rate limiting decorator for API endpoints"""
    def decorator(f):
        from functools import wraps
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_id = current_user.id if current_user.is_authenticated else request.remote_addr
            if not rate_limiter.check_rate_limit(user_id, requests_per_minute):
                return jsonify({
                    'success': False,
                    'error': 'Rate limit exceeded. Please try again later.'
                }), 429
            return f(*args, **kwargs)
        return decorated_function
    return decorator


@individual_plan_api_bp.route('/api/individual-plan/daily-tasks')
@login_required
@rate_limit(requests_per_minute=180)  # 180 requests per minute for learning-map APIs
def api_daily_tasks():
    """
    Get today's daily tasks for the user.
    
    Returns:
        JSON: {
            'tasks': {
                'new_questions': int,
                'reviews_due': int,
                'total_tasks': int,
                'estimated_time': int,
                'goal': int,
                'time_goal': int
            },
            'questions_today': int
        }
    """
    try:
        daily_tasks = get_daily_tasks(current_user)
        
        # Get today's questions count (placeholder - would query UserActivity)
        from models import UserActivity
        from datetime import date
        
        today_activity = UserActivity.query.filter_by(
            user_id=current_user.id,
            activity_date=date.today()
        ).first()
        
        questions_today = today_activity.lessons_completed if today_activity else 0
        
        return jsonify({
            'tasks': daily_tasks,
            'questions_today': questions_today
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@individual_plan_api_bp.route('/api/individual-plan/progress')
@login_required
@rate_limit(requests_per_minute=180)  # 180 requests per minute for learning-map APIs
def api_progress_summary():
    """
    Get comprehensive progress summary.
    
    Returns:
        JSON: {
            'overall_progress': float,
            'daily_streak': int,
            'longest_streak': int,
            'questions_today': int,
            'time_today': int,
            'daily_goal': int,
            'time_goal': int,
            'categories': list,
            'weak_categories': list,
            'sr_stats': dict,
            'time_invested': int,
            'learning_velocity': float,
            'retention_rate': float
        }
    """
    try:
        from utils.helpers import get_user_profession_code
        
        # DEBUG
        profession = get_user_profession_code(current_user)
        current_app.logger.info(f"🔍 API Progress - User {current_user.id}, profession: {profession}")
        
        progress = get_progress_summary(current_user)
        
        # Log categories
        current_app.logger.info(f"🔍 API Progress - categories count: {len(progress.get('categories', []))}, percentages: {[c['percentage'] for c in progress.get('categories', [])]}")
        
        return jsonify(progress)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@individual_plan_api_bp.route('/api/individual-plan/data')
@login_required
def api_individual_plan_data():
    """Get individual plan data for the Individual Plan tab"""
    try:
        from models import UserActivity
        from datetime import date
        from utils.domain_helpers import get_category_summary
        from utils.helpers import get_user_profession_code
        
        # Get daily tasks
        daily_tasks = get_daily_tasks(current_user)
        
        # Get today's activity
        today_activity = UserActivity.query.filter_by(
            user_id=current_user.id,
            activity_date=date.today()
        ).first()
        
        questions_today = today_activity.lessons_completed if today_activity else 0
        
        # Get categories
        profession = get_user_profession_code(current_user)
        categories = get_category_summary(current_user, profession)
        
        # Get progress summary
        progress_data = get_progress_summary(current_user)
        
        return jsonify({
            'daily_tasks': daily_tasks,
            'questions_today': questions_today,
            'daily_streak': progress_data.get('daily_streak', 0),
            'categories': categories,
            'weak_categories': progress_data.get('weak_categories', [])
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@individual_plan_api_bp.route('/learning-map/daily-session')
@login_required
def start_daily_session():
    """
    Start today's daily learning session.
    Redirects to IRT practice with today's selected questions.
    """
    # Check if profile is complete
    from utils.profile_check import check_profile_complete
    profile_check = check_profile_complete(current_user)
    
    if not profile_check['is_complete']:
        lang = session.get('lang', 'nl')
        return redirect(url_for('learning_map_bp.complete_profile', lang=lang))
    
    # КРИТИЧНО: Проверяем, прошёл ли пользователь диагностику
    from utils.diagnostic_check import check_diagnostic_completed, get_diagnostic_redirect_url
    if not check_diagnostic_completed(current_user.id):
        lang = session.get('lang', 'nl')
        flash('Для начала обучения необходимо пройти диагностический тест. Это поможет создать персонализированный план обучения.', 'info')
        current_app.logger.info(f"User {current_user.id} redirected to diagnostic from start_daily_session")
        return redirect(get_diagnostic_redirect_url(lang))
    
    try:
        from utils.individual_plan_helpers import get_or_create_learning_plan, select_questions_for_today
        from models import DiagnosticSession
        
        current_app.logger.info(f"🔄 Starting daily session for user {current_user.id}")
        
        # Get or create learning plan
        try:
            plan = get_or_create_learning_plan(current_user)
            current_app.logger.info(f"✅ Learning plan retrieved/created: {plan.id if plan else None}")
        except Exception as e:
            current_app.logger.error(f"❌ Error getting/creating learning plan: {e}", exc_info=True)
            raise
        
        if not plan:
            flash('Kon geen leerplan vinden. Start eerst een diagnostische test.', 'warning')
            return redirect(url_for('dashboard.index'))
        
        # Select today's questions
        try:
            questions = select_questions_for_today(current_user, count=20)
            current_app.logger.info(f"✅ Selected {len(questions) if questions else 0} questions for today")
        except Exception as e:
            current_app.logger.error(f"❌ Error selecting questions: {e}", exc_info=True)
            raise
        
        # If no questions available, try with a smaller count or continue anyway
        if not questions:
            current_app.logger.warning(f"⚠️ No questions available for user {current_user.id}, trying smaller count")
            questions = select_questions_for_today(current_user, count=10)
            if not questions:
                flash('Geen vragen beschikbaar. Probeer later opnieuw.', 'warning')
                return redirect(url_for('learning_map_bp.learning_map', lang=session.get('lang', 'nl'), path_id='irt'))
        
        # ✅ Create a DiagnosticSession for tracking today's practice
        try:
            from datetime import datetime, timezone
            diagnostic_session = DiagnosticSession.create_session(
                user_id=current_user.id,
                session_type='daily_practice',
                ip_address=request.remote_addr
            )
            current_app.logger.info(f"✅ Diagnostic session created: {diagnostic_session.id}")
        except Exception as e:
            current_app.logger.error(f"❌ Error creating diagnostic session: {e}", exc_info=True)
            raise
        
        # Store question IDs and session IDs in Flask session for practice
        session['daily_session_questions'] = [q.id for q in questions]
        session['daily_session_diagnostic_id'] = diagnostic_session.id  # Store diagnostic session ID
        session['daily_session_active'] = True
        # Track the calendar day for auto-rotation
        from datetime import date as _date
        session['daily_session_date'] = _date.today().isoformat()
        session['learning_plan_id'] = plan.id
        session['learning_mode'] = 'daily_practice'
        
        # Create a mock session for automated_practice
        from datetime import datetime
        session['current_session'] = {
            'type': 'practice',
            'day': datetime.now().strftime('%A'),  # Monday, Tuesday, etc.
            'duration': 30,
            'questions_count': len(questions),
            'focus_domains': []
        }
        session['current_week'] = 1
        
        current_app.logger.info(f"✅ Daily session started: user={current_user.id}, diagnostic_id={diagnostic_session.id}, questions={len(questions)}")
        
        # Redirect to automated practice
        return redirect(url_for('learning.automated_practice'))
        
    except Exception as e:
        current_app.logger.error(f"❌ CRITICAL ERROR starting daily session for user {current_user.id}: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        flash(f'Fout bij starten sessie: {str(e)}. Probeer opnieuw.', 'error')
        lang = session.get('lang', 'nl')
        return redirect(url_for('learning_map_bp.learning_map', lang=lang, path_id='irt'))


@individual_plan_api_bp.route('/api/individual-plan/update-progress', methods=['POST'])
@login_required
def api_update_progress():
    """
    Update daily progress after practice session.
    
    Expects JSON: {
        'questions_answered': int,
        'time_spent_minutes': int
    }
    
    Returns:
        JSON: {
            'daily_streak': int,
            'goal_met': bool,
            'learning_velocity': float
        }
    """
    try:
        data = request.get_json()
        
        questions = data.get('questions_answered', 0)
        time_spent = data.get('time_spent_minutes', 0)
        
        result = update_daily_progress(current_user, questions, time_spent)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@individual_plan_api_bp.route('/api/individual-plan/categories')
@login_required
def api_categories():
    """
    Get categories for the user's profession.
    
    Returns:
        JSON: {
            'categories': list of category objects
        }
    """
    try:
        from utils.domain_helpers import get_category_summary
        from utils.helpers import get_user_profession_code
        
        profession = get_user_profession_code(current_user)
        categories = get_category_summary(current_user, profession)
        
        return jsonify({
            'categories': categories
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@individual_plan_api_bp.route('/api/individual-plan/recommendations')
@login_required
def api_recommendations():
    """
    Get learning recommendations for the user.
    
    Returns:
        JSON: {
            'focus_category': dict,
            'study_plan': list,
            'next_review_date': date,
            'recommendations': list
        }
    """
    try:
        from utils.individual_plan_helpers import get_learning_recommendations
        
        recommendations = get_learning_recommendations(current_user)
        return jsonify(recommendations)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@individual_plan_api_bp.route('/api/individual-plan/reset-plan', methods=['POST'])
@login_required
def api_reset_plan():
    """
    Reset the user's learning plan to initial state.
    
    Returns:
        JSON: {
            'success': bool,
            'message': str
        }
    """
    try:
        from utils.individual_plan_helpers import reset_learning_plan
        
        plan = reset_learning_plan(current_user)
        
        return jsonify({
            'success': True,
            'message': 'Learning plan reset successfully',
            'plan_id': plan.id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@individual_plan_api_bp.route('/api/individual-plan/focus-category/<int:category_id>', methods=['POST'])
@login_required
def focus_on_category(category_id):
    """
    Start practice focused on a specific category.
    
    Returns:
        JSON: {
            'success': bool,
            'redirect_url': str (URL to start practice),
            'questions_count': int
        }
    """
    try:
        from models import DomainCategory, BIGDomain, Question
        from utils.individual_plan_helpers import get_or_create_learning_plan
        from utils.helpers import get_user_profession_code
        from sqlalchemy import func
        
        # Get the category
        category = DomainCategory.query.get(category_id)
        if not category:
            return jsonify({'success': False, 'error': 'Category not found'}), 404
        
        # Get or create learning plan
        plan = get_or_create_learning_plan(current_user)
        
        profession = get_user_profession_code(current_user)
        
        # Get domains for this category
        domains = BIGDomain.query.filter_by(category_id=category_id, profession=profession).all()
        domain_ids = [d.id for d in domains]
        
        if not domain_ids:
            return jsonify({'success': False, 'error': 'No domains found for this category'}), 400
        
        # Get questions from these domains (limit to 20)
        questions = Question.query.filter(
            Question.profession == profession,
            Question.big_domain_id.in_(domain_ids)
        ).order_by(func.random()).limit(20).all()
        
        if not questions:
            return jsonify({'success': False, 'error': 'No questions found for this category'}), 400
        
        # ✅ Create a DiagnosticSession for category-focused practice
        from models import DiagnosticSession
        from datetime import datetime, timezone
        
        diagnostic_session = DiagnosticSession.create_session(
            user_id=current_user.id,
            session_type='category_practice',
            ip_address=request.remote_addr
        )
        
        # Store in Flask session
        session['daily_session_questions'] = [q.id for q in questions]
        session['daily_session_diagnostic_id'] = diagnostic_session.id
        session['focus_category_id'] = category_id
        session['daily_session_active'] = True
        session['learning_plan_id'] = plan.id
        session['learning_mode'] = 'category_practice'
        
        # Create mock session for automated_practice
        session['current_session'] = {
            'type': 'practice',
            'day': datetime.now().strftime('%A'),
            'duration': 30,
            'questions_count': len(questions),
            'focus_domains': [d.name for d in domains[:3]],  # Top 3 domains
            'category_name': category.name,
            'category_id': category_id
        }
        session['current_week'] = 1
        
        current_app.logger.info(f"✅ Category practice started: user={current_user.id}, category={category.name}, questions={len(questions)}")
        
        return jsonify({
            'success': True,
            'redirect_url': url_for('learning.automated_practice'),
            'questions_count': len(questions),
            'category_name': category.name
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        current_app.logger.error(f"Error starting category practice: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# Fallback endpoint for VP daily scenario (in case vp_daily_bp is not registered)
@individual_plan_api_bp.route('/api/vp/daily-scenario', methods=['GET'])
@login_required
def fallback_vp_daily_scenario():
    """
    Fallback endpoint for VP daily scenario if vp_daily_bp is not registered
    """
    try:
        from utils.virtual_patient_utils import VirtualPatientSelector
        scenario = VirtualPatientSelector.get_daily_scenario(current_user)
        
        if not scenario:
            return jsonify({
                'success': False,
                'message': 'No virtual patient scenarios available for your specialty'
            }), 200
        
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
        current_app.logger.error(f"Error in fallback VP daily scenario: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
