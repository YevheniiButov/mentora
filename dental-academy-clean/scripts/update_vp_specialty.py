#!/usr/bin/env python3
"""
Скрипт для обновления specialty виртуальных пациентов
Пример использования:
    python scripts/update_vp_specialty.py --scenario-id 4 --specialty general_practice
    python scripts/update_vp_specialty.py --all --specialty general_practice
"""
import sys
import os
import argparse

# Добавляем корневую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import VirtualPatientScenario, db

def update_specialty(scenario_id=None, specialty=None, all_scenarios=False):
    """Обновляет specialty для сценариев"""
    app = create_app()
    
    with app.app_context():
        try:
            if all_scenarios:
                scenarios = VirtualPatientScenario.query.all()
                print(f"\n📝 Найдено {len(scenarios)} сценариев для обновления")
            elif scenario_id:
                scenarios = [VirtualPatientScenario.query.get(scenario_id)]
                if not scenarios[0]:
                    print(f"❌ Сценарий с ID {scenario_id} не найден!")
                    return 1
            else:
                print("❌ Укажите --scenario-id или --all")
                return 1
            
            if not specialty:
                print("❌ Укажите --specialty (dentistry, general_practice, pharmacy, nursing)")
                return 1
            
            valid_specialties = ['dentistry', 'general_practice', 'pharmacy', 'nursing']
            if specialty not in valid_specialties:
                print(f"❌ Неверная specialty. Допустимые: {', '.join(valid_specialties)}")
                return 1
            
            updated = 0
            for scenario in scenarios:
                old_specialty = scenario.specialty
                scenario.specialty = specialty
                db.session.add(scenario)
                updated += 1
                print(f"   ✅ ID {scenario.id:3d} | {scenario.title:50s} | "
                      f"{old_specialty:15s} → {specialty}")
            
            db.session.commit()
            print(f"\n✅ Обновлено {updated} сценариев")
            print(f"📊 Новая specialty: {specialty}")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Ошибка при обновлении: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Обновить specialty виртуальных пациентов')
    parser.add_argument('--scenario-id', type=int, help='ID сценария для обновления')
    parser.add_argument('--all', action='store_true', help='Обновить все сценарии')
    parser.add_argument('--specialty', required=True, 
                       choices=['dentistry', 'general_practice', 'pharmacy', 'nursing'],
                       help='Новая specialty')
    
    args = parser.parse_args()
    
    exit(update_specialty(
        scenario_id=args.scenario_id,
        specialty=args.specialty,
        all_scenarios=args.all
    ))

