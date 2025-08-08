#!/usr/bin/env python3
"""
Скрипт для отладки условий завершения диагностики
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import BIGDomain, Question, DiagnosticSession, User, DiagnosticResponse
from utils.irt_engine import IRTEngine
from datetime import datetime, timezone
import json

def debug_termination_conditions():
    """Отладка условий завершения диагностики"""
    
    print("🔍 ОТЛАДКА УСЛОВИЙ ЗАВЕРШЕНИЯ ДИАГНОСТИКИ")
    print("=" * 60)
    
    with app.app_context():
        
        # Создаем тестовую сессию
        test_user = User.query.first()
        if not test_user:
            print("   ❌ Нет пользователей в базе данных")
            return
        
        # Создаем диагностическую сессию типа 'readiness'
        session = DiagnosticSession(
            user_id=test_user.id,
            session_type='diagnostic',
            test_length=130,
            time_limit=60,
            current_ability=0.0,
            ability_se=1.0,
            questions_answered=0,
            correct_answers=0,
            status='active',
            started_at=datetime.now(timezone.utc)
        )
        
        # Устанавливаем данные сессии для типа 'readiness'
        session_data = {
            'diagnostic_type': 'readiness',
            'max_questions': 130
        }
        session.session_data = json.dumps(session_data)
        
        db.session.add(session)
        db.session.commit()
        
        print(f"   ✅ Создана тестовая сессия ID: {session.id}")
        print(f"   📊 Тип диагностики: readiness (130 вопросов)")
        
        # Тестируем IRT Engine
        irt_engine = IRTEngine(session, diagnostic_type='readiness')
        
        # Проверяем начальные условия
        print(f"\n🔍 НАЧАЛЬНЫЕ УСЛОВИЯ:")
        termination_info = irt_engine._check_termination_conditions(session)
        print(f"   should_terminate: {termination_info['should_terminate']}")
        print(f"   reason: {termination_info['reason']}")
        print(f"   message: {termination_info['message']}")
        
        # Симулируем ответы на вопросы
        for i in range(1, 6):  # 5 вопросов
            print(f"\n🔍 ОТВЕТ {i}:")
            
            # Выбираем вопрос
            if i == 1:
                question = irt_engine.select_initial_question()
            else:
                question = irt_engine.select_next_question()
            
            if not question:
                print(f"   ❌ Не удалось выбрать вопрос {i}")
                break
            
            print(f"   Вопрос: ID {question.id} - {question.category}")
            print(f"   Домен: {question.big_domain.code if question.big_domain else 'Нет домена'}")
            
            # Симулируем ответ
            response = DiagnosticResponse(
                session_id=session.id,
                question_id=question.id,
                selected_answer="A",
                is_correct=True,
                response_time=30.0,
                responded_at=datetime.now(timezone.utc)
            )
            db.session.add(response)
            
            # Обновляем сессию
            session.questions_answered = i
            session.correct_answers = i
            session.current_ability = 0.5
            session.ability_se = 1.0 - (i * 0.1)  # Уменьшаем SE с каждым ответом
            db.session.commit()
            
            print(f"   Ответов: {session.questions_answered}")
            print(f"   Ability: {session.current_ability:.3f}")
            print(f"   SE: {session.ability_se:.3f}")
            
            # Проверяем условия завершения
            termination_info = irt_engine._check_termination_conditions(session)
            print(f"   should_terminate: {termination_info['should_terminate']}")
            print(f"   reason: {termination_info['reason']}")
            print(f"   message: {termination_info['message']}")
            
            if termination_info['should_terminate']:
                print(f"   ⚠️ Диагностика должна завершиться после {i} вопросов!")
                break
        
        # Очистка
        db.session.delete(session)
        db.session.commit()
        
        print(f"\n✅ Отладка завершена!")

def check_domain_coverage():
    """Проверка покрытия доменов"""
    
    print(f"\n📊 ПРОВЕРКА ПОКРЫТИЯ ДОМЕНОВ")
    print("=" * 60)
    
    with app.app_context():
        
        # Получаем все домены
        domains = BIGDomain.query.filter_by(is_active=True).all()
        
        domains_with_questions = []
        total_questions = 0
        
        for domain in domains:
            questions_count = Question.query.filter_by(big_domain_id=domain.id).count()
            total_questions += questions_count
            
            if questions_count > 0:
                domains_with_questions.append(domain.code)
                print(f"   • {domain.code}: {questions_count} вопросов")
            else:
                print(f"   • {domain.code}: 0 вопросов (пустой домен)")
        
        print(f"\n📈 СТАТИСТИКА:")
        print(f"   Всего доменов: {len(domains)}")
        print(f"   Доменов с вопросами: {len(domains_with_questions)}")
        print(f"   Всего вопросов: {total_questions}")
        print(f"   Минимум вопросов для покрытия: {len(domains_with_questions)} (по 1 на домен)")

if __name__ == "__main__":
    debug_termination_conditions()
    check_domain_coverage() 