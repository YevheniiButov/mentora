# routes/learning_routes.py - Learning system routes

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, g
from flask_login import login_required, current_user
from utils.serializers import safe_jsonify
from models import LearningPath, Subject, Module, Lesson, UserProgress
from extensions import db
from datetime import datetime, timezone
from functools import wraps
from flask import session
from models import PersonalLearningPlan, Question, BIGDomain, DiagnosticSession, DiagnosticResponse, StudySession
def _rebuild_study_schedule_from_sessions(plan):
    """
    Build a minimal study schedule structure from existing StudySession records.
    Returns schedule dict or None if rebuild not possible.
    """
    try:
        sessions = plan.study_sessions.order_by(StudySession.id).all()
        if not sessions:
            current_app.logger.warning(f"Schedule rebuild: plan {plan.id} has no study sessions")
            return None

        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekly_schedule = []
        current_week_sessions = []
        week_number = 1

        for idx, study_session in enumerate(sessions):
            day_index = idx % 7
            if day_index == 0 and current_week_sessions:
                # finalize previous week
                estimated_hours = sum(
                    (session_entry.get('duration', 0) or 0) / 60.0
                    for session_entry in current_week_sessions
                )
                weekly_schedule.append({
                    'week_number': week_number,
                    'focus_domains': [],
                    'daily_sessions': current_week_sessions,
                    'milestone_test': False,
                    'estimated_hours': round(estimated_hours, 2)
                })
                week_number += 1
                current_week_sessions = []

            focus_domains = []
            if study_session.domain_id:
                domain = BIGDomain.query.get(study_session.domain_id)
                if domain and domain.code:
                    focus_domains.append(domain.code)

            duration_minutes = study_session.planned_duration or plan.daily_goal_minutes or 30
            session_entry = {
                'day': day_names[day_index],
                'type': study_session.session_type or 'practice',
                'duration': duration_minutes,
                'focus_domains': focus_domains
            }
            current_week_sessions.append(session_entry)

        if current_week_sessions:
            estimated_hours = sum(
                (session_entry.get('duration', 0) or 0) / 60.0
                for session_entry in current_week_sessions
            )
            weekly_schedule.append({
                'week_number': week_number,
                'focus_domains': [],
                'daily_sessions': current_week_sessions,
                'milestone_test': False,
                'estimated_hours': round(estimated_hours, 2)
            })

        if not weekly_schedule:
            current_app.logger.warning(f"Schedule rebuild produced empty weekly_schedule for plan {plan.id}")
            return None

        schedule = {
            'weekly_schedule': weekly_schedule,
            'total_weeks': len(weekly_schedule),
            'recovered_from': 'study_sessions'
        }
        return schedule
    except Exception as rebuild_error:
        current_app.logger.error(f"Failed to rebuild study schedule for plan {plan.id}: {rebuild_error}")
        return None
import os
import json
from flask import jsonify
from models import UserLearningProgress
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from utils.daily_learning_algorithm import DailyLearningAlgorithm
from utils.mastery_helpers import update_item_mastery

learning_bp = Blueprint('learning', __name__)

@learning_bp.route('/')
@login_required
def index():
    """BI-toets Learning Map - overview of all learning paths for dentists"""
    
    # Получаем пути обучения, сгруппированные по компонентам экзамена
    exam_components = {
        'THEORETICAL': [],
        'METHODOLOGY': [],
        'PRACTICAL': [],
        'CLINICAL': []
    }
    
    for path in LearningPath.query.filter_by(is_active=True).order_by(LearningPath.exam_weight.desc()).all():
        # Получаем прогресс пользователя по этому пути
        user_progress = UserLearningProgress.query.filter_by(
            user_id=current_user.id,
            learning_path_id=path.id
        ).first()
        
        progress_percent = user_progress.progress_percentage if user_progress else 0
        
        path_data = {
            'path': path,
            'progress_percent': progress_percent,
            'modules_count': len(path.modules) if path.modules else 0,
            'total_hours': path.total_estimated_hours or 0,
            'duration_weeks': path.duration_weeks or 0
        }
        
        exam_components[path.exam_component].append(path_data)
    
    # Рассчитываем общий прогресс по BI-toets
    total_weight = sum(p['path'].exam_weight for paths in exam_components.values() for p in paths)
    weighted_progress = sum(
        p['progress_percent'] * p['path'].exam_weight / total_weight 
        for paths in exam_components.values() 
        for p in paths
    )
    
    return render_template('learning/bi_toets_index.html', 
                         exam_components=exam_components,
                         total_progress=weighted_progress,
                         total_weight=total_weight)

@learning_bp.route('/path/<path_id>')
@login_required
def learning_path(path_id):
    """View specific BI-toets learning path with modules"""
    
    path = LearningPath.query.filter_by(id=path_id).first_or_404()
    
    # Получаем прогресс пользователя по этому пути
    user_progress = UserLearningProgress.query.filter_by(
        user_id=current_user.id,
        learning_path_id=path.id
    ).first()
    
    if not user_progress:
        # Создаем новую запись прогресса
        user_progress = UserLearningProgress(
            user_id=current_user.id,
            learning_path_id=path.id,
            progress_percentage=0.0,
            completed_modules=[],
            is_active=True
        )
        db.session.add(user_progress)
        db.session.commit()
    
    # Анализируем модули пути
    modules_data = []
    if path.modules:
        # path.modules - это JSON, поэтому нужно его десериализовать
        try:
            modules_list = path.modules if isinstance(path.modules, list) else []
            for module in modules_list:
                # Реализуем прогресс по модулям
                module_id = module.get('id')
                if module_id:
                    # Получаем прогресс по модулю из UserLearningProgress
                    module_progress_obj = UserLearningProgress.query.filter_by(
                        user_id=current_user.id,
                        learning_path_id=module_id
                    ).first()
                    module_progress = module_progress_obj.progress_percentage if module_progress_obj else 0
                else:
                    module_progress = 0
                    
                modules_data.append({
                    'id': module.get('id'),
                    'name': module.get('name'),
                    'domains': module.get('domains', []),
                    'estimated_hours': module.get('estimated_hours', 0),
                    'progress_percent': module_progress,
                    'learning_cards_path': module.get('learning_cards_path'),
                    'virtual_patients': module.get('virtual_patients', [])
                })
        except Exception as e:
            current_app.logger.error(f"Error processing modules for path {path_id}: {e}")
            modules_data = []
    
    # Проверяем предварительные требования
    prerequisites_met = True
    if path.prerequisites:
        for prereq_id in path.prerequisites:
            prereq_progress = UserLearningProgress.query.filter_by(
                user_id=current_user.id,
                learning_path_id=prereq_id
            ).first()
            if not prereq_progress or prereq_progress.progress_percentage < 80:
                prerequisites_met = False
                break
    
    return render_template('learning/path.html',
                         path=path,
                         user_progress=user_progress,
                         modules=modules_data,
                         prerequisites_met=prerequisites_met)

