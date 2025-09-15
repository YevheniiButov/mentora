#!/usr/bin/env python3
"""
QUICK FIX для email регистрации
Временная замена send_email_confirmation на прямую отправку
"""

def create_quick_fix():
    """Создает временное решение"""
    
    quick_fix_code = '''
# QUICK FIX - Замена для send_email_confirmation в auth_routes.py
# Вставьте этот код вместо вызова send_email_confirmation

try:
    print("=== QUICK FIX: Прямая отправка email подтверждения ===")
    
    from flask_mail import Message
    from extensions import mail
    from flask import current_app
    
    # Генерируем URL подтверждения
    base_url = current_app.config.get('BASE_URL', 'https://mentora.com.in')
    confirmation_url = f"{base_url}/auth/confirm-email/{confirmation_token}"
    
    # Создаем сообщение (как в test-email)
    msg = Message(
        subject='🦷 Mentora - Подтверждение регистрации',
        recipients=[user.email],
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    
    # Простой HTML контент
    msg.html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #3ECDC1, #2DB5A9); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="margin: 0;">🦷 Mentora</h1>
            <p style="margin: 10px 0 0 0;">Система обучения медицинских работников</p>
        </div>
        
        <div style="background: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h2>Подтверждение регистрации</h2>
            
            <p>Здравствуйте, <strong>{user.first_name}</strong>!</p>
            
            <p>Благодарим за регистрацию в Mentora. Для активации аккаунта подтвердите ваш email адрес:</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{confirmation_url}" 
                   style="background: linear-gradient(135deg, #3ECDC1, #2DB5A9); color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">
                    Подтвердить Email
                </a>
            </div>
            
            <p style="color: #666; font-size: 14px;">
                Если кнопка не работает, скопируйте эту ссылку в браузер:<br>
                <span style="word-break: break-all;">{confirmation_url}</span>
            </p>
            
            <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
            
            <p style="color: #666; font-size: 12px; text-align: center;">
                Если вы не регистрировались в Mentora, просто проигнорируйте это письмо.
            </p>
        </div>
    </body>
    </html>
    """
    
    # Текстовая версия
    msg.body = f"""
Mentora - Подтверждение регистрации

Здравствуйте, {user.first_name}!

Благодарим за регистрацию в Mentora. Для активации аккаунта подтвердите ваш email адрес:

{confirmation_url}

Если вы не регистрировались в Mentora, просто проигнорируйте это письмо.

С уважением,
Команда Mentora
    """
    
    # Отправляем
    print(f"📧 Отправляем на: {user.email}")
    mail.send(msg)
    print("✅ QUICK FIX: Email отправлен успешно!")
    
    email_sent = True
    
except Exception as e:
    print(f"❌ QUICK FIX ERROR: {e}")
    import traceback
    print(f"📋 TRACEBACK: {traceback.format_exc()}")
    email_sent = False
'''
    
    return quick_fix_code

def show_implementation_steps():
    """Показывает шаги для применения quick fix"""
    
    print("🚀 QUICK FIX IMPLEMENTATION")
    print("=" * 50)
    
    print("📝 ШАГ 1: Найти в auth_routes.py строки:")
    print("   from utils.email_service import send_email_confirmation")
    print("   email_sent = send_email_confirmation(user, confirmation_token)")
    print()
    
    print("📝 ШАГ 2: Заменить на код выше")
    print()
    
    print("📝 ШАГ 3: Перезапустить приложение")
    print()
    
    print("📝 ШАГ 4: Тестировать регистрацию")
    print()
    
    print("⚠️ ВАЖНО:")
    print("• Это временное решение")
    print("• После исправления send_email_confirmation вернуть обратно")
    print("• Код проще чем send_email_confirmation, меньше точек отказа")

if __name__ == '__main__':
    print("🦷 Mentora Email Quick Fix Generator")
    print("=" * 50)
    
    # Создаем quick fix код
    fix_code = create_quick_fix()
    
    # Сохраняем в файл
    with open('email_quick_fix_code.txt', 'w', encoding='utf-8') as f:
        f.write(fix_code)
    
    print("✅ Quick fix код сохранен в email_quick_fix_code.txt")
    print()
    
    # Показываем шаги
    show_implementation_steps()
    
    print("\n🎯 РЕЗУЛЬТАТ:")
    print("• Убираем сложную логику send_email_confirmation")
    print("• Используем простую прямую отправку")
    print("• Как в test-email, который работает")
    print("• Легче отлаживать")
