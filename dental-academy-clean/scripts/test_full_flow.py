import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from models import User
from datetime import datetime, timezone

def create_test_user():
    with app.app_context():
        # Создаем тестового пользователя
        test_email = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
        
        user = User(
            email=test_email,
            username=f"test_user_{datetime.now().strftime('%H%M%S')}",
            first_name="Test",
            last_name="User",
            requires_diagnostic=True,  # Важно!
            registration_completed=True,
            email_verified=True
        )
        user.set_password("testpass123")
        
        db.session.add(user)
        db.session.commit()
        
        print(f"✅ Создан тестовый пользователь: {test_email}")
        print(f"   ID: {user.id}")
        print(f"   Пароль: testpass123")
        print(f"   requires_diagnostic: {user.requires_diagnostic}")
        print("\n🔗 Теперь:")
        print(f"   1. Войди в систему с этими данными")
        print(f"   2. Система должна перенаправить на диагностику")
        print(f"   3. После диагностики проверь daily plan")
        
        return user.id, test_email

def test_integration_with_new_user():
    """Тестирование интеграции с новым пользователем"""
    with app.app_context():
        # Создаем тестового пользователя
        user_id, email = create_test_user()
        
        print(f"\n🧪 ТЕСТИРОВАНИЕ НА НОВОМ ПОЛЬЗОВАТЕЛЕ: {email}")
        print("=" * 70)
        
        # Импортируем и запускаем проверку интеграции
        from scripts.check_integration import run_integration_check
        run_integration_check(email)

if __name__ == '__main__':
    test_integration_with_new_user() 