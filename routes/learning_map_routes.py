# routes/learning_map_routes.py

from flask import (
    Blueprint, render_template, request, session, redirect, url_for, g, flash, 
    jsonify, current_app
)
from models import VirtualPatientScenario, VirtualPatientAttempt
from flask_login import login_required, current_user
from models import db, LearningPath, Subject, Module, Lesson, UserProgress, Test, UserExamDate, ContentCategory
from sqlalchemy import func
import json
import os
from datetime import datetime
from translations import get_translation as t  # предполагаем, что функция называется get_translation
# Создаем Blueprint для карты обучения
learning_map_bp = Blueprint(
    "learning_map_bp",
    __name__,
    url_prefix='/<string:lang>/learning-map',
    template_folder='../templates'
    )

# --- Языковые и защитные обработчики ---
SUPPORTED_LANGUAGES = ['en', 'ru', 'nl', 'uk', 'es', 'pt', 'tr', 'fa']
DEFAULT_LANGUAGE = 'en'

@learning_map_bp.before_request
def before_request_learning_map():
    """
    Извлекает и валидирует язык из URL.
    """
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

@learning_map_bp.context_processor
def inject_lang_learning_map():
    """Добавляет lang в контекст шаблонов этого блюпринта."""
    lang = getattr(g, 'lang', session.get('lang', DEFAULT_LANGUAGE))
    return dict(lang=lang)

@learning_map_bp.route("/check-categories")
@login_required
def check_categories(lang):
    """Проверяет категории и создает тестовые данные если их нет"""
    try:
        from models import ContentCategory, ContentSubcategory, ContentTopic
        
        # Проверяем существующие категории
        categories = ContentCategory.query.all()
        
        output = "<h1>Проверка категорий</h1>"
        
        if not categories:
            output += "<p style='color:red'>Категории не найдены. Создаем тестовые данные...</p>"
            
            # Создаем тестовую категорию
            cat = ContentCategory(
                name="Анатомия зуба",
                slug="tooth-anatomy",
                icon="bi-book",
                order=1
            )
            db.session.add(cat)
            db.session.flush()
            
            # Создаем подкатегорию
            subcat = ContentSubcategory(
                name="Строение зуба",
                slug="tooth-structure",
                category_id=cat.id,
                icon="bi-diagram-3",
                order=1
            )
            db.session.add(subcat)
            db.session.flush()
            
            # Создаем тему
            topic = ContentTopic(
                name="Коронка зуба",
                slug="tooth-crown",
                subcategory_id=subcat.id,
                description="Строение коронки зуба",
                order=1
            )
            db.session.add(topic)
            db.session.commit()
            
            output += "<p style='color:green'>Тестовые данные успешно созданы!</p>"
        else:
            output += f"<p>Найдено категорий: {len(categories)}</p>"
            
            for cat in categories:
                output += f"<h2>{cat.name} (ID: {cat.id})</h2>"
                subcats = cat.subcategories.all() if hasattr(cat.subcategories, 'all') else []
                output += f"<p>Подкатегорий: {len(subcats)}</p>"
        
        # Проверяем, правильно ли загружаются категории
        check_cat = ContentCategory.query.first()
        if check_cat:
            output += f"<h3>Тестовая категория загружена:</h3>"
            output += f"<p>ID: {check_cat.id}, Название: {check_cat.name}</p>"
        
        return output
    except Exception as e:
        return f"<h1>Ошибка</h1><p>{str(e)}</p><p>Тип: {type(e).__name__}</p>"

