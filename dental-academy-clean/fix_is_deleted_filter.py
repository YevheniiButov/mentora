#!/usr/bin/env python3
"""
Скрипт для исправления фильтра is_deleted
Устанавливает is_deleted = false для всех NULL значений
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

def fix_is_deleted_filter(conn):
    """Исправить фильтр is_deleted"""
    cursor = conn.cursor()
    
    print("\n🔧 ИСПРАВЛЕНИЕ ФИЛЬТРА is_deleted")
    print("=" * 50)
    
    # Проверяем текущее состояние
    print("\n📊 ТЕКУЩЕЕ СОСТОЯНИЕ:")
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM forum_posts 
        WHERE is_deleted IS NULL
    """)
    
    null_count = cursor.fetchone()[0]
    print(f"   Постов с is_deleted = NULL: {null_count}")
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM forum_posts 
        WHERE is_deleted = true
    """)
    
    deleted_count = cursor.fetchone()[0]
    print(f"   Постов с is_deleted = true: {deleted_count}")
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM forum_posts 
        WHERE is_deleted = false
    """)
    
    active_count = cursor.fetchone()[0]
    print(f"   Постов с is_deleted = false: {active_count}")
    
    # Устанавливаем is_deleted = false для всех NULL значений
    print("\n🔧 УСТАНОВКА is_deleted = false ДЛЯ NULL ЗНАЧЕНИЙ...")
    
    cursor.execute("""
        UPDATE forum_posts 
        SET is_deleted = false 
        WHERE is_deleted IS NULL
    """)
    
    updated_count = cursor.rowcount
    print(f"   ✅ Обновлено постов: {updated_count}")
    
    # Проверяем результат
    print("\n📊 РЕЗУЛЬТАТ ПОСЛЕ ИСПРАВЛЕНИЯ:")
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM forum_posts 
        WHERE is_deleted IS NULL
    """)
    
    null_count_after = cursor.fetchone()[0]
    print(f"   Постов с is_deleted = NULL: {null_count_after}")
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM forum_posts 
        WHERE is_deleted = true
    """)
    
    deleted_count_after = cursor.fetchone()[0]
    print(f"   Постов с is_deleted = true: {deleted_count_after}")
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM forum_posts 
        WHERE is_deleted = false
    """)
    
    active_count_after = cursor.fetchone()[0]
    print(f"   Постов с is_deleted = false: {active_count_after}")
    
    # Тестируем API запрос
    print("\n🔍 ТЕСТИРОВАНИЕ API ЗАПРОСА:")
    print("-" * 30)
    
    # Тестируем тему ID 40
    topic_id = 40
    print(f"\n📋 Тестируем тему ID {topic_id}:")
    
    cursor.execute("""
        SELECT COUNT(*) 
        FROM forum_posts 
        WHERE topic_id = %s AND is_deleted = false
    """, (topic_id,))
    
    api_posts_count = cursor.fetchone()[0]
    print(f"   Постов в API запросе: {api_posts_count}")
    
    if api_posts_count > 0:
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
        
        print(f"   Примеры постов:")
        for post in sample_posts:
            post_id, content, created_at, first_name, last_name = post
            author_name = f"{first_name} {last_name}".strip() if first_name and last_name else "Неизвестно"
            print(f"      📝 Пост ID {post_id}: {content[:30]}... (Автор: {author_name})")
    
    # Проверяем все темы
    print(f"\n📋 ПОСТЫ ПО ВСЕМ ТЕМАМ:")
    cursor.execute("SELECT id, title FROM forum_topics ORDER BY id")
    topics = cursor.fetchall()
    
    for topic_id, title in topics:
        cursor.execute("""
            SELECT COUNT(*) 
            FROM forum_posts 
            WHERE topic_id = %s AND is_deleted = false
        """, (topic_id,))
        
        post_count = cursor.fetchone()[0]
        print(f"   📋 Тема ID {topic_id}: {post_count} активных постов")
    
    conn.commit()
    print("\n✅ Все изменения сохранены!")

def main():
    """Основная функция"""
    print("🔧 ИСПРАВЛЕНИЕ ФИЛЬТРА is_deleted ФОРУМА")
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
        fix_is_deleted_filter(conn)
        
        print("\n🎉 ГОТОВО! Теперь форум должен работать правильно:")
        print("   ✅ Все NULL значения is_deleted установлены в false")
        print("   ✅ API запросы теперь возвращают посты")
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
