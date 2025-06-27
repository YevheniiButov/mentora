#!/usr/bin/env python3
"""
Скрипт для отладки данных, передаваемых в шаблон results
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import PreAssessmentAttempt

def debug_results_data():
    """Отладка данных результатов"""
    app = create_app()
    with app.app_context():
        # Находим попытку
        attempt = PreAssessmentAttempt.query.filter_by(id=2).first()
        if not attempt:
            print("Попытка не найдена")
            return
        
        print(f"Попытка ID: {attempt.id}")
        
        # Получаем анализ результатов
        analysis = attempt.get_recommended_plan()
        category_scores = attempt.get_category_scores()
        
        # Форматируем данные для отображения (как в функции results)
        from routes.assessment_routes import format_time_spent, format_category_results, analyze_assessment_results
        
        results_data = {
            'overall_score': attempt.total_score,
            'correct_answers': attempt.correct_answers,
            'total_questions': attempt.total_questions,
            'time_spent': format_time_spent(attempt.time_spent),
            'completion_time': format_time_spent(attempt.time_spent),
            'accuracy': round((attempt.correct_answers / attempt.total_questions) * 100, 1),
            'completion_date': attempt.completed_at,
            'category_results': format_category_results(category_scores),
            'categories': format_category_results(category_scores),
            'skill_level': analysis.get('overall_level', 'intermediate'),
            'skill_description': analysis.get('skill_description', 'Средний уровень подготовки'),
            'strengths': analysis.get('strengths', []),
            'weaknesses': analysis.get('weaknesses', []),
            'recommendations': analysis.get('recommendations', [])[:5],
            'study_time_estimate': analysis.get('study_time_estimate', {}),
            'learning_plan_preview': analysis.get('learning_plan', {})
        }
        
        print("\n=== ДАННЫЕ ДЛЯ ШАБЛОНА ===")
        print(f"overall_score: {results_data['overall_score']}")
        print(f"correct_answers: {results_data['correct_answers']}")
        print(f"total_questions: {results_data['total_questions']}")
        print(f"accuracy: {results_data['accuracy']}")
        print(f"skill_level: {results_data['skill_level']}")
        print(f"strengths: {results_data['strengths']}")
        print(f"weaknesses: {results_data['weaknesses']}")
        
        print("\n=== РЕКОМЕНДАЦИИ В RESULTS_DATA ===")
        for i, rec in enumerate(results_data['recommendations']):
            print(f"Рекомендация {i+1}:")
            if isinstance(rec, dict):
                print(f"  title: {rec.get('title', 'N/A')} (тип: {type(rec.get('title', 'N/A'))})")
                print(f"  description: {rec.get('description', 'N/A')} (тип: {type(rec.get('description', 'N/A'))})")
            else:
                print(f"  rec: {rec} (тип: {type(rec)})")
            print()

if __name__ == "__main__":
    debug_results_data()
