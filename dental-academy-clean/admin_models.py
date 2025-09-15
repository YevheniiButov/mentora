"""
Расширенные модели для админ-панели Mentora
CRM система, аналитика и управление контактами
"""

from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, and_, or_
import json

# Импортируем db из основного приложения
from models import db

class Profession(db.Model):
    """Модель профессий для медицинских работников"""
    __tablename__ = 'profession'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, comment='Название профессии на английском')
    name_nl = db.Column(db.String(100), nullable=True, comment='Название профессии на голландском')
    code = db.Column(db.String(20), unique=True, nullable=False, comment='Код профессии')
    category = db.Column(db.String(50), nullable=False, comment='Категория: medical, dental, pharmacy, nursing')
    
    # Требования для работы в Нидерландах
    big_exam_required = db.Column(db.Boolean, default=True, comment='Требуется ли экзамен BIG')
    dutch_language_required = db.Column(db.Boolean, default=True, comment='Требуется ли знание голландского')
    experience_required = db.Column(db.Integer, default=0, comment='Требуемый опыт работы (лет)')
    
    # Описание и требования
    description = db.Column(db.Text, nullable=True, comment='Описание профессии')
    requirements = db.Column(db.Text, nullable=True, comment='Требования в JSON формате')
    salary_range = db.Column(db.String(50), nullable=True, comment='Диапазон зарплат')
    
    # Статус
    is_active = db.Column(db.Boolean, default=True, comment='Активна ли профессия')
    is_popular = db.Column(db.Boolean, default=False, comment='Популярная профессия')
    
    # Временные метки
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    contacts = db.relationship('Contact', backref='profession', lazy='dynamic')
    analytics = db.relationship('ProfessionAnalytics', backref='profession', lazy='dynamic')
    
    def __repr__(self):
        return f'<Profession {self.code}: {self.name}>'
    
    def to_dict(self):
        """Преобразование в словарь для JSON"""
        return {
            'id': self.id,
            'name': self.name,
            'name_nl': self.name_nl,
            'code': self.code,
            'category': self.category,
            'big_exam_required': self.big_exam_required,
            'dutch_language_required': self.dutch_language_required,
            'experience_required': self.experience_required,
            'description': self.description,
            'requirements': self.requirements,
            'salary_range': self.salary_range,
            'is_active': self.is_active,
            'is_popular': self.is_popular,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @property
    def contacts_count(self):
        """Количество контактов в этой профессии"""
        return self.contacts.count()
    
    @property
    def active_contacts_count(self):
        """Количество активных контактов"""
        return self.contacts.filter_by(contact_status='active').count()

class Contact(db.Model):
    """Модель контактов для CRM системы"""
    __tablename__ = 'contact'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, comment='Связанный пользователь')
    
    # Основная информация
    full_name = db.Column(db.String(200), nullable=False, comment='Полное имя')
    email = db.Column(db.String(120), nullable=False, index=True, comment='Email адрес')
    phone = db.Column(db.String(20), nullable=True, comment='Телефон')
    date_of_birth = db.Column(db.Date, nullable=True, comment='Дата рождения')
    gender = db.Column(db.String(10), nullable=True, comment='Пол')
    
    # Адрес
    country = db.Column(db.String(100), nullable=False, comment='Страна')
    city = db.Column(db.String(100), nullable=True, comment='Город')
    address = db.Column(db.Text, nullable=True, comment='Адрес')
    postal_code = db.Column(db.String(20), nullable=True, comment='Почтовый индекс')
    
    # Профессиональная информация
    profession_id = db.Column(db.Integer, db.ForeignKey('profession.id'), nullable=True, comment='Профессия')
    current_job_title = db.Column(db.String(200), nullable=True, comment='Текущая должность')
    current_employer = db.Column(db.String(200), nullable=True, comment='Текущий работодатель')
    years_of_experience = db.Column(db.Integer, nullable=True, comment='Опыт работы (лет)')
    
    # Образование
    education_level = db.Column(db.String(100), nullable=True, comment='Уровень образования')
    university = db.Column(db.String(200), nullable=True, comment='Университет')
    graduation_year = db.Column(db.Integer, nullable=True, comment='Год окончания')
    
    # Языки
    dutch_level = db.Column(db.String(20), nullable=True, comment='Уровень голландского')
    english_level = db.Column(db.String(20), nullable=True, comment='Уровень английского')
    other_languages = db.Column(db.Text, nullable=True, comment='Другие языки в JSON')
    
    # CRM поля
    contact_status = db.Column(db.String(50), default='lead', comment='Статус: lead, prospect, active, inactive, converted')
    lead_source = db.Column(db.String(100), nullable=True, comment='Источник лида')
    lead_score = db.Column(db.Integer, default=0, comment='Оценка лида (0-100)')
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, comment='Назначен на пользователя')
    
    # Финансовая информация
    budget_range = db.Column(db.String(50), nullable=True, comment='Бюджет на обучение')
    payment_method = db.Column(db.String(50), nullable=True, comment='Способ оплаты')
    payment_status = db.Column(db.String(50), default='pending', comment='Статус оплаты')
    
    # Коммуникация
    preferred_contact_method = db.Column(db.String(50), default='email', comment='Предпочитаемый способ связи')
    preferred_contact_time = db.Column(db.String(50), nullable=True, comment='Предпочитаемое время связи')
    timezone = db.Column(db.String(50), nullable=True, comment='Часовой пояс')
    
    # Отслеживание активности
    last_contact_date = db.Column(db.DateTime, nullable=True, comment='Дата последнего контакта')
    next_followup_date = db.Column(db.DateTime, nullable=True, comment='Дата следующего контакта')
    total_contacts = db.Column(db.Integer, default=0, comment='Общее количество контактов')
    
    # Заметки и теги
    notes = db.Column(db.Text, nullable=True, comment='Заметки')
    tags = db.Column(db.Text, nullable=True, comment='Теги в JSON формате')
    custom_fields = db.Column(db.Text, nullable=True, comment='Пользовательские поля в JSON')
    
    # Аналитика
    registration_date = db.Column(db.DateTime, default=datetime.utcnow, comment='Дата регистрации')
    registration_source = db.Column(db.String(100), nullable=True, comment='Источник регистрации')
    first_visit_country = db.Column(db.String(100), nullable=True, comment='Страна первого визита')
    device_type = db.Column(db.String(50), nullable=True, comment='Тип устройства')
    browser = db.Column(db.String(50), nullable=True, comment='Браузер')
    
    # Временные метки
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    user = db.relationship('User', foreign_keys=[user_id], backref='contact_profile')
    assigned_user = db.relationship('User', foreign_keys=[assigned_to], backref='assigned_contacts')
    activities = db.relationship('ContactActivity', backref='contact', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Contact {self.full_name}: {self.email}>'
    
    def to_dict(self):
        """Преобразование в словарь для JSON"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'country': self.country,
            'city': self.city,
            'address': self.address,
            'postal_code': self.postal_code,
            'profession_id': self.profession_id,
            'profession_name': self.profession.name if self.profession else None,
            'current_job_title': self.current_job_title,
            'current_employer': self.current_employer,
            'years_of_experience': self.years_of_experience,
            'education_level': self.education_level,
            'university': self.university,
            'graduation_year': self.graduation_year,
            'dutch_level': self.dutch_level,
            'english_level': self.english_level,
            'other_languages': self.other_languages,
            'contact_status': self.contact_status,
            'lead_source': self.lead_source,
            'lead_score': self.lead_score,
            'assigned_to': self.assigned_to,
            'assigned_user_name': self.assigned_user.get_display_name() if self.assigned_user else None,
            'budget_range': self.budget_range,
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'preferred_contact_method': self.preferred_contact_method,
            'preferred_contact_time': self.preferred_contact_time,
            'timezone': self.timezone,
            'last_contact_date': self.last_contact_date.isoformat() if self.last_contact_date else None,
            'next_followup_date': self.next_followup_date.isoformat() if self.next_followup_date else None,
            'total_contacts': self.total_contacts,
            'notes': self.notes,
            'tags': self.tags,
            'custom_fields': self.custom_fields,
            'registration_date': self.registration_date.isoformat() if self.registration_date else None,
            'registration_source': self.registration_source,
            'first_visit_country': self.first_visit_country,
            'device_type': self.device_type,
            'browser': self.browser,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @property
    def status_display(self):
        """Отображаемое название статуса"""
        status_map = {
            'lead': 'Лид',
            'prospect': 'Потенциальный клиент',
            'active': 'Активный',
            'inactive': 'Неактивный',
            'converted': 'Конвертированный'
        }
        return status_map.get(self.contact_status, self.contact_status)
    
    @property
    def days_since_last_contact(self):
        """Дней с последнего контакта"""
        if not self.last_contact_date:
            return None
        return (datetime.utcnow() - self.last_contact_date).days
    
    @property
    def days_until_followup(self):
        """Дней до следующего контакта"""
        if not self.next_followup_date:
            return None
        return (self.next_followup_date - datetime.utcnow()).days
    
    @property
    def age(self):
        """Возраст контакта"""
        if not self.date_of_birth:
            return None
        today = datetime.utcnow().date()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))

class ContactActivity(db.Model):
    """Модель активности контактов"""
    __tablename__ = 'contact_activity'
    
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False, comment='ID контакта')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, comment='ID пользователя, выполнившего действие')
    
    # Информация об активности
    activity_type = db.Column(db.String(50), nullable=False, comment='Тип активности: call, email, meeting, note, task')
    activity_subtype = db.Column(db.String(50), nullable=True, comment='Подтип активности')
    subject = db.Column(db.String(200), nullable=True, comment='Тема активности')
    description = db.Column(db.Text, nullable=True, comment='Описание активности')
    
    # Детали активности
    duration = db.Column(db.Integer, nullable=True, comment='Длительность в минутах')
    outcome = db.Column(db.String(100), nullable=True, comment='Результат активности')
    next_action = db.Column(db.String(200), nullable=True, comment='Следующее действие')
    next_action_date = db.Column(db.DateTime, nullable=True, comment='Дата следующего действия')
    
    # Статус
    status = db.Column(db.String(50), default='completed', comment='Статус: planned, in_progress, completed, cancelled')
    priority = db.Column(db.String(20), default='normal', comment='Приоритет: low, normal, high, urgent')
    
    # Дополнительные данные
    metadata = db.Column(db.Text, nullable=True, comment='Дополнительные данные в JSON')
    attachments = db.Column(db.Text, nullable=True, comment='Вложения в JSON')
    
    # Временные метки
    scheduled_at = db.Column(db.DateTime, nullable=True, comment='Запланированное время')
    started_at = db.Column(db.DateTime, nullable=True, comment='Время начала')
    completed_at = db.Column(db.DateTime, nullable=True, comment='Время завершения')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    contact = db.relationship('Contact', backref='activities')
    user = db.relationship('User', backref='contact_activities')
    
    def __repr__(self):
        return f'<ContactActivity {self.activity_type}: {self.contact.full_name}>'
    
    def to_dict(self):
        """Преобразование в словарь для JSON"""
        return {
            'id': self.id,
            'contact_id': self.contact_id,
            'contact_name': self.contact.full_name if self.contact else None,
            'user_id': self.user_id,
            'user_name': self.user.get_display_name() if self.user else None,
            'activity_type': self.activity_type,
            'activity_subtype': self.activity_subtype,
            'subject': self.subject,
            'description': self.description,
            'duration': self.duration,
            'outcome': self.outcome,
            'next_action': self.next_action,
            'next_action_date': self.next_action_date.isoformat() if self.next_action_date else None,
            'status': self.status,
            'priority': self.priority,
            'metadata': self.metadata,
            'attachments': self.attachments,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @property
    def activity_display(self):
        """Отображаемое название типа активности"""
        type_map = {
            'call': 'Звонок',
            'email': 'Email',
            'meeting': 'Встреча',
            'note': 'Заметка',
            'task': 'Задача',
            'sms': 'SMS',
            'whatsapp': 'WhatsApp',
            'video_call': 'Видеозвонок'
        }
        return type_map.get(self.activity_type, self.activity_type)
    
    @property
    def status_display(self):
        """Отображаемое название статуса"""
        status_map = {
            'planned': 'Запланировано',
            'in_progress': 'В процессе',
            'completed': 'Завершено',
            'cancelled': 'Отменено'
        }
        return status_map.get(self.status, self.status)

class CountryAnalytics(db.Model):
    """Аналитика по странам"""
    __tablename__ = 'country_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    country_code = db.Column(db.String(2), nullable=False, index=True, comment='Код страны ISO')
    country_name = db.Column(db.String(100), nullable=False, comment='Название страны')
    
    # Статистика пользователей
    total_users = db.Column(db.Integer, default=0, comment='Общее количество пользователей')
    active_users = db.Column(db.Integer, default=0, comment='Активные пользователи')
    new_users_today = db.Column(db.Integer, default=0, comment='Новые пользователи сегодня')
    new_users_this_week = db.Column(db.Integer, default=0, comment='Новые пользователи на этой неделе')
    new_users_this_month = db.Column(db.Integer, default=0, comment='Новые пользователи в этом месяце')
    
    # Метрики конверсии
    conversion_rate = db.Column(db.Float, default=0.0, comment='Конверсия регистрация -> активность')
    completion_rate = db.Column(db.Float, default=0.0, comment='Процент завершения курсов')
    exam_pass_rate = db.Column(db.Float, default=0.0, comment='Процент сдачи экзаменов')
    
    # Метрики вовлеченности
    avg_session_duration = db.Column(db.Float, default=0.0, comment='Средняя длительность сессии (минуты)')
    avg_pages_per_session = db.Column(db.Float, default=0.0, comment='Среднее количество страниц за сессию')
    bounce_rate = db.Column(db.Float, default=0.0, comment='Процент отказов')
    
    # Финансовые метрики
    total_revenue = db.Column(db.Float, default=0.0, comment='Общий доход')
    avg_revenue_per_user = db.Column(db.Float, default=0.0, comment='Средний доход с пользователя')
    
    # Временные метки
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CountryAnalytics {self.country_code}: {self.country_name}>'
    
    def to_dict(self):
        """Преобразование в словарь для JSON"""
        return {
            'id': self.id,
            'country_code': self.country_code,
            'country_name': self.country_name,
            'total_users': self.total_users,
            'active_users': self.active_users,
            'new_users_today': self.new_users_today,
            'new_users_this_week': self.new_users_this_week,
            'new_users_this_month': self.new_users_this_month,
            'conversion_rate': self.conversion_rate,
            'completion_rate': self.completion_rate,
            'exam_pass_rate': self.exam_pass_rate,
            'avg_session_duration': self.avg_session_duration,
            'avg_pages_per_session': self.avg_pages_per_session,
            'bounce_rate': self.bounce_rate,
            'total_revenue': self.total_revenue,
            'avg_revenue_per_user': self.avg_revenue_per_user,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class DeviceAnalytics(db.Model):
    """Аналитика по устройствам и браузерам"""
    __tablename__ = 'device_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Информация об устройстве
    device_category = db.Column(db.String(50), nullable=False, comment='Категория: mobile, desktop, tablet')
    device_type = db.Column(db.String(100), nullable=True, comment='Тип устройства: iPhone, Samsung, etc.')
    browser = db.Column(db.String(50), nullable=False, comment='Браузер: Chrome, Safari, Firefox')
    browser_version = db.Column(db.String(20), nullable=True, comment='Версия браузера')
    os = db.Column(db.String(50), nullable=False, comment='Операционная система')
    os_version = db.Column(db.String(20), nullable=True, comment='Версия ОС')
    screen_resolution = db.Column(db.String(20), nullable=True, comment='Разрешение экрана')
    
    # Статистика использования
    users_count = db.Column(db.Integer, default=0, comment='Количество пользователей')
    sessions_count = db.Column(db.Integer, default=0, comment='Количество сессий')
    page_views_count = db.Column(db.Integer, default=0, comment='Количество просмотров страниц')
    
    # Метрики производительности
    avg_page_load_time = db.Column(db.Float, default=0.0, comment='Среднее время загрузки страницы (секунды)')
    bounce_rate = db.Column(db.Float, default=0.0, comment='Процент отказов')
    avg_session_duration = db.Column(db.Float, default=0.0, comment='Средняя длительность сессии (минуты)')
    avg_pages_per_session = db.Column(db.Float, default=0.0, comment='Среднее количество страниц за сессию')
    
    # Метрики конверсии
    conversion_rate = db.Column(db.Float, default=0.0, comment='Конверсия')
    completion_rate = db.Column(db.Float, default=0.0, comment='Процент завершения')
    
    # Временные метки
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DeviceAnalytics {self.device_category} {self.browser} {self.os}>'
    
    def to_dict(self):
        """Преобразование в словарь для JSON"""
        return {
            'id': self.id,
            'device_category': self.device_category,
            'device_type': self.device_type,
            'browser': self.browser,
            'browser_version': self.browser_version,
            'os': self.os,
            'os_version': self.os_version,
            'screen_resolution': self.screen_resolution,
            'users_count': self.users_count,
            'sessions_count': self.sessions_count,
            'page_views_count': self.page_views_count,
            'avg_page_load_time': self.avg_page_load_time,
            'bounce_rate': self.bounce_rate,
            'avg_session_duration': self.avg_session_duration,
            'avg_pages_per_session': self.avg_pages_per_session,
            'conversion_rate': self.conversion_rate,
            'completion_rate': self.completion_rate,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ProfessionAnalytics(db.Model):
    """Аналитика по профессиям"""
    __tablename__ = 'profession_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    profession_id = db.Column(db.Integer, db.ForeignKey('profession.id'), nullable=False, comment='ID профессии')
    
    # Статистика регистраций
    total_registrations = db.Column(db.Integer, default=0, comment='Общее количество регистраций')
    new_registrations_today = db.Column(db.Integer, default=0, comment='Новые регистрации сегодня')
    new_registrations_this_week = db.Column(db.Integer, default=0, comment='Новые регистрации на этой неделе')
    new_registrations_this_month = db.Column(db.Integer, default=0, comment='Новые регистрации в этом месяце')
    
    # Статистика активности
    active_users = db.Column(db.Integer, default=0, comment='Активные пользователи')
    users_with_progress = db.Column(db.Integer, default=0, comment='Пользователи с прогрессом')
    users_completed_courses = db.Column(db.Integer, default=0, comment='Пользователи, завершившие курсы')
    
    # Метрики обучения
    avg_progress = db.Column(db.Float, default=0.0, comment='Средний прогресс (%)')
    avg_time_spent = db.Column(db.Float, default=0.0, comment='Среднее время обучения (часы)')
    avg_lessons_completed = db.Column(db.Float, default=0.0, comment='Среднее количество завершенных уроков')
    
    # Метрики экзаменов
    total_exam_attempts = db.Column(db.Integer, default=0, comment='Общее количество попыток экзаменов')
    successful_exam_attempts = db.Column(db.Integer, default=0, comment='Успешные попытки экзаменов')
    exam_pass_rate = db.Column(db.Float, default=0.0, comment='Процент сдачи экзаменов')
    avg_exam_score = db.Column(db.Float, default=0.0, comment='Средний балл экзамена')
    
    # Метрики вовлеченности
    avg_session_duration = db.Column(db.Float, default=0.0, comment='Средняя длительность сессии (минуты)')
    avg_sessions_per_user = db.Column(db.Float, default=0.0, comment='Среднее количество сессий на пользователя')
    retention_rate_7d = db.Column(db.Float, default=0.0, comment='7-дневная ретенция')
    retention_rate_30d = db.Column(db.Float, default=0.0, comment='30-дневная ретенция')
    
    # Временные метки
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связи
    profession = db.relationship('Profession', backref='analytics')
    
    def __repr__(self):
        return f'<ProfessionAnalytics {self.profession_id}>'
    
    def to_dict(self):
        """Преобразование в словарь для JSON"""
        return {
            'id': self.id,
            'profession_id': self.profession_id,
            'profession_name': self.profession.name if self.profession else None,
            'total_registrations': self.total_registrations,
            'new_registrations_today': self.new_registrations_today,
            'new_registrations_this_week': self.new_registrations_this_week,
            'new_registrations_this_month': self.new_registrations_this_month,
            'active_users': self.active_users,
            'users_with_progress': self.users_with_progress,
            'users_completed_courses': self.users_completed_courses,
            'avg_progress': self.avg_progress,
            'avg_time_spent': self.avg_time_spent,
            'avg_lessons_completed': self.avg_lessons_completed,
            'total_exam_attempts': self.total_exam_attempts,
            'successful_exam_attempts': self.successful_exam_attempts,
            'exam_pass_rate': self.exam_pass_rate,
            'avg_exam_score': self.avg_exam_score,
            'avg_session_duration': self.avg_session_duration,
            'avg_sessions_per_user': self.avg_sessions_per_user,
            'retention_rate_7d': self.retention_rate_7d,
            'retention_rate_30d': self.retention_rate_30d,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }