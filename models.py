# models.py
import json
from extensions import db
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.types import Text
from datetime import datetime, timezone
from flask import g
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
import logging

class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    role = db.Column(db.String(20), default='user')
    has_subscription = db.Column(db.Boolean, default=False)
    subscription_expires = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    language = db.Column(db.String(5), default='en')
    # Отношения
    progress = db.relationship('UserProgress', backref='user', lazy='dynamic',
                              cascade='all, delete-orphan')
    # Поля для онбординга
    onboarding_completed = db.Column(db.Boolean, default=False)
    guide_completed = db.Column(db.Boolean, default=False)
    skip_guides = db.Column(db.Boolean, default=False)
    @property
    def is_admin(self):
        """Возвращает True, если пользователь имеет роль admin."""
        return self.role == 'admin'
    # Дополнительные методы
    def __repr__(self):
        return f'<User {self.username}>'
    
    def get_completed_lessons(self):
        """Возвращает список завершенных уроков пользователя."""
        return self.progress.filter_by(completed=True).all()
    
    def get_progress_for_module(self, module_id):
        """Возвращает прогресс пользователя для конкретного модуля."""
        from sqlalchemy import func
        from models import Lesson
        # Находим все уроки в модуле
        lessons_subquery = db.session.query(Lesson.id).filter_by(module_id=module_id).subquery()
        # Подсчитываем прогресс
        completed = self.progress.filter(
            UserProgress.lesson_id.in_(lessons_subquery),
            UserProgress.completed == True
         ).count()
        total = db.session.query(func.count(Lesson.id)).filter_by(module_id=module_id).scalar() or 0
        return {
            'completed': completed,
            'total': total,
            'percent': int((completed / total) * 100) if total > 0 else 0
         }

# --- Модель LearningPath (Уровень 1: 5 Категорий Экзамена) ---
class LearningPath(db.Model):
    __tablename__ = 'learning_path'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, default=0)
    icon = db.Column(db.String(50), default="list-task")
    subjects = db.relationship("Subject", backref="learning_path", lazy='dynamic', cascade="all, delete-orphan")
    exam_phase = db.Column(db.Integer, default=1) # Соответствие фазе экзамена
    def __repr__(self): return f'<LearningPath {self.name}>'
    is_active = db.Column(db.Boolean, default=True) 

# --- Модель Subject (Уровень 2: Большой Предмет/Раздел) ---
class Subject(db.Model):
    __tablename__ = 'subject'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, default=0)
    icon = db.Column(db.String(50), default="folder2-open")
    learning_path_id = db.Column(db.Integer, db.ForeignKey("learning_path.id", ondelete='CASCADE'), nullable=False)
    module = db.relationship("Module", backref="subject", lazy='dynamic', cascade="all, delete-orphan")
    final_test = db.relationship("Test", backref="subject_final_test_owner", lazy=True, uselist=False, cascade="all, delete-orphan", foreign_keys='Test.subject_final_test_id') # Changed backref for clarity
    def __repr__(self): return f'<Subject {self.id}: {self.name} (Path ID: {self.learning_path_id})>'

# --- Модель Module (Уровень 3: Подтема) ---
class Module(db.Model):
    __tablename__ = 'module'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False) # Название подтемы
    description = db.Column(db.Text, nullable=True)
    order = db.Column(db.Integer, default=0) # Порядок внутри Subject
    icon = db.Column(db.String(50), default="file-earmark-text")
    module_type = db.Column(db.String(50), default='content', index=True)
    is_premium = db.Column(db.Boolean, default=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subject.id", ondelete='CASCADE'), nullable=False)
    is_final_test = db.Column(db.Boolean, default=False, nullable=False, index=True)
    lessons = db.relationship("Lesson", backref="module", lazy='dynamic', cascade="all, delete-orphan")
    # Связь с промежуточными тестами в модуле (если Test.module_intermediate_test_id используется)
    intermediate_tests = db.relationship("Test", backref="module_intermediate_test_owner", lazy='dynamic', foreign_keys='Test.module_intermediate_test_id')
    def __repr__(self):
        final_status = "FINAL" if self.is_final_test else ""
        premium_status = "Premium" if self.is_premium else "Free"
        return f'<Module {self.id}: {self.title} (Subject ID: {self.subject_id}, {final_status}{premium_status})>'

# --- Новая иерархия контента ---
class ContentCategory(db.Model): # ПЕРЕИМЕНОВАНО из Category
    __tablename__ = 'categories' # Имя таблицы остается 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False)
    icon = db.Column(db.String(50), default='folder')
    order = db.Column(db.Integer, default=0)
    subcategories = db.relationship('ContentSubcategory', backref='content_category', lazy='dynamic', cascade="all, delete-orphan") # Используем новое имя ContentSubcategory и новый backref

class ContentSubcategory(db.Model): # ПЕРЕИМЕНОВАНО из Subcategory
    __tablename__ = 'subcategories' # Имя таблицы остается 'subcategories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False) # Ссылается на ContentCategory.__tablename__
    icon = db.Column(db.String(50), default='bookmark')
    order = db.Column(db.Integer, default=0)
    topics = db.relationship('ContentTopic', backref='content_subcategory', lazy='dynamic', cascade="all, delete-orphan") # Используем новое имя ContentTopic и новый backref

class ContentTopic(db.Model): # ПЕРЕИМЕНОВАНО из Topic (иерархического)
    __tablename__ = 'topics' # Имя таблицы остается 'topics'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False)
    subcategory_id = db.Column(db.Integer, db.ForeignKey('subcategories.id'), nullable=False) # Ссылается на ContentSubcategory.__tablename__
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)
    parent_topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=True) # Ссылка на родительскую тему
    
    # Исправленное отношение с Lesson
    lessons = db.relationship('Lesson', 
                             foreign_keys="Lesson.topic_id", # Определяем, какой внешний ключ использовать
                             backref='content_topic', 
                             lazy='dynamic', 
                             cascade="all, delete-orphan") 
    
    subtopics = db.relationship('ContentTopic', backref=db.backref('parent', remote_side=[id]), lazy='dynamic', cascade="all, delete-orphan") # Связь с подтемами
    __table_args__ = (db.UniqueConstraint('slug', 'subcategory_id', name='uc_topic_slug_subcategory'),)

# --- Модель Lesson (Уровень 4: Урок/Карточка/Мини-тест) ---
class Lesson(db.Model):
    __tablename__ = 'lessons'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text)
    content_type = db.Column(db.String(50))
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'))
    order = db.Column(db.Integer, default=0)
    
    # Добавляем внешний ключ для связи с ContentTopic
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'), nullable=True)
    
    # Другие поля для подтем
    subtopic = db.Column(db.String(255), nullable=True, index=True)
    subtopic_slug = db.Column(db.String(255), nullable=True, index=True)
    subtopic_order = db.Column(db.Integer, default=0)
    
    # Отношения
    progress = db.relationship('UserProgress', backref='lesson', lazy=True)
    
    def extract_subtopic(self):
        """Извлекает module_title из контента урока"""
        if not self.content:
            return None
        try:
            content_data = json.loads(self.content)
            # Прямой доступ (верхний уровень)
            if 'module_title' in content_data:
                return content_data.get('module_title')
            # Если контент - это карточка или тест
            if content_data.get('type') in ['learning', 'test']:
                return content_data.get('module_title')
            # Если контент содержит массив cards
            if 'cards' in content_data and content_data['cards']:
                return content_data['cards'][0].get('module_title')
            # Если контент содержит массив questions
            if 'questions' in content_data and content_data['questions']:
                return content_data['questions'][0].get('module_title')
        except (json.JSONDecodeError, AttributeError, KeyError, TypeError):
            pass
        return None
        
    def __repr__(self):
        return f'<Lesson {self.title}>'

class UserProgress(db.Model):
    __tablename__ = 'user_progress'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete='CASCADE'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey("lessons.id", ondelete='CASCADE'), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    time_spent = db.Column(db.Float, default=0.0)
    last_accessed = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    __table_args__ = (db.UniqueConstraint('user_id', 'lesson_id', name='_user_lesson_uc'),)
    
    def add_time(self, minutes):
        self.time_spent = (self.time_spent or 0.0) + minutes
        
    def __repr__(self):
        return f'<UserProgress User:{self.user_id} Lesson:{self.lesson_id} Done:{self.completed}>'

# --- Модели Category и Question (для хранения MCQ вопросов) ---
class QuestionCategory(db.Model): # ПЕРЕИМЕНОВАНО из Category (для вопросов)
    __tablename__ = 'category' # Имя таблицы остается 'category'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    questions = db.relationship('Question', backref='question_category', lazy='dynamic', cascade="all, delete-orphan") # Новый backref
    
    def __repr__(self): return f'<QuestionCategory {self.name}>' # Изменено имя класса в repr

