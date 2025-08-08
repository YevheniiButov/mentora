#!/usr/bin/env python3
"""
Финальный тест для проверки всех исправлений ежедневного плана
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import User, SpacedRepetitionItem
from utils.daily_learning_algorithm import DailyLearningAlgorithm
from datetime import datetime, timezone

def final_test():
    """Финальный тест всех исправлений"""
    
    print("🎯 ФИНАЛЬНЫЙ ТЕСТ ЕЖЕДНЕВНОГО ПЛАНА")
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
        now = datetime.now(timezone.utc)
        overdue = [i for i in items if i.next_review.replace(tzinfo=timezone.utc) < now]
        
        print(f"   📚 Просроченных элементов: {len(overdue)}")
        
        # Генерируем ежедневный план
        algorithm = DailyLearningAlgorithm()
        daily_plan_result = algorithm.generate_daily_plan(user.id, target_minutes=30)
        
        if daily_plan_result['success']:
            print("   ✅ План сгенерирован успешно")
            
            # Проверяем структуру для шаблона
            daily_plan = daily_plan_result['daily_plan']
            
            print(f"\n   📊 Результат для шаблона:")
            print(f"      daily_plan.review_section.content: {len(daily_plan['review_section']['content'])} элементов")
            
            # Показываем первые 3 элемента повторения
            review_items = daily_plan['review_section']['content'][:3]
            for i, item in enumerate(review_items):
                print(f"      {i+1}. {item['title'][:50]}... (Домен: {item['domain']}, Просрочен: {item['overdue_days']} дней)")
            
            # Проверяем условие в шаблоне
            has_content = bool(daily_plan.get('review_section', {}).get('content'))
            print(f"\n   🧪 Условие в шаблоне:")
            print(f"      daily_plan.review_section.content: {has_content}")
            
            if has_content:
                print("      ✅ Должен отображаться РЕАЛЬНЫЙ контент (не заглушки)")
            else:
                print("      ❌ Будут отображаться заглушки")
                
        else:
            print(f"   ❌ Ошибка генерации: {daily_plan_result['error']}")

if __name__ == "__main__":
    final_test() 