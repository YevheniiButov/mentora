"""
Административные роуты для управления системой
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from extensions import csrf
from utils.decorators import admin_required
from models import (
    db,
    User,
    LearningPath,
    Subject,
    Module,
    Lesson,
    MedicalTerm,
    UserProgress,
    Question,
    QuestionCategory,
    VirtualPatientScenario,
    VirtualPatientAttempt,
    DiagnosticSession,
    BIGDomain,
    PersonalLearningPlan,
    IRTParameters,
    DiagnosticResponse,
    WebsiteVisit,
    PageView,
    UserSession,
    ProfileAuditLog,
    Profession,
    ProfessionSpecialization,
    Contact,
    CountryAnalytics,
    DeviceAnalytics,
    ProfessionAnalytics,
    AnalyticsEvent,
    AdminAuditLog,
    SystemHealthLog,
    DatabaseBackup,
    EmailTemplate,
    CommunicationCampaign,
    SystemNotification,
    ForumTopic,
    ForumPost,
    UserTermProgress,
    DailyFlashcardProgress,
    UserEnglishProgress,
    UserItemMastery,
    EnglishPassage,
    TestAttempt,
)
from datetime import datetime, timedelta, date
import json
from sqlalchemy import func, and_, or_, distinct
from datetime import timezone
import logging

# Initialize logger
logger = logging.getLogger(__name__)

def get_date_func():
    """Get database-specific date function"""
    try:
        # Try to detect database type
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        if inspector.dialect.name == 'postgresql':
            return func.date_trunc('day', func.cast(func.now(), db.Date))
        else:
            return func.date
    except:
        return func.date

def safe_date_query(query, date_column, target_date):
    """Safe date query that works with both PostgreSQL and SQLite"""
    try:
        # Try PostgreSQL first
        return query.filter(func.date_trunc('day', date_column) == target_date)
    except Exception:
        # Fallback to SQLite
        return query.filter(func.date(date_column) == target_date)

admin_bp = Blueprint('admin', __name__)


# ========================================
# FLASHCARDS (MEDICAL TERMS) MANAGEMENT
# ========================================


@admin_bp.route('/flashcards/manage')
@login_required
@admin_required
def flashcards_manager():
    """Просмотр и фильтрация медицинских терминов для флешкарт."""
    search = (request.args.get('search') or '').strip()
    selected_category = (request.args.get('category') or '').strip()
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=25, type=int)

    per_page = max(5, min(per_page, 100))
    query = MedicalTerm.query

    if search:
        pattern = f"%{search}%"
        query = query.filter(
            or_(
                MedicalTerm.term_nl.ilike(pattern),
                MedicalTerm.term_en.ilike(pattern),
                MedicalTerm.definition_nl.ilike(pattern),
            )
        )

    if selected_category:
        query = query.filter(MedicalTerm.category == selected_category)

    query = query.order_by(MedicalTerm.term_nl.asc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    categories = [
        row[0]
        for row in db.session.query(MedicalTerm.category)
        .distinct()
        .order_by(MedicalTerm.category.asc())
        .all()
        if row[0]
    ]

    return render_template(
        'admin/flashcards_manager.html',
        terms=pagination.items,
        pagination=pagination,
        categories=categories,
        search=search,
        selected_category=selected_category,
        per_page=per_page,
    )


@admin_bp.route('/flashcards/<int:term_id>/update', methods=['POST'])
@login_required
@admin_required
def flashcards_update(term_id):
    """Обновление данных медицинского термина."""
    term = MedicalTerm.query.get_or_404(term_id)

    def _cleanup(value: str):
        return value.strip() if value and value.strip() else None

    filter_search = (request.form.get('filter_search') or '').strip()
    filter_category = (request.form.get('filter_category') or '').strip()
    filter_page_raw = request.form.get('filter_page')
    filter_per_page_raw = request.form.get('filter_per_page')

    try:
        term_nl = (request.form.get('term_nl') or '').strip()
        if not term_nl:
            flash('Нидерландский термин является обязательным.', 'error')
            raise ValueError('term_nl required')

        term_category = (request.form.get('term_category') or '').strip()
        if not term_category:
            flash('Категория не может быть пустой.', 'error')
            raise ValueError('category required')

        term.term_nl = term_nl
        term.definition_nl = request.form.get('definition_nl') or None
        term.term_en = _cleanup(request.form.get('term_en'))
        term.term_ru = _cleanup(request.form.get('term_ru'))
        term.term_uk = _cleanup(request.form.get('term_uk'))
        term.term_es = _cleanup(request.form.get('term_es'))
        term.term_pt = _cleanup(request.form.get('term_pt'))
        term.term_tr = _cleanup(request.form.get('term_tr'))
        term.term_fa = _cleanup(request.form.get('term_fa'))
        term.term_ar = _cleanup(request.form.get('term_ar'))
        term.category = term_category
        term.audio_url = _cleanup(request.form.get('audio_url'))

        difficulty_raw = request.form.get('difficulty')
        if difficulty_raw is not None and difficulty_raw.strip():
            try:
                difficulty_value = int(difficulty_raw)
            except ValueError:
                difficulty_value = term.difficulty or 1
        else:
            difficulty_value = term.difficulty or 1
        term.difficulty = max(1, min(difficulty_value, 5))

        frequency_raw = request.form.get('frequency')
        if frequency_raw is not None and frequency_raw.strip():
            try:
                frequency_value = int(frequency_raw)
            except ValueError:
                frequency_value = term.frequency or 1
        else:
            frequency_value = term.frequency or 1
        term.frequency = max(1, frequency_value)

        db.session.commit()
        flash('Термин успешно обновлён.', 'success')
    except ValueError:
        db.session.rollback()
    except Exception as exc:
        db.session.rollback()
        current_app.logger.error(f"Failed to update medical term {term_id}: {exc}")
        flash('Не удалось обновить термин. Проверьте данные и попробуйте снова.', 'error')

    redirect_args = {}
    if filter_search:
        redirect_args['search'] = filter_search
    if filter_category:
        redirect_args['category'] = filter_category

    try:
        filter_page = int(filter_page_raw)
        if filter_page > 1:
            redirect_args['page'] = filter_page
    except (TypeError, ValueError):
        pass

    try:
        filter_per_page = int(filter_per_page_raw)
        if filter_per_page and filter_per_page != 25:
            redirect_args['per_page'] = max(5, min(filter_per_page, 100))
    except (TypeError, ValueError):
        pass

    return redirect(url_for('admin.flashcards_manager', **redirect_args))

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Enhanced admin dashboard with real-time metrics"""
    try:
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
    
    except Exception as e:
        current_app.logger.error(f"Dashboard error: {str(e)}")
        # Return basic dashboard with error message
        return render_template('admin/dashboard_new.html',
                             users_metrics={'total_users': 0, 'new_today': 0, 'new_week': 0, 'active_week': 0},
                             diagnostic_metrics={'total_sessions': 0, 'completed_sessions': 0, 'sessions_today': 0, 'sessions_week': 0, 'avg_ability': 0, 'completion_rate': 0},
                             learning_metrics={'total_plans': 0, 'active_plans': 0, 'avg_progress': 0, 'overdue_reassessments': 0},
                             content_metrics={'total_lessons': 0, 'lessons_completed_week': 0, 'avg_time_per_lesson': 0},
                             recent_users=[],
                             recent_sessions=[],
                             error=str(e))

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
    profession_filter = request.args.get('profession', 'all')
    search = request.args.get('search', '')
    
    query = Question.query
    
    # Поиск
    if search:
        query = query.filter(Question.text.ilike(f'%{search}%'))
    
    # Фильтр по домену
    if domain_filter != 'all':
        query = query.filter_by(domain=domain_filter)
    
    # Фильтр по профессии
    if profession_filter != 'all':
        query = query.filter_by(profession=profession_filter)
    
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
    
    # Получаем список профессий для фильтра
    professions = db.session.query(Question.profession).filter(Question.profession.isnot(None)).distinct().all()
    professions = [p[0] for p in professions if p[0]]
    
    return render_template('admin/questions_management.html',
                         questions=questions,
                         domains=domains,
                         professions=professions,
                         domain_filter=domain_filter,
                         profession_filter=profession_filter,
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
        question.profession = request.form.get('profession')
        
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
        'DIAGNOSTIC_MIN_QUESTIONS': current_app.config.get('DIAGNOSTIC_MIN_QUESTIONS', 20),
        'DIAGNOSTIC_MAX_QUESTIONS': current_app.config.get('DIAGNOSTIC_MAX_QUESTIONS', 50),
        'REASSESSMENT_DAYS': current_app.config.get('REASSESSMENT_DAYS', 14),
        'MIN_LESSONS_PER_DAY': current_app.config.get('MIN_LESSONS_PER_DAY', 3),
        'MAX_LESSONS_PER_DAY': current_app.config.get('MAX_LESSONS_PER_DAY', 10),
        'IRT_CONVERGENCE_THRESHOLD': current_app.config.get('IRT_CONVERGENCE_THRESHOLD', 0.001),
        'ENABLE_AI_ASSISTANT': current_app.config.get('ENABLE_AI_ASSISTANT', True),
        'ENABLE_VIRTUAL_PATIENTS': current_app.config.get('ENABLE_VIRTUAL_PATIENTS', True)
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
                current_app.config[setting] = float(value)
            else:
                current_app.config[setting] = int(value)
    
    # Булевы настройки
    current_app.config['ENABLE_AI_ASSISTANT'] = 'ENABLE_AI_ASSISTANT' in request.form
    current_app.config['ENABLE_VIRTUAL_PATIENTS'] = 'ENABLE_VIRTUAL_PATIENTS' in request.form
    
    # Сохраняем в файл конфигурации
    save_config_to_file(current_app.config)
    
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
    upload_path = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
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
    db_url = current_app.config.get('SQLALCHEMY_DATABASE_URI')
    backup_file = f"backups/mentora_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sql"
    # subprocess.run(['pg_dump', db_url, '-f', backup_file])
    pass

def save_config_to_file(config):
    """Save configuration to file"""
    import os
    import json
    from datetime import datetime
    
    try:
        # Create config backup directory
        config_dir = os.path.join(current_app.root_path, 'config_backups')
        os.makedirs(config_dir, exist_ok=True)
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(config_dir, f'config_backup_{timestamp}.json')
        
        # Save current config to backup file
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False, default=str)
        
        # Also save to environment file if specified
        env_file = os.path.join(current_app.root_path, '.env')
        if os.path.exists(env_file):
            # Create environment backup
            env_backup = os.path.join(config_dir, f'env_backup_{timestamp}.env')
            with open(env_file, 'r', encoding='utf-8') as src:
                with open(env_backup, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
        
        current_app.logger.info(f"Configuration saved to {backup_file}")
        return True
        
    except Exception as e:
        current_app.logger.error(f"Error saving configuration: {str(e)}")
        return False

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
        return redirect(url_for('daily_learning.learning_map', lang='ru'))
        
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

@admin_bp.route('/crm/users')
@login_required
@admin_required
def crm_users():
    """Enhanced CRM for users with full registration data"""
    try:
        # Get filter parameters
        status_filter = request.args.get('status', 'all')
        profession_filter = request.args.get('profession', 'all')
        nationality_filter = request.args.get('nationality', 'all')
        legal_status_filter = request.args.get('legal_status', 'all')
        dutch_level_filter = request.args.get('dutch_level', 'all')
        english_level_filter = request.args.get('english_level', 'all')
        search_query = request.args.get('search', '').strip()
        sort_by = request.args.get('sort', 'created_at')
        sort_order = request.args.get('order', 'desc')
        
        # Build query
        query = User.query
        
        # Apply filters
        if status_filter != 'all':
            if status_filter == 'active':
                query = query.filter_by(is_active=True)
            elif status_filter == 'inactive':
                query = query.filter_by(is_active=False)
            elif status_filter == 'confirmed':
                query = query.filter_by(email_confirmed=True)
            elif status_filter == 'unconfirmed':
                query = query.filter_by(email_confirmed=False)
            elif status_filter == 'digid':
                query = query.filter_by(created_via_digid=True)
            elif status_filter == 'regular':
                query = query.filter_by(created_via_digid=False)
        
        if profession_filter != 'all':
            query = query.filter_by(profession=profession_filter)
        
        if nationality_filter != 'all':
            query = query.filter_by(nationality=nationality_filter)
        
        if legal_status_filter != 'all':
            query = query.filter_by(legal_status=legal_status_filter)
        
        if dutch_level_filter != 'all':
            query = query.filter_by(dutch_level=dutch_level_filter)
        
        if english_level_filter != 'all':
            query = query.filter_by(english_level=english_level_filter)
        
        if search_query:
            query = query.filter(
                or_(
                    User.first_name.ilike(f'%{search_query}%'),
                    User.last_name.ilike(f'%{search_query}%'),
                    User.email.ilike(f'%{search_query}%'),
                    User.phone.ilike(f'%{search_query}%'),
                    User.workplace.ilike(f'%{search_query}%'),
                    User.university_name.ilike(f'%{search_query}%')
                )
            )
        
        # Apply sorting
        if sort_by == 'name':
            if sort_order == 'asc':
                query = query.order_by(User.first_name.asc(), User.last_name.asc())
            else:
                query = query.order_by(User.first_name.desc(), User.last_name.desc())
        elif sort_by == 'email':
            if sort_order == 'asc':
                query = query.order_by(User.email.asc())
            else:
                query = query.order_by(User.email.desc())
        elif sort_by == 'profession':
            if sort_order == 'asc':
                query = query.order_by(User.profession.asc())
            else:
                query = query.order_by(User.profession.desc())
        elif sort_by == 'nationality':
            if sort_order == 'asc':
                query = query.order_by(User.nationality.asc())
            else:
                query = query.order_by(User.nationality.desc())
        else:  # created_at
            if sort_order == 'asc':
                query = query.order_by(User.created_at.asc())
            else:
                query = query.order_by(User.created_at.desc())
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = 25
        users = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get filter options
        professions = db.session.query(User.profession).filter(User.profession.isnot(None)).distinct().all()
        nationalities = db.session.query(User.nationality).filter(User.nationality.isnot(None)).distinct().all()
        legal_statuses = db.session.query(User.legal_status).filter(User.legal_status.isnot(None)).distinct().all()
        dutch_levels = db.session.query(User.dutch_level).filter(User.dutch_level.isnot(None)).distinct().all()
        english_levels = db.session.query(User.english_level).filter(User.english_level.isnot(None)).distinct().all()
        
        # Statistics
        stats = {
            'total_users': User.query.count(),
            'active_users': User.query.filter_by(is_active=True).count(),
            'confirmed_users': User.query.filter_by(email_confirmed=True).count(),
            'digid_users': User.query.filter_by(created_via_digid=True).count(),
            'profession_stats': db.session.query(
                User.profession, func.count(User.id)
            ).filter(User.profession.isnot(None)).group_by(User.profession).all(),
            'nationality_stats': db.session.query(
                User.nationality, func.count(User.id)
            ).filter(User.nationality.isnot(None)).group_by(User.nationality).all()
        }
        
        return render_template('admin/crm_users.html',
                             users=users,
                             professions=[p[0] for p in professions],
                             nationalities=[n[0] for n in nationalities],
                             legal_statuses=[l[0] for l in legal_statuses],
                             dutch_levels=[d[0] for d in dutch_levels],
                             english_levels=[e[0] for e in english_levels],
                             status_filter=status_filter,
                             profession_filter=profession_filter,
                             nationality_filter=nationality_filter,
                             legal_status_filter=legal_status_filter,
                             dutch_level_filter=dutch_level_filter,
                             english_level_filter=english_level_filter,
                             search_query=search_query,
                             sort_by=sort_by,
                             sort_order=sort_order,
                             stats=stats)
    
    except Exception as e:
        current_app.logger.error(f"Error in CRM users: {str(e)}")
        flash(f'Ошибка загрузки пользователей: {str(e)}', 'error')
        return render_template('admin/crm_users.html',
                             users=None, professions=[], nationalities=[], legal_statuses=[],
                             status_filter='all', profession_filter='all', nationality_filter='all',
                             legal_status_filter='all', search_query='',                              sort_by='created_at',
                             sort_order='desc', stats={})

@admin_bp.route('/crm/users/export')
@login_required
@admin_required
def crm_users_export():
    """Export users data to CSV or Excel"""
    try:
        import csv
        import io
        from flask import make_response
        
        # Get filter parameters (same as crm_users)
        status_filter = request.args.get('status', 'all')
        profession_filter = request.args.get('profession', 'all')
        nationality_filter = request.args.get('nationality', 'all')
        legal_status_filter = request.args.get('legal_status', 'all')
        dutch_level_filter = request.args.get('dutch_level', 'all')
        english_level_filter = request.args.get('english_level', 'all')
        search_query = request.args.get('search', '').strip()
        export_format = request.args.get('export', 'csv')
        user_ids = request.args.get('user_ids', '')
        
        # Build query (same logic as crm_users)
        query = User.query
        
        if user_ids:
            # Export specific users
            user_id_list = [int(id) for id in user_ids.split(',')]
            query = query.filter(User.id.in_(user_id_list))
        else:
            # Apply same filters as crm_users
            if status_filter != 'all':
                if status_filter == 'active':
                    query = query.filter_by(is_active=True)
                elif status_filter == 'inactive':
                    query = query.filter_by(is_active=False)
                elif status_filter == 'confirmed':
                    query = query.filter_by(email_confirmed=True)
                elif status_filter == 'unconfirmed':
                    query = query.filter_by(email_confirmed=False)
                elif status_filter == 'digid':
                    query = query.filter_by(created_via_digid=True)
                elif status_filter == 'regular':
                    query = query.filter_by(created_via_digid=False)
            
            if profession_filter != 'all':
                query = query.filter_by(profession=profession_filter)
            
            if nationality_filter != 'all':
                query = query.filter_by(nationality=nationality_filter)
            
            if legal_status_filter != 'all':
                query = query.filter_by(legal_status=legal_status_filter)
            
            if dutch_level_filter != 'all':
                query = query.filter_by(dutch_level=dutch_level_filter)
            
            if english_level_filter != 'all':
                query = query.filter_by(english_level=english_level_filter)
            
            if search_query:
                query = query.filter(
                    or_(
                        User.first_name.ilike(f'%{search_query}%'),
                        User.last_name.ilike(f'%{search_query}%'),
                        User.email.ilike(f'%{search_query}%'),
                        User.phone.ilike(f'%{search_query}%'),
                        User.workplace.ilike(f'%{search_query}%'),
                        User.university_name.ilike(f'%{search_query}%')
                    )
                )
        
        users = query.order_by(User.created_at.desc()).all()
        
        if export_format == 'csv':
            # Create CSV
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow([
                'ID', 'First Name', 'Last Name', 'Email', 'Phone', 'Country Code',
                'Birth Date', 'Gender', 'Nationality', 'Other Nationality',
                'Profession', 'Other Profession', 'Workplace', 'Specialization',
                'Legal Status', 'Other Legal Status', 'Dutch Level', 'English Level',
                'Program Interests', 'Required Consents', 'Optional Consents', 'Program Notifications',
                'Motivation', 'IDW Assessment', 'Big Exam Registered', 'Exam Date',
                'University Name', 'Degree Type', 'Study Start Year', 'Study End Year',
                'Study Country', 'Medical Specialization', 'Work Experience',
                'Additional Qualifications', 'Additional Education Info',
                'Email Confirmed', 'DigiD User', 'Active', 'Created At', 'Last Login'
            ])
            
            # Write data
            for user in users:
                # Parse program interests
                program_interests = ''
                if user.program_interests:
                    try:
                        import json
                        interests = json.loads(user.program_interests)
                        program_interests = ', '.join(interests) if interests else ''
                    except:
                        program_interests = user.program_interests
                
                writer.writerow([
                    user.id,
                    user.first_name or '',
                    user.last_name or '',
                    user.email or '',
                    user.phone or '',
                    user.country_code or '',
                    user.birth_date.strftime('%Y-%m-%d') if user.birth_date else '',
                    user.gender or '',
                    user.nationality or '',
                    user.other_nationality or '',
                    user.profession or '',
                    user.other_profession or '',
                    user.workplace or '',
                    user.specialization or '',
                    user.legal_status or '',
                    user.other_legal_status or '',
                    user.dutch_level or '',
                    user.english_level or '',
                    program_interests,
                    'Yes' if user.required_consents else 'No',
                    'Yes' if user.optional_consents else 'No',
                    'Yes' if user.program_notifications else 'No',
                    user.motivation or '',
                    user.idw_assessment or '',
                    user.big_exam_registered or '',
                    user.exam_date.strftime('%Y-%m-%d') if user.exam_date else '',
                    user.university_name or '',
                    user.degree_type or '',
                    user.study_start_year or '',
                    user.study_end_year or '',
                    user.study_country or '',
                    user.medical_specialization or '',
                    user.work_experience or '',
                    user.additional_qualifications or '',
                    user.additional_education_info or '',
                    'Yes' if user.email_confirmed else 'No',
                    'Yes' if user.created_via_digid else 'No',
                    'Yes' if user.is_active else 'No',
                    user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else '',
                    user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else ''
                ])
            
            # Create response
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename=mentora_users_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            return response
        
        elif export_format == 'excel':
            # For Excel export, we would need openpyxl or xlsxwriter
            # For now, return CSV with Excel extension
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Same logic as CSV but with Excel extension
            writer.writerow([
                'ID', 'First Name', 'Last Name', 'Email', 'Phone', 'Country Code',
                'Birth Date', 'Gender', 'Nationality', 'Other Nationality',
                'Profession', 'Other Profession', 'Workplace', 'Specialization',
                'Legal Status', 'Other Legal Status', 'Dutch Level', 'English Level',
                'University Name', 'Degree Type', 'Study Start Year', 'Study End Year',
                'Study Country', 'Medical Specialization', 'Work Experience',
                'Additional Qualifications', 'Additional Education Info',
                'Email Confirmed', 'DigiD User', 'Active', 'Created At', 'Last Login'
            ])
            
            for user in users:
                writer.writerow([
                    user.id,
                    user.first_name or '',
                    user.last_name or '',
                    user.email or '',
                    user.phone or '',
                    user.country_code or '',
                    user.birth_date.strftime('%Y-%m-%d') if user.birth_date else '',
                    user.gender or '',
                    user.nationality or '',
                    user.other_nationality or '',
                    user.profession or '',
                    user.other_profession or '',
                    user.workplace or '',
                    user.specialization or '',
                    user.legal_status or '',
                    user.other_legal_status or '',
                    user.dutch_level or '',
                    user.english_level or '',
                    user.university_name or '',
                    user.degree_type or '',
                    user.study_start_year or '',
                    user.study_end_year or '',
                    user.study_country or '',
                    user.medical_specialization or '',
                    user.work_experience or '',
                    user.additional_qualifications or '',
                    user.additional_education_info or '',
                    'Yes' if user.email_confirmed else 'No',
                    'Yes' if user.created_via_digid else 'No',
                    'Yes' if user.is_active else 'No',
                    user.created_at.strftime('%Y-%m-%d %H:%M:%S') if user.created_at else '',
                    user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else ''
                ])
            
            response = make_response(output.getvalue())
            response.headers['Content-Type'] = 'text/csv'
            response.headers['Content-Disposition'] = f'attachment; filename=mentora_users_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            return response
        
        else:
            flash('Invalid export format', 'error')
            return redirect(url_for('admin.crm_users'))
    
    except Exception as e:
        current_app.logger.error(f"Error exporting users: {str(e)}")
        flash(f'Error exporting users: {str(e)}', 'error')
        return redirect(url_for('admin.crm_users'))

@admin_bp.route('/crm/users/<int:user_id>/details')
@login_required
@admin_required
def crm_user_details(user_id):
    """Get user details for modal"""
    try:
        user = User.query.get_or_404(user_id)
        return render_template('admin/crm_user_details.html', user=user)
    except Exception as e:
        current_app.logger.error(f"Error loading user details: {str(e)}")
        return f"Error loading user details: {str(e)}", 500

@admin_bp.route('/crm/users/send-email', methods=['POST'])
@login_required
@admin_required
def crm_users_send_email():
    """Send email to users"""
    try:
        data = request.get_json()
        subject = data.get('subject')
        message = data.get('message')
        user_id = data.get('user_id')
        user_ids = data.get('user_ids')
        
        if not subject or not message:
            return jsonify({'success': False, 'error': 'Subject and message are required'})
        
        # Get users to send email to
        if user_id:
            users = [User.query.get(user_id)]
        elif user_ids:
            user_id_list = [int(id) for id in user_ids.split(',')]
            users = User.query.filter(User.id.in_(user_id_list)).all()
        else:
            return jsonify({'success': False, 'error': 'No users specified'})
        
        # Send emails using admin email service
        from utils.admin_email_service import send_bulk_admin_emails
        
        result = send_bulk_admin_emails(users, subject, message, 'custom')
        sent_count = result['sent']
        
        if result['errors']:
            current_app.logger.warning(f"Some emails failed to send: {result['errors']}")
        
        return jsonify({
            'success': True, 
            'message': f'Email sent to {sent_count} users',
            'sent_count': sent_count
        })
    
    except Exception as e:
        current_app.logger.error(f"Error sending emails: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@admin_bp.route('/virtual-patients')
@login_required
@admin_required
def virtual_patients():
    """Управление виртуальными пациентами"""
    try:
        scenarios = VirtualPatientScenario.query.order_by(VirtualPatientScenario.created_at.desc()).all()
        
        # Добавляем статистику по каждому сценарию
        scenarios_with_stats = []
        for scenario in scenarios:
            try:
                attempts_count = VirtualPatientAttempt.query.filter_by(scenario_id=scenario.id).count()
            except Exception as e:
                current_app.logger.error(f"Error counting attempts for scenario {scenario.id}: {str(e)}")
                attempts_count = 0
            
            try:
                completed_count = VirtualPatientAttempt.query.filter_by(scenario_id=scenario.id, completed=True).count()
            except Exception as e:
                current_app.logger.error(f"Error counting completed attempts for scenario {scenario.id}: {str(e)}")
                completed_count = 0
            
            try:
                avg_score = db.session.query(db.func.avg(VirtualPatientAttempt.score)).filter_by(
                    scenario_id=scenario.id, completed=True
                ).scalar() or 0
            except Exception as e:
                current_app.logger.error(f"Error calculating avg score for scenario {scenario.id}: {str(e)}")
                avg_score = 0
            
            scenarios_with_stats.append({
                'scenario': scenario,
                'attempts_count': attempts_count,
                'completed_count': completed_count,
                'avg_score': round(avg_score, 1)
            })
        
        return render_template('admin/virtual_patients.html', scenarios=scenarios_with_stats)
    
    except Exception as e:
        current_app.logger.error(f"Error in virtual_patients route: {str(e)}")
        flash(f'Ошибка загрузки виртуальных пациентов: {str(e)}', 'error')
        
        # Return empty data in case of error
        return render_template('admin/virtual_patients.html', scenarios=[])

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
            # Note: StudySession model not imported, using alternative approach
            # study_sessions = StudySession.query.limit(50).all()
            study_sessions = []  # Placeholder until StudySession is properly imported
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

# ========================================
# ENHANCED USER MANAGEMENT ROUTES
# ========================================

@admin_bp.route('/users/list', methods=['GET', 'POST'])
@login_required
@admin_required
def users_list():
    """Enhanced users list with filters and pagination"""
    # Handle POST request for creating new user
    if request.method == 'POST':
        try:
            first_name = request.form.get('first_name')
            last_name = request.form.get('last_name')
            email = request.form.get('email')
            password = request.form.get('password')
            role = request.form.get('role', 'user')
            
            # Validate required fields
            if not all([first_name, last_name, email, password]):
                flash('Все поля обязательны для заполнения', 'error')
                return redirect(url_for('admin.users_list'))
            
            # Check if user with this email already exists
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash('Пользователь с таким email уже существует', 'error')
                return redirect(url_for('admin.users_list'))
            
            # Create new user
            from werkzeug.security import generate_password_hash
            new_user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password_hash=generate_password_hash(password),
                role=role,
                is_active=True,
                email_confirmed=False
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            flash(f'Пользователь {first_name} {last_name} успешно создан', 'success')
            return redirect(url_for('admin.users_list'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating user: {str(e)}")
            flash(f'Ошибка при создании пользователя: {str(e)}', 'error')
            return redirect(url_for('admin.users_list'))
    
    # Handle GET request - show users list
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        status_filter = request.args.get('status', 'all')
        role_filter = request.args.get('role', 'all')
        consent_filter = request.args.get('consent_filter', 'all')
        sort_by = request.args.get('sort', 'created_at')
        sort_order = request.args.get('order', 'desc')
        
        # Base query - по умолчанию исключаем удаленных пользователей
        query = User.query.filter(User.is_deleted == False)
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term),
                    User.email.ilike(search_term),
                    User.username.ilike(search_term)
                )
            )
        
        # Apply status filter
        if status_filter != 'all':
            if status_filter == 'active':
                query = query.filter(User.is_active == True)
            elif status_filter == 'inactive':
                query = query.filter(User.is_active == False)
            elif status_filter == 'email_verified':
                query = query.filter(User.email_confirmed == True)
            elif status_filter == 'email_unverified':
                query = query.filter(User.email_confirmed == False)
            elif status_filter == 'digid':
                query = query.filter(User.created_via_digid == True)
        
        # Apply role filter
        if role_filter != 'all':
            query = query.filter(User.role == role_filter)
        
        # Apply consent filter
        if consent_filter != 'all':
            if consent_filter == 'required_yes':
                query = query.filter(User.required_consents == True)
            elif consent_filter == 'required_no':
                query = query.filter(User.required_consents == False)
            elif consent_filter == 'marketing_yes':
                query = query.filter(User.optional_consents == True)
            elif consent_filter == 'marketing_no':
                query = query.filter(User.optional_consents == False)
        
        # Apply sorting
        if sort_by == 'name':
            order_col = User.first_name
        elif sort_by == 'email':
            order_col = User.email
        elif sort_by == 'last_login':
            order_col = User.last_login
        elif sort_by == 'created_at':
            order_col = User.created_at
        else:
            order_col = User.created_at
        
        if sort_order == 'desc':
            order_col = order_col.desc()
        
        query = query.order_by(order_col)
        
        # Paginate
        try:
            users = query.paginate(
                page=page, per_page=per_page, error_out=False
            )
        except Exception as e:
            current_app.logger.error(f"Error paginating users: {str(e)}")
            users = None
        
        # Get statistics with error handling
        stats = {
            'total_users': 0,
            'active_users': 0,
            'admin_users': 0,
            'digid_users': 0,
            'online_users': 0,
            'inactive_users': 0
        }
        
        try:
            stats['total_users'] = User.query.count()
        except Exception as e:
            current_app.logger.error(f"Error counting total users: {str(e)}")
        
        try:
            stats['active_users'] = User.query.filter(User.is_active == True).count()
        except Exception as e:
            current_app.logger.error(f"Error counting active users: {str(e)}")
        
        try:
            stats['admin_users'] = User.query.filter(User.role == 'admin').count()
        except Exception as e:
            current_app.logger.error(f"Error counting admin users: {str(e)}")
        
        try:
            stats['digid_users'] = User.query.filter(User.created_via_digid == True).count()
        except Exception as e:
            current_app.logger.error(f"Error counting digid users: {str(e)}")
        
        try:
            online_threshold = datetime.now(timezone.utc) - timedelta(minutes=5)
            stats['online_users'] = User.query.filter(User.last_login >= online_threshold).count()
        except Exception as e:
            current_app.logger.error(f"Error counting online users: {str(e)}")
        
        stats['inactive_users'] = stats['total_users'] - stats['active_users']
        
        return render_template('admin/users_list.html',
                             users=users,
                             stats=stats,
                             search=search,
                             status_filter=status_filter,
                             role_filter=role_filter,
                             consent_filter=consent_filter,
                             sort_by=sort_by,
                             sort_order=sort_order,
                             error_message=None)
    
    except Exception as e:
        current_app.logger.error(f"Error in users_list route: {str(e)}")
        flash(f'Ошибка загрузки списка пользователей: {str(e)}', 'error')
        
        # Return empty data in case of error
        return render_template('admin/users_list.html',
                             users=None,
                             stats={
                                 'total_users': 0,
                                 'active_users': 0,
                                 'admin_users': 0,
                                 'digid_users': 0,
                                 'online_users': 0,
                                 'inactive_users': 0
                             },
                             search='',
                             status_filter='all',
                             role_filter='all',
                             consent_filter='all',
                             sort_by='created_at',
                             sort_order='desc',
                             error_message=str(e))

@admin_bp.route('/users/<int:user_id>')
@login_required
@admin_required
def user_detail(user_id):
    """Detailed user profile for admin"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Initialize default values
        stats = {}
        recent_activity = []
        progress_summary = {}
        login_history = []
        recent_visits = []
        audit_logs = []
        is_online = False
        
        # Get user statistics with error handling
        try:
            stats = user.get_dashboard_stats()
        except Exception as e:
            current_app.logger.error(f"Error getting dashboard stats for user {user_id}: {str(e)}")
            stats = {
                'total_sessions': 0,
                'completed_tests': 0,
                'average_score': 0,
                'last_activity': None
            }
        
        # Get recent activity with error handling
        try:
            recent_activity = user.get_recent_activity(days=30)
        except Exception as e:
            current_app.logger.error(f"Error getting recent activity for user {user_id}: {str(e)}")
            recent_activity = []
        
        # Get progress summary with error handling
        try:
            progress_summary = user.get_progress_stats()
        except Exception as e:
            current_app.logger.error(f"Error getting progress stats for user {user_id}: {str(e)}")
            progress_summary = {
                'total_progress': 0,
                'completed_modules': 0,
                'total_modules': 0
            }
        
        # Get login history with error handling
        try:
            login_history = UserSession.query.filter_by(user_id=user_id).order_by(
                UserSession.started_at.desc()
            ).limit(10).all()
        except Exception as e:
            current_app.logger.error(f"Error getting login history for user {user_id}: {str(e)}")
            login_history = []
        
        # Get website visits with error handling
        try:
            recent_visits = WebsiteVisit.query.filter_by(user_id=user_id).order_by(
                WebsiteVisit.created_at.desc()
            ).limit(20).all()
        except Exception as e:
            current_app.logger.error(f"Error getting recent visits for user {user_id}: {str(e)}")
            recent_visits = []
        
        # Get audit logs with error handling
        try:
            audit_logs = ProfileAuditLog.query.filter_by(user_id=user_id).order_by(
                ProfileAuditLog.created_at.desc()
            ).limit(20).all()
        except Exception as e:
            current_app.logger.error(f"Error getting audit logs for user {user_id}: {str(e)}")
            audit_logs = []
        
        # Check if user is currently online with error handling
        try:
            online_threshold = datetime.now(timezone.utc) - timedelta(minutes=5)
            if user.last_login:
                # Ensure both datetimes are timezone-aware
                if user.last_login.tzinfo is None:
                    # If last_login is naive, assume it's UTC
                    last_login_aware = user.last_login.replace(tzinfo=timezone.utc)
                else:
                    last_login_aware = user.last_login
                is_online = last_login_aware >= online_threshold
            else:
                is_online = False
        except Exception as e:
            current_app.logger.error(f"Error checking online status for user {user_id}: {str(e)}")
            is_online = False
        
        return render_template('admin/user_detail.html',
                             user=user,
                             stats=stats,
                             recent_activity=recent_activity,
                             progress_summary=progress_summary,
                             login_history=login_history,
                             recent_visits=recent_visits,
                             audit_logs=audit_logs,
                             is_online=is_online)
    
    except Exception as e:
        current_app.logger.error(f"Error in user_detail route for user {user_id}: {str(e)}")
        flash(f'Ошибка загрузки профиля пользователя: {str(e)}', 'error')
        
        # Try to get basic user info for error page
        try:
            user = User.query.get(user_id)
            if user:
                return render_template('admin/user_detail.html',
                                     user=user,
                                     stats={},
                                     recent_activity=[],
                                     progress_summary={},
                                     login_history=[],
                                     recent_visits=[],
                                     audit_logs=[],
                                     is_online=False,
                                     error_message=str(e))
            else:
                flash('Пользователь не найден', 'error')
                return redirect(url_for('admin.users_list'))
        except Exception as e2:
            current_app.logger.error(f"Error in error handling for user {user_id}: {str(e2)}")
            flash('Критическая ошибка при загрузке пользователя', 'error')
            return redirect(url_for('admin.users_list'))

@admin_bp.route('/users/<int:user_id>/extended')
@login_required
@admin_required
def user_detail_extended(user_id):
    """Extended user profile with ALL registration fields"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Check if user is currently online (fix timezone issue)
        is_online = False
        try:
            if user.last_login:
                # Make both datetimes timezone-aware for comparison
                now_utc = datetime.now(timezone.utc)
                
                # If last_login is naive, assume it's UTC
                if user.last_login.tzinfo is None:
                    last_login_utc = user.last_login.replace(tzinfo=timezone.utc)
                else:
                    last_login_utc = user.last_login
                
                online_threshold = now_utc - timedelta(minutes=5)
                # Ensure both datetimes are timezone-aware for comparison
                if last_login_utc and last_login_utc.tzinfo is None:
                    last_login_utc = last_login_utc.replace(tzinfo=timezone.utc)
                is_online = last_login_utc and last_login_utc >= online_threshold
        except Exception as tz_error:
            current_app.logger.warning(f"Error checking online status for user {user_id}: {str(tz_error)}")
            is_online = False
        
        return render_template('admin/user_detail_extended.html',
                             user=user,
                             is_online=is_online)
    
    except Exception as e:
        current_app.logger.error(f"Error in user_detail_extended route for user {user_id}: {str(e)}")
        flash(f'Ошибка загрузки расширенной информации о пользователе: {str(e)}', 'error')
        return redirect(url_for('admin.user_detail', user_id=user_id))

@admin_bp.route('/users/<int:user_id>/learning-progress')
@login_required
@admin_required
def user_learning_progress(user_id):
    """Детальный прогресс обучения пользователя"""
    try:
        user = User.query.get_or_404(user_id)
        
        # 1. Диагностические сессии
        diagnostic_sessions = DiagnosticSession.query.filter_by(
            user_id=user_id
        ).order_by(DiagnosticSession.started_at.desc()).limit(50).all()
        
        diagnostic_stats = {
            'total': DiagnosticSession.query.filter_by(user_id=user_id).count(),
            'completed': DiagnosticSession.query.filter(
                DiagnosticSession.user_id == user_id,
                DiagnosticSession.completed_at.isnot(None)
            ).count(),
            'by_type': {}
        }
        
        # Статистика по типам диагностик
        for session_type in ['quick_30', 'full_60', 'express', 'preliminary', 'readiness', 'full', 'comprehensive']:
            count = DiagnosticSession.query.filter_by(
                user_id=user_id,
                session_type=session_type
            ).count()
            if count > 0:
                diagnostic_stats['by_type'][session_type] = count
        
        # Последняя диагностика
        last_diagnostic = DiagnosticSession.query.filter(
            DiagnosticSession.user_id == user_id,
            DiagnosticSession.completed_at.isnot(None)
        ).order_by(DiagnosticSession.completed_at.desc()).first()
        
        # 2. Термины (Flashcards)
        terms_stats = {
            'total_studied': UserTermProgress.query.filter_by(user_id=user_id).count(),
            'total_terms': MedicalTerm.query.count(),
            'due_reviews': UserTermProgress.query.filter(
                UserTermProgress.user_id == user_id,
                UserTermProgress.next_review <= datetime.now(timezone.utc)
            ).count(),
            'mastered': UserItemMastery.query.filter_by(
                user_id=user_id,
                item_type='term'
            ).filter(UserItemMastery.mastered_at.isnot(None)).count(),
            'by_category': {}
        }
        
        # Статистика по категориям терминов
        category_stats = db.session.query(
            MedicalTerm.category,
            func.count(UserTermProgress.id).label('count')
        ).join(
            UserTermProgress, MedicalTerm.id == UserTermProgress.term_id
        ).filter(
            UserTermProgress.user_id == user_id
        ).group_by(MedicalTerm.category).all()
        
        for category, count in category_stats:
            terms_stats['by_category'][category or 'uncategorized'] = count
        
        # Время на флешкарты
        total_flashcard_time = db.session.query(
            func.sum(DailyFlashcardProgress.time_spent)
        ).filter_by(user_id=user_id).scalar() or 0
        
        # 3. Английское чтение
        english_stats = {
            'total_passages': EnglishPassage.query.count(),
            'completed': UserEnglishProgress.query.filter_by(user_id=user_id).count(),
            'mastered': UserItemMastery.query.filter_by(
                user_id=user_id,
                item_type='english'
            ).filter(UserItemMastery.mastered_at.isnot(None)).count(),
            'average_score': 0,
            'passages': []
        }
        
        # Прогресс по текстам
        english_progress = UserEnglishProgress.query.filter_by(
            user_id=user_id
        ).order_by(UserEnglishProgress.completed_at.desc()).limit(20).all()
        
        total_score = 0
        completed_count = 0
        for progress in english_progress:
            passage = EnglishPassage.query.get(progress.passage_id)
            if passage:
                # UserEnglishProgress использует поле 'score' (количество правильных ответов), а не 'correct_answers'
                # score уже содержит количество правильных ответов, нужно вычислить процент
                if progress.total_questions and progress.total_questions > 0:
                    score_percent = (progress.score / progress.total_questions * 100) if progress.score else 0
                else:
                    score_percent = 0
                total_score += score_percent
                completed_count += 1
                english_stats['passages'].append({
                    'passage': passage,
                    'progress': progress,
                    'score': round(score_percent, 1)
                })
        
        if completed_count > 0:
            english_stats['average_score'] = round(total_score / completed_count, 1)
        
        # 4. Виртуальные пациенты
        vp_stats = {
            'total_scenarios': VirtualPatientScenario.query.count(),
            'attempts': VirtualPatientAttempt.query.filter_by(user_id=user_id).count(),
            'completed': VirtualPatientAttempt.query.filter_by(
                user_id=user_id,
                completed=True
            ).count(),
            'mastered': UserItemMastery.query.filter_by(
                user_id=user_id,
                item_type='virtual_patient'
            ).filter(UserItemMastery.mastered_at.isnot(None)).count(),
            'average_score': 0,
            'scenarios': []
        }
        
        # Прогресс по сценариям
        vp_attempts = VirtualPatientAttempt.query.filter_by(
            user_id=user_id
        ).order_by(VirtualPatientAttempt.completed_at.desc()).limit(20).all()
        
        total_vp_score = 0
        completed_vp_count = 0
        for attempt in vp_attempts:
            scenario = VirtualPatientScenario.query.get(attempt.scenario_id)
            if scenario and attempt.completed:
                # VirtualPatientAttempt имеет свойство percentage_score
                score = attempt.percentage_score if hasattr(attempt, 'percentage_score') else 0
                total_vp_score += score
                completed_vp_count += 1
                vp_stats['scenarios'].append({
                    'scenario': scenario,
                    'attempt': attempt,
                    'score': round(score, 1)
                })
        
        if completed_vp_count > 0:
            vp_stats['average_score'] = round(total_vp_score / completed_vp_count, 1)
        
        # 5. Мастерство (UserItemMastery)
        mastery_stats = {
            'total_items': UserItemMastery.query.filter_by(user_id=user_id).count(),
            'mastered_items': UserItemMastery.query.filter_by(
                user_id=user_id
            ).filter(UserItemMastery.mastered_at.isnot(None)).count(),
            'by_type': {}
        }
        
        # Статистика по типам элементов
        for item_type in ['question', 'term', 'english', 'virtual_patient']:
            total = UserItemMastery.query.filter_by(
                user_id=user_id,
                item_type=item_type
            ).count()
            mastered = UserItemMastery.query.filter_by(
                user_id=user_id,
                item_type=item_type
            ).filter(UserItemMastery.mastered_at.isnot(None)).count()
            
            if total > 0:
                mastery_stats['by_type'][item_type] = {
                    'total': total,
                    'mastered': mastered,
                    'percentage': round((mastered / total) * 100, 1) if total > 0 else 0
                }
        
        # 6. Тесты (TestAttempt)
        # TestAttempt не имеет поля completed_at, используем attempt_date
        test_attempts = TestAttempt.query.filter_by(
            user_id=user_id
        ).order_by(TestAttempt.attempt_date.desc()).limit(50).all()
        
        # TestAttempt не имеет полей completed и score, считаем только общее количество
        test_stats = {
            'total': TestAttempt.query.filter_by(user_id=user_id).count(),
            'completed': TestAttempt.query.filter_by(user_id=user_id).count(),  # Все попытки считаются завершенными
            'average_score': 0
        }
        
        # Подсчитываем правильные ответы
        correct_answers = TestAttempt.query.filter_by(
            user_id=user_id,
            is_correct=True
        ).count()
        
        total_attempts = test_stats['total']
        if total_attempts > 0:
            test_stats['average_score'] = round((correct_answers / total_attempts) * 100, 1)
        
        return render_template('admin/user_learning_progress.html',
                             user=user,
                             diagnostic_sessions=diagnostic_sessions,
                             diagnostic_stats=diagnostic_stats,
                             last_diagnostic=last_diagnostic,
                             terms_stats=terms_stats,
                             total_flashcard_time=total_flashcard_time,
                             english_stats=english_stats,
                             vp_stats=vp_stats,
                             mastery_stats=mastery_stats,
                             test_attempts=test_attempts,
                             test_stats=test_stats)
    
    except Exception as e:
        current_app.logger.error(f"Error in user_learning_progress route for user {user_id}: {str(e)}", exc_info=True)
        flash(f'Ошибка загрузки прогресса обучения: {str(e)}', 'error')
        return redirect(url_for('admin.user_detail', user_id=user_id))

@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_user(user_id):
    """Edit user profile (admin only)"""
    user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        try:
            # Get old values for audit log
            old_values = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active,
                'profession': user.profession,
                'language': user.language
            }
            
            # Update user fields
            user.first_name = request.form.get('first_name', '').strip()
            user.last_name = request.form.get('last_name', '').strip()
            user.email = request.form.get('email', '').strip()
            user.role = request.form.get('role', 'user')
            user.is_active = 'is_active' in request.form
            user.profession = request.form.get('profession', '')
            user.language = request.form.get('language', 'nl')
            user.phone = request.form.get('phone', '')
            user.workplace = request.form.get('workplace', '')
            
            # Log changes
            for field, old_value in old_values.items():
                new_value = getattr(user, field)
                if old_value != new_value:
                    try:
                        if hasattr(user, 'log_profile_change'):
                            user.log_profile_change(
                                field=field,
                                old_value=old_value,
                                new_value=new_value,
                                changed_by=current_user.id
                            )
                    except Exception as log_error:
                        # Don't fail the main operation if logging fails
                        print(f"Warning: Failed to log profile change: {log_error}")
            
            user.profile_updated_at = datetime.now(timezone.utc)
            db.session.commit()
            
            # Send welcome email if user was activated
            if user.is_active and not old_values.get('is_active', False):
                try:
                    from utils.email_service import send_welcome_email
                    send_welcome_email(user)
                    current_app.logger.info(f"Welcome email sent to activated user: {user.email}")
                    flash('Профиль пользователя успешно обновлен. Welcome email отправлен.', 'success')
                except Exception as email_error:
                    current_app.logger.warning(f"Failed to send welcome email to {user.email}: {str(email_error)}")
                    flash(f'Профиль пользователя успешно обновлен. Ошибка отправки welcome email: {str(email_error)}', 'warning')
            else:
                flash('Профиль пользователя успешно обновлен', 'success')
            
            return redirect(url_for('admin.user_detail', user_id=user_id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка при обновлении профиля: {str(e)}', 'danger')
    
    return render_template('admin/edit_user.html', user=user)

@admin_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
@login_required
@admin_required
def reset_user_password(user_id):
    """Reset user password (admin only)"""
    user = User.query.get_or_404(user_id)
    
    if user.created_via_digid:
        flash('Нельзя сбросить пароль для пользователей DigiD', 'warning')
        return redirect(url_for('admin.user_detail', user_id=user_id))
    
    try:
        # Generate new temporary password
        import secrets
        import string
        temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        
        # Update password
        user.set_password(temp_password)
        
        # Clear any existing reset tokens
        user.password_reset_token = None
        user.password_reset_sent_at = None
        
        # Log the password reset
        try:
            if hasattr(user, 'log_profile_change'):
                user.log_profile_change(
                    field='password',
                    old_value='[HIDDEN]',
                    new_value='[RESET BY ADMIN]',
                    changed_by=current_user.id
                )
        except Exception as log_error:
            print(f"Warning: Failed to log password reset: {log_error}")
        
        db.session.commit()
        
        # Отправляем email с новым паролем
        from utils.admin_email_service import send_password_reset_email
        
        email_sent = send_password_reset_email(user, temp_password)
        
        if email_sent:
            flash(f'Пароль сброшен и отправлен на {user.email}', 'success')
        else:
            flash(f'Пароль сброшен: {temp_password} (ошибка отправки email)', 'warning')
        
        return redirect(url_for('admin.user_detail', user_id=user_id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при сбросе пароля: {str(e)}', 'danger')
        return redirect(url_for('admin.user_detail', user_id=user_id))

@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    """Toggle user active status"""
    user = User.query.get_or_404(user_id)
    
    # Prevent deactivating yourself
    if user.id == current_user.id:
        flash('Нельзя деактивировать собственный аккаунт', 'warning')
        return redirect(url_for('admin.user_detail', user_id=user_id))
    
    try:
        old_status = user.is_active
        user.is_active = not user.is_active
        
        # Log the status change
        try:
            if hasattr(user, 'log_profile_change'):
                user.log_profile_change(
                    field='is_active',
                    old_value=old_status,
                    new_value=user.is_active,
                    changed_by=current_user.id
                )
        except Exception as log_error:
            print(f"Warning: Failed to log status change: {log_error}")
        
        db.session.commit()
        
        status_text = 'активирован' if user.is_active else 'деактивирован'
        
        # Send welcome email if user was activated
        if user.is_active and not old_status:
            try:
                from utils.email_service import send_welcome_email
                send_welcome_email(user)
                current_app.logger.info(f"Welcome email sent to activated user: {user.email}")
                flash(f'Пользователь {status_text}. Welcome email отправлен.', 'success')
            except Exception as email_error:
                current_app.logger.warning(f"Failed to send welcome email to {user.email}: {str(email_error)}")
                flash(f'Пользователь {status_text}. Ошибка отправки welcome email: {str(email_error)}', 'warning')
        else:
            flash(f'Пользователь {status_text}', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при изменении статуса: {str(e)}', 'danger')
    
    return redirect(url_for('admin.user_detail', user_id=user_id))

@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete user (admin only)"""
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting yourself
    if user.id == current_user.id:
        flash('Нельзя удалить собственный аккаунт', 'danger')
        return redirect(url_for('admin.user_detail', user_id=user_id))
    
    # Prevent deleting other admins without confirmation
    if user.is_admin:
        confirm = request.form.get('confirm_admin_delete')
        if not confirm:
            flash('Для удаления администратора требуется подтверждение', 'warning')
            return redirect(url_for('admin.user_detail', user_id=user_id))
    
    try:
        from models import DailyAssignment
        
        user_email = user.email
        
        # Явно удаляем daily_assignments перед удалением пользователя
        # (хотя есть CASCADE, но лучше быть явным для избежания ошибок)
        daily_assignments = DailyAssignment.query.filter_by(user_id=user_id).all()
        if daily_assignments:
            for assignment in daily_assignments:
                db.session.delete(assignment)
            current_app.logger.info(f"Deleted {len(daily_assignments)} daily assignments for user {user_id}")
        
        # Теперь удаляем пользователя
        db.session.delete(user)
        db.session.commit()
        
        flash(f'Пользователь {user_email} удален', 'success')
        return redirect(url_for('admin.users_list'))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting user {user_id}: {str(e)}")
        flash(f'Ошибка при удалении пользователя: {str(e)}', 'danger')
        return redirect(url_for('admin.user_detail', user_id=user_id))

@admin_bp.route('/users/bulk-actions', methods=['POST'])
@login_required
@admin_required
def bulk_user_actions():
    """Bulk actions on users"""
    print(f"=== BULK ACTIONS DEBUG ===")
    print(f"Form data: {request.form}")
    print(f"Action: {request.form.get('action')}")
    print(f"User IDs: {request.form.getlist('user_ids')}")
    
    action = request.form.get('action')
    user_ids = request.form.getlist('user_ids')
    
    if not user_ids:
        print("=== NO USER IDS SELECTED ===")
        flash('Не выбраны пользователи', 'warning')
        return redirect(url_for('admin.users_list'))
    
    user_ids = [int(uid) for uid in user_ids if uid.isdigit()]
    
    # Prevent actions on yourself
    if current_user.id in user_ids:
        user_ids.remove(current_user.id)
        flash('Действие не может быть применено к вашему аккаунту', 'warning')
    
    if not user_ids:
        return redirect(url_for('admin.users_list'))
    
    try:
        if action == 'activate':
            # Get users before activation for email sending
            users_to_activate = User.query.filter(User.id.in_(user_ids)).all()
            
            # Activate users
            User.query.filter(User.id.in_(user_ids)).update({'is_active': True})
            db.session.commit()
            
            # Send welcome emails to activated users
            welcome_emails_sent = 0
            for user in users_to_activate:
                try:
                    from utils.email_service import send_welcome_email
                    send_welcome_email(user)
                    welcome_emails_sent += 1
                    current_app.logger.info(f"Welcome email sent to activated user: {user.email}")
                except Exception as email_error:
                    current_app.logger.warning(f"Failed to send welcome email to {user.email}: {str(email_error)}")
            
            flash(f'Активировано пользователей: {len(user_ids)}. Отправлено welcome emails: {welcome_emails_sent}', 'success')
            
        elif action == 'deactivate':
            User.query.filter(User.id.in_(user_ids)).update({'is_active': False})
            flash(f'Деактивировано пользователей: {len(user_ids)}', 'success')
            
        elif action == 'delete':
            # Additional safety check - prevent deleting admins without confirmation
            admin_users = User.query.filter(User.id.in_(user_ids), User.is_admin == True).all()
            if admin_users:
                flash('Нельзя удалить администраторов через массовые действия. Удаляйте их по одному.', 'danger')
                return redirect(url_for('admin.users_list'))
            
            # Get user emails for logging before deletion
            users_to_delete = User.query.filter(User.id.in_(user_ids)).all()
            user_emails = [user.email for user in users_to_delete]
            
            # Delete users
            User.query.filter(User.id.in_(user_ids)).delete()
            flash(f'Удалено пользователей: {len(user_ids)}', 'success')
            
            # Log the action
            current_app.logger.info(f"Admin {current_user.email} bulk deleted users: {user_emails}")
            
        elif action == 'make_admin':
            User.query.filter(User.id.in_(user_ids)).update({'role': 'admin'})
            flash(f'Назначено администраторами: {len(user_ids)}', 'success')
            
        elif action == 'make_user':
            User.query.filter(User.id.in_(user_ids)).update({'role': 'user'})
            flash(f'Понижены до обычных пользователей: {len(user_ids)}', 'success')
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при выполнении массового действия: {str(e)}', 'danger')
    
    return redirect(url_for('admin.users_list'))

# ========================================
# ONLINE USERS AND ANALYTICS
# ========================================

@admin_bp.route('/users/online')
@login_required
@admin_required
def online_users():
    """Show currently online users"""
    try:
        # Users active in the last 5 minutes
        online_threshold = datetime.now(timezone.utc) - timedelta(minutes=5)
        
        # Initialize empty lists in case of errors
        online_users = []
        active_sessions = []
        recent_visits = []
        
        try:
            online_users = User.query.filter(
                User.last_login >= online_threshold,
                User.is_active == True
            ).order_by(User.last_login.desc()).all()
        except Exception as e:
            current_app.logger.error(f"Error fetching online users: {str(e)}")
            online_users = []
        
        try:
            # Get active sessions
            active_sessions = UserSession.query.filter(
                UserSession.is_active == True,
                UserSession.last_activity >= online_threshold
            ).order_by(UserSession.last_activity.desc()).all()
        except Exception as e:
            current_app.logger.error(f"Error fetching active sessions: {str(e)}")
            active_sessions = []
        
        try:
            # Get current page views
            recent_visits = WebsiteVisit.query.filter(
                WebsiteVisit.created_at >= online_threshold
            ).order_by(WebsiteVisit.created_at.desc()).limit(50).all()
        except Exception as e:
            current_app.logger.error(f"Error fetching recent visits: {str(e)}")
            recent_visits = []
        
        # Statistics
        stats = {
            'online_users': len(online_users),
            'active_sessions': len(active_sessions),
            'recent_page_views': len(recent_visits),
            'unique_visitors': len(set(visit.ip_address for visit in recent_visits if visit.ip_address))
        }
        
        return render_template('admin/online_users.html',
                             online_users=online_users,
                             active_sessions=active_sessions,
                             recent_visits=recent_visits,
                             stats=stats)
    
    except Exception as e:
        current_app.logger.error(f"Error in online_users route: {str(e)}")
        flash(f'Ошибка загрузки данных: {str(e)}', 'error')
        
        # Return empty data in case of error
        return render_template('admin/online_users.html',
                             online_users=[],
                             active_sessions=[],
                             recent_visits=[],
                             stats={
                                 'online_users': 0,
                                 'active_sessions': 0,
                                 'recent_page_views': 0,
                                 'unique_visitors': 0
                             })

@admin_bp.route('/analytics/visitors')
@login_required
@admin_required
def visitors_analytics():
    """Detailed visitor analytics"""
    try:
        # Time filters
        time_filter = request.args.get('timeframe', '24h')
        
        if time_filter == '24h':
            start_time = datetime.now(timezone.utc) - timedelta(hours=24)
        elif time_filter == '7d':
            start_time = datetime.now(timezone.utc) - timedelta(days=7)
        elif time_filter == '30d':
            start_time = datetime.now(timezone.utc) - timedelta(days=30)
        else:
            start_time = datetime.now(timezone.utc) - timedelta(hours=24)
        
        # Initialize default values
        total_visits = 0
        unique_visitors = 0
        registered_user_visits = 0
        popular_pages = []
        countries = []
        
        # Get visit statistics with error handling
        try:
            total_visits = WebsiteVisit.query.filter(
                WebsiteVisit.created_at >= start_time
            ).count()
        except Exception as e:
            current_app.logger.error(f"Error counting total visits: {str(e)}")
        
        try:
            unique_visitors = db.session.query(WebsiteVisit.ip_address).filter(
                WebsiteVisit.created_at >= start_time
            ).distinct().count()
        except Exception as e:
            current_app.logger.error(f"Error counting unique visitors: {str(e)}")
        
        try:
            registered_user_visits = WebsiteVisit.query.filter(
                WebsiteVisit.created_at >= start_time,
                WebsiteVisit.user_id.isnot(None)
            ).count()
        except Exception as e:
            current_app.logger.error(f"Error counting registered user visits: {str(e)}")
        
        # Popular pages with error handling
        try:
            popular_pages_raw = db.session.query(
                WebsiteVisit.page_url,
                func.count(WebsiteVisit.id).label('visits'),
                func.count(func.distinct(WebsiteVisit.ip_address)).label('unique_visitors')
            ).filter(
                WebsiteVisit.created_at >= start_time
            ).group_by(WebsiteVisit.page_url).order_by(
                func.count(WebsiteVisit.id).desc()
            ).limit(10).all()
            
            # Convert Row objects to dictionaries
            popular_pages = []
            for page in popular_pages_raw:
                popular_pages.append({
                    'page_url': page.page_url,
                    'visits': page.visits,
                    'unique_visitors': page.unique_visitors
                })
        except Exception as e:
            current_app.logger.error(f"Error fetching popular pages: {str(e)}")
            popular_pages = []
        
        # Geographic distribution with error handling
        try:
            countries_raw = db.session.query(
                WebsiteVisit.country,
                func.count(WebsiteVisit.id).label('visits')
            ).filter(
                WebsiteVisit.created_at >= start_time,
                WebsiteVisit.country.isnot(None)
            ).group_by(WebsiteVisit.country).order_by(
                func.count(WebsiteVisit.id).desc()
            ).limit(10).all()
            
            # Convert Row objects to dictionaries
            countries = []
            for country in countries_raw:
                countries.append({
                    'country': country.country,
                    'visits': country.visits
                })
        except Exception as e:
            current_app.logger.error(f"Error fetching countries: {str(e)}")
            countries = []
        
        # Browser and device stats with error handling
        browsers = []
        devices = []
        hourly_stats = []
        
        try:
            browsers_raw = db.session.query(
                WebsiteVisit.browser,
                func.count(WebsiteVisit.id).label('visits')
            ).filter(
                WebsiteVisit.created_at >= start_time,
                WebsiteVisit.browser.isnot(None)
            ).group_by(WebsiteVisit.browser).order_by(
                func.count(WebsiteVisit.id).desc()
            ).limit(5).all()
            
            # Convert Row objects to dictionaries
            browsers = []
            for browser in browsers_raw:
                browsers.append({
                    'browser': browser.browser,
                    'visits': browser.visits
                })
        except Exception as e:
            current_app.logger.error(f"Error fetching browsers: {str(e)}")
        
        try:
            devices_raw = db.session.query(
                WebsiteVisit.device_type,
                func.count(WebsiteVisit.id).label('visits')
            ).filter(
                WebsiteVisit.created_at >= start_time,
                WebsiteVisit.device_type.isnot(None)
            ).group_by(WebsiteVisit.device_type).order_by(
                func.count(WebsiteVisit.id).desc()
            ).all()
            
            # Convert Row objects to dictionaries
            devices = []
            for device in devices_raw:
                devices.append({
                    'device_type': device.device_type,
                    'visits': device.visits
                })
        except Exception as e:
            current_app.logger.error(f"Error fetching devices: {str(e)}")
        
        # Hourly distribution (for 24h) with error handling
        if time_filter == '24h':
            try:
                for hour in range(24):
                    hour_start = datetime.now(timezone.utc).replace(hour=hour, minute=0, second=0, microsecond=0)
                    hour_end = hour_start + timedelta(hours=1)
                    
                    hour_visits = WebsiteVisit.query.filter(
                        WebsiteVisit.created_at >= hour_start,
                        WebsiteVisit.created_at < hour_end
                    ).count()
                    
                    hourly_stats.append({
                        'hour': hour,
                        'visits': hour_visits
                    })
            except Exception as e:
                current_app.logger.error(f"Error fetching hourly stats: {str(e)}")
                hourly_stats = []
        
        # Calculate bounce rate (sessions with only 1 page view)
        bounce_sessions = db.session.query(UserSession.session_id).join(
            PageView, UserSession.session_id == PageView.session_id
        ).group_by(UserSession.session_id).having(
            func.count(PageView.id) == 1
        ).subquery()
        
        total_sessions = UserSession.query.count()
        bounced_sessions = db.session.query(bounce_sessions.c.session_id).count()
        bounce_rate = (bounced_sessions / total_sessions * 100) if total_sessions > 0 else 0
        
        # Calculate average session duration
        # Use PostgreSQL-compatible function instead of julianday
        try:
            # Try PostgreSQL EXTRACT function first
            avg_duration_query = db.session.query(
                func.avg(
                    func.extract('epoch', UserSession.last_activity) - 
                    func.extract('epoch', UserSession.started_at)
                )
            ).filter(
                UserSession.last_activity.isnot(None)
            ).scalar()
        except Exception as e:
            # Fallback for SQLite or other databases
            try:
                avg_duration_query = db.session.query(
                    func.avg(
                        func.julianday(UserSession.last_activity) - 
                        func.julianday(UserSession.started_at)
                    ) * 24 * 60 * 60  # Convert to seconds
                ).filter(
                    UserSession.last_activity.isnot(None)
                ).scalar()
            except Exception:
                # If both fail, return 0
                avg_duration_query = 0
        
        avg_session_duration = avg_duration_query or 0
        
        stats = {
            'total_visits': total_visits,
            'unique_visitors': unique_visitors,
            'registered_user_visits': registered_user_visits,
            'bounce_rate': round(bounce_rate, 2),
            'avg_session_duration': round(avg_session_duration, 0)
        }
        
        return render_template('admin/visitors_analytics.html',
                             stats=stats,
                             popular_pages=popular_pages,
                             countries=countries,
                             browsers=browsers,
                             devices=devices,
                             hourly_stats=hourly_stats,
                             time_filter=time_filter,
                             error_message=None)
    
    except Exception as e:
        current_app.logger.error(f"Error in visitors_analytics route: {str(e)}")
        flash(f'Ошибка загрузки аналитики посетителей: {str(e)}', 'error')
        
        # Return empty data in case of error
        return render_template('admin/visitors_analytics.html',
                             stats={
                                 'total_visits': 0,
                                 'unique_visitors': 0,
                                 'registered_user_visits': 0,
                                 'bounce_rate': 0,
                                 'avg_session_duration': 0
                             },
                             popular_pages=[],
                             countries=[],
                             browsers=[],
                             devices=[],
                             hourly_stats=[],
                             time_filter='24h',
                             error_message=str(e))

# ========================================
# USER SUPPORT SYSTEM
# ========================================

@admin_bp.route('/support')
@login_required
@admin_required
def support_dashboard():
    """User support dashboard"""
    # Recent password reset requests
    recent_resets = User.query.filter(
        User.password_reset_sent_at.isnot(None),
        User.password_reset_sent_at >= datetime.now(timezone.utc) - timedelta(days=7)
    ).order_by(User.password_reset_sent_at.desc()).limit(10).all()
    
    # Unverified email accounts
    unverified_emails = User.query.filter(
        User.email_confirmed == False,
        User.created_at >= datetime.now(timezone.utc) - timedelta(days=30)
    ).order_by(User.created_at.desc()).limit(20).all()
    
    # Inactive users (haven't logged in for 30 days)
    inactive_users = User.query.filter(
        or_(
            User.last_login < datetime.now(timezone.utc) - timedelta(days=30),
            User.last_login.is_(None)
        ),
        User.is_active == True
    ).order_by(User.created_at.desc()).limit(20).all()
    
    # Failed login attempts (you might need to implement this)
    failed_logins = []
    
    stats = {
        'recent_resets': len(recent_resets),
        'unverified_emails': len(unverified_emails),
        'inactive_users': len(inactive_users),
        'failed_logins': len(failed_logins)
    }
    
    return render_template('admin/support_dashboard.html',
                         stats=stats,
                         recent_resets=recent_resets,
                         unverified_emails=unverified_emails,
                         inactive_users=inactive_users,
                         failed_logins=failed_logins)

@admin_bp.route('/support/send-verification/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def resend_verification_email(user_id):
    """Resend verification email to user"""
    user = User.query.get_or_404(user_id)
    
    if user.email_confirmed:
        flash('Email уже подтвержден', 'info')
        return redirect(url_for('admin.support_dashboard'))
    
    try:
        # Generate new token
        token = user.generate_email_confirmation_token()
        
        # Отправляем реальное письмо с подтверждением
        from utils.email_service import send_email_confirmation
        email_sent = send_email_confirmation(user, token)
        
        if email_sent:
            flash(f'Письмо с подтверждением отправлено на {user.email}', 'success')
        else:
            flash(f'Ошибка отправки письма на {user.email}', 'error')
        
        db.session.commit()
        
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при отправке письма: {str(e)}', 'danger')
    
    return redirect(url_for('admin.support_dashboard'))

@admin_bp.route('/support/force-verify/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def force_verify_email(user_id):
    """Force verify user email (admin action)"""
    user = User.query.get_or_404(user_id)
    
    try:
        user.confirm_email()
        
        # Log the action
        try:
            if hasattr(user, 'log_profile_change'):
                user.log_profile_change(
                    field='email_confirmed',
                    old_value=False,
                    new_value=True,
                    changed_by=current_user.id
                )
        except Exception as log_error:
            print(f"Warning: Failed to log email verification: {log_error}")
        
        db.session.commit()
        
        flash(f'Email для {user.email} принудительно подтвержден', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Ошибка при подтверждении email: {str(e)}', 'danger')
    
    return redirect(url_for('admin.support_dashboard'))

# ========================================
# API ENDPOINTS FOR REAL-TIME DATA
# ========================================

@admin_bp.route('/api/users/stats')
@login_required
@admin_required
def api_user_stats():
    """Real-time user statistics API"""
    try:
        # Online users (last 5 minutes)
        online_threshold = datetime.now(timezone.utc) - timedelta(minutes=5)
        
        try:
            online_users = User.query.filter(
                User.last_login >= online_threshold,
                User.is_active == True
            ).count()
        except Exception as e:
            current_app.logger.error(f"Error counting online users: {str(e)}")
            online_users = 0
        
        # Today's statistics
        today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        
        try:
            new_users_today = User.query.filter(
                User.created_at >= today_start
            ).count()
        except Exception as e:
            current_app.logger.error(f"Error counting new users: {str(e)}")
            new_users_today = 0
        
        try:
            active_sessions_today = UserSession.query.filter(
                UserSession.started_at >= today_start
            ).count()
        except Exception as e:
            current_app.logger.error(f"Error counting active sessions: {str(e)}")
            active_sessions_today = 0
        
        try:
            visits_today = WebsiteVisit.query.filter(
                WebsiteVisit.created_at >= today_start
            ).count()
        except Exception as e:
            current_app.logger.error(f"Error counting visits: {str(e)}")
            visits_today = 0
        
        return jsonify({
            'online_users': online_users,
            'new_users_today': new_users_today,
            'active_sessions_today': active_sessions_today,
            'visits_today': visits_today,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
    
    except Exception as e:
        current_app.logger.error(f"Error in api_user_stats: {str(e)}")
        return jsonify({
            'online_users': 0,
            'new_users_today': 0,
            'active_sessions_today': 0,
            'visits_today': 0,
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'error': 'Failed to load statistics'
        }), 500

@admin_bp.route('/api/users/search')
@login_required
@admin_required
def api_user_search():
    """User search API"""
    query = request.args.get('q', '').strip()
    limit = request.args.get('limit', 10, type=int)
    
    if not query or len(query) < 2:
        return jsonify([])
    
    search_term = f"%{query}%"
    users = User.query.filter(
        or_(
            User.first_name.ilike(search_term),
            User.last_name.ilike(search_term),
            User.email.ilike(search_term),
            User.username.ilike(search_term)
        )
    ).limit(limit).all()
    
    return jsonify([
        {
            'id': user.id,
            'name': user.get_display_name(),
            'email': user.email,
            'is_active': user.is_active,
            'role': user.role,
            'last_login': user.last_login.isoformat() if user.last_login else None
        }
        for user in users
    ])

# ========================================
# CRM SYSTEM ROUTES
# ========================================

@admin_bp.route('/crm')
@login_required
@admin_required
def crm_dashboard():
    """CRM Dashboard with sales funnel and key metrics"""
    try:
        # Sales funnel data
        leads = Contact.query.filter_by(contact_status='lead').count()
        prospects = Contact.query.filter_by(contact_status='prospect').count()
        clients = Contact.query.filter_by(contact_status='client').count()
        inactive = Contact.query.filter_by(contact_status='inactive').count()
        
        # Key metrics
        total_contacts = Contact.query.count()
        # Try PostgreSQL-compatible date function first
        try:
            new_contacts_today = Contact.query.filter(
                func.date_trunc('day', Contact.created_at) == date.today()
            ).count()
        except Exception:
            # Fallback for SQLite
            new_contacts_today = Contact.query.filter(
                func.date(Contact.created_at) == date.today()
            ).count()
        
        # Conversion rate calculation
        conversion_rate = 0
        if total_contacts > 0:
            conversion_rate = (clients / total_contacts) * 100
        
        # Recent contacts
        recent_contacts = Contact.query.order_by(Contact.created_at.desc()).limit(10).all()
        
        # Follow-up tasks
        overdue_followups = Contact.query.filter(
            Contact.next_followup_date < datetime.utcnow(),
            Contact.contact_status.in_(['lead', 'prospect'])
        ).count()
        
        # Lead sources
        lead_sources = db.session.query(
            Contact.lead_source,
            func.count(Contact.id).label('count')
        ).group_by(Contact.lead_source).all()
        
        # Profession distribution
        profession_stats = db.session.query(
            Profession.name,
            func.count(Contact.id).label('count')
        ).join(Contact, Profession.id == Contact.profession_id).group_by(Profession.name).all()
        
        return render_template('admin/crm_dashboard.html',
                             leads=leads,
                             prospects=prospects,
                             clients=clients,
                             inactive=inactive,
                             total_contacts=total_contacts,
                             new_contacts_today=new_contacts_today,
                             conversion_rate=conversion_rate,
                             recent_contacts=recent_contacts,
                             overdue_followups=overdue_followups,
                             lead_sources=lead_sources,
                             profession_stats=profession_stats)
    
    except Exception as e:
        current_app.logger.error(f"Error in CRM dashboard: {str(e)}")
        flash(f'Ошибка загрузки CRM дашборда: {str(e)}', 'error')
        return render_template('admin/crm_dashboard.html',
                             leads=0, prospects=0, clients=0, inactive=0,
                             total_contacts=0, new_contacts_today=0,
                             conversion_rate=0, recent_contacts=[],
                             overdue_followups=0, lead_sources=[],
                             profession_stats=[])

@admin_bp.route('/crm/contacts', methods=['GET', 'POST'])
@login_required
@admin_required
def crm_contacts():
    """Contact management page"""
    try:
        # Handle POST request for adding new contact
        if request.method == 'POST':
            try:
                # Create new contact
                contact = Contact(
                    full_name=request.form.get('full_name'),
                    email=request.form.get('email'),
                    phone=request.form.get('phone'),
                    profession_id=request.form.get('profession_id', type=int) or None,
                    workplace=request.form.get('workplace'),
                    contact_status=request.form.get('contact_status', 'lead'),
                    lead_source=request.form.get('lead_source'),
                    notes=request.form.get('notes')
                )
                
                db.session.add(contact)
                db.session.commit()
                
                flash('Контакт успешно добавлен!', 'success')
                return redirect(url_for('admin.crm_contacts'))
                
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error creating contact: {str(e)}")
                flash(f'Ошибка создания контакта: {str(e)}', 'error')
        
        # Get filter parameters
        status_filter = request.args.get('status', 'all')
        profession_filter = request.args.get('profession', 'all')
        search_query = request.args.get('search', '').strip()
        
        # Build query
        query = Contact.query
        
        if status_filter != 'all':
            query = query.filter_by(contact_status=status_filter)
        
        if profession_filter != 'all':
            query = query.filter_by(profession_id=profession_filter)
        
        if search_query:
            query = query.filter(
                or_(
                    Contact.full_name.ilike(f'%{search_query}%'),
                    Contact.email.ilike(f'%{search_query}%'),
                    Contact.phone.ilike(f'%{search_query}%')
                )
            )
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = 20
        contacts = query.order_by(Contact.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get professions for filter
        professions = Profession.query.filter_by(is_active=True).all()
        
        return render_template('admin/crm_contacts.html',
                             contacts=contacts,
                             professions=professions,
                             status_filter=status_filter,
                             profession_filter=profession_filter,
                             search_query=search_query)
    
    except Exception as e:
        current_app.logger.error(f"Error in CRM contacts: {str(e)}")
        flash(f'Ошибка загрузки контактов: {str(e)}', 'error')
        return render_template('admin/crm_contacts.html',
                             contacts=None, professions=[],
                             status_filter='all', profession_filter='all',
                             search_query='')

@admin_bp.route('/crm/contacts/<int:contact_id>')
@login_required
@admin_required
def crm_contact_detail(contact_id):
    """Contact detail page"""
    try:
        contact = Contact.query.get_or_404(contact_id)
        professions = Profession.query.filter_by(is_active=True).all()
        admin_users = User.query.filter_by(role='admin').all()
        
        return render_template('admin/crm_contact_detail.html',
                             contact=contact,
                             professions=professions,
                             admin_users=admin_users)
    
    except Exception as e:
        current_app.logger.error(f"Error loading contact detail: {str(e)}")
        flash(f'Ошибка загрузки контакта: {str(e)}', 'error')
        return redirect(url_for('admin.crm_contacts'))

@admin_bp.route('/crm/contacts/<int:contact_id>/update', methods=['POST'])
@login_required
@admin_required
def crm_contact_update(contact_id):
    """Update contact information"""
    try:
        contact = Contact.query.get_or_404(contact_id)
        
        # Update fields
        contact.full_name = request.form.get('full_name', contact.full_name)
        contact.email = request.form.get('email', contact.email)
        contact.phone = request.form.get('phone', contact.phone)
        contact.profession_id = request.form.get('profession_id', type=int) or None
        contact.workplace = request.form.get('workplace', contact.workplace)
        contact.big_number = request.form.get('big_number', contact.big_number)
        contact.contact_status = request.form.get('contact_status', contact.contact_status)
        contact.lead_source = request.form.get('lead_source', contact.lead_source)
        contact.assigned_to = request.form.get('assigned_to', type=int) or None
        contact.notes = request.form.get('notes', contact.notes)
        
        # Update follow-up date if provided
        followup_date = request.form.get('next_followup_date')
        if followup_date:
            try:
                contact.next_followup_date = datetime.strptime(followup_date, '%Y-%m-%d')
            except ValueError:
                pass
        
        contact.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash('Контакт успешно обновлен', 'success')
        return redirect(url_for('admin.crm_contact_detail', contact_id=contact_id))
    
    except Exception as e:
        current_app.logger.error(f"Error updating contact: {str(e)}")
        db.session.rollback()
        flash(f'Ошибка обновления контакта: {str(e)}', 'error')
        return redirect(url_for('admin.crm_contact_detail', contact_id=contact_id))

@admin_bp.route('/crm/professions')
@login_required
@admin_required
def crm_professions():
    """Profession management page"""
    try:
        professions = Profession.query.filter_by(is_active=True).all()
        
        # Get contact counts for each profession
        profession_stats = []
        for profession in professions:
            contact_count = Contact.query.filter_by(profession_id=profession.id).count()
            profession_stats.append({
                'profession': profession,
                'contact_count': contact_count
            })
        
        return render_template('admin/crm_professions.html',
                             profession_stats=profession_stats)
    
    except Exception as e:
        current_app.logger.error(f"Error loading professions: {str(e)}")
        flash(f'Ошибка загрузки профессий: {str(e)}', 'error')
        return render_template('admin/crm_professions.html',
                             profession_stats=[])

@admin_bp.route('/crm/professions/create', methods=['GET', 'POST'])
@login_required
@admin_required
def crm_profession_create():
    """Create new profession"""
    if request.method == 'POST':
        try:
            profession = Profession(
                name=request.form.get('name'),
                name_nl=request.form.get('name_nl'),
                code=request.form.get('code'),
                category=request.form.get('category'),
                big_exam_required=bool(request.form.get('big_exam_required')),
                description=request.form.get('description'),
                requirements=request.form.get('requirements')
            )
            
            db.session.add(profession)
            db.session.commit()
            
            flash('Профессия успешно создана', 'success')
            return redirect(url_for('admin.crm_professions'))
        
        except Exception as e:
            current_app.logger.error(f"Error creating profession: {str(e)}")
            db.session.rollback()
            flash(f'Ошибка создания профессии: {str(e)}', 'error')
    
    return render_template('admin/crm_profession_form.html')

@admin_bp.route('/crm/contacts/send-email', methods=['POST'])
@login_required
@admin_required
def crm_contacts_send_email():
    """Send email to CRM contacts"""
    try:
        data = request.get_json()
        subject = data.get('subject')
        message = data.get('message')
        contact_id = data.get('contact_id')
        contact_ids = data.get('contact_ids')
        email_type = data.get('email_type', 'crm_lead')
        
        if not subject or not message:
            return jsonify({'success': False, 'error': 'Subject and message are required'})
        
        # Get contacts to send email to
        if contact_id:
            contacts = [Contact.query.get(contact_id)]
        elif contact_ids:
            contact_id_list = [int(id) for id in contact_ids.split(',')]
            contacts = Contact.query.filter(Contact.id.in_(contact_id_list)).all()
        else:
            return jsonify({'success': False, 'error': 'No contacts specified'})
        
        # Send emails using CRM email service
        from utils.admin_email_service import send_bulk_admin_emails
        
        result = send_bulk_admin_emails(contacts, subject, message, email_type)
        sent_count = result['sent']
        
        if result['errors']:
            current_app.logger.warning(f"Some CRM emails failed to send: {result['errors']}")
        
        return jsonify({
            'success': True, 
            'message': f'Email sent to {sent_count} contacts',
            'sent_count': sent_count
        })
    
    except Exception as e:
        current_app.logger.error(f"Error sending CRM emails: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@admin_bp.route('/crm/api/contacts/stats')
@login_required
@admin_required
def crm_contacts_stats():
    """API endpoint for contact statistics"""
    try:
        # Status distribution
        status_stats = db.session.query(
            Contact.contact_status,
            func.count(Contact.id).label('count')
        ).group_by(Contact.contact_status).all()
        
        # Monthly registrations (last 12 months)
        monthly_stats = []
        for i in range(12):
            month_start = datetime.utcnow().replace(day=1) - timedelta(days=30*i)
            month_end = month_start + timedelta(days=30)
            
            count = Contact.query.filter(
                Contact.created_at >= month_start,
                Contact.created_at < month_end
            ).count()
            
            monthly_stats.append({
                'month': month_start.strftime('%Y-%m'),
                'count': count
            })
        
        return jsonify({
            'status_stats': [{'status': s.contact_status, 'count': s.count} for s in status_stats],
            'monthly_stats': monthly_stats
        })
    
    except Exception as e:
        current_app.logger.error(f"Error in CRM contacts stats: {str(e)}")
        return jsonify({'error': 'Failed to load statistics'}), 500

# ========================================
# ADVANCED ANALYTICS ROUTES
# ========================================

@admin_bp.route('/analytics/advanced')
@login_required
@admin_required
def advanced_analytics():
    """Advanced analytics dashboard with detailed insights"""
    try:
        # Get time range
        timeframe = request.args.get('timeframe', '7d')
        days = 7 if timeframe == '7d' else 30 if timeframe == '30d' else 90
        
        # Country analytics
        country_stats = db.session.query(
            CountryAnalytics.country_name,
            CountryAnalytics.total_users,
            CountryAnalytics.active_users,
            CountryAnalytics.conversion_rate,
            CountryAnalytics.completion_rate,
            CountryAnalytics.avg_session_duration
        ).order_by(CountryAnalytics.total_users.desc()).limit(10).all()
        
        # Device analytics
        device_stats = db.session.query(
            DeviceAnalytics.device_category,
            DeviceAnalytics.browser,
            DeviceAnalytics.os,
            func.sum(DeviceAnalytics.users_count).label('total_users'),
            func.avg(DeviceAnalytics.avg_session_duration).label('avg_session'),
            func.avg(DeviceAnalytics.conversion_rate).label('avg_conversion')
        ).group_by(
            DeviceAnalytics.device_category,
            DeviceAnalytics.browser,
            DeviceAnalytics.os
        ).order_by(func.sum(DeviceAnalytics.users_count).desc()).limit(15).all()
        
        # Profession analytics
        profession_stats = db.session.query(
            ProfessionAnalytics.profession_id,
            Profession.name,
            func.sum(ProfessionAnalytics.total_registrations).label('total_registrations'),
            func.sum(ProfessionAnalytics.active_users).label('active_users'),
            func.avg(ProfessionAnalytics.avg_progress).label('avg_progress'),
            func.avg(ProfessionAnalytics.exam_pass_rate).label('exam_pass_rate')
        ).join(Profession, ProfessionAnalytics.profession_id == Profession.id).group_by(
            ProfessionAnalytics.profession_id,
            Profession.name
        ).order_by(func.sum(ProfessionAnalytics.total_registrations).desc()).all()
        
        # Recent events
        recent_events = AnalyticsEvent.query.order_by(
            AnalyticsEvent.created_at.desc()
        ).limit(20).all()
        
        # Summary statistics
        total_countries = CountryAnalytics.query.count()
        total_devices = DeviceAnalytics.query.count()
        total_professions = ProfessionAnalytics.query.count()
        total_events = AnalyticsEvent.query.count()
        
        return render_template('admin/advanced_analytics.html',
                             country_stats=country_stats,
                             device_stats=device_stats,
                             profession_stats=profession_stats,
                             recent_events=recent_events,
                             total_countries=total_countries,
                             total_devices=total_devices,
                             total_professions=total_professions,
                             total_events=total_events,
                             timeframe=timeframe)
    
    except Exception as e:
        current_app.logger.error(f"Error in advanced analytics: {str(e)}")
        flash(f'Ошибка загрузки расширенной аналитики: {str(e)}', 'error')
        return render_template('admin/advanced_analytics.html',
                             country_stats=[], device_stats=[], profession_stats=[],
                             recent_events=[], total_countries=0, total_devices=0,
                             total_professions=0, total_events=0, timeframe='7d')

@admin_bp.route('/analytics/countries')
@login_required
@admin_required
def analytics_countries():
    """Detailed country analytics page"""
    try:
        # Get filter parameters
        sort_by = request.args.get('sort', 'total_users')
        order = request.args.get('order', 'desc')
        
        # Build query
        query = CountryAnalytics.query
        
        # Apply sorting
        if sort_by == 'total_users':
            query = query.order_by(CountryAnalytics.total_users.desc() if order == 'desc' else CountryAnalytics.total_users.asc())
        elif sort_by == 'conversion_rate':
            query = query.order_by(CountryAnalytics.conversion_rate.desc() if order == 'desc' else CountryAnalytics.conversion_rate.asc())
        elif sort_by == 'completion_rate':
            query = query.order_by(CountryAnalytics.completion_rate.desc() if order == 'desc' else CountryAnalytics.completion_rate.asc())
        elif sort_by == 'avg_session_duration':
            query = query.order_by(CountryAnalytics.avg_session_duration.desc() if order == 'desc' else CountryAnalytics.avg_session_duration.asc())
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = 25
        countries = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return render_template('admin/analytics_countries.html',
                             countries=countries,
                             sort_by=sort_by,
                             order=order)
    
    except Exception as e:
        current_app.logger.error(f"Error in country analytics: {str(e)}")
        flash(f'Ошибка загрузки аналитики по странам: {str(e)}', 'error')
        return render_template('admin/analytics_countries.html',
                             countries=None, sort_by='total_users', order='desc')

@admin_bp.route('/analytics/devices')
@login_required
@admin_required
def analytics_devices():
    """Detailed device analytics page"""
    try:
        # Get filter parameters
        device_filter = request.args.get('device', 'all')
        sort_by = request.args.get('sort', 'users_count')
        order = request.args.get('order', 'desc')
        
        # Build query
        query = DeviceAnalytics.query
        
        if device_filter != 'all':
            query = query.filter_by(device_category=device_filter)
        
        # Apply sorting
        if sort_by == 'users_count':
            query = query.order_by(DeviceAnalytics.users_count.desc() if order == 'desc' else DeviceAnalytics.users_count.asc())
        elif sort_by == 'avg_session_duration':
            query = query.order_by(DeviceAnalytics.avg_session_duration.desc() if order == 'desc' else DeviceAnalytics.avg_session_duration.asc())
        elif sort_by == 'conversion_rate':
            query = query.order_by(DeviceAnalytics.conversion_rate.desc() if order == 'desc' else DeviceAnalytics.conversion_rate.asc())
        elif sort_by == 'bounce_rate':
            query = query.order_by(DeviceAnalytics.bounce_rate.asc() if order == 'desc' else DeviceAnalytics.bounce_rate.desc())
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = 25
        devices = query.paginate(page=page, per_page=per_page, error_out=False)
        
        # Get device categories for filter
        device_categories = db.session.query(DeviceAnalytics.device_category).distinct().all()
        device_categories = [cat[0] for cat in device_categories]
        
        return render_template('admin/analytics_devices.html',
                             devices=devices,
                             device_categories=device_categories,
                             device_filter=device_filter,
                             sort_by=sort_by,
                             order=order)
    
    except Exception as e:
        current_app.logger.error(f"Error in device analytics: {str(e)}")
        flash(f'Ошибка загрузки аналитики по устройствам: {str(e)}', 'error')
        return render_template('admin/analytics_devices.html',
                             devices=None, device_categories=[],
                             device_filter='all', sort_by='users_count', order='desc')

@admin_bp.route('/analytics/professions')
@login_required
@admin_required
def analytics_professions():
    """Detailed profession analytics page"""
    try:
        # Get filter parameters
        sort_by = request.args.get('sort', 'total_registrations')
        order = request.args.get('order', 'desc')
        
        # Build query with profession join
        query = db.session.query(
            ProfessionAnalytics,
            Profession.name.label('profession_name')
        ).join(Profession, ProfessionAnalytics.profession_id == Profession.id)
        
        # Apply sorting
        if sort_by == 'total_registrations':
            query = query.order_by(ProfessionAnalytics.total_registrations.desc() if order == 'desc' else ProfessionAnalytics.total_registrations.asc())
        elif sort_by == 'active_users':
            query = query.order_by(ProfessionAnalytics.active_users.desc() if order == 'desc' else ProfessionAnalytics.active_users.asc())
        elif sort_by == 'avg_progress':
            query = query.order_by(ProfessionAnalytics.avg_progress.desc() if order == 'desc' else ProfessionAnalytics.avg_progress.asc())
        elif sort_by == 'exam_pass_rate':
            query = query.order_by(ProfessionAnalytics.exam_pass_rate.desc() if order == 'desc' else ProfessionAnalytics.exam_pass_rate.asc())
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = 25
        professions = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return render_template('admin/analytics_professions.html',
                             professions=professions,
                             sort_by=sort_by,
                             order=order)
    
    except Exception as e:
        current_app.logger.error(f"Error in profession analytics: {str(e)}")
        flash(f'Ошибка загрузки аналитики по профессиям: {str(e)}', 'error')
        return render_template('admin/analytics_professions.html',
                             professions=None, sort_by='total_registrations', order='desc')

@admin_bp.route('/analytics/events')
@login_required
@admin_required
def analytics_events():
    """Analytics events tracking page"""
    try:
        # Get filter parameters
        event_filter = request.args.get('event', 'all')
        category_filter = request.args.get('category', 'all')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        
        # Build query
        query = AnalyticsEvent.query
        
        if event_filter != 'all':
            query = query.filter_by(event_name=event_filter)
        
        if category_filter != 'all':
            query = query.filter_by(event_category=category_filter)
        
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                query = query.filter(AnalyticsEvent.created_at >= date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
                query = query.filter(AnalyticsEvent.created_at <= date_to_obj)
            except ValueError:
                pass
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = 50
        events = query.order_by(AnalyticsEvent.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get filter options
        event_names = db.session.query(AnalyticsEvent.event_name).distinct().all()
        event_names = [name[0] for name in event_names]
        
        event_categories = db.session.query(AnalyticsEvent.event_category).distinct().all()
        event_categories = [cat[0] for cat in event_categories]
        
        return render_template('admin/analytics_events.html',
                             events=events,
                             event_names=event_names,
                             event_categories=event_categories,
                             event_filter=event_filter,
                             category_filter=category_filter,
                             date_from=date_from,
                             date_to=date_to)
    
    except Exception as e:
        current_app.logger.error(f"Error in analytics events: {str(e)}")
        flash(f'Ошибка загрузки событий аналитики: {str(e)}', 'error')
        return render_template('admin/analytics_events.html',
                             events=None, event_names=[], event_categories=[],
                             event_filter='all', category_filter='all',
                             date_from='', date_to='')

@admin_bp.route('/analytics/export')
@login_required
@admin_required
def analytics_export():
    """Export analytics data"""
    try:
        export_type = request.args.get('type', 'countries')
        format_type = request.args.get('format', 'json')
        
        if export_type == 'countries':
            data = CountryAnalytics.query.all()
            data = [item.to_dict() for item in data]
        elif export_type == 'devices':
            data = DeviceAnalytics.query.all()
            data = [item.to_dict() for item in data]
        elif export_type == 'professions':
            data = db.session.query(
                ProfessionAnalytics,
                Profession.name.label('profession_name')
            ).join(Profession, ProfessionAnalytics.profession_id == Profession.id).all()
            data = [item[0].to_dict() for item in data]
        elif export_type == 'events':
            data = AnalyticsEvent.query.limit(1000).all()
            data = [item.to_dict() for item in data]
        else:
            return jsonify({'error': 'Invalid export type'}), 400
        
        if format_type == 'json':
            return jsonify({
                'export_type': export_type,
                'exported_at': datetime.utcnow().isoformat(),
                'count': len(data),
                'data': data
            })
        elif format_type == 'csv':
            # Simple CSV export (would need proper CSV library for production)
            csv_data = "Export type,Exported at,Count\n"
            csv_data += f"{export_type},{datetime.utcnow().isoformat()},{len(data)}\n"
            csv_data += "Data exported as JSON (use JSON format for full data)\n"
            return csv_data, 200, {'Content-Type': 'text/csv'}
        else:
            return jsonify({'error': 'Invalid format type'}), 400
    
    except Exception as e:
        current_app.logger.error(f"Error in analytics export: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ========================================
# ADMINISTRATIVE TOOLS ROUTES
# ========================================

@admin_bp.route('/database')
@login_required
@admin_required
def database_management():
    """Database management dashboard"""
    try:
        # Get recent backups
        recent_backups = DatabaseBackup.query.order_by(
            DatabaseBackup.started_at.desc()
        ).limit(10).all()
        
        # Get database statistics
        total_users = User.query.count()
        total_contacts = Contact.query.count()
        total_professions = Profession.query.count()
        total_analytics_events = AnalyticsEvent.query.count()
        
        # Get backup statistics
        total_backups = DatabaseBackup.query.count()
        successful_backups = DatabaseBackup.query.filter_by(status='completed').count()
        failed_backups = DatabaseBackup.query.filter_by(status='failed').count()
        
        return render_template('admin/database_management.html',
                             recent_backups=recent_backups,
                             total_users=total_users,
                             total_contacts=total_contacts,
                             total_professions=total_professions,
                             total_analytics_events=total_analytics_events,
                             total_backups=total_backups,
                             successful_backups=successful_backups,
                             failed_backups=failed_backups)
    
    except Exception as e:
        current_app.logger.error(f"Error in database management: {str(e)}")
        flash(f'Ошибка загрузки управления БД: {str(e)}', 'error')
        return render_template('admin/database_management.html',
                             recent_backups=[], total_users=0, total_contacts=0,
                             total_professions=0, total_analytics_events=0,
                             total_backups=0, successful_backups=0, failed_backups=0)

@admin_bp.route('/database/backup', methods=['POST'])
@login_required
@admin_required
def create_database_backup():
    """Create a manual database backup"""
    try:
        backup_name = f"manual_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Create backup record
        backup = DatabaseBackup(
            admin_user_id=current_user.id,
            backup_name=backup_name,
            backup_type='manual',
            status='in_progress'
        )
        
        db.session.add(backup)
        db.session.commit()
        
        # Perform actual backup
        try:
            backup_result = perform_database_backup(backup)
            
            # Update backup record with results
            backup.status = 'completed'
            backup.completed_at = datetime.utcnow()
            backup.file_path = backup_result.get('file_path')
            backup.file_size = backup_result.get('file_size')
            backup.tables_count = backup_result.get('tables_count')
            backup.records_count = backup_result.get('records_count')
            backup.backup_duration = backup_result.get('duration')
            backup.expires_at = datetime.utcnow() + timedelta(days=30)  # Keep for 30 days
            
            db.session.commit()
            
            # Log admin action
            audit_log = AdminAuditLog(
                admin_user_id=current_user.id,
                action='database_backup_completed',
                target_type='system',
                details=json.dumps({
                    'backup_name': backup_name,
                    'file_size': backup.file_size,
                    'tables_count': backup.tables_count,
                    'records_count': backup.records_count
                }),
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                request_url=request.url,
                request_method=request.method
            )
            db.session.add(audit_log)
            db.session.commit()
            
            flash(f'Резервная копия "{backup_name}" создана успешно', 'success')
            return jsonify({
                'status': 'success',
                'message': 'Backup created successfully',
                'backup_id': backup.id
            })
            
        except Exception as backup_error:
            # Update backup record with error
            backup.status = 'failed'
            backup.error_message = str(backup_error)
            backup.completed_at = datetime.utcnow()
            db.session.commit()
            
            current_app.logger.error(f"Backup failed: {str(backup_error)}")
            flash(f'Ошибка создания резервной копии: {str(backup_error)}', 'error')
            return jsonify({'error': str(backup_error)}), 500
    
    except Exception as e:
        current_app.logger.error(f"Error creating database backup: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@admin_bp.route('/system')
@login_required
@admin_required
def system_health():
    """System health monitoring dashboard"""
    try:
        # Get recent health logs
        recent_logs = SystemHealthLog.query.order_by(
            SystemHealthLog.created_at.desc()
        ).limit(20).all()
        
        # Get current system status
        latest_log = SystemHealthLog.query.order_by(
            SystemHealthLog.created_at.desc()
        ).first()
        
        # Get system statistics
        total_logs = SystemHealthLog.query.count()
        healthy_logs = SystemHealthLog.query.filter_by(status='healthy').count()
        warning_logs = SystemHealthLog.query.filter_by(status='warning').count()
        critical_logs = SystemHealthLog.query.filter_by(status='critical').count()
        
        # Get recent notifications
        recent_notifications = SystemNotification.query.filter_by(
            is_active=True
        ).order_by(SystemNotification.created_at.desc()).limit(10).all()
        
        return render_template('admin/system_health.html',
                             recent_logs=recent_logs,
                             latest_log=latest_log,
                             total_logs=total_logs,
                             healthy_logs=healthy_logs,
                             warning_logs=warning_logs,
                             critical_logs=critical_logs,
                             recent_notifications=recent_notifications)
    
    except Exception as e:
        current_app.logger.error(f"Error in system health: {str(e)}")
        flash(f'Ошибка загрузки мониторинга системы: {str(e)}', 'error')
        return render_template('admin/system_health.html',
                             recent_logs=[], latest_log=None,
                             total_logs=0, healthy_logs=0, warning_logs=0, critical_logs=0,
                             recent_notifications=[])

@admin_bp.route('/communication')
@login_required
@admin_required
def communication_hub():
    """Communication hub dashboard"""
    try:
        # Get email templates
        email_templates = EmailTemplate.query.filter_by(is_active=True).all()
        
        # Get email campaigns
        email_campaigns = CommunicationCampaign.query.order_by(
            CommunicationCampaign.created_at.desc()
        ).limit(10).all()
        
        # Get template statistics
        total_templates = EmailTemplate.query.count()
        active_templates = EmailTemplate.query.filter_by(is_active=True).count()
        system_templates = EmailTemplate.query.filter_by(is_system=True).count()
        
        # Get campaign statistics
        total_campaigns = CommunicationCampaign.query.count()
        draft_campaigns = CommunicationCampaign.query.filter_by(status='draft').count()
        sent_campaigns = CommunicationCampaign.query.filter_by(status='completed').count()
        
        return render_template('admin/communication_hub.html',
                             email_templates=email_templates,
                             email_campaigns=email_campaigns,
                             total_templates=total_templates,
                             active_templates=active_templates,
                             system_templates=system_templates,
                             total_campaigns=total_campaigns,
                             draft_campaigns=draft_campaigns,
                             sent_campaigns=sent_campaigns)
    
    except Exception as e:
        current_app.logger.error(f"Error in communication hub: {str(e)}")
        flash(f'Ошибка загрузки коммуникационного центра: {str(e)}', 'error')
        return render_template('admin/communication_hub.html',
                             email_templates=[], email_campaigns=[],
                             total_templates=0, active_templates=0, system_templates=0,
                             total_campaigns=0, draft_campaigns=0, sent_campaigns=0)

@admin_bp.route('/audit')
@login_required
@admin_required
def audit_logs():
    """Admin audit logs page"""
    try:
        # Get filter parameters
        action_filter = request.args.get('action', 'all')
        target_filter = request.args.get('target', 'all')
        admin_filter = request.args.get('admin', 'all')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        
        # Build query
        query = AdminAuditLog.query
        
        if action_filter != 'all':
            query = query.filter_by(action=action_filter)
        
        if target_filter != 'all':
            query = query.filter_by(target_type=target_filter)
        
        if admin_filter != 'all':
            query = query.filter_by(admin_user_id=admin_filter)
        
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                query = query.filter(AdminAuditLog.created_at >= date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
                query = query.filter(AdminAuditLog.created_at <= date_to_obj)
            except ValueError:
                pass
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = 50
        audit_logs = query.order_by(AdminAuditLog.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get filter options
        actions = db.session.query(AdminAuditLog.action).distinct().all()
        actions = [action[0] for action in actions]
        
        targets = db.session.query(AdminAuditLog.target_type).distinct().all()
        targets = [target[0] for target in targets]
        
        admins = db.session.query(User.id, User.email).filter_by(role='admin').all()
        
        return render_template('admin/audit_logs.html',
                             audit_logs=audit_logs,
                             actions=actions,
                             targets=targets,
                             admins=admins,
                             action_filter=action_filter,
                             target_filter=target_filter,
                             admin_filter=admin_filter,
                             date_from=date_from,
                             date_to=date_to)
    
    except Exception as e:
        current_app.logger.error(f"Error in audit logs: {str(e)}")
        flash(f'Ошибка загрузки логов аудита: {str(e)}', 'error')
        return render_template('admin/audit_logs.html',
                             audit_logs=None, actions=[], targets=[], admins=[],
                             action_filter='all', target_filter='all', admin_filter='all',
                             date_from='', date_to='')

@admin_bp.route('/notifications')
@login_required
@admin_required
def system_notifications():
    """System notifications management"""
    try:
        # Get filter parameters
        type_filter = request.args.get('type', 'all')
        priority_filter = request.args.get('priority', 'all')
        status_filter = request.args.get('status', 'all')
        
        # Build query
        query = SystemNotification.query
        
        if type_filter != 'all':
            query = query.filter_by(notification_type=type_filter)
        
        if priority_filter != 'all':
            query = query.filter_by(priority=priority_filter)
        
        if status_filter == 'active':
            query = query.filter_by(is_active=True)
        elif status_filter == 'inactive':
            query = query.filter_by(is_active=False)
        
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = 25
        notifications = query.order_by(SystemNotification.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get statistics
        total_notifications = SystemNotification.query.count()
        active_notifications = SystemNotification.query.filter_by(is_active=True).count()
        unread_notifications = SystemNotification.query.filter_by(is_read=False).count()
        
        return render_template('admin/system_notifications.html',
                             notifications=notifications,
                             total_notifications=total_notifications,
                             active_notifications=active_notifications,
                             unread_notifications=unread_notifications,
                             type_filter=type_filter,
                             priority_filter=priority_filter,
                             status_filter=status_filter)
    
    except Exception as e:
        current_app.logger.error(f"Error in system notifications: {str(e)}")
        flash(f'Ошибка загрузки уведомлений: {str(e)}', 'error')
        return render_template('admin/system_notifications.html',
                             notifications=None, total_notifications=0,
                             active_notifications=0, unread_notifications=0,
                             type_filter='all', priority_filter='all', status_filter='all')

@admin_bp.route('/notifications/create', methods=['POST'])
@login_required
@admin_required
def create_notification():
    """Create a new system notification"""
    try:
        data = request.get_json()
        
        notification = SystemNotification(
            title=data.get('title'),
            message=data.get('message'),
            notification_type=data.get('type', 'info'),
            priority=data.get('priority', 'normal'),
            target_users=data.get('target_users'),
            target_roles=data.get('target_roles'),
            action_url=data.get('action_url'),
            action_text=data.get('action_text')
        )
        
        db.session.add(notification)
        db.session.commit()
        
        # Log admin action
        audit_log = AdminAuditLog(
            admin_user_id=current_user.id,
            action='notification_created',
            target_type='system',
            target_id=notification.id,
            details=json.dumps({
                'title': notification.title,
                'type': notification.notification_type,
                'priority': notification.priority
            }),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            request_url=request.url,
            request_method=request.method
        )
        db.session.add(audit_log)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Notification created successfully',
            'notification_id': notification.id
        })
    
    except Exception as e:
        current_app.logger.error(f"Error creating notification: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ========================================
# CAMPAIGN MANAGEMENT ROUTES
# ========================================

@admin_bp.route('/communication/campaigns/<int:campaign_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_campaign(campaign_id):
    """Edit communication campaign"""
    try:
        campaign = CommunicationCampaign.query.get_or_404(campaign_id)
        
        if request.method == 'POST':
            campaign.name = request.form.get('name', campaign.name)
            campaign.description = request.form.get('description', campaign.description)
            campaign.message = request.form.get('message', campaign.message)
            campaign.action_url = request.form.get('action_url', campaign.action_url)
            campaign.action_text = request.form.get('action_text', campaign.action_text)
            campaign.target_filters = request.form.get('target_filters', campaign.target_filters)
            
            db.session.commit()
            flash('Кампания обновлена успешно', 'success')
            return redirect(url_for('admin.communication_campaigns'))
        
        return render_template('admin/communication/edit_campaign.html', campaign=campaign)
        
    except Exception as e:
        current_app.logger.error(f"Error editing campaign: {str(e)}")
        flash(f'Ошибка редактирования кампании: {str(e)}', 'error')
        return redirect(url_for('admin.communication_campaigns'))

@admin_bp.route('/communication/campaigns/<int:campaign_id>/start', methods=['POST'])
@login_required
@admin_required
def start_campaign(campaign_id):
    """Start communication campaign"""
    try:
        campaign = CommunicationCampaign.query.get_or_404(campaign_id)
        
        if campaign.status == 'draft':
            campaign.status = 'active'
            campaign.started_at = datetime.utcnow()
            db.session.commit()
            
            # Log admin action
            audit_log = AdminAuditLog(
                admin_user_id=current_user.id,
                action='campaign_started',
                target_type='campaign',
                target_id=campaign_id,
                details=json.dumps({'campaign_name': campaign.name}),
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                request_url=request.url,
                request_method=request.method
            )
            db.session.add(audit_log)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Кампания запущена успешно'})
        else:
            return jsonify({'success': False, 'error': 'Кампания уже активна или завершена'})
            
    except Exception as e:
        current_app.logger.error(f"Error starting campaign: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/communication/campaigns/<int:campaign_id>/stop', methods=['POST'])
@login_required
@admin_required
def stop_campaign(campaign_id):
    """Stop communication campaign"""
    try:
        campaign = CommunicationCampaign.query.get_or_404(campaign_id)
        
        if campaign.status == 'active':
            campaign.status = 'stopped'
            campaign.stopped_at = datetime.utcnow()
            db.session.commit()
            
            # Log admin action
            audit_log = AdminAuditLog(
                admin_user_id=current_user.id,
                action='campaign_stopped',
                target_type='campaign',
                target_id=campaign_id,
                details=json.dumps({'campaign_name': campaign.name}),
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                request_url=request.url,
                request_method=request.method
            )
            db.session.add(audit_log)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Кампания остановлена успешно'})
        else:
            return jsonify({'success': False, 'error': 'Кампания не активна'})
            
    except Exception as e:
        current_app.logger.error(f"Error stopping campaign: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/communication/campaigns/<int:campaign_id>/cancel', methods=['POST'])
@login_required
@admin_required
def cancel_campaign(campaign_id):
    """Cancel communication campaign"""
    try:
        campaign = CommunicationCampaign.query.get_or_404(campaign_id)
        
        if campaign.status in ['draft', 'active']:
            campaign.status = 'cancelled'
            campaign.cancelled_at = datetime.utcnow()
            db.session.commit()
            
            # Log admin action
            audit_log = AdminAuditLog(
                admin_user_id=current_user.id,
                action='campaign_cancelled',
                target_type='campaign',
                target_id=campaign_id,
                details=json.dumps({'campaign_name': campaign.name}),
                ip_address=request.remote_addr,
                user_agent=request.headers.get('User-Agent'),
                request_url=request.url,
                request_method=request.method
            )
            db.session.add(audit_log)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Кампания отменена успешно'})
        else:
            return jsonify({'success': False, 'error': 'Кампания уже завершена или отменена'})
            
    except Exception as e:
        current_app.logger.error(f"Error cancelling campaign: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/communication/campaigns/<int:campaign_id>/details')
@login_required
@admin_required
def campaign_details(campaign_id):
    """View campaign details"""
    try:
        campaign = CommunicationCampaign.query.get_or_404(campaign_id)
        
        # Get campaign statistics
        stats = {
            'total_recipients': 0,
            'emails_sent': 0,
            'emails_delivered': 0,
            'emails_opened': 0,
            'clicks': 0
        }
        
        # Calculate stats based on campaign type and filters
        if campaign.target_filters:
            try:
                filters = json.loads(campaign.target_filters)
                query = User.query
                
                if filters.get('status'):
                    query = query.filter(User.is_active == (filters['status'] == 'active'))
                if filters.get('profession'):
                    query = query.filter(User.profession == filters['profession'])
                if filters.get('country'):
                    query = query.filter(User.country == filters['country'])
                
                stats['total_recipients'] = query.count()
            except:
                pass
        
        return render_template('admin/communication/campaign_details.html', 
                             campaign=campaign, stats=stats)
        
    except Exception as e:
        current_app.logger.error(f"Error viewing campaign details: {str(e)}")
        flash(f'Ошибка загрузки деталей кампании: {str(e)}', 'error')
        return redirect(url_for('admin.communication_campaigns'))


def perform_database_backup(backup_record):
    """Perform actual database backup"""
    import os
    import subprocess
    import tempfile
    from datetime import datetime
    
    start_time = datetime.utcnow()
    
    try:
        # Get database URI
        db_uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
        
        # Create backups directory if it doesn't exist
        backup_dir = os.path.join(current_app.root_path, 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create backup file path
        backup_filename = f"{backup_record.backup_name}.sql"
        backup_file_path = os.path.join(backup_dir, backup_filename)
        
        if db_uri.startswith('sqlite:///'):
            # SQLite backup
            import sqlite3
            db_path = db_uri.replace('sqlite:///', '')
            
            # Perform SQLite backup
            source_conn = sqlite3.connect(db_path)
            backup_conn = sqlite3.connect(backup_file_path.replace('.sql', '.db'))
            
            # Copy database
            source_conn.backup(backup_conn)
            
            # Close connections
            source_conn.close()
            backup_conn.close()
            
            # Get file size
            file_size = os.path.getsize(backup_file_path.replace('.sql', '.db'))
            
            # Count tables and records
            conn = sqlite3.connect(backup_file_path.replace('.sql', '.db'))
            cursor = conn.cursor()
            
            # Get table count
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            tables_count = len(tables)
            
            # Get total record count
            total_records = 0
            for table in tables:
                table_name = table[0]
                if table_name != 'sqlite_sequence':  # Skip system table
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    count = cursor.fetchone()[0]
                    total_records += count
            
            conn.close()
            
        elif db_uri.startswith('postgresql://'):
            # PostgreSQL backup using pg_dump
            try:
                # Parse PostgreSQL URI
                import urllib.parse as urlparse
                parsed = urlparse.urlparse(db_uri)
                
                # Set environment variables for pg_dump
                env = os.environ.copy()
                env['PGPASSWORD'] = parsed.password or ''
                
                # Build pg_dump command
                cmd = [
                    'pg_dump',
                    '-h', parsed.hostname or 'localhost',
                    '-p', str(parsed.port or 5432),
                    '-U', parsed.username or 'postgres',
                    '-d', parsed.path[1:] if parsed.path else 'postgres',
                    '--no-password',
                    '--verbose',
                    '--clean',
                    '--if-exists',
                    '--create',
                    '-f', backup_file_path
                ]
                
                # Execute pg_dump
                result = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=300)
                
                if result.returncode != 0:
                    raise Exception(f"pg_dump failed: {result.stderr}")
                
                # Get file size
                file_size = os.path.getsize(backup_file_path)
                
                # Count tables and records using SQLAlchemy
                from sqlalchemy import text
                with db.engine.connect() as conn:
                    # Get table count
                    result = conn.execute(text("""
                        SELECT COUNT(*) 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                    """))
                    tables_count = result.scalar()
                    
                    # Get total record count
                    result = conn.execute(text("""
                        SELECT SUM(n_tup_ins - n_tup_del) as total_records
                        FROM pg_stat_user_tables
                    """))
                    total_records = result.scalar() or 0
                
            except subprocess.TimeoutExpired:
                raise Exception("Backup timeout - database too large")
            except FileNotFoundError:
                raise Exception("pg_dump not found - PostgreSQL tools not installed")
            except Exception as e:
                raise Exception(f"PostgreSQL backup failed: {str(e)}")
        
        else:
            raise Exception(f"Unsupported database type: {db_uri}")
        
        # Calculate duration
        end_time = datetime.utcnow()
        duration = (end_time - start_time).total_seconds()
        
        return {
            'file_path': backup_file_path,
            'file_size': file_size,
            'tables_count': tables_count,
            'records_count': total_records,
            'duration': duration
        }
        
    except Exception as e:
        current_app.logger.error(f"Database backup failed: {str(e)}")
        raise Exception(f"Backup failed: {str(e)}")

@admin_bp.route('/mobile')
@login_required
@admin_required
def mobile_admin():
    """Mobile admin panel"""
    try:
        # Get quick stats with error handling
        stats = {
            'total_users': User.query.count(),
            'active_users': User.query.filter_by(is_active=True).count(),
            'total_topics': ForumTopic.query.count(),
            'total_messages': ForumPost.query.count()
        }
        
        return render_template('admin/mobile_admin.html', stats=stats)
        
    except Exception as e:
        current_app.logger.error(f"Mobile admin error: {str(e)}")
        # Return with default stats if there's an error
        stats = {
            'total_users': 0,
            'active_users': 0,
            'total_topics': 0,
            'total_messages': 0
        }
        return render_template('admin/mobile_admin.html', stats=stats)

@admin_bp.route('/monitoring/dashboard')
@login_required
@admin_required
def monitoring_dashboard():
    """Monitoring dashboard with system health and analytics"""
    try:
        from models import db, User, ForumTopic, ForumPost, RegistrationVisitor, RegistrationLog
        from datetime import datetime, timedelta
        from sqlalchemy import func, desc
        
        # Get basic statistics
        stats = {
            'total_users': User.query.count(),
            'active_users': User.query.filter_by(is_active=True).count(),
            'total_topics': ForumTopic.query.count(),
            'total_messages': ForumPost.query.count()
        }
        
        # Get registration statistics
        try:
            registration_stats = {
                'total_visitors': RegistrationVisitor.query.count(),
                'completed_registrations': RegistrationVisitor.query.filter_by(registration_completed=True).count(),
                'email_entries': RegistrationVisitor.query.filter(RegistrationVisitor.email_entered.isnot(None)).count(),
                'name_entries': RegistrationVisitor.query.filter(RegistrationVisitor.first_name_entered.isnot(None)).count()
            }
        except Exception as e:
            current_app.logger.error(f"Error fetching registration stats: {str(e)}")
            registration_stats = {
                'total_visitors': 0,
                'completed_registrations': 0,
                'email_entries': 0,
                'name_entries': 0
            }
        
        # Get recent activity
        try:
            recent_visitors = RegistrationVisitor.query.order_by(
                desc(RegistrationVisitor.entry_time)
            ).limit(10).all()
        except Exception as e:
            current_app.logger.error(f"Error fetching recent visitors: {str(e)}")
            recent_visitors = []
        
        # Get system health
        try:
            from models import SystemHealthLog
            latest_health = SystemHealthLog.query.order_by(
                desc(SystemHealthLog.created_at)
            ).first()
        except Exception as e:
            current_app.logger.error(f"Error fetching system health: {str(e)}")
            latest_health = None
        
        return render_template('admin/monitoring_dashboard.html', 
                             stats=stats,
                             registration_stats=registration_stats,
                             recent_visitors=recent_visitors,
                             latest_health=latest_health)
        
    except Exception as e:
        current_app.logger.error(f"Monitoring dashboard error: {str(e)}")
        return render_template('admin/monitoring_dashboard.html', 
                             stats={'total_users': 0, 'active_users': 0, 'total_topics': 0, 'total_messages': 0},
                             registration_stats={'total_visitors': 0, 'completed_registrations': 0, 'email_entries': 0, 'name_entries': 0},
                             recent_visitors=[],
                             latest_health=None,
                             error=str(e))

@admin_bp.route('/registration-analytics')
@login_required
@admin_required
def registration_analytics():
    """Аналитика регистрации"""
    from utils.visitor_tracker import VisitorTracker
    from models import RegistrationVisitor, db
    from datetime import datetime, timedelta
    from sqlalchemy import func, desc
    
    # Получаем период (по умолчанию 7 дней)
    days = request.args.get('days', 7, type=int)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Получаем сводку
    summary = VisitorTracker.get_analytics_summary(days)
    
    # Получаем детальную статистику по дням
    try:
        # Try PostgreSQL-compatible date function first
        try:
            daily_stats = db.session.query(
                func.date_trunc('day', RegistrationVisitor.entry_time).label('date'),
                RegistrationVisitor.page_type,
                func.count(RegistrationVisitor.id).label('visits'),
                func.count(func.distinct(RegistrationVisitor.ip_address)).label('unique_visitors'),
                func.count(RegistrationVisitor.email_entered).label('email_entries'),
                func.count(RegistrationVisitor.form_started).label('form_starts'),
                func.count(RegistrationVisitor.form_abandoned).label('form_abandonments'),
                func.count(RegistrationVisitor.registration_completed).label('successful_registrations')
            ).filter(
                RegistrationVisitor.entry_time >= start_date
            ).group_by(
                func.date_trunc('day', RegistrationVisitor.entry_time),
                RegistrationVisitor.page_type
            ).order_by(
                desc('date')
            ).all()
        except Exception:
            # Fallback for SQLite
            daily_stats = db.session.query(
                func.date(RegistrationVisitor.entry_time).label('date'),
                RegistrationVisitor.page_type,
                func.count(RegistrationVisitor.id).label('visits'),
                func.count(func.distinct(RegistrationVisitor.ip_address)).label('unique_visitors'),
                func.count(RegistrationVisitor.email_entered).label('email_entries'),
                func.count(RegistrationVisitor.form_started).label('form_starts'),
                func.count(RegistrationVisitor.form_abandoned).label('form_abandonments'),
                func.count(RegistrationVisitor.registration_completed).label('successful_registrations')
            ).filter(
                RegistrationVisitor.entry_time >= start_date
            ).group_by(
                func.date(RegistrationVisitor.entry_time),
                RegistrationVisitor.page_type
            ).order_by(
                desc('date')
            ).all()
    except Exception as e:
        current_app.logger.error(f"Error fetching daily stats: {str(e)}")
        daily_stats = []
    
    # Получаем последние посетители с email (безопасный запрос)
    try:
        # Используем только базовые поля, которые точно существуют
        recent_visitors = RegistrationVisitor.query.filter(
            RegistrationVisitor.email_entered.isnot(None),
            RegistrationVisitor.entry_time >= start_date
        ).order_by(
            desc(RegistrationVisitor.entry_time)
        ).limit(100).all()
    except Exception as e:
        current_app.logger.error(f"Error fetching recent visitors: {str(e)}")
        # Fallback: пустой список
        recent_visitors = []
    
    # Получаем всех посетителей за период (для подробной аналитики)
    try:
        all_visitors = RegistrationVisitor.query.filter(
            RegistrationVisitor.entry_time >= start_date
        ).order_by(
            desc(RegistrationVisitor.entry_time)
        ).limit(500).all()
    except Exception as e:
        current_app.logger.error(f"Error fetching all visitors: {str(e)}")
        all_visitors = []
    
    # Получаем статистику по странам (если есть данные)
    try:
        country_stats = db.session.query(
            RegistrationVisitor.country,
            func.count(RegistrationVisitor.id).label('visits')
        ).filter(
            RegistrationVisitor.country.isnot(None),
            RegistrationVisitor.entry_time >= start_date
        ).group_by(
            RegistrationVisitor.country
        ).order_by(
            desc('visits')
        ).limit(20).all()
    except Exception as e:
        current_app.logger.error(f"Error fetching country stats: {str(e)}")
        country_stats = []
    
    # Получаем статистику по IP адресам
    try:
        ip_stats = db.session.query(
            RegistrationVisitor.ip_address,
            func.count(RegistrationVisitor.id).label('visits'),
            func.count(RegistrationVisitor.email_entered).label('email_entries'),
            func.count(RegistrationVisitor.registration_completed).label('completed')
        ).filter(
            RegistrationVisitor.entry_time >= start_date
        ).group_by(
            RegistrationVisitor.ip_address
        ).order_by(
            desc('visits')
        ).limit(50).all()
    except Exception as e:
        current_app.logger.error(f"Error fetching IP stats: {str(e)}")
        ip_stats = []
    
    # Получаем статистику по времени (часы дня)
    try:
        hourly_stats = db.session.query(
            func.extract('hour', RegistrationVisitor.entry_time).label('hour'),
            func.count(RegistrationVisitor.id).label('visits'),
            func.count(RegistrationVisitor.registration_completed).label('completed')
        ).filter(
            RegistrationVisitor.entry_time >= start_date
        ).group_by(
            func.extract('hour', RegistrationVisitor.entry_time)
        ).order_by('hour').all()
    except Exception as e:
        current_app.logger.error(f"Error fetching hourly stats: {str(e)}")
        hourly_stats = []
    
    return render_template('admin/registration_analytics.html',
                         summary=summary,
                         daily_stats=daily_stats,
                         recent_visitors=recent_visitors,
                         all_visitors=all_visitors,
                         country_stats=country_stats,
                         ip_stats=ip_stats,
                         hourly_stats=hourly_stats,
                         days=days,
                         start_date=start_date,
                         end_date=end_date)

@admin_bp.route('/visitor-details/<int:visitor_id>')
@login_required
@admin_required
def visitor_details(visitor_id):
    """Get detailed information about a specific visitor"""
    try:
        from models import RegistrationVisitor
        
        visitor = RegistrationVisitor.query.get_or_404(visitor_id)
        
        return render_template('admin/visitor_details.html', visitor=visitor)
        
    except Exception as e:
        current_app.logger.error(f"Error loading visitor details: {str(e)}")
        return f"Error loading visitor details: {str(e)}", 500

@admin_bp.route('/membership-test')
@login_required
@admin_required
def membership_test():
    """Hidden testing panel for membership features"""
    try:
        # Get stats
        total_users = User.query.count()
        premium_users = User.query.filter_by(membership_type='premium').count()
        users_with_qr = User.query.filter(User.qr_code_path.isnot(None)).count()
        
        # Get recent users for testing
        recent_users = User.query.order_by(User.created_at.desc()).limit(20).all()
        
        return render_template('admin/membership_test.html',
            total_users=total_users,
            premium_users=premium_users,
            users_with_qr=users_with_qr,
            recent_users=recent_users
        )
        
    except Exception as e:
        current_app.logger.error(f"Error loading membership test panel: {str(e)}")
        flash(f'Error loading membership test panel: {str(e)}', 'error')
        return redirect(url_for('admin.dashboard'))

@admin_bp.route('/membership-test/activate/<int:user_id>')
@login_required
@admin_required
def test_activate_premium(user_id):
    """Manually activate Premium for testing"""
    try:
        user = User.query.get_or_404(user_id)
        
        from datetime import datetime, timedelta
        user.membership_type = 'premium'
        user.membership_expires = datetime.utcnow() + timedelta(days=30)
        
        # Generate member ID if not exists
        if not user.member_id:
            import hashlib
            user_hash = hashlib.md5(str(user.id).encode()).hexdigest()[:5].upper()
            user.member_id = f"MNT-{user_hash}"
        
        # Generate QR
        from routes.membership_routes import generate_member_qr
        generate_member_qr(user)
        
        db.session.commit()
        
        flash(f'Premium activated for {user.get_display_name()} (ID: {user.member_id})', 'success')
        
    except Exception as e:
        current_app.logger.error(f"Error activating premium for user {user_id}: {str(e)}")
        flash(f'Error activating premium: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('admin.membership_test'))

@admin_bp.route('/membership-test/deactivate/<int:user_id>')
@login_required
@admin_required
def test_deactivate_premium(user_id):
    """Manually deactivate Premium for testing"""
    try:
        user = User.query.get_or_404(user_id)
        
        user.membership_type = 'free'
        user.membership_expires = None
        user.qr_code_path = None
        
        db.session.commit()
        
        flash(f'Premium deactivated for {user.get_display_name()}', 'info')
        
    except Exception as e:
        current_app.logger.error(f"Error deactivating premium for user {user_id}: {str(e)}")
        flash(f'Error deactivating premium: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('admin.membership_test'))

# ========================================
# SOFT DELETE USER MANAGEMENT
# ========================================

@admin_bp.route('/users/soft-delete/<int:user_id>')
@login_required
@admin_required
def soft_delete_user(user_id):
    """Мягкое удаление пользователя - сохраняет данные, но скрывает от обычных запросов"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Проверяем, не пытаемся ли удалить себя
        if user.id == current_user.id:
            flash('Вы не можете удалить свой собственный аккаунт!', 'error')
            return redirect(url_for('admin.users_list'))
        
        # Проверяем, не пытаемся ли удалить другого админа
        if user.role == 'admin' and user.id != current_user.id:
            flash('Вы не можете удалить другого администратора!', 'error')
            return redirect(url_for('admin.users_list'))
        
        # Выполняем мягкое удаление
        user.soft_delete(current_user.id)
        
        flash(f'Пользователь {user.get_display_name()} был мягко удален. Данные сохранены.', 'success')
        
    except Exception as e:
        current_app.logger.error(f"Error soft deleting user {user_id}: {str(e)}")
        flash(f'Ошибка при удалении пользователя: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('admin.users_list'))

@admin_bp.route('/users/restore/<int:user_id>')
@login_required
@admin_required
def restore_user(user_id):
    """Восстановление пользователя после мягкого удаления"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Проверяем, что пользователь действительно удален
        if not user.is_soft_deleted():
            flash('Пользователь не был удален!', 'warning')
            return redirect(url_for('admin.users_list'))
        
        # Восстанавливаем пользователя
        user.restore()
        
        flash(f'Пользователь {user.get_display_name()} был восстановлен.', 'success')
        
    except Exception as e:
        current_app.logger.error(f"Error restoring user {user_id}: {str(e)}")
        flash(f'Ошибка при восстановлении пользователя: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('admin.users_list'))

@admin_bp.route('/users/hard-delete/<int:user_id>')
@login_required
@admin_required
def hard_delete_user(user_id):
    """Жесткое удаление пользователя - удаляет все данные навсегда (только для удаленных пользователей)"""
    try:
        user = User.query.get_or_404(user_id)
        
        # Проверяем, что пользователь был мягко удален
        if not user.is_soft_deleted():
            flash('Сначала выполните мягкое удаление пользователя!', 'error')
            return redirect(url_for('admin.users_list'))
        
        # Проверяем, не пытаемся ли удалить себя
        if user.id == current_user.id:
            flash('Вы не можете удалить свой собственный аккаунт!', 'error')
            return redirect(url_for('admin.users_list'))
        
        # Проверяем, не пытаемся ли удалить другого админа
        if user.role == 'admin' and user.id != current_user.id:
            flash('Вы не можете удалить другого администратора!', 'error')
            return redirect(url_for('admin.users_list'))
        
        # Получаем имя пользователя для сообщения
        user_name = user.get_display_name()
        
        # Явно удаляем daily_assignments перед удалением пользователя
        from models import DailyAssignment
        daily_assignments = DailyAssignment.query.filter_by(user_id=user_id).all()
        if daily_assignments:
            for assignment in daily_assignments:
                db.session.delete(assignment)
            current_app.logger.info(f"Deleted {len(daily_assignments)} daily assignments for user {user_id}")
        
        # Выполняем жесткое удаление
        db.session.delete(user)
        db.session.commit()
        
        flash(f'Пользователь {user_name} был полностью удален из системы.', 'warning')
        
    except Exception as e:
        current_app.logger.error(f"Error hard deleting user {user_id}: {str(e)}")
        flash(f'Ошибка при полном удалении пользователя: {str(e)}', 'error')
        db.session.rollback()
    
    return redirect(url_for('admin.users_list'))

@admin_bp.route('/users/deleted')
@login_required
@admin_required
def deleted_users():
    """Список удаленных пользователей"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        role_filter = request.args.get('role', 'all')
        sort_by = request.args.get('sort', 'deleted_at')
        sort_order = request.args.get('order', 'desc')
        
        # Base query - только удаленные пользователи
        query = User.query.filter(User.is_deleted == True)
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                or_(
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term),
                    User.email.ilike(search_term),
                    User.username.ilike(search_term)
                )
            )
        
        # Apply role filter
        if role_filter != 'all':
            query = query.filter(User.role == role_filter)
        
        # Apply sorting
        if sort_by == 'name':
            order_col = User.first_name
        elif sort_by == 'email':
            order_col = User.email
        elif sort_by == 'deleted_at':
            order_col = User.deleted_at
        elif sort_by == 'created_at':
            order_col = User.created_at
        else:
            order_col = User.deleted_at
        
        if sort_order == 'asc':
            query = query.order_by(order_col.asc())
        else:
            query = query.order_by(order_col.desc())
        
        # Pagination
        users = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Statistics
        stats = {
            'total_deleted': User.query.filter(User.is_deleted == True).count(),
            'deleted_admins': User.query.filter(User.is_deleted == True, User.role == 'admin').count(),
            'deleted_users': User.query.filter(User.is_deleted == True, User.role == 'user').count(),
        }
        
        return render_template('admin/deleted_users.html', 
                             users=users, 
                             stats=stats,
                             search=search,
                             role_filter=role_filter,
                             sort_by=sort_by,
                             sort_order=sort_order,
                             per_page=per_page)
        
    except Exception as e:
        current_app.logger.error(f"Error loading deleted users: {str(e)}")
        return render_template('admin/deleted_users.html', 
                             users=None, 
                             error_message=str(e),
                             per_page=20) 