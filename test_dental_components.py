#!/usr/bin/env python3
"""
Тестовый скрипт для проверки компонентов Dental Academy
"""

import requests
import json
import time

def test_dental_components():
    """Тестирование компонентов Dental Academy"""
    
    base_url = "http://localhost:5000"
    
    print("🧪 Тестирование компонентов Dental Academy")
    print("=" * 50)
    
    # Тест 1: Проверка доступности редактора
    print("\n1. Проверка доступности редактора...")
    try:
        response = requests.get(f"{base_url}/admin/enhanced-editor", timeout=5)
        if response.status_code == 200:
            print("✅ Редактор доступен")
        else:
            print(f"❌ Редактор недоступен: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения к редактору: {e}")
        return False
    
    # Тест 2: Проверка загрузки CSS компонентов
    print("\n2. Проверка загрузки CSS компонентов...")
    try:
        response = requests.get(f"{base_url}/static/css/dental-components.css", timeout=5)
        if response.status_code == 200:
            css_content = response.text
            if "learning-path-btn" in css_content and "subject-card" in css_content:
                print("✅ CSS компонентов загружен корректно")
            else:
                print("⚠️ CSS загружен, но не содержит ожидаемые стили")
        else:
            print(f"❌ CSS компонентов недоступен: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка загрузки CSS: {e}")
    
    # Тест 3: Проверка загрузки JS компонентов
    print("\n3. Проверка загрузки JS компонентов...")
    try:
        response = requests.get(f"{base_url}/static/js/dental-grapesjs-components.js", timeout=5)
        if response.status_code == 200:
            js_content = response.text
            if "learning-path-button" in js_content and "subject-card" in js_content:
                print("✅ JS компонентов загружен корректно")
            else:
                print("⚠️ JS загружен, но не содержит ожидаемые компоненты")
        else:
            print(f"❌ JS компонентов недоступен: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка загрузки JS: {e}")
    
    # Тест 4: Проверка API шаблонов
    print("\n4. Проверка API шаблонов...")
    try:
        response = requests.get(f"{base_url}/api/templates", timeout=5)
        if response.status_code == 200:
            templates = response.json()
            print(f"✅ API шаблонов работает, найдено шаблонов: {len(templates)}")
        else:
            print(f"⚠️ API шаблонов недоступен: {response.status_code}")
    except Exception as e:
        print(f"⚠️ Ошибка API шаблонов: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Тестирование завершено!")
    print("\n📋 Следующие шаги:")
    print("1. Откройте браузер и перейдите на http://localhost:5000/admin/enhanced-editor")
    print("2. Проверьте, что в панели блоков появились компоненты 'Dental Academy'")
    print("3. Попробуйте добавить компоненты на холст")
    print("4. Проверьте работу traits (свойств) компонентов")
    
    return True

def check_server_status():
    """Проверка статуса сервера"""
    try:
        response = requests.get("http://localhost:5000", timeout=3)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🚀 Запуск тестирования компонентов Dental Academy")
    
    # Проверяем, запущен ли сервер
    if not check_server_status():
        print("❌ Сервер не запущен. Запустите 'python app.py' и попробуйте снова.")
        exit(1)
    
    # Запускаем тесты
    test_dental_components() 