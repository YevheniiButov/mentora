#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Расширенный проверочный скрипт для тестирования интеграции системы
Проверяет полную цепочку включая переоценку и блокировку задач
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, User, DiagnosticSession, PersonalLearningPlan, UserProgress, TestAttempt, TestSession, TestResult
from datetime import datetime, timedelta, timezone
from utils.daily_learning_algorithm import DailyLearningAlgorithm
from utils.learning_plan_generator import create_learning_plan_from_diagnostic
import json

def log_step(step_name, message, data=None, status="INFO"):
    """Логирует шаг с данными и статусом"""
    status_icons = {
        "INFO": "🔍",
        "SUCCESS": "✅", 
        "WARNING": "⚠️",
        "ERROR": "❌",
        "DEBUG": "🔧"
    }
    
    icon = status_icons.get(status, "🔍")
    print(f"\n{icon} ШАГ {step_name}")
    print(f"   {message}")
    if data:
        if isinstance(data, dict):
            for key, value in data.items():
                print(f"   {key}: {value}")
        else:
            print(f"   Данные: {data}")
    print("-" * 50)

def create_test_user():
    """Создает тестового пользователя"""
    log_step("1. СОЗДАНИЕ ПОЛЬЗОВАТЕЛЯ", "Создаем тестового пользователя для проверки")
    
    # Удаляем существующего тестового пользователя
    existing_user = User.query.filter_by(email='test@integration.com').first()
    if existing_user:
        # Удаляем связанные данные
        DiagnosticSession.query.filter_by(user_id=existing_user.id).delete()
        PersonalLearningPlan.query.filter_by(user_id=existing_user.id).delete()
        UserProgress.query.filter_by(user_id=existing_user.id).delete()
        TestAttempt.query.filter_by(user_id=existing_user.id).delete()
        TestSession.query.filter_by(user_id=existing_user.id).delete()
        TestResult.query.filter_by(user_id=existing_user.id).delete()
        db.session.delete(existing_user)
        db.session.commit()
        print(f"   ✅ Удален существующий пользователь ID: {existing_user.id}")
    
    # Создаем нового пользователя
    test_user = User(
        email='test@integration.com',
        username='test_integration',
        first_name='Test',
        last_name='Integration',
        requires_diagnostic=True,
        registration_completed=True
    )
    db.session.add(test_user)
    db.session.commit()
    
    log_step("1.1 ПОЛЬЗОВАТЕЛЬ СОЗДАН", f"Пользователь ID: {test_user.id}", {
        "email": test_user.email,
        "requires_diagnostic": test_user.requires_diagnostic,
        "registration_completed": test_user.registration_completed
    }, "SUCCESS")
    
    return test_user

def create_test_diagnostic(user):
    """Создает тестовую диагностику с реальными данными"""
    log_step("2. СОЗДАНИЕ ДИАГНОСТИКИ", f"Создаем диагностику для пользователя {user.id}")
    
    # Создаем диагностическую сессию с более реалистичными данными
    test_session = DiagnosticSession(
        user_id=user.id,
        session_type='diagnostic',
        current_ability=0.45,  # Более реалистичная способность
        questions_answered=15,
        correct_answers=9,
        status='completed',
        started_at=datetime.now(timezone.utc) - timedelta(hours=1),
        completed_at=datetime.now(timezone.utc)
    )
    
    # Добавляем более детальные тестовые данные
    test_session.session_data = json.dumps({
        'domain_results': {
            'THER': {'correct': 3, 'total': 4, 'accuracy': 0.75},
            'SURG': {'correct': 2, 'total': 4, 'accuracy': 0.50},
            'ORTH': {'correct': 4, 'total': 4, 'accuracy': 1.00},
            'PEDO': {'correct': 1, 'total': 3, 'accuracy': 0.33}
        },
        'question_responses': [
            {'question_id': 1, 'selected_option': 'A', 'is_correct': True, 'response_time': 45},
            {'question_id': 2, 'selected_option': 'B', 'is_correct': False, 'response_time': 30},
            {'question_id': 3, 'selected_option': 'C', 'is_correct': True, 'response_time': 60}
        ]
    })
    
    db.session.add(test_session)
    db.session.commit()
    
    log_step("2.1 ДИАГНОСТИКА СОЗДАНА", f"Диагностика ID: {test_session.id}", {
        "current_ability": test_session.current_ability,
        "questions_answered": test_session.questions_answered,
        "correct_answers": test_session.correct_answers,
        "accuracy": f"{test_session.correct_answers/test_session.questions_answered*100:.1f}%"
    }, "SUCCESS")
    
    return test_session

