"""
Helper functions for Individual Plan daily tasks and learning management.

This module provides functions to:
- Get or create learning plans
- Generate daily tasks (new questions + SR reviews)
- Update plans from diagnostic results
- Track progress and statistics
- Select questions for study sessions
"""

from models import (
    PersonalLearningPlan, SpacedRepetitionItem, Question, BIGDomain, DomainCategory,
    DiagnosticSession, TestAttempt, UserTermProgress, DailyFlashcardProgress,
    UserEnglishProgress, VirtualPatientAttempt, EnglishPassage, MedicalTerm,
    VirtualPatientScenario, DailyAssignment
)
from utils.helpers import get_user_profession_code
from utils.domain_helpers import get_categories_for_profession, calculate_category_progress
from utils.mastery_helpers import get_mastery_statistics
from extensions import db
from datetime import date, timedelta, datetime, timezone
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
    
    # Get fixed assignments for today
    today = date.today()
    assignments = {}
    for assignment_type in ['test', 'terms', 'virtual_patient', 'english']:
        assignment = DailyAssignment.query.filter_by(
            user_id=user.id,
            assignment_date=today,
            assignment_type=assignment_type
        ).first()
        
        if assignment:
            item_ids = assignment.get_item_ids()
            assignments[assignment_type] = {
                'exists': True,
                'item_count': len(item_ids),
                'completed': assignment.completed,
                'attempts': assignment.attempts
            }
        else:
            assignments[assignment_type] = {
                'exists': False,
                'item_count': 0,
                'completed': False,
                'attempts': 0
            }
    
    return {
        'new_questions': new_questions_needed,
        'reviews_due': reviews_due,
        'total_tasks': reviews_due + new_questions_needed,
        'estimated_time': estimated_time,
        'sr_items': sr_items_due,
        'weak_categories': weak_categories,
        'goal': daily_goal,
        'time_goal': plan.daily_time_goal or 30,
        'assignments': assignments  # New: fixed assignments info
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


def get_category_progress(user):
    """
    Get progress statistics for all learning categories:
    - Tests (DiagnosticSession, TestAttempt)
    - Terms (UserTermProgress, DailyFlashcardProgress)
    - English Reading (UserEnglishProgress)
    - Virtual Patients (VirtualPatientAttempt)
    
    Returns:
        dict: {
            'tests': {...},
            'terms': {...},
            'english': {...},
            'virtual_patients': {...}
        }
    """
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # 1. TESTS Progress (per-question mastery)
    assigned_question_ids = get_all_assignment_item_ids(user, 'test')
    question_mastery_stats = get_mastery_statistics(
        user.id,
        'question',
        assigned_question_ids if assigned_question_ids else None
    )
    total_questions_assigned = len(assigned_question_ids) if assigned_question_ids else question_mastery_stats['total_items']
    total_questions_assigned = total_questions_assigned or 0
    
    avg_score = db.session.query(
        func.avg(DiagnosticSession.correct_answers / DiagnosticSession.questions_answered * 100)
    ).filter(
        DiagnosticSession.user_id == user.id,
        DiagnosticSession.status == 'completed',
        DiagnosticSession.questions_answered > 0
    ).scalar() or 0
    
    tests_progress_percent = round((question_mastery_stats['mastered_items'] / total_questions_assigned) * 100, 1) if total_questions_assigned else 0
    tests_progress_percent = min(tests_progress_percent, 100.0)
    
    tests_progress = {
        'name': 'Тесты',
        'name_en': 'Tests',
        'icon': 'bi-lightning-charge-fill',
        'color': '#667eea',
        'total_completed': question_mastery_stats['mastered_items'],
        'completed_today': question_mastery_stats['mastered_today'],
        'avg_score': round(avg_score, 1),
        'total_questions': int(total_questions_assigned),
        'progress_percent': tests_progress_percent,
        'accuracy': question_mastery_stats['accuracy']
    }
    
    # 2. TERMS Progress (mastery requires two sessions)
    assigned_term_ids = get_all_assignment_item_ids(user, 'terms')
    term_mastery_stats = get_mastery_statistics(
        user.id,
        'term',
        assigned_term_ids if assigned_term_ids else None
    )
    total_terms_available = len(assigned_term_ids) if assigned_term_ids else MedicalTerm.query.count() or 0
    
    daily_flashcard = DailyFlashcardProgress.query.filter_by(
        user_id=user.id,
        date=now.date()
    ).first()
    terms_today = daily_flashcard.terms_studied if daily_flashcard and daily_flashcard.terms_studied else 0
    
    terms_progress_percent = round((term_mastery_stats['mastered_items'] / total_terms_available) * 100, 1) if total_terms_available else 0
    terms_progress_percent = min(terms_progress_percent, 100.0)
    
    terms_progress = {
        'name': 'Термины',
        'name_en': 'Terms',
        'icon': 'bi-journal-text',
        'color': '#f093fb',
        'total_studied': term_mastery_stats['total_items'],
        'studied_today': terms_today,
        'mastered': term_mastery_stats['mastered_items'],
        'total_available': total_terms_available,
        'progress_percent': terms_progress_percent,
        'accuracy': term_mastery_stats['accuracy']
    }
    
    # 3. ENGLISH READING Progress
    assigned_passage_ids = get_all_assignment_item_ids(user, 'english')
    english_mastery_stats = get_mastery_statistics(
        user.id,
        'english',
        assigned_passage_ids if assigned_passage_ids else None
    )
    total_passages_available = len(assigned_passage_ids) if assigned_passage_ids else EnglishPassage.query.count() or 0
    
    avg_english_score = db.session.query(
        func.avg(UserEnglishProgress.score / UserEnglishProgress.total_questions * 100)
    ).filter(
        UserEnglishProgress.user_id == user.id,
        UserEnglishProgress.total_questions > 0
    ).scalar() or 0
    
    english_progress_percent = round((english_mastery_stats['mastered_items'] / total_passages_available) * 100, 1) if total_passages_available else 0
    english_progress_percent = min(english_progress_percent, 100.0)
    
    english_progress = {
        'name': 'Английский',
        'name_en': 'English Reading',
        'icon': 'bi-book',
        'color': '#4facfe',
        'total_completed': english_mastery_stats['mastered_items'],
        'completed_today': english_mastery_stats['mastered_today'],
        'avg_score': round(avg_english_score, 1),
        'total_available': total_passages_available,
        'progress_percent': english_progress_percent,
        'accuracy': english_mastery_stats['accuracy']
    }
    
    # 4. VIRTUAL PATIENTS Progress
    assigned_vp_ids = get_all_assignment_item_ids(user, 'virtual_patient')
    vp_mastery_stats = get_mastery_statistics(
        user.id,
        'virtual_patient',
        assigned_vp_ids if assigned_vp_ids else None
    )
    total_vp_available = len(assigned_vp_ids) if assigned_vp_ids else VirtualPatientScenario.query.filter_by(is_published=True).count() or 0
    
    avg_vp_score = db.session.query(
        func.avg(VirtualPatientAttempt.score)
    ).filter(
        VirtualPatientAttempt.user_id == user.id,
        VirtualPatientAttempt.completed == True
    ).scalar() or 0
    
    vp_progress_percent = round((vp_mastery_stats['mastered_items'] / total_vp_available) * 100, 1) if total_vp_available else 0
    vp_progress_percent = min(vp_progress_percent, 100.0)
    
    vp_progress = {
        'name': 'Виртуальные пациенты',
        'name_en': 'Virtual Patients',
        'icon': 'bi-heart-pulse-fill',
        'color': '#fa709a',
        'total_completed': vp_mastery_stats['mastered_items'],
        'completed_today': vp_mastery_stats['mastered_today'],
        'avg_score': round(avg_vp_score, 1),
        'total_available': total_vp_available,
        'progress_percent': vp_progress_percent,
        'accuracy': vp_mastery_stats['accuracy']
    }
    
    return {
        'tests': tests_progress,
        'terms': terms_progress,
        'english': english_progress,
        'virtual_patients': vp_progress
    }


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
    from models import DiagnosticSession, DiagnosticResponse
    
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
    # BUT: If plan.overall_progress is 0 but user has diagnostic, set a minimum progress
    if has_diagnostic:
        if plan.overall_progress > 0:
            overall_progress = plan.overall_progress
        else:
            # User has diagnostic but plan shows 0% - this means they should be able to practice
            # Set a small progress to indicate they can start practicing
            overall_progress = 1.0  # 1% to indicate they can practice
    else:
        overall_progress = 0
    
    # Get recent sessions (last 5 completed sessions)
    recent_sessions_query = StudySession.query.join(PersonalLearningPlan).filter(
        PersonalLearningPlan.user_id == user.id,
        StudySession.status == 'completed'
    ).order_by(StudySession.completed_at.desc()).limit(5).all()
    
    # ✅ Also get DiagnosticSession results (category practice, daily practice, etc.)
    diagnostic_sessions_query = DiagnosticSession.query.filter(
        DiagnosticSession.user_id == user.id,
        DiagnosticSession.status == 'completed',
        DiagnosticSession.questions_answered > 0  # Only include sessions with actual questions
    ).order_by(DiagnosticSession.completed_at.desc()).limit(5).all()
    
    recent_sessions = []
    
    # Add StudySession results
    for session in recent_sessions_query:
        recent_sessions.append({
            'id': session.id,
            'date': session.completed_at.strftime('%Y-%m-%d') if session.completed_at else '',
            'questions': session.questions_answered,
            'correct': session.correct_answers,
            'accuracy': round((session.correct_answers / session.questions_answered * 100) if session.questions_answered > 0 else 0, 1),
            'time': session.actual_duration or 0
        })
    
    # Add DiagnosticSession results
    for session in diagnostic_sessions_query:
        recent_sessions.append({
            'id': session.id,
            'date': session.completed_at.strftime('%Y-%m-%d') if session.completed_at else '',
            'questions': session.questions_answered,
            'correct': session.correct_answers,
            'accuracy': round((session.correct_answers / session.questions_answered * 100) if session.questions_answered > 0 else 0, 1),
            'time': int((sum(r.response_time or 0 for r in DiagnosticResponse.query.filter_by(session_id=session.id).all()) / 60)) or 0
        })
    
    # Sort all sessions by date (most recent first) and limit to 5
    recent_sessions = sorted(recent_sessions, key=lambda x: x['date'], reverse=True)[:5]
    
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
    
    # Get category progress (Tests, Terms, English, VP)
    category_progress = get_category_progress(user)
    
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
        'category_progress': category_progress,  # New: detailed progress by learning category
        'sr_stats': {
            'total_items': total_sr_items,
            'mastered_items': mastered_items,
            'streak': plan.sr_streak or 0,
            'total_reviews': plan.total_sr_reviews or 0
        },
        'time_invested': total_time_minutes,  # Return in minutes
        'time_invested_hours': int(total_time_minutes // 60),  # Full hours
        'time_invested_minutes': int(total_time_minutes % 60),  # Remaining minutes
        'time_today_hours': int(time_today // 60),  # Today's full hours
        'time_today_minutes': int(time_today % 60),  # Today's remaining minutes
        'learning_velocity': plan.learning_velocity or 0.0,
        'retention_rate': plan.retention_rate or 0.0,
        'recent_sessions': recent_sessions,
        'activity_last_30_days': activity_last_30_days
    }


def get_or_create_daily_assignment(user, assignment_type, item_ids_func, default_count=10):
    """
    Получить или создать дневное задание для пользователя.
    
    Args:
        user: User object
        assignment_type: 'test', 'terms', 'virtual_patient', 'english'
        item_ids_func: Функция для генерации новых ID элементов (если задания нет)
        default_count: Количество элементов по умолчанию
    
    Returns:
        tuple: (DailyAssignment object, list of item IDs)
    """
    today = date.today()
    
    # Проверяем, есть ли уже задание на сегодня
    assignment = DailyAssignment.query.filter_by(
        user_id=user.id,
        assignment_date=today,
        assignment_type=assignment_type
    ).first()
    
    if assignment:
        # Задание уже есть - возвращаем те же самые ID
        item_ids = assignment.get_item_ids()
        return assignment, item_ids
    
    # Задания нет - создаем новое
    # Генерируем ID элементов через функцию
    item_ids = item_ids_func(default_count) if item_ids_func else []
    
    # Создаем новое задание
    assignment = DailyAssignment(
        user_id=user.id,
        assignment_date=today,
        assignment_type=assignment_type
    )
    assignment.set_item_ids(item_ids)
    
    db.session.add(assignment)
    db.session.commit()
    
    return assignment, item_ids


def select_questions_for_today(user, count=20, use_fixed_assignments=True):
    """
    Select questions for today's study session.
    Mix of: SR reviews + new questions from weak categories.
    
    IMPORTANT: If use_fixed_assignments=True, returns FIXED questions for today
    (same questions every time user starts session on the same day).
    
    Args:
        user: User object
        count: Total questions to select
        use_fixed_assignments: If True, use fixed daily assignments
        
    Returns:
        list: Question objects
    """
    plan = get_or_create_learning_plan(user)
    profession = get_user_profession_code(user)
    
    # Если используем фиксированные задания - проверяем/создаем их
    if use_fixed_assignments:
        def generate_question_ids(target_count):
            """Генерирует ID вопросов для нового задания"""
            selected_ids = []
            
            # Get questions already answered today
            from datetime import datetime, timezone
            today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            
            from models import DiagnosticSession, DiagnosticResponse
            today_responses = DiagnosticResponse.query.join(DiagnosticSession).filter(
                DiagnosticSession.user_id == user.id,
                DiagnosticSession.completed_at >= today_start
            ).all()
            
            answered_today_ids = set([r.question_id for r in today_responses])
            
            # 1. Get SR reviews due (приоритет - вопросы из Spaced Repetition)
            sr_items_due = SpacedRepetitionItem.query.filter(
                SpacedRepetitionItem.user_id == user.id,
                SpacedRepetitionItem.next_review <= date.today()
            ).limit(target_count // 2).all()
            
            # Добавляем ID из SR
            for sr_item in sr_items_due:
                if sr_item.question_id not in answered_today_ids:
                    selected_ids.append(sr_item.question_id)
                    if len(selected_ids) >= target_count:
                        return selected_ids[:target_count]
            
            # 2. Get new questions from weak categories
            remaining = target_count - len(selected_ids)
            
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
                        sr_question_ids = [item.question_id for item in sr_items_due]
                        used_question_ids = list(answered_today_ids) + sr_question_ids + selected_ids
                        
                        new_questions = Question.query.filter(
                            Question.profession == profession,
                            Question.big_domain_id.in_(domain_ids),
                            ~Question.id.in_(used_question_ids) if used_question_ids else True
                        ).order_by(func.random()).limit(remaining).all()
                        
                        selected_ids.extend([q.id for q in new_questions])
            
            # 3. Если все еще нужно больше - добавляем случайные вопросы
            if len(selected_ids) < target_count:
                remaining = target_count - len(selected_ids)
                used_ids = selected_ids.copy()
                used_ids.extend(answered_today_ids)
                
                random_questions = Question.query.filter(
                    Question.profession == profession,
                    ~Question.id.in_(used_ids) if used_ids else True
                ).order_by(func.random()).limit(remaining).all()
                
                selected_ids.extend([q.id for q in random_questions])
            
            return selected_ids[:target_count]
        
        # Получаем или создаем задание
        assignment, question_ids = get_or_create_daily_assignment(
            user, 
            'test', 
            generate_question_ids, 
            default_count=count
        )
        
        # Возвращаем вопросы по ID
        selected_questions = Question.query.filter(Question.id.in_(question_ids)).all()
        return selected_questions
    
    # Старая логика (без фиксации) - для обратной совместимости
    selected_questions = []
    
    # Get questions already answered today
    from datetime import datetime, timezone
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
    ).limit(count // 2).all()
    
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


def select_terms_for_today(user, count=10, use_fixed_assignments=True):
    """
    Select terms for today's study session.
    
    Args:
        user: User object
        count: Total terms to select
        use_fixed_assignments: If True, use fixed daily assignments
        
    Returns:
        list: MedicalTerm objects
    """
    if use_fixed_assignments:
        def generate_term_ids(target_count):
            """Генерирует ID терминов для нового задания"""
            selected_ids = []
            
            # Get terms studied in recent days (last 5 days to avoid repetition)
            today = date.today()
            recent_days_start = datetime.combine(today - timedelta(days=5), datetime.min.time()).replace(tzinfo=timezone.utc)
            
            # Get all terms studied in recent days from DailyAssignment
            recent_assignments = DailyAssignment.query.filter(
                DailyAssignment.user_id == user.id,
                DailyAssignment.assignment_type == 'terms',
                DailyAssignment.assignment_date >= (today - timedelta(days=5)),
                DailyAssignment.assignment_date < today  # Exclude today
            ).all()
            
            # Collect all term IDs from recent assignments
            recently_studied_ids = set()
            for assignment in recent_assignments:
                term_ids = assignment.get_item_ids()
                recently_studied_ids.update(term_ids)
            
            # Also get terms from UserTermProgress that were reviewed recently
            recent_reviews = UserTermProgress.query.filter(
                UserTermProgress.user_id == user.id,
                UserTermProgress.last_reviewed >= recent_days_start
            ).all()
            recently_studied_ids.update([r.term_id for r in recent_reviews if r.term_id])
            
            # 1. Get terms from SR (UserTermProgress with next_review <= today)
            # Prioritize terms based on user's difficulty feedback (quality)
            # Terms with low quality (hard) should be reviewed more often
            sr_terms = UserTermProgress.query.filter(
                UserTermProgress.user_id == user.id,
                UserTermProgress.next_review <= datetime.now(timezone.utc)
            ).order_by(
                # Priority 1: Low last_quality (1=Again, 2=Hard) - user found it difficult
                # Priority 2: Low ease_factor - term is generally difficult for user
                # Priority 3: Low mastery_level - term not mastered yet
                # Priority 4: Older last_reviewed - haven't been studied recently
                UserTermProgress.last_quality.asc().nullsfirst(),  # 1,2,3,4,5 -> prioritize 1,2
                UserTermProgress.ease_factor.asc(),  # Lower ease = harder for user
                UserTermProgress.mastery_level.asc(),  # Lower mastery = needs more practice
                UserTermProgress.last_reviewed.asc().nullsfirst()  # Older reviews first
            ).limit(target_count * 3).all()  # Get more to filter and sort
            
            # Filter out recently studied terms and prioritize by difficulty
            # Sort by priority: low quality > low ease_factor > low mastery > low accuracy > older reviews
            sr_terms_sorted = sorted(
                [sr for sr in sr_terms if sr.term_id not in recently_studied_ids],
                key=lambda x: (
                    x.last_quality if x.last_quality is not None else 5,  # Lower quality = higher priority (1=Again, 2=Hard)
                    x.ease_factor,  # Lower ease = harder for user
                    x.mastery_level,  # Lower mastery = needs more practice
                    -(x.times_correct / x.times_reviewed if x.times_reviewed > 0 else 0),  # Lower accuracy = higher priority
                    x.last_reviewed if x.last_reviewed else datetime.min.replace(tzinfo=timezone.utc)  # Older = higher priority
                )
            )
            
            for sr_term in sr_terms_sorted:
                    selected_ids.append(sr_term.term_id)
                    if len(selected_ids) >= target_count:
                        return selected_ids[:target_count]
            
            # 2. Get new terms (terms without UserTermProgress)
            remaining = target_count - len(selected_ids)
            if remaining > 0:
                used_ids = selected_ids.copy()
                used_ids.extend(recently_studied_ids)
                
                # Get terms that user has never studied
                studied_term_ids = db.session.query(UserTermProgress.term_id).filter(
                    UserTermProgress.user_id == user.id
                ).distinct().all()
                studied_term_ids_set = set([t[0] for t in studied_term_ids])
                used_ids.extend(studied_term_ids_set)
                
                new_terms = MedicalTerm.query.filter(
                    ~MedicalTerm.id.in_(used_ids) if used_ids else True
                ).order_by(
                    # Prioritize by difficulty and frequency
                    MedicalTerm.difficulty.desc(),
                    MedicalTerm.frequency.desc()
                ).limit(remaining).all()
                
                selected_ids.extend([t.id for t in new_terms])
            
            # 3. If still not enough, add random terms (excluding recently studied)
            remaining = target_count - len(selected_ids)
            if remaining > 0:
                used_ids = selected_ids.copy()
                used_ids.extend(recently_studied_ids)
                
                random_terms = MedicalTerm.query.filter(
                    ~MedicalTerm.id.in_(used_ids) if used_ids else True
                ).order_by(func.random()).limit(remaining).all()
                
                selected_ids.extend([t.id for t in random_terms])
            
            return selected_ids[:target_count]
        
        # Получаем или создаем задание
        assignment, term_ids = get_or_create_daily_assignment(
            user,
            'terms',
            generate_term_ids,
            default_count=count
        )
        
        # Возвращаем термины по ID
        selected_terms = MedicalTerm.query.filter(MedicalTerm.id.in_(term_ids)).all()
        return selected_terms
    
    # Старая логика (без фиксации)
    # Get terms from SR
    sr_terms = UserTermProgress.query.filter(
        UserTermProgress.user_id == user.id,
        UserTermProgress.next_review <= datetime.now(timezone.utc)
    ).limit(count).all()
    
    selected_terms = [MedicalTerm.query.get(sr.term_id) for sr in sr_terms if sr.term_id]
    
    # Если нужно больше - добавляем случайные
    if len(selected_terms) < count:
        remaining = count - len(selected_terms)
        used_ids = [t.id for t in selected_terms]
        random_terms = MedicalTerm.query.filter(
            ~MedicalTerm.id.in_(used_ids) if used_ids else True
        ).order_by(func.random()).limit(remaining).all()
        selected_terms.extend(random_terms)
    
    return selected_terms[:count]


def select_vp_for_today(user, use_fixed_assignments=True):
    """
    Select virtual patient scenario for today.
    
    Args:
        user: User object
        use_fixed_assignments: If True, use fixed daily assignments
        
    Returns:
        VirtualPatientScenario object or None
    """
    if use_fixed_assignments:
        def generate_vp_id():
            """Генерирует ID ВП для нового задания"""
            # Get VP completed today
            today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            completed_today = VirtualPatientAttempt.query.filter(
                VirtualPatientAttempt.user_id == user.id,
                VirtualPatientAttempt.started_at >= today_start,
                VirtualPatientAttempt.completed == True
            ).all()
            
            completed_vp_ids = set([v.scenario_id for v in completed_today if v.scenario_id])
            
            # Get random VP that user hasn't completed today
            random_vp = VirtualPatientScenario.query.filter(
                VirtualPatientScenario.is_published == True,
                ~VirtualPatientScenario.id.in_(completed_vp_ids) if completed_vp_ids else True
            ).order_by(func.random()).first()
            
            return [random_vp.id] if random_vp else []
        
        # Получаем или создаем задание
        assignment, vp_ids = get_or_create_daily_assignment(
            user,
            'virtual_patient',
            generate_vp_id,
            default_count=1
        )
        
        if vp_ids:
            return VirtualPatientScenario.query.get(vp_ids[0])
        return None
    
    # Старая логика (без фиксации)
    # Get random published VP
    random_vp = VirtualPatientScenario.query.filter_by(
        is_published=True
    ).order_by(func.random()).first()
    
    return random_vp


def get_daily_assignment_items(user, assignment_type):
    """
    Получить элементы дневного задания для пользователя.
    
    Args:
        user: User object
        assignment_type: 'test', 'terms', 'virtual_patient', 'english'
    
    Returns:
        list: ID элементов или None если задания нет
    """
    today = date.today()
    
    assignment = DailyAssignment.query.filter_by(
        user_id=user.id,
        assignment_date=today,
        assignment_type=assignment_type
    ).first()
    
    if assignment:
        return assignment.get_item_ids()
    
    return None


def get_all_assignment_item_ids(user, assignment_type):
    """
    Получить уникальные ID элементов всех дневных заданий пользователя указанного типа.
    """
    assignments = DailyAssignment.query.filter_by(
        user_id=user.id,
        assignment_type=assignment_type
    ).all()
    
    unique_ids = set()
    for assignment in assignments:
        try:
            item_ids = assignment.get_item_ids()
            if item_ids:
                unique_ids.update(item_ids)
        except Exception:
            continue
    return unique_ids


def select_english_passage_for_today(user, use_fixed_assignments=True):
    """
    Select English reading passage for today.
    
    Args:
        user: User object
        use_fixed_assignments: If True, use fixed daily assignments
        
    Returns:
        EnglishPassage object or None
    """
    if use_fixed_assignments:
        def generate_passage_id(target_count=1):
            """Генерирует ID текста для нового задания"""
            # Get passages completed today
            today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
            completed_today = UserEnglishProgress.query.filter(
                UserEnglishProgress.user_id == user.id,
                UserEnglishProgress.completed_at >= today_start
            ).all()
            
            completed_passage_ids = set([p.passage_id for p in completed_today if p.passage_id])
            
            # Get random passage that user hasn't completed today
            random_passage = EnglishPassage.query.filter(
                ~EnglishPassage.id.in_(completed_passage_ids) if completed_passage_ids else True
            ).order_by(func.random()).first()
            
            return [random_passage.id] if random_passage else []
        
        # Получаем или создаем задание
        assignment, passage_ids = get_or_create_daily_assignment(
            user,
            'english',
            generate_passage_id,
            default_count=1
        )
        
        if passage_ids:
            return EnglishPassage.query.get(passage_ids[0])
        return None
    
    # Старая логика (без фиксации)
    # Get random passage
    random_passage = EnglishPassage.query.order_by(func.random()).first()
    return random_passage


def add_to_spaced_repetition(user_id, question_id, was_correct):
    """
    Добавить вопрос в Spaced Repetition при неправильном ответе.
    
    Args:
        user_id: ID пользователя
        question_id: ID вопроса
        was_correct: bool - правильный ли ответ
    """
    from utils.simple_spaced_repetition import SimpleSpacedRepetition
    
    try:
        sr_system = SimpleSpacedRepetition()
        # Конвертируем boolean в quality (0-5)
        # Если неправильно - добавляем с низким качеством для повторения
        # Если правильно - тоже добавляем, но с высоким качеством
        quality = 5 if was_correct else 2  # 2 = нужно повторить, но не критично
        
        # Если ответ неправильный - добавляем с качеством 0 для обязательного повторения
        if not was_correct:
            quality = 0
        
        sr_system.calculate_next_review(
            user_id=user_id,
            question_id=question_id,
            quality=quality
        )
        
        db.session.commit()
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error adding to spaced repetition: {e}")
        db.session.rollback()


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


def check_all_tasks_completed_today(user):
    """
    Проверяет, выполнены ли все задачи на сегодня.
    
    Args:
        user: User object
    
    Returns:
        bool: True если все задачи выполнены
    """
    from routes.learning import get_daily_tasks
    
    today = datetime.now(timezone.utc).date()
    today_start = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
    today_end = today_start + timedelta(days=1)
    
    # Получаем задачи на сегодня
    tasks_data = get_daily_tasks(user.id, study_day=None)
    tasks = tasks_data.get('tasks', [])
    
    if not tasks:
        return False
    
    # Проверяем каждую задачу
    for task in tasks:
        task_type = task.get('type')
        target = task.get('target', 0)
        
        if task_type == 'test' or task_type == 'diagnostic_test' or task_type == 'big_test':
            # Проверяем тесты
            from models import DiagnosticSession
            tests_today = DiagnosticSession.query.filter(
                DiagnosticSession.user_id == user.id,
                DiagnosticSession.started_at >= today_start,
                DiagnosticSession.started_at < today_end
            ).all()
            tests_completed = len([t for t in tests_today if (
                getattr(t, 'status', None) == 'completed' or 
                getattr(t, 'completed_at', None) is not None
            )])
            if tests_completed < target:
                return False
        
        elif task_type == 'terms' or task_type == 'flashcards':
            # Проверяем термины
            flashcard_today = DailyFlashcardProgress.query.filter_by(
                user_id=user.id,
                date=today
            ).first()
            terms_completed = flashcard_today.terms_studied if flashcard_today else 0
            if terms_completed < target:
                return False
        
        elif task_type == 'virtual_patient':
            # Проверяем ВП
            vp_today = VirtualPatientAttempt.query.filter(
                VirtualPatientAttempt.user_id == user.id,
                VirtualPatientAttempt.started_at >= today_start,
                VirtualPatientAttempt.started_at < today_end
            ).all()
            vp_completed = len([v for v in vp_today if getattr(v, 'completed', False)])
            if vp_completed < target:
                return False
        
        elif task_type == 'english' or task_type == 'english_reading':
            # Проверяем английский
            english_today = UserEnglishProgress.query.filter(
                UserEnglishProgress.user_id == user.id,
                UserEnglishProgress.completed_at >= today_start,
                UserEnglishProgress.completed_at < today_end
            ).all()
            english_completed = len(english_today)
            if english_completed < target:
                return False
        
        elif task_type == 'memory_game':
            # Игра "память" отслеживается на клиенте, считаем выполненной если другие задачи выполнены
            pass
    
    return True


def get_study_day(user):
    """
    Получить текущий день учебы пользователя.
    
    Args:
        user: User object
    
    Returns:
        int: День учебы (начиная с 1)
    """
    plan = get_or_create_learning_plan(user)
    
    # Получаем study_day_count из daily_goal_met_count (временное решение)
    # или из domain_analysis
    study_day = getattr(plan, 'daily_goal_met_count', None)
    
    if study_day is None or study_day == 0:
        # Пытаемся получить из domain_analysis
        study_data = plan.get_domain_analysis()
        if study_data and isinstance(study_data, dict):
            study_day = study_data.get('_study_day_data', {}).get('study_day_count', 0)
    
    # Если все еще 0 или None, возвращаем 1 (первый день)
    if not study_day or study_day == 0:
        return 1
    
    return study_day


def get_cycle_info(study_day):
    """
    Определяет информацию о текущем цикле обучения.
    
    Args:
        study_day: День учебы (начиная с 1)
    
    Returns:
        dict: {
            'cycle': int,  # Номер цикла (1, 2, 3...)
            'day_in_cycle': int,  # День в цикле (1-28)
            'config': dict  # Конфигурация цикла
        }
    """
    if study_day <= 0:
        study_day = 1
    
    # Каждый цикл = 28 дней
    cycle = ((study_day - 1) // 28) + 1
    day_in_cycle = ((study_day - 1) % 28) + 1
    
    # Определяем конфигурацию цикла
    if cycle == 1:
        multiplier = 1.0
        focus = 'foundation'
        name_key = 'cycle_basic'
        description_key = 'cycle_basic_description'
    elif cycle == 2:
        multiplier = 1.2
        focus = 'adaptation'
        name_key = 'cycle_adaptive'
        description_key = 'cycle_adaptive_description'
    elif cycle == 3:
        multiplier = 1.5
        focus = 'advanced'
        name_key = 'cycle_advanced'
        description_key = 'cycle_advanced_description'
    else:  # cycle >= 4
        multiplier = 1.5 + (cycle - 3) * 0.1  # Увеличиваем сложность
        focus = 'expert'
        name_key = 'cycle_expert'
        description_key = 'cycle_expert_description'
    
    return {
        'cycle': cycle,
        'day_in_cycle': day_in_cycle,
        'config': {
            'multiplier': multiplier,
            'focus': focus,
            'name_key': name_key,
            'description_key': description_key
        }
    }


def update_study_day_count(user):
    """
    Обновляет счетчик дней учебы на основе выполнения задач.
    
    Args:
        user: User object
    
    Returns:
        dict: {
            'study_day': int,
            'cycle_info': dict,
            'first_successful_day': date or None
        }
    """
    plan = get_or_create_learning_plan(user)
    
    # Получаем текущий день учебы
    current_study_day = get_study_day(user)
    
    # Проверяем, выполнены ли все задачи сегодня
    all_completed = check_all_tasks_completed_today(user)
    
    # Получаем информацию о первом успешном дне
    study_data = plan.get_domain_analysis()
    if study_data and isinstance(study_data, dict):
        study_day_data = study_data.get('_study_day_data', {})
        first_successful_day_str = study_day_data.get('first_successful_day')
        if first_successful_day_str:
            try:
                from datetime import datetime as dt
                first_successful_day = dt.fromisoformat(first_successful_day_str).date()
            except:
                first_successful_day = None
        else:
            first_successful_day = None
    else:
        first_successful_day = None
    
    # Если все задачи выполнены сегодня и это новый успешный день
    if all_completed:
        today = date.today()
        
        # Проверяем, не был ли сегодняшний день уже засчитан
        # (чтобы не увеличивать счетчик несколько раз за день)
        last_successful_date_str = None
        if study_data and isinstance(study_data, dict):
            study_day_data = study_data.get('_study_day_data', {})
            last_successful_date_str = study_day_data.get('last_successful_date')
        
        if not last_successful_date_str or last_successful_date_str != today.isoformat():
            # Увеличиваем счетчик дней учебы
            new_study_day = current_study_day + 1
            
            # Сохраняем в daily_goal_met_count (временное решение)
            plan.daily_goal_met_count = new_study_day
            
            # Сохраняем в domain_analysis
            if not study_data:
                study_data = {}
            if '_study_day_data' not in study_data:
                study_data['_study_day_data'] = {}
            
            study_data['_study_day_data']['study_day_count'] = new_study_day
            study_data['_study_day_data']['last_successful_date'] = today.isoformat()
            
            if not first_successful_day:
                first_successful_day = today
                study_data['_study_day_data']['first_successful_day'] = today.isoformat()
            
            plan.set_domain_analysis(study_data)
            db.session.commit()
            
            current_study_day = new_study_day
    
    # Получаем информацию о цикле
    cycle_info = get_cycle_info(current_study_day)
    
    return {
        'study_day': current_study_day,
        'cycle_info': cycle_info,
        'first_successful_day': first_successful_day
    }
