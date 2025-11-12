#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Daily Learning Algorithm Engine
Personal Learning Trainer для MENTORA Platform
"""

import logging
import math
import random
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from sqlalchemy import and_, func

from extensions import db
from models import (
    User, DiagnosticSession, UserProgress, PersonalLearningPlan,
    SpacedRepetitionItem, Question, Lesson, Subject, Module,
    BIGDomain, ContentTopic, DiagnosticResponse, ContentDomainMapping,
    StudySession
)
from utils.simple_spaced_repetition import SimpleSpacedRepetition
from utils.irt_engine import IRTEngine
from utils.irt_spaced_integration import get_irt_spaced_integration
from utils.domain_mapping import convert_abilities_to_new_format, convert_abilities_to_old_format, map_old_to_new_domain, get_domain_name
from utils.diagnostic_data_manager import DiagnosticDataManager

logger = logging.getLogger(__name__)

class DailyLearningAlgorithm:
    """
    Алгоритм генерации ежедневного плана обучения
    Интегрирует IRT, Spaced Repetition и Learning Map
    """
    
    # Пороги для определения сложности
    WEAK_DOMAIN_THRESHOLD = 0.5  # Порог для слабых доменов (IRT theta)
    
    def __init__(self):
        self.srs = SimpleSpacedRepetition()
        self.irt_engine = IRTEngine()
        
        # Константы алгоритма
        self.MIN_TIME_PER_ITEM = 5  # минимальное время на элемент (минуты)
        self.MAX_TIME_PER_ITEM = 20  # максимальное время на элемент (минуты)
        self.REVIEW_TIME_WEIGHT = 1.5  # множитель времени для повторений
        
        # Веса для приоритизации
        self.EXAM_WEIGHT = 0.4
        self.URGENCY_WEIGHT = 0.3
        self.WEAKNESS_WEIGHT = 0.3
        
        self._overdue_reviews = []
    
    def _validate_learning_plan(self, plan: PersonalLearningPlan) -> Dict:
        """
        Валидирует план обучения на наличие необходимых данных
        
        Args:
            plan: PersonalLearningPlan для валидации
            
        Returns:
            Dict с результатом валидации
        """
        if not plan:
            return {
                'valid': False,
                'error': 'Learning plan is None',
                'requires_diagnostic': True,
                'message': 'План обучения не найден'
            }
        
        # Проверяем связь с диагностической сессией
        if not plan.diagnostic_session_id:
            return {
                'valid': False,
                'error': 'No diagnostic session linked to learning plan',
                'requires_diagnostic': True,
                'message': 'План обучения не связан с диагностикой'
            }
        
        # Используем новый метод валидации из PersonalLearningPlan
        is_valid, reason = plan.is_valid_for_daily_tasks()
        if not is_valid:
            return {
                'valid': False,
                'error': reason,
                'requires_diagnostic': True,
                'message': f'План обучения невалиден: {reason}'
            }
        
        # Получаем данные для возврата
        domain_analysis = plan.get_domain_analysis()
        weak_domains = plan.get_weak_domains()
        
        return {
            'valid': True,
            'domain_analysis': domain_analysis,
            'weak_domains': weak_domains
        }
    
    def generate_daily_plan(self, user_id: int, target_minutes: int = 30) -> Dict:
        """
        Генерирует ежедневный план обучения с интеграцией IRT + Spaced Repetition
        
        Args:
            user_id: ID пользователя
            target_minutes: целевое время обучения в минутах
            
        Returns:
            Словарь с ежедневным планом
        """
        try:
            # Получаем данные пользователя
            user = User.query.get(user_id)
            if not user:
                raise ValueError(f"Пользователь {user_id} не найден")
            
            # Проверяем активный план обучения и дату переоценки
            active_plan = PersonalLearningPlan.query.filter_by(
                user_id=user_id,
                status='active'
            ).first()
            
            # КРИТИЧНО: Проверяем, нужно ли обновить план на новый день
            from datetime import date, datetime, timezone
            today = date.today()
            today_start = datetime.combine(today, datetime.min.time()).replace(tzinfo=timezone.utc)
            
            # Удаляем старые незавершенные StudySession из предыдущих дней
            if active_plan:
                old_planned_sessions = StudySession.query.filter(
                    StudySession.learning_plan_id == active_plan.id,
                    StudySession.status == 'planned',
                    StudySession.started_at < today_start
                ).all()
                
                if old_planned_sessions:
                    logger.info(f"User {user_id}: Removing {len(old_planned_sessions)} old planned sessions from previous days")
                    for old_session in old_planned_sessions:
                        db.session.delete(old_session)
                    db.session.commit()
            
            # ПРОВЕРКА ПРОСРОЧЕННОЙ ПЕРЕОЦЕНКИ (ПЕРВЫЙ ПРИОРИТЕТ)
            if active_plan and active_plan.next_diagnostic_date:
                
                if active_plan.next_diagnostic_date < today:
                    days_overdue = (today - active_plan.next_diagnostic_date).days
                    
                    # Блокируем если просрочено более 3 дней
                    if days_overdue > 3:
                        logger.warning(f"User {user_id}: Reassessment overdue by {days_overdue} days, blocking daily plan")
                        return {
                            'success': False,
                            'requires_reassessment': True,
                            'days_overdue': days_overdue,
                            'message': f'Переоценка просрочена на {days_overdue} дней. Пройдите переоценку для продолжения обучения.',
                            'next_diagnostic_date': active_plan.next_diagnostic_date.isoformat()
                        }
                    else:
                        # Предупреждение если просрочено менее 3 дней
                        logger.info(f"User {user_id}: Reassessment overdue by {days_overdue} days, showing warning")
                        reassessment_warning = True
            
            # ВАЛИДАЦИЯ: Проверяем план обучения
            if active_plan:
                validation_result = self._validate_learning_plan(active_plan)
                if not validation_result['valid']:
                    logger.error(f"User {user_id}: Learning plan validation failed: {validation_result['error']}")
                    return {
                        'success': False,
                        'error': validation_result['error'],
                        'requires_diagnostic': validation_result['requires_diagnostic'],
                        'message': validation_result['message']
                    }
            else:
                logger.error(f"User {user_id}: No active learning plan found")
                return {
                    'success': False,
                    'error': 'No active learning plan',
                    'requires_diagnostic': True,
                    'message': 'Не найден активный план обучения. Необходимо пройти диагностику.'
                }
            
            # Проверяем необходимость переоценки, но не блокируем генерацию
            reassessment_warning = False
            if active_plan and active_plan.next_diagnostic_date:
                from datetime import date
                today = date.today()
                if active_plan.next_diagnostic_date <= today:
                    # Прошло 14 дней без переоценки - добавляем предупреждение
                    reassessment_warning = True
                    logger.warning(f"User {user_id} needs reassessment but continuing with existing data")
            
            # КРИТИЧНО: Проверяем, есть ли уже план на сегодня
            if active_plan:
                today_planned_sessions = StudySession.query.filter(
                    StudySession.learning_plan_id == active_plan.id,
                    StudySession.status == 'planned',
                    StudySession.started_at >= today_start
                ).all()
                
                # Если есть запланированные сессии на сегодня, возвращаем существующий план
                if today_planned_sessions:
                    logger.info(f"User {user_id}: Found {len(today_planned_sessions)} planned sessions for today, returning existing plan")
                    # Формируем план из существующих сессий
                    return self._format_existing_plan(today_planned_sessions, user, active_plan, reassessment_warning)
            
            # Используем интегрированную систему IRT + Spaced Repetition
            try:
                irt_spaced_integration = get_irt_spaced_integration()
                integrated_plan = irt_spaced_integration.generate_adaptive_daily_plan(
                    user_id, target_minutes
                )
                
                if not integrated_plan.get('success', True):
                    # Если интегрированная система не смогла создать план, используем старую логику
                    logger.warning(f"Integrated plan failed for user {user_id}, falling back to legacy algorithm")
                    return self._generate_legacy_plan(user_id, target_minutes, active_plan, reassessment_warning)
                
                # Форматируем план для совместимости с существующим API
                formatted_plan = self._format_integrated_plan(integrated_plan, user, active_plan, reassessment_warning)
                
                return formatted_plan
                
            except Exception as e:
                logger.warning(f"Integrated system error for user {user_id}: {e}, falling back to legacy algorithm")
                return self._generate_legacy_plan(user_id, target_minutes, active_plan, reassessment_warning)
            
        except Exception as e:
            logger.error(f"Error in generate_daily_plan for user {user_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'requires_diagnostic': True,
                'message': 'Ошибка при создании ежедневного плана. Необходимо пройти диагностику.'
            }
    
    def _analyze_current_abilities(self, user_id: int) -> Dict[str, float]:
        """Analyze current abilities including progress from study sessions with improved validation"""
        import logging
        logger = logging.getLogger(__name__)
        
        # Get base abilities from learning plan
        active_plan = PersonalLearningPlan.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        if not active_plan:
            logger.warning(f"User {user_id}: No active learning plan found")
            raise ValueError("No active learning plan found. Please complete diagnostic assessment first.")
        
        # Check if user has completed diagnostic session
        diagnostic_session = DiagnosticSession.query.filter_by(
            user_id=user_id,
            status='completed'
        ).order_by(DiagnosticSession.completed_at.desc()).first()
        
        if not diagnostic_session:
            logger.warning(f"User {user_id}: No completed diagnostic session found")
            raise ValueError("No diagnostic assessment completed. Please complete diagnostic assessment first.")
        
        # Check if diagnostic is too old (more than 30 days)
        from datetime import datetime, timezone, timedelta
        # Ensure both datetimes are timezone-aware for comparison
        now_utc = datetime.now(timezone.utc)
        completed_at_utc = diagnostic_session.completed_at
        if completed_at_utc and completed_at_utc.tzinfo is None:
            # If completed_at is naive, assume it's UTC
            completed_at_utc = completed_at_utc.replace(tzinfo=timezone.utc)
        
        if completed_at_utc:
            days_since_diagnostic = (now_utc - completed_at_utc).days
            if days_since_diagnostic > 30:
                logger.warning(f"User {user_id}: Diagnostic is {days_since_diagnostic} days old")
                # Don't raise error, but log warning
        
        # Get base abilities from domain analysis
        domain_analysis = active_plan.get_domain_analysis()
        if not domain_analysis:
            logger.warning(f"User {user_id}: No domain analysis found in learning plan")
            raise ValueError("No domain analysis found. Please complete diagnostic assessment first.")
        
        # Extract base abilities
        base_abilities = {}
        for domain_code, domain_data in domain_analysis.items():
            if isinstance(domain_data, dict) and 'current_ability' in domain_data:
                try:
                    ability = float(domain_data['current_ability'])
                    if -4.0 <= ability <= 4.0:  # Validate range
                        base_abilities[domain_code] = ability
                    else:
                        logger.warning(f"User {user_id}: Invalid ability value for domain {domain_code}: {ability}")
                        base_abilities[domain_code] = 0.0
                except (ValueError, TypeError) as e:
                    logger.warning(f"User {user_id}: Error parsing ability for domain {domain_code}: {e}")
                    base_abilities[domain_code] = 0.0
            else:
                logger.warning(f"User {user_id}: Missing or invalid domain data for {domain_code}")
                base_abilities[domain_code] = 0.0
        
        if not base_abilities:
            logger.error(f"User {user_id}: No valid abilities found in domain analysis")
            raise ValueError("No valid abilities found. Please complete diagnostic assessment first.")
        
        logger.info(f"User {user_id}: Base abilities loaded for {len(base_abilities)} domains")
        
        # Update abilities from recent study sessions
        try:
            updated_abilities = self._update_abilities_from_study_sessions(user_id, base_abilities)
            logger.info(f"User {user_id}: Abilities updated from study sessions")
            return updated_abilities
        except Exception as e:
            logger.warning(f"User {user_id}: Error updating abilities from study sessions: {e}")
            # Return base abilities if study session update fails
            return base_abilities
    
    def _update_abilities_from_study_sessions(self, user_id: int, base_abilities: Dict[str, float]) -> Dict[str, float]:
        """
        Update abilities based on completed study sessions with good results
        
        Args:
            user_id: User ID
            base_abilities: Base abilities from diagnostic
            
        Returns:
            Updated abilities dictionary
        """
        updated_abilities = base_abilities.copy()
        
        try:
            # Get completed study sessions with good accuracy (>70%)
            completed_sessions = StudySession.query.filter(
                and_(
                    StudySession.learning_plan_id == PersonalLearningPlan.query.filter_by(
                        user_id=user_id, status='active'
                    ).first().id,
                    StudySession.status == 'completed',
                    StudySession.correct_answers > 0,
                    StudySession.questions_answered > 0
                )
            ).all()
            
            for session in completed_sessions:
                if session.get_accuracy() > 0.7:  # Good performance threshold
                    # Get domain name from domain_id
                    domain = BIGDomain.query.get(session.domain_id)
                    if domain and domain.code in updated_abilities:
                        # Calculate ability improvement
                        # Formula: new_ability = old_ability + 0.1 * (accuracy - 0.7)
                        accuracy = session.get_accuracy()
                        improvement = 0.1 * (accuracy - 0.7)
                        updated_abilities[domain.code] = min(1.0, updated_abilities[domain.code] + improvement)
            
            # Update the learning plan with new abilities
            active_plan = PersonalLearningPlan.query.filter_by(
                user_id=user_id, status='active'
            ).first()
            
            if active_plan:
                # Update domain analysis with new abilities
                domain_analysis = active_plan.get_domain_analysis()
                if domain_analysis:
                    for domain, ability in updated_abilities.items():
                        if domain in domain_analysis:
                            domain_analysis[domain]['accuracy'] = ability
                    
                    active_plan.set_domain_analysis(domain_analysis)
                    db.session.commit()
                    
                    logger.info(f"Updated abilities for user {user_id} based on study sessions")
            
        except Exception as e:
            logger.error(f"Error updating abilities from study sessions for user {user_id}: {str(e)}")
            # Return base abilities if update fails
            return base_abilities
        
        return updated_abilities
    
    def _identify_weak_domains(self, abilities: Dict[str, float], user_id: int) -> List[str]:
        """Определяет слабые домены на основе способностей с улучшенной валидацией"""
        import logging
        logger = logging.getLogger(__name__)
        
        # Получаем активный план
        active_plan = PersonalLearningPlan.query.filter_by(
            user_id=user_id,
            status='active'
        ).first()
        
        if active_plan:
            # Используем weak_domains из плана
            weak_domains = active_plan.get_weak_domains()
            
            # ВАЛИДАЦИЯ: Проверяем что weak_domains содержат реальные данные
            if weak_domains and len(weak_domains) > 0:
                logger.info(f"User {user_id}: Using {len(weak_domains)} weak domains from learning plan")
                return weak_domains
            else:
                logger.warning(f"User {user_id}: No weak domains found in learning plan")
        
        # ВАЛИДАЦИЯ: Проверяем наличие abilities
        if not abilities:
            logger.error(f"User {user_id}: No abilities data provided")
            raise ValueError("No ability data available. Please complete diagnostic assessment first.")
        
        # Проверяем что abilities содержат валидные данные
        valid_abilities = {}
        for domain, ability in abilities.items():
            if isinstance(ability, (int, float)) and ability is not None:
                valid_abilities[domain] = ability
        
        if not valid_abilities:
            logger.error(f"User {user_id}: No valid ability values found in abilities dict")
            raise ValueError("No valid ability data available. Please complete diagnostic assessment first.")
        
        # ВАЛИДАЦИЯ: Проверяем наличие диагностической сессии
        if active_plan and not active_plan.diagnostic_session_id:
            logger.error(f"User {user_id}: Learning plan has no diagnostic session")
            raise ValueError("Learning plan not linked to diagnostic session. Please complete diagnostic assessment first.")
        
        # Если нет плана или weak_domains пустые, определяем по IRT способностям
        weak_domains = []
        
        # Используем адаптивный порог на основе среднего значения способностей
        if valid_abilities:
            avg_ability = sum(valid_abilities.values()) / len(valid_abilities)
            # Адаптивный порог: 0.5 стандартного отклонения ниже среднего
            threshold = max(0.1, avg_ability - 0.5)  # Минимум 0.1
        else:
            threshold = 0.5  # Fallback порог
        
        for domain, ability in valid_abilities.items():
            if ability < threshold:
                weak_domains.append(domain)
        
        # ВАЛИДАЦИЯ: Проверяем что найдены слабые домены
        if not weak_domains:
            logger.warning(f"User {user_id}: No weak domains identified with threshold {threshold}")
            # Если нет слабых доменов, берем домены с самыми низкими способностями
            sorted_domains = sorted(valid_abilities.items(), key=lambda x: x[1])
            weak_domains = [domain for domain, ability in sorted_domains[:3]]  # Топ-3 самых слабых
        
        logger.info(f"User {user_id}: Identified {len(weak_domains)} weak domains from {len(valid_abilities)} valid abilities (threshold: {threshold:.2f})")
        return weak_domains
    
    def _get_overdue_reviews(self, user_id: int) -> List[Dict]:
        """Получает просроченные повторения"""
        overdue_items = SpacedRepetitionItem.query.filter(
            and_(
                SpacedRepetitionItem.user_id == user_id,
                SpacedRepetitionItem.is_active == True,
                SpacedRepetitionItem.next_review < datetime.now(timezone.utc)
            )
        ).all()
        
        overdue_reviews = []
        for item in overdue_items:
            # Получаем информацию о контенте
            content_info = self._get_content_info(item.question_id, 'question')
            
            overdue_reviews.append({
                'id': item.question_id,
                'type': 'question',
                'title': content_info.get('title', f'Question #{item.question_id}'),
                'domain': item.domain,
                'overdue_days': (datetime.now(timezone.utc) - item.next_review.replace(tzinfo=timezone.utc)).days,
                'ease_factor': item.ease_factor,
                'repetitions': item.repetitions,
                'estimated_time': self._estimate_review_time(item)
            })
        
        # Если нет просроченных повторений, создаем рекомендацию
        if not overdue_reviews:
            overdue_reviews.append({
                'id': 0,
                'type': 'recommendation',
                'title': 'Повторение изученного материала',
                'domain': 'GENERAL',
                'overdue_days': 0,
                'ease_factor': 2.5,
                'repetitions': 0,
                'estimated_time': 5,
                'message': 'Рекомендуется регулярно повторять изученный материал для закрепления знаний'
            })
        
        return overdue_reviews
    
    def _calculate_domain_priorities(self, weak_domains: List[str], 
                                   user_id: int, overdue_reviews: List[Dict]) -> Dict[str, float]:
        """Рассчитывает приоритеты доменов"""
        priorities = {}
        
        # Получаем план обучения пользователя
        learning_plan = PersonalLearningPlan.query.filter_by(
            user_id=user_id, status='active'
        ).first()
        
        exam_date = learning_plan.exam_date if learning_plan else None
        if exam_date:
            # Убеждаемся, что exam_date - это date, а не datetime
            if isinstance(exam_date, datetime):
                exam_date = exam_date.date()
            days_to_exam = (exam_date - datetime.now(timezone.utc).date()).days
        else:
            days_to_exam = 365
        
        # Базовые веса доменов (можно настроить)
        domain_weights = {
            'THER': 0.15, 'SURG': 0.12, 'ORTH': 0.10, 'PEDO': 0.10,
            'PERI': 0.12, 'ENDO': 0.10, 'RAD': 0.08, 'ANAT': 0.08,
            'PHAR': 0.08, 'COMM': 0.07
        }
        
        for domain in domain_weights.keys():
            # Фактор срочности (ближе к экзамену - выше приоритет)
            urgency_factor = max(0.1, 1.0 - (days_to_exam / 365))
            
            # Фактор слабости (слабые домены получают бонус)
            weakness_factor = 1.5 if domain in weak_domains else 1.0
            
            # Фактор просроченных повторений
            overdue_factor = 1.0
            domain_overdue = [r for r in overdue_reviews if r['domain'] == domain]
            if domain_overdue:
                overdue_factor = 1.0 + (len(domain_overdue) * 0.2)
            
            # Итоговый приоритет
            priorities[domain] = (
                domain_weights.get(domain, 0.1) * self.EXAM_WEIGHT +
                urgency_factor * self.URGENCY_WEIGHT +
                weakness_factor * self.WEAKNESS_WEIGHT
            ) * overdue_factor
        
        return priorities
    
    def _allocate_time_by_priority(self, priorities: Dict[str, float], 
                                  total_minutes: int, overdue_reviews: List[Dict]) -> Dict[str, int]:
        """Распределяет время по приоритетам"""
        # Нормализуем приоритеты
        total_priority = sum(priorities.values())
        if total_priority == 0:
            total_priority = 1
        
        # Распределяем время
        time_allocation = {}
        for domain, priority in priorities.items():
            allocated_time = int((priority / total_priority) * total_minutes)
            time_allocation[domain] = max(self.MIN_TIME_PER_ITEM, allocated_time)
        
        # Корректируем общее время
        total_allocated = sum(time_allocation.values())
        if total_allocated > total_minutes:
            # Уменьшаем время пропорционально
            factor = total_minutes / total_allocated
            for domain in time_allocation:
                time_allocation[domain] = max(
                    self.MIN_TIME_PER_ITEM,
                    int(time_allocation[domain] * factor)
                )
        
        return time_allocation
    
    def _select_daily_content(self, time_allocation: Dict, abilities: Dict, 
                            user_id: int, overdue_reviews: List) -> Dict:
        """Выбирает контент для каждого домена на основе IRT способностей"""
        
        daily_content = {
            'theory': [],
            'practice': [],
            'review': []
        }
        
        # Добавляем просроченные повторения
        for review in overdue_reviews:
            daily_content['review'].append(review)
        
        # Получаем активный план обучения для определения weak_domains
        learning_plan = PersonalLearningPlan.query.filter_by(
            user_id=user_id, status='active'
        ).first()
        
        if learning_plan:
            # Используем weak_domains из плана обучения
            weak_domains = learning_plan.get_weak_domains()
            current_ability = learning_plan.current_ability or 0.0
        else:
            # Если нет плана, определяем слабые домены на основе abilities
            weak_domains = self._identify_weak_domains(abilities, user_id)
            current_ability = 0.5
        
        # Приоритизируем слабые домены
        prioritized_domains = []
        
        # Сначала добавляем слабые домены
        for domain in weak_domains:
            if domain in time_allocation:
                prioritized_domains.append(domain)
        
        # Затем добавляем остальные домены
        for domain, allocated_time in time_allocation.items():
            if domain not in prioritized_domains:
                prioritized_domains.append(domain)
        
        # Для каждого домена выбираем контент
        for domain in prioritized_domains:
            allocated_time = time_allocation.get(domain, 0)
            if allocated_time <= 0:
                continue
                
            domain_ability = abilities.get(domain, current_ability)
            
            # Определяем сложность контента относительно current_ability
            difficulty_level = self._get_difficulty_level_relative_to_ability(domain_ability, current_ability)
            
            # Выбираем теорию
            theory_items = self._select_theory_content(
                domain, difficulty_level, allocated_time // 3, user_id
            )
            daily_content['theory'].extend(theory_items)
            
            # Выбираем практику
            practice_items = self._select_practice_content(
                domain, difficulty_level, allocated_time // 3, user_id
            )
            daily_content['practice'].extend(practice_items)
        
        return daily_content
    
    def _get_difficulty_level(self, ability: float) -> str:
        """Определяет уровень сложности на основе способностей"""
        if ability < 0.3:
            return 'easy'
        elif ability < 0.7:
            return 'medium'
        else:
            return 'hard'
    
    def _get_difficulty_level_relative_to_ability(self, domain_ability, current_ability: float) -> str:
        """Определяет сложность контента относительно текущей способности пользователя"""
        # Handle both dict and float domain_ability
        if isinstance(domain_ability, dict):
            domain_ability_value = domain_ability.get('ability_estimate', 0.5)
        else:
            domain_ability_value = float(domain_ability) if domain_ability is not None else 0.5
        
        # Разница между способностью в домене и общей способностью
        ability_diff = domain_ability_value - current_ability
        
        if ability_diff < -0.2:
            # Домен значительно слабее - выбираем легкий контент
            return 'easy'
        elif ability_diff > 0.2:
            # Домен сильнее - выбираем сложный контент
            return 'hard'
        else:
            # Домен примерно на уровне - выбираем средний контент
            return 'medium'
    
    def _select_theory_content(self, domain: str, difficulty: str, time_minutes: int, user_id: int) -> List[Dict]:
        """Select theory content for domain using ContentDomainMapping"""
        # Get domain
        big_domain = BIGDomain.query.filter_by(code=domain).first()
        if not big_domain:
            return []
        
        # Get mapped content
        mappings = ContentDomainMapping.query.filter_by(
            domain_id=big_domain.id
        ).all()
        
        available_lessons = []
        for mapping in mappings:
            if mapping.lesson_id:
                lesson = Lesson.query.get(mapping.lesson_id)
                if lesson and not self._is_lesson_completed(lesson.id, user_id):
                    available_lessons.append(lesson)
        
        # Sort by relevance score and difficulty
        available_lessons.sort(key=lambda l: (
            mapping.relevance_score if mapping else 0.5,
            abs(l.difficulty - self._get_target_difficulty(difficulty))
        ), reverse=True)
        
        # Select lessons that fit in time
        selected_lessons = []
        total_time = 0
        
        for lesson in available_lessons:
            # Используем фиксированное время для урока (15 минут)
            lesson_duration = 15
            if total_time + lesson_duration <= time_minutes:
                selected_lessons.append({
                    'type': 'lesson',
                    'id': lesson.id,
                    'title': lesson.title,
                    'duration': lesson_duration,
                    'difficulty': lesson.difficulty
                })
                total_time += lesson_duration
        
        # Если нет доступных уроков, создаем рекомендацию
        if not selected_lessons:
            selected_lessons.append({
                'type': 'recommendation',
                'id': 0,
                'title': f'Изучите основы {get_domain_name(map_old_to_new_domain(domain))}',
                'duration': 15,
                'difficulty': 'medium',
                'message': 'Рекомендуется пройти диагностику для получения персонализированного контента'
            })
        
        return selected_lessons

    def _is_lesson_completed(self, lesson_id: int, user_id: int) -> bool:
        """Check if lesson is completed by user"""
        progress = UserProgress.query.filter_by(
            user_id=user_id,
            lesson_id=lesson_id,
            completed=True
        ).first()
        return progress is not None
    
    def _get_target_difficulty(self, difficulty: str) -> float:
        """Get target difficulty value for sorting"""
        difficulty_map = {
            'easy': 0.0,
            'medium': 0.5,
            'hard': 1.0
        }
        return difficulty_map.get(difficulty, 0.5)

    def _select_practice_content(self, domain: str, difficulty: str, 
                               time_minutes: int, user_id: int) -> List[Dict]:
        """
        Выбирает практический контент для домена с учетом IRT сложности и уровня знаний пользователя.
        
        Args:
            domain: Код домена (например, 'THER')
            difficulty: Уровень сложности ('easy', 'medium', 'hard')
            time_minutes: Доступное время в минутах
            user_id: ID пользователя
        
        Returns:
            Список словарей с информацией о вопросах
        """
        try:
            # 1. Получаем текущую способность пользователя (theta)
            user_ability = 0.0  # По умолчанию средний уровень
            
            # Пытаемся получить способность из последней диагностической сессии
            last_session = DiagnosticSession.query.filter_by(
                user_id=user_id,
                status='completed'
            ).order_by(DiagnosticSession.completed_at.desc()).first()
            
            if last_session:
                user_ability = last_session.current_ability or 0.0
            else:
                # Если нет диагностики, пытаемся оценить по ответам на вопросы
                responses = DiagnosticResponse.query.filter_by(user_id=user_id).all()
                if responses:
                    try:
                        user_ability, _ = self.irt_engine.estimate_ability([
                            {
                                'question_id': r.question_id,
                                'is_correct': r.is_correct,
                                'irt_params': r.question.irt_parameters.get_parameters() if r.question.irt_parameters else None
                            }
                            for r in responses if r.question and r.question.irt_parameters
                        ])
                    except Exception as e:
                        logger.warning(f"Не удалось оценить способность пользователя: {e}")
                        user_ability = 0.0

            # 2. Находим домен по коду (с маппингом старых кодов)
            from utils.domain_mapping import map_old_to_new_domain
            mapped_domain = map_old_to_new_domain(domain)
            big_domain = BIGDomain.query.filter_by(code=mapped_domain).first()
            if not big_domain:
                logger.warning(f"Домен {domain} (маппинг: {mapped_domain}) не найден в базе данных")
                return []

            # 3. Находим вопросы для домена
            questions_in_domain = Question.query.filter(
                Question.big_domain_id == big_domain.id
            ).all()
            
            # Если нет вопросов по big_domain_id, ищем по строковому полю domain
            if not questions_in_domain:
                questions_in_domain = Question.query.filter(
                    Question.domain == domain
                ).all()
            
            if not questions_in_domain:
                logger.warning(f"Не найдено вопросов для домена {domain}")
                return []

            # 4. Фильтруем вопросы с IRT параметрами
            questions_with_irt = []
            questions_without_irt = []
            
            for question in questions_in_domain:
                if question.irt_parameters and question.irt_parameters.difficulty is not None:
                    questions_with_irt.append(question)
                else:
                    questions_without_irt.append(question)

            # 5. Выбираем вопросы с учетом сложности и времени
            selected_items = []
            max_items = min(len(questions_in_domain), time_minutes // 3)  # 3 минуты на вопрос
            
            if questions_with_irt:
                # Сортируем вопросы по близости IRT сложности к способности пользователя
                sorted_questions = sorted(
                    questions_with_irt,
                    key=lambda q: abs(q.irt_parameters.difficulty - user_ability)
                )
                
                # Выбираем вопросы в зависимости от требуемой сложности
                if difficulty == 'easy':
                    # Выбираем вопросы с IRT сложностью ниже способности пользователя
                    selected_questions = [
                        q for q in sorted_questions 
                        if q.irt_parameters.difficulty <= user_ability
                    ][:max_items]
                elif difficulty == 'hard':
                    # Выбираем вопросы с IRT сложностью выше способности пользователя
                    selected_questions = [
                        q for q in sorted_questions 
                        if q.irt_parameters.difficulty > user_ability
                    ][:max_items]
                else:  # medium
                    # Выбираем вопросы с IRT сложностью близкой к способности пользователя
                    selected_questions = sorted_questions[:max_items]
                
                # Если не хватает вопросов с IRT, добавляем остальные
                if len(selected_questions) < max_items:
                    remaining_irt = [q for q in questions_with_irt if q not in selected_questions]
                    if remaining_irt:
                        additional_needed = max_items - len(selected_questions)
                        selected_questions.extend(random.sample(remaining_irt, min(additional_needed, len(remaining_irt))))
                
                # Добавляем вопросы без IRT параметров, если нужно
                if len(selected_questions) < max_items and questions_without_irt:
                    additional_needed = max_items - len(selected_questions)
                    selected_questions.extend(random.sample(questions_without_irt, min(additional_needed, len(questions_without_irt))))
                    
            else:
                # Если нет вопросов с IRT, используем все доступные
                selected_questions = random.sample(questions_in_domain, min(max_items, len(questions_in_domain)))

            # 6. Исключаем недавно решенные вопросы
            recent_question_ids = set([
                item.question_id for item in SpacedRepetitionItem.query.filter(
                and_(
                    SpacedRepetitionItem.user_id == user_id,
                    SpacedRepetitionItem.last_review >= datetime.now(timezone.utc) - timedelta(days=3)
                )
                ).all()
            ])
            
            final_questions = [
                q for q in selected_questions 
                if q.id not in recent_question_ids
            ]
            
            # Если все вопросы недавно решались, берем случайные
            if not final_questions and selected_questions:
                final_questions = random.sample(selected_questions, min(3, len(selected_questions)))

            # 7. Формируем результат
            for question in final_questions:
                # Извлекаем название из текста вопроса
                title = question.text
                if title.startswith('KLINISCHE CASUS:'):
                    title = title.replace('KLINISCHE CASUS:', '').strip()
                    if len(title) > 60:
                        title = title[:60] + '...'
                elif len(title) > 50:
                    title = title[:50] + '...'
                
                # Оцениваем время на основе сложности
                if question.irt_parameters and question.irt_parameters.difficulty is not None:
                    irt_diff = abs(question.irt_parameters.difficulty - user_ability)
                    estimated_time = max(2, min(8, int(3 + irt_diff * 2)))
                else:
                    estimated_time = 3
                
                selected_items.append({
                    'id': question.id,
                    'type': 'question',
                    'title': title,
                    'question_text': question.text[:100] + '...' if len(question.text) > 100 else question.text,
                    'domain': domain,
                    'difficulty': self._get_question_difficulty(question),
                    'estimated_time': estimated_time,
                    'options': question.options[:2] if question.options else [],
                    'irt_difficulty': question.irt_parameters.difficulty if question.irt_parameters else None
                })
            
            # Если нет выбранных элементов, создаем рекомендацию
            if not selected_items:
                selected_items.append({
                    'id': 0,
                    'type': 'recommendation',
                    'title': f'Практика по {get_domain_name(map_old_to_new_domain(domain))}',
                    'question_text': f'Рекомендуется пройти диагностику для получения персонализированных практических заданий по теме {get_domain_name(map_old_to_new_domain(domain))}',
                    'domain': domain,
                    'difficulty': 'medium',
                    'estimated_time': 5,
                    'message': 'Пройти диагностику для получения персонализированного контента'
                })
            
            return selected_items
            
        except Exception as e:
            logger.error(f"Ошибка при выборе практического контента для домена {domain}: {e}")
            # Возвращаем рекомендацию вместо резервного контента
            return [{
                'id': 0,
                'type': 'recommendation',
                'title': f'Практика по {get_domain_name(map_old_to_new_domain(domain))}',
                'question_text': f'Рекомендуется пройти диагностику для получения персонализированных практических заданий',
                'domain': domain,
                'difficulty': 'medium',
                'estimated_time': 5,
                'options': []
            }]
    
    def _get_lesson_difficulty(self, lesson: Lesson) -> int:
        """
        Получает сложность урока в процентах (0-100)
        
        Args:
            lesson: Объект урока
            
        Returns:
            Сложность в процентах
        """
        # Используем поле difficulty из модели Lesson
        if hasattr(lesson, 'difficulty') and lesson.difficulty is not None:
            # Конвертируем IRT difficulty (-4 до 4) в проценты (0-100)
            irt_diff = lesson.difficulty
            if irt_diff <= -2:
                return 20  # Очень легко
            elif irt_diff <= -1:
                return 35  # Легко
            elif irt_diff <= 0:
                return 50  # Средне
            elif irt_diff <= 1:
                return 65  # Сложно
            elif irt_diff <= 2:
                return 80  # Очень сложно
            else:
                return 95  # Эксперт
        else:
            # Если нет IRT сложности, используем порядковый номер
            return min(100, max(20, lesson.order * 5))
    
    def _get_question_difficulty(self, question: Question) -> int:
        """
        Получает сложность вопроса в процентах (0-100)
        
        Args:
            question: Объект вопроса
            
        Returns:
            Сложность в процентах
        """
        # Приоритет: IRT параметры > difficulty_level > дефолт
        if hasattr(question, 'irt_parameters') and question.irt_parameters:
            irt_diff = question.irt_parameters.difficulty
            if irt_diff is not None:
                # Конвертируем IRT difficulty (-4 до 4) в проценты (0-100)
                if irt_diff <= -2:
                    return 20  # Очень легко
                elif irt_diff <= -1:
                    return 35  # Легко
                elif irt_diff <= 0:
                    return 50  # Средне
                elif irt_diff <= 1:
                    return 65  # Сложно
                elif irt_diff <= 2:
                    return 80  # Очень сложно
                else:
                    return 95  # Эксперт
        
        # Если нет IRT параметров, используем difficulty_level
        if hasattr(question, 'difficulty_level') and question.difficulty_level is not None:
            diff_level = question.difficulty_level
            if diff_level <= 1:
                return 25  # Легко
            elif diff_level <= 2:
                return 40  # Средне-легко
            elif diff_level <= 3:
                return 55  # Средне
            elif diff_level <= 4:
                return 70  # Средне-сложно
            else:
                return 85  # Сложно
        
        # Дефолтное значение
        return 50
    
    def _estimate_review_time(self, item: SpacedRepetitionItem) -> int:
        """Оценивает время на повторение"""
        base_time = 2  # базовое время в минутах
        if item.repetitions > 5:
            return base_time  # хорошо изученные элементы
        elif item.repetitions > 2:
            return base_time + 1
        else:
            return base_time + 2
    
    def _get_content_info(self, content_id: int, content_type: str) -> Dict:
        """Получает информацию о контенте"""
        if content_type == 'question':
            question = Question.query.get(content_id)
            if question:
                # Извлекаем название из текста вопроса
                title = question.text
                if title.startswith('KLINISCHE CASUS:'):
                    # Для клинических случаев берем описание пациента
                    title = title.replace('KLINISCHE CASUS:', '').strip()
                    if len(title) > 60:
                        title = title[:60] + '...'
                elif len(title) > 50:
                    title = title[:50] + '...'
                
                return {
                    'title': title,
                    'text': question.text[:100] + '...' if len(question.text) > 100 else question.text
                }
        elif content_type == 'lesson':
            lesson = Lesson.query.get(content_id)
            if lesson:
                return {
                    'title': lesson.title,
                    'text': lesson.content[:100] + '...' if lesson.content and len(lesson.content) > 100 else (lesson.content or '')
                }
        
        return {'title': f'{content_type.title()} #{content_id}'}
    
    def _format_for_learning_map(self, daily_content: Dict, user: User) -> Dict:
        """Форматирует контент для отображения в Learning Map"""
        
        theory_items = []
        practice_items = []
        review_items = []
        total_time = 0
        
        # Обрабатываем контент по доменам
        for domain, content in daily_content.items():
            if isinstance(content, dict) and 'lessons' in content:
                # Новый формат с уроками
                lessons = content.get('lessons', [])
                allocated_time = content.get('allocated_time', 0)
                
                # Распределяем уроки по секциям
                for i, lesson in enumerate(lessons):
                    item = {
                        'id': lesson.id,
                        'title': lesson.title,
                        'domain': domain,
                        'estimated_time': min(allocated_time / max(len(lessons), 1), 15),  # минут на урок
                        'difficulty': lesson.difficulty if hasattr(lesson, 'difficulty') else 0.0,
                        'type': 'lesson'
                    }
                    
                    # Распределяем по типам активности
                    if i == 0:
                        # Первый урок в домене - теория
                        theory_items.append(item)
                    elif i < len(lessons) - 1:
                        # Средние уроки - практика
                        practice_items.append(item)
                    else:
                        # Последний урок - повторение
                        review_items.append(item)
                
                total_time += allocated_time
            else:
                # Старый формат с готовыми секциями
                if 'theory' in daily_content:
                    theory_items.extend(daily_content.get('theory', []))
                if 'practice' in daily_content:
                    practice_items.extend(daily_content.get('practice', []))
                if 'review' in daily_content:
                    review_items.extend(daily_content.get('review', []))
                
                # Подсчитываем общее время
                for section in ['theory', 'practice', 'review']:
                    if section in daily_content:
                        total_time += sum(item.get('estimated_time', 0) for item in daily_content[section])
        
        # Добавляем просроченные повторения в секцию review
        overdue_reviews = getattr(self, '_overdue_reviews', [])
        for review in overdue_reviews[:3]:  # Максимум 3 повторения
            if review.get('type') == 'recommendation':
                review_items.append({
                    'id': review.get('id', 0),
                    'title': review.get('title', 'Рекомендация'),
                    'domain': review.get('domain', 'GENERAL'),
                    'estimated_time': review.get('estimated_time', 5),
                    'difficulty': 'medium',
                    'type': 'recommendation',
                    'message': review.get('message', '')
                })
            else:
                review_items.append({
                    'id': review.get('id', 0),
                    'title': f"Повторение: {review.get('title', 'Элемент')}",
                    'domain': review.get('domain_code', 'GENERAL'),
                    'estimated_time': 10,
                    'difficulty': 0.0,
                    'type': 'review'
                })
        
        # Формируем финальную структуру
        formatted_plan = {
            'total_time': int(total_time),
            'sections': {
                'theory': {
                    'title': 'Теория',
                    'items': theory_items,
                    'total_items': len(theory_items),
                    'estimated_time': sum(item.get('estimated_time', 0) for item in theory_items)
                },
                'practice': {
                    'title': 'Практика',
                    'items': practice_items,
                    'total_items': len(practice_items),
                    'estimated_time': sum(item.get('estimated_time', 0) for item in practice_items)
                },
                'review': {
                    'title': 'Повторение',
                    'items': review_items,
                    'total_items': len(review_items),
                    'estimated_time': sum(item.get('estimated_time', 0) for item in review_items)
                }
            },
            'theory': {  # Для обратной совместимости
                'items': theory_items
            },
            'practice': {
                'items': practice_items
            },
            'review': {
                'items': review_items
            }
        }
        
        return formatted_plan 
    
    def _create_study_sessions(self, daily_content: Dict, user: User, active_plan: PersonalLearningPlan) -> List[StudySession]:
        """
        Create StudySession records for each task in the daily plan
        
        Args:
            daily_content: Daily content dictionary
            user: User object
            active_plan: Active learning plan
            
        Returns:
            List of created StudySession objects
        """
        study_sessions = []
        
        try:
            # Обрабатываем каждый домен
            for domain_code, domain_data in daily_content.items():
                if not isinstance(domain_data, dict):
                    continue
                
                # Обрабатываем теоретический контент
                theory_items = domain_data.get('theory', {}).get('items', [])
                if isinstance(theory_items, list):
                    for item in theory_items:
                        if isinstance(item, dict) and 'id' in item:
                            from datetime import datetime, timezone
                            session = StudySession(
                                learning_plan_id=active_plan.id,
                                session_type='theory',
                                domain_id=self._get_domain_id_by_name(domain_code),
                                content_ids=self._serialize_content_ids([item['id']], item.get('type', 'lesson')),
                                planned_duration=item.get('duration', 15),
                                difficulty_level=float(item.get('difficulty', 0.0)) if isinstance(item.get('difficulty'), (int, float)) else 0.0,
                                status='planned',
                                started_at=datetime.now(timezone.utc)  # Используем started_at как created_at для проверки даты
                            )
                            db.session.add(session)
                            study_sessions.append(session)
                
                # Обрабатываем практический контент
                practice_items = domain_data.get('practice', {}).get('items', [])
                if isinstance(practice_items, list):
                    for item in practice_items:
                        if isinstance(item, dict) and 'id' in item:
                            from datetime import datetime, timezone
                            session = StudySession(
                                learning_plan_id=active_plan.id,
                                session_type='practice',
                                domain_id=self._get_domain_id_by_name(domain_code),
                                content_ids=self._serialize_content_ids([item['id']], item.get('type', 'question')),
                                planned_duration=item.get('duration', 15),
                                difficulty_level=float(item.get('difficulty', 0.0)) if isinstance(item.get('difficulty'), (int, float)) else 0.0,
                                status='planned',
                                started_at=datetime.now(timezone.utc)  # Используем started_at как created_at для проверки даты
                            )
                            db.session.add(session)
                            study_sessions.append(session)
                
                # Обрабатываем повторения
                review_items = domain_data.get('review', {}).get('items', [])
                if isinstance(review_items, list):
                    for item in review_items:
                        if isinstance(item, dict) and 'id' in item:
                            from datetime import datetime, timezone
                            session = StudySession(
                                learning_plan_id=active_plan.id,
                                session_type='review',
                                domain_id=self._get_domain_id_by_name(domain_code),
                                content_ids=self._serialize_content_ids([item['id']], item.get('type', 'lesson')),
                                planned_duration=item.get('duration', 10),
                                difficulty_level=float(item.get('difficulty', 0.0)) if isinstance(item.get('difficulty'), (int, float)) else 0.0,
                                status='planned',
                                started_at=datetime.now(timezone.utc)  # Используем started_at как created_at для проверки даты
                            )
                            db.session.add(session)
                            study_sessions.append(session)
            
            # Commit all sessions
            if study_sessions:
                db.session.commit()
                logger.info(f"Created {len(study_sessions)} study sessions for user {user.id}")
            else:
                logger.warning(f"No study sessions created for user {user.id}")
            
        except Exception as e:
            # Rollback on error
            db.session.rollback()
            logger.error(f"Error creating study sessions for user {user.id}: {str(e)}")
            raise
        
        return study_sessions
    
    def _get_adaptive_learning_path(self, active_plan: PersonalLearningPlan) -> Dict:
        """
        Получает адаптивный путь обучения для пользователя
        
        Args:
            active_plan: Активный план обучения
            
        Returns:
            Словарь с адаптивным путем
        """
        try:
            if not active_plan:
                return {'success': False, 'error': 'Нет активного плана обучения'}
            
            # Получаем адаптивный путь через план обучения
            adaptive_path = active_plan.get_adaptive_learning_path()
            
            if not adaptive_path.get('success', False):
                logger.warning(f"Не удалось получить адаптивный путь для пользователя {active_plan.user_id}")
                return {
                    'success': False,
                    'error': adaptive_path.get('error', 'Неизвестная ошибка'),
                    'path_id': 'basic_path',
                    'path_name': 'Базовый путь обучения',
                    'modules': []
                }
            
            return adaptive_path
            
        except Exception as e:
            logger.error(f"Ошибка получения адаптивного пути: {e}")
            return {
                'success': False,
                'error': str(e),
                'path_id': 'basic_path',
                'path_name': 'Базовый путь обучения',
                'modules': []
            }
    
    def _select_daily_content_with_adaptive_path(self, time_allocation: Dict, abilities: Dict, 
                                               user_id: int, overdue_reviews: List, 
                                               adaptive_path: Dict) -> Dict:
        """
        Выбирает контент для каждого домена с учетом адаптивного пути обучения
        """
        try:
            # Если есть успешный адаптивный путь, используем его модули
            if adaptive_path.get('success', False) and adaptive_path.get('modules'):
                return self._select_content_from_adaptive_path(
                    adaptive_path, time_allocation, abilities, user_id, overdue_reviews
                )
            else:
                # Если нет адаптивного пути, используем стандартный алгоритм
                return self._select_daily_content(
                    time_allocation, abilities, user_id, overdue_reviews
                )
                
        except Exception as e:
            logger.error(f"Ошибка выбора контента с адаптивным путем: {e}")
            # Возвращаем стандартный контент в случае ошибки
            return self._select_daily_content(
                time_allocation, abilities, user_id, overdue_reviews
            )
    
    def _select_content_from_adaptive_path(self, adaptive_path: Dict, time_allocation: Dict,
                                         abilities: Dict, user_id: int, 
                                         overdue_reviews: List) -> Dict:
        """
        Выбирает контент из адаптивного пути обучения
        """
        daily_content = {
            'theory': [],
            'practice': [],
            'review': []
        }
        
        # Добавляем просроченные повторения
        for review in overdue_reviews:
            daily_content['review'].append(review)
        
        # Получаем модули из адаптивного пути
        modules = adaptive_path.get('modules', [])
        
        # Распределяем время между модулями
        total_allocated_time = sum(time_allocation.values())
        if total_allocated_time == 0:
            total_allocated_time = 30  # Дефолтное время
        
        # Выбираем модули для изучения сегодня
        selected_modules = self._select_modules_for_today(modules, total_allocated_time)
        
        # Распределяем контент по секциям
        for module in selected_modules:
            module_content = self._extract_module_content(module, user_id)
            
            # Распределяем уроки по секциям
            lessons = module_content.get('lessons', [])
            if lessons:
                # Первые уроки - теория
                theory_lessons = lessons[:len(lessons)//2]
                daily_content['theory'].extend(theory_lessons)
                
                # Остальные уроки - практика
                practice_lessons = lessons[len(lessons)//2:]
                daily_content['practice'].extend(practice_lessons)
        
        return daily_content
    
    def _select_modules_for_today(self, modules: List[Dict], total_time: int) -> List[Dict]:
        """
        Выбирает модули для изучения сегодня
        """
        selected_modules = []
        current_time = 0
        
        for module in modules:
            module_time = module.get('estimated_hours', 2) * 60  # Конвертируем в минуты
            
            if current_time + module_time <= total_time:
                selected_modules.append(module)
                current_time += module_time
            else:
                # Если модуль не помещается полностью, добавляем частично
                remaining_time = total_time - current_time
                if remaining_time >= 30:  # Минимум 30 минут
                    partial_module = module.copy()
                    partial_module['estimated_hours'] = remaining_time / 60
                    selected_modules.append(partial_module)
                break
        
        return selected_modules
    
    def _extract_module_content(self, module: Dict, user_id: int) -> Dict:
        """
        Извлекает контент из модуля адаптивного пути
        """
        module_id = module.get('id')
        if not module_id or module_id == 0:
            # Это базовый модуль, создаем рекомендацию
            return {
                'lessons': [{
                    'id': 0,
                    'title': module.get('title', 'Рекомендация'),
                    'type': 'recommendation',
                    'estimated_time': 15,
                    'difficulty': module.get('difficulty', 0.0),
                    'message': 'Пройти диагностику для получения персонализированного контента'
                }]
            }
        
        # Получаем реальный модуль из базы данных
        try:
            db_module = Module.query.get(module_id)
            if not db_module:
                return {'lessons': []}
            
            lessons = []
            for lesson in db_module.lessons.all():
                lessons.append({
                    'id': lesson.id,
                    'title': lesson.title,
                    'type': 'lesson',
                    'estimated_time': 15,
                    'difficulty': lesson.difficulty or 0.0,
                    'content_type': lesson.content_type or 'text'
                })
            
            return {'lessons': lessons}
            
        except Exception as e:
            logger.error(f"Ошибка извлечения контента модуля {module_id}: {e}")
            return {'lessons': []}
    
    def _get_domain_id_by_name(self, domain_name: str) -> int:
        """Get domain ID by domain name/code"""
        try:
            domain = BIGDomain.query.filter_by(code=domain_name).first()
            if domain:
                return domain.id
            
            # Try by name if code not found
            domain = BIGDomain.query.filter_by(name=domain_name).first()
            if domain:
                return domain.id
            
            # Return default domain ID (1) if not found
            return 1
        except Exception as e:
            logger.error(f"Error getting domain ID for {domain_name}: {str(e)}")
            return 1
    
    def _serialize_content_ids(self, content_ids: List[int], content_type: str) -> str:
        """Serialize content IDs to JSON string"""
        import json
        try:
            return json.dumps({
                'ids': content_ids,
                'type': content_type
            })
        except Exception as e:
            logger.error(f"Error serializing content IDs: {str(e)}")
            return json.dumps({'ids': [], 'type': content_type})
    
    def _generate_legacy_plan(self, user_id: int, target_minutes: int, 
                            active_plan: PersonalLearningPlan, reassessment_warning: bool) -> Dict:
        """Генерирует план обучения используя старую логику (fallback)"""
        try:
            # ВАЛИДАЦИЯ: Проверяем наличие активного плана
            if not active_plan:
                logger.error(f"User {user_id}: No active learning plan found")
                return {
                    'success': False,
                    'error': 'No active learning plan',
                    'requires_diagnostic': True,
                    'message': 'Не найден активный план обучения. Необходимо пройти диагностику.'
                }
            
            # ВАЛИДАЦИЯ: Проверяем связь с диагностической сессией
            if not active_plan.diagnostic_session_id:
                logger.error(f"User {user_id}: Learning plan has no diagnostic session")
                return {
                    'success': False,
                    'error': 'Learning plan not linked to diagnostic session',
                    'requires_diagnostic': True,
                    'message': 'План обучения не связан с диагностикой. Необходимо пройти диагностику.'
                }
            
            # ВАЛИДАЦИЯ: Проверяем наличие domain_analysis
            domain_analysis = active_plan.get_domain_analysis()
            if not domain_analysis:
                logger.error(f"User {user_id}: No domain analysis in learning plan")
                return {
                    'success': False,
                    'error': 'No domain analysis in learning plan',
                    'requires_diagnostic': True,
                    'message': 'В плане обучения отсутствует анализ доменов. Необходимо пройти диагностику.'
                }
            
            # Анализируем текущие способности
            abilities = self._analyze_current_abilities(user_id)
            
            # ВАЛИДАЦИЯ: Проверяем что abilities содержат данные
            if not abilities:
                logger.error(f"User {user_id}: No abilities data available")
                return {
                    'success': False,
                    'error': 'No abilities data available',
                    'requires_diagnostic': True,
                    'message': 'Отсутствуют данные о способностях. Необходимо пройти диагностику.'
                }
            
            # Получаем адаптивный путь обучения
            adaptive_path = self._get_adaptive_learning_path(active_plan)
            
            # Определяем слабые домены
            try:
                weak_domains = self._identify_weak_domains(abilities, user_id)
            except ValueError as e:
                logger.error(f"User {user_id}: Error identifying weak domains: {e}")
                return {
                    'success': False,
                    'error': str(e),
                    'requires_diagnostic': True,
                    'message': 'Ошибка определения слабых областей. Необходимо пройти диагностику.'
                }
            
            # ВАЛИДАЦИЯ: Проверяем что найдены слабые домены
            if not weak_domains:
                logger.error(f"User {user_id}: No weak domains identified")
                return {
                    'success': False,
                    'error': 'No weak domains identified',
                    'requires_diagnostic': True,
                    'message': 'Не удалось определить слабые области. Необходимо пройти диагностику.'
                }
            
            # Получаем просроченные повторения
            overdue_reviews = self._get_overdue_reviews(user_id)
            
            # Рассчитываем приоритеты доменов
            domain_priorities = self._calculate_domain_priorities(
                weak_domains, user_id, overdue_reviews
            )
            
            # Распределяем время по приоритетам
            time_allocation = self._allocate_time_by_priority(
                domain_priorities, target_minutes, overdue_reviews
            )
            
            # Выбираем контент для изучения
            if adaptive_path:
                daily_content = self._select_daily_content_with_adaptive_path(
                    time_allocation, abilities, user_id, overdue_reviews, adaptive_path
                )
            else:
                daily_content = self._select_daily_content(
                    time_allocation, abilities, user_id, overdue_reviews
                )
            
            # Получаем пользователя для форматирования
            user = User.query.get(user_id)
            if not user:
                logger.error(f"User {user_id} not found")
                return {
                    'success': False,
                    'error': 'User not found',
                    'requires_diagnostic': True,
                    'message': 'Пользователь не найден.'
                }
            
            # Форматируем для Learning Map
            formatted_plan = self._format_for_learning_map(daily_content, user)
            
            # Добавляем предупреждение о переоценке
            if reassessment_warning:
                formatted_plan['reassessment_warning'] = True
                formatted_plan['reassessment_message'] = 'Рекомендуется пройти повторную диагностику'
            
            return formatted_plan
            
        except Exception as e:
            logger.error(f"Error in legacy plan generation for user {user_id}: {e}")
            return {
                'success': False,
                'error': str(e),
                'requires_diagnostic': True,
                'message': 'Ошибка при создании плана обучения. Необходимо пройти диагностику.'
            }
    
    def _format_existing_plan(self, study_sessions: List[StudySession], user: User,
                             active_plan: PersonalLearningPlan, reassessment_warning: bool) -> Dict:
        """
        Форматирует существующий план из StudySession записей
        
        Args:
            study_sessions: Список StudySession с status='planned' на сегодня
            user: User object
            active_plan: PersonalLearningPlan object
            reassessment_warning: Флаг предупреждения о переоценке
            
        Returns:
            Словарь с отформатированным планом
        """
        try:
            from datetime import datetime, timezone
            import json
            
            theory_items = []
            practice_items = []
            review_items = []
            
            for session in study_sessions:
                try:
                    content_ids_data = json.loads(session.content_ids) if session.content_ids else {}
                    item_ids = content_ids_data.get('ids', [])
                    content_type = content_ids_data.get('type', 'question')
                    
                    for item_id in item_ids:
                        item = {
                            'id': item_id,
                            'type': content_type,
                            'session_id': session.id,
                            'estimated_time': session.planned_duration or 15,
                            'difficulty': session.difficulty_level or 0.0
                        }
                        
                        # Добавляем название в зависимости от типа
                        if content_type == 'lesson':
                            from models import Lesson
                            lesson = Lesson.query.get(item_id)
                            if lesson:
                                item['title'] = lesson.title
                            else:
                                item['title'] = f'Урок #{item_id}'
                        elif content_type == 'question':
                            from models import Question
                            question = Question.query.get(item_id)
                            if question:
                                title = question.text
                                if len(title) > 50:
                                    title = title[:50] + '...'
                                item['title'] = title
                            else:
                                item['title'] = f'Вопрос #{item_id}'
                        else:
                            item['title'] = f'{content_type.title()} #{item_id}'
                        
                        # Распределяем по секциям в зависимости от типа сессии
                        if session.session_type == 'theory':
                            theory_items.append(item)
                        elif session.session_type == 'practice':
                            practice_items.append(item)
                        elif session.session_type == 'review':
                            review_items.append(item)
                        else:
                            # По умолчанию добавляем в практику
                            practice_items.append(item)
                            
                except Exception as e:
                    logger.warning(f"Error formatting session {session.id}: {e}")
                    continue
            
            # Формируем структуру плана
            formatted_plan = {
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                },
                'plan_date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                'target_minutes': sum(s.planned_duration or 15 for s in study_sessions),
                'sections': {
                    'theory': {
                        'title': 'Теория',
                        'items': theory_items,
                        'total_items': len(theory_items),
                        'estimated_time': sum(item.get('estimated_time', 15) for item in theory_items)
                    },
                    'practice': {
                        'title': 'Практика',
                        'items': practice_items,
                        'total_items': len(practice_items),
                        'estimated_time': sum(item.get('estimated_time', 15) for item in practice_items)
                    },
                    'review': {
                        'title': 'Повторение',
                        'items': review_items,
                        'total_items': len(review_items),
                        'estimated_time': sum(item.get('estimated_time', 15) for item in review_items)
                    }
                },
                'theory': {'items': theory_items},  # Для обратной совместимости
                'practice': {'items': practice_items},
                'review': {'items': review_items}
            }
            
            if reassessment_warning:
                formatted_plan['reassessment_warning'] = True
                formatted_plan['reassessment_message'] = 'Рекомендуется пройти повторную диагностику'
            
            return formatted_plan
            
        except Exception as e:
            logger.error(f"Error formatting existing plan: {e}")
            # В случае ошибки возвращаем пустой план
            return {
                'success': False,
                'error': str(e),
                'message': 'Ошибка при форматировании существующего плана'
            }
    
    def _format_integrated_plan(self, integrated_plan: Dict, user: User, 
                              active_plan: PersonalLearningPlan, reassessment_warning: bool) -> Dict:
        """Форматирует интегрированный план для совместимости с существующим API"""
        try:
            # Создаем структуру совместимую с Learning Map
            formatted_plan = {
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email
                },
                'plan_date': datetime.now(timezone.utc).strftime('%Y-%m-%d'),
                'target_minutes': integrated_plan.get('target_minutes', 30),
                'estimated_time': integrated_plan.get('estimated_time', {}),
                'sections': []
            }
            
            # Добавляем секцию повторений
            review_items = integrated_plan.get('review_items', [])
            if review_items:
                review_section = {
                    'type': 'review',
                    'title': 'Повторение',
                    'description': f'{len(review_items)} элементов готовых к повторению',
                    'items': []
                }
                
                for item in review_items:
                    review_section['items'].append({
                        'id': item.question_id,
                        'type': 'question',
                        'title': f'Вопрос #{item.question_id}',
                        'domain': item.domain,
                        'difficulty': self._get_difficulty_level(item.irt_difficulty),
                        'confidence': f"{item.confidence_level:.1%}",
                        'estimated_time': 3,  # 3 минуты на повторение
                        'irt_insights': {
                            'difficulty': item.irt_difficulty,
                            'user_ability': item.user_ability,
                            'learning_rate': item.learning_rate
                        }
                    })
                
                formatted_plan['sections'].append(review_section)
            
            # Добавляем секцию нового контента
            new_content = integrated_plan.get('new_content', [])
            if new_content:
                content_section = {
                    'type': 'new_content',
                    'title': 'Новый материал',
                    'description': 'Рекомендуемые материалы для изучения',
                    'items': new_content
                }
                formatted_plan['sections'].append(content_section)
            
            # Добавляем IRT инсайты
            irt_insights = integrated_plan.get('irt_insights', {})
            if irt_insights:
                formatted_plan['irt_insights'] = irt_insights
            
            # Добавляем рекомендации
            recommendations = integrated_plan.get('learning_recommendations', [])
            if recommendations:
                formatted_plan['recommendations'] = recommendations
            
            # Добавляем предупреждение о переоценке
            if reassessment_warning:
                formatted_plan['reassessment_warning'] = True
                formatted_plan['reassessment_message'] = 'Рекомендуется пройти повторную диагностику'
            
            # Создаем StudySession записи
            if active_plan:
                study_sessions = self._create_integrated_study_sessions(
                    formatted_plan, user, active_plan
                )
                formatted_plan['study_sessions'] = study_sessions
            
            return formatted_plan
            
        except Exception as e:
            logger.error(f"Error formatting integrated plan: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Ошибка при форматировании плана'
            }
    
    def _create_integrated_study_sessions(self, formatted_plan: Dict, user: User, 
                                        active_plan: PersonalLearningPlan) -> List[StudySession]:
        """Создает StudySession записи для интегрированного плана"""
        study_sessions = []
        
        try:
            from datetime import datetime, timezone
            for section in formatted_plan.get('sections', []):
                if section['type'] == 'review':
                    # Создаем сессию для повторений
                    session = StudySession(
                        learning_plan_id=active_plan.id,
                        session_type='review',
                        content_ids=self._serialize_content_ids(
                            [item['id'] for item in section['items']], 'question'
                        ),
                        planned_duration=len(section['items']) * 3,  # 3 минуты на элемент
                        status='planned',
                        started_at=datetime.now(timezone.utc)  # Используем started_at для проверки даты
                    )
                    study_sessions.append(session)
                
                elif section['type'] == 'new_content':
                    # Создаем сессию для нового контента
                    session = StudySession(
                        learning_plan_id=active_plan.id,
                        session_type='practice',
                        content_ids=self._serialize_content_ids(
                            [item['id'] for item in section['items']], 'lesson'
                        ),
                        planned_duration=formatted_plan.get('estimated_time', {}).get('new_content', 15),
                        status='planned',
                        started_at=datetime.now(timezone.utc)  # Используем started_at для проверки даты
                    )
                    study_sessions.append(session)
            
            # Сохраняем сессии в базу данных
            for session in study_sessions:
                db.session.add(session)
            db.session.commit()
            
            return study_sessions
            
        except Exception as e:
            logger.error(f"Error creating integrated study sessions: {e}")
            db.session.rollback()
            return [] 

def generate_from_personal_plan(personal_plan: PersonalLearningPlan, target_minutes: int = 30) -> Dict:
    """
    Generate daily plan using existing PersonalLearningPlan
    """
    try:
        # ВАЛИДАЦИЯ: Проверяем наличие необходимых данных в плане
        if not personal_plan:
            logger.error("PersonalLearningPlan is None")
            return {
                'success': False,
                'error': 'Learning plan not found',
                'requires_diagnostic': True,
                'message': 'Необходимо создать план обучения на основе диагностики'
            }
        
        # Проверяем наличие диагностической сессии
        if not personal_plan.diagnostic_session_id:
            logger.error(f"PersonalLearningPlan {personal_plan.id} has no diagnostic_session_id")
            return {
                'success': False,
                'error': 'No diagnostic session linked to learning plan',
                'requires_diagnostic': True,
                'message': 'План обучения не связан с диагностикой. Необходимо пройти диагностику.'
            }
        
        # Проверяем наличие domain_analysis
        domain_analysis = personal_plan.get_domain_analysis()
        if not domain_analysis:
            logger.error(f"PersonalLearningPlan {personal_plan.id} has no domain_analysis")
            return {
                'success': False,
                'error': 'No domain analysis in learning plan',
                'requires_diagnostic': True,
                'message': 'В плане обучения отсутствует анализ доменов. Необходимо пройти диагностику.'
            }
        
        # Получаем weak domains из плана
        weak_domains = personal_plan.get_weak_domains()
        
        # ВАЛИДАЦИЯ: Проверяем что weak_domains не пустые
        if not weak_domains:
            logger.warning(f"PersonalLearningPlan {personal_plan.id} has empty weak_domains, creating from domain_analysis")
            
            # Создаем weak_domains на основе анализа
            weak_domains = []
            for domain_code, domain_data in domain_analysis.items():
                if isinstance(domain_data, dict):
                    # Используем score если есть, иначе ability_estimate
                    score = domain_data.get('score', domain_data.get('ability_estimate', 100))
                    if score < 70:  # Порог для слабых доменов
                        weak_domains.append(domain_code)
            
            # ВАЛИДАЦИЯ: Если все еще нет weak_domains, это критическая ошибка
            if not weak_domains:
                logger.error(f"PersonalLearningPlan {personal_plan.id}: No weak domains could be identified from domain_analysis")
                return {
                    'success': False,
                    'error': 'No weak domains identified in learning plan',
                    'requires_diagnostic': True,
                    'message': 'Не удалось определить слабые области. Необходимо пройти диагностику.'
                }
            
            # Сохраняем обновленные weak_domains
            personal_plan.set_weak_domains(weak_domains)
            db.session.commit()
            logger.info(f"Created {len(weak_domains)} weak domains from domain_analysis for plan {personal_plan.id}")
        
        logger.info(f"Generating daily plan from PersonalLearningPlan {personal_plan.id}")
        logger.info(f"Weak domains: {weak_domains}")
        
        # Создаем экземпляр DailyLearningAlgorithm
        algorithm = DailyLearningAlgorithm()
        
        # Рассчитываем приоритеты доменов
        priorities = algorithm._calculate_domain_priorities(
            weak_domains=weak_domains,
            user_id=personal_plan.user_id,
            overdue_reviews=[]  # TODO: implement overdue reviews
        )
        
        # Распределяем время
        time_allocation = algorithm._allocate_time_by_priority(
            priorities=priorities,
            total_minutes=target_minutes,
            overdue_reviews=[]
        )
        
        # Создаем контент для каждого домена
        daily_content = {}
        total_allocated_time = 0
        
        for domain_code, allocated_minutes in time_allocation.items():
            if allocated_minutes <= 0:
                continue
                
            domain_content = {
                'domain': domain_code,
                'time_minutes': allocated_minutes,
                'theory': [],
                'practice': [],
                'reviews': []
            }
            
            # Получаем теоретический контент
            theory_content = algorithm._select_theory_content(
                domain=domain_code,
                difficulty='adaptive',
                time_minutes=max(5, allocated_minutes // 2),
                user_id=personal_plan.user_id
            )
            
            # Получаем практический контент
            practice_content = algorithm._select_practice_content(
                domain=domain_code,
                difficulty='adaptive', 
                time_minutes=max(5, allocated_minutes // 2),
                user_id=personal_plan.user_id
            )
            
            # Создаем правильную структуру данных для _create_study_sessions
            domain_content['theory'] = {
                'items': theory_content if isinstance(theory_content, list) else []
            }
            domain_content['practice'] = {
                'items': practice_content if isinstance(practice_content, list) else []
            }
            domain_content['review'] = {
                'items': []
            }
            
            daily_content[domain_code] = domain_content
            total_allocated_time += allocated_minutes
        
        # Создаем StudySession записи
        study_sessions = algorithm._create_study_sessions(
            daily_content=daily_content,
            user=personal_plan.user,
            active_plan=personal_plan
        )
        
        return {
            'success': True,
            'daily_content': daily_content,
            'study_sessions': study_sessions,
            'total_allocated_time': total_allocated_time,
            'weak_domains': weak_domains,
            'plan_id': personal_plan.id
        }
        
    except Exception as e:
        logger.error(f"Error in generate_from_personal_plan for plan {personal_plan.id if personal_plan else 'None'}: {e}")
        return {
            'success': False,
            'error': str(e),
            'requires_diagnostic': True,
            'message': 'Ошибка при создании ежедневного плана. Необходимо пройти диагностику.'
        }

def create_emergency_plan(user_id: int, target_minutes: int = 30) -> Dict:
    """
    Создает экстренный план когда основной план не работает
    """
    try:
        logger.info(f"Creating emergency plan for user {user_id}")
        
        # Получаем все активные домены
        from models import BIGDomain
        all_domains = BIGDomain.query.filter_by(is_active=True).limit(3).all()
        
        if not all_domains:
            # Fallback к базовому контенту
            return {
                'success': True,
                'daily_plan': {
                    'domains': {},
                    'total_time': target_minutes,
                    'session_count': 0,
                    'source': 'emergency_plan',
                    'plan_id': None
                },
                'study_sessions': []
            }
        
        # Создаем простой план с первыми 3 доменами
        daily_content = {}
        time_per_domain = target_minutes // len(all_domains)
        
        for domain in all_domains:
            daily_content[domain.code] = {
                'domain': domain.code,
                'time_minutes': time_per_domain,
                'theory': [],
                'practice': [],
                'reviews': []
            }
        
        return {
            'success': True,
            'daily_plan': {
                'domains': daily_content,
                'total_time': target_minutes,
                'session_count': 0,
                'source': 'emergency_plan',
                'plan_id': None
            },
            'study_sessions': []
        }
        
    except Exception as e:
        logger.error(f"Error creating emergency plan for user {user_id}: {str(e)}")
        # Финальный fallback
        return {
            'success': True,
            'daily_plan': {
                'domains': {},
                'total_time': target_minutes,
                'session_count': 0,
                'source': 'fallback_plan',
                'plan_id': None
            },
            'study_sessions': []
        } 