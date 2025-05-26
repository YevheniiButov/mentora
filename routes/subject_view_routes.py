# routes/subject_view_routes.py
import json
import random
import os # Добавлен импорт os
from flask import Blueprint, render_template, request, session, redirect, url_for, g, flash, current_app
from flask_login import login_required, current_user
from models import (
    db, Subject, Module, UserProgress, Lesson, ContentCategory,
    ContentSubcategory, ContentTopic, LearningPath,
    VirtualPatientScenario, VirtualPatientAttempt # Убедитесь, что эти модели существуют
)
# Предполагается, что эти функции существуют в указанном файле или вы предоставите их реализацию
from routes.learning_map_routes import get_module_stats, get_user_stats, calculate_subject_progress
from translations import get_translation as t

subject_view_bp = Blueprint(
    "subject_view_bp",
    __name__,
    url_prefix='/<string:lang>/learning-map/subject', # Префикс из Фрагмента 2
    template_folder='../templates'
)

# Языковые настройки из Фрагмента 2
SUPPORTED_LANGUAGES = ['en', 'ru', 'nl', 'uk', 'es', 'pt', 'tr', 'fa']
DEFAULT_LANGUAGE = 'en'

@subject_view_bp.before_request
def before_request_subject_view():
    """Извлекает и валидирует язык из URL."""
    lang_from_url = request.view_args.get('lang') if request.view_args else None
    if lang_from_url and lang_from_url in SUPPORTED_LANGUAGES:
        g.lang = lang_from_url
    else:
        g.lang = session.get('lang') \
                 or request.accept_languages.best_match(SUPPORTED_LANGUAGES) \
                 or DEFAULT_LANGUAGE
    if session.get('lang') != g.lang:
        session['lang'] = g.lang

@subject_view_bp.context_processor
def inject_lang_subject_view():
    """Добавляет lang в контекст шаблонов этого блюпринта."""
    lang = getattr(g, 'lang', session.get('lang', DEFAULT_LANGUAGE))
    return dict(lang=lang)

# ФУНКЦИЯ ИЗ ФРАГМЕНТА 1 (с небольшими доработками из предыдущего ответа)
def get_virtual_patients_for_subject(subject_object, user_id):
    """
    Получает виртуальных пациентов для конкретного предмета.
    Args:
        subject_object: Объект Subject
        user_id: ID пользователя
    Returns:
        List: Список виртуальных пациентов с прогрессом
    """
    if not subject_object:
        current_app.logger.info("Предмет не предоставлен для get_virtual_patients_for_subject, возврат пустого списка.")
        return []

    try:
        all_published_scenarios = VirtualPatientScenario.query.filter_by(is_published=True).all()
        relevant_scenarios = []
        processed_scenario_ids = set()

        subject_name_lower = subject_object.name.lower()
        category_mapping = {
            'diagnosis': ['диагностика', 'диагноз', 'diagnostic'],
            'treatment': ['лечение', 'терапия', 'treatment', 'behandeling'],
            'emergency': ['неотложная', 'экстренная', 'spoed', 'emergency'],
            'communication': ['коммуникация', 'общение', 'communicatie'],
            'dental_anatomy': ['анатомия', 'anatomy'],
            'periodontology': ['пародонтология', 'periodontology', 'пародонтологія'],
            'endodontics': ['эндодонтия', 'endodontics', 'ендодонтія'],
        }

        for scenario in all_published_scenarios:
            if scenario.id in processed_scenario_ids:
                continue

            # Прямая связь через атрибут subject_id (если бы он был в модели VirtualPatientScenario)
            # if hasattr(scenario, 'subject_id') and scenario.subject_id == subject_object.id:
            #     relevant_scenarios.append(scenario)
            #     processed_scenario_ids.add(scenario.id)
            #     continue
            
            scenario_category_lower = scenario.category.lower().strip() if scenario.category else ''

            if scenario_category_lower and scenario_category_lower in subject_name_lower:
                relevant_scenarios.append(scenario)
                processed_scenario_ids.add(scenario.id)
                continue

            if scenario_category_lower in category_mapping:
                keywords_for_category = category_mapping[scenario_category_lower]
                if any(keyword.lower() in subject_name_lower for keyword in keywords_for_category):
                    relevant_scenarios.append(scenario)
                    processed_scenario_ids.add(scenario.id)
        
        if not relevant_scenarios:
            current_app.logger.info(f"Специфичные VP для предмета '{subject_object.name}' не найдены. Попытка загрузить общие/последние.")
            # Пример: взять несколько последних сценариев, если нет специфичных
            fallback_scenarios = VirtualPatientScenario.query.filter_by(is_published=True).order_by(VirtualPatientScenario.created_at.desc()).limit(3).all()
            for fs in fallback_scenarios:
                 if fs.id not in processed_scenario_ids: # Чтобы не дублировать, если вдруг они уже были добавлены другой логикой
                    relevant_scenarios.append(fs)
                    processed_scenario_ids.add(fs.id)


        for scenario_instance in relevant_scenarios:
            best_attempt = VirtualPatientAttempt.query.filter_by(
                user_id=user_id,
                scenario_id=scenario_instance.id,
                completed=True
            ).order_by(VirtualPatientAttempt.score.desc()).first()
            
            attempts_count = VirtualPatientAttempt.query.filter_by(
                user_id=user_id, 
                scenario_id=scenario_instance.id
            ).count()

            percentage = 0
            best_attempt_id_for_results = None # Для ссылки на результаты
            if best_attempt:
                best_attempt_id_for_results = best_attempt.id
                if scenario_instance.max_score and scenario_instance.max_score > 0:
                    percentage = round((best_attempt.score / scenario_instance.max_score) * 100)
            
            scenario_instance.user_progress = {
                'completed': bool(best_attempt),
                'score': best_attempt.score if best_attempt else 0,
                'max_score': scenario_instance.max_score,
                'percentage': percentage,
                'completion_date': best_attempt.completed_at if best_attempt else None,
                'attempts_count': attempts_count,
                'best_attempt_id': best_attempt_id_for_results # Добавляем ID лучшей попытки
            }
        
        return relevant_scenarios
        
    except Exception as e:
        current_app.logger.error(f"Ошибка в get_virtual_patients_for_subject для предмета ID {subject_object.id if subject_object else 'N/A'}: {e}", exc_info=True)
        return []

