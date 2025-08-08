#!/usr/bin/env python3
"""
Скрипт для проверки того, что отображается в планировщике обучения
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from models import User, PersonalLearningPlan, DiagnosticSession
from datetime import datetime, timezone
import json

def check_planner_display():
    """Проверяет, что отображается в планировщике обучения"""
    
    with app.app_context():
        print("🔍 ПРОВЕРКА ОТОБРАЖЕНИЯ В ПЛАНИРОВЩИКЕ")
        print("=" * 60)
        
        # Проверяем пользователя Demo Gebruiker (ID: 6)
        user = User.query.get(6)
        if not user:
            print("❌ Пользователь Demo Gebruiker не найден")
            return
        
        print(f"👤 Пользователь: {user.get_display_name()} (ID: {user.id})")
        print("-" * 50)
        
        # Получаем активный план
        active_plan = PersonalLearningPlan.query.filter_by(
            user_id=user.id,
            status='active'
        ).first()
        
        if not active_plan:
            print("❌ Активный план не найден")
            return
        
        print(f"📋 Активный план: ID {active_plan.id}")
        
        # Получаем последнюю диагностику
        latest_diagnostic = DiagnosticSession.query.filter_by(
            user_id=user.id,
            status='completed'
        ).order_by(DiagnosticSession.completed_at.desc()).first()
        
        if not latest_diagnostic:
            print("❌ Диагностика не найдена")
            return
        
        print(f"🔬 Диагностика: ID {latest_diagnostic.id}")
        
        # Симулируем логику планировщика
        print(f"\n🔄 СИМУЛЯЦИЯ ЛОГИКИ ПЛАНИРОВЩИКА:")
        print("-" * 40)
        
        # Получаем данные диагностики
        diagnostic_data = latest_diagnostic.generate_results()
        print(f"📄 Diagnostic data: {diagnostic_data}")
        
        # ВСЕ 25 доменов BIG экзамена (как в планировщике)
        ALL_BIG_DOMAINS = {
            'domain_1': 'Endodontics',
            'domain_2': 'Periodontics', 
            'domain_3': 'Orthodontics',
            'domain_4': 'Oral Surgery',
            'domain_5': 'Prosthodontics',
            'domain_6': 'Preventive Care',
            'domain_7': 'Dental Materials',
            'domain_8': 'Oral Pathology',
            'domain_9': 'Oral Medicine',
            'domain_10': 'Dental Radiology',
            'domain_11': 'Dental Anatomy',
            'domain_12': 'Dental Physiology',
            'domain_13': 'Dental Pharmacology',
            'domain_14': 'Dental Anesthesia',
            'domain_15': 'Dental Emergency',
            'domain_16': 'Dental Ethics',
            'domain_17': 'Dental Law',
            'domain_18': 'Practice Management',
            'domain_19': 'Patient Communication',
            'domain_20': 'Infection Control',
            'domain_21': 'Dental Implants',
            'domain_22': 'Cosmetic Dentistry',
            'domain_23': 'Pediatric Dentistry',
            'domain_24': 'Geriatric Dentistry',
            'domain_25': 'Special Needs Dentistry'
        }
        
        # Маппинг старых доменов на новые
        OLD_TO_NEW_DOMAIN_MAPPING = {
            'THER': 'domain_1',      # Терапевтическая стоматология -> Endodontics
            'SURG': 'domain_4',      # Хирургическая стоматология -> Oral Surgery
            'PROTH': 'domain_5',     # Ортопедическая стоматология -> Prosthodontics
            'PEDI': 'domain_23',     # Детская стоматология -> Pediatric Dentistry
            'PARO': 'domain_2',      # Пародонтология -> Periodontics
            'ORTHO': 'domain_3',     # Ортодонтия -> Orthodontics
            'PREV': 'domain_6',      # Профилактика -> Preventive Care
            'ETHIEK': 'domain_16',   # Этика и право -> Dental Ethics
            'ANATOMIE': 'domain_11', # Анатомия -> Dental Anatomy
            'FYSIOLOGIE': 'domain_12', # Физиология -> Dental Physiology
            'PATHOLOGIE': 'domain_8', # Патология -> Oral Pathology
            'MICROBIOLOGIE': 'domain_20', # Микробиология -> Infection Control
            'MATERIAALKUNDE': 'domain_7', # Материаловедение -> Dental Materials
            'RADIOLOGIE': 'domain_10', # Рентгенология -> Dental Radiology
            'ALGEMENE_GENEESKUNDE': 'domain_9', # Общая медицина -> Oral Medicine
            'EMERGENCY': 'domain_15', # Неотложная помощь -> Dental Emergency
            'SYSTEMIC': 'domain_9',  # Системные заболевания -> Oral Medicine
            'PHARMA': 'domain_13',   # Фармакология -> Dental Pharmacology
            'INFECTION': 'domain_20', # Инфекционный контроль -> Infection Control
            'SPECIAL': 'domain_25',  # Специальные группы пациентов -> Special Needs Dentistry
            'DIAGNOSIS': 'domain_8', # Сложная диагностика -> Oral Pathology
            'DUTCH': 'domain_18',    # Голландская система здравоохранения -> Practice Management
            'PROFESSIONAL': 'domain_17', # Профессиональное развитие -> Dental Law
            'FARMACOLOGIE': 'domain_13', # Фармакология (альтернативное название) -> Dental Pharmacology
            'DIAGNOSIS_SPECIAL': 'domain_8' # Специальная диагностика -> Oral Pathology
        }
        
        # Симулируем логику планировщика
        diagnostic_results = {
            'overall_score': latest_diagnostic.current_ability if latest_diagnostic else 0,
            'domains': []
        }
        
        print(f"\n📊 ДОМЕНЫ В ПЛАНИРОВЩИКЕ:")
        print("-" * 30)
        
        for domain_code, domain_name in ALL_BIG_DOMAINS.items():
            # Проверяем есть ли данные по этому домену (прямое совпадение)
            if (diagnostic_data.get('domain_statistics') and 
                domain_code in diagnostic_data['domain_statistics'] and
                diagnostic_data['domain_statistics'][domain_code].get('has_data', False)):
                
                # Есть прямые данные
                domain_data = diagnostic_data['domain_statistics'][domain_code]
                score = domain_data.get('accuracy_percentage', 0)
                questions_answered = domain_data.get('questions_answered', 0)
                correct_answers = domain_data.get('correct_answers', 0)
                print(f"✅ {domain_name}: {score}% ({correct_answers}/{questions_answered})")
            else:
                # Проверяем маппинг старых доменов
                score = 0
                questions_answered = 0
                correct_answers = 0
                
                # Ищем старый домен, который маппится на этот новый
                for old_domain, new_domain in OLD_TO_NEW_DOMAIN_MAPPING.items():
                    if new_domain == domain_code:
                        if (diagnostic_data.get('domain_statistics') and 
                            old_domain in diagnostic_data['domain_statistics'] and
                            diagnostic_data['domain_statistics'][old_domain].get('has_data', False)):
                            
                            # Нашли данные в старом домене
                            old_domain_data = diagnostic_data['domain_statistics'][old_domain]
                            score = old_domain_data.get('accuracy_percentage', 0)
                            questions_answered = old_domain_data.get('questions_answered', 0)
                            correct_answers = old_domain_data.get('correct_answers', 0)
                            print(f"🔄 {domain_name}: {score}% ({correct_answers}/{questions_answered}) [из {old_domain}]")
                            break
                
                if score == 0:
                    print(f"❌ {domain_name}: 0% (нет данных)")
            
            # Расчет часов
            hours = max(24 - score * 0.3, 8)
            
            domain_result = {
                'code': domain_code,
                'name': domain_name,
                'score': score,
                'target': 85,
                'hours': hours,
                'questions_answered': questions_answered,
                'correct_answers': correct_answers
            }
            
            diagnostic_results['domains'].append(domain_result)
        
        print(f"\n📈 ИТОГОВАЯ СТАТИСТИКА:")
        print("-" * 30)
        print(f"📊 Всего доменов: {len(diagnostic_results['domains'])}")
        
        # Подсчитываем статистику
        total_hours = sum(d['hours'] for d in diagnostic_results['domains'])
        weak_domains = [d for d in diagnostic_results['domains'] if d['score'] < 70]
        strong_domains = [d for d in diagnostic_results['domains'] if d['score'] >= 70]
        
        print(f"⏰ Общее время обучения: {total_hours:.1f} часов")
        print(f"⚠️ Слабых доменов: {len(weak_domains)}")
        print(f"✅ Сильных доменов: {len(strong_domains)}")
        
        if weak_domains:
            print(f"\n⚠️ СЛАБЫЕ ДОМЕНЫ (показываются в планировщике):")
            for domain in weak_domains[:5]:  # Показываем первые 5
                print(f"   • {domain['name']}: {domain['score']}% ({domain['hours']:.1f} ч)")
            if len(weak_domains) > 5:
                print(f"   ... и еще {len(weak_domains) - 5} доменов")
        
        print(f"\n🔍 ВЫВОД:")
        print("-" * 20)
        print("Планировщик показывает данные из диагностики, а не из обновленного плана!")
        print("Нужно обновить логику планировщика, чтобы он использовал данные из PersonalLearningPlan")

if __name__ == "__main__":
    check_planner_display() 