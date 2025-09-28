#!/usr/bin/env python3
"""
Скрипт для отправки инструкций по восстановлению пароля всем пользователям.
"""

import os
import sys
from datetime import datetime, timezone

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from models import db, User

def send_instructions_to_users():
    """Отправляет инструкции по восстановлению пароля всем пользователям"""
    
    with app.app_context():
        try:
            print("📧 Отправка инструкций по восстановлению пароля...")
            
            # Находим всех пользователей
            users = User.query.filter(User.email.isnot(None)).all()
            
            print(f"📋 Найдено {len(users)} пользователей для отправки инструкций")
            
            sent_count = 0
            failed_count = 0
            
            for user in users:
                try:
                    print(f"\n👤 Отправка пользователю: {user.email}")
                    
                    # Генерируем токен сброса пароля
                    reset_token = user.generate_password_reset_token()
                    db.session.commit()
                    
                    # Отправляем email
                    from utils.email_service import send_password_reset_email
                    email_sent = send_password_reset_email(user, reset_token)
                    
                    if email_sent:
                        print(f"   ✅ Email отправлен")
                        sent_count += 1
                    else:
                        print(f"   ❌ Не удалось отправить email")
                        failed_count += 1
                        
                except Exception as e:
                    print(f"   ❌ Ошибка для {user.email}: {str(e)}")
                    failed_count += 1
            
            print(f"\n📊 Результаты:")
            print(f"   ✅ Отправлено: {sent_count}")
            print(f"   ❌ Ошибок: {failed_count}")
            print(f"   📧 Всего: {len(users)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка при отправке инструкций: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

def create_instruction_email():
    """Создает шаблон email с инструкциями"""
    
    template = """
# Инструкции по восстановлению доступа к аккаунту Mentora

## Проблема
Мы обнаружили техническую проблему с системой регистрации, которая могла повлиять на ваш доступ к аккаунту.

## Решение
1. Перейдите на страницу восстановления пароля: https://bigmentor.nl/forgot-password
2. Введите ваш email адрес
3. Проверьте почту и перейдите по ссылке в письме
4. Установите новый пароль
5. Войдите в систему с новым паролем

## Альтернатива
Если у вас есть проблемы с восстановлением пароля, обратитесь к администратору.

## Контакты
- Email: support@mentora.com
- Сайт: https://bigmentor.nl

С уважением,
Команда Mentora
"""
    
    with open('password_reset_instructions.txt', 'w', encoding='utf-8') as f:
        f.write(template)
    
    print("📝 Создан файл password_reset_instructions.txt с инструкциями")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--create-template':
        create_instruction_email()
    else:
        print("📧 Отправка инструкций по восстановлению пароля")
        print("=" * 50)
        print()
        print("Этот скрипт отправит всем пользователям инструкции по восстановлению пароля.")
        print()
        
        confirm = input("Продолжить? (y/N): ").strip().lower()
        if confirm == 'y':
            success = send_instructions_to_users()
            if success:
                print("\n✅ Отправка завершена!")
            else:
                print("\n❌ Отправка завершилась с ошибками!")
        else:
            print("Отменено пользователем.")


