#!/usr/bin/env python3
"""
Исправление ограничений внешних ключей для SQLite
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from sqlalchemy import text, inspect

def get_sqlite_foreign_keys():
    """Получает информацию о внешних ключах в SQLite"""
    
    with app.app_context():
        try:
            # Получаем инспектор базы данных
            inspector = inspect(db.engine)
            
            # Получаем список всех таблиц
            tables = inspector.get_table_names()
            
            foreign_keys_info = []
            
            for table_name in tables:
                try:
                    # Получаем информацию о внешних ключах для каждой таблицы
                    foreign_keys = inspector.get_foreign_keys(table_name)
                    
                    for fk in foreign_keys:
                        # Проверяем, ссылается ли внешний ключ на таблицу user
                        if fk['referred_table'] == 'user' and 'id' in fk.get('referred_columns', []):
                            for local_column in fk.get('constrained_columns', []):
                                foreign_keys_info.append({
                                    'table_name': table_name,
                                    'column_name': local_column,
                                    'foreign_table': fk['referred_table'],
                                    'foreign_column': fk['referred_columns'][0] if fk['referred_columns'] else 'id',
                                    'constraint_name': fk.get('name', f'fk_{table_name}_{local_column}'),
                                    'ondelete': fk.get('options', {}).get('ondelete', 'NO ACTION')
                                })
                except Exception as e:
                    print(f"⚠️ Ошибка при получении внешних ключей для таблицы {table_name}: {e}")
                    continue
            
            return foreign_keys_info
            
        except Exception as e:
            print(f"❌ Ошибка при получении информации о внешних ключах: {e}")
            return []

def show_foreign_key_constraints():
    """Показывает все ограничения внешних ключей"""
    
    foreign_keys = get_sqlite_foreign_keys()
    
    if not foreign_keys:
        print("ℹ️ Внешних ключей, ссылающихся на user.id, не найдено")
        return
    
    print(f"📋 Найдено {len(foreign_keys)} внешних ключей, ссылающихся на user.id:")
    
    for fk in foreign_keys:
        print(f"📊 {fk['table_name']}.{fk['column_name']} -> {fk['foreign_table']}.{fk['foreign_column']}")
        print(f"   Ограничение: {fk['constraint_name']}")
        print(f"   Правило удаления: {fk['ondelete']}")

def fix_foreign_key_constraints():
    """Исправляет ограничения внешних ключей для каскадного удаления"""
    
    with app.app_context():
        try:
            print("🔧 Исправление ограничений внешних ключей для SQLite...")
            
            # В SQLite нельзя изменить ограничения внешних ключей напрямую
            # Нужно пересоздать таблицы с новыми ограничениями
            print("⚠️ SQLite не поддерживает изменение ограничений внешних ключей")
            print("💡 Рекомендуется использовать ручное удаление связанных записей")
            
            foreign_keys = get_sqlite_foreign_keys()
            
            if not foreign_keys:
                print("ℹ️ Внешних ключей не найдено")
                return True
            
            print(f"📋 Найдено {len(foreign_keys)} внешних ключей:")
            
            for fk in foreign_keys:
                table_name = fk['table_name']
                column_name = fk['column_name']
                constraint_name = fk['constraint_name']
                
                print(f"📊 {table_name}.{column_name}")
                print(f"   Текущее правило: {fk['ondelete']}")
                
                # Проверяем, может ли колонка быть NULL
                try:
                    result = db.session.execute(text(f"PRAGMA table_info({table_name})"))
                    columns = result.fetchall()
                    
                    column_nullable = True
                    for col in columns:
                        if col[1] == column_name:  # col[1] - имя колонки
                            column_nullable = col[3] == 0  # col[3] - notnull (0 = nullable, 1 = not null)
                            break
                    
                    print(f"   Колонка nullable: {column_nullable}")
                    
                except Exception as e:
                    print(f"   ⚠️ Не удалось получить информацию о колонке: {e}")
                    column_nullable = True
            
            print("\n💡 Рекомендации:")
            print("1. Используйте скрипт delete_user_safely.py для ручного удаления")
            print("2. Или пересоздайте таблицы с правильными ограничениями")
            print("3. Или мигрируйте на PostgreSQL для полной поддержки CASCADE")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при исправлении ограничений: {e}")
            return False

def test_user_deletion(user_id=None):
    """Тестирует удаление пользователя"""
    
    with app.app_context():
        try:
            if user_id is None:
                # Создаем тестового пользователя
                from models import User, RegistrationVisitor, ForumPost
                from datetime import datetime
                
                test_user = User(
                    email="test_sqlite_delete@example.com",
                    password_hash="test_hash",
                    first_name="Test",
                    last_name="SQLite"
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
                    email_entered="test_sqlite_delete@example.com"
                )
                db.session.add(visitor)
                
                # Создаем пост форума (если есть тема)
                from models import ForumTopic
                topic = ForumTopic.query.first()
                if topic:
                    post = ForumPost(
                        content="Test post for SQLite cascade deletion",
                        topic_id=topic.id,
                        author_id=user_id
                    )
                    db.session.add(post)
                    print(f"📝 Создан тестовый пост форума")
                
                db.session.commit()
                print(f"📊 Создана запись visitor")
            
            print(f"🗑️ Тестируем удаление пользователя ID: {user_id}")
            
            # Используем наш безопасный метод удаления
            from delete_user_safely import delete_user_safely
            success = delete_user_safely(user_id)
            
            if success:
                print("✅ Пользователь удален успешно!")
                print("🎉 Безопасное удаление работает корректно!")
                return True
            else:
                print("❌ Не удалось удалить пользователя")
                return False
            
        except Exception as e:
            print(f"❌ Ошибка при тестировании удаления: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python3 fix_sqlite_foreign_key_constraints.py show     - показать ограничения")
        print("  python3 fix_sqlite_foreign_key_constraints.py fix      - показать рекомендации")
        print("  python3 fix_sqlite_foreign_key_constraints.py test     - протестировать удаление")
        print("  python3 fix_sqlite_foreign_key_constraints.py delete <user_id> - удалить пользователя")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "show":
        show_foreign_key_constraints()
    elif command == "fix":
        success = fix_foreign_key_constraints()
        if not success:
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