@learning_bp.route('/subject/<int:subject_id>')
@login_required
def subject(subject_id):
    """View specific subject with modules"""
    
    subject = Subject.query.get_or_404(subject_id)
    
    modules_data = []
    for module in subject.modules.order_by(Module.order).all():
        module_progress = module.get_progress_for_user(current_user.id)
        modules_data.append({
            'module': module,
            **module_progress
        })
    
    # Get subject progress
    subject_progress = subject.get_progress_for_user(current_user.id)
    
    return render_template('learning/subject.html',
                         subject=subject,
                         modules=modules_data,
                         **subject_progress)

@learning_bp.route('/module/<int:module_id>')
@login_required
def module(module_id):
    """View specific module with lessons"""
    
    module = Module.query.get_or_404(module_id)
    
    # Get all lessons in this module
    lessons = module.lessons.order_by(Lesson.order).all()
    
    # Get user progress for each lesson
    lessons_data = []
    for lesson in lessons:
        progress = lesson.get_user_progress(current_user.id)
        lessons_data.append({
            'lesson': lesson,
            'progress': progress,
            'completed': progress.completed if progress else False,
            'time_spent': progress.time_spent if progress else 0
        })
    
    # Get module progress
    module_progress = module.get_progress_for_user(current_user.id)
    
    return render_template('learning/module.html',
                         module=module,
                         lessons=lessons_data,
                         **module_progress)

@learning_bp.route('/lesson/<int:lesson_id>')
@login_required
def lesson(lesson_id):
    """View and study specific lesson"""
    
    lesson = Lesson.query.get_or_404(lesson_id)
    
    # Get or create user progress
    progress = lesson.get_user_progress(current_user.id)
    if not progress:
        progress = UserProgress(
            user_id=current_user.id,
            lesson_id=lesson.id
        )
        db.session.add(progress)
        db.session.commit()
    
    # Update last accessed
    progress.last_accessed = datetime.now(timezone.utc)
    db.session.commit()
    
    # Get navigation info (previous/next lessons)
    module = lesson.module
    if not module:
        flash('Урок не связан с модулем', 'error')
        return redirect(url_for('learning.index'))
    
    lessons_in_module = module.lessons.order_by(Lesson.order).all()
    
    current_index = next((i for i, l in enumerate(lessons_in_module) if l.id == lesson.id), 0)
    prev_lesson = lessons_in_module[current_index - 1] if current_index > 0 else None
    next_lesson = lessons_in_module[current_index + 1] if current_index < len(lessons_in_module) - 1 else None
    
    # Parse content if it's JSON
    import json
    content_data = None
    if lesson.content:
        try:
            content_data = json.loads(lesson.content)
        except (json.JSONDecodeError, TypeError):
            content_data = {'text': lesson.content}
    
    return render_template('learning/lesson.html',
                         lesson=lesson,
                         module=module,
                         progress=progress,
                         content_data=content_data,
                         prev_lesson=prev_lesson,
                         next_lesson=next_lesson,
                         lesson_index=current_index + 1,
                         total_lessons=len(lessons_in_module))

@learning_bp.route('/lesson/<int:lesson_id>/complete', methods=['POST'])
@login_required
def complete_lesson(lesson_id):
    """Mark lesson as completed"""
    
    lesson = Lesson.query.get_or_404(lesson_id)
    
    # Get or create progress
    progress = lesson.get_user_progress(current_user.id)
    if not progress:
        progress = UserProgress(
            user_id=current_user.id,
            lesson_id=lesson.id
        )
        db.session.add(progress)
    
    # Get time spent from request
    time_spent = float(request.form.get('time_spent', 0))
    score = request.form.get('score')
    
    # Mark as completed
    if not progress.completed:
        progress.mark_completed(score=float(score) if score else None)
        
        # ✅ FIX: Update daily activity, streak, XP
        xp_earned = 10  # Base XP for completing a lesson
        current_user.update_daily_activity(
            lessons_completed=1,
            time_spent=time_spent,
            xp_earned=xp_earned
        )
    
    # Add time spent
    if time_spent > 0:
        progress.add_time_spent(time_spent)
    
    try:
        db.session.commit()
        
        # ✅ Clear cache after progress update
        from utils.diagnostic_data_manager import clear_cache
        clear_cache(current_user.id)
        
        # Return JSON response for AJAX requests
        if request.headers.get('Content-Type') == 'application/json':
            return safe_jsonify({
                'success': True,
                'message': 'Lesson completed successfully!',
                'completed': True,
                'time_spent': progress.time_spent,
                'score': progress.score
            })
        
        flash('Lesson completed successfully!', 'success')
        
        # Redirect to next lesson or module
        module = lesson.module
        lessons_in_module = module.lessons.order_by(Lesson.order).all()
        current_index = next((i for i, l in enumerate(lessons_in_module) if l.id == lesson.id), 0)
        
        if current_index < len(lessons_in_module) - 1:
            next_lesson = lessons_in_module[current_index + 1]
            return redirect(url_for('learning.lesson', lesson_id=next_lesson.id))
        else:
            return redirect(url_for('learning.module', module_id=module.id))
    
    except Exception as e:
        db.session.rollback()
        
        if request.headers.get('Content-Type') == 'application/json':
            return safe_jsonify({
                'success': False,
                'message': 'Failed to complete lesson'
            }), 500
        
        flash('Failed to complete lesson. Please try again.', 'error')
        return redirect(url_for('learning.lesson', lesson_id=lesson_id))