def test_learning_plan_creation(user, diagnostic_session):
    """Тестирует создание плана обучения"""
    log_step("3. СОЗДАНИЕ ПЛАНА ОБУЧЕНИЯ", f"Создаем план на основе диагностики {diagnostic_session.id}")
    
    try:
        plan = create_learning_plan_from_diagnostic(
            user_id=user.id,
            diagnostic_session_id=diagnostic_session.id
        )
        
        log_step("3.1 ПЛАН СОЗДАН", f"План ID: {plan.id}", {
            "current_ability": plan.current_ability,
            "target_ability": plan.target_ability,
            "weak_domains_count": len(plan.get_weak_domains()),
            "strong_domains_count": len(plan.get_strong_domains()),
            "next_diagnostic_date": plan.next_diagnostic_date,
            "overall_progress": f"{plan.overall_progress}%"
        }, "SUCCESS")
        
        return plan
        
    except Exception as e:
        log_step("3.1 ОШИБКА СОЗДАНИЯ ПЛАНА", f"Ошибка: {e}", {}, "ERROR")
        return None

def test_daily_tasks_generation(user, learning_plan):
    """Тестирует генерацию ежедневных задач"""
    log_step("4. ГЕНЕРАЦИЯ ЕЖЕДНЕВНЫХ ЗАДАЧ", f"Генерируем задачи для плана {learning_plan.id}")
    
    try:
        algorithm = DailyLearningAlgorithm()
        daily_plan = algorithm.generate_daily_plan(
            user_id=user.id,
            target_minutes=45
        )
        
        if daily_plan.get('success'):
            daily_sections = daily_plan.get('daily_plan', {})
            section_stats = {}
            
            for section_name, section_data in daily_sections.items():
                content = section_data.get('content', [])
                section_stats[section_name] = len(content)
            
            log_step("4.1 ЗАДАЧИ СГЕНЕРИРОВАНЫ", "Ежедневный план создан", {
                "target_minutes": daily_plan.get('target_minutes'),
                "weak_domains": daily_plan.get('weak_domains', [])[:3],  # Показываем первые 3
                "sections": section_stats,
                "total_content_items": sum(section_stats.values())
            }, "SUCCESS")
            
            return daily_plan
        else:
            log_step("4.1 ОШИБКА ГЕНЕРАЦИИ", f"Ошибка: {daily_plan.get('error')}", {
                "requires_diagnostic": daily_plan.get('requires_diagnostic'),
                "requires_reassessment": daily_plan.get('requires_reassessment')
            }, "ERROR")
            return None
            
    except Exception as e:
        log_step("4.1 КРИТИЧЕСКАЯ ОШИБКА", f"Исключение: {e}", {}, "ERROR")
        return None

