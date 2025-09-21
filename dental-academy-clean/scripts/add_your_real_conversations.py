#!/usr/bin/env python3
"""
Скрипт для добавления реальных переписок пользователя из create_production_topics.py
"""

import os
import sys
from datetime import datetime, timedelta
import random

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, ForumCategory, ForumTopic, ForumPost, User

def get_your_real_conversations():
    """Возвращает реальные переписки из вашего оригинального скрипта"""
    
    # Находим категории
    general_category = ForumCategory.query.filter_by(slug='general').first()
    if not general_category:
        print("❌ General category not found!")
        return None
    
    # Находим или создаем фейковых пользователей
    fake_users = []
    user_names = ['Maria', 'Ahmed', 'Priya', 'Carlos', 'Anna', 'Lucas', 'Emma', 'Alex', 'David']
    
    for name in user_names:
        # Ищем пользователя по имени
        user = User.query.filter(User.first_name.ilike(f'%{name}%')).first()
        if not user:
            # Создаем нового пользователя
            user = User(
                email=f'{name.lower()}@example.com',
                first_name=name,
                last_name='',
                role='user',
                is_active=True,
                created_at=datetime.now() - timedelta(days=random.randint(30, 90))
            )
            db.session.add(user)
            print(f"✅ Created user: {name}")
        else:
            print(f"⏭️ User exists: {name}")
        fake_users.append(user)
    
    db.session.commit()
    
    # Находим админа
    admin_user = User.query.filter_by(is_admin=True).first()
    if not admin_user:
        admin_user = User.query.first()
    
    if not admin_user:
        print("❌ No admin user found!")
        return None
    
    print(f"✅ Using admin: {admin_user.email}")
    
    # Ваши реальные переписки
    conversations_data = [
        {
            'topic_title': 'AKV tandartsen - BIG Registration Discussion 🦷',
            'topic_content': 'Discussion about AKV tests and BIG registration process for dentists. Share your experiences and get help from the community!',
            'category': general_category,
            'author': admin_user,
            'messages': [
                {
                    'author': 'Maria',
                    'content': 'Goedemorgen collega\'s, Ik heb een vraag, moeten we alle documenten bij BiG inleveren voordat we de AKV-toetsen afleggen, of moeten we eerst de tests afleggen?',
                    'day_offset': 0,
                    'hour': 9,
                    'minute': 23
                },
                {
                    'author': 'Priya',
                    'content': 'Volgens mij kun je het beste eerst de taaltoets doen en daarna de documenten samen met het taalcertificaat opsturen.',
                    'day_offset': 0,
                    'hour': 9,
                    'minute': 45
                },
                {
                    'author': 'Maria',
                    'content': 'Bedankt!',
                    'day_offset': 0,
                    'hour': 14,
                    'minute': 12
                },
                {
                    'author': 'Ahmed',
                    'content': 'Hallo er bestaat geen akv test meer 👍',
                    'day_offset': 0,
                    'hour': 14,
                    'minute': 28
                },
                {
                    'author': 'Maria',
                    'content': 'Hoe bedoel je?',
                    'day_offset': 0,
                    'hour': 14,
                    'minute': 31
                },
                {
                    'author': 'Carlos',
                    'content': 'In plaats van AKV toets, moeten we nu B2+ taal certificaat halen en alle documenten naar CIBG sturen. Daarna krijgen we een datum voor BI-toets',
                    'day_offset': 0,
                    'hour': 14,
                    'minute': 47
                },
                {
                    'author': 'Maria',
                    'content': 'Maar als we slagen voor de BGB en of Babel examens, dan wordt dat beschouwd als een B2+ certificaat? Krijgen we een certificaat van hun?',
                    'day_offset': 0,
                    'hour': 16,
                    'minute': 19
                },
                {
                    'author': 'Anna',
                    'content': 'Maar als we slagen voor de BGB en of Babel examens, dan wordt dat beschouwd als een B2+ certificaat? Krijgen we een certificaat van hun?',
                    'day_offset': 0,
                    'hour': 16,
                    'minute': 30
                },
                {
                    'author': 'Anna',
                    'content': 'Inderdaad',
                    'day_offset': 0,
                    'hour': 16,
                    'minute': 32
                },
                {
                    'author': 'Maria',
                    'content': 'Bedankt!',
                    'day_offset': 0,
                    'hour': 18,
                    'minute': 15
                }
            ]
        },
        {
            'topic_title': 'General Chat - Let\'s talk about everything! 💬',
            'topic_content': 'This is a general discussion thread where you can talk about anything - from your day to your experiences in the Netherlands, or just have a casual conversation with fellow healthcare professionals!',
            'category': general_category,
            'author': admin_user,
            'messages': [
                {
                    'author': 'Emma',
                    'content': 'Dankjewel!',
                    'day_offset': 1,
                    'hour': 9,
                    'minute': 17
                },
                {
                    'author': 'Lucas',
                    'content': 'Deze krijg ik net binnen...',
                    'day_offset': 1,
                    'hour': 9,
                    'minute': 34
                },
                {
                    'author': 'Alex',
                    'content': 'не за что',
                    'day_offset': 1,
                    'hour': 15,
                    'minute': 22
                },
                {
                    'author': 'David',
                    'content': 'Missed voice call',
                    'day_offset': 2,
                    'hour': 11,
                    'minute': 8
                }
            ]
        }
    ]
    
    return conversations_data, fake_users, admin_user