# --- Маршрут отображения карты обучения (обновленный) ---
@learning_map_bp.route("/")
@learning_map_bp.route("/<int:path_id>")
@login_required
def learning_map(lang, path_id=None):
    """Отображает интерактивную карту обучения."""
    current_lang = g.lang
    
    try:
        # Добавьте явный импорт ContentCategory
        from models import ContentCategory
        
        # Добавьте загрузку категорий
        content_categories = ContentCategory.query.order_by(ContentCategory.order).all()
        print(f"DEBUG: Загружено категорий: {len(content_categories)}")

        for cat in content_categories:
            print(f"DEBUG: Категория: {cat.name}, подкатегорий: {cat.subcategories.count()}")
            for subcat in cat.subcategories.all():
                print(f"DEBUG:   Подкатегория: {subcat.name}, тем: {subcat.topics.count()}")
                for topic in subcat.topics.all():
                    print(f"DEBUG:     Тема: {topic.name}")
        # Получаем все пути обучения
        learning_paths = LearningPath.query.filter_by(is_active=True).order_by(LearningPath.order).all()
        for path in learning_paths:
            if path.id == 6:  # Virtual Patients
                vp_stats = get_virtual_patients_stats(current_user.id)
                path.vp_stats = vp_stats        
        # Если path_id не указан, используем первый путь
        if path_id is None and learning_paths:
            path_id = learning_paths[0].id
        
        # Получаем запрашиваемый путь
        current_path = LearningPath.query.get_or_404(path_id) if path_id else None
        
        # Получаем все предметы с предзагрузкой модулей
        all_subjects = []
        
        # Обрабатываем предметы и их модули
        subjects_query = Subject.query.all()
        for subject in subjects_query:
            # Получаем все модули для этого предмета
            modules = Module.query.filter_by(subject_id=subject.id).order_by(Module.order).all()
            
            # Обрабатываем каждый модуль
            processed_modules = []
            total_progress = 0
            
            for module in modules:
                # Получаем статистику модуля
                module_stats = get_module_stats(module.id, current_user.id)
                
                # Добавляем модуль с прогрессом
                processed_modules.append({
                    'id': module.id,
                    'title': module.title,
                    'description': module.description if hasattr(module, 'description') else '',
                    'is_premium': module.is_premium if hasattr(module, 'is_premium') else False,
                    'is_final_test': module.is_final_test if hasattr(module, 'is_final_test') else False,
                    'icon': module.icon if hasattr(module, 'icon') else 'file-earmark-text',
                    'progress': module_stats['progress'],
                    'completed_lessons': module_stats['completed_lessons'],
                    'total_lessons': module_stats['total_lessons']
                })
                
                total_progress += module_stats['progress']
            
            # Вычисляем средний прогресс предмета
            subject_progress = round(total_progress / len(modules)) if modules else 0
            
            # Создаем словарь с информацией о предмете
            subject_data = {
                'id': subject.id,
                'name': subject.name,
                'description': subject.description if hasattr(subject, 'description') else '',
                'icon': subject.icon if hasattr(subject, 'icon') else 'folder2-open',
                'learning_path_id': subject.learning_path_id,
                'progress': subject_progress,
                'modules': processed_modules
            }
            
            all_subjects.append(subject_data)
        
        # Статистика пользователя
        stats = get_user_stats(current_user.id)

        content_categories = ContentCategory.query.order_by(ContentCategory.order).all()

        
        return render_template(
                    "learning/subject_view.html",  # Изменено с map.html на subject_view.html
                    title='Learning Map',
                    learning_paths=learning_paths,
                    current_path=current_path,
                    subjects=all_subjects,
                    selected_subject=None,  # Добавлен этот параметр
                    user=current_user,
                    has_subscription=current_user.has_subscription,
                    stats=stats,
                    recommendations=get_user_recommendations(current_user.id),  # Добавляем рекомендации
                    content_categories=content_categories

        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash("An error occurred while loading the learning map: " + str(e), "danger")
        return redirect(url_for('main_bp.index', lang=current_lang))

# --- НОВЫЙ API-маршрут для запуска модуля ---
@learning_map_bp.route("/api/start-module/<int:module_id>")
@login_required
def start_module(lang, module_id):
    """Начать или продолжить изучение модуля через API"""
    try:
        # Получаем модуль
        module = Module.query.get_or_404(module_id)
        
        # Проверяем доступность для пользователя
        if module.is_premium and not current_user.has_subscription:
            return jsonify({
                'success': False, 
                'message': 'This module is only available to premium subscribers'
            }), 403
        
        # Находим первый урок или незавершенный урок
        lessons = Lesson.query.filter_by(module_id=module.id).order_by(Lesson.order).all()
        lesson = lessons[0] if lessons else None
        
        if lesson:
            redirect_url = url_for('lesson_bp.lesson_view', 
                                   lang=g.lang, 
                                   module_id=module.id, 
                                   lesson_index=0)
            return jsonify({
                'success': True,
                'redirect_url': redirect_url
            })
        else:
            return jsonify({
                'success': False, 
                'message': 'No lessons found in this module'
            }), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@learning_map_bp.route("/manage-test-data")
@login_required
def manage_test_data(lang):
    """Диагностика и управление тестовыми данными"""
    try:
        # Импортируем здесь явно, чтобы увидеть ошибки импорта
        from models import ContentCategory, ContentSubcategory, ContentTopic
        
        # Проверка существующих данных
        categories = ContentCategory.query.all()
        subcategories = ContentSubcategory.query.all()
        topics = ContentTopic.query.all()
        
        # Если нет данных, создаем тестовые
        if not categories:
            category = ContentCategory(
                name="Анатомия зуба",
                slug="dental-anatomy",
                icon="bi-book",
                order=1
            )
            db.session.add(category)
            db.session.flush()
            
            flash("✅ Создана категория: Анатомия зуба", "success")
        else:
            # Используем существующую категорию
            category = categories[0]
            flash(f"ℹ️ Найдена категория: {category.name}", "info")
        
        if not subcategories:
            subcategory = ContentSubcategory(
                name="Строение зуба",
                slug="tooth-structure",
                category_id=category.id,
                icon="bi-diagram-3",
                order=1
            )
            db.session.add(subcategory)
            db.session.flush()
            
            flash("✅ Создана подкатегория: Строение зуба", "success")
        else:
            # Используем существующую подкатегорию
            subcategory = subcategories[0]
            flash(f"ℹ️ Найдена подкатегория: {subcategory.name}", "info")
        
        if not topics:
            topic = ContentTopic(
                name="Коронка зуба",
                slug="tooth-crown",
                subcategory_id=subcategory.id,
                description="Изучение строения коронки зуба",
                order=1
            )
            db.session.add(topic)
            db.session.flush()
            
            flash("✅ Создана тема: Коронка зуба", "success")
        else:
            # Используем существующую тему
            topic = topics[0]
            flash(f"ℹ️ Найдена тема: {topic.name}", "info")
        
        # Создаем урок, связанный с темой
        modules = Module.query.all()
        if modules:
            module = modules[0]
            
            # Проверяем, есть ли уже уроки в этой теме
            existing_lesson = Lesson.query.filter_by(content_topic_id=topic.id).first()
            
            if not existing_lesson:
                lesson = Lesson(
                    title=f"Урок по теме {topic.name}",
                    module_id=module.id,
                    content_type="learning_card",
                    content_topic_id=topic.id,
                    order=1,
                    content=json.dumps({
                        "cards": [
                            {"title": "Введение", "content": "Содержимое карточки"}
                        ]
                    })
                )
                db.session.add(lesson)
                
                flash(f"✅ Создан урок для темы: {topic.name}", "success")
            else:
                flash(f"ℹ️ Урок для темы {topic.name} уже существует", "info")
        else:
            flash("⚠️ Не найдено ни одного модуля для создания урока", "warning")
        
        # Сохраняем изменения
        db.session.commit()
        
        # Готовим данные для отчета
        report = {
            "categories_count": len(categories),
            "categories": [{"id": c.id, "name": c.name, "subcategories_count": c.subcategories.count() if hasattr(c.subcategories, 'count') else '?'} for c in categories],
            "subcategories_count": len(subcategories),
            "subcategories": [{"id": s.id, "name": s.name, "category_id": s.category_id, "topics_count": s.topics.count() if hasattr(s.topics, 'count') else '?'} for s in subcategories],
            "topics_count": len(topics),
            "topics": [{"id": t.id, "name": t.name, "subcategory_id": t.subcategory_id} for t in topics],
        }
        
        # Возвращаем страницу с отчетом о данных
        return render_template(
            "diagnostic.html",  # Создайте простой шаблон для отображения диагностики
            title="Диагностика данных",
            report=report
        )
    except Exception as e:
        db.session.rollback()
        flash(f"❌ Ошибка: {str(e)}", "danger")
        
        # Возвращаем страницу с информацией об ошибке
        return render_template(
            "diagnostic.html",
            title="Ошибка диагностики",
            error=str(e),
            error_type=type(e).__name__
        )

# --- Существующий маршрут перенаправления ---
@learning_map_bp.route("/start-module/<int:module_id>")
@login_required
def start_module_redirect(lang, module_id):
    """Перенаправляет на правильную страницу модуля"""
    try:
        # Получаем модуль
        module = Module.query.get_or_404(module_id)
        
        # Проверяем доступность для пользователя
        if module.is_premium and not current_user.has_subscription:
            flash('This module is only available to premium subscribers', 'warning')
            return redirect(url_for('learning_map_bp.learning_map', lang=g.lang))

        # Если это финальный тест
        if module.is_final_test:
            subject = Subject.query.get(module.subject_id)
            return redirect(url_for('tests.start_final_test', lang=g.lang, subject_id=subject.id))
            
        # Перенаправляем на новую страницу модуля
        return redirect(url_for('modules_bp.module_view', lang=g.lang, module_id=module.id))
    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f'Error starting module: {str(e)}', 'danger')
        return redirect(url_for('learning_map_bp.learning_map', lang=g.lang))

