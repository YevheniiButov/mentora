"""
Virtual Patient Daily Learning Utils
Утилиты для системы ежедневного обучения с виртуальными пациентами
"""

import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy import and_, or_, desc, func

from models import VirtualPatientScenario, VirtualPatientAttempt, User, db


class VirtualPatientSelector:
    """Класс для выбора сценариев виртуальных пациентов для ежедневного обучения"""
    
    def __init__(self, user: User):
        self.user = user
        self.specialty = getattr(user, 'specialty', 'dentistry')
    
    def get_daily_scenarios(self, limit: int = 3) -> List[VirtualPatientScenario]:
        """
        Получить сценарии для ежедневного обучения
        
        Args:
            limit: Максимальное количество сценариев
            
        Returns:
            Список доступных сценариев
        """
        # Получаем сценарии, подходящие для пользователя
        available_scenarios = self._get_available_scenarios()
        
        # Фильтруем по специальности
        specialty_scenarios = [
            scenario for scenario in available_scenarios 
            if scenario.specialty == self.specialty
        ]
        
        # Если нет сценариев для специальности, берем общие
        if not specialty_scenarios:
            specialty_scenarios = [
                scenario for scenario in available_scenarios 
                if scenario.specialty == 'general'
            ]
        
        # Сортируем по приоритету (новые, не игранные, по сложности)
        prioritized_scenarios = self._prioritize_scenarios(specialty_scenarios)
        
        return prioritized_scenarios[:limit]
    
    def _get_available_scenarios(self) -> List[VirtualPatientScenario]:
        """Получить все доступные опубликованные сценарии"""
        return VirtualPatientScenario.query.filter(
            VirtualPatientScenario.is_published == True
        ).all()
    
    def _prioritize_scenarios(self, scenarios: List[VirtualPatientScenario]) -> List[VirtualPatientScenario]:
        """
        Приоритизировать сценарии для ежедневного обучения
        
        Приоритет:
        1. Никогда не игранные
        2. Не игранные в последние 7 дней
        3. По сложности (easy -> medium -> hard)
        4. По дате создания (новые)
        """
        never_played = []
        not_recently_played = []
        recently_played = []
        
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        
        for scenario in scenarios:
            last_attempt = VirtualPatientAttempt.query.filter(
                and_(
                    VirtualPatientAttempt.user_id == self.user.id,
                    VirtualPatientAttempt.scenario_id == scenario.id
                )
            ).order_by(desc(VirtualPatientAttempt.completed_at)).first()
            
            if not last_attempt:
                never_played.append(scenario)
            elif last_attempt.completed_at and last_attempt.completed_at < seven_days_ago:
                not_recently_played.append(scenario)
            else:
                recently_played.append(scenario)
        
        # Сортируем каждую группу по сложности и дате
        def sort_by_difficulty_and_date(scenarios_list):
            difficulty_order = {'easy': 1, 'medium': 2, 'hard': 3}
            return sorted(scenarios_list, key=lambda x: (
                difficulty_order.get(x.difficulty, 2),
                x.created_at
            ))
        
        # Объединяем в порядке приоритета
        prioritized = []
        prioritized.extend(sort_by_difficulty_and_date(never_played))
        prioritized.extend(sort_by_difficulty_and_date(not_recently_played))
        prioritized.extend(sort_by_difficulty_and_date(recently_played))
        
        return prioritized
    
    def get_scenario_by_keywords(self, keywords: List[str], limit: int = 5) -> List[VirtualPatientScenario]:
        """
        Найти сценарии по ключевым словам
        
        Args:
            keywords: Список ключевых слов для поиска
            limit: Максимальное количество результатов
            
        Returns:
            Список подходящих сценариев
        """
        if not keywords:
            return []
        
        # Поиск по ключевым словам в target_keywords
        keyword_conditions = []
        for keyword in keywords:
            keyword_conditions.append(
                VirtualPatientScenario.target_keywords.contains(keyword)
            )
        
        scenarios = VirtualPatientScenario.query.filter(
            and_(
                VirtualPatientScenario.is_published == True,
                VirtualPatientScenario.specialty == self.specialty,
                or_(*keyword_conditions)
            )
        ).limit(limit).all()
        
        return scenarios
    
    def get_user_progress_stats(self) -> Dict:
        """
        Получить статистику прогресса пользователя
        
        Returns:
            Словарь со статистикой
        """
        # Общая статистика
        total_attempts = VirtualPatientAttempt.query.filter(
            VirtualPatientAttempt.user_id == self.user.id
        ).count()
        
        completed_attempts = VirtualPatientAttempt.query.filter(
            and_(
                VirtualPatientAttempt.user_id == self.user.id,
                VirtualPatientAttempt.completed == True
            )
        ).count()
        
        # Статистика за последние 30 дней
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_attempts = VirtualPatientAttempt.query.filter(
            and_(
                VirtualPatientAttempt.user_id == self.user.id,
                VirtualPatientAttempt.started_at >= thirty_days_ago
            )
        ).count()
        
        # Средний балл
        avg_score_result = db.session.query(
            func.avg(VirtualPatientAttempt.score)
        ).filter(
            and_(
                VirtualPatientAttempt.user_id == self.user.id,
                VirtualPatientAttempt.completed == True
            )
        ).scalar()
        
        avg_score = float(avg_score_result) if avg_score_result else 0.0
        
        # Статистика по специальностям
        specialty_stats = db.session.query(
            VirtualPatientScenario.specialty,
            func.count(VirtualPatientAttempt.id).label('attempts'),
            func.avg(VirtualPatientAttempt.score).label('avg_score')
        ).join(
            VirtualPatientAttempt, 
            VirtualPatientScenario.id == VirtualPatientAttempt.scenario_id
        ).filter(
            VirtualPatientAttempt.user_id == self.user.id
        ).group_by(
            VirtualPatientScenario.specialty
        ).all()
        
        return {
            'total_attempts': total_attempts,
            'completed_attempts': completed_attempts,
            'completion_rate': (completed_attempts / total_attempts * 100) if total_attempts > 0 else 0,
            'recent_attempts': recent_attempts,
            'average_score': round(avg_score, 1),
            'specialty_stats': [
                {
                    'specialty': stat.specialty,
                    'attempts': stat.attempts,
                    'avg_score': round(float(stat.avg_score or 0), 1)
                }
                for stat in specialty_stats
            ]
        }
    
    def get_recommended_scenarios(self, limit: int = 3) -> List[VirtualPatientScenario]:
        """
        Получить рекомендованные сценарии на основе прогресса пользователя
        
        Args:
            limit: Максимальное количество рекомендаций
            
        Returns:
            Список рекомендованных сценариев
        """
        # Получаем сценарии, которые пользователь еще не проходил
        attempted_scenario_ids = db.session.query(
            VirtualPatientAttempt.scenario_id
        ).filter(
            VirtualPatientAttempt.user_id == self.user.id
        ).subquery()
        
        new_scenarios = VirtualPatientScenario.query.filter(
            and_(
                VirtualPatientScenario.is_published == True,
                VirtualPatientScenario.specialty == self.specialty,
                ~VirtualPatientScenario.id.in_(attempted_scenario_ids)
            )
        ).limit(limit).all()
        
        # Если новых сценариев недостаточно, добавляем недавно не игранные
        if len(new_scenarios) < limit:
            remaining_limit = limit - len(new_scenarios)
            additional_scenarios = self.get_daily_scenarios(remaining_limit)
            new_scenarios.extend(additional_scenarios)
        
        return new_scenarios[:limit]


