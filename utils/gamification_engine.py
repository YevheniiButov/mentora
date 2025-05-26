# utils/gamification_engine.py
"""
Движок геймификации
"""

import json
from typing import List, Dict, Optional
from datetime import datetime, timedelta

class GamificationEngine:
    """Основной класс системы геймификации"""
    
    def __init__(self, db_session):
        self.db = db_session
        self.level_thresholds = [0, 100, 250, 500, 1000, 1750, 2750, 4250, 6500, 10000, 15000]
        
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
    
    def get_or_create_user_stats(self, user_id: int):
        """Получает или создает статистику пользователя"""
        from models import UserStats
        
        stats = self.db.query(UserStats).filter_by(user_id=user_id).first()
        if not stats:
            stats = UserStats(user_id=user_id)
            self.db.add(stats)
            self.db.commit()
        return stats
    
    def award_experience_points(self, user_id: int, points: int, source: str = None) -> Dict:
        """Начисляет очки опыта пользователю"""

        print(f"🔍 DEBUG award_experience_points: user_id={user_id}, points={points}, source={source}")
        stats = self.get_or_create_user_stats(user_id)
        old_level = stats.current_level
        print(f"🔍 DEBUG: old XP = {stats.total_experience_points}, old level = {old_level}")
        # Начисляем очки
        stats.total_experience_points += points
        print(f"🔍 DEBUG: new XP = {stats.total_experience_points}")
        # Проверяем повышение уровня
        new_level = self.calculate_level(stats.total_experience_points)
        level_up = new_level > old_level
        
        if level_up:
            stats.current_level = new_level
            
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
        """Обрабатывает завершение сценария и начисляет награды"""
        print(f"🔍 DEBUG: attempt_data = {attempt_data}")

        rewards = {
            'experience_points': 0,
            'new_achievements': [],
            'level_up': False
        }
        
        stats = self.get_or_create_user_stats(user_id)
        score = attempt_data.get('score', 0)
        max_score = attempt_data.get('max_score', 100)
        score_percentage = (score / max_score) * 100 if max_score > 0 else 0
        print(f"🔍 DEBUG: score={score}, max_score={max_score}, percentage={score_percentage}")
        # Обновляем статистику
        stats.total_scenarios_completed += 1
        stats.total_score_earned += score
        
        if stats.total_scenarios_completed > 0:
            stats.average_score_percentage = stats.total_score_earned / stats.total_scenarios_completed
        
        # Обновляем активность
        stats.last_activity_date = datetime.utcnow()
        
        # Начисляем базовые очки опыта
        base_points = self.calculate_base_experience_points(score_percentage)
        print(f"🔍 DEBUG: base_points={base_points}")
        # Начисляем очки опыта
        xp_result = self.award_experience_points(user_id, base_points, 'scenario_completion')
        rewards.update(xp_result)
        rewards['experience_points'] = rewards['points_awarded']  
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