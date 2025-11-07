#!/usr/bin/env python3
"""
Скрипт для проверки регистраций за сегодня
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from extensions import db
from models import User, RegistrationVisitor
from datetime import datetime, date, timedelta

def check_today_registrations():
    """Проверяет регистрации за сегодня"""
    with app.app_context():
        try:
            # Получаем сегодняшнюю дату
            today = date.today()
            print(f"📅 Проверяем данные за {today}")
            print("=" * 50)
            
            # Проверяем пользователей, созданных сегодня
            today_users = User.query.filter(
                db.func.date(User.created_at) == today
            ).all()
            
            print(f"👥 ПОЛЬЗОВАТЕЛИ СОЗДАННЫЕ СЕГОДНЯ: {len(today_users)}")
            for user in today_users:
                print(f"   - ID: {user.id}, Email: {user.email}, Создан: {user.created_at}")
                print(f"     Имя: {user.first_name} {user.last_name}")
                print(f"     Профессия: {user.profession}")
                print(f"     Регистрация завершена: {user.registration_completed}")
                print()
            
            # Проверяем посетителей страниц регистрации за сегодня
            today_visitors = RegistrationVisitor.query.filter(
                db.func.date(RegistrationVisitor.entry_time) == today
            ).all()
            
            print(f"🌐 ПОСЕТИТЕЛИ СТРАНИЦ РЕГИСТРАЦИИ СЕГОДНЯ: {len(today_visitors)}")
            for visitor in today_visitors:
                print(f"   - ID: {visitor.id}, IP: {visitor.ip_address}")
                print(f"     Страница: {visitor.page_type}")
                print(f"     Время: {visitor.entry_time}")
                print(f"     Email введен: {visitor.email_entered}")
                print(f"     Имя введено: {visitor.first_name_entered} {visitor.last_name_entered}")
                print(f"     Форма начата: {visitor.form_started}")
                print(f"     Регистрация завершена: {visitor.registration_completed}")
                print()
            
            # Проверяем статистику за последние 7 дней
            week_ago = today - timedelta(days=7)
            week_users = User.query.filter(
                db.func.date(User.created_at) >= week_ago
            ).count()
            
            week_visitors = RegistrationVisitor.query.filter(
                db.func.date(RegistrationVisitor.entry_time) >= week_ago
            ).count()
            
            print(f"📊 СТАТИСТИКА ЗА ПОСЛЕДНИЕ 7 ДНЕЙ:")
            print(f"   - Пользователи: {week_users}")
            print(f"   - Посетители: {week_visitors}")
            print()
            
            # Проверяем общую статистику
            total_users = User.query.count()
            total_visitors = RegistrationVisitor.query.count()
            
            print(f"📈 ОБЩАЯ СТАТИСТИКА:")
            print(f"   - Всего пользователей: {total_users}")
            print(f"   - Всего посетителей: {total_visitors}")
            print()
            
            # Проверяем последние записи
            print(f"🕐 ПОСЛЕДНИЕ 10 ПОЛЬЗОВАТЕЛЕЙ:")
            recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
            for user in recent_users:
                print(f"   - {user.created_at.strftime('%Y-%m-%d %H:%M')} | {user.email} | {user.first_name} {user.last_name}")
            
            print()
            print(f"🕐 ПОСЛЕДНИЕ 10 ПОСЕТИТЕЛЕЙ:")
            recent_visitors = RegistrationVisitor.query.order_by(RegistrationVisitor.entry_time.desc()).limit(10).all()
            for visitor in recent_visitors:
                print(f"   - {visitor.entry_time.strftime('%Y-%m-%d %H:%M')} | {visitor.ip_address} | {visitor.page_type}")
            
        except Exception as e:
            print(f"❌ Ошибка: {str(e)}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    check_today_registrations()


