# models.py - Essential Database Models (Clean Version)
# Only critical models for core functionality

import json
from datetime import datetime, timezone, date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from typing import Dict
from utils.serializers import JSONSerializableMixin, to_json_safe

def safe_json_dumps(obj):
    """Safely serialize object to JSON string, handling datetime objects"""
    class DateTimeEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            if isinstance(obj, date):
                return obj.isoformat()
            return super().default(obj)
    
    return json.dumps(obj, cls=DateTimeEncoder, ensure_ascii=False)

# ========================================
# USER MANAGEMENT
# ========================================

class User(db.Model, UserMixin):
    """User model for authentication and progress tracking"""
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=True, index=True)  # Made nullable for DigiD users
    password_hash = db.Column(db.String(128), nullable=True)  # Made nullable for DigiD users
    
    # DigiD Authentication fields
    digid_username = db.Column(db.String(80), unique=True, nullable=True, index=True)
    bsn = db.Column(db.String(9), unique=True, nullable=True, index=True)  # Dutch Social Security Number
    digid_verified = db.Column(db.Boolean, default=False)
    created_via_digid = db.Column(db.Boolean, default=False)
    
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    
    # Personal Information (Extended Profile)
    profile_photo = db.Column(db.String(255), nullable=True)  # Path to profile photo
    phone = db.Column(db.String(20), nullable=True)
    birth_date = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)  # male, female, other
    
    # Registration completion fields
    registration_completed = db.Column(db.Boolean, default=False)
    profession = db.Column(db.String(50), nullable=True)  # tandarts, apotheker, huisarts, verpleegkundige
    diploma_file = db.Column(db.String(255), nullable=True)  # Path to uploaded diploma file
    language_certificate = db.Column(db.String(255), nullable=True)  # Path to uploaded language certificate
    
    # Professional Information (Extended)
    big_number = db.Column(db.String(20), nullable=True)  # BIG registration number
    workplace = db.Column(db.String(255), nullable=True)  # Current workplace/practice
    specialization = db.Column(db.String(100), nullable=True)  # Medical specialization
    registration_date = db.Column(db.Date, nullable=True)  # Date when BIG was obtained
    license_expiry = db.Column(db.Date, nullable=True)  # BIG license expiry date
    
    # Additional Documents (JSON field for flexibility)
    additional_documents = db.Column(db.Text, nullable=True)  # JSON array of document paths
    language_certificates = db.Column(db.Text, nullable=True)  # JSON array of language cert paths
    
    # Account status
    is_active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20), default='user')  # user, admin
    
    # Preferences & Settings
    language = db.Column(db.String(5), default='en')
    theme = db.Column(db.String(20), default='light')
    
    # Notification Preferences (JSON field)
    notification_settings = db.Column(db.Text, nullable=True)  # JSON for notification preferences
    
    # Privacy Settings (JSON field)
    privacy_settings = db.Column(db.Text, nullable=True)  # JSON for privacy settings
    
    # Gamification
    level = db.Column(db.Integer, default=1)
    xp = db.Column(db.Integer, default=0)
    
    # Subscription
    has_subscription = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    profile_updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    progress = db.relationship('UserProgress', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    digid_sessions = db.relationship('DigiDSession', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    audit_logs = db.relationship('ProfileAuditLog', backref='user', lazy='dynamic', cascade='all, delete-orphan', foreign_keys='ProfileAuditLog.user_id')
    
    # Gamification relationships
    achievements = db.relationship('UserAchievement', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    activities = db.relationship('UserActivity', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    streak = db.relationship('UserStreak', backref='user', uselist=False, cascade='all, delete-orphan')
    reminders = db.relationship('UserReminder', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def is_admin(self):
        """Check if user has admin role"""
        return self.role == 'admin'
    
    @property
    def full_name(self):
        """Get user's full name (deprecated, use get_display_name() instead)"""
        return self.get_display_name()
    
    def get_notification_settings(self):
        """Get notification settings as dict"""
        if self.notification_settings:
            try:
                return json.loads(self.notification_settings)
            except:
                pass
        # Default settings
        return {
            'email_notifications': True,
            'sms_notifications': False,
            'push_notifications': True,
            'learning_reminders': True,
            'exam_notifications': True,
            'community_updates': False,
            'marketing_emails': False
        }
    
    def set_notification_settings(self, settings):
        """Set notification settings from dict"""
        self.notification_settings = safe_json_dumps(settings)
    
    def get_privacy_settings(self):
        """Get privacy settings as dict"""
        if self.privacy_settings:
            try:
                return json.loads(self.privacy_settings)
            except:
                pass
        # Default settings
        return {
            'profile_visibility': 'registered_users',  # public, registered_users, private
            'show_progress': True,
            'show_achievements': True,
            'allow_messages': True,
            'show_last_seen': True,
            'data_sharing': False,
            'analytics_tracking': True
        }
    
    def set_privacy_settings(self, settings):
        """Set privacy settings from dict"""
        self.privacy_settings = safe_json_dumps(settings)
    
    def get_additional_documents(self):
        """Get additional documents as list"""
        if self.additional_documents:
            try:
                return json.loads(self.additional_documents)
            except:
                pass
        return []
    
    def add_additional_document(self, document_path, document_type, document_name):
        """Add an additional document"""
        docs = self.get_additional_documents()
        docs.append({
            'path': document_path,
            'type': document_type,
            'name': document_name,
            'uploaded_at': datetime.now(timezone.utc).isoformat()
        })
        self.additional_documents = safe_json_dumps(docs)
    
    def get_language_certificates(self):
        """Get language certificates as list"""
        if self.language_certificates:
            try:
                return json.loads(self.language_certificates)
            except:
                pass
        return []
    
    def add_language_certificate(self, cert_path, cert_type, cert_level):
        """Add a language certificate"""
        certs = self.get_language_certificates()
        certs.append({
            'path': cert_path,
            'type': cert_type,
            'level': cert_level,
            'uploaded_at': datetime.now(timezone.utc).isoformat()
        })
        self.language_certificates = safe_json_dumps(certs)
    
    def get_progress_stats(self):
        """Get user's learning progress statistics"""
        completed_lessons = self.progress.filter_by(completed=True).count()
        total_time = db.session.query(db.func.sum(UserProgress.time_spent)).filter_by(user_id=self.id).scalar() or 0
        
        # Calculate activity days (unique days with progress)
        from datetime import datetime, timedelta
        unique_days = db.session.query(
            db.func.count(db.func.distinct(db.func.date(UserProgress.last_accessed)))
        ).filter_by(user_id=self.id).scalar() or 0
        
        return {
            'completed_lessons': completed_lessons,
            'total_time_spent': total_time,
            'total_progress': self.progress.count(),
            'activity_days': unique_days
        }
    
    def is_digid_user(self):
        """Check if user was created via DigiD authentication"""
        return self.created_via_digid and self.digid_verified
    
    def get_authentication_method(self):
        """Get the primary authentication method used by this user"""
        if self.is_digid_user():
            return 'digid'
        elif self.password_hash:
            return 'password'
        else:
            return 'unknown'
    
    def get_display_name(self):
        """Get the best available display name for the user"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.username:
            return self.username
        elif self.digid_username:
            return self.digid_username
        else:
            return self.email
    
    def get_profession_display(self):
        """Get the profession display name with emoji"""
        profession_display = {
            'tandarts': '🦷 Tandarts',
            'apotheker': '💊 Apotheker',
            'huisarts': '🩺 Huisarts',
            'verpleegkundige': '👩‍⚕️ Verpleegkundige'
        }
        return profession_display.get(self.profession, self.profession or 'Не указана')
    
    def can_use_password_auth(self):
        """Check if user can authenticate with password"""
        return self.password_hash is not None
    
    def can_use_digid_auth(self):
        """Check if user can authenticate with DigiD"""
        return self.digid_verified and self.bsn is not None
    
    def log_profile_change(self, field, old_value, new_value, changed_by=None):
        """Log a profile change for audit trail"""
        audit_log = ProfileAuditLog(
            user_id=self.id,
            field_changed=field,
            old_value=str(old_value) if old_value is not None else None,
            new_value=str(new_value) if new_value is not None else None,
            changed_by=changed_by or self.id,
            change_type='profile_update'
        )
        db.session.add(audit_log)
    
    # ========================================
    # GAMIFICATION METHODS
    # ========================================
    
    def get_or_create_streak(self):
        """Get or create user streak record"""
        streak = UserStreak.query.filter_by(user_id=self.id).first()
        if not streak:
            streak = UserStreak(user_id=self.id)
            db.session.add(streak)
        return streak
    
    def update_activity(self, activity_date=None, lessons_completed=0, time_spent=0.0, xp_earned=0, 
                       modules_accessed=0, tests_taken=0, virtual_patients_completed=0):
        """Update daily activity record"""
        from datetime import date
        
        if activity_date is None:
            activity_date = date.today()
        
        # Get or create activity record
        activity = UserActivity.query.filter_by(user_id=self.id, activity_date=activity_date).first()
        if not activity:
            activity = UserActivity(user_id=self.id, activity_date=activity_date)
            db.session.add(activity)
        
        # Update values
        activity.lessons_completed += lessons_completed
        activity.time_spent += time_spent
        activity.xp_earned += xp_earned
        activity.modules_accessed += modules_accessed
        activity.tests_taken += tests_taken
        activity.virtual_patients_completed += virtual_patients_completed
        
        # Update user XP
        self.xp += xp_earned
        
        # Update streak
        if lessons_completed > 0 or time_spent > 0:
            streak = self.get_or_create_streak()
            streak.update_streak(activity_date)
        
        # Check for achievements
        self.check_achievements()
        
        return activity
    
    def check_achievements(self):
        """Check and award achievements based on current progress"""
        from sqlalchemy import func
        
        # Get user stats
        stats = self.get_progress_stats()
        total_time_hours = stats['total_time_spent'] / 60  # Convert to hours
        streak = self.get_or_create_streak()
        
        # Get all achievements user hasn't earned yet
        earned_achievement_ids = [ua.achievement_id for ua in 
                                UserAchievement.query.filter_by(user_id=self.id).all()]
        
        available_achievements = Achievement.query.filter(
            Achievement.is_active == True,
            ~Achievement.id.in_(earned_achievement_ids)
        ).all()
        
        new_achievements = []
        
        for achievement in available_achievements:
            earned = False
            
            if achievement.requirement_type == 'lessons_completed':
                earned = stats['completed_lessons'] >= achievement.requirement_value
            elif achievement.requirement_type == 'hours_studied':
                earned = total_time_hours >= achievement.requirement_value
            elif achievement.requirement_type == 'streak_days':
                earned = streak.current_streak >= achievement.requirement_value
            elif achievement.requirement_type == 'longest_streak':
                earned = streak.longest_streak >= achievement.requirement_value
            elif achievement.requirement_type == 'xp_earned':
                earned = self.xp >= achievement.requirement_value
            elif achievement.requirement_type == 'level_reached':
                earned = self.level >= achievement.requirement_value
            
            if earned:
                user_achievement = UserAchievement(
                    user_id=self.id,
                    achievement_id=achievement.id
                )
                db.session.add(user_achievement)
                new_achievements.append(achievement)
        
        return new_achievements
    
    def get_earned_achievements(self):
        """Get all achievements earned by user"""
        return db.session.query(Achievement).join(UserAchievement).filter(
            UserAchievement.user_id == self.id
        ).order_by(UserAchievement.earned_at.desc()).all()
    
    def get_recent_activity(self, days=7):
        """Get recent activity for specified number of days"""
        from datetime import date, timedelta
        
        start_date = date.today() - timedelta(days=days)
        return UserActivity.query.filter(
            UserActivity.user_id == self.id,
            UserActivity.activity_date >= start_date
        ).order_by(UserActivity.activity_date.desc()).all()
    
    def get_activity_chart_data(self, days=30):
        """Get activity data for charts"""
        from datetime import date, timedelta
        
        start_date = date.today() - timedelta(days=days)
        activities = UserActivity.query.filter(
            UserActivity.user_id == self.id,
            UserActivity.activity_date >= start_date
        ).order_by(UserActivity.activity_date.asc()).all()
        
        # Create chart data
        chart_data = {
            'labels': [str(activity.activity_date) for activity in activities],
            'lessons': [activity.lessons_completed for activity in activities],
            'time': [activity.time_spent for activity in activities],
            'xp': [activity.xp_earned for activity in activities]
        }
        
        return chart_data
    
    def get_upcoming_reminders(self, days=7):
        """Get upcoming reminders"""
        from datetime import datetime, timedelta
        
        end_date = datetime.now() + timedelta(days=days)
        return UserReminder.query.filter(
            UserReminder.user_id == self.id,
            UserReminder.is_active == True,
            UserReminder.is_completed == False,
            UserReminder.reminder_date <= end_date
        ).order_by(UserReminder.reminder_date.asc()).all()
    
    def get_dashboard_stats(self):
        """Get comprehensive dashboard statistics"""
        from datetime import date, timedelta
        from sqlalchemy import func
        
        stats = self.get_progress_stats()
        streak = self.get_or_create_streak()
        
        # Get today's activity
        today_activity = UserActivity.query.filter_by(
            user_id=self.id, 
            activity_date=date.today()
        ).first()
        
        # Get week activity
        week_start = date.today() - timedelta(days=7)
        week_stats = db.session.query(
            func.sum(UserActivity.lessons_completed),
            func.sum(UserActivity.time_spent),
            func.sum(UserActivity.xp_earned)
        ).filter(
            UserActivity.user_id == self.id,
            UserActivity.activity_date >= week_start
        ).first()
        
        # Calculate level progress
        level_xp_required = self.level * 100  # 100 XP per level
        level_progress = min(100, (self.xp % level_xp_required) / level_xp_required * 100)
        
        # Check if level up is needed
        if self.xp >= level_xp_required:
            new_level = (self.xp // 100) + 1
            if new_level > self.level:
                self.level = new_level
        
        dashboard_stats = {
            **stats,
            'current_streak': streak.current_streak,
            'longest_streak': streak.longest_streak,
            'level': self.level,
            'xp': self.xp,
            'level_progress': level_progress,
            'today_lessons': today_activity.lessons_completed if today_activity else 0,
            'today_time': today_activity.time_spent if today_activity else 0,
            'today_xp': today_activity.xp_earned if today_activity else 0,
            'week_lessons': week_stats[0] or 0,
            'week_time': week_stats[1] or 0,
            'week_xp': week_stats[2] or 0,
            'achievements_count': UserAchievement.query.filter_by(user_id=self.id).count(),
            'active_reminders': UserReminder.query.filter_by(
                user_id=self.id, is_active=True, is_completed=False
            ).count()
        }
        
        return dashboard_stats
    
    def get_next_recommended_modules(self, limit=5):
        """Get next recommended modules based on progress"""
        # Get modules from incomplete subjects
        incomplete_modules = []
        
        # Get all subjects and their modules
        subjects = Subject.query.all()
        for subject in subjects:
            subject_progress = subject.get_progress_for_user(self.id)
            if subject_progress['progress_percent'] < 100:
                # Get modules for this subject
                modules = subject.module.all()
                for module in modules:
                    module_progress = module.get_progress_for_user(self.id)
                    if module_progress['progress_percent'] < 100:
                        # Get the learning path for this subject
                        path = LearningPath.query.get(subject.learning_path_id)
                        incomplete_modules.append({
                            'module': module,
                            'subject': subject,
                            'path': path,
                            'progress': module_progress
                        })
        
        # Sort by progress (modules with some progress first)
        incomplete_modules.sort(key=lambda x: x['progress']['progress_percent'], reverse=True)
        
        return incomplete_modules[:limit]
    
    def __repr__(self):
        username_display = self.username or self.digid_username or self.email
        return f'<User {username_display}>'

    def get_path_progress(self, path_id):
        """Получить прогресс по конкретному пути"""
        return UserLearningProgress.query.filter_by(
            user_id=self.id,
            learning_path_id=path_id
        ).first()
    
    def get_all_path_progress(self):
        """Получить прогресс по всем путям"""
        progress_records = UserLearningProgress.query.filter_by(
            user_id=self.id
        ).all()
        
        return {record.learning_path_id: record for record in progress_records}
    
    def get_completed_paths(self):
        """Получить завершенные пути обучения"""
        return UserLearningProgress.query.filter_by(
            user_id=self.id,
            progress_percentage=100
        ).all()
    
    def get_active_paths(self):
        """Получить активные пути обучения"""
        return UserLearningProgress.query.filter_by(
            user_id=self.id,
            is_active=True
        ).filter(UserLearningProgress.progress_percentage < 100).all()
    
    def get_bi_toets_readiness(self):
        """Рассчитать готовность к BI-toets"""
        all_progress = self.get_all_path_progress()
        
        # Веса компонентов
        component_weights = {
            'THEORETICAL': 70,
            'METHODOLOGY': 10,
            'PRACTICAL': 15,
            'CLINICAL': 5
        }
        
        total_score = 0
        component_scores = {}
        
        for component, weight in component_weights.items():
            component_paths = LearningPath.get_by_component(component)
            component_total = 0
            component_completed = 0
            
            for path in component_paths:
                progress = all_progress.get(path.id)
                if progress:
                    component_total += path.exam_weight
                    component_completed += path.exam_weight * (progress.progress_percentage / 100)
            
            if component_total > 0:
                component_score = (component_completed / component_total) * weight
                component_scores[component] = component_score
                total_score += component_score
        
        return {
            'total_score': total_score,
            'component_scores': component_scores,
            'readiness_level': self._get_readiness_level(total_score)
        }
    
    def _get_readiness_level(self, score):
        """Определить уровень готовности"""
        if score >= 85:
            return 'excellent'
        elif score >= 70:
            return 'good'
        elif score >= 50:
            return 'fair'
        else:
            return 'needs_improvement'

class ProfileAuditLog(db.Model):
    """Audit log for tracking profile changes"""
    __tablename__ = 'profile_audit_log'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    
    # Change details
    field_changed = db.Column(db.String(100), nullable=False)
    old_value = db.Column(db.Text, nullable=True)
    new_value = db.Column(db.Text, nullable=True)
    change_type = db.Column(db.String(50), default='profile_update')  # profile_update, file_upload, settings_change
    
    # Metadata
    changed_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Who made the change
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    changed_by_user = db.relationship('User', foreign_keys=[changed_by], backref='changes_made')
    
    def __repr__(self):
        return f'<ProfileAuditLog {self.field_changed}: {self.old_value} -> {self.new_value}>'

# ========================================
# LEARNING CONTENT HIERARCHY
# ========================================

class LearningPath(db.Model):
    """Top-level learning paths (5 exam categories)"""
    __tablename__ = 'learning_path'
    
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    name_nl = db.Column(db.String(200))
    name_ru = db.Column(db.String(200))
    description = db.Column(db.Text)
    
    # BI-toets специфика
    exam_component = db.Column(db.String(20), nullable=False)  # THEORETICAL, METHODOLOGY, PRACTICAL, CLINICAL
    exam_weight = db.Column(db.Float, nullable=False)  # Вес в процентах
    exam_type = db.Column(db.String(20), nullable=False)  # multiple_choice, open_book, practical_theory, interview, case_study
    
    # Структура обучения
    duration_weeks = db.Column(db.Integer)
    total_estimated_hours = db.Column(db.Integer)
    prerequisites = db.Column(db.JSON)  # Список ID предварительных путей
    
    # Модули и связи
    modules = db.Column(db.JSON)  # Структура модулей
    
    # Оценка
    assessment = db.Column(db.JSON)  # Структура оценки
    
    # Метаданные
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Связи
    user_progress = db.relationship('UserLearningProgress', backref='learning_path', lazy=True)
    
    def __repr__(self):
        return f'<LearningPath {self.id}: {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'name_nl': self.name_nl,
            'name_ru': self.name_ru,
            'description': self.description,
            'exam_component': self.exam_component,
            'exam_weight': self.exam_weight,
            'exam_type': self.exam_type,
            'duration_weeks': self.duration_weeks,
            'total_estimated_hours': self.total_estimated_hours,
            'prerequisites': self.prerequisites or [],
            'modules': self.modules or [],
            'assessment': self.assessment or {},
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_by_component(cls, component):
        """Получить все пути по компоненту экзамена"""
        return cls.query.filter_by(exam_component=component, is_active=True).all()
    
    @classmethod
    def get_bi_toets_structure(cls):
        """Получить полную структуру BI-toets"""
        return {
            'THEORETICAL': cls.get_by_component('THEORETICAL'),
            'METHODOLOGY': cls.get_by_component('METHODOLOGY'),
            'PRACTICAL': cls.get_by_component('PRACTICAL'),
            'CLINICAL': cls.get_by_component('CLINICAL')
        }
    
    def calculate_total_hours(self):
        """Рассчитать общее количество часов из модулей"""
        if not self.modules:
            return 0
        
        total = 0
        for module in self.modules:
            total += module.get('estimated_hours', 0)
        return total
    
    def get_domains(self):
        """Получить все домены из модулей"""
        domains = set()
        if self.modules:
            for module in self.modules:
                module_domains = module.get('domains', [])
                domains.update(module_domains)
        return list(domains)

class Subject(db.Model):
    """Subject areas within learning paths"""
    __tablename__ = 'subject'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, default=0)
    icon = db.Column(db.String(50), default="folder2-open")
    
    # Foreign keys
    learning_path_id = db.Column(db.Integer, db.ForeignKey("learning_path.id", ondelete='CASCADE'), nullable=False)
    
    # Relationships
    module = db.relationship("Module", backref="subject", lazy='dynamic', cascade="all, delete-orphan")
    final_test = db.relationship("Test", backref="subject_final_test_owner", lazy=True, uselist=False, cascade="all, delete-orphan", foreign_keys='Test.subject_final_test_id')
    
    def get_progress_for_user(self, user_id):
        """Get completion progress for this subject"""
        total_lessons = 0
        completed_lessons = 0
        
        for module in self.module:
            module_stats = module.get_progress_for_user(user_id)
            total_lessons += module_stats['total_lessons']
            completed_lessons += module_stats['completed_lessons']
        
        progress_percent = int((completed_lessons / total_lessons * 100)) if total_lessons > 0 else 0
        
        return {
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'progress_percent': progress_percent
        }
    
    def __repr__(self):
        return f'<Subject {self.id}: {self.name} (Path ID: {self.learning_path_id})>'

class Module(db.Model):
    """Modules/subtopics within subjects"""
    __tablename__ = 'module'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, default=0)
    icon = db.Column(db.String(50), default="file-earmark-text")
    module_type = db.Column(db.String(50), default='content', index=True)
    is_premium = db.Column(db.Boolean, default=False)
    
    # Foreign keys
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id", ondelete='CASCADE'), nullable=False)
    is_final_test = db.Column(db.Boolean, default=False, nullable=False, index=True)
    
    # Relationships
    lessons = db.relationship("Lesson", backref="module", lazy='dynamic', cascade="all, delete-orphan")
    intermediate_tests = db.relationship("Test", backref="module_intermediate_test_owner", lazy='dynamic', foreign_keys='Test.module_intermediate_test_id')
    
    def get_progress_for_user(self, user_id):
        """Get completion progress for this module"""
        total_lessons = self.lessons.count()
        completed_lessons = UserProgress.query.join(Lesson).filter(
            Lesson.module_id == self.id,
            UserProgress.user_id == user_id,
            UserProgress.completed == True
        ).count()
        
        progress_percent = int((completed_lessons / total_lessons * 100)) if total_lessons > 0 else 0
        
        return {
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'progress_percent': progress_percent
        }
    
    def __repr__(self):
        final_status = "FINAL" if self.is_final_test else ""
        premium_status = "Premium" if self.is_premium else "Free"
        return f'<Module {self.id}: {self.title} (Subject ID: {self.subject_id}, {final_status}{premium_status})>'

class Lesson(db.Model):
    """Individual lessons/cards within modules"""
    __tablename__ = 'lessons'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)
    content_type = db.Column(db.String(50))
    order = db.Column(db.Integer, default=0)
    
    # Foreign keys
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'))
    
    # Subtopic organization
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=True)
    subtopic = db.Column(db.String(255), nullable=True, index=True)
    subtopic_slug = db.Column(db.String(255), nullable=True, index=True)
    subtopic_order = db.Column(db.Integer, default=0)
    
    # Relationships
    progress = db.relationship('UserProgress', backref='lesson', lazy=True)
    
    def extract_subtopic(self):
        if not self.content:
            return None
        try:
            content_data = json.loads(self.content)
            if 'module_title' in content_data:
                return content_data.get('module_title')
            if content_data.get('type') in ['learning', 'test']:
                return content_data.get('module_title')
            if 'cards' in content_data and content_data['cards']:
                return content_data['cards'][0].get('module_title')
            if 'questions' in content_data and content_data['questions']:
                return content_data['questions'][0].get('module_title')
        except (json.JSONDecodeError, AttributeError, KeyError, TypeError):
            pass
        return None
    
    def get_user_progress(self, user_id):
        """Get progress for specific user"""
        return UserProgress.query.filter_by(user_id=user_id, lesson_id=self.id).first()
    
    def is_completed_by_user(self, user_id):
        """Check if lesson is completed by user"""
        progress = self.get_user_progress(user_id)
        return progress and progress.completed
    
    def __repr__(self):
        return f'<Lesson {self.title}>'

# ========================================
# PROGRESS TRACKING
# ========================================

class UserProgress(db.Model):
    """Track user progress through lessons"""
    __tablename__ = 'user_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete='CASCADE'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey("lessons.id", ondelete='CASCADE'), nullable=False)
    
    # Progress data
    completed = db.Column(db.Boolean, default=False)
    time_spent = db.Column(db.Float, default=0.0)  # minutes
    score = db.Column(db.Float)  # for quizzes/tests
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime)
    last_accessed = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('user_id', 'lesson_id', name='_user_lesson_uc'),)
    
    def mark_completed(self, score=None):
        """Mark lesson as completed"""
        self.completed = True
        self.completed_at = datetime.now(timezone.utc)
        if score is not None:
            self.score = score
    
    def add_time_spent(self, minutes):
        """Add time spent to lesson"""
        self.time_spent += minutes
        self.last_accessed = datetime.now(timezone.utc)
    
    def __repr__(self):
        return f'<UserProgress User:{self.user_id} Lesson:{self.lesson_id} Done:{self.completed}>'

# ========================================
# TESTING SYSTEM
# ========================================

class QuestionCategory(db.Model):
    """Categories for organizing test questions"""
    __tablename__ = 'category'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    
    def __repr__(self):
        return f'<QuestionCategory {self.name}>'

class Question(db.Model):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    options = db.Column(db.JSON, nullable=False)
    correct_answer_index = db.Column(db.Integer, nullable=False)
    correct_answer_text = db.Column(db.String(500), nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False)
    domain = db.Column(db.String(20), nullable=False)
    difficulty_level = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
    tags = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Дополнительные поля для расширенной функциональности
    big_domain_id = db.Column(db.Integer, db.ForeignKey('big_domain.id'), nullable=True, index=True)
    question_type = db.Column(db.String(50), default='multiple_choice', nullable=False)
    clinical_context = db.Column(db.Text, nullable=True)
    learning_objectives = db.Column(db.JSON, nullable=True)

    # Relationships
    big_domain = db.relationship('BIGDomain', backref='questions', lazy=True)
    irt_parameters = db.relationship('IRTParameters', backref='question', uselist=False, cascade='all, delete-orphan')

    @property
    def irt_difficulty(self):
        """Get IRT difficulty parameter"""
        return self.irt_parameters.difficulty if self.irt_parameters else None
    
    @property
    def irt_discrimination(self):
        """Get IRT discrimination parameter"""
        return self.irt_parameters.discrimination if self.irt_parameters else None
    
    @property
    def irt_guessing(self):
        """Get IRT guessing parameter"""
        return self.irt_parameters.guessing if self.irt_parameters else None

    def validate_irt_parameters(self):
        """
        Validate IRT parameters according to 3PL model constraints
        
        Raises:
            ValueError: If any parameter is outside valid range
        """
        if not self.irt_parameters:
            raise ValueError("No IRT parameters found for this question")
        
        self.irt_parameters.validate_parameters()
    
    def set_irt_parameters(self, difficulty: float, discrimination: float, guessing: float):
        """
        Set IRT parameters with validation
        
        Args:
            difficulty: b-parameter (item difficulty)
            discrimination: a-parameter (item discrimination)
            guessing: c-parameter (guessing parameter)
        """
        if not self.irt_parameters:
            # Create new IRTParameters record
            from extensions import db
            self.irt_parameters = IRTParameters(
                question_id=self.id,
                difficulty=difficulty,
                discrimination=discrimination,
                guessing=guessing
            )
            db.session.add(self.irt_parameters)
        else:
            # Update existing IRTParameters
            self.irt_parameters.set_parameters(difficulty, discrimination, guessing)
    
    def get_irt_parameters(self) -> dict:
        """
        Get IRT parameters as dictionary with validation
        
        Returns:
            Dict with IRT parameters
        """
        if not self.irt_parameters:
            return None
        
        return self.irt_parameters.get_parameters()

    def to_dict(self):
        return {
            'id': self.id,
            'text': self.text,
            'options': self.options,
            'correct_answer_index': self.correct_answer_index,
            'correct_answer_text': self.correct_answer_text,
            'explanation': self.explanation,
            'category': self.category,
            'domain': self.domain,
            'difficulty_level': self.difficulty_level,
            'image_url': self.image_url,
            'tags': self.tags,
            'irt_params': self.get_irt_parameters() if self.irt_parameters else None
        }

class Test(db.Model):
    __tablename__ = 'test'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    test_type = db.Column(db.String(50), default='final_subject')
    subject_final_test_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True, index=True)
    module_intermediate_test_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=True, index=True)
    attempts = db.relationship("TestAttempt", backref="test", lazy='dynamic', cascade="all, delete-orphan")
    
    def __repr__(self): 
        return f'<Test {self.id}: {self.title} (Type: {self.test_type})>'

class TestAttempt(db.Model):
    __tablename__ = 'test_attempt'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete='CASCADE'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey("test.id", ondelete='CASCADE'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("questions.id", ondelete='CASCADE'), nullable=False)
    selected_option = db.Column(db.String(255))
    is_correct = db.Column(db.Boolean)
    attempt_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self): 
        return f'<TestAttempt User:{self.user_id} Test:{self.test_id} Q:{self.question_id} Correct:{self.is_correct}>'

class UserExamDate(db.Model):
    __tablename__ = 'user_exam_date'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exam_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    user = db.relationship('User', backref=db.backref('exam_dates', lazy=True))

# ========================================
# UTILITY FUNCTIONS
# ========================================

def create_sample_data():
    """Create sample data for testing (called from CLI)"""
    
    # Create learning path
    path = LearningPath(
        name="Dental Fundamentals",
        description="Basic dental knowledge and skills",
        order=1
    )
    db.session.add(path)
    db.session.flush()
    
    # Create subject
    subject = Subject(
        name="Oral Anatomy",
        description="Study of oral and dental anatomy",
        learning_path_id=path.id,
        order=1
    )
    db.session.add(subject)
    db.session.flush()
    
    # Create module
    module = Module(
        title="Tooth Structure",
        description="Understanding tooth anatomy and structure",
        subject_id=subject.id,
        order=1
    )
    db.session.add(module)
    db.session.flush()
    
    # Create lessons
    lessons_data = [
        {
            "title": "Crown Anatomy",
            "content": "The crown is the visible part of the tooth above the gum line...",
            "order": 1
        },
        {
            "title": "Root System",
            "content": "The root anchors the tooth to the jawbone...",
            "order": 2
        },
        {
            "title": "Enamel Properties",
            "content": "Enamel is the hardest substance in the human body...",
            "order": 3
        }
    ]
    
    for lesson_data in lessons_data:
        lesson = Lesson(
            title=lesson_data["title"],
            content=lesson_data["content"],
            module_id=module.id,
            order=lesson_data["order"]
        )
        db.session.add(lesson)
    
    # Create question category
    category = QuestionCategory(
        name="Oral Anatomy",
        description="Questions about oral and dental anatomy"
    )
    db.session.add(category)
    db.session.flush()
    
    # Create sample questions
    questions_data = [
        {
            "text": "What is the hardest substance in the human body?",
            "options": ["Bone", "Enamel", "Dentin", "Cementum"],
            "correct_answer": "Enamel",
            "explanation": "Tooth enamel is the hardest substance in the human body."
        },
        {
            "text": "How many permanent teeth does an adult typically have?",
            "options": ["28", "30", "32", "34"],
            "correct_answer": "32",
            "explanation": "Adults typically have 32 permanent teeth including wisdom teeth."
        }
    ]
    
    for q_data in questions_data:
        question = Question(
            text=q_data["text"],
            options=safe_json_dumps(q_data["options"]),
            correct_answer_index=q_data["options"].index(q_data["correct_answer"]),
            correct_answer_text=q_data["correct_answer"],
            explanation=q_data["explanation"],
            category=category.name,
            domain="Dental Anatomy",
            difficulty_level=3,
            image_url=None,
            tags=None,
            irt_difficulty=None,
            irt_discrimination=None,
            irt_guessing=None
        )
        db.session.add(question)
    
    db.session.commit()
    print("✅ Sample data created successfully!")
    
    return {
        'learning_paths': 1,
        'subjects': 1,
        'modules': 1,
        'lessons': len(lessons_data),
        'categories': 1,
        'questions': len(questions_data)
    }

# --- Virtual Patient Models ---
class VirtualPatientScenario(db.Model):
    """Модель для сценариев виртуальных пациентов"""
    __tablename__ = 'virtual_patient_scenario'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    difficulty = db.Column(db.String(20), default='medium')  # easy, medium, hard
    category = db.Column(db.String(50), nullable=True, index=True)  # diagnosis, treatment, emergency
    max_score = db.Column(db.Integer, default=100)
    is_premium = db.Column(db.Boolean, default=False)
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # JSON данные сценария
    scenario_data = db.Column(db.Text, nullable=False)
    
    # Отношения
    attempts = db.relationship("VirtualPatientAttempt", backref="scenario", lazy='dynamic', cascade="all, delete-orphan")
    
    @property
    def localized_data(self):
        """Возвращает данные сценария в зависимости от языка"""
        try:
            data = json.loads(self.scenario_data)
            # Возвращаем default данные для простоты
            return data.get('default', {})
        except (json.JSONDecodeError, TypeError):
            return {
                "patient_info": {
                    "name": "Пациент",
                    "age": 30,
                    "gender": "male",
                    "medical_history": "Данные недоступны"
                },
                "initial_state": {
                    "patient_statement": "Здравствуйте, доктор!",
                    "patient_emotion": "neutral",
                    "notes": "Начальное состояние"
                },
                "dialogue_nodes": [],
                "outcomes": {}
            }
    
    def __repr__(self):
        return f'<VirtualPatientScenario {self.title}>'

class VirtualPatientAttempt(db.Model):
    """Модель для попыток прохождения виртуальных пациентов"""
    __tablename__ = 'virtual_patient_attempt'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete='CASCADE'), nullable=False)
    scenario_id = db.Column(db.Integer, db.ForeignKey("virtual_patient_scenario.id", ondelete='CASCADE'), nullable=False)
    
    # Результаты
    score = db.Column(db.Integer, default=0)
    max_score = db.Column(db.Integer, default=100)
    completed = db.Column(db.Boolean, default=False)
    time_spent = db.Column(db.Float, default=0.0)  # в минутах
    
    # Временные метки
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # История диалога (JSON)
    dialogue_history = db.Column(db.Text, nullable=True)
    
    # Отношения
    user = db.relationship("User", backref=db.backref("virtual_patient_attempts", lazy='dynamic'))
    
    @property
    def percentage_score(self):
        """Возвращает процент от максимального балла"""
        if self.max_score > 0:
            return int((self.score / self.max_score) * 100)
        return 0
    
    def __repr__(self):
        return f'<VirtualPatientAttempt {self.user_id}-{self.scenario_id}>'

# --- Модели для системы обучения ---
class ContentCategory(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    icon = db.Column(db.String(50), default='folder')
    order = db.Column(db.Integer, default=0)
    subcategories = db.relationship('ContentSubcategory', backref='content_category', lazy='dynamic', cascade="all, delete-orphan")

class ContentSubcategory(db.Model):
    __tablename__ = 'subcategories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    icon = db.Column(db.String(50), default='bookmark')
    order = db.Column(db.Integer, default=0)
    topics = db.relationship('ContentTopic', backref='content_subcategory', lazy='dynamic', cascade="all, delete-orphan")

class ContentTopic(db.Model):
    __tablename__ = 'topics'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategories.id'), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)
    parent_topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=True)
    
    lessons = db.relationship('Lesson', 
                             foreign_keys="Lesson.topic_id",
                             backref='content_topic', 
                             lazy='dynamic', 
                             cascade="all, delete-orphan")
    
    subtopics = db.relationship('ContentTopic', backref=db.backref('parent', remote_side=[id]), lazy='dynamic', cascade="all, delete-orphan")
    __table_args__ = (db.UniqueConstraint('slug', 'subcategory_id', name='uc_topic_slug_subcategory'),) 

# ========================================
# DIGID AUTHENTICATION
# ========================================

class DigiDSession(db.Model):
    """Model for tracking DigiD authentication sessions"""
    __tablename__ = 'digid_session'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    
    # Session data
    session_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    bsn = db.Column(db.String(9), nullable=False)
    digid_username = db.Column(db.String(80), nullable=False)
    
    # Session status
    is_active = db.Column(db.Boolean, default=True)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_used = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def is_expired(self):
        """Check if session has expired"""
        expires_at = self.expires_at
        if expires_at is not None and expires_at.tzinfo is None:
            # Преобразуем naive datetime в UTC-aware
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return datetime.now(timezone.utc) > expires_at
    
    def refresh(self):
        """Refresh session by updating last_used timestamp"""
        self.last_used = datetime.now(timezone.utc)
    
    def deactivate(self):
        """Deactivate session"""
        self.is_active = False
    
    def __repr__(self):
        return f'<DigiDSession {self.session_id} for User {self.user_id}>'

# ========================================
# DATABASE MIGRATION FUNCTIONS
# ========================================

def upgrade_database_for_digid():
    """
    Upgrade existing database to support DigiD authentication.
    This function should be called during application startup or migration.
    """
    try:
        # Check if DigiD columns already exist
        inspector = db.inspect(db.engine)
        existing_columns = [col['name'] for col in inspector.get_columns('user')]
        
        # List of new columns to add
        new_columns = [
            'digid_username',
            'bsn', 
            'digid_verified',
            'created_via_digid'
        ]
        
        # Check which columns need to be added
        missing_columns = [col for col in new_columns if col not in existing_columns]
        
        if missing_columns:
            print(f"Adding DigiD columns to User table: {missing_columns}")
            
            # Add missing columns one by one
            for column_name in missing_columns:
                if column_name == 'digid_username':
                    db.engine.execute("ALTER TABLE user ADD COLUMN digid_username VARCHAR(80) UNIQUE")
                elif column_name == 'bsn':
                    db.engine.execute("ALTER TABLE user ADD COLUMN bsn VARCHAR(9) UNIQUE")
                elif column_name == 'digid_verified':
                    db.engine.execute("ALTER TABLE user ADD COLUMN digid_verified BOOLEAN DEFAULT FALSE")
                elif column_name == 'created_via_digid':
                    db.engine.execute("ALTER TABLE user ADD COLUMN created_via_digid BOOLEAN DEFAULT FALSE")
            
            # Make username and password_hash nullable if they aren't already
            try:
                db.engine.execute("ALTER TABLE user MODIFY COLUMN username VARCHAR(80) NULL")
                db.engine.execute("ALTER TABLE user MODIFY COLUMN password_hash VARCHAR(128) NULL")
            except Exception as e:
                print(f"Note: Could not modify existing columns (this is normal if already nullable): {e}")
            
            print("✅ DigiD columns added successfully")
        else:
            print("✅ DigiD columns already exist")
        
        # Check if DigiDSession table exists
        if 'digid_session' not in inspector.get_table_names():
            print("Creating DigiDSession table...")
            DigiDSession.__table__.create(db.engine)
            print("✅ DigiDSession table created successfully")
        else:
            print("✅ DigiDSession table already exists")
            
        return True
        
    except Exception as e:
        print(f"❌ Error upgrading database for DigiD: {e}")
        return False

def create_digid_user(digid_username, bsn, email, first_name=None, last_name=None):
    """
    Create a new user account via DigiD authentication.
    
    Args:
        digid_username (str): DigiD username
        bsn (str): Dutch Social Security Number
        email (str): User's email address
        first_name (str, optional): User's first name
        last_name (str, optional): User's last name
    
    Returns:
        User: The created user object or None if creation failed
    """
    try:
        # Check if user already exists
        existing_user = User.query.filter(
            (User.digid_username == digid_username) | 
            (User.bsn == bsn) | 
            (User.email == email)
        ).first()
        
        if existing_user:
            # Update existing user with DigiD info if needed
            if not existing_user.digid_verified:
                existing_user.digid_username = digid_username
                existing_user.bsn = bsn
                existing_user.digid_verified = True
                existing_user.created_via_digid = True
                if first_name:
                    existing_user.first_name = first_name
                if last_name:
                    existing_user.last_name = last_name
                db.session.commit()
                print(f"Updated existing user {existing_user.id} with DigiD authentication")
            return existing_user
        
        # Create new user
        user = User(
            email=email,
            digid_username=digid_username,
            bsn=bsn,
            digid_verified=True,
            created_via_digid=True,
            first_name=first_name,
            last_name=last_name,
            username=None,  # DigiD users don't need username
            password_hash=None  # DigiD users don't have password
        )
        
        db.session.add(user)
        db.session.commit()
        
        print(f"Created new DigiD user: {user.id} ({user.email})")
        return user
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating DigiD user: {e}")
        return None

# ========================================
# GAMIFICATION MODELS
# ========================================

class Achievement(db.Model):
    """Model for user achievements and badges"""
    __tablename__ = 'achievement'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    icon = db.Column(db.String(50), default='star')
    category = db.Column(db.String(50), default='general')  # learning, time, streak, special
    
    # Requirements for earning this achievement
    requirement_type = db.Column(db.String(50), nullable=False)  # lessons_completed, hours_studied, streak_days, etc.
    requirement_value = db.Column(db.Integer, nullable=False)
    
    # Display properties
    badge_color = db.Column(db.String(20), default='primary')
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user_achievements = db.relationship('UserAchievement', backref='achievement', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Achievement {self.name}>'

class UserAchievement(db.Model):
    """Model for tracking user earned achievements"""
    __tablename__ = 'user_achievement'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievement.id', ondelete='CASCADE'), nullable=False)
    
    earned_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('user_id', 'achievement_id', name='_user_achievement_uc'),)
    
    def __repr__(self):
        return f'<UserAchievement {self.user_id}:{self.achievement_id}>'

class UserActivity(db.Model):
    """Model for tracking daily user activity"""
    __tablename__ = 'user_activity'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    
    activity_date = db.Column(db.Date, nullable=False)
    lessons_completed = db.Column(db.Integer, default=0)
    time_spent = db.Column(db.Float, default=0.0)  # minutes
    xp_earned = db.Column(db.Integer, default=0)
    
    # Activity details
    modules_accessed = db.Column(db.Integer, default=0)
    tests_taken = db.Column(db.Integer, default=0)
    virtual_patients_completed = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Unique constraint
    __table_args__ = (db.UniqueConstraint('user_id', 'activity_date', name='_user_activity_date_uc'),)
    
    def __repr__(self):
        return f'<UserActivity {self.user_id}:{self.activity_date}>'

class UserStreak(db.Model):
    """Model for tracking user learning streaks"""
    __tablename__ = 'user_streak'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.Date, nullable=True)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Unique constraint - one streak record per user
    __table_args__ = (db.UniqueConstraint('user_id', name='_user_streak_uc'),)
    
    def update_streak(self, activity_date):
        """Update streak based on activity date"""
        from datetime import timedelta
        
        if self.last_activity_date is None:
            # First activity
            self.current_streak = 1
            self.longest_streak = 1
            self.last_activity_date = activity_date
        else:
            days_diff = (activity_date - self.last_activity_date).days
            
            if days_diff == 1:
                # Consecutive day
                self.current_streak += 1
                self.longest_streak = max(self.longest_streak, self.current_streak)
            elif days_diff == 0:
                # Same day, no change
                pass
            else:
                # Streak broken
                self.current_streak = 1
            
            self.last_activity_date = activity_date
    
    def __repr__(self):
        return f'<UserStreak {self.user_id}:{self.current_streak}>'

class UserReminder(db.Model):
    """Model for user reminders and deadlines"""
    __tablename__ = 'user_reminder'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    reminder_type = db.Column(db.String(50), default='general')  # exam, deadline, goal, general
    
    # Timing
    reminder_date = db.Column(db.DateTime, nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Related entities
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=True)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=True)
    
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<UserReminder {self.title}>'

# ========================================
# BI-TOETS DIAGNOSTIC TESTING MODELS
# ========================================

class BIGDomain(db.Model):
    """BI-toets domains based on ACTA 180 ECTS program - Updated Structure"""
    __tablename__ = 'big_domain'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(20), nullable=False, unique=True)  # e.g., 'THER', 'SURG', 'EMERGENCY'
    description = db.Column(db.Text, nullable=True)
    weight_percentage = db.Column(db.Float, nullable=False)  # ACTA weight
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # НОВЫЕ ПОЛЯ ДЛЯ РЕСТРУКТУРИЗАЦИИ
    category = db.Column(db.String(50), nullable=True, index=True)  # THEORETICAL, METHODOLOGY, PRACTICAL, CLINICAL
    exam_type = db.Column(db.String(50), nullable=True, index=True)  # multiple_choice, open_book, practical, case_study, interview
    is_critical = db.Column(db.Boolean, default=False, index=True)  # Критические домены для приоритета
    subcategories = db.Column(db.Text, nullable=True)  # JSON array of subcategories
    historical_questions = db.Column(db.Boolean, default=True)  # 80-90% повторяющихся вопросов
    open_book = db.Column(db.Boolean, default=False)  # Open Book экзамен
    
    # Relationships
    # Note: backref is defined in Question model
    
    # ОБНОВЛЕННЫЕ ДОМЕНЫ BI-TOETS (30 доменов)
    DOMAIN_CODES = {
        # ТЕОРЕТИЧЕСКИЕ ДОМЕНЫ (70% веса)
        'THER': 'Терапевтическая стоматология',
        'SURG': 'Хирургическая стоматология', 
        'PROTH': 'Ортопедическая стоматология',
        'PEDI': 'Детская стоматология',
        'PARO': 'Пародонтология',
        'ORTHO': 'Ортодонтия',
        'PREV': 'Профилактика',
        'ANATOMIE': 'Анатомия',
        'FYSIOLOGIE': 'Физиология',
        'PATHOLOGIE': 'Патология',
        'MICROBIOLOGIE': 'Микробиология',
        'MATERIAALKUNDE': 'Материаловедение',
        'RADIOLOGIE': 'Рентгенология',
        'ALGEMENE_GENEESKUNDE': 'Общая медицина',
        'EMERGENCY': 'Неотложная помощь',
        'SYSTEMIC': 'Системные заболевания',
        'PHARMACOLOGY': 'Фармакология',  # Объединено с FARMACOLOGIE
        'INFECTION': 'Инфекционный контроль',
        'SPECIAL': 'Специальные группы пациентов',
        'DIAGNOSIS': 'Диагностика',  # Объединено с DIAGNOSIS_SPECIAL
        'DUTCH': 'Голландская система здравоохранения',
        'PROFESSIONAL': 'Профессиональное развитие',
        'ETHIEK': 'Этика и право',
        
        # МЕТОДОЛОГИЯ (Open Book) - 10% веса
        'STATISTICS': 'Статистика и анализ данных',
        'RESEARCH_METHOD': 'Методология исследований',
        
        # ПРАКТИЧЕСКИЕ НАВЫКИ (Simodont) - 15% веса
        'PRACTICAL_SKILLS': 'Практические навыки',
        
        # КЛИНИЧЕСКИЕ НАВЫКИ - 5% веса
        'TREATMENT_PLANNING': 'Планирование лечения',
        'COMMUNICATION': 'Коммуникативные навыки'
    }
    
    @classmethod
    def initialize_domains(cls):
        """Инициализация всех доменов в базе данных - Обновленная структура"""
        
        # ОБНОВЛЕННЫЕ ВЕСА И КАТЕГОРИИ (30 доменов)
        domain_config = {
            # ТЕОРЕТИЧЕСКИЕ ДОМЕНЫ (70% веса)
            'THER': {'weight': 15.0, 'category': 'THEORETICAL', 'exam_type': 'multiple_choice', 'critical': True},
            'SURG': {'weight': 10.0, 'category': 'THEORETICAL', 'exam_type': 'multiple_choice', 'critical': True},
            'PROTH': {'weight': 8.0, 'category': 'THEORETICAL', 'exam_type': 'multiple_choice', 'critical': False},
            'PEDI': {'weight': 7.0, 'category': 'THEORETICAL', 'exam_type': 'multiple_choice', 'critical': False},
            'PARO': {'weight': 8.0, 'category': 'THEORETICAL', 'exam_type': 'multiple_choice', 'critical': False},
            'ORTHO': {'weight': 6.0, 'category': 'THEORETICAL', 'exam_type': 'multiple_choice', 'critical': False},
            'PREV': {'weight': 5.0, 'category': 'THEORETICAL', 'exam_type': 'multiple_choice', 'critical': False},
            'ANATOMIE': {'weight': 4.0, 'category': 'THEORETICAL', 'exam_type': 'multiple_choice', 'critical': False},
            'FYSIOLOGIE': {'weight': 4.0, 'category': 'THEORETICAL', 'exam_type': 'multiple_choice', 'critical': False},
            'PATHOLOGIE': {'weight': 5.0, 'category': 'THEORETICAL', 'exam_type': 'multiple_choice', 'critical': False},
            'MICROBIOLOGIE': {'weight': 3.0, 'category': 'THEORETICAL', 'exam_type': 'multiple_choice', 'critical': False},
            'MATERIAALKUNDE': {'weight': 3.0, 'category': 'THEORETICAL', 'exam_type': 'multiple_choice', 'critical': False},
            'RADIOLOGIE': {'weight': 4.0, 'category': 'THEORETICAL', 'exam_type': 'multiple_choice', 'critical': False},
            'ALGEMENE_GENEESKUNDE': {'weight': 2.0, 'category': 'THEORETICAL', 'exam_type': 'multiple_choice', 'critical': False},
            'EMERGENCY': {'weight': 10.0, 'category': 'THEORETICAL', 'exam_type': 'multiple_choice', 'critical': True},
            'SYSTEMIC': {'weight': 7.0, 'category': 'THEORETICAL', 'exam_type': 'multiple_choice', 'critical': True},
            'PHARMACOLOGY': {'weight': 8.0, 'category': 'THEORETICAL', 'exam_type': 'multiple_choice', 'critical': True},
            'INFECTION': {'weight': 5.0, 'category': 'THEORETICAL', 'exam_type': 'multiple_choice', 'critical': False},
            'SPECIAL': {'weight': 4.0, 'category': 'THEORETICAL', 'exam_type': 'multiple_choice', 'critical': False},
            'DIAGNOSIS': {'weight': 10.0, 'category': 'THEORETICAL', 'exam_type': 'multiple_choice', 'critical': True},
            'DUTCH': {'weight': 3.0, 'category': 'THEORETICAL', 'exam_type': 'multiple_choice', 'critical': False},
            'PROFESSIONAL': {'weight': 2.0, 'category': 'THEORETICAL', 'exam_type': 'multiple_choice', 'critical': False},
            'ETHIEK': {'weight': 3.0, 'category': 'CLINICAL', 'exam_type': 'case_study', 'critical': False},
            
            # МЕТОДОЛОГИЯ (Open Book) - 10% веса
            'STATISTICS': {
                'weight': 6.0, 
                'category': 'METHODOLOGY', 
                'exam_type': 'open_book', 
                'critical': True,
                'open_book': True,
                'subcategories': ['descriptive', 'inferential', 'clinical_trials']
            },
            'RESEARCH_METHOD': {
                'weight': 6.0, 
                'category': 'METHODOLOGY', 
                'exam_type': 'open_book', 
                'critical': True,
                'open_book': True,
                'subcategories': ['study_design', 'biostatistics', 'evidence_based']
            },
            
            # ПРАКТИЧЕСКИЕ НАВЫКИ (Simodont) - 15% веса
            'PRACTICAL_SKILLS': {
                'weight': 15.0, 
                'category': 'PRACTICAL', 
                'exam_type': 'practical', 
                'critical': True,
                'subcategories': ['manual_skills', 'caries_excavation', 'endo_prep', 'crown_prep', 'gebits_reinigung']
            },
            
            # КЛИНИЧЕСКИЕ НАВЫКИ - 5% веса
            'TREATMENT_PLANNING': {
                'weight': 12.0, 
                'category': 'CLINICAL', 
                'exam_type': 'case_study', 
                'critical': True,
                'subcategories': ['comprehensive', 'endodontic', 'trauma_resorption', 'cariology_pediatric']
            },
            'COMMUNICATION': {
                'weight': 8.0, 
                'category': 'CLINICAL', 
                'exam_type': 'interview', 
                'critical': True,
                'subcategories': ['intake_gesprek', 'patient_interaction', 'dutch_medical']
            }
        }
        
        for code, name in cls.DOMAIN_CODES.items():
            config = domain_config.get(code, {})
            domain = cls.query.filter_by(code=code).first()
            
            if not domain:
                domain = cls(
                    code=code,
                    name=name,
                    weight_percentage=config.get('weight', 3.0),
                    category=config.get('category', 'THEORETICAL'),
                    exam_type=config.get('exam_type', 'multiple_choice'),
                    is_critical=config.get('critical', False),
                    open_book=config.get('open_book', False),
                    subcategories=safe_json_dumps(config.get('subcategories', [])),
                    is_active=True
                )
                db.session.add(domain)
            else:
                # Обновляем существующие домены
                domain.weight_percentage = config.get('weight', domain.weight_percentage)
                domain.category = config.get('category', domain.category)
                domain.exam_type = config.get('exam_type', domain.exam_type)
                domain.is_critical = config.get('critical', domain.is_critical)
                domain.open_book = config.get('open_book', domain.open_book)
                domain.subcategories = safe_json_dumps(config.get('subcategories', []))
        
        db.session.commit()
    
    def to_dict(self):
        """Преобразовать домен в словарь"""
        return {
            'id': self.id,
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'weight_percentage': self.weight_percentage,
            'order': self.order,
            'is_active': self.is_active,
            'category': self.category,
            'exam_type': self.exam_type,
            'is_critical': self.is_critical,
            'open_book': self.open_book,
            'subcategories': json.loads(self.subcategories) if self.subcategories else [],
            'questions_count': self.questions.count()
        }
    
    def __repr__(self):
        return f'<BIGDomain {self.code}: {self.name} ({self.weight_percentage}%)>'

class IRTParameters(db.Model):
    """IRT parameters for 3PL model (difficulty, discrimination, guessing)"""
    __tablename__ = 'irt_parameters'
    
    id = db.Column(db.Integer, primary_key=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False, unique=True)
    
    # 3PL Model Parameters
    difficulty = db.Column(db.Float, nullable=False, index=True)  # b-parameter (location)
    discrimination = db.Column(db.Float, nullable=False, index=True)  # a-parameter (slope)
    guessing = db.Column(db.Float, default=0.25, index=True)  # c-parameter (lower asymptote)
    
    # Calibration data
    calibration_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    calibration_sample_size = db.Column(db.Integer, nullable=True)
    reliability = db.Column(db.Float, nullable=True)  # Item reliability
    
    # Standard errors
    se_difficulty = db.Column(db.Float, nullable=True)
    se_discrimination = db.Column(db.Float, nullable=True)
    se_guessing = db.Column(db.Float, nullable=True)
    
    # Fit statistics
    infit = db.Column(db.Float, nullable=True)  # Weighted mean square
    outfit = db.Column(db.Float, nullable=True)  # Unweighted mean square
    
    # Relationships
    # question = db.relationship('Question', foreign_keys=[question_id], backref='irt_parameters', uselist=False)
    
    # Индексы для оптимизации запросов
    __table_args__ = (
        db.Index('idx_irt_difficulty_range', 'difficulty'),
        db.Index('idx_irt_discrimination_range', 'discrimination'),
        db.Index('idx_irt_question_domain', 'question_id'),
    )
    
    def validate_parameters(self):
        """
        Validate IRT parameters according to 3PL model constraints
        
        Raises:
            ValueError: If any parameter is outside valid range
        """
        # Validate difficulty (b-parameter): typically [-4.0, 4.0]
        if not (-4.0 <= self.difficulty <= 4.0):
            raise ValueError(f"IRT difficulty must be between -4.0 and 4.0, got {self.difficulty}")
        
        # Validate discrimination (a-parameter): typically [0.1, 4.0]
        if not (0.1 <= self.discrimination <= 4.0):
            raise ValueError(f"IRT discrimination must be between 0.1 and 4.0, got {self.discrimination}")
        
        # Validate guessing (c-parameter): typically [0.0, 0.5]
        if not (0.0 <= self.guessing <= 0.5):
            raise ValueError(f"IRT guessing must be between 0.0 and 0.5, got {self.guessing}")
    
    def set_parameters(self, difficulty: float, discrimination: float, guessing: float):
        """
        Set IRT parameters with validation
        
        Args:
            difficulty: b-parameter (item difficulty)
            discrimination: a-parameter (item discrimination)
            guessing: c-parameter (guessing parameter)
        """
        self.difficulty = difficulty
        self.discrimination = discrimination
        self.guessing = guessing
        
        # Validate parameters
        self.validate_parameters()
    
    def get_parameters(self) -> dict:
        """
        Get IRT parameters as dictionary with validation
        
        Returns:
            Dict with IRT parameters
        """
        self.validate_parameters()
        
        return {
            'difficulty': self.difficulty,
            'discrimination': self.discrimination,
            'guessing': self.guessing
        }
    
    def get_3pl_probability(self, theta):
        """Calculate probability of correct response using 3PL model"""
        import math
        a, b, c = self.discrimination, self.difficulty, self.guessing
        exponent = a * (theta - b)
        p_star = 1 / (1 + math.exp(-exponent))
        return c + (1 - c) * p_star
    
    def get_information(self, theta):
        """Calculate item information at ability level theta"""
        p = self.get_3pl_probability(theta)
        a, c = self.discrimination, self.guessing
        return (a**2) * p * (1 - p) * ((1 - c)**2) / ((p - c)**2)
    
    def __repr__(self):
        return f'<IRTParameters Q{self.question_id}: a={self.discrimination:.3f}, b={self.difficulty:.3f}, c={self.guessing:.3f}>'

class DiagnosticSession(db.Model):
    """Session for adaptive diagnostic testing"""
    __tablename__ = 'diagnostic_session'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    
    # Session configuration
    session_type = db.Column(db.String(50), nullable=False)  # 'diagnostic', 'adaptive', 'practice'
    test_length = db.Column(db.Integer, nullable=True)  # Max questions (null for adaptive)
    time_limit = db.Column(db.Integer, nullable=True)  # Minutes (null for no limit)
    
    # Current state
    current_ability = db.Column(db.Float, default=0.0)  # Current theta estimate
    ability_se = db.Column(db.Float, default=1.0)  # Standard error of ability
    questions_answered = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    current_question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=True)
    
    # Session data (JSON)
    session_data = db.Column(db.Text, nullable=True)  # JSON with response history
    ability_history = db.Column(db.Text, nullable=True)  # JSON with ability progression
    
    # Status
    status = db.Column(db.String(20), default='active')  # active, completed, paused, terminated
    termination_reason = db.Column(db.String(50), nullable=True)  # max_questions, time_limit, precision_reached
    
    # IP address for session tracking
    ip_address = db.Column(db.String(45), nullable=True)
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime, nullable=True)
    last_activity = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = db.relationship('User', backref='diagnostic_sessions')
    responses = db.relationship('DiagnosticResponse', backref='session', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_session_data(self):
        """Get session data as dict"""
        if self.session_data:
            try:
                return json.loads(self.session_data)
            except:
                pass
        return {}
    
    def set_session_data(self, data):
        """Set session data from dict"""
        self.session_data = safe_json_dumps(data)
    
    def get_ability_history(self):
        """Get ability progression as list"""
        if self.ability_history:
            try:
                return json.loads(self.ability_history)
            except:
                pass
        return []
    
    def add_ability_estimate(self, ability, se, question_id):
        """Add ability estimate to history"""
        history = self.get_ability_history()
        history.append({
            'ability': ability,
            'se': se,
            'question_id': question_id,
            'timestamp': datetime.now(timezone.utc).isoformat()
        })
        self.ability_history = safe_json_dumps(history)
    
    def get_accuracy(self):
        """Get current accuracy"""
        if self.questions_answered > 0:
            return self.correct_answers / self.questions_answered
        return 0.0
    
    def is_precise_enough(self, min_se=0.3):
        """Check if ability estimate is precise enough"""
        return self.ability_se <= min_se
    
    
        # Безопасная сериализация datetime объектов
        def safe_datetime_serialize(obj):
            if hasattr(obj, 'isoformat'):
                return obj.isoformat()
            return obj
        
    def generate_results(self):
        """Generate comprehensive diagnostic results"""
        from utils.irt_engine import IRTEngine
        
        # Initialize IRT engine for this session
        irt_engine = IRTEngine(self)
        
        # Get detailed domain statistics with real percentages
        domain_stats = irt_engine.get_domain_detailed_statistics()
        
        # Calculate domain abilities (percentages)
        domain_abilities = {}
        weak_domains = []
        strong_domains = []
        
        for domain_code, stats in domain_stats.items():
            if stats['has_data']:
                # Use the actual accuracy percentage from domain statistics
                ability_percentage = stats['accuracy_percentage']
                domain_abilities[domain_code] = ability_percentage / 100.0  # Convert to decimal
                
                # Classify domains based on percentage
                if ability_percentage < 50:  # Weak domain (less than 50%)
                    weak_domains.append(domain_code)
                elif ability_percentage >= 80:  # Strong domain (80% or higher)
                    strong_domains.append(domain_code)
            else:
                # No data for this domain
                domain_abilities[domain_code] = None
        
        # Calculate overall statistics
        accuracy = self.get_accuracy()
        avg_response_time = 0
        if self.questions_answered > 0:
            avg_response_time = db.session.query(
                db.func.avg(DiagnosticResponse.response_time)
            ).filter_by(session_id=self.id).scalar() or 0
        
        # Convert IRT ability to readiness percentage
        current_ability_theta = self.current_ability
        readiness_percentage = irt_engine.convert_irt_ability_to_readiness_percentage(current_ability_theta)
        performance_percentage = irt_engine.convert_irt_ability_to_performance_percentage(current_ability_theta)
        
        # Calculate target ability and study weeks
        target_ability = irt_engine.calculate_target_ability()
        study_hours_per_week = 20.0  # Default study hours
        weeks_to_target = irt_engine.calculate_weeks_to_target(
            readiness_percentage, target_ability, study_hours_per_week
        )
        
        # Generate results dictionary
        results = {
            'session_id': self.id,
            'user_id': self.user_id,
            'session_type': self.session_type,
            'status': self.status,
            
            # Ability estimates (properly converted)
            'final_ability': current_ability_theta,
            'ability_se': self.ability_se,
            'readiness_percentage': round(readiness_percentage, 1),
            'performance_percentage': round(performance_percentage, 1),
            'target_ability': target_ability,
            'weeks_to_target': weeks_to_target,
            'study_hours_per_week': study_hours_per_week,
            'confidence_interval': irt_engine.get_confidence_interval(),
            
            # Performance statistics
            'questions_answered': self.questions_answered,
            'correct_answers': self.correct_answers,
            'accuracy': accuracy,
            'avg_response_time': avg_response_time,
            
            # Domain analysis with real percentages
            'domain_abilities': domain_abilities,
            'domain_statistics': domain_stats,  # Detailed stats for each domain
            'weak_domains': weak_domains,
            'strong_domains': strong_domains,
            
            # Timing
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'duration_minutes': 0
        }
        
        # Calculate duration
        if self.started_at and self.completed_at:
            duration = self.completed_at - self.started_at
            results['duration_minutes'] = duration.total_seconds() / 60
        
        return results
    
    @classmethod
    def create_session(cls, user_id, session_type, ip_address=None):
        """Create a new diagnostic session"""
        session = cls(
            user_id=user_id,
            session_type=session_type,
            status='active',
            started_at=datetime.now(timezone.utc)
        )
        db.session.add(session)
        db.session.commit()
        return session
    
    def record_response(self, question_id, selected_option, response_time=None):
        """Record a response to a question"""
        # Get question to check if answer is correct
        question = Question.query.get(question_id)
        if not question:
            raise ValueError(f"Question {question_id} not found")
        
        # Prepare selected_str for response record
        selected_str = str(selected_option).strip()
        
        # Check if answer is correct using the question's check_answer method
        # selected_option should be the index of the selected option
        try:
            selected_index = int(selected_option)
            is_correct = question.check_answer(selected_index)
        except (ValueError, TypeError):
            # If selected_option is not a valid index, compare with correct_answer_text
            correct_str = str(question.correct_answer_text).strip()
            is_correct = selected_str == correct_str
        
        # Create response record
        response = DiagnosticResponse(
            session_id=self.id,
            question_id=question_id,
            selected_answer=selected_str,
            is_correct=is_correct,
            response_time=response_time
        )
        db.session.add(response)
        
        # Update session statistics
        self.questions_answered += 1
        if is_correct:
            self.correct_answers += 1
        
        # Update last activity
        self.last_activity = datetime.now(timezone.utc)
        
        # Update ability estimate using IRT
        self._update_ability_estimate()
        
        db.session.commit()
        return response
    
    def _update_ability_estimate(self):
        """Update ability estimate using IRT algorithm"""
        from utils.irt_engine import IRTEngine
        
        # Get all responses for this session
        responses = self.responses.all()
        
        if not responses:
            return
        
        # Prepare response data for IRT engine
        response_data = []
        for resp in responses:
            question = resp.question
            # IRT parameters are stored directly in Question model
            
            response_data.append({
                'question_id': resp.question_id,
                'is_correct': resp.is_correct,
                'irt_params': {
                    'difficulty': question.irt_difficulty,
                    'discrimination': question.irt_discrimination,
                    'guessing': question.irt_guessing
                }
            })
        
        if response_data:
            # Use IRT engine to estimate ability
            irt_engine = IRTEngine()
            theta, se = irt_engine.estimate_ability(response_data)
            
            # Update session with new estimates
            self.current_ability = theta
            self.ability_se = se
            
            # Add to ability history
            self.add_ability_estimate(theta, se, responses[-1].question_id)
    
    def get_responses_dict(self):
        """Получить responses как список словарей (JSON-safe)"""
        return [response.to_dict() for response in self.responses.all()]
    
    def __repr__(self):
        return f'<DiagnosticSession {self.id}: User{self.user_id} {self.session_type} θ={self.current_ability:.3f}±{self.ability_se:.3f}>'

class DiagnosticResponse(db.Model, JSONSerializableMixin):
    """Individual response in diagnostic session"""
    __tablename__ = 'diagnostic_response'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('diagnostic_session.id', ondelete='CASCADE'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    
    # Response data
    selected_answer = db.Column(db.String(255), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    response_time = db.Column(db.Float, nullable=True)  # Seconds
    confidence_level = db.Column(db.Integer, nullable=True)  # 1-5 scale
    
    # IRT data
    ability_before = db.Column(db.Float, nullable=True)  # θ before this question
    ability_after = db.Column(db.Float, nullable=True)   # θ after this question
    se_before = db.Column(db.Float, nullable=True)       # SE before this question
    se_after = db.Column(db.Float, nullable=True)        # SE after this question
    
    # Item information
    item_information = db.Column(db.Float, nullable=True)  # Information provided by this item
    expected_response = db.Column(db.Float, nullable=True)  # Expected probability of correct response
    
    # Timestamp
    responded_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    question = db.relationship('Question')
    
    def to_dict(self):
        """Безопасная сериализация в словарь с обработкой datetime"""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'question_id': self.question_id,
            'selected_answer': self.selected_answer,
            'is_correct': self.is_correct,
            'response_time': self.response_time,
            'confidence_level': self.confidence_level,
            'ability_before': self.ability_before,
            'ability_after': self.ability_after,
            'se_before': self.se_before,
            'se_after': self.se_after,
            'item_information': self.item_information,
            'expected_response': self.expected_response,
            'responded_at': self.responded_at.isoformat() if self.responded_at else None
        }
    
    def __repr__(self):
        return f'<DiagnosticResponse Session{self.session_id} Q{self.question_id} {"✓" if self.is_correct else "✗"}>'

class PersonalLearningPlan(db.Model, JSONSerializableMixin):
    """Personalized learning plan based on diagnostic results"""
    __tablename__ = 'personal_learning_plan'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    
    # Plan configuration
    exam_date = db.Column(db.Date, nullable=True)
    start_date = db.Column(db.Date, nullable=True)  # Дата начала обучения
    end_date = db.Column(db.Date, nullable=True)    # Дата окончания обучения
    intensity = db.Column(db.String(20), default='moderate')  # light, moderate, intensive
    study_time = db.Column(db.String(20), default='afternoon')  # morning, afternoon, evening, flexible
    diagnostic_session_id = db.Column(db.Integer, db.ForeignKey('diagnostic_session.id'), nullable=True)
    target_ability = db.Column(db.Float, default=0.5)  # Target theta for exam readiness
    study_hours_per_week = db.Column(db.Float, default=20.0)
    
    # Current status
    current_ability = db.Column(db.Float, default=0.0)
    overall_progress = db.Column(db.Float, default=0.0)  # 0-100%
    estimated_readiness = db.Column(db.Float, nullable=True)  # Probability of passing
    
    # Domain analysis (JSON)
    domain_analysis = db.Column(db.Text, nullable=True)  # JSON with domain-specific data
    weak_domains = db.Column(db.Text, nullable=True)     # JSON list of weak domains
    strong_domains = db.Column(db.Text, nullable=True)   # JSON list of strong domains
    
    # Study schedule (JSON)
    study_schedule = db.Column(db.Text, nullable=True)   # JSON with weekly schedule
    milestones = db.Column(db.Text, nullable=True)       # JSON with milestone dates
    
    # Status
    status = db.Column(db.String(20), default='active')  # active, completed, paused
    last_updated = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = db.relationship('User', backref='learning_plans')
    diagnostic_session = db.relationship('DiagnosticSession', backref='learning_plans')
    study_sessions = db.relationship('StudySession', backref='learning_plan', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_domain_analysis(self):
        """Get domain analysis as dict"""
        if self.domain_analysis:
            try:
                return json.loads(self.domain_analysis)
            except:
                pass
        return {}
    
    def set_domain_analysis(self, analysis):
        """Set domain analysis from dict"""
        self.domain_analysis = safe_json_dumps(analysis)
    
    def get_weak_domains(self):
        """Get weak domains as list"""
        if self.weak_domains:
            try:
                return json.loads(self.weak_domains)
            except:
                pass
        return []
    
    def get_weak_domain_names(self):
        """Get weak domain names instead of codes"""
        domain_codes = self.get_weak_domains()
        domain_names = []
        
        for code in domain_codes:
            domain = BIGDomain.query.filter_by(code=code).first()
            if domain:
                domain_names.append(domain.name)
            else:
                domain_names.append(code)  # Fallback to code if domain not found
        
        return domain_names
    
    def set_weak_domains(self, domains):
        """Set weak domains from list"""
        self.weak_domains = safe_json_dumps(domains)
    
    def get_strong_domains(self):
        """Get strong domains as list"""
        if self.strong_domains:
            try:
                return json.loads(self.strong_domains)
            except:
                pass
        return []
    
    def get_strong_domain_names(self):
        """Get strong domain names instead of codes"""
        domain_codes = self.get_strong_domains()
        domain_names = []
        
        for code in domain_codes:
            domain = BIGDomain.query.filter_by(code=code).first()
            if domain:
                domain_names.append(domain.name)
            else:
                domain_names.append(code)  # Fallback to code if domain not found
        
        return domain_names
    
    def set_strong_domains(self, domains):
        """Set strong domains from list"""
        self.strong_domains = safe_json_dumps(domains)
    
    def get_study_schedule(self):
        """Get study schedule as dict"""
        if self.study_schedule:
            try:
                return json.loads(self.study_schedule)
            except:
                pass
        return {}
    
    def set_study_schedule(self, schedule):
        """Set study schedule from dict"""
        self.study_schedule = safe_json_dumps(schedule)
    
    def get_milestones(self):
        """Get real milestones based on user progress"""
        from utils.learning_plan_generator import LearningPlanGenerator
        
        # Создаем генератор планов
        generator = LearningPlanGenerator(self.user_id)
        
        # Генерируем реальные вехи на основе прогресса
        real_milestones = generator._create_milestones(self.exam_date)
        
        # Если вех нет, возвращаем пустой список
        if not real_milestones:
            return []
        
        return real_milestones
    
    def set_milestones(self, milestones):
        """Set milestones from list"""
        self.milestones = safe_json_dumps(milestones)
    
    def calculate_readiness(self):
        """Calculate probability of passing exam"""
        if self.current_ability >= self.target_ability:
            return min(0.95, 0.7 + (self.current_ability - self.target_ability) * 0.5)
        else:
            return max(0.05, 0.3 + (self.current_ability / self.target_ability) * 0.4)
    
    def __repr__(self):
        return f'<PersonalLearningPlan User{self.user_id}: θ={self.current_ability:.3f} Progress={self.overall_progress:.1f}%>'

class StudySession(db.Model):
    """Individual study session within learning plan"""
    __tablename__ = 'study_session'
    
    id = db.Column(db.Integer, primary_key=True)
    learning_plan_id = db.Column(db.Integer, db.ForeignKey('personal_learning_plan.id', ondelete='CASCADE'), nullable=False)
    
    # Session details
    session_type = db.Column(db.String(50), nullable=False)  # 'theory', 'practice', 'test', 'review'
    domain_id = db.Column(db.Integer, db.ForeignKey('big_domain.id'), nullable=True)
    
    # Content
    content_ids = db.Column(db.Text, nullable=True)  # JSON list of lesson/module IDs
    questions_answered = db.Column(db.Integer, default=0)
    correct_answers = db.Column(db.Integer, default=0)
    
    # Timing
    planned_duration = db.Column(db.Integer, nullable=True)  # Minutes
    actual_duration = db.Column(db.Integer, nullable=True)   # Minutes
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Progress
    progress_percent = db.Column(db.Float, default=0.0)
    difficulty_level = db.Column(db.Float, nullable=True)  # Average difficulty of content
    
    # Status
    status = db.Column(db.String(20), default='planned')  # planned, in_progress, completed, skipped
    
    # Relationships
    domain = db.relationship('BIGDomain')
    
    def get_content_ids(self):
        """Get content IDs as list"""
        if self.content_ids:
            try:
                return json.loads(self.content_ids)
            except:
                pass
        return []
    
    def set_content_ids(self, ids):
        """Set content IDs from list"""
        self.content_ids = safe_json_dumps(ids)
    
    def get_accuracy(self):
        """Get session accuracy"""
        if self.questions_answered > 0:
            return self.correct_answers / self.questions_answered
        return 0.0
    
    def __repr__(self):
        return f'<StudySession {self.session_type}: {self.progress_percent:.1f}% {"✓" if self.status == "completed" else "⏳"}>'

# ========================================
# EXTEND EXISTING MODELS
# ========================================

# Add new fields to existing Question model
# УДАЛЕНО: Дублирующие определения полей Question (они уже есть в классе)

# Add new fields to existing Test model
Test.test_format = db.Column(db.String(50), default='standard')  # standard, adaptive, diagnostic
Test.irt_enabled = db.Column(db.Boolean, default=False)
Test.min_questions = db.Column(db.Integer, nullable=True)
Test.max_questions = db.Column(db.Integer, nullable=True)
Test.precision_threshold = db.Column(db.Float, default=0.3)  # SE threshold for adaptive tests
Test.passing_score = db.Column(db.Float, nullable=True)  # Passing threshold

# Add new fields to existing TestAttempt model
TestAttempt.ability_estimate = db.Column(db.Float, nullable=True)  # θ estimate
TestAttempt.ability_se = db.Column(db.Float, nullable=True)  # Standard error
TestAttempt.response_time = db.Column(db.Float, nullable=True)  # Seconds
TestAttempt.difficulty_rating = db.Column(db.Integer, nullable=True)  # User's difficulty rating 1-5

class ContentDomainMapping(db.Model):
    """Связь контента (уроков, модулей) с доменами BIG"""
    __tablename__ = 'content_domain_mapping'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Связи с контентом
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=True)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True)
    
    # Связь с доменом BIG
    domain_id = db.Column(db.Integer, db.ForeignKey('big_domain.id'), nullable=False)
    
    # Релевантность контента для домена (0.0 - 1.0)
    relevance_score = db.Column(db.Float, default=0.5)
    
    # Тип связи
    relationship_type = db.Column(db.String(50), default='primary')  # primary, secondary, related
    
    # Метаданные
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Relationships
    lesson = db.relationship('Lesson', backref='domain_mappings')
    module = db.relationship('Module', backref='domain_mappings')
    subject = db.relationship('Subject', backref='domain_mappings')
    domain = db.relationship('BIGDomain', backref='content_mappings')
    
    def __repr__(self):
        content_type = 'Lesson' if self.lesson_id else 'Module' if self.module_id else 'Subject'
        content_id = self.lesson_id or self.module_id or self.subject_id
        return f'<ContentDomainMapping {content_type}:{content_id} -> {self.domain.name}:{self.relevance_score}>'

# Модели для системы промежуточного тестирования

class TestSession(db.Model):
    """Сессия промежуточного тестирования"""
    __tablename__ = 'test_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    test_type = db.Column(db.String(50), default='adaptive')  # adaptive, standard, practice
    difficulty = db.Column(db.String(20), default='medium')  # easy, medium, hard
    total_questions = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, default=0)
    score = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='in_progress')  # in_progress, completed, abandoned
    session_data = db.Column(db.Text)  # JSON данные сессии
    started_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime)
    
    # Связи
    user = db.relationship('User', backref='test_sessions')
    module = db.relationship('Module', backref='test_sessions')
    results = db.relationship('TestResult', backref='session', cascade='all, delete-orphan')
    
    def set_session_data(self, data: Dict):
        """Сохраняет данные сессии в JSON формате"""
        self.session_data = safe_json_dumps(data, ensure_ascii=False)
    
    def get_session_data(self) -> Dict:
        """Получает данные сессии из JSON формата"""
        if self.session_data:
            return json.loads(self.session_data)
        return {}

class TestResult(db.Model):
    """Результат промежуточного теста"""
    __tablename__ = 'test_results'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    test_session_id = db.Column(db.Integer, db.ForeignKey('test_sessions.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=False)
    score = db.Column(db.Float, nullable=False)
    correct_answers = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    test_type = db.Column(db.String(50), default='adaptive')
    difficulty = db.Column(db.String(20), default='medium')
    time_spent = db.Column(db.Integer, default=0)  # в секундах
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    
    # Связи
    user = db.relationship('User', backref='test_results')
    module = db.relationship('Module', backref='test_results')
    
    @property
    def percentage_score(self) -> float:
        """Возвращает процент правильных ответов"""
        return (self.correct_answers / self.total_questions * 100) if self.total_questions > 0 else 0
    
    @property
    def performance_level(self) -> str:
        """Возвращает уровень производительности"""
        if self.percentage_score >= 90:
            return 'excellent'
        elif self.percentage_score >= 80:
            return 'good'
        elif self.percentage_score >= 70:
            return 'satisfactory'
        elif self.percentage_score >= 60:
            return 'needs_improvement'
        else:
            return 'poor'

class UserLearningProgress(db.Model):
    __tablename__ = 'user_learning_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    learning_path_id = db.Column(db.String(50), db.ForeignKey('learning_path.id'), nullable=False)
    
    # Прогресс
    progress_percentage = db.Column(db.Float, default=0.0)  # 0-100%
    completed_modules = db.Column(db.JSON, default=list)  # Список завершенных модулей
    current_module = db.Column(db.String(50))  # Текущий модуль
    
    # Время
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Статистика
    total_time_spent = db.Column(db.Integer, default=0)  # В минутах
    lessons_completed = db.Column(db.Integer, default=0)
    tests_passed = db.Column(db.Integer, default=0)
    
    # Метаданные
    notes = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    
    # Связи
    user = db.relationship('User', backref='learning_progress')
    
    def __repr__(self):
        return f'<UserLearningProgress {self.user_id}:{self.learning_path_id} - {self.progress_percentage}%>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'learning_path_id': self.learning_path_id,
            'progress_percentage': self.progress_percentage,
            'completed_modules': self.completed_modules or [],
            'current_module': self.current_module,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'last_accessed': self.last_accessed.isoformat() if self.last_accessed else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'total_time_spent': self.total_time_spent,
            'lessons_completed': self.lessons_completed,
            'tests_passed': self.tests_passed,
            'is_active': self.is_active
        }
    
    def update_progress(self, module_id=None, time_spent=0):
        """Обновить прогресс пользователя"""
        self.last_accessed = datetime.utcnow()
        self.total_time_spent += time_spent
        
        if module_id and module_id not in (self.completed_modules or []):
            if not self.completed_modules:
                self.completed_modules = []
            self.completed_modules.append(module_id)
        
        # Рассчитать процент завершения
        if self.learning_path:
            total_modules = len(self.learning_path.modules or [])
            if total_modules > 0:
                self.progress_percentage = (len(self.completed_modules or []) / total_modules) * 100
        
        # Проверить завершение
        if self.progress_percentage >= 100 and not self.completed_at:
            self.completed_at = datetime.utcnow()
    
    def is_completed(self):
        """Проверить, завершен ли путь"""
        return self.progress_percentage >= 100
    
    def get_remaining_modules(self):
        """Получить оставшиеся модули"""
        if not self.learning_path or not self.learning_path.modules:
            return []
        
        completed = set(self.completed_modules or [])
        all_modules = [m['id'] for m in self.learning_path.modules]
        return [m for m in all_modules if m not in completed]
    
    def get_next_module(self):
        """Получить следующий модуль для изучения"""
        remaining = self.get_remaining_modules()
        return remaining[0] if remaining else None

# Добавляем методы к существующей модели User
def get_path_progress(self, path_id):
    """Получить прогресс по конкретному пути"""
    return UserLearningProgress.query.filter_by(
        user_id=self.id,
        learning_path_id=path_id
    ).first()

def get_all_path_progress(self):
    """Получить прогресс по всем путям"""
    progress_records = UserLearningProgress.query.filter_by(
        user_id=self.id
    ).all()
    
    return {record.learning_path_id: record for record in progress_records}

def get_completed_paths(self):
    """Получить завершенные пути обучения"""
    return UserLearningProgress.query.filter_by(
        user_id=self.id,
        progress_percentage=100
    ).all()

def get_active_paths(self):
    """Получить активные пути обучения"""
    return UserLearningProgress.query.filter_by(
        user_id=self.id,
        is_active=True
    ).filter(UserLearningProgress.progress_percentage < 100).all()

def get_bi_toets_readiness(self):
    """Рассчитать готовность к BI-toets"""
    all_progress = self.get_all_path_progress()
    
    # Веса компонентов
    component_weights = {
        'THEORETICAL': 70,
        'METHODOLOGY': 10,
        'PRACTICAL': 15,
        'CLINICAL': 5
    }
    
    total_score = 0
    component_scores = {}
    
    for component, weight in component_weights.items():
        component_paths = LearningPath.get_by_component(component)
        component_total = 0
        component_completed = 0
        
        for path in component_paths:
            progress = all_progress.get(path.id)
            if progress:
                component_total += path.exam_weight
                component_completed += path.exam_weight * (progress.progress_percentage / 100)
        
        if component_total > 0:
            component_score = (component_completed / component_total) * weight
            component_scores[component] = component_score
            total_score += component_score
    
    return {
        'total_score': total_score,
        'component_scores': component_scores,
        'readiness_level': self._get_readiness_level(total_score)
    }

def _get_readiness_level(self, score):
    """Определить уровень готовности"""
    if score >= 85:
        return 'excellent'
    elif score >= 70:
        return 'good'
    elif score >= 50:
        return 'fair'
    else:
        return 'needs_improvement'

# ... existing code ...
        return 'needs_improvement'

# ... existing code ...