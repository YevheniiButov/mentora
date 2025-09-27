#!/usr/bin/env python3
"""
Скрипт для настройки переписок комьюнити на продакшене
Использует forum_topics и forum_posts таблицы
"""

import os
import sys
import psycopg2
from datetime import datetime, timedelta
import random

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

def clear_community_data(conn):
    """Удалить все данные комьюнити"""
    try:
        cursor = conn.cursor()
        
        print("🧹 Начинаем очистку комьюнити...")
        
        # 1. Удаляем все посты форума
        print("📝 Удаляем все посты форума...")
        cursor.execute("DELETE FROM forum_posts")
        posts_deleted = cursor.rowcount
        print(f"   Удалено постов: {posts_deleted}")
        
        # 2. Удаляем все темы форума
        print("💬 Удаляем все темы форума...")
        cursor.execute("DELETE FROM forum_topics")
        topics_deleted = cursor.rowcount
        print(f"   Удалено тем: {topics_deleted}")
        
        # 3. Удаляем категории форума (если есть)
        print("📂 Очищаем категории форума...")
        cursor.execute("DELETE FROM forum_categories")
        categories_deleted = cursor.rowcount
        print(f"   Удалено категорий: {categories_deleted}")
        
        # Подтверждаем изменения
        conn.commit()
        
        print("✅ Все данные комьюнити очищены!")
        print(f"📊 Статистика очистки:")
        print(f"   - Постов: {posts_deleted}")
        print(f"   - Тем: {topics_deleted}")
        print(f"   - Категорий: {categories_deleted}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при очистке: {e}")
        conn.rollback()
        return False

