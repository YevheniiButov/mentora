#!/usr/bin/env python3
"""
Скрипт для добавления сообщений в существующие темы
"""

import os
import sys

def add_messages_to_topics():
    """Добавляет сообщения в существующие темы"""
    
    try:
        # Добавляем путь к проекту
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_root)
        
        # Импортируем Flask приложение
        from app import app
        from extensions import db
        from models import ForumCategory, ForumTopic, ForumPost, User
        from datetime import datetime, timedelta
        import random
        
        print("🔍 Adding messages to existing topics...")
        
        with app.app_context():
            # Проверяем подключение к БД
            try:
                db.session.execute(db.text("SELECT 1"))
                print("✅ Database connection successful")
            except Exception as e:
                print(f"❌ Database connection failed: {str(e)}")
                return False
            
            # Находим пользователей для сообщений
            users = User.query.filter_by(is_active=True).limit(10).all()
            if len(users) < 3:
                print("❌ Not enough users for messages")
                return False
            
            print(f"✅ Found {len(users)} users for messages")
            
            # Находим темы без сообщений
            topics_without_messages = ForumTopic.query.filter(
                ~ForumTopic.posts.any()
            ).limit(5).all()
            
            print(f"📝 Found {len(topics_without_messages)} topics without messages")
            
            # Сообщения для разных тем
            messages_data = {
                'BIG Exam Study Materials & Resources 📚': [
                    "Hi everyone! I'm preparing for the BIG exam and looking for study materials. Any recommendations?",
                    "I found this great resource: [link]. It helped me a lot with the medical terminology.",
                    "Thanks for sharing! I'll check it out.",
                    "Has anyone taken the exam recently? What was it like?",
                    "I took it last month. The questions were quite challenging but fair."
                ],
                'Practice Questions & Mock Exams 🧠': [
                    "Does anyone know where I can find practice questions for the BIG exam?",
                    "There are some good mock exams on the official website.",
                    "I've been using the Mentora platform - it has excellent practice tests.",
                    "How often should I practice? I'm taking the exam in 3 months.",
                    "I'd recommend daily practice, at least 30 minutes per day."
                ],
                'Language Learning Resources - Dutch & English 🗣️': [
                    "I need to improve my Dutch for the exam. Any good resources?",
                    "Duolingo is great for basics, but for medical Dutch you need specialized courses.",
                    "I'm taking a medical Dutch course at the local university. It's very helpful.",
                    "What about English? Is the exam in English or Dutch?",
                    "The exam is in Dutch, but you can use English-Dutch medical dictionaries."
                ],
                'Living in the Netherlands - Tips & Experiences 🇳🇱': [
                    "I'm moving to the Netherlands next month. Any tips for newcomers?",
                    "Get your BSN number as soon as possible - you'll need it for everything.",
                    "The healthcare system is different here. Make sure you understand how it works.",
                    "I've been here for 2 years. The work-life balance is amazing!",
                    "Don't forget to register with a GP (huisarts) when you arrive."
                ],
                'Job Search & Career Advice 💼': [
                    "I'm looking for medical jobs in the Netherlands. Any advice?",
                    "LinkedIn is very popular here for professional networking.",
                    "Make sure your CV follows Dutch standards - it's different from other countries.",
                    "I found my job through a recruitment agency. They were very helpful.",
                    "The interview process can be quite lengthy - be patient!"
                ]
            }
            
            created_messages = 0
            
            for topic in topics_without_messages:
                if topic.title in messages_data:
                    print(f"\n📋 Adding messages to: '{topic.title}'")
                    
                    messages = messages_data[topic.title]
                    base_time = topic.created_at
                    
                    for i, message_text in enumerate(messages):
                        # Выбираем случайного пользователя
                        author = random.choice(users)
                        
                        # Время сообщения - через несколько часов после создания темы
                        message_time = base_time + timedelta(hours=i*2, minutes=random.randint(0, 59))
                        
                        # Создаем сообщение
                        post = ForumPost(
                            topic_id=topic.id,
                            author_id=author.id,
                            content=message_text,
                            created_at=message_time,
                            updated_at=message_time
                        )
                        
                        db.session.add(post)
                        created_messages += 1
                        print(f"  ✅ Added message by {author.first_name}: {message_text[:50]}...")
                    
                    # Обновляем счетчик ответов в теме
                    topic.replies_count = len(messages)
                    topic.updated_at = base_time + timedelta(hours=len(messages)*2)
            
            db.session.commit()
            print(f"\n🎉 Successfully added {created_messages} messages to topics!")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция"""
    print("🚀 Add Messages to Topics")
    print("=" * 50)
    
    success = add_messages_to_topics()
    
    if success:
        print("✅ Script completed successfully!")
        sys.exit(0)
    else:
        print("❌ Script failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
