#!/usr/bin/env python3
"""
Скрипт для исправления удаленных постов
Восстанавливает посты, помеченные как удаленные
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

def fix_deleted_posts(conn):
    """Исправить удаленные посты"""
    cursor = conn.cursor()
    
    print("\n🔧 ИСПРАВЛЕНИЕ УДАЛЕННЫХ ПОСТОВ")
    print("=" * 50)
    
    # Проверяем текущее состояние
    print("\n📊 ТЕКУЩЕЕ СОСТОЯНИЕ:")
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM forum_posts 
        WHERE is_deleted = true
    """)
    
    deleted_count = cursor.fetchone()[0]
    print(f"   Удаленных постов: {deleted_count}")
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM forum_posts 
        WHERE is_deleted = false OR is_deleted IS NULL
    """)
    
    active_count = cursor.fetchone()[0]
    print(f"   Активных постов: {active_count}")
    
    # Проверяем посты по темам ДО исправления
    print("\n📋 ПОСТЫ ПО ТЕМАМ ДО ИСПРАВЛЕНИЯ:")
    cursor.execute("SELECT id, title FROM forum_topics ORDER BY id")
    topics = cursor.fetchall()
    
    for topic_id, title in topics:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM forum_posts 
            WHERE topic_id = %s AND (is_deleted = false OR is_deleted IS NULL)
        """, (topic_id,))
        
        post_count = cursor.fetchone()[0]
        print(f"   📋 Тема ID {topic_id}: {post_count} активных постов")
    
    # Восстанавливаем все удаленные посты
    print("\n🔧 ВОССТАНОВЛЕНИЕ УДАЛЕННЫХ ПОСТОВ...")
    
    cursor.execute("""
        UPDATE forum_posts 
        SET is_deleted = false 
        WHERE is_deleted = true
    """)
    
    restored_count = cursor.rowcount
    print(f"   ✅ Восстановлено постов: {restored_count}")
    
    # Проверяем посты по темам ПОСЛЕ исправления
    print("\n📋 ПОСТЫ ПО ТЕМАМ ПОСЛЕ ИСПРАВЛЕНИЯ:")
    
    for topic_id, title in topics:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM forum_posts 
            WHERE topic_id = %s AND (is_deleted = false OR is_deleted IS NULL)
        """, (topic_id,))
        
        post_count = cursor.fetchone()[0]
        print(f"   📋 Тема ID {topic_id}: {post_count} активных постов")
    
    # Обновляем replies_count для всех тем
    print("\n📊 ОБНОВЛЕНИЕ replies_count...")
    
    cursor.execute("""
        UPDATE forum_topics 
        SET replies_count = (
            SELECT COUNT(*) - 1 
            FROM forum_posts 
            WHERE forum_posts.topic_id = forum_topics.id 
            AND (forum_posts.is_deleted = false OR forum_posts.is_deleted IS NULL)
        )
    """)
    
    updated_topics = cursor.rowcount
    print(f"   ✅ Обновлено тем: {updated_topics}")
    
    # Обновляем last_reply_at и last_reply_by
    print("\n🕐 ОБНОВЛЕНИЕ last_reply_at и last_reply_by...")
    
    cursor.execute("""
        UPDATE forum_topics 
        SET 
            last_reply_at = (
                SELECT MAX(created_at) 
                FROM forum_posts 
                WHERE forum_posts.topic_id = forum_topics.id 
                AND (forum_posts.is_deleted = false OR forum_posts.is_deleted IS NULL)
            ),
            last_reply_by = (
                SELECT author_id 
                FROM forum_posts 
                WHERE forum_posts.topic_id = forum_topics.id 
                AND (forum_posts.is_deleted = false OR forum_posts.is_deleted IS NULL)
                ORDER BY created_at DESC 
                LIMIT 1
            )
        WHERE replies_count > 0
    """)
    
    updated_replies = cursor.rowcount
    print(f"   ✅ Обновлено тем с ответами: {updated_replies}")
    
    # Финальная проверка
    print("\n📊 ФИНАЛЬНАЯ ПРОВЕРКА:")
    print("-" * 30)
    
    cursor.execute("""
        SELECT ft.id, ft.title, ft.replies_count, ft.last_reply_at, ft.last_reply_by,
               u.first_name, u.last_name
        FROM forum_topics ft
        LEFT JOIN "user" u ON ft.last_reply_by = u.id
        ORDER BY ft.id
    """)
    
    topics_final = cursor.fetchall()
    
    for topic in topics_final:
        topic_id, title, replies_count, last_reply_at, last_reply_by, first_name, last_name = topic
        last_reply_name = f"{first_name} {last_name}".strip() if first_name and last_name else "Неизвестно"
        
        print(f"   📋 Тема ID {topic_id}:")
        print(f"      Название: {title[:50]}...")
        print(f"      Ответы: {replies_count}")
        print(f"      Последний ответ: {last_reply_at} от {last_reply_name}")
        print()
    
    conn.commit()
    print("✅ Все изменения сохранены!")

def main():
    """Основная функция"""
    print("🔧 ИСПРАВЛЕНИЕ УДАЛЕННЫХ ПОСТОВ ФОРУМА")
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
        fix_deleted_posts(conn)
        
        print("\n🎉 ГОТОВО! Теперь форум должен работать правильно:")
        print("   ✅ Все удаленные посты восстановлены")
        print("   ✅ replies_count обновлен для всех тем")
        print("   ✅ last_reply_at и last_reply_by установлены")
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
