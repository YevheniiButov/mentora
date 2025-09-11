#!/usr/bin/env python3
"""
Скрипт для генерации превью email подтверждения
"""

from flask import Flask, render_template
import os

# Создаем Flask app для рендеринга шаблонов
app = Flask(__name__)
app.config['BASE_URL'] = 'https://mentora.com.in'

# Мокаем пользователя
class MockUser:
    def __init__(self):
        self.first_name = "John"
        self.last_name = "Doe"
        self.email = "john.doe@example.com"

# Мокаем токен
mock_token = "test_token_123456789"

with app.app_context():
    # Генерируем URLs
    base_url = app.config.get('BASE_URL', 'https://mentora.com.in')
    confirmation_url = f"{base_url}/auth/confirm-email/{mock_token}"
    unsubscribe_url = f"{base_url}/auth/unsubscribe/1"
    privacy_policy_url = f"{base_url}/privacy"
    
    # Рендерим HTML версию
    html_content = render_template('emails/confirm_email.html', 
                                 user=MockUser(), 
                                 confirmation_url=confirmation_url,
                                 unsubscribe_url=unsubscribe_url,
                                 privacy_policy_url=privacy_policy_url)
    
    # Сохраняем в файл
    with open('email_preview.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✅ Email превью создан: email_preview.html")
    print("📧 Откройте файл в браузере для скриншота")
    print(f"🔗 Confirmation URL: {confirmation_url}")
    print(f"🔗 Unsubscribe URL: {unsubscribe_url}")
    print(f"🔗 Privacy Policy URL: {privacy_policy_url}")
