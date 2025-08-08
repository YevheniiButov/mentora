#!/usr/bin/env python3
"""
Простой тест API для проверки интеграции IRT + Spaced Repetition
"""

import requests
import json

def test_api_endpoints():
    """Тестирует API endpoints интеграции"""
    base_url = "http://127.0.0.1:5001"
    
    print("=== Тестирование API интеграции IRT + Spaced Repetition ===\n")
    
    # Тест 1: Получение статистики
    print("1. Тестирование получения статистики:")
    try:
        response = requests.get(f"{base_url}/irt-spaced/statistics")
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Статистика получена успешно")
            print(f"      - Всего элементов: {data.get('review_statistics', {}).get('total_items', 0)}")
            print(f"      - Готовых к повторению: {data.get('review_statistics', {}).get('due_items', 0)}")
            print(f"      - Просроченных: {data.get('review_statistics', {}).get('overdue_items', 0)}")
        else:
            print(f"   ❌ Ошибка получения статистики: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка запроса: {e}")
    print()
    
    # Тест 2: Получение расписания повторений
    print("2. Тестирование получения расписания повторений:")
    try:
        response = requests.get(f"{base_url}/irt-spaced/review-schedule?max_items=5")
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Расписание получено успешно")
            print(f"      - Количество элементов: {data.get('total_count', 0)}")
            if data.get('review_items'):
                print("      - Первые элементы:")
                for i, item in enumerate(data['review_items'][:3]):
                    print(f"        {i+1}. Вопрос {item['id']} (приоритет: {item.get('priority_score', 0):.2f})")
        else:
            print(f"   ❌ Ошибка получения расписания: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка запроса: {e}")
    print()
    
    # Тест 3: Получение пользовательских инсайтов
    print("3. Тестирование получения пользовательских инсайтов:")
    try:
        response = requests.get(f"{base_url}/irt-spaced/user-insights")
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Инсайты получены успешно")
            insights = data.get('insights', {})
            print(f"      - Сильнейший домен: {insights.get('strongest_domain', 'Нет данных')}")
            print(f"      - Слабейший домен: {insights.get('weakest_domain', 'Нет данных')}")
            print(f"      - Общая способность: {insights.get('overall_ability', 0):.3f}")
        else:
            print(f"   ❌ Ошибка получения инсайтов: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка запроса: {e}")
    print()
    
    # Тест 4: Получение адаптивного плана
    print("4. Тестирование получения адаптивного плана:")
    try:
        response = requests.get(f"{base_url}/irt-spaced/adaptive-plan?target_minutes=30")
        if response.status_code == 200:
            data = response.json()
            print("   ✅ Адаптивный план получен успешно")
            print(f"      - Целевое время: {data.get('target_minutes', 0)} минут")
            print(f"      - Элементы для повторения: {len(data.get('review_items', []))}")
            print(f"      - Новый контент: {len(data.get('new_content', []))}")
            
            # Показываем IRT инсайты
            irt_insights = data.get('irt_insights', {})
            if irt_insights:
                print(f"      - Сильнейший домен: {irt_insights.get('strongest_domain', 'Нет данных')}")
                print(f"      - Слабейший домен: {irt_insights.get('weakest_domain', 'Нет данных')}")
                print(f"      - Общая способность: {irt_insights.get('overall_ability', 0):.3f}")
        else:
            print(f"   ❌ Ошибка получения плана: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Ошибка запроса: {e}")
    print()
    
    print("=== Тестирование API завершено ===")

if __name__ == "__main__":
    test_api_endpoints() 