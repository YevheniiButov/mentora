"""
Data Validator for IRT System
Комплексная система валидации данных для обеспечения стабильности IRT системы
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import math

from models import (
    Question, IRTParameters, DiagnosticSession, DiagnosticResponse,
    StudySession, StudySessionResponse, PersonalLearningPlan, User
)
from extensions import db

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Уровни валидации"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Результат валидации"""
    is_valid: bool
    level: ValidationLevel
    message: str
    field: Optional[str] = None
    value: Optional[Any] = None
    expected_range: Optional[Tuple] = None
    suggestions: Optional[List[str]] = None


class DataValidator:
    """Основной класс валидации данных"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.validation_results: List[ValidationResult] = []
    
    def validate_irt_parameters(self, irt_params: IRTParameters) -> List[ValidationResult]:
        """
        Валидация IRT параметров
        
        Args:
            irt_params: IRTParameters объект
            
        Returns:
            Список результатов валидации
        """
        results = []
        
        # Валидация difficulty
        if irt_params.difficulty is not None:
            if not (-5.0 <= irt_params.difficulty <= 5.0):
                results.append(ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Difficulty out of valid range: {irt_params.difficulty}",
                    field="difficulty",
                    value=irt_params.difficulty,
                    expected_range=(-5.0, 5.0),
                    suggestions=["Recalibrate IRT parameters", "Check question responses"]
                ))
            elif abs(irt_params.difficulty) > 4.0:
                results.append(ValidationResult(
                    is_valid=True,
                    level=ValidationLevel.WARNING,
                    message=f"Difficulty is extreme: {irt_params.difficulty}",
                    field="difficulty",
                    value=irt_params.difficulty,
                    expected_range=(-4.0, 4.0),
                    suggestions=["Consider recalibration if question is too easy/hard"]
                ))
        
        # Валидация discrimination
        if irt_params.discrimination is not None:
            if not (0.1 <= irt_params.discrimination <= 4.0):
                results.append(ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Discrimination out of valid range: {irt_params.discrimination}",
                    field="discrimination",
                    value=irt_params.discrimination,
                    expected_range=(0.1, 4.0),
                    suggestions=["Recalibrate IRT parameters", "Check question quality"]
                ))
            elif irt_params.discrimination < 0.3:
                results.append(ValidationResult(
                    is_valid=True,
                    level=ValidationLevel.WARNING,
                    message=f"Low discrimination: {irt_params.discrimination}",
                    field="discrimination",
                    value=irt_params.discrimination,
                    expected_range=(0.3, 4.0),
                    suggestions=["Question may be too easy or poorly designed"]
                ))
        
        # Валидация guessing
        if irt_params.guessing is not None:
            if not (0.0 <= irt_params.guessing <= 0.5):
                results.append(ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Guessing out of valid range: {irt_params.guessing}",
                    field="guessing",
                    value=irt_params.guessing,
                    expected_range=(0.0, 0.5),
                    suggestions=["Check question format", "Recalibrate parameters"]
                ))
            elif irt_params.guessing > 0.4:
                results.append(ValidationResult(
                    is_valid=True,
                    level=ValidationLevel.WARNING,
                    message=f"High guessing parameter: {irt_params.guessing}",
                    field="guessing",
                    value=irt_params.guessing,
                    expected_range=(0.0, 0.4),
                    suggestions=["Question may have too many options", "Consider redesign"]
                ))
        
        # Валидация стандартных ошибок
        if irt_params.se_difficulty is not None:
            if irt_params.se_difficulty > 1.0:
                results.append(ValidationResult(
                    is_valid=True,
                    level=ValidationLevel.WARNING,
                    message=f"High SE for difficulty: {irt_params.se_difficulty}",
                    field="se_difficulty",
                    value=irt_params.se_difficulty,
                    expected_range=(0.0, 1.0),
                    suggestions=["Need more responses for reliable calibration"]
                ))
        
        if irt_params.se_discrimination is not None:
            if irt_params.se_discrimination > 0.5:
                results.append(ValidationResult(
                    is_valid=True,
                    level=ValidationLevel.WARNING,
                    message=f"High SE for discrimination: {irt_params.se_discrimination}",
                    field="se_discrimination",
                    value=irt_params.se_discrimination,
                    expected_range=(0.0, 0.5),
                    suggestions=["Need more responses for reliable calibration"]
                ))
        
        # Валидация fit statistics
        if irt_params.infit is not None:
            if not (0.5 <= irt_params.infit <= 1.5):
                results.append(ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Infit out of acceptable range: {irt_params.infit}",
                    field="infit",
                    value=irt_params.infit,
                    expected_range=(0.5, 1.5),
                    suggestions=["Question may not fit IRT model", "Check for unusual response patterns"]
                ))
        
        if irt_params.outfit is not None:
            if not (0.5 <= irt_params.outfit <= 1.5):
                results.append(ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Outfit out of acceptable range: {irt_params.outfit}",
                    field="outfit",
                    value=irt_params.outfit,
                    expected_range=(0.5, 1.5),
                    suggestions=["Question may not fit IRT model", "Check for unusual response patterns"]
                ))
        
        return results
    
    def validate_diagnostic_session(self, session: DiagnosticSession) -> List[ValidationResult]:
        """
        Валидация диагностической сессии
        
        Args:
            session: DiagnosticSession объект
            
        Returns:
            Список результатов валидации
        """
        results = []
        
        # Проверка базовых полей
        if session.user_id is None:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.CRITICAL,
                message="Session has no user_id",
                field="user_id"
            ))
        
        if session.session_type not in ['diagnostic', 'adaptive', 'practice']:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Invalid session type: {session.session_type}",
                field="session_type",
                value=session.session_type,
                suggestions=["Use valid session type: diagnostic, adaptive, practice"]
            ))
        
        # Проверка способности
        if session.current_ability is not None:
            if not (-4.0 <= session.current_ability <= 4.0):
                results.append(ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Ability out of valid range: {session.current_ability}",
                    field="current_ability",
                    value=session.current_ability,
                    expected_range=(-4.0, 4.0),
                    suggestions=["Recalculate ability estimate", "Check IRT parameters"]
                ))
        
        # Проверка стандартной ошибки
        if session.ability_se is not None:
            if session.ability_se <= 0 or session.ability_se > 2.0:
                results.append(ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Invalid standard error: {session.ability_se}",
                    field="ability_se",
                    value=session.ability_se,
                    expected_range=(0.0, 2.0),
                    suggestions=["Recalculate standard error", "Check response data"]
                ))
        
        # Проверка статистики ответов
        if session.questions_answered < 0:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Negative questions answered: {session.questions_answered}",
                field="questions_answered",
                value=session.questions_answered,
                suggestions=["Reset session statistics"]
            ))
        
        if session.correct_answers < 0:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Negative correct answers: {session.correct_answers}",
                field="correct_answers",
                value=session.correct_answers,
                suggestions=["Reset session statistics"]
            ))
        
        if session.correct_answers > session.questions_answered:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"More correct answers than questions: {session.correct_answers} > {session.questions_answered}",
                field="correct_answers",
                value=session.correct_answers,
                suggestions=["Reset session statistics", "Check response data"]
            ))
        
        # Проверка временных меток
        if session.started_at and session.completed_at:
            if session.completed_at < session.started_at:
                results.append(ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message="Completion time before start time",
                    field="timestamps",
                    suggestions=["Check session timestamps"]
                ))
            
            duration = session.completed_at - session.started_at
            if duration.total_seconds() < 10:  # Меньше 10 секунд
                results.append(ValidationResult(
                    is_valid=True,
                    level=ValidationLevel.WARNING,
                    message=f"Very short session duration: {duration.total_seconds():.1f}s",
                    field="duration",
                    value=duration.total_seconds(),
                    suggestions=["Check for session interruption", "Verify completion"]
                ))
        
        return results
    
    def validate_study_session(self, session: StudySession) -> List[ValidationResult]:
        """
        Валидация учебной сессии
        
        Args:
            session: StudySession объект
            
        Returns:
            Список результатов валидации
        """
        results = []
        
        # Проверка базовых полей
        if session.learning_plan_id is None:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.CRITICAL,
                message="Session has no learning_plan_id",
                field="learning_plan_id"
            ))
        
        if session.session_type not in ['theory', 'practice', 'test', 'review']:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Invalid session type: {session.session_type}",
                field="session_type",
                value=session.session_type,
                suggestions=["Use valid session type: theory, practice, test, review"]
            ))
        
        # Проверка статистики
        if session.questions_answered < 0:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Negative questions answered: {session.questions_answered}",
                field="questions_answered",
                value=session.questions_answered
            ))
        
        if session.correct_answers < 0:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Negative correct answers: {session.correct_answers}",
                field="correct_answers",
                value=session.correct_answers
            ))
        
        if session.correct_answers > session.questions_answered:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"More correct answers than questions: {session.correct_answers} > {session.questions_answered}",
                field="correct_answers",
                value=session.correct_answers
            ))
        
        # Проверка прогресса
        if session.progress_percent < 0 or session.progress_percent > 100:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Invalid progress percentage: {session.progress_percent}",
                field="progress_percent",
                value=session.progress_percent,
                expected_range=(0.0, 100.0)
            ))
        
        # Проверка IRT данных
        if session.session_ability_before is not None:
            if not (-4.0 <= session.session_ability_before <= 4.0):
                results.append(ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Invalid ability before: {session.session_ability_before}",
                    field="session_ability_before",
                    value=session.session_ability_before,
                    expected_range=(-4.0, 4.0)
                ))
        
        if session.session_ability_after is not None:
            if not (-4.0 <= session.session_ability_after <= 4.0):
                results.append(ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Invalid ability after: {session.session_ability_after}",
                    field="session_ability_after",
                    value=session.session_ability_after,
                    expected_range=(-4.0, 4.0)
                ))
        
        # Проверка версии
        if session.version < 1:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Invalid version: {session.version}",
                field="version",
                value=session.version,
                suggestions=["Reset version to 1"]
            ))
        
        return results
    
    def validate_personal_learning_plan(self, plan: PersonalLearningPlan) -> List[ValidationResult]:
        """
        Валидация персонального плана обучения
        
        Args:
            plan: PersonalLearningPlan объект
            
        Returns:
            Список результатов валидации
        """
        results = []
        
        # Проверка базовых полей
        if plan.user_id is None:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.CRITICAL,
                message="Plan has no user_id",
                field="user_id"
            ))
        
        # Проверка способности
        if plan.current_ability is not None:
            if not (-4.0 <= plan.current_ability <= 4.0):
                results.append(ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Invalid current ability: {plan.current_ability}",
                    field="current_ability",
                    value=plan.current_ability,
                    expected_range=(-4.0, 4.0)
                ))
        
        # Проверка целевой способности
        if plan.target_ability is not None:
            if not (-4.0 <= plan.target_ability <= 4.0):
                results.append(ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Invalid target ability: {plan.target_ability}",
                    field="target_ability",
                    value=plan.target_ability,
                    expected_range=(-4.0, 4.0)
                ))
        
        # Проверка прогресса
        if plan.overall_progress < 0 or plan.overall_progress > 100:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Invalid overall progress: {plan.overall_progress}",
                field="overall_progress",
                value=plan.overall_progress,
                expected_range=(0.0, 100.0)
            ))
        
        # Проверка часов обучения
        if plan.study_hours_per_week < 0 or plan.study_hours_per_week > 168:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Invalid study hours per week: {plan.study_hours_per_week}",
                field="study_hours_per_week",
                value=plan.study_hours_per_week,
                expected_range=(0.0, 168.0)
            ))
        
        # Проверка дат
        if plan.start_date and plan.end_date:
            if plan.end_date < plan.start_date:
                results.append(ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message="End date before start date",
                    field="dates",
                    suggestions=["Check plan dates"]
                ))
        
        return results
    
    def validate_response_data(self, response: DiagnosticResponse) -> List[ValidationResult]:
        """
        Валидация данных ответа
        
        Args:
            response: DiagnosticResponse объект
            
        Returns:
            Список результатов валидации
        """
        results = []
        
        # Проверка базовых полей
        if response.session_id is None:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.CRITICAL,
                message="Response has no session_id",
                field="session_id"
            ))
        
        if response.question_id is None:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.CRITICAL,
                message="Response has no question_id",
                field="question_id"
            ))
        
        # Проверка времени ответа
        if response.response_time is not None:
            if response.response_time < 0:
                results.append(ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Negative response time: {response.response_time}",
                    field="response_time",
                    value=response.response_time
                ))
            elif response.response_time < 500:  # Меньше 0.5 секунды
                results.append(ValidationResult(
                    is_valid=True,
                    level=ValidationLevel.WARNING,
                    message=f"Very fast response: {response.response_time}ms",
                    field="response_time",
                    value=response.response_time,
                    suggestions=["Check for accidental clicks", "Verify response quality"]
                ))
            elif response.response_time > 300000:  # Больше 5 минут
                results.append(ValidationResult(
                    is_valid=True,
                    level=ValidationLevel.WARNING,
                    message=f"Very slow response: {response.response_time}ms",
                    field="response_time",
                    value=response.response_time,
                    suggestions=["Check for session interruption", "Verify response quality"]
                ))
        
        # Проверка IRT данных
        if response.ability_before is not None:
            if not (-4.0 <= response.ability_before <= 4.0):
                results.append(ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Invalid ability before: {response.ability_before}",
                    field="ability_before",
                    value=response.ability_before,
                    expected_range=(-4.0, 4.0)
                ))
        
        if response.ability_after is not None:
            if not (-4.0 <= response.ability_after <= 4.0):
                results.append(ValidationResult(
                    is_valid=False,
                    level=ValidationLevel.ERROR,
                    message=f"Invalid ability after: {response.ability_after}",
                    field="ability_after",
                    value=response.ability_after,
                    expected_range=(-4.0, 4.0)
                ))
        
        return results
    
    def validate_question(self, question: Question) -> List[ValidationResult]:
        """
        Валидация вопроса
        
        Args:
            question: Question объект
            
        Returns:
            Список результатов валидации
        """
        results = []
        
        # Проверка текста вопроса
        if not question.text or len(question.text.strip()) < 10:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="Question text too short or empty",
                field="text",
                value=question.text,
                suggestions=["Add more content to question text"]
            ))
        
        # Проверка вариантов ответов
        if not question.options or len(question.options) < 2:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="Question has insufficient answer options",
                field="options",
                value=question.options,
                suggestions=["Add more answer options"]
            ))
        
        # Проверка индекса правильного ответа
        if question.correct_answer_index is None:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="No correct answer index specified",
                field="correct_answer_index"
            ))
        elif question.correct_answer_index < 0 or question.correct_answer_index >= len(question.options):
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Invalid correct answer index: {question.correct_answer_index}",
                field="correct_answer_index",
                value=question.correct_answer_index,
                expected_range=(0, len(question.options) - 1)
            ))
        
        # Проверка объяснения
        if not question.explanation or len(question.explanation.strip()) < 10:
            results.append(ValidationResult(
                is_valid=True,
                level=ValidationLevel.WARNING,
                message="Question explanation too short or missing",
                field="explanation",
                value=question.explanation,
                suggestions=["Add detailed explanation for the correct answer"]
            ))
        
        return results
    
    def validate_user_data(self, user: User) -> List[ValidationResult]:
        """
        Валидация данных пользователя
        
        Args:
            user: User объект
            
        Returns:
            Список результатов валидации
        """
        results = []
        
        # Проверка email
        if not user.email or '@' not in user.email:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message="Invalid email format",
                field="email",
                value=user.email
            ))
        
        # Проверка уровня
        if user.level < 1:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Invalid user level: {user.level}",
                field="level",
                value=user.level,
                expected_range=(1, float('inf'))
            ))
        
        # Проверка опыта
        if user.xp < 0:
            results.append(ValidationResult(
                is_valid=False,
                level=ValidationLevel.ERROR,
                message=f"Negative XP: {user.xp}",
                field="xp",
                value=user.xp
            ))
        
        return results
    
    def validate_all_data(self) -> Dict[str, List[ValidationResult]]:
        """
        Комплексная валидация всех данных системы
        
        Returns:
            Словарь с результатами валидации по категориям
        """
        all_results = {
            'questions': [],
            'irt_parameters': [],
            'diagnostic_sessions': [],
            'study_sessions': [],
            'learning_plans': [],
            'responses': [],
            'users': []
        }
        
        try:
            # Валидация вопросов
            questions = Question.query.limit(100).all()  # Ограничиваем для производительности
            for question in questions:
                all_results['questions'].extend(self.validate_question(question))
            
            # Валидация IRT параметров
            irt_params = IRTParameters.query.limit(100).all()
            for params in irt_params:
                all_results['irt_parameters'].extend(self.validate_irt_parameters(params))
            
            # Валидация диагностических сессий
            diagnostic_sessions = DiagnosticSession.query.limit(50).all()
            for session in diagnostic_sessions:
                all_results['diagnostic_sessions'].extend(self.validate_diagnostic_session(session))
            
            # Валидация учебных сессий
            study_sessions = StudySession.query.limit(50).all()
            for session in study_sessions:
                all_results['study_sessions'].extend(self.validate_study_session(session))
            
            # Валидация планов обучения
            learning_plans = PersonalLearningPlan.query.limit(50).all()
            for plan in learning_plans:
                all_results['learning_plans'].extend(self.validate_personal_learning_plan(plan))
            
            # Валидация ответов
            responses = DiagnosticResponse.query.limit(100).all()
            for response in responses:
                all_results['responses'].extend(self.validate_response_data(response))
            
            # Валидация пользователей
            users = User.query.limit(50).all()
            for user in users:
                all_results['users'].extend(self.validate_user_data(user))
            
        except Exception as e:
            self.logger.error(f"Error during comprehensive validation: {e}")
            all_results['error'] = [ValidationResult(
                is_valid=False,
                level=ValidationLevel.CRITICAL,
                message=f"Validation error: {str(e)}"
            )]
        
        return all_results
    
    def get_validation_summary(self, results: Dict[str, List[ValidationResult]]) -> Dict:
        """
        Получение сводки валидации
        
        Args:
            results: Результаты валидации
            
        Returns:
            Сводка валидации
        """
        summary = {
            'total_issues': 0,
            'critical_issues': 0,
            'errors': 0,
            'warnings': 0,
            'info': 0,
            'categories': {}
        }
        
        for category, category_results in results.items():
            if category == 'error':
                continue
                
            category_summary = {
                'total': len(category_results),
                'critical': len([r for r in category_results if r.level == ValidationLevel.CRITICAL]),
                'errors': len([r for r in category_results if r.level == ValidationLevel.ERROR]),
                'warnings': len([r for r in category_results if r.level == ValidationLevel.WARNING]),
                'info': len([r for r in category_results if r.level == ValidationLevel.INFO])
            }
            
            summary['categories'][category] = category_summary
            summary['total_issues'] += category_summary['total']
            summary['critical_issues'] += category_summary['critical']
            summary['errors'] += category_summary['errors']
            summary['warnings'] += category_summary['warnings']
            summary['info'] += category_summary['info']
        
        # Определяем общий статус
        if summary['critical_issues'] > 0:
            summary['status'] = 'critical'
        elif summary['errors'] > 0:
            summary['status'] = 'error'
        elif summary['warnings'] > 0:
            summary['status'] = 'warning'
        else:
            summary['status'] = 'healthy'
        
        return summary


def validate_system_health() -> Dict:
    """
    Функция для проверки здоровья системы данных
    
    Returns:
        Отчет о состоянии данных системы
    """
    validator = DataValidator()
    
    try:
        # Выполняем комплексную валидацию
        results = validator.validate_all_data()
        
        # Получаем сводку
        summary = validator.get_validation_summary(results)
        
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'summary': summary,
            'details': results,
            'recommendations': _generate_validation_recommendations(summary)
        }
        
    except Exception as e:
        logger.error(f"Error during system health validation: {e}")
        return {
            'timestamp': datetime.now(timezone.utc).isoformat(),
            'error': str(e),
            'status': 'error'
        }


def _generate_validation_recommendations(summary: Dict) -> List[str]:
    """Генерирует рекомендации на основе результатов валидации"""
    recommendations = []
    
    if summary['critical_issues'] > 0:
        recommendations.append(f"CRITICAL: {summary['critical_issues']} critical issues found. Immediate action required.")
    
    if summary['errors'] > 0:
        recommendations.append(f"ERROR: {summary['errors']} validation errors found. Review and fix data issues.")
    
    if summary['warnings'] > 0:
        recommendations.append(f"WARNING: {summary['warnings']} warnings found. Consider addressing data quality issues.")
    
    # Специфические рекомендации по категориям
    for category, cat_summary in summary['categories'].items():
        if cat_summary['critical'] > 0:
            recommendations.append(f"Review {category} data - {cat_summary['critical']} critical issues")
        elif cat_summary['errors'] > 0:
            recommendations.append(f"Check {category} data - {cat_summary['errors']} validation errors")
    
    if not recommendations:
        recommendations.append("Data validation passed successfully. System is healthy.")
    
    return recommendations 