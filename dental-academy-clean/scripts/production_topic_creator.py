#!/usr/bin/env python3
"""
Простой скрипт для создания тем на продакшене
Работает с минимальными зависимостями
"""

import os
import sys
import sqlite3
from datetime import datetime, timedelta
import random

def get_database_path():
    """Получает путь к базе данных"""
    # Пробуем разные варианты
    possible_paths = [
        os.getenv('DATABASE_URL', '').replace('sqlite:///', ''),
        'instance/dental_academy_clean.db',
        'instance/dental_academy.db',
        'instance/app.db',
        'instance/database.db',
        'database.db',
        'app.db',
        '/opt/render/project/src/instance/dental_academy_clean.db',
        '/app/instance/dental_academy_clean.db'
    ]
    
    for path in possible_paths:
        if path and os.path.exists(path):
            print(f"✅ Found database: {path}")
            return path
    
    print("❌ Database not found!")
    print("Searched paths:")
    for path in possible_paths:
        print(f"  - {path}")
    return None

def create_topics_direct():
    """Создает темы напрямую через SQLite"""
    
    db_path = get_database_path()
    if not db_path:
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔍 Checking database structure...")
        
        # Проверяем существование таблиц
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='forum_categories'")
        if not cursor.fetchone():
            print("❌ forum_categories table not found!")
            return False
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='forum_topics'")
        if not cursor.fetchone():
            print("❌ forum_topics table not found!")
            return False
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='forum_posts'")
        if not cursor.fetchone():
            print("❌ forum_posts table not found!")
            return False
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user'")
        if not cursor.fetchone():
            print("❌ user table not found!")
            return False
        
        print("✅ All required tables found")
        
        # Находим или создаем категорию
        cursor.execute("SELECT id FROM forum_categories WHERE slug = 'general'")
        category_result = cursor.fetchone()
        
        if not category_result:
            print("📁 Creating general category...")
            cursor.execute("""
                INSERT INTO forum_categories (name, slug, description, is_active, order_num, created_at, updated_at)
                VALUES ('General Discussion', 'general', 'General discussions about BIG registration', 1, 1, ?, ?)
            """, (datetime.now(), datetime.now()))
            category_id = cursor.lastrowid
        else:
            category_id = category_result[0]
            print(f"✅ Found category with ID: {category_id}")
        
        # Находим пользователя-админа
        cursor.execute("SELECT id FROM user WHERE role = 'admin' LIMIT 1")
        admin_result = cursor.fetchone()
        
        if not admin_result:
            cursor.execute("SELECT id FROM user LIMIT 1")
            admin_result = cursor.fetchone()
        
        if not admin_result:
            print("❌ No users found! Please create a user first.")
            return False
        
        admin_id = admin_result[0]
        print(f"✅ Found admin user with ID: {admin_id}")
        
        # Создаем фейковых пользователей
        fake_users = [
            ('Maria', 'maria@example.com'),
            ('Ahmed', 'ahmed@example.com'),
            ('Priya', 'priya@example.com'),
            ('Carlos', 'carlos@example.com'),
            ('Anna', 'anna@example.com')
        ]
        
        user_ids = {}
        for name, email in fake_users:
            cursor.execute("SELECT id FROM user WHERE email = ?", (email,))
            result = cursor.fetchone()
            
            if not result:
                print(f"👤 Creating fake user: {name}")
                cursor.execute("""
                    INSERT INTO user (email, first_name, last_name, role, is_active, created_at)
                    VALUES (?, ?, '', 'user', 1, ?)
                """, (email, name, datetime.now() - timedelta(days=random.randint(30, 90))))
                user_ids[name] = cursor.lastrowid
            else:
                user_ids[name] = result[0]
                print(f"⏭️ User already exists: {name}")
        
        # Создаем темы
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
            }
        ]
        
        created_count = 0
        
        for i, topic_data in enumerate(topics_data):
            # Проверяем, не существует ли уже такая тема
            cursor.execute("SELECT id FROM forum_topics WHERE title = ?", (topic_data['title'],))
            if cursor.fetchone():
                print(f"⏭️ Topic already exists: {topic_data['title']}")
                continue
            
            # Создаем тему
            topic_date = base_date + timedelta(days=i*2)
            
            cursor.execute("""
                INSERT INTO forum_topics (title, content, category_id, author_id, status, is_sticky, is_locked, 
                                        views_count, replies_count, likes_count, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'active', 0, 0, ?, ?, ?, ?, ?)
            """, (
                topic_data['title'],
                topic_data['content'],
                category_id,
                admin_id,
                random.randint(50, 200),
                len(topic_data['messages']),
                random.randint(5, 25),
                topic_date,
                topic_date + timedelta(days=random.randint(1, 5))
            ))
            
            topic_id = cursor.lastrowid
            
            # Создаем сообщения
            for message_data in topic_data['messages']:
                author_name, content, day_offset, hour, minute = message_data
                author_id = user_ids.get(author_name, admin_id)
                
                message_date = topic_date + timedelta(days=day_offset, hours=hour, minutes=minute)
                
                cursor.execute("""
                    INSERT INTO forum_posts (topic_id, author_id, content, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (topic_id, author_id, content, message_date, message_date))
            
            created_count += 1
            print(f"✅ Created topic: {topic_data['title']}")
        
        conn.commit()
        conn.close()
        
        print(f"\n🎉 Successfully created {created_count} topics!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция"""
    print("🚀 Production Topic Creator")
    print("=" * 50)
    
    success = create_topics_direct()
    
    if success:
        print("✅ Script completed successfully!")
        sys.exit(0)
    else:
        print("❌ Script failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
