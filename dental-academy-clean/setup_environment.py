#!/usr/bin/env python3
"""
🔧 Автоматическая настройка окружения для Mentora
Этот скрипт создаст .env файл с новыми безопасными учетными данными
"""

import os
import secrets
import string
from pathlib import Path

def generate_secret_key(length=50):
    """Генерирует безопасный секретный ключ"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_mailersend_credentials():
    """Генерирует новые учетные данные для MailerSend"""
    # Генерируем новый username
    username_id = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    username = f"MS_{username_id}@mentora.mlsender.net"
    
    # Генерируем новый password
    password_parts = [
        'mssp',
        ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12)),
        ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12)),
        ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    ]
    password = '.'.join(password_parts)
    
    return username, password

def create_env_file():
    """Создает .env файл с новыми учетными данными"""
    env_content = f"""# .env - Переменные окружения для Mentora
# ВНИМАНИЕ: Этот файл НЕ должен попадать в Git!
# Создано автоматически: {os.popen('date').read().strip()}

# Flask Configuration
SECRET_KEY={generate_secret_key()}
FLASK_ENV=development
FLASK_DEBUG=1

# Database Configuration
DATABASE_URL=sqlite:///dental_academy_clean.db

# Email Configuration - MailerSend (НОВЫЕ БЕЗОПАСНЫЕ УЧЕТНЫЕ ДАННЫЕ)
MAIL_SERVER=smtp.mailersend.net
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USE_SSL=false
MAIL_USERNAME={generate_mailersend_credentials()[0]}
MAIL_PASSWORD={generate_mailersend_credentials()[1]}
MAIL_DEFAULT_SENDER=Mentora <noreply@mentora.com>

# Email Settings
MAIL_SUPPRESS_SEND=true
EMAIL_CONFIRMATION_SALT={generate_secret_key(32)}

# DigiD Configuration (для production)
DIGID_ENTITY_ID=mentora-entity-id
DIGID_ACS_URL=https://mentora.com/digid/callback
DIGID_SLO_URL=https://mentora.com/digid/logout
DIGID_CERTIFICATE_PATH=/secure/path/to/certificate.pem
DIGID_PRIVATE_KEY_PATH=/secure/path/to/private-key.pem

# DigiD URLs
DIGID_BASE_URL=https://digid.nl
DIGID_AUTH_URL=https://digid.nl/auth
DIGID_LOGOUT_URL_EXTERNAL=https://digid.nl/logout
"""
    
    # Записываем в .env файл
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print("✅ .env файл создан успешно!")
    return True

def check_gitignore():
    """Проверяет, что .env файл исключен из Git"""
    gitignore_path = Path('.gitignore')
    if gitignore_path.exists():
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if '.env' in content:
                print("✅ .env файл правильно исключен из Git")
                return True
            else:
                print("⚠️  .env файл НЕ исключен из Git! Добавляем...")
                with open(gitignore_path, 'a', encoding='utf-8') as f:
                    f.write('\n# Environment variables\n.env\n')
                print("✅ .env файл добавлен в .gitignore")
                return True
    else:
        print("❌ .gitignore файл не найден!")
        return False

def main():
    """Основная функция настройки"""
    print("🔧 Настройка окружения для Mentora...")
    print("=" * 50)
    
    # Проверяем .gitignore
    if not check_gitignore():
        print("❌ Не удалось настроить .gitignore")
        return False
    
    # Создаем .env файл
    if create_env_file():
        print("✅ Окружение настроено успешно!")
        print("\n📋 Что было сделано:")
        print("  - Создан .env файл с новыми учетными данными")
        print("  - Сгенерированы безопасные секретные ключи")
        print("  - Настроены новые SMTP учетные данные")
        print("  - Проверена защита .env файла от Git")
        
        print("\n🚨 ВАЖНО:")
        print("  1. Обновите учетные данные в MailerSend")
        print("  2. Отзовите старые скомпрометированные ключи")
        print("  3. Протестируйте отправку email")
        
        return True
    else:
        print("❌ Не удалось создать .env файл")
        return False

if __name__ == "__main__":
    main()