# --- API-эндпоинт ---
@learning_map_bp.route("/api/data/<int:path_id>")
@login_required
def get_learning_map_data(lang, path_id):
    """API-эндпоинт для получения данных карты обучения"""
    try:
        # Получаем запрашиваемый путь обучения
        learning_path = LearningPath.query.get_or_404(path_id)
        
        # Формируем базовый ответ
        result = {
            "path": {
                "id": learning_path.id,
                "name": learning_path.name,
                "description": learning_path.description
            },
            "subjects": []
        }
        
        # Получаем все предметы для этого пути
        subjects = Subject.query.filter_by(learning_path_id=path_id).order_by(subject.order).all()
        
        # Добавляем информацию о каждом предмете
        for subject in subjects:
            # Рассчитываем прогресс предмета
            subject_progress = calculate_subject_progress(subject.id, current_user.id)
            
            subject_data = {
                "id": subject.id,
                "name": subject.name,
                "description": subject.description,
                "icon": subject.icon,
                "progress": subject_progress,
                "modules": []
            }
            
            # Получаем модули для предмета
            modules = Module.query.filter_by(subject_id=subject.id).order_by(Module.order).all()
            
            # Добавляем информацию о каждом модуле
            for module in modules:
                # Получаем статистику для модуля
                module_stats = get_module_stats(module.id, current_user.id)
                
                module_data = {
                    "id": module.id,
                    "title": module.title,
                    "description": module.description,
                    "icon": module.icon,
                    "order": module.order,
                    "is_premium": module.is_premium,
                    "is_final_test": module.is_final_test,
                    "progress": module_stats["progress"],
                    "completed_lessons": module_stats["completed_lessons"],
                    "total_lessons": module_stats["total_lessons"]
                }
                
                subject_data["modules"].append(module_data)
            
            result["subjects"].append(subject_data)
        
        return jsonify(result)
    except Exception as e:
        # Логируем ошибку
        current_app.logger.error(f"Общая ошибка API: {str(e)}")
        # Возвращаем информацию об ошибке в ответе
        return jsonify({
            "error": "Внутренняя ошибка сервера",
            "details": str(e),
            "type": type(e).__name__
        }), 500


