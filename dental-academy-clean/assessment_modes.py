#!/usr/bin/env python3
"""
Режимы работы диагностической системы
ASSESSMENT MODE: только диагностика уровня знаний
LEARNING MODE: показ вопросов с объяснениями БЕЗ влияния на диагностику
"""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timezone
from sqlalchemy import and_, or_

from extensions import db
from models import (
    User, Question, DiagnosticSession, DiagnosticResponse, 
    IRTParameters, Specialty, SpecialtyDomain
)
from utils.irt_engine import IRTEngine
from utils.adaptive_question_selector import AdaptiveQuestionSelector

logger = logging.getLogger(__name__)


class AssessmentMode:
    """Чистая диагностика знаний с IRT оценкой"""
    
    def __init__(self, specialty_id: int):
        self.specialty_id = specialty_id
        self.irt_engine = IRTEngine()
        self.adaptive_selector = AdaptiveQuestionSelector()
        self.specialty = Specialty.query.get(specialty_id)
        
        if not self.specialty:
            raise ValueError(f"Specialty {specialty_id} not found")
        
        if not self.specialty.is_calibrated:
            raise ValueError(f"Specialty {self.specialty.code} is not yet calibrated")
    
    def start_diagnostic_session(self, user_id: int, session_type: str = 'diagnostic') -> DiagnosticSession:
        """Начать диагностическую сессию"""
        try:
            # Проверяем, нет ли активной сессии
            active_session = DiagnosticSession.query.filter_by(
                user_id=user_id,
                specialty_id=self.specialty_id,
                status='active'
            ).first()
            
            if active_session:
                logger.warning(f"User {user_id} already has active session {active_session.id}")
                return active_session
            
            # Создаем новую сессию
            session = DiagnosticSession(
                user_id=user_id,
                specialty_id=self.specialty_id,
                assessment_mode='assessment',
                session_type=session_type,
                current_ability=0.0,  # Начальная оценка способности
                ability_se=1.0,       # Начальная стандартная ошибка
                status='active'
            )
            
            db.session.add(session)
            db.session.commit()
            
            logger.info(f"Started assessment session {session.id} for user {user_id}, specialty {self.specialty.code}")
            return session
            
        except Exception as e:
            logger.error(f"Error starting assessment session: {str(e)}")
            db.session.rollback()
            raise
    
    def select_next_question(self, session: DiagnosticSession) -> Optional[Question]:
        """Выбрать следующий вопрос для диагностики"""
        try:
            # Получаем только калиброванные вопросы
            calibrated_questions = Question.query.filter(
                and_(
                    Question.specialty_id == self.specialty_id,
                    Question.is_calibrated == True,
                    Question.calibration_status == 'calibrated'
                )
            ).all()
            
            if not calibrated_questions:
                logger.error(f"No calibrated questions found for specialty {self.specialty_id}")
                return None
            
            # Исключаем уже отвеченные вопросы
            answered_question_ids = [r.question_id for r in session.responses.all()]
            available_questions = [q for q in calibrated_questions if q.id not in answered_question_ids]
            
            if not available_questions:
                logger.info(f"No more questions available for session {session.id}")
                return None
            
            # Используем адаптивный алгоритм выбора
            selected_question = self.adaptive_selector.select_optimal_question(
                session, available_questions
            )
            
            if selected_question:
                # Обновляем текущий вопрос в сессии
                session.current_question_id = selected_question.id
                db.session.commit()
                
                logger.info(f"Selected question {selected_question.id} for session {session.id}")
            
            return selected_question
            
        except Exception as e:
            logger.error(f"Error selecting next question: {str(e)}")
            return None
    
    def process_response(self, session: DiagnosticSession, question_id: int, 
                        selected_answer: str, response_time: float) -> DiagnosticResponse:
        """Обработать ответ пользователя"""
        try:
            question = Question.query.get(question_id)
            if not question:
                raise ValueError(f"Question {question_id} not found")
            
            # Проверяем правильность ответа
            is_correct = selected_answer == question.correct_answer_text
            
            # Сохраняем текущие значения способности
            ability_before = session.current_ability
            se_before = session.ability_se
            
            # Обновляем IRT способность
            ability_after, se_after = self.irt_engine.update_ability_estimate(
                session, question_id, is_correct
            )
            
            # Создаем запись ответа
            response = DiagnosticResponse(
                session_id=session.id,
                question_id=question_id,
                selected_answer=selected_answer,
                is_correct=is_correct,
                response_time=response_time,
                ability_before=ability_before,
                ability_after=ability_after,
                se_before=se_before,
                se_after=se_after,
                specialty_id=self.specialty_id,
                response_mode='assessment'
            )
            
            # Рассчитываем информацию от вопроса
            irt_params = question.get_irt_parameters()
            if irt_params['calibrated']:
                item_info = self.irt_engine.calculate_item_information(
                    ability_after, 
                    irt_params['difficulty'],
                    irt_params['discrimination'],
                    irt_params['guessing']
                )
                response.item_information = item_info
                
                # Рассчитываем ожидаемую вероятность правильного ответа
                expected_prob = self.irt_engine.calculate_3pl_probability(
                    ability_after,
                    irt_params['difficulty'],
                    irt_params['discrimination'],
                    irt_params['guessing']
                )
                response.expected_response = expected_prob
            
            db.session.add(response)
            
            # Обновляем статистику сессии
            session.questions_answered += 1
            if is_correct:
                session.correct_answers += 1
            
            # Обновляем способность в сессии
            session.current_ability = ability_after
            session.ability_se = se_after
            
            # Добавляем в историю способности
            session.add_ability_estimate(ability_after, se_after, question_id)
            
            db.session.commit()
            
            logger.info(f"Processed response for session {session.id}, question {question_id}: "
                       f"{'correct' if is_correct else 'incorrect'}, ability: {ability_after:.3f}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing response: {str(e)}")
            db.session.rollback()
            raise
    
    def check_termination_criteria(self, session: DiagnosticSession) -> Tuple[bool, str]:
        """Проверить критерии завершения диагностики"""
        try:
            # Критерий 1: Достигнута достаточная точность
            if session.ability_se <= 0.3:
                return True, "precision_reached"
            
            # Критерий 2: Максимальное количество вопросов
            max_questions = 50  # Можно настроить
            if session.questions_answered >= max_questions:
                return True, "max_questions"
            
            # Критерий 3: Время сессии (если установлено)
            if session.time_limit:
                elapsed_time = (datetime.now(timezone.utc) - session.started_at).total_seconds() / 60
                if elapsed_time >= session.time_limit:
                    return True, "time_limit"
            
            # Критерий 4: Нет доступных вопросов
            available_questions = self._get_available_questions_count(session)
            if available_questions == 0:
                return True, "no_more_questions"
            
            return False, "continue"
            
        except Exception as e:
            logger.error(f"Error checking termination criteria: {str(e)}")
            return False, "error"
    
    def complete_session(self, session: DiagnosticSession) -> Dict:
        """Завершить диагностическую сессию"""
        try:
            # Завершаем сессию
            session.status = 'completed'
            session.completed_at = datetime.now(timezone.utc)
            session.termination_reason = "completed"
            
            # Генерируем результаты
            results = self._generate_diagnostic_results(session)
            
            # Сохраняем результаты в сессии
            session.percentile_rank = results['percentile_rank']
            session.set_category_scores(results['category_scores'])
            session.results_generated = True
            
            db.session.commit()
            
            logger.info(f"Completed assessment session {session.id} for user {session.user_id}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error completing session: {str(e)}")
            db.session.rollback()
            raise
    
    def _get_available_questions_count(self, session: DiagnosticSession) -> int:
        """Получить количество доступных вопросов"""
        answered_question_ids = [r.question_id for r in session.responses.all()]
        
        available_count = Question.query.filter(
            and_(
                Question.specialty_id == self.specialty_id,
                Question.is_calibrated == True,
                ~Question.id.in_(answered_question_ids)
            )
        ).count()
        
        return available_count
    
    def _generate_diagnostic_results(self, session: DiagnosticSession) -> Dict:
        """Генерировать результаты диагностики"""
        from utils.diagnostic_results import DiagnosticResults
        
        results_generator = DiagnosticResults(session)
        return results_generator.generate_comprehensive_report()


