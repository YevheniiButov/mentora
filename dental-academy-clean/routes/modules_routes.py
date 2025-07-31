# routes/modules_routes.py
from flask import Blueprint, render_template, redirect, url_for, g, flash, current_app, request
from flask_login import login_required, current_user
from models import db, Module, Lesson, UserProgress, Subject
from utils.unified_stats import get_unified_user_stats, get_module_stats_unified
import json
from collections import defaultdict
import logging

# Создаем Blueprint
modules_bp = Blueprint(
    "modules_bp",
    __name__,
    url_prefix='/<string:lang>/modules',
    template_folder='../templates'
)

@modules_bp.context_processor
def inject_lang_modules():
    current_lang = g.lang
    lang = getattr(g, 'lang', current_app.config.get('DEFAULT_LANGUAGE', 'nl'))
    return dict(lang=lang)

def create_slug(text):
    """Создаёт унифицированный слаг из текста"""
    if not text:
        return ""
    # Заменяем пробелы, дефисы, слеши и другие символы на подчеркивания
    import re
    return re.sub(r'[^a-z0-9]+', '_', text.lower()).strip('_')

def extract_module_title(lesson):
    """Извлекает module_title из различных форматов контента урока"""
    if not lesson.content:
        return None
    
    try:
        content_data = json.loads(lesson.content)
        
        # Прямой доступ (верхний уровень)
        if 'module_title' in content_data:
            return content_data.get('module_title')
            
        # Если контент - это карточка или тест
        if content_data.get('type') in ['learning', 'test']:
            return content_data.get('module_title')
            
        # Если контент содержит массив cards
        if 'cards' in content_data and content_data['cards']:
            return content_data['cards'][0].get('module_title')
            
        # Если контент содержит массив questions
        if 'questions' in content_data and content_data['questions']:
            return content_data['questions'][0].get('module_title')
            
    except (json.JSONDecodeError, AttributeError, KeyError, TypeError) as e:
        current_app.logger.warning(f"Error extracting module_title for lesson {lesson.id}: {e}")
        
    return None

@modules_bp.route("/")
@login_required
def modules_list(lang):
    """Отображает список доступных модулей обучения."""
    user = current_user
    categorized_modules = {}
    
    try:
        modules = Module.query.all()
        for module in modules:
            category = getattr(module, 'module_type', 'misc')
            if category not in categorized_modules:
                categorized_modules[category] = []
            
            # Получаем уроки из БД
            lessons = Lesson.query.filter_by(module_id=module.id).all()
            total_lessons = len(lessons)
            
            # Получаем завершенные уроки
            completed_lessons = UserProgress.query.filter_by(
                user_id=user.id,
                completed=True
            ).filter(UserProgress.lesson_id.in_([l.id for l in lessons])).count()
            
            module_data = {
                'id': module.id,
                'title': module.title,
                'description': getattr(module, 'description', ''),
                'is_premium': getattr(module, 'is_premium', False),
                'icon': getattr(module, 'icon', 'book'),
                'total_lessons': total_lessons,
                'completed_lessons': completed_lessons
            }
            
            categorized_modules[category].append(module_data)
    except Exception as e:
        current_app.logger.error(f"Error fetching modules: {e}", exc_info=True)
        flash("Failed to load modules list.", "danger")
        categorized_modules = {}
    
    return render_template('learning/modules_list.html', 
                           categories=categorized_modules, 
                           user=user)

