#!/usr/bin/env python3
"""
Тест для проверки роутинга доменов
"""
import requests
import sys

def test_domain_routing():
    """Тестировать роутинг доменов"""
    print("🧪 Тестирование роутинга доменов...")
    
    # Тестовые URL
    test_urls = [
        {
            "url": "https://bigmentor.nl",
            "expected": "обычная главная страница",
            "should_contain": "bigmentor"
        },
        {
            "url": "https://mentora.com.in", 
            "expected": "космическая лендинговая страница",
            "should_contain": "Mentora - Come In to Excellence"
        }
    ]
    
    for test in test_urls:
        print(f"\n🌐 Тестируем: {test['url']}")
        print(f"   Ожидается: {test['expected']}")
        
        try:
            response = requests.get(test['url'], timeout=10)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                if test['should_contain'] in response.text:
                    print(f"   ✅ {test['expected']} загружается корректно")
                else:
                    print(f"   ⚠️  Страница загружается, но не содержит ожидаемый контент")
                    print(f"   Найденный контент: {response.text[:100]}...")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Ошибка подключения: {e}")

def test_login_endpoint():
    """Тестировать endpoint входа"""
    print("\n🔐 Тестирование endpoint входа...")
    
    # Тест с правильным доменом
    print("\n📝 Тест с mentora.com.in:")
    try:
        response = requests.post(
            "https://mentora.com.in/mentora-login",
            json={"username": "test", "password": "test"},
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Test)"
            },
            timeout=10
        )
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
        
        if response.status_code == 401:  # Ожидаем 401 (неверные учетные данные)
            print("   ✅ Endpoint работает (401 - неверные учетные данные)")
        elif response.status_code == 400:
            print("   ✅ Endpoint работает (400 - неверные данные)")
        else:
            print(f"   ⚠️  Неожиданный статус: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Ошибка подключения: {e}")
    
    # Тест с неправильным доменом
    print("\n📝 Тест с bigmentor.nl (должен быть 403):")
    try:
        response = requests.post(
            "https://bigmentor.nl/mentora-login",
            json={"username": "test", "password": "test"},
            headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (Test)"
            },
            timeout=10
        )
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text[:200]}...")
        
        if response.status_code == 403:
            print("   ✅ Защита домена работает (403 - неавторизованный домен)")
        else:
            print(f"   ⚠️  Неожиданный статус: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Ошибка подключения: {e}")

def main():
    """Основная функция"""
    print("🚀 Тестирование роутинга доменов для mentora-nl сервиса")
    print("=" * 60)
    
    test_domain_routing()
    test_login_endpoint()
    
    print("\n" + "=" * 60)
    print("✅ Тестирование завершено!")
    print("\n📋 Что проверить:")
    print("1. bigmentor.nl - должна показывать обычную главную страницу")
    print("2. mentora.com.in - должна показывать космическую лендинговую страницу")
    print("3. /mentora-login работает только с mentora.com.in")
    print("4. После деплоя на Render оба домена должны работать корректно")

if __name__ == "__main__":
    main()
