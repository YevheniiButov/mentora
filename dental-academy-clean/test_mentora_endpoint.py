#!/usr/bin/env python3
"""
Тест для проверки endpoint mentora-login
"""
import requests
import json

def test_mentora_endpoint():
    """Тестировать endpoint mentora-login"""
    print("🔐 Тестирование endpoint mentora-login")
    print("=" * 50)
    
    # Тест 1: Правильный домен с правильными заголовками
    print("\n📝 Тест 1: mentora.com.in с правильными заголовками")
    try:
        response = requests.post(
            "https://mentora.com.in/mentora-login",
            json={"username": "test", "password": "test"},
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (Test)"
            },
            timeout=10
        )
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'Not set')}")
        print(f"   Response (first 200 chars): {response.text[:200]}...")
        
        if response.status_code == 400:
            print("   ✅ Endpoint работает (400 - неверные данные)")
        elif response.status_code == 401:
            print("   ✅ Endpoint работает (401 - неверные учетные данные)")
        elif response.status_code == 200 and 'application/json' in response.headers.get('Content-Type', ''):
            print("   ✅ Endpoint работает (200 - JSON ответ)")
        else:
            print(f"   ⚠️  Неожиданный ответ")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Ошибка подключения: {e}")
    
    # Тест 2: Неправильный домен
    print("\n📝 Тест 2: bigmentor.nl (должен быть 403)")
    try:
        response = requests.post(
            "https://bigmentor.nl/mentora-login",
            json={"username": "test", "password": "test"},
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "Mozilla/5.0 (Test)"
            },
            timeout=10
        )
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'Not set')}")
        print(f"   Response (first 200 chars): {response.text[:200]}...")
        
        if response.status_code == 403:
            print("   ✅ Защита домена работает (403 - неавторизованный домен)")
        else:
            print(f"   ⚠️  Неожиданный статус: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Ошибка подключения: {e}")
    
    # Тест 3: GET запрос (должен быть 405)
    print("\n📝 Тест 3: GET запрос (должен быть 405)")
    try:
        response = requests.get(
            "https://mentora.com.in/mentora-login",
            timeout=10
        )
        print(f"   Status Code: {response.status_code}")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'Not set')}")
        
        if response.status_code == 405:
            print("   ✅ Метод не разрешен (405 - только POST)")
        else:
            print(f"   ⚠️  Неожиданный статус: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Ошибка подключения: {e}")

def main():
    """Основная функция"""
    print("🚀 Тестирование endpoint mentora-login")
    print("=" * 60)
    
    test_mentora_endpoint()
    
    print("\n" + "=" * 60)
    print("✅ Тестирование завершено!")
    print("\n📋 Ожидаемые результаты:")
    print("1. mentora.com.in POST → 400/401 (неверные данные)")
    print("2. bigmentor.nl POST → 403 (неавторизованный домен)")
    print("3. mentora.com.in GET → 405 (метод не разрешен)")

if __name__ == "__main__":
    main()


