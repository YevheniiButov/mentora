#!/usr/bin/env python3
"""
Тестовый скрипт для проверки эндпоинтов трекинга
"""

import requests
import json
from datetime import datetime

def test_tracking_endpoints():
    """Тестирует эндпоинты трекинга"""
    base_url = "http://localhost:5000"
    
    print("🧪 ТЕСТИРОВАНИЕ ЭНДПОИНТОВ ТРЕКИНГА")
    print("=" * 50)
    
    # Тестируем эндпоинт track-form-start
    print("1. Тестируем /track-form-start")
    try:
        response = requests.post(f"{base_url}/track-form-start", 
                               json={
                                   "page_type": "quick_register",
                                   "timestamp": datetime.now().isoformat()
                               },
                               timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Успешно")
        else:
            print(f"   ❌ Ошибка: {response.text}")
    except Exception as e:
        print(f"   💥 Исключение: {str(e)}")
    
    print()
    
    # Тестируем эндпоинт track-email-entry
    print("2. Тестируем /track-email-entry")
    try:
        response = requests.post(f"{base_url}/track-email-entry", 
                               json={
                                   "email": "test@example.com",
                                   "page_type": "quick_register",
                                   "timestamp": datetime.now().isoformat()
                               },
                               timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Успешно")
        else:
            print(f"   ❌ Ошибка: {response.text}")
    except Exception as e:
        print(f"   💥 Исключение: {str(e)}")
    
    print()
    
    # Тестируем эндпоинт track-name-entry
    print("3. Тестируем /track-name-entry")
    try:
        response = requests.post(f"{base_url}/track-name-entry", 
                               json={
                                   "first_name": "Тест",
                                   "last_name": "Пользователь",
                                   "page_type": "quick_register",
                                   "timestamp": datetime.now().isoformat()
                               },
                               timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Успешно")
        else:
            print(f"   ❌ Ошибка: {response.text}")
    except Exception as e:
        print(f"   💥 Исключение: {str(e)}")
    
    print()
    
    # Тестируем эндпоинт track-registration-visit
    print("4. Тестируем /track-registration-visit")
    try:
        response = requests.post(f"{base_url}/track-registration-visit", 
                               json={
                                   "page_type": "quick_register",
                                   "timestamp": datetime.now().isoformat()
                               },
                               timeout=5)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Успешно")
        else:
            print(f"   ❌ Ошибка: {response.text}")
    except Exception as e:
        print(f"   💥 Исключение: {str(e)}")
    
    print()
    print("🎯 РЕЗУЛЬТАТ:")
    print("Если все эндпоинты возвращают 200 - трекинг работает")
    print("Если есть ошибки - нужно проверить сервер")

if __name__ == "__main__":
    test_tracking_endpoints()
