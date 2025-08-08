#!/usr/bin/env python3
import json
import os
from collections import defaultdict
from datetime import datetime

def analyze_domains():
    try:
        # Читаем файл с вопросами
        with open('../scripts/160_2.json', 'r', encoding='utf-8') as f:
            questions_data = json.load(f)
        
        # Статистика по доменам
        domain_stats = defaultdict(int)
        domain_irt = defaultdict(lambda: {'difficulty': [], 'discrimination': [], 'guessing': []})
        domain_difficulty = defaultdict(lambda: {1: 0, 2: 0, 3: 0})
        domain_categories = defaultdict(set)
        
        # Анализируем каждый вопрос
        for question in questions_data:
            domain = question['domain']
            
            # Подсчет вопросов по доменам
            domain_stats[domain] += 1
            
            # IRT параметры по доменам
            if 'irt_parameters' in question:
                irt = question['irt_parameters']
                domain_irt[domain]['difficulty'].append(irt['difficulty'])
                domain_irt[domain]['discrimination'].append(irt['discrimination'])
                domain_irt[domain]['guessing'].append(irt['guessing'])
            
            # Уровни сложности по доменам
            domain_difficulty[domain][question['difficulty_level']] += 1
            
            # Категории по доменам
            domain_categories[domain].add(question['category'])
        
        # Вычисляем средние IRT параметры
        average_irt = {}
        for domain, irt_data in domain_irt.items():
            difficulty = irt_data['difficulty']
            discrimination = irt_data['discrimination']
            guessing = irt_data['guessing']
            
            if difficulty:
                average_irt[domain] = {
                    'avg_difficulty': round(sum(difficulty) / len(difficulty), 3),
                    'avg_discrimination': round(sum(discrimination) / len(discrimination), 3),
                    'avg_guessing': round(sum(guessing) / len(guessing), 3),
                    'min_difficulty': min(difficulty),
                    'max_difficulty': max(difficulty),
                    'min_discrimination': min(discrimination),
                    'max_discrimination': max(discrimination)
                }
        
        # Преобразуем Set в списки для JSON
        domain_categories_list = {domain: list(categories) for domain, categories in domain_categories.items()}
        
        # Анализ проблем
        problems = {
            'insufficient_domains': [],
            'excessive_domains': [],
            'invalid_irt': [],
            'duplicate_domains': []
        }
        
        # Домены с недостаточным количеством вопросов
        for domain, count in domain_stats.items():
            if count < 10:
                problems['insufficient_domains'].append({
                    'domain': domain,
                    'count': count,
                    'needed': 10 - count
                })
        
        # Домены с избыточным количеством вопросов
        for domain, count in domain_stats.items():
            if count > 30:
                problems['excessive_domains'].append({
                    'domain': domain,
                    'count': count,
                    'excess': count - 30
                })
        
        # Проверка IRT параметров
        for question in questions_data:
            if 'irt_parameters' in question:
                irt = question['irt_parameters']
                if irt['difficulty'] > 2 or irt['discrimination'] < 1:
                    problems['invalid_irt'].append({
                        'id': question['id'],
                        'domain': question['domain'],
                        'difficulty': irt['difficulty'],
                        'discrimination': irt['discrimination'],
                        'issue': 'difficulty_too_high' if irt['difficulty'] > 2 else 'discrimination_too_low'
                    })
        
        # Поиск дублирующихся доменов
        potential_duplicates = {
            'PHARMA': 'FARMACOLOGIE',
            'ETHIEK': 'PROFESSIONAL'
        }
        
        for domain1, domain2 in potential_duplicates.items():
            if domain1 in domain_stats and domain2 in domain_stats:
                problems['duplicate_domains'].append({
                    'domain1': domain1,
                    'domain2': domain2,
                    'count1': domain_stats[domain1],
                    'count2': domain_stats[domain2],
                    'total': domain_stats[domain1] + domain_stats[domain2]
                })
        
        # Общая статистика
        total_questions = len(questions_data)
        total_domains = len(domain_stats)
        average_questions_per_domain = round(total_questions / total_domains, 2)
        
        report = {
            'summary': {
                'total_questions': total_questions,
                'total_domains': total_domains,
                'average_questions_per_domain': average_questions_per_domain,
                'date_analyzed': datetime.now().isoformat()
            },
            'domain_statistics': dict(domain_stats),
            'domain_irt_averages': average_irt,
            'domain_difficulty_levels': dict(domain_difficulty),
            'domain_categories': domain_categories_list,
            'problems': problems
        }
        
        # Сохраняем отчет
        with open('domain_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print('✅ Анализ завершен. Результаты сохранены в analysis/domain_report.json')
        
        return report
        
    except Exception as error:
        print(f'❌ Ошибка при анализе: {error}')
        return None

if __name__ == '__main__':
    analyze_domains() 