@modules_bp.route("/<int:module_id>")
@login_required
def module_view(lang, module_id):
    """Отображает содержимое модуля с группировкой по подтемам."""
    try:
        module = Module.query.get_or_404(module_id)
        
        # Получаем текущий Subject
        current_subject = Subject.query.get(module.subject_id) if module.subject_id else None
        
        # Получаем все Subject'ы для левой колонки
        all_subjects = Subject.query.all()
        
        # Добавляем модули и прогресс для каждого Subject
        subjects_with_data = []
        for subject in all_subjects:
            # Получаем модули Subject'а
            subject_modules = Module.query.filter_by(subject_id=subject.id).all()
            
            # Вычисляем прогресс Subject'а
            total_lessons = 0
            completed_lessons = 0
            
            for mod in subject_modules:
                module_lessons = Lesson.query.filter_by(module_id=mod.id).all()
                total_lessons += len(module_lessons)
                
                if module_lessons:
                    lesson_ids = [lesson.id for lesson in module_lessons]
                    completed_lessons += UserProgress.query.filter_by(
                        user_id=current_user.id,
                        completed=True
                    ).filter(UserProgress.lesson_id.in_(lesson_ids)).count()
            
            # Вычисляем прогресс в процентах
            progress = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
            
            # Добавляем вычисленные данные
            subject.modules = subject_modules  # Добавляем модули к объекту subject
            subject.progress = progress
            subject.total_lessons = total_lessons
            subject.completed_lessons = completed_lessons
            
            subjects_with_data.append(subject)
        
        # Получаем все уроки модуля
        lessons = Lesson.query.filter_by(module_id=module.id).order_by(Lesson.order).all()
        current_app.logger.info(f"Module '{module.title}' has {len(lessons)} lessons")
        
        # Группируем уроки по подтемам (существующая логика)
        subtopics = defaultdict(list)
        
        for lesson in lessons:
            subtopic_name = None
            subtopic_slug = None
            
            # Если поля subtopic и subtopic_slug заполнены, используем их
            if lesson.subtopic and lesson.subtopic_slug:
                subtopic_name = lesson.subtopic
                subtopic_slug = lesson.subtopic_slug
            else:
                # Иначе извлекаем из контента
                extracted_module_title = extract_module_title(lesson)
                
                if extracted_module_title:
                    subtopic_name = extracted_module_title
                    subtopic_slug = create_slug(extracted_module_title)
                else:
                    # Fallback: используем тип контента
                    if lesson.content_type == 'learning_card':
                        subtopic_name = f"{module.title} - Обучающие материалы"
                    elif lesson.content_type in ['quiz', 'test_question']:
                        subtopic_name = f"{module.title} - Тесты"
                    else:
                        subtopic_name = f"{module.title} - Общие материалы"
                    subtopic_slug = create_slug(subtopic_name)
            
            lesson_with_slug = {
                'lesson': lesson,
                'slug': subtopic_slug
            }
            subtopics[subtopic_name].append(lesson_with_slug)
        
        # Преобразуем в формат для шаблона
        topics_with_subtopics = []
        
        # Получаем все уроки для всех подтем за один запрос
        all_lessons_for_progress = []
        for subtopic_lessons in subtopics.values():
            all_lessons_for_progress.extend([item['lesson'] for item in subtopic_lessons])
        
        # Получаем весь прогресс пользователя за один запрос
        lesson_ids = [lesson.id for lesson in all_lessons_for_progress]
        progress_dict = {}
        
        if lesson_ids:
            progress_entries = UserProgress.query.filter(
                UserProgress.user_id == current_user.id,
                UserProgress.lesson_id.in_(lesson_ids)
            ).all()
            progress_dict = {entry.lesson_id: entry.completed for entry in progress_entries}
        
        for subtopic_name, subtopic_lessons in subtopics.items():
            subtopic_slug = subtopic_lessons[0]['slug']
            lessons_only = [item['lesson'] for item in subtopic_lessons]
            
            # Подсчитываем прогресс (оптимизированная версия)
            completed_lessons = sum(1 for lesson in lessons_only if progress_dict.get(lesson.id, False))
            
            topic_data = {
                'topic': {
                    'name': subtopic_name,
                    'description': f"Подтема: {subtopic_name}",
                    'slug': subtopic_slug
                },
                'lessons': lessons_only,
                'total_lessons': len(lessons_only),
                'completed_lessons': completed_lessons,
                'progress_percent': int((completed_lessons / len(lessons_only)) * 100) if lessons_only else 0
            }
            topics_with_subtopics.append(topic_data)
        
        # Сортируем подтемы по номеру модуля из card_id первой карточки
        def get_module_order(topic_data):
            try:
                first_lesson = topic_data['lessons'][0] if topic_data['lessons'] else None
                if not first_lesson or not first_lesson.content:
                    return 999
                
                content_data = json.loads(first_lesson.content)
                if 'cards' in content_data and content_data['cards']:
                    first_card = content_data['cards'][0]
                    card_id = first_card.get('card_id', '')
                    
                    import re
                    match = re.search(r'_m(\d+)_', card_id)
                    if match:
                        return int(match.group(1))
                
                return 999
            except (json.JSONDecodeError, KeyError, ValueError, IndexError):
                return 999
        
        topics_with_subtopics.sort(key=get_module_order)
        
        current_app.logger.info(f"Grouped into {len(topics_with_subtopics)} subtopics: {[t['topic']['name'] for t in topics_with_subtopics]}")
        
        # Получаем статистику пользователя через унифицированную систему
        stats = get_unified_user_stats(current_user.id)
        
        # Получаем рекомендации (добавляем этот импорт если его нет) 
        from routes.subject_view_routes import get_user_recommendations
        recommendations = get_user_recommendations(current_user.id)
        
        # Получаем все модули с прогрессом для левой колонки (оптимизированная версия)
        all_modules = Module.query.filter_by(subject_id=module.subject_id).order_by(Module.order).all()
        modules_with_progress = []
        
        if all_modules:
            # Получаем все уроки для всех модулей за один запрос
            module_ids = [mod.id for mod in all_modules]
            all_lessons = Lesson.query.filter(Lesson.module_id.in_(module_ids)).all()
            
            # Группируем уроки по модулям
            lessons_by_module = {}
            for lesson in all_lessons:
                if lesson.module_id not in lessons_by_module:
                    lessons_by_module[lesson.module_id] = []
                lessons_by_module[lesson.module_id].append(lesson)
            
            # Получаем весь прогресс пользователя за один запрос
            all_lesson_ids = [lesson.id for lesson in all_lessons]
            completed_progress = UserProgress.query.filter(
                UserProgress.user_id == current_user.id,
                UserProgress.lesson_id.in_(all_lesson_ids),
                UserProgress.completed == True
            ).with_entities(UserProgress.lesson_id).all()
            
            completed_lesson_ids = {entry.lesson_id for entry in completed_progress}
            
            # Рассчитываем прогресс для каждого модуля
            for mod in all_modules:
                module_lessons = lessons_by_module.get(mod.id, [])
                total_lessons = len(module_lessons)
                
                if total_lessons > 0:
                    module_lesson_ids = {lesson.id for lesson in module_lessons}
                    completed_lessons = len(module_lesson_ids.intersection(completed_lesson_ids))
                    progress = int((completed_lessons / total_lessons) * 100)
                else:
                    completed_lessons = 0
                    progress = 0
                
                modules_with_progress.append({
                    'module': mod,
                    'progress': progress,
                    'completed_lessons': completed_lessons,
                    'total_lessons': total_lessons,
                    'is_current': mod.id == module.id
                })
        else:
            modules_with_progress = []

        return render_template(
            "learning/module.html",
            module=module,
            current_subject=current_subject,
            subjects=subjects_with_data,  # Передаем subjects с данными
            modules_with_progress=modules_with_progress,  # Добавляем модули с прогрессом
            topics_with_subtopics=topics_with_subtopics,
            stats=stats,  # Добавляем статистику
            recommendations=recommendations,  # Добавляем рекомендации
            title=module.title,
            lang=lang
        )
    except Exception as e:
        current_app.logger.error(f"Error loading module {module_id}: {e}", exc_info=True)
        flash(f"Error loading module: {e}", "danger")
        return redirect(url_for('modules_bp.modules_list', lang=lang))
