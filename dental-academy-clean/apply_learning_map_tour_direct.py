#!/usr/bin/env python3
"""
Скрипт для прямого применения миграции learning_map_tour_completed
Используется когда Alembic не может применить миграцию из-за множественных голов
"""
import sys
import os

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

def apply_migration():
    """Применить миграцию напрямую через SQL"""
    with app.app_context():
        try:
            # Проверить, существует ли колонка
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'user' 
                AND column_name = 'learning_map_tour_completed'
            """))
            exists = result.fetchone() is not None
            
            if exists:
                print("✅ Колонка learning_map_tour_completed уже существует")
            else:
                print("❌ Колонка learning_map_tour_completed не существует")
                # Добавить колонку
                db.session.execute(text("""
                    ALTER TABLE "user" 
                    ADD COLUMN learning_map_tour_completed BOOLEAN NOT NULL DEFAULT false
                """))
                db.session.commit()
                print("✅ Колонка learning_map_tour_completed успешно добавлена")
            
            # Пометить миграцию как примененную в alembic_version
            # Проверить, есть ли уже запись
            result = db.session.execute(text("""
                SELECT version_num FROM alembic_version WHERE version_num = 'a1b2c3d4e5f6'
            """))
            version_exists = result.fetchone() is not None
            
            if not version_exists:
                # Добавить версию миграции
                db.session.execute(text("""
                    INSERT INTO alembic_version (version_num) 
                    VALUES ('a1b2c3d4e5f6')
                    ON CONFLICT (version_num) DO NOTHING
                """))
                db.session.commit()
                print("✅ Миграция a1b2c3d4e5f6 помечена как примененная")
            else:
                print("✅ Миграция a1b2c3d4e5f6 уже помечена как примененная")
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            sys.exit(1)

if __name__ == '__main__':
    apply_migration()

