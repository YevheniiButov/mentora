#!/usr/bin/env python3
"""
Исправленный скрипт для создания готовых тем в сообществе для продакшена
Работает с PostgreSQL на Render
"""

import os
import sys
from datetime import datetime, timedelta
import random

def create_production_topics():
    """Создает темы через Flask приложение (для PostgreSQL)"""
    
    try:
        # Добавляем путь к проекту
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_root)
        
        # Импортируем Flask приложение
        from app import app
        from extensions import db
        from models import ForumCategory, ForumTopic, ForumPost, User
        
        print("🔍 Checking database connection...")
        
        with app.app_context():
            # Проверяем подключение к БД
            try:
                db.session.execute(db.text("SELECT 1"))
                print("✅ Database connection successful")
            except Exception as e:
                print(f"❌ Database connection failed: {str(e)}")
                return False
            
            # Находим или создаем категорию
            category = ForumCategory.query.filter_by(slug='general').first()
            
            if not category:
                print("📁 Creating general category...")
                category = ForumCategory(
                    name='General Discussion',
                    slug='general',
                    description='General discussions about BIG registration',
                    is_active=True,
                    order_num=1
                )
                db.session.add(category)
                db.session.commit()
                print(f"✅ Created category with ID: {category.id}")
            else:
                print(f"✅ Found category: {category.name}")
            
            # Находим пользователя-админа
            admin_user = User.query.filter_by(role='admin').first()
            
            if not admin_user:
                admin_user = User.query.first()
            
            if not admin_user:
                print("❌ No users found! Please create a user first.")
                return False
            
            print(f"✅ Found admin user: {admin_user.email}")
            
            # Создаем фейковых пользователей
            fake_users = [
                ('Maria', 'maria@example.com'),
                ('Ahmed', 'ahmed@example.com'),
                ('Priya', 'priya@example.com'),
                ('Carlos', 'carlos@example.com'),
                ('Anna', 'anna@example.com'),
                ('Lucas', 'lucas@example.com'),
                ('Emma', 'emma@example.com'),
                ('Alex', 'alex@example.com'),
                ('David', 'david@example.com')
            ]
            
            user_ids = {}
            for name, email in fake_users:
                user = User.query.filter_by(email=email).first()
                
                if not user:
                    print(f"👤 Creating fake user: {name}")
                    user = User(
                        email=email,
                        first_name=name,
                        last_name='',
                        role='user',
                        is_active=True,
                        created_at=datetime.now() - timedelta(days=random.randint(30, 90))
                    )
                    db.session.add(user)
                    db.session.commit()
                    user_ids[name] = user.id
                else:
                    user_ids[name] = user.id
                    print(f"⏭️ User already exists: {name}")
            
            # ВАШИ ОРИГИНАЛЬНЫЕ ТЕМЫ С ПЕРЕПИСКАМИ
            base_date = datetime(2025, 9, 1)
            
            topics_data = [
                {
                    'title': 'AKV tandartsen - BIG Registration Discussion 🦷',
                    'content': 'Discussion about AKV tests and BIG registration process for dentists. Share your experiences and get help from the community!',
                    'messages': [
                        ('Maria', 'Goedemorgen collega\'s, Ik heb een vraag, moeten we alle documenten bij BiG inleveren voordat we de AKV-toetsen afleggen, of moeten we eerst de tests afleggen?', 0, 9, 23),
                        ('Priya', 'Volgens mij kun je het beste eerst de taaltoets doen en daarna de documenten samen met het taalcertificaat opsturen.', 0, 9, 45),
                        ('Maria', 'Bedankt!', 0, 14, 12),
                        ('Ahmed', 'Hallo er bestaat geen akv test meer 👍', 0, 14, 28),
                        ('Maria', 'Hoe bedoel je?', 0, 14, 31),
                        ('Carlos', 'In plaats van AKV toets, moeten we nu B2+ taal certificaat halen en alle documenten naar CIBG sturen. Daarna krijgen we een datum voor BI-toets', 0, 14, 47),
                        ('Maria', 'Maar als we slagen voor de BGB en of Babel examens, dan wordt dat beschouwd als een B2+ certificaat? Krijgen we een certificaat van hun?', 0, 16, 19),
                        ('Anna', 'Inderdaad', 0, 16, 32),
                        ('Maria', 'Bedankt!', 0, 18, 15)
                    ]
                },
                {
                    'title': 'General Chat - Let\'s talk about everything! 💬',
                    'content': 'This is a general discussion thread where you can talk about anything - from your day to your experiences in the Netherlands, or just have a casual conversation with fellow healthcare professionals!',
                    'messages': [
                        ('Emma', 'Dankjewel!', 1, 9, 17),
                        ('Lucas', 'Deze krijg ik net binnen...', 1, 9, 34),
                        ('Alex', 'не за что', 1, 15, 22),
                        ('David', 'Missed voice call', 2, 11, 8)
                    ]
                },
                {
                    'title': 'Welcome to Mentora Community! 👋',
                    'content': 'Welcome to our community! This is a place where international healthcare professionals can share experiences, ask questions, and support each other on their journey to BIG registration in the Netherlands.\n\nFeel free to introduce yourself and share your background!',
                    'messages': []
                },
                {
                    'title': 'BIG Registration Process - Share Your Experience 📋',
                    'content': 'Share your experience with the BIG registration process! What challenges did you face? What tips do you have for others? Let\'s help each other navigate this complex process.',
                    'messages': []
                },
                {
                    'title': 'Living in the Netherlands - Tips & Experiences 🇳🇱',
                    'content': 'Share your experiences living in the Netherlands! Housing, transportation, culture, language learning - anything that might help newcomers adapt to life in the Netherlands.',
                    'messages': []
                },
                {
                    'title': 'BIG Exam Study Materials & Resources 📚',
                    'content': 'Share and discuss study materials, resources, and preparation strategies for the BIG exam. What worked for you? What resources do you recommend?',
                    'messages': []
                },
                {
                    'title': 'Practice Questions & Mock Exams 🧠',
                    'content': 'Practice makes perfect! Share practice questions, discuss mock exams, and help each other prepare for the BIG exam.',
                    'messages': []
                },
                {
                    'title': 'Language Learning Resources - Dutch & English 🗣️',
                    'content': 'Language is key to success! Share resources, tips, and experiences learning Dutch and English for healthcare professionals.',
                    'messages': []
                },
                {
                    'title': 'Medical Terminology & Translation Help 🏥',
                    'content': 'Need help with medical terminology? Share translation resources, ask questions, and help each other with medical Dutch and English terms.',
                    'messages': []
                },
                {
                    'title': 'Document Translation & Legalization Help 📄',
                    'content': 'Navigating document requirements can be tricky. Share experiences with translation services, legalization processes, and document requirements.',
                    'messages': []
                },
                {
                    'title': 'Job Search & Career Advice 💼',
                    'content': 'Looking for healthcare jobs in the Netherlands? Share job opportunities, career advice, and experiences with the Dutch healthcare job market.',
                    'messages': []
                },
                {
                    'title': 'Technical Support & Platform Help 🛠️',
                    'content': 'Having trouble with the platform? Need help with features? This is the place to ask for technical support and platform assistance.',
                    'messages': []
                },
                {
                    'title': 'Success Stories & Motivation 🌟',
                    'content': 'Share your success stories! Whether you\'ve passed the BIG exam, found a job, or achieved any milestone in your journey, inspire others with your story!',
                    'messages': []
                }
            ]
            
            created_count = 0
            
            for i, topic_data in enumerate(topics_data):
                # Проверяем, не существует ли уже такая тема
                existing_topic = ForumTopic.query.filter_by(title=topic_data['title']).first()
                if existing_topic:
                    print(f"⏭️ Topic already exists: {topic_data['title']}")
                    continue
                
                # Создаем тему
                topic_date = base_date + timedelta(days=i*2)
                
                topic = ForumTopic(
                    title=topic_data['title'],
                    content=topic_data['content'],
                    category_id=category.id,
                    author_id=admin_user.id,  # ВСЕ ТЕМЫ ОТ ADMIN USER
                    status='active',
                    is_sticky=False,
                    is_locked=False,
                    views_count=random.randint(50, 200),
                    replies_count=len(topic_data['messages']),
                    likes_count=random.randint(5, 25),
                    created_at=topic_date,
                    updated_at=topic_date + timedelta(days=random.randint(1, 5))
                )
                
                db.session.add(topic)
                db.session.commit()
                
                # Создаем сообщения
                for message_data in topic_data['messages']:
                    author_name, content, day_offset, hour, minute = message_data
                    author_id = user_ids.get(author_name, admin_user.id)
                    
                    message_date = topic_date + timedelta(days=day_offset, hours=hour, minutes=minute)
                    
                    post = ForumPost(
                        topic_id=topic.id,
                        author_id=author_id,
                        content=content,
                        created_at=message_date,
                        updated_at=message_date
                    )
                    
                    db.session.add(post)
                
                db.session.commit()
                created_count += 1
                print(f"✅ Created topic: {topic_data['title']}")
            
            print(f"\n🎉 Successfully created {created_count} topics!")
            return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция"""
    print("🚀 Production Topic Creator (Fixed)")
    print("=" * 50)
    
    success = create_production_topics()
    
    if success:
        print("✅ Script completed successfully!")
        sys.exit(0)
    else:
        print("❌ Script failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