class Question(db.Model):
    __tablename__ = 'question'
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    image_filename = db.Column(db.String(255), nullable=True)
    options = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.String(255), nullable=False)
    explanation = db.Column(db.Text, nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id', ondelete='CASCADE'), nullable=False, index=True) # Ссылается на QuestionCategory.__tablename__
    
    def get_options_list(self):
        if self.options:
            try: return json.loads(self.options)
            except json.JSONDecodeError: return []
        return []
        
    def check_answer(self, submitted_answer): 
        return str(submitted_answer) == str(self.correct_answer)
        
    def __repr__(self): 
        return f'<Question {self.id}: CatID={self.category_id}>'

# --- Модель Test ---
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

# --- Модель TestAttempt ---
class TestAttempt(db.Model):
    __tablename__ = 'test_attempt'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete='CASCADE'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey("test.id", ondelete='CASCADE'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey("question.id", ondelete='CASCADE'), nullable=False)
    selected_option = db.Column(db.String(255))
    is_correct = db.Column(db.Boolean)
    attempt_date = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    question = db.relationship("Question")
    
    def __repr__(self): 
        return f'<TestAttempt User:{self.user_id} Test:{self.test_id} Q:{self.question_id} Correct:{self.is_correct}>'

# --- Модель для хранения информации о дате экзамена ---
class UserExamDate(db.Model):
    __tablename__ = 'user_exam_date'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exam_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    user = db.relationship('User', backref=db.backref('exam_dates', lazy=True))

# --- Модели Форума ---
class ForumTopic(db.Model): # ПЕРЕИМЕНОВАНО из Topic (для форума)
    __tablename__ = 'topic' # Имя таблицы остается 'topic'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    views = db.Column(db.Integer, default=0)
    is_featured = db.Column(db.Boolean, default=False, index=True)
    category = db.Column(db.String(50), nullable=True, index=True) # This might need a ForeignKey to a ForumCategory model if you have one
    author = db.relationship('User', backref=db.backref('forum_topics', lazy='dynamic')) # backref 'forum_topics' in User model
    posts = db.relationship('Post', backref='forum_topic', lazy='dynamic', cascade="all, delete-orphan") # Новый backref
    
    def __repr__(self): 
        return f'<ForumTopic "{self.title[:30]}...">' 

class Post(db.Model):
    __tablename__ = 'post'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id', ondelete='CASCADE'), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=lambda: datetime.now(timezone.utc))
    author = db.relationship('User', backref=db.backref('forum_posts', lazy='dynamic')) # Ссылается на ForumTopic.__tablename__
    
    def __repr__(self): 
        return f'<Post {self.id} in Topic {self.topic_id}>'

# --- Virtual Patient Models ---
class VirtualPatientScenario(db.Model):
    __tablename__ = 'virtual_patient_scenario'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    difficulty = db.Column(db.String(20), default='medium')
    category = db.Column(db.String(50), nullable=True, index=True)
    timeframe = db.Column(db.Integer, default=0)
    max_score = db.Column(db.Integer, default=100)
    is_premium = db.Column(db.Boolean, default=False)
    is_published = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    scenario_data = db.Column(db.Text, nullable=False)
    attempts = db.relationship("VirtualPatientAttempt", backref="scenario", lazy='dynamic', cascade="all, delete-orphan")
    
    @property
    def localized_data(self):
        """Returns scenario data in the current user language"""
        try:
            data = json.loads(self.scenario_data)
            current_lang = getattr(g, 'lang', 'en') # Используем getattr, как и было
            
            if current_lang in data.get('translations', {}):
                return data['translations'][current_lang]
            return data.get('default', {}) # Возвращаем default, если есть, или пустой dict
        except (json.JSONDecodeError, TypeError): # TypeError если scenario_data is None
            return {
                "patient_info": {"name": "Error Patient","age": 0,"gender": "unknown","image": "patient_maria.jpg","medical_history": "Error loading patient data"},
                "initial_state": {"node_id": "error","patient_statement": "There was an error loading the scenario data.","patient_emotion": "concerned","notes": "Please contact technical support."},
                "dialogue_nodes": [],
                "outcomes": {}
            }

class VirtualPatientAttempt(db.Model):
    __tablename__ = 'virtual_patient_attempt'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id", ondelete='CASCADE'), nullable=False)
    scenario_id = db.Column(db.Integer, db.ForeignKey("virtual_patient_scenario.id", ondelete='CASCADE'), nullable=False)
    score = db.Column(db.Integer, default=0)
    max_score = db.Column(db.Integer, default=100)
    completed = db.Column(db.Boolean, default=False)
    time_spent = db.Column(db.Float, default=0.0)
    started_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    completed_at = db.Column(db.DateTime, nullable=True)
    dialogue_history = db.Column(db.Text, nullable=True)
    user = db.relationship("User", backref=db.backref("virtual_patient_attempts", lazy='dynamic'))
    
    @property
    def percentage_score(self):
        if self.max_score == 0:
            return 0
        return int((self.score / self.max_score) * 100)
    
class AchievementType(Enum):
    """Типы достижений"""
    COMPLETION = "completion"           # За завершение сценариев
    PERFORMANCE = "performance"         # За высокие результаты
    CONSISTENCY = "consistency"         # За регулярное обучение
    IMPROVEMENT = "improvement"         # За прогресс
    SOCIAL = "social"                  # За социальные активности
    SPECIAL = "special"                # Специальные достижения

class BadgeRarity(Enum):
    """Редкость значков"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

class UserAchievement(db.Model):
    """Достижения пользователей"""
    __tablename__ = 'user_achievements'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    achievement_id = Column(Integer, ForeignKey('achievement.id'), nullable=False)
    earned_at = Column(DateTime, default=datetime.utcnow)
    progress_value = Column(Float, default=0.0)  # Для постепенных достижений
    
    # Отношения
    user = relationship("User", backref="achievements")
    achievement = relationship("Achievement", backref="user_achievements")

class Achievement(db.Model):
    """Достижения системы"""
    __tablename__ = 'achievement'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String(50), nullable=False)
    type = Column(String(20), nullable=False)  # AchievementType
    rarity = Column(String(20), default=BadgeRarity.COMMON.value)
    points = Column(Integer, default=10)
    requirement = Column(Text)  # JSON с требованиями
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserStats(db.Model):
    """Статистика пользователей"""
    __tablename__ = 'user_stats'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False, unique=True)
    
    # Основные статистики
    total_scenarios_completed = Column(Integer, default=0)
    total_score_earned = Column(Integer, default=0)
    average_score_percentage = Column(Float, default=0.0)
    total_time_spent_minutes = Column(Integer, default=0)
    current_streak_days = Column(Integer, default=0)
    longest_streak_days = Column(Integer, default=0)
    last_activity_date = Column(DateTime)
    
    # Специализированные статистики
    perfect_scores_count = Column(Integer, default=0)
    empathy_score_average = Column(Float, default=0.0)
    clinical_score_average = Column(Float, default=0.0)
    communication_score_average = Column(Float, default=0.0)
    
    # Геймификация
    total_experience_points = Column(Integer, default=0)
    current_level = Column(Integer, default=1)
    points_to_next_level = Column(Integer, default=100)
    
    # Отношения
    user = relationship("User", backref="stats")

class LeaderboardEntry(db.Model):
    """Записи таблицы лидеров"""
    __tablename__ = 'leaderboard_entry'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    category = Column(String(50), nullable=False)  # weekly, monthly, all_time
    metric_type = Column(String(50), nullable=False)  # score, streak, scenarios
    value = Column(Float, nullable=False)
    rank = Column(Integer, nullable=False)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Отношения
    user = relationship("User")

# utils/gamification_engine.py
"""
Движок геймификации
"""

import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from models import UserAchievement, Achievement, UserStats, LeaderboardEntry, User

class GamificationEngine:
    """Основной класс системы геймификации"""
    
    def __init__(self, db_session):
        self.db = db_session
        self.level_thresholds = [0, 100, 250, 500, 1000, 1750, 2750, 4250, 6500, 10000, 15000]
        
    def award_experience_points(self, user_id: int, points: int, source: str = None) -> Dict:
        """
        Начисляет очки опыта пользователю
        
        Args:
            user_id: ID пользователя
            points: Количество очков
            source: Источник начисления
            
        Returns:
            Dict: Информация о начислении (новый уровень, достижения и т.д.)
        """
        stats = self.get_or_create_user_stats(user_id)
        old_level = stats.current_level
        
        # Начисляем очки
        stats.total_experience_points += points
        
        # Проверяем повышение уровня
        new_level = self.calculate_level(stats.total_experience_points)
        level_up = new_level > old_level
        
        if level_up:
            stats.current_level = new_level
            stats.points_to_next_level = self.get_points_to_next_level(stats.total_experience_points)
            
            # Проверяем достижения за уровни
            self.check_level_achievements(user_id, new_level)
        else:
            stats.points_to_next_level = self.get_points_to_next_level(stats.total_experience_points)
        
        self.db.commit()
        
        return {
            'points_awarded': points,
            'total_points': stats.total_experience_points,
            'level_up': level_up,
            'old_level': old_level,
            'new_level': stats.current_level,
            'points_to_next_level': stats.points_to_next_level
        }
    
    def process_scenario_completion(self, user_id: int, attempt_data: Dict) -> Dict:
        """
        Обрабатывает завершение сценария и начисляет награды
        
        Args:
            user_id: ID пользователя
            attempt_data: Данные о попытке
            
        Returns:
            Dict: Информация о наградах
        """
        rewards = {
            'experience_points': 0,
            'new_achievements': [],
            'level_up': False,
            'streak_updated': False
        }
        
        stats = self.get_or_create_user_stats(user_id)
        score = attempt_data.get('score', 0)
        max_score = attempt_data.get('max_score', 100)
        score_percentage = (score / max_score) * 100 if max_score > 0 else 0
        
        # Обновляем статистику
        stats.total_scenarios_completed += 1
        stats.total_score_earned += score
        stats.average_score_percentage = ((stats.average_score_percentage * (stats.total_scenarios_completed - 1) + score_percentage) / 
                                         stats.total_scenarios_completed)
        
        if attempt_data.get('time_spent'):
            stats.total_time_spent_minutes += int(attempt_data['time_spent'] / 60)
        
        # Обновляем серию (streak)
        self.update_user_streak(user_id)
        
        # Начисляем базовые очки опыта
        base_points = self.calculate_base_experience_points(score_percentage)
        
        # Бонусы
        bonus_points = 0
        
        # Бонус за перфектный результат
        if score_percentage >= 95:
            stats.perfect_scores_count += 1
            bonus_points += 20
            rewards['new_achievements'].extend(self.check_perfect_score_achievements(user_id))
        
        # Бонус за быстрое завершение
        if attempt_data.get('time_spent', 0) > 0:
            avg_time_per_decision = attempt_data['time_spent'] / max(1, len(json.loads(attempt_data.get('dialogue_history', '{}')).get('decisions', [])))
            if avg_time_per_decision < 30:  # Быстрые решения
                bonus_points += 10
        
        total_points = base_points + bonus_points
        rewards['experience_points'] = total_points
        
        # Начисляем очки опыта
        xp_result = self.award_experience_points(user_id, total_points, 'scenario_completion')
        rewards.update(xp_result)
        
        # Проверяем достижения
        rewards['new_achievements'].extend(self.check_completion_achievements(user_id))
        rewards['new_achievements'].extend(self.check_performance_achievements(user_id, score_percentage))
        rewards['new_achievements'].extend(self.check_consistency_achievements(user_id))
        
        # Обновляем таблицы лидеров
        self.update_leaderboards(user_id)
        
        self.db.commit()
        
        return rewards
    
    def calculate_base_experience_points(self, score_percentage: float) -> int:
        """Рассчитывает базовые очки опыта за сценарий"""
        if score_percentage >= 90:
            return 50
        elif score_percentage >= 80:
            return 40
        elif score_percentage >= 70:
            return 30
        elif score_percentage >= 60:
            return 25
        elif score_percentage >= 50:
            return 20
        else:
            return 15
    
    def calculate_level(self, total_points: int) -> int:
        """Рассчитывает уровень на основе общих очков"""
        for level, threshold in enumerate(self.level_thresholds):
            if total_points < threshold:
                return max(1, level)
        return len(self.level_thresholds)
    
    def get_points_to_next_level(self, current_points: int) -> int:
        """Получает количество очков до следующего уровня"""
        current_level = self.calculate_level(current_points)
        if current_level >= len(self.level_thresholds):
            return 0
        
        next_threshold = self.level_thresholds[current_level]
        return max(0, next_threshold - current_points)
    
    def update_user_streak(self, user_id: int) -> bool:
        """Обновляет серию активности пользователя"""
        stats = self.get_or_create_user_stats(user_id)
        today = datetime.utcnow().date()
        
        if stats.last_activity_date:
            last_activity = stats.last_activity_date.date()
            days_diff = (today - last_activity).days
            
            if days_diff == 1:
                # Продолжаем серию
                stats.current_streak_days += 1
                stats.longest_streak_days = max(stats.longest_streak_days, stats.current_streak_days)
            elif days_diff > 1:
                # Серия прервана
                stats.current_streak_days = 1
        else:
            # Первая активность
            stats.current_streak_days = 1
        
        stats.last_activity_date = datetime.utcnow()
        return True
    
    def check_completion_achievements(self, user_id: int) -> List[Achievement]:
        """Проверяет достижения за завершение сценариев"""
        stats = self.get_or_create_user_stats(user_id)
        new_achievements = []
        
        completion_milestones = {
            1: "first_scenario",
            5: "novice_learner", 
            10: "dedicated_student",
            25: "experienced_practitioner",
            50: "scenario_master",
            100: "virtual_patient_expert"
        }
        
        if stats.total_scenarios_completed in completion_milestones:
            achievement_key = completion_milestones[stats.total_scenarios_completed]
            achievement = self.get_achievement_by_key(achievement_key)
            if achievement and not self.user_has_achievement(user_id, achievement.id):
                self.award_achievement(user_id, achievement.id)
                new_achievements.append(achievement)
        
        return new_achievements
    
    def check_performance_achievements(self, user_id: int, score_percentage: float) -> List[Achievement]:
        """Проверяет достижения за производительность"""
        new_achievements = []
        
        # Достижения за высокие результаты
        if score_percentage >= 95:
            achievement = self.get_achievement_by_key("perfectionist")
            if achievement and not self.user_has_achievement(user_id, achievement.id):
                self.award_achievement(user_id, achievement.id)
                new_achievements.append(achievement)
        
        return new_achievements
    
    def check_consistency_achievements(self, user_id: int) -> List[Achievement]:
        """Проверяет достижения за постоянство"""
        stats = self.get_or_create_user_stats(user_id)
        new_achievements = []
        
        streak_milestones = {
            3: "committed_learner",
            7: "week_warrior", 
            14: "two_week_champion",
            30: "monthly_master",
            100: "dedication_legend"
        }
        
        if stats.current_streak_days in streak_milestones:
            achievement_key = streak_milestones[stats.current_streak_days]
            achievement = self.get_achievement_by_key(achievement_key)
            if achievement and not self.user_has_achievement(user_id, achievement.id):
                self.award_achievement(user_id, achievement.id)
                new_achievements.append(achievement)
        
        return new_achievements
    
    def check_perfect_score_achievements(self, user_id: int) -> List[Achievement]:
        """Проверяет достижения за идеальные результаты"""
        stats = self.get_or_create_user_stats(user_id)
        new_achievements = []
        
        perfect_milestones = {
            1: "first_perfect",
            5: "excellence_seeker",
            10: "perfectionist_master"
        }
        
        if stats.perfect_scores_count in perfect_milestones:
            achievement_key = perfect_milestones[stats.perfect_scores_count]
            achievement = self.get_achievement_by_key(achievement_key)
            if achievement and not self.user_has_achievement(user_id, achievement.id):
                self.award_achievement(user_id, achievement.id)
                new_achievements.append(achievement)
        
        return new_achievements
    
    def check_level_achievements(self, user_id: int, level: int) -> List[Achievement]:
        """Проверяет достижения за уровни"""
        new_achievements = []
        
        level_milestones = {
            5: "rising_star",
            10: "experienced_learner",
            15: "advanced_practitioner",
            20: "expert_level"
        }
        
        if level in level_milestones:
            achievement_key = level_milestones[level]
            achievement = self.get_achievement_by_key(achievement_key)
            if achievement and not self.user_has_achievement(user_id, achievement.id):
                self.award_achievement(user_id, achievement.id)
                new_achievements.append(achievement)
        
        return new_achievements
    
    def update_leaderboards(self, user_id: int):
        """Обновляет таблицы лидеров"""
        stats = self.get_or_create_user_stats(user_id)
        today = datetime.utcnow()
        
        # Еженедельная таблица лидеров
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        self.update_leaderboard_entry(
            user_id, 'weekly', 'total_score', 
            stats.total_score_earned, week_start, week_end
        )
        
        # Месячная таблица лидеров
        month_start = today.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        self.update_leaderboard_entry(
            user_id, 'monthly', 'scenarios_completed',
            stats.total_scenarios_completed, month_start, month_end
        )
    
    def get_user_leaderboard_position(self, user_id: int, category: str, metric_type: str) -> Optional[int]:
        """Получает позицию пользователя в таблице лидеров"""
        entry = self.db.query(LeaderboardEntry).filter_by(
            user_id=user_id,
            category=category,
            metric_type=metric_type
        ).first()
        
        return entry.rank if entry else None
    
    def get_leaderboard(self, category: str, metric_type: str, limit: int = 10) -> List[Dict]:
        """Получает топ пользователей в таблице лидеров"""
        entries = self.db.query(LeaderboardEntry).join(User).filter(
            LeaderboardEntry.category == category,
            LeaderboardEntry.metric_type == metric_type
        ).order_by(LeaderboardEntry.rank).limit(limit).all()
        
        leaderboard = []
        for entry in entries:
            leaderboard.append({
                'rank': entry.rank,
                'user_name': entry.user.first_name + ' ' + entry.user.last_name,
                'value': entry.value,
                'user_id': entry.user_id
            })
        
        return leaderboard
    
    def get_user_achievements_summary(self, user_id: int) -> Dict:
        """Получает сводку достижений пользователя"""
        user_achievements = self.db.query(UserAchievement).join(Achievement).filter(
            UserAchievement.user_id == user_id
        ).all()
        
        total_achievements = self.db.query(Achievement).filter_by(is_active=True).count()
        
        achievements_by_rarity = {}
        total_points = 0
        
        for user_achievement in user_achievements:
            achievement = user_achievement.achievement
            rarity = achievement.rarity
            
            if rarity not in achievements_by_rarity:
                achievements_by_rarity[rarity] = 0
            achievements_by_rarity[rarity] += 1
            total_points += achievement.points
        
        return {
            'total_earned': len(user_achievements),
            'total_available': total_achievements,
            'completion_percentage': (len(user_achievements) / total_achievements) * 100 if total_achievements > 0 else 0,
            'by_rarity': achievements_by_rarity,
            'total_achievement_points': total_points,
            'recent_achievements': [ua.achievement for ua in user_achievements[-5:]]
        }
    
    # Вспомогательные методы
    def get_or_create_user_stats(self, user_id: int) -> UserStats:
        """Получает или создает статистику пользователя"""
        stats = self.db.query(UserStats).filter_by(user_id=user_id).first()
        if not stats:
            stats = UserStats(user_id=user_id)
            self.db.add(stats)
            self.db.commit()
        return stats
    
    def get_achievement_by_key(self, key: str) -> Optional[Achievement]:
        """Получает достижение по ключу"""
        return self.db.query(Achievement).filter_by(name=key, is_active=True).first()
    
    def user_has_achievement(self, user_id: int, achievement_id: int) -> bool:
        """Проверяет, есть ли у пользователя достижение"""
        return self.db.query(UserAchievement).filter_by(
            user_id=user_id, 
            achievement_id=achievement_id
        ).first() is not None
    
    def award_achievement(self, user_id: int, achievement_id: int):
        """Награждает пользователя достижением"""
        if not self.user_has_achievement(user_id, achievement_id):
            user_achievement = UserAchievement(
                user_id=user_id,
                achievement_id=achievement_id
            )
            self.db.add(user_achievement)
            
            # Начисляем очки за достижение
            achievement = self.db.query(Achievement).get(achievement_id)
            if achievement:
                self.award_experience_points(user_id, achievement.points, f'achievement_{achievement.name}')
    
    def update_leaderboard_entry(self, user_id: int, category: str, metric_type: str, 
                                value: float, period_start: datetime, period_end: datetime):
        """Обновляет запись в таблице лидеров"""
        entry = self.db.query(LeaderboardEntry).filter_by(
            user_id=user_id,
            category=category,
            metric_type=metric_type,
            period_start=period_start
        ).first()
        
        if not entry:
            entry = LeaderboardEntry(
                user_id=user_id,
                category=category,
                metric_type=metric_type,
                period_start=period_start,
                period_end=period_end
            )
            self.db.add(entry)
        
        entry.value = value
        entry.last_updated = datetime.utcnow()
        
        # Пересчитываем ранги для этой категории
        self.recalculate_ranks(category, metric_type, period_start)
    
    def recalculate_ranks(self, category: str, metric_type: str, period_start: datetime):
        """Пересчитывает ранги в таблице лидеров"""
        entries = self.db.query(LeaderboardEntry).filter_by(
            category=category,
            metric_type=metric_type,
            period_start=period_start
        ).order_by(LeaderboardEntry.value.desc()).all()
        
        for rank, entry in enumerate(entries, 1):
            entry.rank = rank    

# ===== RAG SYSTEM MODELS =====

class UserAPIKey(db.Model):
    """Пользовательские API ключи для AI провайдеров с шифрованием"""
    __tablename__ = 'user_api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    provider = db.Column(db.String(50), nullable=False, index=True)  # groq, deepseek, openai
    encrypted_api_key = db.Column(db.Text, nullable=False)  # Зашифрованный API ключ
    key_name = db.Column(db.String(100), nullable=True)  # Пользовательское имя ключа
    is_active = db.Column(db.Boolean, default=True, index=True)
    
    # Статистика использования
    tokens_used_today = db.Column(db.Integer, default=0)
    total_tokens_used = db.Column(db.Integer, default=0)
    last_used_at = db.Column(db.DateTime, nullable=True)
    daily_limit_reset = db.Column(db.Date, default=datetime.utcnow().date())
    
    # Метаданные
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Отношения
    user = db.relationship('User', backref=db.backref('api_keys', lazy='dynamic', cascade='all, delete-orphan'))
    
    # Уникальный индекс: один ключ на провайдера на пользователя
    __table_args__ = (
        db.UniqueConstraint('user_id', 'provider', name='uc_user_provider_key'),
        db.Index('idx_user_api_keys_active', 'user_id', 'is_active'),
        db.Index('idx_user_api_keys_provider', 'provider', 'is_active'),
    )
    
    def reset_daily_usage_if_needed(self):
        """Сбрасывает дневное использование если прошел день"""
        today = datetime.utcnow().date()
        if self.daily_limit_reset < today:
            self.tokens_used_today = 0
            self.daily_limit_reset = today
            db.session.commit()
    
    def add_token_usage(self, tokens_used: int):
        """Добавляет использованные токены к статистике"""
        self.reset_daily_usage_if_needed()
        self.tokens_used_today += tokens_used
        self.total_tokens_used += tokens_used
        self.last_used_at = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<UserAPIKey {self.user_id}:{self.provider}>'


class AIConversation(db.Model):
    """История разговоров с AI ассистентом"""
    __tablename__ = 'ai_conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    
    # Контент разговора
    user_message = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    
    # Метаданные AI запроса
    provider = db.Column(db.String(50), nullable=False, index=True)  # groq, deepseek, openai
    model_used = db.Column(db.String(100), nullable=True)
    tokens_used = db.Column(db.Integer, default=0)
    response_time_ms = db.Column(db.Integer, nullable=True)
    
    # RAG контекст
    rag_sources = db.Column(db.JSON, nullable=True)  # Источники для RAG
    context_used = db.Column(db.Text, nullable=True)  # Использованный контекст
    
    # Пользовательские оценки
    user_rating = db.Column(db.Integer, nullable=True)  # 1-5 звезд
    user_feedback = db.Column(db.Text, nullable=True)
    
    # Метаданные
    language = db.Column(db.String(5), default='en', index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    # Отношения
    user = db.relationship('User', backref=db.backref('ai_conversations', lazy='dynamic', cascade='all, delete-orphan'))
    
    # Индексы для поиска
    __table_args__ = (
        db.Index('idx_ai_conversations_user_date', 'user_id', 'created_at'),
        db.Index('idx_ai_conversations_provider', 'provider', 'created_at'),
        db.Index('idx_ai_conversations_language', 'language', 'created_at'),
    )
    
    def __repr__(self):
        return f'<AIConversation {self.id}: {self.user_id}>'


class ContentEmbedding(db.Model):
    """Векторные представления образовательного контента для RAG"""
    __tablename__ = 'content_embeddings'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Ссылки на контент
    content_type = db.Column(db.String(50), nullable=False, index=True)  # lesson, question, module, virtual_patient
    content_id = db.Column(db.Integer, nullable=False, index=True)  # ID соответствующего объекта
    
    # Текстовые данные
    text_chunk = db.Column(db.Text, nullable=False)  # Чанк текста
    chunk_index = db.Column(db.Integer, default=0)  # Порядковый номер чанка
    title = db.Column(db.String(500), nullable=True)  # Заголовок для отображения
    
    # Векторное представление
    embedding_vector = db.Column(db.JSON, nullable=False)  # Векторное представление
    vector_model = db.Column(db.String(100), default='all-MiniLM-L6-v2')  # Модель для создания векторов
    
    # Метаданные для фильтрации
    language = db.Column(db.String(5), default='en', index=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True, index=True)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=True, index=True)
    difficulty_level = db.Column(db.String(20), nullable=True, index=True)  # beginner, intermediate, advanced
    
    # Версионирование и качество
    content_hash = db.Column(db.String(64), nullable=False, index=True)  # MD5 хэш исходного контента
    embedding_quality_score = db.Column(db.Float, nullable=True)  # Оценка качества эмбеддинга
    
    # Метаданные
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Отношения
    subject = db.relationship('Subject', backref=db.backref('content_embeddings', lazy='dynamic'))
    module = db.relationship('Module', backref=db.backref('content_embeddings', lazy='dynamic'))
    
    # Композитные индексы для эффективного поиска
    __table_args__ = (
        db.UniqueConstraint('content_type', 'content_id', 'chunk_index', 'language', name='uc_content_chunk_lang'),
        db.Index('idx_embeddings_content', 'content_type', 'content_id'),
        db.Index('idx_embeddings_search', 'language', 'subject_id', 'difficulty_level'),
        db.Index('idx_embeddings_hash', 'content_hash'),
    )
    
    def __repr__(self):
        return f'<ContentEmbedding {self.content_type}:{self.content_id}:{self.chunk_index}>'


class RAGCache(db.Model):
    """Кэш для RAG запросов и результатов"""
    __tablename__ = 'rag_cache'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Ключ запроса
    query_hash = db.Column(db.String(64), unique=True, nullable=False, index=True)  # MD5 хэш запроса
    query_text = db.Column(db.Text, nullable=False)  # Исходный текст запроса
    
    # Параметры поиска
    language = db.Column(db.String(5), default='en', index=True)
    content_filters = db.Column(db.JSON, nullable=True)  # Фильтры (subject_id, difficulty, etc.)
    
    # Результаты поиска
    search_results = db.Column(db.JSON, nullable=False)  # Найденные релевантные чанки
    context_text = db.Column(db.Text, nullable=True)  # Сгенерированный контекст
    relevance_scores = db.Column(db.JSON, nullable=True)  # Оценки релевантности
    
    # Статистика использования
    hit_count = db.Column(db.Integer, default=1)
    last_used_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    # Метаданные
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime, nullable=True, index=True)  # TTL кэша
    
    # Индексы
    __table_args__ = (
        db.Index('idx_rag_cache_language', 'language', 'last_used_at'),
        db.Index('idx_rag_cache_expires', 'expires_at'),
    )
    
    def is_expired(self) -> bool:
        """Проверяет, истек ли кэш"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def touch(self):
        """Обновляет время последнего использования и счетчик попаданий"""
        self.hit_count += 1
        self.last_used_at = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<RAGCache {self.query_hash[:8]}... ({self.hit_count} hits)>'    

# ============================================================================
# ASSESSMENT SYSTEM MODELS
# ============================================================================

class AssessmentCategory(db.Model):
    """Категории для оценки знаний"""
    __tablename__ = 'assessment_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    weight = db.Column(db.Float, default=1.0)  # Вес категории в общей оценке
    min_questions = db.Column(db.Integer, default=5)  # Минимум вопросов
    max_questions = db.Column(db.Integer, default=15)  # Максимум вопросов
    color = db.Column(db.String(7), default='#3ECDC1')  # Цвет для UI
    icon = db.Column(db.String(50), default='book')
    
    # Голландские специфичные поля
    is_dutch_specific = db.Column(db.Boolean, default=False)  # Специфично для Нидерландов
    dutch_weight = db.Column(db.Float, default=1.0)  # Вес для голландской оценки
    critical_for_netherlands = db.Column(db.Boolean, default=False)  # Критично для работы в Нидерландах
    name_en = db.Column(db.String(100))  # Английский перевод названия
    name_ru = db.Column(db.String(100))  # Русский перевод названия
    
    # Связи
    questions = db.relationship('AssessmentQuestion', backref='category', lazy='dynamic')
    
    def __repr__(self):
        return f'<AssessmentCategory {self.name}>'

class AssessmentQuestion(db.Model):
    """Вопросы для предварительной оценки"""
    __tablename__ = 'assessment_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('assessment_categories.id'), nullable=False)
    
    # Контент вопроса
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), default='multiple_choice')  # multiple_choice, true_false, scale
    
    # Варианты ответов (JSON)
    options = db.Column(db.Text)  # JSON список опций
    correct_answer = db.Column(db.Integer)  # Индекс правильного ответа
    explanation = db.Column(db.Text)  # Объяснение ответа
    
    # Метаданные
    difficulty_level = db.Column(db.Integer, default=1)  # 1-5 (новичок-эксперт)
    time_limit = db.Column(db.Integer, default=60)  # секунды
    points = db.Column(db.Integer, default=1)
    
    # Связанные модули обучения
    related_modules = db.Column(db.Text)  # JSON список ID модулей
    
    # Статистика
    times_asked = db.Column(db.Integer, default=0)
    times_correct = db.Column(db.Integer, default=0)
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_options(self):
        """Получить варианты ответов как список"""
        return json.loads(self.options) if self.options else []
    
    def set_options(self, options_list):
        """Установить варианты ответов"""
        self.options = json.dumps(options_list, ensure_ascii=False)
    
    def get_related_modules(self):
        """Получить связанные модули"""
        return json.loads(self.related_modules) if self.related_modules else []
    
    def __repr__(self):
        return f'<AssessmentQuestion {self.id}: {self.question_text[:50]}>'

