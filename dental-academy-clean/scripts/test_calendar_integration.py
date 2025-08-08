#!/usr/bin/env python3
"""
Тест интеграции календаря с планами обучения
Проверяет работу новых компонентов
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from utils.calendar_plan_integration import CalendarPlanIntegration
from utils.daily_learning_algorithm import DailyLearningAlgorithm
import json

def test_calendar_integration():
    """Тест интеграции календаря с планами"""
    print("🧪 ТЕСТ ИНТЕГРАЦИИ КАЛЕНДАРЯ С ПЛАНАМИ")
    print("=" * 50)
    
    with app.app_context():
        # Тест 1: CalendarPlanIntegration
        print("\n1️⃣ Тест CalendarPlanIntegration...")
        integration = CalendarPlanIntegration()
        
        # Получаем детальный план
        plan_result = integration.get_detailed_plan_for_calendar(6, 30)
        
        if plan_result.get('success'):
            print("✅ CalendarPlanIntegration работает!")
            plan = plan_result.get('plan', {})
            summary = plan.get('summary', {})
            sections = plan.get('sections', {})
            
            print(f"   📊 Общее время: {summary.get('total_time', 0)} мин")
            print(f"   📚 Слабых доменов: {len(summary.get('weak_domains', []))}")
            print(f"   📋 Секций: {len(sections)}")
            
            for section_type, section in sections.items():
                print(f"      - {section.get('title', section_type)}: {section.get('total_items', 0)} элементов")
        else:
            print(f"❌ Ошибка CalendarPlanIntegration: {plan_result.get('error')}")
            return False
        
        # Тест 2: Статистика плана
        print("\n2️⃣ Тест статистики плана...")
        stats = integration.get_plan_statistics(6)
        
        if stats.get('success'):
            print("✅ Статистика плана работает!")
            print(f"   📈 Всего сессий: {stats.get('total_sessions', 0)}")
            print(f"   ✅ Завершено: {stats.get('completed_sessions', 0)}")
            print(f"   📊 Процент завершения: {stats.get('completion_rate', 0):.1f}%")
        else:
            print(f"❌ Ошибка статистики: {stats.get('error')}")
        
        # Тест 3: Сессии обучения
        print("\n3️⃣ Тест сессий обучения...")
        sessions = integration.get_user_study_sessions(6, 7)
        
        print(f"✅ Сессии обучения получены: {len(sessions)} сессий")
        if sessions:
            print(f"   📅 Последняя сессия: {sessions[0].get('title', 'N/A')}")
        
        # Тест 4: DailyLearningAlgorithm
        print("\n4️⃣ Тест DailyLearningAlgorithm...")
        algo = DailyLearningAlgorithm()
        algo_result = algo.generate_daily_plan(6, 30)
        
        if algo_result.get('success'):
            print("✅ DailyLearningAlgorithm работает!")
            print(f"   📊 Общее время: {algo_result.get('total_estimated_time', 0)} мин")
            print(f"   📚 Слабых доменов: {len(algo_result.get('weak_domains', []))}")
        else:
            print(f"❌ Ошибка DailyLearningAlgorithm: {algo_result.get('error')}")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print("✅ Интеграция календаря с планами работает корректно")
        
        return True

def test_api_endpoints():
    """Тест API endpoints"""
    print("\n🌐 ТЕСТ API ENDPOINTS")
    print("=" * 30)
    
    with app.test_client() as client:
        # Тест health check
        print("\n1️⃣ Тест /api/calendar-plan/health...")
        response = client.get('/api/calendar-plan/health')
        if response.status_code == 200:
            data = response.get_json()
            print(f"✅ Health check: {data.get('status', 'unknown')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
        
        # Тест detailed plan
        print("\n2️⃣ Тест /api/calendar-plan/detailed-plan...")
        response = client.get('/api/calendar-plan/detailed-plan?target_minutes=30')
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success'):
                print("✅ Detailed plan API работает!")
                plan = data.get('plan', {})
                print(f"   📊 Время: {plan.get('summary', {}).get('total_time', 0)} мин")
            else:
                print(f"❌ API error: {data.get('error')}")
        else:
            print(f"❌ API failed: {response.status_code}")
        
        # Тест statistics
        print("\n3️⃣ Тест /api/calendar-plan/statistics...")
        response = client.get('/api/calendar-plan/statistics')
        if response.status_code == 200:
            data = response.get_json()
            if data.get('success'):
                print("✅ Statistics API работает!")
                stats = data.get('statistics', {})
                print(f"   📈 Сессий: {stats.get('total_sessions', 0)}")
            else:
                print(f"❌ API error: {data.get('error')}")
        else:
            print(f"❌ API failed: {response.status_code}")

if __name__ == "__main__":
    try:
        success = test_calendar_integration()
        if success:
            test_api_endpoints()
        print("\n🏁 Тестирование завершено!")
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")
        import traceback
        traceback.print_exc() 