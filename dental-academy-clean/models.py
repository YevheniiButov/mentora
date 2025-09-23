# models.py - Essential Database Models (Clean Version)
# Only critical models for core functionality

import json
import numpy as np
from datetime import datetime, timedelta, timezone, date
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db
from typing import Dict, Tuple, List
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
    password_hash = db.Column(db.String(255), nullable=True)  # Made nullable for DigiD users
    
    # DigiD Authentication fields
    digid_username = db.Column(db.String(80), unique=True, nullable=True, index=True)
    bsn = db.Column(db.String(9), unique=True, nullable=True, index=True)  # Dutch Social Security Number
    digid_verified = db.Column(db.Boolean, default=False)
    created_via_digid = db.Column(db.Boolean, default=False)
    
    # Email Confirmation fields
    email_confirmed = db.Column(db.Boolean, default=False)
    email_confirmation_token = db.Column(db.String(255), nullable=True, index=True)
    email_confirmation_sent_at = db.Column(db.DateTime, nullable=True)
    
    # Password Reset fields
    password_reset_token = db.Column(db.String(255), nullable=True, index=True)
    password_reset_sent_at = db.Column(db.DateTime, nullable=True)
    
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    
    # Personal Information (Extended Profile)
    profile_photo = db.Column(db.String(255), nullable=True)  # Path to profile photo
    phone = db.Column(db.String(20), nullable=True)
    country_code = db.Column(db.String(10), nullable=True)  # Country code for phone
    birth_date = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(10), nullable=True)  # male, female, other
    nationality = db.Column(db.String(50), nullable=True)  # Nationality
    
    # Registration completion fields
    registration_completed = db.Column(db.Boolean, default=False)
    profession = db.Column(db.String(50), nullable=True)  # tandarts, apotheker, huisarts, verpleegkundige
    diploma_file = db.Column(db.String(255), nullable=True)  # Path to uploaded diploma file
    language_certificate = db.Column(db.String(255), nullable=True)  # Path to uploaded language certificate
    
    # Professional Information (Extended)
    workplace = db.Column(db.String(255), nullable=True)  # Current workplace/practice
    specialization = db.Column(db.String(100), nullable=True)  # Medical specialization
    other_profession = db.Column(db.String(100), nullable=True)  # Custom profession if "other" selected
    other_nationality = db.Column(db.String(100), nullable=True)  # Custom nationality if "other" selected
    other_legal_status = db.Column(db.String(100), nullable=True)  # Custom legal status if "other" selected
    
    # Additional Documents (JSON field for flexibility)
    additional_documents = db.Column(db.Text, nullable=True)  # JSON array of document paths
    language_certificates = db.Column(db.Text, nullable=True)  # JSON array of language cert paths
    
    # Extended Registration Information
    legal_status = db.Column(db.String(50), nullable=True)  # EU citizen, non-EU resident, etc.
    dutch_level = db.Column(db.String(10), nullable=True)  # A1, A2, B1, B2, C1, C2, native
    english_level = db.Column(db.String(10), nullable=True)  # A1, A2, B1, B2, C1, C2, native
    idw_assessment = db.Column(db.String(50), nullable=True)  # completed, in_progress, not_started, not_required
    big_exam_registered = db.Column(db.String(50), nullable=True)  # registered, not_registered, planning_to_register
    exam_date = db.Column(db.Date, nullable=True)  # Planned exam date
    preparation_time = db.Column(db.String(50), nullable=True)  # 1_month, 3_months, 6_months, 1_year, more_than_year
    
    # Additional Text Information
    diploma_info = db.Column(db.Text, nullable=True)  # Information about diploma/certificate (legacy)
    work_experience = db.Column(db.Text, nullable=True)  # Work experience description
    additional_qualifications = db.Column(db.Text, nullable=True)  # Additional qualifications
    
    # Structured Education Information
    university_name = db.Column(db.String(255), nullable=True)  # University/Institution name
    degree_type = db.Column(db.String(50), nullable=True)  # bachelor, master, doctorate, medical_degree, etc.
    study_start_year = db.Column(db.Integer, nullable=True)  # Start year of studies
    study_end_year = db.Column(db.Integer, nullable=True)  # End year of studies
    study_country = db.Column(db.String(50), nullable=True)  # Country where studies were completed
    medical_specialization = db.Column(db.String(100), nullable=True)  # Medical specialization
    additional_education_info = db.Column(db.Text, nullable=True)  # Additional education information
    
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
    
    # Consent fields (new simplified structure)
    required_consents = db.Column(db.Boolean, default=False)  # Terms, Privacy, Data Processing, Data Usage
    optional_consents = db.Column(db.Boolean, default=False)  # Marketing, Newsletter, Research
    digital_signature = db.Column(db.String(255), nullable=True)  # Digital signature text
    
    # Program interests and motivation (for early registration)
    program_interests = db.Column(db.Text, nullable=True)  # JSON list of program interests
    motivation = db.Column(db.Text, nullable=True)  # User motivation text
    program_notifications = db.Column(db.Boolean, default=False)  # Consent for program notifications
    
    # Learning flow control
    requires_diagnostic = db.Column(db.Boolean, default=True)  # Flag to redirect new users to diagnostic
    
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
            'tandarts': 'Tandarts',
            'apotheker': '💊 Apotheker',
            'huisarts': '🩺 Huisarts',
            'verpleegkundige': '👩‍⚕️ Verpleegkundige'
        }
        return profession_display.get(self.profession, self.profession or 'Not specified')
    
    def can_use_password_auth(self):
        """Check if user can authenticate with password"""
        return self.password_hash is not None
    
    def generate_email_confirmation_token(self):
        """Generate email confirmation token"""
        import secrets
        import hashlib
        from datetime import datetime, timezone
        
        # Generate random token
        token = secrets.token_urlsafe(32)
        
        # Create hash of token for storage
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        self.email_confirmation_token = token_hash
        self.email_confirmation_sent_at = datetime.now(timezone.utc)
        
        return token
    
    def verify_email_confirmation_token(self, token):
        """Verify email confirmation token"""
        import hashlib
        from datetime import datetime, timezone, timedelta
        
        if not self.email_confirmation_token:
            return False
        
        # Check if token is expired
        if self.email_confirmation_sent_at:
            # Ensure both dates are timezone-aware
            sent_at = self.email_confirmation_sent_at
            if sent_at.tzinfo is None:
                # If sent_at is naive, assume it's UTC
                sent_at = sent_at.replace(tzinfo=timezone.utc)
            
            # Get expiry time from config (default 24 hours)
            from flask import current_app
            expiry_seconds = current_app.config.get('EMAIL_CONFIRMATION_EXPIRES', 86400)  # 24 hours default
            expiry_time = sent_at + timedelta(seconds=expiry_seconds)
            current_time = datetime.now(timezone.utc)
            
            # Debug logging
            print(f"=== TOKEN EXPIRY CHECK ===")
            print(f"Token sent at: {sent_at}")
            print(f"Current time: {current_time}")
            print(f"Expiry time: {expiry_time}")
            print(f"Expiry seconds: {expiry_seconds}")
            print(f"Time until expiry: {(expiry_time - current_time).total_seconds()} seconds")
            
            if current_time > expiry_time:
                print(f"=== TOKEN EXPIRED ===")
                return False
        
        # Verify token hash
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return token_hash == self.email_confirmation_token
    
    def confirm_email(self):
        """Confirm user's email"""
        self.email_confirmed = True
        self.email_confirmation_token = None
        self.email_confirmation_sent_at = None
    
    def generate_password_reset_token(self):
        """Generate password reset token"""
        import secrets
        import hashlib
        from datetime import datetime, timezone
        
        # Generate random token
        token = secrets.token_urlsafe(32)
        
        # Create hash of token for storage
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        self.password_reset_token = token_hash
        self.password_reset_sent_at = datetime.now(timezone.utc)
        
        return token
    
    def verify_password_reset_token(self, token):
        """Verify password reset token"""
        import hashlib
        from datetime import datetime, timezone, timedelta
        
        if not self.password_reset_token or not self.password_reset_sent_at:
            return False
        
        # Check if token is expired (1 hour)
        # Ensure password_reset_sent_at is timezone-aware
        sent_at = self.password_reset_sent_at
        if sent_at and sent_at.tzinfo is None:
            sent_at = sent_at.replace(tzinfo=timezone.utc)
        
        if sent_at and datetime.now(timezone.utc) - sent_at > timedelta(hours=1):
            return False
        
        # Verify token hash
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return token_hash == self.password_reset_token
    
    def clear_password_reset_token(self):
        """Clear password reset token"""
        self.password_reset_token = None
        self.password_reset_sent_at = None
    
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

# Analytics Models
class WebsiteVisit(db.Model):
    """Track website visits and user analytics"""
    __tablename__ = 'website_visits'
    
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False, index=True)  # IPv6 support
    user_agent = db.Column(db.Text, nullable=True)
    referrer = db.Column(db.String(500), nullable=True)
    page_url = db.Column(db.String(500), nullable=False)
    page_title = db.Column(db.String(200), nullable=True)
    session_id = db.Column(db.String(100), nullable=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)
    country = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    browser = db.Column(db.String(50), nullable=True)
    os = db.Column(db.String(50), nullable=True)
    device_type = db.Column(db.String(20), nullable=True)  # desktop, mobile, tablet
    visit_duration = db.Column(db.Integer, nullable=True)  # seconds
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationship
    user = db.relationship('User', backref='visits')
    
    def __repr__(self):
        return f'<WebsiteVisit {self.id}: {self.ip_address} -> {self.page_url}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'referrer': self.referrer,
            'page_url': self.page_url,
            'page_title': self.page_title,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'country': self.country,
            'city': self.city,
            'browser': self.browser,
            'os': self.os,
            'device_type': self.device_type,
            'visit_duration': self.visit_duration,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class PageView(db.Model):
    """Track individual page views with more detail"""
    __tablename__ = 'page_views'
    
    id = db.Column(db.Integer, primary_key=True)
    visit_id = db.Column(db.Integer, db.ForeignKey('website_visits.id'), nullable=False)
    session_id = db.Column(db.String(100), db.ForeignKey('user_sessions.session_id'), nullable=True, index=True)
    page_url = db.Column(db.String(500), nullable=False)
    page_title = db.Column(db.String(200), nullable=True)
    time_on_page = db.Column(db.Integer, nullable=True)  # seconds
    scroll_depth = db.Column(db.Integer, nullable=True)  # percentage
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    visit = db.relationship('WebsiteVisit', backref='page_views')
    session = db.relationship('UserSession', backref='page_views')
    
    def __repr__(self):
        return f'<PageView {self.id}: {self.page_url}>'

