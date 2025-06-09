#!/usr/bin/env python3
"""
Скрипт для запуска тестов ИИ виджетов
Поддерживает различные типы тестирования и конфигурации
"""

import sys
import os
import subprocess
import argparse
import time
from pathlib import Path

def print_banner():
    """Печать баннера"""
    print("🧪" + "="*60)
    print("  ТЕСТИРОВАНИЕ ИИ ВИДЖЕТОВ - DENTAL ACADEMY")
    print("="*62)
    print()

def check_requirements():
    """Проверка требований для запуска тестов"""
    print("🔍 Проверка требований...")
    
    requirements = {
        'flask': 'Flask приложение',
        'selenium': 'Selenium для браузерных тестов',
        'unittest': 'Модуль unittest для базовых тестов'
    }
    
    missing = []
    
    try:
        import flask
        print("  ✅ Flask установлен")
    except ImportError:
        missing.append('flask')
        print("  ❌ Flask не установлен")
    
    try:
        import selenium
        print("  ✅ Selenium установлен")
    except ImportError:
        missing.append('selenium')
        print("  ⚠️ Selenium не установлен (опциональный)")
    
    if missing and 'flask' in missing:
        print("\n❌ Критические зависимости отсутствуют!")
        print("Установите: pip install flask")
        return False
    
    print("  ✅ Базовые требования выполнены")
    return True

def run_unit_tests():
    """Запуск unit тестов"""
    print("\n🧪 Запуск Unit тестов...")
    
    test_file = "tests/test_ai_widgets.py"
    
    if not os.path.exists(test_file):
        print(f"❌ Файл тестов не найден: {test_file}")
        return False
    
    try:
        # Добавляем текущую директорию в PYTHONPATH
        env = os.environ.copy()
        current_dir = os.getcwd()
        if 'PYTHONPATH' in env:
            env['PYTHONPATH'] = f"{current_dir}:{env['PYTHONPATH']}"
        else:
            env['PYTHONPATH'] = current_dir
        
        result = subprocess.run([
            sys.executable, "-m", "unittest", 
            "tests.test_ai_widgets", "-v"
        ], capture_output=True, text=True, timeout=120, env=env)
        
        print("📋 Результаты Unit тестов:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Предупреждения/Ошибки:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Unit тесты пройдены успешно!")
            return True
        else:
            print("❌ Unit тесты завершились с ошибками")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏱️ Тайм-аут выполнения unit тестов")
        return False
    except Exception as e:
        print(f"❌ Ошибка выполнения unit тестов: {e}")
        return False

def run_selenium_tests():
    """Запуск Selenium тестов"""
    print("\n🌐 Запуск Selenium тестов...")
    
    # Проверяем наличие Selenium
    try:
        import selenium
    except ImportError:
        print("⚠️ Selenium не установлен, пропускаем браузерные тесты")
        return True  # Не критично
    
    test_file = "tests/test_ai_widgets_selenium.py"
    
    if not os.path.exists(test_file):
        print(f"❌ Файл Selenium тестов не найден: {test_file}")
        return False
    
    print("⚠️ Предварительные требования для Selenium:")
    print("  1. Flask сервер должен быть запущен на localhost:5000")
    print("  2. ChromeDriver должен быть установлен")
    print("  3. Тестовый пользователь должен существовать в БД")
    
    response = input("\nПродолжить Selenium тесты? (y/n): ").lower()
    if response != 'y':
        print("⏭️ Selenium тесты пропущены")
        return True
    
    try:
        result = subprocess.run([
            sys.executable, "tests/test_ai_widgets_selenium.py"
        ], capture_output=True, text=True, timeout=300)
        
        print("📋 Результаты Selenium тестов:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Предупреждения/Ошибки:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ Selenium тесты пройдены успешно!")
            return True
        else:
            print("❌ Selenium тесты завершились с ошибками")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏱️ Тайм-аут выполнения Selenium тестов")
        return False
    except Exception as e:
        print(f"❌ Ошибка выполнения Selenium тестов: {e}")
        return False

def check_server_status():
    """Проверка статуса Flask сервера"""
    print("\n🌐 Проверка статуса сервера...")
    
    try:
        import requests
        
        response = requests.get("http://localhost:5000/en/", timeout=5)
        if response.status_code == 200:
            print("  ✅ Сервер доступен на localhost:5000")
            return True
        else:
            print(f"  ⚠️ Сервер отвечает с кодом: {response.status_code}")
            return False
            
    except ImportError:
        print("  ⚠️ Requests не установлен, пропускаем проверку сервера")
        return True
    except Exception as e:
        print(f"  ❌ Сервер недоступен: {e}")
        print("  💡 Запустите Flask приложение: python app.py")
        return False

