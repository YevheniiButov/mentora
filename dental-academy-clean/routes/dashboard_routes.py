# routes/dashboard_routes.py - Enhanced Learning Dashboard Routes

from flask import Blueprint, render_template, jsonify, request, redirect, url_for, flash, session, g
from flask_login import login_required, current_user
from models import (
    LearningPath, Subject, Module, Lesson, UserProgress, 
    Achievement, UserAchievement, UserActivity, UserStreak, UserReminder,
    PersonalLearningPlan, StudySession
)
from extensions import db
from datetime import datetime, date, timedelta, timezone
from sqlalchemy import func, desc
from utils.learning_plan_generator import create_learning_plan_from_diagnostic, update_user_learning_plan
from models import DiagnosticSession
from utils.adaptive_planner import adapt_user_learning_plan, get_plan_insights

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
@login_required
def index():
    """Enhanced main dashboard with gamification widgets"""
    
    # Проверка необходимости диагностики (временно отключено для предварительного запуска)
    # if current_user.requires_diagnostic:
    #     # Проверяем есть ли завершенная диагностика
    #     completed_diagnostic = DiagnosticSession.query.filter_by(
    #         user_id=current_user.id,
    #         status='completed'
    #     ).first()
    #     
    #     if not completed_diagnostic:
    #         flash('Для персонализации обучения необходимо пройти диагностический тест.', 'info')
    #         return redirect(url_for('diagnostic.choose_diagnostic_type'))
    
    # Get comprehensive dashboard stats
    dashboard_stats = current_user.get_dashboard_stats()
    
    # Get user's streak information
    streak = current_user.get_or_create_streak()
    
    # Get recent achievements
    recent_achievements = current_user.get_earned_achievements()[:3]
    
    # Get next recommended modules
    recommended_modules = current_user.get_next_recommended_modules(4)
    
    # Get upcoming reminders
    upcoming_reminders = current_user.get_upcoming_reminders(7)
    
    # Get recent activity
    recent_activity = current_user.get_recent_activity(5)
    
    # Get activity chart data for the last 7 days
    chart_data = current_user.get_activity_chart_data(7)
    
    # Calculate BIG exam preparation status
    big_exam_status = calculate_big_exam_status(current_user)
    
    # Get learning paths with progress
    learning_paths = get_learning_paths_with_progress(current_user)
    
    # Get today's goals/targets
    today_goals = get_daily_goals(current_user)
    
    # Get active learning plan
    active_plan = PersonalLearningPlan.query.filter_by(
        user_id=current_user.id,
        status='active'
    ).order_by(PersonalLearningPlan.last_updated.desc()).first()
    
    # Check if reassessment is needed
    reassessment_needed = False
    reassessment_required = False
    reassessment_url = None
    
    if active_plan and active_plan.next_diagnostic_date:
        today = date.today()
        days_until_reassessment = (active_plan.next_diagnostic_date - today).days
        
        if days_until_reassessment <= 0:
            # Переоценка просрочена
            flash(f'Необходимо пройти переоценку прогресса для продолжения эффективного обучения!', 'warning')
            # Добавляем в контекст для показа большого баннера
            reassessment_required = True
            reassessment_url = url_for('diagnostic_bp.start_reassessment', plan_id=active_plan.id)
        elif days_until_reassessment <= 3:
            # Скоро переоценка
            flash(f'Через {days_until_reassessment} дня запланирована переоценка прогресса', 'info')
    
    return render_template('dashboard/enhanced_index.html',
                         user=current_user,
                         stats=dashboard_stats,
                         streak=streak,
                         recent_achievements=recent_achievements,
                         recommended_modules=recommended_modules,
                         upcoming_reminders=upcoming_reminders,
                         recent_activity=recent_activity,
                         chart_data=chart_data,
                         big_exam_status=big_exam_status,
                         learning_paths=learning_paths,
                         today_goals=today_goals,
                         active_plan=active_plan,
                         reassessment_needed=reassessment_needed,
                         reassessment_required=reassessment_required,
                         reassessment_url=reassessment_url,
                         today=date.today())

@dashboard_bp.route('/achievements')
@login_required
def achievements():
    """Redirect to learning map with gamification tab"""
    lang = g.get('lang', 'en')
    # Редирект на карту обучения с параметром для открытия таба gamification
    return redirect(url_for('daily_learning.learning_map', lang=lang) + '?tab=games')

