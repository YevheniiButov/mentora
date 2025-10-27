"""
Helper functions for Individual Plan daily tasks and learning management.

This module provides functions to:
- Get or create learning plans
- Generate daily tasks (new questions + SR reviews)
- Update plans from diagnostic results
- Track progress and statistics
- Select questions for study sessions
"""

from models import PersonalLearningPlan, SpacedRepetitionItem, Question, BIGDomain, DomainCategory
from utils.helpers import get_user_profession_code
from utils.domain_helpers import get_categories_for_profession, calculate_category_progress
from extensions import db
from datetime import date, timedelta
from sqlalchemy import func
import json


def get_or_create_learning_plan(user):
    """
    Get existing active learning plan or create new one.
    
    Args:
        user: User object
        
    Returns:
        PersonalLearningPlan object
    """
    # Try to get active plan
    plan = PersonalLearningPlan.query.filter_by(
        user_id=user.id,
        status='active'
    ).first()
    
    if not plan:
        # Create new plan
        plan = PersonalLearningPlan(
            user_id=user.id,
            start_date=date.today(),
            intensity='moderate',
            daily_question_goal=20,
            daily_time_goal=30,
            spaced_repetition_enabled=True,
            status='active'
        )
        db.session.add(plan)
        db.session.commit()
    
    return plan


def get_daily_tasks(user):
    """
    Get today's tasks: new questions + SR reviews.
    
    Returns:
        dict: {
            'new_questions': int,
            'reviews_due': int,
            'total_tasks': int,
            'estimated_time': int,
            'sr_items': list,
            'weak_categories': list,
            'goal': int
        }
    """
    plan = get_or_create_learning_plan(user)
    profession = get_user_profession_code(user)
    
    # Get SR reviews due today
    sr_items_due = SpacedRepetitionItem.query.filter(
        SpacedRepetitionItem.user_id == user.id,
        SpacedRepetitionItem.next_review <= date.today()
    ).all()
    
    reviews_due = len(sr_items_due)
    
    # Calculate new questions needed to reach daily goal
    daily_goal = plan.daily_question_goal or 20  # Default to 20 if None
    new_questions_needed = max(0, daily_goal - reviews_due)
    
    # Get weak categories for focus
    weak_categories = plan.get_weak_categories()
    
    # Estimate time (assuming 1.5 min per question)
    estimated_time = int((reviews_due + new_questions_needed) * 1.5)
    
    return {
        'new_questions': new_questions_needed,
        'reviews_due': reviews_due,
        'total_tasks': reviews_due + new_questions_needed,
        'estimated_time': estimated_time,
        'sr_items': sr_items_due,
        'weak_categories': weak_categories,
        'goal': daily_goal,
        'time_goal': plan.daily_time_goal or 30
    }


