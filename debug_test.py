#!/usr/bin/env python3
"""
Простой тест для отладки планировщика
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, DiagnosticSession, PersonalLearningPlan
from utils.learning_plan_generator import convert_diagnostic_to_planner_format

def debug_test():
    """Простой тест для отладки"""
    
    with app.app_context():
        print("🔍 ОТЛАДКА: Начинаем тест...")
        
        # Находим любого пользователя
        user = User.query.first()
        if not user:
            print("❌ Пользователи не найдены")
            return
        
        print(f"✅ Найден пользователь: {user.email} (ID: {user.id})")
        
        # Находим диагностическую сессию
        diagnostic_session = DiagnosticSession.query.filter_by(
            user_id=user.id,
            status='completed'
        ).first()
        
        if not diagnostic_session:
            print("❌ Диагностическая сессия не найдена")
            return
        
        print(f"✅ Найдена диагностическая сессия: {diagnostic_session.id}")
        
        # Тестируем generate_results
        print("\n🔍 ОТЛАДКА: Тестируем generate_results()...")
        diagnostic_data = diagnostic_session.generate_results()
        print(f"🔍 ОТЛАДКА: diagnostic_data keys = {list(diagnostic_data.keys())}")
        print(f"🔍 ОТЛАДКА: domain_statistics = {diagnostic_data.get('domain_statistics', {})}")
        
        # Тестируем конвертер
        print("\n🔍 ОТЛАДКА: Тестируем конвертер...")
        converted = convert_diagnostic_to_planner_format(diagnostic_data)
        print(f"🔍 ОТЛАДКА: converted = {converted}")
        
        # Проверяем план обучения
        print("\n🔍 ОТЛАДКА: Проверяем план обучения...")
        learning_plan = PersonalLearningPlan.query.filter_by(
            user_id=user.id,
            status='active'
        ).first()
        
        if learning_plan:
            print(f"✅ Найден план обучения: {learning_plan.id}")
            print(f"🔍 ОТЛАДКА: plan.domain_analysis = {learning_plan.domain_analysis}")
            domain_analysis = learning_plan.get_domain_analysis()
            print(f"🔍 ОТЛАДКА: plan.get_domain_analysis() = {domain_analysis}")
        else:
            print("❌ План обучения не найден")

if __name__ == '__main__':
    debug_test() 