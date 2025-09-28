#!/usr/bin/env python3
"""
Умный скрипт для добавления подходящих фейковых переписок в конкретные темы.
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

def add_smart_fake_conversations():
    """Добавляет подходящие фейковые переписки в конкретные темы"""
    
    with app.app_context():
        try:
            print("🔍 Starting to add smart fake conversations...")
            
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

            # Определяем переписки для конкретных тем
            topic_conversations = {
                # BIG Registration темы
                'AKV tandartsen - BIG Registration Discussion 🦷': [
                    {'author': 'Maria', 'content': 'Goedemorgen collega\'s, Ik heb een vraag, moeten we alle documenten bij BiG inleveren voordat we de AKV-toetsen afleggen, of moeten we eerst de tests afleggen?', 'delay_minutes': 0},
                    {'author': 'Priya', 'content': 'Volgens mij kun je het beste eerst de taaltoets doen en daarna de documenten samen met het taalcertificaat opsturen.', 'delay_minutes': 5},
                    {'author': 'Maria', 'content': 'Bedankt!', 'delay_minutes': 10},
                    {'author': 'Ahmed', 'content': 'Hallo er bestaat geen akv test meer 👍', 'delay_minutes': 15},
                    {'author': 'Maria', 'content': 'Hoe bedoel je?', 'delay_minutes': 18},
                    {'author': 'Carlos', 'content': 'In plaats van AKV toets, moeten we nu B2+ taal certificaat halen en alle documenten naar CIBG sturen. Daarna krijgen we een datum voor BI-toets', 'delay_minutes': 22},
                    {'author': 'Maria', 'content': 'Maar als we slagen voor de BGB en of Babel examens, dan wordt dat beschouwd als een B2+ certificaat? Krijgen we een certificaat van hun?', 'delay_minutes': 30},
                    {'author': 'Anna', 'content': 'Inderdaad', 'delay_minutes': 35},
                    {'author': 'Maria', 'content': 'Bedankt!', 'delay_minutes': 40}
                ],
                
                'BIG Registration Process - Share Your Experience 📋': [
                    {'author': 'Lucas', 'content': 'Hi everyone! I just completed my BIG registration process. Happy to share my experience if anyone has questions.', 'delay_minutes': 0},
                    {'author': 'Emma', 'content': 'That\'s great! How long did the whole process take for you?', 'delay_minutes': 5},
                    {'author': 'Lucas', 'content': 'About 3 months from start to finish. The language test was the longest part.', 'delay_minutes': 8},
                    {'author': 'Alex', 'content': 'What documents did you need to submit?', 'delay_minutes': 12},
                    {'author': 'Lucas', 'content': 'Diploma, transcripts, language certificate, and passport copy. All had to be translated and legalized.', 'delay_minutes': 15},
                    {'author': 'David', 'content': 'Thanks for sharing! This is really helpful.', 'delay_minutes': 20}
                ],
                
                # Study Materials темы
                'BIG Exam Study Materials & Resources 📚': [
                    {'author': 'Priya', 'content': 'Does anyone have good study materials for the BIG exam? I\'m looking for comprehensive resources.', 'delay_minutes': 0},
                    {'author': 'Ahmed', 'content': 'I used the official BIG study guide and some online courses. They were quite helpful.', 'delay_minutes': 5},
                    {'author': 'Carlos', 'content': 'There are some good YouTube channels with medical terminology in Dutch. Very useful for the language part.', 'delay_minutes': 8},
                    {'author': 'Anna', 'content': 'I found practice questions on the BIG website very helpful. They give you a good idea of the format.', 'delay_minutes': 12},
                    {'author': 'Priya', 'content': 'Thanks everyone! I\'ll check those out.', 'delay_minutes': 16}
                ],
                
                'Practice Questions & Mock Exams 🧠': [
                    {'author': 'Emma', 'content': 'Has anyone taken the practice exam recently? I\'m planning to take it next week.', 'delay_minutes': 0},
                    {'author': 'Lucas', 'content': 'Yes! I took it last week. It was quite challenging but very similar to the real exam.', 'delay_minutes': 3},
                    {'author': 'Alex', 'content': 'What topics should I focus on?', 'delay_minutes': 7},
                    {'author': 'David', 'content': 'Definitely anatomy and pharmacology. Those sections were heavy.', 'delay_minutes': 10},
                    {'author': 'Emma', 'content': 'Thanks for the tips! I\'ll focus on those areas.', 'delay_minutes': 14}
                ],
                
                # Language темы
                'Language Learning Resources - Dutch & English 🗣️': [
                    {'author': 'Maria', 'content': 'What\'s the best way to improve medical Dutch? I need to prepare for the language test.', 'delay_minutes': 0},
                    {'author': 'Ahmed', 'content': 'I recommend reading medical journals in Dutch and watching Dutch medical documentaries.', 'delay_minutes': 5},
                    {'author': 'Priya', 'content': 'There are some good apps for medical terminology. Also, try to practice with native speakers.', 'delay_minutes': 8},
                    {'author': 'Carlos', 'content': 'I found that working in a Dutch hospital really helped with the practical language skills.', 'delay_minutes': 12},
                    {'author': 'Maria', 'content': 'Great suggestions! Thank you all.', 'delay_minutes': 16}
                ],
                
                'Medical Terminology & Translation Help 🏥': [
                    {'author': 'Anna', 'content': 'Can someone help me translate this medical term: "bloeddruk"?', 'delay_minutes': 0},
                    {'author': 'Lucas', 'content': 'That\'s "blood pressure" in English.', 'delay_minutes': 2},
                    {'author': 'Emma', 'content': 'There\'s a good medical dictionary app that I use. Very helpful for quick translations.', 'delay_minutes': 5},
                    {'author': 'Alex', 'content': 'I can help with translations if needed. Just post the terms here.', 'delay_minutes': 8},
                    {'author': 'Anna', 'content': 'Thanks! I\'ll keep that in mind.', 'delay_minutes': 12}
                ],
                
                # Living in Netherlands
                'Living in the Netherlands - Tips & Experiences 🇳🇱': [
                    {'author': 'David', 'content': 'Hi! I\'m planning to move to the Netherlands soon. Any tips for finding accommodation?', 'delay_minutes': 0},
                    {'author': 'Maria', 'content': 'Start looking early! The housing market is quite competitive, especially in Amsterdam.', 'delay_minutes': 5},
                    {'author': 'Ahmed', 'content': 'Consider cities like Utrecht or Rotterdam. They\'re more affordable and still well-connected.', 'delay_minutes': 8},
                    {'author': 'Priya', 'content': 'Make sure you have all your documents ready. The registration process can take time.', 'delay_minutes': 12},
                    {'author': 'David', 'content': 'Thanks for the advice! I\'ll start looking soon.', 'delay_minutes': 16}
                ],
                
                # Job Search
                'Job Search & Career Advice 💼': [
                    {'author': 'Carlos', 'content': 'Any tips for finding dental jobs in the Netherlands? I\'m a recent graduate.', 'delay_minutes': 0},
                    {'author': 'Anna', 'content': 'LinkedIn is very important here. Also check the dental association job board.', 'delay_minutes': 5},
                    {'author': 'Lucas', 'content': 'Networking is key. Try to attend dental conferences and meet people in the field.', 'delay_minutes': 8},
                    {'author': 'Emma', 'content': 'Consider starting with temporary positions to gain experience and build connections.', 'delay_minutes': 12},
                    {'author': 'Carlos', 'content': 'Great advice! I\'ll start with LinkedIn and networking.', 'delay_minutes': 16}
                ],
                
                # Success Stories
                'Success Stories & Motivation 🌟': [
                    {'author': 'Alex', 'content': 'I just passed my BIG exam! 🎉 After 6 months of studying, it feels amazing!', 'delay_minutes': 0},
                    {'author': 'David', 'content': 'Congratulations! That\'s fantastic news! 🎊', 'delay_minutes': 2},
                    {'author': 'Maria', 'content': 'Well done! Any tips for those still preparing?', 'delay_minutes': 5},
                    {'author': 'Alex', 'content': 'Stay consistent with your study schedule and don\'t give up. It\'s worth it in the end!', 'delay_minutes': 8},
                    {'author': 'Priya', 'content': 'Thanks for the motivation! I needed to hear that today.', 'delay_minutes': 12}
                ],
                
                # Technical Support
                'Technical Support & Platform Help 🛠️': [
                    {'author': 'Emma', 'content': 'I\'m having trouble accessing the practice questions. Is anyone else experiencing this?', 'delay_minutes': 0},
                    {'author': 'Lucas', 'content': 'I had the same issue yesterday. Try clearing your browser cache.', 'delay_minutes': 3},
                    {'author': 'Alex', 'content': 'If that doesn\'t work, try using a different browser or incognito mode.', 'delay_minutes': 6},
                    {'author': 'David', 'content': 'You can also contact the support team. They\'re usually very responsive.', 'delay_minutes': 9},
                    {'author': 'Emma', 'content': 'Thanks! I\'ll try those suggestions.', 'delay_minutes': 12}
                ],
                
                # General Chat
                'General Chat - Let\'s talk about everything! 💬': [
                    {'author': 'Anna', 'content': 'How is everyone doing today?', 'delay_minutes': 0},
                    {'author': 'Lucas', 'content': 'Good! Just finished a long study session. How about you?', 'delay_minutes': 3},
                    {'author': 'Emma', 'content': 'Same here! The community is really helpful for staying motivated.', 'delay_minutes': 6},
                    {'author': 'Alex', 'content': 'Absolutely! It\'s great to have people going through the same journey.', 'delay_minutes': 9},
                    {'author': 'David', 'content': 'Couldn\'t agree more! Good luck everyone! 💪', 'delay_minutes': 12}
                ],
                
                # Welcome
                'Welcome to Mentora Community! 👋': [
                    {'author': 'Maria', 'content': 'Welcome everyone to our community! Feel free to ask questions and share experiences.', 'delay_minutes': 0},
                    {'author': 'Ahmed', 'content': 'Thanks for creating this space! It\'s great to connect with other dental professionals.', 'delay_minutes': 5},
                    {'author': 'Priya', 'content': 'I\'m excited to be part of this community. Looking forward to learning from everyone!', 'delay_minutes': 8},
                    {'author': 'Carlos', 'content': 'This is exactly what we needed. A supportive community for our BIG journey!', 'delay_minutes': 12},
                    {'author': 'Anna', 'content': 'Let\'s help each other succeed! 🎯', 'delay_minutes': 16}
                ]
            }

            base_date = datetime(2025, 1, 15) # Базовая дата для сообщений

            for topic in topics:
                print(f"\n📝 Processing topic: {topic.title}")
                
                # Удаляем все существующие посты в этой теме
                deleted_posts_count = ForumPost.query.filter_by(topic_id=topic.id).delete()
                db.session.commit()
                print(f"🗑️ Deleted {deleted_posts_count} existing posts")

                # Получаем переписку для этой темы
                conversation = topic_conversations.get(topic.title, [])
                
                if not conversation:
                    print(f"⚠️ No specific conversation found for topic: {topic.title}")
                    # Добавляем общую переписку для тем без специфической
                    conversation = [
                        {'author': 'Maria', 'content': 'Hello everyone! Thanks for creating this topic.', 'delay_minutes': 0},
                        {'author': 'Ahmed', 'content': 'Great topic! Looking forward to the discussion.', 'delay_minutes': 5},
                        {'author': 'Priya', 'content': 'I agree! This is very helpful.', 'delay_minutes': 10}
                    ]

                # Добавляем новые сообщения
                for message_data in conversation:
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
                topic.replies_count = len(conversation)
                db.session.add(topic)
                db.session.commit()
                print(f"📊 Topic '{topic.title}' now has {topic.replies_count} messages")
            
            print(f"\n🎉 Successfully added smart fake conversations to {len(topics)} topics!")
            print(f"📊 Total posts in database: {ForumPost.query.count()}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Error adding smart fake conversations: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    add_smart_fake_conversations()


