#!/usr/bin/env python3
"""
Тестовый скрипт для проверки аналитических эндпоинтов
"""

import requests
import json
from datetime import datetime

def test_endpoint(url, method='GET', data=None, headers=None):
    """Тестирует эндпоинт"""
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, json=data, headers=headers)
        
        print(f"🔍 {method} {url}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Success")
            try:
                result = response.json()
                print(f"   📊 Response keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
            except:
                print(f"   📄 Response length: {len(response.text)} chars")
        else:
            print(f"   ❌ Error: {response.text[:200]}")
        
        print()
        return response.status_code == 200
        
    except Exception as e:
        print(f"   💥 Exception: {str(e)}")
        print()
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 ТЕСТИРОВАНИЕ АНАЛИТИЧЕСКИХ ЭНДПОИНТОВ")
    print("=" * 50)
    
    # Базовый URL (замените на ваш)
    base_url = "http://localhost:5000"
    
    # Тестируем публичные эндпоинты трекинга
    print("📊 ПУБЛИЧНЫЕ ЭНДПОИНТЫ ТРЕКИНГА:")
    print("-" * 30)
    
    tracking_endpoints = [
        ("/track-registration-visit", "POST", {"page_type": "test", "timestamp": datetime.now().isoformat()}),
        ("/track-form-start", "POST", {"page_type": "test", "timestamp": datetime.now().isoformat()}),
        ("/track-form-submit", "POST", {"page_type": "test", "timestamp": datetime.now().isoformat()}),
        ("/track-page-exit", "POST", {"page_type": "test", "timestamp": datetime.now().isoformat()}),
        ("/track-email-entry", "POST", {"email": "test@example.com", "page_type": "test", "timestamp": datetime.now().isoformat()}),
        ("/track-name-entry", "POST", {"first_name": "Test", "last_name": "User", "page_type": "test", "timestamp": datetime.now().isoformat()})
    ]
    
    success_count = 0
    total_count = len(tracking_endpoints)
    
    for endpoint, method, data in tracking_endpoints:
        url = f"{base_url}{endpoint}"
        if test_endpoint(url, method, data):
            success_count += 1
    
    print(f"📈 РЕЗУЛЬТАТЫ ТРЕКИНГА: {success_count}/{total_count} успешно")
    print()
    
    # Тестируем админские эндпоинты (требуют авторизации)
    print("🔐 АДМИНСКИЕ ЭНДПОИНТЫ (требуют авторизации):")
    print("-" * 40)
    
    admin_endpoints = [
        "/admin/monitoring/dashboard",
        "/admin/registration-analytics",
        "/admin/dashboard"
    ]
    
    admin_success = 0
    for endpoint in admin_endpoints:
        url = f"{base_url}{endpoint}"
        if test_endpoint(url):
            admin_success += 1
    
    print(f"📈 РЕЗУЛЬТАТЫ АДМИНКИ: {admin_success}/{len(admin_endpoints)} доступны")
    print()
    
    # Общая статистика
    total_success = success_count + admin_success
    total_endpoints = total_count + len(admin_endpoints)
    
    print("🎯 ОБЩАЯ СТАТИСТИКА:")
    print(f"   ✅ Успешно: {total_success}/{total_endpoints}")
    print(f"   📊 Процент успеха: {(total_success/total_endpoints)*100:.1f}%")
    
    if total_success == total_endpoints:
        print("   🎉 ВСЕ ЭНДПОИНТЫ РАБОТАЮТ!")
    elif success_count == total_count:
        print("   ✅ Все трекинг эндпоинты работают")
        print("   ⚠️ Некоторые админские эндпоинты недоступны (требуют авторизации)")
    else:
        print("   ⚠️ Есть проблемы с некоторыми эндпоинтами")

if __name__ == "__main__":
    main()


