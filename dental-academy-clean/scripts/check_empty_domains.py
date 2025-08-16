#!/usr/bin/env python3
"""
Скрипт для проверки пустых доменов в базе данных
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import BIGDomain, Question
from extensions import db

def check_empty_domains():
    """Проверить домены без вопросов"""
    
    print('🔍 ПРОВЕРКА ПУСТЫХ ДОМЕНОВ')
    print('=' * 50)
    
    with app.app_context():
        # Получаем все активные домены
        domains = BIGDomain.query.filter_by(is_active=True).order_by(BIGDomain.code).all()
        
        print(f'📊 Всего активных доменов: {len(domains)}')
        
        empty_domains = []
        domains_with_questions = []
        total_questions = 0
        
        for domain in domains:
            questions_count = Question.query.filter_by(big_domain_id=domain.id).count()
            total_questions += questions_count
            
            if questions_count == 0:
                empty_domains.append({
                    'code': domain.code,
                    'name': domain.name,
                    'weight': domain.weight_percentage,
                    'id': domain.id
                })
            else:
                domains_with_questions.append({
                    'code': domain.code,
                    'name': domain.name,
                    'questions': questions_count,
                    'weight': domain.weight_percentage,
                    'id': domain.id
                })
        
        print(f'\n📋 ПУСТЫЕ ДОМЕНЫ ({len(empty_domains)}):')
        if empty_domains:
            print(f'   {"Код":<20} {"Название":<30} {"Вес":<8} {"ID":<6}')
            print('   ' + '-' * 70)
            
            for domain in empty_domains:
                print(f'   {domain["code"]:<20} {domain["name"]:<30} {domain["weight"]:<8} {domain["id"]:<6}')
        else:
            print('   ✅ Нет пустых доменов!')
        
        print(f'\n📋 ДОМЕНЫ С ВОПРОСАМИ ({len(domains_with_questions)}):')
        print(f'   {"Код":<20} {"Название":<30} {"Вопросов":<10} {"Вес":<8} {"ID":<6}')
        print('   ' + '-' * 80)
        
        # Сортируем по количеству вопросов (по убыванию)
        domains_with_questions.sort(key=lambda x: x['questions'], reverse=True)
        
        for domain in domains_with_questions:
            print(f'   {domain["code"]:<20} {domain["name"]:<30} {domain["questions"]:<10} {domain["weight"]:<8} {domain["id"]:<6}')
        
        print(f'\n📊 СТАТИСТИКА:')
        print(f'   Всего доменов: {len(domains)}')
        print(f'   Доменов с вопросами: {len(domains_with_questions)}')
        print(f'   Пустых доменов: {len(empty_domains)}')
        print(f'   Всего вопросов: {total_questions}')
        
        if empty_domains:
            print(f'\n⚠️  ВНИМАНИЕ: Найдено {len(empty_domains)} пустых доменов!')
            print('   Эти домены могут вызывать проблемы в диагностической системе.')
        else:
            print(f'\n✅ Отлично! Все домены содержат вопросы.')

if __name__ == '__main__':
    check_empty_domains()