# Полная версия функций для расчета и отображения прогресса
def calculate_subject_progress(subject_id, user_id):
    """Рассчитывает прогресс предмета для пользователя"""
    try:
        # Получаем все уроки для данного предмета через JOIN
        subject_lessons = db.session.query(Lesson.id).join(
            Module, Module.id == Lesson.module_id
        ).filter(
            Module.subject_id == subject_id
        ).all()
        
        # Преобразуем результат в список ID уроков
        lesson_ids = [lesson[0] for lesson in subject_lessons]
        total_lessons = len(lesson_ids)
        
        if total_lessons == 0:
            return 0
        
        # Получаем все завершенные уроки за один запрос
        completed_lessons_count = UserProgress.query.filter(
            UserProgress.user_id == user_id,
            UserProgress.lesson_id.in_(lesson_ids),
            UserProgress.completed == True
        ).count()
        
        # Расчет прогресса для данного предмета
        return round((completed_lessons_count / total_lessons) * 100) if total_lessons > 0 else 0
    except Exception as e:
        current_app.logger.error(f"Ошибка в calculate_subject_progress: {str(e)}", exc_info=True)
        return 0

def get_user_recommendations(user_id, limit=3):
    """
    Возвращает рекомендуемые модули для пользователя
    """
    try:
        # Получаем уроки, которые пользователь начал, но не завершил
        in_progress_lesson_ids = db.session.query(UserProgress.lesson_id).filter(
            UserProgress.user_id == user_id,
            UserProgress.completed == False
        ).all()
        in_progress_lesson_ids = [lesson_id[0] for lesson_id in in_progress_lesson_ids]
        
        # Получаем модули для этих уроков
        in_progress_modules = []
        
        if in_progress_lesson_ids:
            in_progress_modules = db.session.query(
                Module, Lesson, Subject.name.label('subject_name')
            ).join(
                Lesson, Lesson.module_id == Module.id
            ).join(
                Subject, Subject.id == Module.subject_id
            ).filter(
                Lesson.id.in_(in_progress_lesson_ids)
            ).group_by(Module.id).limit(limit).all()
        
        # Если нет незавершенных модулей, рекомендуем популярные или следующие в порядке
        if len(in_progress_modules) < limit:
            # Получаем модули, которые пользователь еще не начал
            remaining_limit = limit - len(in_progress_modules)
            
            completed_module_ids = db.session.query(Module.id).join(
                Lesson, Lesson.module_id == Module.id
            ).join(
                UserProgress, UserProgress.lesson_id == Lesson.id
            ).filter(
                UserProgress.user_id == user_id,
                UserProgress.completed == True
            ).group_by(Module.id).having(
                db.func.count(Lesson.id) == db.func.count(UserProgress.id)
            ).all()
            
            completed_module_ids = [module_id[0] for module_id in completed_module_ids]
            
            # Исключаем модули, которые уже в процессе
            in_progress_module_ids = [module[0].id for module in in_progress_modules]
            
            # Формируем список исключаемых ID
            exclude_ids = completed_module_ids + in_progress_module_ids
            
            # Получаем следующие модули для рекомендации
            next_modules_query = db.session.query(
                Module, Subject.name.label('subject_name')
            ).join(
                Subject, Subject.id == Module.subject_id
            )
            
            # Добавляем фильтр только если есть что исключать
            if exclude_ids:
                next_modules_query = next_modules_query.filter(
                    ~Module.id.in_(exclude_ids)
                )
            
            next_modules = next_modules_query.order_by(
                Module.id
            ).limit(remaining_limit).all()
            
            # Форматируем данные
            next_modules_formatted = [
                {
                    'module_id': module.id,
                    'title': module.title, 
                    'icon': module.icon if hasattr(module, 'icon') else 'journal-text',
                    'subject_name': subject_name
                } for module, subject_name in next_modules
            ]
        else:
            next_modules_formatted = []
        
        # Форматируем данные для модулей в процессе
        in_progress_formatted = [
            {
                'module_id': module.id,
                'title': module.title, 
                'icon': module.icon if hasattr(module, 'icon') else 'journal-text',
                'subject_name': subject_name
            } for module, lesson, subject_name in in_progress_modules
        ]
        
        # Объединяем результаты
        recommendations = in_progress_formatted + next_modules_formatted
        
        return recommendations[:limit]  # Ограничиваем количество рекомендаций
        
    except Exception as e:
        current_app.logger.error(f"Ошибка при получении рекомендаций: {str(e)}", exc_info=True)
        return []
    
