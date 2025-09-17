#!/usr/bin/env python3
"""
Проверка пользователей с неподтвержденными email адресами
"""

import os
import sys
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Загружаем переменные окружения
load_dotenv()

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask
from extensions import init_extensions, db
from models import User

def check_unconfirmed_users():
    """Проверяем пользователей с неподтвержденными email"""
    
    # Создаем Flask приложение
    app = Flask(__name__)
    
    # Настройки для работы с базой данных
    app.config.update({
        'SECRET_KEY': 'test-secret-key',
        'SQLALCHEMY_DATABASE_URI': os.environ.get('DATABASE_URL', 'sqlite:///dental_academy_clean.db'),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
    })
    
    # Инициализируем расширения
    init_extensions(app)
    
    with app.app_context():
        print("=== ПРОВЕРКА ПОЛЬЗОВАТЕЛЕЙ С НЕПОДТВЕРЖДЕННЫМИ EMAIL ===")
        print()
        
        # Находим всех пользователей
        all_users = User.query.all()
        print(f"📊 Всего пользователей в базе: {len(all_users)}")
        
        # Пользователи с неподтвержденными email
        unconfirmed_users = User.query.filter_by(email_confirmed=False).all()
        print(f"❌ Пользователи с неподтвержденными email: {len(unconfirmed_users)}")
        
        # Пользователи с подтвержденными email
        confirmed_users = User.query.filter_by(email_confirmed=True).all()
        print(f"✅ Пользователи с подтвержденными email: {len(confirmed_users)}")
        
        # Пользователи без флага email_confirmed (старые записи)
        no_flag_users = User.query.filter(User.email_confirmed.is_(None)).all()
        print(f"❓ Пользователи без флага email_confirmed: {len(no_flag_users)}")
        
        print()
        
        if unconfirmed_users:
            print("🔍 ДЕТАЛИ ПОЛЬЗОВАТЕЛЕЙ С НЕПОДТВЕРЖДЕННЫМИ EMAIL:")
            print("-" * 80)
            for user in unconfirmed_users:
                print(f"ID: {user.id}")
                print(f"Email: {user.email}")
                print(f"Имя: {user.first_name} {user.last_name}")
                print(f"Роль: {user.role}")
                print(f"Активен: {user.is_active}")
                print(f"Создан: {user.created_at}")
                print(f"Email подтвержден: {user.email_confirmed}")
                print("-" * 40)
        
        if no_flag_users:
            print("🔍 ДЕТАЛИ ПОЛЬЗОВАТЕЛЕЙ БЕЗ ФЛАГА EMAIL_CONFIRMED:")
            print("-" * 80)
            for user in no_flag_users:
                print(f"ID: {user.id}")
                print(f"Email: {user.email}")
                print(f"Имя: {user.first_name} {user.last_name}")
                print(f"Роль: {user.role}")
                print(f"Активен: {user.is_active}")
                print(f"Создан: {user.created_at}")
                print(f"Email подтвержден: {user.email_confirmed}")
                print("-" * 40)
        
        # Проверяем пользователей, созданных за последние 7 дней
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_users = User.query.filter(User.created_at >= week_ago).all()
        print(f"📅 Пользователи, созданные за последние 7 дней: {len(recent_users)}")
        
        if recent_users:
            print("🔍 НЕДАВНИЕ ПОЛЬЗОВАТЕЛИ:")
            print("-" * 80)
            for user in recent_users:
                print(f"ID: {user.id}")
                print(f"Email: {user.email}")
                print(f"Имя: {user.first_name} {user.last_name}")
                print(f"Email подтвержден: {user.email_confirmed}")
                print(f"Создан: {user.created_at}")
                print("-" * 40)
        
        # Статистика по ролям
        print("📊 СТАТИСТИКА ПО РОЛЯМ:")
        print("-" * 40)
        roles = db.session.query(User.role, db.func.count(User.id)).group_by(User.role).all()
        for role, count in roles:
            print(f"{role or 'None'}: {count}")

if __name__ == '__main__':
    check_unconfirmed_users()
