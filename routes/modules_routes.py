# routes/modules_routes.py
from flask import Blueprint, render_template, redirect, url_for, g, flash, current_app, request
from flask_login import login_required, current_user
from models import db, Module, Lesson, UserProgress
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
    lang = getattr(g, 'lang', current_app.config['DEFAULT_LANGUAGE'])
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
        
        # Получаем все модули для левого столбца (группируем по предмету если есть)
        if hasattr(module, 'subject_id') and module.subject_id:
            # Получаем модули того же предмета
            all_modules = Module.query.filter_by(subject_id=module.subject_id).order_by(Module.order).all()
        else:
            # Если нет subject_id, получаем все модули
            all_modules = Module.query.order_by(Module.title).all()
        
        # Добавляем прогресс для каждого модуля
        modules_with_progress = []
        for mod in all_modules:
            # Получаем все уроки модуля
            module_lessons = Lesson.query.filter_by(module_id=mod.id).all()
            total_lessons = len(module_lessons)
            
            # Получаем завершенные уроки
            completed_lessons = 0
            if total_lessons > 0:
                lesson_ids = [lesson.id for lesson in module_lessons]
                completed_lessons = UserProgress.query.filter_by(
                    user_id=current_user.id,
                    completed=True
                ).filter(UserProgress.lesson_id.in_(lesson_ids)).count()
            
            # Вычисляем прогресс
            progress = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
            
            modules_with_progress.append({
                'module': mod,
                'progress': progress,
                'completed_lessons': completed_lessons,
                'total_lessons': total_lessons,
                'is_current': mod.id == module_id
            })
        
        # Получаем все уроки модуля
        lessons = Lesson.query.filter_by(module_id=module.id).order_by(Lesson.order).all()
        current_app.logger.info(f"Module '{module.title}' has {len(lessons)} lessons")
        
        # Сначала проверяем наличие полей subtopic в уроках
        has_subtopic_fields = False
        for lesson in lessons:
            if lesson.subtopic and lesson.subtopic_slug:
                has_subtopic_fields = True
                break
        
        # Группируем уроки по подтемам
        subtopics = defaultdict(list)
        
        for lesson in lessons:
            subtopic_name = None
            subtopic_slug = None
            
            # Если поля subtopic и subtopic_slug заполнены, используем их
            if has_subtopic_fields and lesson.subtopic and lesson.subtopic_slug:
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
            
            # Добавляем ключ slug к хранимым данным
            lesson_with_slug = {
                'lesson': lesson,
                'slug': subtopic_slug
            }
            subtopics[subtopic_name].append(lesson_with_slug)
        
        # Преобразуем в формат для шаблона
        topics_with_subtopics = []
        for subtopic_name, subtopic_lessons in subtopics.items():
            # Получаем слаг из первого урока
            subtopic_slug = subtopic_lessons[0]['slug']
            
            # Выделяем объекты уроков для подсчета прогресса
            lessons_only = [item['lesson'] for item in subtopic_lessons]
            
            # Подсчитываем прогресс
            completed_lessons = 0
            for lesson in lessons_only:
                progress = UserProgress.query.filter_by(
                    user_id=current_user.id,
                    lesson_id=lesson.id
                ).first()
                if progress and progress.completed:
                    completed_lessons += 1
            
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
        
        # Сортируем подтемы
        topics_with_subtopics.sort(key=lambda x: x['topic']['name'])
        
        current_app.logger.info(f"Grouped into {len(topics_with_subtopics)} subtopics: {[t['topic']['name'] for t in topics_with_subtopics]}")
        
        return render_template(
            "learning/module.html",
            module=module,
            modules_with_progress=modules_with_progress,  # Новый параметр для левого столбца
            topics_with_subtopics=topics_with_subtopics,
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
    """Отображает список уроков для конкретной подтемы с интерактивными элементами."""
    try:
        module = Module.query.get_or_404(module_id)
        
        # Получаем все модули для левого столбца (группируем по предмету если есть)
        if hasattr(module, 'subject_id') and module.subject_id:
            # Получаем модули того же предмета
            all_modules = Module.query.filter_by(subject_id=module.subject_id).order_by(Module.order).all()
        else:
            # Если нет subject_id, получаем все модули
            all_modules = Module.query.order_by(Module.title).all()
        
        # Добавляем прогресс для каждого модуля
        modules_with_progress = []
        for mod in all_modules:
            # Получаем все уроки модуля
            module_lessons = Lesson.query.filter_by(module_id=mod.id).all()
            total_lessons = len(module_lessons)
            
            # Получаем завершенные уроки
            completed_lessons = 0
            if total_lessons > 0:
                lesson_ids = [lesson.id for lesson in module_lessons]
                completed_lessons = UserProgress.query.filter_by(
                    user_id=current_user.id,
                    completed=True
                ).filter(UserProgress.lesson_id.in_(lesson_ids)).count()
            
            # Вычисляем прогресс
            progress = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
            
            modules_with_progress.append({
                'module': mod,
                'progress': progress,
                'completed_lessons': completed_lessons,
                'total_lessons': total_lessons,
                'is_current': mod.id == module_id
            })
        
        # Получаем уроки подтемы
        subtopic_lessons = Lesson.query.filter_by(
            module_id=module_id,
            subtopic_slug=slug
        ).order_by(Lesson.subtopic_order, Lesson.order).all()
        
        if not subtopic_lessons:
            # Если уроки не найдены по subtopic_slug, попробуем найти по извлеченному module_title
            all_lessons = Lesson.query.filter_by(module_id=module_id).order_by(Lesson.order).all()
            subtopic_lessons = []
            
            for lesson in all_lessons:
                extracted_title = extract_module_title(lesson)
                if extracted_title and create_slug(extracted_title) == slug:
                    subtopic_lessons.append(lesson)
            
            if not subtopic_lessons:
                flash("Подтема не найдена" if lang == 'ru' else "Subtopic not found", "danger")
                return redirect(url_for('modules_bp.module_view', lang=lang, module_id=module.id))
        
        # Название подтемы
        subtopic_name = subtopic_lessons[0].subtopic if subtopic_lessons[0].subtopic else "Подтема"
        
        # Подготовка карточек и тестов для интерактивного отображения
        cards = []
        tests = []
        
        for lesson in subtopic_lessons:
            if lesson.content_type == 'learning_card' and lesson.content:
                try:
                    content_data = json.loads(lesson.content)
                    if 'cards' in content_data:
                        for card in content_data['cards']:
                            cards.append({
                                'question': card.get('question', ''),
                                'answer': card.get('answer', ''),
                                'lesson_id': lesson.id
                            })
                except (json.JSONDecodeError, KeyError, AttributeError) as e:
                    current_app.logger.error(f"Error parsing card content: {e}")
                    
            elif lesson.content_type in ['quiz', 'test_question'] and lesson.content:
                try:
                    content_data = json.loads(lesson.content)
                    if 'questions' in content_data:
                        for question in content_data['questions']:
                            tests.append({
                                'question': question.get('question', ''),
                                'options': question.get('options', []),
                                'correct_answer': question.get('correct_answer', 0),
                                'explanation': question.get('explanation', ''),
                                'lesson_id': lesson.id
                            })
                except (json.JSONDecodeError, KeyError, AttributeError) as e:
                    current_app.logger.error(f"Error parsing test content: {e}")
        
        # Чередуем карточки и тесты (2 карточки, 1 тест)
        interleaved_content = []
        card_index = 0
        test_index = 0
        
        # Чередование контента
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
        
        # Получаем прогресс пользователя для уроков
        user_progress = {}
        for lesson in subtopic_lessons:
            progress = UserProgress.query.filter_by(
                user_id=current_user.id,
                lesson_id=lesson.id
            ).first()
            user_progress[lesson.id] = progress.completed if progress else False
        
        current_app.logger.info(f"Prepared {len(interleaved_content)} items for display")
        
        # Используем специальный шаблон для интерактивного отображения
        return render_template(
            "learning/interactive_subtopic.html",
            module=module,
            modules_with_progress=modules_with_progress,  # Новый параметр
            subtopic_name=subtopic_name,
            subtopic_slug=slug,  # Добавляем slug для навигации
            content=interleaved_content,
            lessons=subtopic_lessons,
            user_progress=user_progress,
            total_items=len(interleaved_content),
            lang=lang
        )
    except Exception as e:
        current_app.logger.error(f"Error in subtopic_lessons_list: {e}", exc_info=True)
        flash(f"Error loading subtopic: {e}", "danger")
        return redirect(url_for('modules_bp.module_view', lang=lang, module_id=module.id))