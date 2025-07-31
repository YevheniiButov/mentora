#!/usr/bin/env python3
"""
Адаптивный планировщик обучения
Динамически корректирует план на основе прогресса пользователя
"""

from typing import Dict, List, Optional, Tuple
from models import User, PersonalLearningPlan, UserProgress, Lesson, Module, BIGDomain
from extensions import db
from datetime import datetime, timezone, timedelta
import json

class AdaptivePlanner:
    """Адаптивный планировщик обучения"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.user = User.query.get(user_id)
    
    def adapt_learning_plan(self, plan_id: int) -> Dict:
        """Адаптирует план обучения на основе текущего прогресса"""
        
        plan = PersonalLearningPlan.query.get_or_404(plan_id)
        
        # Анализируем текущий прогресс
        progress_analysis = self._analyze_current_progress(plan)
        
        # Определяем области для корректировки
        adjustments = self._identify_adjustments(plan, progress_analysis)
        
        # Применяем корректировки
        updated_plan = self._apply_adjustments(plan, adjustments)
        
        # Обновляем план в базе данных
        self._save_updated_plan(plan, updated_plan)
        
        return {
            'plan_id': plan.id,
            'adjustments_made': adjustments,
            'new_schedule': updated_plan.get('study_schedule'),
            'updated_readiness': updated_plan.get('estimated_readiness'),
            'recommendations': self._generate_recommendations(adjustments)
        }
    
    def _analyze_current_progress(self, plan: PersonalLearningPlan) -> Dict:
        """Анализирует текущий прогресс пользователя"""
        
        # Получаем сессии обучения для плана
        study_sessions = plan.study_sessions.all()
        
        # Анализируем прогресс по сессиям
        total_sessions = len(study_sessions)
        completed_sessions = 0
        total_time_spent = 0
        total_lessons = 0
        completed_lessons = 0
        
        for session in study_sessions:
            if session.status == 'completed':
                completed_sessions += 1
                total_time_spent += session.actual_duration or 0
            
            # Получаем уроки из сессии
            content_ids = session.get_content_ids()
            if content_ids:
                total_lessons += len(content_ids)
                # Проверяем прогресс по урокам
                for lesson_id in content_ids:
                    lesson = Lesson.query.get(lesson_id)
                    if lesson:
                        progress = lesson.get_user_progress(self.user_id)
                        if progress and progress.completed:
                            completed_lessons += 1
        
        # Анализируем прогресс по доменам
        domain_progress = self._analyze_domain_progress(plan, {})
        
        # Рассчитываем общую статистику
        overall_progress = {
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions,
            'total_lessons': total_lessons,
            'completed_lessons': completed_lessons,
            'completion_rate': (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0,
            'total_time_spent': total_time_spent,
            'average_time_per_lesson': (total_time_spent / completed_lessons) if completed_lessons > 0 else 0,
            'domain_progress': domain_progress
        }
        
        return overall_progress
    
    def _extract_lessons_from_schedule(self, study_schedule: Dict) -> List[Lesson]:
        """Извлекает все уроки из расписания плана"""
        
        all_lessons = []
        
        if not study_schedule or 'weekly_schedule' not in study_schedule:
            return all_lessons
        
        for week in study_schedule['weekly_schedule']:
            for daily_session in week.get('daily_sessions', []):
                # Получаем уроки для этой сессии
                session_lessons = self._get_lessons_for_session(daily_session)
                all_lessons.extend(session_lessons)
        
        return list(set(all_lessons))  # Убираем дубликаты
    
    def _get_lessons_for_session(self, daily_session: Dict) -> List[Lesson]:
        """Получает уроки для конкретной сессии"""
        
        lessons = []
        focus_domains = daily_session.get('focus_domains', [])
        
        if focus_domains:
            # Получаем уроки для слабых областей
            for domain_name in focus_domains:
                domain_lessons = self._get_lessons_for_domain(domain_name)
                lessons.extend(domain_lessons)
        else:
            # Общие уроки
            lessons = Lesson.query.limit(5).all()
        
        return lessons[:3]  # Ограничиваем количество уроков на сессию
    
    def _get_lessons_for_domain(self, domain_name: str) -> List[Lesson]:
        """Получает уроки для конкретного домена"""
        
        from utils.content_recommendations import get_smart_recommendations
        return get_smart_recommendations(self.user_id, [domain_name], limit=3)
    
    def _analyze_domain_progress(self, plan: PersonalLearningPlan, lesson_progress: Dict) -> Dict:
        """Анализирует прогресс по доменам"""
        
        weak_domains = plan.get_weak_domains()
        domain_analysis = {}
        
        for domain_name in weak_domains:
            domain = BIGDomain.query.filter_by(name=domain_name).first()
            if not domain:
                continue
            
            # Получаем уроки домена
            domain_lessons = self._get_lessons_for_domain(domain_name)
            
            # Анализируем прогресс по урокам домена
            domain_completed = 0
            domain_time_spent = 0
            domain_scores = []
            
            for lesson in domain_lessons:
                if lesson.id in lesson_progress:
                    progress = lesson_progress[lesson.id]
                    if progress['completed']:
                        domain_completed += 1
                    domain_time_spent += progress['time_spent'] or 0
                    if progress['score']:
                        domain_scores.append(progress['score'])
            
            domain_analysis[domain_name] = {
                'total_lessons': len(domain_lessons),
                'completed_lessons': domain_completed,
                'completion_rate': (domain_completed / len(domain_lessons) * 100) if domain_lessons else 0,
                'time_spent': domain_time_spent,
                'average_score': sum(domain_scores) / len(domain_scores) if domain_scores else 0,
                'needs_attention': domain_completed < len(domain_lessons) * 0.7  # Нужно внимание если < 70%
            }
        
        return domain_analysis
    
    def _identify_adjustments(self, plan: PersonalLearningPlan, progress_analysis: Dict) -> Dict:
        """Определяет необходимые корректировки плана"""
        
        adjustments = {
            'schedule_changes': [],
            'domain_priorities': {},
            'time_adjustments': {},
            'difficulty_adjustments': {}
        }
        
        # Анализируем общий прогресс
        completion_rate = progress_analysis['completion_rate']
        avg_time_per_lesson = progress_analysis['average_time_per_lesson']
        
        # Корректировки на основе скорости изучения
        if completion_rate < 50:
            # Медленный прогресс - упрощаем план
            adjustments['schedule_changes'].append({
                'type': 'simplify',
                'reason': 'Низкий темп изучения',
                'action': 'Уменьшить количество уроков в день'
            })
            adjustments['time_adjustments']['session_duration'] = 'reduce'
        
        elif completion_rate > 80:
            # Быстрый прогресс - ускоряем план
            adjustments['schedule_changes'].append({
                'type': 'accelerate',
                'reason': 'Высокий темп изучения',
                'action': 'Увеличить количество уроков в день'
            })
            adjustments['time_adjustments']['session_duration'] = 'increase'
        
        # Корректировки на основе прогресса по доменам
        domain_progress = progress_analysis['domain_progress']
        for domain_name, progress in domain_progress.items():
            if progress['needs_attention']:
                adjustments['domain_priorities'][domain_name] = 'high'
                adjustments['schedule_changes'].append({
                    'type': 'refocus',
                    'reason': f'Слабая область: {domain_name}',
                    'action': f'Увеличить время на изучение {domain_name}'
                })
            elif progress['completion_rate'] > 90:
                adjustments['domain_priorities'][domain_name] = 'low'
                adjustments['schedule_changes'].append({
                    'type': 'reduce_focus',
                    'reason': f'Сильная область: {domain_name}',
                    'action': f'Уменьшить время на изучение {domain_name}'
                })
        
        # Корректировки на основе времени до экзамена
        if plan.exam_date:
            days_until_exam = (plan.exam_date - datetime.now(timezone.utc).date()).days
            
            if days_until_exam < 30:
                # Экзамен скоро - интенсифицируем
                adjustments['schedule_changes'].append({
                    'type': 'intensify',
                    'reason': 'Экзамен через менее 30 дней',
                    'action': 'Увеличить интенсивность обучения'
                })
                adjustments['time_adjustments']['intensity'] = 'high'
            
            elif days_until_exam > 90:
                # Экзамен далеко - можно расслабиться
                adjustments['schedule_changes'].append({
                    'type': 'relax',
                    'reason': 'Экзамен через более 90 дней',
                    'action': 'Уменьшить интенсивность обучения'
                })
                adjustments['time_adjustments']['intensity'] = 'low'
        
        return adjustments
    
    def _apply_adjustments(self, plan: PersonalLearningPlan, adjustments: Dict) -> Dict:
        """Применяет корректировки к плану"""
        
        # Получаем текущий план
        current_schedule = plan.get_study_schedule()
        updated_schedule = current_schedule.copy() if current_schedule else {}
        
        # Применяем изменения к расписанию
        if 'weekly_schedule' in updated_schedule:
            for week in updated_schedule['weekly_schedule']:
                for daily_session in week['daily_sessions']:
                    self._adjust_daily_session(daily_session, adjustments)
        
        # Обновляем готовность к экзамену
        new_readiness = self._calculate_updated_readiness(plan, adjustments)
        
        return {
            'study_schedule': updated_schedule,
            'estimated_readiness': new_readiness,
            'adjustments_applied': adjustments
        }
    
    def _adjust_daily_session(self, daily_session: Dict, adjustments: Dict):
        """Корректирует ежедневную сессию"""
        
        # Корректируем длительность
        if 'time_adjustments' in adjustments:
            if adjustments['time_adjustments'].get('session_duration') == 'reduce':
                daily_session['duration'] = max(0.5, daily_session['duration'] * 0.8)
            elif adjustments['time_adjustments'].get('session_duration') == 'increase':
                daily_session['duration'] = min(4.0, daily_session['duration'] * 1.2)
        
        # Корректируем фокус на доменах
        if 'domain_priorities' in adjustments:
            focus_domains = daily_session.get('focus_domains', [])
            new_focus = []
            
            for domain in focus_domains:
                priority = adjustments['domain_priorities'].get(domain, 'medium')
                if priority == 'high':
                    # Добавляем домен несколько раз для увеличения фокуса
                    new_focus.extend([domain, domain])
                elif priority == 'low':
                    # Пропускаем домен
                    continue
                else:
                    new_focus.append(domain)
            
            daily_session['focus_domains'] = new_focus[:3]  # Ограничиваем количество
    
    def _calculate_updated_readiness(self, plan: PersonalLearningPlan, adjustments: Dict) -> float:
        """Рассчитывает обновленную готовность к экзамену"""
        
        # Базовая готовность
        base_readiness = plan.estimated_readiness or 0.5
        
        # Корректировки на основе изменений
        readiness_adjustment = 0.0
        
        for change in adjustments.get('schedule_changes', []):
            if change['type'] == 'accelerate':
                readiness_adjustment += 0.1
            elif change['type'] == 'intensify':
                readiness_adjustment += 0.15
            elif change['type'] == 'simplify':
                readiness_adjustment -= 0.05
            elif change['type'] == 'relax':
                readiness_adjustment -= 0.1
        
        # Корректировки на основе приоритетов доменов
        high_priority_domains = sum(1 for p in adjustments.get('domain_priorities', {}).values() if p == 'high')
        readiness_adjustment += high_priority_domains * 0.05
        
        # Ограничиваем готовность в диапазоне 0-1
        new_readiness = max(0.0, min(1.0, base_readiness + readiness_adjustment))
        
        return new_readiness
    
    def _save_updated_plan(self, plan: PersonalLearningPlan, updated_plan: Dict):
        """Сохраняет обновленный план в базе данных"""
        
        # Обновляем расписание
        if 'study_schedule' in updated_plan:
            plan.set_study_schedule(updated_plan['study_schedule'])
        
        # Обновляем готовность
        if 'estimated_readiness' in updated_plan:
            plan.estimated_readiness = updated_plan['estimated_readiness']
        
        # Обновляем время последнего обновления
        plan.last_updated = datetime.now(timezone.utc)
        
        # Сохраняем изменения
        db.session.commit()
    
    def _generate_recommendations(self, adjustments: Dict) -> List[str]:
        """Генерирует рекомендации на основе корректировок"""
        
        recommendations = []
        
        for change in adjustments.get('schedule_changes', []):
            if change['type'] == 'simplify':
                recommendations.append("💡 Рекомендуем уменьшить нагрузку и сосредоточиться на качестве изучения")
            elif change['type'] == 'accelerate':
                recommendations.append("🚀 Отличный прогресс! Можете увеличить темп изучения")
            elif change['type'] == 'intensify':
                recommendations.append("⚡ Экзамен скоро! Увеличьте интенсивность подготовки")
            elif change['type'] == 'refocus':
                recommendations.append(f"🎯 Сосредоточьтесь на изучении: {change['reason']}")
            elif change['type'] == 'reduce_focus':
                recommendations.append(f"✅ {change['reason']} - можете сократить время на эту область")
        
        if not recommendations:
            recommendations.append("📚 Продолжайте обучение в текущем темпе")
        
        return recommendations
    
    def get_plan_insights(self, plan_id: int) -> Dict:
        """Получает аналитику по плану обучения"""
        
        plan = PersonalLearningPlan.query.get_or_404(plan_id)
        progress_analysis = self._analyze_current_progress(plan)
        
        return {
            'plan_id': plan.id,
            'overall_progress': progress_analysis['completion_rate'],
            'time_spent': progress_analysis['total_time_spent'],
            'domain_analysis': progress_analysis['domain_progress'],
            'estimated_readiness': plan.estimated_readiness,
            'days_until_exam': (plan.exam_date - datetime.now(timezone.utc).date()).days if plan.exam_date else None,
            'last_updated': plan.last_updated.isoformat() if plan.last_updated else None
        }

def adapt_user_learning_plan(user_id: int, plan_id: int) -> Dict:
    """Простая функция для адаптации плана обучения"""
    
    planner = AdaptivePlanner(user_id)
    return planner.adapt_learning_plan(plan_id)

def get_plan_insights(user_id: int, plan_id: int) -> Dict:
    """Получает аналитику по плану обучения"""
    
    planner = AdaptivePlanner(user_id)
    return planner.get_plan_insights(plan_id) 