@modules_bp.route("/<int:module_id>/subtopic/<slug>")
@login_required
def subtopic_lessons_list(lang, module_id, slug):
    """Интерактивное обучение по подтеме с унифицированным дизайном."""
    try:
        module = Module.query.get_or_404(module_id)
        
        # Получаем уроки подтемы
        subtopic_lessons = Lesson.query.filter_by(
            module_id=module_id,
            subtopic_slug=slug
        ).order_by(Lesson.subtopic_order, Lesson.order).all()

        if not subtopic_lessons:
            flash("Subtopic not found", "error")
            return redirect(url_for('modules_bp.module_view', lang=lang, module_id=module_id))

        subtopic_name = subtopic_lessons[0].subtopic if subtopic_lessons else "Unknown Subtopic"

        # Парсим контент и разделяем карточки и тесты
        cards = []
        tests = []

        for lesson in subtopic_lessons:
            try:
                if lesson.content:
                    content_data = json.loads(lesson.content)
                    
                    if lesson.content_type == 'learning_card' and 'cards' in content_data:
                        for card in content_data['cards']:
                            cards.append({
                                'question': card.get('question', ''),
                                'answer': card.get('answer', ''),
                                'card_id': card.get('card_id', ''),
                                'lesson_id': lesson.id
                            })
                    
                    elif lesson.content_type in ['quiz', 'test_question'] and 'questions' in content_data:
                        for question in content_data['questions']:
                            tests.append({
                                'question': question.get('question', ''),
                                'options': question.get('options', []),
                                'correct_answer': question.get('correct_answer', 0),
                                'explanation': question.get('explanation', ''),
                                'card_id': question.get('card_id', ''),
                                'lesson_id': lesson.id
                            })
            except (json.JSONDecodeError, KeyError) as e:
                current_app.logger.warning(f"Error parsing lesson {lesson.id}: {e}")
                continue

        # Чередуем контент: 2 карточки → 1 тест
        interleaved_content = []
        card_index = 0
        test_index = 0

        while card_index < len(cards) or test_index < len(tests):
            # Добавляем до 2 карточек
            for _ in range(2):
                if card_index < len(cards):
                    interleaved_content.append({
                        'type': 'card',
                        'data': cards[card_index]
                    })
                    card_index += 1

            # Добавляем 1 тест
            if test_index < len(tests):
                interleaved_content.append({
                    'type': 'test',
                    'data': tests[test_index]
                })
                test_index += 1

        # Получаем все модули с прогрессом для левой колонки (оптимизированная версия)
        all_modules = Module.query.filter_by(subject_id=module.subject_id).order_by(Module.order).all()
        modules_with_progress = []
        
        if all_modules:
            # Получаем все уроки для всех модулей за один запрос
            module_ids = [mod.id for mod in all_modules]
            all_lessons = Lesson.query.filter(Lesson.module_id.in_(module_ids)).all()
            
            # Группируем уроки по модулям
            lessons_by_module = {}
            for lesson in all_lessons:
                if lesson.module_id not in lessons_by_module:
                    lessons_by_module[lesson.module_id] = []
                lessons_by_module[lesson.module_id].append(lesson)
            
            # Получаем весь прогресс пользователя за один запрос
            all_lesson_ids = [lesson.id for lesson in all_lessons]
            completed_progress = UserProgress.query.filter(
                UserProgress.user_id == current_user.id,
                UserProgress.lesson_id.in_(all_lesson_ids),
                UserProgress.completed == True
            ).with_entities(UserProgress.lesson_id).all()
            
            completed_lesson_ids = {entry.lesson_id for entry in completed_progress}
            
            # Рассчитываем прогресс для каждого модуля
            for mod in all_modules:
                module_lessons = lessons_by_module.get(mod.id, [])
                total_lessons = len(module_lessons)
                
                if total_lessons > 0:
                    module_lesson_ids = {lesson.id for lesson in module_lessons}
                    completed_lessons = len(module_lesson_ids.intersection(completed_lesson_ids))
                    progress = int((completed_lessons / total_lessons) * 100)
                else:
                    completed_lessons = 0
                    progress = 0
                
                modules_with_progress.append({
                    'module': mod,
                    'progress': progress,
                    'completed_lessons': completed_lessons,
                    'total_lessons': total_lessons,
                    'is_current': mod.id == module.id
                })
        else:
            modules_with_progress = []

        # Получаем прогресс пользователя для уроков подтемы (оптимизированная версия)
        lesson_ids = [lesson.id for lesson in subtopic_lessons]
        user_progress = {}
        
        if lesson_ids:
            # Получаем весь прогресс за один запрос
            progress_entries = UserProgress.query.filter(
                UserProgress.user_id == current_user.id,
                UserProgress.lesson_id.in_(lesson_ids)
            ).all()
            
            # Создаем словарь для быстрого доступа
            progress_dict = {entry.lesson_id: entry.completed for entry in progress_entries}
            
            # Заполняем user_progress
            for lesson in subtopic_lessons:
                user_progress[lesson.id] = progress_dict.get(lesson.id, False)
        else:
            # Если нет уроков, создаем пустой словарь
            user_progress = {}

        current_app.logger.info(f"Subtopic '{subtopic_name}' loaded with {len(interleaved_content)} items")

        return render_template(
            "learning/interactive_subtopic.html",
            module=module,
            subtopic_name=subtopic_name,
            content=interleaved_content,
            total_items=len(interleaved_content),
            modules_with_progress=modules_with_progress,
            user_progress=user_progress,
            current_item=1,  # Для прогресса
            lang=lang
        )

    except Exception as e:
        current_app.logger.error(f"Error in subtopic_lessons_list: {e}", exc_info=True)
        flash("Error loading subtopic content", "error")
        return redirect(url_for('modules_bp.module_view', lang=lang, module_id=module_id))