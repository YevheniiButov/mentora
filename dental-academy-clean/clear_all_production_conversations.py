#!/usr/bin/env python3
"""
Скрипт для полной очистки всех переписок на продакшене
Удаляет все сообщения, темы и связанные данные
"""

import os
import sys
import psycopg2
from datetime import datetime

def get_production_db_connection():
    """Получить подключение к продакшн базе данных"""
    try:
        # Продакшн параметры подключения
        conn = psycopg2.connect(
            host=os.environ.get('DATABASE_HOST', 'dpg-d0t3qvh2g6b8s7i1q1kg-a.oregon-postgres.render.com'),
            database=os.environ.get('DATABASE_NAME', 'mentora_production'),
            user=os.environ.get('DATABASE_USER', 'mentora_user'),
            password=os.environ.get('DATABASE_PASSWORD'),
            port=os.environ.get('DATABASE_PORT', '5432'),
            sslmode='require'
        )
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

def verify_cleanup(conn):
    """Проверить, что очистка прошла успешно"""
    try:
        cursor = conn.cursor()
        
        # Проверяем количество сообщений
        cursor.execute("SELECT COUNT(*) FROM messages")
        messages_count = cursor.fetchone()[0]
        
        # Проверяем количество тем
        cursor.execute("SELECT COUNT(*) FROM topics")
        topics_count = cursor.fetchone()[0]
        
        print(f"\n🔍 Проверка очистки:")
        print(f"   - Сообщений осталось: {messages_count}")
        print(f"   - Тем осталось: {topics_count}")
        
        if messages_count == 0 and topics_count == 0:
            print("✅ Очистка прошла успешно!")
            return True
        else:
            print("⚠️ Остались данные, требующие ручной очистки")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при проверке: {e}")
        return False

def main():
    """Основная функция"""
    print("🚀 СКРИПТ ПОЛНОЙ ОЧИСТКИ ПЕРЕПИСОК НА ПРОДАКШЕНЕ")
    print("=" * 60)
    print(f"⏰ Время запуска: {datetime.now()}")
    
    # Проверяем переменные окружения
    if not os.environ.get('DATABASE_PASSWORD'):
        print("❌ Переменная DATABASE_PASSWORD не установлена!")
        print("Установите пароль от продакшн базы данных:")
        print("export DATABASE_PASSWORD='ваш_пароль'")
        return False
    
    # Подключаемся к базе данных
    conn = get_production_db_connection()
    if not conn:
        return False
    
    try:
        # Выполняем очистку
        success = clear_all_conversations(conn)
        
        if success:
            # Проверяем результат
            verify_cleanup(conn)
            print("\n🎉 ГОТОВО! Все переписки очищены.")
            print("Теперь можно создавать новые переписки по скриншотам.")
        else:
            print("\n❌ Очистка не удалась. Проверьте ошибки выше.")
            
    finally:
        conn.close()
        print("\n🔌 Соединение с базой данных закрыто.")

if __name__ == "__main__":
    main()
