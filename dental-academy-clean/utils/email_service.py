# utils/email_service.py - Simplified Email Service with Direct Sending

from flask import current_app
from flask_mail import Mail, Message
from extensions import mail

def init_mail(app):
    """Initialize Flask-Mail with the app"""
    mail.init_app(app)
    return mail

def send_email_confirmation(user, token, temp_password=None):
    """Send email confirmation using Resend API or SMTP fallback"""
    try:
        print(f"=== EMAIL CONFIRMATION START for {user.email} ===")
        
        # Check email provider
        email_provider = current_app.config.get('EMAIL_PROVIDER', 'smtp')
        print(f"=== EMAIL_PROVIDER: {email_provider} ===")
        
        if email_provider == 'resend':
            # Use Resend API
            from utils.resend_email_service import send_email_confirmation_resend
            return send_email_confirmation_resend(user, temp_password, token)
        else:
            # Use SMTP fallback
            return send_email_confirmation_smtp(user, token, temp_password)
            
    except Exception as e:
        print(f"=== EMAIL CONFIRMATION ERROR: {str(e)} ===")
        print(f"=== ERROR TYPE: {type(e).__name__} ===")
        import traceback
        print(f"=== TRACEBACK: {traceback.format_exc()} ===")
        
        current_app.logger.error(f"Failed to send email confirmation to {user.email}: {str(e)}")
        return False

