#!/usr/bin/env python3
"""
Скрипт для проверки структуры продакшн базы данных
"""

import os
import psycopg2

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

def check_database_structure(conn):
    """Проверить структуру базы данных"""
    try:
        cursor = conn.cursor()
        
        print("🔍 Проверяем структуру базы данных...")
        
        # Получаем список всех таблиц
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        
        print(f"\n📋 Найдено таблиц: {len(tables)}")
        print("=" * 50)
        
        for table in tables:
            table_name = table[0]
            print(f"📄 Таблица: {table_name}")
            
            # Получаем колонки для каждой таблицы
            cursor.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position;
            """, (table_name,))
            
            columns = cursor.fetchall()
            
            for col in columns:
                col_name, data_type, nullable = col
                nullable_str = "NULL" if nullable == "YES" else "NOT NULL"
                print(f"   └─ {col_name} ({data_type}) {nullable_str}")
            
            # Получаем количество записей
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"   📊 Записей: {count}")
            print()
        
        return [table[0] for table in tables]
        
    except Exception as e:
        print(f"❌ Ошибка при проверке структуры: {e}")
        return []

def check_specific_tables(conn, table_names):
    """Проверить содержимое конкретных таблиц"""
    cursor = conn.cursor()
    
    # Проверяем таблицы, связанные с сообщениями/переписками
    interesting_tables = ['users', 'topics', 'messages', 'conversations', 'chats', 'posts', 'comments']
    
    print("🔍 Проверяем интересующие таблицы...")
    
    for table in interesting_tables:
        if table in table_names:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"✅ {table}: {count} записей")
                
                if count > 0:
                    # Показываем несколько примеров записей
                    cursor.execute(f"SELECT * FROM {table} LIMIT 3")
                    samples = cursor.fetchall()
                    
                    cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = %s ORDER BY ordinal_position", (table,))
                    columns = [col[0] for col in cursor.fetchall()]
                    
                    print(f"   Колонки: {', '.join(columns)}")
                    for i, sample in enumerate(samples):
                        print(f"   Пример {i+1}: {sample}")
                    print()
                    
            except Exception as e:
                print(f"❌ Ошибка при проверке {table}: {e}")
        else:
            print(f"❌ Таблица {table} не найдена")

def main():
    """Основная функция"""
    print("🔍 ПРОВЕРКА СТРУКТУРЫ ПРОДАКШН БАЗЫ ДАННЫХ")
    print("=" * 60)
    
    # Подключаемся к базе данных
    conn = get_production_db_connection()
    if not conn:
        return False
    
    try:
        # Проверяем структуру
        tables = check_database_structure(conn)
        
        if tables:
            # Проверяем конкретные таблицы
            check_specific_tables(conn, tables)
        
        print("✅ Проверка завершена!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        
    finally:
        conn.close()
        print("\n🔌 Соединение с базой данных закрыто.")

if __name__ == "__main__":
    main()
