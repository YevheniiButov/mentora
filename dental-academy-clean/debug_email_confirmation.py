#!/usr/bin/env python3
"""
Диагностический скрипт для проверки email подтверждения
"""

import os
import sys
from flask import Flask, url_for
from app import app
from models import User, db
from datetime import datetime, timezone, timedelta

def debug_email_confirmation():
    """Диагностика проблем с email подтверждением"""
    
    with app.app_context():
        print("🔍 EMAIL CONFIRMATION DIAGNOSTICS")
        print("=" * 50)
        
        # 1. Проверяем настройки
        print("\n📧 EMAIL SETTINGS:")
        print(f"   EMAIL_PROVIDER: {app.config.get('EMAIL_PROVIDER')}")
        print(f"   MAIL_SUPPRESS_SEND: {app.config.get('MAIL_SUPPRESS_SEND')}")
        print(f"   BASE_URL: {app.config.get('BASE_URL')}")
        print(f"   RESEND_API_KEY: {'SET' if app.config.get('RESEND_API_KEY') else 'NOT SET'}")
        
        # 2. Проверяем маршрут
        print("\n🔗 ROUTE CHECK:")
        try:
            test_url = url_for('auth.confirm_email', token='test-token-123')
            print(f"   ✅ Route exists: {test_url}")
        except Exception as e:
            print(f"   ❌ Route error: {e}")
        
        # 3. Проверяем пользователей с неподтвержденными email
        print("\n👥 USERS WITH UNCONFIRMED EMAIL:")
        unconfirmed_users = User.query.filter_by(email_confirmed=False).all()
        print(f"   Found {len(unconfirmed_users)} users with unconfirmed email")
        
        for user in unconfirmed_users[:5]:  # Показываем только первых 5
            print(f"   - {user.email} (created: {user.created_at})")
            if user.email_confirmation_token:
                print(f"     Token: {user.email_confirmation_token[:20]}...")
            if user.email_confirmation_sent_at:
                print(f"     Sent at: {user.email_confirmation_sent_at}")
        
        # 4. Проверяем токены
        print("\n🔑 TOKEN ANALYSIS:")
        for user in unconfirmed_users[:3]:  # Анализируем только первых 3
            if user.email_confirmation_token and user.email_confirmation_sent_at:
                print(f"\n   User: {user.email}")
                print(f"   Token hash: {user.email_confirmation_token[:20]}...")
                print(f"   Sent at: {user.email_confirmation_sent_at}")
                
                # Проверяем срок действия
                sent_at = user.email_confirmation_sent_at
                if sent_at.tzinfo is None:
                    sent_at = sent_at.replace(tzinfo=timezone.utc)
                
                expiry_seconds = app.config.get('EMAIL_CONFIRMATION_EXPIRES', 86400)
                expiry_time = sent_at + timedelta(seconds=expiry_seconds)
                current_time = datetime.now(timezone.utc)
                
                print(f"   Expiry time: {expiry_time}")
                print(f"   Current time: {current_time}")
                print(f"   Time until expiry: {(expiry_time - current_time).total_seconds()} seconds")
                
                if current_time > expiry_time:
                    print(f"   ❌ TOKEN EXPIRED!")
                else:
                    print(f"   ✅ Token still valid")
        
        # 5. Тестируем генерацию URL
        print("\n🌐 URL GENERATION TEST:")
        test_token = "test-token-12345"
        base_url = app.config.get('BASE_URL', 'https://bigmentor.nl')
        test_url = f"{base_url}/auth/confirm-email/{test_token}"
        print(f"   Generated URL: {test_url}")
        
        # 6. Проверяем шаблоны email
        print("\n📄 EMAIL TEMPLATES:")
        try:
            from utils.email_service import get_confirmation_email_html, get_confirmation_email_text
            
            # Создаем тестового пользователя
            test_user = User()
            test_user.first_name = "Test"
            test_user.email = "test@example.com"
            
            html_content = get_confirmation_email_html(test_user, test_url)
            text_content = get_confirmation_email_text(test_user, test_url)
            
            print(f"   ✅ HTML template: {len(html_content)} characters")
            print(f"   ✅ Text template: {len(text_content)} characters")
            
            # Проверяем, содержит ли URL
            if test_url in html_content:
                print(f"   ✅ URL found in HTML template")
            else:
                print(f"   ❌ URL NOT found in HTML template")
                
            if test_url in text_content:
                print(f"   ✅ URL found in text template")
            else:
                print(f"   ❌ URL NOT found in text template")
                
        except Exception as e:
            print(f"   ❌ Template error: {e}")
        
        print("\n" + "=" * 50)
        print("🔍 DIAGNOSTICS COMPLETE")

if __name__ == "__main__":
    debug_email_confirmation()