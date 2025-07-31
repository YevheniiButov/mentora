#!/usr/bin/env python3
"""
Скрипт для очистки старых вопросов и загрузки новых с IRT параметрами
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import Question, QuestionCategory, IRTParameters, BIGDomain
from datetime import datetime, timezone
import json

def clear_all_questions():
    """Очищает все вопросы из базы данных"""
    
    print("🗑️ ОЧИСТКА ВСЕХ ВОПРОСОВ")
    print("=" * 40)
    
    with app.app_context():
        try:
            # Удаляем IRT параметры
            irt_count = IRTParameters.query.delete()
            print(f"✅ Удалено IRT параметров: {irt_count}")
            
            # Удаляем вопросы
            questions_count = Question.query.delete()
            print(f"✅ Удалено вопросов: {questions_count}")
            
            # Удаляем категории вопросов
            categories_count = QuestionCategory.query.delete()
            print(f"✅ Удалено категорий: {categories_count}")
            
            # Сохраняем изменения
            db.session.commit()
            print("✅ База данных очищена успешно")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Ошибка при очистке: {e}")
            raise

def create_categories():
    """Создает базовые категории вопросов"""
    
    print("\n📂 СОЗДАНИЕ КАТЕГОРИЙ")
    print("=" * 40)
    
    with app.app_context():
        categories = [
            "Терапевтическая стоматология",
            "Хирургическая стоматология", 
            "Ортопедическая стоматология",
            "Ортодонтия",
            "Детская стоматология",
            "Этика и право",
            "Диагностика",
            "Неотложная помощь"
        ]
        
        created_categories = {}
        
        for cat_name in categories:
            category = QuestionCategory(name=cat_name)
            db.session.add(category)
            db.session.flush()  # Получаем ID
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
        
        return domain_mapping

def create_sample_questions_with_irt():
    """Создает примеры вопросов с IRT параметрами"""
    
    print("\n📝 СОЗДАНИЕ ВОПРОСОВ С IRT ПАРАМЕТРАМИ")
    print("=" * 40)
    
    with app.app_context():
        # Получаем категории
        categories = {cat.name: cat.id for cat in QuestionCategory.query.all()}
        
        # Получаем домены
        domains = get_domain_mapping()
        
        # Примеры вопросов с IRT параметрами
        questions_data = [
            {
                "text": "Этические дилеммы - Автономия vs. благодеяние. 70-летний пациент с множественными сопутствующими заболеваниями отказывается от рекомендованной экстракции инфицированного зуба. Понимает риски сепсиса, но 'не хочет терять больше зубов'. Семья настаивает на лечении. Пациент психически компетентен, но эмоционально расстроен из-за потери зубов. Как должно быть разрешено это этическое противоречие между автономией пациента и медицинским благодеянием?",
                "options": json.dumps([
                    "Уважать автономию пациента - соблюдать отказ от лечения",
                    "Отменить автономию из-за серьезного медицинского риска", 
                    "Согласие семьи может заменить отказ пациента",
                    "Психиатрическая оценка для оценки компетентности",
                    "Компромиссное лечение с менее инвазивным подходом"
                ]),
                "correct_answer": "Уважать автономию пациента - соблюдать отказ от лечения",
                "explanation": "Принцип медицинской этики автономии требует уважения решений компетентного пациента, даже когда они медикаментозно нецелесообразны. Пациент понимает последствия и принимает информированное решение.",
                "category_id": categories.get("Этика и право", 1),
                "big_domain_id": domains.get("ETHIEK", domains.get("Этика", 1)),
                "difficulty_level": 4,
                "question_type": "clinical_case",
                "clinical_context": "Этическая дилемма с автономией пациента",
                "irt_params": {
                    "difficulty": 0.8,
                    "discrimination": 1.9,
                    "guessing": 0.17
                }
            },
            {
                "text": "Диагностика кариеса. У пациента 25 лет обнаружено темное пятно на жевательной поверхности первого моляра. При зондировании поверхность твердая, безболезненная. Какой диагноз наиболее вероятен?",
                "options": json.dumps([
                    "Поверхностный кариес (caries superficialis)",
                    "Средний кариес (caries media)",
                    "Глубокий кариес (caries profunda)",
                    "Пигментированный фиссурный кариес",
                    "Здоровый зуб с пигментацией"
                ]),
                "correct_answer": "Пигментированный фиссурный кариес",
                "explanation": "Темное пятно с твердой поверхностью при зондировании характерно для пигментированного фиссурного кариеса. Отсутствие боли и твердость поверхности указывают на стабилизированный процесс.",
                "category_id": categories.get("Диагностика", 1),
                "big_domain_id": domains.get("THER", domains.get("Терапевтическая стоматология", 1)),
                "difficulty_level": 3,
                "question_type": "diagnostic",
                "clinical_context": "Диагностика кариеса",
                "irt_params": {
                    "difficulty": 0.3,
                    "discrimination": 1.2,
                    "guessing": 0.2
                }
            },
            {
                "text": "Неотложная помощь. Пациент 35 лет обратился с жалобами на сильную боль в области верхнего правого клыка, усиливающуюся при накусывании. Боль иррадиирует в висок. При осмотре: зуб интактный, перкуссия болезненная, слизистая в проекции корня отечна. Какой диагноз наиболее вероятен?",
                "options": json.dumps([
                    "Острый пульпит",
                    "Острый периодонтит",
                    "Острый периостит",
                    "Невралгия тройничного нерва",
                    "Синусит"
                ]),
                "correct_answer": "Острый периодонтит",
                "explanation": "Клиническая картина характерна для острого периодонтита: боль при накусывании, болезненная перкуссия, отек слизистой в проекции корня.",
                "category_id": categories.get("Неотложная помощь", 1),
                "big_domain_id": domains.get("THER", domains.get("Терапевтическая стоматология", 1)),
                "difficulty_level": 4,
                "question_type": "emergency",
                "clinical_context": "Неотложная стоматологическая помощь",
                "irt_params": {
                    "difficulty": 0.6,
                    "discrimination": 1.5,
                    "guessing": 0.2
                }
            }
        ]
        
        created_questions = []
        
        for q_data in questions_data:
            # Создаем вопрос
            question = Question(
                text=q_data["text"],
                options=q_data["options"],
                correct_answer=q_data["correct_answer"],
                explanation=q_data["explanation"],
                category_id=q_data["category_id"],
                big_domain_id=q_data["big_domain_id"],
                difficulty_level=q_data["difficulty_level"],
                question_type=q_data["question_type"],
                clinical_context=q_data["clinical_context"]
            )
            
            db.session.add(question)
            db.session.flush()  # Получаем ID вопроса
            
            # Создаем IRT параметры
            irt_params = q_data["irt_params"]
            irt = IRTParameters(
                question_id=question.id,
                difficulty=irt_params["difficulty"],
                discrimination=irt_params["discrimination"],
                guessing=irt_params["guessing"]
            )
            
            db.session.add(irt)
            created_questions.append(question.id)
            
            print(f"✅ Создан вопрос ID {question.id}: {q_data['text'][:50]}...")
            print(f"   IRT: difficulty={irt_params['difficulty']}, discrimination={irt_params['discrimination']}, guessing={irt_params['guessing']}")
        
        db.session.commit()
        print(f"\n✅ Создано вопросов: {len(created_questions)}")
        return created_questions

def main():
    """Основная функция"""
    
    print("🚀 ЗАГРУЗКА НОВЫХ ВОПРОСОВ С IRT ПАРАМЕТРАМИ")
    print("=" * 50)
    
    # Подтверждение
    response = input("⚠️ Это удалит ВСЕ существующие вопросы. Продолжить? (да/нет): ")
    if response.lower() != 'да':
        print("❌ Операция отменена")
        return
    
    try:
        # 1. Очищаем все вопросы
        clear_all_questions()
        
        # 2. Создаем категории
        create_categories()
        
        # 3. Создаем вопросы с IRT параметрами
        create_sample_questions_with_irt()
        
        print("\n🎉 ЗАГРУЗКА ЗАВЕРШЕНА УСПЕШНО!")
        print("=" * 50)
        print("✅ Все старые вопросы удалены")
        print("✅ Созданы новые категории")
        print("✅ Загружены вопросы с IRT параметрами")
        print("✅ Готово к использованию!")
        
    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        print("Попробуйте запустить скрипт снова")

if __name__ == '__main__':
    main() 