#!/usr/bin/env python3
"""
Force Load Production Data Script
Принудительно загружает данные на production
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
from scripts.seed_production_data_runner import main as load_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def force_load_data():
    """Принудительно загрузить данные"""
    logger.info("🚀 Принудительная загрузка данных на production...")
    
    try:
        with app.app_context():
            # Check current state
            questions_before = Question.query.count()
            irt_before = IRTParameters.query.count()
            domains_before = BIGDomain.query.count()
            
            logger.info(f"📊 Состояние до загрузки:")
            logger.info(f"  - Вопросов: {questions_before}")
            logger.info(f"  - IRT параметров: {irt_before}")
            logger.info(f"  - Доменов: {domains_before}")
            
            # Force load data
            logger.info("📥 Загрузка данных...")
            load_data()
            
            # Check after loading
            questions_after = Question.query.count()
            irt_after = IRTParameters.query.count()
            domains_after = BIGDomain.query.count()
            
            logger.info(f"📊 Состояние после загрузки:")
            logger.info(f"  - Вопросов: {questions_after}")
            logger.info(f"  - IRT параметров: {irt_after}")
            logger.info(f"  - Доменов: {domains_after}")
            
            # Test IRT engine
            logger.info("🧪 Тестирование IRT Engine...")
            from utils.irt_engine import IRTEngine
            irt_engine = IRTEngine()
            test_question = irt_engine.select_initial_question()
            
            if test_question:
                logger.info(f"✅ IRT Engine работает - выбран вопрос: {test_question.id}")
                logger.info("✅ Принудительная загрузка данных завершена успешно!")
                return True
            else:
                logger.error("❌ IRT Engine не может выбрать вопрос после загрузки")
                return False
                
    except Exception as e:
        logger.error(f"❌ Ошибка при принудительной загрузке данных: {e}")
        return False

def main():
    """Основная функция"""
    success = force_load_data()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
