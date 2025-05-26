# routes/tests_routes.py 
from flask import (
    Blueprint, render_template, request, session, redirect, url_for, g, flash, current_app
)
from flask_login import login_required, current_user
from models import db, Question, UserProgress, ContentCategory

# Имя блюпринта изменено на "tests" (без "_bp")
tests_bp = Blueprint("tests_bp", __name__, url_prefix="/<string:lang>/tests")

# --- Языковые и защитные обработчики ---
SUPPORTED_LANGUAGES = ['en', 'ru', 'nl', 'uk', 'es', 'pt', 'tr', 'fa']
DEFAULT_LANGUAGE = 'en'

@tests_bp.before_request
def before_request_tests():
    """Извлекает и валидирует язык из URL."""
    # Получаем lang из аргументов URL
    lang_from_url = request.view_args.get('lang') if request.view_args else None

    # Валидация и установка языка в g
    if lang_from_url and lang_from_url in SUPPORTED_LANGUAGES:
        g.lang = lang_from_url
    else:
        # Если в URL нет валидного языка, берем из сессии или accept_languages
        g.lang = session.get('lang') \
                 or request.accept_languages.best_match(SUPPORTED_LANGUAGES) \
                 or DEFAULT_LANGUAGE

    # Обновляем сессию, если язык отличается
    if session.get('lang') != g.lang:
        session['lang'] = g.lang

@tests_bp.context_processor
def inject_lang_tests():
    """Добавляет lang в контекст шаблонов этого блюпринта."""
    lang = getattr(g, 'lang', session.get('lang', DEFAULT_LANGUAGE))
    return dict(lang=lang)

# --- Страница НАСТРОЙКИ теста ---
@tests_bp.route("/", methods=['GET'])
@login_required
def setup_test(lang):
    current_lang = g.lang
    try:
        # Получаем категории динамически из БД
        distinct_categories = db.session.query(Question.category).distinct().all()
        categories = sorted([cat[0] for cat in distinct_categories if cat[0]])
        if not categories:  # Если категории в БД не найдены, используем заглушку
            categories = ["Anatomy", "Ethics", "Physiology", "Pathology"]  # Пример
            flash("Warning: No categories found in the database. Using default list.", "warning")
    except Exception as e:
        current_app.logger.error(f"Error fetching categories: {e}", exc_info=True)
        flash("Could not load test categories.", "danger")
        categories = []

    test_lengths = [5, 10, 15, 20, 25]  # Пример
    # Обновлен путь к шаблону
    return render_template("tests/setup.html", categories=categories, test_lengths=test_lengths)

# --- Маршрут для ЗАПУСКА теста ---
@tests_bp.route("/start", methods=['POST'])
@login_required
def start_custom_test(lang):
    current_lang = g.lang
    selected_category = request.form.get('category')
    try:
        selected_length = int(request.form.get('length', 10))
    except ValueError:
        flash("Invalid test length selected.", "warning")
        return redirect(url_for('.setup_test', lang=current_lang))

    try:
        query = Question.query
        if selected_category and selected_category != 'all':
            query = query.filter(Question.category == selected_category)
        all_matching_ids = [q.id for q in query.with_entities(Question.id).all()]

        if not all_matching_ids:
            flash(f"No questions found for category '{selected_category}'.", "warning")
            return redirect(url_for('.setup_test', lang=current_lang))

        actual_length = min(selected_length, len(all_matching_ids))
        if actual_length == 0:  # Доп. проверка, если вдруг all_matching_ids пуст после фильтрации
             flash(f"No questions available for the selected criteria.", "warning")
             return redirect(url_for('.setup_test', lang=current_lang))
        if actual_length < selected_length:
             flash(f"Warning: Only {actual_length} questions available for this category. Test adjusted.", "info")

        selected_question_ids = random.sample(all_matching_ids, actual_length)
    except Exception as e:
        current_app.logger.error(f"Error querying questions: {e}", exc_info=True)
        flash("An error occurred while preparing the test.", "danger")
        return redirect(url_for('.setup_test', lang=current_lang))

    session['test_question_ids'] = selected_question_ids
    session['test_step'] = 0
    session['test_score'] = 0
    session['test_total'] = actual_length
    session.pop('last_answered_step', None)
    session.pop('last_step_result', None)

    current_app.logger.info(f"Starting test: Category='{selected_category}', Length={actual_length}, Q_IDs={selected_question_ids}")
    return redirect(url_for('.take_test', lang=current_lang))

