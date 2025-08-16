#!/usr/bin/env python3
"""
Скрипт для импорта 20 новых вопросов в базу данных
"""

import json
import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import Question, BIGDomain, IRTParameters
from extensions import db

def import_new_questions():
    """Импортировать новые вопросы в базу данных"""
    
    print('📥 ИМПОРТ НОВЫХ ВОПРОСОВ В БАЗУ ДАННЫХ')
    print('=' * 50)
    
    # Путь к файлу с вопросами
    questions_file = '/Users/evgenijbutov/Desktop/demo/flask-app 2/dental-academy-clean/scripts/questions_export_20250812_020211.json'
    
    try:
        # Читаем файл с вопросами
        with open(questions_file, 'r', encoding='utf-8') as f:
            all_questions = json.load(f)
        
        print(f'📊 Загружено {len(all_questions)} вопросов из файла')
        
        # Фильтруем только новые вопросы (ID 381-400)
        new_questions = [q for q in all_questions if 381 <= q['id'] <= 400]
        
        print(f'📋 Найдено {len(new_questions)} новых вопросов для импорта')
        
        with app.app_context():
            imported_count = 0
            skipped_count = 0
            
            for question_data in new_questions:
                question_id = question_data['id']
                
                # Проверяем, существует ли уже вопрос с таким ID
                existing_question = Question.query.get(question_id)
                if existing_question:
                    print(f'⚠️  Вопрос {question_id} уже существует, пропускаем')
                    skipped_count += 1
                    continue
                
                # Находим домен
                domain_code = question_data['domain']
                domain = BIGDomain.query.filter_by(code=domain_code).first()
                
                if not domain:
                    print(f'❌ Домен {domain_code} не найден для вопроса {question_id}')
                    skipped_count += 1
                    continue
                
                # Создаем новый вопрос
                new_question = Question(
                    id=question_id,
                    text=question_data['text'],
                    options=question_data['options'],
                    correct_answer_index=question_data['correct_answer_index'],
                    correct_answer_text=question_data['correct_answer_text'],
                    explanation=question_data['explanation'],
                    category=question_data['category'],
                    domain=question_data['domain'],
                    difficulty_level=question_data['difficulty_level'],
                    image_url=question_data.get('image_url'),
                    tags=question_data.get('tags'),
                    big_domain_id=domain.id,
                    question_type=question_data.get('question_type', 'multiple_choice'),
                    clinical_context=question_data.get('clinical_context'),
                    learning_objectives=question_data.get('learning_objectives'),
                    created_at=datetime.fromisoformat(question_data['created_at'].replace('Z', '+00:00')),
                    updated_at=datetime.fromisoformat(question_data['updated_at'].replace('Z', '+00:00'))
                )
                
                # Добавляем в базу данных
                db.session.add(new_question)
                
                # Создаем IRT параметры
                irt_data = question_data.get('irt_parameters')
                if irt_data:
                    irt_params = IRTParameters(
                        question_id=question_id,
                        difficulty=irt_data['difficulty'],
                        discrimination=irt_data['discrimination'],
                        guessing=irt_data['guessing'],
                        calibration_date=datetime.fromisoformat(irt_data['calibration_date'].replace('Z', '+00:00')) if irt_data.get('calibration_date') else None
                    )
                    db.session.add(irt_params)
                
                print(f'✅ Импортирован вопрос {question_id}: {domain_code}')
                imported_count += 1
            
            # Сохраняем изменения
            try:
                db.session.commit()
                print(f'\n📊 РЕЗУЛЬТАТ ИМПОРТА:')
                print(f'   Импортировано: {imported_count} вопросов')
                print(f'   Пропущено: {skipped_count} вопросов')
                print(f'   Всего: {imported_count + skipped_count} вопросов')
                
                return True
                
            except Exception as e:
                print(f'❌ Ошибка при сохранении: {e}')
                db.session.rollback()
                return False
                
    except Exception as e:
        print(f'❌ Ошибка при чтении файла: {e}')
        return False

def verify_import():
    """Проверить результаты импорта"""
    
    print('\n🔍 ПРОВЕРКА РЕЗУЛЬТАТОВ ИМПОРТА')
    print('=' * 40)
    
    with app.app_context():
        # Проверяем новые домены
        new_domains = ['COMMUNICATION', 'PRACTICAL_SKILLS', 'STATISTICS', 'TREATMENT_PLANNING']
        
        for domain_code in new_domains:
            domain = BIGDomain.query.filter_by(code=domain_code).first()
            if domain:
                questions_count = Question.query.filter_by(big_domain_id=domain.id).count()
                print(f'   {domain_code}: {questions_count} вопросов')
            else:
                print(f'   {domain_code}: домен не найден')
        
        # Общая статистика
        total_questions = Question.query.count()
        total_domains = BIGDomain.query.filter_by(is_active=True).count()
        
        print(f'\n📊 ОБЩАЯ СТАТИСТИКА:')
        print(f'   Всего вопросов в БД: {total_questions}')
        print(f'   Всего доменов: {total_domains}')
        
        # Проверяем пустые домены
        empty_domains = []
        domains_with_questions = []
        
        all_domains = BIGDomain.query.filter_by(is_active=True).all()
        for domain in all_domains:
            questions_count = Question.query.filter_by(big_domain_id=domain.id).count()
            if questions_count == 0:
                empty_domains.append(domain.code)
            else:
                domains_with_questions.append(domain.code)
        
        print(f'\n📋 ПУСТЫЕ ДОМЕНЫ ({len(empty_domains)}):')
        for domain_code in empty_domains:
            print(f'   • {domain_code}')
        
        if not empty_domains:
            print('   ✅ Нет пустых доменов!')

def update_domain_weights():
    """Обновить веса доменов"""
    
    print('\n⚖️  ОБНОВЛЕНИЕ ВЕСОВ ДОМЕНОВ')
    print('=' * 40)
    
    with app.app_context():
        weight_updates = {
            'COMMUNICATION': 6.0,
            'PRACTICAL_SKILLS': 15.0,
            'STATISTICS': 5.0,
            'TREATMENT_PLANNING': 10.0
        }
        
        updated_count = 0
        
        for domain_code, weight in weight_updates.items():
            domain = BIGDomain.query.filter_by(code=domain_code).first()
            if domain:
                old_weight = domain.weight_percentage
                domain.weight_percentage = weight
                print(f'   {domain_code}: {old_weight}% -> {weight}%')
                updated_count += 1
        
        try:
            db.session.commit()
            print(f'\n✅ Обновлено весов: {updated_count}')
            return True
        except Exception as e:
            print(f'❌ Ошибка при обновлении весов: {e}')
            db.session.rollback()
            return False

if __name__ == '__main__':
    print('🚀 Запуск импорта новых вопросов...')
    
    # Импортируем вопросы
    import_success = import_new_questions()
    
    if import_success:
        # Обновляем веса доменов
        weight_success = update_domain_weights()
        
        # Проверяем результаты
        verify_import()
        
        if weight_success:
            print('\n✅ Импорт и обновление завершены успешно!')
        else:
            print('\n⚠️  Импорт завершен, но обновление весов не удалось!')
    else:
        print('\n❌ Импорт завершился с ошибками!')


