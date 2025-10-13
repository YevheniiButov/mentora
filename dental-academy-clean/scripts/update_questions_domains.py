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
    """Получить ID домена BIG по коду"""
    domain_mapping = {
        'THER': 'Therapeutische stomatologie',
        'SURG': 'Chirurgische stomatologie', 
        'PROTH': 'Prothetische stomatologie',
        'PEDI': 'Pediatrische stomatologie',
        'PARO': 'Parodontologie',
        'ORTHO': 'Orthodontie',
        'PREV': 'Preventie',
        'ETHIEK': 'Ethiek en recht',
        'ANATOMIE': 'Anatomie',
        'FYSIOLOGIE': 'Fysiologie',
        'PATHOLOGIE': 'Pathologie',
        'MICROBIOLOGIE': 'Microbiologie',
        'MATERIAALKUNDE': 'Materiaalkunde',
        'RADIOLOGIE': 'Radiologie',
        'ALGEMENE_GENEESKUNDE': 'Algemene geneeskunde'
    }
    
    domain_name = domain_mapping.get(domain_code)
    if domain_name:
        domain = BIGDomain.query.filter_by(name=domain_name).first()
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

