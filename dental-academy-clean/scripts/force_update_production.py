#!/usr/bin/env python3
"""
🚨 CRITICAL PRODUCTION UPDATE SCRIPT
Принудительное обновление production для исправления ошибки создания вопросов
"""

import os
import sys
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Главная функция для принудительного обновления"""
    logger.info("🚨 CRITICAL UPDATE: Принудительное обновление production")
    logger.info(f"⏰ Время обновления: {datetime.now()}")
    logger.info("✅ Production должен обновиться после этого коммита")
    
    # Проверяем, что мы в production
    if os.environ.get('RENDER'):
        logger.info("🌐 Обнаружена среда Render - production")
    else:
        logger.info("💻 Локальная среда разработки")
    
    logger.info("🎯 Цель: Исправить ошибку 'dict' object has no attribute '_sa_instance_state'")
    logger.info("🔧 Решение: Удаление поля 'id' из question_data перед созданием Question объекта")

if __name__ == "__main__":
    main()
