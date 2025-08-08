#!/usr/bin/env python3
"""
Скрипт для отладки генерации ежедневного плана
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, SpacedRepetitionItem
from utils.daily_learning_algorithm import DailyLearningAlgorithm
from datetime import datetime, timezone

def debug_daily_plan():
    """Отладка генерации ежедневного плана"""
    
    print("🔍 ОТЛАДКА ГЕНЕРАЦИИ ЕЖЕДНЕВНОГО ПЛАНА")
    print("=" * 60)
    
    with app.app_context():
        
        # Получаем пользователя
        user = User.query.first()
        if not user:
            print("   ❌ Нет пользователей в базе данных")
            return
        
        print(f"   👤 Пользователь ID: {user.id}")
        
        # Проверяем Spaced Repetition элементы
        items = SpacedRepetitionItem.query.filter_by(user_id=user.id).all()
        print(f"   📚 Всего элементов Spaced Repetition: {len(items)}")
        
        now = datetime.now(timezone.utc)
        overdue = [i for i in items if i.next_review.replace(tzinfo=timezone.utc) < now]
        print(f"   ⏰ Просроченных элементов: {len(overdue)}")
        
        # Показываем детали просроченных элементов
        for i, item in enumerate(overdue[:3]):
            overdue_days = (now - item.next_review.replace(tzinfo=timezone.utc)).days
            print(f"      {i+1}. Вопрос {item.question_id} (Домен: {item.domain}) - просрочен на {overdue_days} дней")
        
        # Генерируем ежедневный план
        print("\n   🎯 Генерация ежедневного плана...")
        algorithm = DailyLearningAlgorithm()
        daily_plan = algorithm.generate_daily_plan(user.id, target_minutes=30)
        
        if daily_plan['success']:
            print("   ✅ План сгенерирован успешно")
            
            # Проверяем секции
            daily_plan_data = daily_plan['daily_plan']
            
            print(f"   📖 Теория: {len(daily_plan_data['theory_section']['content'])} элементов")
            print(f"   ✏️ Практика: {len(daily_plan_data['practice_section']['content'])} элементов")
            print(f"   🔄 Повторение: {len(daily_plan_data['review_section']['content'])} элементов")
            
            # Показываем детали секции повторения
            review_section = daily_plan_data['review_section']
            print(f"\n   🔍 Детали секции повторения:")
            print(f"      Время: {review_section['estimated_time']} минут")
            
            if review_section['content']:
                for i, item in enumerate(review_section['content']):
                    print(f"      {i+1}. {item['title']} (Домен: {item['domain']}, Просрочен: {item['overdue_days']} дней)")
            else:
                print("      ❌ Секция повторения пуста!")
                
        else:
            print(f"   ❌ Ошибка генерации: {daily_plan['error']}")

if __name__ == "__main__":
    debug_daily_plan() 