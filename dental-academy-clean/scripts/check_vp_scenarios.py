#!/usr/bin/env python3
"""
Скрипт для проверки виртуальных пациентов в базе данных
Можно запускать на продакшене для быстрой проверки
"""
import sys
import os

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import VirtualPatientScenario, db

def check_scenarios():
    """Проверяет наличие виртуальных пациентов в БД"""
    app = create_app()
    
    with app.app_context():
        try:
            # Подсчет всех сценариев
            total_count = VirtualPatientScenario.query.count()
            print(f"\n📊 Общее количество виртуальных пациентов: {total_count}")
            
            if total_count == 0:
                print("⚠️  Виртуальных пациентов не найдено!")
                return
            
            # Подсчет опубликованных
            published_count = VirtualPatientScenario.query.filter_by(is_published=True).count()
            print(f"✅ Опубликованных: {published_count}")
            print(f"❌ Неопубликованных: {total_count - published_count}")
            
            # Группировка по специальности
            from sqlalchemy import func
            specialty_counts = db.session.query(
                VirtualPatientScenario.specialty,
                func.count(VirtualPatientScenario.id).label('count')
            ).group_by(VirtualPatientScenario.specialty).all()
            
            print(f"\n📋 По специальностям:")
            for specialty, count in specialty_counts:
                print(f"   - {specialty}: {count}")
            
            # Группировка по сложности
            difficulty_counts = db.session.query(
                VirtualPatientScenario.difficulty,
                func.count(VirtualPatientScenario.id).label('count')
            ).group_by(VirtualPatientScenario.difficulty).all()
            
            print(f"\n🎯 По сложности:")
            for difficulty, count in difficulty_counts:
                print(f"   - {difficulty}: {count}")
            
            # Список всех сценариев
            print(f"\n📝 Список всех сценариев:")
            scenarios = VirtualPatientScenario.query.order_by(VirtualPatientScenario.id).all()
            for scenario in scenarios:
                status = "✅" if scenario.is_published else "❌"
                print(f"   {status} ID: {scenario.id:3d} | {scenario.title:50s} | "
                      f"specialty: {scenario.specialty:15s} | "
                      f"difficulty: {scenario.difficulty:10s}")
            
            print("\n" + "="*80)
            
        except Exception as e:
            print(f"❌ Ошибка при проверке: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    return 0

if __name__ == '__main__':
    exit(check_scenarios())

