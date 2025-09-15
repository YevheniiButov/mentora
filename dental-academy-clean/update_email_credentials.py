#!/usr/bin/env python3
"""
Обновление учетных данных email
Обновляет .env файл с рабочими учетными данными Brevo
"""

import os
import shutil
from datetime import datetime

def backup_files():
    """Создает резервные копии файлов"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Резервная копия .env
    if os.path.exists('.env'):
        shutil.copy2('.env', f'.env.backup_{timestamp}')
        print(f"✅ Создана резервная копия .env: .env.backup_{timestamp}")
    
    # Резервная копия render.yaml
    if os.path.exists('render.yaml'):
        shutil.copy2('render.yaml', f'render.yaml.backup_{timestamp}')
        print(f"✅ Создана резервная копия render.yaml: render.yaml.backup_{timestamp}")

def update_env_file():
    """Обновляет .env файл с рабочими учетными данными"""
    print("\n🔧 Обновление .env файла...")
    
    # Читаем текущий .env файл
    with open('.env', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Обновляем учетные данные
    content = content.replace(
        'MAIL_USERNAME=96d92f001@smtp-brevo.com',
        'MAIL_USERNAME=96d92f002@smtp-brevo.com'
    )
    content = content.replace(
        'MAIL_PASSWORD=JrbVFGpHhgynKMOQ',
        'MAIL_PASSWORD=AdHL3pP0rkRt1S8N'
    )
    
    # Записываем обновленный файл
    with open('.env', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ .env файл обновлен с рабочими учетными данными")

def update_render_yaml():
    """Обновляет render.yaml с рабочими учетными данными"""
    print("\n🔧 Обновление render.yaml...")
    
    # Читаем текущий render.yaml файл
    with open('render.yaml', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Обновляем учетные данные
    content = content.replace(
        'value: "96d92f001@smtp-brevo.com"',
        'value: "96d92f002@smtp-brevo.com"'
    )
    content = content.replace(
        'value: "JrbVFGpHhgynKMOQ"',
        'value: "AdHL3pP0rkRt1S8N"'
    )
    
    # Записываем обновленный файл
    with open('render.yaml', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ render.yaml обновлен с рабочими учетными данными")

def test_updated_credentials():
    """Тестирует обновленные учетные данные"""
    print("\n🧪 Тестирование обновленных учетных данных...")
    
    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        # Обновленные настройки
        smtp_server = 'smtp-relay.brevo.com'
        smtp_port = 587
        username = '96d92f002@smtp-brevo.com'
        password = 'AdHL3pP0rkRt1S8N'
        
        print(f"Сервер: {smtp_server}")
        print(f"Пользователь: {username}")
        
        # Тестируем соединение
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(username, password)
        print("✅ Аутентификация успешна!")
        
        # Создаем тестовое письмо
        msg = MIMEMultipart()
        msg['From'] = 'noreply@mentora.com'
        msg['To'] = 'xapstom@gmail.com'
        msg['Subject'] = 'Mentora Email Fix - Test'
        
        body = """
Тест обновленных учетных данных Brevo

Если вы получили это письмо, значит:
✅ Учетные данные обновлены корректно
✅ SMTP сервер работает
✅ Аутентификация прошла успешно
✅ Email отправка работает

Настройки:
- Сервер: smtp-relay.brevo.com
- Пользователь: 96d92f002@smtp-brevo.com
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
        
    except Exception as e:
        print(f"❌ Ошибка при тестировании: {e}")
        return False

def main():
    print("🦷 Обновление учетных данных email")
    print("=" * 50)
    
    # Создаем резервные копии
    backup_files()
    
    # Обновляем файлы
    update_env_file()
    update_render_yaml()
    
    # Тестируем обновленные учетные данные
    success = test_updated_credentials()
    
    if success:
        print("\n🎉 Учетные данные успешно обновлены!")
        print("Теперь можно тестировать отправку писем через Flask приложение.")
        print("\n📋 Следующие шаги:")
        print("1. Запустить тест Flask приложения: python3 test_flask_email.py")
        print("2. Протестировать регистрацию пользователя")
        print("3. Задеплоить изменения в продакшен")
    else:
        print("\n❌ Ошибка при обновлении учетных данных")
        print("Проверьте настройки в Brevo панели")

if __name__ == '__main__':
    main()