def run_linting():
    """Запуск линтеров для проверки качества кода"""
    print("\n🔍 Проверка качества кода...")
    
    # Проверяем наличие flake8
    try:
        result = subprocess.run(["flake8", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("  ✅ flake8 доступен")
            
            # Запускаем flake8 для тестов
            lint_result = subprocess.run([
                "flake8", "tests/", "--max-line-length=100", 
                "--ignore=E501,W503"
            ], capture_output=True, text=True)
            
            if lint_result.returncode == 0:
                print("  ✅ Код тестов соответствует стандартам")
            else:
                print("  ⚠️ Найдены проблемы со стилем кода:")
                print(lint_result.stdout)
        else:
            print("  ⚠️ flake8 не найден")
            
    except FileNotFoundError:
        print("  ⚠️ flake8 не установлен (pip install flake8)")

def generate_test_report(results):
    """Генерация отчета о тестировании"""
    print("\n📊 Генерация отчета...")
    
    report_lines = [
        "# 📋 Отчет о тестировании ИИ виджетов",
        f"\n**Дата:** {time.strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Версия Python:** {sys.version}",
        "\n## 📈 Результаты тестирования\n"
    ]
    
    for test_type, status in results.items():
        status_icon = "✅" if status else "❌"
        report_lines.append(f"- {status_icon} {test_type}")
    
    report_lines.extend([
        "\n## 📝 Детали",
        "\n### Unit тесты",
        "- Проверка HTML структуры виджетов",
        "- Проверка CSS классов и стилей", 
        "- Проверка JavaScript функций",
        "- Проверка безопасности и авторизации",
        "- Проверка мобильной адаптивности",
        "\n### Selenium тесты (если запущены)",
        "- Интерактивность виджетов",
        "- Браузерная совместимость",
        "- Реальное поведение в браузере",
        "\n## 🎯 Рекомендации",
        "\nДля полного тестирования также выполните:",
        "1. Мануальное тестирование по чек-листу",
        "2. Тестирование на реальных устройствах", 
        "3. Нагрузочное тестирование AI endpoints",
        "4. Accessibility тестирование"
    ])
    
    report_content = "\n".join(report_lines)
    
    try:
        with open("test_report.md", "w", encoding="utf-8") as f:
            f.write(report_content)
        print("✅ Отчет сохранен в test_report.md")
    except Exception as e:
        print(f"⚠️ Не удалось сохранить отчет: {e}")
        print("\n📋 Содержание отчета:")
        print(report_content)

def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(description="Запуск тестов ИИ виджетов")
    parser.add_argument("--unit-only", action="store_true", 
                       help="Запустить только Unit тесты")
    parser.add_argument("--selenium-only", action="store_true",
                       help="Запустить только Selenium тесты")
    parser.add_argument("--no-server-check", action="store_true",
                       help="Пропустить проверку сервера")
    parser.add_argument("--with-lint", action="store_true",
                       help="Включить проверку качества кода")
    
    args = parser.parse_args()
    
    print_banner()
    
    # Проверка требований
    if not check_requirements():
        return 1
    
    results = {}
    
    # Проверка сервера (если нужно)
    if not args.no_server_check and not args.unit_only:
        server_ok = check_server_status()
        results['Статус сервера'] = server_ok
    
    # Линтинг (если запрошен)
    if args.with_lint:
        run_linting()
    
    # Unit тесты
    if not args.selenium_only:
        unit_success = run_unit_tests()
        results['Unit тесты'] = unit_success
    
    # Selenium тесты
    if not args.unit_only:
        selenium_success = run_selenium_tests()
        results['Selenium тесты'] = selenium_success
    
    # Генерация отчета
    generate_test_report(results)
    
    # Итоговый результат
    print("\n" + "="*50)
    total_passed = sum(1 for status in results.values() if status)
    total_tests = len(results)
    
    if total_passed == total_tests:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
        print(f"✅ {total_passed}/{total_tests} тест-групп успешно")
        return 0
    else:
        print("⚠️ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ")
        print(f"✅ {total_passed}/{total_tests} тест-групп успешно")
        print("\n💡 Проверьте детали выше и исправьте найденные проблемы")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 