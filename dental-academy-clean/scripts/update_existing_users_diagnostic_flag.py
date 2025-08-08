#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script to update requires_diagnostic flag for existing users
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, User, DiagnosticSession

def update_existing_users():
    """Update requires_diagnostic flag for existing users"""
    
    with app.app_context():
        print("🔧 Обновление флага requires_diagnostic для существующих пользователей...")
        
        # Get all users
        users = User.query.all()
        print(f"📊 Найдено пользователей: {len(users)}")
        
        updated_count = 0
        
        for user in users:
            # Check if user has any completed diagnostic sessions
            has_diagnostic = DiagnosticSession.query.filter_by(
                user_id=user.id,
                status='completed'
            ).first() is not None
            
            # Update the flag
            if has_diagnostic:
                user.requires_diagnostic = False
                print(f"✅ Пользователь {user.id} ({user.email}): имеет диагностику, флаг установлен в False")
            else:
                user.requires_diagnostic = True
                print(f"⚠️ Пользователь {user.id} ({user.email}): нет диагностики, флаг установлен в True")
            
            updated_count += 1
        
        # Commit changes
        db.session.commit()
        
        print(f"✅ Обновлено пользователей: {updated_count}")
        print("🎉 Обновление завершено!")

if __name__ == '__main__':
    update_existing_users() 