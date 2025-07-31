#!/usr/bin/env python3
"""
Скрипт для загрузки 80 вопросов с IRT параметрами
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Question, QuestionCategory, IRTParameters, BIGDomain
from datetime import datetime, timezone
import json

def create_categories():
    """Создает категории вопросов"""
    
    with app.app_context():
        categories = [
            "Терапевтическая стоматология",
            "Хирургическая стоматология", 
            "Ортопедическая стоматология",
            "Ортодонтия",
            "Детская стоматология",
            "Этика и право",
            "Диагностика",
            "Неотложная помощь",
            "Фармакология",
            "Анатомия и физиология"
        ]
        
        created_categories = {}
        
        for cat_name in categories:
            # Проверяем, существует ли уже категория
            existing = QuestionCategory.query.filter_by(name=cat_name).first()
            if existing:
                created_categories[cat_name] = existing.id
                print(f"✅ Категория уже существует: {cat_name} (ID: {existing.id})")
            else:
                category = QuestionCategory(name=cat_name)
                db.session.add(category)
                db.session.flush()
                created_categories[cat_name] = category.id
                print(f"✅ Создана категория: {cat_name} (ID: {category.id})")
        
        db.session.commit()
        return created_categories

def get_domain_mapping():
    """Получает маппинг доменов BIG"""
    
    with app.app_context():
        domains = BIGDomain.query.all()
        domain_mapping = {}
        
        for domain in domains:
            domain_mapping[domain.code] = domain.id
            domain_mapping[domain.name] = domain.id
            # Добавляем варианты написания
            domain_mapping[domain.code.upper()] = domain.id
            domain_mapping[domain.code.lower()] = domain.id
        
        print("📋 Доступные домены:")
        for domain in domains:
            print(f"   {domain.code} -> {domain.name} (ID: {domain.id})")
        
        return domain_mapping

def create_question_with_irt(question_data, categories, domains):
    """Создает вопрос с IRT параметрами"""
    
    with app.app_context():
        # Определяем категорию по домену или типу вопроса
        category_name = question_data.get('category', 'Диагностика')
        category_id = categories.get(category_name, categories.get('Диагностика', 1))
        
        # Определяем домен
        domain_code = question_data.get('domain', 'THER')
        domain_id = domains.get(domain_code, domains.get('THER', 1))
        
        # Создаем вопрос
        question = Question(
            text=question_data['text'],
            options=json.dumps(question_data['options']),
            correct_answer=question_data['correct_answer'],
            explanation=question_data['explanation'],
            category_id=category_id,
            big_domain_id=domain_id,
            difficulty_level=question_data.get('difficulty_level', 3),
            question_type=question_data.get('question_type', 'multiple_choice'),
            clinical_context=question_data.get('clinical_context', '')
        )
        
        db.session.add(question)
        db.session.flush()
        
        # Создаем IRT параметры
        irt_params = question_data['irt_params']
        irt = IRTParameters(
            question_id=question.id,
            difficulty=irt_params['difficulty'],
            discrimination=irt_params['discrimination'],
            guessing=irt_params['guessing']
        )
        
        db.session.add(irt)
        db.session.commit()
        
        return question.id

def load_sample_questions():
    """Загружает примеры вопросов (замените на ваши 80 вопросов)"""
    
    print("\n📝 ЗАГРУЗКА ВОПРОСОВ")
    print("=" * 40)
    
    with app.app_context():
        categories = create_categories()
        domains = get_domain_mapping()
        
        # Пример структуры вопроса (замените на ваши данные)
        sample_questions = [
            {
                "text": "Этические дилеммы - Автономия vs. благодеяние. 70-летний пациент с множественными сопутствующими заболеваниями отказывается от рекомендованной экстракции инфицированного зуба. Понимает риски сепсиса, но 'не хочет терять больше зубов'. Семья настаивает на лечении. Пациент психически компетентен, но эмоционально расстроен из-за потери зубов. Как должно быть разрешено это этическое противоречие между автономией пациента и медицинским благодеянием?",
                "options": [
                    "Уважать автономию пациента - соблюдать отказ от лечения",
                    "Отменить автономию из-за серьезного медицинского риска", 
                    "Согласие семьи может заменить отказ пациента",
                    "Психиатрическая оценка для оценки компетентности",
                    "Компромиссное лечение с менее инвазивным подходом"
                ],
                "correct_answer": "Уважать автономию пациента - соблюдать отказ от лечения",
                "explanation": "Принцип медицинской этики автономии требует уважения решений компетентного пациента, даже когда они медикаментозно нецелесообразны. Пациент понимает последствия и принимает информированное решение.",
                "category": "Этика и право",
                "domain": "ETHIEK",
                "difficulty_level": 4,
                "question_type": "clinical_case",
                "clinical_context": "Этическая дилемма с автономией пациента",
                "irt_params": {
                    "difficulty": 0.8,
                    "discrimination": 1.9,
                    "guessing": 0.17
                }
            }
        ]
        
        created_count = 0
        
        for i, q_data in enumerate(sample_questions, 1):
            try:
                question_id = create_question_with_irt(q_data, categories, domains)
                print(f"✅ Вопрос {i} создан (ID: {question_id})")
                created_count += 1
            except Exception as e:
                print(f"❌ Ошибка при создании вопроса {i}: {e}")
        
        print(f"\n✅ Создано вопросов: {created_count}")
        return created_count

def main():
    """Основная функция"""
    
    print("🚀 ЗАГРУЗКА 80 ВОПРОСОВ С IRT ПАРАМЕТРАМИ")
    print("=" * 50)
    
    try:
        # Загружаем вопросы
        count = load_sample_questions()
        
        print(f"\n🎉 ЗАГРУЗКА ЗАВЕРШЕНА!")
        print("=" * 50)
        print(f"✅ Загружено вопросов: {count}")
        print("📝 Для загрузки всех 80 вопросов:")
        print("   1. Откройте файл scripts/load_80_questions.py")
        print("   2. Замените sample_questions на ваши 80 вопросов")
        print("   3. Запустите скрипт снова")
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")

if __name__ == '__main__':
    main() 