def get_module_stats(module_id, user_id):
    """Рассчитывает статистику модуля для пользователя (оптимизированная версия)"""
    try:
        # Получаем все уроки в модуле
        lessons = Lesson.query.filter_by(module_id=module_id).with_entities(Lesson.id).all()
        lesson_ids = [lesson.id for lesson in lessons]
        total_lessons = len(lesson_ids)
        
        if total_lessons == 0:
            return {
                "progress": 0,
                "completed_lessons": 0,
                "total_lessons": 0
            }
        
        # Получаем количество завершенных уроков за один запрос
        completed_lessons = UserProgress.query.filter(
            UserProgress.user_id == user_id,
            UserProgress.lesson_id.in_(lesson_ids),
            UserProgress.completed == True
        ).count()
        
        # Рассчитываем прогресс
        progress = (completed_lessons / total_lessons) * 100 if total_lessons > 0 else 0
        
        return {
            "progress": round(progress),
            "completed_lessons": completed_lessons,
            "total_lessons": total_lessons
        }
    except Exception as e:
        current_app.logger.error(f"Ошибка в get_module_stats: {str(e)}", exc_info=True)
        return {
            "progress": 0,
            "completed_lessons": 0,
            "total_lessons": 0
        }

def get_user_stats(user_id):
    """Получает статистику обучения пользователя"""
    try:
        # Общее количество завершенных уроков
        completed_lessons_count = UserProgress.query.filter_by(
            user_id=user_id,
            completed=True
        ).count()
        
        # Общее количество уроков
        total_lessons_count = Lesson.query.count()
        
        # Расчет общего прогресса
        overall_progress = round((completed_lessons_count / total_lessons_count) * 100) if total_lessons_count > 0 else 0
        
        # Общее время обучения (в минутах)
        total_time_spent = db.session.query(
            func.sum(UserProgress.time_spent)
        ).filter_by(
            user_id=user_id
        ).scalar() or 0
        
        # Количество дней активности
        active_days_count = db.session.query(
            func.count(func.distinct(func.date(UserProgress.last_accessed)))
        ).filter_by(
            user_id=user_id
        ).scalar() or 0
        
        # Получаем дату последнего экзамена, если есть
        next_exam_date = None
        try:
            # Вы можете адаптировать эту логику под свою структуру данных
            if hasattr(current_user, 'exam_dates') and current_user.exam_dates:
                next_exam = db.session.query(UserExamDate).filter(
                    UserExamDate.user_id == user_id,
                    UserExamDate.exam_date > datetime.utcnow()
                ).order_by(UserExamDate.exam_date).first()
                
                if next_exam:
                    next_exam_date = next_exam.exam_date.strftime('%d.%m.%Y')
        except Exception as e:
            print(f"Error getting exam date: {e}")
        
        # Статистика по путям обучения
        learning_paths_stats = []
        for path in LearningPath.query.all():
            # Получаем все уроки для данного пути обучения через JOIN
            path_lessons = db.session.query(Lesson.id).join(
                Module, Module.id == Lesson.module_id
            ).join(
                Subject, Subject.id == Module.subject_id
            ).filter(
                Subject.learning_path_id == path.id
            ).all()
            
            # Преобразуем результат в список ID уроков
            path_lesson_ids = [lesson[0] for lesson in path_lessons]
            path_total_lessons = len(path_lesson_ids)
            
            # Количество завершенных уроков для этого пути
            path_completed_lessons = UserProgress.query.filter(
                UserProgress.user_id == user_id,
                UserProgress.lesson_id.in_(path_lesson_ids),
                UserProgress.completed == True
            ).count() if path_lesson_ids else 0
            
            # Расчет прогресса для данного пути
            path_progress = round((path_completed_lessons / path_total_lessons) * 100) if path_total_lessons > 0 else 0
            
            learning_paths_stats.append({
                'id': path.id,
                'name': path.name,
                'progress': path_progress,
                'completed_lessons': path_completed_lessons,
                'total_lessons': path_total_lessons
            })
        
        return {
            'overall_progress': overall_progress,
            'completed_lessons': completed_lessons_count,
            'total_lessons': total_lessons_count,
            'total_time_spent': round(float(total_time_spent), 1),
            'active_days': active_days_count,
            'next_exam_date': next_exam_date,
            'learning_paths': learning_paths_stats
        }
    except Exception as e:
        current_app.logger.error(f"Ошибка в get_user_stats: {str(e)}", exc_info=True)
        return {
            'overall_progress': 0,
            'completed_lessons': 0,
            'total_lessons': 0,
            'total_time_spent': 0,
            'active_days': 0,
            'next_exam_date': None,
            'learning_paths': []
        }
