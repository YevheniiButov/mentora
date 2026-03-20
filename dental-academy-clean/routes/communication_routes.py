from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from extensions import db
from models import User, Contact, EmailTemplate, IncomingEmail, EmailAttachment
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

# Обработка CSRF токена из JSON для preview запросов
@communication_bp.before_request
def handle_json_csrf():
    """Извлекает CSRF токен из JSON тела запроса и устанавливает в заголовок"""
    if request.method == 'POST' and request.is_json:
        try:
            # Используем get_data с cache=True чтобы можно было прочитать данные несколько раз
            raw_data = request.get_data(cache=True)
            if raw_data:
                data = json.loads(raw_data)
                if 'csrf_token' in data and 'X-CSRFToken' not in request.headers:
                    # Устанавливаем токен в заголовок через environ (Flask-WTF проверяет заголовки)
                    request.environ['HTTP_X_CSRFTOKEN'] = data['csrf_token']
        except (json.JSONDecodeError, TypeError):
            pass  # Если не удалось распарсить, продолжаем без изменений

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

# НОВЫЙ: Массовая рассылка с визуальным редактором
@communication_bp.route('/bulk-email', methods=['GET', 'POST'])
@login_required
@admin_required
def bulk_email():
    """Массовая рассылка с визуальным редактором на основе фирменного шаблона"""
    
    if request.method == 'POST':
        try:
            # Получаем данные из формы
            if request.is_json:
                data = request.get_json() or {}
            else:
                # Обрабатываем FormData (может содержать файлы)
                data = request.form.to_dict()
                # Получаем множественные значения
                if 'value_prop_items' in request.form:
                    data['value_prop_items'] = request.form.getlist('value_prop_items')
                if 'recipient_emails' in request.form:
                    data['recipient_emails'] = request.form.getlist('recipient_emails')
                if 'selected_user_ids' in request.form:
                    data['selected_user_ids'] = request.form.getlist('selected_user_ids')
                # Преобразуем строковые значения в нужные типы
                if 'preview' in data:
                    data['preview'] = data['preview'].lower() in ('true', '1', 'yes', 'on')
            
            # Если это запрос на превью, возвращаем только HTML
            preview_request = data.get('preview', False)
            if isinstance(preview_request, str):
                preview_request = preview_request.lower() in ('true', '1', 'yes', 'on')
            
            if preview_request:
                try:
                    email_template_type = data.get('email_template_type', 'universal')
                    has_gif = data.get('has_gif', False) or data.get('gif_file')  # Для превью
                    
                    if email_template_type == 'big_preparation':
                        greeting_name = data.get('greeting_name', 'there') or 'there'
                        if isinstance(greeting_name, str):
                            greeting_name = greeting_name.strip()
                        cta_url = data.get('cta_url', 'https://bigmentor.nl/en/learning-map') or 'https://bigmentor.nl/en/learning-map'
                        if isinstance(cta_url, str):
                            cta_url = cta_url.strip()
                        
                        html_content = generate_big_preparation_email(
                            greeting_name=greeting_name,
                            cta_url=cta_url
                        )
                    elif email_template_type == 'learning_map_welcome':
                        greeting_name = data.get('greeting_name', 'there') or 'there'
                        if isinstance(greeting_name, str):
                            greeting_name = greeting_name.strip()
                        cta_url = data.get('cta_url', 'https://bigmentor.nl/en/learning-map') or 'https://bigmentor.nl/en/learning-map'
                        if isinstance(cta_url, str):
                            cta_url = cta_url.strip()
                        
                        # Для preview используем has_gif флаг, но файл не загружен
                        html_content = generate_learning_map_welcome_email(
                            greeting_name=greeting_name,
                            cta_url=cta_url,
                            has_gif=bool(has_gif)
                        )
                    else:
                        greeting_name = data.get('greeting_name', 'Иван') or 'Иван'
                        if isinstance(greeting_name, str):
                            greeting_name = greeting_name.strip()
                        main_title = data.get('main_title', '🎯 Начните свой путь к успеху') or '🎯 Начните свой путь к успеху'
                        if isinstance(main_title, str):
                            main_title = main_title.strip()
                        main_subtitle = data.get('main_subtitle', 'Карта Обучения MENTORA готова помочь вам') or 'Карта Обучения MENTORA готова помочь вам'
                        if isinstance(main_subtitle, str):
                            main_subtitle = main_subtitle.strip()
                        intro_text = data.get('intro_text', '') or ''
                        if isinstance(intro_text, str):
                            intro_text = intro_text.strip()
                        value_prop_title = data.get('value_prop_title', '💡 Почему стоит начать прямо сейчас:') or '💡 Почему стоит начать прямо сейчас:'
                        if isinstance(value_prop_title, str):
                            value_prop_title = value_prop_title.strip()
                        value_prop_items = data.get('value_prop_items', [])
                        if isinstance(value_prop_items, str):
                            value_prop_items = [item.strip() for item in value_prop_items.split('\n') if item.strip()]
                        elif not isinstance(value_prop_items, list):
                            value_prop_items = []
                        cta_text = data.get('cta_text', '🚀 Открыть Карту Обучения') or '🚀 Открыть Карту Обучения'
                        if isinstance(cta_text, str):
                            cta_text = cta_text.strip()
                        cta_url = data.get('cta_url', 'https://bigmentor.nl/learning-map') or 'https://bigmentor.nl/learning-map'
                        if isinstance(cta_url, str):
                            cta_url = cta_url.strip()
                        motivation_title = data.get('motivation_title', '💪 Начните с малого') or '💪 Начните с малого'
                        if isinstance(motivation_title, str):
                            motivation_title = motivation_title.strip()
                        motivation_text = data.get('motivation_text', '') or ''
                        if isinstance(motivation_text, str):
                            motivation_text = motivation_text.strip()
                        
                        html_content = generate_email_template(
                            greeting_name=greeting_name,
                            main_title=main_title,
                            main_subtitle=main_subtitle,
                            intro_text=intro_text,
                            value_prop_title=value_prop_title,
                            value_prop_items=value_prop_items,
                            cta_text=cta_text,
                            cta_url=cta_url,
                            motivation_title=motivation_title,
                            motivation_text=motivation_text
                        )
                    
                    return jsonify({'success': True, 'html': html_content})
                except Exception as e:
                    current_app.logger.error(f'Error generating preview: {str(e)}', exc_info=True)
                    return jsonify({'success': False, 'error': f'Ошибка генерации превью: {str(e)}'}), 400
            
            subject = data.get('subject', '').strip()
            email_template_type = data.get('email_template_type', 'universal')  # universal или learning_map_welcome
            gif_file = request.files.get('gif_file')  # Загруженный GIF файл
            
            # Для welcome шаблона нужны только эти поля
            if email_template_type == 'learning_map_welcome':
                greeting_name = data.get('greeting_name', 'there') or 'there'
                if isinstance(greeting_name, str):
                    greeting_name = greeting_name.strip()
                cta_url = data.get('cta_url', 'https://bigmentor.nl/en/learning-map') or 'https://bigmentor.nl/en/learning-map'
                if isinstance(cta_url, str):
                    cta_url = cta_url.strip()
            else:
                # Для универсального шаблона все поля
                greeting_name = data.get('greeting_name', 'Иван') or 'Иван'
                if isinstance(greeting_name, str):
                    greeting_name = greeting_name.strip()
                main_title = data.get('main_title', '🎯 Начните свой путь к успеху') or '🎯 Начните свой путь к успеху'
                if isinstance(main_title, str):
                    main_title = main_title.strip()
                main_subtitle = data.get('main_subtitle', 'Карта Обучения MENTORA готова помочь вам') or 'Карта Обучения MENTORA готова помочь вам'
                if isinstance(main_subtitle, str):
                    main_subtitle = main_subtitle.strip()
                intro_text = data.get('intro_text', '') or ''
                if isinstance(intro_text, str):
                    intro_text = intro_text.strip()
                value_prop_title = data.get('value_prop_title', '💡 Почему стоит начать прямо сейчас:') or '💡 Почему стоит начать прямо сейчас:'
                if isinstance(value_prop_title, str):
                    value_prop_title = value_prop_title.strip()
                value_prop_items = data.get('value_prop_items', [])
                if isinstance(value_prop_items, str):
                    value_prop_items = value_prop_items.strip()
                elif isinstance(value_prop_items, list):
                    value_prop_items = [item.strip() if isinstance(item, str) else str(item) for item in value_prop_items]
                cta_text = data.get('cta_text', '🚀 Открыть Карту Обучения') or '🚀 Открыть Карту Обучения'
                if isinstance(cta_text, str):
                    cta_text = cta_text.strip()
                cta_url = data.get('cta_url', 'https://bigmentor.nl/learning-map') or 'https://bigmentor.nl/learning-map'
                if isinstance(cta_url, str):
                    cta_url = cta_url.strip()
                motivation_title = data.get('motivation_title', '💪 Начните с малого') or '💪 Начните с малого'
                if isinstance(motivation_title, str):
                    motivation_title = motivation_title.strip()
                motivation_text = data.get('motivation_text', '') or ''
                if isinstance(motivation_text, str):
                    motivation_text = motivation_text.strip()
            
            recipient_type = data.get('recipient_type', 'all')  # all, users, contacts, custom, selected
            recipient_emails = data.get('recipient_emails', [])  # Список email для custom
            selected_user_ids = data.get('selected_user_ids', [])  # Список ID выбранных пользователей
            filter_marketing_consent = data.get('filter_marketing_consent', False)  # Только с согласием на маркетинг
            
            # Валидация
            if not subject:
                return jsonify({'success': False, 'error': 'Тема письма обязательна'}), 400
            
            # Определяем получателей
            recipients = []
            
            if recipient_type == 'all':
                query = User.query.filter(User.email.isnot(None), User.is_active == True)
                if filter_marketing_consent:
                    query = query.filter(User.optional_consents == True)
                recipients = [user.email for user in query.all()]
            elif recipient_type == 'users':
                query = User.query.filter(User.email.isnot(None), User.is_active == True)
                if filter_marketing_consent:
                    query = query.filter(User.optional_consents == True)
                recipients = [user.email for user in query.all()]
            elif recipient_type == 'selected':
                # Выбранные пользователи из списка
                if selected_user_ids:
                    if isinstance(selected_user_ids, str):
                        selected_user_ids = [int(id.strip()) for id in selected_user_ids.split(',') if id.strip()]
                    elif not isinstance(selected_user_ids, list):
                        selected_user_ids = []
                    recipients = [user.email for user in User.query.filter(
                        User.id.in_(selected_user_ids),
                        User.email.isnot(None),
                        User.is_active == True
                    ).all()]
                else:
                    recipients = []
            elif recipient_type == 'contacts':
                recipients = [contact.email for contact in Contact.query.filter(Contact.email.isnot(None)).all()]
            elif recipient_type == 'custom':
                recipients = [email.strip() for email in recipient_emails if email.strip()]
            
            if not recipients:
                return jsonify({'success': False, 'error': 'Нет получателей для рассылки'}), 400
            
            # Генерируем HTML на основе выбранного шаблона
            if email_template_type == 'big_preparation':
                html_content = generate_big_preparation_email(
                    greeting_name=greeting_name,
                    cta_url=cta_url
                )
            elif email_template_type == 'learning_map_welcome':
                html_content = generate_learning_map_welcome_email(
                    greeting_name=greeting_name,
                    cta_url=cta_url,
                    has_gif=bool(gif_file and gif_file.filename)
                )
            else:
                # Обрабатываем value_prop_items (может быть строкой или списком) только для универсального шаблона
                if isinstance(value_prop_items, str):
                    # Разбиваем по строкам, если передана строка
                    value_prop_items = [item.strip() for item in value_prop_items.split('\n') if item.strip()]
                elif not isinstance(value_prop_items, list):
                    value_prop_items = []
                
                html_content = generate_email_template(
                    greeting_name=greeting_name,
                    main_title=main_title,
                    main_subtitle=main_subtitle,
                    intro_text=intro_text,
                    value_prop_title=value_prop_title,
                    value_prop_items=value_prop_items,
                    cta_text=cta_text,
                    cta_url=cta_url,
                    motivation_title=motivation_title,
                    motivation_text=motivation_text
                )
            
            # Обрабатываем GIF файл как встроенное изображение через CID
            attachments = None
            if gif_file and gif_file.filename:
                import base64
                gif_content = gif_file.read()
                gif_base64 = base64.b64encode(gif_content).decode('utf-8')
                # Используем CID для встроенного изображения в Resend API
                attachments = [{
                    "filename": gif_file.filename,
                    "content": gif_base64,
                    "cid": "learning_map_gif"  # Content-ID для встраивания в HTML
                }]
            
            # Отправляем через Resend API
            from utils.resend_email_service import send_email_via_resend
            import time
            
            sent_count = 0
            failed_count = 0
            errors = []
            
            # Resend API лимит: 2 запроса в секунду, добавляем задержку 0.6 сек между запросами
            delay_between_emails = 0.6  # 600 мс для надежности (чуть больше чем минимум 0.5 сек)
            
            for idx, recipient_email in enumerate(recipients):
                try:
                    # Добавляем задержку перед каждым запросом (кроме первого)
                    if idx > 0:
                        time.sleep(delay_between_emails)
                    
                    # Попытка отправки с retry при rate limit
                    max_retries = 3
                    retry_delay = 1.0  # Начальная задержка для retry
                    success = False
                    
                    for attempt in range(max_retries):
                        success = send_email_via_resend(
                            to_email=recipient_email,
                            subject=subject,
                            html_content=html_content,
                            from_name="Mentora Team",
                            attachments=attachments
                        )
                        
                        if success:
                            break
                        
                        # Если это не последняя попытка и была ошибка rate limit, ждем и повторяем
                        if attempt < max_retries - 1:
                            # Проверяем, была ли это ошибка rate limit (429)
                            # send_email_via_resend возвращает False при любой ошибке
                            # Добавляем дополнительную задержку перед retry
                            time.sleep(retry_delay * (attempt + 1))  # Экспоненциальная задержка
                    
                    if success:
                        sent_count += 1
                        current_app.logger.info(f'Bulk email sent to {recipient_email} via Resend')
                    else:
                        failed_count += 1
                        errors.append(f"Failed to send to {recipient_email} after {max_retries} attempts")
                        current_app.logger.error(f'Failed to send bulk email to {recipient_email} after {max_retries} attempts')
                        
                except Exception as e:
                    failed_count += 1
                    errors.append(f"Error sending to {recipient_email}: {str(e)}")
                    current_app.logger.error(f'Error sending bulk email to {recipient_email}: {str(e)}')
            
            # Результат
            if sent_count > 0:
                if failed_count == 0:
                    return jsonify({
                        'success': True,
                        'message': f'✅ Email успешно отправлен {sent_count} получателям!',
                        'sent': sent_count,
                        'failed': failed_count
                    })
                else:
                    return jsonify({
                        'success': True,
                        'message': f'⚠️ Email отправлен {sent_count} получателям, {failed_count} не удалось отправить',
                        'sent': sent_count,
                        'failed': failed_count,
                        'errors': errors[:10]  # Первые 10 ошибок
                    })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Не удалось отправить email ни одному получателю',
                    'errors': errors[:10]
                }), 400
                
        except Exception as e:
            current_app.logger.error(f'Bulk email sending failed: {str(e)}', exc_info=True)
            # Всегда возвращаем JSON, даже при ошибках
            return jsonify({'success': False, 'error': str(e)}), 500
    
    # GET запрос - показываем форму
    # Получаем статистику пользователей
    total_users = User.query.filter(User.email.isnot(None), User.is_active == True).count()
    users_with_marketing = User.query.filter(User.email.isnot(None), User.is_active == True, User.optional_consents == True).count()
    total_contacts = Contact.query.filter(Contact.email.isnot(None)).count()
    
    # Получаем список всех пользователей для выбора
    all_users = User.query.filter(User.email.isnot(None), User.is_active == True).order_by(User.email).all()
    
    return render_template('admin/communication/bulk_email.html',
                         total_users=total_users,
                         users_with_marketing=users_with_marketing,
                         total_contacts=total_contacts,
                         all_users=all_users)

