# routes/subject_view_routes.py
import json
import random
import os # Добавлен импорт os
from datetime import datetime, timedelta
import traceback
from flask import Blueprint, render_template, request, session, redirect, url_for, g, flash, current_app, jsonify
from flask_login import login_required, current_user
from extensions import db
from models import (
    Module, Lesson, UserProgress, Subject, LearningPath, User,
    VirtualPatientScenario, Test, Question, TestAttempt,
    ContentCategory, ContentSubcategory, ContentTopic, VirtualPatientAttempt
)
from translations import get_translation as t
from utils.unified_stats import get_unified_user_stats, get_module_stats_unified, get_subject_stats_unified

subject_view_bp = Blueprint(
    "subject_view_bp",
    __name__,
    url_prefix='/<string:lang>/learning-map/subject', # Префикс из Фрагмента 2
    template_folder='../templates'
)

# Языковые настройки из Фрагмента 2
SUPPORTED_LANGUAGES = ['en', 'ru', 'nl', 'uk', 'es', 'pt', 'tr', 'fa', 'ar']
DEFAULT_LANGUAGE = 'en'

@subject_view_bp.before_request
def before_request_subject_view():
    """Извлекает и валидирует язык из URL."""
    try:
        current_app.logger.info(f"=== before_request_subject_view called ===")
        current_app.logger.info(f"Request URL: {request.url}")
        current_app.logger.info(f"Request path: {request.path}")
        current_app.logger.info(f"View args: {request.view_args}")
        
        lang_from_url = request.view_args.get('lang') if request.view_args else None
        current_app.logger.info(f"Language from URL: {lang_from_url}")
        
        if lang_from_url and lang_from_url in SUPPORTED_LANGUAGES:
            g.lang = lang_from_url
        else:
            g.lang = session.get('lang') \
                     or request.accept_languages.best_match(SUPPORTED_LANGUAGES) \
                     or DEFAULT_LANGUAGE
        
        current_app.logger.info(f"Final language: {g.lang}")
        
        if session.get('lang') != g.lang:
            session['lang'] = g.lang
            
        current_app.logger.info(f"=== before_request_subject_view completed successfully ===")
            
    except Exception as e:
        current_app.logger.error(f"Error in before_request_subject_view: {e}", exc_info=True)
        # Не блокируем запрос, устанавливаем язык по умолчанию
        g.lang = DEFAULT_LANGUAGE

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


