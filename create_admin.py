import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

# Импортируем модели и конфигурацию из основного приложения
from app import create_app
from models import User
from extensions import db, bcrypt

# Создаем приложение с правильной конфигурацией
app = create_app()

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
                    admin.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
                    admin.name = name
                    admin.has_subscription = True
                    db.session.commit()
                    print(f"Пользователь {email} успешно обновлён до администратора!")
                return
            
            # Создаем нового администратора
            new_admin = User(
                email=email,
                username=email,
                password_hash=bcrypt.generate_password_hash(password).decode('utf-8'),
                name=name,
                role='admin',
                has_subscription=True,
                is_active=True,
                language='en'  # Добавляем язык по умолчанию
            )
            
            # Добавляем в базу данных
            db.session.add(new_admin)
            db.session.commit()
            
            # Проверяем, что хеш пароля создан правильно
            if not new_admin.password_hash.startswith('$2b$'):
                raise Exception("Неверный формат хеша пароля")
            
            print(f"Администратор {email} успешно создан!")
            print(f"Email: {email}")
            print(f"Пароль: {password}")
            print(f"Хеш пароля: {new_admin.password_hash[:20]}...")
            
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
        password = input("Введите пароль (минимум 6 символов): ")
        while len(password) < 6:
            print("Пароль должен содержать минимум 6 символов!")
            password = input("Введите пароль (минимум 6 символов): ")
        name = input("Введите имя (по умолчанию 'Администратор'): ") or "Администратор"
    
    create_admin(email, password, name)