def test_reassessment_scenario(user, learning_plan):
    """Тестирует сценарий переоценки"""
    log_step("5. ТЕСТИРОВАНИЕ ПЕРЕОЦЕНКИ", f"Проверяем сценарий переоценки для плана {learning_plan.id}")
    
    # Устанавливаем дату переоценки в прошлое
    learning_plan.next_diagnostic_date = datetime.now(timezone.utc).date() - timedelta(days=1)
    db.session.commit()
    
    log_step("5.1 ДАТА ПЕРЕОЦЕНКИ УСТАНОВЛЕНА", "Дата переоценки установлена в прошлое", {
        "next_diagnostic_date": learning_plan.next_diagnostic_date,
        "days_overdue": 1
    }, "WARNING")
    
    # Проверяем, что алгоритм блокирует генерацию задач
    try:
        algorithm = DailyLearningAlgorithm()
        daily_plan = algorithm.generate_daily_plan(
            user_id=user.id,
            target_minutes=30
        )
        
        if not daily_plan.get('success') and daily_plan.get('requires_reassessment'):
            log_step("5.2 БЛОКИРОВКА РАБОТАЕТ", "Алгоритм правильно блокирует генерацию", {
                "success": daily_plan.get('success'),
                "requires_reassessment": daily_plan.get('requires_reassessment'),
                "redirect_url": daily_plan.get('redirect_url'),
                "error_message": daily_plan.get('error')
            }, "SUCCESS")
            
            return True
        else:
            log_step("5.2 ОШИБКА БЛОКИРОВКИ", "Алгоритм не блокирует генерацию", {
                "success": daily_plan.get('success'),
                "requires_reassessment": daily_plan.get('requires_reassessment')
            }, "ERROR")
            return False
            
    except Exception as e:
        log_step("5.2 КРИТИЧЕСКАЯ ОШИБКА", f"Исключение при проверке блокировки: {e}", {}, "ERROR")
        return False

def test_reassessment_completion(user, learning_plan):
    """Тестирует завершение переоценки"""
    log_step("6. ЗАВЕРШЕНИЕ ПЕРЕОЦЕНКИ", f"Создаем новую диагностику типа 'reassessment'")
    
    # Создаем новую диагностическую сессию типа 'reassessment'
    reassessment_session = DiagnosticSession(
        user_id=user.id,
        session_type='reassessment',
        current_ability=0.65,  # Улучшенная способность
        questions_answered=12,
        correct_answers=9,
        status='completed',
        started_at=datetime.now(timezone.utc) - timedelta(minutes=30),
        completed_at=datetime.now(timezone.utc)
    )
    
    # Добавляем данные переоценки
    reassessment_session.session_data = json.dumps({
        'domain_results': {
            'THER': {'correct': 4, 'total': 4, 'accuracy': 1.00},
            'SURG': {'correct': 3, 'total': 4, 'accuracy': 0.75},
            'ORTH': {'correct': 4, 'total': 4, 'accuracy': 1.00},
            'PEDO': {'correct': 2, 'total': 3, 'accuracy': 0.67}
        }
    })
    
    db.session.add(reassessment_session)
    db.session.commit()
    
    log_step("6.1 ПЕРЕОЦЕНКА СОЗДАНА", f"Переоценка ID: {reassessment_session.id}", {
        "current_ability": reassessment_session.current_ability,
        "improvement": f"+{reassessment_session.current_ability - 0.45:.2f}",
        "accuracy": f"{reassessment_session.correct_answers/reassessment_session.questions_answered*100:.1f}%"
    }, "SUCCESS")
    
    # Обновляем план обучения с новыми результатами
    try:
        learning_plan.current_ability = reassessment_session.current_ability
        learning_plan.diagnostic_session_id = reassessment_session.id
        learning_plan.next_diagnostic_date = datetime.now(timezone.utc).date() + timedelta(days=14)
        learning_plan.diagnostic_reminder_sent = False
        
        # Обновляем анализ доменов
        results = reassessment_session.generate_results()
        learning_plan.set_domain_analysis(results.get('domain_abilities', {}))
        learning_plan.set_weak_domains(results.get('weak_domains', []))
        learning_plan.set_strong_domains(results.get('strong_domains', []))
        
        db.session.commit()
        
        log_step("6.2 ПЛАН ОБНОВЛЕН", "План обновлен с результатами переоценки", {
            "new_current_ability": learning_plan.current_ability,
            "new_next_diagnostic_date": learning_plan.next_diagnostic_date,
            "weak_domains_count": len(learning_plan.get_weak_domains()),
            "strong_domains_count": len(learning_plan.get_strong_domains())
        }, "SUCCESS")
        
        return reassessment_session
        
    except Exception as e:
        log_step("6.2 ОШИБКА ОБНОВЛЕНИЯ", f"Ошибка обновления плана: {e}", {}, "ERROR")
        return None

