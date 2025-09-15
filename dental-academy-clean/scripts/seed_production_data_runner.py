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
from models import db, create_sample_data, User, LearningPath

def seed_production_data():
    """Загружает данные для production"""
    
    with app.app_context():
        try:
            print("🌱 Начинаем загрузку данных для production...")
            
            # Проверяем, есть ли уже данные
            existing_paths = db.session.query(LearningPath).count()
            existing_users = db.session.query(User).count()
            
            print(f"📊 Текущее состояние БД:")
            print(f"   - Пользователей: {existing_users}")
            print(f"   - Учебных путей: {existing_paths}")
            
            # Создаем таблицы если их нет (БЕЗОПАСНО - не удаляет данные)
            db.create_all()
            print("✅ Таблицы базы данных проверены/созданы")
            
            # Загружаем базовые данные только если их нет
            if existing_paths == 0:
                print("📚 Загружаем базовые учебные материалы...")
                create_sample_data()
                print("✅ Базовые данные загружены")
            else:
                print("✅ Базовые данные уже существуют, пропускаем загрузку")
            
            print("✅ Загрузка данных завершена успешно!")
            print("🔒 ВАЖНО: Существующие пользователи НЕ затронуты!")
            
        except Exception as e:
            print(f"❌ Ошибка загрузки данных: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    seed_production_data()
