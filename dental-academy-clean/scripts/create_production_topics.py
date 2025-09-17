#!/usr/bin/env python3
"""
Скрипт для создания готовых тем в сообществе для продакшена
"""

import os
import sys
from datetime import datetime

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, ForumCategory, ForumTopic, ForumPost, User

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
            
            # Находим первого пользователя (админа)
            admin_user = User.query.filter_by(is_admin=True).first()
            if not admin_user:
                admin_user = User.query.first()
            
            if not admin_user:
                print("❌ No users found! Please create a user first.")
                return
            
            print(f"✅ Найден пользователь: {admin_user.email}")
            
            # Создаем темы
            topics_data = [
                # General Discussion
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
                    'author': admin_user
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
            for topic_data in topics_data:
                # Проверяем, не существует ли уже такая тема
                existing_topic = ForumTopic.query.filter_by(
                    title=topic_data['title'],
                    author_id=admin_user.id
                ).first()
                
                if not existing_topic:
                    topic = ForumTopic(
                        title=topic_data['title'],
                        content=topic_data['content'],
                        category_id=topic_data['category'].id,
                        author_id=topic_data['author'].id,
                        status='active',
                        is_sticky=False,
                        is_locked=False,
                        views_count=0,
                        replies_count=0,
                        likes_count=0,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
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
