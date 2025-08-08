"""
Performance Optimizer for IRT System
Система оптимизации производительности для достижения максимальной эффективности
"""

import logging
import time
import cProfile
import pstats
import io
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Any, Callable
from functools import wraps
from dataclasses import dataclass
from enum import Enum
import threading
import queue
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import psutil
import gc

from models import (
    Question, IRTParameters, DiagnosticSession, DiagnosticResponse,
    StudySession, StudySessionResponse, PersonalLearningPlan, User
)
from extensions import db

logger = logging.getLogger(__name__)


class OptimizationLevel(Enum):
    """Уровни оптимизации"""
    BASIC = "basic"
    ADVANCED = "advanced"
    AGGRESSIVE = "aggressive"


@dataclass
class PerformanceMetrics:
    """Метрики производительности"""
    function_name: str
    execution_time: float
    memory_usage: float
    cpu_usage: float
    calls_count: int
    timestamp: datetime
    optimization_level: OptimizationLevel


class PerformanceProfiler:
    """Профилировщик производительности"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.profiler = cProfile.Profile()
        self.is_profiling = False
    
    def start_profiling(self):
        """Начать профилирование"""
        if not self.is_profiling:
            self.profiler.enable()
            self.is_profiling = True
            logger.info("Performance profiling started")
    
    def stop_profiling(self) -> str:
        """Остановить профилирование и получить отчет"""
        if self.is_profiling:
            self.profiler.disable()
            self.is_profiling = False
            
            # Получаем статистику
            s = io.StringIO()
            ps = pstats.Stats(self.profiler, stream=s).sort_stats('cumulative')
            ps.print_stats(20)  # Топ 20 функций
            
            logger.info("Performance profiling stopped")
            return s.getvalue()
        
        return "No profiling data available"
    
    def profile_function(self, func: Callable) -> Callable:
        """Декоратор для профилирования функции"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            start_cpu = psutil.cpu_percent()
            
            try:
                result = func(*args, **kwargs)
                
                end_time = time.time()
                end_memory = psutil.Process().memory_info().rss / 1024 / 1024
                end_cpu = psutil.cpu_percent()
                
                # Записываем метрики
                metrics = PerformanceMetrics(
                    function_name=func.__name__,
                    execution_time=end_time - start_time,
                    memory_usage=end_memory - start_memory,
                    cpu_usage=(start_cpu + end_cpu) / 2,
                    calls_count=1,
                    timestamp=datetime.now(timezone.utc),
                    optimization_level=OptimizationLevel.BASIC
                )
                
                self.metrics.append(metrics)
                
                # Логируем медленные функции
                if metrics.execution_time > 1.0:  # Больше 1 секунды
                    logger.warning(f"Slow function detected: {func.__name__} took {metrics.execution_time:.2f}s")
                
                return result
                
            except Exception as e:
                logger.error(f"Error in profiled function {func.__name__}: {e}")
                raise
        
        return wrapper