class PreAssessmentAttempt(db.Model):
    """Попытки прохождения предварительной оценки"""
    __tablename__ = 'pre_assessment_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Результаты
    total_questions = db.Column(db.Integer, nullable=False)
    correct_answers = db.Column(db.Integer, default=0)
    total_score = db.Column(db.Float, default=0.0)  # Общий балл (0-100)
    
    # Результаты по категориям (JSON)
    category_scores = db.Column(db.Text)  # {category_id: {score, correct, total}}
    
    # Временные метрики
    started_at = db.Column(db.DateTime, nullable=False)
    completed_at = db.Column(db.DateTime)
    time_spent = db.Column(db.Integer)  # секунды
    
    # Рекомендованный план
    recommended_plan = db.Column(db.Text)  # JSON с планом обучения
    
    is_completed = db.Column(db.Boolean, default=False)
    
    # Связи
    answers = db.relationship('PreAssessmentAnswer', backref='attempt', lazy='dynamic')
    user = db.relationship('User', backref='assessment_attempts')
    
    def get_category_scores(self):
        """Получить результаты по категориям"""
        return json.loads(self.category_scores) if self.category_scores else {}
    
    def set_category_scores(self, scores_dict):
        """Установить результаты по категориям"""
        self.category_scores = json.dumps(scores_dict)
    
    def get_recommended_plan(self):
        """Получить рекомендованный план"""
        return json.loads(self.recommended_plan) if self.recommended_plan else {}
    
    def set_recommended_plan(self, plan_dict):
        """Установить рекомендованный план"""
        self.recommended_plan = json.dumps(plan_dict, ensure_ascii=False)
    
    def __repr__(self):
        return f'<PreAssessmentAttempt {self.id}: User {self.user_id}>'

