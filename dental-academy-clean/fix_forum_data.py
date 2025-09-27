#!/usr/bin/env python3
"""
Скрипт для исправления данных форума
Исправляет replies_count и обновляет статистику
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
    
    # Исправляем replies_count для всех тем
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
    
    # Обновляем last_reply_at и last_reply_by
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
    
    # Проверяем пользователей с проблемными именами
    print("\n👥 Проверка пользователей...")
    
    cursor.execute('SELECT id, first_name, last_name, email FROM "user" WHERE id IN (57, 62)')
    users = cursor.fetchall()
    
    for user in users:
        user_id, first_name, last_name, email = user
        print(f"   👤 ID: {user_id}, Имя: '{first_name}' '{last_name}', Email: {email}")
        
        if not first_name or not last_name:
            print(f"   ⚠️ Пользователь {user_id} имеет пустые имена!")
    
    # Фиксируем имена пользователей если нужно
    print("\n🔧 Исправление имен пользователей...")
    
    # ID 57 - Liliam
    cursor.execute('UPDATE "user" SET first_name = %s, last_name = %s WHERE id = %s', ('Liliam', 'Silva', 57))
    print("   ✅ Исправлено имя пользователя ID 57: Liliam Silva")
    
    # ID 62 - Shiva
    cursor.execute('UPDATE "user" SET first_name = %s, last_name = %s WHERE id = %s', ('Shiva', 'Mohammadi', 62))
    print("   ✅ Исправлено имя пользователя ID 62: Shiva Mohammadi")
    
    # Проверяем результат
    print("\n📊 ПРОВЕРКА РЕЗУЛЬТАТА:")
    print("-" * 30)
    
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
        last_reply_name = f"{first_name} {last_name}" if first_name and last_name else "Неизвестно"
        
        print(f"   📋 Тема ID {topic_id}:")
        print(f"      Название: {title[:50]}...")
        print(f"      Ответы: {replies_count}")
        print(f"      Последний ответ: {last_reply_at} от {last_reply_name}")
        print()
    
    conn.commit()
    print("✅ Все изменения сохранены!")

def main():
    """Основная функция"""
    print("🔧 ИСПРАВЛЕНИЕ ДАННЫХ ФОРУМА НА ПРОДАКШЕНЕ")
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
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()
        print("\n🔌 Соединение с базой данных закрыто.")

if __name__ == "__main__":
    main()
