#!/usr/bin/env python3
"""
Тест переключения языка на страницах профиля
"""

import requests
import time

def test_profile_language_switching():
    """Тестирует переключение языка на страницах профиля"""
    
    base_url = "http://localhost:5002"
    
    # Список страниц профиля для тестирования
    profile_pages = [
        "/profile",
        "/profile/personal-info", 
        "/profile/documents",
        "/profile/settings",
        "/profile/security",
        "/profile/statistics"
    ]
    
    # Список языков для тестирования
    languages = ['nl', 'en', 'ru', 'uk', 'es', 'pt', 'fa', 'tr']
    
    print("🔍 ТЕСТИРОВАНИЕ ПЕРЕКЛЮЧЕНИЯ ЯЗЫКА НА СТРАНИЦАХ ПРОФИЛЯ")
    print("=" * 70)
    
    # Сначала нужно залогиниться (это упрощенный тест)
    print("⚠️  Внимание: Этот тест требует авторизованного пользователя")
    print("   Пожалуйста, откройте браузер и залогиньтесь на http://localhost:5002")
    print("   Затем нажмите Enter для продолжения...")
    input()
    
    for page in profile_pages:
        print(f"\n📄 Тестируем страницу: {page}")
        print("-" * 50)
        
        for lang in languages:
            url = f"{base_url}{page}?lang={lang}"
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    # Проверяем, есть ли в HTML указание на язык
                    if f'lang="{lang}"' in response.text or f"lang={lang}" in response.text:
                        print(f"  ✅ {lang.upper()}: Страница загружена, язык установлен")
                    else:
                        print(f"  ⚠️  {lang.upper()}: Страница загружена, но язык может быть неправильным")
                elif response.status_code == 302:
                    print(f"  🔄 {lang.upper()}: Перенаправление (возможно, требуется авторизация)")
                else:
                    print(f"  ❌ {lang.upper()}: Ошибка {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"  ❌ {lang.upper()}: Ошибка соединения - {e}")
            
            time.sleep(0.5)  # Небольшая задержка между запросами
    
    print("\n" + "=" * 70)
    print("✅ Тестирование завершено!")
    print("\n💡 Рекомендации:")
    print("   1. Проверьте, что селектор языка в заголовке работает")
    print("   2. Убедитесь, что при переключении языка URL обновляется")
    print("   3. Проверьте, что контент страницы переводится")

if __name__ == "__main__":
    test_profile_language_switching()
