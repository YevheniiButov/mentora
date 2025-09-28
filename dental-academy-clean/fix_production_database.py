#!/usr/bin/env python3
"""
Скрипт для исправления базы данных на продакшене
Добавляет недостающие поля для логирования имен
"""

import sys
import os
sys.path.append('.')

from app import app, db
from sqlalchemy import text, inspect

def check_and_add_missing_columns():
    """Проверяет и добавляет недостающие колонки в таблицу registration_visitors"""
    
    with app.app_context():
        try:
            print("=== ПРОВЕРКА И ИСПРАВЛЕНИЕ БАЗЫ ДАННЫХ ===")
            
            # Проверяем, существует ли таблица registration_visitors
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            if 'registration_visitors' not in tables:
                print("❌ Таблица registration_visitors не найдена!")
                return False
            
            print("✅ Таблица registration_visitors найдена")
            
            # Получаем список колонок
            columns = [col['name'] for col in inspector.get_columns('registration_visitors')]
            print(f"Существующие колонки: {columns}")
            
            # Проверяем и добавляем недостающие колонки
            missing_columns = []
            
            if 'first_name_entered' not in columns:
                missing_columns.append('first_name_entered')
                print("⚠️ Колонка first_name_entered отсутствует")
            else:
                print("✅ Колонка first_name_entered существует")
                
            if 'last_name_entered' not in columns:
                missing_columns.append('last_name_entered')
                print("⚠️ Колонка last_name_entered отсутствует")
            else:
                print("✅ Колонка last_name_entered существует")
                
            if 'name_entered_at' not in columns:
                missing_columns.append('name_entered_at')
                print("⚠️ Колонка name_entered_at отсутствует")
            else:
                print("✅ Колонка name_entered_at существует")
            
            # Добавляем недостающие колонки
            if missing_columns:
                print(f"\n🔧 Добавляем недостающие колонки: {missing_columns}")
                
                for column in missing_columns:
                    try:
                        if column in ['first_name_entered', 'last_name_entered']:
                            # Добавляем VARCHAR колонки с индексом
                            db.session.execute(text(f'ALTER TABLE registration_visitors ADD COLUMN {column} VARCHAR(100)'))
                            db.session.execute(text(f'CREATE INDEX ix_registration_visitors_{column} ON registration_visitors ({column})'))
                            print(f"✅ Добавлена колонка {column} с индексом")
                        elif column == 'name_entered_at':
                            # Добавляем DATETIME колонку
                            db.session.execute(text(f'ALTER TABLE registration_visitors ADD COLUMN {column} DATETIME'))
                            print(f"✅ Добавлена колонка {column}")
                            
                    except Exception as e:
                        print(f"❌ Ошибка при добавлении колонки {column}: {e}")
                        db.session.rollback()
                        return False
                
                db.session.commit()
                print("✅ Все колонки успешно добавлены!")
            else:
                print("✅ Все необходимые колонки уже существуют")
            
            # Финальная проверка
            print("\n=== ФИНАЛЬНАЯ ПРОВЕРКА ===")
            final_columns = [col['name'] for col in inspector.get_columns('registration_visitors')]
            required_columns = ['first_name_entered', 'last_name_entered', 'name_entered_at']
            
            for col in required_columns:
                if col in final_columns:
                    print(f"✅ {col} - OK")
                else:
                    print(f"❌ {col} - ОТСУТСТВУЕТ")
                    return False
            
            print("\n🎉 База данных успешно исправлена!")
            return True
            
        except Exception as e:
            print(f"❌ Критическая ошибка: {e}")
            db.session.rollback()
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = check_and_add_missing_columns()
    if success:
        print("\n✅ Скрипт выполнен успешно!")
        sys.exit(0)
    else:
        print("\n❌ Скрипт завершился с ошибкой!")
        sys.exit(1)


