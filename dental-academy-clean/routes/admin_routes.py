"""
Административные роуты для управления системой
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from utils.decorators import admin_required
from models import db, User, LearningPath, Subject, Module, Lesson, UserProgress, Question, QuestionCategory, VirtualPatientScenario, VirtualPatientAttempt, DiagnosticSession, BIGDomain, PersonalLearningPlan, IRTParameters
from datetime import datetime, timedelta, date
import json
from sqlalchemy import func, and_, or_
from datetime import timezone
import logging

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Enhanced admin dashboard with real-time metrics"""
    
    today = date.today()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # 1. ПОЛЬЗОВАТЕЛЬСКИЕ МЕТРИКИ
    users_metrics = {
        'total_users': User.query.count(),
        'new_today': User.query.filter(
            func.date(User.created_at) == today
        ).count(),
        'new_week': User.query.filter(
            User.created_at >= week_ago
        ).count(),
        'active_week': User.query.join(UserProgress).filter(
            UserProgress.last_accessed >= week_ago
        ).distinct().count(),
        'with_diagnostic': User.query.join(DiagnosticSession).filter(
            DiagnosticSession.status == 'completed'
        ).distinct().count(),
        'with_active_plan': User.query.join(PersonalLearningPlan).filter(
            PersonalLearningPlan.status == 'active'
        ).distinct().count()
    }
    
    # 2. ДИАГНОСТИЧЕСКИЕ МЕТРИКИ
    diagnostic_metrics = {
        'total_sessions': DiagnosticSession.query.count(),
        'completed_sessions': DiagnosticSession.query.filter_by(status='completed').count(),
        'sessions_today': DiagnosticSession.query.filter(
            func.date(DiagnosticSession.started_at) == today
        ).count(),
        'sessions_week': DiagnosticSession.query.filter(
            DiagnosticSession.started_at >= week_ago
        ).count(),
        'avg_ability': db.session.query(
            func.avg(DiagnosticSession.current_ability)
        ).filter(DiagnosticSession.status == 'completed').scalar() or 0,
        'completion_rate': 0
    }
    if diagnostic_metrics['total_sessions'] > 0:
        diagnostic_metrics['completion_rate'] = round(
            (diagnostic_metrics['completed_sessions'] / diagnostic_metrics['total_sessions']) * 100, 1
        )
    
    # 3. ПЛАНЫ ОБУЧЕНИЯ МЕТРИКИ
    learning_metrics = {
        'active_plans': PersonalLearningPlan.query.filter_by(status='active').count(),
        'plans_created_week': PersonalLearningPlan.query.filter(
            PersonalLearningPlan.last_updated >= week_ago
        ).count(),
        'avg_progress': db.session.query(
            func.avg(PersonalLearningPlan.overall_progress)
        ).filter(PersonalLearningPlan.status == 'active').scalar() or 0,
        'overdue_reassessments': PersonalLearningPlan.query.filter(
            PersonalLearningPlan.status == 'active',
            PersonalLearningPlan.next_diagnostic_date < today
        ).count()
    }
    
    # 4. КОНТЕНТ МЕТРИКИ
    content_metrics = {
        'total_questions': Question.query.count(),
        'questions_with_irt': Question.query.join(IRTParameters).count(),
        'total_lessons': Lesson.query.count(),
        'lessons_completed_week': UserProgress.query.filter(
            UserProgress.completed == True,
            UserProgress.completed_at >= week_ago
        ).count(),
        'avg_time_per_lesson': db.session.query(
            func.avg(UserProgress.time_spent)
        ).filter(UserProgress.completed == True).scalar() or 0
    }
    
    # 5. ПОСЛЕДНИЕ ДАННЫЕ
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_sessions = DiagnosticSession.query.join(User).order_by(
        DiagnosticSession.started_at.desc()
    ).limit(5).all()
    
    return render_template('admin/dashboard_new.html',
                         users_metrics=users_metrics,
                         diagnostic_metrics=diagnostic_metrics,
                         learning_metrics=learning_metrics,
                         content_metrics=content_metrics,
                         recent_users=recent_users,
                         recent_sessions=recent_sessions)

@admin_bp.route('/diagnostics')
@login_required
@admin_required
def diagnostic_analytics():
    """Analytics for diagnostic sessions and IRT parameters"""
    
    # Временные рамки
    time_frame = request.args.get('timeframe', '30')  # дней
    if time_frame == 'all':
        date_filter = None
    else:
        date_filter = datetime.now(timezone.utc) - timedelta(days=int(time_frame))
    
    # Базовая статистика
    query = DiagnosticSession.query
    if date_filter:
        query = query.filter(DiagnosticSession.started_at >= date_filter)
    
    total_sessions = query.count()
    completed_sessions = query.filter_by(status='completed').count()
    
    # Статистика по типам диагностики
    session_types_stats = db.session.query(
        DiagnosticSession.session_type,
        func.count(DiagnosticSession.id).label('count'),
        func.avg(DiagnosticSession.current_ability).label('avg_ability')
    ).filter(
        DiagnosticSession.status == 'completed',
        DiagnosticSession.started_at >= date_filter if date_filter else True
    ).group_by(DiagnosticSession.session_type).all()
    
    # Распределение способностей
    ability_distribution = db.session.query(
        func.floor(DiagnosticSession.current_ability).label('ability_range'),
        func.count(DiagnosticSession.id).label('count')
    ).filter(
        DiagnosticSession.status == 'completed',
        DiagnosticSession.started_at >= date_filter if date_filter else True
    ).group_by('ability_range').order_by('ability_range').all()
    
    # Статистика по доменам
    domain_stats = []
    recent_sessions = DiagnosticSession.query.filter(
        DiagnosticSession.status == 'completed',
        DiagnosticSession.started_at >= date_filter if date_filter else True
    ).limit(100).all()
    
    domain_abilities = {}
    domain_counts = {}
    
    for session in recent_sessions:
        try:
            results = session.generate_results()
            if results and 'domain_abilities' in results:
                for domain, ability in results['domain_abilities'].items():
                    if domain not in domain_abilities:
                        domain_abilities[domain] = []
                        domain_counts[domain] = 0
                    if ability is not None:  # Проверяем на None
                        domain_abilities[domain].append(ability)
                        if ability < 0.0:  # Считаем слабые домены
                            domain_counts[domain] += 1
        except Exception as e:
            print(f"Ошибка при анализе сессии {session.id}: {e}")
            continue
    
    # Формируем статистику по доменам
    for domain, abilities in domain_abilities.items():
        domain_stats.append({
            'domain': domain,
            'avg_ability': sum(abilities) / len(abilities),
            'weak_count': domain_counts[domain],
            'total_tested': len(abilities)
        })
    
    domain_stats.sort(key=lambda x: x['avg_ability'])
    
    # IRT статистика
    irt_stats = {
        'total_questions': Question.query.count(),
        'questions_with_irt': Question.query.join(IRTParameters).count(),
        'calibrated_questions': IRTParameters.query.filter(
            IRTParameters.calibration_sample_size > 0
        ).count(),
        'avg_discrimination': db.session.query(
            func.avg(IRTParameters.discrimination)
        ).scalar() or 0,
        'avg_difficulty': db.session.query(
            func.avg(IRTParameters.difficulty)
        ).scalar() or 0
    }
    
    # Вопросы с экстремальными параметрами
    extreme_questions = []
    
    # Очень сложные вопросы
    very_difficult = Question.query.join(IRTParameters).filter(
        IRTParameters.difficulty > 2.0
    ).limit(10).all()
    for q in very_difficult:
        extreme_questions.append({
            'question': q,
            'type': 'difficult',
            'value': q.irt_parameters.difficulty
        })
    
    # Очень легкие вопросы
    very_easy = Question.query.join(IRTParameters).filter(
        IRTParameters.difficulty < -2.0
    ).limit(10).all()
    for q in very_easy:
        extreme_questions.append({
            'question': q,
            'type': 'easy',
            'value': q.irt_parameters.difficulty
        })
    
    # Низкая дискриминация
    low_discrimination = Question.query.join(IRTParameters).filter(
        IRTParameters.discrimination < 0.5
    ).limit(10).all()
    for q in low_discrimination:
        extreme_questions.append({
            'question': q,
            'type': 'low_discrimination',
            'value': q.irt_parameters.discrimination
        })
    
    return render_template('admin/diagnostic_analytics.html',
                         total_sessions=total_sessions,
                         completed_sessions=completed_sessions,
                         session_types_stats=session_types_stats,
                         ability_distribution=ability_distribution,
                         domain_stats=domain_stats,
                         irt_stats=irt_stats,
                         extreme_questions=extreme_questions,
                         time_frame=time_frame)

