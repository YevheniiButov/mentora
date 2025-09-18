"""
Admin Email Service
Сервис для отправки email из админ-кабинета
"""

from flask import current_app
from models import User
from utils.email_service import send_email_confirmation
from utils.resend_email_service import send_email_confirmation_resend
import requests
import json

def send_admin_email(user, subject, message, email_type='custom'):
    """
    Отправляет email пользователю из админ-кабинета
    
    Args:
        user: Объект пользователя
        subject: Тема письма
        message: Содержимое письма
        email_type: Тип письма ('custom', 'confirmation', 'notification')
    
    Returns:
        bool: True если письмо отправлено успешно
    """
    try:
        print(f"=== ADMIN EMAIL SENDING to {user.email} ===")
        print(f"=== SUBJECT: {subject} ===")
        print(f"=== TYPE: {email_type} ===")
        
        # Проверяем провайдера email
        email_provider = current_app.config.get('EMAIL_PROVIDER', 'smtp')
        print(f"=== EMAIL_PROVIDER: {email_provider} ===")
        
        if email_provider == 'resend':
            return send_admin_email_resend(user, subject, message, email_type)
        else:
            return send_admin_email_smtp(user, subject, message, email_type)
            
    except Exception as e:
        print(f"=== ADMIN EMAIL ERROR: {str(e)} ===")
        current_app.logger.error(f"Failed to send admin email to {user.email}: {str(e)}")
        return False

def send_admin_email_resend(user, subject, message, email_type):
    """Отправляет email через Resend API"""
    try:
        api_key = current_app.config.get('RESEND_API_KEY')
        from_email = current_app.config.get('RESEND_FROM_EMAIL', 'Mentora <noreply@bigmentor.nl>')
        
        if not api_key:
            print("❌ RESEND_API_KEY not configured")
            return False
        
        # Подготавливаем HTML и текстовое содержимое
        html_content = get_admin_email_html(user, subject, message, email_type)
        text_content = get_admin_email_text(user, subject, message, email_type)
        
        # Данные для Resend API
        email_data = {
            "from": from_email,
            "to": [user.email],
            "subject": subject,
            "html": html_content,
            "text": text_content
        }
        
        # Отправляем через Resend API
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            "https://api.resend.com/emails",
            headers=headers,
            json=email_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Admin email sent successfully via Resend")
            print(f"📧 Email ID: {result.get('id')}")
            current_app.logger.info(f"Admin email sent to {user.email} via Resend. ID: {result.get('id')}")
            return True
        else:
            print(f"❌ Resend API error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Resend API exception: {str(e)}")
        current_app.logger.error(f"Failed to send admin email to {user.email} via Resend: {str(e)}")
        return False

def send_admin_email_smtp(user, subject, message, email_type):
    """Отправляет email через SMTP (fallback)"""
    try:
        from flask_mail import Message
        from extensions import mail
        
        # Проверяем, отключена ли отправка email
        mail_suppress = current_app.config.get('MAIL_SUPPRESS_SEND', False)
        
        if mail_suppress:
            # Development mode - console output
            print(f"\n{'='*60}")
            print(f"📧 ADMIN EMAIL for {user.email}")
            print(f"{'='*60}")
            print(f"👤 User: {user.first_name} {user.last_name}")
            print(f"📧 Email: {user.email}")
            print(f"📝 Subject: {subject}")
            print(f"📄 Message: {message}")
            print(f"🏷️ Type: {email_type}")
            print(f"{'='*60}\n")
            return True
        
        # Создаем сообщение
        msg = Message(
            subject=subject,
            recipients=[user.email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # HTML и текстовое содержимое
        msg.html = get_admin_email_html(user, subject, message, email_type)
        msg.body = get_admin_email_text(user, subject, message, email_type)
        
        # Отправляем email
        mail.send(msg)
        print(f"✅ Admin email sent successfully via SMTP")
        current_app.logger.info(f"Admin email sent to {user.email} via SMTP")
        return True
        
    except Exception as e:
        print(f"❌ SMTP error: {str(e)}")
        current_app.logger.error(f"Failed to send admin email to {user.email} via SMTP: {str(e)}")
        return False

def get_admin_email_html(user, subject, message, email_type):
    """Генерирует HTML содержимое для admin email"""
    base_url = current_app.config.get('BASE_URL', 'https://bigmentor.nl')
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{subject}</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background-color: #3ECDC1; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 20px; background-color: #f9f9f9; }}
            .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
            .message {{ background-color: white; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Mentora</h1>
                <p>Стоматологическая академия</p>
            </div>
            <div class="content">
                <h2>Здравствуйте, {user.first_name}!</h2>
                <div class="message">
                    {message.replace(chr(10), '<br>')}
                </div>
                <p>С уважением,<br>Команда Mentora</p>
            </div>
            <div class="footer">
                <p>Это письмо отправлено из административной панели Mentora</p>
                <p><a href="{base_url}">Перейти на сайт</a></p>
            </div>
        </div>
    </body>
    </html>
    """

def get_admin_email_text(user, subject, message, email_type):
    """Генерирует текстовое содержимое для admin email"""
    return f"""
Здравствуйте, {user.first_name}!

{message}

С уважением,
Команда Mentora

---
Это письмо отправлено из административной панели Mentora
"""

def send_bulk_admin_emails(users, subject, message, email_type='custom'):
    """
    Отправляет email нескольким пользователям
    
    Args:
        users: Список объектов пользователей
        subject: Тема письма
        message: Содержимое письма
        email_type: Тип письма
    
    Returns:
        dict: Результат отправки {'sent': int, 'failed': int, 'errors': list}
    """
    result = {'sent': 0, 'failed': 0, 'errors': []}
    
    for user in users:
        if user and user.email:
            try:
                success = send_admin_email(user, subject, message, email_type)
                if success:
                    result['sent'] += 1
                else:
                    result['failed'] += 1
                    result['errors'].append(f"Failed to send to {user.email}")
            except Exception as e:
                result['failed'] += 1
                result['errors'].append(f"Error sending to {user.email}: {str(e)}")
    
    return result