def add_real_conversations():
    """Добавляет реальные переписки пользователя"""
    
    with app.app_context():
        try:
            print("🔍 Getting your real conversations...")
            
            # Получаем данные
            result = get_your_real_conversations()
            if not result:
                return
            
            conversations_data, fake_users, admin_user = result
            
            # Базовая дата
            base_date = datetime(2025, 9, 20)  # 20 сентября 2025
            
            for i, conv_data in enumerate(conversations_data):
                print(f"\n📝 Processing conversation {i+1}: {conv_data['topic_title']}")
                
                # Ищем тему
                topic = ForumTopic.query.filter_by(title=conv_data['topic_title']).first()
                if not topic:
                    print(f"❌ Topic not found: {conv_data['topic_title']}")
                    continue
                
                print(f"✅ Found topic: {topic.title}")
                
                # Удаляем существующие сообщения в этой теме
                existing_posts = ForumPost.query.filter_by(topic_id=topic.id).all()
                for post in existing_posts:
                    db.session.delete(post)
                print(f"🗑️ Deleted {len(existing_posts)} existing posts")
                
                # Добавляем новые сообщения
                topic_date = base_date + timedelta(days=i)
                
                for j, message_data in enumerate(conv_data['messages']):
                    # Находим автора
                    author = None
                    for user in fake_users:
                        if user.first_name == message_data['author']:
                            author = user
                            break
                    
                    if not author:
                        print(f"⚠️ Author not found: {message_data['author']}, using first available")
                        author = fake_users[0]
                    
                    # Создаем время сообщения
                    hour = message_data.get('hour', 10)
                    minute = message_data.get('minute', random.randint(0, 59))
                    message_date = topic_date + timedelta(
                        days=message_data['day_offset'], 
                        hours=hour, 
                        minutes=minute
                    )
                    
                    # Создаем сообщение
                    post = ForumPost(
                        topic_id=topic.id,
                        author_id=author.id,
                        content=message_data['content'],
                        created_at=message_date,
                        updated_at=message_date
                    )
                    
                    db.session.add(post)
                    print(f"  ✅ Added message from {message_data['author']}: {message_data['content'][:50]}...")
                
                # Обновляем счетчик сообщений в теме
                topic.replies_count = len(conv_data['messages'])
                topic.updated_at = datetime.now()
                
                print(f"📊 Topic '{topic.title}' now has {topic.replies_count} messages")
            
            # Сохраняем изменения
            db.session.commit()
            
            print(f"\n🎉 Successfully added your real conversations!")
            print(f"📊 Total posts in database: {ForumPost.query.count()}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding conversations: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    add_real_conversations()
