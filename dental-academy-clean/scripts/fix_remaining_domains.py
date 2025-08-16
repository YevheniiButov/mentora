#!/usr/bin/env python3
"""
Скрипт для исправления оставшихся доменов
Добавляет DIAGNOSIS_SPECIAL и исправляет маппинг остальных доменов
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import BIGDomain, Question
from extensions import db

def add_missing_domain():
    """Добавить недостающий домен DIAGNOSIS_SPECIAL"""
    
    print('🔧 ДОБАВЛЕНИЕ ДОМЕНА DIAGNOSIS_SPECIAL')
    print('=' * 50)
    
    with app.app_context():
        # Проверяем, существует ли уже домен
        existing_domain = BIGDomain.query.filter_by(code='DIAGNOSIS_SPECIAL').first()
        
        if existing_domain:
            print('⚠️  Домен DIAGNOSIS_SPECIAL уже существует')
            return existing_domain
        
        # Создаем новый домен
        new_domain = BIGDomain(
            code='DIAGNOSIS_SPECIAL',
            name='Special Diagnosis',
            description='Special diagnostic procedures and techniques',
            weight_percentage=5.0,
            is_active=True
        )
        
        try:
            db.session.add(new_domain)
            db.session.commit()
            print(f'✅ Домен DIAGNOSIS_SPECIAL создан (ID: {new_domain.id})')
            return new_domain
            
        except Exception as e:
            print(f'❌ Ошибка при создании домена: {e}')
            db.session.rollback()
            return None

def fix_domain_mappings():
    """Исправить маппинг остальных доменов"""
    
    print('\n🔧 ИСПРАВЛЕНИЕ МАППИНГА ОСТАЛЬНЫХ ДОМЕНОВ')
    print('=' * 60)
    
    with app.app_context():
        # Маппинг доменов для исправления
        domain_mappings = {
            'DUTCH': 'DUTCH',
            'PROFESSIONAL': 'PROFESSIONAL', 
            'SPECIAL': 'SPECIAL'
        }
        
        fixed_count = 0
        
        for old_domain, new_domain_code in domain_mappings.items():
            print(f'\n📝 Исправление домена {old_domain} -> {new_domain_code}')
            
            # Найдем целевой домен
            target_domain = BIGDomain.query.filter_by(code=new_domain_code).first()
            
            if not target_domain:
                print(f'   ❌ Домен {new_domain_code} не найден')
                continue
            
            # Найдем вопросы с неправильным маппингом
            questions = Question.query.filter_by(domain=old_domain).all()
            
            if not questions:
                print(f'   ⚠️  Нет вопросов с domain="{old_domain}"')
                continue
            
            print(f'   📊 Найдено {len(questions)} вопросов для исправления')
            
            # Исправляем маппинг
            for question in questions:
                old_big_domain_id = question.big_domain_id
                question.big_domain_id = target_domain.id
                question.domain = new_domain_code
                fixed_count += 1
                print(f'   ✅ Вопрос {question.id}: {old_domain} -> {new_domain_code}')
            
            try:
                db.session.commit()
                print(f'   ✅ Маппинг для {old_domain} исправлен')
                
            except Exception as e:
                print(f'   ❌ Ошибка при сохранении: {e}')
                db.session.rollback()
        
        return fixed_count

def verify_fixes():
    """Проверить результаты исправлений"""
    
    print('\n🔍 ПРОВЕРКА РЕЗУЛЬТАТОВ')
    print('=' * 40)
    
    with app.app_context():
        # Проверяем домен DIAGNOSIS_SPECIAL
        diag_special = BIGDomain.query.filter_by(code='DIAGNOSIS_SPECIAL').first()
        if diag_special:
            questions_count = Question.query.filter_by(big_domain_id=diag_special.id).count()
            print(f'📊 Домен DIAGNOSIS_SPECIAL: {questions_count} вопросов')
        
        # Проверяем исправленные домены
        domains_to_check = ['DUTCH', 'PROFESSIONAL', 'SPECIAL']
        
        for domain_code in domains_to_check:
            domain = BIGDomain.query.filter_by(code=domain_code).first()
            if domain:
                questions_count = Question.query.filter_by(big_domain_id=domain.id).count()
                print(f'📊 Домен {domain_code}: {questions_count} вопросов')
            else:
                print(f'❌ Домен {domain_code} не найден')
        
        # Общая статистика
        print(f'\n📈 ОБЩАЯ СТАТИСТИКА:')
        domains = BIGDomain.query.filter_by(is_active=True).order_by(BIGDomain.code).all()
        
        total_questions = 0
        domains_with_questions = 0
        
        for domain in domains:
            questions_count = Question.query.filter_by(big_domain_id=domain.id).count()
            total_questions += questions_count
            
            if questions_count > 0:
                domains_with_questions += 1
                print(f'   ✅ {domain.code}: {questions_count} вопросов')
            else:
                print(f'   ⚠️  {domain.code}: 0 вопросов (пустой)')
        
        print(f'\n📊 ИТОГО:')
        print(f'   Всего доменов: {len(domains)}')
        print(f'   Доменов с вопросами: {domains_with_questions}')
        print(f'   Пустых доменов: {len(domains) - domains_with_questions}')
        print(f'   Всего вопросов: {total_questions}')

if __name__ == '__main__':
    print('🚀 Запуск исправления оставшихся доменов...')
    
    # Добавляем недостающий домен
    new_domain = add_missing_domain()
    
    # Исправляем маппинг
    fixed_count = fix_domain_mappings()
    
    # Проверяем результаты
    verify_fixes()
    
    print('\n✅ Операция завершена!')


