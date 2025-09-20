#!/usr/bin/env python3
"""
Скрипт для исправления email client - добавляет недостающие колонки
"""

import os
import sys

def fix_email_client():
    """Исправляет email client добавляя недостающие колонки"""
    
    try:
        # Добавляем путь к проекту
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_root)
        
        # Импортируем Flask приложение
        from app import app
        from extensions import db
        from sqlalchemy import text
        
        print("🔧 Fixing email client database schema...")
        
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
            
            # Проверяем и добавляем колонки если нужно
            try:
                if is_postgresql:
                    # Проверяем source_account
                    result = db.session.execute(text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'incoming_emails' 
                        AND column_name = 'source_account'
                    """))
                    
                    if not result.fetchone():
                        print("📝 Adding source_account column...")
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
                        print("✅ Added source_account column")
                    else:
                        print("✅ source_account column already exists")
                    
                    # Проверяем другие колонки если нужно
                    columns_to_check = [
                        'category', 'tags', 'is_replied', 'reply_sent_at'
                    ]
                    
                    for column in columns_to_check:
                        result = db.session.execute(text(f"""
                            SELECT column_name 
                            FROM information_schema.columns 
                            WHERE table_name = 'incoming_emails' 
                            AND column_name = '{column}'
                        """))
                        
                        if not result.fetchone():
                            print(f"📝 Adding {column} column...")
                            if column == 'category':
                                db.session.execute(text(f"""
                                    ALTER TABLE incoming_emails 
                                    ADD COLUMN {column} VARCHAR(50)
                                """))
                            elif column == 'tags':
                                db.session.execute(text(f"""
                                    ALTER TABLE incoming_emails 
                                    ADD COLUMN {column} TEXT
                                """))
                            elif column == 'is_replied':
                                db.session.execute(text(f"""
                                    ALTER TABLE incoming_emails 
                                    ADD COLUMN {column} BOOLEAN DEFAULT FALSE
                                """))
                            elif column == 'reply_sent_at':
                                db.session.execute(text(f"""
                                    ALTER TABLE incoming_emails 
                                    ADD COLUMN {column} TIMESTAMP
                                """))
                            print(f"✅ Added {column} column")
                        else:
                            print(f"✅ {column} column already exists")
                    
                else:  # SQLite
                    print("📝 SQLite detected - checking columns...")
                    result = db.session.execute(text("PRAGMA table_info(incoming_emails)"))
                    existing_columns = [row[1] for row in result.fetchall()]
                    
                    columns_to_add = {
                        'source_account': 'VARCHAR(50)',
                        'category': 'VARCHAR(50)',
                        'tags': 'TEXT',
                        'is_replied': 'BOOLEAN DEFAULT 0',
                        'reply_sent_at': 'TIMESTAMP'
                    }
                    
                    for column, column_type in columns_to_add.items():
                        if column not in existing_columns:
                            print(f"📝 Adding {column} column...")
                            db.session.execute(text(f"""
                                ALTER TABLE incoming_emails 
                                ADD COLUMN {column} {column_type}
                            """))
                            print(f"✅ Added {column} column")
                        else:
                            print(f"✅ {column} column already exists")
                    
                    # Обновляем существующие записи
                    db.session.execute(text("""
                        UPDATE incoming_emails 
                        SET source_account = 'info' 
                        WHERE source_account IS NULL
                    """))
                
                db.session.commit()
                print("🎉 Successfully fixed email client database schema!")
                
                return True
                
            except Exception as e:
                print(f"❌ Error fixing schema: {str(e)}")
                db.session.rollback()
                return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция"""
    print("🚀 Email Client Database Fixer")
    print("=" * 50)
    
    success = fix_email_client()
    
    if success:
        print("✅ Script completed successfully!")
        sys.exit(0)
    else:
        print("❌ Script failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