class PreAssessmentAnswer(db.Model):
    """Ответы пользователя на вопросы оценки"""
    __tablename__ = 'pre_assessment_answers'
    
    id = db.Column(db.Integer, primary_key=True)
    attempt_id = db.Column(db.Integer, db.ForeignKey('pre_assessment_attempts.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('assessment_questions.id'), nullable=False)
    
    # Ответ пользователя
    user_answer = db.Column(db.Integer)  # Индекс выбранного ответа
    is_correct = db.Column(db.Boolean, default=False)
    points_earned = db.Column(db.Float, default=0.0)
    
    # Время ответа
    time_spent = db.Column(db.Integer)  # секунды на вопрос
    answered_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связи
    question = db.relationship('AssessmentQuestion', backref='user_answers')
    
    def __repr__(self):
        return f'<PreAssessmentAnswer {self.id}: Q{self.question_id}>'

class LearningPlan(db.Model):
    """Персонализированные планы обучения"""
    __tablename__ = 'learning_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assessment_attempt_id = db.Column(db.Integer, db.ForeignKey('pre_assessment_attempts.id'))
    
    # Метаданные плана
    plan_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    difficulty_level = db.Column(db.String(20))  # beginner, intermediate, advanced
    estimated_duration = db.Column(db.Integer)  # часы
    
    # Структура плана (JSON)
    plan_structure = db.Column(db.Text)  # Детальная структура плана
    
    # Прогресс
    total_modules = db.Column(db.Integer, default=0)
    completed_modules = db.Column(db.Integer, default=0)
    
    # Статус
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    # Связи
    user = db.relationship('User', backref='learning_plans')
    assessment_attempt = db.relationship('PreAssessmentAttempt', backref='learning_plan')
    
    def get_plan_structure(self):
        """Получить структуру плана"""
        return json.loads(self.plan_structure) if self.plan_structure else {}
    
    def set_plan_structure(self, structure_dict):
        """Установить структуру плана"""
        self.plan_structure = json.dumps(structure_dict, ensure_ascii=False)
    
    def calculate_progress(self):
        """Вычислить прогресс выполнения плана"""
        if self.total_modules == 0:
            return 0
        return round((self.completed_modules / self.total_modules) * 100, 1)
    
    def __repr__(self):
        return f'<LearningPlan {self.id}: {self.plan_name}>'    

# ============================================================================
# DUTCH ASSESSMENT SYSTEM MODELS
# ============================================================================

class DutchCompetencyLevel(db.Model):
    """Уровни компетенции для голландской системы оценки"""
    __tablename__ = 'dutch_competency_levels'
    
    id = db.Column(db.Integer, primary_key=True)
    level_name = db.Column(db.String(20), nullable=False)  # insufficient, basic, competent, proficient
    threshold = db.Column(db.Float, nullable=False)  # Пороговое значение для уровня
    description = db.Column(db.Text)  # Описание уровня
    recommendation = db.Column(db.Text)  # Рекомендации для достижения уровня
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<DutchCompetencyLevel {self.level_name}>'

class DutchAssessmentResult(db.Model):
    """Результаты голландской оценки знаний"""
    __tablename__ = 'dutch_assessment_results'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    attempt_id = db.Column(db.Integer, db.ForeignKey('pre_assessment_attempts.id'), nullable=False)
    
    # Результаты оценки
    competency_level = db.Column(db.String(20), nullable=False)  # insufficient, basic, competent, proficient
    overall_score = db.Column(db.Float, nullable=False)  # Общий балл
    critical_areas_score = db.Column(db.Float, nullable=False)  # Балл по критическим областям
    
    # Возможности работы
    can_work_supervised = db.Column(db.Boolean, default=False)  # Может работать под надзором
    can_work_independently = db.Column(db.Boolean, default=False)  # Может работать самостоятельно
    
    # Региональная специфика
    regional_focus = db.Column(db.String(20))  # urban, rural - фокус на городскую или сельскую практику
    
    # Сертификация и следующие шаги
    certification_pathway = db.Column(db.Text)  # JSON с путем сертификации
    next_steps = db.Column(db.Text)  # JSON с следующими шагами
    
    # Детальные результаты по категориям
    category_scores = db.Column(db.Text)  # JSON с результатами по категориям
    
    # Метаданные
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Связи
    user = db.relationship('User', backref='dutch_assessments')
    attempt = db.relationship('PreAssessmentAttempt', backref='dutch_result')
    
    def get_certification_pathway(self):
        """Получить путь сертификации"""
        return json.loads(self.certification_pathway) if self.certification_pathway else {}
    
    def set_certification_pathway(self, pathway_dict):
        """Установить путь сертификации"""
        self.certification_pathway = json.dumps(pathway_dict, ensure_ascii=False)
    
    def get_next_steps(self):
        """Получить следующие шаги"""
        return json.loads(self.next_steps) if self.next_steps else {}
    
    def set_next_steps(self, steps_dict):
        """Установить следующие шаги"""
        self.next_steps = json.dumps(steps_dict, ensure_ascii=False)
    
    def get_category_scores(self):
        """Получить результаты по категориям"""
        return json.loads(self.category_scores) if self.category_scores else {}
    
    def set_category_scores(self, scores_dict):
        """Установить результаты по категориям"""
        self.category_scores = json.dumps(scores_dict, ensure_ascii=False)
    
    def __repr__(self):
        return f'<DutchAssessmentResult {self.id}: User {self.user_id}, Level {self.competency_level}>'    

# ============================================================================
# CONTENT EDITOR MODELS
# ============================================================================

class ContentTemplate(db.Model):
    """Модель для хранения шаблонов контента"""
    __tablename__ = 'content_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.String(100), unique=True, nullable=False, index=True)
    name = db.Column(db.JSON, nullable=False)  # Многоязычные названия
    description = db.Column(db.JSON, nullable=True)  # Многоязычные описания
    category = db.Column(db.String(50), nullable=False, index=True)
    icon = db.Column(db.String(50), nullable=True)
    version = db.Column(db.String(20), default='1.0')
    structure = db.Column(db.JSON, nullable=False)  # JSON структура шаблона
    template_metadata = db.Column(db.JSON, nullable=True)  # Дополнительные метаданные
    tags = db.Column(db.JSON, nullable=True)  # Теги для поиска
    author = db.Column(db.String(100), default='Dental Academy')
    is_active = db.Column(db.Boolean, default=True)
    is_public = db.Column(db.Boolean, default=True)
    is_system = db.Column(db.Boolean, default=False, index=True)  # Системный шаблон
    language = db.Column(db.String(5), default='en', index=True)  # Основной язык шаблона
    usage_count = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=0.0)
    rating_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Связи
    creator = db.relationship('User', backref='created_templates', foreign_keys=[created_by])
    
    def __repr__(self):
        return f'<ContentTemplate {self.template_id}>'
    
    def get_name(self, lang='ru'):
        """Получить название на указанном языке"""
        if isinstance(self.name, dict):
            return self.name.get(lang, self.name.get('ru', self.template_id))
        return self.name
    
    def get_description(self, lang='ru'):
        """Получить описание на указанном языке"""
        if isinstance(self.description, dict):
            return self.description.get(lang, self.description.get('ru', ''))
        return self.description or ''
    
    def increment_usage(self):
        """Увеличить счетчик использования"""
        self.usage_count += 1
        db.session.commit()
    
    def update_rating(self, new_rating):
        """Обновить рейтинг шаблона"""
        total_rating = self.rating * self.rating_count + new_rating
        self.rating_count += 1
        self.rating = total_rating / self.rating_count
        db.session.commit()
    
    def to_dict(self, lang='ru'):
        """Преобразовать в словарь для API"""
        return {
            'id': self.id,
            'template_id': self.template_id,
            'name': self.get_name(lang),
            'description': self.get_description(lang),
            'category': self.category,
            'icon': self.icon,
            'version': self.version,
            'structure': self.structure,
            'metadata': self.template_metadata,
            'tags': self.tags,
            'author': self.author,
            'is_active': self.is_active,
            'is_public': self.is_public,
            'usage_count': self.usage_count,
            'rating': self.rating,
            'rating_count': self.rating_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }
    
    @classmethod
    def get_by_category(cls, category, lang='ru', limit=None):
        """Получить шаблоны по категории"""
        query = cls.query.filter_by(category=category, is_active=True, is_public=True)
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @classmethod
    def search(cls, query, lang='ru', limit=None):
        """Поиск шаблонов по названию, описанию или тегам"""
        search_term = f'%{query}%'
        results = cls.query.filter(
            db.or_(
                cls.name.contains({lang: search_term}),
                cls.description.contains({lang: search_term}),
                cls.tags.contains([query])
            ),
            cls.is_active == True,
            cls.is_public == True
        )
        if limit:
            results = results.limit(limit)
        return results.all()

class ContentPage(db.Model):
    """Основная модель для страниц редактора контента"""
    __tablename__ = 'content_pages'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    slug = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    
    # Тип контента и связь с существующими моделями
    content_type = db.Column(db.String(50), nullable=False, index=True)  # lesson, module, subject, custom
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=True, index=True)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=True, index=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True, index=True)
    
    # Контент страницы
    content_data = db.Column(db.Text, nullable=False)  # JSON с контентом страницы
    page_metadata = db.Column(db.Text, nullable=True)  # JSON с метаданными
    
    # Шаблон
    template_id = db.Column(db.Integer, db.ForeignKey('content_templates.id'), nullable=True, index=True)
    
    # Статус и публикация
    status = db.Column(db.String(20), default='draft', index=True)  # draft, published, archived
    is_published = db.Column(db.Boolean, default=False, index=True)
    published_at = db.Column(db.DateTime, nullable=True, index=True)
    
    # Мультиязычность
    language = db.Column(db.String(5), default='en', index=True)
    original_page_id = db.Column(db.Integer, db.ForeignKey('content_pages.id'), nullable=True, index=True)  # Для переводов
    
    # SEO и навигация
    seo_title = db.Column(db.String(255), nullable=True)
    seo_description = db.Column(db.Text, nullable=True)
    seo_keywords = db.Column(db.String(500), nullable=True)
    canonical_url = db.Column(db.String(500), nullable=True)
    
    # Создатель и время
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Отношения
    creator = db.relationship('User', foreign_keys=[created_by], backref=db.backref('created_content_pages', lazy='dynamic'))
    updater = db.relationship('User', foreign_keys=[updated_by], backref=db.backref('updated_content_pages', lazy='dynamic'))
    lesson = db.relationship('Lesson', backref=db.backref('content_pages', lazy='dynamic'))
    module = db.relationship('Module', backref=db.backref('content_pages', lazy='dynamic'))
    subject = db.relationship('Subject', backref=db.backref('content_pages', lazy='dynamic'))
    original_page = db.relationship('ContentPage', remote_side=[id], backref=db.backref('translations', lazy='dynamic'))
    versions = db.relationship('ContentPageVersion', backref='content_page', lazy='dynamic', cascade='all, delete-orphan')
    
    # Индексы для производительности
    __table_args__ = (
        db.Index('idx_content_type_status', 'content_type', 'status'),
        db.Index('idx_language_published', 'language', 'is_published'),
        db.Index('idx_created_by_status', 'created_by', 'status'),
        db.Index('idx_slug_language', 'slug', 'language'),
        db.UniqueConstraint('slug', 'language', name='uc_content_page_slug_language'),
    )
    
    def get_content_data(self):
        """Получить данные контента"""
        return json.loads(self.content_data) if self.content_data else {}
    
    def set_content_data(self, content_dict):
        """Установить данные контента"""
        self.content_data = json.dumps(content_dict, ensure_ascii=False)
    
    def get_page_metadata(self):
        """Получить метаданные страницы"""
        return json.loads(self.page_metadata) if self.page_metadata else {}
    
    def set_page_metadata(self, metadata_dict):
        """Установить метаданные страницы"""
        self.page_metadata = json.dumps(metadata_dict, ensure_ascii=False)
    
    def publish(self):
        """Опубликовать страницу"""
        self.status = 'published'
        self.is_published = True
        self.published_at = datetime.now(timezone.utc)
    
    def archive(self):
        """Архивировать страницу"""
        self.status = 'archived'
        self.is_published = False
    
    def create_version(self, user_id, version_notes=None):
        """Создать новую версию страницы"""
        version = ContentPageVersion(
            content_page_id=self.id,
            version_number=self.versions.count() + 1,
            title=self.title,
            content_data=self.content_data,
            version_metadata=self.page_metadata,
            created_by=user_id,
            version_notes=version_notes
        )
        return version
    
    def get_latest_version(self):
        """Получить последнюю версию"""
        return self.versions.order_by(ContentPageVersion.version_number.desc()).first()
    
    def __repr__(self):
        return f'<ContentPage {self.id}: {self.title} ({self.content_type})>'

