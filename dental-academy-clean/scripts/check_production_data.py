#!/usr/bin/env python3
"""
Production Data Check and Load Script
Проверяет и загружает данные на production если они отсутствуют
"""

import sys
import os
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import app, db
from models import Question, IRTParameters, BIGDomain, User
from utils.irt_engine import IRTEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database_status():
    """Проверить статус базы данных"""
    logger.info("🔍 Проверка статуса базы данных...")
    
    try:
        with app.app_context():
            # Check questions
            questions_count = Question.query.count()
            logger.info(f"📊 Вопросов в базе: {questions_count}")
            
            # Check IRT parameters
            irt_count = IRTParameters.query.count()
            logger.info(f"📊 IRT параметров: {irt_count}")
            
            # Check domains
            domains_count = BIGDomain.query.count()
            logger.info(f"📊 Доменов: {domains_count}")
            
            # Check users
            users_count = User.query.count()
            logger.info(f"📊 Пользователей: {users_count}")
            
            # Test IRT engine
            logger.info("🧪 Тестирование IRT Engine...")
            irt_engine = IRTEngine()
            test_question = irt_engine.select_initial_question()
            
            if test_question:
                logger.info(f"✅ IRT Engine работает - выбран вопрос: {test_question.id}")
                return True
            else:
                logger.error("❌ IRT Engine не может выбрать вопрос")
                return False
                
    except Exception as e:
        logger.error(f"❌ Ошибка при проверке базы данных: {e}")
        return False

def load_missing_data():
    """Загрузить недостающие данные"""
    logger.info("📥 Загрузка недостающих данных...")
    
    try:
        # Import the production data loader
        from scripts.seed_production_data_runner import main as load_data
        
        # Run the data loader
        load_data()
        logger.info("✅ Данные загружены успешно")
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка при загрузке данных: {e}")
        return False

def create_test_user():
    """Создать тестового пользователя если нет пользователей"""
    logger.info("👤 Проверка тестового пользователя...")
    
    try:
        with app.app_context():
            # Check if we have any users
            user_count = User.query.count()
            logger.info(f"Пользователей в базе: {user_count}")
            
            if user_count == 0:
                logger.info("Создание тестового пользователя...")
                
                # Create test user
                test_user = User(
                    username='test.user',
                    email='test@mentora.nl',
                    is_active=True
                )
                test_user.set_password('test123')
                db.session.add(test_user)
                db.session.commit()
                
                logger.info("✅ Тестовый пользователь создан")
                return True
            else:
                logger.info("✅ Пользователи уже есть в базе")
                return True
                
    except Exception as e:
        logger.error(f"❌ Ошибка при создании тестового пользователя: {e}")
        return False

def main():
    """Основная функция"""
    logger.info("🚀 Запуск проверки production данных...")
    
    # Check current status
    status_ok = check_database_status()
    
    if not status_ok:
        logger.warning("⚠️ Проблемы с данными обнаружены")
        
        # Try to load missing data
        logger.info("🔄 Попытка загрузки недостающих данных...")
        if load_missing_data():
            # Check again after loading
            logger.info("🔄 Повторная проверка после загрузки...")
            status_ok = check_database_status()
        else:
            logger.error("❌ Не удалось загрузить данные")
            return False
    
    # Ensure we have a test user
    create_test_user()
    
    if status_ok:
        logger.info("✅ Все проверки пройдены успешно!")
        return True
    else:
        logger.error("❌ Проблемы с данными остались")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
