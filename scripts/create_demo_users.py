#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для создания демо пользователей DigiD
Создает тестовых пользователей с разными ролями для разработки
"""

import os
import sys
import logging
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash

# Добавляем корневую директорию в путь для импорта
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import db, User
from config import get_config
from sqlalchemy import text


# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scripts/demo_users_creation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


# Демо пользователи DigiD
DEMO_USERS = [
    {
        'bsn': '123456789',
        'digid_username': 'jan.jansen',
        'first_name': 'Jan',
        'last_name': 'Jansen',
        'email': 'jan.jansen@demo.dental-academy.nl',
        'role': 'student',
        'digid_verified': True,
        'created_via_digid': True
    },
    {
        'bsn': '987654321',
        'digid_username': 'maria.devries',
        'first_name': 'Maria',
        'last_name': 'de Vries',
        'email': 'maria.devries@demo.dental-academy.nl',
        'role': 'docent',
        'digid_verified': True,
        'created_via_digid': True
    },
    {
        'bsn': '111222333',
        'digid_username': 'admin.user',
        'first_name': 'Admin',
        'last_name': 'User',
        'email': 'admin@demo.dental-academy.nl',
        'role': 'admin',
        'digid_verified': True,
        'created_via_digid': True
    }
]


def check_existing_users():
    """Проверка существующих пользователей"""
    logger.info("🔍 Проверка существующих пользователей...")
    
    existing_users = []
    for user_data in DEMO_USERS:
        # Проверяем по BSN
        user_by_bsn = User.query.filter_by(bsn=user_data['bsn']).first()
        if user_by_bsn:
            existing_users.append({
                'bsn': user_data['bsn'],
                'username': user_by_bsn.username,
                'role': user_by_bsn.role,
                'exists': True
            })
            logger.warning(f"⚠️ Пользователь с BSN {user_data['bsn']} уже существует: {user_by_bsn.username}")
            continue
            
        # Проверяем по email
        user_by_email = User.query.filter_by(email=user_data['email']).first()
        if user_by_email:
            existing_users.append({
                'email': user_data['email'],
                'username': user_by_email.username,
                'role': user_by_email.role,
                'exists': True
            })
            logger.warning(f"⚠️ Пользователь с email {user_data['email']} уже существует: {user_by_email.username}")
            continue
            
        # Проверяем по digid_username
        user_by_digid = User.query.filter_by(digid_username=user_data['digid_username']).first()
        if user_by_digid:
            existing_users.append({
                'digid_username': user_data['digid_username'],
                'username': user_by_digid.username,
                'role': user_by_digid.role,
                'exists': True
            })
            logger.warning(f"⚠️ Пользователь с DigiD username {user_data['digid_username']} уже существует: {user_by_digid.username}")
            continue
    
    return existing_users


def create_demo_user(user_data):
    """Создание одного демо пользователя"""
    try:
        # Создаем пользователя
        user = User(
            username=user_data['digid_username'],
            email=user_data['email'],
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            role=user_data['role'],
            bsn=user_data['bsn'],
            digid_username=user_data['digid_username'],
            digid_verified=user_data['digid_verified'],
            created_via_digid=user_data['created_via_digid'],
            is_active=True
        )
        
        # Генерируем случайный пароль (для совместимости)
        user.password_hash = generate_password_hash('demo123456')
        
        # Добавляем в базу данных
        db.session.add(user)
        db.session.commit()
        
        logger.info(f"✅ Создан пользователь: {user.username} (BSN: {user.bsn}, Роль: {user.role})")
        return user
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Ошибка создания пользователя {user_data['digid_username']}: {str(e)}")
        raise


def create_all_demo_users():
    """Создание всех демо пользователей"""
    logger.info("🚀 Начало создания демо пользователей DigiD...")
    
    # Проверяем существующих пользователей
    existing_users = check_existing_users()
    
    if existing_users:
        logger.info(f"📊 Найдено {len(existing_users)} существующих пользователей")
        
        # Спрашиваем подтверждение
        response = input("\n❓ Обнаружены существующие пользователи. Продолжить создание? (y/N): ")
        if response.lower() != 'y':
            logger.info("❌ Создание отменено пользователем")
            return False
    
    # Создаем пользователей
    created_users = []
    failed_users = []
    
    for user_data in DEMO_USERS:
        try:
            # Проверяем, не существует ли уже пользователь
            existing_user = User.query.filter(
                (User.bsn == user_data['bsn']) |
                (User.email == user_data['email']) |
                (User.digid_username == user_data['digid_username'])
            ).first()
            
            if existing_user:
                logger.warning(f"⏭️ Пропускаем {user_data['digid_username']} - уже существует")
                continue
            
            user = create_demo_user(user_data)
            created_users.append(user)
            
        except Exception as e:
            logger.error(f"❌ Не удалось создать пользователя {user_data['digid_username']}: {str(e)}")
            failed_users.append(user_data)
    
    # Выводим результаты
    logger.info(f"\n📋 РЕЗУЛЬТАТЫ СОЗДАНИЯ:")
    logger.info(f"✅ Успешно создано: {len(created_users)}")
    logger.info(f"❌ Ошибок: {len(failed_users)}")
    logger.info(f"⏭️ Пропущено: {len(existing_users)}")
    
    if created_users:
        logger.info(f"\n👥 Созданные пользователи:")
        for user in created_users:
            logger.info(f"   • {user.username} (BSN: {user.bsn}, Роль: {user.role})")
    
    if failed_users:
        logger.error(f"\n❌ Неудачные попытки:")
        for user_data in failed_users:
            logger.error(f"   • {user_data['digid_username']} (BSN: {user_data['bsn']})")
    
    return len(created_users) > 0


def main():
    """Основная функция"""
    try:
        logger.info("🔧 Инициализация приложения...")
        
        # Создаем приложение
        app = create_app()
        
        with app.app_context():
            # Проверяем подключение к базе данных
            try:
                with db.engine.connect() as conn:
                    conn.execute(text('SELECT 1'))
                logger.info("✅ Подключение к базе данных успешно")
            except Exception as e:
                logger.error(f"❌ Ошибка подключения к базе данных: {str(e)}")
                return False
            
            # Создаем демо пользователей
            success = create_all_demo_users()
            
            if success:
                logger.info("🎉 Скрипт завершен успешно!")
                return True
            else:
                logger.warning("⚠️ Скрипт завершен с предупреждениями")
                return False
                
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {str(e)}")
        return False


if __name__ == '__main__':
    print("🔧 Скрипт создания демо пользователей DigiD")
    print("=" * 50)
    
    success = main()
    
    if success:
        print("\n✅ Скрипт выполнен успешно!")
        print("\n📋 Информация о демо пользователях:")
        print("   • BSN: 123456789 | Jan Jansen | Студент")
        print("   • BSN: 987654321 | Maria de Vries | Преподаватель") 
        print("   • BSN: 111222333 | Admin User | Администратор")
        print("\n🔐 Пароль для всех пользователей: demo123456")
        print("⚠️ ВНИМАНИЕ: Используйте только для разработки!")
    else:
        print("\n❌ Скрипт завершен с ошибками!")
        print("Проверьте логи в файле scripts/demo_users_creation.log")
    
    sys.exit(0 if success else 1) 