def get_virtual_patients_stats(user_id):
    """Получает статистику виртуальных пациентов для пользователя"""
    try:
        # Общее количество сценариев
        total_scenarios = VirtualPatientScenario.query.filter_by(is_published=True).count()
        
        # Завершенные сценарии
        completed_scenarios = db.session.query(VirtualPatientAttempt.scenario_id).filter_by(
            user_id=user_id,
            completed=True
        ).distinct().count()
        
        # Средний балл
        avg_score_data = db.session.query(
            db.func.avg(VirtualPatientAttempt.score).label('avg_score'),
            db.func.avg(VirtualPatientScenario.max_score).label('avg_max_score')
        ).join(
            VirtualPatientScenario,
            VirtualPatientAttempt.scenario_id == VirtualPatientScenario.id
        ).filter(
            VirtualPatientAttempt.user_id == user_id,
            VirtualPatientAttempt.completed == True
        ).first()
        
        avg_percentage = 0
        if avg_score_data and avg_score_data.avg_score and avg_score_data.avg_max_score:
            avg_percentage = round((avg_score_data.avg_score / avg_score_data.avg_max_score) * 100)
        
        return {
            'total': total_scenarios,
            'completed': completed_scenarios,
            'percentage': round((completed_scenarios / total_scenarios * 100) if total_scenarios > 0 else 0),
            'avg_score': avg_percentage
        }
    except Exception as e:
        current_app.logger.error(f"Error getting virtual patients stats: {e}")
        return {
            'total': 0,
            'completed': 0,
            'percentage': 0,
            'avg_score': 0
        }

