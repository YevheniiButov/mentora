#!/usr/bin/env python3
"""
Скрипт для импорта вопросов для huisarts (врачей общей практики)
Импортирует вопросы из arts_irt.json и arts_irt_part2.json
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import app
from models import db, Question

def import_huisarts_questions():
    """Импортировать вопросы для huisarts"""
    
    with app.app_context():
        try:
            print("🏥 ИМПОРТ ВОПРОСОВ ДЛЯ HUISARTS")
            print("=" * 50)
            
            # Проверяем, есть ли уже вопросы для huisarts
            existing_huisarts = Question.query.filter_by(profession='huisarts').count()
            if existing_huisarts > 0:
                print(f"⚠️  В базе уже есть {existing_huisarts} вопросов для huisarts")
                response = input("Продолжить импорт? (y/N): ")
                if response.lower() != 'y':
                    print("❌ Импорт отменен")
                    return False
            
            # Импортируем из первого файла
            print("📁 Импортируем из arts_irt.json...")
            arts_file = Path(__file__).parent / 'arts_irt.json'
            if not arts_file.exists():
                print(f"❌ Файл {arts_file} не найден")
                return False
                
            with open(arts_file, 'r', encoding='utf-8') as f:
                arts_data = json.load(f)
            
            questions_imported = 0
            for question_data in arts_data['questions']:
                # Создаем новый вопрос
                question = Question(
                    text=question_data['question_text'],
                    options=question_data['options'],
                    correct_answer_index=ord(question_data['correct_answer']) - ord('A'),  # A=0, B=1, C=2, D=3
                    correct_answer_text=question_data['options'][ord(question_data['correct_answer']) - ord('A')],
                    explanation=question_data.get('explanation', ''),
                    category=question_data.get('category', 'General Medicine'),
                    domain='huisarts',  # Устанавливаем домен как huisarts
                    difficulty_level=1 if question_data.get('difficulty_estimate') == 'easy' else 2,
                    profession='huisarts',  # Устанавливаем профессию
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                db.session.add(question)
                questions_imported += 1
                
                if questions_imported % 50 == 0:
                    print(f"   Импортировано {questions_imported} вопросов...")
            
            print(f"✅ Импортировано {questions_imported} вопросов из arts_irt.json")
            
            # Импортируем из второго файла
            print("📁 Импортируем из arts_irt_part2.json...")
            arts_part2_file = Path(__file__).parent / 'arts_irt_part2.json'
            if not arts_part2_file.exists():
                print(f"❌ Файл {arts_part2_file} не найден")
                return False
                
            with open(arts_part2_file, 'r', encoding='utf-8') as f:
                arts_part2_data = json.load(f)
            
            part2_imported = 0
            for question_data in arts_part2_data['questions']:
                # Создаем новый вопрос
                question = Question(
                    text=question_data['question_text'],
                    options=question_data['options'],
                    correct_answer_index=ord(question_data['correct_answer']) - ord('A'),  # A=0, B=1, C=2, D=3
                    correct_answer_text=question_data['options'][ord(question_data['correct_answer']) - ord('A')],
                    explanation=question_data.get('explanation', ''),
                    category=question_data.get('category', 'General Medicine'),
                    domain='huisarts',  # Устанавливаем домен как huisarts
                    difficulty_level=1 if question_data.get('difficulty_estimate') == 'easy' else 2,
                    profession='huisarts',  # Устанавливаем профессию
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                db.session.add(question)
                part2_imported += 1
                
                if part2_imported % 50 == 0:
                    print(f"   Импортировано {part2_imported} вопросов...")
            
            print(f"✅ Импортировано {part2_imported} вопросов из arts_irt_part2.json")
            
            # Сохраняем все изменения
            print("💾 Сохраняем изменения в базе данных...")
            db.session.commit()
            
            total_imported = questions_imported + part2_imported
            print()
            print("🎉 ИМПОРТ ЗАВЕРШЕН!")
            print("=" * 50)
            print(f"📊 Результаты:")
            print(f"   arts_irt.json: {questions_imported} вопросов")
            print(f"   arts_irt_part2.json: {part2_imported} вопросов")
            print(f"   Всего импортировано: {total_imported} вопросов")
            print(f"   Профессия: huisarts")
            
            return True
            
        except Exception as e:
            print(f"❌ ОШИБКА: {str(e)}")
            db.session.rollback()
            return False

def main():
    """Основная функция"""
    print("🏥 СКРИПТ ИМПОРТА ВОПРОСОВ ДЛЯ HUISARTS")
    print("=" * 50)
    print(f"⏰ Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    success = import_huisarts_questions()
    
    if success:
        print()
        print("✅ Скрипт успешно завершен!")
    else:
        print()
        print("❌ Скрипт завершен с ошибками!")
        sys.exit(1)

if __name__ == '__main__':
    main()




