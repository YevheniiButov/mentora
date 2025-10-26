#!/usr/bin/env python3
"""
Безопасный импорт вопросов на продакшн с автоматическим определением столбцов
"""
import os
import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import psycopg2
except ImportError:
    print("❌ Необходимо установить psycopg2: pip install psycopg2-binary")
    sys.exit(1)

def get_available_columns(cursor):
    """Получить список доступных столбцов в таблице questions"""
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'questions'
        ORDER BY ordinal_position
    """)
    return {row[0]: row[1] for row in cursor.fetchall()}

def import_questions_safe():
    """Безопасный импорт с автоматическим определением столбцов"""
    
    # Найти файл экспорта
    export_dir = Path('scripts')
    export_files = sorted(export_dir.glob('questions_export_*.json'), reverse=True)
    if not export_files:
        print("❌ Не найден файл экспорта")
        return
    
    json_file = export_files[0]
    print(f"📄 Загружаем файл: {json_file}")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    questions = data.get('questions', [])
    print(f"📊 Загружено {len(questions)} вопросов")
    
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        print("❌ DATABASE_URL не установлен!")
        return
    
    print("🔗 Подключаемся к БД...")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        print("✅ Подключение успешно")
        
        # Получить доступные столбцы
        available_columns = get_available_columns(cur)
        print(f"\n📋 Доступные столбцы ({len(available_columns)}):")
        for col, dtype in available_columns.items():
            print(f"   - {col}: {dtype}")
        
        # Проверить текущее количество
        cur.execute('SELECT COUNT(*) FROM questions')
        current_count = cur.fetchone()[0]
        print(f"\n📊 Текущее количество вопросов: {current_count}")
        
        imported = 0
        skipped = 0
        errors = 0
        
        print("\n📥 Импортируем вопросы...\n")
        
        for i, q in enumerate(questions, 1):
            try:
                # Проверить существование
                cur.execute('SELECT id FROM questions WHERE text = %s', (q['text'],))
                if cur.fetchone():
                    skipped += 1
                    continue
                
                # Сформировать INSERT с только доступными столбцами
                columns = []
                values = []
                
                # Базовые обязательные столбцы
                for col in ['text', 'options', 'correct_answer_index', 'correct_answer_text', 
                           'explanation', 'category', 'domain', 'difficulty_level']:
                    if col in available_columns:
                        columns.append(col)
                        if col in ['options', 'tags', 'learning_objectives']:
                            values.append(json.dumps(q.get(col)) if q.get(col) else None)
                        else:
                            values.append(q.get(col))
                
                # Опциональные столбцы
                optional_cols = ['image_url', 'tags', 'big_domain_id', 'question_type', 
                               'clinical_context', 'learning_objectives', 'profession', 
                               'created_at', 'updated_at', 'id']
                
                for col in optional_cols:
                    if col in available_columns:
                        columns.append(col)
                        if col in ['tags', 'learning_objectives']:
                            values.append(json.dumps(q.get(col)) if q.get(col) else None)
                        elif col == 'options':
                            values.append(json.dumps(q.get(col)) if q.get(col) else None)
                        else:
                            values.append(q.get(col))
                
                # Выполнить INSERT
                placeholders = ', '.join(['%s'] * len(values))
                columns_str = ', '.join(columns)
                
                cur.execute(f'''
                    INSERT INTO questions ({columns_str})
                    VALUES ({placeholders})
                ''', values)
                
                imported += 1
                
                if i % 50 == 0:
                    print(f"   ✓ Обработано: {i}/{len(questions)} (импортировано: {imported}, пропущено: {skipped})")
                    conn.commit()
                
            except Exception as e:
                errors += 1
                if errors <= 3:  # Показать первые 3 ошибки
                    print(f"\n❌ Ошибка на вопросе {i} (ID: {q.get('id', '?')}): {e}")
                    import traceback
                    traceback.print_exc()
                    print()
        
        conn.commit()
        
        cur.execute('SELECT COUNT(*) FROM questions')
        final_count = cur.fetchone()[0]
        
        print("\n" + "=" * 60)
        print("✅ ИМПОРТ ЗАВЕРШЕН")
        print("=" * 60)
        print(f"📥 Импортировано новых: {imported}")
        print(f"⏭️  Пропущено (уже есть): {skipped}")
        print(f"❌ Ошибок: {errors}")
        print(f"📊 Всего вопросов: {current_count} → {final_count}")
        print("=" * 60)
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 БЕЗОПАСНЫЙ ИМПОРТ ВОПРОСОВ")
    print("=" * 60)
    print()
    
    import_questions_safe()
    print()
