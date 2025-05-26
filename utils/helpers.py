# utils/helpers.py
"""
Вспомогательные функции для работы с модулями и уроками
"""

import json
import re
from flask import current_app


def create_slug(text):
    """Создаёт унифицированный слаг из текста"""
    if not text:
        return ""
    # Заменяем пробелы, дефисы, слеши и другие символы на подчеркивания
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


def get_subtopic_name_and_slug(lesson, module_title_fallback=""):
    """
    Получает название и слаг подтемы для урока
    
    Args:
        lesson: Объект урока
        module_title_fallback: Название модуля для fallback
        
    Returns:
        tuple: (subtopic_name, subtopic_slug)
    """
    subtopic_name = None
    subtopic_slug = None
    
    # Если поля subtopic и subtopic_slug заполнены, используем их
    if hasattr(lesson, 'subtopic') and hasattr(lesson, 'subtopic_slug') and lesson.subtopic and lesson.subtopic_slug:
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
                subtopic_name = f"{module_title_fallback} - Обучающие материалы"
            elif lesson.content_type in ['quiz', 'test_question']:
                subtopic_name = f"{module_title_fallback} - Тесты"
            else:
                subtopic_name = f"{module_title_fallback} - Общие материалы"
            subtopic_slug = create_slug(subtopic_name)
    
    return subtopic_name, subtopic_slug


def group_lessons_by_subtopics(lessons, module_title=""):
    """
    Группирует уроки по подтемам
    
    Args:
        lessons: Список уроков
        module_title: Название модуля для fallback
        
    Returns:
        dict: Словарь с группировкой по подтемам
    """
    from collections import defaultdict
    
    subtopics = defaultdict(list)
    
    for lesson in lessons:
        subtopic_name, subtopic_slug = get_subtopic_name_and_slug(lesson, module_title)
        
        # Добавляем ключ slug к хранимым данным
        lesson_with_slug = {
            'lesson': lesson,
            'slug': subtopic_slug
        }
        subtopics[subtopic_name].append(lesson_with_slug)
    
    return subtopics


def calculate_subtopic_progress(subtopic_lessons, user_id):
    """
    Вычисляет прогресс для подтемы
    
    Args:
        subtopic_lessons: Список уроков подтемы
        user_id: ID пользователя
        
    Returns:
        dict: Статистика прогресса
    """
    from models import UserProgress
    
    total_lessons = len(subtopic_lessons)
    completed_lessons = 0
    
    for lesson in subtopic_lessons:
        progress = UserProgress.query.filter_by(
            user_id=user_id,
            lesson_id=lesson.id
        ).first()
        if progress and progress.completed:
            completed_lessons += 1
    
    progress_percent = int((completed_lessons / total_lessons) * 100) if total_lessons > 0 else 0
    
    return {
        'total_lessons': total_lessons,
        'completed_lessons': completed_lessons,
        'progress_percent': progress_percent
    }


def prepare_subtopics_with_progress(lessons, user_id, module_title=""):
    """
    Подготавливает список подтем с прогрессом для передачи в шаблон
    
    Args:
        lessons: Список уроков
        user_id: ID пользователя
        module_title: Название модуля
        
    Returns:
        list: Список подтем с прогрессом
    """
    subtopics = group_lessons_by_subtopics(lessons, module_title)
    subtopics_with_progress = []
    
    for subtopic_name, subtopic_lessons in subtopics.items():
        # Получаем слаг из первого урока
        subtopic_slug = subtopic_lessons[0]['slug']
        
        # Выделяем объекты уроков для подсчета прогресса
        lessons_only = [item['lesson'] for item in subtopic_lessons]
        
        # Подсчитываем прогресс
        progress_stats = calculate_subtopic_progress(lessons_only, user_id)
        
        subtopic_data = {
            'name': subtopic_name,
            'slug': subtopic_slug,
            'lessons': lessons_only,
            **progress_stats
        }
        subtopics_with_progress.append(subtopic_data)
    
    # Сортируем подтемы
    subtopics_with_progress.sort(key=lambda x: x['name'])
    
    return subtopics_with_progress