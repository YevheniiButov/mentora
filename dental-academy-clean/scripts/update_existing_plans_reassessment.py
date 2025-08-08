#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для обновления существующих планов обучения
Добавляет даты переоценки для планов без них
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import db, PersonalLearningPlan
from datetime import date, timedelta

def update_existing_plans():
    """Обновляет существующие планы обучения с датами переоценки"""
    
    with app.app_context():
        print("🔍 Начинаем обновление существующих планов обучения...")
        
        # Получаем все активные планы без даты переоценки
        plans_to_update = PersonalLearningPlan.query.filter(
            PersonalLearningPlan.status == 'active',
            PersonalLearningPlan.next_diagnostic_date.is_(None)
        ).all()
        
        print(f"🔍 Найдено планов для обновления: {len(plans_to_update)}")
        
        updated_count = 0
        for plan in plans_to_update:
            try:
                # Устанавливаем дату переоценки на 14 дней от сегодня
                plan.next_diagnostic_date = date.today() + timedelta(days=14)
                plan.diagnostic_reminder_sent = False
                
                print(f"🔍 Обновлен план {plan.id} для пользователя {plan.user_id}")
                updated_count += 1
                
            except Exception as e:
                print(f"❌ Ошибка обновления плана {plan.id}: {e}")
        
        # Сохраняем изменения
        try:
            db.session.commit()
            print(f"✅ Успешно обновлено планов: {updated_count}")
        except Exception as e:
            print(f"❌ Ошибка сохранения изменений: {e}")
            db.session.rollback()
        
        # Проверяем планы с просроченной переоценкой
        overdue_plans = PersonalLearningPlan.query.filter(
            PersonalLearningPlan.status == 'active',
            PersonalLearningPlan.next_diagnostic_date <= date.today()
        ).all()
        
        print(f"🔍 Планов с просроченной переоценкой: {len(overdue_plans)}")
        
        for plan in overdue_plans:
            print(f"⚠️  План {plan.id} (пользователь {plan.user_id}): переоценка просрочена с {plan.next_diagnostic_date}")

if __name__ == '__main__':
    update_existing_plans() 