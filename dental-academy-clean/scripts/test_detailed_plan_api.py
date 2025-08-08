#!/usr/bin/env python3
"""
Тест API детального плана
"""

import requests
import json

def test_detailed_plan_api():
    """Тест API детального плана"""
    print("🧪 ТЕСТ API ДЕТАЛЬНОГО ПЛАНА")
    print("=" * 30)
    
    try:
        # Тест 1: Health check
        print("\n1️⃣ Тест health check...")
        response = requests.get("http://127.0.0.1:5000/api/calendar-plan/health", timeout=10)
        print(f"   Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Результат: {data.get('status', 'unknown')}")
        else:
            print(f"   Ошибка: {response.text}")
        
        # Тест 2: Detailed plan
        print("\n2️⃣ Тест detailed plan...")
        response = requests.get("http://127.0.0.1:5000/api/calendar-plan/detailed-plan?target_minutes=30", timeout=10)
        print(f"   Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                plan = data.get('plan', {})
                summary = plan.get('summary', {})
                sections = plan.get('sections', {})
                
                print(f"   ✅ План получен успешно!")
                print(f"   📊 Общее время: {summary.get('total_time', 0)} мин")
                print(f"   📚 Слабых доменов: {len(summary.get('weak_domains', []))}")
                print(f"   📋 Секций: {len(sections)}")
                
                for section_type, section in sections.items():
                    print(f"      - {section.get('title', section_type)}: {section.get('total_items', 0)} элементов")
            else:
                print(f"   ❌ Ошибка: {data.get('error')}")
        else:
            print(f"   ❌ Ошибка HTTP: {response.text}")
        
        # Тест 3: Statistics
        print("\n3️⃣ Тест statistics...")
        response = requests.get("http://127.0.0.1:5000/api/calendar-plan/statistics", timeout=10)
        print(f"   Статус: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                stats = data.get('statistics', {})
                print(f"   ✅ Статистика получена!")
                print(f"   📈 Сессий: {stats.get('total_sessions', 0)}")
                print(f"   ✅ Завершено: {stats.get('completed_sessions', 0)}")
                print(f"   📊 Процент: {stats.get('completion_rate', 0):.1f}%")
            else:
                print(f"   ❌ Ошибка: {data.get('error')}")
        else:
            print(f"   ❌ Ошибка HTTP: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Не удалось подключиться к серверу")
        print("   Убедитесь, что Flask сервер запущен на порту 5000")
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")

if __name__ == "__main__":
    test_detailed_plan_api() 