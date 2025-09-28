#!/usr/bin/env python3
"""
Диагностический скрипт для проверки состояния переписок.
"""

import os
import sys
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, ForumTopic, ForumPost, User

def debug_conversations():
    """Диагностика состояния переписок"""
    
    with app.app_context():
        try:
            print("🔍 Starting conversation diagnostics...")
            
            # Проверяем пользователей
            users = User.query.all()
            print(f"👥 Total users: {len(users)}")
            for user in users[:5]:  # Показываем первых 5
                print(f"  - {user.first_name} {user.last_name} ({user.email}) - Role: {user.role}")
            
            # Проверяем темы
            topics = ForumTopic.query.all()
            print(f"\n📋 Total topics: {len(topics)}")
            
            # Проверяем сообщения
            posts = ForumPost.query.all()
            print(f"💬 Total posts: {len(posts)}")
            
            # Проверяем сообщения по темам
            print(f"\n📊 Posts per topic:")
            for topic in topics:
                topic_posts = ForumPost.query.filter_by(topic_id=topic.id).count()
                print(f"  - {topic.title}: {topic_posts} posts")
                
                # Показываем первые 2 сообщения в каждой теме
                if topic_posts > 0:
                    first_posts = ForumPost.query.filter_by(topic_id=topic.id).limit(2).all()
                    for post in first_posts:
                        author_name = post.author.first_name if post.author else "Unknown"
                        print(f"    * {author_name}: {post.content[:50]}...")
            
            # Проверяем последние сообщения
            print(f"\n🕒 Last 5 posts:")
            recent_posts = ForumPost.query.order_by(ForumPost.created_at.desc()).limit(5).all()
            for post in recent_posts:
                author_name = post.author.first_name if post.author else "Unknown"
                topic_title = post.topic.title if post.topic else "Unknown Topic"
                print(f"  - {author_name} in '{topic_title}': {post.content[:50]}...")
            
            print(f"\n✅ Diagnostics completed!")
            
        except Exception as e:
            print(f"❌ Error in diagnostics: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    debug_conversations()


