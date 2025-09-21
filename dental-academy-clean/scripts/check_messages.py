#!/usr/bin/env python3
"""
Скрипт для проверки сообщений в темах
"""

import os
import sys

# Add the project root to the sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app import app
from extensions import db
from models import ForumTopic, ForumPost, User

def check_messages():
    """Проверяет сообщения в темах"""
    print("🔍 Checking messages in topics...")
    
    with app.app_context():
        try:
            db.session.execute(db.text("SELECT 1"))
            print("✅ Database connection successful")
        except Exception as e:
            print(f"❌ Database connection failed: {str(e)}")
            return False

        # Получаем все темы
        topics = ForumTopic.query.all()
        print(f"\n📋 Found {len(topics)} topics:")
        
        total_messages = 0
        for topic in topics:
            messages = ForumPost.query.filter_by(topic_id=topic.id).all()
            total_messages += len(messages)
            print(f"  📝 '{topic.title}' - {len(messages)} messages")
            
            # Показываем первые 3 сообщения
            for i, msg in enumerate(messages[:3]):
                author = User.query.get(msg.author_id)
                author_name = f"{author.first_name} {author.last_name}" if author else "Unknown"
                print(f"    {i+1}. {author_name}: {msg.content[:50]}...")
        
        print(f"\n📊 Total messages: {total_messages}")
        
        # Проверяем пользователей
        users = User.query.all()
        print(f"\n👥 Found {len(users)} users:")
        for user in users:
            print(f"  - {user.first_name} {user.last_name} ({user.email}) - {user.role}")
        
        return True

def main():
    """Основная функция"""
    print("🚀 Check Messages Script")
    print("=" * 50)
    
    success = check_messages()
    
    if success:
        print("✅ Script completed successfully!")
        sys.exit(0)
    else:
        print("❌ Script failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