class UserSession(db.Model):
    """Track user sessions"""
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)
    ip_address = db.Column(db.String(45), nullable=False)
    user_agent = db.Column(db.Text, nullable=True)
    country = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    browser = db.Column(db.String(50), nullable=True)
    os = db.Column(db.String(50), nullable=True)
    device_type = db.Column(db.String(20), nullable=True)
    started_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    ended_at = db.Column(db.DateTime, nullable=True)
    is_active = db.Column(db.Boolean, default=True, index=True)
    total_visits = db.Column(db.Integer, default=0)
    
    # Relationship
    user = db.relationship('User', backref='sessions')
    
    def __repr__(self):
        return f'<UserSession {self.session_id}: {self.ip_address}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'country': self.country,
            'city': self.city,
            'browser': self.browser,
            'os': self.os,
            'device_type': self.device_type,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'is_active': self.is_active,
            'total_visits': self.total_visits
        }
    
    def can_use_digid_auth(self):
        """Check if user can authenticate with DigiD"""
        return self.digid_verified and self.bsn is not None
    
    def log_profile_change(self, field, old_value, new_value, changed_by=None):
        """Log a profile change for audit trail"""
        try:
            # Ensure we have a valid user ID
            if not hasattr(self, 'id') or self.id is None:
                return
                
            # Check if ProfileAuditLog table exists
            from sqlalchemy import inspect
            inspector = inspect(db.engine)
            if 'profile_audit_log' not in inspector.get_table_names():
                # Try to get current_app for logging, but don't fail if not available
                try:
                    from flask import current_app
                    current_app.logger.warning("ProfileAuditLog table does not exist, skipping audit log")
                except (RuntimeError, ImportError):
                    pass  # current_app not available, skip logging
                return
                
            audit_log = ProfileAuditLog(
                user_id=self.id,
                field_changed=field,
                old_value=str(old_value) if old_value is not None else None,
                new_value=str(new_value) if new_value is not None else None,
                changed_by=changed_by or self.id,
                change_type='profile_update'
            )
            db.session.add(audit_log)
            db.session.commit()
        except Exception as e:
            # Log the error but don't fail the main operation
            try:
                from flask import current_app
                current_app.logger.error(f"Failed to log profile change: {str(e)}")
            except (RuntimeError, ImportError):
                pass  # current_app not available, skip logging
            try:
                db.session.rollback()
            except:
                pass  # Don't fail if rollback fails
    
    def __repr__(self):
        return f'<UserSession {self.session_id}: {self.ip_address}>'

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
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    name_nl = db.Column(db.String(200))
    name_ru = db.Column(db.String(200))
    description = db.Column(db.Text)
    
    # BI-toets specific
    exam_component = db.Column(db.String(20), nullable=False)  # THEORETICAL, METHODOLOGY, PRACTICAL, CLINICAL
    exam_weight = db.Column(db.Float, nullable=False)  # Weight in percentage
    exam_type = db.Column(db.String(20), nullable=False)  # multiple_choice, open_book, practical_theory, interview, case_study
    
    # Learning structure
    duration_weeks = db.Column(db.Integer)
    total_estimated_hours = db.Column(db.Integer)
    prerequisites = db.Column(db.JSON)  # List of prerequisite path IDs
    
    # Modules and connections
    modules = db.Column(db.JSON)  # Module structure
    
    # Assessment
    assessment = db.Column(db.JSON)  # Assessment structure
    
    # IRT адаптивность
    irt_difficulty_range = db.Column(db.JSON)  # Диапазон сложности для IRT (min, max)
    irt_discrimination_range = db.Column(db.JSON)  # Диапазон дискриминации
    target_ability_levels = db.Column(db.JSON)  # Целевые уровни способностей для разных этапов
    adaptive_routing = db.Column(db.JSON)  # Правила адаптивной маршрутизации
    
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
    
    def get_irt_difficulty_range(self) -> Tuple[float, float]:
        """Get IRT difficulty range for this path"""
        if self.irt_difficulty_range:
            try:
                if isinstance(self.irt_difficulty_range, str):
                    range_data = json.loads(self.irt_difficulty_range)
                else:
                    range_data = self.irt_difficulty_range
                return range_data.get('min', -3.0), range_data.get('max', 3.0)
            except:
                pass
        return -3.0, 3.0  # Default range
    
    def get_target_ability_levels(self) -> Dict[str, float]:
        """Get target ability levels for different stages"""
        if self.target_ability_levels:
            try:
                if isinstance(self.target_ability_levels, str):
                    return json.loads(self.target_ability_levels)
                else:
                    return self.target_ability_levels
            except:
                pass
        return {
            'beginner': 0.3,
            'intermediate': 0.5,
            'advanced': 0.7,
            'expert': 0.9
        }
    
    def get_adaptive_routing_rules(self) -> Dict:
        """Get adaptive routing rules"""
        if self.adaptive_routing:
            try:
                if isinstance(self.adaptive_routing, str):
                    return json.loads(self.adaptive_routing)
                else:
                    return self.adaptive_routing
            except:
                pass
        return {
            'weak_domain_priority': 1.5,
            'strong_domain_priority': 0.8,
            'difficulty_adjustment_factor': 0.2,
            'review_frequency_multiplier': 1.2
        }
    
    def is_suitable_for_ability(self, user_ability: float) -> bool:
        """Check if this path is suitable for user's ability level"""
        min_diff, max_diff = self.get_irt_difficulty_range()
        return min_diff <= user_ability <= max_diff
    
    def get_recommended_modules_for_ability(self, user_ability: float, weak_domains: List[str] = None) -> List[Dict]:
        """Get recommended modules based on user ability and weak domains"""
        if not self.modules:
            return []
        
        target_levels = self.get_target_ability_levels()
        routing_rules = self.get_adaptive_routing_rules()
        
        recommended_modules = []
        
        for module in self.modules:
            module_difficulty = module.get('difficulty', 0.5)
            module_domains = module.get('domains', [])
            
            # Calculate suitability score
            difficulty_match = 1.0 - abs(user_ability - module_difficulty) / 2.0
            domain_priority = 1.0
            
            if weak_domains and module_domains:
                # Check if module covers weak domains
                weak_domain_coverage = len(set(weak_domains) & set(module_domains))
                if weak_domain_coverage > 0:
                    domain_priority = routing_rules.get('weak_domain_priority', 1.5)
            
            suitability_score = difficulty_match * domain_priority
            
            if suitability_score > 0.3:  # Minimum threshold
                recommended_modules.append({
                    'module': module,
                    'suitability_score': suitability_score,
                    'difficulty_match': difficulty_match,
                    'domain_priority': domain_priority
                })
        
        # Sort by suitability score
        recommended_modules.sort(key=lambda x: x['suitability_score'], reverse=True)
        
        return recommended_modules

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
    
    # IRT-based difficulty level
    difficulty = db.Column(db.Float, default=0.0)  # IRT-based difficulty level
    
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
    
    def check_answer(self, selected_index):
        """Check if the selected answer is correct"""
        return selected_index == self.correct_answer_index

    @property
    def irt_difficulty(self):
        """Get IRT difficulty parameter - calculated from response statistics if not available"""
        if self.irt_parameters and self.irt_parameters.difficulty is not None:
            return self.irt_parameters.difficulty
        
        # ИСПРАВЛЕНИЕ: Попробовать автокалибровку
        try:
            from utils.irt_calibration import calibration_service
            params = calibration_service.calibrate_question_from_responses(self.id)
            if params:
                return params.difficulty
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to auto-calibrate question {self.id}: {e}")
        
        # Fallback к расчету из статистики ответов
        calculated_params = self.calculate_default_irt_params()
        if calculated_params:
            return calculated_params['difficulty']
        
        return 0.0  # Безопасная заглушка
    
    @property
    def irt_discrimination(self):
        """Get IRT discrimination parameter - calculated from response statistics if not available"""
        if self.irt_parameters and self.irt_parameters.discrimination is not None:
            return self.irt_parameters.discrimination
        
        # ИСПРАВЛЕНИЕ: Попробовать автокалибровку
        try:
            from utils.irt_calibration import calibration_service
            params = calibration_service.calibrate_question_from_responses(self.id)
            if params:
                return params.discrimination
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to auto-calibrate question {self.id}: {e}")
        
        # Fallback к расчету из статистики ответов
        calculated_params = self.calculate_default_irt_params()
        if calculated_params:
            return calculated_params['discrimination']
        
        return 1.0  # Безопасная заглушка
    
    @property
    def irt_guessing(self):
        """Get IRT guessing parameter - calculated from response statistics if not available"""
        if self.irt_parameters and self.irt_parameters.guessing is not None:
            return self.irt_parameters.guessing
        
        # ИСПРАВЛЕНИЕ: Попробовать автокалибровку
        try:
            from utils.irt_calibration import calibration_service
            params = calibration_service.calibrate_question_from_responses(self.id)
            if params:
                return params.guessing
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Failed to auto-calibrate question {self.id}: {e}")
        
        # Fallback к расчету из статистики ответов
        calculated_params = self.calculate_default_irt_params()
        if calculated_params:
            return calculated_params['guessing']
        
        return 0.25  # Безопасная заглушка

    def calculate_default_irt_params(self) -> dict:
        """
        Calculate IRT parameters from response statistics and domain averages
        
        Returns:
            Dict with calculated IRT parameters or None if insufficient data
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Get response statistics
        response_stats = self._get_response_statistics()
        
        if response_stats['total_responses'] >= 5:
            # Calculate from actual response data
            difficulty = self._calculate_difficulty_from_responses(response_stats)
            discrimination = self._calculate_discrimination_from_responses(response_stats)
            guessing = self._calculate_guessing_from_responses(response_stats)
            
            logger.info(f"Calculated IRT parameters for question {self.id} from {response_stats['total_responses']} responses: "
                       f"difficulty={difficulty:.3f}, discrimination={discrimination:.3f}, guessing={guessing:.3f}")
            
            return {
                'difficulty': difficulty,
                'discrimination': discrimination,
                'guessing': guessing,
                'source': 'response_statistics',
                'sample_size': response_stats['total_responses']
            }
        
        elif response_stats['total_responses'] > 0:
            # Use domain averages for questions with some responses
            domain_params = self._get_domain_average_params()
            if domain_params:
                logger.info(f"Using domain averages for question {self.id} with {response_stats['total_responses']} responses")
                return domain_params
        
        else:
            # Use domain averages for questions with no responses
            domain_params = self._get_domain_average_params()
            if domain_params:
                logger.info(f"Using domain averages for question {self.id} with no responses")
                return domain_params
        
        return None

    def _get_response_statistics(self) -> dict:
        """Get response statistics for this question"""
        from sqlalchemy import func
        
        # Get TestAttempt statistics
        test_stats = db.session.query(
            func.count(TestAttempt.id).label('total'),
            func.sum(db.case((TestAttempt.is_correct == True, 1), else_=0)).label('correct')
        ).filter_by(question_id=self.id).first()
        
        # Get DiagnosticResponse statistics
        diag_stats = db.session.query(
            func.count(DiagnosticResponse.id).label('total'),
            func.sum(db.case((DiagnosticResponse.is_correct == True, 1), else_=0)).label('correct')
        ).filter_by(question_id=self.id).first()
        
        total_responses = (test_stats.total or 0) + (diag_stats.total or 0)
        correct_responses = (test_stats.correct or 0) + (diag_stats.correct or 0)
        
        return {
            'total_responses': total_responses,
            'correct_responses': correct_responses,
            'p_correct': correct_responses / total_responses if total_responses > 0 else 0.0
        }

    def _calculate_difficulty_from_responses(self, stats: dict) -> float:
        """Calculate difficulty parameter from response statistics"""
        import numpy as np
        
        p_correct = stats['p_correct']
        
        # Handle edge cases
        if p_correct <= 0.05:
            return 3.0  # Very difficult
        elif p_correct >= 0.95:
            return -3.0  # Very easy
        
        # Convert to IRT difficulty using logit transformation
        # b = -ln(p/(1-p))
        difficulty = -np.log(p_correct / (1 - p_correct))
        
        # Clip to reasonable range
        return np.clip(difficulty, -3.0, 3.0)

    def _calculate_discrimination_from_responses(self, stats: dict) -> float:
        """Calculate discrimination parameter from response statistics and question characteristics"""
        import numpy as np
        
        # Base discrimination based on question type
        base_discrimination = 1.0
        
        # Adjust based on domain
        domain_factors = {
            'MED': 1.2,    # Medical ethics - high discrimination
            'ANAT': 0.9,   # Anatomy - medium
            'PHARMA': 1.1, # Pharmacology - above medium
            'PATH': 1.15,  # Pathology - high
            'THER': 1.1,   # Therapeutic dentistry
            'SURG': 1.05,  # Surgical dentistry
            'ORTH': 1.0,   # Orthodontics
            'PEDO': 0.95,  # Pediatric dentistry
            'PERI': 1.1,   # Periodontology
            'ENDO': 1.15,  # Endodontics
            'RAD': 1.0,    # Radiology
            'PHAR': 1.1,   # Pharmacology
            'COMM': 1.2,   # Communication
        }
        
        if self.domain in domain_factors:
            base_discrimination *= domain_factors[self.domain]
        
        # Adjust based on question type
        if self.question_type == 'clinical_case':
            base_discrimination *= 1.1  # Clinical cases more discriminative
        elif self.question_type == 'theory':
            base_discrimination *= 0.95  # Theoretical questions less discriminative
        
        # Adjust based on difficulty level
        if self.difficulty_level == 1:
            base_discrimination *= 0.9  # Easy questions less discriminative
        elif self.difficulty_level == 3:
            base_discrimination *= 1.1  # Hard questions more discriminative
        
        # Add small random variation
        discrimination = base_discrimination + np.random.normal(0, 0.1)
        
        # Clip to reasonable range
        return np.clip(discrimination, 0.5, 2.5)

    def _calculate_guessing_from_responses(self, stats: dict) -> float:
        """Calculate guessing parameter based on question characteristics"""
        import numpy as np
        
        # Base guessing parameter for multiple choice
        base_guessing = 0.25
        
        # Adjust based on number of options
        if hasattr(self, 'options') and self.options:
            num_options = len(self.options)
            if num_options == 2:
                base_guessing = 0.5
            elif num_options == 3:
                base_guessing = 0.33
            elif num_options == 4:
                base_guessing = 0.25
            elif num_options == 5:
                base_guessing = 0.2
            else:
                base_guessing = 1.0 / num_options
        
        # Adjust based on question type
        if self.question_type == 'clinical_case':
            base_guessing *= 0.8  # Clinical cases have lower guessing
        elif self.question_type == 'theory':
            base_guessing *= 1.1  # Theory questions have higher guessing
        
        # Add small random variation
        guessing = base_guessing + np.random.normal(0, 0.02)
        
        # Clip to reasonable range
        return np.clip(guessing, 0.05, 0.5)

    def _get_domain_average_params(self) -> dict:
        """Get average IRT parameters for questions in the same domain"""
        from sqlalchemy import func
        
        # Get domain averages from questions with IRT parameters
        domain_averages = db.session.query(
            func.avg(IRTParameters.difficulty).label('avg_difficulty'),
            func.avg(IRTParameters.discrimination).label('avg_discrimination'),
            func.avg(IRTParameters.guessing).label('avg_guessing'),
            func.count(IRTParameters.id).label('sample_size')
        ).join(Question).filter(
            Question.domain == self.domain,
            IRTParameters.difficulty.isnot(None),
            IRTParameters.discrimination.isnot(None),
            IRTParameters.guessing.isnot(None)
        ).first()
        
        if domain_averages and domain_averages.sample_size >= 3:
            return {
                'difficulty': float(domain_averages.avg_difficulty),
                'discrimination': float(domain_averages.avg_discrimination),
                'guessing': float(domain_averages.avg_guessing),
                'source': 'domain_averages',
                'sample_size': domain_averages.sample_size
            }
        
        # Fallback to global averages if domain has insufficient data
        global_averages = db.session.query(
            func.avg(IRTParameters.difficulty).label('avg_difficulty'),
            func.avg(IRTParameters.discrimination).label('avg_discrimination'),
            func.avg(IRTParameters.guessing).label('avg_guessing'),
            func.count(IRTParameters.id).label('sample_size')
        ).filter(
            IRTParameters.difficulty.isnot(None),
            IRTParameters.discrimination.isnot(None),
            IRTParameters.guessing.isnot(None)
        ).first()
        
        if global_averages and global_averages.sample_size >= 10:
            return {
                'difficulty': float(global_averages.avg_difficulty),
                'discrimination': float(global_averages.avg_discrimination),
                'guessing': float(global_averages.avg_guessing),
                'source': 'global_averages',
                'sample_size': global_averages.sample_size
            }
        
        # Final fallback to reasonable defaults
        return {
            'difficulty': 0.0,
            'discrimination': 1.0,
            'guessing': 0.25,
            'source': 'default_values',
            'sample_size': 0
        }

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
    
    def auto_generate_irt_parameters(self):
        """
        Automatically generate IRT parameters for this question
        """
        # Create IRT parameters if they don't exist
        if not self.irt_parameters:
            from extensions import db
            # Generate initial parameters first
            initial_params = self.calculate_default_irt_params()
            if initial_params:
                irt_params = IRTParameters(
                    question_id=self.id,
                    difficulty=initial_params['difficulty'],
                    discrimination=initial_params['discrimination'],
                    guessing=initial_params['guessing']
                )
            else:
                # Use default values if calculation fails
                irt_params = IRTParameters(
                    question_id=self.id,
                    difficulty=0.0,
                    discrimination=1.0,
                    guessing=0.25
                )
            db.session.add(irt_params)
            db.session.flush()  # Get the ID
            self.irt_parameters = irt_params
        
        # Auto-generate parameters based on question type
        self.irt_parameters.auto_generate_parameters(self.question_type)
        
        # Log the auto-generation
        from extensions import db
        db.session.commit()
        
        return self.irt_parameters

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
# COMMUNITY FORUM MODELS
# ========================================

class ForumCategory(db.Model):
    """Категории форума"""
    __tablename__ = 'forum_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))  # Bootstrap icon class
    color = db.Column(db.String(20))  # CSS color
    order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    topics = db.relationship('ForumTopic', backref='category', lazy='dynamic', cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<ForumCategory {self.name}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'icon': self.icon,
            'color': self.color,
            'order': self.order,
            'is_active': self.is_active,
            'topics_count': self.topics.count(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ForumTopic(db.Model):
    """Темы форума"""
    __tablename__ = 'forum_topics'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('forum_categories.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Статус темы
    status = db.Column(db.String(20), default='normal')  # normal, pinned, locked, hidden
    is_sticky = db.Column(db.Boolean, default=False)
    is_locked = db.Column(db.Boolean, default=False)
    
    # Статистика
    views_count = db.Column(db.Integer, default=0)
    replies_count = db.Column(db.Integer, default=0)
    likes_count = db.Column(db.Integer, default=0)
    
    # Временные метки
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_reply_at = db.Column(db.DateTime)
    last_reply_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    author = db.relationship('User', foreign_keys=[author_id], backref='forum_topics')
    last_reply_user = db.relationship('User', foreign_keys=[last_reply_by], backref='last_replies')
    posts = db.relationship('ForumPost', backref='topic', lazy='dynamic', cascade="all, delete-orphan")
    likes = db.relationship('ForumTopicLike', backref='topic', lazy='dynamic', cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<ForumTopic {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category_id': self.category_id,
            'author_id': self.author_id,
            'author_name': self.author.full_name if self.author else 'Unknown',
            'status': self.status,
            'is_sticky': self.is_sticky,
            'is_locked': self.is_locked,
            'views_count': self.views_count,
            'replies_count': self.replies_count,
            'likes_count': self.likes_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'last_reply_at': self.last_reply_at.isoformat() if self.last_reply_at else None,
            'last_reply_by': self.last_reply_by,
            'last_reply_user': self.last_reply_user.full_name if self.last_reply_user else None
        }
    
    def increment_views(self):
        """Увеличить счетчик просмотров"""
        self.views_count += 1
        db.session.commit()
    
    def update_reply_stats(self):
        """Обновить статистику ответов"""
        self.replies_count = self.posts.count() - 1  # -1 для исключения первого поста (сама тема)
        if self.replies_count > 0:
            last_post = self.posts.order_by(ForumPost.created_at.desc()).first()
            if last_post:
                self.last_reply_at = last_post.created_at
                self.last_reply_by = last_post.author_id
        else:
            self.last_reply_at = None
            self.last_reply_by = None
        db.session.commit()

class ForumPost(db.Model):
    """Посты в темах форума"""
    __tablename__ = 'forum_posts'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('forum_topics.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    parent_post_id = db.Column(db.Integer, db.ForeignKey('forum_posts.id'), nullable=True)
    
    # Статус поста
    is_edited = db.Column(db.Boolean, default=False)
    edited_at = db.Column(db.DateTime)
    is_deleted = db.Column(db.Boolean, default=False)
    deleted_at = db.Column(db.DateTime)
    deleted_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Статистика
    likes_count = db.Column(db.Integer, default=0)
    
    # Временные метки
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    author = db.relationship('User', foreign_keys=[author_id], backref='forum_posts')
    deleted_by_user = db.relationship('User', foreign_keys=[deleted_by], backref='deleted_posts')
    parent_post = db.relationship('ForumPost', remote_side=[id], backref='replies')
    likes = db.relationship('ForumPostLike', backref='post', lazy='dynamic', cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<ForumPost {self.id}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'topic_id': self.topic_id,
            'author_id': self.author_id,
            'author_name': self.author.full_name if self.author else 'Unknown',
            'parent_post_id': self.parent_post_id,
            'is_edited': self.is_edited,
            'edited_at': self.edited_at.isoformat() if self.edited_at else None,
            'is_deleted': self.is_deleted,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'likes_count': self.likes_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def mark_as_edited(self):
        """Отметить пост как отредактированный"""
        self.is_edited = True
        self.edited_at = datetime.utcnow()
        db.session.commit()
    
    def soft_delete(self, deleted_by_user_id):
        """Мягкое удаление поста"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        self.deleted_by = deleted_by_user_id
        db.session.commit()