# МАРШРУТ view_subject ИЗ ФРАГМЕНТА 2, ОБНОВЛЕННЫЙ ЛОГИКОЙ ИЗ ФРАГМЕНТА 1
@subject_view_bp.route("/<int:subject_id>")
@login_required
def view_subject(lang, subject_id): # subject_id=None убрано, т.к. он обязателен для этого маршрута
    """Отображает страницу просмотра предмета с его модулями и виртуальными пациентами."""
    current_lang = g.lang
    
    try:
        learning_paths = LearningPath.query.order_by(LearningPath.order).all()
        content_categories = ContentCategory.query.order_by(ContentCategory.order).all()
        
        selected_subject = Subject.query.get_or_404(subject_id)
        subject_modules = Module.query.filter_by(subject_id=subject_id).order_by(Module.order).all()
        
        for module in subject_modules:
            module_stats = get_module_stats(module.id, current_user.id)
            module.progress = module_stats.get("progress", 0)
            module.completed_lessons = module_stats.get("completed_lessons", 0)
            module.total_lessons = module_stats.get("total_lessons", 0)
        
        # ИНТЕГРАЦИЯ: Загружаем виртуальных пациентов
        virtual_patients = get_virtual_patients_for_subject(selected_subject, current_user.id)
        
        stats = get_user_stats(current_user.id)
        recommendations = get_user_recommendations(current_user.id) # Используем реализацию ниже
        random_fact = get_random_fact(g.lang) # Используем реализацию ниже
        
        return render_template(
            "learning/subject_view.html",
            title=selected_subject.name, # selected_subject точно будет из-за get_or_404
            learning_paths=learning_paths,
            content_categories=content_categories,
            selected_subject=selected_subject,
            subject_modules=subject_modules,
            virtual_patients=virtual_patients,  # Передаем виртуальных пациентов
            subjects=Subject.query.all(),
            user=current_user,
            has_subscription=current_user.has_subscription,
            stats=stats,
            recommendations=recommendations,
            random_fact=random_fact
        )
    except Exception as e:
        current_app.logger.error(f"Ошибка в view_subject (ID: {subject_id}): {e}", exc_info=True)
        flash(t("error_occurred_loading_data") + ": " + str(e), "danger")
        return redirect(url_for('main_bp.index', lang=current_lang)) # Измените на подходящий fallback маршрут

