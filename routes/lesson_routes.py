# routes/lesson_routes.py

from flask import (
    Blueprint, render_template, redirect, url_for, request, session, 
    flash, g, current_app, jsonify
)
from flask_login import login_required, current_user
from models import db, Module, Lesson, UserProgress
from datetime import datetime
import json
import logging
from utils.unified_stats import track_lesson_progress, clear_stats_cache

# Создаем Blueprint для уроков
lesson_bp = Blueprint(
    "lesson_bp", 
    __name__, 
    url_prefix='/<string:lang>/module/<int:module_id>/lesson',
    template_folder='../templates'
)

# Контекстный процессор для языка
@lesson_bp.context_processor
def inject_lang():
    lang = getattr(g, 'lang', current_app.config.get('DEFAULT_LANGUAGE', 'en'))
    return dict(lang=lang)

# Обновленный метод в lesson_routes.py

@lesson_bp.route("/<int:lesson_index>", methods=["GET", "POST"])
@login_required
def lesson_view(lang, module_id, lesson_index):
    """Отображает урок по индексу в модуле."""
    try:
        # Получаем модуль
        module = Module.query.get_or_404(module_id)
        
        # Получаем все уроки для модуля из базы данных
        lessons = Lesson.query.filter_by(module_id=module_id).order_by(Lesson.order).all()
        total_lessons = len(lessons)
        
        # Проверяем индекс урока
        if lesson_index < 0 or lesson_index >= total_lessons:
            flash("Урок не найден" if lang == 'ru' else "Lesson not found", "danger")
            return redirect(url_for('modules_bp.module_view', lang=lang, module_id=module_id))
        
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
            lang=lang
        )
    except Exception as e:
        current_app.logger.error(f"Error in lesson_view: {e}", exc_info=True)
        flash(f"Ошибка при загрузке урока: {e}" if lang == 'ru' else f"Error loading lesson: {e}", "danger")
        return redirect(url_for('modules_bp.module_view', lang=lang, module_id=module_id))
    

@lesson_bp.route("/mark-completed/<int:lesson_id>", methods=["POST"])
@login_required
def mark_lesson_completed(lang, module_id, lesson_id):
    """Отмечает урок как завершенный."""
    try:
        # Проверяем, существует ли урок
        lesson = Lesson.query.get_or_404(lesson_id)
        
        # Проверяем, принадлежит ли урок указанному модулю
        if lesson.module_id != module_id:
            return jsonify({'success': False, 'message': 'Lesson does not belong to this module'}), 400
        
        # Обновляем прогресс
        success = update_lesson_progress(current_user.id, lesson_id, completed=True)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Failed to update progress'}), 500
        
    except Exception as e:
        current_app.logger.error(f"Error marking lesson as completed: {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500

@lesson_bp.route("/save-progress/<int:lesson_id>", methods=["POST"])
@login_required
def save_lesson_progress(lang, module_id, lesson_id):
    """Сохраняет прогресс по уроку."""
    try:
        # Получаем данные из запроса
        data = request.get_json()
        time_spent = data.get('time_spent', 0)
        completed = data.get('completed', False)
        
        # Проверяем, существует ли урок
        lesson = Lesson.query.get_or_404(lesson_id)
        
        # Проверяем, принадлежит ли урок указанному модулю
        if lesson.module_id != module_id:
            return jsonify({'success': False, 'message': 'Lesson does not belong to this module'}), 400
        
        # Обновляем прогресс
        success = update_lesson_progress(current_user.id, lesson_id, time_spent=time_spent, completed=completed)
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Failed to update progress'}), 500
        
    except Exception as e:
        current_app.logger.error(f"Error saving lesson progress: {e}", exc_info=True)
        return jsonify({'success': False, 'message': str(e)}), 500

# Вспомогательные функции

def update_lesson_progress(user_id, lesson_id, time_spent=None, viewed=False, completed=False):
    """
    Обертка для обратной совместимости
    Использует унифицированную систему отслеживания прогресса
    """
    return track_lesson_progress(user_id, lesson_id, time_spent, completed)

def get_lesson_progress(user_id, lesson_id):
    """Получает информацию о прогрессе пользователя по уроку."""
    try:
        progress = UserProgress.query.filter_by(
            user_id=user_id,
            lesson_id=lesson_id
        ).first()
        
        if progress:
            return {
                'completed': progress.completed,
                'time_spent': progress.time_spent,
                'last_accessed': progress.last_accessed
            }
        else:
            return {
                'completed': False,
                'time_spent': 0,
                'last_accessed': None
            }
    except Exception as e:
        current_app.logger.error(f"Error getting lesson progress: {e}", exc_info=True)
        return {
            'completed': False,
            'time_spent': 0,
            'last_accessed': None,
            'error': str(e)
        }

# Дополнительные маршруты для навигации

@lesson_bp.route("/<int:lesson_index>/next", methods=["POST"])
@login_required
def next_lesson(lang, module_id, lesson_index):
    """Переходит к следующему уроку в модуле."""
    try:
        lessons = Lesson.query.filter_by(module_id=module_id).order_by(Lesson.order).all()
        total_lessons = len(lessons)
        
        # Отмечаем текущий урок как завершенный
        if lesson_index < total_lessons:
            current_lesson = lessons[lesson_index]
            update_lesson_progress(current_user.id, current_lesson.id, completed=True)
        
        # Проверяем, есть ли следующий урок
        next_index = lesson_index + 1
        if next_index < total_lessons:
            return redirect(url_for('lesson_bp.lesson_view', lang=lang, module_id=module_id, lesson_index=next_index))
        else:
            # Если это был последний урок, возвращаемся к модулю
            flash("Поздравляем! Вы завершили модуль!" if lang == 'ru' else "Congratulations! You completed the module!", "success")
            return redirect(url_for('modules_bp.module_view', lang=lang, module_id=module_id))
            
    except Exception as e:
        current_app.logger.error(f"Error in next_lesson: {e}", exc_info=True)
        flash(f"Ошибка при переходе к следующему уроку" if lang == 'ru' else "Error moving to next lesson", "danger")
        return redirect(url_for('modules_bp.module_view', lang=lang, module_id=module_id))

@lesson_bp.route("/<int:lesson_index>/previous", methods=["POST"])
@login_required  
def previous_lesson(lang, module_id, lesson_index):
    """Переходит к предыдущему уроку в модуле."""
    try:
        # Проверяем, есть ли предыдущий урок
        previous_index = lesson_index - 1
        if previous_index >= 0:
            return redirect(url_for('lesson_bp.lesson_view', lang=lang, module_id=module_id, lesson_index=previous_index))
        else:
            # Если это был первый урок, возвращаемся к модулю
            return redirect(url_for('modules_bp.module_view', lang=lang, module_id=module_id))
            
    except Exception as e:
        current_app.logger.error(f"Error in previous_lesson: {e}", exc_info=True)
        flash(f"Ошибка при переходе к предыдущему уроку" if lang == 'ru' else "Error moving to previous lesson", "danger")
        return redirect(url_for('modules_bp.module_view', lang=lang, module_id=module_id))