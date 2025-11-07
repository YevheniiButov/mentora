#!/usr/bin/env python3
"""
Скрипт для тестирования функциональности входа на mentora.com.in
"""
import requests
import json
import sys

def test_mentora_login():
    """Тестировать функциональность входа"""
    print("🧪 Тестирование входа на mentora.com.in...")
    
    # Тестовые данные
    test_credentials = [
        {
            "username": "mentora@bigmentor.nl",
            "password": "mentora2024!",
            "description": "Production test user"
        },
        {
            "username": "mentora_prod_test",
            "password": "mentora2024!",
            "description": "Production test user (username)"
        },
        {
            "username": "test@mentora.com",
            "password": "mentora123",
            "description": "Local test user"
        },
        {
            "username": "admin@mentora.com",
            "password": "admin123",
            "description": "Admin user"
        }
    ]
    
    base_url = "https://mentora.com.in"
    login_url = f"{base_url}/mentora-login"
    
    print(f"🌐 Тестируем URL: {login_url}")
    
    for creds in test_credentials:
        print(f"\n📝 Тестируем: {creds['description']}")
        print(f"   Username: {creds['username']}")
        
        try:
            # Отправить запрос на вход
            response = requests.post(
                login_url,
                json={
                    "username": creds["username"],
                    "password": creds["password"]
                },
                headers={
                    "Content-Type": "application/json",
                    "Host": "mentora.com.in"
                },
                timeout=10
            )
            
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    print(f"   ✅ Успешный вход!")
                    print(f"   Redirect URL: {data.get('redirect_url', 'N/A')}")
                else:
                    print(f"   ❌ Ошибка входа: {data.get('message', 'Unknown error')}")
            else:
                print(f"   ❌ HTTP Error: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error Message: {error_data.get('message', 'No message')}")
                except:
                    print(f"   Response: {response.text[:100]}...")
                    
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Connection Error: {e}")
    
    print("\n📋 Ручное тестирование:")
    print("1. Откройте https://mentora.com.in в браузере")
    print("2. Введите ваши учетные данные")
    print("3. Нажмите 'Come In'")
    print("4. Проверьте, что происходит перенаправление на dashboard")

def test_landing_page():
    """Тестировать загрузку лендинговой страницы"""
    print("\n🌐 Тестирование лендинговой страницы...")
    
    test_urls = [
        "https://mentora.com.in",
        "https://www.mentora.com.in",
        "http://mentora.com.in",
        "http://www.mentora.com.in"
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                if "Mentora - Come In to Excellence" in response.text:
                    print(f"✅ {url} - Лендинговая страница загружается")
                else:
                    print(f"⚠️  {url} - Страница загружается, но не содержит ожидаемый контент")
            else:
                print(f"❌ {url} - HTTP {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {url} - Ошибка подключения: {e}")

def main():
    """Основная функция"""
    print("🚀 Тестирование функциональности входа mentora.com.in")
    print("=" * 60)
    
    # Тестировать лендинговую страницу
    test_landing_page()
    
    # Тестировать функциональность входа
    test_mentora_login()
    
    print("\n" + "=" * 60)
    print("✅ Тестирование завершено!")
    print("\n📋 Следующие шаги:")
    print("1. Проверьте результаты тестирования выше")
    print("2. При необходимости обновите тестовые учетные данные")
    print("3. Протестируйте вручную в браузере")
    print("4. После успешного тестирования - задеплоить на продакшн")

if __name__ == "__main__":
    main()