@subject_view_bp.route("/<int:subject_id>")
@login_required
def view_subject(lang, subject_id):
    """Отображает страницу просмотра предмета с его модулями и виртуальными пациентами."""
    current_lang = g.lang
    
    # Логируем сразу в начале функции
    current_app.logger.info(f"=== view_subject called with lang={lang}, subject_id={subject_id} ===")
    current_app.logger.info(f"Request URL: {request.url}")
    current_app.logger.info(f"Request endpoint: {request.endpoint}")

    def is_mobile_request():
        # Используем имеющуюся систему определения мобильных устройств
        from utils.mobile_detection import get_mobile_detector
        detector = get_mobile_detector()
        is_mobile = detector.is_mobile_device
        
        # Добавляем отладочную информацию
        user_agent = request.headers.get('User-Agent', 'No User-Agent')
        current_app.logger.info(f"Mobile detection - User-Agent: {user_agent}")
        current_app.logger.info(f"Mobile detection - is_mobile_device: {is_mobile}")
        current_app.logger.info(f"Mobile detection - device_type: {detector.device_type}")
        
        return is_mobile

    try:
        learning_paths = LearningPath.query.order_by(LearningPath.order).all()
        content_categories = ContentCategory.query.order_by(ContentCategory.order).all()

        selected_subject = Subject.query.get_or_404(subject_id)
        subject_modules = Module.query.filter_by(subject_id=subject_id).order_by(Module.order).all()

        # Обрабатываем модули текущего предмета
        for module in subject_modules:
            module_stats = get_module_stats_unified(module.id, current_user.id)
            module.progress = module_stats.get("progress", 0)
            module.completed_lessons = module_stats.get("completed_lessons", 0)
            module.total_lessons = module_stats.get("total_lessons", 0)

        virtual_patients = get_virtual_patients_for_subject(selected_subject, current_user.id)
        stats = get_unified_user_stats(current_user.id)
        recommendations = get_user_recommendations(current_user.id)
        random_fact = get_random_fact(g.lang)

        # Получаем все предметы и добавляем к ним данные о прогрессе
        all_subjects = Subject.query.all()
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
                current_app.logger.error(f"Error calculating progress for subject {subject.id}: {e}")
                # Устанавливаем значения по умолчанию при ошибке
                subject.progress_percentage = 0
                subject.total_lessons = 0
                subject.completed_lessons = 0
                subject.is_completed = False
                subject.estimated_time = "2h"
                subject.category = 'general'

        template = "mobile/learning/subject_view_mobile.html" if is_mobile_request() else "learning/subject_view.html"
        
        # Добавляем отладочную информацию о выбранном шаблоне
        current_app.logger.info(f"Selected template: {template}")

        return render_template(
            template,
            title=selected_subject.name,
            learning_paths=learning_paths,
            content_categories=content_categories,
            selected_subject=selected_subject,
            subject_modules=subject_modules,
            virtual_patients=virtual_patients,
            subjects=all_subjects,  # Используем обработанный список предметов
            user=current_user,
            has_subscription=current_user.has_subscription,
            stats=stats,
            recommendations=recommendations,
            random_fact=random_fact,
            # Добавляем данные для мобильного шаблона
            current_language=g.lang,
            user_stats=stats,
            supported_languages=SUPPORTED_LANGUAGES
        )

    except Exception as e:
        current_app.logger.error(f"Ошибка в view_subject (ID: {subject_id}): {e}", exc_info=True)
        flash(t("error_occurred_loading_data") + ": " + str(e), "danger")
        return redirect(url_for('main.index', lang=current_lang))

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
        
        stats = get_unified_user_stats(current_user.id)
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
            stats=get_unified_user_stats(current_user.id),
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
            stats=get_unified_user_stats(current_user.id),
            recommendations=get_user_recommendations(current_user.id),
            random_fact=get_random_fact(g.lang),
            user=current_user,
            has_subscription=current_user.has_subscription
        )
    except Exception as e:
        current_app.logger.error(f"Ошибка в view_category (ID: {category_id}): {e}", exc_info=True)
        flash(t("error_loading_category_data"), "danger")
        return redirect(url_for('.learning_hierarchy_view', lang=lang))

# Простой тестовый маршрут для проверки работы Blueprint
@subject_view_bp.route("/test")
def simple_test(lang):
    """Простой тест для проверки работы Blueprint."""
    return f"Blueprint works! Language: {lang}, URL: {request.url}"

# Тестовый маршрут для проверки определения мобильных устройств (без @login_required)
@subject_view_bp.route("/mobile-test-no-auth")
def mobile_test_no_auth(lang):
    """Тестовый маршрут для проверки определения мобильных устройств без авторизации."""
    from utils.mobile_detection import get_mobile_detector
    
    detector = get_mobile_detector()
    device_info = detector.get_device_info()
    
    user_agent = request.headers.get('User-Agent', 'No User-Agent')
    
    test_info = {
        'user_agent': user_agent,
        'device_info': device_info,
        'should_use_mobile': detector.should_use_mobile_template(),
        'template_would_be': "mobile/learning/subject_view_mobile.html" if detector.is_mobile_device else "learning/subject_view.html",
        'url': request.url,
        'endpoint': request.endpoint
    }
    
    return jsonify(test_info)

