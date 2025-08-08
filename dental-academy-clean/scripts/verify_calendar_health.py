#!/usr/bin/env python3
"""
Скрипт для проверки работоспособности календаря
Запускайте этот скрипт после любых изменений!
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from utils.diagnostic_data_manager import DiagnosticDataManager
from utils.domain_mapping import get_domain_name, ALL_BIG_DOMAINS
from models import User, DiagnosticSession

def check_diagnostic_data_manager():
    """Проверить DiagnosticDataManager"""
    print("🔍 Проверка DiagnosticDataManager...")
    
    try:
        with app.app_context():
            # Проверяем данные для пользователя 6
            data = DiagnosticDataManager.get_user_diagnostic_data(6)
            
            if not data.get('has_diagnostic'):
                print("❌ Нет данных диагностики")
                return False
                
            domains = data.get('domains', [])
            if len(domains) != 28:
                print(f"❌ Неправильное количество доменов: {len(domains)} (ожидается 28)")
                return False
                
            domains_with_data = [d for d in domains if d.get('score', 0) > 0]
            if len(domains_with_data) == 0:
                print("❌ Нет доменов с данными")
                return False
                
            print(f"✅ DiagnosticDataManager работает: {len(domains_with_data)} доменов с данными")
            return True
            
    except Exception as e:
        print(f"❌ Ошибка в DiagnosticDataManager: {e}")
        return False

def check_domain_mapping():
    """Проверить маппинг доменов"""
    print("🔍 Проверка маппинга доменов...")
    
    try:
        # Проверяем количество доменов
        if len(ALL_BIG_DOMAINS) != 28:
            print(f"❌ Неправильное количество доменов: {len(ALL_BIG_DOMAINS)} (ожидается 28)")
            return False
            
        # Проверяем названия доменов
        test_domains = ['THER', 'SURG', 'PROTH', 'PEDI', 'PARO']
        for domain_code in test_domains:
            name = get_domain_name(domain_code)
            if not name or name == domain_code:
                print(f"❌ Неправильное название для {domain_code}: {name}")
                return False
                
        print("✅ Маппинг доменов работает корректно")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в маппинге доменов: {e}")
        return False

def check_database_data():
    """Проверить данные в базе данных"""
    print("🔍 Проверка данных в базе данных...")
    
    try:
        with app.app_context():
            # Проверяем пользователя
            user = User.query.get(6)
            if not user:
                print("❌ Пользователь 6 не найден")
                return False
                
            # Проверяем диагностические сессии
            sessions = DiagnosticSession.query.filter_by(user_id=6, status='completed').all()
            if len(sessions) == 0:
                print("❌ Нет завершенных диагностических сессий")
                return False
                
            latest_session = max(sessions, key=lambda s: s.questions_answered)
            if latest_session.questions_answered < 10:
                print(f"❌ Недостаточно вопросов в последней сессии: {latest_session.questions_answered}")
                return False
                
            print(f"✅ Данные в БД корректны: {len(sessions)} сессий, {latest_session.questions_answered} вопросов")
            return True
            
    except Exception as e:
        print(f"❌ Ошибка при проверке БД: {e}")
        return False

def check_learning_plan_data():
    """Проверить данные плана обучения"""
    print("🔍 Проверка данных плана обучения...")
    
    try:
        with app.app_context():
            plan_data = DiagnosticDataManager.get_learning_plan_data(6)
            
            if not plan_data.get('has_plan'):
                print("❌ Нет активного плана обучения")
                return False
                
            plan_info = plan_data.get('plan_data', {})
            if not plan_info.get('exam_date'):
                print("❌ Нет даты экзамена в плане")
                return False
                
            print(f"✅ План обучения корректен: экзамен {plan_info.get('exam_date')}")
            return True
            
    except Exception as e:
        print(f"❌ Ошибка при проверке плана обучения: {e}")
        return False

def main():
    """Основная функция проверки"""
    print("🏥 ПРОВЕРКА РАБОТОСПОСОБНОСТИ КАЛЕНДАРЯ")
    print("=" * 50)
    
    checks = [
        check_domain_mapping,
        check_database_data,
        check_diagnostic_data_manager,
        check_learning_plan_data
    ]
    
    passed = 0
    total = len(checks)
    
    for check in checks:
        if check():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 РЕЗУЛЬТАТ: {passed}/{total} проверок пройдено")
    
    if passed == total:
        print("✅ КАЛЕНДАРЬ РАБОТАЕТ КОРРЕКТНО!")
        print("🌐 URL: http://127.0.0.1:5000/dashboard/learning-planner/26")
        return True
    else:
        print("❌ ЕСТЬ ПРОБЛЕМЫ! Проверьте логи выше.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 