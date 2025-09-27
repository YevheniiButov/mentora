#!/usr/bin/env python3
"""
Миграция: Добавление полей для soft delete в таблицу forum_topics
Добавляет поля: is_deleted, deleted_at, deleted_by
"""

import os
import sys
import psycopg2
from datetime import datetime, timezone

def get_database_url():
    """Получить DATABASE_URL из переменных окружения"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ ОШИБКА: DATABASE_URL не найден в переменных окружения")
        print("Установите переменную: export DATABASE_URL='postgresql://...'")
        sys.exit(1)
    return database_url

def add_deletion_fields():
    """Добавить поля для soft delete в forum_topics"""
    
    database_url = get_database_url()
    
    try:
        print("🔧 ДОБАВЛЕНИЕ ПОЛЕЙ SOFT DELETE В FORUM_TOPICS")
        print("=" * 60)
        
        # Подключение к базе данных
        conn = psycopg2.connect(database_url)
        conn.autocommit = False
        cur = conn.cursor()
        
        print("✅ Подключение к базе данных установлено")
        
        # Проверим, существуют ли уже поля
        cur.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'forum_topics' 
            AND column_name IN ('is_deleted', 'deleted_at', 'deleted_by')
        """)
        existing_columns = [row[0] for row in cur.fetchall()]
        
        print(f"📊 Существующие колонки: {existing_columns}")
        
        # Добавляем is_deleted
        if 'is_deleted' not in existing_columns:
            print("➕ Добавляем колонку is_deleted...")
            cur.execute("""
                ALTER TABLE forum_topics 
                ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE
            """)
            print("✅ Колонка is_deleted добавлена")
        else:
            print("ℹ️ Колонка is_deleted уже существует")
        
        # Добавляем deleted_at
        if 'deleted_at' not in existing_columns:
            print("➕ Добавляем колонку deleted_at...")
            cur.execute("""
                ALTER TABLE forum_topics 
                ADD COLUMN deleted_at TIMESTAMP WITH TIME ZONE
            """)
            print("✅ Колонка deleted_at добавлена")
        else:
            print("ℹ️ Колонка deleted_at уже существует")
        
        # Добавляем deleted_by
        if 'deleted_by' not in existing_columns:
            print("➕ Добавляем колонку deleted_by...")
            cur.execute("""
                ALTER TABLE forum_topics 
                ADD COLUMN deleted_by INTEGER REFERENCES "user"(id)
            """)
            print("✅ Колонка deleted_by добавлена")
        else:
            print("ℹ️ Колонка deleted_by уже существует")
        
        # Создаем индекс для оптимизации запросов
        print("🔍 Создаем индекс для is_deleted...")
        try:
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_forum_topics_is_deleted 
                ON forum_topics(is_deleted)
            """)
            print("✅ Индекс создан")
        except Exception as e:
            print(f"ℹ️ Индекс уже существует или ошибка: {e}")
        
        # Проверяем структуру таблицы
        print("\n📋 Проверяем структуру таблицы forum_topics...")
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'forum_topics' 
            ORDER BY ordinal_position
        """)
        
        columns = cur.fetchall()
        print("Структура таблицы forum_topics:")
        for col in columns:
            print(f"  - {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
        
        # Коммитим изменения
        conn.commit()
        print("\n✅ Миграция успешно завершена!")
        print("🎉 Поля is_deleted, deleted_at, deleted_by добавлены в forum_topics")
        
    except Exception as e:
        print(f"\n❌ ОШИБКА при выполнении миграции: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
        sys.exit(1)
    
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    add_deletion_fields()
