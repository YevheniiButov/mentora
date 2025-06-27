#!/usr/bin/env python3
"""
Скрипт инициализации вопросов предварительной оценки знаний в стоматологии
Загружает категории и вопросы в базу данных
"""
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from models import AssessmentCategory, AssessmentQuestion
from data.dental_assessment_questions import ASSESSMENT_QUESTIONS, create_assessment_categories

def init_dental_categories():
    """Инициализация категорий предварительной оценки"""
    app = create_app()
    with app.app_context():
        print("📚 Инициализация категорий предварительной оценки...")
        categories = create_assessment_categories()
        category_map = {}
        
        for category_data in categories:
            existing = AssessmentCategory.query.filter_by(slug=category_data['slug']).first()
            if not existing:
                category = AssessmentCategory(
                    name=category_data['name'],
                    slug=category_data['slug'],
                    description=category_data['description'],
                    weight=category_data['weight'],
                    min_questions=category_data['min_questions'],
                    max_questions=category_data['max_questions'],
                    color=category_data['color'],
                    icon=category_data['icon'],
                    is_dutch_specific=False  # Это не нидерландские вопросы
                )
                db.session.add(category)
                db.session.flush()  # Получаем ID
                print(f"✅ Добавлена категория: {category_data['name']}")
                category_map[category_data['slug']] = category.id
            else:
                print(f"⚠️ Категория уже существует: {category_data['name']}")
                category_map[category_data['slug']] = existing.id
        
        db.session.commit()
        print("✅ Категории инициализированы")
        return category_map

def init_dental_questions():
    """Инициализация вопросов предварительной оценки"""
    app = create_app()
    with app.app_context():
        print("📝 Инициализация вопросов предварительной оценки...")
        
        # Сначала создаем категории
        category_map = init_dental_categories()
        
        question_count = 0
        for question_data in ASSESSMENT_QUESTIONS:
            category_slug = question_data['category']
            if category_slug not in category_map:
                print(f"❌ Категория не найдена: {category_slug}")
                continue
                
            category_id = category_map[category_slug]
            
            # Проверяем, не существует ли уже такой вопрос
            existing_question = AssessmentQuestion.query.filter_by(
                category_id=category_id,
                question_text=question_data['question']
            ).first()
            
            if not existing_question:
                question = AssessmentQuestion(
                    category_id=category_id,
                    question_text=question_data['question'],
                    question_type='multiple_choice',
                    options=json.dumps(question_data['options'], ensure_ascii=False),
                    correct_answer=question_data['correct_answer'],
                    explanation=question_data.get('explanation', ''),
                    difficulty_level=question_data.get('difficulty', 3),
                    time_limit=question_data.get('time_limit', 120),
                    points=question_data.get('points', 1),
                    related_modules=json.dumps(question_data.get('related_modules', [])),
                    is_active=True
                )
                db.session.add(question)
                question_count += 1
            else:
                print(f"⚠️ Вопрос уже существует: {question_data['question'][:50]}...")
        
        db.session.commit()
        print(f"✅ Добавлено {question_count} новых вопросов")

def check_dental_questions():
    """Проверка вопросов предварительной оценки в базе данных"""
    app = create_app()
    with app.app_context():
        print("🔍 Проверка вопросов предварительной оценки в базе данных...")
        
        # Проверяем категории
        categories = AssessmentCategory.query.filter(
            AssessmentCategory.slug.in_(['knowledge_center', 'communication', 'preclinical_skills', 'clinical_cases', 'exam_preparation'])
        ).all()
        
        print(f"📂 Найдено {len(categories)} категорий предварительной оценки:")
        for category in categories:
            question_count = AssessmentQuestion.query.filter_by(category_id=category.id).count()
            print(f"  - {category.name}: {question_count} вопросов")
        
        # Общая статистика
        total_questions = AssessmentQuestion.query.join(AssessmentCategory).filter(
            AssessmentCategory.slug.in_(['knowledge_center', 'communication', 'preclinical_skills', 'clinical_cases', 'exam_preparation'])
        ).count()
        
        print(f"📊 Всего вопросов предварительной оценки: {total_questions}")

def main():
    """Основная функция"""
    print("🦷 Инициализация системы предварительной оценки знаний в стоматологии")
    print("=" * 70)
    
    try:
        # Инициализируем категории и вопросы
        init_dental_questions()
        
        # Проверяем результат
        check_dental_questions()
        
        print("\n🎉 Инициализация завершена успешно!")
        
    except Exception as e:
        print(f"❌ Ошибка при инициализации: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 