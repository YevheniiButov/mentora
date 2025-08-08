#!/usr/bin/env python3
"""
Скрипт для тестирования обновленного планировщика
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from models import User, PersonalLearningPlan, DiagnosticSession
from datetime import datetime, timezone
import json

def test_updated_planner():
    """Тестирует обновленный планировщик"""
    
    with app.app_context():
        print("🧪 ТЕСТИРОВАНИЕ ОБНОВЛЕННОГО ПЛАНИРОВЩИКА")
        print("=" * 60)
        
        # Проверяем пользователя Demo Gebruiker (ID: 6)
        user = User.query.get(6)
        if not user:
            print("❌ Пользователь Demo Gebruiker не найден")
            return
        
        print(f"👤 Пользователь: {user.get_display_name()} (ID: {user.id})")
        print("-" * 50)
        
        # Получаем активный план
        active_plan = PersonalLearningPlan.query.filter_by(
            user_id=user.id,
            status='active'
        ).first()
        
        if not active_plan:
            print("❌ Активный план не найден")
            return
        
        print(f"📋 Активный план: ID {active_plan.id}")
        
        # Проверяем данные плана
        print(f"\n📊 ДАННЫЕ ПЛАНА:")
        print("-" * 30)
        
        if active_plan.domain_analysis:
            try:
                domain_analysis = json.loads(active_plan.domain_analysis)
                print(f"✅ Domain analysis: {len(domain_analysis)} доменов")
                
                # Показываем первые 5 доменов
                for i, (domain_name, domain_data) in enumerate(domain_analysis.items()):
                    if i >= 5:
                        print(f"   ... и еще {len(domain_analysis) - 5} доменов")
                        break
                    print(f"   • {domain_name}: {domain_data.get('score', 0)}% ({domain_data.get('hours', 0)} ч)")
                
            except json.JSONDecodeError as e:
                print(f"❌ Ошибка парсинга domain_analysis: {e}")
        else:
            print("❌ Domain analysis пустой")
        
        if active_plan.weak_domains:
            try:
                weak_domains = json.loads(active_plan.weak_domains)
                print(f"⚠️ Weak domains: {len(weak_domains)} доменов")
                for domain in weak_domains[:5]:
                    print(f"   • {domain}")
                if len(weak_domains) > 5:
                    print(f"   ... и еще {len(weak_domains) - 5} доменов")
            except json.JSONDecodeError as e:
                print(f"❌ Ошибка парсинга weak_domains: {e}")
        else:
            print("❌ Weak domains пустой")
        
        if active_plan.study_schedule:
            try:
                study_schedule = json.loads(active_plan.study_schedule)
                print(f"📅 Study schedule: {study_schedule.get('total_weeks', 0)} недель")
                print(f"   • Total hours: {study_schedule.get('total_hours', 0)}")
                print(f"   • Weekly schedule: {len(study_schedule.get('weekly_schedule', []))} недель")
            except json.JSONDecodeError as e:
                print(f"❌ Ошибка парсинга study_schedule: {e}")
        else:
            print("❌ Study schedule пустой")
        
        print(f"\n📈 СТАТИСТИКА ПЛАНА:")
        print("-" * 30)
        print(f"📊 Общий прогресс: {active_plan.overall_progress:.1f}%")
        print(f"🎯 Текущая готовность: {active_plan.current_ability:.2f}")
        print(f"📈 Оценка готовности: {active_plan.estimated_readiness:.1%}")
        print(f"📅 Дата экзамена: {active_plan.exam_date}")
        
        # Симулируем логику планировщика
        print(f"\n🔄 СИМУЛЯЦИЯ ОБНОВЛЕННОГО ПЛАНИРОВЩИКА:")
        print("-" * 40)
        
        diagnostic_results = {
            'overall_score': active_plan.current_ability,
            'domains': []
        }
        
        if active_plan.domain_analysis:
            try:
                domain_analysis = json.loads(active_plan.domain_analysis)
                
                for domain_name, domain_data in domain_analysis.items():
                    domain_result = {
                        'code': domain_data.get('domain_code', 'unknown'),
                        'name': domain_name,
                        'score': domain_data.get('score', 0),
                        'target': domain_data.get('target', 85),
                        'hours': domain_data.get('hours', 24.0),
                        'questions_answered': domain_data.get('questions_answered', 0),
                        'correct_answers': domain_data.get('correct_answers', 0)
                    }
                    diagnostic_results['domains'].append(domain_result)
                
                print(f"✅ Используем данные из плана: {len(diagnostic_results['domains'])} доменов")
                
                # Показываем статистику
                total_hours = sum(d['hours'] for d in diagnostic_results['domains'])
                weak_domains = [d for d in diagnostic_results['domains'] if d['score'] < 70]
                strong_domains = [d for d in diagnostic_results['domains'] if d['score'] >= 70]
                
                print(f"⏰ Общее время обучения: {total_hours:.1f} часов")
                print(f"⚠️ Слабых доменов: {len(weak_domains)}")
                print(f"✅ Сильных доменов: {len(strong_domains)}")
                
                if weak_domains:
                    print(f"\n⚠️ СЛАБЫЕ ДОМЕНЫ (показываются в планировщике):")
                    for domain in weak_domains[:5]:
                        print(f"   • {domain['name']}: {domain['score']}% ({domain['hours']:.1f} ч)")
                    if len(weak_domains) > 5:
                        print(f"   ... и еще {len(weak_domains) - 5} доменов")
                
            except json.JSONDecodeError as e:
                print(f"❌ Ошибка парсинга: {e}")
        else:
            print("❌ Нет данных в плане")
        
        print(f"\n✅ ТЕСТ ЗАВЕРШЕН!")
        print("Теперь планировщик должен показывать обновленные данные из плана.")

if __name__ == "__main__":
    test_updated_planner() 