#!/usr/bin/env python3
"""
Скрипт для тестирования роута комьюнити
"""

import os
import sys

def test_community_route():
    """Тестирует роут комьюнити"""
    
    try:
        # Добавляем путь к проекту
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_root)
        
        # Импортируем Flask приложение
        from app import app
        from extensions import db
        from models import ForumCategory, ForumTopic, User
        
        print("🔍 Testing community route...")
        
        with app.app_context():
            # Проверяем подключение к БД
            try:
                db.session.execute(db.text("SELECT 1"))
                print("✅ Database connection successful")
            except Exception as e:
                print(f"❌ Database connection failed: {str(e)}")
                return False
            
            # Тестируем запросы как в роуте
            print("\n📁 Testing categories query...")
            categories = ForumCategory.query.filter_by(is_active=True).order_by(ForumCategory.order).all()
            print(f"✅ Found {len(categories)} active categories")
            
            print("\n📝 Testing recent topics query...")
            recent_topics = ForumTopic.query.order_by(ForumTopic.created_at.desc()).limit(10).all()
            print(f"✅ Found {len(recent_topics)} recent topics:")
            for topic in recent_topics:
                print(f"  - '{topic.title}' - {topic.created_at}")
            
            print("\n🔥 Testing popular topics query...")
            popular_topics = ForumTopic.query.order_by(ForumTopic.views_count.desc()).limit(5).all()
            print(f"✅ Found {len(popular_topics)} popular topics:")
            for topic in popular_topics:
                print(f"  - '{topic.title}' - {topic.views_count} views")
            
            # Проверяем есть ли активные пользователи
            print("\n👥 Testing users...")
            users = User.query.filter_by(is_active=True).all()
            print(f"✅ Found {len(users)} active users")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция"""
    print("🚀 Community Route Tester")
    print("=" * 50)
    
    success = test_community_route()
    
    if success:
        print("✅ Script completed successfully!")
        sys.exit(0)
    else:
        print("❌ Script failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
