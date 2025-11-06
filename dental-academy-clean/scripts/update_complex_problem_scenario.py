#!/usr/bin/env python3
"""
Скрипт для обновления сценария "Complex Dental Problem" в БД
Исправляет ошибку с отсутствующим узлом treatment_success_path
"""

import sys
import os
import json

# Добавляем путь к корню проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from extensions import db
from models import VirtualPatientScenario

def update_complex_problem_scenario():
    """Обновить сценарий Complex Problem из JSON файла"""
    
    app = create_app()
    
    with app.app_context():
        # Путь к JSON файлу
        json_path = os.path.join(os.path.dirname(__file__), '..', 'cards', 'virtual_patient', 'complex_problem.json')
        
        # Читаем JSON
        print(f"📖 Читаю файл: {json_path}")
        with open(json_path, 'r', encoding='utf-8') as f:
            scenario_json = json.load(f)
        
        # Ищем сценарий в БД по title (голландская версия)
        nl_title = scenario_json['title']['nl']
        print(f"🔍 Ищу сценарий с title: {nl_title}")
        
        scenario = VirtualPatientScenario.query.filter_by(title=nl_title).first()
        
        if not scenario:
            print(f"❌ Сценарий '{nl_title}' не найден в БД")
            print(f"Доступные сценарии:")
            all_scenarios = VirtualPatientScenario.query.all()
            for s in all_scenarios:
                print(f"  - {s.title} (ID: {s.id})")
            return False
        
        print(f"✅ Нашел сценарий: ID={scenario.id}, title={scenario.title}")
        
        # Обновляем scenario_data
        old_data = json.loads(scenario.scenario_data)
        print(f"📝 Старая структура: {list(old_data.keys())}")
        
        # Обновляем
        scenario.scenario_data = json.dumps(scenario_json, ensure_ascii=False)
        
        # Проверяем обновленные данные
        new_data = json.loads(scenario.scenario_data)
        nl_nodes = new_data['scenario_data']['translations']['nl']['dialogue_nodes']
        print(f"✅ Новая структура содержит {len(nl_nodes)} узлов")
        
        # Проверяем, что treatment_success_path больше нет
        found_bad_ref = False
        for node in nl_nodes:
            for option in node.get('options', []):
                if option.get('next_node') == 'treatment_success_path':
                    print(f"❌ Найдена ссылка на treatment_success_path в узле: {node['id']}")
                    found_bad_ref = True
        
        if not found_bad_ref:
            print("✅ Все ссылки на несуществующие узлы исправлены")
        
        # Сохраняем
        db.session.commit()
        print(f"💾 Сценарий успешно обновлен в БД")
        
        return True

if __name__ == '__main__':
    print("=" * 60)
    print("Обновление сценария Virtual Patient: Complex Problem")
    print("=" * 60)
    
    success = update_complex_problem_scenario()
    
    if success:
        print("\n✅ Обновление завершено успешно!")
        print("Теперь можно протестировать сценарий на продакшене")
    else:
        print("\n❌ Обновление не удалось")
        sys.exit(1)