# Добавляем отладочный маршрут для быстрого добавления тестового прогресса
@learning_map_bp.route("/debug/add-progress")
@login_required
def debug_add_progress(lang):
    """Временный маршрут для добавления тестового прогресса"""
    try:
        # Получаем несколько уроков для тестирования
        lessons = Lesson.query.limit(5).all()
        
        if not lessons:
            flash("Уроки не найдены в базе данных", "warning")
            return redirect(url_for('learning_map_bp.learning_map', lang=lang))
            
        added_count = 0
        lesson_info = []
        
        for lesson in lessons:
            # Проверяем, есть ли уже запись прогресса
            progress = UserProgress.query.filter_by(
                user_id=current_user.id,
                lesson_id=lesson.id
            ).first()
            
            status = 'existing'
            
            if not progress:
                # Создаем новую запись
                progress = UserProgress(
                    user_id=current_user.id,
                    lesson_id=lesson.id,
                    completed=True,
                    time_spent=10.0  # Тестовое значение времени
                )
                db.session.add(progress)
                added_count += 1
                status = 'created'
            elif not progress.completed:
                # Обновляем существующую запись
                progress.completed = True
                progress.time_spent = (progress.time_spent or 0.0) + 10.0
                added_count += 1
                status = 'updated'
                
            # Собираем информацию об уроке для отладки
            module = Module.query.get(lesson.module_id)
            lesson_info.append({
                'id': lesson.id,
                'title': lesson.title,
                'module_id': lesson.module_id,
                'module_title': module.title if module else 'Unknown',
                'status': status
            })
                
        # Сохраняем изменения в базе данных
        db.session.commit()
        
        # Получаем обновленную статистику пользователя
        stats = get_user_stats(current_user.id)
        
        # Отображаем подробную страницу с информацией о прогрессе
        return render_template(
            "debug_progress.html",
            stats=stats,
            lessons=lesson_info,
            added_count=added_count
        )
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Ошибка при добавлении тестового прогресса: {str(e)}", exc_info=True)
        flash(f"❌ Ошибка при добавлении тестового прогресса: {str(e)}", "danger")
        return redirect(url_for('learning_map_bp.learning_map', lang=lang))
    
    
@learning_map_bp.route("/debug/progress-status")
@login_required
def debug_progress_status(lang):
    """Отладочный маршрут для отображения текущего состояния прогресса"""
    try:
        # Получаем все записи прогресса для текущего пользователя
        progress_entries = UserProgress.query.filter_by(
            user_id=current_user.id
        ).all()
        
        # Группируем по статусу
        completed_entries = [p for p in progress_entries if p.completed]
        incomplete_entries = [p for p in progress_entries if not p.completed]
        
        # Получаем статистику
        stats = get_user_stats(current_user.id)
        
        # Подробная информация о прогрессе уроков
        lessons_progress = []
        for entry in progress_entries:
            lesson = Lesson.query.get(entry.lesson_id)
            if lesson:
                module = Module.query.get(lesson.module_id)
                lessons_progress.append({
                    'id': lesson.id,
                    'title': lesson.title,
                    'module_id': lesson.module_id,
                    'module_title': module.title if module else 'Unknown',
                    'completed': entry.completed,
                    'time_spent': entry.time_spent,
                    'last_accessed': entry.last_accessed
                })
        
        # Статистика модулей
        modules_stats = []
        for module in Module.query.all():
            module_stats = get_module_stats(module.id, current_user.id)
            modules_stats.append({
                'id': module.id,
                'title': module.title,
                'progress': module_stats['progress'],
                'completed_lessons': module_stats['completed_lessons'],
                'total_lessons': module_stats['total_lessons']
            })
        
        # Сортируем модули по прогрессу (от наибольшего к наименьшему)
        modules_stats.sort(key=lambda x: x['progress'], reverse=True)
        
        # Сортируем уроки по времени доступа (последние сверху)
        lessons_progress.sort(key=lambda x: x['last_accessed'] if x.get('last_accessed') else datetime.min, reverse=True)
        
        return render_template(
            "debug_progress_status.html",
            stats=stats,
            lessons_progress=lessons_progress,
            modules_stats=modules_stats,
            completed_count=len(completed_entries),
            incomplete_count=len(incomplete_entries),
            total_count=len(progress_entries)
        )
        
    except Exception as e:
        current_app.logger.error(f"Ошибка при получении статистики прогресса: {str(e)}", exc_info=True)
        flash(f"❌ Ошибка при получении статистики прогресса: {str(e)}", "danger")
        return redirect(url_for('learning_map_bp.learning_map', lang=lang))
    