class ForumTopicLike(db.Model):
    """Лайки тем форума"""
    __tablename__ = 'forum_topic_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('forum_topics.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='topic_likes')
    
    __table_args__ = (db.UniqueConstraint('topic_id', 'user_id', name='uc_topic_like'),)

class ForumPostLike(db.Model):
    """Лайки постов форума"""
    __tablename__ = 'forum_post_likes'
    
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('forum_posts.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='post_likes')
    
    __table_args__ = (db.UniqueConstraint('post_id', 'user_id', name='uc_post_like'),)

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
    # Note: backref is defined in Question model (line 1021)
    # This creates a bidirectional relationship: Question.irt_parameters ↔ IRTParameters.question
    
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
    
    def auto_generate_parameters(self, question_type: str = 'multiple_choice'):
        """
        Automatically generate IRT parameters for a question
        
        Args:
            question_type: Type of question ('multiple_choice', 'open_ended', etc.)
        """
        # Generate initial parameters
        self.generate_initial_parameters(question_type)
        
        # Log the auto-generation
        from extensions import db
        db.session.commit()
        
        return self
    
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
    
    def generate_initial_parameters(self, question_type: str = 'multiple_choice'):
        """
        Generate initial IRT parameters for a new question
        
        Args:
            question_type: Type of question ('multiple_choice', 'open_ended', etc.)
        """
        import random
        import numpy as np
        
        # Generate difficulty from normal distribution (-3 to 3)
        self.difficulty = np.random.normal(0, 1.5)
        self.difficulty = max(-3.0, min(3.0, self.difficulty))
        
        # Generate discrimination from uniform distribution (0.5 to 2.5)
        self.discrimination = random.uniform(0.5, 2.5)
        
        # Set guessing parameter based on question type
        if question_type == 'multiple_choice':
            # For 5-option multiple choice, guessing = 0.2
            self.guessing = 0.2
        elif question_type == 'true_false':
            # For true/false questions, guessing = 0.5
            self.guessing = 0.5
        else:
            # For open-ended questions, guessing = 0.0
            self.guessing = 0.0
        
        # Update calibration date
        self.calibration_date = datetime.now(timezone.utc)
        self.calibration_sample_size = 0
        
        # Log the parameter generation
        from extensions import db
        db.session.commit()
        
        return self
    
    def initialize_default_parameters(self):
        """Initialize IRT parameters based on question category and difficulty"""
        import random
        import numpy as np
        
        # Get question difficulty level if available
        if hasattr(self.question, 'difficulty_level'):
            base_difficulty = self.question.difficulty_level
        else:
            base_difficulty = 0.0
        
        # Set difficulty (b-parameter) with normal distribution
        self.difficulty = np.random.normal(base_difficulty, 0.5)
        self.difficulty = max(-3.0, min(3.0, self.difficulty))  # Clamp to [-3, 3]
        
        # Set discrimination (a-parameter) 
        self.discrimination = np.random.uniform(0.5, 2.0)
        
        # Guessing parameter for multiple choice
        self.guessing = 0.25
        
        # Set calibration data
        self.calibration_date = datetime.now(timezone.utc)
        self.calibration_sample_size = 0
        
        db.session.commit()
        
        # Log the initialization
        try:
            from app import app
            app.logger.info(f"Initialized IRT parameters for question {self.question_id}: "
                           f"difficulty={self.difficulty:.3f}, discrimination={self.discrimination:.3f}")
        except ImportError:
            # If app is not available, just continue
            pass
        
        return self
    
    def calibrate_from_responses(self, responses: list):
        """
        Recalibrate IRT parameters based on user responses
        
        Args:
            responses: List of response dictionaries with 'user_ability' and 'is_correct' keys
        """
        if len(responses) < 5:
            # Need at least 5 responses for reliable calibration
            return False
        
        import numpy as np
        from scipy.optimize import minimize  # type: ignore
        from scipy.stats import logistic
        
        # Extract data
        abilities = [r['user_ability'] for r in responses]
        correct = [r['is_correct'] for r in responses]
        
        # Define negative log-likelihood function for 3PL model
        def neg_log_likelihood(params):
            a, b, c = params
            if a <= 0 or c < 0 or c > 1:
                return float('inf')
            
            log_likelihood = 0
            for theta, response in zip(abilities, correct):
                # 3PL probability
                p = c + (1 - c) / (1 + np.exp(-a * (theta - b)))
                
                # Avoid log(0) or log(1)
                p = max(0.001, min(0.999, p))
                
                if response:
                    log_likelihood += np.log(p)
                else:
                    log_likelihood += np.log(1 - p)
            
            return -log_likelihood
        
        # Initial parameter estimates
        initial_params = [self.discrimination, self.difficulty, self.guessing]
        
        # Optimize parameters
        try:
            result = minimize(neg_log_likelihood, initial_params, 
                           bounds=[(0.1, 4.0), (-4.0, 4.0), (0.0, 0.5)],
                           method='L-BFGS-B')
            
            if result.success:
                # Update parameters
                self.discrimination = result.x[0]
                self.difficulty = result.x[1]
                self.guessing = result.x[2]
                
                # Update calibration data
                self.calibration_date = datetime.now(timezone.utc)
                self.calibration_sample_size = len(responses)
                
                # Calculate reliability (correlation between predicted and actual)
                predicted_probs = []
                for theta in abilities:
                    p = self.get_3pl_probability(theta)
                    predicted_probs.append(p)
                
                # Calculate correlation
                if len(predicted_probs) > 1:
                    correlation = np.corrcoef(predicted_probs, correct)[0, 1]
                    self.reliability = correlation if not np.isnan(correlation) else 0.0
                
                # Log calibration
                from extensions import db
                db.session.commit()
                
                return True
            else:
                return False
                
        except Exception as e:
            # Log error and return False
            return False
    
    def get_calibration_quality(self) -> dict:
        """
        Get calibration quality metrics
        
        Returns:
            Dict with calibration quality information
        """
        quality = {
            'sample_size': self.calibration_sample_size or 0,
            'reliability': self.reliability or 0.0,
            'calibration_date': self.calibration_date,
            'is_calibrated': self.calibration_sample_size is not None and self.calibration_sample_size >= 10
        }
        
        # Add quality assessment
        if quality['sample_size'] >= 50 and quality['reliability'] > 0.7:
            quality['quality_level'] = 'excellent'
        elif quality['sample_size'] >= 20 and quality['reliability'] > 0.5:
            quality['quality_level'] = 'good'
        elif quality['sample_size'] >= 10:
            quality['quality_level'] = 'fair'
        else:
            quality['quality_level'] = 'poor'
        
        return quality

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
        domain_stats = {}
        try:
            domain_stats = irt_engine.get_domain_detailed_statistics()
        except (AttributeError, Exception) as e:
            # Fallback - create empty stats
            import logging
            logging.warning(f"Error getting domain statistics: {e}")
            domain_stats = {}
        
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
                # No data for this domain - set to 0.0 instead of None
                domain_abilities[domain_code] = 0.0
        
        # Calculate overall statistics
        accuracy = self.get_accuracy()
        avg_response_time = 0
        if self.questions_answered > 0:
            avg_response_time = db.session.query(
                db.func.avg(DiagnosticResponse.response_time)
            ).filter_by(session_id=self.id).scalar() or 0
        
        # Convert IRT ability to readiness percentage
        current_ability_theta = self.current_ability
        try:
            readiness_percentage = irt_engine.convert_irt_ability_to_readiness_percentage(current_ability_theta)
            performance_percentage = irt_engine.convert_irt_ability_to_performance_percentage(current_ability_theta)
        except (AttributeError, Exception) as e:
            import logging
            logging.warning(f"Error converting IRT abilities: {e}")
            readiness_percentage = 50.0  # Default 50%
            performance_percentage = 50.0  # Default 50%
        
        # Calculate target ability and study weeks
        try:
            target_ability = irt_engine.calculate_target_ability()
            study_hours_per_week = 20.0  # Default study hours
            weeks_to_target = irt_engine.calculate_weeks_to_target(
                readiness_percentage, target_ability, study_hours_per_week
            )
        except (AttributeError, Exception) as e:
            import logging
            logging.warning(f"Error calculating target ability: {e}")
            target_ability = 0.5  # Default target
            study_hours_per_week = 20.0
            weeks_to_target = 12  # Default 12 weeks
        
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
            'confidence_interval': irt_engine.get_confidence_interval() if hasattr(irt_engine, 'get_confidence_interval') else [-1.0, 1.0],
            
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
            # Ensure both timestamps are timezone-aware
            started_at = self.started_at
            completed_at = self.completed_at
            
            # If started_at is naive, make it timezone-aware
            if started_at.tzinfo is None:
                started_at = started_at.replace(tzinfo=timezone.utc)
            
            # If completed_at is naive, make it timezone-aware
            if completed_at.tzinfo is None:
                completed_at = completed_at.replace(tzinfo=timezone.utc)
            
            duration = completed_at - started_at
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
        """Update ability estimate using IRT algorithm with proper MLE and standard errors"""
        from utils.irt_engine import IRTEngine
        import math
        
        # Get all responses for this session
        responses = self.responses.all()
        
        if not responses:
            return
        
        # Prepare response data for IRT engine with validation
        response_data = []
        for resp in responses:
            question = resp.question
            # Validate IRT parameters before using them
            if (question.irt_difficulty is not None and 
                question.irt_discrimination is not None and 
                question.irt_guessing is not None):
                
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
            # Use IRT engine to estimate ability with proper MLE
            irt_engine = IRTEngine()
            theta, se = irt_engine.estimate_ability(response_data)
            
            # Update session with new estimates
            self.current_ability = theta
            self.ability_se = se
            
            # Add to ability history
            self.add_ability_estimate(theta, se, responses[-1].question_id)
        else:
            # Fallback: if no valid IRT parameters, use simple proportion
            correct_count = sum(1 for r in responses if r.is_correct)
            total_count = len(responses)
            if total_count > 0:
                proportion = correct_count / total_count
                # Simple mapping to theta scale
                theta = 2 * (proportion - 0.5)  # Maps 0->-1, 0.5->0, 1->1
                se = 1.0 / math.sqrt(total_count)  # Simple standard error
                
                self.current_ability = theta
                self.ability_se = se
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
    
    # Diagnostic reassessment
    next_diagnostic_date = db.Column(db.Date, nullable=True)  # Дата следующей переоценки
    diagnostic_reminder_sent = db.Column(db.Boolean, default=False)  # Флаг отправки напоминания
    
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
    
    def set_next_diagnostic_date(self, days_ahead: int = None):
        """
        Set the next diagnostic date using adaptive scheduling
        
        Args:
            days_ahead: Number of days ahead for next diagnostic (if None, uses adaptive calculation)
        """
        from datetime import date, timedelta
        
        if days_ahead is None:
            # Use adaptive scheduling
            try:
                from utils.scheduler_service import get_scheduler
                scheduler = get_scheduler()
                adaptive_interval = scheduler.calculate_adaptive_interval(self.user_id, self)
                days_ahead = adaptive_interval
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error calculating adaptive interval for plan {self.id}: {str(e)}")
                days_ahead = 21  # Fallback to default
        
        # Use start_date if available, otherwise use current date
        if self.start_date:
            base_date = self.start_date
        else:
            base_date = date.today()
        
        self.next_diagnostic_date = base_date + timedelta(days=days_ahead)
        self.diagnostic_reminder_sent = False
        
        # Log the diagnostic date setting
        from extensions import db
        db.session.commit()
        
        return self.next_diagnostic_date
    
    def calculate_adaptive_weak_domains(self, abilities: dict) -> list:
        """
        Calculate weak domains using adaptive thresholds based on BIG exam weights
        
        Args:
            abilities: Dictionary of domain abilities
            
        Returns:
            List of weak domain codes
        """
        weak_domains = []
        
        # Get domain weights from BIG exam structure
        from models import BIGDomain
        
        for domain_code, ability in abilities.items():
            # Get domain weight
            domain = BIGDomain.query.filter_by(code=domain_code).first()
            weight = domain.weight_percentage if domain else 5.0  # Default weight
            
            # Adaptive threshold based on domain importance
            # Critical domains (high weight) have stricter thresholds
            if weight >= 12:  # Critical domains (THER, SURG, etc.)
                threshold = -0.3  # Stricter threshold for critical domains
            elif weight >= 8:  # Important domains
                threshold = -0.4  # Medium threshold
            else:  # Standard domains
                threshold = -0.5  # Standard threshold (1 SD below mean)
            
            if ability < threshold:
                weak_domains.append(domain_code)
        
        return weak_domains
    
    def calculate_confidence_interval(self, ability: float, se: float, confidence_level: float = 0.95) -> tuple:
        """
        Calculate confidence interval for ability estimate
        
        Args:
            ability: Ability estimate (theta)
            se: Standard error of ability estimate
            confidence_level: Confidence level (default 0.95 for 95% CI)
            
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        import math
        from scipy import stats
        
        # Calculate z-score for confidence level
        z_score = stats.norm.ppf((1 + confidence_level) / 2)
        
        # Calculate confidence interval
        margin_of_error = z_score * se
        lower_bound = ability - margin_of_error
        upper_bound = ability + margin_of_error
        
        return (lower_bound, upper_bound)
    
    def update_after_reassessment(self, new_abilities: dict, reassessment_date: date = None):
        """
        Обновляет план после переоценки диагностики
        
        Args:
            new_abilities: Новые способности по доменам
            reassessment_date: Дата переоценки (по умолчанию сегодня)
        """
        if reassessment_date is None:
            reassessment_date = date.today()
        
        # Обновляем domain_analysis с новыми способностями
        domain_analysis = self.get_domain_analysis()
        for domain_code, ability in new_abilities.items():
            if domain_code in domain_analysis:
                domain_analysis[domain_code]['ability_estimate'] = ability
                domain_analysis[domain_code]['last_updated'] = reassessment_date.isoformat()
        
        self.set_domain_analysis(domain_analysis)
        
        # Пересчитываем weak_domains на основе новых способностей
        weak_domains = self.calculate_adaptive_weak_domains(new_abilities)
        self.set_weak_domains(weak_domains)
        
        # Обновляем общую способность (среднее по всем доменам)
        if new_abilities:
            self.current_ability = sum(new_abilities.values()) / len(new_abilities)
        
        # Устанавливаем дату следующей переоценки (через 14 дней)
        self.set_next_diagnostic_date(14)
        
        # Сбрасываем флаг напоминания
        self.diagnostic_reminder_sent = False
        
        # Обновляем timestamp
        self.last_updated = datetime.now(timezone.utc)
        
        return self
    
    def update_progress_from_session(self, session: 'StudySession') -> bool:
        """
        Обновляет прогресс плана обучения на основе завершенной сессии
        
        Args:
            session: Завершенная StudySession
            
        Returns:
            bool: True если обновление прошло успешно
        """
        try:
            import logging
            logger = logging.getLogger(__name__)
            
            # Проверяем что сессия завершена
            if session.status != 'completed':
                logger.warning(f"Session {session.id} is not completed, status: {session.status}")
                return False
            
            # Получаем данные сессии
            session_accuracy = session.get_accuracy()
            session_duration = session.actual_duration or 0
            session_ability_change = session.ability_change or 0
            
            logger.info(f"Updating plan {self.id} from session {session.id}: "
                       f"accuracy={session_accuracy:.2f}, duration={session_duration}min, "
                       f"ability_change={session_ability_change:.3f}")
            
            # 1. ОБНОВЛЯЕМ ОБЩИЙ ПРОГРЕСС
            # Рассчитываем вклад сессии в общий прогресс
            session_weight = min(1.0, session_duration / 30.0)  # Нормализуем к 30 минутам
            progress_contribution = session_weight * session_accuracy * 0.1  # 10% за идеальную сессию
            
            # Обновляем overall_progress
            new_progress = min(100.0, self.overall_progress + progress_contribution)
            progress_change = new_progress - self.overall_progress
            self.overall_progress = new_progress
            
            logger.info(f"Plan {self.id}: overall_progress {self.overall_progress:.1f}% "
                       f"(+{progress_change:.1f}%)")
            
            # 2. ОБНОВЛЯЕМ IRT СПОСОБНОСТИ
            if session_ability_change != 0 and session.ability_confidence:
                # Обновляем способность в соответствующем домене
                if session.domain:
                    domain_code = session.domain.code
                    domain_analysis = self.get_domain_analysis()
                    
                    if domain_code in domain_analysis:
                        old_ability = domain_analysis[domain_code].get('ability_estimate', 0.0)
                        new_ability = old_ability + session_ability_change
                        
                        # Ограничиваем способность разумными пределами
                        new_ability = max(-3.0, min(3.0, new_ability))
                        
                        # Обновляем в domain_analysis
                        domain_analysis[domain_code]['ability_estimate'] = new_ability
                        domain_analysis[domain_code]['last_updated'] = datetime.now(timezone.utc).isoformat()
                        
                        self.set_domain_analysis(domain_analysis)
                        
                        logger.info(f"Plan {self.id}: domain {domain_code} ability "
                                   f"{old_ability:.3f} → {new_ability:.3f} "
                                   f"(change: {session_ability_change:.3f})")
                        
                        # 3. ПРОВЕРЯЕМ НУЖНО ЛИ ОБНОВИТЬ WEAK_DOMAINS
                        if abs(session_ability_change) > 0.1:  # Значительное изменение
                            self._update_weak_domains_if_needed()
            
            # 4. ОБНОВЛЯЕМ ОБЩУЮ СПОСОБНОСТЬ
            domain_analysis = self.get_domain_analysis()
            if domain_analysis:
                abilities = [data.get('ability_estimate', 0.0) for data in domain_analysis.values()]
                if abilities:
                    new_overall_ability = sum(abilities) / len(abilities)
                    ability_change = new_overall_ability - self.current_ability
                    self.current_ability = new_overall_ability
                    
                    logger.info(f"Plan {self.id}: overall ability "
                               f"{self.current_ability:.3f} (change: {ability_change:.3f})")
            
            # 5. ОБНОВЛЯЕМ TIMESTAMP
            self.last_updated = datetime.now(timezone.utc)
            
            # 6. ОБНОВЛЯЕМ next_diagnostic_date на основе прогресса
            if self.overall_progress >= 80:
                # Для продвинутых учеников - еженедельная переоценка
                self.set_next_diagnostic_date(7)
                logger.info(f"Plan {self.id}: Set next diagnostic to 7 days (advanced learner)")
            else:
                # Для остальных - двухнедельная переоценка
                self.set_next_diagnostic_date(14)
                logger.info(f"Plan {self.id}: Set next diagnostic to 14 days (standard learner)")
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating plan {self.id} from session {session.id}: {e}")
            return False
    
    def _update_weak_domains_if_needed(self):
        """
        Обновляет weak_domains если способности значительно изменились
        """
        try:
            domain_analysis = self.get_domain_analysis()
            if not domain_analysis:
                return
            
            # Получаем текущие способности
            current_abilities = {}
            for domain_code, data in domain_analysis.items():
                if isinstance(data, dict) and 'ability_estimate' in data:
                    current_abilities[domain_code] = data['ability_estimate']
            
            if not current_abilities:
                return
            
            # Рассчитываем новые weak_domains
            new_weak_domains = self.calculate_adaptive_weak_domains(current_abilities)
            current_weak_domains = self.get_weak_domains()
            
            # Проверяем есть ли значительные изменения
            if set(new_weak_domains) != set(current_weak_domains):
                self.set_weak_domains(new_weak_domains)
                
                import logging
                logger = logging.getLogger(__name__)
                logger.info(f"Plan {self.id}: weak_domains updated: "
                           f"{current_weak_domains} → {new_weak_domains}")
        
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error updating weak_domains for plan {self.id}: {e}")
    
    def _recalculate_weak_domains(self):
        """
        Пересчитывает weak domains на основе текущего анализа доменов (scores)
        """
        try:
            import logging
            logger = logging.getLogger(__name__)
            
            domain_analysis = self.get_domain_analysis()
            if not domain_analysis:
                logger.warning(f"Plan {self.id}: No domain analysis available for recalculation")
                return
            
            # Рассчитываем новые weak и strong domains на основе scores
            new_weak_domains = []
            new_strong_domains = []
            
            for domain_code, domain_data in domain_analysis.items():
                if isinstance(domain_data, dict):
                    score = domain_data.get('score', 0)
                    
                    if score < 70:  # Ниже 70% - слабый домен
                        new_weak_domains.append(domain_code)
                    elif score >= 85:  # Выше 85% - сильный домен
                        new_strong_domains.append(domain_code)
            
            # Получаем текущие списки для сравнения
            current_weak = set(self.get_weak_domains())
            current_strong = set(self.get_strong_domains())
            new_weak_set = set(new_weak_domains)
            new_strong_set = set(new_strong_domains)
            
            # Обновляем только если есть значительные изменения
            if current_weak != new_weak_set or current_strong != new_strong_set:
                self.set_weak_domains(new_weak_domains)
                self.set_strong_domains(new_strong_domains)
                
                logger.info(f"Plan {self.id}: Updated weak domains: {list(current_weak)} → {new_weak_domains}")
                logger.info(f"Plan {self.id}: Updated strong domains: {list(current_strong)} → {new_strong_domains}")
                
                # Если нет слабых доменов, предполагаем готовность к экзамену
                if len(new_weak_domains) == 0:
                    self.estimated_readiness = 0.9
                    logger.info(f"Plan {self.id}: No weak domains found, setting estimated_readiness to 0.9")
                else:
                    # Рассчитываем готовность на основе количества слабых доменов
                    total_domains = len(domain_analysis)
                    weak_ratio = len(new_weak_domains) / total_domains
                    self.estimated_readiness = max(0.1, 1.0 - weak_ratio)
                    logger.info(f"Plan {self.id}: Updated estimated_readiness to {self.estimated_readiness:.2f}")
        
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error recalculating weak domains for plan {self.id}: {e}")
    
    def is_valid_for_daily_tasks(self) -> tuple[bool, str]:
        """
        Проверяет, содержит ли план достаточно данных для генерации ежедневных задач
        
        Returns:
            Tuple[bool, str]: (валиден ли план, причина невалидности)
        """
        try:
            # Проверяем weak_domains
            weak_domains = self.get_weak_domains()
            if not weak_domains or len(weak_domains) == 0:
                return False, "No weak domains identified"
            
            # Проверяем domain_analysis 
            domain_analysis = self.get_domain_analysis()
            if not domain_analysis:
                return False, "No domain analysis data"
                
            # Проверяем, что анализ содержит данные для слабых доменов
            for domain in weak_domains:
                if domain not in domain_analysis:
                    return False, f"Missing analysis for weak domain: {domain}"
            
            return True, "Plan is valid"
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error validating plan {self.id} for daily tasks: {e}")
            return False, f"Validation error: {str(e)}"
    
    def get_adaptive_learning_path(self, target_domain: str = None) -> dict:
        """
        Получает адаптивный путь обучения на основе текущих способностей
        
        Args:
            target_domain: Целевой домен (опционально)
            
        Returns:
            Словарь с адаптивным путем обучения
        """
        try:
            from utils.adaptive_path_selector import AdaptivePathSelector
            
            selector = AdaptivePathSelector()
            return selector.select_adaptive_path(self.user_id, target_domain)
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Ошибка получения адаптивного пути для пользователя {self.user_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def update_adaptive_path_after_reassessment(self, new_abilities: dict) -> dict:
        """
        Обновляет адаптивный путь обучения после переоценки
        
        Args:
            new_abilities: Новые способности после переоценки
            
        Returns:
            Результат обновления пути
        """
        try:
            from utils.adaptive_path_selector import AdaptivePathSelector
            
            # Сначала обновляем план обучения
            self.update_after_reassessment(new_abilities)
            
            # Затем обновляем адаптивный путь
            selector = AdaptivePathSelector()
            return selector.update_path_after_reassessment(self.user_id, new_abilities)
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Ошибка обновления адаптивного пути для пользователя {self.user_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def __repr__(self):
        return f'<PersonalLearningPlan User{self.user_id}: θ={self.current_ability:.3f} Progress={self.overall_progress:.1f}%>'
    
    def update_ability_safely(self, new_ability: float, domain: str = None, confidence: float = None) -> bool:
        """
        Безопасное обновление способности с защитой от конфликтов
        
        Args:
            new_ability: Новая оценка способности
            domain: Домен для обновления (если None - общая способность)
            confidence: Уверенность в оценке
            
        Returns:
            True если обновление успешно, False если конфликт
        """
        from extensions import db
        from sqlalchemy import and_
        
        try:
            # Проверяем, не было ли обновления с момента загрузки
            current_plan = PersonalLearningPlan.query.filter(
                and_(
                    PersonalLearningPlan.id == self.id,
                    PersonalLearningPlan.last_updated == self.last_updated
                )
            ).first()
            
            if not current_plan:
                # План был изменен другим процессом
                return False
            
            # Обновляем общую способность
            if domain is None:
                self.current_ability = new_ability
            else:
                # Обновляем способность конкретного домена
                domain_analysis = self.get_domain_analysis()
                if domain_analysis is None:
                    domain_analysis = {}
                
                domain_analysis[domain] = new_ability
                self.set_domain_analysis(domain_analysis)
                
                # Пересчитываем общую способность
                if domain_analysis:
                    self.current_ability = sum(domain_analysis.values()) / len(domain_analysis)
            
            # Обновляем временную метку
            self.last_updated = datetime.now(timezone.utc)
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка при обновлении способности плана: {e}")
            return False
    
    def get_ability_update_lock_key(self) -> str:
        """Генерирует ключ блокировки для обновления способности"""
        return f"ability_update_lock_{self.user_id}_{self.id}"
    
    def should_update_ability(self, new_ability: float, min_change_threshold: float = 0.05) -> bool:
        """
        Проверяет, нужно ли обновлять способность
        
        Args:
            new_ability: Новая оценка способности
            min_change_threshold: Минимальный порог изменения для обновления
            
        Returns:
            True если изменение достаточно значимо
        """
        if self.current_ability is None:
            return True
        
        change = abs(new_ability - self.current_ability)
        return change >= min_change_threshold

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
    
    # НОВЫЕ ПОЛЯ ДЛЯ IRT ОБРАТНОЙ СВЯЗИ
    # IRT данные сессии
    session_ability_before = db.Column(db.Float, nullable=True)  # Способность до сессии
    session_ability_after = db.Column(db.Float, nullable=True)   # Способность после сессии
    ability_change = db.Column(db.Float, nullable=True)          # Изменение способности
    ability_confidence = db.Column(db.Float, nullable=True)      # Уверенность в изменении
    
    # Версионность для предотвращения конфликтов
    version = db.Column(db.Integer, default=1)  # Оптимистичная блокировка
    last_ability_update = db.Column(db.DateTime, nullable=True)  # Время последнего обновления способности
    
    # Флаги обработки
    ability_updated = db.Column(db.Boolean, default=False)  # Флаг успешного обновления способности
    feedback_processed = db.Column(db.Boolean, default=False)  # Флаг обработки обратной связи
    
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
    
    def start_session(self):
        """Start the study session"""
        self.started_at = datetime.now(timezone.utc)
        self.status = 'in_progress'
        
        # Записываем начальную способность
        if self.learning_plan:
            self.session_ability_before = self.learning_plan.current_ability
        
        # Log session start
        from extensions import db
        db.session.commit()
        
        return self
    
    def complete_session(self, actual_duration: int = None, accuracy: float = None):
        """
        Complete the study session
        
        Args:
            actual_duration: Actual duration in minutes
            accuracy: Session accuracy (0.0 - 1.0)
        """
        self.completed_at = datetime.now(timezone.utc)
        self.status = 'completed'
        self.progress_percent = 100.0
        
        if actual_duration is not None:
            self.actual_duration = actual_duration
        
        if accuracy is not None:
            # Update correct answers based on accuracy
            if self.questions_answered > 0:
                self.correct_answers = int(self.questions_answered * accuracy)
        
        # Log session completion
        from extensions import db
        db.session.commit()
        
        return self
    
    def update_progress(self, questions_answered: int = None, correct_answers: int = None, 
                       progress_percent: float = None, time_spent: int = None):
        """
        Update session progress
        
        Args:
            questions_answered: Number of questions answered
            correct_answers: Number of correct answers
            progress_percent: Progress percentage (0-100)
            time_spent: Time spent in minutes
        """
        if questions_answered is not None:
            self.questions_answered = questions_answered
        
        if correct_answers is not None:
            self.correct_answers = correct_answers
        
        if progress_percent is not None:
            self.progress_percent = max(0.0, min(100.0, progress_percent))
        
        if time_spent is not None:
            self.actual_duration = time_spent
        
        # Log progress update
        from extensions import db
        db.session.commit()
        
        return self
    
    def update_ability_safely(self, new_ability: float, confidence: float = None) -> bool:
        """
        Безопасное обновление способности с защитой от конфликтов
        
        Args:
            new_ability: Новая оценка способности
            confidence: Уверенность в оценке
            
        Returns:
            True если обновление успешно, False если конфликт
        """
        from extensions import db
        from sqlalchemy import and_
        
        try:
            # Проверяем, не было ли обновления с момента загрузки
            current_session = StudySession.query.filter(
                and_(
                    StudySession.id == self.id,
                    StudySession.version == self.version
                )
            ).first()
            
            if not current_session:
                # Сессия была изменена другим процессом
                return False
            
            # Обновляем способность
            self.session_ability_after = new_ability
            if self.session_ability_before is not None:
                self.ability_change = new_ability - self.session_ability_before
            
            if confidence is not None:
                self.ability_confidence = confidence
            
            self.ability_updated = True
            self.last_ability_update = datetime.now(timezone.utc)
            self.version += 1  # Увеличиваем версию
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка при обновлении способности: {e}")
            return False
    
    def mark_feedback_processed(self):
        """Отмечает, что обратная связь обработана"""
        self.feedback_processed = True
        from extensions import db
        db.session.commit()
    
    def get_irt_feedback_data(self) -> dict:
        """Получает данные для IRT обратной связи"""
        return {
            'session_id': self.id,
            'domain_id': self.domain_id,
            'questions_answered': self.questions_answered,
            'correct_answers': self.correct_answers,
            'accuracy': self.get_accuracy(),
            'ability_before': self.session_ability_before,
            'ability_after': self.session_ability_after,
            'ability_change': self.ability_change,
            'confidence': self.ability_confidence,
            'version': self.version
        }

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
    learning_path_id = db.Column(db.Integer, db.ForeignKey('learning_path.id'), nullable=False)
    
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

class SpacedRepetitionItem(db.Model):
    """Модель для элементов системы интервального повторения (SM-2 алгоритм)"""
    __tablename__ = 'spaced_repetition_item'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False)
    
    # SM-2 параметры
    ease_factor = db.Column(db.Float, default=2.5)  # Фактор легкости (1.3 - 2.5)
    interval = db.Column(db.Integer, default=1)  # Интервал в днях
    repetitions = db.Column(db.Integer, default=0)  # Количество повторений
    
    # Качество ответов (0-5)
    quality = db.Column(db.Integer, default=0)  # Последнее качество ответа
    average_quality = db.Column(db.Float, default=0.0)  # Среднее качество
    
    # Временные метки
    next_review = db.Column(db.DateTime, nullable=False)
    last_review = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Дополнительные данные
    domain = db.Column(db.String(50), nullable=True, index=True)  # Домен вопроса
    total_reviews = db.Column(db.Integer, default=0)  # Общее количество повторений
    consecutive_correct = db.Column(db.Integer, default=0)  # Подряд правильных ответов
    consecutive_incorrect = db.Column(db.Integer, default=0)  # Подряд неправильных ответов
    
    # IRT данные (опционально)
    irt_difficulty = db.Column(db.Float, nullable=True)
    user_ability = db.Column(db.Float, nullable=True)
    
    # Статус
    is_active = db.Column(db.Boolean, default=True)
    
    # Уникальное ограничение
    __table_args__ = (db.UniqueConstraint('user_id', 'question_id', name='_user_question_sr_uc'),)
    
    # Связи
    user = db.relationship('User', backref='spaced_repetition_items')
    question = db.relationship('Question', backref='spaced_repetition_items')
    
    def update_after_review(self, quality: int, user_ability: float = None):
        """
        Обновление элемента после повторения (SM-2 алгоритм)
        
        Args:
            quality: Качество ответа (0-5)
            user_ability: IRT способность пользователя (опционально)
        """
        self.quality = quality
        self.last_review = datetime.now(timezone.utc)
        self.total_reviews += 1
        
        # Обновляем среднее качество
        if self.average_quality == 0:
            self.average_quality = quality
        else:
            self.average_quality = (self.average_quality * (self.total_reviews - 1) + quality) / self.total_reviews
        
        # Обновляем счетчики подряд правильных/неправильных ответов
        if quality >= 3:  # Правильный ответ
            self.consecutive_correct += 1
            self.consecutive_incorrect = 0
        else:  # Неправильный ответ
            self.consecutive_incorrect += 1
            self.consecutive_correct = 0
        
        # Применяем SM-2 алгоритм
        self._apply_sm2_algorithm(quality)
        
        # Обновляем IRT данные
        if user_ability is not None:
            self.user_ability = user_ability
    
    def _apply_sm2_algorithm(self, quality: int):
        """Применение SM-2 алгоритма"""
        # Обновляем фактор легкости
        if quality >= 3:  # Правильный ответ
            self.ease_factor = max(1.3, self.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))
        else:  # Неправильный ответ
            self.ease_factor = max(1.3, self.ease_factor - 0.2)
        
        # Обновляем количество повторений
        if quality >= 3:
            self.repetitions += 1
        else:
            self.repetitions = 0
        
        # Рассчитываем новый интервал
        if self.repetitions == 0:
            self.interval = 1
        elif self.repetitions == 1:
            self.interval = 6
        else:
            self.interval = int(self.interval * self.ease_factor)
        
        # Рассчитываем дату следующего повторения
        self.next_review = datetime.now(timezone.utc) + timedelta(days=self.interval)
    
    def is_due(self) -> bool:
        """Проверка, готов ли элемент к повторению"""
        # Убеждаемся, что next_review имеет timezone
        if self.next_review.tzinfo is None:
            next_review = self.next_review.replace(tzinfo=timezone.utc)
        else:
            next_review = self.next_review
        return datetime.now(timezone.utc) >= next_review
    
    def get_days_overdue(self) -> int:
        """Количество дней просрочки"""
        if not self.is_due():
            return 0
        # Убеждаемся, что next_review имеет timezone
        if self.next_review.tzinfo is None:
            next_review = self.next_review.replace(tzinfo=timezone.utc)
        else:
            next_review = self.next_review
        return (datetime.now(timezone.utc) - next_review).days
    
    def get_priority_score(self) -> float:
        """Расчет приоритета для повторения"""
        # Базовый приоритет на основе просрочки
        days_overdue = self.get_days_overdue()
        base_priority = days_overdue / max(1, self.interval)
        
        # Корректировка на основе качества ответов
        quality_factor = 1.0
        if self.average_quality < 3.0:
            quality_factor = 1.5  # Проблемные вопросы получают приоритет
        
        # Корректировка на основе IRT сложности
        difficulty_factor = 1.0
        if self.irt_difficulty and self.irt_difficulty > 1.0:
            difficulty_factor = 1.3  # Сложные вопросы получают приоритет
        
        return base_priority * quality_factor * difficulty_factor
    
    def to_dict(self) -> dict:
        """Преобразование в словарь"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'question_id': self.question_id,
            'ease_factor': self.ease_factor,
            'interval': self.interval,
            'repetitions': self.repetitions,
            'quality': self.quality,
            'average_quality': self.average_quality,
            'next_review': self.next_review.isoformat() if self.next_review else None,
            'last_review': self.last_review.isoformat() if self.last_review else None,
            'domain': self.domain,
            'total_reviews': self.total_reviews,
            'consecutive_correct': self.consecutive_correct,
            'consecutive_incorrect': self.consecutive_incorrect,
            'is_due': self.is_due(),
            'days_overdue': self.get_days_overdue(),
            'priority_score': self.get_priority_score()
        }
    
    def __repr__(self):
        return f'<SpacedRepetitionItem User:{self.user_id} Question:{self.question_id} Interval:{self.interval} Due:{self.is_due()}>'


