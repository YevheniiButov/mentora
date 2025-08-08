#!/usr/bin/env python3
"""
Скрипт для исправления irt_params на irt_parameters в JSON файлах
"""

import json
import os
import glob
from pathlib import Path

def fix_json_file(file_path):
    """Исправить irt_params на irt_parameters в JSON файле"""
    
    print(f"🔧 Исправляю файл: {file_path}")
    
    try:
        # Читаем файл
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Счетчики изменений
        changes_count = 0
        
        # Обрабатываем массив вопросов
        if isinstance(data, list):
            for question in data:
                if isinstance(question, dict) and 'irt_params' in question:
                    # Переименовываем ключ
                    question['irt_parameters'] = question.pop('irt_params')
                    changes_count += 1
                    print(f"  ✅ Исправлен вопрос ID: {question.get('id', 'unknown')}")
        
        # Обрабатываем объект с вопросами
        elif isinstance(data, dict):
            if 'questions' in data and isinstance(data['questions'], list):
                for question in data['questions']:
                    if isinstance(question, dict) and 'irt_params' in question:
                        question['irt_parameters'] = question.pop('irt_params')
                        changes_count += 1
                        print(f"  ✅ Исправлен вопрос ID: {question.get('id', 'unknown')}")
        
        # Сохраняем исправленный файл
        if changes_count > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"  💾 Сохранено {changes_count} изменений")
        else:
            print(f"  ℹ️ Изменений не найдено")
            
        return changes_count
        
    except Exception as e:
        print(f"  ❌ Ошибка при обработке файла: {str(e)}")
        return 0

def main():
    """Основная функция"""
    
    print("🔧 ИСПРАВЛЕНИЕ irt_params → irt_parameters")
    print("=" * 50)
    
    # Находим все JSON файлы в scripts/
    scripts_dir = Path("scripts")
    json_files = []
    
    # Добавляем файлы из scripts/
    json_files.extend(glob.glob("scripts/*.json"))
    
    # Добавляем файлы из подпапок scripts/
    json_files.extend(glob.glob("scripts/*/*.json"))
    
    # Добавляем файлы из cards/
    json_files.extend(glob.glob("cards/*/*.json"))
    
    print(f"📁 Найдено {len(json_files)} JSON файлов")
    print()
    
    total_changes = 0
    processed_files = 0
    
    for file_path in json_files:
        if os.path.exists(file_path):
            changes = fix_json_file(file_path)
            total_changes += changes
            processed_files += 1
            print()
    
    print("=" * 50)
    print(f"✅ ОБРАБОТКА ЗАВЕРШЕНА")
    print(f"📁 Обработано файлов: {processed_files}")
    print(f"🔧 Всего изменений: {total_changes}")
    
    if total_changes > 0:
        print("\n🎉 Все файлы успешно исправлены!")
    else:
        print("\nℹ️ Изменений не найдено - возможно, файлы уже исправлены")

if __name__ == "__main__":
    main() 