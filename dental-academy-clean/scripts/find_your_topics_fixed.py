#!/usr/bin/env python3
"""
Скрипт для поиска тем с вашим именем (исправленный)
"""

import os
import sys

def find_your_topics():
    """Находит темы с вашим именем"""
    
    try:
        # Добавляем путь к проекту
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_root)
        
        # Импортируем Flask приложение
        from app import app
        from extensions import db
        from models import ForumCategory, ForumTopic, User
        
        print("🔍 Finding topics with your name...")
        
        with app.app_context():
            # Проверяем подключение к БД
            try:
                db.session.execute(db.text("SELECT 1"))
                print("✅ Database connection successful")
            except Exception as e:
                print(f"❌ Database connection failed: {str(e)}")
                return False
            
            # Находим все темы с вашим именем (исправленный запрос)
            your_topics = ForumTopic.query.join(User, ForumTopic.author_id == User.id).filter(
                User.first_name.like('%Yevhenii%') | 
                User.first_name.like('%Евгений%') |
                User.last_name.like('%Butov%')
            ).all()
            
            print(f"\n📝 Found {len(your_topics)} topics with your name:")
            
            for topic in your_topics:
                author_name = f"{topic.author.first_name} {topic.author.last_name}".strip()
                print(f"  - '{topic.title}'")
                print(f"    Author: {author_name} ({topic.author.email})")
                print(f"    Created: {topic.created_at}")
                print(f"    ID: {topic.id}")
                print("")
            
            # Также проверим все темы от admin@mentora.com
            admin_topics = ForumTopic.query.join(User, ForumTopic.author_id == User.id).filter(
                User.email == 'admin@mentora.com'
            ).all()
            
            print(f"\n📝 Found {len(admin_topics)} topics from admin@mentora.com:")
            
            for topic in admin_topics:
                print(f"  - '{topic.title}'")
                print(f"    Author: {topic.author.first_name} {topic.author.last_name}")
                print(f"    Created: {topic.created_at}")
                print(f"    ID: {topic.id}")
                print("")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция"""
    print("🚀 Your Topics Finder (Fixed)")
    print("=" * 50)
    
    success = find_your_topics()
    
    if success:
        print("✅ Script completed successfully!")
        sys.exit(0)
    else:
        print("❌ Script failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
