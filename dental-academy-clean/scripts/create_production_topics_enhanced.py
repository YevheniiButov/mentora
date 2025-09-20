#!/usr/bin/env python3
"""
Улучшенный скрипт для создания готовых тем в сообществе для продакшена
Работает с различными конфигурациями и окружениями
"""

import os
import sys
import logging
from datetime import datetime, timedelta
import random

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('topic_creation.log')
    ]
)
logger = logging.getLogger(__name__)

def setup_environment():
    """Настройка окружения для работы скрипта"""
    try:
        # Добавляем путь к проекту
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sys.path.insert(0, project_root)
        
        # Проверяем переменные окружения
        logger.info("🔍 Checking environment variables...")
        
        # Проверяем основные переменные
        required_vars = ['DATABASE_URL', 'SECRET_KEY']
        missing_vars = []
        
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.warning(f"⚠️ Missing environment variables: {missing_vars}")
            logger.info("🔧 Trying to load from .env file...")
            
            # Пытаемся загрузить из .env файла
            env_file = os.path.join(project_root, '.env')
            if os.path.exists(env_file):
                from dotenv import load_dotenv
                load_dotenv(env_file)
                logger.info("✅ Loaded environment from .env file")
            else:
                logger.warning("⚠️ No .env file found")
        
        # Проверяем DATABASE_URL
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            logger.error("❌ DATABASE_URL not found!")
            return False
        
        logger.info(f"✅ Database URL configured: {database_url[:20]}...")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error setting up environment: {str(e)}")
        return False

def test_database_connection():
    """Тестирует подключение к базе данных"""
    try:
        from app import app
        from models import db
        
        with app.app_context():
            # Простой тест подключения
            from sqlalchemy import text
            result = db.session.execute(text('SELECT 1')).fetchone()
            if result:
                logger.info("✅ Database connection successful")
                return True
            else:
                logger.error("❌ Database connection failed")
                return False
                
    except Exception as e:
        logger.error(f"❌ Database connection error: {str(e)}")
        return False

def create_fake_users():
    """Создает фейковых пользователей для сообщений"""
    try:
        from models import db, User
        
        fake_users = [
            {'name': 'Maria', 'email': 'maria@example.com'},
            {'name': 'Ahmed', 'email': 'ahmed@example.com'},
            {'name': 'Priya', 'email': 'priya@example.com'},
            {'name': 'Carlos', 'email': 'carlos@example.com'},
            {'name': 'Anna', 'email': 'anna@example.com'},
            {'name': 'Lucas', 'email': 'lucas@example.com'},
            {'name': 'Emma', 'email': 'emma@example.com'},
            {'name': 'Dr. Sarah', 'email': 'drsarah@example.com'},
            {'name': 'Alex', 'email': 'alex@example.com'},
            {'name': 'David', 'email': 'david@example.com'}
        ]
        
        created_users = []
        for user_data in fake_users:
            # Проверяем, не существует ли уже пользователь
            existing_user = User.query.filter_by(email=user_data['email']).first()
            if not existing_user:
                user = User(
                    email=user_data['email'],
                    first_name=user_data['name'],
                    last_name='',
                    role='user',
                    is_active=True,
                    created_at=datetime.now() - timedelta(days=random.randint(30, 90))
                )
                db.session.add(user)
                created_users.append(user)
                logger.info(f"✅ Created fake user: {user_data['name']}")
            else:
                created_users.append(existing_user)
                logger.info(f"⏭️ User already exists: {user_data['name']}")
        
        db.session.commit()
        return created_users
        
    except Exception as e:
        logger.error(f"❌ Error creating fake users: {str(e)}")
        db.session.rollback()
        return []

def create_topic_with_messages(topic_data, fake_users, base_date):
    """Создает тему с сообщениями"""
    try:
        from models import db, ForumTopic, ForumPost
        
        # Создаем тему
        topic = ForumTopic(
            title=topic_data['title'],
            content=topic_data['content'],
            category_id=topic_data['category'].id,
            author_id=topic_data['author'].id,
            status='active',
            is_sticky=False,
            is_locked=False,
            views_count=random.randint(50, 200),
            replies_count=len(topic_data.get('messages', [])),
            likes_count=random.randint(5, 25),
            created_at=base_date,
            updated_at=base_date + timedelta(days=random.randint(1, 5))
        )
        
        db.session.add(topic)
        db.session.flush()  # Получаем ID темы
        
        # Создаем сообщения
        if 'messages' in topic_data:
            for i, message_data in enumerate(topic_data['messages']):
                # Находим пользователя по имени
                author = None
                for user in fake_users:
                    if user.first_name == message_data['author']:
                        author = user
                        break
                
                if not author:
                    author = fake_users[0]  # Fallback
                
                # Создаем реалистичное время с минутами
                hour = message_data.get('hour', 10)
                minute = message_data.get('minute', random.randint(0, 59))
                message_date = base_date + timedelta(days=message_data['day_offset'], hours=hour, minutes=minute)
                
                post = ForumPost(
                    topic_id=topic.id,
                    author_id=author.id,
                    content=message_data['content'],
                    created_at=message_date,
                    updated_at=message_date
                )
                
                db.session.add(post)
        
        return topic
        
    except Exception as e:
        logger.error(f"❌ Error creating topic with messages: {str(e)}")
        db.session.rollback()
        return None