# Тестовый маршрут для принудительного использования мобильного шаблона
@subject_view_bp.route("/force-mobile/<int:subject_id>")
@login_required
def force_mobile_subject(lang, subject_id):
    """Принудительно загружает мобильную версию страницы предмета."""
    current_lang = g.lang
    
    current_app.logger.info(f"=== force_mobile_subject called with lang={lang}, subject_id={subject_id} ===")

    try:
        learning_paths = LearningPath.query.order_by(LearningPath.order).all()
        content_categories = ContentCategory.query.order_by(ContentCategory.order).all()

        selected_subject = Subject.query.get_or_404(subject_id)
        subject_modules = Module.query.filter_by(subject_id=subject_id).order_by(Module.order).all()

        virtual_patients = get_virtual_patients_for_subject(selected_subject, current_user.id)
        stats = get_unified_user_stats(current_user.id)
        recommendations = get_user_recommendations(current_user.id)
        random_fact = get_random_fact(g.lang)

        template = "mobile/learning/subject_view_mobile.html"  # Принудительно мобильный шаблон
        current_app.logger.info(f"Force using mobile template: {template}")

        return render_template(
            template,
            title=selected_subject.name,
            learning_paths=learning_paths,
            content_categories=content_categories,
            selected_subject=selected_subject,
            subject_modules=subject_modules,
            virtual_patients=virtual_patients,
            subjects=Subject.query.all(),
            user=current_user,
            has_subscription=current_user.has_subscription,
            stats=stats,
            recommendations=recommendations,
            random_fact=random_fact,
            # Добавляем данные для мобильного шаблона
            current_language=g.lang,
            user_stats=stats,
            supported_languages=SUPPORTED_LANGUAGES
        )

    except Exception as e:
        current_app.logger.error(f"Ошибка в force_mobile_subject (ID: {subject_id}): {e}", exc_info=True)
        flash(t("error_occurred_loading_data") + ": " + str(e), "danger")
        return redirect(url_for('main.index', lang=current_lang))

# Добавьте этот отладочный маршрут в subject_view_routes.py