class VirtualPatientSessionManager:
    """Менеджер сессий виртуальных пациентов"""
    
    def __init__(self, user: User, scenario: VirtualPatientScenario):
        self.user = user
        self.scenario = scenario
        self.attempt = None
    
    def start_session(self) -> VirtualPatientAttempt:
        """
        Начать новую сессию
        
        Returns:
            Созданная попытка
        """
        self.attempt = VirtualPatientAttempt(
            user_id=self.user.id,
            scenario_id=self.scenario.id,
            max_score=self.scenario.max_score,
            started_at=datetime.utcnow()
        )
        
        db.session.add(self.attempt)
        db.session.commit()
        
        return self.attempt
    
    def save_fill_in_answer(self, node_id: str, answer: str) -> bool:
        """
        Сохранить ответ на fill-in вопрос
        
        Args:
            node_id: ID узла диалога
            answer: Ответ пользователя
            
        Returns:
            True если успешно сохранено
        """
        if not self.attempt:
            return False
        
        try:
            self.attempt.add_fill_in_answer(node_id, answer)
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False
    
    def complete_session(self, score: int, dialogue_history: List[Dict] = None) -> bool:
        """
        Завершить сессию
        
        Args:
            score: Полученный балл
            dialogue_history: История диалога
            
        Returns:
            True если успешно завершено
        """
        if not self.attempt:
            return False
        
        try:
            self.attempt.score = score
            self.attempt.completed = True
            self.attempt.completed_at = datetime.utcnow()
            
            if dialogue_history:
                self.attempt.dialogue_history = json.dumps(dialogue_history)
            
            # Обновляем время прохождения
            if self.attempt.started_at:
                time_spent = (self.attempt.completed_at - self.attempt.started_at).total_seconds() / 60
                self.attempt.time_spent = time_spent
            
            # Отмечаем сценарий как сыгранный
            self.scenario.mark_played()
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False
    
    def get_session_data(self) -> Dict:
        """
        Получить данные текущей сессии
        
        Returns:
            Словарь с данными сессии
        """
        if not self.attempt:
            return {}
        
        return {
            'attempt_id': self.attempt.id,
            'scenario_id': self.attempt.scenario_id,
            'score': self.attempt.score,
            'max_score': self.attempt.max_score,
            'completed': self.attempt.completed,
            'time_spent': self.attempt.time_spent,
            'started_at': self.attempt.started_at.isoformat() if self.attempt.started_at else None,
            'completed_at': self.attempt.completed_at.isoformat() if self.attempt.completed_at else None,
            'fill_in_answers': self.attempt.fill_in_answers_dict,
            'fill_in_score': self.attempt.fill_in_score
        }


