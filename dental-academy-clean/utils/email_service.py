# utils/email_service.py - Email Service Functions

import secrets
import string
from datetime import datetime, timezone, timedelta
from flask import current_app, render_template, url_for
from flask_mail import Message
from extensions import mail
from models import User, db

def generate_confirmation_token():
    """Generate a secure confirmation token"""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))

def send_welcome_email(user):
    """Send welcome email to new user"""
    try:
        # Generate confirmation token
        token = generate_confirmation_token()
        user.email_confirmation_token = token
        user.email_confirmation_sent_at = datetime.now(timezone.utc)
        db.session.commit()
        
        # Create confirmation URL
        confirm_url = url_for('auth.confirm_email', token=token, _external=True)
        
        # Create email message
        msg = Message(
            subject='Welcome to Mentora - Please Confirm Your Email',
            recipients=[user.email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # Email body
        msg.html = render_template('emails/welcome.html', 
                                 user=user, 
                                 confirm_url=confirm_url)
        msg.body = f"""
Welcome to Mentora, {user.first_name}!

Thank you for registering with Mentora. To complete your registration and activate your account, please confirm your email address by clicking the link below:

{confirm_url}

If you did not register for Mentora, please ignore this email.

Best regards,
The Mentora Team
        """
        
        # Send email
        if not current_app.config.get('MAIL_SUPPRESS_SEND', False):
            mail.send(msg)
            current_app.logger.info(f"Welcome email sent to {user.email}")
        else:
            current_app.logger.info(f"Welcome email suppressed for {user.email} (MAIL_SUPPRESS_SEND=True)")
            
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
        return False

def send_password_reset_email(user):
    """Send password reset email to user"""
    try:
        # Generate reset token
        token = generate_confirmation_token()
        user.password_reset_token = token
        user.password_reset_sent_at = datetime.now(timezone.utc)
        db.session.commit()
        
        # Create reset URL
        reset_url = url_for('auth.reset_password', token=token, _external=True)
        
        # Create email message
        msg = Message(
            subject='Reset Your Mentora Password',
            recipients=[user.email],
            sender=current_app.config['MAIL_DEFAULT_SENDER']
        )
        
        # Email body
        msg.html = render_template('emails/password_reset.html', 
                                 user=user, 
                                 reset_url=reset_url)
        msg.body = f"""
Hello {user.first_name},

You requested a password reset for your Mentora account. To reset your password, click the link below:

{reset_url}

This link will expire in 1 hour for security reasons.

If you did not request a password reset, please ignore this email.

Best regards,
The Mentora Team
        """
        
        # Send email
        if not current_app.config.get('MAIL_SUPPRESS_SEND', False):
            mail.send(msg)
            current_app.logger.info(f"Password reset email sent to {user.email}")
        else:
            current_app.logger.info(f"Password reset email suppressed for {user.email} (MAIL_SUPPRESS_SEND=True)")
            
        return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send password reset email to {user.email}: {str(e)}")
        return False

def send_email_confirmation(user):
    """Send email confirmation to user"""
    return send_welcome_email(user)  # Same function for now

def is_token_valid(user, token, token_type='confirmation'):
    """Check if email confirmation or password reset token is valid"""
    try:
        if token_type == 'confirmation':
            stored_token = user.email_confirmation_token
            sent_at = user.email_confirmation_sent_at
        elif token_type == 'reset':
            stored_token = user.password_reset_token
            sent_at = user.password_reset_sent_at
        else:
            return False
            
        if not stored_token or not sent_at:
            return False
            
        # Check if token matches
        if stored_token != token:
            return False
            
        # Check if token is not expired (24 hours for confirmation, 1 hour for reset)
        expiry_hours = 24 if token_type == 'confirmation' else 1
        expiry_time = sent_at + timedelta(hours=expiry_hours)
        
        if datetime.now(timezone.utc) > expiry_time:
            return False
            
        return True
        
    except Exception as e:
        current_app.logger.error(f"Error validating {token_type} token: {str(e)}")
        return False