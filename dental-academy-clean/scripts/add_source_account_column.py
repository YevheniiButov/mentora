#!/usr/bin/env python3
"""
Скрипт для добавления колонки source_account в таблицу incoming_emails
"""

import os
import sys

def add_source_account_column():
    """Добавляет колонку source_account в таблицу incoming_emails"""
    
    try:
        # Добавляем путь к проекту
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_root)
        
        # Импортируем Flask приложение
        from app import app
        from extensions import db
        from sqlalchemy import text
        
        print("🔧 Adding source_account column to incoming_emails table...")
        
        with app.app_context():
            # Проверяем подключение к БД
            try:
                db.session.execute(text("SELECT 1"))
                print("✅ Database connection successful")
            except Exception as e:
                print(f"❌ Database connection failed: {str(e)}")
                return False
            
            # Проверяем существует ли колонка
            try:
                result = db.session.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'incoming_emails' 
                    AND column_name = 'source_account'
                """))
                
                if result.fetchone():
                    print("✅ Column source_account already exists")
                    return True
                else:
                    print("📝 Column source_account does not exist, adding it...")
                    
            except Exception as e:
                print(f"❌ Error checking column: {str(e)}")
                return False
            
            # Добавляем колонку
            try:
                db.session.execute(text("""
                    ALTER TABLE incoming_emails 
                    ADD COLUMN source_account VARCHAR(50) NOT NULL DEFAULT 'info'
                """))
                
                db.session.commit()
                print("✅ Successfully added source_account column")
                
                # Обновляем существующие записи
                db.session.execute(text("""
                    UPDATE incoming_emails 
                    SET source_account = 'info' 
                    WHERE source_account IS NULL OR source_account = ''
                """))
                
                db.session.commit()
                print("✅ Updated existing records with default source_account value")
                
                return True
                
            except Exception as e:
                print(f"❌ Error adding column: {str(e)}")
                db.session.rollback()
                return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция"""
    print("🚀 Source Account Column Adder")
    print("=" * 50)
    
    success = add_source_account_column()
    
    if success:
        print("✅ Script completed successfully!")
        sys.exit(0)
    else:
        print("❌ Script failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
