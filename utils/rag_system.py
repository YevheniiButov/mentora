"""
RAG (Retrieval-Augmented Generation) система для Dental Academy
Обеспечивает семантический поиск по образовательному контенту и генерацию контекста для AI
"""

import os
import json
import hashlib
import logging
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime, timedelta
import numpy as np
from sqlalchemy import and_, or_
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import re

from models import (
    db, Lesson, Module, Subject, Question, VirtualPatientScenario,
    ContentEmbedding, RAGCache, User
)


class RAGSystem:
    """Основной класс RAG системы для Dental Academy"""
    
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Инициализация RAG системы
        
        Args:
            model_name: Название модели для создания эмбеддингов
        """
        self.model_name = model_name
        self.embedding_model = None
        self.chunk_size = 512  # Размер чанка в символах
        self.chunk_overlap = 50  # Перекрытие между чанками
        self.min_similarity_threshold = 0.3  # Минимальный порог схожести
        self.cache_ttl_hours = 24  # TTL кэша в часах
        
        # Настройка логирования
        self.logger = logging.getLogger(__name__)
        
    def _get_embedding_model(self):
        """Ленивая загрузка модели эмбеддингов"""
        if self.embedding_model is None:
            try:
                self.embedding_model = SentenceTransformer(self.model_name)
                self.logger.info(f"Загружена модель эмбеддингов: {self.model_name}")
            except Exception as e:
                self.logger.error(f"Ошибка загрузки модели {self.model_name}: {e}")
                raise
        return self.embedding_model
    
    def chunk_text(self, text: str, title: str = "") -> List[Dict[str, Any]]:
        """
        Разбивает текст на чанки с перекрытием
        
        Args:
            text: Исходный текст
            title: Заголовок для включения в чанки
            
        Returns:
            Список чанков с метаданными
        """
        if not text.strip():
            return []
        
        # Удаляем HTML теги и лишние пробелы
        clean_text = re.sub(r'<[^>]+>', '', text)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        chunks = []
        
        # Если текст короткий, возвращаем как один чанк
        if len(clean_text) <= self.chunk_size:
            chunks.append({
                'text': clean_text,
                'index': 0,
                'title': title,
                'length': len(clean_text)
            })
            return chunks
        
        # Разбиваем на чанки с перекрытием
        start = 0
        chunk_index = 0
        
        while start < len(clean_text):
            end = start + self.chunk_size
            
            # Пытаемся найти конец предложения для естественного разрыва
            if end < len(clean_text):
                sentence_end = clean_text.rfind('.', start, end)
                if sentence_end > start + self.chunk_size // 2:
                    end = sentence_end + 1
            
            chunk_text = clean_text[start:end].strip()
            
            # Добавляем заголовок к чанку если есть
            if title:
                chunk_text = f"{title}\n\n{chunk_text}"
            
            chunks.append({
                'text': chunk_text,
                'index': chunk_index,
                'title': title,
                'length': len(chunk_text)
            })
            
            # Следующий чанк начинается с учетом перекрытия
            start = end - self.chunk_overlap
            chunk_index += 1
            
            # Защита от бесконечного цикла
            if start <= 0:
                break
        
        return chunks
    
    def create_embedding(self, text: str) -> np.ndarray:
        """
        Создает векторное представление текста
        
        Args:
            text: Текст для векторизации
            
        Returns:
            Вектор эмбеддинга
        """
        try:
            model = self._get_embedding_model()
            embedding = model.encode(text, convert_to_numpy=True)
            return embedding
        except Exception as e:
            self.logger.error(f"Ошибка создания эмбеддинга: {e}")
            raise
    
    def _calculate_content_hash(self, content: str) -> str:
        """Вычисляет MD5 хэш контента"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def process_lesson_content(self, lesson: Lesson, language: str = 'en') -> List[ContentEmbedding]:
        """
        Обрабатывает урок и создает эмбеддинги
        
        Args:
            lesson: Объект урока
            language: Язык контента
            
        Returns:
            Список созданных эмбеддингов
        """
        if not lesson.content:
            return []
        
        content_hash = self._calculate_content_hash(lesson.content)
        
        # Проверяем, есть ли уже эмбеддинги для этого контента
        existing = db.session.query(ContentEmbedding).filter_by(
            content_type='lesson',
            content_id=lesson.id,
            language=language,
            content_hash=content_hash
        ).first()
        
        if existing:
            self.logger.info(f"Эмбеддинги для урока {lesson.id} уже существуют")
            return db.session.query(ContentEmbedding).filter_by(
                content_type='lesson',
                content_id=lesson.id,
                language=language
            ).all()
        
        # Удаляем старые эмбеддинги если контент изменился
        db.session.query(ContentEmbedding).filter_by(
            content_type='lesson',
            content_id=lesson.id,
            language=language
        ).delete()
        
        # Создаем чанки
        chunks = self.chunk_text(lesson.content, lesson.title)
        embeddings = []
        
        for chunk_data in chunks:
            try:
                # Создаем вектор
                embedding_vector = self.create_embedding(chunk_data['text'])
                
                # Создаем запись в БД
                embedding = ContentEmbedding(
                    content_type='lesson',
                    content_id=lesson.id,
                    text_chunk=chunk_data['text'],
                    chunk_index=chunk_data['index'],
                    title=lesson.title,
                    embedding_vector=embedding_vector.tolist(),
                    vector_model=self.model_name,
                    language=language,
                    subject_id=lesson.module.subject_id if lesson.module else None,
                    module_id=lesson.module_id,
                    content_hash=content_hash
                )
                
                db.session.add(embedding)
                embeddings.append(embedding)
                
            except Exception as e:
                self.logger.error(f"Ошибка обработки чанка урока {lesson.id}: {e}")
                continue
        
        try:
            db.session.commit()
            self.logger.info(f"Создано {len(embeddings)} эмбеддингов для урока {lesson.id}")
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Ошибка сохранения эмбеддингов урока {lesson.id}: {e}")
            raise
        
        return embeddings
    
    def process_test_questions(self, questions: List[Question], language: str = 'en') -> List[ContentEmbedding]:
        """
        Обрабатывает тестовые вопросы и создает эмбеддинги
        
        Args:
            questions: Список вопросов
            language: Язык контента
            
        Returns:
            Список созданных эмбеддингов
        """
        embeddings = []
        
        for question in questions:
            # Формируем полный текст вопроса
            full_text = question.text
            if question.explanation:
                full_text += f"\n\nОбъяснение: {question.explanation}"
            
            content_hash = self._calculate_content_hash(full_text)
            
            # Проверяем существующие эмбеддинги
            existing = db.session.query(ContentEmbedding).filter_by(
                content_type='question',
                content_id=question.id,
                language=language,
                content_hash=content_hash
            ).first()
            
            if existing:
                continue
            
            # Удаляем старые эмбеддинги
            db.session.query(ContentEmbedding).filter_by(
                content_type='question',
                content_id=question.id,
                language=language
            ).delete()
            
            try:
                # Создаем вектор
                embedding_vector = self.create_embedding(full_text)
                
                # Создаем запись в БД
                embedding = ContentEmbedding(
                    content_type='question',
                    content_id=question.id,
                    text_chunk=full_text,
                    chunk_index=0,
                    title=f"Вопрос: {question.text[:100]}...",
                    embedding_vector=embedding_vector.tolist(),
                    vector_model=self.model_name,
                    language=language,
                    content_hash=content_hash
                )
                
                db.session.add(embedding)
                embeddings.append(embedding)
                
            except Exception as e:
                self.logger.error(f"Ошибка обработки вопроса {question.id}: {e}")
                continue
        
        try:
            db.session.commit()
            self.logger.info(f"Создано {len(embeddings)} эмбеддингов для {len(questions)} вопросов")
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Ошибка сохранения эмбеддингов вопросов: {e}")
            raise
        
        return embeddings
    
    def process_virtual_patient_scenarios(self, scenarios: List[VirtualPatientScenario], language: str = 'en') -> List[ContentEmbedding]:
        """
        Обрабатывает сценарии виртуальных пациентов
        
        Args:
            scenarios: Список сценариев
            language: Язык контента
            
        Returns:
            Список созданных эмбеддингов
        """
        embeddings = []
        
        for scenario in scenarios:
            # Формируем полный текст сценария
            full_text = f"{scenario.title}\n\n{scenario.description or ''}"
            if scenario.scenario_data:
                try:
                    scenario_json = json.loads(scenario.scenario_data)
                    if 'patient_info' in scenario_json:
                        full_text += f"\n\nИнформация о пациенте: {json.dumps(scenario_json['patient_info'], ensure_ascii=False)}"
                except json.JSONDecodeError:
                    pass
            
            content_hash = self._calculate_content_hash(full_text)
            
            # Проверяем существующие эмбеддинги
            existing = db.session.query(ContentEmbedding).filter_by(
                content_type='virtual_patient',
                content_id=scenario.id,
                language=language,
                content_hash=content_hash
            ).first()
            
            if existing:
                continue
            
            # Удаляем старые эмбеддинги
            db.session.query(ContentEmbedding).filter_by(
                content_type='virtual_patient',
                content_id=scenario.id,
                language=language
            ).delete()
            
            # Создаем чанки для длинного контента
            chunks = self.chunk_text(full_text, scenario.title)
            
            for chunk_data in chunks:
                try:
                    # Создаем вектор
                    embedding_vector = self.create_embedding(chunk_data['text'])
                    
                    # Создаем запись в БД
                    embedding = ContentEmbedding(
                        content_type='virtual_patient',
                        content_id=scenario.id,
                        text_chunk=chunk_data['text'],
                        chunk_index=chunk_data['index'],
                        title=scenario.title,
                        embedding_vector=embedding_vector.tolist(),
                        vector_model=self.model_name,
                        language=language,
                        difficulty_level=scenario.difficulty,
                        content_hash=content_hash
                    )
                    
                    db.session.add(embedding)
                    embeddings.append(embedding)
                    
                except Exception as e:
                    self.logger.error(f"Ошибка обработки чанка сценария {scenario.id}: {e}")
                    continue
        
        try:
            db.session.commit()
            self.logger.info(f"Создано {len(embeddings)} эмбеддингов для {len(scenarios)} сценариев")
        except Exception as e:
            db.session.rollback()
            self.logger.error(f"Ошибка сохранения эмбеддингов сценариев: {e}")
            raise
        
        return embeddings
    
    def process_all_content(self, language: str = 'en', batch_size: int = 10) -> Dict[str, int]:
        """
        Обрабатывает весь образовательный контент для создания эмбеддингов
        
        Args:
            language: Язык контента
            batch_size: Размер батча для обработки
            
        Returns:
            Статистика обработанного контента
        """
        stats = {
            'lessons_processed': 0,
            'questions_processed': 0,
            'scenarios_processed': 0,
            'total_embeddings_created': 0,
            'errors': 0
        }
        
        try:
            # Обрабатываем уроки
            lessons = db.session.query(Lesson).filter(
                Lesson.content.isnot(None),
                Lesson.content != ''
            ).all()
            
            for i in range(0, len(lessons), batch_size):
                batch = lessons[i:i + batch_size]
                for lesson in batch:
                    try:
                        embeddings = self.process_lesson_content(lesson, language)
                        stats['total_embeddings_created'] += len(embeddings)
                        stats['lessons_processed'] += 1
                    except Exception as e:
                        self.logger.error(f"Ошибка обработки урока {lesson.id}: {e}")
                        stats['errors'] += 1
            
            # Обрабатываем вопросы
            questions = db.session.query(Question).filter(
                Question.text.isnot(None),
                Question.text != ''
            ).all()
            
            for i in range(0, len(questions), batch_size):
                batch = questions[i:i + batch_size]
                try:
                    embeddings = self.process_test_questions(batch, language)
                    stats['total_embeddings_created'] += len(embeddings)
                    stats['questions_processed'] += len(batch)
                except Exception as e:
                    self.logger.error(f"Ошибка обработки батча вопросов: {e}")
                    stats['errors'] += 1
            
            # Обрабатываем сценарии виртуальных пациентов
            scenarios = db.session.query(VirtualPatientScenario).filter(
                VirtualPatientScenario.is_published == True
            ).all()
            
            for i in range(0, len(scenarios), batch_size):
                batch = scenarios[i:i + batch_size]
                try:
                    embeddings = self.process_virtual_patient_scenarios(batch, language)
                    stats['total_embeddings_created'] += len(embeddings)
                    stats['scenarios_processed'] += len(batch)
                except Exception as e:
                    self.logger.error(f"Ошибка обработки батча сценариев: {e}")
                    stats['errors'] += 1
            
            self.logger.info(f"Обработка контента завершена: {stats}")
            
        except Exception as e:
            self.logger.error(f"Критическая ошибка при обработке контента: {e}")
            stats['errors'] += 1
        
        return stats
    
    def _create_query_hash(self, query: str, filters: Dict = None, language: str = 'en') -> str:
        """Создает хэш для запроса RAG"""
        query_data = {
            'query': query.lower().strip(),
            'filters': filters or {},
            'language': language
        }
        query_str = json.dumps(query_data, sort_keys=True)
        return hashlib.md5(query_str.encode('utf-8')).hexdigest()
    
    def semantic_search(self, 
                       query: str, 
                       language: str = 'en',
                       limit: int = 5,
                       filters: Dict = None,
                       use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Выполняет семантический поиск по контенту
        
        Args:
            query: Поисковый запрос
            language: Язык поиска
            limit: Максимальное количество результатов
            filters: Дополнительные фильтры (subject_id, difficulty, content_type)
            use_cache: Использовать кэш результатов
            
        Returns:
            Список релевантных результатов
        """
        if not query.strip():
            return []
        
        query_hash = self._create_query_hash(query, filters, language)
        
        # Проверяем кэш
        if use_cache:
            cached_result = db.session.query(RAGCache).filter_by(
                query_hash=query_hash
            ).first()
            
            if cached_result and not cached_result.is_expired():
                cached_result.touch()
                return cached_result.search_results
        
        try:
            # Создаем вектор запроса
            query_embedding = self.create_embedding(query)
            
            # Строим запрос к БД
            query_builder = db.session.query(ContentEmbedding).filter_by(language=language)
            
            # Применяем фильтры
            if filters:
                if 'subject_id' in filters:
                    query_builder = query_builder.filter_by(subject_id=filters['subject_id'])
                if 'difficulty' in filters:
                    query_builder = query_builder.filter_by(difficulty_level=filters['difficulty'])
                if 'content_type' in filters:
                    content_types = filters['content_type'] if isinstance(filters['content_type'], list) else [filters['content_type']]
                    query_builder = query_builder.filter(ContentEmbedding.content_type.in_(content_types))
            
            # Получаем эмбеддинги
            embeddings = query_builder.all()
            
            if not embeddings:
                return []
            
            # Вычисляем схожесть
            embedding_vectors = np.array([emb.embedding_vector for emb in embeddings])
            similarities = cosine_similarity([query_embedding], embedding_vectors)[0]
            
            # Фильтруем по минимальному порогу и сортируем
            results = []
            for i, embedding in enumerate(embeddings):
                similarity = similarities[i]
                if similarity >= self.min_similarity_threshold:
                    results.append({
                        'embedding_id': embedding.id,
                        'content_type': embedding.content_type,
                        'content_id': embedding.content_id,
                        'text': embedding.text_chunk,
                        'title': embedding.title,
                        'similarity': float(similarity),
                        'chunk_index': embedding.chunk_index,
                        'subject_id': embedding.subject_id,
                        'module_id': embedding.module_id,
                        'difficulty_level': embedding.difficulty_level
                    })
            
            # Сортируем по релевантности
            results.sort(key=lambda x: x['similarity'], reverse=True)
            results = results[:limit]
            
            # Сохраняем в кэш
            if use_cache and results:
                try:
                    expires_at = datetime.utcnow() + timedelta(hours=self.cache_ttl_hours)
                    cache_entry = RAGCache(
                        query_hash=query_hash,
                        query_text=query,
                        language=language,
                        content_filters=filters,
                        search_results=results,
                        relevance_scores=[r['similarity'] for r in results],
                        expires_at=expires_at
                    )
                    db.session.add(cache_entry)
                    db.session.commit()
                except Exception as e:
                    self.logger.warning(f"Ошибка сохранения кэша: {e}")
                    db.session.rollback()
            
            self.logger.info(f"Найдено {len(results)} релевантных результатов для запроса: {query[:50]}...")
            return results
            
        except Exception as e:
            self.logger.error(f"Ошибка семантического поиска: {e}")
            return []
    
    def generate_rag_context(self, 
                           query: str, 
                           language: str = 'en',
                           max_context_length: int = 2000,
                           **search_kwargs) -> Dict[str, Any]:
        """
        Генерирует контекст для RAG на основе семантического поиска
        
        Args:
            query: Поисковый запрос
            language: Язык
            max_context_length: Максимальная длина контекста
            **search_kwargs: Дополнительные параметры для поиска
            
        Returns:
            Словарь с контекстом и источниками
        """
        # Выполняем семантический поиск
        search_results = self.semantic_search(query, language=language, **search_kwargs)
        
        if not search_results:
            return {
                'context': '',
                'sources': [],
                'total_sources': 0,
                'query': query
            }
        
        # Формируем контекст из результатов
        context_parts = []
        sources = []
        current_length = 0
        
        for result in search_results:
            text = result['text']
            
            # Проверяем, не превышаем ли лимит
            if current_length + len(text) > max_context_length:
                if current_length == 0:  # Хотя бы один результат должен быть включен
                    text = text[:max_context_length]
                    context_parts.append(text)
                    current_length += len(text)
                break
            
            context_parts.append(text)
            current_length += len(text)
            
            # Добавляем источник
            sources.append({
                'type': result['content_type'],
                'id': result['content_id'],
                'title': result['title'],
                'similarity': result['similarity'],
                'chunk_index': result.get('chunk_index', 0)
            })
        
        context_text = '\n\n---\n\n'.join(context_parts)
        
        return {
            'context': context_text,
            'sources': sources,
            'total_sources': len(sources),
            'query': query,
            'context_length': len(context_text)
        }
    
    def cleanup_expired_cache(self) -> int:
        """Очищает истекший кэш RAG"""
        try:
            deleted_count = db.session.query(RAGCache).filter(
                RAGCache.expires_at < datetime.utcnow()
            ).delete()
            db.session.commit()
            
            self.logger.info(f"Удалено {deleted_count} истекших записей кэша")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Ошибка очистки кэша: {e}")
            db.session.rollback()
            return 0
    
    def get_content_statistics(self, language: str = 'en') -> Dict[str, Any]:
        """Получает статистику обработанного контента"""
        try:
            stats = {}
            
            # Общее количество эмбеддингов
            total_embeddings = db.session.query(ContentEmbedding).filter_by(language=language).count()
            stats['total_embeddings'] = total_embeddings
            
            # По типам контента
            for content_type in ['lesson', 'question', 'virtual_patient']:
                count = db.session.query(ContentEmbedding).filter_by(
                    language=language,
                    content_type=content_type
                ).count()
                stats[f'{content_type}_embeddings'] = count
            
            # Статистика кэша
            cache_entries = db.session.query(RAGCache).filter_by(language=language).count()
            stats['cache_entries'] = cache_entries
            
            # Последняя обработка
            latest_embedding = db.session.query(ContentEmbedding).filter_by(
                language=language
            ).order_by(ContentEmbedding.created_at.desc()).first()
            
            if latest_embedding:
                stats['last_processed'] = latest_embedding.created_at.isoformat()
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Ошибка получения статистики: {e}")
            return {} 