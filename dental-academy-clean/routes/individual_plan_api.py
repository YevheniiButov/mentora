"""
API endpoints for Individual Plan functionality.

This module provides REST API endpoints for:
- Daily tasks management
- Progress tracking
- Daily session handling
- Progress updates
"""

from flask import Blueprint, jsonify, redirect, url_for, request, session, current_app
from flask_login import login_required, current_user
from utils.individual_plan_helpers import (
    get_daily_tasks,
    get_progress_summary,
    update_daily_progress,
    select_questions_for_today
)

individual_plan_api_bp = Blueprint('individual_plan_api', __name__)


@individual_plan_api_bp.route('/api/individual-plan/daily-tasks')
@login_required
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
    try:
        from utils.individual_plan_helpers import get_or_create_learning_plan
        
        # Get or create learning plan
        plan = get_or_create_learning_plan(current_user)
        
        if not plan:
            flash('Kon geen leerplan vinden. Start eerst een diagnostische test.', 'warning')
            return redirect(url_for('dashboard.index'))
        
        # Select today's questions
        questions = select_questions_for_today(current_user, count=20)
        
        if not questions:
            flash('Geen vragen beschikbaar. Probeer later opnieuw.', 'warning')
            return redirect(url_for('dashboard.index'))
        
        # Store question IDs and plan info in session for practice
        session['daily_session_questions'] = [q.id for q in questions]
        session['daily_session_active'] = True
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
        
        # Redirect to automated practice
        return redirect(url_for('learning.automated_practice'))
        
    except Exception as e:
        print(f"Error starting daily session: {e}")
        import traceback
        traceback.print_exc()
        flash('Fout bij starten sessie. Probeer opnieuw.', 'error')
        return redirect(url_for('dashboard.index'))


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
