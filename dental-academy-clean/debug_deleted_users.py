#!/usr/bin/env python3
"""
Диагностика ошибки 500 на странице удаленных пользователей
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import User
from extensions import db

def debug_deleted_users():
    """Диагностика страницы удаленных пользователей"""
    with app.app_context():
        print("🔍 ДИАГНОСТИКА УДАЛЕННЫХ ПОЛЬЗОВАТЕЛЕЙ")
        print("=" * 50)
        
        try:
            # 1. Проверяем, существуют ли поля для мягкого удаления
            print("\n📊 ПРОВЕРКА ПОЛЕЙ БАЗЫ ДАННЫХ:")
            inspector = db.inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('user')]
            
            required_fields = ['is_deleted', 'deleted_at', 'deleted_by']
            for field in required_fields:
                if field in columns:
                    print(f"   ✅ {field}: существует")
                else:
                    print(f"   ❌ {field}: НЕ НАЙДЕНО!")
            
            # 2. Проверяем количество пользователей
            print(f"\n👥 СТАТИСТИКА ПОЛЬЗОВАТЕЛЕЙ:")
            total_users = User.query.count()
            active_users = User.query.filter(User.is_deleted == False).count()
            deleted_users = User.query.filter(User.is_deleted == True).count()
            
            print(f"   Всего пользователей: {total_users}")
            print(f"   Активных: {active_users}")
            print(f"   Удаленных: {deleted_users}")
            
            # 3. Проверяем запрос удаленных пользователей
            print(f"\n🔍 ТЕСТИРОВАНИЕ ЗАПРОСА:")
            try:
                deleted_query = User.query.filter(User.is_deleted == True)
                deleted_count = deleted_query.count()
                print(f"   ✅ Запрос удаленных пользователей работает: {deleted_count} записей")
                
                # Пробуем получить первую страницу
                page = deleted_query.paginate(page=1, per_page=20, error_out=False)
                print(f"   ✅ Пагинация работает: {page.total} записей, {len(page.items)} на странице")
                
            except Exception as e:
                print(f"   ❌ Ошибка в запросе: {str(e)}")
                return False
            
            # 4. Проверяем шаблон
            print(f"\n📄 ПРОВЕРКА ШАБЛОНА:")
            template_path = "templates/admin/deleted_users.html"
            if os.path.exists(template_path):
                print(f"   ✅ Шаблон существует: {template_path}")
            else:
                print(f"   ❌ Шаблон НЕ НАЙДЕН: {template_path}")
                return False
            
            # 5. Тестируем рендеринг шаблона
            print(f"\n🎨 ТЕСТИРОВАНИЕ РЕНДЕРИНГА:")
            try:
                from flask import render_template
                from datetime import datetime
                
                # Создаем тестовые данные
                test_data = {
                    'users': page,
                    'stats': {
                        'total_deleted': deleted_count,
                        'deleted_admins': User.query.filter(User.is_deleted == True, User.role == 'admin').count(),
                        'deleted_users': User.query.filter(User.is_deleted == True, User.role == 'user').count(),
                    },
                    'search': '',
                    'role_filter': 'all',
                    'sort_by': 'deleted_at',
                    'sort_order': 'desc'
                }
                
                # Пробуем рендерить шаблон
                rendered = render_template('admin/deleted_users.html', **test_data)
                print(f"   ✅ Шаблон рендерится успешно ({len(rendered)} символов)")
                
            except Exception as e:
                print(f"   ❌ Ошибка рендеринга: {str(e)}")
                import traceback
                traceback.print_exc()
                return False
            
            print(f"\n✅ ВСЕ ПРОВЕРКИ ПРОШЛИ УСПЕШНО!")
            return True
            
        except Exception as e:
            print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == "__main__":
    if debug_deleted_users():
        print("\n🎉 Диагностика завершена успешно!")
    else:
        print("\n💥 Обнаружены проблемы!")






