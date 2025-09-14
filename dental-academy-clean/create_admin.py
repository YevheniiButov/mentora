#!/usr/bin/env python3
"""
Скрипт для создания администратора на деплой сервере
"""

import os
import sys
from datetime import datetime

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import User, db
from extensions import db as db_ext

def create_admin():
    """Создает администратора в системе"""
    
    print("🔧 Создание администратора для Mentora")
    print("=" * 50)
    
    # Создаем Flask приложение
    app = create_app()
    
    with app.app_context():
        try:
            # Проверяем, есть ли уже админы
            existing_admins = User.query.filter_by(role='admin').count()
            print(f"📊 Найдено существующих админов: {existing_admins}")
            
            if existing_admins > 0:
                print("⚠️  В системе уже есть администраторы:")
                admins = User.query.filter_by(role='admin').all()
                for admin in admins:
                    print(f"   - {admin.email} ({admin.first_name} {admin.last_name})")
                
                response = input("\n❓ Создать дополнительного админа? (y/N): ").strip().lower()
                if response not in ['y', 'yes', 'да']:
                    print("❌ Создание отменено")
                    return
            
            # Получаем данные для нового админа
            print("\n📝 Введите данные для нового администратора:")
            
            email = input("📧 Email: ").strip()
            if not email:
                print("❌ Email обязателен!")
                return
            
            # Проверяем, не существует ли уже пользователь с таким email
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                print(f"❌ Пользователь с email {email} уже существует!")
                if existing_user.role == 'admin':
                    print("   Этот пользователь уже является администратором")
                else:
                    response = input("❓ Сделать этого пользователя администратором? (y/N): ").strip().lower()
                    if response in ['y', 'yes', 'да']:
                        existing_user.role = 'admin'
                        existing_user.is_active = True
                        existing_user.email_confirmed = True
                        db.session.commit()
                        print(f"✅ Пользователь {email} теперь администратор!")
                        return
                return
            
            first_name = input("👤 Имя: ").strip()
            last_name = input("👤 Фамилия: ").strip()
            
            password = input("🔐 Пароль: ").strip()
            if not password:
                print("❌ Пароль обязателен!")
                return
            
            if len(password) < 8:
                print("⚠️  Пароль должен содержать минимум 8 символов")
                response = input("❓ Продолжить? (y/N): ").strip().lower()
                if response not in ['y', 'yes', 'да']:
                    return
            
            # Создаем нового администратора
            admin = User(
                email=email,
                username=email,  # Используем email как username
                first_name=first_name,
                last_name=last_name,
                role='admin',
                is_active=True,
                email_confirmed=True,  # Админ не нуждается в подтверждении email
                registration_completed=True,
                language='en',
                created_at=datetime.utcnow()
            )
            
            # Устанавливаем пароль
            admin.set_password(password)
            
            # Добавляем в базу данных
            db.session.add(admin)
            db.session.commit()
            
            print("\n✅ Администратор успешно создан!")
            print(f"   📧 Email: {email}")
            print(f"   👤 Имя: {first_name} {last_name}")
            print(f"   🔑 Роль: admin")
            print(f"   ✅ Статус: активен")
            print(f"   📧 Email подтвержден: да")
            
            print("\n🌐 Теперь вы можете войти в админ панель:")
            print("   URL: /admin")
            print("   Email: " + email)
            print("   Пароль: [введенный вами пароль]")
            
        except Exception as e:
            print(f"❌ Ошибка при создании администратора: {str(e)}")
            db.session.rollback()
            return False
    
    return True

def list_admins():
    """Показывает список всех администраторов"""
    
    print("👥 Список администраторов")
    print("=" * 30)
    
    app = create_app()
    
    with app.app_context():
        try:
            admins = User.query.filter_by(role='admin').all()
            
            if not admins:
                print("❌ Администраторы не найдены")
                return
            
            for i, admin in enumerate(admins, 1):
                status = "✅ Активен" if admin.is_active else "❌ Неактивен"
                email_confirmed = "✅ Да" if admin.email_confirmed else "❌ Нет"
                
                print(f"{i}. {admin.email}")
                print(f"   👤 Имя: {admin.first_name} {admin.last_name}")
                print(f"   🔑 Роль: {admin.role}")
                print(f"   📊 Статус: {status}")
                print(f"   📧 Email подтвержден: {email_confirmed}")
                print(f"   📅 Создан: {admin.created_at.strftime('%Y-%m-%d %H:%M') if admin.created_at else 'Неизвестно'}")
                print()
                
        except Exception as e:
            print(f"❌ Ошибка при получении списка администраторов: {str(e)}")

def main():
    """Главная функция"""
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'list':
            list_admins()
            return
        elif command == 'create':
            create_admin()
            return
        elif command == 'help':
            print("🔧 Скрипт управления администраторами")
            print("=" * 40)
            print("Использование:")
            print("  python3 create_admin.py create  - Создать нового администратора")
            print("  python3 create_admin.py list    - Показать список администраторов")
            print("  python3 create_admin.py help    - Показать эту справку")
            return
        else:
            print(f"❌ Неизвестная команда: {command}")
            print("Используйте 'python3 create_admin.py help' для справки")
            return
    
    # Если команда не указана, предлагаем создать админа
    print("🔧 Создание администратора для Mentora")
    print("=" * 40)
    print("Доступные команды:")
    print("  create - Создать нового администратора")
    print("  list   - Показать список администраторов")
    print("  help   - Показать справку")
    print()
    
    choice = input("❓ Что вы хотите сделать? (create/list/help): ").strip().lower()
    
    if choice == 'create':
        create_admin()
    elif choice == 'list':
        list_admins()
    elif choice == 'help':
        print("\n📖 Справка:")
        print("  create - Создает нового администратора с правами доступа к админ панели")
        print("  list   - Показывает всех существующих администраторов в системе")
        print("  help   - Показывает эту справку")
    else:
        print("❌ Неверный выбор")

if __name__ == '__main__':
    main()
