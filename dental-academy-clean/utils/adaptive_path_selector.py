#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adaptive Path Selector for IRT-based Learning
Адаптивный выбор путей обучения на основе IRT результатов
"""

import logging
import json
import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta, timezone

from extensions import db
from models import (
    LearningPath, PersonalLearningPlan, User, BIGDomain,
    Lesson, Module, Question, ContentDomainMapping
)

logger = logging.getLogger(__name__)

class AdaptivePathSelector:
    """
    Адаптивный селектор путей обучения на основе IRT способностей пользователя
    """
    
    def __init__(self):
        self.ABILITY_THRESHOLDS = {
            'beginner': -1.0,      # Начинающий уровень
            'intermediate': 0.0,   # Средний уровень  
            'advanced': 1.0,       # Продвинутый уровень
            'expert': 2.0          # Эксперт уровень
        }
        
        self.DIFFICULTY_MARGIN = 0.5  # Допустимое отклонение сложности
        self.MAX_PATH_LENGTH = 10     # Максимальное количество модулей в пути
        
    def select_adaptive_path(self, user_id: int, target_domain: str = None) -> Dict:
        """
        Выбирает адаптивный путь обучения для пользователя
        
        Args:
            user_id: ID пользователя
            target_domain: Целевой домен (опционально)
            
        Returns:
            Словарь с адаптивным путем обучения
        """
        try:
            # Получаем данные пользователя
            user = User.query.get(user_id)
            if not user:
                raise ValueError(f"Пользователь {user_id} не найден")
            
            # Получаем активный план обучения
            learning_plan = PersonalLearningPlan.query.filter_by(
                user_id=user_id,
                status='active'
            ).first()
            
            if not learning_plan:
                raise ValueError("Активный план обучения не найден")
            
            # Получаем текущие способности пользователя
            current_abilities = learning_plan.get_domain_analysis()
            if not current_abilities:
                raise ValueError("Не удалось получить способности пользователя")
            
            # Определяем общую способность пользователя
            overall_ability = learning_plan.current_ability or 0.0
            
            # Выбираем подходящие пути обучения
            suitable_paths = self._find_suitable_paths(overall_ability, target_domain)
            
            if not suitable_paths:
                # Если нет подходящих путей, создаем базовый путь
                return self._create_basic_path(user_id, overall_ability, target_domain)
            
            # Выбираем оптимальный путь
            optimal_path = self._select_optimal_path(suitable_paths, current_abilities, learning_plan)
            
            # Адаптируем путь под конкретного пользователя
            personalized_path = self._personalize_path(optimal_path, current_abilities, learning_plan)
            
            return {
                'success': True,
                'path_id': optimal_path.id,
                'path_name': optimal_path.name,
                'estimated_duration': optimal_path.duration_weeks,
                'total_hours': optimal_path.total_estimated_hours,
                'modules': personalized_path['modules'],
                'difficulty_level': self._get_ability_level(overall_ability),
                'target_ability': learning_plan.target_ability,
                'current_ability': overall_ability,
                'weak_domains': learning_plan.get_weak_domains(),
                'strong_domains': learning_plan.get_strong_domains()
            }
            
        except Exception as e:
            logger.error(f"Ошибка выбора адаптивного пути для пользователя {user_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _find_suitable_paths(self, user_ability: float, target_domain: str = None) -> List[LearningPath]:
        """
        Находит подходящие пути обучения на основе способностей пользователя
        """
        # Получаем все активные пути обучения
        query = LearningPath.query.filter_by(is_active=True)
        
        if target_domain:
            # Фильтруем по целевому домену
            query = query.filter(LearningPath.exam_component == target_domain)
        
        all_paths = query.all()
        suitable_paths = []
        
        for path in all_paths:
            # Проверяем подходит ли путь для способностей пользователя
            if self._is_path_suitable(path, user_ability):
                suitable_paths.append(path)
        
        # Сортируем по релевантности
        suitable_paths.sort(key=lambda p: self._calculate_path_relevance(p, user_ability), reverse=True)
        
        return suitable_paths
    
    def _is_path_suitable(self, path: LearningPath, user_ability: float) -> bool:
        """
        Проверяет подходит ли путь обучения для способностей пользователя
        """
        try:
            # Получаем диапазон сложности пути
            difficulty_range = path.get_irt_difficulty_range()
            if not difficulty_range:
                return True  # Если нет данных о сложности, считаем подходящим
            
            min_diff, max_diff = difficulty_range
            
            # Проверяем попадает ли способность пользователя в диапазон
            # Добавляем небольшой запас для обучения
            margin = self.DIFFICULTY_MARGIN
            return (min_diff - margin) <= user_ability <= (max_diff + margin)
            
        except Exception as e:
            logger.warning(f"Ошибка проверки подходящести пути {path.id}: {e}")
            return True
    
    def _calculate_path_relevance(self, path: LearningPath, user_ability: float) -> float:
        """
        Рассчитывает релевантность пути обучения для пользователя
        """
        try:
            # Базовый вес пути
            relevance = 1.0
            
            # Учитываем вес экзамена
            relevance *= (path.exam_weight or 1.0)
            
            # Учитываем соответствие сложности
            difficulty_range = path.get_irt_difficulty_range()
            if difficulty_range:
                min_diff, max_diff = difficulty_range
                # Чем ближе способность к центру диапазона, тем выше релевантность
                center = (min_diff + max_diff) / 2
                distance = abs(user_ability - center)
                relevance *= math.exp(-distance)  # Экспоненциальное убывание
            
            # Учитываем целевые уровни способностей
            target_levels = path.get_target_ability_levels()
            if target_levels:
                # Находим ближайший целевой уровень
                closest_target = min(target_levels.values(), 
                                   key=lambda x: abs(x - user_ability))
                target_distance = abs(user_ability - closest_target)
                relevance *= math.exp(-target_distance)
            
            return relevance
            
        except Exception as e:
            logger.warning(f"Ошибка расчета релевантности пути {path.id}: {e}")
            return 1.0
    
    def _select_optimal_path(self, suitable_paths: List[LearningPath], 
                           current_abilities: Dict, learning_plan: PersonalLearningPlan) -> LearningPath:
        """
        Выбирает оптимальный путь из подходящих
        """
        if not suitable_paths:
            raise ValueError("Нет подходящих путей обучения")
        
        # Получаем слабые домены
        weak_domains = learning_plan.get_weak_domains()
        
        # Сортируем пути по приоритету
        scored_paths = []
        for path in suitable_paths:
            score = self._calculate_path_score(path, current_abilities, weak_domains)
            scored_paths.append((path, score))
        
        # Выбираем путь с наивысшим баллом
        scored_paths.sort(key=lambda x: x[1], reverse=True)
        return scored_paths[0][0]
    
    def _calculate_path_score(self, path: LearningPath, current_abilities: Dict, 
                            weak_domains: List[str]) -> float:
        """
        Рассчитывает балл пути с учетом слабых доменов
        """
        score = 1.0
        
        # Получаем домены пути
        path_domains = path.get_domains()
        
        # Бонус за покрытие слабых доменов
        weak_domains_covered = 0
        for domain in weak_domains:
            if domain in path_domains:
                weak_domains_covered += 1
        
        if weak_domains:
            coverage_ratio = weak_domains_covered / len(weak_domains)
            score *= (1.0 + coverage_ratio)  # Бонус до 100%
        
        # Учитываем общую сложность пути
        difficulty_range = path.get_irt_difficulty_range()
        if difficulty_range:
            min_diff, max_diff = difficulty_range
            avg_difficulty = (min_diff + max_diff) / 2
            
            # Предпочитаем пути с умеренной сложностью
            if -0.5 <= avg_difficulty <= 1.5:
                score *= 1.2
        
        return score
    
    def _personalize_path(self, path: LearningPath, current_abilities: Dict, 
                         learning_plan: PersonalLearningPlan) -> Dict:
        """
        Персонализирует путь обучения под конкретного пользователя
        """
        try:
            # Получаем модули пути
            modules_data = path.modules or []
            
            # Адаптируем модули под способности пользователя
            personalized_modules = []
            
            for module_data in modules_data:
                personalized_module = self._adapt_module(module_data, current_abilities, learning_plan)
                if personalized_module:
                    personalized_modules.append(personalized_module)
            
            # Ограничиваем количество модулей
            if len(personalized_modules) > self.MAX_PATH_LENGTH:
                personalized_modules = personalized_modules[:self.MAX_PATH_LENGTH]
            
            return {
                'modules': personalized_modules,
                'total_modules': len(personalized_modules),
                'estimated_weeks': path.duration_weeks,
                'total_hours': path.total_estimated_hours
            }
            
        except Exception as e:
            logger.error(f"Ошибка персонализации пути {path.id}: {e}")
            return {
                'modules': [],
                'total_modules': 0,
                'estimated_weeks': 0,
                'total_hours': 0
            }
    
    def _adapt_module(self, module_data: Dict, current_abilities: Dict, 
                     learning_plan: PersonalLearningPlan) -> Optional[Dict]:
        """
        Адаптирует модуль под способности пользователя
        """
        try:
            module_id = module_data.get('id')
            if not module_id:
                return None
            
            # Получаем модуль из базы данных
            module = Module.query.get(module_id)
            if not module:
                return None
            
            # Определяем сложность модуля
            module_difficulty = self._calculate_module_difficulty(module, current_abilities)
            
            # Проверяем подходит ли модуль для пользователя
            user_ability = learning_plan.current_ability or 0.0
            if abs(module_difficulty - user_ability) > self.DIFFICULTY_MARGIN:
                # Модуль слишком сложный или легкий - пропускаем
                return None
            
            # Адаптируем уроки в модуле
            adapted_lessons = self._adapt_lessons(module, current_abilities, learning_plan)
            
            return {
                'id': module.id,
                'title': module.title,
                'description': module.description,
                'difficulty': module_difficulty,
                'estimated_hours': module_data.get('estimated_hours', 2),
                'lessons': adapted_lessons,
                'domain': self._get_module_domain(module)
            }
            
        except Exception as e:
            logger.warning(f"Ошибка адаптации модуля: {e}")
            return None
    
    def _calculate_module_difficulty(self, module: Module, current_abilities: Dict) -> float:
        """
        Рассчитывает сложность модуля на основе уроков
        """
        try:
            lessons = module.lessons.all()
            if not lessons:
                return 0.0
            
            total_difficulty = 0.0
            valid_lessons = 0
            
            for lesson in lessons:
                if lesson.difficulty is not None:
                    total_difficulty += lesson.difficulty
                    valid_lessons += 1
            
            if valid_lessons == 0:
                return 0.0
            
            return total_difficulty / valid_lessons
            
        except Exception as e:
            logger.warning(f"Ошибка расчета сложности модуля {module.id}: {e}")
            return 0.0
    
    def _adapt_lessons(self, module: Module, current_abilities: Dict, 
                      learning_plan: PersonalLearningPlan) -> List[Dict]:
        """
        Адаптирует уроки в модуле под способности пользователя
        """
        try:
            lessons = module.lessons.all()
            user_ability = learning_plan.current_ability or 0.0
            
            adapted_lessons = []
            
            for lesson in lessons:
                # Проверяем подходит ли урок для пользователя
                if lesson.difficulty is None or abs(lesson.difficulty - user_ability) <= self.DIFFICULTY_MARGIN:
                    adapted_lessons.append({
                        'id': lesson.id,
                        'title': lesson.title,
                        'difficulty': lesson.difficulty or 0.0,
                        'estimated_time': 15,  # 15 минут на урок
                        'content_type': lesson.content_type or 'text'
                    })
            
            # Сортируем уроки по сложности
            adapted_lessons.sort(key=lambda x: x['difficulty'])
            
            return adapted_lessons
            
        except Exception as e:
            logger.warning(f"Ошибка адаптации уроков модуля {module.id}: {e}")
            return []
    
    def _get_module_domain(self, module: Module) -> str:
        """
        Определяет домен модуля
        """
        try:
            # Пытаемся найти домен через ContentDomainMapping
            mapping = ContentDomainMapping.query.filter_by(module_id=module.id).first()
            if mapping and mapping.domain:
                return mapping.domain.code
            
            # Если нет маппинга, возвращаем общий домен
            return 'GENERAL'
            
        except Exception as e:
            logger.warning(f"Ошибка определения домена модуля {module.id}: {e}")
            return 'GENERAL'
    
    def _create_basic_path(self, user_id: int, user_ability: float, target_domain: str = None) -> Dict:
        """
        Создает базовый путь обучения если нет подходящих
        """
        return {
            'success': True,
            'path_id': 'basic_path',
            'path_name': 'Базовый путь обучения',
            'estimated_duration': 4,
            'total_hours': 20,
            'modules': [
                {
                    'id': 0,
                    'title': 'Введение в предмет',
                    'description': 'Базовые концепции для начала обучения',
                    'difficulty': max(-1.0, user_ability - 0.5),
                    'estimated_hours': 2,
                    'lessons': [
                        {
                            'id': 0,
                            'title': 'Основы',
                            'difficulty': max(-1.0, user_ability - 0.5),
                            'estimated_time': 15,
                            'content_type': 'text'
                        }
                    ],
                    'domain': target_domain or 'GENERAL'
                }
            ],
            'difficulty_level': self._get_ability_level(user_ability),
            'target_ability': user_ability + 0.5,
            'current_ability': user_ability,
            'weak_domains': [],
            'strong_domains': []
        }
    
    def _get_ability_level(self, ability: float) -> str:
        """
        Определяет уровень способностей пользователя
        """
        if ability >= self.ABILITY_THRESHOLDS['expert']:
            return 'expert'
        elif ability >= self.ABILITY_THRESHOLDS['advanced']:
            return 'advanced'
        elif ability >= self.ABILITY_THRESHOLDS['intermediate']:
            return 'intermediate'
        else:
            return 'beginner'
    
    def update_path_after_reassessment(self, user_id: int, new_abilities: Dict) -> Dict:
        """
        Обновляет путь обучения после переоценки способностей
        """
        try:
            # Получаем план обучения
            learning_plan = PersonalLearningPlan.query.filter_by(
                user_id=user_id,
                status='active'
            ).first()
            
            if not learning_plan:
                raise ValueError("Активный план обучения не найден")
            
            # Обновляем способности в плане
            learning_plan.update_after_reassessment(new_abilities)
            
            # Выбираем новый адаптивный путь
            new_path = self.select_adaptive_path(user_id)
            
            return {
                'success': True,
                'message': 'Путь обучения обновлен после переоценки',
                'new_path': new_path
            }
            
        except Exception as e:
            logger.error(f"Ошибка обновления пути после переоценки для пользователя {user_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            } 