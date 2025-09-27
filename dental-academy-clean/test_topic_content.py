#!/usr/bin/env python3
"""
Скрипт для тестирования загрузки контента темы
Проверяет, что возвращает API /community/topic/<id>/content
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

def test_topic_content_api(conn):
    """Тестируем логику API загрузки контента темы"""
    cursor = conn.cursor()
    
    print("\n🔍 ТЕСТИРОВАНИЕ API ЗАГРУЗКИ КОНТЕНТА ТЕМЫ")
    print("=" * 60)
    
    # Тестируем тему ID 40
    topic_id = 40
    print(f"\n📋 Тестируем тему ID {topic_id}:")
    
    # Получаем тему
    cursor.execute("""
        SELECT ft.id, ft.title, ft.content, ft.category_id, ft.author_id, ft.created_at, ft.updated_at,
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
    
    topic_id, title, content, category_id, author_id, created_at, updated_at, first_name, last_name, email, category_name, category_slug = topic_data
    
    print(f"   ✅ Тема найдена:")
    print(f"      Название: {title}")
    print(f"      Автор: {first_name} {last_name} (ID: {author_id})")
    print(f"      Категория: {category_name} (ID: {category_id})")
    print(f"      Создана: {created_at}")
    
    # Получаем посты
    cursor.execute("""
        SELECT fp.id, fp.content, fp.author_id, fp.created_at, fp.updated_at, fp.is_edited, fp.is_deleted,
               u.first_name, u.last_name, u.email
        FROM forum_posts fp
        LEFT JOIN "user" u ON fp.author_id = u.id
        WHERE fp.topic_id = %s AND fp.is_deleted = false
        ORDER BY fp.created_at ASC
    """, (topic_id,))
    
    posts_data = cursor.fetchall()
    
    print(f"\n📝 Посты в теме:")
    print(f"   ✅ Найдено постов: {len(posts_data)}")
    
    for i, post in enumerate(posts_data):
        post_id, post_content, post_author_id, post_created_at, post_updated_at, is_edited, is_deleted, post_first_name, post_last_name, post_email = post
        author_name = f"{post_first_name} {post_last_name}" if post_first_name and post_last_name else "Неизвестно"
        
        print(f"      📝 Пост {i+1} (ID: {post_id}):")
        print(f"         Автор: {author_name} (ID: {post_author_id})")
        print(f"         Контент: {post_content[:50]}...")
        print(f"         Создан: {post_created_at}")
        print(f"         Редактирован: {is_edited}, Удален: {is_deleted}")
    
    # Симулируем данные, которые должен возвращать API
    print(f"\n🔧 ДАННЫЕ ДЛЯ API:")
    print("-" * 30)
    
    # Данные темы
    topic_api_data = {
        'id': topic_id,
        'title': title,
        'content': content,
        'author': {
            'id': author_id,
            'name': f"{first_name} {last_name}".strip(),
            'email': email
        },
        'category': {
            'id': category_id,
            'name': category_name,
            'slug': category_slug
        },
        'created_at': created_at.strftime('%d.%m.%Y %H:%M'),
        'updated_at': updated_at.strftime('%d.%m.%Y %H:%M') if updated_at else None,
        'replies_count': len(posts_data) - 1  # -1 для исключения первого поста
    }
    
    print(f"   📋 Тема API данные:")
    print(f"      ID: {topic_api_data['id']}")
    print(f"      Автор: {topic_api_data['author']['name']}")
    print(f"      Ответы: {topic_api_data['replies_count']}")
    
    # Данные постов
    posts_api_data = []
    for post in posts_data:
        post_id, post_content, post_author_id, post_created_at, post_updated_at, is_edited, is_deleted, post_first_name, post_last_name, post_email = post
        
        post_api_data = {
            'id': post_id,
            'content': post_content,
            'author': {
                'id': post_author_id,
                'name': f"{post_first_name} {post_last_name}".strip(),
                'email': post_email
            },
            'created_at': post_created_at.strftime('%d.%m.%Y %H:%M'),
            'updated_at': post_updated_at.strftime('%d.%m.%Y %H:%M') if post_updated_at else None,
            'is_edited': is_edited,
            'is_deleted': is_deleted
        }
        posts_api_data.append(post_api_data)
    
    print(f"\n   📝 Посты API данные:")
    print(f"      Всего постов: {len(posts_api_data)}")
    
    for i, post in enumerate(posts_api_data):
        print(f"      Пост {i+1}: {post['author']['name']} - {post['content'][:30]}...")
    
    # Проверяем логику отображения
    print(f"\n🎯 ЛОГИКА ОТОБРАЖЕНИЯ:")
    print("-" * 30)
    print(f"   JavaScript код: posts.forEach(post => {{")
    print(f"   if (post.id !== posts[0].id) {{ // Показывать пост")
    print(f"   }} else {{ // Не показывать первый пост")
    print(f"   }}")
    print()
    
    if posts_api_data:
        first_post_id = posts_api_data[0]['id']
        print(f"   Первый пост ID: {first_post_id}")
        print(f"   Посты, которые будут показаны:")
        
        for post in posts_api_data:
            if post['id'] != first_post_id:
                print(f"      ✅ Пост ID {post['id']}: {post['author']['name']}")
            else:
                print(f"      ❌ Пост ID {post['id']}: {post['author']['name']} (ПЕРВЫЙ - НЕ ПОКАЗЫВАТЬ)")
    
    print(f"\n📊 ИТОГ:")
    print(f"   Всего постов в базе: {len(posts_data)}")
    print(f"   Постов для отображения: {len(posts_api_data) - 1 if posts_api_data else 0}")
    print(f"   Должно отображаться: {len(posts_data) - 1} постов")

def main():
    """Основная функция"""
    print("🔍 ТЕСТИРОВАНИЕ API ЗАГРУЗКИ КОНТЕНТА ТЕМЫ")
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
        test_topic_content_api(conn)
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False
        
    finally:
        conn.close()
        print("\n🔌 Соединение с базой данных закрыто.")

if __name__ == "__main__":
    main()
