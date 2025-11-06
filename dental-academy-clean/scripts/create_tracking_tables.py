#!/usr/bin/env python3
"""
Скрипт для создания таблиц отслеживания посетителей регистрации
"""

import os
import sys
from datetime import datetime

def create_tracking_tables():
    """Создает таблицы для отслеживания посетителей"""
    print("🔧 Creating tracking tables...")
    
    try:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_root)
        
        from app import app
        from extensions import db
        
        with app.app_context():
            try:
                # Проверяем подключение к базе данных
                db.session.execute(db.text("SELECT 1"))
                print("✅ Database connection successful")
            except Exception as e:
                print(f"❌ Database connection failed: {str(e)}")
                return False
            
            try:
                # Создаем все таблицы
                db.create_all()
                print("✅ All tables created successfully")
                
                # Проверяем, что таблицы созданы
                from models import RegistrationVisitor, RegistrationAnalytics
                
                # Проверяем RegistrationVisitor
                result = db.session.execute(db.text("SELECT COUNT(*) FROM registration_visitors")).scalar()
                print(f"✅ RegistrationVisitor table exists (records: {result})")
                
                # Проверяем RegistrationAnalytics
                result = db.session.execute(db.text("SELECT COUNT(*) FROM registration_analytics")).scalar()
                print(f"✅ RegistrationAnalytics table exists (records: {result})")
                
                return True
                
            except Exception as e:
                print(f"❌ Error creating tables: {str(e)}")
                import traceback
                traceback.print_exc()
                return False
                
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция"""
    print("🚀 Create Tracking Tables Script")
    print("=" * 50)
    
    success = create_tracking_tables()
    
    if success:
        print("✅ Script completed successfully!")
        sys.exit(0)
    else:
        print("❌ Script failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()


