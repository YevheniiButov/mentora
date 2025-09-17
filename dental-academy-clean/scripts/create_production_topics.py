#!/usr/bin/env python3
"""
Скрипт для создания готовых тем в сообществе для продакшена
"""

import os
import sys
from datetime import datetime, timedelta
import random

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, ForumCategory, ForumTopic, ForumPost, User

def create_fake_users():
    """Создает фейковых пользователей для сообщений"""
    fake_users = [
        {'name': 'Gabriella', 'email': 'gabriella@example.com'},
        {'name': 'Sina', 'email': 'sina@example.com'},
        {'name': 'Rinsy', 'email': 'rinsy@example.com'},
        {'name': 'S. Donmez', 'email': 'sdonmez@example.com'},
        {'name': 'Olga', 'email': 'olga@example.com'},
        {'name': 'Liliam', 'email': 'liliam@example.com'},
        {'name': 'Markell', 'email': 'markell@example.com'},
        {'name': 'Dr. Liza', 'email': 'drliza@example.com'},
        {'name': 'Vladimir', 'email': 'vladimir@example.com'},
        {'name': 'Denis', 'email': 'denis@example.com'}
    ]
    
    created_users = []
    for user_data in fake_users:
        # Проверяем, не существует ли уже пользователь
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
            print(f"⏭️ User already exists: {user_data['name']}")
    
    db.session.commit()
    return created_users

def create_topic_with_messages(topic_data, fake_users, base_date):
    """Создает тему с сообщениями"""
    # Создаем тему
    topic = ForumTopic(
        title=topic_data['title'],
        content=topic_data['content'],
        category_id=topic_data['category'].id,
        author_id=topic_data['author'].id,
        status='active',
        is_sticky=False,
        is_locked=False,
        views_count=random.randint(50, 200),
        replies_count=len(topic_data.get('messages', [])),
        likes_count=random.randint(5, 25),
        created_at=base_date,
        updated_at=base_date + timedelta(days=random.randint(1, 5))
    )
    
    db.session.add(topic)
    db.session.flush()  # Получаем ID темы
    
    # Создаем сообщения
    if 'messages' in topic_data:
        for i, message_data in enumerate(topic_data['messages']):
            # Находим пользователя по имени
            author = None
            for user in fake_users:
                if user.first_name == message_data['author']:
                    author = user
                    break
            
            if not author:
                author = fake_users[0]  # Fallback
            
            message_date = base_date + timedelta(days=message_data['day_offset'], hours=message_data.get('hour', 10))
            
            post = ForumPost(
                topic_id=topic.id,
                author_id=author.id,
                content=message_data['content'],
                created_at=message_date,
                updated_at=message_date
            )
            
            db.session.add(post)
    
    return topic

