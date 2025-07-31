#!/usr/bin/env python3
"""
Тестовый скрипт для проверки CSS Variables Manager
"""

import requests
import json
import time

def test_css_variables_manager():
    """Тестирование CSS Variables Manager"""
    
    base_url = "http://localhost:5000"
    
    print("🎨 Тестирование CSS Variables Manager")
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
    
    # Тест 2: Проверка загрузки CSS Variables Manager
    print("\n2. Проверка загрузки CSS Variables Manager...")
    try:
        response = requests.get(f"{base_url}/static/js/css-variables-manager.js", timeout=5)
        if response.status_code == 200:
            js_content = response.text
            if "CSSVariablesManager" in js_content and "loadProjectVariables" in js_content:
                print("✅ CSS Variables Manager загружен корректно")
            else:
                print("⚠️ JS загружен, но не содержит ожидаемые функции")
        else:
            print(f"❌ CSS Variables Manager недоступен: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка загрузки CSS Variables Manager: {e}")
    
    # Тест 3: Проверка загрузки CSS стилей панели
    print("\n3. Проверка загрузки CSS стилей панели...")
    try:
        response = requests.get(f"{base_url}/static/css/css-variables-panel.css", timeout=5)
        if response.status_code == 200:
            css_content = response.text
            if "css-variables-panel" in css_content and "variable-control" in css_content:
                print("✅ CSS стили панели загружены корректно")
            else:
                print("⚠️ CSS загружен, но не содержит ожидаемые стили")
        else:
            print(f"❌ CSS стили панели недоступны: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка загрузки CSS стилей: {e}")
    
    # Тест 4: Проверка CSS файлов проекта
    print("\n4. Проверка CSS файлов проекта...")
    css_files = [
        '/static/css/themes/core-variables.css',
        '/static/css/base/global.css',
        '/static/css/components/components.css',
        '/static/css/pages/learning_map.css'
    ]
    
    for css_file in css_files:
        try:
            response = requests.get(f"{base_url}{css_file}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {css_file} - доступен")
            else:
                print(f"⚠️ {css_file} - недоступен ({response.status_code})")
        except Exception as e:
            print(f"⚠️ {css_file} - ошибка загрузки: {e}")
    
    # Тест 5: Проверка интеграции в шаблоне
    print("\n5. Проверка интеграции в шаблоне...")
    try:
        response = requests.get(f"{base_url}/admin/enhanced-editor", timeout=5)
        if response.status_code == 200:
            html_content = response.text
            if "css-variables-manager.js" in html_content and "css-variables-panel.css" in html_content:
                print("✅ CSS Variables Manager интегрирован в шаблон")
            else:
                print("⚠️ CSS Variables Manager не найден в шаблоне")
        else:
            print(f"❌ Не удалось загрузить шаблон: {response.status_code}")
    except Exception as e:
        print(f"❌ Ошибка проверки интеграции: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Тестирование CSS Variables Manager завершено!")
    print("\n📋 Следующие шаги:")
    print("1. Откройте браузер и перейдите на http://localhost:5000/admin/enhanced-editor")
    print("2. Дождитесь загрузки редактора")
    print("3. Проверьте, что в правой панели появилась секция 'CSS Variables'")
    print("4. Попробуйте изменить переменные и увидеть изменения в реальном времени")
    print("5. Проверьте работу экспорта/импорта переменных")
    
    return True

def check_server_status():
    """Проверка статуса сервера"""
    try:
        response = requests.get("http://localhost:5000", timeout=3)
        return response.status_code == 200
    except:
        return False

if __name__ == "__main__":
    print("🚀 Запуск тестирования CSS Variables Manager")
    
    # Проверяем, запущен ли сервер
    if not check_server_status():
        print("❌ Сервер не запущен. Запустите 'python app.py' и попробуйте снова.")
        exit(1)
    
    # Запускаем тесты
    test_css_variables_manager() 