@learning_bp.route('/search')
@login_required
def search():
    """Search lessons and content"""
    
    query = request.args.get('q', '').strip()
    
    if not query:
        return render_template('learning/search.html', results=[], query=query)
    
    # Search in lesson titles and content
    results = []
    
    # Search lessons
    lessons = Lesson.query.filter(
        (Lesson.title.contains(query)) |
        (Lesson.content.contains(query))
    ).all()
    
    for lesson in lessons:
        progress = lesson.get_user_progress(current_user.id)
        results.append({
            'type': 'lesson',
            'item': lesson,
            'module': lesson.module,
            'subject': lesson.module.subject,
            'path': lesson.module.subject.learning_path,
            'completed': progress.completed if progress else False
        })
    
    # Search modules
    modules = Module.query.filter(
        (Module.title.contains(query)) |
        (Module.description.contains(query))
    ).all()
    
    for module in modules:
        progress = module.get_progress_for_user(current_user.id)
        results.append({
            'type': 'module',
            'item': module,
            'subject': module.subject,
            'path': module.subject.learning_path,
            'progress_percent': progress['progress_percent']
        })
    
    return render_template('learning/search.html', results=results, query=query)

@learning_bp.route('/api/progress/<int:lesson_id>', methods=['POST'])
@login_required
def api_update_progress(lesson_id):
    """API endpoint to update lesson progress"""
    
    lesson = Lesson.query.get_or_404(lesson_id)
    
    # Get or create progress
    progress = lesson.get_user_progress(current_user.id)
    if not progress:
        progress = UserProgress(
            user_id=current_user.id,
            lesson_id=lesson.id
        )
        db.session.add(progress)
    
    # Update progress data
    data = request.get_json()
    
    if 'time_spent' in data:
        progress.add_time_spent(float(data['time_spent']))
    
    if 'completed' in data and data['completed']:
        progress.mark_completed(score=data.get('score'))
        
        # ✅ FIX: Update daily activity, streak, XP
        xp_earned = 10
        current_user.update_daily_activity(
            lessons_completed=1,
            time_spent=float(data.get('time_spent', 0)),
            xp_earned=xp_earned
        )
    
    try:
        db.session.commit()
        
        # ✅ Clear cache after progress update
        from utils.diagnostic_data_manager import clear_cache
        clear_cache(current_user.id)
        
        return safe_jsonify({
            'success': True,
            'completed': progress.completed,
            'time_spent': progress.time_spent,
            'score': progress.score
        })
    
    except Exception as e:
        db.session.rollback()
        return safe_jsonify({
            'success': False,
            'error': str(e)
        }), 500

@learning_bp.route('/api/path-progress/<path_id>', methods=['POST'])
@login_required
def api_update_path_progress(path_id):
    """API endpoint to update learning path progress"""
    
    path = LearningPath.query.filter_by(id=path_id).first_or_404()
    
    # Get or create progress
    progress = UserLearningProgress.query.filter_by(
        user_id=current_user.id,
        learning_path_id=path.id
    ).first()
    
    if not progress:
        progress = UserLearningProgress(
            user_id=current_user.id,
            learning_path_id=path.id,
            progress_percentage=0.0,
            completed_modules=[],
            is_active=True
        )
        db.session.add(progress)
    
    # Update progress data
    data = request.get_json()
    
    if 'progress_percentage' in data:
        progress.progress_percentage = float(data['progress_percentage'])
    
    if 'completed_modules' in data:
        progress.completed_modules = data['completed_modules']
    
    if 'time_spent' in data:
        progress.total_time_spent += int(data['time_spent'])
    
    if 'lessons_completed' in data:
        progress.lessons_completed += int(data['lessons_completed'])
    
    if 'tests_passed' in data:
        progress.tests_passed += int(data['tests_passed'])
    
    progress.last_accessed = datetime.now(timezone.utc)
    
    try:
        db.session.commit()
        return safe_jsonify({
            'success': True,
            'progress_percentage': progress.progress_percentage,
            'completed_modules': progress.completed_modules,
            'total_time_spent': progress.total_time_spent,
            'lessons_completed': progress.lessons_completed,
            'tests_passed': progress.tests_passed
        })
    
    except Exception as e:
        db.session.rollback()
        return safe_jsonify({
            'success': False,
            'error': str(e)
        }), 500 

@learning_bp.route('/automated/theory')
@learning_bp.route('/automated/theory/<int:plan_id>/<int:week>')
@login_required
def automated_theory(plan_id=None, week=None):
    """Automated theory learning session"""
    
    # Get learning plan session data from URL parameters or session
    if plan_id is None:
        plan_id = session.get('learning_plan_id')
    if week is None:
        week = session.get('current_week')
    
    current_session = session.get('current_session')
    
    print(f"🔧 DEBUG: automated_theory - plan_id={plan_id}, week={week}, session={current_session}")
    
    if not plan_id:
        flash('ID плана обучения не найден', 'error')
        return redirect(url_for('dashboard.index'))
    
    # Get the learning plan
    plan = PersonalLearningPlan.query.get_or_404(plan_id)
    
    # If we don't have session data, try to reconstruct it
    if not current_session or not week:
        study_schedule = plan.get_study_schedule()
        if study_schedule and study_schedule.get('weekly_schedule'):
            # Find the first session
            for week_data in study_schedule['weekly_schedule']:
                for daily_session in week_data['daily_sessions']:
                    if daily_session['type'] == 'theory':
                        current_session = daily_session
                        week = week_data['week_number']
                        # Save to session for future use
                        session['learning_plan_id'] = plan_id
                        session['current_week'] = week
                        session['current_session'] = current_session
                        session['learning_mode'] = 'automated'
                        break
                if current_session:
                    break
    
    if not current_session:
        flash('Сессия обучения не найдена', 'error')
        return redirect(url_for('dashboard.learning_plan', plan_id=plan_id))
    
    # Get recommended lessons based on weak domains using smart recommendations
    weak_domains = plan.get_weak_domain_names()  # Используем полные названия
    
    # Use smart content recommendations
    from utils.content_recommendations import get_smart_recommendations
    recommended_lessons = get_smart_recommendations(current_user.id, weak_domains, limit=6)
    
    # If no domain-specific lessons, get general lessons
    if not recommended_lessons:
        recommended_lessons = Lesson.query.limit(5).all()
    
    return render_template('learning/automated_theory.html',
                         plan=plan,
                         current_week=week,
                         current_session=current_session,
                         recommended_lessons=recommended_lessons)

