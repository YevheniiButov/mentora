#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Student Dashboard
Улучшенный dashboard для студента с predictive analytics и IRT интеграцией
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from extensions import db
from models import (
    User, PersonalLearningPlan, UserProgress, UserActivity,
    DiagnosticSession, BIGDomain, StudySession, VirtualPatientAttempt
)

@dataclass
class DashboardMetrics:
    """Метрики для dashboard"""
    exam_readiness: float  # Процент готовности к экзамену
    weak_domains: List[str]  # Слабые домены
    strong_domains: List[str]  # Сильные домены
    study_streak: int  # Текущая серия дней обучения
    weekly_progress: float  # Прогресс за неделю
    time_to_readiness: int  # Дней до готовности к экзамену
    overall_theta: float  # Общий θ
    confidence_interval: Tuple[float, float]  # Доверительный интервал

@dataclass
class PredictiveAnalytics:
    """Predictive analytics для экзамена"""
    success_probability: float  # Вероятность успешной сдачи
    critical_areas: List[str]  # Критические области для улучшения
    recommended_study_hours: float  # Рекомендуемые часы обучения
    exam_date_prediction: datetime  # Предполагаемая дата готовности
    risk_factors: List[str]  # Факторы риска

class EnhancedStudentDashboard:
    """Улучшенный dashboard для студента"""
    
    def __init__(self):
        self.target_theta = 0.5  # Целевой θ для экзамена
        self.min_confidence = 0.7  # Минимальная уверенность
        
    def generate_student_dashboard(self, user_id: int) -> Dict:
        """
        Генерация полного dashboard для студента
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Полный dashboard с метриками и рекомендациями
        """
        user = User.query.get(user_id)
        if not user:
            return {}
        
        # Получаем план пользователя
        plan = PersonalLearningPlan.query.filter_by(user_id=user_id).first()
        
        # Рассчитываем метрики
        metrics = self._calculate_dashboard_metrics(user_id, plan)
        
        # Получаем predictive analytics
        analytics = self._generate_predictive_analytics(user_id, plan, metrics)
        
        # Получаем сегодняшний план
        today_plan = self._get_daily_content(user_id, plan)
        
        # Получаем еженедельные рекомендации
        weekly_recommendations = self._get_weekly_recommendations(user_id, plan)
        
        # Получаем статистику активности
        activity_stats = self._get_activity_statistics(user_id)
        
        return {
            'user_info': {
                'name': user.get_display_name(),
                'profession': user.get_profession_display(),
                'level': user.level,
                'xp': user.xp
            },
            'metrics': {
                'exam_readiness': metrics.exam_readiness,
                'weak_domains': metrics.weak_domains,
                'strong_domains': metrics.strong_domains,
                'study_streak': metrics.study_streak,
                'weekly_progress': metrics.weekly_progress,
                'time_to_readiness': metrics.time_to_readiness,
                'overall_theta': metrics.overall_theta,
                'confidence_interval': metrics.confidence_interval
            },
            'predictive_analytics': {
                'success_probability': analytics.success_probability,
                'critical_areas': analytics.critical_areas,
                'recommended_study_hours': analytics.recommended_study_hours,
                'exam_date_prediction': analytics.exam_date_prediction.isoformat() if analytics.exam_date_prediction else None,
                'risk_factors': analytics.risk_factors
            },
            'today_plan': today_plan,
            'weekly_recommendations': weekly_recommendations,
            'activity_statistics': activity_stats,
            'quick_actions': self._get_quick_actions(user_id, metrics, analytics)
        }
    
    def _calculate_dashboard_metrics(self, user_id: int, plan: PersonalLearningPlan) -> DashboardMetrics:
        """Расчет метрик для dashboard"""
        
        # Получаем последнюю диагностическую сессию
        latest_session = DiagnosticSession.query.filter_by(
            user_id=user_id, 
            status='completed'
        ).order_by(DiagnosticSession.completed_at.desc()).first()
        
        if not latest_session:
            # Если нет диагностики, используем базовые значения
            return DashboardMetrics(
                exam_readiness=0.0,
                weak_domains=[],
                strong_domains=[],
                study_streak=0,
                weekly_progress=0.0,
                time_to_readiness=999,
                overall_theta=0.0,
                confidence_interval=(0.0, 0.0)
            )
        
        # Рассчитываем готовность к экзамену
        exam_readiness = self._calculate_exam_readiness(latest_session)
        
        # Определяем слабые и сильные домены
        weak_domains, strong_domains = self._identify_domain_strengths(latest_session)
        
        # Получаем серию дней обучения
        study_streak = self._get_study_streak(user_id)
        
        # Рассчитываем недельный прогресс
        weekly_progress = self._calculate_weekly_progress(user_id)
        
        # Оцениваем время до готовности
        time_to_readiness = self._estimate_time_to_readiness(plan, latest_session)
        
        # Получаем общий θ
        overall_theta = latest_session.current_ability
        
        # Рассчитываем доверительный интервал
        confidence_interval = self._calculate_confidence_interval(latest_session)
        
        return DashboardMetrics(
            exam_readiness=exam_readiness,
            weak_domains=weak_domains,
            strong_domains=strong_domains,
            study_streak=study_streak,
            weekly_progress=weekly_progress,
            time_to_readiness=time_to_readiness,
            overall_theta=overall_theta,
            confidence_interval=confidence_interval
        )
    
    def _generate_predictive_analytics(self, user_id: int, plan: PersonalLearningPlan, 
                                     metrics: DashboardMetrics) -> PredictiveAnalytics:
        """Генерация predictive analytics"""
        
        # Рассчитываем вероятность успеха
        success_probability = self._calculate_success_probability(metrics, plan)
        
        # Определяем критические области
        critical_areas = self._identify_critical_areas(metrics, plan)
        
        # Рекомендуемые часы обучения
        recommended_hours = self._calculate_recommended_study_hours(metrics, plan)
        
        # Предполагаемая дата готовности
        exam_date_prediction = self._predict_exam_readiness_date(metrics, plan)
        
        # Факторы риска
        risk_factors = self._identify_risk_factors(metrics, plan)
        
        return PredictiveAnalytics(
            success_probability=success_probability,
            critical_areas=critical_areas,
            recommended_study_hours=recommended_hours,
            exam_date_prediction=exam_date_prediction,
            risk_factors=risk_factors
        )
    
    def _calculate_exam_readiness(self, session: DiagnosticSession) -> float:
        """Расчет готовности к экзамену"""
        # Конвертируем θ в процент готовности
        theta = session.current_ability
        
        # Простая линейная модель: θ = 0.5 соответствует 70% готовности
        if theta >= 0.5:
            readiness = 70 + (theta - 0.5) * 60  # 70-100%
        else:
            readiness = theta * 140  # 0-70%
        
        return max(0.0, min(100.0, readiness))
    
    def _identify_domain_strengths(self, session: DiagnosticSession) -> Tuple[List[str], List[str]]:
        """Определение сильных и слабых доменов"""
        # Получаем доменные способности из сессии
        domain_abilities = session.get_domain_abilities()
        
        weak_domains = []
        strong_domains = []
        
        for domain, theta in domain_abilities.items():
            if theta < 0.0:  # Слабый домен
                weak_domains.append(domain)
            elif theta > 0.3:  # Сильный домен
                strong_domains.append(domain)
        
        return weak_domains[:5], strong_domains[:5]  # Топ-5
    
    def _get_study_streak(self, user_id: int) -> int:
        """Получение текущей серии дней обучения"""
        # Получаем streak пользователя
        streak = User.query.get(user_id).get_or_create_streak()
        return streak.current_streak
    
    def _calculate_weekly_progress(self, user_id: int) -> float:
        """Расчет недельного прогресса"""
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        
        # Получаем активность за неделю
        activity = UserActivity.query.filter(
            UserActivity.user_id == user_id,
            UserActivity.activity_date >= week_ago.date()
        ).all()
        
        if not activity:
            return 0.0
        
        # Рассчитываем прогресс на основе времени обучения
        total_time = sum(a.time_spent for a in activity)
        total_lessons = sum(a.lessons_completed for a in activity)
        
        # Простая метрика: время + уроки
        progress = (total_time / 60) * 0.7 + total_lessons * 0.3
        return min(100.0, progress)
    
    def _estimate_time_to_readiness(self, plan: PersonalLearningPlan, 
                                  session: DiagnosticSession) -> int:
        """Оценка времени до готовности к экзамену"""
        if not plan or not session:
            return 999
        
        current_theta = session.current_ability
        target_theta = plan.target_ability or self.target_theta
        
        if current_theta >= target_theta:
            return 0
        
        # Простая модель: 0.1 улучшения θ за неделю при 20 часах обучения
        theta_gap = target_theta - current_theta
        weeks_needed = theta_gap / 0.1
        
        return int(weeks_needed * 7)  # Дни
    
    def _calculate_confidence_interval(self, session: DiagnosticSession) -> Tuple[float, float]:
        """Расчет доверительного интервала"""
        theta = session.current_ability
        se = session.ability_se or 0.3
        
        # 95% доверительный интервал
        lower = theta - 1.96 * se
        upper = theta + 1.96 * se
        
        return (lower, upper)
    
    def _calculate_success_probability(self, metrics: DashboardMetrics, 
                                     plan: PersonalLearningPlan) -> float:
        """Расчет вероятности успешной сдачи экзамена"""
        # Базовая вероятность на основе готовности
        base_probability = metrics.exam_readiness / 100.0
        
        # Корректировка на основе факторов
        adjustments = []
        
        # Корректировка на основе серии обучения
        if metrics.study_streak > 7:
            adjustments.append(0.1)
        elif metrics.study_streak < 3:
            adjustments.append(-0.1)
        
        # Корректировка на основе слабых доменов
        if len(metrics.weak_domains) > 5:
            adjustments.append(-0.15)
        elif len(metrics.weak_domains) < 2:
            adjustments.append(0.1)
        
        # Корректировка на основе времени до экзамена
        if plan and plan.exam_date:
            days_to_exam = (plan.exam_date - datetime.now(timezone.utc).date()).days
            if days_to_exam < 30:
                adjustments.append(-0.2)
            elif days_to_exam > 90:
                adjustments.append(0.05)
        
        # Применяем корректировки
        final_probability = base_probability + sum(adjustments)
        return max(0.0, min(1.0, final_probability))
    
    def _identify_critical_areas(self, metrics: DashboardMetrics, 
                               plan: PersonalLearningPlan) -> List[str]:
        """Определение критических областей"""
        critical_areas = []
        
        # Добавляем слабые домены
        critical_areas.extend(metrics.weak_domains[:3])
        
        # Добавляем домены с высоким весом в экзамене
        if plan:
            weak_domains = plan.get_weak_domains()
            # Фильтруем по важности в экзамене
            exam_weights = self._get_exam_weights()
            high_weight_weak = [d for d in weak_domains if exam_weights.get(d, 1.0) > 5.0]
            critical_areas.extend(high_weight_weak[:2])
        
        return list(set(critical_areas))[:5]  # Уникальные, максимум 5
    
    def _calculate_recommended_study_hours(self, metrics: DashboardMetrics, 
                                         plan: PersonalLearningPlan) -> float:
        """Расчет рекомендуемых часов обучения"""
        base_hours = plan.study_hours_per_week if plan else 20.0
        
        # Корректировка на основе готовности
        if metrics.exam_readiness < 50:
            base_hours += 5.0  # Больше часов если низкая готовность
        elif metrics.exam_readiness > 80:
            base_hours -= 2.0  # Меньше часов если высокая готовность
        
        # Корректировка на основе времени до готовности
        if metrics.time_to_readiness < 30:
            base_hours += 3.0  # Срочность
        
        return max(10.0, min(40.0, base_hours))
    
    def _predict_exam_readiness_date(self, metrics: DashboardMetrics, 
                                   plan: PersonalLearningPlan) -> Optional[datetime]:
        """Предсказание даты готовности к экзамену"""
        if not plan or metrics.time_to_readiness == 999:
            return None
        
        return datetime.now(timezone.utc) + timedelta(days=metrics.time_to_readiness)
    
    def _identify_risk_factors(self, metrics: DashboardMetrics, 
                             plan: PersonalLearningPlan) -> List[str]:
        """Определение факторов риска"""
        risk_factors = []
        
        # Низкая готовность
        if metrics.exam_readiness < 50:
            risk_factors.append("Низкая готовность к экзамену")
        
        # Много слабых доменов
        if len(metrics.weak_domains) > 5:
            risk_factors.append("Много слабых областей")
        
        # Короткая серия обучения
        if metrics.study_streak < 3:
            risk_factors.append("Нерегулярное обучение")
        
        # Мало времени до экзамена
        if plan and plan.exam_date:
            days_to_exam = (plan.exam_date - datetime.now(timezone.utc).date()).days
            if days_to_exam < 30:
                risk_factors.append("Мало времени до экзамена")
        
        # Низкий недельный прогресс
        if metrics.weekly_progress < 30:
            risk_factors.append("Низкий недельный прогресс")
        
        return risk_factors
    
    def _get_daily_content(self, user_id: int, plan: PersonalLearningPlan) -> Dict:
        """Получение контента на сегодня"""
        # Здесь должна быть логика получения рекомендованного контента
        # Пока возвращаем заглушку
        return {
            'recommended_lessons': [],
            'practice_tests': [],
            'review_items': [],
            'estimated_time': 0
        }
    
    def _get_weekly_recommendations(self, user_id: int, plan: PersonalLearningPlan) -> List[Dict]:
        """Получение еженедельных рекомендаций"""
        # Здесь должна быть логика получения рекомендаций
        # Пока возвращаем заглушку
        return [
            {
                'type': 'focus_domain',
                'title': 'Сфокусируйтесь на терапевтической стоматологии',
                'description': 'Этот домен требует больше внимания',
                'priority': 'high'
            }
        ]
    
    def _get_activity_statistics(self, user_id: int) -> Dict:
        """Получение статистики активности"""
        # Получаем активность за последние 30 дней
        month_ago = datetime.now(timezone.utc) - timedelta(days=30)
        
        activity = UserActivity.query.filter(
            UserActivity.user_id == user_id,
            UserActivity.activity_date >= month_ago.date()
        ).all()
        
        total_time = sum(a.time_spent for a in activity)
        total_lessons = sum(a.lessons_completed for a in activity)
        total_tests = sum(a.tests_taken for a in activity)
        active_days = len(activity)
        
        return {
            'total_time_hours': total_time / 60,
            'lessons_completed': total_lessons,
            'tests_taken': total_tests,
            'active_days': active_days,
            'average_daily_time': total_time / max(1, active_days) / 60
        }
    
    def _get_quick_actions(self, user_id: int, metrics: DashboardMetrics, 
                          analytics: PredictiveAnalytics) -> List[Dict]:
        """Получение быстрых действий"""
        actions = []
        
        # Диагностика если давно не проходили
        if metrics.exam_readiness == 0.0:
            actions.append({
                'type': 'diagnostic',
                'title': 'Пройти диагностику',
                'description': 'Определите ваш текущий уровень',
                'priority': 'high',
                'url': f'/diagnostic/start'
            })
        
        # Повторение если есть слабые домены
        if metrics.weak_domains:
            actions.append({
                'type': 'review',
                'title': 'Повторить слабые области',
                'description': f'Сфокусируйтесь на: {", ".join(metrics.weak_domains[:3])}',
                'priority': 'medium',
                'url': f'/review/weak-domains'
            })
        
        # Практика если низкая готовность
        if metrics.exam_readiness < 60:
            actions.append({
                'type': 'practice',
                'title': 'Практические тесты',
                'description': 'Улучшите навыки решения задач',
                'priority': 'high',
                'url': f'/practice/tests'
            })
        
        return actions
    
    def _get_exam_weights(self) -> Dict[str, float]:
        """Получение весов доменов в экзамене"""
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
        } 