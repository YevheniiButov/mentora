#!/usr/bin/env python3
"""
Быстрая проверка сообщений в базе данных
"""

import os
import sys

def quick_check():
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_root)
        
        from app import app
        from extensions import db
        from models import ForumTopic, ForumPost
        
        with app.app_context():
            print("🔍 Quick check of messages...")
            
            # Проверяем все темы
            topics = ForumTopic.query.all()
            print(f"\n📋 Total topics: {len(topics)}")
            
            total_messages = 0
            for topic in topics:
                message_count = ForumPost.query.filter_by(topic_id=topic.id).count()
                total_messages += message_count
                status = "✅" if message_count > 0 else "❌"
                print(f"{status} '{topic.title}' - {message_count} messages")
            
            print(f"\n📊 Total messages in database: {total_messages}")
            
            # Проверяем конкретные темы
            akv_topic = ForumTopic.query.filter_by(title="AKV tandartsen - BIG Registration Discussion 🦷").first()
            if akv_topic:
                akv_messages = ForumPost.query.filter_by(topic_id=akv_topic.id).all()
                print(f"\n🦷 AKV Topic messages ({len(akv_messages)}):")
                for msg in akv_messages[:3]:
                    author = msg.author.first_name if msg.author else "Unknown"
                    print(f"  - {author}: {msg.content[:60]}...")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == '__main__':
    quick_check()
