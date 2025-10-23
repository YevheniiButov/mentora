#!/usr/bin/env python3
"""
Миграция для добавления полей мягкого удаления пользователей
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
from models import User
from sqlalchemy import text

def add_soft_delete_fields():
    """Добавляет поля для мягкого удаления пользователей"""
    
    with app.app_context():
        try:
            print("🔄 Добавление полей для мягкого удаления пользователей...")
            
            # Проверяем, существуют ли уже поля
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('user')]
            
            if 'is_deleted' in columns:
                print("✅ Поля для мягкого удаления уже существуют!")
                return
            
            # Добавляем поля для мягкого удаления (по одному для SQLite)
            with db.engine.connect() as connection:
                # Добавляем is_deleted
                connection.execute(text("ALTER TABLE \"user\" ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE"))
                connection.commit()
                
                # Добавляем deleted_at
                connection.execute(text("ALTER TABLE \"user\" ADD COLUMN deleted_at TIMESTAMP"))
                connection.commit()
                
                # Добавляем deleted_by
                connection.execute(text("ALTER TABLE \"user\" ADD COLUMN deleted_by INTEGER REFERENCES \"user\"(id)"))
                connection.commit()
            
            print("✅ Поля для мягкого удаления успешно добавлены!")
            print("   - is_deleted: BOOLEAN DEFAULT FALSE")
            print("   - deleted_at: TIMESTAMP")
            print("   - deleted_by: INTEGER REFERENCES user(id)")
            
        except Exception as e:
            print(f"❌ Ошибка при добавлении полей: {str(e)}")
            return False
        
        return True

if __name__ == "__main__":
    success = add_soft_delete_fields()
    if success:
        print("\n🎉 Миграция завершена успешно!")
        print("Теперь вы можете использовать мягкое удаление пользователей в админ панели.")
    else:
        print("\n❌ Миграция не удалась!")
        sys.exit(1)