class StudySessionResponse(db.Model):
    """Detailed responses within study sessions for IRT feedback"""
    __tablename__ = 'study_session_response'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('study_session.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    is_correct = db.Column(db.Boolean, nullable=False)
    response_time = db.Column(db.Integer)  # milliseconds
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    session = db.relationship('StudySession', backref='responses')
    question = db.relationship('Question')
    
    def __repr__(self):
        return f'<StudySessionResponse {self.session_id}-{self.question_id}: {self.is_correct}>'
    
    @property
    def response_time_seconds(self):
        """Convert response time to seconds"""
        return self.response_time / 1000 if self.response_time else None

# ========================================
# CRM SYSTEM MODELS
# ========================================

class Profession(db.Model):
    """Profession model for managing different medical professions"""
    __tablename__ = 'profession'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    name_nl = db.Column(db.String(100), nullable=True)
    code = db.Column(db.String(20), unique=True, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # medical, dental, pharmacy
    big_exam_required = db.Column(db.Boolean, default=True)
    description = db.Column(db.Text, nullable=True)
    requirements = db.Column(db.Text, nullable=True)  # JSON string
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    specializations = db.relationship('ProfessionSpecialization', backref='profession', lazy='dynamic', cascade='all, delete-orphan')
    profession_contacts = db.relationship('Contact', lazy='dynamic')
    
    def __repr__(self):
        return f'<Profession {self.code}: {self.name}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'name_nl': self.name_nl,
            'code': self.code,
            'category': self.category,
            'big_exam_required': self.big_exam_required,
            'description': self.description,
            'requirements': self.requirements,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ProfessionSpecialization(db.Model):
    """Specialization model for professions"""
    __tablename__ = 'profession_specialization'
    
    id = db.Column(db.Integer, primary_key=True)
    profession_id = db.Column(db.Integer, db.ForeignKey('profession.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    name_nl = db.Column(db.String(100), nullable=True)
    code = db.Column(db.String(20), nullable=True)
    requirements = db.Column(db.Text, nullable=True)  # JSON string
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ProfessionSpecialization {self.name}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'profession_id': self.profession_id,
            'name': self.name,
            'name_nl': self.name_nl,
            'code': self.code,
            'requirements': self.requirements,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Contact(db.Model):
    """Contact model for CRM system"""
    __tablename__ = 'contact'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Basic information
    full_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    
    # Professional information
    profession_id = db.Column(db.Integer, db.ForeignKey('profession.id'), nullable=True)
    workplace = db.Column(db.String(255), nullable=True)
    big_number = db.Column(db.String(20), nullable=True)  # BIG registration number
    
    # CRM fields
    contact_status = db.Column(db.String(50), default='lead')  # lead, prospect, client, inactive
    lead_source = db.Column(db.String(100), nullable=True)  # website, referral, digid, social_media
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Communication tracking
    last_contact_date = db.Column(db.DateTime, nullable=True)
    next_followup_date = db.Column(db.DateTime, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    # Analytics
    registration_date = db.Column(db.DateTime, default=datetime.utcnow)
    registration_source = db.Column(db.String(100), nullable=True)
    first_visit_country = db.Column(db.String(100), nullable=True)
    device_type = db.Column(db.String(50), nullable=True)
    browser = db.Column(db.String(50), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], backref='contact_profile')
    assigned_user = db.relationship('User', foreign_keys=[assigned_to], backref='assigned_contacts')
    profession = db.relationship('Profession', foreign_keys=[profession_id], overlaps="profession_contacts")
    
    def __repr__(self):
        return f'<Contact {self.full_name}: {self.email}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'profession_id': self.profession_id,
            'profession_name': self.profession.name if self.profession else None,
            'workplace': self.workplace,
            'big_number': self.big_number,
            'contact_status': self.contact_status,
            'lead_source': self.lead_source,
            'assigned_to': self.assigned_to,
            'assigned_user_name': self.assigned_user.get_display_name() if self.assigned_user else None,
            'last_contact_date': self.last_contact_date.isoformat() if self.last_contact_date else None,
            'next_followup_date': self.next_followup_date.isoformat() if self.next_followup_date else None,
            'notes': self.notes,
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
        """Get display name for contact status"""
        status_map = {
            'lead': 'Лид',
            'prospect': 'Потенциальный клиент',
            'client': 'Клиент',
            'inactive': 'Неактивный'
        }
        return status_map.get(self.contact_status, self.contact_status)
    
    @property
    def days_since_last_contact(self):
        """Calculate days since last contact"""
        if not self.last_contact_date:
            return None
        return (datetime.utcnow() - self.last_contact_date).days
    
    @property
    def days_until_followup(self):
        """Calculate days until next followup"""
        if not self.next_followup_date:
            return None
        return (self.next_followup_date - datetime.utcnow()).days

# ========================================
# ADVANCED ANALYTICS MODELS
# ========================================

class CountryAnalytics(db.Model):
    """Analytics model for country-based statistics"""
    __tablename__ = 'country_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    country_code = db.Column(db.String(2), nullable=False, index=True)
    country_name = db.Column(db.String(100), nullable=False)
    
    # User statistics
    total_users = db.Column(db.Integer, default=0)
    active_users = db.Column(db.Integer, default=0)
    new_users_today = db.Column(db.Integer, default=0)
    new_users_this_week = db.Column(db.Integer, default=0)
    new_users_this_month = db.Column(db.Integer, default=0)
    
    # Conversion metrics
    conversion_rate = db.Column(db.Float, default=0.0)  # registration to active
    completion_rate = db.Column(db.Float, default=0.0)  # course completion
    exam_pass_rate = db.Column(db.Float, default=0.0)   # exam success
    
    # Engagement metrics
    avg_session_duration = db.Column(db.Float, default=0.0)  # in minutes
    avg_pages_per_session = db.Column(db.Float, default=0.0)
    bounce_rate = db.Column(db.Float, default=0.0)
    
    # Revenue metrics (if applicable)
    total_revenue = db.Column(db.Float, default=0.0)
    avg_revenue_per_user = db.Column(db.Float, default=0.0)
    
    # Timestamps
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CountryAnalytics {self.country_code}: {self.country_name}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
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
    """Analytics model for device and browser statistics"""
    __tablename__ = 'device_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Device information
    device_category = db.Column(db.String(50), nullable=False)  # mobile, desktop, tablet
    device_type = db.Column(db.String(100), nullable=True)      # iPhone, Samsung, etc.
    browser = db.Column(db.String(50), nullable=False)          # Chrome, Safari, Firefox
    browser_version = db.Column(db.String(20), nullable=True)
    os = db.Column(db.String(50), nullable=False)               # Windows, macOS, iOS, Android
    os_version = db.Column(db.String(20), nullable=True)
    screen_resolution = db.Column(db.String(20), nullable=True) # 1920x1080, 375x667
    
    # Usage statistics
    users_count = db.Column(db.Integer, default=0)
    sessions_count = db.Column(db.Integer, default=0)
    page_views_count = db.Column(db.Integer, default=0)
    
    # Performance metrics
    avg_page_load_time = db.Column(db.Float, default=0.0)  # in seconds
    bounce_rate = db.Column(db.Float, default=0.0)
    avg_session_duration = db.Column(db.Float, default=0.0)  # in minutes
    avg_pages_per_session = db.Column(db.Float, default=0.0)
    
    # Conversion metrics
    conversion_rate = db.Column(db.Float, default=0.0)
    completion_rate = db.Column(db.Float, default=0.0)
    
    # Timestamps
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DeviceAnalytics {self.device_category} {self.browser} {self.os}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
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
    """Analytics model for profession-based statistics"""
    __tablename__ = 'profession_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    profession_id = db.Column(db.Integer, db.ForeignKey('profession.id'), nullable=False)
    
    # Registration statistics
    total_registrations = db.Column(db.Integer, default=0)
    new_registrations_today = db.Column(db.Integer, default=0)
    new_registrations_this_week = db.Column(db.Integer, default=0)
    new_registrations_this_month = db.Column(db.Integer, default=0)
    
    # Activity statistics
    active_users = db.Column(db.Integer, default=0)
    users_with_progress = db.Column(db.Integer, default=0)
    users_completed_courses = db.Column(db.Integer, default=0)
    
    # Learning metrics
    avg_progress = db.Column(db.Float, default=0.0)  # percentage
    avg_time_spent = db.Column(db.Float, default=0.0)  # in hours
    avg_lessons_completed = db.Column(db.Float, default=0.0)
    
    # Exam metrics
    total_exam_attempts = db.Column(db.Integer, default=0)
    successful_exam_attempts = db.Column(db.Integer, default=0)
    exam_pass_rate = db.Column(db.Float, default=0.0)
    avg_exam_score = db.Column(db.Float, default=0.0)
    
    # Engagement metrics
    avg_session_duration = db.Column(db.Float, default=0.0)  # in minutes
    avg_sessions_per_user = db.Column(db.Float, default=0.0)
    retention_rate_7d = db.Column(db.Float, default=0.0)  # 7-day retention
    retention_rate_30d = db.Column(db.Float, default=0.0)  # 30-day retention
    
    # Timestamps
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    profession = db.relationship('Profession', backref='analytics')
    
    def __repr__(self):
        return f'<ProfessionAnalytics {self.profession_id}>'

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
    activity_metadata = db.Column(db.Text, nullable=True, comment='Дополнительные данные в JSON')
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
        return f'<ContactActivity {self.activity_type}: {self.contact.full_name if self.contact else "Unknown"}>'
    
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
            'activity_metadata': self.activity_metadata,
            'attachments': self.attachments,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
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

class AnalyticsEvent(db.Model):
    """Model for tracking custom analytics events"""
    __tablename__ = 'analytics_event'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Event details
    event_name = db.Column(db.String(100), nullable=False, index=True)
    event_category = db.Column(db.String(50), nullable=False)  # user, system, error, performance
    event_action = db.Column(db.String(100), nullable=False)   # click, view, submit, error
    event_label = db.Column(db.String(200), nullable=True)     # additional context
    
    # Event data
    event_data = db.Column(db.Text, nullable=True)  # JSON string
    event_value = db.Column(db.Float, nullable=True)  # numeric value
    
    # Context information
    page_url = db.Column(db.String(500), nullable=True)
    referrer_url = db.Column(db.String(500), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    
    # Device and location
    device_type = db.Column(db.String(50), nullable=True)
    browser = db.Column(db.String(50), nullable=True)
    os = db.Column(db.String(50), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = db.relationship('User', backref='analytics_events')
    
    def __repr__(self):
        return f'<AnalyticsEvent {self.event_name}: {self.event_action}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_email': self.user.email if self.user else None,
            'event_name': self.event_name,
            'event_category': self.event_category,
            'event_action': self.event_action,
            'event_label': self.event_label,
            'event_data': self.event_data,
            'event_value': self.event_value,
            'page_url': self.page_url,
            'referrer_url': self.referrer_url,
            'user_agent': self.user_agent,
            'ip_address': self.ip_address,
            'device_type': self.device_type,
            'browser': self.browser,
            'os': self.os,
            'country': self.country,
            'city': self.city,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# ========================================
# ADMINISTRATIVE TOOLS MODELS
# ========================================

class AdminAuditLog(db.Model):
    """Audit log for all admin actions"""
    __tablename__ = 'admin_audit_log'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Action details
    action = db.Column(db.String(100), nullable=False)  # 'user_created', 'bulk_delete', 'data_export'
    target_type = db.Column(db.String(50), nullable=False)  # 'user', 'contact', 'profession', 'system'
    target_id = db.Column(db.Integer, nullable=True)  # ID of affected record
    
    # Details
    details = db.Column(db.Text, nullable=True)  # JSON string with action details
    old_values = db.Column(db.Text, nullable=True)  # JSON string with old values
    new_values = db.Column(db.Text, nullable=True)  # JSON string with new values
    
    # Context
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    request_url = db.Column(db.String(500), nullable=True)
    request_method = db.Column(db.String(10), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    admin_user = db.relationship('User', backref='admin_audit_logs')
    
    def __repr__(self):
        return f'<AdminAuditLog {self.action}: {self.target_type}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'admin_user_id': self.admin_user_id,
            'admin_email': self.admin_user.email if self.admin_user else None,
            'action': self.action,
            'target_type': self.target_type,
            'target_id': self.target_id,
            'details': self.details,
            'old_values': self.old_values,
            'new_values': self.new_values,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'request_url': self.request_url,
            'request_method': self.request_method,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class SystemHealthLog(db.Model):
    """System health monitoring log"""
    __tablename__ = 'system_health_log'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Health metrics
    cpu_usage = db.Column(db.Float, nullable=True)  # CPU usage percentage
    memory_usage = db.Column(db.Float, nullable=True)  # Memory usage percentage
    disk_usage = db.Column(db.Float, nullable=True)  # Disk usage percentage
    database_connections = db.Column(db.Integer, nullable=True)  # Active DB connections
    response_time = db.Column(db.Float, nullable=True)  # Average response time in ms
    
    # Application metrics
    active_users = db.Column(db.Integer, nullable=True)
    total_requests = db.Column(db.Integer, nullable=True)
    error_count = db.Column(db.Integer, nullable=True)
    cache_hit_rate = db.Column(db.Float, nullable=True)
    
    # Status
    status = db.Column(db.String(20), default='healthy')  # healthy, warning, critical
    alerts = db.Column(db.Text, nullable=True)  # JSON string with alerts
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<SystemHealthLog {self.status}: {self.created_at}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'disk_usage': self.disk_usage,
            'database_connections': self.database_connections,
            'response_time': self.response_time,
            'active_users': self.active_users,
            'total_requests': self.total_requests,
            'error_count': self.error_count,
            'cache_hit_rate': self.cache_hit_rate,
            'status': self.status,
            'alerts': self.alerts,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class DatabaseBackup(db.Model):
    """Database backup records"""
    __tablename__ = 'database_backup'
    
    id = db.Column(db.Integer, primary_key=True)
    admin_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Backup details
    backup_name = db.Column(db.String(200), nullable=False)
    backup_type = db.Column(db.String(50), nullable=False)  # 'manual', 'scheduled', 'before_deploy'
    file_path = db.Column(db.String(500), nullable=True)  # Path to backup file
    file_size = db.Column(db.BigInteger, nullable=True)  # File size in bytes
    
    # Backup status
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    error_message = db.Column(db.Text, nullable=True)
    
    # Backup metadata
    tables_count = db.Column(db.Integer, nullable=True)
    records_count = db.Column(db.Integer, nullable=True)
    backup_duration = db.Column(db.Float, nullable=True)  # Duration in seconds
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)  # When backup should be deleted
    
    # Relationships
    admin_user = db.relationship('User', backref='database_backups')
    
    def __repr__(self):
        return f'<DatabaseBackup {self.backup_name}: {self.status}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'admin_user_id': self.admin_user_id,
            'admin_email': self.admin_user.email if self.admin_user else None,
            'backup_name': self.backup_name,
            'backup_type': self.backup_type,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'status': self.status,
            'error_message': self.error_message,
            'tables_count': self.tables_count,
            'records_count': self.records_count,
            'backup_duration': self.backup_duration,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }

class EmailTemplate(db.Model):
    """Email templates for communication"""
    __tablename__ = 'email_template'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Template details
    name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    template_type = db.Column(db.String(50), nullable=False)  # 'welcome', 'reminder', 'notification', 'marketing'
    
    # Content
    html_content = db.Column(db.Text, nullable=False)
    text_content = db.Column(db.Text, nullable=True)
    
    # Template variables (JSON)
    variables = db.Column(db.Text, nullable=True)  # Available template variables
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_system = db.Column(db.Boolean, default=False)  # System templates cannot be deleted
    
    # Usage statistics
    sent_count = db.Column(db.Integer, default=0)
    last_sent_at = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<EmailTemplate {self.name}: {self.template_type}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'name': self.name,
            'subject': self.subject,
            'template_type': self.template_type,
            'html_content': self.html_content,
            'text_content': self.text_content,
            'variables': self.variables,
            'is_active': self.is_active,
            'is_system': self.is_system,
            'sent_count': self.sent_count,
            'last_sent_at': self.last_sent_at.isoformat() if self.last_sent_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

# EmailCampaign model removed - using CommunicationCampaign instead

class SystemNotification(db.Model):
    """System notifications and alerts"""
    __tablename__ = 'system_notification'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Notification details
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # 'info', 'warning', 'error', 'success'
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, critical
    
    # Target
    target_users = db.Column(db.Text, nullable=True)  # JSON with user IDs or 'all'
    target_roles = db.Column(db.Text, nullable=True)  # JSON with roles
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Actions
    action_url = db.Column(db.String(500), nullable=True)
    action_text = db.Column(db.String(100), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<SystemNotification {self.title}: {self.notification_type}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'notification_type': self.notification_type,
            'priority': self.priority,
            'target_users': self.target_users,
            'target_roles': self.target_roles,
            'is_read': self.is_read,
            'is_active': self.is_active,
            'action_url': self.action_url,
            'action_text': self.action_text,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }

# Communication Models
class CommunicationHistory(db.Model):
    """История коммуникации с пользователями и контактами"""
    __tablename__ = 'communication_history'
    
    id = db.Column(db.Integer, primary_key=True)
    recipient_type = db.Column(db.String(20), nullable=False)
    recipient_id = db.Column(db.Integer, nullable=False)
    recipient_email = db.Column(db.String(255), nullable=False)
    recipient_name = db.Column(db.String(255), nullable=True)
    sender_id = db.Column(db.Integer, nullable=False)
    sender_name = db.Column(db.String(255), nullable=True)
    subject = db.Column(db.String(500), nullable=False)
    message = db.Column(db.Text, nullable=False)
    email_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='sent')
    external_id = db.Column(db.String(255), nullable=True)
    action_url = db.Column(db.String(500), nullable=True)
    action_text = db.Column(db.String(255), nullable=True)
    template_used = db.Column(db.String(100), nullable=True)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    delivered_at = db.Column(db.DateTime, nullable=True)
    opened_at = db.Column(db.DateTime, nullable=True)
    clicked_at = db.Column(db.DateTime, nullable=True)
    extra_data = db.Column(db.JSON, nullable=True)
    
    def __repr__(self):
        return f'<CommunicationHistory {self.id}: {self.recipient_email}>'


class CommunicationCampaign(db.Model):
    """Кампании массовых рассылок"""
    __tablename__ = 'communication_campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    email_type = db.Column(db.String(50), nullable=False)
    subject = db.Column(db.String(500), nullable=False)
    message = db.Column(db.Text, nullable=False)
    action_url = db.Column(db.String(500), nullable=True)
    action_text = db.Column(db.String(255), nullable=True)
    target_type = db.Column(db.String(20), nullable=False)
    target_filters = db.Column(db.JSON, nullable=True)
    status = db.Column(db.String(20), default='draft')
    scheduled_at = db.Column(db.DateTime, nullable=True)
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    total_recipients = db.Column(db.Integer, default=0)
    sent_count = db.Column(db.Integer, default=0)
    delivered_count = db.Column(db.Integer, default=0)
    opened_count = db.Column(db.Integer, default=0)
    clicked_count = db.Column(db.Integer, default=0)
    failed_count = db.Column(db.Integer, default=0)
    created_by = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CommunicationCampaign {self.id}: {self.name}>'


class Invitation(db.Model):
    """Модель для системы приглашений пользователей"""
    __tablename__ = 'invitation'
    
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    invited_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Данные приглашения
    email = db.Column(db.String(120), nullable=False, index=True)
    token = db.Column(db.String(255), nullable=False, unique=True, index=True)
    
    # Статус приглашения
    status = db.Column(db.String(20), default='pending')  # pending, accepted, expired, cancelled
    expires_at = db.Column(db.DateTime, nullable=False)
    
    # Дополнительная информация
    message = db.Column(db.Text, nullable=True)  # Персональное сообщение от админа
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Созданный пользователь
    
    # Временные метки
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    accepted_at = db.Column(db.DateTime, nullable=True)
    
    # Связи
    contact = db.relationship('Contact', backref='invitations')
    inviter = db.relationship('User', foreign_keys=[invited_by], backref='sent_invitations')
    created_user = db.relationship('User', foreign_keys=[user_id], backref='invitation_created_user')
    
    def __repr__(self):
        return f'<Invitation {self.email}: {self.status}>'
    
    def is_expired(self):
        """Проверка истечения срока действия приглашения"""
        return datetime.utcnow() > self.expires_at
    
    def is_valid(self):
        """Проверка валидности приглашения"""
        return self.status == 'pending' and not self.is_expired()
    
    def to_dict(self):
        """Преобразование в словарь для JSON"""
        return {
            'id': self.id,
            'contact_id': self.contact_id,
            'contact_name': self.contact.full_name if self.contact else None,
            'email': self.email,
            'status': self.status,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'accepted_at': self.accepted_at.isoformat() if self.accepted_at else None,
            'is_expired': self.is_expired(),
            'is_valid': self.is_valid()
        }

# ========================================
# REGISTRATION LOGGING
# ========================================

class RegistrationLog(db.Model):
    """Model for storing registration logs in database"""
    __tablename__ = 'registration_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False, index=True)  # registration_started, validation_error, etc.
    registration_type = db.Column(db.String(50), nullable=False, index=True)  # quick_registration, full_registration, etc.
    level = db.Column(db.String(20), nullable=False, index=True)  # INFO, WARNING, ERROR
    
    # Context data
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    referrer = db.Column(db.Text, nullable=True)
    url = db.Column(db.Text, nullable=True)
    method = db.Column(db.String(10), nullable=True)
    
    # User context
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)
    user_email = db.Column(db.String(120), nullable=True, index=True)
    user_type = db.Column(db.String(20), nullable=True)  # authenticated, anonymous
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)

class RegistrationVisitor(db.Model):
    """Model for tracking visitors to registration pages"""
    __tablename__ = 'registration_visitors'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Visitor identification
    ip_address = db.Column(db.String(45), nullable=False, index=True)
    session_id = db.Column(db.String(100), nullable=True, index=True)
    
    # Visit details
    page_type = db.Column(db.String(50), nullable=False, index=True)  # quick_register, full_register, login
    entry_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    exit_time = db.Column(db.DateTime, nullable=True)
    time_on_page = db.Column(db.Integer, nullable=True)  # seconds
    
    # Browser/Device info
    user_agent = db.Column(db.Text, nullable=True)
    referrer = db.Column(db.Text, nullable=True)
    language = db.Column(db.String(10), nullable=True)
    
    # Interaction tracking
    email_entered = db.Column(db.String(120), nullable=True, index=True)  # Partial email if entered
    email_entered_at = db.Column(db.DateTime, nullable=True)
    first_name_entered = db.Column(db.String(100), nullable=True, index=True)  # First name if entered
    last_name_entered = db.Column(db.String(100), nullable=True, index=True)  # Last name if entered
    name_entered_at = db.Column(db.DateTime, nullable=True)
    form_started = db.Column(db.Boolean, default=False, nullable=False)
    form_abandoned = db.Column(db.Boolean, default=False, nullable=False)
    registration_completed = db.Column(db.Boolean, default=False, nullable=False)
    
    # Additional data
    country = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    
    # Foreign key to user if registration completed
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)

class RegistrationAnalytics(db.Model):
    """Model for aggregated registration analytics"""
    __tablename__ = 'registration_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Time period
    date = db.Column(db.Date, nullable=False, index=True)
    hour = db.Column(db.Integer, nullable=True, index=True)  # 0-23
    
    # Metrics
    page_visits = db.Column(db.Integer, default=0, nullable=False)
    unique_visitors = db.Column(db.Integer, default=0, nullable=False)
    email_entries = db.Column(db.Integer, default=0, nullable=False)
    form_starts = db.Column(db.Integer, default=0, nullable=False)
    form_abandonments = db.Column(db.Integer, default=0, nullable=False)
    successful_registrations = db.Column(db.Integer, default=0, nullable=False)
    
    # Conversion rates (stored as percentages * 100 for precision)
    email_to_form_rate = db.Column(db.Integer, nullable=True)  # (form_starts / email_entries) * 10000
    form_to_success_rate = db.Column(db.Integer, nullable=True)  # (successful_registrations / form_starts) * 10000
    
    # Page type breakdown
    page_type = db.Column(db.String(50), nullable=False, index=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Event specific data
    field = db.Column(db.String(100), nullable=True)  # for validation errors
    error_code = db.Column(db.String(100), nullable=True)  # for business logic errors
    error_message = db.Column(db.Text, nullable=True)
    form_data = db.Column(db.Text, nullable=True)  # JSON string of sanitized form data
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'event_type': self.event_type,
            'registration_type': self.registration_type,
            'level': self.level,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'referrer': self.referrer,
            'url': self.url,
            'method': self.method,
            'user_id': self.user_id,
            'user_email': self.user_email,
            'user_type': self.user_type,
            'field': self.field,
            'error_code': self.error_code,
            'error_message': self.error_message,
            'form_data': json.loads(self.form_data) if self.form_data else None,
            'created_at': self.created_at.isoformat()
        }


class ProfessionClick(db.Model, JSONSerializableMixin):
    """Track profession card clicks on BIG info page"""
    __tablename__ = 'profession_clicks'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Click data
    profession = db.Column(db.String(100), nullable=False, index=True)
    profession_type = db.Column(db.String(20), nullable=False, index=True)  # 'eu' or 'non-eu'
    target_url = db.Column(db.String(500), nullable=False)
    page_url = db.Column(db.String(500), nullable=False)
    
    # User context
    ip_address = db.Column(db.String(45), nullable=False, index=True)
    user_agent = db.Column(db.Text, nullable=True)
    language = db.Column(db.String(10), nullable=True, index=True)
    
    # User identification (if logged in)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, index=True)
    user_email = db.Column(db.String(120), nullable=True, index=True)
    
    # Timestamps
    clicked_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'profession': self.profession,
            'profession_type': self.profession_type,
            'target_url': self.target_url,
            'page_url': self.page_url,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'language': self.language,
            'user_id': self.user_id,
            'user_email': self.user_email,
            'clicked_at': self.clicked_at.isoformat(),
            'created_at': self.created_at.isoformat()
        }


