#!/usr/bin/env python3
"""
Скрипт для отладки проблемы с рекомендациями
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import PreAssessmentAttempt

def debug_recommendations():
    """Отладка рекомендаций"""
    app = create_app()
    with app.app_context():
        # Находим попытку
        attempt = PreAssessmentAttempt.query.filter_by(id=2).first()
        if not attempt:
            print("Попытка не найдена")
            return
        
        print(f"Попытка ID: {attempt.id}")
        print(f"Пользователь: {attempt.user_id}")
        print(f"Завершена: {attempt.is_completed}")
        
        # Получаем анализ
        from routes.assessment_routes import analyze_assessment_results
        analysis = analyze_assessment_results(attempt)
        
        print("\n=== АНАЛИЗ ===")
        print(f"overall_level: {analysis['overall_level']}")
        print(f"strengths: {analysis['strengths']}")
        print(f"weaknesses: {analysis['weaknesses']}")
        
        print("\n=== РЕКОМЕНДАЦИИ ===")
        for i, rec in enumerate(analysis['recommendations']):
            print(f"Рекомендация {i+1}:")
            print(f"  title: {rec['title']} (тип: {type(rec['title'])})")
            print(f"  description: {rec['description']} (тип: {type(rec['description'])})")
            print(f"  gradient: {rec['gradient']}")
            print(f"  icon: {rec['icon']}")
            print(f"  duration: {rec['duration']}")
            print(f"  difficulty: {rec['difficulty']}")
            print()

if __name__ == "__main__":
    debug_recommendations()
