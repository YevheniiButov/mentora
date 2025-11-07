#!/usr/bin/env python3
"""
Тест локального доступа к тестовой карте обучения
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import User, db
from flask_login import login_user

def test_local_access():
    """Тестируем доступ к тестовой карте"""
    with app.app_context():
        print("🧪 ТЕСТ ЛОКАЛЬНОГО ДОСТУПА К ТЕСТОВОЙ КАРТЕ")
        print("=" * 50)
        
        # 1. Проверяем, есть ли пользователи
        users_count = User.query.count()
        print(f"👥 Пользователей в системе: {users_count}")
        
        if users_count == 0:
            print("❌ Нет пользователей в системе!")
            return False
        
        # 2. Получаем первого пользователя
        test_user = User.query.first()
        print(f"👤 Тестовый пользователь: {test_user.get_display_name()} ({test_user.email})")
        
        # 3. Проверяем маршрут тестовой карты
        with app.test_client() as client:
            # Создаем сессию и авторизуемся
            with client.session_transaction() as sess:
                sess['_user_id'] = str(test_user.id)
                sess['_fresh'] = True
            
            # Тестируем доступ к тестовой карте
            response = client.get('/test-learning-map/')
            print(f"📊 Статус ответа: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ Тестовая карта доступна!")
                
                # Проверяем содержимое
                content = response.get_data(as_text=True)
                if 'Тестовая карта обучения' in content:
                    print("✅ Заголовок найден в содержимом")
                else:
                    print("❌ Заголовок не найден в содержимом")
                
                if 'Статистика пользователя' in content:
                    print("✅ Статистика пользователя найдена")
                else:
                    print("❌ Статистика пользователя не найдена")
                
                return True
            else:
                print(f"❌ Ошибка доступа: {response.status_code}")
                return False

if __name__ == "__main__":
    if test_local_access():
        print("\n🎉 Тестовая карта работает локально!")
        print("🌐 Откройте: http://127.0.0.1:5002/test-learning-map/")
    else:
        print("\n💥 Проблемы с доступом к тестовой карте!")