def create_production_topics_enhanced():
    """Создает готовые темы для продакшена с улучшенной обработкой ошибок"""
    
    logger.info("🚀 Starting enhanced topic creation script...")
    
    # Настройка окружения
    if not setup_environment():
        logger.error("❌ Failed to setup environment")
        return False
    
    # Тест подключения к базе данных
    if not test_database_connection():
        logger.error("❌ Database connection test failed")
        return False
    
    try:
        from app import app
        from models import db, ForumCategory, ForumTopic, ForumPost, User
        
        with app.app_context():
            logger.info("🔍 Checking database connection...")
            
            # Проверяем подключение
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            logger.info("✅ Database connection successful")
            
            # Находим или создаем категории
            categories_data = [
                {
                    'name': 'General Discussion',
                    'slug': 'general',
                    'description': 'General discussions about BIG registration and healthcare in the Netherlands',
                    'order': 1
                },
                {
                    'name': 'Study Materials',
                    'slug': 'study-materials',
                    'description': 'Share and discuss study materials for BIG exams',
                    'order': 2
                },
                {
                    'name': 'Support & Help',
                    'slug': 'support',
                    'description': 'Get help and support from the community',
                    'order': 3
                }
            ]
            
            categories = {}
            for cat_data in categories_data:
                category = ForumCategory.query.filter_by(slug=cat_data['slug']).first()
                if not category:
                    category = ForumCategory(
                        name=cat_data['name'],
                        slug=cat_data['slug'],
                        description=cat_data['description'],
                        is_active=True,
                        order=cat_data['order']
                    )
                    db.session.add(category)
                    logger.info(f"✅ Created category: {cat_data['name']}")
                else:
                    logger.info(f"✅ Found category: {cat_data['name']}")
                
                categories[cat_data['slug']] = category
            
            # Сохраняем категории
            db.session.commit()
            
            # Создаем фейковых пользователей
            logger.info("👥 Creating fake users...")
            fake_users = create_fake_users()
            
            if not fake_users:
                logger.error("❌ Failed to create fake users")
                return False
            
            # Находим первого пользователя (админа)
            admin_user = User.query.filter_by(is_admin=True).first()
            if not admin_user:
                admin_user = User.query.first()
            
            if not admin_user:
                logger.error("❌ No users found! Please create a user first.")
                return False
            
            logger.info(f"✅ Found user: {admin_user.email}")
            
            # Создаем темы с сообщениями
            base_date = datetime(2025, 9, 1)  # 1 сентября 2025
            
            topics_data = [
                # General Discussion
                {
                    'title': 'AKV tandartsen - BIG Registration Discussion 🦷',
                    'content': 'Discussion about AKV tests and BIG registration process for dentists. Share your experiences and get help from the community!',
                    'category': categories['general'],
                    'author': admin_user,
                    'messages': [
                        {
                            'author': 'Maria',
                            'content': 'Goedemorgen collega\'s, Ik heb een vraag, moeten we alle documenten bij BiG inleveren voordat we de AKV-toetsen afleggen, of moeten we eerst de tests afleggen?',
                            'day_offset': 0,
                            'hour': 9,
                            'minute': 23
                        },
                        {
                            'author': 'Priya',
                            'content': 'Volgens mij kun je het beste eerst de taaltoets doen en daarna de documenten samen met het taalcertificaat opsturen.',
                            'day_offset': 0,
                            'hour': 9,
                            'minute': 45
                        },
                        {
                            'author': 'Maria',
                            'content': 'Bedankt!',
                            'day_offset': 0,
                            'hour': 14,
                            'minute': 12
                        },
                        {
                            'author': 'Ahmed',
                            'content': 'Hallo er bestaat geen akv test meer 👍',
                            'day_offset': 0,
                            'hour': 14,
                            'minute': 28
                        },
                        {
                            'author': 'Maria',
                            'content': 'Hoe bedoel je?',
                            'day_offset': 0,
                            'hour': 14,
                            'minute': 31
                        },
                        {
                            'author': 'Carlos',
                            'content': 'In plaats van AKV toets, moeten we nu B2+ taal certificaat halen en alle documenten naar CIBG sturen. Daarna krijgen we een datum voor BI-toets',
                            'day_offset': 0,
                            'hour': 14,
                            'minute': 47
                        },
                        {
                            'author': 'Maria',
                            'content': 'Maar als we slagen voor de BGB en of Babel examens, dan wordt dat beschouwd als een B2+ certificaat? Krijgen we een certificaat van hun?',
                            'day_offset': 0,
                            'hour': 16,
                            'minute': 19
                        },
                        {
                            'author': 'Anna',
                            'content': 'Inderdaad',
                            'day_offset': 0,
                            'hour': 16,
                            'minute': 32
                        },
                        {
                            'author': 'Maria',
                            'content': 'Bedankt!',
                            'day_offset': 0,
                            'hour': 18,
                            'minute': 15
                        }
                    ]
                },
                {
                    'title': 'General Chat - Let\'s talk about everything! 💬',
                    'content': 'This is a general discussion thread where you can talk about anything - from your day to your experiences in the Netherlands, or just have a casual conversation with fellow healthcare professionals!',
                    'category': categories['general'],
                    'author': admin_user,
                    'messages': [
                        {
                            'author': 'Emma',
                            'content': 'Dankjewel!',
                            'day_offset': 1,
                            'hour': 9,
                            'minute': 17
                        },
                        {
                            'author': 'Lucas',
                            'content': 'Deze krijg ik net binnen...',
                            'day_offset': 1,
                            'hour': 9,
                            'minute': 34
                        },
                        {
                            'author': 'Alex',
                            'content': 'не за что',
                            'day_offset': 1,
                            'hour': 15,
                            'minute': 22
                        },
                        {
                            'author': 'David',
                            'content': 'Missed voice call',
                            'day_offset': 2,
                            'hour': 11,
                            'minute': 8
                        }
                    ]
                },
                {
                    'title': 'Welcome to Mentora Community! 👋',
                    'content': 'Welcome to our community! This is a place where international healthcare professionals can share experiences, ask questions, and support each other on their journey to BIG registration in the Netherlands.\n\nFeel free to introduce yourself and share your background!',
                    'category': categories['general'],
                    'author': admin_user
                }
            ]
            
            created_count = 0
            for i, topic_data in enumerate(topics_data):
                # Проверяем, не существует ли уже такая тема
                existing_topic = ForumTopic.query.filter_by(
                    title=topic_data['title'],
                    author_id=admin_user.id
                ).first()
                
                if not existing_topic:
                    # Создаем тему с разными датами
                    topic_date = base_date + timedelta(days=i*2)  # Каждая тема через 2 дня
                    
                    if 'messages' in topic_data:
                        topic = create_topic_with_messages(topic_data, fake_users, topic_date)
                    else:
                        topic = ForumTopic(
                            title=topic_data['title'],
                            content=topic_data['content'],
                            category_id=topic_data['category'].id,
                            author_id=topic_data['author'].id,
                            status='active',
                            is_sticky=False,
                            is_locked=False,
                            views_count=random.randint(20, 100),
                            replies_count=0,
                            likes_count=random.randint(2, 15),
                            created_at=topic_date,
                            updated_at=topic_date + timedelta(days=random.randint(1, 3))
                        )
                        db.session.add(topic)
                    
                    if topic:
                        created_count += 1
                        logger.info(f"✅ Created topic: {topic_data['title']}")
                    else:
                        logger.error(f"❌ Failed to create topic: {topic_data['title']}")
                else:
                    logger.info(f"⏭️ Topic already exists: {topic_data['title']}")
            
            # Сохраняем изменения
            db.session.commit()
            
            logger.info(f"\n🎉 Successfully created {created_count} topics!")
            logger.info(f"📊 Total topics in database: {ForumTopic.query.count()}")
            logger.info(f"📁 Categories: {ForumCategory.query.count()}")
            
            return True
            
    except Exception as e:
        logger.error(f"❌ Error creating topics: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return False

if __name__ == '__main__':
    success = create_production_topics_enhanced()
    if success:
        logger.info("✅ Script completed successfully!")
        sys.exit(0)
    else:
        logger.error("❌ Script failed!")
        sys.exit(1)
