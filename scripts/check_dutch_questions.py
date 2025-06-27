#!/usr/bin/env python3
"""
Скрипт для проверки вопросов Dutch assessment в базе данных
"""
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import AssessmentCategory, AssessmentQuestion

def check_dutch_questions():
    """Проверка вопросов Dutch assessment в базе данных"""
    app = create_app()
    with app.app_context():
        print("🔍 Проверка вопросов Dutch assessment в базе данных...")
        
        # Проверяем категории
        dutch_categories = AssessmentCategory.query.filter_by(is_dutch_specific=True).all()
        print(f"📂 Найдено {len(dutch_categories)} нидерландских категорий:")
        
        for category in dutch_categories:
            print(f"  - {category.name} (slug: {category.slug})")
            
            # Проверяем вопросы для каждой категории
            questions = AssessmentQuestion.query.filter_by(
                category_id=category.id,
                is_active=True
            ).all()
            
            print(f"    📝 Вопросов в категории: {len(questions)}")
            
            if questions:
                print("    Примеры вопросов:")
                for i, question in enumerate(questions[:3]):  # Показываем первые 3
                    print(f"      {i+1}. Текст: {question.question_text[:100]}...")
                    try:
                        options = json.loads(question.options)
                        print(f"         Варианты: {options[:2]}...")  # Первые 2 варианта
                    except:
                        print(f"         Варианты: ОШИБКА ПАРСИНГА JSON")
                    print(f"         Правильный ответ: {question.correct_answer}")
            else:
                print("    ❌ Вопросов нет!")
            print()

if __name__ == '__main__':
    check_dutch_questions() 