#!/usr/bin/env python3
"""
Скрипт для переключения с Resend на SMTP для отправки email
"""

import os
from app import app

def switch_to_smtp():
    """Переключает email провайдер на SMTP"""
    
    print("🔄 SWITCHING EMAIL PROVIDER TO SMTP")
    print("=" * 50)
    
    # Проверяем текущие настройки
    print("📧 CURRENT EMAIL SETTINGS:")
    print(f"   EMAIL_PROVIDER: {app.config.get('EMAIL_PROVIDER')}")
    print(f"   MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
    print(f"   MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
    print(f"   RESEND_API_KEY: {'SET' if app.config.get('RESEND_API_KEY') else 'NOT SET'}")
    
    # Рекомендации по настройке SMTP
    print("\n🔧 SMTP CONFIGURATION RECOMMENDATIONS:")
    print("=" * 50)
    
    print("\n1. Gmail SMTP (рекомендуется):")
    print("   EMAIL_PROVIDER=smtp")
    print("   MAIL_SERVER=smtp.gmail.com")
    print("   MAIL_PORT=587")
    print("   MAIL_USE_TLS=true")
    print("   MAIL_USERNAME=your-email@gmail.com")
    print("   MAIL_PASSWORD=your-app-password")
    print("   MAIL_DEFAULT_SENDER=Mentora <info@bigmentor.nl>")
    
    print("\n2. Outlook SMTP:")
    print("   EMAIL_PROVIDER=smtp")
    print("   MAIL_SERVER=smtp-mail.outlook.com")
    print("   MAIL_PORT=587")
    print("   MAIL_USE_TLS=true")
    print("   MAIL_USERNAME=your-email@outlook.com")
    print("   MAIL_PASSWORD=your-password")
    
    print("\n3. Custom SMTP:")
    print("   EMAIL_PROVIDER=smtp")
    print("   MAIL_SERVER=your-smtp-server.com")
    print("   MAIL_PORT=587")
    print("   MAIL_USE_TLS=true")
    print("   MAIL_USERNAME=your-email@domain.com")
    print("   MAIL_PASSWORD=your-password")
    
    print("\n📝 INSTRUCTIONS:")
    print("=" * 50)
    print("1. Обновите переменные окружения в .env файле")
    print("2. Перезапустите приложение")
    print("3. Протестируйте регистрацию нового пользователя")
    print("4. Проверьте получение email подтверждения")
    
    print("\n✅ После настройки SMTP:")
    print("- Новые пользователи получат email подтверждения")
    print("- Существующие пользователи смогут запросить повторную отправку")
    print("- Все токены будут действительны 24 часа")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    switch_to_smtp()