def update_plan_from_diagnostic(user, diagnostic_results):
    """
    Update learning plan based on diagnostic test results.
    
    Args:
        user: User object
        diagnostic_results: DiagnosticSession object or dict with domain scores
        
    Returns:
        PersonalLearningPlan: Updated plan
    """
    from utils.domain_helpers import get_user_weak_categories, get_user_strong_categories, get_category_summary
    from models import DiagnosticSession
    
    plan = get_or_create_learning_plan(user)
    profession = get_user_profession_code(user)
    
    # If diagnostic_results is a DiagnosticSession object, extract data
    if isinstance(diagnostic_results, DiagnosticSession):
        diagnostic_session = diagnostic_results
        
        # Calculate overall progress from diagnostic accuracy
        if diagnostic_session.questions_answered > 0:
            accuracy = (diagnostic_session.correct_answers / diagnostic_session.questions_answered) * 100
            plan.overall_progress = round(accuracy, 1)
        
        # Initialize other fields if they are None
        if plan.time_invested is None:
            plan.time_invested = 0
        if plan.retention_rate is None:
            plan.retention_rate = 0.0
        if plan.daily_streak is None:
            plan.daily_streak = 0
        if plan.longest_daily_streak is None:
            plan.longest_daily_streak = 0
        if plan.daily_question_goal is None:
            plan.daily_question_goal = 20
        if plan.daily_time_goal is None:
            plan.daily_time_goal = 30
    
    # Get weak and strong categories
    weak_cats = get_user_weak_categories(user, profession, threshold=60)
    strong_cats = get_user_strong_categories(user, profession, threshold=80)
    
    # Update plan with category info
    weak_cat_ids = [cat['id'] for cat in weak_cats]
    strong_cat_ids = [cat['id'] for cat in strong_cats]
    
    plan.set_weak_categories(weak_cat_ids)
    plan.set_strong_categories(strong_cat_ids)
    
    # Set focus on weakest category
    if weak_cat_ids:
        plan.current_category_focus = weak_cat_ids[0]
    
    # Update category abilities from diagnostic
    category_abilities = {}
    for cat in weak_cats + strong_cats:
        category_abilities[cat['id']] = cat['percentage'] / 100.0
    plan.set_category_abilities(category_abilities)
    
    # Calculate category progress
    all_categories = get_category_summary(user, profession)
    if all_categories:
        total_progress = sum(cat['percentage'] for cat in all_categories)
        avg_progress = total_progress / len(all_categories)
        plan.set_category_progress({
            cat['id']: cat['percentage'] for cat in all_categories
        })
        # Update overall progress if not set from diagnostic
        if plan.overall_progress == 0.0 and avg_progress > 0:
            plan.overall_progress = round(avg_progress, 1)
    
    # Set next review date (in 1 week if SR enabled)
    if plan.spaced_repetition_enabled:
        plan.next_review_date = date.today() + timedelta(days=7)
    
    db.session.commit()
    
    print(f"✅ Plan updated: overall_progress={plan.overall_progress}%, time_invested={plan.time_invested}, retention_rate={plan.retention_rate}")
    
    return plan


