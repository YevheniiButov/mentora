#!/usr/bin/env python3
"""
Безопасное удаление пользователя с очисткой связанных записей
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import User, RegistrationVisitor
from sqlalchemy import text

def delete_user_safely(user_id):
    """Безопасно удаляет пользователя и все связанные записи"""
    
    with app.app_context():
        try:
            print(f"🗑️ Начинаем удаление пользователя ID: {user_id}")
            
            # Проверяем, существует ли пользователь
            user = User.query.get(user_id)
            if not user:
                print(f"❌ Пользователь с ID {user_id} не найден")
                return False
            
            print(f"👤 Найден пользователь: {user.email}")
            
            # 1. Удаляем все записи в registration_visitors
            registration_visitors = RegistrationVisitor.query.filter_by(user_id=user_id).all()
            print(f"📊 Найдено записей в registration_visitors: {len(registration_visitors)}")
            
            for visitor in registration_visitors:
                db.session.delete(visitor)
                print(f"   ✅ Удалена запись visitor ID: {visitor.id}")
            
            # 2. Удаляем посты форума
            try:
                from models import ForumPost
                forum_posts = ForumPost.query.filter_by(author_id=user_id).all()
                print(f"📝 Найдено постов форума: {len(forum_posts)}")
                
                for post in forum_posts:
                    db.session.delete(post)
                    print(f"   ✅ Удален пост ID: {post.id}")
            except Exception as e:
                print(f"   ⚠️ Ошибка при удалении постов форума: {e}")
            
            # 3. Удаляем лайки постов
            try:
                from models import ForumPostLike
                post_likes = ForumPostLike.query.filter_by(user_id=user_id).all()
                print(f"👍 Найдено лайков постов: {len(post_likes)}")
                
                for like in post_likes:
                    db.session.delete(like)
                    print(f"   ✅ Удален лайк поста ID: {like.id}")
            except Exception as e:
                print(f"   ⚠️ Ошибка при удалении лайков постов: {e}")
            
            # 4. Удаляем лайки тем форума
            try:
                from models import ForumTopicLike
                topic_likes = ForumTopicLike.query.filter_by(user_id=user_id).all()
                print(f"👍 Найдено лайков тем: {len(topic_likes)}")
                
                for like in topic_likes:
                    db.session.delete(like)
                    print(f"   ✅ Удален лайк темы ID: {like.id}")
            except Exception as e:
                print(f"   ⚠️ Ошибка при удалении лайков тем: {e}")
            
            # 5. Удаляем темы форума
            try:
                from models import ForumTopic
                forum_topics = ForumTopic.query.filter_by(author_id=user_id).all()
                print(f"📋 Найдено тем форума: {len(forum_topics)}")
                
                for topic in forum_topics:
                    db.session.delete(topic)
                    print(f"   ✅ Удалена тема ID: {topic.id}")
            except Exception as e:
                print(f"   ⚠️ Ошибка при удалении тем форума: {e}")
            
            # 6. Удаляем другие связанные записи
            try:
                # Тестовые результаты
                from models import TestResult
                test_results = TestResult.query.filter_by(user_id=user_id).all()
                if test_results:
                    print(f"📊 Найдено результатов тестов: {len(test_results)}")
                    for result in test_results:
                        db.session.delete(result)
                    print(f"   ✅ Удалены результаты тестов")
                
                # Сессии тестов
                from models import TestSessions
                test_sessions = TestSessions.query.filter_by(user_id=user_id).all()
                if test_sessions:
                    print(f"📊 Найдено сессий тестов: {len(test_sessions)}")
                    for session in test_sessions:
                        db.session.delete(session)
                    print(f"   ✅ Удалены сессии тестов")
                
                # Регистрационные логи
                from models import RegistrationLogs
                reg_logs = RegistrationLogs.query.filter_by(user_id=user_id).all()
                if reg_logs:
                    print(f"📝 Найдено логов регистрации: {len(reg_logs)}")
                    for log in reg_logs:
                        db.session.delete(log)
                    print(f"   ✅ Удалены логи регистрации")
                
                # Активность пользователя
                from models import UserActivity
                user_activities = UserActivity.query.filter_by(user_id=user_id).all()
                if user_activities:
                    print(f"📈 Найдено записей активности: {len(user_activities)}")
                    for activity in user_activities:
                        db.session.delete(activity)
                    print(f"   ✅ Удалены записи активности")
                
                # Достижения
                from models import UserAchievement
                achievements = UserAchievement.query.filter_by(user_id=user_id).all()
                if achievements:
                    print(f"🏆 Найдено достижений: {len(achievements)}")
                    for achievement in achievements:
                        db.session.delete(achievement)
                    print(f"   ✅ Удалены достижения")
                
                # Прогресс обучения
                from models import UserProgress
                progress_records = UserProgress.query.filter_by(user_id=user_id).all()
                if progress_records:
                    print(f"📚 Найдено записей прогресса: {len(progress_records)}")
                    for progress in progress_records:
                        db.session.delete(progress)
                    print(f"   ✅ Удалены записи прогресса")
                
            except Exception as e:
                print(f"   ⚠️ Ошибка при удалении дополнительных записей: {e}")
            
            # 5. Теперь удаляем самого пользователя
            db.session.delete(user)
            print(f"✅ Пользователь {user.email} удален")
            
            # 6. Сохраняем изменения
            db.session.commit()
            print("💾 Изменения сохранены в базе данных")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при удалении пользователя: {e}")
            db.session.rollback()
            return False

def list_users_with_registration_data():
    """Показывает пользователей, у которых есть данные в registration_visitors"""
    
    with app.app_context():
        try:
            print("📋 Пользователи с данными регистрации:")
            
            # SQL запрос для получения пользователей с количеством записей в registration_visitors
            result = db.session.execute(text("""
                SELECT u.id, u.email, u.first_name, u.last_name, COUNT(rv.id) as visitor_records
                FROM "user" u
                LEFT JOIN registration_visitors rv ON u.id = rv.user_id
                WHERE rv.user_id IS NOT NULL
                GROUP BY u.id, u.email, u.first_name, u.last_name
                ORDER BY visitor_records DESC
            """))
            
            users = result.fetchall()
            
            if not users:
                print("   ℹ️ Нет пользователей с данными регистрации")
                return
            
            for user in users:
                user_id, email, first_name, last_name, visitor_records = user
                name = f"{first_name} {last_name}".strip() if first_name or last_name else "Без имени"
                print(f"   👤 ID: {user_id} | Email: {email} | Имя: {name} | Записей: {visitor_records}")
                
        except Exception as e:
            print(f"❌ Ошибка при получении списка пользователей: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python delete_user_safely.py <user_id>     - удалить пользователя")
        print("  python delete_user_safely.py list          - показать пользователей с данными регистрации")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "list":
        list_users_with_registration_data()
    else:
        try:
            user_id = int(command)
            success = delete_user_safely(user_id)
            if success:
                print("🎉 Пользователь успешно удален!")
            else:
                print("💥 Не удалось удалить пользователя")
                sys.exit(1)
        except ValueError:
            print("❌ Неверный ID пользователя. Должно быть число.")
            sys.exit(1)
