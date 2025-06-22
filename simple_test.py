#!/usr/bin/env python3
"""
Простой тест для проверки доступности универсального загрузчика
"""
import requests

BASE_URL = "http://localhost:8081"
UPLOADER_PAGE_URL = f"{BASE_URL}/en/admin/uploader/"

def test_uploader_page():
    """Тестирование доступности страницы загрузчика"""
    try:
        response = requests.get(UPLOADER_PAGE_URL)
        print(f"Status: {response.status_code}")
        print(f"URL: {response.url}")
        print(f"Headers: {dict(response.headers)}")
        
        # Проверяем, есть ли редирект на логин
        if "login" in response.url.lower():
            print("❌ Страница перенаправляет на логин - требуется авторизация")
        elif response.status_code == 200:
            print("✅ Страница загрузчика доступна")
            # Проверяем содержимое
            if "универсальный загрузчик" in response.text.lower() or "uploader" in response.text.lower():
                print("✅ Содержимое страницы корректно")
            else:
                print("⚠️ Содержимое страницы не содержит ожидаемых элементов")
        else:
            print(f"❌ Ошибка доступа: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Ошибка соединения: {e}")

if __name__ == "__main__":
    test_uploader_page() 