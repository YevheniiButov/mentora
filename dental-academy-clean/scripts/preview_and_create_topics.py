#!/usr/bin/env python3
"""
Скрипт для предпросмотра и создания тем с вашими переписками
"""

import os
import sys

def preview_topics():
    """Показывает предпросмотр тем которые будут созданы"""
    
    print("📋 PREVIEW: Topics that will be created:")
    print("=" * 60)
    
    # Ваши темы с переписками (замените на свои)
    topics_preview = [
        {
            'title': 'BIG Exam Preparation - Share Your Experience 📚',
            'author': 'Admin User',
            'content': 'Let\'s discuss BIG exam preparation strategies, study materials, and share experiences.',
            'messages': [
                {'author': 'Maria', 'content': 'Hi everyone! I\'m preparing for the BIG exam. Any tips for the medical terminology section?'},
                {'author': 'Ahmed', 'content': 'I found the official study guide very helpful. Also, practice with Dutch medical terms daily.'},
                {'author': 'Priya', 'content': 'Don\'t forget about the practical scenarios. They can be tricky!'},
                {'author': 'Carlos', 'content': 'I took the exam last month. The questions were fair but time management is crucial.'},
                {'author': 'Anna', 'content': 'Good luck everyone! You\'ve got this! 💪'}
            ]
        },
        {
            'title': 'Living in the Netherlands - Tips & Experiences 🇳🇱',
            'author': 'Admin User', 
            'content': 'Share your experiences about living and working in the Netherlands as a healthcare professional.',
            'messages': [
                {'author': 'Emma', 'content': 'Just moved to Amsterdam! Any recommendations for finding a good GP?'},
                {'author': 'Lucas', 'content': 'Welcome! I recommend checking the BIG register for qualified doctors in your area.'},
                {'author': 'Alex', 'content': 'The healthcare system here is quite different from what I\'m used to. Any advice?'},
                {'author': 'David', 'content': 'Make sure you understand the insurance system. It\'s mandatory here.'}
            ]
        },
        {
            'title': 'Language Learning - Dutch & English 🗣️',
            'author': 'Admin User',
            'content': 'Discuss language learning resources, tips, and experiences for healthcare professionals.',
            'messages': [
                {'author': 'Sofia', 'content': 'What\'s the best way to learn medical Dutch? Any specific courses?'},
                {'author': 'Tom', 'content': 'I\'m taking a medical Dutch course at the local university. Very comprehensive!'},
                {'author': 'Lisa', 'content': 'Duolingo is good for basics, but you need specialized medical vocabulary.'},
                {'author': 'Mark', 'content': 'Practice with Dutch colleagues. They\'re usually very helpful!'}
            ]
        }
    ]
    
    for i, topic in enumerate(topics_preview, 1):
        print(f"\n{i}. 📝 {topic['title']}")
        print(f"   👤 Author: {topic['author']}")
        print(f"   📄 Content: {topic['content']}")
        print(f"   💬 Messages ({len(topic['messages'])}):")
        
        for j, message in enumerate(topic['messages'], 1):
            print(f"      {j}. {message['author']}: {message['content']}")
    
    print(f"\n📊 SUMMARY:")
    print(f"   • {len(topics_preview)} topics will be created")
    print(f"   • {sum(len(topic['messages']) for topic in topics_preview)} messages will be added")
    print(f"   • All topics will be created by 'Admin User'")
    
    return topics_preview

def create_topics_with_preview(topics_data):
    """Создает темы на основе предпросмотра"""
    
    try:
        # Добавляем путь к проекту
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_root)
        
        # Импортируем Flask приложение
        from app import app
        from extensions import db
        from models import ForumCategory, ForumTopic, ForumPost, User
        from datetime import datetime, timedelta
        import random
        
        print("\n🔧 Creating topics...")
        
        with app.app_context():
            # Проверяем подключение к БД
            try:
                db.session.execute(db.text("SELECT 1"))
                print("✅ Database connection successful")
            except Exception as e:
                print(f"❌ Database connection failed: {str(e)}")
                return False
            
            # Находим категорию
            category = ForumCategory.query.filter_by(slug='general').first()
            if not category:
                print("❌ General category not found")
                return False
            
            # Находим админа
            admin_user = User.query.filter_by(email='admin@mentora.com').first()
            if not admin_user:
                print("❌ Admin user not found")
                return False
            
            # Находим пользователей для сообщений
            users = User.query.filter_by(is_active=True).limit(10).all()
            if len(users) < 3:
                print("❌ Not enough users for messages")
                return False
            
            created_topics = 0
            created_messages = 0
            
            for topic_data in topics_data:
                # Создаем тему
                topic = ForumTopic(
                    title=topic_data['title'],
                    content=topic_data['content'],
                    category_id=category.id,
                    author_id=admin_user.id,
                    status='active',
                    is_sticky=False,
                    is_locked=False,
                    views_count=random.randint(50, 200),
                    replies_count=len(topic_data['messages']),
                    likes_count=random.randint(5, 25),
                    created_at=datetime.now() - timedelta(days=random.randint(1, 30))
                )
                
                db.session.add(topic)
                db.session.commit()
                
                # Создаем сообщения
                base_time = topic.created_at
                for i, message_data in enumerate(topic_data['messages']):
                    # Находим пользователя по имени
                    author_user = None
                    for user in users:
                        if user.first_name == message_data['author']:
                            author_user = user
                            break
                    
                    if not author_user:
                        author_user = random.choice(users)
                    
                    message_time = base_time + timedelta(hours=i*2, minutes=random.randint(0, 59))
                    
                    post = ForumPost(
                        topic_id=topic.id,
                        author_id=author_user.id,
                        content=message_data['content'],
                        created_at=message_time,
                        updated_at=message_time
                    )
                    
                    db.session.add(post)
                    created_messages += 1
                
                created_topics += 1
                print(f"✅ Created topic: {topic_data['title']}")
            
            db.session.commit()
            print(f"\n🎉 Successfully created {created_topics} topics with {created_messages} messages!")
            return True
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция"""
    print("🚀 Preview and Create Topics")
    print("=" * 50)
    
    # Показываем предпросмотр
    topics_data = preview_topics()
    
    # Спрашиваем подтверждение
    print(f"\n❓ Do you want to create these topics? (y/n): ", end="")
    response = input().lower().strip()
    
    if response in ['y', 'yes', 'да', 'д']:
        success = create_topics_with_preview(topics_data)
        
        if success:
            print("✅ Script completed successfully!")
            sys.exit(0)
        else:
            print("❌ Script failed!")
            sys.exit(1)
    else:
        print("❌ Operation cancelled by user")
        sys.exit(0)

if __name__ == '__main__':
    main()
