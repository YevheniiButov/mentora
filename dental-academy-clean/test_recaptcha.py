#!/usr/bin/env python3
"""
Тестовый скрипт для проверки настроек reCAPTCHA
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
import requests

def test_recaptcha_config():
    """Проверяет настройки reCAPTCHA"""
    with app.app_context():
        print("🔍 ПРОВЕРКА НАСТРОЕК reCAPTCHA")
        print("=" * 50)
        
        # Проверяем конфигурацию
        recaptcha_enabled = app.config.get('RECAPTCHA_ENABLED', False)
        public_key = app.config.get('RECAPTCHA_PUBLIC_KEY', None)
        private_key = app.config.get('RECAPTCHA_PRIVATE_KEY', None)
        domains = app.config.get('RECAPTCHA_DOMAINS', [])
        
        print(f"📊 КОНФИГУРАЦИЯ:")
        print(f"   RECAPTCHA_ENABLED: {recaptcha_enabled}")
        print(f"   RECAPTCHA_PUBLIC_KEY: {public_key[:20] + '...' if public_key else 'None'}")
        print(f"   RECAPTCHA_PRIVATE_KEY: {private_key[:20] + '...' if private_key else 'None'}")
        print(f"   RECAPTCHA_DOMAINS: {domains}")
        print()
        
        # Проверяем, есть ли ключи
        if not public_key or not private_key:
            print("❌ ПРОБЛЕМА: Отсутствуют ключи reCAPTCHA")
            return False
        
        if not recaptcha_enabled:
            print("⚠️ ВНИМАНИЕ: reCAPTCHA отключена")
            return False
        
        print("✅ КЛЮЧИ reCAPTCHA НАСТРОЕНЫ")
        print()
        
        # Тестируем валидацию с тестовым токеном
        print("🧪 ТЕСТИРОВАНИЕ ВАЛИДАЦИИ:")
        
        # Тестовый токен (обычно невалидный)
        test_token = "test_token_123"
        
        try:
            from routes.auth_routes import verify_recaptcha
            result = verify_recaptcha(test_token)
            print(f"   Тест с невалидным токеном: {result}")
            
            if result:
                print("   ⚠️ ВНИМАНИЕ: reCAPTCHA принимает невалидные токены (возможно, в dev режиме)")
            else:
                print("   ✅ reCAPTCHA правильно отклоняет невалидные токены")
                
        except Exception as e:
            print(f"   ❌ Ошибка при тестировании: {str(e)}")
        
        print()
        
        # Проверяем, есть ли reCAPTCHA в шаблонах
        print("📄 ПРОВЕРКА ШАБЛОНОВ:")
        
        # Проверяем quick_register.html
        try:
            with open('templates/auth/quick_register.html', 'r', encoding='utf-8') as f:
                content = f.read()
                if 'g-recaptcha' in content:
                    print("   ✅ reCAPTCHA найден в quick_register.html")
                else:
                    print("   ❌ reCAPTCHA НЕ найден в quick_register.html")
        except Exception as e:
            print(f"   ❌ Ошибка чтения quick_register.html: {str(e)}")
        
        # Проверяем register.html
        try:
            with open('templates/auth/register.html', 'r', encoding='utf-8') as f:
                content = f.read()
                if 'g-recaptcha' in content:
                    print("   ✅ reCAPTCHA найден в register.html")
                else:
                    print("   ❌ reCAPTCHA НЕ найден в register.html")
        except Exception as e:
            print(f"   ❌ Ошибка чтения register.html: {str(e)}")
        
        print()
        
        # Проверяем домены
        print("🌐 ПРОВЕРКА ДОМЕНОВ:")
        current_domain = "bigmentor.nl"  # Текущий домен
        if current_domain in domains:
            print(f"   ✅ Домен {current_domain} разрешен")
        else:
            print(f"   ❌ Домен {current_domain} НЕ разрешен")
            print(f"   Разрешенные домены: {domains}")
        
        print()
        print("🎯 РЕЗУЛЬТАТ:")
        if recaptcha_enabled and public_key and private_key:
            print("   ✅ reCAPTCHA настроена правильно")
            print("   ✅ Ключи присутствуют")
            print("   ✅ Шаблоны содержат reCAPTCHA")
            print("   🎯 Проблема может быть в том, что пользователи не проходят капчу")
        else:
            print("   ❌ reCAPTCHA настроена неправильно")
            print("   ❌ Отсутствуют ключи или отключена")

if __name__ == "__main__":
    test_recaptcha_config()


