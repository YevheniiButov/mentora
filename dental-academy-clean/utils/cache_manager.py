"""
Cache Manager for IRT System
Система кэширования для оптимизации производительности и снижения нагрузки на базу данных
"""

import logging
import time
import json
import hashlib
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from collections import OrderedDict
import pickle
import gzip

from models import (
    Question, IRTParameters, DiagnosticSession, DiagnosticResponse,
    StudySession, StudySessionResponse, PersonalLearningPlan, User, BIGDomain
)
from extensions import db

logger = logging.getLogger(__name__)


class CacheLevel(Enum):
    """Уровни кэширования"""
    NONE = "none"
    BASIC = "basic"
    AGGRESSIVE = "aggressive"


@dataclass
class CacheEntry:
    """Запись в кэше"""
    key: str
    value: Any
    created_at: datetime
    expires_at: datetime
    access_count: int
    last_accessed: datetime
    size_bytes: int


class LRUCache:
    """LRU (Least Recently Used) кэш"""
    
    def __init__(self, max_size: int = 1000, max_memory_mb: int = 100):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.lock = threading.RLock()
        self.total_memory = 0
        
        logger.info(f"LRU Cache initialized: max_size={max_size}, max_memory={max_memory_mb}MB")
    
    def get(self, key: str) -> Optional[Any]:
        """
        Получить значение из кэша
        
        Args:
            key: Ключ
            
        Returns:
            Значение или None
        """
        with self.lock:
            if key in self.cache:
                entry = self.cache[key]
                
                # Проверяем срок действия
                if datetime.now(timezone.utc) > entry.expires_at:
                    self._remove_entry(key)
                    return None
                
                # Обновляем статистику доступа
                entry.access_count += 1
                entry.last_accessed = datetime.now(timezone.utc)
                
                # Перемещаем в конец (LRU)
                self.cache.move_to_end(key)
                
                logger.debug(f"Cache hit: {key}")
                return entry.value
            
            logger.debug(f"Cache miss: {key}")
            return None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 3600) -> bool:
        """
        Установить значение в кэш
        
        Args:
            key: Ключ
            value: Значение
            ttl_seconds: Время жизни в секундах
            
        Returns:
            True если успешно
        """
        with self.lock:
            # Удаляем существующую запись
            if key in self.cache:
                self._remove_entry(key)
            
            # Создаем новую запись
            now = datetime.now(timezone.utc)
            expires_at = now + timedelta(seconds=ttl_seconds)
            
            # Оцениваем размер
            try:
                size_bytes = len(pickle.dumps(value))
            except:
                size_bytes = 1024  # Fallback размер
            
            entry = CacheEntry(
                key=key,
                value=value,
                created_at=now,
                expires_at=expires_at,
                access_count=0,
                last_accessed=now,
                size_bytes=size_bytes
            )
            
            # Проверяем лимиты
            if not self._can_add_entry(entry):
                self._evict_entries(entry.size_bytes)
            
            # Добавляем запись
            self.cache[key] = entry
            self.total_memory += entry.size_bytes
            
            logger.debug(f"Cache set: {key}, size={size_bytes} bytes")
            return True
    
    def delete(self, key: str) -> bool:
        """
        Удалить запись из кэша
        
        Args:
            key: Ключ
            
        Returns:
            True если запись была удалена
        """
        with self.lock:
            return self._remove_entry(key)
    
    def clear(self):
        """Очистить весь кэш"""
        with self.lock:
            self.cache.clear()
            self.total_memory = 0
            logger.info("Cache cleared")
    
    def get_stats(self) -> Dict:
        """
        Получить статистику кэша
        
        Returns:
            Статистика кэша
        """
        with self.lock:
            total_entries = len(self.cache)
            total_memory_mb = self.total_memory / 1024 / 1024
            
            # Находим самые популярные записи
            popular_entries = sorted(
                self.cache.values(),
                key=lambda x: x.access_count,
                reverse=True
            )[:5]
            
            return {
                'total_entries': total_entries,
                'total_memory_mb': total_memory_mb,
                'max_size': self.max_size,
                'max_memory_mb': self.max_memory_bytes / 1024 / 1024,
                'popular_entries': [
                    {
                        'key': entry.key,
                        'access_count': entry.access_count,
                        'size_bytes': entry.size_bytes
                    }
                    for entry in popular_entries
                ]
            }
    
    def _remove_entry(self, key: str) -> bool:
        """Удалить запись из кэша"""
        if key in self.cache:
            entry = self.cache[key]
            self.total_memory -= entry.size_bytes
            del self.cache[key]
            return True
        return False
    
    def _can_add_entry(self, entry: CacheEntry) -> bool:
        """Проверить, можно ли добавить запись"""
        return (
            len(self.cache) < self.max_size and
            self.total_memory + entry.size_bytes <= self.max_memory_bytes
        )
    
    def _evict_entries(self, needed_bytes: int):
        """Удалить записи для освобождения места"""
        while (
            len(self.cache) > 0 and
            (len(self.cache) >= self.max_size or
             self.total_memory + needed_bytes > self.max_memory_bytes)
        ):
            # Удаляем самую старую запись (LRU)
            oldest_key = next(iter(self.cache))
            self._remove_entry(oldest_key)


