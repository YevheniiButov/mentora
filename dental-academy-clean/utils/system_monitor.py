"""
System monitoring and event logging utility.

This module provides functions for logging system events, errors, and user activities
with automatic email notifications for critical issues.
"""

import traceback
import logging
from datetime import datetime, timezone
from flask import request, current_app, g
from flask_login import current_user
from models import SystemEvent, db
from utils.resend_email_service import send_email_via_resend

logger = logging.getLogger(__name__)

def get_admin_email():
    """Получает email администратора из конфигурации Flask"""
    try:
        # Пытаемся получить из конфигурации Flask
        admin_email = current_app.config.get('ADMIN_EMAIL')
        if admin_email:
            return admin_email
    except:
        pass
    
    # Fallback: пытаемся получить из переменных окружения
    import os
    admin_email = os.getenv('ADMIN_EMAIL')
    if admin_email:
        return admin_email
    
    # Последний fallback: используем дефолтный email
    return 'admin@bigmentor.nl'


def get_request_info():
    """Собирает информацию о текущем запросе"""
    try:
        return {
            'ip_address': request.remote_addr if request else None,
            'user_agent': request.headers.get('User-Agent') if request else None,
            'request_url': request.url if request else None,
            'request_method': request.method if request else None,
        }
    except:
        return {}


def log_event(
    event_type: str,
    severity: str,
    title: str,
    message: str = None,
    user_id: int = None,
    user_email: str = None,
    error_traceback: str = None,
    metadata: dict = None,
    send_email: bool = False
):
    """
    Логирует системное событие в базу данных.
    
    Args:
        event_type: Тип события ('error', 'login', 'registration', 'warning', 'info')
        severity: Уровень серьезности ('critical', 'error', 'warning', 'info')
        title: Краткое описание события
        message: Подробное сообщение
        user_id: ID пользователя (если применимо)
        user_email: Email пользователя (если user_id неизвестен)
        error_traceback: Полный traceback для ошибок
        metadata: Дополнительные данные в виде словаря
        send_email: Отправить email уведомление (автоматически для critical/error)
    """
    try:
        # Получаем информацию о запросе
        request_info = get_request_info()
        
        # Определяем user_id и user_email
        if not user_id and current_user and current_user.is_authenticated:
            user_id = current_user.id
            user_email = user_email or current_user.email
        
        # Создаем событие
        event = SystemEvent(
            event_type=event_type,
            severity=severity,
            title=title,
            message=message,
            user_id=user_id,
            user_email=user_email,
            ip_address=request_info.get('ip_address'),
            user_agent=request_info.get('user_agent'),
            request_url=request_info.get('request_url'),
            request_method=request_info.get('request_method'),
            error_traceback=error_traceback
        )
        
        if metadata:
            event.set_metadata(metadata)
        
        db.session.add(event)
        db.session.commit()
        
        # Отправляем email для критических ошибок или если явно запрошено
        should_send_email = send_email or severity in ('critical', 'error')
        if should_send_email:
            try:
                send_event_notification_email(event)
                event.email_sent = True
                event.email_sent_at = datetime.now(timezone.utc)
                db.session.commit()
            except Exception as e:
                logger.error(f"Failed to send notification email for event {event.id}: {e}")
        
        # Отправляем Telegram уведомление для критических событий
        if severity in ('critical', 'error'):
            try:
                from utils.telegram_notifier import send_event_notification
                send_event_notification(
                    event_type=event_type,
                    severity=severity,
                    title=title,
                    message=message,
                    user_email=user_email,
                    request_url=request_info.get('request_url')
                )
            except Exception as e:
                logger.error(f"Failed to send Telegram notification for event {event.id}: {e}")
        
        logger.info(f"System event logged: {event_type} {severity} - {title}")
        return event
        
    except Exception as e:
        logger.error(f"Failed to log system event: {e}", exc_info=True)
        return None


def log_error(
    title: str,
    message: str = None,
    exception: Exception = None,
    user_id: int = None,
    metadata: dict = None,
    send_email: bool = True
):
    """
    Логирует ошибку в систему.
    
    Args:
        title: Краткое описание ошибки
        message: Подробное сообщение
        exception: Объект исключения (для получения traceback)
        user_id: ID пользователя (если применимо)
        metadata: Дополнительные данные
        send_email: Отправить email уведомление
    """
    error_traceback = None
    if exception:
        error_traceback = ''.join(traceback.format_exception(type(exception), exception, exception.__traceback__))
    
    severity = 'critical' if send_email else 'error'
    
    return log_event(
        event_type='error',
        severity=severity,
        title=title,
        message=message or str(exception) if exception else None,
        user_id=user_id,
        error_traceback=error_traceback,
        metadata=metadata,
        send_email=send_email
    )


