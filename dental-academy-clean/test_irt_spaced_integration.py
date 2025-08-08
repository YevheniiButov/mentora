#!/usr/bin/env python3
"""
Тестовый скрипт для проверки интеграции IRT + Spaced Repetition
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app
from utils.irt_spaced_integration import get_irt_spaced_integration
from models import User, Question, SpacedRepetitionItem

def test_irt_spaced_integration():
    """Тестирует интеграцию IRT + Spaced Repetition"""
    with app.app_context():
        print("=== Тестирование интеграции IRT + Spaced Repetition ===\n")
        
        # Получаем тестового пользователя
        user = User.query.first()
        if not user:
            print("❌ Нет пользователей в базе данных")
            return
        
        print(f"Тестируем с пользователем: {user.username or user.email}")
        
        # Получаем несколько вопросов для тестирования
        questions = Question.query.limit(5).all()
        if not questions:
            print("❌ Нет вопросов в базе данных")
            return
        
        print(f"Найдено {len(questions)} вопросов для тестирования\n")
        
        # Тест 1: Создание интегрированных элементов
        print("1. Тестирование создания интегрированных элементов:")
        integrated_items = []
        
        irt_spaced_integration = get_irt_spaced_integration()
        for question in questions:
            try:
                item = irt_spaced_integration.create_integrated_item(
                    question.id, user.id
                )
                integrated_items.append(item)
                print(f"   ✅ Создан элемент для вопроса {question.id}")
                print(f"      - Домен: {item.domain}")
                print(f"      - IRT сложность: {item.irt_difficulty:.3f}")
                print(f"      - Способность пользователя: {item.user_ability:.3f}")
                print(f"      - Уровень уверенности: {item.confidence_level:.3f}")
                print(f"      - Скорость обучения: {item.learning_rate:.3f}")
                print()
            except Exception as e:
                print(f"   ❌ Ошибка создания элемента для вопроса {question.id}: {e}")
        
        if not integrated_items:
            print("❌ Не удалось создать интегрированные элементы")
            return
        
        # Тест 2: Обработка ответов
        print("2. Тестирование обработки ответов:")
        
        for i, item in enumerate(integrated_items):
            try:
                # Симулируем разные качества ответов
                qualities = [5, 3, 1]  # Отличный, средний, плохой
                response_times = [10, 30, 60]  # Быстрый, средний, медленный
                
                for quality, response_time in zip(qualities, response_times):
                    old_interval = item.interval
                    old_ability = item.user_ability
                    
                    result = irt_spaced_integration.process_review_response(
                        item, quality, response_time
                    )
                    
                    if result['success']:
                        print(f"   ✅ Обработан ответ для вопроса {item.question_id}")
                        print(f"      - Качество: {quality}, Время: {response_time}с")
                        print(f"      - Старый интервал: {old_interval}, Новый: {result['new_interval']}")
                        print(f"      - Изменение способности: {result['ability_change']:.3f}")
                        print(f"      - IRT-скорректированное качество: {result['irt_adjusted_quality']:.1f}")
                        print()
                    else:
                        print(f"   ❌ Ошибка обработки ответа: {result.get('error')}")
            except Exception as e:
                print(f"   ❌ Ошибка обработки ответа для вопроса {item.question_id}: {e}")
        
        # Тест 3: Получение расписания повторений
        print("3. Тестирование получения расписания повторений:")
        
        try:
            review_schedule = irt_spaced_integration.get_optimal_review_schedule(
                user.id, max_items=10
            )
            
            print(f"   ✅ Получено расписание повторений: {len(review_schedule)} элементов")
            
            if review_schedule:
                print("   Топ элементы для повторения:")
                for i, item in enumerate(review_schedule[:3]):
                    priority_score = irt_spaced_integration._calculate_priority_score(item)
                    print(f"      {i+1}. Вопрос {item.question_id} (приоритет: {priority_score:.2f})")
                    print(f"         - Домен: {item.domain}")
                    print(f"         - Уверенность: {item.confidence_level:.1%}")
                    print(f"         - Повторений: {item.repetitions}")
            print()
            
        except Exception as e:
            print(f"   ❌ Ошибка получения расписания: {e}")
        
        # Тест 4: Генерация адаптивного плана
        print("4. Тестирование генерации адаптивного плана:")
        
        try:
            adaptive_plan = irt_spaced_integration.generate_adaptive_daily_plan(
                user.id, target_minutes=30
            )
            
            if adaptive_plan.get('success', True):
                print("   ✅ Адаптивный план создан успешно")
                print(f"      - Целевое время: {adaptive_plan.get('target_minutes')} минут")
                print(f"      - Элементы для повторения: {len(adaptive_plan.get('review_items', []))}")
                print(f"      - Новый контент: {len(adaptive_plan.get('new_content', []))}")
                
                # Показываем IRT инсайты
                irt_insights = adaptive_plan.get('irt_insights', {})
                if irt_insights:
                    print(f"      - Сильнейший домен: {irt_insights.get('strongest_domain')}")
                    print(f"      - Слабейший домен: {irt_insights.get('weakest_domain')}")
                    print(f"      - Общая способность: {irt_insights.get('overall_ability', 0):.3f}")
                
                # Показываем рекомендации
                recommendations = adaptive_plan.get('learning_recommendations', [])
                if recommendations:
                    print("      - Рекомендации:")
                    for rec in recommendations:
                        print(f"        * {rec}")
            else:
                print(f"   ❌ Ошибка создания плана: {adaptive_plan.get('error')}")
            print()
            
        except Exception as e:
            print(f"   ❌ Ошибка генерации плана: {e}")
        
        # Тест 5: Статистика
        print("5. Тестирование статистики:")
        
        try:
            # Получаем статистику повторений
            from routes.irt_spaced_routes import _get_review_statistics, _get_irt_statistics
            
            review_stats = _get_review_statistics(user.id)
            irt_stats = _get_irt_statistics(user.id)
            
            print("   ✅ Статистика получена:")
            print(f"      - Всего элементов: {review_stats.get('total_items', 0)}")
            print(f"      - Готовых к повторению: {review_stats.get('due_items', 0)}")
            print(f"      - Просроченных: {review_stats.get('overdue_items', 0)}")
            
            if irt_stats:
                print(f"      - Общая IRT способность: {irt_stats.get('overall_ability', 0):.3f}")
                print(f"      - Количество доменов: {irt_stats.get('domain_count', 0)}")
            
            print()
            
        except Exception as e:
            print(f"   ❌ Ошибка получения статистики: {e}")
        
        print("=== Тестирование завершено ===")

if __name__ == "__main__":
    test_irt_spaced_integration() 