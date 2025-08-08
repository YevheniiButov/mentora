#!/usr/bin/env python3
"""
Скрипт для проверки исправлений критических багов
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from extensions import db
from models import User, PersonalLearningPlan, Question, IRTParameters, BIGDomain
from utils.irt_calibration import calibration_service
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_personal_plans():
    """Проверить планы обучения"""
    print("🔍 Проверка планов обучения...")
    
    # Проверить планы без weak_domains
    plans_without_weak_domains = PersonalLearningPlan.query.filter(
        PersonalLearningPlan.status == 'active',
        (PersonalLearningPlan.weak_domains.is_(None) | 
         PersonalLearningPlan.weak_domains == '[]' |
         PersonalLearningPlan.weak_domains == '')
    ).count()
    
    total_active_plans = PersonalLearningPlan.query.filter_by(status='active').count()
    
    print(f"   Всего активных планов: {total_active_plans}")
    print(f"   Планов без weak_domains: {plans_without_weak_domains}")
    
    if plans_without_weak_domains == 0:
        print("   ✅ Все планы имеют weak_domains")
        return True
    else:
        print(f"   ⚠️  {plans_without_weak_domains} планов без weak_domains")
        return False

def check_irt_parameters():
    """Проверить IRT параметры"""
    print("\n🔍 Проверка IRT параметров...")
    
    # Проверить вопросы без IRT параметров
    questions_without_irt = db.session.query(Question).outerjoin(IRTParameters).filter(
        IRTParameters.id.is_(None)
    ).count()
    
    total_questions = Question.query.count()
    questions_with_irt = IRTParameters.query.count()
    
    print(f"   Всего вопросов: {total_questions}")
    print(f"   Вопросов с IRT параметрами: {questions_with_irt}")
    print(f"   Вопросов без IRT параметров: {questions_without_irt}")
    
    coverage_percent = (questions_with_irt / total_questions * 100) if total_questions > 0 else 0
    print(f"   Покрытие IRT параметрами: {coverage_percent:.1f}%")
    
    if coverage_percent >= 95:
        print("   ✅ Отличное покрытие IRT параметрами")
        return True
    elif coverage_percent >= 80:
        print("   ⚠️  Хорошее покрытие, но можно улучшить")
        return True
    else:
        print("   ❌ Низкое покрытие IRT параметрами")
        return False

def check_duplicate_routes():
    """Проверить дублирование роутов"""
    print("\n🔍 Проверка дублирования роутов...")
    
    # Проверить файлы на наличие дублирующих роутов
    route_files = [
        'routes/learning_routes.py',
        'routes/learning_routes_new.py',
        'routes/learning_map_routes.py',
        'app.py'
    ]
    
    duplicate_routes = []
    
    for file_path in route_files:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'learning-map' in content:
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if 'learning-map' in line and '@' in line:
                            duplicate_routes.append(f"{file_path}:{i+1} - {line.strip()}")
    
    print(f"   Найдено {len(duplicate_routes)} упоминаний learning-map:")
    for route in duplicate_routes[:5]:  # Показываем первые 5
        print(f"     {route}")
    
    if len(duplicate_routes) <= 3:
        print("   ✅ Минимальное дублирование роутов")
        return True
    else:
        print("   ⚠️  Обнаружено дублирование роутов")
        return False

def run_irt_calibration_test():
    """Запустить тестовую калибровку IRT"""
    print("\n🔍 Тестовая калибровка IRT...")
    
    try:
        # Получить статистику калибровки
        stats = calibration_service.get_calibration_statistics()
        
        if 'error' in stats:
            print(f"   ❌ Ошибка получения статистики: {stats['error']}")
            return False
        
        print(f"   Общая статистика:")
        print(f"     Всего вопросов: {stats['total_questions']}")
        print(f"     С IRT параметрами: {stats['questions_with_irt']}")
        print(f"     Без IRT параметров: {stats['questions_without_irt']}")
        print(f"     Общее покрытие: {stats['overall_coverage_percent']}%")
        
        # Показать статистику по доменам
        print(f"   Статистика по доменам:")
        for domain_code, domain_stats in list(stats['domain_statistics'].items())[:5]:
            print(f"     {domain_code}: {domain_stats['coverage_percent']}% "
                  f"({domain_stats['with_irt']}/{domain_stats['total_questions']})")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Ошибка тестовой калибровки: {e}")
        return False

def main():
    """Основная функция проверки"""
    print("🚀 ПРОВЕРКА ИСПРАВЛЕНИЙ КРИТИЧЕСКИХ БАГОВ")
    print("=" * 50)
    
    # Создаем минимальное Flask приложение для работы с БД
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        # Проверяем все компоненты
        plan_check = check_personal_plans()
        irt_check = check_irt_parameters()
        route_check = check_duplicate_routes()
        calibration_check = run_irt_calibration_test()
        
        print("\n" + "=" * 50)
        print("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ:")
        print(f"   Планы обучения: {'✅' if plan_check else '❌'}")
        print(f"   IRT параметры: {'✅' if irt_check else '❌'}")
        print(f"   Дублирование роутов: {'✅' if route_check else '❌'}")
        print(f"   Калибровка IRT: {'✅' if calibration_check else '❌'}")
        
        all_passed = plan_check and irt_check and route_check and calibration_check
        
        if all_passed:
            print("\n🎉 ВСЕ КРИТИЧЕСКИЕ БАГИ ИСПРАВЛЕНЫ!")
        else:
            print("\n⚠️  НЕКОТОРЫЕ ПРОБЛЕМЫ ОСТАЛИСЬ")
        
        return all_passed

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 