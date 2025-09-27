#!/usr/bin/env python3
"""
Скрипт для проверки данных форума
Проверяет, есть ли темы и посты в базе данных
"""

import os
import psycopg2
from urllib.parse import urlparse

def get_production_db_connection():
    """Получить подключение к продакшн базе данных через DATABASE_URL"""
    try:
        database_url = os.environ.get('DATABASE_URL')
        
        if not database_url:
            print("❌ DATABASE_URL не найден в переменных окружения!")
            return None
        
        print(f"🔗 Используем DATABASE_URL: {database_url[:50]}...")
        
        conn = psycopg2.connect(database_url, sslmode='require')
        print("✅ Подключение к продакшн базе данных установлено")
        return conn
        
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        return None

def check_forum_data(conn):
    """Проверить данные форума"""
    cursor = conn.cursor()
    
    print("\n📊 ПРОВЕРКА ДАННЫХ ФОРУМА")
    print("=" * 50)
    
    # Проверяем категории
    print("\n📂 Категории форума:")
    cursor.execute("SELECT id, name, slug, is_active FROM forum_categories ORDER BY id")
    categories = cursor.fetchall()
    
    if categories:
        for cat in categories:
            cat_id, name, slug, is_active = cat
            print(f"   ✅ ID: {cat_id}, Название: {name}, Slug: {slug}, Активна: {is_active}")
    else:
        print("   ❌ Категории не найдены!")
    
    # Проверяем темы
    print("\n💬 Темы форума:")
    cursor.execute("""
        SELECT ft.id, ft.title, ft.category_id, ft.author_id, ft.views_count, ft.replies_count, ft.created_at,
               u.first_name, u.last_name
        FROM forum_topics ft
        LEFT JOIN "user" u ON ft.author_id = u.id
        ORDER BY ft.id
    """)
    topics = cursor.fetchall()
    
    if topics:
        for topic in topics:
            topic_id, title, cat_id, author_id, views, replies, created_at, first_name, last_name = topic
            author_name = f"{first_name} {last_name}" if first_name and last_name else "Неизвестно"
            print(f"   ✅ ID: {topic_id}")
            print(f"      Название: {title[:50]}...")
            print(f"      Автор: {author_name} (ID: {author_id})")
            print(f"      Категория: {cat_id}")
            print(f"      Просмотры: {views}, Ответы: {replies}")
            print(f"      Создано: {created_at}")
            print()
    else:
        print("   ❌ Темы не найдены!")
    
    # Проверяем посты
    print("\n📝 Посты форума:")
    cursor.execute("""
        SELECT fp.id, fp.topic_id, fp.author_id, fp.content, fp.created_at,
               u.first_name, u.last_name
        FROM forum_posts fp
        LEFT JOIN "user" u ON fp.author_id = u.id
        ORDER BY fp.topic_id, fp.created_at
    """)
    posts = cursor.fetchall()
    
    if posts:
        print(f"   ✅ Найдено постов: {len(posts)}")
        current_topic = None
        
        for post in posts:
            post_id, topic_id, author_id, content, created_at, first_name, last_name = post
            author_name = f"{first_name} {last_name}" if first_name and last_name else "Неизвестно"
            
            if current_topic != topic_id:
                print(f"\n   📋 Тема ID {topic_id}:")
                current_topic = topic_id
            
            print(f"      📝 Пост ID {post_id}: {content[:50]}...")
            print(f"         Автор: {author_name}, Время: {created_at}")
    else:
        print("   ❌ Посты не найдены!")
    
    # Проверяем пользователей
    print("\n👥 Пользователи с @example.com:")
    cursor.execute('SELECT id, first_name, last_name, email FROM "user" WHERE email LIKE \'%@example.com\' ORDER BY id')
    users = cursor.fetchall()
    
    if users:
        print(f"   ✅ Найдено пользователей: {len(users)}")
        for user in users:
            user_id, first_name, last_name, email = user
            print(f"      👤 ID: {user_id}, Имя: {first_name} {last_name}, Email: {email}")
    else:
        print("   ❌ Пользователи не найдены!")

def main():
    """Основная функция"""
    print("🔍 ПРОВЕРКА ДАННЫХ ФОРУМА НА ПРОДАКШЕНЕ")
    print("=" * 60)
    
    # Проверяем переменные окружения
    if not os.environ.get('DATABASE_URL'):
        print("❌ DATABASE_URL не найден в переменных окружения!")
        return False
    
    # Подключаемся к базе данных
    conn = get_production_db_connection()
    if not conn:
        return False
    
    try:
        check_forum_data(conn)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
        
    finally:
        conn.close()
        print("\n🔌 Соединение с базой данных закрыто.")

if __name__ == "__main__":
    main()