# НОВЫЙ РОУТ ИЗ ФРАГМЕНТА 1
@subject_view_bp.route("/virtual-patients") # Будет доступен по /<lang>/learning-map/subject/virtual-patients
@login_required
def all_virtual_patients(lang):
    """Отображает все доступные виртуальные пациенты, сгруппированные по категориям."""
    try:
        all_published_scenarios = VirtualPatientScenario.query.filter_by(is_published=True).order_by(
            VirtualPatientScenario.category, VirtualPatientScenario.title
        ).all()
        
        categorized_scenarios = {}
        
        for scenario in all_published_scenarios:
            category_name = scenario.category or t("general_category", lang=g.lang)
            if category_name not in categorized_scenarios:
                categorized_scenarios[category_name] = []
            
            best_attempt = VirtualPatientAttempt.query.filter_by(
                user_id=current_user.id,
                scenario_id=scenario.id,
                completed=True
            ).order_by(VirtualPatientAttempt.score.desc()).first()
            
            attempts_count = VirtualPatientAttempt.query.filter_by(
                user_id=current_user.id, 
                scenario_id=scenario.id
            ).count()

            percentage = 0
            best_attempt_id_for_results = None
            if best_attempt:
                best_attempt_id_for_results = best_attempt.id
                if scenario.max_score and scenario.max_score > 0:
                    percentage = round((best_attempt.score / scenario.max_score) * 100)

            scenario.user_progress = {
                'completed': bool(best_attempt),
                'score': best_attempt.score if best_attempt else 0,
                'max_score': scenario.max_score,
                'percentage': percentage,
                'completion_date': best_attempt.completed_at if best_attempt else None,
                'attempts_count': attempts_count,
                'best_attempt_id': best_attempt_id_for_results
            }
            
            categorized_scenarios[category_name].append(scenario)
        
        stats = get_user_stats(current_user.id)
        recommendations = get_user_recommendations(current_user.id)
        
        return render_template(
            "learning/virtual_patients_overview.html", # Убедитесь, что шаблон существует
            categorized_scenarios=categorized_scenarios,
            stats=stats,
            recommendations=recommendations,
            user=current_user,
            has_subscription=current_user.has_subscription,
            title=t("all_virtual_patients_title", lang=g.lang)
        )
    except Exception as e:
        current_app.logger.error(f"Ошибка при загрузке обзора виртуальных пациентов: {e}", exc_info=True)
        flash(t("error_loading_virtual_patients"), "danger")
        # Измените 'learning_map_bp.learning_map' на существующий маршрут, если он другой
        return redirect(url_for('learning_map_bp.learning_map', lang=lang))


# ФУНКЦИИ ИЗ ФРАГМЕНТА 2 (get_user_recommendations, learning_hierarchy_view, view_hierarchy, manage_test_data, view_category, get_random_fact)
# Оставляем их здесь, так как они были частью "старой" (более полной) версии файла.

