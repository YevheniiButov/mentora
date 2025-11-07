#!/usr/bin/env python3
"""
Скрипт для удаления вопроса по ID
"""
import sys
import os

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from extensions import db
from models import Question, DiagnosticResponse, TestAttempt
from sqlalchemy.orm import Session

def delete_question_by_id(question_id):
    """Удалить вопрос по ID"""
    with app.app_context():
        session = db.session
        question = session.get(Question, question_id)
        if not question:
            print(f"❌ Вопрос с ID {question_id} не найден")
            return False
        
        print(f"📋 Найден вопрос ID {question_id}:")
        print(f"   Текст: {question.text}")
        print(f"   Домен: {question.domain}")
        print(f"   Категория: {question.category}")
        print(f"   Варианты: {question.options}")
        
        # Показываем связанные данные
        responses_count = DiagnosticResponse.query.filter_by(question_id=question_id).count()
        attempts_count = TestAttempt.query.filter_by(question_id=question_id).count()
        
        print(f"\n📊 Связанные записи:")
        print(f"   Ответов в диагностических сессиях: {responses_count}")
        print(f"   Попыток в тестах: {attempts_count}")
        
        # Если есть связанные записи, спрашиваем подтверждение
        if responses_count > 0 or attempts_count > 0:
            print(f"\n⚠️  ВНИМАНИЕ: У вопроса есть {responses_count + attempts_count} связанных записей!")
            print("   Они также будут удалены.")
        
        # Если ID передан как аргумент, удаляем без подтверждения (для автоматизации)
        if len(sys.argv) > 2 and sys.argv[2] == '--force':
            confirm = 'yes'
        else:
            confirm = input(f"\n❓ Вы уверены, что хотите удалить вопрос ID {question_id}? (yes/y/no): ")
        
        if confirm.lower() in ('yes', 'y'):
            try:
                # Удаляем связанные записи
                if responses_count > 0:
                    DiagnosticResponse.query.filter_by(question_id=question_id).delete()
                    print(f"   ✅ Удалено {responses_count} ответов")
                
                if attempts_count > 0:
                    TestAttempt.query.filter_by(question_id=question_id).delete()
                    print(f"   ✅ Удалено {attempts_count} попыток")
                
                # Удаляем вопрос
                db.session.delete(question)
                db.session.commit()
                print(f"\n✅ Вопрос ID {question_id} успешно удален!")
                return True
            except Exception as e:
                db.session.rollback()
                print(f"\n❌ Ошибка при удалении: {e}")
                import traceback
                traceback.print_exc()
                return False
        else:
            print("❌ Удаление отменено")
            return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Использование: python3 scripts/delete_question_by_id.py <ID> [--force]")
        print("Пример: python3 scripts/delete_question_by_id.py 532")
        sys.exit(1)
    
    try:
        question_id = int(sys.argv[1])
        delete_question_by_id(question_id)
    except ValueError:
        print(f"❌ Ошибка: '{sys.argv[1]}' не является корректным ID (должно быть число)")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

