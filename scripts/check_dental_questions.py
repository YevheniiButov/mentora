#!/usr/bin/env python3
"""
Скрипт для проверки вопросов предварительной оценки в системе
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import AssessmentCategory, AssessmentQuestion

def check_dental_questions():
    """Проверка вопросов предварительной оценки в системе"""
    app = create_app()
    with app.app_context():
        print("🔍 Проверка вопросов предварительной оценки в системе...")
        
        # Проверяем категории
        categories = AssessmentCategory.query.filter_by(is_dutch_specific=False).all()
        
        print(f"📂 Найдено {len(categories)} категорий предварительной оценки:")
        for category in categories:
            question_count = AssessmentQuestion.query.filter_by(category_id=category.id).count()
            print(f"  - {category.name} ({category.slug}): {question_count} вопросов")
            print(f"    Описание: {category.description}")
            print(f"    Цвет: {category.color}, Иконка: {category.icon}")
            print(f"    Вес: {category.weight}, Вопросов: {category.min_questions}-{category.max_questions}")
            print()
        
        # Общая статистика
        total_questions = AssessmentQuestion.query.join(AssessmentCategory).filter(
            AssessmentCategory.is_dutch_specific == False
        ).count()
        
        print(f"📊 Всего вопросов предварительной оценки: {total_questions}")
        
        # Проверяем несколько примеров вопросов
        print("\n📝 Примеры вопросов:")
        for category in categories[:2]:  # Показываем первые 2 категории
            questions = AssessmentQuestion.query.filter_by(category_id=category.id).limit(2).all()
            print(f"\n{category.name}:")
            for i, question in enumerate(questions, 1):
                print(f"  {i}. {question.question_text[:80]}...")
                print(f"     Сложность: {question.difficulty_level}, Время: {question.time_limit}с")
                print(f"     Опции: {len(question.get_options())} вариантов")

if __name__ == "__main__":
    check_dental_questions() 