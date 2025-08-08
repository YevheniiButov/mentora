#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Learning Recommendation Engine
Улучшенная система рекомендаций с интеграцией IRT и временной приоритизации
"""

import json
import math
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from extensions import db
from models import (
    User, PersonalLearningPlan, BIGDomain, Question, 
    IRTParameters, UserProgress, VirtualPatientScenario,
    DiagnosticSession, DiagnosticResponse
)

@dataclass
class IRTTestResult:
    """Результат IRT диагностики"""
    domain: str
    theta_estimate: float  # IRT способность
    standard_error: float  # Стандартная ошибка
    questions_answered: int
    correct_answers: int
    time_spent: float  # в минутах

@dataclass
class EnhancedLearningRecommendation:
    """Улучшенная рекомендация для обучения"""
    domain: str
    priority_score: float  # Комбинированный приоритет
    skill_gap: float  # Разрыв между текущим и целевым уровнем
    exam_importance: float  # Важность в экзамене
    urgency_factor: float  # Временной фактор
    recommended_content: Dict[str, List]  # Контент по типам
    estimated_time: int  # в минутах
    difficulty_level: str
    confidence_level: str  # Уверенность в рекомендации

class EnhancedLearningRecommendationEngine:
    """Улучшенный движок рекомендаций с IRT интеграцией"""
    
    def __init__(self):
        self.target_theta = 0.5  # Целевой уровень для экзамена
        self.min_confidence = 0.7  # Минимальная уверенность для рекомендаций
        
    def get_big_exam_weights_2025(self) -> Dict[str, float]:
        """Веса доменов в экзамене BI-toets 2025"""
        return {
            'THER': 8.0,   # Терапевтическая стоматология
            'SURG': 7.0,   # Хирургическая стоматология
            'ORTH': 6.0,   # Ортодонтия
            'PEDO': 5.0,   # Детская стоматология
            'PERI': 5.0,   # Пародонтология
            'ENDO': 4.0,   # Эндодонтия
            'RAD': 4.0,    # Рентгенология
            'STAT': 3.0,   # Статистика
            'RES': 3.0,    # Исследования
            'COMM': 2.0,   # Коммуникация
            'ETH': 2.0,    # Этика
            'LAW': 1.0,    # Право
            # ... остальные домены
        }
    
    def calculate_urgency_factor(self, exam_date: Optional[datetime], 
                                current_date: datetime = None) -> float:
        """Расчет фактора срочности на основе даты экзамена"""
        if not exam_date:
            return 1.0  # Нейтральный фактор если дата не указана
            
        if not current_date:
            current_date = datetime.now(timezone.utc)
            
        days_to_exam = (exam_date - current_date).days
        
        if days_to_exam <= 30:
            return 3.0  # Высокая срочность
        elif days_to_exam <= 90:
            return 2.0  # Средняя срочность
        elif days_to_exam <= 180:
            return 1.5  # Умеренная срочность
        else:
            return 1.0  # Низкая срочность
    
    def post_diagnostic_algorithm(self, user_id: int, 
                                 diagnostic_results: List[IRTTestResult],
                                 exam_date: Optional[datetime] = None) -> List[EnhancedLearningRecommendation]:
        """
        Основной алгоритм пост-диагностических рекомендаций
        
        Args:
            user_id: ID пользователя
            diagnostic_results: Результаты IRT диагностики
            exam_date: Дата экзамена
            
        Returns:
            Список улучшенных рекомендаций
        """
        user = User.query.get(user_id)
        if not user:
            return []
            
        # Получаем веса экзамена
        exam_weights = self.get_big_exam_weights_2025()
        
        # Рассчитываем фактор срочности
        urgency_factor = self.calculate_urgency_factor(exam_date)
        
        # Создаем словарь способностей по доменам
        domain_abilities = {result.domain: result.theta_estimate for result in diagnostic_results}
        
        # Рассчитываем приоритеты для каждого домена
        priorities = {}
        for result in diagnostic_results:
            domain = result.domain
            
            # Разрыв в навыках (skill gap)
            skill_gap = max(0, self.target_theta - result.theta_estimate)
            
            # Важность в экзамене
            exam_importance = exam_weights.get(domain, 1.0)
            
            # Комбинированный приоритет
            priority_score = skill_gap * exam_importance * urgency_factor
            
            # Учитываем уверенность в оценке
            confidence_penalty = 1.0 - min(1.0, result.standard_error / 0.5)
            priority_score *= confidence_penalty
            
            priorities[domain] = {
                'priority_score': priority_score,
                'skill_gap': skill_gap,
                'exam_importance': exam_importance,
                'urgency_factor': urgency_factor,
                'confidence': confidence_penalty,
                'theta_estimate': result.theta_estimate,
                'standard_error': result.standard_error
            }
        
        # Сортируем домены по приоритету
        sorted_domains = sorted(priorities.items(), 
                              key=lambda x: x[1]['priority_score'], 
                              reverse=True)
        
        # Генерируем рекомендации
        recommendations = []
        for domain, priority_data in sorted_domains[:10]:  # Топ-10 доменов
            recommendation = self._create_enhanced_recommendation(
                domain, priority_data, user
            )
            if recommendation:
                recommendations.append(recommendation)
        
        return recommendations
    
    def _create_enhanced_recommendation(self, domain: str, 
                                      priority_data: Dict, 
                                      user: User) -> Optional[EnhancedLearningRecommendation]:
        """Создание улучшенной рекомендации для домена"""
        
        # Получаем домен из БД
        big_domain = BIGDomain.query.filter_by(code=domain).first()
        if not big_domain:
            return None
            
        # Подбираем контент на основе IRT способности
        recommended_content = self._smart_content_selection(
            domain, priority_data['theta_estimate'], user
        )
        
        # Оцениваем время обучения
        estimated_time = self._estimate_learning_time(recommended_content)
        
        # Определяем уровень сложности
        difficulty_level = self._get_difficulty_level(
            priority_data['skill_gap'], priority_data['exam_importance']
        )
        
        # Определяем уровень уверенности
        confidence_level = self._get_confidence_level(priority_data['confidence'])
        
        return EnhancedLearningRecommendation(
            domain=domain,
            priority_score=priority_data['priority_score'],
            skill_gap=priority_data['skill_gap'],
            exam_importance=priority_data['exam_importance'],
            urgency_factor=priority_data['urgency_factor'],
            recommended_content=recommended_content,
            estimated_time=estimated_time,
            difficulty_level=difficulty_level,
            confidence_level=confidence_level
        )
    
    def _smart_content_selection(self, domain: str, user_theta: float, 
                               user: User) -> Dict[str, List]:
        """
        Умный подбор контента на основе IRT способности
        
        Args:
            domain: Код домена
            user_theta: IRT способность пользователя
            user: Объект пользователя
            
        Returns:
            Словарь с рекомендованным контентом по типам
        """
        # Оптимальная сложность контента (чуть выше текущего уровня)
        optimal_difficulty = user_theta + 0.3
        
        # Диапазон сложности для подбора
        min_difficulty = max(-3.0, optimal_difficulty - 0.5)
        max_difficulty = min(3.0, optimal_difficulty + 0.5)
        
        recommended_content = {
            'learning_cards': [],
            'adaptive_tests': [],
            'virtual_patients': [],
            'practice_sessions': []
        }
        
        # 1. Learning Cards (теория)
        cards = self._get_learning_cards_for_domain(
            domain, min_difficulty, max_difficulty, limit=5
        )
        recommended_content['learning_cards'] = cards
        
        # 2. Adaptive Tests (практика)
        tests = self._get_adaptive_tests_for_domain(
            domain, optimal_difficulty, limit=3
        )
        recommended_content['adaptive_tests'] = tests
        
        # 3. Virtual Patients (клинические сценарии)
        vp_scenarios = self._get_virtual_patients_for_domain(
            domain, user_theta, limit=2
        )
        recommended_content['virtual_patients'] = vp_scenarios
        
        # 4. Practice Sessions (комбинированные)
        practice = self._get_practice_sessions_for_domain(
            domain, user_theta, limit=3
        )
        recommended_content['practice_sessions'] = practice
        
        return recommended_content
    
    def _get_learning_cards_for_domain(self, domain: str, min_diff: float, 
                                     max_diff: float, limit: int = 5) -> List[Dict]:
        """Получение карточек обучения для домена"""
        # Здесь должна быть логика подбора карточек по IRT параметрам
        # Пока возвращаем заглушку
        return [
            {
                'id': f'card_{domain}_1',
                'title': f'Learning Card for {domain}',
                'difficulty': min_diff + 0.2,
                'estimated_time': 5
            }
        ]
    
    def _get_adaptive_tests_for_domain(self, domain: str, target_theta: float, 
                                     limit: int = 3) -> List[Dict]:
        """Получение адаптивных тестов для домена"""
        return [
            {
                'id': f'test_{domain}_1',
                'title': f'Adaptive Test for {domain}',
                'target_theta': target_theta,
                'estimated_time': 15
            }
        ]
    
    def _get_virtual_patients_for_domain(self, domain: str, user_theta: float, 
                                       limit: int = 2) -> List[Dict]:
        """Получение виртуальных пациентов для домена"""
        return [
            {
                'id': f'vp_{domain}_1',
                'title': f'Virtual Patient for {domain}',
                'difficulty': user_theta + 0.2,
                'estimated_time': 20
            }
        ]
    
    def _get_practice_sessions_for_domain(self, domain: str, user_theta: float, 
                                        limit: int = 3) -> List[Dict]:
        """Получение практических сессий для домена"""
        return [
            {
                'id': f'practice_{domain}_1',
                'title': f'Practice Session for {domain}',
                'difficulty': user_theta + 0.1,
                'estimated_time': 30
            }
        ]
    
    def _estimate_learning_time(self, content: Dict[str, List]) -> int:
        """Оценка времени обучения на основе контента"""
        total_time = 0
        
        for content_type, items in content.items():
            for item in items:
                total_time += item.get('estimated_time', 10)
        
        return total_time
    
    def _get_difficulty_level(self, skill_gap: float, exam_importance: float) -> str:
        """Определение уровня сложности"""
        combined_score = skill_gap * exam_importance
        
        if combined_score > 0.5:
            return 'high'
        elif combined_score > 0.2:
            return 'medium'
        else:
            return 'low'
    
    def _get_confidence_level(self, confidence: float) -> str:
        """Определение уровня уверенности"""
        if confidence > 0.8:
            return 'high'
        elif confidence > 0.6:
            return 'medium'
        else:
            return 'low'
    
    def generate_weekly_plan(self, user_id: int, 
                           recommendations: List[EnhancedLearningRecommendation]) -> Dict:
        """Генерация еженедельного плана обучения"""
        user = User.query.get(user_id)
        if not user:
            return {}
            
        # Получаем план пользователя
        plan = PersonalLearningPlan.query.filter_by(user_id=user_id).first()
        if not plan:
            return {}
        
        weekly_hours = plan.study_hours_per_week or 20.0
        available_minutes = weekly_hours * 60
        
        weekly_plan = {
            'total_recommended_time': 0,
            'daily_plans': {},
            'focus_domains': [],
            'estimated_progress': {}
        }
        
        # Распределяем контент по дням недели
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        daily_minutes = available_minutes / 7
        
        current_day = 0
        current_daily_time = 0
        
        for rec in recommendations[:5]:  # Топ-5 рекомендаций
            if current_daily_time >= daily_minutes:
                current_day += 1
                current_daily_time = 0
                
            if current_day >= len(days):
                break
                
            day = days[current_day]
            if day not in weekly_plan['daily_plans']:
                weekly_plan['daily_plans'][day] = []
            
            # Добавляем контент на день
            daily_content = {
                'domain': rec.domain,
                'priority_score': rec.priority_score,
                'content': rec.recommended_content,
                'estimated_time': min(rec.estimated_time, daily_minutes - current_daily_time)
            }
            
            weekly_plan['daily_plans'][day].append(daily_content)
            current_daily_time += daily_content['estimated_time']
            weekly_plan['total_recommended_time'] += daily_content['estimated_time']
        
        # Фокусные домены
        weekly_plan['focus_domains'] = [rec.domain for rec in recommendations[:3]]
        
        # Оценка прогресса
        weekly_plan['estimated_progress'] = self._estimate_weekly_progress(
            recommendations, weekly_plan['total_recommended_time']
        )
        
        return weekly_plan
    
    def _estimate_weekly_progress(self, recommendations: List[EnhancedLearningRecommendation], 
                                total_time: int) -> Dict:
        """Оценка ожидаемого прогресса за неделю"""
        total_skill_gap = sum(rec.skill_gap for rec in recommendations)
        estimated_improvement = min(total_skill_gap * 0.1, 0.2)  # Максимум 0.2 улучшения за неделю
        
        return {
            'estimated_theta_improvement': estimated_improvement,
            'domains_to_improve': len([r for r in recommendations if r.skill_gap > 0.1]),
            'confidence_in_estimate': 0.7
        } 