def get_progress_summary(user):
    """
    Get comprehensive progress summary for Individual Plan.
    
    Returns:
        dict: {
            'overall_progress': float,
            'daily_streak': int,
            'questions_today': int,
            'time_today': int,
            'categories': list,
            'weak_areas': list,
            'sr_stats': dict
        }
    """
    from utils.domain_helpers import get_category_summary
    
    plan = get_or_create_learning_plan(user)
    profession = get_user_profession_code(user)
    
    # Get category summary
    categories = get_category_summary(user, profession)
    
    # Calculate today's activity from StudySession
    from datetime import datetime, timezone
    from models import StudySession, PersonalLearningPlan
    
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Get completed sessions for today from StudySession
    sessions_today = StudySession.query.join(PersonalLearningPlan).filter(
        PersonalLearningPlan.user_id == user.id,
        StudySession.status == 'completed',
        StudySession.completed_at >= today_start
    ).all()
    
    # Sum up questions and time from today's StudySession
    questions_today = sum(session.questions_answered for session in sessions_today)
    time_today = sum(session.actual_duration or 0 for session in sessions_today)
    
    # ALSO count questions from DiagnosticSession (IRT practice sessions)
    from models import DiagnosticSession, DiagnosticResponse
    diagnostic_sessions_today = DiagnosticSession.query.filter(
        DiagnosticSession.user_id == user.id,
        DiagnosticSession.status == 'completed',
        DiagnosticSession.completed_at >= today_start
    ).all()
    
    # Add diagnostic session questions
    diagnostic_questions_today = sum(session.questions_answered for session in diagnostic_sessions_today)
    questions_today += diagnostic_questions_today
    
    # Calculate time from DiagnosticSession responses
    diagnostic_time_today = 0
    for session in diagnostic_sessions_today:
        # Get all responses for this session
        responses = DiagnosticResponse.query.filter_by(session_id=session.id).all()
        # Sum up response_time (in seconds), convert to minutes
        session_time = sum(response.response_time or 0 for response in responses) / 60
        diagnostic_time_today += session_time
    
    time_today += diagnostic_time_today
    
    # DEBUG: Log the counts
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"DEBUG questions_today: StudySession={questions_today - diagnostic_questions_today}, DiagnosticSession={diagnostic_questions_today}, Total={questions_today}")
    logger.info(f"DEBUG time_today: StudySession={time_today - diagnostic_time_today}, DiagnosticSession={diagnostic_time_today}, Total={time_today}")
    
    # SR statistics
    total_sr_items = SpacedRepetitionItem.query.filter_by(user_id=user.id).count()
    mastered_items = SpacedRepetitionItem.query.filter(
        SpacedRepetitionItem.user_id == user.id,
        SpacedRepetitionItem.ease_factor >= 2.5,
        SpacedRepetitionItem.repetitions >= 3
    ).count()
    
    # Check if user has completed diagnostic
    from models import DiagnosticSession
    has_diagnostic = DiagnosticSession.query.filter_by(
        user_id=user.id,
        status='completed'
    ).first() is not None
    
    # If user has diagnostic, use plan progress, otherwise show 0
    overall_progress = plan.overall_progress if has_diagnostic else 0
    
    # Get recent sessions (last 5 completed sessions)
    recent_sessions_query = StudySession.query.join(PersonalLearningPlan).filter(
        PersonalLearningPlan.user_id == user.id,
        StudySession.status == 'completed'
    ).order_by(StudySession.completed_at.desc()).limit(5).all()
    
    recent_sessions = []
    for session in recent_sessions_query:
        recent_sessions.append({
            'id': session.id,
            'date': session.completed_at.strftime('%Y-%m-%d') if session.completed_at else '',
            'questions': session.questions_answered,
            'correct': session.correct_answers,
            'accuracy': round((session.correct_answers / session.questions_answered * 100) if session.questions_answered > 0 else 0, 1),
            'time': session.actual_duration or 0
        })
    
    # Get last 30 days activity data
    from datetime import timedelta
    activity_last_30_days = []
    for i in range(29, -1, -1):
        date = datetime.now(timezone.utc).date() - timedelta(days=i)
        date_start = datetime.combine(date, datetime.min.time()).replace(tzinfo=timezone.utc)
        date_end = date_start + timedelta(days=1)
        
        # Count questions answered on this date from StudySession
        day_sessions = StudySession.query.join(PersonalLearningPlan).filter(
            PersonalLearningPlan.user_id == user.id,
            StudySession.status == 'completed',
            StudySession.completed_at >= date_start,
            StudySession.completed_at < date_end
        ).all()
        
        questions_count = sum(session.questions_answered for session in day_sessions)
        
        # Also count questions from DiagnosticSession
        diagnostic_day_sessions = DiagnosticSession.query.filter(
            DiagnosticSession.user_id == user.id,
            DiagnosticSession.status == 'completed',
            DiagnosticSession.completed_at >= date_start,
            DiagnosticSession.completed_at < date_end
        ).all()
        
        diagnostic_questions = sum(session.questions_answered for session in diagnostic_day_sessions)
        questions_count += diagnostic_questions
        
        activity_last_30_days.append({
            'date': date.isoformat(),
            'questions': questions_count
        })
    
    # Calculate streak from activity_last_30_days
    streak = 0
    if activity_last_30_days:
        # Skip today (last element) and count consecutive days with questions, starting from yesterday
        # This allows streak to continue even if user hasn't answered questions yet today
        for i in range(len(activity_last_30_days) - 2, -1, -1):  # Start from second-to-last element
            if activity_last_30_days[i]['questions'] > 0:
                streak += 1
            else:
                break
    
    # DEBUG: Log streak calculation
    import logging
    logger = logging.getLogger(__name__)
    logger.info(f"🔍 STREAK DEBUG: streak={streak}, activity_last_30_days[-4:0]={activity_last_30_days[-4:] if len(activity_last_30_days) >= 4 else 'N/A'}")
    
    # Calculate total questions answered (sum of all days in activity_last_30_days)
    total_questions_answered = sum(day['questions'] for day in activity_last_30_days)
    
    # Calculate total time for last 30 days (use plan.time_invested or sum from sessions)
    # We'll use plan.time_invested if available, otherwise calculate from sessions
    total_time_minutes = plan.time_invested or 0
    if total_time_minutes == 0:
        # Fallback: sum up time from all completed sessions in last 30 days
        for session in StudySession.query.join(PersonalLearningPlan).filter(
            PersonalLearningPlan.user_id == user.id,
            StudySession.status == 'completed',
            StudySession.completed_at >= (datetime.now(timezone.utc) - timedelta(days=30))
        ).all():
            if session.actual_duration:
                total_time_minutes += session.actual_duration
    
    return {
        'overall_progress': overall_progress,
        'daily_streak': streak if streak > 0 else (plan.daily_streak or 0),
        'longest_streak': plan.longest_daily_streak or 0,
        'questions_today': questions_today,
        'questions_total': total_questions_answered,  # Total questions in last 30 days
        'time_today': time_today,
        'daily_goal': plan.daily_question_goal,
        'time_goal': plan.daily_time_goal,
        'categories': categories,
        'weak_categories': [c for c in categories if c['percentage'] < 60],
        'sr_stats': {
            'total_items': total_sr_items,
            'mastered_items': mastered_items,
            'streak': plan.sr_streak or 0,
            'total_reviews': plan.total_sr_reviews or 0
        },
        'time_invested': total_time_minutes,  # Return in minutes
        'time_invested_hours': round(total_time_minutes / 60, 1),  # Return in hours
        'learning_velocity': plan.learning_velocity or 0.0,
        'retention_rate': plan.retention_rate or 0.0,
        'recent_sessions': recent_sessions,
        'activity_last_30_days': activity_last_30_days
    }


