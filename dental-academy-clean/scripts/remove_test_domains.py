#!/usr/bin/env python3
"""
Скрипт для удаления тестовых доменов
Удаляет только TEST и TEST_DOMAIN_1754899017.787052
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import BIGDomain
from extensions import db

def remove_test_domains():
    """Удалить тестовые домены TEST и TEST_DOMAIN_1754899017.787052"""
    
    test_domains = ['TEST', 'TEST_DOMAIN_1754899017.787052']
    
    print('🗑️  УДАЛЕНИЕ ТЕСТОВЫХ ДОМЕНОВ')
    print('=' * 50)
    
    with app.app_context():
        removed_count = 0
        
        for domain_code in test_domains:
            domain = BIGDomain.query.filter_by(code=domain_code).first()
            
            if domain:
                print(f'\n📊 Найден домен: {domain_code}')
                print(f'   ID: {domain.id}')
                print(f'   Название: {domain.name}')
                print(f'   Вес: {domain.weight_percentage}%')
                
                # Проверяем, что домен действительно пустой
                questions_count = len(domain.questions) if hasattr(domain, 'questions') else 0
                print(f'   Вопросов: {questions_count}')
                
                if questions_count == 0:
                    try:
                        db.session.delete(domain)
                        db.session.commit()
                        print(f'   ✅ Домен {domain_code} успешно удален')
                        removed_count += 1
                    except Exception as e:
                        print(f'   ❌ Ошибка при удалении домена {domain_code}: {e}')
                        db.session.rollback()
                else:
                    print(f'   ⚠️  Домен {domain_code} содержит {questions_count} вопросов - НЕ УДАЛЯЕМ')
            else:
                print(f'\n❌ Домен {domain_code} не найден в базе данных')
        
        print(f'\n📈 РЕЗУЛЬТАТ:')
        print(f'   Удалено доменов: {removed_count}')
        
        if removed_count > 0:
            print('✅ Операция завершена успешно!')
        else:
            print('❌ Операция завершена с ошибками!')

if __name__ == '__main__':
    remove_test_domains()