@dashboard_bp.route('/activity')
@login_required
def activity():
    """Redirect to learning map with progress tab"""
    lang = g.get('lang', 'en')
    # Редирект на карту обучения с параметром для открытия таба progress
    return redirect(url_for('daily_learning.learning_map', lang=lang) + '?tab=progress')

@dashboard_bp.route('/reminders')
@login_required
def reminders():
    """Reminders and deadlines management"""
    
    # Get reminders by category
    upcoming_reminders = current_user.get_upcoming_reminders(30)
    overdue_reminders = UserReminder.query.filter(
        UserReminder.user_id == current_user.id,
        UserReminder.is_active == True,
        UserReminder.is_completed == False,
        UserReminder.reminder_date < datetime.now()
    ).order_by(UserReminder.reminder_date.asc()).all()
    
    completed_reminders = UserReminder.query.filter(
        UserReminder.user_id == current_user.id,
        UserReminder.is_completed == True
    ).order_by(UserReminder.completed_at.desc()).limit(10).all()
    
    return render_template('dashboard/reminders.html',
                         upcoming_reminders=upcoming_reminders,
                         overdue_reminders=overdue_reminders,
                         completed_reminders=completed_reminders)

@dashboard_bp.route('/learning-plan/<int:plan_id>')
# @login_required  # Временно отключено для тестирования
def learning_plan(plan_id):
    """Display user's learning plan"""
    
    # Проверяем, авторизован ли пользователь
    if not current_user.is_authenticated:
        flash('Для просмотра плана обучения необходимо авторизоваться', 'warning')
        return redirect(url_for('auth.login'))
    
    # Get the learning plan
    plan = PersonalLearningPlan.query.filter_by(
        id=plan_id,
        user_id=current_user.id
    ).first()
    
    if not plan:
        # If specific plan not found, get the most recent active plan
        plan = PersonalLearningPlan.query.filter_by(
            user_id=current_user.id,
            status='active'
        ).order_by(PersonalLearningPlan.last_updated.desc()).first()
        
        if not plan:
            # Redirect to diagnostic if no plan exists
            return redirect(url_for('diagnostic.start_diagnostic'))
    
    # Get study sessions for this plan
    study_sessions = plan.study_sessions.order_by(StudySession.started_at.desc()).limit(10).all()
    
    # Calculate plan statistics
    total_sessions = plan.study_sessions.count()
    completed_sessions = plan.study_sessions.filter_by(status='completed').count()
    upcoming_sessions = plan.study_sessions.filter_by(status='planned').count()
    
    # Get domain analysis
    domain_analysis = plan.get_domain_analysis()
    weak_domains = plan.get_weak_domain_names()  # Используем полные названия
    strong_domains = plan.get_strong_domain_names()  # Используем полные названия
    
    # Get study schedule and milestones
    study_schedule = plan.get_study_schedule()
    milestones = plan.get_milestones()
    
    # Redirect to the enhanced learning planner
    return redirect(url_for("learning_planner.learning_planner", plan_id=plan_id))
    # Redirect to the enhanced learning planner
    return redirect(url_for("learning_planner.learning_planner", plan_id=plan_id))
    # Redirect to the enhanced learning planner
    return redirect(url_for("learning_planner.learning_planner", plan_id=plan_id))
    # Redirect to the enhanced learning planner
    return redirect(url_for("learning_planner.learning_planner", plan_id=plan_id))
    # Redirect to the enhanced learning planner
    return redirect(url_for("learning_planner.learning_planner", plan_id=plan_id))
    # Redirect to the enhanced learning planner
    return redirect(url_for("learning_planner.learning_planner", plan_id=plan_id))
    # Redirect to the enhanced learning planner
    return redirect(url_for("learning_planner.learning_planner", plan_id=plan_id))
    # Redirect to the enhanced learning planner
    return redirect(url_for("learning_planner.learning_planner", plan_id=plan_id))
    # Redirect to the enhanced learning planner
    return redirect(url_for("learning_planner.learning_planner", plan_id=plan_id))
    # Redirect to the enhanced learning planner
    return redirect(url_for("learning_planner.learning_planner", plan_id=plan_id))
    # Redirect to the enhanced learning planner
    return redirect(url_for("learning_planner.learning_planner", plan_id=plan_id))

