#!/usr/bin/env python3
"""
Скрипт для замены старых вопросов Dutch assessment на новые
"""
import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from extensions import db
from models import AssessmentCategory, AssessmentQuestion, PreAssessmentAnswer
from data.dutch_assessment_questions import DUTCH_DENTAL_QUESTIONS

def replace_dutch_questions():
    """Замена старых вопросов Dutch assessment на новые"""
    app = create_app()
    with app.app_context():
        print("🔄 Замена вопросов Dutch assessment...")
        
        # Получаем нидерландские категории
        dutch_categories = AssessmentCategory.query.filter_by(is_dutch_specific=True).all()
        category_map = {cat.slug: cat for cat in dutch_categories}
        
        # Удаляем старые вопросы из нидерландских категорий
        for category in dutch_categories:
            old_questions = AssessmentQuestion.query.filter_by(category_id=category.id).all()
            
            # Сначала удаляем связанные ответы
            for question in old_questions:
                PreAssessmentAnswer.query.filter_by(question_id=question.id).delete()
                db.session.delete(question)
                
            print(f"🗑️ Удалено {len(old_questions)} старых вопросов из категории {category.name}")
        
        # Коммитим удаление
        db.session.commit()
        
        # Добавляем новые вопросы
        question_count = 0
        for question_data in DUTCH_DENTAL_QUESTIONS:
            category_slug = question_data['category']
            if category_slug not in category_map:
                print(f"❌ Категория не найдена: {category_slug}")
                continue
                
            category = category_map[category_slug]
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
        print(f"✅ Добавлено {question_count} новых вопросов")
        print("🎉 Замена завершена!")

if __name__ == '__main__':
    replace_dutch_questions() 