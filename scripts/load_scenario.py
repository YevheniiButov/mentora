# scripts/load_scenario.py

import sys
import os
import json
from datetime import datetime

# Добавляем корневую директорию проекта в путь Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import db, VirtualPatientScenario
from flask import g

def load_scenario(file_path, replace=False):
    """
    Загружает сценарий из JSON файла в базу данных
    
    Args:
        file_path (str): Путь к JSON файлу
        replace (bool): Заменить существующий сценарий с таким же названием
    """
    if not os.path.exists(file_path):
        print(f"❌ Файл {file_path} не существует!")
        return False
    
    try:
        # Загружаем данные сценария
        with open(file_path, 'r', encoding='utf-8') as f:
            scenario_data = f.read()
        
        # Проверяем, что это валидный JSON
        json_data = json.loads(scenario_data)
        
        # Извлекаем базовое название сценария
        if "default" in json_data and "patient_info" in json_data["default"]:
            title = json_data["default"]["patient_info"].get("name", "Unnamed Patient")
        else:
            # Используем имя файла, если имя не найдено
            title = os.path.basename(file_path).replace(".json", "")
        
        # Другая метаинформация
        description = "Virtual patient scenario"
        if "default" in json_data and "initial_state" in json_data["default"]:
            description = json_data["default"]["initial_state"].get("patient_statement", description)[:100] + "..."
        
        # Определяем сложность и категорию из имени файла
        filename = os.path.basename(file_path).lower()
        
        difficulty = "medium"
        if "easy" in filename:
            difficulty = "easy"
        elif "hard" in filename:
            difficulty = "hard"
        
        category = "general"
        for possible_category in ["restorative", "diagnostic", "surgical", "pediatric", "orthodontic"]:
            if possible_category in filename:
                category = possible_category
                break
        
        # Загружаем сценарий в базу данных
        with app.app_context():
            # Устанавливаем контекст для g.lang
            g.lang = 'en'
            
            # Проверяем, существует ли уже сценарий с таким названием
            existing = VirtualPatientScenario.query.filter_by(title=title).first()
            
            if existing:
                if replace:
                    print(f"Заменяем существующий сценарий '{title}'...")
                    existing.description = description
                    existing.difficulty = difficulty
                    existing.category = category
                    existing.scenario_data = scenario_data
                    db.session.commit()
                    print(f"✅ Сценарий '{title}' успешно обновлен!")
                    return True
                else:
                    print(f"Сценарий с названием '{title}' уже существует, пропускаем...")
                    return False
            
            # Создаем новый сценарий
            scenario = VirtualPatientScenario(
                title=title,
                description=description,
                difficulty=difficulty,
                category=category,
                is_premium=False,
                is_published=True,
                max_score=100,
                scenario_data=scenario_data,
                created_at=datetime.utcnow()
            )
            
            db.session.add(scenario)
            db.session.commit()
            
            print(f"✅ Сценарий '{title}' успешно добавлен!")
            return True
            
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка в формате JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка при загрузке сценария: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python load_scenario.py <путь_к_файлу> [--replace]")
        print("  --replace: заменить существующий сценарий с таким же названием")
        sys.exit(1)
    
    file_path = sys.argv[1]
    replace = "--replace" in sys.argv
    
    load_scenario(file_path, replace)