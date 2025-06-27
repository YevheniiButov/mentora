from flask import (
    Blueprint, render_template, request, jsonify, redirect, url_for, g, flash, session, current_app, abort
)
from flask_login import login_required, current_user
from datetime import datetime, timedelta
import json
import random
from extensions import db
from models import (
    AssessmentCategory, AssessmentQuestion, PreAssessmentAttempt, 
    PreAssessmentAnswer, LearningPlan, User
)
from translations_new import get_translation as t
from data.dutch_assessment_categories import REGIONAL_FOCUS

assessment_bp = Blueprint(
    "assessment_bp",
    __name__,
    url_prefix='/<string:lang>/assessment',
    template_folder='../templates'
)

@assessment_bp.before_request
def before_request_assessment():
    """Извлекает и валидирует язык из URL"""
    try:
        lang_from_url = request.view_args.get('lang') if request.view_args else None
        
        SUPPORTED_LANGUAGES = ['en', 'ru', 'nl', 'uk', 'es', 'pt', 'tr', 'fa', 'ar']
        DEFAULT_LANGUAGE = 'en'
        
        if lang_from_url and lang_from_url in SUPPORTED_LANGUAGES:
            g.lang = lang_from_url
        else:
            g.lang = session.get('lang') or DEFAULT_LANGUAGE
        
        if session.get('lang') != g.lang:
            session['lang'] = g.lang
            
    except Exception as e:
        current_app.logger.error(f"Error in before_request_assessment: {e}")
        g.lang = 'en'

@assessment_bp.context_processor
def inject_lang_assessment():
    """Добавляет lang в контекст шаблонов"""
    return dict(lang=getattr(g, 'lang', 'en'))

@assessment_bp.route('/')
@login_required
def intro(lang):
    """Начальная страница предварительной оценки"""
    g.lang = lang
    
    # Проверяем, проходил ли пользователь оценку ранее
    previous_attempt = PreAssessmentAttempt.query.filter_by(
        user_id=current_user.id,
        is_completed=True
    ).order_by(PreAssessmentAttempt.completed_at.desc()).first()
    
    # Статистика оценки
    total_questions = AssessmentQuestion.query.filter_by(is_active=True).count()
    
    # Получаем категории для предварительной оценки (не нидерландские)
    categories = AssessmentCategory.query.filter_by(is_dutch_specific=False).order_by(AssessmentCategory.name).all()
    
    # Общая статистика прохождения
    total_assessments = PreAssessmentAttempt.query.filter_by(is_completed=True).count()
    avg_stats = db.session.query(
        db.func.avg(PreAssessmentAttempt.time_spent).label('avg_time'),
        db.func.avg(PreAssessmentAttempt.total_score).label('avg_score')
    ).filter_by(is_completed=True).first()
    
    return render_template(
        'assessment/intro.html',
        title=t('pre_assessment_title', lang=g.lang),
        total_questions=total_questions,
        categories=categories,
        previous_attempt=previous_attempt,
        total_assessments=total_assessments,
        avg_time=int(avg_stats.avg_time / 60) if avg_stats.avg_time else 45,
        avg_score=int(avg_stats.avg_score) if avg_stats.avg_score else 70,
        estimated_time=60  # минут
    )

@assessment_bp.route('/start', methods=['POST'])
@login_required
def start_assessment(lang):
    """Начало прохождения оценки"""
    g.lang = lang
    
    try:
        # Получаем данные из запроса
        data = request.get_json() or {}
        selected_categories = data.get('selected_categories', ['knowledge', 'communication', 'preclinical', 'workstation'])
        
        # Проверяем, нет ли незавершенной попытки
        existing_attempt = PreAssessmentAttempt.query.filter_by(
            user_id=current_user.id,
            is_completed=False
        ).first()
        
        if existing_attempt:
            # Удаляем незавершенную попытку
            PreAssessmentAnswer.query.filter_by(attempt_id=existing_attempt.id).delete()
            db.session.delete(existing_attempt)
        
        # Создаем новую попытку
        attempt = PreAssessmentAttempt(
            user_id=current_user.id,
            started_at=datetime.utcnow(),
            total_questions=50
        )
        
        db.session.add(attempt)
        db.session.flush()  # Получаем ID
        
        # Выбираем вопросы для оценки с учетом выбранных категорий
        selected_questions = select_assessment_questions(selected_categories)
        
        # Сохраняем порядок вопросов в сессии
        session['assessment_attempt_id'] = attempt.id
        session['assessment_questions'] = [q.id for q in selected_questions]
        session['current_question_index'] = 0
        session['assessment_start_time'] = datetime.utcnow().isoformat()
        session['selected_categories'] = selected_categories
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'attempt_id': attempt.id,
            'redirect_url': url_for('assessment_bp.question', lang=g.lang, question_num=1)
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error starting assessment: {e}")
        return jsonify({
            'success': False,
            'error': t('error_starting_assessment', lang=g.lang)
        }), 500

