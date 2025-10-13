#!/usr/bin/env python3
"""
Скрипт для обновления существующих вопросов - привязываем их к доменам BIG
"""
import os
import sys
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import app
from models import db, Question, BIGDomain

def get_big_domain_id_by_code(domain_code):
    """Получить ID домена BIG по коду - ищет напрямую в БД"""
    # Сначала пробуем найти по точному коду
    domain = BIGDomain.query.filter_by(code=domain_code).first()
    if domain:
        return domain.id
    
    # Fallback: старые коды могут отличаться, пробуем маппинг
    legacy_mapping = {
        # Основные стоматологические домены
        'THER': 'THERAPEUTIC_DENTISTRY',
        'SURG': 'SURGICAL_DENTISTRY',
        'PROTH': 'PROSTHODONTICS',
        'PEDI': 'PEDIATRIC_DENTISTRY',
        'PARO': 'PERIODONTOLOGY',
        'ORTHO': 'ORTHODONTICS',
        'PREV': 'PREVENTIVE_DENTISTRY',
        
        # Базовые науки
        'ANATOMIE': 'ANATOMY',
        'FYSIOLOGIE': 'PHYSIOLOGY',
        'PATHOLOGIE': 'PATHOLOGY',
        'MICROBIOLOGIE': 'MICROBIOLOGY',
        'MATERIAALKUNDE': 'MATERIALS_SCIENCE',
        'RADIOLOGIE': 'RADIOLOGY',
        
        # Фармакология и медицина
        'FARMACOLOGIE': 'PHARMACOLOGY',
        'PHARMA': 'PHARMACOLOGY',
        'ALGEMENE_GENEESKUNDE': 'GENERAL_MEDICINE',
        'EMERGENCY': 'EMERGENCY_MEDICINE',
        
        # Системные заболевания и инфекции
        'SYSTEMIC': 'SYSTEMIC_DISEASES',
        'INFECTION': 'INFECTIOUS_DISEASES',
        'INFECTIOUS': 'INFECTIOUS_DISEASES',
        
        # Специальные случаи и диагностика
        'SPECIAL': 'SPECIAL_CASES',
        'DIAGNOSIS': 'DIAGNOSTICS',
        'DIAGNOSIS_SPECIAL': 'SPECIAL_DIAGNOSTICS',
        
        # Голландское законодательство и этика
        'DUTCH': 'DUTCH_DENTISTRY',
        'ETHIEK': 'ETHICS_NL',
        'PROFESSIONAL': 'PROFESSIONAL_ETHICS',
        'PROFESSIONAL_ETHIEK': 'PROFESSIONAL_ETHICS'
    }
    
    new_code = legacy_mapping.get(domain_code)
    if new_code:
        domain = BIGDomain.query.filter_by(code=new_code).first()
        return domain.id if domain else None
    
    return None

def update_questions_domains():
    """Обновляет существующие вопросы - привязывает их к доменам BIG"""
    
    with app.app_context():
        try:
            print("🔄 Обновляем привязку вопросов к доменам BIG...")
            
            # Проверяем наличие доменов
            domains_count = BIGDomain.query.count()
            if domains_count == 0:
                print("❌ Домены BIG не найдены! Сначала запустите: flask create-domains")
                sys.exit(1)
            
            print(f"✅ Найдено {domains_count} доменов BIG")
            
            # Получаем все вопросы без привязки к доменам
            questions = Question.query.filter_by(big_domain_id=None).all()
            total_questions = len(questions)
            
            if total_questions == 0:
                print("✅ Все вопросы уже привязаны к доменам!")
                return
            
            print(f"📊 Найдено {total_questions} вопросов без привязки к доменам")
            
            updated_count = 0
            skipped_count = 0
            
            for question in questions:
                if question.domain:  # Если есть текстовый код домена
                    big_domain_id = get_big_domain_id_by_code(question.domain)
                    if big_domain_id:
                        question.big_domain_id = big_domain_id
                        updated_count += 1
                        
                        if updated_count % 50 == 0:
                            print(f"   📝 Обновлено {updated_count}/{total_questions} вопросов...")
                    else:
                        print(f"   ⚠️ Домен не найден для кода: {question.domain}")
                        skipped_count += 1
                else:
                    print(f"   ⚠️ Вопрос {question.id} не имеет кода домена")
                    skipped_count += 1
            
            db.session.commit()
            print(f"\n✅ Успешно обновлено {updated_count} вопросов!")
            if skipped_count > 0:
                print(f"⚠️ Пропущено {skipped_count} вопросов (не удалось определить домен)")
            
            # Показать статистику по доменам
            print("\n📊 СТАТИСТИКА ПО ДОМЕНАМ:")
            for domain in BIGDomain.query.all():
                questions_count = Question.query.filter_by(big_domain_id=domain.id).count()
                print(f"   {domain.code} ({domain.name}): {questions_count} вопросов")
            
            # Показать количество вопросов без домена
            no_domain_count = Question.query.filter_by(big_domain_id=None).count()
            if no_domain_count > 0:
                print(f"\n⚠️ Вопросов без домена: {no_domain_count}")
            
        except Exception as e:
            print(f"❌ Ошибка обновления: {str(e)}")
            db.session.rollback()
            sys.exit(1)

if __name__ == "__main__":
    update_questions_domains()

