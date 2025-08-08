#!/usr/bin/env python3
"""
Скрипт для очистки активных диагностических сессий в продакшене
"""

import os
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.append(str(Path(__file__).parent))

# Устанавливаем переменную окружения для продакшена
os.environ['FLASK_ENV'] = 'production'

from app import app
from models import DiagnosticSession, Question
from extensions import db
from datetime import datetime, timezone

def clear_active_sessions():
    """Очистить все активные диагностические сессии"""
    with app.app_context():
        try:
            # Проверяем подключение к базе данных
            print("🔍 Проверяем подключение к базе данных...")
            
            # Проверяем количество вопросов
            questions_count = Question.query.count()
            print(f"📊 Вопросов в базе данных: {questions_count}")
            
            # Находим все активные сессии
            active_sessions = DiagnosticSession.query.filter_by(status='active').all()
            print(f"🔍 Найдено активных сессий: {len(active_sessions)}")
            
            if not active_sessions:
                print("✅ Активных сессий не найдено")
                return
            
            for session in active_sessions:
                print(f"📋 Сессия {session.id} для пользователя {session.user_id}")
                print(f"   Создана: {session.started_at}")
                print(f"   Вопросов отвечено: {session.questions_answered}")
                print(f"   Правильных ответов: {session.correct_answers}")
                
                # Завершаем сессию
                session.status = 'terminated'
                session.termination_reason = 'admin_clear'
                session.completed_at = datetime.now(timezone.utc)
            
            # Сохраняем изменения
            db.session.commit()
            
            print(f"✅ Очищено сессий: {len(active_sessions)}")
            
        except Exception as e:
            print(f"❌ Ошибка при очистке сессий: {e}")
            db.session.rollback()
            raise

def check_database_status():
    """Проверяем статус базы данных"""
    with app.app_context():
        try:
            print("🔍 Проверяем статус базы данных...")
            
            # Проверяем количество вопросов
            questions_count = Question.query.count()
            print(f"📊 Вопросов в базе данных: {questions_count}")
            
            # Проверяем активные сессии
            active_sessions = DiagnosticSession.query.filter_by(status='active').all()
            print(f"🔍 Активных сессий: {len(active_sessions)}")
            
            if active_sessions:
                print("📋 Детали активных сессий:")
                for session in active_sessions:
                    print(f"   - Сессия {session.id}: пользователь {session.user_id}, "
                          f"вопросов: {session.questions_answered}, "
                          f"создана: {session.started_at}")
            
            return questions_count, len(active_sessions)
            
        except Exception as e:
            print(f"❌ Ошибка при проверке базы данных: {e}")
            return 0, 0

if __name__ == '__main__':
    print("🚀 Скрипт очистки активных сессий для продакшена")
    print("=" * 50)
    
    # Сначала проверяем статус
    questions_count, active_count = check_database_status()
    
    if active_count > 0:
        print(f"\n🔧 Найдено {active_count} активных сессий. Очищаем...")
        clear_active_sessions()
        
        # Проверяем результат
        print("\n🔍 Проверяем результат...")
        check_database_status()
    else:
        print("\n✅ Активных сессий не найдено. Очистка не требуется.")
    
    print("\n✅ Скрипт завершен") 