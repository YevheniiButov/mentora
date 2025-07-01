# init_content_editor.py - Скрипт для инициализации Content Editor

"""
Скрипт для инициализации системы Content Editor.
Создает таблицы в БД и загружает базовые шаблоны.

Использование:
python init_content_editor.py
"""

import os
import sys
import json
from datetime import datetime

# Добавляем корневую папку в путь для импорта модулей
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_sample_templates():
    """Создает примеры шаблонов для тестирования"""
    return {
        "lesson_basic": {
            "name": {"en": "Basic Lesson Template", "ru": "Базовый шаблон урока"},
            "description": {"en": "Simple lesson template with text and images", "ru": "Простой шаблон урока с текстом и изображениями"},
            "category": "lesson",
            "language": "en",
            "is_system": True,
            "tags": ["lesson", "basic", "text"],
            "template_metadata": {
                "author": "system",
                "version": "1.0",
                "difficulty": "beginner"
            },
            "structure": [
                {
                    "type": "heading",
                    "level": 1,
                    "content": "Lesson Title",
                    "styles": "color: #2C3E50; font-size: 32px; font-weight: bold; text-align: center; margin: 30px 0;"
                },
                {
                    "type": "text",
                    "content": "This is the main content of your lesson. You can add paragraphs, explanations, and educational content here.",
                    "styles": "font-size: 16px; line-height: 1.8; color: #34495E; margin: 20px 0; text-align: justify;"
                },
                {
                    "type": "image",
                    "src": "/static/images/placeholder.jpg",
                    "alt": "Educational Image",
                    "caption": "Figure 1: Example image for the lesson",
                    "styles": "max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin: 20px 0;"
                },
                {
                    "type": "list",
                    "items": [
                        "First important point",
                        "Second key concept", 
                        "Third essential knowledge"
                    ],
                    "styles": "margin: 15px 0; padding-left: 20px;"
                },
                {
                    "type": "button",
                    "content": "Continue to Next Section",
                    "href": "#next",
                    "styles": "background: #3ECDC1; color: white; padding: 12px 24px; border-radius: 6px; text-decoration: none; display: inline-block; margin: 20px 0;"
                }
            ]
        },
        "quiz_interactive": {
            "name": {"en": "Interactive Quiz Template", "ru": "Интерактивный шаблон теста"},
            "description": {"en": "Quiz template with multiple choice questions and feedback", "ru": "Шаблон теста с вопросами с выбором ответа и обратной связью"},
            "category": "quiz",
            "language": "en",
            "is_system": True,
            "tags": ["quiz", "interactive", "assessment"],
            "template_metadata": {
                "author": "system",
                "version": "1.0",
                "question_count": 3
            },
            "structure": [
                {
                    "type": "heading",
                    "level": 1,
                    "content": "Knowledge Check Quiz",
                    "styles": "color: #6C5CE7; font-size: 28px; font-weight: bold; text-align: center; margin: 20px 0;"
                },
                {
                    "type": "quiz",
                    "content": "What is the primary function of molars?",
                    "options": [
                        "Cutting food",
                        "Tearing food", 
                        "Grinding food",
                        "Holding food"
                    ],
                    "correct": 2,
                    "explanation": "Molars are designed for grinding and crushing food with their flat surfaces.",
                    "styles": "border: 2px solid #6C5CE7; border-radius: 8px; padding: 20px; margin: 20px 0; background: #f8fafc;"
                },
                {
                    "type": "divider",
                    "styles": "height: 2px; background: linear-gradient(90deg, #3ECDC1, #6C5CE7); margin: 30px 0;"
                },
                {
                    "type": "button",
                    "content": "Submit Quiz",
                    "styles": "background: #6C5CE7; color: white; padding: 12px 30px; border-radius: 6px; text-decoration: none; display: block; text-align: center; margin: 20px auto; max-width: 200px;"
                }
            ]
        },
        "flashcard_dental": {
            "name": {"en": "Dental Flashcard Template", "ru": "Шаблон стоматологических карточек"},
            "description": {"en": "Interactive flashcard for dental terminology and concepts", "ru": "Интерактивные карточки для стоматологической терминологии и концепций"},
            "category": "flashcard",
            "language": "en",
            "is_system": True,
            "tags": ["flashcard", "terminology", "memory"],
            "template_metadata": {
                "author": "system",
                "version": "1.0",
                "difficulty": "intermediate"
            },
            "structure": [
                {
                    "type": "heading",
                    "level": 2,
                    "content": "Dental Terminology Flashcards",
                    "styles": "color: #FDCB6E; font-size: 24px; font-weight: bold; text-align: center; margin: 20px 0;"
                },
                {
                    "type": "flashcard",
                    "front": {
                        "type": "text",
                        "content": "Caries",
                        "styles": "font-size: 28px; font-weight: bold; text-align: center; color: white;"
                    },
                    "back": {
                        "type": "text", 
                        "content": "Tooth decay caused by bacteria producing acid that demineralizes tooth enamel",
                        "styles": "font-size: 16px; text-align: center; color: white; line-height: 1.6;"
                    },
                    "styles": "min-height: 200px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.1);"
                },
                {
                    "type": "button",
                    "content": "Next Card",
                    "styles": "background: #FDCB6E; color: #2c3e50; padding: 10px 20px; border-radius: 6px; text-decoration: none; display: block; text-align: center; margin: 20px auto; max-width: 150px;"
                }
            ]
        }
    }