@learning_bp.route('/automated/practice')
@learning_bp.route('/automated/practice/<int:plan_id>/<int:week>')
@login_required
def automated_practice(plan_id=None, week=None):
    """Automated practice session"""
    
    # Get learning plan session data from URL parameters or session
    if plan_id is None:
        plan_id = session.get('learning_plan_id')
    if week is None:
        week = session.get('current_week')
    
    current_session = session.get('current_session')
    # Auto-rotate daily session by calendar date (сброс в полночь)
    try:
        from datetime import date as _date
        session_date = session.get('daily_session_date')
        today_str = _date.today().isoformat()
        
        if session_date and session_date != today_str:
            # Outdated daily session → start a new one
            current_app.logger.info(f"Daily session date mismatch: session_date={session_date}, today={today_str}. Resetting session.")
            session.pop('daily_session_questions', None)
            session.pop('daily_session_diagnostic_id', None)
            session.pop('daily_session_active', None)
            session.pop('daily_session_date', None)
            return redirect(url_for('individual_plan_api.start_daily_session'))
    except Exception as e:
        current_app.logger.warning(f"Error checking daily session date: {e}")
        pass
    
    print(f"🔧 DEBUG: automated_practice - plan_id={plan_id}, week={week}, session={current_session}")
    
    if not plan_id:
        flash('ID плана обучения не найден', 'error')
        return redirect(url_for('dashboard.index'))
    
    plan = PersonalLearningPlan.query.get_or_404(plan_id)
    
    # If we don't have session data, try to reconstruct it
    if not current_session or not week:
        study_schedule = plan.get_study_schedule()
        if study_schedule and study_schedule.get('weekly_schedule'):
            # Find the first practice session
            for week_data in study_schedule['weekly_schedule']:
                for daily_session in week_data['daily_sessions']:
                    if daily_session['type'] == 'practice':
                        current_session = daily_session
                        week = week_data['week_number']
                        # Save to session for future use
                        session['learning_plan_id'] = plan_id
                        session['current_week'] = week
                        session['current_session'] = current_session
                        session['learning_mode'] = 'automated'
                        break
                if current_session:
                    break
    
    if not current_session:
        flash('Сессия обучения не найдена', 'error')
        return redirect(url_for('dashboard.learning_plan', plan_id=plan_id))
    
    # Get practice questions based on weak domains
    weak_domains = plan.get_weak_domain_names()  # Используем полные названия
    practice_questions = []
    
    # Check if we have daily_session_questions in session (from start_daily_session)
    if 'daily_session_questions' in session and session.get('daily_session_active'):
        # Use the questions already selected for today
        question_ids = session.get('daily_session_questions', [])
        practice_questions = Question.query.filter(Question.id.in_(question_ids)).all()
        print(f"🔧 DEBUG: Using {len(practice_questions)} questions from daily_session_questions")
    else:
        # Fallback: get questions based on weak domains
        if weak_domains:
            for domain_name in weak_domains:
                domain_questions = Question.query.join(BIGDomain).filter(
                    BIGDomain.name.contains(domain_name)
                ).limit(5).all()
                practice_questions.extend(domain_questions)
        
        # If no domain-specific questions, get general questions
        if not practice_questions:
            practice_questions = Question.query.limit(10).all()
        
        # Store for next time to avoid repeats
        session['last_practice_questions'] = [q.id for q in practice_questions]
    
    # Convert Question objects to JSON-serializable dictionaries
    questions_data = []
    for q in practice_questions:
        questions_data.append({
            'id': q.id,
            'text': q.text,
            'options': q.options,
            'correct_answer_index': q.correct_answer_index,
            'correct_answer_text': q.correct_answer_text,
            'explanation': q.explanation,
            'difficulty_level': q.difficulty_level,
            'category': q.category,
            'domain': q.domain,
            'question_type': q.question_type
        })
    
    return render_template('learning/automated_practice.html',
                         plan=plan,
                         current_week=week,
                         current_session=current_session,
                         practice_questions=questions_data)

@learning_bp.route('/automated/test')
@login_required
def automated_test():
    """Automated test session"""
    
    plan_id = session.get('learning_plan_id')
    current_week = session.get('current_week')
    current_session = session.get('current_session')
    
    if not plan_id or not current_session:
        flash('Сессия обучения не найдена', 'error')
        return redirect(url_for('dashboard.index'))
    
    plan = PersonalLearningPlan.query.get_or_404(plan_id)
    
    # Get or create a test for this week
    # For now, we'll redirect to a general test
    return redirect(url_for('diagnostic.start_diagnostic'))

@learning_bp.route('/automated/review')
@login_required
def automated_review():
    """Automated review session"""
    
    plan_id = session.get('learning_plan_id')
    current_week = session.get('current_week')
    current_session = session.get('current_session')
    
    if not plan_id or not current_session:
        flash('Сессия обучения не найдена', 'error')
        return redirect(url_for('dashboard.index'))
    
    plan = PersonalLearningPlan.query.get_or_404(plan_id)
    
    # Get recently completed lessons for review
    recent_lessons = UserProgress.query.filter_by(
        user_id=current_user.id,
        completed=True
    ).order_by(UserProgress.completed_at.desc()).limit(10).all()
    
    return render_template('learning/automated_review.html',
                         plan=plan,
                         current_week=current_week,
                         current_session=current_session,
                         recent_lessons=recent_lessons)

