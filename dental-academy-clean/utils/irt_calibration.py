#!/usr/bin/env python3
"""
IRT Calibration Service
Автоматическая калибровка IRT параметров для вопросов
"""

import math
import numpy as np
import logging
from datetime import datetime, timezone
from typing import Dict, Optional, List, Tuple
from sqlalchemy import func

from models import Question, IRTParameters, DiagnosticResponse, TestAttempt, BIGDomain
from extensions import db

logger = logging.getLogger(__name__)


class IRTCalibrationService:
    """Сервис для калибровки IRT параметров"""
    
    def __init__(self):
        self.min_responses_for_calibration = 5
        self.default_difficulty = 0.0
        self.default_discrimination = 1.0
        self.default_guessing = 0.25
    
    def calibrate_question_from_responses(self, question_id: int) -> Optional[IRTParameters]:
        """
        Калибровать вопрос на основе истории ответов
        
        Args:
            question_id: ID вопроса для калибровки
            
        Returns:
            IRTParameters или None если недостаточно данных
        """
        try:
            # Получаем все ответы на этот вопрос
            responses = self._get_all_responses_for_question(question_id)
            
            if len(responses) < self.min_responses_for_calibration:
                logger.info(f"Question {question_id}: insufficient responses ({len(responses)}), using defaults")
                return self._create_default_parameters(question_id)
            
            # Рассчитываем базовую статистику
            correct_count = sum(1 for r in responses if r['is_correct'])
            total_count = len(responses)
            correct_rate = correct_count / total_count
            
            # Рассчитываем IRT параметры
            difficulty = self._calculate_difficulty_from_rate(correct_rate)
            discrimination = self._calculate_discrimination_from_responses(responses)
            guessing = self._calculate_guessing_from_question(question_id)
            
            # Создаем IRT параметры
            irt_params = IRTParameters(
                question_id=question_id,
                difficulty=difficulty,
                discrimination=discrimination,
                guessing=guessing,
                calibration_date=datetime.now(timezone.utc),
                calibration_sample_size=total_count
            )
            
            # Сохраняем в базу
            db.session.add(irt_params)
            db.session.commit()
            
            logger.info(f"Question {question_id}: calibrated with {total_count} responses "
                       f"(difficulty={difficulty:.3f}, discrimination={discrimination:.3f}, guessing={guessing:.3f})")
            
            return irt_params
            
        except Exception as e:
            logger.error(f"Error calibrating question {question_id}: {str(e)}")
            return self._create_default_parameters(question_id)
    
    def _get_all_responses_for_question(self, question_id: int) -> List[Dict]:
        """Получить все ответы на вопрос из разных источников"""
        responses = []
        
        # Ответы из диагностических сессий
        diag_responses = DiagnosticResponse.query.filter_by(question_id=question_id).all()
        for resp in diag_responses:
            responses.append({
                'is_correct': resp.is_correct,
                'response_time': resp.response_time,
                'source': 'diagnostic'
            })
        
        # Ответы из тестов
        test_responses = TestAttempt.query.filter_by(question_id=question_id).all()
        for resp in test_responses:
            responses.append({
                'is_correct': resp.is_correct,
                'response_time': None,
                'source': 'test'
            })
        
        return responses
    
    def _calculate_difficulty_from_rate(self, correct_rate: float) -> float:
        """
        Рассчитать сложность из процента правильных ответов
        
        Args:
            correct_rate: Процент правильных ответов (0.0 - 1.0)
            
        Returns:
            IRT difficulty parameter
        """
        # Обрабатываем крайние случаи
        if correct_rate <= 0.05:
            return 3.0  # Очень сложный
        elif correct_rate >= 0.95:
            return -3.0  # Очень легкий
        
        # Логит трансформация: b = -ln(p/(1-p))
        difficulty = -math.log(correct_rate / (1 - correct_rate))
        
        # Ограничиваем диапазон
        return np.clip(difficulty, -3.0, 3.0)
    
    def _calculate_discrimination_from_responses(self, responses: List[Dict]) -> float:
        """
        Рассчитать дискриминацию на основе характеристик вопроса
        
        Args:
            responses: Список ответов
            
        Returns:
            IRT discrimination parameter
        """
        # Базовая дискриминация
        base_discrimination = 1.0
        
        # Получаем вопрос для анализа характеристик
        question = Question.query.get(responses[0]['question_id']) if responses else None
        if question:
            # Корректируем на основе домена
            domain_factors = {
                'MED': 1.2,    # Медицинская этика - высокая дискриминация
                'ANAT': 0.9,   # Анатомия - средняя
                'PHARMA': 1.1, # Фармакология - выше средней
                'PATH': 1.15,  # Патология - высокая
                'THER': 1.1,   # Терапевтическая стоматология
                'SURG': 1.05,  # Хирургическая стоматология
                'ORTH': 1.0,   # Ортодонтия
                'PEDO': 0.95,  # Детская стоматология
                'PERI': 1.1,   # Пародонтология
                'ENDO': 1.15,  # Эндодонтия
                'RAD': 1.0,    # Рентгенология
                'PHAR': 1.1,   # Фармакология
                'COMM': 1.2,   # Коммуникация
            }
            
            if question.domain in domain_factors:
                base_discrimination *= domain_factors[question.domain]
            
            # Корректируем на основе типа вопроса
            if hasattr(question, 'question_type'):
                if question.question_type == 'clinical_case':
                    base_discrimination *= 1.1  # Клинические случаи более дискриминативны
                elif question.question_type == 'theory':
                    base_discrimination *= 0.95  # Теоретические вопросы менее дискриминативны
        
        # Добавляем небольшую случайную вариацию
        discrimination = base_discrimination + np.random.normal(0, 0.1)
        
        # Ограничиваем диапазон
        return np.clip(discrimination, 0.5, 2.5)
    
    def _calculate_guessing_from_question(self, question_id: int) -> float:
        """
        Рассчитать параметр угадывания на основе характеристик вопроса
        
        Args:
            question_id: ID вопроса
            
        Returns:
            IRT guessing parameter
        """
        question = Question.query.get(question_id)
        if not question:
            return self.default_guessing
        
        # Базовая вероятность угадывания для множественного выбора
        base_guessing = 0.25
        
        # Корректируем на основе количества вариантов
        if hasattr(question, 'options') and question.options:
            num_options = len(question.options)
            if num_options == 2:
                base_guessing = 0.5
            elif num_options == 3:
                base_guessing = 0.33
            elif num_options == 4:
                base_guessing = 0.25
            elif num_options == 5:
                base_guessing = 0.2
            else:
                base_guessing = 1.0 / num_options
        
        # Корректируем на основе типа вопроса
        if hasattr(question, 'question_type'):
            if question.question_type == 'clinical_case':
                base_guessing *= 0.8  # Клинические случаи имеют меньшее угадывание
            elif question.question_type == 'theory':
                base_guessing *= 1.1  # Теоретические вопросы имеют большее угадывание
        
        # Добавляем небольшую случайную вариацию
        guessing = base_guessing + np.random.normal(0, 0.02)
        
        # Ограничиваем диапазон
        return np.clip(guessing, 0.05, 0.5)
    
    def _create_default_parameters(self, question_id: int) -> IRTParameters:
        """
        Создать параметры по умолчанию для вопроса
        
        Args:
            question_id: ID вопроса
            
        Returns:
            IRTParameters с дефолтными значениями
        """
        irt_params = IRTParameters(
            question_id=question_id,
            difficulty=self.default_difficulty,
            discrimination=self.default_discrimination,
            guessing=self.default_guessing,
            calibration_date=datetime.now(timezone.utc),
            calibration_sample_size=0
        )
        
        db.session.add(irt_params)
        db.session.commit()
        
        logger.info(f"Question {question_id}: created default parameters")
        return irt_params
    
    def batch_calibrate_domain(self, domain_code: str) -> Dict[str, int]:
        """
        Пакетная калибровка всех вопросов домена
        
        Args:
            domain_code: Код домена
            
        Returns:
            Статистика калибровки
        """
        try:
            # Получаем домен
            domain = BIGDomain.query.filter_by(code=domain_code).first()
            if not domain:
                logger.error(f"Domain {domain_code} not found")
                return {'success': False, 'error': 'Domain not found'}
            
            # Получаем все вопросы домена без IRT параметров
            questions_without_irt = db.session.query(Question).outerjoin(IRTParameters).filter(
                Question.big_domain_id == domain.id,
                IRTParameters.id.is_(None)
            ).all()
            
            logger.info(f"Found {len(questions_without_irt)} questions without IRT parameters in domain {domain_code}")
            
            calibrated_count = 0
            default_count = 0
            
            for question in questions_without_irt:
                irt_params = self.calibrate_question_from_responses(question.id)
                if irt_params and irt_params.calibration_sample_size > 0:
                    calibrated_count += 1
                else:
                    default_count += 1
            
            return {
                'success': True,
                'domain': domain_code,
                'total_questions': len(questions_without_irt),
                'calibrated': calibrated_count,
                'defaults': default_count
            }
            
        except Exception as e:
            logger.error(f"Error batch calibrating domain {domain_code}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_calibration_statistics(self) -> Dict:
        """
        Получить статистику калибровки по всем доменам
        
        Returns:
            Статистика калибровки
        """
        try:
            # Общая статистика
            total_questions = Question.query.count()
            questions_with_irt = IRTParameters.query.count()
            questions_without_irt = total_questions - questions_with_irt
            
            # Статистика по доменам
            domain_stats = {}
            domains = BIGDomain.query.filter_by(is_active=True).all()
            
            for domain in domains:
                domain_questions = Question.query.filter_by(big_domain_id=domain.id).count()
                domain_with_irt = db.session.query(Question).join(IRTParameters).filter(
                    Question.big_domain_id == domain.id
                ).count()
                
                domain_stats[domain.code] = {
                    'name': domain.name,
                    'total_questions': domain_questions,
                    'with_irt': domain_with_irt,
                    'without_irt': domain_questions - domain_with_irt,
                    'coverage_percent': round((domain_with_irt / domain_questions * 100) if domain_questions > 0 else 0, 1)
                }
            
            return {
                'total_questions': total_questions,
                'questions_with_irt': questions_with_irt,
                'questions_without_irt': questions_without_irt,
                'overall_coverage_percent': round((questions_with_irt / total_questions * 100) if total_questions > 0 else 0, 1),
                'domain_statistics': domain_stats
            }
            
        except Exception as e:
            logger.error(f"Error getting calibration statistics: {str(e)}")
            return {'error': str(e)}


# Глобальный экземпляр сервиса
calibration_service = IRTCalibrationService() 