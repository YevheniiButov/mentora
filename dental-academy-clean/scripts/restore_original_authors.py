#!/usr/bin/env python3
"""
Скрипт для восстановления оригинальных авторов тем
"""

import os
import sys

def restore_original_authors():
    """Восстанавливает оригинальных авторов тем"""
    
    try:
        # Добавляем путь к проекту
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_root)
        
        # Импортируем Flask приложение
        from app import app
        from extensions import db
        from models import ForumCategory, ForumTopic, User
        
        print("🔍 Restoring original topic authors...")
        
        with app.app_context():
            # Проверяем подключение к БД
            try:
                db.session.execute(db.text("SELECT 1"))
                print("✅ Database connection successful")
            except Exception as e:
                print(f"❌ Database connection failed: {str(e)}")
                return False
            
            # Находим оригинального админа
            admin_user = User.query.filter_by(email='admin@mentora.com').first()
            if not admin_user:
                print("❌ Admin user not found!")
                return False
            
            print(f"✅ Found admin user: {admin_user.first_name} {admin_user.last_name}")
            
            # Находим ваш аккаунт
            your_user = User.query.filter_by(email='test@mentora.com.in').first()
            if not your_user:
                print("❌ Your user account not found!")
                return False
            
            print(f"✅ Found your user: {your_user.first_name} {your_user.last_name}")
            
            # Восстанавливаем авторов тем
            print(f"\n🔄 Restoring topic authors...")
            
            all_topics = ForumTopic.query.all()
            
            for topic in all_topics:
                # Тема "bi exam" должна быть от вашего имени
                if topic.title == 'bi exam':
                    topic.author_id = your_user.id
                    print(f"✅ '{topic.title}' -> {your_user.first_name} {your_user.last_name}")
                else:
                    # Все остальные темы от админа
                    topic.author_id = admin_user.id
                    print(f"✅ '{topic.title}' -> {admin_user.first_name} {admin_user.last_name}")
            
            db.session.commit()
            print(f"\n🎉 Successfully restored original authors!")
            
            # Удаляем созданных украинских пользователей
            print(f"\n🗑️ Removing Ukrainian users...")
            
            ukrainian_emails = [
                'oleksandr.petrenko@example.com',
                'maria.kovalenko@example.com',
                'andrii.shevchenko@example.com',
                'olena.bondarenko@example.com',
                'dmytro.melnyk@example.com',
                'natalia.tkachenko@example.com',
                'serhii.morozhenko@example.com',
                'irina.levchenko@example.com'
            ]
            
            for email in ukrainian_emails:
                user = User.query.filter_by(email=email).first()
                if user:
                    print(f"🗑️ Removing user: {user.first_name} {user.last_name} ({email})")
                    db.session.delete(user)
            
            db.session.commit()
            print(f"✅ Removed all Ukrainian users!")
            
            return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция"""
    print("🚀 Original Authors Restorer")
    print("=" * 50)
    
    success = restore_original_authors()
    
    if success:
        print("✅ Script completed successfully!")
        sys.exit(0)
    else:
        print("❌ Script failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