@subject_view_bp.route("/debug/<int:subject_id>")
@login_required
def debug_view_subject(lang, subject_id):
    """Отладка загрузки данных для view_subject"""
    try:
        html = [f"<h1>🔍 Отладка view_subject для ID: {subject_id}</h1>"]
        
        # 1. Проверяем предмет
        selected_subject = Subject.query.get(subject_id)
        if not selected_subject:
            return f"<h1>❌ Subject с ID {subject_id} не найден!</h1>"
        
        html.append(f"""
        <h2>1. Предмет</h2>
        <ul>
            <li><strong>ID:</strong> {selected_subject.id}</li>
            <li><strong>Название:</strong> {selected_subject.name}</li>
            <li><strong>Learning Path ID:</strong> {selected_subject.learning_path_id}</li>
            <li><strong>Описание:</strong> {getattr(selected_subject, 'description', 'Нет описания')}</li>
        </ul>
        """)
        
        # 2. Проверяем загрузку модулей
        html.append("<h2>2. Загрузка модулей</h2>")
        
        # Точно такой же запрос как в view_subject
        subject_modules = Module.query.filter_by(subject_id=subject_id).order_by(Module.order).all()
        
        html.append(f"<p><strong>Найдено модулей:</strong> {len(subject_modules)}</p>")
        
        if subject_modules:
            html.append("<h3>Детали модулей:</h3>")
            for i, module in enumerate(subject_modules):
                # Получаем статистику модуля
                try:
                    module_stats = get_module_stats_unified(module.id, current_user.id)
                    
                    html.append(f"""
                    <div style="border: 1px solid #ccc; padding: 10px; margin: 10px 0;">
                        <h4>Модуль {i+1}: {module.title}</h4>
                        <ul>
                            <li><strong>ID:</strong> {module.id}</li>
                            <li><strong>Title:</strong> {module.title}</li>
                            <li><strong>Order:</strong> {getattr(module, 'order', 'Не установлен')}</li>
                            <li><strong>Subject ID:</strong> {module.subject_id}</li>
                            <li><strong>Description:</strong> {getattr(module, 'description', 'Нет описания')}</li>
                            <li><strong>Is Premium:</strong> {getattr(module, 'is_premium', False)}</li>
                        </ul>
                        
                        <h5>Статистика модуля:</h5>
                        <ul>
                            <li><strong>Progress:</strong> {module_stats.get('progress', 0)}%</li>
                            <li><strong>Completed Lessons:</strong> {module_stats.get('completed_lessons', 0)}</li>
                            <li><strong>Total Lessons:</strong> {module_stats.get('total_lessons', 0)}</li>
                        </ul>
                        
                        <h5>Уроки в модуле:</h5>
                        <ul>
                    """)
                    
                    module_lessons = Lesson.query.filter_by(module_id=module.id).all()
                    for lesson in module_lessons[:5]:  # Показываем первые 5
                        html.append(f"<li>{lesson.title}</li>")
                    
                    if len(module_lessons) > 5:
                        html.append(f"<li>... и еще {len(module_lessons) - 5} уроков</li>")
                    
                    html.append("</ul></div>")
                    
                except Exception as e:
                    html.append(f"<p style='color: red;'>Ошибка получения статистики модуля: {e}</p>")
        else:
            html.append("<p style='color: red;'>❌ <strong>ПРОБЛЕМА: Модули не найдены!</strong></p>")
            
            # Проверяем есть ли модули в БД для этого предмета
            all_modules = Module.query.all()
            html.append(f"<p>Всего модулей в БД: {len(all_modules)}</p>")
            
            if all_modules:
                html.append("<h4>Все модули в БД:</h4><ul>")
                for module in all_modules:
                    html.append(f"<li>ID: {module.id}, Title: {module.title}, Subject ID: {module.subject_id}</li>")
                html.append("</ul>")
                
                # Проверяем есть ли модули с правильным subject_id
                matching_modules = [m for m in all_modules if m.subject_id == subject_id]
                html.append(f"<p style='color: blue;'>Модулей с subject_id={subject_id}: {len(matching_modules)}</p>")
        
        # 3. Тест шаблона
        html.append("<h2>3. Тест передачи данных в шаблон</h2>")
        
        template_data = {
            'selected_subject': selected_subject,
            'subject_modules': subject_modules,
            'user': current_user,
            'has_subscription': current_user.has_subscription
        }
        
        html.append(f"""
        <h4>Данные для шаблона:</h4>
        <ul>
            <li><strong>selected_subject:</strong> {template_data['selected_subject'].name if template_data['selected_subject'] else 'None'}</li>
            <li><strong>subject_modules:</strong> {len(template_data['subject_modules'])} модулей</li>
            <li><strong>user:</strong> {template_data['user'].username if template_data['user'] else 'None'}</li>
            <li><strong>has_subscription:</strong> {template_data['has_subscription']}</li>
        </ul>
        """)
        
        # 4. Ссылки для тестирования
        html.append(f"""
        <h2>4. Тестирование</h2>
        <p><a href="{url_for('subject_view_bp.view_subject', lang=lang, subject_id=subject_id)}" 
              style="background: blue; color: white; padding: 10px; text-decoration: none;">
            🎯 Открыть оригинальную страницу предмета
        </a></p>
        """)
        
        return "".join(html)
        
    except Exception as e:
        import traceback
        return f"<h1>❌ Ошибка отладки</h1><p>{str(e)}</p><pre>{traceback.format_exc()}</pre>"    

