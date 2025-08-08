#!/usr/bin/env python3
"""
Скрипт для очистки активных диагностических сессий
"""

from app import app
from models import DiagnosticSession
from datetime import datetime, timezone

def clear_active_sessions():
    """Очистить все активные диагностические сессии"""
    with app.app_context():
        # Найти все активные сессии
        active_sessions = DiagnosticSession.query.filter_by(status='active').all()
        
        print(f"Найдено активных сессий: {len(active_sessions)}")
        
        for session in active_sessions:
            print(f"Сессия {session.id} для пользователя {session.user_id}")
            print(f"  Создана: {session.started_at}")
            print(f"  Вопросов отвечено: {session.questions_answered}")
            print(f"  Правильных ответов: {session.correct_answers}")
            
            # Завершить сессию
            session.status = 'terminated'
            session.termination_reason = 'admin_clear'
            session.completed_at = datetime.now(timezone.utc)
        
        # Сохранить изменения
        from extensions import db
        db.session.commit()
        
        print(f"Очищено сессий: {len(active_sessions)}")

if __name__ == '__main__':
    clear_active_sessions() 