class ContentPageVersion(db.Model):
    """Версионирование страниц контента"""
    __tablename__ = 'content_page_versions'
    
    id = db.Column(db.Integer, primary_key=True)
    content_page_id = db.Column(db.Integer, db.ForeignKey('content_pages.id', ondelete='CASCADE'), nullable=False, index=True)
    
    # Версия
    version_number = db.Column(db.Integer, nullable=False, index=True)
    version_notes = db.Column(db.Text, nullable=True)  # Заметки о версии
    
    # Данные версии
    title = db.Column(db.String(255), nullable=False)
    content_data = db.Column(db.Text, nullable=False)  # JSON с контентом на момент версии
    version_metadata = db.Column(db.Text, nullable=True)  # JSON с метаданными на момент версии
    
    # Создатель и время
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    
    # Отношения
    creator = db.relationship('User', backref=db.backref('content_page_versions', lazy='dynamic'))
    
    # Индексы для производительности
    __table_args__ = (
        db.Index('idx_page_version_number', 'content_page_id', 'version_number'),
        db.Index('idx_version_created_at', 'created_at'),
        db.UniqueConstraint('content_page_id', 'version_number', name='uc_content_page_version'),
    )
    
    def get_content_data(self):
        """Получить данные контента версии"""
        return json.loads(self.content_data) if self.content_data else {}
    
    def get_version_metadata(self):
        """Получить метаданные версии"""
        return json.loads(self.version_metadata) if self.version_metadata else {}
    
    def restore_to_page(self, target_page):
        """Восстановить эту версию в целевую страницу"""
        target_page.title = self.title
        target_page.content_data = self.content_data
        target_page.version_metadata = self.version_metadata
        target_page.updated_at = datetime.now(timezone.utc)
        target_page.updated_by = target_page.created_by  # Или передать текущего пользователя
    
    def __repr__(self):
        return f'<ContentPageVersion {self.id}: Page {self.content_page_id}, v{self.version_number}>'    

