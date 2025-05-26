# models/gamification.py
"""
Модели для системы геймификации
"""

from datetime import datetime, timedelta
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from models import db

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
    last_updated = Column(DateTime, default=datetime.utcnow)
    
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