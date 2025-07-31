# utils/irt_engine.py - IRT Engine for Adaptive Testing
# Professional implementation for BI-toets diagnostic testing

import math
import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timezone
from extensions import db
from models import Question, DiagnosticSession, DiagnosticResponse, BIGDomain
from models import IRTParameters # Added missing import

class IRTEngine:
    """IRT Engine for 3PL model adaptive testing with domain support"""
    
    def __init__(self, session: Optional[DiagnosticSession] = None, diagnostic_type: str = 'express'):
        self.session = session
        self.max_iterations = 50
        self.convergence_threshold = 0.001
        self.min_se_threshold = 0.4  # Увеличен порог стандартной ошибки для завершения
        
        # Настройки в зависимости от типа диагностики
        self.diagnostic_type = diagnostic_type
        
        if diagnostic_type == 'express':
            # Экспресс диагностика: 1 вопрос на домен
            self.questions_per_domain = 1
            self.max_questions = 25  # Максимум 25 вопросов
        elif diagnostic_type == 'preliminary':
            # Предварительная диагностика: 3 вопроса на домен
            self.questions_per_domain = 3
            self.max_questions = 75  # Максимум 75 вопросов
        elif diagnostic_type == 'readiness':
            # Диагностика готовности: 6 вопросов на домен
            self.questions_per_domain = 6
            self.max_questions = 130  # Максимум 130 вопросов
        else:
            # По умолчанию экспресс
            self.diagnostic_type = 'express'
            self.questions_per_domain = 1
            self.max_questions = 25
        
        # Загрузить домены и их веса
        self.all_domains = self.load_all_domains()
        self.domain_weights = self.load_domain_weights()
        
        # Рассчитать минимальное количество вопросов
        self.min_questions = len(self.all_domains) * self.questions_per_domain
    
    def load_all_domains(self) -> Dict[str, BIGDomain]:
        """Загрузить все активные домены"""
        domains = BIGDomain.query.filter_by(is_active=True).all()
        return {domain.code: domain for domain in domains}
    
    def load_domain_weights(self) -> Dict[str, float]:
        """Загрузить веса доменов для приоритизации"""
        return {domain.code: domain.weight_percentage for domain in self.all_domains.values()}
    
    def get_domain_questions(self, domain_code: str, difficulty_range: Optional[Tuple[float, float]] = None, limit: int = 100) -> List[Question]:
        """Получить вопросы для конкретного домена с оптимизацией производительности"""
        query = Question.query.filter_by(domain=domain_code)
        
        if difficulty_range:
            min_diff, max_diff = difficulty_range
            # Используем JOIN для оптимизации запроса
            query = query.join(IRTParameters).filter(
                IRTParameters.difficulty.between(min_diff, max_diff)
            )
        
        # Добавляем лимит для предотвращения загрузки всех вопросов
        return query.limit(limit).all()
    
    def select_next_question_by_domain(self, domain_code: str, current_ability: float = 0.0, answered_question_ids: set = None) -> Optional[Question]:
        """Выбрать следующий вопрос для конкретного домена"""
        if answered_question_ids is None:
            answered_question_ids = set()
            
        questions = self.get_domain_questions(domain_code)
        
        # Исключить уже отвеченные вопросы
        available_questions = [q for q in questions if q.id not in answered_question_ids]
        
        if not available_questions:
            return None
        
        # Обеспечить, что current_ability не None
        if current_ability is None:
            current_ability = 0.0
        
        # Найти вопрос с оптимальной сложностью для current_ability
        optimal_question = None
        min_distance = float('inf')
        
        for question in available_questions:
            if not hasattr(question, 'irt_difficulty') or question.irt_difficulty is None:
                continue
                
            difficulty = question.irt_difficulty
            distance = abs(difficulty - current_ability)
            
            if distance < min_distance:
                min_distance = distance
                optimal_question = question
        
        return optimal_question or available_questions[0]
    
    def calculate_domain_abilities(self, user_responses: List[Dict]) -> Dict[str, float]:
        """Рассчитать способности пользователя по каждому домену"""
        domain_abilities = {}
        
        for domain_code in self.all_domains.keys():
            domain_responses = [r for r in user_responses if r.get('domain') == domain_code]
            
            if domain_responses and len(domain_responses) >= 1:  # Минимум 1 ответ для домена
                domain_abilities[domain_code] = self.estimate_ability(domain_responses)[0]
            else:
                domain_abilities[domain_code] = None  # Нет данных для домена
        
        return domain_abilities
    
    def get_domain_statistics(self, domain_code: str) -> Dict:
        """Получить статистику по домену"""
        domain = self.all_domains.get(domain_code)
        if not domain:
            return {}
        
        questions = self.get_domain_questions(domain_code)
        
        return {
            'code': domain_code,
            'name': domain.name,
            'description': domain.description,
            'weight': domain.weight_percentage,
            'question_count': len(questions),
            'average_difficulty': np.mean([q.irt_difficulty for q in questions]) if questions else 0.0,
            'difficulty_range': {
                'min': min([q.irt_difficulty for q in questions]) if questions else 0.0,
                'max': max([q.irt_difficulty for q in questions]) if questions else 0.0
            }
        }
        
    def estimate_ability(self, responses: List[Dict]) -> Tuple[float, float]:
        """
        Estimate ability (theta) using Maximum Likelihood Estimation (MLE)
        
        Args:
            responses: List of dicts with 'question_id', 'is_correct', 'irt_params'
            
        Returns:
            Tuple of (theta_estimate, standard_error)
        """
        if not responses:
            return 0.0, 1.0
            
        # Initial guess: proportion correct mapped to theta scale
        proportion_correct = sum(r['is_correct'] for r in responses) / len(responses)
        initial_theta = self._proportion_to_theta(proportion_correct)
        
        # Newton-Raphson iteration for MLE
        theta = initial_theta
        for iteration in range(self.max_iterations):
            first_derivative = 0.0
            second_derivative = 0.0
            
            for response in responses:
                # Получаем IRT параметры из словаря response
                irt_params = response['irt_params']
                is_correct = response['is_correct']
                
                # Calculate probability and derivatives
                p = self._3pl_probability(theta, irt_params)
                q = 1 - p
                
                # Avoid division by zero
                if p <= 0 or p >= 1:
                    continue
                
                # First derivative (gradient)
                first_derivative += irt_params['discrimination'] * (is_correct - p)
                
                # Second derivative (Hessian)
                second_derivative -= irt_params['discrimination']**2 * p * q
                
                # Avoid division by zero
                if abs(second_derivative) < 1e-10:
                    second_derivative = -1e-10
            
            # Newton-Raphson step
            if abs(second_derivative) > 1e-10:
                delta = first_derivative / second_derivative
                theta -= delta
                
                # Check convergence
                if abs(delta) < self.convergence_threshold:
                    break
            else:
                break
        
        # Limit theta to reasonable range
        theta = max(-4.0, min(4.0, theta))
        
        # Calculate standard error
        se = self._calculate_standard_error(theta, responses)
        
        # Limit standard error to reasonable range
        se = max(0.1, min(2.0, se))
        
        return theta, se
    
    def select_initial_question(self) -> Optional[Question]:
        """
        Select initial question for diagnostic session
        
        Returns:
            Selected question or None if no questions available
        """
        # Get all questions (IRT parameters are stored directly in Question model)
        questions = Question.query.all()
        
        if not questions:
            return None
        
        # For initial question, select one with medium difficulty (close to 0)
        best_question = None
        min_diff_from_zero = float('inf')
        
        for question in questions:
            # IRT parameters are stored directly in Question model
            diff_from_zero = abs(question.irt_difficulty)
            if diff_from_zero < min_diff_from_zero:
                min_diff_from_zero = diff_from_zero
                best_question = question
        
        return best_question
    
    def select_next_question(self) -> Optional[Question]:
        """Выбрать следующий вопрос для адаптивного тестирования"""
        if not self.session:
            return None
        
        # Получить историю ответов для анализа покрытия доменов
        responses = self.session.responses.all()
        domain_question_counts = {}
        answered_question_ids = set()
        
        for response in responses:
            question = response.question
            answered_question_ids.add(question.id)
            if hasattr(question, 'domain') and question.domain:
                domain = question.domain
                domain_question_counts[domain] = domain_question_counts.get(domain, 0) + 1
        
        # Найти домены, которые нуждаются в дополнительных вопросах
        domains_needing_questions = []
        for domain_code in self.all_domains.keys():
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
            
            # Выбрать домен с наивысшим приоритетом
            priority_domain = domains_needing_questions[0]['domain']
            return self.select_next_question_by_domain(priority_domain, self.current_ability_estimate, answered_question_ids)
        
        # Если все домены покрыты, использовать стандартную логику
        # Найти вопрос с оптимальной сложностью, исключая уже отвеченные
        all_questions = Question.query.filter(~Question.id.in_(answered_question_ids)).all()
        
        if not all_questions:
            # Если все вопросы отвечены, завершить диагностику
            return None
        
        optimal_question = None
        min_distance = float('inf')
        
        for question in all_questions:
            if not hasattr(question, 'irt_difficulty') or question.irt_difficulty is None:
                continue
                
            distance = abs(question.irt_difficulty - self.current_ability_estimate)
            
            if distance < min_distance:
                min_distance = distance
                optimal_question = question
        
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
            if hasattr(question, 'domain') and question.domain:
                domain = question.domain
                if domain not in domain_responses:
                    domain_responses[domain] = []
                domain_responses[domain].append(response)
        
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
                # Нет ответов по этому домену
                domain_abilities[domain_code] = None
        
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
        """Get detailed statistics for each domain"""
        if not self.session:
            return {}
        
        # Get all responses for this session
        responses = self.session.responses.all()
        if not responses:
            return {}
        
        # Группировать ответы по доменам
        domain_responses = {}
        for response in responses:
            # Получаем вопрос из базы данных
            question = Question.query.get(response.question_id)
            if question and hasattr(question, 'domain') and question.domain:
                domain = question.domain
                if domain not in domain_responses:
                    domain_responses[domain] = []
                domain_responses[domain].append(response)
        
        # Рассчитать детальную статистику для каждого домена
        domain_stats = {}
        for domain_code in self.all_domains.keys():
            domain = self.all_domains[domain_code]
            
            if domain_code in domain_responses and domain_responses[domain_code]:
                # Есть ответы по этому домену
                domain_resp_list = domain_responses[domain_code]
                correct_count = sum(1 for resp in domain_resp_list if resp.is_correct)
                total_count = len(domain_resp_list)
                accuracy = correct_count / total_count
                
                domain_stats[domain_code] = {
                    'name': domain.name,
                    'questions_answered': total_count,
                    'correct_answers': correct_count,
                    'accuracy': accuracy,
                    'accuracy_percentage': round(accuracy * 100, 1),
                    'has_data': True
                }
            else:
                # Нет ответов по этому домену
                domain_stats[domain_code] = {
                    'name': domain.name,
                    'questions_answered': 0,
                    'correct_answers': 0,
                    'accuracy': None,
                    'accuracy_percentage': None,
                    'has_data': False
                }
        
        return domain_stats
    
    def _check_termination_conditions(self, session: DiagnosticSession) -> Dict:
        """
        Check if diagnostic session should terminate
        
        Returns:
            Dict with termination info
        """
        # Проверить покрытие доменов (минимум questions_per_domain вопросов на домен)
        min_questions_per_domain = self.questions_per_domain
        total_domains = len(self.all_domains)
        min_total_questions = total_domains * min_questions_per_domain
        
        if session.questions_answered < min_total_questions:
            return {
                'should_terminate': False,
                'reason': 'domain_coverage',
                'message': f'Need at least {min_questions_per_domain} question(s) per domain ({total_domains} domains = {min_total_questions} questions)'
            }
        
        # Check minimum questions requirement
        if session.questions_answered < self.min_questions:
            return {
                'should_terminate': False,
                'reason': 'min_questions',
                'message': f'Need at least {self.min_questions} questions'
            }
        
        # Check maximum questions limit
        if session.questions_answered >= self.max_questions:
            return {
                'should_terminate': True,
                'reason': 'max_questions',
                'message': f'Maximum {self.max_questions} questions reached'
            }
        
        # Check precision threshold (only after minimum questions)
        if session.questions_answered >= self.min_questions and session.ability_se <= self.min_se_threshold:
            return {
                'should_terminate': True,
                'reason': 'precision_reached',
                'message': 'Sufficient precision achieved'
            }
        
        # Check maximum questions (if set in session)
        if session.test_length and session.questions_answered >= session.test_length:
            return {
                'should_terminate': True,
                'reason': 'max_questions',
                'message': 'Maximum questions reached'
            }
        
        return {
            'should_terminate': False,
            'reason': 'continue',
            'message': 'Continue with more questions'
        }
    
    def _3pl_probability(self, theta: float, irt_params: Dict) -> float:
        """Calculate 3PL probability"""
        a = irt_params['discrimination']
        b = irt_params['difficulty']
        c = irt_params['guessing']
        
        return c + (1 - c) / (1 + math.exp(-a * (theta - b)))
    
    def _calculate_item_information(self, theta: float, a: float, b: float, c: float) -> float:
        """Calculate item information at given theta"""
        p = self._3pl_probability(theta, {'discrimination': a, 'difficulty': b, 'guessing': c})
        q = 1 - p
        return a**2 * p * q
    
    def _calculate_standard_error(self, theta: float, responses: List[Dict]) -> float:
        """
        Calculate standard error of ability estimate
        
        Args:
            theta: Current ability estimate
            responses: List of response dicts with IRT parameters
            
        Returns:
            Standard error of ability estimate
        """
        import math
        
        total_information = 0.0
        
        for response in responses:
            # Получаем IRT параметры из словаря response
            irt_params = response['irt_params']
            
            information = self._calculate_item_information(
                theta,
                irt_params['discrimination'],
                irt_params['difficulty'],
                irt_params['guessing']
            )
            total_information += information
        
        if total_information > 0:
            return 1.0 / math.sqrt(total_information)
        else:
            return 1.0
    
    def _proportion_to_theta(self, proportion: float) -> float:
        """Convert proportion correct to initial theta estimate"""
        # Ensure proportion is in valid range
        proportion = max(0.01, min(0.99, proportion))
        
        # Use logit transformation to map proportion to theta scale
        # This maps 0.5 to 0, 0.9 to ~2, 0.1 to ~-2
        theta = math.log(proportion / (1 - proportion))
        
        # Limit to reasonable range
        return max(-3.0, min(3.0, theta)) 

    def convert_irt_ability_to_readiness_percentage(self, theta: float) -> float:
        """
        Convert IRT ability (theta) to readiness percentage (0-100%)
        
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
        
        # Use logistic function to convert theta to probability
        # This gives us a smooth curve from 0 to 1
        import math
        probability = 1 / (1 + math.exp(-theta))
        
        # Convert to percentage and ensure it's within 0-100 range
        percentage = probability * 100
        return max(0.0, min(100.0, percentage))
    
    def convert_irt_ability_to_performance_percentage(self, theta: float) -> float:
        """
        Convert IRT ability to performance percentage for display
        This is a more conservative conversion for display purposes
        """
        if theta is None:
            return 0.0
        
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
        
        # Ensure reasonable bounds
        return max(0.0, min(100.0, percentage)) 

    def calculate_target_ability(self) -> float:
        """
        Calculate target ability for exam readiness
        Based on typical BI-toets requirements
        """
        # Target theta for passing BI-toets is typically around 0.0 to 0.5
        # This represents average to above-average ability
        target_theta = 0.3
        
        # Convert to readiness percentage
        target_readiness = self.convert_irt_ability_to_readiness_percentage(target_theta)
        
        return round(target_readiness, 1)
    
    def calculate_weeks_to_target(self, current_ability: float, target_ability: float, 
                                 study_hours_per_week: float = 20.0) -> int:
        """
        Calculate estimated weeks needed to reach target ability
        
        Args:
            current_ability: Current readiness percentage
            target_ability: Target readiness percentage
            study_hours_per_week: Hours of study per week
            
        Returns:
            Estimated weeks needed
        """
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

    def update_ability_estimate(self, response: 'DiagnosticResponse') -> Dict[str, float]:
        """
        Update ability estimate for a diagnostic session after a new response
        
        Args:
            response: DiagnosticResponse object with question and answer data
            
        Returns:
            Dict with updated ability data: {'ability': float, 'se': float, 'item_info': float}
        """
        if not self.session:
            return {'ability': 0.0, 'se': 1.0, 'item_info': 0.0}
        
        try:
            print(f"🔍 ОТЛАДКА: update_ability_estimate вызвана")
            print(f"🔍 ОТЛАДКА: response = {response}")
            print(f"🔍 ОТЛАДКА: response.question_id = {response.question_id}")
            print(f"🔍 ОТЛАДКА: response.question = {response.question}")
            
            # Get all responses for this session to recalculate ability
            all_responses = self.session.responses.order_by(DiagnosticResponse.id).all()
            print(f"🔍 ОТЛАДКА: всего ответов в сессии = {len(all_responses)}")
            
            # Convert responses to IRT format
            irt_responses = []
            for resp in all_responses:
                print(f"🔍 ОТЛАДКА: обрабатываем ответ {resp.id}, question_id = {resp.question_id}")
                
                # Получаем вопрос через relationship
                question = resp.question
                print(f"🔍 ОТЛАДКА: question = {question}")
                
                if question and hasattr(question, 'irt_difficulty') and question.irt_difficulty is not None:
                    print(f"🔍 ОТЛАДКА: вопрос имеет IRT параметры")
                    irt_responses.append({
                        'question_id': resp.question_id,
                        'is_correct': resp.is_correct,
                        'irt_params': {
                            'difficulty': question.irt_difficulty,
                            'discrimination': question.irt_discrimination,
                            'guessing': question.irt_guessing
                        }
                    })
                else:
                    print(f"🔍 ОТЛАДКА: вопрос не имеет IRT параметров")
            
            print(f"🔍 ОТЛАДКА: irt_responses = {len(irt_responses)}")
            
            # Calculate new ability estimate
            if irt_responses:
                new_ability, new_se = self.estimate_ability(irt_responses)
                
                # Store previous ability before updating
                previous_ability = self.session.current_ability
                previous_se = self.session.ability_se
                
                # Update session with new ability
                self.session.current_ability = new_ability
                self.session.ability_se = new_se
                
                # Update the response record with ability data
                response.ability_before = previous_ability
                response.ability_after = new_ability
                response.se_before = previous_se
                response.se_after = new_se
                
                # Calculate item information for this question
                # Получаем вопрос через relationship
                question = response.question
                print(f"🔍 ОТЛАДКА: текущий вопрос = {question}")
                
                if question and hasattr(question, 'irt_difficulty') and question.irt_difficulty is not None:
                    print(f"🔍 ОТЛАДКА: вычисляем item_information")
                    item_info = self._calculate_item_information(
                        new_ability, 
                        question.irt_discrimination,
                        question.irt_difficulty,
                        question.irt_guessing
                    )
                    response.item_information = item_info
                else:
                    print(f"🔍 ОТЛАДКА: вопрос не имеет IRT параметров, item_info = 0")
                    item_info = 0.0
                
                # Save updates
                from extensions import db
                db.session.commit()
                
                print(f"🎯 IRT Updated: ability={new_ability:.3f}, SE={new_se:.3f}")
                
                return {
                    'ability': new_ability,
                    'se': new_se,
                    'item_info': item_info,
                    'previous_ability': previous_ability,
                    'previous_se': previous_se
                }
            else:
                print(f"🔍 ОТЛАДКА: нет IRT ответов для вычисления")
                return {'ability': 0.0, 'se': 1.0, 'item_info': 0.0}
                
        except Exception as e:
            print(f"❌ IRT Error in update_ability_estimate: {e}")
            import traceback
            traceback.print_exc()
            return {'ability': 0.0, 'se': 1.0, 'item_info': 0.0} 