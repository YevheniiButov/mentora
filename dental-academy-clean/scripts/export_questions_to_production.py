#!/usr/bin/env python3
"""
Экспорт вопросов из локальной БД в JSON для загрузки на продакшн
"""
import os
import sys
import json
import sqlite3
from datetime import datetime
from pathlib import Path

def export_questions_from_sqlite():
    """Экспортировать все вопросы из локальной SQLite БД"""
    
    # Путь к локальной БД
    local_db = 'instance/dental_academy_clean.db'
    
    if not os.path.exists(local_db):
        print(f"❌ Локальная БД не найдена: {local_db}")
        return None
    
    print(f"📂 Подключение к локальной БД: {local_db}")
    
    conn = sqlite3.connect(local_db)
    conn.row_factory = sqlite3.Row  # Возвращать строки как словари
    cursor = conn.cursor()
    
    # Получить общее количество вопросов
    cursor.execute('SELECT COUNT(*) FROM questions')
    total = cursor.fetchone()[0]
    
    print(f"📊 Найдено вопросов: {total}")
    
    # Получить все вопросы
    cursor.execute('''
        SELECT 
            id,
            text,
            options,
            correct_answer_index,
            correct_answer_text,
            explanation,
            category,
            domain,
            difficulty_level,
            image_url,
            tags,
            big_domain_id,
            question_type,
            clinical_context,
            learning_objectives,
            profession,
            created_at,
            updated_at
        FROM questions
        ORDER BY id
    ''')
    
    questions = cursor.fetchall()
    
    print(f"✅ Загружено {len(questions)} вопросов")
    
    # Конвертировать в JSON-совместимый формат
    export_data = {
        "metadata": {
            "version": "1.0",
            "total_questions": len(questions),
            "exported_from": "local_sqlite_db",
            "export_date": datetime.now().isoformat(),
            "database_file": local_db
        },
        "questions": []
    }
    
    for row in questions:
        question = {
            "id": row['id'],
            "text": row['text'],
            "options": json.loads(row['options']) if row['options'] and isinstance(row['options'], str) else row['options'],
            "correct_answer_index": row['correct_answer_index'],
            "correct_answer_text": row['correct_answer_text'],
            "explanation": row['explanation'],
            "category": row['category'],
            "domain": row['domain'],
            "difficulty_level": row['difficulty_level'],
            "image_url": row['image_url'],
            "tags": json.loads(row['tags']) if row['tags'] and isinstance(row['tags'], str) else row['tags'],
            "big_domain_id": row['big_domain_id'],
            "question_type": row['question_type'],
            "clinical_context": row['clinical_context'],
            "learning_objectives": json.loads(row['learning_objectives']) if row['learning_objectives'] and isinstance(row['learning_objectives'], str) else row['learning_objectives'],
            "profession": row['profession'],
            "created_at": row['created_at'] if row['created_at'] else None,
            "updated_at": row['updated_at'] if row['updated_at'] else None
        }
        export_data["questions"].append(question)
    
    # Сохранить в JSON
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f'scripts/questions_export_{timestamp}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Экспорт завершен: {output_file}")
    print(f"   Размер файла: {os.path.getsize(output_file) / 1024:.2f} KB")
    
    conn.close()
    
    return output_file

def show_statistics():
    """Показать статистику по вопросам"""
    
    local_db = 'instance/dental_academy_clean.db'
    
    if not os.path.exists(local_db):
        print(f"❌ Локальная БД не найдена")
        return
    
    conn = sqlite3.connect(local_db)
    cursor = conn.cursor()
    
    # Общее количество
    cursor.execute('SELECT COUNT(*) FROM questions')
    total = cursor.fetchone()[0]
    
    # По категориям
    cursor.execute('''
        SELECT category, COUNT(*) 
        FROM questions 
        GROUP BY category 
        ORDER BY COUNT(*) DESC
    ''')
    categories = cursor.fetchall()
    
    # По профессиям
    cursor.execute('''
        SELECT profession, COUNT(*) 
        FROM questions 
        WHERE profession IS NOT NULL
        GROUP BY profession 
        ORDER BY COUNT(*) DESC
    ''')
    professions = cursor.fetchall()
    
    # По доменам
    cursor.execute('''
        SELECT domain, COUNT(*) 
        FROM questions 
        WHERE domain IS NOT NULL
        GROUP BY domain 
        ORDER BY COUNT(*) DESC
    ''')
    domains = cursor.fetchall()
    
    print("\n📊 СТАТИСТИКА ВОПРОСОВ:")
    print(f"   Всего вопросов: {total}")
    
    print("\n📁 По категориям:")
    for cat, count in categories[:10]:
        print(f"   - {cat}: {count}")
    
    print("\n👨‍⚕️ По профессиям:")
    for prof, count in professions:
        print(f"   - {prof}: {count}")
    
    print("\n🏷️ По доменам:")
    for dom, count in domains[:10]:
        print(f"   - {dom}: {count}")
    
    conn.close()

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 ЭКСПОРТ ВОПРОСОВ ИЗ ЛОКАЛЬНОЙ БД")
    print("=" * 60)
    print()
    
    # Показать статистику
    show_statistics()
    print()
    
    # Экспортировать
    output_file = export_questions_from_sqlite()
    
    if output_file:
        print()
        print("=" * 60)
        print("✅ ЭКСПОРТ ЗАВЕРШЕН УСПЕШНО")
        print("=" * 60)
        print()
        print(f"📄 Файл: {output_file}")
        print()
        print("📋 Следующие шаги:")
        print("   1. Проверьте файл с вопросами")
        print("   2. Загрузите файл на продакшн")
        print("   3. Используйте scripts/import_questions_to_production.py")
        print("      для импорта на Render")
        print()







