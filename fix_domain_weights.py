#!/usr/bin/env python3
"""
Исправление весов доменов до 100%
"""

from app import app
from models import BIGDomain
from extensions import db
from sqlalchemy import text
import json

def fix_domain_weights():
    with app.app_context():
        print("🔧 ИСПРАВЛЕНИЕ ВЕСОВ ДОМЕНОВ")
        print("=" * 50)
        
        # 1. Аудит текущего состояния
        domains = BIGDomain.query.filter_by(is_active=True).all()
        total_weight = sum(d.weight_percentage for d in domains)
        print(f"📊 Текущий общий вес: {total_weight:.1f}%")
        
        # 2. Определяем правильные веса
        # Критические домены (85% от общего веса)
        critical_weights = {
            'THER': 12.0,              # Терапевтическая стоматология
            'PRACTICAL_SKILLS': 12.0,  # Практические навыки
            'TREATMENT_PLANNING': 10.0, # Планирование лечения
            'SURG': 8.0,               # Хирургическая стоматология
            'EMERGENCY': 8.0,          # Неотложная помощь
            'DIAGNOSIS': 8.0,          # Диагностика
            'PHARMA': 6.0,             # Фармакология
            'COMMUNICATION': 6.0,      # Коммуникативные навыки
            'SYSTEMIC': 5.0,           # Системные заболевания
            'STATISTICS': 5.0,         # Статистика
            'RESEARCH_METHOD': 5.0     # Методология
        }
        
        # Некритические домены (15% от общего веса)
        non_critical_domains = [
            'PROTH', 'PEDI', 'PARO', 'ORTHO', 'PREV', 'ANATOMIE', 'FYSIOLOGIE',
            'PATHOLOGIE', 'MICROBIOLOGIE', 'MATERIAALKUNDE', 'RADIOLOGIE',
            'ALGEMENE_GENEESKUNDE', 'INFECTION', 'SPECIAL', 'DUTCH', 'PROFESSIONAL', 'ETHIEK'
        ]
        
        # Распределяем 15% между некритическими доменами
        non_critical_weight = 15.0 / len(non_critical_domains)
        
        print(f"📋 План исправления:")
        print(f"   • Критических доменов: {len(critical_weights)} (85%)")
        print(f"   • Некритических доменов: {len(non_critical_domains)} (15%)")
        print(f"   • Вес некритического домена: {non_critical_weight:.2f}%")
        
        # 3. Обновляем веса
        try:
            # Обновляем критические домены
            for code, weight in critical_weights.items():
                db.session.execute(text(
                    "UPDATE big_domain SET weight_percentage = :weight WHERE code = :code"
                ), {'weight': weight, 'code': code})
                print(f"✅ {code}: {weight:.1f}%")
            
            # Обновляем некритические домены
            for code in non_critical_domains:
                db.session.execute(text(
                    "UPDATE big_domain SET weight_percentage = :weight WHERE code = :code"
                ), {'weight': non_critical_weight, 'code': code})
                print(f"✅ {code}: {non_critical_weight:.2f}%")
            
            db.session.commit()
            print("\n✅ Веса обновлены!")
            
        except Exception as e:
            print(f"❌ Ошибка при обновлении: {e}")
            db.session.rollback()
            return
        
        # 4. Проверяем результат
        print("\n📊 РЕЗУЛЬТАТ ИСПРАВЛЕНИЯ:")
        print("=" * 50)
        
        domains = BIGDomain.query.filter_by(is_active=True).all()
        total_weight = sum(d.weight_percentage for d in domains)
        print(f"Общий вес: {total_weight:.1f}%")
        
        # Группируем по категориям
        categories = {}
        for domain in domains:
            cat = domain.category or 'UNCATEGORIZED'
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(domain)
        
        for category, domain_list in categories.items():
            cat_weight = sum(d.weight_percentage for d in domain_list)
            print(f"\n📋 {category} ({len(domain_list)} доменов, {cat_weight:.1f}%):")
            for domain in sorted(domain_list, key=lambda x: x.weight_percentage, reverse=True):
                critical = "⭐" if domain.is_critical else "  "
                print(f"   {critical} {domain.code:15} | {domain.name:35} | {domain.weight_percentage:5.1f}%")
        
        # Проверяем критические домены
        critical = [d for d in domains if d.is_critical]
        critical_weight = sum(d.weight_percentage for d in critical)
        print(f"\n⭐ КРИТИЧЕСКИЕ ДОМЕНЫ ({len(critical)} доменов, {critical_weight:.1f}%):")
        for domain in sorted(critical, key=lambda x: x.weight_percentage, reverse=True):
            print(f"   {domain.code:15} | {domain.name:35} | {domain.weight_percentage:5.1f}%")
        
        # Валидация
        if abs(total_weight - 100.0) < 0.1:
            print(f"\n✅ ВАЛИДАЦИЯ ПРОЙДЕНА: Общий вес = {total_weight:.1f}%")
        else:
            print(f"\n❌ ВАЛИДАЦИЯ НЕ ПРОЙДЕНА: Общий вес = {total_weight:.1f}% (должен быть 100%)")

if __name__ == "__main__":
    fix_domain_weights() 