# Добавляем debug маршрут для диагностики статистики
@subject_view_bp.route("/debug/stats/<int:subject_id>")
@login_required
def debug_stats_view(lang, subject_id):
    """Debug версия для диагностики проблемы со статистикой"""
    try:
        current_app.logger.info(f"=== DEBUG STATS: Начало диагностики для пользователя {current_user.id} ===")
        
        # 1. Проверка авторизации
        current_app.logger.info(f"1. АВТОРИЗАЦИЯ:")
        current_app.logger.info(f"   - current_user: {current_user}")
        current_app.logger.info(f"   - current_user.id: {current_user.id}")
        current_app.logger.info(f"   - current_user.is_authenticated: {current_user.is_authenticated}")
        
        # 2. Проверка данных в базе
        current_app.logger.info(f"2. ДАННЫЕ В БАЗЕ:")
        
        # Проверяем записи UserProgress
        user_progress_count = UserProgress.query.filter_by(user_id=current_user.id).count()
        completed_progress_count = UserProgress.query.filter_by(user_id=current_user.id, completed=True).count()
        
        current_app.logger.info(f"   - Всего записей UserProgress: {user_progress_count}")
        current_app.logger.info(f"   - Завершенных уроков: {completed_progress_count}")
        
        # Проверяем уроки в базе
        total_lessons = Lesson.query.count()
        current_app.logger.info(f"   - Всего уроков в базе: {total_lessons}")
        
        # 3. Вызов функции get_unified_user_stats
        current_app.logger.info(f"3. ВЫЗОВ get_unified_user_stats:")
        stats = get_unified_user_stats(current_user.id)
        current_app.logger.info(f"   - Результат get_unified_user_stats: {stats}")
        
        # 4. Проверка конкретных значений
        current_app.logger.info(f"4. ПРОВЕРКА ЗНАЧЕНИЙ:")
        current_app.logger.info(f"   - stats.overall_progress: {stats.get('overall_progress', 'НЕТ')}")
        current_app.logger.info(f"   - stats.completed_lessons: {stats.get('completed_lessons', 'НЕТ')}")
        current_app.logger.info(f"   - stats.total_lessons: {stats.get('total_lessons', 'НЕТ')}")
        current_app.logger.info(f"   - stats.total_time_spent: {stats.get('total_time_spent', 'НЕТ')}")
        current_app.logger.info(f"   - stats.active_days: {stats.get('active_days', 'НЕТ')}")
        
        # 5. Проверка предмета
        selected_subject = Subject.query.get(subject_id)
        current_app.logger.info(f"5. ПРЕДМЕТ:")
        current_app.logger.info(f"   - selected_subject: {selected_subject}")
        if selected_subject:
            current_app.logger.info(f"   - subject.name: {selected_subject.name}")
            current_app.logger.info(f"   - subject.id: {selected_subject.id}")
        
        # 6. Проверка модулей предмета
        subject_modules = Module.query.filter_by(subject_id=subject_id).all()
        current_app.logger.info(f"6. МОДУЛИ ПРЕДМЕТА:")
        current_app.logger.info(f"   - Количество модулей: {len(subject_modules)}")
        
        for i, module in enumerate(subject_modules[:3]):  # Показываем первые 3
            module_stats = get_module_stats_unified(module.id, current_user.id)
            current_app.logger.info(f"   - Модуль {i+1}: {module.title}")
            current_app.logger.info(f"     * progress: {module_stats.get('progress', 0)}%")
            current_app.logger.info(f"     * completed_lessons: {module_stats.get('completed_lessons', 0)}")
            current_app.logger.info(f"     * total_lessons: {module_stats.get('total_lessons', 0)}")
        
        # 7. Формируем HTML для отображения результатов
        html = []
        html.append(f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Debug Stats - Subject {subject_id}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .debug-section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .success {{ background-color: #d4edda; border-color: #c3e6cb; }}
                .warning {{ background-color: #fff3cd; border-color: #ffeaa7; }}
                .error {{ background-color: #f8d7da; border-color: #f5c6cb; }}
                .info {{ background-color: #d1ecf1; border-color: #bee5eb; }}
                pre {{ background: #f8f9fa; padding: 10px; border-radius: 3px; overflow-x: auto; }}
                .stat-item {{ margin: 10px 0; padding: 10px; background: #f8f9fa; border-radius: 3px; }}
                .stat-label {{ font-weight: bold; color: #495057; }}
                .stat-value {{ color: #28a745; font-size: 1.2em; }}
            </style>
        </head>
        <body>
            <h1>🔍 Debug Statistics - Subject {subject_id}</h1>
            <p><strong>User:</strong> {current_user.username} (ID: {current_user.id})</p>
            <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        """)
        
        # Секция авторизации
        html.append(f"""
        <div class="debug-section success">
            <h3>✅ 1. Авторизация</h3>
            <div class="stat-item">
                <div class="stat-label">Пользователь:</div>
                <div class="stat-value">{current_user.username}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">ID пользователя:</div>
                <div class="stat-value">{current_user.id}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Авторизован:</div>
                <div class="stat-value">{current_user.is_authenticated}</div>
            </div>
        </div>
        """)
        
        # Секция данных в базе
        html.append(f"""
        <div class="debug-section info">
            <h3>📊 2. Данные в базе</h3>
            <div class="stat-item">
                <div class="stat-label">Всего записей UserProgress:</div>
                <div class="stat-value">{user_progress_count}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Завершенных уроков:</div>
                <div class="stat-value">{completed_progress_count}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Всего уроков в базе:</div>
                <div class="stat-value">{total_lessons}</div>
            </div>
        </div>
        """)
        
        # Секция статистики
        html.append(f"""
        <div class="debug-section {'success' if stats.get('overall_progress', 0) > 0 else 'warning'}">
            <h3>📈 3. Статистика пользователя</h3>
            <div class="stat-item">
                <div class="stat-label">Общий прогресс:</div>
                <div class="stat-value">{stats.get('overall_progress', 0)}%</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Завершенных уроков:</div>
                <div class="stat-value">{stats.get('completed_lessons', 0)}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Всего уроков:</div>
                <div class="stat-value">{stats.get('total_lessons', 0)}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Время обучения (мин):</div>
                <div class="stat-value">{stats.get('total_time_spent', 0)}</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">Дней активности:</div>
                <div class="stat-value">{stats.get('active_days', 0)}</div>
            </div>
        </div>
        """)
        
        # Секция предмета
        if selected_subject:
            html.append(f"""
            <div class="debug-section info">
                <h3>📚 4. Предмет</h3>
                <div class="stat-item">
                    <div class="stat-label">Название:</div>
                    <div class="stat-value">{selected_subject.name}</div>
                </div>
                <div class="stat-item">
                    <div class="stat-label">ID:</div>
                    <div class="stat-value">{selected_subject.id}</div>
                </div>
            </div>
            """)
        
        # Секция модулей
        html.append(f"""
        <div class="debug-section info">
            <h3>📖 5. Модули предмета ({len(subject_modules)})</h3>
        """)
        
        for i, module in enumerate(subject_modules[:5]):  # Показываем первые 5
            module_stats = get_module_stats_unified(module.id, current_user.id)
            html.append(f"""
            <div class="stat-item">
                <div class="stat-label">Модуль {i+1}: {module.title}</div>
                <div class="stat-value">
                    Прогресс: {module_stats.get('progress', 0)}% 
                    ({module_stats.get('completed_lessons', 0)}/{module_stats.get('total_lessons', 0)})
                </div>
            </div>
            """)
        
        if len(subject_modules) > 5:
            html.append(f"<p><em>... и еще {len(subject_modules) - 5} модулей</em></p>")
        
        html.append("</div>")
        
        # Секция действий
        html.append(f"""
        <div class="debug-section warning">
            <h3>🔧 6. Действия</h3>
            <p><a href="{url_for('learning_map_bp.debug_add_progress', lang=lang)}" 
                  style="background: #007bff; color: white; padding: 10px; text-decoration: none; border-radius: 3px;">
                ➕ Добавить тестовый прогресс
            </a></p>
            <p><a href="{url_for('subject_view_bp.view_subject', lang=lang, subject_id=subject_id)}" 
                  style="background: #28a745; color: white; padding: 10px; text-decoration: none; border-radius: 3px;">
                🎯 Открыть оригинальную страницу
            </a></p>
        </div>
        """)
        
        # Секция сырых данных
        html.append(f"""
        <div class="debug-section">
            <h3>🔍 7. Сырые данные</h3>
            <pre>{json.dumps(stats, indent=2, ensure_ascii=False)}</pre>
        </div>
        """)
        
        html.append("</body></html>")
        
        current_app.logger.info(f"=== DEBUG STATS: Диагностика завершена ===")
        
        return "".join(html)
        
    except Exception as e:
        current_app.logger.error(f"Ошибка в debug_stats_view: {e}", exc_info=True)
        return f"""
        <h1>❌ Ошибка диагностики</h1>
        <p><strong>Ошибка:</strong> {str(e)}</p>
        <pre>{traceback.format_exc()}</pre>
        """    