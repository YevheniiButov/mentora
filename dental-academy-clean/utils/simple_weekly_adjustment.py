#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Weekly Adjustment System
Система еженедельной корректировки плана обучения
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta, timezone
from extensions import db
from models import User, UserProgress, PersonalLearningPlan, SpacedRepetitionItem

class SimpleWeeklyAdjustment:
    """Система еженедельной корректировки плана обучения"""
    
    def __init__(self):
        self.progress_threshold = 0.8  # 80% от запланированного прогресса
        self.adjustment_factors = {
            'increase_questions': 1.2,  # Увеличить на 20%
            'decrease_questions': 0.8,  # Уменьшить на 20%
            'maintain': 1.0  # Оставить как есть
        }
    
    def analyze_weekly_progress(self, user_id: int) -> Dict:
        """
        Анализ еженедельного прогресса пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Результат анализа прогресса
        """
        # Получаем план обучения пользователя
        learning_plan = PersonalLearningPlan.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        if not learning_plan:
            return {
                'has_plan': False,
                'message': 'У пользователя нет активного плана обучения'
            }
        
        # Рассчитываем период анализа (последние 7 дней)
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=7)
        
        # Получаем статистику активности
        activity_stats = self._get_activity_statistics(user_id, start_date, end_date)
        
        # Получаем статистику повторений
        repetition_stats = self._get_repetition_statistics(user_id, start_date, end_date)
        
        # Рассчитываем запланированный прогресс
        planned_progress = self._calculate_planned_progress(learning_plan, start_date, end_date)
        
        # Рассчитываем фактический прогресс
        actual_progress = self._calculate_actual_progress(activity_stats, repetition_stats)
        
        # Анализируем прогресс
        progress_analysis = self._analyze_progress(actual_progress, planned_progress)
        
        return {
            'has_plan': True,
            'learning_plan': {
                'id': learning_plan.id,
                'intensity': learning_plan.intensity,
                'study_hours_per_week': learning_plan.study_hours_per_week,
                'overall_progress': learning_plan.overall_progress
            },
            'period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': 7
            },
            'planned_progress': planned_progress,
            'actual_progress': actual_progress,
            'progress_analysis': progress_analysis,
            'activity_stats': activity_stats,
            'repetition_stats': repetition_stats,
            'recommendations': self._generate_recommendations(progress_analysis, activity_stats)
        }
    
    def adjust_plan(self, user_id: int, adjustment_type: str) -> Dict:
        """
        Корректировка плана обучения
        
        Args:
            user_id: ID пользователя
            adjustment_type: Тип корректировки (increase, decrease, maintain)
            
        Returns:
            Результат корректировки
        """
        learning_plan = PersonalLearningPlan.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        if not learning_plan:
            return {
                'success': False,
                'message': 'План обучения не найден'
            }
        
        # Применяем корректировку
        if adjustment_type == 'increase':
            factor = self.adjustment_factors['increase_questions']
            action = 'Увеличено количество вопросов на 20%'
        elif adjustment_type == 'decrease':
            factor = self.adjustment_factors['decrease_questions']
            action = 'Уменьшено количество вопросов на 20%'
        else:
            factor = self.adjustment_factors['maintain']
            action = 'План оставлен без изменений'
        
        # Обновляем план
        learning_plan.study_hours_per_week *= factor
        learning_plan.last_updated = datetime.now(timezone.utc)
        
        # Сохраняем изменения
        db.session.commit()
        
        return {
            'success': True,
            'action': action,
            'new_study_hours': learning_plan.study_hours_per_week,
            'adjustment_factor': factor
        }
    
    def increase_daily_questions(self, user_id: int) -> Dict:
        """
        Увеличение количества ежедневных вопросов
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Результат увеличения
        """
        return self.adjust_plan(user_id, 'increase')
    
    def get_weekly_report(self, user_id: int) -> Dict:
        """
        Получение еженедельного отчета
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Еженедельный отчет
        """
        # Анализируем прогресс
        analysis = self.analyze_weekly_progress(user_id)
        
        if not analysis['has_plan']:
            return analysis
        
        # Получаем статистику по доменам
        domain_stats = self._get_domain_statistics(user_id)
        
        # Формируем отчет
        report = {
            'user_id': user_id,
            'report_date': datetime.now(timezone.utc).isoformat(),
            'period': analysis['period'],
            'summary': {
                'planned_hours': analysis['planned_progress']['total_hours'],
                'actual_hours': analysis['actual_progress']['total_hours'],
                'completion_rate': analysis['progress_analysis']['completion_rate'],
                'accuracy': analysis['repetition_stats']['average_accuracy'],
                'questions_reviewed': analysis['repetition_stats']['total_reviews']
            },
            'progress_analysis': analysis['progress_analysis'],
            'activity_breakdown': analysis['activity_stats'],
            'repetition_breakdown': analysis['repetition_stats'],
            'domain_performance': domain_stats,
            'recommendations': analysis['recommendations'],
            'next_week_goals': self._generate_next_week_goals(analysis)
        }
        
        return report
    
    def _get_activity_statistics(self, user_id: int, start_date: datetime, end_date: datetime) -> Dict:
        """Получение статистики активности"""
        # Получаем прогресс по урокам за период
        progress_items = UserProgress.query.filter(
            UserProgress.user_id == user_id,
            UserProgress.last_accessed >= start_date,
            UserProgress.last_accessed <= end_date
        ).all()
        
        total_lessons = len(progress_items)
        completed_lessons = sum(1 for item in progress_items if item.completed)
        total_time = sum(item.time_spent for item in progress_items)
        
        return {
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'completion_rate': (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0,
            'total_time_minutes': total_time,
            'average_time_per_lesson': (total_time / total_lessons) if total_lessons > 0 else 0
        }
    
    def _get_repetition_statistics(self, user_id: int, start_date: datetime, end_date: datetime) -> Dict:
        """Получение статистики повторений"""
        # Получаем элементы повторений за период
        repetition_items = SpacedRepetitionItem.query.filter(
            SpacedRepetitionItem.user_id == user_id,
            SpacedRepetitionItem.last_review >= start_date,
            SpacedRepetitionItem.last_review <= end_date,
            SpacedRepetitionItem.is_active == True
        ).all()
        
        total_reviews = len(repetition_items)
        correct_answers = sum(1 for item in repetition_items if item.quality >= 3)
        average_accuracy = (correct_answers / total_reviews * 100) if total_reviews > 0 else 0
        
        return {
            'total_reviews': total_reviews,
            'correct_answers': correct_answers,
            'incorrect_answers': total_reviews - correct_answers,
            'average_accuracy': average_accuracy,
            'average_quality': sum(item.quality for item in repetition_items) / total_reviews if total_reviews > 0 else 0
        }
    
    def _calculate_planned_progress(self, learning_plan: PersonalLearningPlan, start_date: datetime, end_date: datetime) -> Dict:
        """Расчет запланированного прогресса"""
        # Рассчитываем запланированные часы на неделю
        planned_hours_per_week = learning_plan.study_hours_per_week
        planned_hours = (planned_hours_per_week / 7) * 7  # Пропорционально дням
        
        # Рассчитываем запланированные вопросы (примерно 2 минуты на вопрос)
        planned_questions = int(planned_hours * 60 / 2)
        
        return {
            'total_hours': planned_hours,
            'total_questions': planned_questions,
            'hours_per_day': planned_hours / 7,
            'questions_per_day': planned_questions / 7
        }
    
    def _calculate_actual_progress(self, activity_stats: Dict, repetition_stats: Dict) -> Dict:
        """Расчет фактического прогресса"""
        total_hours = activity_stats['total_time_minutes'] / 60
        total_questions = repetition_stats['total_reviews']
        
        return {
            'total_hours': total_hours,
            'total_questions': total_questions,
            'hours_per_day': total_hours / 7,
            'questions_per_day': total_questions / 7
        }
    
    def _analyze_progress(self, actual_progress: Dict, planned_progress: Dict) -> Dict:
        """Анализ прогресса"""
        # Рассчитываем процент выполнения
        hours_completion = (actual_progress['total_hours'] / planned_progress['total_hours'] * 100) if planned_progress['total_hours'] > 0 else 0
        questions_completion = (actual_progress['total_questions'] / planned_progress['total_questions'] * 100) if planned_progress['total_questions'] > 0 else 0
        
        # Определяем статус
        if hours_completion >= self.progress_threshold * 100:
            status = 'on_track'
            message = 'Прогресс соответствует плану'
        elif hours_completion >= 0.6 * 100:
            status = 'slightly_behind'
            message = 'Прогресс немного отстает от плана'
        else:
            status = 'behind'
            message = 'Прогресс значительно отстает от плана'
        
        return {
            'completion_rate': hours_completion,
            'questions_completion_rate': questions_completion,
            'status': status,
            'message': message,
            'hours_difference': actual_progress['total_hours'] - planned_progress['total_hours'],
            'questions_difference': actual_progress['total_questions'] - planned_progress['total_questions']
        }
    
    def _get_domain_statistics(self, user_id: int) -> Dict:
        """Получение статистики по доменам"""
        # Получаем статистику повторений по доменам за последние 7 дней
        start_date = datetime.now(timezone.utc) - timedelta(days=7)
        
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
    
    def _generate_recommendations(self, progress_analysis: Dict, activity_stats: Dict) -> List[Dict]:
        """Генерация рекомендаций"""
        recommendations = []
        
        # Рекомендации на основе прогресса
        if progress_analysis['status'] == 'behind':
            recommendations.append({
                'type': 'increase_effort',
                'priority': 'high',
                'message': 'Прогресс значительно отстает от плана',
                'action': 'Увеличьте время обучения на 20%'
            })
        elif progress_analysis['status'] == 'slightly_behind':
            recommendations.append({
                'type': 'moderate_increase',
                'priority': 'medium',
                'message': 'Прогресс немного отстает от плана',
                'action': 'Увеличьте время обучения на 10%'
            })
        
        # Рекомендации на основе активности
        if activity_stats['completion_rate'] < 70:
            recommendations.append({
                'type': 'focus_completion',
                'priority': 'medium',
                'message': 'Низкий процент завершения уроков',
                'action': 'Сфокусируйтесь на завершении начатых уроков'
            })
        
        # Рекомендации на основе времени
        if activity_stats['average_time_per_lesson'] < 5:
            recommendations.append({
                'type': 'increase_engagement',
                'priority': 'low',
                'message': 'Мало времени на урок',
                'action': 'Уделяйте больше времени изучению материала'
            })
        
        return recommendations
    
    def _generate_next_week_goals(self, analysis: Dict) -> Dict:
        """Генерация целей на следующую неделю"""
        if not analysis['has_plan']:
            return {}
        
        current_plan = analysis['learning_plan']
        progress_analysis = analysis['progress_analysis']
        
        # Корректируем цели на основе текущего прогресса
        if progress_analysis['status'] == 'behind':
            adjustment_factor = 1.2  # Увеличиваем на 20%
        elif progress_analysis['status'] == 'slightly_behind':
            adjustment_factor = 1.1  # Увеличиваем на 10%
        else:
            adjustment_factor = 1.0  # Оставляем как есть
        
        adjusted_hours = current_plan['study_hours_per_week'] * adjustment_factor
        adjusted_questions = int(adjusted_hours * 60 / 2)  # 2 минуты на вопрос
        
        return {
            'target_hours': adjusted_hours,
            'target_questions': adjusted_questions,
            'hours_per_day': adjusted_hours / 7,
            'questions_per_day': adjusted_questions / 7,
            'adjustment_factor': adjustment_factor,
            'focus_areas': self._identify_focus_areas(analysis)
        }
    
    def _identify_focus_areas(self, analysis: Dict) -> List[str]:
        """Определение областей для фокусировки"""
        focus_areas = []
        
        # Анализируем статистику по доменам
        domain_stats = analysis.get('domain_statistics', {})
        weak_domains = []
        
        for domain, stats in domain_stats.items():
            if stats['accuracy'] < 70:
                weak_domains.append(domain)
        
        if weak_domains:
            focus_areas.append(f"Слабые домены: {', '.join(weak_domains[:3])}")
        
        # Анализируем активность
        activity_stats = analysis.get('activity_stats', {})
        if activity_stats.get('completion_rate', 0) < 70:
            focus_areas.append("Завершение начатых уроков")
        
        if activity_stats.get('average_time_per_lesson', 0) < 5:
            focus_areas.append("Углубленное изучение материала")
        
        return focus_areas 