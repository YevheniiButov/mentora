"""
Communication Hub Routes
Центр коммуникации для управления перепиской с клиентами
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from utils.decorators import admin_required
from models import db, User, Contact
# Models are now in main models.py
from datetime import datetime, timedelta
import json

communication_bp = Blueprint('communication', __name__, url_prefix='/admin/communication')

@communication_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Главная страница Communication Hub"""
    
    # Статистика за последние 30 дней
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    
    stats = {
        'total_emails_sent': CommunicationHistory.query.filter(
            CommunicationHistory.sent_at >= thirty_days_ago
        ).count(),
        'emails_to_users': CommunicationHistory.query.filter(
            CommunicationHistory.recipient_type == 'user',
            CommunicationHistory.sent_at >= thirty_days_ago
        ).count(),
        'emails_to_contacts': CommunicationHistory.query.filter(
            CommunicationHistory.recipient_type == 'contact',
            CommunicationHistory.sent_at >= thirty_days_ago
        ).count(),
        'active_campaigns': CommunicationCampaign.query.filter(
            CommunicationCampaign.status.in_(['scheduled', 'running'])
        ).count(),
        'templates_count': EmailTemplate.query.filter_by(is_active=True).count()
    }
    
    # Последние отправленные письма
    recent_emails = CommunicationHistory.query.order_by(
        CommunicationHistory.sent_at.desc()
    ).limit(10).all()
    
    # Активные кампании
    active_campaigns = CommunicationCampaign.query.filter(
        CommunicationCampaign.status.in_(['scheduled', 'running'])
    ).order_by(CommunicationCampaign.scheduled_at.desc()).limit(5).all()
    
    # Популярные шаблоны
    popular_templates = EmailTemplate.query.filter_by(is_active=True).order_by(
        EmailTemplate.usage_count.desc()
    ).limit(5).all()
    
    return render_template('admin/communication/dashboard.html',
                         stats=stats,
                         recent_emails=recent_emails,
                         active_campaigns=active_campaigns,
                         popular_templates=popular_templates)

@communication_bp.route('/history')
@login_required
@admin_required
def history():
    """История всех отправленных писем"""
    
    # Фильтры
    page = request.args.get('page', 1, type=int)
    recipient_type = request.args.get('type', 'all')
    email_type = request.args.get('email_type', 'all')
    status = request.args.get('status', 'all')
    search = request.args.get('search', '')
    
    # Построение запроса
    query = CommunicationHistory.query
    
    if recipient_type != 'all':
        query = query.filter(CommunicationHistory.recipient_type == recipient_type)
    
    if email_type != 'all':
        query = query.filter(CommunicationHistory.email_type == email_type)
    
    if status != 'all':
        query = query.filter(CommunicationHistory.status == status)
    
    if search:
        query = query.filter(
            or_(
                CommunicationHistory.recipient_email.contains(search),
                CommunicationHistory.subject.contains(search),
                CommunicationHistory.recipient_name.contains(search)
            )
        )
    
    # Пагинация
    emails = query.order_by(CommunicationHistory.sent_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/communication/history.html',
                         emails=emails,
                         recipient_type=recipient_type,
                         email_type=email_type,
                         status=status,
                         search=search)

@communication_bp.route('/templates')
@login_required
@admin_required
def templates():
    """Управление шаблонами email"""
    
    templates = EmailTemplate.query.filter_by(is_active=True).order_by(
        EmailTemplate.updated_at.desc()
    ).all()
    
    return render_template('admin/communication/templates.html', templates=templates)

