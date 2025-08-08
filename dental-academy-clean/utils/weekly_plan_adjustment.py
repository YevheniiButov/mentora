#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Weekly Plan Adjustment System
Система еженедельной корректировки плана обучения на основе прогресса
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from extensions import db
from models import (
    User, PersonalLearningPlan, UserProgress, UserActivity,
    DiagnosticSession, BIGDomain, StudySession
)

@dataclass
class WeeklyProgressAnalysis:
    """Анализ еженедельного прогресса"""
    planned_hours: float
    actual_hours: float
    completion_rate: float
    domains_studied: List[str]
    domains_mastered: List[str]
    domains_struggling: List[str]
    overall_theta_change: float
    study_efficiency: float
    adherence_score: float

@dataclass
class PlanAdjustment:
    """Корректировка плана"""
    intensity_change: str  # increase, decrease, maintain
    hours_adjustment: float
    focus_domains_change: List[str]
    new_milestones: List[Dict]
    estimated_readiness_change: float
    recommendations: List[str]

class WeeklyPlanAdjustmentSystem:
    """Система еженедельной корректировки плана обучения"""
    
    def __init__(self):
        self.min_completion_rate = 0.7  # Минимальная норма выполнения
        self.max_intensity_increase = 0.3  # Максимальное увеличение интенсивности
        self.theta_improvement_threshold = 0.1  # Порог улучшения θ
        
    def analyze_weekly_progress(self, user_id: int, week_start: datetime = None) -> WeeklyProgressAnalysis:
        """
        Анализ еженедельного прогресса пользователя
        
        Args:
            user_id: ID пользователя
            week_start: Начало недели (по умолчанию - неделю назад)
            
        Returns:
            Анализ прогресса
        """
        if not week_start:
            week_start = datetime.now(timezone.utc) - timedelta(days=7)
            
        week_end = week_start + timedelta(days=7)
        
        # Получаем план пользователя
        plan = PersonalLearningPlan.query.filter_by(user_id=user_id).first()
        if not plan:
            return None
            
        # Получаем активность за неделю
        weekly_activity = self._get_weekly_activity(user_id, week_start, week_end)
        
        # Получаем прогресс по доменам
        domain_progress = self._get_domain_progress(user_id, week_start, week_end)
        
        # Анализируем изменения θ
        theta_change = self._analyze_theta_change(user_id, week_start, week_end)
        
        # Рассчитываем метрики
        planned_hours = plan.study_hours_per_week or 20.0
        actual_hours = weekly_activity.get('total_time_spent', 0) / 60  # Переводим в часы
        
        completion_rate = actual_hours / planned_hours if planned_hours > 0 else 0
        
        # Определяем освоенные и проблемные домены
        domains_mastered = self._identify_mastered_domains(domain_progress)
        domains_struggling = self._identify_struggling_domains(domain_progress)
        
        # Рассчитываем эффективность обучения
        study_efficiency = self._calculate_study_efficiency(weekly_activity, domain_progress)
        
        # Рассчитываем показатель соблюдения плана
        adherence_score = self._calculate_adherence_score(plan, weekly_activity)
        
        return WeeklyProgressAnalysis(
            planned_hours=planned_hours,
            actual_hours=actual_hours,
            completion_rate=completion_rate,
            domains_studied=list(domain_progress.keys()),
            domains_mastered=domains_mastered,
            domains_struggling=domains_struggling,
            overall_theta_change=theta_change,
            study_efficiency=study_efficiency,
            adherence_score=adherence_score
        )
    
    def adjust_learning_plan(self, user_id: int, analysis: WeeklyProgressAnalysis) -> PlanAdjustment:
        """
        Корректировка плана обучения на основе анализа
        
        Args:
            user_id: ID пользователя
            analysis: Анализ еженедельного прогресса
            
        Returns:
            Корректировка плана
        """
        plan = PersonalLearningPlan.query.filter_by(user_id=user_id).first()
        if not plan:
            return None
            
        recommendations = []
        intensity_change = 'maintain'
        hours_adjustment = 0.0
        focus_domains_change = []
        
        # 1. Анализ выполнения плана
        if analysis.completion_rate < self.min_completion_rate:
            # План выполняется плохо
            if analysis.completion_rate < 0.5:
                intensity_change = 'decrease'
                hours_adjustment = -2.0
                recommendations.append("Снижаем интенсивность из-за низкого выполнения плана")
            else:
                recommendations.append("Улучшайте соблюдение плана обучения")
        elif analysis.completion_rate > 1.2:
            # План перевыполняется
            intensity_change = 'increase'
            hours_adjustment = 2.0
            recommendations.append("Увеличиваем интенсивность - план перевыполняется")
        
        # 2. Анализ прогресса по θ
        if analysis.overall_theta_change < self.theta_improvement_threshold:
            # Медленный прогресс
            if analysis.study_efficiency < 0.6:
                recommendations.append("Низкая эффективность обучения - рассмотрите изменение подхода")
            else:
                recommendations.append("Прогресс медленнее ожидаемого - может потребоваться больше времени")
        
        # 3. Анализ освоенных доменов
        if analysis.domains_mastered:
            recommendations.append(f"Отлично! Освоены домены: {', '.join(analysis.domains_mastered)}")
            # Перемещаем освоенные домены в режим поддержания
            focus_domains_change.extend(analysis.domains_mastered)
        
        # 4. Анализ проблемных доменов
        if analysis.domains_struggling:
            recommendations.append(f"Требуют внимания домены: {', '.join(analysis.domains_struggling)}")
            # Добавляем проблемные домены в фокус
            focus_domains_change.extend(analysis.domains_struggling)
        
        # 5. Корректировка интенсивности на основе эффективности
        if analysis.study_efficiency > 0.8 and analysis.completion_rate > 0.9:
            intensity_change = 'increase'
            hours_adjustment += 1.0
            recommendations.append("Высокая эффективность - можно увеличить нагрузку")
        
        # 6. Генерация новых вех
        new_milestones = self._generate_new_milestones(plan, analysis)
        
        # 7. Оценка изменения готовности к экзамену
        estimated_readiness_change = self._estimate_readiness_change(analysis)
        
        return PlanAdjustment(
            intensity_change=intensity_change,
            hours_adjustment=hours_adjustment,
            focus_domains_change=focus_domains_change,
            new_milestones=new_milestones,
            estimated_readiness_change=estimated_readiness_change,
            recommendations=recommendations
        )
    
    def apply_plan_adjustment(self, user_id: int, adjustment: PlanAdjustment) -> bool:
        """
        Применение корректировки к плану пользователя
        
        Args:
            user_id: ID пользователя
            adjustment: Корректировка плана
            
        Returns:
            Успешность применения
        """
        try:
            plan = PersonalLearningPlan.query.filter_by(user_id=user_id).first()
            if not plan:
                return False
            
            # Обновляем часы обучения
            current_hours = plan.study_hours_per_week or 20.0
            new_hours = max(5.0, min(40.0, current_hours + adjustment.hours_adjustment))
            plan.study_hours_per_week = new_hours
            
            # Обновляем интенсивность
            if adjustment.intensity_change == 'increase':
                if plan.intensity == 'light':
                    plan.intensity = 'moderate'
                elif plan.intensity == 'moderate':
                    plan.intensity = 'intensive'
            elif adjustment.intensity_change == 'decrease':
                if plan.intensity == 'intensive':
                    plan.intensity = 'moderate'
                elif plan.intensity == 'moderate':
                    plan.intensity = 'light'
            
            # Обновляем фокусные домены
            current_weak_domains = plan.get_weak_domains()
            
            # Удаляем освоенные домены из слабых
            for domain in adjustment.focus_domains_change:
                if domain in current_weak_domains:
                    current_weak_domains.remove(domain)
            
            plan.set_weak_domains(current_weak_domains)
            
            # Обновляем вехи
            current_milestones = plan.get_milestones()
            current_milestones.extend(adjustment.new_milestones)
            plan.set_milestones(current_milestones)
            
            # Обновляем время последнего обновления
            plan.last_updated = datetime.now(timezone.utc)
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Error applying plan adjustment: {e}")
            return False
    
    def _get_weekly_activity(self, user_id: int, week_start: datetime, 
                           week_end: datetime) -> Dict:
        """Получение активности за неделю"""
        activity = UserActivity.query.filter(
            UserActivity.user_id == user_id,
            UserActivity.activity_date >= week_start.date(),
            UserActivity.activity_date < week_end.date()
        ).all()
        
        total_time = sum(a.time_spent for a in activity)
        total_lessons = sum(a.lessons_completed for a in activity)
        total_tests = sum(a.tests_taken for a in activity)
        
        return {
            'total_time_spent': total_time,
            'lessons_completed': total_lessons,
            'tests_taken': total_tests,
            'active_days': len(activity)
        }
    
    def _get_domain_progress(self, user_id: int, week_start: datetime, 
                           week_end: datetime) -> Dict[str, Dict]:
        """Получение прогресса по доменам за неделю"""
        # Здесь должна быть логика получения прогресса по доменам
        # Пока возвращаем заглушку
        return {
            'THER': {'progress': 0.8, 'questions_answered': 15, 'correct_answers': 12},
            'SURG': {'progress': 0.6, 'questions_answered': 10, 'correct_answers': 6},
            'ORTH': {'progress': 0.9, 'questions_answered': 8, 'correct_answers': 7}
        }
    
    def _analyze_theta_change(self, user_id: int, week_start: datetime, 
                            week_end: datetime) -> float:
        """Анализ изменения θ за неделю"""
        # Получаем диагностические сессии за период
        sessions = DiagnosticSession.query.filter(
            DiagnosticSession.user_id == user_id,
            DiagnosticSession.completed_at >= week_start,
            DiagnosticSession.completed_at < week_end,
            DiagnosticSession.status == 'completed'
        ).order_by(DiagnosticSession.completed_at).all()
        
        if len(sessions) < 2:
            return 0.0
        
        # Рассчитываем изменение θ
        first_theta = sessions[0].current_ability
        last_theta = sessions[-1].current_ability
        
        return last_theta - first_theta
    
    def _identify_mastered_domains(self, domain_progress: Dict[str, Dict]) -> List[str]:
        """Определение освоенных доменов"""
        mastered = []
        for domain, progress in domain_progress.items():
            if progress['progress'] > 0.85 and progress['correct_answers'] / progress['questions_answered'] > 0.8:
                mastered.append(domain)
        return mastered
    
    def _identify_struggling_domains(self, domain_progress: Dict[str, Dict]) -> List[str]:
        """Определение проблемных доменов"""
        struggling = []
        for domain, progress in domain_progress.items():
            if progress['progress'] < 0.6 or progress['correct_answers'] / progress['questions_answered'] < 0.6:
                struggling.append(domain)
        return struggling
    
    def _calculate_study_efficiency(self, activity: Dict, domain_progress: Dict[str, Dict]) -> float:
        """Расчет эффективности обучения"""
        if not activity['total_time_spent']:
            return 0.0
        
        # Простая метрика: количество правильных ответов на час обучения
        total_correct = sum(p['correct_answers'] for p in domain_progress.values())
        hours_studied = activity['total_time_spent'] / 60
        
        return total_correct / hours_studied if hours_studied > 0 else 0.0
    
    def _calculate_adherence_score(self, plan: PersonalLearningPlan, activity: Dict) -> float:
        """Расчет показателя соблюдения плана"""
        planned_hours = plan.study_hours_per_week or 20.0
        actual_hours = activity['total_time_spent'] / 60
        
        if planned_hours == 0:
            return 0.0
        
        adherence = actual_hours / planned_hours
        return min(1.0, adherence)  # Максимум 100%
    
    def _generate_new_milestones(self, plan: PersonalLearningPlan, 
                               analysis: WeeklyProgressAnalysis) -> List[Dict]:
        """Генерация новых вех на основе анализа"""
        milestones = []
        
        # Веха на основе освоенных доменов
        if analysis.domains_mastered:
            milestones.append({
                'type': 'domain_mastered',
                'title': f'Освоены домены: {", ".join(analysis.domains_mastered)}',
                'date': datetime.now(timezone.utc).date(),
                'achievement': True
            })
        
        # Веха на основе прогресса
        if analysis.overall_theta_change > 0.1:
            milestones.append({
                'type': 'theta_improvement',
                'title': f'Улучшение θ на {analysis.overall_theta_change:.2f}',
                'date': datetime.now(timezone.utc).date(),
                'achievement': True
            })
        
        # Веха на основе соблюдения плана
        if analysis.adherence_score > 0.9:
            milestones.append({
                'type': 'plan_adherence',
                'title': 'Отличное соблюдение плана обучения',
                'date': datetime.now(timezone.utc).date(),
                'achievement': True
            })
        
        return milestones
    
    def _estimate_readiness_change(self, analysis: WeeklyProgressAnalysis) -> float:
        """Оценка изменения готовности к экзамену"""
        # Простая модель на основе нескольких факторов
        factors = [
            analysis.completion_rate * 0.3,  # Соблюдение плана
            analysis.study_efficiency * 0.2,  # Эффективность
            analysis.overall_theta_change * 2.0,  # Улучшение θ
            len(analysis.domains_mastered) * 0.05,  # Освоенные домены
            -len(analysis.domains_struggling) * 0.03  # Проблемные домены
        ]
        
        return sum(factors) 