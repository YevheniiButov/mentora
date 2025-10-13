# utils/irt_engine.py - IRT Engine for Adaptive Testing
# Professional implementation for BI-toets diagnostic testing

import math
import numpy as np
import logging
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timezone
from extensions import db
from models import Question, DiagnosticSession, DiagnosticResponse, BIGDomain
from models import IRTParameters # Added missing import
from utils.metrics import record_fallback_usage, record_error

# Добавляем импорты для оптимизации
from utils.cache_manager import get_cached_question, get_cached_irt_parameters, get_cached_domain_questions
from utils.performance_optimizer import profile_function, performance_optimizer

logger = logging.getLogger(__name__)

def validate_irt_parameters_for_calculation(difficulty: float, discrimination: float, guessing: float) -> Tuple[bool, str]:
    """
    Валидация IRT параметров перед использованием в расчетах
    
    Args:
        difficulty: Параметр сложности
        discrimination: Параметр дискриминации
        guessing: Параметр угадывания
        
    Returns:
        (is_valid, error_message)
    """
    # Проверка difficulty
    if not (-5.0 <= difficulty <= 5.0):
        return False, f"Difficulty out of valid range: {difficulty} (expected: -5.0 to 5.0)"
    
    # Проверка discrimination
    if not (0.1 <= discrimination <= 4.0):
        return False, f"Discrimination out of valid range: {discrimination} (expected: 0.1 to 4.0)"
    
    # Проверка guessing
    if not (0.0 <= guessing <= 0.5):
        return False, f"Guessing out of valid range: {guessing} (expected: 0.0 to 0.5)"
    
    # Проверка логической консистентности
    if discrimination < 0.3:
        return False, f"Very low discrimination: {discrimination} (may cause numerical issues)"
    
    if guessing > 0.4:
        return False, f"Very high guessing: {guessing} (may cause numerical issues)"
    
    return True, ""


def safe_3pl_probability(ability: float, difficulty: float, discrimination: float, guessing: float) -> Tuple[float, bool]:
    """
    Безопасный расчет вероятности по 3PL модели с валидацией
    
    Args:
        ability: Способность пользователя
        difficulty: Сложность вопроса
        discrimination: Дискриминация вопроса
        guessing: Параметр угадывания
        
    Returns:
        (probability, is_valid)
    """
    try:
        # Валидация входных параметров
        is_valid, error_msg = validate_irt_parameters_for_calculation(difficulty, discrimination, guessing)
        if not is_valid:
            logger.warning(f"Invalid IRT parameters in 3PL calculation: {error_msg}")
            return guessing, False  # Возвращаем guessing как fallback
        
        # Валидация ability
        if not (-4.0 <= ability <= 4.0):
            logger.warning(f"Ability out of valid range: {ability}")
            ability = max(-4.0, min(4.0, ability))  # Ограничиваем ability
        
        # Расчет вероятности
        exponent = discrimination * (ability - difficulty)
        
        # Защита от переполнения
        if exponent > 700:  # exp(700) слишком большое число
            probability = guessing
        elif exponent < -700:  # exp(-700) слишком маленькое число
            probability = guessing + (1 - guessing)
        else:
            probability = guessing + (1 - guessing) / (1 + math.exp(-exponent))
        
        # Проверка результата
        if not (0.0 <= probability <= 1.0):
            logger.warning(f"Invalid probability calculated: {probability}")
            probability = max(0.0, min(1.0, probability))
        
        return probability, True
        
    except Exception as e:
        logger.error(f"Error in 3PL probability calculation: {e}")
        return guessing, False


def safe_ability_estimation(responses: List[Dict], initial_ability: float = 0.0) -> Tuple[float, float, bool]:
    """
    Безопасная оценка способности с валидацией данных
    
    Args:
        responses: Список ответов с IRT параметрами
        initial_ability: Начальная оценка способности
        
    Returns:
        (ability, standard_error, is_valid)
    """
    try:
        if not responses:
            logger.warning("No responses provided for ability estimation")
            return initial_ability, 1.0, False
        
        # Валидация ответов
        valid_responses = []
        for i, response in enumerate(responses):
            if 'irt_params' not in response:
                logger.warning(f"Response {i} missing IRT parameters")
                continue
            
            irt_params = response['irt_params']
            required_fields = ['difficulty', 'discrimination', 'guessing']
            
            if not all(field in irt_params for field in required_fields):
                logger.warning(f"Response {i} missing required IRT fields")
                continue
            
            # Валидация IRT параметров
            is_valid, error_msg = validate_irt_parameters_for_calculation(
                irt_params['difficulty'],
                irt_params['discrimination'],
                irt_params['guessing']
            )
            
            if not is_valid:
                logger.warning(f"Response {i} has invalid IRT parameters: {error_msg}")
                continue
            
            valid_responses.append(response)
        
        if not valid_responses:
            logger.warning("No valid responses for ability estimation")
            return initial_ability, 1.0, False
        
        # Используем только валидные ответы для оценки
        ability = initial_ability
        max_iterations = 50
        tolerance = 0.001
        
        for iteration in range(max_iterations):
            prev_ability = ability
            
            # Расчет первой и второй производных логарифма правдоподобия
            first_derivative = 0.0
            second_derivative = 0.0
            
            for response in valid_responses:
                irt_params = response['irt_params']
                is_correct = response['is_correct']
                
                # Безопасный расчет вероятности
                probability, prob_valid = safe_3pl_probability(
                    ability,
                    irt_params['difficulty'],
                    irt_params['discrimination'],
                    irt_params['guessing']
                )
                
                if not prob_valid:
                    continue
                
                # Расчет производных
                if probability > 0 and probability < 1:
                    first_derivative += irt_params['discrimination'] * (is_correct - probability)
                    second_derivative -= irt_params['discrimination'] ** 2 * probability * (1 - probability)
            
            # Проверка сходимости
            if abs(second_derivative) < 1e-10:
                logger.warning("Second derivative too small, stopping iteration")
                break
            
            # Обновление оценки способности
            ability_change = first_derivative / second_derivative
            ability -= ability_change
            
            # Ограничение ability
            ability = max(-4.0, min(4.0, ability))
            
            # Проверка сходимости
            if abs(ability - prev_ability) < tolerance:
                break
        
        # Расчет стандартной ошибки
        if abs(second_derivative) > 1e-10:
            standard_error = 1.0 / math.sqrt(-second_derivative)
        else:
            standard_error = 1.0
        
        # Ограничение стандартной ошибки
        standard_error = max(0.1, min(2.0, standard_error))
        
        return ability, standard_error, True
        
    except Exception as e:
        logger.error(f"Error in ability estimation: {e}")
        return initial_ability, 1.0, False

