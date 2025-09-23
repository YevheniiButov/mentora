#!/usr/bin/env python3
"""
Скрипт для объединения 90 вопросов из дополнительных доменов в один JSON файл
"""

import json
import os
from pathlib import Path

def load_questions_from_file(file_path):
    """Загружает вопросы из JSON файла"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            questions = json.load(f)
        return questions
    except Exception as e:
        print(f"❌ Ошибка загрузки {file_path}: {e}")
        return []

def combine_all_questions():
    """Объединяет все 90 вопросов в один JSON файл"""
    domains_dir = Path("scripts/new_domains")
    
    # Список файлов с вопросами
    domain_files = [
        "communication_questions.json",
        "practical_theory_questions.json", 
        "research_method_questions.json",
        "statistics_questions.json",
        "treatment_planning_questions.json"
    ]
    
    all_questions = []
    total_questions = 0
    
    print("🔄 Объединение 90 вопросов из дополнительных доменов...")
    
    for filename in domain_files:
        file_path = domains_dir / filename
        if file_path.exists():
            questions = load_questions_from_file(file_path)
            domain_name = filename.replace("_questions.json", "").replace("_", " ").title()
            
            print(f"✅ {domain_name}: {len(questions)} вопросов")
            all_questions.extend(questions)
            total_questions += len(questions)
        else:
            print(f"❌ Файл не найден: {filename}")
    
    # Сортируем по ID
    all_questions.sort(key=lambda x: x.get('id', 0))
    
    # Создаем итоговый JSON
    output_data = {
        "metadata": {
            "version": "1.0",
            "total_questions": total_questions,
            "domains_count": len(domain_files),
            "created_date": "2025-01-27",
            "description": "90 вопросов из дополнительных доменов для IRT системы",
            "source_files": domain_files
        },
        "questions": all_questions
    }
    
    # Сохраняем в файл
    output_file = "90_questions_combined.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n🎯 ИТОГО: {total_questions} вопросов объединено")
    print(f"📄 Сохранено в: {output_file}")
    
    return output_file, total_questions

def main():
    """Основная функция"""
    print("🚀 ОБЪЕДИНЕНИЕ 90 ВОПРОСОВ В JSON")
    print("=" * 40)
    
    output_file, total = combine_all_questions()
    
    if total > 0:
        print(f"\n✅ УСПЕШНО СОЗДАН JSON ФАЙЛ:")
        print(f"   📄 Файл: {output_file}")
        print(f"   📊 Вопросов: {total}")
        print(f"   🎯 Готов к использованию в IRT системе")
        
        # Показываем размер файла
        file_size = os.path.getsize(output_file)
        print(f"   📏 Размер: {file_size:,} байт")
        
        # Показываем пример структуры
        print(f"\n📋 СТРУКТУРА ФАЙЛА:")
        print(f"   ├── metadata (информация о файле)")
        print(f"   └── questions (массив из {total} вопросов)")
        
        print(f"\n🎯 Файл готов для использования в IRT системе!")
    else:
        print("❌ Не удалось объединить вопросы")

if __name__ == "__main__":
    main()