# --- Маршрут ПРОХОЖДЕНИЯ теста ---
@tests_bp.route("/take", methods=['GET', 'POST'])
@login_required
def take_test(lang):
    current_lang = g.lang

    if 'test_question_ids' not in session or 'test_step' not in session:
        flash("No active test found. Please start a new test.", "info")
        return redirect(url_for('.setup_test', lang=current_lang))

    question_ids = session['test_question_ids']
    step = session['test_step']
    total = session.get('test_total', len(question_ids))  # Используем test_total из сессии

    if step >= total:
        final_score = session.get("test_score", 0)
        session.pop("test_question_ids", None)
        session.pop("test_step", None)
        session.pop("test_score", None)
        session.pop("test_total", None)
        session.pop("last_answered_step", None)
        session.pop("last_step_result", None)
        current_app.logger.info(f"Test finished. Score: {final_score}/{total}")
        # Обновлен путь к шаблону
        return render_template("tests/result.html", score=final_score, total=total)

    current_question_id = question_ids[step]
    try:
        question = Question.query.get(current_question_id)
        if not question:
            raise ValueError(f"Question ID {current_question_id} not found")
    except Exception as e:
         current_app.logger.error(f"Error fetching question ID {current_question_id}: {e}", exc_info=True)
         flash("An error occurred loading question. Skipping.", "danger")
         session['test_step'] += 1
         return redirect(url_for('.take_test', lang=current_lang))

    current_app.logger.debug(f"Displaying question {step + 1}/{total} (ID: {current_question_id}): {question.text[:30]}...")
    result = None
    correct_answer_text = question.correct_answer
    explanation = question.explanation
    options = question.get_options_list()
    submitted_answer = None

    if request.method == "POST":
        submitted_answer = request.form.get("selected_option")
        current_app.logger.debug(f"Received answer: {submitted_answer}")
        is_correct = question.check_answer(submitted_answer)
        result = "correct" if is_correct else "incorrect"
        if session.get("last_answered_step") != step:
            if is_correct:
                session["test_score"] = session.get("test_score", 0) + 1
        else:
            result = "already_answered_" + result
        session["last_answered_step"] = step
        session["last_step_result"] = result
        current_app.logger.debug(f"Result: {result}. Score: {session.get('test_score', 0)}")
    elif session.get("last_answered_step") == step:
        result = session.get("last_step_result")
        # Восстанавливаем информацию о предыдущем ответе, если пользователь перезагрузил страницу
        if "already_answered_" in str(result):
            result = result.replace("already_answered_", "")

    # Обновлен путь к шаблону и передаются дополнительные параметры
    return render_template("tests/question.html", 
                           question=question, 
                           step=step, 
                           total=total, 
                           result=result, 
                           correct_answer=correct_answer_text,
                           explanation=explanation,
                           options=options,
                           submitted_answer=submitted_answer)

# --- Маршрут для перехода к СЛЕДУЮЩЕМУ вопросу ---
@tests_bp.route("/next", methods=["POST"])
@login_required
def next_question(lang):
    current_lang = g.lang
    if "test_step" in session:
        session["test_step"] += 1
        session.pop("last_answered_step", None)
        session.pop("last_step_result", None)
        current_app.logger.debug(f"Advancing to step {session['test_step']}")
        return redirect(url_for(".take_test", lang=current_lang))
    else:
        flash("No active test session found.", "warning")
        return redirect(url_for(".setup_test", lang=current_lang))

# --- Маршрут для теста по конкретному модулю ---
@tests_bp.route("/module/<int:module_id>", methods=['GET'])
@login_required
def start_module_test(lang, module_id):
    """Запускает тест для конкретного модуля."""
    current_lang = g.lang
    # Здесь должна быть логика выбора вопросов из конкретного модуля
    try:
        # Получаем вопросы, связанные с данным модулем
        questions = Question.query.filter_by(module_id=module_id).all()
        if not questions:
            flash(f"No questions found for this module.", "warning")
            return redirect(url_for('modules_bp.module_view', lang=lang, module_id=module_id))
            
        # Выбираем до 10 случайных вопросов (или меньше, если вопросов меньше 10)
        question_ids = [q.id for q in questions]
        actual_length = min(10, len(question_ids))
        selected_question_ids = random.sample(question_ids, actual_length)
        
        # Сохраняем выбранные вопросы в сессии
        session['test_question_ids'] = selected_question_ids
        session['test_step'] = 0
        session['test_score'] = 0
        session['test_total'] = actual_length
        session.pop('last_answered_step', None)
        session.pop('last_step_result', None)
        
        current_app.logger.info(f"Starting module test for module {module_id}, with {actual_length} questions")
        return redirect(url_for('.take_test', lang=current_lang))
    except Exception as e:
        current_app.logger.error(f"Error starting module test: {e}", exc_info=True)
        flash(f"Error starting module test: {e}", "danger")
        return redirect(url_for('modules_bp.module_view', lang=lang, module_id=module_id))

# --- Маршрут для итогового теста ---
@tests_bp.route("/final/<int:subject_id>", methods=['GET'])
@login_required
def start_final_test(lang, subject_id):
    """Запускает итоговый тест по предмету."""
    current_lang = g.lang
    try:
        # Получаем вопросы, связанные с данным предметом
        questions = Question.query.filter_by(subject_id=subject_id).all()
        if not questions:
            flash(f"No questions found for this subject's final test.", "warning")
            return redirect(url_for('learning_map_bp.learning_map', lang=lang))
            
        # Выбираем до 20 случайных вопросов (или меньше, если вопросов меньше 20)
        question_ids = [q.id for q in questions]
        actual_length = min(20, len(question_ids))
        selected_question_ids = random.sample(question_ids, actual_length)
        
        # Сохраняем выбранные вопросы в сессии
        session['test_question_ids'] = selected_question_ids
        session['test_step'] = 0
        session['test_score'] = 0
        session['test_total'] = actual_length
        session['is_final_test'] = True  # Отмечаем, что это финальный тест
        session.pop('last_answered_step', None)
        session.pop('last_step_result', None)
        
        current_app.logger.info(f"Starting final test for subject {subject_id}, with {actual_length} questions")
        return redirect(url_for('.take_test', lang=current_lang))
    except Exception as e:
        current_app.logger.error(f"Error starting final test: {e}", exc_info=True)
        flash(f"Error starting final test: {e}", "danger")
        return