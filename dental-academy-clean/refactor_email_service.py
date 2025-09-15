#!/usr/bin/env python3
"""
РЕФАКТОРИНГ email_service.py
Переписываем на прямую отправку для надежности
"""

email_service_refactored = '''
# utils/email_service.py - Simplified Email Service with Direct Sending

from flask import current_app
from flask_mail import Mail, Message
from extensions import mail

def send_email_confirmation(user, token):
    """Send email confirmation using direct method (reliable)"""
    try:
        print(f"=== EMAIL CONFIRMATION START for {user.email} ===")
        
        # Generate confirmation URL
        base_url = current_app.config.get('BASE_URL', 'https://mentora.com.in')
        confirmation_url = f"{base_url}/auth/confirm-email/{token}"
        
        print(f"=== CONFIRMATION_URL: {confirmation_url} ===")
        
        # Check if email sending is suppressed
        mail_suppress = current_app.config.get('MAIL_SUPPRESS_SEND', False)
        print(f"=== MAIL_SUPPRESS_SEND: {mail_suppress} ===")
        
        if mail_suppress:
            # Development mode - console output
            print(f"\\n{'='*60}")
            print(f"📧 EMAIL CONFIRMATION для {user.email}")
            print(f"{'='*60}")
            print(f"👤 Пользователь: {user.first_name} {user.last_name}")
            print(f"📧 Email: {user.email}")
            print(f"🔗 Ссылка подтверждения: {confirmation_url}")
            print(f"{'='*60}\\n")
            
            current_app.logger.info(f"Email confirmation (console mode) for {user.email}")
            return True
        
        print("=== PRODUCTION MODE - SENDING REAL EMAIL ===")
        
        # Create message
        msg = Message(
            subject='🦷 Mentora - Подтверждение регистрации',
            recipients=[user.email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # HTML content (inline for reliability)
        msg.html = get_confirmation_email_html(user, confirmation_url)
        
        # Text content (inline for reliability)  
        msg.body = get_confirmation_email_text(user, confirmation_url)
        
        # Send email
        print("=== ATTEMPTING TO SEND EMAIL ===")
        mail.send(msg)
        print("=== EMAIL SENT SUCCESSFULLY ===")
        
        current_app.logger.info(f"Email confirmation sent to {user.email}")
        return True
        
    except Exception as e:
        print(f"=== EMAIL CONFIRMATION ERROR: {str(e)} ===")
        print(f"=== ERROR TYPE: {type(e).__name__} ===")
        import traceback
        print(f"=== TRACEBACK: {traceback.format_exc()} ===")
        
        current_app.logger.error(f"Failed to send email confirmation to {user.email}: {str(e)}")
        return False

def get_confirmation_email_html(user, confirmation_url):
    """Generate HTML content for confirmation email"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Email Confirmation - Mentora</title>
    </head>
    <body style="font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #3ECDC1, #2DB5A9); color: white; padding: 40px 30px; text-align: center;">
                <h1 style="margin: 0; font-size: 32px; font-weight: bold;">🦷 Mentora</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Система обучения медицинских работников</p>
            </div>
            
            <!-- Content -->
            <div style="padding: 40px 30px;">
                <h2 style="color: #2d3748; margin-top: 0; font-size: 24px;">Подтверждение регистрации</h2>
                
                <p style="color: #4a5568; font-size: 16px; line-height: 1.6;">
                    Здравствуйте, <strong>{user.first_name}</strong>!
                </p>
                
                <p style="color: #4a5568; font-size: 16px; line-height: 1.6;">
                    Благодарим за регистрацию в системе Mentora. Для завершения регистрации и активации вашего аккаунта, пожалуйста, подтвердите ваш email адрес.
                </p>
                
                <!-- CTA Button -->
                <div style="text-align: center; margin: 40px 0;">
                    <a href="{confirmation_url}" 
                       style="background: linear-gradient(135deg, #3ECDC1, #2DB5A9); 
                              color: white; 
                              padding: 16px 32px; 
                              text-decoration: none; 
                              border-radius: 8px; 
                              font-weight: bold; 
                              font-size: 16px;
                              display: inline-block;
                              box-shadow: 0 4px 12px rgba(62, 205, 193, 0.3);">
                        ✅ Подтвердить Email
                    </a>
                </div>
                
                <!-- Alternative link -->
                <div style="background-color: #f7fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin: 30px 0;">
                    <p style="color: #4a5568; font-size: 14px; margin: 0 0 10px 0;">
                        <strong>Если кнопка не работает,</strong> скопируйте и вставьте эту ссылку в адресную строку браузера:
                    </p>
                    <p style="color: #3182ce; font-size: 14px; word-break: break-all; margin: 0; font-family: monospace; background: white; padding: 10px; border-radius: 4px;">
                        {confirmation_url}
                    </p>
                </div>
                
                <!-- Important note -->
                <div style="background-color: #fef5e7; border-left: 4px solid #f6ad55; padding: 15px; margin: 20px 0;">
                    <p style="color: #744210; font-size: 14px; margin: 0;">
                        <strong>Важно:</strong> Ссылка действительна в течение 24 часов. После этого потребуется запросить новую ссылку для подтверждения.
                    </p>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background-color: #f7fafc; padding: 30px; text-align: center; border-top: 1px solid #e2e8f0;">
                <p style="color: #718096; font-size: 14px; margin: 0 0 15px 0;">
                    Если вы не регистрировались в Mentora, просто проигнорируйте это письмо.
                </p>
                
                <p style="color: #4a5568; font-size: 14px; margin: 0;">
                    <strong>Mentora</strong><br>
                    Email: <a href="mailto:support@mentora.com.in" style="color: #3182ce;">support@mentora.com.in</a><br>
                    Website: <a href="https://mentora.com.in" style="color: #3182ce;">mentora.com.in</a>
                </p>
                
                <p style="color: #a0aec0; font-size: 12px; margin: 20px 0 0 0;">
                    © 2024 Mentora. Все права защищены.
                </p>
            </div>
        </div>
    </body>
    </html>
    """

def get_confirmation_email_text(user, confirmation_url):
    """Generate text content for confirmation email"""
    return f"""
MENTORA - Подтверждение регистрации

Здравствуйте, {user.first_name}!

Благодарим за регистрацию в системе Mentora. Для завершения регистрации и активации вашего аккаунта, пожалуйста, подтвердите ваш email адрес.

Ссылка для подтверждения:
{confirmation_url}

ВАЖНО: Ссылка действительна в течение 24 часов.

Если вы не регистрировались в Mentora, просто проигнорируйте это письмо.

---
С уважением,
Команда Mentora

Email: support@mentora.com.in
Website: https://mentora.com.in

© 2024 Mentora. Все права защищены.
    """

def send_password_reset_email(user, token):
    """Send password reset email using direct method"""
    try:
        print(f"=== PASSWORD RESET START for {user.email} ===")
        
        # Generate reset URL
        base_url = current_app.config.get('BASE_URL', 'https://mentora.com.in')
        reset_url = f"{base_url}/auth/reset-password/{token}"
        
        # Check if suppressed
        if current_app.config.get('MAIL_SUPPRESS_SEND', False):
            print(f"\\n{'='*60}")
            print(f"🔐 PASSWORD RESET для {user.email}")
            print(f"🔗 Ссылка: {reset_url}")
            print(f"{'='*60}\\n")
            return True
        
        # Create message
        msg = Message(
            subject='🔐 Mentora - Сброс пароля',
            recipients=[user.email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # HTML content
        msg.html = get_password_reset_html(user, reset_url)
        msg.body = get_password_reset_text(user, reset_url)
        
        # Send
        mail.send(msg)
        
        current_app.logger.info(f"Password reset email sent to {user.email}")
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send password reset to {user.email}: {str(e)}")
        return False

def get_password_reset_html(user, reset_url):
    """Generate HTML for password reset email"""
    return f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #3ECDC1, #2DB5A9); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
            <h1 style="margin: 0;">🦷 Mentora</h1>
            <p style="margin: 10px 0 0 0;">Сброс пароля</p>
        </div>
        
        <div style="background: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h2>Сброс пароля</h2>
            
            <p>Здравствуйте, <strong>{user.first_name}</strong>!</p>
            
            <p>Вы запросили сброс пароля для вашего аккаунта в Mentora.</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" 
                   style="background: linear-gradient(135deg, #3ECDC1, #2DB5A9); color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">
                    🔐 Сбросить пароль
                </a>
            </div>
            
            <p style="color: #666; font-size: 14px;">
                Ссылка действительна 1 час. Если вы не запрашивали сброс пароля, проигнорируйте это письмо.
            </p>
        </div>
    </body>
    </html>
    """

def get_password_reset_text(user, reset_url):
    """Generate text for password reset email"""
    return f"""
MENTORA - Сброс пароля

Здравствуйте, {user.first_name}!

Вы запросили сброс пароля для вашего аккаунта в Mentora.

Ссылка для сброса пароля:
{reset_url}

Ссылка действительна 1 час.

Если вы не запрашивали сброс пароля, проигнорируйте это письмо.

---
С уважением,
Команда Mentora
    """

def send_welcome_email(user):
    """Send welcome email after confirmation"""
    try:
        if current_app.config.get('MAIL_SUPPRESS_SEND', False):
            print(f"Welcome email (console) for {user.email}")
            return True
        
        msg = Message(
            subject='🎉 Добро пожаловать в Mentora!',
            recipients=[user.email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        msg.html = f"""
        <h1>🎉 Добро пожаловать, {user.first_name}!</h1>
        <p>Ваш аккаунт успешно активирован!</p>
        <p><a href="https://mentora.com.in/dashboard">Перейти в дашборд</a></p>
        """
        
        msg.body = f"Добро пожаловать, {user.first_name}! Ваш аккаунт активирован."
        
        mail.send(msg)
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send welcome email: {str(e)}")
        return False
'''

print("📧 РЕФАКТОРИНГ email_service.py")
print("=" * 50)

print("✅ ПРЕИМУЩЕСТВА НОВОГО ПОДХОДА:")
print("• Все email контент в одном файле")
print("• Нет зависимости от template файлов")
print("• Легко отлаживать и модифицировать")
print("• Красивый HTML все еще возможен")
print("• Функции разделены по типам email")
print("• Консистентная обработка ошибок")

print("\n🎨 СТРУКТУРА:")
print("• send_email_confirmation() - основная функция")
print("• get_confirmation_email_html() - HTML контент")
print("• get_confirmation_email_text() - текстовый контент")
print("• Аналогично для других типов писем")

print("\n🔧 КАК ПРИМЕНИТЬ:")
print("1. Замени содержимое utils/email_service.py на код выше")
print("2. Перезапусти приложение")
print("3. Тестируй регистрацию")

print("\n💡 РЕЗУЛЬТАТ:")
print("• Надежная отправка email")
print("• Красивый дизайн писем")
print("• Легкая поддержка")
print("• Нет проблем с шаблонами")

return email_service_refactored
