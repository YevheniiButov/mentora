#!/usr/bin/env python3
"""
Скрипт для проверки порядка вопросов в базе данных
по сравнению с файлом 160_2.json
"""

import json
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import Question, BIGDomain
from extensions import db

def load_160_2_order():
    """Загрузить порядок вопросов из файла 160_2.json"""
    
    file_path = os.path.join(os.path.dirname(__file__), '160_2.json')
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Создаем словарь: id -> позиция в файле
        order_dict = {}
        for i, question in enumerate(data):
            question_id = question.get('id')
            if question_id:
                order_dict[question_id] = i + 1  # +1 для удобства (начиная с 1)
        
        return order_dict, data
        
    except Exception as e:
        print(f"❌ Ошибка при загрузке файла 160_2.json: {e}")
        return {}, []

def check_question_order():
    """Проверить порядок вопросов в базе данных"""
    
    print('🔍 ПРОВЕРКА ПОРЯДКА ВОПРОСОВ')
    print('=' * 50)
    
    # Загружаем порядок из файла
    file_order, file_data = load_160_2_order()
    
    if not file_order:
        print('❌ Не удалось загрузить данные из файла')
        return
    
    print(f'📊 Загружено {len(file_order)} вопросов из файла')
    
    with app.app_context():
        # Получаем все вопросы из БД, отсортированные по ID
        db_questions = Question.query.order_by(Question.id).all()
        
        print(f'📊 Найдено {len(db_questions)} вопросов в базе данных')
        
        # Проверяем соответствие ID
        file_ids = set(file_order.keys())
        db_ids = {q.id for q in db_questions}
        
        print(f'\n📋 АНАЛИЗ ID ВОПРОСОВ:')
        print(f'   В файле: {len(file_ids)} вопросов')
        print(f'   В БД: {len(db_ids)} вопросов')
        print(f'   Общие: {len(file_ids & db_ids)} вопросов')
        print(f'   Только в файле: {len(file_ids - db_ids)} вопросов')
        print(f'   Только в БД: {len(db_ids - file_ids)} вопросов')
        
        # Проверяем порядок для общих вопросов
        common_ids = file_ids & db_ids
        
        if common_ids:
            print(f'\n📊 ПРОВЕРКА ПОРЯДКА ДЛЯ {len(common_ids)} ОБЩИХ ВОПРОСОВ:')
            
            # Создаем список ID в порядке БД
            db_order = []
            for q in db_questions:
                if q.id in common_ids:
                    db_order.append(q.id)
            
            # Создаем список ID в порядке файла
            file_order_list = []
            for question in file_data:
                question_id = question.get('id')
                if question_id in common_ids:
                    file_order_list.append(question_id)
            
            # Сравниваем порядки
            order_matches = 0
            order_mismatches = []
            
            for i, (file_id, db_id) in enumerate(zip(file_order_list, db_order)):
                if file_id == db_id:
                    order_matches += 1
                else:
                    order_mismatches.append({
                        'position': i + 1,
                        'file_id': file_id,
                        'db_id': db_id,
                        'file_domain': next((q.get('domain') for q in file_data if q.get('id') == file_id), 'N/A'),
                        'db_domain': next((q.domain for q in db_questions if q.id == db_id), 'N/A')
                    })
            
            print(f'   ✅ Совпадений по порядку: {order_matches}')
            print(f'   ❌ Несовпадений по порядку: {len(order_mismatches)}')
            
            if order_mismatches:
                print(f'\n📋 ПЕРВЫЕ 10 НЕСОВПАДЕНИЙ:')
                print(f'   {"Поз":<4} {"Файл ID":<8} {"БД ID":<8} {"Файл домен":<15} {"БД домен":<15}')
                print('   ' + '-' * 60)
                
                for mismatch in order_mismatches[:10]:
                    print(f'   {mismatch["position"]:<4} {mismatch["file_id"]:<8} {mismatch["db_id"]:<8} '
                          f'{mismatch["file_domain"]:<15} {mismatch["db_domain"]:<15}')
                
                if len(order_mismatches) > 10:
                    print(f'   ... и еще {len(order_mismatches) - 10} несовпадений')
            
            # Проверяем порядок по доменам
            print(f'\n📊 АНАЛИЗ ПО ДОМЕНАМ:')
            
            # Группируем вопросы по доменам
            domain_analysis = {}
            
            for question in file_data:
                domain = question.get('domain')
                question_id = question.get('id')
                
                if domain and question_id in common_ids:
                    if domain not in domain_analysis:
                        domain_analysis[domain] = {'file_order': [], 'db_order': []}
                    
                    domain_analysis[domain]['file_order'].append(question_id)
            
            # Добавляем порядок из БД
            for question in db_questions:
                if question.id in common_ids:
                    domain = question.domain
                    if domain in domain_analysis:
                        domain_analysis[domain]['db_order'].append(question.id)
            
            # Анализируем каждый домен
            for domain, orders in domain_analysis.items():
                file_order_domain = orders['file_order']
                db_order_domain = orders['db_order']
                
                if file_order_domain == db_order_domain:
                    status = "✅"
                else:
                    status = "❌"
                
                print(f'   {status} {domain}: {len(file_order_domain)} вопросов')
        
        # Показываем примеры вопросов
        print(f'\n📋 ПРИМЕРЫ ВОПРОСОВ (первые 5):')
        print(f'   {"ID":<6} {"Файл домен":<15} {"БД домен":<15} {"Порядок":<10}')
        print('   ' + '-' * 55)
        
        for i, question in enumerate(db_questions[:5]):
            file_domain = file_order.get(question.id, 'N/A')
            if file_domain != 'N/A':
                file_domain = next((q.get('domain') for q in file_data if q.get('id') == question.id), 'N/A')
            
            order_status = "✅" if file_domain == question.domain else "❌"
            
            print(f'   {question.id:<6} {file_domain:<15} {question.domain:<15} {order_status:<10}')

if __name__ == '__main__':
    check_question_order()


