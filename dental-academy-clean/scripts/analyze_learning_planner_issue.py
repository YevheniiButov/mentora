#!/usr/bin/env python3
"""
Скрипт для анализа проблемы с планировщиком обучения
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from models import User, PersonalLearningPlan, DiagnosticSession
from utils.daily_learning_algorithm import DailyLearningAlgorithm
from datetime import datetime, timezone
import json

def analyze_learning_planner_issue():
    """Анализирует проблему с планировщиком обучения"""
    
    with app.app_context():
        print("🔍 АНАЛИЗ ПРОБЛЕМЫ С ПЛАНИРОВЩИКОМ ОБУЧЕНИЯ")
        print("=" * 70)
        
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
        print(f"   📅 Дата экзамена: {active_plan.exam_date}")
        print(f"   🎯 Целевая готовность: {active_plan.target_ability}")
        print(f"   📊 Текущая готовность: {active_plan.current_ability}")
        print(f"   📈 Общий прогресс: {active_plan.overall_progress:.1f}%")
        print(f"   ⏰ Часов в неделю: {active_plan.study_hours_per_week}")
        
        # Анализируем domain_analysis
        print(f"\n🔍 АНАЛИЗ DOMAIN_ANALYSIS:")
        print("-" * 30)
        
        if active_plan.domain_analysis:
            try:
                domain_data = json.loads(active_plan.domain_analysis)
                print(f"   📄 Domain analysis (JSON): {domain_data}")
                
                if isinstance(domain_data, dict):
                    for domain, data in domain_data.items():
                        print(f"   • {domain}: {data}")
                elif isinstance(domain_data, list):
                    for item in domain_data:
                        print(f"   • {item}")
                        
            except json.JSONDecodeError as e:
                print(f"   ❌ Ошибка парсинга JSON: {e}")
                print(f"   📄 Сырые данные: {active_plan.domain_analysis}")
        else:
            print("   ❌ Domain analysis пустой")
        
        # Анализируем weak_domains
        print(f"\n⚠️ АНАЛИЗ WEAK_DOMAINS:")
        print("-" * 30)
        
        if active_plan.weak_domains:
            try:
                weak_domains = json.loads(active_plan.weak_domains)
                print(f"   📄 Weak domains (JSON): {weak_domains}")
                
                if isinstance(weak_domains, list):
                    for domain in weak_domains:
                        print(f"   • {domain}")
                        
            except json.JSONDecodeError as e:
                print(f"   ❌ Ошибка парсинга JSON: {e}")
                print(f"   📄 Сырые данные: {active_plan.weak_domains}")
        else:
            print("   ❌ Weak domains пустой")
        
        # Анализируем study_schedule
        print(f"\n📅 АНАЛИЗ STUDY_SCHEDULE:")
        print("-" * 30)
        
        if active_plan.study_schedule:
            try:
                study_schedule = json.loads(active_plan.study_schedule)
                print(f"   📄 Study schedule (JSON): {study_schedule}")
                
                if isinstance(study_schedule, dict):
                    for key, value in study_schedule.items():
                        print(f"   • {key}: {value}")
                elif isinstance(study_schedule, list):
                    for item in study_schedule:
                        print(f"   • {item}")
                        
            except json.JSONDecodeError as e:
                print(f"   ❌ Ошибка парсинга JSON: {e}")
                print(f"   📄 Сырые данные: {active_plan.study_schedule}")
        else:
            print("   ❌ Study schedule пустой")
        
        # Получаем последнюю диагностику
        latest_diagnostic = DiagnosticSession.query.filter_by(
            user_id=user.id,
            status='completed'
        ).order_by(DiagnosticSession.completed_at.desc()).first()
        
        if latest_diagnostic:
            print(f"\n🔬 ПОСЛЕДНЯЯ ДИАГНОСТИКА:")
            print("-" * 30)
            print(f"   📅 Дата: {latest_diagnostic.completed_at.strftime('%Y-%m-%d %H:%M')}")
            print(f"   📊 Вопросов отвечено: {latest_diagnostic.questions_answered}")
            print(f"   ✅ Правильных ответов: {latest_diagnostic.correct_answers}")
            print(f"   📈 Точность: {(latest_diagnostic.correct_answers/latest_diagnostic.questions_answered*100):.1f}%")
            
            # Анализируем session_data
            if latest_diagnostic.session_data:
                try:
                    session_data = json.loads(latest_diagnostic.session_data)
                    print(f"   📄 Session data: {session_data}")
                except json.JSONDecodeError as e:
                    print(f"   ❌ Ошибка парсинга session_data: {e}")
        
        # Генерируем ежедневный план для сравнения
        print(f"\n📅 ЕЖЕДНЕВНЫЙ ПЛАН (для сравнения):")
        print("-" * 40)
        
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
                
                # Практика
                practice_section = daily_plan['practice_section']
                print(f"\n✏️ ПРАКТИКА ({practice_section['estimated_time']} мин):")
                if practice_section['content']:
                    for item in practice_section['content']:
                        print(f"   • {item['title']} ({item['estimated_time']} мин, {item['difficulty']})")
                
                # Повторение
                review_section = daily_plan['review_section']
                print(f"\n🔄 ПОВТОРЕНИЕ ({review_section['estimated_time']} мин):")
                if review_section['content']:
                    for item in review_section['content']:
                        print(f"   • {item['title']} ({item['estimated_time']} мин)")
                
                print(f"\n⏱️ ОБЩЕЕ ВРЕМЯ: {daily_plan_result['total_estimated_time']} минут")
                
                # Слабые домены
                if daily_plan_result['weak_domains']:
                    print(f"\n⚠️ СЛАБЫЕ ДОМЕНЫ (из ежедневного плана):")
                    for domain in daily_plan_result['weak_domains']:
                        print(f"   • {domain}")
                
            else:
                print("❌ Ошибка генерации ежедневного плана")
                
        except Exception as e:
            print(f"❌ Ошибка при генерации ежедневного плана: {e}")
        
        print(f"\n🔍 ВЫВОДЫ:")
        print("-" * 20)
        print("1. Планировщик обучения показывает только один домен (Эндодонтия)")
        print("2. Ежедневный план генерирует разнообразный контент")
        print("3. Проблема в том, что планировщик и ежедневный план не связаны")
        print("4. Нужно синхронизировать данные между системами")

if __name__ == "__main__":
    analyze_learning_planner_issue() 