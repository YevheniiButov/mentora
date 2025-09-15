#!/usr/bin/env python3
"""
Скрипт для заполнения аналитических данных
"""
import os
import sys
import json
import random
from pathlib import Path
from datetime import datetime, timedelta

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import app
from models import db, User, Contact, Profession, CountryAnalytics, DeviceAnalytics, ProfessionAnalytics, AnalyticsEvent

def get_country_data():
    """Возвращает данные о странах"""
    return [
        {'code': 'NL', 'name': 'Netherlands'},
        {'code': 'DE', 'name': 'Germany'},
        {'code': 'BE', 'name': 'Belgium'},
        {'code': 'PL', 'name': 'Poland'},
        {'code': 'ES', 'name': 'Spain'},
        {'code': 'IT', 'name': 'Italy'},
        {'code': 'FR', 'name': 'France'},
        {'code': 'UK', 'name': 'United Kingdom'},
        {'code': 'UA', 'name': 'Ukraine'},
        {'code': 'RU', 'name': 'Russia'},
        {'code': 'TR', 'name': 'Turkey'},
        {'code': 'PT', 'name': 'Portugal'},
        {'code': 'GR', 'name': 'Greece'},
        {'code': 'RO', 'name': 'Romania'},
        {'code': 'BG', 'name': 'Bulgaria'},
        {'code': 'HU', 'name': 'Hungary'},
        {'code': 'CZ', 'name': 'Czech Republic'},
        {'code': 'SK', 'name': 'Slovakia'},
        {'code': 'SI', 'name': 'Slovenia'},
        {'code': 'HR', 'name': 'Croatia'},
    ]

def get_device_data():
    """Возвращает данные об устройствах"""
    return [
        # Desktop
        {'category': 'desktop', 'browser': 'Chrome', 'os': 'Windows', 'version': '10'},
        {'category': 'desktop', 'browser': 'Chrome', 'os': 'macOS', 'version': '13'},
        {'category': 'desktop', 'browser': 'Firefox', 'os': 'Windows', 'version': '10'},
        {'category': 'desktop', 'browser': 'Safari', 'os': 'macOS', 'version': '13'},
        {'category': 'desktop', 'browser': 'Edge', 'os': 'Windows', 'version': '10'},
        
        # Mobile
        {'category': 'mobile', 'browser': 'Chrome', 'os': 'Android', 'version': '13'},
        {'category': 'mobile', 'browser': 'Safari', 'os': 'iOS', 'version': '16'},
        {'category': 'mobile', 'browser': 'Samsung Internet', 'os': 'Android', 'version': '13'},
        {'category': 'mobile', 'browser': 'Firefox', 'os': 'Android', 'version': '13'},
        
        # Tablet
        {'category': 'tablet', 'browser': 'Safari', 'os': 'iOS', 'version': '16'},
        {'category': 'tablet', 'browser': 'Chrome', 'os': 'Android', 'version': '13'},
    ]

def get_profession_data():
    """Возвращает данные о профессиях"""
    return [
        {'name': 'Tandarts', 'name_nl': 'Tandarts', 'code': 'TAND', 'category': 'dental'},
        {'name': 'Apotheker', 'name_nl': 'Apotheker', 'code': 'APOT', 'category': 'pharmacy'},
        {'name': 'Huisarts', 'name_nl': 'Huisarts', 'code': 'HUIS', 'category': 'medical'},
        {'name': 'Verpleegkundige', 'name_nl': 'Verpleegkundige', 'code': 'VERP', 'category': 'medical'},
        {'name': 'Fysiotherapeut', 'name_nl': 'Fysiotherapeut', 'code': 'FYSI', 'category': 'medical'},
        {'name': 'Psycholoog', 'name_nl': 'Psycholoog', 'code': 'PSYC', 'category': 'medical'},
        {'name': 'Dierenarts', 'name_nl': 'Dierenarts', 'code': 'DIER', 'category': 'veterinary'},
    ]

