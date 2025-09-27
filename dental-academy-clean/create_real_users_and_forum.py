#!/usr/bin/env python3
"""
Скрипт для создания реальных пользователей и тем форума
Создает пользователей с правильными именами и данными из скриншотов
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

def create_real_users(conn):
    """Создать реальных пользователей из скриншотов"""
    cursor = conn.cursor()
    
    users_data = [
        {
            'name': 'Liliam',
            'email': 'liliam@example.com',
            'phone': '+31 6 21657736'
        },
        {
            'name': 'Ümit Isiklar',
            'email': 'umit@example.com',
            'phone': '+32 485 82 22 30'
        },
        {
            'name': 'Bahar Yıldız',
            'email': 'bahar@example.com',
            'phone': '+31 6 85293141'
        },
        {
            'name': 'Drs. B. De lange',
            'email': 'dr.bdelange@example.com',
            'phone': '+31 6 38699969'
        },
        {
            'name': 'Viktoriia',
            'email': 'viktoriia@example.com',
            'phone': '+31 6 15403678'
        },
        {
            'name': 'Shiva',
            'email': 'shiva@example.com',
            'phone': '+31 6 28130004'
        },
        {
            'name': 'Karlien Bruwer',
            'email': 'karlien@example.com',
            'phone': '+27 60 996 6634'
        },
        {
            'name': 'Pelin Babayigit',
            'email': 'pelin@example.com',
            'phone': '+90 536 202 01'
        },
        {
            'name': 'Rinsy',
            'email': 'rinsy@example.com',
            'phone': '+91 85900 24133'
        },
        {
            'name': 'Yuliya Termonia',
            'email': 'yuliya@example.com',
            'phone': '+32 456 18 65 74'
        },
        {
            'name': 'Rami',
            'email': 'rami@example.com',
            'phone': '+31 6 87917954'
        }
    ]
    
    users = []
    
    print("👥 Создание реальных пользователей...")
    for user_data in users_data:
        # Проверяем, существует ли пользователь
        cursor.execute('SELECT id FROM "user" WHERE email = %s', (user_data['email'],))
        existing_user = cursor.fetchone()
        
        if existing_user:
            user_id = existing_user[0]
            print(f"👤 Пользователь {user_data['name']} уже существует (ID: {user_id})")
        else:
            # Создаем нового пользователя с минимальными полями
            cursor.execute('''
                INSERT INTO "user" (
                    first_name, last_name, email, phone, 
                    password_hash, created_at, is_active
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (
                user_data['name'].split()[0] if ' ' in user_data['name'] else user_data['name'],
                user_data['name'].split()[1] if ' ' in user_data['name'] else '',
                user_data['email'],
                user_data['phone'],
                'hashed_password_123',  # Временный пароль
                datetime.now(),
                True
            ))
            user_id = cursor.fetchone()[0]
            print(f"✅ Создан пользователь {user_data['name']} (ID: {user_id})")
        
        users.append({
            'id': user_id,
            'name': user_data['name'],
            'email': user_data['email'],
            'phone': user_data['phone']
        })
    
    conn.commit()
    return users

def create_forum_topics(conn, users):
    """Создать темы форума с реальными пользователями"""
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
    
    # Создаем пользователей для поиска
    user_lookup = {user['name']: user['id'] for user in users}
    
    # Данные для тем и постов
    topics_data = [
        {
            'title': 'Taal certificaten en diploma erkenning',
            'description': 'Discussie over welke taal certificaten nodig zijn voor diploma erkenning',
            'author': 'Liliam',
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
            'author': 'Karlien Bruwer',
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
            'author': 'Shiva',
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
    
    created_topics = []
    
    print("💬 Создание тем и постов...")
    for topic_data in topics_data:
        # Получаем автора темы
        topic_author_id = user_lookup.get(topic_data['author'])
        if not topic_author_id:
            print(f"❌ Автор темы {topic_data['author']} не найден!")
            continue
        
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
            user_id = user_lookup.get(post_data['user'])
            if not user_id:
                print(f"⚠️ Пользователь {post_data['user']} не найден, пропускаем пост")
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
    
    return len(created_topics)

def main():
    """Основная функция"""
    print("🚀 СОЗДАНИЕ РЕАЛЬНЫХ ПОЛЬЗОВАТЕЛЕЙ И ФОРУМА")
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
        # Создаем реальных пользователей
        print("\n👥 ШАГ 1: Создание реальных пользователей")
        users = create_real_users(conn)
        
        # Создаем темы форума
        print("\n💬 ШАГ 2: Создание тем форума")
        topics_count = create_forum_topics(conn, users)
        
        print(f"\n🎉 ГОТОВО! Результат:")
        print(f"   - Пользователей: {len(users)}")
        print(f"   - Тем: {topics_count}")
        print("   - Постов: множество")
        print("\nКомьюнити форум создан с реальными пользователями! 📱")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()
        print("\n🔌 Соединение с базой данных закрыто.")

if __name__ == "__main__":
    main()
