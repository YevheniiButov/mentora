"""
Feedback Monitor for StudySession → IRT Integration
Мониторинг и валидация обратной связи для предотвращения конфликтов
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy import and_, func
from models import StudySession, PersonalLearningPlan, StudySessionResponse
from extensions import db

logger = logging.getLogger(__name__)


class FeedbackMonitor:
    """Мониторинг обратной связи StudySession → IRT"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_pending_feedback_sessions(self, user_id: Optional[int] = None) -> List[StudySession]:
        """
        Получает сессии с необработанной обратной связью
        
        Args:
            user_id: ID пользователя (опционально)
            
        Returns:
            Список сессий с необработанной обратной связью
        """
        query = StudySession.query.filter(
            and_(
                StudySession.status == 'completed',
                StudySession.feedback_processed == False
            )
        ).order_by(StudySession.completed_at.desc())
        
        if user_id:
            query = query.join(PersonalLearningPlan).filter(
                PersonalLearningPlan.user_id == user_id
            )
        
        return query.all()
    
    def get_failed_feedback_sessions(self, hours_back: int = 24) -> List[StudySession]:
        """
        Получает сессии с неудачной обработкой обратной связи
        
        Args:
            hours_back: Количество часов назад для поиска
            
        Returns:
            Список сессий с неудачной обработкой
        """
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours_back)
        
        return StudySession.query.filter(
            and_(
                StudySession.status == 'completed',
                StudySession.feedback_processed == False,
                StudySession.completed_at >= cutoff_time,
                StudySession.questions_answered > 0
            )
        ).order_by(StudySession.completed_at.desc()).all()
    
    def validate_session_for_feedback(self, session: StudySession) -> Tuple[bool, str]:
        """
        Валидирует сессию для обработки обратной связи
        
        Args:
            session: StudySession объект
            
        Returns:
            (is_valid, error_message)
        """
        # Проверяем статус
        if session.status != 'completed':
            return False, f"Session {session.id} is not completed (status: {session.status})"
        
        # Проверяем наличие ответов
        if session.questions_answered == 0:
            return False, f"Session {session.id} has no answered questions"
        
        # Проверяем наличие плана обучения
        if not session.learning_plan:
            return False, f"Session {session.id} has no associated learning plan"
        
        # Проверяем время завершения
        if not session.completed_at:
            return False, f"Session {session.id} has no completion time"
        
        # Проверяем, не слишком ли старая сессия (больше 30 дней)
        if session.completed_at < datetime.now(timezone.utc) - timedelta(days=30):
            return False, f"Session {session.id} is too old (completed: {session.completed_at})"
        
        return True, ""
    
    def get_feedback_statistics(self, user_id: Optional[int] = None, days: int = 7) -> Dict:
        """
        Получает статистику обработки обратной связи
        
        Args:
            user_id: ID пользователя (опционально)
            days: Количество дней для анализа
            
        Returns:
            Словарь со статистикой
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        # Базовый запрос
        base_query = StudySession.query.filter(
            StudySession.completed_at >= cutoff_date
        )
        
        if user_id:
            base_query = base_query.join(PersonalLearningPlan).filter(
                PersonalLearningPlan.user_id == user_id
            )
        
        # Общая статистика
        total_sessions = base_query.count()
        completed_feedback = base_query.filter(
            StudySession.feedback_processed == True
        ).count()
        pending_feedback = base_query.filter(
            StudySession.feedback_processed == False
        ).count()
        
        # Статистика по дням
        daily_stats = db.session.query(
            func.date(StudySession.completed_at).label('date'),
            func.count(StudySession.id).label('total'),
            func.sum(func.case([(StudySession.feedback_processed == True, 1)], else_=0)).label('processed'),
            func.sum(func.case([(StudySession.feedback_processed == False, 1)], else_=0)).label('pending')
        ).filter(
            StudySession.completed_at >= cutoff_date
        )
        
        if user_id:
            daily_stats = daily_stats.join(PersonalLearningPlan).filter(
                PersonalLearningPlan.user_id == user_id
            )
        
        daily_stats = daily_stats.group_by(
            func.date(StudySession.completed_at)
        ).order_by(
            func.date(StudySession.completed_at)
        ).all()
        
        return {
            'total_sessions': total_sessions,
            'completed_feedback': completed_feedback,
            'pending_feedback': pending_feedback,
            'success_rate': (completed_feedback / total_sessions * 100) if total_sessions > 0 else 0,
            'daily_stats': [
                {
                    'date': str(stat.date),
                    'total': stat.total,
                    'processed': stat.processed,
                    'pending': stat.pending,
                    'success_rate': (stat.processed / stat.total * 100) if stat.total > 0 else 0
                }
                for stat in daily_stats
            ]
        }
    
    def detect_conflicts(self, user_id: Optional[int] = None) -> List[Dict]:
        """
        Обнаруживает потенциальные конфликты в обработке обратной связи
        
        Args:
            user_id: ID пользователя (опционально)
            
        Returns:
            Список потенциальных конфликтов
        """
        conflicts = []
        
        # Поиск сессий с дублирующимися обновлениями способности
        query = StudySession.query.filter(
            and_(
                StudySession.ability_updated == True,
                StudySession.last_ability_update.isnot(None)
            )
        )
        
        if user_id:
            query = query.join(PersonalLearningPlan).filter(
                PersonalLearningPlan.user_id == user_id
            )
        
        sessions = query.order_by(StudySession.last_ability_update.desc()).all()
        
        # Группируем по времени обновления (в пределах 1 секунды)
        time_groups = {}
        for session in sessions:
            update_time = session.last_ability_update.replace(microsecond=0)
            if update_time not in time_groups:
                time_groups[update_time] = []
            time_groups[update_time].append(session)
        
        # Находим группы с несколькими сессиями
        for update_time, session_group in time_groups.items():
            if len(session_group) > 1:
                conflicts.append({
                    'type': 'concurrent_updates',
                    'update_time': update_time.isoformat(),
                    'sessions': [
                        {
                            'session_id': s.id,
                            'user_id': s.learning_plan.user_id,
                            'ability_change': s.ability_change,
                            'version': s.version
                        }
                        for s in session_group
                    ],
                    'description': f"Multiple sessions updated ability at {update_time}"
                })
        
        return conflicts
    
    def detect_ability_update_conflicts(self) -> List[Dict]:
        """
        Обнаруживает конфликты при обновлении способностей
        
        Returns:
            Список конфликтов с деталями
        """
        try:
            conflicts = []
            
            # Проверяем планы с высокими версиями (потенциальные конфликты)
            high_version_plans = PersonalLearningPlan.query.filter(
                PersonalLearningPlan.version > 10
            ).all()
            
            for plan in high_version_plans:
                conflicts.append({
                    'type': 'high_version',
                    'plan_id': plan.id,
                    'user_id': plan.user_id,
                    'version': plan.version,
                    'description': f'Plan {plan.id} has high version {plan.version}'
                })
            
            # Проверяем сессии с неудачными обновлениями
            failed_updates = StudySession.query.filter(
                and_(
                    StudySession.status == 'completed',
                    StudySession.ability_updated == False,
                    StudySession.feedback_processed == True
                )
            ).all()
            
            for session in failed_updates:
                conflicts.append({
                    'type': 'failed_update',
                    'session_id': session.id,
                    'plan_id': session.learning_plan_id,
                    'description': f'Session {session.id} failed ability update'
                })
            
            # Проверяем одновременные обновления
            recent_updates = PersonalLearningPlan.query.filter(
                PersonalLearningPlan.last_ability_update > datetime.now(timezone.utc) - timedelta(minutes=5)
            ).all()
            
            if len(recent_updates) > 1:
                conflicts.append({
                    'type': 'concurrent_updates',
                    'count': len(recent_updates),
                    'description': f'{len(recent_updates)} plans updated in last 5 minutes'
                })
            
            return conflicts
            
        except Exception as e:
            self.logger.error(f"Error detecting conflicts: {e}")
            return []
    
    def cleanup_old_sessions(self, days: int = 90) -> int:
        """
        Очищает старые сессии (только логирование, без удаления данных)
        
        Args:
            days: Количество дней для определения "старых" сессий
            
        Returns:
            Количество старых сессий
        """
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=days)
        
        old_sessions = StudySession.query.filter(
            StudySession.completed_at < cutoff_date
        ).count()
        
        self.logger.info(f"Found {old_sessions} sessions older than {days} days")
        return old_sessions
    
    def generate_feedback_report(self, user_id: Optional[int] = None) -> Dict:
        """
        Генерирует отчет по обработке обратной связи
        
        Args:
            user_id: ID пользователя (опционально)
            
        Returns:
            Отчет в виде словаря
        """
        # Получаем статистику
        stats = self.get_feedback_statistics(user_id, days=30)
        
        # Получаем конфликты
        conflicts = self.detect_conflicts(user_id)
        
        # Получаем необработанные сессии
        pending_sessions = self.get_pending_feedback_sessions(user_id)
        
        # Получаем неудачные сессии
        failed_sessions = self.get_failed_feedback_sessions(hours_back=24)
        
        return {
            'generated_at': datetime.now(timezone.utc).isoformat(),
            'user_id': user_id,
            'statistics': stats,
            'conflicts': conflicts,
            'pending_sessions_count': len(pending_sessions),
            'failed_sessions_count': len(failed_sessions),
            'recommendations': self._generate_recommendations(stats, conflicts, pending_sessions, failed_sessions)
        }
    
    def _generate_recommendations(self, stats: Dict, conflicts: List, 
                                pending_sessions: List, failed_sessions: List) -> List[str]:
        """Генерирует рекомендации на основе анализа"""
        recommendations = []
        
        # Анализ успешности обработки
        success_rate = stats.get('success_rate', 0)
        if success_rate < 90:
            recommendations.append(f"Low feedback processing success rate: {success_rate:.1f}%. Check for system issues.")
        
        # Анализ конфликтов
        if conflicts:
            recommendations.append(f"Found {len(conflicts)} potential conflicts. Review concurrent update handling.")
        
        # Анализ необработанных сессий
        if pending_sessions:
            recommendations.append(f"Found {len(pending_sessions)} pending feedback sessions. Consider batch processing.")
        
        # Анализ неудачных сессий
        if failed_sessions:
            recommendations.append(f"Found {len(failed_sessions)} failed feedback sessions in last 24h. Investigate failures.")
        
        # Общие рекомендации
        if not recommendations:
            recommendations.append("Feedback processing is working well. No immediate action required.")
        
        return recommendations

    def get_system_health(self) -> Dict:
        """
        Получает общий статус здоровья системы обратной связи
        
        Returns:
            Словарь с информацией о здоровье системы
        """
        try:
            # Получаем статистику
            pending_sessions = self.get_pending_feedback_sessions()
            conflicts = self.detect_ability_update_conflicts()
            stuck_sessions = self.get_stuck_sessions()
            
            # Рассчитываем health score
            total_sessions = len(pending_sessions) + len(conflicts) + len(stuck_sessions)
            
            if total_sessions == 0:
                health_score = 100.0
                status = 'healthy'
            else:
                # Штрафы за проблемы
                penalty = len(pending_sessions) * 5 + len(conflicts) * 10 + len(stuck_sessions) * 15
                health_score = max(0.0, 100.0 - penalty)
                
                if health_score >= 90:
                    status = 'healthy'
                elif health_score >= 70:
                    status = 'warning'
                elif health_score >= 50:
                    status = 'error'
                else:
                    status = 'critical'
            
            return {
                'status': status,
                'health_score': health_score,
                'pending_sessions': len(pending_sessions),
                'conflicts': len(conflicts),
                'stuck_sessions': len(stuck_sessions),
                'total_issues': total_sessions,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system health: {e}")
            return {
                'status': 'error',
                'health_score': 0.0,
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

    def get_stuck_sessions(self, max_age_hours: int = 24) -> List[StudySession]:
        """
        Получает сессии, которые зависли в обработке
        
        Args:
            max_age_hours: Максимальный возраст сессии в часах
            
        Returns:
            Список зависших сессий
        """
        try:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=max_age_hours)
            
            stuck_sessions = StudySession.query.filter(
                and_(
                    StudySession.status == 'completed',
                    StudySession.feedback_processed == False,
                    StudySession.completed_at < cutoff_time
                )
            ).all()
            
            return stuck_sessions
            
        except Exception as e:
            self.logger.error(f"Error getting stuck sessions: {e}")
            return []


def monitor_feedback_health() -> Dict:
    """
    Функция для мониторинга здоровья системы обратной связи
    
    Returns:
        Отчет о состоянии системы
    """
    monitor = FeedbackMonitor()
    
    try:
        # Получаем общую статистику
        stats = monitor.get_feedback_statistics(days=7)
        
        # Получаем конфликты
        conflicts = monitor.detect_conflicts()
        
        # Получаем необработанные сессии
        pending_sessions = monitor.get_pending_feedback_sessions()
        
        # Оцениваем здоровье системы
        health_score = 100
        
        # Штраф за низкую успешность
        success_rate = stats.get('success_rate', 0)
        if success_rate < 95:
            health_score -= (95 - success_rate) * 2
        
        # Штраф за конфликты
        health_score -= len(conflicts) * 10
        
        # Штраф за необработанные сессии
        if len(pending_sessions) > 100:
            health_score -= 20
        
        health_score = max(0, health_score)
        
        return {
            'health_score': health_score,
            'status': 'healthy' if health_score >= 80 else 'warning' if health_score >= 60 else 'critical',
            'statistics': stats,
            'conflicts_count': len(conflicts),
            'pending_sessions_count': len(pending_sessions),
            'last_check': datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error monitoring feedback health: {e}")
        return {
            'health_score': 0,
            'status': 'error',
            'error': str(e),
            'last_check': datetime.now(timezone.utc).isoformat()
        } 