def create_community_users(conn):
    """Создать пользователей для комьюнити"""
    cursor = conn.cursor()
    
    users_data = [
        {
            'name': 'Liliam',
            'email': 'liliam@example.com',
            'phone': '+31 6 21657736',
            'avatar': 'L',
            'avatar_color': 'blue'
        },
        {
            'name': 'Ümit Isiklar',
            'email': 'umit@example.com',
            'phone': '+32 485 82 22 30',
            'avatar': 'Ü',
            'avatar_color': 'green'
        },
        {
            'name': 'Bahar Yıldız',
            'email': 'bahar@example.com',
            'phone': '+31 6 85293141',
            'avatar': 'B',
            'avatar_color': 'purple'
        },
        {
            'name': 'Drs. B. De lange',
            'email': 'dr.bdelange@example.com',
            'phone': '+31 6 38699969',
            'avatar': 'D',
            'avatar_color': 'blue'
        },
        {
            'name': 'Viktoriia',
            'email': 'viktoriia@example.com',
            'phone': '+31 6 15403678',
            'avatar': 'V',
            'avatar_color': 'pink'
        },
        {
            'name': 'Shiva',
            'email': 'shiva@example.com',
            'phone': '+31 6 28130004',
            'avatar': 'S',
            'avatar_color': 'orange'
        },
        {
            'name': 'Karlien Bruwer',
            'email': 'karlien@example.com',
            'phone': '+27 60 996 6634',
            'avatar': 'K',
            'avatar_color': 'pink'
        },
        {
            'name': 'Pelin Babayigit',
            'email': 'pelin@example.com',
            'phone': '+90 536 202 01',
            'avatar': 'P',
            'avatar_color': 'blue'
        },
        {
            'name': 'Rinsy',
            'email': 'rinsy@example.com',
            'phone': '+91 85900 24133',
            'avatar': 'R',
            'avatar_color': 'purple'
        },
        {
            'name': 'Yuliya Termonia',
            'email': 'yuliya@example.com',
            'phone': '+32 456 18 65 74',
            'avatar': 'Y',
            'avatar_color': 'green'
        },
        {
            'name': 'Rami',
            'email': 'rami@example.com',
            'phone': '+31 6 87917954',
            'avatar': 'R',
            'avatar_color': 'red'
        }
    ]
    
    users = []
    
    print("👥 Создание пользователей...")
    for user_data in users_data:
        # Проверяем, существует ли пользователь
        cursor.execute("SELECT id FROM \"user\" WHERE email = %s", (user_data['email'],))
        existing_user = cursor.fetchone()
        
        if existing_user:
            user_id = existing_user[0]
            print(f"👤 Пользователь {user_data['name']} уже существует (ID: {user_id})")
        else:
            # Создаем нового пользователя
            cursor.execute("""
                INSERT INTO \"user\" (
                    first_name, last_name, email, phone, 
                    password_hash, is_verified, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                user_data['name'].split()[0] if ' ' in user_data['name'] else user_data['name'],
                user_data['name'].split()[1] if ' ' in user_data['name'] else '',
                user_data['email'],
                user_data['phone'],
                'hashed_password_123',  # Временный пароль
                True,
                datetime.now()
            ))
            user_id = cursor.fetchone()[0]
            print(f"✅ Создан пользователь {user_data['name']} (ID: {user_id})")
        
        users.append({
            'id': user_id,
            'name': user_data['name'],
            'email': user_data['email'],
            'phone': user_data['phone'],
            'avatar': user_data['avatar'],
            'avatar_color': user_data['avatar_color']
        })
    
    conn.commit()
    return users

def create_community_forum(conn, users):
    """Создать форум комьюнити с темами и постами"""
    cursor = conn.cursor()
    
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
    
    # Создаем темы и посты
    topics_data = [
        {
            'title': 'Taal certificaten en diploma erkenning',
            'description': 'Discussie over welke taal certificaten nodig zijn voor diploma erkenning',
            'posts': [
                {
                    'user': 'Liliam',
                    'content': "Goedemiddag collega's heeft iemand material voor lezen exam van BGB academy?",
                    'timestamp': '13:13',
                    'date_offset': 0
                },
                {
                    'user': 'Ümit Isiklar',
                    'content': "Goedemiddag Collega's. Ik wil aan Nederland aanvragen om diploma gelijkwaardig te hebben.Welke niveau taal certificaat moet ik hebben? Engels en Nederlands.Alvast bedankt.",
                    'timestamp': '13:22',
                    'date_offset': 0
                },
                {
                    'user': 'Ümit Isiklar',
                    'content': "ik ben een nieuwe lid hier",
                    'timestamp': '13:22',
                    'date_offset': 0
                },
                {
                    'user': 'Liliam',
                    'content': "B2+",
                    'timestamp': '13:22',
                    'date_offset': 0
                },
                {
                    'user': 'Ümit Isiklar',
                    'content': "Engels ook?",
                    'timestamp': '13:23',
                    'date_offset': 0
                },
                {
                    'user': 'Liliam',
                    'content': "Volgens mij wel",
                    'timestamp': '13:23',
                    'date_offset': 0
                },
                {
                    'user': 'Bahar Yıldız',
                    'content': "B2 lezen voor Engels ook heb jij nodig",
                    'timestamp': '13:27',
                    'date_offset': 0
                },
                {
                    'user': 'Ümit Isiklar',
                    'content': "Ok,dank u wel",
                    'timestamp': '13:24',
                    'date_offset': 0
                },
                {
                    'user': 'Ümit Isiklar',
                    'content': "Dank u wel.",
                    'timestamp': '13:34',
                    'date_offset': 0
                },
                {
                    'user': 'Drs. B. De lange',
                    'content': "C1 Nederlands",
                    'timestamp': '20:01',
                    'date_offset': 0
                }
            ]
        },
        {
            'title': 'BIG Registratie en werkprocessen',
            'description': 'Informatie over BIG registratie en nieuwe regels voor IND',
            'posts': [
                {
                    'user': 'Karlien Bruwer',
                    'content': 'Dag, heeft iemand informatie over het proces van een tijdelijk "onofficiële" BIG registratie?',
                    'timestamp': '10:10',
                    'date_offset': -1
                },
                {
                    'user': 'Karlien Bruwer',
                    'content': 'Dag, heeft iemand informatie over het proces van een tijdelijk "onofficiële" BIG registratie? Ik wel geïnteresseerd... mag ik je vragen waar je over deze informatie hebt gehoord? Alvast bedankt',
                    'timestamp': '11:22',
                    'date_offset': -1
                },
                {
                    'user': 'Pelin Babayigit',
                    'content': 'Kan ik hier meer over leren, alstublieft? Alvast bedankt',
                    'timestamp': '11:44',
                    'date_offset': -1
                },
                {
                    'user': 'Karlien Bruwer',
                    'content': 'Ik heb gehoort dat het een nieuwe "regel" is voor de IND (om te werken voordat je BIG registratie hebt) maar ik weet niet veel. Ik zal laat weten als Ik meer weet.',
                    'timestamp': '12:06',
                    'date_offset': -1
                },
                {
                    'user': 'Rinsy',
                    'content': 'Zeer geinteresseerd',
                    'timestamp': '12:07',
                    'date_offset': -1
                },
                {
                    'user': 'Yuliya Termonia',
                    'content': 'Ik heb in januari in webinar deel genomen. Ze hebben niets erover gezegd. Misschien praat je over het werk onder supervisie (stage) als een deel van het geheel proces?',
                    'timestamp': '12:29',
                    'date_offset': -1
                },
                {
                    'user': 'Rami',
                    'content': 'Hallo allemaal is er iemand die het spreken-examen op de Babel School wil doen? En Is er iemand die de test heeft gedaan en informatie met ons kan delen?',
                    'timestamp': '09:58',
                    'date_offset': -4
                }
            ]
        },
        {
            'title': 'BGB Examen materialen en ervaringen',
            'description': 'Delen van materialen en ervaringen voor BGB examens',
            'posts': [
                {
                    'user': 'Shiva',
                    'content': 'Hello, Heeft iemand van mijn vrienden onlangs het BGB-examen gedaan, specifiek de onderdelen Lezen en Spreken?',
                    'timestamp': '21:50',
                    'date_offset': -1
                },
                {
                    'user': 'Ümit Isiklar',
                    'content': 'Betekent het 4.1 mondeling?Dank u wel.',
                    'timestamp': '19:16',
                    'date_offset': -2
                }
            ]
        }
    ]
    
    # Создаем пользователей для поиска
    user_lookup = {user['name']: user['id'] for user in users}
    
    created_topics = []
    
    print("💬 Создание тем и постов...")
    for topic_data in topics_data:
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
            user_lookup.get('Liliam', 1),  # Автор по умолчанию
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
            user_id = user_lookup.get(post_data['user'])
            if not user_id:
                continue
            
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
                user_id,
                post_time,
                post_time,
                False,
                False
            ))
            
            print(f"   📝 Добавлен пост от {post_data['user']}: {post_data['content'][:50]}...")
    
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
    
    return len(users), len(created_topics)

def main():
    """Основная функция"""
    print("🚀 НАСТРОЙКА КОМЬЮНИТИ НА ПРОДАКШЕНЕ")
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
        # Очищаем все данные комьюнити
        print("\n🧹 ШАГ 1: Очистка существующих данных комьюнити")
        success = clear_community_data(conn)
        
        if not success:
            print("❌ Очистка не удалась!")
            return False
        
        # Создаем пользователей
        print("\n👥 ШАГ 2: Создание пользователей")
        users = create_community_users(conn)
        
        # Создаем форум
        print("\n💬 ШАГ 3: Создание форума")
        users_count, topics_count = create_community_forum(conn, users)
        
        print(f"\n🎉 ГОТОВО! Результат:")
        print(f"   - Пользователей: {users_count}")
        print(f"   - Тем: {topics_count}")
        print("   - Постов: множество")
        print("\nКомьюнити теперь выглядит как в WhatsApp! 📱")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()
        print("\n🔌 Соединение с базой данных закрыто.")

if __name__ == "__main__":
    main()
