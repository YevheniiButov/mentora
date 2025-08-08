#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки работы адаптивного селектора путей обучения
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from extensions import db
from models import User, PersonalLearningPlan, LearningPath, BIGDomain
from utils.adaptive_path_selector import AdaptivePathSelector
import json

def create_test_app():
    """Создает тестовое Flask приложение"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    db.init_app(app)
    
    return app

def test_adaptive_path_selector():
    """Тестирует адаптивный селектор путей"""
    app = create_test_app()
    
    with app.app_context():
        # Создаем таблицы
        db.create_all()
        
        print("🧪 Тестирование адаптивного селектора путей обучения")
        print("=" * 60)
        
        # Создаем тестового пользователя
        test_user = User(
            email='test@example.com',
            username='testuser',
            first_name='Test',
            last_name='User'
        )
        test_user.set_password('password123')
        db.session.add(test_user)
        db.session.commit()
        
        print(f"✅ Создан тестовый пользователь: {test_user.id}")
        
        # Создаем тестовый план обучения
        test_plan = PersonalLearningPlan(
            user_id=test_user.id,
            current_ability=0.5,  # Средний уровень способностей
            target_ability=1.0,   # Целевой уровень
            study_hours_per_week=20.0,
            status='active'
        )
        
        # Устанавливаем тестовые способности по доменам
        test_abilities = {
            'THER': 0.3,  # Слабый домен
            'SURG': 0.7,  # Сильный домен
            'ORTH': 0.5,  # Средний домен
            'PEDO': 0.2,  # Очень слабый домен
            'PERI': 0.6,  # Средний домен
            'ENDO': 0.4,  # Средний домен
            'RAD': 0.8,   # Сильный домен
            'ANAT': 0.5,  # Средний домен
            'PHAR': 0.3,  # Слабый домен
            'COMM': 0.6   # Средний домен
        }
        
        test_plan.set_domain_analysis(test_abilities)
        test_plan.set_weak_domains(['PEDO', 'THER', 'PHAR'])
        test_plan.set_strong_domains(['RAD', 'SURG'])
        
        db.session.add(test_plan)
        db.session.commit()
        
        print(f"✅ Создан тестовый план обучения: {test_plan.id}")
        print(f"   Текущая способность: {test_plan.current_ability}")
        print(f"   Целевая способность: {test_plan.target_ability}")
        print(f"   Слабые домены: {test_plan.get_weak_domains()}")
        print(f"   Сильные домены: {test_plan.get_strong_domains()}")
        
        # Создаем тестовые пути обучения
        test_paths = [
            {
                'id': 'path_1',
                'name': 'Базовый путь для начинающих',
                'exam_component': 'THEORETICAL',
                'exam_weight': 0.3,
                'exam_type': 'multiple_choice',
                'duration_weeks': 8,
                'total_estimated_hours': 40,
                'irt_difficulty_range': [-1.0, 0.5],
                'irt_discrimination_range': [0.5, 1.5],
                'target_ability_levels': {'beginner': -0.5, 'intermediate': 0.0},
                'adaptive_routing': {'focus_weak_domains': True},
                'modules': [
                    {'id': 1, 'title': 'Введение в теорию', 'estimated_hours': 4},
                    {'id': 2, 'title': 'Основные концепции', 'estimated_hours': 6}
                ]
            },
            {
                'id': 'path_2',
                'name': 'Продвинутый путь для опытных',
                'exam_component': 'CLINICAL',
                'exam_weight': 0.4,
                'exam_type': 'case_study',
                'duration_weeks': 12,
                'total_estimated_hours': 60,
                'irt_difficulty_range': [0.5, 2.0],
                'irt_discrimination_range': [1.0, 2.0],
                'target_ability_levels': {'intermediate': 0.5, 'advanced': 1.0},
                'adaptive_routing': {'focus_strong_domains': True},
                'modules': [
                    {'id': 3, 'title': 'Клинические случаи', 'estimated_hours': 8},
                    {'id': 4, 'title': 'Практические навыки', 'estimated_hours': 10}
                ]
            }
        ]
        
        for path_data in test_paths:
            path = LearningPath(**path_data)
            db.session.add(path)
        
        db.session.commit()
        print(f"✅ Создано {len(test_paths)} тестовых путей обучения")
        
        # Тестируем адаптивный селектор
        selector = AdaptivePathSelector()
        
        print("\n🔍 Тестирование выбора адаптивного пути...")
        
        # Тест 1: Выбор пути без указания домена
        result1 = selector.select_adaptive_path(test_user.id)
        print(f"Результат 1 (без домена): {result1.get('success', False)}")
        if result1.get('success'):
            print(f"   Выбранный путь: {result1.get('path_name', 'N/A')}")
            print(f"   Количество модулей: {result1.get('total_modules', 0)}")
            print(f"   Уровень сложности: {result1.get('difficulty_level', 'N/A')}")
        
        # Тест 2: Выбор пути для конкретного домена
        result2 = selector.select_adaptive_path(test_user.id, target_domain='THEORETICAL')
        print(f"\nРезультат 2 (домен THEORETICAL): {result2.get('success', False)}")
        if result2.get('success'):
            print(f"   Выбранный путь: {result2.get('path_name', 'N/A')}")
            print(f"   Количество модулей: {result2.get('total_modules', 0)}")
        
        # Тест 3: Обновление пути после переоценки
        print(f"\n🔍 Тестирование обновления пути после переоценки...")
        new_abilities = {
            'THER': 0.6,  # Улучшился
            'SURG': 0.8,  # Остался сильным
            'PEDO': 0.4,  # Улучшился
            'PHAR': 0.5   # Улучшился
        }
        
        result3 = selector.update_path_after_reassessment(test_user.id, new_abilities)
        print(f"Результат 3 (обновление): {result3.get('success', False)}")
        if result3.get('success'):
            print(f"   Сообщение: {result3.get('message', 'N/A')}")
        
        # Тест 4: Получение адаптивного пути через план обучения
        print(f"\n🔍 Тестирование получения пути через план обучения...")
        adaptive_path = test_plan.get_adaptive_learning_path()
        print(f"Результат 4 (через план): {adaptive_path.get('success', False)}")
        if adaptive_path.get('success'):
            print(f"   Путь: {adaptive_path.get('path_name', 'N/A')}")
            print(f"   Модули: {len(adaptive_path.get('modules', []))}")
        
        print("\n" + "=" * 60)
        print("✅ Тестирование завершено!")
        
        # Очистка
        db.session.delete(test_plan)
        db.session.delete(test_user)
        for path in LearningPath.query.all():
            db.session.delete(path)
        db.session.commit()
        
        print("🧹 Тестовые данные очищены")

if __name__ == '__main__':
    test_adaptive_path_selector() 