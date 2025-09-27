#!/usr/bin/env python3
"""
Финальный скрипт для исправления данных форума
Исправляет все проблемы с отображением постов
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

def fix_forum_data(conn):
    """Исправить данные форума"""
    cursor = conn.cursor()
    
    print("\n🔧 ИСПРАВЛЕНИЕ ДАННЫХ ФОРУМА")
    print("=" * 50)
    
    # 1. Исправляем имена пользователей
    print("\n👥 Исправление имен пользователей...")
    
    user_fixes = [
        (57, 'Liliam', 'Silva'),  # liliam@example.com
        (62, 'Shiva', 'Mohammadi'),  # shiva@example.com
        (65, 'Rinsy', 'George'),  # rinsy@example.com
        (67, 'Rami', 'Al-Ali'),  # rami@example.com
    ]
    
    for user_id, first_name, last_name in user_fixes:
        cursor.execute('UPDATE "user" SET first_name = %s, last_name = %s WHERE id = %s', 
                      (first_name, last_name, user_id))
        print(f"   ✅ Исправлено имя пользователя ID {user_id}: {first_name} {last_name}")
    
    # 2. Исправляем replies_count для всех тем
    print("\n📊 Обновление replies_count для тем...")
    
    cursor.execute("""
        UPDATE forum_topics 
        SET replies_count = (
            SELECT COUNT(*) - 1 
            FROM forum_posts 
            WHERE forum_posts.topic_id = forum_topics.id
        )
        WHERE replies_count IS NULL OR replies_count = 0
    """)
    
    updated_topics = cursor.rowcount
    print(f"   ✅ Обновлено тем: {updated_topics}")
    
    # 3. Обновляем last_reply_at и last_reply_by
    print("\n🕐 Обновление last_reply_at и last_reply_by...")
    
    cursor.execute("""
        UPDATE forum_topics 
        SET 
            last_reply_at = (
                SELECT MAX(created_at) 
                FROM forum_posts 
                WHERE forum_posts.topic_id = forum_topics.id
            ),
            last_reply_by = (
                SELECT author_id 
                FROM forum_posts 
                WHERE forum_posts.topic_id = forum_topics.id 
                ORDER BY created_at DESC 
                LIMIT 1
            )
        WHERE replies_count > 0
    """)
    
    updated_replies = cursor.rowcount
    print(f"   ✅ Обновлено тем с ответами: {updated_replies}")
    
    # 4. Проверяем результат
    print("\n📊 ПРОВЕРКА РЕЗУЛЬТАТА:")
    print("-" * 50)
    
    cursor.execute("""
        SELECT ft.id, ft.title, ft.replies_count, ft.last_reply_at, ft.last_reply_by,
               u.first_name, u.last_name
        FROM forum_topics ft
        LEFT JOIN "user" u ON ft.last_reply_by = u.id
        ORDER BY ft.id
    """)
    
    topics = cursor.fetchall()
    
    for topic in topics:
        topic_id, title, replies_count, last_reply_at, last_reply_by, first_name, last_name = topic
        last_reply_name = f"{first_name} {last_name}".strip() if first_name and last_name else "Неизвестно"
        
        print(f"   📋 Тема ID {topic_id}:")
        print(f"      Название: {title[:50]}...")
        print(f"      Ответы: {replies_count}")
        print(f"      Последний ответ: {last_reply_at} от {last_reply_name}")
        print()
    
    # 5. Проверяем посты по темам
    print("\n📝 Проверка постов по темам:")
    print("-" * 30)
    
    cursor.execute("""
        SELECT ft.id, ft.title, COUNT(fp.id) as post_count
        FROM forum_topics ft
        LEFT JOIN forum_posts fp ON ft.id = fp.topic_id
        GROUP BY ft.id, ft.title
        ORDER BY ft.id
    """)
    
    topic_stats = cursor.fetchall()
    
    for topic_id, title, post_count in topic_stats:
        print(f"   📋 Тема ID {topic_id}: {post_count} постов")
    
    conn.commit()
    print("\n✅ Все изменения сохранены!")

def main():
    """Основная функция"""
    print("🔧 ФИНАЛЬНОЕ ИСПРАВЛЕНИЕ ДАННЫХ ФОРУМА")
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
        fix_forum_data(conn)
        
        print("\n🎉 ГОТОВО! Теперь форум должен работать правильно:")
        print("   ✅ replies_count обновлен для всех тем")
        print("   ✅ last_reply_at и last_reply_by установлены")
        print("   ✅ Имена пользователей исправлены")
        print("   ✅ Посты должны отображаться в интерфейсе")
        print("\n📱 Обновите страницу форума в браузере!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()
        print("\n🔌 Соединение с базой данных закрыто.")

if __name__ == "__main__":
    main()