@assessment_bp.route('/question/<int:question_num>')
@login_required 
def question(lang, question_num):
    """Отображение конкретного вопроса"""
    g.lang = lang
    
    # Проверяем сессию
    if 'assessment_attempt_id' not in session:
        flash(t('assessment_session_expired', lang=g.lang), 'warning')
        return redirect(url_for('assessment_bp.intro', lang=g.lang))
    
    attempt_id = session['assessment_attempt_id']
    question_ids = session.get('assessment_questions', [])
    
    # Усиленная защита: если вопросов нет или номер некорректен
    if not question_ids or question_num < 1 or question_num > len(question_ids):
        flash(t('invalid_question_number', lang=g.lang) + '. ' + t('start_new_attempt', lang=g.lang), 'error')
        return redirect(url_for('assessment_bp.intro', lang=g.lang))
    
    # Получаем вопрос
    question_id = question_ids[question_num - 1]
    question = AssessmentQuestion.query.get_or_404(question_id)
    
    # Проверяем, отвечал ли пользователь на этот вопрос
    existing_answer = PreAssessmentAnswer.query.filter_by(
        attempt_id=attempt_id,
        question_id=question_id
    ).first()
    
    # Вычисляем прогресс
    progress = (question_num / len(question_ids)) * 100
    
    # Оставшееся время (60 минут общего времени)
    start_time = datetime.fromisoformat(session['assessment_start_time'])
    elapsed_time = (datetime.utcnow() - start_time).total_seconds()
    remaining_time = max(0, 3600 - elapsed_time)  # 3600 секунд = 60 минут
    
    return render_template(
        'assessment/question.html',
        question=question,
        question_num=question_num,
        total_questions=len(question_ids),
        progress=round(progress, 1),
        remaining_time=int(remaining_time),
        existing_answer=existing_answer
    )

@assessment_bp.route('/answer', methods=['POST'])
@login_required
def submit_answer(lang):
    """Сохранение ответа на вопрос"""
    g.lang = lang
    
    try:
        data = request.get_json()
        question_id = data.get('question_id')
        user_answer = data.get('answer')
        time_spent = data.get('time_spent', 0)
        
        # Валидация
        if not question_id or user_answer is None:
            return jsonify({'success': False, 'error': 'Invalid data'}), 400
        
        attempt_id = session.get('assessment_attempt_id')
        if not attempt_id:
            return jsonify({'success': False, 'error': 'Session expired'}), 400
        
        question = AssessmentQuestion.query.get(question_id)
        if not question:
            return jsonify({'success': False, 'error': 'Question not found'}), 404
        
        # Проверяем правильность ответа
        is_correct = user_answer == question.correct_answer
        points_earned = question.points if is_correct else 0
        
        # Сохраняем или обновляем ответ
        existing_answer = PreAssessmentAnswer.query.filter_by(
            attempt_id=attempt_id,
            question_id=question_id
        ).first()
        
        if existing_answer:
            existing_answer.user_answer = user_answer
            existing_answer.is_correct = is_correct
            existing_answer.points_earned = points_earned
            existing_answer.time_spent = time_spent
            existing_answer.answered_at = datetime.utcnow()
        else:
            answer = PreAssessmentAnswer(
                attempt_id=attempt_id,
                question_id=question_id,
                user_answer=user_answer,
                is_correct=is_correct,
                points_earned=points_earned,
                time_spent=time_spent
            )
            db.session.add(answer)
        
        # Обновляем статистику вопроса
        question.times_asked += 1
        if is_correct:
            question.times_correct += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'is_correct': is_correct,
            'explanation': question.explanation if is_correct else None
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error submitting answer: {e}")
        return jsonify({'success': False, 'error': 'Server error'}), 500

@assessment_bp.route('/navigation', methods=['POST'])
@login_required
def navigate(lang):
    """Навигация между вопросами"""
    g.lang = lang
    
    data = request.get_json()
    direction = data.get('direction')  # 'next' или 'previous'
    current_question = data.get('current_question', 1)
    
    question_ids = session.get('assessment_questions', [])
    total_questions = len(question_ids)
    
    if direction == 'next':
        next_question = min(current_question + 1, total_questions)
    elif direction == 'previous':
        next_question = max(current_question - 1, 1)
    else:
        return jsonify({'success': False, 'error': 'Invalid direction'}), 400
    
    # Если это последний вопрос и пользователь идет дальше - завершаем тест
    if direction == 'next' and current_question == total_questions:
        return jsonify({
            'success': True,
            'action': 'complete',
            'redirect_url': url_for('assessment_bp.complete', lang=g.lang)
        })
    
    return jsonify({
        'success': True,
        'action': 'navigate',
        'redirect_url': url_for('assessment_bp.question', lang=g.lang, question_num=next_question)
    })

