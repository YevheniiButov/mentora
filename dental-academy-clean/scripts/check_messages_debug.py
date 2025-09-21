#!/usr/bin/env python3
"""
Скрипт для детальной проверки сообщений в темах
"""

import os
import sys

# Add the project root to the sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app import app
from extensions import db
from models import ForumTopic, ForumPost, User

def check_messages_debug():
    """Детальная проверка сообщений в темах"""
    print("🔍 Detailed messages check...")
    
    with app.app_context():
        try:
            db.session.execute(db.text("SELECT 1"))
            print("✅ Database connection successful")
        except Exception as e:
            print(f"❌ Database connection failed: {str(e)}")
            return False

        # Проверяем конкретные темы
        target_topics = [
            'AKV tandartsen - BIG Registration Discussion 🦷',
            'General Chat - Let\'s talk about everything! 💬'
        ]
        
        for topic_title in target_topics:
            print(f"\n📋 Checking topic: '{topic_title}'")
            
            topic = ForumTopic.query.filter_by(title=topic_title).first()
            if not topic:
                print(f"❌ Topic not found!")
                continue
            
            print(f"✅ Topic found: ID={topic.id}, Author ID={topic.author_id}")
            
            # Проверяем сообщения
            messages = ForumPost.query.filter_by(topic_id=topic.id).order_by(ForumPost.created_at).all()
            print(f"📝 Found {len(messages)} messages:")
            
            for i, msg in enumerate(messages):
                author = User.query.get(msg.author_id)
                author_name = f"{author.first_name} {author.last_name}" if author else f"User ID {msg.author_id}"
                print(f"  {i+1}. {author_name}: {msg.content[:60]}...")
                print(f"     Created: {msg.created_at}, ID: {msg.id}")
            
            # Проверяем replies_count в теме
            print(f"📊 Topic replies_count: {topic.replies_count}")
            print(f"📊 Actual messages count: {len(messages)}")
            
            if topic.replies_count != len(messages):
                print(f"⚠️ MISMATCH: replies_count ({topic.replies_count}) != actual messages ({len(messages)})")
                # Исправляем
                topic.replies_count = len(messages)
                db.session.add(topic)
                print(f"✅ Fixed replies_count to {len(messages)}")
        
        db.session.commit()
        print("\n🎉 Check completed!")
        return True

def main():
    """Основная функция"""
    print("🚀 Messages Debug Check")
    print("=" * 50)
    
    success = check_messages_debug()
    
    if success:
        print("✅ Script completed successfully!")
        sys.exit(0)
    else:
        print("❌ Script failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
