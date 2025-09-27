#!/usr/bin/env python3
"""
Исправленный скрипт для создания темы-голосования о уровнях нидерландского языка
Работает с существующими таблицами форума БЕЗ колонки is_verified
"""

import os
import sys
import psycopg2
from datetime import datetime, timezone
import hashlib

def create_dutch_level_poll():
    """Создать тему с голосованием о уровнях нидерландского"""
    
    # Подключение к базе данных
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        print("❌ DATABASE_URL не установлен!")
        return False
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        print("✅ Подключение к базе данных установлено")
        
        # Создание темы от имени administrator
        print("\n📊 Создание темы-голосования...")
        
        # Получаем ID администратора или создаем его
        admin_id = get_or_create_admin(cur)
        
        # Получаем ID категории "Collega Chat"
        category_id = get_collega_chat_category(cur)
        
        # Создаем тему с голосованием в контенте
        poll_content = '''Hallo allemaal! 🇳🇱

Ik ben benieuwd op welk niveau iedereen Nederlands spreekt. Dit helpt ons om elkaar beter te begrijpen en eventueel studiepartners te vinden.

**🗳️ POLL: Op welk niveau Nederlands spreek je?**

📊 **Huidige resultaten (62 stemmen):**
• **A1 - Beginner**: 3 stemmen (5%)
• **A2 - Elementary**: 10 stemmen (16%) 
• **B1 - Intermediate**: 23 stemmen (37%) ⭐
• **B2 - Upper Intermediate**: 11 stemmen (18%)
• **B2+ - Advanced Intermediate**: 8 stemmen (13%)
• **C1 - Advanced**: 5 stemmen (8%)
• **C2 - Proficiency**: 2 stemmen (3%)

---
Hello everyone! 

I'm curious about what level of Dutch everyone speaks. This will help us understand each other better and possibly find study partners.

**🗳️ POLL: What level of Dutch do you speak?**

📊 **Current results (62 votes):**
• **A1 - Beginner**: 3 votes (5%)
• **A2 - Elementary**: 10 votes (16%) 
• **B1 - Intermediate**: 23 votes (37%) ⭐
• **B2 - Upper Intermediate**: 11 votes (18%)
• **B2+ - Advanced Intermediate**: 8 votes (13%)
• **C1 - Advanced**: 5 votes (8%)
• **C2 - Proficiency**: 2 votes (3%)

**B1 is the most popular level!** 🎉'''

        topic_data = {
            'title': 'Op welk niveau Nederlands spreek je? (Dutch Level Poll)',
            'content': poll_content,
            'category_id': category_id,
            'author_id': admin_id,
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc),
            'views_count': 0,
            'replies_count': 0,
            'likes_count': 0,
            'last_reply_at': datetime.now(timezone.utc),
            'last_reply_by': admin_id
        }
        
        # Вставляем тему
        insert_query = """
        INSERT INTO forum_topics (
            title, content, category_id, author_id, created_at, updated_at,
            views_count, replies_count, likes_count, last_reply_at, last_reply_by
        ) VALUES (
            %(title)s, %(content)s, %(category_id)s, %(author_id)s, %(created_at)s, %(updated_at)s,
            %(views_count)s, %(replies_count)s, %(likes_count)s, %(last_reply_at)s, %(last_reply_by)s
        ) RETURNING id
        """
        
        cur.execute(insert_query, topic_data)
        topic_id = cur.fetchone()[0]
        print(f"✅ Создана тема ID: {topic_id}")
        
        # Создаем несколько комментариев от разных пользователей
        print("\n💬 Создание комментариев...")
        
        # Получаем существующих пользователей
        cur.execute("SELECT id FROM \"user\" WHERE email LIKE '%@example.com' LIMIT 10")
        users = cur.fetchall()
        
        if len(users) < 5:
            print(f"⚠️ Недостаточно пользователей ({len(users)}), создаем дополнительных...")
            # Создаем дополнительных пользователей
            for i in range(5 - len(users)):
                user_id = create_demo_user(cur, f"voter_{i+1}")
                users.append((user_id,))
        
        # Комментарии на голландском и английском
        comments = [
            "Ik ben B1! Wie wil er samen oefenen? 😊",
            "A2 hier. Nederlands is moeilijk maar leuk! 🇳🇱",
            "B2+ here. Happy to help others practice! 💪",
            "C1 niveau. Ik kan jullie helpen met moeilijke grammatica! 📚",
            "A1 beginner. Dank je voor deze poll! 🙏"
        ]
        
        for i, comment in enumerate(comments):
            if i < len(users):
                user_id = users[i][0]
                
                comment_data = {
                    'topic_id': topic_id,
                    'author_id': user_id,
                    'content': comment,
                    'created_at': datetime.now(timezone.utc),
                    'is_deleted': False
                }
                
                comment_query = """
                INSERT INTO forum_posts (
                    topic_id, author_id, content, created_at, is_deleted
                ) VALUES (
                    %(topic_id)s, %(author_id)s, %(content)s, %(created_at)s, %(is_deleted)s
                )
                """
                
                cur.execute(comment_query, comment_data)
                print(f"✅ Создан комментарий: {comment[:30]}...")
        
        # Обновляем статистику темы
        cur.execute("""
            UPDATE forum_topics 
            SET replies_count = (SELECT COUNT(*) FROM forum_posts WHERE topic_id = %s AND is_deleted = false)
            WHERE id = %s
        """, (topic_id, topic_id))
        
        # Коммитим изменения
        conn.commit()
        print("\n🎉 Голосование успешно создано!")
        print(f"📊 Тема ID: {topic_id}")
        print(f"💬 Комментариев: {len(comments)}")
        print(f"👥 Всего голосов в тексте: 62")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        if conn:
            conn.rollback()
        return False
    finally:
        if conn:
            conn.close()

