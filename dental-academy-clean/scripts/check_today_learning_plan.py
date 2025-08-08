#!/usr/bin/env python3
"""
Скрипт для проверки ежедневного плана обучения на сегодня
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from models import User, PersonalLearningPlan, DiagnosticSession
from utils.daily_learning_algorithm import DailyLearningAlgorithm
from datetime import datetime, timezone

def check_today_learning_plan():
    """Проверяет ежедневный план обучения на сегодня"""
    
    with app.app_context():
        print("📚 ПРОВЕРКА ЕЖЕДНЕВНОГО ПЛАНА ОБУЧЕНИЯ НА СЕГОДНЯ")
        print("=" * 70)
        
        # Получаем всех пользователей с активными планами
        users_with_plans = db.session.query(User).join(
            PersonalLearningPlan, 
            User.id == PersonalLearningPlan.user_id
        ).filter(
            PersonalLearningPlan.status == 'active'
        ).all()
        
        if not users_with_plans:
            print("❌ Нет пользователей с активными планами обучения")
            return
        
        print(f"👥 Найдено пользователей с активными планами: {len(users_with_plans)}")
        print()
        
        # Проверяем план для каждого пользователя
        for user in users_with_plans:
            print(f"🔍 Пользователь: {user.get_display_name()} (ID: {user.id})")
            print("-" * 50)
            
            # Получаем активный план
            active_plan = PersonalLearningPlan.query.filter_by(
                user_id=user.id,
                status='active'
            ).first()
            
            if active_plan:
                print(f"📋 Активный план: ID {active_plan.id}")
                print(f"   📅 Дата экзамена: {active_plan.exam_date}")
                print(f"   🎯 Целевая готовность: {active_plan.target_ability}")
                print(f"   📊 Текущая готовность: {active_plan.current_ability}")
                print(f"   📈 Общий прогресс: {active_plan.overall_progress:.1f}%")
                print(f"   ⏰ Часов в неделю: {active_plan.study_hours_per_week}")
                
                # Получаем последнюю диагностику
                latest_diagnostic = DiagnosticSession.query.filter_by(
                    user_id=user.id,
                    status='completed'
                ).order_by(DiagnosticSession.completed_at.desc()).first()
                
                if latest_diagnostic:
                    print(f"🔬 Последняя диагностика: {latest_diagnostic.completed_at.strftime('%Y-%m-%d %H:%M')}")
                    print(f"   📊 Вопросов отвечено: {latest_diagnostic.questions_answered}")
                    print(f"   ✅ Правильных ответов: {latest_diagnostic.correct_answers}")
                    print(f"   📈 Точность: {(latest_diagnostic.correct_answers/latest_diagnostic.questions_answered*100):.1f}%")
            
            # Генерируем ежедневный план
            print("\n📅 ЕЖЕДНЕВНЫЙ ПЛАН НА СЕГОДНЯ:")
            print("-" * 30)
            
            try:
                algorithm = DailyLearningAlgorithm()
                daily_plan_result = algorithm.generate_daily_plan(
                    user_id=user.id,
                    target_minutes=30
                )
                
                if daily_plan_result['success']:
                    daily_plan = daily_plan_result['daily_plan']
                    
                    # Теория
                    theory_section = daily_plan['theory_section']
                    print(f"📖 ТЕОРИЯ ({theory_section['estimated_time']} мин):")
                    if theory_section['content']:
                        for item in theory_section['content']:
                            print(f"   • {item['title']} ({item['estimated_time']} мин, {item['difficulty']})")
                    else:
                        print("   • Нет запланированных уроков теории")
                    
                    # Практика
                    practice_section = daily_plan['practice_section']
                    print(f"\n✏️ ПРАКТИКА ({practice_section['estimated_time']} мин):")
                    if practice_section['content']:
                        for item in practice_section['content']:
                            print(f"   • {item['title']} ({item['estimated_time']} мин, {item['difficulty']})")
                    else:
                        print("   • Нет запланированных практических заданий")
                    
                    # Повторение
                    review_section = daily_plan['review_section']
                    print(f"\n🔄 ПОВТОРЕНИЕ ({review_section['estimated_time']} мин):")
                    if review_section['content']:
                        for item in review_section['content']:
                            print(f"   • {item['title']} ({item['estimated_time']} мин)")
                    else:
                        print("   • Нет запланированных повторений")
                    
                    print(f"\n⏱️ ОБЩЕЕ ВРЕМЯ: {daily_plan_result['total_estimated_time']} минут")
                    
                    # Слабые домены
                    if daily_plan_result['weak_domains']:
                        print(f"\n⚠️ СЛАБЫЕ ДОМЕНЫ:")
                        for domain in daily_plan_result['weak_domains']:
                            print(f"   • {domain}")
                    
                else:
                    print("❌ Ошибка генерации плана")
                    
            except Exception as e:
                print(f"❌ Ошибка при генерации плана: {e}")
            
            print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    check_today_learning_plan() 