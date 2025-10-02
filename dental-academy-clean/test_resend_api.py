#!/usr/bin/env python3
"""
Test Resend API Integration
Тестирует отправку email через Resend API
"""

import os
import requests
import json

def test_resend_api():
    """Тестирует Resend API"""
    print("🧪 TESTING RESEND API")
    print("=" * 50)
    
    # Получаем переменные окружения
    api_key = os.environ.get('RESEND_API_KEY')
    from_email = os.environ.get('RESEND_FROM_EMAIL', 'Mentora <noreply@bigmentor.nl>')
    test_email = os.environ.get('TEST_EMAIL', 'test@example.com')
    
    print(f"API Key: {'*' * len(api_key) if api_key else 'NOT SET'}")
    print(f"From Email: {from_email}")
    print(f"Test Email: {test_email}")
    
    if not api_key:
        print("❌ RESEND_API_KEY not set")
        return False
    
    # Подготавливаем тестовое сообщение
    email_data = {
        "from": from_email,
        "to": [test_email],
        "subject": "Mentora - Test Email",
        "html": """
        <h1>Test Email from Mentora</h1>
        <p>This is a test email to verify Resend API integration.</p>
        <p>If you receive this email, the integration is working correctly!</p>
        """,
        "text": "Test Email from Mentora\n\nThis is a test email to verify Resend API integration.\n\nIf you receive this email, the integration is working correctly!"
    }
    
    # Отправляем через Resend API
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print("\n📧 Sending test email...")
    
    try:
        response = requests.post(
            "https://api.resend.com/emails",
            headers=headers,
            json=email_data,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Email sent successfully!")
            print(f"📧 Email ID: {result.get('id')}")
            return True
        else:
            print(f"❌ Email sending failed")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return False

def test_resend_domains():
    """Тестирует получение доменов Resend"""
    print("\n🌐 TESTING RESEND DOMAINS")
    print("=" * 50)
    
    api_key = os.environ.get('RESEND_API_KEY')
    
    if not api_key:
        print("❌ RESEND_API_KEY not set")
        return False
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            "https://api.resend.com/domains",
            headers=headers,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            domains = response.json()
            print(f"✅ Domains retrieved successfully!")
            print(f"📋 Domains: {json.dumps(domains, indent=2)}")
            return True
        else:
            print(f"❌ Failed to retrieve domains")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception occurred: {e}")
        return False

def main():
    """Основная функция тестирования"""
    print("🚀 RESEND API TESTING TOOL")
    print("=" * 50)
    
    # Тестируем получение доменов
    domains_ok = test_resend_domains()
    
    # Тестируем отправку email
    email_ok = test_resend_api()
    
    print("\n" + "=" * 50)
    if domains_ok and email_ok:
        print("🎉 ALL TESTS PASSED!")
        print("Resend API integration is working correctly.")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Check the configuration and try again.")

if __name__ == "__main__":
    main()