@assessment_bp.route('/complete')
@login_required
def complete(lang):
    """Завершение оценки и расчет результатов"""
    g.lang = lang
    
    attempt_id = session.get('assessment_attempt_id')
    if not attempt_id:
        flash(t('assessment_session_expired', lang=g.lang), 'warning')
        return redirect(url_for('assessment_bp.intro', lang=g.lang))
    
    try:
        # Получаем попытку
        attempt = PreAssessmentAttempt.query.get(attempt_id)
        if not attempt or attempt.is_completed:
            return redirect(url_for('assessment_bp.results', lang=g.lang, attempt_id=attempt_id))
        
        # Рассчитываем результаты
        results = calculate_assessment_results(attempt)
        
        # Обновляем попытку
        attempt.completed_at = datetime.utcnow()
        attempt.is_completed = True
        attempt.correct_answers = results['total_correct']
        attempt.total_score = results['total_score']
        attempt.time_spent = (attempt.completed_at - attempt.started_at).total_seconds()
        
        # Сохраняем результаты по категориям
        attempt.set_category_scores(results['category_scores'])
        
        # Анализируем результаты и создаем рекомендации
        analysis = analyze_assessment_results(attempt)
        
        # Сохраняем рекомендации
        attempt.set_recommended_plan(analysis)
        
        db.session.commit()
        
        # Очищаем сессию
        session.pop('assessment_attempt_id', None)
        session.pop('assessment_questions', None)
        session.pop('current_question_index', None)
        session.pop('assessment_start_time', None)
        
        return redirect(url_for('assessment_bp.results', lang=g.lang, attempt_id=attempt.id))
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error completing assessment: {e}")
        flash(t('error_completing_assessment', lang=g.lang), 'error')
        return redirect(url_for('assessment_bp.intro', lang=g.lang))

@assessment_bp.route('/results/<int:attempt_id>')
@login_required
def results(lang, attempt_id):
    """Отображение результатов оценки"""
    g.lang = lang
    
    attempt = PreAssessmentAttempt.query.filter_by(
        id=attempt_id,
        user_id=current_user.id,
        is_completed=True
    ).first_or_404()
    
    # Получаем анализ результатов с правильным форматом рекомендаций
    analysis = analyze_assessment_results(attempt)
    category_scores = attempt.get_category_scores()
    
    # Форматируем данные для отображения
    results_data = {
        'overall_score': attempt.total_score,
        'correct_answers': attempt.correct_answers,
        'total_questions': attempt.total_questions,
        'time_spent': format_time_spent(attempt.time_spent),
        'completion_time': format_time_spent(attempt.time_spent),
        'accuracy': round((attempt.correct_answers / attempt.total_questions) * 100, 1),
        'completion_date': attempt.completed_at,
        'category_results': format_category_results(category_scores),
        'categories': format_category_results(category_scores),
        'skill_level': analysis.get('overall_level', 'intermediate'),
        'skill_description': analysis.get('skill_description', 'Средний уровень подготовки'),
        'strengths': analysis.get('strengths', []),
        'weaknesses': analysis.get('weaknesses', []),
        'recommendations': analysis.get('recommendations', [])[:5],  # Топ-5
        'study_time_estimate': analysis.get('study_time_estimate', {}),
        'learning_plan_preview': analysis.get('learning_plan', {})
    }
    
    return render_template(
        'assessment/results.html',
        attempt=attempt,
        results=results_data,
        title=t('assessment_results_title', lang=g.lang)
    )

