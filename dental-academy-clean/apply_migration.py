#!/usr/bin/env python3
"""
Скрипт для применения миграции БД на продакшене
"""
import os
import sys
from pathlib import Path

# Добавить текущую директорию в путь
sys.path.insert(0, str(Path(__file__).parent))

try:
    import psycopg2
    from urllib.parse import urlparse
except ImportError:
    print("❌ Необходимо установить psycopg2:")
    print("   pip install psycopg2-binary")
    sys.exit(1)

def apply_migration():
    """Применить миграцию к базе данных"""
    
    # Получить DATABASE_URL
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        print("❌ DATABASE_URL не установлен в переменных окружения!")
        print("   Установите его командой: export DATABASE_URL='postgresql://...'")
        sys.exit(1)
    
    print(f"🔗 Подключаемся к БД...")
    
    try:
        # Подключиться к БД
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("✅ Подключение успешно")
        
        # Прочитать файл миграции
        migration_file = Path('migrations/add_missing_columns.sql')
        if not migration_file.exists():
            print(f"❌ Файл миграции не найден: {migration_file}")
            sys.exit(1)
        
        print(f"📄 Читаем файл миграции: {migration_file}")
        
        # Выполнить миграцию
        print("🔧 Применяем миграцию...")
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        # Выполнить SQL
        cur.execute(sql)
        
        # Сохранить изменения
        conn.commit()
        
        print("✅ Миграция применена успешно!")
        
        # Проверить результат
        print("\n🔍 Проверяем результаты миграции...")
        
        # Проверить questions.profession
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = 'questions' 
            AND column_name = 'profession'
        """)
        
        result = cur.fetchone()
        if result:
            print(f"   ✅ questions.profession: {result[1]} (nullable: {result[2]})")
        else:
            print("   ❌ questions.profession не найден")
        
        # Проверить personal_learning_plan
        cur.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns 
            WHERE table_name = 'personal_learning_plan' 
            AND column_name IN ('spaced_repetition_enabled', 'sr_algorithm', 'next_review_date', 'sr_streak', 'total_sr_reviews')
            ORDER BY column_name
        """)
        
        results = cur.fetchall()
        if results:
            print(f"   ✅ personal_learning_plan - найдено {len(results)} столбцов:")
            for row in results:
                print(f"      - {row[0]}: {row[1]}")
        else:
            print("   ❌ Столбцы в personal_learning_plan не найдены")
        
        print("\n🎉 Миграция завершена успешно!")
        print("   Пожалуйста, перезапустите приложение для применения изменений")
        
        # Закрыть соединение
        cur.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Ошибка при работе с БД: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 СКРИПТ ПРИМЕНЕНИЯ МИГРАЦИИ БД")
    print("=" * 60)
    print()
    
    apply_migration()
    
    print()
    print("=" * 60)







