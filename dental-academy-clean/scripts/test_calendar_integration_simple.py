#!/usr/bin/env python3
"""
Простой тест интеграции календаря с планами
"""

from app import app
from utils.calendar_plan_integration import CalendarPlanIntegration
import json

def test_simple_integration():
    """Простой тест интеграции"""
    print("🧪 ПРОСТОЙ ТЕСТ ИНТЕГРАЦИИ КАЛЕНДАРЯ С ПЛАНАМИ")
    print("=" * 50)
    
    with app.app_context():
        # Тест 1: Получение детального плана
        print("\n1️⃣ Тест получения детального плана...")
        integration = CalendarPlanIntegration()
        plan_result = integration.get_detailed_plan_for_calendar(6, 30)
        
        if plan_result.get('success'):
            plan = plan_result.get('plan', {})
            sections = plan.get('sections', {})
            
            print("✅ Детальный план получен!")
            print(f"   📊 Общее время: {plan.get('summary', {}).get('total_time', 0)} мин")
            print(f"   📋 Секций: {len(sections)}")
            
            # Показываем содержимое каждой секции
            for section_type, section in sections.items():
                items = section.get('items', [])
                print(f"   📚 {section.get('title', section_type)}: {len(items)} элементов")
                
                # Показываем первые 3 элемента каждой секции
                for i, item in enumerate(items[:3]):
                    print(f"      {i+1}. {item.get('title', 'Без названия')} ({item.get('estimated_time', 0)} мин)")
                
                if len(items) > 3:
                    print(f"      ... и еще {len(items) - 3} элементов")
            
            print("\n🎯 РЕЗУЛЬТАТ: План готов для интеграции в календарь!")
            print("   Каждый элемент будет отображаться как событие в календаре")
            print("   Пользователь сможет кликнуть на событие и увидеть детали")
            
        else:
            print(f"❌ Ошибка получения плана: {plan_result.get('error')}")

if __name__ == "__main__":
    test_simple_integration() 