def get_user_recommendations(user_id, limit=3):
    """Возвращает рекомендуемые модули для пользователя."""
    try:
        in_progress_lesson_ids_query = db.session.query(UserProgress.lesson_id).filter(
            UserProgress.user_id == user_id,
            UserProgress.completed == False
        )
        in_progress_lesson_ids = [item[0] for item in in_progress_lesson_ids_query.all()]
        
        in_progress_modules_formatted = []
        processed_module_ids = set()

        if in_progress_lesson_ids:
            in_progress_modules_data = db.session.query(
                Module, Subject.name.label('subject_name')
            ).join(
                Lesson, Lesson.module_id == Module.id
            ).join(
                Subject, Subject.id == Module.subject_id
            ).filter(
                Lesson.id.in_(in_progress_lesson_ids)
            ).distinct(Module.id).limit(limit).all()
            
            for mod, subj_name in in_progress_modules_data:
                in_progress_modules_formatted.append({
                    'module_id': mod.id,
                    'title': mod.title, 
                    'icon': getattr(mod, 'icon', 'journal-text'),
                    'subject_name': subj_name
                })
                processed_module_ids.add(mod.id)

        recommendations = list(in_progress_modules_formatted)
        
        if len(recommendations) < limit:
            remaining_limit = limit - len(recommendations)
            
            completed_lesson_ids = [row[0] for row in db.session.query(UserProgress.lesson_id).filter(
                UserProgress.user_id == user_id,
                UserProgress.completed == True
            ).all()]

            # Модули, где все уроки завершены
            # Это упрощенная логика; для точного определения завершенности модуля может потребоваться более сложный запрос
            if completed_lesson_ids:
                fully_completed_modules_q = db.session.query(Module.id)\
                    .join(Lesson, Module.id == Lesson.module_id)\
                    .filter(Lesson.id.in_(completed_lesson_ids))\
                    .group_by(Module.id)\
                    .having(db.func.count(Lesson.id) == db.session.query(db.func.count(Lesson.id)).filter(Lesson.module_id == Module.id).scalar_subquery()) # Проверяем, что все уроки модуля завершены
                
                fully_completed_module_ids = [row[0] for row in fully_completed_modules_q.all()]
                processed_module_ids.update(fully_completed_module_ids)

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
        facts_file_path = os.path.join(current_app.root_path, 'data', 'dental_facts.json')
        with open(facts_file_path, 'r', encoding='utf-8') as file:
            all_facts_data = json.load(file)
        
        facts_list = all_facts_data.get('facts', []) 
        if not facts_list:
            raise ValueError("Список 'facts' пуст или отсутствует в dental_facts.json")

        random_fact_translations = random.choice(facts_list)
        return random_fact_translations.get(lang, random_fact_translations.get('en', {"title": "Fact", "fact": "Fact not available."}))

    except FileNotFoundError:
        current_app.logger.error(f"Файл dental_facts.json не найден по пути: {facts_file_path}")
    except json.JSONDecodeError as e:
        current_app.logger.error(f"Ошибка декодирования JSON из dental_facts.json: {str(e)}")
    except Exception as e:
        current_app.logger.error(f"Неожиданная ошибка в get_random_fact: {str(e)}", exc_info=True)
    
    default_facts = {
        'en': {'title': 'Did you know?', 'fact': 'Tooth enamel is the hardest substance in the human body!'},
        'ru': {'title': 'Знаете ли вы?', 'fact': 'Зубная эмаль - самая твёрдая ткань человеческого организма!'},
        'nl': {'title': 'Wist u dat?', 'fact': 'Tandglazuur is de hardste substantie in het menselijk lichaam!'}
    }
    return default_facts.get(lang, default_facts['en'])

@subject_view_bp.route("/hierarchy")
@login_required
def learning_hierarchy_view(lang):
    try:
        categories = ContentCategory.query.order_by(ContentCategory.name).all()
        # Для отладки:
        # current_app.logger.info(f"Найдено категорий для иерархии: {len(categories)}")
        # for cat in categories:
        #     current_app.logger.info(f"Категория: {cat.name}, подкатегорий: {cat.subcategories.count()}")

        return render_template(
            "learning/subject_view.html", # Этот шаблон должен уметь отображать иерархию категорий
            title=t("learning_hierarchy_page_title", lang=g.lang),
            # Передаем категории под другим именем, чтобы основной шаблон знал, что отображать
            content_categories_for_hierarchy=categories, 
            selected_subject=None, 
            stats=get_user_stats(current_user.id),
            recommendations=get_user_recommendations(current_user.id),
            random_fact=get_random_fact(g.lang),
            user=current_user,
            has_subscription=current_user.has_subscription,
            page_description=t("learning_hierarchy_page_description", lang=g.lang)
        )
    except Exception as e:
        current_app.logger.error(f"Ошибка в learning_hierarchy_view: {str(e)}", exc_info=True)
        flash(t("error_loading_data_try_again"), "danger")
        return redirect(url_for("learning_map_bp.learning_map", lang=lang)) # Убедитесь, что маршрут 'learning_map_bp.learning_map' существует

# Функция view_hierarchy из вашего "старого" кода кажется дублирующей learning_hierarchy_view
# Если она нужна отдельно, можно оставить, но логика очень похожа.
# def view_hierarchy(lang): ...

