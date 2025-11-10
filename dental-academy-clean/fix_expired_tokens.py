#!/usr/bin/env python3
"""
Скрипт для исправления истекших токенов email подтверждения
"""

import os
import sys
from datetime import datetime, timezone, timedelta
from app import app
from models import User, db
from utils.email_service import send_email_confirmation

def fix_expired_tokens():
    """Исправляет истекшие токены email подтверждения"""
    
    with app.app_context():
        print("🔧 FIXING EXPIRED EMAIL CONFIRMATION TOKENS")
        print("=" * 60)
        
        # Находим пользователей с неподтвержденными email
        unconfirmed_users = User.query.filter_by(email_confirmed=False).all()
        print(f"📧 Found {len(unconfirmed_users)} users with unconfirmed email")
        
        expired_count = 0
        fixed_count = 0
        
        for user in unconfirmed_users:
            print(f"\n👤 Processing user: {user.email}")
            
            # Проверяем, истек ли токен
            if user.email_confirmation_sent_at:
                sent_at = user.email_confirmation_sent_at
                if sent_at.tzinfo is None:
                    sent_at = sent_at.replace(tzinfo=timezone.utc)
                
                expiry_seconds = app.config.get('EMAIL_CONFIRMATION_EXPIRES', 86400)
                expiry_time = sent_at + timedelta(seconds=expiry_seconds)
                current_time = datetime.now(timezone.utc)
                
                if current_time > expiry_time:
                    print(f"   ❌ Token expired (sent: {sent_at}, expired: {expiry_time})")
                    expired_count += 1
                    
                    # Генерируем новый токен
                    try:
                        new_token = user.generate_email_confirmation_token()
                        db.session.commit()
                        
                        # Отправляем новый email
                        email_sent = send_email_confirmation(user, new_token)
                        
                        if email_sent:
                            print(f"   ✅ New confirmation email sent")
                            fixed_count += 1
                        else:
                            print(f"   ❌ Failed to send new confirmation email")
                            
                    except Exception as e:
                        print(f"   ❌ Error fixing token: {e}")
                        db.session.rollback()
                else:
                    print(f"   ✅ Token still valid (expires: {expiry_time})")
            else:
                print(f"   ⚠️  No confirmation token found")
                
                # Генерируем новый токен для пользователей без токена
                try:
                    new_token = user.generate_email_confirmation_token()
                    db.session.commit()
                    
                    # Отправляем новый email
                    email_sent = send_email_confirmation(user, new_token)
                    
                    if email_sent:
                        print(f"   ✅ New confirmation email sent")
                        fixed_count += 1
                    else:
                        print(f"   ❌ Failed to send new confirmation email")
                        
                except Exception as e:
                    print(f"   ❌ Error generating token: {e}")
                    db.session.rollback()
        
        print(f"\n📊 SUMMARY:")
        print(f"   Total users with unconfirmed email: {len(unconfirmed_users)}")
        print(f"   Expired tokens found: {expired_count}")
        print(f"   Tokens fixed: {fixed_count}")
        
        if fixed_count > 0:
            print(f"\n✅ SUCCESS: {fixed_count} users received new confirmation emails")
        else:
            print(f"\n⚠️  No tokens needed fixing")
        
        print("=" * 60)

if __name__ == "__main__":
    fix_expired_tokens()