@communication_bp.route('/templates/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_template():
    """Создание нового шаблона"""
    
    if request.method == 'POST':
        try:
            template = EmailTemplate(
                name=request.form.get('name'),
                description=request.form.get('description'),
                subject=request.form.get('subject'),
                message=request.form.get('message'),
                email_type=request.form.get('email_type'),
                action_url=request.form.get('action_url'),
                action_text=request.form.get('action_text'),
                created_by=current_user.id
            )
            
            db.session.add(template)
            db.session.commit()
            
            flash('Шаблон создан успешно', 'success')
            return redirect(url_for('communication.templates'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка создания шаблона: {str(e)}', 'error')
    
    return render_template('admin/communication/create_template.html')

@communication_bp.route('/templates/<int:template_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_template(template_id):
    """Редактирование шаблона"""
    
    template = EmailTemplate.query.get_or_404(template_id)
    
    if request.method == 'POST':
        try:
            template.name = request.form.get('name')
            template.description = request.form.get('description')
            template.subject = request.form.get('subject')
            template.message = request.form.get('message')
            template.email_type = request.form.get('email_type')
            template.action_url = request.form.get('action_url')
            template.action_text = request.form.get('action_text')
            template.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            flash('Шаблон обновлен успешно', 'success')
            return redirect(url_for('communication.templates'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка обновления шаблона: {str(e)}', 'error')
    
    return render_template('admin/communication/edit_template.html', template=template)

@communication_bp.route('/campaigns')
@login_required
@admin_required
def campaigns():
    """Управление кампаниями рассылок"""
    
    campaigns = CommunicationCampaign.query.order_by(
        CommunicationCampaign.created_at.desc()
    ).all()
    
    return render_template('admin/communication/campaigns.html', campaigns=campaigns)

@communication_bp.route('/campaigns/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_campaign():
    """Создание новой кампании"""
    
    if request.method == 'POST':
        try:
            campaign = CommunicationCampaign(
                name=request.form.get('name'),
                description=request.form.get('description'),
                email_type=request.form.get('email_type'),
                subject=request.form.get('subject'),
                message=request.form.get('message'),
                action_url=request.form.get('action_url'),
                action_text=request.form.get('action_text'),
                target_type=request.form.get('target_type'),
                target_filters=json.loads(request.form.get('target_filters', '{}')),
                created_by=current_user.id
            )
            
            db.session.add(campaign)
            db.session.commit()
            
            flash('Кампания создана успешно', 'success')
            return redirect(url_for('communication.campaigns'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Ошибка создания кампании: {str(e)}', 'error')
    
    return render_template('admin/communication/create_campaign.html')

@communication_bp.route('/send-email', methods=['POST'])
@login_required
@admin_required
def send_email():
    """Отправка email через Communication Hub"""
    
    try:
        data = request.get_json()
        recipient_type = data.get('recipient_type')  # 'user' или 'contact'
        recipient_id = data.get('recipient_id')
        subject = data.get('subject')
        message = data.get('message')
        email_type = data.get('email_type', 'custom')
        action_url = data.get('action_url')
        action_text = data.get('action_text')
        
        if not all([recipient_type, recipient_id, subject, message]):
            return jsonify({'success': False, 'error': 'Missing required fields'})
        
        # Получаем получателя
        if recipient_type == 'user':
            recipient = User.query.get(recipient_id)
            recipient_email = recipient.email
            recipient_name = recipient.get_display_name()
        elif recipient_type == 'contact':
            recipient = Contact.query.get(recipient_id)
            recipient_email = recipient.email
            recipient_name = recipient.full_name
        else:
            return jsonify({'success': False, 'error': 'Invalid recipient type'})
        
        if not recipient:
            return jsonify({'success': False, 'error': 'Recipient not found'})
        
        # Отправляем email
        from utils.admin_email_service import send_admin_email
        
        email_sent = send_admin_email(
            recipient, 
            subject, 
            message, 
            email_type,
            action_url=action_url,
            action_text=action_text
        )
        
        if email_sent:
            # Сохраняем в историю
            history = CommunicationHistory(
                recipient_type=recipient_type,
                recipient_id=recipient_id,
                recipient_email=recipient_email,
                recipient_name=recipient_name,
                sender_id=current_user.id,
                sender_name=current_user.get_display_name(),
                subject=subject,
                message=message,
                email_type=email_type,
                action_url=action_url,
                action_text=action_text,
                template_used=f"{email_type}_template"
            )
            
            db.session.add(history)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Email sent successfully'})
        else:
            return jsonify({'success': False, 'error': 'Failed to send email'})
            
    except Exception as e:
        current_app.logger.error(f"Error sending email: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@communication_bp.route('/api/recipients')
@login_required
@admin_required
def get_recipients():
    """API для получения списка получателей"""
    
    recipient_type = request.args.get('type', 'all')
    search = request.args.get('search', '')
    
    recipients = []
    
    if recipient_type in ['all', 'users']:
        users_query = User.query
        if search:
            users_query = users_query.filter(
                or_(
                    User.email.contains(search),
                    User.first_name.contains(search),
                    User.last_name.contains(search)
                )
            )
        
        users = users_query.limit(50).all()
        for user in users:
            recipients.append({
                'id': user.id,
                'type': 'user',
                'email': user.email,
                'name': user.get_display_name(),
                'status': 'Active' if user.is_active else 'Inactive'
            })
    
    if recipient_type in ['all', 'contacts']:
        contacts_query = Contact.query
        if search:
            contacts_query = contacts_query.filter(
                or_(
                    Contact.email.contains(search),
                    Contact.first_name.contains(search),
                    Contact.last_name.contains(search)
                )
            )
        
        contacts = contacts_query.limit(50).all()
        for contact in contacts:
            recipients.append({
                'id': contact.id,
                'type': 'contact',
                'email': contact.email,
                'name': contact.full_name,
                'status': contact.contact_status.title()
            })
    
    return jsonify({'recipients': recipients})

@communication_bp.route('/api/templates')
@login_required
@admin_required
def get_templates():
    """API для получения шаблонов"""
    
    email_type = request.args.get('type', 'all')
    
    query = EmailTemplate.query.filter_by(is_active=True)
    if email_type != 'all':
        query = query.filter(EmailTemplate.email_type == email_type)
    
    templates = query.all()
    
    return jsonify({'templates': [template.to_dict() for template in templates]})