@assessment_bp.route('/create-plan/<int:attempt_id>', methods=['GET', 'POST'])
@login_required
def create_learning_plan(lang, attempt_id):
    """Создание персонализированного плана обучения"""
    g.lang = lang
    
    attempt = PreAssessmentAttempt.query.filter_by(
        id=attempt_id,
        user_id=current_user.id,
        is_completed=True
    ).first_or_404()
    
    if request.method == 'GET':
        # Показываем форму настройки плана
        return render_template(
            'assessment/plan_preferences.html',
            attempt=attempt,
            preferences={},  # Пустой словарь для новых предпочтений
            title=t('create_learning_plan_title', lang=g.lang)
        )
    
    try:
        # Получаем предпочтения пользователя из формы
        # Обычная HTML-форма отправляется как form-data, не JSON
        form_data = request.form.to_dict()
        
        # Создаем простой план обучения
        plan_name = f"Персонализированный план - {datetime.utcnow().strftime('%d.%m.%Y')}"
        
        # Анализируем результаты для создания плана
        analysis = attempt.get_recommended_plan()
        category_scores = attempt.get_category_scores()
        
        # Определяем слабые области для фокуса
        weak_areas = []
        for category_id, scores in category_scores.items():
            if scores['score'] < 70:  # Меньше 70% - слабая область
                category = AssessmentCategory.query.get(int(category_id))
                if category:
                    weak_areas.append(category.name)
        
        # Создаем структуру плана
        plan_structure = {
            'focus_areas': weak_areas[:3],  # Топ-3 слабые области
            'estimated_duration': 40,  # часов
            'modules': [
                {
                    'title': 'Базовые концепции',
                    'duration': 10,
                    'priority': 'high'
                },
                {
                    'title': 'Практические навыки',
                    'duration': 15,
                    'priority': 'medium'
                },
                {
                    'title': 'Продвинутые темы',
                    'duration': 15,
                    'priority': 'low'
                }
            ]
        }
        
        # Создаем план в базе данных
        plan = LearningPlan(
            user_id=current_user.id,
            assessment_attempt_id=attempt_id,
            plan_name=plan_name,
            description=f"Персонализированный план на основе оценки от {attempt.completed_at.strftime('%d.%m.%Y')}",
            difficulty_level='intermediate',
            estimated_duration=40,
            plan_structure=json.dumps(plan_structure, ensure_ascii=False),
            total_modules=3,
            completed_modules=0,
            is_active=True,
            started_at=datetime.utcnow()
        )
        
        db.session.add(plan)
        db.session.commit()
        
        # Для обычной HTML-формы всегда делаем редирект
        flash(t('learning_plan_created_success', lang=g.lang), 'success')
        return redirect(url_for('assessment_bp.view_plan', lang=g.lang, plan_id=plan.id))
        
    except Exception as e:
        current_app.logger.error(f"Error creating learning plan: {e}")
        flash(t('error_creating_plan', lang=g.lang), 'error')
        # При ошибке возвращаемся к форме с пустыми предпочтениями
        return render_template(
            'assessment/plan_preferences.html',
            attempt=attempt,
            preferences={},  # Пустой словарь для избежания UndefinedError
            title=t('create_learning_plan_title', lang=g.lang)
        )

@assessment_bp.route('/plan/<int:plan_id>')
@login_required
def view_plan(lang, plan_id):
    """Просмотр созданного плана обучения"""
    g.lang = lang
    
    plan = LearningPlan.query.filter_by(
        id=plan_id,
        user_id=current_user.id
    ).first_or_404()
    
    plan_structure = plan.get_plan_structure()
    
    # Текущий прогресс
    progress_data = calculate_plan_progress(plan)
    
    return render_template(
        'assessment/learning_plan.html',
        plan=plan,
        plan_structure=plan_structure,
        progress=progress_data,
        title=f"{t('learning_plan_title', lang=g.lang)}: {plan.plan_name}"
    )

@assessment_bp.route('/api/questions/random')
@login_required
def api_random_questions(lang):
    """API: получение случайных вопросов для быстрой оценки"""
    g.lang = lang
    
    count = min(int(request.args.get('count', 10)), 20)  # Максимум 20 вопросов
    category_id = request.args.get('category_id')
    
    query = AssessmentQuestion.query.filter_by(is_active=True)
    
    if category_id:
        query = query.filter_by(category_id=category_id)
    
    questions = query.all()
    
    if len(questions) > count:
        questions = random.sample(questions, count)
    
    questions_data = []
    for q in questions:
        questions_data.append({
            'id': q.id,
            'category': q.category.name,
            'question': q.question_text,
            'options': q.get_options(),
            'difficulty': q.difficulty_level,
            'time_limit': q.time_limit
        })
    
    return jsonify({
        'questions': questions_data,
        'total': len(questions_data)
    })

