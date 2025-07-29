#!/usr/bin/env python3
"""
Исправление распределения доменов по категориям
"""

from app import app
from models import BIGDomain
from extensions import db
from sqlalchemy import text

def fix_category_distribution():
    with app.app_context():
        print("🔧 ИСПРАВЛЕНИЕ РАСПРЕДЕЛЕНИЯ ПО КАТЕГОРИЯМ")
        print("=" * 50)
        
        # Целевое распределение:
        # THEORETICAL: 70% (22 домена)
        # METHODOLOGY: 10% (2 домена) 
        # PRACTICAL: 15% (1 домен)
        # CLINICAL: 5% (3 домена)
        
        # Перераспределяем домены по категориям
        category_reassignments = {
            # Перемещаем TREATMENT_PLANNING из CLINICAL в THEORETICAL
            'TREATMENT_PLANNING': 'THEORETICAL',
            # Перемещаем COMMUNICATION из CLINICAL в THEORETICAL  
            'COMMUNICATION': 'THEORETICAL',
            # ETHIEK остается в CLINICAL
        }
        
        print("📋 План перераспределения:")
        for code, new_category in category_reassignments.items():
            print(f"   • {code}: CLINICAL → {new_category}")
        
        # Обновляем категории
        try:
            for code, new_category in category_reassignments.items():
                db.session.execute(text(
                    "UPDATE big_domain SET category = :category WHERE code = :code"
                ), {'category': new_category, 'code': code})
                print(f"✅ {code}: {new_category}")
            
            db.session.commit()
            print("\n✅ Категории обновлены!")
            
        except Exception as e:
            print(f"❌ Ошибка при обновлении: {e}")
            db.session.rollback()
            return
        
        # Проверяем результат
        print("\n📊 РЕЗУЛЬТАТ ПЕРЕРАСПРЕДЕЛЕНИЯ:")
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
        
        # Проверяем соответствие целевым показателям
        print(f"\n🎯 СООТВЕТСТВИЕ ЦЕЛЕВЫМ ПОКАЗАТЕЛЯМ:")
        theoretical_weight = sum(d.weight_percentage for d in domains if d.category == 'THEORETICAL')
        methodology_weight = sum(d.weight_percentage for d in domains if d.category == 'METHODOLOGY')
        practical_weight = sum(d.weight_percentage for d in domains if d.category == 'PRACTICAL')
        clinical_weight = sum(d.weight_percentage for d in domains if d.category == 'CLINICAL')
        
        print(f"   • THEORETICAL: {theoretical_weight:.1f}% (цель: 70%)")
        print(f"   • METHODOLOGY: {methodology_weight:.1f}% (цель: 10%)")
        print(f"   • PRACTICAL: {practical_weight:.1f}% (цель: 15%)")
        print(f"   • CLINICAL: {clinical_weight:.1f}% (цель: 5%)")
        
        # Проверяем количество доменов
        theoretical_count = len([d for d in domains if d.category == 'THEORETICAL'])
        methodology_count = len([d for d in domains if d.category == 'METHODOLOGY'])
        practical_count = len([d for d in domains if d.category == 'PRACTICAL'])
        clinical_count = len([d for d in domains if d.category == 'CLINICAL'])
        
        print(f"\n📊 КОЛИЧЕСТВО ДОМЕНОВ:")
        print(f"   • THEORETICAL: {theoretical_count} (цель: 22)")
        print(f"   • METHODOLOGY: {methodology_count} (цель: 2)")
        print(f"   • PRACTICAL: {practical_count} (цель: 1)")
        print(f"   • CLINICAL: {clinical_count} (цель: 3)")
        print(f"   • ВСЕГО: {len(domains)} доменов")

if __name__ == "__main__":
    fix_category_distribution() 