@subject_view_bp.route("/manage-test-data")
@login_required
def manage_test_data(lang):
    action = request.args.get('action', '')
    if action == 'create':
        try:
            category = ContentCategory.query.filter_by(slug="test-category").first()
            if not category:
                category = ContentCategory(name="Тестовая категория", slug="test-category", icon="book", order=100)
                db.session.add(category)
                db.session.flush()

            subcategory = ContentSubcategory.query.filter_by(slug="test-subcategory").first()
            if not subcategory:
                subcategory = ContentSubcategory(name="Тестовая подкатегория", slug="test-subcategory", category_id=category.id, icon="bookmark", order=1)
                db.session.add(subcategory)
                db.session.flush()
            
            topic = ContentTopic.query.filter_by(slug="test-topic").first()
            if not topic:
                topic = ContentTopic(name="Тестовая тема", slug="test-topic", subcategory_id=subcategory.id, description="Описание тестовой темы", order=1)
                db.session.add(topic)
            
            db.session.commit()
            flash("Тестовые данные иерархии созданы.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка при создании тестовых данных: {str(e)}", "danger")
            current_app.logger.error(f"Ошибка manage_test_data (create): {e}", exc_info=True)
        return redirect(url_for('.manage_test_data', lang=lang)) # Перенаправление для избежания повторной отправки формы

    elif action == 'check':
        # ... (код для проверки, как в вашем Фрагменте 2) ...
        return jsonify({
            "categories_count": ContentCategory.query.count(),
            "subcategories_count": ContentSubcategory.query.count(),
            "topics_count": ContentTopic.query.count(),
        })
    elif action == 'delete':
        try:
            # Более безопасное удаление, если есть связанные уроки
            topics_to_delete = ContentTopic.query.filter(ContentTopic.slug.like("test-topic%")).all()
            for tpc in topics_to_delete:
                Lesson.query.filter_by(topic_id=tpc.id).update({"topic_id": None}) # Отвязываем уроки
                db.session.delete(tpc)
            
            subcategories_to_delete = ContentSubcategory.query.filter(ContentSubcategory.slug.like("test-subcategory%")).all()
            for subcat in subcategories_to_delete:
                ContentTopic.query.filter_by(subcategory_id=subcat.id).delete() # Удаляем связанные темы
                db.session.delete(subcat)

            categories_to_delete = ContentCategory.query.filter(ContentCategory.slug.like("test-category%")).all()
            for cat in categories_to_delete:
                ContentSubcategory.query.filter_by(category_id=cat.id).delete() # Удаляем связанные подкатегории
                db.session.delete(cat)

            db.session.commit()
            flash("Тестовые данные иерархии удалены.", "info")
        except Exception as e:
            db.session.rollback()
            flash(f"Ошибка при удалении тестовых данных: {str(e)}", "danger")
            current_app.logger.error(f"Ошибка manage_test_data (delete): {e}", exc_info=True)
        return redirect(url_for('.manage_test_data', lang=lang))
            
    return f"""
    <h1>Управление тестовыми данными иерархии</h1>
    <p>Текущий язык: {lang}</p>
    <ul>
        <li><a href="{url_for('.manage_test_data', lang=lang, action='create')}">Создать тестовые данные</a></li>
        <li><a href="{url_for('.manage_test_data', lang=lang, action='check')}">Проверить (JSON)</a></li>
        <li><a href="{url_for('.manage_test_data', lang=lang, action='delete')}">Удалить тестовые данные</a></li>
    </ul>
    <p><a href="{url_for('.learning_hierarchy_view', lang=lang)}">К иерархии</a></p>
    """    

@subject_view_bp.route("/category/<int:category_id>")
@login_required
def view_category(lang, category_id):
    try:
        category = ContentCategory.query.get_or_404(category_id)
        subcategories = category.subcategories.order_by(ContentSubcategory.order).all()
        
        return render_template(
            "learning/category_view.html", # Убедитесь, что шаблон существует
            title=category.name,
            category=category,
            subcategories=subcategories,
            stats=get_user_stats(current_user.id),
            recommendations=get_user_recommendations(current_user.id),
            random_fact=get_random_fact(g.lang),
            user=current_user,
            has_subscription=current_user.has_subscription
        )
    except Exception as e:
        current_app.logger.error(f"Ошибка в view_category (ID: {category_id}): {e}", exc_info=True)
        flash(t("error_loading_category_data"), "danger")
        return redirect(url_for('.learning_hierarchy_view', lang=lang))