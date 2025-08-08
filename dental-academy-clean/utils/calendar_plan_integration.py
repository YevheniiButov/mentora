"""
Интеграция планов обучения с календарем
Безопасная интеграция DailyLearningAlgorithm в календарь
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
from models import User, PersonalLearningPlan, StudySession
from utils.daily_learning_algorithm import DailyLearningAlgorithm

logger = logging.getLogger(__name__)

class CalendarPlanIntegration:
    """Интеграция планов обучения с календарем"""
    
    def __init__(self):
        self.algorithm = DailyLearningAlgorithm()
    
    def get_detailed_plan_for_calendar(self, user_id: int, target_minutes: int = 30) -> Dict:
        """
        Получить детальный план для отображения в календаре
        
        Args:
            user_id: ID пользователя
            target_minutes: Целевое время в минутах
            
        Returns:
            Словарь с детальным планом
        """
        try:
            # Генерируем план через DailyLearningAlgorithm
            plan_result = self.algorithm.generate_daily_plan(user_id, target_minutes)
            
            if not plan_result.get('success'):
                return {
                    'success': False,
                    'error': plan_result.get('error', 'Неизвестная ошибка'),
                    'requires_diagnostic': plan_result.get('requires_diagnostic', False)
                }
            
            # Форматируем для календаря
            calendar_plan = self._format_plan_for_calendar(plan_result)
            
            return {
                'success': True,
                'plan': calendar_plan,
                'generated_at': plan_result.get('generated_at'),
                'total_time': plan_result.get('total_estimated_time', 0)
            }
            
        except Exception as e:
            logger.error(f"Error generating detailed plan for user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'requires_diagnostic': True
            }
    
    def _format_plan_for_calendar(self, plan_result: Dict) -> Dict:
        """
        Форматировать план для отображения в календаре
        
        Args:
            plan_result: Результат DailyLearningAlgorithm
            
        Returns:
            Отформатированный план
        """
        daily_plan = plan_result.get('daily_plan', {})
        
        formatted_plan = {
            'sections': {},
            'summary': {
                'total_time': plan_result.get('total_estimated_time', 0),
                'weak_domains': plan_result.get('weak_domains', []),
                'abilities': plan_result.get('abilities', {})
            }
        }
        
        # Форматируем каждую секцию
        for section_type, section_data in daily_plan.items():
            if isinstance(section_data, dict) and 'items' in section_data:
                formatted_plan['sections'][section_type] = {
                    'title': section_data.get('title', section_type.title()),
                    'total_items': section_data.get('total_items', 0),
                    'estimated_time': section_data.get('estimated_time', 0),
                    'items': self._format_section_items(section_data.get('items', []), section_type)
                }
        
        return formatted_plan
    
    def _format_section_items(self, items: List[Dict], section_type: str) -> List[Dict]:
        """
        Форматировать элементы секции для календаря
        
        Args:
            items: Список элементов
            section_type: Тип секции
            
        Returns:
            Отформатированные элементы
        """
        formatted_items = []
        
        for item in items:
            formatted_item = {
                'id': item.get('id'),
                'title': item.get('title', 'Без названия'),
                'domain': item.get('domain', 'GENERAL'),
                'difficulty': item.get('difficulty', 'medium'),
                'estimated_time': item.get('estimated_time', 15),
                'type': item.get('type', section_type),
                'description': item.get('description', ''),
                'url': self._generate_content_url(item, section_type)
            }
            formatted_items.append(formatted_item)
        
        return formatted_items
    
    def _generate_content_url(self, item: Dict, section_type: str) -> str:
        """
        Генерировать URL для контента
        
        Args:
            item: Элемент контента
            section_type: Тип секции
            
        Returns:
            URL для контента
        """
        content_id = item.get('id')
        content_type = item.get('type', section_type)
        
        if content_type == 'lesson':
            return f'/learning/lesson/{content_id}'
        elif content_type == 'question':
            return f'/learning/practice/{content_id}'
        elif content_type == 'review':
            return f'/learning/review/{content_id}'
        else:
            return f'/learning/{content_type}/{content_id}'
    
    def get_user_study_sessions(self, user_id: int, days: int = 7) -> List[Dict]:
        """
        Получить сессии обучения пользователя для календаря
        
        Args:
            user_id: ID пользователя
            days: Количество дней назад
            
        Returns:
            Список сессий
        """
        try:
            # Получаем активный план
            active_plan = PersonalLearningPlan.query.filter_by(
                user_id=user_id,
                status='active'
            ).first()
            
            if not active_plan:
                return []
            
            # Получаем сессии за последние дни
            start_date = datetime.now(timezone.utc) - timedelta(days=days)
            
            # Проверяем, есть ли атрибут created_at
            if hasattr(StudySession, 'created_at'):
                sessions = StudySession.query.filter(
                    StudySession.learning_plan_id == active_plan.id,
                    StudySession.created_at >= start_date
                ).order_by(StudySession.created_at.desc()).all()
            else:
                # Если нет created_at, получаем все сессии
                sessions = StudySession.query.filter(
                    StudySession.learning_plan_id == active_plan.id
                ).all()
            
            # Форматируем для календаря
            calendar_sessions = []
            for session in sessions:
                # Используем текущее время, если нет created_at
                session_time = session.created_at if hasattr(session, 'created_at') and session.created_at else datetime.now(timezone.utc)
                
                calendar_session = {
                    'id': session.id,
                    'title': f"{session.session_type.title()} - {session.domain.name if session.domain else 'General'}",
                    'start': session_time.isoformat(),
                    'end': (session_time + timedelta(minutes=session.planned_duration or 0)).isoformat(),
                    'duration': session.planned_duration or 0,
                    'type': session.session_type,
                    'status': session.status,
                    'domain': session.domain.name if session.domain else 'General',
                    'difficulty': session.difficulty_level or 0.0
                }
                calendar_sessions.append(calendar_session)
            
            return calendar_sessions
            
        except Exception as e:
            logger.error(f"Error getting study sessions for user {user_id}: {str(e)}")
            return []
    
    def get_plan_statistics(self, user_id: int) -> Dict:
        """
        Получить статистику плана обучения
        
        Args:
            user_id: ID пользователя
            
        Returns:
            Статистика плана
        """
        try:
            # Получаем активный план
            active_plan = PersonalLearningPlan.query.filter_by(
                user_id=user_id,
                status='active'
            ).first()
            
            if not active_plan:
                return {
                    'success': False,
                    'error': 'Нет активного плана обучения'
                }
            
            # Получаем сессии
            sessions = StudySession.query.filter_by(
                learning_plan_id=active_plan.id
            ).all()
            
            # Подсчитываем статистику
            total_sessions = len(sessions)
            completed_sessions = len([s for s in sessions if s.status == 'completed'])
            total_time = sum(s.planned_duration or 0 for s in sessions)
            completed_time = sum(s.actual_duration or 0 for s in sessions if s.status == 'completed')
            
            # Статистика по доменам
            domain_stats = {}
            for session in sessions:
                domain_name = session.domain.name if session.domain else 'General'
                if domain_name not in domain_stats:
                    domain_stats[domain_name] = {
                        'total_sessions': 0,
                        'completed_sessions': 0,
                        'total_time': 0,
                        'completed_time': 0
                    }
                
                domain_stats[domain_name]['total_sessions'] += 1
                domain_stats[domain_name]['total_time'] += session.planned_duration or 0
                
                if session.status == 'completed':
                    domain_stats[domain_name]['completed_sessions'] += 1
                    domain_stats[domain_name]['completed_time'] += session.actual_duration or 0
            
            return {
                'success': True,
                'total_sessions': total_sessions,
                'completed_sessions': completed_sessions,
                'completion_rate': (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0,
                'total_time': total_time,
                'completed_time': completed_time,
                'time_completion_rate': (completed_time / total_time * 100) if total_time > 0 else 0,
                'domain_stats': domain_stats
            }
            
        except Exception as e:
            logger.error(f"Error getting plan statistics for user {user_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            } 