# ===== GRAPESJS MODELS =====

class GrapesJSPage(db.Model):
    """Модель для страниц созданных в GrapesJS"""
    __tablename__ = 'grapejs_pages'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False, default='Новая страница')
    slug = db.Column(db.String(255), unique=True, nullable=True)
    
    # Контент GrapesJS
    html = db.Column(db.Text)
    css = db.Column(db.Text)
    components = db.Column(db.Text)  # JSON строка компонентов GrapesJS
    styles = db.Column(db.Text)      # JSON строка стилей GrapesJS
    
    # Связи
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=True)
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'), nullable=True)
    
    # Метаданные
    is_published = db.Column(db.Boolean, default=False)
    is_template = db.Column(db.Boolean, default=False)
    category = db.Column(db.String(100), default='general')
    description = db.Column(db.Text)
    
    # Временные метки
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    published_at = db.Column(db.DateTime, nullable=True)
    
    # Индексы
    __table_args__ = (
        db.Index('idx_grapejs_pages_user_id', 'user_id'),
        db.Index('idx_grapejs_pages_lesson_id', 'lesson_id'),
        db.Index('idx_grapejs_pages_published', 'is_published'),
        db.Index('idx_grapejs_pages_template', 'is_template'),
    )
    
    # Relationships
    user = db.relationship('User', backref=db.backref('grapejs_pages', lazy='dynamic'))
    lesson = db.relationship('Lesson', backref=db.backref('grapejs_pages', lazy='dynamic'))
    module = db.relationship('Module', backref=db.backref('grapejs_pages', lazy='dynamic'))
    
    def __repr__(self):
        return f'<GrapesJSPage {self.title}>'
    
    def to_dict(self):
        """Сериализация в словарь"""
        return {
            'id': self.id,
            'title': self.title,
            'slug': self.slug,
            'html': self.html,
            'css': self.css,
            'components': self.components,
            'styles': self.styles,
            'user_id': self.user_id,
            'lesson_id': self.lesson_id,
            'module_id': self.module_id,
            'is_published': self.is_published,
            'is_template': self.is_template,
            'category': self.category,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'published_at': self.published_at.isoformat() if self.published_at else None,
        }
    
    @staticmethod
    def generate_slug(title):
        """Генерация slug из заголовка"""
        import re
        try:
            import unidecode
            slug = unidecode.unidecode(title).lower()
        except ImportError:
            # Fallback без unidecode
            slug = title.lower()
        
        slug = re.sub(r'[^a-z0-9\-]', '-', slug)
        slug = re.sub(r'-+', '-', slug).strip('-')
        return slug[:100]  # Ограничиваем длину


