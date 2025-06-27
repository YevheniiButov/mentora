#!/usr/bin/env python3
"""
Скрипт инициализации нидерландской системы оценки
Загружает категории и вопросы в базу данных
"""
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from models import AssessmentCategory, AssessmentQuestion
from data.dutch_assessment_categories import DUTCH_ASSESSMENT_CATEGORIES
from data.dutch_assessment_questions import DUTCH_DENTAL_QUESTIONS

def init_dutch_categories():
    """Инициализация нидерландских категорий"""
    app = create_app()
    with app.app_context():
        print("🇳🇱 Инициализация нидерландских категорий оценки...")
        for category_data in DUTCH_ASSESSMENT_CATEGORIES:
            existing = AssessmentCategory.query.filter_by(slug=category_data['slug']).first()
            if not existing:
                category = AssessmentCategory(
                    name=category_data['name'],
                    name_en=category_data.get('name_en'),
                    name_ru=category_data.get('name_ru'),
                    slug=category_data['slug'],
                    description=category_data['description'],
                    weight=category_data['weight'],
                    min_questions=category_data['min_questions'],
                    max_questions=category_data['max_questions'],
                    color=category_data['color'],
                    icon=category_data['icon'],
                    is_dutch_specific=category_data.get('is_dutch_specific', False),
                    critical_for_netherlands=category_data.get('critical_for_netherlands', False)
                )
                db.session.add(category)
                print(f"✅ Добавлена категория: {category_data['name']}")
            else:
                print(f"⚠️ Категория уже существует: {category_data['name']}")
        db.session.commit()
        print("✅ Категории инициализированы")

def init_dutch_questions():
    """Инициализация нидерландских вопросов"""
    app = create_app()
    with app.app_context():
        print("📝 Инициализация нидерландских вопросов...")
        categories = {cat.slug: cat for cat in AssessmentCategory.query.all()}
        question_count = 0
        for question_data in DUTCH_DENTAL_QUESTIONS:
            category_slug = question_data['category']
            if category_slug not in categories:
                print(f"❌ Категория не найдена: {category_slug}")
                continue
            category = categories[category_slug]
            existing_question = AssessmentQuestion.query.filter_by(
                category_id=category.id,
                question_text=question_data['question']
            ).first()
            if not existing_question:
                question = AssessmentQuestion(
                    category_id=category.id,
                    question_text=question_data['question'],
                    question_type=question_data.get('question_type', 'multiple_choice'),
                    options=json.dumps(question_data['options']),
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
        db.session.commit()
        print(f"✅ Добавлено {question_count} вопросов")

if __name__ == '__main__':
    print("🚀 Запуск инициализации нидерландской системы оценки...")
    init_dutch_categories()
    init_dutch_questions()
    print("🎉 Инициализация завершена!") 