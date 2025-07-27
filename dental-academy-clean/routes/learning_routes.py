# routes/learning_routes.py - Learning system routes

from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, g
from flask_login import login_required, current_user
from utils.serializers import safe_jsonify
from models import LearningPath, Subject, Module, Lesson, UserProgress
from extensions import db
from datetime import datetime, timezone
from functools import wraps
from flask import session
from models import PersonalLearningPlan, Question, BIGDomain

learning_bp = Blueprint('learning', __name__)

@learning_bp.route('/')
@login_required
def index():
    """Learning map - overview of all learning paths"""
    
    learning_paths = []
    for path in LearningPath.query.filter_by(is_active=True).order_by(LearningPath.order).all():
        
        # Calculate progress for this path
        total_lessons = 0
        completed_lessons = 0
        
        for subject in path.subjects:
            subject_progress = subject.get_progress_for_user(current_user.id)
            total_lessons += subject_progress['total_lessons']
            completed_lessons += subject_progress['completed_lessons']
        
        progress_percent = int((completed_lessons / total_lessons * 100)) if total_lessons > 0 else 0
        
        path_data = {
            'path': path,
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'progress_percent': progress_percent,
            'subjects_count': path.subjects.count()
        }
        learning_paths.append(path_data)
    
    return render_template('learning/index.html', learning_paths=learning_paths)

@learning_bp.route('/path/<int:path_id>')
@login_required
def learning_path(path_id):
    """View specific learning path with subjects"""
    
    path = LearningPath.query.get_or_404(path_id)
    
    subjects_data = []
    for subject in path.subjects.order_by(Subject.order).all():
        subject_progress = subject.get_progress_for_user(current_user.id)
        subjects_data.append({
            'subject': subject,
            **subject_progress
        })
    
    # Calculate path totals
    path_total_lessons = sum(s['total_lessons'] for s in subjects_data)
    path_completed_lessons = sum(s['completed_lessons'] for s in subjects_data)
    path_progress_percent = int((path_completed_lessons / path_total_lessons * 100)) if path_total_lessons > 0 else 0
    
    return render_template('learning/path.html',
                         path=path,
                         subjects=subjects_data,
                         total_lessons=path_total_lessons,
                         completed_lessons=path_completed_lessons,
                         progress_percent=path_progress_percent)

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
    
    # Add time spent
    if time_spent > 0:
        progress.add_time_spent(time_spent)
    
    try:
        db.session.commit()
        
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
    
    try:
        db.session.commit()
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
    
    if weak_domains:
        for domain_name in weak_domains:
            domain_questions = Question.query.join(BIGDomain).filter(
                BIGDomain.name.contains(domain_name)
            ).limit(5).all()
            practice_questions.extend(domain_questions)
    
    # If no domain-specific questions, get general questions
    if not practice_questions:
        practice_questions = Question.query.limit(10).all()
    
    return render_template('learning/automated_practice.html',
                         plan=plan,
                         current_week=week,
                         current_session=current_session,
                         practice_questions=practice_questions)

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
        
        # Добавляем диагностику
        current_app.logger.info(f"Complete session request - plan_id: {plan_id}, week: {current_week}, session: {current_session}")
        
        if not plan_id or not current_session:
            current_app.logger.error(f"Missing session data - plan_id: {plan_id}, current_session: {current_session}")
            return safe_jsonify({'error': 'No active session'}), 400
        
        plan = PersonalLearningPlan.query.get_or_404(plan_id)
        current_app.logger.info(f"Found plan: {plan.id} for user: {plan.user_id}")
        
        # Get study schedule
        study_schedule = plan.get_study_schedule()
        current_app.logger.info(f"Study schedule keys: {list(study_schedule.keys()) if study_schedule else 'None'}")
        
        if not study_schedule or 'weekly_schedule' not in study_schedule:
            current_app.logger.error(f"Invalid study schedule: {study_schedule}")
            return safe_jsonify({'error': 'Invalid study schedule'}), 500
        
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
            
            # Determine next redirect
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
            session.pop('learning_plan_id', None)
            session.pop('current_week', None)
            session.pop('current_session', None)
            session.pop('learning_mode', None)
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
