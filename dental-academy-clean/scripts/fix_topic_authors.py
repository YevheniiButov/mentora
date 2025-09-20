#!/usr/bin/env python3
"""
Скрипт для исправления авторов тем
"""

import os
import sys

def fix_topic_authors():
    """Исправляет авторов тем"""
    
    try:
        # Добавляем путь к проекту
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_root)
        
        # Импортируем Flask приложение
        from app import app
        from extensions import db
        from models import ForumCategory, ForumTopic, User
        
        print("🔍 Fixing topic authors...")
        
        with app.app_context():
            # Проверяем подключение к БД
            try:
                db.session.execute(db.text("SELECT 1"))
                print("✅ Database connection successful")
            except Exception as e:
                print(f"❌ Database connection failed: {str(e)}")
                return False
            
            # Находим или создаем украинских пользователей
            ukrainian_users = [
                {'first_name': 'Олександр', 'last_name': 'Петренко', 'email': 'oleksandr.petrenko@example.com'},
                {'first_name': 'Марія', 'last_name': 'Коваленко', 'email': 'maria.kovalenko@example.com'},
                {'first_name': 'Андрій', 'last_name': 'Шевченко', 'email': 'andrii.shevchenko@example.com'},
                {'first_name': 'Олена', 'last_name': 'Бондаренко', 'email': 'olena.bondarenko@example.com'},
                {'first_name': 'Дмитро', 'last_name': 'Мельник', 'email': 'dmytro.melnyk@example.com'},
                {'first_name': 'Наталія', 'last_name': 'Ткаченко', 'email': 'natalia.tkachenko@example.com'},
                {'first_name': 'Сергій', 'last_name': 'Морозенко', 'email': 'serhii.morozhenko@example.com'},
                {'first_name': 'Ірина', 'last_name': 'Левченко', 'email': 'irina.levchenko@example.com'}
            ]
            
            created_users = []
            
            for user_data in ukrainian_users:
                # Проверяем существует ли пользователь
                existing_user = User.query.filter_by(email=user_data['email']).first()
                
                if not existing_user:
                    print(f"👤 Creating Ukrainian user: {user_data['first_name']} {user_data['last_name']}")
                    new_user = User(
                        email=user_data['email'],
                        first_name=user_data['first_name'],
                        last_name=user_data['last_name'],
                        role='user',
                        is_active=True
                    )
                    db.session.add(new_user)
                    db.session.commit()
                    created_users.append(new_user)
                    print(f"✅ Created user: {new_user.first_name} {new_user.last_name}")
                else:
                    created_users.append(existing_user)
                    print(f"⏭️ User already exists: {existing_user.first_name} {existing_user.last_name}")
            
            # Находим тему с вашим именем
            your_topic = ForumTopic.query.filter_by(title='bi exam').first()
            
            if your_topic:
                print(f"\n🔧 Found topic with your name: '{your_topic.title}'")
                print(f"Current author: {your_topic.author.first_name} {your_topic.author.last_name}")
                
                # Меняем автора на первого украинского пользователя
                if created_users:
                    new_author = created_users[0]
                    old_author = your_topic.author
                    
                    your_topic.author_id = new_author.id
                    db.session.commit()
                    
                    print(f"✅ Changed author from '{old_author.first_name} {old_author.last_name}' to '{new_author.first_name} {new_author.last_name}'")
                else:
                    print("❌ No Ukrainian users available")
            else:
                print("❌ Topic 'bi exam' not found")
            
            # Перераспределяем остальные темы между украинскими пользователями
            print(f"\n🔄 Redistributing other topics...")
            
            all_topics = ForumTopic.query.all()
            ukrainian_user_index = 0
            
            for topic in all_topics:
                if topic.title != 'bi exam':  # Пропускаем уже исправленную тему
                    # Меняем автора на следующего украинского пользователя
                    new_author = created_users[ukrainian_user_index % len(created_users)]
                    old_author = topic.author
                    
                    topic.author_id = new_author.id
                    db.session.commit()
                    
                    print(f"✅ '{topic.title}' -> {new_author.first_name} {new_author.last_name}")
                    
                    ukrainian_user_index += 1
            
            print(f"\n🎉 Successfully fixed all topic authors!")
            return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция"""
    print("🚀 Topic Authors Fixer")
    print("=" * 50)
    
    success = fix_topic_authors()
    
    if success:
        print("✅ Script completed successfully!")
        sys.exit(0)
    else:
        print("❌ Script failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()
