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
daily_learning_bp = Blueprint('daily_learning', __name__)

# Поддерживаемые языки
SUPPORTED_LANGUAGES = ['en', 'ru', 'nl', 'uk', 'es', 'pt', 'tr', 'fa', 'ar']
DEFAULT_LANGUAGE = 'en'

@daily_learning_bp.before_request
def before_request_daily_learning():
    """Обработка языка для всех маршрутов daily_learning"""
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

@daily_learning_bp.route('/learning-map')
@daily_learning_bp.route('/<string:lang>/learning-map')
@login_required
def learning_map(lang='en'):
    """Learning map with PersonalLearningPlan integration"""
    
    # СНАЧАЛА проверяем PersonalLearningPlan
    personal_plan = PersonalLearningPlan.query.filter_by(
        user_id=current_user.id, 
        status='active'
    ).first()
    
    if personal_plan:
        try:
            # Используем существующий персональный план
            daily_plan_result = generate_from_personal_plan(personal_plan)
            # Адаптируем результат для шаблона
            daily_plan_result = _adapt_daily_plan_for_template(daily_plan_result)
            logger.info(f"Using PersonalLearningPlan {personal_plan.id} for user {current_user.id}")
        except Exception as e:
            logger.error(f"Failed to generate from personal plan: {e}")
            # Создать новый план вместо fallback
            daily_plan_result = create_emergency_plan(current_user.id)
            daily_plan_result = _adapt_daily_plan_for_template(daily_plan_result)
    else:
        logger.warning(f"No PersonalLearningPlan found for user {current_user.id}")
        # ИСПРАВЛЕНИЕ: Создать emergency plan вместо редиректа
        flash('Создаем временный план обучения', 'info')
        daily_plan_result = create_emergency_plan(current_user.id)
        daily_plan_result = _adapt_daily_plan_for_template(daily_plan_result)
    
    # Получаем данные для шаблона
    try:
        # Получаем прогресс пользователя
        user_progress = UserProgress.query.filter_by(user_id=current_user.id).all()
        completed_lessons = [p for p in user_progress if p.completed]
        
        # Получаем статистику по доменам
        domain_stats = {}
        if personal_plan:
            domain_analysis = personal_plan.get_domain_analysis()
            if domain_analysis:
                for domain_code, domain_data in domain_analysis.items():
                    if isinstance(domain_data, dict):
                        domain_stats[domain_code] = {
                            'name': get_domain_name(domain_code),
                            'score': domain_data.get('score', 0),
                            'questions_answered': domain_data.get('questions_answered', 0)
                        }
        
        # Собираем planner_data (ожидается шаблоном)
        planner_data = {
            'has_active_plan': bool(personal_plan),
            'plan_progress': personal_plan.overall_progress if personal_plan else 0,
            'exam_readiness': float(personal_plan.estimated_readiness or personal_plan.calculate_readiness()) if personal_plan else 0.0,
            'weak_domains': personal_plan.get_weak_domains() if personal_plan else [],
            'strong_domains': personal_plan.get_strong_domains() if personal_plan else [],
            'next_milestone': None
        }
        
        # Берем ближайший незавершенный milestone
        if personal_plan:
            try:
                milestones = personal_plan.get_milestones()
                for milestone in milestones:
                    if not milestone.get('completed', False):
                        planner_data['next_milestone'] = milestone
                        break
            except Exception:
                pass
        
        # В шаблон передаем непосредственно объект плана (sections/estimated_time/...) 
        daily_plan = daily_plan_result.get('daily_plan', daily_plan_result)
        
        # Подготавливаем данные для JavaScript
        diagnostic_results = {
            'domains': [],
            'overall_score': personal_plan.overall_progress if personal_plan else 0,
            'total_hours': 0,
            'exam_date': None
        }
        
        # Добавляем домены из domain_stats
        if domain_stats:
            for domain_code, domain_data in domain_stats.items():
                diagnostic_results['domains'].append({
                    'code': domain_code,
                    'name': domain_data['name'],
                    'score': domain_data['score'],
                    'questions_answered': domain_data['questions_answered']
                })
        
        # Получаем study sessions для календаря
        study_sessions = []
        if personal_plan:
            from models import StudySession
            sessions = StudySession.query.filter_by(
                learning_plan_id=personal_plan.id,
                status='planned'
            ).limit(10).all()
            
            for session in sessions:
                study_sessions.append({
                    'id': session.id,
                    'title': f"{session.session_type.title()} Session",
                    'start': getattr(session, 'planned_start_time', None).isoformat() if getattr(session, 'planned_start_time', None) else None,
                    'duration': session.planned_duration,
                    'type': session.session_type,
                    'domain': session.domain_id
                })
        
        diagnostic_results['study_sessions'] = study_sessions
        
        return render_template('learning/learning_map.html',
                             daily_plan=daily_plan,
                             planner_data=planner_data,
                             diagnostic_results=diagnostic_results,
                             user=current_user,
                             completed_lessons=len(completed_lessons),
                             domain_stats=domain_stats,
                             active_plan=personal_plan,
                             plan_id=(personal_plan.id if personal_plan else None),
                             lang=lang)
                              
    except Exception as e:
        logger.error(f"Error rendering learning map for user {current_user.id}: {e}")
        flash('Ошибка при загрузке плана обучения', 'error')
        # Вместо редиректа показываем пустую страницу
        return render_template('learning/learning_map.html',
                             daily_plan={},
                             planner_data={'has_active_plan': False},
                             diagnostic_results={'domains': []},
                             user=current_user,
                             completed_lessons=0,
                             domain_stats={},
                             active_plan=None,
                             plan_id=None,
                             lang=lang)

