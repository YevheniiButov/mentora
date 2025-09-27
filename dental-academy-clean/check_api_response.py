#!/usr/bin/env python3
"""
Скрипт для проверки ответа API
Проверяет, что именно возвращает API /community/topic/<id>/content
"""

import os
import psycopg2
from urllib.parse import urlparse
import json

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

def check_api_response(conn):
    """Проверяем, что возвращает API"""
    cursor = conn.cursor()
    
    print("\n🔍 ПРОВЕРКА ОТВЕТА API")
    print("=" * 50)
    
    # Тестируем тему ID 40
    topic_id = 40
    print(f"\n📋 Тестируем тему ID {topic_id}:")
    
    # Получаем тему (как в API)
    cursor.execute("""
        SELECT ft.id, ft.title, ft.content, ft.category_id, ft.author_id, ft.created_at, ft.updated_at,
               ft.last_reply_at, ft.last_reply_by, ft.views_count, ft.replies_count, ft.is_sticky, ft.is_locked, ft.status,
               u.first_name, u.last_name, u.email,
               fc.name as category_name, fc.slug as category_slug
        FROM forum_topics ft
        LEFT JOIN "user" u ON ft.author_id = u.id
        LEFT JOIN forum_categories fc ON ft.category_id = fc.id
        WHERE ft.id = %s
    """, (topic_id,))
    
    topic_data = cursor.fetchone()
    
    if not topic_data:
        print(f"   ❌ Тема ID {topic_id} не найдена!")
        return
    
    print(f"   ✅ Тема найдена:")
    print(f"      Название: {topic_data[1]}")
    print(f"      Автор: {topic_data[14]} {topic_data[15]} (ID: {topic_data[4]})")
    print(f"      Ответы: {topic_data[10]}")
    
    # Получаем посты (как в API)
    cursor.execute("""
        SELECT fp.id, fp.content, fp.author_id, fp.created_at, fp.updated_at, fp.is_edited, fp.is_deleted,
               u.first_name, u.last_name, u.email
        FROM forum_posts fp
        LEFT JOIN "user" u ON fp.author_id = u.id
        WHERE fp.topic_id = %s AND fp.is_deleted = false
        ORDER BY fp.created_at ASC
    """, (topic_id,))
    
    posts_data = cursor.fetchall()
    
    print(f"\n📝 Посты в теме (API запрос):")
    print(f"   ✅ Найдено постов: {len(posts_data)}")
    
    for i, post in enumerate(posts_data):
        post_id, content, author_id, created_at, updated_at, is_edited, is_deleted, first_name, last_name, email = post
        author_name = f"{first_name} {last_name}".strip() if first_name and last_name else "Неизвестно"
        
        print(f"      📝 Пост {i+1} (ID: {post_id}):")
        print(f"         Автор: {author_name} (ID: {author_id})")
        print(f"         Контент: {content[:50]}...")
        print(f"         Удален: {is_deleted}")
    
    # Проверяем посты БЕЗ фильтра is_deleted
    print(f"\n📝 Посты в теме (БЕЗ фильтра is_deleted):")
    cursor.execute("""
        SELECT fp.id, fp.content, fp.author_id, fp.created_at, fp.is_deleted,
               u.first_name, u.last_name
        FROM forum_posts fp
        LEFT JOIN "user" u ON fp.author_id = u.id
        WHERE fp.topic_id = %s
        ORDER BY fp.created_at ASC
    """, (topic_id,))
    
    all_posts = cursor.fetchall()
    print(f"   ✅ Найдено постов: {len(all_posts)}")
    
    for i, post in enumerate(all_posts):
        post_id, content, author_id, created_at, is_deleted, first_name, last_name = post
        author_name = f"{first_name} {last_name}".strip() if first_name and last_name else "Неизвестно"
        
        print(f"      📝 Пост {i+1} (ID: {post_id}):")
        print(f"         Автор: {author_name}")
        print(f"         Контент: {content[:30]}...")
        print(f"         Удален: {is_deleted}")
    
    # Симулируем данные API
    print(f"\n🔧 ДАННЫЕ API (JSON):")
    print("-" * 30)
    
    if topic_data:
        topic_api_data = {
            'id': topic_data[0],
            'title': topic_data[1],
            'content': topic_data[2],
            'author': {
                'id': topic_data[4],
                'name': f"{topic_data[14]} {topic_data[15]}".strip(),
                'email': topic_data[16]
            },
            'category': {
                'id': topic_data[3],
                'name': topic_data[17],
                'slug': topic_data[18]
            },
            'created_at': topic_data[5].strftime('%d.%m.%Y %H:%M'),
            'updated_at': topic_data[6].strftime('%d.%m.%Y %H:%M') if topic_data[6] else None,
            'last_reply_at': topic_data[7].strftime('%d.%m.%Y %H:%M') if topic_data[7] else None,
            'views_count': topic_data[9],
            'replies_count': topic_data[10],
            'is_sticky': topic_data[11],
            'is_locked': topic_data[12],
            'status': topic_data[13]
        }
        
        print(f"   📋 Тема API данные:")
        print(f"      ID: {topic_api_data['id']}")
        print(f"      Автор: {topic_api_data['author']['name']}")
        print(f"      Ответы: {topic_api_data['replies_count']}")
        print(f"      Просмотры: {topic_api_data['views_count']}")
    
    # Данные постов API
    posts_api_data = []
    for post in posts_data:
        post_id, content, author_id, created_at, updated_at, is_edited, is_deleted, first_name, last_name, email = post
        
        post_api_data = {
            'id': post_id,
            'content': content,
            'author': {
                'id': author_id,
                'name': f"{first_name} {last_name}".strip(),
                'email': email
            },
            'created_at': created_at.strftime('%d.%m.%Y %H:%M'),
            'updated_at': updated_at.strftime('%d.%m.%Y %H:%M') if updated_at else None,
            'is_edited': is_edited,
            'is_deleted': is_deleted
        }
        posts_api_data.append(post_api_data)
    
    print(f"\n   📝 Посты API данные:")
    print(f"      Всего постов: {len(posts_api_data)}")
    
    for i, post in enumerate(posts_api_data):
        print(f"      Пост {i+1}: {post['author']['name']} - {post['content'][:30]}...")
    
    # Проверяем логику JavaScript
    print(f"\n🎯 ЛОГИКА JAVASCRIPT:")
    print("-" * 30)
    
    if posts_api_data:
        print(f"   posts.forEach(post => {{")
        print(f"       if (post.id !== posts[0].id) {{ // Показывать пост")
        print(f"       }} else {{ // Не показывать первый пост")
        print(f"       }}")
        print()
        
        first_post_id = posts_api_data[0]['id']
        print(f"   Первый пост ID: {first_post_id}")
        print(f"   Посты, которые будут показаны:")
        
        shown_count = 0
        for post in posts_api_data:
            if post['id'] != first_post_id:
                print(f"      ✅ Пост ID {post['id']}: {post['author']['name']}")
                shown_count += 1
            else:
                print(f"      ❌ Пост ID {post['id']}: {post['author']['name']} (ПЕРВЫЙ - НЕ ПОКАЗЫВАТЬ)")
        
        print(f"\n   📊 ИТОГ:")
        print(f"      Всего постов в API: {len(posts_api_data)}")
        print(f"      Постов для отображения: {shown_count}")
        print(f"      Должно отображаться: {len(posts_api_data) - 1} постов")
    
    else:
        print("   ❌ Постов нет в API ответе!")

def main():
    """Основная функция"""
    print("🔍 ПРОВЕРКА ОТВЕТА API ФОРУМА")
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
        check_api_response(conn)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
        
    finally:
        conn.close()
        print("\n🔌 Соединение с базой данных закрыто.")

if __name__ == "__main__":
    main()
