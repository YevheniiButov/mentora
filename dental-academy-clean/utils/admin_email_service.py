"""
Admin Email Service
Сервис для отправки email из админ-кабинета
"""

from flask import current_app, render_template
from models import User
from utils.email_service import send_email_confirmation
from utils.resend_email_service import send_email_confirmation_resend
import requests
import json

def send_admin_email(user, subject, message, email_type='custom', **kwargs):
    """
    Отправляет email пользователю из админ-кабинета
    
    Args:
        user: Объект пользователя
        subject: Тема письма
        message: Содержимое письма
        email_type: Тип письма ('custom', 'confirmation', 'notification', 'password_reset')
        **kwargs: Дополнительные параметры для шаблонов
    
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
            return send_admin_email_resend(user, subject, message, email_type, **kwargs)
        else:
            return send_admin_email_smtp(user, subject, message, email_type, **kwargs)
            
    except Exception as e:
        print(f"=== ADMIN EMAIL ERROR: {str(e)} ===")
        current_app.logger.error(f"Failed to send admin email to {user.email}: {str(e)}")
        return False

def send_admin_email_resend(user, subject, message, email_type, **kwargs):
    """Отправляет email через Resend API"""
    try:
        api_key = current_app.config.get('RESEND_API_KEY')
        from_email = current_app.config.get('RESEND_FROM_EMAIL', 'Mentora <noreply@bigmentor.nl>')
        
        if not api_key:
            print("❌ RESEND_API_KEY not configured")
            return False
        
        # Подготавливаем HTML и текстовое содержимое
        html_content = get_admin_email_html(user, subject, message, email_type, **kwargs)
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

def send_admin_email_smtp(user, subject, message, email_type, **kwargs):
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
        msg.html = get_admin_email_html(user, subject, message, email_type, **kwargs)
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

def get_admin_email_html(user, subject, message, email_type, **kwargs):
    """Генерирует HTML содержимое для admin email используя шаблоны"""
    base_url = current_app.config.get('BASE_URL', 'https://bigmentor.nl')
    
    # Выбираем шаблон в зависимости от типа письма
    if email_type == 'password_reset':
        template = 'emails/admin_password_reset.html'
        template_vars = {
            'user': user,
            'subject': subject,
            'message': message,
            'temp_password': kwargs.get('temp_password', ''),
            'login_url': f"{base_url}/auth/login"
        }
    elif email_type == 'notification':
        template = 'emails/admin_notification.html'
        template_vars = {
            'user': user,
            'subject': subject,
            'message': message,
            'notification_type': kwargs.get('notification_type', 'custom'),
            'action_url': kwargs.get('action_url'),
            'action_text': kwargs.get('action_text')
        }
    else:  # custom
        template = 'emails/admin_custom.html'
        template_vars = {
            'user': user,
            'subject': subject,
            'message': message,
            'action_url': kwargs.get('action_url'),
            'action_text': kwargs.get('action_text')
        }
    
    try:
        return render_template(template, **template_vars)
    except Exception as e:
        print(f"Template rendering error: {e}")
        # Fallback to simple HTML
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>{subject}</title>
        </head>
        <body>
            <h1>Mentora</h1>
            <h2>Здравствуйте, {user.first_name}!</h2>
            <p>{message.replace(chr(10), '<br>')}</p>
            <p>С уважением,<br>Команда Mentora</p>
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

def send_bulk_admin_emails(users, subject, message, email_type='custom', **kwargs):
    """
    Отправляет email нескольким пользователям
    
    Args:
        users: Список объектов пользователей
        subject: Тема письма
        message: Содержимое письма
        email_type: Тип письма
        **kwargs: Дополнительные параметры для шаблонов
    
    Returns:
        dict: Результат отправки {'sent': int, 'failed': int, 'errors': list}
    """
    result = {'sent': 0, 'failed': 0, 'errors': []}
    
    for user in users:
        if user and user.email:
            try:
                success = send_admin_email(user, subject, message, email_type, **kwargs)
                if success:
                    result['sent'] += 1
                else:
                    result['failed'] += 1
                    result['errors'].append(f"Failed to send to {user.email}")
            except Exception as e:
                result['failed'] += 1
                result['errors'].append(f"Error sending to {user.email}: {str(e)}")
    
    return result

def send_password_reset_email(user, temp_password):
    """
    Отправляет email с новым паролем пользователю
    
    Args:
        user: Объект пользователя
        temp_password: Временный пароль
    
    Returns:
        bool: True если письмо отправлено успешно
    """
    subject = "Mentora - Новый пароль"
    message = "Ваш пароль был сброшен администратором."
    
    return send_admin_email(
        user, 
        subject, 
        message, 
        'password_reset', 
        temp_password=temp_password
    )

def send_notification_email(user, subject, message, notification_type='custom', action_url=None, action_text=None):
    """
    Отправляет уведомление пользователю
    
    Args:
        user: Объект пользователя
        subject: Тема письма
        message: Содержимое письма
        notification_type: Тип уведомления ('system_update', 'maintenance', 'feature', 'custom')
        action_url: URL для кнопки действия
        action_text: Текст кнопки действия
    
    Returns:
        bool: True если письмо отправлено успешно
    """
    return send_admin_email(
        user, 
        subject, 
        message, 
        'notification', 
        notification_type=notification_type,
        action_url=action_url,
        action_text=action_text
    )

def send_custom_email(user, subject, message, action_url=None, action_text=None):
    """
    Отправляет кастомное письмо пользователю
    
    Args:
        user: Объект пользователя
        subject: Тема письма
        message: Содержимое письма
        action_url: URL для кнопки действия
        action_text: Текст кнопки действия
    
    Returns:
        bool: True если письмо отправлено успешно
    """
    return send_admin_email(
        user, 
        subject, 
        message, 
        'custom', 
        action_url=action_url,
        action_text=action_text
    )
