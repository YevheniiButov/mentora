# routes/lesson_routes.py - Lesson routes

from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, g
from flask_login import login_required, current_user
from models import Module, Lesson, UserProgress
from extensions import db
import json
from datetime import datetime, timezone

lesson_bp = Blueprint('lesson', __name__)

# Функции для работы с прогрессом
def track_lesson_progress(user_id, lesson_id):
    """Отслеживает прогресс урока"""
    try:
        progress = UserProgress.query.filter_by(
            user_id=user_id,
            lesson_id=lesson_id
        ).first()
        
        if not progress:
            progress = UserProgress(
                user_id=user_id,
                lesson_id=lesson_id,
                viewed=True,
                viewed_at=datetime.now(timezone.utc)
            )
            db.session.add(progress)
        else:
            progress.viewed = True
            progress.viewed_at = datetime.now(timezone.utc)
        
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error tracking lesson progress: {e}")
        db.session.rollback()

def update_lesson_progress(user_id, lesson_id, viewed=False, completed=False):
    """Обновляет прогресс урока"""
    try:
        progress = UserProgress.query.filter_by(
            user_id=user_id,
            lesson_id=lesson_id
        ).first()
        
        if not progress:
            progress = UserProgress(
                user_id=user_id,
                lesson_id=lesson_id,
                viewed=viewed,
                completed=completed,
                viewed_at=datetime.now(timezone.utc) if viewed else None,
                completed_at=datetime.now(timezone.utc) if completed else None
            )
            db.session.add(progress)
        else:
            if viewed:
                progress.viewed = True
                progress.viewed_at = datetime.now(timezone.utc)
            if completed:
                progress.completed = True
                progress.completed_at = datetime.now(timezone.utc)
        
        db.session.commit()
    except Exception as e:
        current_app.logger.error(f"Error updating lesson progress: {e}")
        db.session.rollback()

# Контекстный процессор для языка
@lesson_bp.context_processor
def inject_lang():
    current_lang = g.lang
    lang = getattr(g, 'lang', current_app.config.get('DEFAULT_LANGUAGE', 'en'))
    return dict(lang=lang)

# Обновленный метод в lesson_routes.py
@lesson_bp.route("/<int:lesson_index>", methods=["GET", "POST"])
@login_required
def lesson_view(module_id, lesson_index):
    current_lang = g.lang
    """Отображает урок по индексу в модуле."""
    try:
        # Получаем модуль
        module = Module.query.get_or_404(module_id)
        
        # Получаем все уроки для модуля из базы данных
        lessons = Lesson.query.filter_by(module_id=module_id).order_by(Lesson.order).all()
        total_lessons = len(lessons)
        
        # Проверяем индекс урока
        if lesson_index < 0 or lesson_index >= total_lessons:
            flash("Урок не найден" if current_lang == 'ru' else "Lesson not found", "danger")
            return redirect(url_for('modules_bp.module_view', lang=current_lang, module_id=module_id))
        
        # Получаем текущий урок
        lesson = lessons[lesson_index]
        
        # Группируем уроки по подтемам для левого столбца
        from collections import defaultdict
        subtopics = defaultdict(list)
        
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

        def create_slug(text):
            """Создаёт унифицированный слаг из текста"""
            if not text:
                return ""
            import re
            return re.sub(r'[^a-z0-9]+', '_', text.lower()).strip('_')
        
        for lesson_item in lessons:
            subtopic_name = None
            subtopic_slug = None
            
            # Если поля subtopic и subtopic_slug заполнены, используем их
            if lesson_item.subtopic and lesson_item.subtopic_slug:
                subtopic_name = lesson_item.subtopic
                subtopic_slug = lesson_item.subtopic_slug
            else:
                # Иначе извлекаем из контента
                extracted_module_title = extract_module_title(lesson_item)
                
                if extracted_module_title:
                    subtopic_name = extracted_module_title
                    subtopic_slug = create_slug(extracted_module_title)
                else:
                    # Fallback: используем тип контента
                    if lesson_item.content_type == 'learning_card':
                        subtopic_name = f"{module.title} - Обучающие материалы"
                    elif lesson_item.content_type in ['quiz', 'test_question']:
                        subtopic_name = f"{module.title} - Тесты"
                    else:
                        subtopic_name = f"{module.title} - Общие материалы"
                    subtopic_slug = create_slug(subtopic_name)
            
            subtopics[subtopic_name].append({
                'lesson': lesson_item,
                'slug': subtopic_slug
            })
        
        # Преобразуем в формат для шаблона с добавлением прогресса
        subtopics_with_progress = []
        current_subtopic = None
        
        for subtopic_name, subtopic_lessons in subtopics.items():
            subtopic_slug = subtopic_lessons[0]['slug']
            lessons_only = [item['lesson'] for item in subtopic_lessons]
            
            # Подсчитываем прогресс
            completed_lessons = 0
            for lesson_item in lessons_only:
                progress = UserProgress.query.filter_by(
                    user_id=current_user.id,
                    lesson_id=lesson_item.id
                ).first()
                if progress and progress.completed:
                    completed_lessons += 1
            
            # Проверяем, является ли эта подтема текущей
            is_current = lesson.id in [l.id for l in lessons_only]
            if is_current:
                current_subtopic = subtopic_name
            
            subtopic_data = {
                'name': subtopic_name,
                'slug': subtopic_slug,
                'lessons': lessons_only,
                'total_lessons': len(lessons_only),
                'completed_lessons': completed_lessons,
                'progress_percent': int((completed_lessons / len(lessons_only)) * 100) if lessons_only else 0,
                'is_current': is_current
            }
            subtopics_with_progress.append(subtopic_data)
        
        # Сортируем подтемы
        subtopics_with_progress.sort(key=lambda x: x['name'])
        
        # Обрабатываем содержимое урока в зависимости от типа
        processed_content = None
        if lesson.content:
            try:
                content_data = json.loads(lesson.content)
                
                if lesson.content_type == 'learning_card' and 'cards' in content_data:
                    # Для learning_card: показываем все карточки
                    processed_content = {
                        'type': 'learning_cards',
                        'cards': content_data['cards']
                    }
                    current_app.logger.info(f"Loaded {len(content_data['cards'])} learning cards")
                
                elif lesson.content_type in ['quiz', 'test_question'] and 'questions' in content_data:
                    # Для quiz: показываем вопросы
                    processed_content = {
                        'type': 'quiz',
                        'questions': content_data['questions']
                    }
                    current_app.logger.info(f"Loaded {len(content_data['questions'])} quiz questions")
                
                else:
                    # Fallback: показываем как есть
                    processed_content = content_data
                    
            except json.JSONDecodeError as e:
                current_app.logger.error(f"JSON decode error: {e}")
                # Если не JSON, используем как текст
                processed_content = {'type': 'text', 'content': lesson.content}
        
        # Обработка формы квиза (пока упростим)
        quiz_result = None
        
        # Отслеживаем прогресс урока
        track_lesson_progress(current_user.id, lesson.id)
        
        # Обновляем прогресс пользователя
        update_lesson_progress(current_user.id, lesson.id, viewed=True)
        
        return render_template(
            "learning/lesson.html",
            module=module,
            lesson=lesson,
            lesson_index=lesson_index,
            total_lessons=total_lessons,
            quiz_result=quiz_result,
            processed_content=processed_content,
            subtopics_with_progress=subtopics_with_progress,  # Новый параметр
            current_subtopic=current_subtopic,  # Текущая подтема
            lang=current_lang
        )
    except Exception as e:
        current_app.logger.error(f"Error in lesson_view: {e}", exc_info=True)
        flash(f"Ошибка при загрузке урока: {e}" if current_lang == 'ru' else f"Error loading lesson: {e}", "danger")
        return redirect(url_for('modules_bp.module_view', lang=current_lang, module_id=module_id))

