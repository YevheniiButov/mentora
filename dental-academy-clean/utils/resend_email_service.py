# utils/resend_email_service.py
"""
Resend Email Service for Mentora
Использует Resend API для отправки email подтверждений
"""

import requests
import json
from datetime import datetime
from flask import current_app
from models import User
from utils.email_service import get_confirmation_email_html, get_confirmation_email_text, get_invitation_with_password_html, get_invitation_with_password_text
# Токены генерируются в модели User

def send_email_confirmation_resend(user, temp_password=None, token=None):
    """
    Отправляет email подтверждение через Resend API
    """
    try:
        # Используем переданный токен или генерируем новый
        if not token:
            token = user.generate_email_confirmation_token()
        
        confirmation_url = f"{current_app.config.get('BASE_URL', 'https://bigmentor.nl')}/auth/confirm-email/{token}"
        
        print(f"=== RESEND EMAIL CONFIRMATION for {user.email} ===")
        print(f"=== CONFIRMATION_URL: {confirmation_url} ===")
        print(f"=== TEMP_PASSWORD: {temp_password} ===")
        
        # Проверяем, отключена ли отправка email
        mail_suppress = current_app.config.get('MAIL_SUPPRESS_SEND', False)
        print(f"=== MAIL_SUPPRESS_SEND: {mail_suppress} ===")
        
        if mail_suppress:
            # Development mode - console output
            print(f"\n{'='*60}")
            print(f"📧 EMAIL CONFIRMATION for {user.email}")
            print(f"{'='*60}")
            print(f"👤 User: {user.first_name} {user.last_name}")
            print(f"📧 Email: {user.email}")
            if temp_password:
                print(f"🔑 Temporary Password: {temp_password}")
            print(f"🔗 Confirmation link: {confirmation_url}")
            print(f"⏰ Token valid for: 24 hours")
            print(f"{'='*60}")
            print(f"💡 Copy the link above and open in browser to confirm")
            if temp_password:
                print(f"🔑 User can login with email and password: {temp_password}")
            print(f"{'='*60}\n")
            
            current_app.logger.info(f"Email confirmation (console mode) for {user.email}")
            return True
        
        # Получаем настройки Resend
        api_key = current_app.config.get('RESEND_API_KEY')
        from_email = current_app.config.get('RESEND_FROM_EMAIL', 'Mentora <info@bigmentor.nl>')
        
        if not api_key:
            print("❌ RESEND_API_KEY not configured")
            return False
        
        print("=== PRODUCTION MODE - SENDING REAL EMAIL VIA RESEND ===")
        
        # Подготавливаем данные для Resend API
        # Проверка совместимости для старой/новой версии функций
        try:
            # Попытка с новой сигнатурой (3 аргумента)
            html_content = get_confirmation_email_html(user, confirmation_url, temp_password)
            text_content = get_confirmation_email_text(user, confirmation_url, temp_password)
        except TypeError:
            # Fallback для старой сигнатуры (2 аргумента)
            print("=== USING OLD SIGNATURE FALLBACK ===")
            html_content = get_confirmation_email_html(user, confirmation_url)
            text_content = get_confirmation_email_text(user, confirmation_url)
        
        email_data = {
            "from": from_email,
            "to": [user.email],
            "subject": "MENTORA - Email Confirmation",
            "html": html_content,
            "text": text_content,
            "click_tracking": False,  # Отключаем click tracking для лучшей доставляемости
            "open_tracking": False   # Отключаем open tracking для лучшей доставляемости
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
            print(f"✅ Email sent successfully via Resend")
            print(f"📧 Email ID: {result.get('id')}")
            current_app.logger.info(f"Email confirmation sent to {user.email} via Resend")
            return True
        else:
            print(f"❌ Resend API error: {response.status_code}")
            print(f"❌ Response: {response.text}")
            current_app.logger.error(f"Resend API error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"=== RESEND EMAIL CONFIRMATION ERROR: {str(e)} ===")
        print(f"=== ERROR TYPE: {type(e).__name__} ===")
        import traceback
        traceback.print_exc()
        current_app.logger.error(f"Resend email confirmation error: {str(e)}", exc_info=True)
        return False


def send_invitation_with_password_resend(user, temp_password, token):
    """
    Отправляет приглашение с паролем через Resend API
    """
    try:
        confirmation_url = f"{current_app.config.get('BASE_URL', 'https://bigmentor.nl')}/auth/confirm-email/{token}"
        
        print(f"=== RESEND INVITATION WITH PASSWORD for {user.email} ===")
        print(f"=== CONFIRMATION_URL: {confirmation_url} ===")
        print(f"=== TEMP_PASSWORD: {temp_password} ===")
        
        # Проверяем, отключена ли отправка email
        mail_suppress = current_app.config.get('MAIL_SUPPRESS_SEND', False)
        print(f"=== MAIL_SUPPRESS_SEND: {mail_suppress} ===")
        
        if mail_suppress:
            # Development mode - console output
            print(f"\n{'='*60}")
            print(f"📧 INVITATION WITH PASSWORD for {user.email}")
            print(f"{'='*60}")
            print(f"Subject: Welcome to Mentora - Your Account Details")
            print(f"To: {user.email}")
            print(f"Confirmation URL: {confirmation_url}")
            print(f"Temporary Password: {temp_password}")
            print(f"{'='*60}")
            return True
        
        # Получаем API ключ
        api_key = current_app.config.get('RESEND_API_KEY')
        if not api_key:
            print("❌ RESEND_API_KEY not configured")
            return False
        
        print("=== PRODUCTION MODE - SENDING REAL EMAIL VIA RESEND ===")
        
        # Подготавливаем данные для Resend API
        # Проверка совместимости для старой/новой версии функций
        try:
            # Попытка с новой сигнатурой (3 аргумента)
            html_content = get_invitation_with_password_html(user, confirmation_url, temp_password)
            text_content = get_invitation_with_password_text(user, confirmation_url, temp_password)
        except TypeError:
            # Fallback для старой сигнатуры (2 аргумента)
            print("=== USING OLD SIGNATURE FALLBACK ===")
            html_content = get_invitation_with_password_html(user, confirmation_url)
            text_content = get_invitation_with_password_text(user, confirmation_url)
        
        email_data = {
            "from": "Mentora <noreply@bigmentor.nl>",
            "to": [user.email],
            "subject": "Welcome to Mentora - Your Account Details",
            "html": html_content,
            "text": text_content,
            "click_tracking": False,  # Отключаем click tracking для лучшей доставляемости
            "open_tracking": False   # Отключаем open tracking для лучшей доставляемости
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
            print(f"✅ INVITATION WITH PASSWORD EMAIL SENT via Resend")
            print(f"Email ID: {result.get('id', 'N/A')}")
            return True
        else:
            print(f"❌ RESEND API ERROR: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"=== RESEND INVITATION WITH PASSWORD ERROR: {str(e)} ===")
        print(f"=== ERROR TYPE: {type(e).__name__} ===")
        import traceback
        print(f"=== TRACEBACK: {traceback.format_exc()}")
        return False


def get_confirmation_email_html(user, confirmation_url):
    """Генерирует HTML версию email подтверждения"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Email Confirmation - Mentora</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #1d4ed8; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .button {{ display: inline-block; background: #1d4ed8; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Mentora</h1>
                <p>Professional Platform</p>
            </div>
            <div class="content">
                <h2>Welcome to Mentora, {user.first_name}!</h2>
                <p>Thank you for registering with Mentora. To complete your registration and start your professional journey, please confirm your email address.</p>
                
                <p>Click the button below to confirm your email:</p>
                
                <a href="{confirmation_url}" class="button">Confirm Email Address</a>
                
                <p>If the button doesn't work, you can copy and paste this link into your browser:</p>
                <p><a href="{confirmation_url}">{confirmation_url}</a></p>
                
                <p><strong>Important:</strong> This confirmation link will expire in 24 hours.</p>
                
                <p>If you didn't create an account with Mentora, you can safely ignore this email.</p>
            </div>
            <div class="footer">
                <p>&copy; 2024 Mentora. All rights reserved.</p>
                <p>This email was sent to {user.email}</p>
            </div>
        </div>
    </body>
    </html>
    """

def get_confirmation_email_text(user, confirmation_url):
    """Генерирует текстовую версию email подтверждения"""
    return f"""
Welcome to Mentora, {user.first_name}!

Thank you for registering with Mentora. To complete your registration and start your professional journey, please confirm your email address.

Click the link below to confirm your email:
{confirmation_url}

Important: This confirmation link will expire in 24 hours.

If you didn't create an account with Mentora, you can safely ignore this email.

Best regards,
The Mentora Team

---
© 2025 Mentora. All rights reserved.
This email was sent to {user.email}
    """

def send_password_reset_email_resend(user, token):
    """
    Отправляет email сброса пароля через Resend API
    """
    try:
        reset_url = f"{current_app.config.get('BASE_URL', 'https://bigmentor.nl')}/auth/reset-password/{token}"
        
        print(f"=== RESEND PASSWORD RESET for {user.email} ===")
        print(f"=== RESET_URL: {reset_url} ===")
        
        # Проверяем, отключена ли отправка email
        mail_suppress = current_app.config.get('MAIL_SUPPRESS_SEND', False)
        print(f"=== MAIL_SUPPRESS_SEND: {mail_suppress} ===")
        
        if mail_suppress:
            # Development mode - console output
            print(f"\n{'='*60}")
            print(f"🔐 PASSWORD RESET for {user.email}")
            print(f"{'='*60}")
            print(f"👤 User: {user.first_name} {user.last_name}")
            print(f"📧 Email: {user.email}")
            print(f"🔗 Reset link: {reset_url}")
            print(f"⏰ Token valid for: 1 hour")
            print(f"{'='*60}")
            print(f"💡 Copy the link above and open in browser to reset password")
            print(f"{'='*60}\n")
            
            # Log to file for admin access
            try:
                with open('logs/password_reset_links.log', 'a') as f:
                    f.write(f"{datetime.now().isoformat()} - {user.email} - {reset_url} - RESEND_CONSOLE_MODE\n")
            except:
                pass
                
            return True
        
        # Production mode - send via Resend API
        print("=== PRODUCTION MODE - SENDING PASSWORD RESET VIA RESEND API ===")
        
        # Get Resend API key
        resend_api_key = current_app.config.get('RESEND_API_KEY')
        if not resend_api_key:
            print("=== ERROR: RESEND_API_KEY not configured ===")
            return False
        
        # Prepare email data
        email_data = {
            "from": current_app.config.get('MAIL_DEFAULT_SENDER', 'Mentora <info@bigmentor.nl>'),
            "to": [user.email],
            "subject": "MENTORA - Password Reset Request",
            "html": get_password_reset_html_resend(user, reset_url),
            "text": get_password_reset_text_resend(user, reset_url)
        }
        
        print(f"=== SENDING TO RESEND API ===")
        print(f"=== FROM: {email_data['from']} ===")
        print(f"=== TO: {email_data['to']} ===")
        print(f"=== SUBJECT: {email_data['subject']} ===")
        
        # Send via Resend API
        headers = {
            "Authorization": f"Bearer {resend_api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            "https://api.resend.com/emails",
            headers=headers,
            json=email_data,
            timeout=30
        )
        
        print(f"=== RESEND API RESPONSE STATUS: {response.status_code} ===")
        print(f"=== RESEND API RESPONSE: {response.text} ===")
        
        if response.status_code == 200:
            result = response.json()
            print(f"=== PASSWORD RESET EMAIL SENT SUCCESSFULLY VIA RESEND ===")
            print(f"=== EMAIL ID: {result.get('id')} ===")
            
            current_app.logger.info(f"Password reset email sent to {user.email} via Resend API")
            return True
        else:
            print(f"=== RESEND API ERROR: {response.status_code} - {response.text} ===")
            current_app.logger.error(f"Failed to send password reset via Resend API to {user.email}: {response.text}")
            return False
            
    except Exception as e:
        print(f"=== RESEND PASSWORD RESET ERROR: {str(e)} ===")
        import traceback
        print(f"=== TRACEBACK: {traceback.format_exc()} ===")
        
        current_app.logger.error(f"Failed to send password reset via Resend to {user.email}: {str(e)}")
        return False

def send_email_via_resend(to_email, subject, html_content, from_name="Mentora Team", attachments=None):
    """
    Универсальная функция для отправки email через Resend API
    
    Args:
        to_email: Email получателя
        subject: Тема письма
        html_content: HTML содержимое письма
        from_name: Имя отправителя
        attachments: Список вложений в формате [{"filename": "file.gif", "content": base64_content, "cid": "learning_map_gif"}]
    """
    try:
        from flask import current_app
        import base64
        
        # Проверяем, отключена ли отправка email
        mail_suppress = current_app.config.get('MAIL_SUPPRESS_SEND', False)
        
        if mail_suppress:
            print(f"\n{'='*60}")
            print(f"📧 EMAIL (Resend - console mode) to {to_email}")
            print(f"{'='*60}")
            print(f"📧 To: {to_email}")
            print(f"📧 Subject: {subject}")
            print(f"📧 From: {from_name}")
            print(f"📧 Content: HTML email with professional template")
            if attachments:
                print(f"📧 Attachments: {len(attachments)} file(s)")
            print(f"{'='*60}\n")
            return True
        
        # Получаем настройки Resend
        api_key = current_app.config.get('RESEND_API_KEY')
        from_email = current_app.config.get('RESEND_FROM_EMAIL', 'Mentora <info@bigmentor.nl>')
        
        if not api_key:
            print("❌ RESEND_API_KEY not configured")
            return False
        
        # Подготавливаем данные для Resend API
        email_data = {
            "from": from_email,
            "to": [to_email],
            "subject": subject,
            "html": html_content,
            "click_tracking": False,
            "open_tracking": False
        }
        
        # Добавляем вложения, если есть
        if attachments:
            email_data["attachments"] = []
            for att in attachments:
                attachment_data = {
                    "filename": att.get("filename", "attachment"),
                    "content": att.get("content")  # base64 encoded content
                }
                # Если указан CID, добавляем его для встроенных изображений
                if att.get("cid"):
                    attachment_data["cid"] = att.get("cid")
                email_data["attachments"].append(attachment_data)
        
        # Отправляем через Resend API
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post("https://api.resend.com/emails", headers=headers, json=email_data, timeout=30)
        
        # Проверяем статус ответа
        if response.status_code == 200:
            response_json = response.json()
            print(f"✅ Email sent successfully via Resend to {to_email}")
            print(f"📧 Email ID: {response_json.get('id')}")
            return True
        else:
            # Логируем детали ошибки
            error_details = {
                'status_code': response.status_code,
                'response_text': response.text,
                'api_key_present': bool(api_key),
                'api_key_length': len(api_key) if api_key else 0
            }
            print(f"❌ Resend API request failed: {error_details}")
            current_app.logger.error(f"Resend API error for {to_email}: {error_details}")
            
            # Для 401 ошибки даем более понятное сообщение
            if response.status_code == 401:
                print("❌ Resend API: Unauthorized - Check RESEND_API_KEY configuration")
                current_app.logger.error("Resend API: Invalid or missing API key")
            
            return False
        
    except requests.exceptions.RequestException as e:
        error_msg = f"Resend API request failed: {str(e)}"
        print(f"❌ {error_msg}")
        current_app.logger.error(f"{error_msg} for {to_email}")
        return False
    except Exception as e:
        error_msg = f"Failed to send email via Resend API: {str(e)}"
        print(f"❌ {error_msg}")
        current_app.logger.error(f"{error_msg} for {to_email}", exc_info=True)
        return False

def get_password_reset_html_resend(user, reset_url):
    """Generate HTML for password reset email via Resend"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Password Reset - Mentora</title>
    </head>
    <body style="font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5;">
        <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff;">
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #1d4ed8, #2DB5A9); color: white; padding: 40px 30px; text-align: center;">
                <h1 style="margin: 0; font-size: 32px; font-weight: bold;">MENTORA</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Password Reset</p>
            </div>
            
            <!-- Content -->
            <div style="padding: 40px 30px;">
                <h2 style="color: #2d3748; margin-top: 0; font-size: 24px;">Password Reset</h2>
                
                <p style="color: #4a5568; font-size: 16px; line-height: 1.6;">
                    Hello, <strong>{user.first_name}</strong>!
                </p>
                
                <p style="color: #4a5568; font-size: 16px; line-height: 1.6;">
                    You have requested a password reset for your Mentora account. Click the button below to create a new password.
                </p>
                
                <!-- CTA Button -->
                <div style="text-align: center; margin: 40px 0;">
                    <a href="{reset_url}" 
                       style="background: linear-gradient(135deg, #1d4ed8, #2DB5A9); 
                              color: white; 
                              padding: 16px 32px; 
                              text-decoration: none; 
                              border-radius: 8px; 
                              font-weight: bold; 
                              font-size: 16px;
                              display: inline-block;
                              box-shadow: 0 4px 12px rgba(29, 78, 216, 0.3);">
                        🔐 Reset Password
                    </a>
                </div>
                
                <!-- Alternative link -->
                <div style="background-color: #f7fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin: 30px 0;">
                    <p style="color: #4a5568; font-size: 14px; margin: 0 0 10px 0;">
                        <strong>If the button doesn't work,</strong> copy this link:
                    </p>
                    <p style="word-break: break-all; background: #f8f9fa; padding: 10px; border-radius: 5px; font-family: monospace; font-size: 12px; color: #2d3748;">
                        {reset_url}
                    </p>
                </div>
                
                <!-- Warning -->
                <div style="background-color: #fff5f5; border: 1px solid #fed7d7; border-radius: 8px; padding: 20px; margin: 30px 0;">
                    <p style="color: #c53030; font-size: 14px; margin: 0;">
                        <strong>⚠️ Important:</strong> This link will expire in 1 hour. If you didn't request this reset, please ignore this email.
                    </p>
                </div>
                
                <p style="color: #4a5568; font-size: 14px; line-height: 1.6;">
                    If you have any questions, please contact our support team at 
                    <a href="mailto:info@bigmentor.nl" style="color: #1d4ed8;">info@bigmentor.nl</a>
                </p>
            </div>
            
            <!-- Footer -->
            <div style="background-color: #f7fafc; padding: 30px; text-align: center; border-top: 1px solid #e2e8f0;">
                <p style="color: #718096; font-size: 14px; margin: 0;">
                    <strong>Mentora Team</strong><br>
                    Professional Development Platform<br>
                    Website: <a href="https://bigmentor.nl" style="color: #1d4ed8;">bigmentor.nl</a>
                </p>
                <p style="color: #a0aec0; font-size: 12px; margin: 10px 0 0 0;">
                    © 2024 Mentora. All rights reserved.<br>
                    This email was sent to {user.email}
                </p>
            </div>
        </div>
    </body>
    </html>
    """

def get_password_reset_text_resend(user, reset_url):
    """Generate text version for password reset email via Resend"""
    return f"""
MENTORA - Password Reset Request

Hello {user.first_name} {user.last_name},

We received a request to reset your password for your Mentora account.

To reset your password, click the link below:
{reset_url}

IMPORTANT:
- This link will expire in 1 hour
- If you didn't request this reset, please ignore this email
- Your password will remain unchanged until you click the link

If you have any questions, please contact our support team at info@bigmentor.nl

Best regards,
Mentora Team
Professional Development Platform
Website: https://bigmentor.nl

© 2024 Mentora. All rights reserved.
This email was sent to {user.email}
    """

def send_welcome_email_resend(user):
    """Send welcome email using Resend API"""
    try:
        print(f"=== WELCOME EMAIL RESEND START for {user.email} ===")
        
        # Проверяем, отключена ли отправка email
        mail_suppress = current_app.config.get('MAIL_SUPPRESS_SEND', False)
        print(f"=== MAIL_SUPPRESS_SEND: {mail_suppress} ===")
        
        if mail_suppress:
            print(f"=== WELCOME EMAIL SUPPRESSED (TESTING MODE) ===")
            print(f"=== WELCOME EMAIL CONTENT ===")
            print(f"To: {user.email}")
            print(f"Subject: 🎉 Welcome to Mentora!")
            print(f"Content: Welcome, {user.first_name}! Your account has been created and is ready to use.")
            return True
        
        # Получаем настройки
        api_key = current_app.config.get('RESEND_API_KEY')
        from_email = current_app.config.get('RESEND_FROM_EMAIL', 'Mentora <info@bigmentor.nl>')
        
        if not api_key:
            print("❌ RESEND_API_KEY not configured!")
            return False
        
        # Подготавливаем HTML контент
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #1d4ed8, #2DB5A9); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="margin: 0;">🎉 Welcome!</h1>
            </div>
            
            <div style="background: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2>Welcome, {user.first_name}!</h2>
                
                <p>🎉 <strong>Welcome to Mentora!</strong> Your account has been created and is ready to use.</p>
                
                <div style="background: #f8f9fa; border: 1px solid #e9ecef; border-radius: 8px; padding: 20px; margin: 20px 0;">
                    <h3 style="color: #2c3e50; margin-top: 0;">📧 Your Login Details:</h3>
                    <p><strong>Email:</strong> {user.email}</p>
                    <p><strong>Password:</strong> The password you created during registration</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://bigmentor.nl/login" 
                       style="background: linear-gradient(135deg, #1d4ed8, #2DB5A9); color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">
                        🚀 Login to Mentora
                    </a>
                </div>
                
                <p style="color: #666;">Best regards,<br>Mentora Team</p>
            </div>
        </body>
        </html>
        """
        
        # Подготавливаем данные для Resend API
        email_data = {
            "from": from_email,
            "to": [user.email],
            "subject": "🎉 Welcome to Mentora!",
            "html": html_content,
            "click_tracking": False,
            "open_tracking": False
        }
        
        # Отправляем через Resend API
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post("https://api.resend.com/emails", headers=headers, json=email_data)
        response.raise_for_status()
        
        response_json = response.json()
        print(f"✅ Welcome email sent successfully via Resend! ID: {response_json.get('id')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error sending welcome email via Resend: {str(e)}")
        return False
