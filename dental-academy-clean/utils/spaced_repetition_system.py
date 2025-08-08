#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spaced Repetition System
Система интервального повторения на основе SM-2 алгоритма с IRT интеграцией
"""

import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from extensions import db
from models import User, Question, IRTParameters, UserProgress

@dataclass
class SpacedRepetitionItem:
    """Элемент системы интервального повторения"""
    question_id: int
    user_id: int
    domain: str
    ease_factor: float = 2.5  # Фактор легкости (SM-2)
    interval: int = 1  # Интервал в днях
    repetitions: int = 0  # Количество повторений
    quality: int = 0  # Качество ответа (0-5)
    next_review: datetime = None
    last_review: datetime = None
    irt_difficulty: float = 0.0
    user_ability: float = 0.0

class SpacedRepetitionSystem:
    """Система интервального повторения с IRT интеграцией"""
    
    def __init__(self):
        self.min_ease_factor = 1.3
        self.max_ease_factor = 2.5
        self.initial_ease_factor = 2.5
        
    def calculate_review_schedule(self, question_id: int, user_id: int, 
                                quality: int, user_ability: float = None) -> Dict:
        """
        Расчет расписания повторения на основе SM-2 + IRT
        
        Args:
            question_id: ID вопроса
            user_id: ID пользователя
            quality: Качество ответа (0-5)
            user_ability: IRT способность пользователя
            
        Returns:
            Словарь с данными для следующего повторения
        """
        # Получаем или создаем элемент повторения
        item = self._get_or_create_item(question_id, user_id)
        
        # Получаем IRT параметры вопроса
        irt_params = self._get_irt_parameters(question_id)
        
        # Обновляем IRT данные
        if user_ability is not None:
            item.user_ability = user_ability
        if irt_params:
            item.irt_difficulty = irt_params.get('difficulty', 0.0)
        
        # Рассчитываем IRT-скорректированное качество
        adjusted_quality = self._adjust_quality_by_irt(quality, item, irt_params)
        
        # Применяем SM-2 алгоритм
        new_interval, new_ease_factor, new_repetitions = self._sm2_algorithm(
            item, adjusted_quality
        )
        
        # Рассчитываем дату следующего повторения
        next_review = datetime.now(timezone.utc) + timedelta(days=new_interval)
        
        # Обновляем элемент
        item.interval = new_interval
        item.ease_factor = new_ease_factor
        item.repetitions = new_repetitions
        item.quality = quality
        item.last_review = datetime.now(timezone.utc)
        item.next_review = next_review
        
        # Сохраняем в БД
        self._save_item(item)
        
        return {
            'next_review': next_review,
            'interval': new_interval,
            'ease_factor': new_ease_factor,
            'repetitions': new_repetitions,
            'adjusted_quality': adjusted_quality,
            'irt_difficulty': item.irt_difficulty,
            'user_ability': item.user_ability
        }
    
    def _adjust_quality_by_irt(self, quality: int, item: SpacedRepetitionItem, 
                             irt_params: Dict) -> float:
        """
        Корректировка качества ответа на основе IRT
        
        Args:
            quality: Исходное качество (0-5)
            item: Элемент повторения
            irt_params: IRT параметры вопроса
            
        Returns:
            Скорректированное качество
        """
        if not irt_params:
            return quality
        
        difficulty = irt_params.get('difficulty', 0.0)
        discrimination = irt_params.get('discrimination', 1.0)
        guessing = irt_params.get('guessing', 0.25)
        
        # Рассчитываем ожидаемую вероятность правильного ответа
        expected_probability = self._3pl_probability(
            item.user_ability, difficulty, discrimination, guessing
        )
        
        # Корректируем качество на основе ожидаемой вероятности
        if expected_probability > 0.9:
            # Очень легкий вопрос - снижаем качество
            adjustment = -0.5
        elif expected_probability > 0.7:
            # Легкий вопрос - небольшая корректировка
            adjustment = -0.2
        elif expected_probability < 0.3:
            # Очень сложный вопрос - повышаем качество
            adjustment = 0.5
        elif expected_probability < 0.5:
            # Сложный вопрос - небольшая корректировка
            adjustment = 0.2
        else:
            # Средняя сложность - без корректировки
            adjustment = 0.0
        
        adjusted_quality = max(0, min(5, quality + adjustment))
        return adjusted_quality
    
    def _3pl_probability(self, theta: float, difficulty: float, 
                        discrimination: float, guessing: float) -> float:
        """3PL модель IRT для расчета вероятности правильного ответа"""
        try:
            exponent = discrimination * (theta - difficulty)
            probability = guessing + (1 - guessing) / (1 + math.exp(-exponent))
            return max(0.0, min(1.0, probability))
        except:
            return 0.5
    
    def _sm2_algorithm(self, item: SpacedRepetitionItem, quality: float) -> Tuple[int, float, int]:
        """
        SM-2 алгоритм для интервального повторения
        
        Args:
            item: Элемент повторения
            quality: Качество ответа (0-5)
            
        Returns:
            (новый_интервал, новый_ease_factor, новые_повторения)
        """
        # SM-2 алгоритм
        if quality >= 3:
            # Правильный ответ
            if item.repetitions == 0:
                new_interval = 1
            elif item.repetitions == 1:
                new_interval = 6
            else:
                new_interval = int(item.interval * item.ease_factor)
            
            new_repetitions = item.repetitions + 1
        else:
            # Неправильный ответ
            new_interval = 1
            new_repetitions = 0
        
        # Обновляем ease factor
        new_ease_factor = item.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        new_ease_factor = max(self.min_ease_factor, min(self.max_ease_factor, new_ease_factor))
        
        return new_interval, new_ease_factor, new_repetitions
    
    def get_due_items(self, user_id: int, domain: str = None, limit: int = 20) -> List[Dict]:
        """
        Получение элементов, готовых к повторению
        
        Args:
            user_id: ID пользователя
            domain: Домен (опционально)
            limit: Максимальное количество элементов
            
        Returns:
            Список элементов для повторения
        """
        current_time = datetime.now(timezone.utc)
        
        # Здесь должна быть логика получения из БД
        # Пока возвращаем заглушку
        due_items = []
        
        # Пример логики:
        # SELECT * FROM spaced_repetition_items 
        # WHERE user_id = ? AND next_review <= ? 
        # AND (domain = ? OR ? IS NULL)
        # ORDER BY next_review ASC LIMIT ?
        
        return due_items
    
    def get_review_statistics(self, user_id: int, days: int = 30) -> Dict:
        """
        Статистика повторений за период
        
        Args:
            user_id: ID пользователя
            days: Количество дней для анализа
            
        Returns:
            Статистика повторений
        """
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Здесь должна быть логика получения статистики из БД
        stats = {
            'total_reviews': 0,
            'correct_answers': 0,
            'incorrect_answers': 0,
            'average_quality': 0.0,
            'items_mastered': 0,
            'items_struggling': 0,
            'domain_breakdown': {},
            'daily_progress': []
        }
        
        return stats
    
    def _get_or_create_item(self, question_id: int, user_id: int) -> SpacedRepetitionItem:
        """Получение или создание элемента повторения"""
        # Здесь должна быть логика работы с БД
        # Пока возвращаем новый элемент
        return SpacedRepetitionItem(
            question_id=question_id,
            user_id=user_id,
            domain='THER',  # Должно получаться из вопроса
            ease_factor=self.initial_ease_factor
        )
    
    def _get_irt_parameters(self, question_id: int) -> Optional[Dict]:
        """Получение IRT параметров вопроса"""
        try:
            irt_params = IRTParameters.query.filter_by(question_id=question_id).first()
            if irt_params:
                return {
                    'difficulty': irt_params.difficulty,
                    'discrimination': irt_params.discrimination,
                    'guessing': irt_params.guessing
                }
        except:
            pass
        return None
    
    def _save_item(self, item: SpacedRepetitionItem):
        """Сохранение элемента в БД"""
        # Здесь должна быть логика сохранения в БД
        # Пока просто pass
        pass

class AdaptiveReviewScheduler:
    """Адаптивный планировщик повторений с IRT"""
    
    def __init__(self, srs: SpacedRepetitionSystem):
        self.srs = srs
        
    def schedule_optimal_reviews(self, user_id: int, available_time: int) -> List[Dict]:
        """
        Планирование оптимальных повторений на основе доступного времени
        
        Args:
            user_id: ID пользователя
            available_time: Доступное время в минутах
            
        Returns:
            Список запланированных повторений
        """
        # Получаем элементы, готовые к повторению
        due_items = self.srs.get_due_items(user_id, limit=50)
        
        # Сортируем по приоритету
        prioritized_items = self._prioritize_items(due_items, user_id)
        
        # Выбираем элементы в рамках доступного времени
        scheduled_items = []
        total_time = 0
        
        for item in prioritized_items:
            estimated_time = self._estimate_review_time(item)
            
            if total_time + estimated_time <= available_time:
                scheduled_items.append({
                    'question_id': item['question_id'],
                    'domain': item['domain'],
                    'estimated_time': estimated_time,
                    'priority_score': item['priority_score'],
                    'last_review': item['last_review'],
                    'interval': item['interval']
                })
                total_time += estimated_time
            else:
                break
        
        return scheduled_items
    
    def _prioritize_items(self, items: List[Dict], user_id: int) -> List[Dict]:
        """Приоритизация элементов для повторения"""
        for item in items:
            # Рассчитываем приоритет на основе:
            # 1. Времени с последнего повторения
            # 2. Сложности вопроса (IRT)
            # 3. Истории ответов пользователя
            
            priority_score = self._calculate_item_priority(item, user_id)
            item['priority_score'] = priority_score
        
        # Сортируем по приоритету
        return sorted(items, key=lambda x: x['priority_score'], reverse=True)
    
    def _calculate_item_priority(self, item: Dict, user_id: int) -> float:
        """Расчет приоритета элемента"""
        # Базовый приоритет на основе времени
        days_overdue = (datetime.now(timezone.utc) - item['last_review']).days
        base_priority = days_overdue / max(1, item['interval'])
        
        # Корректировка на основе IRT сложности
        irt_penalty = 1.0
        if item.get('irt_difficulty', 0) > 1.0:
            irt_penalty = 1.2  # Сложные вопросы получают приоритет
        
        # Корректировка на основе истории ответов
        history_penalty = 1.0
        if item.get('average_quality', 3.0) < 3.0:
            history_penalty = 1.3  # Проблемные вопросы получают приоритет
        
        return base_priority * irt_penalty * history_penalty
    
    def _estimate_review_time(self, item: Dict) -> int:
        """Оценка времени на повторение"""
        # Базовое время
        base_time = 2  # минуты
        
        # Корректировка на основе сложности
        if item.get('irt_difficulty', 0) > 1.0:
            base_time += 1
        
        # Корректировка на основе истории
        if item.get('average_quality', 3.0) < 3.0:
            base_time += 1
        
        return base_time 