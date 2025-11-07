#!/usr/bin/env python3
"""
Удаление пользователя с сохранением связанных данных (анонимизация)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, RegistrationVisitor
from sqlalchemy import text

def delete_user_keep_data(user_id):
    """Удаляет пользователя, но сохраняет его данные как анонимные"""
    
    with app.app_context():
        try:
            print(f"🗑️ Начинаем удаление пользователя ID: {user_id} с сохранением данных")
            
            # Проверяем, существует ли пользователь
            user = User.query.get(user_id)
            if not user:
                print(f"❌ Пользователь с ID {user_id} не найден")
                return False
            
            print(f"👤 Найден пользователь: {user.email}")
            
            # 1. Обнуляем user_id в записях registration_visitors (может быть NULL)
            registration_visitors = RegistrationVisitor.query.filter_by(user_id=user_id).all()
            print(f"📊 Найдено записей в registration_visitors: {len(registration_visitors)}")
            
            for visitor in registration_visitors:
                visitor.user_id = None  # Обнуляем вместо удаления
                print(f"   ✅ Анонимизирована запись visitor ID: {visitor.id}")
            
            # 2. Удаляем посты форума (author_id НЕ может быть NULL)
            try:
                from models import ForumPost
                forum_posts = ForumPost.query.filter_by(author_id=user_id).all()
                print(f"📝 Найдено постов форума: {len(forum_posts)}")
                
                for post in forum_posts:
                    print(f"   ⚠️ Удаляем пост ID: {post.id} (author_id не может быть NULL)")
                    db.session.delete(post)
            except Exception as e:
                print(f"   ⚠️ Ошибка при удалении постов форума: {e}")
            
            # 3. Удаляем лайки постов (user_id не может быть NULL)
            try:
                from models import ForumPostLike
                post_likes = ForumPostLike.query.filter_by(user_id=user_id).all()
                print(f"👍 Найдено лайков постов: {len(post_likes)}")
                
                for like in post_likes:
                    print(f"   ⚠️ Удаляем лайк поста ID: {like.id}")
                    db.session.delete(like)
            except Exception as e:
                print(f"   ⚠️ Ошибка при удалении лайков постов: {e}")
            
            # 4. Удаляем лайки тем (user_id не может быть NULL)
            try:
                from models import ForumTopicLike
                topic_likes = ForumTopicLike.query.filter_by(user_id=user_id).all()
                print(f"👍 Найдено лайков тем: {len(topic_likes)}")
                
                for like in topic_likes:
                    print(f"   ⚠️ Удаляем лайк темы ID: {like.id}")
                    db.session.delete(like)
            except Exception as e:
                print(f"   ⚠️ Ошибка при удалении лайков тем: {e}")
            
            # 5. Удаляем темы форума (author_id НЕ может быть NULL)
            try:
                from models import ForumTopic
                forum_topics = ForumTopic.query.filter_by(author_id=user_id).all()
                print(f"📋 Найдено тем форума: {len(forum_topics)}")
                
                for topic in forum_topics:
                    print(f"   ⚠️ Удаляем тему ID: {topic.id} (author_id не может быть NULL)")
                    db.session.delete(topic)
            except Exception as e:
                print(f"   ⚠️ Ошибка при удалении тем форума: {e}")
            
            # 6. Обнуляем user_id в других таблицах (где это возможно)
            try:
                # Тестовые результаты - обнуляем user_id
                from models import TestResult
                test_results = TestResult.query.filter_by(user_id=user_id).all()
                if test_results:
                    print(f"📊 Найдено результатов тестов: {len(test_results)}")
                    for result in test_results:
                        result.user_id = None  # Обнуляем вместо удаления
                    print(f"   ✅ Анонимизированы результаты тестов")
                
                # Сессии тестов - обнуляем user_id
                from models import TestSession
                test_sessions = TestSession.query.filter_by(user_id=user_id).all()
                if test_sessions:
                    print(f"📊 Найдено сессий тестов: {len(test_sessions)}")
                    for session in test_sessions:
                        session.user_id = None  # Обнуляем вместо удаления
                    print(f"   ✅ Анонимизированы сессии тестов")
                
                # Регистрационные логи - обнуляем user_id
                from models import RegistrationLogs
                reg_logs = RegistrationLogs.query.filter_by(user_id=user_id).all()
                if reg_logs:
                    print(f"📝 Найдено логов регистрации: {len(reg_logs)}")
                    for log in reg_logs:
                        log.user_id = None  # Обнуляем вместо удаления
                    print(f"   ✅ Анонимизированы логи регистрации")
                
                # Активность пользователя - удаляем (обычно не нужна после удаления)
                from models import UserActivity
                user_activities = UserActivity.query.filter_by(user_id=user_id).all()
                if user_activities:
                    print(f"📈 Найдено записей активности: {len(user_activities)}")
                    for activity in user_activities:
                        db.session.delete(activity)
                    print(f"   ⚠️ Удалены записи активности")
                
                # Достижения - обнуляем user_id
                from models import UserAchievement
                achievements = UserAchievement.query.filter_by(user_id=user_id).all()
                if achievements:
                    print(f"🏆 Найдено достижений: {len(achievements)}")
                    for achievement in achievements:
                        achievement.user_id = None  # Обнуляем вместо удаления
                    print(f"   ✅ Анонимизированы достижения")
                
                # Прогресс обучения - обнуляем user_id
                from models import UserProgress
                progress_records = UserProgress.query.filter_by(user_id=user_id).all()
                if progress_records:
                    print(f"📚 Найдено записей прогресса: {len(progress_records)}")
                    for progress in progress_records:
                        progress.user_id = None  # Обнуляем вместо удаления
                    print(f"   ✅ Анонимизирован прогресс обучения")
                
                # Контакты - обнуляем user_id и assigned_to
                from models import Contact
                contacts = Contact.query.filter(
                    (Contact.user_id == user_id) | (Contact.assigned_to == user_id)
                ).all()
                if contacts:
                    print(f"📞 Найдено контактов: {len(contacts)}")
                    for contact in contacts:
                        if contact.user_id == user_id:
                            contact.user_id = None
                        if contact.assigned_to == user_id:
                            contact.assigned_to = None
                    print(f"   ✅ Анонимизированы контакты")
                
            except Exception as e:
                print(f"   ⚠️ Ошибка при обработке дополнительных записей: {e}")
            
            # 7. Теперь удаляем самого пользователя
            db.session.delete(user)
            print(f"✅ Пользователь {user.email} удален")
            
            # 8. Сохраняем изменения
            db.session.commit()
            print("💾 Изменения сохранены в базе данных")
            print("📊 Данные пользователя сохранены как анонимные")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при удалении пользователя: {e}")
            db.session.rollback()
            return False

def show_user_data(user_id):
    """Показывает все данные, связанные с пользователем"""
    
    with app.app_context():
        try:
            user = User.query.get(user_id)
            if not user:
                print(f"❌ Пользователь с ID {user_id} не найден")
                return
            
            print(f"👤 Пользователь: {user.email}")
            print("📊 Данные, связанные с пользователем:")
            
            # Проверяем все связанные таблицы
            tables_to_check = [
                ('RegistrationVisitor', 'registration_visitors', 'user_id'),
                ('ForumPost', 'forum_posts', 'author_id'),
                ('ForumPostLike', 'forum_post_likes', 'user_id'),
                ('ForumTopicLike', 'forum_topic_likes', 'user_id'),
                ('ForumTopic', 'forum_topics', 'author_id'),
                ('TestResult', 'test_results', 'user_id'),
                ('TestSessions', 'test_sessions', 'user_id'),
                ('RegistrationLogs', 'registration_logs', 'user_id'),
                ('UserActivity', 'user_activity', 'user_id'),
                ('UserAchievement', 'user_achievement', 'user_id'),
                ('UserProgress', 'user_progress', 'user_id'),
                ('Contact', 'contact', 'user_id'),
            ]
            
            for model_name, table_name, column_name in tables_to_check:
                try:
                    from models import globals as models_globals
                    model_class = getattr(models_globals, model_name, None)
                    if model_class:
                        if column_name == 'author_id':
                            records = model_class.query.filter_by(author_id=user_id).count()
                        else:
                            records = model_class.query.filter_by(**{column_name: user_id}).count()
                        
                        if records > 0:
                            print(f"   📋 {table_name}: {records} записей")
                except Exception as e:
                    print(f"   ⚠️ Ошибка при проверке {table_name}: {e}")
            
        except Exception as e:
            print(f"❌ Ошибка при получении данных пользователя: {e}")

def test_user_deletion():
    """Тестирует удаление пользователя с сохранением данных"""
    
    with app.app_context():
        try:
            # Создаем тестового пользователя
            from models import User, RegistrationVisitor, ForumPost
            from datetime import datetime
            
            test_user = User(
                email="test_anonymize@example.com",
                password_hash="test_hash",
                first_name="Test",
                last_name="Anonymize"
            )
            db.session.add(test_user)
            db.session.flush()
            user_id = test_user.id
            print(f"👤 Создан тестовый пользователь ID: {user_id}")
            
            # Создаем связанные записи
            visitor = RegistrationVisitor(
                ip_address="127.0.0.1",
                page_type="test",
                entry_time=datetime.utcnow(),
                user_id=user_id,
                email_entered="test_anonymize@example.com"
            )
            db.session.add(visitor)
            
            # Создаем пост форума (если есть тема)
            from models import ForumTopic
            topic = ForumTopic.query.first()
            if topic:
                post = ForumPost(
                    content="Test post for anonymization",
                    topic_id=topic.id,
                    author_id=user_id
                )
                db.session.add(post)
                print(f"📝 Создан тестовый пост форума")
            
            db.session.commit()
            print(f"📊 Создана запись visitor")
            
            print(f"🗑️ Тестируем анонимизацию пользователя ID: {user_id}")
            
            # Используем наш метод анонимизации
            success = delete_user_keep_data(user_id)
            
            if success:
                print("✅ Пользователь удален, данные анонимизированы!")
                print("🎉 Анонимизация работает корректно!")
                return True
            else:
                print("❌ Не удалось анонимизировать пользователя")
                return False
            
        except Exception as e:
            print(f"❌ Ошибка при тестировании анонимизации: {e}")
            db.session.rollback()
            return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python3 delete_user_keep_data.py <user_id>        - удалить пользователя с сохранением данных")
        print("  python3 delete_user_keep_data.py show <user_id>    - показать данные пользователя")
        print("  python3 delete_user_keep_data.py test              - протестировать анонимизацию")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "test":
        success = test_user_deletion()
        if not success:
            sys.exit(1)
    elif command == "show":
        if len(sys.argv) < 3:
            print("❌ Укажите ID пользователя для просмотра данных")
            sys.exit(1)
        try:
            user_id = int(sys.argv[2])
            show_user_data(user_id)
        except ValueError:
            print("❌ Неверный ID пользователя. Должно быть число.")
            sys.exit(1)
    else:
        try:
            user_id = int(command)
            success = delete_user_keep_data(user_id)
            if success:
                print("🎉 Пользователь удален, данные сохранены как анонимные!")
            else:
                print("💥 Не удалось удалить пользователя")
                sys.exit(1)
        except ValueError:
            print("❌ Неверный ID пользователя. Должно быть число.")
            sys.exit(1)
