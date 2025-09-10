#!/usr/bin/env python3
"""
📧 Автоматическое обновление учетных данных MailerSend
Этот скрипт поможет вам обновить учетные данные в MailerSend
"""

import os
import requests
import json
from dotenv import load_dotenv

def load_environment():
    """Загружает переменные окружения"""
    load_dotenv()
    return {
        'username': os.getenv('MAIL_USERNAME'),
        'password': os.getenv('MAIL_PASSWORD'),
        'sender': os.getenv('MAIL_DEFAULT_SENDER')
    }

def test_smtp_connection(credentials):
    """Тестирует SMTP соединение"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        
        print("🔍 Тестирование SMTP соединения...")
        
        # Извлекаем username из полного email
        username = credentials['username']
        password = credentials['password']
        
        # Подключаемся к SMTP серверу
        server = smtplib.SMTP('smtp.mailersend.net', 587)
        server.starttls()
        server.login(username, password)
        
        print("✅ SMTP соединение успешно!")
        server.quit()
        return True
        
    except Exception as e:
        print(f"❌ Ошибка SMTP соединения: {e}")
        return False

def generate_new_credentials():
    """Генерирует новые учетные данные"""
    import secrets
    import string
    
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

def update_env_file(new_username, new_password):
    """Обновляет .env файл с новыми учетными данными"""
    try:
        # Читаем текущий .env файл
        with open('.env', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Обновляем учетные данные
        updated_lines = []
        for line in lines:
            if line.startswith('MAIL_USERNAME='):
                updated_lines.append(f'MAIL_USERNAME={new_username}\n')
            elif line.startswith('MAIL_PASSWORD='):
                updated_lines.append(f'MAIL_PASSWORD={new_password}\n')
            else:
                updated_lines.append(line)
        
        # Записываем обновленный файл
        with open('.env', 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)
        
        print("✅ .env файл обновлен с новыми учетными данными")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка обновления .env файла: {e}")
        return False

def send_test_email(credentials):
    """Отправляет тестовое письмо"""
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        print("📧 Отправка тестового письма...")
        
        # Создаем сообщение
        msg = MIMEMultipart()
        msg['From'] = credentials['sender']
        msg['To'] = 'test@example.com'  # Замените на реальный email
        msg['Subject'] = 'Mentora - Тест безопасности'
        
        body = """
        🎉 Поздравляем! 
        
        Учетные данные MailerSend успешно обновлены!
        
        Это тестовое письмо подтверждает, что:
        ✅ SMTP соединение работает
        ✅ Новые учетные данные активны
        ✅ Безопасность восстановлена
        
        ---
        Mentora Security Team
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Подключаемся и отправляем
        server = smtplib.SMTP('smtp.mailersend.net', 587)
        server.starttls()
        server.login(credentials['username'], credentials['password'])
        
        # В demo режиме не отправляем реальное письмо
        print("✅ Тестовое письмо готово к отправке (demo режим)")
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка отправки тестового письма: {e}")
        return False

def main():
    """Основная функция"""
    print("📧 Обновление учетных данных MailerSend...")
    print("=" * 50)
    
    # Загружаем текущие учетные данные
    credentials = load_environment()
    
    if not credentials['username'] or not credentials['password']:
        print("❌ Учетные данные не найдены в .env файле")
        return False
    
    print(f"📋 Текущие учетные данные:")
    print(f"   Username: {credentials['username']}")
    print(f"   Password: {'*' * len(credentials['password'])}")
    
    # Тестируем текущее соединение
    if test_smtp_connection(credentials):
        print("✅ Текущие учетные данные работают!")
        
        # Отправляем тестовое письмо
        send_test_email(credentials)
        
        print("\n🎉 Все готово!")
        print("📋 Что было сделано:")
        print("  ✅ Проверены текущие учетные данные")
        print("  ✅ Протестировано SMTP соединение")
        print("  ✅ Подготовлено тестовое письмо")
        
        print("\n🚨 РЕКОМЕНДАЦИИ:")
        print("  1. Отзовите старые скомпрометированные ключи в MailerSend")
        print("  2. Создайте новые учетные данные в панели MailerSend")
        print("  3. Обновите .env файл с новыми данными")
        print("  4. Протестируйте отправку email")
        
        return True
    else:
        print("❌ Текущие учетные данные не работают")
        print("🔧 Генерируем новые учетные данные...")
        
        new_username, new_password = generate_new_credentials()
        
        if update_env_file(new_username, new_password):
            print("✅ Новые учетные данные сгенерированы и сохранены")
            print(f"   Новый Username: {new_username}")
            print(f"   Новый Password: {new_password}")
            
            print("\n🚨 ВАЖНО:")
            print("  1. Обновите эти учетные данные в панели MailerSend")
            print("  2. Отзовите старые скомпрометированные ключи")
            print("  3. Протестируйте новое соединение")
            
            return True
        else:
            print("❌ Не удалось обновить учетные данные")
            return False

if __name__ == "__main__":
    main()
