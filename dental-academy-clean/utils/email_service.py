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
        # Generate URLs - используем статические URL для избежания ошибок вне контекста запроса
        base_url = current_app.config.get('BASE_URL', 'https://mentora.com.in')
        confirmation_url = f"{base_url}/auth/confirm-email/{token}"
        unsubscribe_url = f"{base_url}/auth/unsubscribe/{user.id}"
        privacy_policy_url = f"{base_url}/privacy"
        
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
        try:
            msg.html = render_template('emails/confirm_email.html', 
                                     user=user, 
                                     confirmation_url=confirmation_url,
                                     unsubscribe_url=unsubscribe_url,
                                     privacy_policy_url=privacy_policy_url)
        except Exception as template_error:
            current_app.logger.warning(f"Failed to render HTML email template: {template_error}")
            # Fallback HTML content
            msg.html = f"""
            <h1>Подтверждение регистрации</h1>
            <p>Здравствуйте, {user.first_name}!</p>
            <p>Для подтверждения вашего email адреса, пожалуйста, перейдите по ссылке:</p>
            <p><a href="{confirmation_url}">Подтвердить email</a></p>
            <p>Если вы не регистрировались на нашем сайте, просто проигнорируйте это письмо.</p>
            <p>С уважением,<br>Команда Mentora</p>
            """
        
        try:
            msg.body = render_template('emails/confirm_email.txt', 
                                     user=user, 
                                     confirmation_url=confirmation_url,
                                     unsubscribe_url=unsubscribe_url,
                                     privacy_policy_url=privacy_policy_url)
        except Exception as template_error:
            current_app.logger.warning(f"Failed to render text email template: {template_error}")
            # Fallback text content
            msg.body = f"""
Подтверждение регистрации

Здравствуйте, {user.first_name}!

Для подтверждения вашего email адреса, пожалуйста, перейдите по ссылке:
{confirmation_url}

Если вы не регистрировались на нашем сайте, просто проигнорируйте это письмо.

С уважением,
Команда Mentora
            """
        
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
        print("=== EMAIL SERVICE: send_password_reset_email START ===")
        
        # Check if mail is initialized
        print(f"=== MAIL OBJECT CHECK: {mail is not None} ===")
        print(f"=== MAIL APP CHECK: {hasattr(mail, 'app') and mail.app is not None} ===")
        
        # Generate reset URL
        reset_url = f"{current_app.config.get('BASE_URL', 'https://mentora.com.in')}/auth/reset-password/{token}"
        print(f"=== RESET URL GENERATED: {reset_url} ===")
        
        # Check if email sending is suppressed (development mode)
        mail_suppress = current_app.config.get('MAIL_SUPPRESS_SEND', False)
        print(f"=== MAIL_SUPPRESS_SEND CHECK: {mail_suppress} ===")
        
        if mail_suppress:
            print("=== DEVELOPMENT MODE - OUTPUTTING TO CONSOLE ===")
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
            print("=== EMAIL SERVICE: CONSOLE MODE SUCCESS ===")
            return True
        
        print("=== PRODUCTION MODE - SENDING REAL EMAIL ===")
        
        # Check email configuration
        print(f"=== MAIL CONFIG CHECK ===")
        print(f"MAIL_SERVER: {current_app.config.get('MAIL_SERVER')}")
        print(f"MAIL_PORT: {current_app.config.get('MAIL_PORT')}")
        print(f"MAIL_USE_TLS: {current_app.config.get('MAIL_USE_TLS')}")
        print(f"MAIL_USERNAME: {current_app.config.get('MAIL_USERNAME')}")
        print(f"MAIL_PASSWORD: {'SET' if current_app.config.get('MAIL_PASSWORD') else 'NOT SET'}")
        
        # Production mode - send real email
        print("=== CREATING MESSAGE ===")
        msg = Message(
            subject='Password Reset - Mentora',
            recipients=[user.email],
            sender=('Mentora', 'noreply@mentora.com.in')
        )
        print("=== MESSAGE CREATED ===")
        
        # Render email template
        print("=== RENDERING EMAIL TEMPLATES ===")
        try:
            msg.html = render_template('emails/reset_password.html', 
                                     user=user, 
                                     reset_url=reset_url)
            print("=== HTML TEMPLATE RENDERED ===")
        except Exception as template_error:
            print(f"=== HTML TEMPLATE ERROR: {template_error} ===")
            msg.html = f"<h1>Password Reset</h1><p>Click <a href='{reset_url}'>here</a> to reset your password.</p>"
        
        try:
            msg.body = render_template('emails/reset_password.txt', 
                                     user=user, 
                                     reset_url=reset_url)
            print("=== TEXT TEMPLATE RENDERED ===")
        except Exception as template_error:
            print(f"=== TEXT TEMPLATE ERROR: {template_error} ===")
            msg.body = f"Password Reset\n\nClick here to reset your password: {reset_url}"
        
        # Send email
        print("=== SENDING EMAIL ===")
        mail.send(msg)
        print("=== EMAIL SENT SUCCESSFULLY ===")
        
        current_app.logger.info(f"Password reset email sent to {user.email}")
        return True
        
    except Exception as e:
        print(f"=== EMAIL SERVICE ERROR: {str(e)} ===")
        import traceback
        print(f"=== EMAIL SERVICE TRACEBACK: {traceback.format_exc()} ===")
        
        current_app.logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
        return False
