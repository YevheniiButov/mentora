# utils/resend_email_service.py
"""
Resend Email Service for Mentora
Использует Resend API для отправки email подтверждений
"""

import requests
import json
from flask import current_app
from models import User
# Токены генерируются в модели User

def send_email_confirmation_resend(user):
    """
    Отправляет email подтверждение через Resend API
    """
    try:
        # Генерируем токен подтверждения
        token = user.generate_email_confirmation_token()
        confirmation_url = f"{current_app.config.get('BASE_URL', 'https://bigmentor.nl')}/auth/confirm-email/{token}"
        
        print(f"=== RESEND EMAIL CONFIRMATION for {user.email} ===")
        print(f"=== CONFIRMATION_URL: {confirmation_url} ===")
        
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
            print(f"🔗 Confirmation link: {confirmation_url}")
            print(f"⏰ Token valid for: 24 hours")
            print(f"{'='*60}")
            print(f"💡 Copy the link above and open in browser to confirm")
            print(f"{'='*60}\n")
            
            current_app.logger.info(f"Email confirmation (console mode) for {user.email}")
            return True
        
        # Получаем настройки Resend
        api_key = current_app.config.get('RESEND_API_KEY')
        from_email = current_app.config.get('RESEND_FROM_EMAIL', 'Mentora <noreply@bigmentor.nl>')
        
        if not api_key:
            print("❌ RESEND_API_KEY not configured")
            return False
        
        print("=== PRODUCTION MODE - SENDING REAL EMAIL VIA RESEND ===")
        
        # Подготавливаем данные для Resend API
        email_data = {
            "from": from_email,
            "to": [user.email],
            "subject": "MENTORA - Email Confirmation",
            "html": get_confirmation_email_html(user, confirmation_url),
            "text": get_confirmation_email_text(user, confirmation_url)
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
            .header {{ background: #3ECDC1; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
            .button {{ display: inline-block; background: #3ECDC1; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎓 Mentora</h1>
                <p>Dental Academy Platform</p>
            </div>
            <div class="content">
                <h2>Welcome to Mentora, {user.first_name}!</h2>
                <p>Thank you for registering with Mentora. To complete your registration and start your dental learning journey, please confirm your email address.</p>
                
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

Thank you for registering with Mentora. To complete your registration and start your dental learning journey, please confirm your email address.

Click the link below to confirm your email:
{confirmation_url}

Important: This confirmation link will expire in 24 hours.

If you didn't create an account with Mentora, you can safely ignore this email.

Best regards,
The Mentora Team

---
© 2024 Mentora. All rights reserved.
This email was sent to {user.email}
    """
