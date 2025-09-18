# utils/email_service.py - Simplified Email Service with Direct Sending

from flask import current_app
from flask_mail import Mail, Message
from extensions import mail

def init_mail(app):
    """Initialize Flask-Mail with the app"""
    mail.init_app(app)
    return mail

def send_email_confirmation(user, token):
    """Send email confirmation using Resend API or SMTP fallback"""
    try:
        print(f"=== EMAIL CONFIRMATION START for {user.email} ===")
        
        # Check email provider
        email_provider = current_app.config.get('EMAIL_PROVIDER', 'smtp')
        print(f"=== EMAIL_PROVIDER: {email_provider} ===")
        
        if email_provider == 'resend':
            # Use Resend API
            from utils.resend_email_service import send_email_confirmation_resend
            return send_email_confirmation_resend(user)
        else:
            # Use SMTP fallback
            return send_email_confirmation_smtp(user, token)
            
    except Exception as e:
        print(f"=== EMAIL CONFIRMATION ERROR: {str(e)} ===")
        print(f"=== ERROR TYPE: {type(e).__name__} ===")
        import traceback
        print(f"=== TRACEBACK: {traceback.format_exc()} ===")
        
        current_app.logger.error(f"Failed to send email confirmation to {user.email}: {str(e)}")
        return False

