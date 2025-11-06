#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Spaced Repetition System with SM-2 Algorithm
Система интервального повторения с SM-2 алгоритмом
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta, timezone
from extensions import db
from models import User, Question, UserProgress, SpacedRepetitionItem, IRTParameters

class SimpleSpacedRepetition:
    """Система интервального повторения с SM-2 алгоритмом"""
    
    def __init__(self):
        self.min_ease_factor = 1.3
        self.max_ease_factor = 2.5
        self.initial_ease_factor = 2.5
        
    def calculate_next_review(self, user_id: int, question_id: int, 
                            quality: int, user_ability: float = None) -> Dict:
        """
        Расчет следующего повторения на основе SM-2 алгоритма
        
        Args:
            user_id: ID пользователя
            question_id: ID вопроса
            quality: Качество ответа (0-5)
            user_ability: IRT способность пользователя (опционально)
            
        Returns:
            Словарь с данными для следующего повторения
        """
        # Получаем или создаем элемент повторения
        item = self._get_or_create_item(user_id, question_id)
        
        # Получаем IRT параметры вопроса
        irt_params = self._get_irt_parameters(question_id)
        
        # Обновляем IRT данные
        if user_ability is not None:
            item.user_ability = user_ability
        if irt_params:
            item.irt_difficulty = irt_params.get('difficulty', 0.0)
        
        # Обновляем элемент после повторения
        item.update_after_review(quality, user_ability)
        
        # Сохраняем изменения
        db.session.commit()
        
        return {
            'next_review': item.next_review,
            'interval': item.interval,
            'ease_factor': item.ease_factor,
            'repetitions': item.repetitions,
            'quality': quality,
            'reason': self._get_review_reason(item, quality),
            'total_reviews': item.total_reviews,
            'average_quality': item.average_quality
        }
    
    def get_due_reviews(self, user_id: int, limit: int = 20) -> List[Dict]:
        """
        Получение вопросов, готовых к повторению
        
        Args:
            user_id: ID пользователя
            limit: Максимальное количество вопросов
            
        Returns:
            Список вопросов для повторения
        """
        # Получаем элементы, готовые к повторению
        due_items = SpacedRepetitionItem.query.filter_by(
            user_id=user_id,
            is_active=True
        ).filter(
            SpacedRepetitionItem.next_review <= datetime.now(timezone.utc)
        ).order_by(
            SpacedRepetitionItem.next_review.asc()
        ).limit(limit).all()
        
        # Преобразуем в словари с данными вопросов
        due_reviews = []
        for item in due_items:
            question = Question.query.get(item.question_id)
            if question:
                review_data = item.to_dict()
                review_data['question'] = {
                    'id': question.id,
                    'text': question.text,
                    'options': question.options,
                    'category': question.category,
                    'domain': question.domain
                }
                due_reviews.append(review_data)
        
        return due_reviews
    
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
        
        # Получаем статистику из БД
        items = SpacedRepetitionItem.query.filter_by(
            user_id=user_id,
            is_active=True
        ).filter(
            SpacedRepetitionItem.last_review >= start_date
        ).all()
        
        # Рассчитываем статистику
        total_reviews = len(items)
        correct_answers = sum(1 for item in items if item.quality >= 3)
        incorrect_answers = total_reviews - correct_answers
        average_accuracy = (correct_answers / total_reviews * 100) if total_reviews > 0 else 0
        
        # Статистика за сегодня
        today = datetime.now(timezone.utc).date()
        reviews_today = sum(1 for item in items if item.last_review and item.last_review.date() == today)
        
        # Статистика за неделю
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        reviews_this_week = sum(1 for item in items if item.last_review and item.last_review >= week_ago)
        
        # Количество просроченных повторений
        due_reviews = SpacedRepetitionItem.query.filter_by(
            user_id=user_id,
            is_active=True
        ).filter(
            SpacedRepetitionItem.next_review <= datetime.now(timezone.utc)
        ).count()
        
        return {
            'total_reviews': total_reviews,
            'correct_answers': correct_answers,
            'incorrect_answers': incorrect_answers,
            'average_accuracy': average_accuracy,
            'reviews_today': reviews_today,
            'reviews_this_week': reviews_this_week,
            'due_reviews': due_reviews,
            'period_days': days
        }
    
    def get_domain_statistics(self, user_id: int, days: int = 30) -> Dict:
        """
        Статистика по доменам
        
        Args:
            user_id: ID пользователя
            days: Количество дней для анализа
            
        Returns:
            Статистика по доменам
        """
        start_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Получаем статистику по доменам
        domain_stats = db.session.query(
            SpacedRepetitionItem.domain,
            db.func.count(SpacedRepetitionItem.id).label('total_reviews'),
            db.func.avg(SpacedRepetitionItem.average_quality).label('avg_quality'),
            db.func.sum(db.case((SpacedRepetitionItem.quality >= 3, 1), else_=0)).label('correct_answers')
        ).filter(
            SpacedRepetitionItem.user_id == user_id,
            SpacedRepetitionItem.is_active == True,
            SpacedRepetitionItem.last_review >= start_date,
            SpacedRepetitionItem.domain.isnot(None)
        ).group_by(
            SpacedRepetitionItem.domain
        ).all()
        
        result = {}
        for domain, total, avg_quality, correct in domain_stats:
            accuracy = (correct / total * 100) if total > 0 else 0
            result[domain] = {
                'total_reviews': total,
                'correct_answers': correct,
                'accuracy': accuracy,
                'average_quality': float(avg_quality) if avg_quality else 0
            }
        
        return result
    
    def _get_or_create_item(self, user_id: int, question_id: int) -> SpacedRepetitionItem:
        """Получение или создание элемента повторения"""
        item = SpacedRepetitionItem.query.filter_by(
            user_id=user_id,
            question_id=question_id
        ).first()
        
        if not item:
            # Получаем вопрос для определения домена
            question = Question.query.get(question_id)
            domain = question.domain if question else None
            
            # Создаем новый элемент
            item = SpacedRepetitionItem(
                user_id=user_id,
                question_id=question_id,
                domain=domain,
                next_review=datetime.now(timezone.utc) + timedelta(days=1),
                ease_factor=self.initial_ease_factor
            )
            db.session.add(item)
            db.session.flush()  # Получаем ID
        
        return item
    
    def _get_irt_parameters(self, question_id: int) -> Optional[Dict]:
        """Получение IRT параметров вопроса"""
        irt_params = IRTParameters.query.filter_by(question_id=question_id).first()
        if irt_params:
            return {
                'difficulty': irt_params.difficulty,
                'discrimination': irt_params.discrimination,
                'guessing': irt_params.guessing
            }
        return None
    
    def _get_review_reason(self, item: SpacedRepetitionItem, quality: int) -> str:
        """Получение причины повторения"""
        if quality < 3:
            return "Неправильный ответ - повторить через 1 день"
        elif item.repetitions == 0:
            return "Первое повторение"
        elif item.repetitions == 1:
            return "Второе повторение (через 6 дней)"
        else:
            return f"Повторение #{item.repetitions} (интервал: {item.interval} дней)"