def get_or_create_admin(cur):
    """Получить или создать администратора"""
    # Ищем администратора
    cur.execute("SELECT id FROM \"user\" WHERE email = 'administrator@mentora.nl'")
    admin = cur.fetchone()
    
    if admin:
        return admin[0]
    
    # Создаем администратора БЕЗ is_verified
    admin_data = {
        'email': 'administrator@mentora.nl',
        'first_name': 'Admin',
        'last_name': 'Istrator',
        'password_hash': hashlib.sha256('admin123'.encode()).hexdigest(),
        'created_at': datetime.now(timezone.utc),
        'is_active': True
    }
    
    insert_query = """
    INSERT INTO \"user\" (email, first_name, last_name, password_hash, created_at, is_active)
    VALUES (%(email)s, %(first_name)s, %(last_name)s, %(password_hash)s, %(created_at)s, %(is_active)s)
    RETURNING id
    """
    
    cur.execute(insert_query, admin_data)
    admin_id = cur.fetchone()[0]
    print(f"✅ Создан администратор ID: {admin_id}")
    return admin_id

def get_collega_chat_category(cur):
    """Получить ID категории Collega Chat"""
    cur.execute("SELECT id FROM forum_categories WHERE name = 'Collega Chat'")
    category = cur.fetchone()
    
    if not category:
        raise Exception("Категория 'Collega Chat' не найдена!")
    
    return category[0]

def create_demo_user(cur, username):
    """Создать демо-пользователя для голосования БЕЗ is_verified"""
    user_data = {
        'email': f'{username}@example.com',
        'first_name': username.title(),
        'last_name': 'Voter',
        'password_hash': hashlib.sha256('demo123'.encode()).hexdigest(),
        'created_at': datetime.now(timezone.utc),
        'is_active': True
    }
    
    insert_query = """
    INSERT INTO \"user\" (email, first_name, last_name, password_hash, created_at, is_active)
    VALUES (%(email)s, %(first_name)s, %(last_name)s, %(password_hash)s, %(created_at)s, %(is_active)s)
    RETURNING id
    """
    
    cur.execute(insert_query, user_data)
    return cur.fetchone()[0]

if __name__ == "__main__":
    print("🇳🇱 СОЗДАНИЕ ГОЛОСОВАНИЯ О НИДЕРЛАНДСКОМ ЯЗЫКЕ (ИСПРАВЛЕННАЯ ВЕРСИЯ)")
    print("=" * 70)
    
    success = create_dutch_level_poll()
    
    if success:
        print("\n✅ ГОТОВО! Голосование создано успешно!")
        print("🌐 Перейдите в комьюнити чтобы увидеть результат")
    else:
        print("\n❌ ОШИБКА! Не удалось создать голосование")
        sys.exit(1)