@dashboard_bp.route('/learning-plan/<int:plan_id>/start-learning')
# @login_required  # Временно отключено для тестирования
def start_learning_plan(plan_id):
    """Start automated learning based on personal learning plan"""
    
    # Проверяем, авторизован ли пользователь
    if not current_user.is_authenticated:
        flash('Для начала обучения необходимо авторизоваться', 'warning')
        return redirect(url_for('auth.login'))
    
    # Get the learning plan
    plan = PersonalLearningPlan.query.get_or_404(plan_id)
    
    # Get study schedule
    study_schedule = plan.get_study_schedule()
    
    if not study_schedule or not study_schedule.get('weekly_schedule'):
        flash('План обучения не содержит расписания', 'warning')
        return redirect(url_for('dashboard.learning_plan', plan_id=plan_id))
    
    # Find the next session to start
    next_session = None
    current_week = None
    
    for week_data in study_schedule['weekly_schedule']:
        for session in week_data['daily_sessions']:
            # Check if this session is not completed
            # For now, we'll start with the first session
            next_session = session
            current_week = week_data
            break
        if next_session:
            break
    
    if not next_session:
        flash('Все сессии в плане завершены!', 'success')
        return redirect(url_for('dashboard.learning_plan', plan_id=plan_id))
    
    # Store learning plan session in Flask session
    session['learning_plan_id'] = plan_id
    session['current_week'] = current_week['week_number']
    session['current_session'] = next_session
    session['learning_mode'] = 'automated'
    
    # Отладка: выводим данные сессии
    print(f"🔧 DEBUG: Сохраняем в сессию: plan_id={plan_id}, week={current_week['week_number']}, session={next_session}")
    print(f"🔧 DEBUG: Текущая сессия: {session}")
    
    # Redirect to appropriate learning content based on session type
    if next_session['type'] == 'theory':
        # Redirect to theory lessons with parameters
        return redirect(url_for('learning.automated_theory', plan_id=plan_id, week=current_week['week_number']))
    elif next_session['type'] == 'practice':
        # Redirect to practice exercises with parameters
        return redirect(url_for('learning.automated_practice', plan_id=plan_id, week=current_week['week_number']))
    elif next_session['type'] == 'test':
        # Redirect to test with parameters
        return redirect(url_for('learning.automated_test', plan_id=plan_id, week=current_week['week_number']))
    elif next_session['type'] == 'review':
        # Redirect to review materials with parameters
        return redirect(url_for('learning.automated_review', plan_id=plan_id, week=current_week['week_number']))
    else:
        # Default to theory with parameters
        return redirect(url_for('learning.automated_theory', plan_id=plan_id, week=current_week['week_number']))

@dashboard_bp.route('/learning-plan/<int:plan_id>/progress')
# @login_required  # Временно отключено для тестирования
def learning_plan_progress(plan_id):
    """Get learning plan progress for AJAX updates"""
    
    plan = PersonalLearningPlan.query.get_or_404(plan_id)
    study_schedule = plan.get_study_schedule()
    
    if not study_schedule:
        return jsonify({'error': 'No schedule found'})
    
    # Calculate progress
    total_sessions = 0
    completed_sessions = 0
    
    for week_data in study_schedule['weekly_schedule']:
        for session in week_data['daily_sessions']:
            total_sessions += 1
            # Here you would check if session is completed
            # For now, we'll use a simple counter
    
    progress_percent = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0
    
    return jsonify({
        'plan_id': plan_id,
        'total_sessions': total_sessions,
        'completed_sessions': completed_sessions,
        'progress_percent': progress_percent,
        'current_ability': plan.current_ability,
        'target_ability': plan.target_ability,
        'estimated_readiness': plan.estimated_readiness
    })

@dashboard_bp.route('/api/dashboard-stats')
@login_required
def api_dashboard_stats():
    """API endpoint for dashboard statistics"""
    
    stats = current_user.get_dashboard_stats()
    chart_data = current_user.get_activity_chart_data(7)
    
    return jsonify({
        'stats': stats,
        'chart_data': chart_data,
        'streak': {
            'current': current_user.get_or_create_streak().current_streak,
            'longest': current_user.get_or_create_streak().longest_streak
        }
    })

@dashboard_bp.route('/api/update-reminder/<int:reminder_id>', methods=['POST'])
@login_required
def update_reminder(reminder_id):
    """Update reminder status"""
    
    reminder = UserReminder.query.filter_by(
        id=reminder_id,
        user_id=current_user.id
    ).first()
    
    if not reminder:
        return jsonify({'error': 'Reminder not found'}), 404
    
    data = request.get_json()
    
    if data.get('completed'):
        reminder.is_completed = True
        reminder.completed_at = datetime.now()
    
    db.session.commit()
    
    return jsonify({'success': True})

