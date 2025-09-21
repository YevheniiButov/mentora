#!/usr/bin/env python3
"""
Скрипт для исправления авторов сообщений
"""

import os
import sys

# Add the project root to the sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app import app
from extensions import db
from models import ForumTopic, ForumPost, User

def fix_message_authors():
    """Исправляет авторов сообщений"""
    print("🔍 Fixing message authors...")
    
    with app.app_context():
        try:
            db.session.execute(db.text("SELECT 1"))
            print("✅ Database connection successful")
        except Exception as e:
            print(f"❌ Database connection failed: {str(e)}")
            return False

        # Получаем админа
        admin_user = User.query.filter_by(role='admin').first()
        if not admin_user:
            print("❌ Admin user not found!")
            return False
        
        print(f"✅ Found admin: {admin_user.first_name} {admin_user.last_name} (ID: {admin_user.id})")
        
        # Получаем всех пользователей
        all_users = User.query.all()
        print(f"📊 Total users in database: {len(all_users)}")
        
        # Проверяем сообщения с несуществующими авторами
        all_posts = ForumPost.query.all()
        print(f"📊 Total posts in database: {len(all_posts)}")
        
        fixed_count = 0
        for post in all_posts:
            author = User.query.get(post.author_id)
            if not author:
                print(f"❌ Post {post.id} has invalid author_id: {post.author_id}")
                # Исправляем на админа
                post.author_id = admin_user.id
                db.session.add(post)
                fixed_count += 1
                print(f"✅ Fixed post {post.id} author to admin")
        
        if fixed_count > 0:
            db.session.commit()
            print(f"🎉 Fixed {fixed_count} posts with invalid authors")
        else:
            print("✅ All posts have valid authors")
        
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
            
            messages = ForumPost.query.filter_by(topic_id=topic.id).order_by(ForumPost.created_at).all()
            print(f"📝 Topic has {len(messages)} messages")
            
            # Обновляем replies_count
            topic.replies_count = len(messages)
            db.session.add(topic)
            
            for i, msg in enumerate(messages):
                author = User.query.get(msg.author_id)
                if author:
                    print(f"  {i+1}. {author.first_name}: {msg.content[:50]}...")
                else:
                    print(f"  {i+1}. INVALID AUTHOR (ID: {msg.author_id}): {msg.content[:50]}...")
        
        db.session.commit()
        print("\n🎉 Author fix completed!")
        return True

def main():
    """Основная функция"""
    print("🚀 Fix Message Authors")
    print("=" * 50)
    
    success = fix_message_authors()
    
    if success:
        print("✅ Script completed successfully!")
        sys.exit(0)
    else:
        print("❌ Script failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
