#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IRT + Spaced Repetition Integration Engine
Интеграция IRT диагностики и системы интервального повторения
"""

import logging
import math
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass

from extensions import db
from models import (
    User, Question, IRTParameters, SpacedRepetitionItem, 
    DiagnosticSession, DiagnosticResponse, BIGDomain,
    PersonalLearningPlan, StudySession
)
from utils.irt_engine import IRTEngine
from utils.simple_spaced_repetition import SimpleSpacedRepetition
from utils.metrics import record_fallback_usage, record_error

logger = logging.getLogger(__name__)

@dataclass
class IRTSpacedItem:
    """Интегрированный элемент IRT + Spaced Repetition"""
    question_id: int
    user_id: int
    domain: str
    
    # IRT параметры
    irt_difficulty: float
    irt_discrimination: float
    irt_guessing: float
    user_ability: float
    
    # Spaced Repetition параметры (SM-2)
    ease_factor: float = 2.5
    interval: int = 1
    repetitions: int = 0
    quality: int = 0
    next_review: Optional[datetime] = None
    last_review: Optional[datetime] = None
    
    # Интеграционные параметры
    irt_adjusted_interval: Optional[int] = None
    confidence_level: float = 0.5
    learning_rate: float = 1.0

class IRTSpacedIntegration:
    """
    Интегрированная система IRT + Spaced Repetition
    
    Принципы интеграции:
    1. IRT определяет базовую сложность и способности пользователя
    2. Spaced Repetition адаптирует интервалы на основе IRT данных
    3. Обратная связь обновляет как IRT способности, так и SR интервалы
    """
    
    def __init__(self):
        self.irt_engine = IRTEngine()
        self.srs = SimpleSpacedRepetition()
        
        # Константы интеграции
        self.IRT_WEIGHT = 0.6  # Вес IRT в финальном решении
        self.SR_WEIGHT = 0.4   # Вес Spaced Repetition
        
        # Пороги для адаптации
        self.HIGH_CONFIDENCE_THRESHOLD = 0.8
        self.LOW_CONFIDENCE_THRESHOLD = 0.3
        self.ABILITY_CHANGE_THRESHOLD = 0.1
        
        # Множители для интервалов
        self.EASY_QUESTION_MULTIPLIER = 1.2  # Увеличиваем интервал для легких вопросов
        self.HARD_QUESTION_MULTIPLIER = 0.8  # Уменьшаем интервал для сложных вопросов
        
    def create_integrated_item(self, question_id: int, user_id: int, 
                             user_ability: float = None) -> IRTSpacedItem:
        """
        Создает интегрированный элемент IRT + Spaced Repetition
        
        Args:
            question_id: ID вопроса
            user_id: ID пользователя
            user_ability: IRT способность пользователя
            
        Returns:
            IRTSpacedItem с интегрированными параметрами
        """
        try:
            # Получаем вопрос и его IRT параметры
            question = Question.query.get(question_id)
            if not question:
                raise ValueError(f"Question {question_id} not found")
            
            # Получаем IRT параметры
            irt_params = IRTParameters.query.filter_by(question_id=question_id).first()
            if not irt_params:
                logger.warning(f"No IRT parameters for question {question_id}")
                # Используем дефолтные значения
                irt_difficulty = 0.0
                irt_discrimination = 1.0
                irt_guessing = 0.0
            else:
                irt_difficulty = irt_params.difficulty
                irt_discrimination = irt_params.discrimination
                irt_guessing = irt_params.guessing
            
            # Получаем домен
            domain = BIGDomain.query.get(question.big_domain_id)
            domain_code = domain.code if domain else "unknown"
            
            # Если способность не передана, получаем из последней диагностики
            if user_ability is None:
                user_ability = self._get_user_ability(user_id, domain_code)
            
            # Получаем или создаем Spaced Repetition элемент
            sr_item = SpacedRepetitionItem.query.filter_by(
                user_id=user_id, question_id=question_id
            ).first()
            
            if sr_item:
                # Используем существующие SR параметры
                ease_factor = sr_item.ease_factor
                interval = sr_item.interval
                repetitions = sr_item.repetitions
                quality = sr_item.quality
                next_review = sr_item.next_review
                last_review = sr_item.last_review
            else:
                # Создаем новые SR параметры
                ease_factor = 2.5
                interval = 1
                repetitions = 0
                quality = 0
                next_review = datetime.now(timezone.utc)
                last_review = None
            
            # Рассчитываем IRT-скорректированный интервал
            irt_adjusted_interval = self._calculate_irt_adjusted_interval(
                irt_difficulty, user_ability, interval
            )
            
            # Рассчитываем уровень уверенности
            confidence_level = self._calculate_confidence_level(
                irt_difficulty, user_ability, repetitions, quality
            )
            
            # Рассчитываем скорость обучения
            learning_rate = self._calculate_learning_rate(
                user_ability, irt_difficulty, repetitions, quality
            )
            
            return IRTSpacedItem(
                question_id=question_id,
                user_id=user_id,
                domain=domain_code,
                irt_difficulty=irt_difficulty,
                irt_discrimination=irt_discrimination,
                irt_guessing=irt_guessing,
                user_ability=user_ability,
                ease_factor=ease_factor,
                interval=interval,
                repetitions=repetitions,
                quality=quality,
                next_review=next_review,
                last_review=last_review,
                irt_adjusted_interval=irt_adjusted_interval,
                confidence_level=confidence_level,
                learning_rate=learning_rate
            )
            
        except Exception as e:
            logger.error(f"Error creating integrated item: {e}")
            record_error("irt_spaced_integration", f"create_integrated_item failed: {e}")
            raise
    
    def process_review_response(self, item: IRTSpacedItem, quality: int, 
                              response_time: float = None) -> Dict:
        """
        Обрабатывает ответ пользователя и обновляет интегрированные параметры
        
        Args:
            item: IRTSpacedItem
            quality: Качество ответа (0-5)
            response_time: Время ответа в секундах (опционально)
            
        Returns:
            Словарь с обновленными параметрами
        """
        try:
            # Обновляем базовые SR параметры
            old_interval = item.interval
            old_ease_factor = item.ease_factor
            
            # Применяем SM-2 алгоритм
            new_interval, new_ease_factor, new_repetitions = self._apply_sm2_algorithm(
                item, quality
            )
            
            # Рассчитываем IRT-скорректированное качество
            irt_adjusted_quality = self._adjust_quality_by_irt(
                quality, item.irt_difficulty, item.user_ability
            )
            
            # Обновляем IRT способность пользователя
            ability_change = self._update_user_ability(
                item, irt_adjusted_quality, response_time
            )
            
            # Рассчитываем финальный интервал с учетом IRT
            final_interval = self._calculate_final_interval(
                new_interval, item.irt_difficulty, item.user_ability + ability_change
            )
            
            # Обновляем элемент
            item.quality = quality
            item.interval = final_interval
            item.ease_factor = new_ease_factor
            item.repetitions = new_repetitions
            item.user_ability += ability_change
            item.last_review = datetime.now(timezone.utc)
            item.next_review = datetime.now(timezone.utc) + timedelta(days=final_interval)
            
            # Обновляем интегрированные параметры
            item.irt_adjusted_interval = self._calculate_irt_adjusted_interval(
                item.irt_difficulty, item.user_ability, final_interval
            )
            item.confidence_level = self._calculate_confidence_level(
                item.irt_difficulty, item.user_ability, item.repetitions, item.quality
            )
            item.learning_rate = self._calculate_learning_rate(
                item.user_ability, item.irt_difficulty, item.repetitions, item.quality
            )
            
            # Сохраняем в базу данных
            self._save_integrated_item(item)
            
            return {
                'success': True,
                'old_interval': old_interval,
                'new_interval': final_interval,
                'ability_change': ability_change,
                'irt_adjusted_quality': irt_adjusted_quality,
                'confidence_level': item.confidence_level,
                'learning_rate': item.learning_rate,
                'next_review': item.next_review
            }
            
        except Exception as e:
            logger.error(f"Error processing review response: {e}")
            record_error("irt_spaced_integration", f"process_review_response failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_optimal_review_schedule(self, user_id: int, domain: str = None, 
                                  max_items: int = 20) -> List[IRTSpacedItem]:
        """
        Получает оптимальное расписание повторений с учетом IRT
        
        Args:
            user_id: ID пользователя
            domain: Домен (опционально)
            max_items: Максимальное количество элементов
            
        Returns:
            Список IRTSpacedItem для повторения
        """
        try:
            # Получаем готовые к повторению элементы
            query = SpacedRepetitionItem.query.filter_by(
                user_id=user_id, is_active=True
            ).filter(
                SpacedRepetitionItem.next_review <= datetime.now(timezone.utc)
            )
            
            if domain:
                query = query.filter_by(domain=domain)
            
            sr_items = query.all()
            
            # Создаем интегрированные элементы
            integrated_items = []
            for sr_item in sr_items:
                try:
                    integrated_item = self.create_integrated_item(
                        sr_item.question_id, user_id
                    )
                    integrated_items.append(integrated_item)
                except Exception as e:
                    logger.warning(f"Failed to create integrated item for question {sr_item.question_id}: {e}")
                    continue
            
            # Сортируем по приоритету (IRT + SR)
            integrated_items.sort(key=lambda x: self._calculate_priority_score(x), reverse=True)
            
            # Возвращаем топ элементы
            return integrated_items[:max_items]
            
        except Exception as e:
            logger.error(f"Error getting optimal review schedule: {e}")
            record_error("irt_spaced_integration", f"get_optimal_review_schedule failed: {e}")
            return []
    
    def generate_adaptive_daily_plan(self, user_id: int, target_minutes: int = 30) -> Dict:
        """
        Генерирует адаптивный ежедневный план с интеграцией IRT + SR
        
        Args:
            user_id: ID пользователя
            target_minutes: Целевое время в минутах
            
        Returns:
            Словарь с ежедневным планом
        """
        try:
            # Получаем пользователя
            user = User.query.get(user_id)
            if not user:
                raise ValueError(f"User {user_id} not found")
            
            # Получаем активный план обучения
            active_plan = PersonalLearningPlan.query.filter_by(
                user_id=user_id, status='active'
            ).first()
            
            if not active_plan:
                raise ValueError("No active learning plan found")
            
            # Получаем текущие способности
            current_abilities = self._get_current_abilities(user_id)
            
            # Получаем готовые к повторению элементы
            review_items = self.get_optimal_review_schedule(user_id, max_items=50)
            
            # Распределяем время
            review_time = min(target_minutes * 0.4, len(review_items) * 3)  # 40% на повторения
            new_content_time = target_minutes - review_time
            
            # Формируем план
            daily_plan = {
                'user_id': user_id,
                'target_minutes': target_minutes,
                'current_abilities': current_abilities,
                'review_items': review_items[:int(review_time / 3)],  # 3 минуты на повторение
                'new_content': self._select_new_content(user_id, current_abilities, new_content_time),
                'estimated_time': {
                    'review': review_time,
                    'new_content': new_content_time,
                    'total': target_minutes
                },
                'irt_insights': self._generate_irt_insights(user_id, current_abilities),
                'learning_recommendations': self._generate_learning_recommendations(
                    user_id, current_abilities, review_items
                )
            }
            
            return daily_plan
            
        except Exception as e:
            logger.error(f"Error generating adaptive daily plan: {e}")
            record_error("irt_spaced_integration", f"generate_adaptive_daily_plan failed: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    # Приватные методы
    
    def _get_user_ability(self, user_id: int, domain: str) -> float:
        """Получает IRT способность пользователя для домена"""
        try:
            # Получаем последнюю диагностическую сессию
            session = DiagnosticSession.query.filter_by(
                user_id=user_id
            ).order_by(DiagnosticSession.id.desc()).first()
            
            if session and session.session_data:
                domain_abilities = session.session_data.get('domain_abilities', {})
                return domain_abilities.get(domain, 0.0)
            
            return 0.0
            
        except Exception as e:
            logger.warning(f"Error getting user ability: {e}")
            return 0.0
    
    def _calculate_irt_adjusted_interval(self, difficulty: float, ability: float, 
                                       base_interval: int) -> int:
        """Рассчитывает IRT-скорректированный интервал"""
        # Разница между сложностью и способностью
        difficulty_gap = abs(difficulty - ability)
        
        # Если вопрос слишком легкий для пользователя
        if ability > difficulty + 0.5:
            return int(base_interval * self.EASY_QUESTION_MULTIPLIER)
        # Если вопрос слишком сложный
        elif ability < difficulty - 0.5:
            return int(base_interval * self.HARD_QUESTION_MULTIPLIER)
        # Если сложность подходящая
        else:
            return base_interval
    
    def _calculate_confidence_level(self, difficulty: float, ability: float, 
                                  repetitions: int, quality: int) -> float:
        """Рассчитывает уровень уверенности в знании"""
        # Базовый уровень на основе IRT
        irt_confidence = 1.0 / (1.0 + math.exp(-(ability - difficulty)))
        
        # Корректировка на основе истории повторений
        sr_confidence = min(1.0, repetitions * 0.2 + quality * 0.1)
        
        # Взвешенное среднее
        return self.IRT_WEIGHT * irt_confidence + self.SR_WEIGHT * sr_confidence
    
    def _calculate_learning_rate(self, ability: float, difficulty: float, 
                               repetitions: int, quality: int) -> float:
        """Рассчитывает скорость обучения"""
        # Базовая скорость на основе IRT
        if ability < difficulty:
            base_rate = 1.2  # Быстрее учимся сложным вещам
        else:
            base_rate = 0.8  # Медленнее учимся легким вещам
        
        # Корректировка на основе качества ответов
        quality_factor = 1.0 + (quality - 2.5) * 0.1
        
        # Корректировка на основе количества повторений
        repetition_factor = 1.0 - repetitions * 0.05
        
        return base_rate * quality_factor * repetition_factor
    
    def _apply_sm2_algorithm(self, item: IRTSpacedItem, quality: int) -> Tuple[int, float, int]:
        """Применяет SM-2 алгоритм"""
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
        new_ease_factor = max(1.3, min(2.5, new_ease_factor))
        
        return new_interval, new_ease_factor, new_repetitions
    
    def _adjust_quality_by_irt(self, quality: int, difficulty: float, ability: float) -> float:
        """Корректирует качество ответа на основе IRT"""
        # Если вопрос слишком легкий, снижаем качество
        if ability > difficulty + 1.0:
            return max(0, quality - 1)
        # Если вопрос слишком сложный, повышаем качество
        elif ability < difficulty - 1.0:
            return min(5, quality + 1)
        else:
            return quality
    
    def _update_user_ability(self, item: IRTSpacedItem, adjusted_quality: float, 
                           response_time: float = None) -> float:
        """Обновляет IRT способность пользователя"""
        # Простая модель обновления способности
        if adjusted_quality >= 3:
            # Правильный ответ - увеличиваем способность
            ability_change = 0.05 * item.learning_rate
        else:
            # Неправильный ответ - уменьшаем способность
            ability_change = -0.03 * item.learning_rate
        
        # Корректировка на основе времени ответа
        if response_time:
            if response_time < 10:  # Быстрый ответ
                ability_change *= 1.2
            elif response_time > 60:  # Медленный ответ
                ability_change *= 0.8
        
        return ability_change
    
    def _calculate_final_interval(self, sr_interval: int, difficulty: float, 
                                ability: float) -> int:
        """Рассчитывает финальный интервал с учетом IRT"""
        irt_adjusted = self._calculate_irt_adjusted_interval(difficulty, ability, sr_interval)
        
        # Взвешенное среднее
        return int(self.SR_WEIGHT * sr_interval + self.IRT_WEIGHT * irt_adjusted)
    
    def _calculate_priority_score(self, item: IRTSpacedItem) -> float:
        """Рассчитывает приоритет элемента для повторения"""
        # Базовый приоритет на основе просрочки
        days_overdue = 0
        if item.next_review and item.next_review < datetime.now(timezone.utc):
            days_overdue = (datetime.now(timezone.utc) - item.next_review).days
        
        overdue_score = min(10, days_overdue * 0.5)
        
        # Приоритет на основе IRT
        difficulty_gap = abs(item.irt_difficulty - item.user_ability)
        irt_score = 5 * (1 - difficulty_gap)  # Выше приоритет для подходящих по сложности
        
        # Приоритет на основе уверенности
        confidence_score = (1 - item.confidence_level) * 3  # Выше приоритет для неопределенных
        
        return overdue_score + irt_score + confidence_score
    
    def _save_integrated_item(self, item: IRTSpacedItem):
        """Сохраняет интегрированный элемент в базу данных"""
        try:
            # Обновляем SpacedRepetitionItem
            sr_item = SpacedRepetitionItem.query.filter_by(
                user_id=item.user_id, question_id=item.question_id
            ).first()
            
            if sr_item:
                sr_item.ease_factor = item.ease_factor
                sr_item.interval = item.interval
                sr_item.repetitions = item.repetitions
                sr_item.quality = item.quality
                sr_item.next_review = item.next_review
                sr_item.last_review = item.last_review
                sr_item.user_ability = item.user_ability
                sr_item.irt_difficulty = item.irt_difficulty
            else:
                # Создаем новый элемент
                sr_item = SpacedRepetitionItem(
                    user_id=item.user_id,
                    question_id=item.question_id,
                    domain=item.domain,
                    ease_factor=item.ease_factor,
                    interval=item.interval,
                    repetitions=item.repetitions,
                    quality=item.quality,
                    next_review=item.next_review,
                    last_review=item.last_review,
                    user_ability=item.user_ability,
                    irt_difficulty=item.irt_difficulty
                )
                db.session.add(sr_item)
            
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Error saving integrated item: {e}")
            db.session.rollback()
            raise
    
    def _get_current_abilities(self, user_id: int) -> Dict[str, float]:
        """Получает текущие способности пользователя"""
        try:
            session = DiagnosticSession.query.filter_by(
                user_id=user_id
            ).order_by(DiagnosticSession.id.desc()).first()
            
            if session and session.session_data:
                # session_data может быть строкой JSON
                if isinstance(session.session_data, str):
                    import json
                    data = json.loads(session.session_data)
                else:
                    data = session.session_data
                return data.get('domain_abilities', {})
            
            return {}
            
        except Exception as e:
            logger.warning(f"Error getting current abilities: {e}")
            return {}
    
    def _select_new_content(self, user_id: int, abilities: Dict[str, float], 
                          time_minutes: int) -> List[Dict]:
        """Выбирает новый контент для изучения"""
        # Заглушка - в реальной реализации здесь будет логика выбора контента
        return []
    
    def _generate_irt_insights(self, user_id: int, abilities: Dict[str, float]) -> Dict:
        """Генерирует IRT инсайты для пользователя"""
        insights = {
            'strongest_domain': None,
            'weakest_domain': None,
            'overall_ability': 0.0,
            'recommendations': []
        }
        
        if abilities:
            # Находим сильные и слабые домены
            sorted_domains = sorted(abilities.items(), key=lambda x: x[1], reverse=True)
            insights['strongest_domain'] = sorted_domains[0][0] if sorted_domains else None
            insights['weakest_domain'] = sorted_domains[-1][0] if sorted_domains else None
            insights['overall_ability'] = sum(abilities.values()) / len(abilities)
            
            # Генерируем рекомендации
            if insights['overall_ability'] < 0.3:
                insights['recommendations'].append("Рекомендуется больше практики в слабых областях")
            elif insights['overall_ability'] > 0.7:
                insights['recommendations'].append("Отличный прогресс! Можно переходить к более сложным темам")
        
        return insights
    
    def _generate_learning_recommendations(self, user_id: int, abilities: Dict[str, float], 
                                         review_items: List[IRTSpacedItem]) -> List[str]:
        """Генерирует рекомендации по обучению"""
        recommendations = []
        
        # Анализируем готовые к повторению элементы
        if review_items:
            recommendations.append(f"У вас {len(review_items)} элементов готовых к повторению")
        
        # Анализируем способности
        if abilities:
            weak_domains = [domain for domain, ability in abilities.items() if ability < 0.5]
            if weak_domains:
                recommendations.append(f"Рекомендуется уделить внимание доменам: {', '.join(weak_domains)}")
        
        return recommendations

# Глобальный экземпляр для использования в других модулях
_irt_spaced_integration_instance = None

def get_irt_spaced_integration() -> IRTSpacedIntegration:
    """Получает глобальный экземпляр IRTSpacedIntegration"""
    global _irt_spaced_integration_instance
    if _irt_spaced_integration_instance is None:
        _irt_spaced_integration_instance = IRTSpacedIntegration()
    return _irt_spaced_integration_instance

# Для обратной совместимости
irt_spaced_integration = get_irt_spaced_integration 