@dashboard_bp.route('/api/activity-log', methods=['POST'])
@login_required
def log_activity():
    """Log user activity (called from frontend)"""
    
    data = request.get_json()
    
    current_user.update_activity(
        lessons_completed=data.get('lessons_completed', 0),
        time_spent=data.get('time_spent', 0),
        xp_earned=data.get('xp_earned', 0),
        modules_accessed=data.get('modules_accessed', 0),
        tests_taken=data.get('tests_taken', 0),
        virtual_patients_completed=data.get('virtual_patients_completed', 0)
    )
    
    db.session.commit()
    
    # Check for new achievements
    new_achievements = current_user.check_achievements()
    
    return jsonify({
        'success': True,
        'new_achievements': [{'name': a.name, 'description': a.description} for a in new_achievements]
    })

@dashboard_bp.route('/test-session')
def test_session():
    """Тестовый маршрут для проверки сессии"""
    
    # Сохраняем тестовые данные в сессию
    session['test_data'] = {
        'plan_id': 1,
        'week': 1,
        'session_type': 'theory',
        'timestamp': datetime.now().isoformat()
    }
    
    print(f"🔧 DEBUG: Сохранены данные в сессию: {session['test_data']}")
    
    return jsonify({
        'message': 'Данные сохранены в сессию',
        'session_data': session.get('test_data'),
        'all_session': dict(session)
    })

@dashboard_bp.route('/check-session')
def check_session():
    """Проверка данных сессии"""
    
    test_data = session.get('test_data')
    
    return jsonify({
        'session_exists': test_data is not None,
        'session_data': test_data,
        'all_session': dict(session)
    })

@dashboard_bp.route('/learning-planner')
@login_required
def learning_planner_redirect():
    """Redirect to learning map with planner tab"""
    lang = g.get('lang', 'en')
    # Редирект на карту обучения с параметром для открытия таба planner
    return redirect(url_for('daily_learning.learning_map', lang=lang) + '?tab=planner')

