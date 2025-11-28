# utils/registration_logger.py - Structured logging for registration processes

import logging
import json
from datetime import datetime
from flask import request, current_app
from flask_login import current_user
import traceback

class RegistrationLogger:
    """Structured logger for registration processes"""
    
    def __init__(self):
        self.logger = logging.getLogger('registration')
        self.logger.setLevel(logging.INFO)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler for all registration logs
        try:
            import os
            log_dir = os.path.join(os.getcwd(), 'logs')
            os.makedirs(log_dir, exist_ok=True)
            
            file_handler = logging.FileHandler(
                os.path.join(log_dir, 'registration.log'),
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
        except Exception as e:
            print(f"Warning: Could not create file handler: {e}")
        
        # Separate file for errors only
        try:
            error_handler = logging.FileHandler(
                os.path.join(log_dir, 'registration_errors.log'),
                encoding='utf-8'
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(formatter)
            self.logger.addHandler(error_handler)
        except Exception as e:
            print(f"Warning: Could not create error file handler: {e}")
    
    def _get_request_context(self):
        """Get request context information"""
        try:
            from flask import request
            return {
                'ip_address': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', ''),
                'referrer': request.headers.get('Referer', ''),
                'url': request.url,
                'method': request.method,
                'timestamp': datetime.utcnow().isoformat()
            }
        except (RuntimeError, ImportError):  # Working outside of request context
            return {
                'ip_address': 'N/A',
                'user_agent': 'N/A',
                'referrer': 'N/A',
                'url': 'N/A',
                'method': 'N/A',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _get_user_context(self):
        """Get current user context if available"""
        try:
            from flask_login import current_user
            if current_user and current_user.is_authenticated:
                return {
                    'user_id': current_user.id,
                    'user_email': current_user.email,
                    'user_type': 'authenticated'
                }
        except (RuntimeError, ImportError):
            pass
        return {'user_type': 'anonymous'}
    
    def log_registration_start(self, registration_type, form_data=None):
        """Log the start of a registration process"""
        context = {
            'event': 'registration_started',
            'registration_type': registration_type,
            'request_context': self._get_request_context(),
            'user_context': self._get_user_context()
        }
        
        if form_data:
            # Sanitize sensitive data
            sanitized_data = self._sanitize_form_data(form_data)
            context['form_data'] = sanitized_data
        
        self.logger.info(f"Registration started: {json.dumps(context, indent=2)}")
        self._save_to_database('registration_started', registration_type, 'INFO', context)
    
    def log_validation_error(self, registration_type, field, error_message, form_data=None):
        """Log validation errors"""
        context = {
            'event': 'validation_error',
            'registration_type': registration_type,
            'field': field,
            'error_message': error_message,
            'request_context': self._get_request_context(),
            'user_context': self._get_user_context()
        }
        
        if form_data:
            sanitized_data = self._sanitize_form_data(form_data)
            context['form_data'] = sanitized_data
        
        self.logger.warning(f"Validation error: {json.dumps(context, indent=2)}")
        self._save_to_database('validation_error', registration_type, 'WARNING', context)
    
    def log_business_logic_error(self, registration_type, error_type, error_message, form_data=None):
        """Log business logic errors (email exists, etc.)"""
        context = {
            'event': 'business_logic_error',
            'registration_type': registration_type,
            'error_type': error_type,
            'error_message': error_message,
            'request_context': self._get_request_context(),
            'user_context': self._get_user_context()
        }
        
        if form_data:
            sanitized_data = self._sanitize_form_data(form_data)
            context['form_data'] = sanitized_data
        
        self.logger.warning(f"Business logic error: {json.dumps(context, indent=2)}")
        self._save_to_database('business_logic_error', registration_type, 'WARNING', context)
    
    def log_database_error(self, registration_type, operation, error_message, form_data=None):
        """Log database-related errors"""
        context = {
            'event': 'database_error',
            'registration_type': registration_type,
            'operation': operation,
            'error_message': error_message,
            'request_context': self._get_request_context(),
            'user_context': self._get_user_context()
        }
        
        if form_data:
            sanitized_data = self._sanitize_form_data(form_data)
            context['form_data'] = sanitized_data
        
        self.logger.error(f"Database error: {json.dumps(context, indent=2)}")
        self._save_to_database('database_error', registration_type, 'ERROR', context)
    
    def log_email_error(self, registration_type, email_address, error_message, form_data=None):
        """Log email sending errors"""
        context = {
            'event': 'email_error',
            'registration_type': registration_type,
            'email_address': email_address,
            'error_message': error_message,
            'request_context': self._get_request_context(),
            'user_context': self._get_user_context()
        }
        
        if form_data:
            sanitized_data = self._sanitize_form_data(form_data)
            context['form_data'] = sanitized_data
        
        self.logger.error(f"Email error: {json.dumps(context, indent=2)}")
        self._save_to_database('email_error', registration_type, 'ERROR', context)
    
    def log_file_upload_error(self, registration_type, filename, error_message, form_data=None):
        """Log file upload errors"""
        context = {
            'event': 'file_upload_error',
            'registration_type': registration_type,
            'filename': filename,
            'error_message': error_message,
            'request_context': self._get_request_context(),
            'user_context': self._get_user_context()
        }
        
        if form_data:
            sanitized_data = self._sanitize_form_data(form_data)
            context['form_data'] = sanitized_data
        
        self.logger.error(f"File upload error: {json.dumps(context, indent=2)}")
        self._save_to_database('file_upload_error', registration_type, 'ERROR', context)
    
    def log_registration_success(self, registration_type, user_id, email, form_data=None):
        """Log successful registration"""
        context = {
            'event': 'registration_success',
            'registration_type': registration_type,
            'user_id': user_id,
            'email': email,
            'request_context': self._get_request_context(),
            'user_context': self._get_user_context()
        }
        
        if form_data:
            sanitized_data = self._sanitize_form_data(form_data)
            context['form_data'] = sanitized_data
        
        self.logger.info(f"Registration success: {json.dumps(context, indent=2)}")
        self._save_to_database('registration_success', registration_type, 'INFO', context)
    
    def log_unexpected_error(self, registration_type, error, form_data=None):
        """Log unexpected errors with full traceback"""
        context = {
            'event': 'unexpected_error',
            'registration_type': registration_type,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'request_context': self._get_request_context(),
            'user_context': self._get_user_context()
        }
        
        if form_data:
            sanitized_data = self._sanitize_form_data(form_data)
            context['form_data'] = sanitized_data
        
        self.logger.error(f"Unexpected error: {json.dumps(context, indent=2)}")
        self._save_to_database('unexpected_error', registration_type, 'ERROR', context)
        
        # Send admin notification for critical errors
        self._send_admin_notification('critical_error', context)
    
    def _sanitize_form_data(self, form_data):
        """Remove sensitive information from form data for logging"""
        if not form_data:
            return {}
        
        # Fields to sanitize (replace with asterisks)
        sensitive_fields = ['password', 'confirm_password', 'g-recaptcha-response']
        
        sanitized = {}
        for key, value in form_data.items():
            if key.lower() in sensitive_fields:
                sanitized[key] = '***' if value else None
            elif isinstance(value, str) and len(value) > 100:
                # Truncate very long values
                sanitized[key] = value[:100] + '...'
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _send_admin_notification(self, notification_type, context):
        """Send admin notification for critical events"""
        try:
            from flask import current_app
            
            # Get admin email from config
            admin_email = current_app.config.get('ADMIN_EMAIL')
            if not admin_email:
                return
            
            # Prepare notification data
            notification_data = {
                'type': notification_type,
                'timestamp': datetime.utcnow().isoformat(),
                'context': context
            }
            
            # Save notification to database for admin panel
            self._save_notification_to_db(notification_data)
            
            # Email уведомления отключены - используем только Telegram бот
            # if notification_type == 'critical_error':
            #     self._send_critical_error_email(admin_email, context)
                
        except Exception as e:
            # Don't let notification errors break the main flow
            print(f"Warning: Could not send admin notification: {e}")
    
    def _save_notification_to_db(self, notification_data):
        """Save notification to database for admin panel"""
        try:
            from models import db
            from datetime import datetime
            
            # Create a simple notification record
            notification = {
                'type': notification_data['type'],
                'data': json.dumps(notification_data['context']),
                'created_at': datetime.utcnow(),
                'read': False
            }
            
            # Save to a simple JSON file for now (can be moved to DB later)
            import os
            notifications_file = os.path.join(os.getcwd(), 'logs', 'admin_notifications.json')
            
            notifications = []
            if os.path.exists(notifications_file):
                try:
                    with open(notifications_file, 'r', encoding='utf-8') as f:
                        notifications = json.load(f)
                except:
                    notifications = []
            
            notifications.append(notification)
            
            # Keep only last 100 notifications
            if len(notifications) > 100:
                notifications = notifications[-100:]
            
            with open(notifications_file, 'w', encoding='utf-8') as f:
                json.dump(notifications, f, indent=2, ensure_ascii=False, default=str)
                
        except Exception as e:
            print(f"Warning: Could not save notification to DB: {e}")
    
    # Email уведомления отключены - используем только Telegram бот
    # def _send_critical_error_email(self, admin_email, context):
    #     """Send email notification for critical errors"""
    #     pass

    def _save_to_database(self, event_type, registration_type, level, context):
        """Save log entry to database"""
        try:
            from flask import current_app
            from models import RegistrationLog, db
            
            # Check if we're in an application context
            if not current_app:
                print("Warning: No Flask application context for database logging")
                return
            
            # Extract data from context
            request_context = context.get('request_context', {})
            user_context = context.get('user_context', {})
            form_data = context.get('form_data', {})
            
            # Extract email from form data if available
            registration_email = None
            if form_data and isinstance(form_data, dict):
                registration_email = form_data.get('email')
            
            # Use email from user context if not in form data
            if not registration_email:
                registration_email = user_context.get('user_email')
            
            # Create log entry
            # Note: field, error_code, error_message, form_data are stored in context but not in model
            # They are logged to file/console but not saved to database
            log_entry = RegistrationLog(
                event_type=event_type,
                registration_type=registration_type,
                level=level,
                ip_address=request_context.get('ip_address'),
                user_agent=request_context.get('user_agent'),
                referrer=request_context.get('referrer'),
                url=request_context.get('url'),
                method=request_context.get('method'),
                user_id=user_context.get('user_id'),
                user_email=registration_email,  # Use extracted email
                user_type=user_context.get('user_type')
            )
            
            db.session.add(log_entry)
            db.session.commit()
            
        except Exception as e:
            print(f"Warning: Could not save log to database: {e}")

# Global instance
registration_logger = RegistrationLogger()