class GrapesJSAsset(db.Model):
    """Модель для медиа ресурсов GrapesJS"""
    __tablename__ = 'grapejs_assets'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    mime_type = db.Column(db.String(100))
    width = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)
    
    # Связи
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    page_id = db.Column(db.Integer, db.ForeignKey('grapejs_pages.id'), nullable=True)
    
    # Метаданные
    alt_text = db.Column(db.String(255))
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=False)
    
    # Временные метки
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Индексы
    __table_args__ = (
        db.Index('idx_grapejs_assets_user_id', 'user_id'),
        db.Index('idx_grapejs_assets_page_id', 'page_id'),
        db.Index('idx_grapejs_assets_public', 'is_public'),
    )
    
    # Relationships
    user = db.relationship('User', backref=db.backref('grapejs_assets', lazy='dynamic'))
    page = db.relationship('GrapesJSPage', backref=db.backref('assets', lazy='dynamic'))
    
    def __repr__(self):
        return f'<GrapesJSAsset {self.original_name}>'
    
    def to_dict(self):
        """Сериализация в словарь"""
        return {
            'id': self.id,
            'filename': self.filename,
            'original_name': self.original_name,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'mime_type': self.mime_type,
            'width': self.width,
            'height': self.height,
            'alt_text': self.alt_text,
            'description': self.description,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'url': f'/static/uploads/grapejs/{self.filename}'
        }


