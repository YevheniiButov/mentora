#!/usr/bin/env python3
"""
Безопасный деплой в production с резервным копированием
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import app
from models import db, User, Contact, Profession

def backup_users():
    """Создает резервную копию всех пользователей"""
    try:
        print("💾 СОЗДАНИЕ РЕЗЕРВНОЙ КОПИИ ПОЛЬЗОВАТЕЛЕЙ")
        print("=" * 50)
        
        users = User.query.all()
        backup_data = []
        
        for user in users:
            user_data = {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'is_active': user.is_active,
                'email_confirmed': user.email_confirmed,
                'registration_completed': user.registration_completed,
                'language': user.language,
                'created_at': user.created_at.isoformat() if user.created_at else None,
                'last_login': user.last_login.isoformat() if user.last_login else None,
                'password_hash': user.password_hash  # ВАЖНО: сохраняем хеш пароля
            }
            backup_data.append(user_data)
        
        # Сохраняем в файл
        backup_file = f"backups/users_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        os.makedirs("backups", exist_ok=True)
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Резервная копия создана: {backup_file}")
        print(f"📊 Сохранено пользователей: {len(backup_data)}")
        
        return backup_file, backup_data
        
    except Exception as e:
        print(f"❌ Ошибка создания резервной копии: {e}")
        return None, None

def restore_users(backup_file):
    """Восстанавливает пользователей из резервной копии"""
    try:
        print("🔄 ВОССТАНОВЛЕНИЕ ПОЛЬЗОВАТЕЛЕЙ")
        print("=" * 50)
        
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        restored_count = 0
        for user_data in backup_data:
            # Проверяем, не существует ли уже пользователь
            existing_user = User.query.filter_by(email=user_data['email']).first()
            if existing_user:
                print(f"⚠️  Пользователь {user_data['email']} уже существует, пропускаем")
                continue
            
            # Создаем пользователя
            user = User(
                email=user_data['email'],
                username=user_data['username'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                role=user_data['role'],
                is_active=user_data['is_active'],
                email_confirmed=user_data['email_confirmed'],
                registration_completed=user_data['registration_completed'],
                language=user_data['language']
            )
            
            # Восстанавливаем хеш пароля
            user.password_hash = user_data['password_hash']
            
            # Восстанавливаем даты
            if user_data['created_at']:
                user.created_at = datetime.fromisoformat(user_data['created_at'])
            if user_data['last_login']:
                user.last_login = datetime.fromisoformat(user_data['last_login'])
            
            db.session.add(user)
            restored_count += 1
        
        db.session.commit()
        print(f"✅ Восстановлено пользователей: {restored_count}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка восстановления: {e}")
        db.session.rollback()
        return False

def safe_production_deploy():
    """Безопасный деплой с резервным копированием"""
    try:
        print("🚀 БЕЗОПАСНЫЙ PRODUCTION ДЕПЛОЙ")
        print("=" * 60)
        
        with app.app_context():
            # 1. Проверяем текущее состояние БД
            print("1️⃣ ПРОВЕРКА ТЕКУЩЕГО СОСТОЯНИЯ")
            try:
                user_count = User.query.count()
                print(f"   👥 Пользователей в БД: {user_count}")
                
                if user_count > 0:
                    # Создаем резервную копию
                    backup_file, backup_data = backup_users()
                    if not backup_file:
                        print("❌ Не удалось создать резервную копию!")
                        return False
                else:
                    print("   ⚠️  БД пуста, резервная копия не нужна")
                    backup_file = None
                    
            except Exception as e:
                print(f"   ❌ Ошибка проверки БД: {e}")
                return False
            
            # 2. Выполняем миграции БД
            print("\n2️⃣ ВЫПОЛНЕНИЕ МИГРАЦИЙ БД")
            try:
                # Создаем все таблицы
                db.create_all()
                print("   ✅ Таблицы БД созданы/обновлены")
            except Exception as e:
                print(f"   ❌ Ошибка миграций: {e}")
                return False
            
            # 3. Проверяем состояние после миграций
            print("\n3️⃣ ПРОВЕРКА ПОСЛЕ МИГРАЦИЙ")
            try:
                user_count_after = User.query.count()
                print(f"   👥 Пользователей после миграций: {user_count_after}")
                
                if user_count > 0 and user_count_after == 0:
                    print("   🚨 ДАННЫЕ ПОТЕРЯНЫ! Восстанавливаем из резервной копии...")
                    
                    if backup_file and os.path.exists(backup_file):
                        if restore_users(backup_file):
                            print("   ✅ Данные восстановлены!")
                        else:
                            print("   ❌ Не удалось восстановить данные!")
                            return False
                    else:
                        print("   ❌ Резервная копия не найдена!")
                        return False
                        
            except Exception as e:
                print(f"   ❌ Ошибка проверки после миграций: {e}")
                return False
            
            # 4. Обеспечиваем наличие админа
            print("\n4️⃣ ПРОВЕРКА АДМИНИСТРАТОРА")
            try:
                admins = User.query.filter_by(role='admin').all()
                print(f"   👑 Администраторов: {len(admins)}")
                
                if len(admins) == 0:
                    print("   🔨 Создаем администратора...")
                    
                    admin = User(
                        email="admin@mentora.com",
                        username="admin@mentora.com",
                        first_name="Admin",
                        last_name="User",
                        role='admin',
                        is_active=True,
                        email_confirmed=True,
                        registration_completed=True,
                        language='en'
                    )
                    admin.set_password("AdminPass123!")
                    db.session.add(admin)
                    db.session.commit()
                    print("   ✅ Администратор создан")
                else:
                    print("   ✅ Администраторы уже существуют")
                    
            except Exception as e:
                print(f"   ❌ Ошибка создания админа: {e}")
                return False
            
            # 5. Финальная проверка
            print("\n5️⃣ ФИНАЛЬНАЯ ПРОВЕРКА")
            try:
                final_user_count = User.query.count()
                final_admin_count = User.query.filter_by(role='admin').count()
                
                print(f"   👥 Итого пользователей: {final_user_count}")
                print(f"   👑 Итого администраторов: {final_admin_count}")
                
                if final_admin_count > 0:
                    print("   ✅ Деплой завершен успешно!")
                    return True
                else:
                    print("   ❌ Администраторы отсутствуют!")
                    return False
                    
            except Exception as e:
                print(f"   ❌ Ошибка финальной проверки: {e}")
                return False
        
    except Exception as e:
        print(f"❌ КРИТИЧЕСКАЯ ОШИБКА ДЕПЛОЯ: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = safe_production_deploy()
    if not success:
        print("❌ ДЕПЛОЙ ЗАВЕРШИЛСЯ С ОШИБКОЙ")
        sys.exit(1)
    else:
        print("✅ ДЕПЛОЙ ВЫПОЛНЕН УСПЕШНО")