@learning_bp.route('/automated/complete-session', methods=['POST'])
@login_required
def complete_automated_session():
    """Complete current automated learning session"""
    try:
        plan_id = session.get('learning_plan_id')
        current_week = session.get('current_week')
        current_session = session.get('current_session')
        
        # Get data from request
        data = request.get_json() or {}
        questions_answered = data.get('questions_answered', 0)
        correct_answers = data.get('correct_answers', 0)
        time_spent = data.get('time_spent', 0)
        
        # Добавляем диагностику
        current_app.logger.info(f"Complete session request - plan_id: {plan_id}, week: {current_week}, session: {current_session}")
        current_app.logger.info(f"Session data: questions_answered={questions_answered}, correct_answers={correct_answers}, time_spent={time_spent}")
        
        if not plan_id or not current_session:
            # Мягкое восстановление: если сессия потеряна, перенаправим на запуск дневной сессии
            current_app.logger.warning(
                f"No active session in complete_automated_session – plan_id={plan_id}, current_session={current_session}. "
                "Returning redirect to start_daily_session."
            )
            # Попробуем закрыть DiagnosticSession, если он есть
            diagnostic_session_id = session.get('daily_session_diagnostic_id')
            if diagnostic_session_id:
                try:
                    diagnostic_session = DiagnosticSession.query.get(diagnostic_session_id)
                    if diagnostic_session:
                        diagnostic_session.questions_answered = questions_answered
                        diagnostic_session.correct_answers = correct_answers
                        diagnostic_session.completed_at = datetime.now(timezone.utc)
                        diagnostic_session.status = 'completed'
                        db.session.commit()
                except Exception as e2:
                    current_app.logger.error(f"Failed to finalize DiagnosticSession on soft-complete: {e2}")
            redirect_url = url_for('individual_plan_api.start_daily_session')
            return safe_jsonify({
                'success': True,
                'redirect_url': redirect_url,
                'next_session': None,
                'completed': False
            }), 200
        
        plan = PersonalLearningPlan.query.get_or_404(plan_id)
        current_app.logger.info(f"Found plan: {plan.id} for user: {plan.user_id}")
        
        # ✅ Update DiagnosticSession if this is a daily practice session
        diagnostic_session_id = session.get('daily_session_diagnostic_id')
        if diagnostic_session_id:
            diagnostic_session = DiagnosticSession.query.get(diagnostic_session_id)
            if diagnostic_session:
                session_completed_at = datetime.now(timezone.utc)
                diagnostic_session.questions_answered = questions_answered
                diagnostic_session.correct_answers = correct_answers
                diagnostic_session.completed_at = session_completed_at
                diagnostic_session.status = 'completed'
                if time_spent is not None:
                    try:
                        current_time_spent = diagnostic_session.time_spent or 0.0
                        diagnostic_session.time_spent = current_time_spent + float(time_spent)
                    except Exception as e:
                        current_app.logger.warning(f"Failed to update diagnostic_session time_spent: {e}")

                session_date = (diagnostic_session.completed_at or session_completed_at).date()
                responses = DiagnosticResponse.query.filter_by(session_id=diagnostic_session.id).all()
                for response in responses:
                    if not response.question_id:
                        continue
                    update_item_mastery(
                        user_id=current_user.id,
                        item_type='question',
                        item_id=response.question_id,
                        is_correct=bool(response.is_correct),
                        session_reference=f'test-{diagnostic_session.id}',
                        session_date=session_date
                    )

                current_app.logger.info(f"✅ Updated DiagnosticSession {diagnostic_session_id}: questions={questions_answered}, correct={correct_answers}")
        
        # ✅ Update time_invested if time_spent provided
        if time_spent > 0:
            plan.add_time_invested(int(time_spent))
            current_app.logger.info(f"Updated time_invested: {plan.time_invested}")
        
        # ✅ Update daily streak when session is completed
        from datetime import date
        plan.update_daily_streak(date.today())
        current_app.logger.info(f"Updated daily streak: {plan.daily_streak}")
        db.session.commit()
        
        # ✅ Для дневных сессий всегда возвращаем на карту дневной сессии после завершения
        # Не требуем study schedule для daily sessions
        if session.get('daily_session_active'):
            # После завершения любой сессии в дневном режиме возвращаем на карту дневной сессии
            # Пользователь сам выберет следующий шаг оттуда
            lang = session.get('lang', 'nl')
            redirect_url = f'/{lang}/learning-map/daily-session'
            return safe_jsonify({
                'success': True,
                'redirect_url': redirect_url,
                'next_session': None,
                'completed': True
            }), 200
        
        # Для не-дневных сессий нужен study schedule
        study_schedule = plan.get_study_schedule()
        current_app.logger.info(f"Study schedule keys: {list(study_schedule.keys()) if study_schedule else 'None'}")
        
        if not study_schedule or 'weekly_schedule' not in study_schedule:
            current_app.logger.warning(f"Invalid study schedule detected for plan {plan.id}, attempting rebuild. Raw schedule: {study_schedule}")
            rebuilt_schedule = _rebuild_study_schedule_from_sessions(plan)
            if rebuilt_schedule and rebuilt_schedule.get('weekly_schedule'):
                plan.set_study_schedule(rebuilt_schedule)
                study_schedule = rebuilt_schedule
                db.session.commit()
                current_app.logger.info(f"Study schedule rebuilt from existing sessions for plan {plan.id}")
            else:
                # Если не удалось перестроить, но это не критично - просто возвращаем на dashboard
                current_app.logger.warning(f"Unable to rebuild study schedule for plan {plan.id}, redirecting to dashboard")
                return safe_jsonify({
                    'success': True,
                    'redirect_url': url_for('dashboard.index'),
                    'next_session': None,
                    'completed': True
                }), 200
        
        # Find next session
        next_session = None
        next_week = None
        
        found_current = False
        for week_data in study_schedule['weekly_schedule']:
            for session_data in week_data['daily_sessions']:
                if found_current:
                    next_session = session_data
                    next_week = week_data
                    break
                if (week_data['week_number'] == current_week and 
                    session_data['day'] == current_session['day'] and 
                    session_data['type'] == current_session['type']):
                    found_current = True
                    current_app.logger.info(f"Found current session: {session_data}")
            if next_session:
                break
        
        current_app.logger.info(f"Next session found: {next_session is not None}")
        
        # Update session data
        if next_session:
            session['current_week'] = next_week['week_number']
            session['current_session'] = next_session
            
            # Determine next redirect (для не-дневных сессий)
            if next_session['type'] == 'theory':
                redirect_url = url_for('learning.automated_theory')
            elif next_session['type'] == 'practice':
                redirect_url = url_for('learning.automated_practice')
            elif next_session['type'] == 'test':
                redirect_url = url_for('learning.automated_test')
            elif next_session['type'] == 'review':
                redirect_url = url_for('learning.automated_review')
            else:
                redirect_url = url_for('learning.automated_theory')
        else:
            # All sessions completed
            if session.get('daily_session_active'):
                # Если это дневная сессия и план не знает «следующей», возвращаем на карту дневной сессии
                lang = session.get('lang', 'nl')
                redirect_url = f'/{lang}/learning-map/daily-session'
            else:
                session.pop('learning_plan_id', None)
                session.pop('current_week', None)
                session.pop('current_session', None)
                session.pop('learning_mode', None)
                session.pop('daily_session_diagnostic_id', None)  # Clear diagnostic session ID
                redirect_url = url_for('dashboard.learning_plan', plan_id=plan_id)
        
        current_app.logger.info(f"Redirect URL: {redirect_url}")
        
        return safe_jsonify({
            'success': True,
            'redirect_url': redirect_url,
            'next_session': next_session,
            'completed': next_session is None
        })
        
    except Exception as e:
        current_app.logger.error(f"Error completing automated session: {str(e)}")
        import traceback
        traceback.print_exc()
        return safe_jsonify({
            'error': 'Internal server error',
            'details': str(e)
        }), 500