def send_email_confirmation_smtp(user, token, temp_password=None):
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
        
        print("=== PRODUCTION MODE - SENDING REAL EMAIL VIA SMTP ===")
        
        # Create message
        msg = Message(
            subject='MENTORA - Email Confirmation',
            recipients=[user.email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # HTML content (inline for reliability)
        msg.html = get_confirmation_email_html(user, confirmation_url, temp_password)
        
        # Text content (inline for reliability)  
        msg.body = get_confirmation_email_text(user, confirmation_url, temp_password)
        
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

def get_confirmation_email_html(user, confirmation_url, temp_password=None):
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
                
                <p style="color: #4a5568; font-size: 16px; line-height: 1.6;">
                    <strong>Your login credentials:</strong><br>
                    📧 Email: <strong>{user.email}</strong><br>
                    🔑 Password: Use the temporary password below
                </p>
                
                {f'''
                <!-- Temporary Password Info -->
                <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 8px; padding: 20px; margin: 30px 0;">
                    <h3 style="color: #856404; margin: 0 0 15px 0; font-size: 18px;">🔑 Your Temporary Password</h3>
                    <p style="color: #856404; font-size: 16px; line-height: 1.6; margin: 0 0 15px 0;">
                        For your quick registration, we have generated a temporary password for you:
                    </p>
                    <div style="background-color: #ffffff; border: 2px solid #856404; border-radius: 6px; padding: 15px; text-align: center; margin: 15px 0;">
                        <p style="color: #856404; font-size: 20px; font-weight: bold; font-family: monospace; margin: 0; letter-spacing: 2px;">
                            {temp_password}
                        </p>
                    </div>
                    <p style="color: #856404; font-size: 14px; line-height: 1.5; margin: 15px 0 0 0;">
                        <strong>Important:</strong> Please save this password securely. You can change it after confirming your email and logging in.
                    </p>
                </div>
                ''' if temp_password else ''}
                
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
                
                <!-- Next steps -->
                <div style="background-color: #e6fffa; border-left: 4px solid #3ECDC1; padding: 20px; margin: 30px 0;">
                    <h3 style="color: #2d3748; margin: 0 0 15px 0; font-size: 18px;">🚀 What happens next?</h3>
                    <ol style="color: #4a5568; font-size: 14px; line-height: 1.6; margin: 0; padding-left: 20px;">
                        <li>Click the "Confirm Email" button above</li>
                        <li>You'll be redirected to the login page</li>
                        <li>Use your email and the temporary password to log in</li>
                        <li>You can change your password in your profile settings</li>
                        <li>Start exploring the Mentora learning platform!</li>
                    </ol>
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

def get_confirmation_email_text(user, confirmation_url, temp_password=None):
    """Generate text content for confirmation email"""
    return f"""
MENTORA - Email Confirmation

Hello, {user.first_name}!

Thank you for registering with Mentora. To complete your pre-registration and activate your account, please confirm your email address.

YOUR LOGIN CREDENTIALS:
📧 Email: {user.email}
🔑 Password: Use the temporary password below

{f'''
🔑 YOUR TEMPORARY PASSWORD:
{temp_password}

Important: Please save this password securely. You can change it after confirming your email and logging in.

''' if temp_password else ''}

🚀 WHAT HAPPENS NEXT:
1. Click the confirmation link below
2. You'll be redirected to the login page
3. Use your email and the temporary password to log in
4. You can change your password in your profile settings
5. Start exploring the Mentora learning platform!

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
    """Send password reset email using the same logic as email confirmation"""
    try:
        print(f"=== PASSWORD RESET START for {user.email} ===")
        
        # Check email provider (same as email confirmation)
        email_provider = current_app.config.get('EMAIL_PROVIDER', 'smtp')
        print(f"=== EMAIL_PROVIDER: {email_provider} ===")
        
        if email_provider == 'resend':
            # Use Resend API (same as email confirmation)
            print("=== USING RESEND API FOR PASSWORD RESET ===")
            try:
                from utils.resend_email_service import send_password_reset_email_resend
                print("=== RESEND FUNCTION IMPORTED SUCCESSFULLY ===")
                return send_password_reset_email_resend(user, token)
            except ImportError as e:
                print(f"=== RESEND IMPORT ERROR: {e} ===")
                print("=== FALLING BACK TO SMTP ===")
                return send_password_reset_email_smtp(user, token)
        else:
            # Use SMTP fallback (same as email confirmation)
            print("=== USING SMTP FALLBACK FOR PASSWORD RESET ===")
            return send_password_reset_email_smtp(user, token)
            
    except Exception as e:
        print(f"=== PASSWORD RESET ERROR: {str(e)} ===")
        import traceback
        print(f"=== TRACEBACK: {traceback.format_exc()} ===")
        
        current_app.logger.error(f"Failed to send password reset to {user.email}: {str(e)}")
        return False

def send_admin_password_reset_email(user, temp_password, language='ru'):
    """Send admin password reset email with temporary password"""
    try:
        print(f"=== ADMIN PASSWORD RESET EMAIL for {user.email} (lang: {language}) ===")
        
        # Check email provider
        email_provider = current_app.config.get('EMAIL_PROVIDER', 'smtp')
        print(f"=== EMAIL_PROVIDER: {email_provider} ===")
        
        if email_provider == 'resend':
            # Use Resend API
            from utils.resend_email_service import send_admin_password_reset_email_resend
            return send_admin_password_reset_email_resend(user, temp_password, language)
        else:
            # Use SMTP fallback
            return send_admin_password_reset_email_smtp(user, temp_password, language)
            
    except Exception as e:
        print(f"=== ADMIN PASSWORD RESET ERROR: {str(e)} ===")
        current_app.logger.error(f"Failed to send admin password reset email to {user.email}: {str(e)}")
        return False

def send_admin_password_reset_email_smtp(user, temp_password, language='ru'):
    """Send admin password reset email using SMTP"""
    try:
        print(f"=== SMTP ADMIN PASSWORD RESET for {user.email} ===")
        
        # Generate login URL
        base_url = current_app.config.get('BASE_URL', 'https://bigmentor.nl')
        login_url = f"{base_url}/auth/login"
        
        print(f"=== LOGIN_URL: {login_url} ===")
        
        # Check if email sending is suppressed
        mail_suppress = current_app.config.get('MAIL_SUPPRESS_SEND', False)
        if mail_suppress:
            print("=== EMAIL SENDING SUPPRESSED (TESTING MODE) ===")
            return True
        
        # Create message
        subject = "Сброс пароля - Mentora"
        
        # Render HTML template
        from flask import render_template_string
        try:
            with open(f'templates/emails/password_reset_admin_{language}.html', 'r', encoding='utf-8') as f:
                html_template = f.read()
            html_body = render_template_string(html_template, 
                                             user=user, 
                                             temp_password=temp_password,
                                             login_url=login_url)
        except Exception as e:
            print(f"=== ERROR RENDERING HTML TEMPLATE: {e} ===")
            html_body = f"""
            <h2>Сброс пароля - Mentora</h2>
            <p>Здравствуйте, {user.first_name}!</p>
            <p>Ваш пароль был сброшен администратором системы Mentora.</p>
            <p><strong>Ваш новый временный пароль: {temp_password}</strong></p>
            <p><a href="{login_url}">Войти в систему</a></p>
            """
        
        # Render text template
        try:
            with open(f'templates/emails/password_reset_admin_{language}.txt', 'r', encoding='utf-8') as f:
                text_template = f.read()
            text_body = render_template_string(text_template,
                                             user=user,
                                             temp_password=temp_password,
                                             login_url=login_url)
        except Exception as e:
            print(f"=== ERROR RENDERING TEXT TEMPLATE: {e} ===")
            text_body = f"""
            Mentora - Сброс пароля
            
            Здравствуйте, {user.first_name}!
            
            Ваш пароль был сброшен администратором системы Mentora.
            
            Ваш новый временный пароль: {temp_password}
            
            Войти в систему: {login_url}
            """
        
        # Create message
        msg = Message(
            subject=subject,
            recipients=[user.email],
            html=html_body,
            body=text_body,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@bigmentor.nl')
        )
        
        print(f"=== SENDING EMAIL TO: {user.email} ===")
        print(f"=== SUBJECT: {subject} ===")
        
        # Send email
        mail.send(msg)
        
        print(f"=== EMAIL SENT SUCCESSFULLY to {user.email} ===")
        return True
        
    except Exception as e:
        print(f"=== SMTP ADMIN PASSWORD RESET ERROR: {str(e)} ===")
        import traceback
        print(f"=== TRACEBACK: {traceback.format_exc()} ===")
        return False

def send_password_reset_email_smtp(user, token):
    """Send password reset email using SMTP"""
    try:
        print(f"=== SMTP PASSWORD RESET for {user.email} ===")
        
        # Generate reset URL
        base_url = current_app.config.get('BASE_URL', 'https://bigmentor.nl')
        reset_url = f"{base_url}/auth/reset-password/{token}"
        
        print(f"=== RESET_URL: {reset_url} ===")
        
        # Check if email sending is suppressed
        mail_suppress = current_app.config.get('MAIL_SUPPRESS_SEND', False)
        if mail_suppress:
            print("=== EMAIL SENDING SUPPRESSED (TESTING MODE) ===")
            return True
        
        # Create message
        subject = "Сброс пароля - Mentora"
        
        # Get HTML and text content
        html_body = get_password_reset_html(user, reset_url)
        text_body = get_password_reset_text(user, reset_url)
        
        # Create message
        msg = Message(
            subject=subject,
            recipients=[user.email],
            html=html_body,
            body=text_body,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@bigmentor.nl')
        )
        
        print(f"=== SENDING EMAIL TO: {user.email} ===")
        print(f"=== SUBJECT: {subject} ===")
        
        # Send email
        mail.send(msg)
        
        print(f"=== EMAIL SENT SUCCESSFULLY to {user.email} ===")
        return True
        
    except Exception as e:
        print(f"=== SMTP PASSWORD RESET ERROR: {str(e)} ===")
        import traceback
        print(f"=== TRACEBACK: {traceback.format_exc()} ===")
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


def send_invitation_email(contact, invitation):
    """Send invitation email to contact"""
    try:
        print(f"=== INVITATION EMAIL START for {contact.email} ===")
        
        # Check email provider
        email_provider = current_app.config.get('EMAIL_PROVIDER', 'smtp')
        print(f"=== EMAIL_PROVIDER: {email_provider} ===")
        
        if email_provider == 'resend':
            # Use Resend API
            from utils.resend_email_service import send_invitation_email_resend
            return send_invitation_email_resend(contact, invitation)
        else:
            # Use SMTP fallback
            return send_invitation_email_smtp(contact, invitation)
            
    except Exception as e:
        print(f"=== INVITATION EMAIL ERROR: {str(e)} ===")
        current_app.logger.error(f"Failed to send invitation email to {contact.email}: {str(e)}")
        return False


def send_invitation_email_smtp(contact, invitation):
    """Send invitation email using SMTP"""
    try:
        print(f"=== SMTP INVITATION EMAIL for {contact.email} ===")
        
        # Generate invitation URL
        base_url = current_app.config.get('BASE_URL', 'https://bigmentor.nl')
        invitation_url = f"{base_url}/auth/invite/{invitation.token}"
        
        print(f"=== INVITATION_URL: {invitation_url} ===")
        
        # Check if email sending is suppressed
        mail_suppress = current_app.config.get('MAIL_SUPPRESS_SEND', False)
        if mail_suppress:
            print(f"=== MAIL_SUPPRESS_SEND is True, skipping actual email send ===")
            return True
        
        # Create message
        msg = Message(
            subject="You're invited to join Mentora!",
            recipients=[contact.email],
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@bigmentor.nl')
        )
        
        # Email body
        msg.body = f"""
Hello {contact.full_name}!

You have been invited to join Mentora - the comprehensive platform for medical professionals preparing for the BIG exam.

To complete your registration, please click the link below and set your password:

{invitation_url}

This invitation will expire on {invitation.expires_at.strftime('%B %d, %Y at %H:%M')}.

{f"Personal message: {invitation.message}" if invitation.message else ""}

Once you complete your registration, you will have access to:
- Comprehensive study materials
- Practice exams and questions
- Progress tracking
- Expert guidance and support

If you have any questions, please don't hesitate to contact us.

Best regards,
Mentora Team
        """
        
        # HTML version
        msg.html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Invitation to Mentora</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #3498db, #2980b9); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; background: #3498db; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .button:hover {{ background: #2980b9; }}
                .features {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .feature {{ margin: 10px 0; }}
                .footer {{ text-align: center; margin-top: 30px; color: #7f8c8d; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to Mentora!</h1>
                    <p>Your invitation to join our platform</p>
                </div>
                
                <div class="content">
                    <h2>Hello {contact.full_name}!</h2>
                    
                    <p>You have been invited to join <strong>Mentora</strong> - the comprehensive platform for dental professionals preparing for the BIG exam.</p>
                    
                    <p>To complete your registration, please click the button below and set your password:</p>
                    
                    <div style="text-align: center;">
                        <a href="{invitation_url}" class="button">Complete Registration</a>
                    </div>
                    
                    <p><strong>Important:</strong> This invitation will expire on {invitation.expires_at.strftime('%B %d, %Y at %H:%M')}.</p>
                    
                    {f'<div style="background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 20px 0;"><strong>Personal message:</strong><br>{invitation.message}</div>' if invitation.message else ''}
                    
                    <div class="features">
                        <h3>What you'll get access to:</h3>
                        <div class="feature">📚 Comprehensive study materials</div>
                        <div class="feature">📝 Practice exams and questions</div>
                        <div class="feature">📊 Progress tracking</div>
                        <div class="feature">👨‍⚕️ Expert guidance and support</div>
                    </div>
                    
                    <p>If you have any questions, please don't hesitate to contact us.</p>
                    
                    <div class="footer">
                        <p>Best regards,<br>Mentora Team</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        mail.send(msg)
        
        current_app.logger.info(f"Invitation email sent to {contact.email}")
        return True
        
    except Exception as e:
        print(f"=== INVITATION EMAIL ERROR: {str(e)} ===")
        current_app.logger.error(f"Failed to send invitation email: {str(e)}")
        return False


def send_invitation_with_password(user, temp_password, token=None):
    """Send invitation email with temporary password"""
    try:
        print(f"=== INVITATION WITH PASSWORD START for {user.email} ===")
        
        # Use provided token or generate new one
        if not token:
            token = user.generate_email_confirmation_token()
        
        confirmation_url = f"{current_app.config.get('BASE_URL', 'https://bigmentor.nl')}/auth/confirm-email/{token}"
        
        print(f"=== INVITATION_URL: {confirmation_url} ===")
        print(f"=== TEMP_PASSWORD: {temp_password} ===")
        
        # Check email provider
        email_provider = current_app.config.get('EMAIL_PROVIDER', 'smtp')
        print(f"=== EMAIL_PROVIDER: {email_provider} ===")
        
        if email_provider == 'resend':
            # Use Resend API
            from utils.resend_email_service import send_invitation_with_password_resend
            return send_invitation_with_password_resend(user, temp_password, token)
        else:
            # Use SMTP fallback
            return send_invitation_with_password_smtp(user, temp_password, token)
            
    except Exception as e:
        print(f"=== INVITATION WITH PASSWORD ERROR: {str(e)} ===")
        current_app.logger.error(f"Failed to send invitation with password to {user.email}: {str(e)}")
        return False


def send_invitation_with_password_smtp(user, temp_password, token):
    """Send invitation with password using SMTP"""
    try:
        print(f"=== SMTP INVITATION WITH PASSWORD for {user.email} ===")
        
        confirmation_url = f"{current_app.config.get('BASE_URL', 'https://bigmentor.nl')}/auth/confirm-email/{token}"
        
        # Check if email sending is suppressed
        mail_suppress = current_app.config.get('MAIL_SUPPRESS_SEND', False)
        if mail_suppress:
            print(f"=== MAIL_SUPPRESS_SEND is True, skipping actual email send ===")
            print(f"=== INVITATION EMAIL CONTENT ===")
            print(f"To: {user.email}")
            print(f"Subject: Welcome to Mentora - Your Account Details")
            print(f"Confirmation URL: {confirmation_url}")
            print(f"Temporary Password: {temp_password}")
            print(f"=== END INVITATION EMAIL CONTENT ===")
            return True
        
        # Create message
        msg = Message(
            subject="Welcome to Mentora - Your Account Details",
            recipients=[user.email],
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'Mentora <info@bigmentor.nl>')
        )
        
        # HTML content
        msg.html = get_invitation_with_password_html(user, confirmation_url, temp_password)
        
        # Text content
        msg.body = get_invitation_with_password_text(user, confirmation_url, temp_password)
        
        # Send email
        mail = current_app.extensions.get('mail')
        if mail:
            mail.send(msg)
            print(f"=== INVITATION WITH PASSWORD EMAIL SENT via SMTP ===")
        else:
            print(f"=== MAIL EXTENSION NOT FOUND ===")
            return False
        
        current_app.logger.info(f"Invitation with password email sent to {user.email}")
        return True
        
    except Exception as e:
        print(f"=== INVITATION WITH PASSWORD ERROR: {str(e)} ===")
        current_app.logger.error(f"Failed to send invitation with password email: {str(e)}")
        return False


def get_invitation_with_password_html(user, confirmation_url, temp_password):
    """Generate HTML content for invitation with password email"""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welcome to Mentora</title>
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
                <h2 style="color: #2d3748; margin-top: 0; font-size: 24px;">Welcome to Mentora, {user.first_name}!</h2>
                
                <p style="color: #4a5568; font-size: 16px; line-height: 1.6;">
                    You have been invited to join Mentora - the comprehensive platform for medical professionals preparing for the BIG exam.
                </p>
                
                <p style="color: #4a5568; font-size: 16px; line-height: 1.6;">
                    <strong>Your account has been created with the following credentials:</strong>
                </p>
                
                <!-- Login Credentials -->
                <div style="background-color: #e6fffa; border: 2px solid #3ECDC1; border-radius: 8px; padding: 20px; margin: 30px 0;">
                    <h3 style="color: #2d3748; margin: 0 0 15px 0; font-size: 18px;">🔑 Your Login Credentials</h3>
                    <p style="color: #4a5568; font-size: 16px; line-height: 1.6; margin: 0 0 15px 0;">
                        <strong>📧 Email:</strong> {user.email}<br>
                        <strong>🔑 Temporary Password:</strong>
                    </p>
                    <div style="background-color: #ffffff; border: 2px solid #3ECDC1; border-radius: 6px; padding: 15px; text-align: center; margin: 15px 0;">
                        <p style="color: #2d3748; font-size: 20px; font-weight: bold; font-family: monospace; margin: 0; letter-spacing: 2px;">
                            {temp_password}
                        </p>
                    </div>
                    <p style="color: #4a5568; font-size: 14px; line-height: 1.5; margin: 15px 0 0 0;">
                        <strong>Important:</strong> Please save this password securely. You can change it after confirming your email and logging in.
                    </p>
                </div>
                
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
                        ✅ Confirm Email & Activate Account
                    </a>
                </div>
                
                <!-- Next Steps -->
                <div style="background-color: #fef5e7; border-left: 4px solid #f6ad55; padding: 20px; margin: 30px 0;">
                    <h3 style="color: #744210; margin: 0 0 15px 0; font-size: 18px;">🚀 What happens next?</h3>
                    <ol style="color: #744210; font-size: 14px; line-height: 1.6; margin: 0; padding-left: 20px;">
                        <li>Click the "Confirm Email & Activate Account" button above</li>
                        <li>You'll be redirected to the login page</li>
                        <li>Use your email and the temporary password to log in</li>
                        <li>You can change your password in your profile settings</li>
                        <li>Start exploring the Mentora learning platform!</li>
                    </ol>
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
                    If you did not expect this invitation, please ignore this email.
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


def get_invitation_with_password_text(user, confirmation_url, temp_password):
    """Generate text content for invitation with password email"""
    return f"""
MENTORA - Welcome to Your Account

Hello, {user.first_name}!

You have been invited to join Mentora - the comprehensive platform for medical professionals preparing for the BIG exam.

YOUR ACCOUNT CREDENTIALS:
📧 Email: {user.email}
🔑 Temporary Password: {temp_password}

🚀 WHAT HAPPENS NEXT:
1. Click the confirmation link below
2. You'll be redirected to the login page
3. Use your email and the temporary password to log in
4. You can change your password in your profile settings
5. Start exploring the Mentora learning platform!

Confirmation link:
{confirmation_url}

If the link doesn't work, copy and paste it into your browser address bar.

Important: This link is valid for 24 hours. After that, you will need to request a new confirmation link.

If you did not expect this invitation, please ignore this email.

Best regards,
The Mentora Team

Email: info@bigmentor.nl
Website: https://bigmentor.nl

© 2024 Mentora. All rights reserved.
"""


def send_admin_alert_email(admin_email, subject, message):
    """Send alert email to admin"""
    try:
        print(f"=== ADMIN ALERT EMAIL to {admin_email} ===")
        
        # Check if email sending is suppressed
        mail_suppress = current_app.config.get('MAIL_SUPPRESS_SEND', False)
        if mail_suppress:
            print(f"=== MAIL_SUPPRESS_SEND is True, skipping admin alert email ===")
            return True
        
        # Create message
        msg = Message(
            subject=subject,
            recipients=[admin_email],
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@bigmentor.nl')
        )
        
        # Email body
        msg.body = message
        
        # HTML version
        msg.html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Admin Alert</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 800px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #dc3545; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                .alert {{ background: #fff3cd; color: #856404; padding: 15px; border-radius: 5px; margin: 20px 0; border: 1px solid #ffeaa7; }}
                .code {{ background: #f8f9fa; padding: 15px; border-radius: 5px; font-family: monospace; white-space: pre-wrap; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚨 Admin Alert</h1>
                    <p>Critical System Event</p>
                </div>
                
                <div class="content">
                    <div class="alert">
                        <strong>⚠️ Attention Required:</strong> A critical error has occurred in the registration system.
                    </div>
                    
                    <h2>Alert Details</h2>
                    <div class="code">{message}</div>
                    
                    <p><strong>Action Required:</strong> Please investigate this issue and take appropriate action.</p>
                    
                    <p>This is an automated alert from the Mentora registration system.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        mail.send(msg)
        
        current_app.logger.info(f"Admin alert email sent to {admin_email}")
        return True
        
    except Exception as e:
        print(f"=== ADMIN ALERT EMAIL ERROR: {str(e)} ===")
        current_app.logger.error(f"Failed to send admin alert email: {str(e)}")
        return False
