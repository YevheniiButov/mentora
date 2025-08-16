#!/usr/bin/env python3
"""
Скрипт для исправления маппинга доменов
Переносит вопросы FARMACOLOGIE и PHARMA в домен PHARMACOLOGY
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import BIGDomain, Question
from extensions import db

def fix_pharmacology_mapping():
    """Исправить маппинг фармакологических доменов"""
    
    print('🔧 ИСПРАВЛЕНИЕ МАППИНГА ФАРМАКОЛОГИЧЕСКИХ ДОМЕНОВ')
    print('=' * 60)
    
    with app.app_context():
        # Найдем домен PHARMACOLOGY
        pharma_domain = BIGDomain.query.filter_by(code='PHARMACOLOGY').first()
        
        if not pharma_domain:
            print('❌ Домен PHARMACOLOGY не найден')
            return False
        
        print(f'📊 Найден домен PHARMACOLOGY (ID: {pharma_domain.id})')
        print(f'   Название: {pharma_domain.name}')
        
        # Найдем вопросы с domain="FARMACOLOGIE"
        farma_questions = Question.query.filter_by(domain='FARMACOLOGIE').all()
        print(f'\n🔍 Найдено {len(farma_questions)} вопросов с domain="FARMACOLOGIE"')
        
        # Найдем вопросы с domain="PHARMA"
        pharma_questions = Question.query.filter_by(domain='PHARMA').all()
        print(f'🔍 Найдено {len(pharma_questions)} вопросов с domain="PHARMA"')
        
        total_questions_to_fix = len(farma_questions) + len(pharma_questions)
        
        if total_questions_to_fix == 0:
            print('✅ Нет вопросов для исправления')
            return True
        
        print(f'\n📝 ИСПРАВЛЕНИЕ МАППИНГА:')
        
        fixed_count = 0
        
        # Исправляем вопросы FARMACOLOGIE
        for question in farma_questions:
            old_domain_id = question.big_domain_id
            question.big_domain_id = pharma_domain.id
            fixed_count += 1
            print(f'   ✅ Вопрос {question.id}: FARMACOLOGIE -> PHARMACOLOGY (было: {old_domain_id})')
        
        # Исправляем вопросы PHARMA
        for question in pharma_questions:
            old_domain_id = question.big_domain_id
            question.big_domain_id = pharma_domain.id
            fixed_count += 1
            print(f'   ✅ Вопрос {question.id}: PHARMA -> PHARMACOLOGY (было: {old_domain_id})')
        
        # Сохраняем изменения
        try:
            db.session.commit()
            print(f'\n📊 РЕЗУЛЬТАТ:')
            print(f'   Исправлено вопросов: {fixed_count}')
            print(f'   FARMACOLOGIE: {len(farma_questions)}')
            print(f'   PHARMA: {len(pharma_questions)}')
            
            # Проверяем результат
            final_count = Question.query.filter_by(big_domain_id=pharma_domain.id).count()
            print(f'   Всего в PHARMACOLOGY: {final_count}')
            
            return True
            
        except Exception as e:
            print(f'❌ Ошибка при сохранении: {e}')
            db.session.rollback()
            return False

def verify_fix():
    """Проверить результат исправления"""
    
    print('\n🔍 ПРОВЕРКА РЕЗУЛЬТАТА')
    print('=' * 40)
    
    with app.app_context():
        # Проверяем домен PHARMACOLOGY
        pharma_domain = BIGDomain.query.filter_by(code='PHARMACOLOGY').first()
        if pharma_domain:
            questions = Question.query.filter_by(big_domain_id=pharma_domain.id).all()
            print(f'📊 Домен PHARMACOLOGY: {len(questions)} вопросов')
            
            # Проверяем, остались ли вопросы с неправильными domain
            farma_remaining = Question.query.filter_by(domain='FARMACOLOGIE').count()
            pharma_remaining = Question.query.filter_by(domain='PHARMA').count()
            
            print(f'🔍 Осталось вопросов с domain="FARMACOLOGIE": {farma_remaining}')
            print(f'🔍 Осталось вопросов с domain="PHARMA": {pharma_remaining}')
            
            if farma_remaining == 0 and pharma_remaining == 0:
                print('✅ Все вопросы успешно перенесены!')
            else:
                print('⚠️  Некоторые вопросы не были перенесены')
        
        # Показываем статистику по доменам
        print(f'\n📈 ОБНОВЛЕННАЯ СТАТИСТИКА ДОМЕНОВ:')
        domains = BIGDomain.query.filter_by(is_active=True).order_by(BIGDomain.code).all()
        
        for domain in domains:
            questions_count = Question.query.filter_by(big_domain_id=domain.id).count()
            if questions_count > 0:
                print(f'   • {domain.code}: {questions_count} вопросов')

if __name__ == '__main__':
    print('🚀 Запуск исправления маппинга доменов...')
    
    success = fix_pharmacology_mapping()
    
    if success:
        verify_fix()
        print('\n✅ Операция завершена успешно!')
    else:
        print('\n❌ Операция завершена с ошибками!')


