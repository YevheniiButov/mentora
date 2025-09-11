# utils/email_service.py - Email service for sending confirmation emails

from flask import current_app, render_template
from flask_mail import Mail, Message
import os

# Initialize Flask-Mail
mail = Mail()

def init_mail(app):
    """Initialize Flask-Mail with the app"""
    mail.init_app(app)
    return mail

def send_email_confirmation(user, token):
    """Send email confirmation to user"""
    try:
        # Generate confirmation URL
        confirmation_url = f"{current_app.config.get('BASE_URL', 'http://localhost:5000')}/auth/confirm-email/{token}"
        
        # Check if email sending is suppressed (development mode)
        if current_app.config.get('MAIL_SUPPRESS_SEND', False):
            # Development mode - output to console
            print(f"\n{'='*60}")
            print(f"📧 EMAIL CONFIRMATION для {user.email}")
            print(f"{'='*60}")
            print(f"👤 Пользователь: {user.first_name} {user.last_name}")
            print(f"📧 Email: {user.email}")
            print(f"🔗 Ссылка подтверждения: {confirmation_url}")
            print(f"⏰ Токен действителен: 1 час")
            print(f"🕐 Отправлено: {user.email_confirmation_sent_at}")
            print(f"{'='*60}")
            print(f"💡 Скопируйте ссылку выше и откройте в браузере для подтверждения")
            print(f"{'='*60}\n")
            
            current_app.logger.info(f"Email confirmation (console mode) for {user.email}")
            return True
        
        # Production mode - send real email
        msg = Message(
            subject='Registration approve',
            recipients=[user.email],
            sender=('Mentora', 'noreply@mentora.com.in')
        )
        
        # Render email template
        msg.html = render_template('emails/confirm_email.html', 
                                 user=user, 
                                 confirmation_url=confirmation_url)
        msg.body = render_template('emails/confirm_email.txt', 
                                 user=user, 
                                 confirmation_url=confirmation_url)
        
        # Send email
        mail.send(msg)
        
        current_app.logger.info(f"Email confirmation sent to {user.email}")
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send email confirmation to {user.email}: {str(e)}")
        return False

def send_welcome_email(user):
    """Send welcome email after successful registration"""
    try:
        msg = Message(
            subject='Welcome to Mentora!',
            recipients=[user.email],
            sender=('Mentora', 'noreply@mentora.com.in')
        )
        
        # Render email template
        msg.html = render_template('emails/welcome.html', user=user)
        msg.body = render_template('emails/welcome.txt', user=user)
        
        # Send email
        mail.send(msg)
        
        current_app.logger.info(f"Welcome email sent to {user.email}")
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
        return False

def send_password_reset_email(user, token):
    """Send password reset email"""
    try:
        # Generate reset URL
        reset_url = f"{current_app.config.get('BASE_URL', 'http://localhost:5000')}/auth/reset-password/{token}"
        
        # Check if email sending is suppressed (development mode)
        if current_app.config.get('MAIL_SUPPRESS_SEND', False):
            # Development mode - output to console
            print(f"\n{'='*60}")
            print(f"🔐 PASSWORD RESET для {user.email}")
            print(f"{'='*60}")
            print(f"👤 Пользователь: {user.first_name} {user.last_name}")
            print(f"📧 Email: {user.email}")
            print(f"🔗 Ссылка сброса пароля: {reset_url}")
            print(f"⏰ Токен действителен: 1 час")
            print(f"🕐 Отправлено: {user.password_reset_sent_at}")
            print(f"{'='*60}")
            print(f"💡 Скопируйте ссылку выше и откройте в браузере для сброса пароля")
            print(f"{'='*60}\n")
            
            current_app.logger.info(f"Password reset email (console mode) for {user.email}")
            return True
        
        # Production mode - send real email
        msg = Message(
            subject='Password Reset - Mentora',
            recipients=[user.email],
            sender=('Mentora', 'noreply@mentora.com.in')
        )
        
        # Render email template
        msg.html = render_template('emails/reset_password.html', 
                                 user=user, 
                                 reset_url=reset_url)
        msg.body = render_template('emails/reset_password.txt', 
                                 user=user, 
                                 reset_url=reset_url)
        
        # Send email
        mail.send(msg)
        
        current_app.logger.info(f"Password reset email sent to {user.email}")
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
        return False
