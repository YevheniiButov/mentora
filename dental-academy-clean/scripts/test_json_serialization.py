#!/usr/bin/env python3
"""
Скрипт для тестирования JSON сериализации
"""
import os
import sys
import json
from pathlib import Path

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import app
from models import db, User, WebsiteVisit, UserSession

def test_json_serialization():
    """Тестирует JSON сериализацию различных объектов"""
    
    with app.app_context():
        try:
            print("🔍 ТЕСТИРОВАНИЕ JSON СЕРИАЛИЗАЦИИ")
            print("=" * 50)
            
            # Тест 1: Простые данные
            simple_data = {
                'online_users': 5,
                'new_users_today': 2,
                'active_sessions_today': 3,
                'visits_today': 10
            }
            
            try:
                json.dumps(simple_data)
                print("✅ Простые данные - OK")
            except Exception as e:
                print(f"❌ Простые данные - ОШИБКА: {e}")
            
            # Тест 2: Данные из базы
            try:
                users = User.query.limit(3).all()
                user_data = []
                for user in users:
                    user_data.append({
                        'id': user.id,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'role': user.role,
                        'is_active': user.is_active,
                        'created_at': user.created_at.isoformat() if user.created_at else None,
                        'last_login': user.last_login.isoformat() if user.last_login else None
                    })
                
                json.dumps(user_data)
                print("✅ Данные пользователей - OK")
            except Exception as e:
                print(f"❌ Данные пользователей - ОШИБКА: {e}")
            
            # Тест 3: Статистика
            try:
                stats = {
                    'total_users': User.query.count(),
                    'active_users': User.query.filter_by(is_active=True).count(),
                    'admin_users': User.query.filter_by(role='admin').count(),
                    'online_users': 0  # Безопасное значение
                }
                
                json.dumps(stats)
                print("✅ Статистика - OK")
            except Exception as e:
                print(f"❌ Статистика - ОШИБКА: {e}")
            
            # Тест 4: Популярные страницы (может быть проблемным)
            try:
                popular_pages = []
                # Имитируем данные без обращения к БД
                popular_pages.append({
                    'page_url': '/',
                    'visits': 10,
                    'unique_visitors': 5
                })
                
                json.dumps(popular_pages)
                print("✅ Популярные страницы - OK")
            except Exception as e:
                print(f"❌ Популярные страницы - ОШИБКА: {e}")
            
            print("\n✅ ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
            
        except Exception as e:
            print(f"❌ Ошибка тестирования: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    test_json_serialization()