class IncomingEmail(db.Model):
    """Incoming emails from POP/IMAP"""
    __tablename__ = 'incoming_emails'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Email details
    message_id = db.Column(db.String(255), unique=True, nullable=False)
    subject = db.Column(db.String(500), nullable=False)
    sender_email = db.Column(db.String(255), nullable=False)
    sender_name = db.Column(db.String(255), nullable=True)
    recipient_email = db.Column(db.String(255), nullable=False)
    source_account = db.Column(db.String(50), nullable=False, default='info')  # info, support, etc.
    
    # Content
    html_content = db.Column(db.Text, nullable=True)
    text_content = db.Column(db.Text, nullable=True)
    
    # Email metadata
    date_received = db.Column(db.DateTime, nullable=False)
    size_bytes = db.Column(db.Integer, default=0)
    has_attachments = db.Column(db.Boolean, default=False)
    attachment_count = db.Column(db.Integer, default=0)
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    is_important = db.Column(db.Boolean, default=False)
    is_spam = db.Column(db.Boolean, default=False)
    is_deleted = db.Column(db.Boolean, default=False)
    
    # Categories/Tags
    category = db.Column(db.String(50), nullable=True)  # support, sales, general, etc.
    tags = db.Column(db.Text, nullable=True)  # JSON array of tags
    
    # Response tracking
    is_replied = db.Column(db.Boolean, default=False)
    reply_sent_at = db.Column(db.DateTime, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<IncomingEmail {self.message_id}: {self.subject}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'message_id': self.message_id,
            'subject': self.subject,
            'sender_email': self.sender_email,
            'sender_name': self.sender_name,
            'recipient_email': self.recipient_email,
            'source_account': self.source_account,
            'html_content': self.html_content,
            'text_content': self.text_content,
            'date_received': self.date_received.isoformat() if self.date_received else None,
            'size_bytes': self.size_bytes,
            'has_attachments': self.has_attachments,
            'attachment_count': self.attachment_count,
            'is_read': self.is_read,
            'is_important': self.is_important,
            'is_spam': self.is_spam,
            'is_deleted': self.is_deleted,
            'category': self.category,
            'tags': self.tags,
            'is_replied': self.is_replied,
            'reply_sent_at': self.reply_sent_at.isoformat() if self.reply_sent_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class EmailAttachment(db.Model):
    """Email attachments"""
    __tablename__ = 'email_attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    email_id = db.Column(db.Integer, db.ForeignKey('incoming_emails.id'), nullable=False)
    
    # Attachment details
    filename = db.Column(db.String(255), nullable=False)
    content_type = db.Column(db.String(100), nullable=False)
    size_bytes = db.Column(db.Integer, nullable=False)
    file_path = db.Column(db.String(500), nullable=True)  # Path to stored file
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    email = db.relationship('IncomingEmail', backref='attachments')
    
    def __repr__(self):
        return f'<EmailAttachment {self.filename}>'
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'email_id': self.email_id,
            'filename': self.filename,
            'content_type': self.content_type,
            'size_bytes': self.size_bytes,
            'file_path': self.file_path,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