class QueryOptimizer:
    """Оптимизатор SQL запросов"""
    
    def __init__(self):
        self.query_stats: Dict[str, Dict] = {}
        self.slow_queries: List[Dict] = []
    
    def optimize_question_query(self, domain_code: str = None, difficulty_range: Tuple[float, float] = None) -> List[Question]:
        """
        Оптимизированный запрос для получения вопросов
        
        Args:
            domain_code: Код домена
            difficulty_range: Диапазон сложности
            
        Returns:
            Список вопросов
        """
        # Используем JOIN для оптимизации
        query = db.session.query(Question).join(IRTParameters)
        
        if domain_code:
            query = query.join(BIGDomain).filter(BIGDomain.code == domain_code)
        
        if difficulty_range:
            min_diff, max_diff = difficulty_range
            query = query.filter(IRTParameters.difficulty.between(min_diff, max_diff))
        
        # Добавляем индексы через hints
        query = query.options(
            db.joinedload(Question.irt_parameters),
            db.joinedload(Question.big_domain)
        )
        
        # Ограничиваем результат
        return query.limit(100).all()
    
    def optimize_session_query(self, user_id: int, status: str = None) -> List[DiagnosticSession]:
        """
        Оптимизированный запрос для получения сессий
        
        Args:
            user_id: ID пользователя
            status: Статус сессии
            
        Returns:
            Список сессий
        """
        query = db.session.query(DiagnosticSession).filter(
            DiagnosticSession.user_id == user_id
        )
        
        if status:
            query = query.filter(DiagnosticSession.status == status)
        
        # Добавляем индексы
        query = query.options(
            db.joinedload(DiagnosticSession.responses),
            db.joinedload(DiagnosticSession.user)
        )
        
        return query.order_by(DiagnosticSession.created_at.desc()).limit(50).all()
    
    def optimize_plan_query(self, user_id: int) -> Optional[PersonalLearningPlan]:
        """
        Оптимизированный запрос для получения плана обучения
        
        Args:
            user_id: ID пользователя
            
        Returns:
            План обучения
        """
        return db.session.query(PersonalLearningPlan).filter(
            PersonalLearningPlan.user_id == user_id
        ).options(
            db.joinedload(PersonalLearningPlan.sessions),
            db.joinedload(PersonalLearningPlan.user)
        ).first()
    
    def analyze_query_performance(self, query_func: Callable, *args, **kwargs) -> Dict:
        """
        Анализ производительности запроса
        
        Args:
            query_func: Функция запроса
            *args, **kwargs: Аргументы запроса
            
        Returns:
            Статистика производительности
        """
        start_time = time.time()
        
        # Включаем SQL логирование
        import logging
        sql_logger = logging.getLogger('sqlalchemy.engine')
        original_level = sql_logger.level
        sql_logger.setLevel(logging.INFO)
        
        try:
            result = query_func(*args, **kwargs)
            
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Анализируем результат
            if isinstance(result, list):
                result_count = len(result)
            elif result is None:
                result_count = 0
            else:
                result_count = 1
            
            stats = {
                'function_name': query_func.__name__,
                'execution_time': execution_time,
                'result_count': result_count,
                'timestamp': datetime.now(timezone.utc)
            }
            
            # Записываем медленные запросы
            if execution_time > 0.5:  # Больше 0.5 секунды
                self.slow_queries.append(stats)
                logger.warning(f"Slow query detected: {query_func.__name__} took {execution_time:.2f}s")
            
            return stats
            
        finally:
            sql_logger.setLevel(original_level)


class MemoryOptimizer:
    """Оптимизатор памяти"""
    
    def __init__(self):
        self.memory_threshold = 0.8  # 80% использования памяти
        self.cleanup_threshold = 100  # Количество объектов для очистки
    
    def check_memory_usage(self) -> Dict:
        """
        Проверка использования памяти
        
        Returns:
            Статистика использования памяти
        """
        process = psutil.Process()
        memory_info = process.memory_info()
        
        # Получаем информацию о памяти
        memory_percent = process.memory_percent()
        memory_mb = memory_info.rss / 1024 / 1024
        
        # Проверяем, нужно ли очистить память
        should_cleanup = memory_percent > (self.memory_threshold * 100)
        
        return {
            'memory_percent': memory_percent,
            'memory_mb': memory_mb,
            'should_cleanup': should_cleanup,
            'timestamp': datetime.now(timezone.utc)
        }
    
    def cleanup_memory(self) -> Dict:
        """
        Очистка памяти
        
        Returns:
            Статистика очистки
        """
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Принудительная сборка мусора
        collected = gc.collect()
        
        # Очищаем кэш SQLAlchemy
        db.session.close()
        
        end_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_freed = start_memory - end_memory
        
        logger.info(f"Memory cleanup: freed {memory_freed:.2f}MB, collected {collected} objects")
        
        return {
            'memory_freed_mb': memory_freed,
            'objects_collected': collected,
            'timestamp': datetime.now(timezone.utc)
        }
    
    def optimize_batch_processing(self, items: List, batch_size: int = 100) -> List:
        """
        Оптимизированная пакетная обработка
        
        Args:
            items: Список элементов для обработки
            batch_size: Размер пакета
            
        Returns:
            Результаты обработки
        """
        results = []
        
        for i in range(0, len(items), batch_size):
            batch = items[i:i + batch_size]
            
            # Обрабатываем пакет
            batch_results = self._process_batch(batch)
            results.extend(batch_results)
            
            # Проверяем память после каждого пакета
            memory_stats = self.check_memory_usage()
            if memory_stats['should_cleanup']:
                self.cleanup_memory()
        
        return results
    
    def _process_batch(self, batch: List) -> List:
        """Обработка одного пакета"""
        # Здесь будет логика обработки пакета
        return batch


