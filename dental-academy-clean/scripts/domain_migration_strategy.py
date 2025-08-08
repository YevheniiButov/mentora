#!/usr/bin/env python3
"""
Стратегия миграции доменов для исправления потери данных (29→30 доменов)
Объединяет дублирующиеся домены и создает отсутствующие
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, BIGDomain, Question, DiagnosticResponse, PersonalLearningPlan
import json
from collections import defaultdict

def create_migration_strategy():
    """Создание стратегии миграции доменов"""
    
    with app.app_context():
        print("🔧 СТРАТЕГИЯ МИГРАЦИИ ДОМЕНОВ")
        print("=" * 50)
        
        # 1. Анализ текущего состояния
        print("\n1. АНАЛИЗ ТЕКУЩЕГО СОСТОЯНИЯ:")
        
        domains = BIGDomain.query.all()
        domain_map = {d.code: d for d in domains}
        
        # Проверка отсутствующих доменов
        expected_domains = set(BIGDomain.DOMAIN_CODES.keys())
        existing_domains = set(domain_map.keys())
        missing_domains = expected_domains - existing_domains
        
        print(f"   Ожидаемые домены: {len(expected_domains)}")
        print(f"   Существующие домены: {len(existing_domains)}")
        print(f"   Отсутствующие домены: {list(missing_domains)}")
        
        # 2. Анализ дублирования в планах обучения
        print("\n2. АНАЛИЗ ДУБЛИРОВАНИЯ В ПЛАНАХ ОБУЧЕНИЯ:")
        
        plans = PersonalLearningPlan.query.all()
        domain_variations = defaultdict(set)
        
        for plan in plans:
            if plan.domain_analysis:
                try:
                    analysis = plan.get_domain_analysis()
                    if analysis:
                        for domain_code in analysis.keys():
                            domain_variations[domain_code].add(domain_code)
                except:
                    pass
        
        # Выявление вариаций названий доменов
        print("   Вариации названий доменов:")
        for base_domain, variations in domain_variations.items():
            if len(variations) > 1:
                print(f"     {base_domain}: {list(variations)}")
        
        # 3. Создание карты миграции
        print("\n3. КАРТА МИГРАЦИИ:")
        
        migration_map = {
            # Объединение дублирующихся доменов
            'PHARMA': 'PHARMACOLOGY',  # PHARMA → PHARMACOLOGY
            'FARMACOLOGIE': 'PHARMACOLOGY',  # FARMACOLOGIE → PHARMACOLOGY
            'DIAGNOSIS_SPECIAL': 'DIAGNOSIS',  # DIAGNOSIS_SPECIAL → DIAGNOSIS
            
            # Старые названия → новые коды
            'Caries': 'THER',
            'Endodontics': 'THER', 
            'Periodontics': 'PARO',
            'Anatomy': 'ANATOMIE',
            'Pharmacology': 'PHARMACOLOGY',
            'Diagnostics': 'DIAGNOSIS',
            'Surgery': 'SURG',
            'Emergency': 'EMERGENCY',
            
            # Русские названия → коды
            'Терапевтическая стоматология': 'THER',
            'Хирургическая стоматология': 'SURG',
            'Ортопедическая стоматология': 'PROTH',
            'Детская стоматология': 'PEDI',
            'Пародонтология': 'PARO',
            'Ортодонтия': 'ORTHO',
            'Профилактика': 'PREV',
            'Этика и право': 'ETHIEK',
            'Анатомия': 'ANATOMIE',
            'Физиология': 'FYSIOLOGIE',
            'Патология': 'PATHOLOGIE',
            'Микробиология': 'MICROBIOLOGIE',
            'Материаловедение': 'MATERIAALKUNDE',
            'Рентгенология': 'RADIOLOGIE',
            'Общая медицина': 'ALGEMENE_GENEESKUNDE',
            'Неотложная помощь': 'EMERGENCY',
            'Системные заболевания': 'SYSTEMIC',
            'Фармакология': 'PHARMACOLOGY',
            'Инфекционный контроль': 'INFECTION',
            'Специальные группы пациентов': 'SPECIAL',
            'Сложная диагностика': 'DIAGNOSIS',
            'Голландская система здравоохранения': 'DUTCH',
            'Профессиональное развитие': 'PROFESSIONAL',
            'Практические навыки': 'PRACTICAL_SKILLS',
            'Планирование лечения': 'TREATMENT_PLANNING',
            'Коммуникативные навыки': 'COMMUNICATION',
            'Статистика и анализ данных': 'STATISTICS',
            
            # Английские названия → коды
            'Orthodontics': 'ORTHO',
            'Oral Surgery': 'SURG',
            'Prosthodontics': 'PROTH',
            'Preventive Care': 'PREV',
            'Dental Materials': 'MATERIAALKUNDE',
            'Oral Pathology': 'PATHOLOGIE',
            'Oral Medicine': 'ALGEMENE_GENEESKUNDE',
            'Dental Radiology': 'RADIOLOGIE',
            'Dental Anatomy': 'ANATOMIE',
            'Dental Physiology': 'FYSIOLOGIE',
            'Dental Pharmacology': 'PHARMACOLOGY',
            'Dental Anesthesia': 'EMERGENCY',
            'Dental Emergency': 'EMERGENCY',
            'Dental Ethics': 'ETHIEK',
            'Dental Law': 'ETHIEK',
            'Practice Management': 'PROFESSIONAL',
            'Patient Communication': 'COMMUNICATION',
            'Infection Control': 'INFECTION',
            'Dental Implants': 'PROTH',
            'Cosmetic Dentistry': 'PROTH',
            'Pediatric Dentistry': 'PEDI',
            'Geriatric Dentistry': 'SPECIAL',
            'Special Needs Dentistry': 'SPECIAL'
        }
        
        print("   Карта миграции создана:")
        for old_name, new_code in migration_map.items():
            print(f"     {old_name} → {new_code}")
        
        # 4. Создание плана миграции
        print("\n4. ПЛАН МИГРАЦИИ:")
        
        migration_plan = {
            'step_1': {
                'description': 'Создание отсутствующего домена PHARMACOLOGY',
                'actions': [
                    'Создать домен PHARMACOLOGY с правильными параметрами',
                    'Обновить все вопросы с domain=PHARMA на domain=PHARMACOLOGY',
                    'Обновить все DiagnosticResponse с вопросами PHARMA'
                ]
            },
            'step_2': {
                'description': 'Объединение дублирующихся доменов',
                'actions': [
                    'Объединить PHARMA и FARMACOLOGIE в PHARMACOLOGY',
                    'Объединить DIAGNOSIS_SPECIAL в DIAGNOSIS',
                    'Обновить все ссылки в базе данных'
                ]
            },
            'step_3': {
                'description': 'Миграция планов обучения',
                'actions': [
                    'Обновить все PersonalLearningPlan.domain_analysis',
                    'Заменить старые названия доменов на коды',
                    'Обеспечить наличие всех 30 доменов в каждом плане'
                ]
            },
            'step_4': {
                'description': 'Валидация миграции',
                'actions': [
                    'Проверить целостность данных',
                    'Убедиться, что все 30 доменов присутствуют',
                    'Проверить отсутствие потери данных'
                ]
            }
        }
        
        for step_name, step_info in migration_plan.items():
            print(f"   {step_name.upper()}: {step_info['description']}")
            for action in step_info['actions']:
                print(f"     - {action}")
        
        # 5. Сохранение стратегии
        strategy_data = {
            'migration_map': migration_map,
            'migration_plan': migration_plan,
            'missing_domains': list(missing_domains),
            'domain_variations': {k: list(v) for k, v in domain_variations.items()},
            'current_domains': {d.code: d.name for d in domains},
            'expected_domains': BIGDomain.DOMAIN_CODES
        }
        
        with open('analysis/domain_migration_strategy.json', 'w', encoding='utf-8') as f:
            json.dump(strategy_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 Стратегия сохранена в: analysis/domain_migration_strategy.json")
        
        return strategy_data

if __name__ == '__main__':
    create_migration_strategy() 