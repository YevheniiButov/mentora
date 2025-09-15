#!/usr/bin/env python3
"""
ФИНАЛЬНЫЙ ТЕСТ РЕГИСТРАЦИИ
Полное тестирование процесса регистрации с детальным логированием
"""

import os
import sys

print("🦷 Mentora Registration Email Final Test")
print("=" * 60)
print("Проверяем ВСЕ шаги процесса регистрации")
print()

print("📋 ПРОБЛЕМЫ КОТОРЫЕ БЫЛИ ИСПРАВЛЕНЫ:")
print("-" * 40)
print("✅ 1. Расхождение доменов: mentora.com vs mentora.com.in")
print("✅ 2. Ошибки в email шаблонах: url_for() в email")
print("✅ 3. Недостаточное логирование в email_service.py")
print("✅ 4. Добавлено логирование в auth_routes.py")
print()

print("🔍 ЧТО ТЕПЕРЬ ПРОВЕРЯЕМ:")
print("-" * 40)
print("1. Прямая отправка email (как на /test-email)")
print("2. Функция send_email_confirmation")
print("3. Полный процесс регистрации")
print("4. Анализ различий")
print()

# Настройки как в продакшене
os.environ['FLASK_ENV'] = 'production'
os.environ['MAIL_SUPPRESS_SEND'] = 'false'
os.environ['MAIL_SERVER'] = 'smtp-relay.brevo.com'
os.environ['MAIL_PORT'] = '587'
os.environ['MAIL_USE_TLS'] = 'True'
os.environ['MAIL_USERNAME'] = '96d92f002@smtp-brevo.com'
os.environ['MAIL_PASSWORD'] = 'AdHL3pP0rkRt1S8N'
os.environ['MAIL_DEFAULT_SENDER'] = 'Mentora <noreply@mentora.com.in>'