@learning_bp.route('/test-theory')
def test_theory():
    """Тестовый маршрут для отладки теории без авторизации"""
    
    # Создаем тестовые данные
    test_data = {
        'plan_id': 1,
        'current_week': 1,
        'current_session': {
            'type': 'theory',
            'duration': 2.0,
            'focus_domains': ['Терапия', 'Хирургия']
        },
        'recommended_lessons': [
            {
                'id': 1,
                'title': 'Основы стоматологической терапии',
                'description': 'Введение в основные принципы терапевтической стоматологии',
                'estimated_duration': 45,
                'module': {'name': 'Терапия'}
            },
            {
                'id': 2,
                'title': 'Хирургические вмешательства',
                'description': 'Основы хирургической стоматологии и показания к операциям',
                'estimated_duration': 60,
                'module': {'name': 'Хирургия'}
            }
        ]
    }
    
    return render_template('learning/automated_theory.html',
                         plan=test_data,
                         current_week=test_data['current_week'],
                         current_session=test_data['current_session'],
                         recommended_lessons=test_data['recommended_lessons'])

@learning_bp.route('/learning-paths')
@login_required
def learning_paths():
    """Отображение путей обучения в структуре BI-toets"""
    try:
        # Получить структуру BI-toets
        learning_paths = LearningPath.get_bi_toets_structure()
        
        return render_template('dashboard/learning_paths.html', 
                             learning_paths=learning_paths)
    except Exception as e:
        flash(f'Ошибка при загрузке путей обучения: {str(e)}', 'error')
        return redirect(url_for('dashboard.index'))