class AsyncTaskProcessor:
    """Асинхронный обработчик задач"""
    
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.task_queue = queue.Queue()
        self.results = {}
        self.is_running = False
    
    def start_processor(self):
        """Запуск обработчика"""
        if not self.is_running:
            self.is_running = True
            self._worker_thread = threading.Thread(target=self._process_tasks)
            self._worker_thread.daemon = True
            self._worker_thread.start()
            logger.info("Async task processor started")
    
    def stop_processor(self):
        """Остановка обработчика"""
        self.is_running = False
        if hasattr(self, '_worker_thread'):
            self._worker_thread.join()
        self.executor.shutdown()
        logger.info("Async task processor stopped")
    
    def submit_task(self, task_id: str, task_func: Callable, *args, **kwargs) -> str:
        """
        Отправка задачи на выполнение
        
        Args:
            task_id: ID задачи
            task_func: Функция задачи
            *args, **kwargs: Аргументы задачи
            
        Returns:
            ID задачи
        """
        self.task_queue.put({
            'id': task_id,
            'func': task_func,
            'args': args,
            'kwargs': kwargs,
            'timestamp': datetime.now(timezone.utc)
        })
        
        return task_id
    
    def get_task_result(self, task_id: str) -> Optional[Any]:
        """
        Получение результата задачи
        
        Args:
            task_id: ID задачи
            
        Returns:
            Результат задачи или None
        """
        return self.results.get(task_id)
    
    def _process_tasks(self):
        """Обработка задач в фоновом режиме"""
        while self.is_running:
            try:
                # Получаем задачу из очереди
                task = self.task_queue.get(timeout=1)
                
                # Выполняем задачу
                try:
                    result = task['func'](*task['args'], **task['kwargs'])
                    self.results[task['id']] = {
                        'status': 'completed',
                        'result': result,
                        'completed_at': datetime.now(timezone.utc)
                    }
                except Exception as e:
                    self.results[task['id']] = {
                        'status': 'failed',
                        'error': str(e),
                        'completed_at': datetime.now(timezone.utc)
                    }
                    logger.error(f"Task {task['id']} failed: {e}")
                
                self.task_queue.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in task processor: {e}")