def populate_country_analytics():
    """Заполняет аналитику по странам"""
    print("🌍 Заполнение аналитики по странам...")
    
    countries = get_country_data()
    
    for country_data in countries:
        # Проверяем, существует ли уже запись
        existing = CountryAnalytics.query.filter_by(country_code=country_data['code']).first()
        
        if existing:
            print(f"  ✅ {country_data['name']} уже существует")
            continue
        
        # Создаем новую запись с случайными данными
        analytics = CountryAnalytics(
            country_code=country_data['code'],
            country_name=country_data['name'],
            total_users=random.randint(50, 2000),
            active_users=random.randint(20, 800),
            new_users_today=random.randint(0, 20),
            new_users_this_week=random.randint(5, 100),
            new_users_this_month=random.randint(20, 300),
            conversion_rate=random.uniform(5, 25),
            completion_rate=random.uniform(30, 80),
            exam_pass_rate=random.uniform(60, 95),
            avg_session_duration=random.uniform(5, 45),
            avg_pages_per_session=random.uniform(3, 15),
            bounce_rate=random.uniform(20, 60),
            total_revenue=random.uniform(1000, 50000),
            avg_revenue_per_user=random.uniform(50, 500)
        )
        
        db.session.add(analytics)
        print(f"  ➕ Добавлена аналитика для {country_data['name']}")
    
    db.session.commit()
    print("✅ Аналитика по странам заполнена")

def populate_device_analytics():
    """Заполняет аналитику по устройствам"""
    print("📱 Заполнение аналитики по устройствам...")
    
    devices = get_device_data()
    
    for device_data in devices:
        # Проверяем, существует ли уже запись
        existing = DeviceAnalytics.query.filter_by(
            device_category=device_data['category'],
            browser=device_data['browser'],
            os=device_data['os']
        ).first()
        
        if existing:
            print(f"  ✅ {device_data['browser']} на {device_data['os']} уже существует")
            continue
        
        # Создаем новую запись с случайными данными
        analytics = DeviceAnalytics(
            device_category=device_data['category'],
            device_type=f"{device_data['browser']} Device" if device_data['category'] == 'mobile' else None,
            browser=device_data['browser'],
            browser_version=device_data.get('version'),
            os=device_data['os'],
            os_version=device_data.get('version'),
            screen_resolution=f"{random.randint(1920, 2560)}x{random.randint(1080, 1440)}" if device_data['category'] == 'desktop' else f"{random.randint(375, 414)}x{random.randint(667, 896)}",
            users_count=random.randint(100, 1500),
            sessions_count=random.randint(200, 3000),
            page_views_count=random.randint(500, 8000),
            avg_page_load_time=random.uniform(1, 6),
            bounce_rate=random.uniform(15, 50),
            avg_session_duration=random.uniform(3, 30),
            avg_pages_per_session=random.uniform(2, 12),
            conversion_rate=random.uniform(8, 25),
            completion_rate=random.uniform(40, 85)
        )
        
        db.session.add(analytics)
        print(f"  ➕ Добавлена аналитика для {device_data['browser']} на {device_data['os']}")
    
    db.session.commit()
    print("✅ Аналитика по устройствам заполнена")

def populate_profession_analytics():
    """Заполняет аналитику по профессиям"""
    print("👨‍⚕️ Заполнение аналитики по профессиям...")
    
    professions_data = get_profession_data()
    
    for prof_data in professions_data:
        # Сначала создаем профессию, если её нет
        profession = Profession.query.filter_by(code=prof_data['code']).first()
        
        if not profession:
            profession = Profession(
                name=prof_data['name'],
                name_nl=prof_data['name_nl'],
                code=prof_data['code'],
                category=prof_data['category'],
                big_exam_required=True,
                description=f"Профессия {prof_data['name']}",
                is_active=True
            )
            db.session.add(profession)
            db.session.flush()  # Получаем ID
        
        # Проверяем, существует ли уже аналитика
        existing = ProfessionAnalytics.query.filter_by(profession_id=profession.id).first()
        
        if existing:
            print(f"  ✅ Аналитика для {prof_data['name']} уже существует")
            continue
        
        # Создаем новую запись с случайными данными
        analytics = ProfessionAnalytics(
            profession_id=profession.id,
            total_registrations=random.randint(50, 1000),
            new_registrations_today=random.randint(0, 10),
            new_registrations_this_week=random.randint(2, 50),
            new_registrations_this_month=random.randint(10, 150),
            active_users=random.randint(20, 400),
            users_with_progress=random.randint(30, 600),
            users_completed_courses=random.randint(5, 100),
            avg_progress=random.uniform(20, 90),
            avg_time_spent=random.uniform(5, 50),
            avg_lessons_completed=random.uniform(2, 20),
            total_exam_attempts=random.randint(10, 200),
            successful_exam_attempts=random.randint(5, 150),
            exam_pass_rate=random.uniform(60, 95),
            avg_exam_score=random.uniform(70, 95),
            avg_session_duration=random.uniform(10, 60),
            avg_sessions_per_user=random.uniform(3, 15),
            retention_rate_7d=random.uniform(40, 80),
            retention_rate_30d=random.uniform(20, 60)
        )
        
        db.session.add(analytics)
        print(f"  ➕ Добавлена аналитика для {prof_data['name']}")
    
    db.session.commit()
    print("✅ Аналитика по профессиям заполнена")