def generate_big_preparation_email(greeting_name="there", cta_url="https://bigmentor.nl/en/learning-map"):
    """Генерирует HTML шаблон письма 'Ready to Start Your BIG Preparation?'"""
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ready to Start Your BIG Preparation?</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #f5f5f5;
            color: #1f2937;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
        }}
        
        /* HEADER */
        .header {{
            background: linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%);
            padding: 40px 24px;
            text-align: center;
            color: white;
        }}
        
        .logo {{
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 12px;
            letter-spacing: -0.5px;
        }}
        
        .header-subtitle {{
            font-size: 14px;
            opacity: 0.95;
            font-weight: 400;
        }}
        
        /* MAIN CONTENT */
        .content {{
            padding: 40px 24px;
        }}
        
        .greeting {{
            font-size: 22px;
            font-weight: 600;
            margin-bottom: 16px;
            color: #1f2937;
        }}
        
        .intro-text {{
            font-size: 15px;
            color: #4b5563;
            margin-bottom: 32px;
            line-height: 1.7;
        }}
        
        /* PROBLEM SECTION */
        .problem-section {{
            background-color: #fef3f8;
            border-left: 4px solid #EC4899;
            padding: 20px;
            border-radius: 6px;
            margin: 32px 0;
            font-size: 14px;
            color: #4b5563;
            line-height: 1.7;
        }}
        
        .problem-title {{
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 12px;
            font-size: 15px;
        }}
        
        /* SOLUTION SECTION */
        .solution-section {{
            margin: 40px 0;
            padding: 24px;
            background: linear-gradient(135deg, #f0f4ff 0%, #fef3f8 100%);
            border-radius: 8px;
            border-left: 4px solid #8B5CF6;
        }}
        
        .solution-title {{
            font-size: 16px;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 20px;
        }}
        
        .feature-list {{
            display: grid;
            gap: 14px;
        }}
        
        .feature {{
            display: flex;
            gap: 12px;
            font-size: 14px;
            color: #374151;
        }}
        
        .feature-icon {{
            flex-shrink: 0;
            width: 20px;
            height: 20px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #8B5CF6;
            font-weight: 700;
        }}
        
        /* WHY NOW SECTION */
        .why-now {{
            background-color: #fef3f8;
            padding: 24px;
            border-radius: 8px;
            margin: 32px 0;
            border-left: 4px solid #EC4899;
        }}
        
        .why-now-title {{
            font-size: 14px;
            font-weight: 600;
            color: #EC4899;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 12px;
        }}
        
        .why-now-text {{
            font-size: 14px;
            color: #4b5563;
            line-height: 1.7;
        }}
        
        .highlight {{
            font-weight: 600;
            color: #1f2937;
        }}
        
        /* CTA SECTION */
        .cta-section {{
            margin: 40px 0;
            text-align: center;
        }}
        
        .cta-button {{
            display: inline-block;
            background: linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%);
            color: white;
            padding: 16px 40px;
            border-radius: 6px;
            text-decoration: none;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.2s ease;
            border: none;
            cursor: pointer;
        }}
        
        .cta-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(139, 92, 246, 0.3);
        }}
        
        .cta-secondary {{
            display: block;
            margin-top: 12px;
            font-size: 14px;
            color: #8B5CF6;
            text-decoration: none;
        }}
        
        /* SOCIAL PROOF */
        .social-proof {{
            margin: 32px 0;
            text-align: center;
            font-size: 13px;
            color: #6b7280;
        }}
        
        .proof-item {{
            display: inline-block;
            padding: 0 12px;
        }}
        
        /* FOOTER */
        .footer {{
            background-color: #f9fafb;
            padding: 24px;
            border-top: 1px solid #e5e7eb;
            text-align: center;
            font-size: 12px;
            color: #6b7280;
        }}
        
        /* RESPONSIVE */
        @media (max-width: 480px) {{
            .content {{
                padding: 24px 16px;
            }}
            
            .greeting {{
                font-size: 18px;
            }}
            
            .cta-button {{
                padding: 14px 32px;
                font-size: 15px;
                width: 100%;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- HEADER -->
        <div class="header">
            <div class="logo">Mentora</div>
            <div class="header-subtitle">Your BIG Preparation Starts Here</div>
        </div>
        
        <!-- MAIN CONTENT -->
        <div class="content">
            <div class="greeting">You're Ready to Begin 🚀</div>
            
            <div class="intro-text">
                You created your Mentora account — that's the first step. Now comes the important part: actually starting to prepare for the BIG exam.
                <br><br>
                If you're thinking "where do I even begin?" or "there's so much material" — that's exactly why Mentora exists.
            </div>
            
            <!-- THE PROBLEM -->
            <div class="problem-section">
                <div class="problem-title">Here's the reality:</div>
                You need to pass a complex exam. There are thousands of questions. Limited exam spots. And you don't know where to start.
                <br><br>
                Most people try to study everything at once — and burn out in 2 weeks.
            </div>
            
            <!-- THE SOLUTION -->
            <div class="solution-section">
                <div class="solution-title">Here's what Mentora does:</div>
                <div class="feature-list">
                    <div class="feature">
                        <div class="feature-icon">1</div>
                        <div><strong>Creates a personalized study plan</strong> based on your level — no guessing</div>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">2</div>
                        <div><strong>Picks the right difficulty</strong> for each question — challenging but not overwhelming</div>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">3</div>
                        <div><strong>Shows your progress daily</strong> — so you actually feel motivated to continue</div>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">4</div>
                        <div><strong>Covers all areas:</strong> Tests, Medical Terminology, English Reading, Virtual Patients</div>
                    </div>
                    <div class="feature">
                        <div class="feature-icon">5</div>
                        <div><strong>Works in your language</strong> — 9 languages supported</div>
                    </div>
                </div>
            </div>
            
            <!-- WHY NOW -->
            <div class="why-now">
                <div class="why-now-title">⏰ Why Start Now?</div>
                <div class="why-now-text">
                    The sooner you start, the more time you have to practice. Most people who pass BIG didn't cram — they started early and built consistency.
                    <br><br>
                    Think about it: <span class="highlight">just 30 minutes a day, 5 days a week = 130 hours of study in 3 months.</span> That's the difference between passing and not passing.
                </div>
            </div>
            
            <!-- FIRST STEP -->
            <div style="margin: 32px 0; padding: 20px; background-color: #f9fafb; border-radius: 6px; border: 1px dashed #d1d5db;">
                <div style="font-size: 14px; font-weight: 600; color: #1f2937; margin-bottom: 8px;">Your first step takes 15 minutes:</div>
                <div style="font-size: 14px; color: #4b5563; line-height: 1.6;">
                    1. Log in to your account<br>
                    2. Take a quick diagnostic test<br>
                    3. See your personalized learning plan<br>
                    4. Start your first daily tasks
                </div>
            </div>
            
            <!-- CTA -->
            <div class="cta-section">
                <a href="{cta_url}" class="cta-button">Start Learning Now</a>
                <a href="https://bigmentor.nl/login/auth/login" class="cta-secondary">Log in to your account</a>
            </div>
            
            <!-- PS -->
            <div style="margin-top: 32px; padding: 16px; background-color: #fef3f8; border-radius: 6px; font-size: 14px; color: #4b5563; border-left: 3px solid #8B5CF6;">
                <strong>P.S.</strong> Still not sure? The best way to know if Mentora works for you is to try it. Log in, take one diagnostic test, see if it makes sense. That's 10 minutes. Worth trying, right?
            </div>
        </div>
        
        <!-- FOOTER -->
        <div class="footer">
            <p>Mentora — Platform for BIG Exam Preparation in the Netherlands</p>
            <p style="margin-top: 12px; color: #9ca3af;">© 2025 Mentora. All rights reserved.</p>
        </div>
    </div>
</body>
</html>'''

def generate_learning_map_welcome_email(greeting_name="there", cta_url="https://bigmentor.nl/en/learning-map", has_gif=False):
    """Генерирует HTML шаблон welcome email для карты обучения с GIF"""
    
    gif_section = ''
    if has_gif:
        # Используем CID (Content-ID) для встроенного изображения
        # Resend API будет использовать CID из attachments для встраивания изображения
        gif_section = '''
            <!-- GIF SECTION -->
            <div class="gif-section">
                <img src="cid:learning_map_gif" alt="Mentora Learning Map Demo" style="max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);">
            </div>
        '''
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Learning Map is Ready</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background-color: #f5f5f5;
            color: #1f2937;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: #ffffff;
        }}
        
        /* HEADER */
        .header {{
            background: linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%);
            padding: 40px 24px;
            text-align: center;
            color: white;
        }}
        
        .logo {{
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 12px;
            letter-spacing: -0.5px;
        }}
        
        .header-subtitle {{
            font-size: 14px;
            opacity: 0.95;
            font-weight: 400;
        }}
        
        /* MAIN CONTENT */
        .content {{
            padding: 40px 24px;
        }}
        
        .greeting {{
            font-size: 22px;
            font-weight: 600;
            margin-bottom: 16px;
            color: #1f2937;
        }}
        
        .intro-text {{
            font-size: 15px;
            color: #4b5563;
            margin-bottom: 32px;
            line-height: 1.7;
        }}
        
        /* GIF SECTION */
        .gif-section {{
            margin: 32px 0;
            text-align: center;
        }}
        
        .gif-section img {{
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }}
        
        /* TABS SHOWCASE */
        .tabs-section {{
            margin: 40px 0;
        }}
        
        .tabs-title {{
            font-size: 16px;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 20px;
            text-align: center;
        }}
        
        .tabs-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 12px;
            margin-bottom: 12px;
        }}
        
        .tab-card {{
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 16px;
            text-align: center;
            background-color: #f9fafb;
            transition: all 0.2s ease;
        }}
        
        .tab-card:hover {{
            border-color: #8B5CF6;
            background-color: #faf5ff;
        }}
        
        .tab-icon {{
            font-size: 24px;
            margin-bottom: 8px;
        }}
        
        .tab-name {{
            font-size: 13px;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 4px;
        }}
        
        .tab-desc {{
            font-size: 12px;
            color: #6b7280;
            line-height: 1.4;
        }}
        
        /* THREE COLUMN SECTION */
        .value-section {{
            margin: 40px 0;
            padding: 24px;
            background-color: #f9fafb;
            border-radius: 8px;
            border-left: 4px solid #8B5CF6;
        }}
        
        .value-title {{
            font-size: 14px;
            font-weight: 600;
            color: #8B5CF6;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 16px;
        }}
        
        .value-items {{
            display: grid;
            gap: 12px;
        }}
        
        .value-item {{
            display: flex;
            gap: 12px;
            font-size: 14px;
            color: #374151;
        }}
        
        .value-icon {{
            flex-shrink: 0;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #8B5CF6;
            font-weight: 600;
        }}
        
        /* CTA SECTION */
        .cta-section {{
            margin: 40px 0;
            text-align: center;
        }}
        
        .cta-button {{
            display: inline-block;
            background: linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%);
            color: white;
            padding: 16px 40px;
            border-radius: 6px;
            text-decoration: none;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.2s ease;
            border: none;
            cursor: pointer;
        }}
        
        .cta-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(139, 92, 246, 0.3);
        }}
        
        /* STATS SECTION */
        .stats-section {{
            background: linear-gradient(135deg, #f0f4ff 0%, #fef3f8 100%);
            padding: 24px;
            border-radius: 8px;
            margin: 40px 0;
        }}
        
        .stats-title {{
            font-size: 14px;
            font-weight: 600;
            color: #1f2937;
            margin-bottom: 16px;
            text-align: center;
        }}
        
        .stat {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid rgba(139, 92, 246, 0.1);
            font-size: 14px;
        }}
        
        .stat:last-child {{
            border-bottom: none;
        }}
        
        .stat-label {{
            color: #4b5563;
        }}
        
        .stat-value {{
            font-weight: 600;
            color: #8B5CF6;
            font-size: 15px;
        }}
        
        /* FOOTER */
        .footer {{
            background-color: #f9fafb;
            padding: 24px;
            border-top: 1px solid #e5e7eb;
            text-align: center;
            font-size: 12px;
            color: #6b7280;
        }}
        
        .footer-links {{
            margin-top: 12px;
        }}
        
        .footer-links a {{
            color: #8B5CF6;
            text-decoration: none;
            margin: 0 8px;
        }}
        
        /* RESPONSIVE */
        @media (max-width: 480px) {{
            .content {{
                padding: 24px 16px;
            }}
            
            .greeting {{
                font-size: 18px;
            }}
            
            .tabs-grid {{
                grid-template-columns: 1fr;
                gap: 8px;
            }}
            
            .cta-button {{
                padding: 14px 32px;
                font-size: 15px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- HEADER -->
        <div class="header">
            <div class="logo">Mentora</div>
            <div class="header-subtitle">Your Learning Map is Ready</div>
        </div>
        
        <!-- MAIN CONTENT -->
        <div class="content">
            <div class="greeting">Hi {greeting_name}! 👋</div>
            
            <div class="intro-text">
                You've just joined Mentora. Here's what you need to know: your personal <strong>learning map is already built</strong> — the system has created a study schedule tailored to your profile that actually works.
                <br><br>
                This isn't just another study app. It combines adaptive tests, medical terminology learning, English reading, and virtual patient scenarios — all in one place. The system picks the right difficulty level for you, tracks your progress, and shows exactly what's improving.
            </div>
            
            {gif_section}
            
            <!-- TABS SHOWCASE -->
            <div class="tabs-section">
                <div class="tabs-title">Here's what you'll find inside:</div>
                <div class="tabs-grid">
                    <div class="tab-card">
                        <div class="tab-icon">🎯</div>
                        <div class="tab-name">Daily Plan</div>
                        <div class="tab-desc">Personalized tasks</div>
                    </div>
                    <div class="tab-card">
                        <div class="tab-icon">🧪</div>
                        <div class="tab-name">IRT Tests</div>
                        <div class="tab-desc">Adaptive testing</div>
                    </div>
                    <div class="tab-card">
                        <div class="tab-icon">🇳🇱</div>
                        <div class="tab-name">Dutch Terms</div>
                        <div class="tab-desc">Medical terminology</div>
                    </div>
                    <div class="tab-card">
                        <div class="tab-icon">📖</div>
                        <div class="tab-name">English Reading</div>
                        <div class="tab-desc">Reading passages</div>
                    </div>
                    <div class="tab-card">
                        <div class="tab-icon">👨‍⚕️</div>
                        <div class="tab-name">Virtual Patients</div>
                        <div class="tab-desc">Clinical scenarios</div>
                    </div>
                    <div class="tab-card">
                        <div class="tab-icon">📈</div>
                        <div class="tab-name">Progress</div>
                        <div class="tab-desc">Charts & achievements</div>
                    </div>
                </div>
            </div>
            
            <!-- VALUE PROPOSITION -->
            <div class="value-section">
                <div class="value-title">Why This Works</div>
                <div class="value-items">
                    <div class="value-item">
                        <div class="value-icon">✓</div>
                        <div>The system picks questions at your exact level — not boring, not too hard</div>
                    </div>
                    <div class="value-item">
                        <div class="value-icon">✓</div>
                        <div>See your progress every day — points, streaks, badges, achievements</div>
                    </div>
                    <div class="value-item">
                        <div class="value-icon">✓</div>
                        <div>Everything's organized by subject — no guessing what to study</div>
                    </div>
                </div>
            </div>
            
            <!-- STATS -->
            <div class="stats-section">
                <div class="stats-title">Average Results Over 3 Months</div>
                <div class="stat">
                    <span class="stat-label">📝 Questions answered</span>
                    <span class="stat-value">1,200+</span>
                </div>
                <div class="stat">
                    <span class="stat-label">🧠 Terms learned</span>
                    <span class="stat-value">250+</span>
                </div>
                <div class="stat">
                    <span class="stat-label">👨‍⚕️ Virtual patients</span>
                    <span class="stat-value">8+</span>
                </div>
                <div class="stat">
                    <span class="stat-label">🔥 Consecutive study days</span>
                    <span class="stat-value">42+</span>
                </div>
            </div>
            
            <!-- CTA -->
            <div class="cta-section">
                <a href="{cta_url}" class="cta-button">Open Your Learning Map</a>
            </div>
            
            <!-- PS -->
            <div style="margin-top: 32px; padding: 16px; background-color: #fef3f8; border-radius: 6px; font-size: 14px; color: #4b5563; border-left: 3px solid #8B5CF6;">
                <strong>P.S.</strong> Try it right now — it'll take 15 minutes to see how it works. All features are available for you.
            </div>
        </div>
        
        <!-- FOOTER -->
        <div class="footer">
            <p>Mentora — Platform for BIG Exam Preparation in the Netherlands</p>
            <p style="margin-top: 12px; color: #9ca3af;">© 2025 Mentora. All rights reserved.</p>
        </div>
    </div>
</body>
</html>'''

def generate_email_template(greeting_name, main_title, main_subtitle, intro_text,
                           value_prop_title, value_prop_items, cta_text, cta_url,
                           motivation_title, motivation_text):
    """Генерирует HTML шаблон email на основе переданных данных"""
    
    # Формируем список преимуществ
    value_prop_html = ''
    if value_prop_items:
        for item in value_prop_items:
            if item and str(item).strip():
                value_prop_html += f'<li style="margin-bottom: 10px;">{str(item).strip()}</li>'
    
    # Если нет элементов, добавляем дефолтные
    if not value_prop_html:
        value_prop_html = '''
        <li style="margin-bottom: 10px;"><strong style="color: #1d4ed8;">Персонализированный подход</strong> — система адаптируется под ваш уровень</li>
        <li style="margin-bottom: 10px;"><strong style="color: #1d4ed8;">Экономия времени</strong> — четкий план действий каждый день</li>
        <li style="margin-bottom: 10px;"><strong style="color: #1d4ed8;">Отслеживание прогресса</strong> — видите свой рост в реальном времени</li>
        <li style="margin-bottom: 0;"><strong style="color: #1d4ed8;">Гибкость</strong> — учитесь в своем темпе, когда удобно</li>
        '''
    
    return f'''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{main_title}</title>
</head>
<body style="margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; background-color: #f5f7fa; line-height: 1.6;">
    
    <!-- Email Container -->
    <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="background-color: #f5f7fa; padding: 40px 20px;">
        <tr>
            <td align="center">
                
                <!-- Main Content Card -->
                <table role="presentation" width="600" cellpadding="0" cellspacing="0" style="background: #ffffff; border-radius: 20px; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08); overflow: hidden; max-width: 600px;">
                    
                    <!-- Header with Gradient -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%); padding: 40px 40px 30px 40px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 32px; font-weight: 700; letter-spacing: -0.5px;">
                                {main_title}
                            </h1>
                            <p style="margin: 16px 0 0 0; color: rgba(255, 255, 255, 0.95); font-size: 18px; font-weight: 400;">
                                {main_subtitle}
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Main Content -->
                    <tr>
                        <td style="padding: 40px;">
                            
                            <!-- Personal Greeting -->
                            <p style="margin: 0 0 20px 0; color: #1a202c; font-size: 18px; font-weight: 600; line-height: 1.7;">
                                Привет, {greeting_name}!
                            </p>
                            
                            <p style="margin: 0 0 24px 0; color: #64748b; font-size: 16px; line-height: 1.7;">
                                {intro_text if intro_text else 'Подготовка к экзамену BI-toets — это важный шаг в вашей карьере. Мы создали <strong style="color: #1d4ed8;">Карту Обучения MENTORA</strong> — ваш персональный помощник, который сделает этот путь эффективным и структурированным.'}
                            </p>
                            
                            <!-- Value Proposition -->
                            <div style="background: linear-gradient(135deg, rgba(29, 78, 216, 0.1) 0%, rgba(50, 163, 154, 0.1) 100%); border-radius: 16px; padding: 24px; margin: 24px 0; border-left: 4px solid #1d4ed8;">
                                <h3 style="margin: 0 0 12px 0; color: #1a202c; font-size: 20px; font-weight: 700;">
                                    {value_prop_title}
                                </h3>
                                <ul style="margin: 0; padding-left: 24px; color: #64748b; font-size: 15px; line-height: 1.8;">
                                    {value_prop_html}
                                </ul>
                            </div>
                            
                            <!-- Main CTA Button -->
                            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" style="margin: 30px 0 40px 0;">
                                <tr>
                                    <td align="center">
                                        <a href="{cta_url}" 
                                           style="display: inline-block; background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%); color: #ffffff; text-decoration: none; padding: 18px 48px; border-radius: 12px; font-weight: 600; font-size: 18px; box-shadow: 0 4px 16px rgba(29, 78, 216, 0.3); transition: transform 0.2s;">
                                            {cta_text}
                                        </a>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Motivation Section -->
                            <div style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%); border-radius: 16px; padding: 28px; margin: 30px 0; text-align: center;">
                                <h3 style="margin: 0 0 16px 0; color: #1a202c; font-size: 20px; font-weight: 700;">
                                    {motivation_title}
                                </h3>
                                <p style="margin: 0; color: #64748b; font-size: 16px; line-height: 1.7;">
                                    {motivation_text if motivation_text else 'Не нужно сразу проходить все модули. Начните с <strong style="color: #1d4ed8;">15-20 минут в день</strong> — этого достаточно, чтобы поддерживать регулярность и видеть прогресс.'}
                                </p>
                            </div>
                            
                            <!-- Help & Support -->
                            <div style="border-top: 1px solid #e2e8f0; padding-top: 24px; margin-top: 30px; text-align: center;">
                                <p style="margin: 0 0 12px 0; color: #94a3b8; font-size: 14px;">
                                    💡 <strong style="color: #64748b;">Совет:</strong> При первом входе вы увидите интерактивный тур, 
                                    который поможет быстро освоиться с платформой.
                                </p>
                                <p style="margin: 0; color: #94a3b8; font-size: 14px;">
                                    Возникли вопросы? Напишите нам на 
                                    <a href="mailto:support@mentora.nl" style="color: #1d4ed8; text-decoration: none; font-weight: 500;">support@mentora.nl</a>
                                </p>
                            </div>
                            
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background: #f8fafc; padding: 30px 40px; text-align: center; border-top: 1px solid #e2e8f0;">
                            <p style="margin: 0 0 12px 0; color: #64748b; font-size: 14px;">
                                <strong style="color: #1a202c;">MENTORA</strong> - Ваш путь к успешной сдаче экзамена BI-toets
                            </p>
                            <p style="margin: 0; color: #94a3b8; font-size: 12px;">
                                © 2025 MENTORA. Все права защищены.
                            </p>
                            <p style="margin: 16px 0 0 0; color: #94a3b8; font-size: 12px;">
                                <a href="#" style="color: #94a3b8; text-decoration: underline;">Отписаться от рассылки</a>
                            </p>
                        </td>
                    </tr>
                    
                </table>
                
            </td>
        </tr>
    </table>
    
</body>
</html>'''

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
            from utils.resend_email_service import send_email_via_resend
            import time
            
            sent_count = 0
            failed_count = 0
            
            # Resend API лимит: 2 запроса в секунду, добавляем задержку 0.6 сек между запросами
            delay_between_emails = 0.6  # 600 мс для надежности
            
            for idx, recipient_email in enumerate(recipients):
                try:
                    # Добавляем задержку перед каждым запросом (кроме первого)
                    if idx > 0:
                        time.sleep(delay_between_emails)
                    
                    # Генерируем HTML контент
                    html_content = render_template(
                        f'admin/communication/email_templates/{template_type}.html',
                        additional_data=additional_data,
                        recipient_email=recipient_email,
                        current_user=current_user
                    )
                    
                    # Отправляем через Resend API
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
            
            # Генерация токена подтверждения email
            confirmation_token = user.generate_email_confirmation_token()
            
            # Сохранение в базу данных
            db.session.add(user)
            db.session.commit()
            
            # Отправка email с приглашением
            try:
                from utils.email_service import send_invitation_with_password
                email_sent = send_invitation_with_password(user, temp_password, confirmation_token)
                
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


# ========================================
# EMAIL TEMPLATE MANAGEMENT ROUTES
# ========================================

@communication_bp.route('/templates')
@login_required
@admin_required
def templates():
    """List all email templates"""
    try:
        # Get all templates with usage statistics
        templates = EmailTemplate.query.filter_by(is_active=True).order_by(EmailTemplate.created_at.desc()).all()
        
        # Add usage count for each template
        for template in templates:
            template.usage_count = template.sent_count
        
        return render_template('admin/communication/templates.html', templates=templates)
        
    except Exception as e:
        current_app.logger.error(f"Error loading templates: {str(e)}")
        flash('Ошибка загрузки шаблонов', 'error')
        return redirect(url_for('communication.hub'))

@communication_bp.route('/templates/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_template():
    """Create new email template"""
    if request.method == 'POST':
        try:
            # Get form data
            name = request.form.get('name', '').strip()
            subject = request.form.get('subject', '').strip()
            email_type = request.form.get('email_type', '').strip()
            description = request.form.get('description', '').strip()
            message = request.form.get('message', '').strip()
            action_url = request.form.get('action_url', '').strip()
            action_text = request.form.get('action_text', '').strip()
            
            # Validation
            if not name or not subject or not email_type or not message:
                flash('Заполните все обязательные поля', 'error')
                return redirect(url_for('communication.create_template'))
            
            # Create template
            template = EmailTemplate(
                name=name,
                subject=subject,
                template_type=email_type,
                html_content=message,
                text_content=message,  # Use same content for text version
                variables=json.dumps({
                    'description': description,
                    'action_url': action_url,
                    'action_text': action_text
                }),
                is_active=True,
                is_system=False
            )
            
            db.session.add(template)
            db.session.commit()
            
            flash('Шаблон успешно создан!', 'success')
            return redirect(url_for('communication.templates'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creating template: {str(e)}")
            flash(f'Ошибка создания шаблона: {str(e)}', 'error')
            return redirect(url_for('communication.create_template'))
    
    # GET request - show form
    return render_template('admin/communication/create_template.html')

@communication_bp.route('/templates/<int:template_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_template(template_id):
    """Edit email template"""
    template = EmailTemplate.query.get_or_404(template_id)
    
    if request.method == 'POST':
        try:
            # Get form data
            template.name = request.form.get('name', '').strip()
            template.subject = request.form.get('subject', '').strip()
            template.template_type = request.form.get('email_type', '').strip()
            template.html_content = request.form.get('message', '').strip()
            template.text_content = template.html_content  # Use same content for text version
            
            # Parse variables
            description = request.form.get('description', '').strip()
            action_url = request.form.get('action_url', '').strip()
            action_text = request.form.get('action_text', '').strip()
            
            template.variables = json.dumps({
                'description': description,
                'action_url': action_url,
                'action_text': action_text
            })
            
            template.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            flash('Шаблон успешно обновлен!', 'success')
            return redirect(url_for('communication.templates'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating template: {str(e)}")
            flash(f'Ошибка обновления шаблона: {str(e)}', 'error')
            return redirect(url_for('communication.edit_template', template_id=template_id))
    
    # GET request - show form with template data
    try:
        variables = json.loads(template.variables) if template.variables else {}
    except:
        variables = {}
    
    return render_template('admin/communication/edit_template.html', 
                         template=template,
                         description=variables.get('description', ''),
                         action_url=variables.get('action_url', ''),
                         action_text=variables.get('action_text', ''))

@communication_bp.route('/templates/<int:template_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_template(template_id):
    """Delete email template"""
    try:
        template = EmailTemplate.query.get_or_404(template_id)
        
        # Don't allow deletion of system templates
        if template.is_system:
            flash('Системные шаблоны нельзя удалять', 'error')
            return redirect(url_for('communication.templates'))
        
        # Soft delete - mark as inactive
        template.is_active = False
        template.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Шаблон успешно удален!'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting template: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@communication_bp.route('/templates/<int:template_id>/duplicate', methods=['POST'])
@login_required
@admin_required
def duplicate_template(template_id):
    """Duplicate email template"""
    try:
        original_template = EmailTemplate.query.get_or_404(template_id)
        
        # Create duplicate
        new_template = EmailTemplate(
            name=f"{original_template.name} (копия)",
            subject=original_template.subject,
            template_type=original_template.template_type,
            html_content=original_template.html_content,
            text_content=original_template.text_content,
            variables=original_template.variables,
            is_active=True,
            is_system=False,
            sent_count=0,
            last_sent_at=None
        )
        
        db.session.add(new_template)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Шаблон успешно скопирован!'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error duplicating template: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ========================================
# EMAIL CLIENT ROUTES (POP/IMAP)
# ========================================

@communication_bp.route('/inbox')
@login_required
@admin_required
def inbox():
    """Email inbox - view incoming emails"""
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        category = request.args.get('category', 'all')
        status = request.args.get('status', 'all')  # all, unread, important, spam
        source = request.args.get('source', 'all')  # all, info, support
        
        # Build query
        query = IncomingEmail.query.filter_by(is_deleted=False)
        
        # Apply filters
        if category != 'all':
            query = query.filter_by(category=category)
        
        if source != 'all':
            query = query.filter_by(source_account=source)
        
        if status == 'unread':
            query = query.filter_by(is_read=False)
        elif status == 'important':
            query = query.filter_by(is_important=True)
        elif status == 'spam':
            query = query.filter_by(is_spam=True)
        
        # Order by date (newest first)
        query = query.order_by(IncomingEmail.date_received.desc())
        
        # Paginate
        emails = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        # Get statistics
        stats = {
            'total': IncomingEmail.query.filter_by(is_deleted=False).count(),
            'unread': IncomingEmail.query.filter_by(is_deleted=False, is_read=False).count(),
            'important': IncomingEmail.query.filter_by(is_deleted=False, is_important=True).count(),
            'spam': IncomingEmail.query.filter_by(is_deleted=False, is_spam=True).count(),
            'info': IncomingEmail.query.filter_by(is_deleted=False, source_account='info').count(),
            'support': IncomingEmail.query.filter_by(is_deleted=False, source_account='support').count()
        }
        
        return render_template('admin/communication/inbox.html', 
                             emails=emails, 
                             stats=stats,
                             current_category=category,
                             current_status=status,
                             current_source=source)
        
    except Exception as e:
        current_app.logger.error(f"Error loading inbox: {str(e)}")
        flash('Ошибка загрузки почты', 'error')
        return redirect(url_for('communication.hub'))

@communication_bp.route('/inbox/<int:email_id>')
@login_required
@admin_required
def view_email(email_id):
    """View individual email"""
    try:
        email = IncomingEmail.query.get_or_404(email_id)
        
        # Mark as read
        if not email.is_read:
            email.is_read = True
            email.updated_at = datetime.utcnow()
            db.session.commit()
        
        return render_template('admin/communication/view_email.html', email=email)
        
    except Exception as e:
        current_app.logger.error(f"Error viewing email: {str(e)}")
        flash('Ошибка загрузки письма', 'error')
        return redirect(url_for('communication.inbox'))

@communication_bp.route('/inbox/fetch', methods=['POST'])
@login_required
@admin_required
def fetch_emails():
    """Fetch new emails from POP/IMAP server"""
    try:
        from utils.email_client import EmailClient, get_multiple_email_configs
        
        # Get configurations for all email accounts
        configs = get_multiple_email_configs()
        total_saved = 0
        
        for account_key, config in configs.items():
            try:
                current_app.logger.info(f"Fetching emails from {config['name']} ({config['email']})")
                
                client = EmailClient(config)
                
                # Try IMAP first, then POP
                emails_data = client.fetch_emails_imap(limit=50)
                if not emails_data:
                    emails_data = client.fetch_emails_pop(limit=50)
                
                client.disconnect()
                
                if not emails_data:
                    current_app.logger.info(f"No emails found in {config['name']} account")
                    continue
                
                # Save emails to database
                saved_count = 0
                for email_data in emails_data:
                    try:
                        # Check if email already exists
                        existing = IncomingEmail.query.filter_by(
                            message_id=email_data['message_id']
                        ).first()
                        
                        if existing:
                            continue
                        
                        # Create new email record
                        email = IncomingEmail(
                            message_id=email_data['message_id'],
                            subject=email_data['subject'],
                            sender_email=email_data['sender_email'],
                            sender_name=email_data['sender_name'],
                            recipient_email=email_data['recipient_email'],
                            source_account=account_key,  # Add source account
                            html_content=email_data['html_content'],
                            text_content=email_data['text_content'],
                            date_received=email_data['date_received'],
                            size_bytes=email_data['size_bytes'],
                            has_attachments=email_data['has_attachments'],
                            attachment_count=email_data['attachment_count']
                        )
                        
                        db.session.add(email)
                        saved_count += 1
                        
                    except Exception as e:
                        current_app.logger.error(f"Error saving email from {config['name']}: {str(e)}")
                        continue
                
                total_saved += saved_count
                current_app.logger.info(f"Saved {saved_count} emails from {config['name']} account")
                
            except Exception as e:
                current_app.logger.error(f"Error fetching emails from {config['name']}: {str(e)}")
                continue
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Fetched {total_saved} new emails from all accounts',
            'count': total_saved
        })
        
    except Exception as e:
        current_app.logger.error(f"Error fetching emails: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@communication_bp.route('/inbox/<int:email_id>/mark-important', methods=['POST'])
@login_required
@admin_required
def mark_important(email_id):
    """Mark email as important/unimportant"""
    try:
        email = IncomingEmail.query.get_or_404(email_id)
        email.is_important = not email.is_important
        email.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'is_important': email.is_important
        })
        
    except Exception as e:
        current_app.logger.error(f"Error marking email important: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@communication_bp.route('/inbox/<int:email_id>/mark-spam', methods=['POST'])
@login_required
@admin_required
def mark_spam(email_id):
    """Mark email as spam/not spam"""
    try:
        email = IncomingEmail.query.get_or_404(email_id)
        email.is_spam = not email.is_spam
        email.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'is_spam': email.is_spam
        })
        
    except Exception as e:
        current_app.logger.error(f"Error marking email spam: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@communication_bp.route('/inbox/<int:email_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_email(email_id):
    """Delete email (soft delete)"""
    try:
        email = IncomingEmail.query.get_or_404(email_id)
        email.is_deleted = True
        email.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Email deleted'})
        
    except Exception as e:
        current_app.logger.error(f"Error deleting email: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@communication_bp.route('/inbox/<int:email_id>/reply', methods=['GET', 'POST'])
@login_required
@admin_required
def reply_email(email_id):
    """Reply to email"""
    try:
        email = IncomingEmail.query.get_or_404(email_id)
        
        if request.method == 'POST':
            # Get reply data
            reply_subject = request.form.get('subject', '').strip()
            reply_content = request.form.get('content', '').strip()
            
            if not reply_subject or not reply_content:
                flash('Заполните все поля', 'error')
                return redirect(url_for('communication.reply_email', email_id=email_id))
            
            # Send reply (using existing email service)
            try:
                from utils.email_service import send_email_confirmation
                
                # Create reply content
                reply_html = f"""
                <div style="border-left: 3px solid #ccc; padding-left: 15px; margin: 20px 0;">
                    <p><strong>От:</strong> {email.sender_name or email.sender_email}</p>
                    <p><strong>Дата:</strong> {email.date_received.strftime('%d.%m.%Y %H:%M')}</p>
                    <p><strong>Тема:</strong> {email.subject}</p>
                    <div style="background: #f5f5f5; padding: 10px; margin: 10px 0;">
                        {email.html_content or email.text_content}
                    </div>
                </div>
                
                <div style="margin: 20px 0;">
                    {reply_content}
                </div>
                """
                
                # Send email
                success = send_email_confirmation(
                    recipient_email=email.sender_email,
                    subject=reply_subject,
                    html_content=reply_html
                )
                
                if success:
                    # Mark as replied
                    email.is_replied = True
                    email.reply_sent_at = datetime.utcnow()
                    email.updated_at = datetime.utcnow()
                    db.session.commit()
                    
                    flash('Ответ отправлен успешно!', 'success')
                    return redirect(url_for('communication.view_email', email_id=email_id))
                else:
                    flash('Ошибка отправки ответа', 'error')
                    
            except Exception as e:
                current_app.logger.error(f"Error sending reply: {str(e)}")
                flash(f'Ошибка отправки ответа: {str(e)}', 'error')
        
        # GET request - show reply form
        reply_subject = f"Re: {email.subject}" if not email.subject.startswith('Re:') else email.subject
        
        return render_template('admin/communication/reply_email.html', 
                             email=email, 
                             reply_subject=reply_subject)
        
    except Exception as e:
        current_app.logger.error(f"Error replying to email: {str(e)}")
        flash('Ошибка при ответе на письмо', 'error')
        return redirect(url_for('communication.inbox'))