@assessment_bp.route('/api/statistics')
@login_required
def api_assessment_statistics(lang):
    """API: статистика прохождения оценок"""
    g.lang = lang
    
    # Общая статистика
    stats = db.session.query(
        db.func.count(PreAssessmentAttempt.id).label('total_attempts'),
        db.func.avg(PreAssessmentAttempt.total_score).label('avg_score'),
        db.func.avg(PreAssessmentAttempt.time_spent).label('avg_time')
    ).filter_by(is_completed=True).first()
    
    # Статистика пользователя
    user_attempts = PreAssessmentAttempt.query.filter_by(
        user_id=current_user.id,
        is_completed=True
    ).order_by(PreAssessmentAttempt.completed_at.desc()).limit(5).all()
    
    user_stats = []
    for attempt in user_attempts:
        user_stats.append({
            'id': attempt.id,
            'score': attempt.total_score,
            'date': attempt.completed_at.isoformat(),
            'time_spent': attempt.time_spent
        })
    
    return jsonify({
        'global_stats': {
            'total_attempts': stats.total_attempts or 0,
            'average_score': round(stats.avg_score or 0, 1),
            'average_time': round((stats.avg_time or 0) / 60, 1)  # в минутах
        },
        'user_stats': user_stats
    })

# Вспомогательные функции

def select_assessment_questions(selected_categories):
    """Выбор вопросов для оценки с учетом выбранных категорий"""
    
    categories = AssessmentCategory.query.all()
    selected_questions = []
    
    for category in categories:
        if category.slug in selected_categories:
            # Количество вопросов из каждой категории
            questions_needed = min(category.max_questions, 
                                 max(category.min_questions, 
                                     int(50 * (category.weight / sum(c.weight for c in categories)))))
            
            # Получаем вопросы категории
            category_questions = AssessmentQuestion.query.filter_by(
                category_id=category.id,
                is_active=True
            ).all()
            
            if len(category_questions) > questions_needed:
                # Выбираем случайные вопросы, но с балансом по сложности
                easy = [q for q in category_questions if q.difficulty_level <= 2]
                medium = [q for q in category_questions if q.difficulty_level == 3]
                hard = [q for q in category_questions if q.difficulty_level >= 4]
                
                selected = []
                
                # 40% легких, 40% средних, 20% сложных
                selected.extend(random.sample(easy, min(len(easy), int(questions_needed * 0.4))))
                selected.extend(random.sample(medium, min(len(medium), int(questions_needed * 0.4))))
                selected.extend(random.sample(hard, min(len(hard), int(questions_needed * 0.2))))
                
                # Добираем до нужного количества если нужно
                remaining = questions_needed - len(selected)
                if remaining > 0:
                    available = [q for q in category_questions if q not in selected]
                    selected.extend(random.sample(available, min(len(available), remaining)))
                
                selected_questions.extend(selected[:questions_needed])
            else:
                selected_questions.extend(category_questions)
    
    # Перемешиваем порядок вопросов
    random.shuffle(selected_questions)
    
    return selected_questions[:50]  # Ограничиваем до 50 вопросов

def calculate_assessment_results(attempt):
    """Расчет результатов оценки"""
    
    answers = attempt.answers.all()
    
    # Общие результаты
    total_questions = len(answers)
    correct_answers = sum(1 for answer in answers if answer.is_correct)
    total_score = (correct_answers / total_questions * 100) if total_questions > 0 else 0
    
    # Результаты по категориям
    category_scores = {}
    category_stats = {}
    
    for answer in answers:
        category_id = answer.question.category_id
        category_name = answer.question.category.name
        
        if category_id not in category_stats:
            category_stats[category_id] = {
                'name': category_name,
                'correct': 0,
                'total': 0
            }
        
        category_stats[category_id]['total'] += 1
        if answer.is_correct:
            category_stats[category_id]['correct'] += 1
    
    # Преобразуем в нужный формат
    for category_id, stats in category_stats.items():
        score = (stats['correct'] / stats['total'] * 100) if stats['total'] > 0 else 0
        category_scores[str(category_id)] = {
            'score': round(score, 1),
            'correct': stats['correct'],
            'total': stats['total']
        }
    
    return {
        'total_correct': correct_answers,
        'total_questions': total_questions,
        'total_score': round(total_score, 1),
        'category_scores': category_scores
    }

