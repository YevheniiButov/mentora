#!/usr/bin/env python3
"""
Скрипт для создания тестового контента для демонстрации новой системы навигации
"""

import json
from app import create_app
from models import db, ContentCategory, ContentSubcategory, ContentTopic, Lesson, Module, Subject, LearningPath

def create_slug(text):
    """Создает URL-friendly slug из текста"""
    import re
    import unicodedata
    
    if not text:
        return ""
    
    # Удаляем HTML теги если есть
    text = re.sub(r'<[^>]+>', '', text)
    
    # Нормализуем unicode символы
    text = unicodedata.normalize('NFKD', text)
    
    # Конвертируем в нижний регистр
    text = text.lower()
    
    # Заменяем пробелы и специальные символы на дефисы
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    
    # Удаляем дефисы в начале и конце
    text = text.strip('-')
    
    return text[:50]  # Ограничиваем длину

def create_test_content():
    """Создает тестовый контент"""
    
    print("🚀 Создание тестового контента...")
    
    # 1. Создаем категории
    categories_data = [
        {
            'name': 'Анатомия зуба',
            'icon': 'diagram-3',
            'subcategories': [
                {
                    'name': 'Строение зуба',
                    'icon': 'gear',
                    'topics': [
                        {
                            'name': 'Коронка зуба',
                            'description': 'Изучение строения коронки зуба'
                        },
                        {
                            'name': 'Корень зуба',
                            'description': 'Анатомия корневой системы'
                        }
                    ]
                }
            ]
        },
        {
            'name': 'Стоматологические заболевания',
            'icon': 'bug',
            'subcategories': [
                {
                    'name': 'Кариес',
                    'icon': 'exclamation-triangle',
                    'topics': [
                        {
                            'name': 'Этиология кариеса',
                            'description': 'Причины возникновения кариеса'
                        }
                    ]
                }
            ]
        }
    ]
    
    # Создаем контент
    for cat_data in categories_data:
        print(f"📁 Создание категории: {cat_data['name']}")
        
        # Создаем категорию
        category = ContentCategory(
            name=cat_data['name'],
            slug=create_slug(cat_data['name']),
            icon=cat_data['icon'],
            order=len(ContentCategory.query.all()) + 1
        )
        db.session.add(category)
        db.session.flush()
        
        # Создаем подкатегории
        for subcat_data in cat_data['subcategories']:
            print(f"  📂 Создание подкатегории: {subcat_data['name']}")
            
            subcategory = ContentSubcategory(
                name=subcat_data['name'],
                slug=create_slug(subcat_data['name']),
                category_id=category.id,
                icon=subcat_data['icon'],
                order=len(category.subcategories.all()) + 1
            )
            db.session.add(subcategory)
            db.session.flush()
            
            # Создаем темы
            for topic_data in subcat_data['topics']:
                print(f"    📄 Создание темы: {topic_data['name']}")
                
                topic = ContentTopic(
                    name=topic_data['name'],
                    slug=create_slug(topic_data['name']),
                    subcategory_id=subcategory.id,
                    description=topic_data['description'],
                    order=len(subcategory.topics.all()) + 1
                )
                db.session.add(topic)
                db.session.flush()
                
                # Создаем тестовые уроки для темы
                create_test_lessons_for_topic(topic)
    
    db.session.commit()
    print("✅ Тестовый контент создан!")

def create_test_lessons_for_topic(topic):
    """Создает тестовые уроки для темы"""
    
    # Найдем или создадим модуль для связи
    module = Module.query.first()
    if not module:
        # Создаем тестовый модуль
        learning_path = LearningPath.query.first()
        if not learning_path:
            learning_path = LearningPath(
                name="Тестовый путь обучения",
                description="Для тестирования",
                order=1
            )
            db.session.add(learning_path)
            db.session.flush()
        
        subject = Subject.query.first()
        if not subject:
            subject = Subject(
                name="Тестовый предмет",
                description="Для тестирования",
                learning_path_id=learning_path.id,
                order=1
            )
            db.session.add(subject)
            db.session.flush()
        
        module = Module(
            title="Тестовый модуль",
            description="Для тестирования",
            subject_id=subject.id,
            order=1
        )
        db.session.add(module)
        db.session.flush()
    
    # Создаем теоретический урок
    theory_content = {
        "cards": [
            {
                "question": f"Что такое {topic.name}?",
                "answer": f"Подробное объяснение {topic.name}. Это важная тема в стоматологии.",
                "tags": ["теория", "основы"]
            }
        ]
    }
    
    theory_lesson = Lesson(
        title=f"{topic.name} - Теория",
        module_id=module.id,
        content_type='learning_card',
        content=json.dumps(theory_content, ensure_ascii=False),
        order=1,
        topic_id=topic.id
    )
    db.session.add(theory_lesson)
    
    print(f"      ✅ Создан урок для темы {topic.name}")

if __name__ == '__main__':
    app = create_app()
    
    with app.app_context():
        try:
            create_test_content()
            
            print("\n🎉 ГОТОВО! Тестовый контент создан.")
            print("📋 Создано:")
            print(f"   - Категорий: {ContentCategory.query.count()}")
            print(f"   - Подкатегорий: {ContentSubcategory.query.count()}")
            print(f"   - Тем: {ContentTopic.query.count()}")
            print("\n🌐 Перейди по адресу: http://127.0.0.1:5000/ru/learn/")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            db.session.rollback()
            raise
