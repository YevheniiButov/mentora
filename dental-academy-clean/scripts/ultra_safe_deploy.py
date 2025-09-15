#!/usr/bin/env python3
"""
🔒 СУПЕР-БЕЗОПАСНЫЙ ДЕПЛОЙ СКРИПТ
НЕ удаляет существующих пользователей!
"""
import os
import sys
import logging
from datetime import datetime, timezone
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def ultra_safe_deploy():
    """Ультра-безопасный деплой без потери данных"""
    logger.info("🚀 ULTRA-SAFE DEPLOY STARTING...")
    logger.info("🔒 Гарантия: НИ ОДИН пользователь НЕ будет удален!")
    
    try:
        # Import после настройки path
        from app import create_app
        from extensions import db
        from models import User, LearningPath, Subject, Module, Lesson, Question
        
        app = create_app()
        
        with app.app_context():
            # 1. ПРОВЕРЯЕМ СУЩЕСТВУЮЩИЕ ДАННЫЕ
            logger.info("📊 Checking existing data...")
            
            users_count = User.query.count()
            admins_count = User.query.filter_by(role='admin').count()
            paths_count = LearningPath.query.count()
            
            logger.info(f"   👥 Users: {users_count}")
            logger.info(f"   👑 Admins: {admins_count}")
            logger.info(f"   📚 Learning paths: {paths_count}")
            
            # 2. СОЗДАЕМ BACKUP TIMESTAMP
            timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
            logger.info(f"📅 Deploy timestamp: {timestamp}")
            
            # 3. БЕЗОПАСНО СОЗДАЕМ ТАБЛИЦЫ (НЕ УДАЛЯЕТ ДАННЫЕ!)
            logger.info("🔧 Ensuring database tables exist...")
            try:
                db.create_all()
                logger.info("✅ Database tables checked/created safely")
            except Exception as e:
                logger.error(f"❌ Database creation error: {e}")
                return False
            
            # 4. ПРОВЕРЯЕМ АДМИНА (НЕ ПЕРЕЗАПИСЫВАЕМ!)
            logger.info("👑 Ensuring admin exists...")
            
            # Ищем ЛЮБОГО админа
            existing_admin = User.query.filter_by(role='admin').first()
            
            if existing_admin:
                logger.info(f"✅ Admin already exists: {existing_admin.email}")
                logger.info("🔒 NO admin modification needed!")
            else:
                # Создаем админа ТОЛЬКО если его нет
                logger.info("🆕 Creating new admin (none exists)...")
                
                admin_email = os.environ.get('ADMIN_EMAIL', 'admin@mentora.com')
                admin_password = os.environ.get('ADMIN_PASSWORD', 'AdminPass123!')
                
                try:
                    admin = User(
                        email=admin_email,
                        username=admin_email,
                        first_name="System",
                        last_name="Administrator",
                        role='admin',
                        is_active=True,
                        email_confirmed=True,
                        registration_completed=True,
                        language='en'
                    )
                    admin.set_password(admin_password)
                    
                    db.session.add(admin)
                    db.session.commit()
                    
                    logger.info(f"✅ NEW admin created: {admin_email}")
                    
                except Exception as e:
                    logger.error(f"❌ Admin creation failed: {e}")
                    db.session.rollback()
                    return False
            
            # 5. ДОБАВЛЯЕМ БАЗОВЫЕ ДАННЫЕ (ТОЛЬКО ЕСЛИ ИХ НЕТ!)
            logger.info("📚 Checking learning content...")
            
            if paths_count == 0:
                logger.info("📖 Creating basic learning content...")
                try:
                    from models import create_sample_data
                    result = create_sample_data()
                    logger.info(f"✅ Basic content created: {result}")
                except Exception as e:
                    logger.error(f"⚠️  Content creation warning: {e}")
                    # НЕ failing - контент не критичен
            else:
                logger.info("✅ Learning content already exists")
            
            # 6. ФИНАЛЬНАЯ ПРОВЕРКА
            final_users = User.query.count()
            final_admins = User.query.filter_by(role='admin').count()
            
            logger.info("🎉 ULTRA-SAFE DEPLOY COMPLETED!")
            logger.info(f"📊 FINAL STATS:")
            logger.info(f"   👥 Total users: {final_users}")
            logger.info(f"   👑 Admin users: {final_admins}")
            logger.info(f"   📈 Users preserved: {users_count}")
            logger.info(f"   🔒 Zero data loss: {'YES' if final_users >= users_count else 'WARNING'}")
            
            # 7. SAFETY CHECK
            if final_users < users_count:
                logger.error("🚨 DATA LOSS DETECTED! Rolling back...")
                db.session.rollback()
                return False
            
            return True
            
    except Exception as e:
        logger.error(f"❌ DEPLOY FAILED: {e}")
        logger.error("🔄 Check logs and try again")
        return False

if __name__ == '__main__':
    success = ultra_safe_deploy()
    
    if success:
        logger.info("✅ Deploy successful - ready for production!")
        sys.exit(0)
    else:
        logger.error("❌ Deploy failed - check logs")
        sys.exit(1)