@dashboard_bp.route('/create-learning-plan', methods=['GET', 'POST'])
@login_required
def create_learning_plan():
    """Создает современный план обучения на основе диагностики"""
    
    if request.method == 'POST':
        # Поддержка как JSON, так и form data
        if request.is_json:
            data = request.get_json() or {}
        else:
            data = request.form.to_dict()
        
        # Получаем параметры плана
        exam_date_str = data.get('exam_date')
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        intensity = data.get('intensity', 'moderate')
        study_time = data.get('study_time', 'afternoon')
        diagnostic_session_id = data.get('diagnostic_session_id')
        
        exam_date = None
        start_date = None
        end_date = None
        
        # Парсим даты
        if exam_date_str:
            try:
                exam_date = datetime.strptime(exam_date_str, '%Y-%m-%d')
                exam_date = exam_date.replace(tzinfo=timezone.utc)
            except ValueError:
                return jsonify({'success': False, 'message': 'Неверный формат даты экзамена'})
        
        if start_date_str:
            try:
                start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                start_date = start_date.replace(tzinfo=timezone.utc)
            except ValueError:
                return jsonify({'success': False, 'message': 'Неверный формат даты начала'})
        
        if end_date_str:
            try:
                end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                end_date = end_date.replace(tzinfo=timezone.utc)
            except ValueError:
                return jsonify({'success': False, 'message': 'Неверный формат даты окончания'})
        
        try:
            # Создаем план обучения с дополнительными параметрами
            plan = create_learning_plan_from_diagnostic(
                current_user.id, 
                exam_date,
                start_date=start_date,
                end_date=end_date,
                intensity=intensity,
                study_time=study_time,
                diagnostic_session_id=diagnostic_session_id
            )
            
            # Генерируем цели обучения
            goals = generate_learning_goals(plan, diagnostic_session_id)
            
            # Генерируем расписание занятий
            schedule = generate_study_schedule(plan, intensity, study_time)
            
            if request.is_json:
                return jsonify({
                    'success': True,
                    'plan_id': plan.id,
                    'redirect_url': url_for('dashboard.learning_plan', plan_id=plan.id),
                    'goals': goals,
                    'schedule': schedule
                })
            else:
                flash(f'План обучения успешно создан! ID: {plan.id}', 'success')
                return redirect(url_for('dashboard.learning_plan', plan_id=plan.id))
            
        except ValueError as e:
            error_msg = f'Ошибка: {str(e)}'
            if request.is_json:
                return jsonify({'success': False, 'message': error_msg})
            else:
                flash(error_msg, 'error')
                return redirect(url_for('dashboard.create_learning_plan'))
        except Exception as e:
            error_msg = f'Произошла ошибка при создании плана: {str(e)}'
            if request.is_json:
                return jsonify({'success': False, 'message': error_msg})
            else:
                flash(error_msg, 'error')
                return redirect(url_for('dashboard.create_learning_plan'))
    
    # GET запрос - показываем современный интерфейс
    # Проверяем, есть ли диагностическая сессия
    diagnostic_session = DiagnosticSession.query.filter_by(
        user_id=current_user.id,
        status='completed'
    ).order_by(DiagnosticSession.completed_at.desc()).first()
    
    if not diagnostic_session:
        flash('Для создания плана обучения необходимо сначала пройти диагностику', 'warning')
        return redirect(url_for('diagnostic.start_diagnostic'))
    
    # Получаем результаты диагностики
    diagnostic_results = diagnostic_session.generate_results()
    
    # Подготавливаем данные для нового интерфейса
    learning_plan_data = {
        'sessionId': diagnostic_session.id,
        'overallScore': int(diagnostic_results.get('readiness_percentage', 0)),
        'readinessLevel': 'ready' if diagnostic_results.get('readiness_percentage', 0) >= 80 else 'almost_ready' if diagnostic_results.get('readiness_percentage', 0) >= 60 else 'in_progress',
        'questionsAnswered': diagnostic_session.questions_answered,
        'correctAnswers': diagnostic_session.correct_answers,
        'completionDate': diagnostic_session.completed_at.isoformat() if diagnostic_session.completed_at else None
    }
    
    # Подготавливаем данные доменов
    domains = []
    domain_statistics = diagnostic_results.get('domain_statistics', {})
    
    for domain_code, domain_data in domain_statistics.items():
        if domain_data.get('has_data', False):
            # Получаем информацию о домене
            from models import BIGDomain
            domain_info = BIGDomain.query.filter_by(code=domain_code).first()
            domain_name = domain_info.name if domain_info else domain_code
            
            # Рассчитываем оценку домена
            domain_score = int(domain_data.get('accuracy_percentage', 0))
            
            # Определяем целевые показатели
            target_score = 90 if domain_score >= 80 else 85 if domain_score >= 70 else 80
            estimated_hours = max(24 - domain_score * 0.3, 8)  # Больше часов для слабых областей
            
            domains.append({
                'name': domain_name,
                'code': domain_code,
                'score': domain_score,
                'target': target_score,
                'hours': int(estimated_hours),
                'questionsAnswered': domain_data.get('questions_answered', 0),
                'correctAnswers': domain_data.get('correct_answers', 0)
            })
    
    learning_plan_data['domains'] = domains
    
    return render_template('dashboard/learning_planner_translated.html',
                         diagnostic_session=diagnostic_session,
                         learning_plan_data=learning_plan_data,
                         diagnostic_results=learning_plan_data,
                         lang=request.args.get('lang', 'ru'))

def generate_learning_goals(plan, diagnostic_session_id):
    """Генерирует цели обучения на основе плана"""
    goals = []
    
    # Получаем диагностическую сессию
    diagnostic_session = DiagnosticSession.query.get(diagnostic_session_id)
    if not diagnostic_session:
        return goals
    
    results = diagnostic_session.generate_results()
    domain_statistics = results.get('domain_statistics', {})
    
    # Сортируем домены по приоритету (слабые области в первую очередь)
    weak_domains = []
    for domain_code, domain_data in domain_statistics.items():
        if domain_data.get('has_data', False):
            score = domain_data.get('accuracy_percentage', 0)
            if score < 70:
                weak_domains.append({
                    'code': domain_code,
                    'name': domain_data.get('name', domain_code),
                    'score': score
                })
    
    # Сортируем по возрастанию оценки
    weak_domains.sort(key=lambda x: x['score'])
    
    # Создаем цели для слабых областей
    for i, domain in enumerate(weak_domains[:3]):
        weeks_needed = max(4 - i, 2)  # Больше времени для самых слабых областей
        target_score = min(domain['score'] + 15, 85)  # Реалистичная цель
        
        goals.append({
            'title': f'Улучшить знания в {domain["name"]}',
            'description': f'Повысить уровень с {domain["score"]}% до {target_score}% за {weeks_needed} недели',
            'deadline': f'{weeks_needed} недели',
            'progress': 0,
            'priority': 'high' if i == 0 else 'medium'
        })
    
    # Добавляем общую цель подготовки
    goals.append({
        'title': 'Подготовка к финальному тесту',
        'description': 'Пройти все практические модули и достичь общего уровня готовности 85%',
        'deadline': '12 недель',
        'progress': int(results.get('readiness_percentage', 0)),
        'priority': 'medium'
    })
    
    return goals

