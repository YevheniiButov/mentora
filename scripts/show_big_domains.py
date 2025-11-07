#!/usr/bin/env python3
"""Show all BIG domains in database"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from models import BIGDomain

with app.app_context():
    print("🔍 ПРОВЕРКА BIG-ДОМЕНОВ В БАЗЕ ДАННЫХ:")
    print("=" * 50)
    
    domains = BIGDomain.query.all()
    
    if domains:
        print(f"📊 Найдено доменов: {len(domains)}")
        print("\n📋 СПИСОК ВСЕХ ДОМЕНОВ:")
        print("-" * 50)
        
        for domain in domains:
            print(f"   {domain.code}: {domain.name}")
        
        print("-" * 50)
        print(f"✅ Всего доменов в БД: {len(domains)}")
        
        # Проверка ожидаемых доменов
        expected_codes = ['THER', 'SURG', 'PROTH', 'PEDI', 'PARO', 'ORTHO', 'PREV', 'ETHIEK', 
                         'ANATOMIE', 'FYSIOLOGIE', 'PATHOLOGIE', 'MICROBIOLOGIE', 
                         'MATERIAALKUNDE', 'RADIOLOGIE', 'ALGEMENE', 'ALGEMENE_GENEESKUNDE']
        
        existing_codes = [d.code for d in domains]
        missing_codes = [code for code in expected_codes if code not in existing_codes]
        
        if missing_codes:
            print(f"\n⚠️ Отсутствующие домены: {missing_codes}")
        else:
            print(f"\n✅ Все ожидаемые домены присутствуют!")
            
    else:
        print("❌ Домены не найдены в базе данных!")
        print("💡 Нужно создать домены через скрипт create_big_domains.py") 