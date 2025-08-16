#!/usr/bin/env python3
"""
Скрипт для исправления дублирования доменов
Объединяет дублирующиеся домены и удаляет пустые
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import BIGDomain, Question
from extensions import db

def find_duplicate_domains():
    """Найти дублирующиеся домены"""
    
    print('🔍 ПОИСК ДУБЛИРУЮЩИХСЯ ДОМЕНОВ')
    print('=' * 50)
    
    with app.app_context():
        # Получаем все домены
        domains = BIGDomain.query.filter_by(is_active=True).all()
        
        # Группируем по нормализованному коду (в нижнем регистре)
        domain_groups = {}
        
        for domain in domains:
            normalized_code = domain.code.lower()
            if normalized_code not in domain_groups:
                domain_groups[normalized_code] = []
            domain_groups[normalized_code].append(domain)
        
        # Находим дубликаты
        duplicates = {}
        for normalized_code, domain_list in domain_groups.items():
            if len(domain_list) > 1:
                duplicates[normalized_code] = domain_list
        
        if duplicates:
            print(f'📊 Найдено {len(duplicates)} групп дублирующихся доменов:')
            
            for normalized_code, domain_list in duplicates.items():
                print(f'\n🔍 Группа: {normalized_code}')
                print(f'   {"Код":<20} {"Название":<30} {"Вопросов":<10} {"ID":<6} {"Вес":<8}')
                print('   ' + '-' * 80)
                
                for domain in domain_list:
                    questions_count = Question.query.filter_by(big_domain_id=domain.id).count()
                    print(f'   {domain.code:<20} {domain.name:<30} {questions_count:<10} {domain.id:<6} {domain.weight_percentage:<8}')
            
            return duplicates
        else:
            print('✅ Дублирующихся доменов не найдено!')
            return {}

def fix_duplicate_domains(duplicates):
    """Исправить дублирующиеся домены"""
    
    if not duplicates:
        print('❌ Нет дубликатов для исправления')
        return
    
    print(f'\n🔧 ИСПРАВЛЕНИЕ ДУБЛИРУЮЩИХСЯ ДОМЕНОВ')
    print('=' * 50)
    
    with app.app_context():
        total_fixed = 0
        
        for normalized_code, domain_list in duplicates.items():
            print(f'\n📝 Исправление группы: {normalized_code}')
            
            # Сортируем домены по количеству вопросов (больше вопросов = приоритет)
            domain_list.sort(key=lambda d: Question.query.filter_by(big_domain_id=d.id).count(), reverse=True)
            
            # Первый домен становится основным
            main_domain = domain_list[0]
            main_questions = Question.query.filter_by(big_domain_id=main_domain.id).count()
            
            print(f'   🎯 Основной домен: {main_domain.code} (ID: {main_domain.id}, {main_questions} вопросов)')
            
            # Остальные домены удаляем, предварительно перенеся вопросы
            for duplicate_domain in domain_list[1:]:
                duplicate_questions = Question.query.filter_by(big_domain_id=duplicate_domain.id).count()
                
                print(f'   📋 Дубликат: {duplicate_domain.code} (ID: {duplicate_domain.id}, {duplicate_questions} вопросов)')
                
                if duplicate_questions > 0:
                    # Переносим вопросы в основной домен
                    questions_to_move = Question.query.filter_by(big_domain_id=duplicate_domain.id).all()
                    
                    for question in questions_to_move:
                        old_domain_id = question.big_domain_id
                        question.big_domain_id = main_domain.id
                        question.domain = main_domain.code
                        print(f'      ✅ Вопрос {question.id}: {duplicate_domain.code} -> {main_domain.code}')
                    
                    total_fixed += duplicate_questions
                
                # Удаляем дублирующийся домен
                try:
                    db.session.delete(duplicate_domain)
                    print(f'      🗑️  Домен {duplicate_domain.code} удален')
                except Exception as e:
                    print(f'      ❌ Ошибка при удалении домена {duplicate_domain.code}: {e}')
                    db.session.rollback()
                    continue
        
        # Сохраняем изменения
        try:
            db.session.commit()
            print(f'\n📊 РЕЗУЛЬТАТ:')
            print(f'   Перенесено вопросов: {total_fixed}')
            print(f'   Удалено дублирующихся доменов: {sum(len(domains) - 1 for domains in duplicates.values())}')
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
        # Проверяем, остались ли дубликаты
        domains = BIGDomain.query.filter_by(is_active=True).all()
        
        domain_codes = {}
        for domain in domains:
            normalized_code = domain.code.lower()
            if normalized_code not in domain_codes:
                domain_codes[normalized_code] = []
            domain_codes[normalized_code].append(domain)
        
        remaining_duplicates = {code: domains for code, domains in domain_codes.items() if len(domains) > 1}
        
        if remaining_duplicates:
            print(f'⚠️  Остались дубликаты: {len(remaining_duplicates)}')
            for code, domains in remaining_duplicates.items():
                print(f'   {code}: {[d.code for d in domains]}')
        else:
            print('✅ Дубликаты полностью устранены!')
        
        # Показываем финальную статистику
        total_domains = len(domains)
        domains_with_questions = 0
        total_questions = 0
        
        for domain in domains:
            questions_count = Question.query.filter_by(big_domain_id=domain.id).count()
            total_questions += questions_count
            if questions_count > 0:
                domains_with_questions += 1
        
        print(f'\n📊 ФИНАЛЬНАЯ СТАТИСТИКА:')
        print(f'   Всего доменов: {total_domains}')
        print(f'   Доменов с вопросами: {domains_with_questions}')
        print(f'   Пустых доменов: {total_domains - domains_with_questions}')
        print(f'   Всего вопросов: {total_questions}')

if __name__ == '__main__':
    print('🚀 Запуск исправления дублирующихся доменов...')
    
    duplicates = find_duplicate_domains()
    
    if duplicates:
        success = fix_duplicate_domains(duplicates)
        
        if success:
            verify_fixes()
            print('\n✅ Исправление дубликатов завершено успешно!')
        else:
            print('\n❌ Исправление завершилось с ошибками!')
    else:
        print('\n✅ Дубликатов не найдено, исправление не требуется!')