def generate_study_schedule(plan, intensity, study_time):
    """Генерирует расписание занятий"""
    schedule = []
    
    # Определяем часы в день в зависимости от интенсивности
    hours_per_day = {
        'light': 1.5,
        'moderate': 2.5,
        'intensive': 4
    }.get(intensity, 2.5)
    
    # Определяем временные слоты
    time_slots = {
        'morning': '08:00-12:00',
        'afternoon': '12:00-18:00',
        'evening': '18:00-22:00',
        'flexible': 'Гибкое время'
    }.get(study_time, '12:00-18:00')
    
    # Генерируем расписание на неделю
    weekdays = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница']
    
    for i, day in enumerate(weekdays):
        schedule.append({
            'day': day,
            'time': time_slots,
            'duration': f'{hours_per_day}ч',
            'type': 'study'
        })
    
    return schedule

@dashboard_bp.route('/update-learning-plan/<int:plan_id>')
@login_required
def update_learning_plan(plan_id):
    """Обновляет план обучения"""
    
    plan = PersonalLearningPlan.query.get_or_404(plan_id)
    
    # Проверяем права доступа
    if plan.user_id != current_user.id:
        flash('У вас нет прав для обновления этого плана', 'error')
        return redirect(url_for('dashboard.index'))
    
    try:
        # Обновляем план
        updated_plan = update_user_learning_plan(current_user.id)
        
        if updated_plan:
            flash('План обучения обновлен!', 'success')
        else:
            flash('Не удалось обновить план обучения', 'warning')
            
    except Exception as e:
        flash(f'Ошибка при обновлении плана: {str(e)}', 'error')
    
    return redirect(url_for('dashboard.learning_plan', plan_id=plan_id))

@dashboard_bp.route('/plan/<int:plan_id>/adapt', methods=['GET', 'POST'])
@login_required
def adapt_plan(plan_id):
    """Адаптирует план обучения на основе прогресса"""
    
    if request.method == 'GET':
        """Показывает страницу адаптации плана"""
        try:
            # Получаем текущий план
            plan = PersonalLearningPlan.query.get_or_404(plan_id)
            
            # Получаем аналитику
            insights = get_plan_insights(current_user.id, plan_id)
            
            return render_template('dashboard/plan_adapt.html',
                                 plan=plan,
                                 insights=insights,
                                 plan_id=plan_id)
        
        except Exception as e:
            flash(f'Ошибка при загрузке страницы адаптации: {str(e)}', 'error')
            return redirect(url_for('dashboard.learning_plan', plan_id=plan_id))
    
    else:  # POST
        """Адаптирует план обучения"""
        try:
            # Адаптируем план
            result = adapt_user_learning_plan(current_user.id, plan_id)
            
            return jsonify({
                'success': True,
                'message': 'План успешно адаптирован',
                'adjustments': result['adjustments_made'],
                'recommendations': result['recommendations'],
                'new_readiness': result['updated_readiness']
            })
        
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Ошибка при адаптации плана: {str(e)}'
            }), 500

@dashboard_bp.route('/plan/<int:plan_id>/insights')
@login_required
def plan_insights(plan_id):
    """Показывает аналитику по плану обучения"""
    
    try:
        insights = get_plan_insights(current_user.id, plan_id)
        
        return render_template('dashboard/plan_insights.html',
                             insights=insights,
                             plan_id=plan_id)
    
    except Exception as e:
        flash(f'Ошибка при загрузке аналитики: {str(e)}', 'error')
        return redirect(url_for('dashboard.learning_plan', plan_id=plan_id))

# Helper functions
def calculate_big_exam_status(user):
    """Calculate BIG exam preparation status"""
    
    # Get BIG-related learning paths
    big_paths = LearningPath.query.filter(
        LearningPath.name.contains('BIG'),
        LearningPath.is_active == True
    ).all()
    
    total_progress = 0
    total_paths = len(big_paths)
    
    for path in big_paths:
        path_progress = 0
        total_subjects = path.subjects.count()
        
        for subject in path.subjects:
            subject_progress = subject.get_progress_for_user(user.id)
            path_progress += subject_progress['progress_percent']
        
        if total_subjects > 0:
            total_progress += path_progress / total_subjects
    
    overall_progress = total_progress / total_paths if total_paths > 0 else 0
    
    # Determine readiness level
    if overall_progress >= 80:
        readiness = 'ready'
    elif overall_progress >= 60:
        readiness = 'almost_ready'
    elif overall_progress >= 40:
        readiness = 'in_progress'
    else:
        readiness = 'getting_started'
    
    return {
        'progress': int(overall_progress),
        'readiness': readiness,
        'paths_count': total_paths,
        'exam_date': user.exam_dates[0].exam_date if user.exam_dates else None
    }