class GrapesJSTemplate(db.Model):
    """Модель для шаблонов GrapesJS"""
    __tablename__ = 'grapejs_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    preview_image = db.Column(db.String(255))
    
    # Контент шаблона
    html = db.Column(db.Text)
    css = db.Column(db.Text)
    components = db.Column(db.Text)
    styles = db.Column(db.Text)
    
    # Метаданные
    category = db.Column(db.String(100), default='general')
    is_public = db.Column(db.Boolean, default=False)
    is_official = db.Column(db.Boolean, default=False)
    usage_count = db.Column(db.Integer, default=0)
    
    # Связи
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Временные метки
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Индексы
    __table_args__ = (
        db.Index('idx_grapejs_templates_category', 'category'),
        db.Index('idx_grapejs_templates_public', 'is_public'),
        db.Index('idx_grapejs_templates_official', 'is_official'),
    )
    
    # Relationships
    user = db.relationship('User', backref=db.backref('grapejs_templates', lazy='dynamic'))
    
    def __repr__(self):
        return f'<GrapesJSTemplate {self.name}>'
    
    def to_dict(self):
        """Сериализация в словарь"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'preview_image': self.preview_image,
            'html': self.html,
            'css': self.css,
            'components': self.components,
            'styles': self.styles,
            'category': self.category,
            'is_public': self.is_public,
            'is_official': self.is_official,
            'usage_count': self.usage_count,
            'user_id': self.user_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class EditablePageTemplate(db.Model):
    """
    Модель для редактируемых шаблонов страниц с поддержкой GrapesJS
    Model for editable page templates with GrapesJS support
    
    Позволяет администраторам редактировать существующие Jinja2 шаблоны
    через интерфейс GrapesJS, сохраняя при этом логику шаблонов.
    Allows administrators to edit existing Jinja2 templates through
    GrapesJS interface while preserving template logic.
    """
    __tablename__ = 'editable_page_templates'
    
    # Основные поля / Primary fields
    id = db.Column(db.Integer, primary_key=True)
    template_path = db.Column(db.String(500), nullable=False, index=True)  # Путь к Jinja2 шаблону / Path to Jinja2 template
    original_content = db.Column(db.Text, nullable=False)  # Оригинальное содержимое шаблона / Original template content
    grapesjs_content = db.Column(db.Text, nullable=True)  # Контент отредактированный в GrapesJS / Content edited in GrapesJS
    css_overrides = db.Column(db.Text, nullable=True)  # CSS переопределения / CSS overrides
    js_modifications = db.Column(db.Text, nullable=True)  # JavaScript модификации / JavaScript modifications
    is_live = db.Column(db.Boolean, default=False, index=True)  # Активен ли шаблон / Is template active
    language = db.Column(db.String(5), default='en', index=True)  # Язык шаблона (en/ru) / Template language
    
    # Связи / Relationships
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    
    # Временные метки / Timestamps
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    # Дополнительные метаданные / Additional metadata
    template_name = db.Column(db.String(255), nullable=True)  # Человекочитаемое имя / Human-readable name
    description = db.Column(db.Text, nullable=True)  # Описание шаблона / Template description
    category = db.Column(db.String(100), default='general', index=True)  # Категория шаблона / Template category
    version = db.Column(db.String(20), default='1.0')  # Версия шаблона / Template version
    is_system = db.Column(db.Boolean, default=False, index=True)  # Системный шаблон / System template
    
    # Индексы для производительности / Performance indexes
    __table_args__ = (
        db.Index('idx_editable_templates_path_lang', 'template_path', 'language'),
        db.Index('idx_editable_templates_live', 'is_live'),
        db.Index('idx_editable_templates_category', 'category'),
        db.Index('idx_editable_templates_created_by', 'created_by'),
    )
    
    # Отношения / Relationships
    creator = db.relationship('User', backref=db.backref('editable_templates', lazy='dynamic'))
    
    def __repr__(self):
        """Строковое представление модели / String representation of the model"""
        return f'<EditablePageTemplate {self.template_path} ({self.language})>'
    
    def to_dict(self):
        """
        Сериализация в словарь / Serialize to dictionary
        
        Returns:
            dict: Словарь с данными шаблона / Dictionary with template data
        """
        return {
            'id': self.id,
            'template_path': self.template_path,
            'template_name': self.template_name,
            'description': self.description,
            'original_content': self.original_content,
            'grapesjs_content': self.grapesjs_content,
            'css_overrides': self.css_overrides,
            'js_modifications': self.js_modifications,
            'is_live': self.is_live,
            'language': self.language,
            'category': self.category,
            'version': self.version,
            'is_system': self.is_system,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def backup(self):
        """
        Создание резервной копии шаблона / Create template backup
        
        Returns:
            dict: Резервная копия данных шаблона / Template data backup
        """
        return {
            'template_path': self.template_path,
            'original_content': self.original_content,
            'grapesjs_content': self.grapesjs_content,
            'css_overrides': self.css_overrides,
            'js_modifications': self.js_modifications,
            'language': self.language,
            'version': self.version,
            'backup_created_at': datetime.now(timezone.utc).isoformat(),
        }
    
    def restore(self, backup_data):
        """
        Восстановление шаблона из резервной копии / Restore template from backup
        
        Args:
            backup_data (dict): Данные резервной копии / Backup data
            
        Returns:
            bool: True если восстановление успешно / True if restore successful
        """
        try:
            self.original_content = backup_data.get('original_content', self.original_content)
            self.grapesjs_content = backup_data.get('grapesjs_content', self.grapesjs_content)
            self.css_overrides = backup_data.get('css_overrides', self.css_overrides)
            self.js_modifications = backup_data.get('js_modifications', self.js_modifications)
            self.language = backup_data.get('language', self.language)
            self.version = backup_data.get('version', self.version)
            self.updated_at = datetime.now(timezone.utc)
            return True
        except Exception as e:
            print(f"Ошибка восстановления шаблона / Template restore error: {e}")
            return False
    
    def get_effective_content(self):
        """
        Получение эффективного содержимого шаблона / Get effective template content
        
        Returns:
            str: Эффективное содержимое (GrapesJS или оригинальное) / Effective content (GrapesJS or original)
        """
        return self.grapesjs_content if self.grapesjs_content else self.original_content
    
    def has_modifications(self):
        """
        Проверка наличия модификаций / Check if template has modifications
        
        Returns:
            bool: True если есть модификации / True if has modifications
        """
        return bool(self.grapesjs_content or self.css_overrides or self.js_modifications)
    
    def reset_to_original(self):
        """
        Сброс к оригинальному содержимому / Reset to original content
        
        Returns:
            bool: True если сброс успешен / True if reset successful
        """
        try:
            self.grapesjs_content = None
            self.css_overrides = None
            self.js_modifications = None
            self.updated_at = datetime.now(timezone.utc)
            return True
        except Exception as e:
            print(f"Ошибка сброса шаблона / Template reset error: {e}")
            return False
    
    @classmethod
    def get_by_path_and_language(cls, template_path, language='en'):
        """
        Получение шаблона по пути и языку / Get template by path and language
        
        Args:
            template_path (str): Путь к шаблону / Template path
            language (str): Язык шаблона / Template language
            
        Returns:
            EditablePageTemplate: Найденный шаблон или None / Found template or None
        """
        return cls.query.filter_by(
            template_path=template_path,
            language=language
        ).first()
    
    @classmethod
    def get_live_templates(cls, language='en'):
        """
        Получение активных шаблонов / Get live templates
        
        Args:
            language (str): Язык шаблонов / Template language
            
        Returns:
            list: Список активных шаблонов / List of live templates
        """
        return cls.query.filter_by(
            is_live=True,
            language=language
        ).all()
    
    def activate(self):
        """
        Активация шаблона / Activate template
        
        Returns:
            bool: True если активация успешна / True if activation successful
        """
        try:
            self.is_live = True
            self.updated_at = datetime.now(timezone.utc)
            return True
        except Exception as e:
            print(f"Ошибка активации шаблона / Template activation error: {e}")
            return False
    
    def deactivate(self):
        """
        Деактивация шаблона / Deactivate template
        
        Returns:
            bool: True если деактивация успешна / True if deactivation successful
        """
        try:
            self.is_live = False
            self.updated_at = datetime.now(timezone.utc)
            return True
        except Exception as e:
            print(f"Ошибка деактивации шаблона / Template deactivation error: {e}")
            return False