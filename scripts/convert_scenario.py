# scripts/convert_scenario.py

import sys
import os
import json
from datetime import datetime

# Добавляем корневую директорию проекта в путь Python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def convert_scenario(input_file, output_file):
    """
    Преобразует сценарий из исходного формата в формат, совместимый с модулем виртуального пациента
    
    Args:
        input_file: Путь к исходному JSON файлу
        output_file: Путь для сохранения преобразованного JSON файла
    """
    try:
        # Загружаем исходный сценарий
        with open(input_file, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
        
        # Создаем структуру нового сценария
        converted_data = {
            "default": {
                "patient_info": {
                    "name": original_data["scenario"]["default"]["patient_info"]["name"],
                    "age": original_data["scenario"]["default"]["patient_info"]["age"],
                    "gender": "male",  # Предполагаем, что Иван - мужчина
                    "image": "patient_default.jpg",  # Используем изображение по умолчанию
                    "medical_history": ", ".join(original_data["scenario"]["default"]["patient_info"]["medical_history"]["conditions"]) + 
                                      ". Принимает: " + ", ".join(original_data["scenario"]["default"]["patient_info"]["medical_history"]["medications"]) + 
                                      ". Аллергии: " + original_data["scenario"]["default"]["patient_info"]["medical_history"]["allergies"]
                },
                "initial_state": {
                    "node_id": "start",
                    "patient_statement": original_data["scenario"]["default"]["patient_info"]["initial_complaint"],
                    "patient_emotion": "concerned",
                    "notes": "Пациент с сахарным диабетом и гипертонией. Жалуется на острую пульсирующую боль в зубе 36."
                },
                "dialogue_nodes": [],
                "outcomes": {
                    "correct_diagnosis": {
                        "text": "Отлично! Вы правильно диагностировали хронический апикальный периодонтит, учли сопутствующие заболевания пациента и провели лечение с соблюдением всех мер безопасности.",
                        "min_score": 70,
                        "badge": "clinical_reasoning_1"
                    },
                    "partial_diagnosis": {
                        "text": "Вы верно поставили диагноз, но не полностью учли сопутствующие заболевания при лечении.",
                        "min_score": 40,
                        "badge": null
                    },
                    "incorrect_diagnosis": {
                        "text": "Вы не смогли правильно диагностировать периодонтит и/или не учли сопутствующие заболевания, что привело к осложнениям.",
                        "min_score": 0,
                        "badge": null
                    }
                }
            }
        }
        
        # Преобразуем узлы диалога
        for node in original_data["scenario"]["default"]["dialogue_nodes"]:
            if node["speaker"] == "system" and "is_terminal" in node and node["is_terminal"]:
                # Пропускаем терминальные узлы, так как они не нужны в новом формате
                continue
            
            converted_node = {
                "id": node["id"]
            }
            
            # Добавляем высказывание пациента, если это узел пациента
            if node["speaker"] == "patient":
                converted_node["patient_statement"] = node["text"]
                converted_node["patient_emotion"] = node.get("emotional_state", "neutral").lower().split(',')[0].strip()
            elif "observations" in node:
                converted_node["patient_statement"] = node.get("text", "")
                converted_node["notes"] = node["observations"]
            else:
                converted_node["patient_statement"] = node.get("text", "")
            
            # Преобразуем действия в опции
            if "actions" in node:
                converted_node["options"] = []
                for action in node["actions"]:
                    option = {
                        "text": action["text"],
                        "next_node": action["next_node_id"],
                        "score": action.get("evaluation", {}).get("score_delta", 0)
                    }
                    converted_node["options"].append(option)
            
            converted_data["default"]["dialogue_nodes"].append(converted_node)
        
        # Сохраняем преобразованный сценарий
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(converted_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Сценарий успешно преобразован и сохранен в {output_file}")
        return True
            
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка в формате JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка при преобразовании сценария: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Использование: python convert_scenario.py <input_file> <output_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    convert_scenario(input_file, output_file)