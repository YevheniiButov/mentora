#!/usr/bin/env python3
"""
Максимально простой скрипт для добавления переписок.
"""

import os
import sys
from datetime import datetime, timedelta

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, ForumTopic, ForumPost, User

def add_simple_conversations():
    """Добавляет простые переписки"""
    
    with app.app_context():
        try:
            print("🔍 Starting simple conversations...")
            
            # Находим любого пользователя
            user = User.query.first()
            if not user:
                print("❌ No users found!")
                return
            
            print(f"✅ Using user: {user.email}")

            # Получаем все темы
            topics = ForumTopic.query.all()
            print(f"📋 Found {len(topics)} topics")
            
            if not topics:
                print("❌ No topics found!")
                return

            # Простые сообщения
            simple_messages = [
                "Hello everyone!",
                "Great topic!",
                "Thanks for sharing!",
                "Very helpful!",
                "I agree!",
                "Good point!",
                "Thanks for the info!",
                "This is useful!",
                "I have the same question!",
                "Great discussion!"
            ]

            base_date = datetime(2025, 1, 15)

            for i, topic in enumerate(topics):
                print(f"\n📝 Processing topic {i+1}: {topic.title}")
                
                # Удаляем старые сообщения
                ForumPost.query.filter_by(topic_id=topic.id).delete()
                db.session.commit()
                
                # Добавляем 3-5 простых сообщений
                num_messages = 3 + (i % 3)  # 3-5 сообщений
                
                for j in range(num_messages):
                    message_date = base_date + timedelta(minutes=j*5)
                    
                    post = ForumPost(
                        topic_id=topic.id,
                        author_id=user.id,
                        content=simple_messages[j % len(simple_messages)],
                        created_at=message_date,
                        updated_at=message_date
                    )
                    db.session.add(post)
                    print(f"  ✅ Added message {j+1}: {simple_messages[j % len(simple_messages)]}")
                
                # Обновляем счетчик
                topic.replies_count = num_messages
                db.session.add(topic)
                db.session.commit()
                print(f"📊 Topic now has {num_messages} messages")
            
            print(f"\n🎉 Successfully added simple conversations!")
            print(f"📊 Total posts: {ForumPost.query.count()}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    add_simple_conversations()