def init_content_editor():
    """Инициализирует систему Content Editor"""
    print("🚀 Initializing Dental Academy Content Editor...")
    
    try:
        # Импортируем Flask приложение
        from app import app, db
        from models import ContentTemplate
        
        with app.app_context():
            print("📊 Creating database tables...")
            
            # Создаем все таблицы
            db.create_all()
            print("✅ Database tables created successfully")
            
            # Проверяем, есть ли уже шаблоны
            existing_templates = ContentTemplate.query.count()
            if existing_templates > 0:
                print(f"📋 Found {existing_templates} existing templates")
                
                response = input("Do you want to add sample templates anyway? (y/n): ")
                if response.lower() != 'y':
                    print("⏭️ Skipping template creation")
                    return
            
            print("📝 Creating sample templates...")
            
            # Создаем примеры шаблонов
            templates_data = create_sample_templates()
            created_count = 0
            
            for template_id, template_info in templates_data.items():
                try:
                    # Проверяем, существует ли уже такой шаблон
                    existing = ContentTemplate.query.filter_by(template_id=template_id).first()
                    if existing:
                        print(f"   ⚠️ Template '{template_id}' already exists, skipping")
                        continue
                    
                    # Создаем новый шаблон
                    template = ContentTemplate(
                        template_id=template_id,
                        name=template_info['name'],
                        description=template_info['description'],
                        category=template_info['category'],
                        structure=template_info['structure'],
                        template_metadata=template_info['template_metadata'],
                        tags=template_info['tags'],
                        is_system=template_info['is_system'],
                        language=template_info['language']
                    )
                    
                    db.session.add(template)
                    created_count += 1
                    print(f"   ✅ Created template: {template_info['name']}")
                    
                except Exception as e:
                    print(f"   ❌ Error creating template '{template_id}': {e}")
            
            # Сохраняем в БД
            db.session.commit()
            print(f"💾 Created {created_count} templates successfully")
            
            # Создаем папку для медиа файлов
            media_dir = os.path.join(app.static_folder, 'uploads')
            os.makedirs(media_dir, exist_ok=True)
            print(f"📁 Media directory created: {media_dir}")
            
            # Создаем папку для данных
            data_dir = os.path.join(app.root_path, 'data')
            os.makedirs(data_dir, exist_ok=True)
            print(f"📁 Data directory created: {data_dir}")
            
            print("\n🎉 Content Editor initialization completed successfully!")
            print("\n📋 Summary:")
            print(f"   • Database tables: ✅ Created")
            print(f"   • Sample templates: ✅ {created_count} created")
            print(f"   • Media directory: ✅ Created")
            print(f"   • Data directory: ✅ Created")
            
            print("\n🚀 Next steps:")
            print("   1. Register the content_editor blueprint in your app")
            print("   2. Add navigation menu items for the editor")
            print("   3. Create the frontend templates")
            print("   4. Test the editor functionality")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're running this script from the Flask app directory")
    except Exception as e:
        print(f"❌ Initialization error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = init_content_editor()
    if success:
        print("\n✨ Content Editor is ready to use!")
    else:
        print("\n💥 Initialization failed. Please check the errors above.")
        sys.exit(1) 