def analyze_assessment_results(attempt):
    """Анализ результатов оценки и создание рекомендаций"""
    
    category_scores = attempt.get_category_scores()
    overall_score = attempt.total_score
    
    # Определяем общий уровень
    if overall_score >= 85:
        overall_level = 'advanced'
    elif overall_score >= 70:
        overall_level = 'intermediate'
    else:
        overall_level = 'beginner'
    
    # Анализируем сильные и слабые стороны
    strengths = []
    weaknesses = []
    
    for category_id, scores in category_scores.items():
        category = AssessmentCategory.query.get(int(category_id))
        if not category:
            continue
            
        if scores['score'] >= 80:
            strengths.append(category.name)
        elif scores['score'] < 60:
            weaknesses.append(category.name)
    
    # Создаем рекомендации
    recommendations = []
    if weaknesses:
        recommendations.append({
            'title': 'Сосредоточьтесь на слабых областях',
            'description': f"Рекомендуется углубленное изучение: {', '.join(weaknesses[:3])}",
            'gradient': 'linear-gradient(135deg, #ff6b6b, #ee5a24)',
            'icon': 'exclamation-triangle',
            'duration': '20-30 часов',
            'difficulty': 'Средний'
        })
    
    if overall_score < 70:
        recommendations.append({
            'title': 'Базовый курс',
            'description': 'Рекомендуется пройти базовый курс для укрепления фундамента знаний',
            'gradient': 'linear-gradient(135deg, #4ecdc4, #44a08d)',
            'icon': 'book',
            'duration': '40-60 часов',
            'difficulty': 'Начинающий'
        })
    
    if strengths:
        recommendations.append({
            'title': 'Развитие сильных сторон',
            'description': f"Продолжайте развивать ваши сильные области: {', '.join(strengths[:2])}",
            'gradient': 'linear-gradient(135deg, #a8edea, #fed6e3)',
            'icon': 'star',
            'duration': '15-25 часов',
            'difficulty': 'Продвинутый'
        })
    
    # Добавляем общие рекомендации
    recommendations.append({
        'title': 'Практические занятия',
        'description': 'Регулярно проходите практические тесты для закрепления материала',
        'gradient': 'linear-gradient(135deg, #667eea, #764ba2)',
        'icon': 'clipboard-check',
        'duration': '10-15 часов',
        'difficulty': 'Любой уровень'
    })
    
    recommendations.append({
        'title': 'Повторение материала',
        'description': 'Систематически повторяйте изученный материал для лучшего запоминания',
        'gradient': 'linear-gradient(135deg, #f093fb, #f5576c)',
        'icon': 'arrow-clockwise',
        'duration': '5-10 часов',
        'difficulty': 'Любой уровень'
    })
    
    # Оценка времени обучения
    study_time_estimate = {
        'beginner': 60,  # часов
        'intermediate': 40,
        'advanced': 20
    }
    
    return {
        'overall_level': overall_level,
        'strengths': strengths,
        'weaknesses': weaknesses,
        'recommendations': recommendations,
        'study_time_estimate': study_time_estimate.get(overall_level, 40),
        'learning_plan': {
            'focus_areas': weaknesses[:3],
            'estimated_duration': study_time_estimate.get(overall_level, 40)
        }
    }

