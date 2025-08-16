#!/usr/bin/env python3
"""
Скрипт для сравнения доменов в базе данных с доменами в файле 160_2.json
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import BIGDomain, Question
from extensions import db

def load_160_2_domains():
    """Загрузить домены из файла 160_2.json"""
    
    file_path = os.path.join(os.path.dirname(__file__), '160_2.json')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Собираем уникальные домены
        domains_in_file = set()
        domain_question_counts = {}
        
        for question in data:
            domain = question.get('domain')
            if domain:
                domains_in_file.add(domain)
                domain_question_counts[domain] = domain_question_counts.get(domain, 0) + 1
        
        return domains_in_file, domain_question_counts
        
    except Exception as e:
        print(f"❌ Ошибка при загрузке файла 160_2.json: {e}")
        return set(), {}

def get_database_domains():
    """Получить домены из базы данных"""
    
    with app.app_context():
        domains = BIGDomain.query.filter_by(is_active=True).all()
        
        domain_codes = set()
        domain_stats = {}
        
        for domain in domains:
            domain_codes.add(domain.code)
            questions_count = Question.query.filter_by(big_domain_id=domain.id).count()
            
            domain_stats[domain.code] = {
                'id': domain.id,
                'name': domain.name,
                'questions_count': questions_count,
                'weight': domain.weight_percentage
            }
        
        return domain_codes, domain_stats

def compare_domains():
    """Сравнить домены между файлом и базой данных"""
    
    print('🔍 СРАВНЕНИЕ ДОМЕНОВ: 160_2.JSON vs БАЗА ДАННЫХ')
    print('=' * 70)
    
    # Загружаем домены из файла
    file_domains, file_question_counts = load_160_2_domains()
    
    # Загружаем домены из базы данных
    db_domains, db_domain_stats = get_database_domains()
    
    print(f'\n📊 СТАТИСТИКА:')
    print(f'   Доменов в 160_2.json: {len(file_domains)}')
    print(f'   Доменов в базе данных: {len(db_domains)}')
    
    # Домены только в файле
    only_in_file = file_domains - db_domains
    print(f'   Доменов только в файле: {len(only_in_file)}')
    
    # Домены только в базе данных
    only_in_db = db_domains - file_domains
    print(f'   Доменов только в БД: {len(only_in_db)}')
    
    # Общие домены
    common_domains = file_domains & db_domains
    print(f'   Общих доменов: {len(common_domains)}')
    
    # Детальный анализ
    print(f'\n📋 ДОМЕНЫ ТОЛЬКО В ФАЙЛЕ 160_2.JSON:')
    if only_in_file:
        for domain in sorted(only_in_file):
            questions = file_question_counts.get(domain, 0)
            print(f'   • {domain}: {questions} вопросов')
    else:
        print('   Нет')
    
    print(f'\n📋 ДОМЕНЫ ТОЛЬКО В БАЗЕ ДАННЫХ:')
    if only_in_db:
        for domain in sorted(only_in_db):
            stats = db_domain_stats[domain]
            print(f'   • {domain}: {stats["questions_count"]} вопросов (вес: {stats["weight"]}%)')
    else:
        print('   Нет')
    
    print(f'\n📋 ОБЩИЕ ДОМЕНЫ:')
    if common_domains:
        print(f'   {"Код":<20} {"В файле":<10} {"В БД":<10} {"Разница":<10}')
        print('   ' + '-' * 50)
        
        for domain in sorted(common_domains):
            file_count = file_question_counts.get(domain, 0)
            db_count = db_domain_stats[domain]['questions_count']
            difference = db_count - file_count
            
            status = "✅" if difference == 0 else "⚠️" if difference > 0 else "❌"
            print(f'   {status} {domain:<17} {file_count:<10} {db_count:<10} {difference:+<10}')
    else:
        print('   Нет')
    
    # Анализ соответствия
    print(f'\n🎯 АНАЛИЗ СООТВЕТСТВИЯ:')
    
    if len(only_in_file) == 0 and len(only_in_db) == 0:
        print('   ✅ Идеальное соответствие - все домены совпадают')
    elif len(only_in_file) == 0:
        print('   ✅ Все домены из файла есть в БД')
        print(f'   ⚠️  В БД есть {len(only_in_db)} дополнительных доменов')
    elif len(only_in_db) == 0:
        print('   ❌ В БД отсутствуют домены из файла')
        print(f'   ⚠️  Отсутствует {len(only_in_file)} доменов')
    else:
        print('   ⚠️  Частичное соответствие')
        print(f'   ❌ Отсутствует в БД: {len(only_in_file)} доменов')
        print(f'   ⚠️  Дополнительно в БД: {len(only_in_db)} доменов')

if __name__ == '__main__':
    compare_domains()


