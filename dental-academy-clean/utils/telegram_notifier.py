"""
Telegram bot notifications for system events.

This module provides functions for sending notifications to Telegram
when critical system events occur.
"""

import logging
import os
import requests
from typing import Optional

logger = logging.getLogger(__name__)

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


def send_telegram_message(message: str, parse_mode: str = 'HTML') -> bool:
    """
    Отправляет сообщение в Telegram.
    
    Args:
        message: Текст сообщения
        parse_mode: Режим парсинга ('HTML' или 'Markdown')
    
    Returns:
        bool: True если сообщение отправлено успешно
    """
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram bot token or chat ID not configured")
        return False
    
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': parse_mode
        }
        
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        
        logger.info("Telegram notification sent successfully")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to send Telegram notification: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending Telegram notification: {e}")
        return False


def send_event_notification(event_type: str, severity: str, title: str, 
                           message: str = None, user_email: str = None,
                           request_url: str = None) -> bool:
    """
    Отправляет уведомление о системном событии в Telegram.
    
    Args:
        event_type: Тип события
        severity: Уровень серьезности
        title: Заголовок события
        message: Подробное сообщение
        user_email: Email пользователя
        request_url: URL запроса
    
    Returns:
        bool: True если уведомление отправлено
    """
    # Формируем эмодзи в зависимости от серьезности
    emoji_map = {
        'critical': '🔴',
        'error': '🟠',
        'warning': '🟡',
        'info': '🔵'
    }
    emoji = emoji_map.get(severity, '⚪')
    
    # Формируем сообщение
    telegram_message = f"{emoji} <b>{severity.upper()}</b> - {title}\n\n"
    
    if event_type:
        telegram_message += f"<b>Type:</b> {event_type}\n"
    
    if user_email:
        telegram_message += f"<b>User:</b> {user_email}\n"
    
    if request_url:
        # Обрезаем URL для Telegram
        short_url = request_url[:50] + '...' if len(request_url) > 50 else request_url
        telegram_message += f"<b>URL:</b> {short_url}\n"
    
    if message:
        # Обрезаем сообщение для Telegram (макс 4000 символов)
        short_message = message[:500] + '...' if len(message) > 500 else message
        telegram_message += f"\n{short_message}"
    
    telegram_message += f"\n\n<a href='https://bigmentor.nl/admin/monitoring/events'>View in Admin Panel</a>"
    
    return send_telegram_message(telegram_message)


def send_critical_error_notification(title: str, message: str = None, 
                                    traceback: str = None, user_email: str = None,
                                    request_url: str = None) -> bool:
    """
    Отправляет уведомление о критической ошибке в Telegram.
    
    Args:
        title: Заголовок ошибки
        message: Сообщение об ошибке
        traceback: Traceback ошибки
        user_email: Email пользователя
        request_url: URL запроса
    
    Returns:
        bool: True если уведомление отправлено
    """
    telegram_message = f"🔴 <b>CRITICAL ERROR</b>\n\n"
    telegram_message += f"<b>{title}</b>\n\n"
    
    if user_email:
        telegram_message += f"<b>User:</b> {user_email}\n"
    
    if request_url:
        short_url = request_url[:50] + '...' if len(request_url) > 50 else request_url
        telegram_message += f"<b>URL:</b> {short_url}\n"
    
    if message:
        short_message = message[:300] + '...' if len(message) > 300 else message
        telegram_message += f"\n{short_message}"
    
    if traceback:
        # Берем только последние строки traceback
        traceback_lines = traceback.split('\n')
        last_lines = '\n'.join(traceback_lines[-10:])  # Последние 10 строк
        telegram_message += f"\n\n<code>{last_lines[:500]}</code>"
    
    telegram_message += f"\n\n<a href='https://bigmentor.nl/admin/monitoring/events'>View Details</a>"
    
    return send_telegram_message(telegram_message)


def send_new_registration_notification(user_email: str, registration_method: str = 'email') -> bool:
    """
    Отправляет уведомление о новой регистрации в Telegram.
    
    Args:
        user_email: Email нового пользователя
        registration_method: Метод регистрации
    
    Returns:
        bool: True если уведомление отправлено
    """
    telegram_message = f"🆕 <b>New User Registration</b>\n\n"
    telegram_message += f"<b>Email:</b> {user_email}\n"
    telegram_message += f"<b>Method:</b> {registration_method}\n"
    telegram_message += f"\n<a href='https://bigmentor.nl/admin/monitoring/events'>View in Admin Panel</a>"
    
    return send_telegram_message(telegram_message)


def send_user_login_notification(user_email: str, user_id: int = None) -> bool:
    """
    Отправляет уведомление о входе пользователя в Telegram.
    
    Args:
        user_email: Email пользователя
        user_id: ID пользователя (опционально)
    
    Returns:
        bool: True если уведомление отправлено
    """
    telegram_message = f"🟢 <b>User Logged In</b>\n\n"
    telegram_message += f"<b>Email:</b> {user_email}\n"
    if user_id:
        telegram_message += f"<b>User ID:</b> {user_id}\n"
    telegram_message += f"\n<a href='https://bigmentor.nl/admin/monitoring/events'>View in Admin Panel</a>"
    
    return send_telegram_message(telegram_message)

