"""
Утилита для проверки завершенности диагностики пользователя
"""
from models import DiagnosticSession, User
from extensions import db
from flask import current_app


def check_diagnostic_completed(user_id):
    """
    Проверить, прошел ли пользователь диагностику
    
    Args:
        user_id: ID пользователя
        
    Returns:
        bool: True если есть завершенная диагностическая сессия
    """
    try:
        # Проверяем наличие завершенной диагностической сессии
        # Исключаем daily_practice, так как это не диагностика
        diagnostic_session = DiagnosticSession.query.filter(
            DiagnosticSession.user_id == user_id,
            DiagnosticSession.status == 'completed',
            DiagnosticSession.completed_at.isnot(None),
            DiagnosticSession.session_type != 'daily_practice'
        ).order_by(DiagnosticSession.completed_at.desc()).first()
        
        return diagnostic_session is not None
    except Exception as e:
        current_app.logger.error(f"Error checking diagnostic completion for user {user_id}: {e}")
        return False


def requires_diagnostic_check(user):
    """
    Проверить, требуется ли пользователю пройти диагностику
    
    Args:
        user: Объект User
        
    Returns:
        bool: True если требуется диагностика
    """
    try:
        # Проверяем флаг requires_diagnostic
        if getattr(user, 'requires_diagnostic', False):
            return True
        
        # Проверяем наличие завершенной диагностики
        has_completed = check_diagnostic_completed(user.id)
        
        # Если диагностика не пройдена, требуется диагностика
        return not has_completed
    except Exception as e:
        current_app.logger.error(f"Error checking diagnostic requirement for user {user.id}: {e}")
        # В случае ошибки, требуем диагностику для безопасности
        return True


def get_diagnostic_redirect_url(lang='nl'):
    """
    Получить URL для редиректа на диагностику
    
    Args:
        lang: Язык пользователя
        
    Returns:
        str: URL для редиректа
    """
    # Используем прямой URL, так как blueprint может быть не зарегистрирован в контексте
    return f'/{lang}/big-diagnostic/start'

