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
    password_hash = db.Column(db.String(200), nullable=False) 
    name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_login = db.Column(db.DateTime)
    role = db.Column(db.String(20), default='user')
    has_subscription = db.Column(db.Boolean, default=False)
    subscription_expires = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    language = db.Column(db.String(5), default='en')
    # Отношения
    progress = db.relationship('UserProgress', backref='user', lazy='dynamic',
                              cascade='all, delete-orphan')
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