try:
    from app import app
    from extensions import db, mail
    from models import User
    from utils.email_service import send_email_confirmation
    from flask_mail import Message
    
    def test_direct_email():
        """Тест прямой отправки (как test-email работает)"""
        print("🧪 ТЕСТ 1: Прямая отправка email")
        print("-" * 50)
        
        with app.app_context():
            try:
                # Создаем сообщение точно как в email_test_routes.py
                msg = Message(
                    subject='🧪 Final Test - Direct Email',
                    recipients=['xapstom@gmail.com']
                )
                
                msg.html = """
                <h1>🧪 Финальный тест прямой отправки</h1>
                <p>Если вы получили это письмо, значит прямая отправка через Flask-Mail работает!</p>
                """
                
                msg.body = "Финальный тест прямой отправки через Flask-Mail"
                
                print(f"📧 Создание сообщения: OK")
                print(f"📨 Получатель: {msg.recipients}")
                print(f"📤 Отправка...")
                
                mail.send(msg)
                
                print("✅ Прямая отправка УСПЕШНА!")
                return True
                
            except Exception as e:
                print(f"❌ Ошибка прямой отправки: {e}")
                return False
    
    def test_email_confirmation_function():
        """Тест функции send_email_confirmation"""
        print("\n🧪 ТЕСТ 2: Функция send_email_confirmation")
        print("-" * 50)
        
        with app.app_context():
            # Создаем тестового пользователя
            test_user = User(
                email='test.final@example.com',
                first_name='Final',
                last_name='Test'
            )
            test_user.id = 999
            
            test_token = 'final-test-token-123'
            
            print(f"👤 Тестовый пользователь: {test_user.email}")
            print(f"🔑 Токен: {test_token}")
            print(f"📤 Вызов send_email_confirmation...")
            
            try:
                result = send_email_confirmation(test_user, test_token)
                
                if result:
                    print("✅ send_email_confirmation УСПЕШНА!")
                    return True
                else:
                    print("❌ send_email_confirmation вернула False!")
                    return False
                    
            except Exception as e:
                print(f"❌ Ошибка send_email_confirmation: {e}")
                import traceback
                print(f"📋 Трейсбек: {traceback.format_exc()}")
                return False
    
    def analyze_differences():
        """Анализ различий между работающим и неработающим"""
        print("\n📊 АНАЛИЗ РАЗЛИЧИЙ")
        print("-" * 50)
        
        print("🔄 Работающий процесс (test-email):")
        print("   1. Flask app context")
        print("   2. Message() создание") 
        print("   3. mail.send() прямой вызов")
        print("   4. ✅ Успех")
        print()
        
        print("🔄 Процесс регистрации:")
        print("   1. Flask app context")
        print("   2. send_email_confirmation() вызов")
        print("   3. └─ render_template() для HTML/Text")
        print("   4. └─ Message() создание")
        print("   5. └─ mail.send() вызов")
        print("   6. ❓ Неизвестный результат")
        print()
        
        print("💡 ВОЗМОЖНЫЕ ПРОБЛЕМЫ:")
        print("   • Ошибка в render_template()")
        print("   • Неправильные URL в шаблонах") 
        print("   • Исключение не логируется")
        print("   • mail объект не инициализирован правильно")
    
    def recommendations():
        """Рекомендации для дальнейшей диагностики"""
        print("\n📝 РЕКОМЕНДАЦИИ")
        print("-" * 50)
        
        print("🎯 СЛЕДУЮЩИЕ ШАГИ:")
        print("1. Запустите приложение заново")
        print("2. Попробуйте регистрацию")
        print("3. Смотрите на логи в консоли - теперь все детально логируется")
        print("4. Если email_sent = False:")
        print("   • Проверьте трейсбек в логах")
        print("   • Проверьте шаблоны emails/")
        print("   • Проверьте что mail объект инициализирован")
        print()
        
        print("🔧 ЕСЛИ ПРОБЛЕМА ОСТАЕТСЯ:")
        print("1. Временно замените send_email_confirmation на прямой вызов:")
        print("   msg = Message(...)")
        print("   mail.send(msg)")
        print("2. Проверьте что в продакшене MAIL_SUPPRESS_SEND=false")
        print("3. Добавьте try/except в каждый шаг send_email_confirmation")
        print()
        
        print("📧 БЫСТРЫЙ WORKAROUND:")
        print("Если нужно срочно, можно:")
        print("• Скопировать логику из email_test_routes.py")
        print("• Заменить send_email_confirmation прямой отправкой")
        print("• Или временно отключить email подтверждение")
    
    def run_final_test():
        """Запуск финального теста"""
        print("🚀 ЗАПУСК ФИНАЛЬНОГО ТЕСТА")
        print("=" * 60)
        
        # Тесты
        test1_success = test_direct_email()
        test2_success = test_email_confirmation_function()
        
        # Анализ
        analyze_differences()
        
        # Результаты
        print("\n📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ")
        print("=" * 40)
        print(f"✅ Прямая отправка: {'РАБОТАЕТ' if test1_success else 'НЕ РАБОТАЕТ'}")
        print(f"{'✅' if test2_success else '❌'} Email confirmation: {'РАБОТАЕТ' if test2_success else 'НЕ РАБОТАЕТ'}")
        
        if test1_success and test2_success:
            print("\n🎉 ОБА ТЕСТА ПРОШЛИ!")
            print("📧 Email отправка должна работать в регистрации")
            print("🔍 Если письма все еще не приходят - проверьте продакшен логи")
        elif test1_success and not test2_success:
            print("\n⚠️ НАЙДЕНА ПРОБЛЕМА!")
            print("📧 Прямая отправка работает, но send_email_confirmation НЕТ")
            print("🎯 Проблема в функции send_email_confirmation или шаблонах")
        else:
            print("\n❌ КРИТИЧЕСКАЯ ПРОБЛЕМА!")
            print("📧 Даже прямая отправка не работает")
            print("🔧 Проверьте базовые настройки SMTP")
        
        # Рекомендации
        recommendations()
        
        return test1_success, test2_success
    
    if __name__ == '__main__':
        run_final_test()

except ImportError as e:
    print(f"❌ Ошибка импорта: {e}")
    print("🔍 Убедитесь, что скрипт запускается из корневой директории проекта")
except Exception as e:
    print(f"❌ Неожиданная ошибка: {e}")
    import traceback
    print(f"📋 Трейсбек: {traceback.format_exc()}")