def select_questions_for_today(user, count=20):
    """
    Select questions for today's study session.
    Mix of: SR reviews + new questions from weak categories.
    
    IMPORTANT: Excludes questions already answered today.
    
    Args:
        user: User object
        count: Total questions to select
        
    Returns:
        list: Question objects
    """
    plan = get_or_create_learning_plan(user)
    profession = get_user_profession_code(user)
    
    selected_questions = []
    
    # Get questions already answered today
    from datetime import datetime, timezone, date
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    
    from models import DiagnosticSession, DiagnosticResponse
    today_responses = DiagnosticResponse.query.join(DiagnosticSession).filter(
        DiagnosticSession.user_id == user.id,
        DiagnosticSession.completed_at >= today_start
    ).all()
    
    answered_today_ids = set([r.question_id for r in today_responses])
    
    # 1. Get SR reviews due
    sr_items_due = SpacedRepetitionItem.query.filter(
        SpacedRepetitionItem.user_id == user.id,
        SpacedRepetitionItem.next_review <= date.today()
    ).limit(count // 2).all()  # Max 50% of daily questions from SR
    
    # Get questions for these SR items (exclude already answered)
    for sr_item in sr_items_due:
        if sr_item.question_id not in answered_today_ids:
            question = Question.query.get(sr_item.question_id)
            if question:
                selected_questions.append(question)
    
    # 2. Get new questions from weak categories
    remaining = count - len(selected_questions)
    
    if remaining > 0:
        weak_cat_ids = plan.get_weak_categories()
        
        if weak_cat_ids:
            # Get domains from weak categories
            weak_domains = BIGDomain.query.filter(
                BIGDomain.category_id.in_(weak_cat_ids),
                BIGDomain.profession == profession
            ).all()
            
            domain_ids = [d.id for d in weak_domains]
            
            if domain_ids:
                # Get questions from these domains
                # Exclude questions already in SR AND already answered today
                sr_question_ids = [item.question_id for item in sr_items_due]
                used_question_ids = list(answered_today_ids) + sr_question_ids + [q.id for q in selected_questions]
                
                new_questions = Question.query.filter(
                    Question.profession == profession,
                    Question.big_domain_id.in_(domain_ids),
                    ~Question.id.in_(used_question_ids) if used_question_ids else True
                ).order_by(func.random()).limit(remaining).all()
                
                selected_questions.extend(new_questions)
        
        # 3. If still need more, get random questions
        if len(selected_questions) < count:
            remaining = count - len(selected_questions)
            used_ids = [q.id for q in selected_questions]
            used_ids.extend(answered_today_ids)
            
            random_questions = Question.query.filter(
                Question.profession == profession,
                ~Question.id.in_(used_ids) if used_ids else True
            ).order_by(func.random()).limit(remaining).all()
            
            selected_questions.extend(random_questions)
    
    return selected_questions


def update_daily_progress(user, questions_answered, time_spent_minutes):
    """
    Update daily progress and streaks.
    
    Args:
        user: User object
        questions_answered: int
        time_spent_minutes: int
        
    Returns:
        dict: Updated progress info
    """
    plan = get_or_create_learning_plan(user)
    
    # Update daily streak
    plan.update_daily_streak()
    
    # Check if daily goal was met
    goal_met = plan.check_daily_goal_met(questions_answered, time_spent_minutes)
    
    # Update learning velocity
    plan.update_learning_velocity(questions_answered, time_spent_minutes)
    
    # Add time invested
    plan.add_time_invested(time_spent_minutes)
    
    # Update last activity
    plan.last_activity_date = date.today()
    
    db.session.commit()
    
    return {
        'daily_streak': plan.daily_streak,
        'goal_met': goal_met,
        'learning_velocity': plan.learning_velocity,
        'time_invested': plan.time_invested,
        'goal_met_count': plan.daily_goal_met_count
    }


def get_learning_recommendations(user):
    """
    Get personalized learning recommendations.
    
    Returns:
        dict: {
            'focus_category': dict,
            'study_plan': list,
            'next_review_date': date,
            'recommendations': list
        }
    """
    plan = get_or_create_learning_plan(user)
    profession = get_user_profession_code(user)
    
    # Get current focus category
    focus_category = None
    if plan.current_category_focus:
        focus_category = DomainCategory.query.get(plan.current_category_focus)
    
    # Get weak categories for recommendations
    weak_cats = plan.get_weak_categories()
    weak_categories = DomainCategory.query.filter(
        DomainCategory.id.in_(weak_cats)
    ).all() if weak_cats else []
    
    # Generate study plan recommendations
    recommendations = []
    
    if plan.daily_streak < 3:
        recommendations.append("Try to maintain a daily study streak for better retention")
    
    if plan.learning_velocity and plan.learning_velocity < 20:
        recommendations.append("Consider taking breaks between questions to improve focus")
    
    if plan.retention_rate and plan.retention_rate < 70:
        recommendations.append("Focus more on spaced repetition reviews")
    
    if not plan.spaced_repetition_enabled:
        recommendations.append("Enable spaced repetition for better long-term retention")
    
    return {
        'focus_category': focus_category.to_dict() if focus_category else None,
        'study_plan': [cat.to_dict() for cat in weak_categories[:3]],  # Top 3 weak categories
        'next_review_date': plan.next_review_date,
        'recommendations': recommendations,
        'daily_goal': plan.daily_question_goal,
        'time_goal': plan.daily_time_goal
    }


def reset_learning_plan(user):
    """
    Reset learning plan to initial state.
    
    Args:
        user: User object
        
    Returns:
        PersonalLearningPlan: Reset plan
    """
    # Get or create plan
    plan = get_or_create_learning_plan(user)
    
    # Reset all progress fields
    plan.overall_progress = 0.0
    plan.current_ability = 0.0
    plan.daily_streak = 0
    plan.sr_streak = 0
    plan.total_sr_reviews = 0
    plan.daily_goal_met_count = 0
    plan.time_invested = 0
    plan.learning_velocity = None
    plan.retention_rate = None
    
    # Reset JSON fields
    plan.set_category_progress({})
    plan.set_weak_categories([])
    plan.set_strong_categories([])
    plan.set_category_abilities({})
    
    # Reset dates
    plan.last_activity_date = None
    plan.next_review_date = None
    
    # Reset focus
    plan.current_category_focus = None
    
    db.session.commit()
    
    return plan
