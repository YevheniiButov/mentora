#!/usr/bin/env python3
"""
Скрипт для проверки вероятности дублирования доменов
Только анализ, без внесения изменений
"""

import sys
import os
from difflib import SequenceMatcher
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import BIGDomain, Question
from extensions import db

def similarity(a, b):
    """Вычислить схожесть между двумя строками (0-1)"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def check_domain_similarity():
    """Проверить схожесть доменов для выявления возможных дубликатов"""
    
    print('🔍 ПРОВЕРКА СХОЖЕСТИ ДОМЕНОВ')
    print('=' * 50)
    
    with app.app_context():
        # Получаем все домены
        domains = BIGDomain.query.filter_by(is_active=True).order_by(BIGDomain.code).all()
        
        print(f'📊 Всего доменов для проверки: {len(domains)}')
        
        # Создаем список доменов с информацией
        domain_info = []
        for domain in domains:
            questions_count = Question.query.filter_by(big_domain_id=domain.id).count()
            domain_info.append({
                'id': domain.id,
                'code': domain.code,
                'name': domain.name,
                'questions': questions_count,
                'weight': domain.weight_percentage
            })
        
        # Проверяем схожесть между всеми парами доменов
        potential_duplicates = []
        
        for i, domain1 in enumerate(domain_info):
            for j, domain2 in enumerate(domain_info[i+1:], i+1):
                # Проверяем схожесть кодов
                code_similarity = similarity(domain1['code'], domain2['code'])
                
                # Проверяем схожесть названий
                name_similarity = similarity(domain1['name'], domain2['name'])
                
                # Если схожесть высокая, добавляем в список
                if code_similarity > 0.7 or name_similarity > 0.7:
                    potential_duplicates.append({
                        'domain1': domain1,
                        'domain2': domain2,
                        'code_similarity': code_similarity,
                        'name_similarity': name_similarity,
                        'total_similarity': (code_similarity + name_similarity) / 2
                    })
        
        # Сортируем по общей схожести (по убыванию)
        potential_duplicates.sort(key=lambda x: x['total_similarity'], reverse=True)
        
        if potential_duplicates:
            print(f'\n⚠️  НАЙДЕНО {len(potential_duplicates)} ПОТЕНЦИАЛЬНЫХ ДУБЛИКАТОВ:')
            print('=' * 80)
            
            for i, duplicate in enumerate(potential_duplicates, 1):
                d1 = duplicate['domain1']
                d2 = duplicate['domain2']
                
                print(f'\n{i}. СХОЖЕСТЬ: {duplicate["total_similarity"]:.1%}')
                print(f'   Код: {duplicate["code_similarity"]:.1%} | Название: {duplicate["name_similarity"]:.1%}')
                print(f'   {"Домен 1":<20} {"Код":<20} {"Название":<30} {"Вопросов":<10} {"ID":<6}')
                print(f'   {d1["code"]:<20} {d1["code"]:<20} {d1["name"]:<30} {d1["questions"]:<10} {d1["id"]:<6}')
                print(f'   {d2["code"]:<20} {d2["code"]:<20} {d2["name"]:<30} {d2["questions"]:<10} {d2["id"]:<6}')
                
                # Рекомендация
                if duplicate['total_similarity'] > 0.9:
                    recommendation = "🔴 ВЫСОКАЯ ВЕРОЯТНОСТЬ ДУБЛИКАТА"
                elif duplicate['total_similarity'] > 0.8:
                    recommendation = "🟡 СРЕДНЯЯ ВЕРОЯТНОСТЬ ДУБЛИКАТА"
                else:
                    recommendation = "🟢 НИЗКАЯ ВЕРОЯТНОСТЬ ДУБЛИКАТА"
                
                print(f'   {recommendation}')
        else:
            print('\n✅ Потенциальных дубликатов не найдено!')
        
        # Дополнительная проверка: домены с одинаковым количеством вопросов
        print(f'\n📊 ДОПОЛНИТЕЛЬНАЯ ПРОВЕРКА:')
        
        # Группируем домены по количеству вопросов
        questions_groups = {}
        for domain in domain_info:
            questions_count = domain['questions']
            if questions_count not in questions_groups:
                questions_groups[questions_count] = []
            questions_groups[questions_count].append(domain)
        
        # Показываем группы с несколькими доменами
        multiple_domains_groups = {count: domains for count, domains in questions_groups.items() if len(domains) > 1}
        
        if multiple_domains_groups:
            print(f'\n📋 ДОМЕНЫ С ОДИНАКОВЫМ КОЛИЧЕСТВОМ ВОПРОСОВ:')
            for questions_count, domains in sorted(multiple_domains_groups.items()):
                print(f'\n   {questions_count} вопросов ({len(domains)} доменов):')
                for domain in domains:
                    print(f'      • {domain["code"]} ({domain["name"]})')
        else:
            print('\n   Нет доменов с одинаковым количеством вопросов')
        
        # Статистика по схожести
        print(f'\n📈 СТАТИСТИКА СХОЖЕСТИ:')
        if potential_duplicates:
            high_similarity = len([d for d in potential_duplicates if d['total_similarity'] > 0.9])
            medium_similarity = len([d for d in potential_duplicates if 0.8 < d['total_similarity'] <= 0.9])
            low_similarity = len([d for d in potential_duplicates if d['total_similarity'] <= 0.8])
            
            print(f'   Высокая схожесть (>90%): {high_similarity}')
            print(f'   Средняя схожесть (80-90%): {medium_similarity}')
            print(f'   Низкая схожесть (<80%): {low_similarity}')
        else:
            print('   Нет данных для анализа схожести')

if __name__ == '__main__':
    check_domain_similarity()