@learning_map_bp.route('/api/path/<int:path_id>/subjects')
def get_path_subjects(path_id):
    # Получаем язык из g, установленный в middleware
    lang = g.lang
    
    # Получаем путь по ID
    path = LearningPath.query.get_or_404(path_id)
    
    # Получаем предметы этого пути
    subjects = Subject.query.filter_by(learning_path_id=path_id).all()
    
    # Формируем ответ в JSON
    subjects_data = []
    for subject in subjects:
        # Вычисляем прогресс для данного пользователя
        progress = 0
        if current_user.is_authenticated:
            # Получаем прогресс предмета (адаптируйте этот код согласно вашей системе)
            # Пример расчета прогресса (замените на свою логику):
            lessons_complete = UserProgress.query.join(Lesson).join(Module).filter(
                UserProgress.user_id == current_user.id,
                UserProgress.completed == True,
                Module.subject_id == subject.id
            ).count()
            
            # Общее количество уроков в предмете
            total_lessons = Lesson.query.join(Module).filter(
                Module.subject_id == subject.id
            ).count()
            
            if total_lessons > 0:
                progress = round((lessons_complete / total_lessons) * 100)
        
        subjects_data.append({
            'id': subject.id,
            'name': subject.name,
            'description': subject.description,
            'progress': progress
        })
    
    return jsonify({
        'path_id': path_id,
        'path_name': path.name,
        'path_description': path.description,
        'subjects': subjects_data,
        'learning_map_text': t('learning_map', lang)
    })

@learning_map_bp.route('/path/<int:path_id>')
@login_required  # Добавляем декоратор для авторизации
def view_path(lang, path_id):
    """Отображает предметы выбранного учебного пути."""
    try:
        # Получаем путь по ID
        path = LearningPath.query.get_or_404(path_id)
        
        # Логирование вместо print
        current_app.logger.info(f"Запрошен путь ID: {path_id}, название: {path.name}")
        
        # Получаем предметы этого пути
        path_subjects = Subject.query.filter_by(learning_path_id=path_id).all()
        
        # Логирование информации о предметах
        current_app.logger.info(f"Найдено предметов: {len(path_subjects)}")
        for subject in path_subjects:
            current_app.logger.info(f"  - Предмет: {subject.id}, {subject.name}")
        
        # Получаем все пути (для левой колонки)
        learning_paths = LearningPath.query.order_by(LearningPath.order).all()
        
        # Получаем все предметы (с сортировкой для предсказуемости)
        subjects = Subject.query.order_by(Subject.name).all()
        
        # Получаем категории контента
        content_categories = ContentCategory.query.order_by(ContentCategory.order).all()
        
        # Получаем статистику пользователя
        stats = get_user_stats(current_user.id)
        
        # Получаем рекомендации
        recommendations = get_user_recommendations(current_user.id)
        
        # Добавляем скрипт для активации категории
        extra_scripts = """
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Активируем выбранную категорию
            const pathId = "%s";
            
            // Активируем соответствующую кнопку в левом меню
            const pathButton = document.querySelector(`.learning-path-button[data-path="${pathId}"]`);
            if (pathButton) {
                // Программно нажимаем на кнопку
                pathButton.click();
            }
            
            // Активируем кнопку в мобильном меню
            const mobileButton = document.querySelector(`.mobile-nav-item[data-path="${pathId}"]`);
            if (mobileButton) {
                mobileButton.classList.add('active');
            }
        });
        </script>
        """ % path_id
        
        return render_template(
            'learning/subject_view.html',
            learning_paths=learning_paths,
            subjects=subjects,
            selected_path=path,
            selected_subject=None,
            subject_modules=None,
            stats=stats,
            recommendations=recommendations,
            content_categories=content_categories,
            lang=lang,
            extra_scripts=extra_scripts  # Передаем скрипт в шаблон
        )
    except Exception as e:
        current_app.logger.error(f"Ошибка при отображении пути {path_id}: {str(e)}", exc_info=True)
        flash(f"Ошибка при загрузке данных: {str(e)}", "danger")
        return redirect(url_for('learning_map_bp.learning_map', lang=lang))
    