def test_post_reassessment_tasks(user, learning_plan):
    """Тестирует генерацию задач после переоценки"""
    log_step("7. ЗАДАЧИ ПОСЛЕ ПЕРЕОЦЕНКИ", f"Проверяем генерацию задач после переоценки")
    
    try:
        algorithm = DailyLearningAlgorithm()
        daily_plan = algorithm.generate_daily_plan(
            user_id=user.id,
            target_minutes=30
        )
        
        if daily_plan.get('success'):
            daily_sections = daily_plan.get('daily_plan', {})
            section_stats = {}
            
            for section_name, section_data in daily_sections.items():
                content = section_data.get('content', [])
                section_stats[section_name] = len(content)
            
            log_step("7.1 ЗАДАЧИ ВОССТАНОВЛЕНЫ", "Задачи генерируются после переоценки", {
                "success": daily_plan.get('success'),
                "target_minutes": daily_plan.get('target_minutes'),
                "sections": section_stats,
                "total_content_items": sum(section_stats.values())
            }, "SUCCESS")
            
            return True
        else:
            log_step("7.1 ОШИБКА ВОССТАНОВЛЕНИЯ", f"Задачи не генерируются: {daily_plan.get('error')}", {
                "success": daily_plan.get('success'),
                "requires_diagnostic": daily_plan.get('requires_diagnostic'),
                "requires_reassessment": daily_plan.get('requires_reassessment')
            }, "ERROR")
            return False
            
    except Exception as e:
        log_step("7.1 КРИТИЧЕСКАЯ ОШИБКА", f"Исключение: {e}", {}, "ERROR")
        return False

def run_integration_test():
    """Запускает полный тест интеграции"""
    print("🚀 РАСШИРЕННАЯ ПРОВЕРКА ИНТЕГРАЦИИ СИСТЕМЫ")
    print("=" * 70)
    
    with app.app_context():
        try:
            # Шаг 1: Создание пользователя
            user = create_test_user()
            if not user:
                return False
            
            # Шаг 2: Создание диагностики
            diagnostic_session = create_test_diagnostic(user)
            if not diagnostic_session:
                return False
            
            # Шаг 3: Создание плана обучения
            learning_plan = test_learning_plan_creation(user, diagnostic_session)
            if not learning_plan:
                return False
            
            # Шаг 4: Генерация ежедневных задач
            daily_plan = test_daily_tasks_generation(user, learning_plan)
            if not daily_plan:
                return False
            
            # Шаг 5: Тестирование сценария переоценки
            reassessment_blocked = test_reassessment_scenario(user, learning_plan)
            if not reassessment_blocked:
                return False
            
            # Шаг 6: Завершение переоценки
            reassessment_session = test_reassessment_completion(user, learning_plan)
            if not reassessment_session:
                return False
            
            # Шаг 7: Восстановление генерации задач
            tasks_restored = test_post_reassessment_tasks(user, learning_plan)
            if not tasks_restored:
                return False
            
            print("\n🎉 РАСШИРЕННАЯ ИНТЕГРАЦИЯ ПРОШЛА УСПЕШНО!")
            print("✅ Все компоненты работают корректно")
            print("✅ Система переоценки функционирует")
            print("✅ Блокировка и восстановление задач работает")
            
            return True
            
        except Exception as e:
            print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = run_integration_test()
    if success:
        print("\n✅ Расширенная проверка завершена успешно")
        sys.exit(0)
    else:
        print("\n❌ Расширенная проверка завершена с ошибками")
        sys.exit(1) 