from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from flask_mail import Message
from extensions import mail, db
from models import User, Contact
from utils.decorators import admin_required
from datetime import datetime, timedelta
import json
import logging

communication_bp = Blueprint('communication', __name__, url_prefix='/admin/communication')

# Проверка SMTP конфигурации
@communication_bp.before_request
def check_mail_config():
    """Проверяем, что SMTP настроен"""
    if not mail:
        flash('SMTP не настроен! Проверьте конфигурацию email.', 'error')

# Главная страница Communication Hub
@communication_bp.route('/')
@login_required
@admin_required
def hub():
    """Главная страница Communication Hub"""
    # Получаем статистику для отображения
    users = User.query.filter(User.email.isnot(None)).all()
    contacts = Contact.query.filter(Contact.email.isnot(None)).all()
    
    return render_template('admin/communication/hub.html', 
                         users=users, contacts=contacts)

# Отправка профессиональных email
@communication_bp.route('/send-professional', methods=['GET', 'POST'])
@login_required
@admin_required
def send_professional():
    """Отправка профессиональных email с реальной функциональностью"""
    
    if request.method == 'POST':
        try:
            # Получение данных формы
            template_type = request.form.get('template_type')
            recipients = request.form.getlist('recipients')
            subject = request.form.get('subject')
            additional_data = request.form.get('additional_data', '')
            
            if not template_type or not recipients or not subject:
                flash('Please fill in all required fields!', 'error')
                return redirect(url_for('communication.send_professional'))
            
            # РЕАЛЬНАЯ отправка через Flask-Mail
            sent_count = 0
            failed_count = 0
            
            for recipient_email in recipients:
                try:
                    # Создаем сообщение
                    msg = Message(
                        subject=subject,
                        recipients=[recipient_email],
                        html=render_template(
                            f'admin/communication/email_templates/{template_type}.html',
                            additional_data=additional_data,
                            recipient_email=recipient_email,
                            current_user=current_user
                        ),
                        sender=('Mentora Team', 'info@bigmentor.nl')
                    )
                    
                    # Отправляем email
                    mail.send(msg)
                    sent_count += 1
                    
                    # Логируем успешную отправку
                    current_app.logger.info(f'Professional email sent to {recipient_email} using template {template_type}')
                    
                except Exception as e:
                    failed_count += 1
                    current_app.logger.error(f'Failed to send email to {recipient_email}: {str(e)}')
            
            # Результат отправки
            if sent_count > 0:
                if failed_count == 0:
                    flash(f'✅ Email sent successfully to {sent_count} recipients!', 'success')
                else:
                    flash(f'⚠️ Email sent to {sent_count} recipients, {failed_count} failed.', 'warning')
            else:
                flash('❌ Failed to send email to any recipients!', 'error')
            
            return redirect(url_for('communication.hub'))
            
        except Exception as e:
            current_app.logger.error(f'Email sending failed: {str(e)}')
            flash(f'❌ Email sending failed: {str(e)}', 'error')
    
    # Получение пользователей для выбора получателей
    users = User.query.filter(User.email.isnot(None)).all()
    contacts = Contact.query.filter(Contact.email.isnot(None)).all()
    
    return render_template('admin/communication/send_professional.html', 
                         users=users, contacts=contacts)

# API для поиска пользователей
@communication_bp.route('/api/search-users')
@login_required
@admin_required
def search_users():
    """API для поиска пользователей и контактов"""
    query = request.args.get('query', '').strip()
    
    if len(query) < 2:
        return jsonify([])
    
    # Поиск пользователей
    users = User.query.filter(
        db.or_(
            User.email.contains(query),
            User.first_name.contains(query),
            User.last_name.contains(query)
        )
    ).filter(User.email.isnot(None)).limit(10).all()
    
    # Поиск контактов
    contacts = Contact.query.filter(
        db.or_(
            Contact.email.contains(query),
            Contact.first_name.contains(query),
            Contact.last_name.contains(query)
        )
    ).filter(Contact.email.isnot(None)).limit(10).all()
    
    # Формируем результат
    result = []
    
    # Добавляем пользователей
    for user in users:
        result.append({
            'id': f'user_{user.id}',
            'email': user.email,
            'name': f"{user.first_name} {user.last_name}".strip() or user.username,
            'type': 'User',
            'type_icon': '👤'
        })
    
    # Добавляем контакты
    for contact in contacts:
        result.append({
            'id': f'contact_{contact.id}',
            'email': contact.email,
            'name': f"{contact.first_name} {contact.last_name}".strip() or contact.email,
            'type': 'Contact',
            'type_icon': '📇'
        })
    
    return jsonify(result)

