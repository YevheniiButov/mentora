from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from extensions import db
from models import User, Contact
from utils.decorators import admin_required
from datetime import datetime, timedelta
import json
import logging

communication_bp = Blueprint('communication', __name__, url_prefix='/admin/communication')

# Проверка Resend API конфигурации
@communication_bp.before_request
def check_resend_config():
    """Проверяем, что Resend API настроен"""
    resend_api_key = current_app.config.get('RESEND_API_KEY')
    if not resend_api_key:
        flash('Resend API не настроен! Проверьте конфигурацию email.', 'error')

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
            
            # РЕАЛЬНАЯ отправка через Resend API
            sent_count = 0
            failed_count = 0
            
            for recipient_email in recipients:
                try:
                    # Генерируем HTML контент
                    html_content = render_template(
                        f'admin/communication/email_templates/{template_type}.html',
                        additional_data=additional_data,
                        recipient_email=recipient_email,
                        current_user=current_user
                    )
                    
                    # Отправляем через Resend API
                    from utils.resend_email_service import send_email_via_resend
                    success = send_email_via_resend(
                        to_email=recipient_email,
                        subject=subject,
                        html_content=html_content,
                        from_name="Mentora Team"
                    )
                    
                    if success:
                        sent_count += 1
                        current_app.logger.info(f'Professional email sent to {recipient_email} using template {template_type} via Resend API')
                    else:
                        failed_count += 1
                        current_app.logger.error(f'Failed to send email to {recipient_email} via Resend API')
                    
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
    
    return render_template('admin/communication/send_professional_email.html', 
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

# Тестовый маршрут для проверки Resend API
@communication_bp.route('/test-smtp')
@login_required
@admin_required
def test_smtp():
    """Тестовый маршрут для проверки Resend API конфигурации"""
    try:
        # Проверяем конфигурацию
        email_provider = current_app.config.get('EMAIL_PROVIDER', 'smtp')
        resend_api_key = current_app.config.get('RESEND_API_KEY')
        resend_from_email = current_app.config.get('RESEND_FROM_EMAIL')
        mail_suppress_send = current_app.config.get('MAIL_SUPPRESS_SEND', False)
        
        config_info = {
            'EMAIL_PROVIDER': email_provider,
            'RESEND_API_KEY': '***' + (resend_api_key[-4:] if resend_api_key else 'None'),
            'RESEND_FROM_EMAIL': resend_from_email,
            'MAIL_SUPPRESS_SEND': mail_suppress_send
        }
        
        # Если отправка отключена, показываем только конфигурацию
        if mail_suppress_send:
            return f"""
            <h2>📧 Resend API Configuration Test</h2>
            <p><strong>Status:</strong> Email sending is suppressed (development mode)</p>
            <h3>Configuration:</h3>
            <pre>{json.dumps(config_info, indent=2)}</pre>
            <p>To test real sending, set MAIL_SUPPRESS_SEND=false</p>
            <p><a href="{url_for('communication.hub')}">← Back to Communication Hub</a></p>
            """
        
        # Пытаемся отправить тестовый email через Resend API
        test_email = request.args.get('email', 'test@example.com')
        
        from utils.resend_email_service import send_email_via_resend
        
        test_html = f'''
        <h2>✅ Resend API Test Successful!</h2>
        <p>This is a test email to verify Resend API configuration.</p>
        <p><strong>Sent from:</strong> Mentora Communication Hub</p>
        <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Provider:</strong> Resend API</p>
        <p><strong>Configuration:</strong></p>
        <pre>{json.dumps(config_info, indent=2)}</pre>
        '''
        
        success = send_email_via_resend(
            to_email=test_email,
            subject='🧪 Resend API Test from Mentora',
            html_content=test_html,
            from_name="Mentora Team"
        )
        
        if success:
            return f"""
            <h2>✅ Resend API Test Successful!</h2>
            <p>Test email sent successfully to: <strong>{test_email}</strong></p>
            <h3>Configuration:</h3>
            <pre>{json.dumps(config_info, indent=2)}</pre>
            <p><a href="{url_for('communication.hub')}">← Back to Communication Hub</a></p>
            """
        else:
            return f"""
            <h2>❌ Resend API Test Failed!</h2>
            <p>Failed to send test email to: <strong>{test_email}</strong></p>
            <h3>Configuration:</h3>
            <pre>{json.dumps(config_info, indent=2)}</pre>
            <p><strong>Possible solutions:</strong></p>
            <ul>
                <li>Check RESEND_API_KEY is set correctly</li>
                <li>Verify RESEND_FROM_EMAIL is valid</li>
                <li>Check Resend API quota and limits</li>
                <li>Verify domain authentication in Resend</li>
            </ul>
            <p><a href="{url_for('communication.hub')}">← Back to Communication Hub</a></p>
            """
        
    except Exception as e:
        current_app.logger.error(f'Resend API test failed: {str(e)}')
        return f"""
        <h2>❌ Resend API Test Failed!</h2>
        <p><strong>Error:</strong> {str(e)}</p>
        <h3>Configuration:</h3>
        <pre>{json.dumps(config_info, indent=2)}</pre>
        <p><strong>Possible solutions:</strong></p>
        <ul>
            <li>Check RESEND_API_KEY is set correctly</li>
            <li>Verify RESEND_FROM_EMAIL is valid</li>
            <li>Check Resend API quota and limits</li>
            <li>Verify domain authentication in Resend</li>
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

# Создание пользователя с отправкой приглашения
@communication_bp.route('/create-user', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    """Создание нового пользователя с отправкой приглашения"""
    
    if request.method == 'POST':
        try:
            # Получение данных формы
            first_name = request.form.get('first_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            email = request.form.get('email', '').strip()
            profession = request.form.get('profession', 'dentist')
            birth_date_str = request.form.get('birth_date', '')
            
            # Валидация
            if not all([first_name, last_name, email]):
                flash('Пожалуйста, заполните все обязательные поля!', 'error')
                return redirect(url_for('communication.create_user'))
            
            # Проверка на существующего пользователя
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash(f'Пользователь с email {email} уже существует!', 'error')
                return redirect(url_for('communication.create_user'))
            
            # Парсинг даты рождения
            birth_date = None
            if birth_date_str:
                try:
                    birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
                except ValueError:
                    flash('Неверный формат даты рождения!', 'error')
                    return redirect(url_for('communication.create_user'))
            
            # Генерация временного пароля
            import secrets
            import string
            temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
            
            # Создание пользователя
            user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                birth_date=birth_date,
                profession=profession,
                required_consents=True,  # Админ создает пользователя
                optional_consents=False,  # По умолчанию без маркетинговых согласий
                is_active=False,  # Требует подтверждения email
                email_confirmed=False
            )
            
            # Установка пароля
            user.set_password(temp_password)
            
            # Сохранение в базу данных
            db.session.add(user)
            db.session.commit()
            
            # Отправка email с приглашением
            try:
                from utils.email_service import send_email_confirmation
                email_sent = send_email_confirmation(user, user.generate_email_confirmation_token(), temp_password)
                
                if email_sent:
                    flash(f'✅ Пользователь {first_name} {last_name} создан успешно! Приглашение отправлено на {email}', 'success')
                    current_app.logger.info(f'User {user.email} created by admin {current_user.email} with invitation sent')
                else:
                    flash(f'⚠️ Пользователь создан, но не удалось отправить приглашение на {email}', 'warning')
                    current_app.logger.warning(f'User {user.email} created but invitation email failed')
                    
            except Exception as e:
                flash(f'⚠️ Пользователь создан, но ошибка при отправке приглашения: {str(e)}', 'warning')
                current_app.logger.error(f'User {user.email} created but invitation email error: {str(e)}')
            
            return redirect(url_for('communication.hub'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f'User creation failed: {str(e)}')
            flash(f'❌ Ошибка при создании пользователя: {str(e)}', 'error')
            return redirect(url_for('communication.create_user'))
    
    # GET запрос - показать форму
    return render_template('admin/communication/create_user.html')