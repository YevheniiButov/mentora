"""
CRM роуты для админ-панели Mentora
Управление контактами, профессиями и CRM системой
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from utils.decorators import admin_required
from models import db, User
from admin_models import Profession, Contact, ContactActivity, CountryAnalytics, DeviceAnalytics, ProfessionAnalytics
from datetime import datetime, timedelta, date
import json
from sqlalchemy import func, and_, or_, desc, asc
import logging

# Создаем blueprint для CRM
crm_bp = Blueprint('crm', __name__, url_prefix='/admin/crm')

@crm_bp.route('/')
@login_required
@admin_required
def dashboard():
    """CRM Dashboard с воронкой продаж и ключевыми метриками"""
    try:
        # Воронка продаж
        leads = Contact.query.filter_by(contact_status='lead').count()
        prospects = Contact.query.filter_by(contact_status='prospect').count()
        active_contacts = Contact.query.filter_by(contact_status='active').count()
        converted = Contact.query.filter_by(contact_status='converted').count()
        
        # Ключевые метрики
        total_contacts = Contact.query.count()
        new_contacts_today = Contact.query.filter(
            func.date(Contact.created_at) == date.today()
        ).count()
        
        # Конверсия
        conversion_rate = 0
        if total_contacts > 0:
            conversion_rate = (converted / total_contacts) * 100
        
        # Недавние контакты
        recent_contacts = Contact.query.order_by(Contact.created_at.desc()).limit(10).all()
        
        # Задачи для последующего контакта
        overdue_followups = Contact.query.filter(
            Contact.next_followup_date < datetime.utcnow(),
            Contact.contact_status.in_(['lead', 'prospect'])
        ).count()
        
        # Источники лидов
        lead_sources = db.session.query(
            Contact.lead_source,
            func.count(Contact.id).label('count')
        ).group_by(Contact.lead_source).all()
        
        # Распределение по профессиям
        profession_stats = db.session.query(
            Profession.name,
            func.count(Contact.id).label('count')
        ).join(Contact, Profession.id == Contact.profession_id).group_by(Profession.name).all()
        
        # Активность за последние 30 дней
        activities_last_30_days = ContactActivity.query.filter(
            ContactActivity.created_at >= datetime.utcnow() - timedelta(days=30)
        ).count()
        
        # Топ активные пользователи
        top_active_users = db.session.query(
            User.email,
            func.count(ContactActivity.id).label('activity_count')
        ).join(ContactActivity, User.id == ContactActivity.user_id).group_by(User.id).order_by(
            desc('activity_count')
        ).limit(5).all()
        
        return render_template('admin/crm/dashboard.html',
                             leads=leads,
                             prospects=prospects,
                             active_contacts=active_contacts,
                             converted=converted,
                             total_contacts=total_contacts,
                             new_contacts_today=new_contacts_today,
                             conversion_rate=conversion_rate,
                             recent_contacts=recent_contacts,
                             overdue_followups=overdue_followups,
                             lead_sources=lead_sources,
                             profession_stats=profession_stats,
                             activities_last_30_days=activities_last_30_days,
                             top_active_users=top_active_users)
    
    except Exception as e:
        current_app.logger.error(f"Ошибка в CRM dashboard: {str(e)}")
        flash(f'Ошибка загрузки CRM дашборда: {str(e)}', 'error')
        return render_template('admin/crm/dashboard.html',
                             leads=0, prospects=0, active_contacts=0, converted=0,
                             total_contacts=0, new_contacts_today=0, conversion_rate=0,
                             recent_contacts=[], overdue_followups=0, lead_sources=[],
                             profession_stats=[], activities_last_30_days=0, top_active_users=[])

@crm_bp.route('/contacts')
@login_required
@admin_required
def contacts():
    """Управление контактами с фильтрами и поиском"""
    try:
        # Получаем параметры фильтрации
        status_filter = request.args.get('status', 'all')
        profession_filter = request.args.get('profession', 'all')
        country_filter = request.args.get('country', 'all')
        search_query = request.args.get('search', '').strip()
        sort_by = request.args.get('sort', 'created_at')
        sort_order = request.args.get('order', 'desc')
        
        # Строим запрос
        query = Contact.query
        
        # Фильтры
        if status_filter != 'all':
            query = query.filter_by(contact_status=status_filter)
        
        if profession_filter != 'all':
            query = query.filter_by(profession_id=profession_filter)
        
        if country_filter != 'all':
            query = query.filter_by(country=country_filter)
        
        if search_query:
            query = query.filter(
                or_(
                    Contact.full_name.ilike(f'%{search_query}%'),
                    Contact.email.ilike(f'%{search_query}%'),
                    Contact.phone.ilike(f'%{search_query}%'),
                    Contact.current_job_title.ilike(f'%{search_query}%')
                )
            )
        
        # Сортировка
        if sort_order == 'desc':
            query = query.order_by(desc(getattr(Contact, sort_by)))
        else:
            query = query.order_by(asc(getattr(Contact, sort_by)))
        
        # Пагинация
        page = request.args.get('page', 1, type=int)
        per_page = 20
        contacts = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Получаем данные для фильтров
        professions = Profession.query.filter_by(is_active=True).all()
        countries = db.session.query(Contact.country).distinct().all()
        countries = [country[0] for country in countries if country[0]]
        
        return render_template('admin/crm/contacts.html',
                             contacts=contacts,
                             professions=professions,
                             countries=countries,
                             status_filter=status_filter,
                             profession_filter=profession_filter,
                             country_filter=country_filter,
                             search_query=search_query,
                             sort_by=sort_by,
                             sort_order=sort_order)
    
    except Exception as e:
        current_app.logger.error(f"Ошибка в управлении контактами: {str(e)}")
        flash(f'Ошибка загрузки контактов: {str(e)}', 'error')
        return render_template('admin/crm/contacts.html',
                             contacts=None, professions=[], countries=[],
                             status_filter='all', profession_filter='all',
                             country_filter='all', search_query='',
                             sort_by='created_at', sort_order='desc')

@crm_bp.route('/contacts/<int:contact_id>')
@login_required
@admin_required
def contact_detail(contact_id):
    """Детальная информация о контакте"""
    try:
        contact = Contact.query.get_or_404(contact_id)
        
        # Получаем активность контакта
        activities = ContactActivity.query.filter_by(contact_id=contact_id).order_by(
            ContactActivity.created_at.desc()
        ).limit(20).all()
        
        # Статистика активности
        total_activities = ContactActivity.query.filter_by(contact_id=contact_id).count()
        activities_this_month = ContactActivity.query.filter(
            ContactActivity.contact_id == contact_id,
            ContactActivity.created_at >= datetime.utcnow().replace(day=1)
        ).count()
        
        # Следующие задачи
        upcoming_tasks = ContactActivity.query.filter(
            ContactActivity.contact_id == contact_id,
            ContactActivity.status == 'planned',
            ContactActivity.scheduled_at > datetime.utcnow()
        ).order_by(ContactActivity.scheduled_at).limit(5).all()
        
        return render_template('admin/crm/contact_detail.html',
                             contact=contact,
                             activities=activities,
                             total_activities=total_activities,
                             activities_this_month=activities_this_month,
                             upcoming_tasks=upcoming_tasks)
    
    except Exception as e:
        current_app.logger.error(f"Ошибка загрузки контакта {contact_id}: {str(e)}")
        flash(f'Ошибка загрузки контакта: {str(e)}', 'error')
        return redirect(url_for('crm.contacts'))

@crm_bp.route('/contacts/<int:contact_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def contact_edit(contact_id):
    """Редактирование контакта"""
    try:
        contact = Contact.query.get_or_404(contact_id)
        
        if request.method == 'POST':
            # Обновляем данные контакта
            contact.full_name = request.form.get('full_name', contact.full_name)
            contact.email = request.form.get('email', contact.email)
            contact.phone = request.form.get('phone', contact.phone)
            contact.country = request.form.get('country', contact.country)
            contact.city = request.form.get('city', contact.city)
            contact.profession_id = request.form.get('profession_id') or None
            contact.contact_status = request.form.get('contact_status', contact.contact_status)
            contact.lead_score = int(request.form.get('lead_score', contact.lead_score))
            contact.notes = request.form.get('notes', contact.notes)
            
            # Обновляем дату следующего контакта
            next_followup = request.form.get('next_followup_date')
            if next_followup:
                contact.next_followup_date = datetime.strptime(next_followup, '%Y-%m-%dT%H:%M')
            
            contact.updated_at = datetime.utcnow()
            
            db.session.commit()
            
            # Создаем запись активности
            activity = ContactActivity(
                contact_id=contact.id,
                user_id=current_user.id,
                activity_type='note',
                subject='Контакт обновлен',
                description=f'Контакт обновлен пользователем {current_user.email}',
                status='completed',
                completed_at=datetime.utcnow()
            )
            db.session.add(activity)
            db.session.commit()
            
            flash('Контакт успешно обновлен', 'success')
            return redirect(url_for('crm.contact_detail', contact_id=contact.id))
        
        # Получаем профессии для выбора
        professions = Profession.query.filter_by(is_active=True).all()
        
        return render_template('admin/crm/contact_edit.html',
                             contact=contact,
                             professions=professions)
    
    except Exception as e:
        current_app.logger.error(f"Ошибка редактирования контакта {contact_id}: {str(e)}")
        flash(f'Ошибка редактирования контакта: {str(e)}', 'error')
        return redirect(url_for('crm.contacts'))

@crm_bp.route('/contacts/create', methods=['GET', 'POST'])
@login_required
@admin_required
def contact_create():
    """Создание нового контакта"""
    try:
        if request.method == 'POST':
            # Создаем новый контакт
            contact = Contact(
                full_name=request.form.get('full_name'),
                email=request.form.get('email'),
                phone=request.form.get('phone'),
                country=request.form.get('country'),
                city=request.form.get('city'),
                profession_id=request.form.get('profession_id') or None,
                contact_status=request.form.get('contact_status', 'lead'),
                lead_source=request.form.get('lead_source'),
                notes=request.form.get('notes'),
                assigned_to=current_user.id
            )
            
            db.session.add(contact)
            db.session.commit()
            
            # Создаем запись активности
            activity = ContactActivity(
                contact_id=contact.id,
                user_id=current_user.id,
                activity_type='note',
                subject='Контакт создан',
                description=f'Новый контакт создан пользователем {current_user.email}',
                status='completed',
                completed_at=datetime.utcnow()
            )
            db.session.add(activity)
            db.session.commit()
            
            flash('Контакт успешно создан', 'success')
            return redirect(url_for('crm.contact_detail', contact_id=contact.id))
        
        # Получаем профессии для выбора
        professions = Profession.query.filter_by(is_active=True).all()
        
        return render_template('admin/crm/contact_create.html',
                             professions=professions)
    
    except Exception as e:
        current_app.logger.error(f"Ошибка создания контакта: {str(e)}")
        flash(f'Ошибка создания контакта: {str(e)}', 'error')
        return redirect(url_for('crm.contacts'))

@crm_bp.route('/professions')
@login_required
@admin_required
def professions():
    """Управление профессиями"""
    try:
        # Получаем параметры фильтрации
        category_filter = request.args.get('category', 'all')
        search_query = request.args.get('search', '').strip()
        
        # Строим запрос
        query = Profession.query
        
        if category_filter != 'all':
            query = query.filter_by(category=category_filter)
        
        if search_query:
            query = query.filter(
                or_(
                    Profession.name.ilike(f'%{search_query}%'),
                    Profession.name_nl.ilike(f'%{search_query}%'),
                    Profession.code.ilike(f'%{search_query}%')
                )
            )
        
        query = query.order_by(Profession.name)
        
        # Пагинация
        page = request.args.get('page', 1, type=int)
        per_page = 20
        professions = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Получаем категории для фильтра
        categories = db.session.query(Profession.category).distinct().all()
        categories = [cat[0] for cat in categories if cat[0]]
        
        return render_template('admin/crm/professions.html',
                             professions=professions,
                             categories=categories,
                             category_filter=category_filter,
                             search_query=search_query)
    
    except Exception as e:
        current_app.logger.error(f"Ошибка в управлении профессиями: {str(e)}")
        flash(f'Ошибка загрузки профессий: {str(e)}', 'error')
        return render_template('admin/crm/professions.html',
                             professions=None, categories=[],
                             category_filter='all', search_query='')

@crm_bp.route('/activities')
@login_required
@admin_required
def activities():
    """Управление активностью контактов"""
    try:
        # Получаем параметры фильтрации
        activity_type = request.args.get('type', 'all')
        status_filter = request.args.get('status', 'all')
        user_filter = request.args.get('user', 'all')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        
        # Строим запрос
        query = ContactActivity.query
        
        if activity_type != 'all':
            query = query.filter_by(activity_type=activity_type)
        
        if status_filter != 'all':
            query = query.filter_by(status=status_filter)
        
        if user_filter != 'all':
            query = query.filter_by(user_id=user_filter)
        
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
                query = query.filter(ContactActivity.created_at >= date_from_obj)
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
                query = query.filter(ContactActivity.created_at <= date_to_obj)
            except ValueError:
                pass
        
        query = query.order_by(ContactActivity.created_at.desc())
        
        # Пагинация
        page = request.args.get('page', 1, type=int)
        per_page = 50
        activities = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Получаем данные для фильтров
        activity_types = db.session.query(ContactActivity.activity_type).distinct().all()
        activity_types = [t[0] for t in activity_types if t[0]]
        
        users = User.query.filter_by(role='admin').all()
        
        return render_template('admin/crm/activities.html',
                             activities=activities,
                             activity_types=activity_types,
                             users=users,
                             activity_type=activity_type,
                             status_filter=status_filter,
                             user_filter=user_filter,
                             date_from=date_from,
                             date_to=date_to)
    
    except Exception as e:
        current_app.logger.error(f"Ошибка в управлении активностью: {str(e)}")
        flash(f'Ошибка загрузки активности: {str(e)}', 'error')
        return render_template('admin/crm/activities.html',
                             activities=None, activity_types=[], users=[],
                             activity_type='all', status_filter='all',
                             user_filter='all', date_from='', date_to='')

# ========================================
# API ENDPOINTS
# ========================================

@crm_bp.route('/api/stats')
@login_required
@admin_required
def api_stats():
    """API для получения статистики CRM"""
    try:
        # Основная статистика
        stats = {
            'total_contacts': Contact.query.count(),
            'new_contacts_today': Contact.query.filter(
                func.date(Contact.created_at) == date.today()
            ).count(),
            'new_contacts_this_week': Contact.query.filter(
                Contact.created_at >= datetime.utcnow() - timedelta(days=7)
            ).count(),
            'new_contacts_this_month': Contact.query.filter(
                Contact.created_at >= datetime.utcnow() - timedelta(days=30)
            ).count(),
            'leads': Contact.query.filter_by(contact_status='lead').count(),
            'prospects': Contact.query.filter_by(contact_status='prospect').count(),
            'active_contacts': Contact.query.filter_by(contact_status='active').count(),
            'converted': Contact.query.filter_by(contact_status='converted').count(),
            'overdue_followups': Contact.query.filter(
                Contact.next_followup_date < datetime.utcnow(),
                Contact.contact_status.in_(['lead', 'prospect'])
            ).count(),
            'activities_today': ContactActivity.query.filter(
                func.date(ContactActivity.created_at) == date.today()
            ).count(),
            'activities_this_week': ContactActivity.query.filter(
                ContactActivity.created_at >= datetime.utcnow() - timedelta(days=7)
            ).count()
        }
        
        # Конверсия
        if stats['total_contacts'] > 0:
            stats['conversion_rate'] = (stats['converted'] / stats['total_contacts']) * 100
        else:
            stats['conversion_rate'] = 0
        
        return jsonify(stats)
    
    except Exception as e:
        current_app.logger.error(f"Ошибка API статистики CRM: {str(e)}")
        return jsonify({'error': str(e)}), 500

@crm_bp.route('/api/contacts/export')
@login_required
@admin_required
def api_contacts_export():
    """API для экспорта контактов"""
    try:
        format_type = request.args.get('format', 'json')
        
        # Получаем все контакты
        contacts = Contact.query.all()
        
        if format_type == 'json':
            return jsonify([contact.to_dict() for contact in contacts])
        
        elif format_type == 'csv':
            import csv
            import io
            
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Заголовки
            writer.writerow([
                'ID', 'Full Name', 'Email', 'Phone', 'Country', 'City',
                'Profession', 'Status', 'Lead Source', 'Created At'
            ])
            
            # Данные
            for contact in contacts:
                writer.writerow([
                    contact.id,
                    contact.full_name,
                    contact.email,
                    contact.phone or '',
                    contact.country,
                    contact.city or '',
                    contact.profession.name if contact.profession else '',
                    contact.contact_status,
                    contact.lead_source or '',
                    contact.created_at.strftime('%Y-%m-%d %H:%M:%S')
                ])
            
            output.seek(0)
            return output.getvalue(), 200, {'Content-Type': 'text/csv'}
        
        else:
            return jsonify({'error': 'Неподдерживаемый формат'}), 400
    
    except Exception as e:
        current_app.logger.error(f"Ошибка экспорта контактов: {str(e)}")
        return jsonify({'error': str(e)}), 500

@crm_bp.route('/api/activities/create', methods=['POST'])
@login_required
@admin_required
def api_activity_create():
    """API для создания активности"""
    try:
        data = request.get_json()
        
        activity = ContactActivity(
            contact_id=data.get('contact_id'),
            user_id=current_user.id,
            activity_type=data.get('activity_type'),
            activity_subtype=data.get('activity_subtype'),
            subject=data.get('subject'),
            description=data.get('description'),
            duration=data.get('duration'),
            outcome=data.get('outcome'),
            next_action=data.get('next_action'),
            next_action_date=datetime.fromisoformat(data.get('next_action_date')) if data.get('next_action_date') else None,
            status=data.get('status', 'completed'),
            priority=data.get('priority', 'normal'),
            scheduled_at=datetime.fromisoformat(data.get('scheduled_at')) if data.get('scheduled_at') else None,
            completed_at=datetime.utcnow() if data.get('status') == 'completed' else None
        )
        
        db.session.add(activity)
        
        # Обновляем дату последнего контакта
        contact = Contact.query.get(data.get('contact_id'))
        if contact:
            contact.last_contact_date = datetime.utcnow()
            contact.total_contacts += 1
        
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Активность создана успешно',
            'activity_id': activity.id
        })
    
    except Exception as e:
        current_app.logger.error(f"Ошибка создания активности: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@crm_bp.route('/api/contacts/<int:contact_id>/update-status', methods=['POST'])
@login_required
@admin_required
def api_contact_update_status(contact_id):
    """API для обновления статуса контакта"""
    try:
        contact = Contact.query.get_or_404(contact_id)
        data = request.get_json()
        
        old_status = contact.contact_status
        new_status = data.get('status')
        
        contact.contact_status = new_status
        contact.updated_at = datetime.utcnow()
        
        # Создаем запись активности
        activity = ContactActivity(
            contact_id=contact.id,
            user_id=current_user.id,
            activity_type='note',
            subject='Изменение статуса',
            description=f'Статус изменен с "{old_status}" на "{new_status}"',
            status='completed',
            completed_at=datetime.utcnow()
        )
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({
            'status': 'success',
            'message': 'Статус контакта обновлен'
        })
    
    except Exception as e:
        current_app.logger.error(f"Ошибка обновления статуса контакта: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
