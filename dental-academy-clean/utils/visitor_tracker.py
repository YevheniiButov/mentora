#!/usr/bin/env python3
"""
Утилита для отслеживания посетителей страниц регистрации
"""

import hashlib
import json
from datetime import datetime, timedelta
from flask import request, session, current_app
from extensions import db
from models import RegistrationVisitor, RegistrationAnalytics

class VisitorTracker:
    """Класс для отслеживания посетителей регистрационных страниц"""
    
    @staticmethod
    def get_client_ip():
        """Получает IP адрес клиента"""
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        elif request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        else:
            return request.remote_addr or '127.0.0.1'
    
    @staticmethod
    def generate_session_id():
        """Генерирует уникальный ID сессии"""
        ip = VisitorTracker.get_client_ip()
        user_agent = request.headers.get('User-Agent', '')
        timestamp = datetime.now().isoformat()
        
        # Создаем хеш для уникальной идентификации сессии
        session_data = f"{ip}_{user_agent}_{timestamp}"
        return hashlib.md5(session_data.encode()).hexdigest()
    
    @staticmethod
    def track_page_visit(page_type, language=None):
        """Отслеживает посещение страницы регистрации"""
        try:
            # Проверяем, есть ли уже активная сессия для этого IP
            ip_address = VisitorTracker.get_client_ip()
            session_id = session.get('visitor_session_id')
            
            if not session_id:
                session_id = VisitorTracker.generate_session_id()
                session['visitor_session_id'] = session_id
            
            # Проверяем, не был ли уже записан этот визит
            existing_visit = RegistrationVisitor.query.filter_by(
                ip_address=ip_address,
                session_id=session_id,
                page_type=page_type,
                exit_time=None
            ).first()
            
            if existing_visit:
                # Обновляем время входа
                existing_visit.entry_time = datetime.utcnow()
                existing_visit.language = language
                existing_visit.referrer = request.headers.get('Referer')
            else:
                # Создаем новую запись
                visitor = RegistrationVisitor(
                    ip_address=ip_address,
                    session_id=session_id,
                    page_type=page_type,
                    entry_time=datetime.utcnow(),
                    user_agent=request.headers.get('User-Agent'),
                    referrer=request.headers.get('Referer'),
                    language=language
                )
                db.session.add(visitor)
            
            db.session.commit()
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error tracking page visit: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def track_email_entry(email, page_type):
        """Отслеживает ввод email адреса"""
        try:
            ip_address = VisitorTracker.get_client_ip()
            session_id = session.get('visitor_session_id')
            
            if not session_id:
                return False
            
            # Находим активную сессию
            visitor = RegistrationVisitor.query.filter_by(
                ip_address=ip_address,
                session_id=session_id,
                page_type=page_type,
                exit_time=None
            ).first()
            
            if visitor:
                visitor.email_entered = email
                visitor.email_entered_at = datetime.utcnow()
                db.session.commit()
                return True
            
            return False
            
        except Exception as e:
            current_app.logger.error(f"Error tracking email entry: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def track_form_start(page_type):
        """Отслеживает начало заполнения формы"""
        try:
            ip_address = VisitorTracker.get_client_ip()
            session_id = session.get('visitor_session_id')
            
            if not session_id:
                return False
            
            visitor = RegistrationVisitor.query.filter_by(
                ip_address=ip_address,
                session_id=session_id,
                page_type=page_type,
                exit_time=None
            ).first()
            
            if visitor:
                visitor.form_started = True
                db.session.commit()
                return True
            
            return False
            
        except Exception as e:
            current_app.logger.error(f"Error tracking form start: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def track_form_abandonment(page_type):
        """Отслеживает отказ от заполнения формы"""
        try:
            ip_address = VisitorTracker.get_client_ip()
            session_id = session.get('visitor_session_id')
            
            if not session_id:
                return False
            
            visitor = RegistrationVisitor.query.filter_by(
                ip_address=ip_address,
                session_id=session_id,
                page_type=page_type,
                exit_time=None
            ).first()
            
            if visitor and visitor.form_started and not visitor.registration_completed:
                visitor.form_abandoned = True
                visitor.exit_time = datetime.utcnow()
                
                # Вычисляем время на странице
                if visitor.entry_time:
                    time_diff = visitor.exit_time - visitor.entry_time
                    visitor.time_on_page = int(time_diff.total_seconds())
                
                db.session.commit()
                return True
            
            return False
            
        except Exception as e:
            current_app.logger.error(f"Error tracking form abandonment: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def track_registration_completion(page_type, user_id=None):
        """Отслеживает успешную регистрацию"""
        try:
            ip_address = VisitorTracker.get_client_ip()
            session_id = session.get('visitor_session_id')
            
            if not session_id:
                return False
            
            visitor = RegistrationVisitor.query.filter_by(
                ip_address=ip_address,
                session_id=session_id,
                page_type=page_type,
                exit_time=None
            ).first()
            
            if visitor:
                visitor.registration_completed = True
                visitor.exit_time = datetime.utcnow()
                visitor.user_id = user_id
                
                # Вычисляем время на странице
                if visitor.entry_time:
                    time_diff = visitor.exit_time - visitor.entry_time
                    visitor.time_on_page = int(time_diff.total_seconds())
                
                db.session.commit()
                return True
            
            return False
            
        except Exception as e:
            current_app.logger.error(f"Error tracking registration completion: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def track_page_exit(page_type):
        """Отслеживает выход со страницы"""
        try:
            ip_address = VisitorTracker.get_client_ip()
            session_id = session.get('visitor_session_id')
            
            if not session_id:
                return False
            
            visitor = RegistrationVisitor.query.filter_by(
                ip_address=ip_address,
                session_id=session_id,
                page_type=page_type,
                exit_time=None
            ).first()
            
            if visitor:
                visitor.exit_time = datetime.utcnow()
                
                # Вычисляем время на странице
                if visitor.entry_time:
                    time_diff = visitor.exit_time - visitor.entry_time
                    visitor.time_on_page = int(time_diff.total_seconds())
                
                db.session.commit()
                return True
            
            return False
            
        except Exception as e:
            current_app.logger.error(f"Error tracking page exit: {str(e)}")
            db.session.rollback()
            return False
    
    @staticmethod
    def get_analytics_summary(days=7):
        """Получает сводку аналитики за последние дни"""
        try:
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=days)
            
            # Агрегируем данные
            from sqlalchemy import func
            
            summary = db.session.query(
                RegistrationVisitor.page_type,
                func.count(RegistrationVisitor.id).label('total_visits'),
                func.count(func.distinct(RegistrationVisitor.ip_address)).label('unique_visitors'),
                func.count(RegistrationVisitor.email_entered).label('email_entries'),
                func.count(RegistrationVisitor.form_started).label('form_starts'),
                func.count(RegistrationVisitor.form_abandoned).label('form_abandonments'),
                func.count(RegistrationVisitor.registration_completed).label('successful_registrations')
            ).filter(
                RegistrationVisitor.entry_time >= start_date
            ).group_by(
                RegistrationVisitor.page_type
            ).all()
            
            return [
                {
                    'page_type': row.page_type,
                    'total_visits': row.total_visits,
                    'unique_visitors': row.unique_visitors,
                    'email_entries': row.email_entries,
                    'form_starts': row.form_starts,
                    'form_abandonments': row.form_abandonments,
                    'successful_registrations': row.successful_registrations,
                    'email_to_form_rate': (row.form_starts / row.email_entries * 100) if row.email_entries > 0 else 0,
                    'form_to_success_rate': (row.successful_registrations / row.form_starts * 100) if row.form_starts > 0 else 0
                }
                for row in summary
            ]
            
        except Exception as e:
            current_app.logger.error(f"Error getting analytics summary: {str(e)}")
            return []
