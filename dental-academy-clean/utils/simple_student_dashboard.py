#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple Student Dashboard
Дашборд для студента с прогрессом обучения
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta, timezone
from extensions import db
from models import User, UserProgress, PersonalLearningPlan, SpacedRepetitionItem, Question

class SimpleStudentDashboard:
    """Дашборд для студента с прогрессом обучения"""
    
    def __init__(self):
        self.chart_days = 30  # Количество дней для графиков
        self.dashboard_periods = {
            'today': 1,
            'week': 7,
            'month': 30
        }
    
    def get_dashboard(self, user_id: int) -> Dict:
        """
        Получение основного дашборда
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Данные дашборда
        """
        # Получаем пользователя
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Пользователь не найден'}
        
        # Получаем план обучения
        learning_plan = PersonalLearningPlan.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        # Получаем статистику
        overall_stats = self._get_overall_statistics(user_id)
        recent_activity = self._get_recent_activity(user_id)
        repetition_stats = self._get_repetition_overview(user_id)
        domain_progress = self._get_domain_progress(user_id)
        
        # Формируем дашборд
        dashboard = {
            'user': {
                'id': user.id,
                'name': user.full_name,
                'level': user.level,
                'xp': user.xp
            },
            'learning_plan': {
                'has_plan': learning_plan is not None,
                'overall_progress': learning_plan.overall_progress if learning_plan else 0,
                'target_ability': learning_plan.target_ability if learning_plan else 0,
                'current_ability': learning_plan.current_ability if learning_plan else 0
            },
            'overall_statistics': overall_stats,
            'recent_activity': recent_activity,
            'repetition_overview': repetition_stats,
            'domain_progress': self.get_domain_progress(user_id),
            'quick_actions': self._get_quick_actions(user_id),
            'achievements': self._get_recent_achievements(user_id)
        }
        
        return dashboard
    
    def get_progress_chart(self, user_id: int, days: int = 30) -> Dict:
        """
        Получение данных для графика прогресса
        
        Args:
            user_id: ID пользователя
            days: Количество дней для графика
            
        Returns:
            Данные для графика
        """
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)
        
        # Получаем данные по дням
        daily_data = []
        current_date = start_date
        
        while current_date <= end_date:
            day_start = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            # Статистика за день
            day_stats = self._get_daily_statistics(user_id, day_start, day_end)
            
            daily_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'day': current_date.strftime('%d'),
                'month': current_date.strftime('%b'),
                'lessons_completed': day_stats['lessons_completed'],
                'time_spent': day_stats['time_spent'],
                'questions_reviewed': day_stats['questions_reviewed'],
                'accuracy': day_stats['accuracy'],
                'xp_earned': day_stats['xp_earned']
            })
            
            current_date += timedelta(days=1)
        
        return {
            'period': {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d'),
                'days': days
            },
            'daily_data': daily_data,
            'summary': self._calculate_chart_summary(daily_data)
        }
    
    def get_domain_progress(self, user_id: int) -> Dict:
        """
        Получение прогресса по доменам
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Прогресс по доменам
        """
        # Получаем статистику повторений по доменам
        domain_stats = db.session.query(
            SpacedRepetitionItem.domain,
            db.func.count(SpacedRepetitionItem.id).label('total_reviews'),
            db.func.avg(SpacedRepetitionItem.average_quality).label('avg_quality'),
            db.func.sum(db.case((SpacedRepetitionItem.quality >= 3, 1), else_=0)).label('correct_answers'),
            db.func.max(SpacedRepetitionItem.last_review).label('last_review')
        ).filter(
            SpacedRepetitionItem.user_id == user_id,
            SpacedRepetitionItem.is_active == True,
            SpacedRepetitionItem.domain.isnot(None)
        ).group_by(
            SpacedRepetitionItem.domain
        ).all()
        
        domains = []
        for domain, total, avg_quality, correct, last_review in domain_stats:
            accuracy = (correct / total * 100) if total > 0 else 0
            
            # Определяем статус домена
            if accuracy >= 80:
                status = 'excellent'
            elif accuracy >= 70:
                status = 'good'
            elif accuracy >= 60:
                status = 'fair'
            else:
                status = 'needs_improvement'
            
            domains.append({
                'domain': domain,
                'total_reviews': total,
                'correct_answers': correct,
                'accuracy': accuracy,
                'average_quality': float(avg_quality) if avg_quality else 0,
                'last_review': last_review.isoformat() if last_review else None,
                'status': status,
                'progress_percentage': min(accuracy, 100)  # Для визуализации
            })
        
        # Сортируем по точности (убывание)
        domains.sort(key=lambda x: x['accuracy'], reverse=True)
        
        return {
            'domains': domains,
            'total_domains': len(domains),
            'average_accuracy': sum(d['accuracy'] for d in domains) / len(domains) if domains else 0,
            'strongest_domain': domains[0] if domains else None,
            'weakest_domain': domains[-1] if domains else None
        }
    
    def get_streak_info(self, user_id: int) -> Dict:
        """
        Получение информации о серии обучения
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Информация о серии
        """
        user = User.query.get(user_id)
        if not user:
            return {'error': 'Пользователь не найден'}
        
        streak = user.get_or_create_streak()
        
        return {
            'current_streak': streak.current_streak,
            'longest_streak': streak.longest_streak,
            'last_activity': streak.last_activity_date.isoformat() if streak.last_activity_date else None,
            'is_active_today': self._is_active_today(user_id),
            'next_milestone': self._get_next_streak_milestone(streak.current_streak)
        }
    
    def _get_overall_statistics(self, user_id: int) -> Dict:
        """Получение общей статистики"""
        # Статистика за последние 30 дней
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=30)
        
        # Прогресс по урокам
        progress_items = UserProgress.query.filter(
            UserProgress.user_id == user_id,
            UserProgress.last_accessed >= start_date
        ).all()
        
        total_lessons = len(progress_items)
        completed_lessons = sum(1 for item in progress_items if item.completed)
        total_time = sum(item.time_spent for item in progress_items)
        
        # Статистика повторений
        repetition_items = SpacedRepetitionItem.query.filter(
            SpacedRepetitionItem.user_id == user_id,
            SpacedRepetitionItem.last_review >= start_date,
            SpacedRepetitionItem.is_active == True
        ).all()
        
        total_reviews = len(repetition_items)
        correct_reviews = sum(1 for item in repetition_items if item.quality >= 3)
        average_accuracy = (correct_reviews / total_reviews * 100) if total_reviews > 0 else 0
        
        return {
            'period_days': 30,
            'lessons': {
                'total': total_lessons,
                'completed': completed_lessons,
                'completion_rate': (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
            },
            'time': {
                'total_hours': total_time / 60,
                'average_per_day': (total_time / 60) / 30,
                'total_minutes': total_time
            },
            'repetitions': {
                'total': total_reviews,
                'correct': correct_reviews,
                'accuracy': average_accuracy,
                'average_per_day': total_reviews / 30
            }
        }
    
    def _get_recent_activity(self, user_id: int) -> Dict:
        """Получение недавней активности"""
        # Активность за последние 7 дней
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=7)
        
        # Получаем активность по дням
        daily_activity = []
        current_date = start_date
        
        while current_date <= end_date:
            day_start = current_date.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            day_stats = self._get_daily_statistics(user_id, day_start, day_end)
            
            daily_activity.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'day_name': current_date.strftime('%a'),
                'day_number': current_date.day,
                'lessons_completed': day_stats['lessons_completed'],
                'time_spent': day_stats['time_spent'],
                'questions_reviewed': day_stats['questions_reviewed'],
                'xp_earned': day_stats['xp_earned'],
                'is_active': day_stats['is_active']
            })
            
            current_date += timedelta(days=1)
        
        return {
            'period_days': 7,
            'daily_activity': daily_activity,
            'active_days': sum(1 for day in daily_activity if day['is_active']),
            'total_lessons': sum(day['lessons_completed'] for day in daily_activity),
            'total_time': sum(day['time_spent'] for day in daily_activity),
            'total_questions': sum(day['questions_reviewed'] for day in daily_activity)
        }
    
    def _get_repetition_overview(self, user_id: int) -> Dict:
        """Получение обзора повторений"""
        # Просроченные повторения
        due_reviews = SpacedRepetitionItem.query.filter_by(
            user_id=user_id,
            is_active=True
        ).filter(
            SpacedRepetitionItem.next_review <= datetime.now(timezone.utc)
        ).count()
        
        # Повторения за сегодня
        today = datetime.now(timezone.utc).date()
        today_reviews = SpacedRepetitionItem.query.filter(
            SpacedRepetitionItem.user_id == user_id,
            SpacedRepetitionItem.is_active == True,
            db.func.date(SpacedRepetitionItem.last_review) == today
        ).count()
        
        # Статистика за неделю
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        week_reviews = SpacedRepetitionItem.query.filter(
            SpacedRepetitionItem.user_id == user_id,
            SpacedRepetitionItem.is_active == True,
            SpacedRepetitionItem.last_review >= week_ago
        ).all()
        
        week_correct = sum(1 for item in week_reviews if item.quality >= 3)
        week_accuracy = (week_correct / len(week_reviews) * 100) if week_reviews else 0
        
        return {
            'due_reviews': due_reviews,
            'today_reviews': today_reviews,
            'week_reviews': len(week_reviews),
            'week_accuracy': week_accuracy,
            'priority_level': self._get_priority_level(due_reviews)
        }
    
    def _get_quick_actions(self, user_id: int) -> List[Dict]:
        """Получение быстрых действий"""
        actions = []
        
        # Проверяем просроченные повторения
        due_reviews = SpacedRepetitionItem.query.filter_by(
            user_id=user_id,
            is_active=True
        ).filter(
            SpacedRepetitionItem.next_review <= datetime.now(timezone.utc)
        ).count()
        
        if due_reviews > 0:
            actions.append({
                'type': 'review',
                'title': f'Повторить {due_reviews} вопросов',
                'description': 'У вас есть просроченные повторения',
                'priority': 'high',
                'action': 'start_review'
            })
        
        # Проверяем активность сегодня
        if not self._is_active_today(user_id):
            actions.append({
                'type': 'study',
                'title': 'Начать обучение',
                'description': 'Сегодня еще не было активности',
                'priority': 'medium',
                'action': 'start_study'
            })
        
        # Проверяем прогресс
        learning_plan = PersonalLearningPlan.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        if learning_plan and learning_plan.overall_progress < 50:
            actions.append({
                'type': 'progress',
                'title': 'Продолжить обучение',
                'description': f'Прогресс: {learning_plan.overall_progress:.1f}%',
                'priority': 'medium',
                'action': 'continue_learning'
            })
        
        return actions
    
    def _get_recent_achievements(self, user_id: int) -> List[Dict]:
        """Получение недавних достижений"""
        # Получаем последние 5 достижений
        recent_achievements = db.session.query(
            'UserAchievement', 'Achievement'
        ).join(
            'Achievement'
        ).filter(
            'UserAchievement.user_id == user_id'
        ).order_by(
            'UserAchievement.earned_at.desc()'
        ).limit(5).all()
        
        achievements = []
        for user_achievement, achievement in recent_achievements:
            achievements.append({
                'id': achievement.id,
                'name': achievement.name,
                'description': achievement.description,
                'icon': achievement.icon,
                'category': achievement.category,
                'earned_at': user_achievement.earned_at.isoformat(),
                'badge_color': achievement.badge_color
            })
        
        return achievements
    
    def _get_daily_statistics(self, user_id: int, day_start: datetime, day_end: datetime) -> Dict:
        """Получение статистики за день"""
        # Прогресс по урокам
        progress_items = UserProgress.query.filter(
            UserProgress.user_id == user_id,
            UserProgress.last_accessed >= day_start,
            UserProgress.last_accessed < day_end
        ).all()
        
        lessons_completed = sum(1 for item in progress_items if item.completed)
        time_spent = sum(item.time_spent for item in progress_items)
        
        # Повторения
        repetition_items = SpacedRepetitionItem.query.filter(
            SpacedRepetitionItem.user_id == user_id,
            SpacedRepetitionItem.last_review >= day_start,
            SpacedRepetitionItem.last_review < day_end,
            SpacedRepetitionItem.is_active == True
        ).all()
        
        questions_reviewed = len(repetition_items)
        correct_answers = sum(1 for item in repetition_items if item.quality >= 3)
        accuracy = (correct_answers / questions_reviewed * 100) if questions_reviewed > 0 else 0
        
        # XP (примерный расчет)
        xp_earned = lessons_completed * 10 + questions_reviewed * 2
        
        return {
            'lessons_completed': lessons_completed,
            'time_spent': time_spent,
            'questions_reviewed': questions_reviewed,
            'accuracy': accuracy,
            'xp_earned': xp_earned,
            'is_active': lessons_completed > 0 or questions_reviewed > 0
        }
    
    def _calculate_chart_summary(self, daily_data: List[Dict]) -> Dict:
        """Расчет сводки для графика"""
        total_lessons = sum(day['lessons_completed'] for day in daily_data)
        total_time = sum(day['time_spent'] for day in daily_data)
        total_questions = sum(day['questions_reviewed'] for day in daily_data)
        total_xp = sum(day['xp_earned'] for day in daily_data)
        
        # Средняя точность
        accuracy_values = [day['accuracy'] for day in daily_data if day['questions_reviewed'] > 0]
        average_accuracy = sum(accuracy_values) / len(accuracy_values) if accuracy_values else 0
        
        return {
            'total_lessons': total_lessons,
            'total_time_hours': total_time / 60,
            'total_questions': total_questions,
            'total_xp': total_xp,
            'average_accuracy': average_accuracy,
            'active_days': sum(1 for day in daily_data if day['is_active'])
        }
    
    def _is_active_today(self, user_id: int) -> bool:
        """Проверка активности сегодня"""
        today = datetime.now(timezone.utc).date()
        
        # Проверяем прогресс по урокам
        has_lesson_activity = UserProgress.query.filter(
            UserProgress.user_id == user_id,
            db.func.date(UserProgress.last_accessed) == today
        ).first() is not None
        
        # Проверяем повторения
        has_repetition_activity = SpacedRepetitionItem.query.filter(
            SpacedRepetitionItem.user_id == user_id,
            SpacedRepetitionItem.is_active == True,
            SpacedRepetitionItem.last_review.isnot(None),
            db.func.date(SpacedRepetitionItem.last_review) == today
        ).first() is not None
        
        return has_lesson_activity or has_repetition_activity
    
    def _get_priority_level(self, due_reviews: int) -> str:
        """Определение уровня приоритета"""
        if due_reviews > 20:
            return 'critical'
        elif due_reviews > 10:
            return 'high'
        elif due_reviews > 5:
            return 'medium'
        else:
            return 'low'
    
    def _get_next_streak_milestone(self, current_streak: int) -> Dict:
        """Получение следующей вехи серии"""
        milestones = [7, 14, 30, 60, 100]
        
        for milestone in milestones:
            if current_streak < milestone:
                return {
                    'milestone': milestone,
                    'days_remaining': milestone - current_streak,
                    'achievement': f'{milestone} дней подряд'
                }
        
        return {
            'milestone': None,
            'days_remaining': 0,
            'achievement': 'Все вехи достигнуты!'
        } 