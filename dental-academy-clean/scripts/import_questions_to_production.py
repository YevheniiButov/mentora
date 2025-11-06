#!/usr/bin/env python3
"""
Импорт вопросов на продакшн (Render)
"""
import os
import sys
import json
from pathlib import Path

# Добавить текущую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import psycopg2
    from psycopg2.extras import execute_values
except ImportError:
    print("❌ Необходимо установить psycopg2:")
    print("   pip install psycopg2-binary")
    sys.exit(1)

def import_questions_to_production(json_file=None):
    """Импортировать вопросы из JSON в продакшн БД"""
    
    # Найти файл экспорта
    if not json_file:
        # Ищем последний файл экспорта
        export_dir = Path('scripts')
        export_files = sorted(export_dir.glob('questions_export_*.json'), reverse=True)
        if not export_files:
            print("❌ Не найден файл экспорта")
            print("   Сначала запустите: python3 scripts/export_questions_to_production.py")
            return
        
        json_file = export_files[0]
    
    print(f"📄 Загружаем файл: {json_file}")
    
    # Прочитать JSON
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data.get('questions', [])
    print(f"📊 Загружено {len(questions)} вопросов из JSON")
    
    # Получить DATABASE_URL
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        print("❌ DATABASE_URL не установлен!")
        print("   Установите его командой: export DATABASE_URL='postgresql://...'")
        return
    
    print("🔗 Подключаемся к продакшн БД...")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("✅ Подключение успешно")
        
        # Проверить текущее количество вопросов
        cur.execute('SELECT COUNT(*) FROM questions')
        current_count = cur.fetchone()[0]
        print(f"📊 Текущее количество вопросов на продакшене: {current_count}")
        
        # Импортировать вопросы
        imported = 0
        skipped = 0
        errors = 0
        
        print("\n📥 Импортируем вопросы...")
        
        for i, q in enumerate(questions, 1):
            try:
                # Проверить, существует ли вопрос
                cur.execute(
                    'SELECT id FROM questions WHERE text = %s',
                    (q['text'],)
                )
                existing = cur.fetchone()
                
                if existing:
                    skipped += 1
                    continue
                
                # Вставить новый вопрос
                cur.execute('''
                    INSERT INTO questions (
                        id, text, options, correct_answer_index, correct_answer_text,
                        explanation, category, domain, difficulty_level, image_url,
                        tags, big_domain_id, question_type, clinical_context,
                        learning_objectives, profession, created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                ''', (
                    q.get('id'),
                    q.get('text'),
                    json.dumps(q.get('options')) if q.get('options') else None,
                    q.get('correct_answer_index'),
                    q.get('correct_answer_text'),
                    q.get('explanation'),
                    q.get('category'),
                    q.get('domain'),
                    q.get('difficulty_level'),
                    q.get('image_url'),
                    json.dumps(q.get('tags')) if q.get('tags') else None,
                    q.get('big_domain_id'),
                    q.get('question_type'),
                    q.get('clinical_context'),
                    json.dumps(q.get('learning_objectives')) if q.get('learning_objectives') else None,
                    q.get('profession'),
                    q.get('created_at'),
                    q.get('updated_at')
                ))
                
                imported += 1
                
                if i % 100 == 0:
                    print(f"   Обработано: {i}/{len(questions)}")
                    conn.commit()  # Промежуточный коммит
                    
            except Exception as e:
                errors += 1
                print(f"   ❌ Ошибка при импорте вопроса {q.get('id')}: {e}")
                if errors <= 3:  # Показать первые 3 ошибки
                    import traceback
                    traceback.print_exc()
                continue
        
        # Финальный коммит
        conn.commit()
        
        # Проверить результат
        cur.execute('SELECT COUNT(*) FROM questions')
        final_count = cur.fetchone()[0]
        
        print("\n" + "=" * 60)
        print("✅ ИМПОРТ ЗАВЕРШЕН")
        print("=" * 60)
        print(f"📥 Импортировано новых: {imported}")
        print(f"⏭️  Пропущено (уже есть): {skipped}")
        print(f"❌ Ошибок: {errors}")
        print(f"📊 Всего вопросов на продакшене: {current_count} → {final_count}")
        print("=" * 60)
        
        cur.close()
        conn.close()
        
    except psycopg2.Error as e:
        print(f"❌ Ошибка при работе с БД: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 ИМПОРТ ВОПРОСОВ НА ПРОДАКШН")
    print("=" * 60)
    print()
    
    # Проверить, что на продакшене
    database_url = os.environ.get('DATABASE_URL', '')
    if 'localhost' in database_url or '127.0.0.1' in database_url:
        print("⚠️  ВНИМАНИЕ: Похоже, что DATABASE_URL указывает на локальную БД!")
        response = input("   Продолжить? (yes/no): ")
        if response.lower() != 'yes':
            print("Отменено")
            sys.exit(0)
    
    import_questions_to_production()
    print()
