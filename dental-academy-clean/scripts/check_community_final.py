#!/usr/bin/env python3
"""
Финальная проверка комьюнити
"""

import os
import sys

def check_community_final():
    """Финальная проверка комьюнити"""
    
    try:
        # Добавляем путь к проекту
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_root)
        
        # Импортируем Flask приложение
        from app import app
        from extensions import db
        from models import ForumCategory, ForumTopic, User
        
        print("🔍 Final community check...")
        
        with app.app_context():
            # Проверяем подключение к БД
            try:
                db.session.execute(db.text("SELECT 1"))
                print("✅ Database connection successful")
            except Exception as e:
                print(f"❌ Database connection failed: {str(e)}")
                return False
            
            # Проверяем категории
            categories = ForumCategory.query.filter_by(is_active=True).order_by(ForumCategory.order).all()
            print(f"\n📁 Active categories: {len(categories)}")
            for cat in categories:
                print(f"  - {cat.name} (ID: {cat.id}, Slug: {cat.slug})")
            
            # Проверяем темы
            all_topics = ForumTopic.query.order_by(ForumTopic.created_at.desc()).limit(10).all()
            print(f"\n📝 Recent topics: {len(all_topics)}")
            for topic in all_topics:
                author_name = f"{topic.author.first_name} {topic.author.last_name}".strip() if topic.author else 'Unknown'
                print(f"  - '{topic.title}' by {author_name}")
                print(f"    Created: {topic.created_at}, Status: {topic.status}")
            
            # Проверяем пользователей
            users = User.query.filter_by(is_active=True).limit(5).all()
            print(f"\n👥 Sample users: {len(users)}")
            for user in users:
                print(f"  - {user.first_name} {user.last_name} ({user.email}) - Role: {user.role}")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция"""
    print("🚀 Final Community Checker")
    print("=" * 50)
    
    success = check_community_final()
    
    if success:
        print("✅ Script completed successfully!")
        sys.exit(0)
    else:
        print("❌ Script failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