def create_production_topics():
    """Создает готовые темы для продакшена"""
    
    with app.app_context():
        try:
            print("🔍 Проверяем подключение к базе данных...")
            
            # Проверяем подключение
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            print("✅ Подключение к базе данных успешно")
            
            # Находим или создаем категории
            general_category = ForumCategory.query.filter_by(slug='general').first()
            if not general_category:
                general_category = ForumCategory(
                    name='General Discussion',
                    slug='general',
                    description='General discussions about BIG registration and healthcare in the Netherlands',
                    is_active=True,
                    order=1
                )
                db.session.add(general_category)
                print("✅ Создана категория: General Discussion")
            else:
                print("✅ Найдена категория: General Discussion")
            
            study_category = ForumCategory.query.filter_by(slug='study-materials').first()
            if not study_category:
                study_category = ForumCategory(
                    name='Study Materials',
                    slug='study-materials',
                    description='Share and discuss study materials for BIG exams',
                    is_active=True,
                    order=2
                )
                db.session.add(study_category)
                print("✅ Создана категория: Study Materials")
            else:
                print("✅ Найдена категория: Study Materials")
            
            support_category = ForumCategory.query.filter_by(slug='support').first()
            if not support_category:
                support_category = ForumCategory(
                    name='Support & Help',
                    slug='support',
                    description='Get help and support from the community',
                    is_active=True,
                    order=3
                )
                db.session.add(support_category)
                print("✅ Создана категория: Support & Help")
            else:
                print("✅ Найдена категория: Support & Help")
            
            # Сохраняем категории
            db.session.commit()
            
            # Создаем фейковых пользователей
            print("👥 Создаем фейковых пользователей...")
            fake_users = create_fake_users()
            
            # Находим первого пользователя (админа)
            admin_user = User.query.filter_by(is_admin=True).first()
            if not admin_user:
                admin_user = User.query.first()
            
            if not admin_user:
                print("❌ No users found! Please create a user first.")
                return
            
            print(f"✅ Найден пользователь: {admin_user.email}")
            
            # Создаем темы с сообщениями
            base_date = datetime(2025, 9, 1)  # 1 сентября 2025
            
            topics_data = [
                # General Discussion
                {
                    'title': 'AKV tandartsen - BIG Registration Discussion 🦷',
                    'content': 'Discussion about AKV tests and BIG registration process for dentists. Share your experiences and get help from the community!',
                    'category': general_category,
                    'author': admin_user,
                    'messages': [
                        {
                            'author': 'Gabriella',
                            'content': 'Goedemorgen collega\'s, Ik heb een vraag, moeten we alle documenten bij BiG inleveren voordat we de AKV-toetsen afleggen, of moeten we eerst de tests afleggen?',
                            'day_offset': 0,
                            'hour': 10
                        },
                        {
                            'author': 'Rinsy',
                            'content': 'Volgens mij kun je het beste eerst de taaltoets doen en daarna de documenten samen met het taalcertificaat opsturen.',
                            'day_offset': 0,
                            'hour': 10
                        },
                        {
                            'author': 'Gabriella',
                            'content': 'Bedankt!',
                            'day_offset': 0,
                            'hour': 14
                        },
                        {
                            'author': 'Sina',
                            'content': 'Hallo er bestaat geen akv test meer 👍',
                            'day_offset': 0,
                            'hour': 14
                        },
                        {
                            'author': 'Gabriella',
                            'content': 'Hoe bedoel je?',
                            'day_offset': 0,
                            'hour': 14
                        },
                        {
                            'author': 'S. Donmez',
                            'content': 'In plaats van AKV toets, moeten we nu B2+ taal certificaat halen en alle documenten naar CIBG sturen. Daarna krijgen we een datum voor BI-toets',
                            'day_offset': 0,
                            'hour': 14
                        },
                        {
                            'author': 'Gabriella',
                            'content': 'Maar als we slagen voor de BGB en of Babel examens, dan wordt dat beschouwd als een B2+ certificaat? Krijgen we een certificaat van hun?',
                            'day_offset': 0,
                            'hour': 16
                        },
                        {
                            'author': 'Olga',
                            'content': 'Maar als we slagen voor de BGB en of Babel examens, dan wordt dat beschouwd als een B2+ certificaat? Krijgen we een certificaat van hun?',
                            'day_offset': 0,
                            'hour': 16
                        },
                        {
                            'author': 'Olga',
                            'content': 'Inderdaad',
                            'day_offset': 0,
                            'hour': 16
                        },
                        {
                            'author': 'Gabriella',
                            'content': 'Bedankt!',
                            'day_offset': 0,
                            'hour': 18
                        }
                    ]
                },
                {
                    'title': 'Welcome to Mentora Community! 👋',
                    'content': 'Welcome to our community! This is a place where international healthcare professionals can share experiences, ask questions, and support each other on their journey to BIG registration in the Netherlands.\n\nFeel free to introduce yourself and share your background!',
                    'category': general_category,
                    'author': admin_user
                },
                {
                    'title': 'General Chat - Let\'s talk about everything! 💬',
                    'content': 'This is a general discussion thread where you can talk about anything - from your day to your experiences in the Netherlands, or just have a casual conversation with fellow healthcare professionals!',
                    'category': general_category,
                    'author': admin_user,
                    'messages': [
                        {
                            'author': 'Liliam',
                            'content': 'Dankjewel!',
                            'day_offset': 1,
                            'hour': 9
                        },
                        {
                            'author': 'Markell',
                            'content': 'Deze krijg ik net binnen...',
                            'day_offset': 1,
                            'hour': 9
                        },
                        {
                            'author': 'Vladimir',
                            'content': 'не за что',
                            'day_offset': 1,
                            'hour': 15
                        },
                        {
                            'author': 'Denis',
                            'content': 'Missed voice call',
                            'day_offset': 2,
                            'hour': 11
                        }
                    ]
                },
                {
                    'title': 'BIG Registration Process - Share Your Experience 📋',
                    'content': 'Share your experience with the BIG registration process! What challenges did you face? What tips do you have for others? Let\'s help each other navigate this complex process.',
                    'category': general_category,
                    'author': admin_user
                },
                {
                    'title': 'Living in the Netherlands - Tips & Experiences 🇳🇱',
                    'content': 'Share your experiences living in the Netherlands! Housing, transportation, culture, language learning - anything that might help newcomers adapt to life in the Netherlands.',
                    'category': general_category,
                    'author': admin_user
                },
                
                # Study Materials
                {
                    'title': 'BIG Exam Study Materials & Resources 📚',
                    'content': 'Share useful study materials, books, online courses, and resources for BIG exam preparation. What helped you the most in your studies?',
                    'category': study_category,
                    'author': admin_user
                },
                {
                    'title': 'Practice Questions & Mock Exams 🧠',
                    'content': 'Share practice questions, mock exams, and test your knowledge with fellow students. Let\'s prepare together for the BIG exam!',
                    'category': study_category,
                    'author': admin_user
                },
                {
                    'title': 'Language Learning Resources - Dutch & English 🗣️',
                    'content': 'Share resources for learning Dutch and improving your English. Language skills are crucial for BIG registration and working in the Netherlands.',
                    'category': study_category,
                    'author': admin_user
                },
                {
                    'title': 'Medical Terminology & Translation Help 🏥',
                    'content': 'Need help with medical terminology translation? Share difficult terms, ask for translations, and help others with medical language questions.',
                    'category': study_category,
                    'author': admin_user
                },
                
                # Support & Help
                {
                    'title': 'Document Translation & Legalization Help 📄',
                    'content': 'Get help with document translation, legalization, and notarization processes. Share your experiences and help others navigate these bureaucratic requirements.',
                    'category': support_category,
                    'author': admin_user
                },
                {
                    'title': 'Job Search & Career Advice 💼',
                    'content': 'Share job opportunities, career advice, and networking tips. Help each other find employment opportunities in the Dutch healthcare sector.',
                    'category': support_category,
                    'author': admin_user
                },
                {
                    'title': 'Technical Support & Platform Help 🛠️',
                    'content': 'Having trouble with the platform? Need help with registration, navigation, or any technical issues? Ask here and get help from the community!',
                    'category': support_category,
                    'author': admin_user
                },
                {
                    'title': 'Success Stories & Motivation 🌟',
                    'content': 'Share your success stories! Whether you\'ve passed the BIG exam, found a job, or achieved any milestone in your journey - inspire others with your achievements!',
                    'category': support_category,
                    'author': admin_user
                }
            ]
            
            created_count = 0
            for i, topic_data in enumerate(topics_data):
                # Проверяем, не существует ли уже такая тема
                existing_topic = ForumTopic.query.filter_by(
                    title=topic_data['title'],
                    author_id=admin_user.id
                ).first()
                
                if not existing_topic:
                    # Создаем тему с разными датами
                    topic_date = base_date + timedelta(days=i*2)  # Каждая тема через 2 дня
                    
                    if 'messages' in topic_data:
                        topic = create_topic_with_messages(topic_data, fake_users, topic_date)
                    else:
                        topic = ForumTopic(
                            title=topic_data['title'],
                            content=topic_data['content'],
                            category_id=topic_data['category'].id,
                            author_id=topic_data['author'].id,
                            status='active',
                            is_sticky=False,
                            is_locked=False,
                            views_count=random.randint(20, 100),
                            replies_count=0,
                            likes_count=random.randint(2, 15),
                            created_at=topic_date,
                            updated_at=topic_date + timedelta(days=random.randint(1, 3))
                        )
                        db.session.add(topic)
                    
                    created_count += 1
                    print(f"✅ Created topic: {topic_data['title']}")
                else:
                    print(f"⏭️ Topic already exists: {topic_data['title']}")
            
            # Сохраняем изменения
            db.session.commit()
            
            print(f"\n🎉 Successfully created {created_count} topics!")
            print(f"📊 Total topics in database: {ForumTopic.query.count()}")
            print(f"📁 Categories: {ForumCategory.query.count()}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error creating topics: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    create_production_topics()
