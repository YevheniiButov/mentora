#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для миграции существующих пользователей в DigiD формат
Обновляет существующих пользователей для поддержки DigiD аутентификации
"""

import os
import sys
import logging
import random
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
        logging.FileHandler('scripts/migrate_to_digid.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def generate_mock_bsn():
    """Генерация случайного BSN для миграции"""
    # BSN должен быть 9 цифр и соответствовать алгоритму 11-proef
    while True:
        bsn = ''.join([str(random.randint(0, 9)) for _ in range(9)])
        if validate_bsn(bsn):
            return bsn


def validate_bsn(bsn):
    """Валидация BSN по алгоритму 11-proef"""
    if len(bsn) != 9 or not bsn.isdigit():
        return False
    
    # Алгоритм 11-proef для BSN
    total = 0
    for i in range(9):
        digit = int(bsn[i])
        if i == 8:  # Последняя цифра
            total -= digit
        else:
            total += digit * (9 - i)
    
    return total % 11 == 0


def generate_digid_username(first_name, last_name, existing_usernames):
    """Генерация уникального DigiD username"""
    base_username = f"{first_name.lower()}.{last_name.lower()}".replace(' ', '')
    
    if base_username not in existing_usernames:
        return base_username
    
    # Добавляем случайное число
    counter = 1
    while True:
        username = f"{base_username}{counter}"
        if username not in existing_usernames:
            return username
        counter += 1


def analyze_existing_users():
    """Анализ существующих пользователей"""
    logger.info("🔍 Анализ существующих пользователей...")
    
    users = User.query.all()
    analysis = {
        'total_users': len(users),
        'digid_users': 0,
        'regular_users': 0,
        'users_with_bsn': 0,
        'users_without_bsn': 0,
        'users_with_digid_username': 0,
        'users_without_digid_username': 0,
        'migratable_users': [],
        'already_migrated': []
    }
    
    existing_bsns = set()
    existing_digid_usernames = set()
    
    for user in users:
        # Проверяем, уже ли пользователь мигрирован
        if user.bsn and user.digid_username and user.digid_verified:
            analysis['digid_users'] += 1
            analysis['already_migrated'].append(user)
            existing_bsns.add(user.bsn)
            existing_digid_usernames.add(user.digid_username)
        else:
            analysis['regular_users'] += 1
            
            # Проверяем наличие BSN
            if user.bsn:
                analysis['users_with_bsn'] += 1
                existing_bsns.add(user.bsn)
            else:
                analysis['users_without_bsn'] += 1
            
            # Проверяем наличие digid_username
            if user.digid_username:
                analysis['users_with_digid_username'] += 1
                existing_digid_usernames.add(user.digid_username)
            else:
                analysis['users_without_digid_username'] += 1
            
            # Добавляем в список для миграции
            analysis['migratable_users'].append({
                'user': user,
                'needs_bsn': not user.bsn,
                'needs_digid_username': not user.digid_username,
                'needs_digid_verification': not user.digid_verified
            })
    
    return analysis, existing_bsns, existing_digid_usernames


def migrate_user(user_data, existing_bsns, existing_digid_usernames):
    """Миграция одного пользователя"""
    user = user_data['user']
    logger.info(f"🔄 Миграция пользователя: {user.username}")
    
    try:
        # Генерируем BSN если нужно
        if user_data['needs_bsn']:
            while True:
                bsn = generate_mock_bsn()
                if bsn not in existing_bsns:
                    user.bsn = bsn
                    existing_bsns.add(bsn)
                    logger.info(f"   ✅ Сгенерирован BSN: {bsn}")
                    break
        
        # Генерируем digid_username если нужно
        if user_data['needs_digid_username']:
            digid_username = generate_digid_username(
                user.first_name or 'user',
                user.last_name or 'unknown',
                existing_digid_usernames
            )
            user.digid_username = digid_username
            existing_digid_usernames.add(digid_username)
            logger.info(f"   ✅ Сгенерирован DigiD username: {digid_username}")
        
        # Устанавливаем флаги DigiD
        if user_data['needs_digid_verification']:
            user.digid_verified = True
            user.created_via_digid = False  # Существующий пользователь
            logger.info(f"   ✅ Установлены флаги DigiD")
        
        # Обновляем timestamp
        user.updated_at = datetime.now(timezone.utc)
        
        # Сохраняем изменения
        db.session.commit()
        
        logger.info(f"   ✅ Пользователь {user.username} успешно мигрирован")
        return True
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"   ❌ Ошибка миграции пользователя {user.username}: {str(e)}")
        return False


def migrate_all_users():
    """Миграция всех пользователей"""
    logger.info("🚀 Начало миграции пользователей в DigiD формат...")
    
    # Анализируем существующих пользователей
    analysis, existing_bsns, existing_digid_usernames = analyze_existing_users()
    
    # Выводим анализ
    logger.info(f"\n📊 АНАЛИЗ ПОЛЬЗОВАТЕЛЕЙ:")
    logger.info(f"   Всего пользователей: {analysis['total_users']}")
    logger.info(f"   Уже мигрированы: {analysis['digid_users']}")
    logger.info(f"   Требуют миграции: {analysis['regular_users']}")
    logger.info(f"   С BSN: {analysis['users_with_bsn']}")
    logger.info(f"   Без BSN: {analysis['users_without_bsn']}")
    logger.info(f"   С DigiD username: {analysis['users_with_digid_username']}")
    logger.info(f"   Без DigiD username: {analysis['users_without_digid_username']}")
    
    if not analysis['migratable_users']:
        logger.info("✅ Все пользователи уже мигрированы!")
        return True
    
    # Показываем пользователей для миграции
    logger.info(f"\n🔄 ПОЛЬЗОВАТЕЛИ ДЛЯ МИГРАЦИИ:")
    for i, user_data in enumerate(analysis['migratable_users'], 1):
        user = user_data['user']
        needs = []
        if user_data['needs_bsn']:
            needs.append("BSN")
        if user_data['needs_digid_username']:
            needs.append("DigiD username")
        if user_data['needs_digid_verification']:
            needs.append("DigiD флаги")
        
        logger.info(f"   {i}. {user.username} ({user.email}) - нужно: {', '.join(needs)}")
    
    # Спрашиваем подтверждение
    response = input(f"\n❓ Мигрировать {len(analysis['migratable_users'])} пользователей? (y/N): ")
    if response.lower() != 'y':
        logger.info("❌ Миграция отменена пользователем")
        return False
    
    # Выполняем миграцию
    successful_migrations = 0
    failed_migrations = 0
    
    for user_data in analysis['migratable_users']:
        if migrate_user(user_data, existing_bsns, existing_digid_usernames):
            successful_migrations += 1
        else:
            failed_migrations += 1
    
    # Выводим результаты
    logger.info(f"\n📋 РЕЗУЛЬТАТЫ МИГРАЦИИ:")
    logger.info(f"✅ Успешно мигрировано: {successful_migrations}")
    logger.info(f"❌ Ошибок: {failed_migrations}")
    logger.info(f"⏭️ Пропущено: {len(analysis['already_migrated'])}")
    
    return successful_migrations > 0


def create_migration_report():
    """Создание отчета о миграции"""
    logger.info("📋 Создание отчета о миграции...")
    
    users = User.query.all()
    report = {
        'total_users': len(users),
        'digid_users': 0,
        'regular_users': 0,
        'users_by_role': {},
        'migration_status': []
    }
    
    for user in users:
        # Подсчитываем по ролям
        role = user.role or 'unknown'
        if role not in report['users_by_role']:
            report['users_by_role'][role] = 0
        report['users_by_role'][role] += 1
        
        # Проверяем статус миграции
        if user.bsn and user.digid_username and user.digid_verified:
            report['digid_users'] += 1
            status = 'migrated'
        else:
            report['regular_users'] += 1
            status = 'needs_migration'
        
        report['migration_status'].append({
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'bsn': user.bsn,
            'digid_username': user.digid_username,
            'digid_verified': user.digid_verified,
            'status': status
        })
    
    # Сохраняем отчет в файл
    report_file = 'scripts/migration_report.txt'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("ОТЧЕТ О МИГРАЦИИ ПОЛЬЗОВАТЕЛЕЙ В DIGID\n")
        f.write("=" * 50 + "\n\n")
        f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Всего пользователей: {report['total_users']}\n")
        f.write(f"Мигрировано в DigiD: {report['digid_users']}\n")
        f.write(f"Требуют миграции: {report['regular_users']}\n\n")
        
        f.write("ПОЛЬЗОВАТЕЛИ ПО РОЛЯМ:\n")
        for role, count in report['users_by_role'].items():
            f.write(f"  {role}: {count}\n")
        f.write("\n")
        
        f.write("ДЕТАЛЬНЫЙ СТАТУС:\n")
        for user_status in report['migration_status']:
            f.write(f"  {user_status['username']} ({user_status['email']}) - {user_status['status']}\n")
            if user_status['status'] == 'needs_migration':
                missing = []
                if not user_status['bsn']:
                    missing.append('BSN')
                if not user_status['digid_username']:
                    missing.append('DigiD username')
                if not user_status['digid_verified']:
                    missing.append('DigiD verification')
                f.write(f"    Отсутствует: {', '.join(missing)}\n")
    
    logger.info(f"📄 Отчет сохранен в {report_file}")
    return report


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
            
            # Выполняем миграцию
            success = migrate_all_users()
            
            # Создаем отчет
            report = create_migration_report()
            
            if success:
                logger.info("🎉 Миграция завершена успешно!")
                return True
            else:
                logger.warning("⚠️ Миграция завершена с предупреждениями")
                return False
                
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {str(e)}")
        return False


if __name__ == '__main__':
    print("🔧 Скрипт миграции пользователей в DigiD формат")
    print("=" * 50)
    
    success = main()
    
    if success:
        print("\n✅ Миграция выполнена успешно!")
        print("📄 Подробный отчет сохранен в scripts/migration_report.txt")
    else:
        print("\n❌ Миграция завершена с ошибками!")
        print("Проверьте логи в файле scripts/migrate_to_digid.log")
    
    sys.exit(0 if success else 1) 