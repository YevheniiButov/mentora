#!/usr/bin/env python3
"""
Быстрое исправление регистрации - диагностика и решение
"""

import requests
import json
import time

def quick_diagnosis():
    """Быстрая диагностика проблемы"""
    
    print("=== БЫСТРАЯ ДИАГНОСТИКА РЕГИСТРАЦИИ ===")
    print()
    
    base_url = "https://bigmentor.nl"
    
    # 1. Проверяем страницу регистрации
    print("🔍 1. Проверяем страницу регистрации...")
    try:
        response = requests.get(f"{base_url}/auth/register", timeout=10)
        if response.status_code == 200:
            print("✅ Страница доступна")
            
            # Ищем reCAPTCHA
            if 'recaptcha' in response.text.lower():
                print("⚠️  reCAPTCHA найдена на странице")
            else:
                print("✅ reCAPTCHA не найдена")
        else:
            print(f"❌ Страница недоступна: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return
    
    print()
    
    # 2. Тестируем регистрацию
    print("🔍 2. Тестируем регистрацию...")
    
    test_email = f"quick_test_{int(time.time())}@example.com"
    test_data = {
        'email': test_email,
        'first_name': 'Quick',
        'last_name': 'Test',
        'password': 'TestPassword123!',
        'confirm_password': 'TestPassword123!',
        'birth_date': '1990-01-01',
        'nationality': 'ukraine',
        'profession': 'tandarts',
        'legal_status': 'non_eu',
        'dutch_level': 'a1',
        'english_level': 'b2',
        'university_name': 'Test University',
        'degree_type': 'bachelor',
        'study_start_year': '2010',
        'study_end_year': '2014',
        'study_country': 'ukraine',
        'required_consents': 'on',
        'digital_signature': 'Quick Test'
    }
    
    try:
        response = requests.post(f"{base_url}/auth/register", data=test_data, timeout=30)
        
        print(f"📊 Статус: {response.status_code}")
        
        if response.status_code == 200:
            try:
                result = response.json()
                print(f"📊 Ответ: {json.dumps(result, indent=2)}")
                
                if result.get('success'):
                    print("✅ РЕГИСТРАЦИЯ РАБОТАЕТ!")
                    print(f"   User ID: {result.get('user_id')}")
                    print(f"   Email отправлен: {result.get('email_sent')}")
                    
                    print()
                    print("🎯 ПРОБЛЕМА В БРАУЗЕРЕ:")
                    print("1. Откройте https://bigmentor.nl/auth/register")
                    print("2. Заполните форму")
                    print("3. Проверьте консоль браузера (F12)")
                    print("4. Ищите ошибки JavaScript")
                    
                else:
                    print("❌ Регистрация не удалась!")
                    print(f"   Ошибка: {result.get('error')}")
                    
            except json.JSONDecodeError:
                print("❌ Ответ не JSON")
                print(f"📊 Содержимое: {response.text[:200]}")
        else:
            print(f"❌ HTTP ошибка: {response.status_code}")
            print(f"📊 Содержимое: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ Ошибка запроса: {e}")
    
    print()
    print("🚨 ВОЗМОЖНЫЕ ПРОБЛЕМЫ:")
    print("1. reCAPTCHA блокирует в браузере (но не в API)")
    print("2. JavaScript ошибки в браузере")
    print("3. Проблемы с обработкой ответа")
    print("4. Конфликт скриптов")
    
    print()
    print("💡 БЫСТРОЕ РЕШЕНИЕ:")
    print("1. Отключить reCAPTCHA полностью в Render")
    print("2. Проверить JavaScript консоль")
    print("3. Упростить обработку ответа")

if __name__ == '__main__':
    quick_diagnosis()
