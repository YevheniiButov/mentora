import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt  # Используем Flask-Bcrypt вместо werkzeug.security
from datetime import datetime

# Настройка базовой конфигурации
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)  # Создаем экземпляр bcrypt для этого приложения

# Определение минимального класса User
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    role = db.Column(db.String(20), default='user')
    has_subscription = db.Column(db.Boolean, default=False)
    subscription_expires = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    language = db.Column(db.String(5), default='en')

# Функция создания администратора
def create_admin(email, password, name="Администратор"):
    with app.app_context():
        try:
            # Проверяем, существует ли уже пользователь с таким email
            admin = User.query.filter_by(email=email).first()
            
            if admin:
                if admin.role == 'admin':
                    print(f"Администратор с email {email} уже существует!")
                else:
                    # Обновляем роль до admin
                    admin.role = 'admin'
                    admin.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')  # Используем bcrypt вместо werkzeug
                    admin.name = name
                    admin.has_subscription = True
                    db.session.commit()
                    print(f"Пользователь {email} успешно обновлён до администратора!")
                return
            
            # Создаем нового администратора
            new_admin = User(
                email=email,
                username=email,
                password_hash=bcrypt.generate_password_hash(password).decode('utf-8'),  # Используем bcrypt вместо werkzeug
                name=name,
                role='admin',
                has_subscription=True,
                is_active=True
            )
            
            # Добавляем в базу данных
            db.session.add(new_admin)
            db.session.commit()
            print(f"Администратор {email} успешно создан!")
            print(f"Email: {email}")
            print(f"Пароль: {password}")
            
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка при создании администратора: {e}")
            print("Проверьте структуру базы данных и модели User.")

if __name__ == "__main__":
    # Если переданы аргументы, используем их
    if len(sys.argv) >= 3:
        email = sys.argv[1]
        password = sys.argv[2]
        name = sys.argv[3] if len(sys.argv) > 3 else "Администратор"
    else:
        # Иначе запрашиваем ввод
        email = input("Введите email администратора: ")
        password = input("Введите пароль: ")
        name = input("Введите имя (по умолчанию 'Администратор'): ") or "Администратор"
    
    create_admin(email, password, name)