def send_email_confirmation_smtp(user, token):
    """Send email confirmation using SMTP (fallback method)"""
    try:
        print(f"=== SMTP EMAIL CONFIRMATION for {user.email} ===")
        
        # Generate confirmation URL
        base_url = current_app.config.get('BASE_URL', 'https://bigmentor.nl')
        confirmation_url = f"{base_url}/auth/confirm-email/{token}"
        
        print(f"=== CONFIRMATION_URL: {confirmation_url} ===")
        
        # Check if email sending is suppressed
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
        
        print("=== PRODUCTION MODE - SENDING REAL EMAIL VIA SMTP ===")
        
        # Create message
        msg = Message(
            subject='MENTORA - Email Confirmation',
            recipients=[user.email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # HTML content (inline for reliability)
        msg.html = get_confirmation_email_html(user, confirmation_url)
        
        # Text content (inline for reliability)  
        msg.body = get_confirmation_email_text(user, confirmation_url)
        
        # Send email
        print("=== ATTEMPTING TO SEND EMAIL VIA SMTP ===")
        mail.send(msg)
        print("=== EMAIL SENT SUCCESSFULLY VIA SMTP ===")
        
        current_app.logger.info(f"Email confirmation sent to {user.email} via SMTP")
        return True
        
    except Exception as e:
        print(f"=== SMTP EMAIL CONFIRMATION ERROR: {str(e)} ===")
        print(f"=== ERROR TYPE: {type(e).__name__} ===")
        import traceback
        print(f"=== TRACEBACK: {traceback.format_exc()} ===")
        
        current_app.logger.error(f"Failed to send email confirmation to {user.email} via SMTP: {str(e)}")
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
                <h1 style="margin: 0; font-size: 32px; font-weight: bold;">MENTORA</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Medical Education Platform</p>
            </div>
            
            <!-- Content -->
            <div style="padding: 40px 30px;">
                <h2 style="color: #2d3748; margin-top: 0; font-size: 24px;">Email Confirmation</h2>
                
                <p style="color: #4a5568; font-size: 16px; line-height: 1.6;">
                    Hello, <strong>{user.first_name}</strong>!
                </p>
                
                <p style="color: #4a5568; font-size: 16px; line-height: 1.6;">
                    Thank you for registering with Mentora. To complete your pre-registration and activate your account, please confirm your email address.
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
                        ✅ Confirm Email
                    </a>
                </div>
                
                <!-- Alternative link -->
                <div style="background-color: #f7fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin: 30px 0;">
                    <p style="color: #4a5568; font-size: 14px; margin: 0 0 10px 0;">
                        <strong>If the button doesn't work,</strong> copy and paste this link into your browser address bar:
                    </p>
                    <p style="color: #3182ce; font-size: 14px; word-break: break-all; margin: 0; font-family: monospace; background: white; padding: 10px; border-radius: 4px;">
                        {confirmation_url}
                    </p>
                </div>
                
                <!-- Important note -->
                <div style="background-color: #fef5e7; border-left: 4px solid #f6ad55; padding: 15px; margin: 20px 0;">
                    <p style="color: #744210; font-size: 14px; margin: 0;">
                        <strong>Important:</strong> This link is valid for 24 hours. After that, you will need to request a new confirmation link.
                    </p>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background-color: #f7fafc; padding: 30px; text-align: center; border-top: 1px solid #e2e8f0;">
                <p style="color: #718096; font-size: 14px; margin: 0 0 15px 0;">
                    If you did not register with Mentora, please ignore this email.
                </p>
                
                <p style="color: #4a5568; font-size: 14px; margin: 0;">
                    <strong>Mentora</strong><br>
                    Email: <a href="mailto:info@bigmentor.nl" style="color: #3182ce;">info@bigmentor.nl</a><br>
                    Website: <a href="https://bigmentor.nl" style="color: #3182ce;">bigmentor.nl</a>
                </p>
                
                <p style="color: #a0aec0; font-size: 12px; margin: 20px 0 0 0;">
                    © 2024 Mentora. All rights reserved.
                </p>
            </div>
        </div>
    </body>
    </html>
    """

def get_confirmation_email_text(user, confirmation_url):
    """Generate text content for confirmation email"""
    return f"""
MENTORA - Email Confirmation

Hello, {user.first_name}!

Thank you for registering with Mentora. To complete your pre-registration and activate your account, please confirm your email address.

Confirmation link:
{confirmation_url}

IMPORTANT: This link is valid for 24 hours.

If you did not register with Mentora, please ignore this email.

---
Best regards,
Mentora Team

Email: info@bigmentor.nl
Website: https://bigmentor.nl

© 2024 Mentora. All rights reserved.
    """

def send_password_reset_email(user, token):
    """Send password reset email using direct method"""
    try:
        print(f"=== PASSWORD RESET START for {user.email} ===")
        
        # Generate reset URL
        base_url = current_app.config.get('BASE_URL', 'https://bigmentor.nl')
        reset_url = f"{base_url}/auth/reset-password/{token}"
        
        print(f"=== RESET_URL: {reset_url} ===")
        
        # Check if suppressed
        mail_suppress = current_app.config.get('MAIL_SUPPRESS_SEND', False)
        print(f"=== MAIL_SUPPRESS_SEND: {mail_suppress} ===")
        
        if mail_suppress:
            print(f"\n{'='*60}")
            print(f"🔐 PASSWORD RESET for {user.email}")
            print(f"🔗 Link: {reset_url}")
            print(f"{'='*60}\n")
            return True
        
        print("=== PRODUCTION MODE - SENDING PASSWORD RESET ===")
        
        # Create message
        msg = Message(
            subject='MENTORA - Password Reset',
            recipients=[user.email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # HTML content
        msg.html = get_password_reset_html(user, reset_url)
        msg.body = get_password_reset_text(user, reset_url)
        
        # Send
        print("=== ATTEMPTING TO SEND PASSWORD RESET ===")
        mail.send(msg)
        print("=== PASSWORD RESET EMAIL SENT SUCCESSFULLY ===")
        
        current_app.logger.info(f"Password reset email sent to {user.email}")
        return True
        
    except Exception as e:
        print(f"=== PASSWORD RESET ERROR: {str(e)} ===")
        import traceback
        print(f"=== TRACEBACK: {traceback.format_exc()} ===")
        
        current_app.logger.error(f"Failed to send password reset to {user.email}: {str(e)}")
        return False

def get_password_reset_html(user, reset_url):
    """Generate HTML for password reset email"""
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
            <div style="background: linear-gradient(135deg, #3ECDC1, #2DB5A9); color: white; padding: 40px 30px; text-align: center;">
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
                       style="background: linear-gradient(135deg, #3ECDC1, #2DB5A9); 
                              color: white; 
                              padding: 16px 32px; 
                              text-decoration: none; 
                              border-radius: 8px; 
                              font-weight: bold; 
                              font-size: 16px;
                              display: inline-block;
                              box-shadow: 0 4px 12px rgba(62, 205, 193, 0.3);">
                        🔐 Reset Password
                    </a>
                </div>
                
                <!-- Alternative link -->
                <div style="background-color: #f7fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin: 30px 0;">
                    <p style="color: #4a5568; font-size: 14px; margin: 0 0 10px 0;">
                        <strong>If the button doesn't work,</strong> copy this link:
                    </p>
                    <p style="color: #3182ce; font-size: 14px; word-break: break-all; margin: 0; font-family: monospace; background: white; padding: 10px; border-radius: 4px;">
                        {reset_url}
                    </p>
                </div>
                
                <!-- Important note -->
                <div style="background-color: #fef5e7; border-left: 4px solid #f6ad55; padding: 15px; margin: 20px 0;">
                    <p style="color: #744210; font-size: 14px; margin: 0;">
                        <strong>Important:</strong> This link is valid for 1 hour. If you did not request a password reset, please ignore this email.
                    </p>
                </div>
            </div>
            
            <!-- Footer -->
            <div style="background-color: #f7fafc; padding: 30px; text-align: center; border-top: 1px solid #e2e8f0;">
                <p style="color: #718096; font-size: 14px; margin: 0 0 15px 0;">
                    If you did not request a password reset, your account remains secure.
                </p>
                
                <p style="color: #4a5568; font-size: 14px; margin: 0;">
                    <strong>Mentora</strong><br>
                    Email: <a href="mailto:info@bigmentor.nl" style="color: #3182ce;">info@bigmentor.nl</a><br>
                    Website: <a href="https://bigmentor.nl" style="color: #3182ce;">bigmentor.nl</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """

def get_password_reset_text(user, reset_url):
    """Generate text for password reset email"""
    return f"""
MENTORA - Password Reset

Hello, {user.first_name}!

You have requested a password reset for your Mentora account.

Password reset link:
{reset_url}

IMPORTANT: This link is valid for 1 hour.

If you did not request a password reset, please ignore this email.

---
Best regards,
Mentora Team

Email: info@bigmentor.nl
Website: https://bigmentor.nl
    """

def send_welcome_email(user):
    """Send welcome email after confirmation"""
    try:
        print(f"=== WELCOME EMAIL START for {user.email} ===")
        
        if current_app.config.get('MAIL_SUPPRESS_SEND', False):
            print(f"Welcome email (console) for {user.email}")
            return True
        
        msg = Message(
            subject='🎉 Welcome to Mentora!',
            recipients=[user.email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        msg.html = f"""
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #3ECDC1, #2DB5A9); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="margin: 0;">🎉 Welcome!</h1>
            </div>
            
            <div style="background: white; padding: 30px; border-radius: 0 0 10px 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <h2>Welcome, {user.first_name}!</h2>
                
                <p>Congratulations! You have successfully completed your pre-registration for Mentora. We will notify you when the platform becomes available.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://bigmentor.nl/dashboard" 
                       style="background: linear-gradient(135deg, #3ECDC1, #2DB5A9); color: white; padding: 15px 30px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block;">
                        🚀 Go to Dashboard
                    </a>
                </div>
                
                <p style="color: #666;">Best regards,<br>Mentora Team</p>
            </div>
        </body>
        </html>
        """
        
        msg.body = f"""
Welcome to Mentora!

Hello, {user.first_name}!

Congratulations! You have successfully completed your pre-registration for Mentora. We will notify you when the platform becomes available.

Go to Dashboard: https://bigmentor.nl/dashboard

Best regards,
Mentora Team
        """
        
        mail.send(msg)
        
        current_app.logger.info(f"Welcome email sent to {user.email}")
        return True
        
    except Exception as e:
        print(f"=== WELCOME EMAIL ERROR: {str(e)} ===")
        current_app.logger.error(f"Failed to send welcome email: {str(e)}")
        return False
