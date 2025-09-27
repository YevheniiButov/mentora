#!/usr/bin/env python3
"""
Рабочий скрипт для создания форума
Убирает поле slug из forum_topics, так как его нет в схеме
"""

import os
import sys
import psycopg2
from datetime import datetime, timedelta
import re

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

def create_slug(text):
    """Создать slug из текста"""
    # Конвертируем в lowercase и заменяем пробелы на дефисы
    slug = text.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)  # Удаляем спецсимволы
    slug = re.sub(r'[-\s]+', '-', slug)   # Заменяем пробелы и множественные дефисы
    return slug.strip('-')

def create_forum_categories(conn):
    """Создать категории форума с правильными полями"""
    cursor = conn.cursor()
    
    print("📂 Создание категории форума...")
    
    # Проверяем структуру таблицы forum_categories
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'forum_categories'
        ORDER BY ordinal_position;
    """)
    
    columns = [row[0] for row in cursor.fetchall()]
    print(f"📋 Колонки forum_categories: {columns}")
    
    # Создаем категорию с обязательными полями
    try:
        category_name = 'Collega Chat'
        category_slug = create_slug(category_name)
        
        cursor.execute("""
            INSERT INTO forum_categories (
                name, slug, description, is_active, created_at
            ) VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            category_name,
            category_slug,
            'Discussie tussen collega\'s over BIG registratie, examens en carrière',
            True,
            datetime.now()
        ))
        
        category_id = cursor.fetchone()[0]
        print(f"✅ Создана категория: {category_name} (slug: {category_slug}, ID: {category_id})")
        return category_id
        
    except Exception as e:
        print(f"❌ Ошибка создания категории: {e}")
        return None

def create_forum_topics(conn, category_id):
    """Создать темы форума"""
    cursor = conn.cursor()
    
    # Получаем пользователей для создания тем
    cursor.execute("SELECT id, first_name, last_name FROM \"user\" WHERE email LIKE '%@example.com' ORDER BY id DESC LIMIT 11")
    users = cursor.fetchall()
    
    print(f"👥 Найдено пользователей: {len(users)}")
    
    # Создаем lookup для пользователей
    user_lookup = {}
    for user in users:
        user_id, first_name, last_name = user
        name = f"{first_name} {last_name}".strip()
        user_lookup[name] = user_id
        print(f"   👤 {name} (ID: {user_id})")
    
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
                    'user': 'Drs. B.',
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
        
        # Проверяем структуру таблицы forum_topics
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'forum_topics'
            ORDER BY ordinal_position;
        """)
        
        topic_columns = [row[0] for row in cursor.fetchall()]
        print(f"📋 Колонки forum_topics: {topic_columns}")
        
        # Создаем тему БЕЗ поля slug (его нет в схеме)
        try:
            topic_title = topic_data['title']
            
            cursor.execute("""
                INSERT INTO forum_topics (
                    title, content, category_id, author_id, created_at, updated_at
                ) VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                topic_title,
                topic_data['description'],
                category_id,
                topic_author_id,
                datetime.now(),
                datetime.now()
            ))
            
            topic_id = cursor.fetchone()[0]
            created_topics.append(topic_id)
            
            print(f"✅ Создана тема: {topic_title} (ID: {topic_id})")
            
        except Exception as e:
            print(f"❌ Ошибка создания темы {topic_data['title']}: {e}")
            continue
        
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
            
            try:
                cursor.execute("""
                    INSERT INTO forum_posts (
                        content, topic_id, author_id, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s)
                """, (
                    post_data['content'],
                    topic_id,
                    user_id,
                    post_time,
                    post_time
                ))
                
                print(f"   📝 Добавлен пост от {post_data['user']}: {post_data['content'][:50]}...")
                
            except Exception as e:
                print(f"❌ Ошибка создания поста: {e}")
                continue
    
    conn.commit()
    print(f"\n🎉 Создано {len(created_topics)} тем с постами!")
    
    return len(created_topics)

def main():
    """Основная функция"""
    print("🚀 РАБОЧИЙ СКРИПТ ФОРУМА (БЕЗ SLUG В ТЕМАХ)")
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
        # Создаем категорию форума
        print("\n📂 ШАГ 1: Создание категории форума")
        category_id = create_forum_categories(conn)
        
        if not category_id:
            print("❌ Не удалось создать категорию!")
            return False
        
        # Создаем темы форума
        print("\n💬 ШАГ 2: Создание тем форума")
        topics_count = create_forum_topics(conn, category_id)
        
        print(f"\n🎉 ГОТОВО! Результат:")
        print(f"   - Категорий: 1")
        print(f"   - Тем: {topics_count}")
        print("   - Постов: множество")
        print("\nФорум создан успешно! 📱")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()
        print("\n🔌 Соединение с базой данных закрыто.")

if __name__ == "__main__":
    main()