def format_time_spent(seconds):
    """Форматирование времени"""
    if not seconds:
        return "0 мин"
    
    minutes = int(seconds // 60)
    hours = minutes // 60
    minutes = minutes % 60
    
    if hours > 0:
        return f"{hours}ч {minutes}мин"
    else:
        return f"{minutes}мин"

def format_category_results(category_scores):
    """Форматирование результатов по категориям"""
    
    formatted_results = []
    
    for category_id, scores in category_scores.items():
        category = AssessmentCategory.query.get(int(category_id))
        if not category:
            continue
            
        score = scores['score']
        
        # Определяем уровень
        if score >= 85:
            level = 'excellent'
            level_text = 'Отличный'
            level_class = 'success'
        elif score >= 70:
            level = 'good'
            level_text = 'Хороший'
            level_class = 'info'
        elif score >= 50:
            level = 'satisfactory'
            level_text = 'Удовлетворительный'
            level_class = 'warning'
        else:
            level = 'needs_improvement'
            level_text = 'Требует улучшения'
            level_class = 'danger'
        
        formatted_results.append({
            'category_name': category.name,
            'score': score,
            'correct': scores['correct'],
            'total': scores['total'],
            'level': level,
            'level_text': level_text,
            'level_class': level_class,
            'color': category.color,
            'icon': category.icon
        })
    
    return sorted(formatted_results, key=lambda x: x['score'], reverse=True)

def calculate_plan_progress(plan):
    """Расчет прогресса выполнения плана"""
    
    # Заглушка - в реальности здесь будет анализ прогресса по модулям
    return {
        'overall_progress': plan.calculate_progress(),
        'completed_modules': plan.completed_modules,
        'total_modules': plan.total_modules,
        'days_active': 0,  # Количество дней с активностью
        'current_phase': 1,  # Текущая фаза обучения
        'next_milestone': 'Завершение базовых модулей'  # Ближайшая цель
    }

# ===== DUTCH ASSESSMENT ROUTES =====

@assessment_bp.route('/dutch-intro')
@login_required 
def dutch_intro(lang):
    """Введение в оценку для работы в Нидерландах"""
    g.lang = lang
    
    # Получаем нидерландские категории
    dutch_categories = AssessmentCategory.query.filter_by(is_dutch_specific=True).all()
    
    # Предыдущие попытки пользователя
    previous_attempts = PreAssessmentAttempt.query.filter_by(
        user_id=current_user.id,
        is_completed=True
    ).order_by(PreAssessmentAttempt.completed_at.desc()).limit(3).all()
    
    return render_template('assessment/dutch_intro.html',
                         dutch_categories=dutch_categories,
                         previous_attempts=previous_attempts,
                         title=t('dutch_assessment_title', lang=g.lang))

@assessment_bp.route('/dutch-start', methods=['POST'])
@login_required
def start_dutch_assessment(lang):
    """Начало нидерландской оценки"""
    g.lang = lang
    
    try:
        # Получаем данные из JSON или form
        if request.is_json:
            data = request.get_json()
            regional_focus = data.get('regional_focus', 'general')
            include_big_exam = data.get('include_big_exam', False)
        else:
            regional_focus = request.form.get('regional_focus', 'general')
            include_big_exam = request.form.get('include_big_exam', False)
        
        # Проверяем, нет ли незавершенной попытки
        existing_attempt = PreAssessmentAttempt.query.filter_by(
            user_id=current_user.id,
            is_completed=False
        ).first()
        
        if existing_attempt:
            # Удаляем незавершенную попытку
            PreAssessmentAnswer.query.filter_by(attempt_id=existing_attempt.id).delete()
            db.session.delete(existing_attempt)
        
        # Создаем попытку с нидерландскими вопросами
        attempt = PreAssessmentAttempt(
            user_id=current_user.id,
            started_at=datetime.utcnow(),
            is_completed=False
        )
        
        # Выбираем вопросы из нидерландских категорий
        questions = _select_dutch_questions(include_big_exam, regional_focus)
        attempt.total_questions = len(questions)
        
        db.session.add(attempt)
        db.session.flush()
        
        # Сохраняем в сессии информацию о нидерландской оценке
        session['dutch_assessment'] = {
            'attempt_id': attempt.id,
            'questions': [q.id for q in questions],
            'regional_focus': regional_focus,
            'include_big_exam': include_big_exam,
            'current_question': 0
        }
        
        # Также сохраняем для совместимости с существующими маршрутами
        session['assessment_attempt_id'] = attempt.id
        session['assessment_questions'] = [q.id for q in questions]
        session['current_question_index'] = 0
        session['assessment_start_time'] = datetime.utcnow().isoformat()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'attempt_id': attempt.id,
            'redirect_url': url_for('assessment_bp.question', lang=g.lang, question_num=1)
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error starting Dutch assessment: {e}")
        return jsonify({
            'success': False,
            'error': t('error_starting_assessment', lang=g.lang)
        }), 500

@assessment_bp.route('/dutch-results/<int:attempt_id>')
@login_required
def dutch_results(lang, attempt_id):
    """Результаты нидерландской оценки с специализированным анализом"""
    g.lang = lang
    
    attempt = PreAssessmentAttempt.query.get_or_404(attempt_id)
    
    if attempt.user_id != current_user.id:
        abort(403)
    
    # Используем нидерландский анализатор
    from services.dutch_assessment_analyzer import DutchAssessmentAnalyzer
    
    analyzer = DutchAssessmentAnalyzer()
    regional_focus = session.get('dutch_assessment', {}).get('regional_focus')
    analysis = analyzer.analyze_dutch_competency(attempt, regional_focus)
    
    # Сохраняем результат
    from models import DutchAssessmentResult
    dutch_result = DutchAssessmentResult(
        user_id=current_user.id,
        attempt_id=attempt_id,
        competency_level=analysis['competency_level']['level'],
        overall_score=analysis['overall_score'],
        critical_areas_score=analysis['competency_level']['critical_areas_score'],
        can_work_supervised=analysis['practice_readiness']['supervised_practice']['ready'],
        can_work_independently=analysis['practice_readiness']['independent_general']['ready'],
        regional_focus=regional_focus,
        certification_pathway=json.dumps(analysis['certification_pathway']),
        next_steps=json.dumps(analysis['next_steps']),
        category_scores=json.dumps(analysis.get('category_analyses', []))
    )
    
    db.session.add(dutch_result)
    db.session.commit()
    
    return render_template('assessment/dutch_results.html',
                         attempt=attempt,
                         analysis=analysis,
                         dutch_result=dutch_result,
                         title=t('dutch_assessment_results_title', lang=g.lang))

def _select_dutch_questions(include_big_exam=False, regional_focus='general'):
    """Выбор вопросов для нидерландской оценки"""
    
    # Получаем нидерландские категории
    dutch_categories = AssessmentCategory.query.filter_by(is_dutch_specific=True).all()
    
    if include_big_exam:
        # Добавляем BIG экзаменационные категории
        big_categories = AssessmentCategory.query.filter(
            AssessmentCategory.slug.like('big_%')
        ).all()
        dutch_categories.extend(big_categories)
    
    selected_questions = []
    
    for category in dutch_categories:
        # Применяем региональные веса
        question_count = category.min_questions
        if regional_focus in REGIONAL_FOCUS:
            weight = REGIONAL_FOCUS[regional_focus].get('additional_weight', {}).get(category.slug, 1.0)
            if weight > 1.0:
                question_count = min(category.max_questions, int(question_count * weight))
        
        # Выбираем вопросы категории
        questions = AssessmentQuestion.query.filter_by(
            category_id=category.id,
            is_active=True
        ).order_by(db.func.random()).limit(question_count).all()
        
        selected_questions.extend(questions)
    
    # Перемешиваем порядок вопросов
    random.shuffle(selected_questions)
    
    return selected_questions[:60]  # Ограничиваем до 60 вопросов для Dutch assessment 

@assessment_bp.route('/big-exam-prep')
@login_required
def big_exam_prep(lang):
    """Страница подготовки к BIG экзамену"""
    g.lang = lang
    
    # Получаем BIG экзаменационные категории
    big_categories = AssessmentCategory.query.filter(
        AssessmentCategory.slug.like('big_%')
    ).all()
    
    # Получаем статистику по BIG экзамену
    previous_attempts = PreAssessmentAttempt.query.filter(
        PreAssessmentAttempt.user_id == current_user.id,
        PreAssessmentAttempt.is_completed == True
    ).order_by(PreAssessmentAttempt.completed_at.desc()).limit(5).all()
    
    return render_template('assessment/big_exam_prep.html',
                         big_categories=big_categories,
                         previous_attempts=previous_attempts,
                         format_time_spent=format_time_spent,
                         title=t('big_exam_prep', lang=g.lang))

@assessment_bp.route('/test-options')
def test_options(lang):
    """Тестовый маршрут для проверки опций"""
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Тест опций</title>
        <style>
            .option {
                display: grid;
                grid-template-columns: auto 1fr;
                gap: 12px;
                padding: 16px;
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                cursor: pointer;
                transition: all 0.15s ease;
                background: white;
                margin-bottom: 8px;
            }
            .option:hover {
                border-color: #93c5fd;
                background: #eff6ff;
                transform: translateY(-1px);
                box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            }
            .option.selected {
                border-color: #3b82f6;
                background: #eff6ff;
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            }
            .option-letter {
                width: 32px;
                height: 32px;
                background: #f3f4f6;
                color: #374151;
                border-radius: 6px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: 600;
                font-size: 14px;
                transition: all 0.15s ease;
            }
            .option.selected .option-letter {
                background: #3b82f6;
                color: white;
            }
            .option-text {
                font-size: 16px;
                color: #111827;
                line-height: 1.5;
                align-self: center;
            }
        </style>
    </head>
    <body>
        <h1>Тест опций</h1>
        <div class="options-grid">
            <div class="option" onclick="selectOption(this, 0)">
                <div class="option-letter">A</div>
                <div class="option-text">Первый вариант ответа</div>
            </div>
            <div class="option" onclick="selectOption(this, 1)">
                <div class="option-letter">B</div>
                <div class="option-text">Второй вариант ответа</div>
            </div>
            <div class="option" onclick="selectOption(this, 2)">
                <div class="option-letter">C</div>
                <div class="option-text">Третий вариант ответа</div>
            </div>
            <div class="option" onclick="selectOption(this, 3)">
                <div class="option-letter">D</div>
                <div class="option-text">Четвертый вариант ответа</div>
            </div>
        </div>
        <button id="next-btn" disabled onclick="alert('Кнопка работает!')">Далее</button>
        <div id="debug">Ожидание клика...</div>
        
        <script>
            let selectedOption = null;
            
            function selectOption(element, optionIndex) {
                console.log('selectOption called with:', element, optionIndex);
                
                document.querySelectorAll('.option').forEach(opt => {
                    opt.classList.remove('selected');
                });
                
                element.classList.add('selected');
                selectedOption = optionIndex;
                
                document.getElementById('next-btn').disabled = false;
                document.getElementById('debug').textContent = 'Выбран вариант ' + optionIndex;
            }
        </script>
    </body>
    </html>
    ''' 