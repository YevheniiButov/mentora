#!/usr/bin/env python3
"""
Тест аутентификации Brevo
Проверяет правильность учетных данных
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_brevo_credentials():
    """Тестирует учетные данные Brevo"""
    print("🔐 Тест аутентификации Brevo")
    print("=" * 50)
    
    # Настройки из render.yaml
    smtp_server = 'smtp-relay.brevo.com'
    smtp_port = 587
    username = '96d92f001@smtp-brevo.com'
    password = 'JrbVFGpHhgynKMOQ'
    
    print(f"Сервер: {smtp_server}")
    print(f"Порт: {smtp_port}")
    print(f"Пользователь: {username}")
    print(f"Пароль: {'*' * len(password)}")
    
    try:
        print("\n🔄 Подключение к SMTP серверу...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        
        # Включаем debug режим для детальной информации
        server.set_debuglevel(1)
        
        print("🔄 Инициализация TLS...")
        server.starttls()
        
        print("🔄 Аутентификация...")
        server.login(username, password)
        
        print("✅ Успешная аутентификация!")
        
        # Создаем тестовое письмо
        msg = MIMEMultipart()
        msg['From'] = 'noreply@mentora.com'
        msg['To'] = 'xapstom@gmail.com'
        msg['Subject'] = 'Brevo Auth Test'
        
        body = """
Тест аутентификации Brevo

Если вы получили это письмо, значит:
✅ SMTP сервер работает
✅ Аутентификация прошла успешно
✅ Учетные данные корректны

Настройки:
- Сервер: smtp-relay.brevo.com
- Порт: 587
- TLS: Включен

С уважением,
Система тестирования Mentora
        """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        print("📧 Отправка тестового письма...")
        server.send_message(msg)
        
        print("✅ Письмо отправлено успешно!")
        
        server.quit()
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ Ошибка аутентификации: {e}")
        print("🔍 Возможные причины:")
        print("1. Неправильный логин или пароль")
        print("2. Аккаунт заблокирован")
        print("3. Нужно сгенерировать новый SMTP пароль в Brevo")
        return False
        
    except smtplib.SMTPConnectError as e:
        print(f"❌ Ошибка подключения: {e}")
        print("🔍 Проверьте сервер и порт")
        return False
        
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

def test_alternative_credentials():
    """Тестирует альтернативные учетные данные"""
    print("\n🔄 Тест альтернативных учетных данных")
    print("=" * 50)
    
    # Альтернативные настройки (если основные не работают)
    alternatives = [
        {
            'name': 'Основные (из render.yaml)',
            'server': 'smtp-relay.brevo.com',
            'port': 587,
            'username': '96d92f001@smtp-brevo.com',
            'password': 'JrbVFGpHhgynKMOQ'
        },
        {
            'name': 'Альтернативные (если есть)',
            'server': 'smtp-relay.brevo.com',
            'port': 587,
            'username': '96d92f002@smtp-brevo.com',
            'password': 'AdHL3pP0rkRt1S8N'
        }
    ]
    
    for creds in alternatives:
        print(f"\n🧪 Тестирование: {creds['name']}")
        print(f"Пользователь: {creds['username']}")
        
        try:
            server = smtplib.SMTP(creds['server'], creds['port'])
            server.starttls()
            server.login(creds['username'], creds['password'])
            print(f"✅ {creds['name']} - аутентификация успешна!")
            server.quit()
            return creds
        except Exception as e:
            print(f"❌ {creds['name']} - ошибка: {e}")
    
    return None

if __name__ == '__main__':
    print("🦷 Brevo Authentication Test")
    print("=" * 50)
    
    # Тестируем основные учетные данные
    success = test_brevo_credentials()
    
    if not success:
        # Тестируем альтернативные
        working_creds = test_alternative_credentials()
        
        if working_creds:
            print(f"\n✅ Найдены рабочие учетные данные: {working_creds['name']}")
            print("Обновите настройки в .env и render.yaml")
        else:
            print("\n❌ Ни один набор учетных данных не работает")
            print("Проверьте настройки в Brevo панели")
    else:
        print("\n🎉 Основные учетные данные работают!")