def get_learning_paths_with_progress(user):
    """Get learning paths with detailed progress"""
    
    paths = []
    for path in LearningPath.query.filter_by(is_active=True).all():
        total_lessons = 0
        completed_lessons = 0
        
        # Get subjects for this learning path
        subjects = Subject.query.filter_by(learning_path_id=path.id).all()
        subjects_count = len(subjects)
        
        for subject in subjects:
            subject_progress = subject.get_progress_for_user(user.id)
            total_lessons += subject_progress['total_lessons']
            completed_lessons += subject_progress['completed_lessons']
        
        progress_percent = int((completed_lessons / total_lessons * 100)) if total_lessons > 0 else 0
        
        paths.append({
            'id': path.id,
            'name': path.name,
            'description': path.description,
            'icon': getattr(path, 'icon', 'folder'),
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'progress_percent': progress_percent,
            'subjects_count': subjects_count
        })
    
    return paths

def get_daily_goals(user):
    """Get user's daily learning goals"""
    
    # Default daily goals
    daily_goals = {
        'lessons_target': 3,
        'time_target': 30,  # minutes
        'xp_target': 100
    }
    
    # Get today's progress
    today_activity = UserActivity.query.filter_by(
        user_id=user.id,
        activity_date=date.today()
    ).first()
    
    if today_activity:
        daily_goals.update({
            'lessons_completed': today_activity.lessons_completed,
            'time_spent': today_activity.time_spent,
            'xp_earned': today_activity.xp_earned
        })
    else:
        daily_goals.update({
            'lessons_completed': 0,
            'time_spent': 0,
            'xp_earned': 0
        })
    
    # Calculate completion percentages
    daily_goals['lessons_progress'] = min(100, (daily_goals['lessons_completed'] / daily_goals['lessons_target']) * 100)
    daily_goals['time_progress'] = min(100, (daily_goals['time_spent'] / daily_goals['time_target']) * 100)
    daily_goals['xp_progress'] = min(100, (daily_goals['xp_earned'] / daily_goals['xp_target']) * 100)
    
    return daily_goals

def calculate_achievement_progress(user, achievement):
    """Calculate user's progress towards an achievement"""
    
    stats = user.get_progress_stats()
    streak = user.get_or_create_streak()
    
    if achievement.requirement_type == 'lessons_completed':
        current_value = stats['completed_lessons']
    elif achievement.requirement_type == 'hours_studied':
        current_value = stats['total_time_spent'] / 60
    elif achievement.requirement_type == 'streak_days':
        current_value = streak.current_streak
    elif achievement.requirement_type == 'longest_streak':
        current_value = streak.longest_streak
    elif achievement.requirement_type == 'xp_earned':
        current_value = user.xp
    elif achievement.requirement_type == 'level_reached':
        current_value = user.level
    else:
        current_value = 0
    
    progress = min(100, (current_value / achievement.requirement_value) * 100)
    
    return {
        'current_value': current_value,
        'target_value': achievement.requirement_value,
        'progress_percent': int(progress)
    }

def calculate_activity_stats(user):
    """Calculate comprehensive activity statistics"""
    
    from datetime import datetime, timedelta
    
    # Get activity for different periods
    today = date.today()
    week_start = today - timedelta(days=7)
    month_start = today - timedelta(days=30)
    
    # Query activity stats
    week_stats = db.session.query(
        func.sum(UserActivity.lessons_completed),
        func.sum(UserActivity.time_spent),
        func.sum(UserActivity.xp_earned),
        func.count(UserActivity.id)
    ).filter(
        UserActivity.user_id == user.id,
        UserActivity.activity_date >= week_start
    ).first()
    
    month_stats = db.session.query(
        func.sum(UserActivity.lessons_completed),
        func.sum(UserActivity.time_spent),
        func.sum(UserActivity.xp_earned),
        func.count(UserActivity.id)
    ).filter(
        UserActivity.user_id == user.id,
        UserActivity.activity_date >= month_start
    ).first()
    
    # Get most active day
    most_active_day = db.session.query(
        UserActivity.activity_date,
        func.sum(UserActivity.lessons_completed + UserActivity.time_spent + UserActivity.xp_earned).label('total_activity')
    ).filter(
        UserActivity.user_id == user.id
    ).group_by(UserActivity.activity_date).order_by(desc('total_activity')).first()
    
    return {
        'week': {
            'lessons': week_stats[0] or 0,
            'time': week_stats[1] or 0,
            'xp': week_stats[2] or 0,
            'active_days': week_stats[3] or 0
        },
        'month': {
            'lessons': month_stats[0] or 0,
            'time': month_stats[1] or 0,
            'xp': month_stats[2] or 0,
            'active_days': month_stats[3] or 0
        },
        'most_active_day': most_active_day.activity_date if most_active_day else None
    } 
