#!/usr/bin/env python3
"""
Точный скрипт для исправления переписок - добавляет сообщения в правильные темы
"""

import os
import sys

def fix_conversations_precise():
    """Точно исправляет переписки - добавляет в правильные темы"""
    
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
        
        print("🔧 Fixing conversations precisely...")
        
        with app.app_context():
            # Проверяем подключение к БД
            try:
                db.session.execute(db.text("SELECT 1"))
                print("✅ Database connection successful")
            except Exception as e:
                print(f"❌ Database connection failed: {str(e)}")
                return False
            
            # Находим пользователей
            users = User.query.filter_by(is_active=True).limit(10).all()
            if len(users) < 3:
                print("❌ Not enough users for messages")
                return False
            
            print(f"✅ Found {len(users)} users for messages")
            
            # ВАШИ ТОЧНЫЕ ПЕРЕПИСКИ
            conversations = {
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
            
            # УДАЛЯЕМ ВСЕ СУЩЕСТВУЮЩИЕ СООБЩЕНИЯ
            print("🗑️ Deleting all existing messages...")
            ForumPost.query.delete()
            db.session.commit()
            print("✅ All messages deleted")
            
            # СБРАСЫВАЕМ СЧЕТЧИКИ В ТЕМАХ
            print("🔄 Resetting topic counters...")
            topics = ForumTopic.query.all()
            for topic in topics:
                topic.replies_count = 0
                topic.updated_at = datetime.now()
                db.session.add(topic)
            db.session.commit()
            print("✅ Topic counters reset")
            
            # ДОБАВЛЯЕМ СООБЩЕНИЯ В ПРАВИЛЬНЫЕ ТЕМЫ
            created_messages = 0
            
            for topic_title, messages in conversations.items():
                topic = ForumTopic.query.filter_by(title=topic_title).first()
                if topic:
                    print(f"\n📝 Adding messages to: '{topic.title}'")
                    
                    base_time = topic.created_at
                    
                    for i, message_text in enumerate(messages):
                        # Выбираем случайного пользователя
                        author = random.choice(users)
                        
                        # Время сообщения
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
                    db.session.add(topic)
                    print(f"✅ Updated replies_count for '{topic.title}' to {topic.replies_count}")
                else:
                    print(f"❌ Topic not found: {topic_title}")
            
            db.session.commit()
            print(f"\n🎉 Successfully added {created_messages} messages to correct topics!")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция"""
    print("🚀 Fix Conversations Precise")
    print("=" * 50)
    
    success = fix_conversations_precise()
    
    if success:
        print("✅ Script completed successfully!")
        sys.exit(0)
    else:
        print("❌ Script failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
