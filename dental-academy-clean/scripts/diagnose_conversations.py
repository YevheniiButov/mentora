#!/usr/bin/env python3
"""
Диагностический скрипт для выяснения проблем с переписками
"""

import os
import sys

# Add the project root to the sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app import app
from extensions import db
from models import ForumTopic, ForumPost, User

def diagnose_conversations():
    """Диагностика проблем с переписками"""
    print("🔍 Diagnosing conversation issues...")
    
    with app.app_context():
        try:
            db.session.execute(db.text("SELECT 1"))
            print("✅ Database connection successful")
        except Exception as e:
            print(f"❌ Database connection failed: {str(e)}")
            return False

        # 1. Проверяем пользователей
        print("\n👥 CHECKING USERS:")
        all_users = User.query.all()
        print(f"Total users: {len(all_users)}")
        
        active_users = User.query.filter_by(is_active=True).all()
        print(f"Active users: {len(active_users)}")
        
        if len(active_users) < 3:
            print("❌ Not enough active users!")
            return False
        
        print("Active users:")
        for user in active_users[:5]:  # Показываем первых 5
            print(f"  - {user.first_name} {user.last_name} ({user.email}) - ID: {user.id}")
        
        # 2. Проверяем темы
        print("\n📋 CHECKING TOPICS:")
        target_topics = [
            'AKV tandartsen - BIG Registration Discussion 🦷',
            'General Chat - Let\'s talk about everything! 💬'
        ]
        
        for topic_title in target_topics:
            topic = ForumTopic.query.filter_by(title=topic_title).first()
            if topic:
                print(f"✅ Found: '{topic.title}' (ID: {topic.id})")
                print(f"   Author ID: {topic.author_id}")
                print(f"   Replies count: {topic.replies_count}")
                print(f"   Created: {topic.created_at}")
                
                # Проверяем сообщения
                messages = ForumPost.query.filter_by(topic_id=topic.id).all()
                print(f"   Actual messages: {len(messages)}")
                
                if messages:
                    print("   Recent messages:")
                    for msg in messages[-3:]:  # Последние 3
                        author = User.query.get(msg.author_id)
                        author_name = f"{author.first_name} {author.last_name}" if author else f"User ID {msg.author_id}"
                        print(f"     - {author_name}: {msg.content[:50]}...")
            else:
                print(f"❌ Not found: '{topic_title}'")
        
        # 3. Проверяем все темы
        print("\n📊 ALL TOPICS:")
        all_topics = ForumTopic.query.all()
        print(f"Total topics: {len(all_topics)}")
        
        for topic in all_topics:
            messages_count = ForumPost.query.filter_by(topic_id=topic.id).count()
            print(f"  - '{topic.title}' - Replies: {topic.replies_count}, Actual: {messages_count}")
        
        # 4. Проверяем все сообщения
        print("\n💬 ALL MESSAGES:")
        all_posts = ForumPost.query.all()
        print(f"Total posts: {len(all_posts)}")
        
        if all_posts:
            print("Recent posts:")
            for post in all_posts[-5:]:  # Последние 5
                author = User.query.get(post.author_id)
                author_name = f"{author.first_name} {author.last_name}" if author else f"User ID {post.author_id}"
                topic = ForumTopic.query.get(post.topic_id)
                topic_title = topic.title if topic else f"Topic ID {post.topic_id}"
                print(f"  - {author_name} in '{topic_title}': {post.content[:50]}...")
        
        return True

def main():
    """Основная функция"""
    print("🚀 Diagnose Conversations")
    print("=" * 50)
    
    success = diagnose_conversations()
    
    if success:
        print("✅ Diagnosis completed successfully!")
        sys.exit(0)
    else:
        print("❌ Diagnosis failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