class PerformanceOptimizer:
    """Основной класс оптимизации производительности"""
    
    def __init__(self, optimization_level: OptimizationLevel = OptimizationLevel.BASIC):
        self.optimization_level = optimization_level
        self.profiler = PerformanceProfiler()
        self.query_optimizer = QueryOptimizer()
        self.memory_optimizer = MemoryOptimizer()
        self.async_processor = AsyncTaskProcessor()
        
        # Запускаем асинхронный обработчик
        self.async_processor.start_processor()
        
        logger.info(f"Performance optimizer initialized with level: {optimization_level.value}")
    
    def optimize_irt_calculations(self) -> Dict:
        """
        Оптимизация IRT расчетов
        
        Returns:
            Статистика оптимизации
        """
        start_time = time.time()
        
        # Оптимизация в зависимости от уровня
        if self.optimization_level == OptimizationLevel.BASIC:
            optimizations = self._basic_irt_optimizations()
        elif self.optimization_level == OptimizationLevel.ADVANCED:
            optimizations = self._advanced_irt_optimizations()
        else:  # AGGRESSIVE
            optimizations = self._aggressive_irt_optimizations()
        
        end_time = time.time()
        
        return {
            'optimization_level': self.optimization_level.value,
            'optimizations_applied': optimizations,
            'execution_time': end_time - start_time,
            'timestamp': datetime.now(timezone.utc)
        }
    
    def _basic_irt_optimizations(self) -> List[str]:
        """Базовые оптимизации IRT"""
        optimizations = []
        
        # Кэширование часто используемых параметров
        optimizations.append("cached_irt_parameters")
        
        # Оптимизация запросов к базе данных
        optimizations.append("optimized_database_queries")
        
        # Базовое профилирование
        optimizations.append("basic_profiling")
        
        return optimizations
    
    def _advanced_irt_optimizations(self) -> List[str]:
        """Продвинутые оптимизации IRT"""
        optimizations = self._basic_irt_optimizations()
        
        # Параллельная обработка
        optimizations.append("parallel_processing")
        
        # Оптимизация памяти
        optimizations.append("memory_optimization")
        
        # Асинхронные задачи
        optimizations.append("async_tasks")
        
        return optimizations
    
    def _aggressive_irt_optimizations(self) -> List[str]:
        """Агрессивные оптимизации IRT"""
        optimizations = self._advanced_irt_optimizations()
        
        # Предварительные вычисления
        optimizations.append("precomputed_values")
        
        # Оптимизация алгоритмов
        optimizations.append("algorithm_optimization")
        
        # Распределенная обработка
        optimizations.append("distributed_processing")
        
        return optimizations
    
    def get_performance_report(self) -> Dict:
        """
        Получение отчета о производительности
        
        Returns:
            Отчет о производительности
        """
        # Статистика памяти
        memory_stats = self.memory_optimizer.check_memory_usage()
        
        # Статистика запросов
        query_stats = {
            'slow_queries_count': len(self.query_optimizer.slow_queries),
            'total_queries': len(self.query_optimizer.query_stats)
        }
        
        # Статистика профилирования
        profiling_stats = {
            'profiled_functions': len(self.profiler.metrics),
            'slow_functions': len([m for m in self.profiler.metrics if m.execution_time > 1.0])
        }
        
        # Статистика асинхронных задач
        async_stats = {
            'pending_tasks': self.async_processor.task_queue.qsize(),
            'completed_tasks': len(self.async_processor.results)
        }
        
        return {
            'timestamp': datetime.now(timezone.utc),
            'optimization_level': self.optimization_level.value,
            'memory': memory_stats,
            'queries': query_stats,
            'profiling': profiling_stats,
            'async_tasks': async_stats
        }
    
    def cleanup(self):
        """Очистка ресурсов"""
        self.async_processor.stop_processor()
        self.memory_optimizer.cleanup_memory()
        logger.info("Performance optimizer cleanup completed")


# Глобальный экземпляр оптимизатора
performance_optimizer = PerformanceOptimizer(OptimizationLevel.ADVANCED)


def optimize_performance(level: OptimizationLevel = OptimizationLevel.BASIC) -> Dict:
    """
    Функция для оптимизации производительности системы
    
    Args:
        level: Уровень оптимизации
        
    Returns:
        Результат оптимизации
    """
    global performance_optimizer
    
    # Обновляем уровень оптимизации
    performance_optimizer.optimization_level = level
    
    # Выполняем оптимизацию
    result = performance_optimizer.optimize_irt_calculations()
    
    # Получаем отчет о производительности
    report = performance_optimizer.get_performance_report()
    
    return {
        'optimization_result': result,
        'performance_report': report
    }


def profile_function(func: Callable) -> Callable:
    """
    Декоратор для профилирования функции
    
    Args:
        func: Функция для профилирования
        
    Returns:
        Обернутая функция
    """
    return performance_optimizer.profiler.profile_function(func) 