class IRTCacheManager:
    """Менеджер кэширования для IRT системы"""
    
    def __init__(self, cache_level: CacheLevel = CacheLevel.BASIC):
        self.cache_level = cache_level
        self.lru_cache = LRUCache(max_size=2000, max_memory_mb=200)
        
        # Специализированные кэши
        self.question_cache = LRUCache(max_size=500, max_memory_mb=50)
        self.irt_params_cache = LRUCache(max_size=1000, max_memory_mb=50)
        self.session_cache = LRUCache(max_size=300, max_memory_mb=30)
        self.plan_cache = LRUCache(max_size=200, max_memory_mb=20)
        
        logger.info(f"IRT Cache Manager initialized with level: {cache_level.value}")
    
    def get_question(self, question_id: int) -> Optional[Question]:
        """
        Получить вопрос из кэша
        
        Args:
            question_id: ID вопроса
            
        Returns:
            Вопрос или None
        """
        if self.cache_level == CacheLevel.NONE:
            return None
        
        cache_key = f"question:{question_id}"
        cached_question_id = self.question_cache.get(cache_key)
        
        if cached_question_id:
            # Кэшируем только ID, загружаем объект заново
            logger.debug(f"Cache hit for question {question_id}, reloading from database")
            fresh_question = Question.query.options(
                db.joinedload(Question.irt_parameters),
                db.joinedload(Question.big_domain)
            ).get(question_id)
            
            if fresh_question:
                return fresh_question
            else:
                # Вопрос больше не существует, удаляем из кэша
                self.question_cache.delete(cache_key)
        
        # Загружаем из базы данных
        question = Question.query.options(
            db.joinedload(Question.irt_parameters),
            db.joinedload(Question.big_domain)
        ).get(question_id)
        
        if question:
            # Кэшируем только ID
            self.question_cache.set(cache_key, question_id, ttl_seconds=1800)  # 30 минут
        
        return question
    
    def get_irt_parameters(self, question_id: int) -> Optional[IRTParameters]:
        """
        Получить IRT параметры из кэша
        
        Args:
            question_id: ID вопроса
            
        Returns:
            IRT параметры или None
        """
        if self.cache_level == CacheLevel.NONE:
            return None
        
        cache_key = f"irt_params:{question_id}"
        cached_params_id = self.irt_params_cache.get(cache_key)
        
        if cached_params_id:
            # Кэшируем только ID, загружаем объект заново
            logger.debug(f"Cache hit for IRT params {question_id}, reloading from database")
            fresh_params = IRTParameters.query.filter_by(question_id=question_id).first()
            
            if fresh_params:
                return fresh_params
            else:
                # Параметры больше не существуют, удаляем из кэша
                self.irt_params_cache.delete(cache_key)
        
        # Загружаем из базы данных
        params = IRTParameters.query.filter_by(question_id=question_id).first()
        if params:
            # Кэшируем только ID
            self.irt_params_cache.set(cache_key, params.id, ttl_seconds=3600)  # 1 час
        
        return params
    
    def get_domain_questions(self, domain_code: str, difficulty_range: Optional[Tuple[float, float]] = None) -> List[Question]:
        """
        Получить вопросы домена из кэша
        
        Args:
            domain_code: Код домена
            difficulty_range: Диапазон сложности
            
        Returns:
            Список вопросов
        """
        if self.cache_level == CacheLevel.NONE:
            return []
        
        # Создаем ключ кэша
        if difficulty_range:
            min_diff, max_diff = difficulty_range
            cache_key = f"domain_questions:{domain_code}:{min_diff:.2f}-{max_diff:.2f}"
        else:
            cache_key = f"domain_questions:{domain_code}"
        
        cached_question_ids = self.question_cache.get(cache_key)
        
        if cached_question_ids:
            # Кэшируем только ID, загружаем объекты заново
            logger.info(f"Cache hit for domain {domain_code}, reloading {len(cached_question_ids)} questions from database")
            
            try:
                # Загружаем свежие объекты из базы данных по ID
                fresh_questions = Question.query.options(
                    db.joinedload(Question.irt_parameters),
                    db.joinedload(Question.big_domain)
                ).filter(Question.id.in_(cached_question_ids)).all()
                
                logger.info(f"Successfully loaded {len(fresh_questions)} fresh questions from database")
                
                # Проверяем, что все вопросы загружены
                if len(fresh_questions) != len(cached_question_ids):
                    logger.warning(f"Some questions missing: expected {len(cached_question_ids)}, got {len(fresh_questions)}")
                    # Обновляем кэш с актуальными ID
                    actual_ids = [q.id for q in fresh_questions]
                    self.question_cache.set(cache_key, actual_ids, ttl_seconds=900)
                
                return fresh_questions
                
            except Exception as e:
                logger.error(f"Error reloading questions for domain {domain_code}: {e}")
                logger.error(f"Error type: {type(e)}")
                import traceback
                logger.error(f"Full traceback: {traceback.format_exc()}")
                # Очищаем поврежденный кэш
                self.question_cache.delete(cache_key)
                logger.info(f"Cleared damaged cache for domain {domain_code}")
        
        # Загружаем из базы данных напрямую (ИСПРАВЛЕНИЕ РЕКУРСИИ)
        # from extensions import db  # Уже импортировано в начале файла
        
        # Прямой запрос к базе данных без использования IRTEngine
        domain = BIGDomain.query.filter_by(code=domain_code).first()
        if not domain:
            return []
        
        query = Question.query.filter_by(big_domain_id=domain.id)
        
        if difficulty_range:
            min_diff, max_diff = difficulty_range
            query = query.join(IRTParameters).filter(
                IRTParameters.difficulty >= min_diff,
                IRTParameters.difficulty <= max_diff
            )
        
        questions = query.limit(100).all()
        
        if questions:
            # Кэшируем только ID вопросов
            question_ids = [q.id for q in questions]
            self.question_cache.set(cache_key, question_ids, ttl_seconds=900)  # 15 минут
            logger.info(f"Cached {len(question_ids)} question IDs for domain {domain_code}")
        
        return questions
    
    def get_user_sessions(self, user_id: int, status: str = None) -> List[DiagnosticSession]:
        """
        Получить сессии пользователя из кэша
        
        Args:
            user_id: ID пользователя
            status: Статус сессии
            
        Returns:
            Список сессий
        """
        if self.cache_level == CacheLevel.NONE:
            return []
        
        cache_key = f"user_sessions:{user_id}:{status or 'all'}"
        cached_sessions = self.session_cache.get(cache_key)
        
        if cached_sessions:
            return cached_sessions
        
        # Загружаем из базы данных
        query = DiagnosticSession.query.filter(DiagnosticSession.user_id == user_id)
        if status:
            query = query.filter(DiagnosticSession.status == status)
        
        sessions = query.order_by(DiagnosticSession.created_at.desc()).limit(50).all()
        
        if sessions:
            self.session_cache.set(cache_key, sessions, ttl_seconds=300)  # 5 минут
        
        return sessions
    
    def get_learning_plan(self, user_id: int) -> Optional[PersonalLearningPlan]:
        """
        Получить план обучения из кэша
        
        Args:
            user_id: ID пользователя
            
        Returns:
            План обучения или None
        """
        if self.cache_level == CacheLevel.NONE:
            return None
        
        cache_key = f"learning_plan:{user_id}"
        cached_plan = self.plan_cache.get(cache_key)
        
        if cached_plan:
            return cached_plan
        
        # Загружаем из базы данных
        plan = PersonalLearningPlan.query.filter_by(user_id=user_id).first()
        if plan:
            self.plan_cache.set(cache_key, plan, ttl_seconds=600)  # 10 минут
        
        return plan
    
    def invalidate_question_cache(self, question_id: int):
        """Инвалидировать кэш вопроса"""
        cache_key = f"question:{question_id}"
        self.question_cache.delete(cache_key)
        
        # Инвалидируем связанные кэши
        self.irt_params_cache.delete(f"irt_params:{question_id}")
        
        logger.debug(f"Invalidated cache for question {question_id}")
    
    def invalidate_user_cache(self, user_id: int):
        """Инвалидировать кэш пользователя"""
        # Удаляем все кэши, связанные с пользователем
        for cache in [self.session_cache, self.plan_cache]:
            keys_to_delete = []
            for key in cache.cache.keys():
                if f":{user_id}:" in key or key.endswith(f":{user_id}"):
                    keys_to_delete.append(key)
            
            for key in keys_to_delete:
                cache.delete(key)
        
        logger.debug(f"Invalidated cache for user {user_id}")
    
    def invalidate_domain_cache(self, domain_code: str):
        """Инвалидировать кэш домена"""
        keys_to_delete = []
        for key in self.question_cache.cache.keys():
            if key.startswith(f"domain_questions:{domain_code}"):
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            self.question_cache.delete(key)
        
        logger.debug(f"Invalidated cache for domain {domain_code}")
    
    def get_cache_stats(self) -> Dict:
        """
        Получить статистику всех кэшей
        
        Returns:
            Объединенная статистика
        """
        return {
            'cache_level': self.cache_level.value,
            'general_cache': self.lru_cache.get_stats(),
            'question_cache': self.question_cache.get_stats(),
            'irt_params_cache': self.irt_params_cache.get_stats(),
            'session_cache': self.session_cache.get_stats(),
            'plan_cache': self.plan_cache.get_stats(),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def clear_all_caches(self):
        """Очистить все кэши"""
        self.lru_cache.clear()
        self.question_cache.clear()
        self.irt_params_cache.clear()
        self.session_cache.clear()
        self.plan_cache.clear()
        
        logger.info("All caches cleared")


# Глобальный экземпляр менеджера кэширования
cache_manager = IRTCacheManager(CacheLevel.BASIC)


def get_cached_question(question_id: int) -> Optional[Question]:
    """Получить вопрос из кэша"""
    return cache_manager.get_question(question_id)


def get_cached_irt_parameters(question_id: int) -> Optional[IRTParameters]:
    """Получить IRT параметры из кэша"""
    return cache_manager.get_irt_parameters(question_id)


def get_cached_domain_questions(domain_code: str, difficulty_range: Optional[Tuple[float, float]] = None) -> List[Question]:
    """Получить вопросы домена из кэша"""
    return cache_manager.get_domain_questions(domain_code, difficulty_range)


def invalidate_question_cache(question_id: int):
    """Инвалидировать кэш вопроса"""
    cache_manager.invalidate_question_cache(question_id)


def invalidate_user_cache(user_id: int):
    """Инвалидировать кэш пользователя"""
    cache_manager.invalidate_user_cache(user_id)


def get_cache_stats() -> Dict:
    """Получить статистику кэширования"""
    return cache_manager.get_cache_stats() 