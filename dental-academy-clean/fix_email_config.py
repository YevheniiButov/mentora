#!/usr/bin/env python3
"""
Скрипт для исправления настроек email
Обновляет .env файл с правильными настройками Brevo
"""

import os
import shutil
from datetime import datetime

def backup_env_file():
    """Создает резервную копию .env файла"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f".env.backup_{timestamp}"
    shutil.copy2('.env', backup_name)
    print(f"✅ Создана резервная копия: {backup_name}")
    return backup_name

def update_env_file():
    """Обновляет .env файл с настройками Brevo"""
    print("🔧 Обновление настроек email в .env файле...")
    
    # Читаем текущий .env файл
    with open('.env', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Обновляем настройки email
    updated_lines = []
    for line in lines:
        if line.startswith('MAIL_SERVER='):
            updated_lines.append('MAIL_SERVER=smtp-relay.brevo.com\n')
        elif line.startswith('MAIL_USERNAME='):
            updated_lines.append('MAIL_USERNAME=96d92f001@smtp-brevo.com\n')
        elif line.startswith('MAIL_PASSWORD='):
            updated_lines.append('MAIL_PASSWORD=JrbVFGpHhgynKMOQ\n')
        elif line.startswith('# Email Configuration - MailerSend'):
            updated_lines.append('# Email Configuration - Brevo (соответствует продакшену)\n')
        else:
            updated_lines.append(line)
    
    # Записываем обновленный файл
    with open('.env', 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)
    
    print("✅ .env файл обновлен с настройками Brevo")

def test_email_config():
    """Тестирует настройки email"""
    print("\n🧪 Тестирование настроек email...")
    
    # Импортируем настройки
    from config import get_config
    config = get_config()
    
    print(f"MAIL_SERVER: {config.MAIL_SERVER}")
    print(f"MAIL_PORT: {config.MAIL_PORT}")
    print(f"MAIL_USE_TLS: {config.MAIL_USE_TLS}")
    print(f"MAIL_USERNAME: {config.MAIL_USERNAME}")
    print(f"MAIL_PASSWORD: {'SET' if config.MAIL_PASSWORD else 'NOT SET'}")
    print(f"MAIL_SUPPRESS_SEND: {config.MAIL_SUPPRESS_SEND}")
    
    # Проверяем, что настройки соответствуют продакшену
    expected_settings = {
        'MAIL_SERVER': 'smtp-relay.brevo.com',
        'MAIL_PORT': 587,
        'MAIL_USE_TLS': True,
        'MAIL_USERNAME': '96d92f001@smtp-brevo.com'
    }
    
    all_correct = True
    for key, expected_value in expected_settings.items():
        actual_value = getattr(config, key)
        if actual_value != expected_value:
            print(f"❌ {key}: ожидается {expected_value}, получено {actual_value}")
            all_correct = False
        else:
            print(f"✅ {key}: {actual_value}")
    
    if all_correct:
        print("\n✅ Все настройки email корректны!")
        return True
    else:
        print("\n❌ Найдены несоответствия в настройках email")
        return False

def main():
    print("🦷 Mentora Email Configuration Fix")
    print("=" * 50)
    
    # Создаем резервную копию
    backup_file = backup_env_file()
    
    # Обновляем настройки
    update_env_file()
    
    # Тестируем настройки
    success = test_email_config()
    
    if success:
        print("\n🎉 Настройки email успешно обновлены!")
        print("Теперь можно тестировать отправку писем через Flask приложение.")
    else:
        print("\n⚠️ Обнаружены проблемы с настройками.")
        print(f"Можно восстановить из резервной копии: {backup_file}")

if __name__ == '__main__':
    main()
