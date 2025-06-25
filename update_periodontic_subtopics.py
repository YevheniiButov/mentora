#!/usr/bin/env python3
"""
Скрипт для обновления подтем в модуле Periodontic
"""

from app import create_app, db
from models import Module, Lesson
import json

def update_periodontic_subtopics():
    """Обновляет подтемы для модуля Periodontic"""
    app = create_app()
    
    with app.app_context():
        # Получаем модуль Periodontic
        module = Module.query.get(4)
        if not module:
            print("❌ Модуль Periodontic не найден")
            return
        
        print(f"📚 Обновляем подтемы для модуля: {module.title}")
        
        # Получаем все уроки модуля
        lessons = Lesson.query.filter_by(module_id=4).all()
        print(f"📖 Найдено уроков: {len(lessons)}")
        
        updated = 0
        subtopics = set()
        
        for lesson in lessons:
            if lesson.content:
                try:
                    content_data = json.loads(lesson.content)
                    module_title = None
                    
                    # Проверяем разные структуры
                    if 'module_title' in content_data:
                        module_title = content_data.get('module_title')
                    elif 'cards' in content_data and content_data['cards']:
                        # Берем module_title из первой карточки
                        module_title = content_data['cards'][0].get('module_title')
                    elif 'questions' in content_data and content_data['questions']:
                        # Берем module_title из первого вопроса
                        module_title = content_data['questions'][0].get('module_title')
                    
                    if module_title:
                        lesson.subtopic = module_title
                        lesson.subtopic_slug = module_title.lower().replace(' ', '-').replace(':', '')
                        subtopics.add(module_title)
                        updated += 1
                        
                except (json.JSONDecodeError, KeyError) as e:
                    print(f"⚠️ Ошибка парсинга урока {lesson.id}: {e}")
                    continue
        
        # Сохраняем изменения
        db.session.commit()
        
        print(f"✅ Обновлено уроков: {updated}")
        print(f"📋 Найдено подтем: {len(subtopics)}")
        
        for subtopic in sorted(subtopics):
            print(f"   - {subtopic}")

if __name__ == "__main__":
    update_periodontic_subtopics() 