# Маршрут для отображения урока по lesson_id
@lesson_bp.route("/view/<int:lesson_id>")
@login_required
def lesson_view_by_id(lesson_id):
    """Отображает урок по его ID"""
    current_lang = g.lang
    
    try:
        # Получаем урок
        lesson = Lesson.query.get_or_404(lesson_id)
        
        # Получаем модуль
        module = lesson.module
        if not module:
            flash("Урок не связан с модулем" if current_lang == 'ru' else "Lesson not linked to module", "danger")
            return redirect(url_for('learning.index'))
        
        # Получаем все уроки модуля
        lessons_in_module = module.lessons.order_by(Lesson.order).all()
        current_index = next((i for i, l in enumerate(lessons_in_module) if l.id == lesson.id), 0)
        
        # Получаем предыдущий и следующий уроки
        prev_lesson = lessons_in_module[current_index - 1] if current_index > 0 else None
        next_lesson = lessons_in_module[current_index + 1] if current_index < len(lessons_in_module) - 1 else None
        
        # Получаем или создаем прогресс
        progress = lesson.get_user_progress(current_user.id)
        if not progress:
            progress = UserProgress(
                user_id=current_user.id,
                lesson_id=lesson.id
            )
            db.session.add(progress)
            db.session.commit()
        
        # Обновляем время последнего доступа
        progress.last_accessed = datetime.now(timezone.utc)
        db.session.commit()
        
        # Обрабатываем контент
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
    
    except Exception as e:
        current_app.logger.error(f"Error in lesson_view_by_id: {e}", exc_info=True)
        flash(f"Ошибка при загрузке урока: {e}" if current_lang == 'ru' else f"Error loading lesson: {e}", "danger")
        return redirect(url_for('learning.index'))

@lesson_bp.route("/mark-completed/<int:lesson_id>", methods=["POST"])
@login_required
def mark_lesson_completed(lesson_id):
    """Отмечает урок как завершенный"""
    try:
        update_lesson_progress(current_user.id, lesson_id, completed=True)
        return jsonify({'success': True, 'message': 'Урок отмечен как завершенный'})
    except Exception as e:
        current_app.logger.error(f"Error marking lesson completed: {e}")
        return jsonify({'success': False, 'message': f'Ошибка: {e}'}), 500

@lesson_bp.route("/progress/<int:module_id>")
@login_required
def module_progress(module_id):
    """Показывает прогресс по модулю"""
    try:
        module = Module.query.get_or_404(module_id)
        lessons = Lesson.query.filter_by(module_id=module_id).order_by(Lesson.order).all()
        
        progress_data = []
        total_lessons = len(lessons)
        completed_lessons = 0
        
        for lesson in lessons:
            progress = UserProgress.query.filter_by(
                user_id=current_user.id,
                lesson_id=lesson.id
            ).first()
            
            is_completed = progress and progress.completed
            if is_completed:
                completed_lessons += 1
            
            progress_data.append({
                'lesson_id': lesson.id,
                'title': lesson.title,
                'completed': is_completed,
                'viewed': progress and progress.viewed
            })
        
        progress_percentage = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
        
        return render_template(
            "learning/module_progress.html",
            module=module,
            progress_data=progress_data,
            total_lessons=total_lessons,
            completed_lessons=completed_lessons,
            progress_percentage=progress_percentage
        )
    except Exception as e:
        current_app.logger.error(f"Error in module_progress: {e}")
        flash(f"Ошибка при загрузке прогресса: {e}", "danger")
        return redirect(url_for('modules_bp.module_view', module_id=module_id))