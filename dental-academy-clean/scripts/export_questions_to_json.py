#!/usr/bin/env python3
"""
Скрипт для экспорта всех вопросов из базы данных в JSON файл
"""

import json
import sys
import os
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import Question, BIGDomain, IRTParameters
from extensions import db

def export_questions_to_json():
    """Экспортировать все вопросы в JSON файл"""
    
    print('📤 ЭКСПОРТ ВОПРОСОВ В JSON ФАЙЛ')
    print('=' * 50)
    
    with app.app_context():
        # Получаем все вопросы с их доменами и IRT параметрами
        questions = Question.query.options(
            db.joinedload(Question.big_domain),
            db.joinedload(Question.irt_parameters)
        ).order_by(Question.id).all()
        
        print(f'📊 Найдено {len(questions)} вопросов в базе данных')
        
        # Подготавливаем данные для экспорта
        export_data = []
        
        for question in questions:
            # Получаем IRT параметры
            irt_params = question.irt_parameters
            irt_data = None
            if irt_params:
                irt_data = {
                    'difficulty': irt_params.difficulty,
                    'discrimination': irt_params.discrimination,
                    'guessing': irt_params.guessing,
                    'calibration_date': irt_params.calibration_date.isoformat() if irt_params.calibration_date else None
                }
            
            # Получаем информацию о домене
            domain_info = None
            if question.big_domain:
                domain_info = {
                    'code': question.big_domain.code,
                    'name': question.big_domain.name,
                    'weight_percentage': question.big_domain.weight_percentage
                }
            
            # Создаем объект вопроса
            question_data = {
                'id': question.id,
                'text': question.text,
                'options': question.options,
                'correct_answer_index': question.correct_answer_index,
                'correct_answer_text': question.correct_answer_text,
                'explanation': question.explanation,
                'category': question.category,
                'domain': question.domain,  # строка домена
                'domain_info': domain_info,  # полная информация о домене
                'difficulty_level': question.difficulty_level,
                'question_type': question.question_type,
                'clinical_context': question.clinical_context,
                'learning_objectives': question.learning_objectives,
                'image_url': question.image_url,
                'tags': question.tags,
                'irt_parameters': irt_data,
                'created_at': question.created_at.isoformat() if question.created_at else None,
                'updated_at': question.updated_at.isoformat() if question.updated_at else None
            }
            
            export_data.append(question_data)
        
        # Создаем имя файла с временной меткой
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'questions_export_{timestamp}.json'
        filepath = os.path.join(os.path.dirname(__file__), filename)
        
        # Экспортируем в JSON
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            print(f'✅ Экспорт завершен успешно!')
            print(f'📁 Файл сохранен: {filepath}')
            print(f'📊 Экспортировано вопросов: {len(export_data)}')
            
            # Показываем статистику по доменам
            domain_stats = {}
            for question in export_data:
                domain = question['domain']
                if domain not in domain_stats:
                    domain_stats[domain] = 0
                domain_stats[domain] += 1
            
            print(f'\n📋 СТАТИСТИКА ПО ДОМЕНАМ:')
            print(f'   {"Домен":<20} {"Вопросов":<10}')
            print('   ' + '-' * 30)
            
            for domain, count in sorted(domain_stats.items()):
                print(f'   {domain:<20} {count:<10}')
            
            return filepath
            
        except Exception as e:
            print(f'❌ Ошибка при экспорте: {e}')
            return None

def create_summary_report(filepath):
    """Создать краткий отчет об экспорте"""
    
    if not filepath:
        return
    
    report_filename = filepath.replace('.json', '_report.md')
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Анализируем данные
        total_questions = len(data)
        domains_with_irt = 0
        domains_without_irt = 0
        
        domain_stats = {}
        irt_stats = {'with_irt': 0, 'without_irt': 0}
        
        for question in data:
            domain = question['domain']
            if domain not in domain_stats:
                domain_stats[domain] = {'total': 0, 'with_irt': 0, 'without_irt': 0}
            
            domain_stats[domain]['total'] += 1
            
            if question['irt_parameters']:
                domain_stats[domain]['with_irt'] += 1
                irt_stats['with_irt'] += 1
            else:
                domain_stats[domain]['without_irt'] += 1
                irt_stats['without_irt'] += 1
        
        # Создаем отчет
        report_content = f"""# Отчет об экспорте вопросов

## Общая информация
- **Дата экспорта**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Файл**: {os.path.basename(filepath)}
- **Всего вопросов**: {total_questions}

## Статистика IRT параметров
- **С IRT параметрами**: {irt_stats['with_irt']} ({irt_stats['with_irt']/total_questions*100:.1f}%)
- **Без IRT параметров**: {irt_stats['without_irt']} ({irt_stats['without_irt']/total_questions*100:.1f}%)

## Статистика по доменам

| Домен | Всего | С IRT | Без IRT | % с IRT |
|-------|-------|-------|---------|---------|
"""
        
        for domain, stats in sorted(domain_stats.items()):
            irt_percentage = stats['with_irt'] / stats['total'] * 100 if stats['total'] > 0 else 0
            report_content += f"| {domain} | {stats['total']} | {stats['with_irt']} | {stats['without_irt']} | {irt_percentage:.1f}% |\n"
        
        report_content += f"""
## Структура файла
Файл содержит массив объектов вопросов со следующими полями:
- `id`: уникальный идентификатор
- `question_text`: текст вопроса
- `options`: варианты ответов
- `correct_answer`: правильный ответ
- `explanation`: объяснение
- `difficulty_level`: уровень сложности
- `domain`: код домена
- `domain_info`: полная информация о домене
- `irt_parameters`: IRT параметры (если есть)
- `created_at`: дата создания
- `updated_at`: дата обновления

## Использование
Этот файл можно использовать для:
- Резервного копирования данных
- Импорта в другую систему
- Анализа структуры вопросов
- Восстановления данных при необходимости
"""
        
        with open(report_filename, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f'📄 Отчет создан: {report_filename}')
        
    except Exception as e:
        print(f'❌ Ошибка при создании отчета: {e}')

if __name__ == '__main__':
    print('🚀 Запуск экспорта вопросов...')
    
    filepath = export_questions_to_json()
    
    if filepath:
        create_summary_report(filepath)
        print('\n✅ Экспорт и создание отчета завершены успешно!')
    else:
        print('\n❌ Экспорт завершился с ошибками!')
