"""
Аналитические роуты для админ-панели Mentora
Детальная аналитика по странам, устройствам, профессиям
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from utils.decorators import admin_required
from models import db, User, WebsiteVisit, PageView, UserSession
from admin_models import CountryAnalytics, DeviceAnalytics, ProfessionAnalytics, Contact, Profession
from datetime import datetime, timedelta, date
import json
from sqlalchemy import func, and_, or_, desc, asc
import logging

# Создаем blueprint для аналитики
analytics_bp = Blueprint('analytics', __name__, url_prefix='/admin/analytics')

@analytics_bp.route('/')
@login_required
@admin_required
def dashboard():
    """Главная страница аналитики с обзором"""
    try:
        # Общая статистика
        total_users = User.query.count()
        total_contacts = Contact.query.count()
        total_professions = Profession.query.count()
        
        # Статистика за последние 30 дней
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        new_users_30d = User.query.filter(User.created_at >= thirty_days_ago).count()
        new_contacts_30d = Contact.query.filter(Contact.created_at >= thirty_days_ago).count()
        
        # Статистика посещений
        total_visits = WebsiteVisit.query.count()
        visits_30d = WebsiteVisit.query.filter(WebsiteVisit.visit_date >= thirty_days_ago).count()
        
        # Топ страны по контактам
        top_countries = db.session.query(
            Contact.country,
            func.count(Contact.id).label('count')
        ).group_by(Contact.country).order_by(desc('count')).limit(10).all()
        
        # Топ профессии
        top_professions = db.session.query(
            Profession.name,
            func.count(Contact.id).label('count')
        ).join(Contact, Profession.id == Contact.profession_id).group_by(Profession.name).order_by(
            desc('count')
        ).limit(10).all()
        
        # Статистика по устройствам
        device_stats = db.session.query(
            DeviceAnalytics.device_category,
            func.sum(DeviceAnalytics.users_count).label('total_users')
        ).group_by(DeviceAnalytics.device_category).all()
        
        # Конверсия по странам
        country_conversion = db.session.query(
            CountryAnalytics.country_name,
            CountryAnalytics.conversion_rate,
            CountryAnalytics.total_users
        ).order_by(desc(CountryAnalytics.conversion_rate)).limit(10).all()
        
        return render_template('admin/analytics/dashboard.html',
                             total_users=total_users,
                             total_contacts=total_contacts,
                             total_professions=total_professions,
                             new_users_30d=new_users_30d,
                             new_contacts_30d=new_contacts_30d,
                             total_visits=total_visits,
                             visits_30d=visits_30d,
                             top_countries=top_countries,
                             top_professions=top_professions,
                             device_stats=device_stats,
                             country_conversion=country_conversion)
    
    except Exception as e:
        current_app.logger.error(f"Ошибка в аналитическом дашборде: {str(e)}")
        flash(f'Ошибка загрузки аналитики: {str(e)}', 'error')
        return render_template('admin/analytics/dashboard.html',
                             total_users=0, total_contacts=0, total_professions=0,
                             new_users_30d=0, new_contacts_30d=0,
                             total_visits=0, visits_30d=0,
                             top_countries=[], top_professions=[],
                             device_stats=[], country_conversion=[])

@analytics_bp.route('/countries')
@login_required
@admin_required
def countries():
    """Детальная аналитика по странам"""
    try:
        # Получаем параметры фильтрации
        search_query = request.args.get('search', '').strip()
        sort_by = request.args.get('sort', 'total_users')
        sort_order = request.args.get('order', 'desc')
        
        # Строим запрос
        query = CountryAnalytics.query
        
        if search_query:
            query = query.filter(
                or_(
                    CountryAnalytics.country_name.ilike(f'%{search_query}%'),
                    CountryAnalytics.country_code.ilike(f'%{search_query}%')
                )
            )
        
        # Сортировка
        if sort_order == 'desc':
            query = query.order_by(desc(getattr(CountryAnalytics, sort_by)))
        else:
            query = query.order_by(asc(getattr(CountryAnalytics, sort_by)))
        
        # Пагинация
        page = request.args.get('page', 1, type=int)
        per_page = 20
        countries = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return render_template('admin/analytics/countries.html',
                             countries=countries,
                             search_query=search_query,
                             sort_by=sort_by,
                             sort_order=sort_order)
    
    except Exception as e:
        current_app.logger.error(f"Ошибка в аналитике по странам: {str(e)}")
        flash(f'Ошибка загрузки аналитики по странам: {str(e)}', 'error')
        return render_template('admin/analytics/countries.html',
                             countries=None, search_query='',
                             sort_by='total_users', sort_order='desc')

@analytics_bp.route('/devices')
@login_required
@admin_required
def devices():
    """Детальная аналитика по устройствам и браузерам"""
    try:
        # Получаем параметры фильтрации
        device_category = request.args.get('category', 'all')
        browser_filter = request.args.get('browser', 'all')
        os_filter = request.args.get('os', 'all')
        search_query = request.args.get('search', '').strip()
        
        # Строим запрос
        query = DeviceAnalytics.query
        
        if device_category != 'all':
            query = query.filter_by(device_category=device_category)
        
        if browser_filter != 'all':
            query = query.filter_by(browser=browser_filter)
        
        if os_filter != 'all':
            query = query.filter_by(os=os_filter)
        
        if search_query:
            query = query.filter(
                or_(
                    DeviceAnalytics.device_type.ilike(f'%{search_query}%'),
                    DeviceAnalytics.browser.ilike(f'%{search_query}%'),
                    DeviceAnalytics.os.ilike(f'%{search_query}%')
                )
            )
        
        query = query.order_by(desc(DeviceAnalytics.users_count))
        
        # Пагинация
        page = request.args.get('page', 1, type=int)
        per_page = 20
        devices = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Получаем данные для фильтров
        categories = db.session.query(DeviceAnalytics.device_category).distinct().all()
        categories = [cat[0] for cat in categories if cat[0]]
        
        browsers = db.session.query(DeviceAnalytics.browser).distinct().all()
        browsers = [browser[0] for browser in browsers if browser[0]]
        
        operating_systems = db.session.query(DeviceAnalytics.os).distinct().all()
        operating_systems = [os[0] for os in operating_systems if os[0]]
        
        return render_template('admin/analytics/devices.html',
                             devices=devices,
                             categories=categories,
                             browsers=browsers,
                             operating_systems=operating_systems,
                             device_category=device_category,
                             browser_filter=browser_filter,
                             os_filter=os_filter,
                             search_query=search_query)
    
    except Exception as e:
        current_app.logger.error(f"Ошибка в аналитике по устройствам: {str(e)}")
        flash(f'Ошибка загрузки аналитики по устройствам: {str(e)}', 'error')
        return render_template('admin/analytics/devices.html',
                             devices=None, categories=[], browsers=[],
                             operating_systems=[], device_category='all',
                             browser_filter='all', os_filter='all',
                             search_query='')

@analytics_bp.route('/professions')
@login_required
@admin_required
def professions():
    """Детальная аналитика по профессиям"""
    try:
        # Получаем параметры фильтрации
        category_filter = request.args.get('category', 'all')
        search_query = request.args.get('search', '').strip()
        sort_by = request.args.get('sort', 'total_registrations')
        sort_order = request.args.get('order', 'desc')
        
        # Строим запрос
        query = ProfessionAnalytics.query.join(Profession)
        
        if category_filter != 'all':
            query = query.filter(Profession.category == category_filter)
        
        if search_query:
            query = query.filter(
                or_(
                    Profession.name.ilike(f'%{search_query}%'),
                    Profession.name_nl.ilike(f'%{search_query}%'),
                    Profession.code.ilike(f'%{search_query}%')
                )
            )
        
        # Сортировка
        if sort_order == 'desc':
            query = query.order_by(desc(getattr(ProfessionAnalytics, sort_by)))
        else:
            query = query.order_by(asc(getattr(ProfessionAnalytics, sort_by)))
        
        # Пагинация
        page = request.args.get('page', 1, type=int)
        per_page = 20
        professions = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Получаем категории для фильтра
        categories = db.session.query(Profession.category).distinct().all()
        categories = [cat[0] for cat in categories if cat[0]]
        
        return render_template('admin/analytics/professions.html',
                             professions=professions,
                             categories=categories,
                             category_filter=category_filter,
                             search_query=search_query,
                             sort_by=sort_by,
                             sort_order=sort_order)
    
    except Exception as e:
        current_app.logger.error(f"Ошибка в аналитике по профессиям: {str(e)}")
        flash(f'Ошибка загрузки аналитики по профессиям: {str(e)}', 'error')
        return render_template('admin/analytics/professions.html',
                             professions=None, categories=[],
                             category_filter='all', search_query='',
                             sort_by='total_registrations', sort_order='desc')

@analytics_bp.route('/reports')
@login_required
@admin_required
def reports():
    """Отчеты и экспорт данных"""
    try:
        # Получаем параметры отчета
        report_type = request.args.get('type', 'summary')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        format_type = request.args.get('format', 'json')
        
        # Определяем даты
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            except ValueError:
                date_from_obj = datetime.utcnow() - timedelta(days=30)
        else:
            date_from_obj = datetime.utcnow() - timedelta(days=30)
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            except ValueError:
                date_to_obj = datetime.utcnow()
        else:
            date_to_obj = datetime.utcnow()
        
        # Генерируем отчет
        if report_type == 'summary':
            report_data = generate_summary_report(date_from_obj, date_to_obj)
        elif report_type == 'countries':
            report_data = generate_countries_report(date_from_obj, date_to_obj)
        elif report_type == 'professions':
            report_data = generate_professions_report(date_from_obj, date_to_obj)
        elif report_type == 'devices':
            report_data = generate_devices_report(date_from_obj, date_to_obj)
        else:
            report_data = generate_summary_report(date_from_obj, date_to_obj)
        
        # Экспорт в нужном формате
        if format_type == 'json':
            return jsonify(report_data)
        elif format_type == 'csv':
            return export_to_csv(report_data, report_type)
        else:
            return render_template('admin/analytics/reports.html',
                                 report_data=report_data,
                                 report_type=report_type,
                                 date_from=date_from,
                                 date_to=date_to,
                                 format_type=format_type)
    
    except Exception as e:
        current_app.logger.error(f"Ошибка в отчетах: {str(e)}")
        flash(f'Ошибка генерации отчета: {str(e)}', 'error')
        return render_template('admin/analytics/reports.html',
                             report_data={}, report_type='summary',
                             date_from='', date_to='', format_type='json')

# ========================================
# API ENDPOINTS
# ========================================

@analytics_bp.route('/api/countries')
@login_required
@admin_required
def api_countries():
    """API для получения данных по странам"""
    try:
        countries = CountryAnalytics.query.all()
        return jsonify([country.to_dict() for country in countries])
    
    except Exception as e:
        current_app.logger.error(f"Ошибка API стран: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/api/devices')
@login_required
@admin_required
def api_devices():
    """API для получения данных по устройствам"""
    try:
        devices = DeviceAnalytics.query.all()
        return jsonify([device.to_dict() for device in devices])
    
    except Exception as e:
        current_app.logger.error(f"Ошибка API устройств: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/api/professions')
@login_required
@admin_required
def api_professions():
    """API для получения данных по профессиям"""
    try:
        professions = ProfessionAnalytics.query.join(Profession).all()
        return jsonify([prof.to_dict() for prof in professions])
    
    except Exception as e:
        current_app.logger.error(f"Ошибка API профессий: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/api/charts/overview')
@login_required
@admin_required
def api_charts_overview():
    """API для данных графиков обзора"""
    try:
        # Данные для графика пользователей по месяцам
        monthly_users = db.session.query(
            func.date_trunc('month', User.created_at).label('month'),
            func.count(User.id).label('count')
        ).group_by('month').order_by('month').all()
        
        # Данные для графика контактов по месяцам
        monthly_contacts = db.session.query(
            func.date_trunc('month', Contact.created_at).label('month'),
            func.count(Contact.id).label('count')
        ).group_by('month').order_by('month').all()
        
        # Данные для графика по странам
        country_data = db.session.query(
            Contact.country,
            func.count(Contact.id).label('count')
        ).group_by(Contact.country).order_by(desc('count')).limit(10).all()
        
        # Данные для графика по профессиям
        profession_data = db.session.query(
            Profession.name,
            func.count(Contact.id).label('count')
        ).join(Contact, Profession.id == Contact.profession_id).group_by(Profession.name).order_by(
            desc('count')
        ).limit(10).all()
        
        return jsonify({
            'monthly_users': [{'month': str(m.month), 'count': m.count} for m in monthly_users],
            'monthly_contacts': [{'month': str(m.month), 'count': m.count} for m in monthly_contacts],
            'countries': [{'country': c.country, 'count': c.count} for c in country_data],
            'professions': [{'profession': p.name, 'count': p.count} for p in profession_data]
        })
    
    except Exception as e:
        current_app.logger.error(f"Ошибка API графиков: {str(e)}")
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/api/export/<report_type>')
@login_required
@admin_required
def api_export(report_type):
    """API для экспорта данных"""
    try:
        format_type = request.args.get('format', 'json')
        date_from = request.args.get('date_from', '')
        date_to = request.args.get('date_to', '')
        
        # Определяем даты
        if date_from:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
        else:
            date_from_obj = datetime.utcnow() - timedelta(days=30)
        
        if date_to:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
        else:
            date_to_obj = datetime.utcnow()
        
        # Генерируем данные
        if report_type == 'countries':
            data = CountryAnalytics.query.all()
            data = [item.to_dict() for item in data]
        elif report_type == 'devices':
            data = DeviceAnalytics.query.all()
            data = [item.to_dict() for item in data]
        elif report_type == 'professions':
            data = ProfessionAnalytics.query.join(Profession).all()
            data = [item.to_dict() for item in data]
        else:
            return jsonify({'error': 'Неподдерживаемый тип отчета'}), 400
        
        # Экспорт
        if format_type == 'json':
            return jsonify(data)
        elif format_type == 'csv':
            return export_to_csv(data, report_type)
        else:
            return jsonify({'error': 'Неподдерживаемый формат'}), 400
    
    except Exception as e:
        current_app.logger.error(f"Ошибка экспорта {report_type}: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ========================================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# ========================================

def generate_summary_report(date_from, date_to):
    """Генерация сводного отчета"""
    try:
        # Общая статистика
        total_users = User.query.count()
        total_contacts = Contact.query.count()
        total_professions = Profession.query.count()
        
        # Статистика за период
        period_users = User.query.filter(
            User.created_at >= date_from,
            User.created_at <= date_to
        ).count()
        
        period_contacts = Contact.query.filter(
            Contact.created_at >= date_from,
            Contact.created_at <= date_to
        ).count()
        
        # Топ страны
        top_countries = db.session.query(
            Contact.country,
            func.count(Contact.id).label('count')
        ).filter(
            Contact.created_at >= date_from,
            Contact.created_at <= date_to
        ).group_by(Contact.country).order_by(desc('count')).limit(10).all()
        
        # Топ профессии
        top_professions = db.session.query(
            Profession.name,
            func.count(Contact.id).label('count')
        ).join(Contact, Profession.id == Contact.profession_id).filter(
            Contact.created_at >= date_from,
            Contact.created_at <= date_to
        ).group_by(Profession.name).order_by(desc('count')).limit(10).all()
        
        return {
            'period': {
                'from': date_from.isoformat(),
                'to': date_to.isoformat()
            },
            'summary': {
                'total_users': total_users,
                'total_contacts': total_contacts,
                'total_professions': total_professions,
                'period_users': period_users,
                'period_contacts': period_contacts
            },
            'top_countries': [{'country': c.country, 'count': c.count} for c in top_countries],
            'top_professions': [{'profession': p.name, 'count': p.count} for p in top_professions]
        }
    
    except Exception as e:
        current_app.logger.error(f"Ошибка генерации сводного отчета: {str(e)}")
        return {}

def generate_countries_report(date_from, date_to):
    """Генерация отчета по странам"""
    try:
        countries = CountryAnalytics.query.all()
        return [country.to_dict() for country in countries]
    
    except Exception as e:
        current_app.logger.error(f"Ошибка генерации отчета по странам: {str(e)}")
        return []

def generate_professions_report(date_from, date_to):
    """Генерация отчета по профессиям"""
    try:
        professions = ProfessionAnalytics.query.join(Profession).all()
        return [prof.to_dict() for prof in professions]
    
    except Exception as e:
        current_app.logger.error(f"Ошибка генерации отчета по профессиям: {str(e)}")
        return []

def generate_devices_report(date_from, date_to):
    """Генерация отчета по устройствам"""
    try:
        devices = DeviceAnalytics.query.all()
        return [device.to_dict() for device in devices]
    
    except Exception as e:
        current_app.logger.error(f"Ошибка генерации отчета по устройствам: {str(e)}")
        return []

def export_to_csv(data, report_type):
    """Экспорт данных в CSV формат"""
    try:
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        if not data:
            return "Нет данных для экспорта", 200, {'Content-Type': 'text/csv'}
        
        # Заголовки
        if isinstance(data, list) and len(data) > 0:
            headers = list(data[0].keys())
            writer.writerow(headers)
            
            # Данные
            for row in data:
                writer.writerow([row.get(header, '') for header in headers])
        
        output.seek(0)
        return output.getvalue(), 200, {'Content-Type': 'text/csv'}
    
    except Exception as e:
        current_app.logger.error(f"Ошибка экспорта в CSV: {str(e)}")
        return "Ошибка экспорта", 500, {'Content-Type': 'text/plain'}
