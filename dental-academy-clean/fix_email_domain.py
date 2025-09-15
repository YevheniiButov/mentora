#!/usr/bin/env python3
"""
Quick Fix для проблемы с доменом email
Исправляет несоответствие между mentora.com и mentora.com.in
"""

import os
import re

def fix_env_file():
    """Исправляем .env файл"""
    env_file = '.env'
    
    if not os.path.exists(env_file):
        print("❌ .env файл не найден")
        return False
    
    print("🔧 Исправляем .env файл...")
    
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Исправляем домен
    old_content = content
    content = content.replace('noreply@mentora.com>', 'noreply@mentora.com.in>')
    content = content.replace('MAIL_DEFAULT_SENDER=Mentora <noreply@mentora.com>', 
                             'MAIL_DEFAULT_SENDER=Mentora <noreply@mentora.com.in>')
    
    if content != old_content:
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ .env файл исправлен")
        return True
    else:
        print("ℹ️ .env файл уже корректный")
        return True

def fix_render_yaml():
    """Исправляем render.yaml файл"""
    render_file = 'render.yaml'
    
    if not os.path.exists(render_file):
        print("❌ render.yaml файл не найден")
        return False
    
    print("🔧 Исправляем render.yaml файл...")
    
    with open(render_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Исправляем домен в render.yaml
    old_content = content
    content = content.replace('value: "Mentora <noreply@mentora.com>"', 
                             'value: "Mentora <noreply@mentora.com.in>"')
    
    if content != old_content:
        # Создаем бэкап
        backup_file = f"{render_file}.backup_{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')}"
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(old_content)
        print(f"📁 Создан бэкап: {backup_file}")
        
        # Сохраняем исправленный файл
        with open(render_file, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ render.yaml файл исправлен")
        return True
    else:
        print("ℹ️ render.yaml файл уже корректный")
        return True

def check_email_config():
    """Проверяем текущую конфигурацию email"""
    print("\n📧 Текущая конфигурация email:")
    print("=" * 50)
    
    env_vars = {
        'MAIL_SERVER': os.environ.get('MAIL_SERVER', 'НЕ УСТАНОВЛЕНО'),
        'MAIL_PORT': os.environ.get('MAIL_PORT', 'НЕ УСТАНОВЛЕНО'),
        'MAIL_USE_TLS': os.environ.get('MAIL_USE_TLS', 'НЕ УСТАНОВЛЕНО'),
        'MAIL_USERNAME': os.environ.get('MAIL_USERNAME', 'НЕ УСТАНОВЛЕНО'),
        'MAIL_PASSWORD': '***' if os.environ.get('MAIL_PASSWORD') else 'НЕ УСТАНОВЛЕНО',
        'MAIL_DEFAULT_SENDER': os.environ.get('MAIL_DEFAULT_SENDER', 'НЕ УСТАНОВЛЕНО'),
        'MAIL_SUPPRESS_SEND': os.environ.get('MAIL_SUPPRESS_SEND', 'НЕ УСТАНОВЛЕНО')
    }
    
    for key, value in env_vars.items():
        print(f"{key}: {value}")
    
    print("=" * 50)

def test_email_import():
    """Тестируем импорт email модулей"""
    print("\n🧪 Тестируем импорт email модулей...")
    
    try:
        from flask import Flask
        from flask_mail import Mail, Message
        print("✅ Flask-Mail импортирован успешно")
        
        # Создаем тестовое приложение
        app = Flask(__name__)
        app.config['MAIL_SERVER'] = 'smtp-relay.brevo.com'
        app.config['MAIL_PORT'] = 587
        app.config['MAIL_USE_TLS'] = True
        app.config['MAIL_USERNAME'] = '96d92f002@smtp-brevo.com'
        app.config['MAIL_PASSWORD'] = 'AdHL3pP0rkRt1S8N'
        app.config['MAIL_DEFAULT_SENDER'] = 'noreply@mentora.com.in'
        
        mail = Mail(app)
        print("✅ Mail объект создан успешно")
        
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return False

if __name__ == '__main__':
    print("🦷 Mentora Email Domain Fix")
    print("=" * 50)
    
    # Проверяем текущую конфигурацию
    check_email_config()
    
    # Исправляем файлы
    env_fixed = fix_env_file()
    render_fixed = fix_render_yaml()
    
    # Тестируем импорт
    import_ok = test_email_import()
    
    print("\n📋 Результаты исправления:")
    print("=" * 50)
    print(f"✅ .env файл: {'ИСПРАВЛЕН' if env_fixed else 'ОШИБКА'}")
    print(f"✅ render.yaml: {'ИСПРАВЛЕН' if render_fixed else 'ОШИБКА'}")
    print(f"✅ Email модули: {'РАБОТАЮТ' if import_ok else 'ОШИБКА'}")
    
    if env_fixed and render_fixed and import_ok:
        print("\n🎉 Все исправления завершены успешно!")
        print("\n📋 Следующие шаги:")
        print("1. Перезапустите Flask приложение")
        print("2. Проверьте логи при регистрации")
        print("3. Тестируйте отправку email")
        print("4. В случае проблем в продакшене - обновите Render Environment Variables")
    else:
        print("\n❌ Есть проблемы, которые нужно исправить вручную")
