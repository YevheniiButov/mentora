#!/usr/bin/env python3
"""
Тест функции выбора вопросов для Quick Test
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import User, Question, BIGDomain
from diagnostic_config.diagnostic_domains import get_quick_test_config
from routes.diagnostic_routes import select_questions_for_quick_test
from collections import Counter

def test_tandarts():
    """Тест для стоматологов"""
    print("🦷 ТЕСТ ДЛЯ СТОМАТОЛОГОВ")
    print("=" * 40)
    
    # Создаем мок-пользователя
    class MockUser:
        profession = 'Tandarts'
    
    user = MockUser()
    
    try:
        # Получаем конфигурацию
        config = get_quick_test_config('tandarts')
        print(f"📋 Конфигурация: {config['filter_type']} с {len(config['areas'])} областями")
        
        # Выбираем вопросы
        questions = select_questions_for_quick_test(user)
        print(f"📊 Выбрано вопросов: {len(questions)}")
        print(f"🎯 Цель: 31 вопрос для стоматологов")
        
        if questions:
            # Проверяем распределение по доменам
            domains = Counter([q.big_domain.name if q.big_domain else 'None' for q in questions])
            
            print(f"\n📋 Распределение по доменам:")
            for domain, count in domains.most_common():
                print(f"  {domain}: {count} вопросов")
        else:
            print("❌ Вопросы не найдены!")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

def test_huisarts():
    """Тест для врачей"""
    print("\n🩺 ТЕСТ ДЛЯ ВРАЧЕЙ")
    print("=" * 40)
    
    # Создаем мок-пользователя
    class MockUser:
        profession = 'Huisarts'
    
    user = MockUser()
    
    try:
        # Получаем конфигурацию
        config = get_quick_test_config('huisarts')
        print(f"📋 Конфигурация: {config['filter_type']} с {len(config['areas'])} областями")
        
        # Выбираем вопросы
        questions = select_questions_for_quick_test(user)
        print(f"📊 Выбрано вопросов: {len(questions)}")
        print(f"🎯 Цель: 30 вопросов для врачей")
        
        if questions:
            # Проверяем распределение по категориям
            categories = Counter([q.category for q in questions])
            
            print(f"\n📋 Распределение по категориям:")
            for category, count in categories.most_common(10):
                print(f"  {category}: {count} вопросов")
        else:
            print("❌ Вопросы не найдены!")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Основная функция тестирования"""
    print("🧪 ТЕСТИРОВАНИЕ QUICK TEST")
    print("=" * 50)
    
    # Используем существующее приложение
    with app.app_context():
        # Тест для стоматологов
        test_tandarts()
        
        # Тест для врачей
        test_huisarts()
        
        print("\n✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")

if __name__ == "__main__":
    main()
