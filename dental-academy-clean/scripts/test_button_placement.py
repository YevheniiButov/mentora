#!/usr/bin/env python3
"""
Тест размещения кнопки "Детальный план" в календаре
"""

import requests
from bs4 import BeautifulSoup
import re

def test_button_placement():
    """Тест размещения кнопки в календаре"""
    print("🧪 ТЕСТ РАЗМЕЩЕНИЯ КНОПКИ В КАЛЕНДАРЕ")
    print("=" * 40)
    
    try:
        # Получаем страницу календаря
        url = "http://127.0.0.1:5000/dashboard/learning-planner/26"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            print("✅ Страница календаря загружена успешно")
            
            # Парсим HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Проверяем наличие header-content
            header_content = soup.find('div', class_='header-content')
            if header_content:
                print("✅ Элемент .header-content найден")
                
                # Проверяем наличие action-buttons
                action_buttons = header_content.find('div', class_='action-buttons')
                if action_buttons:
                    print("✅ Элемент .action-buttons найден")
                    
                    # Проверяем наличие кнопки "Детальный план"
                    plan_button = action_buttons.find('button', string=re.compile(r'Детальный план'))
                    if plan_button:
                        print("✅ Кнопка '📋 Детальный план' найдена!")
                        print(f"   Класс: {plan_button.get('class', [])}")
                        print(f"   Текст: {plan_button.get_text().strip()}")
                    else:
                        print("❌ Кнопка 'Детальный план' НЕ найдена")
                        print("   Доступные кнопки:")
                        for button in action_buttons.find_all('button'):
                            print(f"   - {button.get_text().strip()}")
                else:
                    print("❌ Элемент .action-buttons НЕ найден")
            else:
                print("❌ Элемент .header-content НЕ найден")
                
        else:
            print(f"❌ Ошибка загрузки страницы: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Не удалось подключиться к серверу")
        print("   Убедитесь, что Flask сервер запущен на порту 5000")
    except Exception as e:
        print(f"❌ Ошибка тестирования: {e}")

if __name__ == "__main__":
    test_button_placement() 