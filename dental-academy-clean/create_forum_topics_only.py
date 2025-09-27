#!/usr/bin/env python3
"""
Скрипт для создания тем форума без создания пользователей
Использует существующих пользователей
"""

import os
import sys
import psycopg2
from datetime import datetime, timedelta

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

def get_existing_users(conn):
    """Получить существующих пользователей"""
    cursor = conn.cursor()
    
    print("👥 Получение существующих пользователей...")
    
    # Получаем всех пользователей
    cursor.execute("""
        SELECT id, first_name, last_name, email 
        FROM "user" 
        WHERE is_active = true
        ORDER BY created_at DESC
        LIMIT 20
    """)
    
    users = cursor.fetchall()
    
    print(f"✅ Найдено пользователей: {len(users)}")
    
    for user in users:
        user_id, first_name, last_name, email = user
        name = f"{first_name} {last_name}".strip()
        print(f"   👤 {name} ({email}) - ID: {user_id}")
    
    return users

def create_forum_topics(conn, users):
    """Создать темы форума с существующими пользователями"""
    cursor = conn.cursor()
    
    # Выбираем первых нескольких пользователей для создания тем
    selected_users = users[:5] if len(users) >= 5 else users
    
    print(f"🎯 Используем {len(selected_users)} пользователей для создания тем")
    
    # Создаем категорию форума
    print("📂 Создание категории форума...")
    cursor.execute("""
        INSERT INTO forum_categories (
            name, description, order_index, created_at
        ) VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (
        'Collega Chat',
        'Discussie tussen collega\'s over BIG registratie, examens en carrière',
        1,
        datetime.now()
    ))
    
    category_id = cursor.fetchone()[0]
    print(f"✅ Создана категория: Collega Chat (ID: {category_id})")
    
    # Данные для тем и постов
    topics_data = [
        {
            'title': 'Taal certificaten en diploma erkenning',
            'description': 'Discussie over welke taal certificaten nodig zijn voor diploma erkenning',
            'author_index': 0,  # Первый пользователь
            'posts': [
                {
                    'content': "Goedemiddag collega's heeft iemand material voor lezen exam van BGB academy?",
                    'author_index': 0,
                    'timestamp': '13:13',
                    'date_offset': 0
                },
                {
                    'content': "Goedemiddag Collega's. Ik wil aan Nederland aanvragen om diploma gelijkwaardig te hebben.Welke niveau taal certificaat moet ik hebben? Engels en Nederlands.Alvast bedankt.",
                    'author_index': 1 if len(selected_users) > 1 else 0,
                    'timestamp': '13:22',
                    'date_offset': 0
                },
                {
                    'content': "ik ben een nieuwe lid hier",
                    'author_index': 1 if len(selected_users) > 1 else 0,
                    'timestamp': '13:22',
                    'date_offset': 0
                },
                {
                    'content': "B2+",
                    'author_index': 0,
                    'timestamp': '13:22',
                    'date_offset': 0
                },
                {
                    'content': "Engels ook?",
                    'author_index': 1 if len(selected_users) > 1 else 0,
                    'timestamp': '13:23',
                    'date_offset': 0
                },
                {
                    'content': "Volgens mij wel",
                    'author_index': 0,
                    'timestamp': '13:23',
                    'date_offset': 0
                },
                {
                    'content': "B2 lezen voor Engels ook heb jij nodig",
                    'author_index': 2 if len(selected_users) > 2 else 1 if len(selected_users) > 1 else 0,
                    'timestamp': '13:27',
                    'date_offset': 0
                },
                {
                    'content': "Ok,dank u wel",
                    'author_index': 1 if len(selected_users) > 1 else 0,
                    'timestamp': '13:24',
                    'date_offset': 0
                },
                {
                    'content': "Dank u wel.",
                    'author_index': 1 if len(selected_users) > 1 else 0,
                    'timestamp': '13:34',
                    'date_offset': 0
                },
                {
                    'content': "C1 Nederlands",
                    'author_index': 3 if len(selected_users) > 3 else 0,
                    'timestamp': '20:01',
                    'date_offset': 0
                }
            ]
        },
        {
            'title': 'BIG Registratie en werkprocessen',
            'description': 'Informatie over BIG registratie en nieuwe regels voor IND',
            'author_index': 0,
            'posts': [
                {
                    'content': 'Dag, heeft iemand informatie over het proces van een tijdelijk "onofficiële" BIG registratie?',
                    'author_index': 0,
                    'timestamp': '10:10',
                    'date_offset': -1
                },
                {
                    'content': 'Dag, heeft iemand informatie over het proces van een tijdelijk "onofficiële" BIG registratie? Ik wel geïnteresseerd... mag ik je vragen waar je over deze informatie hebt gehoord? Alvast bedankt',
                    'author_index': 0,
                    'timestamp': '11:22',
                    'date_offset': -1
                },
                {
                    'content': 'Kan ik hier meer over leren, alstublieft? Alvast bedankt',
                    'author_index': 1 if len(selected_users) > 1 else 0,
                    'timestamp': '11:44',
                    'date_offset': -1
                },
                {
                    'content': 'Ik heb gehoort dat het een nieuwe "regel" is voor de IND (om te werken voordat je BIG registratie hebt) maar ik weet niet veel. Ik zal laat weten als Ik meer weet.',
                    'author_index': 0,
                    'timestamp': '12:06',
                    'date_offset': -1
                },
                {
                    'content': 'Zeer geinteresseerd',
                    'author_index': 2 if len(selected_users) > 2 else 1 if len(selected_users) > 1 else 0,
                    'timestamp': '12:07',
                    'date_offset': -1
                },
                {
                    'content': 'Ik heb in januari in webinar deel genomen. Ze hebben niets erover gezegd. Misschien praat je over het werk onder supervisie (stage) als een deel van het geheel proces?',
                    'author_index': 3 if len(selected_users) > 3 else 0,
                    'timestamp': '12:29',
                    'date_offset': -1
                },
                {
                    'content': 'Hallo allemaal is er iemand die het spreken-examen op de Babel School wil doen? En Is er iemand die de test heeft gedaan en informatie met ons kan delen?',
                    'author_index': 4 if len(selected_users) > 4 else 0,
                    'timestamp': '09:58',
                    'date_offset': -4
                }
            ]
        },
        {
            'title': 'BGB Examen materialen en ervaringen',
            'description': 'Delen van materialen en ervaringen voor BGB examens',
            'author_index': 0,
            'posts': [
                {
                    'content': 'Hello, Heeft iemand van mijn vrienden onlangs het BGB-examen gedaan, specifiek de onderdelen Lezen en Spreken?',
                    'author_index': 0,
                    'timestamp': '21:50',
                    'date_offset': -1
                },
                {
                    'content': 'Betekent het 4.1 mondeling?Dank u wel.',
                    'author_index': 1 if len(selected_users) > 1 else 0,
                    'timestamp': '19:16',
                    'date_offset': -2
                }
            ]
        }
    ]
    
    created_topics = []
    
    print("💬 Создание тем и постов...")
    for topic_data in topics_data:
        # Получаем автора темы
        topic_author = selected_users[topic_data['author_index']]
        topic_author_id = topic_author[0]
        
        # Создаем тему
        cursor.execute("""
            INSERT INTO forum_topics (
                title, content, category_id, author_id, created_at, updated_at,
                is_pinned, is_locked, views_count, replies_count
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            topic_data['title'],
            topic_data['description'],
            category_id,
            topic_author_id,
            datetime.now(),
            datetime.now(),
            False,
            False,
            0,
            0
        ))
        
        topic_id = cursor.fetchone()[0]
        created_topics.append(topic_id)
        
        print(f"✅ Создана тема: {topic_data['title']} (ID: {topic_id})")
        
        # Добавляем посты
        for i, post_data in enumerate(topic_data['posts']):
            # Получаем автора поста
            post_author = selected_users[post_data['author_index']]
            post_author_id = post_author[0]
            post_author_name = f"{post_author[1]} {post_author[2]}".strip()
            
            # Создаем временную метку
            base_date = datetime.now() + timedelta(days=post_data['date_offset'])
            hour, minute = map(int, post_data['timestamp'].split(':'))
            post_time = base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Добавляем небольшую задержку между постами
            post_time += timedelta(minutes=i * 2)
            
            cursor.execute("""
                INSERT INTO forum_posts (
                    content, topic_id, author_id, created_at, updated_at,
                    is_edited, is_deleted
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                post_data['content'],
                topic_id,
                post_author_id,
                post_time,
                post_time,
                False,
                False
            ))
            
            print(f"   📝 Добавлен пост от {post_author_name}: {post_data['content'][:50]}...")
    
    # Обновляем статистику тем
    for topic_id in created_topics:
        cursor.execute("""
            UPDATE forum_topics 
            SET replies_count = (
                SELECT COUNT(*) - 1 FROM forum_posts 
                WHERE topic_id = %s AND is_deleted = false
            ),
            last_reply_at = (
                SELECT MAX(created_at) FROM forum_posts 
                WHERE topic_id = %s AND is_deleted = false
            )
            WHERE id = %s
        """, (topic_id, topic_id, topic_id))
    
    conn.commit()
    print(f"\n🎉 Создано {len(created_topics)} тем с постами!")
    
    return len(created_topics)

def main():
    """Основная функция"""
    print("🚀 СОЗДАНИЕ ТЕМ ФОРУМА ДЛЯ КОМЬЮНИТИ")
    print("=" * 60)
    print(f"⏰ Время запуска: {datetime.now()}")
    
    # Проверяем переменные окружения
    if not os.environ.get('DATABASE_URL'):
        print("❌ DATABASE_URL не найден в переменных окружения!")
        return False
    
    # Подключаемся к базе данных
    conn = get_production_db_connection()
    if not conn:
        return False
    
    try:
        # Получаем существующих пользователей
        users = get_existing_users(conn)
        
        if not users:
            print("❌ Пользователи не найдены!")
            return False
        
        # Создаем темы форума
        topics_count = create_forum_topics(conn, users)
        
        print(f"\n🎉 ГОТОВО! Результат:")
        print(f"   - Тем: {topics_count}")
        print("   - Постов: множество")
        print("\nКомьюнити форум создан с существующими пользователями! 📱")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()
        print("\n🔌 Соединение с базой данных закрыто.")

if __name__ == "__main__":
    main()
