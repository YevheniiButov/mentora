#!/usr/bin/env python3
"""
Простой скрипт для добавления переписок (точно сработает)
"""

import os
import sys

def simple_add_conversations():
    """Простое добавление переписок"""
    
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
        
        print("🔍 Simple add conversations...")
        
        with app.app_context():
            # Проверяем подключение к БД
            try:
                db.session.execute(db.text("SELECT 1"))
                print("✅ Database connection successful")
            except Exception as e:
                print(f"❌ Database connection failed: {str(e)}")
                return False
            
            # Находим пользователей (точно как в старом скрипте)
            users = User.query.filter_by(is_active=True).limit(10).all()
            if len(users) < 3:
                print("❌ Not enough users for messages")
                return False
            
            print(f"✅ Found {len(users)} users for messages")
            
            # ВАШИ ПЕРЕПИСКИ
            conversations = [
                "Goedemorgen collega's, Ik heb een vraag, moeten we alle documenten bij BiG inleveren voordat we de AKV-toetsen afleggen, of moeten we eerst de tests afleggen?",
                "Volgens mij kun je het beste eerst de taaltoets doen en daarna de documenten samen met het taalcertificaat opsturen.",
                "Bedankt!",
                "Hallo er bestaat geen akv test meer 👍",
                "Hoe bedoel je?",
                "In plaats van AKV toets, moeten we nu B2+ taal certificaat halen en alle documenten naar CIBG sturen. Daarna krijgen we een datum voor BI-toets",
                "Maar als we slagen voor de BGB en of Babel examens, dan wordt dat beschouwd als een B2+ certificaat? Krijgen we een certificaat van hun?",
                "Inderdaad",
                "Bedankt!",
                "Dankjewel!",
                "Deze krijg ik net binnen...",
                "не за что",
                "Missed voice call"
            ]
            
            # Находим темы БЕЗ сообщений (как в старом скрипте)
            topics_without_messages = ForumTopic.query.filter(
                ~ForumTopic.posts.any()
            ).limit(2).all()
            
            print(f"📝 Found {len(topics_without_messages)} topics without messages")
            
            if not topics_without_messages:
                print("❌ No topics without messages found")
                return False
            
            created_messages = 0
            
            # Добавляем сообщения к первым двум темам без сообщений
            for i, topic in enumerate(topics_without_messages[:2]):
                print(f"\n📋 Adding messages to: '{topic.title}'")
                
                # Берем первые несколько сообщений для первой темы, остальные для второй
                if i == 0:
                    messages_to_add = conversations[:9]  # Первые 9 сообщений
                else:
                    messages_to_add = conversations[9:]  # Остальные 4 сообщения
                
                base_time = topic.created_at
                
                for j, message_text in enumerate(messages_to_add):
                    # Выбираем случайного пользователя
                    author = random.choice(users)
                    
                    # Время сообщения
                    message_time = base_time + timedelta(hours=j*2, minutes=random.randint(0, 59))
                    
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
                topic.replies_count = len(messages_to_add)
                topic.updated_at = base_time + timedelta(hours=len(messages_to_add)*2)
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
    print("🚀 Simple Add Conversations")
    print("=" * 50)
    
    success = simple_add_conversations()
    
    if success:
        print("✅ Script completed successfully!")
        sys.exit(0)
    else:
        print("❌ Script failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
