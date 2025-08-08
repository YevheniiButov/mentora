#!/usr/bin/env python3
"""
Система умных рекомендаций контента
Рекомендует уроки на основе слабых областей и прогресса пользователя
"""

from typing import List, Dict, Optional
from models import User, Lesson, Module, Subject, ContentDomainMapping, BIGDomain, UserProgress
from extensions import db
import math

class ContentRecommender:
    """Система рекомендаций контента"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.user = User.query.get(user_id)
    
    def get_recommended_lessons(self, weak_domains: List[str], limit: int = 10) -> List[Lesson]:
        """Получает рекомендованные уроки для слабых областей"""
        
        if not weak_domains:
            return self._get_general_lessons(limit)
        
        recommended_lessons = []
        
        # Получаем домены
        domains = BIGDomain.query.filter(BIGDomain.name.in_(weak_domains)).all()
        
        for domain in domains:
            # Получаем уроки, связанные с доменом
            domain_lessons = self._get_lessons_for_domain(domain.id, limit // len(domains))
            recommended_lessons.extend(domain_lessons)
        
        # Если не нашли достаточно уроков, добавляем общие
        if len(recommended_lessons) < limit:
            additional_lessons = self._get_general_lessons(limit - len(recommended_lessons))
            recommended_lessons.extend(additional_lessons)
        
        # Сортируем по релевантности и сложности
        recommended_lessons = self._rank_lessons(recommended_lessons, weak_domains)
        
        return recommended_lessons[:limit]
    
    def get_personalized_recommendations(self, plan_id: int, limit: int = 10) -> List[Dict]:
        """Получает персонализированные рекомендации на основе плана обучения"""
        
        from models import PersonalLearningPlan
        plan = PersonalLearningPlan.query.get(plan_id)
        
        if not plan:
            return []
        
        weak_domains = plan.get_weak_domains()
        user_progress = self._get_user_progress()
        
        recommendations = []
        
        # Рекомендации по слабым областям
        for domain_name in weak_domains:
            domain_recommendations = self._get_domain_recommendations(
                domain_name, user_progress, limit // len(weak_domains)
            )
            recommendations.extend(domain_recommendations)
        
        # Рекомендации по прогрессу
        progress_recommendations = self._get_progress_based_recommendations(
            user_progress, limit // 2
        )
        recommendations.extend(progress_recommendations)
        
        # Сортируем по приоритету
        recommendations.sort(key=lambda x: x['priority'], reverse=True)
        
        return recommendations[:limit]
    
    def _get_lessons_for_domain(self, domain_id: int, limit: int) -> List[Lesson]:
        """Получает уроки для конкретного домена"""
        
        # Получаем маппинги контента к домену
        mappings = ContentDomainMapping.query.filter(
            ContentDomainMapping.domain_id == domain_id,
            ContentDomainMapping.lesson_id.is_not(None)
        ).order_by(ContentDomainMapping.relevance_score.desc()).limit(limit).all()
        
        lesson_ids = [m.lesson_id for m in mappings if m.lesson_id]
        
        if lesson_ids:
            lessons = Lesson.query.filter(Lesson.id.in_(lesson_ids)).all()
            return lessons
        
        # Fallback: ищем по названию модуля/предмета
        return self._get_lessons_by_name_fallback(domain_id, limit)
    
    def _get_lessons_by_name_fallback(self, domain_id: int, limit: int) -> List[Lesson]:
        """Fallback поиск уроков по названию"""
        
        domain = BIGDomain.query.get(domain_id)
        if not domain:
            return []
        
        # Ищем уроки в модулях, связанных с доменом
        lessons = Lesson.query.join(Module).join(Subject).filter(
            db.or_(
                Subject.name.contains(domain.name),
                Module.title.contains(domain.name)
            )
        ).limit(limit).all()
        
        return lessons
    
    def _get_general_lessons(self, limit: int) -> List[Lesson]:
        """Получает общие уроки"""
        return Lesson.query.limit(limit).all()
    
    def _rank_lessons(self, lessons: List[Lesson], weak_domains: List[str]) -> List[Lesson]:
        """Ранжирует уроки по релевантности"""
        
        def calculate_score(lesson):
            score = 0.0
            
            # Базовый балл
            score += 1.0
            
            # Бонус за связь со слабыми областями
            for domain_name in weak_domains:
                if domain_name.lower() in lesson.title.lower():
                    score += 2.0
                if lesson.module and domain_name.lower() in lesson.module.title.lower():
                    score += 1.5
            
            # Бонус за не изученные уроки
            if not lesson.is_completed_by_user(self.user_id):
                score += 1.0
            
            return score
        
        # Сортируем по баллу
        lessons.sort(key=calculate_score, reverse=True)
        return lessons
    
    def _get_user_progress(self) -> Dict:
        """Получает прогресс пользователя"""
        
        progress = UserProgress.query.filter_by(user_id=self.user_id).all()
        
        completed_lessons = [p.lesson_id for p in progress if p.completed]
        total_time = sum(p.time_spent for p in progress)
        
        return {
            'completed_lessons': completed_lessons,
            'total_time': total_time,
            'total_lessons': len(progress)
        }
    
    def _get_domain_recommendations(self, domain_name: str, user_progress: Dict, limit: int) -> List[Dict]:
        """Получает рекомендации для конкретного домена"""
        
        domain = BIGDomain.query.filter_by(name=domain_name).first()
        if not domain:
            return []
        
        # Получаем уроки домена
        lessons = self._get_lessons_for_domain(domain.id, limit * 2)
        
        recommendations = []
        for lesson in lessons:
            # Пропускаем уже изученные
            if lesson.id in user_progress['completed_lessons']:
                continue
            
            # Рассчитываем приоритет
            priority = self._calculate_lesson_priority(lesson, domain, user_progress)
            
            recommendations.append({
                'type': 'lesson',
                'content': lesson,
                'domain': domain,
                'priority': priority,
                'reason': f'Рекомендуется для изучения {domain_name}'
            })
        
        return recommendations[:limit]
    
    def _get_progress_based_recommendations(self, user_progress: Dict, limit: int) -> List[Dict]:
        """Получает рекомендации на основе прогресса"""
        
        # Находим уроки, которые пользователь начал, но не завершил
        in_progress_lessons = UserProgress.query.filter_by(
            user_id=self.user_id,
            completed=False
        ).filter(UserProgress.time_spent > 0).limit(limit).all()
        
        recommendations = []
        for progress in in_progress_lessons:
            lesson = progress.lesson
            if lesson:
                recommendations.append({
                    'type': 'continue',
                    'content': lesson,
                    'priority': 3.0,  # Высокий приоритет для продолжения
                    'reason': 'Продолжить изучение',
                    'progress': progress
                })
        
        return recommendations
    
    def _calculate_lesson_priority(self, lesson: Lesson, domain: BIGDomain, user_progress: Dict) -> float:
        """Рассчитывает приоритет урока"""
        
        priority = 1.0
        
        # Бонус за релевантность домена
        mapping = ContentDomainMapping.query.filter_by(
            lesson_id=lesson.id,
            domain_id=domain.id
        ).first()
        
        if mapping:
            priority += mapping.relevance_score
        
        # Бонус за сложность (если пользователь готов)
        if user_progress['total_lessons'] > 10:
            priority += 0.5
        
        # Штраф за длинные уроки (если у пользователя мало времени)
        if user_progress['total_time'] < 60:  # Меньше часа изучения
            priority -= 0.3
        
        return priority
    
    def get_next_lesson(self, current_lesson_id: int = None) -> Optional[Lesson]:
        """Получает следующий рекомендуемый урок"""
        
        if current_lesson_id:
            current_lesson = Lesson.query.get(current_lesson_id)
            if current_lesson:
                # Получаем следующий урок в модуле
                next_lesson = self._get_next_in_module(current_lesson)
                if next_lesson:
                    return next_lesson
        
        # Если нет текущего урока или следующего в модуле, рекомендуем новый
        user_progress = self._get_user_progress()
        completed_ids = user_progress['completed_lessons']
        
        # Ищем не изученные уроки
        available_lessons = Lesson.query.filter(
            ~Lesson.id.in_(completed_ids)
        ).limit(10).all()
        
        if available_lessons:
            # Возвращаем первый доступный
            return available_lessons[0]
        
        return None
    
    def _get_next_in_module(self, current_lesson: Lesson) -> Optional[Lesson]:
        """Получает следующий урок в том же модуле"""
        
        if not current_lesson.module:
            return None
        
        # Получаем все уроки модуля
        module_lessons = current_lesson.module.lessons.order_by(Lesson.order).all()
        
        # Находим текущий урок
        current_index = next((i for i, l in enumerate(module_lessons) if l.id == current_lesson.id), -1)
        
        if current_index >= 0 and current_index < len(module_lessons) - 1:
            next_lesson = module_lessons[current_index + 1]
            
            # Проверяем, не изучен ли уже
            if not next_lesson.is_completed_by_user(self.user_id):
                return next_lesson
        
        return None

def get_smart_recommendations(user_id: int, weak_domains: List[str], limit: int = 10) -> List[Lesson]:
    """Простая функция для получения умных рекомендаций"""
    
    recommender = ContentRecommender(user_id)
    return recommender.get_recommended_lessons(weak_domains, limit)

def get_personalized_recommendations(user_id: int, plan_id: int, limit: int = 10) -> List[Dict]:
    """Получает персонализированные рекомендации"""
    
    recommender = ContentRecommender(user_id)
    return recommender.get_personalized_recommendations(plan_id, limit) 