# Предварительный просмотр шаблона
@communication_bp.route('/api/preview-template')
@login_required
@admin_required
def preview_template():
    """API для предварительного просмотра email шаблона"""
    template_type = request.args.get('template_type')
    additional_data = request.args.get('additional_data', '')
    
    if not template_type:
        return jsonify({'success': False, 'error': 'Template type is required'})
    
    try:
        html_content = render_template(
            f'admin/communication/email_templates/{template_type}.html',
            additional_data=additional_data,
            recipient_email='example@example.com',
            current_user=current_user
        )
        return jsonify({'success': True, 'html': html_content})
    except Exception as e:
        current_app.logger.error(f'Template preview failed: {str(e)}')
        return jsonify({'success': False, 'error': str(e)})

# Тестовый маршрут для проверки SMTP
@communication_bp.route('/test-smtp')
@login_required
@admin_required
def test_smtp():
    """Тестовый маршрут для проверки SMTP конфигурации"""
    try:
        # Проверяем конфигурацию
        mail_server = current_app.config.get('MAIL_SERVER')
        mail_port = current_app.config.get('MAIL_PORT')
        mail_username = current_app.config.get('MAIL_USERNAME')
        mail_default_sender = current_app.config.get('MAIL_DEFAULT_SENDER')
        
        config_info = {
            'MAIL_SERVER': mail_server,
            'MAIL_PORT': mail_port,
            'MAIL_USERNAME': mail_username,
            'MAIL_DEFAULT_SENDER': mail_default_sender,
            'MAIL_SUPPRESS_SEND': current_app.config.get('MAIL_SUPPRESS_SEND', False)
        }
        
        # Если отправка отключена, показываем только конфигурацию
        if current_app.config.get('MAIL_SUPPRESS_SEND', False):
            return f"""
            <h2>SMTP Configuration Test</h2>
            <p><strong>Status:</strong> Email sending is suppressed (development mode)</p>
            <h3>Configuration:</h3>
            <pre>{json.dumps(config_info, indent=2)}</pre>
            <p>To test real sending, set MAIL_SUPPRESS_SEND=false</p>
            """
        
        # Пытаемся отправить тестовый email
        test_email = request.args.get('email', 'test@example.com')
        
        msg = Message(
            subject='🧪 SMTP Test from Mentora',
            recipients=[test_email],
            html='''
            <h2>✅ SMTP Test Successful!</h2>
            <p>This is a test email to verify SMTP configuration.</p>
            <p><strong>Sent from:</strong> Mentora Communication Hub</p>
            <p><strong>Time:</strong> {}</p>
            <p><strong>Configuration:</strong></p>
            <pre>{}</pre>
            '''.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                      json.dumps(config_info, indent=2)),
            sender=('Mentora Team', 'info@bigmentor.nl')
        )
        
        mail.send(msg)
        
        return f"""
        <h2>✅ SMTP Test Successful!</h2>
        <p>Test email sent successfully to: <strong>{test_email}</strong></p>
        <h3>Configuration:</h3>
        <pre>{json.dumps(config_info, indent=2)}</pre>
        <p><a href="{url_for('communication.hub')}">← Back to Communication Hub</a></p>
        """
        
    except Exception as e:
        current_app.logger.error(f'SMTP test failed: {str(e)}')
        return f"""
        <h2>❌ SMTP Test Failed!</h2>
        <p><strong>Error:</strong> {str(e)}</p>
        <h3>Configuration:</h3>
        <pre>{json.dumps(config_info, indent=2)}</pre>
        <p><strong>Possible solutions:</strong></p>
        <ul>
            <li>Check MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD</li>
            <li>Verify SMTP credentials</li>
            <li>Check firewall settings</li>
            <li>Enable "Less secure app access" for Gmail</li>
        </ul>
        <p><a href="{url_for('communication.hub')}">← Back to Communication Hub</a></p>
        """

# Статистика отправленных email
@communication_bp.route('/stats')
@login_required
@admin_required
def stats():
    """Статистика отправленных email"""
    # Здесь можно добавить логику для подсчета отправленных email
    # Пока возвращаем простую страницу
    return render_template('admin/communication/stats.html')

# История отправленных email
@communication_bp.route('/history')
@login_required
@admin_required
def history():
    """История отправленных email"""
    # Здесь можно добавить логику для отображения истории
    # Пока возвращаем простую страницу
    return render_template('admin/communication/history.html')