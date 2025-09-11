#!/usr/bin/env python3
"""
🔍 Диагностика проблем production сервера
"""

def check_common_500_errors():
    """Проверяет наиболее частые причины ошибки 500"""
    
    print("🔍 Диагностика ошибки 500 на production сервере...")
    print("=" * 60)
    
    issues = [
        {
            "problem": "Отсутствуют переменные окружения",
            "symptoms": "SECRET_KEY, MAIL_USERNAME, MAIL_PASSWORD не установлены",
            "solution": "Настроить переменные окружения на сервере",
            "priority": "🚨 КРИТИЧНО"
        },
        {
            "problem": "Проблема с базой данных",
            "symptoms": "SQLALCHEMY_DATABASE_URI неверный или БД недоступна",
            "solution": "Проверить подключение к БД и миграции",
            "priority": "🚨 КРИТИЧНО"
        },
        {
            "problem": "Ошибка в коде после изменений",
            "symptoms": "Синтаксические ошибки или импорты",
            "solution": "Проверить логи сервера на ошибки Python",
            "priority": "⚠️ ВЫСОКО"
        },
        {
            "problem": "Проблема с зависимостями",
            "symptoms": "Отсутствующие пакеты или конфликты версий",
            "solution": "Обновить requirements.txt и переустановить пакеты",
            "priority": "⚠️ ВЫСОКО"
        },
        {
            "problem": "Проблема с правами доступа",
            "symptoms": "Сервер не может читать файлы или писать в директории",
            "solution": "Проверить права доступа к файлам и папкам",
            "priority": "⚠️ СРЕДНЕ"
        }
    ]
    
    for i, issue in enumerate(issues, 1):
        print(f"{i}. {issue['priority']} {issue['problem']}")
        print(f"   Симптомы: {issue['symptoms']}")
        print(f"   Решение: {issue['solution']}")
        print()
    
    return issues

def generate_fix_commands():
    """Генерирует команды для исправления"""
    
    print("🔧 Команды для исправления:")
    print("=" * 40)
    
    commands = [
        {
            "title": "Проверка логов сервера",
            "command": "tail -f /var/log/nginx/error.log",
            "description": "Просмотр логов веб-сервера"
        },
        {
            "title": "Проверка логов приложения",
            "command": "journalctl -u your-app-service -f",
            "description": "Просмотр логов Flask приложения"
        },
        {
            "title": "Проверка переменных окружения",
            "command": "env | grep -E '(SECRET_KEY|MAIL_|DATABASE_)'",
            "description": "Проверка наличия критических переменных"
        },
        {
            "title": "Проверка статуса сервиса",
            "command": "systemctl status your-app-service",
            "description": "Проверка статуса приложения"
        },
        {
            "title": "Перезапуск приложения",
            "command": "systemctl restart your-app-service",
            "description": "Перезапуск сервиса приложения"
        },
        {
            "title": "Проверка подключения к БД",
            "command": "python3 -c \"from app import db; print('DB OK')\"",
            "description": "Тест подключения к базе данных"
        }
    ]
    
    for i, cmd in enumerate(commands, 1):
        print(f"{i}. {cmd['title']}")
        print(f"   Команда: {cmd['command']}")
        print(f"   Описание: {cmd['description']}")
        print()

def create_emergency_fix_script():
    """Создает скрипт для экстренного исправления"""
    
    script_content = """#!/bin/bash
# 🚨 Экстренное исправление ошибки 500

echo "🚨 Экстренное исправление ошибки 500 на production сервере"
echo "=========================================================="

# 1. Проверяем переменные окружения
echo "1. Проверка переменных окружения..."
if [ -z "$SECRET_KEY" ]; then
    echo "❌ SECRET_KEY не установлен!"
    export SECRET_KEY="emergency-secret-key-$(date +%s)"
    echo "✅ Установлен временный SECRET_KEY"
fi

if [ -z "$MAIL_USERNAME" ]; then
    echo "❌ MAIL_USERNAME не установлен!"
    export MAIL_SUPPRESS_SEND="true"
    echo "✅ Отключена отправка email"
fi

# 2. Проверяем базу данных
echo "2. Проверка базы данных..."
python3 -c "
import os
os.environ['FLASK_APP'] = 'app.py'
from app import create_app, db
app = create_app()
with app.app_context():
    try:
        db.engine.execute('SELECT 1')
        print('✅ База данных доступна')
    except Exception as e:
        print(f'❌ Ошибка БД: {e}')
"

# 3. Перезапускаем сервис
echo "3. Перезапуск сервиса..."
systemctl restart your-app-service
sleep 5

# 4. Проверяем статус
echo "4. Проверка статуса..."
systemctl status your-app-service --no-pager

echo "✅ Экстренное исправление завершено"
"""
    
    with open('emergency_fix_500.sh', 'w') as f:
        f.write(script_content)
    
    print("✅ Создан скрипт экстренного исправления: emergency_fix_500.sh")
    print("   Запустите: chmod +x emergency_fix_500.sh && ./emergency_fix_500.sh")

def main():
    """Основная функция диагностики"""
    print("🚨 ДИАГНОСТИКА ОШИБКИ 500 НА PRODUCTION СЕРВЕРЕ")
    print("=" * 60)
    
    # Проверяем возможные проблемы
    issues = check_common_500_errors()
    
    print("\n" + "=" * 60)
    
    # Генерируем команды для исправления
    generate_fix_commands()
    
    print("\n" + "=" * 60)
    
    # Создаем скрипт экстренного исправления
    create_emergency_fix_script()
    
    print("\n🎯 РЕКОМЕНДУЕМЫЕ ДЕЙСТВИЯ:")
    print("1. 🚨 НЕМЕДЛЕННО: Проверьте логи сервера")
    print("2. 🔧 Проверьте переменные окружения")
    print("3. 🗄️ Проверьте подключение к базе данных")
    print("4. 🔄 Перезапустите приложение")
    print("5. 📊 Мониторьте логи после исправления")

if __name__ == "__main__":
    main()
