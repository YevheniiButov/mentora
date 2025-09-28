#!/usr/bin/env python3
"""
Скрипт для удаления всех тем и сообщений
"""

import os
import sys

def delete_all_topics():
    """Удаляет все темы и сообщения"""
    
    try:
        # Добавляем путь к проекту
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_root)
        
        # Импортируем Flask приложение
        from app import app
        from extensions import db
        from models import ForumCategory, ForumTopic, ForumPost, User
        
        print("🗑️ Deleting all topics and messages...")
        
        with app.app_context():
            # Проверяем подключение к БД
            try:
                db.session.execute(db.text("SELECT 1"))
                print("✅ Database connection successful")
            except Exception as e:
                print(f"❌ Database connection failed: {str(e)}")
                return False
            
            # Подсчитываем что будет удалено
            topics_count = ForumTopic.query.count()
            posts_count = ForumPost.query.count()
            
            print(f"📊 Found {topics_count} topics and {posts_count} posts to delete")
            
            if topics_count == 0:
                print("✅ No topics to delete")
                return True
            
            # Удаляем все сообщения
            print("🗑️ Deleting all posts...")
            ForumPost.query.delete()
            
            # Удаляем все темы
            print("🗑️ Deleting all topics...")
            ForumTopic.query.delete()
            
            # Коммитим изменения
            db.session.commit()
            
            print(f"✅ Successfully deleted {topics_count} topics and {posts_count} posts!")
            return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция"""
    print("🚀 Delete All Topics")
    print("=" * 50)
    
    success = delete_all_topics()
    
    if success:
        print("✅ Script completed successfully!")
        sys.exit(0)
    else:
        print("❌ Script failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()