@learning_bp.route('/api/learning-paths/<path_id>')
def get_learning_path(path_id):
    """API для получения детальной информации о пути обучения"""
    try:
        path = LearningPath.query.get(path_id)
        if not path:
            return jsonify({'success': False, 'message': 'Путь не найден'})
        
        return jsonify({
            'success': True,
            'path': path.to_dict()
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@learning_bp.route('/learning/path/<path_id>')
@login_required
def start_learning_path(path_id):
    """Начать обучение по выбранному пути"""
    try:
        path = LearningPath.query.get(path_id)
        if not path:
            flash('Путь обучения не найден', 'error')
            return redirect(url_for('learning.learning_paths'))
        
        # Проверить предварительные требования
        if path.prerequisites:
            user_progress = current_user.get_all_path_progress()
            missing_prereqs = []
            
            for prereq_id in path.prerequisites:
                prereq_progress = user_progress.get(prereq_id)
                if not prereq_progress or prereq_progress.progress_percentage < 100:
                    missing_prereqs.append(prereq_id)
            
            if missing_prereqs:
                flash('Необходимо завершить предварительные пути обучения', 'warning')
                return redirect(url_for('learning.learning_paths'))
        
        # Создать или получить прогресс пользователя
        progress = UserLearningProgress.query.filter_by(
            user_id=current_user.id,
            learning_path_id=path_id
        ).first()
        
        if not progress:
            progress = UserLearningProgress(
                user_id=current_user.id,
                learning_path_id=path_id,
                progress_percentage=0,
                completed_modules=[],
                last_accessed=datetime.now(timezone.utc)
            )
            db.session.add(progress)
            db.session.commit()
        
        # Перенаправить на первый модуль
        if path.modules:
            first_module = path.modules[0]
            return redirect(url_for('learning.module_view', 
                                  path_id=path_id, 
                                  module_id=first_module['id']))
        
        flash('Путь обучения не содержит модулей', 'error')
        return redirect(url_for('learning.learning_paths'))
        
    except Exception as e:
        flash(f'Ошибка при запуске пути обучения: {str(e)}', 'error')
        return redirect(url_for('learning.learning_paths'))

@learning_bp.route('/learning/path/<path_id>/module/<module_id>')
@login_required
def module_view(path_id, module_id):
    """Отображение модуля обучения"""
    try:
        path = LearningPath.query.get(path_id)
        if not path:
            flash('Путь обучения не найден', 'error')
            return redirect(url_for('learning.learning_paths'))
        
        # Найти модуль
        module = None
        for m in path.modules:
            if m['id'] == module_id:
                module = m
                break
        
        if not module:
            flash('Модуль не найден', 'error')
            return redirect(url_for('learning.learning_paths'))
        
        # Получить прогресс пользователя
        progress = UserLearningProgress.query.filter_by(
            user_id=current_user.id,
            learning_path_id=path_id
        ).first()
        
        # Загрузить контент модуля
        module_content = load_module_content(module)
        
        return render_template('learning/module_view.html',
                             path=path,
                             module=module,
                             module_content=module_content,
                             progress=progress)
        
    except Exception as e:
        flash(f'Ошибка при загрузке модуля: {str(e)}', 'error')
        return redirect(url_for('learning.learning_paths'))

def load_module_content(module):
    """Загрузить контент модуля (карточки, виртуальные пациенты и т.д.)"""
    content = {
        'learning_cards': [],
        'virtual_patients': [],
        'theory_content': []
    }
    
    try:
        # Загрузить карточки обучения
        if 'learning_cards_path' in module:
            cards_path = module['learning_cards_path']
            if cards_path and os.path.exists(cards_path):
                # Здесь будет логика загрузки карточек
                pass
        
        # Загрузить виртуальных пациентов
        if 'virtual_patients' in module:
            for patient_id in module['virtual_patients']:
                # Здесь будет логика загрузки виртуальных пациентов
                pass
        
        # Загрузить теоретический контент
        if 'content' in module:
            content['theory_content'] = module['content']
        
        return content
        
    except Exception as e:
        print(f"Ошибка при загрузке контента модуля: {e}")
        return content

# Функция для получения языка
def get_lang():
    """Получает язык из g или возвращает 'nl' по умолчанию"""
    return getattr(g, 'lang', 'nl')

# Создаем Blueprint для фармацевтических инструментов
pharmacy_tools_bp = Blueprint('pharmacy_tools', __name__)

@pharmacy_tools_bp.before_request
def before_request():
    """Выполняется перед каждым запросом к pharmacy_tools"""
    lang = request.view_args.get('lang')
    g.lang = lang
    session['lang'] = lang

@pharmacy_tools_bp.context_processor
def inject_lang():
    """Внедряет язык в контекст шаблонов"""
    return {'lang': g.lang}

@pharmacy_tools_bp.route('/<lang>/farmacie/advanced-drug-checker')
@login_required
def advanced_drug_checker(lang):
    """Расширенный Drug Interaction Checker"""
    # Используем переданный параметр lang
    
    # База данных лекарственных взаимодействий
    drug_interactions = {
        'warfarine': {
            'name': 'Warfarine',
            'category': 'Anticoagulantia',
            'interactions': {
                'ibuprofen': {
                    'severity': 'MAJOR',
                    'description': 'Verhoogd bloedingsrisico door remming van bloedplaatjesaggregatie',
                    'recommendation': 'Vermijd combinatie. Gebruik paracetamol als alternatief.',
                    'mechanism': 'Synergistische remming van bloedstolling'
                },
                'aspirine': {
                    'severity': 'MAJOR',
                    'description': 'Verhoogd risico op bloedingen',
                    'recommendation': 'Strikte monitoring van INR vereist',
                    'mechanism': 'Dubbele remming van bloedstolling'
                },
                'omeprazol': {
                    'severity': 'MODERATE',
                    'description': 'Mogelijk verhoogde warfarine effectiviteit',
                    'recommendation': 'Monitor INR frequentie verhogen',
                    'mechanism': 'CYP2C19 remming'
                }
            }
        },
        'digoxine': {
            'name': 'Digoxine',
            'category': 'Cardiaca',
            'interactions': {
                'furosemide': {
                    'severity': 'MAJOR',
                    'description': 'Verhoogd risico op digitalis toxiciteit door hypokaliëmie',
                    'recommendation': 'Strikte monitoring van kalium en digoxine spiegel',
                    'mechanism': 'Kaliumverlies door diurese'
                },
                'amiodarone': {
                    'severity': 'MAJOR',
                    'description': 'Verhoogde digoxine concentratie door remming van uitscheiding',
                    'recommendation': 'Digoxine dosering met 50% verlagen',
                    'mechanism': 'P-gp remming'
                },
                'verapamil': {
                    'severity': 'MODERATE',
                    'description': 'Verhoogde digoxine concentratie',
                    'recommendation': 'Monitor digoxine spiegel',
                    'mechanism': 'P-gp remming'
                }
            }
        },
        'simvastatine': {
            'name': 'Simvastatine',
            'category': 'Lipidenverlagers',
            'interactions': {
                'amiodarone': {
                    'severity': 'MAJOR',
                    'description': 'Verhoogd risico op rhabdomyolyse',
                    'recommendation': 'Simvastatine dosering beperken tot 20mg/dag',
                    'mechanism': 'CYP3A4 remming'
                },
                'diltiazem': {
                    'severity': 'MODERATE',
                    'description': 'Verhoogde statine concentratie',
                    'recommendation': 'Monitor voor spierklachten',
                    'mechanism': 'CYP3A4 remming'
                }
            }
        },
        'metoprolol': {
            'name': 'Metoprolol',
            'category': 'Beta-blokkers',
            'interactions': {
                'verapamil': {
                    'severity': 'MODERATE',
                    'description': 'Verhoogd risico op bradycardie en hypotensie',
                    'recommendation': 'Strikte monitoring van hartritme en bloeddruk',
                    'mechanism': 'Additieve cardiodepressieve effecten'
                },
                'digoxine': {
                    'severity': 'MINOR',
                    'description': 'Mogelijk verhoogde bradycardie',
                    'recommendation': 'Monitor hartritme',
                    'mechanism': 'Additieve bradycardie'
                }
            }
        },
        'clopidogrel': {
            'name': 'Clopidogrel',
            'category': 'Antiplaatjesmiddelen',
            'interactions': {
                'omeprazol': {
                    'severity': 'MODERATE',
                    'description': 'Verminderde effectiviteit van clopidogrel',
                    'recommendation': 'Overweeg pantoprazol als alternatief',
                    'mechanism': 'CYP2C19 remming'
                },
                'aspirine': {
                    'severity': 'MAJOR',
                    'description': 'Verhoogd bloedingsrisico',
                    'recommendation': 'Alleen bij specifieke indicaties (ACS, PCI)',
                    'mechanism': 'Dubbele antiplaatjeswerking'
                }
            }
        }
    }
    
    # Категории лекарств для фильтрации
    drug_categories = {
        'Anticoagulantia': ['warfarine', 'acenocoumarol', 'fenprocoumon'],
        'Cardiaca': ['digoxine', 'amiodarone', 'verapamil', 'diltiazem'],
        'Lipidenverlagers': ['simvastatine', 'atorvastatine', 'pravastatine'],
        'Beta-blokkers': ['metoprolol', 'atenolol', 'bisoprolol'],
        'Antiplaatjesmiddelen': ['clopidogrel', 'aspirine', 'ticagrelor'],
        'NSAIDs': ['ibuprofen', 'diclofenac', 'naproxen'],
        'Protonpompremmers': ['omeprazol', 'pantoprazol', 'esomeprazol']
    }
    
    return render_template(
        'learning/advanced_drug_checker.html',
        drug_interactions=drug_interactions,
        drug_categories=drug_categories,
        lang=lang
    )

@pharmacy_tools_bp.route('/<lang>/farmacie/api/check-interaction', methods=['POST'])
@login_required
def check_interaction(lang):
    """API endpoint для проверки взаимодействий"""
    try:
        data = request.get_json()
        drug1 = data.get('drug1', '').lower()
        drug2 = data.get('drug2', '').lower()
        
        if not drug1 or not drug2:
            return safe_jsonify({'error': 'Beide medicijnen moeten worden ingevuld'}), 400
        
        # База данных взаимодействий (упрощенная версия)
        interactions_db = {
            'warfarine+ibuprofen': {
                'severity': 'MAJOR',
                'description': 'Verhoogd bloedingsrisico',
                'recommendation': 'Vermijd combinatie',
                'mechanism': 'Synergistische remming van bloedstolling'
            },
            'warfarine+aspirine': {
                'severity': 'MAJOR',
                'description': 'Verhoogd risico op bloedingen',
                'recommendation': 'Strikte monitoring van INR',
                'mechanism': 'Dubbele remming van bloedstolling'
            },
            'digoxine+furosemide': {
                'severity': 'MAJOR',
                'description': 'Digitalis toxiciteit risico',
                'recommendation': 'Monitor kalium en digoxine spiegel',
                'mechanism': 'Kaliumverlies door diurese'
            },
            'simvastatine+amiodarone': {
                'severity': 'MAJOR',
                'description': 'Verhoogd risico op rhabdomyolyse',
                'recommendation': 'Dosering beperken tot 20mg/dag',
                'mechanism': 'CYP3A4 remming'
            }
        }
        
        # Проверяем взаимодействие
        key1 = f"{drug1}+{drug2}"
        key2 = f"{drug2}+{drug1}"
        
        interaction = interactions_db.get(key1) or interactions_db.get(key2)
        
        if interaction:
            return safe_jsonify({
                'found': True,
                'interaction': interaction
            })
        else:
            return safe_jsonify({
                'found': False,
                'message': 'Geen bekende interactie gevonden'
            })
            
    except Exception as e:
        current_app.logger.error(f"Error in check_interaction: {e}")
        return safe_jsonify({'error': 'Er is een fout opgetreden'}), 500

@pharmacy_tools_bp.route('/<lang>/farmacie/api/search-drugs')
@login_required
def search_drugs(lang):
    """API endpoint для поиска лекарств"""
    try:
        query = request.args.get('q', '').lower()
        
        # База данных лекарств
        drugs_db = {
            'warfarine': {'name': 'Warfarine', 'category': 'Anticoagulantia'},
            'digoxine': {'name': 'Digoxine', 'category': 'Cardiaca'},
            'simvastatine': {'name': 'Simvastatine', 'category': 'Lipidenverlagers'},
            'metoprolol': {'name': 'Metoprolol', 'category': 'Beta-blokkers'},
            'clopidogrel': {'name': 'Clopidogrel', 'category': 'Antiplaatjesmiddelen'},
            'ibuprofen': {'name': 'Ibuprofen', 'category': 'NSAIDs'},
            'omeprazol': {'name': 'Omeprazol', 'category': 'Protonpompremmers'},
            'aspirine': {'name': 'Aspirine', 'category': 'Antiplaatjesmiddelen'},
            'furosemide': {'name': 'Furosemide', 'category': 'Diuretica'},
            'amiodarone': {'name': 'Amiodarone', 'category': 'Anti-aritmica'},
            'verapamil': {'name': 'Verapamil', 'category': 'Calciumantagonisten'},
            'diltiazem': {'name': 'Diltiazem', 'category': 'Calciumantagonisten'},
            'paracetamol': {'name': 'Paracetamol', 'category': 'Analgetica'}
        }
        
        # Фильтруем по запросу
        results = []
        for drug_id, drug_info in drugs_db.items():
            if query in drug_id or query in drug_info['name'].lower():
                results.append({
                    'id': drug_id,
                    'name': drug_info['name'],
                    'category': drug_info['category']
                })
        
        return safe_jsonify({'drugs': results[:10]})  # Ограничиваем до 10 результатов
        
    except Exception as e:
        current_app.logger.error(f"Error in search_drugs: {e}")

# Удален старый роут learning-map - теперь используется новый в learning_routes_new.py

@learning_bp.route('/knowledge-base')
@login_required  
def knowledge_base():
    # Пока просто заглушка
    return render_template('learning/knowledge_base.html')

@learning_bp.route('/learning-cards/<path:path>')
@login_required
def learning_cards(path):
    """Отображение обучающих карточек по указанному пути"""
    try:
        # Проверяем существование файла карточек
        cards_file = f"cards/{path}/learning_cards.json"
        
        if not os.path.exists(cards_file):
            flash("Файл карточек не найден", "warning")
            return redirect(url_for('learning_bp.index'))
        
        # Загружаем карточки
        with open(cards_file, 'r', encoding='utf-8') as f:
            cards_data = json.load(f)
        
        return render_template('learning/learning_cards.html',
                             cards=cards_data.get('cards', []),
                             path=path,
                             title=cards_data.get('title', 'Обучающие карточки'))
                             
    except Exception as e:
        current_app.logger.error(f"Error loading learning cards: {e}")
        flash("Ошибка при загрузке карточек", "danger")
        return redirect(url_for('learning_bp.index'))

# Блокировка через CSS overlay - убрано для использования JavaScript overlay