class SimpleReviewScheduler:
    """Простой планировщик повторений с приоритизацией"""
    
    def __init__(self, srs: SimpleSpacedRepetition):
        self.srs = srs
    
    def schedule_daily_reviews(self, user_id: int, available_time: int) -> List[Dict]:
        """
        Планирование ежедневных повторений
        
        Args:
            user_id: ID пользователя
            available_time: Доступное время в минутах
            
        Returns:
            Список запланированных повторений
        """
        # Получаем вопросы, готовые к повторению
        due_reviews = self.srs.get_due_reviews(user_id, limit=100)
        
        # Сортируем по приоритету
        prioritized_reviews = self._prioritize_reviews(due_reviews)
        
        # Оцениваем время на каждый вопрос (2 минуты в среднем)
        estimated_time_per_question = 2
        
        # Рассчитываем максимальное количество вопросов
        max_questions = available_time // estimated_time_per_question
        
        # Выбираем вопросы в рамках доступного времени
        scheduled_reviews = prioritized_reviews[:max_questions]
        
        return scheduled_reviews
    
    def get_review_recommendations(self, user_id: int) -> Dict:
        """Получение рекомендаций по повторению"""
        stats = self.srs.get_review_statistics(user_id, days=7)
        domain_stats = self.srs.get_domain_statistics(user_id, days=7)
        
        recommendations = []
        
        # Рекомендации на основе количества просроченных повторений
        if stats['due_reviews'] > 10:
            recommendations.append({
                'type': 'high_priority',
                'message': f'У вас {stats["due_reviews"]} вопросов для повторения',
                'action': 'Начните с повторения сегодня',
                'priority': 'high'
            })
        elif stats['due_reviews'] > 5:
            recommendations.append({
                'type': 'medium_priority',
                'message': f'У вас {stats["due_reviews"]} вопросов для повторения',
                'action': 'Рекомендуется повторить в ближайшее время',
                'priority': 'medium'
            })
        
        # Рекомендации на основе точности
        if stats['average_accuracy'] < 70:
            recommendations.append({
                'type': 'improvement',
                'message': f'Точность ответов {stats["average_accuracy"]:.1f}%',
                'action': 'Сфокусируйтесь на повторении сложных вопросов',
                'priority': 'medium'
            })
        
        # Рекомендации на основе активности
        if stats['reviews_today'] == 0:
            recommendations.append({
                'type': 'reminder',
                'message': 'Сегодня еще не было повторений',
                'action': 'Выделите 15 минут на повторение',
                'priority': 'low'
            })
        
        # Рекомендации по доменам
        weak_domains = []
        for domain, domain_stat in domain_stats.items():
            if domain_stat['accuracy'] < 70:
                weak_domains.append({
                    'domain': domain,
                    'accuracy': domain_stat['accuracy'],
                    'total_reviews': domain_stat['total_reviews']
                })
        
        if weak_domains:
            weak_domains.sort(key=lambda x: x['accuracy'])
            recommendations.append({
                'type': 'domain_focus',
                'message': f'Слабые домены: {", ".join([d["domain"] for d in weak_domains[:3]])}',
                'action': 'Сфокусируйтесь на повторении этих доменов',
                'priority': 'medium',
                'weak_domains': weak_domains[:3]
            })
        
        return {
            'statistics': stats,
            'domain_statistics': domain_stats,
            'recommendations': recommendations,
            'total_recommendations': len(recommendations)
        }
    
    def _prioritize_reviews(self, reviews: List[Dict]) -> List[Dict]:
        """Приоритизация повторений"""
        for review in reviews:
            # Рассчитываем приоритет на основе нескольких факторов
            priority_score = 0
            
            # Фактор просрочки (самый важный)
            days_overdue = review.get('days_overdue', 0)
            priority_score += days_overdue * 10
            
            # Фактор качества ответов
            avg_quality = review.get('average_quality', 3.0)
            if avg_quality < 3.0:
                priority_score += (3.0 - avg_quality) * 5
            
            # Фактор количества повторений (меньше повторений = выше приоритет)
            repetitions = review.get('repetitions', 0)
            priority_score += max(0, 5 - repetitions)
            
            # Фактор приоритета из модели
            priority_score += review.get('priority_score', 0)
            
            review['calculated_priority'] = priority_score
        
        # Сортируем по приоритету (убывание)
        return sorted(reviews, key=lambda x: x['calculated_priority'], reverse=True) 