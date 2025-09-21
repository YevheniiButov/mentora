#!/usr/bin/env python3
"""
Скрипт для добавления только сообщений к существующим темам
"""

import os
import sys
from datetime import datetime, timedelta
import random

# Add the project root to the sys.path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app import app
from extensions import db
from models import ForumTopic, ForumPost, User

def add_messages_only():
    """Добавляет сообщения к существующим темам"""
    print("🔍 Adding messages to existing topics...")
    
    with app.app_context():
        try:
            db.session.execute(db.text("SELECT 1"))
            print("✅ Database connection successful")
        except Exception as e:
            print(f"❌ Database connection failed: {str(e)}")
            return False

        # Получаем пользователей
        user_ids = {}
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
        
        for name, email in fake_users:
            user = User.query.filter_by(email=email).first()
            if user:
                user_ids[name] = user.id
                print(f"✅ Found user: {name}")
            else:
                print(f"❌ User not found: {name}")
        
        # Получаем админа
        admin_user = User.query.filter_by(role='admin').first()
        if admin_user:
            user_ids['Admin'] = admin_user.id
            print(f"✅ Found admin: {admin_user.first_name}")
        
        # Определяем темы и сообщения
        topics_messages = {
            'AKV tandartsen - BIG Registration Discussion 🦷': [
                ('Maria', 'Goedemorgen collega\'s, Ik heb een vraag, moeten we alle documenten bij BiG inleveren voordat we de AKV-toetsen afleggen, of moeten we eerst de tests afleggen?'),
                ('Priya', 'Volgens mij kun je het beste eerst de taaltoets doen en daarna de documenten samen met het taalcertificaat opsturen.'),
                ('Maria', 'Bedankt!'),
                ('Ahmed', 'Hallo er bestaat geen akv test meer 👍'),
                ('Maria', 'Hoe bedoel je?'),
                ('Carlos', 'In plaats van AKV toets, moeten we nu B2+ taal certificaat halen en alle documenten naar CIBG sturen. Daarna krijgen we een datum voor BI-toets'),
                ('Maria', 'Maar als we slagen voor de BGB en of Babel examens, dan wordt dat beschouwd als een B2+ certificaat? Krijgen we een certificaat van hun?'),
                ('Anna', 'Inderdaad'),
                ('Maria', 'Bedankt!')
            ],
            'General Chat - Let\'s talk about everything! 💬': [
                ('Emma', 'Dankjewel!'),
                ('Lucas', 'Deze krijg ik net binnen...'),
                ('Alex', 'не за что'),
                ('David', 'Missed voice call')
            ]
        }
        
        created_messages = 0
        
        for topic_title, messages in topics_messages.items():
            topic = ForumTopic.query.filter_by(title=topic_title).first()
            if not topic:
                print(f"❌ Topic not found: {topic_title}")
                continue
            
            print(f"\n📝 Adding messages to: {topic_title}")
            
            # Проверяем, есть ли уже сообщения
            existing_messages = ForumPost.query.filter_by(topic_id=topic.id).count()
            if existing_messages > 0:
                print(f"⏭️ Topic already has {existing_messages} messages, skipping...")
                continue
            
            # Добавляем сообщения
            base_date = topic.created_at
            for i, (author_name, content) in enumerate(messages):
                author_id = user_ids.get(author_name, user_ids.get('Admin'))
                if not author_id:
                    print(f"❌ Author not found: {author_name}")
                    continue
                
                message_date = base_date + timedelta(minutes=i*5)  # 5 минут между сообщениями
                
                post = ForumPost(
                    topic_id=topic.id,
                    author_id=author_id,
                    content=content,
                    created_at=message_date,
                    updated_at=message_date
                )
                
                db.session.add(post)
                created_messages += 1
                print(f"  ✅ Added message by {author_name}: {content[:50]}...")
            
            db.session.commit()
        
        print(f"\n🎉 Successfully added {created_messages} messages!")
        return True

def main():
    """Основная функция"""
    print("🚀 Add Messages Only Script")
    print("=" * 50)
    
    success = add_messages_only()
    
    if success:
        print("✅ Script completed successfully!")
        sys.exit(0)
    else:
        print("❌ Script failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
