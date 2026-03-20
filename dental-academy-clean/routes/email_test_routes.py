# routes/email_test_routes.py - Тестовые роуты для email

from flask import Blueprint, request, jsonify, render_template, current_app
from flask_login import login_required, current_user
from extensions import mail
from flask_mail import Message
from datetime import datetime

email_test_bp = Blueprint('email_test', __name__)

@email_test_bp.route('/test-email')
# @login_required  # Убираем требование авторизации для тестирования  
def test_email_page():
    """Страница для тестирования email"""
    return render_template('test_email.html')

@email_test_bp.route('/send-test-email', methods=['POST'])
# @login_required  # Убираем для тестирования
def send_test_email():
    """API для отправки тестового email"""
    try:
        recipient = request.json.get('recipient', 'xapstom@gmail.com')  # Дефолтный email
        
        # Создаем тестовое сообщение
        msg = Message(
            subject='🦷 Mentora - Тестовое письмо',
            recipients=[recipient]
        )
        
        msg.html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                <div style="background: linear-gradient(135deg, #1d4ed8, #2DB5A9); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="margin: 0; font-size: 28px;">🦷 Mentora</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Система обучения медицинских работников</p>
                </div>
                
                <div style="padding: 30px;">
                    <h2 style="color: #2d3748; margin-top: 0;">Тестовое письмо</h2>
                    
                    <p style="color: #4a5568; line-height: 1.6;">
                        Привет, <strong>Тестер</strong>!
                    </p>
                    
                    <p style="color: #4a5568; line-height: 1.6;">
                        Это тестовое письмо для проверки работы email-системы Mentora.
                        Если вы получили это сообщение, значит настройка email работает корректно!
                    </p>
                    
                    <div style="background-color: #f7fafc; border-left: 4px solid #1d4ed8; padding: 15px; margin: 20px 0;">
                        <h3 style="margin: 0 0 10px 0; color: #2d3748; font-size: 16px;">Информация о тесте:</h3>
                        <ul style="margin: 0; padding-left: 20px; color: #4a5568;">
                            <li>Время отправки: {datetime.now().strftime('%d.%m.%Y %H:%M')}</li>
                            <li>Получатель: {recipient}</li>
                            <li>SMTP сервер: {current_app.config.get('MAIL_SERVER')}</li>
                            <li>Порт: {current_app.config.get('MAIL_PORT')}</li>
                        </ul>
                    </div>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="https://mentora.com.in/dashboard" 
                           style="background: linear-gradient(135deg, #1d4ed8, #2DB5A9); color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                            Перейти в дашборд
                        </a>
                    </div>
                    
                    <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 30px 0;">
                    
                    <p style="color: #718096; font-size: 14px; text-align: center; margin: 0;">
                        С уважением,<br>
                        <strong>Команда Mentora</strong><br>
                        <a href="https://mentora.com.in" style="color: #1d4ed8;">mentora.com.in</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.body = f"""
Mentora - Тестовое письмо

Привет, Тестер!

Это тестовое письмо для проверки работы email-системы Mentora.
Если вы получили это сообщение, значит настройка email работает корректно!

Информация о тесте:
- Время отправки: {datetime.now().strftime('%d.%m.%Y %H:%M')}
- Получатель: {recipient}
- SMTP сервер: {current_app.config.get('MAIL_SERVER')}
- Порт: {current_app.config.get('MAIL_PORT')}

Перейти в дашборд: https://mentora.com.in/dashboard

С уважением,
Команда Mentora
https://mentora.com.in
        """
        
        # Отправляем письмо
        mail.send(msg)
        
        return jsonify({
            'success': True,
            'message': f'Тестовое письмо отправлено на {recipient}',
            'smtp_info': {
                'server': current_app.config.get('MAIL_SERVER'),
                'port': current_app.config.get('MAIL_PORT'),
                'suppress_send': current_app.config.get('MAIL_SUPPRESS_SEND')
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }), 500

@email_test_bp.route('/email-config')
# @login_required  # Убираем для тестирования
def email_config():
    """Показать текущую конфигурацию email"""
    config_info = {
        'MAIL_SERVER': current_app.config.get('MAIL_SERVER'),
        'MAIL_PORT': current_app.config.get('MAIL_PORT'),
        'MAIL_USE_TLS': current_app.config.get('MAIL_USE_TLS'),
        'MAIL_USE_SSL': current_app.config.get('MAIL_USE_SSL'),
        'MAIL_USERNAME': current_app.config.get('MAIL_USERNAME'),
        'MAIL_DEFAULT_SENDER': current_app.config.get('MAIL_DEFAULT_SENDER'),
        'MAIL_SUPPRESS_SEND': current_app.config.get('MAIL_SUPPRESS_SEND'),
        'FLASK_ENV': current_app.config.get('FLASK_ENV')
    }
    
    return jsonify({
        'success': True,
        'config': config_info,
        'recommendations': {
            'mail_suppress_send': 'Должно быть False для отправки писем',
            'mail_server': 'Должен быть smtp-relay.brevo.com',
            'mail_port': 'Должен быть 587 для TLS',
            'mail_use_tls': 'Должно быть True для безопасности'
        }
    })
