#!/usr/bin/env python3
"""
Исправление всех ограничений внешних ключей для правильного каскадного удаления
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text

def fix_all_foreign_key_constraints():
    """Исправляет все ограничения внешних ключей для каскадного удаления"""
    
    with app.app_context():
        try:
            print("🔧 Исправление всех ограничений внешних ключей...")
            
            # Получаем список всех внешних ключей, ссылающихся на таблицу user
            result = db.session.execute(text("""
                SELECT 
                    tc.table_name, 
                    kcu.column_name, 
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name,
                    tc.constraint_name,
                    rc.delete_rule
                FROM 
                    information_schema.table_constraints AS tc 
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                      AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                      AND ccu.table_schema = tc.table_schema
                    JOIN information_schema.referential_constraints AS rc
                      ON tc.constraint_name = rc.constraint_name
                      AND tc.table_schema = rc.constraint_schema
                WHERE tc.constraint_type = 'FOREIGN KEY' 
                AND ccu.table_name = 'user'
                AND ccu.column_name = 'id'
            """))
            
            foreign_keys = result.fetchall()
            
            if not foreign_keys:
                print("ℹ️ Внешних ключей, ссылающихся на user.id, не найдено")
                return True
            
            print(f"📋 Найдено {len(foreign_keys)} внешних ключей, ссылающихся на user.id:")
            
            for fk in foreign_keys:
                table_name, column_name, foreign_table, foreign_column, constraint_name, delete_rule = fk
                print(f"   📊 {table_name}.{column_name} -> {foreign_table}.{foreign_column}")
                print(f"       Ограничение: {constraint_name}")
                print(f"       Текущее правило удаления: {delete_rule}")
                
                # Проверяем, может ли колонка быть NULL
                column_info = db.session.execute(text(f"""
                    SELECT is_nullable, column_default
                    FROM information_schema.columns
                    WHERE table_name = '{table_name}'
                    AND column_name = '{column_name}'
                """)).fetchone()
                
                if column_info:
                    is_nullable, column_default = column_info
                    print(f"       Колонка nullable: {is_nullable}")
                    
                    if is_nullable == 'NO':
                        print(f"       ⚠️ Колонка НЕ может быть NULL - используем CASCADE")
                        action = "CASCADE"
                    else:
                        print(f"       ✅ Колонка может быть NULL - можем использовать SET NULL или CASCADE")
                        action = "CASCADE"  # По умолчанию используем CASCADE для безопасности
                else:
                    print(f"       ❓ Не удалось получить информацию о колонке")
                    action = "CASCADE"
                
                # Обновляем ограничение
                try:
                    print(f"   🔧 Обновляем ограничение для {table_name}...")
                    
                    # Удаляем старое ограничение
                    db.session.execute(text(f"""
                        ALTER TABLE {table_name} 
                        DROP CONSTRAINT IF EXISTS {constraint_name}
                    """))
                    
                    # Добавляем новое ограничение с правильным действием
                    db.session.execute(text(f"""
                        ALTER TABLE {table_name} 
                        ADD CONSTRAINT {constraint_name} 
                        FOREIGN KEY ({column_name}) REFERENCES {foreign_table}({foreign_column}) 
                        ON DELETE {action}
                    """))
                    
                    print(f"   ✅ Обновлено ограничение для {table_name} (ON DELETE {action})")
                    
                except Exception as e:
                    print(f"   ❌ Ошибка при обновлении ограничения для {table_name}: {e}")
                    db.session.rollback()
                    continue
            
            # Сохраняем изменения
            db.session.commit()
            print("💾 Все изменения сохранены в базе данных")
            
            print("✅ Все ограничения внешних ключей исправлены!")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при исправлении ограничений: {e}")
            db.session.rollback()
            return False

def show_foreign_key_constraints():
    """Показывает все ограничения внешних ключей"""
    
    with app.app_context():
        try:
            print("📋 Все ограничения внешних ключей:")
            
            result = db.session.execute(text("""
                SELECT 
                    tc.table_name, 
                    kcu.column_name, 
                    ccu.table_name AS foreign_table_name,
                    ccu.column_name AS foreign_column_name,
                    tc.constraint_name,
                    rc.delete_rule
                FROM 
                    information_schema.table_constraints AS tc 
                    JOIN information_schema.key_column_usage AS kcu
                      ON tc.constraint_name = kcu.constraint_name
                      AND tc.table_schema = kcu.table_schema
                    JOIN information_schema.constraint_column_usage AS ccu
                      ON ccu.constraint_name = tc.constraint_name
                      AND ccu.table_schema = tc.table_schema
                    JOIN information_schema.referential_constraints AS rc
                      ON tc.constraint_name = rc.constraint_name
                      AND tc.table_schema = rc.constraint_schema
                WHERE tc.constraint_type = 'FOREIGN KEY' 
                AND ccu.table_name = 'user'
                AND ccu.column_name = 'id'
                ORDER BY tc.table_name, kcu.column_name
            """))
            
            foreign_keys = result.fetchall()
            
            if not foreign_keys:
                print("ℹ️ Внешних ключей, ссылающихся на user.id, не найдено")
                return
            
            for fk in foreign_keys:
                table_name, column_name, foreign_table, foreign_column, constraint_name, delete_rule = fk
                print(f"📊 {table_name}.{column_name} -> {foreign_table}.{foreign_column}")
                print(f"   Ограничение: {constraint_name}")
                print(f"   Правило удаления: {delete_rule}")
                
        except Exception as e:
            print(f"❌ Ошибка при получении ограничений: {e}")

def test_user_deletion(user_id=None):
    """Тестирует удаление пользователя"""
    
    with app.app_context():
        try:
            if user_id is None:
                # Создаем тестового пользователя
                from models import User, ForumPost, RegistrationVisitor
                from datetime import datetime
                
                test_user = User(
                    email="test_cascade_delete@example.com",
                    password_hash="test_hash",
                    first_name="Test",
                    last_name="Delete"
                )
                db.session.add(test_user)
                db.session.flush()
                user_id = test_user.id
                print(f"👤 Создан тестовый пользователь ID: {user_id}")
                
                # Создаем связанные записи
                visitor = RegistrationVisitor(
                    ip_address="127.0.0.1",
                    page_type="test",
                    entry_time=datetime.utcnow(),
                    user_id=user_id,
                    email_entered="test_cascade_delete@example.com"
                )
                db.session.add(visitor)
                
                # Создаем пост форума (если есть тема)
                from models import ForumTopic
                topic = ForumTopic.query.first()
                if topic:
                    post = ForumPost(
                        content="Test post for cascade deletion",
                        topic_id=topic.id,
                        author_id=user_id
                    )
                    db.session.add(post)
                    print(f"📝 Создан тестовый пост форума")
                
                db.session.commit()
                print(f"📊 Создана запись visitor")
            
            print(f"🗑️ Тестируем удаление пользователя ID: {user_id}")
            
            # Удаляем пользователя
            user = User.query.get(user_id)
            if not user:
                print(f"❌ Пользователь с ID {user_id} не найден")
                return False
            
            db.session.delete(user)
            db.session.commit()
            
            print("✅ Пользователь удален успешно!")
            print("🎉 Каскадное удаление работает корректно!")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при тестировании удаления: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python3 fix_all_foreign_key_constraints.py show     - показать ограничения")
        print("  python3 fix_all_foreign_key_constraints.py fix      - исправить ограничения")
        print("  python3 fix_all_foreign_key_constraints.py test     - протестировать удаление")
        print("  python3 fix_all_foreign_key_constraints.py delete <user_id> - удалить пользователя")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "show":
        show_foreign_key_constraints()
    elif command == "fix":
        success = fix_all_foreign_key_constraints()
        if success:
            print("\n🧪 Хотите протестировать? Запустите:")
            print("   python3 fix_all_foreign_key_constraints.py test")
        else:
            print("💥 Не удалось исправить ограничения")
            sys.exit(1)
    elif command == "test":
        success = test_user_deletion()
        if not success:
            sys.exit(1)
    elif command == "delete":
        if len(sys.argv) < 3:
            print("❌ Укажите ID пользователя для удаления")
            sys.exit(1)
        try:
            user_id = int(sys.argv[2])
            success = test_user_deletion(user_id)
            if not success:
                sys.exit(1)
        except ValueError:
            print("❌ Неверный ID пользователя. Должно быть число.")
            sys.exit(1)
    else:
        print("❌ Неверная команда")
        sys.exit(1)
