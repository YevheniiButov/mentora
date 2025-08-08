"""
Общий менеджер данных диагностики для синхронизации между компонентами системы
"""

from models import DiagnosticSession, PersonalLearningPlan, User
from utils.domain_mapping import convert_abilities_to_new_format, convert_abilities_to_old_format, map_old_to_new_domain, get_domain_name, ALL_BIG_DOMAINS
from datetime import datetime, timezone
import json
import logging

logger = logging.getLogger(__name__)

class DiagnosticDataManager:
    """Менеджер для работы с данными диагностики"""
    
    @staticmethod
    def get_user_diagnostic_data(user_id: int) -> dict:
        """
        Получить актуальные данные диагностики пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Словарь с данными диагностики в новом формате
        """
        try:
            # Получаем последнюю завершенную диагностику
            latest_diagnostic = DiagnosticSession.query.filter_by(
                user_id=user_id,
                status='completed'
            ).order_by(DiagnosticSession.completed_at.desc()).first()
            
            if not latest_diagnostic:
                return {
                    'has_diagnostic': False,
                    'overall_score': 0,
                    'domains': [],
                    'diagnostic_date': None
                }
            
            # Получаем активный план обучения
            active_plan = PersonalLearningPlan.query.filter_by(
                user_id=user_id,
                status='active'
            ).first()
            
                                # Генерируем результаты диагностики
            try:
                diagnostic_data = latest_diagnostic.generate_results()
            except Exception as e:
                logger.warning(f"Error generating diagnostic results: {e}")
                # Используем реальные данные из сессии
                diagnostic_data = {
                    'domain_statistics': {},
                    'domain_abilities': {},
                    'weak_domains': [],
                    'strong_domains': [],
                    'questions_answered': latest_diagnostic.questions_answered,
                    'correct_answers': latest_diagnostic.correct_answers,
                    'current_ability': latest_diagnostic.current_ability
                }
            
            # Подготавливаем данные в новом формате
            result = {
                'has_diagnostic': True,
                'overall_score': latest_diagnostic.current_ability or 0,
                'diagnostic_date': latest_diagnostic.completed_at.isoformat() if latest_diagnostic.completed_at else None,
                'domains': []
            }
            
            # Обрабатываем все домены
            for domain_code in ALL_BIG_DOMAINS:
                domain_name = get_domain_name(domain_code)
                domain_result = DiagnosticDataManager._process_domain_data(
                    domain_code, domain_name, diagnostic_data
                )
                result['domains'].append(domain_result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting diagnostic data for user {user_id}: {str(e)}")
            return {
                'has_diagnostic': False,
                'overall_score': 0,
                'domains': [],
                'error': str(e)
            }
    
    @staticmethod
    def _process_domain_data(domain_code: str, domain_name: str, diagnostic_data: dict) -> dict:
        """
        Обработать данные для конкретного домена
        
        Args:
            domain_code: Код домена (например, 'domain_1')
            domain_name: Название домена (например, 'Endodontics')
            diagnostic_data: Данные диагностики
            
        Returns:
            Словарь с данными домена
        """
        # Инициализируем значения по умолчанию
        score = 0
        questions_answered = 0
        correct_answers = 0
        
        # Проверяем есть ли данные по этому домену
        if (diagnostic_data.get('domain_statistics') and 
            domain_code in diagnostic_data['domain_statistics']):
            
            # Есть данные для домена
            domain_data = diagnostic_data['domain_statistics'][domain_code]
            score = domain_data.get('accuracy_percentage', 0)
            questions_answered = domain_data.get('questions_answered', 0)
            correct_answers = domain_data.get('correct_answers', 0)
        elif diagnostic_data.get('domain_abilities') and domain_code in diagnostic_data['domain_abilities']:
            # Используем данные из domain_abilities как fallback
            ability = diagnostic_data['domain_abilities'][domain_code]
            score = max(0, min(100, ability * 100))  # Конвертируем в проценты
            questions_answered = diagnostic_data.get('questions_answered', 0)
            correct_answers = int(questions_answered * ability) if questions_answered > 0 else 0
        
        # Обрабатываем None значения
        if score is None:
            score = 0
        if questions_answered is None:
            questions_answered = 0
        if correct_answers is None:
            correct_answers = 0
            
        return {
            'code': domain_code,
            'name': domain_name,
            'score': score,
            'target': 85,
            'hours': max(24 - score * 0.3, 8),  # Расчет часов
            'questions_answered': questions_answered,
            'correct_answers': correct_answers,
            'has_data': questions_answered > 0
        }
    
    @staticmethod
    def get_learning_plan_data(user_id: int) -> dict:
        """
        Получить данные плана обучения пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Словарь с данными плана обучения
        """
        try:
            learning_plan = PersonalLearningPlan.query.filter_by(
                user_id=user_id,
                status='active'
            ).first()
            
            if not learning_plan:
                return {
                    'has_plan': False,
                    'plan_data': {}
                }
            
            return {
                'has_plan': True,
                'plan_data': {
                    'exam_date': learning_plan.exam_date.isoformat() if learning_plan.exam_date else None,
                    'start_date': learning_plan.start_date.isoformat() if learning_plan.start_date else None,
                    'end_date': learning_plan.end_date.isoformat() if learning_plan.end_date else None,
                    'intensity': learning_plan.intensity,
                    'study_time': learning_plan.study_time,
                    'current_ability': round(learning_plan.current_ability, 1) if learning_plan.current_ability else 0,
                    'overall_progress': round(learning_plan.overall_progress, 1) if learning_plan.overall_progress else 0,
                    'estimated_readiness': round(learning_plan.estimated_readiness, 1) if learning_plan.estimated_readiness else 0,
                    'next_diagnostic_date': learning_plan.next_diagnostic_date.isoformat() if learning_plan.next_diagnostic_date else None
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting learning plan data for user {user_id}: {str(e)}")
            return {
                'has_plan': False,
                'plan_data': {},
                'error': str(e)
            }
    
    @staticmethod
    def get_unified_user_data(user_id: int) -> dict:
        """
        Получить унифицированные данные пользователя для всех компонентов
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Словарь с унифицированными данными
        """
        diagnostic_data = DiagnosticDataManager.get_user_diagnostic_data(user_id)
        plan_data = DiagnosticDataManager.get_learning_plan_data(user_id)
        
        return {
            'user_id': user_id,
            'diagnostic': diagnostic_data,
            'learning_plan': plan_data,
            'generated_at': datetime.now(timezone.utc).isoformat()
        } 