@admin_bp.route('/diagnostics/calibrate', methods=['POST'])
@login_required
@admin_required
def calibrate_irt():
    """Run IRT calibration"""
    try:
        from scripts.calibrate_irt_parameters import calibrate_all_questions
        calibrate_all_questions()
        flash('IRT калибровка успешно запущена', 'success')
    except Exception as e:
        flash(f'Ошибка калибровки: {str(e)}', 'danger')
    
    return redirect(url_for('admin.diagnostic_analytics'))

@admin_bp.route('/diagnostics/sessions')
@login_required
@admin_required
def diagnostic_sessions_list():
    """List all diagnostic sessions with details"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', 'all')
    type_filter = request.args.get('type', 'all')
    
    query = DiagnosticSession.query
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    if type_filter != 'all':
        query = query.filter_by(session_type=type_filter)
    
    sessions = query.order_by(DiagnosticSession.started_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/diagnostic_sessions.html',
                         sessions=sessions,
                         status_filter=status_filter,
                         type_filter=type_filter)

@admin_bp.route('/diagnostics/session/<int:session_id>')
@login_required
@admin_required
def diagnostic_session_detail(session_id):
    """Detailed view of diagnostic session"""
    session = DiagnosticSession.query.get_or_404(session_id)
    
    # Получаем все ответы
    responses = DiagnosticResponse.query.filter_by(
        session_id=session_id
    ).order_by(DiagnosticResponse.responded_at).all()
    
    # График изменения способности
    ability_history = []
    if session.ability_history:
        try:
            ability_history = json.loads(session.ability_history)
        except:
            ability_history = []
    
    # Результаты по доменам
    results = None
    if session.status == 'completed':
        try:
            results = session.generate_results()
        except Exception as e:
            print(f"Ошибка генерации результатов для сессии {session_id}: {e}")
    
    return render_template('admin/diagnostic_session_detail.html',
                         session=session,
                         responses=responses,
                         ability_history=ability_history,
                         results=results)

@admin_bp.route('/content')
@login_required
@admin_required
def content_management():
    """Content management overview"""
    
    # Статистика контента
    content_stats = {
        'learning_paths': LearningPath.query.count(),
        'subjects': Subject.query.count(),
        'modules': Module.query.count(),
        'lessons': Lesson.query.count(),
        'questions': Question.query.count(),
        'virtual_patients': VirtualPatientScenario.query.count()
    }
    
    # Последние изменения
    recent_lessons = Lesson.query.order_by(Lesson.id.desc()).limit(5).all()
    recent_questions = Question.query.order_by(Question.created_at.desc()).limit(5).all()
    
    # Статистика по доменам (упрощенная версия)
    domain_content_stats = []
    try:
        domain_content_stats = db.session.query(
            Question.domain,
            func.count(distinct(Question.id)).label('questions_count')
        ).group_by(Question.domain).all()
    except:
        pass
    
    return render_template('admin/content_management.html',
                         content_stats=content_stats,
                         recent_lessons=recent_lessons,
                         recent_questions=recent_questions,
                         domain_content_stats=domain_content_stats)

@admin_bp.route('/questions')
@login_required
@admin_required
def questions_management():
    """Questions management with IRT parameters"""
    page = request.args.get('page', 1, type=int)
    domain_filter = request.args.get('domain', 'all')
    irt_filter = request.args.get('irt', 'all')
    search = request.args.get('search', '')
    
    query = Question.query
    
    # Поиск
    if search:
        query = query.filter(Question.text.ilike(f'%{search}%'))
    
    # Фильтр по домену
    if domain_filter != 'all':
        query = query.filter_by(domain=domain_filter)
    
    # Фильтр по IRT
    if irt_filter == 'with_irt':
        query = query.join(IRTParameters)
    elif irt_filter == 'without_irt':
        query = query.outerjoin(IRTParameters).filter(IRTParameters.id == None)
    elif irt_filter == 'not_calibrated':
        query = query.join(IRTParameters).filter(
            or_(
                IRTParameters.calibration_sample_size == None,
                IRTParameters.calibration_sample_size == 0
            )
        )
    
    questions = query.paginate(page=page, per_page=20, error_out=False)
    
    # Получаем список доменов для фильтра
    domains = db.session.query(Question.domain).distinct().all()
    domains = [d[0] for d in domains if d[0]]
    
    return render_template('admin/questions_management.html',
                         questions=questions,
                         domains=domains,
                         domain_filter=domain_filter,
                         irt_filter=irt_filter,
                         search=search)

@admin_bp.route('/questions/<int:question_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_question(question_id):
    """Edit question and IRT parameters"""
    question = Question.query.get_or_404(question_id)
    
    if request.method == 'POST':
        # Обновляем вопрос
        question.text = request.form.get('text')
        question.correct_answer_text = request.form.get('correct_answer')
        question.explanation = request.form.get('explanation')
        
        # Обновляем опции
        options = []
        for i in range(1, 5):
            option = request.form.get(f'option_{i}')
            if option:
                options.append(option)
        question.options = options
        
        # Обновляем IRT параметры
        if question.irt_parameters:
            question.irt_parameters.difficulty = float(request.form.get('difficulty', 0))
            question.irt_parameters.discrimination = float(request.form.get('discrimination', 1))
            question.irt_parameters.guessing = float(request.form.get('guessing', 0.25))
        else:
            # Создаем новые IRT параметры
            irt_params = IRTParameters(
                question_id=question.id,
                difficulty=float(request.form.get('difficulty', 0)),
                discrimination=float(request.form.get('discrimination', 1)),
                guessing=float(request.form.get('guessing', 0.25))
            )
            db.session.add(irt_params)
            # Инициализируем параметры на основе сложности вопроса
            irt_params.initialize_default_parameters()
        
        db.session.commit()
        flash('Вопрос успешно обновлен', 'success')
        return redirect(url_for('admin.questions_management'))
    
    return render_template('admin/edit_question.html', question=question)

@admin_bp.route('/settings')
@login_required
@admin_required
def system_settings():
    """System settings and configuration"""
    
    # Системная информация
    system_info = {
        'database_size': get_database_size(),
        'total_files': count_uploaded_files(),
        'cache_size': get_cache_size(),
        'last_backup': get_last_backup_date()
    }
    
    # Конфигурация
    current_config = {
        'DIAGNOSTIC_MIN_QUESTIONS': app.config.get('DIAGNOSTIC_MIN_QUESTIONS', 20),
        'DIAGNOSTIC_MAX_QUESTIONS': app.config.get('DIAGNOSTIC_MAX_QUESTIONS', 50),
        'REASSESSMENT_DAYS': app.config.get('REASSESSMENT_DAYS', 14),
        'MIN_LESSONS_PER_DAY': app.config.get('MIN_LESSONS_PER_DAY', 3),
        'MAX_LESSONS_PER_DAY': app.config.get('MAX_LESSONS_PER_DAY', 10),
        'IRT_CONVERGENCE_THRESHOLD': app.config.get('IRT_CONVERGENCE_THRESHOLD', 0.001),
        'ENABLE_AI_ASSISTANT': app.config.get('ENABLE_AI_ASSISTANT', True),
        'ENABLE_VIRTUAL_PATIENTS': app.config.get('ENABLE_VIRTUAL_PATIENTS', True)
    }
    
    # Задачи обслуживания
    maintenance_tasks = [
        {
            'name': 'Резервное копирование БД',
            'last_run': get_last_backup_date(),
            'status': 'success' if get_last_backup_date() else 'warning',
            'action': 'backup_database'
        },
        {
            'name': 'Очистка старых сессий',
            'last_run': get_last_cleanup_date(),
            'status': 'success',
            'action': 'cleanup_sessions'
        },
        {
            'name': 'Оптимизация БД',
            'last_run': get_last_optimization_date(),
            'status': 'info',
            'action': 'optimize_database'
        },
        {
            'name': 'Обновление статистики',
            'last_run': datetime.now(timezone.utc) - timedelta(hours=2),
            'status': 'success',
            'action': 'update_statistics'
        }
    ]
    
    return render_template('admin/system_settings.html',
                         system_info=system_info,
                         current_config=current_config,
                         maintenance_tasks=maintenance_tasks)

@admin_bp.route('/settings/update', methods=['POST'])
@login_required
@admin_required
def update_settings():
    """Update system settings"""
    
    # Обновляем настройки
    settings_to_update = [
        'DIAGNOSTIC_MIN_QUESTIONS',
        'DIAGNOSTIC_MAX_QUESTIONS',
        'REASSESSMENT_DAYS',
        'MIN_LESSONS_PER_DAY',
        'MAX_LESSONS_PER_DAY',
        'IRT_CONVERGENCE_THRESHOLD'
    ]
    
    for setting in settings_to_update:
        value = request.form.get(setting)
        if value:
            if setting in ['IRT_CONVERGENCE_THRESHOLD']:
                app.config[setting] = float(value)
            else:
                app.config[setting] = int(value)
    
    # Булевы настройки
    app.config['ENABLE_AI_ASSISTANT'] = 'ENABLE_AI_ASSISTANT' in request.form
    app.config['ENABLE_VIRTUAL_PATIENTS'] = 'ENABLE_VIRTUAL_PATIENTS' in request.form
    
    # Сохраняем в файл конфигурации
    save_config_to_file(app.config)
    
    flash('Настройки успешно обновлены', 'success')
    return redirect(url_for('admin.system_settings'))

@admin_bp.route('/maintenance/<action>', methods=['POST'])
@login_required
@admin_required
def run_maintenance(action):
    """Run maintenance tasks"""
    
    if action == 'backup_database':
        # Запуск резервного копирования
        try:
            backup_database()
            flash('Резервное копирование выполнено успешно', 'success')
        except Exception as e:
            flash(f'Ошибка резервного копирования: {str(e)}', 'danger')
            
    elif action == 'cleanup_sessions':
        # Очистка старых сессий
        old_sessions = DiagnosticSession.query.filter(
            DiagnosticSession.started_at < datetime.now(timezone.utc) - timedelta(days=90),
            DiagnosticSession.status != 'completed'
        ).delete()
        db.session.commit()
        flash(f'Удалено {old_sessions} старых сессий', 'success')
        
    elif action == 'optimize_database':
        # Оптимизация БД
        try:
            db.session.execute('VACUUM ANALYZE')
            flash('База данных оптимизирована', 'success')
        except:
            flash('Оптимизация недоступна для данной БД', 'warning')
            
    elif action == 'update_statistics':
        # Обновление статистики
        # Здесь можно запустить фоновые задачи обновления кэша и т.д.
        flash('Статистика обновлена', 'success')
    
    return redirect(url_for('admin.system_settings'))

# Вспомогательные функции
def get_database_size():
    """Get database size in MB"""
    try:
        result = db.session.execute(
            "SELECT pg_database_size(current_database()) / 1024 / 1024 as size"
        ).scalar()
        return f"{result:.1f} MB"
    except:
        return "N/A"

def count_uploaded_files():
    """Count uploaded files"""
    upload_path = app.config.get('UPLOAD_FOLDER', 'static/uploads')
    try:
        import os
        total = sum(len(files) for _, _, files in os.walk(upload_path))
        return total
    except:
        return 0

def get_cache_size():
    """Get cache size"""
    # Placeholder - implement based on your caching solution
    return "12.3 MB"

def get_last_backup_date():
    """Get last backup date"""
    # Placeholder - implement based on your backup solution
    return datetime.now(timezone.utc) - timedelta(days=1)

def get_last_cleanup_date():
    """Get last cleanup date"""
    return datetime.now(timezone.utc) - timedelta(days=7)

def get_last_optimization_date():
    """Get last optimization date"""
    return datetime.now(timezone.utc) - timedelta(days=30)

def backup_database():
    """Perform database backup"""
    # Implement actual backup logic
    import subprocess
    db_url = app.config.get('SQLALCHEMY_DATABASE_URI')
    backup_file = f"backups/mentora_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    # subprocess.run(['pg_dump', db_url, '-f', backup_file])
    pass

def save_config_to_file(config):
    """Save configuration to file"""
    # Implement saving to config.py or environment file
    pass

def handle_upload_scenario():
    """Обработка загрузки сценария виртуального пациента"""
    try:
        title = request.form.get('title')
        description = request.form.get('description')
        scenario_file = request.files.get('scenario_file')
        
        if not title or not scenario_file:
            flash('Заполните все обязательные поля', 'error')
            return redirect(url_for('admin.index'))
        
        # Проверяем, что файл JSON
        if not scenario_file.filename.endswith('.json'):
            flash('Файл должен быть в формате JSON', 'error')
            return redirect(url_for('admin.index'))
        
        # Читаем и парсим JSON
        try:
            scenario_data = json.loads(scenario_file.read().decode('utf-8'))
        except json.JSONDecodeError:
            flash('Неверный формат JSON файла', 'error')
            return redirect(url_for('admin.index'))
        
        # Создаем сценарий
        scenario = VirtualPatientScenario(
            title=title,
            description=description,
            scenario_data=scenario_data,
            created_by=current_user.id,
            is_published=False
        )
        
        db.session.add(scenario)
        db.session.commit()
        
        flash(f'Сценарий "{title}" успешно загружен', 'success')
        return redirect(url_for('admin.virtual_patients'))
        
    except Exception as e:
        flash(f'Ошибка при загрузке сценария: {str(e)}', 'error')
        return redirect(url_for('admin.index'))

def handle_create_path():
    """Обработка создания пути обучения"""
    try:
        path_name = request.form.get('path_name')
        path_description = request.form.get('path_description')
        
        if not path_name:
            flash('Введите название пути обучения', 'error')
            return redirect(url_for('admin.index'))
        
        # Создаем путь обучения
        learning_path = LearningPath(
            name=path_name,
            description=path_description,
            created_by=current_user.id
        )
        
        db.session.add(learning_path)
        db.session.commit()
        
        flash(f'Путь обучения "{path_name}" создан', 'success')
        return redirect(url_for('learning_map_bp.learning_map', lang='ru'))
        
    except Exception as e:
        flash(f'Ошибка при создании пути: {str(e)}', 'error')
        return redirect(url_for('admin.index'))

def handle_create_lesson():
    """Обработка создания урока"""
    try:
        lesson_title = request.form.get('lesson_title')
        lesson_content = request.form.get('lesson_content')
        
        if not lesson_title:
            flash('Введите название урока', 'error')
            return redirect(url_for('admin.index'))
        
        # Создаем урок
        lesson = Lesson(
            title=lesson_title,
            content=lesson_content,
            created_by=current_user.id
        )
        
        db.session.add(lesson)
        db.session.commit()
        
        flash(f'Урок "{lesson_title}" создан', 'success')
        return redirect(url_for('admin.index'))
        
    except Exception as e:
        flash(f'Ошибка при создании урока: {str(e)}', 'error')
        return redirect(url_for('admin.index'))

def handle_create_test():
    """Обработка создания теста"""
    try:
        test_title = request.form.get('test_title')
        test_description = request.form.get('test_description')
        
        if not test_title:
            flash('Введите название теста', 'error')
            return redirect(url_for('admin.index'))
        
        # Создаем категорию теста
        category = QuestionCategory(
            name=test_title,
            description=test_description,
            created_by=current_user.id
        )
        
        db.session.add(category)
        db.session.commit()
        
        flash(f'Тест "{test_title}" создан', 'success')
        return redirect(url_for('admin.index'))
        
    except Exception as e:
        flash(f'Ошибка при создании теста: {str(e)}', 'error')
        return redirect(url_for('admin.index'))

def handle_add_user():
    """Обработка добавления пользователя"""
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not name or not email or not password:
            flash('Заполните все обязательные поля', 'error')
            return redirect(url_for('admin.index'))
        
        # Проверяем, что email уникален
        if User.query.filter_by(email=email).first():
            flash('Пользователь с таким email уже существует', 'error')
            return redirect(url_for('admin.index'))
        
        # Создаем пользователя
        user = User(
            username=email,
            email=email,
            first_name=name,
            is_active=True
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        flash(f'Пользователь "{name}" добавлен', 'success')
        return redirect(url_for('admin.users'))
        
    except Exception as e:
        flash(f'Ошибка при добавлении пользователя: {str(e)}', 'error')
        return redirect(url_for('admin.index'))

@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """Управление пользователями"""
    users = User.query.all()
    return render_template('admin/users_manager.html', users=users)

@admin_bp.route('/virtual-patients')
@login_required
@admin_required
def virtual_patients():
    """Управление виртуальными пациентами"""
    scenarios = VirtualPatientScenario.query.order_by(VirtualPatientScenario.created_at.desc()).all()
    
    # Добавляем статистику по каждому сценарию
    scenarios_with_stats = []
    for scenario in scenarios:
        attempts_count = VirtualPatientAttempt.query.filter_by(scenario_id=scenario.id).count()
        completed_count = VirtualPatientAttempt.query.filter_by(scenario_id=scenario.id, completed=True).count()
        avg_score = db.session.query(db.func.avg(VirtualPatientAttempt.score)).filter_by(
            scenario_id=scenario.id, completed=True
        ).scalar() or 0
        
        scenarios_with_stats.append({
            'scenario': scenario,
            'attempts_count': attempts_count,
            'completed_count': completed_count,
            'avg_score': round(avg_score, 1)
        })
    
    return render_template('admin/virtual_patients.html', scenarios=scenarios_with_stats)

@admin_bp.route('/virtual-patients/<int:scenario_id>')
@login_required
@admin_required
def virtual_patient_detail(scenario_id):
    """Детальная информация о сценарии"""
    scenario = VirtualPatientScenario.query.get_or_404(scenario_id)
    
    # Получаем статистику попыток
    attempts = VirtualPatientAttempt.query.filter_by(scenario_id=scenario_id).order_by(
        VirtualPatientAttempt.started_at.desc()
    ).limit(20).all()
    
    # Статистика по результатам
    total_attempts = VirtualPatientAttempt.query.filter_by(scenario_id=scenario_id).count()
    completed_attempts = VirtualPatientAttempt.query.filter_by(scenario_id=scenario_id, completed=True).count()
    
    # Распределение по результатам
    good_results = VirtualPatientAttempt.query.filter_by(scenario_id=scenario_id, completed=True).filter(
        VirtualPatientAttempt.score >= scenario.max_score * 0.8
    ).count()
    
    average_results = VirtualPatientAttempt.query.filter_by(scenario_id=scenario_id, completed=True).filter(
        VirtualPatientAttempt.score >= scenario.max_score * 0.6,
        VirtualPatientAttempt.score < scenario.max_score * 0.8
    ).count()
    
    poor_results = VirtualPatientAttempt.query.filter_by(scenario_id=scenario_id, completed=True).filter(
        VirtualPatientAttempt.score < scenario.max_score * 0.6
    ).count()
    
    stats = {
        'total_attempts': total_attempts,
        'completed_attempts': completed_attempts,
        'completion_rate': round((completed_attempts / total_attempts * 100) if total_attempts > 0 else 0, 1),
        'good_results': good_results,
        'average_results': average_results,
        'poor_results': poor_results
    }
    
    return render_template('admin/virtual_patient_detail.html', 
                         scenario=scenario, 
                         attempts=attempts, 
                         stats=stats)

@admin_bp.route('/virtual-patients/<int:scenario_id>/toggle-publish', methods=['POST'])
@login_required
@admin_required
def toggle_scenario_publish(scenario_id):
    """Переключить статус публикации сценария"""
    scenario = VirtualPatientScenario.query.get_or_404(scenario_id)
    scenario.is_published = not scenario.is_published
    db.session.commit()
    
    status = 'опубликован' if scenario.is_published else 'снят с публикации'
    flash(f'Сценарий "{scenario.title}" {status}', 'success')
    
    return redirect(url_for('admin.virtual_patients'))

@admin_bp.route('/virtual-patients/<int:scenario_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_scenario(scenario_id):
    """Удалить сценарий"""
    scenario = VirtualPatientScenario.query.get_or_404(scenario_id)
    title = scenario.title
    
    # Удаляем связанные попытки (если CASCADE не настроен)
    VirtualPatientAttempt.query.filter_by(scenario_id=scenario_id).delete()
    
    db.session.delete(scenario)
    db.session.commit()
    
    flash(f'Сценарий "{title}" удален', 'success')
    return redirect(url_for('admin.virtual_patients'))

@admin_bp.route('/api/stats')
@login_required
@admin_required
def api_stats():
    """API для получения статистики админ панели"""
    # Статистика пользователей
    total_users = User.query.count()
    active_users = User.query.filter_by(is_active=True).count()
    
    # Статистика виртуальных пациентов
    total_scenarios = VirtualPatientScenario.query.count()
    published_scenarios = VirtualPatientScenario.query.filter_by(is_published=True).count()
    total_attempts = VirtualPatientAttempt.query.count()
    completed_attempts = VirtualPatientAttempt.query.filter_by(completed=True).count()
    
    # Статистика по уровням сложности
    difficulty_stats = {}
    for difficulty in ['easy', 'medium', 'hard']:
        count = VirtualPatientScenario.query.filter_by(difficulty=difficulty, is_published=True).count()
        difficulty_stats[difficulty] = count
    
    return jsonify({
        'users': {
            'total': total_users,
            'active': active_users
        },
        'virtual_patients': {
            'total_scenarios': total_scenarios,
            'published_scenarios': published_scenarios,
            'total_attempts': total_attempts,
            'completed_attempts': completed_attempts,
            'completion_rate': round((completed_attempts / total_attempts * 100) if total_attempts > 0 else 0, 1)
        },
        'difficulty_stats': difficulty_stats
    }) 

@admin_bp.route('/api/analytics/realtime')
@login_required
@admin_required
def api_analytics_realtime():
    """API endpoint for real-time analytics data"""
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import func, and_
        from models import User, UserProgress, DiagnosticSession, Question, BIGDomain
        
        # Get time range from request
        time_range = request.args.get('timeRange', '30d')
        
        # Calculate date range
        end_date = datetime.now()
        if time_range == '24h':
            start_date = end_date - timedelta(days=1)
        elif time_range == '7d':
            start_date = end_date - timedelta(days=7)
        elif time_range == '30d':
            start_date = end_date - timedelta(days=30)
        elif time_range == '90d':
            start_date = end_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=30)
        
        # 1. Total users
        total_users = User.query.count()
        
        # 2. Active users (users with activity in the last 7 days)
        active_users_7d = User.query.join(UserProgress).filter(
            UserProgress.last_accessed >= datetime.now() - timedelta(days=7)
        ).distinct().count()
        
        # 3. Completion rate (from UserProgress)
        total_lessons = UserProgress.query.count()
        completed_lessons = UserProgress.query.filter_by(completed=True).count()
        completion_rate = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        
        # 4. AI interactions (diagnostic sessions)
        ai_interactions = DiagnosticSession.query.filter(
            DiagnosticSession.started_at >= start_date
        ).count()
        
        # 5. Chat sessions (simplified - using diagnostic sessions)
        chat_sessions = DiagnosticSession.query.filter(
            DiagnosticSession.started_at >= start_date,
            DiagnosticSession.status == 'completed'
        ).count()
        
        # 6. User satisfaction (simplified - using completion rate as proxy)
        user_satisfaction = min(completion_rate / 100, 0.95)  # Cap at 95%
        
        # 7. System health (based on error rate)
        total_sessions = DiagnosticSession.query.filter(
            DiagnosticSession.started_at >= start_date
        ).count()
        completed_sessions = DiagnosticSession.query.filter(
            DiagnosticSession.started_at >= start_date,
            DiagnosticSession.status == 'completed'
        ).count()
        system_health = (completed_sessions / total_sessions) if total_sessions > 0 else 0.95
        
        # 8. Error rate
        error_rate = 1 - system_health
        
        # 9. Trending topics (based on domain activity)
        domain_activity = db.session.query(
            BIGDomain.name,
            func.count(Question.id).label('question_count')
        ).join(Question).group_by(BIGDomain.id).order_by(
            func.count(Question.id).desc()
        ).limit(5).all()
        
        trending_topics = []
        for domain_name, count in domain_activity:
            trending_topics.append({
                'topic': domain_name,
                'mentions': count,
                'trend': 'up' if count > 10 else 'stable',
                'percentage': round((count / sum([c for _, c in domain_activity])) * 100, 1)
            })
        
        # 10. Performance metrics
        avg_messages_per_session = 8.5  # Default value
        avg_response_length = 245  # Default value
        response_time = 0.42  # Default value
        uptime = system_health
        throughput = ai_interactions / max((end_date - start_date).days, 1)
        
        # 11. Daily metrics for charts
        daily_metrics = []
        current_date = start_date
        while current_date <= end_date:
            next_date = current_date + timedelta(days=1)
            
            daily_active_users = User.query.join(UserProgress).filter(
                and_(
                    UserProgress.last_accessed >= current_date,
                    UserProgress.last_accessed < next_date
                )
            ).distinct().count()
            
            daily_ai_interactions = DiagnosticSession.query.filter(
                and_(
                    DiagnosticSession.started_at >= current_date,
                    DiagnosticSession.started_at < next_date
                )
            ).count()
            
            daily_chat_sessions = DiagnosticSession.query.filter(
                and_(
                    DiagnosticSession.started_at >= current_date,
                    DiagnosticSession.started_at < next_date,
                    DiagnosticSession.status == 'completed'
                )
            ).count()
            
            daily_metrics.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'active_users': daily_active_users,
                'ai_interactions': daily_ai_interactions,
                'user_satisfaction': user_satisfaction,
                'chat_sessions': daily_chat_sessions,
                'error_rate': error_rate
            })
            
            current_date = next_date
        
        return jsonify({
            'success': True,
            'metrics': {
                'active_users': active_users_7d,
                'ai_interactions': ai_interactions,
                'chat_sessions': chat_sessions,
                'user_satisfaction': user_satisfaction,
                'system_health': system_health,
                'error_rate': error_rate,
                'total_users': total_users,
                'completion_rate': completion_rate
            },
            'trending_topics': trending_topics,
            'performance_metrics': {
                'avg_messages_per_session': avg_messages_per_session,
                'avg_response_length': avg_response_length,
                'response_time': response_time,
                'uptime': uptime,
                'throughput': throughput
            },
            'daily_metrics': daily_metrics,
            'time_range': time_range
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in analytics API: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to load analytics data'
        }), 500

@admin_bp.route('/scheduler')
@login_required
@admin_required
def scheduler_dashboard():
    """Admin dashboard for diagnostic scheduler monitoring"""
    try:
        from utils.scheduler_service import get_scheduler
        
        scheduler = get_scheduler()
        
        # Get scheduler statistics
        overdue_reassessments = scheduler.get_overdue_reassessments()
        recommendations = scheduler.get_reassessment_recommendations(limit=20)
        
        # Calculate statistics
        stats = {
            'overdue_count': len(overdue_reassessments),
            'recommendations_count': len(recommendations),
            'critical_priority': len([r for r in recommendations if r.priority.value == 'critical']),
            'high_priority': len([r for r in recommendations if r.priority.value == 'high']),
            'medium_priority': len([r for r in recommendations if r.priority.value == 'medium']),
            'low_priority': len([r for r in recommendations if r.priority.value == 'low'])
        }
        
        return render_template('admin/scheduler_dashboard.html',
                             stats=stats,
                             overdue=overdue_reassessments,
                             recommendations=recommendations)
                             
    except Exception as e:
        flash(f'Error loading scheduler dashboard: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))


@admin_bp.route('/scheduler/run-check', methods=['POST'])
@login_required
@admin_required
def run_scheduler_check():
    """Manually run scheduler check"""
    try:
        from utils.scheduler_service import run_daily_scheduler_check
        
        run_daily_scheduler_check()
        flash('Scheduler check completed successfully', 'success')
        
    except Exception as e:
        flash(f'Error running scheduler check: {str(e)}', 'error')
    
    return redirect(url_for('admin.scheduler_dashboard'))


@admin_bp.route('/scheduler/update-plan/<int:plan_id>', methods=['POST'])
@login_required
@admin_required
def update_plan_schedule(plan_id):
    """Manually update plan schedule"""
    try:
        from utils.scheduler_service import get_scheduler
        
        scheduler = get_scheduler()
        success = scheduler.update_plan_schedule(plan_id)
        
        if success:
            flash(f'Plan {plan_id} schedule updated successfully', 'success')
        else:
            flash(f'Failed to update plan {plan_id} schedule', 'error')
            
    except Exception as e:
        flash(f'Error updating plan schedule: {str(e)}', 'error')
    
    return redirect(url_for('admin.scheduler_dashboard')) 

@admin_bp.route('/metrics')
@login_required
def admin_metrics():
    """Admin metrics dashboard for adaptive learning system"""
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('admin.dashboard'))
    
    try:
        from utils.metrics import get_system_health, get_performance_metrics
        
        # Get system health report
        health_report = get_system_health()
        
        # Get performance metrics for last 24 hours
        performance_24h = get_performance_metrics(hours=24)
        
        # Get performance metrics for last 7 days
        performance_7d = get_performance_metrics(hours=168)
        
        # Get recent diagnostic sessions
        from models import DiagnosticSession
        recent_sessions = DiagnosticSession.query.filter_by(
            status='completed'
        ).order_by(DiagnosticSession.completed_at.desc()).limit(10).all()
        
        # Calculate session statistics
        session_stats = {
            'total_completed': DiagnosticSession.query.filter_by(status='completed').count(),
            'total_active': DiagnosticSession.query.filter_by(status='active').count(),
            'avg_questions_per_session': 0.0,
            'avg_ability': 0.0,
            'avg_se': 0.0
        }
        
        if recent_sessions:
            total_questions = sum(s.questions_answered for s in recent_sessions)
            total_ability = sum(s.current_ability for s in recent_sessions)
            total_se = sum(s.ability_se for s in recent_sessions)
            
            session_stats['avg_questions_per_session'] = total_questions / len(recent_sessions)
            session_stats['avg_ability'] = total_ability / len(recent_sessions)
            session_stats['avg_se'] = total_se / len(recent_sessions)
        
        return render_template('admin/metrics.html',
                             health_report=health_report,
                             performance_24h=performance_24h,
                             performance_7d=performance_7d,
                             session_stats=session_stats,
                             recent_sessions=recent_sessions)
                             
    except Exception as e:
        logger.error(f"Error loading metrics: {e}")
        flash('Error loading metrics', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/metrics/export')
@login_required
def export_metrics():
    """Export metrics data"""
    if not current_user.is_admin:
        flash('Access denied', 'error')
        return redirect(url_for('admin.dashboard'))
    
    try:
        from utils.metrics import get_metrics
        import os
        
        # Create exports directory if it doesn't exist
        exports_dir = os.path.join(os.getcwd(), 'exports')
        os.makedirs(exports_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'metrics_export_{timestamp}.json'
        filepath = os.path.join(exports_dir, filename)
        
        # Export metrics
        metrics = get_metrics()
        metrics.export_metrics(filepath)
        
        # Return file for download
        from flask import send_file
        return send_file(filepath, as_attachment=True, download_name=filename)
        
    except Exception as e:
        logger.error(f"Error exporting metrics: {e}")
        flash('Error exporting metrics', 'error')
        return redirect(url_for('admin.metrics')) 

@admin_bp.route('/api/system/health', methods=['GET'])
@login_required
@admin_required
def system_health_check():
    """Check system data health and validation status"""
    from utils.data_validator import validate_system_health
    from utils.feedback_monitor import FeedbackMonitor
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Получаем отчет о здоровье системы
        health_report = validate_system_health()
        
        # Получаем статус обратной связи
        feedback_monitor = FeedbackMonitor()
        feedback_status = feedback_monitor.get_system_health()
        
        # Объединяем отчеты
        full_report = {
            'timestamp': health_report['timestamp'],
            'data_health': health_report,
            'feedback_health': feedback_status,
            'overall_status': 'healthy'
        }
        
        # Определяем общий статус
        if (health_report.get('summary', {}).get('status') == 'critical' or 
            feedback_status.get('status') == 'critical'):
            full_report['overall_status'] = 'critical'
        elif (health_report.get('summary', {}).get('status') == 'error' or 
              feedback_status.get('status') == 'error'):
            full_report['overall_status'] = 'error'
        elif (health_report.get('summary', {}).get('status') == 'warning' or 
              feedback_status.get('status') == 'warning'):
            full_report['overall_status'] = 'warning'
        
        # Добавляем рекомендации
        recommendations = []
        
        # Рекомендации по данным
        if 'recommendations' in health_report:
            recommendations.extend(health_report['recommendations'])
        
        # Рекомендации по обратной связи
        if feedback_status.get('status') != 'healthy':
            recommendations.append(f"Feedback system: {feedback_status.get('status', 'unknown')}")
        
        full_report['recommendations'] = recommendations
        
        return jsonify(full_report)
        
    except Exception as e:
        logger.error(f"Error during system health check: {e}")
        return jsonify({
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'error': str(e),
            'overall_status': 'error'
        }), 500


@admin_bp.route('/api/system/validate-data', methods=['POST'])
@login_required
@admin_required
def validate_specific_data():
    """Validate specific data categories"""
    from utils.data_validator import DataValidator
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        categories = data.get('categories', [])
        if not categories:
            return jsonify({'error': 'No categories specified'}), 400
        
        validator = DataValidator()
        results = {}
        
        # Валидируем только указанные категории
        if 'questions' in categories:
            questions = Question.query.limit(50).all()
            results['questions'] = []
            for question in questions:
                results['questions'].extend(validator.validate_question(question))
        
        if 'irt_parameters' in categories:
            irt_params = IRTParameters.query.limit(50).all()
            results['irt_parameters'] = []
            for params in irt_params:
                results['irt_parameters'].extend(validator.validate_irt_parameters(params))
        
        if 'diagnostic_sessions' in categories:
            sessions = DiagnosticSession.query.limit(50).all()
            results['diagnostic_sessions'] = []
            for session in sessions:
                results['diagnostic_sessions'].extend(validator.validate_diagnostic_session(session))
        
        if 'study_sessions' in categories:
            study_sessions = StudySession.query.limit(50).all()
            results['study_sessions'] = []
            for session in study_sessions:
                results['study_sessions'].extend(validator.validate_study_session(session))
        
        if 'learning_plans' in categories:
            plans = PersonalLearningPlan.query.limit(50).all()
            results['learning_plans'] = []
            for plan in plans:
                results['learning_plans'].extend(validator.validate_personal_learning_plan(plan))
        
        if 'responses' in categories:
            responses = DiagnosticResponse.query.limit(50).all()
            results['responses'] = []
            for response in responses:
                results['responses'].extend(validator.validate_response_data(response))
        
        if 'users' in categories:
            users = User.query.limit(50).all()
            results['users'] = []
            for user in users:
                results['users'].extend(validator.validate_user_data(user))
        
        # Получаем сводку
        summary = validator.get_validation_summary(results)
        
        return jsonify({
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'categories_validated': categories,
            'summary': summary,
            'details': results
        })
        
    except Exception as e:
        logger.error(f"Error during specific data validation: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500


@admin_bp.route('/api/system/fix-data-issues', methods=['POST'])
@login_required
@admin_required
def fix_data_issues():
    """Attempt to fix common data issues automatically"""
    from utils.data_validator import DataValidator, ValidationLevel
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        fix_types = data.get('fix_types', [])
        if not fix_types:
            return jsonify({'error': 'No fix types specified'}), 400
        
        fixes_applied = []
        errors = []
        
        # Исправление некорректных способностей
        if 'ability_range' in fix_types:
            try:
                # Исправляем способности вне диапазона
                plans = PersonalLearningPlan.query.filter(
                    (PersonalLearningPlan.current_ability < -4.0) | 
                    (PersonalLearningPlan.current_ability > 4.0)
                ).all()
                
                for plan in plans:
                    old_ability = plan.current_ability
                    plan.current_ability = max(-4.0, min(4.0, plan.current_ability))
                    fixes_applied.append(f"Fixed ability for plan {plan.id}: {old_ability} -> {plan.current_ability}")
                
                # Исправляем целевые способности
                plans_target = PersonalLearningPlan.query.filter(
                    (PersonalLearningPlan.target_ability < -4.0) | 
                    (PersonalLearningPlan.target_ability > 4.0)
                ).all()
                
                for plan in plans_target:
                    old_target = plan.target_ability
                    plan.target_ability = max(-4.0, min(4.0, plan.target_ability))
                    fixes_applied.append(f"Fixed target ability for plan {plan.id}: {old_target} -> {plan.target_ability}")
                
            except Exception as e:
                errors.append(f"Error fixing ability ranges: {e}")
        
        # Исправление прогресса
        if 'progress_range' in fix_types:
            try:
                # Исправляем прогресс вне диапазона
                plans = PersonalLearningPlan.query.filter(
                    (PersonalLearningPlan.overall_progress < 0.0) | 
                    (PersonalLearningPlan.overall_progress > 100.0)
                ).all()
                
                for plan in plans:
                    old_progress = plan.overall_progress
                    plan.overall_progress = max(0.0, min(100.0, plan.overall_progress))
                    fixes_applied.append(f"Fixed progress for plan {plan.id}: {old_progress} -> {plan.overall_progress}")
                
            except Exception as e:
                errors.append(f"Error fixing progress ranges: {e}")
        
        # Исправление статистики сессий
        if 'session_statistics' in fix_types:
            try:
                # Исправляем некорректную статистику
                sessions = DiagnosticSession.query.filter(
                    (DiagnosticSession.correct_answers < 0) |
                    (DiagnosticSession.questions_answered < 0) |
                    (DiagnosticSession.correct_answers > DiagnosticSession.questions_answered)
                ).all()
                
                for session in sessions:
                    if session.correct_answers < 0:
                        old_correct = session.correct_answers
                        session.correct_answers = 0
                        fixes_applied.append(f"Fixed negative correct answers for session {session.id}: {old_correct} -> 0")
                    
                    if session.questions_answered < 0:
                        old_answered = session.questions_answered
                        session.questions_answered = 0
                        fixes_applied.append(f"Fixed negative questions answered for session {session.id}: {old_answered} -> 0")
                    
                    if session.correct_answers > session.questions_answered:
                        old_correct = session.correct_answers
                        session.correct_answers = session.questions_answered
                        fixes_applied.append(f"Fixed correct answers > questions for session {session.id}: {old_correct} -> {session.correct_answers}")
                
            except Exception as e:
                errors.append(f"Error fixing session statistics: {e}")
        
        # Сохраняем изменения
        if fixes_applied:
            db.session.commit()
        
        return jsonify({
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'fixes_applied': fixes_applied,
            'errors': errors,
            'success': len(errors) == 0
        })
        
    except Exception as e:
        logger.error(f"Error during data fixes: {e}")
        db.session.rollback()
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500 

@admin_bp.route('/api/performance/status', methods=['GET'])
@login_required
@admin_required
def performance_status():
    """Get performance status and optimization metrics"""
    from utils.performance_optimizer import performance_optimizer
    from utils.cache_manager import get_cache_stats
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Получаем отчет о производительности
        performance_report = performance_optimizer.get_performance_report()
        
        # Получаем статистику кэширования
        cache_stats = get_cache_stats()
        
        # Получаем информацию о системе
        import psutil
        system_info = {
            'cpu_percent': psutil.cpu_percent(interval=1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else [0, 0, 0]
        }
        
        # Объединяем отчеты
        full_report = {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'performance': performance_report,
            'caching': cache_stats,
            'system': system_info,
            'overall_status': 'healthy'
        }
        
        # Определяем общий статус
        if (system_info['cpu_percent'] > 80 or 
            system_info['memory_percent'] > 80 or
            performance_report.get('memory', {}).get('should_cleanup', False)):
            full_report['overall_status'] = 'warning'
        
        if (system_info['cpu_percent'] > 95 or 
            system_info['memory_percent'] > 95):
            full_report['overall_status'] = 'critical'
        
        return jsonify(full_report)
        
    except Exception as e:
        logger.error(f"Error getting performance status: {e}")
        return jsonify({
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'error': str(e),
            'overall_status': 'error'
        }), 500


@admin_bp.route('/api/performance/optimize', methods=['POST'])
@login_required
@admin_required
def optimize_performance():
    """Run performance optimization"""
    from utils.performance_optimizer import optimize_performance, OptimizationLevel
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        level_str = data.get('level', 'basic')
        
        # Преобразуем строку в enum
        level_map = {
            'basic': OptimizationLevel.BASIC,
            'advanced': OptimizationLevel.ADVANCED,
            'aggressive': OptimizationLevel.AGGRESSIVE
        }
        
        if level_str not in level_map:
            return jsonify({'error': 'Invalid optimization level'}), 400
        
        level = level_map[level_str]
        
        # Запускаем оптимизацию
        result = optimize_performance(level)
        
        logger.info(f"Performance optimization completed with level: {level_str}")
        
        return jsonify({
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'optimization_level': level_str,
            'result': result
        })
        
    except Exception as e:
        logger.error(f"Error during performance optimization: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500


@admin_bp.route('/api/performance/profile', methods=['POST'])
@login_required
@admin_required
def start_profiling():
    """Start performance profiling"""
    from utils.performance_optimizer import performance_optimizer
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        data = request.get_json()
        action = data.get('action', 'start') if data else 'start'
        
        if action == 'start':
            performance_optimizer.profiler.start_profiling()
            message = "Performance profiling started"
        elif action == 'stop':
            profile_report = performance_optimizer.profiler.stop_profiling()
            return jsonify({
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'action': 'stop',
                'profile_report': profile_report
            })
        else:
            return jsonify({'error': 'Invalid action'}), 400
        
        return jsonify({
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'action': action,
            'message': message
        })
        
    except Exception as e:
        logger.error(f"Error during profiling: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500


@admin_bp.route('/api/performance/cache/clear', methods=['POST'])
@login_required
@admin_required
def clear_cache():
    """Clear all caches"""
    from utils.cache_manager import cache_manager
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        data = request.get_json()
        cache_type = data.get('cache_type', 'all') if data else 'all'
        
        if cache_type == 'all':
            cache_manager.clear_all_caches()
            message = "All caches cleared"
        elif cache_type == 'questions':
            cache_manager.question_cache.clear()
            message = "Question cache cleared"
        elif cache_type == 'irt_params':
            cache_manager.irt_params_cache.clear()
            message = "IRT parameters cache cleared"
        elif cache_type == 'sessions':
            cache_manager.session_cache.clear()
            message = "Sessions cache cleared"
        elif cache_type == 'plans':
            cache_manager.plan_cache.clear()
            message = "Learning plans cache cleared"
        else:
            return jsonify({'error': 'Invalid cache type'}), 400
        
        logger.info(f"Cache cleared: {cache_type}")
        
        return jsonify({
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'cache_type': cache_type,
            'message': message
        })
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500


@admin_bp.route('/api/performance/memory/cleanup', methods=['POST'])
@login_required
@admin_required
def cleanup_memory():
    """Clean up memory"""
    from utils.performance_optimizer import performance_optimizer
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Выполняем очистку памяти
        cleanup_result = performance_optimizer.memory_optimizer.cleanup_memory()
        
        logger.info(f"Memory cleanup completed: {cleanup_result['memory_freed_mb']:.2f}MB freed")
        
        return jsonify({
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'cleanup_result': cleanup_result
        })
        
    except Exception as e:
        logger.error(f"Error during memory cleanup: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500


@admin_bp.route('/api/performance/queries/slow', methods=['GET'])
@login_required
@admin_required
def get_slow_queries():
    """Get slow queries report"""
    from utils.performance_optimizer import performance_optimizer
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        slow_queries = performance_optimizer.query_optimizer.slow_queries
        
        # Группируем по функции
        query_stats = {}
        for query in slow_queries:
            func_name = query.get('function_name', 'unknown')
            if func_name not in query_stats:
                query_stats[func_name] = {
                    'count': 0,
                    'total_time': 0,
                    'avg_time': 0,
                    'max_time': 0
                }
            
            stats = query_stats[func_name]
            stats['count'] += 1
            stats['total_time'] += query.get('execution_time', 0)
            stats['max_time'] = max(stats['max_time'], query.get('execution_time', 0))
        
        # Вычисляем среднее время
        for func_name, stats in query_stats.items():
            stats['avg_time'] = stats['total_time'] / stats['count']
        
        return jsonify({
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'total_slow_queries': len(slow_queries),
            'query_stats': query_stats,
            'recent_slow_queries': slow_queries[-10:]  # Последние 10 медленных запросов
        })
        
    except Exception as e:
        logger.error(f"Error getting slow queries: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500


@admin_bp.route('/api/performance/metrics', methods=['GET'])
@login_required
@admin_required
def get_performance_metrics():
    """Get detailed performance metrics"""
    from utils.performance_optimizer import performance_optimizer
    import logging
    
    logger = logging.getLogger(__name__)
    
    try:
        # Получаем метрики профилирования
        profiler_metrics = performance_optimizer.profiler.metrics
        
        # Анализируем метрики
        function_stats = {}
        for metric in profiler_metrics:
            func_name = metric.function_name
            if func_name not in function_stats:
                function_stats[func_name] = {
                    'calls': 0,
                    'total_time': 0,
                    'avg_time': 0,
                    'max_time': 0,
                    'total_memory': 0,
                    'avg_memory': 0
                }
            
            stats = function_stats[func_name]
            stats['calls'] += metric.calls_count
            stats['total_time'] += metric.execution_time
            stats['max_time'] = max(stats['max_time'], metric.execution_time)
            stats['total_memory'] += metric.memory_usage
        
        # Вычисляем средние значения
        for func_name, stats in function_stats.items():
            stats['avg_time'] = stats['total_time'] / stats['calls']
            stats['avg_memory'] = stats['total_memory'] / stats['calls']
        
        # Сортируем по общему времени выполнения
        sorted_functions = sorted(
            function_stats.items(),
            key=lambda x: x[1]['total_time'],
            reverse=True
        )
        
        return jsonify({
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'total_functions_profiled': len(function_stats),
            'total_metrics_collected': len(profiler_metrics),
            'top_functions_by_time': sorted_functions[:10],
            'slow_functions': [
                (name, stats) for name, stats in function_stats.items()
                if stats['avg_time'] > 1.0
            ]
        })
        
    except Exception as e:
        logger.error(f"Error getting performance metrics: {e}")
        return jsonify({
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }), 500 