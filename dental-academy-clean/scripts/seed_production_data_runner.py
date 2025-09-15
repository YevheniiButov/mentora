#!/usr/bin/env python3
"""
Скрипт для загрузки данных в production
"""
import os
import sys
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import app
from models import db, create_sample_data

def seed_production_data():
    """Загружает данные для production"""
    
    with app.app_context():
        try:
            print("🌱 Начинаем загрузку данных для production...")
            
            # Создаем таблицы если их нет
            db.create_all()
            print("✅ Таблицы базы данных созданы")
            
            # Загружаем базовые данные
            create_sample_data()
            print("✅ Базовые данные загружены")
            
            print("✅ Загрузка данных завершена успешно!")
            
        except Exception as e:
            print(f"❌ Ошибка загрузки данных: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    seed_production_data()