@daily_learning_bp.route('/knowledge-base')
@daily_learning_bp.route('/<string:lang>/knowledge-base')
@login_required  
def knowledge_base(lang='en'):
    """Knowledge Base - показывает все предметы для свободного изучения"""
    from models import Subject, Module, LearningPath, ContentCategory
    from utils.unified_stats import get_module_stats_unified, get_unified_user_stats
    
    def get_user_recommendations(user_id, limit=3):
        """Получает рекомендации модулей для пользователя на основе его прогресса."""
        try:
            recommendations = []
            
            # Получаем завершенные уроки пользователя
            completed_lessons = UserProgress.query.filter_by(
                user_id=user_id, 
                completed=True
            ).all()
            
            if not completed_lessons:
                # Если нет завершенных уроков, рекомендуем первые модули
                first_modules = db.session.query(
                    Module, Subject.name.label('subject_name')
                ).join(
                    Subject, Subject.id == Module.subject_id
                ).order_by(
                    Module.order, Module.id
                ).limit(limit).all()
                
                for mod, subj_name in first_modules:
                    recommendations.append({
                        'module_id': mod.id,
                        'title': mod.title,
                        'icon': getattr(mod, 'icon', 'journal-text'),
                        'subject_name': subj_name
                    })
                
                return recommendations
            
            # Получаем ID завершенных уроков
            completed_lesson_ids = [lesson.lesson_id for lesson in completed_lessons]
            
            # Получаем модули с завершенными уроками
            modules_with_completed_lessons = db.session.query(
                Module.id, Module.title, Module.icon, Subject.name.label('subject_name'),
                db.func.count(Lesson.id).label('total_lessons'),
                db.func.count(db.case((Lesson.id.in_(completed_lesson_ids), 1))).label('completed_lessons')
            ).join(
                Lesson, Module.id == Lesson.module_id
            ).join(
                Subject, Subject.id == Module.subject_id
            ).group_by(
                Module.id, Module.title, Module.icon, Subject.name
            ).having(
                db.func.count(db.case((Lesson.id.in_(completed_lesson_ids), 1))) > 0
            ).all()
            
            # Обрабатываем модули с прогрессом
            processed_module_ids = set()
            for module_data in modules_with_completed_lessons:
                module_id, title, icon, subject_name, total_lessons, completed_lessons = module_data
                
                if completed_lessons == total_lessons:
                    # Модуль полностью завершен
                    processed_module_ids.add(module_id)
                else:
                    # Модуль частично завершен - добавляем в рекомендации
                    recommendations.append({
                        'module_id': module_id,
                        'title': title,
                        'icon': icon or 'journal-text',
                        'subject_name': subject_name,
                        'progress': f"{completed_lessons}/{total_lessons}"
                    })
            
            # Если нужно больше рекомендаций, добавляем новые модули
            remaining_limit = limit - len(recommendations)
            if remaining_limit > 0:
                next_modules_data = db.session.query(
                    Module, Subject.name.label('subject_name')
                ).join(
                    Subject, Subject.id == Module.subject_id
                ).filter(
                    ~Module.id.in_(list(processed_module_ids))
                ).order_by(
                    Module.order, Module.id 
                ).limit(remaining_limit).all()
                
                for mod, subj_name in next_modules_data:
                    recommendations.append({
                        'module_id': mod.id,
                        'title': mod.title,
                        'icon': getattr(mod, 'icon', 'journal-text'),
                        'subject_name': subj_name
                    })
            
            return recommendations[:limit]
            
        except Exception as e:
            current_app.logger.error(f"Ошибка при получении рекомендаций для пользователя {user_id}: {str(e)}", exc_info=True)
            return []
    
    def get_random_fact(lang):
        """Возвращает случайный факт о стоматологии на указанном языке."""
        try:
            import json
            import os
            facts_file_path = os.path.join(current_app.root_path, 'data', 'dental_facts.json')
            with open(facts_file_path, 'r', encoding='utf-8') as file:
                all_facts_data = json.load(file)
            
            facts_list = all_facts_data.get('facts', [])
            
            if not facts_list:
                return {
                    'text': 'Стоматология - важная область медицины',
                    'source': 'Общие знания'
                }
            
            # Фильтруем факты по языку
            lang_facts = [fact for fact in facts_list if fact.get('lang', 'en') == lang]
            
            if not lang_facts:
                # Если нет фактов на нужном языке, берем английские
                lang_facts = [fact for fact in facts_list if fact.get('lang', 'en') == 'en']
            
            if not lang_facts:
                # Если нет фактов вообще, возвращаем первый
                return facts_list[0] if facts_list else {
                    'text': 'Стоматология - важная область медицины',
                    'source': 'Общие знания'
                }
            
            return random.choice(lang_facts)
            
        except Exception as e:
            current_app.logger.error(f"Ошибка при получении случайного факта: {str(e)}", exc_info=True)
            return {
                'text': 'Стоматология - важная область медицины',
                'source': 'Общие знания'
            }
    
    try:
        # Получаем все предметы
        all_subjects = Subject.query.all()
        
        # Добавляем прогресс для каждого предмета
        for subject in all_subjects:
            try:
                # Получаем все модули предмета
                current_subject_modules = Module.query.filter_by(subject_id=subject.id).all()
                total_lessons = 0
                completed_lessons = 0
                
                for module in current_subject_modules:
                    module_stats = get_module_stats_unified(module.id, current_user.id)
                    total_lessons += module_stats.get("total_lessons", 0)
                    completed_lessons += module_stats.get("completed_lessons", 0)
                
                # Вычисляем прогресс предмета
                if total_lessons > 0:
                    progress_percentage = int((completed_lessons / total_lessons) * 100)
                else:
                    progress_percentage = 0
                
                # Добавляем вычисленные данные к объекту предмета
                subject.progress_percentage = progress_percentage
                subject.total_lessons = total_lessons
                subject.completed_lessons = completed_lessons
                subject.is_completed = progress_percentage == 100
                subject.estimated_time = f"{max(1, total_lessons // 10)}h"  # Примерная оценка времени
                
                # Добавляем категорию по умолчанию если её нет
                if not hasattr(subject, 'category') or not subject.category:
                    subject.category = 'general'
                    
            except Exception as e:
                # Устанавливаем значения по умолчанию при ошибке
                subject.progress_percentage = 0
                subject.total_lessons = 0
                subject.completed_lessons = 0
                subject.is_completed = False
                subject.estimated_time = "2h"
                subject.category = 'general'
        
        # Получаем дополнительные данные
        learning_paths = LearningPath.query.all()
        content_categories = ContentCategory.query.order_by(ContentCategory.order).all()
        stats = get_unified_user_stats(current_user.id)
        recommendations = get_user_recommendations(current_user.id)
        random_fact = get_random_fact(g.lang)
        
        return render_template(
            'learning/subject_view.html',  # Используем существующий шаблон
            title="Knowledge Base",
            learning_paths=learning_paths,
            content_categories=content_categories,
            all_subjects=all_subjects,
            stats=stats,
            recommendations=recommendations,
            random_fact=random_fact,
            is_knowledge_base=True  # Флаг для шаблона
        )
        
    except Exception as e:
        current_app.logger.error(f"Ошибка в knowledge_base: {e}", exc_info=True)
        return render_template('errors/500.html'), 500

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
        
        db.session.commit()
        
        # Trigger ability recalculation
        algorithm = DailyLearningAlgorithm()
        try:
            algorithm._analyze_current_abilities(current_user.id)
        except Exception as e:
            current_app.logger.error(f"Failed to update abilities: {e}")
        
        return jsonify({
            'success': True,
            'session_id': session.id,
            'status': session.status
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
                    'message': 'Session completed and ability updated successfully'
                })
            else:
                return jsonify({
                    'status': 'success',
                    'session_id': session_id,
                    'ability_updated': session.ability_updated,
                    'feedback_processed': session.feedback_processed,
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