class LearningMode:
    """Режим обучения БЕЗ влияния на диагностику"""
    
    def __init__(self, specialty_id: int):
        self.specialty_id = specialty_id
        self.specialty = Specialty.query.get(specialty_id)
        
        if not self.specialty:
            raise ValueError(f"Specialty {specialty_id} not found")
    
    def get_learning_questions(self, domain_code: str = None, limit: int = 10) -> List[Question]:
        """Получить вопросы для обучения"""
        try:
            query = Question.query.filter_by(specialty_id=self.specialty_id)
            
            if domain_code:
                # Фильтруем по домену специальности
                query = query.join(SpecialtyDomain).filter(
                    SpecialtyDomain.domain_code == domain_code
                )
            
            # Сортируем по сложности (от простых к сложным)
            questions = query.order_by(Question.difficulty_level.asc()).limit(limit).all()
            
            logger.info(f"Retrieved {len(questions)} learning questions for specialty {self.specialty.code}")
            return questions
            
        except Exception as e:
            logger.error(f"Error getting learning questions: {str(e)}")
            return []
    
    def get_question_with_explanation(self, question_id: int) -> Optional[Dict]:
        """Показать вопрос с объяснением"""
        try:
            question = Question.query.get(question_id)
            if not question:
                return None
            
            # Проверяем, что вопрос принадлежит правильной специальности
            if question.specialty_id != self.specialty_id:
                logger.warning(f"Question {question_id} doesn't belong to specialty {self.specialty_id}")
                return None
            
            return {
                'question': question,
                'show_explanation': True,
                'learning_mode': True,
                'no_scoring': True,  # Не влияет на диагностику
                'specialty': self.specialty.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Error getting question with explanation: {str(e)}")
            return None
    
    def get_domain_questions(self, domain_code: str, limit: int = 20) -> List[Question]:
        """Получить вопросы по конкретному домену"""
        try:
            questions = Question.query.join(SpecialtyDomain).filter(
                and_(
                    Question.specialty_id == self.specialty_id,
                    SpecialtyDomain.domain_code == domain_code
                )
            ).order_by(Question.difficulty_level.asc()).limit(limit).all()
            
            return questions
            
        except Exception as e:
            logger.error(f"Error getting domain questions: {str(e)}")
            return []
    
    def get_available_domains(self) -> List[Dict]:
        """Получить доступные домены для обучения"""
        try:
            domains = SpecialtyDomain.query.filter_by(specialty_id=self.specialty_id).all()
            
            return [{
                'code': domain.domain_code,
                'name': domain.domain_name,
                'name_en': domain.domain_name_en,
                'name_nl': domain.domain_name_nl,
                'category': domain.category,
                'question_count': domain.question_count,
                'is_critical': domain.is_critical
            } for domain in domains]
            
        except Exception as e:
            logger.error(f"Error getting available domains: {str(e)}")
            return []


class PilotMode:
    """Режим пилотирования для калибровки вопросов"""
    
    def __init__(self, specialty_id: int):
        self.specialty_id = specialty_id
        self.specialty = Specialty.query.get(specialty_id)
        self.irt_engine = IRTEngine()
        
        if not self.specialty:
            raise ValueError(f"Specialty {specialty_id} not found")
    
    def start_pilot_session(self, user_id: int) -> DiagnosticSession:
        """Начать пилотную сессию"""
        try:
            session = DiagnosticSession(
                user_id=user_id,
                specialty_id=self.specialty_id,
                assessment_mode='assessment',
                session_type='pilot',
                current_ability=0.0,
                ability_se=1.0,
                status='active'
            )
            
            db.session.add(session)
            db.session.commit()
            
            logger.info(f"Started pilot session {session.id} for user {user_id}")
            return session
            
        except Exception as e:
            logger.error(f"Error starting pilot session: {str(e)}")
            db.session.rollback()
            raise
    
    def select_pilot_questions(self, session: DiagnosticSession, limit: int = 20) -> List[Question]:
        """Выбрать вопросы для пилотирования"""
        try:
            # Приоритет некалиброванным вопросам с наименьшим количеством ответов
            questions = Question.query.filter(
                and_(
                    Question.specialty_id == self.specialty_id,
                    Question.is_calibrated == False
                )
            ).order_by(Question.response_count.asc()).limit(limit).all()
            
            return questions
            
        except Exception as e:
            logger.error(f"Error selecting pilot questions: {str(e)}")
            return []
    
    def collect_pilot_data(self, session: DiagnosticSession, question_id: int, 
                          is_correct: bool, response_time: float):
        """Собрать данные для калибровки"""
        try:
            from models import PilotResponse
            
            question = Question.query.get(question_id)
            if not question:
                raise ValueError(f"Question {question_id} not found")
            
            # Обновляем статистику вопроса
            question.update_response_stats(is_correct)
            
            # Создаем запись пилотного ответа
            pilot_response = PilotResponse(
                question_id=question_id,
                user_id=session.user_id,
                specialty_id=self.specialty_id,
                is_correct=is_correct,
                response_time=response_time,
                user_ability=session.current_ability
            )
            
            db.session.add(pilot_response)
            db.session.commit()
            
            # Проверяем, готов ли вопрос к калибровке
            if question.response_count >= self.specialty.calibration_threshold:
                self._trigger_calibration(question_id)
            
            logger.info(f"Collected pilot data for question {question_id}: "
                       f"{'correct' if is_correct else 'incorrect'}")
            
        except Exception as e:
            logger.error(f"Error collecting pilot data: {str(e)}")
            db.session.rollback()
            raise
    
    def _trigger_calibration(self, question_id: int):
        """Запустить калибровку вопроса"""
        try:
            from utils.irt_calibration import IRTCalibrationService
            
            calibration_service = IRTCalibrationService()
            irt_params = calibration_service.calibrate_question_from_responses(question_id)
            
            if irt_params:
                # Обновляем статус вопроса
                question = Question.query.get(question_id)
                question.is_calibrated = True
                question.calibration_status = 'calibrated'
                
                # Обновляем счетчики специальности
                self.specialty.calibrated_questions += 1
                
                # Проверяем, готова ли специальность к адаптивному тестированию
                if self.specialty.calibrated_questions >= 50:
                    self.specialty.is_calibrated = True
                
                db.session.commit()
                
                logger.info(f"Question {question_id} calibrated successfully")
            
        except Exception as e:
            logger.error(f"Error triggering calibration: {str(e)}")
            db.session.rollback()


