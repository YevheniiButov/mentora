#!/usr/bin/env python3
"""
Новые модели для системы специальностей
Добавить в models.py после существующих моделей
"""

from datetime import datetime, timezone
from extensions import db

class Specialty(db.Model):
    """Специальности в системе диагностики"""
    __tablename__ = 'specialties'
    
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(20), unique=True, nullable=False, index=True)  # 'DENTIST', 'GP'
    name = db.Column(db.String(100), nullable=False)  # 'Стоматолог', 'Врач общей практики'
    name_en = db.Column(db.String(100), nullable=False)
    name_nl = db.Column(db.String(100), nullable=False)
    
    # Статус системы
    is_active = db.Column(db.Boolean, default=True, index=True)
    is_calibrated = db.Column(db.Boolean, default=False, index=True)  # Есть ли калиброванные вопросы
    total_questions = db.Column(db.Integer, default=0)
    calibrated_questions = db.Column(db.Integer, default=0)
    
    # IRT настройки
    irt_model = db.Column(db.String(10), default='3PL')  # 3PL, 2PL, 1PL
    calibration_threshold = db.Column(db.Integer, default=5)  # Минимум ответов для калибровки
    
    # Метаданные
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    domains = db.relationship('SpecialtyDomain', backref='specialty', lazy='dynamic', cascade='all, delete-orphan')
    questions = db.relationship('Question', backref='specialty', lazy='dynamic')
    diagnostic_sessions = db.relationship('DiagnosticSession', backref='specialty', lazy='dynamic')
    irt_parameters = db.relationship('IRTParameters', backref='specialty', lazy='dynamic')
    
    def __repr__(self):
        return f'<Specialty {self.code}: {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'name_en': self.name_en,
            'name_nl': self.name_nl,
            'is_active': self.is_active,
            'is_calibrated': self.is_calibrated,
            'total_questions': self.total_questions,
            'calibrated_questions': self.calibrated_questions,
            'irt_model': self.irt_model,
            'calibration_threshold': self.calibration_threshold,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_calibration_progress(self):
        """Получить прогресс калибровки"""
        if self.total_questions == 0:
            return 0.0
        return (self.calibrated_questions / self.total_questions) * 100
    
    def is_ready_for_adaptive_testing(self):
        """Готов ли для адаптивного тестирования"""
        return self.is_calibrated and self.calibrated_questions >= 50


class SpecialtyDomain(db.Model):
    """Домены для каждой специальности"""
    __tablename__ = 'specialty_domains'
    
    id = db.Column(db.Integer, primary_key=True)
    specialty_id = db.Column(db.Integer, db.ForeignKey('specialties.id', ondelete='CASCADE'), nullable=False, index=True)
    domain_code = db.Column(db.String(20), nullable=False)  # 'PHARMACOLOGY', 'CARDIOLOGY'
    domain_name = db.Column(db.String(100), nullable=False)
    domain_name_en = db.Column(db.String(100), nullable=False)
    domain_name_nl = db.Column(db.String(100), nullable=False)
    
    # Веса и приоритеты
    weight_percentage = db.Column(db.Float, nullable=False)
    is_critical = db.Column(db.Boolean, default=False, index=True)
    category = db.Column(db.String(50), nullable=False, index=True)  # THEORETICAL, CLINICAL, etc.
    
    # Статистика
    question_count = db.Column(db.Integer, default=0)
    calibrated_count = db.Column(db.Integer, default=0)
    
    # Метаданные
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    questions = db.relationship('Question', backref='specialty_domain', lazy='dynamic')
    
    __table_args__ = (
        db.UniqueConstraint('specialty_id', 'domain_code', name='unique_specialty_domain'),
        db.Index('idx_specialty_domain', 'specialty_id', 'domain_code'),
    )
    
    def __repr__(self):
        return f'<SpecialtyDomain {self.specialty.code}.{self.domain_code}: {self.domain_name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'specialty_id': self.specialty_id,
            'domain_code': self.domain_code,
            'domain_name': self.domain_name,
            'domain_name_en': self.domain_name_en,
            'domain_name_nl': self.domain_name_nl,
            'weight_percentage': self.weight_percentage,
            'is_critical': self.is_critical,
            'category': self.category,
            'question_count': self.question_count,
            'calibrated_count': self.calibrated_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_calibration_progress(self):
        """Получить прогресс калибровки домена"""
        if self.question_count == 0:
            return 0.0
        return (self.calibrated_count / self.question_count) * 100


