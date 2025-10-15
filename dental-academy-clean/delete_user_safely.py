#!/usr/bin/env python3
"""
Безопасное удаление пользователя с очисткой связанных записей
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, RegistrationVisitor
from sqlalchemy import text

def delete_user_safely(user_id):
    """Безопасно удаляет пользователя и все связанные записи"""
    
    with app.app_context():
        try:
            print(f"🗑️ Начинаем удаление пользователя ID: {user_id}")
            
            # Проверяем, существует ли пользователь
            user = User.query.get(user_id)
            if not user:
                print(f"❌ Пользователь с ID {user_id} не найден")
                return False
            
            print(f"👤 Найден пользователь: {user.email}")
            
            # 1. Удаляем все записи в registration_visitors, связанные с этим пользователем
            registration_visitors = RegistrationVisitor.query.filter_by(user_id=user_id).all()
            print(f"📊 Найдено записей в registration_visitors: {len(registration_visitors)}")
            
            for visitor in registration_visitors:
                db.session.delete(visitor)
                print(f"   ✅ Удалена запись visitor ID: {visitor.id}")
            
            # 2. Можно добавить удаление других связанных записей здесь
            # Например, если есть другие таблицы с внешними ключами на user.id
            
            # 3. Теперь удаляем самого пользователя
            db.session.delete(user)
            print(f"✅ Пользователь {user.email} удален")
            
            # 4. Сохраняем изменения
            db.session.commit()
            print("💾 Изменения сохранены в базе данных")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при удалении пользователя: {e}")
            db.session.rollback()
            return False

def list_users_with_registration_data():
    """Показывает пользователей, у которых есть данные в registration_visitors"""
    
    with app.app_context():
        try:
            print("📋 Пользователи с данными регистрации:")
            
            # SQL запрос для получения пользователей с количеством записей в registration_visitors
            result = db.session.execute(text("""
                SELECT u.id, u.email, u.first_name, u.last_name, COUNT(rv.id) as visitor_records
                FROM "user" u
                LEFT JOIN registration_visitors rv ON u.id = rv.user_id
                WHERE rv.user_id IS NOT NULL
                GROUP BY u.id, u.email, u.first_name, u.last_name
                ORDER BY visitor_records DESC
            """))
            
            users = result.fetchall()
            
            if not users:
                print("   ℹ️ Нет пользователей с данными регистрации")
                return
            
            for user in users:
                user_id, email, first_name, last_name, visitor_records = user
                name = f"{first_name} {last_name}".strip() if first_name or last_name else "Без имени"
                print(f"   👤 ID: {user_id} | Email: {email} | Имя: {name} | Записей: {visitor_records}")
                
        except Exception as e:
            print(f"❌ Ошибка при получении списка пользователей: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python delete_user_safely.py <user_id>     - удалить пользователя")
        print("  python delete_user_safely.py list          - показать пользователей с данными регистрации")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        list_users_with_registration_data()
    else:
        try:
            user_id = int(command)
            success = delete_user_safely(user_id)
            if success:
                print("🎉 Пользователь успешно удален!")
            else:
                print("💥 Не удалось удалить пользователя")
                sys.exit(1)
        except ValueError:
            print("❌ Неверный ID пользователя. Должно быть число.")
            sys.exit(1)
