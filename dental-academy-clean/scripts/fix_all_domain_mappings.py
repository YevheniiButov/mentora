#!/usr/bin/env python3
"""
Скрипт для полного исправления маппинга всех доменов
Возвращает каждому домену его правильные вопросы из 160_2.json
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import BIGDomain, Question
from extensions import db

def load_160_2_data():
    """Загрузить данные из файла 160_2.json"""
    
    file_path = os.path.join(os.path.dirname(__file__), '160_2.json')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Группируем вопросы по доменам
        questions_by_domain = {}
        
        for question in data:
            domain = question.get('domain')
            if domain:
                if domain not in questions_by_domain:
                    questions_by_domain[domain] = []
                questions_by_domain[domain].append(question)
        
        return questions_by_domain
        
    except Exception as e:
        print(f"❌ Ошибка при загрузке файла 160_2.json: {e}")
        return {}

def fix_all_domain_mappings():
    """Исправить маппинг всех доменов"""
    
    print('🔧 ПОЛНОЕ ИСПРАВЛЕНИЕ МАППИНГА ВСЕХ ДОМЕНОВ')
    print('=' * 60)
    
    # Загружаем данные из файла
    questions_by_domain = load_160_2_data()
    
    if not questions_by_domain:
        print('❌ Не удалось загрузить данные из файла')
        return False
    
    print(f'📊 Загружено {len(questions_by_domain)} доменов из файла')
    
    with app.app_context():
        total_fixed = 0
        
        for domain_code, questions in questions_by_domain.items():
            print(f'\n📝 Исправление домена: {domain_code} ({len(questions)} вопросов)')
            
            # Найдем домен в базе данных
            domain = BIGDomain.query.filter_by(code=domain_code).first()
            
            if not domain:
                print(f'   ❌ Домен {domain_code} не найден в БД')
                continue
            
            print(f'   📊 Найден домен {domain_code} (ID: {domain.id})')
            
            # Найдем вопросы, которые должны быть в этом домене
            question_ids = [q['id'] for q in questions]
            
            # Исправим маппинг для этих вопросов
            fixed_in_domain = 0
            
            for question_id in question_ids:
                question = Question.query.get(question_id)
                
                if question:
                    old_domain_id = question.big_domain_id
                    old_domain_code = question.domain
                    
                    # Исправляем маппинг
                    question.big_domain_id = domain.id
                    question.domain = domain_code
                    
                    if old_domain_id != domain.id:
                        print(f'   ✅ Вопрос {question_id}: {old_domain_code} -> {domain_code}')
                        fixed_in_domain += 1
                        total_fixed += 1
                else:
                    print(f'   ⚠️  Вопрос {question_id} не найден в БД')
            
            print(f'   📊 Исправлено в домене {domain_code}: {fixed_in_domain} вопросов')
        
        # Сохраняем изменения
        try:
            db.session.commit()
            print('\n📊 РЕЗУЛЬТАТ:')
            print(f'   Всего исправлено вопросов: {total_fixed}')
            return True
            
        except Exception as e:
            print(f'❌ Ошибка при сохранении: {e}')
            db.session.rollback()
            return False

def verify_fixes():
    """Проверить результаты исправлений"""
    
    print('\n🔍 ПРОВЕРКА РЕЗУЛЬТАТОВ')
    print('=' * 40)
    
    with app.app_context():
        # Загружаем оригинальные данные для сравнения
        questions_by_domain = load_160_2_data()
        
        print('📊 СРАВНЕНИЕ С ОРИГИНАЛЬНЫМ РАСПРЕДЕЛЕНИЕМ:')
        print(f'   {"Домен":<20} {"Оригинал":<10} {"В БД":<10} {"Статус":<10}')
        print('   ' + '-' * 50)
        
        total_original = 0
        total_in_db = 0
        
        for domain_code, questions in questions_by_domain.items():
            original_count = len(questions)
            total_original += original_count
            
            # Найдем домен в БД
            domain = BIGDomain.query.filter_by(code=domain_code).first()
            
            if domain:
                db_count = Question.query.filter_by(big_domain_id=domain.id).count()
                total_in_db += db_count
                
                if db_count == original_count:
                    status = "✅"
                elif db_count > original_count:
                    status = "⚠️+"
                else:
                    status = "❌-"
                
                print(f'   {status} {domain_code:<17} {original_count:<10} {db_count:<10} {status:<10}')
            else:
                print(f'   ❌ {domain_code:<17} {original_count:<10} {"N/A":<10} {"N/A":<10}')
        
        print('   ' + '-' * 50)
        print(f'   {"ИТОГО":<17} {total_original:<10} {total_in_db:<10}')
        
        # Показываем домены только в БД
        print(f'\n📋 ДОМЕНЫ ТОЛЬКО В БАЗЕ ДАННЫХ:')
        db_domains = BIGDomain.query.filter_by(is_active=True).all()
        
        for domain in db_domains:
            if domain.code not in questions_by_domain:
                questions_count = Question.query.filter_by(big_domain_id=domain.id).count()
                print(f'   • {domain.code}: {questions_count} вопросов')

if __name__ == '__main__':
    print('🚀 Запуск полного исправления маппинга доменов...')
    
    success = fix_all_domain_mappings()
    
    if success:
        verify_fixes()
        print('\n✅ Операция завершена успешно!')
    else:
        print('\n❌ Операция завершена с ошибками!')


