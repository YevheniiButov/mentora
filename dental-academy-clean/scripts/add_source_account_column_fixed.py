#!/usr/bin/env python3
"""
Скрипт для добавления колонки source_account в таблицу incoming_emails (исправленный)
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
            
            # Определяем тип базы данных
            db_url = str(db.engine.url)
            is_postgresql = 'postgresql' in db_url
            is_sqlite = 'sqlite' in db_url
            
            print(f"📊 Database type: {'PostgreSQL' if is_postgresql else 'SQLite' if is_sqlite else 'Unknown'}")
            
            # Проверяем существует ли колонка
            try:
                if is_postgresql:
                    result = db.session.execute(text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'incoming_emails' 
                        AND column_name = 'source_account'
                    """))
                else:  # SQLite
                    result = db.session.execute(text("PRAGMA table_info(incoming_emails)"))
                    columns = [row[1] for row in result.fetchall()]
                    if 'source_account' in columns:
                        print("✅ Column source_account already exists")
                        return True
                    else:
                        print("📝 Column source_account does not exist, adding it...")
                        
                if is_postgresql and result.fetchone():
                    print("✅ Column source_account already exists")
                    return True
                elif is_postgresql:
                    print("📝 Column source_account does not exist, adding it...")
                    
            except Exception as e:
                print(f"❌ Error checking column: {str(e)}")
                return False
            
            # Добавляем колонку
            try:
                if is_postgresql:
                    db.session.execute(text("""
                        ALTER TABLE incoming_emails 
                        ADD COLUMN source_account VARCHAR(50) NOT NULL DEFAULT 'info'
                    """))
                    
                    # Обновляем существующие записи
                    db.session.execute(text("""
                        UPDATE incoming_emails 
                        SET source_account = 'info' 
                        WHERE source_account IS NULL OR source_account = ''
                    """))
                    
                else:  # SQLite
                    # SQLite не поддерживает ALTER COLUMN с DEFAULT, поэтому добавляем без DEFAULT
                    db.session.execute(text("""
                        ALTER TABLE incoming_emails 
                        ADD COLUMN source_account VARCHAR(50)
                    """))
                    
                    # Обновляем существующие записи
                    db.session.execute(text("""
                        UPDATE incoming_emails 
                        SET source_account = 'info' 
                        WHERE source_account IS NULL
                    """))
                
                db.session.commit()
                print("✅ Successfully added source_account column")
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
    print("🚀 Source Account Column Adder (Fixed)")
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
