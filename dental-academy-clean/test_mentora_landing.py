#!/usr/bin/env python3
"""
Скрипт для тестирования лендинговой страницы mentora.com.in
"""
import requests
import sys

def test_mentora_landing():
    """Тестировать лендинговую страницу"""
    test_urls = [
        "http://mentora.com.in",
        "http://www.mentora.com.in",
        "https://mentora.com.in",
        "https://www.mentora.com.in"
    ]
    
    print("🧪 Тестирование лендинговой страницы mentora.com.in...")
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                if "Mentora - Come In to Excellence" in response.text:
                    print(f"✅ {url} - Лендинговая страница загружается корректно")
                else:
                    print(f"⚠️  {url} - Страница загружается, но не содержит ожидаемый контент")
            else:
                print(f"❌ {url} - Ошибка {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"❌ {url} - Ошибка подключения: {e}")
    
    print("\n📋 Проверьте вручную:")
    print("1. Откройте https://mentora.com.in в браузере")
    print("2. Убедитесь, что загружается космический дизайн")
    print("3. Проверьте, что все элементы отображаются корректно")
    print("4. Протестируйте на мобильных устройствах")

if __name__ == "__main__":
    test_mentora_landing()
