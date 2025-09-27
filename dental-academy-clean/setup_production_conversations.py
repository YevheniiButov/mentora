#!/usr/bin/env python3
"""
Скрипт для настройки переписок на продакшене
Использует DATABASE_URL из Render Environment
"""

import os
import sys
import psycopg2
from datetime import datetime, timedelta
import random
import urllib.parse

def get_production_db_connection():
    """Получить подключение к продакшн базе данных через DATABASE_URL"""
    try:
        # Получаем DATABASE_URL из переменных окружения
        database_url = os.environ.get('DATABASE_URL')
        
        if not database_url:
            print("❌ DATABASE_URL не найден в переменных окружения!")
            print("Установите переменную DATABASE_URL:")
            print("export DATABASE_URL='postgresql://mentora_user:пароль@хост/база'")
            return None
        
        print(f"🔗 Используем DATABASE_URL: {database_url[:50]}...")
        
        # Подключаемся через DATABASE_URL
        conn = psycopg2.connect(database_url, sslmode='require')
        print("✅ Подключение к продакшн базе данных установлено")
        return conn
        
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        return None

def clear_all_conversations(conn):
    """Удалить все переписки и связанные данные"""
    try:
        cursor = conn.cursor()
        
        print("🧹 Начинаем очистку всех переписок...")
        
        # 1. Удаляем все сообщения
        print("📝 Удаляем все сообщения...")
        cursor.execute("DELETE FROM messages")
        messages_deleted = cursor.rowcount
        print(f"   Удалено сообщений: {messages_deleted}")
        
        # 2. Удаляем все темы
        print("💬 Удаляем все темы...")
        cursor.execute("DELETE FROM topics")
        topics_deleted = cursor.rowcount
        print(f"   Удалено тем: {topics_deleted}")
        
        # 3. Удаляем все категории форума (если есть)
        print("📂 Очищаем категории форума...")
        cursor.execute("DELETE FROM forum_categories")
        categories_deleted = cursor.rowcount
        print(f"   Удалено категорий: {categories_deleted}")
        
        # 4. Сбрасываем счетчики (если есть)
        print("🔢 Сбрасываем счетчики...")
        cursor.execute("UPDATE users SET topics_count = 0, messages_count = 0")
        
        # Подтверждаем изменения
        conn.commit()
        
        print("✅ Все переписки успешно очищены!")
        print(f"📊 Статистика очистки:")
        print(f"   - Сообщений: {messages_deleted}")
        print(f"   - Тем: {topics_deleted}")
        print(f"   - Категорий: {categories_deleted}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при очистке: {e}")
        conn.rollback()
        return False

def create_whatsapp_conversations(conn):
    """Создать переписки в стиле WhatsApp"""
    cursor = conn.cursor()
    
    # Список пользователей из скриншотов
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
        cursor.execute("SELECT id FROM users WHERE email = %s", (user_data['email'],))
        existing_user = cursor.fetchone()
        
        if existing_user:
            user_id = existing_user[0]
            print(f"👤 Пользователь {user_data['name']} уже существует (ID: {user_id})")
        else:
            # Создаем нового пользователя
            cursor.execute("""
                INSERT INTO users (
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
    
    # Создаем темы и сообщения
    print("💬 Создание тем и сообщений...")
    
    topics_data = [
        {
            'title': 'Collega Chat - Taal certificaten',
            'description': 'Discussie over taal certificaten en diploma erkenning',
            'messages': [
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
            'title': 'AKV Tandartsen - BIG Registratie',
            'description': 'Informatie over BIG registratie en werkprocessen',
            'messages': [
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
            'title': 'BGB Examen Materialen',
            'description': 'Delen van materialen en ervaringen voor BGB examens',
            'messages': [
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
    
    for topic_data in topics_data:
        # Создаем тему
        cursor.execute("""
            INSERT INTO topics (
                title, content, author_id, created_at, updated_at, 
                is_pinned, category, language
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            topic_data['title'],
            topic_data['description'],
            user_lookup.get('Liliam', 1),  # Автор по умолчанию
            datetime.now(),
            datetime.now(),
            False,
            'General',
            'nl'
        ))
        
        topic_id = cursor.fetchone()[0]
        created_topics.append(topic_id)
        
        print(f"✅ Создана тема: {topic_data['title']} (ID: {topic_id})")
        
        # Добавляем сообщения
        for i, msg_data in enumerate(topic_data['messages']):
            user_id = user_lookup.get(msg_data['user'])
            if not user_id:
                continue
            
            # Создаем временную метку
            base_date = datetime.now() + timedelta(days=msg_data['date_offset'])
            hour, minute = map(int, msg_data['timestamp'].split(':'))
            message_time = base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Добавляем небольшую задержку между сообщениями
            message_time += timedelta(minutes=i * 2)
            
            cursor.execute("""
                INSERT INTO messages (
                    topic_id, author_id, content, created_at, updated_at,
                    is_pinned, message_type
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                topic_id,
                user_id,
                msg_data['content'],
                message_time,
                message_time,
                False,
                'text'
            ))
            
            print(f"   📝 Добавлено сообщение от {msg_data['user']}: {msg_data['content'][:50]}...")
    
    conn.commit()
    print(f"\n🎉 Создано {len(created_topics)} тем с сообщениями!")
    
    return len(users), len(created_topics)

def main():
    """Основная функция"""
    print("🚀 НАСТРОЙКА ПЕРЕПИСОК НА ПРОДАКШЕНЕ")
    print("=" * 60)
    print(f"⏰ Время запуска: {datetime.now()}")
    
    # Проверяем переменные окружения
    if not os.environ.get('DATABASE_URL'):
        print("❌ DATABASE_URL не найден в переменных окружения!")
        print("Установите переменную DATABASE_URL:")
        print("export DATABASE_URL='postgresql://mentora_user:пароль@хост/база'")
        return False
    
    # Подключаемся к базе данных
    conn = get_production_db_connection()
    if not conn:
        return False
    
    try:
        # Очищаем все переписки
        print("\n🧹 ШАГ 1: Очистка существующих переписок")
        success = clear_all_conversations(conn)
        
        if not success:
            print("❌ Очистка не удалась!")
            return False
        
        # Создаем новые переписки
        print("\n💬 ШАГ 2: Создание новых переписок")
        users_count, topics_count = create_whatsapp_conversations(conn)
        
        print(f"\n🎉 ГОТОВО! Результат:")
        print(f"   - Пользователей: {users_count}")
        print(f"   - Тем: {topics_count}")
        print("   - Сообщений: множество")
        print("\nПереписки теперь выглядят как в WhatsApp! 📱")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        conn.rollback()
        return False
        
    finally:
        conn.close()
        print("\n🔌 Соединение с базой данных закрыто.")

if __name__ == "__main__":
    main()
