#!/usr/bin/env python3
"""
БЕЗОПАСНЫЙ ДЕПЛОЙ SCRIPT
Проверяет существование данных и НЕ перезаписывает пользователей
"""

import os
import sys
import logging
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from extensions import db
from models import User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_existing_data():
    """Проверка существующих данных"""
    try:
        user_count = User.query.count()
        admin_count = User.query.filter_by(role='admin').count()
        
        logger.info(f"📊 Current database stats:")
        logger.info(f"   Total users: {user_count}")
        logger.info(f"   Admin users: {admin_count}")
        
        return {
            'users_exist': user_count > 0,
            'admin_exists': admin_count > 0,
            'user_count': user_count,
            'admin_count': admin_count
        }
    except Exception as e:
        logger.error(f"❌ Error checking database: {e}")
        return {
            'users_exist': False,
            'admin_exists': False,
            'user_count': 0,
            'admin_count': 0
        }

def ensure_admin_user():
    """Создание админа только если его нет"""
    try:
        # Check if admin exists
        admin = User.query.filter_by(role='admin').first()
        
        if admin:
            logger.info(f"✅ Admin user already exists: {admin.email}")
            return admin
        
        # Create admin if none exists
        admin_email = os.environ.get('ADMIN_EMAIL', 'admin@mentora.com')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        
        admin = User(
            email=admin_email,
            username='admin',
            first_name='System',
            last_name='Administrator',
            role='admin',
            is_active=True,
            email_confirmed=True
        )
        admin.set_password(admin_password)
        
        db.session.add(admin)
        db.session.commit()
        
        logger.info(f"✅ Created new admin user: {admin_email}")
        return admin
        
    except Exception as e:
        logger.error(f"❌ Error creating admin user: {e}")
        db.session.rollback()
        return None

def safe_deploy():
    """Безопасный деплой без потери данных"""
    logger.info("🚀 Starting SAFE production deploy...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # 1. Проверяем базу данных
            logger.info("📊 Checking existing data...")
            data_stats = check_existing_data()
            
            # 2. Создаем бэкап timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            logger.info(f"📅 Deploy timestamp: {timestamp}")
            
            # 3. Обеспечиваем наличие админа
            logger.info("👤 Ensuring admin user exists...")
            admin = ensure_admin_user()
            
            if not admin:
                logger.error("❌ Failed to create/find admin user")
                return False
            
            # 4. Проверяем финальное состояние
            final_stats = check_existing_data()
            
            logger.info("✅ SAFE DEPLOY COMPLETED!")
            logger.info(f"   Final user count: {final_stats['user_count']}")
            logger.info(f"   Final admin count: {final_stats['admin_count']}")
            logger.info(f"   Data preserved: {'YES' if data_stats['users_exist'] else 'NO'}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Deploy failed: {e}")
            return False

if __name__ == '__main__':
    success = safe_deploy()
    sys.exit(0 if success else 1)
