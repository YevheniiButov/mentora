#!/usr/bin/env python3
"""
Исправление ограничений внешних ключей для автоматического каскадного удаления
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

def fix_foreign_key_constraints():
    """Настраивает каскадное удаление для внешних ключей"""
    
    with app.app_context():
        try:
            print("🔧 Настройка каскадного удаления для внешних ключей...")
            
            # 1. Удаляем старое ограничение
            print("1️⃣ Удаляем старое ограничение foreign key...")
            db.session.execute(text("""
                ALTER TABLE registration_visitors 
                DROP CONSTRAINT IF EXISTS registration_visitors_user_id_fkey
            """))
            
            # 2. Добавляем новое ограничение с CASCADE
            print("2️⃣ Добавляем новое ограничение с CASCADE...")
            db.session.execute(text("""
                ALTER TABLE registration_visitors 
                ADD CONSTRAINT registration_visitors_user_id_fkey 
                FOREIGN KEY (user_id) REFERENCES "user"(id) 
                ON DELETE CASCADE
            """))
            
            # 3. Проверяем, есть ли другие таблицы с внешними ключами на user.id
            print("3️⃣ Проверяем другие таблицы с внешними ключами...")
            
            # Получаем список всех внешних ключей, ссылающихся на таблицу user
            result = db.session.execute(text("""
                SELECT 
                    tc.table_name, 
                    kcu.column_name, 
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name,
                    tc.constraint_name
                FROM 
                    information_schema.table_constraints AS tc 
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                      AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                      AND ccu.table_schema = tc.table_schema
                WHERE tc.constraint_type = 'FOREIGN KEY' 
                AND ccu.table_name = 'user'
                AND ccu.column_name = 'id'
            """))
            
            foreign_keys = result.fetchall()
            
            if foreign_keys:
                print("📋 Найдены внешние ключи, ссылающиеся на user.id:")
                for fk in foreign_keys:
                    table_name, column_name, foreign_table, foreign_column, constraint_name = fk
                    print(f"   📊 {table_name}.{column_name} -> {foreign_table}.{foreign_column} ({constraint_name})")
                    
                    # Обновляем ограничение для каскадного удаления
                    if table_name != 'registration_visitors':  # Уже обработали выше
                        try:
                            print(f"   🔧 Обновляем ограничение для {table_name}...")
                            db.session.execute(text(f"""
                                ALTER TABLE {table_name} 
                                DROP CONSTRAINT IF EXISTS {constraint_name}
                            """))
                            db.session.execute(text(f"""
                                ALTER TABLE {table_name} 
                                ADD CONSTRAINT {constraint_name} 
                                FOREIGN KEY ({column_name}) REFERENCES {foreign_table}({foreign_column}) 
                                ON DELETE CASCADE
                            """))
                            print(f"   ✅ Обновлено ограничение для {table_name}")
                        except Exception as e:
                            print(f"   ⚠️ Не удалось обновить ограничение для {table_name}: {e}")
            else:
                print("ℹ️ Других внешних ключей не найдено")
            
            # 4. Сохраняем изменения
            db.session.commit()
            print("💾 Изменения сохранены в базе данных")
            
            print("✅ Каскадное удаление настроено успешно!")
            print("ℹ️ Теперь при удалении пользователя все связанные записи будут удалены автоматически")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при настройке каскадного удаления: {e}")
            db.session.rollback()
            return False

def test_cascade_deletion():
    """Тестирует каскадное удаление (создает тестового пользователя)"""
    
    with app.app_context():
        try:
            print("🧪 Тестирование каскадного удаления...")
            
            # Создаем тестового пользователя
            from models import User, RegistrationVisitor
            from datetime import datetime
            
            test_user = User(
                email="test_cascade@example.com",
                password_hash="test_hash",
                first_name="Test",
                last_name="User"
            )
            db.session.add(test_user)
            db.session.flush()  # Получаем ID без коммита
            
            user_id = test_user.id
            print(f"👤 Создан тестовый пользователь ID: {user_id}")
            
            # Создаем связанную запись в registration_visitors
            visitor = RegistrationVisitor(
                ip_address="127.0.0.1",
                page_type="test",
                entry_time=datetime.utcnow(),
                user_id=user_id,
                email_entered="test_cascade@example.com"
            )
            db.session.add(visitor)
            db.session.commit()
            
            visitor_id = visitor.id
            print(f"📊 Создана запись visitor ID: {visitor_id}")
            
            # Проверяем, что записи созданы
            user_check = User.query.get(user_id)
            visitor_check = RegistrationVisitor.query.get(visitor_id)
            print(f"✅ Пользователь существует: {user_check is not None}")
            print(f"✅ Запись visitor существует: {visitor_check is not None}")
            
            # Удаляем пользователя
            print("🗑️ Удаляем пользователя...")
            db.session.delete(user_check)
            db.session.commit()
            
            # Проверяем, что записи удалены
            user_check = User.query.get(user_id)
            visitor_check = RegistrationVisitor.query.get(visitor_id)
            print(f"✅ Пользователь удален: {user_check is None}")
            print(f"✅ Запись visitor удалена: {visitor_check is None}")
            
            if user_check is None and visitor_check is None:
                print("🎉 Каскадное удаление работает корректно!")
                return True
            else:
                print("❌ Каскадное удаление не работает")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка при тестировании: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_cascade_deletion()
    else:
        print("🔧 Настройка каскадного удаления...")
        success = fix_foreign_key_constraints()
        if success:
            print("\n🧪 Хотите протестировать? Запустите:")
            print("   python fix_user_deletion_constraints.py test")
        else:
            print("💥 Не удалось настроить каскадное удаление")
            sys.exit(1)