def populate_analytics_events():
    """Заполняет события аналитики"""
    print("📈 Заполнение событий аналитики...")
    
    event_types = [
        {'name': 'page_view', 'category': 'user', 'action': 'view'},
        {'name': 'button_click', 'category': 'user', 'action': 'click'},
        {'name': 'form_submit', 'category': 'user', 'action': 'submit'},
        {'name': 'login', 'category': 'user', 'action': 'submit'},
        {'name': 'registration', 'category': 'user', 'action': 'submit'},
        {'name': 'course_start', 'category': 'user', 'action': 'view'},
        {'name': 'lesson_complete', 'category': 'user', 'action': 'submit'},
        {'name': 'exam_start', 'category': 'user', 'action': 'view'},
        {'name': 'exam_complete', 'category': 'user', 'action': 'submit'},
        {'name': 'error_occurred', 'category': 'error', 'action': 'error'},
        {'name': 'performance_issue', 'category': 'performance', 'action': 'error'},
        {'name': 'system_startup', 'category': 'system', 'action': 'start'},
    ]
    
    countries = get_country_data()
    devices = get_device_data()
    
    # Получаем пользователей
    users = User.query.limit(50).all()
    
    # Создаем события за последние 30 дней
    for i in range(500):
        event_type = random.choice(event_types)
        country = random.choice(countries)
        device = random.choice(devices)
        user = random.choice(users) if users else None
        
        # Случайная дата за последние 30 дней
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)
        
        created_at = datetime.utcnow() - timedelta(
            days=days_ago,
            hours=hours_ago,
            minutes=minutes_ago
        )
        
        event = AnalyticsEvent(
            user_id=user.id if user else None,
            event_name=event_type['name'],
            event_category=event_type['category'],
            event_action=event_type['action'],
            event_label=f"Sample event {i+1}",
            event_data=json.dumps({
                'sample': True,
                'index': i+1,
                'timestamp': created_at.isoformat()
            }),
            event_value=random.uniform(1, 100) if random.random() > 0.5 else None,
            page_url=f"/sample/page/{i+1}",
            referrer_url=f"/referrer/{i+1}" if random.random() > 0.3 else None,
            user_agent=f"Mozilla/5.0 ({device['os']}) {device['browser']}/1.0",
            ip_address=f"192.168.1.{random.randint(1, 254)}",
            device_type=device['category'],
            browser=device['browser'],
            os=device['os'],
            country=country['name'],
            city=f"City {random.randint(1, 100)}",
            created_at=created_at
        )
        
        db.session.add(event)
        
        if (i + 1) % 100 == 0:
            print(f"  ➕ Добавлено {i+1} событий...")
    
    db.session.commit()
    print("✅ События аналитики заполнены")

def main():
    """Основная функция"""
    print("🚀 ЗАПОЛНЕНИЕ АНАЛИТИЧЕСКИХ ДАННЫХ")
    print("=" * 50)
    
    with app.app_context():
        try:
            # Создаем таблицы если их нет
            db.create_all()
            print("✅ Таблицы созданы/проверены")
            
            # Заполняем данные
            populate_country_analytics()
            populate_device_analytics()
            populate_profession_analytics()
            populate_analytics_events()
            
            print("\n🎉 ВСЕ ДАННЫЕ ЗАПОЛНЕНЫ УСПЕШНО!")
            print("=" * 50)
            
            # Показываем статистику
            print(f"📊 Статистика:")
            print(f"  🌍 Стран: {CountryAnalytics.query.count()}")
            print(f"  📱 Устройств: {DeviceAnalytics.query.count()}")
            print(f"  👨‍⚕️ Профессий: {ProfessionAnalytics.query.count()}")
            print(f"  📈 Событий: {AnalyticsEvent.query.count()}")
            
        except Exception as e:
            print(f"❌ Ошибка: {str(e)}")
            db.session.rollback()
            return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
