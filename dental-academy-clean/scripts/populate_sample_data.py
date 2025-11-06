#!/usr/bin/env python3
"""
Скрипт для заполнения примерами данных
Создает тестовые данные для демонстрации функциональности CRM и аналитики
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, User
from admin_models import Profession, Contact, ContactActivity, CountryAnalytics, DeviceAnalytics, ProfessionAnalytics
from datetime import datetime, timedelta, date
import json
import random

def create_sample_data():
    """Создает примеры данных для демонстрации"""
    
    with app.app_context():
        print("🚀 Создание примеров данных для CRM и аналитики...")
        
        # Получаем админа
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            print("❌ Админ не найден. Создайте админа сначала.")
            return
        
        # 1. Создаем профессии
        print("👨‍⚕️ Создание профессий...")
        professions_data = [
            {
                'name': 'Dentist',
                'name_nl': 'Tandarts',
                'code': 'DENT',
                'category': 'dental',
                'description': 'Стоматолог - специалист по лечению зубов и полости рта',
                'big_exam_required': True,
                'dutch_language_required': True,
                'experience_required': 2,
                'salary_range': '€60,000 - €120,000',
                'is_popular': True
            },
            {
                'name': 'General Practitioner',
                'name_nl': 'Huisarts',
                'code': 'GP',
                'category': 'medical',
                'description': 'Врач общей практики - первый контакт с пациентами',
                'big_exam_required': True,
                'dutch_language_required': True,
                'experience_required': 3,
                'salary_range': '€70,000 - €150,000',
                'is_popular': True
            },
            {
                'name': 'Nurse',
                'name_nl': 'Verpleegkundige',
                'code': 'NURSE',
                'category': 'nursing',
                'description': 'Медсестра - уход за пациентами и медицинская помощь',
                'big_exam_required': True,
                'dutch_language_required': True,
                'experience_required': 1,
                'salary_range': '€35,000 - €60,000',
                'is_popular': True
            },
            {
                'name': 'Pharmacist',
                'name_nl': 'Apotheker',
                'code': 'PHARM',
                'category': 'pharmacy',
                'description': 'Фармацевт - специалист по лекарственным препаратам',
                'big_exam_required': True,
                'dutch_language_required': True,
                'experience_required': 2,
                'salary_range': '€50,000 - €90,000',
                'is_popular': False
            },
            {
                'name': 'Physiotherapist',
                'name_nl': 'Fysiotherapeut',
                'code': 'PHYSIO',
                'category': 'medical',
                'description': 'Физиотерапевт - восстановление физических функций',
                'big_exam_required': True,
                'dutch_language_required': True,
                'experience_required': 1,
                'salary_range': '€40,000 - €70,000',
                'is_popular': False
            }
        ]
        
        created_professions = []
        for prof_data in professions_data:
            existing = Profession.query.filter_by(code=prof_data['code']).first()
            if not existing:
                profession = Profession(**prof_data)
                db.session.add(profession)
                created_professions.append(profession)
            else:
                created_professions.append(existing)
        
        db.session.commit()
        print(f"✅ Создано {len(created_professions)} профессий")
        
        # 2. Создаем контакты
        print("👥 Создание контактов...")
        countries = ['Ukraine', 'Poland', 'Romania', 'Bulgaria', 'Lithuania', 'Latvia', 'Estonia', 'Slovakia', 'Czech Republic', 'Hungary']
        cities = ['Kyiv', 'Warsaw', 'Bucharest', 'Sofia', 'Vilnius', 'Riga', 'Tallinn', 'Bratislava', 'Prague', 'Budapest']
        lead_sources = ['Google Ads', 'Facebook', 'LinkedIn', 'Website', 'Referral', 'Email Campaign', 'Conference', 'Direct']
        
        sample_contacts = []
        for i in range(100):
            country = random.choice(countries)
            city = random.choice(cities)
            profession = random.choice(created_professions)
            
            contact = Contact(
                full_name=f"Contact {i+1}",
                email=f"contact{i+1}@example.com",
                phone=f"+380{random.randint(100000000, 999999999)}",
                country=country,
                city=city,
                profession_id=profession.id,
                contact_status=random.choice(['lead', 'prospect', 'active', 'converted']),
                lead_source=random.choice(lead_sources),
                lead_score=random.randint(0, 100),
                years_of_experience=random.randint(0, 15),
                education_level=random.choice(['Bachelor', 'Master', 'PhD']),
                dutch_level=random.choice(['A1', 'A2', 'B1', 'B2', 'C1', 'C2']),
                english_level=random.choice(['B1', 'B2', 'C1', 'C2']),
                budget_range=random.choice(['€1,000-5,000', '€5,000-10,000', '€10,000+']),
                notes=f"Sample contact {i+1} for demonstration purposes",
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 365))
            )
            
            db.session.add(contact)
            sample_contacts.append(contact)
        
        db.session.commit()
        print(f"✅ Создано {len(sample_contacts)} контактов")
        
        # 3. Создаем активность контактов
        print("📈 Создание активности контактов...")
        activity_types = ['call', 'email', 'meeting', 'note', 'task']
        outcomes = ['Positive', 'Neutral', 'Negative', 'Follow-up needed', 'Converted']
        
        for contact in sample_contacts[:50]:  # Активность только для первых 50 контактов
            num_activities = random.randint(1, 5)
            for j in range(num_activities):
                activity = ContactActivity(
                    contact_id=contact.id,
                    user_id=admin.id,
                    activity_type=random.choice(activity_types),
                    subject=f"Activity {j+1} for {contact.full_name}",
                    description=f"Sample activity description for contact {contact.full_name}",
                    duration=random.randint(5, 120),
                    outcome=random.choice(outcomes),
                    status=random.choice(['completed', 'planned']),
                    priority=random.choice(['low', 'normal', 'high']),
                    created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
                )
                
                db.session.add(activity)
        
        db.session.commit()
        print("✅ Создана активность контактов")
        
        # 4. Создаем аналитику по странам
        print("🌍 Создание аналитики по странам...")
        for country in countries:
            existing = CountryAnalytics.query.filter_by(country_name=country).first()
            if not existing:
                country_analytics = CountryAnalytics(
                    country_code=country[:2].upper(),
                    country_name=country,
                    total_users=random.randint(10, 100),
                    active_users=random.randint(5, 50),
                    new_users_today=random.randint(0, 5),
                    new_users_this_week=random.randint(0, 20),
                    new_users_this_month=random.randint(0, 50),
                    conversion_rate=random.uniform(10, 80),
                    completion_rate=random.uniform(20, 90),
                    exam_pass_rate=random.uniform(30, 95),
                    avg_session_duration=random.uniform(10, 60),
                    avg_pages_per_session=random.uniform(3, 15),
                    bounce_rate=random.uniform(10, 50),
                    total_revenue=random.uniform(1000, 50000),
                    avg_revenue_per_user=random.uniform(50, 500)
                )
                
                db.session.add(country_analytics)
        
        db.session.commit()
        print("✅ Создана аналитика по странам")
        
        # 5. Создаем аналитику по устройствам
        print("📱 Создание аналитики по устройствам...")
        device_categories = ['mobile', 'desktop', 'tablet']
        browsers = ['Chrome', 'Safari', 'Firefox', 'Edge', 'Opera']
        operating_systems = ['Windows', 'macOS', 'iOS', 'Android', 'Linux']
        
        for category in device_categories:
            for browser in browsers:
                for os in operating_systems:
                    device_analytics = DeviceAnalytics(
                        device_category=category,
                        browser=browser,
                        os=os,
                        users_count=random.randint(5, 100),
                        sessions_count=random.randint(10, 500),
                        page_views_count=random.randint(50, 2000),
                        avg_page_load_time=random.uniform(1, 5),
                        bounce_rate=random.uniform(10, 60),
                        avg_session_duration=random.uniform(5, 45),
                        avg_pages_per_session=random.uniform(2, 12),
                        conversion_rate=random.uniform(5, 40),
                        completion_rate=random.uniform(15, 85)
                    )
                    
                    db.session.add(device_analytics)
        
        db.session.commit()
        print("✅ Создана аналитика по устройствам")
        
        # 6. Создаем аналитику по профессиям
        print("👨‍⚕️ Создание аналитики по профессиям...")
        for profession in created_professions:
            profession_analytics = ProfessionAnalytics(
                profession_id=profession.id,
                total_registrations=random.randint(20, 200),
                new_registrations_today=random.randint(0, 5),
                new_registrations_this_week=random.randint(0, 20),
                new_registrations_this_month=random.randint(0, 50),
                active_users=random.randint(10, 100),
                users_with_progress=random.randint(5, 80),
                users_completed_courses=random.randint(2, 50),
                avg_progress=random.uniform(20, 90),
                avg_time_spent=random.uniform(10, 100),
                avg_lessons_completed=random.uniform(5, 50),
                total_exam_attempts=random.randint(10, 100),
                successful_exam_attempts=random.randint(5, 80),
                exam_pass_rate=random.uniform(40, 95),
                avg_exam_score=random.uniform(60, 95),
                avg_session_duration=random.uniform(15, 60),
                avg_sessions_per_user=random.uniform(2, 20),
                retention_rate_7d=random.uniform(30, 80),
                retention_rate_30d=random.uniform(20, 70)
            )
            
            db.session.add(profession_analytics)
        
        db.session.commit()
        print("✅ Создана аналитика по профессиям")
        
        print("🎉 Все примеры данных созданы успешно!")
        print(f"📊 Создано:")
        print(f"   - {len(created_professions)} профессий")
        print(f"   - {len(sample_contacts)} контактов")
        print(f"   - Активность для {min(50, len(sample_contacts))} контактов")
        print(f"   - Аналитика по {len(countries)} странам")
        print(f"   - Аналитика по {len(device_categories) * len(browsers) * len(operating_systems)} комбинациям устройств")
        print(f"   - Аналитика по {len(created_professions)} профессиям")

if __name__ == '__main__':
    create_sample_data()
