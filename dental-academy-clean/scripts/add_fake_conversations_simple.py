#!/usr/bin/env python3
"""
Простой скрипт для добавления фейковых переписок в существующие темы.
"""

import os
import sys
from datetime import datetime, timedelta
import random

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, ForumTopic, ForumPost, User

def create_fake_users_if_not_exists():
    """Создает фейковых пользователей для сообщений"""
    fake_users_data = [
        {'name': 'Maria', 'email': 'maria@example.com'},
        {'name': 'Ahmed', 'email': 'ahmed@example.com'},
        {'name': 'Priya', 'email': 'priya@example.com'},
        {'name': 'Carlos', 'email': 'carlos@example.com'},
        {'name': 'Anna', 'email': 'anna@example.com'},
        {'name': 'Lucas', 'email': 'lucas@example.com'},
        {'name': 'Emma', 'email': 'emma@example.com'},
        {'name': 'Alex', 'email': 'alex@example.com'},
        {'name': 'David', 'email': 'david@example.com'}
    ]
    
    created_users = []
    for user_data in fake_users_data:
        existing_user = User.query.filter_by(email=user_data['email']).first()
        if not existing_user:
            user = User(
                email=user_data['email'],
                first_name=user_data['name'],
                last_name='',
                role='user',
                is_active=True,
                created_at=datetime.now() - timedelta(days=random.randint(30, 90))
            )
            db.session.add(user)
            created_users.append(user)
            print(f"✅ Created fake user: {user_data['name']}")
        else:
            created_users.append(existing_user)
            print(f"⏭️ User exists: {user_data['name']}")
    
    db.session.commit()
    return created_users

def add_fake_conversations():
    """Добавляет фейковые переписки в существующие темы"""
    
    with app.app_context():
        try:
            print("🔍 Starting to add fake conversations...")
            
            # Создаем фейковых пользователей
            fake_users = create_fake_users_if_not_exists()
            
            # Находим админа
            admin_user = User.query.filter_by(role='admin').first()
            if not admin_user:
                admin_user = User.query.first() # Fallback to any user
            
            if not admin_user:
                print("❌ No admin user found! Cannot add conversations.")
                return
            
            print(f"✅ Using admin: {admin_user.email}")

            # Получаем все существующие темы
            topics = ForumTopic.query.all()
            print(f"📋 Found {len(topics)} existing topics")
            
            if not topics:
                print("❌ No topics found! Please create topics first.")
                return

            # Фейковые переписки для разных тем
            conversations = [
                {
                    'messages': [
                        {'author': 'Maria', 'content': 'Hello everyone! I have a question about the BIG registration process.', 'delay_minutes': 0},
                        {'author': 'Ahmed', 'content': 'Hi Maria! What specifically do you need help with?', 'delay_minutes': 5},
                        {'author': 'Priya', 'content': 'I can help! I went through the process last month.', 'delay_minutes': 8},
                        {'author': 'Maria', 'content': 'Great! Do I need to submit all documents before taking the tests?', 'delay_minutes': 12},
                        {'author': 'Carlos', 'content': 'No, you can take the language test first, then submit documents with the certificate.', 'delay_minutes': 15},
                        {'author': 'Maria', 'content': 'Perfect! Thank you for the clarification.', 'delay_minutes': 20}
                    ]
                },
                {
                    'messages': [
                        {'author': 'Anna', 'content': 'Has anyone taken the practice exam recently?', 'delay_minutes': 0},
                        {'author': 'Lucas', 'content': 'Yes! I took it last week. It was quite challenging.', 'delay_minutes': 3},
                        {'author': 'Emma', 'content': 'What topics should I focus on?', 'delay_minutes': 7},
                        {'author': 'Alex', 'content': 'Definitely anatomy and pharmacology. Those sections were heavy.', 'delay_minutes': 10},
                        {'author': 'David', 'content': 'I agree! Also practice the clinical scenarios.', 'delay_minutes': 14},
                        {'author': 'Anna', 'content': 'Thanks for the tips! I\'ll focus on those areas.', 'delay_minutes': 18}
                    ]
                },
                {
                    'messages': [
                        {'author': 'Maria', 'content': 'Congratulations to everyone who passed! 🎉', 'delay_minutes': 0},
                        {'author': 'Ahmed', 'content': 'Thank you! It was a long journey but worth it.', 'delay_minutes': 2},
                        {'author': 'Priya', 'content': 'Any job search tips for new graduates?', 'delay_minutes': 5},
                        {'author': 'Carlos', 'content': 'Network, network, network! LinkedIn is your friend.', 'delay_minutes': 8},
                        {'author': 'Anna', 'content': 'Also check out the dental association job board.', 'delay_minutes': 12},
                        {'author': 'Maria', 'content': 'Great advice! Good luck to everyone!', 'delay_minutes': 16}
                    ]
                }
            ]

            base_date = datetime(2025, 1, 15) # Базовая дата для сообщений
            conversation_index = 0

            for topic in topics:
                print(f"\n📝 Processing topic: {topic.title}")
                
                # Удаляем все существующие посты в этой теме
                deleted_posts_count = ForumPost.query.filter_by(topic_id=topic.id).delete()
                db.session.commit()
                print(f"🗑️ Deleted {deleted_posts_count} existing posts")

                # Выбираем переписку для этой темы
                conversation = conversations[conversation_index % len(conversations)]
                conversation_index += 1

                # Добавляем новые сообщения
                for message_data in conversation['messages']:
                    author = next((u for u in fake_users if u.first_name == message_data['author']), admin_user)
                    
                    # Создаем дату сообщения с задержкой
                    message_date = base_date + timedelta(minutes=message_data['delay_minutes'])
                    
                    post = ForumPost(
                        topic_id=topic.id,
                        author_id=author.id,
                        content=message_data['content'],
                        created_at=message_date,
                        updated_at=message_date
                    )
                    db.session.add(post)
                    print(f"  ✅ Added message from {author.first_name}: {message_data['content'][:50]}...")
                
                # Обновляем счетчик сообщений в теме
                topic.replies_count = len(conversation['messages'])
                db.session.add(topic)
                db.session.commit()
                print(f"📊 Topic '{topic.title}' now has {topic.replies_count} messages")
            
            print(f"\n🎉 Successfully added fake conversations to {len(topics)} topics!")
            print(f"📊 Total posts in database: {ForumPost.query.count()}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding fake conversations: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    add_fake_conversations()
