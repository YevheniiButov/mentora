#!/usr/bin/env python3
"""
Скрипт для назначения профессий существующим вопросам
Назначает профессии вопросам:
- Вопросы 1-400: profession='tandarts' (стоматологи)
- Вопросы 401+: profession='huisarts' (врачи общей практики)
"""
import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# Добавляем путь к проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import app
from models import db, Question

def get_question_statistics():
    """Получить статистику по вопросам"""
    tandarts_count = Question.query.filter(
        Question.id >= 1, 
        Question.id <= 400
    ).count()
    
    huisarts_count = Question.query.filter(
        Question.id >= 401
    ).count()
    
    total_questions = Question.query.count()
    
    # Статистика по профессиям
    tandarts_with_profession = Question.query.filter(
        Question.id >= 1, 
        Question.id <= 400,
        Question.profession == 'tandarts'
    ).count()
    
    huisarts_with_profession = Question.query.filter(
        Question.id >= 401,
        Question.profession == 'huisarts'
    ).count()
    
    tandarts_without_profession = tandarts_count - tandarts_with_profession
    huisarts_without_profession = huisarts_count - huisarts_with_profession
    
    return {
        'total_questions': total_questions,
        'tandarts_range': (1, 400),
        'huisarts_range': (401, 'max'),
        'tandarts_count': tandarts_count,
        'huisarts_count': huisarts_count,
        'tandarts_with_profession': tandarts_with_profession,
        'huisarts_with_profession': huisarts_with_profession,
        'tandarts_without_profession': tandarts_without_profession,
        'huisarts_without_profession': huisarts_without_profession
    }

def preview_changes():
    """Предварительный просмотр изменений"""
    print("🔍 ПРЕДВАРИТЕЛЬНЫЙ ПРОСМОТР ИЗМЕНЕНИЙ")
    print("=" * 50)
    
    stats = get_question_statistics()
    
    print(f"📊 Общая статистика:")
    print(f"   Всего вопросов в базе: {stats['total_questions']}")
    print()
    
    print(f"🦷 Вопросы для стоматологов (ID {stats['tandarts_range'][0]}-{stats['tandarts_range'][1]}):")
    print(f"   Всего вопросов в диапазоне: {stats['tandarts_count']}")
    print(f"   Уже имеют profession='tandarts': {stats['tandarts_with_profession']}")
    print(f"   Будет обновлено: {stats['tandarts_without_profession']}")
    print()
    
    print(f"🩺 Вопросы для врачей общей практики (ID {stats['huisarts_range'][0]}+):")
    print(f"   Всего вопросов в диапазоне: {stats['huisarts_count']}")
    print(f"   Уже имеют profession='huisarts': {stats['huisarts_with_profession']}")
    print(f"   Будет обновлено: {stats['huisarts_without_profession']}")
    print()
    
    total_to_update = stats['tandarts_without_profession'] + stats['huisarts_without_profession']
    print(f"📈 ИТОГО БУДЕТ ОБНОВЛЕНО: {total_to_update} вопросов")
    
    if total_to_update == 0:
        print("✅ Все вопросы уже имеют назначенные профессии!")
        return False
    
    return True

def assign_professions():
    """Назначить профессии вопросам"""
    print("🚀 НАЗНАЧЕНИЕ ПРОФЕССИЙ ВОПРОСАМ")
    print("=" * 50)
    
    start_time = datetime.now()
    
    try:
        # Обновляем вопросы для стоматологов (1-400)
        print("🦷 Обновляем вопросы для стоматологов (ID 1-400)...")
        tandarts_updated = db.session.query(Question).filter(
            Question.id >= 1,
            Question.id <= 400,
            Question.profession.is_(None)  # Только те, у которых profession еще не назначена
        ).update(
            {Question.profession: 'tandarts'},
            synchronize_session=False
        )
        print(f"   ✅ Обновлено {tandarts_updated} вопросов")
        
        # Обновляем вопросы для врачей общей практики (401+)
        print("🩺 Обновляем вопросы для врачей общей практики (ID 401+)...")
        huisarts_updated = db.session.query(Question).filter(
            Question.id >= 401,
            Question.profession.is_(None)  # Только те, у которых profession еще не назначена
        ).update(
            {Question.profession: 'huisarts'},
            synchronize_session=False
        )
        print(f"   ✅ Обновлено {huisarts_updated} вопросов")
        
        # Сохраняем изменения
        print("💾 Сохраняем изменения в базе данных...")
        db.session.commit()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print()
        print("🎉 УСПЕШНО ЗАВЕРШЕНО!")
        print("=" * 50)
        print(f"📊 Результаты:")
        print(f"   Стоматологи (tandarts): {tandarts_updated} вопросов")
        print(f"   Врачи общей практики (huisarts): {huisarts_updated} вопросов")
        print(f"   Всего обновлено: {tandarts_updated + huisarts_updated} вопросов")
        print(f"   Время выполнения: {duration:.2f} секунд")
        
        return True
        
    except Exception as e:
        print(f"❌ ОШИБКА: {str(e)}")
        db.session.rollback()
        return False

def main():
    """Основная функция"""
    parser = argparse.ArgumentParser(
        description='Назначить профессии существующим вопросам',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:
  python scripts/assign_question_professions.py --dry-run    # Предварительный просмотр
  python scripts/assign_question_professions.py --commit     # Выполнить обновление
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--dry-run', action='store_true', 
                      help='Предварительный просмотр изменений (по умолчанию)')
    group.add_argument('--commit', action='store_true', 
                      help='Выполнить обновление базы данных')
    
    args = parser.parse_args()
    
    print("🏥 СКРИПТ НАЗНАЧЕНИЯ ПРОФЕССИЙ ВОПРОСАМ")
    print("=" * 50)
    print(f"⏰ Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    with app.app_context():
        if args.dry_run:
            print("🔍 РЕЖИМ ПРЕДВАРИТЕЛЬНОГО ПРОСМОТРА")
            print("(Изменения НЕ будут сохранены)")
            print()
            
            has_changes = preview_changes()
            
            if has_changes:
                print()
                print("💡 Для выполнения изменений запустите:")
                print("   python scripts/assign_question_professions.py --commit")
            else:
                print("✅ Никаких изменений не требуется.")
                
        elif args.commit:
            print("⚠️  РЕЖИМ ВЫПОЛНЕНИЯ")
            print("(Изменения БУДУТ сохранены в базе данных)")
            print()
            
            # Сначала показываем предварительный просмотр
            has_changes = preview_changes()
            
            if not has_changes:
                print("✅ Никаких изменений не требуется.")
                return
            
            print()
            print("🚀 Выполняем обновление...")
            print()
            
            success = assign_professions()
            
            if success:
                print()
                print("✅ Скрипт успешно завершен!")
            else:
                print()
                print("❌ Скрипт завершен с ошибками!")
                sys.exit(1)

if __name__ == '__main__':
    main()