def log_user_login(user_id: int, user_email: str, success: bool = True, error_message: str = None):
    """
    Логирует попытку входа пользователя.
    
    Args:
        user_id: ID пользователя (None если вход неудачный)
        user_email: Email пользователя
        success: Успешный ли вход
        error_message: Сообщение об ошибке (если вход неудачный)
    """
    if success:
        # Проверяем, является ли пользователь админом
        is_admin = False
        if user_id:
            try:
                from models import User
                user = User.query.get(user_id)
                if user:
                    is_admin = user.is_admin
            except Exception as e:
                logger.warning(f"Could not check admin status for user {user_id}: {e}")
        
        log_event(
            event_type='login',
            severity='info',
            title=f'User login: {user_email}',
            message=f'User {user_email} successfully logged in',
            user_id=user_id,
            user_email=user_email,
            send_email=False
        )
        
        # Отправляем Telegram уведомление только для не-админов
        if not is_admin:
            try:
                from utils.telegram_notifier import send_user_login_notification
                send_user_login_notification(user_email, user_id)
            except Exception as e:
                logger.error(f"Failed to send Telegram notification for login: {e}")
    else:
        log_event(
            event_type='login',
            severity='warning',
            title=f'Failed login attempt: {user_email}',
            message=error_message or 'Invalid credentials',
            user_email=user_email,
            send_email=False
        )


def log_user_registration(user_id: int, user_email: str, registration_method: str = 'email'):
    """
    Логирует регистрацию нового пользователя.
    
    Args:
        user_id: ID нового пользователя
        user_email: Email пользователя
        registration_method: Метод регистрации ('email', 'digid', etc.)
    """
    log_event(
        event_type='registration',
        severity='info',
        title=f'New user registration: {user_email}',
        message=f'User registered via {registration_method}',
        user_id=user_id,
        user_email=user_email,
        metadata={'registration_method': registration_method},
        send_email=True  # Отправляем уведомление о новой регистрации
    )
    
    # Отправляем Telegram уведомление о новой регистрации
    try:
        from utils.telegram_notifier import send_new_registration_notification
        send_new_registration_notification(user_email, registration_method)
    except Exception as e:
        logger.error(f"Failed to send Telegram notification for registration: {e}")


def send_event_notification_email(event: SystemEvent):
    """
    Отправляет email уведомление о событии администратору.
    
    Args:
        event: Объект SystemEvent
    """
    try:
        # Формируем тему письма
        subject = f"[{event.severity.upper()}] {event.title}"
        
        # Формируем тело письма
        body_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: {'#dc3545' if event.severity == 'critical' else '#ffc107' if event.severity == 'error' else '#17a2b8'}; color: white; padding: 15px; }}
                .content {{ padding: 20px; }}
                .info-row {{ margin: 10px 0; }}
                .label {{ font-weight: bold; }}
                .traceback {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; font-family: monospace; white-space: pre-wrap; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h2>{event.title}</h2>
            </div>
            <div class="content">
                <div class="info-row">
                    <span class="label">Event Type:</span> {event.event_type}
                </div>
                <div class="info-row">
                    <span class="label">Severity:</span> {event.severity}
                </div>
                <div class="info-row">
                    <span class="label">Time:</span> {event.created_at.strftime('%Y-%m-%d %H:%M:%S UTC') if event.created_at else 'N/A'}
                </div>
                {f'<div class="info-row"><span class="label">User:</span> {event.user_email or f"ID: {event.user_id}"}</div>' if event.user_id or event.user_email else ''}
                {f'<div class="info-row"><span class="label">IP Address:</span> {event.ip_address}</div>' if event.ip_address else ''}
                {f'<div class="info-row"><span class="label">Request URL:</span> {event.request_url}</div>' if event.request_url else ''}
                {f'<div class="info-row"><span class="label">Message:</span> {event.message}</div>' if event.message else ''}
                {f'<div class="info-row"><span class="label">Traceback:</span><div class="traceback">{event.error_traceback}</div></div>' if event.error_traceback else ''}
                <div class="info-row">
                    <a href="https://bigmentor.nl/admin/monitoring/events/{event.id}" style="color: #007bff;">View in Admin Panel</a>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Отправляем email через Resend (используется та же система, что и для всех email в проекте)
        admin_email = get_admin_email()
        send_email_via_resend(
            to_email=admin_email,
            subject=subject,
            html_content=body_html
        )
        
    except Exception as e:
        logger.error(f"Failed to send event notification email: {e}", exc_info=True)
        raise