class PilotResponse(db.Model):
    """Ответы пользователей для калибровки вопросов"""
    __tablename__ = 'pilot_responses'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    specialty_id = db.Column(db.Integer, db.ForeignKey('specialties.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Данные ответа
    is_correct = db.Column(db.Boolean, nullable=False)
    response_time = db.Column(db.Float, nullable=True)  # секунды
    user_ability = db.Column(db.Float, nullable=True)  # θ на момент ответа
    
    # Метаданные
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    question = db.relationship('Question', backref='pilot_responses')
    user = db.relationship('User', backref='pilot_responses')
    specialty = db.relationship('Specialty', backref='pilot_responses')
    
    __table_args__ = (
        db.Index('idx_pilot_question_user', 'question_id', 'user_id'),
        db.Index('idx_pilot_specialty_date', 'specialty_id', 'created_at'),
    )
    
    def __repr__(self):
        return f'<PilotResponse Q{self.question_id} U{self.user_id}: {"✓" if self.is_correct else "✗"}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'question_id': self.question_id,
            'user_id': self.user_id,
            'specialty_id': self.specialty_id,
            'is_correct': self.is_correct,
            'response_time': self.response_time,
            'user_ability': self.user_ability,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class DiagnosticResult(db.Model):
    """Результаты диагностики (отдельно от сессий для аналитики)"""
    __tablename__ = 'diagnostic_results'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('diagnostic_session.id', ondelete='CASCADE'), nullable=False, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, index=True)
    specialty_id = db.Column(db.Integer, db.ForeignKey('specialties.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Основные метрики
    theta_score = db.Column(db.Float, nullable=False)  # Финальная оценка способности
    standard_error = db.Column(db.Float, nullable=False)  # Стандартная ошибка
    confidence_interval_lower = db.Column(db.Float, nullable=True)
    confidence_interval_upper = db.Column(db.Float, nullable=True)
    
    # Процентильный ранг
    percentile_rank = db.Column(db.Float, nullable=True)  # Процентиль среди коллег
    
    # Статистика
    total_questions = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=False)
    accuracy = db.Column(db.Float, nullable=False)  # Процент правильных ответов
    avg_response_time = db.Column(db.Float, nullable=True)  # Среднее время ответа
    
    # Результаты по категориям (JSON)
    category_scores = db.Column(db.Text, nullable=True)  # JSON с оценками по категориям
    domain_analysis = db.Column(db.Text, nullable=True)  # JSON с анализом по доменам
    
    # Временные метки
    session_duration = db.Column(db.Integer, nullable=True)  # Длительность в секундах
    completed_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    session = db.relationship('DiagnosticSession', backref='result', uselist=False)
    user = db.relationship('User', backref='diagnostic_results')
    specialty = db.relationship('Specialty', backref='diagnostic_results')
    
    __table_args__ = (
        db.Index('idx_diagnostic_user_specialty', 'user_id', 'specialty_id'),
        db.Index('idx_diagnostic_theta_score', 'theta_score'),
        db.Index('idx_diagnostic_percentile', 'percentile_rank'),
    )
    
    def __repr__(self):
        return f'<DiagnosticResult S{self.session_id}: θ={self.theta_score:.2f}, {self.percentile_rank}%>'
    
    def to_dict(self):
        import json
        
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'specialty_id': self.specialty_id,
            'theta_score': self.theta_score,
            'standard_error': self.standard_error,
            'confidence_interval': {
                'lower': self.confidence_interval_lower,
                'upper': self.confidence_interval_upper
            },
            'percentile_rank': self.percentile_rank,
            'total_questions': self.total_questions,
            'correct_answers': self.correct_answers,
            'accuracy': self.accuracy,
            'avg_response_time': self.avg_response_time,
            'category_scores': json.loads(self.category_scores) if self.category_scores else {},
            'domain_analysis': json.loads(self.domain_analysis) if self.domain_analysis else {},
            'session_duration': self.session_duration,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    def get_performance_level(self):
        """Получить уровень производительности"""
        if self.percentile_rank is None:
            return "Unknown"
        
        if self.percentile_rank >= 90:
            return "Excellent"
        elif self.percentile_rank >= 75:
            return "Above Average"
        elif self.percentile_rank >= 50:
            return "Average"
        elif self.percentile_rank >= 25:
            return "Below Average"
        else:
            return "Needs Improvement"
