#!/usr/bin/env python3
"""
Скрипт для добавления ваших оригинальных переписок (работает как старый скрипт)
"""

import os
import sys

def add_your_conversations():
    """Добавляет ваши оригинальные переписки"""
    
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
        
        print("🔍 Adding your original conversations...")
        
        with app.app_context():
            # Проверяем подключение к БД
            try:
                db.session.execute(db.text("SELECT 1"))
                print("✅ Database connection successful")
            except Exception as e:
                print(f"❌ Database connection failed: {str(e)}")
                return False
            
            # Находим пользователей (как в старом скрипте)
            users = User.query.filter_by(is_active=True).limit(10).all()
            if len(users) < 3:
                print("❌ Not enough users for messages")
                return False
            
            print(f"✅ Found {len(users)} users for messages")
            for user in users:
                print(f"  - {user.first_name} {user.last_name} ({user.email})")
            
            # ВАШИ ОРИГИНАЛЬНЫЕ ПЕРЕПИСКИ
            conversations_data = {
                'AKV tandartsen - BIG Registration Discussion 🦷': [
                    "Goedemorgen collega's, Ik heb een vraag, moeten we alle documenten bij BiG inleveren voordat we de AKV-toetsen afleggen, of moeten we eerst de tests afleggen?",
                    "Volgens mij kun je het beste eerst de taaltoets doen en daarna de documenten samen met het taalcertificaat opsturen.",
                    "Bedankt!",
                    "Hallo er bestaat geen akv test meer 👍",
                    "Hoe bedoel je?",
                    "In plaats van AKV toets, moeten we nu B2+ taal certificaat halen en alle documenten naar CIBG sturen. Daarna krijgen we een datum voor BI-toets",
                    "Maar als we slagen voor de BGB en of Babel examens, dan wordt dat beschouwd als een B2+ certificaat? Krijgen we een certificaat van hun?",
                    "Inderdaad",
                    "Bedankt!"
                ],
                'General Chat - Let\'s talk about everything! 💬': [
                    "Dankjewel!",
                    "Deze krijg ik net binnen...",
                    "не за что",
                    "Missed voice call"
                ]
            }
            
            created_messages = 0
            
            # Ищем темы по названию (как в новых скриптах)
            for topic_title, messages in conversations_data.items():
                topic = ForumTopic.query.filter_by(title=topic_title).first()
                if not topic:
                    print(f"❌ Topic not found: {topic_title}")
                    continue
                
                print(f"\n📋 Adding messages to: '{topic.title}'")
                
                # Удаляем существующие сообщения (как в force скрипте)
                existing_messages = ForumPost.query.filter_by(topic_id=topic.id).all()
                if existing_messages:
                    print(f"🗑️ Deleting {len(existing_messages)} existing messages...")
                    for msg in existing_messages:
                        db.session.delete(msg)
                    db.session.commit()
                
                # Добавляем новые сообщения
                base_time = topic.created_at
                for i, message_text in enumerate(messages):
                    # Выбираем случайного пользователя (как в старом скрипте)
                    author = random.choice(users)
                    
                    # Время сообщения
                    message_time = base_time + timedelta(minutes=i*5)
                    
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
                topic.updated_at = base_time + timedelta(minutes=len(messages)*5)
                db.session.add(topic)
            
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
    print("🚀 Add Your Original Conversations")
    print("=" * 50)
    
    success = add_your_conversations()
    
    if success:
        print("✅ Script completed successfully!")
        sys.exit(0)
    else:
        print("❌ Script failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
