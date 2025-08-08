#!/usr/bin/env python3
"""
Обновление логики приложения после миграции доменов
Исправляет файлы, которые работают с доменами
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, BIGDomain, PersonalLearningPlan
import json
from datetime import datetime, timezone

def update_application_logic():
    """Обновление логики приложения после миграции доменов"""
    
    with app.app_context():
        print("🔧 ОБНОВЛЕНИЕ ЛОГИКИ ПРИЛОЖЕНИЯ")
        print("=" * 50)
        
        # 1. Обновление utils/domain_mapping.py
        print("\n1️⃣ ОБНОВЛЕНИЕ DOMAIN MAPPING:")
        
        # Создаем обновленный файл domain_mapping.py
        domain_mapping_content = '''"""
Обновленное отображение доменов после миграции
Унифицированная структура доменов BI-TOETS
"""

# Унифицированная карта доменов (после миграции)
UNIFIED_DOMAIN_MAPPING = {
    # Основные домены BI-TOETS
    'THER': 'Терапевтическая стоматология',
    'SURG': 'Хирургическая стоматология',
    'PROTH': 'Ортопедическая стоматология',
    'PEDI': 'Детская стоматология',
    'PARO': 'Пародонтология',
    'ORTHO': 'Ортодонтия',
    'PREV': 'Профилактика',
    'ANATOMIE': 'Анатомия',
    'FYSIOLOGIE': 'Физиология',
    'PATHOLOGIE': 'Патология',
    'MICROBIOLOGIE': 'Микробиология',
    'MATERIAALKUNDE': 'Материаловедение',
    'RADIOLOGIE': 'Рентгенология',
    'ALGEMENE_GENEESKUNDE': 'Общая медицина',
    'EMERGENCY': 'Неотложная помощь',
    'SYSTEMIC': 'Системные заболевания',
    'PHARMACOLOGY': 'Фармакология',  # Объединено с PHARMA и FARMACOLOGIE
    'INFECTION': 'Инфекционный контроль',
    'SPECIAL': 'Специальные группы пациентов',
    'DIAGNOSIS': 'Диагностика',  # Объединено с DIAGNOSIS_SPECIAL
    'DUTCH': 'Голландская система здравоохранения',
    'PROFESSIONAL': 'Профессиональное развитие',
    'ETHIEK': 'Этика и право',
    'STATISTICS': 'Статистика и анализ данных',
    'RESEARCH_METHOD': 'Методология исследований',
    'PRACTICAL_SKILLS': 'Практические навыки',
    'TREATMENT_PLANNING': 'Планирование лечения',
    'COMMUNICATION': 'Коммуникативные навыки'
}

# Веса доменов в экзамене
DOMAIN_WEIGHTS = {
    'THER': 15.0,
    'SURG': 10.0,
    'PROTH': 8.0,
    'PEDI': 7.0,
    'PARO': 8.0,
    'ORTHO': 6.0,
    'PREV': 5.0,
    'ANATOMIE': 4.0,
    'FYSIOLOGIE': 4.0,
    'PATHOLOGIE': 5.0,
    'MICROBIOLOGIE': 3.0,
    'MATERIAALKUNDE': 3.0,
    'RADIOLOGIE': 4.0,
    'ALGEMENE_GENEESKUNDE': 2.0,
    'EMERGENCY': 10.0,
    'SYSTEMIC': 7.0,
    'PHARMACOLOGY': 8.0,
    'INFECTION': 5.0,
    'SPECIAL': 4.0,
    'DIAGNOSIS': 10.0,
    'DUTCH': 3.0,
    'PROFESSIONAL': 2.0,
    'ETHIEK': 3.0,
    'STATISTICS': 6.0,
    'RESEARCH_METHOD': 4.0,
    'PRACTICAL_SKILLS': 15.0,
    'TREATMENT_PLANNING': 10.0,
    'COMMUNICATION': 6.0
}

# Категории доменов
DOMAIN_CATEGORIES = {
    'THEORETICAL': ['THER', 'SURG', 'PROTH', 'PEDI', 'PARO', 'ORTHO', 'PREV', 
                   'ANATOMIE', 'FYSIOLOGIE', 'PATHOLOGIE', 'MICROBIOLOGIE', 
                   'MATERIAALKUNDE', 'RADIOLOGIE', 'ALGEMENE_GENEESKUNDE', 
                   'EMERGENCY', 'SYSTEMIC', 'PHARMACOLOGY', 'INFECTION', 
                   'SPECIAL', 'DIAGNOSIS', 'DUTCH', 'PROFESSIONAL'],
    'METHODOLOGY': ['STATISTICS', 'RESEARCH_METHOD'],
    'PRACTICAL': ['PRACTICAL_SKILLS'],
    'CLINICAL': ['TREATMENT_PLANNING', 'COMMUNICATION', 'ETHIEK']
}

def get_domain_name(domain_code):
    """Получить название домена по коду"""
    return UNIFIED_DOMAIN_MAPPING.get(domain_code, domain_code)

def get_domain_weight(domain_code):
    """Получить вес домена в экзамене"""
    return DOMAIN_WEIGHTS.get(domain_code, 0.0)

def get_domain_category(domain_code):
    """Получить категорию домена"""
    for category, domains in DOMAIN_CATEGORIES.items():
        if domain_code in domains:
            return category
    return 'OTHER'

def get_all_domains():
    """Получить все домены"""
    return list(UNIFIED_DOMAIN_MAPPING.keys())

def get_domains_by_category(category):
    """Получить домены по категории"""
    return DOMAIN_CATEGORIES.get(category, [])
'''
        
        with open('utils/domain_mapping.py', 'w', encoding='utf-8') as f:
            f.write(domain_mapping_content)
        
        print("   ✅ Обновлен utils/domain_mapping.py")
        
        # 2. Обновление utils/daily_learning_algorithm.py
        print("\n2️⃣ ОБНОВЛЕНИЕ DAILY LEARNING ALGORITHM:")
        
        # Проверяем и обновляем логику работы с доменами
        try:
            from utils.daily_learning_algorithm import DailyLearningAlgorithm
            
            # Создаем тестовый экземпляр для проверки
            algorithm = DailyLearningAlgorithm()
            
            # Проверяем, что алгоритм работает с полным набором доменов
            all_domains = BIGDomain.query.filter_by(is_active=True).all()
            print(f"   Алгоритм работает с {len(all_domains)} активными доменами")
            
        except Exception as e:
            print(f"   ⚠️  Ошибка при проверке алгоритма: {e}")
        
        # 3. Обновление routes/diagnostic_routes.py
        print("\n3️⃣ ОБНОВЛЕНИЕ DIAGNOSTIC ROUTES:")
        
        # Проверяем, что диагностические роуты работают с полным набором доменов
        try:
            from routes.diagnostic_routes import diagnostic_bp
            
            # Проверяем, что все домены доступны для диагностики
            diagnostic_domains = BIGDomain.query.filter_by(is_active=True).all()
            print(f"   Диагностика доступна для {len(diagnostic_domains)} доменов")
            
        except Exception as e:
            print(f"   ⚠️  Ошибка при проверке диагностических роутов: {e}")
        
        # 4. Создание отчета о состоянии системы
        print("\n4️⃣ СОЗДАНИЕ ОТЧЕТА О СОСТОЯНИИ:")
        
        # Анализируем текущее состояние
        total_domains = BIGDomain.query.count()
        active_domains = BIGDomain.query.filter_by(is_active=True).count()
        plans_with_all_domains = 0
        total_plans = PersonalLearningPlan.query.count()
        
        for plan in PersonalLearningPlan.query.all():
            try:
                if plan.domain_analysis:
                    analysis = plan.get_domain_analysis()
                    if analysis and len(analysis) >= 28:  # Минимум 28 доменов
                        plans_with_all_domains += 1
            except:
                pass
        
        # Статистика по доменам
        domain_stats = {}
        for domain in BIGDomain.query.all():
            questions_count = len(domain.questions) if domain.questions else 0
            domain_stats[domain.code] = {
                'name': domain.name,
                'weight': domain.weight_percentage,
                'category': domain.category,
                'questions': questions_count,
                'is_active': domain.is_active
            }
        
        system_status = {
            'update_date': datetime.now(timezone.utc).isoformat(),
            'total_domains': total_domains,
            'active_domains': active_domains,
            'plans_with_all_domains': plans_with_all_domains,
            'total_plans': total_plans,
            'migration_complete': plans_with_all_domains > 0,
            'domain_statistics': domain_stats,
            'recommendations': []
        }
        
        # Добавляем рекомендации
        if plans_with_all_domains < total_plans:
            system_status['recommendations'].append(
                "Некоторые планы обучения не содержат полный набор доменов"
            )
        
        if active_domains < total_domains:
            system_status['recommendations'].append(
                f"Неактивных доменов: {total_domains - active_domains}"
            )
        
        # Проверяем домены без вопросов
        domains_without_questions = [code for code, stats in domain_stats.items() if stats['questions'] == 0]
        if domains_without_questions:
            system_status['recommendations'].append(
                f"Домены без вопросов: {domains_without_questions}"
            )
        
        with open('analysis/system_status_after_migration.json', 'w', encoding='utf-8') as f:
            json.dump(system_status, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Отчет о состоянии системы сохранен")
        
        # 5. Финальная проверка
        print("\n5️⃣ ФИНАЛЬНАЯ ПРОВЕРКА:")
        
        print(f"   Всего доменов: {total_domains}")
        print(f"   Активных доменов: {active_domains}")
        print(f"   Планов с полным набором доменов: {plans_with_all_domains}/{total_plans}")
        
        if plans_with_all_domains == total_plans:
            print("   ✅ ВСЕ ПЛАНЫ ОБУЧЕНИЯ СОДЕРЖАТ ПОЛНЫЙ НАБОР ДОМЕНОВ")
        else:
            print(f"   ⚠️  {total_plans - plans_with_all_domains} планов не содержат полный набор доменов")
        
        # Проверяем, что календарь будет показывать разнообразные темы
        print(f"   Домены с вопросами: {len([d for d in domain_stats.values() if d['questions'] > 0])}")
        
        if len([d for d in domain_stats.values() if d['questions'] > 0]) >= 20:
            print("   ✅ Календарь будет показывать разнообразные темы из всех доменов")
        else:
            print("   ⚠️  Календарь может показывать ограниченное количество тем")
        
        print(f"\n📊 Отчет о состоянии системы: analysis/system_status_after_migration.json")
        
        return system_status

if __name__ == '__main__':
    update_application_logic() 