def calculate_fill_in_score(answers: Dict[str, str], correct_answers: Dict[str, str]) -> int:
    """
    Вычислить балл за fill-in вопросы
    
    Args:
        answers: Ответы пользователя {node_id: answer}
        correct_answers: Правильные ответы {node_id: correct_answer}
        
    Returns:
        Количество правильных ответов
    """
    if not answers or not correct_answers:
        return 0
    
    correct_count = 0
    for node_id, user_answer in answers.items():
        if node_id in correct_answers:
            correct_answer = correct_answers[node_id].lower().strip()
            user_answer_clean = user_answer.lower().strip()
            
            # Простое сравнение (можно улучшить)
            if correct_answer == user_answer_clean:
                correct_count += 1
    
    return correct_count


def get_daily_learning_summary(user: User) -> Dict:
    """
    Получить сводку ежедневного обучения
    
    Args:
        user: Пользователь
        
    Returns:
        Словарь со сводкой
    """
    selector = VirtualPatientSelector(user)
    
    # Статистика за сегодня
    today = datetime.utcnow().date()
    today_attempts = VirtualPatientAttempt.query.filter(
        and_(
            VirtualPatientAttempt.user_id == user.id,
            func.date(VirtualPatientAttempt.started_at) == today
        )
    ).count()
    
    # Доступные сценарии
    available_scenarios = selector.get_daily_scenarios(5)
    
    # Рекомендации
    recommended = selector.get_recommended_scenarios(3)
    
    # Общая статистика
    stats = selector.get_user_progress_stats()
    
    return {
        'today_attempts': today_attempts,
        'available_scenarios': [
            {
                'id': scenario.id,
                'title': scenario.title,
                'difficulty': scenario.difficulty,
                'category': scenario.category,
                'max_score': scenario.max_score,
                'specialty': scenario.specialty
            }
            for scenario in available_scenarios
        ],
        'recommended_scenarios': [
            {
                'id': scenario.id,
                'title': scenario.title,
                'difficulty': scenario.difficulty,
                'category': scenario.category,
                'max_score': scenario.max_score,
                'specialty': scenario.specialty
            }
            for scenario in recommended
        ],
        'stats': stats
    }