def get_daily_goals(user):
    """Get user's daily learning goals"""
    
    # Default daily goals
    daily_goals = {
        'lessons_target': 3,
        'time_target': 30,  # minutes
        'xp_target': 100
    }
    
    # Get today's progress
    today_activity = UserActivity.query.filter_by(
        user_id=user.id,
        activity_date=date.today()
    ).first()
    
    if today_activity:
        daily_goals.update({
            'lessons_completed': today_activity.lessons_completed,
            'time_spent': today_activity.time_spent,
            'xp_earned': today_activity.xp_earned
        })
    else:
        daily_goals.update({
            'lessons_completed': 0,
            'time_spent': 0,
            'xp_earned': 0
        })
    
    # Calculate completion percentages
    daily_goals['lessons_progress'] = min(100, (daily_goals['lessons_completed'] / daily_goals['lessons_target']) * 100)
    daily_goals['time_progress'] = min(100, (daily_goals['time_spent'] / daily_goals['time_target']) * 100)
    daily_goals['xp_progress'] = min(100, (daily_goals['xp_earned'] / daily_goals['xp_target']) * 100)
    
    return daily_goals

def calculate_achievement_progress(user, achievement):
    """Calculate user's progress towards an achievement"""
    
    stats = user.get_progress_stats()
    streak = user.get_or_create_streak()
    
    if achievement.requirement_type == 'lessons_completed':
        current_value = stats['completed_lessons']
    elif achievement.requirement_type == 'hours_studied':
        current_value = stats['total_time_spent'] / 60
    elif achievement.requirement_type == 'streak_days':
        current_value = streak.current_streak
    elif achievement.requirement_type == 'longest_streak':
        current_value = streak.longest_streak
    elif achievement.requirement_type == 'xp_earned':
        current_value = user.xp
    elif achievement.requirement_type == 'level_reached':
        current_value = user.level
    else:
        current_value = 0
    
    progress = min(100, (current_value / achievement.requirement_value) * 100)
    
    return {
        'current_value': current_value,
        'target_value': achievement.requirement_value,
        'progress_percent': int(progress)
    }

def calculate_activity_stats(user):
    """Calculate comprehensive activity statistics"""
    
    from datetime import datetime, timedelta
    
    # Get activity for different periods
    today = date.today()
    week_start = today - timedelta(days=7)
    month_start = today - timedelta(days=30)
    
    # Query activity stats
    week_stats = db.session.query(
        func.sum(UserActivity.lessons_completed),
        func.sum(UserActivity.time_spent),
        func.sum(UserActivity.xp_earned),
        func.count(UserActivity.id)
    ).filter(
        UserActivity.user_id == user.id,
        UserActivity.activity_date >= week_start
    ).first()
    
    month_stats = db.session.query(
        func.sum(UserActivity.lessons_completed),
        func.sum(UserActivity.time_spent),
        func.sum(UserActivity.xp_earned),
        func.count(UserActivity.id)
    ).filter(
        UserActivity.user_id == user.id,
        UserActivity.activity_date >= month_start
    ).first()
    
    # Get most active day
    most_active_day = db.session.query(
        UserActivity.activity_date,
        func.sum(UserActivity.lessons_completed + UserActivity.time_spent + UserActivity.xp_earned).label('total_activity')
    ).filter(
        UserActivity.user_id == user.id
    ).group_by(UserActivity.activity_date).order_by(desc('total_activity')).first()
    
    return {
        'week': {
            'lessons': week_stats[0] or 0,
            'time': week_stats[1] or 0,
            'xp': week_stats[2] or 0,
            'active_days': week_stats[3] or 0
        },
        'month': {
            'lessons': month_stats[0] or 0,
            'time': month_stats[1] or 0,
            'xp': month_stats[2] or 0,
            'active_days': month_stats[3] or 0
        },
        'most_active_day': most_active_day.activity_date if most_active_day else None
    } 