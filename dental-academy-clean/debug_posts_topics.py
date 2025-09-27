#!/usr/bin/env python3
"""
Скрипт для отладки связи постов и тем
Проверяет, к каким темам привязаны посты
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

def debug_posts_topics(conn):
    """Отладка связи постов и тем"""
    cursor = conn.cursor()
    
    print("\n🔍 ОТЛАДКА СВЯЗИ ПОСТОВ И ТЕМ")
    print("=" * 60)
    
    # Проверяем все темы
    print("\n📋 ВСЕ ТЕМЫ:")
    cursor.execute("""
        SELECT ft.id, ft.title, ft.category_id, ft.created_at
        FROM forum_topics ft
        ORDER BY ft.id
    """)
    
    topics = cursor.fetchall()
    
    for topic in topics:
        topic_id, title, category_id, created_at = topic
        print(f"   📋 Тема ID {topic_id}: {title[:50]}... (Категория: {category_id}, Создана: {created_at})")
    
    # Проверяем все посты с их темами
    print("\n📝 ВСЕ ПОСТЫ С ТЕМАМИ:")
    cursor.execute("""
        SELECT fp.id, fp.topic_id, fp.content, fp.created_at,
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
            post_id, topic_id, content, created_at, first_name, last_name = post
            author_name = f"{first_name} {last_name}".strip() if first_name and last_name else "Неизвестно"
            
            if current_topic != topic_id:
                print(f"\n   📋 Тема ID {topic_id}:")
                current_topic = topic_id
            
            print(f"      📝 Пост ID {post_id}: {content[:50]}...")
            print(f"         Автор: {author_name}, Время: {created_at}")
    else:
        print("   ❌ Посты не найдены!")
    
    # Проверяем посты для каждой темы отдельно
    print("\n🔍 ПРОВЕРКА ПОСТОВ ПО ТЕМАМ:")
    print("-" * 40)
    
    for topic in topics:
        topic_id, title, category_id, created_at = topic
        
        cursor.execute("""
            SELECT COUNT(*) 
            FROM forum_posts 
            WHERE topic_id = %s AND is_deleted = false
        """, (topic_id,))
        
        post_count = cursor.fetchone()[0]
        print(f"   📋 Тема ID {topic_id}: {post_count} постов")
        
        if post_count > 0:
            cursor.execute("""
                SELECT fp.id, fp.content, fp.created_at,
                       u.first_name, u.last_name
                FROM forum_posts fp
                LEFT JOIN "user" u ON fp.author_id = u.id
                WHERE fp.topic_id = %s AND fp.is_deleted = false
                ORDER BY fp.created_at
                LIMIT 3
            """, (topic_id,))
            
            sample_posts = cursor.fetchall()
            
            for post in sample_posts:
                post_id, content, post_created_at, first_name, last_name = post
                author_name = f"{first_name} {last_name}".strip() if first_name and last_name else "Неизвестно"
                print(f"      📝 Пост ID {post_id}: {content[:30]}... (Автор: {author_name})")
    
    # Проверяем, есть ли посты с is_deleted = true
    print("\n🗑️ ПРОВЕРКА УДАЛЕННЫХ ПОСТОВ:")
    cursor.execute("""
        SELECT COUNT(*) 
        FROM forum_posts 
        WHERE is_deleted = true
    """)
    
    deleted_count = cursor.fetchone()[0]
    print(f"   Удаленных постов: {deleted_count}")
    
    if deleted_count > 0:
        cursor.execute("""
            SELECT fp.id, fp.topic_id, fp.content, fp.created_at
            FROM forum_posts fp
            WHERE fp.is_deleted = true
            ORDER BY fp.topic_id, fp.created_at
            LIMIT 5
        """)
        
        deleted_posts = cursor.fetchall()
        print("   Примеры удаленных постов:")
        
        for post in deleted_posts:
            post_id, topic_id, content, created_at = post
            print(f"      📝 Пост ID {post_id} (Тема {topic_id}): {content[:30]}...")

def main():
    """Основная функция"""
    print("🔍 ОТЛАДКА СВЯЗИ ПОСТОВ И ТЕМ")
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
        debug_posts_topics(conn)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
        
    finally:
        conn.close()
        print("\n🔌 Соединение с базой данных закрыто.")

if __name__ == "__main__":
    main()
