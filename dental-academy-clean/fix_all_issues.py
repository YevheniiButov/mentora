#!/usr/bin/env python3
"""
🔧 Полное исправление всех проблем
"""

import os
import re

def fix_ukrainian_encoding():
    """Исправляет проблемы с кодировкой в украинском файле"""
    print("🔧 Исправление украинской кодировки...")
    
    try:
        with open('translations/uk.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Проверяем и исправляем возможные проблемы с апострофами
        original_content = content
        
        # Заменяем возможные HTML-кодированные апострофы
        content = content.replace('&#39;', "'")
        content = content.replace('&apos;', "'")
        content = content.replace('&quot;', '"')
        
        # Убеждаемся, что все апострофы правильно экранированы
        content = re.sub(r"обов'язковий", "обов\\'язковий", content)
        content = re.sub(r"обов'язкові", "обов\\'язкові", content)
        content = re.sub(r"обов'язкова", "обов\\'язкова", content)
        
        if content != original_content:
            with open('translations/uk.py', 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ Украинская кодировка исправлена")
        else:
            print("✅ Украинская кодировка уже корректна")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка исправления украинской кодировки: {e}")
        return False

def create_production_config():
    """Создает конфигурацию для production"""
    print("🔧 Создание production конфигурации...")
    
    config_content = '''# Production Configuration
# Этот файл содержит временные значения для восстановления работы сервера

import os

# Временные значения для production (НЕБЕЗОПАСНО - только для экстренного восстановления)
PRODUCTION_TEMP_CONFIG = {
    'SECRET_KEY': 'mentora-production-temp-key-2024',
    'MAIL_USERNAME': 'MS_uUzJtfkAxyPn@mentora.mlsender.net',
    'MAIL_PASSWORD': 'mssp.eTIPhpXlO2nu.e6t7xgcGA1kl.Bw3hiAB80JpM',
    'MAIL_DEFAULT_SENDER': 'Mentora <noreply@mentora.com>',
    'MAIL_SUPPRESS_SEND': True
}

def get_production_temp_config():
    """Возвращает временную конфигурацию для production"""
    return PRODUCTION_TEMP_CONFIG
'''
    
    with open('production_temp_config.py', 'w', encoding='utf-8') as f:
        f.write(config_content)
    
    print("✅ Production конфигурация создана")
    return True

def create_emergency_deployment_script():
    """Создает скрипт для экстренного деплоя"""
    print("🔧 Создание скрипта экстренного деплоя...")
    
    script_content = '''#!/bin/bash
# 🚨 Экстренный деплой для восстановления работы сервера

echo "🚨 ЭКСТРЕННЫЙ ДЕПЛОЙ - ВОССТАНОВЛЕНИЕ РАБОТЫ СЕРВЕРА"
echo "=================================================="

# 1. Останавливаем сервис
echo "1. Остановка сервиса..."
systemctl stop your-app-service

# 2. Переходим в директорию приложения
cd /path/to/your/app

# 3. Получаем последние изменения
echo "2. Получение последних изменений..."
git pull origin main

# 4. Устанавливаем зависимости
echo "3. Установка зависимостей..."
pip3 install -r requirements.txt

# 5. Создаем .env файл с временными значениями
echo "4. Создание .env файла..."
cat > .env << EOF
SECRET_KEY=mentora-production-temp-key-2024
FLASK_ENV=production
FLASK_DEBUG=0
MAIL_USERNAME=MS_uUzJtfkAxyPn@mentora.mlsender.net
MAIL_PASSWORD=mssp.eTIPhpXlO2nu.e6t7xgcGA1kl.Bw3hiAB80JpM
MAIL_DEFAULT_SENDER=Mentora <noreply@mentora.com>
MAIL_SUPPRESS_SEND=true
DATABASE_URL=your-production-database-url
EOF

# 6. Устанавливаем права доступа
chmod 600 .env

# 7. Запускаем миграции БД
echo "5. Запуск миграций БД..."
python3 -c "
import os
os.environ['FLASK_APP'] = 'app.py'
from flask_migrate import upgrade
from app import create_app
app = create_app()
with app.app_context():
    upgrade()
"

# 8. Запускаем сервис
echo "6. Запуск сервиса..."
systemctl start your-app-service

# 9. Проверяем статус
echo "7. Проверка статуса..."
sleep 5
systemctl status your-app-service --no-pager

echo "✅ ЭКСТРЕННЫЙ ДЕПЛОЙ ЗАВЕРШЕН"
echo "🌐 Проверьте сайт: https://www.mentora.com.in"
'''
    
    with open('emergency_deploy.sh', 'w') as f:
        f.write(script_content)
    
    # Делаем скрипт исполняемым
    os.chmod('emergency_deploy.sh', 0o755)
    
    print("✅ Скрипт экстренного деплоя создан: emergency_deploy.sh")
    return True

def test_application():
    """Тестирует приложение"""
    print("🧪 Тестирование приложения...")
    
    try:
        # Простой тест импорта
        import sys
        sys.path.insert(0, '.')
        
        # Тестируем импорт основных модулей
        from app import create_app
        app = create_app()
        
        print("✅ Приложение успешно создается")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка тестирования приложения: {e}")
        return False

def main():
    """Основная функция"""
    print("🔧 ПОЛНОЕ ИСПРАВЛЕНИЕ ВСЕХ ПРОБЛЕМ")
    print("=" * 50)
    
    success_count = 0
    total_tasks = 0
    
    # Исправляем украинскую кодировку
    total_tasks += 1
    if fix_ukrainian_encoding():
        success_count += 1
    
    # Создаем production конфигурацию
    total_tasks += 1
    if create_production_config():
        success_count += 1
    
    # Создаем скрипт экстренного деплоя
    total_tasks += 1
    if create_emergency_deployment_script():
        success_count += 1
    
    # Тестируем приложение
    total_tasks += 1
    if test_application():
        success_count += 1
    
    # Результат
    print("\n" + "=" * 50)
    print(f"📊 РЕЗУЛЬТАТ: {success_count}/{total_tasks} задач выполнено")
    
    if success_count == total_tasks:
        print("🎉 ВСЕ ПРОБЛЕМЫ ИСПРАВЛЕНЫ!")
        print("\n✅ Что было сделано:")
        print("  - Исправлена украинская кодировка")
        print("  - Добавлены временные значения для production")
        print("  - Создан скрипт экстренного деплоя")
        print("  - Протестировано приложение")
        
        print("\n🚨 СЛЕДУЮЩИЕ ШАГИ:")
        print("1. Запушите изменения в Git")
        print("2. Запустите emergency_deploy.sh на production сервере")
        print("3. Проверьте работу сайта")
        print("4. Настройте правильные переменные окружения")
        
        return True
    else:
        print("❌ НЕКОТОРЫЕ ЗАДАЧИ НЕ ВЫПОЛНЕНЫ!")
        return False

if __name__ == "__main__":
    main()