class IRTEngine:
    """IRT Engine for 3PL model adaptive testing with domain support"""
    
    def __init__(self, session: Optional[DiagnosticSession] = None, diagnostic_type: str = 'express'):
        self.session = session
        self.max_iterations = 50
        self.convergence_threshold = 0.001
        self.min_se_threshold = 0.4  # Увеличен порог стандартной ошибки для завершения
        
        # Настройки в зависимости от типа диагностики
        self.diagnostic_type = diagnostic_type
        
        if diagnostic_type == 'quick_30':
            # Quick Test: 30 вопросов
            self.questions_per_domain = 1
            self.max_questions = 30
        elif diagnostic_type == 'full_60':
            # Full Test: 60 вопросов
            self.questions_per_domain = 2
            self.max_questions = 60
        elif diagnostic_type == 'learning_30' or diagnostic_type == 'learning':
            # Learning Mode: 30 вопросов с объяснениями
            self.questions_per_domain = 1
            self.max_questions = 30
        # Legacy support
        elif diagnostic_type == 'express':
            self.questions_per_domain = 1
            self.max_questions = 30
        elif diagnostic_type == 'preliminary':
            self.questions_per_domain = 2
            self.max_questions = 60
        elif diagnostic_type == 'full':
            self.questions_per_domain = 2
            self.max_questions = 60
        elif diagnostic_type == 'readiness':
            self.questions_per_domain = 6
            self.max_questions = 130
        elif diagnostic_type == 'comprehensive':
            self.questions_per_domain = 6
            self.max_questions = 130
        else:
            # По умолчанию quick_30
            self.diagnostic_type = 'quick_30'
            self.questions_per_domain = 1
            self.max_questions = 30
        
        # Ленивая загрузка доменов
        self._all_domains = None
        self._domain_weights = None
        self._min_questions = None
    
    def load_all_domains(self) -> Dict[str, BIGDomain]:
        """Загрузить все активные домены"""
        domains = BIGDomain.query.filter_by(is_active=True).all()
        return {domain.code: domain for domain in domains}
    
    @property
    def all_domains(self) -> Dict[str, BIGDomain]:
        """Ленивая загрузка всех доменов"""
        if self._all_domains is None:
            self._all_domains = self.load_all_domains()
        return self._all_domains
    
    @property
    def domain_weights(self) -> Dict[str, float]:
        """Ленивая загрузка весов доменов"""
        if self._domain_weights is None:
            self._domain_weights = {domain.code: domain.weight_percentage for domain in self.all_domains.values()}
        return self._domain_weights
    
    @property
    def min_questions(self) -> int:
        """Ленивый расчет минимального количества вопросов"""
        if self._min_questions is None:
            # Рассчитываем минимальное количество вопросов
            calculated_min = len(self.all_domains) * self.questions_per_domain
            
            # ИСПРАВЛЕНИЕ: Если доменов нет, используем фиксированные минимумы
            if calculated_min == 0:
                if self.diagnostic_type in ['quick_30', 'express', 'learning_30', 'learning']:
                    calculated_min = 25  # Минимум 25 для быстрых тестов (target 30)
                elif self.diagnostic_type in ['full_60', 'preliminary', 'full']:
                    calculated_min = 50  # Минимум 50 для полных тестов (target 60)
                elif self.diagnostic_type in ['readiness', 'comprehensive']:
                    calculated_min = 100  # Минимум 100 для readiness (target 130)
                else:
                    calculated_min = 25  # По умолчанию 25
                logger.warning(f"No domains found, using default min questions: {calculated_min}")
            
            # Но не больше максимального количества вопросов
            self._min_questions = min(calculated_min, self.max_questions)
            logger.info(f"Min questions calculated: {calculated_min}, but limited to max_questions: {self._min_questions}")
        return self._min_questions
    
    def load_domain_weights(self) -> Dict[str, float]:
        """Загрузить веса доменов для приоритизации"""
        return {domain.code: domain.weight_percentage for domain in self.all_domains.values()}
    
    # Оптимизируем метод get_domain_questions с кэшированием
    def get_domain_questions(self, domain_code: str, difficulty_range: Optional[Tuple[float, float]] = None, limit: int = 100) -> List[Question]:
        """Получить вопросы для конкретного домена с оптимизацией производительности"""
        logger.info(f"=== get_domain_questions called for domain: {domain_code} ===")
        
        # Сначала пробуем получить из кэша
        cached_questions = get_cached_domain_questions(domain_code, difficulty_range)
        if cached_questions:
            logger.info(f"Cache hit for domain questions: {domain_code}, returning {len(cached_questions)} questions")
            return cached_questions[:limit]
        
        # Если нет в кэше, загружаем из базы данных
        logger.info(f"Cache miss for domain: {domain_code}, loading from database...")
        from utils.performance_optimizer import performance_optimizer
        query_optimizer = performance_optimizer.query_optimizer
        
        try:
            questions = query_optimizer.optimize_question_query(domain_code, difficulty_range)
            logger.info(f"Loaded {len(questions)} questions for domain {domain_code} from database")
            
            # Проверяем состояние объектов
            for i, question in enumerate(questions[:3]):  # Проверяем первые 3
                logger.info(f"Question {i}: id={question.id}, session_state={db.session.object_session(question)}")
            
            return questions[:limit]
        except Exception as e:
            logger.error(f"Error loading questions for domain {domain_code}: {e}")
            logger.error(f"Error type: {type(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return []
    
    # Оптимизируем метод select_next_question_by_domain
    def select_next_question_by_domain(self, domain_code: str, current_ability: float = 0.0, answered_question_ids: set = None) -> Optional[Question]:
        """Выбрать следующий вопрос для конкретного домена с оптимизацией и правильным исключением отвеченных"""
        if answered_question_ids is None:
            answered_question_ids = set()
        
        try:
            # Используем оптимизированный запрос с прямым исключением отвеченных вопросов
            questions = self.get_domain_questions(domain_code)
            logger.info(f"Found {len(questions)} questions for domain {domain_code}")
            
            # Исключить уже отвеченные вопросы
            available_questions = [q for q in questions if q.id not in answered_question_ids]
            logger.info(f"Available questions after filtering: {len(available_questions)}")
            
            if not available_questions:
                logger.warning(f"No available questions for domain {domain_code} after filtering answered questions: {answered_question_ids}")
                return None
        except Exception as e:
            logger.error(f"Error selecting question for domain {domain_code}: {e}")
            return None
        
        # Детальная проверка IRT параметров с кэшированием
        questions_with_irt = []
        questions_without_irt = []
        
        for question in available_questions:
            # Убеждаемся, что объект Question привязан к session
            try:
                # Проверяем, что объект в session
                _ = question.id
            except Exception:
                # Если объект detached, получаем его заново
                from extensions import db
                question = Question.query.get(question.id)
                if not question:
                    continue
            
            # Получаем IRT параметры с правильным управлением session
            irt_params = question.irt_parameters
            
            if irt_params:
                # Убеждаемся, что объект IRTParameters привязан к session
                try:
                    # Проверяем, что объект в session
                    _ = irt_params.id
                except Exception:
                    # Если объект detached, получаем его заново
                    irt_params = IRTParameters.query.get(irt_params.id)
                
                if irt_params and irt_params.difficulty is not None:
                    questions_with_irt.append(question)
                    logger.debug(f"Question {question.id}: difficulty={irt_params.difficulty}, discrimination={irt_params.discrimination}, guessing={irt_params.guessing}")
                else:
                    questions_without_irt.append(question)
            else:
                questions_without_irt.append(question)
        
        # Приоритет вопросам с IRT параметрами
        if questions_with_irt:
            # Выбираем вопрос с оптимальной сложностью
            optimal_question = self._select_optimal_question(questions_with_irt, current_ability)
            if optimal_question:
                return optimal_question
        
        # Fallback к вопросам без IRT параметров
        if questions_without_irt:
            import random
            return random.choice(questions_without_irt)
        
        return None

    def _select_optimal_question(self, questions: List[Question], current_ability: float) -> Optional[Question]:
        """Выбрать оптимальный вопрос на основе текущей способности"""
        if not questions:
            return None
        
        # Получаем IRT параметры для всех вопросов
        questions_with_params = []
        
        for question in questions:
            # Убеждаемся, что объект Question привязан к session
            try:
                # Проверяем, что объект в session
                _ = question.id
            except Exception:
                # Если объект detached, получаем его заново
                from extensions import db
                question = Question.query.get(question.id)
                if not question:
                    continue
            
            irt_params = question.irt_parameters
            if irt_params:
                # Убеждаемся, что объект IRTParameters привязан к session
                try:
                    # Проверяем, что объект в session
                    _ = irt_params.id
                except Exception:
                    # Если объект detached, получаем его заново
                    irt_params = IRTParameters.query.get(irt_params.id)
                
                if irt_params and irt_params.difficulty is not None:
                    questions_with_params.append((question, irt_params))
        
        if not questions_with_params:
            return None
        
        # Выбираем вопрос с оптимальной сложностью
        # Предпочитаем вопросы со сложностью близкой к текущей способности
        optimal_question = None
        min_distance = float('inf')
        
        for question, irt_params in questions_with_params:
            distance = abs(irt_params.difficulty - current_ability)
            
            # Учитываем дискриминацию (предпочитаем вопросы с высокой дискриминацией)
            discrimination_factor = 1.0 / max(irt_params.discrimination, 0.1)
            adjusted_distance = distance * discrimination_factor
            
            if adjusted_distance < min_distance:
                min_distance = adjusted_distance
                optimal_question = question
        
        return optimal_question
    
    def calculate_domain_abilities(self, user_responses: List[Dict]) -> Dict[str, float]:
        """Рассчитать способности пользователя по каждому домену с улучшенной обработкой ошибок"""
        domain_abilities = {}
        
        for domain_code in self.all_domains.keys():
            domain_responses = [r for r in user_responses if r.get('domain') == domain_code]
            
            if domain_responses and len(domain_responses) >= 1:  # Минимум 1 ответ для домена
                try:
                    theta, se = self.estimate_ability(domain_responses)
                    domain_abilities[domain_code] = theta
                except Exception as e:
                    # Fallback: использовать простую пропорцию
                    correct_count = sum(1 for r in domain_responses if r.get('is_correct', False))
                    total_count = len(domain_responses)
                    if total_count > 0:
                        proportion = correct_count / total_count
                        # Простое преобразование в theta
                        domain_abilities[domain_code] = 2 * (proportion - 0.5)
                    else:
                        domain_abilities[domain_code] = 0.0
            else:
                domain_abilities[domain_code] = None  # Нет данных для домена
        
        return domain_abilities
    
    def get_domain_statistics(self, domain_code: str) -> Dict:
        """Получить статистику по домену с улучшенной обработкой ошибок"""
        domain = self.all_domains.get(domain_code)
        if not domain:
            return {}
        
        questions = self.get_domain_questions(domain_code)
        
        # Фильтровать вопросы с валидными IRT параметрами
        valid_questions = [
            q for q in questions 
            if hasattr(q, 'irt_difficulty') and q.irt_difficulty is not None
        ]
        
        if valid_questions:
            difficulties = [q.irt_difficulty for q in valid_questions]
            average_difficulty = np.mean(difficulties)
            min_difficulty = min(difficulties)
            max_difficulty = max(difficulties)
        else:
            average_difficulty = 0.0
            min_difficulty = 0.0
            max_difficulty = 0.0
        
        return {
            'code': domain_code,
            'name': domain.name,
            'description': domain.description,
            'weight': domain.weight_percentage,
            'question_count': len(questions),
            'valid_irt_questions': len(valid_questions),
            'average_difficulty': average_difficulty,
            'difficulty_range': {
                'min': min_difficulty,
                'max': max_difficulty
            }
        }
        
    # Оптимизируем метод estimate_ability с профилированием
    def estimate_ability(self, responses: List[Dict]) -> Tuple[float, float]:
        """
        Estimate ability (theta) using Maximum Likelihood Estimation (MLE) with optimization
        
        Args:
            responses: List of dicts with 'question_id', 'is_correct', 'irt_params'
            
        Returns:
            Tuple of (theta, standard_error)
        """
        # Используем безопасную функцию оценки способности
        ability, standard_error, is_valid = safe_ability_estimation(responses)
        
        if not is_valid:
            logger.warning("Ability estimation failed, using fallback values")
            return 0.0, 1.0
        
        return ability, standard_error
    
    def select_initial_question(self) -> Optional[Question]:
        """
        Select initial question for diagnostic session with improved fallback logic
        
        Returns:
            Selected question or None if no questions available
        """
        try:
            # First try: Get all questions with IRT parameters
            questions = Question.query.join(IRTParameters).all()
            logger.info(f"Found {len(questions)} questions with IRT parameters")
            
            if not questions:
                logger.warning("No questions with IRT parameters found, trying all questions")
                # Fallback: Get all questions without IRT requirement
                questions = Question.query.all()
                logger.info(f"Found {len(questions)} total questions")
                
                if not questions:
                    logger.error("No questions found in database at all")
                    return None
                
                # Return random question if no IRT parameters available
                import random
                selected = random.choice(questions)
                logger.info(f"Selected random question without IRT: {selected.id}")
                return selected
            
            # For initial question, select one with medium difficulty (close to 0)
            import random
            
            medium_difficulty_questions = []
            questions_with_irt = []
            
            for q in questions:
                try:
                    # Get IRT parameters from the relationship
                    irt_params = q.irt_parameters
                    if irt_params and irt_params.difficulty is not None:
                        questions_with_irt.append(q)
                        if -1.0 <= irt_params.difficulty <= 1.0:
                            medium_difficulty_questions.append(q)
                except Exception as e:
                    logger.warning(f"Error processing question {q.id}: {e}")
                    continue
            
            logger.info(f"Found {len(medium_difficulty_questions)} medium difficulty questions")
            logger.info(f"Found {len(questions_with_irt)} questions with IRT parameters")
            
            if medium_difficulty_questions:
                # Randomly select from medium difficulty questions
                selected = random.choice(medium_difficulty_questions)
                logger.info(f"Selected medium difficulty question: {selected.id}")
                return selected
            
            if questions_with_irt:
                # Fallback 1: select random question with any valid IRT difficulty
                selected = random.choice(questions_with_irt)
                logger.info(f"Selected question with IRT parameters: {selected.id}")
                return selected
            
            # Fallback 2: select any random question
            selected = random.choice(questions)
            logger.info(f"Selected random question: {selected.id}")
            return selected
            
        except Exception as e:
            logger.error(f"Error in select_initial_question: {e}")
            # Final fallback: try to get any question
            try:
                questions = Question.query.limit(10).all()
                if questions:
                    import random
                    selected = random.choice(questions)
                    logger.info(f"Emergency fallback - selected question: {selected.id}")
                    return selected
            except Exception as fallback_error:
                logger.error(f"Emergency fallback also failed: {fallback_error}")
            
            return None
    
    def select_next_question(self) -> Optional[Question]:
        """Выбрать следующий вопрос для адаптивного тестирования с правильным отслеживанием отвеченных вопросов"""
        logger.info("=== IRT ENGINE: select_next_question START ===")
        
        # CIRCUIT BREAKER для предотвращения рекурсии
        if not hasattr(self, '_recursion_counter'):
            self._recursion_counter = 0
        
        if self._recursion_counter > 10:
            logger.error("CIRCUIT BREAKER: Stopping recursion in select_next_question")
            self._recursion_counter = 0
            return None
        
        self._recursion_counter += 1
        
        if not self.session:
            logger.error("No session available")
            self._recursion_counter = 0
            return None
        
        try:
            # Получить все отвеченные вопросы из базы данных напрямую
            answered_questions = DiagnosticResponse.query.filter_by(
                session_id=self.session.id
            ).with_entities(DiagnosticResponse.question_id).all()
            
            answered_question_ids = {q[0] for q in answered_questions}
            logger.info(f"Session {self.session.id} already answered questions: {answered_question_ids}")
            
            # ИСПРАВЛЕНИЕ: Также добавим текущий вопрос в список отвеченных, если он есть
            if self.session.current_question_id:
                answered_question_ids.add(self.session.current_question_id)
                logger.info(f"Added current question {self.session.current_question_id} to answered questions")
            
            # Проверить, есть ли еще доступные вопросы
            total_questions = Question.query.count()
            if len(answered_question_ids) >= total_questions:
                logger.warning(f"All {total_questions} questions have been answered")
                self._recursion_counter = 0
                return None
            
            # Дополнительная проверка: убедимся, что у нас есть вопросы для выбора
            available_questions_count = Question.query.filter(
                ~Question.id.in_(answered_question_ids)
            ).count()
            
            if available_questions_count == 0:
                logger.warning(f"No available questions found. Total: {total_questions}, Answered: {len(answered_question_ids)}")
                self._recursion_counter = 0
                return None
            
            # Получить историю ответов для анализа покрытия доменов
            logger.info("About to get session responses...")
            responses = self.session.responses.all()
            logger.info(f"Found {len(responses)} responses")
            domain_question_counts = {}
            
            for i, response in enumerate(responses):
                logger.info(f"Processing response {i}: question_id={response.question_id}")
                try:
                    logger.info(f"About to access response.question...")
                    question = response.question
                    logger.info(f"Question object: {question}")
                    logger.info(f"Question session state: {db.session.object_session(question)}")
                    
                    # Используем big_domain вместо старого поля domain
                    if hasattr(question, 'big_domain') and question.big_domain:
                        logger.info(f"About to access question.big_domain...")
                        big_domain = question.big_domain
                        logger.info(f"Big domain: {big_domain}")
                        
                        logger.info(f"About to access big_domain.code...")
                        domain_code = big_domain.code
                        logger.info(f"Domain code: {domain_code}")
                        
                        domain_question_counts[domain_code] = domain_question_counts.get(domain_code, 0) + 1
                        logger.info(f"Updated domain counts: {domain_question_counts}")
                    else:
                        logger.info(f"Question {question.id} has no big_domain")
                except Exception as e:
                    logger.error(f"Error processing response {i}: {e}")
                    logger.error(f"Error type: {type(e)}")
                    import traceback
                    logger.error(f"Full traceback: {traceback.format_exc()}")
                    # Continue processing other responses
                    continue
        except Exception as e:
            logger.error(f"Error getting answered questions: {e}")
            answered_question_ids = set()
            domain_question_counts = {}
        
        # ИСПРАВЛЕНИЕ: Получить только домены с доступными вопросами
        domains_with_questions = []
        for domain_code in self.all_domains.keys():
            # Проверить, есть ли доступные вопросы в домене
            domain_questions = self.get_domain_questions(domain_code)
            available_questions = [q for q in domain_questions if q.id not in answered_question_ids]
            
            if available_questions:  # Только домены с доступными вопросами
                domains_with_questions.append(domain_code)
                logger.debug(f"Domain {domain_code} has {len(available_questions)} available questions")
            else:
                logger.debug(f"Domain {domain_code} has no available questions")
        
        if not domains_with_questions:
            logger.warning("No domains with available questions found")
            logger.info(f"Total domains: {len(self.all_domains)}")
            logger.info(f"Answered questions: {len(answered_question_ids)}")
            logger.info(f"Total questions in DB: {Question.query.count()}")
            self._recursion_counter = 0
            return None
        
        # Найти домены, которые нуждаются в дополнительных вопросах
        domains_needing_questions = []
        for domain_code in domains_with_questions:  # Только домены с вопросами
            current_count = domain_question_counts.get(domain_code, 0)
            if current_count < self.questions_per_domain:
                domains_needing_questions.append({
                    'domain': domain_code,
                    'current_count': current_count,
                    'needed_count': self.questions_per_domain - current_count,
                    'weight': self.domain_weights.get(domain_code, 0)
                })
        
        if domains_needing_questions:
            # Сортировать по весу домена (высокий приоритет) и количеству нужных вопросов
            domains_needing_questions.sort(
                key=lambda x: (x['weight'], x['needed_count']), 
                reverse=True
            )
            
            # Попробовать выбрать вопрос из доменов по приоритету
            for domain_info in domains_needing_questions:
                priority_domain = domain_info['domain']
                question = self.select_next_question_by_domain(priority_domain, self.current_ability_estimate, answered_question_ids)
                if question:
                    return question
            
            # Если не удалось выбрать из приоритетных доменов, попробовать любой домен с вопросами
            for domain_code in domains_with_questions:  # Только домены с вопросами
                question = self.select_next_question_by_domain(domain_code, self.current_ability_estimate, answered_question_ids)
                if question:
                    return question
        
        # Если все домены покрыты, использовать стандартную логику
        # Найти вопрос с оптимальной сложностью, исключая уже отвеченные
        # ИСПРАВЛЕНИЕ: Добавляем eager loading для предотвращения detached объектов
        all_questions = Question.query.options(
            db.joinedload(Question.irt_parameters),
            db.joinedload(Question.big_domain)
        ).filter(~Question.id.in_(answered_question_ids)).all()
        
        if not all_questions:
            # Если все вопросы отвечены, завершить диагностику
            self._recursion_counter = 0
            return None
        
        # Проверяем и исправляем detached объекты
        valid_questions = []
        for question in all_questions:
            try:
                # Проверяем, что объект в session
                _ = question.id
                valid_questions.append(question)
            except Exception:
                # Если объект detached, получаем его заново
                fresh_question = Question.query.get(question.id)
                if fresh_question:
                    valid_questions.append(fresh_question)
        
        if not valid_questions:
            self._recursion_counter = 0
            return None
        
        # Попробовать найти вопрос с оптимальной сложностью
        optimal_question = None
        min_distance = float('inf')
        
        for question in valid_questions:
            if not hasattr(question, 'irt_difficulty') or question.irt_difficulty is None:
                continue
                
            distance = abs(question.irt_difficulty - self.current_ability_estimate)
            
            if distance < min_distance:
                min_distance = distance
                optimal_question = question
        
        # Если не нашли вопрос с IRT параметрами, использовать fallback
        if optimal_question is None:
            # Fallback 1: попробовать найти любой вопрос с IRT параметрами
            questions_with_irt = [
                q for q in valid_questions 
                if hasattr(q, 'irt_difficulty') and q.irt_difficulty is not None
            ]
            
            if questions_with_irt:
                # Выбрать случайный вопрос с IRT параметрами
                import random
                optimal_question = random.choice(questions_with_irt)
        
            else:
                # Fallback 2: если нет вопросов с IRT параметрами, выбрать случайный
                import random
                optimal_question = random.choice(valid_questions)
        
        # СБРОС СЧЕТЧИКА РЕКУРСИИ
        self._recursion_counter = 0
        
        if optimal_question:
            logger.info(f"=== IRT ENGINE: Returning question {optimal_question.id} ===")
            logger.info(f"Question object session: {db.session.object_session(optimal_question)}")
            # Force load attributes while session is active
            try:
                _ = optimal_question.id
                _ = optimal_question.text
                _ = optimal_question.options
                logger.info("Question attributes loaded successfully")
            except Exception as e:
                logger.error(f"Error loading question attributes: {e}")
                # Try to re-fetch the question
                optimal_question = Question.query.get(optimal_question.id)
                logger.info(f"Re-fetched question: {optimal_question}")
        else:
            logger.warning("=== IRT ENGINE: No optimal question found ===")
            logger.info(f"Valid questions count: {len(valid_questions)}")
            logger.info(f"All questions count: {len(all_questions)}")
            logger.info(f"Answered questions count: {len(answered_question_ids)}")
        
        return optimal_question
    
    def should_terminate(self) -> bool:
        """Check if current session should terminate"""
        if not self.session:
            return False
        return self._check_termination_conditions(self.session)['should_terminate']
    
    @property
    def current_ability_estimate(self) -> float:
        """Get current ability estimate"""
        return self.session.current_ability if self.session else 0.0
    
    def get_confidence_interval(self) -> List[float]:
        """Get confidence interval for current ability"""
        if not self.session:
            return [0.0, 1.0]
        
        se = self.session.ability_se
        theta = self.session.current_ability
        return [theta - 1.96 * se, theta + 1.96 * se]
    
    def get_domain_abilities(self) -> Dict[str, float]:
        """Get domain-specific ability estimates"""
        if not self.session:
            return {}
        
        # Get all responses for this session
        responses = self.session.responses.all()
        if not responses:
            return {}
        
        # Группировать ответы по доменам
        domain_responses = {}
        for response in responses:
            question = response.question
            # Используем big_domain вместо старого поля domain
            if hasattr(question, 'big_domain') and question.big_domain:
                domain_code = question.big_domain.code
                if domain_code not in domain_responses:
                    domain_responses[domain_code] = []
                domain_responses[domain_code].append(response)
        
        # Рассчитать способности для каждого домена
        domain_abilities = {}
        for domain_code in self.all_domains.keys():
            if domain_code in domain_responses and domain_responses[domain_code]:
                # Есть ответы по этому домену - рассчитать процент правильных
                domain_resp_list = domain_responses[domain_code]
                correct_count = sum(1 for resp in domain_resp_list if resp.is_correct)
                total_count = len(domain_resp_list)
                domain_accuracy = correct_count / total_count
                domain_abilities[domain_code] = domain_accuracy
            else:
                # Нет ответов по этому домену - возвращаем 0.0 вместо None
                domain_abilities[domain_code] = 0.0
        
        return domain_abilities
    
    def estimate_questions_remaining(self) -> int:
        """Estimate number of questions remaining"""
        if not self.session:
            return self.max_questions
        
        # Calculate remaining based on current progress
        questions_answered = self.session.questions_answered
        
        # If we haven't reached minimum, show remaining to minimum
        if questions_answered < self.min_questions:
            return self.min_questions - questions_answered
        
        # If we've reached maximum, no more questions
        if questions_answered >= self.max_questions:
            return 0
        
        # Calculate based on current SE and precision threshold
        current_se = self.session.ability_se
        if current_se <= self.min_se_threshold:
            return 0
        elif current_se <= 0.5:
            return 5
        elif current_se <= 0.8:
            return 10
        else:
            return min(15, self.max_questions - questions_answered)
    
    def get_progress_percentage(self) -> float:
        """Get progress percentage (0-100)"""
        if not self.session:
            return 0.0
        
        # Calculate progress based on SE reduction
        initial_se = 1.0
        current_se = self.session.ability_se
        progress = (initial_se - current_se) / initial_se * 100
        return min(100.0, max(0.0, progress))
    
    def get_domain_detailed_statistics(self) -> Dict[str, Dict]:
        """
        Get detailed statistics for each domain with real IRT calculations
        
        Returns:
            Dict with domain statistics including IRT ability estimates and confidence intervals
        """
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            if not self.session:
                logger.warning("No diagnostic session provided for domain statistics")
                return {}
            
            # Get all responses for this session using SQLAlchemy query
            responses = self.session.responses.all()
            if not responses:
                logger.info(f"No responses found for session {self.session.id}")
                return self._get_default_domain_statistics()
            
            # Group responses by domain using efficient SQLAlchemy queries
            domain_responses = {}
            for response in responses:
                # Get question with domain information
                question = Question.query.get(response.question_id)
                if question and hasattr(question, 'big_domain') and question.big_domain:
                    domain_code = question.big_domain.code
                    if domain_code not in domain_responses:
                        domain_responses[domain_code] = []
                    domain_responses[domain_code].append(response)
            
            # Calculate detailed statistics for each domain
            domain_stats = {}
            for domain_code in self.all_domains.keys():
                domain = self.all_domains[domain_code]
                
                if domain_code in domain_responses and domain_responses[domain_code]:
                    # Real data available for this domain
                    domain_resp_list = domain_responses[domain_code]
                    
                    # Calculate basic statistics
                    correct_count = sum(1 for resp in domain_resp_list if resp.is_correct)
                    total_count = len(domain_resp_list)
                    accuracy = correct_count / total_count if total_count > 0 else 0.0
                    
                    # Calculate IRT ability estimate for this domain
                    irt_responses = []
                    for resp in domain_resp_list:
                        question = resp.question
                        if (question and hasattr(question, 'irt_difficulty') and 
                            question.irt_difficulty is not None):
                            irt_responses.append({
                                'question_id': resp.question_id,
                                'is_correct': resp.is_correct,
                                'irt_params': {
                                    'difficulty': question.irt_difficulty,
                                    'discrimination': question.irt_discrimination or 1.0,
                                    'guessing': question.irt_guessing or 0.25
                                }
                            })
                    
                    # Calculate IRT ability and confidence interval
                    if irt_responses and len(irt_responses) >= 1:
                        try:
                            ability_estimate, standard_error = self.estimate_ability(irt_responses)
                            confidence_interval = [
                                ability_estimate - 1.96 * standard_error,
                                ability_estimate + 1.96 * standard_error
                            ]
                        except Exception as e:
                            logger.error(f"Error calculating IRT ability for domain {domain_code}: {e}")
                            ability_estimate = None
                            standard_error = None
                            confidence_interval = None
                    else:
                        ability_estimate = None
                        standard_error = None
                        confidence_interval = None
                    
                    domain_stats[domain_code] = {
                        'name': domain.name,
                        'questions_answered': total_count,
                        'correct_answers': correct_count,
                        'accuracy': accuracy,
                        'accuracy_percentage': round(accuracy * 100, 1),
                        'has_data': True,
                        'ability_estimate': round(ability_estimate, 3) if ability_estimate is not None else None,
                        'standard_error': round(standard_error, 3) if standard_error is not None else None,
                        'confidence_interval': confidence_interval,
                        'irt_responses_count': len(irt_responses)
                    }
                else:
                    # No responses for this domain - return meaningful defaults
                    domain_stats[domain_code] = self._get_domain_default_stats(domain)
            
            logger.info(f"Generated domain statistics for {len(domain_stats)} domains")
            return domain_stats
            
        except Exception as e:
            logger.error(f"Error in get_domain_detailed_statistics: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return self._get_default_domain_statistics()
    
    def _get_domain_default_stats(self, domain) -> Dict:
        """Get meaningful default statistics for domain with no responses"""
        return {
            'name': domain.name,
            'questions_answered': 0,
            'correct_answers': 0,
            'accuracy': None,
            'accuracy_percentage': None,
            'has_data': False,
            'ability_estimate': None,
            'standard_error': None,
            'confidence_interval': None,
            'irt_responses_count': 0,
            'message': f'No diagnostic data available for {domain.name}. Complete a diagnostic test to see your performance.'
        }
    
    def _get_default_domain_statistics(self) -> Dict[str, Dict]:
        """Get default statistics for all domains when no session data is available"""
        default_stats = {}
        for domain_code, domain in self.all_domains.items():
            default_stats[domain_code] = self._get_domain_default_stats(domain)
        return default_stats
    
    def get_default_domain_statistics(self) -> Dict[str, Dict]:
        """Public method to get default statistics for all domains"""
        return self._get_default_domain_statistics()
    
    def _check_termination_conditions(self, session: DiagnosticSession) -> Dict:
        """
        Check if diagnostic session should terminate
        
        Returns:
            Dict with termination info
        """
        logger.info(f"=== CHECKING TERMINATION CONDITIONS ===")
        logger.info(f"Session ID: {session.id}")
        logger.info(f"Questions answered: {session.questions_answered}")
        logger.info(f"Diagnostic type: {self.diagnostic_type}")
        logger.info(f"Max questions: {self.max_questions}")
        logger.info(f"Min questions: {self.min_questions}")
        logger.info(f"Questions per domain: {self.questions_per_domain}")
        logger.info(f"Ability SE: {session.ability_se}")
        logger.info(f"Min SE threshold: {self.min_se_threshold}")
        
        # Получить только домены с вопросами
        domains_with_questions = []
        for domain_code in self.all_domains.keys():
            questions_count = Question.query.filter_by(big_domain_id=self.all_domains[domain_code].id).count()
            if questions_count > 0:
                domains_with_questions.append(domain_code)
        
        logger.info(f"Domains with questions: {len(domains_with_questions)}")
        
        # Проверить покрытие доменов (минимум questions_per_domain вопросов на домен)
        min_questions_per_domain = self.questions_per_domain
        total_domains_with_questions = len(domains_with_questions)
        calculated_min_total = total_domains_with_questions * min_questions_per_domain
        # Ограничиваем минимальное количество максимальным
        min_total_questions = min(calculated_min_total, self.max_questions)
        
        logger.info(f"Calculated min total questions: {calculated_min_total}")
        logger.info(f"Min total questions needed (limited): {min_total_questions}")
        
        if session.questions_answered < min_total_questions:
            logger.info(f"CONTINUE: Need more questions for domain coverage")
            return {
                'should_terminate': False,
                'reason': 'domain_coverage',
                'message': f'Need at least {min_questions_per_domain} question(s) per domain ({total_domains_with_questions} domains with questions = {min_total_questions} questions)'
            }
        
        # Check minimum questions requirement
        if session.questions_answered < self.min_questions:
            logger.info(f"CONTINUE: Need more questions (minimum not reached)")
            return {
                'should_terminate': False,
                'reason': 'min_questions',
                'message': f'Need at least {self.min_questions} questions'
            }
        
        # Check maximum questions limit
        if session.questions_answered >= self.max_questions:
            logger.info(f"TERMINATE: Maximum questions reached ({session.questions_answered} >= {self.max_questions})")
            return {
                'should_terminate': True,
                'reason': 'max_questions',
                'message': f'Maximum {self.max_questions} questions reached'
            }
        
        # Check precision threshold based on session type (ИСПРАВЛЕНИЕ: используем session_type вместо diagnostic_type)
        session_data = session.get_session_data()
        session_type = session_data.get('session_type', 'preliminary')
        diagnostic_type = session_data.get('diagnostic_type', 'preliminary')
        
        logger.info(f"Session type: {session_type}, Diagnostic type: {diagnostic_type}")
        
        # For learning sessions: Always complete all questions (no early termination)
        if session_type == 'learning':
            max_questions = session_data.get('estimated_total_questions', 30)
            if session.questions_answered >= max_questions:
                logger.info(f"TERMINATE: Learning session completed ({session.questions_answered} >= {max_questions})")
                return {
                    'should_terminate': True,
                    'reason': 'max_questions_learning',
                    'message': f'Learning session completed ({max_questions} questions)'
                }
            # Never terminate early for learning mode
            return {
                'should_terminate': False,
                'reason': 'learning_mode',
                'message': 'Learning mode continues until target questions reached'
            }
        
        # For preliminary sessions (≤40 questions): Use SE threshold
        elif session_type == 'preliminary':
            if session.questions_answered >= self.min_questions and session.ability_se <= self.min_se_threshold:
                logger.info(f"TERMINATE: Sufficient precision achieved for preliminary (SE: {session.ability_se} <= {self.min_se_threshold})")
                return {
                    'should_terminate': True,
                    'reason': 'precision_reached',
                    'message': 'Sufficient precision achieved for preliminary test'
                }
        
        # For full sessions (60 questions): Use question count primarily, SE threshold only if very confident
        elif session_type == 'full':
            min_questions = max(40, session_data.get('estimated_total_questions', 60) * 0.7)
            max_questions = session_data.get('estimated_total_questions', 60)
            
            logger.info(f"Full session: min_questions={min_questions}, max_questions={max_questions}")
            
            # Don't terminate early unless really confident
            if session.questions_answered < min_questions:
                logger.info(f"CONTINUE: Need more questions for full session (answered: {session.questions_answered} < min: {min_questions})")
                return {
                    'should_terminate': False,
                    'reason': 'min_questions_full',
                    'message': f'Need at least {min_questions} questions for full diagnostic'
                }
            elif session.questions_answered >= max_questions:
                logger.info(f"TERMINATE: Full session question limit reached ({session.questions_answered} >= {max_questions})")
                return {
                    'should_terminate': True,
                    'reason': 'max_questions_full',
                    'message': f'Full diagnostic completed ({max_questions} questions)'
                }
            else:
                # Only terminate early if extremely confident (SE < 0.25)
                if session.ability_se < 0.25:
                    logger.info(f"TERMINATE: Extremely confident for full session (SE: {session.ability_se} < 0.25)")
                    return {
                        'should_terminate': True,
                        'reason': 'precision_reached_full',
                        'message': 'Extremely confident - full diagnostic can end early'
                    }
        
        # For comprehensive sessions (130 questions): Use question count only
        elif session_type == 'comprehensive':
            max_questions = session_data.get('estimated_total_questions', 130)
            if session.questions_answered >= max_questions:
                logger.info(f"TERMINATE: Comprehensive session completed ({session.questions_answered} >= {max_questions})")
                return {
                    'should_terminate': True,
                    'reason': 'max_questions_comprehensive',
                    'message': f'Comprehensive diagnostic completed ({max_questions} questions)'
                }
        
        # Fallback: Use original SE threshold logic
        else:
            if session.questions_answered >= self.min_questions and session.ability_se <= self.min_se_threshold:
                logger.info(f"TERMINATE: Sufficient precision achieved (fallback) (SE: {session.ability_se} <= {self.min_se_threshold})")
                return {
                    'should_terminate': True,
                    'reason': 'precision_reached',
                    'message': 'Sufficient precision achieved'
                }
        
        # Check maximum questions (if set in session)
        if session.test_length and session.questions_answered >= session.test_length:
            logger.info(f"TERMINATE: Session test length reached ({session.questions_answered} >= {session.test_length})")
            return {
                'should_terminate': True,
                'reason': 'max_questions',
                'message': 'Maximum questions reached'
            }
        
        logger.info(f"CONTINUE: All conditions met for continuing")
        return {
            'should_terminate': False,
            'reason': 'continue',
            'message': 'Continue with more questions'
        }
    
    def _3pl_probability(self, theta: float, irt_params: Dict) -> float:
        """Calculate 3PL probability with validation"""
        a = irt_params['discrimination']
        b = irt_params['difficulty']
        c = irt_params['guessing']
        
        # Validate parameters
        if a is None or b is None or c is None:
            return 0.5  # Default probability if parameters are missing
        
        # Ensure guessing parameter is in valid range
        c = max(0.0, min(0.5, c))
        
        # Calculate 3PL probability: P(θ) = c + (1-c) / (1 + exp(-a(θ-b)))
        try:
            probability = c + (1 - c) / (1 + math.exp(-a * (theta - b)))
            # Ensure probability is in valid range
            return max(0.0, min(1.0, probability))
        except (OverflowError, ZeroDivisionError):
            # Fallback for numerical issues
            return 0.5
    
    def _calculate_item_information(self, theta: float, a: float, b: float, c: float) -> float:
        """Calculate item information at given theta for 3PL model"""
        p = self._3pl_probability(theta, {'discrimination': a, 'difficulty': b, 'guessing': c})
        q = 1 - p
        
        # 3PL information function: I(θ) = a² * (P - c)² * Q / (P * (1 - c)²)
        if p > c and p < 1:
            return a**2 * (p - c)**2 * q / (p * (1 - c)**2)
        else:
            return 0.0
    
    def _calculate_standard_error(self, theta: float, responses: List[Dict]) -> float:
        """
        Calculate standard error of ability estimate using 3PL information function
        
        Args:
            theta: Current ability estimate
            responses: List of response dicts with IRT parameters
            
        Returns:
            Standard error of ability estimate
        """
        import math
        
        total_information = 0.0
        valid_responses = 0
        
        for response in responses:
            # Получаем IRT параметры из словаря response
            irt_params = response['irt_params']
            
            # Validate IRT parameters
            if (irt_params['discrimination'] is not None and 
                irt_params['difficulty'] is not None and 
                irt_params['guessing'] is not None):
                
                information = self._calculate_item_information(
                    theta,
                    irt_params['discrimination'],
                    irt_params['difficulty'],
                    irt_params['guessing']
                )
                total_information += information
                valid_responses += 1
        
        if total_information > 0:
            se = 1.0 / math.sqrt(total_information)
            # Ensure reasonable bounds for standard error
            return max(0.1, min(2.0, se))
        elif valid_responses > 0:
            # Fallback: simple standard error based on number of responses
            return 1.0 / math.sqrt(valid_responses)
        else:
            # Default standard error if no valid information
            return 1.0
    
    def _proportion_to_theta(self, proportion: float) -> float:
        """Convert proportion correct to initial theta estimate with improved validation"""
        # Ensure proportion is in valid range
        proportion = max(0.01, min(0.99, proportion))
        
        try:
            # Use logit transformation to map proportion to theta scale
            # This maps 0.5 to 0, 0.9 to ~2, 0.1 to ~-2
            theta = math.log(proportion / (1 - proportion))
            
            # Limit to reasonable range
            return max(-3.0, min(3.0, theta))
        except (ValueError, ZeroDivisionError):
            # Fallback for numerical issues
            return 0.0 

    def convert_irt_ability_to_readiness_percentage(self, theta: float) -> float:
        """
        Convert IRT ability (theta) to readiness percentage (0-100%) with improved error handling
        
        IRT theta values typically range from -4 to +4, where:
        - theta = 0: average ability
        - theta = 1: one standard deviation above average
        - theta = -1: one standard deviation below average
        
        We convert this to a readiness percentage where:
        - theta = -2: ~10% readiness
        - theta = 0: ~50% readiness  
        - theta = +2: ~90% readiness
        """
        if theta is None:
            return 0.0
        
        try:
            # Use logistic function to convert theta to probability
            # This gives us a smooth curve from 0 to 1
            import math
            probability = 1 / (1 + math.exp(-theta))
            
            # Convert to percentage and ensure it's within 0-100 range
            percentage = probability * 100
            
            # Round to 1 decimal place to avoid floating point precision issues
            return round(max(0.0, min(100.0, percentage)), 1)
        except (OverflowError, ValueError):
            # Fallback for numerical issues
            if theta > 0:
                return 100.0
            else:
                return 0.0
    
    def convert_irt_ability_to_performance_percentage(self, theta: float) -> float:
        """
        Convert IRT ability to performance percentage for display with improved error handling
        This is a more conservative conversion for display purposes
        """
        if theta is None:
            return 0.0
        
        try:
            # Use a more conservative conversion
            # theta = 0 -> 50%
            # theta = 1 -> 70%
            # theta = 2 -> 85%
            # theta = -1 -> 30%
            # theta = -2 -> 15%
            
            import math
            # Use sigmoid function with adjusted parameters
            probability = 1 / (1 + math.exp(-(theta + 0.5) * 0.8))
            percentage = probability * 100
            
            # Ensure reasonable bounds and round to 1 decimal place
            return round(max(0.0, min(100.0, percentage)), 1)
        except (OverflowError, ValueError):
            # Fallback for numerical issues
            if theta > 0:
                return 100.0
            else:
                return 0.0
    
    def calculate_target_ability(self) -> float:
        """
        Calculate target ability for exam readiness with improved error handling
        Based on typical BI-toets requirements
        """
        try:
            # Target theta for passing BI-toets is typically around 0.0 to 0.5
            # This represents average to above-average ability
            target_theta = 0.3
            
            # Convert to readiness percentage
            target_readiness = self.convert_irt_ability_to_readiness_percentage(target_theta)
            
            return round(target_readiness, 1)
        except Exception:
            # Fallback target ability
            return 50.0
    
    def calculate_weeks_to_target(self, current_ability: float, target_ability: float, 
                                 study_hours_per_week: float = 20.0) -> int:
        """
        Calculate estimated weeks needed to reach target ability with improved error handling
        
        Args:
            current_ability: Current readiness percentage
            target_ability: Target readiness percentage
            study_hours_per_week: Hours of study per week
            
        Returns:
            Estimated weeks needed
        """
        try:
            if current_ability >= target_ability:
                return 0
            
            # Calculate ability gap
            ability_gap = target_ability - current_ability
            
            # Estimate learning rate (percentage points per week)
            # This is a rough estimate based on typical learning curves
            if study_hours_per_week >= 30:
                weekly_progress = 3.0  # 3% per week with intensive study
            elif study_hours_per_week >= 20:
                weekly_progress = 2.0  # 2% per week with moderate study
            elif study_hours_per_week >= 10:
                weekly_progress = 1.5  # 1.5% per week with light study
            else:
                weekly_progress = 1.0  # 1% per week with minimal study
            
            # Calculate weeks needed
            weeks_needed = ability_gap / weekly_progress
            
            # Round up and ensure minimum of 1 week
            return max(1, int(weeks_needed + 0.5))
        except (ValueError, ZeroDivisionError):
            # Fallback: return reasonable default
            return 12  # 12 weeks as default estimate 

    # Оптимизируем метод update_ability_estimate
    def update_ability_estimate(self, response: 'DiagnosticResponse') -> Dict[str, float]:
        """
        Update ability estimate with optimization
        
        Args:
            response: DiagnosticResponse object
            
        Returns:
            Dictionary with updated ability and standard error
        """
        if not self.session:
            return {'ability': 0.0, 'se': 1.0}
        
        try:
            # Получаем все ответы сессии с кэшированием
            responses = self._get_session_responses_optimized()
            
            if not responses:
                return {'ability': 0.0, 'se': 1.0}
            
            # Оцениваем способность
            ability, se = self.estimate_ability(responses)
            
            # Ограничиваем значения
            ability = max(-4.0, min(4.0, ability))
            se = max(0.1, min(2.0, se))
            
            logger.info(f"Ability updated: {ability:.3f}, SE: {se:.3f}")
            
            return {
                'ability': ability,
                'se': se
            }
            
        except Exception as e:
            logger.error(f"Error updating ability estimate: {e}")
            return {'ability': 0.0, 'se': 1.0}

    def _get_session_responses_optimized(self) -> List[Dict]:
        """Получить ответы сессии с оптимизацией и правильным управлением session"""
        if not self.session:
            return []
        
        try:
            # Получаем ответы с предзагрузкой связанных данных
            responses = self.session.responses.options(
                db.joinedload(DiagnosticResponse.question).joinedload(Question.irt_parameters)
            ).all()
            
            # Преобразуем в формат для IRT расчетов
            irt_responses = []
            
            for response in responses:
                try:
                    # Получаем IRT параметры напрямую из связанного объекта
                    # Это гарантирует, что объект привязан к текущей session
                    irt_params = response.question.irt_parameters
                    
                    if irt_params:
                        # Проверяем, что объект привязан к session
                        try:
                            # Проверяем, что объект в session
                            _ = irt_params.id
                        except Exception:
                            # Если объект detached, получаем его заново
                            irt_params = IRTParameters.query.get(irt_params.id)
                        
                        if irt_params:
                            irt_responses.append({
                                'question_id': response.question_id,
                                'is_correct': response.is_correct,
                                'irt_params': {
                                    'difficulty': irt_params.difficulty,
                                    'discrimination': irt_params.discrimination,
                                    'guessing': irt_params.guessing
                                }
                            })
                    else:
                        # Fallback: попробуем получить из кэша
                        cached_params = get_cached_irt_parameters(response.question_id)
                        if cached_params:
                            # Убеждаемся, что cached объект привязан к session
                            try:
                                # Проверяем, что объект в session
                                _ = cached_params.id
                            except Exception:
                                # Получаем свежий объект из базы данных
                                fresh_params = IRTParameters.query.get(cached_params.id)
                                if fresh_params:
                                    irt_responses.append({
                                        'question_id': response.question_id,
                                        'is_correct': response.is_correct,
                                        'irt_params': {
                                            'difficulty': fresh_params.difficulty,
                                            'discrimination': fresh_params.discrimination,
                                            'guessing': fresh_params.guessing
                                        }
                                    })
                
                except Exception as e:
                    logger.warning(f"Error processing response {response.id}: {e}")
                    continue
            
            return irt_responses
            
        except Exception as e:
            logger.error(f"Error in _get_session_responses_optimized: {e}")
            return []


def update_ability_from_session_responses(user_id: int, session_id: int) -> Optional[float]:
    """
    Update user ability based on StudySession responses using IRT with conflict protection
    
    Args:
        user_id: User ID
        session_id: StudySession ID
        
    Returns:
        Updated ability value or None if failed
    """
    from models import StudySessionResponse, PersonalLearningPlan, StudySession
    import logging
    import time
    
    logger = logging.getLogger(__name__)
    
    try:
        # Get session and verify it's completed
        session = StudySession.query.get(session_id)
        if not session:
            logger.warning(f"Session {session_id} not found")
            return None
        
        if session.status != 'completed':
            logger.warning(f"Session {session_id} is not completed (status: {session.status})")
            return None
        
        # Check if feedback already processed
        if session.feedback_processed:
            logger.info(f"Feedback already processed for session {session_id}")
            return session.session_ability_after
        
        # Get active plan with retry logic
        max_retries = 3
        retry_delay = 0.1  # seconds
        
        for attempt in range(max_retries):
            active_plan = PersonalLearningPlan.query.filter_by(
                user_id=user_id, 
                status='active'
            ).first()
            
            if not active_plan:
                logger.warning(f"No active plan found for user {user_id}")
                return None
            
            # Get session responses
            responses = StudySessionResponse.query.filter_by(session_id=session_id).all()
            
            if not responses:
                logger.warning(f"No responses found for session {session_id}")
                return active_plan.current_ability
            
            current_ability = active_plan.current_ability or 0.0
            
            # Process each response using IRT
            new_ability = current_ability
            total_weight = 0.0
            
            for response in responses:
                # Get IRT parameters
                irt_params = response.question.irt_parameters
                if not irt_params:
                    continue  # Skip questions without IRT parameters
                
                difficulty = irt_params.difficulty or 0.0
                discrimination = irt_params.discrimination or 1.0
                guessing = irt_params.guessing or 0.0
                
                # Calculate probability of correct response
                prob_correct = calculate_probability(
                    ability=current_ability,
                    difficulty=difficulty,
                    discrimination=discrimination,
                    guessing=guessing
                )
                
                # Calculate weight based on discrimination and response time
                weight = discrimination
                if response.response_time:
                    # Penalize very fast or very slow responses
                    if response.response_time < 2000:  # Less than 2 seconds
                        weight *= 0.8
                    elif response.response_time > 30000:  # More than 30 seconds
                        weight *= 0.9
                
                # Update ability using Maximum Likelihood Estimation
                if response.is_correct:
                    # Increase ability if answered correctly
                    adjustment = discrimination * (1 - prob_correct) / prob_correct
                else:
                    # Decrease ability if answered incorrectly  
                    adjustment = -discrimination * prob_correct / (1 - prob_correct)
                
                # Apply weighted adjustment
                new_ability += weight * adjustment * 0.1  # Learning rate
                total_weight += weight
            
            # Normalize by total weight
            if total_weight > 0:
                new_ability = current_ability + (new_ability - current_ability) / total_weight
            
            # Keep ability in reasonable bounds [-4, 4]
            new_ability = max(-4.0, min(4.0, new_ability))
            
            # Check if update is significant enough
            if not active_plan.should_update_ability(new_ability, min_change_threshold=0.02):
                logger.info(f"Ability change too small for session {session_id}: {new_ability - current_ability:.3f}")
                session.mark_feedback_processed()
                return current_ability
            
            # Try to update plan safely
            if active_plan.update_ability_safely(new_ability):
                # Update session with new ability
                if session.update_ability_safely(new_ability, confidence=0.8):
                    session.mark_feedback_processed()
                    logger.info(f"Successfully updated ability for user {user_id}: {current_ability:.3f} -> {new_ability:.3f}")
                    return new_ability
                else:
                    logger.warning(f"Failed to update session ability for session {session_id}")
                    return current_ability
            else:
                # Conflict detected, retry with delay
                if attempt < max_retries - 1:
                    logger.info(f"Conflict detected, retrying in {retry_delay}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                else:
                    logger.error(f"Failed to update ability after {max_retries} attempts due to conflicts")
                    return current_ability
        
        return current_ability
        
    except Exception as e:
        logger.error(f"Error updating ability from session responses: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def update_ability_with_lock(user_id: int, new_ability: float, domain: str = None) -> bool:
    """
    Update user ability with distributed lock to prevent conflicts
    
    Args:
        user_id: User ID
        new_ability: New ability value
        domain: Domain to update (optional)
        
    Returns:
        True if update successful, False otherwise
    """
    from models import PersonalLearningPlan
    import logging
    import time
    
    logger = logging.getLogger(__name__)
    
    try:
        # Get active plan
        active_plan = PersonalLearningPlan.query.filter_by(
            user_id=user_id, 
            status='active'
        ).first()
        
        if not active_plan:
            logger.warning(f"No active plan found for user {user_id}")
            return False
        
        # Try to update with retry logic
        max_retries = 3
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            if active_plan.update_ability_safely(new_ability, domain=domain):
                logger.info(f"Successfully updated ability for user {user_id}: {new_ability:.3f}")
                return True
            else:
                if attempt < max_retries - 1:
                    logger.info(f"Update conflict, retrying in {retry_delay}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    logger.error(f"Failed to update ability after {max_retries} attempts")
                    return False
        
        return False
        
    except Exception as e:
        logger.error(f"Error in update_ability_with_lock: {str(e)}")
        return False


def calculate_probability(ability: float, difficulty: float, discrimination: float = 1.0, guessing: float = 0.0) -> float:
    """Calculate probability of correct response using 3PL IRT model"""
    import math
    
    try:
        exponent = discrimination * (ability - difficulty)
        probability = guessing + (1 - guessing) / (1 + math.exp(-exponent))
        return max(0.01, min(0.99, probability))  # Bound between 0.01 and 0.99
    except OverflowError:
        return 0.99 if ability > difficulty else 0.01 