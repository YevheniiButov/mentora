#!/usr/bin/env python3
"""
Диагностика production базы данных
"""
import os
import sys
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import app
from models import db, User

def diagnose_production_db():
    """Диагностирует состояние production БД"""
    
    with app.app_context():
        try:
            print("🔍 ДИАГНОСТИКА PRODUCTION БАЗЫ ДАННЫХ")
            print("=" * 60)
            
            # Проверяем переменные окружения
            print("🌍 ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ:")
            print(f"   DATABASE_URL: {'Установлен' if os.environ.get('DATABASE_URL') else 'НЕ УСТАНОВЛЕН'}")
            print(f"   FLASK_ENV: {os.environ.get('FLASK_ENV', 'Не установлен')}")
            print(f"   SECRET_KEY: {'Установлен' if os.environ.get('SECRET_KEY') else 'НЕ УСТАНОВЛЕН'}")
            
            # Проверяем подключение к БД
            print("\n🔌 ПОДКЛЮЧЕНИЕ К БД:")
            try:
                result = db.session.execute('SELECT 1').scalar()
                print(f"   ✅ Подключение: OK (результат: {result})")
            except Exception as e:
                print(f"   ❌ Ошибка подключения: {e}")
                return False
            
            # Проверяем таблицы
            print("\n📊 ТАБЛИЦЫ БД:")
            try:
                # Проверяем таблицу users
                user_count = User.query.count()
                print(f"   👥 Пользователей: {user_count}")
                
                if user_count > 0:
                    # Показываем последних пользователей
                    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
                    print("   📋 Последние пользователи:")
                    for user in recent_users:
                        print(f"      - {user.email} (ID: {user.id}, Роль: {user.role}, Создан: {user.created_at.strftime('%d.%m.%Y %H:%M')})")
                
                # Проверяем админов
                admins = User.query.filter_by(role='admin').all()
                print(f"   👑 Администраторов: {len(admins)}")
                
                if admins:
                    print("   📋 Список админов:")
                    for admin in admins:
                        print(f"      - {admin.email} (ID: {admin.id}, Активен: {admin.is_active})")
                        print(f"        Последний вход: {admin.last_login.strftime('%d.%m.%Y %H:%M') if admin.last_login else 'Никогда'}")
                
            except Exception as e:
                print(f"   ❌ Ошибка запроса данных: {e}")
                return False
            
            # Проверяем новые таблицы CRM
            print("\n🏢 CRM ТАБЛИЦЫ:")
            try:
                from models import Profession, Contact
                
                profession_count = Profession.query.count()
                contact_count = Contact.query.count()
                
                print(f"   👨‍⚕️ Профессий: {profession_count}")
                print(f"   📞 Контактов: {contact_count}")
                
            except Exception as e:
                print(f"   ⚠️  CRM таблицы: {e}")
            
            print("\n✅ ДИАГНОСТИКА ЗАВЕРШЕНА")
            return True
            
        except Exception as e:
            print(f"❌ КРИТИЧЕСКАЯ ОШИБКА: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    success = diagnose_production_db()
    if not success:
        print("❌ ДИАГНОСТИКА ЗАВЕРШИЛАСЬ С ОШИБКОЙ")
        sys.exit(1)
    else:
        print("✅ ДИАГНОСТИКА ВЫПОЛНЕНА УСПЕШНО")
